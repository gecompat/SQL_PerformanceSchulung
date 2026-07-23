# Master-Umsetzungsplan – SQL-Server-Performance-Schulung

| Merkmal | Wert |
|---|---|
| Status | `PLANNED` |
| Planversion | 1.0 |
| Stand | 2026-07-23 |
| Primäre Zielplattform | SQL Server 2025 |
| Kompatibilitätsmatrix | SQL Server 2019, 2022 und 2025 |
| Bevorzugtes Demonstrationsmittel | T-SQL |
| Verbindlicher Datenschutzstatus | ausschließlich synthetische und firmenneutrale Inhalte |

## 1. Zweck dieses Plans

Dieser Plan beschreibt die vollständige Umsetzung des Schulungsprojekts so detailliert, dass eine spätere Bearbeitung ohne Rekonstruktion der bisherigen Überlegungen begonnen oder fortgesetzt werden kann. Er konkretisiert die Wellen aus [`.ai/ROADMAP.md`](../../.ai/ROADMAP.md), ersetzt aber weder die verbindlichen Projektregeln noch den Demo-Vertrag.

Der Plan erzeugt selbst noch keine Demo-Skripte, Infrastrukturdefinitionen oder Präsentationen. Er legt Arbeitspakete, Reihenfolge, Abhängigkeiten, erwartete Artefakte, Prüfschritte und Abschlusskriterien fest.

## 2. Verbindlicher Ausgangspunkt

Vor jeder Bearbeitung sind in dieser Reihenfolge zu lesen:

1. [`.ai/PROJECT_CONTEXT.md`](../../.ai/PROJECT_CONTEXT.md)
2. [`.ai/PROJECT_RULES.md`](../../.ai/PROJECT_RULES.md)
3. [`.ai/DECISIONS.md`](../../.ai/DECISIONS.md)
4. [`.ai/DEMO_CONTRACT.md`](../../.ai/DEMO_CONTRACT.md)
5. [`.ai/ROADMAP.md`](../../.ai/ROADMAP.md)
6. dieses Dokument
7. [`.ai/BACKLOG.md`](../../.ai/BACKLOG.md)

Die Repository-Grundstruktur wurde mit Commit `25bc970d8b9bb6d4519e52e3d5ab85e85c1c5e66` angelegt. Dieser Commit ist nur die technische Ausgangsbasis; der fachliche und ausführbare Inhalt ist noch zu erstellen.

## 3. Zielzustand

Das Projekt ist abgeschlossen, wenn folgende Artefaktgruppen konsistent vorliegen:

- ein fachlich validiertes Curriculum mit Einsteigerpfad und Expertenvertiefungen,
- eine bereinigte, firmenneutrale Präsentation mit Quellen, Sprecherhinweisen und Demo-Zuordnung,
- ein vollständiger Demo-Katalog mit stabilen IDs,
- reproduzierbare T-SQL-Demos mit Setup, Evidenz, Gegenmaßnahme, Vergleich und Cleanup,
- automatisierbare Docker-/Podman-Labs für portable Standardszenarien,
- automatisierbare Hyper-V-Labs für Windows-, Storage- und OS-nahe Szenarien,
- statische und dynamische Tests für Datenschutz, Struktur, Syntax, Wiederholbarkeit und Versionsverhalten,
- Trainer- und Teilnehmerhinweise für Durchführung, Interpretation und Fehlerbehebung,
- ein Releasepaket mit nachvollziehbarer Versions- und Quellenbasis.

## 4. Nichtziele

- Kein Bestandteil dieses Projekts darf ein anderes Repository verändern.
- Es werden keine realen Diagnoseausgaben, Screenshots, Namen, Logos, Hostnamen, Datenbanknamen, Pfade oder Organisationsinformationen versioniert.
- Das Lab ist kein Produktions-Monitoring-Framework.
- Ein gemessener Effekt auf einer Labormaschine wird nicht als universeller Schwellenwert dargestellt.
- Rot eingestufte Demos werden nicht für Produktionssysteme freigegeben.
- Drittanbieter-Werkzeuge werden nicht ungeprüft eingebettet oder stillschweigend vorausgesetzt.

## 5. Steuerungsmodell

### 5.1 Statuswerte

Jedes Arbeitspaket und jede Demo verwendet genau einen Status:

| Status | Bedeutung |
|---|---|
| `PROPOSED` | vorgesehen, fachlicher Zuschnitt noch offen |
| `RESEARCHED` | Quellen und Versionsgrenzen sind geprüft |
| `DESIGNED` | Ablauf, Datenmodell, Evidenz und Tests sind festgelegt |
| `IMPLEMENTED` | Artefakte sind vorhanden, aber noch nicht vollständig validiert |
| `VALIDATED` | zutreffende Tests und fachliches Review sind erfolgreich |
| `RELEASED` | in einer freigegebenen Schulungsfassung enthalten |
| `BLOCKED` | Fortsetzung benötigt eine dokumentierte Entscheidung oder Voraussetzung |
| `DEFERRED` | bewusst zurückgestellt; Begründung ist dokumentiert |

### 5.2 Größenklassen

- `S`: einzelne, klar begrenzte Änderung ohne neue Infrastruktur.
- `M`: eine vollständige Demo oder ein begrenztes Querschnittsmodul.
- `L`: mehrere abhängige Artefakte oder Multi-Session-/Versionslogik.
- `XL`: eigener Infrastruktur- oder Präsentations-Workstream; zwingend in kleinere PRs aufteilen.

### 5.3 Definition of Ready

