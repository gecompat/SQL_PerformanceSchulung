[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('\A127\.0\.0\.1,[1-9][0-9]{0,4}\z')]
    [string] $Server,

    [Parameter(Mandatory)]
    [switch] $ConfirmDisposableInstance,

    [switch] $CheckXeRequestBoundaries
)

$ErrorActionPreference = 'Stop'
$requiredBuild = '17.0.5065.9'
$requestBoundaryEvents = @('rpc_starting', 'rpc_completed', 'sql_batch_starting', 'sql_batch_completed')
$password = [Environment]::GetEnvironmentVariable('SQLCMDPASSWORD', 'Process')
if (-not $ConfirmDisposableInstance -or [string]::IsNullOrEmpty($password) -or
    [int]($Server.Split(',')[1]) -gt 65535) {
    throw 'RPC component requires a loopback port, disposable-instance confirmation and SQLCMDPASSWORD.'
}

function Read-InputEvent($Observer, [int] $SessionId) {
    $command = $Observer.CreateCommand()
    $command.CommandTimeout = 5
    $command.CommandText = @'
SELECT event_type, event_info
FROM sys.dm_exec_input_buffer(@session_id, NULL);
'@
    $command.Parameters.Add('@session_id', [System.Data.SqlDbType]::Int).Value = $SessionId
    try {
        $reader = $command.ExecuteReader()
        try {
            if (-not $reader.Read() -or $reader.IsDBNull(0) -or $reader.IsDBNull(1)) {
                throw 'RPC component has no complete input-buffer record.'
            }
            $record = @{ Type = $reader.GetString(0); Text = $reader.GetString(1) }
            if ($reader.Read() -or $reader.NextResult()) {
                throw 'RPC component has more than one input-buffer record.'
            }
            return $record
        } finally {
            $reader.Dispose()
        }
    } finally {
        $command.Dispose()
    }
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

function Read-XeRequestBoundaries($Observer, [string] $Name, [int] $SessionId,
                                  [string] $Statement, [string] $OuterBatch) {
    $sql = @"
SELECT CONVERT(nvarchar(max), t.target_data)
FROM sys.dm_xe_sessions AS s
JOIN sys.dm_xe_session_targets AS t ON t.event_session_address = s.address
WHERE s.name = N'$Name' AND t.target_name = N'ring_buffer'
    AND s.dropped_event_count = 0 AND s.dropped_buffer_count = 0
    AND s.largest_event_dropped_size = 0;
"@
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    do {
        $snapshot = Invoke-XeCommand $Observer $sql -Scalar
        if ($snapshot -isnot [string] -or $snapshot.Length -gt 524288) {
            throw 'XE component lost its bounded ring buffer.'
        }
        $settings = [System.Xml.XmlReaderSettings]::new()
        $settings.DtdProcessing = [System.Xml.DtdProcessing]::Prohibit
        $settings.MaxCharactersInDocument = 524288
        $source = [System.IO.StringReader]::new($snapshot)
        try {
            $reader = [System.Xml.XmlReader]::Create($source, $settings)
            try {
                $document = [System.Xml.XmlDocument]::new()
                $document.Load($reader)
            } finally {
                $reader.Dispose()
            }
        } finally {
            $source.Dispose()
        }
        $root = $document.DocumentElement
        $events = $root.SelectNodes('event')
        if ($root.Name -cne 'RingBufferTarget' -or $root.GetAttribute('truncated') -cne '0' -or
            $root.GetAttribute('droppedCount') -cne '0' -or $events.Count -gt $requestBoundaryEvents.Count -or
            $root.GetAttribute('eventCount') -cne [string]$events.Count -or
            $root.GetAttribute('totalEventsProcessed') -cne [string]$events.Count) {
            throw 'XE component captured incomplete or unexpected ring data.'
        }
        if ($events.Count -eq $requestBoundaryEvents.Count) {
            $last = 0L
            for ($i = 0; $i -lt $events.Count; $i++) {
                $event = $events[$i]
                $sequence = 0L
                if ($event.GetAttribute('name') -cne $requestBoundaryEvents[$i] -or
                    $event.GetAttribute('package') -cne 'sqlserver' -or
                    $event.SelectSingleNode("action[@name='session_id']/value").InnerText -cne [string]$SessionId -or
                    -not [long]::TryParse($event.SelectSingleNode("action[@name='event_sequence']/value").InnerText, [ref]$sequence) -or
                    $sequence -le $last) {
                    throw 'XE component did not capture the expected ordered request boundaries.'
                }
                if ($event.SelectSingleNode("action[@name='database_id']/value").InnerText -cne '1') {
                    throw 'XE component observed an unexpected request database.'
                }
                if ($i -lt 2) {
                    $objectName = $event.SelectSingleNode("data[@name='object_name']/value").InnerText
                    $rpcText = $event.SelectSingleNode("data[@name='statement']/value").InnerText
                    if ($objectName -cne 'sp_executesql' -or -not $rpcText.Contains($Statement, [StringComparison]::Ordinal)) {
                        throw 'XE component could not identify the synthetic RPC.'
                    }
                } elseif ($event.SelectSingleNode("data[@name='batch_text']/value").InnerText -cne $OuterBatch) {
                    throw 'XE component could not identify the synthetic outer batch.'
                }
                $last = $sequence
            }
            return $requestBoundaryEvents
        }
        Start-Sleep -Milliseconds 100
    } while ($timer.Elapsed.TotalSeconds -lt 6)
    throw 'XE component did not receive all terminal events within six seconds.'
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
    THROW 51006, 'NOT_PROVEN: unexpected RPC component target.', 1;
SELECT CONVERT(int, @@SPID);
'@
        $sessionId = $command.ExecuteScalar()
        if ($sessionId -isnot [int] -or $sessionId -le 0) {
            throw 'RPC component has no actor session.'
        }

        if ($CheckXeRequestBoundaries) {
            $stage = 'xe_start'
            $xeName = 'optsp_rpc_' + [guid]::NewGuid().ToString('N')
            $events = foreach ($event in $requestBoundaryEvents) {
                "ADD EVENT sqlserver.$event(ACTION(package0.event_sequence, sqlserver.database_id, sqlserver.session_id) WHERE ([sqlserver].[session_id]=($sessionId)))"
            }
            $definition = $events -join ",`n"
            Invoke-XeCommand $observer @"
CREATE EVENT SESSION [$xeName] ON SERVER
$definition
ADD TARGET package0.ring_buffer(SET max_memory=(256))
WITH (MAX_MEMORY=1 MB, MAX_DISPATCH_LATENCY=1 SECONDS, STARTUP_STATE=OFF);
"@
            Invoke-XeCommand $observer "ALTER EVENT SESSION [$xeName] ON SERVER STATE=START;"
        }

        $statement = 'SELECT @value /* OPTSP_RPC_COMPONENT */;'
        $parameters = '@value int'
        $stage = 'stored_procedure'
        $command.CommandType = [System.Data.CommandType]::StoredProcedure
        $command.CommandText = 'sys.sp_executesql'
        $command.Parameters.Add('@stmt', [System.Data.SqlDbType]::NVarChar, -1).Value = $statement
        $command.Parameters.Add('@params', [System.Data.SqlDbType]::NVarChar, -1).Value = $parameters
        $command.Parameters.Add('@value', [System.Data.SqlDbType]::Int).Value = 37
        $procedureResult = $command.ExecuteScalar()
        $procedure = Read-InputEvent $observer $sessionId
        if ($procedureResult -isnot [int] -or $procedureResult -ne 37 -or $procedure.Type -cne 'Language Event' -or
            $procedure.Text -cne "($parameters)$statement") {
            throw 'Input-buffer component did not reproduce the stored procedure shape.'
        }

        $stage = 'text_command'
        $command.Parameters.Clear()
        $command.CommandType = [System.Data.CommandType]::Text
        $command.CommandText = "EXEC sys.sp_executesql N'$statement', N'$parameters', 37;"
        $textResult = $command.ExecuteScalar()
        $text = Read-InputEvent $observer $sessionId
        if ($textResult -isnot [int] -or $textResult -ne 37 -or $text.Type -cne 'Language Event' -or
            $text.Text -cne $command.CommandText) {
            throw 'Input-buffer component did not reproduce the outer SQL language batch.'
        }
        if ($CheckXeRequestBoundaries) {
            $stage = 'xe_read'
            $boundaries = Read-XeRequestBoundaries $observer $xeName $sessionId $statement $command.CommandText
        }
    } finally {
        $command.Dispose()
    }
} catch {
    throw "OPTSP RPC component failed at stage '$stage'."
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

$result = [ordered]@{
    status = 'PASS'
    build = $requiredBuild
    stored_procedure_event = $procedure.Type
    text_command_event = $text.Type
    stored_procedure_shape = 'parameterized_statement'
    text_command_shape = 'outer_exec_batch'
    result = $procedureResult
}
if ($CheckXeRequestBoundaries) {
    $result['xe_request_boundaries'] = $boundaries
    $result['xe_cleanup'] = 'PASS'
}
$result | ConvertTo-Json -Compress
