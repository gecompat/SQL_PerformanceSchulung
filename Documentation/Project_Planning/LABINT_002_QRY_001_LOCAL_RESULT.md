# LABINT-002 – lokaler QRY-001-Container-Nachweis

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED_LOCAL_PROVIDER_PARITY` |
| Stand | 2026-08-09 |
| Szenario | `QRY-001` – SARGability |
| Provider | Docker und Podman |
| SQL-Server-Version | 2025 |
| Sicherheitsstufe | Grün |
| Hyper-V erforderlich | nein |
| Einordnung | technischer Vorläufer für `LABINT-002`; kein Abschluss von `LABSCN-003` |

## 1. Ziel

Der Lauf weist erstmals innerhalb dieses Repositorys praktisch nach, dass ein
vorhandenes Schulungsbeispiel seine Infrastruktur über öffentliche Commands aus
`SQL_Server_Lab` beziehen und anschließend über den bestehenden `FWK-010`-
Harness getestet werden kann.

`QRY-001` wurde gewählt, weil das Szenario grün, Single-Session-fähig und im
Inventar als containergeeigneter Vertical-Slice-Kandidat geführt wird. Der
fachliche Effekt benötigt weder Windows noch Hyper-V.

## 2. Implementierte Artefakte

| Artefakt | Aufgabe |
|---|---|
| `Scenarios/QRY-001/sql-server-lab.json` | versioniertes, secret-freies SQL_Server_Lab-Manifest für eine kompakte SQL-Server-2025-Docker-Instanz |
| `Scenarios/QRY-001/sql-server-lab.podman.json` | äquivalentes Manifest für Podman |
| `Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1` | Provisionierung, Statusprüfung, wiederholter Demolauf, unabhängige Cleanup-Prüfung und Infrastrukturabbau |
| `Tests/Lab/Sql/Assert-QRY-001-Cleanup.sql` | unabhängiger Nachweis, dass die markierte QRY-001-Testdatenbank nicht mehr vorhanden ist |
| `Tests/Static/validate_sql_server_lab_test_catalog.py` | statischer Vertrag für Manifest, Runner, Cleanup-Probe und Hyper-V-freie Topologie |

Der Lab-State liegt unter `Runtime/State/SqlServerLab` und bleibt durch die
vorhandenen Ignore-Regeln außerhalb versionierter Artefakte. Das synthetische
SA-Kennwort wird nur im Prozess gehalten und für `sqlcmd` temporär über
`SQLCMDPASSWORD` bereitgestellt.

## 3. Aufgerufene SQL_Server_Lab-Funktionalität

Der Runner verwendet ausschließlich öffentliche Commands:

1. `Test-SqlServerLabManifest`;
2. `New-SqlServerLab`;
3. `Get-SqlServerLab`;
4. `Invoke-SqlServerLabScript`;
5. `Remove-SqlServerLab`.

Die fachliche Datenbank, die synthetischen Daten, die Messungen und die
Assertions bleiben vollständig im Schulungsrepository. `SQL_Server_Lab`
übernimmt Provider-, Ressourcen-, Port-, Readiness-, State- und
Infrastruktur-Lifecycle.

## 4. Lokaler Laufnachweis

Die folgenden Aufrufe wurden mit jeweils zwei Wiederholungen ausgeführt:

```powershell
$pythonPath = (Get-Command python).Source
$env:SQLPERF_PYTHON = $pythonPath

./Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1 `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
    -PythonPath $pythonPath `
    -Repetitions 2

./Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1 `
    -Provider podman `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
    -PythonPath $pythonPath `
    -Repetitions 2
```

| Prüfschritt | Docker | Podman |
|---|---|---|
| SQL_Server_Lab-Manifest | gültig | gültig |
| Resource Assessment | `RESOURCE_OK` | `RESOURCE_OK` |
| Provisionierung und SQL-Readiness | `RUNNING`, Major Version 17 | `RUNNING`, Major Version 17 |
| Initiale Cleanup-Probe | erfolgreich | erfolgreich |
| `QRY-001`, Lauf 1 | alle Phasen `PASS/OK` | alle Phasen `PASS/OK` |
| Cleanup-Probe nach Lauf 1 | erfolgreich | erfolgreich |
| `QRY-001`, Lauf 2 | alle Phasen `PASS/OK` | alle Phasen `PASS/OK` |
| Cleanup-Probe nach Lauf 2 | erfolgreich | erfolgreich |
| Infrastrukturabbau | `REMOVED`, `CLEANUP_SUCCEEDED` | `REMOVED`, `CLEANUP_SUCCEEDED` |
| verbliebene aktive Lab-Runs | 0 | 0 |

