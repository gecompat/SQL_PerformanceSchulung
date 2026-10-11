# KI mit SQL Server 2025 – Grundlagenbegriffe für den Offlinepfad

Stand: 2026-10-11. Didaktischer TSK-012-Teilentwurf für CUR-013–CUR-018/CUR-022.
Die Begriffserklärungen ergänzen das [Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md).
Sie erweitern keine Runtime-, Provider-, Preview- oder Lehrgangsabnahme.

## Modell, Repräsentation und Aufgabe

Die folgende Tabelle ist ein vereinfachtes Begriffsmodell für die Schulung.
Ein Text-Embedding bildet Text auf Zahlen ab; seine Nähe muss für die konkrete Aufgabe
bewertet werden. Die Geometrievektoren des Offlinepfads entstehen dagegen aus festen
Fixtures. Der Embeddingbegriff ist beschrieben in SRC-087,
[Microsoft Embeddings](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings),
geprüft am 2026-10-11. Dessen Cloudbeispiele werden hier nicht ausgeführt.

| Begriff | Erklärung | Einordnung im Offlinepfad |
|---|---|---|
| Machine Learning (ML) | Verfahren, dessen Modellverhalten aus Trainingsdaten gelernt wird. | Das Erzeugen fester Tabellen-/Vektorfixtures ist kein Modelltraining. |
| Generative AI | Modellverfahren, das neue Ausgaben wie Text erzeugt. | Vorab gespeicherte Antwortfixtures sind keine tatsächlich generierten Antworten. |
| Large Language Model (LLM) | Sprachmodell, das im betrachteten generativen Pfad Text auf Basis von Tokenkontext erzeugt. | Es wird in den acht Offline-Demos nicht aufgerufen. |
| Embedding | Numerische Repräsentation einer Eingabe, erzeugt durch ein bestimmtes Modell. | VECTOR(3) aus festen Geometriewerten zeigt Mathematik, keine gemessene Textsemantik. |
| Modellraum | Koordinatensystem und Bedeutung der Vektoren eines gewählten Modell-/Eingabeprofils. | Gleiche Dimension erlaubt nicht automatisch gemeinsame Suche über GEOMETRY_V1/V2. |
| Provenienz | Nachvollziehbare Herkunft und Verarbeitung einer gespeicherten Information. | Dokumentversion, Quellenbereich, Modellversion/Digest und Chunkprofil erhalten die Bindung. |
| Token | Verarbeitungseinheit eines konkreten Tokenizers. | Tokenzahl lässt sich nicht pauschal aus der Zeichenanzahl eines SQL-Chunks ableiten. |
| Fixture / Replay | Vorab festgelegte Eingabe beziehungsweise gespeicherte Ausgabe für einen kontrollierten Versuch. | QRY-018/019 und DGN-009 prüfen die deklarierten Fälle, keine beliebigen Modellantworten. |

## Vektor und Vergleich

Dokumentiert: SQL VECTOR speichert numerische Komponenten und kann über JSON-
Zeichenfolgen dargestellt werden. Der Typ ersetzt keine Modellprovenienz. Die native
Distanzfunktion berechnet die gewählte Distanz exakt und nutzt keinen Vector Index.
Quellen SRC-072/SRC-073, geprüft am 2026-10-11:
[VECTOR](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17),
[VECTOR_DISTANCE](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-distance-transact-sql?view=sql-server-ver17).
Die folgenden Rechenbeispiele sind Mathematik, keine neue SQL-Runtime.

| Begriff | Erklärung | Beispiel oder Grenze |
|---|---|---|
| Dimension | Anzahl der Komponenten eines Vektors. | [3,4,0] hat drei Komponenten; keine Modellidentität folgt daraus. |
| Basistyp | Numerischer Typ der Komponenten. | Der verwendete Offlinepfad nutzt float32; Darstellung und interne Speicherung sind verschieden. |
| Distanz / Score | Zahl aus einer festgelegten Vergleichsfunktion. | Eine kleine Cosine-Distanz ist kein Wahrheitswert oder fachliches Relevanzurteil. |
| Euclidean Distance | Abstand über die Quadratwurzel der Summe quadrierter Komponentendifferenzen. | [1,0,0] zu [2,0,0] ergibt 1. |
| Cosine Distance | Für von null verschiedene Vektoren: 1 minus normiertes Dot Product. | Gleichgerichtete [1,0,0] und [2,0,0] haben mathematisch Distanz 0. Null-/Zero-Fälle benötigen eigene Kontrolle. |
| Negatives Dot Product | Negierte Summe der komponentenweisen Produkte; SQL-Metric dot. | [3,4,0] mit sich selbst ergibt -(9+16)=-25. Vektorlänge beeinflusst die Rangfolge. |
| norm1 / norm2 / norminf | Summe absoluter Komponenten / euklidische Länge / größter absoluter Komponentenwert. | Für [3,4,0]: 7 / 5 / 4. |
| Normalisierung | Skalierung anhand einer gewählten Norm. | Mit norm2 wird aus [3,4,0] mathematisch [0.6, 0.8, 0]; Modellvertrag und Sonderfälle bleiben relevant. |
| Top-k / Tie | Auswahl der ersten k Treffer; gleiche Scores benötigen eine festgelegte Reihenfolge. | Die Fixture nutzt Id als zusätzliche Sortierung; Tieauflösung schafft keine neue semantische Information. |
| Exact kNN | Exakte Auswahl der nächstgelegenen Kandidaten für eine festgelegte Metric und Kandidatenmenge. | QRY-017 vergleicht nur seine erlaubten Fixturekandidaten. Exact bedeutet nicht fachlich richtige Antwort. |
| ANN | Approximate Nearest Neighbor Search, näherungsweise Auswahl ähnlicher Vektoren. | IDX-011/012 sind nicht qualifiziert. Die vorhandene Exact-Demo belegt weder ANN-Indexnutzung noch Recall. |
| Recall@k | Anteil der Treffer einer festgelegten Referenz-Top-k-Menge, die in der verglichenen Top-k-Menge vorkommen. | Referenz, Kandidatenmenge, k und Tieregel müssen feststehen; hier ist kein ANN-Recall gemessen. |

