# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-26 |
| Geprüfter `main`-Commit | `e265a267764c4db29f3bf76b21622b43780a88fb` |
| Offene Pull Requests | keine |
| Offene Arbeitsbranches | keine durch den GitHub Connector gefunden |
| Zweck | operativer Einstiegspunkt und Korrektur veralteter Statusmarker im Masterplan |

## 1. Geltung

Dieses Dokument ist der kanonische operative Status für die Wiederaufnahme der Arbeiten. Die langfristige Struktur und die fachlichen Arbeitspakete bleiben im [Master-Umsetzungsplan](MASTER_IMPLEMENTATION_PLAN.md) verbindlich. Widersprechen dessen historische Abschnitte 18 oder 20 diesem Status, gilt für Fortschritt, nächsten Einstiegspunkt und Blocker dieses Dokument, bis der Masterplan vollständig konsolidiert wird.

## 2. Abgeschlossener Stand

- Welle 0 und Gate A sind validiert.
- `FWK-001` bis `FWK-012` sind implementiert und auf SQL Server 2019, 2022 und 2025 runtime-validiert.
- Gate B ist mit `QRY-001`, `OPT-002`, `CON-004` und `OPT-013` sowie 24 vollständigen Demoläufen validiert.
- Die SQL-Server-Matrix 2019/2022/2025 ist aktiv und erfolgreich ausgeführt.
- `W2-001` hat alle historischen Beispiele klassifiziert; kein historisches Skript ist dadurch zur direkten Ausführung freigegeben.
- `W2-007` ist abgeschlossen. Der aktive Foliensatz besitzt 84 `KEEP`-Entscheidungen und keine offenen `REFINE`-Claims.
- `ADV-001` hat den quellenbasierten Vertiefungsstrang und fünf LAB-Serien festgelegt.
- `DEC-043` und `PRS-009` haben das Masterdeck als einzige bearbeitete Präsentationsquelle sowie die Profile `BASIS`, `STANDARD` und `VERTIEFUNG` festgelegt.

## 3. Erste Prioritätswelle

Die erste Prioritätswelle umfasst ausschließlich Planungs- und Vertragsartefakte. Sie verändert weder die PowerPoint-Datei noch ausführbare SQL-Demos.

| Reihenfolge | Arbeitspaket | Ergebnis | Status nach dieser Welle |
|---:|---|---|---|
| 1 | Statuskonsolidierung | dieser operative Status ersetzt die veralteten Fortschrittsmarker | `VALIDATED` |
| 2 | `ADV-002` | Claim- und Quellenmatrix für alle Vertiefungsabschnitte | `VALIDATED` |
| 3 | `PRS-011` | SlideKey- und Variantenmanifest-Vertrag einschließlich JSON Schema | `VALIDATED` |

## 4. Unmittelbar nächste ausführbare Arbeiten

Nach Abschluss dieser Welle können folgende Arbeitspakete parallel begonnen werden:

1. `ADV-003`: Curriculum-Lernziele und Traceability für M02, M03, M06 und M07 erweitern.
2. `PRS-012`: Masterdeck mit stabilen SlideKeys und den drei Custom Shows ausstatten.
3. `TST-011`: statischen Variantenvalidator implementieren.
4. `W2-002`: priorisierte historische Beispiele von internen und externen Abhängigkeiten befreien.
5. `TST-002`: automatisierte Privacy-Prüfung für Text-, Office- und Bildmetadaten implementieren.
6. Query Store und Extended Events als zentrale Diagnosepfade in repräsentativen Demos validieren.

## 5. Abhängigkeiten

- `ADV-004` bis `ADV-007` setzen `ADV-003` voraus.
- `ADV-008` setzt die jeweiligen Demo-Designs und Gate V2 voraus.
- `ADV-009` setzt belastbare Demo-Evidenz sowie `PRS-011` voraus.
- `PRS-013` setzt `PRS-012` und den statischen Kern von `TST-011` voraus.
- `TST-012` setzt erzeugte Varianten aus `PRS-013` voraus.
- `W2-003` bis `W2-006` setzen `W2-002` voraus.
- Ressourcengrenzen, Hyper-V- oder Netzwerkprofile werden nur nach einer konkreten Demo-Abhängigkeit bearbeitet.

## 6. Aktuelle Blocker

Es besteht kein globaler technischer Blocker. Die folgenden Abhängigkeiten begrenzen lediglich einzelne Stränge:

- Vertiefungsdemos dürfen erst nach Claim-, Curriculum- und Designfreigabe implementiert werden.
- Eigenständige Präsentationsvarianten dürfen erst nach stabiler Folienidentität und Manifestvalidierung erzeugt werden.
- Rote Ressourcen- und I/O-Demos benötigen eine ausdrücklich zugeordnete isolierte Testumgebung.

## 7. Datenschutzstatus

Die in dieser Welle erzeugten Artefakte enthalten ausschließlich öffentliche technische Quellen-IDs, neutrale Projekt- und Demo-IDs sowie synthetische Beispiele. Es werden keine realen Diagnosewerte, Hostnamen, Zugangsdaten, Kundendaten, internen Pfade oder proprietären Umgebungsinformationen aufgenommen.
