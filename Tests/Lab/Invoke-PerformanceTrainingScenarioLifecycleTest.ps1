#Requires -Version 7.2

<#
.SYNOPSIS
    Prueft einen vollstaendigen Project-Adapter-Lifecycle auf SQL Server 2025 Linux.
.DESCRIPTION
    Provisioniert ueber SQL_Server_Lab, erwartet READY_FOR_USER, fuehrt einen
    fachlichen Reset aus und entfernt danach Adapterartefakte, Infrastruktur
    und den aktiven lokalen Szenario-State. Der Test verwendet ausschliesslich die vier
    oeffentlichen Commands des Schulungsszenario-Moduls.
#>
[CmdletBinding()]
param(
    [ValidateSet('CON-004','CON-006','DGN-005')][string]$ScenarioId = 'CON-004',
    [ValidateSet('docker','podman')][string]$Provider = 'docker',
    [SecureString]$SaPassword,
    [string]$SqlServerLabModulePath,
    [string]$StateRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $StateRoot) {
    $StateRoot = Join-Path $repositoryRoot "Runtime\State\PerformanceTrainingScenario-$($ScenarioId.Replace('-',''))-$Provider"
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

$statePath = Join-Path $StateRoot "$ScenarioId.json"
$ready = $null
$reset = $null
$removed = $null
$previousLabState = $env:SQL_SERVER_LAB_STATE
$priorSqlcmdEnv = $env:SQLCMDPASSWORD

try {
    $ready = Start-PerformanceTrainingScenario `
        -ScenarioId $ScenarioId `
        -Provider $Provider `
        -SaPassword $SaPassword `
        -SqlServerLabModulePath $SqlServerLabModulePath `
        -StateRoot $StateRoot
    if ($ready.Status -ne 'READY_FOR_USER' -or $ready.AdapterContractVersion -ne '0.1') {
        throw "Start lieferte keinen versionierten READY_FOR_USER-Zustand: $($ready | ConvertTo-Json -Compress)"
    }
    if ($ready.SqlcmdVariables.DemoId -ne $ScenarioId -or $ready.SqlcmdVariables.RunToken -ne 'LOCAL') {
        throw 'Die READY_FOR_USER-Uebergabe enthaelt nicht die erwarteten SQLCMD-Variablen.'
    }
    if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
        throw "Der lokale $ScenarioId-Lifecycle-State fehlt nach Start."
    }

    if ($ScenarioId -eq 'DGN-005') {
        $env:SQLCMDPASSWORD = [System.Net.NetworkCredential]::new('', $SaPassword).Password
        foreach ($role in @($ready.SessionRoles | Sort-Object startOrder)) {
            $scriptPath = Join-Path $repositoryRoot $role.script
            & sqlcmd -S $ready.Server -U sa -C -b -d $ready.Database `
                -v 'DemoId=DGN-005' 'RunToken=LOCAL' -i $scriptPath
            if ($LASTEXITCODE -ne 0) {
                throw "Interaktive DGN-005-Phase $($role.role) endete mit Exitcode $LASTEXITCODE."
            }
        }
    }
    elseif ($ScenarioId -eq 'CON-006') {
        $env:SQLCMDPASSWORD = [System.Net.NetworkCredential]::new('', $SaPassword).Password
        $python = (Get-Command python -ErrorAction Stop).Source
        $orchestrator = Join-Path $repositoryRoot 'Demos\00_Framework\Tools\orchestrate_sessions.py'
        $demoRoot = Join-Path $repositoryRoot 'Demos\07_Concurrency\CON-006_Deadlock_Cycle'

        foreach ($manifestName in @('deadlock.json', 'ordered.json')) {
            if ($manifestName -eq 'ordered.json') {
                foreach ($scriptName in @('40_Observation.sql', '50_Mitigation.sql')) {
                    & sqlcmd -S $ready.Server -U sa -C -b -d $ready.Database `
                        -v 'DemoId=CON-006' 'RunToken=LOCAL' -i (Join-Path $demoRoot $scriptName)
                    if ($LASTEXITCODE -ne 0) {
                        throw "Interaktive CON-006-Phase $scriptName endete mit Exitcode $LASTEXITCODE."
                    }
                }
            }
            $manifestPath = Join-Path $demoRoot "Sessions\$manifestName"
            & $python $orchestrator $manifestPath `
                --server $ready.Server --database $ready.Database `
                --auth sql --username sa --show-output
            if ($LASTEXITCODE -ne 0) {
                throw "Interaktive CON-006-Orchestrierung $manifestName endete mit Exitcode $LASTEXITCODE."
            }
        }

        & sqlcmd -S $ready.Server -U sa -C -b -d $ready.Database `
            -v 'DemoId=CON-006' 'RunToken=LOCAL' -i (Join-Path $demoRoot '70_Verification.sql')
        if ($LASTEXITCODE -ne 0) {
            throw "Interaktive CON-006-Verifikation endete mit Exitcode $LASTEXITCODE."
        }
    }

    $reset = Reset-PerformanceTrainingScenario `
        -ScenarioId $ScenarioId `
        -SaPassword $SaPassword `
        -SqlServerLabModulePath $SqlServerLabModulePath `
        -StateRoot $StateRoot
    if ($reset.Status -ne 'READY_FOR_USER' -or $reset.RunId -ne $ready.RunId) {
        throw 'Reset hat den reproduzierbaren READY_FOR_USER-Zustand nicht auf derselben Instanz hergestellt.'
    }

    $removed = Remove-PerformanceTrainingScenario `
        -ScenarioId $ScenarioId `
        -SaPassword $SaPassword `
        -SqlServerLabModulePath $SqlServerLabModulePath `
        -StateRoot $StateRoot `
        -Confirm:$false
    if ($removed.Status -ne 'REMOVED') {
        throw "Remove endete mit Status $($removed.Status)."
    }
    if (Test-Path -LiteralPath $statePath) {
        throw "Der lokale $ScenarioId-Lifecycle-State ist nach Remove noch vorhanden."
    }
}
finally {
    try {
        if ($ready -and -not $removed -and (Test-Path -LiteralPath $statePath -PathType Leaf)) {
            try {
                Remove-PerformanceTrainingScenario `
                    -ScenarioId $ScenarioId `
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
        if ($null -eq $priorSqlcmdEnv) {
            Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue
        }
        else {
            Set-Item Env:SQLCMDPASSWORD -Value $priorSqlcmdEnv
        }
    }
}

[PSCustomObject]@{
    ScenarioId = $ScenarioId
    Provider = $Provider
    SqlVersion = '2025'
    AdapterContractVersion = $ready.AdapterContractVersion
    StartStatus = $ready.Status
    ResetStatus = $reset.Status
    RemoveStatus = $removed.Status
    RunId = $ready.RunId
}
