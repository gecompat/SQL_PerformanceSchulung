# SQL Server 2025 – KI-Feature- und Provider-Matrix

Stand und Prüfung: 2026-10-11. Arbeitspaket: `TSK-003`; Folgequalifikation: `TSK-004`.
Dies ist die fachliche Matrix zum [Workstream-Plan](../Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md).
Quellenautorität bleibt [SOURCE_REGISTER.md](SOURCE_REGISTER.md), Einträge `SRC-072`–`SRC-100`.
Die folgenden Aussagen sind **Dokumentiert**, soweit eine Quelle angegeben ist.
Diese Matrix ersetzt keine empirische Build-/Runtime-/Providerqualifikation;
konkrete Teilnachweise und offene Gates stehen im kanonischen Ausführungsstand.

## 1. Plattform- und Freigabegrenzen

SQL Server 2025 bezeichnet Engine 17.x, SQL Server 2022 Engine 16.x.
SQL Server 2022 besitzt die hier geplanten nativen VECTOR-/AI-Funktionen nicht.
Ein Client mit Copilot kann dagegen auch mit älteren Engines arbeiten.
Azure SQL Database wird nur als Vergleichsplattform beschrieben, nicht als Laborziel freigegeben.

Die Editionstabellen führen native Vektoren, DiskANN, External Models, Embeddings und Chunking
für Enterprise, Standard und Express auf (`SRC-083`, `SRC-084`). Developer übernimmt die
jeweilige Editionsfunktionalität für Entwicklung/Test. Ressourcen- und Parallelitätsgrenzen
bleiben editionsabhängig. Der primäre Labortarget ist Enterprise Developer auf Windows oder
Linux; Express und Standard Developer erhalten erst nach eigener Prüfung eine Laufzeitfreigabe.
Die Featureseiten ohne eigene OS-Grenze werden zusammen mit diesen Editionstabellen gelesen.

**Quellenkonflikt:** Die Linux-Editionstabelle nennt lokale ONNX-Modelle, während das konkrete
ONNX-Verfahren ausdrücklich Windows und installierte Machine Learning Services voraussetzt
(`SRC-080`, `SRC-084`). Daher wird kein ausführbarer Linux-ONNX-Pfad behauptet.
Die Frage bleibt bei `TSK-004` offen; der geplante ONNX-Pfad ist ausschließlich Windows.

## 2. Funktionsmatrix

Die Spalte CL trennt eine dokumentierte Mindestanforderung vom gewählten Laborprofil CL 170.
„Nicht separat genannt“ ist keine Behauptung über beliebige CLs; `TSK-004` prüft dies vor Implementierung.
Alle Quellen wurden am 2026-10-11 geprüft. Edition/OS folgt §1, außer bei ONNX.

