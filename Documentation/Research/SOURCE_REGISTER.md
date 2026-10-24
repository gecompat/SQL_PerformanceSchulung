# Projektweites Quellenregister

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `W0-006`, `ADV-001`, `PRS-009` |
| Status | `VALIDATED` |
| Registerversion | 1.2 |
| Stand | 2026-07-26 |
| Primärer Geltungsbereich | SQL Server 2019, 2022 und 2025 sowie die Präsentationsarchitektur des Schulungsprojekts |
| Kanonische Quellenklasse | öffentlich erreichbare Primärdokumentation des Produktherstellers |

## 1. Zweck

Dieses Register ist die kanonische Quellenbasis für technische Aussagen, Folien, Sprecherhinweise, Teilnehmerunterlagen, Demo-Designs und Tests. Es ergänzt das folienbezogene Aussagenregister um Pflegeinformationen und einen eindeutigen Gültigkeitsbereich.

Eine Quelle belegt nur die in ihrem Aussagebezug benannten Produkteigenschaften. Aus einer allgemeinen Featureübersicht darf keine unbelegte Detailaussage über jede Unterfunktion, Edition oder Compatibility Level abgeleitet werden.

## 2. Verbindliches Metadatenmodell

Jeder Eintrag besitzt mindestens folgende Felder:

| Feld | Bedeutung |
|---|---|
| `ID` | stabile projektweite Kennung; IDs werden nicht wiederverwendet |
| `Klasse` | `PRIMARY`, `SUPPORTING`, `EMPIRICAL_METHOD` oder `RETIRED` |
| `Quelle` | Titel und direkt aufrufbarer Verweis |
| `Aussagebezug` | Produkteigenschaft, Claim-Gruppe oder Demo, für die die Quelle verwendet werden darf |
| `Gültigkeitsbereich` | Engine-Version, Compatibility Level, Konfiguration, Edition oder Plattformgrenze |
| `Aktualisiert` | Datum der letzten Änderung der Registerinterpretation oder Zuordnung |
| `Abgerufen` | Datum der letzten erfolgreichen fachlichen Prüfung der referenzierten Quelle |
| `Status` | `ACTIVE`, `REVIEW_REQUIRED` oder `RETIRED` |
| `Review-Trigger` | Ereignis, das eine erneute Prüfung erzwingt |

`Aktualisiert` bezeichnet nicht ungeprüft das Veröffentlichungsdatum einer Webseite. Viele Dokumentationsseiten besitzen revisionsabhängige oder nicht stabil ausgewiesene Änderungsdaten. Maßgeblich ist deshalb das Datum, an dem der Registereintrag und seine projektseitige Interpretation zuletzt fachlich geändert wurden. Ein von der Quelle verlässlich ausgewiesener Revisionsstand kann ergänzend in Notes dokumentiert werden.

## 3. Evidenzklassen

| Kennzeichnung | Verwendung |
|---|---|
| `DOCUMENTED` | Aussage wird unmittelbar durch mindestens eine aktive Primärquelle getragen. |
| `EMPIRICAL` | konkrete Wirkung, Bandbreite oder Schwelle muss im jeweiligen Workload gemessen werden; die Quelle belegt nur Mechanismus und Messgrößen. |
| `METHOD` | Diagnose-, Mess- oder Unterrichtsablauf; keine Produktgarantie. |
| `DIDACTIC` | Navigation, Lernziel, Transfer oder Zusammenfassung ohne eigenständige technische Produkteigenschaft. |
| `INFERENCE` | logisch hergeleitete Aussage aus mehreren Quellen; Herleitung und Grenzen müssen ausdrücklich genannt werden. |

## 4. Aktive Primärquellen

Der ursprüngliche Prüfstand ist der 24. Juli 2026; spätere Abruf- und Prüfdaten stehen beim jeweiligen Eintrag. Der URL-Parameter `view=sql-server-ver17` bezeichnet die Dokumentationssicht für SQL Server 2025; abweichende Versions- und Compatibility-Level-Grenzen sind im Feld `Gültigkeitsbereich` benannt.

