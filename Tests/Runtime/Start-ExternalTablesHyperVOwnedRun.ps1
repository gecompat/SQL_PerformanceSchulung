[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateSet('Boot', 'Attach')] [string] $Phase,
    [Parameter(Mandatory)] [ValidatePattern('\A[A-Z0-9]{8}\z')] [string] $RunToken,
    [Parameter(Mandatory)] [guid] $SourceVmId,
    [Parameter(Mandatory)] [guid] $QueryVmId,
    [Parameter(Mandatory)] [guid] $SwitchId,
    [Parameter(Mandatory)] [string] $SourceDiskPath,
    [Parameter(Mandatory)] [string] $QueryDiskPath,
    [Parameter(Mandatory)] [guid] $SourceDiskId,
    [Parameter(Mandatory)] [guid] $QueryDiskId,
    [Parameter(Mandatory)] [ValidatePattern('\A[0-9a-fA-F]{64}\z')] [string] $SourceMediaSha256,
    [Parameter(Mandatory)] [ValidatePattern('\A[0-9a-fA-F]{64}\z')] [string] $QueryMediaSha256,
    [switch] $ApplyOwnedRun
)

$ErrorActionPreference = 'Stop'
$ownership = @{
    RunToken=$RunToken; SourceVmId=$SourceVmId; QueryVmId=$QueryVmId; SwitchId=$SwitchId
    SourceDiskPath=$SourceDiskPath; QueryDiskPath=$QueryDiskPath; SourceDiskId=$SourceDiskId; QueryDiskId=$QueryDiskId
}
$ownerCheck = Join-Path $PSScriptRoot 'Remove-ExternalTablesHyperVOwnedRun.ps1'
$networkCheck = Join-Path $PSScriptRoot 'Test-ExternalTablesHyperVNetwork.ps1'
$network = @{ SourceVmId=$SourceVmId; QueryVmId=$QueryVmId; SwitchId=$SwitchId }
$ids = @($SourceVmId, $QueryVmId)
$runDir = [IO.Path]::GetDirectoryName($SourceDiskPath)
$mediaById = @{
    $SourceVmId = @{ Path=(Join-Path $runDir 'source.iso'); Digest=$SourceMediaSha256 }
    $QueryVmId = @{ Path=(Join-Path $runDir 'query.iso'); Digest=$QueryMediaSha256 }
}

function Read-OwnedGuests([string] $ExpectedState) {
    $status = & $ownerCheck @ownership | ConvertFrom-Json
    if ($status.status -cne 'VERIFIED') { throw 'Expected the recorded resource ownership.' }

    $guests = foreach ($id in $ids) {
        $vm = @(Get-VM -Id $id)
        if ($vm.Count -ne 1 -or $vm[0].Id -ne $id -or [string]$vm[0].State -cne $ExpectedState -or
            $vm[0].ProcessorCount -ne 2 -or $vm[0].MemoryStartup -ne 4GB -or
            $vm[0].DynamicMemoryEnabled -isnot [bool] -or $vm[0].DynamicMemoryEnabled) {
            throw 'Expected the recorded guest and its resource profile.'
        }
        $vm[0]
    }
    $switch = @(Get-VMSwitch -Id $SwitchId)
    if ($switch.Count -ne 1 -or $switch[0].Id -ne $SwitchId -or
        $switch[0].Name -cne "SQLPerfExt-$RunToken" -or [string]$switch[0].SwitchType -cne 'Private') {
        throw 'Expected the recorded private switch.'
    }
    foreach ($path in @($SourceDiskPath, $QueryDiskPath)) {
        $disk = @(Get-VHD -Path $path)
        if ($disk.Count -ne 1 -or $disk[0].Size -isnot [ulong] -or
            $disk[0].Size -eq 0 -or $disk[0].Size -gt 24GB) {
            throw 'Expected the recorded guest disk within its capacity limit.'
        }
    }
    return @{ Guests=$guests; Switch=$switch[0] }
}

