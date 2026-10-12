# DGN-010 – synthetischen Indexrat anhand begrenzter Messungen prüfen

Status: PROPOSED, öffentliche Teilimplementierung für TSK-011/CUR-021.
Ein synthetischer Rat empfiehlt einen zusätzlichen INCLUDE-Index. Diese Demo
prüft getrennt ungezwungene Reader-SELECTs und Owner-UPDATEs mit tatsächlichem
Rollback. Vollständiger Indexnettonutzen, INSERT-/Commit-/Buildkosten,
aktuelle Readerpläne und vollständige TP-PERF-Abnahme bleiben offen.

## Lernziel und Aussage

Gleiche SELECT-Ergebnisse beweisen keine Beschleunigung; zusätzliche Indizes
verbrauchen Pages und verändern Schreibarbeit. A enthält ausschließlich den
Clustered Primary Key, B zusätzlich den eigenen Nonclustered Candidateindex
auf Id mit INCLUDE(Value,Payload). SELECT verwendet in beiden Zuständen dieselbe
parametrisierte Abfrage ohne INDEX-Hint. Es gibt keinen Nachweis, dass der
Optimizer den Candidate in jedem Fenster verwendet. UPDATE erhöht Value für
IDs 101–110 und nimmt jede Batchtransaktion wieder zurück. Sein Messfenster
enthält UPDATE-/OUTPUT-/Rollbackaufwand und isoliert keine Indexmaintenancekosten.

Keine Modell-/Provider-/Cloudaufrufe, keine automatische Übernahme von Advice
oder DDL außerhalb der eigenen synthetischen Datenbank. Der Rat ist eine feste
synthetische [Fixture](AdviceFixture.json), kein tatsächlicher LLM-Output.

## Voraussetzungen und Sicherheit

SQL Server 2025, genau 17.0.5005.3, Developer Enterprise, CL170.
Die Edition wird über die dokumentierte EditionID -2117995310 und EngineEdition3
gebunden; ein alter Anzeigename ersetzt diese Prüfung nicht.
2019/2022 liefern SKIP_VERSION vor Setup; andere Builds/Editionen
SKIP_CONFIGURATION. sysadmin ist ausschließlich für Aufbau, Owner-DMV-Abfragen,
Impersonation und Cleanup des isolierten Labs erforderlich. Die Readerquery
läuft als eigener Datenbankuser ohne Login, mit CONNECT und Source-SELECT,
ohne zusätzliche Rollen. Kein Minimalrechte- oder Mehrloginclaim.

YELLOW: ausdrücklich bestätigte neue wegwerfbare Instanz, vier CPU/sechs GiB,
freier Platz für begrenzte 256-MB-Daten-/64-MB-Logdateien und Client. Andere
Hostgrößen sind nicht qualifiziert. SIMPLE; MAXDOP und PREVIEW_FEATURES bleiben
unverändert0; jede feste Query und jeder Indexbuild MAXDOP1. 1000 deterministische
Rows, Id1–1000, Value=Id×3, je 100 F-Payloadbytes. Eine Session je nativer Phase,
300 Sekunden gemeinsames reguläres Budget, danach 60 Sekunden eigener Cleanup.
Hardwareabhängige Samples sind keine allgemeinen Grenzwerte.

## Ausführung

1. Eine eigene Instanz mit den genannten Grenzen bereitstellen. `sqlcmd` muss
   vorhanden sein. Passwort ausschließlich über SQLCMDPASSWORD; kein `-P`.
2. Vom Repositoryroot einen Scope ausführen; beide Flags bestätigen das
   isolierte Lastlab. Der Runner prüft Abwesenheit, Version/Edition/Rechte,
   baut nur SQLPERF_LAB_DGN010_LOCAL auf und bereinigt sie vor Rückgabe.

   ```powershell
   python Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/run_profile.py --server <eigener-lokaler-endpoint> --scope SELECT --confirm-isolated-lab --high-impact-confirmed --summary
   python Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/run_profile.py --server <eigener-lokaler-endpoint> --scope DML --confirm-isolated-lab --high-impact-confirmed --summary
   ```

