# Graph Tables: Versions- und Indexprüfung

Stand: 7. November 2026  
Status: Planungsbefund, keine Implementierungs- oder Laufzeitfreigabe

## Quellenbasis und Befunde

Diese Ergänzung baut auf der [Quellen- und Abdeckungsprüfung](GRAPH_TABLES_SOURCE_COVERAGE_REVIEW.md)
auf und prüft zwei weitere Microsoft-Primärquellen. Sie qualifiziert weder ein
konkretes Schema noch eine SQL-Server-Matrix.

Die SQL-Graph-Architekturdokumentation beschreibt die Graphtabellen ab SQL
Server 2017. Für Node- und Edge-Tabellen werden eindeutige Indizes auf den
jeweiligen Graph-IDs empfohlen; ohne selbst angelegten Index erstellt SQL
Server einen eindeutigen nicht gruppierten Standardindex. Für OLTP-Zugriffe
empfiehlt Microsoft zusätzlich einen Index auf `($from_id, $to_id)`. Die Quelle
warnt davor, Graph-Pseudospalten in Prädikaten direkt miteinander zu
vergleichen, weil deren JSON-Darstellung Konvertierungen und Ineffizienz
verursachen kann; `MATCH` wird dafür als bevorzugter Abfrageweg genannt.

Die SQL-Server-2019-Änderungsübersicht nennt konkrete Graph-Erweiterungen:
`SHORTEST_PATH`, kaskadierende Löschaktionen für Edge Constraints,
Tabellen-/Indexpartitionierung und Aliasunterstützung in Graph-MATCH-Abfragen.
Diese zeitliche Abgrenzung zeigt, warum ein allgemeiner Graph-2017+-Hinweis
keine vollständige 2019/2022/2025-Kompatibilitätsmatrix ersetzt.

Quellen, abgerufen am 7. November 2026:

- [SQL Graph Architecture – SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-architecture?view=sql-server-ver17)
- [What's New in SQL Server 2019](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2019?view=sql-server-ver17)

## Konsequenz für den späteren Vergleich

Der vorgeschlagene Vergleich von `MATCH` und relationalen Joins muss
Indexbedingungen als Teil der Fragestellung offenlegen. Ein sinnvoller
Lernversuch kann zunächst den jeweils dokumentierten Basispfad beschreiben und
danach eine gesonderte, symmetrisch begründete Indexvariante prüfen. Graph-
Pseudospalten-Indizes, relationale Schlüssel-/Fremdschlüsselindizes und
Kantenrichtung dürfen nicht stillschweigend zwischen den Fällen variieren.
Auch eine passende Indexierung wäre kein Beleg für allgemeine Überlegenheit.

Für eine vorläufige Kompatibilitätsübersicht ist nur dies quellenbelegt:

- Graph-Grundfunktionen und Graphtabellen: SQL Server 2017 und höher.
- Die genannten Graph-Erweiterungen wurden für SQL Server 2019 dokumentiert.
- Die geprüften [Releaseübersichten für SQL Server 2022 und 2025](GRAPH_TABLES_2022_2025_SOURCE_REVIEW.md)
  enthalten keinen Graph-Eintrag. Das ist kein Beleg unveränderten Verhaltens
  und ersetzt keine versionierte Referenz oder Zielbuildprüfung. Edition und
  Compatibility Level bleiben ebenso offen; die geprüften Quellen belegen
  weder den vollständigen Featureumfang noch eine Performanceeigenschaft.

Vor einem Demo-Vertrag muss die Fachprüfung die tatsächlichen
SQL-Server-2019/2022/2025-Zielbuilds und alle verwendeten Funktionen gegen die
jeweilige Dokumentation binden. Für jede Ausführung müssen Compatibility Level,
Edition, Datenmodell, Indexdefinitionen und Cleanupbedingungen separat
feststehen. Kein SQL-Lauf ist durch diese Prüfung freigegeben.
