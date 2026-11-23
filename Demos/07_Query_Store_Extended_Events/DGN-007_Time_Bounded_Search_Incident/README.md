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

Query Store, Actual Execution Plan, DMVs (Dynamic Management Views; dynamische Verwaltungssichten für Diagnoseinformationen) und Extended Events liefern unterschiedliche Evidenz. Sie belegen jeweils nur ihren Scope; erst die konsistente Kette aus Zeitfenster, Parameterwert, Verteilung, Plan und gemessener Arbeit stützt eine Ursachenhypothese. Die referenzierte Änderung ist kein allgemeiner Tuningrat.

## Vorführbarer Kontrolllauf

Im [neutralen Query-Store-Kontrolllauf](Automated/README.md#neutrale-kontrollcaptures-vorführen)
lässt sich auf SQL Server 2019, 2022 und 2025 zeigen, wie dieselben vier
Suchaufrufe in zwei Zeitfenstern verglichen werden. Die Vorführung
konzentriert sich auf Ausführungszahlen, Pläne und Laufzeitprofile.
Der anschließende Teilnehmerpfad beschreibt die weitergehende Diagnose
einer möglichen Regression, die eine eigene Laufzeitfreigabe benötigt.

Für die Vertiefung stehen auf dem festgeschriebenen SQL-Server-2025-Build
zwei separat geprüfte Komponenten zur Verfügung. Die erste zeigt
Kompilierwert und Planwiederverwendung. Die zweite vergleicht
`OPTION (RECOMPILE)` mit der Baseline und prüft die Rücknahme.
Die [Vierer-Mix-Diagnose](Contracts/SQL_CAPTURE_PRODUCER.md#querylokale-mitigation-mit-rücknahme-prüfen)
zeigt für dieselben Parameterklassen die Lesezugriffe einzeln und in Summe.
Sie ist als Ergänzung zum Teilnehmervergleich auf dem festgeschriebenen
SQL-Server-2025-Build vorgesehen.
[Vertiefung zur Vorführung](Automated/README.md#vertiefung-mit-sql-server-2025)

## Voraussetzungen und Grenzen

Dies ist Schnitt B zu dem bestehenden, markergebundenen Adapter unter [`Scenarios/DGN-007`](../../../Scenarios/DGN-007/README.md). Der Adapter erzeugt Datenmodell sowie die Fenster `T0_BASELINE` und `T1_INCIDENT`; diese Skripte bauen keinen Ersatzdatenbestand auf und ändern weder `Scenarios/` noch globale Caches. Vor der Ausführung ist eine bestätigte isolierte Wegwerfinstanz erforderlich (`--confirm-isolated-lab`), mit mindestens 4 logischen CPU-Kernen, 8 GB SQL-Server-Speicher sowie Platz für Testdaten, Query Store und TempDB.

Benötigt werden Rechte auf die markierte Testdatenbank, Query Store und zum Verwalten/Lesen einer begrenzten serverseitigen XE-Session. Query Store muss in der Testdatenbank `READ_WRITE` sein, andernfalls lautet der kontrollierte Ausgang `SKIP_QUERY_STORE_REQUIRED`. Fehlen erfolgreich erfasste und phasengebundene T0/T1-Laufzeitprofile oder eine andere erforderliche Evidenzquelle, lautet der Ausgang `SKIP_EVIDENCE_MISSING`. Kein solcher Ausgang ist eine Evidenzbehauptung.

Query-Store-Waits und `MAX_DURATION` für XE werden vor Ort geprüft. PSP (Parameter Sensitive Plan Optimization; Planoptimierung für unterschiedliche Parameterwerte), OPPO (Optional Parameter Plan Optimization; Planoptimierung für optionale Parameter), Query Store Hints und Plan Forcing sind keine Voraussetzung und werden im Primärfall nicht verwendet.

Der bestehende manuelle Adapterpfad ist auf SQL Server 2025 mit Compatibility
Level 170 begrenzt. `40_Observation.sql` prüft den aktuellen Katalogwert vor
der ersten Evidenzausgabe; ein fehlender Wert oder ein anderes Compatibility
Level führt zu `FAIL_CONTRACT`. Die Adaptervalidierung lehnt dieselbe
Abweichung als `PROJECT_ASSERTION_FAILED` ab. Die oben genannten drei
Zielversionen gelten für das Design und die getrennten automatisierten
Teilschnitte; dieser Vorfix erweitert die Teilnehmerfreigabe nicht.

## Ablauf

1. Der Adapter bereitet die synthetische Datenbank `SQLPERF_LAB_DGN007_LOCAL` vor. Nur bei passenden vier Eigentumsmarkern ist sie ein zulässiges Ziel.
2. `00_Preflight.sql` prüft Version, Eigentumsmarker, Query-Store-Zustand und benötigte Rechte.
3. `20_Baseline.sql` dokumentiert T0 und T1 getrennt und richtet ausschließlich die begrenzte XE-Session für nachfolgende Vergleichsausführungen ein.
4. `40_Observation.sql` gibt die Evidenz in sechs Stufen aus. Bis zur sechsten Stufe enthält keine Ausgabe eine Lösungsempfehlung.
5. Erst nach der eigenen Hypothese wird `50_Mitigation.sql` ausgeführt. Es ersetzt nur die fest bekannte Suchprozedur durch eine querylokale `OPTION (RECOMPILE)`-Variante und sichert ihren Originaltext in der Testdatenbank.
6. `60_Comparison.sql` wartet begrenzt auf ein neues Query-Store-Intervall, erzeugt T2 mit denselben vier vorbereiteten Parameterklassen und prüft die Ergebnisgleichheit als bidirektionale Ergebnismenge. Auf den geprüften Builds vergleicht `PHASE_COMPILE_COST` T1 und T2 für dieselben vier Aufrufe in derselben Reihenfolge. Es zeigt Anzahl, CPU-Zeit und Dauer der erfassten Kompilierungen. Eine Positivkontrolle prüft den Messkanal jeder Phase. Unvollständige Kompilierevidenz erscheint als `COMPILE_EVIDENCE_MISSING`. Ausführungs-CPU, Reads und Planwiederverwendung brauchen ihre eigenen Profilbelege.
7. Nach jeder Unterbrechung `90_Cleanup.sql` ausführen. Es stoppt/entfernt ausschließlich die deterministische XE-Session und stellt den gespeicherten Originaltext der Prozedur wieder her. Der Adapter-Cleanup entfernt danach die markierte Datenbank.

Es gibt absichtlich kein freigegebenes `manifest.json`: Die fachliche Demo ist noch nicht runtimevalidiert und darf daher weder in den Laufkatalog noch in den zentralen Ausführungsleitfaden aufgenommen werden. Die Phasen sind manuell gegen den vom Adapter vorbereiteten Zustand auszuführen. Der getrennte [automatisierte Datenmodell-Schnitt](Automated/README.md) besitzt ein eigenes `setup.manifest.json` für Preflight, synthetischen Aufbau, Datenassertion und Cleanup auf den Zielversionen 2019/2022/2025. Dieser Schnitt verwendet den separaten Run-Token `AUTO` und belegt noch keine Incident- oder Capstone-Abnahme.

## Evidenzstufen und Hypothesenblatt

Der getrennte [prospektive Reproduktionsvertrag](Contracts/README.md)
legt gemäß `DEC-068` (Prospektive Duration- und Kontrollseparation für DGN-007 festlegen) die spätere Duration-/Kontrollseparation und den
zusätzlichen Plan-oder-Reads-Profilzweig fest. Seine reine Bewertungslogik
und synthetischen Fixtures sind eine statische Voraussetzung. Sie verändern
weder den Teilnehmerpfad noch die neutralen SQL-Captures und belegen keine
Incident-Runtime-Abnahme. Der
[Live-Befund der kontrollierten Lifecycles](Contracts/README.md#live-befund-aus-den-kontrollierten-lifecycles)
belegt das Reproduktionsprädikat auf allen drei Engines. Die
Ursachen- und Mitigationsabnahme bleibt offen.

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

Prüfen und verwerfen Sie mindestens zwei der ersten drei Hypothesen anhand
der im passenden Scope erwarteten Signale. Ein Signal darf nur dann als
ausgeblieben eingeordnet werden, wenn dieser Scope vollständig beobachtet wurde.

Für diesen Vergleich weist Stufe 3 die Query-Store-SET-Kontexte mit den
zugehörigen Ausführungszahlen aus. Stufe 5 zeigt die Differenzen der
Sitzungszähler für `RESOURCE_SEMAPHORE` und `PAGEIOLATCH_*` um jeden der
acht vorgesehenen Suchaufrufe. Die Stichprobe umfasst den Suchaufruf
und die ihn umgebenden Sitzungsabfragen. Ein `WAITFOR` vor T0 prüft
den Messkanal. Bei fehlender Positivkontrolle, rückläufigen Zählern oder
einer unvollständigen oder abweichenden Requestliste erscheint
`WAIT_EVIDENCE_MISSING` statt einer Nullmessung. Die phasenbezogenen
physischen Lesezugriffe stammen aus den gespeicherten Plan- und
Intervallschlüsseln. Sie erscheinen nur, wenn die erfassten
Ausführungszahlen für jeden Schlüssel übereinstimmen. Je Hypothese gilt
der beobachtete Statement- oder Sitzungsausschnitt.
[Microsoft-Referenz zu Sitzungs-Wait-Zählern](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-session-wait-stats-transact-sql?view=sql-server-ver17).

Eine leere XE- oder Wait-Sicht widerlegt nichts ohne nachgewiesene Session, Predicate, Eventklasse und Zeitfenster.

## Erwartete Resultate und zulässige Abweichungen

T0, T1 und T2 bleiben getrennte Zeitfenster und Query-Store-Intervalle. Die Query-Store-Abfragen sind auf `dbo.usp_CaseSearch` und den Marker `DGN007_CASE_SEARCH` gebunden. Die Ausgaben verwenden keine festen Millisekunden, Plan-Node-IDs, universellen Operatorerwartungen oder Mindestplanzahl. T0 und T1 führen denselben Viererparameter-Mix mit unterschiedlicher erster Suchparameterreihenfolge aus; die tatsächlich erfassten erfolgreichen Runtimeprofile sind an die gespeicherten Phasen und Intervalle gebunden. Plananzahl und Profile beschreiben die verfügbare Evidenz, sind für sich kein Incident- oder Ursachenbeleg. Die in Stufe 5 gezeigte XE-Sitzung startet nach T1. Ihre Ereignisse betreffen nachfolgende Aufrufe. Die separate Kompiliermessung in T1 und T2 verwendet eigene, auf die jeweilige Messsitzung begrenzte Aufnahmen. Planwahl, absolute Dauer, XE-Ereigniszahl und Query-Store-Flush sind empirisch. Fehlende geeignete Evidenz beendet die Bewertung mit einem dokumentierten `SKIP` statt mit einer Ursachenbehauptung.

## Cleanup und Recovery

`90_Cleanup.sql` ist idempotent: Ohne gespeicherten Originaltext erfolgt keine Prozeduränderung; bei passenden Datenbankmarkern wird nur die lokale XE-Session entfernt. Ein Datenbank-Drop ist nicht Bestandteil dieses Ordners und bleibt beim bestehenden markergebundenen Adapter-Cleanup.

## Statische Prüfung und Statusgrenze

Der [Lab-Harness](../../../Tests/Lab/Invoke-DGN007StaticParticipantFlowTest.ps1)
wurde auf einer frischen Podman-Labinstanz mit dem unveränderten
`SQL_Server_Lab`-Stand `ca170c119c4b` ausgeführt. Adapterinstallation,
Validierung und alle sechs Teilnehmerstufen bis T2 und Recovery bestanden.
`Remove-SqlServerLab` meldete `REMOVED`. Eine getrennte Inventarabfrage
fand unter der Lauf-ID keine Container, Volumes oder Netzwerke.
Der Harness meldet Produktversion und Kollation aus der eigenen Instanz
sowie Stufenstatus und Fehlernummern. Die Rohresultate bleiben lokal.
Der Lauf belegt den vorhandenen Teilnehmerablauf über den Lab-Einstieg.
Die integrierte Bewertung der Alternativhypothesen und Kompilierkosten
steht für die Incident-Abnahme weiterhin aus.

Die lokale Korrektur wurde statisch und im nicht-promotenden Teilnehmerablauf auf einer frischen Docker-Instanz mit SQL Server 2025 geprüft; sechs SQL-Stufen sowie Adapter- und Teilnehmer-Cleanup bestanden. Das ist weder vollständige Runtime-Matrix noch Incident-/Ursachenabnahme oder `VALIDATED`-Freigabe. Die Bestätigungsmatrix und Capstone-Qualifikation bleiben offen; die menschliche Generalprobe ist ausgeschlossen.

Die begrenzten Compatibility-Gegenproben laufen mit
`python Tests/Static/test_dgn007_compatibility.py`. Acht Tests prüfen die
extrahierten Katalogabfragen und Guard-Prädikate einschließlich NULL,
fehlender oder fremder Katalogzeile und falschem Compatibility Level.
Mit `--container NAME --confirm-disposable-instance` prüft derselbe Test
zusätzlich T-SQL-Guard- und Kontextfixtures auf einer leeren Developer-
Wegwerfinstanz mit SQL Server 2025. Der Compatibility-Wert der
Kontextprojektion und die fehlende Zielzeile stammen dabei aus dem echten
Katalog in `master`; die
Query-Store-Optionen für die Kontextprojektion sind ein synthetisches Fixture,
da `master` in diesem Lauf keine passende Optionszeile lieferte.
Das prüft weder eine tatsächliche Änderung des Compatibility Levels noch den
vollständigen Adapter- oder Teilnehmerablauf. Das Passwort kommt nur aus
`SQLCMDPASSWORD`; die Testinstanz wird anschließend vom Aufrufer entfernt.

## Quellen und Traceability

- `SRC-001` (Query processing architecture guide), `SRC-007` (Intelligent query processing), `SRC-027` (Monitor performance by using the Query Store), `SRC-028` (Performance monitoring and tuning tools), `SRC-031` (Display an actual execution plan), `SRC-035` (sys.dm_os_wait_stats), `SRC-036` (sys.dm_os_waiting_tasks); Abrufdatum gemäß Quellenregister: 2026-07-26.
- Ergänzend `SRC-040` (Plan properties), `SRC-046` (Slow in the Application, Fast in SSMS (SQL Server Management Studio; Verwaltungs- und Abfragewerkzeug)?), `SRC-047` (What is Parameter Sniffing in SQL Server?), `SRC-051` (Capturing Query Wait Stats with sp_HumanEvents); die Community-Quelle begründet nur Diagnosemethodik.
- `ADV-CLM-013` bis `ADV-CLM-015`, `ADV-CLM-034` bis `ADV-CLM-039`; `LO-M07-04`, `LO-M06-08`, `LO-M03-07`.
- Technische Korrektur der Compatibility-Evidenz, geprüft am 2026-10-06:
  [sys.databases](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-ver17) und
  [DATABASEPROPERTYEX](https://learn.microsoft.com/en-us/sql/t-sql/functions/databasepropertyex-transact-sql?view=sql-server-ver17).
  Der begrenzte Vorfix erzeugt keine neue Lehrinhaltsfreigabe.
