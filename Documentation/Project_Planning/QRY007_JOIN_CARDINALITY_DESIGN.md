# QRY-007 – Entwurf zu Join-Kardinalität und `DISTINCT`

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `QRY-007` – `DISTINCT`, `UNION`, `UNION ALL` und Modellierungsindikatoren |
| Quellen | `SRC-135` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

Dieser Entwurf behandelt ausschließlich Join-Kardinalität, Projektion,
`DISTINCT`, `EXISTS` und gezielte Aggregation. Die weiteren QRY-007-Themen
`UNION`, `UNION ALL` und `SELECT *` werden damit nicht qualifiziert.

## Lernkern

Ein `INNER JOIN` gibt passende Zeilenpaare zurück. Wenn ein Elternsatz mehrere
passende Kindzeilen hat, erscheint die projizierte Elternidentität daher
mehrfach. `DISTINCT` entfernt gleiche projizierte Zeilen; es kann eine falsche
Erwartung über die Kardinalität des Joins verdecken, wenn die Abfrage fachlich
eine Elternmenge liefern soll. Das ist keine pauschale Aussage, dass `DISTINCT`
falsch ist: Es ist korrekt, wenn die gewünschte Ergebnismenge tatsächlich aus
eindeutigen Projektionen besteht.

## Synthetische fachliche Fixture

Die mögliche Lehrfixture hat drei Elternentitäten `P-A`, `P-B` und `P-C` sowie
aktive Kinddatensätze wie folgt:

| Eltern-ID | Anzahl passender aktiver Kinder | Erwartung für „Eltern mit mindestens einem aktiven Kind“ |
|---|---:|---|
| `P-A` | 2 | einmal enthalten |
| `P-B` | 1 | einmal enthalten |
| `P-C` | 0 | ausgeschlossen |

Für die Elternprojektion erzeugt der direkte Join drei Zeilen mit der
Multiplizität `P-A × 2`, `P-B × 1`. Die fachliche Sollmenge ist
`{P-A, P-B}`. Das vollständige Oracle vergleicht Eltern-IDs und Multiplizität;
eine bloße Zeilenzahl reicht nicht. Falls Kindattribute mitprojiziert werden,
sind die `P-A`-Zeilen möglicherweise nicht gleich und `DISTINCT` entfernt sie
nicht. Der Test darf daher nicht behaupten, `DISTINCT` dedupliziere unabhängig
von der Projektion.

## Varianten und Abnahmegrenzen

1. **Direkter Join:** erwartete Zeilenpaare beobachten und die unterschiedliche
   Elternmultiplizität als Diagnose der One-to-many-Beziehung sichtbar machen.
2. **Join plus `DISTINCT`:** eindeutige Elternprojektion mit `{P-A, P-B}`
   vergleichen. Das Ergebnis kann der erwarteten Elternmenge entsprechen,
   während die Join-Kardinalität und deren Ursache weiter geprüft werden muss.
3. **`EXISTS`:** für die Fragestellung „hat mindestens ein passendes Kind?“
   genau die Elternmenge `{P-A, P-B}` als Existenzabfrage formulieren.
4. **Aggregation:** nur verwenden, wenn das Lernziel Kindfakten wie Anzahl
   oder Summe verlangt. Dann zuerst die gewünschte Kindkörnung pro `ParentID`
   eindeutig bestimmen und diese Zusammenfassung gegen ein separates Oracle
   prüfen. Eine Aggregation ist nicht automatisch Ersatz für `EXISTS`.

Alle Ergebnisvergleiche verwenden dieselbe Elternprojektion und denselben
fachlichen Filter. Die Abnahme prüft vollständige IDs, Paarmultiplizität und
die erwartete Elternkörnung. Sie misst weder einen Laufzeitvorteil noch
erzwingt sie eine bestimmte physische Planform. Sort-/Hash-Aggregate oder
Semi-Join-Operatoren sind mögliche Planbeobachtungen, keine Versions-Sollwerte.

## Quellen- und Aussagegrenze

`SRC-135` bindet die dokumentierte `DISTINCT`-Projektion, die passenden
Zeilenpaare eines Joins und die Existenzsemantik von `EXISTS` an Microsoft
Learn. Diese Quellen belegen weder die Kardinalität einer konkreten Fixture
noch einen Performanceeffekt. Ein späterer ausführbarer Schnitt benötigt
weiterhin eigenen Demo-, Setup-/Cleanup-, Ergebnis- und Methodenvertrag sowie
die dafür nötige konkrete Ausführungsfreigabe. Dieses Design erzeugt keinen
Katalogeintrag und führt kein SQL oder eine menschliche Generalprobe aus.
