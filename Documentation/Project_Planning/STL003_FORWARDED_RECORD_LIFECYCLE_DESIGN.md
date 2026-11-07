# STL-003 – Entwurf für den Lebenszyklus weitergeleiteter Heapzeilen

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `STL-003` – Forwarded Records erzeugen, nachweisen und durch Heap-Rebuild zurücknehmen |
| Quellen | `SRC-013`, `SRC-145`, `SRC-146` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Aussagegrenze

Eine Vergrößerung variabler Zeilen in einem Heap kann Datensätze auf andere
Datenseiten verschieben und einen Forwarding Record am bisherigen Ort
hinterlassen. Dieser Entwurf trennt vollständige fachliche Tupel, physische
Forwarded-Record-Metadaten und operative Fetch-Zähler. Ein Heap-Rebuild bildet
die kontrollierte Rücknahme. Daraus folgt keine allgemeine Aussage über
Fragmentierung, Reads, Durchsatz oder Laufzeit.

## Fixture und vollständige Tupeloracles

Die spätere isolierte Demo verwendet genau einen nicht partitionierten Heap
ohne Indizes, Constraints, Trigger oder Kompression. Er enthält 1.000 Zeilen
mit `RowId` 1 bis 1.000 und einer variablen Spalte `Payload varchar(7000)`.
Der initiale Payload ist für jede Zeile eine deterministische 100-Byte-ASCII-
Zeichenfolge. Danach wird für alle 1.000 `RowId`-Werte der Payload auf genau
7.000 ASCII-Bytes vergrößert; der Präfix kodiert jeweils die `RowId`, der Rest
besteht aus `A`. Die Länge liegt unter der In-Row-Grenze einschließlich der
hier verwendeten Spalten und macht keinen LOB-Typ erforderlich.

Für den initialen Zustand kodieren die ersten sieben Payload-Bytes die
nullauf sieben Stellen aufgefüllte dezimale `RowId`; die übrigen 93 Bytes sind
`x`. Im vergrößerten Zustand bleiben dieselben sieben Präfixbytes erhalten,
gefolgt von 6.993 `A`-Bytes. Damit ist jeder Sollwert allein aus `RowId`
reproduzierbar.

Die drei fachlichen Oracles prüfen unabhängig:

1. Nach dem Setup: exakt 1.000 geordnete `(RowId, Payload)`-Tupel mit
   `DATALENGTH(Payload) = 100`.
2. Nach dem Update und vor dem Rebuild: exakt dieselben `RowId`-Werte und je
   die erwartete, zeilenabhängige 7.000-Byte-Zeichenfolge.
3. Nach dem Rebuild: unveränderte vollständige Tupel des zweiten Zustands.

`COUNT(*) = 1000` ist ein Zusatzcheck und ersetzt keinen Tupelvergleich.
Die Fixture setzt weder exakte physische Seitenzahlen noch die Anzahl
weitergeleiteter Zeilen vorab voraus. Ein unabhängiger Qualifikationsvorlauf
muss zeigen, dass das Update dieser konkreten Enginefixture tatsächlich
Forwarding erzeugt; ein abweichender Befund ist offen zu berichten.

## Physische und operative Evidenz

Für das exakt markierte Heapobjekt bindet jede Strukturaufnahme
`sys.dm_db_index_physical_stats` an die aktuelle Datenbank, `object_id`,
`index_id = 0`, Partition 1 und `DETAILED`. Vor dem Update muss
`forwarded_record_count = 0` sein. Nach der Vergrößerung muss der Zähler
größer als null sein. Nach `ALTER TABLE ... REBUILD` wird erneut null erwartet.
Ein positives physisches Orakel belegt Forwarding Records, nicht die Anzahl
fachlicher Zeilen und nicht deren Nutzung durch eine bestimmte Abfrage.

Vor einer gezielten Heap-Leseabfrage und unmittelbar danach wird
`forwarded_fetch_count` aus `sys.dm_db_index_operational_stats` mit demselben
Datenbank-, Objekt- und Heap-Scope erfasst. Nur eine positive Differenz darf
als beobachtete Forwarded Fetches dieses begrenzten Laufs beschrieben werden.
Es gibt keinen festen Sollwert. Ein fehlender, negativer oder durch Cache-
Entfernung beziehungsweise DDL nicht vergleichbarer Delta bleibt
`UNKNOWN`/nicht nachgewiesen; `forwarded_record_count` ersetzt den Fetchbeleg
nicht. Der Zähler ist nicht persistent und kein Leistungsmaß.

Die DETAILED-Physikaufnahme liest alle Seiten. Rechte, Build, Kosten und
Ausführbarkeit dieser Beobachtung bleiben vor dem Runtimeeinsatz zu
qualifizieren. Unabhängige T-SQL-Kompilierung und Versionsmatrix 2019–2025
sind offen.

## Rebuild-, Fehler- und Cleanupgrenze

`ALTER TABLE ... REBUILD` wird ausschließlich auf der neu angelegten,
exakt markierten Fixture ausgeführt. Danach müssen vollständige Nutzdaten
und Zeilenzahl erhalten sein und der physische Forwarded-Record-Zähler null
betragen. Der Rebuild verändert die physische Organisation; Seitenzahlen,
Fetch-Zähler, Reads, Laufzeit und Kosten werden nicht als Invarianten
behauptet. DDL kann operative Statistiken zurücksetzen, deshalb wird der
Fetch-Delta nicht über den Rebuild hinweg gebildet.

Setup und Cleanup besitzen den vollständigen Demo-Marker und exakte
Objektbindung. Fehlerpfade löschen ausschließlich das eigene Objekt; fremde
Objekte oder Datenbanken werden nicht verändert. Der spätere Vertrag muss
zusätzlich ausreichenden Speicher-/Lograum und einen engen Zeit-/Cleanuprahmen
festlegen, bevor irgendein SQL-Lauf zugelassen wird.

Dieser Offlineentwurf implementiert oder katalogisiert keine Demo und
autorisiert weder SQL-/Lab- noch Performanceausführung. Enginefixture,
Forwarding- und Fetch-Oracles, Berechtigungen, Buildmatrix, Cleanup und
Performancegrenzen bleiben offen. Keine menschliche Generalprobe.

## Quellenbindung

`SRC-013` beschreibt Heap- und Forwarding-Semantik. `SRC-145` bindet den
physischen `forwarded_record_count`, die Abweichung zwischen physischen
Records und logischer Zeilenzahl sowie `ALTER TABLE ... REBUILD` als
Heapwartung. `SRC-146` definiert `forwarded_fetch_count` und seine
Metadaten-Cachelebensdauer. Alle Details stehen im
[Quellenregister](../Research/SOURCE_REGISTER.md#heap-forwarding-lifecycle--stl-003).
