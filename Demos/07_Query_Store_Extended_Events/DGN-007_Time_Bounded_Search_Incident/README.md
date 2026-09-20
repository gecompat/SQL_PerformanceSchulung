# DGN-007 – Zeitabhängige Regression eines Suchworkloads

| Feld | Wert |
|---|---|
| Demo-ID | `DGN-007` |
| Status | `IMPLEMENTED_STATIC_SLICE_B` |
| Sicherheitsstufe | `YELLOW` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Sessions | höchstens drei: Workload, Beobachtung, Orchestrierung |

## Lernziel

Die Teilnehmenden verbinden ein zeitlich abgegrenztes Symptom mit Query-Store-Historie, Session- und Plankontext, Datenverteilung sowie eng begrenzten Wait- und Extended-Events-Signalen. Sie bilden eine falsifizierbare Hypothese, verwerfen mindestens zwei Alternativen und vergleichen genau eine reversible Änderung mit derselben Last.

## Fachliche Kernaussage

Query Store, Actual Execution Plan, DMVs und Extended Events liefern unterschiedliche Evidenz. Sie belegen jeweils nur ihren Scope; erst die konsistente Kette aus Zeitfenster, Parameterwert, Verteilung, Plan und gemessener Arbeit stützt eine Ursachenhypothese. Die referenzierte Änderung ist kein allgemeiner Tuningrat.

## Voraussetzungen und Grenzen

Dies ist Schnitt B zu dem bestehenden, markergebundenen Adapter unter [`Scenarios/DGN-007`](../../../Scenarios/DGN-007/README.md). Der Adapter erzeugt Datenmodell sowie die Fenster `T0_BASELINE` und `T1_INCIDENT`; diese Skripte bauen keinen Ersatzdatenbestand auf und ändern weder `Scenarios/` noch globale Caches. Vor der Ausführung ist eine bestätigte isolierte Wegwerfinstanz erforderlich (`--confirm-isolated-lab`), mit mindestens 4 logischen CPU-Kernen, 8 GB SQL-Server-Speicher sowie Platz für Testdaten, Query Store und TempDB.

Benötigt werden Rechte auf die markierte Testdatenbank, Query Store und zum Verwalten/Lesen einer begrenzten serverseitigen XE-Session. Query Store muss in der Testdatenbank `READ_WRITE` sein, andernfalls lautet der kontrollierte Ausgang `SKIP_QUERY_STORE_REQUIRED`. Ist die vorbereitete Historie nicht unterscheidbar, lautet der Ausgang `SKIP_INCIDENT_NOT_REPRODUCED`; ist eine erforderliche Evidenzquelle ungeeignet, lautet er `SKIP_EVIDENCE_MISSING`. Kein solcher Ausgang ist eine Evidenzbehauptung.

Query-Store-Waits und `MAX_DURATION` für XE werden vor Ort geprüft. PSP, OPPO, Query Store Hints und Plan Forcing sind keine Voraussetzung und werden im Primärfall nicht verwendet.

## Ablauf

1. Der Adapter bereitet die synthetische Datenbank `SQLPERF_LAB_DGN007_LOCAL` vor. Nur bei passenden vier Eigentumsmarkern ist sie ein zulässiges Ziel.
2. `00_Preflight.sql` prüft Version, Eigentumsmarker, Query-Store-Zustand und benötigte Rechte.
3. `20_Baseline.sql` dokumentiert T0 und T1 getrennt und richtet ausschließlich die begrenzte XE-Session für nachfolgende Vergleichsausführungen ein.
4. `40_Observation.sql` gibt die Evidenz in sechs Stufen aus. Bis zur sechsten Stufe enthält keine Ausgabe eine Lösungsempfehlung.
5. Erst nach der eigenen Hypothese wird `50_Mitigation.sql` ausgeführt. Es ersetzt nur die fest bekannte Suchprozedur durch eine querylokale `OPTION (RECOMPILE)`-Variante und sichert ihren Originaltext in der Testdatenbank.
6. `60_Comparison.sql` wartet begrenzt auf ein neues Query-Store-Intervall, erzeugt T2 mit denselben vier vorbereiteten Parameterklassen und prüft die Ergebnisgleichheit als bidirektionale Ergebnismenge. CPU-, Read- und Planwiederverwendungswerte werden durch diese Phase nicht selbst behauptet; sie bleiben auf geeignete Query-Store-Evidenz angewiesen.
7. Nach jeder Unterbrechung `90_Cleanup.sql` ausführen. Es stoppt/entfernt ausschließlich die deterministische XE-Session und stellt den gespeicherten Originaltext der Prozedur wieder her. Der Adapter-Cleanup entfernt danach die markierte Datenbank.

