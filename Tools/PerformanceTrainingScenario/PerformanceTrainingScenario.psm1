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
        AdapterPath = 'Scenarios\CON-004\adapter'
        DemoId = 'CON-004'
        RunToken = 'LOCAL'
        Database = 'SQLPERF_LAB_CON004_LOCAL'
        SafetyLevel = 'YELLOW'
    }
    'DGN-005' = @{
        ScenarioPath = 'Scenarios\DGN-005\scenario.json'
        LabManifests = @{
            docker = 'Scenarios\DGN-005\sql-server-lab.json'
            podman = 'Scenarios\DGN-005\sql-server-lab.podman.json'
        }
        DemoRoot = 'Demos\07_Query_Store_Extended_Events\DGN-005_Bounded_Extended_Events'
        AdapterPath = 'Scenarios\DGN-005\adapter'
        DemoId = 'DGN-005'
        RunToken = 'LOCAL'
        Database = 'SQLPERF_LAB_DGN005_LOCAL'
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

function Invoke-WithScenarioSqlcmdPath {
    param(
        [string]$SqlcmdPath,
        [Parameter(Mandatory)][scriptblock]$Action
    )
    if (-not $SqlcmdPath) { return & $Action }
    if (-not (Test-Path -LiteralPath $SqlcmdPath -PathType Leaf)) {
        throw "Das angegebene sqlcmd wurde nicht gefunden: $SqlcmdPath"
    }
    $resolved = (Resolve-Path -LiteralPath $SqlcmdPath).Path
    if ([IO.Path]::GetFileNameWithoutExtension($resolved) -ne 'sqlcmd') {
        throw "-SqlcmdPath muss auf sqlcmd zeigen: $resolved"
    }
    $previousPath = $env:PATH
    try {
        $env:PATH = (Split-Path $resolved -Parent) + [IO.Path]::PathSeparator + $previousPath
        return & $Action
    }
    finally {
        $env:PATH = $previousPath
    }
}

function Invoke-ScenarioAdapter {
    param(
        [Parameter(Mandatory)][string]$AdapterPath,
        [Parameter(Mandatory)][string]$RunId,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [Parameter(Mandatory)][ValidateSet('install','validate','cleanup')][string]$Entrypoint,
        [Parameter(Mandatory)][string]$StateRoot,
        [string]$SqlcmdPath
    )
    $result = Invoke-WithScenarioSqlcmdPath -SqlcmdPath $SqlcmdPath -Action {
        Install-SqlServerLabAdapter `
            -Path $AdapterPath `
            -RunId $RunId `
            -InstanceId 'primary' `
            -SaPassword $SaPassword `
            -Entrypoint $Entrypoint `
            -StateRoot $StateRoot
    }
    if (-not $result.Success -or $result.Status -ne 'ADAPTER_APPLIED') {
        throw "Szenario-Adapterentrypoint '$Entrypoint' fehlgeschlagen ($($result.Status)): $($result.Message)"
    }
    return $result
}

function Get-PerformanceTrainingScenario {
    [CmdletBinding()]
    param(
        [ValidateSet('CON-004','DGN-005')][string]$ScenarioId,
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
        [Parameter(Mandatory)][ValidateSet('CON-004','DGN-005')][string]$ScenarioId,
        [Parameter(Mandatory)][ValidateSet('docker','podman')][string]$Provider,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [string]$SqlServerLabModulePath,
        [string]$SqlcmdPath,
        [string]$StateRoot
    )
    $definition = Resolve-ScenarioDefinition $ScenarioId
    Resolve-LabModule $SqlServerLabModulePath
    $root = Resolve-ScenarioStateRoot $StateRoot
    $env:SQL_SERVER_LAB_STATE = $root
    $statePath = Get-StatePath $ScenarioId $root
    if (Test-Path -LiteralPath $statePath) { throw "$ScenarioId besitzt bereits einen lokalen Lifecycle-Zustand." }
    $manifest = Join-Path $script:RepositoryRoot $definition.LabManifests[$Provider]
    $adapterPath = Join-Path $script:RepositoryRoot $definition.AdapterPath
    $validation = Test-SqlServerLabManifest -Path $manifest
    if (-not $validation.IsValid) { throw "SQL_Server_Lab-Manifest ungueltig: $($validation.Errors -join '; ')" }
    $adapterValidation = Test-SqlServerLabAdapter -Path $adapterPath
    if (-not $adapterValidation.IsReady) { throw "$ScenarioId-Adapter ungueltig: $($adapterValidation.Errors -join '; ')" }
    $lab = New-SqlServerLab -Manifest $manifest -SaPassword $SaPassword -StateRoot $root -NonInteractive
    try {
        $detail = Get-SqlServerLab -RunId $lab.RunId -Detailed
        $instance = @($detail.Instances | Where-Object Id -eq 'primary')[0]
        if (-not $instance -or -not $instance.ContainerUp) { throw 'Die primaere Lab-Instanz ist nicht betriebsbereit.' }
        $server = "$($instance.Host),$($instance.Port)"
        $runtimeAdapterValidation = Invoke-WithScenarioSqlcmdPath -SqlcmdPath $SqlcmdPath -Action {
            Test-SqlServerLabAdapter -Path $adapterPath -RunId $lab.RunId -InstanceId 'primary' -StateRoot $root
        }
        if (-not $runtimeAdapterValidation.IsReady) { throw "$ScenarioId-Adapter ist mit dem Lab-Run inkompatibel: $($runtimeAdapterValidation.Errors -join '; ')" }
        Invoke-ScenarioAdapter -AdapterPath $adapterPath -RunId $lab.RunId -SaPassword $SaPassword -Entrypoint install -StateRoot $root -SqlcmdPath $SqlcmdPath | Out-Null
        Invoke-ScenarioAdapter -AdapterPath $adapterPath -RunId $lab.RunId -SaPassword $SaPassword -Entrypoint validate -StateRoot $root -SqlcmdPath $SqlcmdPath | Out-Null
        $database = $definition.Database
        $contract = Get-Content -Raw -LiteralPath (Join-Path $script:RepositoryRoot $definition.ScenarioPath) | ConvertFrom-Json
        Write-ScenarioState $ScenarioId $root @{
            ScenarioId=$ScenarioId; RunId=$lab.RunId; Provider=$Provider; Database=$database;
            AdapterProjectId=$adapterValidation.ProjectId; AdapterContractVersion=$adapterValidation.Adapter.adapterContractVersion;
            Status='READY_FOR_USER'; CreatedUtc=[DateTime]::UtcNow.ToString('o')
        }
        [PSCustomObject]@{
            ScenarioId=$ScenarioId; Status='READY_FOR_USER'; RunId=$lab.RunId; Provider=$Provider;
            Server=$server; Database=$database; SafetyLevel=$definition.SafetyLevel; AdapterProjectId=$adapterValidation.ProjectId;
            AdapterContractVersion=$adapterValidation.Adapter.adapterContractVersion;
            SqlcmdVariables=[ordered]@{DemoId=$definition.DemoId;RunToken=$definition.RunToken}
            SessionRoles=@($contract.orchestration.manual.sessionScripts | Sort-Object startOrder | Select-Object role,script,startOrder,instruction)
            EntryDocument=Join-Path $script:RepositoryRoot $contract.interactive.entryDocument
            ResetCommand="Reset-PerformanceTrainingScenario -ScenarioId $ScenarioId"
            RemoveCommand="Remove-PerformanceTrainingScenario -ScenarioId $ScenarioId"
        }
    }
    catch {
        Remove-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
        Remove-SqlServerLab -RunId $lab.RunId -StateRoot $root -Force -Confirm:$false | Out-Null
        throw
    }
}

function Reset-PerformanceTrainingScenario {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('CON-004','DGN-005')][string]$ScenarioId,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [string]$SqlServerLabModulePath,
        [string]$SqlcmdPath,
        [string]$StateRoot
    )
    $definition=Resolve-ScenarioDefinition $ScenarioId; Resolve-LabModule $SqlServerLabModulePath
    $root=Resolve-ScenarioStateRoot $StateRoot; $env:SQL_SERVER_LAB_STATE=$root; $state=Read-ScenarioState $ScenarioId $root
    $detail=Get-SqlServerLab -RunId $state.RunId -Detailed; $instance=@($detail.Instances | Where-Object Id -eq 'primary')[0]
    if (-not $instance -or -not $instance.ContainerUp) { throw 'Die Szenarioinstanz ist nicht betriebsbereit.' }
    $adapterPath=Join-Path $script:RepositoryRoot $definition.AdapterPath
    Invoke-ScenarioAdapter -AdapterPath $adapterPath -RunId $state.RunId -SaPassword $SaPassword -Entrypoint cleanup -StateRoot $root -SqlcmdPath $SqlcmdPath | Out-Null
    Invoke-ScenarioAdapter -AdapterPath $adapterPath -RunId $state.RunId -SaPassword $SaPassword -Entrypoint install -StateRoot $root -SqlcmdPath $SqlcmdPath | Out-Null
    Invoke-ScenarioAdapter -AdapterPath $adapterPath -RunId $state.RunId -SaPassword $SaPassword -Entrypoint validate -StateRoot $root -SqlcmdPath $SqlcmdPath | Out-Null
    [PSCustomObject]@{ScenarioId=$ScenarioId;Status='READY_FOR_USER';RunId=$state.RunId;Provider=$state.Provider;Database=$state.Database;AdapterProjectId=$state.AdapterProjectId;AdapterContractVersion=$state.AdapterContractVersion}
}

