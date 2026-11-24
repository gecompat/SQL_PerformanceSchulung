$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot '../Runtime/Remove-ExternalTablesHyperVOwnedRun.ps1'
$directory = [IO.Directory]::CreateTempSubdirectory('sqlperf-ext-owned-test-')
$inputs = @{
    RunToken = 'TEST0053'
    SourceVmId = [guid]::NewGuid()
    QueryVmId = [guid]::NewGuid()
    SwitchId = [guid]::NewGuid()
    SourceDiskId = [guid]::NewGuid()
    QueryDiskId = [guid]::NewGuid()
    SourceDiskPath = Join-Path $directory.FullName 'source.vhdx'
    QueryDiskPath = Join-Path $directory.FullName 'query.vhdx'
}
$fakeGuests = @{}
$fakeDisks = @{}
$fakeEvents = [Collections.Generic.List[string]]::new()
$fake = @{ Switch = $null; ExtraAdapter = $null; ForeignDisk = $false }
$unrelatedVm = [pscustomobject]@{ Id = [guid]::NewGuid(); Name = 'Unrelated' }

function Reset-Fixture {
    $fakeEvents.Clear()
    $fakeGuests.Clear()
    $fakeDisks.Clear()
    $fake.ExtraAdapter = $null
    $fake.ForeignDisk = $false
    $fake.MissingDiskReference = $false
    $fake.InventoryFailure = $false
    $fake.MissingPortReference = $false
    $fake.Switch = [pscustomobject]@{ Id = $inputs.SwitchId; Name = 'SQLPerfExt-TEST0053'; SwitchType = 'Private' }
    foreach ($role in @('SOURCE', 'QUERY')) {
        $vmId = $inputs["$($role)VmId"]
        $path = $inputs["$($role)DiskPath"]
        $fakeGuests[$vmId] = [pscustomobject]@{
            Id = $vmId; Name = "SQLPerfExt-TEST0053-$role"; Notes = "SQLPERF.ExternalTables/TEST0053/$role"
            Path = $path; State = 'Running'
        }
        $fakeDisks[$path] = [pscustomobject]@{
            Path = $path; DiskIdentifier = [string]$inputs["$($role)DiskId"]; VhdFormat = 'VHDX'
            ParentPath = $null; Attached = $true
        }
        [IO.File]::WriteAllBytes($path, [byte[]]::new(0))
    }
}

