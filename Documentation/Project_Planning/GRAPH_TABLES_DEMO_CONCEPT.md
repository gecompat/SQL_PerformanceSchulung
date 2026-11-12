# Graph Tables: statischer Demoentwurf

Stand: 7. November 2026  
Status: `PROPOSED`; Methodik gemäß `DEC-079` freigegeben; registrierter Vertrag mit nicht validiertem Codeentwurf, noch nicht katalogisiert

## Lernziel und Umfang

Der Entwurf konkretisiert `LO-M03-06` und `CLM-047`: eine einzelne Abfrageform
als Hypothese mit identischer Baseline und Vergleichsmessung beurteilen. Die
Lernfrage lautet: Wie lässt sich derselbe feste Zwei-Kanten-Pfad mit Graph-
Tabellen und `MATCH` beziehungsweise mit einem relationalen Kantentisch und
Joins ausdrücken?

Die Abnahme verbindet semantische Korrektheit mit dem bestehenden Lernziel:
beide Varianten müssen dieselben synthetischen gerichteten Pfadtripel liefern;
Planbeobachtung und identische Baseline-/Vergleichsmessung sind verpflichtend,
weil `LO-M03-06` genau diese Methode fordert. Die Messung gilt nur für das
konkrete synthetische Profil und erklärt keinen allgemeinen Leistungsgewinner.
`LO-M02-04` und `LO-M04-04` werden nur dann ergänzt, wenn eine spätere
Erweiterung physische Joinentscheidungen oder Indexkosten ausdrücklich zum
Lernziel macht.

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

Die statische Ergebnisprüfung soll beide Ergebnisrelationen gegen
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

Die vier Graphkanten des Korrektheitsoracles werden nach Einfügen der
Personenknoten durch `INSERT` in `dbo.OracleFriendOf` aufgebaut. `$from_id` und
`$to_id` beziehen ihre Werte aus verbundenen `dbo.OraclePerson.$node_id`-Werten,
anhand der synthetischen `PersonId`. Ein initialer Codeentwurf liegt in
[`QRY-023_Graph_Tables`](../../Demos/05_Query_Patterns/QRY-023_Graph_Tables/README.md);
er ist nicht statisch abgenommen und nicht im allgemeinen Demo-Katalog.

## Beobachtung und zulässige Aussagen

Die Korrektheitsabnahme vergleicht beide Ergebnismengen mit dem festgelegten
Zweizeilenoracle. Die Messabnahme erfasst für beide Formen tatsächliche
Execution Plans und geschätzte Kardinalitäten, Logical Reads, CPU und Duration.
Enginebuild, Compatibility Level, Parameter, Daten, fachlich begründete
Indexierung, Warm-up, Wiederholungen und Messverfahren werden vorab festgelegt
und so weit wie möglich gleich gehalten. `FWK-004` bestimmt die dokumentierten
Wiederholungen, Warm-up-Ausschlüsse, robusten Lagewerte und Streuung; `FWK-005`
bindet Plan- und Statistikevidenz. Der kleine Fünf-Knoten-Vier-Kanten-Aufbau ist
ein Korrektheitsoracle und kein qualifiziertes Messworkload. Ein getrenntes
Design für 10.000 deterministische Zwei-Kanten-Pfade mit 30.000 Knoten und
20.000 Kanten steht im [Messworkload-Entwurf](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md); es ist weder implementiert noch ausgeführt.
Die [Quellen- und Methodenprüfung](GRAPH_TABLES_METHOD_REVIEW.md) grenzt
`MATCH`, Kandidatenindizes, Mess- und Actual-Plan-Erfassung sowie Rechte ab;
`DEC-079` gibt diese Methodik als Grundlage der statischen Vertragsimplementierung
frei.
Unvermeidliche Unterschiede in Planform oder Indexierung werden als Teil der
verglichenen Varianten beschrieben und nicht als isolierter Syntaxeffekt
ausgegeben.

Keine Laufzeit, Planform, Kardinalitätsschätzung oder Performancewirkung wird
vor dieser Ausführung behauptet. Gleiche Ergebnisse belegen keine gleiche
Arbeit; ein einzelner Messlauf begründet keine allgemeine Empfehlung.

## Lifecycle, Sicherheit und offene Gates