| Funktion / Zweck und Mechanismus | Engine / Status | CL und Konfiguration | Berechtigung / Infrastruktur | Security und Performance | Quelle / Syntax |
|---|---|---|---|---|---|
| `VECTOR`: numerische Repräsentation, binär gespeichert, JSON-Konvertierung | 17.x; float32 GA; float16 Preview | Typ unter allen CLs; float16 mit `PREVIEW_FEATURES=ON` | Tabellen-DDL nur beim Setup; DML/SELECT je Objekt; kein Modell nötig | Embeddings schützen; Nutzdaten grob 4d bzw. 2d Bytes, tatsächlichen Speicher messen; float32 1–1998, float16 1–3996 Dimensionen | `SRC-072`; S1 |
| `VECTOR_DISTANCE`: exakte Distanz zweier Vektoren | 17.x; GA | kein separates CL-Minimum genannt; Labor 170 | SELECT auf Eingabeobjekten; keine eigene Inferenzberechtigung | CPU-Arbeit je Kandidat; verwendet keinen Vector Index; cosine, euclidean, negatives dot product | `SRC-073`; S2 |
| `VECTOR_NORM`: Betrag nach norm1/norm2/norminf | 17.x; GA | kein separates CL-Minimum genannt | wie DISTANCE; kein Netzwerk | Eingabe-/Dimension-/Nullfälle prüfen; Norm ist kein Relevanzscore | `SRC-074`; S2 |
| `VECTOR_NORMALIZE`: Skalierung auf Einheitsnorm | 17.x; GA | kein separates CL-Minimum genannt | SELECT, bei Speicherung zusätzlich UPDATE | Modellnormalisierung prüfen; zusätzliche Arbeit und Rundung; Null-/Nullvektor-Gegenproben | `SRC-075`; S2 |
| `VECTORPROPERTY`: Dimensionszahl/BaseType kontrollieren | 17.x; GA | kein separates CL-Minimum genannt | SELECT; kein Netzwerk | Modellwechsel und falsche Dimension erkennen; Metadatenprüfung ersetzt keine Inhaltsprüfung | `SRC-076`; S2 |
| `CREATE VECTOR INDEX`: DiskANN-Zugriffspfad | 17.x; Preview | `PREVIEW_FEATURES=ON`; Labor 170, kein separat genanntes CL-Minimum | `ALTER` auf Tabelle; Basistabelle, clustered INT Primary Key; kein Provider | Build-/Speicher-/Maintenancekosten; kein Recallversprechen; aktuelle Mindestdaten-/Indexformatgrenzen am konkreten Build prüfen | `SRC-077`; S3 |
| `VECTOR_SEARCH`: Approximate Nearest Neighbor Search | 17.x; Preview; Azure SQL Database GA | Preview in SQL Server; passender Index/Metric; Labor 170 | SELECT auf Basistabelle; Rechte an zurückgegebenen Spalten prüfen | Plan/Fallback prüfen; Altformat Postfilter kann weniger als k Treffer liefern; Suche nie als Autorisierung verwenden | `SRC-078`; S3 |
| `AI_GENERATE_CHUNKS`: lokale TVF für Textfragmente | 17.x; kein Previewhinweis auf Funktionsseite / GA-Lehrpfad | **CL mindestens 170**; FIXED, Zeichenanzahl; OVERLAP 0–50 Prozent | SELECT auf Quelltext; kein Modell/Netzwerk | Chunking ist keine Tokenisierung; Größe beeinflusst Kontext, Kosten und Wiederholungen | `SRC-079`; S4 |
| `CREATE EXTERNAL MODEL`: Datenbankobjekt für Embedding-Inferenz | 17.x; REST-Pfad ohne Previewhinweis / GA-Lehrpfad; ONNX Preview | REST separat aktivieren; ONNX siehe §4 | `CREATE EXTERNAL MODEL` oder `ALTER ANY EXTERNAL MODEL`; Nutzung: `EXECUTE ON EXTERNAL MODEL`; Credential separat | registriert Modell, hostet kein generatives LLM; TLS, Secret-/Egressgrenze; Providerformat und Modellparameter festhalten | `SRC-080`, `SRC-082`; S5 |
| `AI_GENERATE_EMBEDDINGS`: Text über External Model einbetten | 17.x; REST-Pfad ohne Previewhinweis / GA-Lehrpfad; ONNX Preview | vorkonfiguriertes EMBEDDINGS-Modell; REST-Instanzoption für REST-Pfad; CL-Minimum nicht separat genannt | Model-EXECUTE, Quelltext-SELECT; optional HTTPS-Provider und Credential | Datenabfluss; Timeout/Retry/Dimension/Truncation; Inferenz separat von SQL-Arbeit messen | `SRC-081`; S5 |
| `sys.sp_invoke_external_rest_endpoint`: zusätzlicher REST-Integrationsbaustein | 17.x; dokumentiert, standardmäßig deaktiviert; kein GenAI-Spezialdienst | Instanzoption `external rest endpoint enabled`; ALTER SETTINGS nur für Bereitstellung | `EXECUTE ANY EXTERNAL ENDPOINT`; Credentialgrenze beachten | HTTPS/TLS; keine automatischen Redirects; HTTP-/Netzfehler trennen; HTTP_EXTERNAL_CONNECTION | `SRC-082`; S6 |
| `sys.vector_indexes`: Indexmetadaten | 17.x; an Preview-Index gebunden | vorhandener Index; Katalogsichtbarkeit | objektbezogene Metadatensichtbarkeit | Identität/Buildparameter lesen; kein Nutzungs-/Qualitätsbeweis | `SRC-097`; S7 |
| GitHub Copilot in SSMS: SQL-/Diagnoseassistenz | **Client**, keine 17.x-Enginefunktion; Copilot GA seit 22.4.1; Agent Mode GA mit 22.10.2 | SSMS 22, Agent Mode ab 22.7; AI Assistance/Copilotzugang; genauer Clientbuild maßgeblich | verbundener SQL-Kontext bzw. ausdrücklich konfigurierter Ausführungskontext; Providerzugang optional | Rechte erzwingt SQL Server; Approval ist keine Sicherheitsgrenze; Datenübertragung/Kosten separat prüfen | `SRC-089`–`SRC-092`, `SRC-098`; keine Engine-Syntax |

