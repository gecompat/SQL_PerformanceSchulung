# SQL Server Performance Schulung

Schulungsunterlagen, SQL-Beispiele und praktische Übungen zum Verstehen,
Analysieren und Verbessern von Microsoft-SQL-Server-Anwendungen.

Die Schulung richtet sich an Entwickler, Datenbankadministratoren und
Analysten mit Grundkenntnissen in Transact-SQL (T-SQL), dem SQL-Server-Dialekt
der Abfragesprache SQL. Sie verbindet technische Erklärungen mit
bewährten Lösungsmustern und nachvollziehbaren Demonstrationen. Sie können
die Unterlagen zum Selbststudium, zur Vorbereitung einer Schulung oder zum
gezielten Nachschlagen verwenden.

## Hier einsteigen

| Ich möchte … | Einstieg |
|---|---|
| die Schulungsfolien ansehen | [Präsentationen und Lernumfang](Presentations/README.md) |
| einen passenden Lernweg wählen | [Themen und Lernwege](Documentation/Curriculum/README.md) |
| ein SQL-Beispiel Schritt für Schritt verstehen | [Erklärungen zu den Fachdemos](Documentation/HowTo/DEMO_WALKTHROUGHS.md) |
| eine Demo selbst ausführen | [Ausführungsleitfaden](Documentation/HowTo/DEMO_EXECUTION_GUIDE.md) und [Demo-Auswahl](Documentation/Demo_Catalog/README.md) |
| eine Übungsumgebung vorbereiten | [Vorhandene SQL-Server-Instanz verwenden](Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md) oder [Container einrichten](Documentation/HowTo/CONTAINER_QUICKSTART.md) |
| einen Fachbegriff oder ein Kürzel nachschlagen | [Glossar mit kurzen Erklärungen](Documentation/GLOSSARY.md) |
| eine Anleitung oder Vertiefung finden | [Dokumentationsübersicht](Documentation/README.md) |

Zum ersten Kennenlernen benötigen Sie keine laufende SQL-Server-Instanz.
Lesen Sie die Folien und die Erklärungen zu den Beispielen. Für eigene
Ausführungen führen die Anleitungen durch Vorbereitung, Ablauf und Aufräumen.

## Was Sie hier lernen

- Abfragen, Ausführungspläne und Statistiken verstehen.
- Passende Query Patterns und Indexstrukturen für ein konkretes Problem wählen.
- Speicher, Pages, Transaktionslog und Columnstore einordnen.
- Blocking, Isolation, Deadlocks und TempDB untersuchen.
- Prozessorverbrauch (CPU), Speicher und Ein-/Ausgabezugriffe (I/O) sowie Wartezeiten richtig interpretieren.
- Query Store, Extended Events und weitere Diagnosewerkzeuge einsetzen.
- Änderungen mit ihren Voraussetzungen, Vorteilen und Grenzen beurteilen.

Ein ergänzendes [Kursangebot zu künstlicher Intelligenz (KI) mit SQL Server 2025](Presentations/AI_SQL_Server_2025/README.md)
behandelt unter anderem Vektoren, Suche und den Umgang mit SQL-Ausgaben von
Sprachmodellen.

## Beispiele und Leistungsangaben

Zum Lehrmaterial gehören auch kurze SQL-Techniken, Lösungsmuster und
erklärende Beispiele. Ihr Nutzen hängt nicht davon ab, ob ein eigener
Vorher-/Nachher-Benchmark vorliegt. Entscheidend ist, welches Problem sie
lösen, wann sie passen und welche Einschränkungen sie haben.

Messdemos zeigen zusätzlich, wie sich eine Wirkung unter bestimmten
Bedingungen untersuchen lässt. Konkrete Messwerte gelten für die jeweils
beschriebene Umgebung und sind keine allgemeingültigen Leistungsversprechen.

Historische Beispiele sind im [Referenzarchiv](Presentations/old/Performance%20Grundlagen%20V-2024.zip)
erhalten. Die [Einordnung der Altbeispiele](Documentation/Inventories/LEGACY_EXAMPLE_CLASSIFICATION.md)
erklärt ihre weitere Verwendung und die Bedeutung der damaligen Migrationsentscheidungen.

## Voraussetzungen für die Praxis

Die Unterlagen behandeln SQL Server 2019, 2022 und 2025. Welche Version,
Edition, Konfiguration und Rechte ein Beispiel benötigt, steht bei der
jeweiligen Demo. Zusätzliche Voraussetzungen für SQL Server 2025 werden
gesondert beschrieben.

Verwenden Sie für die Übungen eine geeignete Testumgebung mit synthetischen
Daten. Lesen Sie vor dem Start die jeweilige Anleitung. Beispiele mit
Last, Konfigurationsänderungen oder Cacheeingriffen benötigen eine dafür
vorgesehene isolierte Umgebung.

## Mitwirken und Lizenz

Hinweise zu fachlichen Korrekturen und Beiträgen stehen in
[Mitwirken](CONTRIBUTING.md). Interne Entwicklungsplanung ist über die
[Projektpflege](Documentation/README.md#projektpflege) erreichbar.

Für Nutzung und Weitergabe gilt [LICENCE.md](LICENCE.md).
