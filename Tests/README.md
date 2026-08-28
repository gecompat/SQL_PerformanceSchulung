# Tests

## Aktive SQL-Server-unabhängige Prüfungen

Der Workflow `.github/workflows/framework-contracts.yml` ist auf Framework-, Demo-Vertrags- und statische Testpfade begrenzt. Er führt aus:

```bash
python Tests/Static/validate_framework_contracts.py
python Tests/Static/test_result_contract_evaluator.py
python Tests/Static/validate_orchestration_runtime.py
python Tests/Static/test_orchestration_runtime.py
```

Die Prüfungen kontrollieren Pflichtdateien, Statuscodes, Eigentumsmarker, deterministische Generatorregeln, T-SQL-Lexik, Python-Syntax, JSON-Metadaten, Ergebnisverträge, Prozesssteuerung, Safety-Gates, Query-Store- und XE-Verträge sowie Cleanup-Priorität. Die Prozess-Selbsttests verwenden ein synthetisches `sqlcmd`-Ersatzprogramm und benötigen weder Netzwerk noch SQL Server.

## Kennungsregistrierung

```bash
python Tests/Static/validate_identifier_registration.py
```

Die Prüfung sichert die zentrale Registry im Profil `foundation-artifact-registry/v2`, die vollständige Übernahme der 211 historischen Kennungen, die unveränderten UUID-Zuordnungen von `DEC-061` und `DEC-062`, die `TSK-###`-Nomenklatur sowie die Regel, dass neue Wellen nicht als Kennungen alloziert werden. Sie verbietet v1-Zähler, Revisionsfelder und getrennte Artefaktdatensätze. Als `PROJECT_SEMANTIC`-Prüfung ergänzt sie das Foundation-Semantiktool und die Foundation-Integritätsprüfung.

## Curriculum- und Privacy-Prüfung

Der Workflow `.github/workflows/privacy-metadata.yml` startet keinen SQL Server und führt aus:

```bash
python3 Tests/Static/validate_adv_003_curriculum.py
python3 Tests/Static/test_privacy_metadata_scanner.py
python3 Tests/Static/validate_privacy_metadata.py .
```

`validate_adv_003_curriculum.py` prüft den unveränderten 84-Folien-Kern, die 39 geplanten Vertiefungsclaims, neun neue Vertiefungslernziele und ihre eindeutige Traceability. Sieben Claims sind durch `ADV-009` und `ADV-010` als Folien im Deck aktiv und werden gegen ihre erwartete Folienliste geprüft; für die übrigen 32 gilt weiterhin, dass eine geplante Claim-Zuordnung keine Runtime- oder Folienfreigabe ist.

`validate_privacy_metadata.py` ist ein User-defined Tool auf Basis der Python-Standardbibliothek. Es prüft Textdateien, Office-Pakete, ZIP-Archive und Medien-Gates. Findings werden ausschließlich als Repository-Pfad, Kategorie und Anzahl ausgegeben; der gefundene Wert erscheint weder im Log noch im kurzlebigen Diagnoseartefakt. Medien, PDFs und andere visuell zu prüfende Binärartefakte werden blockierend gekennzeichnet, sofern kein unveränderter hashgebundener Freigabenachweis vorliegt. Der Scanner ersetzt keine visuelle Einzelprüfung, kein OCR und keinen Rendervergleich.

## ADV-009 – Vertiefungsfolien im aktiven Deck

Der Workflow `.github/workflows/adv009-deck-integration.yml` startet keinen SQL Server und führt aus:

```bash
python3 Tests/Static/validate_adv009_deck_integration.py
python3 Tests/Static/validate_adv_003_curriculum.py
python3 Tests/Static/validate_privacy_metadata.py .
python3 Tools/build_adv009_slides.py --check
```

