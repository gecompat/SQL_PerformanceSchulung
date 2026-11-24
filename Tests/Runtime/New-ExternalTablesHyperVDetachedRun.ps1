[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidatePattern('\A[A-Z0-9]{8}\z')] [string] $RunToken,
    [Parameter(Mandatory)] [string] $RunDirectory,
    [Parameter(Mandatory)] [string] $SourceTemplate,
    [Parameter(Mandatory)] [ValidatePattern('\A[0-9a-fA-F]{64}\z')] [string] $SourceSha256,
    [Parameter(Mandatory)] [string] $QueryTemplate,
    [Parameter(Mandatory)] [ValidatePattern('\A[0-9a-fA-F]{64}\z')] [string] $QuerySha256,
    [switch] $ApplyOwnedRun
)

$ErrorActionPreference = 'Stop'
$prefix = "SQLPerfExt-$RunToken"
$roles = @(
    @{ Role = 'SOURCE'; Template = $SourceTemplate; Digest = $SourceSha256; Leaf = 'source.vhdx' }
    @{ Role = 'QUERY'; Template = $QueryTemplate; Digest = $QuerySha256; Leaf = 'query.vhdx' }
)

function Assert-LocalPath([string] $Path) {
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or $Path -match '^[\\/]{2}' -or
        [IO.Path]::GetFullPath($Path) -cne $Path) {
        throw 'Expected a canonical local path.'
    }
}

function Assert-PhysicalDirectory([string] $Path) {
    Assert-LocalPath $Path
    for ($directory = [IO.DirectoryInfo]::new($Path); $null -ne $directory; $directory = $directory.Parent) {
        $attributes = [IO.File]::GetAttributes($directory.FullName)
        if (-not ($attributes -band [IO.FileAttributes]::Directory) -or
            ($attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Expected a physical directory.'
        }
    }
}

function Read-IndependentDisk([string] $Path) {
    Assert-LocalPath $Path
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.Attributes -band ([IO.FileAttributes]::Directory -bor [IO.FileAttributes]::ReparsePoint) -or
        [IO.Path]::GetExtension($Path) -ine '.vhdx') {
        throw 'Unexpected VHDX file.'
    }
    $vhd = @(Get-VHD -Path $Path)
    $id = [guid]::Empty
    if ($vhd.Count -ne 1 -or $vhd[0].Path -ine $Path -or [string]$vhd[0].VhdFormat -cne 'VHDX' -or
        $null -eq $vhd[0].PSObject.Properties['ParentPath'] -or $vhd[0].ParentPath -or
        $vhd[0].Attached -isnot [bool] -or $vhd[0].Attached -or
        $vhd[0].Size -isnot [ulong] -or $vhd[0].Size -eq 0 -or $vhd[0].Size -gt 24GB -or
        -not [guid]::TryParse([string]$vhd[0].DiskIdentifier, [ref]$id) -or $id -eq [guid]::Empty) {
        throw 'Unexpected detached VHDX metadata.'
    }
    $id
}

function Publish-RunRecord([string] $FileName, $Record) {
    $path = Join-Path $RunDirectory $FileName
    $temporary = Join-Path $RunDirectory ('.prepare-' + [guid]::NewGuid().ToString('N'))
    $bytes = [Text.Encoding]::UTF8.GetBytes(($Record | ConvertTo-Json -Compress))
    try {
        $stream = [IO.File]::Open($temporary, 'CreateNew', 'Write', 'None')
        try { $stream.Write($bytes); $stream.Flush($true) } finally { $stream.Dispose() }
        [IO.File]::Move($temporary, $path)
    } finally {
        [IO.File]::Delete($temporary)
    }
}

function Assert-NameAvailable([string] $Name, $Inventory) {
    if (@($Inventory | Where-Object Name -IEQ $Name).Count) {
        throw 'A recorded provision name is already in use.'
    }
}

