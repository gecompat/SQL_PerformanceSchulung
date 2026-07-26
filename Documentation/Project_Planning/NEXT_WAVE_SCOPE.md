# Verarbeitungswelle – ADV-003 und TST-002

| Merkmal | Wert |
|---|---|
| Status | `IN_PROGRESS` |
| Stand | 2026-07-26 |
| Ausgangsstand | `main` nach Abschluss der ersten Prioritätswelle |
| Arbeitspakete | `ADV-003`, `TST-002` |

## Umfang

Diese Welle überführt die freigegebenen Vertiefungsclaims in beobachtbare Lernziele und geplante Traceability-Zeilen. Zusätzlich implementiert sie eine SQL-Server-unabhängige Privacy- und Metadatenprüfung für Textdateien, Office-Pakete, Archive und eigenständige Medien.

Nicht Bestandteil sind Änderungen am PowerPoint-Masterdeck, die Migration historischer SQL-Beispiele sowie neue Runtime-Demos. `PRS-012`, `W2-002` und die Query-Store-/XE-Pilotvalidierung bleiben getrennte Folgepakete.

## Abnahme

- `ADV-003` erweitert M02, M03, M06 und M07, ohne den Kernpfad zu verändern.
- Alle 39 `ADV-CLM-*`-Claims besitzen eine curriculare Zuordnung und ein Testprofil.
- `TST-002` meldet nur Kategorien und Fundanzahlen, niemals gefundene Schutzwerte.
- Office-Metadaten, externe Beziehungen, Makros/OLE/ActiveX, Archive und Medien werden erfasst.
- Der Scanner besitzt synthetische Selbsttests und einen begrenzten GitHub-Actions-Workflow.
- Keine PowerPoint- oder SQL-Datei wird in dieser Welle geändert.
