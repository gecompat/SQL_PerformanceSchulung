[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('\A127\.0\.0\.1,[1-9][0-9]{0,4}\z')]
    [string] $Server,

    [Parameter(Mandatory)]
    [switch] $ConfirmDisposableInstance,

    [switch] $SequentialControl,

    [switch] $IdenticalBatch
)

$ErrorActionPreference = 'Stop'
$requiredBuild = '17.0.5065.9'
$password = [Environment]::GetEnvironmentVariable('SQLCMDPASSWORD', 'Process')
if (-not $ConfirmDisposableInstance -or [string]::IsNullOrEmpty($password) -or
    [int]($Server.Split(',')[1]) -gt 65535) {
    throw 'Compile witness requires a loopback port, disposable-instance confirmation and SQLCMDPASSWORD.'
}

function Invoke-XeCommand($Observer, [string] $Sql, [switch] $Scalar) {
    $command = $Observer.CreateCommand()
    $command.CommandTimeout = 5
    $command.CommandText = $Sql
    try {
        if ($Scalar) {
            return $command.ExecuteScalar()
        }
        [void] $command.ExecuteNonQuery()
    } finally {
        $command.Dispose()
    }
}

function Read-CompileWitnesses($Observer, [string] $Name, [hashtable] $BatchByActor) {
    $root = $null
    $deadline = [System.Diagnostics.Stopwatch]::StartNew()
    do {
        $snapshot = Invoke-XeCommand $Observer @"
SELECT CONVERT(nvarchar(max), t.target_data)
FROM sys.dm_xe_sessions AS s
JOIN sys.dm_xe_session_targets AS t ON t.event_session_address = s.address
WHERE s.name = N'$Name' AND t.target_name = N'ring_buffer'
    AND s.dropped_event_count = 0 AND s.dropped_buffer_count = 0
    AND s.largest_event_dropped_size = 0 AND s.pending_buffers = 0;
"@ -Scalar
        if ($snapshot -is [string] -and $snapshot.Length -le 2097152) {
            $document = [System.Xml.XmlDocument]::new()
            $document.XmlResolver = $null
            $xmlSettings = [System.Xml.XmlReaderSettings]::new()
            $xmlSettings.DtdProcessing = [System.Xml.DtdProcessing]::Prohibit
            $xmlSettings.MaxCharactersInDocument = 2097152
            $source = [System.IO.StringReader]::new($snapshot)
            try {
                $reader = [System.Xml.XmlReader]::Create($source, $xmlSettings)
                try { $document.Load($reader) } finally { $reader.Dispose() }
            } finally { $source.Dispose() }
            $root = $document.DocumentElement
            $events = $root.SelectNodes('event')
            if ($root.Name -cne 'RingBufferTarget' -or $root.GetAttribute('truncated') -cne '0' -or
                $root.GetAttribute('droppedCount') -cne '0' -or
                $root.GetAttribute('eventCount') -cne [string]$events.Count -or
                $root.GetAttribute('totalEventsProcessed') -cne [string]$events.Count) {
                throw 'Incomplete XE ring buffer.'
            }
            if ($root.SelectNodes("event[@name='rpc_completed']").Count -eq 2) { break }
        }
        Start-Sleep -Milliseconds 100
    } while ($deadline.Elapsed.TotalSeconds -lt 6)
    if ($null -eq $root -or $root.SelectNodes("event[@name='rpc_completed']").Count -ne 2) { throw 'Missing terminal events.' }
    $ordered = $events | ForEach-Object {
        $event = $_
        [pscustomobject]@{
            Name = $event.GetAttribute('name')
            Package = $event.GetAttribute('package')
            Sequence = [long]$event.SelectSingleNode("action[@name='event_sequence']/value").InnerText
            Time = [DateTimeOffset]::ParseExact($event.GetAttribute('timestamp'), "yyyy-MM-dd'T'HH:mm:ss.FFFFFFF'Z'",
                [cultureinfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal).UtcTicks
            Session = [int]$event.SelectSingleNode("action[@name='session_id']/value").InnerText
            Database = $event.SelectSingleNode("action[@name='database_id']/value").InnerText
            Event = $event
        }
    } | Sort-Object Sequence
    $lastSequence = 0L
    foreach ($record in $ordered) {
        if ($record.Package -cne 'sqlserver' -or $record.Database -cne '1' -or
            $record.Sequence -le $lastSequence -or -not $BatchByActor.ContainsKey($record.Session)) {
            throw 'Unbound XE event.'
        }
        $lastSequence = $record.Sequence
    }
    $bounds = @(foreach ($id in ($BatchByActor.Keys | Sort-Object)) {
        $stream = @($ordered | Where-Object Session -eq $id)
        if ($stream.Count -lt 2 -or $stream[0].Name -cne 'rpc_starting' -or $stream[-1].Name -cne 'rpc_completed' -or
            $stream[0].Time -gt $stream[-1].Time) {
            throw 'Unexpected compile witness stream.'
        }
        $statement = $BatchByActor[$id]
        foreach ($edge in @($stream[0], $stream[-1])) {
            if ($edge.Event.SelectSingleNode("data[@name='object_name']/value").InnerText -cne 'sp_executesql' -or
                -not $edge.Event.SelectSingleNode("data[@name='statement']/value").InnerText.Contains($statement, [StringComparison]::Ordinal)) {
                throw 'Unbound RPC boundary.'
            }
        }
        if ($IdenticalBatch -and $stream.Count -eq 2) { continue }
        $ce = @($stream | Select-Object -Skip 1 -SkipLast 2)
        if ($stream[-2].Name -cne 'sql_statement_post_compile' -or $ce.Count -lt 2) {
            throw 'Incomplete first compilation witness.'
        }
        if ($stream[-2].Event.SelectSingleNode("data[@name='is_recompile']/value").InnerText -cne 'false' -or
            $stream[-2].Event.SelectSingleNode("data[@name='statement']/value").InnerText -cne $statement.TrimEnd(';')) {
            throw 'Unbound first compilation.'
        }
        $previousTime = $stream[0].Time
        foreach ($event in $ce) {
            $sqlText = [string]$event.Event.SelectSingleNode("action[@name='sql_text']/value").InnerText
            if ($event.Name -cne 'query_optimizer_estimate_cardinality' -or
                -not $sqlText.Contains($statement, [StringComparison]::Ordinal) -or $event.Time -lt $previousTime) {
                throw 'Unbound estimation event.'
            }
            $previousTime = $event.Time
        }
        if ($previousTime -gt $stream[-2].Time -or $stream[-2].Time -gt $stream[-1].Time) {
            throw 'Compile witness timestamps disagree with the request order.'
        }
        [pscustomobject]@{ Session = $id; First = $ce[0]; Last = $ce[-1]; Count = $ce.Count }
    })
    if ($bounds.Count -eq 0) { throw 'No first compilation witness.' }
    $intervalTicks = $null
    $interleaved = $false
    if ($bounds.Count -eq 2) {
        $intervalTicks = [Math]::Min($bounds[0].Last.Time, $bounds[1].Last.Time) -
            [Math]::Max($bounds[0].First.Time, $bounds[1].First.Time)
        $interleaved = [Math]::Min($bounds[0].Last.Sequence, $bounds[1].Last.Sequence) -gt
            [Math]::Max($bounds[0].First.Sequence, $bounds[1].First.Sequence)
    }
    return [ordered]@{
        compile_actors = @($bounds | ForEach-Object Session)
        ce_counts = @($bounds | ForEach-Object Count)
        sequence_interleaved = $interleaved
        timestamp_interval_ticks = $intervalTicks
    }
}

$settings = [System.Data.SqlClient.SqlConnectionStringBuilder]::new()
$settings['Data Source'] = "tcp:$Server"
$settings['Initial Catalog'] = 'master'
$settings['User ID'] = 'sa'
$settings['Password'] = $password
$settings['Encrypt'] = $true
$settings['TrustServerCertificate'] = $true
$settings['Persist Security Info'] = $false
$settings['Pooling'] = $false
$settings['MultipleActiveResultSets'] = $false
$settings['Connect Timeout'] = 5
$settings['ConnectRetryCount'] = 0

$actor = [System.Data.SqlClient.SqlConnection]::new($settings.ConnectionString)
$observer = [System.Data.SqlClient.SqlConnection]::new($settings.ConnectionString)
$xeName = $null
$stage = 'preflight'
try {
    $actor.Open()
    $observer.Open()
    $command = $actor.CreateCommand()
    $command.CommandTimeout = 5
    try {
        $command.CommandText = @'
SET NOCOUNT ON;
IF DB_NAME() <> N'master'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'ProductVersion')), N'') <> N'17.0.5065.9'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'Edition')), N'') <> N'Enterprise Developer Edition (64-bit)'
    OR COALESCE(IS_SRVROLEMEMBER(N'sysadmin'), 0) <> 1
    OR EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4)
    OR NOT EXISTS (
        SELECT 1 FROM sys.database_scoped_configurations
        WHERE name = N'OPTIMIZED_SP_EXECUTESQL' AND TRY_CONVERT(int, value) = 0
    )
    THROW 51006, 'NOT_PROVEN: unexpected compile witness target.', 1;
