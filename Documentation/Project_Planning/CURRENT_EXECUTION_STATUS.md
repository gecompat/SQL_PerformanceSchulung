# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-27 |
| Geprüfter Ausgangscommit auf `origin/main` | `37bc7d6896603eb614dfdeb41f8a77ff947abe68` |
| Fachliche Hauptwelle | `ADV-008` – nächste Runtime-Schnitte `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC` |
| Infrastrukturwelle | `LABINT-002` – einfacher Runner über öffentliche Commands von `SQL_Server_Lab` |
| Zweck | kanonischer operativer Einstiegspunkt für Demoimplementierung, Runtimevalidierung und Testsystemautomation |

## 1. Verifizierter Repository-Stand

Der Commit `37bc7d6896603eb614dfdeb41f8a77ff947abe68` ist auf `origin/main` vorhanden. Er enthält die unter `ADV-008` implementierten und runtimevalidierten Demos `OPT-015` und `OPT-016` sowie den initialen Lab-Testkatalog.

Welle 0 und Gate A, `FWK-001` bis `FWK-012`, die Framework-Matrix 2019/2022/2025, Gate B, `W2-001`, `W2-007`, `PRS-009`, `PRS-011`, `TST-002`, `ADV-006` und `ADV-007` sind validiert.

## 2. Abgeschlossener ADV-008-Teilstand

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | planweite und operatorbezogene Planevidenz mit synthetischem Out-of-range-Statistikfall, gezielter Statistikaktualisierung und normalisiertem Actual-Plan-Vertrag | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und optimizergewählte Performance Spool mit kontrollierter `NO_PERFORMANCE_SPOOL`-Gegenprobe | `VALIDATED` |

Beide Demos wurden auf SQL Server 2019, 2022 und 2025 jeweils zweimal einschließlich Cleanup validiert.

## 3. Korrigierte Erwartung an SQL_Server_Lab

`SQL_Server_Lab` wird in diesem Projekt ausschließlich als Bereitstellungs- und Lifecycle-Komponente verwendet.

Erwartet werden:

- SQL-Server-Umgebung mit Docker oder Podman erstellen;
- angeforderte SQL-Server-Version und Ressourcenprofil anwenden;
- SQL-Readiness prüfen;
- Run-ID, Provider, Host und Port als PowerShell-Objekt zurückgeben;
- Umgebung anhand der Run-ID sicher entfernen.

Nicht erwartet werden:

- Kenntnis der Schulungsdemos oder Lernziele;
- Ausführung der Demo-Phasen im Lab-Repository;
- eine Project-Adapter- oder Lab-Package-Engine;
- eine generische JSON-/Event-Schnittstelle;
- Migration des Schulungs-Harness in das Lab-Repository.

Die Demoauswahl, Ausführung, fachlichen Assertions, Wiederholungen und Reports bleiben vollständig in `SQL_PerformanceSchulung`.

## 4. Aktueller Lab-Testkatalog

`LABINT-001` stellt bereit:

- den Katalog `Tests/Lab/performance-lab-matrix.json`;
- das zugehörige JSON-Schema;
- eine statische Discovery-Prüfung für alle produktiven Demo-Manifeste;
- die Lanes `SMOKE`, `CORE`, `PROVIDER_PARITY`, `FULL_CONTAINER_MATRIX` und `RED_DISPOSABLE`.

Der Katalog enthält derzeit sechs produktive Demos. Die vollständige Docker-/Podman-/Versionsmatrix umfasst 72 Demoläufe. Der JSON-Katalog ist eine interne Steuerungsdatei des Schulungsprojekts und keine Ausgabeforderung an `SQL_Server_Lab`.

## 5. Derzeit notwendige Änderungen in SQL_Server_Lab

Für `LABINT-002` ist derzeit **keine zusätzliche Lab-Funktion erforderlich**.

Der reale Runner muss zunächst Docker und Podman über die vorhandenen öffentlichen Commands prüfen. Eine Änderung im Lab-Repository wird nur dann verlangt, wenn ein Test eine konkrete, reproduzierbare Lücke nachweist.

Als mögliche Robustheitslücke ist festgehalten, dass das zusätzliche Orphan-Sicherheitsnetz von `Remove-SqlServerLab` Docker-spezifisch erscheint. Der normale Cleanup-Plan enthält bereits providerbezogene Compensation für Docker und Podman. Erst ein tatsächlich unvollständiger Podman-Cleanup begründet eine Anforderung für einen providerneutralen Orphan-Cleanup.

An `SQL_Server_Lab` wurde nichts geändert.

## 6. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `PARTIAL`; `OPT-015` und `OPT-016` sind freigegeben.
- Gate V4 – Lehrmittelfreigabe: offen.
- `LABINT-001`: `VALIDATED`.
- `LABINT-002`: offen.

## 7. Nächste fachliche Verarbeitung

Der nächste abhängige ADV-008-Schnitt umfasst:

1. `QRY-013` – neutraler Client- und Sessionkontext.
2. `QRY-004_CLASSIC_AND_DYNAMIC` – Catch-all, `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL.
3. Query-Store-/XE-Pilotvalidierung vor diagnoseabhängigen Schnitten.
4. `OPT-017` und LAB-VP3-/VP4-Implementierungen anschließend in getrennten Paketen.
5. `DGN-007` erst nach stabiler Query-Store-/XE-Evidenz.
6. `RES-003` zuletzt und ausschließlich auf dedizierter Infrastruktur.

## 8. Nächste Infrastrukturverarbeitung

`LABINT-002` implementiert den einfachen PowerShell-Runner:

1. `SQL_Server_Lab/SqlServerLab.psd1` importieren.
2. Katalog und lokale Voraussetzungen prüfen.
3. `New-SqlServerLab` mit Version, Provider, Profil und Laufzeitkennwort aufrufen.
4. Host und Port aus dem Rückgabeobjekt übernehmen.
5. grüne Demos über den bestehenden `run_demo.py`-Harness ausführen.
6. Demo-Cleanup nach jedem Lauf prüfen.
7. im `finally`-Pfad `Remove-SqlServerLab -RunId ... -Force` aufrufen.
8. vollständigen Infrastrukturabbau prüfen.

Es wird keine zusätzliche Package-, JSON- oder Event-Architektur vorausgesetzt.

## 9. Parallel ausführbare Querschnittsarbeit

Unabhängig von ADV-008 und LABINT bleiben ausführbar:

- `PRS-012` und `TST-011`;
- fachlich getrennte `W2-002`-Teilpakete;
- Query-Store-/Extended-Events-Pilotvalidierung;
- Testumgebungs-How-to für vorhandene SQL-Server-Instanz.

## 10. Abhängigkeiten und Sicherheitsgrenzen

- Ein neues produktives Demo-Manifest benötigt zwingend einen Eintrag im Lab-Testkatalog.
- `LABINT-003` setzt den grünen Runner aus `LABINT-002` voraus.
- `LABINT-004` setzt Safety-Bestätigung und getrennte Umgebungsprofile voraus.
- Eine Lab-Änderung setzt einen konkreten Testbefund und ausdrückliche Freigabe voraus.
- `DGN-007` setzt eine validierte Query-Store- und XE-Nutzung voraus.
- `RES-003` setzt dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget voraus.

## 11. Datenschutz- und Quellenstatus

Die Lab-Integrationsartefakte enthalten ausschließlich Repository-IDs, relative Pfade, öffentliche Versionsbezeichnungen, generische Provider- und Capability-IDs sowie synthetische Demo-IDs. Reale Hosts, Ports, Benutzer, Kennwörter, lokale Pfade und Diagnosedaten werden nicht versioniert.
