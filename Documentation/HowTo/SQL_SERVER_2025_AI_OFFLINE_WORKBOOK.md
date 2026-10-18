# KI mit SQL Server 2025 – Arbeitsheft für den Offlinepfad

Der [VERTIEFUNG-Zweitageskurs](SQL_SERVER_2025_AI_VERTIEFUNG_COURSE.md) verwendet
an Tag 1 dieselben acht Offline-Aufgaben. Der neue Abschnitt
[VERTIEFUNG Tag 2](#vertiefung-tag-2-aufgaben) ergänzt konkrete Beleg-, Rechen-
und Entwurfsaufgaben mit Musterlösungen in diesem Arbeitsheft. Diese Tag-2-
Aufgaben einschließlich RES-008 bleiben im Kurs unbewertet und starten keine
neuen SQL- oder Modellpfade.

Der [STANDARD-Tageskurs](SQL_SERVER_2025_AI_STANDARD_COURSE.md) verwendet alle
acht Offline-Aufgaben und die bestehende Gesamtwertung bis 16 Punkte.
Der [Generalprobenachweis](../Project_Planning/SQL_SERVER_2025_AI_STANDARD_REHEARSAL.md)
belegt die technische/redaktionelle Kursprobe mit erhaltenem optionalen
Full-Text-WARN; die Teilnehmererprobung bleibt offen. Die ergänzenden RES-008-
und E1–E3-Aufgaben gehören nicht zu diesem Tageskurs.

Der [BASIS-Kurs](SQL_SERVER_2025_AI_BASIS_COURSE.md) verwendet aus diesem
Arbeitsheft ausschließlich QRY-014 und QRY-019 als bewertete Aufgaben sowie
QRY-018 als unbewertete Leseaufgabe. Die beiden vorhandenen 0–2-Punkte-Rubriken
ergeben zusammen höchstens vier Punkte. Die vollständige Acht-Aufgaben-Wertung
und alle Musterlösungen bleiben unverändert; der BASIS-Kurs ergänzt keine zweite Lösungssammlung.

Stand: 2026-10-12. TSK-012, Teilentwurf für acht implementierte und lokal qualifizierte
Demos plus die getrennte RES-008-Ergebnisleseaufgabe und drei optionale
Evidenzleseaufgaben. Keine vollständige Curriculum- oder Generalprobenabnahme.
Die Aufgaben, Lösungen und Rubrik sind didaktische Vorschläge; eine tatsächliche
Teilnehmererprobung und gemessene Lehrzeiten stehen aus.

## Vorbereitung und Nachweise

Die [Grundlagenbegriffe](SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md) erklären Modell,
Vektor, Chunk, Retrieval und Antwort vor der ersten Aufgabe.
Der [Trainerleitfaden](SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md) ergänzt die
vorgeschlagene Reihenfolge und Moderation; Lösungen und Rubrik bleiben hier gepflegt.
Das [61-Folien-KI-Deck mit Sprechernotizen](../../Presentations/AI_SQL_Server_2025/README.md)
ist ein geprüfter Materialvorrat. Seine Artefaktprüfung belegt keine Unterrichtsdauer
oder bestandene Teilnehmer-/Generalprobe.

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

Für jede der acht Basisaufgaben zuerst eine Vorhersage notieren, dann den manifestbasierten Lauf
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

## Drei optionale Evidenzleseaufgaben: lokale Komponenten

Diese drei Aufgaben ergänzen die acht Basisaufgaben und RES-008 getrennt.
Sie lesen vorhandene veröffentlichte Teilnachweise; Sie starten dafür weder SQL
noch ein Modell. Keine Installation, Login-/Rollen-DDL, Cloud-/Provideraufrufe
oder Wiederholung privater Qualifikationsskripte. Die Lehrperson verwendet nur die
unten verlinkten öffentlichen Zusammenfassungen. Private Rawreceipts, Vektoren,
Verbindungsnamen, Container-IDs, SIDs oder Secrets werden nicht übernommen.

Für Einsteigende: Eine **Komponente** ist hier ein einzeln geprüfter Schritt,
etwa Vektoren erzeugen, sie in SQL suchen oder eine Verbindung authentifizieren.
Ein erfolgreicher Schritt qualifiziert noch nicht die ganze Anwendung. Eine
**Ergebnis-Erwartung** wird vor dem Versuch festgelegt. Ein fehlgeschlagener
Vergleich bleibt FAIL, auch wenn eine Rückgabe syntaktisch gültig oder der Cleanup
erfolgreich ist. Arbeiten Sie je Aufgabe in vier Schritten:

1. **Zweck:** Welcher einzelne Schritt sollte geprüft werden?
2. **Erwartung:** Welches konkrete Ergebnis war vorher festgelegt?
3. **Beobachtung:** Welcher tatsächliche Befund liegt in der Zusammenfassung vor?
4. **Grenze:** Welche naheliegende Schlussfolgerung folgt daraus noch nicht?

Abgabe je Aufgabe: diese vier kurzen Einträge mit Link zur öffentlichen
Nachweisstelle. Dafür gilt eine eigene optionale Rubrik, keine neue Bestehensgrenze
oder geplante Unterrichtsdauer. Die vorhandenen Teaching-Path-Zeiten bleiben
unveränderte, noch nicht gemessene Planung.

Ein **Receipt** ist das aufgezeichnete Ergebnis eines Modellaufrufs, mit den
gebundenen Eingaben und Rückgaben. Es bescheinigt nicht automatisch fachliche
Richtigkeit. **Top1** bedeutet der erste Treffer in der festgelegten Rangfolge.

### E1 – Vom tatsächlichen Embedding zur SQL-Quelle

Zuordnung: CUR-014/CUR-016/CUR-017; TSK-007/TSK-008-Teilnachweise.
Material: [lokaler Modellkomponentenbeleg](../Project_Planning/SQL_SERVER_2025_AI_MODEL_COMPONENT_REVIEW.md),
[Corpusbeleg](../Project_Planning/SQL_SERVER_2025_AI_MODEL_CORPUS_REVIEW.md) und
[SQL-Persistenz-/Exact-Beleg](../Project_Planning/SQL_SERVER_2025_AI_CORPUS_SQL_REVIEW.md).
Die integrierten PR215–217 betreffen nacheinander getrennte begrenzte Komponenten.

Zweck: Unterscheiden Sie ein tatsächlich zurückgegebenes Modell-Embedding von den
fest zugeordneten Geometrievektoren in QRY-014. Lesen Sie den Corpusfall mit
Nomic: drei synthetische Dokumente und eine Frage. Der öffentliche Corpusvertrag
enthält genau diese englischen Eingaben:

| Eingabe | Unverändertes öffentliches Originalliteral |
|---|---|
| A | `search_document: Synthetic module A contains red building blocks.` |
| B | `search_document: Synthetic module B contains blue building blocks.` |
| C | `search_document: Synthetic module C contains green building blocks.` |
| QUERY | `search_query: Which synthetic module stores crimson building blocks?` |

Deutsch eingeordnet: Die Module enthalten rote, blaue beziehungsweise grüne
Bausteine; die Frage sucht das Modul mit scharlachroten Bausteinen. Die Präfixe
kennzeichnen Dokument und Frage und gehörten zu den damaligen Eingaben. Diese
Tabelle ist Lesematerial, kein Auftrag zu einem neuen Modellaufruf. Zeichnen Sie
die Verbindung vom vorhandenen Modellreceipt zu den gespeicherten SQL-Records
und zum Suchtreffer.

Notieren Sie vorher, wie viele Vektoren für drei Dokumente plus eine Frage zu
erwarten sind und welches Dokument als Top1 festgelegt war. Vergleichen Sie dies
mit Dimension, vollständiger Rücklesung und tatsächlicher SQL-Rangfolge. Ordnen
Sie einen Cosine-Score der Ähnlichkeit zu; ist er eine Wahrscheinlichkeit, dass
die Quelle fachlich richtig ist? Warum lässt der Bestand keinen allgemeinen
Qualitäts- oder vollständigen Live-RAG-Nachweis zu?

### E2 – Erreichbare Generation ist noch keine richtige Antwort

Zuordnung: CUR-016/CUR-017/CUR-022; TSK-007/TSK-008-Teilgrenze.
Material: [abschließender Generationbeleg](../Project_Planning/SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md).
PR218 erhält den Hard6-FAIL und die tatsächlich verbrauchte Requestpopulation.

Zweck: Trennen Sie Modellzugang, Antwortformat und Antwortinhalt. Die feste positive
Erwartung war eine rohe JSON-Antwort mit Entscheidung ANSWER, Quellenkennung A
und Farbwort red. Lesen Sie die tatsächlich beobachteten Antworten und den Grund,
warum nach einem fehlerhaften positiven Fall kein nächster Fall gestartet wurde.

Halten Sie fest, wie viele Inferenz- und Metadatenrequests tatsächlich zur Welle
gehörten. Was ist über die vorbereiteten Fälle mit leerem oder widersprüchlichem
Kontext belegt? Unterscheiden Sie eine ausgegebene Nichtantwort im falschen
positiven Fall von einer geprüften korrekten Enthaltung. Vergleichen Sie diesen
FAIL mit einem optionalen Provider, der gar nicht verfügbar ist: Welche Evidenz
fehlt jeweils? Leiten Sie keine interne Modellursache oder Leistung anderer Modelle ab.

### E3 – SQL-Identität und Tenantzuordnung tatsächlich lesen

Zuordnung: CUR-018/CUR-022; TSK-009-Teilnachweis.
Material: [privater Authentifizierungsfall, öffentliche Zusammenfassung](../Project_Planning/SQL_SERVER_2025_AI_TENANT_LOGIN_REVIEW.md)
und [öffentlicher CON-010-Scope](../../Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/README.md).
Die private Komponente ändert den bisherigen EXECUTE-AS-Scope der öffentlichen Demo nicht.

Zweck: Unterscheiden Sie die tatsächliche Anmeldung einer neuen Verbindung von
EXECUTE AS innerhalb einer vorhandenen Verbindung. Erwarten Sie für Tenant A/B
je die eigene Quelle; was sollte eine authentifizierte, keinem Tenant zugeordnete
Identität sehen? Lesen Sie danach C5, den manipulierten Sessionkontext und die
tatsächlichen Rechtefehler. Welche Identitäts- und Datenbelege gehören zusammen?

Vergleichen Sie außerdem die Cleanupnachweise: C1–C3 besitzen zerstörte eigene
Containernamespaces, aber keine bestandene SQL-Abwesenheitsprüfung; C4/C5 besitzen
tatsächliche Login-/DB-Drops und neue SQL-Abwesenheit. Begründen Sie, warum der
positive C5-Fall weder Pooling, Passwortintegrität noch die vollständige öffentliche
authentifizierte CON-010- oder TSK-009-Abnahme belegt.

## VERTIEFUNG Tag 2 Aufgaben

Diese Aufgaben gehören zum [VERTIEFUNG-Zweitageskurs](SQL_SERVER_2025_AI_VERTIEFUNG_COURSE.md).
Sie verwenden veröffentlichte Zusammenfassungen und ausdrücklich synthetische
Rechenfixtures, keine privaten Receipts oder neuen SQL-/Modellaufrufe. Tag 1
behält seine acht Aufgaben und höchstens 16 Punkte. Alle folgenden Tag-2-Aufgaben
sind unbewertet; auch RES-008 wird hier ohne optionale Zusatzpunktwertung verwendet.
Für die Besprechung jeweils Zweck, vorherige Erwartung, konkreten Beleg und
offene Schlussfolgerung notieren. Lösungen stehen im nachfolgenden Trainerabschnitt.

### ANN und Lifecycle

Material: [öffentlicher V2-Teilnachweis](../Project_Planning/SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md)
und [DML-/Rollenvertrag](SQL_SERVER_2025_AI_IDX012_DML_ROLE_RECORDS.md).
Rechenfixture, ausdrücklich DIDAKTISCH und keine gemessene Suchausgabe:
gleiche erlaubte Kandidaten 1–8, Cosine, k=5; Exact liefert 1/2/3/4/5,
ANN liefert 1/2/6/7/8. Berechnen Sie Recall@5 und nennen Sie die gemeinsamen
Treffer. Erklären Sie, warum doppelte IDs oder eine fremde Tenantpopulation
den Vergleich ungültig machen und die Formel keine Sprachrelevanz misst.

Lesen Sie anschließend die 25 Clientcaptures und acht Rollenkontexte des
begrenzten V2-Records. Trennen Sie COHERENT_PUBLIC_V2 von Generation UNKNOWN,
SQLcleanup TEXTS_COHERENT und voller TP-PERF-Abnahme. Ordnen Sie UPDATE/DELETE/
INSERT/MERGE ohne beziehungsweise mit Index den beobachteten Ergebnissen zu.
Legen Sie eine nächste Prüfung mit unverändertem Build, Kandidaten, tatsächlichem
Plan, Rollback und unabhängigem Cleanup fest. Starten Sie sie nicht im Kurs.

Abgabe: Rechnung, zulässige Population, Rollen-/DML-Grenze und begrenzter Prüfauftrag.

### Messgrenzen und Kosten

Bearbeiten Sie die vorhandene [RES-008-Ergebnisleseaufgabe](#ergänzende-ergebnisleseaufgabe-res-008)
vollständig. Verwenden Sie ausschließlich deren veröffentlichte Beobachtungen.
Ergänzen Sie eine Tabelle mit Messbereich, Population, Einheit und offenem
Nachweis für CPU, Elapsed, Reads, individuelle Querylatenz und Modellqualität.
Die Null-/AA-/Ausreißerfälle bleiben im Vergleich erhalten. Diese Aufgabe
führt keine neue Aggregation privater Rohdaten oder SQL-Qualifikation durch.

### Modellpfade und Provenienz

Material: [Modellpfade](SQL_SERVER_2025_AI_MODEL_PATHS.md) und die vorhandene
DGN-008-Lösung. Entwerfen Sie für die synthetische MOD_A-Wissensbasis eine
Tabelle mit den Spalten Aufrufer, Transport, erlaubte Daten, Modellbindung,
Credentials, endliches Budget und noch fehlender Nachweis. Vergleichen Sie
Controller → lokaler Provider, SQL → HTTPS-Modell, externen Provider und ONNX.
Markieren Sie, an welcher Grenze Text, Vektor und Antwort verarbeitet würden.

Ein vorhandener WhatIf-READY-Befund ist nur eine Planung. Benennen Sie mindestens
zwei Bedingungen vor einem tatsächlichen Aufruf und einen sicheren Ausfallpfad
ohne automatischen Cloudwechsel. Wählen Sie eine passende Offlinealternative,
wenn die Voraussetzungen fehlen. Keine Installation, Secrets oder neuen Aufrufe.

Abgabe: vier Architekturzeilen mit Provenienz, begrenztem Budget und Freigabebedarf.

### SQL Assistenz und Nettonutzen

Material: [begrenzte Originalreaderplanbeobachtung](../Project_Planning/SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md)
und [getrennte Build-/Dropkosten](../Project_Planning/SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md).
Ein synthetischer Assistenzvorschlag fordert einen zusätzlichen INCLUDE-Index.
Lesen Sie die vorhandenen Teilbefunde und erstellen Sie zwei Spalten:
„tatsächlich belegt“ und „vor Empfehlung noch erforderlich“.

Erklären Sie, warum ein tatsächlicher Reader-Seek und unveränderte Results
weder den Nettonutzen noch eine allgemeine Laufzeitverbesserung beweisen.
Formulieren Sie eine widerlegbare Empfehlung für einen begrenzten Workload:
Welche Lesehäufigkeit, DML-Last, Build-/Drop-/Storagekosten und Gegenkontrolle
fehlen? Warum dürfen getrennt instrumentierte Zeitbereiche nicht einfach
addiert werden? Client-Approval ersetzt keine SQL-Berechtigung.

Abgabe: Befund-/Lückentabelle und konkreter nächster Messauftrag ohne Ausführung.

### Betrieb Tenant und Diagnose

Material: [öffentlicher CON-010-Umfang](../Project_Planning/SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md)
und [offene Poolqualifikation](../Project_Planning/SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md).
Erstellen Sie eine Prüftabelle für EXECUTE AS, neue authentifizierte Verbindung
und wiederverwendete Poolverbindung. Welche Identität muss jeweils nachgewiesen
werden, welche erlaubten Rows erwarten Sie und was muss nach Reset gelten?
Eine erfolgreiche einzelne Session erlaubt noch keine Aussage über die beiden
anderen Verbindungspfade. Lesen Sie den tatsächlichen Poolstatus, ohne ihn
aufgrund zerstörter Container oder eines konsistenten Recordformats hochzustufen.

Für RES-009/DGN-011 entwerfen Sie danach ein kleines End-to-End-Protokoll mit
Requestdauer, Fehlern, Durchsatz und getrennten SQL-/Netz-/Modell-/Retryanteilen.
Markieren Sie unbekannte Werte als unbekannt. Eine Batchzeit wird nicht als p99
individueller Requests ausgegeben. RLS, authentifizierte Identität und erlaubter
Antwortkontext bleiben getrennte Kontrollen.

Abgabe: drei Verbindungsgrenzen und ein begrenzter Diagnoseplan mit Abbruch/Cleanup.

### Angriff Evaluation und Transfer

Beginnen Sie mit der vorhandenen DGN-009-Aufgabe und deren fester Antwort-/
Toolpolicy. Entwerfen Sie vier getrennte Fälle für die MOD_A-Wissensbasis:
aktuelle erlaubte Quelle, leerer Kontext, widersprüchliche aktuelle Quellen
und ein manipulierter Absatz mit einer unzulässigen Zusatzaktion. Legen Sie
vorab erwartete Quellen-/Antwort-/Toolentscheidung und tatsächlichen
Rechtebeleg fest. Ein Entwurf ist kein bestandener Test eines Live-Modells.

Die Schlussaufgabe verbindet diese Fälle mit Suchpfad und Kostenentscheidung:
Geben Sie eine begrenzte Empfehlung, einen möglichen Gegenbeleg und den nächsten
Prüfauftrag mit Scope, Erwartung, Abbruch und Cleanup ab. Kein neuer Index,
Provideraufruf oder Wechsel des Unterrichtsmodus entsteht aus dieser Empfehlung.

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

### Lösungen zu VERTIEFUNG Tag 2

Diese Tabelle ergänzt dieselbe gepflegte Trainerquelle. Die Kostenrechnung
verwendet allein die bestehende RES-008-Lösungszeile oben. Es gibt keine neue
Punktwertung oder Kompetenzzertifizierung für Tag 2.

| Aufgabe | Erwartete Erklärung und Grenze | Rückfrage |
|---|---|---|
| ANN und Lifecycle | Gemeinsame IDs 1/2 ergeben 2÷5=0,4 beziehungsweise 40 Prozent Recall@5 der ausdrücklich synthetischen Fixture. Fünf eindeutige Treffer, gleiche erlaubte Kandidaten, k, Modellraum/Metrik und Tie-Regel sind nötig. Keine gemessene ANN- oder Sprachqualität. Im gebundenen SQL-17.0.5005.3-Record stehen vier positive DML-Kontrollen ohne Index vier Fehlern 42231/State1 mit Index gegenüber; Rollback stellt 999 Rows und Transaktionswerte 0/0 her. COHERENT_PUBLIC_V2, 25 Captures und acht Rollenkontexte attestieren keine aktuelle Runtime, Generation oder vollständige TP-PERF. SQLcleanup bleibt TEXTS_COHERENT. | Welcher echte Plan- und Populationsbeleg würde einen ANN-Geschwindigkeitsclaim erst prüfbar machen? |
| Messgrenzen und Kosten | Vorhandene RES-008-Lösung: 20 Warmups, 54 Messfenster, 74 Requests, 5420 Querykontrollen; n=6 je A/B-Pfad eines Paars. Im ersten 384er-Paar steigt CPU 6,5→7 ms und Reads 615→2415, während Elapsed 8169→6151 µs fällt. Unterschiedliche Messgrenzen, geringe Population und feste Geometrie erlauben keine Dimensionsregel, Query-p99 oder Modellqualitätsaussage. N/A, Nullfenster und Ausreißer erhalten. | Welche Population würde eine individuelle Request-p99 benötigen? |
| Modellpfade und Provenienz | Controllerseitiger lokaler Modellaufruf und SQL-seitiger HTTPS-Aufruf sind verschiedene Architekturen. Jede Zeile nennt tatsächlichen Caller/Transport, zugelassenen Kontext, Modellversion/Digest/Dimension, Secretgrenze, Request-/Retry-/Zeitbudget und offenen Nachweis. Cloud erfordert getrennte Egress-/Kosten-/Verarbeitungsfreigabe; ONNX hat eigene OS-/Runtime-/Hostgrenzen. WhatIf READY ist keine Inferenz, Modell-EXECUTE kein APIerfolg. Bei fehlender Voraussetzung bleibt der feste Offlinepfad; kein automatischer Cloudfallback. | Welcher Nachweis prüft den Rückgabewert vor dem VECTOR-INSERT? |
| SQL Assistenz | Gleiche Results und zwei private Originalreaderplanprofile sind begrenzte Belege, kein Indexnettonutzen. Die getrennten Owner-INSERT-/Rollback- und Build-/Dropfenster besitzen eigene Instrumentierung. Vor einer Empfehlung fehlen gleiche Workloadpopulation und Gewichte für Reads/DML, vollständige Kosten und Gegenkontrollen. Keine Addition ungleicher Messgrenzen. Ein konkreter Reader-Seek ist kein allgemeiner Speedup; Runtime-/TP-PERF-/Nettonutzen bleiben NOT_ESTABLISHED. | Welcher Gegenbefund würde die Empfehlung widerlegen? |
| Betrieb Tenant und Diagnose | EXECUTE AS prüft einen DB-Kontext innerhalb einer Session; frische Anmeldung braucht eigene authentifizierte Verbindungsidentität und Rowkontrolle; Pooling zusätzlich echten Reuse, Reset und wiederholte Identitäts-/Tenantprüfung. Ein fremder Sessionwert darf A nicht zu B machen, Unmapped bekommt keine Rows. Ein begrenzter Owner- oder Recordnachweis schließt die offene Poolqualifikation nicht. SQL-Cleanup, Namespaceabbau und bekanntes Clientende getrennt belegen. End-to-End-Diagnose braucht individuelle Requests, getrennte Fehler-/Zeitanteile und vollständige Population. | Was bleibt nach reinem Containerabbau über SQL-Abwesenheit unbekannt? |
| Angriff und Transfer | Im Entwurf darf nur aktuelle erlaubte Evidenz eine Antwort tragen. Leerer oder ungelöst widersprüchlicher Kontext verlangt begründete Nichtantwort; ein Quellenabsatz erteilt keine Toolrechte. Die vorhandene DGN-009-Policy und echte GRANT-/UPDATE-Verweigerungen sind feste Kontrollen, keine Live-Modellabnahme. Jede Empfehlung nennt erlaubte Population und Scope, Gegenbeleg sowie endlichen Prüf-/Abbruch-/Cleanupauftrag. Fehlende Ausführung bleibt offen. | Warum ist eine falsche Nichtantwort im positiven Fall kein bestandener Enthaltungstest? |

### Lösungen zu den drei optionalen Evidenzleseaufgaben

Diese Lösungseinträge gelten ausschließlich für die verlinkten Teilnachweise.
Sie sind didaktische Vorschläge, keine neue Ausführung oder Teilnehmerabnahme.

| Aufgabe | Erwartete Erklärung zum vorhandenen Befund | Rückfrage |
|---|---|---|
| E1 | Corpus-C1 erzeugte vier vollständige Nomic-Vektoren mit je 768 endlichen Koordinaten: drei Dokumente plus eine Frage. Der getrennte SQL-C1 speicherte und las alle vier VECTOR(768)-Records zurück; gesucht wurden die drei Dokumente. Vorab erwartetes und tatsächlich beobachtetes eindeutiges Top1 ist A. Modell- und SQL-Cosines werden unabhängig nachgerechnet und liegen innerhalb der vorher festgelegten 1e-5-Toleranz; SQL-Score für A etwa 0,80313. Score ist keine Wahrheitswahrscheinlichkeit. Der SQL-Schritt verwendete das vorhandene Receipt, keine neue Inferenz. Numerischer Roundtrip belegt keine bitgleichen physischen VECTORbytes, dieser einzelne synthetische englische Fall keine allgemeine Relevanz-/Antwortqualität oder vollständigen Live-RAG. PR215 ist der vorgelagerte Modellkomponentenbeleg; seine zwei separaten Modellaufrufe werden nicht als die vier Corpusaufrufe ausgegeben. | Welcher neue Beleg wäre für eine generierte, tatsächlich quellengestützte Antwort erforderlich? |
| E2 | Hard6 endet FAIL; tatsächlich fünf Inferenz- und 31 Metadatenrequests in der Generationwelle, einschließlich genau einer C4-Vorlagendiagnose. Die vorgelagerte Discovery ist separat und wird nicht in diese Counts umgedeutet. Keine richtige positive Antwort; Nichtantworten oder Codefences verfehlten den vorher festgelegten Vertrag. C2 scheiterte bereits am Sourcegate ohne Modellcall. Fail-first verhinderte sämtliche Negativcase-Aufrufe: deshalb weder bestandene Empty-/Conflict-Enthaltung noch allgemeiner Sicherheitsbeleg. Ein erreichbarer Provider und eine erhaltene Rückgabe sind andere Befunde als ein UNAVAILABLE-Pfad ohne Inferenz; keiner liefert für sich Antwortqualität. Interne Ursache und andere Modelle bleiben unbekannt. | Warum darf eine im positiven Fall falsche Nichtantwort nicht als erfolgreiche ABSTAIN-Kontrolle gezählt werden? |
| E3 | C5 bestätigt drei frische authentifizierte SQL-Loginverbindungen mit passenden Server-/Original-/DBuser-Identitäten und SIDs. A/B erhalten je nur die eigene vollständige Quelle samt VECTOR(3), Unmapped besitzt positive Authentifizierung und null Rows. Der auf B gesetzte Sessionkontext ändert A nicht; Reset und tatsächliche SQL-Verweigerungen sind belegt. 23 Vollstates und fünf Guardfehler begrenzen die Zustands-/Eigentumskontrolle. C1–C3 bleiben FAIL mit SQL-Abwesenheit NOT_ESTABLISHED trotz zerstörter eigener Namespaces; C4/C5 besitzen tatsächliche gehaltene Login-Drops vor DBdrop plus neue getrennte SQL-Abwesenheit. Kein Pooling-, Passwortintegritäts-, Seitenkanal- oder öffentlicher authentifizierter CON-010-/TSK-009-Gesamtnachweis; Owner ist ausdrücklich privilegierter Fixtureharness. | Welche zusätzliche Prüfung wäre für echte wiederverwendete Poolverbindungen nötig? |

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
die Basisrubrik nicht. E1, E2 und E3 werden zusätzlich jeweils getrennt mit optionalen
0–2 Punkten nach denselben Beleg-/Grenzkriterien bewertet (zusammen höchstens sechs
weitere optionale Punkte). Keine dieser Ergänzungen verändert die acht Basisaufgaben,
deren 16 Punkte oder die separate RES-008-Rubrik. Es wird keine
Bestehensschwelle oder Kompetenzzertifizierung aus ungetestetem Material abgeleitet.
Eine Verwechslung von Fixture und Live-Inferenz, Policy und SQL-Rechten oder
Cleanupsummary und tatsächlicher DB-Abwesenheit wird vor der Freigabe weiterer
Übungen geklärt. Ohne passenden Lauf bleibt der praktische Befund offen.

## Offene Erweiterungen

Die drei neuen Leseaufgaben behandeln begrenzte lokale Komponenten, keine
praktische Erweiterung der acht Basisdemos. Vollständige Live-Modellintegration,
echte Credential-/TLS-/Egressfälle, öffentliche authentifizierte CON-010-Tenants,
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
Das [61-Folien-KI-Deck und seine editierbaren Sprechernotizen](../../Presentations/AI_SQL_Server_2025/README.md)
besitzen dokumentierte vollständige Render-/Einzelbild- und native PowerPoint-
Prüfung. Teilnehmererprobung, gemessene Lehrzeiten, vollständige Lehrpfadabnahme
und tatsächliche Generalprobe bleiben offen. Diese Leseaufgaben erzeugen keine
neue Deck-/Office-/SQL-/Modellprüfung.
