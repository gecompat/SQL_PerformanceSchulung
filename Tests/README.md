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

## Curriculum- und Privacy-Prüfung

Der Workflow `.github/workflows/privacy-metadata.yml` startet keinen SQL Server und führt aus:

```bash
python3 Tests/Static/validate_adv_003_curriculum.py
python3 Tests/Static/test_privacy_metadata_scanner.py
python3 Tests/Static/validate_privacy_metadata.py .
```

`validate_adv_003_curriculum.py` prüft den unveränderten 84-Folien-Kern, die 39 geplanten Vertiefungsclaims, neun neue Vertiefungslernziele und ihre eindeutige Traceability. Eine geplante Claim-Zuordnung gilt nicht als Runtime- oder Folienfreigabe.

`validate_privacy_metadata.py` ist ein User-defined Tool auf Basis der Python-Standardbibliothek. Es prüft Textdateien, Office-Pakete, ZIP-Archive und Medien-Gates. Findings werden ausschließlich als Repository-Pfad, Kategorie und Anzahl ausgegeben; der gefundene Wert erscheint weder im Log noch im kurzlebigen Diagnoseartefakt. Medien, PDFs und andere visuell zu prüfende Binärartefakte werden blockierend gekennzeichnet, sofern kein unveränderter hashgebundener Freigabenachweis vorliegt. Der Scanner ersetzt keine visuelle Einzelprüfung, kein OCR und keinen Rendervergleich.

## Vertiefungs-LAB-Designverträge

Die Designverträge werden durch zwei SQL-Server-unabhängige Workflows geprüft:

```bash
python3 Tests/Static/validate_adv_004_005_designs.py
python3 Tests/Static/validate_adv_006_007_designs.py
```

`validate_adv_004_005_designs.py` prüft LAB-VP1 und LAB-VP2 einschließlich Claimabdeckung, Planmechanik, Clientkontext, sichere Parametrisierung sowie PSP-/OPPO-Skip-Verträge.

`validate_adv_006_007_designs.py` prüft LAB-VP3 bis LAB-VP5 einschließlich Memory-Risikotrennung, Featurematrix 2019/2022/2025, Query-Store-Anforderungen, roten `RES-003`-Sicherheitsvertrag, Capstone-Hypothesen, neutrale Fallbezeichnung und Rückfallvertrag. Die Prüfungen bestätigen ausschließlich die Designkonsistenz. Sie ersetzen weder SQL-Server-Runtime-Tests noch die tatsächliche Feature- oder Planformvalidierung.

Beide Workflows führen zusätzlich den vollständigen Repository-Privacy-Scan aus.

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
  --container <ephemerer-container> \
  --expected-major <15|16|17>
```

Der validierte Lauf `30218788526` führte `OPT-015` und `OPT-016` je Version zweimal vollständig aus. Damit wurden zwölf Demoläufe validiert. Nach jedem Lauf prüft der Treiber über `master`, dass die markergebundene Testdatenbank entfernt wurde.

| Demo-ID | Sicherheitsstufe | Runtime-Vertrag | Läufe je Version |
|---|---|---|---:|
| `OPT-015` | `GREEN` | Estimated/Actual Rows, Actual Rows Read, Statistics Usage, identische Ergebnismenge und verbesserte Schätzrichtung | 2 |
| `OPT-016` | `GREEN` | Outer References, hintfreie Spool-Planform, Rebind-/Rewind-Richtung, kontrollierte No-Spool-Gegenprobe und Ergebnisequivalenz | 2 |

`OPT-016` wurde während der Abnahme an die beobachtete Optimizerentscheidung angepasst. Der passende Index verhinderte die Performance Spool nicht zuverlässig. Baseline und Vergleich verwenden deshalb `NO_PERFORMANCE_SPOOL` ausschließlich als explizite Gegenprobe; die untersuchte Problemabfrage bleibt hintfrei.

## Datenschutz und Laufzeitumgebung

Die Matrizen verwenden pro Job eine ephemere Developer-Instanz ohne Host-Port und ohne persistentes Volume. Das Kennwort wird zur Laufzeit erzeugt, maskiert und nicht in Dateien oder Prozessargumenten gespeichert. Kurzlebige Diagnoseartefakte besitzen eine begrenzte Aufbewahrungsdauer und enthalten ausschließlich synthetische Phasen-, Kategorien- und Fehlerausgaben.

Details stehen unter [`Tests/Runtime`](Runtime/README.md), im [Framework-Matrixreview](../Documentation/Project_Planning/SQL_SERVER_RUNTIME_MATRIX_REVIEW.md), im [Gate-B-Review](../Documentation/Project_Planning/GATE_B_REVIEW.md), im [ADV-008-Review](../Documentation/Project_Planning/ADV_008_OPT_015_016_REVIEW.md) und im [Privacy-Prüfverfahren](../Documentation/Quality/PRIVACY_METADATA_REVIEW_PROCEDURE.md).

## Toolklassifikation

- Die Python-Prüfungen und Frameworkskripte sind User-defined Tools des Projekts.
- Das produktive Runtime-Framework verwendet das externe Microsoft-Tool `sqlcmd`.
- GitHub Actions und `actions/checkout` beziehungsweise `actions/upload-artifact` sind Drittanbieter-/Plattformtools der GitHub-Plattform.
- Fehlt `sqlcmd`, wird dies als `SKIP_TOOL_MISSING` und nicht als SQL-Server-Fehler behandelt.

## Nächste Prüfbereiche

- `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC` auf SQL Server 2019, 2022 und 2025,
- Pilotdemos mit Query Store und Extended Events als zentralen Evidenzpfaden,
- statische Variantenprüfung für SlideKeys, Custom Shows und Präsentationsmanifest,
- Windows- oder OS-spezifische Profile nur bei konkreter Demoabhängigkeit,
- Releasevalidierung mit dokumentierten Containerdigests oder CU-Ständen,
- weitere Demos und Inhaltsartefakte der Welle 2.

Tests und Reports dürfen keine realen Zugangsdaten oder Umgebungsinformationen persistieren. Interaktiv notwendige reale Resultsets sind keine Repository-Artefakte.