`validate_adv009_deck_integration.py` prüft das Deckarchiv auf Lesbarkeit, die Anzeigereihenfolge gegen `p:sldIdLst`, je Vertiefungsfolie das Modullabel, genau einen Leitabsatz, genau vier Aufzählungsabsätze und die zutreffende Fußzeilenpaginierung, je Notizfolie den unveränderten Folienmarker samt Kennzeichnungs- und Tiefenzeile, die unveränderte Position der 83 Basisfolien und der Schlussfolie sowie die Übereinstimmung von Folien- und Aussagenregister, Traceability-Matrix, Quellenmanifest, Datenschutzfreigabe und beiden Folienspezifikationen.

Die Prüfung bestätigt Zuordnung und Struktur, nicht Layoutqualität, Lesbarkeit im Vortrag oder fachliche Richtigkeit der Aussagen. Die fachliche Abnahme der Folien 84 bis 93 setzt zusätzlich die Runtime-Abnahme von `QRY-013` und `QRY-004` voraus.

`build_adv009_slides.py --check` bestätigt, dass das Deck bereits erweitert ist und ein erneuter Lauf keine zweite Einfügung erzeugt.

## ADV-010 – Vertiefungsfolien zur parametersensitiven Planoptimierung

Der Workflow `.github/workflows/adv010-deck-integration.yml` startet keinen SQL Server und führt aus:

```bash
python3 Tests/Static/validate_adv010_deck_integration.py
python3 Tests/Static/validate_adv009_deck_integration.py
python3 Tests/Static/validate_adv_003_curriculum.py
python3 Tests/Static/validate_w2_007_presentation.py
python3 Tests/Static/validate_privacy_metadata.py .
python3 Tools/build_adv010_slides.py --check
```

`validate_adv010_deck_integration.py` prüft dieselben Struktur- und Zuordnungseigenschaften wie der Prüfer des Blocks `ADV-009`, zusätzlich die unveränderten Anzeigepositionen des Blocks `ADV-009`, die kanonische Demo `OPT-009` in jeder Sprechernotiz und den Ausgangsfolienumfang im Erzeugungswerkzeug. Das aktive Deck umfasst damit 98 Folien: 84 Basisfolien, 10 Vertiefungsfolien aus `ADV-009` und 4 Vertiefungsfolien aus `ADV-010`.

Die fachliche Abnahme der Folien 94 bis 97 setzt zusätzlich die Runtime-Abnahme von `OPT-009` voraus. Die visuelle Renderprüfung ist nicht Teil der automatisierten Strecke.

## Vertiefungs-LAB-Designverträge

Die Designverträge werden durch zwei SQL-Server-unabhängige Workflows geprüft:

```bash
python3 Tests/Static/validate_adv_004_005_designs.py
python3 Tests/Static/validate_adv_006_007_designs.py
```

`validate_adv_004_005_designs.py` prüft LAB-VP1 und LAB-VP2 einschließlich Claimabdeckung, Planmechanik, Clientkontext, sichere Parametrisierung sowie PSP-/OPPO-Skip-Verträge.

`validate_adv_006_007_designs.py` prüft LAB-VP3 bis LAB-VP5 einschließlich Memory-Risikotrennung, Featurematrix 2019/2022/2025, Query-Store-Anforderungen, roten `RES-003`-Sicherheitsvertrag, Capstone-Hypothesen, neutrale Fallbezeichnung und Rückfallvertrag. Die Prüfungen bestätigen ausschließlich die Designkonsistenz. Sie ersetzen weder SQL-Server-Runtime-Tests noch die tatsächliche Feature- oder Planformvalidierung.

Beide Workflows führen zusätzlich den vollständigen Repository-Privacy-Scan aus.

## SQL_Server_Lab-Integrationsvertrag

Der Workflow `.github/workflows/sql-server-lab-test-catalog.yml` startet keinen Container und führt aus:

