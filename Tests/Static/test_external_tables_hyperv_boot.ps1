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
$fixtureDvd = @{}
$sourceMedia = Join-Path $directory.FullName 'source.iso'
$queryMedia = Join-Path $directory.FullName 'query.iso'
[IO.File]::WriteAllText($sourceMedia, 'synthetic source media')
[IO.File]::WriteAllText($queryMedia, 'synthetic query media')
$bound.SourceMediaSha256 = (Get-FileHash -LiteralPath $sourceMedia).Hash
$bound.QueryMediaSha256 = (Get-FileHash -LiteralPath $queryMedia).Hash
$fixtureDvd[$bound.QueryVmId] = [pscustomobject]@{VMId=$bound.QueryVmId; Path=$null}
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
function Get-VMDvdDrive { param($VM); if ($fixtureDvd.ContainsKey($VM.Id)) { $fixtureDvd[$VM.Id] } }
function Add-VMDvdDrive {
    param($VM, $Path, [switch] $Confirm)
    if ($VM.State -cne 'Off' -or $Path -cne $sourceMedia -or $VM.Id -ne $bound.SourceVmId) {
        throw 'Wrong source medium.'
    }
    $fixtureDvd[$VM.Id] = [pscustomobject]@{VMId=$VM.Id; Path=$Path}
    $events.Add('source-media')
}
function Set-VMDvdDrive {
    param($VMDvdDrive, $Path, [switch] $Confirm)
    if ($VMDvdDrive.Path -or $Path -cne $queryMedia -or $VMDvdDrive.VMId -ne $bound.QueryVmId) {
        throw 'Wrong query medium.'
    }
    $VMDvdDrive.Path = $Path
    $events.Add('query-media')
}
function Start-VM {
    param($VM, [switch] $Confirm)
    if ($VM.Count -ne 2 -or $fixtureAdapters.Count -ne 0) { throw 'Unsafe boot target.' }
    if ($fixtureDvd[$bound.SourceVmId].Path -cne $sourceMedia -or $fixtureDvd[$bound.QueryVmId].Path -cne $queryMedia) {
        throw 'Boot reached before both media matched.'
    }
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
    $correct = $bound.QueryMediaSha256
    $bound.QueryMediaSha256 = $bound.SourceMediaSha256
    Confirm-Rejected 'Boot'
    $bound.QueryMediaSha256 = $correct
    $fixtureDvd[$bound.QueryVmId].Path = $sourceMedia
    Confirm-Rejected 'Boot'
    $fixtureDvd[$bound.QueryVmId].Path = $null
    $originalBytes = [IO.File]::ReadAllBytes($queryMedia)
    [IO.File]::WriteAllText($queryMedia, 'unexpected replacement')
    Confirm-Rejected 'Boot'
    [IO.File]::WriteAllBytes($queryMedia, $originalBytes)
    $boot = & $scriptPath @bound -Phase Boot -ApplyOwnedRun | ConvertFrom-Json
    if ($boot.status -cne 'BOOTED' -or ($events -join ',') -cne 'source-media,query-media,boot' -or $fixtureAdapters.Count) {
        throw 'Boot did not leave the owned guests detached.'
    }
    Confirm-Rejected 'Boot'
    $fixtureAdapters.Add([pscustomobject]@{VMId=[guid]::NewGuid(); SwitchId=$bound.SwitchId; IsManagementOs=$false})
    Confirm-Rejected 'Attach'
    $fixtureAdapters.Clear()
    $fixtureDvd[$bound.QueryVmId].Path = $null
    Confirm-Rejected 'Attach'
    $fixtureDvd[$bound.QueryVmId].Path = $queryMedia
    $attach = & $scriptPath @bound -Phase Attach -ApplyOwnedRun | ConvertFrom-Json
    if ($attach.status -cne 'ATTACHED' -or ($events -join ',') -cne 'source-media,query-media,boot,add,add,connect' -or
        @($fixtureAdapters | Where-Object SwitchId -EQ $bound.SwitchId).Count -ne 2) {
        throw 'Only the owned guests may join their private switch.'
    }
    Confirm-Rejected 'Attach'
} finally {
    [IO.File]::Delete($bound.SourceDiskPath)
    [IO.File]::Delete($bound.QueryDiskPath)
    [IO.File]::Delete($sourceMedia)
    [IO.File]::Delete($queryMedia)
    [IO.Directory]::Delete($directory.FullName)
}
'External Tables Hyper-V boot and attachment tests passed.'
