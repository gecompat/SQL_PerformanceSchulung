# Join-Kardinalität und `DISTINCT`

Diese kurze Erläuterung zeigt, wie eine One-to-many-Beziehung die Zeilen eines
Joins vervielfacht und wann `DISTINCT` oder `EXISTS` zur gewünschten Ergebnismenge
passt. Sie ist eine quellengebundene Erklärung zum Query-Pattern `QRY-007`, aber
keine freigegebene Demo, Messung oder Performancequalifikation.

## Fixture und direkte Join-Ergebnisse

Die Fixture enthält Eltern `P-A`, `P-B` und `P-C`. `P-A` hat zwei aktive Kinder,
`P-B` ein aktives und ein inaktives Kind, `P-C` keines. Die fachliche Frage
lautet: „Welche Eltern haben mindestens ein aktives Kind?“

```sql
DECLARE @Parent TABLE
(
    ParentId char(3) NOT NULL PRIMARY KEY,
    ParentName nvarchar(30) NOT NULL
);

DECLARE @Child TABLE
(
    ChildId int NOT NULL PRIMARY KEY,
    ParentId char(3) NOT NULL,
    IsActive bit NOT NULL
);

INSERT INTO @Parent (ParentId, ParentName)
VALUES ('P-A', N'Alpha'), ('P-B', N'Beta'), ('P-C', N'Gamma');

INSERT INTO @Child (ChildId, ParentId, IsActive)
VALUES (101, 'P-A', 1), (102, 'P-A', 1),
       (201, 'P-B', 1), (202, 'P-B', 0);

SELECT p.ParentId, p.ParentName, c.ChildId
FROM @Parent AS p
INNER JOIN @Child AS c
    ON c.ParentId = p.ParentId
WHERE c.IsActive = 1
ORDER BY p.ParentId, c.ChildId;
```

Die Abfrage gibt drei Zeilenpaare zurück: `P-A` zweimal und `P-B` einmal.
Das ist die Join-Multiplizität der passenden Eltern-/Kindpaare. Sie ist korrekt,
wenn jedes passende Paar gefragt ist. Soll die Abfrage dagegen Eltern mit
mindestens einem aktiven Kind liefern, ist die gewünschte Elternmenge
`{P-A, P-B}` mit genau einer Zeile pro Eltern-ID.

## Projektion, `DISTINCT` und `EXISTS`

```sql
-- Eindeutige Projektion auf Elternattribute; drei Joinpaare werden zwei Zeilen.
SELECT DISTINCT p.ParentId, p.ParentName
FROM @Parent AS p
INNER JOIN @Child AS c
    ON c.ParentId = p.ParentId
WHERE c.IsActive = 1
ORDER BY p.ParentId;

-- Existenzfrage: ein Ergebnis je Elternzeile mit mindestens einem Treffer.
SELECT p.ParentId, p.ParentName
FROM @Parent AS p
WHERE EXISTS
(
    SELECT 1
    FROM @Child AS c
    WHERE c.ParentId = p.ParentId
      AND c.IsActive = 1
)
ORDER BY p.ParentId;
```

Beide Abfragen liefern für diese Elternprojektion `{P-A, P-B}`. Das Ergebnis
von `DISTINCT` allein erklärt aber nicht, warum der Join mehrere Paare erzeugte.
`DISTINCT` entfernt nur gleiche projizierte Zeilen: Werden unterschiedliche
Kindattribute mitprojiziert, können die zwei Zeilen von `P-A` verschieden
bleiben. `EXISTS` passt unmittelbar zur Frage, ob überhaupt ein aktives Kind
vorliegt.

## Aggregation nur für gewünschte Kindfakten

Wenn statt einer bloßen Existenz die Zahl aktiver Kinder gefragt ist, ist die
fachliche Ergebniskörnung eine Zusammenfassung je Eltern-ID:

```sql
SELECT p.ParentId, p.ParentName, COUNT_BIG(c.ChildId) AS ActiveChildCount
FROM @Parent AS p
LEFT JOIN @Child AS c
    ON c.ParentId = p.ParentId
   AND c.IsActive = 1
GROUP BY p.ParentId, p.ParentName
ORDER BY p.ParentId;
```

Das erwartete Ergebnis lautet `P-A = 2`, `P-B = 1`, `P-C = 0`. Die Filterbedingung
für aktive Kinder steht im `ON`, damit `LEFT JOIN` auch `P-C` erhält; `COUNT_BIG`
zählt nur nicht-NULL `ChildId`-Werte. Aggregation ist hier passend, weil die
Kindanzahl selbst Teil der fachlichen Antwort ist. Sie ist nicht automatisch
die richtige Ersatzform für jede Join- oder Existenzabfrage.

## Oracle, Interpretation und Grenzen

Prüfe vollständige IDs und Multiplizitäten, nicht nur die Gesamtzeilenzahl:

| Variante | Erwartung |
|---|---|
| Join mit Eltern- und Kind-ID | drei Paare: `P-A` zweimal, `P-B` einmal |
| `DISTINCT` nur auf Elternspalten | `P-A` und `P-B`, je einmal |
| `EXISTS` auf aktive Kinder | `P-A` und `P-B`, je einmal |
| Anzahl aktiver Kinder je Eltern-ID | `P-A = 2`, `P-B = 1`, `P-C = 0` |

Die `DISTINCT`-Projektion ist fachlich richtig, falls wirklich eine Menge
eindeutiger Elternzeilen verlangt wird. Sie ist keine Reparatur für eine
falsche Beziehung oder eine ungeklärte Ergebniskörnung. Diese Beispiele setzen
keine Index-, Join-Algorithmus- oder Laufzeiterwartung. Der tatsächliche Plan
und Logical Reads wären separate Diagnostik und begründen ohne Messung keinen
Leistungsvorteil.

`SRC-135` im [Quellenregister](../Research/SOURCE_REGISTER.md) bindet die
Microsoft-Dokumentation zu `DISTINCT`, Join-Zeilenpaaren, `EXISTS` und
`GROUP BY`. Der [QRY-007-Entwurf](../Project_Planning/QRY007_JOIN_CARDINALITY_DESIGN.md)
führt den vorgeschlagenen Fixture- und Demo-Grenzvertrag weiter. `UNION`,
`UNION ALL` und `SELECT *` sind in diesem Lerntext nicht qualifiziert. Die
menschliche Generalprobe bleibt ausgeschlossen.
