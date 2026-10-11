# DGN-009 – manipulierte Quellen und Offline-Toolpolicy

Stand: 2026-10-11. CUR-018/CUR-022, TSK-009, TP-RUN.
Basis: `26461f9f9716da3e83f0a807c9e0d64acdf7a45e`, Branch
`codex/sql2025-ai-injection-preparation`. IMPLEMENTED; lokaler Runtime-/Review-/
Integrationsgate noch offen; lokale Versionsqualifikation und Quellenreview bestanden. DGN-008-External-Modelrechte und Livegeneration bleiben
getrennt offen; CON-010 bleibt mit FAIL am [Checkpoint](SQL_SERVER_2025_AI_TENANT_REVIEW.md).

## Tatsächlicher Kontrollumfang

Das FWK-010/FWK-011-Paket hat drei vollständig eingefrorene synthetische Dokumente:
aktuell/trusted, aktuell/untrusted mit CONTROL-/99-Tage-Anweisung und eine alte
widersprüchliche 9-Tage-Version. Identische VECTOR(3)-Werte erlauben eine begrenzte
exakte Cosine-Abfrage. Diese liefert tatsächlich die saubere und manipulierte Quelle;
die alte Quelle bleibt außerhalb der aktuellen Retrievalmenge. Content wird angezeigt,
aber nie zu ausführbarem SQL gemacht. Current/Trusted sind feste Ownermerkmale;
der Harness behauptet keine automatische Erkennung untrusted Contents.

Vier fest im Kontrollharness deklarierte Antwortfixtures liefern 1 akzeptierte und
3 abgelehnte Fälle: Claim 99 mit sauberer Citation, Claim 7 aus untrusted Quelle und
Claim 9 aus veralteter Quelle werden abgelehnt. Die Entscheidung bindet die tatsächlich
retrievte aktuelle vertrauenswürdige Quelle und ihren festen FactDays-Wert. Vier feste
Toolfixtures liefern 1 erlaubten / 3 abgelehnte Versuche. Die vollständige Byteallowlist
erlaubt ReadFact auf Quelle 1; GrantControl, ReadFact auf untrusted Quelle und der
Leerzeichenname bleiben abgelehnt. Nur ReadFact führt festes SQL mit separatem int-
Parameter unter dem eingeschränkten Reader aus und muss tatsächlich 7 Tage liefern.

DGN009_reader hat WITHOUT LOGIN genau CONNECT und SELECT auf lab.Documents,
DGN009_sink nur CONNECT. Feste GRANT CONTROL- und UPDATE-Gegenproben laufen tatsächlich
unter Reader und müssen 4613/229 liefern. GRANT betrifft den separaten Sink; ein
allgemeines Self-GRANT-Verbot wird nicht als fehlendes Grantorrecht gewertet. Vor-/
Nachkontrollen binden sämtliche direkten Benutzerrechte einschließlich CONNECT,
fehlende Rollenmitgliedschaften und die vollständigen Source-/Vektorbytes. REVERT
gilt im Erfolg und Fehler. Der dbo-Harness ist privilegiert und nicht an Querybenutzer
freigegeben. Er validiert keinen authentifizierten Anwendungsservice.

Die acht Ergebnisassertions zählen 1 tatsächliche Baselinezeile, 2 retrievte Quellen,
1/3 akzeptierte/abgelehnte Antworten, 1/3 erlaubte/abgelehnte Tools, 2 tatsächliche
Rechteverweigerungen und 1 tatsächliche positive Toolrow. Fehlende positive Bestände
dürfen keinen Erfolg ergeben. Vier vollständige bytegenaue Eigentumsmarker binden
alle Phasen und Cleanup; eigene Daten-/Logdateien sind auf 256/64 MB begrenzt.

## Private Vorprobe und erste Checkpoints

Die separate private 17.x-Vorprobe scheiterte zunächst vor Fachkontrollen mit 468 am
Collationvergleich zwischen sys.database_permissions und der Tabellenvariable.
Eine kohärente Korrekturwelle wandelte permission_name/state auf beiden Seiten in
vollständige varbinary(max) um und ergänzte volle eingefrorene Source-/Vektorbindung.
Der geänderte Versuch bestand: tatsächlicher GRANT-Fehler 4613, UPDATE-Fehler 229,
zwei retrievte Quellen, Antworten 1/3, Tools 1/3 und eigene DB-Abwesenheit. Beide
eigenen Container wurden nach Ownerlabelprüfung entfernt und ihre Abwesenheit geprüft;
beim ersten SQL-Fehler ersetzte der eigene Containerabbau keinen DB-Abwesenheitsbeleg.

