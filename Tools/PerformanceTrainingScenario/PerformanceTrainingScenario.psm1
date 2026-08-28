Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$script:ScenarioDefinitions = @{
    'CON-004' = @{
        ScenarioPath = 'Scenarios\CON-004\scenario.json'
        LabManifests = @{
            docker = 'Scenarios\CON-004\sql-server-lab.json'
            podman = 'Scenarios\CON-004\sql-server-lab.podman.json'
        }
        DemoRoot = 'Demos\07_Concurrency\CON-004_Blocking_Chain'
        DemoId = 'CON-004'
        RunToken = 'LOCAL'
        SafetyLevel = 'YELLOW'
    }
}

function Resolve-ScenarioStateRoot {
    param([string]$StateRoot)
    if ($StateRoot) { return [IO.Path]::GetFullPath($StateRoot) }
    return Join-Path $script:RepositoryRoot 'Runtime\State\PerformanceTrainingScenario'
}

function Resolve-ScenarioDefinition {
    param([Parameter(Mandatory)][string]$ScenarioId)
    $definition = $script:ScenarioDefinitions[$ScenarioId]
    if (-not $definition) { throw "Unbekanntes Schulungsszenario: $ScenarioId" }
    return $definition
}

function Resolve-LabModule {
    param([string]$SqlServerLabModulePath)
    $candidates = @(
        $SqlServerLabModulePath,
        $env:SQL_SERVER_LAB_MODULE_PATH,
        (Join-Path (Split-Path $script:RepositoryRoot -Parent) 'SQL_Server_Lab\SqlServerLab.psd1')
    ) | Where-Object { $_ }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            Import-Module (Resolve-Path -LiteralPath $candidate).Path -Force
            return
        }
    }
    $module = Get-Module -ListAvailable -Name SqlServerLab | Sort-Object Version -Descending | Select-Object -First 1
    if (-not $module) { throw 'SQL_Server_Lab wurde nicht gefunden.' }
    Import-Module $module.Path -Force
}

function Resolve-Sqlcmd {
    param([string]$SqlcmdPath)
    if ($SqlcmdPath -and (Test-Path -LiteralPath $SqlcmdPath -PathType Leaf)) {
        return (Resolve-Path -LiteralPath $SqlcmdPath).Path
    }
    $command = Get-Command sqlcmd -ErrorAction SilentlyContinue
    if (-not $command) { throw 'Das externe Microsoft-Tool sqlcmd wurde nicht gefunden.' }
    return $command.Source
}

function Get-StatePath {
    param([string]$ScenarioId,[string]$StateRoot)
    return Join-Path (Resolve-ScenarioStateRoot $StateRoot) ($ScenarioId + '.json')
}

function Read-ScenarioState {
    param([string]$ScenarioId,[string]$StateRoot)
    $path = Get-StatePath $ScenarioId $StateRoot
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Kein aktiver Zustand fuer $ScenarioId gefunden." }
    return Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
}

function Write-ScenarioState {
    param([string]$ScenarioId,[string]$StateRoot,[hashtable]$State)
    $path = Get-StatePath $ScenarioId $StateRoot
    $directory = Split-Path $path -Parent
    [IO.Directory]::CreateDirectory($directory) | Out-Null
    $State | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $path -Encoding utf8NoBOM
}

function Invoke-ScenarioSql {
    param(
        [Parameter(Mandatory)][string]$SqlcmdPath,
        [Parameter(Mandatory)][string]$Server,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [Parameter(Mandatory)][string]$ScriptPath,
        [Parameter(Mandatory)][string]$Database,
        [Parameter(Mandatory)][string]$DemoId,
        [Parameter(Mandatory)][string]$RunToken
    )
    $previous = $env:SQLCMDPASSWORD
    try {
        $env:SQLCMDPASSWORD = ([PSCredential]::new('sa',$SaPassword)).GetNetworkCredential().Password
        $targetDatabase = "SQLPERF_LAB_$($DemoId.Replace('-', ''))_$RunToken"
        $arguments = @(
            '-S',$Server,'-U','sa','-C','-d',$Database,'-i',$ScriptPath,
            '-b','-r','1','-v',"DemoId=$DemoId","RunToken=$RunToken",
            "TargetDatabase=$targetDatabase",'ConfirmIsolatedLab=1',
            'HighImpactConfirmed=0','MaximumRuntimeSeconds=300'
        )
        $output = & $SqlcmdPath @arguments 2>&1
        if ($LASTEXITCODE -ne 0) { throw "SQL-Phase fehlgeschlagen: $($output -join [Environment]::NewLine)" }
        return $output
    }
    finally {
        if ($null -eq $previous) { Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue }
        else { $env:SQLCMDPASSWORD = $previous }
    }
}

