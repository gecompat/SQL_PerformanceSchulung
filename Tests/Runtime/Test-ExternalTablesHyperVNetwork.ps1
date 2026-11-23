[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [guid] $SourceVmId,

    [Parameter(Mandatory)]
    [guid] $QueryVmId,

    [Parameter(Mandatory)]
    [guid] $SwitchId
)

$ErrorActionPreference = 'Stop'
if ([guid]::Empty -in @($SourceVmId, $QueryVmId, $SwitchId) -or $SourceVmId -eq $QueryVmId) {
    throw 'External Tables requires two distinct recorded VM IDs and one switch ID.'
}

try {
    $switches = @(Get-VMSwitch -Id $SwitchId -ErrorAction Stop)
    $adapters = @(Get-VMNetworkAdapter -All -ErrorAction Stop)
} catch {
    throw 'External Tables could not read the local Hyper-V network inventory.'
}

if ($switches.Count -ne 1 -or $switches[0].Id -ne $SwitchId -or [string]$switches[0].SwitchType -cne 'Private') {
    throw 'External Tables requires the recorded private Hyper-V switch.'
}

$guestIds = @($SourceVmId, $QueryVmId)
$pilotAdapters = @()
foreach ($adapter in $adapters) {
    if ($null -eq $adapter -or $null -eq $adapter.PSObject.Properties['SwitchId'] -or
        $null -eq $adapter.PSObject.Properties['VMId'] -or $adapter.IsManagementOs -isnot [bool] -or
        ($null -ne $adapter.SwitchId -and $adapter.SwitchId -isnot [guid]) -or
        ($null -ne $adapter.VMId -and $adapter.VMId -isnot [guid])) {
        throw 'External Tables received an unrecognized Hyper-V adapter record.'
    }
    $onPilotSwitch = $adapter.SwitchId -eq $SwitchId
    $pilotGuest = $adapter.VMId -in $guestIds
    if ($onPilotSwitch -and ($adapter.IsManagementOs -or -not $pilotGuest)) {
        throw 'External Tables found a foreign or management adapter on the pilot switch.'
    }
    if ($pilotGuest) {
        if (-not $onPilotSwitch -or $adapter.IsManagementOs) {
            throw 'External Tables found a pilot guest adapter outside the private switch.'
        }
        $pilotAdapters += $adapter.VMId
    }
}

if ($pilotAdapters.Count -ne 2 -or $SourceVmId -notin $pilotAdapters -or $QueryVmId -notin $pilotAdapters) {
    throw 'External Tables requires exactly one attached adapter per pilot guest.'
}

[ordered]@{
    status = 'PASS'
    switch_type = 'Private'
    attached_guest_count = $pilotAdapters.Count
} | ConvertTo-Json -Compress