Es gibt absichtlich kein freigegebenes `manifest.json`: Die fachliche Demo ist noch nicht runtimevalidiert und darf daher weder in den Laufkatalog noch in den zentralen Ausführungsleitfaden aufgenommen werden. Die Phasen sind manuell gegen den vom Adapter vorbereiteten Zustand auszuführen. Der getrennte [automatisierte Datenmodell-Schnitt](Automated/README.md) besitzt ein eigenes `setup.manifest.json` für Preflight, synthetischen Aufbau, Datenassertion und Cleanup auf den Zielversionen 2019/2022/2025. Dieser Schnitt verwendet den separaten Run-Token `AUTO` und belegt noch keine Incident- oder Capstone-Abnahme.

## Evidenzstufen und Hypothesenblatt

| Stufe | Freigabe | Arbeitsauftrag |
|---|---|---|
| 1 | Symptom | Zeitfenster und fachlichen Requesttyp beschreiben. |
| 2 | Historie | Laufzeit- und Planübersicht lesen, ohne Planform zu deuten. |
| 3 | Kontext | Datenbank-, SET- und Cacheattribute auf Unterschiede prüfen. |
| 4 | Plan | Schätzung, tatsächliche Arbeit, Parameter und Statistikbezug vergleichen. |
| 5 | Systemsignale | Waits, Grants und XE nur als zeitlich passenden Hypothesenstart einordnen. |
| 6 | Vergleich | Ergebnisgleichheit und Nebenwirkungen der einen Änderung bewerten. |

| Hypothese | erwartete oder fehlende Evidenz | Urteil nach Stufe 5 | Begründung |
|---|---|---|---|
| Allgemeiner Memory Pressure | `RESOURCE_SEMAPHORE`, wartende Grants, passender Requestscope | offen | |
| I/O-Engpass | `PAGEIOLATCH_*`, Physical Reads, passendes Requestfenster | offen | |
| Client-/SET-Options-Unterschied | abweichende Optionen, Datenbank- oder Cacheattribute | offen | |
| Parameter- und Planwiederverwendung | Verteilung, Compilewert, Laufzeitprofil und Arbeit bilden eine Kette | offen | |

Mindestens zwei der ersten drei Hypothesen müssen anhand fehlender oder widersprechender Evidenz verworfen werden. Eine leere XE- oder Wait-Sicht widerlegt nichts ohne nachgewiesene Session, Predicate, Eventklasse und Zeitfenster.

## Erwartete Resultate und zulässige Abweichungen

T0, T1 und T2 bleiben getrennte Zeitfenster und Query-Store-Intervalle. Die Query-Store-Abfragen sind auf `dbo.usp_CaseSearch` und den Marker `DGN007_CASE_SEARCH` gebunden. Die Ausgaben verwenden keine festen Millisekunden, Plan-Node-IDs oder universellen Operatorerwartungen. Erforderlich sind gleiche fachliche Ergebnismengen für die vier vorbereiteten Vergleichsparameter und mindestens zwei unterscheidbare Query-Store-Plan- oder Laufzeitprofile zwischen T0/T1. Die XE-Session startet erst nach T1; ihre begrenzten Ereignisse gelten ausschließlich als Kontext für nachfolgende Vergleichsausführungen, nicht als rückwirkende T0-/T1-Evidenz. Planwahl, absolute Dauer, XE-Ereigniszahl und Query-Store-Flush sind empirisch. Eine fehlende geeignete Evidenz beendet die jeweilige Bewertung mit einem dokumentierten `SKIP` statt mit einer Ursachenbehauptung.

## Cleanup und Recovery

`90_Cleanup.sql` ist idempotent: Ohne gespeicherten Originaltext erfolgt keine Prozeduränderung; bei passenden Datenbankmarkern wird nur die lokale XE-Session entfernt. Ein Datenbank-Drop ist nicht Bestandteil dieses Ordners und bleibt beim bestehenden markergebundenen Adapter-Cleanup.

## Statische Prüfung und Statusgrenze

Die Artefakte wurden nur statisch geprüft. Es bestehen keine Runtime- oder `VALIDATED`-Behauptungen für die fachliche Demo. Die Runtime-Matrix 2019/2022/2025 und die didaktische Generalprobe bleiben offen.

## Quellen und Traceability

- `SRC-001`, `SRC-007`, `SRC-027`, `SRC-028`, `SRC-031`, `SRC-035`, `SRC-036`; Abrufdatum gemäß Quellenregister: 2026-07-26.
- Ergänzend `SRC-040`, `SRC-046`, `SRC-047`, `SRC-051`; die Community-Quelle begründet nur Diagnosemethodik.
- `ADV-CLM-013` bis `ADV-CLM-015`, `ADV-CLM-034` bis `ADV-CLM-039`; `LO-M07-04`, `LO-M06-08`, `LO-M03-07`.
