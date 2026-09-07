# Demo-Walkthroughs – Schritt-für-Schritt-Erklärungen aller Fachdemos

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `TSK-001` (registriert in `.ai/identity/registry.json`) |
| Status | `VALIDATED` (statisch; jede beschriebene Demo besitzt den zutreffenden Runtime-Matrixnachweis) |
| Stand | 2026-09-07 |
| Geltungsbereich | alle 22 runtimevalidierten Fachdemos |
| Ausführung | `Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md` (vorhandene Instanz) und `Documentation/HowTo/CONTAINER_QUICKSTART.md` (Docker/Podman) |
| Quelle jeder Erklärung | die implementierten SQL-Skripte, `manifest.json` und das Demo-README derselben Demo |

## Zweck dieses Dokuments

Dieses Dokument erklärt jedes Schulungsbeispiel so, dass ein Teilnehmer ohne Vorwissen nachvollziehen kann, was in welcher Phase passiert, warum es passiert und welche Aussage damit belegt wird. Es beschreibt die Implementierung – es ersetzt nicht ihre Ausführung. Wer eine Demo ausführen will, folgt den How-to-Dokumenten oben; wer verstehen will, was er dort sieht, liest hier weiter.

Jede Demo-Erklärung beantwortet dieselben Fragen:

- **Kernfrage:** Was wird demonstriert?
- **Konstruktion:** Wie wird der Testfall aufgebaut – Objekte, Datenmengen, Stellschrauben?
- **Phasen:** Was passiert in Setup, Baseline, Demonstration, Observation, Mitigation und Comparison?
- **Abfrage/Evidenz:** Welche DMVs, Katalogsichten oder Systemobjekte liefern die Messung, und wie wird sie geprüft?
- **Kernaussage:** Welche fachliche Aussage belegt der Lauf?
- **Nicht gesagt wird:** Welche Aussage die Demo bewusst nicht trifft (Schutz vor Übergeneralisierung).
- **Versionsabhängigkeiten:** Welche Skip-Regeln bei SQL Server 2019/2022/2025 gelten.

Die Reihenfolge folgt der Modulstruktur der Präsentation. Die Beschreibungen sind aus dem tatsächlichen Code abgeleitet; Objektnamen, Zeilenzahlen und Assertionslogik entsprechen der Implementierung.

---

# Teil 1 – Optimizer, Statistiken und Execution Plans

## OPT-002 – Statistik-Anatomie

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1 (TSQL_TESTDB, geteilte Testinstanz).

**Kernfrage:** Wie unterscheiden sich Statistikheader, Histogramm und Density Vector einer Stichprobenstatistik – und was ändert sich bei FULLSCAN?

**Konstruktion.** Das Setup füllt `lab.StatisticsData` mit 100 000 Zeilen: 50 000 Zeilen auf dem „heißen" Schlüssel `CategoryId=1`, insgesamt 101 Kategorien, dazu `RegionId`, `Amount` und 400 Bytes Payload. Die Statistik `ST_StatisticsData_Category_Region` auf `(CategoryId, RegionId)` wird bewusst mit `SAMPLE 1000 ROWS` erzeugt – die kleine Stichprobe ist Teil des Experiments.

**Phasen:**

- **BASELINE:** Die tatsächliche Verteilung wird gezählt (100 000 Zeilen gesamt, 50 000 auf `CategoryId=1`) und in `lab.Opt002Evidence` gespeichert.
- **DEMONSTRATION:** `DBCC SHOW_STATISTICS ... WITH STAT_HEADER, DENSITY_VECTOR, HISTOGRAM` gibt die drei Statistikbestandteile aus; zusätzlich lesen `sys.dm_db_stats_properties` (rows, rows_sampled, steps) und `sys.dm_db_stats_histogram` dieselben Werte maschinenlesbar.
- **OBSERVATION:** Die Assertion verlangt: Stichprobe kleiner als Gesamtheit, Histogrammschritte im Bereich 1–200, erstes Schlüsselelement ist `CategoryId`, der Hot-Key ist im Sample sichtbar.
- **MITIGATION:** `UPDATE STATISTICS ... WITH FULLSCAN` (ohne `NORECOMPUTE`).
- **COMPARISON:** Nach FULLSCAN: 100 000 gelesene Zeilen, deterministisch 101 Schritte, `equal_rows` des Hot-Keys exakt 50 000.

**Abfrage/Evidenz:** `sys.dm_db_stats_properties`, `sys.dm_db_stats_histogram`, `DBCC SHOW_STATISTICS`. Die Phase endet mit `SQLPERF_SUMMARY|PASS|OK` nur, wenn alle drei Bestandteile ausgegeben wurden.

**Kernaussage:** Eine Stichprobenstatistik zeigt nur einen Ausschnitt der Verteilung; FULLSCAN macht Histogrammschritte und Hot-Key-Frequenz exakt nachweisbar.

**Nicht gesagt wird:** Dass FULLSCAN grundsätzlich der bessere Weg ist. Die Demo zeigt den Unterschied in der Evidenz, nicht eine Wartungsempfehlung.

**Versionen:** SQL Server 2019–2025 (Major 15–17), Compatibility Level 150/160/170; keine Versionsskips.

## OPT-003 – Sampling, Skew und Histogrammgrenzen

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Wie wirken sich Stichprobenumfang und Histogrammgrenze auf die Darstellung eines starken Hot-Keys aus?

**Konstruktion.** `lab.SkewData` erhält 200 000 Zeilen: 180 000 auf `CategoryId=1`, je 1 000 auf 1 000 weitere Kategorien, 80 Bytes Payload. Index `IX_OPT003_Category`, Statistik mit `SAMPLE 1 PERCENT` – rund 2 000 Zeilen Stichprobe auf eine extrem schiefe Verteilung.

**Phasen:**

- **BASELINE:** rows = 200 000, rows_sampled ≈ 2 000; Header und Histogramm werden ausgelesen.
- **OBSERVATION:** Stichprobe < Gesamtheit; Histogrammschritte ≤ 200 trotz 1 001 Kategorien.
- **MITIGATION:** FULLSCAN.
- **COMPARISON:** rows_sampled = 200 000, Hot-Rows = 180 000 nachweisbar.

**Abfrage/Evidenz:** `DBCC SHOW_STATISTICS` (Header, Histogram), `sys.dm_db_stats_properties`.

**Kernaussage:** Stichprobenrate und Histogrammgrenze sind unabhängige Größen; selbst ein 1-Prozent-Sample kann die Schiefelage sichtbar machen, während die Histogrammgrenze die Detailtiefe begrenzt.

**Nicht gesagt wird:** Keine allgemeine Überlegenheit von FULLSCAN und keine Aussage, wann Sampling ausreicht – das hängt von Verteilung und Abfragemuster ab.

**Versionen:** SQL Server 2019–2025; keine Versionsskips.

## OPT-005 – Ascending Key und Statistikpflege

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Wie entstehen Schätzer für Werte außerhalb des Histogramms, und wie werden Statistiken daraus gepflegt?

**Konstruktion.** `lab.AscendingData` mit 100 000 Zeilen, steigender `EventId` und `EventDate` im Bereich 2025-01-01 bis etwa 2025-04-12; Index `IX_OPT005_Date` mit FULLSCAN; `AUTO_UPDATE_STATISTICS_ASYNC OFF` ist explizit gesetzt.

**Phasen:**

