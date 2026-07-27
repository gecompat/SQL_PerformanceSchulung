# Infrastructure

Die allgemeine Erzeugung und Verwaltung von SQL-Server-Laborumgebungen mit Docker, Podman oder Hyper-V liegt im zentralen Repository:

**https://github.com/gecompat/SQL_Server_Lab**

Dieses Repository (`SQL_PerformanceSchulung`) enthält keine eigene Provider- oder Lab-Provisionierung. Die Schulungsumgebung wird über `SQL_Server_Lab` bereitgestellt. Demo-Manifeste, synthetische Inhalte, Demoausführung und fachliche Assertions verbleiben im Schulungsrepository.

## Workflow

1. SQL-Server-Umgebung mit `SQL_Server_Lab` bereitstellen.
2. Host und Port aus dem zurückgegebenen Lab-Objekt übernehmen.
3. Demo mit dem vorhandenen Harness unter `Demos/00_Framework/Tools/run_demo.py` ausführen.
4. Demo-Cleanup unabhängig verifizieren.
5. Labumgebung über `Remove-SqlServerLab` entfernen.
6. Infrastruktur-Cleanup prüfen.

`SQL_Server_Lab` muss die Schulungsdemos nicht kennen und führt deren fachliche Phasen nicht aus.

## Automatisierte Testmatrix

Die verbindliche Architektur für Docker-/Podman-Testaufbau, Versionsmatrix, Safety-Lanes, Discovery und Cleanup steht unter:

- [`SQL_SERVER_LAB_TEST_AUTOMATION.md`](../Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md)
- [`Tests/Lab/performance-lab-matrix.json`](../Tests/Lab/performance-lab-matrix.json)

`LABINT-001` stellt Verantwortungsgrenze, Katalog, Schema und statische Vollständigkeitsprüfung bereit. `LABINT-002` implementiert den einfachen lokalen Runner über `New-SqlServerLab`, den bestehenden Demo-Harness und `Remove-SqlServerLab`.

Eine Project-Adapter-/Lab-Package-Engine oder generische JSON-/Event-Schnittstelle ist keine Voraussetzung dieses Projekts.

## Lokale Geheimnisse

Secrets, reale Hostnamen, Benutzerkonten, Pfade und interne Netzwerkdaten dürfen nicht eingecheckt werden. Beispielwerte müssen eindeutig synthetisch sein. Lokaler Lab-State und technische Runtime-Diagnosen bleiben außerhalb versionierter Projektpfade.