`GA-Lehrpfad` bedeutet hier die Einordnung ohne Preview-Markierung in den aktiven Referenzen,
keine Zusicherung für jede Unterfunktion, Bibliothek oder künftige Revision.
Keine native allgemeine Chat-/Completion-Funktion wird aus `MODEL_TYPE=EMBEDDINGS` abgeleitet.
Die generative RAG-Stufe liegt in der Anwendung.

### Engine, CL und Client: begrenzter Abgleich vom 2026-10-13

Für diesen Abschnitt wurden die bestehenden Primärquellen SRC-072 und SRC-079
am 2026-10-13 erneut geprüft. Der allgemeine Prüfstand dieser Matrix bleibt
2026-10-11; daraus folgt keine erneute Prüfung aller übrigen Quellen.

| Grenze | Dokumentiert | Im Projekt tatsächlich beobachtet / offen |
|---|---|---|
| Engine | VECTOR gehört zu SQL Server 2025 / 17.x. Ein Client oder ein höherer CL ergänzt die Funktion nicht in einer älteren Engine (SRC-072). | Der [Providerteilnachweis](../Project_Planning/SQL_SERVER_2025_AI_PROVIDER_REVIEW.md) bindet konkrete Builds; 15.x/16.x endeten vor Setup mit Versions-SKIPs. Das ist kein Test nativer VECTOR-Verarbeitung dieser älteren Engines. |
| Compatibility Level | Der VECTOR-Typ ist unter allen CLs verfügbar; AI_GENERATE_CHUNKS verlangt mindestens CL 170 (SRC-072/079). | Die [CL-Istwertqualifikation](../Project_Planning/SQL_SERVER_2025_AI_CL_RESULT_REVIEW.md) bestand auf 17.0.5005.3 mit float32-Skalaren bei CL 150/160/170. Der feste Chunkaufruf lieferte bei CL 150/160 Error 102 und bei CL 170 beide vollständigen Rows. Error 102 bleibt OBSERVED_OTHER_ERROR_NO_AVAILABILITY_CLAIM; keine allgemeine Low-CL-Freigabe. |
| Clienttransport | Native binäre Übertragung benötigt den dokumentierten TDS-/Treiberpfad: TDS 7.4 oder höher und einen unterstützenden Treiber; Microsoft.Data.SqlClient 6.1 dokumentiert SqlVector für float32. Der dokumentierte Abwärtspfad für ältere Clients verwendet VARCHAR(MAX)/JSON (SRC-072). | Der [Corpus-SQL-Nachweis](../Project_Planning/SQL_SERVER_2025_AI_CORPUS_SQL_REVIEW.md) prüfte alle Koordinaten über JSON sowie vollständige Cosine-Ergebnisse. Native binäre Treiberbindung ist hier empirisch UNQUALIFIED; JSON ist kein Nachweis identischer physischer VECTORbits. |

Dokumentierte Treiberunterstützung bedeutet nicht, dass die konkrete Anwendung
bereits qualifiziert wurde. Umgekehrt bedeutet der offene Binärtransportnachweis
keine pauschale Inkompatibilität älterer Clients. Öffentliche Demoprofile bleiben
CL 170; float16, andere Builds/Editionen und die vollständige TSK-004-Abnahme bleiben
offen. Eine verständliche Entscheidungshilfe mit drei Fällen steht im
[Engine-/CL-/Client-Guide](../HowTo/SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY.md).

## 3. Präzise T-SQL-Formen als Planungsbeispiele

Eigenständige Beispiele; nicht ausgeführt und kein Demo-Setup. Die Tabellen-/Modellnamen
sind synthetisch. Bereitstellung, Grants, Datengenerator und Cleanup werden erst implementiert.

### S1 – Typ und Konvertierung