function Get-VM { $fakeGuests.Values; $unrelatedVm }
function Get-VMSwitch { if ($null -ne $fake.Switch) { $fake.Switch } }
function Get-VMNetworkAdapter {
    param([object[]] $VM, [switch] $ManagementOS, [string] $SwitchName)
    if ($ManagementOS) {
        if ($SwitchName -cne $fake.Switch.Name) { throw 'Unexpected management switch lookup.' }
        if ($fake.ExtraAdapter.IsManagementOs) { $fake.ExtraAdapter }
        return
    }
    foreach ($guest in $VM) {
        [pscustomobject]@{ SwitchId = if ($fake.Switch) { $inputs.SwitchId } else { $null }; VMId = $guest.Id; IsManagementOs = $false }
    }
}
function Get-VMHardDiskDrive {
    param($VM)
    if ($VM.Id -eq $unrelatedVm.Id) { throw 'The script queried a foreign drive individually.' }
    [pscustomobject]@{ Path = $VM.Path }
}
function Get-CimInstance {
    param($Namespace, $ClassName, $Filter, $Property)
    if ($ClassName -ceq 'Msvm_EthernetPortAllocationSettingData') {
        if ($fake.Switch) {
            $n = $fakeGuests.Count + [int]($null -ne $fake.ExtraAdapter -and -not $fake.ExtraAdapter.IsManagementOs) - [int]$fake.MissingPortReference
            for ($i = 0; $i -lt $n; $i++) {
                [pscustomobject]@{ HostResource = @(
                    'root\virtualization\v2:Msvm_VirtualEthernetSwitch.CreationClassName="Msvm_VirtualEthernetSwitch",Name="' + $inputs.SwitchId + '"'
                ) }
            }
        }
        return
    }
    if ($Namespace -cne 'root/virtualization/v2' -or $ClassName -cne 'Msvm_StorageAllocationSettingData' -or
        $Filter -cne "ResourceSubType = 'Microsoft:Hyper-V:Virtual Hard Disk'" -or $Property -cne 'HostResource') {
        throw 'Unexpected global VHD inventory query.'
    }
    if ($fake.InventoryFailure) { throw 'Synthetic provider inventory failure.' }
    foreach ($guest in $fakeGuests.Values) {
        if (-not $fake.MissingDiskReference -or $guest.Id -ne $inputs.SourceVmId) {
            [pscustomobject]@{ HostResource = @($guest.Path) }
        }
    }
    if ($fake.ForeignDisk) { [pscustomobject]@{ HostResource = @($inputs.SourceDiskPath) } }
}
function Get-VHD {
    param($Path)
    $fakeDisks[$Path]
}
function Stop-VM {
    param($VM, [switch] $TurnOff, [switch] $Force, [switch] $Confirm)
    if (-not $TurnOff -or -not $Force -or $Confirm -or -not $fakeGuests.ContainsKey($VM.Id)) { throw 'Unexpected stop target.' }
    $fakeEvents.Add("stop:$($VM.Name)")
    $VM.State = 'Off'
}
function Remove-VM {
    param($VM, [switch] $Force, [switch] $Confirm)
    if (-not $Force -or $Confirm -or -not $fakeGuests.ContainsKey($VM.Id) -or $VM.State -cne 'Off') { throw 'Unexpected VM removal target.' }
    $fakeEvents.Add("remove:$($VM.Name)")
    $fakeDisks[$VM.Path].Attached = $false
    $fakeGuests.Remove($VM.Id)
}
function Remove-VMSwitch {
    param($VMSwitch, [switch] $Force, [switch] $Confirm)
    if (-not $Force -or $Confirm -or $VMSwitch.Id -ne $inputs.SwitchId -or $fakeGuests.Count -ne 0 -or
        [IO.File]::Exists($inputs.SourceDiskPath) -or [IO.File]::Exists($inputs.QueryDiskPath)) {
        throw 'Unexpected switch removal target or sequence.'
    }
    $fakeEvents.Add('remove:switch')
    $fake.Switch = $null
}

function Confirm-Rejected {
    try { $null = & $scriptPath @inputs -ApplyOwnedRun }
    catch {
        if ($_.Exception.Message -ceq 'External Tables could not verify or remove the recorded Hyper-V resources.') {
            if ($fakeEvents.Count -ne 0) { throw 'A rejected inventory reached a destructive cmdlet.' }
            return
        }
        throw
    }
    throw 'An ownership conflict was unexpectedly accepted.'
}

