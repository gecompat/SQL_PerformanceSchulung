# Interaktive Schulungsszenarien bedienen

Diese Anleitung standardisiert `LABSCN-004`: Auswahl, Start, Übergabe,
Reset und Remove verwenden für jedes freigegebene Szenario dieselben vier
PowerShell-Commands. Freigegeben sind `CON-004`, `DGN-005` und `CON-006`.

## 1. Sicherheitsgrenze und Voraussetzungen

- PowerShell 7.2 oder neuer;
- `SQL_Server_Lab` als installiertes Modul oder als lokales Repository;
- Docker oder Podman und Microsoft `sqlcmd`;
- mindestens die im Szenarioinventar genannten Ressourcen;
- ausschließlich eine isolierte, vollständig entfernbare Labumgebung.

Das Szenarioinventar unter
`Documentation/Inventories/performance_scenario_inventory.json` ist die
Entscheidungsgrundlage für Provider, SQL-Version, Safety-Level,
Mindestressourcen und Resetstrategie. Ein `YELLOW`- oder `RED`-Szenario wird
nicht gegen eine Instanz mit fremder Arbeit gestartet.

## 2. Szenario auswählen

Vom Repository-Root aus:

```powershell
Import-Module ./Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psd1 -Force
Get-PerformanceTrainingScenario
Get-PerformanceTrainingScenario -ScenarioId CON-004
Get-PerformanceTrainingScenario -ScenarioId DGN-005
Get-PerformanceTrainingScenario -ScenarioId CON-006
```

Die Ausgabe nennt Safety-Level, unterstützte Provider, Zielstatus und
Einstiegsdokument. Nur ein dort gelistetes Szenario besitzt einen freigegebenen
interaktiven Lifecycle.

## 3. Provider prüfen und Szenario starten

Das Labmodul kann explizit übergeben werden; ohne Parameter wird zuerst
`SQL_SERVER_LAB_MODULE_PATH`, danach ein benachbartes `SQL_Server_Lab`-
Repository und schließlich ein installiertes Modul gesucht.

```powershell
$labModule = '../SQL_Server_Lab/SqlServerLab.psd1'
Import-Module $labModule -Force
Test-SqlServerLabPrerequisite -Provider docker
# Alternative:
Test-SqlServerLabPrerequisite -Provider podman

$labCredential = Read-Host 'Synthetisches SA-Kennwort' -AsSecureString
$ready = Start-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -Provider docker `
    -SaPassword $labCredential `
    -SqlServerLabModulePath $labModule
```

Für Podman wird nur `-Provider podman` geändert. Start erstellt eine
scopegebundene Wegwerfumgebung, installiert und validiert den Project Adapter
und liefert erst danach `READY_FOR_USER`. Bei einem Startfehler entfernt der
Command den begonnenen Lab-Run wieder.

## 4. Übergabe an die Benutzerin oder den Benutzer

`$ready` enthält ohne Kennwort:

- `Server` und `Database` für die SQL-Verbindung;
- `SqlcmdVariables` für Demo-ID und Run-Token;
- die geordneten `SessionRoles` mit Skriptpfad und Arbeitsauftrag;
- `EntryDocument`, `ResetCommand` und `RemoveCommand`.

Vor der fachlichen Arbeit müssen `Status`, Provider und Safety-Grenze geprüft
werden:

```powershell
$ready | Select-Object ScenarioId,Status,Provider,Server,Database,SafetyLevel
$ready.SessionRoles | Format-Table startOrder,role,script
```

Nur `READY_FOR_USER` ist eine gültige Übergabe. Die Sessionrollen werden in der
ausgegebenen Reihenfolge gestartet. Für `CON-004` sind das `HEAD`, `MIDDLE`,
`LEAF` und `OBSERVER`; `CON-006` führt danach `ACTOR_A`, `ACTOR_B`, `OBSERVER`,
Evidenz, Gegenmaßnahme und geordnete Gegenprobe. Die konkrete SQLCMD-Belegung
steht im ausgegebenen Einstiegsdokument.

## 5. Reset und erneute Übergabe

```powershell
$reset = Reset-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -SaPassword $labCredential `
    -SqlServerLabModulePath $labModule

$reset.Status
```

Reset führt markergebundenes fachliches Cleanup, Installation und Validierung
auf derselben Labinstanz aus. Nur ein erneutes `READY_FOR_USER` bestätigt einen
erfolgreichen Reset. Infrastruktur und Run-ID bleiben erhalten.

## 6. Remove

```powershell
Remove-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -SaPassword $labCredential `
    -SqlServerLabModulePath $labModule `
    -Confirm:$false
```

Remove beseitigt zuerst die markergeprüften fachlichen Artefakte, danach
Container, Volumes, Secrets und lokalen aktiven Szenario-State. Erfolgsstatus
ist `REMOVED`. Der zugehörige abgeschlossene Lab-Auditdatensatz darf erhalten
bleiben; er enthält kein Kennwort.

## 7. Fehler- und Recovery-Regel

Bei einem Fehler wird nicht auf einer anderen Instanz weitergearbeitet. Zuerst
wird der exakte aktive Zustand angezeigt:

```powershell
Get-PerformanceTrainingScenario -ScenarioId CON-004
```

Ist ein aktiver Szenario-State vorhanden, wird derselbe
`Remove-PerformanceTrainingScenario`-Aufruf wiederholt. Ein direkter Eingriff
in Container oder State-Dateien ist nur eine Recovery-Maßnahme nach Prüfung der
exakten Run-ID. Der normale Lifecycle endet immer über `Remove`.

## 8. Abnahmepfad

Der vollständige Lifecycle ist für Docker und Podman auf SQL Server 2025
praktisch validiert. Er lässt sich mit dem vorhandenen Smoke-Test erneut
prüfen:

```powershell
./Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1 `
    -ScenarioId CON-006 `
    -Provider docker `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1

./Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1 `
    -ScenarioId CON-006 `
    -Provider podman `
    -SqlServerLabModulePath ../SQL_Server_Lab/SqlServerLab.psd1
```

Die Detailanleitungen stehen unter
`Documentation/HowTo/CON_004_INTERACTIVE_SCENARIO.md` und
`Documentation/HowTo/DGN_005_INTERACTIVE_SCENARIO.md` sowie
`Documentation/HowTo/CON_006_INTERACTIVE_SCENARIO.md`.
