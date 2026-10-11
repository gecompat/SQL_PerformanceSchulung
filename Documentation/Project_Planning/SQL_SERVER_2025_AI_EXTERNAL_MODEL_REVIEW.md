# DGN-008 – private Offline-Metadaten- und Rechtevorbereitung

Stand: 2026-10-11. TSK-009, CUR-016/CUR-018/CUR-022. Basis
`8d3b074ddbfb4694f1d111ef41e56514da4a0391` für die private Vorbereitung. Der folgende
vollständige DGN-008-Offline-Slice ist IMPLEMENTED auf Basis
`eb203ed7f06abd3e52be2084fbc02e562eb3ecac`; Runtime-/Review-/Integrationsgate wird
unten getrennt geführt. Die private Vorbereitung ersetzt keine Demopaketabnahme.
Inferenz, Providerbetrieb, echte Credentialbindung und allgemeine Egresskontrolle
bleiben UNQUALIFIED. Die privaten Quellen liegen ignoriert unter Runtime.

## Tatsächlich ausgeführter Umfang

Auf einer eigenen SQL-Server-17.x-Instanz erzeugte der dbo-Labowner ein EXTERNAL MODEL
mit OpenAI/EMBEDDINGS, synthetischem Modellnamen und dem reservierten HTTPS-Ziel
`https://model.example.invalid/v1/embeddings`. CREATE wurde tatsächlich ausgeführt;
kein Embedding-/REST-Aufruf wurde ausgeführt. Das Objekt hat keinen Credentialbezug.
Die getrennte EndpointPolicy enthält nur den synthetischen Alias SYNTHETIC_NO_SECRET,
kein Secret und kein DATABASE SCOPED CREDENTIAL.

Ein WITHOUT LOGIN Reader hat genau CONNECT, SELECT auf der synthetischen Quelltabelle
und EXECUTE auf dem External Model. Vor-/Nachkontrollen binden sämtliche direkten
Rechte bytegenau und fehlende Rollenmitgliedschaften. HAS_PERMS_BY_NAME meldete 1
für EXECUTE: dies ist ausschließlich ein Metadatenbefund, kein tatsächlicher
Modellaufruf. Ein fest parametrisierter SELECT unter Reader lieferte tatsächlich
eine Zeile mit FactDays 7. Drei feste Gegenproben wurden tatsächlich verweigert:
CREATE EXTERNAL MODEL mit 262, UPDATE auf Quellen mit 229 und SELECT auf EndpointPolicy
mit 229. REVERT gilt im Erfolgs- und Fehlerpfad.

Die Anfangsbindung kontrollierte Name, dbo-Owner, HTTPS-Location, API-Format, Modelltyp,
Modellname, fehlenden Credentialbezug und genau ein External Model. Danach blieben
genau dieses Modell und kein CounterModel vorhanden. Quellen, Policyfixture,
Readerrechte und sämtliche konfigurierten/aktiven Hostoptionen blieben unverändert.
Ein vollständiger Nachvergleich sämtlicher External-Model-Metadaten ist damit noch
nicht attestiert. Vier vollständige bytegenaue Eigentumsmarker binden den DB-Abbau;
die eigene DB-Abwesenheit wurde unabhängig geprüft.

## Fehler, Korrektur und Cleanup

Der erste Versuch verwendete Docker network none. Trotz einzelner Readiness-Logtokens
erreichte die Loginprobe innerhalb von 180 Sekunden keinen Login; der SQL-Quelltext
wurde nicht erreicht. Eine spätere Loopbackdiagnose traf bereits den Containerabbau
und lieferte keinen SQL-Beleg. Der eigene Container wurde nach Ownerlabelprüfung
entfernt; ein Readiness-Timeout ist kein fachlicher SQL-PASS.

Eine kohärente Korrekturwelle erzeugte ein eigenes gelabeltes Docker-Netz mit
Internal=true, prüfte diesen Wert und den exakten Container-NetworkMode und verwendete
TCP-Loopback ohne veröffentlichte Ports. Der geänderte Versuch bestand Login,
Modellmetadaten, tatsächlichen SELECT und die drei Rechteverweigerungen:
`CREATE_262|UPDATE_229|POLICY_229|EXECUTE_PERMISSION_1`. Eigene DB, Container und Netz
waren anschließend separat nachgewiesen abwesend. Passwortübergaben verwendeten
ausschließlich Umgebungsvariablennamen, keine Passwortwerte in Prozessargumenten.
Internal=true ist kein allgemeiner DNS-/Egress-Sicherheitsnachweis.

