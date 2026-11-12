# External Tables und Remote Pushdown

External Tables stellen SQL-Server-Metadaten bereit, mit denen Abfragen auf
Daten außerhalb der lokalen Datenbank zugreifen. Sie vermeiden eine lokale
Datenkopie als Voraussetzung für jede Abfrage, verschieben aber weder
automatisch alle Arbeit zur Quelle noch beseitigen sie Netzwerk-, Quell- oder
Data-Movement-Kosten.

Diese Notiz ergänzt das Lernziel `LO-M03-05`: Remote Pushdown anhand des
tatsächlichen Datenwegs und Plans beurteilen. Sie ist erklärender Lerninhalt;
es gibt dafür keine katalogisierte External-Tables-Demo und keinen
Runtime-Nachweis. Der zugehörige [statische Entwurf](../Project_Planning/EXTERNAL_TABLES_DEMO_CONCEPT.md)
und der [Quellenreview](../Project_Planning/EXTERNAL_TABLES_SOURCE_REVIEW.md)
halten die offenen Infrastruktur- und Qualifikationsgates fest.

## Was sich ändert

Eine lokale Tabelle speichert ihre Zeilen in der SQL-Server-Datenbank. Eine
External Table beschreibt dagegen die Zuordnung zu Daten an einer externen
Quelle. Die Datenquelle, ein bei geschützten Quellen erforderliches Credential
und die externe Tabellendefinition bilden zusammen den Zugriffspfad.
`OPENROWSET(BULK ...)` ist ein separater Dateizugriffsweg und nicht dasselbe
wie eine persistente External Table.
Quelltyp, Connector, Betriebssystem und SQL-Server-Version bestimmen, welcher
Weg verfügbar ist.

Der SQL-Server-Connector `sqlserver://` ist der gemeinsame Kandidat für eine
Quelle auf einem relationalen Datenbankverwaltungssystem (RDBMS; relational
database management system) bei SQL Server 2019, 2022 und 2025. Für eine
gemeinsame 2019/2022/2025-Matrix ist
Windows der dokumentierte gemeinsame Betriebssystempfad; der
RDBMS-Connector unter Linux ist in der Produktmatrix ab SQL Server 2025
aufgeführt. Eine SQL-Server-2022-PolyBase-Installation unter Linux benötigt
zusätzlich Trace Flag 13702 beim Start; diese Installationsvoraussetzung
beweist für sich allein keine RDBMS-Connectorverfügbarkeit.

## Wann Pushdown stattfindet

SQL Server kann geeignete Filter, Projektionen, Joins oder Aggregationen an
die externe Quelle senden. Ob das gelingt, hängt vom Connector, vom konkreten
Ausdruck und vom Optimierer ab. Eine External Table oder `PUSHDOWN = ON`
allein belegt keine Remoteausführung. Funktionen oder bestimmte
Prädikatformen können die Auslagerung verhindern.

Die sinnvolle Frage lautet nicht nur „Gibt es Pushdown?“, sondern:

1. Welche Arbeit wurde an die Quelle übergeben?
2. Welche Zeilen und Spalten kamen tatsächlich zurück?
3. Welche Arbeit erledigten der lokale Optimierer und der
   Data Movement Service (DMS; Datenbewegungsdienst)?
4. Welche zusätzlichen Anforderungen entstanden durch Netzwerk, Quelle,
   lokale Verarbeitung und Statistiken?

Der geschätzte Plan kann zusammen mit Trace Flag 6408 die geplante
Remoteabfrage sichtbar machen. `sys.dm_exec_external_work.read_command` kann
für einen laufenden Request zusätzliche Remote-Query-Evidenz liefern. Der
Wert kann jedoch begrenzt oder für bestimmte Connectorarten `NULL` sein; die
Beobachtung muss deshalb an denselben Request gebunden sein. Eine fehlende,
abgeschnittene oder nicht korrelierbare Ausgabe ist kein Pushdown-Nachweis.

