# IDX-004 – Entwurf für Lookup und Treffermenge

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `IDX-004` – Lookup-Kippkurve und abdeckender Index |
| Quellen | `SRC-012`, `SRC-125`, `SRC-137` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Grenze

Wie verändert eine steigende Zahl passender Zeilen den tatsächlich gewählten
Zugriff, wenn ein nicht abdeckender Nonclustered Index für jeden Treffer eine
fehlende Nutzspalte aus dem Clustered Index nachladen muss? Wie unterscheiden
sich Ergebnisse und Planbeobachtung, wenn dieselbe Nutzspalte im Index
enthalten ist?

Der Entwurf sucht keinen allgemein gültigen Prozentsatz, ab dem SQL Server
einen Index Seek mit Key Lookups durch einen Scan ersetzt. Ein möglicher
Übergang ist nur ein Befund für die konkrete Fixture, Build-, Statistik- und
Compilekonstellation. Ebenso sind `Key Lookup`, `Index Scan`, `Clustered Index
Scan` und `Seek` mögliche Beobachtungen, keine Planpflicht.

## Kontrollierte Fixture

Die vorgeschlagene Tabelle `LookupBand` hat 100.000 synthetische Zeilen mit
`RowId int` als eindeutigem Clustered Key, `FilterBand int` und
`Payload char(200)`. Der Generator verwendet die nullbasierte Slotnummer `s`
von 0 bis 99.999 und ordnet ihr die Zeilen-ID
`RowId(s) = ((37 * s) mod 100000) + 1` zu. Da 37 und 100.000 teilerfremd
sind, ist dies eine Permutation: jede `RowId` von 1 bis 100.000 entsteht genau
einmal. Die Slotintervalle unten legen `FilterBand` fest; dadurch liegen die
Gruppen reproduzierbar über den RowId-Bereich verteilt. Für jede Zeile gilt
`Payload = REPLICATE('X', 200)` (genau 200 ASCII-Zeichen; Speicherung in
`char(200)`). Der konstante Payload isoliert die Ergebniskorrektheit und
Datensatzbreite, ist aber kein repräsentativer Anwendungswert.

| `FilterBand` | Treffer | Tabellenanteil |
|---:|---:|---:|
| 1 | 10 | 0,01 % |
| 2 | 50 | 0,05 % |
| 3 | 100 | 0,10 % |
| 4 | 250 | 0,25 % |
| 5 | 500 | 0,50 % |
| 6 | 1.000 | 1 % |
| 7 | 2.000 | 2 % |
| 8 | 5.000 | 5 % |
| 9 | 10.000 | 10 % |
| 10 | 20.000 | 20 % |
| 11 | 40.000 | 40 % |
| 99 | 21.090 | außerhalb der Selektivitätsleiter |

Die 12 Frequenzen ergeben zusammen genau 100.000 Zeilen. Die vollständigen
Slotintervalle `[Start, Ende]` (beide Grenzen eingeschlossen) lauten:

| `FilterBand` | Slotintervall |
|---:|---:|
| 1 | 0–9 |
| 2 | 10–59 |
| 3 | 60–159 |
| 4 | 160–409 |
| 5 | 410–909 |
| 6 | 910–1.909 |
| 7 | 1.910–3.909 |
| 8 | 3.910–8.909 |
| 9 | 8.910–18.909 |
| 10 | 18.910–38.909 |
| 11 | 38.910–78.909 |
| 99 | 78.910–99.999 |

Damit ist die Sollverteilung ohne Zufall, Laufzeit-Zahlenquelle oder
Interpretationsspielraum definiert. Ein späterer Generator muss vor einer
Ausführung die vollständige Bijektion, jeden Band-Count und den Payload prüfen;
dieser statische Entwurf ist kein Enginebefund.

## Vergleichsprofile und identische Abfrage

Für jedes `FilterBand` werden nacheinander drei Profile auf derselben
unveränderten Datengrundlage betrachtet:

| Profil | Sekundärer Index | Erwartete strukturelle Frage |
|---|---|---|
| `BASE` | kein zusätzlicher Nonclustered Index | Ergebnismengen- und Read-Baseline |
| `LOOKUP` | `(FilterBand)`; `Payload` fehlt | Wählt der Optimierer einen Zugriff mit Lookup, einen Indexscan oder einen Scan der Clustered Table? |
| `COVERING` | `(FilterBand) INCLUDE (Payload)` | Ändert Abdeckung den Plan, die Seitenarbeit oder die tatsächliche Lookup-Nutzung? |

Beide sekundären Indizes sind nicht eindeutig. Ihr Clustered Row Locator
`RowId` ist damit im Index verfügbar; `Payload` allein trennt die abdeckende
von der nicht abdeckenden Variante.

Es ist immer nur ein Vergleichsindex vorhanden. Die logische Abfrage bleibt
für alle Bänder und Profile gleich:

```sql
SELECT RowId, FilterBand, Payload
FROM dbo.LookupBand
WHERE FilterBand = @FilterBand
OPTION (RECOMPILE);
```

