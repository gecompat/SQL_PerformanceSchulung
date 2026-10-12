# KI mit SQL Server 2025 – Arbeitsheft für den Offlinepfad

Stand: 2026-10-12. TSK-012, Teilentwurf für acht implementierte und lokal qualifizierte
Demos plus eine getrennte Ergebnisleseaufgabe zum begrenzten PROPOSED-Profil RES-008. Keine vollständige Curriculum-, Masterdeck- oder Generalprobenabnahme.
Die Aufgaben, Lösungen und Rubrik sind didaktische Vorschläge; eine tatsächliche
Teilnehmererprobung und gemessene Lehrzeiten stehen aus.

## Vorbereitung und Nachweise

Die [Grundlagenbegriffe](SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md) erklären Modell,
Vektor, Chunk, Retrieval und Antwort vor der ersten Aufgabe.
Der [Trainerleitfaden](SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md) ergänzt die
vorgeschlagene Reihenfolge und Moderation; Lösungen und Rubrik bleiben hier gepflegt.

Vorwissen: SELECT, ORDER BY, Parameter, Datenbankrechte und der Unterschied zwischen
Engineversion und Compatibility Level. Alle acht Demoprofile verwenden SQL Server
2025, CL170 und eine eigene synthetische Testdatenbank. Die bisherige Runtimequalifikation
betrifft Enterprise Developer auf Linux/Docker; die zusätzliche Podmanprobe deckt
alle acht hier behandelten Offline-Demos ab. Windows und andere Editionen sind damit
nicht qualifiziert. Der optionale Full-Text-Pfad von QRY-017 bleibt bei fehlender
Komponente WARN; daraus folgt keine Full-Text-Abnahme.
2019/2022 prüfen die vorgesehene SKIP_VERSION-Grenze vor Setup. Bei QRY-019 ist dies
eine Workstreamgrenze, keine Aussage über das Alter der Parameterbindung.

Ausführung, Authentifizierung, Preflight, Phasen und markergebundener Recovery stehen
im [Ausführungsleitfaden](DEMO_EXECUTION_GUIDE.md). Das Arbeitsheft führt keinen
zusätzlichen SQL-Aufrufer ein. Verwenden Sie eine eigene dedizierte Testinstanz;
SQL-Authentifizierung nutzt ausschließlich SQLCMDPASSWORD in der Umgebung.
Setup-/Cleanupownerrechte sind keine Teilnehmerrechte. Tatsächliche eingeschränkte
SQL-Identitäten sind Teil der Kontrollen von QRY-019, DGN-008 und DGN-009; die übrigen
Fälle zeigen die fachliche Mechanik im Ownerharness. Die Demoausgabe ersetzt nicht
die unabhängige Prüfung der eigenen DB-Abwesenheit.

Für jede Aufgabe zuerst eine Vorhersage notieren, dann den manifestbasierten Lauf
gemäß Leitfaden beobachten. Notieren Sie Demo-ID, Build, CL, Ergebnisstatus, konkrete
Rows oder Rechtefehler sowie Cleanupstatus. Behalten Sie FAIL, WARN und SKIP bei;
ein neuer Lauf benötigt geänderte Eingaben oder einen begründeten neuen Prüfauftrag.
Verwenden Sie ausschließlich die mitgelieferten synthetischen Fixtures.

Aktuelle Nachweise: [QRY-014–017](../Project_Planning/SQL_SERVER_2025_AI_LOCAL_IMPLEMENTATION_REVIEW.md),
[QRY-018](../Project_Planning/SQL_SERVER_2025_AI_OFFLINE_RAG_REVIEW.md),
[QRY-019](../Project_Planning/SQL_SERVER_2025_AI_SQL_INPUT_REVIEW.md),
[DGN-008](../Project_Planning/SQL_SERVER_2025_AI_EXTERNAL_MODEL_REVIEW.md) und
[DGN-009](../Project_Planning/SQL_SERVER_2025_AI_INJECTION_REVIEW.md).
Diese Abnahmen sind historische, jeweils gebundene Evidenz; dieses Arbeitsheft
behauptet keinen neuen SQL-Lauf. Anforderungen und zusätzliche offene Pfade stehen
im [Workstreamplan](../Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md) und der
[Featurematrix](../Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md).