3. `DGN010_AGGREGATE` zeigt ausschließlich begrenzte Zahlen, sämtliche sechs
   AB-/BA-Samples pro Zustand, Min/Max/Nullanzahl/exakten Mediantext und separate
   drei AA-Paare. Keine Rawqueries, Pläne, UTCs, Requestidentitäten oder Rows.
   Numerische FWK-011-Invarianten PASS; Gesamtstatus bleibt
   WARN_OPTIONAL_EVIDENCE_SKIPPED, Runtime-/TP-PERF-Abnahme NOT_ESTABLISHED.
   Ohne `--summary` wird kein Record exportiert; der Runner persistiert keine
   Rohdaten. FAIL/SKIP erhalten ihren tatsächlichen Grund.

## Phasen und Messgrenzen

Nach idempotentem Setup werden die vollständigen Source-/Config-/Readeroracles
geprüft. Die tatsächliche Löschung der eigenen Row1000 muss 51003 auslösen;
Setup stellt sie wieder her. Eine absichtlich falsche tatsächliche Query-/OUTPUT-
Row muss ebenfalls 51003 auslösen. Beide Gegenproben sind zusätzliche Requests.
Eine separate positive Einstatementkontrolle bindet die unabhängig gelesene DB-ID.

Je Zustand fünf Einstatement-Warmups, anschließend dreimal AB, BA und AA mit
je zwei Fenstern zu 100 Statements: zehn Warmups/18 Messfenster, 1810 vollständige
Statementoracles/18100 Rowkontrollen. 46 vollständige Source-/Indexaufnahmen
kontrollieren Id/Wert/Payloaddigest, tatsächliche Rows/used/reserved Pages,
Version/CL/Config und Readerrechte. Vier Build-/Dropzyklen liegen außerhalb
der Messfenster. AA und Warmups gehen nicht in AB-/BA-Mediane ein.

CPU/Reads/LogicalReads/Writes sind die Deltas derselben vollständigen nativen
Requestidentität vor/nach dem Batch, einschließlich Countergrenzen. UTC-Elapsed
umfasst für SELECT auch Impersonation und Buffertransfer/-löschung, für DML
BEGIN TRAN/UPDATE/OUTPUT/ROLLBACK. Vollständige Ergebnisoracles und JSONaufbereitung
liegen außerhalb. DML prüft jeden Ordinaldigest gegen Value=Id×3+Ordinal sowie
nach Rollback alle 1000 Source-Rows und Transaktionsdepth0. Coarse DMV-Startzeit
ist Identität; sie wird nicht mit datetime2-UTC-Grenzen geordnet. Keine individuellen
Querylatenzen, p95/p99, isolierten Worker-I/O-Kosten oder Signifikanzclaims.

## Cleanup und Recovery

Setup, alle Folgemutationen und Cleanup verlangen die vier vollständigen
bytegenauen Eigentumsmarker: Project, ContractVersion, DemoId, RunToken.
Vorhandene Datenbanken werden im Preflight abgewiesen. Ein Name allein reicht
niemals zum Drop. Nach gestarteter Setup-Phase versucht der Runner innerhalb
des separaten Budgets markergebundenen Cleanup und eine neue unabhängige
Abwesenheitsprüfung. Ein kontrollierter Fehler direkt nach PASS-Setup wird
separat als FAIL_EXECUTION mit nachgewiesenem Cleanup qualifiziert.

Nach Ctrl+C wird nur nach tatsächlich bekanntem sqlcmd-Ende SQLcleanup gestartet.
Bei unbekanntem Ende bleibt FAIL_CLEANUP sichtbar und es wird kein weiterer
SQLclient gestartet. Vor manueller Recovery müssen eigene Instanz und beendeter
Client eindeutig feststehen. Dann ausschließlich den markerprüfenden Cleanup
und anschließend die read-only Abwesenheitsprüfung ausführen:

```powershell
sqlcmd -S <eigener-lokaler-endpoint> -U sa -C -b -i Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/90_Cleanup.sql -v DemoId=DGN-010 RunToken=LOCAL TargetDatabase=SQLPERF_LAB_DGN010_LOCAL
sqlcmd -S <eigener-lokaler-endpoint> -U sa -C -b -i Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/91_Absence.sql
```

Native Markerfehler werfen 51004/FAIL_STATE; scheitert die Bereinigung, bleibt
das Gesamtergebnis FAIL_CLEANUP. Keine automatische Reparatur fremder Marker,
keine fremden Sessions/Container, kein harter Abbruch-/Recoveryclaim während
eines UPDATE-/Indexbuildfensters. Entsorgung der eigenen Instanz erfordert deren
separate vollständige Eigentumsbindung; dieser Demo-Runner provisioniert nichts.
Der eigene Dockeradapter bindet das tatsächliche Ende des nativen sqlcmd über
einen festen Shell-Waitframe an den Transportendstatus. Ein fehlender, doppelter
oder inkohärenter Frame sowie Timeout/Collectorabbruch sperren weitere SQLclients.
Ein beendeter lokaler Pythonproxy allein ist kein Remote-Endnachweis.

## Prüfung, Grenzen und Quellen

Reine Record-/FWK-Gegenfälle: `python Tests/Static/test_dgn010_benchmark.py`.
Controller-/Endstatusgegenfälle: `python Tests/Static/test_dgn010_profile.py`.
Native Consumer: `python Tests/Runtime/run_dgn010_profile.py --container <eigener-wegwerfbarer-container> --expected-major 17`.
Separate reine Marker-/Restore-/Framegegenfälle:
`python Tests/Static/test_dgn010_marker_controls.py`.
Separate native Markerqualifikation auf einer eigenen wegwerfbaren Instanz:
`python Tests/Runtime/run_dgn010_marker_controls.py --container <eigener-wegwerfbarer-container> --expected-major 17`.
Dieser feste Harness erzeugt nur die abwesende eigene DB, verändert jeden der
vier Marker sechsfach und verlangt über acht guarded SQLphasen 192 tatsächliche
51004-Abweisungen, vollständige unveränderte Source-/Metadatensnapshots sowie
24 vollständig gebundene Restores und eigenes Cleanup. SQL2019/2022 liefern
SKIP_VERSION vor Setup. Snapshotbytes werden vollständig als begrenzte
UTF-16-Hexframes transportiert; leere Rollen und primäre/sekundäre Variantwerte
einschließlich Typ/NULL bleiben erhalten. Ein mutierter Marker erlaubt nur die
an genau diese eigene Abweichung gebundene Reparatur. UNKNOWN sperrt weitere SQL.
Dieser Harness ist eine getrennte Abnahme des
[Marker-Teilnachweises](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md).
Zwei Lifecycles je Scope, erforderliche Versions-SKIPs und ein tatsächlicher
Setupfault je unterstütztem Scope werden separat kontrolliert. Aktuelle CI
prüft dieselben Profile. Ein Record-PASS ersetzt weder native Attestation noch
Cleanup, Version, Privacy oder aktuelle Head-/Main-Gates.

[Öffentlicher Auswertungsvertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_BENCHMARK_CONTRACT.md)
und [registrierter Demoentwurf](../../../Documentation/Demo_Catalog/SQL_SERVER_2025_AI_DEMO_DESIGNS.md)
bleiben maßgeblich. Abruf 2026-10-12, Microsoft Learn:
[CREATE INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver17),
[sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-requests-transact-sql?view=sql-server-ver17),
[ROLLBACK TRANSACTION](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/rollback-transaction-transact-sql?view=sql-server-ver17).
[SERVERPROPERTY/EditionID](https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver17)
ordnet -2117995310 vor 2025 Developer und ab 2025 Developer Enterprise zu.
Tabellevariable-OUTPUT bleibt nach Rollback erhalten; der Sourcezustand wird
unabhängig vollständig geprüft. Insert-/Commit-/Buildkosten, vollständige
Readerpläne, größerer Datenumfang und voller Indexnettonutzen bleiben offen.
Die separate Markerqualifikation erweitert ausschließlich den Sicherheitsnachweis.
Harte Unterbrechungen während DML/Build gehören nicht zum Claim dieses begrenzten
Producers; vollständige Runtime-/TP-PERF-Abnahme bleibt NOT_ESTABLISHED.