try {
    Reset-Fixture
    $dry = & $scriptPath @inputs | ConvertFrom-Json
    if ($dry.status -cne 'VERIFIED' -or $fakeEvents.Count -ne 0) { throw 'Read-only mode changed the fixture.' }
    $fake.ExtraAdapter = [pscustomobject]@{ SwitchId = $inputs.SwitchId; VMId = $unrelatedVm.Id; IsManagementOs = $false }
    Confirm-Rejected
    Reset-Fixture
    $fake.ExtraAdapter = [pscustomobject]@{ SwitchId = $inputs.SwitchId; VMId = $null; IsManagementOs = $true }
    Confirm-Rejected
    Reset-Fixture
    $fake.MissingPortReference = $true
    Confirm-Rejected
    Reset-Fixture
    $fake.ForeignDisk = $true
    Confirm-Rejected
    Reset-Fixture
    $fake.MissingDiskReference = $true
    Confirm-Rejected
    Reset-Fixture
    $fake.InventoryFailure = $true
    Confirm-Rejected
    Reset-Fixture
    $fakeGuests[$inputs.SourceVmId].Notes = 'foreign'
    Confirm-Rejected
    Reset-Fixture
    $fakeDisks[$inputs.QueryDiskPath].DiskIdentifier = [string][guid]::NewGuid()
    Confirm-Rejected
    Reset-Fixture
    $result = & $scriptPath @inputs -ApplyOwnedRun | ConvertFrom-Json
    $expected = 'stop:SQLPerfExt-TEST0053-SOURCE,remove:SQLPerfExt-TEST0053-SOURCE,stop:SQLPerfExt-TEST0053-QUERY,remove:SQLPerfExt-TEST0053-QUERY,remove:switch'
    if ($result.status -cne 'REMOVED' -or ($fakeEvents -join ',') -cne $expected) {
        throw 'The owned cleanup did not follow its guarded sequence.'
    }
    $fakeEvents.Clear()
    $result = & $scriptPath @inputs -ApplyOwnedRun | ConvertFrom-Json
    if ($result.status -cne 'REMOVED' -or $fakeEvents.Count -ne 0) { throw 'Cleanup was not repeatable.' }
    Reset-Fixture
    $fakeGuests.Remove($inputs.SourceVmId)
    $fakeDisks[$inputs.SourceDiskPath].Attached = $false
    $result = & $scriptPath @inputs -ApplyOwnedRun | ConvertFrom-Json
    if ($result.status -cne 'REMOVED' -or ($fakeEvents -join ',') -cne
        'stop:SQLPerfExt-TEST0053-QUERY,remove:SQLPerfExt-TEST0053-QUERY,remove:switch') {
        throw 'The cleanup could not resume from an owned disk without its VM.'
    }
    Reset-Fixture
    $fake.Switch = $null
    $fakeGuests[$inputs.SourceVmId].State = 'Off'
    $fakeGuests.Remove($inputs.QueryVmId)
    $fakeDisks[$inputs.QueryDiskPath].Attached = $false
    $partial = $inputs.Clone()
    $partial.QueryVmId = [guid]::Empty
    $partial.SwitchId = [guid]::Empty
    $knownQueryDisk = $partial.QueryDiskId
    $partial.QueryDiskId = [guid]::Empty
    $rejected = $false
    try { $null = & $scriptPath @partial -PartialProvision -ApplyOwnedRun }
    catch {
        if ($_.Exception.Message -cne 'External Tables could not verify or remove the recorded Hyper-V resources.') { throw }
        $rejected = $true
    }
    if (-not $rejected -or $fakeEvents.Count -or -not [IO.File]::Exists($inputs.QueryDiskPath)) {
        throw 'An unrecorded disk was accepted or touched.'
    }

    $partial.QueryDiskId = $knownQueryDisk
    $result = & $scriptPath @partial -PartialProvision -ApplyOwnedRun | ConvertFrom-Json
    if ($result.status -cne 'REMOVED' -or ($fakeEvents -join ',') -cne 'remove:SQLPerfExt-TEST0053-SOURCE' -or
        [IO.File]::Exists($inputs.SourceDiskPath) -or [IO.File]::Exists($inputs.QueryDiskPath)) {
        throw 'Partial recovery did not confirm the recorded VM and both disks were gone.'
    }
    $fakeEvents.Clear()
    $result = & $scriptPath @partial -PartialProvision -ApplyOwnedRun | ConvertFrom-Json
    if ($result.status -cne 'REMOVED' -or $fakeEvents.Count) { throw 'Partial recovery was not repeatable.' }
} finally {
    [IO.File]::Delete($inputs.SourceDiskPath)
    [IO.File]::Delete($inputs.QueryDiskPath)
    [IO.Directory]::Delete($directory.FullName)
}
'External Tables Hyper-V owned cleanup tests passed.'
