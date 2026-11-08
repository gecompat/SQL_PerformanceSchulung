# STL-002 – Entwurf für In-Row, Row-Overflow und LOB

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `STL-002` – identische Nutzdaten in drei Heap-Speicherprofilen |
| Quellen | `SRC-002`, `SRC-136`, `SRC-140`, `SRC-141` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Aussagegrenze

Der Entwurf hält die fachlichen Nutzdaten und deren vollständige Ergebnismenge
konstant, während die Tabellenstruktur dieselbe 6.000-Byte-Zeichenfolge als
In-Row-Variable, Row-Overflow-Variable oder `varchar(max)`-LOB speichert. Die
Allocation-Unit-Zuordnung muss später am SQL-Server-Build bestätigt werden;
Datentyp und plausible Zeilenbreite allein sind kein Enginebefund. Die drei
Profiles liefern außerdem keine allgemeine Aussage, dass Overflow- oder
LOB-Zugriffe stets mehr Reads oder langsamer seien.

Die Page-and-Extent-Architekturdokumentation (`SRC-002`) beschreibt maximal
8.060 Byte In-Row-Daten samt Overhead. Wenn eine variable Zeile diese Grenze
überschreitet, verschiebt SQL Server eine oder mehrere variable Spalten,
beginnend bei den breitesten, in `ROW_OVERFLOW_DATA`; der In-Row-Datensatz
enthält einen 24-Byte-Zeiger. `varchar(max)` fällt unter Large-Value-Semantik;
`large value types out of row = 1` erzwingt für neu eingefügte Werte die
Out-of-Row-Ablage mit einem 16-Byte-Zeiger. Das Ändern der Option konvertiert
vorhandene Werte nicht sofort. Die Fixture verwendet daher frische, leere
Tabellen und setzt die Option vor dem Laden.

## Gemeinsames Tupeloracle und Fixture

Alle drei eigenständigen Tabellen sind nicht partitionierte Heaps ohne
Sekundärindizes, Kompression, Updates oder Deletes. Jede enthält genau 2.000
Zeilen mit `RowId` von 1 bis 2.000. Für jede `RowId` `r` gilt exakt:

```text
Payload(r) = RIGHT(REPLICATE('0', 10) + CONVERT(varchar(10), r), 10)
             + REPLICATE('P', 5990)
Padding(r) = REPLICATE('X', 3000) -- nur im ROW_OVERFLOW-Profil
```

`Payload(r)` enthält damit den zehn Zeichen langen, mit Nullen aufgefüllten
Dezimalwert und 5.990 `P`-Zeichen, insgesamt 6.000 ASCII-Bytes. Im
`ROW_OVERFLOW`-Profil ist `Padding(r)` genau 3.000 ASCII-`X`-Bytes. ASCII
stellt sicher, dass Zeichen- und Byte-Länge gleich sind. Das vollständige
Solltupeloracle pro Profil ist für jedes `r = 1..2000`:

- `INROW`: `(r, Payload(r))`;
- `ROW_OVERFLOW`: `(r, Payload(r), Padding(r))`;
- `LOB`: `(r, Payload(r))`.

Die Oracles vergleichen vollständige Tupel einschließlich Multiplizitäten.
Für den mengenweisen Vergleich werden sie kanonisch nach `RowId` sortiert;
das behauptet keine Reihenfolge der SQL-Ergebnisse. Eine spätere Abfrage, die
eine stabile Ausgabeordnung benötigt, muss `ORDER BY RowId` ausdrücklich
enthalten. In allen Profilen gelten `COUNT(*) = 2000` und für jede Zeile
`DATALENGTH(Payload) = 6000`; im Overflow-Profil kommt
`DATALENGTH(Padding) = 3000` hinzu.

| Profil | Spaltendeklaration und Setup | Erwartete Struktur, noch empirisch zu bestätigen |
|---|---|---|
| `INROW` | `RowId int NOT NULL`, `Payload varchar(6000) NOT NULL`; kein zusätzliches Padding | 6.000 Payload-Bytes plus Schlüssel und Zeilenoverhead bleiben unter 8.060 Bytes; Payload erwartet in `IN_ROW_DATA` |
| `ROW_OVERFLOW` | dieselben `RowId`-/`Payload`-Werte und -Typen, zusätzlich `Padding char(3000) NOT NULL` aus ASCII-`X` | Die Zeile überschreitet die In-Row-Grenze; Payload ist die einzige variable Spalte und wird deshalb als zu verschiebender Kandidat erwartet. SQL Server soll sie nach `ROW_OVERFLOW_DATA` verschieben und einen 24-Byte-Zeiger im In-Row-Datensatz halten |
| `LOB` | `RowId int NOT NULL`, `Payload varchar(max) NOT NULL`; frische Tabelle, danach `sp_tableoption` mit `large value types out of row = 1`, erst dann Inserts | Neue Payload-Werte sollen in `LOB_DATA` liegen, mit 16-Byte-Zeiger im In-Row-Datensatz |