```bash
python3 Tests/Static/validate_sql_server_lab_test_catalog.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Der Validator entdeckt alle produktiven Dateien `Demos/**/manifest.json`, schließt nur Frameworkbeispiele unter `Demos/00_Framework/` aus und verlangt für jedes produktive Manifest genau einen Eintrag in `Tests/Lab/performance-lab-matrix.json`.

Geprüft werden:

- Demo-ID, Manifestpfad und Sicherheitsstufe;
- Docker-/Podman-Zuordnung;
- SQL-Server-Versionen 2019, 2022 und 2025;
- Ressourcenprofil und Environment-Isolation;
- Sessionzahl und erforderliche Capabilities;
- explizite Safety-Bestätigung für gelbe und rote Lanes;
- vollständiger Cleanup-Vertrag im Demo-Manifest;
- Vollständigkeit der aktuellen 96 Läufe umfassenden Container-Gesamtmatrix;
- Verbot von Secrets, realen Hostfeldern und absoluten Pfaden im Katalog.

`LABINT-001` validiert nur Architektur und Katalog. Ein realer Docker-/Podman-Lauf über `SQL_Server_Lab` folgt erst mit `LABINT-002`.

## Szenariendefinitionen

Der Workflow `.github/workflows/performance-scenarios.yml` startet keinen SQL Server und führt aus:

```bash
python Tests/Static/validate_performance_scenarios.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Der Validator prüft `Documentation/Inventories/performance_scenario_inventory.json` und jede Datei `Scenarios/**/scenario.json` gegeneinander: Vertragsversion, eindeutige Demo-IDs, zulässige Orchestrierungsmodi, Übereinstimmung von Inventar und Szenariendefinition sowie die Existenz aller referenzierten Repository-Pfade. Pfade außerhalb des Repositorys und absolute Pfade sind verboten.

Weil Szenariendefinitionen auf Demo-Skripte und Manifeste verweisen, löst der Workflow auch bei Änderungen unterhalb von `Demos/` aus. Er bestätigt ausschließlich die Vertragskonsistenz und ersetzt keinen Lauf der Mehrsitzungsorchestrierung.

## Ausführungspfad je Demo

Der Workflow `.github/workflows/demo-execution-paths.yml` startet keinen SQL Server und führt aus:

```bash
python Tests/Static/validate_demo_execution_paths.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Der Validator prüft `Documentation/Demo_Catalog/demo_execution_paths.json` gegen die Stufenleiter aus Abschnitt 13.2 des Masterplans. Geprüft werden die beidseitige Vollständigkeit gegenüber den produktiven Demo-Manifesten, die Zuordnung von Stufe und Ausführungspfad, die Pflicht zur Begründung oberhalb von Stufe 2, der Instanzbedarf gelber und roter Demos sowie die Übereinstimmung von Sicherheitsstufe, Sitzungszahl, Status und Manifestpfad mit `Tests/Lab/performance-lab-matrix.json` und dem Szenarioinventar.

Der Katalog beschreibt den erforderlichen Ausführungspfad. Er provisioniert keine Umgebung.

## Aktive Framework-Runtime-Matrix

Der Workflow `.github/workflows/framework-sql-matrix.yml` validiert das gemeinsame Framework gegen:

| SQL Server | Major | Compatibility Level | Container |
|---|---:|---:|---|
| 2019 | 15 | 150 | `mcr.microsoft.com/mssql/server:2019-latest` |
| 2022 | 16 | 160 | `mcr.microsoft.com/mssql/server:2022-latest` |
| 2025 | 17 | 170 | `mcr.microsoft.com/mssql/server:2025-latest` |

Der validierte Lauf `30099942191` hat alle drei Matrixjobs erfolgreich abgeschlossen. Geprüft wurden Lifecycle, Preflight, Datengenerator, Messrahmen, Plan-/Statistikevidenz, parallele SQL-Sessions, Query Store, Extended Events, Runtime-Harness und markergeprüftes Cleanup.

## Aktive Gate-B-Pilotmatrix

Der Workflow `.github/workflows/gate-b-pilots.yml` prüft zunächst `Tests/Static/validate_gate_b_pilots.py`. Danach startet er dieselbe SQL-Server-2019/2022/2025-Matrix und führt aus:

```bash
python Tests/Runtime/run_gate_b_pilots.py \
  --target docker \
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der validierte Lauf `30108023315` führte folgende Piloten je Version zweimal vollständig über `FWK-010` aus:

