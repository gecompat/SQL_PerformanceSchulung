# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-07-27 |
| Geprüfter Ausgangscommit auf `origin/main` | `0a16896f484575fb6d76bff13ad19db5e9e96e44` |
| Fachliche Hauptwelle | `ADV-008` – nächste Runtime-Schnitte `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC` |
| Szenariowelle | `LABSCN-002` – Szenarioinventar und Definitionsschema |
| Zweck | kanonischer operativer Einstiegspunkt für Demoimplementierung, interaktive Schulungsszenarien und nachgeordnete Runtimevalidierung |

## 1. Verifizierter Repository-Stand

Der Ausgangsstand enthält die unter `ADV-008` implementierten und runtimevalidierten Demos `OPT-015` und `OPT-016`, den automatisierten Lab-Testkatalog sowie die korrigierte Verantwortungsgrenze zu `SQL_Server_Lab`.

Die während der aktuellen Verarbeitung versehentlich auf `main` angelegten Platzhalterdateien wurden jeweils unmittelbar im Folgecommit vollständig entfernt. Im aktuellen Repositoryinhalt ist keine dieser Dateien vorhanden.

Welle 0 und Gate A, `FWK-001` bis `FWK-012`, die Framework-Matrix 2019/2022/2025, Gate B, `W2-001`, `W2-007`, `PRS-009`, `PRS-011`, `TST-002`, `ADV-006` und `ADV-007` sind validiert.

## 2. Abgeschlossener ADV-008-Teilstand

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | planweite und operatorbezogene Planevidenz mit synthetischem Out-of-range-Statistikfall, gezielter Statistikaktualisierung und normalisiertem Actual-Plan-Vertrag | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und optimizergewählte Performance Spool mit kontrollierter `NO_PERFORMANCE_SPOOL`-Gegenprobe | `VALIDATED` |

Beide Demos wurden auf SQL Server 2019, 2022 und 2025 jeweils zweimal einschließlich Cleanup validiert.

## 3. Verbindlicher Zielzustand der Lab-Integration

`LABSCN-001` und `DEC-044` legen fest:

- Für geeignete Schulungsbeispiele wird eine vollständig vorbereitete Laborumgebung erzeugt.
- Der Benutzer kann ein einzelnes Beispiel auswählen und unabhängig vom vollständigen Schulungslauf starten.
- Die Umgebung kann Docker, Podman, Hyper-V oder eine gemischte Topologie verwenden.
- `SQL_Server_Lab` ist das verbindliche Provisionierungsframework.
- `SQL_PerformanceSchulung` definiert Lernziel, Ausgangssituation, Setup, synthetische Daten, Benutzeraktionen, Beobachtungsabfragen und Reset.
- Nach erfolgreicher Vorbereitung verbleibt die Umgebung im Status `READY_FOR_USER`.
- Der Benutzer kann das Verhalten selbst untersuchen, Abfragen verändern, Parameter variieren, Gegenmaßnahmen testen und Beobachtungen wiederholen.
- Die Umgebung wird erst auf ausdrücklichen Wunsch zurückgesetzt oder vollständig entfernt.

Der kanonische Vertrag steht unter `Documentation/Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`.

## 4. Rolle von SQL_Server_Lab

`SQL_Server_Lab` wird verwendet, um die technische Umgebung zu realisieren. Abhängig vom Szenario kann dies umfassen:

- Docker- oder Podman-Container;
- Hyper-V-VMs mit Windows oder Linux;
- mehrere SQL-Server-Instanzen;
- getrennte CPU-, RAM-, Storage- oder Netzwerkprofile;
- zusätzliche Client- oder Workload-Komponenten;
- gemischte Topologien.

Das Schulungsrepository implementiert keine eigene Providerprovisionierung.

Fehlt für ein konkretes Szenario eine Lab-Fähigkeit, wird diese Lücke mit Szenario-ID, Topologie und technischem Bedarf dokumentiert. Eine Änderung in `SQL_Server_Lab` erfolgt erst nach ausdrücklicher Freigabe.

