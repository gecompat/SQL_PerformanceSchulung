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
einem eindeutigen Clustered Key `RowId`, einem Selektivitätsschlüssel
`FilterBand` und `Payload char(200)`. Jede Frequenzgruppe wird deterministisch
über den gesamten `RowId`-Bereich verteilt; zusammenhängende Gruppen am
Tabellenanfang würden den Clustered-Zugriff ungewollt begünstigen.

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

Die 12 Frequenzen ergeben zusammen genau 100.000 Zeilen. Der spätere Fixture-
Generator muss Verteilung und Counts vor jeder Messung vollständig
attestieren; diese Entwurfsrechnung ist kein Enginebefund.

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

Für jedes Band ist die erwartete Trefferzahl tabellarisch festgelegt; die
Korrektheitsabnahme vergleicht zusätzlich die vollständigen Tupel
`(RowId, FilterBand, Payload)` zwischen `BASE`, `LOOKUP` und `COVERING`.
Eine gleiche Zeilenzahl genügt nicht. Die gemessene tatsächliche Zeilenzahl
und der vollständige Zeileninhalt müssen dem Oracle entsprechen.

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
Lookup- und Compilesemantik. Es erfolgen keine SQL-/DMV-Läufe und keine
menschliche Generalprobe.