| Demo-ID | Sicherheitsstufe | Fokus | Läufe je Version |
|---|---|---|---:|
| `QRY-001` | `GREEN` | SARGability, Seek/Scan und statementbezogene Reads | 2 |
| `OPT-002` | `GREEN` | Statistikheader, Histogramm, Density Vector und Fullscan | 2 |
| `CON-004` | `YELLOW` | Head–Middle–Leaf-Blocking-Chain und blockierungsfreier Vergleich | 2 |
| `OPT-013` | `YELLOW` | Table-Variable-Undergrant, Sort-Spill und Staging-Mitigation | 2 |

Damit wurden insgesamt 24 vollständige Demoläufe ausgeführt. Nach jedem Lauf prüft der Testtreiber unabhängig über `master`, dass die markierte Testdatenbank nicht mehr vorhanden ist. Statische Verträge, alle Runtimejobs und alle Containerentfernungen waren erfolgreich.

## ADV-008 – Runtime-Matrix für OPT-015 und OPT-016

Der Workflow `.github/workflows/adv008-opt015-opt016.yml` prüft zuerst:

```bash
python Tests/Static/validate_adv008_opt015_opt016.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Danach startet er dieselbe SQL-Server-2019/2022/2025-Matrix und führt aus:

```bash
python Tests/Runtime/run_adv008_opt015_opt016.py \
  --target docker \
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der validierte Lauf `30218788526` führte `OPT-015` und `OPT-016` je Version zweimal vollständig aus. Damit wurden zwölf Demoläufe validiert. Nach jedem Lauf prüft der Treiber über `master`, dass die markergebundene Testdatenbank entfernt wurde.

| Demo-ID | Sicherheitsstufe | Runtime-Vertrag | Läufe je Version |
|---|---|---|---:|
| `OPT-015` | `GREEN` | Estimated/Actual Rows, Actual Rows Read, Statistics Usage, identische Ergebnismenge und verbesserte Schätzrichtung | 2 |
| `OPT-016` | `GREEN` | Outer References, hintfreie Spool-Planform, Rebind-/Rewind-Richtung, kontrollierte No-Spool-Gegenprobe und Ergebnisequivalenz | 2 |

`OPT-016` wurde während der Abnahme an die beobachtete Optimizerentscheidung angepasst. Der passende Index verhinderte die Performance Spool nicht zuverlässig. Baseline und Vergleich verwenden deshalb `NO_PERFORMANCE_SPOOL` ausschließlich als explizite Gegenprobe; die untersuchte Problemabfrage bleibt hintfrei.

## ADV-008 – Runtime-Matrix für QRY-013

Der Workflow `.github/workflows/adv008-qry013.yml` prüft zuerst:

```bash
python Tests/Static/validate_adv008_qry013.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Danach startet er dieselbe SQL-Server-2019/2022/2025-Matrix und führt aus:

```bash
python Tests/Runtime/run_adv008_qry013.py \
  --target docker \
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der statische Vertrag `validate_adv008_qry013.py` prüft Bündelaufbau, Phasenreihenfolge, verbotene T-SQL-Konstrukte, die lexikalische Konsistenz aller Phasen, die beiden explizit gesetzten Sessionprofile, den Parameterwechsel in der Beobachtungsphase, den markergebundenen und idempotenten Cleanup sowie die Folienspezifikation `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03.md`.

| Demo-ID | Sicherheitsstufe | Runtime-Vertrag | Läufe je Version |
|---|---|---|---:|
| `QRY-013` | `GREEN` | getrennte Cacheeinträge bei abweichendem Sessionkontext, Ergebnis- und Prüfsummenequivalenz, Planwiederverwendung bei Parameterwechsel, ausgerichteter Kontext mit einem Cacheeintrag | 2 |

Der Status ist `IMPLEMENTED`, nicht `VALIDATED`: Die Runtime-Abnahme über die drei Zielversionen steht aus. Fehlt die Plancache-Evidenz auf der Zielinstanz, endet die betroffene Phase kontrolliert mit `SKIP|SKIP_EVIDENCE_MISSING`; bleibt der Anstieg der logischen Lesevorgänge aus, endet die Beobachtungsphase mit `WARN|WARN_EMPIRICAL_VARIANCE`.

