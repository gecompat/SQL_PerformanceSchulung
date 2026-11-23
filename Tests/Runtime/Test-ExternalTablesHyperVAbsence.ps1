[CmdletBinding()]
param(
    [Parameter(Mandatory)] [guid] $SourceVmId,
    [Parameter(Mandatory)] [guid] $QueryVmId,
    [Parameter(Mandatory)] [guid] $SwitchId,
    [Parameter(Mandatory)] [string] $SourceDiskPath,
    [Parameter(Mandatory)] [string] $QueryDiskPath
)

$ErrorActionPreference = 'Stop'
$expectedIds = @($SourceVmId, $QueryVmId, $SwitchId)
if ([guid]::Empty -in $expectedIds -or @($expectedIds | Select-Object -Unique).Count -ne 3) {
    throw 'External Tables requires distinct recorded VM and switch IDs.'
}

try {
    $diskPaths = foreach ($path in @($SourceDiskPath, $QueryDiskPath)) {
        if (-not [IO.Path]::IsPathFullyQualified($path) -or $path -match '^[\\/]{2}') {
            throw 'Expected an absolute local path.'
        }
        $fullPath = [IO.Path]::GetFullPath($path)
        if ($fullPath -cne $path -or [IO.Path]::GetExtension($fullPath) -ine '.vhdx') {
            throw 'Expected a canonical VHDX path.'
        }
        $fullPath
    }
    $sourceParent = [IO.Path]::GetDirectoryName($diskPaths[0])
    $queryParent = [IO.Path]::GetDirectoryName($diskPaths[1])
    if ($diskPaths[0] -ieq $diskPaths[1] -or $sourceParent -ine $queryParent -or
        $sourceParent -ieq [IO.Path]::GetPathRoot($diskPaths[0])) {
        throw 'Expected separate disk copies in a run directory.'
    }
    # The provisioning transport keeps the owned directory until this check.
    # A missing, inaccessible, or redirected parent cannot prove disk absence.
    for ($directory = [IO.DirectoryInfo]::new($sourceParent); $null -ne $directory; $directory = $directory.Parent) {
        $attributes = [IO.File]::GetAttributes($directory.FullName)
        if (-not ($attributes -band [IO.FileAttributes]::Directory) -or
            ($attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Expected a physical local directory.'
        }
    }
    $diskNames = @([IO.Path]::GetFileName($diskPaths[0]), [IO.Path]::GetFileName($diskPaths[1]))
    $entries = @(Get-ChildItem -LiteralPath $sourceParent -Force -Name -ErrorAction Stop)
} catch {
    throw 'External Tables could not read the recorded disk directory.'
}

try {
    $vms = @(Get-VM -ErrorAction Stop)
    $switches = @(Get-VMSwitch -ErrorAction Stop)
    foreach ($entry in ($vms + $switches)) {
        if ($null -eq $entry -or $entry.Id -isnot [guid] -or $entry.Id -eq [guid]::Empty) {
            throw 'Unexpected Hyper-V inventory record.'
        }
    }
} catch {
    throw 'External Tables could not read the local Hyper-V inventory.'
}

if (@($vms | Where-Object Id -In @($SourceVmId, $QueryVmId)).Count -or
    @($switches | Where-Object Id -EQ $SwitchId).Count -or
    $diskNames[0] -iin $entries -or $diskNames[1] -iin $entries) {
    throw 'External Tables still has a recorded VM, switch, or disk copy.'
}

[ordered]@{ status = 'PASS'; guest_count = 0; switch_count = 0; disk_count = 0 } | ConvertTo-Json -Compress
