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

### 3.6 Sechste fachliche Kandidatengruppe – Execution-Plan-Operatoren-Labor

Diese Kandidatengruppe bereitet ein eigenständiges, synthetisches
Operatoren-Labor vor. Der Anwender soll für wichtige Showplan-Operatoren jeweils
eine kleine Beispielabfrage, die auslösende Daten- und Indexkonstellation, eine
fachliche Erklärung und die maßgeblichen Planproperties erhalten. Das Labor ist
kein vollständiges Operatorlexikon und verspricht keine universell feste
Planform. Es ergänzt die vorhandenen Themen, ohne neue Demo-IDs oder eine neue
Wellenreihenfolge einzuführen.

#### 3.6.1 Gemeinsame Datenbasis

Die spätere Implementierung verwendet eine ausschließlich durch `FWK-002`
markierte Testdatenbank und erzeugt die Faktbasis deterministisch mit `FWK-003`.
Öffentliche Beispieldatenbanken und nicht mitgelieferte Datenquellen sind keine
Voraussetzung. Als Ausgangsprofil gilt:

- `lab.SyntheticFact` mit 100.000 Faktzeilen, 1.000 Schlüsseln,
  reproduzierbarer Verteilung und 200 Bytes Payload; als Referenzparameter
  gelten `Seed = 12012`, `SkewPercent = 80`, `HotKeyPercent = 20`,
  `CorrelationPercent = 80`, `StartDate = 20200101` und
  `DateSpanDays = 3650`;
- `lab.OperatorDimension` mit genau einem Dimensionsdatensatz je verwendetem
  Schlüssel;
- `lab.OperatorHeap` als fachlich identische Heap-Kopie eines begrenzten
  Ausschnitts der Faktzeilen;
- wenige explizit benannte Nonclustered Indexes, davon jeweils eine abdeckende
  und eine nicht abdeckende Variante für die Lookup-Gegenprobe;
- keine zufälligen Werte, keine Systemkataloge als Zahlenquelle und keine
  Abhängigkeit von physischer Page-Verteilung oder einer bestimmten Hardware.

Das Profil ist eine parametrisierte Vorlage und wird je Demo-ID und Run-Token in
der jeweils eigenen markierten Testdatenbank aufgebaut. Es entsteht keine
dauerhafte, demoübergreifend veränderliche Gemeinschaftsdatenbank.

Jede Beispielabfrage erhält einen markergebundenen Query-Kommentar, eine
deterministische Ergebnisassertion und eine unabhängige Cleanup- beziehungsweise
Resetmöglichkeit. Der tatsächliche Ausführungsplan wird über den bestehenden
`FWK-005`-Pfad beobachtet; ein Estimated Plan allein ist keine Runtimeevidenz.

#### 3.6.2 Kandidatenmatrix für spätere Beispielskripte