Ein unabhängiger enger Quellenreview der privaten SQL-Probe und des Adapters fand
keine konkreten Befunde. Er führte keine eigene Runtime aus und ersetzt keinen
späteren Review des vollständigen Demopakets. Ein Implementierungsverantwortlicher,
ein erforderlicher Review und eine von maximal zwei Korrekturwellen bilden den
abgeschlossenen Vorbereitungsschnitt. Modell-/Tokenverbrauch des Orchestrators bleibt
unbekannt; die Probe erzeugt keine Tokens.

## Nächster zulässiger Schnitt

Das vollständige DGN-008-Offline-Paket benötigt getrennte Ingestion-/Retrievalrollen,
vollständig gebundene Modell-/Endpointpolicy-Metadaten, tatsächliche positive
SQL-Nutzung und Rechteverweigerungen sowie Grantreduktion, FWK-Phasen,
Versions-SKIPs, Ergebnis-/Markergegenproben und eigenen Cleanup. EXECUTE am Modell
bleibt bis zu einer gesonderten Providerfreigabe nur als Metadatenrecht qualifiziert.
CON-010 bleibt am FAIL-Checkpoint; Live-Lab-RAG bleibt am DEC-033-Secretgate.
Cloud-/Bezahl-, ONNX- und rote Hoständerungen sind weiterhin nicht freigegeben.

Am 2026-10-11 geprüfte Primärquellen:
[CREATE EXTERNAL MODEL](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-model-transact-sql?view=sql-server-ver17)
beschreibt CREATE-/EXECUTE-Rechte und HTTPS-Ziele;
[sys.external_models](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-external-models-transact-sql?view=sql-server-ver17)
beschreibt den Metadatenvertrag. Diese Dokumentation ersetzt die getrennten lokalen
Ausführungsbelege nicht.

## Vollständiger Offline-FWK-Slice