Ein Arbeitspaket darf implementiert werden, wenn:

- Ziel und Nichtziel eindeutig formuliert sind,
- Datenschutz- und Sicherheitsstufe feststehen,
- betroffene Versionen, Compatibility Levels, Editionen und Betriebssysteme benannt sind,
- Quellenlage und offene fachliche Fragen dokumentiert sind,
- erwartete Evidenz und Messmethode feststehen,
- Abhängigkeiten erfüllt oder als kontrollierte Annahmen dokumentiert sind,
- der geplante Cleanup den Ausgangszustand wiederherstellt.

### 5.4 Definition of Done

Ein Arbeitspaket gilt als erledigt, wenn:

- alle vorgesehenen Artefakte im Repository vorhanden sind,
- Inhalte und Metadaten den Datenschutzregeln entsprechen,
- technische Aussagen auf belastbare Quellen oder klar gekennzeichnete Messungen gestützt sind,
- Setup und Cleanup mindestens zweimal hintereinander erfolgreich ausgeführt wurden,
- alle zutreffenden Tests erfolgreich sind,
- versions- oder editionsbedingte Skip-Regeln begründet sind,
- Dokumentation, Demo-Katalog und Status gemeinsam aktualisiert wurden,
- bekannte Grenzen und Abbruchbedingungen dokumentiert sind.

## 6. Kritischer Pfad und Gates

```mermaid
graph TD
    A["Welle 0: Inventar und Fachprüfung"] --> B["Gate A: freigegebener Themenbestand"]
    B --> C["Welle 1: Demo-Framework"]
    C --> D["Gate B: vier validierte Pilotdemos"]
    D --> E["Welle 2: vorhandene Beispiele"]
    D --> F["Wellen 3–9: Fachdemos"]
    E --> G["Gate C: vollständiger Demo-Katalog"]
    F --> G
    G --> H["Welle 10: Infrastrukturabnahme"]
    H --> I["Gate D: Präsentation und Release"]
```

### Gate A – Fachlicher Bestand freigegeben

- Quelleninventar vollständig.
- Reale oder interne Inhalte sind ausgeschlossen oder sanitisiert.
- Aussagenregister mit `KEEP`, `REFINE`, `REPLACE` oder `REMOVE` gepflegt.
- Fehlende Themen priorisiert.
- Vorläufige Demo-IDs und Curriculum-Zuordnung vorhanden.

### Gate B – Demo-Framework belastbar

Vier Pilotdemos müssen den vollständigen Vertrag erfüllen:

1. eine grüne Single-Session-Demo,
2. eine grüne Plan-/Statistik-Demo,
3. eine gelbe Multi-Session-Blocking-Demo,
4. eine gelbe Ressourcen-Demo mit Abbruchkriterien.

Erst danach werden größere Mengen fachlicher Demos umgesetzt.

### Gate C – Inhaltliche Abdeckung vollständig

- Jeder freigegebene Schulungsabschnitt besitzt mindestens eine Erklärung oder Demo.
- Jede Demo ist einem Curriculum- und Präsentationsabschnitt zugeordnet.
- Überschneidungen wurden bewusst zusammengeführt oder begründet getrennt.
- Alle Demos besitzen Version, Risiko, Laufzeitklasse und Infrastrukturprofil.

### Gate D – Releasefähig

- Statische Prüfungen vollständig grün.
- Alle grünen Demos in der zutreffenden Versionsmatrix validiert.
- Gelbe und rote Demos in den vorgesehenen isolierten Profilen validiert.
- Präsentation, Sprecherhinweise, Teilnehmeranleitung und Demo-Katalog stimmen überein.
- Release- und Wiederherstellungsanleitung geprüft.

## 7. Welle 0 – Inventar, Datenschutz und fachliche Konsolidierung

### Ziel

Alle vorhandenen Schulungsunterlagen und Beispiele werden nachvollziehbar erfasst, datenschutzsicher klassifiziert und fachlich gegen aktuelle Primärquellen geprüft. In dieser Welle werden noch keine vorhandenen Office-Dateien unverändert veröffentlicht.

### Arbeitspakete

| ID | Größe | Arbeit | Ergebnis / Abnahme |
|---|---:|---|---|
| `W0-001` | M | Quellenmanifest für Folien, Dokumente und Beispiele erstellen | Hash, Typ, Umfang, Herkunftsklasse, Privacy-Status und Importentscheidung je Quelle |
| `W0-002` | M | Privacy- und Metadatenprüfung definieren | Prüfliste für sichtbaren Inhalt, Notes, Alt-Text, Office-Metadaten, eingebettete Objekte, Bilder und Exporte |
| `W0-003` | L | Themen- und Aussagenregister erstellen | Jede relevante Aussage erhält Quelle, Folienbezug, Versionsgrenze und Status `KEEP/REFINE/REPLACE/REMOVE` |
| `W0-004` | L | Kritische Bestandsaussagen prüfen | Mindestens CTE, Table Variables, Fill Factor, Partition-Metadaten, Isolation, Columnstore, CE, Filegroups und Memory Grants vollständig bewertet |
| `W0-005` | M | Fehlende Themen bewerten | Priorisierte Gap-Liste mit Lernwert, Demo-Eignung, Aufwand, Risiko und Versionsbezug |
| `W0-006` | M | Quellenregister strukturieren | Primärquelle, Aktualisierungsdatum, Abrufdatum, Aussagebezug und Gültigkeitsbereich je Eintrag |
| `W0-007` | S | Begriffs- und Schreibstandard festlegen | Einheitliche Terminologie, deutsche Erklärung und unveränderte etablierte Fachbegriffe |
| `W0-008` | M | Konflikt- und Entscheidungslog einführen | Offene fachliche Widersprüche werden nicht stillschweigend aufgelöst |

