# Recherchekatalog für weitere SQL-Server-Beispielkategorien

| Merkmal | Wert |
|---|---|
| Status | `RESEARCH_BASELINE` |
| Stand | 2026-08-29 |
| Zielplattformen | SQL Server 2019, 2022 und 2025 |
| Gegenstand | SQL-Server-Datenbankmodul mit reproduzierbaren Performancebeispielen |
| Abgrenzung | Recherche- und Deduplizierungsgrundlage; noch kein Detaildesign und keine Runtimefreigabe |
| Bestehende Basis | [Master-Umsetzungsplan](MASTER_IMPLEMENTATION_PLAN.md), [Szenariokandidaten](LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md), [Folienabdeckung](PRESENTATION_EXAMPLE_COVERAGE_PLAN.md), [Source Register](../Research/SOURCE_REGISTER.md) |

## 1. Ziel und Verbindlichkeit

Dieser Katalog schließt die thematische Recherchebreite für spätere Beispiele.
Er erfasst nicht nur klassische Abfrage- und Indexthemen, sondern auch
Engine-Ressourcen, Betriebswirkungen, Datenbewegung, besondere Datentypen,
Sicherheitsfunktionen und Plattformgrenzen. Damit soll vor einer späteren
Detailplanung nahezu kein relevanter Themenbereich unbemerkt bleiben.

Der Katalog ändert weder die Reihenfolge aus
`NEXT_DEVELOPMENT_WAVES.md` noch den Status einer Demo. Er erzeugt keine neuen
dauerhaften Kennungen. Wo kein eindeutiger Eigentümer vorhanden ist, muss eine
spätere Designentscheidung entweder ein vorhandenes Bündel erweitern oder eine
neue ID über die zentrale v2-Registry beantragen.

## 2. Deduplizierungs- und Auswahlregel

Jede Kategorie erhält genau einen primären späteren Eigentümer. Andere
betroffene Demos dürfen dieselbe Evidenz referenzieren, erzeugen aber kein
Parallelskript. Die Einordnung bedeutet:

- `BESTAND`: Das Thema ist bereits hinreichend identifiziert; kein zusätzlicher
  Recherchekandidat entsteht.
- `ERWEITERN`: Eine klar abgegrenzte Phase kann einem vorhandenen Bündel
  hinzugefügt werden. Vor der Umsetzung bleibt ein eigener Quellen-, Safety-
  und Evidenzentscheid erforderlich.
- `EIGENTÜMER_PRÜFEN`: Die Kategorie ist fachlich relevant, aber kein
  vorhandenes Bündel trägt sie ohne Überladung. Erst Detaildesign und Registry-
  Entscheidung dürfen eine neue ID erzeugen.
- `INFRASTRUKTUR`: Der Effekt benötigt mehrere Instanzen, kontrollierte Host-
  Ressourcen, Storage, Netzwerk oder Betriebslast. Die Kategorie ist erkannt,
  aber nicht für die Kernwellen zugesagt.
- `AUSSERHALB`: Das Thema wird bewusst nicht als unmittelbarer Entwicklungsschnitt
  verfolgt. Die Abgrenzung verhindert, dass es später versehentlich als Lücke
  behandelt wird.

Ein späterer Schnitt wird nur dann entwickelt, wenn er eine verständliche
Kausalitätskette besitzt: kontrollierte Ausgangslage, beobachtbares
SQL-Server-Verhalten, fachlich richtige Gegenprobe und unabhängiges Cleanup.

## 3. Nahezu vollständige Themenlandkarte

### 3.1 Datenlayout, Pages, Dateien und Buffer Pool

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Zeilenbreite, NULL-Bitmap, variable Spalten und Slot Array | Gleiche Fachzeilen mit schmalem und breitem Layout; Pages und Reads vergleichen | `STL-001` | `BESTAND` |
| In-Row, Row-Overflow und LOB | Wertgröße über die Speichergrenze verändern und Page-Kette beobachten | `STL-002` | `BESTAND` |
| Heap, RID und Forwarded Records | Variable Heapzeile vergrößern, Fetches nachweisen und Rebuild gegenprüfen | `STL-003` | `BESTAND` |
| Allocation Units, Extents und Page-Metadaten | Kleine Objekte wachsen lassen und Zuordnung ohne undokumentierte Befehle erklären | `STL-004` | `BESTAND` |
| Files, Filegroups, Proportional Fill und Autogrowth | Gleichmäßig beziehungsweise ungünstig konfigurierte Dateien logisch vergleichen | `STL-005` | `BESTAND` |
| Cold/Warm Cache, Read-ahead und Buffer-Pool-Wirkung | Identische Abfrage mit kaltem und warmem Datenbestand; logische und physische Reads trennen | `STL-006` | `ERWEITERN` |
| Page- und Row-Compression | Größe, CPU und I/O bei gleicher Ergebnismenge gegenüberstellen | `STL-010`, `IDX-008` | `BESTAND` |
| Sparse Columns und breite, dünn besetzte Tabellen | Speicherersparnis gegen Zugriff, Metadaten und Eignungsgrenze vergleichen | späteren Eigentümer prüfen | `EIGENTÜMER_PRÜFEN` |
| Buffer Pool Extension und persistenter Cache | Historisch beziehungsweise plattformspezifisch einordnen, nicht als Standardempfehlung lehren | kein Kernowner | `AUSSERHALB` |

