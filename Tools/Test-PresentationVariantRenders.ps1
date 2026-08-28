[CmdletBinding()]
param(
    [string]$ManifestPath = (Join-Path $PSScriptRoot '..\Presentations\variants\presentation_variants.json'),
    [string]$BuildDirectory = (Join-Path $PSScriptRoot '..\Presentations\variants\build'),
    [string]$RenderDirectory = (Join-Path $PSScriptRoot '..\Runtime\PresentationRenders')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$manifest = Get-Content -LiteralPath (Resolve-Path -LiteralPath $ManifestPath) -Raw -Encoding UTF8 | ConvertFrom-Json
$buildPath = (Resolve-Path -LiteralPath $BuildDirectory).Path
New-Item -ItemType Directory -Path $RenderDirectory -Force | Out-Null
$renderPath = (Resolve-Path -LiteralPath $RenderDirectory).Path
$shortHash = ([string]$manifest.master_sha256).Substring(0, 8)
$powerPoint = $null
$results = @()

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    $masterPath = Join-Path $repositoryRoot ([string]$manifest.master_deck)
    $masterRenderPath = Join-Path $renderPath 'MASTER'
    New-Item -ItemType Directory -Path $masterRenderPath -Force | Out-Null
    Get-ChildItem -LiteralPath $masterRenderPath -Filter '*.PNG' -File | Remove-Item -Force
    $masterPresentation = $null
    try {
        $masterPresentation = $powerPoint.Presentations.Open($masterPath, -1, 0, -1)
        $masterPresentation.Export($masterRenderPath, 'PNG', 1280, 720)
        $masterRendered = @(Get-ChildItem -LiteralPath $masterRenderPath -Filter '*.PNG' -File)
        if ($masterRendered.Count -ne $masterPresentation.Slides.Count) { throw 'Master-Renderumfang ist inkonsistent.' }
        $results += [pscustomobject][ordered]@{
            profile = 'MASTER'
            deck_sha256 = (Get-FileHash -LiteralPath $masterPath -Algorithm SHA256).Hash.ToLowerInvariant()
            slides = $masterPresentation.Slides.Count
            rendered_png = $masterRendered.Count
            status = 'PASS'
        }
    }
    finally {
        if ($null -ne $masterPresentation) {
            $masterPresentation.Close()
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($masterPresentation)
        }
    }
    foreach ($profileName in @('BASIS', 'STANDARD', 'VERTIEFUNG')) {
        $filename = ([string]$manifest.build.filename_pattern).
            Replace('{PROFILE}', $profileName).
            Replace('{MASTER_SHORT_HASH}', $shortHash)
        $variantPath = Join-Path $buildPath $filename
        if (-not (Test-Path -LiteralPath $variantPath -PathType Leaf)) { throw "Variante fehlt: $filename" }
        $profileRenderPath = Join-Path $renderPath $profileName
        New-Item -ItemType Directory -Path $profileRenderPath -Force | Out-Null
        Get-ChildItem -LiteralPath $profileRenderPath -Filter '*.PNG' -File | Remove-Item -Force

        $presentation = $null
        try {
            $presentation = $powerPoint.Presentations.Open($variantPath, -1, 0, -1)
            $presentation.Export($profileRenderPath, 'PNG', 1280, 720)
            $rendered = @(Get-ChildItem -LiteralPath $profileRenderPath -Filter '*.PNG' -File)
            if ($rendered.Count -ne $presentation.Slides.Count) {
                throw "Renderumfang fuer $profileName ist inkonsistent."
            }
            $results += [pscustomobject][ordered]@{
                profile = $profileName
                deck_sha256 = (Get-FileHash -LiteralPath $variantPath -Algorithm SHA256).Hash.ToLowerInvariant()
                slides = $presentation.Slides.Count
                rendered_png = $rendered.Count
                status = 'PASS'
            }
        }
        finally {
            if ($null -ne $presentation) {
                $presentation.Close()
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)
            }
        }
    }
}
finally {
    if ($null -ne $powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$evidence = [ordered]@{
    schema_version = 1
    master_sha256 = [string]$manifest.master_sha256
    results = $results
}
$evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $renderPath 'presentation-render-evidence.json') -Encoding UTF8
$results | Format-Table profile, slides, rendered_png, status
