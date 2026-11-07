# Graph Tables: Quellen- und Methodenreview zu QRY-023

Stand: 7. November 2026
Status: dokumentarisches Review; keine unabhängige Freigabe, Implementierung
oder Ausführung

## Graph-Query und Indexbegründung

Microsoft beschreibt `$from_id` und `$to_id` als gerichtete Endpunkte und
empfiehlt für OLTP-Richtungssuchen einen Index auf dem Paar. Die Graph-Query
verwendet `MATCH`; direkte Gleichheitsprädikate zwischen Graph-ID-Pseudo-Spalten
sind wegen der JSON-Darstellung nicht der vorgesehene Zugriffspfad. Der
Kandidatenindex auf dem Edge-Paar ist damit technisch begründet, aber seine
Eignung für genau diese nicht selektive vollständige Zwei-Hop-Abfrage bleibt
eine zu prüfende Designhypothese. Die Empfehlung belegt keinen erwarteten
Vorteil im Messprofil.

Graph- und relationale Knoten tragen denselben synthetischen `PersonId`-Wert.
Dieser fachliche Schlüssel dient dem Datenabgleich und dem Belegen der
Resultattripel. Er ist nicht mit der intern generierten Graph-ID gleichzusetzen.
Der eindeutige `PersonId`-Index bleibt eine explizite Kandidatenstruktur, deren
Nutzen im tatsächlichen Graph-Plan zu beurteilen ist; der Vertrag darf nicht
behaupten, dass `MATCH` ihn verwendet.

## Mess- und Planevidenz

`FWK-004` bleibt die Messautorität: dieselbe Session für Begin/Ende, registrierte
`WARMUP`-Phase, dieselben Daten und Ressourcen sowie Erfassung von CPU,
Logical Reads, Writes und verstrichener Zeit. Der Prozedur-/Messoverhead wird
mitgeführt und muss im Bericht benannt werden. Der relationale Ausdruck ist die
Baseline, der Graph-Ausdruck die Comparison; die Ausführungsreihenfolge wechselt
pro Paar AB/BA. Rohwerte je Wiederholung bleiben erhalten. Der robuste Vergleich
fasst fünf gepaarte Differenzen je Profil mit Median und ausgewiesener Streuung
zusammen; es gibt keine feste Leistungsgrenze.

Vollständige Tripelgleichheit, Eindeutigkeit und Sollanzahl werden vor den
Messwiederholungen geprüft. `COUNT_BIG(*)` ist ausschließlich das gemeinsame
Messstatement nach bestandener Vollpfadprüfung und wird nicht als Ersatz für
die fachliche Ergebnisgleichheit ausgegeben.

Actual-Plan-Evidenz ist ein getrennter Diagnosegang nach `FWK-005`. Dafür ist
`SHOWPLAN` auf allen referenzierten Datenbanken nötig und die Planerfassung kann
zusätzlichen Aufwand erzeugen. Planlauf und Messwiederholungen bleiben deshalb
getrennte Resultate: Planmetadaten erklären die beobachteten Varianten, sind
aber keine Einzelwiederholung der Messreihe. `STATISTICS IO/TIME` kann alternativ
Logical Reads, CPU und Elapsed ausgeben, verlangt laut Herstellerdokumentation
kein `SHOWPLAN`; ihre Nachrichten und Abgrenzung von Parse-/Compile-Zeit sind im
ausführbaren Vertrag explizit zu behandeln. `FWK-004`-Sessiondeltas bleiben die
vergleichende Messquelle.

Die ausführbaren T-SQL-Dateien bestehen außerdem die
[ScriptDom-Grammatikprüfung](GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md) für die
Parserprofile 150/160/170. Dieses Ergebnis schließt keine Kompilierung gegen
eine konkrete SQL-Engine und keine Objekt-, Berechtigungs- oder
Laufzeitqualifikation ein.

## Konsequenzen für die offene Arbeit

- Das bestehende 10.000-Pfade-Profil und beidseitige `EXCEPT`-Oracle bleiben als
  Vorschlag erhalten.
- Der ausführbare Querytext muss Graph-`MATCH` verwenden und darf nicht direkt
  `$node_id = $from_id` vergleichen.
- Der `$from_id`/`$to_id`-Index und die `PersonId`-Indizes sind zu dokumentierende
  Kandidaten; Indexnutzung wird nur aus den tatsächlichen Plänen behauptet.
- Rechte- und Messvertrag muss `SHOWPLAN` für Actual-Plan-Evidenz getrennt von
  den Berechtigungen für den Messlauf aufführen.
- Fünf Wiederholungspaare liefern kleine Stichproben. Median und Streuung sind
  beschreibend für das Profil; ein statistischer Signifikanz- oder
  Allgemeingültigkeitsclaim ist daraus nicht ableitbar.
- Eine unabhängige Methodenprüfung, formale Vertragsabnahme und sämtliche
  Ausführungsgates bleiben offen.

## Quellen und Projektverträge

- `SRC-122` bis `SRC-127`: [Projektquellenregister](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen).
- [Messworkload-Entwurf](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md).
- [Editions- und Buildreview](GRAPH_TABLES_BUILD_EDITION_REVIEW.md).
- [ScriptDom-Grammatikprüfung](GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md).
- `FWK-003`, `FWK-004`, `FWK-005`, `FWK-011` und `FWK-002`.
