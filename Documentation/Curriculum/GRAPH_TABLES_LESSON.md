# Graph Tables und gerichtete Pfade

SQL Graph ergänzt relationale Tabellen um zwei Rollen: Node-Tabellen speichern
Knoten, Edge-Tabellen speichern gerichtete Beziehungen zwischen Knoten. Die
Tabellen bleiben SQL-Server-Objekte; Graphsyntax stellt zusätzliche
Möglichkeiten bereit, Beziehungen als Muster auszudrücken.

Diese Notiz ergänzt `LO-M03-06`/`CLM-047`: einen Query-Rewrite als einzelne
Hypothese mit identischer Baseline und Vergleichsmessung beurteilen. Sie
erklärt die Modell- und Syntaxunterschiede. Der zugehörige
[QRY-023-Demoentwurf](../Project_Planning/GRAPH_TABLES_DEMO_CONCEPT.md) ist
weiterhin `PROPOSED`, nicht katalogisiert und ungefahren; die Notiz behauptet
keinen Performancevorteil.

## Knoten, Kanten und IDs

Eine Node-Tabelle bildet Entitäten ab, zum Beispiel Personen mit einer
Anwendungs-ID `PersonId`. Eine Edge-Tabelle bildet gerichtete Beziehungen ab,
etwa `Person A kennt Person B`. Graph-Tabellen besitzen intern erzeugte
Graph-IDs. Edge-Zeilen enthalten die Endpunkte `$from_id` und `$to_id`; diese
Werte referenzieren die internen Node-IDs.

Für fachliche Vergleiche und Ergebnistupel ist ein stabiler Anwendungsschlüssel
wie `PersonId` hilfreich. Er ist nicht gleichbedeutend mit `$node_id`. Die
internen IDs werden nicht hart codiert oder als fachliche Identität ausgegeben.
Bei relationalen Modellen stehen dieselben Beziehungen oft als Quell-/Ziel-
Spalten eines Kantentisches.

## Dasselbe Muster mit `MATCH` und Joins ausdrücken

Ein gerichteter Zwei-Kanten-Pfad lautet in Graphsyntax:

```sql
MATCH(p1-(e1)->p2-(e2)->p3)
```

Das Muster beschreibt eine Kante von `p1` nach `p2` und eine weitere von `p2`
nach `p3`. Die Edge-Aliase `e1` und `e2` müssen verschieden sein, auch wenn
beide dieselbe Edge-Tabelle bezeichnen. Start- und Zielbedingungen werden als
zusätzliche Prädikate verbunden. Richtung ist Teil der Abfrage; ein
umgedrehtes oder ungerichtetes Muster fragt etwas anderes.

Relational lässt sich dieselbe Form mit zwei Joins auf den Kantentisch
ausdrücken: erst Quelle und Ziel der ersten Kante verbinden, dann die zweite
Kante am Zwischenknoten anschließen. Beide Formen müssen dieselben
Anwendungs-IDs projizieren und dieselben Start-/Zielwerte verwenden.

Der Graphsyntaxreview bindet diesen `MATCH`-Pfad und die nötigen eindeutigen
Edge-Aliase. Er belegt weder Enginekompilierung noch Laufzeitsemantik für ein
konkretes Build. Vollständige SQL-Formen und das Edge-INSERT-Muster mit
`$node_id` stehen im [statischen QRY-023-Entwurf](../Project_Planning/GRAPH_TABLES_DEMO_CONCEPT.md)
und im [Syntaxreview](../Project_Planning/GRAPH_TABLES_TSQL_SYNTAX_REVIEW.md).

## Korrektheit vor Performance

Ein fairer Rewrite beantwortet dieselbe Frage auf demselben Datenbestand. Vor
dem Messen müssen Richtung, Pfadlänge, Duplikate, Ausgabeform und
Multiplizität feststehen. Beide Ergebnisrelationen werden mit einem
unabhängigen synthetischen Oracle verglichen. Ein bloßer `COUNT(*)` oder eine
Mengenprüfung, die Duplikate ignoriert, beweist keine identischen Ergebnistupel.

Graph- und relationale Varianten laufen trotzdem durch verschiedene
Abfrageformen. `MATCH` beweist keine bestimmte Planform oder Indexnutzung.
Wenn die Frage eine Performancehypothese einschließt, sind tatsächliche Pläne,
Logical Reads, CPU und Laufzeit für dasselbe Profil zu erfassen. Daten,
Compatibility Level, Indizes, Warm-up, Wiederholungen und Messmethode gehören
in den Vergleichsvertrag. Ein kleines Oracle prüft Korrektheit, ist aber kein
Messworkload; ein Messergebnis gilt nur für sein dokumentiertes Profil.

Ein Index auf `$from_id` und `$to_id` ist eine dokumentierte Empfehlung für
OLTP-Richtungssuchen. Das begründet eine prüfbare Kandidatenstruktur, nicht
ihre Nutzung oder einen Vorteil für jede Graphabfrage. Planbelege und Messung
entscheiden für den konkreten Query und Datensatz.

## Version und Einsatzgrenzen

SQL Graph ist laut Produktdokumentation ab SQL Server 2017 verfügbar; die
Schulung betrachtet die Projektprofile 2019, 2022 und 2025. Diese
Versionsmatrix und die Editionsmatrix ersetzen keine Prüfung von Zielbuild,
Compatibility Level oder ausführbarer SQL-Syntax. Eine vorhandene
`MATCH`-Abfrage ist kein Beleg, dass ein relationales Modell für dieselbe
Beziehung unpassend ist.

Graph Tables können ein Beziehungsmodell direkt ausdrücken. Ein relationaler
Kantentisch kann für dieselbe Aufgabe ebenso geeignet sein. Die Wahl richtet
sich nach fachlichem Modell, erforderlichen Abfragen, bestehenden Daten und
qualifizierten Ergebnissen, nicht nach einem pauschalen Performanceurteil.

## Quellen

Die Produktquellen sind im [Projektquellenregister](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen)
unter `SRC-122` bis `SRC-124` geführt:

- [CREATE TABLE (SQL Graph)](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-sql-graph?view=sql-server-ver17)
- [SQL Graph Architecture](https://learn.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-architecture?view=sql-server-ver17)
- [MATCH (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/queries/match-sql-graph?view=sql-server-2017)

Die Projektquellenprüfung und der [Syntaxreview](../Project_Planning/GRAPH_TABLES_TSQL_SYNTAX_REVIEW.md)
trennen dokumentierte Produktregeln von nicht ausgeführtem Demoentwurf und
Runtimequalifikation.
