# DGN-010 – vollständige native Marker-Manipulationsqualifikation

Stand: 2026-10-12, TSK-011/CUR-021; DGN-010 bleibt PROPOSED.
Der [öffentliche Producer](SQL_SERVER_2025_AI_DGN010_PUBLIC_REVIEW.md) ist über
[PR 196](https://github.com/gecompat/SQL_PerformanceSchulung/pull/196) vollständig
integriert. Zehn Head- und acht Main-Workflows bestanden einschließlich tatsächlicher
Consumer-Matrix auf drei Engineversionen. Head 6d9ac26f69ac76f46ade8a094acb8225ce64e7b1,
Main 324c8ba21df182dddeb30c76e4947a793b84b022, ganzer Tree
224dce4178d6d28340657dbdab41c9aa9ffefb88 exakt übernommen; FF-Synchronisierung,
eigener lokaler und Remote-Branchcleanup abgeschlossen. Historischer C1-Editions-FAIL,
Gesamt-WARN und NOT_ESTABLISHED bleiben erhalten.

## Endlicher autorisierter Schnitt und Sicherheitsgrenzen

Sechs kohärente Quellenkandidaten, höchstens zwei neue eigene serielle lokale
SQL-17.0.5005.3-Container je Kandidat, zwölf insgesamt. Zwei vollständig positive
Lifecycles desselben stabilen Kandidaten erforderlich. Retry nur bei relevant
geändertem Nativeinput oder neuer tatsächlicher Evidenz; geschlossene FAILs bleiben
im gemeinsamen privaten Ledger. Keine unveränderten grünen lokalen Wiederholungen.
Ein Implementierungsverantwortlicher; ein vorhandener unabhängiger Reviewer nur
für neue Mutation-/Repair-/Frame-/Endstatus-/Parentrisiken und konkrete Closure.
Modell-/Tokenverbrauch unbekannt. Kein Provider-, Cloud-, ONNX-, roter Host- oder
anderer Repositoryeffekt; nur bestehende ausdrückliche lokale Wellenfreigabe.

Eigenes fixes Image, neue UUID-Namen, voller CID/Name/Image/Ownerlabel sowie
vier CPU/sechs GiB vor Abbau gebunden; Loopback und Passwort ausschließlich ENV.
1000 synthetische Rows, eigene DB SQLPERF_LAB_DGN010_LOCAL mit vier vollständigen
Unicode-Eigentumsmarkern. Keine DB-Preview-/MAXDOPänderung, keine fremde Adoption.
Regulär 300 Sekunden einschließlich Startup; eine gemeinsame Recoverydeadline
60 Sekunden einschließlich guarded Markerrestore, SQLcleanup/DB-Abwesenheit und
Container-/CID-/Namensabwesenheit. Unbekannter Clientendstatus bleibt sticky und
sperrt weitere SQLclients einschließlich Repair und Cleanup. Keine ungebundene
Rettung oder Deadlineerneuerung. Docker verwendet den unveränderten tatsächlichen
Remote-Waitframe aus PR196; ein lokaler Proxy-Poll reicht weiterhin nicht.

## Feste Abnahme

Jeder der vier Marker wird sechsfach tatsächlich verändert: fehlend, FOREIGN,
Wert mit angehängtem Leerzeichen, kompletter Originalwert plus 256 X, Name in
Kleinschreibung, Name mit angehängtem Leerzeichen. Alle acht markergebundenen
öffentlichen SQLphasen müssen je Abweichung genau einen vollständigen tatsächlichen
51004/FAIL_STATE-Frame zurückgeben: Setup, Probe, Delete, Database-ID, Candidate,
SELECT-, DMLfenster und Cleanup. Preflight wird nicht als Markerphase gezählt.
Damit 192 Abweisungen und 24 vollständige Restores je qualifiziertem Lifecycle.

Vor und nach jeder Abweisung wird ein vollständiger begrenzter Snapshot mit
allen 1000 Id/Value/Payload-Rows, DB-ID/Name/CL/Recovery, DB-Optionen, sämtlichen
scoped Configs und Dateigrößen/-limits/-growth, eigenem Schema/Objekten/IDs/Zeitwerten,
Index-/Spaltenmetadaten, Reader/SID/Rechten/Rollen und vollständigen ExtendedProperty-
Bytes verglichen. Keine reinen Bereichs-/Längen-/Präfixkontrollen. Die tatsächlich
abweichenden Marker werden vor Prüfung attestiert; Reparatur erfordert die drei
Originalmarker plus exakt die eigene erzeugte Abweichung und dieselbe DB-ID.
Jeder Restore muss die vollständige ursprüngliche Baseline wiederherstellen.
Source-/Readerprobe vor/nach der Matrix und neue unabhängige DB-Abwesenheit nach
guarded Cleanup bleiben Pflicht. Rawframes/Hashes/Admissionen ausschließlich privat.
Kein Vollruntime-/TP-PERF-/Indexnettonutzen-Claim aus dieser Markerqualifikation.

Vorreview korrigierte einen P2-Kwargfehler beim Recovery-Snapshot, kein Nativeeffekt.
Enger Quellenabschluss von Markerconsumer und Parent bestanden, bytegleiche Promotion
vor Admission. Neun reine Gegenfallmethoden bestanden nach zwei korrigierten
synthetischen Fixturesteuerungen; dieser reine FAIL bleibt getrennt erhalten.
Native Ergebnisse folgen erst nach tatsächlicher Ausführung.

## Verarbeitungsaufwand und CI

Eigene zwei Wiederholungen lokal qualifizieren denselben Quellenkandidaten; CI
verwendet seriell die drei bestehenden Instanzen, keinen zusätzlichen Container
je Marker. Nur SQL2025 führt einmal die komplette feste Markerabnahme aus;
SQL2019/2022 liefern read-only SKIP_VERSION vor Setup. Der neue eng ausgelöste
Step behält 300+60 Sekunden; Jobobergrenze 25 statt 15 Minuten lässt diesen
zusätzlichen begrenzten Nachweis samt Cleanup und bestehender Matrix zu.
PR196 belegt rund neun Minuten für die bisherigen SQL2025-Steps. Die Jobobergrenze
ist keine Erhöhung der lokalen Effekt-/Phasenbudgets und erlaubt keine Cancellation
mutierender Läufe. Höchstens sechs geänderte Sourcekandidaten, aktuelle Head-/Main-
Gates je Kandidat; CI verwendet höchstens 36 bestehende Matrixinstanzen insgesamt.
Ein gemeinsamer Wave-Checkpoint bei drei Kandidaten; nach sechs keine Admission,
nur erforderlicher Cleanup/FAIL-Checkpoint. CI-FAIL bleibt tatsächlich sichtbar.

Trigger nur eigener Runtimehelper, eigener Consumer, eigene reine Tests und bereits
betroffene Workflow-/Publicscope-Abhängigkeiten. Keine zweite Matrix, allgemeine
Suite oder Modellaufrufe je Negativfall. Geänderte Privacy vor Commit; zentraler
Vollprivacycheck am aktuellen Head/Main. Gleiche reine Tests nicht lokal wiederholen,
Logs deterministisch bounded auswerten, keine Review-/Receiptketten.

## Tatsächlicher C1-FAIL und gebundener C2

C1 Token DCA906D5E3904C8E erreichte tatsächliches PASS-Setup, keine Markerprobe.
Der Consumer wies den echten einzelnen USE-Infoframe auf stderr ab; kein
SQL-/Markerfehler und kein Performanceclaim. Qualifikation FAIL, sieben Nativecalls,
eigener markergebundener SQLcleanup und neue DB-/CID-/Namensabwesenheit bestanden,
Cleanup 12,712827 Sekunden, kein unbekannter Endstatus. Dieser geschlossene FAIL
bleibt im gemeinsamen Sechserledger; fünf Kandidaten verbleiben, kein Reset.

C2 ändert ausschließlich die positive Setupdiagnose: exakt der einzelne bekannte
Nativeframe zum Datenbankwechsel ist bei 10_Setup.sql/rc0 zulässig. Andere oder
gemischte Zusatzdiagnosen bleiben FAIL; 51004-Negativframes weiterhin vollständig.
Elf reine Gegenfallmethoden bestanden, einschließlich Known-Info und gemischtem
Info-/Fehlerframe. Neuer enger Deltaabschluss vor C2-Admission bestanden;
Marker-/Source-/Snapshot-/Deadline-/Cleanup-/Parent-/CIgrenzen unverändert.

## Tatsächlicher C2-FAIL und gebundener C3

C2 Token CA908C820F3743FF bestand Setup und volle Source-/Readerprobe, scheiterte
bei der ersten Snapshotabfrage mit tatsächlichem Msg 8114: eine scoped Konfiguration
enthält einen nvarchar-Wert und lässt sich nicht pauschal nach bigint konvertieren.
Zehn Nativecalls, null Markerproben, eigener markergebundener SQLcleanup und neue
DB-/CID-/Namensabwesenheit bestanden; kein unbekannter Endstatus. C1/C2 bleiben
geschlossene FAILs im gemeinsamen Ledger; kein Rücksetzen oder PASS-Umetikettieren.

C3 ändert ausschließlich die vollständige Konfigaufnahme: configuration_id,
Name/Defaultflag, primäre und sekundäre BaseType/Precision/Scale/MaxLength/Collation,
vollständige varbinary(max)-Wertbytes samt DATALENGTH; NULL bleibt separat erhalten.
Der neue reine Konfigbyte-/Typ-/NULLgegenfall bestand; elf unveränderte grüne
Controllerfälle nicht lokal wiederholt. Enger Deltaabschluss vor neuer Admission
bestanden. Snapshot-/Marker-/Source-/Deadline-/Cleanup-/CIgrenzen unverändert.
Dreier Wave-Checkpoint nach diesem Kandidaten; Sechsergrenze bleibt autorisiert.

Primärquellen, Abruf 2026-10-12:
[sys.database_scoped_configurations](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-scoped-configurations-transact-sql?view=sql-server-ver17)
definiert beide Werte als sql_variant;
[CAST und CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17)
beschreibt explizite Konversion nach großen Werttypen;
[SQL_VARIANT_PROPERTY](https://learn.microsoft.com/en-us/sql/t-sql/functions/sql-variant-property-transact-sql?view=sql-server-ver17)
definiert die separat erhaltenen Typmetadaten. Bytes werden ausschließlich innerhalb
desselben tatsächlichen Builds verglichen, kein versionsübergreifender Binärvertrag.

## Dreier Wave-Checkpoint: C3-FAIL und gebundener C4

C3 Token 9DDD496226A14E9E erfasste den vollständigen Konfig-/Row-Snapshot nativ:
176067 UTF-16-Einheiten in 881 vollständigen Frames, keine Trunkierung,
1000 Source-Rows und 41 Konfigurationen mit vollständigen Variantbytes.
Qualifikation FAIL am fehlenden Rollenkey: die tatsächlich leere Rollen-Subquery
wurde NULL und vom äußeren FOR JSON ausgelassen. Zehn Nativecalls/null Markerproben,
eigener SQLcleanup und neue DB-/CID-/Namensabwesenheit bestanden, Cleanup
13,0374421 Sekunden, kein unbekannter Endstatus. Drei unverändert erhaltene
geschlossene FAILs; C4–C6 sind weiterhin autorisierte neue Quellenkandidaten,
höchstens zwei lokale Container je Kandidat, kein Budgetreset.

C4 stellt die leere Rollenliste ausdrücklich als [] dar. Die vollständig begrenzte
Snapshotaufnahme verwendet UTF-16-Hexbytes je 200-Einheiten-Chunk, tatsächliche
Gesamtlänge/Ordinals und vollständige Reassemblierung vor JSON. Damit bleiben auch
Leerzeichen an Chunkgrenzen trotz nativer -W-Ausgabe erhalten. Grenze 200000
UTF-16-Einheiten hält den gesamten Nativeframe unter dem unveränderten 1-MB-Limit.
Ein neuer reiner Leerzeichen-/Hex-/Emptyarrayfall ergänzt die Typ-/NULLgegenfälle;
wegen tatsächlich geändertem Snapshotcodec werden dessen Controllerfälle geprüft.
13 reine Codec-/Controllerfälle PASS. Enger Capture-Deltaabschluss vor C4-Admission
bestanden; kein neues Effektbudget.
Dieser dokumentierte Checkpoint gestattet weitere geänderte Inputs innerhalb
der bestehenden Sechsergrenze und wahrt die ursprünglichen Fehlernachweise.

## Nächste Abnahmegrenze

Integration erst nach den aktuellen Head-/Main-Gates, ganzen Tree-/FF-Nachweisen
und eigenem Branchcleanup. Aktuelle Readerpläne/Indexnutzung, INSERT-/Commit-/Build-
und Worker-/weitere DMLkosten, harte Build-/DMLunterbrechung, vollständige TP-PERF-/
Lehrmaterial-/Modulabnahme bleiben offen. Danach nächste getrennte begrenzte
Frage zur tatsächlichen Readerplan-/Indexnutzung. Allgemeine Entwicklung und
DGN-007/andere Automationen pausiert; Heartbeat bleibt aktiv.


## Tatsächlicher C4-Nachweis und Wave-Checkpoint

Der stabile C4 bestand zwei neue eigene vollständige SQL-17.0.5005.3-Lifecycles,
Tokens 51335850D04844FA/02B1C9C49BF649B8. 982 tatsächliche Nativecalls; je 192 einzelne echte vollständige
51004/FAIL_STATE-Abweisungen über vier Marker/sechs Abweichungen/acht Phasen,
24 an die tatsächliche Abweichung gebundene vollständige Restores und eigene
Source-/Readerprobe vor/nach der Matrix. Keine akzeptierte fremde Fixture.

384 tatsächliche Negativframes, 482 vollständige Stateaufnahmen mit 482000
Id/Value/Payload-Rows und 4000 weitere Source-Proberows aus vier Nativeproben an
Originalframes und ausgewählte Sourcehashes gebunden. Die vollständigen State-
Aufnahmen erhalten alle DB-/Datei-/Config-/Objekt-/Index-/Spalten-/Reader-/Rechte-/
Rollen-/Propertywerte; alle 192 Vergleiche je Profil unverändert, 24 vollständige
Originalbaseline-Restores. Tatsächliche Text-Variantwerte inklusive vollständiger
Bytes/Typ/NULL und tatsächlich leere Rollenliste aufgenommen. Keine Trunkierung,
Byte-/Präfixverkürzung oder angenommene Defaults. Frisch unabhängige DB-ID und
Versions-/Editionsframe attestiert. Regular 300/Gesamtrecovery 60 Sekunden erhalten.

Alle fünf eigenen lokalen Container dieser Wave geschlossen, eigenes guarded
SQLcleanup sowie neue DB-/CID-/Namensabwesenheiten bestanden; kein UNKNOWN.
Die drei historischen C1/C2/C3-FAILs bleiben im selben Sechserledger erhalten.
Vier von sechs Quellenkandidaten verwendet; zwei verbleiben, kein Reset und
keine weiteren lokalen grünen Wiederholungen ohne neue Eingaben. Dreier-FAIL-
Checkpoint und nun vollständiger C4-Ergebnischeckpoint dokumentiert.

13 reine Codec-/Controllergegenfälle PASS; enger unabhängiger Marker-/Parent-/
CI-/Captureabschluss jeweils nur für neue konkrete Risiken, keine Reviewkette.
Echte native Markerqualifikation PASS als separater Sicherheitsclaim; öffentlicher
SELECT-/DML-Producer bleibt Gesamt-WARN, volle Runtime-/TP-PERF-/Indexnettonutzen-
Qualifikation NOT_ESTABLISHED, aktuelle Readerpläne/Indexnutzung weiterhin offen.
Modell-/Tokenverbrauch unbekannt; keine Provider-/Host-/anderen Repositoryeffekte.

Aktuelle Head-/Main-Gates mit tatsächlichem neuen Markerconsumer, PR/Integration,
ganze Treeübernahme, FF-Synchronisierung und eigener lokaler/Remote-Branchcleanup
folgen vor Abschluss. Danach separate tatsächliche Readerplan-/Indexnutzungsfrage;
Workstream und Heartbeat bleiben aktiv.
