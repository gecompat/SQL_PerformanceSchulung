$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot '../Runtime/Start-ExternalTablesHyperVOwnedRun.ps1'
$directory = [IO.Directory]::CreateTempSubdirectory('sqlperf-ext-boot-test-')
$bound = @{
    RunToken='TEST0078'; SourceVmId=[guid]::NewGuid(); QueryVmId=[guid]::NewGuid(); SwitchId=[guid]::NewGuid()
    SourceDiskId=[guid]::NewGuid(); QueryDiskId=[guid]::NewGuid()
    SourceDiskPath=Join-Path $directory.FullName 'source.vhdx'
    QueryDiskPath=Join-Path $directory.FullName 'query.vhdx'
}
$fixtureGuests = @{}
$disks = @{}
$fixtureAdapters = [Collections.Generic.List[object]]::new()
$events = [Collections.Generic.List[string]]::new()
$pilotSwitch = [pscustomobject]@{Id=$bound.SwitchId; Name='SQLPerfExt-TEST0078'; SwitchType='Private'}

foreach ($role in @('SOURCE','QUERY')) {
    $id = $bound["${role}VmId"]
    $disk = $bound["${role}DiskPath"]
    [IO.File]::WriteAllBytes($disk, [byte[]]::new(0))
    $fixtureGuests[$id] = [pscustomobject]@{
        Id=$id; Name="SQLPerfExt-TEST0078-$role"; Notes="SQLPERF.ExternalTables/TEST0078/$role"; State='Off'
        ProcessorCount=2; DynamicMemoryEnabled=$false; MemoryStartup=4GB; Path=$disk
    }
    $disks[$disk] = [pscustomobject]@{
        Path=$disk; DiskIdentifier=[string]$bound["${role}DiskId"]; VhdFormat='VHDX'
        ParentPath=$null; Attached=$false; Size=[ulong]24GB
    }
}
function Get-VM {
    param([guid] $Id)
    if ($PSBoundParameters.ContainsKey('Id')) { $fixtureGuests[$Id] } else { $fixtureGuests.Values }
}
function Get-VMSwitch {
    param([guid] $Id)
    if (-not $PSBoundParameters.ContainsKey('Id') -or $Id -eq $pilotSwitch.Id) { $pilotSwitch }
}
function Get-VMNetworkAdapter { param([switch] $All); $fixtureAdapters }
function Get-VMHardDiskDrive { param($VM); [pscustomobject]@{Path=$VM.Path} }
function Get-VHD { param($Path); $disks[$Path] }
function Start-VM {
    param($VM, [switch] $Confirm)
    if ($VM.Count -ne 2 -or $fixtureAdapters.Count -ne 0) { throw 'Unsafe boot target.' }
    foreach ($guest in $VM) {
        $guest.State = 'Running'
        $disks[$guest.Path].Attached = $true
    }
    $events.Add('boot')
}
function Add-VMNetworkAdapter {
    param($VM, $Name, [switch] $Passthru, [switch] $Confirm)
    if (-not $Passthru -or $VM.State -cne 'Running' -or $Name -cne 'SQLPerfExternal') {
        throw 'Unexpected adapter creation.'
    }
    $adapter = [pscustomobject]@{VMId=$VM.Id; SwitchId=$null; IsManagementOs=$false}
    $fixtureAdapters.Add($adapter)
    $events.Add('add')
    $adapter
}
function Connect-VMNetworkAdapter {
    param($VMNetworkAdapter, $VMSwitch, [switch] $Confirm)
    if ($VMNetworkAdapter.Count -ne 2 -or $VMSwitch.Id -ne $bound.SwitchId -or
        @($VMNetworkAdapter | Where-Object SwitchId).Count) { throw 'Unsafe network targets.' }
    foreach ($adapter in $VMNetworkAdapter) { $adapter.SwitchId = $VMSwitch.Id }
    $events.Add('connect')
}
function Confirm-Rejected([string] $Phase) {
    $count = $events.Count
    try { $null = & $scriptPath @bound -Phase $Phase -ApplyOwnedRun }
    catch {
        if ($_.Exception.Message -ceq 'External Tables could not verify or transition the recorded Hyper-V resources.' -and
            $events.Count -eq $count) { return }
        throw
    }
    throw 'Invalid transition was accepted.'
}
try {
    $dry = & $scriptPath @bound -Phase Boot | ConvertFrom-Json
    if ($dry.status -cne 'VERIFIED' -or $events.Count) { throw 'Dry run changed the fixture.' }
    Confirm-Rejected 'Attach'
    $pilotSwitch.SwitchType = 'External'
    Confirm-Rejected 'Boot'
    $pilotSwitch.SwitchType = 'Private'
    $disks[$bound.SourceDiskPath].Size = [ulong]25GB
    Confirm-Rejected 'Boot'
    $disks[$bound.SourceDiskPath].Size = [ulong]24GB
    $boot = & $scriptPath @bound -Phase Boot -ApplyOwnedRun | ConvertFrom-Json
    if ($boot.status -cne 'BOOTED' -or ($events -join ',') -cne 'boot' -or $fixtureAdapters.Count) {
        throw 'Boot did not leave the owned guests detached.'
    }
    Confirm-Rejected 'Boot'
    $fixtureAdapters.Add([pscustomobject]@{VMId=[guid]::NewGuid(); SwitchId=$bound.SwitchId; IsManagementOs=$false})
    Confirm-Rejected 'Attach'
    $fixtureAdapters.Clear()
    $attach = & $scriptPath @bound -Phase Attach -ApplyOwnedRun | ConvertFrom-Json
    if ($attach.status -cne 'ATTACHED' -or ($events -join ',') -cne 'boot,add,add,connect' -or
        @($fixtureAdapters | Where-Object SwitchId -EQ $bound.SwitchId).Count -ne 2) {
        throw 'Only the owned guests may join their private switch.'
    }
    Confirm-Rejected 'Attach'
} finally {
    [IO.File]::Delete($bound.SourceDiskPath)
    [IO.File]::Delete($bound.QueryDiskPath)
    [IO.Directory]::Delete($directory.FullName)
}
'External Tables Hyper-V boot and attachment tests passed.'
