# W-PRS-001 – Lehrmittelfreigabe

| Merkmal | Wert |
|---|---|
| Welle | `W-PRS-001` |
| Arbeitspakete | `PRS-012`, `PRS-013`, `TST-011`, `TST-012` |
| Status | `VALIDATED` |
| Prüfdatum | 2026-09-01 |
| Masterdeck SHA-256 | `85bd14e4fc91d148889e9ebaa7128f6e1a213366f389aa6e2053f46cc0890ad3` |
| Manifest | `Presentations/variants/presentation_variants.json`, Schema-Version 1 |

## Ergebnis

Das Masterdeck enthält 102 eindeutige SlideKeys in den Speaker Notes und genau die drei vertraglich benannten Custom Shows. Das Manifest bildet die kumulativen Profile mit 41 Folien für `BASIS`, 66 Folien für `STANDARD` und 102 Folien für `VERTIEFUNG` ab. Der read-only Validator prüft Hash, Marker, Claims, Quellen, Lernziele, Demo-IDs, Rollen, Abhängigkeiten, Paarungen, interne Links sowie Custom-Show-Mitgliedschaft und -Reihenfolge.

Der interaktive PowerPoint-Desktop-Build erzeugte alle drei eigenständigen Varianten aus einer Kopie. Ausgeschlossene Folien wurden in absteigender Reihenfolge entfernt. Der Master-Hash war vor und nach dem Build identisch.

| Profil | Folien | SHA-256 der erzeugten Variante | Render |
|---|---:|---|---:|
| `BASIS` | 41 | `ebaa6c3ce170b594031a9bdffb604b147d75d2c02440a3acd53c2f2097769744` | 41 PNG |
| `STANDARD` | 66 | `dcef462891e039d77eec7262d9f3a4cf14d3d23d9a7c67a363bc88c2937c56eb` | 66 PNG |
| `VERTIEFUNG` | 102 | `86156c1da8bc15f534841fbc6810443c86b93560adbbba612b61f236eb2ffbfd` | 102 PNG |

Zusätzlich wurden alle 102 Masterfolien mit PowerPoint Desktop auf 1280 × 720 gerendert. Die 102 Master- und `VERTIEFUNG`-Renderings sind bytegleich. Die vollständige Kontaktbogenprüfung zeigte keine abgeschnittenen Inhalte, Platzhalter, Brandingabweichungen oder Reihenfolgefehler. Der Template-Fidelity-Check meldete `PASS`; der statische Varianten-, Notes-, Metadaten-, Privacy- und Branding-Check meldete ebenfalls `PASS`.

## Reproduzierbarer Bedienpfad

- Custom Shows aktualisieren: `Tools/Set-PresentationCustomShows.ps1`.
- Eigenständige Varianten erzeugen: `Tools/Build-PresentationVariants.ps1 -Profile ALL`.
- Master und Varianten rendern: `Tools/Test-PresentationVariantRenders.ps1`.
- Statischen Mastervertrag prüfen: `Tests/Static/validate_presentation_variants.py`.
- Erzeugte Varianten und Renderumfang prüfen: `Tests/Static/validate_presentation_variant_outputs.py`.

Die `.pptx`-Varianten und PNGs bleiben reproduzierbare lokale Buildartefakte und werden nicht als unabhängig gepflegte fachliche Quellen versioniert.

## Gate V4

Die für diese Welle verlangten Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy-, Branding- und Profilumfangsnachweise liegen vor. Gate V4 ist damit `VALIDATED`.