```sql
DECLARE @q VECTOR(3) = '[2,0,1]';
DECLARE @half VECTOR(3, float16) = '[2,0,1]'; -- separater Preview-Pfad
```

### S2 – skalare Funktionen

```sql
SELECT VECTOR_DISTANCE('cosine', @q, @q),
       VECTOR_DISTANCE('euclidean', @q, @q),
       VECTOR_DISTANCE('dot', @q, @q),
       VECTOR_NORM(@q, 'norm2'),
       VECTOR_NORMALIZE(@q, 'norm2'),
       VECTORPROPERTY(@q, 'Dimensions'),
       VECTORPROPERTY(@q, 'BaseType');
```

norm1/norminf sind die anderen dokumentierten Normargumente. Die Metric bestimmt den Score;
kleinere Distanz bedeutet Nähe, keine Wahrscheinlichkeit fachlicher Korrektheit.

### S3 – Index und Suche nach Indexgeneration

Die [einzelne Parserdiagnose](../Project_Planning/SQL_SERVER_2025_AI_ANN_PARSER_PASS_REVIEW.md)
bestand am eigenen Build 17.0.5005.3: tatsächlicher Previewwert 0 → Fehler 343,
nach separat attestiertem 1 → gleicher Parsertext akzeptiert. Kein Indexbuild oder
Suchlauf durch diese Syntaxdiagnose; historische Batch-/Sessionursache nicht isoliert bewiesen. Der weitere
[Build-/Suchentscheid](../Project_Planning/SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md)
wurde ausdrücklich genehmigt. Sein [Befund](../Project_Planning/SQL_SERVER_2025_AI_ANN_BUILD_REVIEW.md)
bleibt nach beiden Kandidaten FAIL: zuerst Sessionoption QUOTED_IDENTIFIER (1934),
danach eigener Index erstellt, aber Stopp am Generationsgate vor Search (51003).
Konkrete Generation und rohe Typ-/Metric-/Buildparameter unbekannt, weil vor dem
Guard nicht ausgegeben. Keine Such-/Recallevidenz; beide tatsächlichen Restores 0/0
und separate DB-/Containerabwesenheit bestanden.
Die anschließend [bestandene einzelne Metadatenaufnahme](../Project_Planning/SQL_SERVER_2025_AI_ANN_METADATA_REVIEW.md)
belegt nun am eigenen festen Build: DiskANN/COSINE, gültige Buildparameter,
Version-Schlüssel fehlt, Versionsableitungen NULL. Generation UNKNOWN und
keine Such-/Indexnutzungsqualifikation. SRC-097 bezeichnet die Buildparameter
als intern; die dokumentierte Version-Migrationsabfrage liefert hier keinen Wert.
Die zusätzliche Benutzerfreigabe autorisiert einen eigenen begrenzten
[Legacy-Signaturversuch](../Project_Planning/SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_DECISION.md)
ohne numerische Generation zu behaupten. Der
[zweite Kandidat bestand zwei vollständige Ergebnislifecycles](../Project_Planning/SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_REVIEW.md):
je fünf distanzgeprüfte Quellrows und 5/5 Schnittmenge mit Exact-Oracle; tatsächliche
Katalogtexttypen nvarchar. Erster Kandidat FAIL am Speicherformvergleich erhalten.
Beide tatsächlichen Restores und separate DB-/Containerabwesenheit bestanden.
Generation UNKNOWN, Indexnutzung UNPROVEN; keine konkrete Generations-/TP-PERF-/Demoabnahme.
Die eigene [tatsächliche Planausgabe bestand](../Project_Planning/SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md):
Vector Index Seek auf dem voll gebundenen eigenen DiskANN-Index mit fünf
tatsächlichen Rows. Dies belegt Indexnutzung nur für den festen ungefilterten
Suchaufruf; Generation UNKNOWN, kein Performance-/voller Demo-PASS.
Die [Filter-/Ergebnisdiagnose bestand zwei Lifecycles](../Project_Planning/SQL_SERVER_2025_AI_ANN_FILTER_REVIEW.md):
breite Id-Fenster Recall@5 1; Fenster 501–510 null ANN- gegen fünf Exact-Rows,
Recall@5 0/ROWS_BELOW_K. Sichtbarer Legacy-Postfilterverlust am festen Korpus/Query;
gefilterte Indexnutzung UNPROVEN, kein Performance-/voller Demo-PASS.
Die [begrenzte Messdiagnose](../Project_Planning/SQL_SERVER_2025_AI_ANN_MEASUREMENT_REVIEW.md)
bewahrt ungeeignete Session-Nulldeltas als WARN. Zwei geänderte Live-Request-
Lifecycles liefern aktive CPU-/Logical-Read-Deltas; Exact-Zeitnullwerte und
Koordinator-/Workergrenzen bleiben sichtbar. Kein ANN-Vorteil am festen kleinen
Korpus belegt, keine vollständige FWK-/TP-PERF-/Demoabnahme.
Die [einzelne UPDATE-/Rollback-Diagnose](../Project_Planning/SQL_SERVER_2025_AI_ANN_DML_REVIEW.md)
bestand im zweiten Kandidaten zweimal: tatsächlicher SQL-Fehler 42231/State 1,
Transaktionssnapshot 0/0, vollständige Source-/Indexmetadaten unverändert. Erster
Kandidat FAIL an widersprüchlicher JSON-Transaktionsevidenz erhalten. Staleoption
ABSENT, Freshness NOT_TESTED, keine allgemeine DML-/Generations-/Demoabnahme.
Der fachlich unabhängig geprüfte [DEC-074-Profilpfad](../Project_Planning/SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md)
erlaubt ausschließlich für den empirisch gebundenen 17.0.5005.3-Build funktionale
Qualifikation mit Generation UNKNOWN/WARN. Alle übrigen Demo-/TP-PERF-/Recovery-
Gates bleiben Pflicht; keine vollständige Demoabnahme aus den privaten Diagnosen.