Das Overflow-Profil vergleicht gleiche fachliche `RowId`-/`Payload`-Nutzdaten,
aber nicht gleiche gesamte Tabellenzeilen: `Padding` ist ein ausdrücklich
sichtbarer Strukturhebel. Bei 3.000 festen Padding-Bytes, 6.000 variablen
Payload-Bytes und dem Schlüssel liegt die deklarierte Zeilenbreite vor
Zeilenoverhead über 8.060 Byte. Da `Payload` die einzige variable Spalte ist,
ist sie der vorgesehene Verschiebekandidat; die konkrete Allocation-Unit-
Zuordnung bleibt zu qualifizieren. Die Ergebnisprojektion der drei
Vergleichsabfragen bleibt `RowId, Payload`; vollständige Oracles werden
unabhängig davon gegen die jeweilige Fixture einschließlich Padding geprüft.

## Struktur- und Messoracles

Für jeden Heap (`index_id = 0`) werden die Allocation-Unit-Typen und
Seitenzahlen später mit `sys.dm_db_index_physical_stats` erfasst. Das
Soll-Orakel ist:

- in jedem Profil existiert `IN_ROW_DATA`;
- `INROW` besitzt keine zugehörige `ROW_OVERFLOW_DATA`- oder `LOB_DATA`-Einheit
  mit Nutzseiten;
- `ROW_OVERFLOW` besitzt `ROW_OVERFLOW_DATA` mit Nutzseiten und keine
  `LOB_DATA`-Nutzseiten;
- `LOB` besitzt `LOB_DATA` mit Nutzseiten und keine
  `ROW_OVERFLOW_DATA`-Nutzseiten.

`sys.dm_db_partition_stats` liefert ergänzende Zähler
`in_row_data_page_count`, `row_overflow_used_page_count` und
`lob_used_page_count`. Diese zählen Seiten je Partition, nicht die exakte
Spaltenzuordnung; Zähler können auf gecachten Systemtabellenwerten beruhen.
Abweichungen von der erwarteten Allocation-Unit-Zuordnung sind ein
Qualifikationsbefund und dürfen nicht als erfolgreiches Orakel umgedeutet
werden. Zugriffsrechte beider DMVs sind vor der späteren Ausführung anhand des
Zielbuilds festzulegen (`SRC-136`, `SRC-140`).

Eine separate spätere Leseprobe kann dieselbe vollständige Projektion unter
`SET STATISTICS IO ON` lesen und `logical reads` sowie `lob logical reads`
pro Profil protokollieren. Die drei Messungen sind empirische Werte der
konkreten Version, Datenbank, Cache- und Planbedingungen. Es gilt keine
vorab festgelegte numerische Mehrlese-Assertion, kein erzwungener Plan und
keine allgemeine Performanceaussage. Das bloße Auftreten einer LOB-Spalte
beweist keine bestimmte `lob logical reads`-Zahl.

## Cleanup- und Qualifikationsgrenze

Die spätere Demo benötigt einen vollständigen, markergebundenen
Setup-/Cleanupvertrag für genau ihre drei Fixturetabellen. Die LOB-Option ist
tabellenbezogener Zustand; die verworfenen Tabellen werden einschließlich
dieser Option entfernt. Inserts laufen ausschließlich in neuen, eigens
markierten Tabellen. Fehlerpfade müssen bereits angelegte Tabellen entfernen
und dürfen keine fremden Objekte verändern. Der konkrete Cleanup ist vor einer
SQL-Ausführung separat zu qualifizieren.

Noch offen sind Enginevalidierung der 8.060-Byte-Grenze und der tatsächlichen
Allocation-Units, Abgleich der Metadaten-/DMV-Berechtigungen für den
Zielbuild, der vollständige Demo- und Cleanupvertrag sowie spätere
Laufzeitfreigabe. Dieser Entwurf autorisiert keine SQL-, Lab- oder
Performanceausführung und ersetzt keine menschliche oder technische Abnahme.

## Quellenbindung

`SRC-002` bindet Page-, In-Row-, Row-Overflow- und LOB-Pointer-Semantik.
`SRC-136` beschreibt partitionale Seitenzähler für die drei Speicherbereiche.
`SRC-140` bindet Allocation-Unit-Zeilen und physische Heapdiagnostik.
`SRC-141` dokumentiert, dass `large value types out of row = 1` neue
`varchar(max)`-Werte out-of-row mit einem 16-Byte-Zeiger speichert, während
Bestandswerte erst bei späterer Änderung gemäß der neuen Option umgelagert
werden. Die Einstellung benötigt `ALTER`-Berechtigung auf der Tabelle.
`SET STATISTICS IO` stellt `logical reads` und `lob logical reads` getrennt
dar; daraus folgt kein vorbestimmter Mehrlese- oder Leistungseffekt. Die
Primärquellen stehen im
[Quellenregister](../Research/SOURCE_REGISTER.md#in-row-row-overflow-und-lob--stl-002).
