# Graph Tables: Quellen- und Abdeckungsprüfung

Stand: 7. November 2026  
Status: `PROPOSED`; Quellen-/Curriculumprüfung, keine Demo- oder Laufzeitfreigabe

## Zweck und Befund

Diese Prüfung wählt einen möglichen nächsten Entwicklungsschnitt aus dem
Backlog zu Graph Tables und External Tables aus. Sie ordnet noch kein Lernziel,
keine Folie, Demo oder stabile Kennung zu und ändert keinen Implementierungs-
oder Qualifikationsstatus.

Die aktuelle Curriculum-Traceability-Matrix und die vorhandenen Kursinhalte
enthalten keine eigene Abdeckung zu Graph Tables, `MATCH` oder einem Vergleich
mit relationalen Kantenmodellen. Der Themenvorschlag passt fachlich zu
Welle 5 (Abfragen und Optimierung) sowie Welle 6 (Indizes); das ist eine
Planungseinordnung, keine bereits bestätigte Curriculum-Zuordnung.

## Curriculum-Zuordnung als Vorschlag

Als primärer vorhandener Lernzielanker eignet sich `LO-M03-06`: einen
Query-Rewrite als einzelne Hypothese mit identischer Baseline und
Vergleichsmessung durchführen. Das bereits vorhandene `CLM-047` (Query-Rewrite
über Plan und Messung prüfen) ist diesem Lernziel zugeordnet, aber noch keiner
Demo. Der Graph-gegen-relational-Vergleich könnte diese vorhandene Aussage
konkretisieren, wenn beide Varianten dieselbe Frage und Ergebnismenge besitzen
und die Baseline-/Messbedingungen vorab feststehen.

`LO-M02-04` und `LO-M04-04` sind keine Voraussetzung des Kernvorschlags. Sie
kommen nur als zusätzliche Anschlussziele infrage, falls der Demoentwurf
tatsächlich physische Joinentscheidungen beziehungsweise Indexkosten
untersucht. Vorläufiger Arbeitsowner ist die Curriculum-Fachredaktion; die
formale Zuordnung in der Traceability-Matrix bleibt bis zum abgeschlossenen
Demoentwurf `PROPOSED`. Ein neues Lernziel ist nach aktuellem Befund nicht
erforderlich.

## Quellenbefunde

Microsoft beschreibt SQL Graph als Fähigkeit ab SQL Server 2017. Graphdaten
werden in Node- und Edge-Tabellen modelliert; `MATCH` unterstützt
Musterabfragen und Navigation über mehrere Kanten. Dass Graphobjekte Tabellen
sind, erlaubt relationale Operationen, belegt aber keinen Performancevorteil
gegenüber einem relationalen Modell.

Das offizielle Microsoft-Beispiel zeigt synthetische Node-/Edge-Tabellen,
Einfügen von Beispieldaten, `MATCH`-Abfragen und einen Cleanup-Abschnitt. Es
kann als technische Ausgangsbasis für einen späteren isolierten T-SQL-Schnitt
dienen; sein Schema und seine Ausführung sind damit nicht für diese Schulung
qualifiziert.

Quellen, beide abgerufen am 7. November 2026:

- [Graph Processing – SQL Server and Azure SQL Database](https://learn.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-overview?view=sql-server-2017)
- [SQL Graph Database Sample – SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-sample)

Diese zwei Quellen decken den begrenzten Quellenkandidatenrahmen dieser Welle
ab. Sie schließen keine Detailprüfung zu Graph-Indizes, Editionen,
Compatibility Levels oder versionsspezifischen Ausnahmen ein.

## Vorgeschlagener Lehrschnitt

Als späteren Kandidaten empfiehlt sich ein fester Zwei-Kanten-Pfad über
synthetische Knoten und gerichtete Kanten. Dieselbe Fragestellung und
Ergebnismenge werden einmal mit Graphtabellen und `MATCH`, einmal mit einem
relationalen Kantentisch und Joins ausgedrückt. Vor einer Ausführung müssen
Modellsemantik, Duplikate, Richtung, Nullverhalten, Datenverteilung, Indizes,
Version und Compatibility Level festgelegt werden.

Das Lernziel wäre zunächst, Modellierung und Abfragesyntax passend zur
Beziehungsstruktur einzuordnen und die beiden Abfrageformen semantisch korrekt
zu vergleichen. Execution Plans, Cardinality Estimates, Logical Reads, CPU und
Duration sind mögliche Beobachtungsgrößen eines späteren qualifizierten
Versuchs. Ohne diesen Versuch wird weder ein Gleichstand noch eine
Performanceüberlegenheit behauptet.

## Reihenfolge, Sicherheit und offene Entscheidungen

Graph Tables sind als erster Kandidat vor External Tables empfohlen, weil ein
synthetischer Graph in einer lokalen Datenbank entworfen werden kann und dafür
nach bisheriger Quellenprüfung kein externer Connector oder Datendienst
erforderlich ist. Das ist eine begrenzte Planungsschlussfolgerung; die
konkrete Demo-Sicherheit ist erst mit ihrem Vertrag zu beurteilen.

Vor Umsetzung bleiben mindestens offen:

1. Curriculum-Owner und bestehendes Lernziel beziehungsweise begründetes neues
   Lernziel festlegen; Folien- und Traceability-Auswirkung bestimmen.
2. Die [gesonderte Versions- und Indexprüfung](GRAPH_TABLES_VERSION_INDEX_REVIEW.md)
   bindet Graph-Indexgrundlagen und dokumentierte Erweiterungen für SQL Server
   2019. Die geprüften [Releaseübersichten 2022/2025](GRAPH_TABLES_2022_2025_SOURCE_REVIEW.md)
   enthalten keine Graph-Einträge, was Versionsparität nicht beweist. Editions-
   und Compatibility-Level-Grenzen bleiben anhand passender T-SQL-Referenzen
   und Zielbuilds zu prüfen.
3. Einen Demo-Vertrag mit synthetischen Daten, isoliertem Setup, erwarteter
   Ausgabe, zulässiger Evidenz, Messbedingungen und unabhängig bestätigtem
   Cleanup erstellen.
4. Erst danach die erforderlichen Methoden-, Sicherheits-, Ausführungs- und
   Runtime-Gates für den konkreten Schnitt abarbeiten.

External Tables bleiben zurückgestellt, bis der konkrete Datenzugriffsweg,
Connector, Infrastrukturbedarf, unterstützte Versionsmatrix sowie deren
Sicherheits- und Cleanup-Vertrag geprüft sind. Diese Prüfung erteilt weder
Graph- noch External-Table-Laufrechte.