## Teilnehmeraufgaben

### QRY-014 – Dimension und Modellraum

Zuordnung: CUR-013/CUR-014. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/QRY-014_Vector_Type/Expected/result-contract.json).

Sagen Sie voraus, ob zwei VECTOR(3)-Werte aus GEOMETRY_V1 und GEOMETRY_V2 allein
wegen gleicher Dimension gemeinsam gesucht werden dürfen. Lesen Sie die fünf Rows,
Typproperties und Modellraummerkmale. Unterscheiden Sie die abgelehnte falsche
Dimension beziehungsweise ungültiges JSON von einem syntaktisch gültigen Vektor
aus dem falschen Modellraum. Geben Sie zwei zusätzliche Provenienzfelder an.

Abgabe: ein technischer Typbefund, eine fachliche Grenze und zwei Provenienzfelder.

### QRY-015 – Metric und Normalisierung

Zuordnung: CUR-013/CUR-014. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/QRY-015_Vector_Metrics/Expected/result-contract.json).

Sagen Sie voraus, warum die Euclidean-Rangfolge zur Frage [1,0,0] und die rohe
Dot-Rangfolge verschiedene Ersttreffer besitzen. Berechnen Sie für [3,4,0] norm1,
norm2, norminf und negatives Self-Dot-Product. Vergleichen Sie danach die Rangfolge
nach norm2-Normalisierung. Beschreiben Sie, warum ein deterministisch aufgelöster
Tie keine Aussage über Sprachverständnis enthält.

Abgabe: vier berechnete Werte, Erklärung des Rangwechsels und eine Relevanzgrenze.

### QRY-016 – Quellenbereich und Version

Zuordnung: CUR-015. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/QRY-016_Chunk_Provenance/Expected/result-contract.json).

Wählen Sie je einen Chunk aus beiden Dokumentversionen und den Overlapprofilen 0/25.
Ordnen Sie DocId, Version, Reihenfolge, Offset und Länge dem Originaltext zu. Erklären
Sie, warum die summierten Bereichslängen bei Overlap nicht die Länge eindeutigen
Quelltexts darstellen. Entscheiden Sie, ob CHUNK_SIZE=24 ein Modelltokenlimit belegt.

Abgabe: nachvollziehbare Quellenbereiche, Overlaperklärung und Zeichen-/Tokengrenze.

### QRY-017 – Eine Identifierfrage beantworten

Zuordnung: CUR-017/CUR-020. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/QRY-017_Search_Comparison/Expected/result-contract.json).

Wählen Sie für die exakte Kennung MOD_A einen Suchpfad und begründen Sie ihn.
Vergleichen Sie relationale Query, LIKE, optionale Full-Text-Abfrage und Exact Search.
Notieren Sie Tenantfilter und tatsächlich erlaubten Treffer. Beurteilen Sie den
Status bei fehlendem Full-Text. Formulieren Sie, welche Messung vor einer Aussage
über allgemeine Suchperformance oder Sprachsemantik noch fehlen würde.

Abgabe: begründeter Suchpfad, sichtbare optionale Grenze und fehlende Qualitäts-/Messevidenz.

### QRY-018 – Antwort, Ablehnung oder Nichtantwort

Zuordnung: CUR-017/CUR-022. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/QRY-018_Offline_RAG/Expected/result-contract.json).

