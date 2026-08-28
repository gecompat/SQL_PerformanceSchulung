# Präsentationsprofile verwenden und erzeugen

## Custom Show direkt im Masterdeck starten

1. Das kanonische Masterdeck unter `Presentations/` in PowerPoint Desktop öffnen.
2. Unter **Bildschirmpräsentation → Benutzerdefinierte Bildschirmpräsentation** eine der drei Shows wählen:
   - `SQL Performance – Basis`
   - `SQL Performance – Standard`
   - `SQL Performance – Vertiefung`
3. Die Show starten. Das Masterdeck bleibt mit allen 102 Folien vollständig verfügbar.

Die Show-Auswahl ist im schema-v1-Manifest unter `Presentations/variants/presentation_variants.json` verankert. Eine manuelle Änderung der Custom Shows ohne passende Manifeständerung ist nicht zulässig.

## Eigenständige Varianten bauen

Der Build benötigt einen interaktiven Windows-Client mit installiertem PowerPoint Desktop. Aus dem Repository-Stamm:

```powershell
./Tools/Build-PresentationVariants.ps1 -Profile ALL
```

Alternativ kann `BASIS`, `STANDARD` oder `VERTIEFUNG` einzeln gewählt werden. Der Build prüft den Master-Hash, speichert eine Kopie, entfernt ausgeschlossene Folien absteigend, bereinigt Dokumentinformationen und weist den unveränderten Master-Hash vor und nach dem Lauf nach.

Die Ausgabe liegt unter `Presentations/variants/build/`. Diese Dateien sind reproduzierbare Buildartefakte und werden nicht manuell bearbeitet.

## Render- und Abnahmeprüfung

```powershell
./Tools/Test-PresentationVariantRenders.ps1 `
  -RenderDirectory Runtime/PresentationRenders/presentation-variants
```

Danach:

```powershell
python Tests/Static/validate_presentation_variants.py
python Tests/Static/validate_presentation_variant_outputs.py `
  --render-directory Runtime/PresentationRenders/presentation-variants
python Tests/Static/validate_privacy_metadata.py Presentations/variants/build
```

Eine Variante ist nur freigegeben, wenn Folienzahl, SlideKey-Reihenfolge, Notes, Branding, Metadaten, Privacy und Renderumfang vollständig passen und das Masterdeck unverändert blieb.