### 3.2 Transaction Log, Recovery und Schreibpfad

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Log Records, Commit, Rollback und Checkpoint | Kleine Transaktion, Rollback und Checkpoint mit Log- und Wiederherstellungssicht | `STL-007` | `BESTAND` |
| VLF und Logwachstum | Vorab dimensioniertes gegen kleinteilig wachsendes Log | `STL-008` | `BESTAND` |
| Einzelcommit, Batch-Commit und Group Commit | Gleiche DML-Menge mit unterschiedlicher Commitgranularität | `STL-009` | `BESTAND` |
| Delayed Durability | Commitlatenz und Log-I/O gegen ausdrücklich reduzierte Durabilitätsgarantie abgrenzen | `STL-009` | `ERWEITERN` |
| Minimally Logged Bulk Load | Recovery Model, leere/belegte Zielstruktur, `TABLOCK` und protokollierte Extent-Zuordnung vergleichen | `STL-007`, mit Verweis auf `IDX-009` | `ERWEITERN` |
| Log Truncation und Wiederverwendungsblocker | Aktive Transaktion, Logbackup- beziehungsweise Recovery-Model-Grenze und Freigabe des Logs | `STL-008` | `ERWEITERN` |
| Indirect Checkpoint und Recovery-Ziel | Schreibspitzen und Recovery-Ziel nur mit belastbarer I/O-Messung kontrastieren | `STL-007` | `INFRASTRUKTUR` |
| Accelerated Database Recovery | klassisches Rollback gegen PVS-gestützten Rücknahmepfad | `CON-007` | `BESTAND` |

### 3.3 Kompilierung, Parameterisierung und Plan-Cache

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Compilation, Recompilation und Plan Reuse | Objekt- oder Statistikänderung löst nachvollziehbar Wiederverwendung beziehungsweise Recompile aus | `OPT-007` | `BESTAND` |
| Ad-hoc-Cache-Pollution und Plan Stubs | viele literalverschiedene Einmalabfragen mit und ohne `optimize for ad hoc workloads` | `OPT-007` | `ERWEITERN` |
| Simple und Forced Parameterization | gleiche Literalvarianten, Cacheeinträge und Planwiederverwendung; Sensitivitätsrisiko gegenprüfen | `OPT-007`, Vertiefung in `OPT-008`/`OPT-009` | `ERWEITERN` |
| `sp_executesql`, Stored Procedure und unparametrisiertes SQL | Text-, Parameter- und Cacheidentität vergleichen | `OPT-007`, Verweis auf `QRY-004` | `ERWEITERN` |
| Parameter Sniffing und Parameter Sensitivity | heiße und kalte Werte bei identischem Statement | `OPT-008`, `OPT-009`, `OPT-010` | `BESTAND` |
| Compile Lock und Compile Storm | viele gleichzeitige identische Kompilierungen; optimiertes `sp_executesql` nur im 2025-Pfad | `OPT-007`, SQL-2025-Delta | `INFRASTRUKTUR` |
| Trivial Plan, Full Optimization und Early Abort | Planproperties an kleinen und kombinatorisch größeren Abfragen erklären, ohne feste Planform zu versprechen | `OPT-001`, `OPT-007` | `ERWEITERN` |
| Plan Guides | selektive Parameterisierung oder Hint ohne Codeänderung; Wartungsrisiko sichtbar machen | `DGN-004` | `ERWEITERN` |
| Query Store Hints, Plan Forcing und Unforce | Wirkung, Force Failure, Fallback und vollständige Rücknahme | `DGN-004` | `BESTAND` |
| Optimized Plan Forcing | Optimization-Replay-Pfad ab SQL Server 2022 gegen normales Forcing einordnen | `DGN-004` | `ERWEITERN` |