- **BASELINE:** 100 000 Zeilen, ModificationCounter = 0, Histogrammoberende = maximales Datum.
- **DEMONSTRATION:** 20 000 Inserts mit Datum **hinter** dem Histogrammende (Ascending-Key-Situation).
- **OBSERVATION:** ModificationCounter ≥ 20 000, neues Maximum außerhalb des Histogramms.
- **MITIGATION:** `ALTER DATABASE SET AUTO_UPDATE_STATISTICS_ASYNC ON` und ein FULLSCAN-Refresh.
- **COMPARISON:** 120 000 Zeilen, ModificationCounter = 0 nach Refresh, AsyncEnabled = 1.

**Abfrage/Evidenz:** `sys.dm_db_stats_properties` (modification_counter), Histogrammobergrenze, Datenbankoption.

**Kernaussage:** Neue Werte außerhalb des Histogramms sind zunächst unsichtbar; ihre Berücksichtigung verlangt eine Statistikaktualisierung – der asynchrone Modus steuert nur, *wann* aktualisiert wird, nicht *ob*.

**Nicht gesagt wird:** Dass asynchrone Pflege immer besser ist. Der tatsächliche Aktualisierungszeitpunkt ist build- und lastabhängig und wird nicht als PASS-Bedingung behauptet.

**Versionen:** SQL Server 2019–2025; keine harten Versionsskips.

## OPT-009 – Parameter Sensitive Plan Optimization (PSP)

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Wie erzeugt PSP Optimierung mehrere Planformen für ein schiefe Gleichheitsprädikat – und was passiert ohne sie?

**Konstruktion.** `lab.PspOrder` mit 100 000 Zeilen: `OwnerId=1` trägt 99 000 Zeilen, 200 weitere Besitzer je 5 Zeilen. Nicht abdeckender Index `IX_Opt009_PspOrder_OwnerId`. Vier Prozeduren: zwei Reihenfolgevarianten (selektiver Wert zuerst / häufiger Wert zuerst), eine PSP-Variante und eine Opt-out-Variante mit `DISABLE_PARAMETER_SENSITIVE_PLAN`. PSP ist als Datenbankoption initial aus.

**Phasen:**

- **BASELINE (PSP aus, selektiver Wert zuerst):** Ein gecachter Plan für beide Werte; der selektive Wert (5 Zeilen) liest wenig.
- **DEMONSTRATION (PSP aus, häufiger Wert zuerst):** Der Plan für den 99 000-Zeilen-Fall wird zuerst kompiliert; der selektive Wert erbt den ungünstigen Plan – die Reads steigen symmetrisch.
- **OBSERVATION:** Vergleich der Read-Profile aus den Evidence-Tabellen; beide Reihenfolgen erzeugen je einen benachteiligten Fall.
- **MITIGATION (PSP an):** `usp_Opt009SearchPsp` zeigt einen Dispatcherplan mit mindestens zwei Query-Varianten und Kardinalitätsgrenzen; beide Parameterwerte laufen mit niedrigeren Reads als in ihren ungünstigen Fällen.
- **COMPARISON (Opt-out):** `DISABLE_PARAMETER_SENSITIVE_PLAN` erzeugt keinen Dispatcher; die Ergebnismengen bleiben über alle Phasen identisch.

**Abfrage/Evidenz:** Plan-Cache- und Plankörperevidenz je Session; Dispatcher- und Variantenattribute aus dem Actual Plan (`sys.dm_exec_query_plan_stats`, datenbankbezogen `LAST_QUERY_PLAN_STATS = ON`).

**Kernaussage:** PSP Optimierung legt je Kardinalitätsband separate Planvarianten unter einem Dispatcher an – eine gezielte Entschärfung parametersensitiver Fälle, kein allgemeiner Beschleuniger.

**Nicht gesagt wird:** PSP greift nur für bestimmte Prädikatformen (Gleichheit); Bereichs- und LIKE-Prädikate sind ausdrücklich nicht abgedeckt.

**Versionen:** SQL Server 2019 → erwartungsgemäß `SKIP_VERSION`; 2022/2025 (CL 160/170) → Runtime-Evidenz.

## OPT-010 – Optional Parameter Plan Optimization (OPPO)

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Wie verhalten sich optionale Parameter (`OR @p IS NULL`) – und was ändert OPPO Optimierung?

**Konstruktion.** `lab.OppoListing` mit 100 000 Zeilen, `AgentId` 1–2000 (je 50 Zeilen), nicht abdeckender Index. Vier Prozeduren mit dem Muster `(o.AgentId = @AgentId OR @AgentId IS NULL)`: zwei Reihenfolgevarianten (belegter Wert zuerst / NULL zuerst), eine OPPO-Variante, ein Opt-out mit `DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION`. Die Datenbankoption startet aus.

**Phasen:**

- **BASELINE (OPPO aus, belegter Wert zuerst):** Ein Plan; 50 Zeilen selektiv, 100 000 ohne Filter.
- **DEMONSTRATION (OPPO aus, NULL zuerst):** Die Reihenfolge ist – anders als bei PSP – weitgehend neutral; das Kostenverhältnis bleibt in dokumentierter Bandbreite.
- **OBSERVATION:** Kostenverhältnis ≥ 0,5 und Reihenfolgeabweichung ≤ 5 % als tolerierte Bandbreite (FWK-011-Vertrag, kein Fixwert).
- **MITIGATION (OPPO an):** Dispatcherplan mit mindestens zwei Varianten, `OptionalParameterPredicate` im Dispatcher, belegter Parameter günstiger als in der Baseline.
- **COMPARISON (Opt-out):** Kein Dispatcherplan; Ergebnisgleichheit über alle Phasen.

**Abfrage/Evidenz:** Dispatcher- und Variantenevidenz aus dem Plan-Cache, objektbezogen auf die Demo-Prozeduren.

**Kernaussage:** Optionale Parameter erzeugen keine reihenfolgeabhängigen Kosten wie schiefe Gleichheitsprädikate; OPPO Optimierung bildet beide Parameterzustände als getrennte Varianten ab.

**Nicht gesagt wird:** OPPO Optimierung ist eine SQL-Server-2025-Funktion (CL 170) – auf älteren Versionen ist sie nicht vorhanden, nicht nur schlechter.

**Versionen:** SQL Server 2025 → Runtime-Evidenz; 2019/2022 → erwartungsgemäß `SKIP_VERSION`.

## OPT-013 – Controlled Spill

**Sicherheit/Stufe:** YELLOW, 1 Session, Stufe 2 (TSQL_TESTDB auf Wegwerfinstanz – belastet TempDB der ganzen Instanz).

**Kernfrage:** Wie erzeugt eine eingeschränkte Kardinalitätssicht einen Sort-Spill, und wie behebt man ihn ohne Planformwechsel?

**Konstruktion.** `lab.SpillData` mit 300 000 deterministischen Zeilen (`SortKey`, `Payload`, `MeasureValue`). Die Stellschraube: Das Sortieren einer **Table Variable** mit 300 000 Zeilen und dem Hinweis `DISABLE_DEFERRED_COMPILATION_TV` – die feste Erstschätzung (niedrige Zeilenzahl) erzeugt einen Undergrant.

**Phasen:**

- **BASELINE:** Sortierung der Basistabelle: 300 000 Zeilen, `last_spills = 0`, Grant und UsedGrant sichtbar.
- **DEMONSTRATION:** Gleiche Arbeitsmenge über die Table Variable: `last_spills > 0`, kleinerer Grant als Baseline – der kontrollierte Spill.
- **OBSERVATION:** Vergleich von Zeilenzahl (identisch), Grant (unterschiedlich) und Spills (0 gegen > 0).
- **MITIGATION:** Materialisierung in `lab.SpillStage` mit Statistik `ST_SpillStage_Payload_SortKey` (FULLSCAN).
- **COMPARISON:** Gleiche 300 000 Zeilen über die Staging-Tabelle: `last_spills = 0`, Grant ≥ Baseline, keine Spool-Planform erforderlich.