Beide Läufe umfassten `PREFLIGHT`, `SETUP`, `BASELINE`, `DEMONSTRATION`,
`OBSERVATION`, `MITIGATION`, `COMPARISON` und `CLEANUP`.

### 4.1. Aktuellester Podman-Doppel-Lauf (bestätigt)

| Eigenschaft | Wert |
|---|---|
| Datum | 2026-08-09 |
| ScenarioId | `QRY-001` |
| Provider | `podman` |
| SQL Server | `2025` |
| Repetitions | `2` |
| RunId | `1c3edd11-aa0e-4f09-8430-2b85e182aaeb` |
| ScopeId | `38d6ce04-b6f0-4648-a9c4-c3a6c7efa813` |
| Initiale Probe | `Assert-QRY-001-Cleanup.sql` erfolgreich |
| Lauf 1 | `PREFLIGHT/SETUP/BASELINE/DEMONSTRATION/OBSERVATION/MITIGATION/COMPARISON/CLEANUP` = `PASS/OK` |
| Lauf 2 | `PREFLIGHT/SETUP/BASELINE/DEMONSTRATION/OBSERVATION/MITIGATION/COMPARISON/CLEANUP` = `PASS/OK` |
| Cleanup nach letzter Probe | erfolgreich |
| Infrastruktur | `Remove-SqlServerLab` -> `REMOVED`, `CLEANUP_SUCCEEDED` |
| DemoOutcome | `PASS` |

Ausgabe der finalen Objektzeile:

```text
ScenarioId : QRY-001
Provider   : podman
SqlVersion : 2025
Repetitions: 2
DemoOutcome: PASS
InfrastructureState: REMOVED
LabRunId : 1c3edd11-aa0e-4f09-8430-2b85e182aaeb
```

### 4.2. Docker-Doppel-Lauf (bestätigt)

Docker wurde vollständig durchgeführt und bestätigt.

```powershell
.\Tests\Lab\Invoke-SqlServerLabScenarioTest.ps1 `
  -Provider docker `
  -SqlServerLabModulePath ..\SQL_Server_Lab\SqlServerLab.psd1 `
  -PythonPath $pythonPath `
  -Repetitions 2
```

| Eigenschaft | Wert |
|---|---|
| Datum | 2026-08-09 |
| ScenarioId | `QRY-001` |
| Provider | `docker` |
| SQL Server | `2025` |
| Repetitions | `2` |
| RunId | `1ab246f5-9f55-4a58-b1a4-caf318061440` |
| ScopeId | `bcf97733-3322-4694-849a-c85075eed508` |
| Initiale Probe | `Assert-QRY-001-Cleanup.sql` erfolgreich |
| Lauf 1 | `PREFLIGHT/SETUP/BASELINE/DEMONSTRATION/OBSERVATION/MITIGATION/COMPARISON/CLEANUP` = `PASS/OK` |
| Lauf 2 | `PREFLIGHT/SETUP/BASELINE/DEMONSTRATION/OBSERVATION/MITIGATION/COMPARISON/CLEANUP` = `PASS/OK` |
| Cleanup nach letzter Probe | erfolgreich |
| Infrastruktur | `Remove-SqlServerLab` -> `REMOVED`, `CLEANUP_SUCCEEDED` |
| DemoOutcome | `PASS` |

Ausgabe der finalen Objektzeile:

```text
ScenarioId          : QRY-001
Provider            : docker
SqlVersion          : 2025
Repetitions         : 2
DemoOutcome         : PASS
InfrastructureState : REMOVED
LabRunId            : 1ab246f5-9f55-4a58-b1a4-caf318061440
```

## 5. Bewusste Grenze

Dieser Nachweis schließt `LABSCN-003` noch nicht ab. Offen bleiben:

- fachliche Vorbereitung mit Übergabestatus `READY_FOR_USER`;
- interaktive Teilnehmeranleitung und Verbindungsübergabe;
- ein separates Reset-Command für eine beibehaltene Umgebung;
- der ausdrückliche Remove-Workflow eines interaktiven Runs;
- die Versionen 2019 und 2022.

Der implementierte Pfad ist die technische Grundlage für diese Schritte und
ein lokal validierter Smoke-Test, aber kein Ersatz für den interaktiven
Benutzerworkflow.