### 3.4 Statistiken, Cardinality Estimation und adaptive Optimierung

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Histogramm, Density und Schätzfehler | kontrollierte Verteilung mit Estimated/Actual-Vergleich | `OPT-001`, `OPT-002` | `BESTAND` |
| Sampling, Fullscan, Skew und Histogrammgrenzen | identische Daten mit unterschiedlicher Statistikqualität | `OPT-003` | `BESTAND` |
| Spaltenkorrelation, Constraints und Eindeutigkeit | Einzel- gegen Mehrspaltenwissen und Constraint-basierte Vereinfachung | `OPT-004` | `BESTAND` |
| Ascending Key und synchrone/asynchrone Pflege | neu angefügte Werte sowie Blockierungsgrenze der Statistikaktualisierung | `OPT-005` | `BESTAND` |
| Asynchrone Statistikpflege mit Low-Priority-Warten | SQL Server 2022+ gegen reguläre asynchrone Pflege | `OPT-005` | `ERWEITERN` |
| Filtered Statistics | relevante Teilmenge gegen Gesamtverteilung, einschließlich Predicate-Implikation | `OPT-004`, Verweis auf `QRY-011` | `ERWEITERN` |
| Incremental Statistics auf Partitionen | betroffene Partition aktualisieren und globale Sicht erklären | `OPT-005`, Verweis auf `QRY-012` | `ERWEITERN` |
| Persisted Sample Percent | automatische Folgeaktualisierung mit stabiler Stichprobe gegen Standardverhalten | `OPT-003` | `ERWEITERN` |
| CE-Modelle und CE Feedback | Compatibility-Level- und versionsgebundene Schätzung | `OPT-006` | `BESTAND` |
| DOP Feedback | wiederholte parallele Abfrage, Query Store, Wait- und DOP-Entwicklung ab SQL Server 2022 | `OPT-017`, Verweis auf `OPT-006` | `ERWEITERN` |
| Memory Grant Feedback | Grant, Spill, Oszillation sowie persistentes/perzentilbasiertes Feedback | `OPT-014`, `RES-004` | `BESTAND` |
| Batch Mode on Rowstore | gleiche analytische Abfrage mit eligibility-gebundener Row-/Batch-Mode-Evidenz | `OPT-006`, Verweis auf `OPT-017` | `ERWEITERN` |
| Adaptive Join, Interleaved Execution, Table Variable Deferred Compilation und UDF Inlining | jeweils bestehende Baseline mit versionsgebundener adaptiver Variante | `OPT-012`, `QRY-008`, `QRY-009` | `BESTAND` |
| Approximate Query Processing | exakte gegen approximative Aggregation mit Fehlergrenze, CPU und Laufzeit | späteren Eigentümer prüfen | `EIGENTÜMER_PRÜFEN` |

### 3.5 Abfragemuster und Programmierkonstrukte

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| SARGability, Konvertierungen und Datumsintervalle | Indexzugriff und Ergebnisgrenzen bei gleicher Fachfrage | `QRY-001` bis `QRY-003` | `BESTAND` |
| Optionale Parameter und dynamische Suche | statisch, Recompile, dynamisch und adaptive Varianten | `QRY-004` | `BESTAND` |
| OR, `UNION ALL`, `UNION` und Duplikatsemantik | fachlich gleiche und absichtlich nicht gleiche Teilmengen | `QRY-005`, `QRY-007` | `BESTAND` |
| NULL, Semi und Anti Semi Join | `NOT IN`-Falle gegen `NOT EXISTS` | `QRY-006` | `BESTAND` |
| CTE, Temp Table und Table Variable | Materialisierung, Statistik und Deferred Compilation trennen | `QRY-008` | `BESTAND` |
| Rekursive CTE und `MAXRECURSION` | begrenzte Hierarchie gegen Zyklus beziehungsweise explosionsartiges Wachstum | `QRY-008` | `ERWEITERN` |
| Inline TVF, MSTVF und Scalar UDF | Schätzung, Inlining und Planintegration | `QRY-009` | `BESTAND` |
| Cursor, set-based Verarbeitung, `APPLY` und Window Functions | gleiche Fachlogik mit unterschiedlicher Ausführungsform | `QRY-010` | `BESTAND` |
| Pagination | `OFFSET/FETCH` bei tiefen Seiten gegen Keyset/Seek-Fortsetzung | `QRY-001`, mit `QRY-003` für stabilen Schlüssel | `ERWEITERN` |
| Multi-Value-Filter | große `IN`-Liste, Table-Valued Parameter, Temp Table und JSON-Eingabe fachlich gleich vergleichen | `QRY-004`, mit `QRY-008`/`QRY-012` | `ERWEITERN` |
| Computed Column und Predicate Implication | deterministische berechnete Spalte und gefilterter Index | `QRY-011` | `BESTAND` |
| Partition Elimination | statische und dynamische Elimination sowie nicht passende Prädikatform | `QRY-012` | `BESTAND` |
| JSON, XML und Stringverarbeitung | Parse-, Extraktions- und relationale Gegenprobe mit gleicher Ergebnismenge | `QRY-012` | `BESTAND` |
| Leading-Wildcard-Suche und Full-Text Search | `LIKE '%x%'` gegen geeignete Volltextsuche, inklusive Aktualisierungs- und Fragmentkosten | späteren Eigentümer prüfen | `EIGENTÜMER_PRÜFEN` |
| Indexed Views | Aggregation zur Laufzeit gegen materialisierte Sicht und DML-Pflegekosten | späteren Eigentümer prüfen | `EIGENTÜMER_PRÜFEN` |
| `MERGE` und getrennte DML-Anweisungen | Plan-, Locking- und Ergebnisverhalten nur mit klarer Korrektheitsgrenze | kein Kernowner | `AUSSERHALB` |

