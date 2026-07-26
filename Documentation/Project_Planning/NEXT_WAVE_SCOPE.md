# Verarbeitungswelle – ADV-003 und TST-002

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Ausgangsstand | `main` nach Abschluss der ersten Prioritätswelle |
| Arbeitspakete | `ADV-003`, `TST-002` |
| Abnahme-PR | `#17` |

## Umfang

Diese Welle überführt die freigegebenen Vertiefungsclaims in beobachtbare Lernziele und geplante Traceability-Zeilen. Zusätzlich implementiert sie eine SQL-Server-unabhängige Privacy- und Metadatenprüfung für Textdateien, Office-Pakete, Archive und eigenständige Medien.

Nicht Bestandteil sind Änderungen am PowerPoint-Masterdeck, die Migration historischer SQL-Beispiele sowie neue Runtime-Demos. `PRS-012`, `W2-002` und die Query-Store-/XE-Pilotvalidierung bleiben getrennte Folgepakete.

## Abnahme

- `ADV-003` erweitert M02, M03, M06 und M07 um neun beobachtbare Vertiefungslernziele, ohne den Kernpfad zu verändern.
- Alle 39 `ADV-CLM-*`-Claims besitzen genau eine curriculare Zuordnung und ein Testprofil.
- Der aktive Bestand bleibt bei 84 Folien und 84 `KEEP`-Claims.
- `TST-002` meldet nur Pfad, Kategorie und Fundanzahl, niemals gefundene Schutzwerte.
- Office-Metadaten, externe Beziehungen, Makros/OLE/ActiveX, Archive und Medien-Gates werden erfasst.
- Der Scanner besitzt synthetische Selbsttests und einen begrenzten GitHub-Actions-Workflow.
- Der vollständige Repositoryscan sowie bestehende Framework-, Präsentations- und Klassifikationsprüfungen sind erfolgreich.
- Keine PowerPoint- oder SQL-Datei wurde in dieser Welle geändert.

## Folgearbeit

Die nächsten unabhängigen Stränge sind `ADV-004`/`ADV-005`, `PRS-012`/`TST-011`, fachlich geschnittene `W2-002`-Teilpakete und die Query-Store-/XE-Pilotvalidierung.
