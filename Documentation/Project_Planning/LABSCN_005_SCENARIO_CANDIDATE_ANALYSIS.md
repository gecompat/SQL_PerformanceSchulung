# LABSCN-005 – Kandidatenanalyse für weitere SQL_Server_Lab-Szenarien

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `LABSCN-005` |
| Status | `PROPOSED` |
| Stand | 2026-08-29 |
| Schulungsrepository | `gecompat/SQL_PerformanceSchulung` |
| Provisionierungsframework | `gecompat/SQL_Server_Lab` |
| geprüfte Lab-Modulversion | `0.2.0` |
| Zweck | späterer Analyse-, Planungs- und Entwicklungsvorrat; keine Implementierungsfreigabe |

## 1. Ziel und Statusgrenze

Diese Analyse sammelt weitere Schulungsbeispiele, deren technische Umgebung mit
`SQL_Server_Lab` bereitgestellt werden kann oder nach einer konkret benannten
Erweiterung bereitgestellt werden könnte. Sie ergänzt den bestehenden
Szenariovertrag und ändert weder die aktuelle Entwicklungsreihenfolge noch den
Status einer Demo.

Die Aufnahme eines Kandidaten in dieses Dokument bedeutet ausdrücklich nicht,
dass seine fachlichen Aussagen, Quellen, Runtime-Effekte oder Providerpfade
bereits validiert sind. Vor der Umsetzung benötigt jeder Kandidat einen eigenen
Szenariovertrag, ein Quellen-Delta-Review und die zutreffende Safety- und
Runtime-Abnahme.

## 2. Bewertungsgrundlage

Der aktuelle Containerpfad von `SQL_Server_Lab` stellt Docker und Podman,
SQL Server 2019, 2022 und 2025, mehrere Instanzen, feste Ressourcenprofile,
SQL-Memory, `MAXDOP`, Cost Threshold, TempDB- und Datenbankdateikonfiguration,
Query Store, Post-Provision-T-SQL sowie Start, Stop, Restart und Cleanup bereit.

Für die Kandidatenbewertung gelten folgende Einschränkungen:

- `resourceOverrides.maxMemoryMB` und `resourceOverrides.maxCpus` werden noch
  nicht in Providerlimits übernommen; Ressourcenversuche verwenden deshalb die
  belegten Profile `compact`, `standard` oder `performance`.
- `drives[].sizeLimitGB` ist bei Containern derzeit Metadatum und kein
  nachgewiesenes physisches Kapazitätslimit.
- Ein Drive-Typ oder getrenntes Volume beweist noch kein bestimmtes
  I/O-Latenzprofil oder ein getrenntes physisches Backing Device.
- Mehrere Instanzen desselben Containerproviders sind grundsätzlich möglich.
  Providerübergreifende direkte Containernetzwerke, allgemeine Network Faults
  und der breite Hyper-V-SQL-Pfad sind noch nicht freigegeben.
- `SQL_Server_Lab` verantwortet ausschließlich Infrastruktur und Lifecycle.
  Sessionreihenfolge, Workload, Assertions, Beobachtung und fachlicher Reset
  verbleiben in `SQL_PerformanceSchulung`.

## 3. Sofort vertiefbar mit bestehenden Lab-Fähigkeiten

Die Reihenfolge bewertet Lehrwert, bestehende Projektabhängigkeiten,
Reproduzierbarkeit und den zusätzlichen Nutzen der Lab-Provisionierung. Sie ist
keine Änderung an `NEXT_DEVELOPMENT_WAVES.md`.