| Rang | Zuordnung | Daten- oder Abfragekonstellation | Erwartete Kernevidenz | Erklärung für den Anwender | Evidenzklasse |
|---:|---|---|---|---|---|
| 1 | `OPT-001`, `IDX-001` | vollständige Aggregation über `lab.OperatorHeap` | `Table Scan` | Ein Heap besitzt keinen Clustered Index; ohne geeigneten alternativen Zugriff wird die Heapstruktur gelesen. | `REQUIRED` |
| 2 | `OPT-001`, `IDX-001` | breite Abfrage über einen großen Anteil von `lab.SyntheticFact` | `Clustered Index Scan` | Ein Scan kann bei großer Treffermenge günstiger sein als viele Einzelzugriffe; ein Scan ist nicht grundsätzlich ein Fehler. | `ELIGIBLE` |
| 3 | `OPT-001`, `IDX-003` | breite, vollständig durch einen schmalen Nonclustered Index abgedeckte Projektion | `Index Scan` | Der schmalere Index kann vollständig gelesen werden, ohne die breitere Basistabelle zu verwenden. | `ELIGIBLE` |
| 4 | `OPT-001`, `IDX-003` | Gleichheits- und Bereichsprädikat auf einem selektiven indizierten Schlüssel | `Index Seek` oder `Clustered Index Seek`; `Seek Predicates`, optionales Restprädikat | Der Seek grenzt den Schlüsselbereich ein. Gelesene und zurückgegebene Zeilen sowie Seek- und Residual-Prädikate werden getrennt bewertet. | `REQUIRED` |
| 5 | `IDX-001`, `IDX-004` | selektiver nicht abdeckender Nonclustered Index auf der Clustered Table; Payload wird projiziert | `Index Seek`, `Nested Loops`, `Key Lookup`; Ausführungsanzahl des Lookups | Der Nonclustered Index findet Row Locators, fehlende Spalten werden aus dem Clustered Index nachgeladen. Erst viele Lookups können problematisch werden. | `ELIGIBLE` |
| 6 | `IDX-001` | gleiche nicht abdeckende Abfrage auf `lab.OperatorHeap` | `Index Seek`, `Nested Loops`, `RID Lookup` | Ohne Clustered Key verweist der Nonclustered Index über die physische Row-ID auf die Heapzeile. | `ELIGIBLE` |
| 7 | `IDX-003`, `IDX-004` | abdeckenden Index für die Lookup-Abfrage ergänzen und anschließend wieder entfernen | Seek ohne Lookup; identische Ergebnismenge | Die Gegenprobe trennt Zugriff und Abdeckung: Alle benötigten Spalten liegen im Index, daher ist kein zusätzlicher Locatorzugriff erforderlich. | `ELIGIBLE` |
| 8 | `OPT-012` | höchstens zehn äußere Zeilen gegen eine große, auf dem Joinschlüssel indizierte innere Eingabe | `Nested Loops`, Outer References und innere Ausführungsanzahl | Die innere Suche wird für jede äußere Zeile ausgeführt. Kleine äußere Mengen und ein geeigneter innerer Index begünstigen diesen Algorithmus. | `ELIGIBLE` |
| 9 | `OPT-012` | zwei größere, auf dem Joinschlüssel geordnete Eingaben | `Merge Join`; geordnete Inputs oder vorgeschalteter `Sort` | Der Algorithmus führt zwei geordnete Datenströme zusammen. Ein zusätzlich erforderlicher Sort kann den Vorteil verändern. | `ELIGIBLE` |
| 10 | `OPT-012` | größere unsortierte Eingaben ohne passenden Joinindex | `Hash Match` mit Build- und Probe-Seite | Eine Eingabe bildet die Hashtabelle, die andere wird dagegen geprüft. Memory Grant und mögliche Spills gehören zur Erklärung. | `ELIGIBLE` |
| 11 | `OPT-012` | gleiche Ergebnismenge mit kontrollierten querylokalen `LOOP`, `MERGE`- und `HASH`-Gegenproben | drei physische Joinalgorithmen, identische Prüfsumme | Joinhints dienen nur als didaktische Mechanik. Sie sind keine Produktionsvorgabe und beweisen nicht, dass der erzwungene Plan günstiger ist. | `CONTROLLED` |
| 12 | `OPT-012` | kleine und große Runtimeeingabe bei Batch-Mode- und Compatibility-Level-Eligibility | `Adaptive Join`, Schwelle und tatsächlich gewählter Join-Typ | Der Join verschiebt die Wahl zwischen Nested Loops und Hash Join bis zur Laufzeit. Fehlende Eligibility ist ein kontrollierter `SKIP_EVIDENCE_MISSING`. | `ELIGIBLE` |
| 13 | `OPT-001` | `GROUP BY` entlang einer passenden Indexreihenfolge | `Stream Aggregate`; geordnete Eingabe | Bereits geordnete Zeilen können gruppenweise verarbeitet werden, ohne zuerst eine Hashtabelle aufzubauen. | `ELIGIBLE` |
| 14 | `OPT-001` | `GROUP BY` auf einem nicht geordneten Schlüssel; querylokale `HASH GROUP`-Gegenprobe | `Hash Match` als Aggregate | Gruppen werden in einer Hashtabelle gebildet. Grant, tatsächliche Gruppenanzahl und Spillwarnungen werden gemeinsam betrachtet. | `ELIGIBLE` |
| 15 | `OPT-013` | `ORDER BY` ohne passende Indexordnung | `Sort`; Eingabezeilen, Speichergrant und Spillstatus | Der Operator ordnet die gesamte relevante Eingabe. Das vorhandene `OPT-013`-Spill-Labor bleibt die Vertiefung. | `REUSED` |
| 16 | `OPT-011` | `TOP (n)` mit `ORDER BY` ohne passende Indexordnung | `Top` und `Sort` mit Top-N-Eigenschaft oder zulässige äquivalente Planform | Nur die ersten Zeilen der gewünschten Ordnung werden benötigt; das Row Goal kann weitere Planentscheidungen beeinflussen. | `ELIGIBLE` |
| 17 | `QRY-005` | zwei disjunkte Teilmengen mit `UNION ALL` | `Concatenation`; alle Eingabezeilen bleiben erhalten | `UNION ALL` verbindet Datenströme ohne Duplikatentfernung. Die fachliche Disjunktheit wird unabhängig vom Plan geprüft. | `REQUIRED` |
| 18 | `QRY-005`, `QRY-007` | überlappende Teilmengen mit `UNION` beziehungsweise eine kontrollierte `DISTINCT`-Abfrage | `Sort` mit Distinct-Eigenschaft oder `Hash Match` als Aggregate | Duplikatentfernung kann physisch unterschiedlich umgesetzt werden und darf keinen fehlerhaften Join verdecken. | `ELIGIBLE` |
| 19 | `OPT-001` | kleine Zeilenmenge aus einem `VALUES`-Konstruktor | `Constant Scan` | Konstante Zeilen werden ohne Zugriff auf eine Benutzertabelle in den Plan eingebracht. | `REQUIRED` |
| 20 | `OPT-001` | skalare Berechnung aus mindestens einer Tabellenspalte | `Compute Scalar` und definierte Ausgabeliste | Der Operator beschreibt einen skalaren Ausdruck. Laufzeitarbeit kann in andere Operatoren verschoben werden, daher ist fehlende Runtimezeit am Symbol kein Beweis für fehlende Arbeit. | `ELIGIBLE` |
| 21 | `OPT-001`, `QRY-010` | abgeleitete Tabelle mit `ROW_NUMBER()` und äußerem Prädikat auf die berechnete Zeilennummer | `Filter` und dessen Predicate-Property | Ein Filter verwirft Zeilen aus seinem Eingang. Andere Prädikate können dagegen direkt in einen Scan oder Seek verschoben werden, weshalb nicht jede `WHERE`-Klausel ein eigenes Filtersymbol erzeugt. | `ELIGIBLE` |
| 22 | `OPT-001` | skalare Unterabfrage ohne nachweisbare Eindeutigkeit, deren Testdaten zunächst genau einen Treffer liefern | `Stream Aggregate` und `Assert`; optionale Duplikatphase endet kontrolliert | `Assert` schützt die Semantik, dass die skalare Unterabfrage höchstens eine Zeile liefert. Die Fehlergegenprobe wird in einer rücknehmbaren Phase ausgeführt. | `ELIGIBLE` |
| 23 | `QRY-006` | fachlich gleichwertige `EXISTS`- und `NOT EXISTS`-Abfragen einschließlich NULL-Gegenprobe | logischer Semi- beziehungsweise Anti-Semi-Join; variabler physischer Algorithmus | Existenzprüfungen benötigen nicht alle passenden Zeilen oder Spalten. Logische und physische Planform werden ausdrücklich getrennt. | `ELIGIBLE` |
| 24 | `QRY-010` | `ROW_NUMBER()` mit `PARTITION BY` und stabiler Ordnung | `Segment`, `Sequence Project` oder versionsabhängige äquivalente Window-Planform | Die Eingabe wird in Partitionen gegliedert und innerhalb jeder Partition nummeriert. | `ELIGIBLE` |
| 25 | `QRY-010` | laufende Summe mit doppelten Sortierschlüsseln: implizites `RANGE` gegen explizites `ROWS` | `Window Aggregate`, `Window Spool` oder zulässige äquivalente Planform; unterschiedliche fachliche Ergebnisse | Der Window Frame bestimmt, welche Zeilen zur aktuellen Zeile gehören. Operator und Ergebniseffekt müssen getrennt erklärt werden. | `ELIGIBLE` |
| 26 | `OPT-016` | vorhandener korrelierter Apply-/Nested-Loops-Schnitt | Spool, Rebind, Rewind und Outer References | Zwischenergebnisse können wiederverwendet werden; ein Spool ist weder automatisch gut noch automatisch schlecht. | `REUSED` |
| 27 | `OPT-017` | vorhandener ausreichend paralleler Schnitt | `Parallelism` mit Distribute-, Repartition- oder Gather-Streams, Actual DOP und Threadarbeit | Exchanges verteilen oder sammeln Zeilen zwischen Workern. Ohne tatsächliche Parallelismusevidenz bleibt der Lauf kontrolliert unfreigegeben. | `REUSED` |
| 28 | `OPT-012`, `OPT-017` | selektiver Bitmapfilter in einem ausreichend parallelen Hash-Join-Plan | `Bitmap` und tatsächliche Zeilenreduktion | Der Optimierer kann Zeilen früh verwerfen. Die Planform ist ressourcen- und kostenabhängig und wird nicht erzwungen behauptet. | `ELIGIBLE` |
| 29 | `IDX-010` | vorhandene Columnstore-Demo mit geordnetem Prädikat | Columnstore Scan und Segment-Eliminationsevidenz | Metadaten und tatsächliche Segmentzugriffe erklären, warum nicht jedes Segment gelesen werden muss. | `REUSED` |