SELECT CONVERT(int, @@SPID);
'@
        $sessionId = $command.ExecuteScalar()
        if ($sessionId -isnot [int] -or $sessionId -le 0) {
            throw 'Compile witness has no actor session.'
        }

        $second = [System.Data.SqlClient.SqlConnection]::new($settings.ConnectionString)
        try {
            $second.Open()
            $other = $second.CreateCommand()
            $other.CommandTimeout = 5
            try {
                $other.CommandText = 'SELECT CONVERT(int, @@SPID);'
                $secondId = [int]$other.ExecuteScalar()
                if ($secondId -le 0 -or $secondId -eq $sessionId) { throw 'Invalid second actor.' }
                $stage = 'xe_start'
                $xeName = 'optsp_rpc_' + [guid]::NewGuid().ToString('N')
                $filter = "WHERE (([sqlserver].[session_id]=($sessionId)) OR ([sqlserver].[session_id]=($secondId)))"
                $actions = 'ACTION(package0.event_sequence, sqlserver.database_id, sqlserver.session_id)'
                Invoke-XeCommand $observer @"
CREATE EVENT SESSION [$xeName] ON SERVER
ADD EVENT sqlserver.rpc_starting($actions $filter),
ADD EVENT sqlserver.rpc_completed($actions $filter),
ADD EVENT sqlserver.sql_statement_post_compile(SET collect_statement=(1) $actions $filter),
ADD EVENT sqlserver.query_optimizer_estimate_cardinality(
    ACTION(package0.event_sequence, sqlserver.database_id, sqlserver.session_id, sqlserver.sql_text) $filter)
ADD TARGET package0.ring_buffer(SET max_memory=(1024))
WITH (MAX_MEMORY=4 MB, MAX_DISPATCH_LATENCY=1 SECONDS, STARTUP_STATE=OFF);
ALTER EVENT SESSION [$xeName] ON SERVER STATE=START;
"@
                $stems = @(
                    'SELECT @value + (SELECT COUNT(*) FROM (VALUES (1),(2),(3)) a(id)'
                    'JOIN (VALUES (1),(3),(4)) b(id) ON a.id = b.id'
                    'JOIN (VALUES (1),(2),(5)) c(id) ON b.id = c.id'
                    'JOIN (VALUES (1),(2),(6)) d(id) ON c.id = d.id'
                    'JOIN (VALUES (1),(3),(7)) e(id) ON d.id = e.id'
                )
                $common = $stems -join ' '
                $batchByActor = @{
                    $sessionId = "$common WHERE a.id > @value);"
                    $secondId = "$common WHERE a.id > @value AND e.id < 9);"
                }
                if ($IdenticalBatch) { $batchByActor[$secondId] = $batchByActor[$sessionId] }
                foreach ($item in @(@{ Command = $command; Id = $sessionId }, @{ Command = $other; Id = $secondId })) {
                    $rpc = $item.Command
                    $rpc.CommandType = [System.Data.CommandType]::StoredProcedure
                    $rpc.CommandText = 'sys.sp_executesql'
                    $rpc.Parameters.Add('@stmt', [System.Data.SqlDbType]::NVarChar, -1).Value = $batchByActor[$item.Id]
                    $rpc.Parameters.Add('@params', [System.Data.SqlDbType]::NVarChar, -1).Value = '@value int'
                    $rpc.Parameters.Add('@value', [System.Data.SqlDbType]::Int).Value = 37
                }
                $stage = 'synthetic_requests'
                $firstTask = $command.ExecuteScalarAsync()
                if ($SequentialControl) {
                    $firstResult = $firstTask.GetAwaiter().GetResult()
                }
                $otherTask = $other.ExecuteScalarAsync()
                $otherResult = $otherTask.GetAwaiter().GetResult()
                if (-not $SequentialControl) {
                    $firstResult = $firstTask.GetAwaiter().GetResult()
                }
                if ($firstResult -ne 37 -or $otherResult -ne 37) { throw 'Wrong synthetic results.' }
                $stage = 'xe_read'
                $metrics = Read-CompileWitnesses $observer $xeName $batchByActor
            } finally {
                $other.Dispose()
            }
        } finally {
            $second.Dispose()
        }
    } finally {
        $command.Dispose()
    }
} catch {
    throw "OPTSP compile witness failed at stage '$stage'."
} finally {
    try {
        if ($xeName) {
            $remaining = Invoke-XeCommand $observer @"
IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = N'$xeName')
    DROP EVENT SESSION [$xeName] ON SERVER;
SELECT CONVERT(int, CASE WHEN
    EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = N'$xeName')
    OR EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name = N'$xeName') THEN 1 ELSE 0 END);
