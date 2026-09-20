# QRY-006 – Detailreview NULL-Semantik von `NOT IN` und `NOT EXISTS`

| Merkmal | Wert |
|---|---|
| Status | `DECIDED_PLANNING` |
| Stand | 2026-09-19 |
| Kandidat | `QRY-006` – NULL-Semantik bei Anti-Mengen |
| Safety | `GREEN` |
| Umsetzung | noch nicht beauftragt; dieses Dokument ist kein Demo- oder Runtime-Artefakt |

## 1. Zweck und Statusgrenze

Der Planungsschnitt legt den fachlichen Ergebnisvertrag für eine spätere,
synthetische Einzel-Session-Demo fest. Er ergänzt die Kandidatenanalyse, ohne
einen Demo-Katalogeintrag, ein Szenario, ein Manifest oder ein Inventar zu
erzeugen. `QRY-006` bleibt bis zu einem eigenen Implementierungsschnitt und
den dann erforderlichen Laufnachweisen `PLANNED`.

Die Kernaussage betrifft ausschließlich die dreiwertige logische Auswertung.
Sie enthält keine Behauptung über Performance, Indizes oder eine konkrete
Planform.

## 2. Quellengebundene Semantik

Dokumentiert durch `SRC-069`: Liefert die Unterabfrage von `NOT IN` ein
`NULL`, kann der Vergleich für nicht passende Parent-Werte `UNKNOWN` ergeben.
Eine `WHERE`-Bedingung gibt nur `TRUE` weiter; deshalb ist die ungefilterte
`NOT IN`-Abfrage in der festgelegten Gegenprobe leer.

Dokumentiert durch `SRC-070`: `EXISTS` prüft, ob die korrelierte Unterabfrage
Zeilen liefert. Die Negation `NOT EXISTS` gibt einen Parent-Wert weiter, wenn
keine passende Child-Zeile existiert.

Dokumentiert durch `SRC-071`: `NULL` und `UNKNOWN` gehören zur dreiwertigen
Logik. Die Ergebniserklärung bleibt auf diese logische Grenze beschränkt.

## 3. Synthetischer Ergebnisvertrag

Die spätere Demo verwendet ausschließlich eine kleine, synthetische
Parent-/Child-Menge. Die Parent-Menge enthält die Schlüssel `1`, `2` und `3`.
Die Child-Menge enthält genau zwei Zeilen: eine passende Referenz auf Parent
`1` und **exakt ein** `NULL` im Vergleichsschlüssel. Weitere `NULL`-Werte,
Duplikate oder fachliche Nebendaten gehören nicht in diesen ersten Schnitt.

Die drei Abfragen und ihre erwarteten Mengen sind verbindlich:

| Abfrageform | erwartete Ergebnismenge |
|---|---|
| ungefiltertes `NOT IN (SELECT ChildKey ...)` | leer |
| korreliertes `NOT EXISTS` | `{2, 3}` |
| `NOT IN (SELECT ChildKey ... WHERE ChildKey IS NOT NULL)` | `{2, 3}` |

`NOT EXISTS` und das auf `IS NOT NULL` gefilterte `NOT IN` müssen dieselbe
explizite Anti-Menge `{2, 3}` liefern. Die spätere Ergebnissicherung vergleicht
die Mengen unabhängig von einer Ausführungsdarstellung.

## 4. Spätere Demo-Grenze

Ein späterer, separat freizugebender Implementierungsschnitt bleibt `GREEN`
und verwendet genau eine Session im Pfad `TSQL_TESTDB`. Die vorgesehene
Versions- und Compatibility-Level-Matrix ist:

| SQL Server | Compatibility Level | Erwartung |
|---|---:|---|
| 2019 | 150 | Ergebnisvertrag prüfen |
| 2022 | 160 | Ergebnisvertrag prüfen |
| 2025 | 170 | Ergebnisvertrag prüfen |

Die Semantikgrenze ist editions- und betriebssystemunabhängig. Eine spätere
Demo muss Setup und Cleanup markergebunden sowie idempotent gestalten; Cleanup
entfernt ausschließlich die durch den eigenen Marker erzeugten synthetischen
Objekte. Sie darf weder fremde Daten noch globale Instanzzustände verändern.

## 5. Abnahme und Folgearbeit

Vor einer Umsetzung sind ein eigener Demo-Vertrag, Ergebnisassertionen,
statische Prüfung und die Runtime-Matrix zu erstellen. Ein erfolgreicher
Planungsschnitt ist weder ein Runtime-Nachweis noch eine Freigabe für
`READY_FOR_USER`. Es bestehen keine Anforderungen an `SQL_Server_Lab` und
keine Erweiterung bestehender DGN-Artefakte.
