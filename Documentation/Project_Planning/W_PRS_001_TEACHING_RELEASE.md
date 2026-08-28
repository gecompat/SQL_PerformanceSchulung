# W-PRS-001 – Lehrmittelfreigabe

| Merkmal | Wert |
|---|---|
| Welle | `W-PRS-001` |
| Arbeitspakete | `PRS-012`, `PRS-013`, `TST-011`, `TST-012` |
| Status | `VALIDATED` |
| Prüfdatum | 2026-08-28 |
| Masterdeck SHA-256 | `86977ac815f4bd90ad56335bc3fa5847149b0b809da71a58601128b5385111f5` |
| Manifest | `Presentations/variants/presentation_variants.json`, Schema-Version 1 |

## Ergebnis

Das Masterdeck enthält 102 eindeutige SlideKeys in den Speaker Notes und genau die drei vertraglich benannten Custom Shows. Das Manifest bildet die kumulativen Profile mit 41 Folien für `BASIS`, 66 Folien für `STANDARD` und 102 Folien für `VERTIEFUNG` ab. Der read-only Validator prüft Hash, Marker, Claims, Quellen, Lernziele, Demo-IDs, Rollen, Abhängigkeiten, Paarungen, interne Links sowie Custom-Show-Mitgliedschaft und -Reihenfolge.

Der interaktive PowerPoint-Desktop-Build erzeugte alle drei eigenständigen Varianten aus einer Kopie. Ausgeschlossene Folien wurden in absteigender Reihenfolge entfernt. Der Master-Hash war vor und nach dem Build identisch.

| Profil | Folien | SHA-256 der erzeugten Variante | Render |
|---|---:|---|---:|
| `BASIS` | 41 | `651f9308ee80d9b4d0b4cc07fdd7ee0140e8784c906f33b1cf7d60b218c1055d` | 41 PNG |
| `STANDARD` | 66 | `3d0482bd4166c110b84bfa9dabf4da9eda46cd7807ab6cf7c4248c2eb504f183` | 66 PNG |
| `VERTIEFUNG` | 102 | `d498d6b51a762517cec5d63ab019931ef9e4f819e888a0fbf7d76c1a550dc39a` | 102 PNG |

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
