# Graph Tables: statischer Demoentwurf

Stand: 7. November 2026  
Status: `PROPOSED`; Entwurf ohne Demo-ID, Implementierung oder Ausführung

## Lernziel und Umfang

Der Entwurf konkretisiert `LO-M03-06` und `CLM-047`: eine einzelne Abfrageform
als Hypothese mit identischer Baseline und Vergleichsmessung beurteilen. Die
Lernfrage lautet: Wie lässt sich derselbe feste Zwei-Kanten-Pfad mit Graph-
Tabellen und `MATCH` beziehungsweise mit einem relationalen Kantentisch und
Joins ausdrücken?

Die Kernabnahme ist semantisch: beide Varianten liefern für dieselben
synthetischen gerichteten Kanten genau dieselben Pfadtripel. Ein Laufzeit- oder
Leistungsgewinner ist nicht Teil der Aussage. `LO-M02-04` und `LO-M04-04`
werden nur dann ergänzt, wenn eine spätere Erweiterung physische
Joinentscheidungen oder Indexkosten ausdrücklich zum Lernziel macht.

## Synthetisches Modell und Ergebnisoracle

Ein kleiner, deterministischer Graph enthält fünf Personen mit IDs 1 bis 5 und
vier gerichtete Freundschaftskanten:

| Von | Nach |
|---:|---:|
| 1 | 2 |
| 2 | 5 |
| 1 | 3 |
| 3 | 5 |

Die Abfrage sucht alle Pfade mit genau zwei Kanten von Person 1 zu Person 5 und
gibt Start-, Zwischen- und Ziel-ID aus. Das erwartete Ergebnis besteht exakt
aus `(1, 2, 5)` und `(1, 3, 5)`. Der relationale Kantentisch hält dieselben
vier gerichteten Paare; die Graphtabellen modellieren dieselben Knoten und
Kanten. Keine realen Namen oder Daten werden benötigt.

Die spätere statische Ergebnisprüfung soll beide Ergebnisrelationen gegen
dieselbe erwartete Zweizeilenmenge prüfen. Vorher müssen Sortierung,
Duplikatbehandlung, Richtung und Ergebnisform explizit fixiert sein. Eine
Mengenprüfung allein reicht nicht, falls mehrere identische Pfadzeilen möglich
werden; deshalb enthält das festgelegte Fixture keine doppelten Kanten und
keine mehrfachen gleichartigen Pfade.

## Abfrageformen

Der quellengeprüfte [T-SQL-Schnitt](GRAPH_TABLES_TSQL_SYNTAX_REVIEW.md)
verwendet für die Graphvariante `p1-(e1)->p2-(e2)->p3`; `e1` und `e2` sind
verschiedene Aliase derselben Edge-Tabelle. Die relationale Variante joint den
Kantentisch zweimal über Quell- und Ziel-ID mit derselben Knotentabelle. Beide
verwenden dieselben Start-/Zielparameter und projizieren dieselben drei IDs.
Edge-Datensätze werden über `$node_id` der synthetischen Endknoten erzeugt;
interne oder hart codierte Graph-IDs kommen nicht zum Einsatz.

Die geplanten Abfrageformen lauten:

```sql
-- Graphvariante
SELECT p1.PersonId AS StartId, p2.PersonId AS MiddleId, p3.PersonId AS EndId
FROM dbo.Person AS p1, dbo.FriendOf AS e1, dbo.Person AS p2,
     dbo.FriendOf AS e2, dbo.Person AS p3
WHERE MATCH(p1-(e1)->p2-(e2)->p3)
  AND p1.PersonId = @StartPersonId
  AND p3.PersonId = @TargetPersonId;
```

```sql
-- Relationale Variante
SELECT p1.PersonId AS StartId, p2.PersonId AS MiddleId, p3.PersonId AS EndId
FROM dbo.RelPerson AS p1
JOIN dbo.RelFriend AS e1 ON e1.FromPersonId = p1.PersonId
JOIN dbo.RelPerson AS p2 ON p2.PersonId = e1.ToPersonId
JOIN dbo.RelFriend AS e2 ON e2.FromPersonId = p2.PersonId
JOIN dbo.RelPerson AS p3 ON p3.PersonId = e2.ToPersonId
WHERE p1.PersonId = @StartPersonId
  AND p3.PersonId = @TargetPersonId;
```

Die vier Graphkanten werden nach Einfügen der Personenknoten durch je einen
`INSERT` in `dbo.FriendOf` aufgebaut. `$from_id` und `$to_id` beziehen ihre
Werte aus skalaren Unterabfragen auf `dbo.Person.$node_id`, anhand des
synthetischen `PersonId`. Setupskripte und konkrete Inserts entstehen erst
nach Registrierung und vollständigem Demo-Vertrag.

## Beobachtung und zulässige Aussagen

Die Korrektheitsabnahme vergleicht beide Ergebnismengen mit dem festgelegten
Zweizeilenoracle. Der später separat freigegebene Vergleich erfasst zusätzlich
die tatsächlichen Execution Plans und geschätzten Kardinalitäten, Logical
Reads, CPU und Duration beider Formen. Die Bedingungen werden vorab festgelegt
und soweit die jeweiligen Funktionen es erlauben gleich gehalten: Enginebuild,
Compatibility Level, Parameter, Daten, Indizes, Warm-up, Wiederholungen und
Messverfahren. Unvermeidliche Unterschiede in Planform oder Indexierung werden
als Teil der verglichenen Varianten beschrieben und nicht als isolierter
Syntaxeffekt ausgegeben.

Keine Laufzeit, Planform, Kardinalitätsschätzung oder Performancewirkung wird
vor dieser Ausführung behauptet. Gleiche Ergebnisse belegen keine gleiche
Arbeit; ein einzelner Messlauf begründet keine allgemeine Empfehlung.

## Lifecycle, Sicherheit und offene Gates

Ein späteres ausführbares Paket muss die stabil registrierte Demo-ID und den
vollständigen Demo-Vertrag ergänzen. Der isolierte, synthetische Aufbau folgt
dem vorhandenen Framework für markierte Testdatenbanken; Setup und Cleanup
müssen wiederholbar sein und Cleanup darf nur exakt markierte, eigene Objekte
entfernen. Vor Aufnahme in den Demo-Katalog sind Sicherheitsstufe,
Rechte, Ressourcenprofil, Version, Compatibility Level, Edition,
Zielbuilds und erwartete `PASS`-/`SKIP`-Grenzen festzulegen.

Der nächste fachliche Schritt ist, die konkrete `MATCH`- und Join-Syntax gegen
die passenden Microsoft-T-SQL-Referenzen abzugleichen und die registrierte
Demo-Identität erst nach bestätigter Umfangszuordnung anzulegen. Danach folgen
unabhängige Methoden- und Quellenprüfung sowie die statische Vertragsprüfung.
SQL-/Lab-Ausführung und Runtimequalifikation bleiben eigene spätere Gates und
sind durch diesen Entwurf nicht autorisiert.