### Besonders zu prüfende Themen

- CTE-Ausführung und mögliche Spool-Operatoren,
- lesende und schreibende Zugriffe auf Table Variables,
- Deferred Compilation und Compatibility Level,
- Fill Factor, Page Density, Page Splits und Fragmentation,
- korrekte Interpretation von `index_id` und Partition-Metadaten,
- RCSI gegenüber SNAPSHOT und Update-Konflikte,
- versionsabhängige Columnstore-Funktionen,
- Cardinality-Estimation-Modelle gegenüber Feedback-Funktionen,
- tatsächliche Wirkung von Filegroups ohne getrennte physische I/O-Pfade,
- grantable memory, Required/Desired/Requested/Granted/Used Memory,
- Threads, Tasks, Workers, Schedulers und Partitionierung,
- produktive Relevanz und Grenzen undokumentierter Diagnosefunktionen.

## 8. Querschnitt A – Curriculum und Nachverfolgbarkeit

Dieser Workstream beginnt nach `W0-003` und läuft bis zum Release.

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `CUR-001` | M | Zielgruppen und Vorwissen definieren | Einsteiger, Entwicklung, Administration und Vertiefung klar abgegrenzt |
| `CUR-002` | L | Modulreihenfolge entwerfen | Abhängigkeiten zwischen Storage, Optimizer, Query Patterns, Indizes, Concurrency, Ressourcen und Diagnose berücksichtigt |
| `CUR-003` | M | Lernziele je Modul formulieren | beobachtbare und prüfbare Lernziele statt Themenüberschriften |
| `CUR-004` | M | Einsteiger- und Expertenpfad kennzeichnen | gemeinsamer Kern, optionale Vertiefung und notwendiges Vorwissen sichtbar |
| `CUR-005` | L | Traceability-Matrix pflegen | Quelle → Aussage → Curriculum → Folie → Demo → Test vollständig zuordenbar |
| `CUR-006` | M | Zeit- und Durchführungsvarianten entwerfen | Kurz-, Standard- und Vertiefungsformat mit auslassbaren Blöcken |
| `CUR-007` | M | Übungen und Verständnisfragen planen | Aufgabe, erwartete Beobachtung, Fehlannahmen und Musterlösung je Kernmodul |
| `CUR-008` | S | Erfolgskriterien definieren | praktische und theoretische Lernkontrolle dokumentiert |

## 9. Querschnitt B – Demo-Katalog und Benennung

### ID-Schema

| Präfix | Themenbereich |
|---|---|
| `FWK` | gemeinsames Demo-Framework |
| `STL` | Storage, Pages und Transaction Log |
| `OPT` | Optimizer, Statistics und Execution Plans |
| `QRY` | Query Patterns |
| `IDX` | Rowstore und Columnstore |
| `CON` | Concurrency, Isolation und TempDB |
| `RES` | CPU, Memory, I/O und Waits |
| `DGN` | Diagnosewerkzeuge |
| `INF` | Infrastruktur-Labs |

IDs werden nach Veröffentlichung nicht neu nummeriert. Entfernte Kandidaten bleiben im Katalog als `DEFERRED` oder `RETIRED` sichtbar.

### Pflichtfelder des Katalogs

- ID, Titel, Status und Themenbereich,
- Lernziel und fachliche Kernaussage,
- Curriculum- und Präsentationsbezug,
- Version, Compatibility Level, Edition und Betriebssystem,
- Sicherheitsstufe und erforderliches Labprofil,
- Zahl der Sessions, Laufzeitklasse und erwarteter Speicherbedarf,
- Setup-, Evidenz-, Mitigation- und Cleanup-Pfad,
- automatisierbare und manuelle Tests,
- Quellenstatus, letzter Test und bekannte Grenzen.

## 10. Welle 1 – Gemeinsames Demo-Framework

### Ziel

Wiederverwendbare Bausteine verhindern, dass jede Demo eigene Sicherheits-, Mess- und Cleanup-Logik erfindet.

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `FWK-001` | M | Preflight-Vertrag | Version, Edition, Compatibility Level, Rechte, Konfiguration, freier Speicher und Labfreigabe werden geprüft |
| `FWK-002` | M | Lab-Datenbank-Lifecycle | idempotente Anlage, eindeutige Kennzeichnung, Schutz vor falscher Zieldatenbank und vollständiges Entfernen |
| `FWK-003` | L | synthetischer Datengenerator | deterministische Seeds, skalierbare Zeilenzahl, Skew-, Korrelations- und Breitenprofile |
| `FWK-004` | L | Messrahmen | CPU, Duration, Reads, Writes, Rows, Grants, Wait-Deltas und Dateilatenzen themengerecht erfassbar |
| `FWK-005` | M | Plan- und Statistik-Evidenz | Estimated/Actual Plan, relevante XML-Warnings, Statistikheader und Histogramme versionsbewusst dokumentierbar |
| `FWK-006` | M | Multi-Session-Orchestrierung | Sessionreihenfolge, Barrieren, Timeouts, Abbruch und Recovery eindeutig |
| `FWK-007` | M | Query-Store- und XE-Helfer | isolierte Aktivierung, Datenerfassung, Export synthetischer Evidenz und Cleanup |
| `FWK-008` | M | Sicherheits- und Abbruchrahmen | Grün/Gelb/Rot, Ressourcenbudgets, Kill-Switch und Wiederherstellung geprüft |
| `FWK-009` | S | Demo-Dokumentvorlage | alle Pflichtfelder aus dem Demo-Vertrag enthalten |
| `FWK-010` | M | Test-Harness | Setup, Baseline, Demo, Mitigation, Comparison und Cleanup automatisiert aufrufbar |
| `FWK-011` | M | Ergebnisnormalisierung | hardwareabhängige Bereiche, relationale Erwartungen und versionierte Golden-Metadaten statt fragiler Fixwerte |
| `FWK-012` | S | Fehler- und Skip-Vertrag | erwartete Skips von echten Fehlern unterscheidbar; Ursache und Voraussetzung werden ausgegeben |

