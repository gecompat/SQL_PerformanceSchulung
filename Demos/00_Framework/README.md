# Demo-Framework

## Zweck

Dieser Bereich enthält die verbindlichen Daten-, Mess-, Evidenz-, Sicherheits-, Lifecycle-, Status- und Dokumentverträge für alle ausführbaren Schulungsdemos. Die Grundlage wird als transparente Vorlage, eigenständige SQL-Referenzen und plattformneutrales Ergebniswerkzeug bereitgestellt. Es werden keine dauerhaft installierten Steuerobjekte in `master` oder einer versteckten Framework-Datenbank angelegt.

## Implementierungsstand

| Arbeitspaket | Status | Artefakt |
|---|---|---|
| `FWK-001` | `IMPLEMENTED` | `Contracts/FWK-001_Preflight_Contract.md`, `Templates/00_Preflight.sql` |
| `FWK-002` | `IMPLEMENTED` | `Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md`, `Sql/FWK_TestDatabaseLifecycle.sql` |
| `FWK-003` | `IMPLEMENTED` | `Contracts/FWK-003_Synthetic_Data_Contract.md`, `Sql/FWK_SyntheticDataGenerator.sql` |
| `FWK-004` | `IMPLEMENTED` | `Contracts/FWK-004_Measurement_Contract.md`, `Sql/FWK_Measurement.sql` |
| `FWK-005` | `IMPLEMENTED` | `Contracts/FWK-005_Plan_Statistics_Evidence_Contract.md`, `Templates/40_Plan_Statistics_Evidence.sql` |
| `FWK-008` | `IMPLEMENTED` | `Contracts/FWK-008_Safety_Abort_Contract.md`, Sicherheitsgate im Preflight |
| `FWK-009` | `IMPLEMENTED` | `Templates/README_TEMPLATE.md` |
| `FWK-011` | `IMPLEMENTED` | `Contracts/FWK-011_Result_Normalization_Contract.md`, `Tools/evaluate_result_contract.py`, synthetische Beispiele |
| `FWK-012` | `IMPLEMENTED` | `Contracts/FWK-012_Status_Error_Skip_Contract.md`, einheitliche Codes in SQL und Evaluator |
| `FWK-006`, `FWK-007`, `FWK-010` | `PLANNED` | Multi-Session-Orchestrierung, Query-Store-/XE-Helfer und vollständiger Runtime-Harness |

`IMPLEMENTED` bestätigt die vorhandene Vertrags- und Referenzimplementierung sowie statische Tests. Eine Runtime-Validierung gegen SQL Server 2019, 2022 und 2025 erfolgt erst mit `FWK-010` und den Gate-B-Pilotdemos.

## Verzeichnisstruktur

| Pfad | Zweck |
|---|---|
| `Contracts/` | normative technische Verträge |
| `Templates/` | kopierbare Demo-, Preflight- und Evidenzvorlagen |
| `Sql/` | eigenständig ausführbare Framework-Skripte |
| `Tools/` | plattformneutrale Standardbibliothekswerkzeuge |
| `Examples/` | ausschließlich synthetische Verträge und Erwartungsdaten |

## Verwendungsmodell

Eine neue Demo übernimmt `Templates/README_TEMPLATE.md` und `Templates/00_Preflight.sql` in ihr eigenes Verzeichnis. Platzhalter und deaktivierte Checks werden fachlich konkretisiert. Setup und Cleanup verwenden das Namens- und Markerschema aus `FWK-002`.

`FWK-003` erzeugt reproduzierbare Uniform-, Skew-, Korrelations-, Zeit- und Breitenprofile. `FWK-004` koppelt Messungsstart und -ende an dieselbe Session. `FWK-005` gibt Statistikmetadaten, Histogramm und optional Actual Showplan XML interaktiv aus. `FWK-011` prüft synthetische Ergebnisdateien gegen Invarianten, Bereiche, Richtungen und Verhältnisse.

Die Vorlagen werden kopiert, damit jede Demo eigenständig lesbar und ausführbar bleibt. Abweichungen vom Vertrag müssen im Demo-README begründet und durch Tests abgedeckt sein.

## Sicherheitsgrundsätze

- Keine Datenbank wird aufgrund ihres Namens allein gelöscht.
- Framework-SQL verändert ausschließlich vollständig markierte Testdatenbanken.
- Gelbe und rote Demos benötigen technisch erzwungene Bestätigungen.
- Kontrollierte Nichtanwendbarkeit ist `SKIP`, kein technischer Fehler.
- Cleanup adressiert ausschließlich demo-eigene Objekte, Sessions oder vollständig markierte Testdatenbanken.
- Umgebungsdetails, Querytexte und Pläne werden standardmäßig nicht persistiert.
- Generatorwerte sind deterministisch; Prüfsummen sind kein Kollisions- oder Integritätsbeweis.
- Absolute Performancegrenzen benötigen ein technisch kontrolliertes Ressourcenprofil.

## Statische Prüfung

`Tests/Static/validate_framework_contracts.py` prüft Pflichtdateien, Vertragsmarker, Statuscodes, Determinismusregeln, T-SQL-Lexik, Python-Syntax, JSON-Metadaten und verbotene Hochrisikomuster. `Tests/Static/test_result_contract_evaluator.py` führt positive und negative `FWK-011`-Selbsttests aus. Der GitHub-Actions-Workflow läuft nur bei Änderungen an Framework-, Vertrag- oder Testpfaden.