## 5. Rolle der automatisierten Testmatrix

Der vorhandene Katalog `Tests/Lab/performance-lab-matrix.json` bleibt als Qualitätssicherungsinstrument bestehen. Er prüft später:

- Aufbau der Umgebung;
- reproduzierbare Vorbereitung;
- zentrale Kernbeobachtungen;
- Reset;
- vollständigen Abbau.

Die automatisierte Matrix ist nicht der Benutzerworkflow. Ein Testlauf darf eine kurzlebige Umgebung entfernen; ein interaktives Szenario bleibt dagegen nach der Vorbereitung verfügbar.

## 6. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `PARTIAL`; `OPT-015` und `OPT-016` sind freigegeben.
- Gate V4 – Lehrmittelfreigabe: offen.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: offen.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.

## 7. Nächste Szenarioverarbeitung

`LABSCN-002` ist der nächste abhängige Infrastruktur- und Bedienungsschritt:

1. alle vorhandenen und geplanten Beispiele inventarisieren;
2. jedes Beispiel als interaktiv geeignet, nur automatisiert prüfbar oder nicht anwendbar klassifizieren;
3. erforderliche SQL-Versionen, Provider, Topologien und Komponenten erfassen;
4. Host-Mindestanforderungen dokumentieren;
5. Aufbau, Vorbereitung, Benutzerübergabe, Reset und Abbau modellieren;
6. ein Schema für die Szenariodefinitionen erstellen;
7. einen geeigneten grünen Vertical Slice für `LABSCN-003` auswählen.

`LABSCN-003` setzt anschließend erstmals einen vollständigen Benutzerablauf um:

```text
Auswahl
-> Provisionierung mit SQL_Server_Lab
-> fachliche Vorbereitung
-> READY_FOR_USER
-> interaktive Durchführung
-> Reset
-> Remove
```

## 8. Nächste fachliche Verarbeitung

Der nächste abhängige ADV-008-Schnitt umfasst:

1. `QRY-013` – neutraler Client- und Sessionkontext.
2. `QRY-004_CLASSIC_AND_DYNAMIC` – Catch-all, `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL.
3. Query-Store-/XE-Pilotvalidierung vor diagnoseabhängigen Schnitten.
4. `OPT-017` und LAB-VP3-/VP4-Implementierungen anschließend in getrennten Paketen.
5. `DGN-007` erst nach stabiler Query-Store-/XE-Evidenz.
6. `RES-003` zuletzt und ausschließlich auf dedizierter Infrastruktur.

## 9. Parallel ausführbare Querschnittsarbeit

Unabhängig von ADV-008 und LABSCN bleiben ausführbar:

- `PRS-012` und `TST-011`;
- fachlich getrennte `W2-002`-Teilpakete;
- Query-Store-/Extended-Events-Pilotvalidierung;
- `INF-001` – Ausführungsziele und Testumgebungs-How-to für eine vorhandene SQL-Server-Instanz. Die Ausführungsziele sind in `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md` entworfen; die Entkopplung der Runtime-Runner und das How-to stehen aus.

## 10. Abhängigkeiten und Sicherheitsgrenzen

- Eine Szenariodefinition ergänzt das bestehende Demo-Manifest und ersetzt es nicht.
- Jedes interaktive Szenario benötigt Benutzerübergabe, Reset und Abbau.
- Gelbe und rote Szenarien benötigen ihre bestehenden Safety-Gates.
- Gemischte Topologien werden nur bei fachlich nachgewiesenem Bedarf umgesetzt.
- Eine Änderung im Lab-Repository setzt eine konkret dokumentierte fehlende Fähigkeit und ausdrückliche Freigabe voraus.
- `DGN-007` setzt eine validierte Query-Store- und XE-Nutzung voraus.
- `RES-003` setzt dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget voraus.

## 11. Datenschutz- und Quellenstatus

Szenariodefinitionen enthalten ausschließlich synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen. Reale Hosts, Benutzer, Kennwörter, interne Pfade oder produktive Diagnosedaten werden nicht versioniert.
