#Requires -Version 7.2
# Internal worker for run_optsp_paired.py. Its stdout is a bounded private record.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('\A127\.0\.0\.1,[1-9][0-9]{0,4}\z')][string] $Server,
    [Parameter(Mandatory)][ValidatePattern('\AOptspProbe_[a-f0-9]{32}\z')][string] $Database,
    [Parameter(Mandatory)][ValidatePattern('\A[a-f0-9]{32}\z')][string] $Owner,
    [Parameter(Mandatory)][ValidateSet(0, 1)][int] $Option,
    [Parameter(Mandatory)][ValidateSet('PAIR', 'SEQUENTIAL', 'DISTINCT')][string] $Variant
)

$ErrorActionPreference = 'Stop'
$password = [Environment]::GetEnvironmentVariable('SQLCMDPASSWORD', 'Process')
if ([int]($Server.Split(',')[1]) -gt 65535 -or $Database -cne ('OptspProbe_' + $Owner) -or
    [string]::IsNullOrEmpty($password) -or ($Option -eq 1 -and $Variant -ne 'PAIR')) {
    throw 'Invalid isolated OPTSP worker arguments.'
}
$workload = Import-PowerShellDataFile -LiteralPath (Join-Path $PSScriptRoot 'OptspCompileWorkload.psd1')

function Local-Sql($connection, [string]$sql, [switch]$scalar) {
    $cmd=$connection.CreateCommand()
    try {
        $cmd.CommandTimeout=5
        $cmd.CommandText=$sql
        if($scalar){return $cmd.ExecuteScalar()}
        [void]$cmd.ExecuteNonQuery()
    } finally { $cmd.Dispose() }
}
$cs=[System.Data.SqlClient.SqlConnectionStringBuilder]::new()
$cs['Data Source']="tcp:$Server"
$cs['Initial Catalog']='master'
$cs['User ID']='sa'
$cs['Password'] = $password
$cs['Encrypt']=$true
$cs['TrustServerCertificate']=$true
$cs['Pooling']=$false
$cs['Connect Timeout']=5
$cs['ConnectRetryCount']=0
$cs['MultipleActiveResultSets']=$false
$connections=1..3 | ForEach-Object { [System.Data.SqlClient.SqlConnection]::new($cs.ConnectionString) }
$observer=$connections[0]
$actors=@($connections[1],$connections[2])
$xeName="optsp_on_$Owner"
$started=$false
$stage='preflight'
try {
    $observer.Open()
    $dbid=Local-Sql $observer @"
SET NOCOUNT ON;
IF SERVERPROPERTY('ProductVersion')<>N'17.0.5065.9'
 OR SERVERPROPERTY('Edition')<>N'Enterprise Developer Edition (64-bit)'
 OR (SELECT COUNT(*) FROM sys.databases WHERE database_id > 4)<>6
 OR NOT EXISTS (SELECT 1 FROM [$Database].sys.extended_properties WHERE class=0 AND name COLLATE Latin1_General_100_BIN2=N'OptspOwner'
        AND DATALENGTH(CONVERT(nvarchar(4000),value))=64
        AND CONVERT(nvarchar(4000),value) COLLATE Latin1_General_100_BIN2=N'$Owner')
 THROW 51000,'invalid isolated discovery target',1;
SELECT CONVERT(int, DB_ID(N'$Database'));
"@ -Scalar
    if ($dbid -isnot [int] -or $dbid -le 4) { throw 'Invalid database.' }
    $ids=@(foreach($actor in $actors) {
        $actor.Open()
        $id=Local-Sql $actor 'SELECT CONVERT(int,@@SPID);' -Scalar
        if($id -isnot [int] -or $id -le 0) { throw 'Invalid actor.' }
        $actor.ChangeDatabase($Database)
        $id
    })
    if ($ids[0] -eq $ids[1]) { throw 'Duplicate actor.' }
    $censusSql=@"
SELECT COUNT_BIG(*) FROM sys.dm_exec_cached_plans AS p
CROSS APPLY sys.dm_exec_plan_attributes(p.plan_handle) AS a
WHERE a.attribute='dbid' AND TRY_CONVERT(int,a.value)=$dbid;
"@
    $census=$null
    $optionSql=@"
SELECT CASE WHEN EXISTS
 (SELECT 1 FROM sys.databases WHERE database_id=$dbid AND compatibility_level=170 AND is_auto_update_stats_on=0)
 AND EXISTS (SELECT 1 FROM [$Database].sys.database_scoped_configurations WHERE name=N'OPTIMIZED_SP_EXECUTESQL' AND TRY_CONVERT(int,value)=$Option)
 THEN 1 ELSE 0 END;
"@
    if ((Local-Sql $observer $optionSql -Scalar) -ne 1) { throw 'Unexpected scoped profile.' }
    function Digest([string]$value){
        return [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($value))).ToLowerInvariant()
    }
    $profileSql=@"
