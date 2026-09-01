# DGN-005 interaktiv bereitstellen

`DGN-005` verwendet den standardisierten Lifecycle aus
`INTERACTIVE_SCENARIO_LIFECYCLE.md`. Das Szenario ist `YELLOW`, benötigt eine
isolierte Wegwerfinstanz und exportiert keine Eventdateien.

## Start

```powershell
Import-Module ./Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psd1 -Force
$labCredential = Read-Host 'Synthetisches SA-Kennwort' -AsSecureString
$ready = Start-PerformanceTrainingScenario `
    -ScenarioId DGN-005 `
    -Provider docker `
    -SaPassword $labCredential `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1
```

Podman verwendet `-Provider podman`. Eine gültige Übergabe endet mit
`READY_FOR_USER` und nennt `SQLPERF_LAB_DGN005_LOCAL` als Datenbank.

## Interaktiver Ablauf

Ein SQL-Fenster mit der ausgegebenen Datenbank verbinden, SQLCMD-Modus
aktivieren und setzen:

```sql
:setvar DemoId "DGN-005"
:setvar RunToken "LOCAL"
```

Danach die in `$ready.SessionRoles` ausgegebenen Skripte nacheinander starten:

1. `DEMONSTRATION` erzeugt zwei synthetische Fehler;
2. `OBSERVATION` prüft die markergefilterte Ring-Buffer-Evidenz;
3. `MITIGATION` stoppt die Session;
4. `COMPARISON` bestätigt Stopzustand und Evidenzvertrag.

Eine fehlende Ereigniszeile ist nur zusammen mit Session, Filter, Eventklasse
und Zeitraum interpretierbar. Der fachlich zulässige Ausgang
`SKIP_EVIDENCE_MISSING` wird nicht in eine falsche Erfolgsaussage umgedeutet.

## Reset und Remove

```powershell
Reset-PerformanceTrainingScenario `
    -ScenarioId DGN-005 `
    -SaPassword $labCredential `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1

Remove-PerformanceTrainingScenario `
    -ScenarioId DGN-005 `
    -SaPassword $labCredential `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1 `
    -Confirm:$false
```

Reset entfernt Session und Testdatenbank markergebunden und stellt den
`READY_FOR_USER`-Zustand auf derselben Instanz neu her. Remove beseitigt danach
die fachlichen Artefakte und die scopegebundene Labinfrastruktur.

## Lifecycle-Abnahme

```powershell
./Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1 `
    -ScenarioId DGN-005 `
    -Provider docker `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1

./Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1 `
    -ScenarioId DGN-005 `
    -Provider podman `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1
```