Ein unabhängiger enger Quellenreview der privaten SQL-Probe und ihres Adapters fand
im korrigierten Stand keine konkreten Befunde. Er führte keine Runtime aus und gilt
ausschließlich für die festen synthetischen Fälle, nicht für das spätere FWK-Paket.
Die privaten Quellen bleiben ignoriert unter Runtime. Der anschließende vollständige
Demopaket-Slice hat einen Owner, einen erforderlichen Review und höchstens zwei
kohärente Korrekturwellen; der private Vorbereitungsreview ersetzt ihn nicht.

Framework, sieben bestehende KI-Runner-Unitmethoden, 30-Demo-Pfadvalidator,
348-Lauf-Katalogvalidator und 30-Demo-Leitfaden bestanden am vollständigen Kandidaten.
Die Matrixzahl beschreibt geplante zwei Provider × drei Versionen × zwei Wiederholungen
für das Gesamtkatalogprofil; sie ist kein ausgeführter 348-Lauf- oder Podmanbeleg.
Der alte validierte Inventarbestand wird nicht erweitert.

Das vollständige 17.x-Paket bestand seinen ersten lokalen Runtimeversuch: zwei
vollständige Lifecycles mit je acht Ergebnisassertions, Setup-Idempotenz, 80 vollständige
Markerabweichungen und zehn fachliche Gegenproben. Diese betreffen leere Quellen,
falschen FactDays-Wert, manipulierten Content, anderen Vektor, aktualisierte alte Quelle,
untrusted→trusted, andere alte Versionsnummer, zusätzliches UPDATE-Recht, CONTROL am
Sink und fehlendes SELECT. Jede frische vollständig markierte Gegenfixture scheiterte
in COMPARISON mit 51003/FAIL_RESULT_CONTRACT. Markerabweichungen blieben ohne Änderung
der vollständigen Quellen-/Vektor-/Grant-/DB-Konfigurationssnapshot. Cleanup und
unabhängige DB-Abwesenheit bestanden, der eigene Container war anschließend abwesend.

15.x und 16.x bestanden je zwei SKIP_VERSION-Lifecycles vor SETUP ohne Ergebnis-
assertions. Eigene DB-Abwesenheit und Containerabbau wurden ebenfalls separat geprüft.
Diese Versionen liefern keinen Prompt-/Tool-/Rechteruntime-PASS. Für das vollständige
Paket wurde bislang keine Korrekturwelle oder unveränderte Runtimewiederholung verbraucht.

Der erforderliche unabhängige Quellenreview des stabilen vollständigen FWK-Slice fand
keine konkreten Befunde. Er prüfte ausschließlich neue Marker-/Phasen-/Versions-/
Ergebnis-/Cleanup- und Runner-/Metadatendeltas gegenüber der privaten Vorbereitung.
Keine eigene Runtime wurde im Review ausgeführt; sein Quellenschluss ersetzt die
getrennten lokalen Ausführungsbelege nicht. Keine weitere Reviewkette wurde gestartet.

## Aufwand und offene Grenzen

Der vorhandene KI-Runner bekommt genau ein weiteres Demo, zwei Lifecycles je Version
und die neuen gebundenen Marker-/Resultgegenproben. Drei vorhandene CI-Versionsjobs
bleiben erhalten; keine neue Reviewkette, kein Modellaufruf und keine neue Automation.
Katalog-/Guideprüfungen und der konservative alte CI-Selector bleiben unverändert.
Modell-/Tokenverbrauch des Orchestrators bleibt unbekannt; die Demo selbst generiert
keine Tokens. Bestehende CI-Checks werden einmal am aktuellen Head durchgeführt und
nur bei geändertem Input oder neuer konkreter Evidenz wiederholt.

Kein Live-LLM-, allgemeiner Entailment-, Egress-, Tenant- oder Prompt-Injection-
Sicherheitsnachweis. Serverlogins, mehrere Sessions, DGN-008-External-Models,
Endpoint-/Credentialrechte und Providerabnahme bleiben UNQUALIFIED. Lokales Lab-RAG
bleibt am DEC-033-Secretgate; Cloud-/Bezahl-, ONNX- und rote Hoständerungen sind nicht
freigegeben. Nach erfolgreicher Integration folgt ein unabhängiger kleiner DGN-008-
Offline-Rechteschnitt; ein angehaltener CON-010-Slice wird nicht unverändert wiederholt.

Die Primärquellen wurden am 2026-10-11 geprüft: GRANT benötigt passende Grantorrechte
laut [Microsoft](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/grant-a-permission-to-a-principal?view=sql-server-ver17);
4613 bezeichnet fehlendes GRANT-Recht im
[Fehlerkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/errors-events/database-engine-events-and-errors-4000-to-4999?view=sql-server-ver17).
