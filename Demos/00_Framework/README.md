# Demo-Framework

## Zweck

Dieser Bereich enthält die verbindlichen Daten-, Mess-, Evidenz-, Orchestrierungs-, Telemetrie-, Sicherheits-, Lifecycle-, Runtime-, Status- und Dokumentverträge für ausführbare Schulungsdemos. Es werden keine dauerhaft installierten Steuerobjekte in `master` oder einer versteckten Framework-Datenbank angelegt.

## Validierungsstand

| Arbeitspaket | Status | Kernartefakt |
|---|---|---|
| `FWK-001` | `VALIDATED` | Preflight-Vertrag und `Templates/00_Preflight.sql` |
| `FWK-002` (Namens-, Schutz- und Lifecycle-Vertrag für Testdatenbanken) | begrenzter Nachweis; siehe unten | markergeprüfter Testdatenbank-Lifecycle |
| `FWK-003` (Vertrag für synthetische Testdaten) | `VALIDATED` | deterministischer Datengenerator |
| `FWK-004` (Messvertrag) | `VALIDATED` | sessionbezogener Messrahmen |
| `FWK-005` (Vertrag für Plan- und Statistikevidenz) | `VALIDATED` | Plan- und Statistikevidenz |
| `FWK-006` (Multi-Session-Orchestrierungsvertrag) | `VALIDATED` | Datenbanksignale und `Tools/orchestrate_sessions.py` |
| `FWK-007` (Query-Store- und Extended-Events-Vertrag) | `VALIDATED` | Query-Store- und XE-Lifecycle |
| `FWK-008` | `VALIDATED` | Sicherheits- und Abbruchvertrag |
| `FWK-009` | `VALIDATED` | vollständige Demo-Dokumentvorlage |
| `FWK-010` (Runtime-Harness-Vertrag) | `VALIDATED` | `Tools/run_demo.py` |
| `FWK-011` (Ergebnisnormalisierungs- und Erwartungsvertrag) | `VALIDATED` | Ergebnisnormalisierung und Evaluator |
| `FWK-012` | `VALIDATED` | Status-, Fehler- und Skip-Vertrag 1.2 |

`VALIDATED` umfasst die SQL-Server-unabhängigen Vertrags- und Prozess-Selbsttests sowie den erfolgreichen Runtime-Lauf `30099942191` auf SQL Server 2019, 2022 und 2025 in offiziellen Microsoft-Linux-Containern mit Compatibility Levels 150, 160 und 170. Betriebssystem- oder editionsspezifische Erweiterungen benötigen weiterhin eigene Testprofile.

Diese historische Abnahme belegt keine aktuelle allgemeine Eigentumsgarantie.
Die Referenz für Testdatenbanken prüft vorhandene Datenbanken jetzt mit
vollständigen, binären Marker- und Bytelängenvergleichen. Die
[abgegrenzte Eigentumsprüfung](../../Documentation/Project_Planning/FWK_002_FRAMEWORK_OWNERSHIP_REVIEW.md)
führt den tatsächlichen Prüfstand und die weiterhin offene Wiederherstellung
nach fehlgeschlagener Erstmarkierung. Der CREATE-Fehlerpfad erhält eine in
diesem Batch angelegte, noch vorhandene Datenbank ohne vollständige
Eigentumsmarker und liefert `FAIL_CLEANUP` samt ursprünglichem Fehlerrecord.
Ein passender Datenbankname allein genügt nicht. Nach einem Abbruch gilt die
Erhaltung bei ungeklärtem Eigentum gemäß
[Demo-Ausführungsleitfaden](../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md).

Aktion, Demokennung und Lauftoken werden vor jeder Typkürzung vollständig
geprüft. Erst gültige Eingaben dürfen einen Datenbanknamen bestimmen.
Für erlaubte Schreibweise und Normalisierung gilt der
[Namensvertrag](Contracts/FWK-002_TestDatabase_Lifecycle_Contract.md#2-kanonisches-namensschema).
Der [abgegrenzte Eingabenachweis](../../Documentation/Project_Planning/FWK_002_FRAMEWORK_INPUT_REVIEW.md)
trennt vorbereitete Quellen von tatsächlicher Prüfung und Integration.

## Toolklassen

| Klasse | Bestandteile |
|---|---|
| Systemobjekte | SQL-Server-Kataloge, DMVs (Dynamic Management Views; dynamische Verwaltungssichten für Diagnoseinformationen), Query Store und Extended Events |
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

`Tools/run_demo.py` verbindet sich über `--server`, `--auth` und `--username`. Gegen eine vorhandene SQL-Server-Instanz beschreibt `Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md` den vollständigen Ablauf einschließlich Anmeldedaten, Preflight, Cleanup und Recovery. Trägt die Instanz ein selbstsigniertes Zertifikat, wird `Tests/Runtime/host_sqlcmd_target.py` als `--sqlcmd` zwischengeschaltet, weil `build_sqlcmd_command()` selbst kein `-C` setzt.

## Sicherheitsgrundsätze

- Keine Datenbank wird aufgrund ihres Namens allein gelöscht.
- Vorhandene Datenbanken benötigen vor Änderungen vollständig passende Eigentumsmarker; für Neuanlage und Wiederherstellung gelten die gesonderten Vertragsgrenzen.
- Gelbe und rote Demos benötigen technisch erzwungene Bestätigungen.
- Passwörter stehen weder in Manifesten noch in Kommandozeilen; SQL-Authentifizierung verwendet `SQLCMDPASSWORD`.
- Kontrollierte Nichtanwendbarkeit ist `SKIP`, kein technischer Fehler.
- Prozess-Timeouts beenden verbleibende Kindprozesse.
- Umgebungsdetails, Querytexte, Pläne, Event-Daten und Rohoutput werden standardmäßig nicht persistiert.
- Absolute Performancegrenzen benötigen ein technisch kontrolliertes Ressourcenprofil.

## Prüfpfade

Der pfadbegrenzte Workflow `Framework contracts` führt vier SQL-Server-unabhängige Prüfungen aus. Der Workflow `Framework SQL matrix` startet getrennte ephemere Container für SQL Server 2019, 2022 und 2025 und validiert Installation, Laufzeitverträge sowie markergeprüftes Cleanup.

Die Prioritäten und tatsächlichen Nachweise der Pilotdemos stehen im
[aktuellen Ausführungsstand](../../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md).
Eine begrenzte Frameworkprüfung ersetzt keine vollständige Demoabnahme.
