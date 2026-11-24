$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot '../Runtime/New-ExternalTablesHyperVDetachedRun.ps1'
$root = [IO.Directory]::CreateTempSubdirectory('sqlperf-ext-prepare-test-')
$sourcePath = Join-Path $root.FullName 'source-template.vhdx'
$queryPath = Join-Path $root.FullName 'query-template.vhdx'
[IO.File]::WriteAllText($sourcePath, 'synthetic source template')
[IO.File]::WriteAllText($queryPath, 'synthetic query template')
$arguments = @{
    RunToken='TEST0057'; SourceTemplate=$sourcePath; QueryTemplate=$queryPath
    SourceSha256=(Get-FileHash -LiteralPath $sourcePath).Hash
    QuerySha256=(Get-FileHash -LiteralPath $queryPath).Hash
}
$fake = @{ Switch=$null; Failure=$false; TakenName=$null }
$fakeGuests = @{}
$fakeDisks = @{ $sourcePath = [guid]::NewGuid(); $queryPath = [guid]::NewGuid() }
$fakeEvents = [Collections.Generic.List[string]]::new()

function Get-VM {
    param([guid] $Id)
    if ($PSBoundParameters.ContainsKey('Id')) { if ($fakeGuests.ContainsKey($Id)) { $fakeGuests[$Id] }; return }
    $fakeGuests.Values
    if ($fake.TakenName) { [pscustomobject]@{ Name = $fake.TakenName } }
}
function Get-VMSwitch { if ($fake.Switch) { $fake.Switch } }
function Get-VHD {
    param([string] $Path)
    [pscustomobject]@{
        Path=$Path; DiskIdentifier=[string]$fakeDisks[$Path]; VhdFormat='VHDX'
        Attached=$false; ParentPath=$null; Size=[ulong]24GB
    }
}
function Set-VHD {
    param([string] $Path, [switch] $ResetDiskIdentifier, [switch] $Confirm)
    if (-not $ResetDiskIdentifier -or [IO.Path]::GetDirectoryName($Path) -ine $arguments.RunDirectory -or
        -not [IO.File]::Exists((Join-Path $arguments.RunDirectory 'external-tables-provision-intent.json'))) {
        throw 'Unexpected VHDX identity change.'
    }
    $fakeDisks[$Path] = [guid]::NewGuid()
    $fakeEvents.Add('disk')
}
function New-VM {
    param($Name, $Generation, $Path, $MemoryStartupBytes, $VHDPath, $BootDevice)
    if ($fake.Failure -and $Name.EndsWith('-QUERY')) { throw 'Synthetic stop at query VM creation.' }
    if ($Generation -ne 2 -or $MemoryStartupBytes -ne 4GB -or $BootDevice -cne 'VHD' -or
        [IO.Path]::GetDirectoryName($VHDPath) -ine $Path) { throw 'Unexpected creation profile.' }
    $vm = [pscustomobject]@{
        Id=[guid]::NewGuid(); Name=$Name; State='Off'; Notes=''; ProcessorCount=0; VHDPath=$VHDPath
        MemoryStartup=$MemoryStartupBytes; DynamicMemoryEnabled=$true
    }
    $fakeGuests[$vm.Id] = $vm
    $fakeEvents.Add('vm')
    $vm
}
function Set-VM {
    param($VM, $Notes, [switch] $StaticMemory, $AutomaticCheckpointsEnabled, $CheckpointType,
        $AutomaticStartAction, $AutomaticStopAction)
    if ($AutomaticCheckpointsEnabled -or $CheckpointType -cne 'Disabled' -or
        $AutomaticStartAction -cne 'Nothing' -or $AutomaticStopAction -cne 'TurnOff') {
        throw 'Unexpected automatic VM actions.'
    }
    $VM.Notes=$Notes
    $VM.DynamicMemoryEnabled=-not $StaticMemory
}
function Set-VMProcessor { param($VM, [int] $Count); $VM.ProcessorCount=$Count }
function Set-VMFirmware {
    param($VM, $EnableSecureBoot, $SecureBootTemplate)
    if ($EnableSecureBoot -cne 'On' -or $SecureBootTemplate -cne 'MicrosoftUEFICertificateAuthority') {
        throw 'Unexpected Secure Boot configuration.'
    }
}
function Get-VMNetworkAdapter {
    param($VM, [switch] $All)
    if ($All) {
        foreach ($guest in $fakeGuests.Values) { [pscustomobject]@{ VMId=$guest.Id; SwitchId=$null } }
    } else {
        [pscustomobject]@{ VMId=$VM.Id; SwitchId=$null }
    }
}
function Get-VMHardDiskDrive { param($VM); [pscustomobject]@{Path=$VM.VHDPath} }
function New-VMSwitch {
    param($Name, $SwitchType)
    if ($SwitchType -cne 'Private' -or $fakeGuests.Count -ne 2) { throw 'Unexpected switch profile.' }
    $fake.Switch = [pscustomobject]@{ Id=[guid]::NewGuid(); Name=$Name; SwitchType=$SwitchType }
    $fakeEvents.Add('switch')
    $fake.Switch
}