| Rang | Demo-IDs | Szenario und Kernevidenz | Versionen | Safety | Topologie und Profil | Reset | Offene Analyse |
|---:|---|---|---|---|---|---|---|
| 1 | `DGN-003`, `DGN-004`, `DGN-005` | Kontrollierte Planregression; Query-, Plan-, Runtime- und Wait-Historie; Plan Forcing beziehungsweise Query Store Hints; begrenzte Extended-Events-Evidenz und vollständige Rücknahme | 2019–2025; Query Store Hints erst ab 2022 | Grün/Gelb | eine wegwerfbare Docker-/Podman-Instanz, `standard`, Query Store `READ_WRITE` | Query Store, XE-Session und Testdatenbank markergebunden zurücksetzen | Ereignisauswahl, Retention, Feature-Skips und planstabile Regression festlegen |
| 2 | `CON-006`, `DGN-005` | deterministischer Zwei-Session-Deadlock; Fehler 1205; Opfer, Prozesse und Ressourcen im `xml_deadlock_report`; geordnete Zugriffsvariante als Vergleich | 2019–2025 | Gelb | eine isolierte Instanz, zwei Akteure plus Beobachter | offene Transaktionen beenden, Sessions schließen, Datenzustand neu setzen | Session-Signale, Opfervertrag und begrenzte XE-Auswertung entwerfen |
| 3 | `OPT-017`, `RES-002` | parallele Planbereiche, Exchanges, Threadverteilung, Skew, operatorbezogene Zeiten und MAXDOP-Kontrast; optional DOP Feedback | 2019–2025; DOP Feedback ab 2022 und CL 160 | Gelb | eine `performance`-Instanz mit festem CPU-Profil | Workload stoppen, Datenbankkonfiguration und Query Store zurücksetzen | Datenverteilung, Zeitbudget und hardwareunabhängige Invarianten bestimmen |
| 4 | `OPT-014`, `RES-004`, `RES-007` | Required, Desired, Requested, Granted und Used Memory; Overgrant, Undergrant, Spill, konkurrierende Grants und `RESOURCE_SEMAPHORE`; Wait-Scope-Gegenprobe | 2019–2025; persistentes/perzentilbasiertes Feedback ab 2022 | Gelb | `standard` oder `performance`; begrenztes SQL-Memory; mehrere Sessions | Workload beenden, Sessions verifizieren, Query Store und Datenbank neu aufsetzen | Grant-Warten deterministisch erzeugen, ohne allgemeinen Speicherdruck vorzutäuschen |
| 5 | `CON-009` | TempDB-Allocation- und Metadaten-Contention; gleiche gegenüber ungeeigneten Dateilayouts; Mehrsession-Last; optional Memory-optimized TempDB Metadata | 2019–2025; 2025 zusätzlich TempDB-ADR und Space Governance untersuchen | Gelb | isolierte `performance`-Instanz, konfigurierbare TempDB-Dateien, Restart | Sessions und temporäre Objekte entfernen; für Instanzoptionen vollständiger Rebuild zulässig | Allocation, Metadaten, Worktables, Version Store und 2025-Funktionen getrennt schneiden |
| 6 | `CON-007`, `CON-008` | ADR, Persisted Version Store und Rollbackvergleich; auf 2025 zusätzlich TID Locks, Lock After Qualification, RCSI-Kontrast und Lockanzahl | 2019–2025; Optimized Locking nur 2025 | Gelb | eine isolierte Instanz, zwei bis drei Sessions | offene Transaktionen abbrechen, Datenbank neu erzeugen, Optionen zurücksetzen | PVS-Wachstum begrenzen und 2025-Skips sowie ADR-/RCSI-Voraussetzungen präzisieren |
| 7 | `STL-008`, `STL-009` | geplantes gegenüber kleinteiligem Logwachstum, VLF-Struktur, Einzelcommit gegenüber Batch-Commit, Log Flushes und `WRITELOG` | 2019–2025 | Gelb/Rot | wegwerfbare Containerinstanz mit definierten Log-Dateigrößen und Growth-Schritten | Testdatenbank entfernen oder gesamte Instanz verwerfen | VLF-Evidenz von nicht kontrollierbarer Storage-Latenz trennen; keine absoluten Laufzeitzusagen |
| 8 | `IDX-009`, `IDX-010` | Delta Store, Rowgroups, Delete Bitmap, Load-Qualität und Segment Elimination bei geordneter und ungeordneter Beladung | 2019–2025; erweiterte String-Segment-Elimination ab 2022 | Gelb | `performance`, skalierbare synthetische Datenmenge | Testdatenbank neu erzeugen | Datenmenge, Edition, Ladezeitbudget und relationale Erwartungswerte festlegen |
| 9 | `DGN-007` | Capstone „Zeitabhängige Regression eines Suchworkloads“ mit Query Store, Plan-, Parameter-, Wait- und XE-Evidenz sowie widerlegbaren Alternativhypothesen | 2019–2025 gemäß finalem Designvertrag | Gelb | eine isolierte `performance`-Instanz | vollständiger Incident-Reset und Rücknahme der Referenzmaßnahme | erst nach validiertem Query-Store-/XE-Pilot aus Rang 1 zulässig |
| 10 | `RES-003` | kontrollierter instanzweiter Speicherdruck, wartende Grants, `RESOURCE_SEMAPHORE` und Recovery-Nachweis | 2019–2025 | Rot | dedizierte Wegwerfinstanz, festes Ressourcenprofil, Kill-Switch | vollständiger Infrastrukturabbau | zuletzt und separat; High-Impact-Bestätigung und hartes Laufzeitbudget bleiben Pflicht |

### 3.1 Zusätzlich priorisierte fachliche Beispielschnitte

Die folgenden Schnitte ergänzen den Entwicklungsvorrat mit kleineren,
lehrzielgebundenen Beispielen. Sie verwenden ausschließlich bereits registrierte
Demo-IDs. Ihre Reihenfolge gilt nur innerhalb dieser Kandidatengruppe und ändert
weder `NEXT_DEVELOPMENT_WAVES.md` noch bestehende Freigabegates.