**Abfrage/Evidenz:** Actual Plan (Sort-Operator, Warnungen), Memory-Grant-Attribute, `last_spills` aus der Abfragestatistik.

**Kernaussage:** Der Spill entsteht aus der fehlenden Kardinalitätssicht (feste Table-Variable-Schätzung), nicht aus einem Ressourcenmangel; Materialisierung mit sichtbarer Statistik behebt die Ursache.

**Nicht gesagt wird:** Keine Pauschalbewertung von Spools; die Demo zeigt einen Undergrant-Fall, keine universelle Spill-Diagnose. `MAX_GRANT_PERCENT` wird bewusst nicht als Erzeugungsweg verwendet (DEC-041: unterschreitet den internen Mindestgrant nicht zuverlässig).

**Versionen:** SQL Server 2019–2025; gelbe Safety-Gates (isolierter Lab, `--confirm-isolated-lab`, positives Zeitbudget).

## OPT-015 – Plan Properties

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Wie liest man Actual Execution Plans systematisch – von planweiten Eigenschaften bis zu operatorbezogenen Werten?

**Konstruktion.** `lab.WorkItem` mit 200 000 Zeilen in 20 Entity-Gruppen, abdeckender Index `IX_WorkItem_EntityGroupId`, Prozedur `usp_Opt015Workload`. `LAST_QUERY_PLAN_STATS = ON` (Datenbankoption) aktiviert die Nachlauf-Evidenz des letzten Plans.

**Phasen:**

- **BASELINE (`EntityGroupId=5`):** Estimate im plausiblen Band, Actual = 10 000, RowsRead ≥ Actual, StatisticsUsageCount ≥ 1.
- **DEMONSTRATION (`EntityGroupId=999` nach 60 000 Inserts außerhalb des Histogramms):** Estimate deutlich unter Actual – der Schätzfehler wird messbar.
- **OBSERVATION:** Vergleich des absoluten Schätzfehlers |Estimate − Actual| zwischen beiden Läufen.
- **MITIGATION:** `UPDATE STATISTICS ... WITH FULLSCAN` und Recompile.
- **COMPARISON:** Estimate liegt wieder im Band, der absolute Schätzfehler sinkt.

**Abfrage/Evidenz:** Planweite und operatorbezogene Attribute aus `sys.dm_exec_query_plan_stats`; getrennte Auswertung von Estimated Rows, Actual Rows, RowsRead, StatisticsUsage.

**Kernaussage:** Plankommentare sind strukturiert auswertbar – Statement-Ebene (Kosten), Schätzung gegen Laufzeit, Statistikverwendung und Prädikate sind getrennte Informationen.

**Nicht gesagt wird:** Out-of-Range-Werte sind nicht die einzige Ursache für Schätzfehler; die Demo zeigt einen kontrollierten Fall, keine allgemeine Diagnosemethodik.

**Versionen:** SQL Server 2019–2025; `LAST_QUERY_PLAN_STATS` wird datenbankbezogen gesetzt und im Cleanup zurückgenommen.

## OPT-016 – Rebind, Rewind, Outer References und Spools

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Wann entsteht ein Performance-Spool, und wie hängen Rebinds, Rewinds und Outer References zusammen?

**Konstruktion.** `lab.WorkItemDetail` (20 000 Zeilen, 20 Gruppen), `lab.ProbeRequest` mit zwei Profilen: `'H'` = 5 000 wiederholte Requests (10 je Gruppe), `'L'` = 20 einmalige Requests. Prozedur `usp_Opt016Workload` mit `CROSS APPLY`-Top-1-Zugriff; Indizes `IX_ProbeRequest_Profile_Group` und `IX_WorkItemDetail_Group_Sequence`.

**Phasen:**

- **BASELINE (Profil H, Index vorhanden, `NO_PERFORMANCE_SPOOL`):** Nested Loops mit Outer References und Seek – kein Spool.
- **DEMONSTRATION (Index entfernt, Profil H):** Der Optimierer wählt einen Spool-Plan; Rebinds und Rewinds erscheinen.
- **OBSERVATION (Profil L):** Der Spool wird wiederverwendet; `SpoolActualRewinds` ist beim Einmal-Profil höher sichtbar als beim Wiederholungsprofil.
- **MITIGATION:** Index wird wiederhergestellt; zurück zur Seek-Form.
- **COMPARISON:** Identische Ergebnisse zu BASELINE, kein Spool.

**Abfrage/Evidenz:** Operatorattribute aus `sys.dm_exec_query_plan_stats`: Outer References, Rebinds, Actual Rewinds, Spool-Typ.

**Kernaussage:** Rebinds, Rewinds und Spools sind mit der äußeren Schlüsselverteilung gemeinsam zu interpretieren; ein Spool ist weder automatisch Fehler noch automatisch Optimierung.

**Nicht gesagt wird:** Dass Spools generell zu eliminieren sind – die Demo liefert die Interpretationsgrundlage, keine Verbotsregel.

**Versionen:** SQL Server 2019–2025; `LAST_QUERY_PLAN_STATS` datenbankbezogen erforderlich.

## OPT-017 – Parallelism Skew

**Sicherheit/Stufe:** YELLOW, 1 Session, **Stufe 3 CONTAINER** – ein festes Vier-CPU-Profil (empfohlen 8 GB) ist für reproduzierbare Actual-DOP-, Exchange- und Thread-Evidenz erforderlich; eine reine Testdatenbank kann die vier sichtbaren Scheduler nicht garantieren.

**Kernfrage:** Wie verteilen parallele Exchanges Arbeit ungleich auf Threads – und wie misst man das pro Thread?

**Konstruktion.** Zwei Fakttabellen mit je 600 000 Zeilen: Profil `B` balanciert über 4 096 Gruppenschlüssel, Profil `S` konzentriert 95 % auf einen Schlüssel. Prozedur `usp_Opt017Aggregate` mit MAXDOP 4.

**Phasen:**

- **BASELINE (Profil B, MAXDOP 4):** Rowcount und Checksumme der Aggregation.
- **DEMONSTRATION (Profil S, MAXDOP 4):** Gleiche Logik auf konzentrierter Verteilung.
- **OBSERVATION:** Aus dem XML des letzten Actual Plans: Actual DOP, Exchange-Zähler, ActualRows je Thread, Skew-Ratio (Max/Min positiver Threadarbeit).
- **MITIGATION:** Serielle Gegenprobe mit MAXDOP 1.
- **COMPARISON:** Checksummen und Zeilenzahlen identisch; Skew-Ratio ≥ 1 mit Arbeit auf mindestens zwei Threads und vorhandenem Exchange.

**Abfrage/Evidenz:** `sys.dm_exec_query_plan_stats` (XML), operatorbezogene Laufzeitwerte des Parallelism-Operators.

**Kernaussage:** Parallelität erzeugt Exchanges, die Arbeit ungleich verteilen; die tatsächliche Verteilung ist nur pro Thread messbar – Serienlauf als Gegenprobe trennt Skew-Effekt von Parallelisierungsgewinn.

**Nicht gesagt wird:** Keine globale MAXDOP-Empfehlung und keine Bewertung produktiver Pläne.

