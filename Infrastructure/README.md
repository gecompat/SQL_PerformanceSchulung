# Infrastructure

Die allgemeine Erzeugung und Verwaltung von SQL-Server-Laborumgebungen mit Docker, Podman oder Hyper-V liegt im zentralen Repository:

**https://github.com/gecompat/SQL_Server_Lab**

Dieses Repository (`SQL_PerformanceSchulung`) enthält keine eigene Provider- oder Lab-Provisionierung. Die Schulungsumgebung wird über `SQL_Server_Lab` bereitgestellt. Das Schulungsrepository behält ausschließlich den Project Adapter, die Demo-Manifeste, synthetischen Inhalte und fachlichen Assertions.

## Workflow

1. SQL-Server-Umgebung mit `SQL_Server_Lab` bereitstellen.
2. Host und Port aus dem zurückgegebenen Lab-Objekt binden.
3. Demo mit dem vorhandenen Harness unter `Demos/00_Framework/Tools/run_demo.py` ausführen.
4. Demo-Cleanup unabhängig verifizieren.
5. Labumgebung über `Remove-SqlServerLab` entfernen.
6. Infrastruktur-Cleanup und sanitisierten Ergebnisstatus prüfen.

## Automatisierte Testmatrix

Die verbindliche Architektur für Docker-/Podman-Testaufbau, Versionsmatrix, Safety-Lanes, Discovery, Cleanup und spätere Lab-Package-Integration steht unter:

- [`SQL_SERVER_LAB_TEST_AUTOMATION.md`](../Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md)
- [`Tests/Lab/performance-lab-matrix.json`](../Tests/Lab/performance-lab-matrix.json)

Der aktuelle erste Integrationsstand enthält noch keinen ausführbaren Provisionierungsrunner. `LABINT-001` stellt Architektur, Katalog, Schema und statische Vollständigkeitsprüfung bereit. `LABINT-002` implementiert anschließend den lokalen Runner für die grünen Docker-/Podman-Lanes.

## Lokale Geheimnisse

Secrets, reale Hostnamen, Benutzerkonten, Pfade und interne Netzwerkdaten dürfen nicht eingecheckt werden. Beispielwerte müssen eindeutig synthetisch sein. Lokaler Lab-State und technische Runtime-Diagnosen bleiben außerhalb versionierter Projektpfade.
