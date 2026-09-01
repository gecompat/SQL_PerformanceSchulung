# CON-004 interaktiv bereitstellen

Der providerneutrale Standardablauf für Auswahl, Start, Übergabe, Reset und
Remove steht unter `Documentation/HowTo/INTERACTIVE_SCENARIO_LIFECYCLE.md`.

## Voraussetzungen

- PowerShell 7.2 oder neuer;
- `SQL_Server_Lab` ab der im Labkatalog angegebenen Mindestversion;
- Docker oder Podman;
- Microsoft `sqlcmd`;
- eine bestätigte isolierte Wegwerfumgebung.

Der fachliche Aufbau verwendet den Project Adapter unter
`Scenarios/CON-004/adapter` mit Vertragsversion `0.1`. Der Adapter akzeptiert
ausschließlich SQL Server 2025 auf einer Linux-Containerinstanz und enthält
getrennte Entrypoints für Preflight, Installation, Validierung und Cleanup.

Das Szenario ist `YELLOW`. Es hält absichtlich Sperren und darf nicht auf einer
Instanz mit fremder Arbeit ausgeführt werden.

## Auswahl und Start

```powershell
Import-Module ./Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psd1 -Force
Get-PerformanceTrainingScenario -ScenarioId CON-004

$labCredential = Read-Host 'Synthetisches SA-Kennwort' -AsSecureString
$ready = Start-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -Provider docker `
    -SaPassword $labCredential
```

`Start-PerformanceTrainingScenario` provisioniert eine SQL-Server-2025-
Wegwerfinstanz, validiert den Adapter gegen den konkreten Lab-Run, führt dessen
Preflight-, Install- und Validate-Entrypoints aus und endet mit
`READY_FOR_USER`. Die Ausgabe enthält Adaptervertragsversion, Server,
Datenbank, Einstiegspunkt und die
vier Rollen `HEAD`, `MIDDLE`, `LEAF` und `OBSERVER`. Sie enthält kein Kennwort.
`SqlcmdVariables` liefert zusätzlich die verbindlichen Werte `DemoId=CON-004`
und `RunToken=LOCAL`.

## Interaktive Durchführung

Vier SQL-Fenster mit der ausgegebenen Datenbank verbinden und den SQLCMD-Modus
aktivieren. In jedem Fenster vor dem jeweiligen Session-Skript diese Variablen
setzen:

```sql
:setvar DemoId "CON-004"
:setvar RunToken "LOCAL"
```

Danach die in der Übergabe genannten Skripte in der Reihenfolge `HEAD`,
`MIDDLE`, `LEAF`, `OBSERVER` starten. Der Observer prüft die Blocking Chain und
löst anschließend die kontrollierte Freigabe aus. Das automatisierte
Runtime-Manifest bleibt ein getrennter `AUTOMATED_VERIFY`-Pfad.

## Reset

```powershell
Reset-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -SaPassword $labCredential
```

Der Reset entfernt markergeprüft die Testdatenbank und erzeugt Setup und
Baseline neu. Die Infrastruktur bleibt bestehen und der Zustand ist erneut
`READY_FOR_USER`.

## Remove

```powershell
Remove-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -SaPassword $labCredential `
    -Confirm:$false
```

Remove führt zuerst den fachlichen Cleanup aus und entfernt danach die
scopegebundene Lab-Infrastruktur. Lokaler Zustand liegt ausschließlich unter
`Runtime/State/PerformanceTrainingScenario`.

## Vollständiger Lifecycle-Smoke

Der folgende Test prüft Start, `READY_FOR_USER`, Reset auf derselben Instanz,
markergebundenes fachliches Cleanup und den vollständigen Infrastrukturabbau:

```powershell
./Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1 `
    -Provider docker `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1

./Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1 `
    -Provider podman `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1
```
