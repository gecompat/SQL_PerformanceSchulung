# CON-004 interaktiv bereitstellen

## Voraussetzungen

- PowerShell 7.2 oder neuer;
- `SQL_Server_Lab` ab der im Labkatalog angegebenen Mindestversion;
- Docker oder Podman;
- Microsoft `sqlcmd`;
- eine bestätigte isolierte Wegwerfumgebung.

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
Wegwerfinstanz, führt Preflight, Setup und Baseline aus und endet mit
`READY_FOR_USER`. Die Ausgabe enthält Server, Datenbank, Einstiegspunkt und die
vier Rollen `HEAD`, `MIDDLE`, `LEAF` und `OBSERVER`. Sie enthält kein Kennwort.

## Interaktive Durchführung

Vier SQL-Fenster mit der ausgegebenen Datenbank verbinden. Die in der Übergabe
genannten Skripte in der Reihenfolge `HEAD`, `MIDDLE`, `LEAF`, `OBSERVER`
starten. Der Observer prüft die Blocking Chain und löst anschließend die
kontrollierte Freigabe aus. Das automatisierte Runtime-Manifest bleibt ein
getrennter `AUTOMATED_VERIFY`-Pfad.

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
