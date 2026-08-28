[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string]$DeckPath,

    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string]$ManifestPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-IncludedSlides {
    param(
        [Parameter(Mandatory = $true)] [object]$Manifest,
        [Parameter(Mandatory = $true)] [string]$ProfileName
    )

    $profile = $Manifest.profiles.$ProfileName
    $included = foreach ($property in $Manifest.slides.PSObject.Properties) {
        $slideKey = $property.Name
        $slide = $property.Value
        $include = ($profile.include_depth -contains $slide.depth) -and
            (@($slide.roles | Where-Object { $profile.include_roles -contains $_ }).Count -gt 0) -and
            -not ($profile.exclude_slide_keys -contains $slideKey)

        foreach ($override in @($slide.profile_overrides)) {
            if ($override.profile -eq $ProfileName) {
                $include = [bool]$override.include
            }
        }

        if ($include) {
            [pscustomobject]@{ SlideKey = $slideKey; Order = [int]$slide.order }
        }
    }
    return @($included | Sort-Object Order)
}

function Get-SlideKey {
    param([Parameter(Mandatory = $true)] [object]$Slide)
    $texts = for ($shapeIndex = 1; $shapeIndex -le $Slide.NotesPage.Shapes.Count; $shapeIndex++) {
        $shape = $Slide.NotesPage.Shapes.Item($shapeIndex)
        if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
            [string]$shape.TextFrame.TextRange.Text
        }
    }
    $match = [regex]::Match(($texts -join "`n"), '\[SLIDE-ID: (SLD-M0[0-7]-[0-9]{3})\]')
    if (-not $match.Success) { throw "Folie $($Slide.SlideIndex) besitzt keinen SlideKey." }
    return $match.Groups[1].Value
}

$resolvedDeck = (Resolve-Path -LiteralPath $DeckPath).Path
$resolvedManifest = (Resolve-Path -LiteralPath $ManifestPath).Path
$manifest = Get-Content -LiteralPath $resolvedManifest -Raw -Encoding UTF8 | ConvertFrom-Json

$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $presentation = $powerPoint.Presentations.Open($resolvedDeck, 0, 0, -1)

    if ($presentation.Slides.Count -ne @($manifest.slides.PSObject.Properties).Count) {
        throw "Folienzahl stimmt nicht mit dem Manifest ueberein."
    }

    $expectedByOrder = @($manifest.slides.PSObject.Properties |
        ForEach-Object { [pscustomobject]@{ SlideKey = $_.Name; Order = [int]$_.Value.order } } |
        Sort-Object Order)
    foreach ($expected in $expectedByOrder) {
        $current = $null
        for ($slideIndex = 1; $slideIndex -le $presentation.Slides.Count; $slideIndex++) {
            $slide = $presentation.Slides.Item($slideIndex)
            if ((Get-SlideKey -Slide $slide) -eq $expected.SlideKey) { $current = $slide; break }
        }
        if ($null -eq $current) { throw "SlideKey fehlt im Deck: $($expected.SlideKey)" }
        if ($current.SlideIndex -ne $expected.Order) { $current.MoveTo($expected.Order) }
    }

    $expectedNames = @('BASIS', 'STANDARD', 'VERTIEFUNG') |
        ForEach-Object { [string]$manifest.profiles.$_.custom_show }
    $namedShows = $presentation.SlideShowSettings.NamedSlideShows

    for ($index = $namedShows.Count; $index -ge 1; $index--) {
        $existing = $namedShows.Item($index)
        if ($expectedNames -contains [string]$existing.Name) {
            $existing.Delete()
        }
    }

    $result = foreach ($profileName in @('BASIS', 'STANDARD', 'VERTIEFUNG')) {
        $selection = Get-IncludedSlides -Manifest $manifest -ProfileName $profileName
        if ($selection.Count -eq 0) {
            throw "Profil $profileName enthaelt keine Folien."
        }
        [int[]]$slideIds = foreach ($entry in $selection) {
            [int]$presentation.Slides.Item($entry.Order).SlideID
        }
        $showName = [string]$manifest.profiles.$profileName.custom_show
        $namedShows.Add($showName, $slideIds) | Out-Null
        [pscustomobject]@{ Profile = $profileName; CustomShow = $showName; Slides = $slideIds.Count }
    }

    $presentation.Save()
    $result | Format-Table -AutoSize
}
finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)
    }
    if ($null -ne $powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
