$ErrorActionPreference = 'Stop'
$verify = Join-Path $PSScriptRoot '../Runtime/Test-ExternalTablesHyperVAbsence.ps1'
$directory = [IO.Directory]::CreateTempSubdirectory('sqlperf-external-absence-')
$paths = @(
    (Join-Path $directory.FullName 'source.vhdx'),
    (Join-Path $directory.FullName 'query.vhdx')
)
$arguments = @{
    SourceVmId = [guid]::NewGuid()
    QueryVmId = [guid]::NewGuid()
    SwitchId = [guid]::NewGuid()
    SourceDiskPath = $paths[0]
    QueryDiskPath = $paths[1]
}
$unrelated = [pscustomobject]@{ Id = [guid]::NewGuid() }
$vmInventory = $switchInventory = @($unrelated)
$failVmLookup = $failSwitchLookup = $false

function Get-VM {
    [CmdletBinding()]
    param()
    if ($failVmLookup) { throw 'Private inventory error' }
    $vmInventory
}

function Get-VMSwitch {
    [CmdletBinding()]
    param()
    if ($failSwitchLookup) { throw 'Private inventory error' }
    $switchInventory
}

function Confirm-Rejected([string] $Expected) {
    try {
        $null = & $verify @arguments
    } catch {
        if ($_.Exception.Message -ceq $Expected) { return }
        throw
    }
    throw "Unexpected success for condition '$Expected'."
}

try {
    $result = & $verify @arguments | ConvertFrom-Json
    if ($result.status -cne 'PASS' -or $result.guest_count -ne 0 -or
        $result.switch_count -ne 0 -or $result.disk_count -ne 0) {
        throw 'The probe did not confirm absence with unrelated resources present.'
    }

    foreach ($id in @($arguments.SourceVmId, $arguments.QueryVmId)) {
        $vmInventory = @($unrelated, [pscustomobject]@{ Id = $id })
        Confirm-Rejected 'External Tables still has a recorded VM, switch, or disk copy.'
    }
    $vmInventory = @($unrelated)
    $switchInventory = @($unrelated, [pscustomobject]@{ Id = $arguments.SwitchId })
    Confirm-Rejected 'External Tables still has a recorded VM, switch, or disk copy.'
    $switchInventory = @($unrelated)

    foreach ($path in $paths) {
        [IO.File]::WriteAllBytes($path, [byte[]]::new(0))
        Confirm-Rejected 'External Tables still has a recorded VM, switch, or disk copy.'
        [IO.File]::Delete($path)
    }

    $failVmLookup = $true
    Confirm-Rejected 'External Tables could not read the local Hyper-V inventory.'
    $failVmLookup = $false
    $failSwitchLookup = $true
    Confirm-Rejected 'External Tables could not read the local Hyper-V inventory.'
    $failSwitchLookup = $false
    $switchInventory = @([pscustomobject]@{ Id = 'untyped inventory item' })
    Confirm-Rejected 'External Tables could not read the local Hyper-V inventory.'
    $switchInventory = @($unrelated)

    $arguments.QueryDiskPath = $arguments.SourceDiskPath
    Confirm-Rejected 'External Tables could not read the recorded disk directory.'
    $arguments.QueryDiskPath = $paths[1]
    $sourceId = $arguments.SourceVmId
    $arguments.SourceVmId = $arguments.QueryVmId
    Confirm-Rejected 'External Tables requires distinct recorded VM and switch IDs.'
    $arguments.SourceVmId = $sourceId

    [IO.Directory]::Delete($directory.FullName)
    Confirm-Rejected 'External Tables could not read the recorded disk directory.'
} finally {
    if ([IO.Directory]::Exists($directory.FullName)) {
        foreach ($path in $paths) { [IO.File]::Delete($path) }
        [IO.Directory]::Delete($directory.FullName)
    }
}
'External Tables Hyper-V absence tests passed.'