| Rang | Demo-ID | Beispiel und Kernevidenz | Versionen | Safety | Vorläufiger Quellenstatus | Offene Analyse |
|---:|---|---|---|---|---|---|
| 1 | `QRY-006` | NULL-Falle beim Anti-Join: `NOT IN` mit einem `NULL` in der Vergleichsmenge gegen das fachlich korrekte `NOT EXISTS`; Ergebnisvertrag und mögliche Planform getrennt bewerten | 2019–2025 | Grün | `SOURCE_REVIEW_REQUIRED`; Microsoft-Primärquellen zu `IN` und `EXISTS` in den regulären Quellenprozess übernehmen | deterministische Datensätze, Ergebnisassertion und planformunabhängige Kernaussage festlegen |
| 2 | `QRY-008` | Table-Variable-First-Execution-Trap: Compatibility Level 140 gegen 150, stark unterschiedliche erste und zweite Datenmengen sowie `#temp` als Gegenprobe; Schätzung, Joinwahl, Grant und Planwiederverwendung beobachten | 2019–2025; Deferred Compilation ab CL 150 | Grün | `SRC-007`, `SRC-008`, `SRC-011`; konkrete Runtimewirkung bleibt `EMPIRICAL` | Datenmengen so wählen, dass Erstkompilierung und Wiederverwendung sichtbar, aber nicht hardwareabhängig behauptet werden |
| 3 | `QRY-009` | Scalar-UDF-Inlining: kontrolliert inlinefähige und bewusst nicht inlinefähige Funktion mit identischem Ergebnis vergleichen; tatsächliches Inlining, Planintegration und Parallelisierbarkeit nachweisen | 2019–2025; CL 150+ für Scalar UDF Inlining | Grün | `SRC-007`, `SRC-008`; Plan- und Laufzeitwirkung bleibt eligibility- beziehungsweise workloadabhängig | robuste Eligibility-Gegenprobe und kontrollierten Feature-Skip definieren |
| 4 | `DGN-004` | Force, Failure und Unforce: zwei Query-Store-Pläne erzeugen, einen Plan erzwingen, eine Planvoraussetzung kontrolliert entziehen, Force-Failure und Fallback beobachten und anschließend vollständig zurücknehmen; Query Store Hints nur als 2022/2025-Zusatzpfad | 2019–2025; Query Store Hints ab 2022 | Gelb | `SRC-027`; Detailquellen zu Plan Forcing, Failure Reasons und Query Store Hints sind vor dem Design zu registrieren | deterministische Regression und Force-Failure ohne dauerhafte Objekt- oder Query-Store-Reste entwerfen |
| 5 | `IDX-007` | Last-Page-Contention: parallele Inserts mit sequenziellem Schlüssel, `PAGELATCH_EX` und Durchsatz messen und `OPTIMIZE_FOR_SEQUENTIAL_KEY` ein- und ausschalten | 2019–2025 | Gelb | `SOURCE_REVIEW_REQUIRED`; Microsoft-Primärquelle zu `OPTIMIZE_FOR_SEQUENTIAL_KEY` registrieren | Mehrsession-Last, Mindestkonkurrenz, Zeitbudget und kontrollierten Skip bei fehlendem Engpass festlegen |
| 6 | `OPT-014` | Oszillierendes Memory Grant Feedback: kleine und große Parameterwerte abwechseln; Grants, Spills, Feedbackzustand und mögliche Deaktivierung vergleichen; Persistenz und Perzentilmodus als 2022/2025-Zusatzpfad | 2019–2025; persistentes/perzentilbasiertes Feedback ab 2022 | Gelb | `SRC-009`, `SRC-010`, `SRC-050`; konkrete Grant- und Laufzeitwirkung bleibt `EMPIRICAL` | kontrollierte Oszillation, Query-Store-Zustand, Wiederholungszahl und Cleanup festlegen |

`OPT-006` bleibt zunächst ein Research Spike und keine zugesagte Runtime-Demo.
Der Spike vergleicht SQL Server 2019 als Baseline, SQL Server 2022 mit
Cardinality Estimation Feedback und SQL Server 2025 zusätzlich mit CE Feedback
für wiederkehrende Ausdrücke. Maßgeblich sind `SRC-006` bis `SRC-008` und
`SRC-061`. Vor einer Umsetzungsentscheidung müssen Eligibility,
Compatibility-Level, Query-Store-Voraussetzungen sowie tatsächlich verfügbare
Showplan-, Cache- oder Extended-Events-Evidenz reproduzierbar nachgewiesen sein.

Die empfohlene spätere Reihenfolge innerhalb dieser Kandidatengruppe lautet:
`QRY-006` → `QRY-008` → `QRY-009` → `DGN-004` → `IDX-007` → `OPT-014`.
Der `OPT-006`-Spike folgt erst danach oder wird mit dem bestehenden
SQL-Server-2025-Delta-Review verbunden.

### 3.2 Zweite fachliche Kandidatengruppe

Die zweite Kandidatengruppe ergänzt weitere kleine Schnitte, die in der ersten
Gruppe nicht enthalten sind. Vorhandene Legacy-Beispiele sind dabei nur
Rechercheausgangspunkte. Der spätere Demovertrag benötigt weiterhin einen
synthetischen, eigenständigen und gegen die Zielversionen geprüften Aufbau.

