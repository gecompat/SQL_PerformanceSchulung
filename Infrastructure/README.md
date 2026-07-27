# Infrastructure

Die Erzeugung und Verwaltung der für Schulungsbeispiele benötigten SQL-Server-Laborumgebungen liegt im zentralen Repository:

**https://github.com/gecompat/SQL_Server_Lab**

`SQL_PerformanceSchulung` enthält keine eigene Docker-, Podman- oder Hyper-V-Provisionierung. Dieses Repository beschreibt je Beispiel die fachlichen und technischen Anforderungen; `SQL_Server_Lab` wird verwendet, um die passende Umgebung tatsächlich zu erzeugen.

## Primärer Benutzerworkflow

1. Ein einzelnes Schulungsbeispiel oder eine LAB-Serie auswählen.
2. SQL-Server-Versionen, Provider, Topologie, Ressourcen und Zusatzkomponenten aus der Szenariodefinition auflösen.
3. Umgebung über `SQL_Server_Lab` auf Docker, Podman, Hyper-V oder gemischten Providern bereitstellen.
4. Datenbanken, synthetische Daten, Konfigurationen und Ausgangssituation vorbereiten.
5. Umgebung im Status `READY_FOR_USER` mit Verbindungs- und Rollenbeschreibung übergeben.
6. Benutzer führt die vorgesehenen Schritte selbst aus, verändert Abfragen und wiederholt Beobachtungen.
7. Fachlichen Ausgangszustand zurücksetzen oder die gesamte Umgebung ausdrücklich entfernen.

Die Umgebung wird nach der Vorbereitung nicht automatisch abgebaut.

## Verbindliche Architektur

Der kanonische Zielvertrag steht unter:

- [`SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md`](../Documentation/Architecture/SQL_SERVER_LAB_INTERACTIVE_SCENARIOS.md)

Die nachgeordnete technische Qualitätssicherung steht unter:

- [`SQL_SERVER_LAB_TEST_AUTOMATION.md`](../Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md)
- [`Tests/Lab/performance-lab-matrix.json`](../Tests/Lab/performance-lab-matrix.json)

Die Testmatrix prüft Reproduzierbarkeit, Reset und Abbau. Sie ersetzt nicht die interaktive Szenarioauswahl, Benutzerübergabe und Schritt-für-Schritt-Anleitung.

## Verantwortungsgrenze

`SQL_PerformanceSchulung` verantwortet Lernziel, Topologieanforderung, Setup, synthetische Daten, Benutzeraktionen, Beobachtungsabfragen und fachlichen Reset.

`SQL_Server_Lab` wird für Provisionierung und Lifecycle der benötigten Infrastruktur verwendet. Dazu können Docker, Podman, Hyper-V und gemischte Topologien gehören.

Fehlt eine konkret benötigte Fähigkeit, wird die Lücke mit dem betroffenen Szenario dokumentiert. Änderungen in `SQL_Server_Lab` erfolgen erst nach ausdrücklicher Freigabe.

## Lokale Geheimnisse

Secrets, reale Hostnamen, Benutzerkonten, Pfade und interne Netzwerkdaten dürfen nicht eingecheckt werden. Beispielwerte müssen eindeutig synthetisch sein. Lokaler Lab-State und technische Runtime-Diagnosen bleiben außerhalb versionierter Projektpfade.