Die zentrale Registry führt den Schnitt als `QRY-023` unter `TSK-017`. Die
Zuordnung verwendet ausschließlich den bestehenden Lernzielanker `LO-M03-06`
und Claim `CLM-047`; es entsteht kein neues Lernziel. Im Demo-Katalog ist der
Status `PROPOSED` zu verwenden, bis eine Implementierung und die dafür
erforderlichen Qualifikationen tatsächlich vorliegen.

Der statische Vertrag für eine spätere Implementierung lautet:

| Bereich | Festlegung | Abnahmegrenze |
|---|---|---|
| Testdaten | Fünf synthetische Personen-IDs 1–5, vier gerichtete Kanten `(1,2)`, `(2,5)`, `(1,3)`, `(3,5)`; keine realen oder extern bezogenen Daten | Setup ist deterministisch und wiederholbar; Graph- und Relationsmodell enthalten dieselben logischen Paare |
| Ergebnis | Exakt die Tupel `(1,2,5)` und `(1,3,5)` in beiden Varianten, dieselben Spalten und Datentypen, aufsteigend sortiert nach Start-, Zwischen- und Ziel-ID | Beidseitiger Vergleich gegen dasselbe feste Oracle; fehlende, zusätzliche und doppelte Zeilen müssen als Fehler sichtbar werden |
| Abfragen | Gerichteter Zwei-Kanten-`MATCH` mit verschiedenen Edge-Aliasen; relationale Form mit zwei Kantentabellen-Joins; identische Start-/Zielparameter | Keine Behauptung, dass die Formen denselben Plan oder dieselbe Arbeit erzeugen |
| Isolation / Rechte | Nur eigene wegwerfbare markierte Testdatenbank; Setup benötigt DDL- und Insert-Rechte, Abfragephase nur Select, Cleanup die zum Entfernen der eigenen Objekte erforderlichen Rechte | Keine fremde Datenbank, kein gemeinsam genutzter Instanzzustand und keine Rechteausweitung für Lernende |
| Cleanup / Fehlerpfad | Setup markiert alle eigenen Tabellen und den Lauf; Cleanup entfernt ausschließlich nach erfolgreicher Eigentumsprüfung die eigenen Objekte; Teilausfall liefert den Zustand und einen sicheren Wiederaufnahmehinweis | Wiederholung nach Erfolg oder kontrolliertem Setupfehler darf fremde Objekte nicht verändern |
| Version / Skip | Vorgeschlagene Qualifikationsprofile sind SQL Server 2019/150 (`15.0.4500.2`), 2022/160 (`16.0.4305.5`) und 2025/170 (`17.0.5035.5`); Graph ist in den Microsoft-Editionsmatrizen für alle genannten Editionen verfügbar | Die Builds sind zeitgebundene Designpins vom 7.11.2026, keine Graph-Mindestbuilds oder Runtimefreigabe. Read-only Preflight und Setup prüfen die exakte Version; spätere CU/GDR-Stände enden zunächst mit `SKIP`. Image-Digests und tatsächliche Runtimeumgebung bleiben vor Lauf offen; siehe [Editions- und Buildreview](GRAPH_TABLES_BUILD_EDITION_REVIEW.md) |
| Ressourcen / Messung | Korrektheit und Baseline-/Vergleichsmessung sind verpflichtend. Separates vorgeschlagenes Messprofil: 10.000 disjunkte Pfade mit 30.000 Knoten und 20.000 Kanten; Plan, Estimated Rows, Logical Reads, CPU und Duration nach `FWK-004`/`FWK-005` | Kein allgemeiner Performancegewinner. Der [Messworkload-Entwurf](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md) bleibt vor Implementierung statisch zu prüfen; konkrete Builds, Ressourcenwerte und Messgrenzen folgen dem ausführbaren Vertrag |

Vor statischer Abnahme und Katalogintegration der Codeentwürfe bleiben formale
Vertrags-/T-SQL-Abnahme und Prüfung des vorgeschlagenen Messworkloads und Wiederholungsplans,
Bestätigung oder Erneuerung der zeitgebundenen Build-/CU-Pins und Prüfung der bestehenden
Frameworkmarker, Eigentums- und Cleanupkonventionen offen. SQL-/Lab-Ausführung,
Runtimequalifikation und Performanceclaims sind getrennte Gates und durch die
Registrierung nicht autorisiert.