Ressourcengrenze, geprüft am 2026-10-11: `SRC-106` dokumentiert, dass SQL Server 2025
den MAXDOP-Parameter von CREATE VECTOR INDEX/VECTOR_SEARCH ignorieren kann. Die
folgende DDL-Angabe garantiert deshalb keinen tatsächlichen DOP 1. Server- oder
DB-scoped-Konfigurationsalternativen benötigen ihren eigenen Effektentscheid und
Restorevertrag; sie werden nicht automatisch durch eine Previewfreigabe erlaubt.
Am ausgewählten lokalen Build ist Parserannahme und später die Erstellung eines
eigenen Index belegt; Generation/Search bleiben unqualifiziert. Der attestierte
eigene DB-scoped-MAXDOPwert 1 ist kein empirischer Worker-/DOP-Nachweis.
Der historische [Resume-FAIL](../Project_Planning/SQL_SERVER_2025_AI_ANN_RESUME_REVIEW.md)
bleibt erhalten und wird nicht zum aktuellen PASS umgedeutet.

```sql
CREATE VECTOR INDEX IX_Chunks_Vector ON dbo.Chunks(Embedding)
WITH (METRIC = 'cosine', TYPE = 'DiskANN', MAXDOP = 1);

-- SQL-Server-2025-Lehrpfad mit früherer Indexgeneration:
SELECT c.ChunkId, r.distance
FROM VECTOR_SEARCH(TABLE = dbo.Chunks AS c, COLUMN = Embedding,
     SIMILAR_TO = @q, METRIC = 'cosine', TOP_N = 5) AS r
ORDER BY r.distance;

-- Neueste Indexgeneration: derzeit ausdrücklich für Azure-Plattformen genannt.
-- Kein ungeprüfter SQL-Server-2025-Pfad:
SELECT TOP (5) WITH APPROXIMATE c.ChunkId, r.distance
FROM VECTOR_SEARCH(TABLE = dbo.Chunks AS c, COLUMN = Embedding,
     SIMILAR_TO = @q, METRIC = 'cosine') AS r
ORDER BY r.distance;

-- Exaktes Vergleichsoracle, gleiche Kandidaten und Metric:
SELECT TOP (5) ChunkId, VECTOR_DISTANCE('cosine', Embedding, @q) AS Distance
FROM dbo.Chunks
ORDER BY Distance, ChunkId;
```

`SRC-077/078` dokumentieren neue Indexstrukturen neben älteren, deprecated Formen.
Die Vorabprüfung liest Enginebuild, Indexmetadaten und unterstützte Syntax. DML, iterative
Filterung und neue DMV-Maintenance sind kein ungeprüftes SQL-Server-Versprechen.
Fehlender kompatibler ANN-Index kann einen kNN-Fallback verursachen: ohne Planbeleg kein ANN-Claim.