`REQUIRED` bezeichnet eine durch Abfragesemantik und kontrollierten Objektaufbau
zu erwartende Kernevidenz. `ELIGIBLE` bezeichnet eine kosten-, versions- oder
ressourcenabhängige Planform; ihr Ausbleiben führt nicht zu einer falschen
`PASS`-Aussage, sondern gegebenenfalls zu `SKIP_EVIDENCE_MISSING`. `CONTROLLED`
kennzeichnet ausschließlich didaktische, querylokale Hints oder Gegenproben.
`REUSED` verweist auf einen bereits vorhandenen beziehungsweise separat
geplanten Demovertrag und verhindert doppelte Spezialdemos.

#### 3.6.3 Erklär- und Artefaktvertrag

Jedes spätere Beispielskript dokumentiert in derselben Reihenfolge:

1. Lernfrage und häufige Fehlannahme, etwa „Seek ist immer gut“ oder „Scan ist
   immer schlecht“;
2. minimale Daten-, Index- und Abfragekonstellation;
3. fachlich erwartete Ergebnismenge oder Prüfsumme;
4. erwartete logische und physische Operatorfamilie sowie zulässige Varianten;
5. zu prüfende Properties, mindestens geschätzte und tatsächliche Zeilen,
   Ausführungsanzahl, Prädikate, Ordnung, Grant und vorhandene Warnungen;
