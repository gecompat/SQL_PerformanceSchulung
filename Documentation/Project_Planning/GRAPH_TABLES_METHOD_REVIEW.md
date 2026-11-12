# Graph Tables: Quellen- und Methodenreview zu QRY-023

Stand: 12. November 2026
Status: statischer Entwurf und unabhängige Offline-Review durchgeführt;
Methodikgrundlage für statische Vertragsimplementierung durch `DEC-079`
freigegeben; formale Vertrags-/T-SQL-Abnahme und Ausführung bleiben offen

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

Die getrennte Planphase setzt für sqlcmd `SQLCMDMAXVARTYPEWIDTH` auf `0`, bevor
Actual-Plan-XML ausgegeben wird. Microsoft dokumentiert für `-y` den
Standardwert 256 Zeichen und dass XML bei Überschreitung abgeschnitten wird;
`0` hebt diese Begrenzung auf. Da unbegrenzte Ausgabe laut Hersteller bei
großen Resultaten Aufwand verursachen kann, ist die Maßnahme ausschließlich auf
die beiden `COUNT_BIG`-Diagnoseabfragen beschränkt und erzeugt keine Plan-Datei.
Quelle: [sqlcmd-Skriptvariablen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-use-scripting-variables?view=sql-server-ver17)
und [sqlcmd-Option `-y`](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17),
abgerufen am 12. November 2026. Der Skriptdirektivvertrag ist statisch gebunden;
das konkrete Toolverhalten bleibt Runtime zu qualifizieren.

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
- Die unabhängige Offline-Review vom 12. November 2026 prüfte Ergebnisoracle,
  Abfrageformen, Messreihen, Planabfragen und die statischen Harnessverträge.
  Sie fand zunächst offene Identitäts- sowie Ressourcen-/Abbruchgrenzen. Das
  Proposed-Manifest bindet diese Grenzen nun und markiert die technische
  Durchsetzung ausdrücklich offen; der gemeinsame FWK-010-Caller wurde dafür
  nicht verändert.
- Die Review der sqlcmd-Planbreite fand zusätzlich, dass der Validator eine
  spätere Überschreibung von `SQLCMDMAXVARTYPEWIDTH 0` nicht erkannte. Der
  Validator prüft nun den letzten Wert vor `STATISTICS XML ON`; die
  Negativregression `0` gefolgt von `256` wird abgewiesen. Eine unabhängige
  Nachprüfung bestätigte die Korrektur ohne neue P1/P2.
- `DEC-079` genehmigt diese Methodik als Grundlage der statischen
  Vertragsimplementierung; `DEC-080` akzeptiert die acht ausführbaren
  T-SQL-Dateien für ScriptDom-Syntax in 150/160/170. Keine Enginekompilierung,
  Harnessabnahme oder Ausführung folgt daraus. Ressourcen-, Identitäts-,
  Berechtigungs-, Cleanup-, Build-/Image- und Runtimegates bleiben offen.
- Der getrennte Offlineentwurf
  [QRY-023-Effektivrechtequalifikation](QRY023_EFFECTIVE_PERMISSION_DESIGN.md)
  konkretisiert phasenbezogene READER-Zugriffe und fail-closed Inventurregeln
  mit `sys.fn_my_permissions`. `DEC-083` begrenzt die zulässige
  `public`-Baseline auf eine isolierte QRY-023-Einzel-Run-Wegwerfinstanz. Der
  Effektivrechtevergleich, die tatsächliche Rollen-/SID-/Endpointinventur und
  jede SQL-Server-Qualifikation bleiben offen; die Entscheidung autorisiert
  weder Rechteänderungen noch eine Laufzeit.
- Ein weiterer statischer Follow-up sperrt SQLCMD-`GO`-Batchtrenner in READER-
  Skripten, damit ein optionaler Wiederholungswert keine unbeschränkt
  vervielfachte Mess-/Planabfrage erzeugt. Die Rohtextprüfung umfasst auch
  `GO` nach ein- und mehrzeiligen führenden T-SQL-Blockkommentaren; 76
  Regressionen und der QRY-023-Validator bestehen. Microsoft dokumentiert
  `GO [count]` als SQLCMD-Batchterminator, dessen Count die vorherige Batch
  wiederholt ([SQLCMD-Befehle](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-commands),
  abgerufen am 12. November 2026). Unabhängiger Nachreview schloss den P2 ohne
  weitere P1/P2; PR-Gates folgen. Der Laufzeit-Timeout bleibt eine getrennte
  Grenze.

## Quellen und Projektverträge

- `SRC-122` bis `SRC-127`: [Graph-Tables-Quellen](../Research/SOURCE_REGISTER.md#graph-tables--eng-begrenzte-sql-graph--und-compatibility-quellen); `SRC-158`: [Effektivrechte und SQL-Server-`public`-Baseline](../Research/SOURCE_REGISTER.md#qry-023--effektivrechte-und-sql-server-public-baseline).
- [Messworkload-Entwurf](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md).
- [Editions- und Buildreview](GRAPH_TABLES_BUILD_EDITION_REVIEW.md).
- [ScriptDom-Grammatikprüfung](GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md).
- `FWK-003`, `FWK-004`, `FWK-005`, `FWK-011` und `FWK-002`.
