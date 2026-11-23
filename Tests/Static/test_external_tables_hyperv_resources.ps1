$ErrorActionPreference = 'Stop'
$verify = Join-Path $PSScriptRoot '../Runtime/Test-ExternalTablesHyperVResources.ps1'
$arguments = @{
    SourceVmId = [guid]::NewGuid()
    QueryVmId = [guid]::NewGuid()
    SourceDiskPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'source.vhdx'))
    QueryDiskPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'query.vhdx'))
}
$cpuFailure = 'External Tables guest does not match the running CPU and memory profile.'
$diskFailure = 'External Tables guest disk is not an independent VHDX within the capacity limit.'
$attachmentFailure = 'External Tables guest does not have exactly its recorded disk copy attached.'
$inventoryFailure = 'External Tables could not read the recorded Hyper-V guest.'
$queryOnly = $false
$failInventory = $false

function Get-VM {
    [CmdletBinding()]
    param([guid] $Id)
    if ($failInventory) { throw 'Hyper-V details must not leak' }
    if ($Id -eq $arguments.SourceVmId) { if (-not $queryOnly) { $source } }
    elseif ($Id -eq $arguments.QueryVmId) { $query }
    else { throw 'The verifier requested an unrecorded guest.' }
}

function Get-VMHardDiskDrive {
    [CmdletBinding()]
    param([object] $VM)
    $fakeDevices[$VM.Id]
}

function Get-VHD {
    [CmdletBinding()]
    param([string] $Path)
    if (-not $metadata.ContainsKey($Path)) { throw 'The verifier requested an unrecorded disk.' }
    $metadata[$Path]
}

function Confirm-Rejected([string] $Expected) {
    try { $null = & $verify @arguments }
    catch {
        if ($_.Exception.Message -ceq $Expected) { return }
        throw
    }
    throw "Unexpected success for condition '$Expected'."
}

function New-Guest([guid] $Id) {
    [pscustomobject]@{
        Id = $Id; State = 'Running'; ProcessorCount = [long]2; DynamicMemoryEnabled = $false
        MemoryStartup = [long]4GB; MemoryAssigned = [long]4GB
    }
}

$source = New-Guest $arguments.SourceVmId
$query = New-Guest $arguments.QueryVmId
$fakeDevices = @{
    $source.Id = [pscustomobject]@{Path = $arguments.SourceDiskPath}
    $query.Id = [pscustomobject]@{Path = $arguments.QueryDiskPath}
}
$metadata = @{
    $arguments.SourceDiskPath = [pscustomobject]@{
        Path = $arguments.SourceDiskPath; VhdFormat = 'VHDX'; ParentPath = $null; Size = [ulong]24GB
    }
    $arguments.QueryDiskPath = [pscustomobject]@{
        Path = $arguments.QueryDiskPath; VhdFormat = 'VHDX'; ParentPath = $null; Size = [ulong](24GB - 1MB)
    }
}

$result = & $verify @arguments | ConvertFrom-Json
if ($result.status -cne 'PASS' -or $result.guest_count -ne 2 -or
    $result.vcpus_per_guest -ne 2 -or $result.memory_bytes_per_guest -ne 4GB -or
    $result.max_disk_bytes_per_guest -ne 24GB) {
    throw 'The resource verifier did not confirm both recorded guest profiles.'
}

foreach ($change in @(
    @{Name = 'ProcessorCount'; Value = [long]3}
    @{Name = 'DynamicMemoryEnabled'; Value = $true}
    @{Name = 'MemoryStartup'; Value = [long]5GB}
    @{Name = 'MemoryAssigned'; Value = [long]3GB}
    @{Name = 'State'; Value = 'Off'}
)) {
    $previous = $query.($change.Name)
    $query.($change.Name) = $change.Value
    Confirm-Rejected $cpuFailure
    $query.($change.Name) = $previous
}
$queryOnly = $true
Confirm-Rejected $inventoryFailure
$queryOnly = $false
$failInventory = $true
Confirm-Rejected $inventoryFailure
$failInventory = $false
$ownedDevice = $fakeDevices[$query.Id]
$fakeDevices[$query.Id] = @($ownedDevice, $ownedDevice)
Confirm-Rejected $attachmentFailure
$fakeDevices[$query.Id] = $fakeDevices[$source.Id]
Confirm-Rejected $attachmentFailure
$fakeDevices[$query.Id] = $ownedDevice
$queryDisk = $metadata[$arguments.QueryDiskPath]
$queryDisk.Size = [ulong](24GB + 1MB)
Confirm-Rejected $diskFailure
$queryDisk.Size = [ulong]24GB
$queryDisk.ParentPath = 'foreign.vhdx'
Confirm-Rejected $diskFailure
$queryDisk.ParentPath = $null
$queryDisk.VhdFormat = 'VHD'
Confirm-Rejected $diskFailure
'External Tables Hyper-V resource tests passed.'