**Versionen:** SQL Server 2019–2025; Preflight verlangt mindestens vier sichtbare Kerne und effektiven DOP ≥ 2, sonst kontrollierter Skip.

---

# Teil 2 – Query Patterns

## QRY-001 – SARGability

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Kann eine Funktion auf einer indizierten Spalte den Suchbereich verdecken und einen Scan erzwingen – bei identischer Filterarbeit?

**Konstruktion.** `lab.SearchData` mit 300 000 Zeilen, `EventDateTime` deterministisch über einen Datumsbereich verteilt; Index `IX_SearchData_EventDateTime` mit `MeasureValue` als INCLUDE-Spalte.

**Phasen:**

- **BASELINE:** SARGables halboffenes Intervall (`EventDateTime >= @Start AND EventDateTime < @End`); Logical Reads statementbezogen aus `sys.dm_exec_query_stats`; Erwartung: Index Seek.
- **DEMONSTRATION:** Identische Filtermenge über `CONVERT(char(10), EventDateTime, 120) = '2024-03-15'` auf der Indexspalte; Erwartung: Scan mit mehr Reads.
- **OBSERVATION:** Aus `lab.Qry001Evidence`: Ergebnissumme identisch, Zugriffsmethode unterschiedlich, Problem-Reads > Baseline-Reads.
- **MITIGATION:** Das Datum wird auf der **Parameterseite** berechnet (`DATEADD(day, 1, @Start)`), die Spalte bleibt unangetastet.
- **COMPARISON:** Wiederholung der SARGable-Abfrage im gleichen Datenzustand: identisches Ergebnis, weniger Reads, Seek bestätigt.

**Abfrage/Evidenz:** `sys.dm_exec_query_stats` (statementbezogene Logical Reads), Plan-Access-Operator.

**Kernaussage:** SARGability ist keine Syntaxfrage, sondern die Frage, ob der Optimierer aus dem Prädikat einen Suchbereich ableiten kann.

**Nicht gesagt wird:** Nicht jeder Seek ist günstiger als jeder Scan – die Demo vergleicht nur zwei äquivalente Prädikate bei selektivem Datum mit passendem Index.

**Versionen:** SQL Server 2019–2025; Skips nur für Version außerhalb des Bereichs bzw. fehlende Berechtigungen.

## QRY-004 – Classic and Dynamic Search Conditions

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1. Drei Strategien werden nacheinander verglichen, ohne Rangfolge (DEC-056).

