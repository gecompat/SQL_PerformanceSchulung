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
./Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1 `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
    -PythonPath python `
    -Repetitions 2

./Tests/Lab/Invoke-SqlServerLabScenarioTest.ps1 `
    -Provider podman `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
    -PythonPath python `
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