## ADV-008 – Runtime-Matrix für QRY-004

Der Workflow `.github/workflows/adv008-qry004.yml` prüft zuerst:

```bash
python Tests/Static/validate_adv008_qry004.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Danach startet er dieselbe SQL-Server-2019/2022/2025-Matrix und führt aus:

```bash
python Tests/Runtime/run_adv008_qry004.py \
  --target docker \
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der statische Vertrag `validate_adv008_qry004.py` prüft zusätzlich zu Bündelaufbau, Phasenreihenfolge und lexikalischer Konsistenz zwei sicherheitsrelevante Eigenschaften des dynamischen SQL: Es darf keine direkte Stringausführung über `EXEC(...)` geben, und Filterwerte dürfen nicht in den Statementtext konkateniert werden. Geprüft werden ferner die Trennung der drei Strategien, die normalisierte Prädikatsreihenfolge, der markergebundene und idempotente Cleanup sowie die Folienspezifikation `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03_LO08.md`.

| Demo-ID | Sicherheitsstufe | Runtime-Vertrag | Läufe je Version |
|---|---|---|---:|
| `QRY-004` | `GREEN` | eine Catch-all-Planform über drei Selektivitäten, Ergebnis- und Prüfsummenequivalenz aller drei Strategien, zwei Statementformen für drei dynamische Ausführungen, abgewiesene Positivlistenverletzung, literalfreier Statementtext | 2 |

Der Status ist `IMPLEMENTED`, nicht `VALIDATED`. Fehlt die Plancache-Evidenz, endet die betroffene Phase mit `SKIP|SKIP_EVIDENCE_MISSING`; lässt sich der Nutzen der Neuoptimierung oder deren Compilepreis nicht von der Messstreuung trennen, endet die betroffene Phase mit `WARN|WARN_EMPIRICAL_VARIANCE`.

## ADV-008 – Runtime-Matrix für OPT-009

Der Workflow `.github/workflows/adv008-opt009.yml` prüft zuerst:

```bash
python Tests/Static/validate_adv008_opt009.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Danach startet er dieselbe SQL-Server-2019/2022/2025-Matrix und führt aus:

```bash
python Tests/Runtime/run_adv008_opt009.py \
  --target docker \
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der statische Vertrag `validate_adv008_opt009.py` prüft neben Bündelaufbau, Phasenreihenfolge und lexikalischer Konsistenz drei Besonderheiten dieser Demo: Erstens dürfen ausschließlich die Statuscodes aus `FWK-012` in den Zusammenfassungszeilen stehen, damit funktionsspezifische Eigenerfindungen ausgeschlossen sind. Zweitens muss jede Phase genau ein Vergleichsobjekt ausführen, damit Marker und Evidenz eindeutig zugeordnet bleiben. Drittens sind die Query-Store-Sichten `sys.query_store_plan` und `sys.query_store_query_variant` in den SQL-Dateien verboten, solange deren Pilotabnahme offen ist. Geprüft werden ferner der abgeschaltete Ausgangszustand, die Abwahl auf Abfrageebene, der markergebundene und idempotente Cleanup sowie die Folienspezifikation `Documentation/Curriculum/ADV_010_SLIDE_SPECIFICATION_M03_LO08_PSP.md`.

| Demo-ID | Sicherheitsstufe | Runtime-Vertrag | Läufe je Version |
|---|---|---|---:|
| `OPT-009` | `GREEN` | genau eine Planform je Kompilierungsreihenfolge ohne Parametersensitivität, beidseitige Mehrkosten bei identischen Prüfsummen, mindestens ein Dispatcherplan und mindestens zwei Query Variants bei eingeschalteter Optimierung, kein Dispatcherplan bei ausdrücklicher Abwahl | 2 |