`sys.dm_exec_dms_workers` stellt unter anderem `bytes_processed`, Zeit- und
CPU-Felder bereit. Diese Werte sind ergänzende DMS-Evidenz, aber ohne
Profilqualifikation keine vollständige Messung aller übertragenen
Netzwerkbytes. Plan, Remote-Query, DMS-Zähler und Ergebnisdaten beantworten
unterschiedliche Fragen.

## Statistiken und Messwerte

Statistiken beeinflussen Schätzungen und damit die Planwahl. Das Erstellen
externer Statistiken kann Daten von der Quelle importieren; SQL Server kann
beim Sortieren gesampelter Werte außerdem TempDB verwenden. Diese Effekte
sind möglich und profilabhängig, keine garantierte Folge jedes Aufbaus.
Ab SQL Server 2022 können fehlende Statistiken automatisch und synchron
entstehen. Statistikzustand und Statistikaufbau gehören daher in den
Versuchsvertrag und müssen von den eigentlichen Abfrageläufen getrennt
werden.

Ein Laufzeitvergleich benötigt dieselbe synthetische Datenmenge, dieselben
Ergebnistupel, Parameter und Filter sowie dokumentiertes Warm-up und
Wiederholungen. Eine lokale materialisierte Kopie ist dabei eine andere
Architektur: Sie verlagert Speicher und Zugriff, entfernt Remoteverfügbarkeit
und Transport aus dem Abfragepfad und kann eine andere Aktualität haben. Sie
ist daher ein nützlicher Referenzweg, aber keine kausale Isolierung des
External-Table-Effekts. Aus einem einzelnen schnelleren Lauf folgt keine
allgemeine Empfehlung.

## Entscheidungshilfe

External Tables können passen, wenn Abfragen aktuelle, extern verwaltete
Daten ohne dauerhafte lokale Kopie benötigen und Connector, Rechte,
Erreichbarkeit, Verfügbarkeit sowie Quellkapazität kontrollierbar sind.
Eine lokale Kopie oder Materialisierung kann besser passen, wenn wiederholte
Abfragen, Verfügbarkeit bei Netzunterbrechung, lokale Indizes oder ein
definierter Aktualisierungsrhythmus wichtiger sind. Das sind abzuwägende
Architekturmerkmale, keine pauschalen Leistungsregeln.

Vor einem konkreten Einsatz sind mindestens Quelltyp und Connector,
Version/Betriebssystem, Authentifizierung, minimale Quellrechte,
Fehlerverhalten, Netzwerkgrenzen, erwartete Datenmenge und Cleanup zu prüfen.
Credentials gehören in einen geeigneten Secret-Speicher, nicht in SQL-Dateien
oder Repositorykonfiguration.

## Quellen

Die Herstellerbefunde sind im [Projektquellenregister](../Research/SOURCE_REGISTER.md#external-tables-und-polybase-2026-11)
unter `SRC-153` bis `SRC-157` geführt:

- [PolyBase Data Virtualization Guide](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/data-virtualization-guide?view=sql-server-ver17)
- [`CREATE EXTERNAL DATA SOURCE` und `CREATE EXTERNAL TABLE`](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-data-source-transact-sql?view=sql-server-ver17)
- [Pushdown in PolyBase](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-pushdown-computation?view=sql-server-ver17) und [Pushdown erkennen](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-how-to-tell-pushdown-computation?view=sql-server-ver17)
- [PolyBase-Performance](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-performance?view=sql-server-ver17), [`CREATE STATISTICS`](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-statistics-transact-sql?view=sql-server-ver17) und [`sys.dm_exec_dms_workers`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-dms-workers-transact-sql?view=sql-server-ver17)
- [PolyBase-Installation unter Linux](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-linux-setup?view=sql-server-ver17)

Die Erklärungen stützen sich auf Produktdokumentation. Sie ersetzen weder
Connector-/Buildqualifikation noch eine Messung im konkreten Zugriffspfad.