### 3.6 Indexfamilien, Partitionierung und Wartung

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Heap/Clustered, Schlüsselbreite, Abdeckung und Lookup | vorhandene Rowstore-Schnitte und Operatoren-Labor | `IDX-001` bis `IDX-004` | `BESTAND` |
| Redundante Indizes und DML-Kosten | Lesegewinn gegen Schreib-, Speicher- und Wartungskosten | `IDX-005` | `BESTAND` |
| Page Split, Density, Fragmentation und Fill Factor | kontrollierte Insertreihenfolge und sachgerechte Gegenmaßnahme | `IDX-006` | `BESTAND` |
| Last-Page-Contention | parallele sequenzielle Inserts mit geeigneter Gegenprobe | `IDX-007` | `BESTAND` |
| Online und Resumable Index Operations | Blockierungsphasen, Pause/Resume und Edition-/Versionsgrenzen | `IDX-006` | `ERWEITERN` |
| `WAIT_AT_LOW_PRIORITY` bei Indexoperationen | konkurrierende Session und begrenztes Low-Priority-Zeitfenster | `IDX-006`, Verweis auf `CON-004` | `ERWEITERN` |
| Partition Switching und Alignment | metadata-only Wechsel bei passender Struktur gegen bewusst unpassende Definition | `QRY-012`, Verweis auf `IDX-010` | `ERWEITERN` |
| Columnstore-Ladepfad und Rowgroups | kleine gegen Direct-Compressed Loads, Delete Bitmap und Segment Elimination | `IDX-009`, `IDX-010` | `BESTAND` |
| XML Index | ungeindexierte Extraktion gegen Primary/Secondary XML Index und DML-Kosten | `QRY-012` oder neuer Spezialowner nach Detaildesign | `EIGENTÜMER_PRÜFEN` |
| Spatial Index | räumliches Prädikat mit und ohne geeignete Tessellation; false positives erklären | neuer Spezialowner nur bei Curriculumbedarf | `EIGENTÜMER_PRÜFEN` |
| Full-Text Index | Token-/Rangsuche, Fragmentierung und asynchrone Population | neuer Spezialowner nur bei Curriculumbedarf | `EIGENTÜMER_PRÜFEN` |
| SQL-Server-2025-JSON-Index | Previewstatus, native JSON-Speicherung und Eligibility vor jeder Demo neu prüfen | SQL-2025-Delta | `AUSSERHALB` |
| Memory-optimized Hash und Nonclustered Index | Point Lookup, Range Scan, Bucket-Verteilung und Kollisionen | neuer In-Memory-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |

### 3.7 Concurrency, Isolation und Transaktionen

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Anomalien und Isolation Levels | Dirty/Non-repeatable/Phantom/Lost Update sowie Key-Range Locks | `CON-001`, `CON-002` | `BESTAND` |
| RCSI und SNAPSHOT | Statement-/Transaktionssicht und Updatekonflikt | `CON-003` | `BESTAND` |
| Blocking Chain und Head Blocker | vier Rollen mit messbarer Wartezeit | `CON-004` | `BESTAND` |
| Lock Escalation, Schema Locks und Metadaten | Schwellen- beziehungsweise druckabhängige Eskalation und DDL-Blockade | `CON-005` | `BESTAND` |
| Deadlockvarianten | Zugriffreihenfolge und Deadlock Graph | `CON-006` | `BESTAND` |
| Conversion Deadlock | konkurrierende Shared-to-Exclusive-Konvertierung als eigene Phase | `CON-006` | `ERWEITERN` |
| Application Locks | fachliche Ressource mit `sp_getapplock` gegen Tabellenlock-Missbrauch | `CON-004` oder `CON-006` nach Detaildesign | `EIGENTÜMER_PRÜFEN` |
| Optimized Locking | TID Locks und Lock After Qualification im 2025-Pfad | `CON-008` | `BESTAND` |
| Latch, Lock und Spinlock | dieselbe Warteanalyse korrekt nach Synchronisationsart trennen | `RES-005`, Verweis auf `CON-004` | `ERWEITERN` |
| Distributed Transactions | lokale gegen verteilte Commitgrenze und externe Koordinatorabhängigkeit | kein Kernowner | `INFRASTRUKTUR` |

### 3.8 TempDB und kurzlebige Arbeitsdaten

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Temp Table und Table Variable | Statistik-, Kompilierungs- und Scopeunterschiede | `QRY-008` | `BESTAND` |
| Worktables, Workfiles und Spills | Sort-/Hash-Spill als TempDB-Verbraucher | `OPT-013` | `BESTAND` |
| Version Store und Persisted Version Store | lang laufender Reader beziehungsweise ADR-Rollback | `CON-007` | `BESTAND` |
| Allocation- und Metadaten-Contention | hohe Sessionzahl, Dateilayout und Memory-optimized TempDB Metadata | `CON-009` | `BESTAND` |
| Temp Table Caching und Deferred Drop | wiederholte Proc-Ausführung gegen wechselnde Definitionen und Metadatenlast | `CON-009`, Verweis auf `QRY-008` | `ERWEITERN` |
| TempDB-Dateigröße und Autogrowth | kontrolliertes Dateilayout und Wachstumsereignis ohne Storage-Latenzbehauptung | `CON-009`, Verweis auf `STL-005` | `ERWEITERN` |
| TempDB Space Governance | SQL Server 2025 mit Resource-Governor-Klassifizierung und vollständiger Rücknahme | bestehender SQL-2025-Delta-Pfad | `BESTAND` |
| Memory-optimized SCHEMA_ONLY als TempDB-Alternative | hohe kurzlebige Schreiblast gegen klassische temporäre Struktur | neuer In-Memory-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |

### 3.9 CPU, Parallelität, Worker, Memory und Governance

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| CPU-bound Query und Scheduler Yield | rechenintensive Abfrage mit Scheduler- und Wait-Sicht | `RES-001` | `BESTAND` |
| Parallelism, Exchanges und Skew | balancierte gegen konzentrierte Verteilung und serielle Gegenprobe | `OPT-017`, `RES-002` | `BESTAND` |
| Cost Threshold und MAXDOP | querylokale, datenbank- und instanzweite Grenze sauber auseinanderhalten | `RES-002` | `ERWEITERN` |
| Worker Starvation und `THREADPOOL` | viele blockierte oder lang laufende Requests und DAC-/Recovery-Grenze | `RES-001`, mit `DGN-006` | `INFRASTRUKTUR` |
| NUMA, Scheduler- und Memory-Node-Lokalität | ungleich belastete Scheduler/Nodes beobachten, keine Hardwareempfehlung simulieren | `RES-001` | `INFRASTRUKTUR` |
| Buffer Pool, Plan Cache, Lock Memory und Clerks | `max server memory` gegen tatsächliche Clerk- und Prozesssicht | `RES-003` | `ERWEITERN` |
| Query Execution Memory | Grant, Konkurrenz, Spill und `RESOURCE_SEMAPHORE` | `OPT-014`, `RES-003`, `RES-004` | `BESTAND` |
| Resource Governor für CPU, Memory, I/O, DOP und Concurrency | zwei klassifizierte Workloads mit Pool-/Group-Grenzen und Rücknahme | neuer querschnittlicher Owner erforderlich | `EIGENTÜMER_PRÜFEN` |
| Resource-Governor-Grenzen | userseitige Reads gegenüber nicht beherrschten System-/Writepfaden erklären | gleicher späterer Resource-Governor-Owner | `ERWEITERN` |
| In-Memory-OLTP-Speicher und Garbage Collection | sizing, lange Transaktion und nicht freigegebene Zeilenversionen | neuer In-Memory-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |

### 3.10 I/O, Netzwerk und externe Zugriffe

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Page-I/O-Latch gegen Page-Latch | physische I/O-Latenz und In-Memory-Contention diagnostisch trennen | `RES-005` | `BESTAND` |
| Daten- und Logfile-Latenz | DMV-Deltas, `WRITELOG` und kontrollierte Storageprofile | `RES-006` | `BESTAND` |
| Wait-Scope und Netzwerkverbrauch | Request-/Task-/Instanzdelta sowie langsamer Client | `RES-007` | `BESTAND` |
| Read-ahead und Prefetch | große Range-Abfrage, Cachezustand und I/O-Muster | `STL-006`, Verweis auf `RES-006` | `ERWEITERN` |
| Remote Query und Pushdown | lokale Filterung gegen providergebundenes Remote-Pushdown | `QRY-012` | `BESTAND` |
| Provider, Collation, TLS und Netzwerkgrenze | zwei Instanzen mit expliziter Provider- und Zertifikatskonfiguration | `QRY-012` | `INFRASTRUKTUR` |
| Client Fetch Size und Chatty Access | gleiche Ergebnismenge mit gebündeltem gegen zeilenweisem Abruf | `DGN-006`, Verweis auf `RES-007` | `INFRASTRUKTUR` |

### 3.11 Diagnose, Historie und methodischer Vergleich

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| `STATISTICS IO/TIME`, Actual Plan und A/B | identische Ergebnisassertion, geänderte Maßnahme und Delta | `DGN-001` | `BESTAND` |
| Sessions, Requests, Tasks und Live Query Statistics | gleiche laufende Anfrage auf mehreren Beobachtungsebenen | `DGN-002` | `BESTAND` |
| Query Store | Query-, Plan-, Runtime- und verfügbare Wait-Historie | `DGN-003` | `BESTAND` |
| Extended Events | Deadlock, Blocking, Spill, Recompile und Fehler mit begrenztem Target | `DGN-005` | `BESTAND` |
| Workload-Treiber und OS-Metriken | Baseline, kontrollierte Last, Stop und Wiederholung | `DGN-006` | `BESTAND` |
| Lightweight Query Profiling und operatorbezogene Laufzeit | Profiling-Evidenz gegen Mess-Overhead und tatsächlichen Plan | `DGN-002` | `ERWEITERN` |
| Query- und Plan-Hash | textverschiedene beziehungsweise planverschiedene Abfragen gruppieren | `DGN-003` | `ERWEITERN` |
| Memory Clerks, Scheduler-, Latch- und Spinlock-DMVs | vom Symptom zur zuständigen internen Ressource navigieren | `DGN-002`, mit `RES-001`/`RES-003`/`RES-005` | `ERWEITERN` |
| SQL Trace und Profiler | nur als abgelöste Diagnosewege einordnen; keine neue Demo | `DGN-005` zeigt den XE-Ersatz | `AUSSERHALB` |
| Drittanbieter-Monitoring | mögliche Transferdiskussion, aber keine Voraussetzung oder Repositoryintegration | kein Owner | `AUSSERHALB` |