Die Dokumentvorbereitung wurde durch [PR 142](https://github.com/gecompat/SQL_PerformanceSchulung/pull/142)
abgeschlossen: sieben Headprüfungen auf `85a2114a30c9027e614745cf1087f660474d9000`
und fünf Main-Workflows auf Squash `eb203ed7f06abd3e52be2084fbc02e562eb3ecac`
bestanden. Vollständiger Tree `ed243662d98d80a26603120e3b8a994b187df53f`, main-
Synchronisierung und eigener lokaler/remote Branchabbau wurden geprüft.

Eine neue begrenzte Metadatenprobe vor dem vollständigen Slice beantwortete die
neue Setuprollenfrage: ein WITHOUT LOGIN Setupbenutzer mit CREATE EXTERNAL MODEL
über seine eigene Rolle erstellte tatsächlich das Modell und wurde dessen Owner.
Der Katalog meldete OpenAI, Modelltyp 1/EMBEDDINGS, NULL Credential/Parameters;
das Modell-EXECUTE-Securable hat Klasse 110/EXTERNAL_MODEL. Vier volle Marker,
unabhängige DB-Abwesenheit sowie eigener Container-/Netzabbau bestanden. Die vom
privaten Helper zunächst geerbte Zusammenfassungszeile behauptete irrtümlich auch
Reader-/Denialbelege; sie wurde korrigiert und ist keine Evidenz dieser neuen Probe.
Maßgeblich sind ihre eigenen ROLE_MODEL_METADATA-/ROLE_MODEL_PERMISSION-Zeilen und
SETUP_CREATE/DB_ABSENT/INFERENCE_NOT_RUN. Kein unveränderter Retry wurde ausgeführt.

Das vollständige Paket trennt drei eigene Datenbankrollen und drei WITHOUT LOGIN
Benutzer. Setup besitzt nur das CREATE-External-Modelrecht über seine Rolle und
erstellt das Offline-Modell unter dieser Identität. Ingestion besitzt SELECT/UPDATE
auf der synthetischen Source und das Modell-EXECUTE-Metadatenrecht. Retrieval besitzt
Source-SELECT und initial bewusst zusätzliche SELECT-EndpointPolicy-/Modell-EXECUTE-
Grants. MITIGATION nimmt ausschließlich diese beiden zusätzlichen Grants zurück.
COMPARISON prüft den weiterhin tatsächlichen Source-SELECT mit einer 7-Tage-Row,
zwei tatsächlich erfasste Ingestion-UPDATE-OUTPUT-Rows 8/7 und den unveränderten
7-Tage-Nachzustand. Modell-EXECUTE wird nur über HAS_PERMS_BY_NAME geprüft, niemals
als tatsächliche Inferenz dargestellt.

Zwei tatsächliche unprivilegierte CREATE-Gegenproben müssen 262 liefern; Reader-
UPDATE, Ingestion-Policy-SELECT und reduzierter Reader-Policy-SELECT jeweils 229.
Vier vollständige Endpointstrings ergeben per Bytepolicy 1 Allow/3 Deny ohne echten
Abfluss. Kein DATABASE SCOPED CREDENTIAL wird erzeugt; der Alias ist reine synthetische
Tabellenfixture. Der dbo-Harness kontrolliert vor/nach die kanonischen vollständigen
Modellmetadaten einschließlich IDs/Zeitstempeln und NULL Credential/Parameters,
feste Source-/Endpointbytes, alle direkten User-/Rollenrechte, genau die erforderlichen
Rollenmitgliedschaften und unveränderte Hostoptionen. Er ist nicht an Queryrollen
freigegeben und enthält keine allgemeine Anwendungs-/Login-/Poolingabnahme.

Der erste vollständige 17.x-Versuch scheiterte in SETUP: mehrere Tabellenvariablen in
einer DECLARE-Anweisung und Subqueries direkt im PRINT-CONCAT waren ungültig; der
Policy-ELSE-Zweig wurde explizit geklammert. CLEANUP und unabhängige DB-/Container-/
Netzabwesenheit bestanden. Korrekturwelle 1 trennte die Tabellenvariablen, übernahm
die Counts in skalare Variablen und ergänzte zwei fehlende Guidebegriffe. Der geänderte
17.x-Versuch bestand zwei vollständige Lifecycles mit je neun Ergebnisassertions,
Setup-Idempotenz, 80 vollständige Markerabweichungen und zehn Resultgegenproben.

Jede semantische Gegenprobe startet mit frischem Setup und tatsächlich reduzierten
Grants, bevor sie eine Abweichung erzeugt: leere Source, falscher FactDays-Wert,
falscher Alias, nachgestelltes Endpointleerzeichen, veränderte volle ModelBinding-
Location, fehlendes Modell, zusätzliches Reader-UPDATE, zurückgegebenes Policy-SELECT,
zusätzliche Ingestion-Rollenmitgliedschaft oder fehlendes Ingestion-UPDATE. COMPARISON
muss jeweils 51003/FAIL_RESULT_CONTRACT liefern. Markergegenproben binden danach auch
vollständige Modell-IDs/Zeitstempel; ausschließlich der abstrakte Setup-Idempotenz-
vergleich normalisiert frisch erzeugte IDs/Zeitstempel. Alle eigenen DB-/Container-/
Netzabwesenheitsprüfungen bestanden. 15.x und 16.x bestanden je zwei SKIP_VERSION-
Lifecycles vor SETUP, ohne fachliche Assertions; unabhängige DB-Abwesenheit sowie
eigener Container-/Netzabbau bestanden. Dies ist kein Rechteruntime-PASS dieser Versionen.

Der erforderliche unabhängige Quellenreview des vollständigen stabilen Demopakets,
der neuen Runnerkontrollen und Registrierung fand keine konkreten P1/P2-Befunde.
Er führte keine eigene Runtime aus und gilt ausschließlich für den deklarierten
Offline-Metadaten-/Rechtefall. Keine weitere Reviewkette wurde gestartet.

Framework, sieben bestehende KI-Runner-Unitmethoden, 31-Demo-Pfadvalidator, 360-Lauf-
Katalogvalidator und 31-Demo-Leitfaden bestanden. 360 bezeichnet die geplante Matrix
aus zwei Providern, drei Versionen und zwei Wiederholungen, keine ausgeführten
360 Läufe und keinen Podmanbeleg. Der bisherige 22-Demo-Abnahmebestand bleibt erhalten.
Dieser Slice hat einen Owner, einen erforderlichen Review und höchstens zwei
Korrekturwellen; bislang ist eine verbraucht. Die vorhandenen drei KI-CI-Versionsjobs
werden um genau eine Demo erweitert; keine neue Reviewkette, kein Modellaufruf,
keine neue Automation oder Workflowregel. Modell-/Tokenverbrauch bleibt unbekannt.