### S4 – lokales Chunking

```sql
SELECT c.chunk_order, c.chunk
FROM AI_GENERATE_CHUNKS(SOURCE = N'Synthetische technische Wissensbasis.',
     CHUNK_TYPE = FIXED, CHUNK_SIZE = 24, OVERLAP = 25) AS c;
```

`CHUNK_SIZE` ist bei FIXED erforderlich. `ENABLE_CHUNK_SET_ID=1` ist optional;
Dokument-/Versionsbindung wird unabhängig vom erzeugten Gruppierungswert gespeichert.

### S5 – Modelldefinition und Embeddings

```sql
CREATE EXTERNAL MODEL LabEmbeddingModel
WITH (LOCATION = 'https://localhost:11435/api/embed',
      API_FORMAT = 'Ollama', MODEL_TYPE = EMBEDDINGS, MODEL = 'all-minilm');
GRANT EXECUTE ON EXTERNAL MODEL::LabEmbeddingModel TO LabEmbeddingCaller;
SELECT AI_GENERATE_EMBEDDINGS(N'Synthetische Erklärung zu Indexkosten.'
       USE MODEL LabEmbeddingModel);
```

Der Loopback-Port bezeichnet einen erst nach gesonderter Freigabe geprüften TLS-Proxy,
keinen vorhandenen Dienst. Alternative Formate: `Azure OpenAI`, `OpenAI`, `ONNX Runtime`.
`AUTHORIZATION`, `CREDENTIAL`, `PARAMETERS` und bei ONNX `LOCAL_RUNTIME_PATH` sind
zusätzliche dokumentierte Modelldefinitionsparameter. Der Azure-Pfad nutzt das dokumentierte
Deployment-Embedding-Endpointformat; die neuere Provider-v1-API wird nicht automatisch substituiert.
**Offene Referenzinkonsistenz:** `SRC-081` beschreibt den Rückgabetyp als Single-Column Table,
zeigt jedoch skalare SELECT-Beispiele. Resultattyp, Konvertierung zu VECTOR und Treibertransport
sind ein zwingendes Probe-/Abnahmegate von `TSK-004`, kein bereits gelöster Vertrag.

### S6/S7 – REST und Metadaten

```sql
DECLARE @response NVARCHAR(MAX);
EXEC sys.sp_invoke_external_rest_endpoint
     @url = N'https://example.invalid/embeddings', @method = N'POST',
     @payload = N'{"input":"Synthetischer Text"}',
     @timeout = 10, @retry_count = 0, @response = @response OUTPUT;
SELECT object_id, index_id, build_parameters FROM sys.vector_indexes;
```

Der nicht auflösbare Beispielendpoint ist absichtlich kein ausführbares Lehrziel.
Modell-/Credentialkonfiguration wird niemals aus Dokumentationsbeispielen mit Secrets übernommen.

## 4. Infrastruktur- und Provider-Matrix

Alle Zeilen sind **geplant**. „Lokal“ beschreibt die Datenverarbeitung, nicht automatisch fehlende
Netzwerkverbindungen beim Modelldownload. Downloads/Lizenzen/Hashes benötigen einen eigenen Preflight.

