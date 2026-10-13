# SQL-Sessiondaten mit einem strikten Reader lesen

Ein SQL-Ergebnis hat nicht nur einen Wert, sondern auch einen Datentyp. Für einen
.NET-Reader kann `51` deshalb als `smallint` etwas anderes sein als derselbe Wert
als `int`. Diese Lesehilfe zeigt, wie SQL-Projektion und typisierter Getter
zusammenpassen. Zum Lesen sind keine Installation, kein lokales Modell und kein
neuer Driverlauf erforderlich.

## Eine Zahl ist nicht automatisch Int32

[`@@SPID`](https://learn.microsoft.com/en-us/sql/t-sql/functions/spid-transact-sql?view=sql-server-ver17)
liefert die aktuelle Session-ID als `smallint`. Der dokumentierte
[`GetInt32`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getint32?view=sqlclient-dotnet-core-6.1)
konvertiert nicht: Der gelesene Wert muss bereits ein 32-Bit-Integer sein.
Ein numerisch passender Wert allein reicht dafür nicht.

Für einen vorgesehenen `GetInt32(0)` wird die SQL-Projektion ausdrücklich
angepasst. Das folgende Beispiel erläutert den Sourcevertrag; es ist hier kein
neuer Ausführungs- oder Messerfolg:

```sql
SELECT CONVERT(int, @@SPID) AS SessionId;
```

```csharp
// NULL vorher prüfen; ein passender Datentyp ersetzt keine NULL-Kontrolle.
int sessionId = reader.GetInt32(0);
```

Eine alternative Typwahl wäre `GetInt16` für unverändertes `smallint`. Der
vorbereitete Entwurf verwendet die explizite SQL-Konversion zu `int`, damit die
beabsichtigte Sessionstruktur einheitlich bleibt. Eine spätere Übernahme in eine
größere .NET-Struktur ist von der ursprünglichen Readerkonversion zu unterscheiden.

## Die acht Felder getrennt prüfen

Die Ordinals sind die Spaltenpositionen ab null. `CONVERT` bestimmt den
projizierten SQL-Typ; `SERVERPROPERTY` selbst liefert `sql_variant`.

| Ordinal / Feld | SQL-Projektion | Dokumentierter oder ausdrücklich projizierter Typ | Strikter Getter |
|---|---|---|---|
| 0 / SessionId | `CONVERT(int,@@SPID)` | `int`, statt ursprünglichem `smallint` | `GetInt32(0)` |
| 1 / DatabaseId | `DB_ID()` | `int` | `GetInt32(1)` |
| 2 / DatabaseName | `DB_NAME()` | `nvarchar(128)` | `GetString(2)` |
| 3 / Build | `CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion'))` | `nvarchar(128)` | `GetString(3)` |
| 4 / Engine | `CONVERT(int,SERVERPROPERTY('EngineEdition'))` | `int` | `GetInt32(4)` |
| 5 / EditionId | `CONVERT(int,SERVERPROPERTY('EditionID'))` | `int` | `GetInt32(5)` |
| 6 / HostPlatform | `host_platform` aus `sys.dm_os_host_info` | `nvarchar(256)` | `GetString(6)` |
| 7 / CompatibilityLevel | `compatibility_level` aus `sys.databases` | `tinyint` | `GetByte(7)` |

[`GetString`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getstring?view=sqlclient-dotnet-core-6.1)
und [`GetByte`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getbyte?view=sqlclient-dotnet-core-6.1)
führen ebenfalls keine Konversion aus. Ein `tinyint` wird zunächst als `byte`
gelesen; erst danach kann der C#-Konstruktor den Wert in sein `int`-Feld übernehmen.
Die Längen 128/256 in der Tabelle gehören zum dokumentierten beziehungsweise
konfigurierten SQL-Ausdruck.
[`GetDataTypeName`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getdatatypename?view=sqlclient-dotnet-core-6.1) liefert später den Basistyp,
beispielsweise `nvarchar`; dieser Name allein attestiert keine deklarierte
Länge. Der Entwurf erfasst zusätzlich
[`GetFieldType`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqldatareader.getfieldtype?view=sqlclient-dotnet-core-6.1) getrennt davon.
Der konkrete Entwurf verwirft NULL in jedem der acht Felder. Dieser eigene
Ergebnisvertrag behauptet nicht, dass jede Metadatenfunktion grundsätzlich
immer einen sichtbaren, nichtleeren Wert liefern muss.

Drei kleine Entscheidungen helfen beim Lesen einer Fehlersituation:

1. **Wert 51, Typ smallint, Getter GetInt32:** zuerst den Typvertrag korrigieren;
   ein anderer Zahlenwert beseitigt die Typabweichung nicht.
2. **CompatibilityLevel 170, Typ tinyint:** `GetByte` passt; ein späteres C#-`int`
   macht `GetInt32` am ursprünglichen Readerfeld nicht automatisch passend.
3. **GetInt32 passt, aber das Feld ist NULL:** NULL explizit behandeln oder gemäß
   dem konkreten Vertrag abweisen. Weder Nullkonversion noch ein Ersatzwert
   darf unbemerkt aus einer fehlenden Beobachtung einen Erfolg machen.

## Rückgabe, Projektion und Dispose unterscheiden

Ein zurückgekehrtes `ExecuteReaderAsync` bedeutet, dass ein Reader verfügbar
ist. Danach können `ReadAsync`, einzelne Getter, die Ergebnisprüfung oder
`DisposeAsync` scheitern. Ein `InvalidCastException` ist deshalb künftig als
konkreter sicherer Exceptiontyp erhaltenswert. Es ist kein Beleg für einen
VECTOR-Dimensionsfehler und kein Ersatz für die native SQL-Fehlernummer.

Der private Sourceentwurf hält diese Schritte mit eigenen Zeitpunkten und
API-Enden auseinander und bewahrt Primary- und Disposefehler getrennt. Bei
`SqlException` gehören Nummer, Severity, State, Line, Procedure und vollständige
UTF16-Nachricht zusammen. Solche tatsächlichen Detailrecords bleiben privat;
vor einer Speicherung sind Credentials auszuschließen. Messages, Stack,
Connectionstrings und geheime Werte gehören nicht in öffentliche Summaries.

`API_THREW` kann ein bekanntes API-Ende sein und gleichzeitig keinen belegten
Server-/Transportabschluss liefern. Ein später erfolgreiches Dispose löscht
früheres UNKNOWN nicht. Der jeweilige ausführende Caller muss Folge-SQL dann
sperren. Sourcecode und reine Gegenfälle belegen diese geplante Grenze,
keine tatsächlichen künftigen API- oder Serverenden.

## Was bisher beobachtet wurde – und was offen bleibt

Die [Transportakte](../Project_Planning/SQL_SERVER_2025_AI_VECTOR_TRANSPORT_REVIEW.md)
enthält einen bekannten äußeren Prozessabschluss und einen unvollständig
beendeten Sessionreader. Der ursprüngliche konkrete Exceptiontyp wurde dort
nicht erfasst. Der jetzt dokumentierte Typmismatch ist ein überprüfbarer
Sourcebefund; er beweist nicht rückwirkend die tatsächliche Fehlerursache.
Die alte UNKNOWN-Welle bleibt gestoppt.

Dieser [Sessionreader-Schnitt](../Project_Planning/SQL_SERVER_2025_AI_SESSION_READER_REVIEW.md)
ist SOURCE_ONLY: acht projektierte Typ-/Getterbindungen und neue reine
Gegenfälle. Er führt keine Kompilierung, CLR-/Driver-/SQL-/Containerprobe aus.
VECTOR-Roundtrip, NULL-/Dimensionskontrolle, SNI/TDS und vollständige
Runtime-/TSK-004-Abnahme bleiben `NOT_ESTABLISHED`. Für die separate
Einordnung von Engine, Compatibility Level und Clienttransport siehe die
[VECTOR-Kompatibilitätslesehilfe](SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY.md).

## Quellen

Quellenabgleich vom 13.10.2026, `SRC-120` im
[Quellenregister](../Research/SOURCE_REGISTER.md). Weitere Primärverträge:
[DB_ID](https://learn.microsoft.com/en-us/sql/t-sql/functions/db-id-transact-sql?view=sql-server-ver17),
[DB_NAME](https://learn.microsoft.com/en-us/sql/t-sql/functions/db-name-transact-sql?view=sql-server-ver17),
[SERVERPROPERTY](https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver17),
[CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17),
[sys.dm_os_host_info](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-host-info-transact-sql?view=sql-server-ver17),
[sys.databases](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-ver17).
Dokumentation beschreibt Typverträge; tatsächliche serverseitige Resultattypen
und Driverreaktionen brauchen einen eigenen später zugelassenen Beleg.
