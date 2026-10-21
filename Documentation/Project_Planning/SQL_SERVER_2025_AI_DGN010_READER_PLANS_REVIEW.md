# DGN-010: tatsächliche Pläne der ursprünglichen Reader-Abfrage

Status: PROPOSED; erste Readerplanwelle FAIL und sicher geschlossen,
keine vollständige TP-PERF-Abnahme.

[PR 199](https://github.com/gecompat/SQL_PerformanceSchulung/pull/199) ist mit
sieben Head- und fünf Main-Workflows PASS, vollständiger Treeübernahme,
FF-Synchronisierung und eigenem lokalem/Remote-Branchcleanup abgeschlossen.
Die [INSERT-/Rollbackbeobachtung](SQL_SERVER_2025_AI_DGN010_INSERT_REVIEW.md)
und [Reader-Indexnutzung](SQL_SERVER_2025_AI_DGN010_USAGE_REVIEW.md) bleiben
begrenzt; öffentliche Producer weiterhin WARN/NOT_ESTABLISHED.

## Umfang und korrigiertes Entwicklungsbudget

Unter TSK-011/CUR-021 werden drei ursprüngliche ungezwungene Reader-Abfragen
mit zehn Ergebnisrows im Ablauf PK (Primary Key; Primärschlüssel) → Candidate → PK aufgenommen. Der vollständige
öffentliche Querytext einschließlich Parametern 101/110 und MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) 1 bleibt
unverändert; DGN010_reader behält ausschließlich CONNECT und SELECT ohne Rollen.
Quelle: 1000 synthetische Rows mit vollständigen Value-/Payload-Byteoracles.

Sechs zusammenhängende Korrekturkandidaten, maximal zwölf serielle neue eigene
Container, Checkpoint nach Kandidat drei, harte Grenze nach Kandidat sechs.
Zwei stabile vollständige positive Lifecycles desselben Kandidaten erforderlich.
Historische Fehler bleiben erhalten. Retry nur bei geänderten relevanten
Nativeinputs oder neuer Evidenz; keine unveränderten grünen Wiederholungen.
Ein Implementierungsverantwortlicher und der vorhandene unabhängige Reviewer
für die neuen konkreten XE-Eigentums-/Abbau-/XML-/Zuordnungsrisiken.
Modell-/Tokenverbrauch unbekannt; keine behauptete monetäre Durchsetzung.

## Eigene begrenzte Effekte und Evidenz

Fixes bereits vorhandenes SQL-17.0.5005.3-Image, tatsächlicher öffentlicher
Versions-/Editions-/Rechte-/Isolationspreflight. Neuer eigener Container mit
voller CID-/Name-/Image-/Ownerbindung, vier CPU (Central Processing Unit; Prozessor), sechs GiB, Loopbackendpunkt,
ENV-Passwort ohne -P. Andere Repositories bleiben unverändert; keine Cloud-,
Bezahl-, ONNX- oder Hoständerung. Normalbudget insgesamt 300 Sekunden einschließlich
Startup, einmalige gemeinsame Recovery von 60 Sekunden einschließlich SQL-90/91,
frischer unabhängiger DB-Abwesenheit und eigenem Containerabbau. Tatsächlich
bekannter Clientendstatus erforderlich; UNKNOWN sperrt weitere SQL/Repair.

Neue kurzlebige serverbezogene XE-Sitzung ausschließlich in der eigenen neuen
isolierten Instanz. Ein sqlserver.query_post_execution_plan_profile-Ereignis,
Prädikat auf tatsächliche eigene Session-ID und DB-ID, Aktionen session_id,
database_id, sql_text und tsql_stack für die vollständige tatsächliche Queryzuordnung,
package0.ring_buffer mit MAX_MEMORY 1024 KiB und höchstens 20 Events.
Sitzung MAX_MEMORY 1024 KB, MAX_DISPATCH_LATENCY eine Sekunde,
MEMORY_PARTITION_MODE NONE, STARTUP_STATE OFF, MAX_DURATION 30 Sekunden.
Keine SHOWPLAN-Rechte, Traceflags, LAST_QUERY_PLAN_STATS oder Änderungen an
LIGHTWEIGHT_QUERY_PROFILING; keine QUERY_PLAN_PROFILE- oder INDEX-Hints.

