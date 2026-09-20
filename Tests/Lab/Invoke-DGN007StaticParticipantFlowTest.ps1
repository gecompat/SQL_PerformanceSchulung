#Requires -Version 7.2

<#
.SYNOPSIS
    Prueft den nicht-promotenden DGN-007-Teilnehmerablauf auf einer neuen Labinstanz.
.DESCRIPTION
    Provisioniert eine frische SQL-Server-2025-Linux-Instanz ueber SQL_Server_Lab,
    prueft und installiert den DGN-007-Adapter und fuehrt die sechs dokumentierten
    SQL-Stufen aus. Der Lauf ist ein automatisierter Qualitaetsnachweis fuer den
    statischen Teilnehmerablauf; er erweitert weder den Szenariokatalog noch den
    Demo-Laufkatalog und verleiht keinen READY_FOR_USER-Status.

    Das SA-Kennwort wird ausschliesslich als SecureString verarbeitet. Fuer sqlcmd
    wird es nur waehrend der sechs Teilnehmerstufen in SQLCMDPASSWORD der aktuellen
    Prozessumgebung bereitgestellt und danach wiederhergestellt.
#>
[CmdletBinding()]
param(
    [ValidateSet('docker', 'podman')]
    [string]$Provider = 'docker',

    [SecureString]$SaPassword,

    [string]$SqlServerLabModulePath,

    [string]$SqlcmdPath,

    [string]$StateRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$adapterPath = Join-Path $repositoryRoot 'Scenarios\DGN-007\adapter'
$labManifestLeaf = if ($Provider -eq 'docker') {
    'Scenarios\DGN-007\sql-server-lab.json'
} else {
    'Scenarios\DGN-007\sql-server-lab.podman.json'
}
$labManifest = Join-Path $repositoryRoot $labManifestLeaf
$database = 'SQLPERF_LAB_DGN007_LOCAL'

if (-not $StateRoot) {
    $StateRoot = Join-Path $repositoryRoot "Runtime\State\DGN007StaticParticipantFlow-$Provider"
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

function Invoke-Dgn007ParticipantStage {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$ScriptPath,
        [Parameter(Mandatory)][string]$Server,
        [Parameter(Mandatory)][string]$Database,
        [Parameter(Mandatory)][string]$SqlcmdExecutable,
        [string[]]$AllowedSkipCodes = @()
    )
    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) { throw "DGN-007-Stufe ${Name} fehlt: $ScriptPath" }
    $output = & $SqlcmdExecutable -S $Server -U sa -C -b -d $Database -v 'DemoId=DGN-007' 'RunToken=LOCAL' -i $ScriptPath 2>&1
    $exitCode = $LASTEXITCODE
    $outputText = ($output | ForEach-Object { [string]$_ }) -join "`n"
    if ($exitCode -ne 0) { throw "DGN-007-Stufe $Name endete mit Exitcode ${exitCode}: $outputText" }
    $summaries = [regex]::Matches($outputText, '(?m)^SQLPERF_SUMMARY\|(PASS|SKIP)\|([A-Z0-9_]+)\s*$')
    if ($summaries.Count -ne 1) {
        throw "DGN-007-Stufe ${Name} muss genau eine PASS- oder kontrollierte SKIP-Zusammenfassung liefern: $outputText"
    }
    $outcome = $summaries[0].Groups[1].Value
    $code = $summaries[0].Groups[2].Value
    if ($outcome -eq 'PASS' -and $code -ne 'OK') {
        throw "DGN-007-Stufe ${Name} lieferte einen unzulaessigen PASS-Code ${code}: $outputText"
    }
    if ($outcome -eq 'SKIP' -and $code -notin $AllowedSkipCodes) {
        throw "DGN-007-Stufe ${Name} lieferte einen unzulaessigen SKIP-Code ${code}: $outputText"
    }
    return [PSCustomObject]@{ Name = $Name; Script = $ScriptPath; Outcome = $outcome; Code = $code; Output = $outputText }
}

foreach ($path in @($adapterPath, $labManifest)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Erforderliches DGN-007-Artefakt fehlt: $path" }
}

$modulePath = Resolve-SqlServerLabModulePath -ExplicitPath $SqlServerLabModulePath
$sqlcmdExecutable = Resolve-SqlcmdPath -ExplicitPath $SqlcmdPath
Import-Module $modulePath -Force
$manifestValidation = Test-SqlServerLabManifest -Path $labManifest
if (-not $manifestValidation.IsValid) { throw "DGN-007-Lab-Manifest ist ungueltig: $($manifestValidation.Errors -join '; ')" }