Die separate native Markerqualifikation bestand C4 zweimal mit 384 tatsächlichen
Abweisungen, 482 vollständigen unveränderten Stateaufnahmen und 48 Restores,
eigenem SQLcleanup und neu bestätigter DB-/CID-/Namensabwesenheit. C1/C2/C3-FAILs
bleiben dokumentiert. Dieser Sicherheitsnachweis erweitert keine Performance-/
Readerplan-/volle TP-PERF- oder IMPLEMENTED-Abnahme.

## Öffentlicher Kostencontroller – Nativequalifikation offen

Die zusätzliche feste Vorbereitung in `run_cost_profile.py` verbindet den
[Kostenrecordvertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_CONTRACT.md)
mit zwei eigenen CREATE-/DROP-Zyklen, echten Source-/DROP-Abwesenheitsnegativen,
vollständigen State-/Source-/Leasekontrollen und markergebundenem Cleanup.
Elf synthetische Controllermethoden, sieben Eingabemethoden und enger unabhängiger
Quellenreview bestanden. Dies ist kein Native-PASS dieses Kostencontrollers;
Version-/Fehlerlauf-/Owncontainerqualifikation folgt getrennt. Private früher
qualifizierte Buildkosten ersetzen keine öffentliche Controllerabnahme.

Der Runner provisioniert nichts und verlangt dieselben beiden YELLOW-Bestätigungen,
eigene isolierte SQL17.0.5005.3/Developer/CL170-Instanz und SQLCMDPASSWORD im Prozess-
Environment. Nur nach tatsächlichem Preflight/Setup/Negativen/Recordprüfung bleibt
das Ergebnis WARN; Runtime-/TP-PERF-/Worker-/Nettonutzen NOT_ESTABLISHED.
`--summary` gibt bei WARN und vollständig bestätigtem Cleanup nur Aggregate aus.

```powershell
python Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/run_cost_profile.py --server <eigener-lokaler-endpoint> --confirm-isolated-lab --high-impact-confirmed --summary
```

Alle Normalrequests teilen 300 Sekunden und Cleanup insgesamt weitere höchstens
60 Sekunden, beide durch Parentdeadlines verkürzbar. UNKNOWN sperrt weitere SQLclients
und erhält eigene exklusive SQLinputs unter Runtime; kein neuer SQLcleanup oder
stilles Entfernen dieser Inputs. Unlink-/Cleanupfehler bleiben FAIL_CLEANUP.
API-Rohrecords gehören ausschließlich in private Runtime-Evidenz. Kein eigener
Containerabbau durch den Demo-Runner; dieser braucht separate vollständige Eigentumsbindung.

Reine Controllergegenproben: `python Tests/Static/test_dgn010_cost_profile.py`.
Der [enge Controllernachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_CONTROLLER_REVIEW.md)
ist der konkrete Quellen-/Claimvertrag. DGN-010 bleibt PROPOSED.

## Getrennte Kosten-Gateprüfung

Der [Kosten-CI-Consumer](../../../Tests/Runtime/run_dgn010_cost_profile.py) prüft
zwei bounded WARN-Profile auf SQL2025, zweimal Versions-SKIP vorSetup auf2019/22
und eine2025Setup-Recovery. Der [Qualifikationsscope](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_CI_REVIEW.md)
unterscheidet aktuelle Head-/Main-Gates von früheren lokalen Entwicklungsläufen.
Keine volle Performance-/Workerkosten-/Nettonutzenabnahme; DGN-010 bleibt PROPOSED.