| Rang | Demo-ID | Beispiel und Kernevidenz | Versionen | Safety | Vorläufiger Quellenstatus | Offene Analyse |
|---:|---|---|---|---|---|---|
| 1 | `QRY-005` | OR-Aufteilung mit Doppelzählungsfalle: Ausgangsabfrage gegen naives `UNION ALL`, korrekt entkoppelte Zweige und `UNION`; Prüfsummen trennen fachliche Gleichheit von möglicher Laufzeitwirkung | 2019–2025 | Grün | `SOURCE_REVIEW_REQUIRED`; Microsoft-Primärquelle zur Duplikatsemantik von `UNION` und `UNION ALL` registrieren | überlappende Prädikate, identische Projektion und planformunabhängige Ergebnisevidenz festlegen |
| 2 | `QRY-002` | Richtung der impliziten Konvertierung: einmal wird die indexierte Spalte konvertiert, einmal nur der Parameter; `CONVERT_IMPLICIT`, Zugriffspfad, tatsächliche Zeilen und Reads gemeinsam beobachten | 2019–2025 | Grün | `SRC-030`; Quelle zur SARGability- und Planwarnungsdiagnose vor dem Design ergänzen; konkrete Planwirkung bleibt `EMPIRICAL` | Datentypkombinationen und Collation-Grenzen so wählen, dass die Konvertierungsrichtung eindeutig nachweisbar ist |
| 3 | `OPT-004` | Korrelierte Spalten ohne zusätzlichen Index: Einzelstatistiken gegen Mehrspaltenstatistik; Histogramm auf dem ersten Schlüssel, Density-Präfixe, Schätzung und Planwahl getrennt auswerten | 2019–2025 | Grün | `SRC-005`; Plan- und Laufzeitwirkung bleibt `EMPIRICAL` | synthetische Korrelation, Statistikreihenfolge und erwartete Schätzrichtung festlegen |
| 4 | `STL-003` | Lebenszyklus eines Forwarded Record: Heap mit kurzen Zeilen anlegen, variable Spalte vergrößern, Forwarded Records und Fetches nachweisen und über `ALTER TABLE ... REBUILD` kontrolliert zurücknehmen | 2019–2025 | Grün | `SRC-013`; Detailquelle für die verwendeten DMV-Zähler vor dem Design registrieren | Mindestdatenmenge, DMV-Scope, unabhängige Vorher-/Nachher-Zähler und Rebuild-Cleanup festlegen |
| 5 | `QRY-011` | Predicate-Implication-Labor: gefilterter Queue-Index für offene Einträge, passende und nicht implizierende Prädikate sowie eine deterministische Computed Column; unpassende `SET`-Option als kontrollierte Gegenprobe | 2019–2025 | Grün | `SOURCE_REVIEW_REQUIRED`; Primärquellen zu Filtered Indexes und Indizes auf Computed Columns registrieren | Filterprädikat, Determinismus, Präzision und zulässige `SET`-Optionen als getrennte Assertions schneiden |
| 6 | `IDX-005` | Missing Index ist kein Ausführungsauftrag: zwei Abfragen erzeugen überlappende Vorschläge; Vorschläge, vorhandene Indizes, Schlüsselreihenfolge, INCLUDE-Breite und DML-Kosten werden gemeinsam bewertet | 2019–2025 | Gelb | `SRC-032`; konkrete Empfehlung und DML-Wirkung bleiben `METHOD` beziehungsweise `EMPIRICAL` | Vorschlagserfassung, Indexkonsolidierung, DML-Gegenprobe und vollständiges Entfernen der Testindizes festlegen |
| 7 | `OPT-012` | Ein Adaptive-Join-Plan mit zwei Runtimeentscheidungen: derselbe gecachte Plan erhält kleine und große Eingabemengen; Schwelle und tatsächlicher Join-Typ werden nachgewiesen | 2019–2025; CL 140+ und Batch-Mode-Eligibility | Grün | `SRC-001`, `SRC-007`, `SRC-008`; tatsächliche Eligibility und Planform bleiben `EMPIRICAL` | planstabile Eingaben, Batch-Mode-Pfad und kontrollierten `SKIP_EVIDENCE_MISSING` definieren |
| 8 | `STL-010` | Kompressionsschätzung gegen tatsächliches Ergebnis: repetitive und schlecht komprimierbare Datenprofile mit NONE, ROW und PAGE vergleichen; Schätzung, tatsächliche Größe, Reads und CPU getrennt behandeln | 2019–2025 | Gelb | `SOURCE_REVIEW_REQUIRED`; Primärquelle zu `sys.sp_estimate_data_compression_savings` und Editionsgrenzen registrieren | Datenprofile, TempDB-Nutzung, Rebuild-Zeitbudget, Edition-Skip und Rückkehr zu NONE festlegen |

Die empfohlene spätere Reihenfolge innerhalb dieser zweiten Gruppe lautet:
`QRY-005` → `QRY-002` → `OPT-004` → `STL-003` → `QRY-011` → `IDX-005` →
`OPT-012` → `STL-010`. Auch diese Reihenfolge ändert die operative Folge in
`NEXT_DEVELOPMENT_WAVES.md` nicht.

### 3.3 Dritte fachliche Kandidatengruppe – deterministische Grundlagen

Diese Gruppe priorisiert kleine Einzelsession-Beispiele mit fachlich
deterministischen Ergebnissen. Planformen und Laufzeitwirkungen bleiben auch
hier empirische Evidenz und werden nicht aus der fachlichen Aussage abgeleitet.