Die dokumentierte `RECOMPILE`-Semantik bindet jeden Lauf an den aktuellen
Wert von `@FilterBand`, statt einen zuerst kompilierten Plan als Vergleich
über die ganze Leiter vorauszusetzen. Die Compilekosten sind deshalb nicht
Teil einer behaupteten Ausführungszeitverbesserung; diese Designstufe macht
keinen Laufzeitclaim.

## Ergebnisoracle und Beobachtung

## Vollständiges Ergebnistupeloracle

Für ein Band `b` mit Slotintervall `[a_b, z_b]` lautet das vollständige Oracle
die Menge aller Tupel
`(RowId(s), b, REPLICATE('X', 200))` für `s = a_b..z_b`, für den Vergleich
kanonisch aufsteigend sortiert nach `RowId(s)`. Diese Definition umfasst alle drei projizierten Spalten,
jede Zeilenmultiplizität und den vollständigen Payloadinhalt. Sie gilt für
jedes Band einschließlich des Füllbands 99. Die Selektivitätsleiter selbst
wertet die Bänder 1 bis 11 aus; Band 99 füllt die restliche Tabelle auf und ist
kein zusätzlicher Leiterpunkt.

`RowId(s)` ist bijektiv. Zur unabhängigen Rückabbildung einer beliebigen
`RowId` auf ihren Soll-Slot gilt
`s = (((RowId - 1) * 72973) mod 100000)`, da 72.973 das multiplikative Inverse
von 37 modulo 100.000 ist. Damit folgt das Sollband einer Zeile eindeutig aus
dem resultierenden Slotintervall. Ein Oracle-Generator kann diese
Rückabbildung unabhängig vom Vorwärtslauf nutzen.

Für jedes getestete Band wird das vollständige Tupeloracle identisch
gegen `BASE`, `LOOKUP` und `COVERING` geprüft. Die kanonische Sortierung dient
nur dem mengenweisen Vergleich; die Abfrage verspricht keine Ergebnisreihenfolge.
Gleichheit von Zeilenzahl, Prüfsumme oder Bandverteilung allein genügt nicht;
vollständige Tupel und Duplikate müssen übereinstimmen.

Falls eine spätere Ausführung freigegeben wird, werden je Band und Profil
getrennt festgehalten:

- geschätzter und tatsächlicher Plan;
- tatsächlich gewählte Operatoren, geschätzte und tatsächliche Zeilen sowie
  Ausführungszahl von `Key Lookup`, falls vorhanden;
- statementbezogene Logical Reads und CPU-/Elapsed-Ausgabe;
- verwendetes Indexprofil, Kompilierungswert und tatsächlicher Build/
  Compatibility Level.

Ein `Key Lookup` ist nach Microsoft-Dokumentation mit `Nested Loops` gekoppelt;
eine hohe Ausführungszahl relativ zur Tabelle kann Anlass geben, einen
abdeckenden Index zu prüfen. Daraus folgt keine feste Selektivitätsgrenze oder
die Zusage, dass der Optimierer beim nächsten Leiterwert den Zugriff ändert.
Bleibt ein Übergang aus, ist das ein gültiges Ergebnis dieses Workloads und
keine fehlgeschlagene Demo.

## Gültigkeits- und Ausführungsgrenzen

Zielmatrix für einen späteren Vertrag: SQL Server 2019/Compatibility Level 150,
2022/160 und 2025/170. Keine dieser Versionen ist durch diesen Entwurf
kompiliert oder qualifiziert. Statistiken, Session-/Datenbankkontext,
Cachezustand und Messreihenfolge müssen im konkreten Methodenvertrag gebunden
werden. Kein `FORCESEEK`, `FORCESCAN` oder Indexhint wird als didaktische
Abkürzung verwendet.

Die Methode beurteilt weder Schreibkosten noch Update-/Insert-Last, Konkurrenz,
Langzeit-Cacheeffekte oder eine allgemeine optimale Indexwahl. Vor einer
Umsetzung sind ein markierter Demo-/Setup-/Cleanupvertrag, Version-/Buildpins,
Permissions, Fixturegenerator, unabhängiges Ergebnisoracle, Methodenreview und
konkrete Ausführungsfreigabe zu binden. `SRC-012` bindet Index- und
Selektivitätsgrundlagen, `SRC-125` die Plan-/Read-Erfassung und `SRC-137` die
Lookup- und Compilesemantik. `OPTION (RECOMPILE)` verwendet beim Kompilieren
den aktuellen Parameterwert; dies bindet den Entwurf an den jeweiligen
Leiterwert, beweist aber weder eine bestimmte Schätzung noch Planform oder
Ausführungszeit. Die aktuelle Microsoft-Indexdokumentation beschreibt den
Clustered Key als Row Locator nicht eindeutiger Nonclustered Indexes und
Included Columns als Möglichkeit, eine Abfrage abzudecken. Es erfolgen keine
SQL-/DMV-Läufe und keine menschliche Generalprobe.