function Get-PerformanceTrainingScenario {
    [CmdletBinding()]
    param(
        [ValidateSet('CON-004')][string]$ScenarioId,
        [string]$StateRoot
    )
    $ids = if ($ScenarioId) { @($ScenarioId) } else { @($script:ScenarioDefinitions.Keys | Sort-Object) }
    foreach ($id in $ids) {
        $definition = Resolve-ScenarioDefinition $id
        $contract = Get-Content -Raw -LiteralPath (Join-Path $script:RepositoryRoot $definition.ScenarioPath) | ConvertFrom-Json
        $statePath = Get-StatePath $id $StateRoot
        $state = if (Test-Path -LiteralPath $statePath) { Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json } else { $null }
        [PSCustomObject]@{
            ScenarioId = $id
            Title = $contract.title
            SafetyLevel = $definition.SafetyLevel
            Providers = @($definition.LabManifests.Keys | Sort-Object)
            ReadyState = $contract.interactive.readyState
            ActiveState = $state
            EntryDocument = Join-Path $script:RepositoryRoot $contract.interactive.entryDocument
        }
    }
}

function Start-PerformanceTrainingScenario {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('CON-004')][string]$ScenarioId,
        [Parameter(Mandatory)][ValidateSet('docker','podman')][string]$Provider,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [string]$SqlServerLabModulePath,
        [string]$SqlcmdPath,
        [string]$StateRoot
    )
    $definition = Resolve-ScenarioDefinition $ScenarioId
    Resolve-LabModule $SqlServerLabModulePath
    $sqlcmd = Resolve-Sqlcmd $SqlcmdPath
    $root = Resolve-ScenarioStateRoot $StateRoot
    $env:SQL_SERVER_LAB_STATE = $root
    $statePath = Get-StatePath $ScenarioId $root
    if (Test-Path -LiteralPath $statePath) { throw "$ScenarioId besitzt bereits einen lokalen Lifecycle-Zustand." }
    $manifest = Join-Path $script:RepositoryRoot $definition.LabManifests[$Provider]
    $validation = Test-SqlServerLabManifest -Path $manifest
    if (-not $validation.IsValid) { throw "SQL_Server_Lab-Manifest ungueltig: $($validation.Errors -join '; ')" }
    $lab = New-SqlServerLab -Manifest $manifest -SaPassword $SaPassword -StateRoot $root -NonInteractive
    try {
        $detail = Get-SqlServerLab -RunId $lab.RunId -Detailed
        $instance = @($detail.Instances | Where-Object Id -eq 'primary')[0]
        if (-not $instance -or -not $instance.ContainerUp) { throw 'Die primaere Lab-Instanz ist nicht betriebsbereit.' }
        $server = "$($instance.Host),$($instance.Port)"
        $demoRoot = Join-Path $script:RepositoryRoot $definition.DemoRoot
        Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '00_Preflight.sql') 'master' $definition.DemoId $definition.RunToken | Out-Null
        Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '10_Setup.sql') 'master' $definition.DemoId $definition.RunToken | Out-Null
        $database = "SQLPERF_LAB_$($definition.DemoId.Replace('-', ''))_$($definition.RunToken)"
        Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '20_Baseline.sql') $database $definition.DemoId $definition.RunToken | Out-Null
        $contract = Get-Content -Raw -LiteralPath (Join-Path $script:RepositoryRoot $definition.ScenarioPath) | ConvertFrom-Json
        Write-ScenarioState $ScenarioId $root @{
            ScenarioId=$ScenarioId; RunId=$lab.RunId; Provider=$Provider; Database=$database;
            Status='READY_FOR_USER'; CreatedUtc=[DateTime]::UtcNow.ToString('o')
        }
        [PSCustomObject]@{
            ScenarioId=$ScenarioId; Status='READY_FOR_USER'; RunId=$lab.RunId; Provider=$Provider;
            Server=$server; Database=$database; SafetyLevel='YELLOW';
            SessionRoles=@($contract.orchestration.manual.sessionScripts | Sort-Object startOrder | Select-Object role,script,startOrder,instruction)
            EntryDocument=Join-Path $script:RepositoryRoot $contract.interactive.entryDocument
            ResetCommand="Reset-PerformanceTrainingScenario -ScenarioId $ScenarioId"
            RemoveCommand="Remove-PerformanceTrainingScenario -ScenarioId $ScenarioId"
        }
    }
    catch {
        Remove-SqlServerLab -RunId $lab.RunId -StateRoot $root -Force -Confirm:$false | Out-Null
        throw
    }
}

