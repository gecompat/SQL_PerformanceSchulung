# ADV-010 – Fachliche, didaktische und technische Endabnahme

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-010` |
| Status | `VALIDATED` |
| Prüfdatum | 2026-09-01 |
| Zielplattformen | SQL Server 2019, 2022 und 2025 |
| Masterdeck | 102 Folien; SHA-256 `85bd14e4fc91d148889e9ebaa7128f6e1a213366f389aa6e2053f46cc0890ad3` |
| Tiefenprofile | `BASIS` 41, `STANDARD` 66, `VERTIEFUNG` 102 |

## Abnahmeergebnis

Der implementierte Vertiefungsstrang ist fachlich, didaktisch und technisch abgenommen. Die Abnahme erweitert keine Runtimefreigabe auf noch nicht implementierte Demos: verbleibende Claims und Designs behalten ihren dokumentierten Planungsstatus und werden als Folgearbeit behandelt.

| Achse | Nachweis | Ergebnis |
|---|---|---|
| Quellen und Claims | `ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md`, `TRACEABILITY_MATRIX.md`, `validate_adv_003_curriculum.py` | Quellenklasse, Lernziel und Versionsgrenze bleiben je Claim nachvollziehbar. |
| Runtime | Reviews und zweifache 2019/2022/2025-Matrizen für `OPT-015`, `OPT-016`, `QRY-013`, `QRY-004`, `OPT-009`, `OPT-010` und `OPT-017` | Zielmatrix erfüllt; Featuregrenzen liefern kontrollierte Skips, empirische Streuung bleibt als Warnung sichtbar. |
| Deck und Notes | `validate_adv009_deck_integration.py`, `validate_adv010_deck_integration.py`, `validate_adv011_deck_integration.py`, `validate_w2_007_presentation.py` | 102 Folien, stabile SlideKeys, Quellen- und Demo-Bezüge sowie synchronisierte Sprechernotizen. |
| Didaktischer Pfad | vollständiger PowerPoint-Render, Einzelprüfung aller Folien, Kontaktbogen und drei Custom Shows | Kernpfad bleibt kompakt; Standard- und Vertiefungsprofile bauen kumulativ darauf auf. |
| Technik und Privacy | Template-Fidelity, Überlaufprüfung, `validate_presentation_variants.py`, `validate_presentation_variant_outputs.py`, `validate_privacy_metadata.py` | Layout, Varianten, Hashbindung, Metadaten und Mastererhalt sind prüfbar. |

## Fachliche Grenzen

- `WARN_EMPIRICAL_VARIANCE` in `QRY-004` ist ein gültiger empirischer Befund und keine fehlgeschlagene Produktgarantie.
- `OPT-009` und `OPT-010` bleiben an Engine-Version, Compatibility Level, Konfiguration und Eligibility gebunden.
- `OPT-017` belegt Parallelität und Thread-/Operator-Evidenz in einem begrenzten gelben Profil; daraus folgt keine universelle DOP-Empfehlung.
- `RES-003` bleibt ein roter, getrennt freizugebender Folgeschnitt. `DGN-007` und weitere noch nicht implementierte Designs erhalten durch diese Abnahme keinen Runtime-Status.

## Didaktische Übergänge

Die Varianten bilden eine belastbare Progression: `BASIS` vermittelt Messscope und Kernbegriffe, `STANDARD` ergänzt Diagnose- und Abwägungswissen, `VERTIEFUNG` führt in Clientkontext, sichere Parametrisierung, PSP/OPPO und fortgeschrittene Planevidenz. Der Schluss bleibt auf Anzeigeposition 102. Folie 51 trennt den Row-Locator jetzt ohne Linienkreuzung; die Sprechernotiz von `SLD-M03-112` stimmt mit der Runtimewarnung überein.

## Folgeplanung

Die Endabnahme schließt `ADV-010`. Noch offene Demo- und Szenariopakete werden nach Safety-, Lifecycle- und Bedarfsvertrag einzeln priorisiert. Geplante Claims dürfen erst nach eigenem Artefakt-, Quellen- und Runtime-Nachweis auf `KEEP` beziehungsweise `VALIDATED` wechseln.
