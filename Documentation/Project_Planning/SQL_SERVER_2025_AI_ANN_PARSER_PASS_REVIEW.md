# TSK-006 – bestandene einzelne Parser-/Previewdiagnose

Stand: 2026-10-11. Die ausdrücklich genehmigte
[Readinesswiederaufnahme](SQL_SERVER_2025_AI_ANN_READINESS_DECISION.md) bestand
als Syntaxdiagnose. Genau ein privater Kandidat, ein neuer eigener Container,
zwei unveränderte PARSEONLY-Aufrufe; keine Korrekturwelle nach Runtime.
IDX-011/IDX-012 bleiben PROPOSED, kein Indexbuild oder Suchlauf durchgeführt.

## Tatsächlicher Parserbefund

Das eigene SQL-17.0.5005.3-Image wurde durch vollständige Image-ID, CID und Owner
gebunden; Setup prüfte Build, EngineEdition 3 und Linux Ubuntu 24.04 vor DB-Erzeugung.
Eigene Loopbackinstanz mit vier CPUs/sechs GiB, CL170/SIMPLE, 256/64-MB-Dateilimits.
Vier vollständige bytegenaue Marker und genau eine persistente Previewbaseline 0.
Keine Vektordaten; ausschließlich die eigene Baseline-Row, kein Vector-Fixture/Index.

| Phase | Tatsächlicher Previewwert | Parsercode/Befund | Zustandsvergleich |
|---|---|---|---|
| Ausgangszustand, neuer eigener DB-Client | 0 | Code 1, Msg 343/Level 15: VECTOR-Objekttyp unbekannt | vor/nach identisch |
| eigener Enableclient, danach unabhängiger neuer DB-Client | 1 | noch kein Parseraufruf | ausschließlich Previewwert und zugehöriges Defaultflag geändert |
| gleicher fester Parsertext, frischer eigener DB-Client | 1 | Code 0, stdout/stderr leer: Syntax akzeptiert | vor/nach identisch |

Der [feste Parsertext](SQL_SERVER_2025_AI_ANN_PARSER_DECISION.md) referenzierte
bewusst die tatsächlich abwesende `lab.VectorFixture`. SET PARSEONLY prüft ohne
Kompilierung/Ausführung. Die positive Syntaxannahme belegt deshalb keine
Objektbindung, Indexgeneration, Indexnutzung, VECTOR_SEARCH, Recall oder Performance.

Sieben vollständige JSON-Snapshots wurden erhalten: je 107 Hostkonfigurationsrows,
41 DB-scoped-Konfigurationsrows, vier volle Marker, eine Baseline-Tabelle und zwei
Dateimetadatenrows. Alle erfassten Werte, Baseline-/Quellrows und die ausgewählten
sys.databases-Optionsfelder wurden vollständig verglichen; keine abgeschnittenen
JSON-Werte. Andere sys.databases-Metadatenfelder wurden nicht allgemein qualifiziert.
Tatsächliche Fixture-/Vectorindexabwesenheit bestand vor/nach beiden Parseraufrufen.

Die frühere kombinierte Enable-/DDL-Probe und diese frischen Clients haben
unterschiedliche Abläufe. Eine bestimmte Batch-/Sessionursache des historischen
343 ist damit weiterhin nicht isoliert kausal bewiesen. Die alten FAIL-Checkpoints
bleiben unverändert; der neue Parserbefund setzt ihre Budgets nicht zurück.

## Tatsächlicher Restore und Cleanup

Die eigene Recovery meldete `RESTORED_0` und `DROP_CONFIRMED` nach erneutem
Baseline-/Eigentumscheck und tatsächlichem Previewgleichstand 0. Ein weiterer neuer
SQL-Client bestätigte DB-Abwesenheit. Gebundener eigener Containerabbau und separate
Containerabwesenheit bestanden; zusätzlicher Präfixlookup nach Abschluss ebenfalls
leer. Gemeinsamer separater Cleanup: **12,715 Sekunden**, keine Cleanupfehler.
Prozesscode 0; `PASS|CALLS_2|SYNTAX_ONLY_NO_INDEX_OR_SEARCH` ist erhalten.

## Quellen-/Reviewgrenze

Drei betroffene lokale Readiness-/Optionsfixtures bestanden. Die tatsächlich
erhaltene Windows-TCP-Meldung mit einer Punktfortsetzung wurde kontrolliert angenommen;
ungebundene/doppelte Punktzeilen, unbekannte Zusatz-/SQL-/Clientmeldungen und
streamübergreifende Fortsetzungen wurden abgelehnt. Der enge unabhängige
Ausführungsdeltareview fand keine P1/P2. Unveränderte Parser-/Snapshot-/Marker-/
Helperanalyse wurde tatsächlich wiederverwendet; keine erneute Vollanalyse.

| Private Quelle | SHA-256 |
|---|---|
| qualify_parser.py | CE4A8D971467FD58DD88899E45B9B2FA53EE20D70B12AF929E8152C0AB599478 |
| test_parser.py | 19938500DE307B61780AB67AA1C330FD11009F02E2729C8E1321505191DD7441 |
| lifecycle01.log | B2EA02596EC1A0EA5095629A31D11D998EAF574794D1E2E725A0B6F31B050AF6 |

Ausgeführte historische Quellen bleiben unverändert. Ein Owner, ein erforderlicher
Reviewer; Modell-/Tokenverbrauch unbekannt. Der einzelne Diagnoseumfang ist
verbraucht und wird nicht erneut ausgeführt. Ein tatsächlicher
[ANN-Build-/Suchumfang mit DB-scoped-DOP-Pfad](SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md)
benötigt einen neuen ausdrücklichen Budget-/Effektentscheid.
