#Requires -Version 7.2

<#
.SYNOPSIS
    Fuehrt einen projektspezifischen Szenariotest ueber SQL_Server_Lab aus.
.DESCRIPTION
    Validiert das versionierte Lab-Manifest, provisioniert die isolierte
    SQL-Server-Instanz mit SQL_Server_Lab, fuehrt den vorhandenen FWK-010-
    Demoharness wiederholt aus, prueft den Datenbank-Cleanup unabhaengig ueber
    Invoke-SqlServerLabScript und entfernt danach die Lab-Infrastruktur.

    Kennwoerter werden nur als SecureString beziehungsweise temporaer ueber
    SQLCMDPASSWORD weitergegeben. Sie werden weder in Dateien noch in
    Kommandozeilenargumenten persistiert.
.PARAMETER ScenarioId
    Der auszufuehrende Szenario-Vertical-Slice. Derzeit ist QRY-001 verfuegbar.
.PARAMETER Provider
    Containerprovider fuer den Lauf. QRY-001 unterstuetzt docker und podman.
.PARAMETER Repetitions
    Anzahl vollstaendiger Demolaeufe auf derselben Lab-Instanz.
.PARAMETER SaPassword
    Optionales synthetisches SA-Kennwort. Ohne Angabe wird ein zufaelliger,
    nur fuer diesen Prozess gueltiger Wert erzeugt.
.PARAMETER SqlServerLabModulePath
    Pfad zur SqlServerLab.psd1. Ohne Angabe werden die Umgebungsvariable
    SQL_SERVER_LAB_MODULE_PATH, ein benachbartes Repository und installierte
    Module in dieser Reihenfolge geprueft.
.PARAMETER PythonPath
    Pfad zu einem Python-3-Interpreter fuer den vorhandenen FWK-010-Harness.
.PARAMETER StateRoot
    Projektbezogener SQL_Server_Lab-State. Standard ist
    Runtime/State/SqlServerLab und damit ausserhalb versionierter Artefakte.
.PARAMETER KeepEnvironmentOnFailure
    Behaelt das Lab nur nach einem fehlgeschlagenen Test zur Diagnose.
.EXAMPLE
    ./Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1 `
        -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
        -PythonPath python `
        -Repetitions 2