function Read-OwnedDvd($Guest, [bool] $RequireAttached) {
    $expectedPath = $mediaById[$Guest.Id].Path
    $dvd = @(Get-VMDvdDrive -VM $Guest)
    if ($dvd.Count -gt 1 -or ($dvd.Count -eq 1 -and
        ($dvd[0].VMId -ne $Guest.Id -or ($dvd[0].Path -and $dvd[0].Path -ine $expectedPath)))) {
        throw 'The owned guest has an unexpected DVD attachment.'
    }
    if ($RequireAttached -and ($dvd.Count -ne 1 -or $dvd[0].Path -ine $expectedPath)) {
        throw 'The recorded guest ISO attachment was not confirmed.'
    }
    $dvd
}

function Test-RoleMedia {
    if ($SourceMediaSha256 -ieq $QueryMediaSha256) { throw 'Expected distinct role media hashes.' }
    foreach ($medium in $mediaById.Values) {
        $file = Get-Item -LiteralPath $medium.Path -Force
        if ($file -isnot [IO.FileInfo] -or $file.Length -eq 0 -or
            ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
            (Get-FileHash -LiteralPath $medium.Path -Algorithm SHA256).Hash -ine $medium.Digest) {
            throw 'An offline role ISO differs from its recorded digest.'
        }
    }
}

function Read-RelevantAdapters {
    Get-VMNetworkAdapter -All | Where-Object { $_.VMId -in $ids -or $_.SwitchId -eq $SwitchId }
}

try {
    $state = if ($Phase -eq 'Boot') { 'Off' } else { 'Running' }
    $current = Read-OwnedGuests $state
    $adapters = @(Read-RelevantAdapters)
    if ($adapters.Count) { throw 'Expected both guests and the private switch to have no adapters.' }
    if ($Phase -eq 'Boot') { Test-RoleMedia }
    foreach ($guest in $current.Guests) { $null = Read-OwnedDvd $guest ($Phase -eq 'Attach') }

    if (-not $ApplyOwnedRun) {
        '{"status":"VERIFIED"}'
        return
    }
    if ($Phase -eq 'Boot') {
        foreach ($guest in $current.Guests) {
            $dvd = @(Read-OwnedDvd $guest $false)
            $path = $mediaById[$guest.Id].Path
            if (-not $dvd.Count) {
                Add-VMDvdDrive -VM $guest -Path $path -Confirm:$false
            } elseif (-not $dvd[0].Path) {
                Set-VMDvdDrive -VMDvdDrive $dvd[0] -Path $path -Confirm:$false
            }
        }
        foreach ($guest in $current.Guests) { $null = Read-OwnedDvd $guest $true }
        Start-VM -VM $current.Guests -Confirm:$false
        $null = Read-OwnedGuests 'Running'
        if (@(Read-RelevantAdapters).Count) { throw 'The booted guests must remain isolated.' }
        '{"status":"BOOTED"}'
        return
    }

    $newAdapters = foreach ($guest in $current.Guests) {
        $adapter = @(Add-VMNetworkAdapter -VM $guest -Name 'SQLPerfExternal' -Passthru -Confirm:$false)
        if ($adapter.Count -ne 1 -or $adapter[0].VMId -ne $guest.Id -or
            $adapter[0].IsManagementOs -isnot [bool] -or $adapter[0].IsManagementOs -or
            $null -eq $adapter[0].PSObject.Properties['SwitchId'] -or $adapter[0].SwitchId -notin @($null, [guid]::Empty)) {
            throw 'Expected an exact disconnected adapter for the owned guest.'
        }
        $adapter[0]
    }
    $current = Read-OwnedGuests 'Running'
    $adapters = @(Read-RelevantAdapters)
    if ($adapters.Count -ne 2 -or @($adapters | Where-Object { $_.SwitchId -notin @($null, [guid]::Empty) }).Count) {
        throw 'Expected exactly two disconnected adapters before attachment.'
    }
    Connect-VMNetworkAdapter -VMNetworkAdapter $newAdapters -VMSwitch $current.Switch -Confirm:$false
    $status = & $networkCheck @network | ConvertFrom-Json
    if ($status.status -cne 'PASS') { throw 'The exact private network could not be confirmed.' }
    '{"status":"ATTACHED"}'
} catch {
    throw 'External Tables could not verify or transition the recorded Hyper-V resources.'
}