if (-not $SaPassword) {
    $randomBytes = [byte[]]::new(24)
    [Security.Cryptography.RandomNumberGenerator]::Fill($randomBytes)
    $generatedSecret = 'Lab!Aa1_' + [Convert]::ToBase64String($randomBytes)
    Set-Variable -Name SaPassword -Value (ConvertTo-SecureString $generatedSecret -AsPlainText -Force)
    $generatedSecret = $null
}

$previousLabState = $env:SQL_SERVER_LAB_STATE
$previousSqlcmdEnvironment = $env:SQLCMDPASSWORD
$lab = $null; $adapterInstallAttempted = $false; $adapterInstalled = $false; $participantCleanupAttempted = $false
$removed = $null; $operationFailed = $false; $cleanupFailure = $null; $controlledSkip = $null
$stages = [System.Collections.Generic.List[object]]::new()

try {
    $env:SQL_SERVER_LAB_STATE = $StateRoot
    $lab = New-SqlServerLab -Manifest $labManifest -SaPassword $SaPassword -StateRoot $StateRoot -NonInteractive
    if (-not $lab -or $lab.State -ne 'Running') { throw "SQL_Server_Lab meldet nach der Provisionierung keinen Running-State: $($lab.State)" }
    $labStatus = Get-SqlServerLab -RunId $lab.RunId -Detailed
    $instance = @($labStatus.Instances | Where-Object { $_.Id -eq 'primary' })[0]
    if (-not $instance -or -not $instance.ContainerUp -or $instance.Provider -ne $Provider) { throw 'Die primaere DGN-007-Labinstanz ist nicht betriebsbereit.' }

    $adapterPreflight = Test-SqlServerLabAdapter -Path $adapterPath -RunId $lab.RunId -InstanceId primary -StateRoot $StateRoot
    if (-not $adapterPreflight.IsReady) { throw "DGN-007-Adapterpreflight fehlgeschlagen ($($adapterPreflight.Status)): $($adapterPreflight.Errors -join '; ')" }
    $adapterInstallAttempted = $true
    $install = Install-SqlServerLabAdapter -Path $adapterPath -RunId $lab.RunId -InstanceId primary -SaPassword $SaPassword -Entrypoint install -StateRoot $StateRoot
    if (-not $install.Success -or $install.Status -ne 'ADAPTER_APPLIED') { throw "DGN-007-Adapterinstall fehlgeschlagen ($($install.Status)): $($install.Message)" }
    $adapterInstalled = $true
    $validate = Install-SqlServerLabAdapter -Path $adapterPath -RunId $lab.RunId -InstanceId primary -SaPassword $SaPassword -Entrypoint validate -StateRoot $StateRoot
    if (-not $validate.Success -or $validate.Status -ne 'ADAPTER_APPLIED') { throw "DGN-007-Adaptervalidierung fehlgeschlagen ($($validate.Status)): $($validate.Message)" }

    Set-Item -Path Env:SQLCMDPASSWORD -Value (Get-PlainSecret -Secret $SaPassword)
    $server = "$($instance.Host),$($instance.Port)"
    $demoRoot = Join-Path $repositoryRoot 'Demos\07_Query_Store_Extended_Events\DGN-007_Time_Bounded_Search_Incident'
    foreach ($stage in @(
        @{ Name = 'PRECHECK'; Script = '00_Preflight.sql'; AllowedSkipCodes = @('SKIP_QUERY_STORE_REQUIRED') },
        @{ Name = 'TIME_WINDOWS'; Script = '20_Baseline.sql'; AllowedSkipCodes = @('SKIP_INCIDENT_NOT_REPRODUCED') },
        @{ Name = 'EVIDENCE'; Script = '40_Observation.sql'; AllowedSkipCodes = @('SKIP_INCIDENT_NOT_REPRODUCED','SKIP_EVIDENCE_MISSING') },
        @{ Name = 'REFERENCE_CHANGE'; Script = '50_Mitigation.sql'; AllowedSkipCodes = @() },
        @{ Name = 'COMPARISON'; Script = '60_Comparison.sql'; AllowedSkipCodes = @('SKIP_EVIDENCE_MISSING') },
        @{ Name = 'RECOVERY'; Script = '90_Cleanup.sql'; AllowedSkipCodes = @() }
    )) {
        $result = Invoke-Dgn007ParticipantStage -Name $stage.Name -ScriptPath (Join-Path $demoRoot $stage.Script) -Server $server -Database $database -SqlcmdExecutable $sqlcmdExecutable -AllowedSkipCodes $stage.AllowedSkipCodes
        $stages.Add($result)
        if ($stage.Name -eq 'RECOVERY') { $participantCleanupAttempted = $true }
        if ($result.Outcome -eq 'SKIP') {
            $controlledSkip = $result
            break
        }
    }
}
catch { $operationFailed = $true; throw }
finally {
    $cleanupErrors = [System.Collections.Generic.List[string]]::new()
    if ($lab -and $adapterInstallAttempted -and -not $participantCleanupAttempted) {
        try {
            $cleanupScript = Join-Path $repositoryRoot 'Demos\07_Query_Store_Extended_Events\DGN-007_Time_Bounded_Search_Incident\90_Cleanup.sql'
            $detail = Get-SqlServerLab -RunId $lab.RunId -Detailed
            $primary = @($detail.Instances | Where-Object { $_.Id -eq 'primary' })[0]
            if ($primary -and $primary.ContainerUp) {
                Set-Item -Path Env:SQLCMDPASSWORD -Value (Get-PlainSecret -Secret $SaPassword)
                $recoveryResult = Invoke-Dgn007ParticipantStage -Name 'RECOVERY_FINALLY' -ScriptPath $cleanupScript -Server "$($primary.Host),$($primary.Port)" -Database $database -SqlcmdExecutable $sqlcmdExecutable
                $stages.Add($recoveryResult)
                $participantCleanupAttempted = $true
            }
        }
        catch { $cleanupErrors.Add("Teilnehmer-Cleanup: $($_.Exception.Message)") }
    }
    if ($lab -and $adapterInstallAttempted) {
        try {
            $adapterCleanup = Install-SqlServerLabAdapter -Path $adapterPath -RunId $lab.RunId -InstanceId primary -SaPassword $SaPassword -Entrypoint cleanup -SkipPreflight -StateRoot $StateRoot
            if (-not $adapterCleanup.Success -or $adapterCleanup.Status -ne 'ADAPTER_APPLIED') { throw "DGN-007-Adaptercleanup fehlgeschlagen ($($adapterCleanup.Status)): $($adapterCleanup.Message)" }
        }
        catch { $cleanupErrors.Add("Adapter-Cleanup: $($_.Exception.Message)") }
    }
    if ($lab) {
        try {
            $removed = Remove-SqlServerLab -RunId $lab.RunId -StateRoot $StateRoot -Force -Confirm:$false
            if ($removed.Status -ne 'REMOVED') { throw "DGN-007-Lab-Remove endete mit $($removed.Status)." }
        }
        catch { $cleanupErrors.Add("Lab-Remove: $($_.Exception.Message)") }
    }
    try {
        if ($cleanupErrors.Count -gt 0) {
            $cleanupFailure = [System.InvalidOperationException]::new($cleanupErrors -join '; ')
            Write-Warning "DGN-007-Cleanupfehler: $($cleanupFailure.Message)"
        }
    }
    finally {
        $env:SQL_SERVER_LAB_STATE = $previousLabState
        if ($null -eq $previousSqlcmdEnvironment) {
            Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue
        }
        else {
            Set-Item -Path Env:SQLCMDPASSWORD -Value $previousSqlcmdEnvironment
        }
    }
    if ($cleanupFailure -and -not $operationFailed) { throw $cleanupFailure }
}

[PSCustomObject]@{
    ScenarioId = 'DGN-007'; FlowStatus = 'STATIC_PARTICIPANT_FLOW_ONLY'; Provider = $Provider; SqlVersion = '2025'
    AdapterPreflightStatus = $adapterPreflight.Status; InstallStatus = $install.Status; ValidateStatus = $validate.Status
    ParticipantStageResults = @($stages | Select-Object Name, Outcome, Code)
    ParticipantFlowOutcome = if ($controlledSkip) { 'CONTROLLED_SKIP_NO_EVIDENCE_CLAIM' } else { 'COMPLETED_WITHOUT_PROMOTION' }
    ControlledSkipStage = if ($controlledSkip) { $controlledSkip.Name } else { $null }
    ControlledSkipCode = if ($controlledSkip) { $controlledSkip.Code } else { $null }
    AdapterCleanupStatus = $adapterCleanup.Status
    RemoveStatus = $removed.Status; RunId = $lab.RunId
}