**Kernfrage:** Wie unterscheiden sich Catch-all-Prädikate, `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL in Planwiederverwendung und Kosten?

**Konstruktion.** `lab.SearchOrder` mit 20 000 Zeilen (20 × `RARE`, 19 980 × `CMMN`), zwei nicht abdeckende Indizes, Tabelle `lab.Qry004AllowedFilter` als **Positivliste** (DEC-055: Prädikatsbausteine stammen aus der Tabelle, Werte sind über `sys.sp_executesql` gebunden, unbekannte Filter brechen kontrolliert ab; `EXEC(...)` und Wertkonkatenation sind statisch verboten). Drei Prozeduren: `usp_Qry004CatchAll`, `usp_Qry004Recompile` (+ `OPTION (RECOMPILE)`), `usp_Qry004Dynamic`.

**Phasen:**

- **BASELINE (Catch-all, `RARE`):** Logische Reads aus der Cachestatistik; Evidence speichert je Phase/Strategie: RowCount, Checksum, LogicalReads, CachedPlanCount, ExecutionCount, CPU, Literalfreiheit.
- **DEMONSTRATION (Recompile):** `sp_recompile`, dann `RARE` und `COMMON`: selektiver Wert günstiger, häufiger Wert verglichen; Kompilierung neu je Ausführung.
- **OBSERVATION:** Catch-all und Recompile je 25× ohne Filter – identische Arbeitsmenge, unterschiedlich many gecachte Pläne und CPU je Ausführung (Recompile kostet Kompilierung pro Ausführung).
- **MITIGATION:** bewusst keine; die Demo liefert die Vergleichsbasis, keine Rangfolge.
- **COMPARISON:** Drei Strategien auf Ergebnisgleichheit und Cacheeffekte; dynamisches SQL erzeugt je Filterform genau einen Plan.

**Abfrage/Evidenz:** Plan-Cache-Statistik objektbezogen; Literalfreiheit als injektionssicheres Vertragsfeld.

**Kernaussage:** Catch-all wird einfach wiederverwendet (und kann unpassend sein), `OPTION (RECOMPILE)` tauscht Wiederverwendung gegen Einzelfalloptimierung, dynamisches SQL mit Bindung erzeugt je Filterform einen Plan und bleibt sicher.

**Nicht gesagt wird:** Keine Rangfolge der Strategien; PSP/OPPO bleiben in OPT-009/OPT-010; ein absichtlich verwundbares Gegenbeispiel wird nicht gezeigt (kopierbarer Schadcode).

**Versionen:** SQL Server 2019–2025; Skip bei fehlenden Zustandsberechtigungen oder fehlender Cachestatistik.

## QRY-013 – Client- und Sessionkontext

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1.

**Kernfrage:** Warum zeigt derselbe Querytext mit demselben Parameterwert in unterschiedlichen Sessions unterschiedliches Verhalten?

**Konstruktion.** `lab.SearchItem` mit 20 020 Zeilen (20 × `RARE`, 20 000 × `CMMN`), Index auf `CategoryCode`, Prozedur `usp_Qry013Probe` mit Marker `SQLPERF_QRY013_PROBE`. Zwei Client-Profile: `CLIENT_PROFILE_A` (ARITHABORT ON) und `CLIENT_PROFILE_B` (ARITHABORT OFF, sonst identisch) – bewusst **ohne** Produktnamen (DEC-054).

**Phasen:**

- **BASELINE (Profil A, `RARE`):** 1 Cacheeintrag, @@OPTIONS-Wert, 20 Zeilen.
- **DEMONSTRATION (Profil B, `RARE`, gleicher Text):** 2 Cacheeinträge – der abweichende SET-Options-Kontext erzeugt einen eigenen Plan; Ergebnis identisch.
- **OBSERVATION (Profil A, `CMMN`):** Cacheeinträge bleiben bei 2, die Reads unterscheiden sich – der **Parameterwert** ist eine zweite, unabhängige Kontextdimension. Damit ist die Ein-Ursachen-Hypothese („das Tool") widerlegt.
- **MITIGATION:** bewusst keine; die Trennung der zwei Dimensionen ist die Erkenntnis.
- **COMPARISON:** Evidence-Zusammenfassung: Cacheeinträge, SessionOptions, LogicalReads je Phase.

**Abfrage/Evidenz:** Objektbezogene Plancache-Evidenz für die eine Demo-Prozedur, `@@OPTIONS` je Session.

**Kernaussage:** Sessionkontext und Parameterwert sind zwei unabhängig prüfbare Dimensionen; beide erzeugen über objektbezogene Cache-Evidenz nachweisbare Unterschiede ohne Produktzuschreibung.

**Nicht gesagt wird:** Weder ein Client noch ein Treiber wird als Ursache benannt; es gibt keine Empfehlung wie „ARITHABORT immer setzen".

**Versionen:** SQL Server 2019–2025; Skip bei fehlenden Zustandsberechtigungen oder fehlender Cachestatistik.

---

# Teil 3 – Rowstore und Columnstore

## IDX-006 – Page Splits, Density und Fragmentierung

**Sicherheit/Stufe:** YELLOW, 1 Session, Stufe 2 (begrenzte Insert-Last auf Wegwerfinstanz).

**Kernfrage:** Wie unterscheiden sich Page Splits und Density zwischen Fill Factor 100 und 80 unter Schlüssellücken-Inserts?

**Konstruktion.** Zwei identische Tabellen `FF100` und `FF080` mit je 60 000 Zeilen, Clustered Indexes mit Fill Factor 100 bzw. 80.

**Phasen:**

- **BASELINE:** `sys.dm_db_index_physical_stats` (DETAILED): LeafAllocations, PageCount, Density, Fragmentation.
- **DEMONSTRATION:** 60 000 Inserts in Schlüssellücken (ungerade Schlüssel) in beiden Tabellen.
- **OBSERVATION:** Deltas von LeafAllocations und Density gegenüber Baseline.
- **MITIGATION:** Rebuild beider Indexe mit Fill Factor.
- **COMPARISON:** 120 000 Zeilen und identische Checksummen in beiden Tabellen; das Leaf-Allocation-Delta ist bei FF080 kleiner als bei FF100.

**Abfrage/Evidenz:** `sys.dm_db_index_physical_stats` (DETAILED).

**Kernaussage:** Fill Factor beeinflusst die Split-Häufigkeit messbar; Density und logische Fragmentierung sind getrennte Messgrößen.

**Nicht gesagt wird:** Keine universelle Rebuild-Schwelle; Wartungseffekt und Workloadnutzen werden getrennt bewertet.

**Versionen:** SQL Server 2019–2025; keine Versionsskips.

## IDX-010 – Columnstore Segments

**Sicherheit/Stufe:** YELLOW, **Stufe 3 CONTAINER** – die 1,2-Millionen-Zeilen-Columnstore-Last und die Rowgroup-Komprimierung verlangen einen begrenzten Speicher-/Storage-Envelope, den eine geteilte Testinstanz nicht garantiert.

**Kernfrage:** Wie bestimmt die Ladeordnung die Segmentüberlappung – und damit die Segment Elimination?

**Konstruktion.** `OrderedFact` (1 200 000 Zeilen, nach `FactId` sortiert geladen) und `ShuffledFact` (identische Zeilen, deterministisch gemischt), beide als Clustered Columnstore (`CCI_Ordered`, `CCI_Shuffled`).

**Phasen:**

- **BASELINE:** `sys.dm_db_column_store_row_group_physical_stats`: Rowgroup-Status, gelöschte Zeilen.
- **OBSERVATION:** `sys.column_store_segments` für `DateKey`: Segmentanzahl und Überlappung; eine Filterabfrage auf einen schmalen `DateKey`-Bereich zeigt `QualifyingSegments` je Tabelle.
- **MITIGATION:** 5 % Deletes in `OrderedFact`, `REORGANIZE ... COMPRESS_ALL_ROW_GROUPS`.
- **COMPARISON:** Zeilenzahl und Summe identisch in beiden Tabellen; `QualifyingSegments` in OrderedFact < ShuffledFact.

**Abfrage/Evidenz:** Rowgroup- und Segmentmetadaten, Segment-Eliminierungszähler der Filterabfrage.

**Kernaussage:** Sortiertes Laden erzeugt nicht überlappende Segmente; Segment-Eliminierung reduziert die gelesene Datenmenge sichtbar.

**Nicht gesagt wird:** Keine Aussage zu Ordered Nonclustered Columnstore (SQL Server 2025) und keine absoluten Kompressions- oder Ressourcenzahlen.

**Versionen:** SQL Server 2019–2025; kontrollierte Skips bei editions- oder ressourcenbedingter Nichtanwendbarkeit.

---

# Teil 4 – Concurrency, Isolation und TempDB

## CON-004 – Blocking Chain

**Sicherheit/Stufe:** YELLOW, **4 Sessions**, Stufe 2; `--confirm-isolated-lab` erforderlich, Timeout 120 Sekunden, je Signal max. 15 Sekunden.

**Kernfrage:** Wie folgt man eine Blocking Chain vom blockierten Request bis zum Head Blocker – und wie unterscheidet sie sich vom Deadlock?

**Konstruktion.** `lab.BlockingDemo` (2 Zeilen), Signaltabelle `fwk.SessionSignal` mit den Prozeduren `fwk.USP_Signal` und `fwk.USP_WaitForSignal` (Polling alle 100 ms), Evidence-Tabelle für die Kette.

**Phasen (Demonstration als Multi-Session-Phase, `Sessions/problem.json`):**

- **HEAD** (Start-Verzögerung 0 ms): BEGIN TRAN, UPDATE Zeile 1 (X-Sperre), Signal `HEAD_START`, wartet auf `OBSERVED`, dann COMMIT.
- **MIDDLE** (50 ms): UPDATE Zeile 2, dann UPDATE Zeile 1 – blockiert an HEAD.
- **LEAF** (100 ms): UPDATE Zeile 2 – blockiert an MIDDLE.
- **OBSERVER** (150 ms): liest die Kette aus `sys.dm_tran_locks`/`sys.dm_exec_requests` (rekursiv über `blocking_session_id`) und schreibt `ChainDepth=2`, Wait-Typen (`LCK_M_*`) und Wartezeiten in die Evidence.
- **OBSERVATION:** Kette vollständig: Head-Session ohne eigenes `blocking_session_id`, MIDDLE → HEAD, LEAF → MIDDLE, WaitMs > 0; danach Commits und blockierungsfreier Zustand.
- **MITIGATION:** Signal-/Datenreset; Demonstration kurzer Transaktionen.
- **COMPARISON (`Sessions/comparison.json`, Rollen FirstWriter/Follower):** geordnete Ausführung ohne Blockierung.

**Abfrage/Evidenz:** `sys.dm_tran_locks`, `sys.dm_exec_requests`, Session-Signalisierung.

**Kernaussage:** Eine Blocking Chain ist eine gerichtete Wartekette bis zum Head Blocker, der selbst niemanden blockiert – sie ist ein Zustand, kein Fehler, und löst sich durch Transaktionsende.

**Nicht gesagt wird:** Keine Gleichsetzung mit Deadlocks, kein NOLOCK-Einsatz, keine instanzweiten Locking-Änderungen.

**Versionen:** SQL Server 2019–2025; Timeout-Fehler bei fehlenden Signalen, Cleanup mit `ROLLBACK IMMEDIATE` nach Markerprüfung.

## CON-006 – Deadlock Cycle

**Sicherheit/Stufe:** YELLOW, **3 Sessions**, Stufe 2; `--confirm-isolated-lab`, Timeout 180 Sekunden.

**Kernfrage:** Wie entsteht ein Deadlock-Zyklus deterministisch, wer wird Opfer, und wie liest man den Deadlock-Graph?

**Konstruktion.** `lab.DeadlockRows` (Zeilen 1 und 2), `lab.Evidence` (Rolle, Ausgang, Fehlernummer), `fwk.SessionSignal` mit `fwk.USP_Signal`/`fwk.USP_WaitForSignal`.

**Phasen:**

- **BASELINE:** Reset und Integritätsprüfung (genau 2 Zeilen).
- **DEMONSTRATION (`Sessions/deadlock.json`, Multi-Session-Phase):**
  - `ACTOR_A` (`SET DEADLOCK_PRIORITY LOW`): BEGIN TRAN, UPDATE Zeile 1 (+1), Signal `A_LOCKED`, wartet auf `B_LOCKED` (max. 15 s), UPDATE Zeile 2, COMMIT; bei Fehler 1205 wird ein `VICTIM`-Eintrag geschrieben.
  - `ACTOR_B` (`DEADLOCK_PRIORITY HIGH`): UPDATE Zeile 2 (+1), Signal `B_LOCKED`, wartet auf `A_LOCKED`, UPDATE Zeile 1, COMMIT; bei 1205 ebenfalls Evidence.
  - SQL Server erkennt den Zyklus (A wartet auf B, B wartet auf A), wählt die niedrigere Priorität (`ACTOR_A`) als Opfer, `ACTOR_B` committet.
- **OBSERVATION:** `lab.Evidence` enthält genau einen `VICTIM` (1205) und einen `SURVIVOR`; zusätzlich liest der Observer `xml_deadlock_report`-Events aus dem `system_health`-Ringpuffer, gefiltert auf die aktuelle Datenbank-ID. Fehlt der Graph, endet die Phase mit `SKIP_EVIDENCE_MISSING` – die Beobachtung ist optional und wird nicht erfunden.
- **MITIGATION:** Signale und Daten zurücksetzen.
- **COMPARISON (`Sessions/ordered.json`):** Beide Actors aktualisieren in gleicher Reihenfolge (erst Zeile 1, dann 2) – kein Zyklus, beide COMMITS erfolgreich.
- **VERIFICATION:** Hartes Vertragsfeld: genau zwei `COMPLETED`-Einträge in der geordneten Gegenprobe und kein `VICTIM`, sonst `FAIL_RESULT_CONTRACT`.

**Abfrage/Evidenz:** `lab.Evidence`, `sys.dm_xe_session_targets` (system_health, `xml_deadlock_report`), Fehler 1205.

**Kernaussage:** Ein Deadlock ist ein Zyklus gegenseitiger Sperren; SQL Server löst ihn durch Opfer-Abbruch, und `DEADLOCK_PRIORITY` bestimmt das Opfer vorhersagbar.

**Nicht gesagt wird:** Keine Pauschalregel „Deadlocks immer vermeiden"; die Demo zeigt Opferwahl und Graph, nicht allgemeine Auflösungsstrategien.

**Versionen:** SQL Server 2019–2025; `MAX_DURATION`-Syntax nur 2025, sonst expliziter Stop; optionaler Graph-Skip mit `WARN_OPTIONAL_EVIDENCE_SKIPPED`.

## CON-009 – TempDB Cost Classes

**Sicherheit/Stufe:** YELLOW, 1 Session, Stufe 2 (TempDB-Last auf Wegwerfinstanz).

**Kernfrage:** Wie unterscheiden sich User Objects, Internal Objects und Version Store in TempDB – und wie misst man sie getrennt?

**Konstruktion.** `lab.SourceData` mit 150 000 Zeilen (4 000 Gruppenschlüssel, 200 Bytes Payload).

**Phasen:**

- **BASELINE:** `sys.dm_db_session_space_usage`: user_objects_alloc_page_count, internal_objects_alloc_page_count; Version Store als separate Instanzmessung.
- **DEMONSTRATION:** Workload mit drei Klassen: Benutzerobjekt `#UserObject`, HASH-GRID-Aggregation in `#WorkResult` (internal), Sortierung mit `MAX_GRANT_PERCENT = 0.1` in `#SortedWork` (kontrollierter Spill nach internal); Deltas aus Session- und Task-Space-Usage.
- **OBSERVATION:** Deltas User/Internal Pages zwischen Workload und Baseline; Version Store bleibt getrennt.
- **MITIGATION:** Keine Instanzoption wird geändert; die Hebel sind Query- und Indexdesign sowie Lebensdauer temporärer Objekte.
- **COMPARISON:** UserPages-Delta > 0 und InternalPages-Delta > 0.

