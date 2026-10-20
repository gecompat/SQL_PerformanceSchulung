# Projektkontext

## Zweck

Aufbau einer modularen SQL-Server-Performance-Schulung, die technische Zusammenhänge für Einsteiger nachvollziehbar erklärt und zugleich für erfahrene Datenbankfachleute belastbar bleibt.

Das Projekt bereitet Schulungsthemen auf. Es baut kein Lab für ein SQL-Server-Analyseframework auf.

## Zielgruppe

- Einsteiger mit T-SQL-Grundkenntnissen
- Datenbankentwickler
- Datenbankadministratoren
- Performance Engineers

Jede Lerneinheit beginnt verständlich, führt aber bis zur technischen Evidenz über Execution Plans, DMVs, Query Store, Extended Events oder Betriebssystemmetriken.

## Plattformen

| Plattform | Rolle |
|---|---|
| SQL Server 2019 | Mindestversion und Kompatibilitätsprüfung |
| SQL Server 2022 | Zwischenversion mit PSP, CE Feedback und weiteren IQP-Funktionen |
| SQL Server 2025 | Primäre Entwicklungs- und Demonstrationsplattform |

Edition, Betriebssystem, Compatibility Level und Feature-Voraussetzungen sind pro Demo anzugeben.

## Inhaltliche Achsen

- Storage, Pages und Transaktionslog
- Optimizer, Statistiken und Execution Plans
- Query Patterns und typische Performancefallen
- Rowstore- und Columnstore-Indizes
- Concurrency, Isolation und TempDB
- CPU, Memory, I/O, Scheduler und Waits
- Query Store, Extended Events und Diagnosemethodik
- reproduzierbare Testumgebung als unterstützende Ausführungsbasis

## Umsetzungspriorität

1. Schulungsaussage und Lernziel fachlich aufbereiten.
2. Effekt möglichst mit T-SQL und einer isolierten synthetischen Testdatenbank demonstrieren.
3. Zusätzliche Infrastruktur nur verwenden, wenn der Effekt sonst nicht glaubwürdig oder sicher reproduzierbar ist.
4. Für Personen ohne verfügbaren SQL Server ein kompaktes How-to zur Bereitstellung einer Testumgebung anbieten.

## Didaktik

Die Schulung vermittelt technische Zusammenhänge, bewährte Lösungsmuster,
SQL-Techniken, Entwurfsentscheidungen und praktische Diagnose. Erklärungen,
Faustregeln mit benannten Grenzen und kurze Beispiele besitzen auch ohne
eigenen Benchmark didaktischen Wert. Eine fehlende Messung ist kein allgemeines
Ausschlusskriterium für Schulungsinhalte.

Die Begründung passt zur Aussage: dokumentiertes Produktverhalten und
nachvollziehbare Herleitungen tragen qualitative Erklärungen; konkrete
Messwerte und behauptete Leistungsgewinne brauchen einen passenden Nachweis
mit seinen Bedingungen. Messdemos verbinden Ursache, technische Erklärung,
Beobachtung und Vergleich. Hardware, Datenmenge, Edition und Version begrenzen
die Übertragbarkeit ihrer Ergebnisse.

## Sprache

Projekt- und Schulungssprache ist Deutsch. Etablierte englische SQL-Server-Fachbegriffe bleiben erhalten.
