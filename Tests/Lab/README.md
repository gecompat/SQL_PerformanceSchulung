# Tests/Lab – Integration mit SQL_Server_Lab

Dieses Verzeichnis enthält die projektinterne Steuerung für automatisierte Testläufe auf Umgebungen aus `gecompat/SQL_Server_Lab`.

## Dateien

| Datei | Zweck |
|---|---|
| `performance-lab-matrix.json` | katalogisiert alle produktiven Demo-Manifeste und ihre Infrastruktur-, Safety- und Versionsanforderungen |
| `performance-lab-matrix.schema.json` | formaler JSON-Schema-Vertrag für den schulungsinternen Katalog |

Der vollständige Architektur- und Ablaufvertrag steht unter [`Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md`](../../Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md).

## Verantwortungsgrenze

`SQL_Server_Lab` erstellt und entfernt die Docker- oder Podman-Umgebung und liefert Host, Port, Provider und Run-ID zurück.

Dieses Repository:

- wählt die Demos aus;
- führt den vorhandenen Demo-Harness aus;
- bewertet fachliche Ergebnisse;
- prüft den Demo-Cleanup;
- bildet die Versions- und Providermatrix.

Der JSON-Katalog in diesem Verzeichnis wird nicht von `SQL_Server_Lab` verarbeitet. Eine Project-Adapter-/Lab-Package-Engine oder generische JSON-/Event-Schnittstelle ist keine Voraussetzung der Schulungsautomation.

## Discovery-Regel

Der statische Validator entdeckt alle produktiven Dateien `Demos/**/manifest.json`. Manifeste unter `Demos/00_Framework/` gelten als Frameworkbeispiele und werden ausgeschlossen. Jedes andere Manifest muss genau einmal im Testkatalog vorkommen.

## Geplante Commands

`LABINT-002` implementiert einen lokalen PowerShell-Runner mit folgenden Zielaufrufen:

```powershell
# schneller grüner Test auf dem ersten verfügbaren Provider
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 -Lane SMOKE

# grüne Versionsmatrix auf Docker
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 -Lane CORE -Provider docker

# Providerparität einschließlich freigegebener gelber Demos
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 `
    -Lane PROVIDER_PARITY `
    -ConfirmIsolatedLab
```

Der Runner verwendet ausschließlich die öffentlichen Lab-Commands `New-SqlServerLab`, `Get-SqlServerLab` und `Remove-SqlServerLab`. Zusätzliche Lab-Funktionalität wird erst verlangt, wenn ein realer Lauf eine konkrete Lücke nachweist.

## Sicherheitsregeln

- Rot wird niemals implizit eingeschlossen.
- Gelb benötigt eine ausdrückliche Isolationsbestätigung.
- Das SA-Kennwort wird nicht in Katalog, Manifest oder Report persistiert.
- Lokaler Lab-State und technische Diagnosen verbleiben außerhalb versionierter Projektpfade.
- Nach jeder Demo wird ihr fachlicher Cleanup geprüft; danach entfernt `SQL_Server_Lab` die Infrastruktur.
