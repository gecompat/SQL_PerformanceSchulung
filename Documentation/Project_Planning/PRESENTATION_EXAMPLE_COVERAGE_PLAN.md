# Folienbezogener Beispielabdeckungsplan

| Merkmal | Wert |
|---|---|
| Status | `PLANNED` |
| Stand | 2026-08-29 |
| Masterdeck | `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx` |
| Masterdeck-SHA-256 | `85bd14e4fc91d148889e9ebaa7128f6e1a213366f389aa6e2053f46cc0890ad3` |
| Umfang | 102 Folien; Profile `BASIS`, `STANDARD` und `VERTIEFUNG` |
| Inhaltsgrundlage | [Folien- und Aussagenregister](../Inventories/SLIDE_STATEMENT_REGISTER.md), [Traceability-Matrix](../Curriculum/TRACEABILITY_MATRIX.md), [Variantenmanifest](../../Presentations/variants/presentation_variants.json) |
| Ausführungsgrundlage | [Demo-Katalog](../Demo_Catalog/README.md), [Master-Umsetzungsplan](MASTER_IMPLEMENTATION_PLAN.md), [Operatoren-Labor](LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#36-sechste-fachliche-kandidatengruppe--execution-plan-operatoren-labor) |

## 1. Ziel und Geltung

Am Ende der Schulung sollen die Teilnehmer jede technisch relevante
Folienaussage mit einer beobachtbaren Daten-, Abfrage-, Plan-, Concurrency- oder
Diagnosekonstellation verbinden können, weil dieselbe fachliche Kausalität in
Folie, Sprecherhinweis und reproduzierbarer Demo wiederverwendet wird.

Dieser Plan legt noch keine neuen Runtimeartefakte an und hebt keinen Status an.
Er bestimmt für die spätere Entwicklung:

- welche Folien gemeinsam durch ein Beispielbündel erklärt werden;
- welche kanonische Demo-ID Eigentümer der Daten und der Kernevidenz ist;
- welche vorhandene Demo unverändert wiederverwendet wird;
- welche zusätzliche Phase tatsächlich noch entwickelt werden muss;
- welche Grenze eine redundante Parallel-Demo verhindern soll.

Die operative Reihenfolge aus `NEXT_DEVELOPMENT_WAVES.md` bleibt unverändert.
Der vorliegende Plan ist eine Auswahl- und Konsolidierungsgrundlage für spätere
kleine Demo-PRs.

## 2. Vollständigkeit und Auswahlregel

Der geprüfte Foliensatz enthält 102 Folien. 87 Positionen transportieren eine
technische, empirische oder anwendungsbezogene methodische Konstellation und
werden in Abschnitt 4 einem Beispielbündel zugeordnet. Folgende 15 Positionen
erhalten bewusst kein eigenes Script:

- Titel, Modultrenner und Abschluss: Folien 1, 7, 19, 36, 48, 63, 71 und 102;
- Wissenskontrollen: Folien 18, 35, 47, 62, 70 und 80; sie verwenden die
  unmittelbar zuvor behandelte Evidenz;
- Quellenfolie 83; sie bleibt Referenz und erzeugt keine Runtimebehauptung.

Die Transferfolie 82 verwendet den Diagnosefall aus `DGN-007` und bleibt damit
trotz ihrer Übungsrolle in der fachlichen Abdeckung enthalten.

Für die Planung gelten vier Entscheidungen:

| Entscheidung | Bedeutung |
|---|---|
| `WIEDERVERWENDEN` | Ein vorhandener Demovertrag deckt die Folienaussage bereits ab. Es entsteht kein zweites Setup oder Deck-spezifisches Script. |
| `ERGÄNZEN` | Ein vorhandenes Bündel erhält später genau die fehlende Phase oder Gegenprobe; Datenmodell und Evidenzpfad bleiben gemeinsam. |
| `PLANEN` | Die kanonische Demo-ID existiert, aber ein ausführbarer Detailvertrag fehlt noch. |
| `KEIN_EIGENES_SCRIPT` | Die Folie fasst andere Beispiele zusammen oder beschreibt Methode, Eligibility beziehungsweise Transfer ohne eigenen Workload. |

## 3. Regeln gegen Redundanz

1. Es gibt keine Demo pro Folie. Mehrere Folien derselben Kausalkette verwenden
   ein gemeinsames Beispielbündel.
2. `BASIS`, `STANDARD` und `VERTIEFUNG` verwenden dasselbe Setup. Die Profile
   unterscheiden Erklärungstiefe und sichtbare Phasen, nicht Datenbestand oder
   fachliches Ergebnis.
3. Eine Folie besitzt genau einen primären Evidenzeigentümer. Weitere Demo-IDs
   dürfen nur eine klar getrennte Vertiefung oder bereits erzeugte Evidenz
   referenzieren.
4. Bereits `VALIDATED`e Demos werden nicht neu implementiert. Fehlende
   Folienabdeckung wird durch README-, Manifest- oder Katalogzuordnung ergänzt.
5. Der `FWK-003`-Datenaufbau darf als Parameterprofil wiederverwendet werden,
   wird aber je Demo-ID und Run-Token in der eigenen `FWK-002`-markierten
   Datenbank erzeugt. Es gibt keine mutable Gemeinschaftsdatenbank.
6. Eine Beispielphase verändert genau eine relevante Achse: Datenverteilung,
   Kardinalität, Ordnung, Zeilenbreite, Index, Compatibility Level,
   Datenbankoption, Isolation oder Ressourcenprofil.
7. Querliegende Folienaussagen verwenden vorhandene Messungen. Beispielsweise
   erzeugt die Wait-Übersicht auf Folie 75 keinen neuen künstlichen
   `WRITELOG`-Fall, sondern verwendet `STL-009`.
8. Wissenskontrollen erhalten erwartete Beobachtungsfragen, aber keine
   duplizierten SQL-Dateien.
9. Neue dauerhafte Kennungen werden nur über die zentrale v2-Registry
   registriert. Dieser Plan verwendet ausschließlich bestehende Demo-, Claim-,
   Lernziel- und SlideKey-Kennungen.

## 4. Konsolidierte Beispielabdeckung

### 4.1 Einordnung, Diagnosemethode und Versionen

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 2–4, 78–79, 81–82 / `CLM-002` bis `CLM-004`, `CLM-078`, `CLM-079`, `CLM-081`, `CLM-082` | `BASIS` | `DGN-001`, später `DGN-007` | Ein vorhandener fachlicher Fehlerfall wird als Outside-in-Diagnose geführt: Symptom und Messfenster, Systemsignal, Query und Actual Plan, eine Hypothese, genau eine Änderung, identischer A/B-Vergleich und Rückfall. | `DGN-007` erzeugt keinen neuen Root Cause, sondern orchestriert Evidenz eines bereits implementierten Beispiels. `DGN-001` stellt nur den Messvertrag bereit. | `PLANEN` |
| 5, 76–77 / `CLM-005`, `CLM-076`, `CLM-077` | `STANDARD`, `BASIS` | `DGN-002`, `DGN-003`, `DGN-005` | Derselbe markergebundene Querytext wird live über Request-/Task-DMVs, historisch über Query Store und ereignisbezogen über eine begrenzte XE-Session beobachtet. Scope, Zeitbezug, Retention und Capture-Grenze werden direkt verglichen. | Die drei Diagnosepfade verwenden denselben Querymarker. Keiner erzeugt einen eigenen fachlichen Performancefehler. | `ERGÄNZEN` |
| 6, 34 / `CLM-006`, `CLM-034` | `STANDARD`, `VERTIEFUNG` | vorhandene Featuredemos | Eine read-only Eligibility-Matrix übernimmt Engine-Version, Compatibility Level, Datenbankkonfiguration, Query-Store-Zustand und Planbeleg aus `QRY-008`, `QRY-009`, `OPT-009`, `OPT-010`, `OPT-014`, `OPT-017` und `CON-008`. | Keine IQP-Sammeldemo und kein eigener Feature-Workload. Die Matrix darf nur belegte Ergebnisse der jeweiligen Eigentümer anzeigen. | `KEIN_EIGENES_SCRIPT` |

### 4.2 Storage, Pages und Transaction Log

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 8–9, 17 / `CLM-008`, `CLM-009`, `CLM-017` | `BASIS`, `STANDARD` | `STL-005` | Markergebundene Testdatenbank mit Data File, Log File und optional zweiter Data-File-/Filegroup-Phase: Objektplatzierung, Allocation und kontrolliertes Wachstum beobachten; Daten- und Logwachstum sowie IFI-Grenze getrennt erklären. | VLF-Wirkung wird aus `STL-008`, Commit-/Log-Flush-Wirkung aus `STL-009` referenziert. `STL-005` wiederholt diese Lasten nicht. | `PLANEN` |
| 10 / `CLM-010` | `BASIS` | `STL-004` | Eine kleine Rowstore-Tabelle wird von Objekt und Partition über Allocation Unit bis zu Page und Extent verfolgt; Page Count und unterstützte Page-Metadaten bilden die Evidenzkette. | Keine eigene Row-Width- oder Overflow-Demo; diese gehören `STL-001` und `STL-002`. | `PLANEN` |
| 11–13 / `CLM-011` bis `CLM-013` | `STANDARD`, `VERTIEFUNG` | `STL-001`, `STL-002` | `STL-001` erzeugt eine Zeilenbreitenleiter für Fixed-, Variable- und NULL-Anteile. `STL-002` verschiebt dieselben fachlichen Nutzdaten kontrolliert zwischen `IN_ROW_DATA`, `ROW_OVERFLOW_DATA` und `LOB_DATA`. | Beide verwenden die Metadatenabfrage aus `STL-004` als Helfer; sie kopieren dessen Objekt-zu-Page-Lernpfad nicht. | `PLANEN` |
| 14–15 / `CLM-014`, `CLM-015` | `BASIS` | `STL-006` | Identische Query und Ergebnismenge unter dokumentierter Warm-up-Regel; Logical Reads bleiben vergleichbar, Physical Reads und Read-ahead werden nur in bestätigter Wegwerfinfrastruktur als Cold/Warm-Gegenprobe erhoben. | Kein allgemeiner Benchmark und keine Cacheleerung auf geteilter Instanz. `DGN-001` liefert den A/B-Messrahmen. | `PLANEN` |
| 16 / `CLM-016` | `STANDARD` | `STL-007` | Eine begrenzte Transaktion weist Log Records und Log Bytes vor Commit beziehungsweise Rollback nach; eine zweite Phase trennt Log Flush von Checkpoint und Endzustand. | Commit-Batching und `WRITELOG` bleiben ausschließlich in der validierten Demo `STL-009`. | `PLANEN` |

### 4.3 Query Processing, Pläne und Optimizer

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 20–22, 26–27 / `CLM-020` bis `CLM-022`, `CLM-026`, `CLM-027` | `BASIS`, `STANDARD` | `OPT-001`, `OPT-015` | Ein selektiver Zugriff mit kontrollierter Schätzabweichung zeigt Bindung/Optimierung/Ausführung, Estimated und Actual Rows, Datenfluss, Ausführungsanzahl, Prädikate, Warnungen und Planproperties. Die Microqueries des Operatoren-Labors werden als kleine Phasen desselben Eigentümers eingebunden. | `OPT-015` bleibt die validierte Properties-Vertiefung. Es entsteht kein zweiter allgemeiner Planlese-Runner. | `ERGÄNZEN` |
| 23–25 / `CLM-023` bis `CLM-025` | `STANDARD` | `OPT-002`, `OPT-003`, `OPT-004` | `OPT-002` erklärt Header, Histogramm und Density; `OPT-003` belegt Sampling und Skew. `OPT-004` ergänzt korrelierte Spalten, Mehrspaltenstatistik sowie vertrauenswürdige und nicht vertrauenswürdige Constraint-Gegenprobe. | Die drei Demos verwenden ein abgestimmtes `FWK-003`-Profil, besitzen aber getrennte Aussagen. `OPT-004` wiederholt keine Histogrammanatomie. | `ERGÄNZEN` |
| 28 / `CLM-028` | `STANDARD` | `OPT-012` | Identische Joinergebnisse unter kleiner indexierter Outer-Menge, großen unsortierten Inputs und geordneten Inputs; Nested Loops, Hash und Merge werden natürlich oder als klar markierte querylokale Gegenprobe gezeigt. Adaptive Join bleibt eine optionale Eligibility-Phase. | Bitmapfilter gehört nur zur Parallelismusvertiefung; Spills gehören `OPT-013`. Kein Join wird als universell überlegen bezeichnet. | `PLANEN` |
| 29–30 / `CLM-029`, `CLM-030` | `VERTIEFUNG` | `OPT-014`, `OPT-013` | `OPT-014` zeigt Required, Desired, Requested, Granted und Used Memory sowie Under-/Overgrant und Feedback über Wiederholungen. `OPT-013` bleibt der validierte kontrollierte Sort-Spill mit TempDB- und Warnungsevidenz. | `OPT-014` erzeugt keinen zweiten Spill-Pilot; `OPT-013` behauptet keinen Instanz-RAM-Mangel. | `ERGÄNZEN` |
| 31 / `CLM-031` | `VERTIEFUNG` | `OPT-017`, `RES-002` | Das vorhandene balancierte und konzentrierte Datenprofil zeigt Exchanges, Actual DOP, Threadarbeit und Skew. Eine spätere `RES-002`-Phase darf nur DOP-/Overhead-Gegenproben auf demselben Profil ergänzen. | Skew und Exchange-Nachweis bleiben Eigentum von `OPT-017`; `RES-002` baut keinen parallelen Parallelfall nach. | `WIEDERVERWENDEN` |
| 32–33, 84–86, 88 / `CLM-032`, `CLM-033`, `ADV-CLM-013` bis `ADV-CLM-016` | `VERTIEFUNG` | `QRY-013`, `OPT-007`, `OPT-008` | Das validierte `QRY-013` trennt Sessionkontext und Parameterdimension. `OPT-007` ergänzt nur Literal-Storm, Cache-Use-Counts und objektgebundene Invalidierung. `OPT-008` ergänzt nur die umgekehrte Erstkompilierung mit seltenem und häufigem Wert. | SET-Options-Beispiel bleibt ausschließlich `QRY-013`; PSP bleibt ausschließlich `OPT-009`; `OPT-007` leert keinen Instanzcache. Folie 87 gehört primär `QRY-004`. | `ERGÄNZEN` |

### 4.4 Query Patterns und IQP-Vertiefung

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 37–39 / `CLM-037` bis `CLM-039` | `BASIS`, `STANDARD` | `QRY-001`, `QRY-002`, `QRY-003` | `QRY-001` bleibt die validierte Funktion-auf-Spalte-/Range-Gegenprobe. `QRY-002` zeigt beide Richtungen einer impliziten Konvertierung. `QRY-003` vergleicht künstliches Tagesende und halboffenes Intervall für `datetime` und `datetime2(7)`. | Alle drei verwenden eine gemeinsame fachliche Zeitachse, aber jede Demo verändert nur SARGability, Typkonvertierung oder Intervallsemantik. | `ERGÄNZEN` |
| 40, 87, 89–93 / `CLM-040`, `ADV-CLM-016` bis `ADV-CLM-018` | `VERTIEFUNG` | `QRY-004` | Der validierte Schnitt vergleicht statischen Catch-all-Text, `OPTION (RECOMPILE)` und positiv gelistetes, parameterisiertes dynamisches SQL unter identischer Datenverteilung und Ergebnischecksumme. | Keine neue Foliendemo. Die Sprechernotiz muss die in der Matrix beobachtete `WARN_EMPIRICAL_VARIANCE` statt eines garantierten Read-Vorteils wiedergeben. | `WIEDERVERWENDEN` |
| 41–42 / `CLM-041`, `CLM-042` | `STANDARD` | `QRY-008` | Eine CTE wird einmal und mehrfach referenziert; Actual Executions und optionale Spoolform werden beobachtet. Dieselbe Zwischenmenge wird als `#temp` und Table Variable unter CL 140/150 mit kleiner und großer erster Befüllung verglichen. | Der Spill-Mechanismus aus `OPT-013` wird nur als bestehende Evidenz referenziert. `QRY-008` behauptet keine feste Zeilengrenze. | `PLANEN` |
| 43 / `CLM-043` | `STANDARD` | `QRY-009` | Ergebnisgleiche iTVF, geeignete MSTVF und zwei Scalar-UDF-Varianten: CL-/Eligibility-Gegenproben, tatsächliche Integration beziehungsweise Inlining und Plan-/Parallelitätsgrenzen. | Eine Funktion pro Mechanismus, keine separaten Demos für iTVF, MSTVF und UDF. Ausbleibende Eligibility ist ein kontrollierter Skip. | `PLANEN` |
| 44–45 / `CLM-044`, `CLM-045` | `VERTIEFUNG` | `QRY-012` | Getrennte Phasen: lokale Partition-Elimination mit ableitbarem und verdecktem Partitionsprädikat; anschließend nur bei freigegebener Mehrinstanztopologie Remote Pushdown mit kleinem und lokal gefiltertem Resultset. | Partitionierung und Remotezugriff teilen die Demo-ID, aber weder Setup noch Safety-Pfad. JSON/XML/String-Kosten werden nicht in diese Folienphasen gemischt. | `PLANEN` |
| 46 / `CLM-046` | `STANDARD` | `STL-001`, `QRY-002`, `IDX-002`, `QRY-011` | Die Folie verwendet vier bereits zugeordnete Gegenproben: Zeilenbreite, Typgleichheit an Filter-/Joingrenzen, Locatorbreite und deterministische berechnete Spalte. | Kein neues „Datenmodell“-Sammelscript; die Folie verbindet Resultate der vier Eigentümer. | `KEIN_EIGENES_SCRIPT` |
| 94–97 / `ADV-CLM-019` | `VERTIEFUNG` | `OPT-009` | Die validierte Demo zeigt eine Planform in beiden Kompilierungsreihenfolgen, danach Dispatcherplan, Query Variants, Kardinalitätsgrenzen, Eligibility und querylokale Abwahl. | Kein zweiter Parameter-Skew-Aufbau in `OPT-008`; dieser endet vor der PSP-Mechanik. | `WIEDERVERWENDEN` |
| 98–101 / `ADV-CLM-020` | `VERTIEFUNG` | `OPT-010` | Die validierte Demo verwendet bewusst gleichverteilte Daten und trennt optionales NULL-Prädikat, Dispatcher-/Variantenevidenz, Ausschlussgründe und Abwahl von PSP. | Kein Skew und keine Wiederholung des dynamischen SQL aus `QRY-004`. | `WIEDERVERWENDEN` |

### 4.5 Rowstore und Columnstore

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 49, 51 / `CLM-049`, `CLM-051` | `BASIS`, `STANDARD` | `IDX-001` | Fachlich identische Heap- und Clustered-Table mit gleichwertigem Nonclustered Index: RID versus Clustering Key als Locator, Punkt-/Bereichszugriff sowie RID-/Key-Lookup. | Die Operatoren-Labor-Microqueries verweisen auf `IDX-001`; sie legen keine zweite Heap-/Clustered-Datenbasis an. | `PLANEN` |
| 50, 55 / `CLM-050`, `CLM-055` | `STANDARD` | `IDX-002` | Schmaler eindeutiger gegen breiten nicht eindeutigen Clustered Key; B+Tree-Höhe, Page Count, Nonclustered-Indexbreite und beobachtbare Uniqueifier-Wirkung vergleichen. | Locatorart selbst bleibt in `IDX-001`; `IDX-002` untersucht ausschließlich Breite, Eindeutigkeit und Folgekosten. | `PLANEN` |
| 52–53 / `CLM-052`, `CLM-053` | `BASIS`, `STANDARD` | `IDX-003`, `QRY-011` | `IDX-003` vergleicht Key-Reihenfolge und INCLUDE bei Equality, Range, Sort und Gruppierung. `QRY-011` übernimmt ausschließlich Filtered Index und Predicate Implication einschließlich SET-/Computed-Column-Gegenprobe. | INCLUDE und Filtered Index werden nicht in beiden Demos implementiert. | `PLANEN` |
| 54 / `CLM-054` | `STANDARD` | `IDX-004` | Selektivitätsleiter auf einem nicht abdeckenden Index: tatsächliche Umschaltung von Seek plus Lookup zu Scan beobachten; Covering Index als Gegenprobe. | Keine feste Tipping-Point-Prozentzahl. Lookup-Grundmechanik wird aus `IDX-001` übernommen. | `PLANEN` |
| 56–58 / `CLM-056` bis `CLM-058` | `BASIS`, `VERTIEFUNG` | `IDX-005`, `IDX-006` | `IDX-005` bewertet zwei überlappende Missing-Index-Vorschläge gegen Read-Gewinn, Größe und begrenzte DML-Kosten. `IDX-006` bleibt die validierte Page-Split-, Density-, Fragmentation- und Maintenance-Gegenprobe. | `IDX-005` erzeugt keine Fragmentierungslast; `IDX-006` leitet keine neuen Indexvorschläge ab. | `ERGÄNZEN` |
| 59–61 / `CLM-059` bis `CLM-061` | `VERTIEFUNG` | `IDX-009`, `IDX-010` | `IDX-009` zeigt kleine Inserts im Delta Store, geschlossene/komprimierte Rowgroups und Delete Bitmap. `IDX-010` bleibt die validierte Segment-Elimination-, Datenordnungs- und Rowgroup-Qualitätsdemo. | Segment Elimination und Maintenance werden nicht in `IDX-009` nachgebaut; Delta-Store-Lifecycle wird nicht in `IDX-010` verdoppelt. | `ERGÄNZEN` |

### 4.6 Concurrency, Isolation und TempDB

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 64–65 / `CLM-064`, `CLM-065` | `BASIS`, `STANDARD` | `CON-001`, `CON-002`, `CON-003` | Gemeinsames synthetisches Kontomodell, getrennte Phasen: `CON-001` für Dirty/Non-repeatable/Phantom/Lost Update, `CON-002` für Lockhaltedauer und Key-Range-Schutz, `CON-003` für RCSI-Statement-, SNAPSHOT-Transaction-Sicht und Updatekonflikt. | Jedes Phänomen besitzt genau einen Eigentümer. Die drei IDs teilen nur Schema und fachliche Endzustandsassertion. | `PLANEN` |
| 66–67 / `CLM-066`, `CLM-067` | `BASIS`, `STANDARD` | `CON-004`, `CON-006` | Die validierte Blocking Chain zeigt Head Blocker und gerichtete Wartekette; die validierte Deadlock-Demo zeigt einen Zyklus, Opferfehler 1205 und Deadlock Graph. | Kein gemeinsamer Mehrsession-Runner, der beide Fälle gleichzeitig erzeugt; Vergleich erfolgt über normalisierte Evidenz. | `WIEDERVERWENDEN` |
| 68 / `CLM-068` | `VERTIEFUNG` | `CON-009`, `OPT-013`, `CON-003`, später `CON-007` | Eine read-only Kostenübersicht verbindet vorhandene Evidenz für Tempobjekte/interne Objekte, Spill, klassischen Version Store und später ADR/Persistent Version Store. `CON-009` bleibt Eigentümer der TempDB-Kostenklassen. | Keine TempDB-Sammellast. Jeder Kostenpfad wird ausschließlich in seiner fachlichen Eigentümerdemo erzeugt. | `ERGÄNZEN` |
| 69 / `CLM-069` | `VERTIEFUNG` | `CON-008` | SQL Server 2025: identische begrenzte DML-Workload vor und nach Optimized Locking; TID-Lock, LAQ-Eligibility, ADR-/RCSI-Voraussetzungen, Lockanzahl und Endzustand beobachten. | Schema Locks, TempDB-DML und allgemeine Isolation werden nicht wiederholt. Fehlende Eligibility bleibt kontrollierter Skip. | `PLANEN` |

### 4.7 CPU, Memory, I/O, Waits und Diagnose

| Folien / Claims | Profile | Primärer Eigentümer | Geplante Konstellation und Kernevidenz | Redundanzgrenze | Entscheidung |
|---|---|---|---|---|---|
| 72 / `CLM-072` | `BASIS` | `RES-001`, `OPT-017`, `RES-007` | Begrenzte CPU-lastige Query mit Worker-/Scheduler-Evidenz; parallele CPU-gegen-Elapsed-Eigenschaft aus `OPT-017`; Request-/Task-Wait-Scope aus `RES-007`. | `RES-001` erzeugt keinen zweiten Parallel-Skew- oder Wait-Scope-Fall. | `ERGÄNZEN` |
| 73 / `CLM-073` | `STANDARD` | `RES-007` | Die validierte Demo trennt Request-, Task- und Instanzscope als zeitbezogene Deltas und enthält die passende Gegenprobe. | Query-Store-Wait-Historie wird erst durch `DGN-003` ergänzt, nicht in `RES-007` nachgebaut. | `WIEDERVERWENDEN` |
| 74 / `CLM-074` | `VERTIEFUNG` | `RES-003`, `OPT-014` | Mehrere begrenzte Sessions konkurrieren mit derselben grantfähigen Queryform; wartende und laufende Grants, Requested/Granted, Queue-Dauer und `RESOURCE_SEMAPHORE` werden zeitgleich erfasst. | Querylokaler Grant-Lifecycle und Feedback bleiben `OPT-014`; `RES-003` erzeugt nur die rote Concurrency-/Instanzdruck-Phase. | `PLANEN` |
| 75 / `CLM-075` | `BASIS` | `RES-005`, `STL-009`, `RES-007`, `RES-006` | Folienvergleich aus Eigentümerdemos: `PAGEIOLATCH_*` gegen `PAGELATCH_*`, validiertes `WRITELOG`, validiertes `ASYNC_NETWORK_IO` und File-Latency-Deltas. | Keine Wait-Sammeldemo. Ein Signal wird nur dort künstlich erzeugt, wo Safety, Infrastruktur und Ursachenbezug vollständig kontrolliert sind. | `KEIN_EIGENES_SCRIPT` |
| 76 / `CLM-076` | `BASIS` | `DGN-003` | Markerquery erhält mindestens zwei Plan-/Runtimezustände; Query-, Plan-, Runtime- und verfügbare Wait-Historie werden im definierten Intervall nachgewiesen. Plan Forcing bleibt `DGN-004`. | Keine XE-Ereignissammlung und kein Live-DMV-Monitor in dieser Demo. | `PLANEN` |
| 77 / `CLM-077` | `BASIS` | `DGN-002`, `DGN-005` | Derselbe Markerfall wird während der Ausführung über Session/Request/Task-DMVs und ereignisbezogen über verfügbarkeitsgeprüfte XE-Events, Actions und begrenzten `ring_buffer` beobachtet. | Query-Store-Historie bleibt `DGN-003`; XE und DMV liefern keine parallelen Kopien derselben historischen Aussage. | `PLANEN` |

### 4.8 Vorgeschlagene spätere Manifest-Ergänzungen

Das aktuelle Variantenmanifest enthält bei 22 fachlich relevanten Folien noch
keine Demo-ID. Für 18 davon ist nach der Konsolidierung ein primärer Eigentümer
bestimmt. Die Zuordnung wird erst im jeweiligen Demo-PR in Manifest,
Aussagenregister, Traceability und Katalog übernommen:

| Folien | SlideKeys | Primärer Eigentümer | Begründung |
|---|---|---|---|
| 2–3 | `SLD-M00-002`, `SLD-M00-003` | `DGN-001` | gemeinsamer Mess- und A/B-Vertrag für Latenz, Ressourcen, Nebenläufigkeit und vergleichbare Bedingungen |
| 4–5 | `SLD-M00-004`, `SLD-M00-005` | `DGN-007` | Capstone verbindet Diagnosezyklus und Auswahl der Evidenzquelle; `DGN-002`, `DGN-003` und `DGN-005` bleiben Zulieferer |
| 9, 17 | `SLD-M01-003`, `SLD-M01-011` | `STL-005` | Filegroup-/Placement- und Growth-Grenze gehören zum bestehenden Files-/Filegroups-Bündel |
| 11 | `SLD-M01-005` | `STL-001` | Row-Aufbau und nutzbarer Page-Platz sind Voraussetzung der Zeilenbreitenleiter |
| 13 | `SLD-M01-007` | `STL-002` | In-row-, Row-overflow- und LOB-Übergang ist die Kernaussage des Bündels |
| 20–21 | `SLD-M02-002`, `SLD-M02-003` | `OPT-001` | Compile-/Optimize-/Execute-Kontext und begrenzte Optimierersuche werden am allgemeinen Planlesefall erklärt |
| 25 | `SLD-M02-007` | `OPT-004` | Constraint- und Eindeutigkeitsinformation ist Teil der geplanten Korrelations-/Optimizerwissen-Demo |
| 50, 55 | `SLD-M04-003`, `SLD-M04-008` | `IDX-002` | B+Tree-Höhe, Schlüsselbreite, Eindeutigkeit und Uniqueifier werden gemeinsam verglichen |
| 56 | `SLD-M04-009` | `IDX-005` | Read-Gewinn und DML-/Speicher-/Wartungskosten werden als Indexportfolio bewertet |
| 78 | `SLD-M06-008` | `DGN-007` | Outside-in-Ablauf ist die Struktur des Capstone-Falls |
| 79, 81 | `SLD-M06-009`, `SLD-M07-001` | `DGN-001` | reproduzierbarer Vergleich und Leitprinzipien stammen aus demselben Messvertrag |
| 82 | `SLD-M07-002` | `DGN-007` | Transferaufgabe verwendet den Capstone, ohne einen neuen Root Cause zu erzeugen |

Die Folien 6 (`SLD-M00-006`), 34 (`SLD-M02-016`), 46
(`SLD-M03-011`) und 75 (`SLD-M06-005`) bleiben absichtlich ohne primäre Demo-ID.
Sie konsolidieren Feature-, Modellierungs- beziehungsweise Wait-Evidenz mehrerer
Eigentümer und erhalten deshalb nur dokumentierte Verweise, keine künstliche
Sammeldemo.

## 5. Wissenskontrollen und Transfer ohne Parallelskripte

| Folie | Verwendete Evidenz | Erwartete Anwendung |
|---:|---|---|
| 18 | `STL-001`, `STL-005`, `STL-006`, `STL-009` | unveränderten Plan von Cachezustand, Seitenzahl, Storagekonkurrenz und Log-/Growth-Ereignissen abgrenzen |
| 35 | `OPT-001`, `OPT-013`, `OPT-014`, `RES-003` | bei Spill zuerst Schätzung, Grant, Konkurrenz und Row Width prüfen |
| 47 | `QRY-001`, `IDX-003`, `IDX-004` | SARGability von Selektivität, Coverage, Lookup-Kosten und Kostenentscheidung trennen |
| 62 | `IDX-003`, `IDX-005`, `IDX-006` | neuen Index nur aus priorisierter Query, Read-Gewinn und DML-/Betriebskosten begründen |
| 70 | `CON-002`, `CON-003`, `CON-004` | Isolation, Datenbankoption, Transaktion und Lock Resource vor einer Maßnahme bestimmen |
| 80 | `RES-003`, `RES-006`, `RES-007`, `CON-004` | fehlende Zeit entlang Waits, Blocking, I/O, Grant und Clientkonsum eingrenzen |
| 82 | `DGN-001`, später `DGN-007` | aus einem vorhandenen Symptom Messwerte, Hypothese, eine Änderung und Vergleich ableiten |

## 6. Vertrag für die spätere Scriptgenerierung

Wenn ein in Abschnitt 4 als `PLANEN` oder `ERGÄNZEN` markierter Schnitt zur
Entwicklung freigegeben wird, entstehen die Artefakte ausschließlich im
kanonischen Demoordner der bestehenden ID. Der Standardpfad lautet:

```text
00_Preflight.sql
10_Setup.sql
20_Baseline.sql
30_Demonstration.sql
40_Observation.sql
50_Mitigation.sql
60_Comparison.sql
90_Cleanup.sql
README.md
manifest.json
```

Nicht benötigte Phasen dürfen nur mit Begründung entfallen. Für kleine
Operator-Microqueries können mehrere klar benannte Abschnitte in einer Phase
liegen; sie erhalten keinen eigenen Demoordner.

README und Manifest dokumentieren mindestens:

- primäre SlideKeys, Claims, Lernziele und Quellen;
- zusätzlich wiederverwendete Folien ohne zweite Eigentümerschaft;
- Datenprofil, veränderte Achse und identische Ergebnisassertion;
- erwartete Plan-, DMV-, Query-Store-, XE- oder Storageevidenz;
- zulässige Planvarianten und kontrollierte `FWK-012`-Skips;
- Safety, Sessions, Ausführungspfad, Zeitbudget und Kill-Switch;
- SQL Server 2019/2022/2025, Compatibility Level und Featuregrenzen;
- Reset, unabhängiges Cleanup und verbleibenden Endzustand;
- Anwendererklärung: Was ist sichtbar, warum ist es plausibel und welche
  universelle Schlussfolgerung ist ausdrücklich unzulässig.

## 7. Empfohlene spätere Entwicklungsfolge

Diese Folge gilt nur innerhalb der folienbezogenen Abdeckungsarbeit und ordnet
sich den aktiven Entwicklungswellen unter:

1. Manifest- und README-Zuordnungen für bereits `VALIDATED`e Demos ergänzen;
2. grüne Einzelsession-Grundlagen mit breiter Folienwirkung entwickeln:
   `STL-001`, `STL-002`, `STL-004`, `OPT-001`, `OPT-004`, `OPT-012`,
   `QRY-002`, `QRY-003`, `QRY-008`, `QRY-009`, `IDX-001` bis `IDX-005`,
   `IDX-009`, `DGN-001` und `DGN-002`;
3. bereits implementierte, aber noch nicht vollständig runtimefreigegebene
   Eigentümer stabilisieren, insbesondere `QRY-004`, `OPT-017` und `CON-009`;
4. Query Store und XE mit `DGN-003` und `DGN-005` runtimevalidieren;
5. gelbe, rote, Mehrsession-, Provider- und versionsgebundene Schnitte erst nach
   ihrem Detaildesign und Safety-Gate umsetzen;
6. `DGN-007` zuletzt als Capstone aus bereits validierten Evidenzpfaden bauen.

## 8. Abnahmegrenze

Dieser Plan gilt als repository-verankert, wenn Deck-Hash, Registry,
Kontinuität, Curriculum, Variantenmanifest und Privacy statisch grün sind. Das
ist keine Runtimefreigabe der beschriebenen Demos.

Eine spätere Folienaussage gilt erst dann als praktisch belegt, wenn ihr
primärer Eigentümer den vollständigen Demo-Vertrag und die zutreffende
Runtime-Matrix erfüllt. Kontrollierte Warnungen und Skips bleiben
wahrheitsgetreu sichtbar und werden nicht in `PASS` umgeschrieben.
