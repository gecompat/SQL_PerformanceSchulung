[CmdletBinding()]
param(
    [Parameter(Mandatory)] [guid] $SourceVmId,
    [Parameter(Mandatory)] [guid] $QueryVmId,
    [Parameter(Mandatory)] [string] $SourceDiskPath,
    [Parameter(Mandatory)] [string] $QueryDiskPath
)

$ErrorActionPreference = 'Stop'
if ([guid]::Empty -in @($SourceVmId, $QueryVmId) -or $SourceVmId -eq $QueryVmId) {
    throw 'External Tables requires two distinct recorded VM IDs.'
}

try {
    foreach ($path in @($SourceDiskPath, $QueryDiskPath)) {
        if (-not [IO.Path]::IsPathFullyQualified($path) -or $path -match '^[\\/]{2}' -or
            [IO.Path]::GetFullPath($path) -cne $path -or [IO.Path]::GetExtension($path) -ine '.vhdx') {
            throw 'Unexpected VHDX path.'
        }
    }
    if ($SourceDiskPath -ieq $QueryDiskPath) { throw 'Expected two disk copies.' }
} catch {
    throw 'External Tables requires two distinct recorded local VHDX paths.'
}

$targets = @(
    @{ Id = $SourceVmId; Path = $SourceDiskPath }
    @{ Id = $QueryVmId; Path = $QueryDiskPath }
)
foreach ($target in $targets) {
    try {
        $vms = @(Get-VM -Id $target.Id -ErrorAction Stop)
    } catch {
        throw 'External Tables could not read the recorded Hyper-V guest.'
    }
    if ($vms.Count -ne 1 -or $vms[0].Id -isnot [guid] -or $vms[0].Id -ne $target.Id) {
        throw 'External Tables could not read the recorded Hyper-V guest.'
    }
    $vm = $vms[0]
    if ([string]$vm.State -cne 'Running' -or $vm.ProcessorCount -isnot [long] -or $vm.ProcessorCount -ne 2 -or
        $vm.DynamicMemoryEnabled -isnot [bool] -or $vm.DynamicMemoryEnabled -or
        $vm.MemoryStartup -isnot [long] -or $vm.MemoryAssigned -isnot [long] -or
        $vm.MemoryStartup -ne 4GB -or $vm.MemoryAssigned -ne 4GB) {
        throw 'External Tables guest does not match the running CPU and memory profile.'
    }

    try {
        $devices = @(Get-VMHardDiskDrive -VM $vm -ErrorAction Stop)
    } catch {
        throw 'External Tables could not read the recorded guest disk attachment.'
    }
    if ($devices.Count -ne 1 -or $devices[0].Path -ine $target.Path) {
        throw 'External Tables guest does not have exactly its recorded disk copy attached.'
    }

    try {
        $disks = @(Get-VHD -Path $target.Path -ErrorAction Stop)
    } catch {
        throw 'External Tables could not read the recorded VHDX metadata.'
    }
    if ($disks.Count -ne 1 -or $disks[0].Path -ine $target.Path -or
        [string]$disks[0].VhdFormat -cne 'VHDX' -or $disks[0].ParentPath -or
        $null -eq $disks[0].PSObject.Properties['ParentPath'] -or
        $disks[0].Size -isnot [ulong] -or $disks[0].Size -eq 0 -or $disks[0].Size -gt 24GB) {
        throw 'External Tables guest disk is not an independent VHDX within the capacity limit.'
    }
}

[ordered]@{ status = 'PASS'; guest_count = 2; vcpus_per_guest = 2; memory_bytes_per_guest = 4GB; max_disk_bytes_per_guest = 24GB } |
    ConvertTo-Json -Compress
