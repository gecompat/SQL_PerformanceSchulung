# Präsentationsvarianten

Dieses Verzeichnis enthält die maschinenlesbaren Verträge und später erzeugten Artefakte für die Profile `BASIS`, `STANDARD` und `VERTIEFUNG`.

## Kanonische Regeln

- Das PowerPoint-Masterdeck unter `Presentations/` ist die einzige fachlich bearbeitete Präsentationsquelle.
- [`presentation_variants.schema.json`](presentation_variants.schema.json) definiert den Vertrag für das produktive Manifest [`presentation_variants.json`](presentation_variants.json).
- Das Manifest ordnet alle 102 stabilen SlideKeys den Profilen, Rollen, Claims, Quellen, Lernzielen und Demo-IDs zu.
- Der Unterordner `build/` ist für reproduzierbar erzeugte Varianten vorgesehen. Dateien dort sind Build- beziehungsweise Releaseartefakte und dürfen nicht manuell gepflegt werden.
- Die vollständigen fachlichen und technischen Regeln stehen in [`PRESENTATION_VARIANT_MANIFEST_CONTRACT.md`](../../Documentation/Standards/PRESENTATION_VARIANT_MANIFEST_CONTRACT.md).

`PRS-012` bis `TST-012` sind durch [`W_PRS_001_TEACHING_RELEASE.md`](../../Documentation/Project_Planning/W_PRS_001_TEACHING_RELEASE.md) validiert. Bedienung, Build und Renderprüfung beschreibt [`PRESENTATION_VARIANTS.md`](../../Documentation/HowTo/PRESENTATION_VARIANTS.md).
