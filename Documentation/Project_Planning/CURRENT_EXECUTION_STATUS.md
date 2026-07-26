# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-26 |
| Geprüfter Ausgangscommit auf `origin/main` | `1849e2207c67a062cd33e91b184cdc192a784a37` |
| Aktuelle Verarbeitungswelle | `ADV-004`, `ADV-005` |
| Zweck | kanonischer operativer Einstiegspunkt für die nächste Verarbeitung |

## 1. Verifizierter Repository-Stand

Der Commit `1849e2207c67a062cd33e91b184cdc192a784a37` ist auf `origin/main` vorhanden. Er enthält `ADV-003`, `TST-002`, 52 beobachtbare Lernziele, die Zuordnung der 39 Vertiefungsclaims sowie den aktiven Privacy- und Metadaten-Workflow.

Welle 0 und Gate A, `FWK-001` bis `FWK-012`, die SQL-Server-Matrix 2019/2022/2025, Gate B, `W2-001`, `W2-007`, `ADV-001` bis `ADV-003`, `PRS-009`, `PRS-011` und `TST-002` sind validiert.

## 2. Abgeschlossene Designwelle

| Arbeitspaket | Ergebnis | Status |
|---|---|---|
| `ADV-004` | LAB-VP1 sowie `OPT-015`, `OPT-016` und `OPT-017` vollständig entworfen | `VALIDATED` |
| `ADV-005` | LAB-VP2, `QRY-013` und die Erweiterung von `QRY-004` vollständig entworfen | `VALIDATED` |

Die Designwelle erzeugt keine ausführbaren SQL-Demos. Sie legt verbindlich fest:

- synthetische Datenmodelle und Skalierungsprofile,
- Preflight, Setup, Baseline, Problem- beziehungsweise Kontrastzustand, Evidenz, Gegenprobe, Vergleich und Cleanup,
- Sicherheitsstufen und Mindestressourcen,
- Quellen-, Claim- und Lernzielzuordnung,
- versionsabhängige `PASS`- und `SKIP`-Verträge,
- kleine spätere Implementierungsschnitte für `ADV-008`.

## 3. Freigegebene fachliche Folgearbeit

Nach dieser Welle sind folgende Pakete ausführbar:

1. `ADV-006`: LAB-VP3 und LAB-VP4 zu Workspace Memory, Spills und Intelligent Query Processing entwerfen.
2. `ADV-007`: LAB-VP5 und `DGN-007` als vollständigen Incident- und Capstone-Fall entwerfen.
3. Erste Implementierungsschnitte aus `ADV-008` dürfen erst begonnen werden, wenn der jeweilige Designvertrag Gate V2 erfüllt und die zugehörige Testmatrix feststeht.

`OPT-015`, `OPT-016`, `OPT-017`, `QRY-013` und die neue `QRY-004`-Struktur sind damit entworfen, aber ausdrücklich noch nicht `IMPLEMENTED` oder runtime-validiert.

## 4. Parallel ausführbare Querschnittsarbeit

Unabhängig von `ADV-006` und `ADV-007` bleiben ausführbar:

- `PRS-012` und `TST-011`: SlideKeys, Custom Shows und statische Präsentationsvariantenprüfung,
- fachlich getrennte `W2-002`-Teilpakete,
- Query-Store-/Extended-Events-Pilotvalidierung,
- Entscheidungspfad T-SQL/Testdatenbank vor zusätzlicher Infrastruktur im Demo-Katalog,
- Testumgebungs-How-to für vorhandene Instanz sowie Docker/Podman.

## 5. Abhängigkeiten

- `ADV-008` setzt den jeweils zutreffenden Designvertrag aus `ADV-004` bis `ADV-007` und Gate V2 voraus.
- `ADV-009` setzt belastbare Runtime-Evidenz und die Präsentationsvariantenverträge voraus.
- `PRS-013` setzt `PRS-012` und den statischen Kern von `TST-011` voraus.
- `W2-003` bis `W2-006` setzen die jeweils zugehörige Neutralisierung aus `W2-002` voraus.
- Rote Ressourcen- und I/O-Demos benötigen eine konkret zugeordnete isolierte Testumgebung.

## 6. Aktuelle Blocker

Es besteht kein globaler technischer Blocker. Planformabhängige Demos besitzen kontrollierte Skip-Verträge, wenn eine bestimmte Optimizerentscheidung trotz geeignetem Datenprofil nicht erzeugt wird. PSP- und OPPO-Demos dürfen fehlende Eligibility nicht als Produktfehler behandeln.

## 7. Datenschutz- und Quellenstatus

Die Designartefakte enthalten ausschließlich synthetische Objektmodelle, öffentliche Quellen-IDs, neutrale Demo- und Claim-IDs sowie generische Ressourcenprofile. Reale Anwendungs-, Host-, Benutzer-, Kunden-, Zugangs- oder Diagnosedaten sind ausgeschlossen. Jede spätere technische Aussage bleibt an die in `ADV-002` festgelegte Evidenzklasse und Quellenzuordnung gebunden.
