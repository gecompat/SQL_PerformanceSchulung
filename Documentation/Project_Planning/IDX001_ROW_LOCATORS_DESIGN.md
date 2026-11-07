# IDX-001 – Entwurf für Heap- und Clustered-Row-Locators

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `IDX-001` – RID Lookup und Key Lookup vergleichen |
| Quellen | `SRC-012`, `SRC-013`, `SRC-138` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Aussagegrenze

Der Entwurf vergleicht dieselbe logische Abfrage auf zwei Tabellen mit
identischen Zeilen und Spalten: eine Heap-Tabelle ohne Clustered Index und eine
Tabelle mit schmalem eindeutigem Clustered Key. Jeweils ein nicht abdeckender
Nonclustered Index findet Kandidaten über `FilterBand`; `Payload` wird aus der
Basistabelle benötigt. Der Unterschied im Row Locator ist die gezielte
Fragestellung: RID zur Heapzeile oder Clustered Key zur Zeile der Clustered
Table.

Die erwartete Showplan-Zuordnung ist `RID Lookup` für die Heapvariante und
`Key Lookup` für die Clustered-Variante. Beide Operatoren werden in der
Microsoft-Operatorreferenz mit `Nested Loops` verbunden. Das sind
strukturgebundene Diagnoseassertions, keine Zusage, dass der Optimierer bei
jeder Trefferzahl einen Lookup wählt. Ein Scan oder eine andere zulässige
Planform darf nicht durch einen Planhinweis verhindert oder erzwungen werden.

Der Entwurf behauptet weder eine allgemeine Geschwindigkeitsrangfolge noch,
dass RID oder Clustered Key für jeden Workload günstiger sei. Die von Microsoft
beschriebene 8-Byte-RID-Größe ist eine Locator-Eigenschaft, kein alleiniger
Beweis für die Gesamtgröße eines Indexes oder eine Performanceprognose.

## Gemeinsame Fixture und Profile

Vorgeschlagen ist ein deterministischer Datensatz mit 100.000 Zeilen und den
Spalten `RowId int NOT NULL`, `FilterBand int NOT NULL` sowie `Payload char(200)
NOT NULL`. `RowId` läuft lückenlos von 1 bis 100.000; `FilterBand` ist
`(RowId - 1) % 100`; `Payload` wird allein aus `RowId` deterministisch
gebildet. Damit liegen je Band exakt 1.000 Zeilen vor. Die Payload ist bewusst
nicht im Vergleichsindex enthalten.

Zwei Tabellen erhalten exakt dieselben vollständigen Tupel:

| Profil | Basistabellenstruktur | Sekundärindex | Row Locator der nicht eindeutigen NCI |
|---|---|---|---|
| `HEAP` | Heap, ohne Clustered Index | `(FilterBand)` | RID |
| `CLUSTERED` | eindeutiger Clustered Index auf `(RowId)` | `(FilterBand)` | Clustered Key `RowId` |

Auf jeder Tabelle ist ausschließlich dieser eine sekundäre Nonclustered Index
vorhanden. Beide sind nicht eindeutig und nicht abdeckend. Damit bleibt der
logische Suchschlüssel gleich; der Strukturunterschied stammt aus dem
Basistabellen-Row-Locator.

## Abfragefälle und Oracles

Die beiden Tabellen werden mit derselben Abfrageform gelesen:

```sql
SELECT RowId, FilterBand, Payload
FROM dbo.OperatorHeap -- alternativ: dbo.OperatorClustered
WHERE FilterBand = @FilterBand
  AND RowId = @RowId;
```

Der Punktfall verwendet `FilterBand = 36` und `RowId = 37037` und muss genau
ein vollständiges Tupel liefern. Der Suchindex kann zunächst Kandidaten für das
Band lokalisieren; der zusätzliche RowId-Test und die Ausgabe von `Payload`
bleiben Bestandteil derselben logischen Abfrage. Der Bereichsfall verwendet
`FilterBand BETWEEN 37 AND 39` und muss 3.000 vollständige Tupel liefern.
Beide Fälle laufen auf beiden Tabellen. Die vollständigen Tupelmengen und
`RowId`-Multiplizitäten müssen mit dem Fixtureoracle und zwischen HEAP und
CLUSTERED übereinstimmen. Gleiche Zeilenzahl allein genügt nicht.

Die Bereichsform erlaubt keine Schlussfolgerung über einen universellen
Scan-/Lookup-Kipppunkt oder eine repräsentative Selektivität. Es handelt sich
um einen kontrollierten Locatorvergleich auf einer einzelnen synthetischen
Verteilung.

## Beobachtungen und spätere Gates

Bei einer später gesondert autorisierten Engineprüfung werden tatsächliche
Pläne gesammelt. Wenn ein Lookup-Operator vorhanden ist, muss der Heapplan den
RID-Zugriff und der Clustered-Plan den Key-Zugriff zeigen; fehlt ein Lookup,
wird die tatsächliche alternative Planform protokolliert, nicht als Fehler
umgedeutet. Tatsächliche Operatorausführungen, Zeilen, Logical Reads und
verstrichene Zeit bleiben getrennte Messwerte. Ausführbarkeit und
Fixturegenerator sind vor einer späteren SQL-Umsetzung am Engineverhalten zu
prüfen.

Vor Implementierung oder Ausführung sind ein vollständiger
Demo-/Setup-/Cleanupvertrag, Fixture- und Enginevalidierung, Berechtigungs-
und Versionsprüfung, Methodenreview und konkrete Ausführungsfreigabe nötig.
Dieser statische Entwurf erfüllt keines dieser Laufzeitgates und schließt keine
menschliche Generalprobe ein.

Die Quellen-IDs sind im [Quellenregister](../Research/SOURCE_REGISTER.md)
aufgeführt. `SRC-012` beschreibt Row-Locator-Struktur und implizite
Locator-Spalten, `SRC-013` Heap und RID, `SRC-138` die beiden bedingten
Showplan-Operatorzuordnungen.