| Rang | Demo-ID | Beispiel und Kernevidenz | Versionen | Safety | Vorläufiger Quellenstatus | Offene Analyse |
|---:|---|---|---|---|---|---|
| 1 | `QRY-003` | Mitternachtskante: künstliches Tagesende gegen halboffenes Intervall `>= @Start AND < @Folgetag`; Grenzwerte für `datetime` und `datetime2(7)` beweisen Ergebnis- und Präzisionsunterschiede | 2019–2025 | Grün | `SOURCE_REVIEW_REQUIRED`; Primärquellen zu Datums-/Zeitpräzision und Intervallsemantik registrieren | neutrale Grenzdaten, Datentypmatrix, Ergebnisassertion und SARGability-Gegenprobe festlegen |
| 2 | `QRY-007` | `DISTINCT` als Fehlermaskierung: fehlerhafter One-to-many-Join erzeugt Duplikate; `DISTINCT` verdeckt sie, während korrigierte Existenz- oder Aggregationslogik die fachlich richtige Menge liefert | 2019–2025 | Grün | `SOURCE_REVIEW_REQUIRED`; Primärquellen zu `DISTINCT` und Mengensemantik registrieren | fachliche Kardinalität, Duplikatursache, Ergebnisgleichheit und optionale Sort-/Hash-Evidenz trennen |
| 3 | `IDX-003` | Key-Reihenfolge ist nicht INCLUDE: `(Mandant, Status)` gegen `(Status, Mandant)` und INCLUDE-Varianten; Seek Predicate, Residual Predicate und Abdeckung getrennt beobachten | 2019–2025 | Grün | `SRC-012`; konkrete Zugriffspfade bleiben `EMPIRICAL` | vier ausgerichtete Abfragen, identische Ergebnismengen und Indexgrößen-Gegenprobe festlegen |
| 4 | `IDX-004` | Lookup-Kippkurve: schrittweise steigende Treffermenge führt workloadabhängig von Seek plus Lookup zu Scan; Covering Index als Gegenprobe | 2019–2025 | Grün | `SRC-012`; keine feste Tipping-Point-Prozentzahl ableiten | Selektivitätsleiter, beobachtete Umschaltstelle, Planformen und Ergebnisgleichheit festlegen |
| 5 | `IDX-001` | Zwei Row Locators: identische Tabellen als Heap und Clustered Table; RID Lookup, Key Lookup, Punkt- und Bereichszugriff vergleichen | 2019–2025 | Grün | `SRC-012`, `SRC-013`; Planwahl bleibt `EMPIRICAL` | gleiches Datenprofil, gleichwertige Nonclustered Indexes und locatorgebundene Planassertions definieren |
| 6 | `IDX-002` | Clustered-Key-Steuer: schmaler eindeutiger Schlüssel gegen breiten nicht eindeutigen Schlüssel; Größe der Nonclustered Indexes, Page Count und Uniquifier-Wirkung beobachten | 2019–2025 | Grün | `SRC-012`; konkrete Größenwirkung bleibt datenabhängig | Duplikatverteilung, Locatorbreite, unterstützte Metadaten und belastbare Größeninvarianten festlegen |
| 7 | `STL-001` | Zeilenbreitenleiter: feste, variable und nullable Spalten schrittweise ergänzen; durchschnittliche Record-Größe, Zeilen pro Seite und Page Count messen | 2019–2025 | Grün | `SRC-002`; konkrete Seitenauslastung bleibt `EMPIRICAL` | unterstützte Page-/Index-Metadaten, NULL-Verteilung und skalierbare Zeilenzahl festlegen |
| 8 | `STL-002` | Overflow-Grenze: dieselben Nutzdaten gezielt zwischen `IN_ROW_DATA`, `ROW_OVERFLOW_DATA` und `LOB_DATA` verschieben; Allocation Units und zusätzliche Reads nachweisen | 2019–2025 | Grün | `SRC-002`; Detailquelle für verwendete Katalog-/DMV-Zähler ergänzen | Datentypen, Zeilenbreite, Allocation-Unit-Assertions und Cleanup festlegen |

Die empfohlene spätere Reihenfolge lautet: `QRY-003` → `QRY-007` → `IDX-003`
→ `IDX-004` → `IDX-001` → `IDX-002` → `STL-001` → `STL-002`.

### 3.4 Vierte fachliche Kandidatengruppe – Planlebenszyklus und Concurrency

Diese Gruppe verbindet Mehrsession-Szenarien mit Planwiederverwendung und
Live-Diagnose. Jeder Concurrency-Schnitt benötigt benannte Signale, Timeout,
Kill-Switch, offene-Transaktions-Prüfung und vollständigen Reset.