Beurteilen Sie vier Fälle: aktuelle stützende Sieben-Tage-Quelle, existierendes Zitat
außerhalb des erlaubten Retrievalkontexts, fehlender naher Kontext und zwei erlaubte
aktuelle Quellen mit sieben beziehungsweise neun Tagen. Unterscheiden Sie eine
fehlerhafte Antwortfixture von einer begründeten Nichtantwort. Prüfen Sie die
Ergebniscounts und benennen Sie die Grenzen der festen Claimprüfung und Distanzschwelle.

Abgabe: vier Entscheidungen mit Quellenbindung und zwei Verallgemeinerungsgrenzen.

### QRY-019 – Werte und SQL-Struktur trennen

Zuordnung: CUR-018/CUR-021. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/QRY-019_SQL_Input_Policy/Expected/result-contract.json).

Erklären Sie, warum Quote-/Semikolon-/DROP-Text als separat gebundener Fixturewert
einen erlaubten Literal-Treffer liefern kann, während ein Zusatzstatement abgelehnt
wird. Zeigen Sie im Code die feste Statementstruktur, die separaten Werte und den
eingeschränkten Reader. Erklären Sie, warum ein Tabellenname nicht als gewöhnlicher
Wertparameter ersetzt wird und warum der dbo-Kontrollharness kein Teilnehmerrecht ist.

Abgabe: tatsächliche Wertbindung, getrennte Strukturprüfung und zwei Rechtegrenzen.

### DGN-008 – Modellrecht ist noch keine Inferenz

Zuordnung: CUR-016/CUR-018/CUR-022. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/DGN-008_Offline_Model_Rights/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/DGN-008_Offline_Model_Rights/Expected/result-contract.json).

Ordnen Sie Setup, Ingestion und Retrieval ihre tatsächlichen Tätigkeiten zu.
Vergleichen Sie die Rechte vor und nach Mitigation: Welche zwei Retrievalgrants
entfallen, welche erlaubten Reads/Writes bleiben tatsächlich möglich? Unterscheiden
Sie HAS_PERMS_BY_NAME am External Model von einem Embeddingaufruf. Entscheiden Sie,
ob die feste Endpoint-Bytepolicy TLS, DNS, Firewall oder echten Datenabfluss geprüft hat.

Abgabe: Rollenvergleich, positiver Restbetrieb und zwei offene Providergrenzen.

### DGN-009 – Manipulierte Quellen als Daten behandeln

Zuordnung: CUR-018/CUR-022. Material:
[Demo](../../Demos/09_AI_SQL_Server_2025/DGN-009_Offline_Injection/README.md),
[Ergebnisvertrag](../../Demos/09_AI_SQL_Server_2025/DGN-009_Offline_Injection/Expected/result-contract.json).

Verfolgen Sie die tatsächlich retrievte manipulierte Quelle durch Antwort- und
Toolpolicy. Erklären Sie, warum Trust/Current-Merkmale vom Labowner gesetzt werden
und warum ein Toolname mit nachgestelltem Leerzeichen abgelehnt wird. Unterscheiden
Sie Policyablehnung von den tatsächlichen GRANT-/UPDATE-Rechteverweigerungen.
Benennen Sie die einzige ausgeführte erlaubte Toolaktion und die Grenze des Offlinefalls.

Abgabe: Quellen-/Toolentscheidung, tatsächliche SQL-Grenze und kein Live-Sicherheitsclaim.

## Ergänzende Ergebnisleseaufgabe: RES-008

Zuordnung: CUR-020/TSK-012. Dieser getrennte Materialentwurf ergänzt die acht
implementierten Basisübungen. RES-008 bleibt PROPOSED; volle Demo-/TP-PERF-/
Modulabnahme und tatsächliche Teilnehmererprobung sind offen.
Material: [öffentlicher begrenzter Consumer](../../Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/README.md),
[gebundene aggregierte Beobachtungen](../Project_Planning/SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md)
und [fester numerischer Vertrag für Dimension 384](../../Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/Expected/RES008_D384.result-contract.json).

