$ErrorActionPreference = 'Stop'
$verify = Join-Path $PSScriptRoot '../Runtime/Test-ExternalTablesHyperVNetwork.ps1'
$source = [guid]::NewGuid()
$query = [guid]::NewGuid()
$foreign = [guid]::NewGuid()
$pilotSwitchId = [guid]::NewGuid()
$otherSwitch = [guid]::NewGuid()

function New-Adapter([object] $VmId, [guid] $AdapterSwitch, [bool] $Management = $false) {
    [pscustomobject]@{ VMId = $VmId; SwitchId = $AdapterSwitch; IsManagementOs = $Management }
}

function Get-VMSwitch {
    [CmdletBinding()]
    param([guid] $Id)
    if ($Id -ne $pilotSwitchId) { throw 'unexpected switch selector' }
    if ($failLookup) { throw 'private device inventory must not appear in an error' }
    $fakeSwitch
}

function Get-VMNetworkAdapter {
    [CmdletBinding()]
    param([switch] $All)
    if (-not $All) { throw 'expected the complete inventory' }
    $fakeAdapters
}

function Confirm-Rejected([string] $Pattern) {
    try {
        $output = & $verify -SourceVmId $source -QueryVmId $query -SwitchId $pilotSwitchId
    } catch {
        if ($_.Exception.Message -notmatch $Pattern) { throw }
        return
    }
    throw "Unexpected success for expected condition '$Pattern': $output"
}

$failLookup = $false
$private = [pscustomobject]@{ Id = $pilotSwitchId; SwitchType = 'Private' }
$fakeSwitch = $private
$owned = @((New-Adapter $source $pilotSwitchId), (New-Adapter $query $pilotSwitchId))
$unrelated = @((New-Adapter $foreign $otherSwitch), (New-Adapter $null $otherSwitch $true))
$fakeAdapters = $owned + $unrelated
$output = & $verify -SourceVmId $source -QueryVmId $query -SwitchId $pilotSwitchId | ConvertFrom-Json
if ($output.status -cne 'PASS' -or $output.switch_type -cne 'Private' -or $output.attached_guest_count -ne 2) {
    throw 'The exact isolated switch inventory was not accepted.'
}

$fakeAdapters = $owned + @((New-Adapter $foreign $pilotSwitchId))
Confirm-Rejected 'foreign or management'
$fakeAdapters = $owned + @((New-Adapter $null $pilotSwitchId $true))
Confirm-Rejected 'foreign or management'
$fakeAdapters = $owned + @((New-Adapter $query $otherSwitch))
Confirm-Rejected 'outside the private switch'
$fakeAdapters = $owned + @((New-Adapter $query ([guid]::Empty)))
Confirm-Rejected 'outside the private switch'
$fakeAdapters = @($owned[0], $owned[0])
Confirm-Rejected 'exactly one attached adapter per pilot guest'
$fakeAdapters = $owned + @([pscustomobject]@{ VMId = $null; IsManagementOs = $true })
Confirm-Rejected 'unrecognized Hyper-V adapter record'
$fakeAdapters = $owned
$fakeSwitch = [pscustomobject]@{ Id = $pilotSwitchId; SwitchType = 'Internal' }
Confirm-Rejected 'recorded private Hyper-V switch'
$fakeSwitch = $null
Confirm-Rejected 'recorded private Hyper-V switch'
$failLookup = $true
Confirm-Rejected 'could not read the local Hyper-V network inventory'
'External Tables Hyper-V network tests passed.'
