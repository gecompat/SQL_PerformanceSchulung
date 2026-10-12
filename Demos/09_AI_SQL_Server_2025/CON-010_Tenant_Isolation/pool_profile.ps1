param([Parameter(Mandatory)][string]$Admission,[Parameter(Mandatory)][string]$AdmissionSha)
$ErrorActionPreference='Stop'
$script:Operations=[Collections.Generic.List[object]]::new();$script:Checkout=0;
$script:Unknown=$false;$script:Records=[Collections.Generic.List[object]]::new()
$script:Refs=[Collections.Generic.List[object]]::new();$script:Secrets=[Collections.Generic.List[object]]::new()
$script:Owner=$null;$script:Cleanup='NOT_ESTABLISHED';$script:Remaining=@();$script:Status='FAIL';$script:Phase='ASSEMBLY';$script:Fault=$null
$Database='SQLPERF_LAB_CON010_POOLPUBLIC'
$Dll='C:\Program Files\PowerShell\7\System.Data.SqlClient.dll'
$Exe='C:\Program Files\PowerShell\7\pwsh.exe'
function Decode([string]$Text){$Text | ConvertFrom-Json -AsHashtable -DateKind String}
function Failure([Exception]$Exception){
    # No raw message, stack, connection string, credential or ENV is emitted.
    $types=[Collections.Generic.List[string]]::new();$code=$null;$current=$Exception
    $known=@('POOL_ASSEMBLY_PATH','POOL_CREDENTIAL_BINDING','POOL_CREDENTIAL_INSTANCE','POOL_SECRET_CONNECTIONSTRING','POOL_SOURCE_PATH','POOL_SOURCE_CHANGED','POOL_AUTHORITY_CHANGED','POOL_ADMISSION_CHANGED','POOL_DEADLINE','POOL_OPEN_STATE','POOL_OPEN_REQUEST_UNKNOWN','POOL_COMMAND_DEADLINE','POOL_COMMAND_REQUEST_UNKNOWN','POOL_TYPED_VALUE','POOL_OWNER_POPULATION','POOL_CLOSE_STATE','POOL_PHYSICAL_POPULATION','POOL_PHYSICAL_RESIDUE','POOL_RESULT_CONTRACT','POOL_CREDENTIAL_OUTPUT','POOL_RECEIPT_BOUND')
    while($current -and $types.Count-lt6){
        $name=$current.GetType().FullName
        if($name -cnotmatch '^[A-Za-z][A-Za-z0-9_.]{0,159}$'){$name='System.Exception'}
        $types.Add($name)
        if($null-eq $code -and $current.Message -cin $known){$code=$current.Message}
        $current=$current.InnerException
    }
    return @{Phase=$script:Phase;Types=$types.ToArray();Code=$code}
}
function Hash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
if($AdmissionSha -cnotmatch '^[a-f0-9]{64}$' -or (Hash $Admission)-cne $AdmissionSha){throw 'POOL_ADMISSION_BINDING'}
$P=Decode (Get-Content -LiteralPath $Admission -Raw -Encoding utf8)
if($P.status-cne 'OWN_POOL_ADMITTED' -or $P.token-cnotmatch '^[A-F0-9]{16}$' -or $P.server-cnotmatch '^tcp:127\.0\.0\.1,[1-9][0-9]{0,4}$' -or $P.database-cne $Database -or $P.dbid -isnot [long] -and $P.dbid -isnot [int] -or $P.dbid-lt5 -or $P.seconds-le0 -or $P.seconds-gt40){throw 'POOL_INPUT_BINDING'}
$script:PrivateValues=@($env:SQLCMDPASSWORD,$env:TenantSecretA,$env:TenantSecretB,$env:TenantSecretU)
if(@($script:PrivateValues|Select-Object -Unique).Count-ne4 -or @($script:PrivateValues|Where-Object {$_ -cnotmatch '^[A-Za-z0-9!]{40,80}$'}).Count-ne0){throw 'POOL_CREDENTIAL_BINDING'}
$Clock=[Diagnostics.Stopwatch]::StartNew()
function Guard {
    if((Hash $Admission)-cne $AdmissionSha){throw 'POOL_ADMISSION_CHANGED'}
    if($Clock.Elapsed.TotalSeconds-ge $P.seconds){$script:Unknown=$true;throw 'POOL_DEADLINE'}
    if($P.source.Count-lt8){throw 'POOL_SOURCE_CHANGED'}
    foreach($entry in $P.source.GetEnumerator()){
        if($entry.Key-ceq 'HOST/SqlClient'){$path=$Dll}
        elseif($entry.Key-ceq 'HOST/PowerShell'){$path=$Exe}
        else{$path=[IO.Path]::GetFullPath((Join-Path $P.repo $entry.Key));if(-not $path.StartsWith($P.repo.TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'POOL_SOURCE_PATH'}}
        if((Hash $path)-cne $entry.Value){throw 'POOL_SOURCE_CHANGED'}
    }
}
function Secret([string]$Value){
    if($Value -cnotmatch '^[A-Za-z0-9!]{40,80}$'){throw 'POOL_CREDENTIAL_BINDING'}
    $secure=[Security.SecureString]::new();foreach($ch in $Value.ToCharArray()){$secure.AppendChar($ch)};$secure.MakeReadOnly();$script:Secrets.Add($secure);return $secure
}
function Connection([string]$Lane,[object]$Credential,[bool]$Pooling){
    Guard
    $builder=[Activator]::CreateInstance($BuilderType)
    # Builder implements IDictionary: PS property syntax can dispatch property
    # names as unsupported SQL keywords. Bind the actual public typed properties.
    $values=@{DataSource=[string]$P.server;InitialCatalog=$Database;ApplicationName=('SQLPERF_POOLPUBLIC_'+$P.token+'_'+$Lane);Pooling=$Pooling;MinPoolSize=0;MaxPoolSize=1;MultipleActiveResultSets=$false;Enlist=$false;ConnectTimeout=2;ConnectRetryCount=0;Encrypt=$true;TrustServerCertificate=$true}
    foreach($entry in $values.GetEnumerator()){$BuilderType.GetProperty($entry.Key).SetValue($builder,$entry.Value)}
    if($BuilderType.GetProperty('Password').GetValue($builder) -or $BuilderType.GetProperty('UserID').GetValue($builder)){throw 'POOL_SECRET_CONNECTIONSTRING'}
    $text=[string]$BuilderType.GetProperty('ConnectionString').GetValue($builder)
    $connection=[Activator]::CreateInstance($ConnectionType,@($text,$Credential))
    $sha=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($text)))
    return @{Connection=$connection;Key=$sha}
}
function Lane([object]$Connection){
    if($Connection.Credential.UserId-ceq 'sa'){return 'OWNER'}
    foreach($lane in @('A','B','U')){if($Connection.Credential.UserId-ceq $P.logins[$lane][0]){return $lane}}
    throw 'POOL_CREDENTIAL_BINDING'
}
function CredentialSafe([string]$Text){
    foreach($value in $script:PrivateValues){
        foreach($form in @($value,[Convert]::ToHexString([Text.Encoding]::UTF8.GetBytes($value)),[Convert]::ToHexString([Text.Encoding]::Unicode.GetBytes($value)))){
            if($Text.Contains($form,[StringComparison]::OrdinalIgnoreCase)){throw 'POOL_CREDENTIAL_OUTPUT'}
        }
    }
}
function Operation([string]$Kind,[object]$Connection,[string]$Text,[bool]$Returned){
    $digest=$null;CredentialSafe $Text
    if($Kind-ceq 'SCALAR'){$digest=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($Text))).ToLowerInvariant()}
    $script:Operations.Add(@{Ordinal=$script:Operations.Count;Operation=$Kind;Lane=(Lane $Connection);Checkout=$script:Checkout;Returned=$Returned;RequestEnd=$(if($Returned){'RETURNED_TO_CALLER'}else{'UNKNOWN'});ConfiguredTextSha256=$digest;TextScope=$(if($Kind-ceq 'SCALAR'){'CLIENT_CONFIGURED_SECRET_FREE_TEXT'}else{'NOT_APPLICABLE'})})
}
function Close([object]$Connection){
    Guard
    try{$Connection.Close();if($Connection.State.ToString()-cne 'Closed'){throw 'POOL_CLOSE_STATE'};Operation 'CLOSE' $Connection '' $true}
    catch{$script:Unknown=$true;Operation 'CLOSE' $Connection '' $false;throw}
}
function Open([object]$Connection){
    Guard
    try{$Connection.Open();if($Connection.State.ToString()-cne 'Open'){throw 'POOL_OPEN_STATE'};Operation 'OPEN' $Connection '' $true}
    catch{$script:Unknown=$true;Operation 'OPEN' $Connection '' $false;throw [InvalidOperationException]::new('POOL_OPEN_REQUEST_UNKNOWN',$_.Exception)}
}
function Scalar([object]$Connection,[string]$Text,[hashtable]$Values=@{}){
    Guard
    $command=$Connection.CreateCommand();$command.CommandText=$Text
    $remaining=$P.seconds-$Clock.Elapsed.TotalSeconds
    if($remaining-le1){$script:Unknown=$true;throw 'POOL_COMMAND_DEADLINE'}
    $command.CommandTimeout=[Math]::Min(4,[Math]::Floor($remaining))
    foreach($entry in $Values.GetEnumerator()){
        if($entry.Value -is [int]){$param=$command.Parameters.Add($entry.Key,[Data.SqlDbType]::Int);$param.Value=$entry.Value}
        elseif($entry.Value -is [string]){$param=$command.Parameters.Add($entry.Key,[Data.SqlDbType]::NVarChar,256);$param.Value=$entry.Value}
        else{throw 'POOL_TYPED_VALUE'}
    }
    try{$result=$command.ExecuteScalar();Operation 'SCALAR' $Connection $Text $true;return $result}
    catch{$script:Unknown=$true;Operation 'SCALAR' $Connection $Text $false;throw [InvalidOperationException]::new('POOL_COMMAND_REQUEST_UNKNOWN',$_.Exception)}
    finally{$command.Dispose()}
}
function Clear-OwnPools {
    foreach($lane in @('A','B','U')){Guard;$reference=$script:Refs[@('A','B','U').IndexOf($lane)];$null=$clear.Invoke($null,@($reference))}
    foreach($connection in $script:Refs){Guard;Close $connection}
    $ids=@($script:Records | ForEach-Object {$_.Owner.ConnectionId} | Select-Object -Unique)
    if($ids.Count-ne3){throw 'POOL_PHYSICAL_POPULATION'}
    $abs="DECLARE @J nvarchar(max)=(SELECT LOWER(CONVERT(varchar(36),connection_id)) ConnectionId FROM sys.dm_exec_connections WHERE connection_id IN(CONVERT(uniqueidentifier,@Id1),CONVERT(uniqueidentifier,@Id2),CONVERT(uniqueidentifier,@Id3)) ORDER BY connection_id FOR JSON PATH);SELECT COALESCE(@J,N'[]');"
    $remainingText=Scalar $script:Owner ($OwnGuard+$abs) @{'@DbId'=[int]$P.dbid;'@Id1'=[string]$ids[0];'@Id2'=[string]$ids[1];'@Id3'=[string]$ids[2]}
    $script:Remaining=@(Decode $remainingText)
    if($script:Remaining.Count-ne0){throw 'POOL_PHYSICAL_RESIDUE'}
    # Keep actual pool-associated references through fresh physical absence.
    foreach($connection in $script:Refs){Guard;$connection.Dispose()}
}
$Read=@'
SET NOCOUNT ON;
IF DB_ID()<>@DbId OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_CON010_POOLPUBLIC') THROW 51004,'POOL_DB',1;
DECLARE @I nvarchar(max)=(SELECT DB_ID() DatabaseId,DB_NAME() DatabaseName,SUSER_SNAME() SuserName,ORIGINAL_LOGIN() OriginalLogin,USER_NAME() UserName,CONVERT(varchar(max),SUSER_SID(),2) ServerSid,CONVERT(varchar(max),SUSER_SID(ORIGINAL_LOGIN()),2) OriginalSid,CONVERT(varchar(max),(SELECT sid FROM sys.database_principals WHERE principal_id=USER_ID()),2) UserSid,@@SPID SessionId FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
DECLARE @J nvarchar(max)=(SELECT JSON_QUERY(@I) [Identity],JSON_QUERY(COALESCE((SELECT Id,TenantId,Content,DATALENGTH(Content) ContentBytes,CONVERT(varchar(max),CONVERT(varbinary(max),Content),2) ContentHex,CONVERT(varchar(max),V) VectorJson,CONVERT(int,VECTORPROPERTY(V,'Dimensions')) Dimensions,CONVERT(nvarchar(128),VECTORPROPERTY(V,'BaseType')) BaseType,VECTOR_DISTANCE('cosine',V,CONVERT(VECTOR(3),'[1,0,0]')) Distance FROM lab.Documents ORDER BY Id FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) [Rows],CONVERT(int,SESSION_CONTEXT(N'CON010_TenantId')) [Context] FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
IF DATALENGTH(@J)>120000 THROW 51003,'POOL_RESULT_BOUND',1;SELECT @J;
'@
$OwnGuard=@'
SET NOCOUNT ON;
IF DB_ID()<>@DbId OR DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_CON010_POOLPUBLIC') OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_CON010_POOLPUBLIC') THROW 51004,'POOL_DB',1;
DECLARE @E TABLE(Name nvarchar(128),Val nvarchar(max));INSERT @E VALUES(N'SQLPERF.Project',N'SQL_PerformanceSchulung'),(N'SQLPERF.ContractVersion',N'1.0'),(N'SQLPERF.DemoId',N'CON-010'),(N'SQLPERF.RunToken',N'POOLPUBLIC');
IF (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0)<>4 OR EXISTS(SELECT 1 FROM @E e WHERE (SELECT COUNT(*) FROM sys.extended_properties p WHERE p.class=0 AND p.major_id=0 AND p.minor_id=0 AND DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name) AND DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Val) AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=CONVERT(varbinary(max),e.Val) AND CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(p.value,'BaseType'))=N'nvarchar')<>1) THROW 51004,'POOL_MARKERS',1;
'@
$OwnerRead=@'
DECLARE @J nvarchar(max)=(SELECT c.session_id SessionId,LOWER(CONVERT(varchar(36),c.connection_id)) ConnectionId,CONVERT(nvarchar(33),c.connect_time,126) ConnectTime,CONVERT(nvarchar(33),s.login_time,126) LoginTime,s.login_name LoginName,s.original_login_name OriginalLoginName,CONVERT(varchar(max),s.security_id,2) Sid,s.database_id DatabaseId,s.program_name ProgramName,c.net_transport NetTransport,c.auth_scheme AuthScheme FROM sys.dm_exec_connections c JOIN sys.dm_exec_sessions s ON s.session_id=c.session_id WHERE c.session_id=@Spid AND s.database_id=@DbId AND CONVERT(varbinary(max),s.program_name)=CONVERT(varbinary(max),@App) FOR JSON PATH,INCLUDE_NULL_VALUES);
IF (SELECT COUNT(*) FROM OPENJSON(@J))<>1 THROW 51003,'POOL_OWNER_BINDING',1;SELECT @J;
'@
try{
    Guard
    $script:Phase='ASSEMBLY'
    $Assembly=[Reflection.Assembly]::LoadFrom($Dll)
    if(-not $Assembly.Location.Equals($Dll,[StringComparison]::OrdinalIgnoreCase)){throw 'POOL_ASSEMBLY_PATH'}
    $ConnectionType=$Assembly.GetType('System.Data.SqlClient.SqlConnection',$true);$CredentialType=$Assembly.GetType('System.Data.SqlClient.SqlCredential',$true);$BuilderType=$Assembly.GetType('System.Data.SqlClient.SqlConnectionStringBuilder',$true)
    $clear=$ConnectionType.GetMethod('ClearPool',[type[]]@($ConnectionType))
    $script:Phase='OWNER_CREDENTIAL'
    $ownerCredential=[Activator]::CreateInstance($CredentialType,@('sa',(Secret $env:SQLCMDPASSWORD)))
    $script:Phase='OWNER_CONNECTION'
    $ownerInfo=Connection 'OWNER' $ownerCredential $false;$script:Owner=$ownerInfo.Connection;$script:Phase='OWNER_OPEN';Open $script:Owner
    $credentials=@{};$keys=@{}
    foreach($lane in @('A','B','U')){
        $script:Phase='LANE_CREDENTIAL'
        $env:SQLCMDPASSWORD=[Environment]::GetEnvironmentVariable('TenantSecret'+$lane)
        $credentials[$lane]=[Activator]::CreateInstance($CredentialType,@($P.logins[$lane][0],(Secret $env:SQLCMDPASSWORD)))
    }
    $env:SQLCMDPASSWORD=$null
    $ordinal=0
    foreach($lane in @('A','B','U','A','B','U')){
        $script:Phase='CHECKOUT_CONNECTION'
        $ordinal++;$script:Checkout=$ordinal;$info=Connection $lane $credentials[$lane] $true;$connection=$info.Connection;$script:Refs.Add($connection)
        if(-not [object]::ReferenceEquals($connection.Credential,$credentials[$lane])){throw 'POOL_CREDENTIAL_INSTANCE'}
        $script:Phase='CHECKOUT_MARKERS'
        $null=Scalar $script:Owner ($OwnGuard+'SELECT 1;') @{'@DbId'=[int]$P.dbid}
        $script:Phase='CHECKOUT_OPEN'
        Open $connection
        $script:Phase='CHECKOUT_BEFORE'
        $beforeText=Scalar $connection $Read @{'@DbId'=[int]$P.dbid};$before=Decode $beforeText
        $spoof=if($lane-ceq 'A'){2}else{1}
        $script:Phase='CHECKOUT_MARKERS'
        $null=Scalar $script:Owner ($OwnGuard+'SELECT 1;') @{'@DbId'=[int]$P.dbid}
        $script:Phase='CHECKOUT_SPOOF'
        $null=Scalar $connection "EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=@Tenant;SELECT 1;" @{'@Tenant'=[int]$spoof}
        $script:Phase='CHECKOUT_AFTER'
        $afterText=Scalar $connection $Read @{'@DbId'=[int]$P.dbid};$after=Decode $afterText
        $expectedRows=if($lane-ceq 'U'){0}else{1}
        if($null-ne $before.Context -or $after.Context-ne $spoof -or $before.Rows.Count-ne $expectedRows -or $after.Rows.Count-ne $expectedRows){throw 'POOL_RESULT_CONTRACT'}
        foreach($value in @($before,$after)){
            foreach($key in @('ServerSid','OriginalSid','UserSid')){if($value.Identity[$key]-cne $P.sids[$lane]){throw 'POOL_RESULT_CONTRACT'}}
            if($value.Identity.SuserName-cne $P.logins[$lane][0] -or $value.Identity.OriginalLogin-cne $P.logins[$lane][0] -or $value.Identity.UserName-cne $P.logins[$lane][1] -or $value.Identity.DatabaseId-ne $P.dbid){throw 'POOL_RESULT_CONTRACT'}
            if($expectedRows-eq1){$id=if($lane-ceq 'A'){1}else{2};$r=$value.Rows[0];if($r.Id-ne $id -or $r.TenantId-ne $id -or $null-eq $r.Distance -or $r.Distance-ne0 -or $r.Dimensions-ne3 -or $r.BaseType-cne 'float32' -or $r.Content-cne ('Synthetische Quelle '+$lane)){throw 'POOL_RESULT_CONTRACT'}}
        }
        $script:Phase='CHECKOUT_OWNER'
        $ownerText=Scalar $script:Owner ($OwnGuard+$OwnerRead) @{'@DbId'=[int]$P.dbid;'@Spid'=[int]$before.Identity.SessionId;'@App'=('SQLPERF_POOLPUBLIC_'+$P.token+'_'+$lane)}
        $ownerRows=@(Decode $ownerText);if($ownerRows.Count-ne1){throw 'POOL_OWNER_POPULATION'}
        $script:Records.Add(@{Ordinal=$ordinal;Lane=$lane;ClientConnectionId=$connection.ClientConnectionId.ToString('D').ToLowerInvariant();ConnectionState=$connection.State.ToString();PoolKeySha=$info.Key;CredentialOrdinal=(@{A=1;B=2;U=3}[$lane]);Before=$before;After=$after;Owner=$ownerRows[0]})
        $script:Phase='CHECKOUT_CLOSE'
        Guard;Close $connection
        # Keep the actual pool-associated reference until ClearPool, not Dispose here.
    }
    $script:Checkout=0;$script:Phase='POOL_CLEAR'
    Clear-OwnPools
    $script:Phase='OWNER_CLOSE'
    Guard;Close $script:Owner;$script:Owner.Dispose();$script:Owner=$null
    $script:Phase='SECURE_DISPOSE'
    foreach($secure in $script:Secrets){$secure.Dispose()}
    $script:Cleanup='ACTUAL_CLEAR_CLOSE_AND_NEW_ABSENCE';$script:Status='PASS';$script:Phase='COMPLETE'
}catch{
    # No raw exception/connection string/secret output, and no following SQL.
    $script:Fault=Failure $_.Exception
    $script:Status='FAIL'
}finally{
    if($script:Status-cne 'PASS'){
        # Unknown SQL effects are closed by process/own-namespace teardown only.
        # No ClearPool/Close callback after an unconfirmed request, no SQL retry.
        $script:Cleanup='NOT_ESTABLISHED'
    }
}
$receipt=@{Status=$script:Status;RequestEnd=$(if($script:Unknown){'UNKNOWN'}else{'RESPONSE_RECEIVED'});PoolCleanup=$script:Cleanup;Records=$script:Records.ToArray();Operations=$script:Operations.ToArray();RemainingConnections=@($script:Remaining);Token=$P.token;Fault=$script:Fault}
$wire=$receipt | ConvertTo-Json -Depth 40 -Compress
CredentialSafe $wire
if([Text.Encoding]::UTF8.GetByteCount($wire)-gt1000000){throw 'POOL_RECEIPT_BOUND'}
$wire
if($script:Status-cne 'PASS'){exit 1}
