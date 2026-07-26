# Präsentationsvarianten

Dieses Verzeichnis enthält die maschinenlesbaren Verträge und später erzeugten Artefakte für die Profile `BASIS`, `STANDARD` und `VERTIEFUNG`.

## Kanonische Regeln

- Das PowerPoint-Masterdeck unter `Presentations/` ist die einzige fachlich bearbeitete Präsentationsquelle.
- [`presentation_variants.schema.json`](presentation_variants.schema.json) definiert den Vertrag für das spätere Manifest `presentation_variants.json`.
- Das konkrete Manifest wird in `PRS-012` zusammen mit stabilen SlideKeys und den drei PowerPoint Custom Shows erstellt.
- Der Unterordner `build/` ist für reproduzierbar erzeugte Varianten vorgesehen. Dateien dort sind Build- beziehungsweise Releaseartefakte und dürfen nicht manuell gepflegt werden.
- Die vollständigen fachlichen und technischen Regeln stehen in [`PRESENTATION_VARIANT_MANIFEST_CONTRACT.md`](../../Documentation/Standards/PRESENTATION_VARIANT_MANIFEST_CONTRACT.md).

Zum Stand von `PRS-011` existiert bewusst noch kein produktives Manifest, da die bestehenden Folien erst in `PRS-012` stabile SlideKeys erhalten. Ein vorzeitig angelegtes Manifest würde Foliennummern fälschlich als stabile Identität behandeln.
