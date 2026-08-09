# Tests/Lab – Qualitätssicherung für SQL_Server_Lab-Szenarien

Dieses Verzeichnis enthält die projektinterne Steuerung automatisierter Prüfungen für Umgebungen aus `gecompat/SQL_Server_Lab`.

Der primäre Benutzervertrag steht unter [`SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`](../../Documentation/Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md). Dort wird festgelegt, wie ein einzelnes Schulungsbeispiel ausgewählt, technisch vorbereitet, als `READY_FOR_USER` übergeben, interaktiv durchgeführt, zurückgesetzt und entfernt wird.

## Dateien

| Datei | Zweck |
|---|---|
| `performance-lab-matrix.json` | ordnet produktive Demo-Manifeste automatisierten Provider-, Safety- und Versionsprüfungen zu |
| `performance-lab-matrix.schema.json` | formaler JSON-Schema-Vertrag für den schulungsinternen Testkatalog |

Der Testkatalog ist kein Benutzerszenariokatalog. Interaktive Szenariodefinitionen werden unter `LABSCN-002` separat modelliert.

## Rolle der Testautomation

Automatisierte Prüfungen sollen nachweisen, dass:

- die benötigte Umgebung über `SQL_Server_Lab` aufgebaut werden kann;
- die fachliche Vorbereitung reproduzierbar ist;
- zentrale Kernbeobachtungen eintreten;
- der Reset funktioniert;
- die Umgebung vollständig entfernt werden kann.

Ein automatisierter Lauf darf seine kurzlebige Umgebung am Ende entfernen. Das Zielverhalten eines interaktiven Szenarios ist dagegen:

```text
Provisionieren
-> Vorbereiten
-> READY_FOR_USER
-> Benutzer arbeitet mit dem Beispiel
-> Reset oder ausdrücklicher Abbau
```

## Verantwortungsgrenze

`SQL_Server_Lab` wird für Docker, Podman, Hyper-V oder gemischte Topologien verwendet und verwaltet deren Infrastruktur-Lifecycle.

`SQL_PerformanceSchulung` verantwortet Szenarioauswahl, Demo-Harness, synthetische Daten, fachliche Assertions, Benutzeranleitung, Beobachtungsaufträge und Reset.

## Discovery-Regel

Der statische Validator entdeckt alle produktiven Dateien `Demos/**/manifest.json`. Manifeste unter `Demos/00_Framework/` gelten als Frameworkbeispiele und werden ausgeschlossen. Jedes andere Manifest muss genau einmal im Testkatalog vorkommen.

Diese Regel stellt sicher, dass neue Demos in die Qualitätssicherung aufgenommen werden. Sie sagt noch nicht aus, ob die Demo als interaktives Szenario geeignet ist. Diese Klassifikation erfolgt unter `LABSCN-002`.

## Geplante Testcommands

`LABINT-002` implementiert nach dem ersten interaktiven Vertical Slice technische Prüfaufrufe, beispielsweise:

```powershell
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 -Lane SMOKE
./Tests/Lab/Invoke-PerformanceLabMatrix.ps1 -Lane CORE -Provider docker
```

Die spätere Benutzerbedienung für interaktive Szenarien wird getrennt unter `LABSCN-004` standardisiert.

## Lokaler SQL_Server_Lab-Vertical-Slice

`Invoke-SqlServerLabScenarioTest.ps1` führt den ersten ausführbaren,
containerbasierten Integrationspfad für `QRY-001` aus. Der Pfad benötigt keine
Hyper-V- oder Windows-Gastumgebung. Er verwendet ausschließlich öffentliche
Commands aus `SQL_Server_Lab`:

1. `Test-SqlServerLabManifest` validiert das Docker- oder Podman-Manifest unter
   `Scenarios/QRY-001/`;
2. `New-SqlServerLab` erzeugt eine kompakte SQL-Server-2025-Instanz auf Docker
   oder Podman;
3. `Get-SqlServerLab` bestätigt den Live-Status; die SQL-Readiness ist bereits
   Abschlussbedingung der Provisionierung;
4. der vorhandene `FWK-010`-Harness führt `QRY-001` standardmäßig zweimal aus;
5. `Invoke-SqlServerLabScript` prüft nach jedem Lauf unabhängig, dass die
   markierte Testdatenbank entfernt wurde;
6. `Remove-SqlServerLab` entfernt Container, Volumes, Secrets und Run-State
   scopegebunden.

Der Lab-State liegt standardmäßig unter `Runtime/State/SqlServerLab` und wird
nicht versioniert. Das Kennwort wird als `SecureString` erzeugt oder übergeben
und nur für Kindprozesse temporär in `SQLCMDPASSWORD` gesetzt.

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

Der aktuelle Vertical Slice ist auf SQL Server 2025 begrenzt. Docker und Podman
sind lokal mit jeweils zwei vollständigen Läufen validiert. Die Versionen 2019
und 2022 bleiben getrennte Folgearbeiten. Der lokale Laufnachweis und die bewusst
offene Grenze zum interaktiven Workflow stehen unter
[`LABINT_002_QRY_001_LOCAL_RESULT.md`](../../Documentation/Project_Planning/LABINT_002_QRY_001_LOCAL_RESULT.md).

## Sicherheitsregeln

- Rot wird niemals implizit eingeschlossen.
- Gelb benötigt eine ausdrückliche Isolationsbestätigung.
- Secrets werden nicht in Katalog, Szenariodefinition oder Report persistiert.
- Lokaler Lab-State und technische Diagnosen verbleiben außerhalb versionierter Projektpfade.
- Änderungen in `SQL_Server_Lab` erfolgen nur nach konkretem Szenariobefund und ausdrücklicher Freigabe.
