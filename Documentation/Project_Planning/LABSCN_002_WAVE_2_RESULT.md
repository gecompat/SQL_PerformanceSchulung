# LABSCN-002 – Ergebnis Wellen 2 und 3

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Branch | `agent/labscn-wave1-inventory` |
| Arbeitspaket | `LABSCN-002` |
| Verbindliche Ergänzung | `Documentation/Architecture/TSQL_SCENARIO_ORCHESTRATION.md` |
| Folgeschritt | weitere Kandidaten ausschließlich nach eigenem Detailreview und Quellenfreigabe |

## 1. Ergebnis

Das Szenarioinventar, die Szenarioschemata und der erste Szenarioentwurf berücksichtigen nun zwei voneinander unabhängige Klassifikationsachsen. Die Klassen `A` bis `D` beschreiben die technische Reproduzierbarkeit. Die Modi `MANUAL`, `RUNNER_ASSISTED` und `AUTOMATED_VERIFY` beschreiben die fachlich erforderliche Orchestrierungsstufe.

Es gilt verbindlich die kleinste ausreichende Orchestrierungsstufe. Ein vorhandener Runner begründet daher nicht automatisch einen runnergestützten Teilnehmerablauf.

## 2. Source of Truth

Die eigenständigen T-SQL-Dateien und die Teilnehmeranleitung bleiben die fachliche Source of Truth. Python, PowerShell, CI und ein späteres Notebook dürfen diese Artefakte ausführen oder darstellen, aber keine exklusive fachliche SQL-Logik enthalten.

`SQL_Server_Lab` bleibt auf Infrastruktur-Orchestrierung begrenzt. SQL-Sessions, fachliche Reihenfolge, Schleifen, Beobachtungsbereitschaft, Reset und Cleanup werden durch `SQL_PerformanceSchulung` beschrieben.

## 3. Angepasste Vertragsartefakte

`Documentation/Architecture/performance-training-scenario.schema.json` verwendet Vertragsversion `1.1` und verlangt nun einen Orchestrierungsvertrag. Dieser enthält einen Primärmodus, unterstützte Modi und die jeweils erforderlichen Artefakte:

- `MANUAL`: kanonische T-SQL-Skripte je Sessionrolle und eindeutige Startreihenfolge;
- `RUNNER_ASSISTED`: Runnervertrag, Timeout, Stopverhalten und `READY_FOR_OBSERVATION`;
- `AUTOMATED_VERIFY`: vorhandenes Runtime-Manifest für Smoke- und Regressionstests.

`Documentation/Architecture/performance-training-scenario-inventory.schema.json` und `Documentation/Inventories/performance_scenario_inventory.json` führen dieselbe Orchestrierungsachse. Der statische Validator prüft die Konsistenz zwischen Inventar, Szenariodefinition und referenzierten Artefakten.

## 4. Geänderte Einordnung von CON-004

`CON-004` bleibt der bevorzugte erste Vertical Slice. Die primäre Orchestrierungsstufe wurde jedoch von einem implizit runnerzentrierten Ablauf auf `MANUAL` korrigiert.

Der Teilnehmer öffnet vier SQL-Fenster und startet nacheinander:

1. `HEAD`;
2. `MIDDLE`;
3. `LEAF`;
4. `OBSERVER`.

Das bewusste Starten und Beobachten der Sessions ist Bestandteil des Lernziels. Die T-SQL-Signale bleiben erhalten und verhindern zufällige Sleep-basierte Abläufe.

Das vorhandene Runtime-Manifest bleibt unverändert als `AUTOMATED_VERIFY`. Es prüft den fachlichen Zustand automatisiert, ersetzt aber nicht den manuellen Schulungsablauf.

Ein `RUNNER_ASSISTED`-Modus wird für `CON-004` erst implementiert, wenn ein konkreter Bedarf an dauerhaft oder wiederholt erzeugten Blocking-Zuständen besteht.

## 5. Statusmodell

Für manuelle Szenarien ist `READY_FOR_USER` der Übergabestatus: Infrastruktur, Datenbank und Baseline sind vorbereitet; die fachlichen Sessions werden durch den Teilnehmer gestartet.

Für runnergestützte Szenarien ist `READY_FOR_OBSERVATION` der Übergabestatus: Der Runner hat den zu beobachtenden Laufzeitzustand bereits hergestellt und hält ihn innerhalb definierter Grenzen aufrecht.

Nicht jedes Szenario durchläuft beide Zustände.

## 6. Korrigierte Metadaten

Der Lab-Testkatalog führte `CON-004` ursprünglich mit drei Sessions. Das tatsächlich ausgeführte Problemmanifest verwendet vier parallele Sessions: `HEAD`, `MIDDLE`, `LEAF` und `OBSERVER`. Der Katalog wurde auf vier Sessions korrigiert. Der getrennte Vergleichslauf verwendet `FIRST_WRITER` und `FOLLOWER`.

## 7. Validierungsstand

Die JSON-Verträge und Repositorybeziehungen wurden strukturell angepasst. Der statische Validator `Tests/Static/validate_performance_scenarios.py` läuft seit `.github/workflows/performance-scenarios.yml` auf einem GitHub-gehosteten Runner; zuvor war er nur lokal ausführbar.

Damit ist die Vertragskonsistenz zwischen Inventar, Szenariodefinition und referenzierten Repository-Pfaden dauerhaft abgesichert. `LABSCN-003` hat `CON-004` anschließend auf Docker und Podman praktisch validiert; `DGN-005` bestätigt denselben standardisierten Lifecycle als zweiter Slice.

## 8. Geänderte Reihenfolge für LABSCN-003

1. manuelle Teilnehmeranleitung für `CON-004` auf vier SQL-Fenster ausrichten;
2. konkretes `SQL_Server_Lab`-Manifest erstellen;
3. Provisionierung und fachliche Vorbereitung bis `READY_FOR_USER` implementieren;
4. Verbindungs- und Rollenübergabe bereitstellen;
5. manuellen Ablauf und Reset prüfen;
6. vorhandenen FWK-006-/FWK-010-Pfad als `AUTOMATED_VERIFY` ausführen;
7. Docker- und Podman-Lifecycle validieren;
8. anschließend ein eigenständiges, fachlich tatsächlich `RUNNER_ASSISTED` benötigendes Szenario auswählen.

## 9. Abschluss der Folgeintegration

Die Bedienkommandos für Start, Reset und Remove, die Teilnehmerübergabe und die
Docker-/Podman-Runtimeabnahme sind inzwischen implementiert und praktisch
validiert. Das endgültige Inventar umfasst 22 produktive Demos. Weitere
interaktive Szenarien gehören nicht mehr zum Abschluss von `LABSCN-002`,
sondern jeweils als eigener, quellen- und runtimegebundener Schnitt zu
`LABSCN-005`.
