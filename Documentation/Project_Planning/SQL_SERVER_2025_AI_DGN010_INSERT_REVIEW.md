# DGN-010: begrenzte Owner-INSERT-/Rollbackmessung

Status: PROPOSED; private begrenzte Native-INSERT-/Rollbackbeobachtung PASS,
keine vollständige TP-PERF-Abnahme.

## Vorgänger, Umfang und Budget

[PR 198](https://github.com/gecompat/SQL_PerformanceSchulung/pull/198) ist mit
Head7/Main5 PASS, ganzer exakter Treeübernahme, FF-main und eigenem lokalem/
Remotebranchcleanup abgeschlossen. [Tatsächliche Reader-Indexnutzung](SQL_SERVER_2025_AI_DGN010_USAGE_REVIEW.md)
bleibt auf sechs einzelne Queries begrenzt; tatsächliche Readerpläne und
Indexnettonutzen sind weiterhin offen. Öffentliche Producer unverändert WARN.

Die unmittelbar nächste zulässige Frage unter TSK-011/CUR-021 misst Owner-INSERT
mit OUTPUT und tatsächlichem per-INSERT-Rollback ohne/mit eigenem Candidateindex.
Eine Zehnergruppe Id1001–1010/Value=Id*3/Payload100F wird eingefügt und vor dem
nächsten INSERT tatsächlich vollständig zurückgerollt. Originalsource1000 bleibt
nach jedem Statement erhalten; kurzzeitig höchstens1010 Source-Rows, kein
anhaltendes Wachstum. Kein Commit, kein Buildkosten-/Worker-/Plan-/Nettonutzenclaim.

Sechs geänderte zusammenhängende Kandidaten/maximal zwölf serielle neue eigene
Container, zwei stabile volle positive Lifecycles erforderlich; Checkpoint3,
hard6. Historische Fehler erhalten, kein Reset; neue Versuche nur bei geänderten
relevanten Nativeinputs oder neuer Evidenz. Keine neue gewöhnliche lokale
Freigabefrage, keine zusätzliche unveränderte grüne Wiederholung. Ein Owner und
der vorhandene unabhängige Reviewer ausschließlich für neue konkrete INSERT-/
Rollback-/OUTPUT-/Source-/Attributionsrisiken; keine Reviewkette. Modell-/
Tokenverbrauch unbekannt, kein behauptetes Account-/Geldbudget.

## Unveränderte Safetyfloors und neue tatsächliche Oracles

Fixes bereits verfügbares SQL-17.0.5005.3-Image, aktueller öffentlicher Versions-/
Editions-/Permissions-/Bestätigungs-/DB-Abwesenheitspreflight, eigener Container
mit voller Owner-/CID-/Name-/Imagebindung und vier CPU (Central Processing Unit; Prozessor)/sechs GiB/Loopback.
Ausschließlich synthetische eigene Fixture und voller bytegenauer Viermarker-
DB-Guard. ENV-Passwort ohne -P. Keine Cloud-/Bezahl-/ONNX-/Host-/anderen Repoeffekte.

300 Sekunden Gesamtnormalbudget inkl Startup; einmalige gemeinsame60 Recovery
für guarded90/91, neue unabhängigeDB-Abwesenheit und eigenen CID-/Namensabbau.
Bekannter tatsächlicher Clientendstatus vor jedem Folgeeffekt; UNKNOWN bleibt
sticky und sperrt weitere SQL/Restoreversuche. Kein eigener zweiter Provisioner,
öffentliche bereits qualifizierte 00/10/20/21/22/24/90/91 werden direkt verwendet.

Neue feste private30_InsertWindow erzeugt zehn exakt bestimmte echte OUTPUT-Rows
je Ordinal, prüft tatsächliche Insertrowcount10 und Population im eigenen
1001–1010-Bereich, führt je Statement eigenen BEGIN/INSERT/ROLLBACK durch und
prüft danach tatsächliche Transaktionsdepth0/Abwesenheit. Vollständiges ursprüng-
liches 1000-Row-/Value-/Payload-Byteoracle vor/nach dem ganzen Fenster. Negative
Ergebniskontrolle verfälscht nur eigenes OUTPUT nach tatsächlichem Rollback und
muss vollständig51003/FAIL_RESULT_CONTRACT ablehnen. Separate echte Source-
Negativprobe über öffentlichen21/20 und tatsächlicher10-Restore. Kein Verwerfen
oder Übernehmen eines fremden Markers/Objekts und keine angenommene Rücksetzung.

Vollständiger tatsächlicher fünfteiliger Requestschlüssel, vier BIGINTcounter mit
exakten monotonen Differenzen, gleiche UTC-Zeitachse und je Ordinal vollständiger
Id/Value/Payload-SHA256-Digest. TransactionBefore/After0 und tatsächlicher
RollbackCount=Statements. Vollständige geordnete begrenzte Nativeframes/JSONkeys;
keine Counternullen für fehlende Werte. Reine separate private INSERT-Oracle-
Erweiterung statt Mutation gemeinsam genutzter öffentlicher SELECT/DMLcores.

Ein Einzelcontrol, zehn Warmups und18 AB/BA/AA-Messfenster zu100 INSERTs. Sechs
Baseline-, sechs Vergleichs- und drei AA-Paare; Warmups/AA separat, exakte
Dezimalmediane/alle Samples inklusive Nullen/Outlier bleiben sichtbar.1810
Warmup-/Messstatements und18100 volle Roworacles plus separatControl1/10Rows;
kein Mischen von Control und Benchmarksumme. Acht echte Create-/Droptransitions
und46 vollständige Source-/Reader-/Indexproben gebunden. Für jedes positive
Fenster vollständige13-Key-Stateaufnahme vor/nach (29Paare/58Aufnahmen), alle1000
Rows/configVarianttyp/fullBytes/NULL/files/metadata/rights/roles/properties
vollständig gleich. Candidate-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten) ausschließlich außerhalb der Messfenster.