| Rang | Demo-ID | Beispiel und Kernevidenz | Versionen | Safety | Vorläufiger Quellenstatus | Offene Analyse |
|---:|---|---|---|---|---|---|
| 1 | `CON-002` | Das gesperrte Nichts: `SERIALIZABLE` liest einen nicht vorhandenen Schlüssel; eine zweite Session versucht ihn einzufügen; Key-Range-Lock, Wait und Freigabe werden sichtbar | 2019–2025 | Gelb | `SRC-004` | Indexvoraussetzung, Range-Lock-Modus, Sessionreihenfolge und blockierungsfreie Gegenprobe festlegen |
| 2 | `CON-003` | Zwei Uhren des Row Versioning: RCSI liefert einen Statement-Snapshot, SNAPSHOT einen Transaction-Snapshot; ein konkurrierendes Update erzeugt anschließend einen kontrollierten Updatekonflikt | 2019–2025 | Gelb | `SRC-004`; konkrete Fehler- und Version-Store-Evidenz im Detaildesign prüfen | Datenbankoptionen, drei Sessionrollen, Konfliktvertrag und Rücknahme der Optionen festlegen |
| 3 | `CON-001` | Anomalien-Ledger: Dirty Read, Non-repeatable Read, Phantom und Lost Update mit denselben synthetischen Geschäftsdaten und expliziter Endzustandsprüfung | 2019–2025 | Gelb | `SRC-004` | vier Phänomene in getrennte Phasen schneiden und Isolation, Ergebnis sowie Endzustand je Phase assertieren |
| 4 | `CON-005` | `NOLOCK` bedeutet nicht keine Locks: Schema-Stability gegen Schema-Modification beobachten; Lock Escalation bleibt eine getrennte zweite Phase mit begrenzter Zeilenmenge | 2019–2025 | Gelb | `SRC-004`; Escalation bleibt ressourcen- und versionsabhängig | Sch-S-/Sch-M-Sequenz, begrenzte Lockzahl, XE- oder DMV-Evidenz und kontrollierten Skip festlegen |
| 5 | `OPT-008` | Gleiche Prozedur, gegensätzliche Kompilierungsreihenfolge: kleiner und großer Parameterwert erzeugen je nach Erstkompilierung gegensätzliche Plan- und Read-Profile | 2019–2025 | Grün | `SRC-001`, `SRC-007`, `SRC-046`, `SRC-047`; Runtimewirkung bleibt `EMPIRICAL` | ausschließlich querygebundene Cache-Rücknahme, kompilierte Parameterwerte und zwei Reproduktionsrichtungen festlegen |
| 6 | `OPT-007` | Literal Storm: viele semantisch gleiche Literalabfragen gegen `sp_executesql`; Cacheeinträge, Use Counts und Cachegröße vergleichen, ohne den gesamten Instanzcache zu leeren | 2019–2025 | Gelb | `SRC-001`, `SRC-046`; Cachewirkung bleibt `EMPIRICAL` | markergebundene Querytexte, querylokale Cleanup-Strategie und harte Obergrenze der Statements festlegen |
| 7 | `OPT-011` | Row-Goal-Triangulation: `TOP`, `FAST n` und `EXISTS` gegen eine kontrollierte `DISABLE_OPTIMIZER_ROWGOAL`-Gegenprobe; Ergebnismenge, Plan und tatsächliche Arbeit gemeinsam bewerten | 2019–2025 | Grün | `SRC-001`, `SRC-041`; Primärquelle zum Hint im Detailreview ergänzen | reproduzierbare frühe Trefferverteilung und `SKIP_EVIDENCE_MISSING` bei ausbleibender Planwirkung definieren |
| 8 | `DGN-002` | Session–Request–Task-Mikroskop: eine bewusst wartende oder parallele Abfrage von Session über Request und Tasks bis zu Wait Resource und Statementtext verfolgen | 2019–2025 | Grün | `SRC-028`, `SRC-036`; Detailquellen zu Request- und Task-DMVs ergänzen | kurzlebige Beobachtung stabilisieren, Rechte differenzieren und reale Umgebungsdaten aus Ausgaben ausschließen |

Die empfohlene spätere Reihenfolge lautet: `CON-002` → `CON-003` → `CON-001`
→ `CON-005` → `OPT-008` → `OPT-007` → `OPT-011` → `DGN-002`.

### 3.5 Fünfte fachliche Kandidatengruppe – Evidenz, Storage und Ressourcen

Diese Gruppe beginnt mit grünen Evidenz- und Metadatenbeispielen und endet mit
ressourcenabhängigen gelben Schnitten. Instanzweite Cache- oder
Ressourcenoperationen sind ausschließlich in bestätigter Wegwerfinfrastruktur
zulässig.