Der Status ist `IMPLEMENTED`, nicht `VALIDATED`. Auf SQL Server 2019 endet die Demo planmäßig mit `SKIP|SKIP_VERSION`; der Runner wertet diesen Ausgang als bestanden. Stuft der Optimierer die Abfrage trotz passender Version nicht als parametersensitiv ein oder fehlt die Plancache-Evidenz, endet die betroffene Phase mit `SKIP|SKIP_EVIDENCE_MISSING`. Lässt sich der Nutzen der Varianten nicht von der Messstreuung trennen, endet die Phase mit `WARN|WARN_EMPIRICAL_VARIANCE`.

## ADV-008 – Runtime-Matrix für OPT-010

Der Workflow `.github/workflows/adv008-opt010.yml` prüft zuerst:

```bash
python Tests/Static/validate_adv008_opt010.py
python3 Tests/Static/validate_privacy_metadata.py .
```

Danach startet er dieselbe SQL-Server-2019/2022/2025-Matrix und führt aus:

```bash
python Tests/Runtime/run_adv008_opt010.py \
  --target docker \
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der statische Vertrag `validate_adv008_opt010.py` übernimmt die Prüfachsen des OPT-009-Vertrags und ergänzt vier Besonderheiten dieser Demo: Erstens muss der Preflight bereits ab Hauptversion 17 unterscheiden, weil Optional Parameter Plan Optimization vor SQL Server 2025 nicht existiert. Zweitens müssen alle vier Vergleichsobjekte denselben optionalen Prädikatausdruck tragen, damit der Unterschied allein in Konfiguration und Hinweis liegt. Drittens muss die Gegenmaßnahme das optionale Parameterprädikat ausdrücklich nachweisen und ein gleichzeitig auftretendes parametersensitives Prädikat als `WARN_EMPIRICAL_VARIANCE` melden, damit die Wirkung eindeutig zugeordnet bleibt. Viertens ist `PARAMETER_SENSITIVE_PLAN_OPTIMIZATION` in den SQL-Dateien verboten, damit die Nachbardemo nicht mitgeschaltet wird.

| Demo-ID | Sicherheitsstufe | Runtime-Vertrag | Läufe je Version |
|---|---|---|---:|
| `OPT-010` | `GREEN` | genau eine Planform und reihenfolgeunabhängige Lesekosten ohne die Optimierung, mindestens ein Dispatcherplan mit optionalem Parameterprädikat und mindestens zwei Query Variants bei eingeschalteter Optimierung, kein Dispatcherplan bei ausdrücklicher Abwahl, Ergebnisgleichheit über alle vier Phasen | 2 |

Der Status ist `IMPLEMENTED`, nicht `VALIDATED`. Auf SQL Server 2019 und 2022 endet die Demo planmäßig mit `SKIP|SKIP_VERSION`; der Runner wertet diesen Ausgang als bestanden. Stuft der Optimierer die Abfrage trotz passender Version nicht als geeignet ein oder fehlt die Plancache-Evidenz, endet die betroffene Phase mit `SKIP|SKIP_EVIDENCE_MISSING`.

## Ausführungsziele der Runtime-Runner

`Tests/Runtime/execution_target.py` trennt die Prüflogik von der Frage, wo der SQL Server läuft. Die Demo-Runner wählen das Ziel über `--target`:

| Ziel | Verwendung | Pflichtangaben | Evidenzwert |
|---|---|---|---|
| `docker` | wegwerfbare Container-Instanz | `--container` | Gate-Evidenz, sofern auf `github-hosted` ausgeführt |
| `host` | vorhandene SQL-Server-Instanz | `--server`, `--confirm-disposable-instance` | Entwicklungs- und Fehlersuchevidenz |

Ein Lauf gegen eine vorhandene Instanz sieht so aus:

```bash
python Tests/Runtime/run_gate_b_pilots.py \
  --target host \
  --server <instanz> \
  --username <anmeldename> \
  --confirm-disposable-instance
