[CmdletBinding()]
param(
    [string]$MasterDeck = (Join-Path $PSScriptRoot '..\Presentations\Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx'),
    [string]$ManifestPath = (Join-Path $PSScriptRoot '..\Presentations\variants\presentation_variants.json'),
    [ValidateSet('ALL', 'BASIS', 'STANDARD', 'VERTIEFUNG')]
    [string]$Profile = 'ALL'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-IncludedSlides {
    param([object]$Manifest, [string]$ProfileName)
    $profileDefinition = $Manifest.profiles.$ProfileName
    $result = foreach ($property in $Manifest.slides.PSObject.Properties) {
        $slideKey = $property.Name
        $slide = $property.Value
        $include = ($profileDefinition.include_depth -contains $slide.depth) -and
            (@($slide.roles | Where-Object { $profileDefinition.include_roles -contains $_ }).Count -gt 0) -and
            -not ($profileDefinition.exclude_slide_keys -contains $slideKey)
        foreach ($override in @($slide.profile_overrides)) {
            if ($override.profile -eq $ProfileName) { $include = [bool]$override.include }
        }
        if ($include) { [pscustomobject]@{ SlideKey = $slideKey; Order = [int]$slide.order } }
    }
    return @($result | Sort-Object Order)
}

$masterPath = (Resolve-Path -LiteralPath $MasterDeck).Path
$manifestFile = (Resolve-Path -LiteralPath $ManifestPath).Path
$manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
$expectedHash = [string]$manifest.master_sha256
$beforeHash = (Get-FileHash -LiteralPath $masterPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($beforeHash -ne $expectedHash) { throw "Masterdeck-Hash stimmt nicht mit dem Manifest ueberein." }

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$outputDirectory = Join-Path $repositoryRoot ([string]$manifest.build.output_directory)
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
$profiles = if ($Profile -eq 'ALL') { @('BASIS', 'STANDARD', 'VERTIEFUNG') } else { @($Profile) }
$shortHash = $beforeHash.Substring(0, 8)
$powerPoint = $null
$masterPresentation = $null
$results = @()

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $masterPresentation = $powerPoint.Presentations.Open($masterPath, -1, 0, -1)

    foreach ($profileName in $profiles) {
        $included = Get-IncludedSlides -Manifest $manifest -ProfileName $profileName
        $includedOrders = [Collections.Generic.HashSet[int]]::new()
        foreach ($entry in $included) { [void]$includedOrders.Add($entry.Order) }
        $filename = ([string]$manifest.build.filename_pattern).
            Replace('{PROFILE}', $profileName).
            Replace('{MASTER_SHORT_HASH}', $shortHash)
        $outputPath = Join-Path $outputDirectory $filename
        $partialPath = "$outputPath.partial.pptx"
        if (Test-Path -LiteralPath $partialPath) { Remove-Item -LiteralPath $partialPath -Force }

        $variant = $null
        try {
            $masterPresentation.SaveCopyAs($partialPath, 24)
            $variant = $powerPoint.Presentations.Open($partialPath, 0, 0, -1)
            for ($position = $variant.Slides.Count; $position -ge 1; $position--) {
                if (-not $includedOrders.Contains($position)) { $variant.Slides.Item($position).Delete() }
            }
            if ($variant.Slides.Count -ne $included.Count) { throw "Folienzahl fuer $profileName ist inkonsistent." }
            $variant.RemoveDocumentInformation(99)
            $variant.Save()
            $variant.Close()
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($variant)
            $variant = $null
            Move-Item -LiteralPath $partialPath -Destination $outputPath -Force

            $results += [pscustomobject][ordered]@{
                profile = $profileName
                master_sha256 = $beforeHash
                output = $filename
                output_sha256 = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
                slides = $included.Count
                status = 'PASS'
            }
        }
        catch {
            if ($null -ne $variant) {
                $variant.Close()
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($variant)
            }
            if (Test-Path -LiteralPath $partialPath) { Remove-Item -LiteralPath $partialPath -Force }
            throw
        }
    }
}
finally {
    if ($null -ne $masterPresentation) {
        $masterPresentation.Close()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($masterPresentation)
    }
    if ($null -ne $powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$afterHash = (Get-FileHash -LiteralPath $masterPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($afterHash -ne $beforeHash) { throw "Das Masterdeck wurde waehrend des Varianten-Builds veraendert." }

$log = [ordered]@{
    schema_version = 1
    master_deck = [string]$manifest.master_deck
    master_sha256_before = $beforeHash
    master_sha256_after = $afterHash
    preserve_master = ($beforeHash -eq $afterHash)
    results = $results
}
$logPath = Join-Path $outputDirectory 'presentation-variant-build.json'
$log | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $logPath -Encoding UTF8
$results | Format-Table profile, slides, status, output -AutoSize