function Remove-PerformanceTrainingScenario {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][ValidateSet('CON-004','DGN-005')][string]$ScenarioId,
        [Parameter(Mandatory)][SecureString]$SaPassword,
        [string]$SqlServerLabModulePath,
        [string]$SqlcmdPath,
        [string]$StateRoot
    )
    $definition=Resolve-ScenarioDefinition $ScenarioId; Resolve-LabModule $SqlServerLabModulePath
    $root=Resolve-ScenarioStateRoot $StateRoot; $env:SQL_SERVER_LAB_STATE=$root; $state=Read-ScenarioState $ScenarioId $root
    if (-not $PSCmdlet.ShouldProcess("$ScenarioId / $($state.RunId)",'fachliche Artefakte und Lab-Infrastruktur entfernen')) { return }
    $detail=Get-SqlServerLab -RunId $state.RunId -Detailed; $instance=@($detail.Instances | Where-Object Id -eq 'primary')[0]
    if ($instance -and $instance.ContainerUp) {
        $adapterPath=Join-Path $script:RepositoryRoot $definition.AdapterPath
        Invoke-ScenarioAdapter -AdapterPath $adapterPath -RunId $state.RunId -SaPassword $SaPassword -Entrypoint cleanup -StateRoot $root -SqlcmdPath $SqlcmdPath | Out-Null
    }
    $removed=Remove-SqlServerLab -RunId $state.RunId -StateRoot $root -Force -Confirm:$false
    if ($removed.Status -ne 'REMOVED') { throw "Infrastrukturabbau endete mit $($removed.Status)." }
    Remove-Item -LiteralPath (Get-StatePath $ScenarioId $root) -Force
    [PSCustomObject]@{ScenarioId=$ScenarioId;Status='REMOVED';RunId=$state.RunId;Provider=$state.Provider}
}

Export-ModuleMember -Function Get-PerformanceTrainingScenario,Start-PerformanceTrainingScenario,Reset-PerformanceTrainingScenario,Remove-PerformanceTrainingScenario
