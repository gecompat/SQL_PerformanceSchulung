# Graph Tables: T-SQL-Syntaxprüfung

Stand: 12. November 2026
Status: quellengebundene Syntaxprüfung und statische ScriptDom-Akzeptanz gemäß `DEC-080`; keine Enginekompilierung oder Ausführung

## Quellen und konkrete Regeln

## Statische Parse-Abnahme (`DEC-080`)

Der gesperrte ScriptDom-Lauf bestand für die acht ausführbaren T-SQL-Dateien
unter den Grammatiken 150, 160 und 170. `15_Framework.sql` bleibt ein SQLCMD-
Wrapper; geprüft wird dort nur der festgelegte `:r`-Include. Die drei
SQLCMD-Platzhalter werden ausschließlich im flüchtigen Parsertext synthetisch
ersetzt. Das bestätigt Syntaxverträglichkeit mit diesen Parsergrammatiken,
nicht Enginekompilierung, Objektbindung, Rechte, Frameworkprozedurverträge,
Harnessabnahme oder Ausführbarkeit. `QRY-023` bleibt `PROPOSED`.

Die Microsoft-Referenz für `MATCH` beschreibt einfache gerichtete Muster in
`SELECT ... WHERE MATCH(...)`. Muster können mehrere Kanten enthalten, müssen
die Richtung aber ausdrücklich angeben. Ein Edge-Alias darf innerhalb eines
`MATCH`-Musters nicht wiederholt werden; deshalb benötigt der geplante
Zwei-Kanten-Pfad zwei Aliase (`e1`, `e2`), obwohl beide dieselbe Edge-Tabelle
bezeichnen. `MATCH`-Muster unterstützen kein `OR` oder `NOT`; zusätzliche
Start-/Zielprädikate werden mit `AND` verbunden.

Beim `INSERT` in eine Edge-Tabelle müssen `$from_id` und `$to_id` geliefert
werden. Die Microsoft-Referenz zeigt beide Werte als skalare Unterabfragen, die
`$node_id` der Endknoten aus der Knotentabelle lesen. INSERT- und SELECT-Rechte
gehören deshalb in den späteren Mindestberechtigungsvertrag.

Beide Referenzen nennen SQL Server 2017 und höher. Das qualifiziert die Syntax
für keinen einzelnen Projektbuild und belegt keine Edition, Compatibility
Level oder Runtimeeigenschaft.

Quellen, abgerufen am 7. November 2026:

- [MATCH (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/queries/match-sql-graph?view=sql-server-2017)
- [INSERT (SQL Graph)](https://learn.microsoft.com/en-us/sql/t-sql/statements/insert-sql-graph?view=sql-server-ver17)

## Konsequenz für den Entwurf

Die Graphabfrage soll `p1-(e1)->p2-(e2)->p3` verwenden und eindeutige Aliase
für beide Kanten aufnehmen. Edge-Aufbau muss `$node_id` aus den synthetischen
Knotenzeilen referenzieren; hart codierte JSON- oder interne Graph-ID-Werte
sind ausgeschlossen. Die relationale Abfrage verwendet zwei getrennte
Kantentischaliase und dieselbe gerichtete Pfadform.

Vor einer Implementierung ist die konkrete T-SQL-Ausgabe statisch gegen diese
Referenzen und die gewählten Zielversionen zu prüfen. Es erfolgten keine
SQL-Aufrufe.
