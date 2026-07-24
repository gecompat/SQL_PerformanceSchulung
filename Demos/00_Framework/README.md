# Demo-Framework

## Zweck

Dieser Bereich enthält die verbindlichen Daten-, Mess-, Evidenz-, Orchestrierungs-, Telemetrie-, Sicherheits-, Lifecycle-, Runtime-, Status- und Dokumentverträge für ausführbare Schulungsdemos. Es werden keine dauerhaft installierten Steuerobjekte in `master` oder einer versteckten Framework-Datenbank angelegt.

## Implementierungsstand

| Arbeitspaket | Status | Kernartefakt |
|---|---|---|
| `FWK-001` | `IMPLEMENTED` | Preflight-Vertrag und `Templates/00_Preflight.sql` |
| `FWK-002` | `IMPLEMENTED` | markergeprüfter Testdatenbank-Lifecycle |
| `FWK-003` | `IMPLEMENTED` | deterministischer Datengenerator |
| `FWK-004` | `IMPLEMENTED` | sessionbezogener Messrahmen |
| `FWK-005` | `IMPLEMENTED` | Plan- und Statistikevidenz |
| `FWK-006` | `IMPLEMENTED` | Datenbanksignale und `Tools/orchestrate_sessions.py` |
| `FWK-007` | `IMPLEMENTED` | Query-Store- und XE-Lifecycle |
| `FWK-008` | `IMPLEMENTED` | Sicherheits- und Abbruchvertrag |
| `FWK-009` | `IMPLEMENTED` | vollständige Demo-Dokumentvorlage |
| `FWK-010` | `IMPLEMENTED` | `Tools/run_demo.py` |
| `FWK-011` | `IMPLEMENTED` | Ergebnisnormalisierung und Evaluator |
| `FWK-012` | `IMPLEMENTED` | Status-, Fehler- und Skip-Vertrag 1.2 |

`IMPLEMENTED` bestätigt Vertrags- und Referenzimplementierung sowie SQL-Server-unabhängige statische und Prozess-Selbsttests. Runtime-Validierung auf SQL Server 2019, 2022 und 2025 bleibt offen.

## Toolklassen

| Klasse | Bestandteile |
|---|---|
| Systemobjekte | SQL-Server-Kataloge, DMVs, Query Store und Extended Events |
| User-defined Tools | SQL-Vorlagen, `fwk`-Objekte und Python-Module dieses Repositories |
| Externes Microsoft-Tool | `sqlcmd`; wird nicht installiert und bei Fehlen kontrolliert übersprungen |

## Verzeichnisstruktur

| Pfad | Zweck |
|---|---|
| `Contracts/` | normative technische Verträge |
| `Templates/` | kopierbare Demo-, Preflight- und Evidenzvorlagen |
| `Sql/` | eigenständig ausführbare Framework-Skripte |
| `Tools/` | plattformneutrale Prozess- und Ergebniswerkzeuge |
| `Examples/` | ausschließlich synthetische Manifeste, Skripte und Erwartungsdaten |

## Verwendungsmodell

Eine Demo übernimmt Dokument- und SQL-Vorlagen in ihr eigenes Verzeichnis. `FWK-002` schützt den Datenbank-Lifecycle, `FWK-003` erzeugt Daten, `FWK-004` misst, `FWK-005` liefert Plan-/Statistikevidenz, `FWK-006` koordiniert Sessions, `FWK-007` verwaltet temporäre Telemetrie, `FWK-010` steuert den Phasenlauf und `FWK-011` prüft das Ergebnis.

Multi-Session-Abhängigkeiten verwenden Datenbanksignale. Query Store wird über Baseline und Restore zurückgesetzt. Die XE-Referenzsession verwendet ausschließlich einen begrenzten `ring_buffer` und keinen Autostart. Der Runtime-Harness führt Cleanup nach gestarteter Setup-Phase unabhängig vom vorherigen Ergebnis aus.

## Sicherheitsgrundsätze

- Keine Datenbank wird aufgrund ihres Namens allein gelöscht.
- Framework-SQL verändert ausschließlich vollständig markierte Testdatenbanken.
- Gelbe und rote Demos benötigen technisch erzwungene Bestätigungen.
- Passwörter stehen weder in Manifesten noch in Kommandozeilen; SQL-Authentifizierung verwendet `SQLCMDPASSWORD`.
- Kontrollierte Nichtanwendbarkeit ist `SKIP`, kein technischer Fehler.
- Prozess-Timeouts beenden verbleibende Kindprozesse.
- Umgebungsdetails, Querytexte, Pläne, Event-Daten und Rohoutput werden standardmäßig nicht persistiert.
- Absolute Performancegrenzen benötigen ein technisch kontrolliertes Ressourcenprofil.

## Statische Prüfung

Der pfadbegrenzte GitHub-Actions-Workflow führt vier Prüfungen aus:

1. allgemeine Framework-Vertragsprüfung,
2. Selbsttest des Ergebnis-Evaluators,
3. Orchestrierungs-/Runtime-Vertragsprüfung,
4. Prozess-Selbsttest für Erfolg, Fehler, Skip, Timeout, Safety und Cleanup.
