# Graph Tables: Quellenprüfung SQL Server 2022 und 2025

Stand: 7. November 2026  
Status: begrenzter Releaseübersichten-Befund, keine Versionsqualifikation

## Prüffrage

Die bisherige [Graph-Table-Versions- und Indexprüfung](GRAPH_TABLES_VERSION_INDEX_REVIEW.md)
ließ offen, ob die Releaseübersichten von SQL Server 2022 und 2025 konkrete
Graph-Änderungen aufführen. Diese Prüfung untersucht ausschließlich diese
beiden Microsoft-Übersichten; sie ist keine vollständige Featurematrix.

## Befund

Die Microsoft-Übersicht zu SQL Server 2022 enthält keinen Eintrag mit dem
Begriff `Graph` oder `SQL Graph`. Auch die Microsoft-Übersicht zu SQL Server
2025 enthält keinen solchen Eintrag. Dieser negative Suchbefund bedeutet nur,
dass die geprüften Releaseübersichten keine Graph-spezifischen Änderungen
auflisten. Er beweist weder unverändertes Verhalten noch vollständige
Featureparität oder Unterstützung jeder Graphfunktion in jeder Edition und
jedem Compatibility Level.

Die allgemeine Graph-Übersicht und Architekturreferenz beschreiben SQL-Graph-
Grundfunktionen als ab SQL Server 2017 verfügbar und auf SQL Server 2017 und
später anwendbar. Zusammen mit der gesonderten Historie der Graph-Erweiterungen
in SQL Server 2019 ergibt sich eine vorläufige Planungsbasis: Graphtabellen und
`MATCH` können als versionsübergreifender Lehrgegenstand weiter entworfen
werden. Konkrete Funktionen, Editionen und Compatibility-Level-Voraussetzungen
müssen vor dem Demo-Vertrag separat an den passenden T-SQL-Referenzen und
Zielbuilds festgemacht werden.

Quellen, abgerufen am 7. November 2026:

- [What's New in SQL Server 2022](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2022?view=sql-server-ver16)
- [What's New in SQL Server 2025](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17)

## Entscheidung für die weitere Planung

Die Quellenprüfung reicht aus, um den reinen Entwurf eines Graph-vs-relational-
Lehrbeispiels fortzusetzen. Sie reicht nicht aus, um eine 2019/2022/2025-
Kompatibilitätsmatrix, ein konkretes Zielbuild-Set, Editionen, Compatibility
Levels, Graph-Indexvarianten oder Laufrechte zu bestätigen. Vor einem ausführ-
baren Vertrag bleiben die verwendeten Funktionen gegen versionierte
T-SQL-Referenzen zu prüfen. Ein Lauf benötigt weiterhin eigene Freigaben,
isolierte Daten und bestätigten Cleanup.