### Pilotabnahme

Die vier Demos für Gate B werden erst im Detail ausgewählt, wenn Welle 0 abgeschlossen ist. Empfohlene Kandidaten sind SARGability, Statistik-Skew, Blocking Chain und kontrollierter Memory-Grant-/Spill-Effekt.

## 11. Welle 2 – Vorhandene Beispiele modernisieren

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `W2-001` | M | Bestandsbeispiele klassifizieren | `REUSE`, `REFACTOR`, `REBUILD`, `DIAGNOSTIC_ONLY` oder `REMOVE` je Beispiel |
| `W2-002` | L | interne Abhängigkeiten entfernen | ausschließlich synthetische Datenbanken, Tabellen, Werte und neutrale Bezeichnungen |
| `W2-003` | L | Beispiele in Demo-Vertrag überführen | Preflight, Setup, Baseline, Evidenz, Mitigation, Vergleich und Cleanup vorhanden oder begründet entfallen |
| `W2-004` | M | Diagnoseabfragen modernisieren | Version, Rechte, Scope, Delta-Methodik und Messgrenzen dokumentiert |
| `W2-005` | M | bestehende Kernaussagen neu messen | Effekt reproduzierbar; veraltete oder zufällige Effekte werden ersetzt |
| `W2-006` | M | Mapping zu neuen IDs | kein Beispiel bleibt außerhalb von Katalog und Curriculum |

## 12. Wellen 3 bis 9 – Geplanter Demo-Bestand

Die folgende Liste definiert 69 geplante Demo-Bündel. Ein Bündel darf während des Designs in mehrere Demos geteilt werden, wenn Sicherheitsstufe, Version oder didaktischer Ablauf sonst unklar werden. Zusammenlegungen benötigen eine dokumentierte Begründung, damit keine Kernaussage verloren geht.

### Welle 3 – Storage, Pages und Transaction Log

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `STL-001` | Page- und Row-Aufbau, Slot Array, NULL Bitmap und Wirkung der Zeilenbreite | Grün |
| `STL-002` | IN_ROW_DATA, ROW_OVERFLOW_DATA und LOB_DATA | Grün |
| `STL-003` | Heap, RID, Forwarded Records und Lookup-Kosten | Grün |
| `STL-004` | Allocation Units, Extents und Page-Metadaten | Grün |
| `STL-005` | Files, Filegroups, Proportional Fill und Autogrowth | Rot |
| `STL-006` | Buffer Pool, Cold/Warm Cache sowie Logical und Physical Reads | Gelb |
| `STL-007` | Log Records, Commit, Rollback und Checkpoint | Grün |
| `STL-008` | VLF-Struktur und geplantes gegenüber ungeplantem Logwachstum | Rot |
| `STL-009` | kleine Commits, Batch-Commit und `WRITELOG` | Gelb |
| `STL-010` | NONE-, ROW-, PAGE- und Columnstore-Kompression: Größe, CPU und I/O | Gelb |

### Welle 4 – Optimizer, Statistics und Execution Plans

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `OPT-001` | Estimated gegenüber Actual Plan und Schätzfehler | Grün |
| `OPT-002` | Statistikheader, Histogramm und Density Vector | Grün |
| `OPT-003` | Sampling, Fullscan, Skew und Histogrammgrenzen | Grün |
| `OPT-004` | Spaltenkorrelation, Constraints und Eindeutigkeit als Optimizer-Wissen | Grün |
| `OPT-005` | Ascending Key sowie synchrone und asynchrone Statistikpflege | Grün |
| `OPT-006` | Cardinality-Estimation-Modelle und versionsabhängiges Feedback | Grün |
| `OPT-007` | Compilation, Recompilation, Plan Reuse und Ad-hoc-Cache-Pollution | Gelb |
| `OPT-008` | Parameter Sniffing und stabile Reproduktion von Daten-Skew | Grün |
| `OPT-009` | Parameter Sensitive Plan Optimization und Versionsvergleich | Grün |
| `OPT-010` | Optional Parameter Plan Optimization und Alternativen auf älteren Versionen | Grün |
| `OPT-011` | Row Goals durch `TOP`, `FAST n` und `EXISTS` | Grün |
| `OPT-012` | Nested Loops, Merge und Hash Join mit veränderter Kardinalität | Grün |
| `OPT-013` | Sort-, Hash- und Exchange-Spills | Gelb |
| `OPT-014` | Required, Desired, Requested, Granted und Used Memory sowie Memory Grant Feedback | Gelb |

