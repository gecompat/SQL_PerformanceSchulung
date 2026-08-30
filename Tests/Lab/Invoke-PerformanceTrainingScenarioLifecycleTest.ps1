#Requires -Version 7.2

<#
.SYNOPSIS
    Prueft den vollstaendigen CON-004-Adapter-Lifecycle auf SQL Server 2025 Linux.
.DESCRIPTION
    Provisioniert ueber SQL_Server_Lab, erwartet READY_FOR_USER, fuehrt einen
    fachlichen Reset aus und entfernt danach Adapterartefakte, Infrastruktur
    und den aktiven lokalen Szenario-State. Der Test verwendet ausschliesslich die vier
    oeffentlichen Commands des Schulungsszenario-Moduls.
#>
[CmdletBinding()]
param(
    [ValidateSet('docker','podman')][string]$Provider = 'docker',
    [SecureString]$SaPassword,
    [string]$SqlServerLabModulePath,
    [string]$StateRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $StateRoot) {
    $StateRoot = Join-Path $repositoryRoot "Runtime\State\PerformanceTrainingScenario-$Provider"
}
if (-not $SqlServerLabModulePath) {
    $SqlServerLabModulePath = Join-Path (Split-Path $repositoryRoot -Parent) 'SQL_Server_Lab\SqlServerLab.psd1'
}
if (-not $SaPassword) {
    $randomBytes = [byte[]]::new(24)
    [Security.Cryptography.RandomNumberGenerator]::Fill($randomBytes)
    $generatedSecret = "Lab!Aa1_" + [Convert]::ToBase64String($randomBytes)
    Set-Variable -Name SaPassword -Value (
        ConvertTo-SecureString $generatedSecret -AsPlainText -Force
    )
    $generatedSecret = $null
}

Import-Module (Join-Path $repositoryRoot 'Tools\PerformanceTrainingScenario\PerformanceTrainingScenario.psd1') -Force

$statePath = Join-Path $StateRoot 'CON-004.json'
$ready = $null
$reset = $null
$removed = $null
$previousLabState = $env:SQL_SERVER_LAB_STATE

try {
    $ready = Start-PerformanceTrainingScenario `
        -ScenarioId CON-004 `
        -Provider $Provider `
        -SaPassword $SaPassword `
        -SqlServerLabModulePath $SqlServerLabModulePath `
        -StateRoot $StateRoot
    if ($ready.Status -ne 'READY_FOR_USER' -or $ready.AdapterContractVersion -ne '0.1') {
        throw "Start lieferte keinen versionierten READY_FOR_USER-Zustand: $($ready | ConvertTo-Json -Compress)"
    }
    if ($ready.SqlcmdVariables.DemoId -ne 'CON-004' -or $ready.SqlcmdVariables.RunToken -ne 'LOCAL') {
        throw 'Die READY_FOR_USER-Uebergabe enthaelt nicht die erwarteten SQLCMD-Variablen.'
    }
    if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
        throw 'Der lokale CON-004-Lifecycle-State fehlt nach Start.'
    }

    $reset = Reset-PerformanceTrainingScenario `
        -ScenarioId CON-004 `
        -SaPassword $SaPassword `
        -SqlServerLabModulePath $SqlServerLabModulePath `
        -StateRoot $StateRoot
    if ($reset.Status -ne 'READY_FOR_USER' -or $reset.RunId -ne $ready.RunId) {
        throw 'Reset hat den reproduzierbaren READY_FOR_USER-Zustand nicht auf derselben Instanz hergestellt.'
    }

    $removed = Remove-PerformanceTrainingScenario `
        -ScenarioId CON-004 `
        -SaPassword $SaPassword `
        -SqlServerLabModulePath $SqlServerLabModulePath `
        -StateRoot $StateRoot `
        -Confirm:$false
    if ($removed.Status -ne 'REMOVED') {
        throw "Remove endete mit Status $($removed.Status)."
    }
    if (Test-Path -LiteralPath $statePath) {
        throw 'Der lokale CON-004-Lifecycle-State ist nach Remove noch vorhanden.'
    }
}
finally {
    try {
        if ($ready -and -not $removed -and (Test-Path -LiteralPath $statePath -PathType Leaf)) {
            try {
                Remove-PerformanceTrainingScenario `
                    -ScenarioId CON-004 `
                    -SaPassword $SaPassword `
                    -SqlServerLabModulePath $SqlServerLabModulePath `
                    -StateRoot $StateRoot `
                    -Confirm:$false | Out-Null
            }
            catch {
                Import-Module $SqlServerLabModulePath -Force
                Remove-SqlServerLab -RunId $ready.RunId -StateRoot $StateRoot -Force -Confirm:$false | Out-Null
                Remove-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
            }
        }
    }
    finally {
        $env:SQL_SERVER_LAB_STATE = $previousLabState
    }
}

[PSCustomObject]@{
    ScenarioId = 'CON-004'
    Provider = $Provider
    SqlVersion = '2025'
    AdapterContractVersion = $ready.AdapterContractVersion
    StartStatus = $ready.Status
    ResetStatus = $reset.Status
    RemoveStatus = $removed.Status
    RunId = $ready.RunId
}