| ID | Klasse | Quelle | Aussagebezug | Gültigkeitsbereich | Aktualisiert | Abgerufen | Status | Review-Trigger |
|---|---|---|---|---|---|---|---|---|
| `SRC-001` | PRIMARY | [Query processing architecture guide](https://learn.microsoft.com/en-us/sql/relational-databases/query-processing-architecture-guide?view=sql-server-ver17) | Verarbeitungskette, Optimierer, Plan Cache, Parallelität, Workers und Tasks; Claims zu M02 und M06 | SQL Server 2019–2025; Detailverhalten versionsabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | neue Engine-Version oder geänderte Cache-/Parallelitätsdokumentation |
| `SRC-002` | PRIMARY | [Pages and extents architecture guide](https://learn.microsoft.com/en-us/sql/relational-databases/pages-and-extents-architecture-guide?view=sql-server-ver17) | Pages, Extents, Row Layout und grundlegende Speicherorganisation; M01 | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Änderung der Storage-Engine-Dokumentation |
| `SRC-003` | PRIMARY | [Database files and filegroups](https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups?view=sql-server-ver17) | Data Files, Log Files, Filegroups, proportional fill und Autogrowth; `STL-005` | SQL Server 2019–2025; physische Wirkung umgebungsabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | Änderung der Filegrowth- oder Filegroup-Semantik |
| `SRC-004` | PRIMARY | [Transaction locking and row versioning guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17) | Locking, Isolation, RCSI (Read Committed Snapshot Isolation; zeilenversionierte Variante von READ COMMITTED), SNAPSHOT, Konflikte und Row Versioning; M05 | SQL Server 2019–2025; Datenbankoptionen beachten | 2026-07-24 | 2026-07-24 | ACTIVE | neue Locking-/Versioning-Funktion oder geänderte Konfliktsemantik |
| `SRC-005` | PRIMARY | [Statistics](https://learn.microsoft.com/en-us/sql/relational-databases/statistics/statistics?view=sql-server-ver17) | Histogramm, Density, Sampling, Statistikaktualität und Schätzungsgrundlagen; `OPT-002` (Statistiken lesen) bis `OPT-005` (Wachsende Schlüssel und Statistikpflege) | SQL Server 2019–2025; CL und Konfiguration beachten | 2026-07-24 | 2026-07-24 | ACTIVE | neue Statistikfunktion oder geänderte Auto-Update-Regel |
| `SRC-006` | PRIMARY | [Cardinality estimation](https://learn.microsoft.com/en-us/sql/relational-databases/performance/cardinality-estimation-sql-server?view=sql-server-ver17) | CE-Modelle und Modellgrenzen; `OPT-006` | SQL Server 2019–2025; Compatibility Level entscheidend | 2026-07-24 | 2026-07-24 | ACTIVE | neues CE-Modell oder neue CL-Zuordnung |
| `SRC-007` | PRIMARY | [Intelligent query processing](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing?view=sql-server-ver17) | IQP-Funktionsmatrix, Deferred Compilation, Interleaved Execution, PSP (Parameter Sensitive Plan Optimization; Planoptimierung für unterschiedliche Parameterwerte), Batch Mode und Feedbackfunktionen | SQL Server 2019–2025; jeweilige CL- und Konfigurationsgrenzen | 2026-07-24 | 2026-07-24 | ACTIVE | neue IQP-Funktion oder geänderte Voraussetzung |
| `SRC-008` | PRIMARY | [Intelligent query processing features in detail](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-details?view=sql-server-ver17) | Detailgrenzen einzelner IQP-Funktionen; Claims 34, 42 und 43 | versions- und CL-abhängig | 2026-07-24 | 2026-07-24 | ACTIVE | Detailänderung einer referenzierten IQP-Funktion |
| `SRC-009` | PRIMARY | [Memory grant feedback](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-memory-grant-feedback?view=sql-server-ver17) | Overgrant, Undergrant, Feedbackvarianten, Perzentilmodus und Persistenz; `OPT-014` | SQL Server 2019–2025; Persistenz SQL Server 2022+, CL 140+, Query Store `READ_WRITE` | 2026-07-24 | 2026-07-24 | ACTIVE | Änderung der MGF-Voraussetzungen oder Persistenz |
| `SRC-010` | PRIMARY | [sys.dm_exec_query_memory_grants](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-memory-grants-transact-sql?view=sql-server-ver17) | Requested, Granted und Used Memory sowie wartende Grants; `OPT-014`, `RES-003` | SQL Server 2019–2025; Rechte versionsabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | DMV-Spalten- oder Berechtigungsänderung |
| `SRC-011` | PRIMARY | [WITH common_table_expression](https://learn.microsoft.com/en-us/sql/t-sql/queries/with-common-table-expression-transact-sql?view=sql-server-ver17) | CTE-Semantik und fehlende Materialisierungsgarantie; `QRY-008` | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Änderung der CTE-Semantik oder Dokumentation |
| `SRC-012` | PRIMARY | [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17) | Indexstruktur, Key-Reihenfolge, INCLUDE, Filter und Row Locator; M04 | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | neue Indexfunktion oder geänderte Designgrenze |
| `SRC-013` | PRIMARY | [Heaps](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/heaps-tables-without-clustered-indexes?view=sql-server-ver17) | RID (Row Identifier; physischer Zeilenverweis) Lookup, Forwarded Records und geeignete Heap-Szenarien; `STL-003`, `IDX-001` | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Änderung der Heap- oder Forwarded-Record-Dokumentation |
| `SRC-014` | PRIMARY | [Specify fill factor for an index](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/specify-fill-factor-for-an-index?view=sql-server-ver17) | Fill Factor, Page Splits und Ressourcentrade-offs; `IDX-006` (Seitenaufteilungen und Seitenbelegung) | SQL Server 2019–2025; Wirkung empirisch | 2026-07-24 | 2026-07-24 | ACTIVE | geänderte Empfehlung oder Produktsemantik |
| `SRC-015` | PRIMARY | [Optimize index maintenance](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/reorganize-and-rebuild-indexes?view=sql-server-ver17) | Fragmentation, Page Density, Reorganize/Rebuild und Columnstore-Maintenance | SQL Server 2019–2025; Maßnahmenschwellen workloadabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | neue Maintenance-Funktion oder geänderte Messgrößen |
| `SRC-016` | PRIMARY | [Columnstore indexes overview](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/columnstore-indexes-overview?view=sql-server-ver17) | Rowgroups, Delta Store, Delete Bitmap und Background Merge; `IDX-009`, `IDX-010` (Columnstore-Segmente gezielt überspringen) | SQL Server 2019–2025; Edition und Featureumfang prüfen | 2026-07-24 | 2026-07-24 | ACTIVE | neue Columnstore-Funktion oder Editionsänderung |
| `SRC-017` | PRIMARY | [Columnstore query performance](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/columnstore-indexes-query-performance?view=sql-server-ver17) | Batch Mode, Segment Elimination und Rowgroup-Qualität; `IDX-010` | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | geänderte Batch-/Segment-Verhaltensbeschreibung |
| `SRC-018` | PRIMARY | [Partitioned tables and indexes](https://learn.microsoft.com/en-us/sql/relational-databases/partitions/partitioned-tables-and-indexes?view=sql-server-ver17) | Partitionierung, Alignment und Partition Elimination; `QRY-012` | SQL Server 2019–2025; Edition/Limit prüfen | 2026-07-24 | 2026-07-24 | ACTIVE | Funktions- oder Editionsänderung |
| `SRC-019` | PRIMARY | [sys.partitions](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-partitions-transact-sql?view=sql-server-ver17) | Partition-Metadaten und `index_id`-Semantik; `STL-004` | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Katalogspalten- oder Semantikänderung |
| `SRC-020` | PRIMARY | [Create linked servers](https://learn.microsoft.com/en-us/sql/relational-databases/linked-servers/create-linked-servers-sql-server-database-engine?view=sql-server-ver17) | Provider-, Collation- und Pushdown-Grenzen; `QRY-012` | provider- und versionsabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | Provider- oder Sicherheitsänderung |
| `SRC-021` | PRIMARY | [sp_addlinkedserver](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-addlinkedserver-transact-sql?view=sql-server-ver17) | Providerparameter und SQL-Server-2025-Verschlüsselungsanforderung | SQL Server 2019–2025; OLE DB Driver beachten | 2026-07-24 | 2026-07-24 | ACTIVE | Treiber-, Provider- oder Verschlüsselungsänderung |
| `SRC-022` | PRIMARY | [Breaking changes in SQL Server 2025](https://learn.microsoft.com/en-us/sql/database-engine/breaking-changes-to-database-engine-features-in-sql-server-2025?view=sql-server-ver17) | migrationskritische Grenzen von SQL Server 2025 | SQL Server 2025 | 2026-07-24 | 2026-07-24 | ACTIVE | neue Breaking-Change-Dokumentation oder CU-bedingte Korrektur |
| `SRC-023` | PRIMARY | [HASHBYTES](https://learn.microsoft.com/en-us/sql/t-sql/functions/hashbytes-transact-sql?view=sql-server-ver17) | Hashalgorithmen und endliche Hashausgabe; Hash-Eindeutigkeitsinferenz | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Algorithmus- oder Deprecation-Änderung |
| `SRC-024` | PRIMARY | [Create unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17) | Eindeutigkeitsgarantie des Indexschlüssels; Hash-Eindeutigkeitsinferenz | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Änderung der Unique-Index-Semantik |
| `SRC-025` | PRIMARY | [Optimized locking](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-locking?view=sql-server-ver17) | TID (Transaction ID; Transaktionskennung) Locking, LAQ (Lock After Qualification; Sperren erst nach Prüfung der Zeilenqualifikation), ADR-/RCSI-Voraussetzungen und Grenzen; `CON-008` | SQL Server 2025; Datenbankkonfiguration | 2026-07-24 | 2026-07-24 | ACTIVE | Featureänderung, neue Plattform oder geänderte Voraussetzung |
| `SRC-026` | PRIMARY | [Optional parameter plan optimization](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optional-parameter-optimization?view=sql-server-ver17) | OPPO, Dispatcher- und Variant Plans; `QRY-004` (Optionale Filter, Recompile und dynamisches SQL), `OPT-010` (Planoptimierung für optionale Parameter) | SQL Server 2025, CL 170, Datenbankkonfiguration | 2026-07-24 | 2026-07-24 | ACTIVE | Eligibility- oder Defaultänderung |
| `SRC-027` | PRIMARY | [Monitor performance by using the Query Store](https://learn.microsoft.com/en-us/sql/relational-databases/performance/monitoring-performance-by-using-the-query-store?view=sql-server-ver17) | Query-/Plan-/Runtime-Historie, Waits, Regressionen und Plansteuerung; `DGN-003` (Abfragehistorie mit Query Store) | SQL Server 2019–2025; Konfiguration und Read/Write-Status | 2026-07-24 | 2026-07-24 | ACTIVE | Default-, Schema- oder Retention-Änderung |
| `SRC-028` | PRIMARY | [Performance monitoring and tuning tools](https://learn.microsoft.com/en-us/sql/relational-databases/performance/performance-monitoring-and-tuning-tools?view=sql-server-ver17) | Abgrenzung von DMVs (Dynamic Management Views; dynamische Verwaltungssichten für Diagnoseinformationen), Extended Events und weiteren Beobachtungsquellen; Diagnosemethode | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Werkzeug- oder Scopeänderung |
| `SRC-029` | PRIMARY | [tempdb database](https://learn.microsoft.com/en-us/sql/relational-databases/databases/tempdb-database?view=sql-server-ver17) | temporäre Objekte, Worktables, Spills, Version Store und TempDB-Funktionen; `CON-009` (Kosten in tempdb unterscheiden) | SQL Server 2019–2025; versionsabhängige Funktionen | 2026-07-24 | 2026-07-24 | ACTIVE | neue TempDB-Funktion oder Setupempfehlung |
| `SRC-030` | PRIMARY | [Data type precedence](https://learn.microsoft.com/en-us/sql/t-sql/data-types/data-type-precedence-transact-sql?view=sql-server-ver17) | Implicit Conversion und Type Precedence; `QRY-002` | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Datentyp- oder Präzedenzänderung |
| `SRC-031` | PRIMARY | [Display an actual execution plan](https://learn.microsoft.com/en-us/sql/relational-databases/performance/display-an-actual-execution-plan?view=sql-server-ver17) | Runtime-Information im Actual Execution Plan; `OPT-001`, `FWK-005` (Vertrag für Plan- und Statistikevidenz) | SQL Server 2019–2025; Clientdarstellung beachten | 2026-07-24 | 2026-07-24 | ACTIVE | Planattribut- oder Tooländerung |
| `SRC-032` | PRIMARY | [Tune nonclustered indexes with missing index suggestions](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/tune-nonclustered-missing-index-suggestions?view=sql-server-ver17) | Grenzen optimizerbasierter Indexvorschläge; `IDX-005` | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | neue Limitierung oder geänderte DMV-Dokumentation |
| `SRC-033` | PRIMARY | [The transaction log](https://learn.microsoft.com/en-us/sql/relational-databases/logs/the-transaction-log-sql-server?view=sql-server-ver17) | Write-ahead logging, Log Flush, Recovery und VLF-Kontext; `STL-007` bis `STL-009` (Mehrere Änderungen gemeinsam bestätigen) | SQL Server 2019–2025 | 2026-07-24 | 2026-07-24 | ACTIVE | Logarchitektur- oder Recoveryänderung |
| `SRC-034` | PRIMARY | [Database instant file initialization](https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-instant-file-initialization?view=sql-server-ver17) | Data-File-IFI und Log-Autogrowth bis 64 MB ab SQL Server 2022; `STL-005` | SQL Server 2019–2025; Plattform und Berechtigung beachten | 2026-10-05 | 2026-10-05 | ACTIVE | Plattform-, Berechtigungs- oder Log-IFI-Änderung |
| `SRC-035` | PRIMARY | [sys.dm_os_wait_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-wait-stats-transact-sql?view=sql-server-ver17) | instanzweite kumulative Wait Stats und Delta-Bildung; `RES-007` (Wartezeiten im richtigen Messbereich) | SQL Server 2019–2025; Rechte versionsabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | DMV-Spalten-, Scope- oder Rechteänderung |
| `SRC-036` | PRIMARY | [sys.dm_os_waiting_tasks](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-waiting-tasks-transact-sql?view=sql-server-ver17) | aktuelle wartende Tasks, Ressourcen und Blocking-Evidenz; `CON-004` (Blockierungsketten verfolgen), `RES-007` | SQL Server 2019–2025; Rechte versionsabhängig | 2026-07-24 | 2026-07-24 | ACTIVE | DMV-Spalten-, Scope- oder Rechteänderung |
| `SRC-058` | PRIMARY | [What's new in SQL Server 2025](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17) | Einstieg für den SQL-Server-2025-Delta-Review; ersetzt keine Featureseite | SQL Server 2025 | 2026-08-28 | 2026-08-28 | ACTIVE | Release Note, CU (Cumulative Update; kumulatives Produktupdate) oder Änderung des GA-/Preview-Status |
| `SRC-059` | PRIMARY | [sp_executesql – OPTIMIZED_SP_EXECUTESQL](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-executesql-transact-sql?view=sql-server-ver17#optimized_sp_executesql) | serialisierte Compilation identischer Batches, Default OFF und Statistikempfehlung; möglicher Bezug zu `QRY-004` | SQL Server 2025; Datenbankkonfiguration und konkurrierende Compilation erforderlich | 2026-08-28 | 2026-08-28 | ACTIVE | Default-, Wait- oder Konfigurationsänderung |
| `SRC-060` | PRIMARY | [Extended Events sessions – time-bound sessions](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/sql-server-extended-events-sessions?view=sql-server-ver17#time-bound-event-sessions) | `MAX_DURATION` und automatische Beendigung; optionaler Pfad in `DGN-005` (Gezielte Ereigniserfassung mit Extended Events) | SQL Server 2025; Basispfad bleibt 2019–2025 | 2026-08-28 | 2026-08-28 | ACTIVE | Syntax-, Plattform- oder Maximaldaueränderung |
| `SRC-061` | PRIMARY | [CE feedback for expressions](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-ce-feedback-for-expressions?view=sql-server-ver17) | ausdrucksübergreifende Fingerprints, Feedbackzustände und Showplan-/XE-Evidenz; `OPT-006` | SQL Server 2025; CL 160+; Datenbankkonfiguration und Eligibility | 2026-08-28 | 2026-08-28 | ACTIVE | Voraussetzung, Default oder Telemetrieänderung |
| `SRC-062` | PRIMARY | [Tempdb space resource governance](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/tempdb-space-resource-governance?view=sql-server-ver17) | workloadgruppenbezogene TempDB-Datenlimits, Fehler 1138 und Governance-DMVs; möglicher Bezug zu `CON-009`, `RES-004` | SQL Server 2025; instanzweite Resource-Governor-Konfiguration; TempDB-Log und Version Store nicht umfasst | 2026-08-28 | 2026-08-28 | ACTIVE | Editions-, Scope-, DMV- oder Fehlersemantikänderung |
| `SRC-063` | PRIMARY | [Performance tuning with ordered columnstore indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/ordered-columnstore-indexes?view=sql-server-ver17) | Segmentüberlappung, Best-Effort-Ordnung, DOP-/Online-/TempDB-Grenzen; möglicher Bezug zu `IDX-010` | SQL Server 2025 für ordered nonclustered columnstore; Edition und Buildoptionen prüfen | 2026-08-28 | 2026-08-28 | ACTIVE | Editions-, Online-Build- oder Ordnungsgüteänderung |
| `SRC-064` | PRIMARY | [Query Store for secondary replicas](https://learn.microsoft.com/en-us/sql/relational-databases/performance/query-store-for-secondary-replicas?view=sql-server-ver17) | Runtime-/Wait-Erfassung lesbarer Secondaries und Rollensicht | SQL Server 2025; Preview; Always-On-Availability-Group erforderlich | 2026-08-28 | 2026-08-28 | ACTIVE | Preview-/GA-Status, Default oder unterstützte Topologie |
| `SRC-065` | PRIMARY | [Vector data type](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17) | Abgrenzungsquelle für Vector-/KI-Funktionen außerhalb des Performance-Curriculums | SQL Server 2025; Teilfunktionen und Treiberunterstützung versions-/previewabhängig | 2026-08-28 | 2026-08-28 | ACTIVE | Curriculumänderung oder GA-/Treiberstatus |
| `SRC-066` | PRIMARY | [Deadlocks guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide?view=sql-server-ver17) | Deadlock-Zyklus, Opferauflösung, Fehler 1205 und `xml_deadlock_report`; `CON-006` (Zyklische Sperrkonflikte erkennen) | SQL Server 2019–2025; konkrete Opferwahl und Graphinhalt runtimeabhängig | 2026-09-01 | 2026-09-01 | ACTIVE | geänderte Deadlockerkennung, Ereignis- oder Fehlersemantik |
| `SRC-067` | PRIMARY | [SET DEADLOCK_PRIORITY](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-deadlock-priority-transact-sql?view=sql-server-ver17) | Opferpriorität und Kostenentscheidung; `CON-006` | SQL Server 2019–2025; `LOW`, `NORMAL`, `HIGH` und numerische Prioritäten | 2026-09-01 | 2026-09-01 | ACTIVE | geänderte Prioritäts- oder Opferauswahlsemantik |
| `SRC-068` | PRIMARY | [Use the system_health session](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/use-the-system-health-session?view=sql-server-ver17) | vorhandene, begrenzte Deadlock-Graph-Evidenz aus `system_health`; `CON-006` | SQL Server 2019–2025; Retention und Sichtbarkeit sind keine Golden Values | 2026-09-01 | 2026-09-01 | ACTIVE | geänderte Standardsession, Targets oder Retention |
| `SRC-069` | PRIMARY | [IN (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/in-transact-sql?view=sql-server-ver15) | `IN`/`NOT IN` mit Unterabfrage und `NULL`-Rückgabewerten; `QRY-006` (NULL bei NOT IN und NOT EXISTS) | SQL Server 2019–2025; logische Ausdruckssemantik | 2026-09-19 | 2026-09-19 | ACTIVE | Änderung der `IN`-, `NOT IN`- oder `NULL`-Semantik |
| `SRC-070` | PRIMARY | [EXISTS (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/exists-transact-sql?view=sql-server-ver17) | `EXISTS` und `NOT EXISTS` als Existenzprüfung einer Unterabfrage; `QRY-006` | SQL Server 2019–2025; logische Ausdruckssemantik | 2026-09-19 | 2026-09-19 | ACTIVE | Änderung der `EXISTS`- oder `NOT EXISTS`-Semantik |
| `SRC-071` | PRIMARY | [NULL and UNKNOWN (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/null-and-unknown-transact-sql?view=sql-server-ver17) | dreiwertige Logik mit `NULL` und `UNKNOWN` für die Ergebniserklärung von `QRY-006` | SQL Server 2019–2025; logische Ausdruckssemantik | 2026-09-19 | 2026-09-19 | ACTIVE | Änderung der `NULL`-/`UNKNOWN`-Semantik |

## 5. Aktive ergänzende Fach- und Methodenquellen

Die folgenden Quellen vertiefen Operatorverhalten, Optimizer-Interna, Diagnosemethodik und reproduzierbare Fallgestaltung. Sie dürfen eine Microsoft-Primärquelle nicht ersetzen. Undokumentierte Interna werden nur als `EMPIRICAL` oder `INFERENCE` verwendet und benötigen Runtime-Evidenz in der zutreffenden Zielversion. Inhalte, Diagramme und Beispiele werden nicht übernommen; zulässig sind Verweise, eigenständige Erklärungen und eigene synthetische Reproduktionen.

| ID | Klasse | Quelle | Aussagebezug | Gültigkeitsbereich | Aktualisiert | Abgerufen | Status | Review-Trigger |
|---|---|---|---|---|---|---|---|---|
| `SRC-037` | SUPPORTING | [SQL Server Execution Plan Reference](https://sqlserverfast.com/epr/) | Operatorreferenz, Planleselogik und Vertiefungsstrang `V-OPT-A` | Referenz deckt viele Versionen ab; jede konkrete Aussage gegen Zielversion und Primärquelle prüfen | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte Operatorseite, neue Engine-/SSMS-Version oder Lizenz-/Nutzungshinweis |
| `SRC-038` | SUPPORTING | [Generic information – Execution Plans](https://sqlserverfast.com/epr/generic_information/) | Estimated/Actual Plan, Planquellen, Datenfluss und grundlegende Fehlannahmen; `OPT-001`, `OPT-015` (Ausführungspläne systematisch lesen) | SQL Server 2019–2025; Clientdarstellung versionsabhängig | 2026-07-26 | 2026-07-26 | ACTIVE | neue Planart oder geänderte Clientdarstellung |
| `SRC-039` | SUPPORTING | [Common properties](https://sqlserverfast.com/epr/common-properties/) | gemeinsame Operatorattribute, Estimated/Actual Rows, Number of Executions, Rebind/Rewind; `OPT-015`, `OPT-016` (Wiederholte Operatorausführung und Zwischenspeicherung) | konkrete Attribute versionsabhängig; Runtime-Evidenz erforderlich | 2026-07-26 | 2026-07-26 | ACTIVE | neue oder geänderte Planattribute |
| `SRC-040` | SUPPORTING | [Plan properties](https://sqlserverfast.com/epr/plan-properties/) | planweite Eigenschaften, Set Options, MemoryGrantInfo, ThreadStat, Warnings, Dispatcher; `OPT-015`, `QRY-013` (Anwendung langsam, Verwaltungswerkzeug schnell), `OPT-017` (Ungleich verteilte parallele Arbeit) | SQL Server und SSMS (SQL Server Management Studio; Verwaltungs- und Abfragewerkzeug)/VS-Code-Version getrennt beachten | 2026-07-26 | 2026-07-26 | ACTIVE | neue Engine-, CU- oder Clientversion |
| `SRC-041` | SUPPORTING | [Setting and Identifying Row Goals in Execution Plans](https://sqlperformance.com/2018/02/sql-plan/setting-and-identifying-row-goals) | Ursachen, Identifikation und kontrollierte Gegenprobe für Row Goals; `OPT-011` | Optimizer-Interna; SQL Server 2019–2025 empirisch revalidieren | 2026-07-26 | 2026-07-26 | ACTIVE | abweichende Planform oder geänderte Hint-/Trace-Flag-Dokumentation |
| `SRC-042` | SUPPORTING | [Nested Loops Joins and Performance Spools](https://sqlperformance.com/2019/09/sql-performance/nested-loops-joins-performance-spools) | Apply/Nested Loops, Performance Spools, Outer References; `OPT-016`, `OPT-012` | undokumentierte Optimizerdetails; eigene Reproduktion erforderlich | 2026-07-26 | 2026-07-26 | ACTIVE | abweichendes Verhalten in einer Zielversion |
| `SRC-043` | SUPPORTING | [Parallel Execution Plans – Branches and Threads](https://sqlperformance.com/2013/10/sql-plan/parallel-plans-branches-threads) | Branches, Threads und ThreadStat; `OPT-017`, `RES-002` | Planattribute und Engine-Verhalten versionsabhängig | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte Parallelitäts- oder Planattributsemantik |
| `SRC-044` | SUPPORTING | [Understanding Execution Plan Operator Timings](https://sqlperformance.com/2021/03/sql-performance/execution-plan-timings) | Grenzen operatorbezogener CPU-/Elapsed-Zeiten in Row/Batch Mode und Parallelität; `OPT-017`, `DGN-001` | SQL Server 2019–2025; tatsächliche Client-/CU-Ausgabe prüfen | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte Runtime-Plan-Timing-Semantik |
| `SRC-045` | SUPPORTING | [Dynamic Search Conditions in T-SQL](https://www.sommarskog.se/dyn-search.html) | statisches SQL mit Recompile, parameterisiertes dynamisches SQL, optionale und mehrwertige Suchbedingungen; `QRY-004` | Grundmuster versionsübergreifend; PSP/OPPO separat über Primärquellen bewerten | 2026-07-26 | 2026-07-26 | ACTIVE | neue Revision oder geänderte Produktfunktion |
| `SRC-046` | SUPPORTING | [Slow in the Application, Fast in SSMS?](https://www.sommarskog.se/query-plan-mysteries.html) | Plan Cache, SET-Optionen, Cache Keys, Parameterwerte, Anwendung-/SSMS-Differenzen; `QRY-013`, `OPT-007`, `OPT-008` | Revision 2026; einzelne Cache-/Clientdetails gegen Zielversion prüfen | 2026-07-26 | 2026-07-26 | ACTIVE | neue Revision, Treiberänderung oder abweichende Runtime-Evidenz |
| `SRC-047` | EMPIRICAL_METHOD | [What is Parameter Sniffing in SQL Server?](https://www.brentozar.com/archive/2013/06/the-elephant-and-the-mouse-or-parameter-sniffing-in-sql-server/) | didaktische Skew-Reproduktion, Planvergleich und kompilierte Parameterwerte; `OPT-008` | Fallmethode; keine universelle Plan- oder Indexempfehlung | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte Produktfunktion oder nicht reproduzierbarer Effekt |
| `SRC-048` | EMPIRICAL_METHOD | [PSPO: How SQL Server 2022 Tries to Fix Parameter Sniffing](https://www.brentozar.com/archive/2022/08/pspo-how-sql-server-2022-tries-to-fix-parameter-sniffing/) | empirische Grenzfälle von PSP, Query Variants und verbleibender Parameter Sensitivity; `OPT-009` (Parametersensitive Planoptimierung) | SQL Server 2022-Beispiel; aktuelle Primärdokumentation und Ziel-CU maßgeblich | 2026-07-26 | 2026-07-26 | ACTIVE | PSP-Verhaltensänderung oder neue CU-Evidenz |
| `SRC-049` | EMPIRICAL_METHOD | [Handling Optional Parameters](https://erikdarling.com/software-vendor-mistakes-with-sql-server-handling-optional-parameters/) | Catch-all-Prädikate, Schätzfehler und dynamische Suchbedingungen; `QRY-004` | Fallmethode; Sicherheit und Version separat prüfen | 2026-07-26 | 2026-07-26 | ACTIVE | OPPO-/CE-Änderung oder abweichendes Testresultat |
| `SRC-050` | EMPIRICAL_METHOD | [A Little About Memory Grants in SQL Server Query Plans](https://erikdarling.com/a-little-about-memory-grants-in-sql-server-query-plans/) | speicherverbrauchende Operatoren, Zeilenbreite, Sort/Hash und Parallelität; `OPT-014`, `RES-004` | empirische Erklärung; Formeln und Schwellen nicht als dokumentiert behandeln | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte Planattribute oder abweichendes Runtime-Verhalten |
| `SRC-051` | EMPIRICAL_METHOD | [Capturing Query Wait Stats with sp_HumanEvents](https://erikdarling.com/sql-server-community-tools-capturing-query-wait-stats-with-sp_humanevents/) | zeitlicher und querybezogener Wait-Scope als Diagnoseprinzip; `RES-007`, `DGN-005`, `DGN-007` (Zeitabhängige Regression eines Suchworkloads) | Methode; Schulung implementiert eigene T-SQL-/XE-Evidenz und setzt kein Drittanbieter-Tool voraus | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte XE-/Wait-Daten oder Werkzeugabhängigkeit |

## 6. Aktive Präsentations- und Automatisierungsquellen

Diese Microsoft-Primärquellen tragen ausschließlich Aussagen zur PowerPoint-Variantenarchitektur und zum unterstützten Ausführungsmodell. Sie begründen keine SQL-Server-Produkteigenschaft.

| ID | Klasse | Quelle | Aussagebezug | Gültigkeitsbereich | Aktualisiert | Abgerufen | Status | Review-Trigger |
|---|---|---|---|---|---|---|---|---|
| `SRC-052` | PRIMARY | [Create and present a custom show](https://support.microsoft.com/en-us/powerpoint/create-and-present-a-custom-show) | Custom Shows als benannte Teilmengen einer Präsentation für unterschiedliche Zielgruppen; `PRS-009`, `PRS-012` | PowerPoint Desktop; PowerPoint für das Web kann Custom Shows nicht erstellen | 2026-07-26 | 2026-07-26 | ACTIVE | geänderte Custom-Show-Unterstützung oder neue PowerPoint-Hauptversion |
| `SRC-053` | PRIMARY | [SlideShowSettings.NamedSlideShows property](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowsettings.namedslideshows) | programmgesteuerte Anlage und Verwaltung benannter Custom Shows; `PRS-012` | PowerPoint-Objektmodell; konkrete Office-Version prüfen | 2026-07-26 | 2026-07-26 | ACTIVE | Änderung des PowerPoint-Objektmodells |
| `SRC-054` | PRIMARY | [NamedSlideShow.SlideIDs property](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.namedslideshow.slideids) | Zuordnung einer Custom Show über native Slide-IDs; `PRS-012`, `TST-011` | PowerPoint-Objektmodell; native SlideID ist keine projektweite Identität | 2026-07-26 | 2026-07-26 | ACTIVE | Änderung der SlideID- oder Custom-Show-Semantik |
| `SRC-055` | PRIMARY | [Presentation.SaveCopyAs method](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.presentation.savecopyas) | Speichern einer Präsentationskopie ohne Änderung des Originals; `PRS-013` | PowerPoint Desktop und Objektmodell | 2026-07-26 | 2026-07-26 | ACTIVE | Änderung der SaveCopyAs-Semantik oder Dateiformate |
| `SRC-056` | PRIMARY | [SlideRange.Delete method](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.sliderange.delete) | Entfernen ausgeschlossener Folien aus einer erzeugten Kopie; `PRS-013` | PowerPoint-Objektmodell | 2026-07-26 | 2026-07-26 | ACTIVE | Änderung der SlideRange-Semantik |
| `SRC-057` | PRIMARY | [Considerations for server-side Automation of Office](https://support.microsoft.com/en-us/visio/considerations-for-server-side-automation-of-office) | Abgrenzung interaktiver Clientautomation von unbeaufsichtigter serverseitiger Office-Automation; `PRS-013`, `TST-011` | Office-Anwendungen; unbeaufsichtigte nicht-interaktive Automation wird nicht empfohlen oder unterstützt | 2026-07-26 | 2026-07-26 | ACTIVE | neue offizielle Automatisierungs- oder Lizenzierungsrichtlinie |

## 7. Pflegeprozess

Eine Quelle wird erneut geprüft, wenn mindestens eines der folgenden Ereignisse eintritt:

- Aufnahme einer neuen SQL-Server-Hauptversion oder eines neuen Compatibility Levels,
- Änderung eines aktiven Claims, Lernziels oder Demo-Vertrags,
- Änderung der referenzierten Herstellerdokumentation,
- neue oder geänderte Feature-Voraussetzung,
- Änderung des PowerPoint-Objektmodells oder des unterstützten Automatisierungsmodells,
- Runtime-Ergebnis, das der dokumentierten Erwartung widerspricht,
- nicht mehr erreichbarer, umgeleiteter oder als veraltet gekennzeichneter Verweis.

Bei einer inhaltlichen Änderung wird `Aktualisiert` gesetzt und der betroffene Aussagebezug geprüft. Ein nicht erreichbarer Link wird nicht stillschweigend ersetzt. Der Eintrag erhält zunächst `REVIEW_REQUIRED`; Ersatzquelle, geänderte Interpretation und betroffene Claims werden im Konflikt- und Entscheidungslog dokumentiert.

## 8. Abnahme von W0-006, ADV-001 und PRS-009

Die in Welle 0 verwendeten 36 SQL-Server-Primärquellen, die acht Primärquellen des SQL-Server-2025-Delta-Reviews und die drei Primärquellen des `CON-006`-Szenarioreviews besitzen jeweils eine stabile ID, einen Aussagebezug, einen Gültigkeitsbereich, ein Aktualisierungs- und Abrufdatum, einen Status und einen Review-Trigger. Die 15 ergänzenden Fach- und Methodenquellen bleiben getrennt klassifiziert. Die sechs PowerPoint-Primärquellen tragen die Präsentationsentscheidungen. Damit bleibt `W0-006` abgeschlossen; die Quellenregistrierung für `ADV-001`, `PRS-009`, `W-SQL25-001` und `LABSCN-005/CON-006` ist erfüllt.

Weitere Quellen werden fortlaufend in diesem Register ergänzt. Das frühere Dokument `PRIMARY_SOURCES_W0.md` bleibt als validierter Welle-0-Snapshot erhalten; bei widersprüchlichen Pflegeinformationen ist dieses projektweite Register maßgeblich.

## 9. KI-Workstream: aktuelle Primärquellen und Aussagegrenzen

Registriert für `TSK-003` (KI (künstliche Intelligenz; Verfahren für Aufgaben wie Textverarbeitung oder Vorhersagen) mit und für Microsoft SQL Server 2025: Planungsintegration) am 2026-10-11. Neue Quellenkennungen werden in diesem bestehenden
Register vergeben, außerhalb der Task-/Demo-Registry. ACTIVE bedeutet fachlich abgerufene
Quelle, keine Runtimevalidierung. Microsoft (2026) und Ollama (2026) werden mit Titel, URL
und Abrufdatum zitiert; die Forschungsarbeiten mit Erscheinungsjahr. Eigene Erklärungen
ersetzen die Übernahme fremder Lehrbeispiele. Alle Einträge wurden am 2026-10-11 geprüft.
Featurestatus und Voraussetzungen stehen zusätzlich in der
[Featurematrix](SQL_SERVER_2025_AI_FEATURE_MATRIX.md).

| ID | Klasse | Quelle | Aussagebezug | Gültigkeitsbereich / Aussagegrenze | Aktualisiert | Abgerufen | Status | Review-Trigger |
|---|---|---|---|---|---|---|---|---|
| `SRC-072` | PRIMARY | Microsoft (2026), [Vector data type](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17) | VECTOR, Dimension, float32/float16, CL und Treiber | 17.x float32 GA (General Availability; allgemeine Produktverfügbarkeit), float16 Preview; Azurestatus getrennt; kein Benchmark | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API (Application Programming Interface; Programmierschnittstelle), Rechte, Status oder neue abweichende Evidenz |
| `SRC-073` | PRIMARY | Microsoft (2026), [VECTOR_DISTANCE](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-distance-transact-sql?view=sql-server-ver17) | Exact-Distance und Metrics; QRY-015, IDX-011 | 17.x GA; keine Vector-Indexnutzung; kein Relevanzbeweis | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-074` | PRIMARY | Microsoft (2026), [VECTOR_NORM](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-norm-transact-sql?view=sql-server-ver17) | Normtypen; QRY-015 | 17.x GA; Floating-Point-Erwartungen gesondert qualifizieren | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-075` | PRIMARY | Microsoft (2026), [VECTOR_NORMALIZE](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-normalize-transact-sql?view=sql-server-ver17) | Normalisierung; QRY-015 | 17.x GA; Modellnormalisierung nicht pauschal voraussetzen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-076` | PRIMARY | Microsoft (2026), [VECTORPROPERTY](https://learn.microsoft.com/en-us/sql/t-sql/functions/vectorproperty-transact-sql?view=sql-server-ver17) | Dimensions/BaseType; QRY-014 | 17.x GA; Metadaten ersetzen keine Modellprovenienz | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-077` | PRIMARY | Microsoft (2026), [CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17) | DiskANN, Indexgeneration, Build/DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten); IDX-011, IDX-012 | 17.x Preview; PREVIEW_FEATURES/ALTER; neuestes Format derzeit explizit Azure; Buildgrenzen offen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-078` | PRIMARY | Microsoft (2026), [VECTOR_SEARCH](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17) | Syntaxgeneration, Filter, Fallback; IDX-011, CON-010 | 17.x Preview, Azure SQL Database GA; TOP_N und WITH APPROXIMATE getrennt | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-079` | PRIMARY | Microsoft (2026), [AI_GENERATE_CHUNKS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-chunks-transact-sql?view=sql-server-ver17) | Lokales FIXED-Chunking; QRY-016 | 17.x CL170+, kein Previewhinweis; Zeichen statt Tokens; kein Modellcall | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-080` | PRIMARY | Microsoft (2026), [CREATE EXTERNAL MODEL](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-model-transact-sql?view=sql-server-ver17) | API_FORMAT, Rechte, TLS (Transport Layer Security; Verschlüsselungsprotokoll für Verbindungen) und ONNX (Open Neural Network Exchange; Austauschformat für Modelle); QRY-020 bis QRY-022, DGN-008 | 17.x REST (Representational State Transfer; Architekturstil für Webschnittstellen) ohne Previewhinweis; ONNX Preview/Windows/ML Services; Linuxkonflikt offen; kein Chatobjekt | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-081` | PRIMARY | Microsoft (2026), [AI_GENERATE_EMBEDDINGS](https://learn.microsoft.com/en-us/sql/t-sql/functions/ai-generate-embeddings-transact-sql?view=sql-server-ver17) | Inferenz und Diagnoseevents; QRY-020, DGN-011 | 17.x EMBEDDINGS-Modell/Grants; REST ohne Previewhinweis; Resultattyptext vs. skalare Beispiele offen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-082` | PRIMARY | Microsoft (2026), [sp_invoke_external_rest_endpoint](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-invoke-external-rest-endpoint-transact-sql?view=sql-server-ver17) | RESTrechte, TLS, Waits und Credentialgrenze; DGN-008, DGN-011 | 17.x standardmaessig deaktiviert; Azureallowlist nicht automatisch SQL Server; kein Netzlatenzbeweis | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-083` | PRIMARY | Microsoft (2026), [SQL Server 2025 editions](https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025?view=sql-server-ver17) | Windows-Editionen, AI und Ressourcen | 17.x Enterprise/Standard/Express; Developerprofil separat; kein Editionstest | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-084` | PRIMARY | Microsoft (2026), [SQL Server 2025 on Linux editions](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-editions-and-components-2025?view=sql-server-ver17) | Linuxeditionen und OS-Grenzen | 17.x; ONNX-Tabellenangabe widerspricht konkretem Windowsverfahren in SRC-080 | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-085` | PRIMARY | Ollama (2026), [Generate embeddings](https://docs.ollama.com/api/embed) | Ollama /api/embed, Payload, Dimension, Truncation, Timing | Provider; keine Enginegarantie; Modell/API separat probepruefen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-086` | PRIMARY | Ollama (2026), [Authentication](https://docs.ollama.com/api/authentication) | Lokale API ohne Auth; Cloudrouting getrennt | HTTPdefault kein SQL-HTTPS-Endpunkt; Cloudrouting im lokalen Pfad gesperrt | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-087` | PRIMARY | Microsoft (2026), [Generate embeddings with Azure OpenAI](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings) | Embeddingbegriff, Deployment und Tokenlimits | Provider-v1-API; SQL-API_FORMAT-Kompatibilitaet separat; kein Cloudaufbau autorisiert | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-088` | PRIMARY | Microsoft (2026), [Foundry Models data privacy](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy) | Verarbeitung und Retention | Deployment/Modell/Service abhaengig; keine allgemeine Zero-Retention-/Compliancegarantie | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-089` | PRIMARY | Microsoft (2026), [GitHub Copilot in SSMS overview](https://learn.microsoft.com/en-us/ssms/github-copilot/overview) | Client-/Enginegrenze und Assistenz | SSMS22, mehrere Engines; kein alter Azure-OpenAI-Copilot-Previewclaim oder Wirkungsbeleg | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-090` | PRIMARY | Microsoft (2026), [SSMS Agent mode](https://learn.microsoft.com/en-us/ssms/github-copilot/agent-mode) | Tools, Approval und Least Privilege | Ab SSMS22.7; Release Notes und konkreter MCPbuild massgeblich; kein Rechteersatz | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-091` | PRIMARY | Microsoft (2026), [Execution context for GitHub Copilot](https://learn.microsoft.com/en-us/ssms/github-copilot/execution-context) | SQL-Login/User und delegierter Kontext | Client; Kontorechte/Impersonation pruefen; Approval keine Sicherheitsgrenze | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-092` | PRIMARY | Microsoft (2026), [SSMS 22 release notes](https://learn.microsoft.com/en-us/ssms/release-notes-22) | Copilot GA22.4.1, Agent GA22.10.2 | Clientstand 22.10.2 vom 2026-09-28; keine Enginegarantie | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-093` | PRIMARY | Microsoft (2026), [Row-Level Security](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17) | DBseitige Zugriffsgrenze; CON-010 | SQL Server; ANN-/Pooling-/Tenantkombination getrennt testen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-094` | PRIMARY | Microsoft Research (2019), [DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/) | Graph-/ANN-Konzept und Recalltrade-off | Forschungsalgorithmus 2019; kein SQL-Internals-/Benchmarkversprechen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-095` | PRIMARY | NeurIPS (2020), [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://papers.nips.cc/paper_files/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html) | Retrieval, Generierung und Provenienzproblem | Forschungsarchitektur 2020; keine Garantie fuer heutige RAG-Antwortkorrektheit | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-096` | PRIMARY | Microsoft (2026), [CREATE DATABASE SCOPED CREDENTIAL](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-database-scoped-credential-transact-sql?view=sql-server-ver17) | Credentialobjekt/-Rechte und Secretgrenze | 17.x Lab; Endpointregeln zusaetzlich SRC-080/082; keine Beispielsweisecrets uebernehmen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-097` | PRIMARY | Microsoft (2026), [sys.vector_indexes](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-vector-indexes-transact-sql?view=sql-server-ver17) | Indexmetadaten und Buildparameter | 17.x Previewindex; kein Nutzungs-/Recallbeweis | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-098` | PRIMARY | Microsoft (2026), [SSMS Copilot admin controls](https://learn.microsoft.com/en-us/ssms/github-copilot/admin-controls) | Administrative Clientbegrenzung | SSMS22; Policy und konkrete Clientversion getrennt pruefen | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-099` | PRIMARY | Microsoft (2026), [SQL Injection](https://learn.microsoft.com/en-us/sql/relational-databases/security/sql-injection?view=sql-server-ver17) | Parameter/Identifier und untrusted Querytext; QRY-019 | SQL Server; konkrete Statements/Rollen pruefen; LLMtext untrusted | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |
| `SRC-100` | PRIMARY | Microsoft (2026), [Full-Text Search](https://learn.microsoft.com/en-us/sql/relational-databases/search/full-text-search?view=sql-server-ver17) | Lexikalische Suchalternative; QRY-017 | SQL Server; installierte Komponente/Index/Population; keine semantische Antwortgarantie | 2026-10-11 | 2026-10-11 | ACTIVE | geaenderte Funktion, Version, API, Rechte, Status oder neue abweichende Evidenz |

`SRC-027`, `SRC-028` und `SRC-032` wurden für Diagnose/Assistenz am 2026-10-11 erneut gelesen.
Ihre historischen Registerzeilen und früheren Abnahmen bleiben erhalten. Query Store trägt
aggregierte Historie, Werkzeuge ihre Messbereiche und Missing-Index-Hinweise keine vollständige
Workloadentscheidung. Kein SQL-Lauf wird aus Quellenlektüre abgeleitet.

## SQL-Server-Lab-Verträge für den Implementierungspfad

Die folgenden öffentlichen Quellen wurden am 2026-10-11 am Commit
`26468023f74c85d97b253d4dde6c0c5a80b88782` gelesen. Deren datierte Referenzabnahmen
ersetzen keine neue Schulungs-Runtimequalifikation.

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-101` | PRIMARY | SQL Server Lab (2026), [Existing Ollama RAG](https://github.com/gecompat/SQL_Server_Lab/blob/26468023f74c85d97b253d4dde6c0c5a80b88782/Documentation/Architecture/AI_RAG_EXISTING_OLLAMA.md) | Öffentlicher RAG-Controller, lokaler Loopback-HTTP-Pfad, Modell-/Digestprüfung | Öffentliche Projektverträge, keine Hersteller-Freigabe oder neue Runtimeattestation | 2026-10-11 | 2026-10-11 | ACTIVE | Vertrags-/API-/Quellstandänderung oder abweichende Evidenz |
| `SRC-102` | PRIMARY | SQL Server Lab (2026), [SQL HTTPS Bridge](https://github.com/gecompat/SQL_Server_Lab/blob/26468023f74c85d97b253d4dde6c0c5a80b88782/Documentation/Architecture/AI_SQL_HTTPS_BRIDGE.md) | Interne Docker-Referenz für SQL-External-Model; kein allgemeines Gateway-API | Öffentliche Projektverträge, keine Hersteller-Freigabe oder neue Runtimeattestation | 2026-10-11 | 2026-10-11 | ACTIVE | Vertrags-/API-/Quellstandänderung oder abweichende Evidenz |
| `SRC-103` | PRIMARY | SQL Server Lab (2026), [SQL AI Local Acceleration](https://github.com/gecompat/SQL_Server_Lab/blob/26468023f74c85d97b253d4dde6c0c5a80b88782/Documentation/User/SQL_AI_LOCAL_ACCELERATION.md) | Provider-/TLS-/OVMS-Verträge; nur konkret dokumentierte Teile wiederverwenden | Öffentliche Projektverträge, keine Hersteller-Freigabe oder neue Runtimeattestation | 2026-10-11 | 2026-10-11 | ACTIVE | Vertrags-/API-/Quellstandänderung oder abweichende Evidenz |
| `SRC-104` | PRIMARY | Microsoft (2026), [OBJECTPROPERTY](https://learn.microsoft.com/en-us/sql/t-sql/functions/objectproperty-transact-sql?view=sql-server-ver17) | Full-Text-ItemCount/PopulateStatus in QRY-017 | Installierte Komponente und objektbezogene Population; keine Antwortqualitätsgarantie | 2026-10-11 | 2026-10-11 | ACTIVE | Dokumentations-/Propertyänderung oder abweichende Evidenz |
| `SRC-105` | PRIMARY | Microsoft (2026), [SET PARSEONLY](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-parseonly-transact-sql?view=sql-server-ver17) | Private Parserdiagnose ohne Kompilierung/Ausführung | Syntax allein; keine Objektbindung, Index-/Such-/Runtimeabnahme; nicht in Prozeduren/Triggern | 2026-10-11 | 2026-10-11 | ACTIVE | Dokumentations-/Parseränderung oder abweichende Evidenz |
| `SRC-106` | PRIMARY | Microsoft (2026), [SQL Server 2025 known issues](https://learn.microsoft.com/en-us/sql/sql-server/sql-server-2025-known-issues?view=sql-server-ver17#vector-index) | Ignorierter MAXDOP-Parameter bei Vector Index/Search; Ressourcenfreigabe | Dokumentierter SQL-2025-Hinweis, kein empirischer DOP-Befund am eigenen Image; Konfigurationsalternativen separat freigeben | 2026-10-11 | 2026-10-11 | ACTIVE | Behobenes Known Issue, Build-/Dokumentationsänderung oder abweichende Evidenz |
| `SRC-107` | PRIMARY | Microsoft (2026), [Preview features FAQ](https://learn.microsoft.com/sql/sql-server/preview-features-faq) | PREVIEW_FEATURES-Enable und anschließende Zustandsabfrage mit Batchgrenze | Kein Beleg, dass GO oder neue Session den eigenen Fehler 343 beheben; Preview nicht pauschal GA | 2026-10-11 | 2026-10-11 | ACTIVE | Feature-/Build-/Dokumentationsänderung oder abweichende Evidenz |
| `SRC-108` | PRIMARY | Microsoft (2026), [ALTER DATABASE SCOPED CONFIGURATION](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-scoped-configuration-transact-sql?view=sql-server-ver17) | Eigener MAXDOP-Set/Restore und dokumentierter DB-scoped-Konfigurationspfad | Zusätzlicher DB-Effekt separat freigeben; Konfigurationsattestierung ist keine tatsächliche Worker-/DOP-Messung | 2026-10-11 | 2026-10-11 | ACTIVE | Konfigurations-/Dokumentations-/Buildänderung oder abweichende Evidenz |
| `SRC-109` | PRIMARY | Microsoft (2026), [SET QUOTED_IDENTIFIER](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-quoted-identifier-transact-sql?view=sql-server-ver17) | Eigene ad-hoc-Sessionoption vor Vectorindexbuild; Vererbung an EXEC-Batch | Parse-time-Sessionzustand, kein ALTER-DATABASE-Effekt; konkrete Vectorindex-Anforderung durch eigenen Fehler 1934 belegt | 2026-10-11 | 2026-10-11 | ACTIVE | Client-/Session-/Dokumentationsänderung oder abweichende Evidenz |
| `SRC-110` | PRIMARY | Microsoft (2026), [sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17) | Private aktive Requestzähler mit Session-/Request-/Start-/Connection-/DB-Bindung | Zeit ohne preemptive Abschnitte; paralleler Row-Mode-Koordinator ohne vollständige Read-/Write-/Logical-Read-Zähler; kein DOP- oder Performancebeweis | 2026-10-11 | 2026-10-11 | ACTIVE | DMV-/Build-/Methodenänderung oder abweichende Evidenz |
| `SRC-111` | PRIMARY | Microsoft (2026), [sys.dm_exec_sessions](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-sessions-transact-sql?view=sql-server-ver17) | Historische private Sessionmessaufnahme und Quellenabgrenzung | Sessionzähler ersetzen keine attestierte aktive Batchgrenze; eigener Kandidat 01 beobachtet ausschließlich Nulldeltas | 2026-10-11 | 2026-10-11 | ACTIVE | DMV-/Build-/Methodenänderung oder abweichende Evidenz |


## Öffentliche lokale Modellkomponente

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-112` | PRIMARY | Nomic (ohne Datumsangabe), [nomic-embed-text-v1.5 Modellkarte](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) | Dokument-/Fragepräfix, nominale768-Dimension und Apache-2.0 | Kein Live-Digest-, konkreter Artefakt-/Supply-Chain- oder Antwortqualitätsbeleg | 2026-10-12 | 2026-10-12 | ACTIVE | Modellkarten-/Lizenz-/Profiländerung oder abweichende Evidenz |
| `SRC-113` | PRIMARY | SQL Server Lab (2026), [öffentliche AiModel-API](https://github.com/gecompat/SQL_Server_Lab/blob/f4c9fcd30c397e25c95e57d7aeecc98dc194063e/Public/Invoke-SqlServerLabAiModel.ps1) und zugehöriger AiEndpoint-/Katalog-/Schema-/Loadercode am selben Commit | Explizite lokale Lane ohne SQL, WhatIf und begrenzte Embedrequests | Sourcevertrag, kein SQL-RAG-/HTTPS-/Geräte-/Qualitätsnachweis; Caller muss lokale Liveidentität getrennt binden | 2026-10-12 | 2026-10-12 | ACTIVE | Vertrags-/API-/Quellstandänderung oder abweichende Evidenz |
| `SRC-114` | PRIMARY | Microsoft (ohne Datumsangabe), [CREATE LOGIN](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-login-transact-sql?view=sql-server-ver17), [CREATE USER](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql?view=sql-server-ver17), [ORIGINAL_LOGIN](https://learn.microsoft.com/en-us/sql/t-sql/functions/original-login-transact-sql?view=sql-server-ver17), [sys.sql_logins](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-sql-logins-transact-sql?view=sql-server-ver17) und [sys.database_principals](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-principals-transact-sql?view=sql-server-ver17) | Serverlogin-/DBbenutzerzuordnung, ursprüngliche Verbindungsidentität und eigene SID-/Loginmetadaten für begrenzte CON-010-Authentifizierung | Quellenvertrag, kein eigener Authentifizierungs-/Pooling-/RLS-/Cleanup-PASS; SQL-2025-Verhalten und konkrete Rechte tatsächlich prüfen | 2026-10-12 | 2026-10-12 | ACTIVE | Statement-/Funktions-/Katalog-/Versionsänderung oder abweichende Evidenz |
| `SRC-115` | PRIMARY | Microsoft (ohne Datumsangabe), [ClientConnectionId](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlconnection.clientconnectionid?view=netframework-4.8.1), [ADO.NET SQL-Connection-Pooling](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/sql-server-connection-pooling), [ClearPool](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlconnection.clearpool?view=netframework-4.8.1), [SqlCredential](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlcredential?view=netframework-4.8.1), [sys.dm_exec_connections](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-connections-transact-sql?view=sql-server-ver17) und [SESSION_CONTEXT](https://learn.microsoft.com/en-us/sql/t-sql/functions/session-context-transact-sql?view=sql-server-ver17) | Begrenzter privater Poolscope: eigene Credential-/Poolschlüssel, physische Serverbindung, Sessionreset und eigener Abbau | Client-GUID bezeichnet letzten Verbindungsversuch, keine vorab garantierte Stabilität; Reflection/Source kein TDS-/Reuse-/Reset-/Cleanup-PASS, keine Provider-/Supportempfehlung | 2026-10-12 | 2026-10-12 | ACTIVE | API-/Provider-/Build-/Poolingvertrag oder abweichende Evidenz |


## Isolierte native VECTOR-Clientabhängigkeit

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-116` | PRIMARY | Microsoft (2026), [Microsoft.Data.SqlClient6.1.4 NuGetpaket](https://www.nuget.org/packages/Microsoft.Data.SqlClient/6.1.4) und [StableReleasev6.1.4](https://github.com/dotnet/SqlClient/releases/tag/v6.1.4) | Gepinnte projektlokale Laufzeitabhängigkeit, Paket-/Lizenz-/Framework-/Releasevertrag für begrenzte native float32-Clientqualifikation | Dokumentierter Paket-/MIT-/Supportvertrag, kein eigener Assembly-/Typ-/TDS-/SQL-/Qualitätsnachweis; transitive Pakete/Audit und tatsächlichen Scope separat prüfen | 2026-10-13 | 2026-10-13 | ACTIVE | Paket-/Lizenz-/Dependency-/Audit-/API-/Supportänderung oder abweichende Evidenz |

## Binärwerte im gebundenen IDX-012-Recordvertrag

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-117` | PRIMARY | Microsoft (2026), [FOR JSON Datentypkonvertierung](https://learn.microsoft.com/en-us/sql/relational-databases/json/how-for-json-converts-sql-server-data-types-to-json-data-types-sql-server?view=sql-server-ver17) | Kanonische Base64-Darstellung von binary/varbinary im festen JSON-Record, vollständige UTF16LE-Marker-/Dateinamensbytes | Serializervertrag, kein eigener Request-/Herkunfts-/Native-/Cleanup-PASS; Originalrecord und konkrete Bytebindung getrennt prüfen | 2026-10-13 | 2026-10-13 | ACTIVE | Serializer-/Versions-/Captureformatänderung oder abweichende Evidenz |

## TSK-004 – begrenzte lokale Assembly-Ladediagnose

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-118` | PRIMARY | Microsoft (2026), [Default probing](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/default-probing) | Depsdateien werden in Host-Suchinformationen umgesetzt; Default-Kontext, Managed-, Ressourcen- und Native-Suche getrennt einordnen | Dokumentierter Suchalgorithmus, kein Befund zur eigenen FileNotFoundException und kein Loader-/SNI-/TDS-/SQL-PASS | 2026-10-13 | 2026-10-13 | ACTIVE | Host-/Runtime-/Deps- oder Probeverfahren geändert |
| `SRC-119` | PRIMARY | Microsoft (2026), [Managed assembly loading algorithm](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/loading-managed) | Benannte LoadFromAssemblyName-Probe und Typmetadaten getrennt von statischen Referenzen und deren variabler Ladezeit einordnen | Ein geänderter Probehost reproduziert keine verlorenen Fehlermetadaten des früheren SQL-Clients; keine Securityisolation durch den Load-Kontext behaupten | 2026-10-13 | 2026-10-13 | ACTIVE | AssemblyLoadContext-/Runtime-/Typ- oder Diagnoseverfahren geändert |


## TSK-004 – Sessionprojektion und strikte Readergetter

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-120` | PRIMARY | Microsoft (2026), [@@SPID](https://learn.microsoft.com/en-us/sql/t-sql/functions/spid-transact-sql?view=sql-server-ver17), [GetInt32](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getint32?view=sqlclient-dotnet-core-6.1), [GetString](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getstring?view=sqlclient-dotnet-core-6.1), [GetByte](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getbyte?view=sqlclient-dotnet-core-6.1), [GetDataTypeName](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getdatatypename?view=sqlclient-dotnet-core-6.1), [GetFieldType](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getfieldtype?view=sqlclient-dotnet-core-6.1), [DB_ID](https://learn.microsoft.com/en-us/sql/t-sql/functions/db-id-transact-sql?view=sql-server-ver17), [DB_NAME](https://learn.microsoft.com/en-us/sql/t-sql/functions/db-name-transact-sql?view=sql-server-ver17), [SERVERPROPERTY](https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver17), [CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17), [sys.dm_os_host_info](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-host-info-transact-sql?view=sql-server-ver17) und [sys.databases](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-ver17) | Acht Sessionprojektionen: @@SPID smallint, explizit CONVERT(int) für GetInt32; übrige int/nvarchar/tinyint-Felder und strikte Getter ohne Konversion | Dokumentierter Source-/Gettervertrag, keine tatsächliche Driver-/Server-Typmessung oder rückwirkender Beweis der alten UNKNOWN_OR_UNCLASSIFIED-Exception; SOURCE_ONLY, keine VECTOR-/Runtimeabnahme | 2026-10-13 | 2026-10-13 | ACTIVE | Projektions-/Getter-/API-/Serververtrag geändert oder neuer empirischer Befund |

## SqlClient-OPEN-Serialisierung und TLS-Anforderung

| ID | Klasse | Quelle | Verwendung | Grenzen | Abruf | Prüfung | Status | Aktualisierung |
|---|---|---|---|---|---|---|---|---|
| `SRC-121` | PRIMARY | Microsoft (ohne Datumsangabe), [SqlConnectionEncryptOption v6.1.4](https://github.com/dotnet/SqlClient/blob/v6.1.4/src/Microsoft.Data.SqlClient/src/Microsoft/Data/SqlClient/SqlConnectionEncryptOption.cs) und [API6.1](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqlconnectionencryptoption?view=sqlclient-dotnet-core-6.1) | Gepinnte OPEN-Serialisierung: Mandatory hält intern True/ToString liefert True; bool true wird Mandatory zugeordnet | Konfigurierte TLS-Anforderung und sourcegebundener Textvertrag, kein unabhängiger Wire-/TDS-/ausgehandelter TLS-Beleg; TrustServerCertificate ausschließlich eigene isolierte Lab-Ausnahme, keine globale Trust- oder Produktionsanleitung | 2026-10-13 | 2026-10-13 | ACTIVE | API-/Quellversion-/Serialisierungs-/TLS-Vertragsänderung oder abweichende Evidenz |

## DGN-004 – Detailverweise zum bestehenden Query-Store-Quellenumfang SRC-027

Datierte Ergänzung des bestehenden Eintrags `SRC-027`, keine neue Quellenkennung.
Seine historische Registerzeile und früheren Abnahmen bleiben erhalten.
Klasse `PRIMARY`, Status `ACTIVE`; **Aktualisiert und abgerufen: 2026-10-23**.
Aussagebezug: begrenzter DGN-004-Entwurf bei TSK-016 zu Planerzwingung,
Fehlergrund, Ersatzplanung und Rücknahme. Geltungsbereich: SQL Server 2019,
2022 und 2025; neuere Optionen und Rechte versionsabhängig prüfen.
Review-Trigger: geänderte Produktdokumentation, neue Version/Option/Rechte,
Präzisierung des Demo-Vertrags oder abweichendes späteres Laufzeitergebnis.

| Detailquelle innerhalb SRC-027 | Belegter Mechanismus und Grenze |
|---|---|
| [sys.query_store_plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17) | Force-Flag bezeichnet den Auftrag, nicht garantierte Planverwendung; Fehlerzähler wächst bei fehlgeschlagener Kompilierung und wird beim Wechsel von ungezwungen zu erzwungen zurückgesetzt; `8712/NO_INDEX` bezeichnet einen entfernten Index. Sichtrechte versionsabhängig. |
| [sp_query_store_force_plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver17) | Versuch bei Kompilierung, gleicher oder ähnlicher Plan, reguläre Optimierung bei Fehlschlag; Aufruferfolg ist kein Ausführungsbeleg. Neuere optionale Argumente nicht auf 2019 übertragen. |
| [sp_query_store_unforce_plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-unforce-plan-transact-sql?view=sql-server-ver17) | Ausdrückliche Rücknahme für Query-/Plan-Paar und erforderliche ALTER-Berechtigung auf der Datenbank; keine automatische Garantie für sämtliche sonstigen Rücknahmen. |
| [sys.query_store_runtime_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17) | Mehrere Zeilen je aktivem Intervall möglich; nach Plan, Ausführungstyp und Intervall aggregieren. Reguläre, abgebrochene und fehlerhafte Ausführungen unterscheiden. |
| [sys.query_store_query](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) | Query-/Modul-/Text-/Kontextzuordnung; Query-Hash allein ist keine eindeutige Identität. |
| [Optimized plan forcing with Query Store](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17) | Optimierte Planerzwingung ab 2022 als eigener Einflussfaktor; Verhalten und passende versionsgebundene Begrenzung für den klassischen Schnitt vor Umsetzung klären. |
| [sp_recompile](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-recompile-transact-sql?view=sql-server-ver17) | Gezielt ein eigenes Modul zur Neukompilierung bei der nächsten Ausführung markieren; ALTER-Recht am Objekt. Kein Ersatz für tatsächliche Ausführung oder globale Cacheleerung. |

Diese Quellen belegen Produktmechanismen (`DOCUMENTED`). Die konkrete Wahl
zweier Pläne, ihre verlässliche Zuordnung und die Reproduktion von NO_INDEX
im entworfenen kleinen Workload sind noch nicht qualifiziert. Ablauf und
Schutzgrenzen sind `METHOD`/`INFERENCE` (Methodik beziehungsweise Herleitung),
keine gemessenen Produktgarantien. Vor späterer Umsetzung gelten die offenen
lesenden Detailgates im [kanonischen Plan](../../.ai/identity/registry.json)
und seiner [abgeleiteten Ansicht](../../.ai/BACKLOG.md#begrenzter-planungsschnitt-planerzwingung).
Tatsächliche Planbelege folgen zusätzlich dem bestehenden FWK-005-Vertrag;
gespeicherte Query-Store-Pläne oder das Force-Flag allein reichen nicht.

### DGN-004: lesende Vertiefung und Quellenkonflikte vom 24. Oktober 2026

Diese Ergänzung präzisiert den vorigen DGN-004-Abschnitt. Bestehende
Quellenkennungen und historische Registerzeilen bleiben erhalten.
**Aktualisiert und abgerufen: 2026-10-24.** Alle folgenden Detailverweise
sind `PRIMARY`. Geltungsbereich: der begrenzte Plan für SQL Server
2019/150, 2022/160 und 2025/170; Zahlen nach dem Schrägstrich bezeichnen
den Compatibility Level (Datenbank-Kompatibilitätsstufe).
Review-Trigger: geänderte Herstellerdokumentation, neuer Build/Client,
geänderter Ergebnisvertrag oder abweichender späterer Laufbefund.

| Bestehender Quellenumfang | Detailverweis | Aussagebezug und Status |
|---|---|---|
| `SRC-001` | [Query processing architecture guide](https://learn.microsoft.com/en-us/sql/relational-databases/query-processing-architecture-guide?view=sql-server-ver17#forced-parameterization) | `ACTIVE`: datenbankweite erzwungene Parametrisierung nimmt Prozedurinhalte aus; keine Garantie für jede konkrete Engine-Darstellung oder zwei unterschiedliche Pläne. |
| `SRC-027` | [Query-Store-Best-Practices](https://learn.microsoft.com/en-us/sql/relational-databases/performance/best-practice-with-the-query-store?view=sql-server-ver17#avoid-a-drop-and-create-pattern-for-containing-objects), [Query-Zuordnung](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17), [Kontext](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-context-settings-transact-sql?view=sql-server-ver17) | `ACTIVE`: Modul, Text und Kontext zusammenhalten; DROP/CREATE erzeugt neue Zuordnung. Hash allein ist keine eindeutige Identität. Sichtrechte ab 2022 gesondert berücksichtigen. |
| `SRC-031` | [SET STATISTICS XML](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-statistics-xml-transact-sql?view=sql-server-ver17) | `ACTIVE`: tatsächliche Ausführungsinformationen, ausgegebene Ergebnisse und SHOWPLAN-Rechte; keine Garantie eines vollständigen Clienttransports. XML bedeutet Extensible Markup Language, strukturiertes Textformat. |
| `SRC-031` | [Showplan-Schema 2019](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2019/showplanxml.xsd), [Showplan-Schema 2022](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd) | `ACTIVE` nur im beschriebenen RTM-Umfang (Erstveröffentlichungsstand): UsePlan, QueryHash und QueryPlanHash sind optionale Attribute. Attributexistenz ist keine universelle Query-Store-Erzwingungsgarantie und kein vollständiger 2025-Schemavertrag. |
| `SRC-031` | [sqlcmd-Ausgabeoptionen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#-y-variable_length_type_display_width) | `ACTIVE` für den Plan-Erfassungspfad: Großtext/XML standardmäßig auf 256 Zeichen begrenzt; -w ändert Zeilenbreite; -W nicht mit -y/-Y kombinierbar. Konkrete Clientversion und begrenzte vollständige Übertragung später prüfen. |

Innerhalb `SRC-027` erhalten die **strittigen Detailaussagen** den Status
`REVIEW_REQUIRED` (erneute Quellenprüfung erforderlich):

- Die [Katalogbeschreibung](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17)
  ordnet bei `is_optimized_plan_forcing_disabled` den Wert 0 der Deaktivierung zu;
  [Beispiel D der Optimierungsbeschreibung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16#d-select-all-queries-where-optimized-plan-forcing-is-disabled-by-query-store)
  verwendet dafür 1. Die Semantik wird nicht stillschweigend aus dem Namen abgeleitet.
- Die [Force-Prozedurreferenz](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver16)
  führt `disable_optimized_plan_forcing` an dritter Stelle und danach
  `replica_group_id`; [Beispiel C](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16#c-force-a-plan-and-disable-optimized-plan-forcing-in-query-store)
  fordert `replica_group_id` an dritter Stelle und beschreibt es als zusätzlich
  erforderlich. Eine einheitliche buildübergreifende Aufrufvorlage ist daraus
  nicht belastbar abgeleitet.

Diese Konfliktmarkierung betrifft die genannten Aufruf-/Flagdetails.
Die übrigen bereits belegten Eigenschaften des Query Store, der möglichen
gleichen/ähnlichen Planverwendung, des Kompilierungsfehlerzählers und des
Fehlergrunds `8712/NO_INDEX` bleiben davon getrennt. Die verantwortliche
spätere Umsetzungsrolle muss vor mutationsfähiger Freigabe belastbare
buildbezogene Evidenz zur Signatur und Interpretation ergänzen.

Der [kanonische DGN-004-Eintrag](../../.ai/identity/registry.json) dokumentiert
zusätzlich die rein statischen Aufruf-/Proxybefunde am Schulungsstand
`c9c75cefb30fc82aec33f67d9589670a877dd76b`. Der begrenzte Erfassungsentwurf ist
`METHOD`/`INFERENCE` (Methodik beziehungsweise Herleitung), kein ausgeführter
Trunkierungsnachweis. Tatsächliche zwei Planvarianten, Erzwingung, NO_INDEX,
Ersatzplanung und Rücknahme sind weiter empirisch offen. Der [präzisierte Plan](../../.ai/BACKLOG.md#begrenzter-planungsschnitt-planerzwingung)
enthält die verbleibenden Gates; dieser Quellenstand autorisiert keine SQL-Läufe.

### DGN-004: engerer Erfassungsentwurf und Systemreferenzen vom 24. Oktober 2026

Historischer Quellenstand vor der begrenzten Versionsdiagnose. Die Anzeigeherleitung mit `-y 32768` ist durch die nachfolgend dokumentierten Clientbefunde überholt; der ursprüngliche Befund bleibt nachvollziehbar.

Datierte Ergänzung der bestehenden Quellenumfänge `SRC-031` (tatsächliche
Planerfassung) und `SRC-027` (Query Store; persistente Abfrage- und Planhistorie).
Keine neue Quellenkennung; historische Registerzeilen und frühere Befunde
bleiben erhalten. **Aktualisiert und abgerufen: 2026-10-24.** Klasse `PRIMARY`.
Review-Trigger: geänderte Herstellerangaben, Paket-/Clientversion, Ergebnisvertrag
oder neuer tatsächlicher Buildbefund.

| Quellenumfang und Detailquelle | Aussagebezug und Grenze | Status |
|---|---|---|
| `SRC-031`: [sqlcmd-Ausgabeoptionen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#format-options) | Positive feste Anzeigegrenze, maximale Zeilenbreite, Unverträglichkeit von -W mit -y/-Y und Einfluss von -k. Der engere Entwurf mit -y 32768/-w 65535 und Planumfang unter 32.768 UTF-8-Bytes ist METHOD/INFERENCE (Methodik beziehungsweise Herleitung); kein gemessenes Clientverhalten. | `ACTIVE` für dokumentierte Optionen; tatsächliche Erfassung unqualifiziert |
| `SRC-027`: [Microsoft-Systemreferenzen](https://learn.microsoft.com/en-us/sql/tools/sql-database-projects/concepts/package-references?view=sql-server-ver17#system-databases), [2022 / 160.2.8](https://www.nuget.org/packages/Microsoft.SqlServer.Dacpacs.Master/160.2.8), [2025 / 170.0.4](https://www.nuget.org/packages/Microsoft.SqlServer.Dacpacs.Master/170.0.4) | Microsoft.SqlServer.Dacpacs.Master, tools/master.dacpac/model.xml: Force-/Unforce-Prozeduren als SqlExtendedProcedure ohne Parameterliste; Statusspalte nur als SqlComputedColumn ohne Bedeutungsdefinition. DACPAC (Data-tier Application Package) ist ein Datenbankschema-Referenzpaket. Kein Nachweis der Aufrufsignatur, Flaginterpretation oder eines laufenden Zielbuilds. | `ACTIVE` als Schemaquelle; strittige Detailaussagen weiter `REVIEW_REQUIRED` |
| `SRC-027`: [historischer Optimierungsstand](https://github.com/MicrosoftDocs/sql-docs/blob/3a69fbed7e840752b5a704d639931f5f82af3960/docs/relational-databases/performance/optimized-plan-forcing-query-store.md#c-force-a-plan-and-disable-optimized-plan-forcing-in-query-store), [historische Prozedurreferenz](https://github.com/MicrosoftDocs/sql-docs/blob/9385fea21808cf682650481315f6f4bde7c59d8e/docs/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql.md#syntax) | Zusätzlich gelesene historische Dokumentstände lösen den bekannten Argument-/Flagkonflikt nicht auf; keine belastbare gemeinsame ältere Aufrufvorlage daraus ableiten. | `REVIEW_REQUIRED` für die strittigen Vertragsdetails |

Die Systemreferenzen wurden ausschließlich im Arbeitsspeicher als ZIP-/XML-
Quellen gelesen; keine Installation oder Ausführung. Die gepinnten Paketquellen
und SHA-256-Prüfsummen (Prüfwerte der Quellenbytes) stehen im vorhandenen
[kanonischen TSK-016-Eintrag](../../.ai/identity/registry.json) unter
`gate_review_result.reference_packages`. Fehlende Parameterdefinitionen im
Referenzmodell belegen keine fehlenden Argumente am tatsächlichen Server.

Der engere Erfassungsentwurf ersetzt für den ersten Schnitt die frühere
256-KiB-Planobergrenze durch höchstens 32.767 UTF-8-Bytes; KiB bedeutet Kibibyte,
UTF-8 ist eine Unicode-Zeichenkodierung. Die Anzeige-/Bytebeziehung ist eine
Herleitung; Adapter und Laufzeitnachweis bleiben offen. Das Versionsgate bleibt
ebenfalls offen: vor Freigabe benötigt die spätere Umsetzungsrolle eine
eindeutige Herstellerklärung oder einen ausdrücklich autorisierten gezielten
2022-/2025-Buildnachweis zu Aufrufform, tatsächlich deaktivierter optimierter
Planerzwingung am eigenen Plan und Statusinterpretation. Diese Ergänzung
autorisiert keine Probe. Der [engere Entwurf](../../.ai/BACKLOG.md#engerer-erfassungsentwurf-und-offenes-versionsgate)
enthält Grenzen und spätere Abnahme; Umsetzung und weitere autonome Arbeit
bleiben pausiert.

### DGN-004: begrenzte Versionsdiagnose vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage- und Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Die zuvor
ausdrücklich erlaubten privaten Läufe wurden gegen Repository-Basis
`2a111cda7bfcbf3218aaf0153678dbd64d3bbd40` ausgeführt. Jetzt werden ausschließlich
die vorhandenen Befunde dokumentiert; keine weiteren SQL-/Lab-Läufe.
Klassen: `EMPIRISCH` für die benannten Builds, `PRIMARY` für Herstellerangaben.

| Befundquelle | Beobachtung und Grenze |
|---|---|
| SQL Server 2022 `16.0.4265.3`, Developer/Linux, Compatibility Level 160 | Standardaufruf erfolgreich. Danach wechselte QueryHash (Abfragehash) bei gleichem vollständigem Text, Modul, Statement-SQL-Handle und Kontext auf den unveränderten QueryPlanHash (Planhash). Diagnoseinvariante verletzt; erweiterte Signatur und Anforderungsflag nicht geprüft. Keine diagnostizierte Produktursache. |
| SQL Server 2025 `17.0.4075.5`, Enterprise Developer/Linux, Compatibility Level 170 | Vierargumentform mit replica_group_id = 1 an dritter und disable_optimized_plan_forcing = 0/1 an vierter Stelle erfolgreich; Anforderungsflag entsprechend 0/1. Dritter benannter Parameter mit Wert 1 ließ anfänglich Flag 0 bestehen; Wert 0 an dritter Stelle führte zu Rollenfehler 12463. Zehn Fälle: sieben zugeordnete tatsächliche Ausführungen, drei Rollenfehler, zehn Rücknahmeprüfungen. Keine tatsächliche Replay-Abschaltung nachgewiesen. |
| Private Abfrageformen und Planbelege | Kein gespeicherter Optimierungs-Replay (wiederverwendbare Kompilierungsschritte), has_compile_replay_script = 0; fehlendes optionales QueryCompilationReplay ist kein Deaktivierungsbeweis. 24 × 32 und 32 × 24 Zeilen mit nicht eindeutigen Indizes ergänzten die früheren 8-/12-Tabellenformen; keine Form schuf eine positive Replay-Ausgangslage. |
| Client-/Erfassungsbefunde | Der 2022-Client lehnte -y 65534 ab und meldete einen Wertebereich bis 8000; daraus folgt die Unverwendbarkeit des früheren -y-32768-Entwurfs auf diesem Client, ohne diesen Wert separat auszuführen. 2025 lehnte -h zusammen mit -y 0 ab. Direkte XML-Ausgabe wurde bei 65.535 Zeichen innerhalb eines Tokens umgebrochen und strikt abgelehnt. Vollständige private Stückübertragung gelang; kein qualifizierter Demo-Adapter. |

Die aktuellen Herstellerquellen wurden am 24. Oktober 2026 gelesen:

- [Optimierte Planerzwingung, Beispiele C/D](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17): Replikatkennung vor Deaktivierungsparameter, Flag 1 im Deaktivierungsbeispiel. Der lokale 2025-Befund passt zur Anforderungszuordnung, beweist wegen fehlender Replay-Ausgangslage keine tatsächliche Abschaltung.
- [Force-Prozedurreferenz](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver17): abweichende veröffentlichte Parameterreihenfolge; nicht unverändert als gemeinsame 2022-/2025-Vorlage übernehmen.
- [Query-Store-Planmetadaten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17): abweichende veröffentlichte 0/1-Beschreibung. Der begrenzte Anforderungsbefund löst diesen Konflikt nicht pauschal für alle Builds oder tatsächliche Replay-Nutzung auf.
- [Letzter tatsächlicher Plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17): Systemfunktion, Cachebindung, datenbankbezogene Aktivierung und mögliche reduzierte/fehlende Laufzeitinformation. Privat wurden vollständiger Statementbezug und echte Laufzeitzähler zusätzlich verlangt.
- [sqlcmd-Ausgabeoptionen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#format-options): Clientformat und Bytegrenzen getrennt prüfen. Ein größerer privater Plan oder erfolgreicher Stücktransport erweitert den späteren Demo-Vertrag nicht.

Der [kanonische TSK-016-Eintrag](../../.ai/identity/registry.json) bindet unter
`version_probe_result` Build, Falltabelle, Erfassungsmethode, Rücknahme, private
Berichts-/Quellenprüfsummen und offene Gates. Die [menschliche Befundansicht](../../.ai/BACKLOG.md#begrenzte-versionsdiagnose-und-verbleibende-gates)
erklärt die Diagnosebezeichner und den korrigierten Plan. Rohlogs, vollständige
Pläne und Diagnoseskripte bleiben unversioniert; Prüfsummen ersetzen keine
reproduzierbare Demo-Quelle oder unabhängige Laufzeitabnahme.

Erfassungsentscheidung, 2022-Hashbindung/Signatur und tatsächliche Deaktivierung
auf beiden Builds bleiben offen. Der [aktuelle Auftrag](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
erlaubt nur statische Integration dieser Befunde. Kein VALIDATED-Status,
keine weiteren Läufe, Demo-Umsetzung oder Wiederaufnahme übriger Arbeit.

### DGN-004: Hashzuordnung und Replay-Referenz vom 24. Oktober 2026

Ergänzung der bestehenden Umfänge `SRC-027` (Query Store; persistente Abfrage-/
Planhistorie) und `SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung.
Basis der lesenden Sichtung: `a87d1d7e68679238b766fb31a399b46825f14efd`.
Vorhandene private Plan-Dateien und öffentliche Originalquellen wurden gelesen;
keine Tests, SQL-/Lab- oder CI-Läufe während der Sichtung. Die jetzt erlaubten
statischen Veröffentlichungsprüfungen sind davon getrennt.

| Primärquelle und Klasse | Befund und Grenze |
|---|---|
| [Originalreproduktion mit USE PLAN](https://www.sql.kiwi/2024/11/forced-plans-query-hash/), veröffentlicht 2024-11-28; eigene experimentelle Primärquelle | QueryHash (Abfragehash) wird im reproduzierten Forcing-Fall durch QueryPlanHash (Planhash) überschrieben. Historischer Umfang bis einschließlich 2022 CU16; CU bedeutet Cumulative Update, kumulatives Produktupdate. Keine Hersteller-Fixbestätigung für unseren späteren Build. |
| [Originalreproduktion über Query Store](https://kendralittle.com/2024/11/24/query-hash-values-meaningless-same-as-query-plan-hash-sql-server/), veröffentlicht 2024-11-24; eigene experimentelle Primärquelle | Hashüberschreibung im Plan und später auch geänderter query_hash im Query-Store-Katalog. Das bloße Ausweichen auf den Kataloghash ist keine robuste Zuordnung. Eine entsprechende lokale Katalogänderung wurde nicht erfasst. |
| [Microsoft-Replay-Abfrage](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/bigjoin.sql), [Anleitung](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/readme.md); Hersteller-Referenzquelle | Zwei UNION-ALL-Zweige mit je zehn WideWorldImporters-Tabellen und neun Joins, Detailtupel und ORDER BY. Die Anleitung beschreibt has_compile_replay_script = 1, also gespeicherte wiederverwendbare Kompilierungsschritte. Referenz für 2022, keine Projektmessung oder Zusage für verkleinerte synthetische Daten und 2025. |
| [Replay-Eignung und Speicherung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16), [Optimierer-Suchlimit](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/troubleshoot-optimizer-timeout-performance); Herstellergrundlagen | Optimierungsaufwand und Nutzen gegenüber Replay-Speicherkosten bestimmen die Eignung; Joinzahl oder FULL-Optimierung allein garantieren sie nicht. TimeOut im Plan bezeichnet ein internes Aufgaben-/Suchlimit und beweist keinen Clienttimeout. |

Die lokale Leseauswertung bestätigt den Hashwechsel bereits in den Rohplänen von
SQL Server 2022/16.0.4265.3. Vollständiger Text, Statement-SQL-Handle, eigene
Prozedur, Kontext, Sitzungsoptionen, Operatorfolge, Objektdeskriptoren und
Prädikat-XML bleiben gleich; der Vergleich auf 2025/17.0.4075.5 lässt auch die
Hashwerte gleich. Das passt zum veröffentlichten Fehlerbild, ist aber kein
vollständiger semantischer Planäquivalenzbeweis oder Hersteller-Fixnachweis.
Die private Hashinvariante wurde nicht nachträglich als bestanden ausgegeben.

Der kanonische Datensatz bindet den Microsoft-Commit und die Git-Blob-Prüfwerte
von Abfrage und Anleitung. Ausgeschlossen bleiben die Cacheleerung in bigjoin.sql,
[feste Datenbankwiederherstellung und Historienleerung](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/restorewwi.sql),
[bloßer Zweiparameter-Force-Aufruf](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/forceplan.sql)
und [ungefilterte Plansicht](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/find_query_in_query_store.sql).
Weder allgemeine Lab-Infrastruktur noch diese Steuerteile werden übernommen.

Die [kanonische Sichtung bei TSK-016](../../.ai/identity/registry.json) unter
`hash_replay_review_result` enthält die lokalen Planprüfsummen, Originalquellen,
Referenzform und Grenzen. Die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#lesende-hashanalyse-und-replay-referenz)
führt dieselben Inhalte lesbar zusammen; frühere Versionsbefunde bleiben erhalten.
Offen bleiben unabhängiger kombinierter Zuordnungsreview, erweiterte 2022-Signatur,
Replay-Speicherung und tatsächliche Nutzung vor dem Deaktivierungsvergleich auf
beiden Builds sowie Erfassungsentscheidung und Demo-Freigaben. Kein weiterer
Lauf oder Umsetzungsauftrag folgt daraus. Der [aktuelle Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
bindet statische Integration und fortbestehende Pause.

### DGN-004: Plan für kombinierte Zuordnung und begrenzte Replay-Probe vom 24. Oktober 2026

Ergänzung von `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`c238ba5c6e4b00782fd9fbc37d7c87333880823c`; Klasse `METHODE/INFERENZ` für den neuen
Probenentwurf, keine neue Ausführung oder technische Qualifikation. Der bestehende
[Microsoft-Referenzablauf](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/bigjoin.sql)
motiviert UNION-ALL-Joinzweige und Sortierung; die synthetischen 529 Datenzeilen,
Formen A/B und 768 Ergebnistupel sind eigener unimplementierter Plan.

- [Replay-Eignung und Speicherung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16): gespeicherte Kompilierungsschritte, volle Optimierung und Nutzenprüfung. Joinzahl oder Katalogflag allein belegen keine tatsächliche Nutzung. Kein garantierter Eignungs- oder Leistungswert wird daraus abgeleitet.
- [Letzter tatsächlicher Plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17): Cache-/Modulbindung und mögliche reduzierte/fehlende Ausgabe. Der Entwurf verlangt zusätzlich vollständigen Statement-/Kontext-/Struktur-/Tupelbezug und Ausführungszuwachs; alte oder Root-only-Pläne reichen nicht.
- [Offizielles 2022-Showplan-XSD](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd): QueryCompilationReplay ist als optionales xsd:int deklariert. XSD bedeutet XML Schema Definition, Schemadefinition des strukturierten Planformats; der Typ enthält keine belastbare Definition der Rohwertbedeutung. Daher wird insbesondere kein pauschaler Wert 1 als fertiger Nutzungsbeweis festgelegt.

Das Methoden-Gate für positive Replay-Nutzung und Gegenkennzeichnung bleibt offen
und ist vor Umsetzung unabhängig für die Zielbuilds zu klären. Erst danach kann
eine später ausdrücklich autorisierte Ein–Aus–Ein-Folge einen Deaktivierungsnachweis
anstreben. Katalogflag, Compilezeit oder fehlendes optionales Merkmal allein genügen
nicht. Unbekannte Werte oder fehlende positive Beobachtbarkeit werden nicht durch
alternative Telemetrie, Zusatzaufrufe oder gelockerte Nachweisregeln ersetzt.

Die [kanonische Planung bei TSK-016](../../.ai/identity/registry.json) unter
`mapping_replay_probe_plan` und die [abgeleitete Planansicht](../../.ai/BACKLOG.md#kombinierte-planzuordnung-und-begrenzte-synthetische-replay-probe)
binden Daten-/Tupelformeln, kombinierte Zuordnung, zwei Kandidaten, Zählerepochen,
harte Budgets, spätere Gegenfälle und Cleanup. Vorhandene private Planbelege und
frühere Originalquellen bleiben unverändert. Aktuell nur Planung und statische
Integration, keine Umsetzung, Tests der Probe oder SQL-/Lab-Läufe; weitere
Ausführung benötigt einen neuen ausdrücklichen Auftrag. Der
[aktuelle Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md) hält die
übrige Verarbeitung pausiert.

### DGN-004: Quellenreview zum tatsächlichen Replay-Nutzungsnachweis vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`5ac459b83688a366a03396292faf41441f18f315`; ausschließlich lesender Quellenreview,
Abruf am 2026-10-24. Keine neuen Tests, SQL-/Lab-Läufe oder Messwerte. Der
[kanonische Befund bei TSK-016](../../.ai/identity/registry.json) steht unter
`replay_usage_source_review_result`; die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#lesender-quellenreview-zum-tatsächlichen-replay-nutzungsnachweis)
führt alle Aussagen, Grenzen und offenen Gates.

| Quelle | Beleg und Grenze |
|---|---|
| [Microsoft-Katalogvertrag](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17) | DOKUMENTIERT: has_compile_replay_script = 1 bedeutet gespeichert; is_forced_plan markiert eine Anforderung ohne Garantie exakter Planverwendung. Fehler 8675 / OPTIMIZATION_REPLAY_FAILED bedeutet gescheiterte Skriptausführung. INFERENZ: fehlender Fehler allein beweist keinen erfolgreichen Replay. |
| [Microsoft-Designbeschreibung von 2022](https://www.microsoft.com/en-us/sql-server/blog/2022/09/15/intelligent-query-processing-feature-family-additions/) | DOKUMENTIERT: Capture und spätere Replay-Kompilierung sind getrennte Phasen. Ein bereits zwischengespeicherter Plan erfordert keine neue Replay-Kompilierung. Kein konkreter Marker-/Gegenvertrag für unsere beiden Zielbuilds. |
| [Hersteller-XSD 2022](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd) und [Schemaindex](https://schemas.microsoft.com/sqlserver/2004/07/showplan/) | Im Speicher gelesenes XSD (XML Schema Definition; Schemadefinition des Planformats): QueryCompilationReplay ist optionales xsd:int ohne Zustandsbedeutungen; ein erforderliches Script-Textattribut definiert ebenfalls keinen aktuellen Nutzungsnachweis. Der öffentliche Index führt zuletzt 2022 RTM (Release to Manufacturing; ursprünglicher Veröffentlichungsstand), keinen gesonderten 2025-Wertevertrag. Keine Aussage gegen Replay-Unterstützung in 2025. |
| [SQLServerFast-Originalreferenz](https://sqlserverfast.com/epr/plan-properties/) | Eigene Fachreferenz, keine Herstellerzusage: beschreibt QueryCompilationReplay = 1 als Nutzung; Eigenschaft laut Änderungsverlauf am 2025-07-06 ergänzt. Reproduzierbarer Nachweis für die exakten Zielbuilds, vorgesehenen Erfassungsweg und Gegenkennzeichnung fehlt dort. Wert 1 bleibt Kandidat, kein freigegebenes Erfolgskriterium. |
| [Microsoft-Vertrag des letzten tatsächlichen Plans](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17) | DOKUMENTIERT: Cache-Kompilierungsdaten plus letzte bekannte Laufzeitinformationen. METHODE/INFERENZ: Kompilierungsmarker separat zur frischen eigenen Kompilierung und aktuellen Ausführung binden; Cachetreffer, Root-only- oder alte Pläne genügen nicht. |
| [Gepinnte Microsoft-Referenzanleitung](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/readme.md) | Kandidateneignung über Speicherflag und Vergleich von Kompilierungszeiten; kein direkter Werte-/Gegenvertrag für die kleine synthetische Probe oder 2025. Kein Quellablauf ausgeführt und keine Leistungswerte als eigene Messung übernommen. |

Ergebnis: Die Quellenprüfung ist abgeschlossen; das Freigabegate bleibt für
SQL Server 2022/16.0.4265.3 (Developer/Linux, Compatibility Level 160) und
SQL Server 2025/17.0.4075.5 (Enterprise Developer/Linux, Compatibility Level 170)
offen. Positive Markerbedeutung, Gegenkennzeichnung und Erfassung/Korrelation
buildbezogen quellenbelegt unabhängig klären. Fehlendes optionales Attribut,
Forcing-/Deaktivierungsflag, UsePlan, FULL, kein Fehler oder kürzere Compilezeit
sind jeweils allein unzureichend. Eine Ein–Aus–Ein-Folge darf ohne diesen
vorab geklärten Vertrag keinen Nutzungs- oder Deaktivierungsnachweis behaupten.

Der [bestehende Probenplan](../../.ai/BACKLOG.md#kombinierte-planzuordnung-und-begrenzte-synthetische-replay-probe)
und alle historischen Befunde bleiben unverändert. Keine automatische Erweiterung
oder Ersatztelemetrie. Umsetzung und Läufe benötigen nach Methodenfreigabe einen
neuen ausdrücklichen Auftrag; der [aktuelle Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
hält die übrige Verarbeitung pausiert. Statische Dokumentationsintegration
belegt keine technische Versions- oder Demoabnahme.

### DGN-004: QueryCompilationReplay und Gegenkennzeichnung vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`c8069016aa00a6804ed608f22447e5c2a9a18251`; ergänzender lesender Quellenreview,
Abruf am 2026-10-24. Keine neue Umsetzung, Tests der Probe, SQL-/Lab-Läufe oder
Messung. Der [kanonische Befund bei TSK-016](../../.ai/identity/registry.json) steht
unter `query_compilation_replay_counter_review_result`; die
[abgeleitete Befundansicht](../../.ai/BACKLOG.md#querycompilationreplay-und-gegenkennzeichnung--ergänzender-quellenreview)
führt Markergrenzen, Kontrollwege und offene Gates vollständig.

DOKUMENTIERT am gemeinsamen MicrosoftDocs-Quellencommit
`b6fe4934643919b28ddea54ad04c66ff1b2a82d1`:

- [Katalogtabelle, Zeilen 55–57](https://github.com/MicrosoftDocs/sql-docs/blob/b6fe4934643919b28ddea54ad04c66ff1b2a82d1/docs/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql.md#L55-L57), Git-Blob `a7fc21cff62f67111f293cfa71de5af885e6524b`: nennt is_optimized_plan_forcing_disabled = 0 deaktiviert, 1 nicht deaktiviert.
- [Funktionsbeschreibung, Beispiele C/D ab Zeile 118](https://github.com/MicrosoftDocs/sql-docs/blob/b6fe4934643919b28ddea54ad04c66ff1b2a82d1/docs/relational-databases/performance/optimized-plan-forcing-query-store.md#L118-L156), Git-Blob `027099d57a33a44ce88df09af35f4c447a34a215`: zeigt Replikatkennung 1 an dritter und Deaktivierungsanforderung 1 an vierter Stelle; Beispiel D filtert Flag 1 als deaktiviert. Direkter Quellenwiderspruch zur Katalogtabelle. Keine bestätigte Herstellerkorrektur oder neue Produktfehlerdiagnose.

Das [Hersteller-Schema](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd)
definiert QueryCompilationReplay weiterhin nur als optionale Ganzzahl. Die
[originale Fachreferenz](https://sqlserverfast.com/epr/plan-properties/) nennt Wert 1
als Nutzung; ein verifizierter Werte-/Gegenvertrag für beide Zielbuilds fehlt.
0, Abwesenheit oder andere ungeklärte Werte sind kein belastbarer Aus-Zustand.

METHODE/INFERENZ: Eine [dokumentierte Abschaltanforderung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17#c-force-a-plan-and-disable-optimized-plan-forcing-in-query-store)
mit anschließender frischer eigener Kompilierung bleibt ein Kontrollweg, kein
alleiniger beobachteter Gegenmarker. Der [dokumentierte Abfragehinweis](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17#disable_optimized_plan_forcing)
DISABLE_OPTIMIZED_PLAN_FORCING wäre eine gesonderte Negativkontrolle. Sein Einfügen
oder Entfernen ändert aber den Text und möglicherweise die Query-Store-Identität;
der unveränderte Ein–Aus–Ein-Probenplan erlaubt keinen automatischen Ersatz damit.

Für 2022/16.0.4265.3 (Developer/Linux, Compatibility Level 160) und
2025/17.0.4075.5 (Enterprise Developer/Linux, Compatibility Level 170) bleiben
positive Markersemantik, beobachtete Gegenkennzeichnung und Korrelation zur
frischen Kompilierung sowie aktuellen vollständigen Ausführung unabhängig zu
klären. Vorige Quellen-/Versionsbefunde und der Probenplan bleiben erhalten;
keine nachträgliche Laufzeitabnahme. Die [Auftragsgrenzen und Pause](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
gelten weiter. Neue Methoden-/Umsetzungs-/Laufarbeit benötigt gesonderte Freigabe.

### DGN-004: Plan einer gesonderten Hint-Negativkontrolle vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`1027441fb5e799e903f02782591d2d4ca4acba13`; Abruf 2026-10-24.
Der [kanonische Entwurf bei TSK-016](../../.ai/identity/registry.json) steht unter
`hint_negative_control_plan`; die [abgeleitete Detailansicht](../../.ai/BACKLOG.md#gesonderte-hint-negativkontrolle-mit-getrennten-abfrageidentitäten)
enthält Identitäten, vollständige Abfolge, Grenzen und spätere Abnahme.

- DOKUMENTIERT: [DISABLE_OPTIMIZED_PLAN_FORCING und Hint-Scope](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17#disable_optimized_plan_forcing) ab SQL Server 2022; bei UNION gilt die OPTION-Klausel am gesamten Statement. [Herstellerbeispiel E](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17#e-disable-optimized-plan-forcing-for-a-query) verwendet USE HINT. Keine Aussage über ein beobachtetes QueryCompilationReplay-Aus-Merkmal unserer Builds.
- DOKUMENTIERT: [Query-Store-Abfragekatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) führt query_id, object_id und Kontext; query_hash basiert auf der gebundenen logischen Form und schließt Query Hints aus. METHODE: R/H deshalb über getrennte Module, vollständige Texte/Kontexte und eigene Planrollen binden; Hashgleichheit erlaubt keine Zusammenführung.
- DOKUMENTIERT: [Query-Store-Hintkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-hints-transact-sql?view=sql-server-ver17) ordnet externe Hintdefinitionen query_id und Replikatscope zu. METHODE: fremde/unerwartete Hintsteuerung für R/H erkennen und abbrechen; Inline-Hint nicht als dort vorhandene Hintzeile ausgeben oder fremde Regeln löschen.
- DOKUMENTIERT: [Standard-Planerzwingung](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver17) bindet query_id und plan_id. METHODE: eigener Standardaufruf je Identität, kein dritter/vierter Parameter; erfolgreiche tatsächliche klassische Erzwingung unabhängig von bloßer Anforderung prüfen. Der erweiterte 2022-Signaturkonflikt des alten Plans bleibt gesondert offen.

METHODE: Referenz R ohne Hint und Kontrolle H mit dauerhaftem terminalem Inline-Hint
in zwei eigenen Modulen auf derselben synthetischen Form A führen. 529 Datenzeilen,
768 vollständige Ergebnistupel, höchstens neun Nutzaufrufe je Version: fünf R und
vier H. Keine Textänderung in einem Modul, kein Querforcing, kein Ersatzkandidat.
Der Vergleich besitzt zwei positive R-Phasen um zwei H-Gegenphasen; er beweist
keine reversible Abschaltung derselben query_id und ersetzt PR319 nicht.

Der dokumentierte Hint und erfolgreiche aktuelle klassische Erzwingung tragen
höchstens einen quellenbasierten Kontrollvertrag. CONTROL_ONLY bedeutet nur
Kontrollzustand belegt; daraus folgt keine empirische Replay-Abschaltung.
Vor Umsetzung müssen positive R-Marker und H-Gegenvertrag für die exakten Builds
2022/16.0.4265.3 und 2025/17.0.4075.5 unabhängig geklärt sein; alte Quellenkonflikte
und ungeklärte Rohwerte bleiben erhalten. Keine neue Laufzeit-/Versionsabnahme.

Planungsgrenzen: zwei eigene Container insgesamt, 900 Sekunden gemeinsame
reguläre Zeit plus je 60 Sekunden Cleanup; keine automatische Budgetaddition
mit dem alten Plan. Nur statische Dokumentationsintegration, keine Umsetzung,
Tests der Probe oder SQL-/Lab-Läufe. Der [aktuelle Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
bindet die fortbestehende Pause und den Bedarf eines neuen ausdrücklichen Auftrags
für spätere Umsetzung und Läufe nach Methodenfreigabe.

### DGN-004: Prüfbefunde und präzisierter Kompilierungsnachweis vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`5dc12013065d2a571354f091c19f586f2208961f`; Abruf/lesender Review 2026-10-24.
Der [kanonische Review bei TSK-016](../../.ai/identity/registry.json) steht unter
`hint_negative_control_review_result`, die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#prüfbefunde-zur-gesonderten-hint-negativkontrolle)
führt Ergebnis und Grenzen. Der aktive Hint-Plan wird dokumentarisch präzisiert;
kein Test, SQL-/Lab-Lauf oder neue Runtime-/Versionsabnahme wird daraus behauptet.

- DOKUMENTIERT: [Query-Katalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) und [Plan-Katalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17) führen beide count_compiles auf unterschiedlichem Scope. METHODE: für den aktuellen Nutzaufruf genau sys.query_store_query.count_compiles je fester eigener query_id verwenden; R/H und planbezogene Zusatzstatistik nicht summieren.
- DOKUMENTIERT: [sp_recompile](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-recompile-transact-sql?view=sql-server-ver17) veranlasst Neukompilierung beim nächsten Aufruf; erfolgreiche Rückgabe ist kein bereits ausgeführter Nutzaufruf. [Query-Store-Flush](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17) persistiert Speicherdaten und beweist weder allein Kompilierung noch Ausführung oder Replay-Nutzung.
- METHODE: B0 erst nach angenommener Force-Anforderung und vor eigener sp_recompile-Markierung, dann genau ein Nutzaufruf, vollständige Erfassung, vorhandener Flush und B1 zur selben query_id. Unforced Phasen entsprechend ohne Force; erste Identitätsbindung nicht mit erfundenem Nullzähler behandeln. Genau +1 in ununterbrochener Epoche ist strenges geplantes Abnahmekriterium, keine dokumentierte allgemeine Ein-Kompilierung-pro-Aufruf-Garantie. Beobachtbarkeit auf beiden Builds weiterhin ungeprüft.
- METHODE: NOT_PROVEN bei fehlender aktueller Evidenz oder unklarer Epoche von FAIL bei positiv belegter falscher/veralteter Zuordnung trennen. Schlussstatus FAIL_CLEANUP vor FAIL vor NOT_PROVEN vor PASS; sämtliche Ursachen/Teilbelege erhalten. CONTROL_ONLY bedeutet nur Kontrollzustand belegt, keinen empirischen Rundenerfolg und keinen alternativen H-Lauf.

Die Identitäts-/Hint-Grundlage aus dem vorigen Plan bleibt quellenbasiert gestützt;
vollständige konkrete Quelltexte, Marker-/Gegenvertrag, unabhängiger Methodenreview
und empirische Nachweise für 2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben offen.
Neun Nutzaufrufe je Version, zwei Container und gemeinsames Zeitbudget unverändert.
Frühere Quellenreviews und der alte Ein–Aus–Ein-Plan bleiben erhalten. Nur statische
Dokumentationsintegration; die [Auftragsgrenzen](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
halten Umsetzung, SQL-/Lab-Läufe und übrige Verarbeitung pausiert.

### DGN-004: Lesender Prüfbefund zum präzisierten Mess- und Statusvertrag vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`14958e680b5cec132e827c10e642cb7529c1d024`; Abruf/lesender Review 2026-10-24.
Der [kanonische Befund bei TSK-016](../../.ai/identity/registry.json) steht unter
`hint_evidence_status_review_result`; die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#lesender-prüfbefund-zum-präzisierten-mess--und-statusvertrag)
führt die Bestätigungen und verbleibenden Grenzen vollständig.

Der erneute Abgleich mit [Query-Katalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17),
[Plan-Katalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17),
[sp_recompile](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-recompile-transact-sql?view=sql-server-ver17)
und [Query-Store-Flush](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17)
bestätigt die dokumentarische Schlüssigkeit der präzisierten Zähler-/Messgrenzen.
METHODE: genau +1 bleibt eine strenge lokale Abnahmebedingung; kein einzelner
Zähler, Markierungsaufruf oder Flush ist allein Ausführungs-/Replay-Beweis.
Die beiden vorigen Präzisierungslücken sind dokumentarisch behoben; kein weiterer
Widerspruch im konkret geprüften Mess-/Statusvertrag festgestellt. Fehlende
Evidenz, belegte Vertragsverletzung und Bereinigungsfehler sind getrennt;
CONTROL_ONLY bleibt ausschließlich ein Teilbefund, kein empirischer Rundenerfolg.

Keine allgemeine Fehlerfreiheitsbehauptung, unabhängige Methodenfreigabe oder
neue Implementierungs-/Versions-/Demoabnahme. Der aktive Plan bleibt unverändert;
vollständige konkrete Quelltexte, Marker-/Gegenvertrag, unabhängige Reviews und
technische Nachweise für 2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben offen.
Im lesenden Review keine Tests, SQL-/Lab- oder CI-Läufe und kein Push; dieser
Folgeauftrag integriert nur Dokumentation mit statischen Prüfungen. Die
[Auftragsgrenzen](../Project_Planning/CURRENT_EXECUTION_STATUS.md) halten Umsetzung,
SQL-/Lab-Läufe und übrige Verarbeitung pausiert.

### DGN-004: R/H-Abfrageform und Engine-Textzuordnung vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`95105817ec14f4d0050b760611a1559ff19e4254`; Abruf/lesender Review 2026-10-24.
Der [kanonische Befund bei TSK-016](../../.ai/identity/registry.json) steht unter
`rh_query_text_review_result`; die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#rh-abfrageform-und-engine-textzuordnung)
enthält Quellen, Herleitung und offene Abnahmegrenzen vollständig.

- DOKUMENTIERT: [SELECT-Syntax](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver17) ordnet OPTION nach ORDER BY an. [Query Hints](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17) gelten bei UNION mit der OPTION-Klausel am letzten Zweig für das gesamte Statement. Die geplante Referenz R ohne Hint und Kontrolle H mit dauerhaftem terminalem DISABLE_OPTIMIZED_PLAN_FORCING sind damit quellenkonform; vollständiger Prozedurtext und technische Hint-Abnahme fehlen weiterhin.
- QUELLENBEFUND: Das [gepinnte Microsoft-Original](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/bigjoin.sql) (Git-Blob ba8e46ff75a9508585d2e18f9ec29cb57fbf5267) besitzt zehn Tabellen und zwei UNION-ALL-Zweige mit neun Joins, aber neun projizierte Spalten und ORDER BY OrderID. Die synthetische Form A hat zehn int-Spalten einschließlich GroupNo sowie drei Sortierschlüssel. Nur strukturelle Anregung; kein übertragener Eignungsnachweis. INFERENZ: 192 Detailzeilen mal zwei Gruppen mal zwei Zweige ergeben 768 Tupel, 384 verschiedene jeweils zweimal; keine Messung.
- DOKUMENTIERT: [sys.sql_modules](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-sql-modules-transact-sql?view=sql-server-ver17) führt die vollständige Moduldefinition; [sys.dm_exec_sql_text](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-sql-text-transact-sql?view=sql-server-ver17) den Batch-/Prozedurtext. Die [Abfragestatistik](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver17) grenzt Statements durch nullbasierte Byteoffsets darin ab. Batch-/Prozedurbezug, Statement und Planhandle sind zu unterscheiden.
- DOKUMENTIERT: [Query-Store-Abfragetext](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-text-transact-sql?view=sql-server-ver17) bewahrt innere Leerzeichen, Kommentare und Hinweise; äußere Kommentare und Leerraum werden ignoriert. METHODE: vollständige rohe Darstellungen getrennt halten und ihren Quellenbezug vor dem Versiegeln eindeutig belegen. Unterschiedliche Modulnamen gehören zur R/H-Modulidentität; der einzige erlaubte Nutzstatement-Unterschied bleibt der feste terminale Hint. Keine pauschale Textnormalisierung oder Übertragung von OPT-007-Semikolongrenzen.

Der versionierte Bestand enthält den Bauplan, kein vollständig festgeschriebenes
ausführbares R/H-Quellpaar. Die zu weit gehende Planungsabnahme wird entsprechend
begrenzt. Konkrete Quellen, akzeptierte Engine-Darstellungen und die vollständige
Erstzuordnung sind weiterhin unabhängig zu prüfen. Die erste beobachtete Ausgabe
allein beweist ihre eigene Zuordnung nicht. Tatsächliche Darstellung, Planzuordnung
und Replay-Nutzung (Wiederverwendung von Optimierungsschritten) für
2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben ungeprüft; keine unabhängige Methoden-,
Laufzeit- oder Demoabnahme.

Frühere Reviews, Quellkonflikte und der ältere Ein–Aus–Ein-Plan bleiben erhalten.
Mess-/Statusvertrag, neun Aufrufe je Version, zwei Container und gemeinsames
Zeitbudget unverändert. Im lesenden Review keine Tests, SQL-/Lab- oder CI-Läufe
und kein Push; dieser Folgeauftrag erlaubt nur statische Dokumentationsintegration.
Die [Auftragsgrenzen](../Project_Planning/CURRENT_EXECUTION_STATUS.md) halten Umsetzung,
SQL-/Lab-Läufe und übrige Verarbeitung pausiert.

### DGN-004: geplantes R/H-Quellpaar und Textzuordnungsvertrag vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`c005607276b67097018c9772feb04e4b8ad42cac`; Abruf/Planung 2026-10-24. Der
[kanonische Plan bei TSK-016](../../.ai/identity/registry.json) steht unter
`rh_source_text_plan`; die [abgeleitete Detailansicht](../../.ai/BACKLOG.md#geplantes-vollständiges-rh-quellpaar-und-begrenzte-textzuordnung)
enthält beide vollständigen Quellvorlagen, Quellenprüfsummen und Abnahmekriterien.
R ist Referenz ohne Hint, H die Kontrolle mit festem Abfragehinweis; keine neuen
ausführbaren SQL-Dateien, Demo-/Parserimplementierung oder SQL-/Lab-Läufe.

- DOKUMENTIERT: [CREATE PROCEDURE](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver17) liefert den Modulrahmen; [SELECT](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver17) und [Query Hints](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17) stützen die terminale OPTION-Klausel. METHODE: zwei parameterlose eigene Prozeduren mit vollständigen einzeiligen ASCII-Quellwerten, identischem Nutzstatement und genau dem festen terminalen Hint-Unterschied planen. Keine Syntax-/Engine-Abnahme durch bloßes Festschreiben.
- DOKUMENTIERT: [Moduldefinition](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-sql-modules-transact-sql?view=sql-server-ver17) und [Cachetext](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-sql-text-transact-sql?view=sql-server-ver17) sind von den durch [Byteoffsets](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver17) abgegrenzten Statements zu unterscheiden. METHODE: Quellen M sowie Nutzstatement S mit und T ohne letztes Semikolon vorab festlegen; Module/Cachebatch nur M, die drei Statementansichten nur S/T. Die geplante inklusive Endposition oder der -1-Sentinel sind begrenzte Vertragskandidaten nach dem Hersteller-Extraktionsmuster, keine beobachteten Werte der Zielbuilds.
- DOKUMENTIERT: [Query-Store-Abfragetext](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-text-transact-sql?view=sql-server-ver17) bewahrt innere Texte/Hinweise und lässt äußere Kommentare/Leerraum weg. METHODE: diese äußeren Texte in der Quelle vermeiden, keine freie Textbereinigung zulassen. StatementText aus dem vollständigen Plan separat dekodieren und mit Quellen-/Objekt-/Kontext-/Abfrage-/Ausführungsbezug erstzuordnen; erst danach die zulässige Darstellungswahl je Rolle/Build festhalten.
- METHODE/INFERENZ: Die unveränderte synthetische Form A nach dem [gepinnten bigjoin-Muster](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/bigjoin.sql) verwendet zehn Tabellen, neun Joins je Zweig, zehn int-Projektionen und zwei Zweige. 768 erwartete Tupel mit ihren Multiplizitäten bleiben eine rechnerische Erwartung, kein Ausführungs-/Replay-Nachweis. Die konkrete Vorlage ist eine eigene synthetische Anpassung.

DOKUMENTIERT: Der [Query-Katalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) ordnet query_parameterization_type = 0 der fehlenden Parametrisierung zu. METHODE: diesen Wert als strenge lokale Vorbedingung für R/H planen; keine bereits beobachtete Eigenschaft der Prozeduren behaupten.

Planungsabnahme bedeutet vollständige dokumentarische Quellen-/Vertragsfestlegung.
Ein unabhängiger Review und spätere technische M/S/T-/Offsetnachweise für
2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben offen; unbekannte Darstellungen werden
nicht automatisch normalisiert oder zugelassen. Replay (Wiederverwendung von
Optimierungsschritten), Gegenkennzeichnung, Flag-/Signaturkonflikte, Mess-/Statusvertrag
und alle bisherigen Gates bleiben gesondert erhalten. Keine zusätzliche Kalibrierung,
Budgetaddition oder Übernahme von OPT-007-Textbeobachtungen. Nur statische
Dokumentationsintegration; die [Auftragsgrenzen](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
halten Umsetzung, SQL-/Lab-Läufe und übrige Verarbeitung pausiert.

### DGN-004: Prüfbefund zum R/H-Quellpaar und Textvertrag vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`2c1a5fd998b58bc51a2a97fffc2472b275312332`; Abruf/lesender Review 2026-10-24. Der
[kanonische Befund bei TSK-016](../../.ai/identity/registry.json) steht unter
`rh_source_text_review_result`; die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#lesender-prüfbefund-zum-rh-quellpaar-und-textvertrag)
führt Bestätigungen, Grenzen und offene Gates vollständig.

Der Abgleich mit [SELECT](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver17), [Query Hints](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17),
[Byteoffsets und Cachebezug](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver17),
[Query-Store-Abfragetext](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-text-transact-sql?view=sql-server-ver17) und [Moduldefinition](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-sql-modules-transact-sql?view=sql-server-ver17)
stützt die getrennte Betrachtung des vollständigen R/H-Quellpaars und der endlichen
M/S/T-Darstellungen. R ist Referenz ohne Hint, H die Kontrolle mit festem
Abfragehinweis. M bezeichnet den ganzen Modultext, S das Nutzstatement mit und T
ohne letztes Semikolon. Hint-Position und Objekt-/Spaltenbezüge sind quellenkonform;
768 erwartete Tupel bleiben eine rechnerische Herleitung, keine gemessene Ausgabe.

Die [Laufzeitstatistik](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17) dokumentiert mögliche Mehrfachzeilen im aktiven Intervall und die Aggregation nach plan_id, execution_type und runtime_stats_interval_id. Der übergeordnete Zuordnungsvertrag erhält diese Aggregation. Der [Query-Katalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17) belegt die Bedeutung der Parametrisierungsart 0; der tatsächliche R/H-Wert bleibt ungeprüft. Die Ausnahmen für erste Identitätsbindungen in Aufrufen 1/4 dürfen keinen erfundenen Null-Kompilierungszähler erzeugen.

Im konkret geprüften Quellpaar, Textvertrag und den Abnahmekriterien wurde kein
weiterer konkreter Widerspruch festgestellt. Keine allgemeine Fehlerfreiheit oder
unabhängige Freigabe aus diesem Abgleich im selben Arbeitskontext ableiten.
Tatsächliche M/S/T-/Byteoffsetdarstellung, Planzuordnung, Kompilierungsbeobachtbarkeit
und Replay-Nutzung (Wiederverwendung von Optimierungsschritten) auf
2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben offen; bisherige Marker-/Flag-/
Signaturkonflikte erhalten. Aktive Quellvorlagen, Pläne, Abnahmekriterien und alle
Zeit-/Ressourcen-/Ergebnisverträge werden nicht geändert.

Im lesenden Review keine Änderungen, Tests, Validatoren, Parserprüfungen, frische
Prüfsummen-/Bytebereichsprüfung, SQL-/Lab- oder CI-Läufe und kein Push. Dieser
Folgeauftrag integriert ausschließlich Dokumentation mit statischen Prüfungen;
keine Syntax-/Engine-/Versions-/Demoabnahme. Die [Auftragsgrenzen](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
halten Umsetzung, SQL-/Lab-Läufe und übrige Verarbeitung pausiert.

### DGN-004: R-Markersemantik und H-Gegenvertrag vom 24. Oktober 2026

Ergänzung zu `SRC-027` (Query Store; persistente Abfrage-/Planhistorie) und
`SRC-031` (tatsächliche Planerfassung), keine neue Quellenkennung. Basis
`51eab9a11d372a41fbb5f6fd1f91c076c1ceb70d`; Abruf/lesender Review 2026-10-24. Der
[kanonische Befund bei TSK-016](../../.ai/identity/registry.json) steht unter
`rh_replay_marker_review_result`; die [abgeleitete Befundansicht](../../.ai/BACKLOG.md#r-markersemantik-und-beobachtbarer-h-gegenvertrag)
führt Quellen, Schlussfolgerungen und Grenzen vollständig. R ist Referenz ohne
Hint, H die Negativkontrolle mit festem Abfragehinweis.

| Quelle | Beleg und Grenze |
|---|---|
| [Herstellerkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17) | has_compile_replay_script = 1 bedeutet gespeichert; is_forced_plan bezeichnet eine Anforderung. Fehler 8675 / OPTIMIZATION_REPLAY_FAILED bedeutet gescheiterte Skriptausführung. INFERENZ: fehlender Fehler belegt weder Nutzung noch Nichtnutzung. |
| [2022-Showplan-XSD](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd) und [Schemaindex](https://schemas.microsoft.com/sqlserver/2004/07/showplan/) | Schema nur lesend als Text im Arbeitsspeicher geprüft: QueryCompilationReplay bleibt optionale Ganzzahl ohne semantische Zustandswerttabelle; Script-Attribut ist kein aktueller Nutzungsbeleg. Im öffentlichen Index kein gesonderter 2025-Wertevertrag; keine Aussage gegen Feature-Unterstützung. |
| [Originale Fachreferenz](https://sqlserverfast.com/epr/plan-properties/) | Beschreibt QueryCompilationReplay = 1 als Nutzung bei Kompilierung. Kandidat, keine Herstellerzusage oder reproduzierte Werte-/Gegenkennzeichnung beider exakten Builds und des vorgesehenen Erfassungswegs. |
| [Hersteller-Funktionsbeschreibung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17) und [Abfragehinweis](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17#disable_optimized_plan_forcing) | Fester H-Hint dokumentiert Abschaltung. Im bestehenden Vertrag höchstens CONTROL_ONLY (nur Kontrollzustand belegt), solange keine unabhängig erklärte beobachtete Nichtnutzung vorliegt. Keine pauschale 0-/Abwesenheitsinterpretation. |
| [Originale 2022-Ereignisliste](https://gist.github.com/zikato/47068829fc0bb164199447b271860335) | opt_replay_exception_info ist als Fehler-/Ausnahmediagnostik beschrieben. Kein Erfolgs-/Nichtnutzungswertevertrag, keine Abnahme auf unseren exakten Builds oder 2025. INFERENZ: Ereignisstille schließt das Marker-Gate nicht; keine neue Ereignissession autorisiert. |
| [Letzter tatsächlicher Plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17) | Enthält Cache-Kompilierungsdaten und letzte bekannte Laufzeitinformationen. Aktuelle Kompilierung, vollständigen eigenen Plan und aktuelle eigene Ausführung gemeinsam binden; kein Replay-Nachweis allein aus dem Funktionsnamen. |
| [Gepinnte Microsoft-Anleitung](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/readme.md) | Git-Blob d1498eee25536cf53df830ca187da706217a0131: Kandidat über Speicherflag, Demonstration über Kompilierungszeiten. Kein direkter Marker-/Gegenwertevertrag für die begrenzte Probe oder beide Zielbuilds. Keine fremden Messwerte als eigene Evidenz übernommen. |

Eine zusätzliche Literaturspur konnte im geprüften öffentlichen
[Verlagszugang](https://link.springer.com/chapter/10.1007/978-1-4842-8894-8_4)
nicht im relevanten Volltext geprüft werden. Nur bibliografisch geprüft und aus der technischen
Evidenz ausgeschlossen; kein weiterer Markerwiderspruch oder Produktfehler aus
Suchtreffer-Wiedergaben abgeleitet.

Für 2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben positive aktuelle R-Nutzung und
beobachtete H-Nichtnutzung unabhängig zu klären. Replay bedeutet Wiederverwendung
von Optimierungsschritten. Der empirische Vergleich bleibt NOT_PROVEN (nicht
nachgewiesen), mit unverändertem Vorrang positiver Vertrags-/Bereinigungsfehler.
Bestehende Quellenkonflikte, Quellpaar/Textvertrag, Abnahmekriterien und Laufbudgets
bleiben erhalten. Keine Implizitfreigabe durch neue Diagnosehinweise.

Im lesenden Review keine Umsetzung, Tests, Validatoren, Parserprüfungen,
SQL-/Lab- oder CI-Läufe, kein Push und keine Repositoryänderung. Dieser Folgeauftrag
integriert nur Dokumentation mit statischen Prüfungen; keine technische Versions-
oder Demoabnahme. Die [Auftragsgrenzen](../Project_Planning/CURRENT_EXECUTION_STATUS.md)
halten Umsetzung, SQL-/Lab-Läufe und übrige Verarbeitung pausiert.

### DGN-004: Markerprobenplan vom 25. Oktober 2026

Bei TSK-016 (gezielte Curriculum-Ergänzungen) ergänzt der
[kanonisch abgeleitete Markerplan](../../.ai/BACKLOG.md#begrenzte-rh-markerprobe-für-nutzung-und-nichtnutzung)
die vorhandene R/H-Folge: R ist Referenz ohne Hint, H die Negativkontrolle mit
festem Abschalthinweis. Nutzung und Nichtnutzung von Optimierungs-Replay
(Wiederverwendung von Optimierungsschritten) getrennt abnehmen. Quellen erneut
lesend geprüft am 25. Oktober 2026, keine neue empirische Evidenz.

Die [Herstellerbeschreibung zur optimierten Planerzwingung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17)
belegt Skriptaufzeichnung und die querybezogene Abschaltkontrolle. Die
[originale Fachreferenz zu Planeigenschaften](https://sqlserverfast.com/epr/plan-properties/)
liefert QueryCompilationReplay = 1 als positiven Kandidaten; das
[Hersteller-Schema](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd)
nennt weiterhin nur eine optionale Ganzzahl ohne Nutzungs-/Nichtnutzungstabelle.
Die [Herstellerbeschreibung zum letzten tatsächlichen Plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17)
begrenzt die Erfassung auf zwischengespeicherte Kompilierungsinformationen mit
letzten bekannten Laufzeitdaten. Deshalb aktuelle eigene Kompilierung und
Ausführung vollständig zuordnen; weder gespeichertes Skript noch letzter Plan
allein belegen Replay-Nutzung.

**Methodischer Schluss:** Vor Umsetzung unabhängige Zustandssemantik und
Erfassungsvollständigkeit für 2022/16.0.4265.3 und 2025/17.0.4075.5 klären.
Unterschiedliche R/H-Rohwerte kalibrieren ihre Bedeutung nicht selbst. Abwesenheit
darf nur nach eigenständigem Vollständigkeits- und Bedeutungsnachweis eine
Nichtnutzung tragen; derzeit offen. Vorhandene Quellenkennungen SRC-027
(Query Store) und SRC-031 (tatsächliche Planerfassung) genügen; keine neue Kennung.
Neun Nutzaufrufe je Version und vorhandenes gemeinsames Budget unverändert,
keine neue Telemetrie, Implementierung oder SQL-/Lab-Ausführung. Der
[Ausführungsstand](../Project_Planning/CURRENT_EXECUTION_STATUS.md) hält die
offenen Freigabegates und die übrige Verarbeitungspause fest.
