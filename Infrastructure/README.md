# Infrastructure

Die allgemeine Erzeugung und Verwaltung von SQL-Server-Laborumgebungen (Docker, Hyper-V, Podman) liegt im zentralen Repository:

**https://github.com/gecompat/SQL_Server_Lab**

Dieses Repository (`SQL_PerformanceSchulung`) enthaelt keine eigene Lab-Provisionierung. Die Schulungsumgebung wird ueber `SQL_Server_Lab` bereitgestellt.

## Workflow

1. SQL-Server-Umgebung mit `SQL_Server_Lab` bereitstellen
2. Schulungs-Package installieren (Demos, synthetische Testdaten)
3. Demo ausfuehren (`Demos/`)
4. Demo bereinigen
5. Labumgebung ueber `SQL_Server_Lab` entfernen

## Lokale Geheimnisse

Secrets, reale Hostnamen, Benutzerkonten, Pfade und interne Netzwerkdaten duerfen nicht eingecheckt werden. Beispielwerte muessen eindeutig synthetisch sein.
