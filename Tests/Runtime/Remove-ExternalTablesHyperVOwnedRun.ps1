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
    [switch] $PartialProvision,
    [switch] $ApplyOwnedRun,
    [switch] $PassThruVerifiedInventory
)

$ErrorActionPreference = 'Stop'
if ($PassThruVerifiedInventory -and ($PartialProvision -or $ApplyOwnedRun)) {
    throw 'The verified inventory is available for read-only checks of a complete run.'
}
$resourceIds = @($SourceVmId, $QueryVmId, $SwitchId, $SourceDiskId, $QueryDiskId)
if ($PartialProvision) { $resourceIds = @($resourceIds | Where-Object { $_ -ne [guid]::Empty }) }
if ($RunToken -cnotmatch '\A[A-Z0-9]{8}\z' -or [guid]::Empty -in $resourceIds -or
    @($resourceIds | Select-Object -Unique).Count -ne $resourceIds.Count -or
    ($PartialProvision -and (($SourceVmId -ne [guid]::Empty -and $SourceDiskId -eq [guid]::Empty) -or
                            ($QueryVmId -ne [guid]::Empty -and $QueryDiskId -eq [guid]::Empty)))) {
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
    if ($Target.DiskId -eq [guid]::Empty) { throw 'The expected disk path has no recorded disk identity.' }
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
    if ($PartialProvision -and @($switches | Where-Object { $_.Name -ieq $prefix -and $_.Id -ne $SwitchId }).Count) {
        throw 'The expected switch name has no matching creation receipt.'
    }
    $switch = @($switches | Where-Object Id -EQ $SwitchId)
    if ($switch.Count -gt 1 -or ($switch.Count -eq 1 -and
        ($switch[0].Name -cne $prefix -or [string]$switch[0].SwitchType -cne 'Private'))) {
        throw 'Recorded switch identity differs from live metadata.'
    }
    $guestIds = @(@($SourceVmId, $QueryVmId) | Where-Object { $_ -ne [guid]::Empty })
    $guests = @($vms | Where-Object Id -In $guestIds)
    $adapters = @(
        if ($guests.Count) { Get-VMNetworkAdapter -VM $guests }
    )
    foreach ($adapter in $adapters) {
        if ($adapter.VMId -isnot [guid] -or $adapter.VMId -notin $guests.Id -or
            $adapter.IsManagementOs -isnot [bool] -or $adapter.IsManagementOs -or
            $null -eq $adapter.PSObject.Properties['SwitchId'] -or
            ($null -ne $adapter.SwitchId -and $adapter.SwitchId -isnot [guid]) -or
            $adapter.SwitchId -notin @($null, [guid]::Empty, $SwitchId)) {
            throw 'Recorded VM has an unexpected adapter or foreign switch attachment.'
        }
    }
    if ($SwitchId -ne [guid]::Empty) {
        $connected = @($adapters | Where-Object SwitchId -EQ $SwitchId).Count
        $ports = @(Get-CimInstance -Namespace root/virtualization/v2 -ClassName Msvm_EthernetPortAllocationSettingData -Property HostResource)
        $switchName = 'Name="' + $SwitchId.ToString() + '"'
        $references = @($ports | Where-Object {
            $_.HostResource -match ('(?i):Msvm_VirtualEthernetSwitch\..*\b' + [regex]::Escape($switchName))
        })
        if ($references.Count -ne $connected -or ($connected -and $switch.Count -ne 1)) {
            throw 'Recorded switch references differ from the owned guest inventory.'
        }
    }
    $owned = @{}
    foreach ($vm in $vms) {
        $target = @($targets | Where-Object Id -EQ $vm.Id)
        if ($target.Count -eq 0) {
            if ($PartialProvision -and $vm.Name -iin @("$prefix-SOURCE", "$prefix-QUERY")) {
                throw 'The expected VM name has no matching creation receipt.'
            }
            continue
        }
        $drives = @(Get-VMHardDiskDrive -VM $vm)
        $role = $target[0].Role
        if (($PartialProvision -and [string]$vm.State -cne 'Off') -or $owned.ContainsKey($vm.Id) -or $vm.Name -cne "$prefix-$role" -or
            $vm.Notes -cne "SQLPERF.ExternalTables/$RunToken/$role" -or
            $drives.Count -ne 1 -or $drives[0].Path -ine $target[0].DiskPath) {
            throw 'Recorded VM identity or disk attachment differs from live metadata.'
        }
        $owned[$vm.Id] = $vm
    }
    # Read configured VHD references in one provider query, including those of off guests.
    $references = @(Get-CimInstance -Namespace root/virtualization/v2 -ClassName Msvm_StorageAllocationSettingData `
        -Filter "ResourceSubType = 'Microsoft:Hyper-V:Virtual Hard Disk'" -Property HostResource)
    foreach ($target in $targets) {
        $expectedReferences = [int]$owned.ContainsKey($target.Id)
        $matchingReferences = @($references | Where-Object { $target.DiskPath -iin $_.HostResource })
        if ($matchingReferences.Count -ne $expectedReferences) {
            throw 'Recorded disk references differ from the owned guest inventory.'
        }
    }
    return @{ Guests = $owned; Switch = $switch; Adapters = $adapters }
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
    $verifiedDisks = @{}
    foreach ($target in $targets) {
        $disk = Read-OwnedDisk $target
        $verifiedDisks[$target.Id] = $disk
        if (($null -eq $disk -and $inventory.Guests.ContainsKey($target.Id)) -or
            ($null -ne $disk -and $disk.Attached -and -not $inventory.Guests.ContainsKey($target.Id))) {
            throw 'Recorded disk availability differs from the owned guest inventory.'
        }
    }
    if ($PassThruVerifiedInventory) {
        $inventory.Disks = $verifiedDisks
        return $inventory
    }
    if ($ApplyOwnedRun) {
        $current = Read-OwnedInventory
        foreach ($target in $targets) {
            $vm = $current.Guests[$target.Id]
            if ($null -ne $vm) {
                if ([string]$vm.State -cne 'Off') {
                    Stop-VM -VM $vm -TurnOff -Confirm:$false
                    $vm = (Read-OwnedInventory).Guests[$target.Id]
                    if ($null -eq $vm -or [string]$vm.State -cne 'Off') { throw 'VM stop was not confirmed.' }
                }
                Remove-VM -VM $vm -Confirm:$false
                $current = Read-OwnedInventory
            }
        }
        foreach ($target in $targets) {
            if ($current.Guests.Count -ne 0) { throw 'A recorded VM is still present.' }
            $disk = Read-OwnedDisk $target
            if ($null -ne $disk) {
                if ($disk.Attached) { throw 'A recorded disk is still attached.' }
                [IO.File]::Delete($target.DiskPath)
                $current = Read-OwnedInventory
            }
        }
        $remaining = $current
        if ($remaining.Guests.Count -ne 0) { throw 'A recorded VM is still present.' }
        if ($remaining.Switch.Count -eq 1) { Remove-VMSwitch -VMSwitch $remaining.Switch[0] -Confirm:$false }
        if ($PartialProvision) {
            $final = Read-OwnedInventory
            if ($final.Guests.Count -or $final.Switch.Count -or @($targets | ForEach-Object { Read-OwnedDisk $_ }).Count) {
                throw 'Partial provisioning resources are still present.'
            }
        }
    }
} catch {
    throw 'External Tables could not verify or remove the recorded Hyper-V resources.'
}

[ordered]@{ status = if ($ApplyOwnedRun) { 'REMOVED' } else { 'VERIFIED' } } | ConvertTo-Json -Compress