Lesen Sie die bereits gebundenen Beobachtungen und den Vertrag. Diese Aufgabe
fordert keinen neuen SQL-Lauf. Ein späterer begründeter praktischer Lauf verwendet
ausschließlich den Controller aus der Demo-README, beide YELLOW-Bestätigungen
und optional `--summary`. Kein FWK-010-Manifest wird für diesen Teilpfad behauptet.
Nur SQL 17.0.5005.3/CL170 ist das feste Lastprofil; andere Builds beziehungsweise
2019/2022 enden vor Setup mit dem dokumentierten SKIP. Ownerrechte, authentifizierte
eigene Instanz und tatsächlich bestätigter Cleanup bleiben Voraussetzungen.

1. Berechnen Sie aus vier Dimensionen, fünf Warmups je Dimension und drei
   Dimensionspaaren mit je drei AB-/BA-/AA-Blöcken die 74 Requests, 54 Messfenster
   und 5420 Einzelquerykontrollen. Wie viele A- beziehungsweise B-Fenster tragen
   den Median eines Vergleichspaars? Begründen Sie den Ausschluss von Warmup/AA.
2. Lesen Sie Lauf 1, Dimension 384: CPU-Median 6,5/7 ms, Elapsed-Median
   8169/6151 µs, Logical-Reads-Median 615/2415, jeweils A=32/B=384 und n=6.
   Erklären Sie die unterschiedliche Richtung. Benennen Sie die Batchgröße und
   zwei Grenzen vor einer allgemeinen Aussage zur Dimensionswahl.
3. Erläutern Sie ein Elapsed-Nullfenster trotz positiver CPU und ein N/A-Verhältnis
   bei Baseline null. Welche Beobachtung würde verloren gehen, wenn Nullfenster
   oder große Maxima einfach aus dem Datensatz entfernt würden?
4. Ordnen Sie die 30 numerischen FWK-011-Assertions dem begrenzten Profil zu:
   Source-Rows, Vektorbytes, Fenster- und Queryabdeckung, eine Ergebnisrow.
   Weshalb ändern diese PASSs weder Gesamt-WARN noch PROPOSED? Deuten Sie fehlende
   Wait-/Spillbelege und rohen Plan-DOP 0 ohne erfundene Null-/Workerwerte.
5. Unterscheiden Sie gültige Typdimension, größere tatsächliche Nutzdatenbytes,
   identische synthetische Cosinetreffer und echte Modell-/Antwortqualität.
   Benennen Sie zwei neue fachliche Belege, bevor Zero-Padding oder kleinere
   Dimension als Modelloptimierung empfohlen wird.

Abgabe: nachvollziehbare Populationsrechnung, korrekt begrenzte Batchinterpretation,
sichtbare N/A-/Null-/Ausreißergrenzen und getrennte Aussage zu FWK-PASS/Gesamt-WARN/
offener Modellqualität. Keine Rawidentitäten, Querytexte oder Daten realer Systeme
in den Beobachtungsbogen übernehmen. Der freigegebene Aggregationsframe enthält
ausschließlich den dokumentierten begrenzten numerischen Export.

## Trainerlösungen und Rückfragen

Die folgende Tabelle ist dieselbe gepflegte Quelle für die Trainerfassung.
Teilnehmer bearbeiten zuerst die Aufgaben; die Lösungstabelle wird danach besprochen.
Die vorgeschlagenen Rückfragen prüfen Transfer, keine gemessene Lernwirksamkeit.