### Welle 5 – Query Patterns

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `QRY-001` | SARGable und Non-SARGable Prädikate einschließlich Funktionen auf Indexspalten | Grün |
| `QRY-002` | Implicit Conversion, Datentyp- und Collation-Mismatch | Grün |
| `QRY-003` | halboffene Datumsintervalle und Datentypgenauigkeit | Grün |
| `QRY-004` | optionale Parameter: statisches SQL, Recompile, dynamisches SQL und adaptive Varianten | Grün |
| `QRY-005` | `OR` gegenüber geeigneten `UNION ALL`-Varianten | Grün |
| `QRY-006` | NULL-Semantik, `NOT IN`, `NOT EXISTS`, Semi und Anti Semi Join | Grün |
| `QRY-007` | `DISTINCT`, `UNION`, `UNION ALL` und `SELECT *` als Kosten- oder Modellierungsindikator | Grün |
| `QRY-008` | CTE, Temp Table und Table Variable mit versionsabhängiger Optimierung | Grün |
| `QRY-009` | Inline TVF, Multi-Statement TVF und Scalar UDF mit und ohne Inlining | Grün |
| `QRY-010` | `APPLY`, Window Functions, Cursor und set-based Verarbeitung | Gelb |
| `QRY-011` | Computed Column, Filtered Index und Predicate Implication | Grün |
| `QRY-012` | Partition Elimination, Remote Pushdown sowie messbare JSON/XML/String-Kosten | Gelb |

### Welle 6 – Rowstore und Columnstore

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `IDX-001` | Heap gegenüber Clustered Index | Grün |
| `IDX-002` | Breite und Eindeutigkeit des Clustered Key sowie Uniquifier | Grün |
| `IDX-003` | Key-Reihenfolge, Left-Based Prefix und INCLUDE | Grün |
| `IDX-004` | Covering, Key/RID Lookup und Tipping Point | Grün |
| `IDX-005` | redundante/überlappende Indizes und DML-Kosten | Gelb |
| `IDX-006` | Page Splits, Page Density, Fragmentation und Fill Factor | Gelb |
| `IDX-007` | Sequential-Key-Insert, Last-Page-Contention und geeignete Gegenmaßnahmen | Gelb |
| `IDX-008` | Row-/Page-Compression mit Größen-, CPU- und I/O-Trade-off | Gelb |
| `IDX-009` | Columnstore-Interna: Delta Store, Rowgroups, Delete Bitmap und Direct Compressed Load | Gelb |
| `IDX-010` | Segment Elimination, geordnete Columnstore-Varianten und Maintenance | Gelb |

### Welle 7 – Concurrency, Isolation und TempDB

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `CON-001` | Dirty Read, Non-repeatable Read, Phantom und Lost-Update-Szenarien | Gelb |
| `CON-002` | READ COMMITTED, REPEATABLE READ und SERIALIZABLE einschließlich Key-Range Locks | Gelb |
| `CON-003` | RCSI, SNAPSHOT, Statement-/Transaction-Snapshot und Update-Konflikt | Gelb |
| `CON-004` | Blocking Chain, Head Blocker und messbare Wartezeit | Gelb |
| `CON-005` | Lock Escalation, Schema Locks und Metadatenzugriff | Gelb |
| `CON-006` | reproduzierbarer Deadlock mit Deadlock Graph | Gelb |
| `CON-007` | Version Store, ADR und Persisted Version Store | Gelb |
| `CON-008` | versionsabhängiges Optimized Locking, TID Locks und Lock After Qualification | Gelb |
| `CON-009` | TempDB-Allocation-Contention und Memory-optimized TempDB Metadata | Gelb |

### Welle 8 – CPU, Memory, I/O und Waits

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `RES-001` | CPU-bound Query, Worker, Scheduler und `SOS_SCHEDULER_YIELD` | Gelb |
| `RES-002` | Parallelism Overhead, DOP und Parallel Skew | Gelb |
| `RES-003` | Memory Pressure gegenüber Query Execution Memory und `RESOURCE_SEMAPHORE` | Rot |
| `RES-004` | Overgrant, Undergrant, Spill und konkurrierende Grants | Gelb |
| `RES-005` | `PAGEIOLATCH_*` gegenüber `PAGELATCH_*` | Rot |
| `RES-006` | Log- und Datenfile-Latenz, `WRITELOG` und Dateistatistik-Deltas | Rot |
| `RES-007` | Wait-Stat-Deltas, Request-/Task-Waits und `ASYNC_NETWORK_IO` | Gelb |

### Welle 9 – Diagnosewerkzeuge

| ID | Demo-Bündel | Standardrisiko |
|---|---|---|
| `DGN-001` | `STATISTICS IO/TIME`, Actual Plan und kontrollierter A/B-Vergleich | Grün |
| `DGN-002` | Session-, Request- und Task-DMVs sowie Live Query Statistics | Grün |
| `DGN-003` | Query Store: Regression, mehrere Pläne, Runtime- und Wait-Historie | Grün |
| `DGN-004` | Plan Forcing, Query Store Hints und sichere Rücknahme | Gelb |
| `DGN-005` | Extended Events für Deadlocks, Blocking, Spills, Recompiles und Fehler | Gelb |
| `DGN-006` | Workload-Treiber, hohe Sessionzahl, OS-Metriken und reproduzierbare Baselines | Gelb |

## 13. Welle 10 – Infrastruktur-Labs

### 13.1 Architekturprinzip

Die Standardumgebung wird containerbasiert und versionsweise nacheinander gestartet. Dadurch müssen die Images und Datenvolumes nicht gleichzeitig RAM und Storage belegen. Hyper-V wird nur verwendet, wenn Windows-Verhalten, echte virtuelle Datenträger, OS-nahe Messung oder stärkere Isolation fachlich erforderlich sind.

