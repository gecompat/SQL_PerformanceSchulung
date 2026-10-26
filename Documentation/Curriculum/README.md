# Themen und Lernwege

Die Schulung verbindet verständliche Grundlagen mit praktischen
Entscheidungen beim Schreiben, Analysieren und Verbessern von SQL-Code.
Grundkenntnisse in `SELECT`, `JOIN`, Filtern und Aggregationen helfen beim Einstieg.

## Einen Lernweg wählen

| Lernweg | Für wen? | Schwerpunkt |
|---|---|---|
| BASIS | Einstieg in SQL-Server-Performance | Abfragen und Pläne lesen, Statistiken und Zugriffspfade verstehen, erste typische Probleme erkennen |
| STANDARD | Entwickler und Administratoren mit Praxiserfahrung | Query Patterns, Indizes, Parameter, Blocking und die wichtigsten Diagnosewerkzeuge |
| VERTIEFUNG | Fortgeschrittene und Performance Engineers | komplexere Plan- und Ressourcenfragen, versionsabhängiges Verhalten und die Grenzen von Diagnose und Optimierung |

Die zugehörigen [Präsentationen](../../Presentations/README.md) und die
[Variantenanleitung](../HowTo/PRESENTATION_VARIANTS.md) helfen bei der Auswahl
des passenden Umfangs.

## Fachliche Themen

- Speicher, Pages und Transaktionslog
- Optimizer, Statistiken und Ausführungspläne
- Query Patterns und nützliche SQL-Lösungsmuster
- Rowstore- und Columnstore-Indizes
- Concurrency, Isolation und TempDB
- CPU (Central Processing Unit; Prozessor), Speicher, I/O (Input/Output; Ein- und Ausgabezugriffe) und Waits
- Query Store, Extended Events und Diagnose

Sie können die Themen der Reihe nach bearbeiten oder ein konkretes Problem
als Einstieg wählen. Kurze Erklärungen und SQL-Techniken ergänzen die
ausführlichen Messdemos; ein eigener Benchmark ist keine Voraussetzung für
ihren didaktischen Wert.

### Kurze technische Erläuterungen

- [Datentypen und implizite Konvertierung](IMPLICIT_CONVERSION_LESSON.md): passende Parameter, Konvertierungsfehler und Collation.
- [Halboffene Datumsintervalle](HALF_OPEN_DATE_INTERVAL_LESSON.md): inklusive `BETWEEN`-Grenzen und Datentypgenauigkeit.
- [Konkurrierende Abfragespeicherzuteilungen](COMPETING_MEMORY_GRANTS_LESSON.md): aktuelle Grant-Zustände und der Nachweis eines wartenden eigenen Requests.

Diese Notizen ergänzen bestehende Lernziele. Sie sind Erklärungen mit
synthetischen oder rein lesenden Beispielen, keine neuen freigegebenen Demos
oder Laufzeitqualifikationen. Für tatsächlich freigegebene Ausführungen gelten
der jeweilige Demo-Katalogeintrag und der zentrale Ausführungsleitfaden.

## Praktisch weiterarbeiten

Beginnen Sie mit einer [erklärten Fachdemonstration](../HowTo/DEMO_WALKTHROUGHS.md).
Für die eigene Ausführung beschreibt der
[Leitfaden](../HowTo/DEMO_EXECUTION_GUIDE.md) Voraussetzungen, Schritte und Cleanup.

Ein ergänzender [Kurs zu KI mit SQL Server 2025](../../Presentations/AI_SQL_Server_2025/README.md)
behandelt Vektoren, Suche und weitere Anwendungsmuster.

## Für die Unterrichtsplanung

Die [Curriculumarchitektur](CURRICULUM_ARCHITECTURE.md) enthält die detaillierten
Lernziele; die [Traceability-Matrix](TRACEABILITY_MATRIX.md) ordnet sie den
Lehrartefakten zu. Der
[Generalprobenplan](../Project_Planning/PRS_010_REHEARSAL_PLAN.md) bietet Aufgaben
und Musterantworten für eine moderierte Durchführung.
