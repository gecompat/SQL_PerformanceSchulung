#Requires -Version 7.2

<#
.SYNOPSIS
    Prueft den kontrollierten DGN-007-Version-Gate auf einer frischen Linux-Labinstanz.
.DESCRIPTION
    Provisioniert ausschliesslich eine SQL-Server-2019- oder -2022-Instanz ueber
    SQL_Server_Lab und prueft den DGN-007-Adapter read-only gegen diese Instanz.
    Der Adapter darf wegen seines 2025-only-Vertrags nicht bereit sein. Es wird
    kein Adapter-Entrypoint ausgefuehrt; eine explizite Abfrage bestaetigt, dass
    die DGN-007-Testdatenbank nicht angelegt wurde. Das Lab wird immer im
    finally-Pfad entfernt. Dieser Nachweis erweitert weder Szenarioinventar noch
    Lifecycle- oder Runtime-Matrix.
#>
[CmdletBinding()]
param(
    [ValidateSet('docker', 'podman')]
    [string]$Provider = 'docker',

    [ValidateSet('2019', '2022')]
    [string]$SqlVersion,

    [SecureString]$SaPassword,

    [string]$SqlServerLabModulePath,

    [string]$SqlcmdPath,

    [string]$StateRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$adapterPath = Join-Path $repositoryRoot 'Scenarios\DGN-007\adapter'
$database = 'SQLPERF_LAB_DGN007_LOCAL'

if (-not $StateRoot) {
    $StateRoot = Join-Path $repositoryRoot "Runtime\State\DGN007UnsupportedVersionGate-$Provider-$SqlVersion"
}

function Resolve-SqlServerLabModulePath {
    param([string]$ExplicitPath)
    $candidates = @($ExplicitPath, $env:SQL_SERVER_LAB_MODULE_PATH,
        (Join-Path (Split-Path $repositoryRoot -Parent) 'SQL_Server_Lab\SqlServerLab.psd1')) |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    $installed = Get-Module -ListAvailable -Name SqlServerLab | Sort-Object Version -Descending | Select-Object -First 1
    if ($installed) { return $installed.Path }
    throw 'SQL_Server_Lab wurde nicht gefunden. -SqlServerLabModulePath oder SQL_SERVER_LAB_MODULE_PATH ist erforderlich.'
}

function Resolve-SqlcmdPath {
    param([string]$ExplicitPath)
    $candidate = if ($ExplicitPath) { $ExplicitPath } else { 'sqlcmd' }
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    if ($ExplicitPath -and (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) { return (Resolve-Path -LiteralPath $ExplicitPath).Path }
    throw 'sqlcmd wurde nicht gefunden. -SqlcmdPath oder ein sqlcmd-PATH-Eintrag ist erforderlich.'
}

function Get-PlainSecret {
    param([Parameter(Mandatory)][SecureString]$Secret)
    return ([PSCredential]::new('sa', $Secret)).GetNetworkCredential().Password
}

if (-not (Test-Path -LiteralPath $adapterPath -PathType Container)) {
    throw "Erforderlicher DGN-007-Adapter fehlt: $adapterPath"
}

$modulePath = Resolve-SqlServerLabModulePath -ExplicitPath $SqlServerLabModulePath
$sqlcmdExecutable = Resolve-SqlcmdPath -ExplicitPath $SqlcmdPath
Import-Module $modulePath -Force

if (-not $SaPassword) {
    $randomBytes = [byte[]]::new(24)
    [Security.Cryptography.RandomNumberGenerator]::Fill($randomBytes)
    $generatedSecret = 'Lab!Aa1_' + [Convert]::ToBase64String($randomBytes)
    Set-Variable -Name SaPassword -Value (ConvertTo-SecureString $generatedSecret -AsPlainText -Force)
    $generatedSecret = $null
}

$previousLabState = $env:SQL_SERVER_LAB_STATE
$previousSqlcmdEnvironment = $env:SQLCMDPASSWORD
$lab = $null; $removed = $null; $operationFailed = $false; $cleanupFailure = $null
$adapterPreflight = $null; $databaseCheck = $null

try {
    $env:SQL_SERVER_LAB_STATE = $StateRoot
    $lab = New-SqlServerLab -Version $SqlVersion -Provider $Provider -Profile standard `
        -LabName "dgn007-version-gate-$Provider-$SqlVersion" -SaPassword $SaPassword -StateRoot $StateRoot -NonInteractive
    if (-not $lab -or $lab.State -ne 'Running') { throw "SQL_Server_Lab meldet nach der Provisionierung keinen Running-State: $($lab.State)" }

    $labStatus = Get-SqlServerLab -RunId $lab.RunId -Detailed
    $instance = @($labStatus.Instances | Where-Object { $_.Id -eq 'primary' })[0]
    if (-not $instance -or -not $instance.ContainerUp -or $instance.Provider -ne $Provider -or $instance.Version -notlike "$SqlVersion*") {
        throw 'Die primaere DGN-007-Version-Gate-Labinstanz ist nicht betriebsbereit oder besitzt eine unerwartete Version.'
    }

    $adapterPreflight = Test-SqlServerLabAdapter -Path $adapterPath -RunId $lab.RunId -InstanceId primary -StateRoot $StateRoot
    if ($adapterPreflight.IsReady) { throw "DGN-007-Adapterpreflight darf auf SQL Server $SqlVersion nicht bereit sein." }
    $versionError = @($adapterPreflight.Errors | Where-Object { $_ -match "Instanzversion\s+$SqlVersion.*nicht unterstuetzt" })
    if ($versionError.Count -ne 1) {
        throw "DGN-007-Adapterpreflight lieferte keinen eindeutigen Versionsfehler fuer SQL Server ${SqlVersion}: $($adapterPreflight.Errors -join '; ')"
    }
    if ($adapterPreflight.Status -notin @('ADAPTER_UNSUPPORTED_SQL_VERSION', 'ADAPTER_UNSUPPORTED_CONTRACT')) {
        throw "DGN-007-Adapterpreflight endete mit unerwartetem Status $($adapterPreflight.Status)."
    }

    Set-Item -Path Env:SQLCMDPASSWORD -Value (Get-PlainSecret -Secret $SaPassword)
    $databaseCheck = & $sqlcmdExecutable -S "$($instance.Host),$($instance.Port)" -U sa -C -b -d master `
        -Q "SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'$database') IS NULL THEN 'DGN007_DATABASE_ABSENT' ELSE 'DGN007_DATABASE_PRESENT' END;" 2>&1
    $databaseCheckExitCode = $LASTEXITCODE
    $databaseCheckText = ($databaseCheck | ForEach-Object { [string]$_ }) -join "`n"
    if ($databaseCheckExitCode -ne 0 -or $databaseCheckText -notmatch '(?m)^DGN007_DATABASE_ABSENT\s*$') {
        throw "DGN-007-Version-Gate hat einen unerwarteten Datenbankzustand: $databaseCheckText"
    }
}
catch { $operationFailed = $true; throw }
finally {
    $cleanupErrors = [System.Collections.Generic.List[string]]::new()
    if ($lab) {
        try {
            $removed = Remove-SqlServerLab -RunId $lab.RunId -StateRoot $StateRoot -Force -Confirm:$false
            if ($removed.Status -ne 'REMOVED') { throw "DGN-007-Version-Gate-Lab-Remove endete mit $($removed.Status)." }
        }
        catch { $cleanupErrors.Add("Lab-Remove: $($_.Exception.Message)") }
    }
    try {
        if ($cleanupErrors.Count -gt 0) {
            $cleanupFailure = [System.InvalidOperationException]::new($cleanupErrors -join '; ')
            Write-Warning "DGN-007-Version-Gate-Cleanupfehler: $($cleanupFailure.Message)"
        }
    }
    finally {
        $env:SQL_SERVER_LAB_STATE = $previousLabState
        if ($null -eq $previousSqlcmdEnvironment) { Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue }
        else { Set-Item -Path Env:SQLCMDPASSWORD -Value $previousSqlcmdEnvironment }
    }
    if ($cleanupFailure -and -not $operationFailed) { throw $cleanupFailure }
}

[PSCustomObject]@{
    ScenarioId = 'DGN-007'; GateStatus = 'ADAPTER_UNSUPPORTED_SQL_VERSION'; Provider = $Provider; SqlVersion = $SqlVersion
    AdapterPreflightStatus = $adapterPreflight.Status; DatabaseStatus = 'DGN007_DATABASE_ABSENT'
    RemoveStatus = $removed.Status; RunId = $lab.RunId
}