### 3.12 Verfügbarkeit, Datenbewegung und Hintergrundarbeit

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Availability-Group-Sendepfad | Log Generation, Capture, Send, Harden und Queue-Wachstum | neuer HA-Owner erforderlich | `INFRASTRUKTUR` |
| Synchroner Commit | lokale Commitlatenz gegen `HADR_SYNC_COMMIT` und Secondary-Hardening | neuer HA-Owner erforderlich | `INFRASTRUKTUR` |
| Redo und lesbare Secondary | Redo Queue, Read-Last und Datenlatenz getrennt beobachten | neuer HA-Owner erforderlich | `INFRASTRUKTUR` |
| AG Flow Control | Netzwerk-/Speichergrenze gegen Flow-Control-Zähler und Send Queue | neuer HA-Owner erforderlich | `INFRASTRUKTUR` |
| Query Store auf Secondary Replicas | erst nach freigegebener 2025-AG-Topologie | bestehender SQL-2025-Delta-Pfad | `INFRASTRUKTUR` |
| Change Tracking | DML- und Speichermehrkosten gegen anwendungsseitige Änderungsabfrage | neuer Data-Movement-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |
| Change Data Capture | Log-basierte Erfassung, Capture-/Cleanup-Lag und Retention | neuer Data-Movement-Owner erforderlich | `INFRASTRUKTUR` |
| Replikation und Log Shipping | Agent-, Netzwerk-, Latenz- und Retentionwirkungen | kein Kernowner | `INFRASTRUKTUR` |
| Backup/Restore und Kompression | I/O-Reduktion gegen CPU-Kosten; SQL-2025-ZSTD nur versionsgebunden | neuer Operations-Owner erforderlich | `INFRASTRUKTUR` |
| `DBCC CHECKDB` und Wartungsfenster | Laufzeit, I/O, Snapshot-/TempDB-Bedarf und Abbruchgrenze | neuer Operations-Owner erforderlich | `INFRASTRUKTUR` |

### 3.13 In-Memory OLTP, Sicherheit, Spezialfunktionen und Plattform

| Kategorie | Verständlicher späterer Beispielschnitt | Eigentümer oder Entscheidung | Einordnung |
|---|---|---|---|
| Disk-based gegen Memory-optimized OLTP | latch-/locklastige Transaktionsarbeit bei gleicher Fachlogik | neuer In-Memory-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |
| Interpretiertes gegen nativ kompiliertes T-SQL | CPU und unterstützte Planformen bei identischer Operation | neuer In-Memory-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |
| Durable gegen SCHEMA_ONLY Memory-optimized | Wiederanlauf- und Persistenzgrenze sichtbar machen | neuer In-Memory-Owner erforderlich | `EIGENTÜMER_PRÜFEN` |
| TDE | Daten-/Log-I/O, CPU und Backup-Kompression nur in isolierter Messung vergleichen | neuer Security-Owner nur bei Curriculumbedarf | `INFRASTRUKTUR` |
| Always Encrypted und Secure Enclaves | clientseitige Verarbeitung, unterstützte Prädikate und Enclave-Grenze | neuer Security-Owner nur bei Curriculumbedarf | `INFRASTRUKTUR` |
| Row-Level Security | Predicate-Funktion, Planform und Zusatzjoin bei Spezialzugriffen | neuer Security-Owner nur bei Curriculumbedarf | `EIGENTÜMER_PRÜFEN` |
| SQL Audit und zusätzliche XE-Erfassung | Beobachtbarkeit gegen Capture- und Targetkosten | `DGN-005` oder Security-Owner nach Detaildesign | `EIGENTÜMER_PRÜFEN` |
| Temporal Tables | Historienwachstum, Retention und zeitbezogene Abfragepläne | neuer Spezialowner nur bei Curriculumbedarf | `EIGENTÜMER_PRÜFEN` |
| CLR, Graph, Spatial, XML und Full-Text | nur anwendungsbezogene Spezialkosten; kein Sammelscript | jeweiliger Spezialowner erst nach Curriculumfreigabe | `EIGENTÜMER_PRÜFEN` |
| Linux- und Container-Memory-Limits | cgroup, `memorylimitmb`, `max server memory` und notwendiger Headroom | `LABINT-003` beziehungsweise späteres Labdesign | `INFRASTRUKTUR` |
| Container-CPU-Limit und sichtbare Kerne | Hostlimit, SQL-Scheduler, DOP-Eligibility und reproduzierbares Profil | `LABINT-003`, Verweis auf `OPT-017` | `INFRASTRUKTUR` |
| Physische Storage-, Kernel-, NUMA- und Netzwerkoptimierung | nur mit validierter nativer Linux- oder Hyper-V-Lane | `LABINT-003` | `INFRASTRUKTUR` |
| Azure-only Automatic Tuning, Hyperscale, Serverless und Fabric | nicht als SQL-Server-On-Premises-Demo behandeln | kein Owner | `AUSSERHALB` |
| Vector-, KI- und Previewfunktionen ohne Curriculumbedarf | bestehende SQL-2025-Entscheidungen beibehalten | SQL-2025-Delta | `AUSSERHALB` |
| Undokumentierte Trace Flags und interne Befehle | weder Voraussetzung noch Lehrziel | kein Owner | `AUSSERHALB` |