**Abfrage/Evidenz:** `sys.dm_db_session_space_usage`, `sys.dm_db_task_space_usage`, `sys.dm_tran_version_store`.

**Kernaussage:** Die TempDB-Kostenklassen haben unterschiedliche Scopes und Lebenszyklen und werden getrennt gemessen – ein instanzweiter Blick vermischt sie.

**Nicht gesagt wird:** Keine Aussage zu Dateikonfiguration, Memory-optimized TempDB Metadata oder SQL-Server-2025-Space-Governance (zurückgestellt).

**Versionen:** SQL Server 2019–2025; keine Versionsskips.

---

# Teil 5 – Diagnosewerkzeuge

## DGN-003 – Query Store History

**Sicherheit/Stufe:** GREEN, 1 Session, Stufe 1 (Query Store nur in der markierten Testdatenbank).

**Kernfrage:** Wie unterscheidet sich die persistente Query-, Plan- und Runtime-Historie des Query Store von Live-DMV-Daten?

**Konstruktion.** `lab.SearchData` mit 50 000 Zeilen (45 000 häufige Gruppe), Prozedur `lab.usp_Dgn003Search` (MAXDOP 1). Query Store wird in der markierten Datenbank aktiviert: `READ_WRITE`, `MAX_STORAGE_SIZE_MB = 128`, `INTERVAL_LENGTH_MINUTES = 1`, `QUERY_CAPTURE_MODE = ALL`.

**Phasen:**

- **BASELINE:** Ausführung mit `@GroupId=1` nach `sp_recompile`; `sys.sp_query_store_flush_db` zwingt die Historie in die Katalogsichten.
- **DEMONSTRATION:** Wiederholte Ausführungen zur Cache- und Historienbildung.
- **OBSERVATION:** `sys.query_store_query_text`, `sys.query_store_query`, `sys.query_store_plan`, `sys.query_store_runtime_stats`, optional `sys.query_store_wait_stats`: QueryCount ≥ 1, RuntimeRows ≥ 1; PlanCount ≥ 2 ergibt PASS, PlanCount = 1 ergibt `WARN_EMPIRICAL_VARIANCE` (keine erfundene Zwei-Plan-Aussage).
- **MITIGATION:** bewusst keine – Query Store ist selbst die Evidenzquelle.
- **COMPARISON:** Kontrolle der Historiendaten; Cleanup entfernt die Datenbank einschließlich Query Store.

**Abfrage/Evidenz:** Query-Store-Katalogsichten, Flush nach jeder Phase.

**Kernaussage:** Query Store persistiert Ausführungshistorie innerhalb seiner Capture- und Aufbewahrungsgrenzen; mehrere Pläne sind beobachtbar, aber keine garantierte Optimizerentscheidung.

**Nicht gesagt wird:** Plan Forcing und Query Store Hints gehören in DGN-004; hier wird keine Plansteuerung geändert.

**Versionen:** SQL Server 2019–2025; `sys.query_store_wait_stats` optional; Skip bei fehlender Historie im Zeitfenster.

## DGN-005 – Bounded Extended Events

**Sicherheit/Stufe:** YELLOW, 1 Session, Stufe 2 (serverweit sichtbare XE-Session auf Wegwerfinstanz); `--confirm-isolated-lab`, Timeout 360 Sekunden.

**Kernfrage:** Wie wird eine begrenzte Extended-Events-Session definiert – Event, Action, Predicate, Target, Zeitraum – und wie liest man die Ring-Buffer-Evidenz?

**Konstruktion.** Event-Session `SQLPERF_DGN005_<token>` (deterministischer Name): Event `sqlserver.error_reported`, Actions `database_id`/`session_id`, Prädikat `error_number >= 50000 AND database_id = <aktuelle DB>`, Target `package0.ring_buffer` (Begrenzung 1024 KB), `STARTUP_STATE = OFF`, `EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS`. Auf SQL Server 2025 zusätzlich `MAX_DURATION = 300 SECONDS` als eingebautes Zeitbudget; 2019/2022 nutzen den expliziten Stop.