6. Erklärung, weshalb der Operator in dieser Konstellation plausibel ist und
   welche Aussage daraus ausdrücklich nicht folgt;
7. Gegenprobe, Reset und Cleanup.

Die spätere Umsetzung soll mindestens ein Setupskript, thematisch kleine
Abfrageskripte, einen statischen Vertrag, einen Runtime-Runner und einen
Katalogeintrag liefern. Abfragen mit gleichem fachlichem Ziel weisen ihre
Ergebnisgleichheit unabhängig von der Planform nach. DML-Operatoren können in
einem späteren Zusatzschnitt ausschließlich innerhalb einer expliziten
Transaktion mit `ROLLBACK` ergänzt werden; sie gehören nicht zum ersten
Operatoren-Labor.

#### 3.6.4 Quellen- und Umsetzungsgrenze

Vor dem Detaildesign werden mindestens die Microsoft-Primärquellen zur
Showplan-Operatorreferenz, zu physischen Joinalgorithmen, zu Actual Execution
Plans, zur `OVER`-Klausel sowie zu `UNION` und `UNION ALL` über den regulären
Source-Register- und Registry-Prozess aufgenommen. Bis dahin ist die gesamte
Gruppe `SOURCE_REVIEW_REQUIRED`. `SRC-001` und der bestehende `FWK-005`-Vertrag
bilden bereits die allgemeine Grundlage für Optimierer-, Plan- und
Runtimeaussagen.

Die empfohlene spätere Implementierungsfolge lautet:

1. Zugriffe, Lookups und Abdeckung;
2. Nested Loops, Merge und Hash Join mit identischer Ergebnisevidenz;
3. Aggregate, Sort, Top, Concatenation und Duplikatentfernung;
4. Constant Scan, Compute Scalar, Assert sowie Semi-/Anti-Joins;
5. Window-Operatoren;
6. Verweise auf Spool-, Parallelism-, Bitmap- und Columnstore-Vertiefungen.

Eine Implementierung wird erst freigegeben, nachdem der Detailvertrag die
zulässigen Planvarianten festgelegt hat. `VALIDATED` setzt je zwei erfolgreiche
Runtime-Läufe auf SQL Server 2019, 2022 und 2025 voraus; kontrollierte Skips
halten den Workflow wahrheitsgetreu, ersetzen aber keine fehlende Kernevidenz.

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