.EXAMPLE
    ./Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1 `
        -Provider podman `
        -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
        -PythonPath python `
        -Repetitions 2
#>
[CmdletBinding()]
param(
    [ValidateSet('QRY-001')]
    [string]$ScenarioId = 'QRY-001',

    [ValidateSet('docker', 'podman')]
    [string]$Provider = 'docker',

    [ValidateRange(1, 5)]
    [int]$Repetitions = 2,

    [SecureString]$SaPassword,

    [string]$SqlServerLabModulePath,

    [string]$PythonPath,

    [string]$StateRoot,

    [switch]$KeepEnvironmentOnFailure
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$scenario = @{
    'QRY-001' = @{
        LabManifests = @{
            docker = Join-Path $repositoryRoot 'Scenarios\QRY-001\sql-server-lab.json'
            podman = Join-Path $repositoryRoot 'Scenarios\QRY-001\sql-server-lab.podman.json'
        }
        DemoManifest = Join-Path $repositoryRoot 'Demos\05_Query_Patterns\QRY-001_SARGability\manifest.json'
        CleanupProbe = Join-Path $repositoryRoot 'Tests\Lab\Sql\Assert-QRY-001-Cleanup.sql'
    }
}[$ScenarioId]
$labManifest = $scenario.LabManifests[$Provider]

if (-not $StateRoot) {
    $StateRoot = Join-Path $repositoryRoot 'Runtime\State\SqlServerLab'
}

function Resolve-SqlServerLabModulePath {
    [CmdletBinding()]
    param([string]$ExplicitPath)

    $candidates = @(
        $ExplicitPath,
        $env:SQL_SERVER_LAB_MODULE_PATH,
        (Join-Path (Split-Path $repositoryRoot -Parent) 'SQL_Server_Lab\SqlServerLab.psd1')
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $installed = Get-Module -ListAvailable -Name SqlServerLab |
        Sort-Object Version -Descending |
        Select-Object -First 1
    if ($installed) {
        return $installed.Path
    }

    throw 'SQL_Server_Lab wurde nicht gefunden. -SqlServerLabModulePath oder SQL_SERVER_LAB_MODULE_PATH ist erforderlich.'
}

function Resolve-PythonPath {
    [CmdletBinding()]
    param([string]$ExplicitPath)

    foreach ($candidate in @($ExplicitPath, $env:SQLPERF_PYTHON)) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            $command = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($command) { return $command.Source }
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                return (Resolve-Path -LiteralPath $candidate).Path
            }
        }
    }

    foreach ($name in @('python', 'python3', 'py')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }

    throw 'Python 3 wurde nicht gefunden. -PythonPath oder SQLPERF_PYTHON ist erforderlich.'
}

$modulePath = Resolve-SqlServerLabModulePath -ExplicitPath $SqlServerLabModulePath
$pythonExecutable = Resolve-PythonPath -ExplicitPath $PythonPath
$sqlcmdCommand = Get-Command sqlcmd -ErrorAction SilentlyContinue
if (-not $sqlcmdCommand) {
    throw 'Das externe Microsoft-Tool sqlcmd wurde nicht gefunden.'
}

foreach ($requiredPath in @($labManifest, $scenario.DemoManifest, $scenario.CleanupProbe)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Erforderliches Szenarioartefakt fehlt: $requiredPath"
    }
}

Import-Module $modulePath -Force

$validation = Test-SqlServerLabManifest -Path $labManifest
if (-not $validation.IsValid) {
    throw "SQL_Server_Lab-Manifest ungueltig: $($validation.Errors -join '; ')"
}

if (-not $SaPassword) {
    $generatedSecret = ([guid]::NewGuid().ToString('N') + 'aA1!')
    Set-Variable -Name SaPassword -Value (
        ConvertTo-SecureString $generatedSecret -AsPlainText -Force
    )
    $generatedSecret = $null
}

$plainSecret = ([PSCredential]::new('sa', $SaPassword)).GetNetworkCredential().Password
$previousSqlCmdSecret = $env:SQLCMDPASSWORD
$previousLabState = $env:SQL_SERVER_LAB_STATE
$lab = $null
$labStatus = $null
$instance = $null
$removal = $null
$completedRepetitions = 0
$testSucceeded = $false

try {
    Set-Item -Path Env:SQLCMDPASSWORD -Value $plainSecret
    $env:SQL_SERVER_LAB_STATE = $StateRoot

    $lab = New-SqlServerLab `
        -Manifest $labManifest `
        -SaPassword $SaPassword `
        -StateRoot $StateRoot `
        -NonInteractive

    if (-not $lab -or $lab.State -ne 'Running') {
        throw "SQL_Server_Lab meldet nach der Provisionierung keinen Running-State: $($lab.State)"
    }

    $labStatus = Get-SqlServerLab -RunId $lab.RunId -Detailed
    $instance = @($labStatus.Instances | Where-Object { $_.Id -eq 'primary' })[0]
    if (-not $instance -or -not $instance.ContainerUp -or $instance.Provider -ne $Provider) {
        throw 'Die primaere SQL_Server_Lab-Instanz ist nicht running.'
    }

    $initialProbe = Invoke-SqlServerLabScript `
        -RunId $lab.RunId `
        -InstanceId 'primary' `
        -StateRoot $StateRoot `
        -ScriptPath $scenario.CleanupProbe `
        -SaPassword $SaPassword
    if (-not $initialProbe.Success) {
        throw "Initiale QRY-001-Cleanup-Pruefung fehlgeschlagen: $($initialProbe.Message)"
    }

    $runDemoPath = Join-Path $repositoryRoot 'Demos\00_Framework\Tools\run_demo.py'
    $server = "$($instance.Host),$($instance.Port)"

    for ($run = 1; $run -le $Repetitions; $run++) {
        Write-Host "QRY-001: FWK-010-Lauf $run von $Repetitions" -ForegroundColor Cyan
        & $pythonExecutable $runDemoPath $scenario.DemoManifest `
            --server $server `
            --auth sql `
            --username sa `
            --sqlcmd $sqlcmdCommand.Source

        if ($LASTEXITCODE -ne 0) {
            throw "FWK-010-Lauf $run ist mit Exitcode $LASTEXITCODE fehlgeschlagen."
        }

        $cleanupProbe = Invoke-SqlServerLabScript `
            -RunId $lab.RunId `
            -InstanceId 'primary' `
            -StateRoot $StateRoot `
            -ScriptPath $scenario.CleanupProbe `
            -SaPassword $SaPassword
        if (-not $cleanupProbe.Success) {
            throw "Unabhaengige Cleanup-Pruefung nach Lauf $run fehlgeschlagen: $($cleanupProbe.Message)"
        }

        $completedRepetitions++
    }

    $testSucceeded = $true
}
finally {
    try {
        if ($lab -and ($testSucceeded -or -not $KeepEnvironmentOnFailure)) {
            $removal = Remove-SqlServerLab `
                -RunId $lab.RunId `
                -StateRoot $StateRoot `
                -Force `
                -Confirm:$false

            if ($removal.Status -ne 'REMOVED') {
                throw "SQL_Server_Lab-Cleanup endete mit Status $($removal.Status)."
            }
        }
    }
    finally {
        if ($null -eq $previousSqlCmdSecret) {
            Remove-Item -Path Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue
        }
        else {
            Set-Item -Path Env:SQLCMDPASSWORD -Value $previousSqlCmdSecret
        }
        $env:SQL_SERVER_LAB_STATE = $previousLabState
        $plainSecret = $null
    }
}

[PSCustomObject]@{
    ScenarioId          = $ScenarioId
    Provider            = $instance.Provider
    SqlVersion          = $instance.Version
    Repetitions         = $completedRepetitions
    DemoOutcome         = 'PASS'
    InfrastructureState = $removal.Status
    LabRunId            = $lab.RunId
    StateRoot           = $StateRoot
}
