[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('\A127\.0\.0\.1,[1-9][0-9]{0,4}\z')]
    [string] $Server,

    [Parameter(Mandatory)]
    [switch] $ConfirmDisposableInstance
)

$ErrorActionPreference = 'Stop'
$requiredBuild = '17.0.5065.9'
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
    } finally {
        $command.Dispose()
    }
} catch {
    throw "OPTSP RPC component failed at stage '$stage'."
} finally {
    $actor.Dispose()
    $observer.Dispose()
}

[pscustomobject]@{
    status = 'PASS'
    build = $requiredBuild
    stored_procedure_event = $procedure.Type
    text_command_event = $text.Type
    stored_procedure_shape = 'parameterized_statement'
    text_command_shape = 'outer_exec_batch'
    result = $procedureResult
} | ConvertTo-Json -Compress