## 4. Ergebnis der Lückenanalyse

Die vorhandenen 68 Kernbündel plus die bereits registrierten Erweiterungen
decken die klassische Performanceausbildung weitgehend ab. Die Recherche findet
keine Rechtfertigung für eine zweite, parallele Sammlung zu Plänen, Joins,
Statistiken, Indizes, Blocking, TempDB, Waits oder Diagnose. Dort genügen klar
abgegrenzte Phasen der vorhandenen Eigentümer.

Vor einer späteren genauen Planung verbleiben fünf echte Themencluster ohne
eindeutigen bestehenden Eigentümer:

1. **Resource Governor jenseits der TempDB-Space-Governance:** CPU, Memory,
   physische Reads, DOP und gleichzeitige Requests gehören in einen gemeinsamen
   A/B-Schnitt und nicht verteilt in fünf Ressourcendemos.
2. **In-Memory OLTP:** Disk/Memory, Hash/Range, native/interpreted,
   Durable/SCHEMA_ONLY sowie Sizing/GC benötigen eine gemeinsame Datenbasis und
   dürfen nicht als Anhänge an Rowstore- oder TempDB-Demos zerfallen.
3. **HA und Datenbewegung:** AG-Send/Redo/Commit/Flow-Control sowie CDC,
   Change Tracking und Replikation sind erkannt, benötigen aber getrennte
   Infrastruktur- und Curriculumentscheidungen.
4. **Operations-Performance:** Backup/Restore/Kompression und `DBCC CHECKDB`
   sind wichtige Lasten, aber keine Query-Tuning-Demos. Sie benötigen einen
   klaren Operations-Scope und kontrollierte Storageprofile.
5. **Spezialisierte Zugriffswege:** Full-Text, XML, Spatial, Indexed Views,
   Temporal und Sicherheitsprädikate werden nur nach tatsächlichem
   Curriculumbedarf vertieft; ein undifferenziertes Sammelscript wäre redundant
   und didaktisch schwach.

`Approximate Query Processing` bleibt als kleine fachliche Einzelkategorie
sichtbar. Ob sie einen neuen Eigentümer benötigt oder als IQP-Phase eingebettet
wird, entscheidet das spätere Detaildesign.

## 5. Empfohlener späterer Entscheidungsweg

Diese Reihenfolge ist keine neue Entwicklungswelle und verdrängt keinen
operativen Schritt:

1. Zuerst die `ERWEITERN`-Zeilen bei bereits geplanten Demos während deren
   Detaildesign prüfen. Nur eine eigenständige, lernzielgebundene Phase wird
   übernommen.
2. Danach Resource Governor und In-Memory OLTP als zwei querschnittliche
   Designkandidaten bewerten. Beide benötigen Edition-, Ressourcen-, Safety-
   und Cleanup-Nachweise.
3. HA/Datenbewegung und Operations ausschließlich gegen eine dokumentierte
   Infrastruktur- und Curriculumfreigabe planen.
4. Spezialisierte Index-, Datentyp- und Securitythemen nur bei belegter
   Folien- oder Lernziellücke übernehmen.
5. Erst nach der Eigentümerentscheidung Quellen registrieren, gegebenenfalls
   IDs über die v2-Registry anlegen und kleine Implementierungs-PRs schneiden.

## 6. Primärquellen-Startpunkte für spätere Detailanalysen

Die folgenden aktuellen Microsoft-Primärquellen begründen die neu
identifizierten Kategorien. Sie sind Recherche-Startpunkte und erhalten erst
bei einer Umsetzungsentscheidung reguläre `SRC-*`-Kennungen:

- [Query-Store-Best-Practices](https://learn.microsoft.com/en-us/sql/relational-databases/performance/best-practice-with-the-query-store?view=sql-server-ver17) und [Optimize for ad hoc workloads](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/optimize-for-ad-hoc-workloads-server-configuration-option?view=sql-server-ver17) für Parameterisierung und Plan-Cache-Ökonomie;
- [Optimized Plan Forcing](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17) für Optimization Replay ab SQL Server 2022;
- [Statistics](https://learn.microsoft.com/en-us/sql/relational-databases/statistics/statistics?view=sql-server-ver17) für Filtered/Incremental Statistics und asynchrone Low-Priority-Aktualisierung;
- [Intelligent Query Processing](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-details?view=sql-server-ver17) und [DOP Feedback](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-degree-parallelism-feedback?view=sql-server-ver17) für adaptive und approximative Pfade;
- [Online Index Operations](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/guidelines-for-online-index-operations?view=sql-server-ver17) für Online-, Resumable- und Wartungsgrenzen;
- [Minimal Logging](https://learn.microsoft.com/en-us/sql/relational-databases/import-export/prerequisites-for-minimal-logging-in-bulk-import?view=sql-server-ver17) und [Transaction Durability](https://learn.microsoft.com/en-us/sql/relational-databases/logs/control-transaction-durability?view=sql-server-ver17) für Bulk- und Commitpfade;
- [Resource Governor](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/resource-governor?view=sql-server-ver17) für CPU-, Memory-, I/O-, DOP- und Concurrency-Governance;
- [Server Memory Configuration](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/server-memory-server-configuration-options?view=sql-server-ver17), [SQLOS-DMVs](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sql-server-operating-system-related-dynamic-management-views-transact-sql?view=sql-server-ver17) und [Max Worker Threads](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-the-max-worker-threads-server-configuration-option?view=sql-server-ver17) für Clerks, NUMA, Scheduler und Worker;
- [In-Memory OLTP Overview](https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/overview-and-usage-scenarios?view=sql-server-ver17) und [Memory-optimized Tables](https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/introduction-to-memory-optimized-tables?view=sql-server-ver17) für Index-, Concurrency-, Durability- und Native-Compilation-Varianten;
- [Availability-Group Performance](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/monitor-performance-for-always-on-availability-groups?view=sql-server-ver17) für Send-, Harden-, Redo- und Flow-Control-Stufen;
- [Track Data Changes](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/track-data-changes-sql-server?view=sql-server-ver17) für CDC- und Change-Tracking-Grenzen;
- [Backup Compression](https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-compression-sql-server?view=sql-server-ver17) für CPU-/I/O-Trade-offs und SQL-Server-2025-ZSTD;
- [`DBCC CHECKDB`](https://learn.microsoft.com/en-us/sql/t-sql/database-console-commands/dbcc-checkdb-transact-sql?view=sql-server-ver17) für Snapshot-, Locking- und Betriebsgrenzen von Integritätsprüfungen;
- [XML Indexes](https://learn.microsoft.com/en-us/sql/relational-databases/xml/xml-indexes-sql-server?view=sql-server-ver17), [Full-Text Performance](https://learn.microsoft.com/en-us/sql/relational-databases/search/improve-the-performance-of-full-text-queries?view=sql-server-ver17) und [Index Design Guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17) für spezialisierte Zugriffspfade;
- [Indexed Views](https://learn.microsoft.com/en-us/sql/relational-databases/views/create-indexed-views?view=sql-server-ver17) und [Temporal-Table-Grenzen](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal/considerations-limitations?view=sql-server-ver17) für Materialisierungs-, DML- und Historienkosten;
- [Row-Level Security](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17), [Transparent Data Encryption](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/transparent-data-encryption?view=sql-server-ver17) und [Always Encrypted with Secure Enclaves](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-enclaves?view=sql-server-ver17) für Security-bedingte I/O-, Plan- und Funktionsgrenzen;
- [SQL Server Memory on Linux and in Containers](https://learn.microsoft.com/en-us/sql/linux/configure/performance-best-practices-sql-server-memory?view=sql-server-ver17) für cgroup-, Prozess- und Buffer-Pool-Limits.

## 7. Abnahme- und Pflegegrenze

Diese Recherchewelle ist vollständig, wenn alle Kategorien einem vorhandenen
Owner, einer bewussten späteren Eigentümerentscheidung, einer
Infrastrukturabhängigkeit oder einem Ausschluss zugeordnet sind. Sie ist keine
Behauptung, dass jede Kategorie Teil des Curriculums werden muss.

Vor einer Implementierung sind weiterhin erforderlich:

- Quellenprüfung und Registrierung der tatsächlich verwendeten Claims;
- Lernziel- und Folienzuordnung ohne Parallelbeispiel;
- versions-, editions- und compatibility-level-genaue Eligibility;
- Safety-Klasse, Ressourcenprofil, Zeitbudget und Kill-Switch;
- deterministische fachliche Assertion sowie zulässige Plan- oder
  Runtimevarianten;
- Setup, Reset und Cleanup gemäß Demo- beziehungsweise Szenariovertrag;
- Statuspflege erst nach der dafür geforderten Runtimeevidenz.
