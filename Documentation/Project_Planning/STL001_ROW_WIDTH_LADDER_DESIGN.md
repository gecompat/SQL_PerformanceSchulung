# STL-001 – Entwurf für eine Zeilenbreitenleiter

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `STL-001` – feste, variable und nullable Spalten schrittweise ergänzen |
| Quellen | `SRC-002`, `SRC-140` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Aussagegrenze

Der statische Entwurf legt vier kumulative Heapprofile mit identischer
Zeilenzahl fest. Jede Stufe ergänzt genau eine vorher definierte Spalte:
eine feste Zeichenfolge, eine variable Zeichenfolge mit wiederkehrenden
Längen oder eine nullable variable Zeichenfolge mit kontrollierter
NULL-Verteilung. Vollständige Ergebnisoracles, `DATALENGTH`-Verteilungen,
Recordgrößen und Seitenbeobachtungen bleiben unterscheidbare Evidenzen.

Die Page-and-Extent-Dokumentation beschreibt 8-KiB-Seiten, den 96-Byte-
Seitenheader, einen 2-Byte-Slot pro Zeile und die Grenze von 8.060 Bytes für
In-Row-Daten und Overhead. Die Heap-Schätzmethode gibt eine Rechenbasis für
Fixed-/Variable-Daten, NULL-Bitmap, Recordheader und Slot Array. Die
Schätzwerte unten sind daraus abgeleitete Näherungen für genau dieses Fixture;
sie sind keine gemessenen Seitengrößen, keine Aussage über Page Density und
keine Performanceprognose.

## Gemeinsames synthetisches Grundprofil

Jede der vier eigenständigen Tabellen ist ein Heap ohne sekundäre Indizes,
Kompression, LOB-Daten, Deletes oder Updates. Sie enthält dieselben 100.000
synthetischen Schlüssel `RowId` von 1 bis 100.000 und `GroupId tinyint` von
0 bis 99, abgeleitet als `(RowId - 1) % 100`. Jeder Gruppenwert kommt damit
1.000-mal vor. ASCII-Fixturwerte halten Byte- und Zeichenlänge gleich. Die
Profile werden frisch befüllt; es finden keine späteren Zeilenvergrößerungen
statt, die Forwarded Records erzeugen könnten.

## Kumulative Profile und Quelldatenoracles

| Profil | Spalten zusätzlich zum Grundprofil | Verteilung und erwartetes Oracle |
|---|---|---|
| `BASE` | keine | 100.000 vollständige Tupel; je 1.000 Zeilen pro `GroupId` |
| `FIXED_100` | `FixedBlock char(100) NOT NULL` | Jeder Datensatz enthält 100 ASCII-`F`-Bytes; `DATALENGTH=100` |
| `VARIABLE_MIX` | `VariableBlock varchar(200) NOT NULL` | Für `RowId % 5` = 0, 1, 2, 3, 4 gelten der Reihe nach Längen 0, 25, 50, 100 und 200; jeder Wert besteht aus so vielen ASCII-`V`-Bytes. Exakt 20.000 je Länge, Mittelwert 75 Byte |
| `NULLABLE_MIX` | `NullableBlock varchar(100) NULL` | Bei `RowId % 5 = 0` exakt 20.000 Werte aus 80 ASCII-`N`-Bytes; sonst 80.000 `NULL`-Werte |

Für eine beliebige `RowId` `r` von 1 bis 100.000 gelten die vollständigen
Spaltenformeln:

```text
GroupId(r) = (r - 1) % 100
FixedBlock(r) = REPLICATE('F', 100)
VariableLength(r) = CASE r % 5 WHEN 0 THEN 0 WHEN 1 THEN 25 WHEN 2 THEN 50
                              WHEN 3 THEN 100 ELSE 200 END
VariableBlock(r) = REPLICATE('V', VariableLength(r))
NullableBlock(r) = CASE WHEN r % 5 = 0 THEN REPLICATE('N', 80) ELSE NULL END
```

Die vollständigen Solltupel je Profil sind für alle `r = 1..100000`,
kanonisch aufsteigend nach `RowId`:

- `BASE`: `(r, GroupId(r))`;
- `FIXED_100`: `(r, GroupId(r), FixedBlock(r))`;
- `VARIABLE_MIX`: `(r, GroupId(r), FixedBlock(r), VariableBlock(r))`;
- `NULLABLE_MIX`: `(r, GroupId(r), FixedBlock(r), VariableBlock(r), NullableBlock(r))`.

Die kanonische Sortierung dient nur dem Vergleich, nicht als Abfragereihenfolge.
Sie definiert für jede Tabelle alle Spaltenwerte, Nullwerte, Leerstrings und
Multiplizitäten. Damit lassen sich gemeinsam vorhandene Spalten zwischen den
Stufen direkt vergleichen. Die 100.000 `RowId`-Werte sind eindeutig; jeder
`GroupId`-Wert von 0 bis 99 kommt in jedem Profil genau 1.000-mal vor.

Die exakten `DATALENGTH`-Häufigkeiten sind:

| Profil/Spalte | Länge | Häufigkeit |
|---|---:|---:|
| `FIXED_100.FixedBlock` | 100 | 100.000 |
| `VARIABLE_MIX.VariableBlock` | 0 | 20.000 |
| `VARIABLE_MIX.VariableBlock` | 25 | 20.000 |
| `VARIABLE_MIX.VariableBlock` | 50 | 20.000 |
| `VARIABLE_MIX.VariableBlock` | 100 | 20.000 |
| `VARIABLE_MIX.VariableBlock` | 200 | 20.000 |
| `NULLABLE_MIX.VariableBlock` | 0 | 20.000 |
| `NULLABLE_MIX.VariableBlock` | 25 | 20.000 |
| `NULLABLE_MIX.VariableBlock` | 50 | 20.000 |
| `NULLABLE_MIX.VariableBlock` | 100 | 20.000 |
| `NULLABLE_MIX.VariableBlock` | 200 | 20.000 |
| `NULLABLE_MIX.NullableBlock` | 80 | 20.000 |
| `NULLABLE_MIX.NullableBlock` | `NULL` (kein Längenwert) | 80.000 |

Für jede Tabelle müssen `COUNT(*) = 100.000`, alle vollständigen Solltupel und
die `RowId`-Multiplizitäten mit dem deterministischen Generatororacle
übereinstimmen. Alle `DATALENGTH`-Häufigkeiten müssen den Tabellenwerten
entsprechen; alleinige Zeilenzahlen reichen nicht.

## Rechenmodell und Beobachtung

Die Heap-Schätzmethode verwendet für die Datenzeile
`Fixed_Data_Size + Variable_Data_Size + Null_Bitmap + 4` und für jeden
Datensatz zusätzlich einen 2-Byte-Slot. Mit der exakten ASCII-Verteilung
ergibt sich das folgende Modell. Die variable Datengröße ist hier der
Fixturmittelwert, nicht die deklarierte Maximalbreite.

| Profil | Feste Spaltendaten | Variable Nutzdaten im Mittel | Spaltenzahl / variable Spalten | Modellierte Zeilengröße | Modellierte Zeilen pro Seite |
|---|---:|---:|---:|---:|---:|
| `BASE` | 5 B | 0 B | 2 / 0 | 12 B | 578 |
| `FIXED_100` | 105 B | 0 B | 3 / 0 | 112 B | 71 |
| `VARIABLE_MIX` | 105 B | 75 B | 4 / 1 | 191 B | 41 |
| `NULLABLE_MIX` | 105 B | 91 B | 5 / 2 | 209 B | 38 |

Die Rechnung verwendet `Null_Bitmap = 2 + floor((Num_Cols + 7) / 8)`;
`Variable_Data_Size = 2 + 2 * Num_Variable_Cols + mittlere variable Nutzbytes`
und `Row_Size = Fixed_Data_Size + Variable_Data_Size + Null_Bitmap + 4`.
Damit sind die mittleren variablen Datengrößen 79 Byte für `VARIABLE_MIX`
(75 Nutzbytes plus 4 Byte Verwaltungsaufwand) und 97 Byte für `NULLABLE_MIX`
(91 Nutzbytes plus 6 Byte Verwaltungsaufwand). Die NULL-Bitmap beträgt in
allen vier Profilen 3 Byte. Die modellierten Zeilen pro Seite runden
`8096 / (Row_Size + 2)` ab; sie sagen keine exakte reale Seitenauslastung
voraus. Alle Profile liegen weit unter der 8.060-Byte-In-Row-Grenze und testen
daher keinen Row-Overflow-Fall.

Bei einer später separat freigegebenen Engineprüfung kann
`sys.dm_db_index_physical_stats` je Heap und Partition im Modus `DETAILED`
`page_count`, `record_count`, `avg_record_size_in_bytes` und
`avg_page_space_used_in_percent` erfassen. Die Routine liest alle Seiten und
nimmt eine IS-Sperre; ihre Objektberechtigungen und Laufzeitwirkung sind vor
Ausführung zu prüfen. Für einen Heap muss `index_id=0` und `IN_ROW_DATA`
ausgewertet werden. Der mittlere Recordwert ist nicht gleich der Nutzdatenbreite;
`record_count` ersetzt `COUNT(*)` und das Tupeloracle nicht. Abgeleitete
logische Zeilen pro belegter Seite werden als Mittelwert benannt, nicht als
gleichmäßige Seitenbelegung.

## Spätere Gates

Vor einer Umsetzung sind die Formeln und Expected Values unabhängig
nachzurechnen, der Generator am tatsächlichen SQL-Server-Verhalten zu prüfen,
Version und Berechtigungen für die DMF zu qualifizieren und ein vollständiger
Demo-/Setup-/Cleanupvertrag sowie ein Methodenreview zu erstellen. Dieser
Entwurf ist nicht katalogisiert und nicht ausgeführt; er behauptet keine
allgemeine Page Density, Leistung oder Ressourcenaussage. Menschliche
Generalprobe bleibt ausgeschlossen.

`SRC-002` dokumentiert 8-KiB-Seiten, den 96-Byte-Seitenheader, 2-Byte-Slot
Array-Elemente und die 8.060-Byte-Grenze. `SRC-140` bindet die Heap-
Größenschätzung und `sys.dm_db_index_physical_stats` zusammen. `DETAILED`
scannt alle Seiten und die Funktion nimmt unabhängig vom Modus eine
Intent-Shared-Sperre. Für die ausgewählte Heapmessung bleiben daher Rechte,
Ressourcenwirkung und zulässiger Modus vor einer späteren Runtimephase zu
qualifizieren. Die vollständigen Quellen stehen im
[Quellenregister](../Research/SOURCE_REGISTER.md).