SET NOCOUNT ON;
IF EXISTS(SELECT 1 FROM [$Database].sys.objects WHERE is_ms_shipped=0)
    THROW 51004,'unexpected schema in constant fixture database',1;
SELECT (SELECT
    (SELECT compatibility_level, recovery_model, collation_name, owner_sid, is_read_only,
        snapshot_isolation_state,is_read_committed_snapshot_on,is_ansi_null_default_on,is_ansi_nulls_on,
        is_ansi_padding_on,is_ansi_warnings_on,is_arithabort_on,is_concat_null_yields_null_on,
        is_numeric_roundabort_on,is_quoted_identifier_on,is_parameterization_forced,is_cursor_close_on_commit_on,
        is_auto_create_stats_on,is_auto_update_stats_on,is_auto_update_stats_async_on,is_query_store_on,
        is_db_chaining_on,is_trustworthy_on
     FROM sys.databases WHERE database_id=$dbid FOR JSON PATH,INCLUDE_NULL_VALUES) AS database_options,
    (SELECT name,CONVERT(nvarchar(256),value) AS config_value,is_value_default
     FROM [$Database].sys.database_scoped_configurations WHERE name<>N'OPTIMIZED_SP_EXECUTESQL'
     ORDER BY name FOR JSON PATH,INCLUDE_NULL_VALUES) AS scoped_options,
    (SELECT name,type,authentication_type,default_schema_name FROM [$Database].sys.database_principals
     ORDER BY name FOR JSON PATH,INCLUDE_NULL_VALUES) AS principals,
    (SELECT class,major_id,minor_id,grantee_principal_id,grantor_principal_id,type,state
     FROM [$Database].sys.database_permissions ORDER BY class,major_id,minor_id,grantee_principal_id,grantor_principal_id,type,state
     FOR JSON PATH,INCLUDE_NULL_VALUES) AS permissions,
    (SELECT role_principal_id,member_principal_id FROM [$Database].sys.database_role_members
     ORDER BY role_principal_id,member_principal_id FOR JSON PATH,INCLUDE_NULL_VALUES) AS roles,
    (SELECT n.actor,s.language,s.date_format,s.date_first,s.quoted_identifier,s.arithabort,
        s.ansi_null_dflt_on,s.ansi_defaults,s.ansi_warnings,s.ansi_padding,s.ansi_nulls,s.concat_null_yields_null,
        s.transaction_isolation_level,s.lock_timeout,s.deadlock_priority,s.text_size
     FROM (VALUES (0,$($ids[0])),(1,$($ids[1]))) n(actor,session_id)
     JOIN sys.dm_exec_sessions s ON s.session_id=n.session_id
     WHERE s.database_id=$dbid ORDER BY n.actor FOR JSON PATH,INCLUDE_NULL_VALUES) AS session_options,
    0 AS user_objects,0 AS user_rows,0 AS user_statistics
    FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
"@
    function Read-Profile {
        $value=Local-Sql $observer $profileSql -Scalar
        if($value -isnot [string] -or $value.Length -gt 65536){throw 'Invalid bounded profile.'}
        $parsed=$value | ConvertFrom-Json
        $sessionOptions=$parsed.session_options
        if ($sessionOptions -is [string]) { $sessionOptions=$sessionOptions | ConvertFrom-Json }
        if (@($sessionOptions).Count -ne 2) { throw 'Missing session settings.' }
        Digest $value
    }
    $incarnationSql="SELECT CONVERT(varchar(33),sqlserver_start_time,126) FROM sys.dm_os_sys_info;"
    $engineBefore=Digest ([string](Local-Sql $observer $incarnationSql -Scalar))
    $profileBefore=Read-Profile
    $stage='xe_create'
    $actorsFilter="(([sqlserver].[session_id]=($($ids[0]))) OR ([sqlserver].[session_id]=($($ids[1]))))"
    $filter="WHERE (($actorsFilter) AND ([sqlserver].[database_id]=($dbid)))"
    $actions='ACTION(package0.event_sequence,sqlserver.session_id,sqlserver.database_id)'
    $xMode=Local-Sql $observer @"
SELECT MIN(m.map_key) FROM sys.dm_xe_map_values m JOIN sys.dm_xe_packages p ON p.guid=m.object_package_guid
WHERE p.name=N'sqlserver' AND m.name=N'lock_mode' AND m.map_value=N'X' HAVING COUNT_BIG(*)=1;
"@ -Scalar
    if($null -eq $xMode -or $xMode -is [DBNull]) { throw 'Unbound X lock mode.' }
    $lockFilter="WHERE (($actorsFilter) AND ([database_id]=($dbid)) AND ([mode]=($xMode)))"
    if ((Local-Sql $observer "SELECT COUNT(*) FROM sys.server_event_sessions WHERE name=N'$xeName';" -Scalar) -ne 0) {
        throw 'XE session name already exists.'
    }
    $started = $true
    Local-Sql $observer @"
CREATE EVENT SESSION [$xeName] ON SERVER
ADD EVENT sqlserver.rpc_starting($actions $filter),
ADD EVENT sqlserver.rpc_completed($actions $filter),
ADD EVENT sqlserver.sql_statement_post_compile(SET collect_statement=(1) $actions $filter),
ADD EVENT sqlserver.query_optimizer_estimate_cardinality(ACTION(package0.event_sequence,sqlserver.session_id,sqlserver.database_id,sqlserver.sql_text) $filter),
ADD EVENT sqlserver.sp_statement_completed(ACTION(package0.event_sequence,sqlserver.session_id,sqlserver.database_id,sqlserver.plan_handle) $filter),
ADD EVENT sqlos.wait_info(SET collect_wait_resource_desc=(1) $actions WHERE (($actorsFilter) AND ([wait_type]=(5)))),
ADD EVENT sqlserver.lock_acquired(SET collect_resource_description=(1) $actions $lockFilter),
ADD EVENT sqlserver.lock_released(SET collect_resource_description=(1) $actions $lockFilter),
ADD EVENT sqlserver.spexec_batch_compilation_serialization($actions $filter),
ADD EVENT sqlserver.spexec_batch_compilation_serialization_telemetry($actions $filter)
ADD TARGET package0.ring_buffer(SET max_memory=(1024))
WITH(MAX_MEMORY=4 MB, MAX_DISPATCH_LATENCY=1 SECONDS, STARTUP_STATE=OFF);
ALTER EVENT SESSION [$xeName] ON SERVER STATE=START;
"@
    $statement = $workload.Batch
    $texts = @($statement, $statement)
    if ($Variant -eq 'DISTINCT') { $texts[1] = $workload.DistinctBatch }
    $stage='rpc'
    $commands=@(foreach($ordinal in 0..1){
        $actor=$actors[$ordinal]
        $cmd=$actor.CreateCommand()
        $cmd.CommandTimeout=5
        $cmd.CommandType=[System.Data.CommandType]::StoredProcedure
        $cmd.CommandText='sys.sp_executesql'
        $cmd.Parameters.Add('@stmt',[System.Data.SqlDbType]::NVarChar,-1).Value=$texts[$ordinal]
        $cmd.Parameters.Add('@params',[System.Data.SqlDbType]::NVarChar,-1).Value=$workload.Parameters
        $cmd.Parameters.Add('@value',[System.Data.SqlDbType]::Int).Value=$workload.Value
        $cmd
    })
    $barrierIds=@()
    function Confirm-ColdCache {
        $observer.ChangeDatabase($Database)
        try {
            Local-Sql $observer @"
IF DB_ID()<>$dbid OR NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class=0 AND name COLLATE Latin1_General_100_BIN2=N'OptspOwner'
        AND DATALENGTH(CONVERT(nvarchar(4000),value))=64
        AND CONVERT(nvarchar(4000),value) COLLATE Latin1_General_100_BIN2=N'$Owner')
    THROW 51007,'cache reset target is not the owned database',1;
ALTER DATABASE SCOPED CONFIGURATION CLEAR PROCEDURE_CACHE;
"@
        } finally { $observer.ChangeDatabase('master') }
        $count=Local-Sql $observer $censusSql -Scalar
        if($count -ne 0){throw "Cold-plan census after scoped reset returned $count entries."}
        return $count
    }
    try {
        if($Variant -eq 'SEQUENTIAL'){
            $census=Confirm-ColdCache
            $a=$commands[0].ExecuteScalarAsync()
            if($a.GetAwaiter().GetResult() -ne $workload.Value){throw 'Wrong first result.'}
            $b=$commands[1].ExecuteScalarAsync()
            if($b.GetAwaiter().GetResult() -ne $workload.Value){throw 'Wrong second result.'}
        } else {
            Add-Type -TypeDefinition @'
using System;
using System.Data.Common;
using System.Threading.Tasks;
public static class SqlPerfOptspGate {
    public static async Task<object> Execute(DbCommand command, Task gate) {
        await gate.ConfigureAwait(false);
        return await command.ExecuteScalarAsync().ConfigureAwait(false);
    }
}
'@
            $gate=[System.Threading.Tasks.TaskCompletionSource[bool]]::new([System.Threading.Tasks.TaskCreationOptions]::RunContinuationsAsynchronously)
            $a=[SqlPerfOptspGate]::Execute($commands[0],$gate.Task)
            $b=[SqlPerfOptspGate]::Execute($commands[1],$gate.Task)
            if($a.IsCompleted -or $b.IsCompleted -or $gate.Task.IsCompleted){throw 'Barrier registration failed.'}
            $barrierIds=@($ids)
            $census=Confirm-ColdCache
            $gate.SetResult($true)
            if($a.GetAwaiter().GetResult() -ne $workload.Value -or $b.GetAwaiter().GetResult() -ne $workload.Value){throw 'Wrong result.'}
        }
    } finally { foreach($cmd in $commands){$cmd.Dispose()} }
    $stage='xe_read'
    $until=[System.Diagnostics.Stopwatch]::StartNew()
    $root=$null
    do {
        $xml=Local-Sql $observer @"
SELECT CONVERT(nvarchar(max),t.target_data)
FROM sys.dm_xe_sessions s JOIN sys.dm_xe_session_targets t ON s.address=t.event_session_address
WHERE s.name=N'$xeName' AND t.target_name=N'ring_buffer' AND s.dropped_event_count=0
AND s.dropped_buffer_count=0 AND s.largest_event_dropped_size=0 AND s.pending_buffers=0;
"@ -Scalar
        if($xml -is [string] -and $xml.Length -le 2097152){
            $doc=[System.Xml.XmlDocument]::new()
            $doc.XmlResolver=$null
            $settings=[System.Xml.XmlReaderSettings]::new()
            $settings.DtdProcessing=[System.Xml.DtdProcessing]::Prohibit
            $settings.XmlResolver=$null
            $settings.MaxCharactersInDocument=2097152
            $source=[System.IO.StringReader]::new($xml)
            try {
                $reader=[System.Xml.XmlReader]::Create($source,$settings)
                try { $doc.Load($reader) } finally { $reader.Dispose() }
            } finally { $source.Dispose() }
            $root=$doc.DocumentElement
            if($root.SelectNodes("event[@name='rpc_completed']").Count -eq 2){break}
        }
        Start-Sleep -Milliseconds 100
    } while($until.Elapsed.TotalSeconds -lt 7)
    if ($null -eq $root -or $root.Name -cne 'RingBufferTarget' -or $root.GetAttribute('truncated') -ne '0' -or $root.GetAttribute('droppedCount') -ne '0'){
        $diag=Local-Sql $observer @"
SELECT CONCAT(s.dropped_event_count,'|',s.dropped_buffer_count,'|',s.largest_event_dropped_size,'|',s.pending_buffers,'|',DATALENGTH(t.target_data))
FROM sys.dm_xe_sessions s JOIN sys.dm_xe_session_targets t ON s.address=t.event_session_address
WHERE s.name=N'$xeName' AND t.target_name=N'ring_buffer';
"@ -Scalar
        $rootSummary=if($null -eq $root){'absent'}else{ "$($root.Name)|$($root.GetAttribute('truncated'))|$($root.GetAttribute('droppedCount'))|$($root.GetAttribute('eventCount'))" }
        throw "Incomplete ring target: counters=$diag root=$rootSummary."
    }
    $all=@($root.SelectNodes('event'))
    if ($root.GetAttribute('eventCount') -ne [string]$all.Count -or $root.GetAttribute('totalEventsProcessed') -ne [string]$all.Count){throw 'Partial ring capture.'}
    $ord=@($all | ForEach-Object {
        $event=$_
        [pscustomobject]@{
            Id=[int]$event.SelectSingleNode("action[@name='session_id']/value").InnerText
            Db=[int]$event.SelectSingleNode("action[@name='database_id']/value").InnerText
            Seq=[long]$event.SelectSingleNode("action[@name='event_sequence']/value").InnerText
            Name=$event.GetAttribute('name')
            Time=[DateTimeOffset]::ParseExact($event.GetAttribute('timestamp'), "yyyy-MM-dd'T'HH:mm:ss.FFFFFFF'Z'", [cultureinfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal).UtcTicks
            Package=$event.GetAttribute('package')
            Node=$event
        }
    } | Sort-Object Seq)
    if (@($ord.Seq | Sort-Object -Unique).Count -ne $ord.Count) {
        throw 'Duplicate event sequence.'
    }
    foreach ($event in $ord) {
        $expectedPackage = if ($event.Name -eq 'wait_info') { 'sqlos' } else { 'sqlserver' }
        if ($event.Id -notin $ids -or $event.Db -ne $dbid -or $event.Package -cne $expectedPackage) {
            throw 'Unbound event.'
        }
    }
    $handles=@()
    $origin=($ord | Sort-Object Time | Select-Object -First 1).Time
    $runs=@(foreach($id in $ids) {
        $actorIndex=[array]::IndexOf($ids,$id)
        $expectedText=$texts[$actorIndex]
        $own=@($ord | Where-Object Id -eq $id)
        $edges=@($own | Where-Object Name -in @('rpc_starting','rpc_completed'))
        if($edges.Count -ne 2 -or $edges[0].Name -ne 'rpc_starting' -or $edges[1].Name -ne 'rpc_completed'){throw 'Unbound RPC.'}
        foreach($edge in $edges){
            if($edge.Node.SelectSingleNode("data[@name='object_name']/value").InnerText -cne 'sp_executesql' -or
               !$edge.Node.SelectSingleNode("data[@name='statement']/value").InnerText.Contains($expectedText,[StringComparison]::Ordinal)){throw 'Unexpected RPC input.'}
        }
        $stm=@($own | Where-Object Name -eq 'sp_statement_completed')
        if($stm.Count -ne 1 -or $stm[0].Seq -le $edges[0].Seq -or $stm[0].Seq -ge $edges[1].Seq -or
           $stm[0].Node.SelectSingleNode("data[@name='statement']/value").InnerText -cne $expectedText.TrimEnd(';')){throw 'Unbound statement.'}
        $handles+=($stm[0].Node.SelectSingleNode("action[@name='plan_handle']/value").InnerText)
        $compiles=@($own | Where-Object Name -eq 'sql_statement_post_compile')
        $estimates=@($own | Where-Object Name -eq 'query_optimizer_estimate_cardinality')
        if($compiles.Count -gt 1 -or ($compiles.Count -eq 0 -and $estimates.Count)){throw 'Ambiguous compilation.'}
        foreach($compile in $compiles){
            if($compile.Seq -le $edges[0].Seq -or $compile.Seq -ge $stm[0].Seq -or
               $compile.Node.SelectSingleNode("data[@name='statement']/value").InnerText -cne $expectedText.TrimEnd(';') -or
               $compile.Node.SelectSingleNode("data[@name='is_recompile']/value").InnerText -cne 'false'){throw 'Unbound compile.'}
        }
        foreach($ce in $estimates){
            if($ce.Seq -le $edges[0].Seq -or $ce.Seq -ge $compiles[0].Seq -or
               !$ce.Node.SelectSingleNode("action[@name='sql_text']/value").InnerText.Contains($expectedText,[StringComparison]::Ordinal)){throw 'Unbound estimate.'}
        }
        [ordered]@{
            ordinal=$actorIndex;
            request_batch_digest=Digest ($expectedText + '|' + $workload.Parameters);
            rpc_start=($edges[0].Time-$origin);rpc_end=($edges[1].Time-$origin);statement_end=($stm[0].Time-$origin)
            rpc_start_ordinal=$edges[0].Seq;rpc_end_ordinal=$edges[1].Seq;statement_end_ordinal=$stm[0].Seq
            compile_end_ordinal=if($compiles.Count){$compiles[0].Seq}else{$null}
            compile_end=if($compiles.Count){$compiles[0].Time-$origin}else{$null}
            first_estimate=if($estimates.Count){$estimates[0].Time-$origin}else{$null}
            first_estimate_ordinal=if($estimates.Count){$estimates[0].Seq}else{$null}
        }
    })
    $witness = @($ord | Where-Object Name -eq 'wait_info' | ForEach-Object {
        $description = [string]$_.Node.SelectSingleNode("data[@name='wait_resource_desc']/value").InnerText
        [ordered]@{
            ordinal = $_.Seq
            ticks = $_.Time - $origin
            actor = [array]::IndexOf($ids, $_.Id)
            opcode = $_.Node.SelectSingleNode("data[@name='opcode']/text").InnerText
            label = [regex]::Replace($description, '[0-9]+', 'N')
            numeric = @([regex]::Matches($description, '[0-9]+') | ForEach-Object Value)
        }
    })
    $objectLocks = @($ord | Where-Object Name -in @('lock_acquired', 'lock_released') | ForEach-Object {
        if ($_.Node.SelectSingleNode("data[@name='resource_type']/text").InnerText -eq 'OBJECT') {
            $description = [string]$_.Node.SelectSingleNode("data[@name='resource_description']/value").InnerText
            [ordered]@{
                name = $_.Name
                ordinal = $_.Seq
                ticks = $_.Time - $origin
                actor = [array]::IndexOf($ids, $_.Id)
                rawfields = @(foreach ($field in @('object_id', 'resource_0', 'resource_1', 'resource_2')) {
                    [string]$_.Node.SelectSingleNode("data[@name='$field']/value").InnerText
                })
                description = [regex]::Replace($description, '[0-9]+', 'N')
            }
        }
    })
    $cacheText=('(' + $workload.Parameters + ')' + $statement).Replace("'","''")
    $prepared=Local-Sql $observer @"
SELECT CASE WHEN COUNT_BIG(*)=1 THEN MAX(CONVERT(varchar(128), p.plan_handle, 2)) END
FROM sys.dm_exec_cached_plans p CROSS APPLY sys.dm_exec_sql_text(p.plan_handle) t
CROSS APPLY sys.dm_exec_plan_attributes(p.plan_handle) a
WHERE t.text COLLATE Latin1_General_100_BIN2=N'$cacheText' AND DATALENGTH(t.text)=DATALENGTH(N'$cacheText')
  AND p.objtype='Prepared' AND a.attribute='dbid' AND TRY_CONVERT(int,a.value)=$dbid;
"@ -Scalar
    $cache_match=($prepared -is [string] -and $prepared -match '^[0-9a-f]{88}$' -and $handles[0] -eq $prepared -and $handles[1] -eq $prepared)
    if ((Local-Sql $observer $optionSql -Scalar) -ne 1) { throw 'Scoped profile changed.' }
    $out=[ordered]@{
        status='OBSERVED'
        option=$Option
        variant=$Variant
        actors=$runs
        db_id=$dbid
        instance_before=$engineBefore
        instance_after=Digest ([string](Local-Sql $observer $incarnationSql -Scalar))
        profile_before=$profileBefore
        profile_after=Read-Profile
        cache_before=$census
        barrier_actors=@($barrierIds | ForEach-Object { [array]::IndexOf($ids,$_) })
        batch_digest=Digest ($statement + "|" + $workload.Parameters)
        workload_digest=Digest ((@($texts[0], $texts[1], $workload.Parameters) + (@($workload.Value) * 4)) -join "|")
        wait_key_witness=$witness
        object_lock_witness=$objectLocks
        prepared_entry_matches=$cache_match
    }
} catch { throw "OPTSP worker failed at stage $stage." } finally {
    try {
        if ($started) {
            $remaining=Local-Sql $observer @"
IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'$xeName') DROP EVENT SESSION [$xeName] ON SERVER;
SELECT CONVERT(int, CASE WHEN EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'$xeName') OR EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=N'$xeName') THEN 1 ELSE 0 END);
"@ -Scalar
            if($remaining -ne 0){throw 'XE cleanup unconfirmed.'}
        }
    } finally { foreach($c in $connections){$c.Dispose()} }
}
$out.xe_cleanup='PASS'
$out | ConvertTo-Json -Depth 6 -Compress