function Reset-PerformanceTrainingScenario {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('CON-004')][string]$ScenarioId,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [string]$SqlServerLabModulePath,
        [string]$SqlcmdPath,
        [string]$StateRoot
    )
    $definition=Resolve-ScenarioDefinition $ScenarioId; Resolve-LabModule $SqlServerLabModulePath; $sqlcmd=Resolve-Sqlcmd $SqlcmdPath
    $root=Resolve-ScenarioStateRoot $StateRoot; $env:SQL_SERVER_LAB_STATE=$root; $state=Read-ScenarioState $ScenarioId $root
    $detail=Get-SqlServerLab -RunId $state.RunId -Detailed; $instance=@($detail.Instances | Where-Object Id -eq 'primary')[0]
    if (-not $instance -or -not $instance.ContainerUp) { throw 'Die Szenarioinstanz ist nicht betriebsbereit.' }
    $server="$($instance.Host),$($instance.Port)"; $demoRoot=Join-Path $script:RepositoryRoot $definition.DemoRoot
    Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '90_Cleanup.sql') 'master' $definition.DemoId $definition.RunToken | Out-Null
    Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '10_Setup.sql') 'master' $definition.DemoId $definition.RunToken | Out-Null
    Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '20_Baseline.sql') $state.Database $definition.DemoId $definition.RunToken | Out-Null
    [PSCustomObject]@{ScenarioId=$ScenarioId;Status='READY_FOR_USER';RunId=$state.RunId;Provider=$state.Provider;Database=$state.Database}
}

function Remove-PerformanceTrainingScenario {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][ValidateSet('CON-004')][string]$ScenarioId,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [string]$SqlServerLabModulePath,
        [string]$SqlcmdPath,
        [string]$StateRoot
    )
    $definition=Resolve-ScenarioDefinition $ScenarioId; Resolve-LabModule $SqlServerLabModulePath; $sqlcmd=Resolve-Sqlcmd $SqlcmdPath
    $root=Resolve-ScenarioStateRoot $StateRoot; $env:SQL_SERVER_LAB_STATE=$root; $state=Read-ScenarioState $ScenarioId $root
    if (-not $PSCmdlet.ShouldProcess("$ScenarioId / $($state.RunId)",'fachliche Artefakte und Lab-Infrastruktur entfernen')) { return }
    $detail=Get-SqlServerLab -RunId $state.RunId -Detailed; $instance=@($detail.Instances | Where-Object Id -eq 'primary')[0]
    if ($instance -and $instance.ContainerUp) {
        $server="$($instance.Host),$($instance.Port)"; $demoRoot=Join-Path $script:RepositoryRoot $definition.DemoRoot
        Invoke-ScenarioSql $sqlcmd $server $SaPassword (Join-Path $demoRoot '90_Cleanup.sql') 'master' $definition.DemoId $definition.RunToken | Out-Null
    }
    $removed=Remove-SqlServerLab -RunId $state.RunId -StateRoot $root -Force -Confirm:$false
    if ($removed.Status -ne 'REMOVED') { throw "Infrastrukturabbau endete mit $($removed.Status)." }
    Remove-Item -LiteralPath (Get-StatePath $ScenarioId $root) -Force
    [PSCustomObject]@{ScenarioId=$ScenarioId;Status='REMOVED';RunId=$state.RunId;Provider=$state.Provider}
}

Export-ModuleMember -Function Get-PerformanceTrainingScenario,Start-PerformanceTrainingScenario,Reset-PerformanceTrainingScenario,Remove-PerformanceTrainingScenario
