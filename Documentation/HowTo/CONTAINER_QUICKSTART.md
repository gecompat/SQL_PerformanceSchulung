# Docker-/Podman-Quickstart ohne vorhandenen SQL Server

Dieser Quickstart schließt `INF-002` und `INF-003` für den kompakten,
praktisch validierten Arbeitsplatzpfad. Er provisioniert keinen dauerhaften SQL
Server, sondern eine isolierte SQL-Server-2025-Linux-Wegwerfumgebung für das
interaktive Szenario `CON-004`.

## Voraussetzungen

- PowerShell 7.2 oder neuer;
- Git, Microsoft `sqlcmd` und entweder Docker oder Podman;
- mindestens 2 CPU-Kerne, 4 GB freier RAM und 5 GB freier Speicher;
- ein lokales `SQL_Server_Lab`-Repository neben diesem Repository oder ein
  installiertes `SqlServerLab`-Modul.

Unter Windows müssen WSL 2 und Hardwarevirtualisierung für die
Containerruntime aktiv sein. Bei Podman muss die Podman Machine laufen. Die
vollständigen Installationshinweise liegen im `SQL_Server_Lab`-Repository unter
`Documentation/User/INSTALLATION_WINDOWS.md` beziehungsweise
`Documentation/User/INSTALLATION_LINUX.md`.

## 1. Werkzeuge nur prüfen

Vom Root dieses Repositories aus:

```powershell
$PSVersionTable.PSVersion
sqlcmd -?
docker info   # Docker-Pfad
podman info   # Podman-Pfad; bei Bedarf vorher: podman machine start
```

Danach den providerneutralen Lab-Preflight verwenden:

```powershell
$labModule = '../SQL_Server_Lab/SqlServerLab.psd1'
Import-Module $labModule -Force
Test-SqlServerLabPrerequisite -Provider docker
# oder
Test-SqlServerLabPrerequisite -Provider podman
```

Der Preflight verändert keine Labinfrastruktur. Fehlende Runtime-, `sqlcmd`-
oder Ressourcenanforderungen werden vor der Provisionierung sichtbar.

## 2. Kompakten Lifecycle starten

```powershell
Import-Module ./Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psd1 -Force
$labCredential = Read-Host 'Synthetisches SA-Kennwort' -AsSecureString

$ready = Start-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -Provider docker `
    -SaPassword $labCredential `
    -SqlServerLabModulePath $labModule

$ready | Select-Object ScenarioId,Status,Provider,Server,Database,SafetyLevel
$ready.SessionRoles | Format-Table startOrder,role,script
```

Für Podman wird ausschließlich `-Provider podman` verwendet. Das Kennwort
bleibt ein `SecureString`, wird nicht in der Ausgabe angezeigt und nicht im
Repository-State gespeichert. Erst `READY_FOR_USER` erlaubt die Übergabe an
die SQL-Fenster.

## 3. Arbeiten, Reset und Remove

Die Sessionvariablen und die Reihenfolge stehen in `$ready`. Der vollständige
Benutzerablauf ist in `INTERACTIVE_SCENARIO_LIFECYCLE.md` beschrieben.

```powershell
Reset-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -SaPassword $labCredential `
    -SqlServerLabModulePath $labModule

Remove-PerformanceTrainingScenario `
    -ScenarioId CON-004 `
    -SaPassword $labCredential `
    -SqlServerLabModulePath $labModule `
    -Confirm:$false
```

Reset endet erneut mit `READY_FOR_USER`; Remove endet mit `REMOVED`. Der aktive
State liegt ausschließlich unter `Runtime/State/PerformanceTrainingScenario`
und ist nicht versioniert.

## 4. Recovery

Ein fehlgeschlagener Start baut den begonnenen Lab-Run automatisch ab. Bleibt
nach einem späteren Abbruch ein aktiver Zustand, wird zuerst
`Get-PerformanceTrainingScenario -ScenarioId CON-004` ausgeführt und danach
derselbe Remove-Aufruf wiederholt. Container, Volumes oder State-Dateien werden
nicht anhand eines Namensmusters pauschal gelöscht.

## Validierungsgrenze

Der Docker- und Podman-Lifecycle `Start -> READY_FOR_USER -> Reset ->
READY_FOR_USER -> Remove` ist lokal mit SQL Server 2025 praktisch validiert.
Die CI prüft zusätzlich, dass dieser Quickstart nur öffentliche Commands,
synthetische Zugangsdaten und die markergebundene Cleanup-Grenze verwendet.
SQL Server 2019/2022, Hyper-V und gemischte Topologien sind nicht Bestandteil
dieses kompakten Arbeitsplatzpfads.
