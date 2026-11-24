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
    param([switch] $All)
    foreach ($vm in $fakeGuests.Values) {
        [pscustomobject]@{ SwitchId = $inputs.SwitchId; VMId = $vm.Id; IsManagementOs = $false }
    }
    if ($null -ne $fake.ExtraAdapter) { $fake.ExtraAdapter }
}
function Get-VMHardDiskDrive {
    param($VM)
    if ($VM.Id -ne $unrelatedVm.Id) { [pscustomobject]@{ Path = $VM.Path } }
    elseif ($fake.ForeignDisk) { [pscustomobject]@{ Path = $inputs.SourceDiskPath } }
}
function Get-VHD {
    param($Path)
    $fakeDisks[$Path]
}
function Stop-VM {
    param($VM, [switch] $TurnOff, [switch] $Confirm)
    if (-not $TurnOff -or -not $fakeGuests.ContainsKey($VM.Id)) { throw 'Unexpected stop target.' }
    $fakeEvents.Add("stop:$($VM.Name)")
    $VM.State = 'Off'
}
function Remove-VM {
    param($VM, [switch] $Confirm)
    if (-not $fakeGuests.ContainsKey($VM.Id) -or $VM.State -cne 'Off') { throw 'Unexpected VM removal target.' }
    $fakeEvents.Add("remove:$($VM.Name)")
    $fakeDisks[$VM.Path].Attached = $false
    $fakeGuests.Remove($VM.Id)
}
function Remove-VMSwitch {
    param($VMSwitch, [switch] $Confirm)
    if ($VMSwitch.Id -ne $inputs.SwitchId -or $fakeGuests.Count -ne 0 -or
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
    $fake.ForeignDisk = $true
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
} finally {
    [IO.File]::Delete($inputs.SourceDiskPath)
    [IO.File]::Delete($inputs.QueryDiskPath)
    [IO.Directory]::Delete($directory.FullName)
}
'External Tables Hyper-V owned cleanup tests passed.'