### 13.2 Geplante Infrastruktur-Bündel

| ID | Infrastruktur-Bündel | Bevorzugte Plattform |
|---|---|---|
| `INF-001` | portables Eininstanz-Basislab mit Gesundheitsprüfung und Datenpersistenz | Docker und Podman |
| `INF-002` | CPU- und RAM-Begrenzung mit dokumentiertem Ressourcenbudget | Docker, Podman; Hyper-V als Vergleich |
| `INF-003` | gedrosseltes Daten- und Log-I/O mit getrennten Pfaden | Hyper-V primär; Container nur nach nachgewiesener Hostunterstützung |
| `INF-004` | Netzwerk-Latenz, Bandbreite und langsamer Client | Container-Netzwerk oder Hyper-V-QoS |
| `INF-005` | Multi-Instanz-, Failover- und Secondary-Topologie | Container für portable Varianten; Hyper-V für Windows-spezifische Varianten |
| `INF-006` | Windows-Lab mit OS-Metriken und Windows-spezifischen Funktionen | Hyper-V |

### 13.3 Container-Arbeitspakete

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `INF-C01` | M | gemeinsame Compose-Spezifikation | neutrale Variablen, Healthcheck, persistente Volumes und Profile ohne Secrets |
| `INF-C02` | M | Docker-Kompatibilität | Setup, Start, Stop, Reset, Ressourcenlimits und Netzwerk geprüft |
| `INF-C03` | M | Podman-Desktop-Kompatibilität | gleiche Funktionsprüfung; Abweichungen als Override statt Fork dokumentiert |
| `INF-C04` | M | Versionsprofile | 2019, 2022 und 2025 einzeln startbar; Feature-Skips nachvollziehbar |
| `INF-C05` | M | Ressourcenkalibrierung | kleinstes stabiles Profil und erweitertes Lastprofil empirisch ermittelt |
| `INF-C06` | M | Storage-Lifecycle | sparse/persistente Volumes, definierter Reset und maximale Belegung dokumentiert |
| `INF-C07` | M | Netzwerk- und I/O-Fähigkeiten | tatsächlich wirksame Limits gemessen; wirkungslose Einstellungen werden nicht dokumentiert |
| `INF-C08` | S | Secrets-Vertrag | lokale `.env`-Vorlage ohne Werte, keine Credentials im Repository, klare Rotation |

### 13.4 Hyper-V-Arbeitspakete

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `INF-H01` | M | Host-Preflight per PowerShell | Edition, Featurestatus, Virtualization, freier RAM/Storage und Administratorrechte geprüft |
| `INF-H02` | L | reproduzierbares Basisimage | dokumentierter Ursprung, Patchstand, Lizenzstatus und Privacy-bereinigte Vorlage |
| `INF-H03` | L | automatisierter VM-Lifecycle | Create, Start, Stop, Reset und Remove mit Schutz gegen falsche Ziel-VM |
| `INF-H04` | M | differenzierende VHDX-/Checkpoint-Strategie | minimaler Storageverbrauch und reproduzierbarer Rücksetzpunkt |
| `INF-H05` | M | feste Messprofile | CPU und RAM bleiben während einer Messung stabil; dynamische Zuweisung nur außerhalb belastbarer Benchmarks |
| `INF-H06` | L | virtuelle Storage-Topologien | getrennte Daten-/Log-/TempDB-Datenträger und gezielte Drosselung messbar |
| `INF-H07` | M | Netzwerkprofile | internes Netz, NAT/Hostzugriff und optionales QoS ohne reale Umgebungswerte |
| `INF-H08` | M | Windows-Metrikpfad | OS-Zähler, Zeitstempel und SQL-Evidenz zeitlich korrelierbar |
| `INF-H09` | M | Cleanup und Recovery | alle Änderungen rücksetzbar; Notfallpfad und erwartete Restarteffekte dokumentiert |

### 13.5 Ressourcenziel

Die endgültigen Zahlen werden in `INF-C05` und `INF-H05` empirisch bestimmt. Bis dahin gelten folgende Planungsregeln:

- nur eine SQL-Server-Version gleichzeitig für normale Entwicklung starten,
- Mehrinstanzprofile ausschließlich bei einer Demo mit nachgewiesener Abhängigkeit verwenden,
- synthetische Daten bevorzugt reproduzierbar generieren statt große Datenbanken einzuchecken,
- sparse Volumes, differenzierende Disks und kontrollierte Cleanup-Skripte nutzen,
- Basis-, Standard- und Stressprofil getrennt dokumentieren,
- Messwerte nur innerhalb desselben Profils vergleichen,
- bei Storage- und Netzwerkdemos die tatsächlich erreichte Begrenzung messen.

## 14. Querschnitt C – Präsentation und Lehrmaterial

