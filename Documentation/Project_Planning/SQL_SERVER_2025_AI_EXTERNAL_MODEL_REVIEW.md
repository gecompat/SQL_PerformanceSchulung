# DGN-008 – private Offline-Metadaten- und Rechtevorbereitung

Stand: 2026-10-11. TSK-009, CUR-016/CUR-018/CUR-022. Basis
`8d3b074ddbfb4694f1d111ef41e56514da4a0391`. DGN-008 bleibt PROPOSED;
dieser abgeschlossene Vorbereitungsschnitt ist kein vollständiges FWK-Demopaket.
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
