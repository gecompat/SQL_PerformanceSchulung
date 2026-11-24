[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidatePattern('\A[A-Z0-9]{8}\z')] [string] $RunToken,
    [Parameter(Mandatory)] [guid] $SourceVmId,
    [Parameter(Mandatory)] [guid] $QueryVmId,
    [Parameter(Mandatory)] [guid] $SwitchId,
    [Parameter(Mandatory)] [string] $SourceDiskPath,
    [Parameter(Mandatory)] [string] $QueryDiskPath,
    [Parameter(Mandatory)] [guid] $SourceDiskId,
    [Parameter(Mandatory)] [guid] $QueryDiskId,
    [switch] $ApplyOwnedRun
)

$ErrorActionPreference = 'Stop'
$resourceIds = @($SourceVmId, $QueryVmId, $SwitchId, $SourceDiskId, $QueryDiskId)
if ($RunToken -cnotmatch '\A[A-Z0-9]{8}\z' -or [guid]::Empty -in $resourceIds -or
    @($resourceIds | Select-Object -Unique).Count -ne 5) {
    throw 'External Tables expected distinct recorded Hyper-V identities.'
}

$prefix = "SQLPerfExt-$RunToken"
$targets = @(
    @{ Id = $SourceVmId; Role = 'SOURCE'; DiskPath = $SourceDiskPath; DiskId = $SourceDiskId }
    @{ Id = $QueryVmId; Role = 'QUERY'; DiskPath = $QueryDiskPath; DiskId = $QueryDiskId }
)

function Read-OwnedDisk($Target) {
    $entry = Get-Item -LiteralPath $Target.DiskPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $entry) {
        if ([IO.Path]::GetFileName($Target.DiskPath) -iin @(Get-ChildItem -LiteralPath $runDirectory -Name -Force)) {
            throw 'Could not read a recorded disk.'
        }
        return
    }
    if ($entry.Attributes -band ([IO.FileAttributes]::Directory -bor [IO.FileAttributes]::ReparsePoint)) {
        throw 'Unexpected recorded disk object.'
    }
    $disk = @(Get-VHD -Path $Target.DiskPath)
    $id = [guid]::Empty
    if ($disk.Count -ne 1 -or $disk[0].Path -ine $Target.DiskPath -or
        -not [guid]::TryParse([string]$disk[0].DiskIdentifier, [ref]$id) -or $id -ne $Target.DiskId -or
        [string]$disk[0].VhdFormat -cne 'VHDX' -or
        $null -eq $disk[0].PSObject.Properties['ParentPath'] -or $disk[0].ParentPath -or $disk[0].Attached -isnot [bool]) {
        throw 'Recorded VHDX identity differs from live metadata.'
    }
    $disk[0]
}

function Read-OwnedInventory {
    $vms = @(Get-VM)
    $switches = @(Get-VMSwitch)
    if (@(($vms + $switches) | Where-Object { $_.Id -isnot [guid] }).Count) {
        throw 'Unexpected Hyper-V inventory.'
    }
    $switch = @($switches | Where-Object Id -EQ $SwitchId)
    if ($switch.Count -gt 1 -or ($switch.Count -eq 1 -and
        ($switch[0].Name -cne $prefix -or [string]$switch[0].SwitchType -cne 'Private'))) {
        throw 'Recorded switch identity differs from live metadata.'
    }
    $guestIds = @($SourceVmId, $QueryVmId)
    foreach ($adapter in @(Get-VMNetworkAdapter -All)) {
        if ($null -eq $adapter.PSObject.Properties['SwitchId'] -or $null -eq $adapter.PSObject.Properties['VMId'] -or
            $adapter.IsManagementOs -isnot [bool] -or
            ($null -ne $adapter.VMId -and $adapter.VMId -isnot [guid]) -or
            ($null -ne $adapter.SwitchId -and $adapter.SwitchId -isnot [guid])) {
            throw 'Unexpected Hyper-V adapter record.'
        }
        if ($adapter.SwitchId -eq $SwitchId -and
            ($switch.Count -ne 1 -or $adapter.IsManagementOs -or $adapter.VMId -notin $guestIds)) {
            throw 'Recorded switch has a foreign or management attachment.'
        }
        if ($adapter.VMId -in $guestIds -and
            ($adapter.IsManagementOs -or $adapter.SwitchId -notin @($null, [guid]::Empty, $SwitchId))) {
            throw 'Recorded VM has a foreign switch attachment.'
        }
    }
    $owned = @{}
    foreach ($vm in $vms) {
        $drives = @(Get-VMHardDiskDrive -VM $vm)
        $target = @($targets | Where-Object Id -EQ $vm.Id)
        if ($target.Count -eq 0) {
            if (@($drives | Where-Object { $_.Path -iin @($SourceDiskPath, $QueryDiskPath) }).Count) {
                throw 'A foreign VM references a recorded disk.'
            }
            continue
        }
        $role = $target[0].Role
        if ($owned.ContainsKey($vm.Id) -or $vm.Name -cne "$prefix-$role" -or
            $vm.Notes -cne "SQLPERF.ExternalTables/$RunToken/$role" -or
            $drives.Count -ne 1 -or $drives[0].Path -ine $target[0].DiskPath) {
            throw 'Recorded VM identity or disk attachment differs from live metadata.'
        }
        $owned[$vm.Id] = $vm
    }
    return @{ Guests = $owned; Switch = $switch }
}