Die Messintervalle enthalten OUTPUT, tatsächliche Row-/Abwesenheitsoracles und
je Statement BEGIN/ROLLBACK. Diese Prüf- und Rollbackkosten sind ausdrücklich
Teil der beobachteten Batchkosten; keine reine INSERTcpu, Commitdauer, gesamte
Worker-I/O (Input/Output; Ein- und Ausgabezugriffe) oder allgemeine Produktions-/Nettonutzenempfehlung. SYSrequestWrites0
beweist keine Log-I/O-Abwesenheit. Vollständige TP-PERF-/Modulabnahme offen.

## Verarbeitung und Abnahme

Acht reine neue INSERT-/Population-/Rollback-/Counter-/Scope-/Decimalgegenfälle
PASS; PureCLI--help ohneProvision. Enger unabhängiger Sourceabschluss vor Native
erforderlich. Aufnahme von Originalframes und vollständigen tatsächlichen
ausgeführten/importierten Sources unterRuntime/DGN010_INSERT, außerhalbGit;
nur datensparsame gebundene Zahlen/Fehler-/Cleanupaggregate werden veröffentlicht.
Keine öffentliche Producererweiterung und keine neue Demo-ID/IMPLEMENTEDzählung.

Nach geschlossenem Kandidaten aktuelle betroffene statische/Privacy-/Linkgates,
tatsächlich selektierte Head/MainWorkflows, PR→origin/main, ganzer Tree/FF und
eigener lokaler/Remotebranchcleanup. Danach nächste zulässige Kosten-/Planfrage.
Workstream/Heartbeat aktiv; allgemeine Entwicklung/DGN-007/andere Automationen
bleiben pausiert. Fehlende Commit-/Build-/Worker-/Readerplan-/Nettonutzen-/Modul-/
Lehrmaterial-/vollständige Runtimegrenzen bleiben wahrheitsgemäß offen.