Dieser Workstream beginnt erst nach Gate A; finale Folien werden nach Gate C fertiggestellt.

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `PRS-001` | M | neutrales Designsystem | keine Logos/Firmeninformationen; zugängliche Farben, Typografie und Layoutregeln |
| `PRS-002` | L | fachliche Folienbereinigung | jede geprüfte Aussage korrekt, versionsbewusst und ohne pauschale Tuning-Regel |
| `PRS-003` | L | Demo-Integration | Demo-ID, Ausgangslage, Beobachtungsauftrag, Evidenz und Take-away je Vorführung |
| `PRS-004` | L | Sprecherhinweise | Ablauf, Zeitbedarf, Stolperstellen, erwartete Abweichungen und Recovery je Demo |
| `PRS-005` | M | Teilnehmerunterlage | Lernziele, Schlüsselbegriffe, Übungen und Referenzen ohne interne Informationen |
| `PRS-006` | M | Visualisierungen | nur eigene, synthetische oder nachweislich zulässige Assets; Quellenstatus dokumentiert |
| `PRS-007` | M | Barrierefreiheit | Lesbarkeit, Kontrast, Alt-Text und sinnvolle Lesereihenfolge geprüft |
| `PRS-008` | M | Render- und Metadatenprüfung | Folien, Notes, Alt-Text, eingebettete Objekte, Vorschauen und Exportdateien geprüft |
| `PRS-009` | M | Zeitvarianten | Kurz-, Standard- und Vertiefungsdeck aus derselben fachlichen Basis ableitbar |
| `PRS-010` | M | Generalprobe | vollständiger Ablauf einschließlich Start-, Abbruch- und Recovery-Pfade getestet |

## 15. Querschnitt D – Test- und Qualitätsautomatisierung

### 15.1 Testklassen

| Klasse | Inhalt | Ausführung |
|---|---|---|
| Static | Pfade, Namensschema, Links, Pflichtdateien und verbotene Muster | bei jeder Änderung |
| Privacy | Text, Metadaten, Bilder, Logs, erwartete Resultate und Secrets | bei jeder Änderung |
| Contract | Demo-Phasen, Statusfelder, Quellen, Risiko und Cleanup | bei jeder Demoänderung |
| Syntax | T-SQL parse/deploy und Hilfswerkzeug-Syntax | bei jeder relevanten Änderung |
| Runtime Green | Setup, zweimalige Ausführung, Mitigation und Cleanup | automatisiert |
| Runtime Yellow | begrenzte Ressourcen-/Concurrency-Tests | geplant oder manuell freigegeben |
| Runtime Red | Infrastruktur- und Instanzänderungen | ausschließlich isoliertes Lab |
| Presentation | Render, Links, Fonts, Alt-Text und Metadaten | bei Präsentationsänderungen |

### 15.2 Versionsstrategie

- Für schnelle Entwicklung wird primär SQL Server 2025 verwendet.
- Vor Freigabe eines versionsübergreifenden Arbeitspakets wird die zutreffende Matrix 2019/2022/2025 ausgeführt.
- Feature-spezifische Demos müssen auf älteren Versionen kontrolliert mit begründetem `SKIP` reagieren.
- Betriebssystem- und editionsgebundene Pfade werden getrennt getestet.
- Container-Tags, Produktverfügbarkeit und Compatibility Levels werden vor Implementierung gegen aktuelle Primärquellen geprüft und nicht dauerhaft angenommen.

### 15.3 Qualitätsarbeitspakete

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `TST-001` | M | Repository-Strukturtest | alle verbindlichen Pfade, IDs und Links geprüft |
| `TST-002` | L | Privacy-Scanner | Text- und Office-Metadaten, Bilder, Secrets und reale Bezeichner soweit technisch erkennbar geprüft |
| `TST-003` | M | Demo-Contract-Linter | Pflichtphasen und Pflichtmetadaten automatisch geprüft |
| `TST-004` | L | SQL-Runtime-Harness | Versionserkennung, Setup, Ausführung, Timeout, Resultat und Cleanup standardisiert |
| `TST-005` | M | Idempotenz- und Cleanup-Test | zwei vollständige Läufe hinterlassen denselben definierten Ausgangszustand |
| `TST-006` | L | Versionsmatrix | Feature-Matrix, kontrollierte Skips und Ergebnisse zentral dokumentiert |
| `TST-007` | M | Concurrency-Harness | Sessions, Barrieren, Timeouts und Notfall-Cleanup deterministisch |
| `TST-008` | M | Performance-Erwartungsvertrag | relationale Erwartungen und Bandbreiten statt maschinenabhängiger Fixwerte |
| `TST-009` | M | Infrastruktur-Smoke-Test | Erstellen, Healthcheck, Demo-Bereitschaft, Reset und Entfernen geprüft |
| `TST-010` | M | Office-/PDF-Renderprüfung | visuelle Integrität, Links, Notes und Metadaten geprüft |

## 16. Querschnitt E – Dokumentation, Quellen und Betrieb

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `DOC-001` | M | zentrale Installationsanleitung | Voraussetzungen für Container und Hyper-V, ohne Secrets oder reale Pfade |
| `DOC-002` | M | Trainer-Runbook | Startreihenfolge, Zeitplan, Abbruch, Reset und bekannte Abweichungen |
| `DOC-003` | M | Teilnehmer-Runbook | sichere Ausführung grüner Demos und Beobachtungsaufträge |
| `DOC-004` | M | Troubleshooting | Symptom, Ursache, Prüfung und Recovery für erwartbare Labfehler |
| `DOC-005` | M | Versions- und Feature-Matrix | Produktversion, Compatibility Level, Edition, OS und Demostatus |
| `DOC-006` | S | Drittanbieterregister | Werkzeugtyp, Herstellerquelle, Lizenz, Version, Zweck und Alternative |
| `DOC-007` | M | Quellenpflegeprozess | veraltete Links, geändertes Produktverhalten und Revalidierungsdatum |
| `DOC-008` | S | Glossar | fachlich genaue Begriffe mit Verweisen zu Demos und Curriculum |

## 17. Umsetzungspakete und Parallelisierung

Nach Gate B können folgende Stränge unabhängig bearbeitet werden:

- Welle 3 und Welle 6 teilen Datenmodell- und Storage-Abhängigkeiten und sollten koordiniert werden.
- Welle 4 und Welle 5 können parallel laufen, verwenden aber gemeinsam `FWK-003` bis `FWK-005`.
- Welle 7 benötigt `FWK-006` und sollte vor ressourcenintensiven Multi-Session-Demos aus Welle 8 stabil sein.
- Welle 9 beginnt früh mit Pilotwerkzeugen, wird aber erst nach den Fachdemos vollständig abgeschlossen.
- Welle 10 kann nach Gate B parallel entwickelt werden; ihre endgültige Abnahme benötigt konkrete gelbe und rote Demos.
- Präsentationsarbeit kann nach Gate A beginnen, die finale Demo-Integration wartet auf Gate C.

Empfohlene Änderungseinheit ist ein klar begrenztes Framework-Modul oder eine vollständige Demo einschließlich Dokumentation und Tests. Große Themenwellen werden nicht als einzelner unprüfbarer Commit umgesetzt.

## 18. Priorisierte Startreihenfolge

1. `W0-001` Quellenmanifest und `W0-002` Privacy-Verfahren.
2. `W0-003` Aussagenregister und `W0-004` kritische Fachprüfung.
3. `CUR-001` bis `CUR-005` sowie Demo-ID-Vergabe.
4. `FWK-001` bis `FWK-012` als kleine, abhängige Pakete.
5. Vier Pilotdemos und Gate B.
6. Welle 2: vorhandene Beispiele klassifizieren und migrieren.
7. Wellen 3–6: Storage, Optimizer, Query Patterns und Indizes.
8. Wellen 7–9: Concurrency, Ressourcen und Diagnose.
9. Welle 10: vollständige Infrastrukturprofile und rote Demos.
10. Präsentationsintegration, Generalprobe und Releaseabnahme.

## 19. Wiederaufnahmeprotokoll

Bei jeder späteren Fortsetzung ist folgender Ablauf verbindlich:

1. Readme-Reihenfolge aus Abschnitt 2 vollständig lesen.
2. Aktuellen `main`-Commit, offene PRs und laufende Branches prüfen.
3. Im Backlog den obersten `READY`-Punkt wählen, dessen Abhängigkeiten erfüllt sind.
4. Zugehörige Demo-Katalogzeile, Quellen und letzte Testergebnisse lesen.
5. Datenschutzprüfung vor jeder Datei- oder Git-Operation durchführen.
6. Status auf `DESIGNED` oder `IMPLEMENTED` nur mit zugehörigem Artefakt ändern.
7. Relevante Tests ausführen und Ergebnisse ohne reale Umgebungsdaten dokumentieren.
8. Demo-Katalog, Backlog, Quellenregister und gegebenenfalls Entscheidungen gemeinsam aktualisieren.
9. Am Ende festhalten: letzter abgeschlossener Punkt, nächster ausführbarer Punkt, Blocker, Teststatus und betroffene Versionen.

### Übergabeformat

Jede Arbeitsübergabe enthält mindestens:

- letzter geprüfter Commit,
- bearbeitete IDs,
- aktueller Status je ID,
- geänderte Artefakte,
- ausgeführte Tests und Ergebnis,
- nicht ausgeführte Tests mit Begründung,
- bekannte Risiken oder fachliche Unsicherheiten,
- nächster ausführbarer Schritt,
- explizite Blocker oder benötigte Entscheidungen.

## 20. Aktueller Ausführungsmarker

| Feld | Stand |
|---|---|
| Repository-Struktur | abgeschlossen |
| Fachliche Demos | noch nicht implementiert |
| Infrastruktur-Labs | noch nicht implementiert |
| Präsentationsbereinigung | noch nicht begonnen |
| Nächstes Arbeitspaket | `W0-001` – datenschutzsicheres Quellenmanifest |
| Danach | `W0-002`, `W0-003`, `W0-004` |
| Aktueller Blocker | Originalquellen dürfen erst nach Privacy-Prüfung als Arbeitsmaterial übernommen oder neu gespeichert werden |

## 21. Abschluss-Checkliste des Gesamtprojekts

- [ ] Alle Arbeitspakete besitzen einen Endstatus mit Evidenz.
- [ ] Alle freigegebenen Aussagen sind quellen- oder messungsbasiert.
- [ ] Der Demo-Katalog deckt Curriculum und Präsentation vollständig ab.
- [ ] Alle Demos erfüllen den Demo-Vertrag oder dokumentieren begründete Ausnahmen.
- [ ] Alle Beispieldaten und sichtbaren Bezeichnungen sind synthetisch.
- [ ] Präsentationen enthalten keine Firmeninformationen, Logos oder realen Metadaten.
- [ ] Container- und Hyper-V-Labs besitzen Preflight, Setup, Reset, Cleanup und Recovery.
- [ ] Die zutreffende SQL-Server-Matrix ist erfolgreich oder besitzt begründete Feature-Skips.
- [ ] Grüne, gelbe und rote Demos sind sicher getrennt.
- [ ] Trainer- und Teilnehmermaterial stimmen mit den ausführbaren Demos überein.
- [ ] Quellen, Drittanbieter-Abhängigkeiten und Lizenzen sind nachvollziehbar.
- [ ] Eine Generalprobe des vollständigen Schulungsablaufs wurde dokumentiert.
- [ ] Releaseartefakte wurden auf Inhalt, Metadaten, Links und Wiederherstellbarkeit geprüft.