function Confirm-Rejected {
    try { $null = & $scriptPath @arguments -ApplyOwnedRun }
    catch {
        if ($_.Exception.Message -ceq 'External Tables could not verify or prepare the detached Hyper-V resources.') {
            return
        }
        throw
    }
    throw 'Invalid provision request was accepted.'
}

try {
    $arguments.RunDirectory = [IO.Directory]::CreateDirectory((Join-Path $root.FullName 'complete')).FullName
    $dry = & $scriptPath @arguments | ConvertFrom-Json
    if ($dry.status -cne 'VERIFIED' -or $fakeEvents.Count -ne 0 -or @(Get-ChildItem $arguments.RunDirectory).Count) {
        throw 'Read-only mode changed its fixture.'
    }
    $correct = $arguments.QuerySha256
    $arguments.QuerySha256 = '0' * 64
    Confirm-Rejected
    $arguments.QuerySha256 = $correct
    $fake.TakenName = 'SQLPerfExt-TEST0057-QUERY'
    Confirm-Rejected
    $fake.TakenName = $null
    if (@(Get-ChildItem $arguments.RunDirectory).Count -or $fakeEvents.Count) { throw 'Preflight mutated its fixture.' }
    $prepared = & $scriptPath @arguments -ApplyOwnedRun | ConvertFrom-Json
    $ready = Get-Content (Join-Path $arguments.RunDirectory 'external-tables-detached.json') -Raw | ConvertFrom-Json
    if ($prepared.status -cne 'DETACHED' -or ($fakeEvents -join ',') -cne 'disk,vm,disk,vm,switch' -or
        $ready.source_disk_id -eq $ready.query_disk_id -or $ready.source_vm -eq $ready.query_vm) {
        throw 'The two detached resources were not confirmed.'
    }
    Confirm-Rejected
    $fakeGuests.Clear()
    $fake.Switch = $null
    $fake.Failure = $true
    $arguments.RunDirectory = [IO.Directory]::CreateDirectory((Join-Path $root.FullName 'partial')).FullName
    Confirm-Rejected
    if (-not [IO.File]::Exists((Join-Path $arguments.RunDirectory 'external-tables-vm-SOURCE.json')) -or
        -not [IO.File]::Exists((Join-Path $arguments.RunDirectory 'external-tables-disk-QUERY.json')) -or
        [IO.File]::Exists((Join-Path $arguments.RunDirectory 'external-tables-detached.json'))) {
        throw 'The partial ownership records are incomplete.'
    }
    foreach ($role in @('Source', 'Query')) {
        if ((Get-FileHash -LiteralPath $arguments["$($role)Template"]).Hash -cne $arguments["$($role)Sha256"]) {
            throw 'Template content changed.'
        }
    }
} finally {
    $testPath = (Resolve-Path -LiteralPath $root.FullName).ProviderPath
    if ($testPath -cne $root.FullName) { throw 'Unexpected test directory identity.' }
    Remove-Item -LiteralPath $testPath -Recurse
}
'External Tables detached Hyper-V provision tests passed.'