| Pfad | Engine / Provider / Modell / Anwendung | TLS, API und Authentifizierung | Ressourcen und Grenzen | Aktivierung / Abnahme |
|---|---|---|---|---|
| Lokaler Pflichtpfad | 17.x; kein Provider; konstruierte Vektoren, synthetische Chunks; T-SQL | kein externes Netzwerk, DB-Rechte objektbezogen | kleine deterministische Geometrie zeigt Mechanik, keine echte Sprachsemantik | `TSK-005`; vollständig ohne externes Modell |
| Lokale Sprachsemantik | 17.x; vorbereitete lokale Embedding-Runtime, z. B. Ollama; versioniertes Embedding-Modell; Ingestion getrennt von Suche | `/api/embed`; direkte SQL-Anbindung benötigt HTTPS/TLS, vertrauenswürdige Zertifikatskette/SAN, erreichbaren DNS/Port aus Enginekontext; lokales Ollama selbst hat keine Authentifizierung | CPU/RAM, optional GPU; Tokenlimit/Truncation, Dimension, Warm-up, Digest und Lizenz festhalten | `QRY-020`, `TSK-007`; TLS-Proxy und Egress-Abschottung ausdrücklich aktivieren; Cloudmodelle sperren |
| Externe Embeddings | 17.x; Azure OpenAI; genehmigtes Deployment eines Embedding-Modells; begrenzte Ingestion | HTTPS, passendes `API_FORMAT`; Database Scoped Credential und Pfadbindung; API-Key nur Secret Store, alternativ qualifizierte Managed Identity | Quota, Rate Limit, Retry, Transfer, Region und Geldbudget; keine unkontrollierten Einzelaufrufe je Zeile | `QRY-021`; optionales eigenes Freigabegate, kein Cloudaufbau in diesem Auftrag |
| Generative RAG-Stufe | 17.x als Retrieval-Engine; separates lokales generatives LLM oder genehmigter externer Provider; Anwendung orchestriert | Anwendung authentifiziert DB und LLM separat; SQL-External-Model ist kein Completion-Provider; token-/kontextbegrenzte Übergabe | Modellantwort variabel; Kosten, Retrievalbelege, Quellen und Abstention auswerten | `QRY-018`; Offline-Replay für Pflichtübung; echte Inferenz optional |
| Lokale ONNX-Inferenz | 17.x Windows; AI Runtime Host/ONNX Runtime; Modell plus Tokenizer; T-SQL-Embeddingaufruf | Machine Learning Services, `external AI runtimes enabled`, Preview; geprüfte DLLs und Dateirechte | Supply Chain, Native Code und Instanzwirkung; kein Linux-/Containerclaim | `QRY-022`; Rot, eigenes Wegwerflab und gesonderte Freigabe |
| SSMS-Assistenz | SSMS 22.x; GitHub Copilot/ausgewähltes Modell; SQL-Konto und Client | getrennte Client-/Providerauthentifizierung; Ask/Agent und tatsächlichen SQL-Ausführungskontext prüfen | Fehler/Tools, MCP-Zugriff, Kontextübertragung, Kontingente; keine produktiven Diagnoseexports | `DGN-010`; synthetischer Offline-Fall Pflicht, Liveclient optional |

Nicht unterstützte Endpointformate, HTTP statt HTTPS, ungültige Zertifikate oder fehlende
Berechtigungen führen vor Setup zum kontrollierten SKIP; Fehler nach begonnenem Setup führen
zum FAIL samt Cleanup. Ein Self-signed-Zertifikat ohne qualifizierten Vertrauenspfad wird nicht
durch pauschales Abschalten der Zertifikatsprüfung akzeptiert. Containerloopback ist nicht Hostloopback.

## 5. Offene fachliche Prüfungen vor Umsetzung

- `TSK-004`: genaue 17.x-Build-/CU-Bindung für Indexgeneration, TOP_N, Mindestdaten, DML,
  float16 und CLs. Azure-Freigaben bleiben getrennt. Primärtexte ändern sich; Abrufdatum ist kein Buildbeleg.
- `TSK-004`: Resultattyp von `AI_GENERATE_EMBEDDINGS`, treiberabhängiger VECTOR-Transport,
  exakte Error-/SKIP-Fälle sowie Zero-/Nullvektorverhalten.
- `TSK-007`: TLS-/REST-Payloadprobe für Ollama, Azure-Deploymentformat, Authentifizierung,
  Modelllizenz/Hash/Dimension und Offlinefähigkeit. Provider-v1-Kompatibilität ist offen.
- `TSK-009`: reale Berechtigungskette Model-EXECUTE/Credential/REST, RLS mit tatsächlicher
  ANN-Generation und Pooling; negative Fälle unter nichtprivilegierten Rollen.
- `TSK-011`: Agent-/Ask-Modus und Ausführungskontext am konkreten SSMS-Build;
  ältere Azure-OpenAI-Preview-Copilottexte gelten nicht für das heutige GitHub-Copilotprodukt.

Keine dieser offenen Fragen verhindert den Abschluss der Planung; sie verhindert die jeweilige
Implementierungs- beziehungsweise Runtimefreigabe. Eine unbelegte Eigenschaft bleibt Hypothese.