**Phasen:**

- **BASELINE:** Keine Fehler, EventCount = 0.
- **DEMONSTRATION:** Zwei kontrollierte synthetische Fehler (`THROW 51010`/`51011` mit festen Marker-Texten) in TRY-CATCH.
- **OBSERVATION:** Ringpuffer aus `sys.dm_xe_session_targets` (`TRY_CONVERT(xml, target_data)`), Filter auf `error_reported`, Fehler ≥ 50000, aktuelle Datenbank; Erwartung ≥ 1 Event, sonst `SKIP_EVIDENCE_MISSING`.
- **MITIGATION:** Session stoppen (`ALTER ... STATE = STOP`), Flag in Evidence.
- **COMPARISON:** Zustands- und Markerprüfung; Cleanup entfernt die markierte Datenbank.

**Abfrage/Evidenz:** `sys.dm_xe_sessions`, `sys.dm_xe_session_targets`, XML-Auswertung des Ringpuffers.

**Kernaussage:** Extended Events liefern ereignisbezogene Evidenz; ein „nichts gefunden" ist nur aussagekräftig, wenn Session, Filter, Ereignisklasse und Zeitraum geeignet waren.

**Nicht gesagt wird:** Kein allgemeiner Trace und kein Datei-Export; nur Ringpuffer-XML für die markierte Datenbank, keine `.xel`-Dateien.

**Versionen:** SQL Server 2019–2025; `MAX_DURATION` nur 2025; Skip bei fehlenden Berechtigungen; optionaler Evidence-Skip als WARN.

---

# Teil 6 – Storage, Pages und Transaktionslog

## STL-008 – VLF Log Growth

**Sicherheit/Stufe:** **RED**, **Stufe 3 CONTAINER** (dedizierte Wegwerfinstanz) – bewusstes Logwachstum belastet die Instanz; Profil `performance`, Budget 600 Sekunden, mindestens 2 GB freier Speicher.

**Rote Bestätigungen (Preflight-Gates):** `--allow-red` sowie die drei Variablen `HighImpactConfirmed`, `DisposableEnvironmentConfirmed`, `RecoveryPlanConfirmed`; ohne sie endet der Preflight mit `SKIP_HIGH_IMPACT_CONFIRMATION_REQUIRED`.

**Kernfrage:** Wie erzeugen viele kleine Log-Growth-Schritte viele VLFs – und was ändert ein geplanter Growth-Schritt?

**Konstruktion.** Neue Datenbank `SQLPERF_LAB_STL008_<token>` mit **`FILEGROWTH = 1 MB` auf der Logdatei** (Ursachenschraube), Recovery SIMPLE, Extended-Property-Marker für den markergebundenen Cleanup.

**Phasen:**

- **BASELINE:** VLF-Anzahl aus `sys.dm_db_log_info(DB_ID())`, Loggröße und Growth aus `sys.database_files` – gespeichert in `lab.Evidence`.
- **DEMONSTRATION:** 30 000 Inserts (~4 KB Payload je Zeile, ≈ 120 MB Loglast) in **einer** begrenzten Transaktion, danach `CHECKPOINT`; zweite Messung als `SMALL_GROWTH`.
- **OBSERVATION:** VLF-Details (`vlf_sequence_number`, `vlf_size_mb`, `vlf_active`, `vlf_status`) und die Richtungs-Assertion: Log größer **und** VLF-Anzahl höher als Baseline, sonst `SKIP_EVIDENCE_MISSING` – es wird nichts behauptet, was nicht gemessen wurde.
- **MITIGATION:** Nur der **zukünftige** Growth-Schritt wird auf 64 MB geplant (`ALTER DATABASE ... MODIFY FILE ... FILEGROWTH = 64MB`). Kein `SHRINK`, kein Cache-Flush, kein Restart, kein fremder Dateipfad.
- **COMPARISON:** Dritter Messpunkt `PLANNED_GROWTH`; hartes Vertragsfeld `GrowthMB = 64`, sonst `FAIL_RESULT_CONTRACT`.

**Abfrage/Evidenz:** `sys.dm_db_log_info` (VLF-Ebene), `sys.database_files` (Dateiebene), Assertion über die Evidence-Tabelle.

**Kernaussage:** Mehr kleinteilige Growth-Ereignisse erzeugen mehr VLFs; ein größerer geplanter Growth-Schritt reduziert die künftige VLF-Fragmentierung – eine Strukturaussage.

**Nicht gesagt wird:** Keine universelle Zeit- oder Latenzgrenze; Storage-Latenz wird bewusst nicht bewertet, und aus der Dateigröße allein folgt keine Ursache. Der externe Harness ist der Kill-Switch; Cleanup entfernt ausschließlich die vierfach markierte Datenbank.

**Versionen:** SQL Server 2019–2025 (Major 15–17); Skip-Version außerhalb des Bereichs, Skip bei fehlender `CREATE ANY DATABASE`-Berechtigung oder < 2 GB freiem Speicher.

## STL-009 – Commit Batching

**Sicherheit/Stufe:** YELLOW, 1 Session, Stufe 2 (Log-I/O-Last auf Wegwerfinstanz).

**Kernfrage:** Erzeugt Batch-Commit weniger Log-Flush-Ereignisse als Einzelcommits – bei gleicher Arbeitsmenge?

**Konstruktion.** `lab.CommitRows` (Identity + 200 Bytes Payload), Evidence-Tabelle.

**Phasen:**

- **BASELINE:** Dateizähler aus `sys.dm_io_virtual_file_stats` (type = 1): num_of_writes, num_of_bytes_written; `WRITELOG` aus `sys.dm_os_wait_stats`.
- **DEMONSTRATION:** 4 000 Inserts mit Einzel-Commit (`BEGIN TRAN; INSERT; COMMIT` je Zeile).
- **OBSERVATION:** Write-Deltas zwischen Einzel-Commit und Baseline; WRITELOG-Wait-Delta instanzweit als Zeitfenster-Delta.
- **MITIGATION:** Alle 4 000 Inserts in **einer** Transaktion.
- **COMPARISON:** 4 000 Zeilen und identische Checksummen; Batch-Commit erzeugt weniger Schreibvorgänge als Einzel-Commit.

**Abfrage/Evidenz:** `sys.dm_io_virtual_file_stats` (Deltamessung), `sys.dm_os_wait_stats` (`WRITELOG`).

**Kernaussage:** Transaktionsgrenzen steuern das Write-ahead Logging: Batch-Commit reduziert die Anzahl der Log-Flush-Ereignisse, nicht die Datenmenge.

**Nicht gesagt wird:** Kein Einsatz von Delayed Durability, keine Wait-Statistik-Reset, keine absolute Laufzeitbehauptung – die Aussage ist mengenbezogen.

**Versionen:** SQL Server 2019–2025; keine Versionsskips.

---

# Teil 6 – CPU, Memory, I/O und Waits

## RES-007 – Wait Scope Deltas

**Sicherheit/Stufe:** YELLOW, **3 Sessions** (BLOCKER, WAITER, OBSERVER), Stufe 2; `--confirm-isolated-lab`.

**Kernfrage:** Sind Task-Waits, Request-Waits und instanzweite kumulative Waits verschiedene Scopes – und wie misst man sie getrennt?

