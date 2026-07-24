# Demo-Framework

## Zweck

Dieser Bereich enthält die verbindlichen Sicherheits-, Lifecycle-, Status- und Dokumentverträge für alle ausführbaren Schulungsdemos. Die Grundlage wird als transparente Vorlage und als eigenständiges Lifecycle-Skript bereitgestellt. Es werden keine dauerhaft installierten Steuerobjekte in `master` oder einer versteckten Framework-Datenbank angelegt.

## Implementierungsstand

| Arbeitspaket | Status | Artefakt |
|---|---|---|
| `FWK-001` | `IMPLEMENTED` | `Contracts/FWK-001_Preflight_Contract.md`, `Templates/00_Preflight.sql` |
| `FWK-002` | `IMPLEMENTED` | `Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md`, `Sql/FWK_TestDatabaseLifecycle.sql` |
| `FWK-008` | `IMPLEMENTED` | `Contracts/FWK-008_Safety_Abort_Contract.md`, Sicherheitsgate im Preflight |
| `FWK-009` | `IMPLEMENTED` | `Templates/README_TEMPLATE.md` |
| `FWK-012` | `IMPLEMENTED` | `Contracts/FWK-012_Status_Error_Skip_Contract.md`, einheitliche Codes in den SQL-Vorlagen |
| `FWK-003` bis `FWK-007`, `FWK-010`, `FWK-011` | `PLANNED` | nächste Framework-Pakete |

`IMPLEMENTED` bestätigt in diesem Stand die vorhandene Vertrags- und Referenzimplementierung. Eine Runtime-Validierung gegen SQL Server 2019, 2022 und 2025 erfolgt erst mit dem SQL-Runtime-Harness und den Gate-B-Pilotdemos.

## Verzeichnisstruktur

| Pfad | Zweck |
|---|---|
| `Contracts/` | normative technische Verträge |
| `Templates/` | kopierbare Demo- und Preflight-Vorlagen |
| `Sql/` | eigenständig ausführbare Framework-Skripte |

## Verwendungsmodell

Eine neue Demo übernimmt `Templates/README_TEMPLATE.md` und `Templates/00_Preflight.sql` in ihr eigenes Verzeichnis. Platzhalter und deaktivierte Checks werden fachlich konkretisiert. Setup und Cleanup verwenden das Namens- und Markerschema aus `FWK-002`.

Die Vorlagen werden kopiert, damit jede Demo eigenständig lesbar und ausführbar bleibt. Abweichungen vom Vertrag müssen im Demo-README begründet und durch Tests abgedeckt sein.

## Sicherheitsgrundsätze

- Keine Datenbank wird aufgrund ihres Namens allein gelöscht.
- Gelbe und rote Demos benötigen technisch erzwungene Bestätigungen.
- Kontrollierte Nichtanwendbarkeit ist `SKIP`, kein technischer Fehler.
- Cleanup adressiert ausschließlich demo-eigene Objekte, Sessions oder vollständig markierte Testdatenbanken.
- Umgebungsdetails werden standardmäßig nicht ausgegeben und nicht persistiert.

## Statische Prüfung

`Tests/Static/validate_framework_contracts.py` prüft Pflichtdateien, Vertragsmarker, Statuscodes und verbotene Hochrisikomuster. Der zugehörige GitHub-Actions-Workflow läuft nur bei Änderungen an Framework-, Vertrag- oder Testpfaden.