| Rang | Demo-ID | Beispiel und Kernevidenz | Versionen | Safety | Vorläufiger Quellenstatus | Offene Analyse |
|---:|---|---|---|---|---|---|
| 1 | `OPT-001` | Evidenzleiter: Estimated Plan, Actual Plan und Runtime-Messung derselben Abfrage; klar trennen, welche Zeilen-, Warnungs- und Ressourceninformationen erst nach Ausführung existieren | 2019–2025 | Grün | `SRC-001`, `SRC-031` | stabile Planattribute, Clientunabhängigkeit und bewusst erzeugte Schätzabweichung festlegen |
| 2 | `DGN-001` | Fairer A/B-Vergleich: identische Prüfsumme, abwechselnde Ausführungsreihenfolge, Warm-up und mehrere Wiederholungen; IO, CPU und Elapsed Time getrennt behandeln | 2019–2025 | Grün | `SRC-001`, `SRC-031`; Primärquellen zu `STATISTICS IO/TIME` ergänzen | Messprotokoll, Wiederholungszahl, akzeptierte Streuung und keine universelle Gewinneraussage festlegen |
| 3 | `STL-004` | Vom Objekt bis zur Seite: `sys.partitions`, `sys.allocation_units`, Page Allocations und `sys.dm_db_page_info` zu einer unterstützten Metadatenkette verbinden, ohne `DBCC PAGE` | 2019–2025 | Grün | `SRC-002`, `SRC-019`; Detailquellen für Allocation- und Page-DMVs ergänzen | Objekt-/Index-/Partition-/Allocation-/Page-Zuordnung und Berechtigungen festlegen |
| 4 | `STL-007` | Rollback ist protokollierte Arbeit: während einer Transaktion Log Record Count und Log Bytes messen, anschließend rollbacken und Checkpoint-/Recovery-LSN getrennt betrachten | 2019–2025 | Grün | `SRC-033`; Detailquellen für Transaktions- und Log-DMVs ergänzen | unterstützte Zähler, Recovery Model, Checkpointgrenze und Ergebniszustand nach Rollback festlegen |
| 5 | `QRY-010` | Window-Frame-Falle: Running Total mit doppelten Sortierschlüsseln unter implizitem `RANGE` gegen explizites `ROWS`; Cursor nur als optionale ergebnisgleiche Gegenprobe | 2019–2025 | Gelb | `SOURCE_REVIEW_REQUIRED`; Primärquelle zur `OVER`-Klausel registrieren | fachlich erwartete Frames, stabile Sortierung, Prüfsummen und Zeitbudget der prozeduralen Gegenprobe festlegen |
| 6 | `IDX-008` | Gleiches Ergebnis, anderes physisches Format: NONE, ROW und PAGE auf zwei Datenprofilen; Page Count, Reads und DML-Kosten messen | 2019–2025 | Gelb | `SOURCE_REVIEW_REQUIRED`; Primärquellen zu Row-/Page-Compression und Editionen registrieren | repetitive und schlecht komprimierbare Profile, CPU-/I/O-Trennung, Rebuild-Budget und Cleanup festlegen |
| 7 | `STL-006` | Cold/Warm ohne Kollateralschaden: physische und logische Reads auf einer frischen Wegwerfinstanz vergleichen; `DBCC DROPCLEANBUFFERS` nur isoliert und bestätigt | 2019–2025 | Gelb | `SOURCE_REVIEW_REQUIRED`; Primärquellen zu Buffer Pool und Cacheleerung registrieren | instanzweite Wirkung, exklusives Profil, Checkpoint, Wiederholungen und vollständigen Rebuild festlegen |
| 8 | `RES-001` | Begrenzte CPU-Last: CPU-lastige Abfrage mit Zeitbudget und Kill-Switch; Worker, Scheduler und `SOS_SCHEDULER_YIELD` beobachten | 2019–2025 | Gelb | `SRC-001`, `SRC-035`; Detailquelle zum Wait und Scheduler ergänzen | hardwareunabhängige Kernassertion und `SKIP_EVIDENCE_MISSING` bei ausbleibender Wait-Evidenz festlegen |

Die empfohlene spätere Reihenfolge lautet: `OPT-001` → `DGN-001` → `STL-004`
→ `STL-007` → `QRY-010` → `IDX-008` → `STL-006` → `RES-001`.

## 4. Bedingt umsetzbare Kandidaten

| Demo-IDs | Möglichkeit | Vor Umsetzung nachzuweisender Spike | Aktuelle Einordnung |
|---|---|---|---|
| `QRY-012` | zwei SQL-Server-Container für Linked Server, Remote Pushdown, Collation- und Verschlüsselungskontraste | direkte Erreichbarkeit über das providergebundene Labnetz, OLE-DB-Treiber, TLS-/Zertifikatsverhalten, SQL-2025-Providerparameter und Docker-/Podman-Parität | gleicher Provider wahrscheinlich ausreichend; noch kein freigegebener Szenariopfad |
| `STL-005` | Files, Filegroups, Proportional Fill und Autogrowth | logische File-Verteilung zunächst getrennt von physischer Storagewirkung beweisen | logischer Teil im Container möglich; physischer Storagevergleich zurückgestellt |
| `DGN-006`, `RES-007` | hohe Sessionzahl, Host-/Clientmetriken und reproduzierbares `ASYNC_NETWORK_IO` | kontrollierter Workload-Client, Client-Pacing, Abbruch und maschinenunabhängiger Netzwerk-Wait-Vertrag | Runner- oder zusätzliche Clientkomponente erforderlich |
| `CON-009`, `RES-004` | SQL-Server-2025-TempDB-Space-Governance | Resource-Governor-Konfiguration, Workloadklassifizierung, sichere Space-Grenze und vollständige Rücknahme | T-SQL-seitig plausibel; eigener roter beziehungsweise gelber Safety-Schnitt erforderlich |

Für diese Zeilen gilt `SOURCE_REVIEW_REQUIRED`, bis die versions- und
providerbezogenen Aussagen im Source Register geprüft und dem jeweiligen
Szenariovertrag zugeordnet sind.

