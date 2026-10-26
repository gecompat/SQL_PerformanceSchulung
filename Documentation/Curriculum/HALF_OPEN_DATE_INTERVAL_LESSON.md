# Halboffene Datumsintervalle und Datentypgenauigkeit

Diese kurze Lehrnotiz ergänzt `LO-M03-02` mit synthetischen Beispielen. Sie
erläutert Intervallgrenzen; sie ist keine freigegebene QRY-003-Demo und keine
Laufzeit- oder Leistungsqualifikation.

## `BETWEEN` schließt beide Grenzen ein

SQL Server wertet `x BETWEEN a AND b` als `x >= a AND x <= b` aus. Soll ein
Zeitbereich vom Beginn eines Tages bis zum Beginn des Folgetages reichen,
schließt `BETWEEN @Start AND @EndExclusive` daher auch einen Datensatz genau
am Folgetagesbeginn ein. Das ist ein anderes Intervall als
`[@Start, @EndExclusive)`.

```sql
DECLARE @Events TABLE
(
    EventId int NOT NULL PRIMARY KEY,
    OccurredAt datetime2(7) NOT NULL
);

INSERT INTO @Events (EventId, OccurredAt)
VALUES
    (1, '2026-03-07T00:00:00.0000000'),
    (2, '2026-03-07T23:59:59.9999999'),
    (3, '2026-03-08T00:00:00.0000000');

DECLARE @Start datetime2(7) = '2026-03-07T00:00:00.0000000';
DECLARE @EndExclusive datetime2(7) = DATEADD(day, 1, @Start);

-- Schließt den Folgetagesbeginn ein.
SELECT EventId, OccurredAt
FROM @Events
WHERE OccurredAt BETWEEN @Start AND @EndExclusive
ORDER BY EventId;

-- Intervall [Start, EndExclusive): schließt den Folgetagesbeginn aus.
SELECT EventId, OccurredAt
FROM @Events
WHERE OccurredAt >= @Start
  AND OccurredAt < @EndExclusive
ORDER BY EventId;
```

Die erste Abfrage gibt die drei Beispieldatensätze zurück; die zweite nur die
beiden Zeitpunkte des 7. März. Der Unterschied ist an der exakten oberen
Grenze sichtbar und nicht von einer angenommenen letzten Uhrzeit des Tages
abhängig.

## Grenzen passend zum Spaltentyp bilden

Für aufeinanderfolgende Tagesbereiche ist die halboffene Form
`Zeitpunkt >= @Start AND Zeitpunkt < @EndExclusive` geeignet. Der nächste
Bereich kann denselben Wert als Startgrenze verwenden. Erfinde keine
Tagesendgrenze wie `23:59:59.997`: sie hängt von der Auflösung und dem Typ der
Spalte ab und kann Werte auslassen oder in den Folgetag reichen.

SQL Server dokumentiert für `datetime2(p)` eine einstellbare
Nachkommastellenpräzision von 0 bis 7; `datetime2(7)` kann Werte bis
`23:59:59.9999999` darstellen. `datetime` hat eine andere Genauigkeit und
rundet Zeitwerte auf seine darstellbaren Schritte. Deshalb sollen Parameter
und Grenzen den fachlichen Spaltentyp und dessen Präzision abbilden. Eine
Konvertierung der Grenze kann Werte runden oder verwerfen; sie ist keine
neutrale Formatierung.

```sql
-- Beispiel für eine datetime2(3)-Spalte:
DECLARE @Start3 datetime2(3) = '2026-03-07T00:00:00.000';
DECLARE @EndExclusive3 datetime2(3) = DATEADD(day, 1, @Start3);

-- Der Parameter und die Grenzen sind auf datetime2(3) abgestimmt.
-- In einer Anwendung denselben Typ für den gebundenen Parameter verwenden.
```

Bei einer `date`-Spalte ist ein Tagesvergleich eine andere Fragestellung als
bei einem Zeitstempel. Bei `datetimeoffset` müssen zudem die fachliche
Zeitzone und die Bedeutung der Offsetgrenzen geklärt sein. Dieses Beispiel
legt keine Zeitzonenregel fest.

## Quellen

- Microsoft Learn, [BETWEEN (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/between-transact-sql?view=sql-server-ver17): beide Grenzen sind einschließend; Abruf am 2026-10-26.
- Microsoft Learn, [datetime2 (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/data-types/datetime2-transact-sql?view=sql-server-ver17): Wertebereich und einstellbare Bruchteilssekundenpräzision; Abruf am 2026-10-26.
- Microsoft Learn, [datetime (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/data-types/datetime-transact-sql?view=sql-server-ver17): Genauigkeit und Rundungsverhalten; Abruf am 2026-10-26.
- Microsoft Learn, [DATEADD (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/functions/dateadd-transact-sql?view=sql-server-ver17): Rückgabetyp folgt dem Datumseingang, sofern kein Zeichenfolgenliteral verwendet wird; Abruf am 2026-10-26.
