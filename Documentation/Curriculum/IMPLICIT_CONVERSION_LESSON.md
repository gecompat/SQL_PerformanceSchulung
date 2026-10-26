# Datentypen und implizite Konvertierung

Diese Lehrnotiz ergänzt das Kernlernziel `LO-M03-01` in der
[Curriculumarchitektur](CURRICULUM_ARCHITECTURE.md). Sie
erklärt typische Konvertierungen an kleinen, synthetischen T-SQL-Beispielen.
Sie ist keine freigegebene QRY-002-Demo und enthält keine gemessene
Performanceaussage. Der registrierte Demo- und Laufzeitstatus wird dadurch
nicht geändert.

## Datentyppriorität beeinflusst den Ausdruck

Wenn ein Operator Ausdrücke verschiedener Datentypen kombiniert, konvertiert
SQL Server den niedriger priorisierten Typ in den höher priorisierten, sofern
die Konvertierung unterstützt wird. Bei `int` und `nvarchar` hat `int` die
höhere Priorität; ein `+` kann deshalb Addition statt Textverkettung bedeuten:

```sql
DECLARE @Anzahl int = 2;

SELECT @Anzahl + N'3' AS Rechenergebnis; -- 5: N'3' wird für den Ausdruck zu int.
SELECT N'2' + N'3' AS Textverkettung;   -- 23: beide Operanden sind Text.
```

Die Beispiele zeigen unterschiedliche Operatorsemantik. Sie behaupten nicht,
dass eine Textdarstellung und ein Zahlenwert generell fachlich austauschbar
sind. Insbesondere können führende Nullen, Leerzeichen, Vorzeichen,
Dezimalzeichen oder ungültige Zeichen für die Anwendung Bedeutung haben.

## Parameter passend zum Spaltentyp binden

Für Vergleiche sollte ein Anwendungsparameter denselben fachlichen und
SQL-Datentyp wie die Zielspalte verwenden. Das vermeidet, sich auf eine
implizite Konvertierung zu verlassen:

```sql
DECLARE @Kunden TABLE (KundenId int PRIMARY KEY);
INSERT INTO @Kunden (KundenId) VALUES (42), (73);

DECLARE @KundenId int = 42;
SELECT KundenId
FROM @Kunden
WHERE KundenId = @KundenId;
```

Bei einer `int`-Spalte sollte der Client den Parameter als `int` senden, nicht
als Text. Wenn eine Grenze tatsächlich Text liefert, validieren und
konvertieren Sie den Eingang einmal dort. Bei einem nicht konvertierbaren Wert
innerhalb einer grundsätzlich zulässigen Typkonvertierung liefert
`TRY_CONVERT` `NULL`; ist die Typkonvertierung selbst ausdrücklich unzulässig,
entsteht weiterhin ein Fehler:

```sql
DECLARE @Eingabe nvarchar(20) = N'42x';
SELECT TRY_CONVERT(int, @Eingabe) AS GepruefteKundenId; -- NULL
```

Ein anschließender Vergleich mit `NULL` findet keine Zeile. Behandeln Sie
diesen Fall daher als ungültigen Eingang, statt ihn mit einer echten
`NULL`-Kennung gleichzusetzen. Ein direktes `CONVERT(int, @Eingabe)` würde
für `N'42x'` einen Konvertierungsfehler melden.

## Die Spalte nicht vorschnell umformen

Ein Prädikat wie `CAST(KundenId AS nvarchar(20)) = @TextEingang` vergleicht die
Textform der Spalte. Es kann Werte anders behandeln als ein numerischer
Vergleich und dem Optimierer möglicherweise erschweren, einen direkten
Suchbereich für einen Index auf `KundenId` abzuleiten. Das ist keine Aussage,
dass dieses Prädikat stets einen Scan erzeugt.

Bevorzugen Sie einen typgerechten Parameter oder prüfen Sie einen Texteingang
vor dem Vergleich. Konvertierungen auf der Spaltenseite führen nicht in jedem
Fall zum selben Plan; formulieren Sie daraus keine Regel „Konvertierung gleich
Scan“. Für eine konkrete Abfrage sind tatsächlicher Plan, Datentypen,
Ausdrucksform und vorhandene Indizes zu prüfen.

## Collation ist eine eigene Vergleichsregel

Bei Zeichendaten bestimmt die Collation (Zeichensortier- und Vergleichsregel)
unter anderem Sortierung und Vergleichsregeln wie Groß-/Kleinschreibung. Sie
ist getrennt von der Datentyppriorität zu beurteilen. Diese Ausdrücke zeigen, dass
dieselbe Zeichenfolge je nach bewusst gewählter Collation unterschiedlich
verglichen wird:

```sql
SELECT
    CASE WHEN N'a' COLLATE Latin1_General_100_CI_AS =
                   N'A' COLLATE Latin1_General_100_CI_AS THEN 1 ELSE 0 END AS OhneGrossKleinschreibung,
    CASE WHEN N'a' COLLATE Latin1_General_100_CS_AS =
                   N'A' COLLATE Latin1_General_100_CS_AS THEN 1 ELSE 0 END AS MitGrossKleinschreibung;
```

Die Ausdrücke ergeben `1` und `0`. Zwei explizite `COLLATE`-Ausdrücke mit
unterschiedlichen Collations können dagegen einen Konfliktfehler auslösen.
Wenn zwei Spalten oder ein Parameter und eine Spalte verglichen werden,
gleichen Sie die Collation nur dann explizit an, wenn die gewählte
Sortier-/Vergleichssemantik fachlich passt. Eine `COLLATE`-Klausel ist keine
neutrale Reparatur.

## Quellen und Aussagegrenzen

- Microsoft Learn, [Datentyppriorität](https://learn.microsoft.com/en-us/sql/t-sql/data-types/data-type-precedence-transact-sql?view=sql-server-ver17), Abruf 2026-10-26: Konvertierungsrichtung bei Operatoren verschiedener Datentypen.
- Microsoft Learn, [CAST und CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17) sowie [TRY_CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/try-convert-transact-sql?view=sql-server-ver17), Abruf 2026-10-26: explizite Konvertierung und Fehlerverhalten.
- Microsoft Learn, [Collation-Priorität](https://learn.microsoft.com/en-us/sql/t-sql/statements/collation-precedence-transact-sql?view=sql-server-ver17) und [Collation und Unicode](https://learn.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support?view=sql-server-ver17), Abruf 2026-10-26: Vorrangregeln und Auswirkungen auf Zeichenvergleiche.
- Microsoft Learn, [Indexarchitektur und -entwurf](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17), Abruf 2026-10-26: Suchargumente und Grenzen bei Konvertierungen in Prädikaten.
- Microsoft Learn, [Tatsächlichen Ausführungsplan anzeigen](https://learn.microsoft.com/en-us/sql/relational-databases/performance/display-an-actual-execution-plan?view=sql-server-ver17), Abruf 2026-10-26: Laufzeitplan zur Prüfung einer konkreten Abfrage.
- Das vorhandene Quellenregister führt [SRC-030](../Research/SOURCE_REGISTER.md) für Datentyppriorität und `QRY-002`; `SRC-012` behandelt den Indexentwurf.

Diese qualitative Lehrnotiz enthält keine Ausführungspläne, Laufzeit- oder
Logical-Read-Messungen. Sie qualifiziert keine Demo, keinen Versionsmatrixlauf
und keinen Leistungsgewinn.