Vorhandener Sitzungsname wird abgewiesen. Vollständiger Unicode-Name mit frischer
Nonce, tatsächliche event_session_id und komplette native Katalogdefinition aus
Sessions/Events/Actions/Targets/Fields bilden die gehaltene Eigentumsbindung.
sql_variant-Felder werden mit Typ und vollständigen Bytes erhalten. Vor jedem
DROP einschließlich Fehlerpfad: ursprüngliche DB-ID, alle vier vollständigen
bytegenauen Eigentumsmarker, voller Sitzungsname/native ID und exakt dieselbe
komplette Definition prüfen. Kein Adoptieren einer vorhandenen Sitzung und kein
ungeprüfter SQL-Rettungsabbau. Ungebundene Restobjekte führen zu FAIL und werden
nur durch vollständigen gebundenen eigenen Containerabbau entfernt.

Der Ringbuffer wird vor STOP/DROP gelesen. Native dropped_event_count und
dropped_buffer_count müssen tatsächlich null sein; XML (Extensible Markup Language; Format zur strukturierten Darstellung von Daten) truncated/droppedCount
müssen tatsächlich null sein, vollständige Eventpopulation/Frameordinale prüfen.
totalEventsProcessed muss der vollständigen Eventzahl entsprechen; fehlende oder
abweichende Werte sperren PASS, auch bei truncated=0/droppedCount=0.
XML/JSON (JavaScript Object Notation; strukturiertes Textformat) höchstens 220000 UTF-16-Einheiten und Nativeausgabe höchstens ein MB;
keine abgeschnittene Ausgabe oder fehlende Laufzeitcounter als PASS behandeln.

Exakter ursprünglicher SELECT-Textdigest, tatsächlicher fünfteiliger Request,
DB-ID, vollständige Zehnrow-Ergebnisdigests, Session-/DB-Aktionen, Ereigniszeit
innerhalb des Readerintervalls, tatsächlicher Build, Source-/Indexidentität und
echte RunTimeCountersPerThread mit zehn ActualRows/einer Ausführung erforderlich.
Genau ein passender SELECT-Plan; geschätzte Plancachepläne oder Owner-INSERT-Pläne
sind kein Readerplannachweis. Native Parameterwerte werden nicht aus geschätzten
Compiled-Werten abgeleitet; tatsächlicher fester Queryaufruf und Roworacle binden
die Parameter. Pläne beweisen keine allgemeine Performance- oder Nutzenwirkung.

Je Query vollständige 13-Key-Stateaufnahme vor/nach mit allen 1000 Rows,
Config-Variant-/Datei-/Objekt-/Rechte-/Rollen-/Propertybytes, unverändert erforderlich.
Neun Sourceproben, sechs Stateaufnahmen und zwei kontrollierte Candidate-DDL-
Transitions außerhalb der Readeraufnahme. Echte Source- und Ergebnisnegative
müssen jeweils 51003/FAIL_RESULT_CONTRACT ablehnen; Source tatsächlich herstellen.
Sitzungsabbau wird nativ festgestellt; DB-90/91 und frische unabhängige DB-/
Container-/CID-Abwesenheit schließen jeden positiven Lifecycle.

Zwölf neue reine Plan-/Frame-/Loss-/Runtime-/Fremdsource-/Leasegegenfälle PASS;
CLI --help ohne Provision PASS. Enger unabhängiger Sourceabschluss vor Admission
ohne offene P1/P2. Zwei konkrete Befunde wurden vor dem ersten Nativecall behoben:
Root10 zusätzlich zum Source10 und vollständige verarbeitete Ringpopulation.
Der Reviewer führte keine Nativeausführung durch; Syntax, Format und tatsächliche
Readerpläne sind durch die folgenden lokalen Admissions nachzuweisen.
Originalframes und vollständige tatsächliche Sourcehashes bleiben privat unter
Runtime/DGN010_READER_PLANS. Veröffentlichung nur datensparsame Aggregate.
Der private Diagnoseschnitt weicht begründet von den Referenzvorlagen
FWK-005/FWK-007 ab: Lightweight-XE statt SET STATISTICS XML erhält die tatsächlichen
Readerrechte; der Noncename ergänzt den Demo-/Runbezug und verhindert Adoption.
Die ausdrücklich autorisierte lokale Entwicklungswelle umfasst diese synthetische
Diagnoseaufnahme. Private XML-Exporte werden separat mit Source-/Request-/Privacy-
Bindung geprüft; sie werden nicht versioniert. Vollständige DB-/Sitzungsbindung
vor jedem Abbau ersetzt keinen Guard durch eine Namensannahme. Öffentliche
Framework-Verträge und Referenzsession werden nicht verändert.
Planaufnahme getrennt von bisherigen Performance-Messungen: die hier zusätzlich
beobachteten Counter sind keine erneute Performance-Benchmarkqualifikation.

