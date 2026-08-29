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