Die mathematischen Norm-/Normalisierungsbeispiele entsprechen der QRY-015-Fixture;
SQL-Verträge und Floating-Point-Toleranzen bleiben im
[Demovertrag](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/Expected/result-contract.json).

## Text, Retrieval und Antwort

Dokumentiert: AI_GENERATE_CHUNKS verwendet beim FIXED-Profil Zeichenanzahl und
einen prozentualen Overlap; seine Funktionsseite nennt CL mindestens 170.
SRC-079, geprüft am 2026-10-11:
[AI_GENERATE_CHUNKS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-chunks-transact-sql?view=sql-server-ver17).
Diese Quellenangabe qualifiziert nicht nachträglich den angehaltenen lokalen CL-Slice.

| Begriff | Erklärung | Offlinegrenze |
|---|---|---|
| Chunk | Fragment eines Quelltexts nach einem gewählten Profil. | DocId, Version, Reihenfolge, Offset und Länge erhalten die Herkunft. |
| Overlap | Wiederholter Anteil benachbarter Chunkbereiche. | Die Summe der Bereichslängen kann eindeutigen Quelltext mehrfach zählen. |
| Retrieval | Auswahl von Informationen aus einer Kandidatenmenge für eine Frage. | Erlaubter aktueller Kontext ist enger als die Menge aller existierenden Quellen. |
| Kontext | Informationen, die der betrachteten Antwortstufe tatsächlich bereitgestellt werden. | Ein existierendes Zitat außerhalb dieses Kontexts genügt der QRY-018-Policy nicht. |
| Claim | Konkrete überprüfbare Behauptung einer Antwort. | QRY-018 prüft nur seine feste Satzform zur Aufbewahrungsdauer. |
| Citation | Bezug einer Aussage auf eine konkrete Quelle beziehungsweise Stelle. | Existenz, Aktualität, Erlaubnis und tatsächliche Unterstützung des Claims sind getrennte Fragen. |
| Abstention | Begründete Nichtantwort bei fehlender oder widersprüchlicher Evidenz. | Sie darf keinen erfundenen Claim ergänzen; unnötige Nichtantwort ist ein eigener Fixturefehler. |
| RAG | Verbindung von Retrieval und generativer Antwortstufe. | QRY-018 bildet die Kontrollkette als Offline-Replay ab; die generative Stufe ist eine feste Fixture. |

Die Forschungsarchitektur verbindet Retrieval mit Sprachgenerierung, liefert aber
keine allgemeine Korrektheitsgarantie für den hier geplanten Anwendungspfad.
SRC-095, NeurIPS 2020,
[Retrieval-Augmented Generation](https://papers.nips.cc/paper_files/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html),
geprüft am 2026-10-11. Der lokale
[QRY-018-Nachweis](../Project_Planning/SQL_SERVER_2025_AI_OFFLINE_RAG_REVIEW.md)
begrenzt seine Aussage auf die tatsächlich geprüften festen Fälle.

## Drei kurze Transferfragen

1. Ist VECTOR(3) mit passender Cosine-Distanz bereits ein Sprachmodellnachweis?
   Nein: Typ und Distanz belegen allein weder Herkunft des Vektors noch fachliche Qualität.
2. Bedeutet ein Chunk mit 24 Zeichen höchstens 24 Modelltoken?
   Eine solche allgemeine Grenze wird nicht abgeleitet; Tokenizer und Eingabeprofil fehlen.
3. Ist eine zitierte plausible Sieben-Tage-Antwort trotz aktueller Neun-Tage-Gegenquelle freizugeben?
   Im QRY-018-Konfliktfall nicht: Die Fixture kennt keinen Vorrang und verlangt begründete Nichtantwort.

Die Fragen sind didaktische Vorschläge, keine tatsächlich erprobte Kompetenzabnahme.
Weitere Anbieter-, Rechte-, Kosten- und Abnahmegrenzen stehen im
[Arbeitsheft](SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md) und im
[aktuellen Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md).