## Integration und Grenzen

Aktuelle betroffene Privacy-/Link-/Semantikprüfungen, tatsächliche Head-/Main-
Gates, PR → origin/main, vollständiger Treeabgleich, FF-main und eigener lokaler/
Remote-Branchcleanup. Danach unmittelbar nächste zulässige Kostenfrage.
Commit-/Build-/volle Worker-/Nettonutzen-/TP-PERF-/Modul-/Lehrmaterialabnahme offen.
18 Demoentwürfe und 9 IMPLEMENTED/9 PROPOSED bleiben unverändert. Workstream und
Heartbeat aktiv; allgemeine Entwicklung, DGN-007 und andere Automationen pausiert.

Primärquellen, abgerufen 2026-10-12:
[Query Profiling Infrastructure](https://learn.microsoft.com/en-us/sql/relational-databases/performance/query-profiling-infrastructure?view=sql-server-ver17),
[Extended Events targets](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/targets-for-extended-events-in-sql-server?view=sql-server-ver17),
[CREATE EVENT SESSION](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-event-session-transact-sql?view=sql-server-ver17),
[Sessionkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-server-event-sessions-transact-sql?view=sql-server-ver17),
[Feldkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-server-event-session-fields-transact-sql?view=sql-server-ver17).
Lightweight Profiling liefert äquivalente Actual-Pläne; der Ringbuffer verliert
seine Inhalte beim Stop und kann bei der XML-Konversion abschneiden. Daher sind
Aufnahme vor Stop, vollständige Laufzeitcounter und Verlustkontrollen nötig.
MAX_DURATION ist hier auf SQL Server 2025 beschränkt.

## C1: tatsächlicher Formatfehler und gebundene Korrektur

Erster Kandidat E61B7583E24B4997 nach 17 Nativecalls FAIL: genau ein vollständiger
Originalreaderplan war durch den Parser nicht zuzuordnen. Tatsächliche Ring-
population sechs/verarbeitet sechs, keine Drops/Verdrängung/Trunkierung. Die
Lightweight-Pläne haben native Root-/Source-Laufzeitrows, aber kein StatementText.
Der tatsächliche Readerplan hat DegreeOfParallelism=0 mit MaxDOPSetToOne, während
das Ereignis dop=1 meldet; Runtimeparameter int101/110 sind tatsächlich vorhanden.
Der ursprüngliche Parser erwartete StatementText und ausschließlich Plan-DOP1.
Keine angenommene erfolgreiche Planabnahme aus dem Fehllauf. Guarded90/91,
frische DB-Abwesenheit und voller eigener CID-/Namensabbau PASS; kein UNKNOWN.

C2 ergänzt die dokumentierte native sql_text-Aktion. Vollständiger Actiontext
muss der ursprünglichen festen Query entsprechen; ein vorhandener StatementText
muss zusätzlich übereinstimmen. Plan-DOP0 ist ausschließlich mit tatsächlichem
MaxDOPSetToOne und Ereignis-DOP1 zulässig; Root-/Source-Thread0 bleiben Pflicht.
Tatsächliche int-ParameterRuntimeValue101/110 erforderlich, Compiled-Werte sind
kein Ersatz. Tatsächlich beobachtete volle Session-/Prädikat-/Targetfeldbytes
werden jetzt zusätzlich streng ausgewertet. Effekte/Zeiten/Source-/Rechte-
Grenzen unverändert; keine neue Freigabefrage und kein Reset des C1-FAIL.

## C2: tatsächlicher Batchtext und gebundene Statementauflösung

C2-Token 6E7AC8D8F010494C nach 17 Nativecalls ebenfalls FAIL der eindeutigen
Originalqueryzuordnung. Tatsächliche sql_text-Aktion enthielt bei allen sechs
Events den vollständigen Batch, nicht den einzelnen SELECT. Ringpopulation
6/6, keine Drops/Verdrängung/Trunkierung; vollständiger eigener DB-/CID-/Name-
Cleanup PASS, kein UNKNOWN. Enger C2-Review bestand; das tatsächliche Format
blieb bis zur Nativeausführung unbewiesen. Beide FAIL-Lifecycles bleiben erhalten.

C3 ergänzt ausschließlich die dokumentierte tsql_stack-Aktion und liest den
SQLtext zu den tatsächlich aufgenommenen obersten Framehandles über
[sys.dm_exec_sql_text](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-sql-text-transact-sql?view=sql-server-ver17).
Native Stackhandle vollständig 64 Bytes, Byteoffsets/Fulltextgröße/-digest und
vollständiger extrahierter StatementText werden ordinalgebunden erhalten.
Keine Cachepläne oder deren geschätzte Rows werden verwendet. Der Native
sql_text-Batch muss zudem vollständig bytegleich dem tatsächlich gebundenen
festen SQL-Sourcebatch sein. Statementtext aus tatsächlichem Frame muss exakt
Originalquery sein; nur der damit gepaarte native SELECT-Actualplan mit wirklichen
Root-/Source10/Runtime101110 zählt. Keine Ersetzung durch einen ähnlich aussehenden
Ownerplan oder frei gelieferte Handles. Auflösung nach Aufnahme/STOP, vor eigenem
gebundenem DROP; bei fehlendem oder ungültigem Text FAIL/guarded Recovery.
Die interne XML-/JSON-Grenze wird von 180000 auf 220000 UTF-16-Einheiten erhöht,
weil der volle Batch mehrfach im tatsächlichen Target enthalten ist. 1100 feste
HEX-Frames bleiben einschließlich Rahmung/Window unter einem MB Nativeausgabe;
dieser äußere Cap bleibt unverändert. Keine stille Verkürzung/Ersetzung. Eigene
XE-Speicher-/Event-/Effect-/Zeit-/Source-/Readergrenzen unverändert. Kandidat drei markiert
den vorgesehenen Checkpoint; nach seinem sicheren Lifecycleabschluss wird der
tatsächliche Budget-/Befundstand festgehalten. Kein Budgetreset, maximal sechs.

## Checkpoint nach C3 und lokale C4-Korrektur

C3-Token 477003BA58F34CC0 FAIL mit tatsächlichem SQL-Fehler1934: XML-Methoden
verlangen QUOTED_IDENTIFIER ON; die Clientverbindung hatte diese Option nicht
gesetzt. Kein tatsächlicher Readerplan-PASS. Guarded90/91 und frische unabhängige
DB-Abwesenheit sowie voller eigener CID-/Namensabbau PASS, kein UNKNOWN.
Alle drei Kandidaten sicher geschlossen; drei von sechs Kandidaten verbraucht,
drei verbleiben. Kein Reset und keine neue gewöhnliche Freigabefrage.

C4 setzt ausschließlich QUOTED_IDENTIFIER ON in der eigenen temporären
Nativeverbindung vor XML-Methoden. Keine persistente DB-/Instanz-/Hostkonfiguration
und keine neuen Readerrechte. Gehaltene Stack-/Offset-/Frame-/Runtime-/Lease-
Oracles unverändert; der volle tatsächlich ausgeführte Batch wird mit dem neuen
Sourcebytevergleich gebunden. Korrigierter relevanter Nativeinput rechtfertigt
den neuen Kandidaten innerhalb des Sechserbudgets; keine unveränderte Wiederholung.

## C4: Handle-/Offsetguard und C5-Datentypkorrektur

C4-Token BB479F988F4148B6 nach 17 Nativecalls FAIL51003 am vollständigen
Stackhandle-/Offsetguard. Guarded SQLcleanup, frische DB-Abwesenheit und voller
eigener CID-/Namensabbau PASS; kein UNKNOWN. Der abgewiesene konkrete Frame wurde
nicht transportiert; seine genaue Länge/Offsetform ist dadurch nicht attestiert.
Vier von sechs Kandidaten verbraucht, zwei verbleiben; kein Reset.

## C5-FAIL und kohärenter C6-Korrekturkandidat

C5 (16DFE4DF75AD45A5) endet nach 17 Nativecalls mit FAIL bei der vollständigen
SQLtext-/Requestbindung. Guarded90/91 sowie unabhängige DB-/Namens-/CID-Abwesenheit
sind tatsächlich bestätigt; kein unbekanntes Clientende. Cleanup 16,16 Sekunden.
Die vollständigen sechs Nativeevents enthalten denselben Batch, aber ein
UTF-8-Kommentar wurde vom vorhandenen Client als zwei andere Unicodezeichen
übertragen. Die vollständige Bytebindung lehnt dies erwartungsgemäß ab.

Die vorhandene C5-Evidenz zeigt zusätzlich den vollständigen vorbereiteten
Abfragetext mit Parameterdeklaration: Die tatsächlichen Statementoffsets
44/254 schließen ausschließlich das abschließende Semikolon aus; vollständiger
Textumfang 258 Bytes. C6 verwendet einen ausschließlich ASCII enthaltenden
privaten Batch und bindet den extrahierten Originalreader an genau diese
vollständige Textlänge, Parameterdeklaration, SHA-256 und Nativeoffsets.
Keine allgemeine Textnormalisierung oder Aufweichung des vollständigen
SQLtextvergleichs. Originalquery, Rechte, Source-, XE-, Effekt-, Speicher-,
Zeit- und Cleanupgrenzen bleiben unverändert. Die tatsächlich beobachteten
Originalreaderparameter und Runtimezähler werden weiterhin vollständig geprüft.

Fünf von sechs Kandidaten sicher geschlossen und verbraucht; C6 ist der letzte
Korrekturkandidat dieses Schnitts. Vierzehn betroffene reine Tests bestehen.
Der Native-Nachweis zweier frischer stabiler vollständiger Lifecycles steht noch aus.

C5 korrigiert die unbelegte exakte 64-Byte-Annahme auf den dokumentierten
SQL-Datentyp varbinary(64): mindestens ein, höchstens 64 vollständige Bytes,
volle gerade Hexform, vollständige Rawlänge vor dem Cast und gleiche tatsächliche
Binärlänge danach. Keine stillen Padding-/Trunkierungs-/Aliasannahmen. Rawhandle
und geordneter Header bleiben bytegleich dem tatsächlichen XE-Stack gekoppelt.
Offset-/Query-/Plan-/Runtime-/Source-/Leasefloors unverändert. Bei erneutem
Guardfehler werden ausschließlich private gebundene Frameordinal-/Rawhandle-/
Längen-/Offsetdiagnosen ausgegeben, kein positives PASS. Fehlende konkrete
Formatevidenz wird nicht als kurzer Nativehandle ausgegeben. Zwölf reine Tests
einschließlich gültiger voller variabler Handles und falscher/überlanger/
ungerader/aliasbehafteter Handles PASS; enger Deltaabschluss vor C5-Admission.


## C6: geschlossener FAIL-Checkpoint der ersten Readerplanwelle

C6 (9577FCB01FA0466E) endet nach 17 Nativecalls mit FAIL: Die tatsächliche
XE-Ereigniszeit 2026-10-12T09:15:54.768Z besteht den bisherigen Vergleich mit dem
Readerintervall 2026-10-12T09:15:54.7684718 bis 2026-10-12T09:15:54.7684718 nicht.
Die vorliegenden Zeitfelder haben unterschiedliche Nachkommastellen; noch kein
akzeptierter tatsächlicher Originalreaderplannachweis und keine stabile
Zweiprofilqualifikation. Die vorangehenden vollständigen Source-/Request-/
Prepared-Text-/Stackoffsetkontrollen wurden tatsächlich erreicht.

Guarded90/91, frische unabhängige DB-Abwesenheit und voller eigener CID-/
Namensabbau sind bestätigt. Cleanup 13.46 Sekunden, kein
UNKNOWN. Alle sechs Kandidaten dieser Welle sind fehlgeschlagen, alle sechs
Container sicher abwesend; harte Sechsergrenze erreicht. Kein C7 in dieser
Welle, keine unveränderte Wiederholung und kein stilles Zurücksetzen.
Vierzehn betroffene reine Tests und enge unabhängige Quellenreviews ohne
offene P1/P2 ersetzen keinen Native-PASS. Modell-/Tokenverbrauch unbekannt.

Dieser konsistente FAIL-Checkpoint wird über PR integriert. Öffentliche
Producer weiterhin Gesamt-WARN, DGN-010 PROPOSED, vollständige TP-PERF-/
Nettonutzen-/Lehrmaterialabnahme NOT_ESTABLISHED. Aktuelle Head-/Main-Gates,
Integration, ganze Treeübernahme, FF-Synchronisierung und eigener lokaler/
Remote-Branchcleanup folgen. Danach unabhängige autorisierte Folienarbeit und
weitere konkrete Sourcekorrekturen ausschließlich mit sichtbarem Folgecheckpoint.