## 5. Zukünftige Szenarien mit Lab-Fähigkeitslücke

| Demo-IDs oder Erweiterung | Zielbild | Fehlende beziehungsweise noch nicht freigegebene Lab-Fähigkeit |
|---|---|---|
| `RES-005`, `RES-006`, physischer Teil von `STL-005` | `PAGEIOLATCH_*` gegenüber `PAGELATCH_*`, kontrollierte Daten- und Loglatenz sowie getrennte Backing Devices | belastbare I/O-Profile, physische Storage-Bindung, Kapazitätsgrenzen und providerbezogene Messung; voraussichtlich Hyper-V oder native Linux-Lane |
| `RES-007` mit Netzwerkfault | kontrollierte Latenz, Bandbreite, Abbruch und Client-Gegenprobe | Network-Fault-Controller beziehungsweise `netem`-ähnliche, reversible und scopegebundene Capability |
| Erweiterung von `DGN-003` | Query Store auf lesbaren Secondary Replicas unter SQL Server 2025 | vollständig validierte Availability-Group-/Mehrinstanztopologie, Endpunkte, Zertifikate, Failover und Cleanup |
| `DGN-006` auf Windows | SQL- und OS-Metriken, Windows-spezifische Clients oder Authentifizierung | breit freigegebener Hyper-V-SQL-Pfad mit reproduzierbarer Gast-, Netzwerk- und Storage-Konfiguration |
| providerübergreifende Variante von `QRY-012` | direkter SQL-Verkehr zwischen Docker, Podman und gegebenenfalls Hyper-V | gemeinsames providerübergreifendes Netzwerk, IPAM und Exposure-Vertrag |

Auch diese Zeilen gelten vollständig als `SOURCE_REVIEW_REQUIRED`. Eine
Fähigkeitslücke autorisiert keine Änderung in `SQL_Server_Lab`; sie muss zuerst
in einem konkreten Szenariodesign technisch belegt und danach ausdrücklich
freigegeben werden.

## 6. Empfohlene spätere Analysefolge

Die bestehende operative Reihenfolge bleibt maßgeblich. Nach dem ersten
vollständigen `LABSCN-003`-Vertical-Slice kann `LABSCN-005` in dieser Folge
vertieft werden:

1. Query-Store-/Extended-Events-Pilot aus `DGN-003` bis `DGN-005`;
2. `CON-006` als zweites, klar beobachtbares Multi-Session-Szenario;
3. `OPT-017` sowie `OPT-014`/`RES-004` als ressourcengebundene Containerfälle;
4. `CON-009`, `CON-007` und `CON-008` als versionsabhängige Instanz- und
   Concurrency-Schnitte;
5. Log- und Columnstore-Szenarien;
6. bedingte Spikes;
7. rote und infrastrukturell erweiterte Szenarien zuletzt.

## 7. Pflichtfelder der späteren Detailanalyse

Für einen ausgewählten Kandidaten werden vor Implementierungsbeginn mindestens
festgelegt:

- Lernziel, Fehlannahme und fachliche Kernaussage;
- zugehörige Demo-, LAB- und Claim-IDs;
- SQL-Server-Versionen, Compatibility Levels, Edition und Feature-Skips;
- Provider, Instanzen, Ressourcenprofil, Sessions und Clientrollen;
- deterministischer Ausgangszustand und Erzwingungslogik;
- Beobachtungen, Gegenproben und hardwareunabhängige Invarianten;
- Safety-Klasse, Timeout, Kill-Switch, Recovery und vollständiger Cleanup;
- `READY_FOR_USER`-Übergabe, Resetstrategie und automatisierter Smoke-Test;
- Quellenstatus und erforderliches Source-Register-Delta;
- konkrete Lab-Fähigkeitslücke mit technischem Nachweis, falls vorhanden.

## 8. Quellen- und Evidenzstatus

Bereits im Source Register verankerte Grundlagen sind insbesondere `SRC-003`,
`SRC-004`, `SRC-007` bis `SRC-010`, `SRC-015` bis `SRC-017`, `SRC-020` bis
`SRC-022`, `SRC-025`, `SRC-027` bis `SRC-029` sowie `SRC-033` bis `SRC-036`.

Vor einer fachlichen Freigabe sind mindestens folgende zusätzliche oder
aktualisierte Microsoft-Primärquellen im regulären Quellenprozess zu prüfen:

- [Deadlocks Guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide?view=sql-server-ver17);
- [Degree of parallelism feedback](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-degree-parallelism-feedback?view=sql-server-ver17);
- [Accelerated database recovery](https://learn.microsoft.com/en-us/sql/relational-databases/accelerated-database-recovery-concepts?view=sql-server-ver17);
- [Transaction Log Architecture and Management Guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide?view=sql-server-ver17);
- [TempDB space resource governance](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/tempdb-space-resource-governance?view=sql-server-ver17).

Diese Links sind Rechercheausgangspunkte und noch keine neue Freigabe im Source
Register. Der Status bleibt daher für die betroffenen Aussagen
`SOURCE_REVIEW_REQUIRED`.