| Demo | Erwartete Erklärung im konkreten Lab | Rückfrage |
|---|---|---|
| QRY-014 | Dimension 3 und float32 beschreiben den SQL-Typ. Die fünf Geometriewerte sind keine Sprachembeddings. GEOMETRY_V1/V2 werden fachlich getrennt; Modellversion/Digest und Eingabe-/Chunkprofil gehören zur Provenienz. | Welche Modellinformation fehlt trotz gültigem Typ? |
| QRY-015 | norm1=7, norm2=5, norminf=4, negatives Self-Dot-Product=-25. Euclidean bevorzugt Id1, rohes negatives Dot Product Id2 mit größerer Länge. Nach Normalisierung werden gleichgerichtete Werte gleich lang; Id löst den Tie. | Welche fachliche Relevanzbewertung fehlt dem Geometrieversuch? |
| QRY-016 | DocId/Version plus Bereich erhalten den Quellenbezug; Chunktext wird gegen SUBSTRING geprüft. Overlap wiederholt Bereiche und vergrößert summierte Längen. FIXED-Zeichenchunks bestimmen keine Modelltokenzahl. | Welche Quelle würde ein Chunk ohne Version bezeichnen? |
| QRY-017 | Die Identifierquery liefert genau eine autorisierte Row ohne Modellrequest. Fehlendes Full-Text bleibt WARN. Vier konstruierte Rows belegen weder Sprachsemantik noch einen repräsentativen Geschwindigkeitsvergleich; Tenantfilter sind in jeder Query sichtbar. | Warum genügt eine beobachtete Laufzeit nicht für eine allgemeine Empfehlung? |
| QRY-018 | Sieben Tage sind nur bei aktueller, erlaubter, tatsächlich retrievter stützender Quelle akzeptiert. Kontextfremdes Zitat wird abgelehnt; fehlender Kontext und ungelöster Widerspruch erlauben begründete Nichtantwort. Gesamtfixture: 1 ACCEPTED, 7 REJECTED, 2 ABSTAINED. Feste Satzprüfung und 0,05 sind keine allgemeinen Wahrheits-/Relevanzregeln. | Welche konkrete Quelle stützt welchen konkreten Claim? |
| QRY-019 | Nur kanonisches SQL wird ausgeführt; Werte sind separate Parameter. Quote-/DDL-Text bleibt ein Wert und trifft die synthetische Literalrow. Identifier und Zusatzstatements gehören zur festen Strukturpolicy. Reader hat CONNECT und Objekt-SELECT; dbo-Harness, Serverlogin und Anwendungsservice sind unterschiedliche Grenzen. | Warum sind Policyentscheidung und tatsächlicher Readerfehler zwei Belege? |
| DGN-008 | Setup erstellt und besitzt Modellmetadaten. Ingestion schreibt tatsächlich 7→8→7. Retrieval verliert Policy-SELECT und Modell-EXECUTE; Quellen-SELECT bleibt möglich. EXECUTE-Metadaten sind keine Inferenz, SYNTHETIC_NO_SECRET kein Credential. Endpointablehnung prüft Bytes, keine echte Verbindung. | Welche neue Evidenz wäre für einen tatsächlichen Modellaufruf erforderlich? |
| DGN-009 | Manipulierter Inhalt wird tatsächlich retrievt, seine Anweisungen werden nicht zu SQL. Feste Policy liefert Antworten/Tools je 1 erlaubt, 3 abgelehnt. Nur ReadFact auf Quelle1 wird fest parametrisiert ausgeführt; GRANT/UPDATE scheitern tatsächlich mit 4613/229. Trust wird nicht vom Modell erkannt; kein allgemeiner Injection-/Tenant-/Egressnachweis. | Welche Grenze bleibt trotz dieser erfolgreichen festen Kontrollen offen? |
| RES-008, getrennte Ergänzung | 20 Warmups plus 3×3×6=54 Messfenster; 20×1+54×100=5420 kontrollierte Queries. Pro Paar/Pfad sechs AB-/BA-Fenster; AA drei getrennte Baselinepaare. CPU/I/O sind eigene Request-Counterdifferenzen vor/nach der 100-Query-Schleife samt Overhead an diesen Messgrenzen. Elapsed misst die UTC-Zeit der Schleife samt Tempresult-Inserts; die Messgrenzen sind nicht identisch. Ein Elapsed-Nullfenster bei positiver CPU belegt keine fehlende Arbeit; Zeitauflösung, Reihenfolge und Streuung begrenzen die Interpretation. n=6 ergibt keinen belastbaren Query-p99 oder Signifikanznachweis. Baseline null ergibt N/A, Ausreißer bleiben in Max/Medianpopulation. 30 numerische Invarianten und repräsentative rohe Planattribute belegen keine volle Worker-/TP-PERF-/Modellabnahme; Gesamt-WARN/PROPOSED bleiben. Vor einer echten Dimensionsreduktion fehlen ein Vergleich tatsächlich erzeugter Embeddings mit gebundener Modellversion und eine fachlich gelabelte Retrieval-/Antwortbewertung desselben Korpus. | Welche zusätzliche Qualitätsmessung wäre vor einer echten Dimensionsreduktion erforderlich? |