**Konstruktion.** Framework-Signalisierung (`fwk.USP_Signal`/`fwk.USP_WaitForSignal`), Tabelle `lab.WaitRow` (eine Zeile), Evidence-Tabelle; Multi-Session-Manifest `Sessions/wait_scope.json`.

**Phasen:**

- **BASELINE:** `sys.dm_os_wait_stats` (`LCK_M_*`) als Startwerte.
- **DEMONSTRATION (3 Sessions):**
  - BLOCKER: BEGIN TRAN, UPDATE auf `WaitRow`, Signal `BLOCKER_LOCKED`, wartet auf `OBSERVED`, ROLLBACK.
  - WAITER: wartet auf `BLOCKER_LOCKED`, `SET LOCK_TIMEOUT 30000`, UPDATE auf dieselbe Zeile, Signal `WAITER_COMPLETED`.
  - OBSERVER: liest beim Warten des WAITER task- und requestbezogene Waits (`sys.dm_os_waiting_tasks`, `sys.dm_exec_requests` für die Session-ID des WAITER) und signalisiert `OBSERVED`.
- **OBSERVATION:** Task-Wait-Typ und -Dauer (aktuell in der Aufgabe), Request-Wait-Typ und -Dauer (aktuell im Request), instanzweites Delta aus `sys.dm_os_wait_stats` nach dem Rollback.
- **MITIGATION:** Rollback-Prüfung: keine offenen Transaktionen, keine bestehende Blockierung.
- **COMPARISON:** `Value = 1` (Lock-Versuch bestätigt), Instanz-Delta > 0; die drei Scopes sind als TASK/REQUEST/INSTANCE getrennt ausgewiesen.

**Abfrage/Evidenz:** `sys.dm_os_waiting_tasks`, `sys.dm_exec_requests`, `sys.dm_os_wait_stats` (Delta).

**Kernaussage:** Task-, Request- und Instanz-Waits sind getrennte Scopes mit unterschiedlicher Lebensdauer; nur die Instanzstatistik ist kumulativ und nur als Zeitfenster-Delta interpretierbar.

**Nicht gesagt wird:** `ASYNC_NETWORK_IO` wird ohne gepaceten Client bewusst nicht künstlich erzeugt; Waits sind Evidenz, aber kein alleiniger Ursachenbeweis.

**Versionen:** SQL Server 2019–2025; Skip bei fehlenden Zustandsberechtigungen.

---

# Anhang A – Gemeinsame Vertragsbausteine aller Demos

Die Demos teilen einen gemeinsamen Rahmen; diese Bausteine gelten projektweit und werden je Demo nur variiert:

1. **Testdatenbank-Vertrag (`FWK-002`):** Name nach Schema `SQLPERF_LAB_<DEMO ohne Bindestrich>_<RunToken>`; Eigentumsmarker als vier Extended Properties (`SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId`, `SQLPERF.RunToken`). Ein passender Name allein berechtigt nie zum `DROP`.
2. **Preflight (`FWK-001`):** prüft Demo-ID, Zielname, Versionsbereich (Major 15–17), Berechtigungen (`CREATE ANY DATABASE`, `VIEW SERVER STATE`/`VIEW SERVER PERFORMANCE STATE`), Sicherheitsbestätigungen und Ressourcenprofil. Ergebnis ist immer eine Summary-Zeile.
3. **Summary-Zeilen (`FWK-012`):** jede Phase endet mit `SQLPERF_SUMMARY|<PASS|WARN|SKIP|FAIL>|<Code>`; die Gesamtpriorität ist `FAIL > SKIP > WARN > PASS`. Häufige Codes: `SKIP_VERSION`, `SKIP_PERMISSION`, `SKIP_RESOURCE_PROFILE`, `SKIP_EVIDENCE_MISSING`, `WARN_EMPIRICAL_VARIANCE`, `FAIL_CONTRACT`, `FAIL_RESULT_CONTRACT`, `FAIL_CLEANUP`.
4. **Ergebnisverträge (`FWK-011`):** fachliche Invarianten als `EXACT` oder `RANGE`, Performancewirkung bevorzugt als `RATIO`/`DIRECTION` – keine maschinenabhängigen Fixwerte.
5. **Cleanup-Dominanz:** nach begonnener Setup-Phase wird Cleanup immer versucht; ein Cleanup-Fehler ergibt `FAIL_CLEANUP` und dominiert das Gesamtergebnis.

# Anhang B – Ausführung (Kurzverweis)

- **Vorhandene Instanz:** `python Demos/00_Framework/Tools/run_demo.py <Pfad zur manifest.json> --server <instanz> --auth sql --username <name>`; gelbe Demos zusätzlich `--confirm-isolated-lab`, rote Demos zusätzlich `--allow-red`. Details: `Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md`.
- **Ohne SQL Server:** `Start-PerformanceTrainingScenario` aus `Documentation/HowTo/CONTAINER_QUICKSTART.md` (Docker/Podman, SQL Server 2025, Lifecycle `READY_FOR_USER` → Reset → Remove).
- **Interaktive Szenarien:** `CON-004` und `DGN-005` besitzen einen Project-Adapter-Lifecycle mit dokumentiertem Benutzerablauf in `Documentation/HowTo/INTERACTIVE_SCENARIO_LIFECYCLE.md`.
- **Kennungen:** Neue Task-/Entscheidungs-/Demo-Kennungen ausschließlich über `.ai/identity/registry.json` (siehe `.ai/IDENTIFIER_REGISTRATION.md`).

# Anhang C – Versionsmatrix der 22 Fachdemos

| Demo | 2019 (CL 150) | 2022 (CL 160) | 2025 (CL 170) | Stufe | Sicherheit |
|---|---|---|---|---|---|
| OPT-002 | PASS | PASS | PASS | 1 | GREEN |
| OPT-003 | PASS | PASS | PASS | 1 | GREEN |
| OPT-005 | PASS | PASS | PASS | 1 | GREEN |
| OPT-009 | SKIP_VERSION | PASS | PASS | 1 | GREEN |
| OPT-010 | SKIP_VERSION | SKIP_VERSION | PASS | 1 | GREEN |
| OPT-013 | PASS | PASS | PASS | 2 | YELLOW |
| OPT-015 | PASS | PASS | PASS | 1 | GREEN |
| OPT-016 | PASS | PASS | PASS | 1 | GREEN |
| OPT-017 | PASS | PASS | PASS | 3 | YELLOW |
| QRY-001 | PASS | PASS | PASS | 1 | GREEN |
| QRY-004 | PASS | PASS | PASS | 1 | GREEN |
| QRY-013 | PASS | PASS | PASS | 1 | GREEN |
| IDX-006 | PASS | PASS | PASS | 2 | YELLOW |
| IDX-010 | PASS | PASS | PASS | 3 | YELLOW |
| CON-004 | PASS | PASS | PASS | 2 | YELLOW |
| CON-006 | PASS | PASS | PASS | 2 | YELLOW |
| CON-009 | PASS | PASS | PASS | 2 | YELLOW |
| DGN-003 | PASS | PASS | PASS | 1 | GREEN |
| DGN-005 | PASS | PASS | PASS | 2 | YELLOW |
| STL-008 | PASS | PASS | PASS | 3 | RED |
| STL-009 | PASS | PASS | PASS | 2 | YELLOW |
| RES-007 | PASS | PASS | PASS | 2 | YELLOW |

Je Demo besitzt der Matrixnachweis zwei vollständige Läufe je Version; die Evidenzläufe sind in `Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md` verlinkt.