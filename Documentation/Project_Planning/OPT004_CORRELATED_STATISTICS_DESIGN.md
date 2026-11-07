# OPT-004 – Entwurf für korrelierte Spaltenstatistiken

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `OPT-004` – Einzel- und Mehrspaltenstatistiken bei korrelierten Spalten |
| Quellen | `SRC-005`, `SRC-143` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Grenze

Der Entwurf vergleicht gleiche korrelierte Daten in zwei Heaps: einen mit
expliziten Einzelspaltenstatistiken auf `A` und `B` und einen mit denselben
Statistiken plus einer Mehrspaltenstatistik auf `(A, B)`. Er trennt das
vollständige fachliche Ergebnis von Statistikmetadaten und der späteren
Kardinalitätsschätzung im Ausführungsplan.

SQL Server dokumentiert ein Histogramm nur für die erste Spalte eines
Statistikobjekts. Mehrspaltenstatistiken enthalten Dichtewerte für Spalten-
präfixe. Diese Produktsemantik sagt nicht voraus, welche Statistik ein
konkreter Optimierer für eine Abfrage verwendet, welchen Schätzwert er erzeugt
oder welchen Plan er wählt. Die berechneten Referenzwerte unten sind daher
keine Schätzwert- oder Planassertion.

Dieser Schnitt behandelt ausschließlich Spaltenkorrelation und
Mehrspaltenstatistiken. Trusted-/Untrusted-Constraints, Eindeutigkeit und die
weitere Constraint-Gegenprobe aus dem vollständigen OPT-004-Themenumfang
bleiben separat offen.

## Synthetisches Datenprofil

Jede der zwei eigenständigen Heapkopien enthält identische 10.000 Zeilen:

- `RowId`: Ganzzahl von 1 bis 10.000, durch die Fixture eindeutig, aber ohne
  Primary-Key-Constraint oder Index;
- `A`: `(RowId - 1) % 100`, also 100 mögliche Werte mit je 100 Zeilen;
- `B`: `A % 5`, also fünf Werte mit je 2.000 Zeilen.

Es gibt genau 100 beobachtete `(A, B)`-Kombinationen; jede kommt 100-mal vor.
`B` ist vollständig durch `A` bestimmt. Die Tabellen haben keine Indizes,
Constraints, NULL-Werte, Filterstatistiken oder zusätzlichen fachlichen
Spalten.

| Merkmal | Sollverteilung |
|---|---:|
| Zeilen gesamt | 10.000 |
| Distinct `A` | 100; je 100 Zeilen |
| Distinct `B` | 5; je 2.000 Zeilen |
| Distinct `(A, B)` | 100; je 100 Zeilen |
| Treffer `A = 7 AND B = 2` | 100 Zeilen |
| Treffer `A = 7 AND B = 3` | 0 Zeilen |

Das vollständige Tupeloracle für `A = 7 AND B = 2` sind genau die 100 Zeilen,
deren `RowId` mit 8 beginnt und danach in 100er-Schritten bis 9.908 läuft;
für `(7, 3)` ist das Sollresultat leer. Beide Abfragen müssen auf beiden
Heaps dasselbe vollständige Tupelresultat liefern. Ein bloßer Zeilenzähler
ersetzt diesen Tupelvergleich nicht.

## Statistikprofile und getrennte Befunde

| Profil | Vorhandene Statistikobjekte | Erwartete Metadatenform |
|---|---|---|
| `SINGLE` | Einzelspalte `A`, Einzelspalte `B` | Je ein Histogramm auf der jeweiligen Spalte; keine gemeinsame `(A, B)`-Dichte aus diesen Objekten |
| `MULTI_AB` | dieselben Einzelspaltenstatistiken plus `(A, B)` | Histogramm der Mehrspaltenstatistik nur auf `A`; Dichtevektor mit Präfixen `(A)` und `(A, B)` |

Die spätere Fixture soll nach dem Laden ausdrücklich benannte Statistiken mit
`FULLSCAN` erstellen, damit das synthetische Profil nicht von einer
Stichprobenabweichung abhängt. `DBCC SHOW_STATISTICS` kann Header, Histogramm
und Dichtevektor getrennt ausgeben. Der spätere Befund dokumentiert die
Statistiknamen, Schlüsselreihenfolge, Aktualisierung und tatsächlichen
Ausgaben; er behandelt den alten `Density`-Headerwert nicht als vom Optimierer
verwendeten Dichtevektorwert.

Aus den Daten folgen zwei mathematische Vergleichswerte:

- unter der ausdrücklich hypothetischen Unabhängigkeitsannahme:
  `10.000 × (1/100) × (1/5) = 20` Zeilen für `(A = 7, B = 2)`;
- mittlere Häufigkeit einer beobachteten `(A, B)`-Kombination:
  `10.000 / 100 = 100` Zeilen; die entsprechende Präfixdichte ist `1/100`.

20 und 100 sind nachvollziehbare Fixture-Rechnungen. Sie legen nicht fest,
dass der Kardinalitätsschätzer 20 oder 100 liefern muss. Für beide Profile
werden später geschätzte und tatsächliche Zeilen separat erfasst; die
Korrelation und die tatsächliche Verteilung sind das Korrektheitsorakel.

## Spätere Mess- und Cleanupgrenze

Ein späterer, eigener SQL-Schnitt kann für beide Heaps dieselben beiden
Prädikate ausführen und den tatsächlichen Plan, geschätzte/aktuelle Zeilen und
vorhandene Statistikinformationen dokumentieren. Eine Abweichung oder
Übereinstimmung einzelner Schätzwerte ist nur für den konkreten Build,
Compatibility Level, Statistikstand und Abfragefall gültig. Es wird kein
Indexseek, Joinoperator, Planwechsel oder Leistungsvorteil verlangt.

Die spätere Demo braucht einen markergebundenen Vertrag für Aufbau,
Statistikerstellung, Plan-/Ergebnisbeobachtung und Cleanup der zwei eigenen
Tabellen. Enginekompilierung, Rechte, tatsächliche Statistiknutzung,
Planbefunde und Cleanup sind nicht durch diesen Offlineentwurf qualifiziert.
Er autorisiert keine SQL-/Runtimeausführung und keine menschliche Generalprobe.

## Quellenbindung

`SRC-005` belegt die allgemeine Statistik- und Kardinalitätsschätzungssemantik.
`SRC-143` bindet die Spaltenreihenfolge für `CREATE STATISTICS`, Histogramm
und Dichtevektor sowie deren Ausgabe mit `DBCC SHOW_STATISTICS`. Die
Primärseiten stehen im [Quellenregister](../Research/SOURCE_REGISTER.md#statistikaufbau-und-ausgabe--opt-004).
