# CON-006 interaktiv bereitstellen

Der providerneutrale Standardablauf für Auswahl, Start, Übergabe, Reset und
Remove steht unter `Documentation/HowTo/INTERACTIVE_SCENARIO_LIFECYCLE.md`.

## Voraussetzungen und Grenze

- PowerShell 7.2 oder neuer;
- `SQL_Server_Lab` ab Version 0.2.0;
- Docker oder Podman;
- Microsoft `sqlcmd`;
- eine bestätigte isolierte Wegwerfumgebung.

Der Project Adapter unter `Scenarios/CON-006/adapter` unterstützt in
Vertragsversion `0.1` ausschließlich SQL Server 2025 auf einer Linux-
Containerinstanz. Das Szenario ist `YELLOW`: Es erzeugt absichtlich einen
Deadlock und darf nicht auf einer Instanz mit fremder Arbeit ausgeführt werden.

## Auswahl und Start

```powershell
Import-Module ./Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psd1 -Force
Get-PerformanceTrainingScenario -ScenarioId CON-006

$labCredential = Read-Host 'Synthetisches SA-Kennwort' -AsSecureString
$ready = Start-PerformanceTrainingScenario `
    -ScenarioId CON-006 `
    -Provider docker `
    -SaPassword $labCredential
```

Der Start provisioniert eine SQL-Server-2025-Wegwerfinstanz, validiert den
Project Adapter gegen den konkreten Lab-Run und endet mit `READY_FOR_USER`.
Die Ausgabe enthält Server, Datenbank, Rollen und Skriptpfade, aber kein
Kennwort. Für alle SQL-Fenster gelten `DemoId=CON-006` und `RunToken=LOCAL`.

## Deadlock interaktiv durchführen

Drei SQL-Fenster mit der ausgegebenen Datenbank verbinden und SQLCMD-Modus
aktivieren. In jedem Fenster zuerst setzen:

```sql
:setvar DemoId "CON-006"
:setvar RunToken "LOCAL"
```

Danach:

1. `ACTOR_A` in Fenster A starten;
2. `ACTOR_B` in Fenster B starten;
3. `OBSERVER` in Fenster C starten;
4. `EVIDENCE` ausführen und Ergebnisablage sowie optionalen
   `system_health`-Graph prüfen.

Der Ergebnisvertrag verlangt genau ein abgefangenes Opfer mit Fehler 1205 und
genau einen Survivor. `ACTOR_A` besitzt `DEADLOCK_PRIORITY LOW` und ist das
erwartete Opfer. Ein nicht sichtbarer Ring-Buffer-Graph ist kontrollierte
fehlende Zusatzevidenz und ändert diesen Ergebnisvertrag nicht.

## Geordnete Gegenprobe

1. `MITIGATION` ausführen;
2. `ORDERED_A` in Fenster A und `ORDERED_B` in Fenster B starten;
3. `VERIFICATION` ausführen.

Beide Akteure greifen nun in derselben Reihenfolge auf die zwei Zeilen zu. Die
Verifikation verlangt zwei `COMPLETED`-Ergebnisse und kein Opfer. Daraus folgt
keine allgemeine Empfehlung zur Transaktionsgestaltung; die Gegenprobe zeigt
nur die Wirkung einer konsistenten Zugriffsreihenfolge in diesem synthetischen
Vertrag.

## Reset und Remove

```powershell
Reset-PerformanceTrainingScenario `
    -ScenarioId CON-006 `
    -SaPassword $labCredential

Remove-PerformanceTrainingScenario `
    -ScenarioId CON-006 `
    -SaPassword $labCredential `
    -Confirm:$false
```

Reset entfernt die markergeprüfte Testdatenbank und stellt auf derselben
Instanz erneut `READY_FOR_USER` her. Remove führt zuerst den fachlichen Cleanup
aus und entfernt danach ausschließlich die scopegebundene Lab-Infrastruktur.

## Vollständiger Lifecycle-Smoke

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

Der Smoke führt Deadlock, optionale Beobachtung, geordnete Gegenprobe, Reset
und Remove aus. Raw Deadlock-Graphen, Querytexte oder Kennwörter werden nicht
persistiert.
