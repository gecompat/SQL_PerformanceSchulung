# Tests/Lab – Integration mit SQL_Server_Lab

Dieses Verzeichnis enthält den projektseitigen Adaptervertrag für automatisierte Testläufe auf Umgebungen aus `gecompat/SQL_Server_Lab`.

## Dateien

| Datei | Zweck |
|---|---|
| `performance-lab-matrix.json` | katalogisiert alle produktiven Demo-Manifeste und ihre Infrastruktur-, Safety- und Versionsanforderungen |
| `performance-lab-matrix.schema.json` | formaler JSON-Schema-Vertrag für den Katalog |

Der vollständige Architektur- und Ablaufvertrag steht unter [`Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md`](../../Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md).

## Verantwortungsgrenze

`SQL_Server_Lab` provisioniert Docker- oder Podman-Umgebungen und verwaltet deren Infrastruktur-Lifecycle. Dieses Repository führt anschließend den vorhandenen Demo-Harness aus. Fachliche Demo-Phasen werden nicht in das Lab-Repository kopiert.

## Discovery-Regel

Der statische Validator entdeckt alle produktiven Dateien `Demos/**/manifest.json`. Manifeste unter `Demos/00_Framework/` gelten als Frameworkbeispiele und werden ausgeschlossen. Jedes andere Manifest muss genau einmal im Testkatalog vorkommen.

## Geplante Commands

`LABINT-002` implementiert einen lokalen PowerShell-Runner mit folgenden Zielaufrufen:

```powershell
# schneller grüner Test auf dem ersten verfügbaren Provider
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 -Lane SMOKE

# grüne Versionsmatrix auf Docker
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 -Lane CORE -Provider docker

# Providerparität einschließlich gelber Demos
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 `
    -Lane PROVIDER_PARITY `
    -ConfirmIsolatedLab
```

Diese Commands sind in `LABINT-001` noch nicht implementiert. Der aktuelle Stand umfasst Architektur, Katalog, Schema und statische Vollständigkeitsprüfung. Runtimefreigabe wird erst nach realen Docker- und Podman-Läufen erteilt.

## Sicherheitsregeln

- Rot wird niemals implizit eingeschlossen.
- Gelb benötigt eine ausdrückliche Isolationsbestätigung.
- Das SA-Kennwort wird nicht in Katalog, Manifest oder Report persistiert.
- Lokaler Lab-State und technische Diagnosen verbleiben außerhalb versionierter Projektpfade.
- Nach jeder Demo wird ihr fachlicher Cleanup geprüft; danach entfernt `SQL_Server_Lab` die Infrastruktur.
