# Verarbeitungswelle – ADV-004 und ADV-005

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Ausgangscommit | `1849e2207c67a062cd33e91b184cdc192a784a37` |
| Pull Request | `#18` |

## Umfang

Die Welle schließt die vollständige fachliche und technische Designplanung für LAB-VP1 und LAB-VP2 ab. Sie definiert die neuen Demos `OPT-015` (Ausführungspläne systematisch lesen), `OPT-016` (Wiederholte Operatorausführung und Zwischenspeicherung), `OPT-017` (Ungleich verteilte parallele Arbeit) und `QRY-013` (Anwendung langsam, Verwaltungswerkzeug schnell) sowie die Erweiterung von `QRY-004` (Optionale Filter, Recompile und dynamisches SQL).

## Nicht enthalten

- keine ausführbaren SQL-Skripte,
- keine PowerPoint-Änderung,
- keine Query-Store-/XE-Runtimefreigabe,
- keine Umsetzung von `ADV-006` (Design LAB-VP3 und LAB-VP4), `ADV-007` (Design LAB-VP5 und DGN-007) oder `ADV-008` (Review QRY-004),
- keine Neutralisierung historischer Beispiele aus `W2-002`.

## Abnahme

Der maschinenlesbare Designvertrag, beide Detaildesigns, Backlog, Vertiefungsplan und operativer Status sind konsistent. Die Läufe `30214930385`, `30214930363`, `30214930319` und `30214930361` waren erfolgreich. Die Welle ist damit fachlich und statisch abgeschlossen; Runtimefreigaben bleiben Gegenstand von `ADV-008`.
