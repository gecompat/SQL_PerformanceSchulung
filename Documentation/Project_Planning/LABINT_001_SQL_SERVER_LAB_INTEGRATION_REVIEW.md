# Review – LABINT-001 SQL_Server_Lab-Testautomation

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-27 |
| Ursprünglicher Pull Request | `#21` |
| Korrekturgrund | langfristige Lab-Architektur wurde fälschlich als Schulungsanforderung interpretiert |
| geprüfter Lab-Commit | `08fcc9525b9bbc29a5dd9a2ef08de23bd7ef650e` |
| Änderungen in SQL_Server_Lab | keine |
| Runtime-Provisionierung ausgeführt | nein |

## 1. Korrektur

Die erste Fassung des Integrationsreviews leitete aus dem langfristigen Architekturentwurf von `SQL_Server_Lab` zusätzliche Anforderungen ab, die für `SQL_PerformanceSchulung` nicht notwendig sind. Dazu gehörten insbesondere eine Project-Adapter-/Lab-Package-Engine, eine generische JSON-/Event-Schnittstelle sowie weitere allgemeine Control-Plane-Funktionen.

Diese Ableitung war zu weitgehend. Das Schulungsprojekt erwartet keine generische Plattformintegration, sondern eine konkrete Arbeitsteilung:

```text
SQL_Server_Lab erstellt und entfernt die SQL-Server-Umgebung.
SQL_PerformanceSchulung führt seine eigenen Demos aus und bewertet sie.
```

## 2. Tatsächliche Erwartung an SQL_Server_Lab

Für den automatisierten Testlauf reichen folgende öffentliche Fähigkeiten:

- `New-SqlServerLab` für Docker oder Podman;
- Auswahl der SQL-Server-Version und eines Ressourcenprofils;
- SQL-Readiness;
- Rückgabe von Run-ID, Provider, Host und Port;
- `Get-SqlServerLab` zur Zustandsprüfung;
- `Remove-SqlServerLab -Force` zum sicheren Abbau.

Eine zusätzliche Lab-Funktion ist für den ersten Runner gegenwärtig nicht erforderlich.

## 3. Verantwortung des Schulungsrepositories

`SQL_PerformanceSchulung` bleibt Eigentümer von:

- Demo-Discovery und Testkatalog;
- Demo-Manifests;
- synthetischen Daten;
- Preflight, Setup, Baseline, Demonstration, Observation, Mitigation, Comparison und Cleanup;
- fachlichen Assertions und Skip-Verträgen;
- Versions- und Provider-Matrix;
- zusammengefasster Testausgabe.

Der JSON-Katalog unter `Tests/Lab` ist eine interne Steuerungsdatei des Schulungsprojekts. Er ist keine Schnittstellenanforderung an das Lab-Repository.

## 4. Nicht erforderliche Lab-Funktionen

Für dieses Projekt werden nicht vorausgesetzt:

- eine Project-Adapter- oder Lab-Package-Engine;
- eine generische JSON-/Event-Schnittstelle;
- ein allgemeiner Operationsbus;
- die Ausführung der Demo-Phasen durch `SQL_Server_Lab`;
- ein eigener Schulungs-Package-Katalog im Lab;
- eine Migration des bestehenden Demo-Harness in das Lab-Repository.

Diese Funktionen können für andere Ziele des Lab-Repositories sinnvoll sein, gehören jedoch nicht zum Abnahmeumfang der Schulungstestautomation.

## 5. Aktueller Testkatalog

Der Katalog umfasst weiterhin:

- `QRY-001`;
- `OPT-002`;
- `CON-004`;
- `OPT-013`;
- `OPT-015`;
- `OPT-016`.

Die vollständige Container-Matrix umfasst zwei Provider, drei SQL-Server-Versionen, sechs Demos und zwei Wiederholungen. Daraus entstehen aktuell 72 vollständige Demoläufe.

## 6. Mögliche konkrete Lab-Lücke

Im öffentlichen `Remove-SqlServerLab` ist nach dem allgemeinen Cleanup-Plan ein zusätzliches Docker-spezifisches Orphan-Sicherheitsnetz vorhanden. Ein entsprechender Podman-Pfad ist dort nicht sichtbar.

Der normale Cleanup-Plan wird bereits providerbezogen mit `docker rm` oder `podman rm` aufgebaut. Deshalb ist die Docker-spezifische Orphan-Prüfung zunächst nur eine mögliche Robustheitslücke. Sie gilt nicht als nachgewiesener Blocker.

Erst wenn `LABINT-003` einen verbliebenen Podman-Container oder einen unvollständigen Cleanup reproduziert, ist ein providerneutraler Orphan-Cleanup als konkrete Lab-Erweiterung zu verlangen. Eine solche Änderung wird vorab benannt und nicht ohne ausdrückliche Freigabe umgesetzt.

## 7. Statische Abnahme

Der korrigierte Validator prüft weiterhin:

- exakte Übereinstimmung zwischen produktiven Demo-Manifests und Testkatalog;
- Demo-ID, Pfad und Sicherheitsstufe;
- Docker-/Podman- und Versionszuordnung;
- Ressourcenprofil und Environment-Isolation;
- Multi-Session-Capability;
- Safety-Bestätigungen für gelbe und rote Lanes;
- Demo-Cleanup-Vertrag;
- Verbot von Secret-, Host- und absoluten Pfadangaben.

Zusätzlich verhindert er, dass `LABINT-005` oder die zuvor überzogene Pflicht zur nativen Lab-Package-Ausführung erneut in den Backlog aufgenommen wird.

## 8. Statusgrenze

`LABINT-001` ist als Verantwortungs-, Katalog- und statischer Prüfvertrag `VALIDATED`. Die Runtime-Provisionierung über `SQL_Server_Lab` ist noch nicht ausgeführt.

## 9. Nächster Schritt

`LABINT-002` implementiert einen einfachen PowerShell-Runner:

1. Lab-Modul importieren.
2. Umgebung mit `New-SqlServerLab` erstellen.
3. Host und Port übernehmen.
4. grüne Demos mit dem vorhandenen Harness ausführen.
5. Demo-Cleanup prüfen.
6. Umgebung mit `Remove-SqlServerLab` entfernen.

Erst reale Docker-/Podman-Läufe entscheiden, ob im Lab-Repository zusätzliche Funktionalität benötigt wird.
