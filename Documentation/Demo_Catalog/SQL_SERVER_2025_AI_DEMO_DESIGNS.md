# KI-Workstream – vollständiger Demo-Katalogentwurf

Stand: 2026-10-11. Planung: `TSK-003`, Entscheidung: `DEC-073`.
Der ursprüngliche Planungsschnitt führte alle 18 Demos als **PROPOSED**. Seit dem
Implementierungsauftrag vom 2026-10-11 besitzen QRY-014 bis QRY-019 ausführbare
[Demopakete](../../Demos/09_AI_SQL_Server_2025/README.md); deren aktueller Code- und
Nachweisstand ist im [Katalog](README.md#lokale-ki-demos--implementierung-vom-2026-10-11) geführt.
Die übrigen 12 Entwürfe bleiben PROPOSED. QRY-018 implementiert ausschließlich
den Offline-Replay; sein Live-Modellpfad bleibt getrennt und offen.
Die Kennungen sind über die zentrale Registry abgeleitet; ihre endgültige Registrierung erfolgt
mit Planungsintegration. [Workstream-Plan](../Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md)
und [Featurematrix](../Research/SQL_SERVER_2025_AI_FEATURE_MATRIX.md) sind die verbindlichen Ergänzungen.

## Gemeinsamer Vertrag aller folgenden Entwürfe

Jede Demo übernimmt FWK-001–FWK-012 und die Phasen Preflight → Setup → Baseline →
Demonstration → Observation → Mitigation → Comparison → Cleanup. Wiederverwendbare
Phasen dürfen mitgelieferte Frameworkbausteine aufrufen, nicht verborgen andere Demos voraussetzen.
Jede Demo besitzt später eigenes Runbook, Manifest-/Ergebnisvertrag und getrennte Setupphase.

Primärversion ist Engine 17.x, CL 170, Enterprise Developer; Windows/Linux nach Featurematrix.
Enterprise/Standard/Express sind dokumentierte Featureeditionen, aber hier noch keine
qualifizierte Runtime-Matrix. 15.x/16.x werden vor Featureparsing als unsupported erkannt.
Bei Preview wird Zustand geprüft, nicht ungefragt geändert. Setup benötigt eine explizit
bereitgestellte markierte Labdatenbank oder den bestehenden FWK-002-Bootstrap mit getrennten
DB-Erstellungsrechten. Setuprolle darf darin Tabellen/Prozeduren und erforderliche Rollen
anlegen; Abfragerolle erhält nur SELECT bzw. EXECUTE auf den benannten Labobjekten.
DB-DDL umfasst CREATE TABLE und ALTER auf dem Labschema, Index-DDL ALTER auf der Tabelle.
Teilnehmerabfragen benötigen kein sysadmin. Diagnosegrants werden nur bei gewählter Evidenzquelle
erteilt; SQL-2025-DMV-Rechte wie VIEW DATABASE PERFORMANCE STATE werden im Detaildesign geprüft.

Preflight liest Build/Edition/OS/CL, Objektrechte, Marker, Previewoptionen, Tools und freie
Ressourcen. Optionaler Providerzugriff ist zusätzlich ausdrücklich freizugeben und zu prüfen.
Fehlende Voraussetzungen ergeben vor Mutation kontrollierten SKIP gemäß FWK-012; nach Setup
auftretende Vertrags-/Timeout-/Rechte-/Cleanupfehler ergeben FAIL. Kein Fehler wird als SKIP versteckt.

Alle Daten sind synthetisch: Geometrievektoren, technische Fantasiedokumente, Tenant A/B,
versionsgebundene Chunks, Fragen und vorher fixierte Relevanzurteile. Sprachembeddings werden
mit Modell/Version/Digest/Dimension/Normalisierung getrennt geführt. Künstliche Vektoren und
Antwortfixtures behaupten weder gemessene Inferenz noch echte semantische Modellqualität.

### Ressourcen- und Safetyprofile

Die folgenden Limits sind **vorgeschlagene Abbruchgrenzen**, keine universellen Performancewerte.
TSK-004 qualifiziert sie auf dem gewählten Lab vor Runtimefreigabe. Mindesthardware für den
kleinen SQLpfad: vier logische CPU-Kerne, 16 GiB RAM, 10 GiB freier Laborplatz. Ein kleineres
Profil muss getrennt qualifiziert werden. Modellpfade brauchen zusätzliche modellabhängige
Kapazität; GPU ist optional, nie Voraussetzung des Pflichtpfads.

| Profil | Safety / Sessions / Budget | Daten-/Ressourcenobergrenze | Konfiguration / Runtimeabhängigkeit |
|---|---|---|---|
| Lokal | Grün; 1 Session; 180 s regulär, 60 s Cleanup | 1000 Rows, 64 MiB Text, 512 MiB DB, d=3 oder vorbereitetes Profil | 17.x/CL170, vorhandener Frameworkrunner/sqlcmd; kein Netz/Modell |
| Preview klein | Grün; 1 Session; 300 s + 60 s Cleanup | 1000 Rows, d=3/32, 512 MiB DB, MAXDOP1 | vorher genehmigtes PREVIEW_FEATURES in eigener DB; Indexgeneration vorab binden |
| Last | Gelb; 1–8 eigene Sessions; 900 s + 120 s Cleanup | höchstens 100000 Rows, d=32/384/768/1536, 3 GiB DB, 2 GiB definierter Mess-Workspace | bestätigte Wegwerfinstanz mit fixiertem CPU/RAMprofil; FWK-006-Signale/Stop; kein globaler Cacheeingriff |
| Lokales Modell | Gelb; 1 SQL- und 1 eigene Anwendungssession; 600 s + 120 s Cleanup | maximal 50 Embedding-/LLM-Requests, 32 Chunks pro Batch, 2048 Zeichen je Chunk; 1 GiB Korpus | vorab genehmigter eigener lokaler Modellservice, Modell-/Tokenbudget, TLS/APIprobe; keine Instanzoption im Demolauf ändern |
| Externes Modell | Gelb; dieselben endlichen Limits | zusätzlich vorab genehmigtes Geldbudget und max. ein Retry je Request | eigener freigegebener Provider, Secretquelle und Egress-Allowlist; bei fehlendem Geldbudget SKIP |
| Instanz/ONNX | Rot; ausschließlich eigene Wegwerfinstanz; 600 s + 180 s Cleanup | 50 Calls, Modell-/DLL-/RAM-/Diskobergrenzen vor Freigabe fixieren | Windows, ML Services, Preview, externe AI-Runtime; OS-/Instanzänderung braucht eigenen Resetpfad |

Abbruch bei Zeit-/Row-/Request-/DB-/Workspaceüberschreitung, Kill-Switch, nicht erfüllter
Eigentumsprüfung, Fehler oder fehlender Berechtigung. Ein nicht überwachbares erforderliches
Limit verhindert den Start. Recovery stoppt nur eigene markergebundene Sessions/Prozesse,
beendet eigene XE-Sessions, stellt gesicherte DBoptionen wieder her und entfernt ausschließlich
Objekte/Ressourcen mit vollständig passendem Projekt-/Demo-/Run-Token. Unabhängiger
Abwesenheitscheck ist Pflicht; fehlgeschlagener Cleanup bleibt FAIL_CLEANUP.
Vorbestehende Provider/Modelle/Instanzoptionen werden nie als eigene Ressourcen gelöscht.

## QRY-014 – Vektortypen und Dimensionsgrenzen

- Ziel/Zuordnung: `CUR-013`/`CUR-014`, `TSK-005`; VECTOR/JSON und Modellraum trennen.
  Lokal/Grün; SELECT/INSERT auf eigene Vektortabelle; float16 nur separat Preview klein.
- Preflight/Setup: Typ-/CL-/Buildprüfung, markierte DB; Geometrievektoren und fehlerhafte Dimensionsfixture.
  Baseline: gespeicherte float32-Werte samt VECTORPROPERTY.
- Demonstration/Observation: gültige/ungültige Konvertierungen und optional float16;
  Dimension, BaseType und Rundungsdifferenzen sehen. Keine echten Modellgewichte.
- Mitigation/Comparison: Dimension/Modellprovenienz vor INSERT prüfen und Fehlwerte ablehnen.
  Cleanup: eigene Tabellen/DB und ausschließlich selbst geänderte Previewoption wiederherstellen.
- Test/Ergebnis/Abnahme: TP-RUN, reproduzierbarer Seed, exakte Dimensions-/Typinvarianten,
  negative Eingaben ohne Teilpersistenz, float16 optionaler SKIP, unabhängiger Cleanup.
  Grenzen am konkreten Build bestätigen; keine Speicherersparnis ohne Messung.
- Quellen/Abhängigkeit: `SRC-072`, `SRC-076`, `TSK-004`, Framework.

## QRY-015 – Distanz, Norm und Normalisierung

- Ziel: `CUR-013`/`CUR-014`, `TSK-005`; cosine/euclidean/negatives dot erklären.
  Lokal/Grün; reine SELECTs und optional gespeicherte Normalisierung in eigener Tabelle.
- Preflight/Setup: skalare Funktionen; eigene nichtnull Geometriepaare, Null-/Zero-Gegenfälle.
  Baseline: manuell hergeleitete Norm-/Distanzwerte mit tolerierter Floating-Point-Abweichung.
- Demonstration/Observation: norm1/norm2/norminf und normalisierte Vektoren;
  Score-/Rankingunterschiede ohne Index. Zero-/Nullverhalten separat erfassen.
- Mitigation/Comparison: passende Metric und festgelegte Normalisierung; keine gemeinsame
  Suche verschiedener Modellräume. Cleanup: eigener Tabellen-/DB-Lifecycle.
- Test/Ergebnis/Abnahme: TP-RUN; norm2 des normalisierten Nichtnullvektors nahe 1,
  Selbstdistanz für euclidean/cosine nahe 0; dot gesondert bewerten; dokumentierte Fehlfälle.
- Quellen/Abhängigkeit: `SRC-073`–`SRC-075`; `TSK-004`, Framework, keine Provider.

## QRY-016 – Chunking, Overlap und Provenienz

- Ziel: `CUR-015`, `TSK-005`; Import und reproduzierbare Chunkzuordnung.
  Lokal/Grün; CREATE/INSERT/SELECT auf eigenen Documents/Chunks.
- Preflight/Setup: CL170/CHUNKS, deterministische deutsche Fantasietexte mit zwei Versionen.
  Baseline: vollständiger Text und Quellenbereiche; FIXED ohne Overlap.
- Demonstration/Observation: verschiedene Zeichenlängen und 25 Prozent Overlap;
  Ordnung, Duplikate und getrennte Erklärungen; Chunking ist kein Tokenizer.
- Mitigation/Comparison: Version/Bereich/Parameter binden, neue Version getrennt importieren;
  sinnvolle Chunkparameter gegen Fragefixture bewerten. Cleanup: eigene Korpusobjekte/DB.
- Test/Ergebnis/Abnahme: TP-RUN; Quellenrekonstruktion, Reihenfolge, gleiche Eingaben gleicher
  fachlicher Chunkbestand, negative Größe/Overlap, kein Modellcall, unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-079`, `TSK-004`, Framework; keine externen Importdateien nötig.

## QRY-017 – Relationale, Full-Text- und semantische Suche

- Ziel: `CUR-017`/`CUR-020`, `TSK-005`; Suchzweck und Qualitätsmaß unterscheiden.
  Lokal/Grün für kleines Korpus; skaliert Last/Gelb. Full-Text-Komponente optional.
- Preflight/Setup: SELECT, Full-Text-Katalog-/Index-DDL nur Setuprolle, Komponente installiert;
  synthetischer Korpus mit Identifier-/Keyword-/Paraphrasenfragen und freigegebenen Relevanzurteilen.
- Baseline: relationaler Index-/Filterpfad; Full-Text-Populationszustand vor Messung abwarten.
  Demonstration: CONTAINS/FREETEXT und Exact-Distance-Ranking, gleiche erlaubte Dokumente.
- Observation: Ergebnisidentitäten/Qualität, Plans/IO/CPU/Elapsed; konstruierte Vektoren nur
  Mechanikfixture. Echte Semantik aus separat qualifiziertem vorbereitetem Embeddingbestand.
- Mitigation/Comparison: Suchpfad passend zum Fragetyp oder kontrollierte Kombination wählen.
  Cleanup: eigene Full-Text-/Index-/Korpusobjekte/DB; keine globale Katalogänderung.
- Test/Ergebnis/Abnahme: TP-RUN/TP-PERF, Identifier korrekt, Relevanzrubrik getrennt von Recall,
  keine pauschale Überlegenheit; fehlendes Full-Text führt zum gekennzeichneten optionalen SKIP/WARN.
- Quellen/Abhängigkeit: `SRC-073`, `SRC-087`, `SRC-095`, bestehende Full-Text-Produktreferenz
  aus `SRC-100`; `TSK-004`, Framework; echte Embeddings zusätzlich `TSK-007`.

## QRY-018 – RAG mit überprüfbarer Retrieval-Evidenz

- Ziel: `CUR-017`/`CUR-022`, `TSK-008`; vollständige transparente Verarbeitung bewerten.
  Offline-Replay Lokal/Grün; echte lokale Inferenz Lokales Modell/Gelb, Cloud separat optional.
- Preflight/Setup: erlaubte Korpus-/Modellversion, SELECTrolle; Documents/Chunks/Fragen und
  Antwortfixtures mit richtigen, unbelegten, fehlenden und widersprüchlichen Aussagen.
- Baseline: Frage ohne Kontext als ausdrücklich gespeicherte Fixture. Demonstration: Import,
  Chunking, vorbereitetes oder live erzeugtes Embedding, Speicherung, Retrieval, Quellenprüfung,
  begrenzte Kontextübergabe und Antwort mit Quellenstellen. Jeder Schritt sichtbar.
- Observation: Claim-zu-Quellenstelle, fehlende Evidenz, Antwortqualität und Token-/Zeitaufteilung.
  Mitigation: Abstention, Version/Widerspruch und erlaubte Quellen nennen; gleiche Fragen vergleichen.
- Cleanup: eigene DB/Anwendungsfixtures/prozessbezogene Ressourcen; flüchtige Prompts/Antworten entfernen.
  Kein externes Modell löschen, keine unkontrollierte Antwort-/Promptpersistenz.
- Test/Ergebnis/Abnahme: TP-RUN; jeder akzeptierte Claim hat erlaubte stützende Retrievalstelle;
  unzureichende Evidenz ergibt begründete Nichtantwort, Replay/Live klar getrennt; Cleanupcheck.
- Quellen/Abhängigkeit: `SRC-079`–`SRC-081`, `SRC-095`; `TSK-005`, Live zusätzlich `TSK-007`.

## QRY-019 – KI-generiertes SQL und Injection-Abwehr

- Ziel: `CUR-018`/`CUR-021`, `TSK-009`; Modelloutput sicher prüfen.
  Lokal/Grün; synthetische SQL-/Promptfixtures, enges SELECT-/Prozedur-EXECUTE-Recht.
- Preflight/Setup: nichtprivilegierte Rolle, eigene kleine Tabellen und fester Querytemplate.
  Baseline: erlaubter parameterisierter Wertfilter und korrekte Ergebnismenge.
- Demonstration/Observation: Quote-/Mehrstatement-/Identifierfixture fordert Zusatzquery oder DDL;
  Absicht und Fehler sichtbar, keine privilegierte Ausführung eines Angriffstrings.
- Mitigation/Comparison: sp_executesql-Wertparameter, feste Statementstruktur und Identifierallowlist;
  Änderungen nur als geprüfter Entwurf. Cleanup: eigene Rolle/Prozedur/Tabellen/DB.
- Test/Ergebnis/Abnahme: TP-RUN; Attacke verändert keine Querystruktur, unerlaubte Aktion verweigert,
  erlaubter Fall funktioniert, Syntax-/Ergebnisreview und unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-099` (SQL Injection und sichere Eingaben),
  `SRC-091`, `TSK-005`, Framework; LLM-Livezugang nicht erforderlich.

## QRY-020 – Lokale Embeddings über Ollama

- Ziel: `CUR-016`, `TSK-007`; reale lokale Inferenz und direkte SQL-REST-Grenze zeigen.
  Lokales Modell/Gelb; Instanzaktivierung separat Rot, niemals verdeckt im Demolauf.
- Preflight/Setup: vorbereitetes freigegebenes lokales Modell mit Lizenz/Digest; REST bereits aktiviert,
  TLS-Proxy aus Enginekontext erreichbar; Model-EXECUTE, Modell-/Credential-DDL nur Setuprolle.
  Eigene External-Modeldefinition und Chunktabelle; Cloudrouting explizit gesperrt.
- Baseline: konstruierter Vektor ohne Inferenz, daneben definierter direkter /api/embed-Request.
  Demonstration: AI_GENERATE_EMBEDDINGS mit passendem API_FORMAT/Modell und geprüfter Speicherung.
- Observation: Dimension/Null/Truncation, Modell-/Loadzeit, RESTstatus, SQL-/Gesamtzeit.
  Mitigation: geprüfte Chain/Endpointformat/Chunks/Batch- und Tokenlimits; gleiche Fragen vergleichen.
- Cleanup: eigene Modelle/Credentials/DB, eigene Proxyprozesse nur mit Ownershipbeleg;
  vorbestehenden Service erhalten. Instanzzustand nur im separaten roten Bereitstellungslifecycle restaurieren.
- Test/Ergebnis/Abnahme: TP-RUN; reale Inferenz nachgewiesen, gültiger Vektor und Modellraum,
  falscher Trust/HTTP/Auth/Dimension vor Persistenz abgelehnt; Limits und Cleanup bestanden.
- Quellen/Abhängigkeit: `SRC-080`–`SRC-082`, `SRC-085`/`SRC-086`; `TSK-004`, lokale Freigabe.

## QRY-021 – Optionale externe Embeddings

- Ziel: `CUR-016`/`CUR-022`, `TSK-007`; externen Datenfluss/Kosten messen.
  Externes Modell/Gelb; nur genehmigter Azure-OpenAI-Endpoint, keine Dienstbereitstellung in Demo.
- Preflight/Setup: explizite Provider-/Region-/Kosten-/Egressfreigabe, TLS/API und Credentialpfad;
  Secret außerhalb Repository; Model-EXECUTE, Credentialerstellung getrennte Setuprolle.
- Baseline: derselbe synthetische Chunkbestand im lokalen Pfad. Demonstration: begrenztes
  Embeddingbatch, Quota-/Fehlerfixture; keine echten Kostenfehler provozieren.
- Observation: Payload-/Tokenmenge, Requests/Retry, Dimension, Netz-/Modell-/Gesamtzeit und Kostenmenge.
  Mitigation: kleine freigegebene Batches, Cache/Re-Embedding nur bei Änderung, Budgetstop;
  Vergleich innerhalb des gleichen Modellraums, keine Distanzwerte verschiedener Modelle gleichsetzen.
- Cleanup: eigene DBmodelle/Credentials/Fixtures; keine Providerressource löschen;
  Secretwerte nicht loggen. Test: TP-RUN, kein Call ohne Opt-in, maximal genehmigtes Budget,
  Secretscan, Fehler-/Retry-/Dimension-/Cleanupfälle. Qualität und Kosten ohne pauschalen Gewinner.
- Quellen/Abhängigkeit: `SRC-080`–`SRC-082`, `SRC-087`/`SRC-088`/`SRC-096`; `TSK-004`, externe Freigabe.

## QRY-022 – Optionale lokale ONNX-Embeddings

- Ziel: `CUR-016`/`CUR-022`, `TSK-007`; lokale Inferenz mit Native-Code-/Instanzgrenze.
  Instanz/ONNX/Rot; Windows-Wegwerflab, kein Linuxclaim, keine Standard-CI.
- Preflight/Setup: explizite High-Impact-Freigabe, Machine Learning Services, vertrauenswürdige
  Runtime-/Tokenizer-/Modelldateien, Lizenz/Hash/RAMbudget; ALTER SETTINGS nur Bereitstellungsrolle,
  minimale qualifizierte Dateirechte; Optionen sichern und eigene Modelldefinition registrieren.
- Baseline: dieselben synthetischen Eingaben ohne Inferenz; Demonstration: lokale ONNX-Embeddingaufrufe.
  Observation: Typ/Dimension, Runtime-/SQL-Ressourcen und Input-/Supply-Chain-Provenienz.
- Mitigation/Comparison: Hash-/Lizenz-/Versionsabweichung ablehnen, Instanz-/Dateizugriff einschränken.
  Keine absichtlich schädliche DLL oder Modellausführung. Cleanup: eigene Objekte/Dateien,
  Optionsrestore und kompletter Reset der eigenen Instanz mit unabhängiger Abwesenheitsprüfung.
- Test/Ergebnis/Abnahme: TP-RUN plus rotes Resetprofil; reale lokale Inferenz, negative Metadaten-
  und fehlende Runtimefälle, Limits/Recovery; Linuxwiderspruch bleibt offen statt PASS.
- Quellen/Abhängigkeit: `SRC-080`, `SRC-083`/`SRC-084`; `TSK-004`, eigene ONNX-Freigabe.

## IDX-011 – Exact gegen Approximate Vector Search

- Ziel: `CUR-019`, `TSK-006`; Recall/Laufzeit und Planpfad gemeinsam bewerten.
  Preview klein/Grün; skaliert Last/Gelb; ALTER auf eigener Basistabelle, SELECT für Queryrolle.
- Preflight/Setup: Preview bereits freigegeben, konkrete Indexgeneration, clustered INT-PK,
  passender Vektortyp/Metric und genügend Rows am Build; synthetisch nichtdegenerierte Vektoren.
- Baseline: exaktes Top-k mit gleicher Kandidatenmenge/Metric/Tieregel.
  Demonstration: Indexbuild und generationspassendes VECTOR_SEARCH, selektive Filter variieren.
- Observation: tatsächlicher Plan/Index/Fallback, Ergebnismengen, Recall@k und CPU/IO/Elapsed.
  Mitigation/Comparison: geeigneten Such-/Filterpfad auswählen; keine Azure-Iterativfilterannahme.
- Cleanup: eigener Index/DB, gesicherte selbst geänderte Optionen. Test: TP-PERF;
  Oraclevergleich, Fallback gekennzeichnet, keine Indexverwendung ohne Planbeleg,
  Qualität vorab fixiert, Performance ohne feste Beschleunigungsratio; unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-073`, `SRC-077`/`SRC-078`/`SRC-094`/`SRC-097`; `TSK-005`, Previewfreigabe.

## IDX-012 – Vector-Index-Build, DML und Maintenance

- Ziel: `CUR-019`/`CUR-020`, `TSK-006`; Kosten/Freshness am tatsächlichen Indexformat trennen.
  Last/Gelb; eigener Index-DDL-/DML-Setupkontext, keine Produktionswartung.
- Preflight/Setup: gebundener Build und Indexgeneration, Ressourcen/Stop; deterministisches
  Update-/Delete-/Insert-Korpus. Baseline: geladenes Korpus und Exact-Oracle vor Indexbuild.
- Demonstration: Build messen; kontrollierte Datenänderung im erlaubten Format, gegebenenfalls
  dokumentierte Read-only-Grenze bzw. ausdrücklich gewählter ALLOW_STALE_VECTOR_INDEX-Labpfad.
- Observation: Buildzeit, DB/Indexspeicher, Writes/TempDB, Aktualität/Recall;
  neue Maintenance-DMV nur bei belegter Buildunterstützung, nicht automatisch auf 17.x übertragen.
- Mitigation/Comparison: eigener Drop/Recreate nach qualifiziertem Updatepfad, Exact-Gegenprobe;
  manuelle Aktualisierungskosten bilanzieren. Cleanup: eigene DB/Index, Optionsrestore, Sessions stoppen.
- Test/Ergebnis/Abnahme: TP-PERF; gebundene DML-/Stale-Erwartung, Ergebnis-/Freshnesscheck,
  Abbruch beim Build und nach DML, unabhängiger Cleanup; keine dauerhafte Previewgarantie.
- Quellen/Abhängigkeit: `SRC-077`/`SRC-078`/`SRC-097`; `IDX-011`, `TSK-004`.

## RES-008 – Vektordimensionen und Ressourcenbedarf

- Ziel: `CUR-020`, `TSK-010`; Dimension/Precision/Storage/CPU empirisch verbinden.
  Last/Gelb; SELECT, Setup-DDL/INSERT; float16 als separates Previewprofil.
- Preflight/Setup: Hardware-/DB-/Memorylimits, freigegebene Dimensionen 32/384/768/1536;
  gleiches N und definierte synthetische Verteilung. Baseline: float32/kleine Dimension.
- Demonstration/Observation: Dimension einzeln variieren, Speicher/Reads/CPU/Elapsed, Plan,
  Grants/Spills/TempDB bei relevanten Sort-/Joinoperatoren; fehlendes Grantattribut nicht erfinden.
- Mitigation/Comparison: genehmigte kleinere Dimension bzw. Typ nur mit erneuter Qualityprüfung;
  künstliche Trunkierung ist keine automatisch zulässige Modelloperation. Cleanup: eigener DB-/Session-Lifecycle.
- Test/Ergebnis/Abnahme: TP-PERF; gleiche Datenmenge und Messmethode, Ressourcen vorab begrenzt,
  4d/2d nur Nutzdatenmodell, tatsächliche Speicherbelegung gemessen; Qualityverlust dokumentieren.
- Quellen/Abhängigkeit: `SRC-072`, `SRC-027`/`SRC-028`, `TSK-005`/`TSK-009`, Framework.

## RES-009 – Concurrent Vector Workloads und Latenzverteilung

- Ziel: `CUR-020`, `TSK-010`; Throughput/Tails/Qualität unter Konkurrenz beurteilen.
  Last/Gelb; 1/2/4/8 eigene Sessions; keine fremden Sessions beenden.
- Preflight/Setup: positive Budgets/Ownership, FWK-006-Signale, begrenzter Requestgenerator,
  autorisierte eingefrorene Fragen. Baseline: Concurrency1 bei definierter Cachemethode.
- Demonstration/Observation: Concurrent Exact/ANN, Zeit je Request, Fehler/Timeouts,
  CPU/IO/Memory/TempDB/Waitdeltas, Throughput, p50/p95/p99 samt n; Recall im selben Scope.
- Mitigation/Comparison: Request-/Concurrencylimit und geeigneter Indexpfad, gleiche Frageverteilung.
  Cleanup: eigenes Stoppsignal/Runner-/Sessioncleanup, eigene DB; keine instanzweite Cache-/DOPänderung.
- Test/Ergebnis/Abnahme: TP-CON/TP-PERF; endlicher Lauf, fehlende Tailstichprobe N/A/explorativ,
  vollständige Fehlerzählung, kein Quality-/Tenantverlust, Kill-Switch und unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-027`/`SRC-028`/`SRC-078`; `TSK-006`/`TSK-009`, FWK-006.

## DGN-008 – External Models, Rechte und Datenabfluss

- Ziel: `CUR-016`/`CUR-018`/`CUR-022`, `TSK-009`; effektive Autorisierung prüfen.
  Lokal/Grün als SQL-/Policyfixture; echter Provider Lokales/Externes Modell/Gelb;
  Instanzkonfigurationsänderung nur separater Rotpfad.
- Preflight/Setup: eigene Setup-, Ingestion-, Retrievalrolle; synthetischer Credentialname/Secretattrappe
  im Offlinefall, Livecredential nur aus Secret Store; erlaubter Endpoint vorab fixiert.
- Baseline: erlaubte Queryrolle liest erlaubte Daten. Demonstration: Modell-EXECUTE/CREATE,
  Endpoint-/Credentialzugriff und DDL/DML mit verschiedenen Rollen positiv/negativ prüfen.
- Observation: tatsächlicher Ausführungskontext, verweigerte Aktion und begrenzte Auditdaten.
  Mitigation/Comparison: Grants reduzieren, erlaubte Aktion erneut prüfen; Egress-Policyprobe ohne echten Abfluss.
- Cleanup: nur eigene Rollen/Modelle/Credentials/DB; Optionen separat restaurieren.
  Test/Abnahme: TP-RUN, Rechteverweigerung auch bei behaupteter KI-Freigabe, kein Secret im Output,
  erlaubter Use Case funktioniert, kein ungeprüftes pauschales RESTrecht; unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-080`/`SRC-082`/`SRC-091`/`SRC-096`; `TSK-005`, Live zusätzlich `TSK-007`.

## DGN-009 – Prompt Injection und manipulierte Retrieval-Quellen

- Ziel: `CUR-018`/`CUR-022`, `TSK-009`; Trust Boundary statt Promptvertrauen.
  Offline-Lokal/Grün; optionale Livegeneration Lokales Modell/Gelb; kein echtes Angriffsziel.
- Preflight/Setup: feste Toolallowlist und minimale Rolle, Fantasiedokument mit Anweisung zur
  Rechteänderung und zweite widersprüchliche Dokumentversion. Baseline: saubere RAG-Fixture.
- Demonstration/Observation: manipulierten Chunk retrieven und Antwort-/Toolfixture bewerten;
  Instruktion/Quelleninhalt unterscheiden, unzulässigen Toolversuch als Fixture erfassen.
- Mitigation/Comparison: geprüfte Quellenversion, Inhalts-/Instruktionstrennung, serverseitige
  Toolpolicy und Claimbeleg; Promptabwehr allein wird nicht als vollständige Security behauptet.
- Cleanup: eigene Fixtures/DB/Prozesse, keine Promptpersistenz. Test: TP-RUN;
  unerlaubtes Tool trotz Modelltext technisch verweigert, unbelegte Antwort nicht akzeptiert,
  restriktive Rechte bleiben erhalten; Liveergebnis kann variieren, unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-090`/`SRC-091`/`SRC-095`; `QRY-018`, `DGN-008`.

## DGN-010 – LLM-Optimierungsvorschlag und Gegenmessung

- Ziel: `CUR-021`, `TSK-011`; eine plausible Empfehlung widerlegen/relativieren.
  Lokal/Grün im kleinen Profil; Last/Gelb bei skalierter Gegenmessung; optionaler SSMSclient getrennt.
- Preflight/Setup: synthetische relational bereits abgedeckte Query, eigenes Index-DDL nur Setuprolle;
  gespeicherte LLM-Antwortfixture empfiehlt redundanten INCLUDE-Index, keine echte LLM-Antwort behaupten.
- Baseline: korrekte Ergebnismenge, tatsächlicher Plan, Reads/CPU/Elapsed, Insert-/Updatekosten/Indexspeicher.
  Demonstration: Vorschlag fachlich prüfen und nur eigenen Laborindex kontrolliert erstellen.
- Observation: kein belastbarer Lesegewinn oder anderer Plannutzung; zusätzliche DML-/Storagekosten.
  Mitigation/Comparison: Vorschlag begründet verwerfen/relativieren, A/B/BA/AA messen, Index rückbauen.
- Zusatzaufgaben: synthetische Plan-, Query-Store-, Wait-, Konfigurations- und Fehleraussagen
  erklären und jeweils fehlenden Kontext/Version oder nächste Messung nennen.
  Cleanup: eigener Index/DB; keine bestehende OPT-/DGN-Demo ändern.
- Test/Ergebnis/Abnahme: TP-PERF; identische Resultate, LLM-Behauptung gegen echte Evidenz,
  ohne Effektseparation kein erfundenes Widerlegungsergebnis; technische Nebenwirkung beurteilen,
  keine automatische Produktionsänderung; unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-027`/`SRC-028`/`SRC-089`–`SRC-092`; `TSK-005`/`TSK-009`.

## DGN-011 – SQL-, Netzwerk- und Inferenzdiagnose

- Ziel: `CUR-020`, `TSK-010`; Gesamtlatenzursache und Beobachtungsgrenze trennen.
  Offline-Lokal/Grün mit klar deklarierten Zeitfixtures; echte Calls Lokales/Externes Modell/Gelb.
- Preflight/Setup: begrenztes FWK-007-QS/XE-Profil, genehmigte Diagnosegrants, ausgewählte
  Events am Build prüfen; eigene Anwendung mit Request-Token und monotonic Timer.
- Baseline: SQLretrieval mit vorbereitetem Queryvektor. Demonstration: Queryembedding und
  Generationsschritt getrennt, kontrollierte lokale Verzögerungsfixture oder echte Providerlatenz.
- Observation: SQLzeit, DB-Roundtrip, Modell-/Netz-/Rest-/Gesamtzeit, RESTstatus/Timeout;
  ai_generate_embeddings_summary/external_rest_endpoint_summary nur falls verfügbar;
  kein Vollprompt/Secretcapture, kein exakter QS-zu-Einzelrequestclaim.
- Mitigation/Comparison: Embeddingcache/Batch/Timeout/Retry und SQLpfad einzeln ändern;
  gleiche Frageverteilung mit Qualityprüfung. Cleanup: eigene XE stoppen/entfernen,
  gesicherte QSoptionen restaurieren, DB/Runner entfernen; kein globales QS-CLEAR.
- Test/Ergebnis/Abnahme: TP-RUN/TP-PERF; Zeitbereiche/Uhr-/Samplinggrenzen offen,
  Fehlercount/Request-/Budget-/Cleanupnegativfälle, keine Restzeit als reine Netzzeit ausgeben.
- Quellen/Abhängigkeit: `SRC-027`/`SRC-028`/`SRC-081`/`SRC-082`; `TSK-009`, Live `TSK-007`.

## CON-010 – Tenant-Isolation bei semantischer Suche

- Ziel: `CUR-018`, `TSK-009`; Autorisierung vor Kontextübergabe und bei Pooling/Filterung.
  Lokal/Grün; Preview klein für ANN-Gegenprobe; FWK-006 mit 2 Sessions ohne Last optional.
- Preflight/Setup: eigene Tenant-A/B-Rollen, RLS-Policy-DDL nur Setuprolle, kein Policy-ALTER für
  Queryrolle; synthetische getrennte Dokumente, Embeddings und identische semantische Frage.
- Baseline: erlaubte relationale/Exact-Candidate-Menge je authentifiziertem Tenant.
  Demonstration: selektiver Filter, Postfilter-/ANN-Grenze, Kontextwechsel/Pooling/Revocation;
  vertrauenswürdiger serverseitiger Tenant statt vom Prompt gesetzter SESSION_CONTEXT-Wert.
- Observation: Anzahl/Identität/Quelle/Vektorzugriff und an Anwendung übergebener Kontext;
  keine fremden Tenantzeilen oder Embeddings, fehlende erlaubte Treffer als Qualitätsfehler.
- Mitigation/Comparison: DBseitige RLS bzw. getrennte Tabellen/DBs, Policy-/Poolreset,
  autorisierte Candidate Scope; nachträglicher Filter ist keine alleinige Sicherheitsgrenze.
- Cleanup: eigene RLS-/Rollen-/Tabellen-/DBobjekte, eigene Sessions und Kontextzustände.
  Test/Abnahme: TP-RUN/TP-CON; positiver/negativer Zugriff, fehlender/manipulierter Tenant,
  Poolreuse/Revocation, unerlaubter Policywechsel, ANN-Fallback und Leakageprüfung;
  keine allgemeine Seitenkanalsicherheit behaupten, unabhängiger Cleanup.
- Quellen/Abhängigkeit: `SRC-078`/`SRC-091`/`SRC-093`; `TSK-005`, ANN zusätzlich `TSK-006`.

## Gesamtabnahme des Entwurfs

Alle Phasen und Profile sind Planungsanforderungen. Testprofile stammen aus der bestehenden
Traceability-Matrix. Die spätere Umsetzung liefert genaue Aufrufe und tatsächliche Runtime-
assertions, aktuelle Quellen-/Buildbindung und Abbruch-/Cleanupbelege pro Demo.
Aus diesem Katalog entsteht kein ausführbarer Erfolg, keine Implementation und kein Release.