try {
    foreach ($target in $targets) {
        if (-not [IO.Path]::IsPathFullyQualified($target.DiskPath) -or $target.DiskPath -match '^[\\/]{2}' -or
            [IO.Path]::GetFullPath($target.DiskPath) -cne $target.DiskPath -or
            [IO.Path]::GetExtension($target.DiskPath) -ine '.vhdx') {
            throw 'Expected an exact local VHDX path.'
        }
    }
    $runDirectory = [IO.Path]::GetDirectoryName($SourceDiskPath)
    if ($SourceDiskPath -ieq $QueryDiskPath -or $runDirectory -ine [IO.Path]::GetDirectoryName($QueryDiskPath) -or
        $runDirectory -ieq [IO.Path]::GetPathRoot($SourceDiskPath)) {
        throw 'Expected two files in the recorded private directory.'
    }
    for ($directory = [IO.DirectoryInfo]::new($runDirectory); $null -ne $directory; $directory = $directory.Parent) {
        $attributes = [IO.File]::GetAttributes($directory.FullName)
        if (-not ($attributes -band [IO.FileAttributes]::Directory) -or
            ($attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Expected a physical run directory.'
        }
    }
    $inventory = Read-OwnedInventory
    foreach ($target in $targets) {
        $disk = Read-OwnedDisk $target
        if (($null -eq $disk -and $inventory.Guests.ContainsKey($target.Id)) -or
            ($null -ne $disk -and $disk.Attached -and -not $inventory.Guests.ContainsKey($target.Id))) {
            throw 'Recorded disk availability differs from the owned guest inventory.'
        }
    }
    if ($ApplyOwnedRun) {
        foreach ($target in $targets) {
            $current = Read-OwnedInventory
            $vm = $current.Guests[$target.Id]
            if ($null -ne $vm) {
                if ([string]$vm.State -cne 'Off') { Stop-VM -VM $vm -TurnOff -Confirm:$false }
                $off = (Read-OwnedInventory).Guests[$target.Id]
                if ($null -eq $off -or [string]$off.State -cne 'Off') { throw 'VM stop was not confirmed.' }
                Remove-VM -VM $off -Confirm:$false
            }
        }
        foreach ($target in $targets) {
            if ((Read-OwnedInventory).Guests.Count -ne 0) { throw 'A recorded VM is still present.' }
            $disk = Read-OwnedDisk $target
            if ($null -ne $disk) {
                if ($disk.Attached) { throw 'A recorded disk is still attached.' }
                [IO.File]::Delete($target.DiskPath)
            }
        }
        $remaining = Read-OwnedInventory
        if ($remaining.Guests.Count -ne 0) { throw 'A recorded VM is still present.' }
        if ($remaining.Switch.Count -eq 1) { Remove-VMSwitch -VMSwitch $remaining.Switch[0] -Confirm:$false }
    }
} catch {
    throw 'External Tables could not verify or remove the recorded Hyper-V resources.'
}

[ordered]@{ status = if ($ApplyOwnedRun) { 'REMOVED' } else { 'VERIFIED' } } | ConvertTo-Json -Compress
