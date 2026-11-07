# QRY-011 – Entwurf für Filtered Indexes und Prädikatsimplikation

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `QRY-011` – Filtered Index, nicht implizierendes Prädikat und SET-Options-Gegenprobe |
| Quellen | `SRC-147`, `SRC-148` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Aussagegrenze

Der Entwurf trennt vier Fragen: Welche Tupel liefert ein Prädikat? Impliziert
es das Filterprädikat eines Filtered Index? Ist ein berechneter Spaltenindex
für die aktuelle Session eligibility-bedingt verfügbar? Und welchen Plan
wählt der kostenbasierte Optimierer tatsächlich? Die ersten drei Fragen
erhalten dokumentierte beziehungsweise deterministische Oracles; eine
konkrete Indexnutzung, Operatorform oder Leistungswirkung wird nicht
vorweggenommen.

Der Filtered Index filtert auf einer Basisspalte `Status`. Der Index auf der
berechneten Spalte ist ein separater, ungefilterter Index. Microsoft
dokumentiert, dass die Filterdefinition eines Filtered Indexes keine
berechnete Spalte referenzieren darf.

## Synthetische Fixture und Ergebnistupel

Eine einzelne, eigens markierte Heap-Tabelle enthält 10.000 Zeilen:

- `QueueId` ist die eindeutige, aber nicht als Constraint deklarierte Folge
  1 bis 10.000.
- `Status = 0` für Vielfache von 100, sonst `Status = 1`.
- `PayloadValue = (QueueId * 37) % 100003`.
- `QueueBand` ist die berechnete Spalte `QueueId % 100`.

Die vollständige Ergebnismenge wird sortiert und als Tupel
`(QueueId, Status, PayloadValue, QueueBand)` verglichen. Summen, Counts und
Prüfsummen dürfen das Tupeloracle nicht ersetzen.

| Abfrage | Prädikat | Erwartete Zeilen |
|---|---|---|
| passendes Filter | `Status = 0 AND QueueId BETWEEN 1 AND 10000` | 100 Zeilen: `QueueId` 100, 200, …, 10000 |
| nicht implizierend | `Status IN (0, 1) AND QueueId BETWEEN 1 AND 500` | alle 500 IDs von 1 bis 500 |
| berechnete Spalte | `QueueBand = 42` | 100 IDs: 42, 142, …, 9942 |

Der gefilterte Nonclustered Index verwendet `QueueId` als Schlüssel und
`Status`, `PayloadValue` und `QueueBand` als INCLUDE-Spalten, mit Filter
`Status = 0`. Die
berechnete Indexgegenprobe erhält einen separaten Nonclustered Index mit
`QueueBand` als Schlüssel und `QueueId`, `Status`, `PayloadValue` als
INCLUDE-Spalten. Das sind Designziele; tatsächliche Katalogstruktur und
Kompilierbarkeit sind noch nicht enginequalifiziert.

Das Prädikat `Status = 0` impliziert das Indexfilter `Status = 0`; das
Prädikat `Status IN (0, 1)` tut es nicht. Der Optimierer darf den Filtered
Index für die zweite Abfrage nicht als alleinige vollständige Quelle der
Ergebniszeilen verwenden, weil Zeilen mit `Status = 1` zum Ergebnis gehören.
Die Abfrage kann andere Zugriffspfade oder Kombinationen wählen. Daraus
folgt keine Assertion über einen bestimmten Planoperator.

## Computed-Column-Eligibility und SET-Gegenprobe

`QueueBand = QueueId % 100` verwendet ausschließlich einen `int`-Wert und
einen deterministischen, präzisen ganzzahligen Ausdruck. Der berechnete
Spaltenindex wird getrennt vom Filtered Index angelegt. Für Definition,
Indexaufbau, DML und normale SELECT-Ausführung gelten die vom Produkt
dokumentierten SET-Voraussetzungen: `ANSI_NULLS`, `ANSI_PADDING`,
`ANSI_WARNINGS`, `ARITHABORT`, `CONCAT_NULL_YIELDS_NULL` und
`QUOTED_IDENTIFIER` auf `ON`, `NUMERIC_ROUNDABORT` auf `OFF`.

Die begrenzte Negativgegenprobe ändert genau eine Option in einer separaten
read-only SELECT-Session: `NUMERIC_ROUNDABORT ON`; die übrigen sechs bleiben
`ON`. Das Datenorakel für `QueueBand = 42` bleibt identisch. Die dokumentierte
Eligibility-Erwartung ist, dass der Optimierer sowohl den Index auf der
berechneten Spalte als auch einen Filtered Index bei ungeeigneten Required
SET options nicht berücksichtigt. Tatsächliche Pläne unter korrekten und
falschen Optionen sind erst in einer späteren Runtimequalifikation zu
beobachten. Fehlt im korrekten SET-Profil eine Indexnutzung, ist das kein
Fehlschlag des Tupel- oder Implikationsoracles und kein Grund, den Plan zu
erzwingen.

Unter der falschen Option erfolgt ausschließlich SELECT. Es gibt dort keine
INSERT-, UPDATE- oder DELETE-Gegenprobe: Microsoft dokumentiert, dass DML,
welches gefilterte oder berechnete Indexwerte ändert, bei ungeeigneten
Optionen scheitern kann.

## Cleanup- und Qualifikationsgrenze

Setup und Cleanup binden die vollständigen Objekt- und Indexnamen an genau
die eigene markierte Tabelle. Fehlerpfade entfernen ausschließlich die
eigenen Objekte; keine Fremdtabellen werden verändert. Vor einer späteren
Runtime müssen Zielbuilds, Metadatenrechte, T-SQL-Kompilierung,
Katalogassertionen und sicherer Cleanup eigenständig qualifiziert werden.

Der Entwurf autorisiert keine SQL-/Lab-Ausführung, Planabnahme oder
Performanceaussage und ersetzt keine menschliche Generalprobe. Die Auswahl
des Indexes, Estimates, Operatoren, Reads, CPU und Laufzeit bleiben offen.

## Quellenbindung

`SRC-147` bindet Filterdefinition, logische Implikation und Required SET
options für Filtered Indexes. `SRC-148` bindet Determinismus, Präzision, SET-
Voraussetzungen und die Ignorierung des berechneten Indexes bei falschen
Sessionoptionen. Die Primärquellen stehen im
[Quellenregister](../Research/SOURCE_REGISTER.md#filtered-indexes-und-berechnete-indexspalten--qry-011).