```

Ohne `--username` wird Windows-Authentifizierung verwendet. Ohne `--expected-major` liest der Runner die Hauptversion aus der Instanz. Kennwörter werden ausschließlich über `SQLCMDPASSWORD` übergeben.

Die Bestätigung ist verbindlich, weil der Lauf `SQLPERF`-Datenbanken anlegt und wieder löscht. Die Zielinstanz muss eine Wegwerfinstanz sein. Trägt sie ein selbstsigniertes Zertifikat, wird `SQLPERF_HOST_TRUST_SERVER_CERTIFICATE=1` zusätzlich benötigt; ohne diese Freigabe bleibt die Zertifikatsprüfung aktiv.

Die Framework-Matrix bleibt an das Ziel `docker` gebunden, weil sie Query Store und Extended Events auf Serverebene schaltet. Grundlage ist `Documentation/Project_Planning/INF_001_EXECUTION_TARGET_DESIGN.md`. Die Bedienanleitung für eine vorhandene Instanz steht in `Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md`.

Der Workflow `.github/workflows/inf-001-execution-path.yml` startet keinen SQL Server und führt aus:

```bash
python Tests/Static/validate_inf_001_execution_path.py
python3 Tests/Static/validate_privacy_metadata.py .
```

`validate_inf_001_execution_path.py` prüft die öffentliche Schnittstelle des Zielmoduls, die Zieloptionen und Zusammenfassungszeilen der Demo-Runner, die Bindung der Containerlogik an das Zielmodul, den Pflichtinhalt des How-tos, die Runner-Topologie sowie die Pfadfilter und die Runner-Auswahl der Runtime-Workflows.

## Datenschutz und Laufzeitumgebung

Die bestehenden GitHub-Matrizen verwenden pro Job eine ephemere Developer-Instanz ohne Host-Port und ohne persistentes Volume. Der geplante lokale Lab-Runner verwendet stattdessen die von `SQL_Server_Lab` erzeugte, scopegebundene Docker- oder Podman-Umgebung. In beiden Fällen wird das Kennwort zur Laufzeit erzeugt und nicht versioniert.

Kurzlebige Diagnoseartefakte besitzen eine begrenzte Aufbewahrungsdauer und enthalten ausschließlich synthetische Phasen-, Kategorien- und Fehlerausgaben.

Details stehen unter [`Tests/Runtime`](Runtime/README.md), [`Tests/Lab`](Lab/README.md), im [Framework-Matrixreview](../Documentation/Project_Planning/SQL_SERVER_RUNTIME_MATRIX_REVIEW.md), im [Gate-B-Review](../Documentation/Project_Planning/GATE_B_REVIEW.md), im [ADV-008-Review](../Documentation/Project_Planning/ADV_008_OPT_015_016_REVIEW.md) und im [Privacy-Prüfverfahren](../Documentation/Quality/PRIVACY_METADATA_REVIEW_PROCEDURE.md).

## Toolklassifikation

- Die Python-Prüfungen und Frameworkskripte sind User-defined Tools des Projekts.
- Das produktive Runtime-Framework verwendet das externe Microsoft-Tool `sqlcmd`.
- `SQL_Server_Lab` ist die zentrale, projektexterne Provider- und Lifecycle-Komponente für lokale Docker-/Podman-Läufe.
- GitHub Actions und `actions/checkout` beziehungsweise `actions/upload-artifact` sind Drittanbieter-/Plattformtools der GitHub-Plattform.
- Fehlt `sqlcmd`, wird dies als `SKIP_TOOL_MISSING` und nicht als SQL-Server-Fehler behandelt.

## Nächste Prüfbereiche

- `LABINT-002`: grüner lokaler Runner über `SQL_Server_Lab`;
- `QRY-013` und `QRY-004` auf SQL Server 2019, 2022 und 2025;
- Pilotdemos mit Query Store und Extended Events als zentralen Evidenzpfaden;
- statische Variantenprüfung für SlideKeys, Custom Shows und Präsentationsmanifest;
- Windows- oder OS-spezifische Profile nur bei konkreter Demoabhängigkeit;
- Releasevalidierung mit dokumentierten Containerdigests oder CU-Ständen;
- weitere Demos und Inhaltsartefakte der Welle 2.

Tests und Reports dürfen keine realen Zugangsdaten oder Umgebungsinformationen persistieren. Interaktiv notwendige reale Resultsets sind keine Repository-Artefakte.