try {
    if ($RunToken -cnotmatch '\A[A-Z0-9]{8}\z') { throw 'Unexpected run marker.' }
    Assert-PhysicalDirectory $RunDirectory
    if ($RunDirectory -ieq [IO.Path]::GetPathRoot($RunDirectory) -or
        @(Get-ChildItem -LiteralPath $RunDirectory -Force).Count -ne 0) {
        throw 'Expected a fresh private run directory.'
    }
    foreach ($target in $roles) {
        Assert-LocalPath $target.Template
        Assert-PhysicalDirectory ([IO.Path]::GetDirectoryName($target.Template))
        $target.TemplateId = Read-IndependentDisk $target.Template
        if ((Get-FileHash -LiteralPath $target.Template -Algorithm SHA256).Hash -ine $target.Digest) {
            throw 'Template digest differs from its approved value.'
        }
        Assert-NameAvailable "$prefix-$($target.Role)" @(Get-VM)
    }
    Assert-NameAvailable $prefix @(Get-VMSwitch)
    if (-not $ApplyOwnedRun) {
        '{"status":"VERIFIED"}'
        return
    }
    Publish-RunRecord 'external-tables-provision-intent.json' ([ordered]@{
        version = 1; run = $RunToken; switch = $prefix; vms = @("$prefix-SOURCE", "$prefix-QUERY")
        disks = @('source.vhdx', 'query.vhdx')
    })
    foreach ($target in $roles) {
        $role = $target.Role
        $destination = Join-Path $RunDirectory $target.Leaf
        [IO.File]::Copy($target.Template, $destination, $false)
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ine $target.Digest) {
            throw 'Template copy differs from its approved value.'
        }
        Set-VHD -Path $destination -ResetDiskIdentifier -Confirm:$false
        $diskId = Read-IndependentDisk $destination
        if ($diskId -eq $target.TemplateId) { throw 'The copy still has its template disk identifier.' }
        $target.DiskId = $diskId
        Publish-RunRecord "external-tables-disk-$role.json" ([ordered]@{ role=$role; file=$target.Leaf; id="$diskId" })
        $vmName = "$prefix-$role"
        Assert-NameAvailable $vmName @(Get-VM)
        $vm = New-VM -Name $vmName -Generation 2 -Path $RunDirectory -MemoryStartupBytes 4GB -VHDPath $destination -BootDevice VHD
        if ($vm.Id -isnot [guid] -or $vm.Id -eq [guid]::Empty -or $vm.Name -cne $vmName) {
            throw 'Hyper-V did not confirm the created VM identity.'
        }
        $target.VmId = $vm.Id
        Publish-RunRecord "external-tables-vm-$role.json" ([ordered]@{ role=$role; name=$vmName; id="$($vm.Id)" })
        $vmOptions = @{
            VM = $vm; Notes = "SQLPERF.ExternalTables/$RunToken/$role"; StaticMemory = $true
            AutomaticCheckpointsEnabled = $false; CheckpointType = 'Disabled'
            AutomaticStartAction = 'Nothing'; AutomaticStopAction = 'TurnOff'
        }
        Set-VM @vmOptions
        Set-VMProcessor -VM $vm -Count 2
        Set-VMFirmware -VM $vm -EnableSecureBoot On -SecureBootTemplate MicrosoftUEFICertificateAuthority
        $adapters = @(Get-VMNetworkAdapter -VM $vm)
        foreach ($adapter in $adapters) {
            if ($adapter.VMId -ne $vm.Id -or $null -eq $adapter.PSObject.Properties['SwitchId'] -or
                $adapter.SwitchId -notin @($null, [guid]::Empty)) {
                throw 'The new VM has an unexpected network adapter.'
            }
        }
        if ($adapters.Count) { Remove-VMNetworkAdapter -VMNetworkAdapter $adapters -Confirm:$false }
        $current = @(Get-VM -Id $vm.Id)
        $adapters = @(Get-VMNetworkAdapter -VM $vm)
        $drives = @(Get-VMHardDiskDrive -VM $vm)
        if ($current.Count -ne 1 -or $current[0].Id -ne $vm.Id -or
            [string]$current[0].State -cne 'Off' -or $current[0].Notes -cne "SQLPERF.ExternalTables/$RunToken/$role" -or
            $current[0].ProcessorCount -ne 2 -or $current[0].MemoryStartup -ne 4GB -or
            $current[0].DynamicMemoryEnabled -isnot [bool] -or $current[0].DynamicMemoryEnabled -or
            $drives.Count -ne 1 -or $drives[0].Path -ine $destination -or
            $adapters.Count -ne 0) {
            throw 'Hyper-V did not confirm the detached VM profile.'
        }
    }
    if ($roles[0].DiskId -eq $roles[1].DiskId) { throw 'Expected distinct copied disk identifiers.' }
    Assert-NameAvailable $prefix @(Get-VMSwitch)
    $switch = New-VMSwitch -Name $prefix -SwitchType Private
    if ($switch.Id -isnot [guid] -or $switch.Id -eq [guid]::Empty -or $switch.Name -cne $prefix -or
        [string]$switch.SwitchType -cne 'Private') {
        throw 'Hyper-V did not confirm the private switch identity.'
    }
    Publish-RunRecord 'external-tables-switch.json' ([ordered]@{ name=$prefix; id="$($switch.Id)" })
    if (@(Get-VMNetworkAdapter -All | Where-Object SwitchId -EQ $switch.Id).Count) {
        throw 'The prepared private switch already has an attachment.'
    }
    Publish-RunRecord 'external-tables-detached.json' ([ordered]@{
        run=$RunToken; source_vm="$($roles[0].VmId)"; query_vm="$($roles[1].VmId)"; switch="$($switch.Id)"
        source_disk_id="$($roles[0].DiskId)"; query_disk_id="$($roles[1].DiskId)"
    })
    '{"status":"DETACHED"}'
} catch {
    throw 'External Tables could not verify or prepare the detached Hyper-V resources.'
}
