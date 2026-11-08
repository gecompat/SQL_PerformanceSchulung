# QRY-007 – Entwurf zu Join-Kardinalität und `DISTINCT`

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `QRY-007` – Join-Kardinalität, Projektion, `DISTINCT`, `EXISTS` und angeforderte Aggregation |
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

Die Lehrfixture entspricht der [Curriculum-Erläuterung](../Curriculum/DISTINCT_JOIN_CARDINALITY_LESSON.md)
und verwendet genau diese vollständig festgelegten synthetischen Zeilen:

| Eltern-Tupel (`ParentId`, `ParentName`) |
|---|
| `('P-A', N'Alpha')` |
| `('P-B', N'Beta')` |
| `('P-C', N'Gamma')` |

| Kind-Tupel (`ChildId`, `ParentId`, `IsActive`) |
|---|
| `(101, 'P-A', 1)` |
| `(102, 'P-A', 1)` |
| `(201, 'P-B', 1)` |
| `(202, 'P-B', 0)` |

Die Fremdschlüsselwerte sind synthetisch; die Datenmenge enthält absichtlich
keinen Kinddatensatz für `P-C`. Daraus folgen die aktiven Kindzahlen:

| Eltern-ID | Anzahl passender aktiver Kinder | Erwartung für „Eltern mit mindestens einem aktiven Kind“ |
|---|---:|---|
| `P-A` | 2 | einmal enthalten |
| `P-B` | 1 | einmal enthalten |
| `P-C` | 0 | ausgeschlossen |

Der direkte Join mit der Projektion `(ParentId, ParentName, ChildId)` muss
exakt diese sortierten Tupel liefern:

```text
('P-A', N'Alpha', 101)
('P-A', N'Alpha', 102)
('P-B', N'Beta', 201)
```

Die fachliche Sollmenge für die Elternfrage ist `(P-A, Alpha)` und
`(P-B, Beta)`, jeweils genau einmal. Die Kind-ID unterscheidet die beiden
`P-A`-Paare. Wird sie mitprojiziert, lässt `DISTINCT` diese Zeilen zu Recht
getrennt. Das Tupeloracle prüft Werte, Sortierung und Multiplizität; die
Gesamtzeilenzahl allein reicht nicht.

## Varianten und Abnahmegrenzen

1. **Direkter Join:** erwartet exakt die drei oben gelisteten Eltern-/Kind-
   Tupel.
2. **Join plus `DISTINCT` auf Elternspalten:** erwartet
   `[('P-A', N'Alpha'), ('P-B', N'Beta')]`.
3. **`DISTINCT` mit Kind-ID:** erwartet dieselben drei Tupel wie der direkte
   Join, da `ChildId` die passenden Kindzeilen unterscheidet.
4. **`EXISTS`:** für die Frage „hat mindestens ein aktives Kind?“ erwartet
   `[('P-A', N'Alpha'), ('P-B', N'Beta')]`.
5. **Aggregation:** `LEFT JOIN` mit dem Aktivfilter im `ON` und Gruppierung
   je Elternidentität erwartet
   `[('P-A', N'Alpha', 2), ('P-B', N'Beta', 1), ('P-C', N'Gamma', 0)]`.
   `COUNT_BIG(c.ChildId)` zählt nur passende, nicht-NULL Kind-IDs. Der
   Filter im `ON` erhält `P-C`; ein Filter auf die Kindspalte in `WHERE`
   würde die Null-erweiterte Elternzeile verwerfen.

Jede Variante verwendet ihre vollständige sortierte Tupelliste als Oracle.
Damit prüft die Fixture sowohl Joinpaar-Multiplizität als auch die gewünschte
Eltern- oder Aggregatkörnung. Aggregation ist nicht automatisch Ersatz für
`EXISTS`; sie passt hier, weil die Kindanzahl ausdrücklich Teil der Antwort
ist.

Alle Ergebnisvergleiche verwenden denselben fachlichen Filter `IsActive = 1`
und halten die Projektion pro Variante explizit fest. Die Abnahme prüft
vollständige Tupel, Paarmultiplizität und die erwartete Elternkörnung. Sie misst weder einen Laufzeitvorteil noch
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
