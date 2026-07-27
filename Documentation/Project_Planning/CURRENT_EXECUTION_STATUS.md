# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-27 |
| Geprüfter Ausgangscommit auf `origin/main` | `091fa8606491d6f5fff2f3cd483d11868ce7d5e7` |
| Fachliche Hauptwelle | `ADV-008` – nächste Runtime-Schnitte `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC` |
| Parallelwelle | `LABINT-001` – Integration mit `SQL_Server_Lab` |
| Zweck | kanonischer operativer Einstiegspunkt für Demoimplementierung, Runtimevalidierung und Testsystemautomation |

## 1. Verifizierter Repository-Stand

Der Commit `091fa8606491d6f5fff2f3cd483d11868ce7d5e7` ist auf `origin/main` vorhanden. Er enthält `ADV-001` bis `ADV-007`, Gate V2 sowie die unter `ADV-008` implementierten und runtimevalidierten Demos `OPT-015` und `OPT-016`.

Welle 0 und Gate A, `FWK-001` bis `FWK-012`, die Framework-Matrix 2019/2022/2025, Gate B, `W2-001`, `W2-007`, `ADV-001` bis `ADV-007`, `PRS-009`, `PRS-011` und `TST-002` sind validiert.

## 2. Abgeschlossener ADV-008-Teilstand

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | planweite und operatorbezogene Planevidenz mit synthetischem Out-of-range-Statistikfall, gezielter Statistikaktualisierung und normalisiertem Actual-Plan-Vertrag | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und optimizergewählte Performance Spool mit kontrollierter `NO_PERFORMANCE_SPOOL`-Gegenprobe | `VALIDATED` |

Beide Demos besitzen den vollständigen Phasenvertrag. Die Runtime-Matrix führte jede Demo auf SQL Server 2019, 2022 und 2025 zweimal aus. Damit wurden zwölf vollständige Demo-Läufe einschließlich unabhängig geprüftem Cleanup erfolgreich abgeschlossen.

## 3. Parallel abgeschlossene Planungswelle LABINT-001

`SQL_Server_Lab` wurde am Stand `08fcc9525b9bbc29a5dd9a2ef08de23bd7ef650e` gegen die Anforderungen des Schulungsrepositories geprüft. Docker- und Podman-Provisionierung, Portbindung, SQL-Readiness, Run State und scopegebundener Cleanup sind bereits implementiert und reichen für einen ersten externen Schulungsrunner aus.

`LABINT-001` stellt bereit:

- die Architektur unter `Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md`;
- den maschinenlesbaren Katalog `Tests/Lab/performance-lab-matrix.json`;
- das zugehörige JSON-Schema;
- eine statische Discovery-Prüfung für alle produktiven Demo-Manifeste;
- die Lanes `SMOKE`, `CORE`, `PROVIDER_PARITY`, `FULL_CONTAINER_MATRIX` und `RED_DISPOSABLE`;
- die explizite Trennung zwischen vorläufig externem Project Adapter und späterer nativer Lab-Package-Ausführung.

Der aktuelle Katalog enthält sechs produktive Demos. Die vollständige Docker-/Podman-/Versionsmatrix umfasst gegenwärtig 72 Demoläufe.

## 4. Festgestellte Grenze von SQL_Server_Lab

Für `LABINT-002` ist keine Änderung am Lab-Repository erforderlich. Der Runner kann `New-SqlServerLab`, das zurückgegebene Endpunktobjekt, den bestehenden Demo-Harness und `Remove-SqlServerLab` kombinieren.

Für die spätere native Package-Ausführung sind im Lab-Repository noch separat abzustimmende Erweiterungen erforderlich:

- implementierte Project-Adapter-/Lab-Package-Engine;
- öffentliche Recovery- und Cleanup-Commands;
- providerneutraler Orphan-Cleanup einschließlich Podman;
- maschinenlesbarer Capability-, Build- und Image-Digest-Nachweis;
- Ressourcenübersteuerung mit sichtbarem Defizit statt vollständigem `SkipAssessment`;
- strukturierter nichtinteraktiver Event- und Ergebnisvertrag.

An `SQL_Server_Lab` wurde in dieser Welle nichts geändert.

## 5. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `PARTIAL`; `OPT-015` und `OPT-016` sind freigegeben.
- Gate V4 – Lehrmittelfreigabe: offen.
- `LABINT-001`: Architektur- und Katalogfreigabe nach statischer CI-Abnahme.
- `LABINT-002`: noch nicht implementiert.

## 6. Nächste fachliche Verarbeitung

Der nächste abhängige ADV-008-Schnitt umfasst:

1. `QRY-013` – neutraler Client- und Sessionkontext.
2. `QRY-004_CLASSIC_AND_DYNAMIC` – Catch-all, `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL.
3. Query-Store-/XE-Pilotvalidierung vor diagnoseabhängigen Schnitten.
4. `OPT-017` und LAB-VP3-/VP4-Implementierungen anschließend in getrennten Ressourcen- und Featurepaketen.
5. `DGN-007` erst nach stabiler Query-Store-/XE-Evidenz.
6. `RES-003` zuletzt und ausschließlich auf dedizierter Infrastruktur.

## 7. Nächste Infrastrukturverarbeitung

`LABINT-002` implementiert zunächst ausschließlich `SMOKE` und `CORE`:

1. lokales Sibling-Checkout von `SQL_Server_Lab` binden;
2. Modulversion, PowerShell, Python und `sqlcmd` prüfen;
3. Docker oder Podman über das Lab provisionieren;
4. grüne Demos kataloggesteuert ausführen;
5. Demo-Cleanup nach jedem Lauf unabhängig prüfen;
6. im `finally`-Pfad `Remove-SqlServerLab -Force` ausführen;
7. sanitisierten Ergebnisreport erzeugen.

Providerparität und gelbe Demos folgen erst nach erfolgreichem Cleanup- und Versionsnachweis der grünen Lane.

## 8. Parallel ausführbare Querschnittsarbeit

Unabhängig von ADV-008 und LABINT bleiben ausführbar:

- `PRS-012` und `TST-011`;
- fachlich getrennte `W2-002`-Teilpakete;
- Query-Store-/Extended-Events-Pilotvalidierung;
- Testumgebungs-How-to für vorhandene SQL-Server-Instanz.

## 9. Abhängigkeiten und Sicherheitsgrenzen

- Ein neues produktives Demo-Manifest benötigt künftig zwingend einen Eintrag im Lab-Testkatalog.
- `LABINT-003` setzt den funktionierenden grünen Runner aus `LABINT-002` voraus.
- `LABINT-004` setzt Safety-Bestätigung und getrennte Umgebungsprofile voraus.
- `LABINT-005` setzt die ausdrücklich freigegebenen Erweiterungen in `SQL_Server_Lab` voraus.
- `DGN-007` setzt eine validierte Query-Store- und XE-Nutzung voraus.
- `RES-003` setzt dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget voraus.

## 10. Datenschutz- und Quellenstatus

Die Lab-Integrationsartefakte enthalten ausschließlich Repository-IDs, relative Pfade, öffentliche Versionsbezeichnungen, generische Provider- und Capability-IDs sowie synthetische Demo-IDs. Reale Hosts, Ports, Benutzer, Kennwörter, lokale Pfade und Diagnosedaten werden nicht versioniert. Runtime-Reports dürfen keine Plan-XML-, Querytext- oder Secret-Inhalte automatisch exportieren.