## Beobachtungsbogen und Bewertungsrubrik

Ein Bogen je Demo genügt; keine Namen, Kontaktdaten oder Inhalte realer Systeme sammeln.
Verwenden Sie bei Bedarf eine synthetische Teilnehmerkennung. Führen Sie tatsächliche
Lehrzeiten erst bei einer späteren genehmigten Erprobung als Istwerte.

| Feld | Eintrag |
|---|---|
| Demo / synthetische Kennung | |
| Vorhersage / gewählter Such- oder Kontrollpfad | |
| Build / CL / Ergebnisstatus | |
| Konkrete Rows, Counts oder Rechtefehler / zugehörige Phase | |
| Erklärung des Mechanismus | |
| Offene Grenze / zulässige Abweichung | |
| Cleanupsummary / unabhängig geprüfte eigene DB-Abwesenheit | |

Didaktischer Vorschlag: pro Demo 0–2 Punkte. Zwei Punkte verlangen einen passenden
konkreten Beobachtungsbeleg und eine korrekte Aussagegrenze; ein Punkt verlangt eines
davon, null Punkte keines. Acht Basisaufgaben ergeben höchstens 16 Punkte. Die getrennte RES-008-Leseaufgabe
hat optional weitere 0–2 Punkte mit denselben Beleg-/Grenzkriterien und verändert
die Basisrubrik nicht. Es wird keine
Bestehensschwelle oder Kompetenzzertifizierung aus ungetestetem Material abgeleitet.
Eine Verwechslung von Fixture und Live-Inferenz, Policy und SQL-Rechten oder
Cleanupsummary und tatsächlicher DB-Abwesenheit wird vor der Freigabe weiterer
Übungen geklärt. Ohne passenden Lauf bleibt der praktische Befund offen.

## Offene Erweiterungen

Live-Modellintegration, echte Credential-/TLS-/Egressfälle, CON-010-Tenants,
IDX-011/IDX-012-ANN, Performance-/Kostenmessung und vollständige Kursprofile gehören
nicht zur Abnahme dieser acht Übungen. Aktuelle FAIL-/Freigabegrenzen stehen im
[Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md).
Der [CL-Slice](../Project_Planning/SQL_SERVER_2025_AI_COMPATIBILITY_REVIEW.md)
bleibt ein historischer FAIL mit eigener offener Wiederaufnahmegrenze. ANN besitzt
inzwischen ein [öffentliches begrenztes Profil](../../Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search/README.md)
und weitere Teilnachweise im aktuellen Ausführungsstand; historische FAILs werden
dadurch nicht gelöscht. Die Aufgaben lockern weder CL170 noch die offenen
Versions-/Provider-/Gesamtabnahmegates. RES-008 ergänzt nur die oben begrenzte
Ergebnisinterpretation; vollständige Performance-/Modellabnahme bleibt offen.
Masterdeck, Speaker Notes, Render-/Office-Prüfung und tatsächliche Generalprobe
bleiben offene Teile von TSK-012/TSK-014.