Microsoft-Learn-Primärquellen, abgerufen2026-10-12:
[INSERT](https://learn.microsoft.com/en-us/sql/t-sql/statements/insert-transact-sql?view=sql-server-ver17),
[OUTPUT](https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql?view=sql-server-ver17),
[ROLLBACK](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/rollback-transaction-transact-sql?view=sql-server-ver17).
OUTPUT allein belegt keinen dauerhaften Insert/Commit; deshalb Native-
Transaktions-/Abwesenheits- und vollständige Sourceoracles unabhängig kontrolliert.


## Tatsächlicher Native-C1-Nachweis

Der stabile erste Kandidat bestand zwei neue eigene vollständige SQL-17.0.5005.3-
Lifecycles, Tokens FBFF95626B5D4922/9A106CC3A62A44FE. Je 153 tatsächliche
Nativecalls; insgesamt 58 positive Fenster, 3620 Warmup-/Mess-INSERTs plus zwei
separate positive Einzelcontrols. 36200 vollständige Benchmark-OUTPUT-Roworacles
plus 20 separate Controlrows, 3622 tatsächlich geprüfte positive Rollbacks.
92 volle Sourceproben/92000 Rows und 116 vollständige Stateaufnahmen/116000 Rows;
58 vollständige unveränderte Vorher-/Nachherpaare inklusive aller DB-/Datei-/
Config-Variantbytes/NULL/Metadata/Reader-/Rechte-/Rollen-/Property-/Sourcewerte.
Alle ursprünglichen Nativeframes an tatsächliche Sourcehashes und komplette
transportierte Ergebnisse rein gebunden; keine neue SQL-Ausführung für diese
Recordprüfung. Vier echte vollständige 51003/FAIL_RESULT_CONTRACT-Gegenframes,
Source-/OUTPUT-Negative tatsächlich abgewiesen und ursprüngliche Source erhalten.

Je Profil zehn Warmups, 18 AB/BA/AA-Fenster zu hundert INSERTs, sechs Baseline-/
sechs Vergleichssamples und drei AA-Paare. Mediane pro Hundert-INSERT-Fenster,
Warmups/AA ausgeschlossen; sämtliche Originalsamples/Range/Nullwerte/AA lokal
erhalten. Kein Durchschnitt über die beiden Profile und keine Signifikanzbehauptung.

| Profil | CPU ohne/mit (ms) | Logical Reads ohne/mit | Elapsed ohne/mit (µs) |
| --- | --- | --- | --- |
| 1 | 23.5 / 30.5 | 8958 / 15155.5 | 24686.5 / 36995.5 |
| 2 | 23 / 32 | 8957 / 15152.5 | 22608.5 / 39136 |

In diesen beiden begrenzten Profilen liegen die Candidate-Mediane für CPU,
Logical Reads und Elapsed höher. Das beobachtet INSERT-/OUTPUT-/Rowprüf-/
BEGIN-/ROLLBACK-Batchkosten unter den festgelegten Bedingungen. Keine reine
INSERTcpu, Commit-/Builddauer, gesamte Worker-/Log-I/O oder Gesamt-Nettonutzen-
qualifikation. Ergebnisse anderer Workloads, Datenumfänge und tatsächlicher
Readerpläne sind damit nicht attestiert; ein Seek allein belegt keinen Lesegewinn.

Originalsource1000 nach jedem Statement wiederhergestellt, kurzzeitig nur zehn
zusätzliche synthetische Rows; kein Commit. Acht kontrollierte Create-/Drop-
transitions außerhalb der Messfenster je Profil, Source-/Readerrechte unverändert.
Guarded90/91 sowie frisch unabhängige DB-Abwesenheit, voller eigener CID-/Name-
Cleanup bestanden; beide eigenen Container abwesend, kein UNKNOWN. Ein von sechs
Kandidaten verwendet, keine weiteren unveränderten grünen Wiederholungen.
Acht reine neue Gegenfälle und enger unabhängiger Review ohne offene P1/P2
bestanden; Modell-/Tokenverbrauch unbekannt, keine anderen Repositories verändert.

Dies ist PASS der begrenzten privaten INSERT-/Rollbackbeobachtung; öffentliche
Producer unverändert Gesamt-WARN, Runtime/TP-PERF/Indexnettonutzen NOT_ESTABLISHED.
Tatsächliche Readerpläne, Commit-/Build-/volle Workerkosten, vollständige Modul-/
Lehrmaterial-/Workstreamabnahme bleiben offen. Aktuelle selektierte Head-/Main-
Gates, PR/Integration, ganzer Tree/FF-main und eigener lokaler/Remotebranchcleanup
folgen. Danach unmittelbar nächste zulässige begrenzte Kosten-/Planfrage;
Workstream/Heartbeat bleiben aktiv.