"@ -Scalar
            if ($remaining -isnot [int] -or $remaining -ne 0) {
                throw 'XE component did not verify cleanup.'
            }
        }
    } finally {
        $actor.Dispose()
        $observer.Dispose()
    }
}

$overlap = $metrics.sequence_interleaved -and $metrics.timestamp_interval_ticks -gt 0
if ($SequentialControl -and ($metrics.sequence_interleaved -or $metrics.timestamp_interval_ticks -gt 0)) {
    throw 'Sequential control produced overlapping compile witness events.'
}
if ($SequentialControl -and $IdenticalBatch -and
    ($metrics.compile_actors.Count -ne 1 -or $metrics.compile_actors[0] -ne $sessionId)) {
    throw 'Identical sequential control requires exactly one first compilation, from the first request.'
}
$decision = 'NOT_PROVEN'
if ($SequentialControl) {
    $decision = 'CONTROL_PASS'
} elseif ($overlap) {
    $decision = 'OVERLAP_OBSERVED'
}
[ordered]@{
    decision = $decision
    build = $requiredBuild
    identical_batch = [bool]$IdenticalBatch
    first_compile_count = $metrics.compile_actors.Count
    ce_counts = $metrics.ce_counts
    sequence_interleaved = $metrics.sequence_interleaved
    timestamp_interval_ticks = $metrics.timestamp_interval_ticks
    xe_cleanup = 'PASS'
} | ConvertTo-Json -Compress
