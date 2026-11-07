# IDX-005 – Entwurf zum Prüfen überlappender Missing-Index-Vorschläge

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `IDX-005` – Vorschläge prüfen, zusammenführen oder begründet verwerfen |
| Quellen | `SRC-032`, `SRC-149`, `SRC-012` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Lernfrage und Aussagegrenze

Eine Missing-Index-Anforderung ist eine vor der Ausführung erzeugte
Optimiererschätzung für eine einzelne Abfrage. Sie ist weder ein getesteter
Vorteil noch ein DDL-Auftrag. Der Entwurf vergleicht zwei synthetische
Abfragen, erfasst die tatsächlich von der Zielengine ausgegebenen Requests
und bewertet danach Überschneidungen, vorhandene Strukturen, Schlüsselreihen-
folge, INCLUDE-Breite und DML-Auswirkungen.

Es gibt keine statische Assertion, dass SQL Server einen bestimmten Request,
eine bestimmte Spaltenliste oder eine bestimmte Verbesserung vorschlagen
muss. Falls im qualifizierten Build kein verwendbares überlappendes Paar
auftritt, bleibt der Kandidatenclaim offen; Fixture, Query oder Sollbefund
werden nicht nachträglich angepasst, um einen gewünschten Request zu
erzwingen.

## Synthetische Basistabelle und Ergebnistupel

Die Request-Quelle ist eine markierte Heap-Tabelle ohne Clustered oder
Nonclustered Indexes und mit 100.000 deterministisch geladenen Zeilen. Sie
enthält `WorkItemId` von 1 bis 100.000,
`TenantId = ((WorkItemId - 1) % 100) + 1`,
`BlockNo = (WorkItemId - 1) / 100` als ganzzahligen Quotienten,
`Status = BlockNo % 100`, `CreatedBucket = BlockNo` und
`Amount = (WorkItemId * 37) % 100003`. Eine eigene kleine
`TenantProfile`-Tabelle enthält eine Zeile pro `TenantId`, einen eindeutigen
Clustered Index auf `TenantId` und `RegionCode = TenantId % 10`. Beide
Abfragen joinen auf diese Tabelle und filtern `RegionCode = 7`, damit die spätere Engineprobe
nicht nur auf einen trivialen Einzelheapplan angewiesen ist. Die Abfragen
projizieren ausschließlich die fünf vollständigen `WorkItem`-Spalten.
Weitere Foreign Keys oder externe Abhängigkeiten gibt es nicht. Das
Tupeloracle verwendet alle Tupel
`(WorkItemId, TenantId, Status, CreatedBucket, Amount)` in
`WorkItemId`-Reihenfolge.

Zwei Abfragen verwenden dieselben Projektionen und einen überlappenden
Prädikatskern:

```sql
-- Q1: Tenant-Gleichheit
SELECT w.WorkItemId, w.TenantId, w.Status, w.CreatedBucket, w.Amount
FROM dbo.WorkItem AS w
JOIN dbo.TenantProfile AS t ON t.TenantId = w.TenantId
WHERE w.TenantId = 17 AND t.RegionCode = 7;

-- Q2: derselbe Kern plus Bereichsprädikat
SELECT w.WorkItemId, w.TenantId, w.Status, w.CreatedBucket, w.Amount
FROM dbo.WorkItem AS w
JOIN dbo.TenantProfile AS t ON t.TenantId = w.TenantId
WHERE w.TenantId = 17 AND w.Status = 7 AND t.RegionCode = 7
  AND w.CreatedBucket BETWEEN 500 AND 599;
```

Nach der Generatorformel muss Q1 1.000 vollständige Tupel liefern: die
`WorkItemId`-Folge `17 + 100k` für `k = 0..999`. Q2 muss genau ein
vollständiges Tupel mit `WorkItemId = 50717` liefern. Diese Oracles gelten
unabhängig von Vorschlag, Index oder Plan.

## Request-Erfassung und Konsolidierung

Vor jeder Index-DDL werden für beide Abfragen die tatsächlichen
Missing-Index-Ausgaben des exakt gebundenen Basistabellenobjekts gesichert.
Das Snapshot muss Request- und Gruppenhandles, Datenbank-/Objektidentität,
Equality-, Inequality- und INCLUDE-Spalten sowie verfügbare Gruppenwerte
enthalten. Requestgruppen werden nur aus den DMV-Feldern verknüpft; ähnlich
aussehende Requests verschiedener Objekte oder Builds werden nicht
zusammengeführt. Da Index- oder Tabellenmetadatenänderungen die flüchtigen
Requests löschen können, erfolgt die Aufnahme vor dem Anlegen von
Vergleichsprofilen.

Der erwartete überlappende Kandidatenraum für die anschließende Designprüfung
ist:

- getrennte Variante Q1: Schlüssel `(TenantId)`, dazu `Status`,
  `CreatedBucket`, `WorkItemId` und `Amount` als INCLUDE;
- getrennte Variante Q2: Schlüssel `(TenantId, Status, CreatedBucket)`, dazu
  `WorkItemId` und `Amount` als INCLUDE;
- Konsolidierungskandidat: Schlüssel `(TenantId, Status, CreatedBucket)` und
  INCLUDE `(WorkItemId, Amount)`.

Der dritte Kandidat ist nur ein überprüfbarer Entwurf: der Schlüsselpräfix
`(TenantId)` kann Q1 adressieren; `Status` ergänzt die zweite
Equality-Bedingung und `CreatedBucket` den Q2-Bereich. Equality-Spalten
stehen vor der Inequality-Spalte. Die endgültige
Übernahme hängt jedoch von den tatsächlichen Requests, vorhandenen Indizes,
Query-Abdeckung und Indexbreite ab. Eine DMV-Ausgabe wird nicht ungeprüft als
`CREATE INDEX` übernommen. Der Basistabellen-Heap und gegebenenfalls bereits
vorhandene Indizes werden vor jeder DDL geprüft.

Microsoft dokumentiert, dass Missing-Index-Vorschläge keine Schlüsselreihen-
folge festlegen, INCLUDE-Breite nicht gegen Kosten abwägen, ähnliche
Empfehlungen erzeugen und vor Ausführung nicht getestet werden. Sie decken
nicht alle Indexarten oder triviale Pläne ab. Sollte die Zielengine trotz
des Joinprofils einen trivialen Plan verwenden oder deshalb keine Requests
erzeugen, bleibt die Gegenprobe unqualifiziert; es gibt keine spätere
Fixtureänderung allein zur Requesterzeugung. Schätzwerte bleiben
Optimiererannahmen; Requests sind nicht persistent und können durch Neustart
oder Metadatenänderungen verschwinden.

## DML- und Ergebnisgegenprobe

Für einen späteren Vergleich dienen drei neue, markergebundene Tabellenkopien
mit identischen Starttupeln: ohne zusätzliche Nonclustered Indexes, mit den
getrennten Kandidaten und mit dem konsolidierten Kandidaten. Nach getrenntem
Setup erhält jede Variante dieselbe begrenzte deterministische DML-Folge:

1. 100 neue synthetische IDs einfügen;
2. für IDs 2001 bis 2100 `Status = Status + 1` und
   `CreatedBucket = CreatedBucket + 1000` setzen;
3. für IDs 3001 bis 3100 `Amount = Amount + 1` setzen;
4. IDs 4001 bis 4100 löschen.

Die Inserts verwenden IDs 100001 bis 100100 und dieselben Generatorformeln
wie der Basissatz. Die vier DML-Gruppen sind disjunkt und über alle Profile
bytegleich vorgegeben.

Nach jedem Abschnitt werden betroffene Rowcounts und die vollständigen
sortierten Ergebnistupel zwischen Varianten verglichen. Die DML-Oracles
belegen nur identische fachliche Änderungen. Writes, CPU, Reads, Logbytes,
Speicherbedarf, Laufzeit und Wartungskosten sind spätere empirische Messwerte;
aus der Zahl der Indexe oder den Missing-Index-Kosten wird kein quantitativer
DML-Aufwand abgeleitet.

## Cleanup- und Qualifikationsgrenze

Die Request-Aufnahme erfolgt vor Änderungen an der Quelltabelle. Alle drei
Vergleichsprofile liegen unter exakten, eigenen Markern und benutzen eindeutige
Objekt-/Indexnamen. Fehlerpfade entfernen nur die eigenen Tabellen und deren
Indexes. Es werden weder vorhandene Projektindizes geändert noch
Requests anderer Datenbanken verarbeitet.

Vor einer späteren SQL-Ausführung bleiben Zielbuild, DMV-Rechte,
T-SQL-Kompilierung, tatsächliche Vorschlagsgruppe, robuste Cleanuppfade und
ein enges Laufzeit-/Ressourcenbudget zu qualifizieren. Ein fehlendes oder
nicht überlappendes Requestpaar ist ein Qualifikationsbefund, kein Anlass zum
Retry mit verändertem Fixture. Dieser Entwurf autorisiert keine
SQL-/Runtimeausführung, Indeximplementierung, Plan- oder Performanceabnahme
und keine menschliche Generalprobe.

## Quellenbindung

`SRC-032` dokumentiert Grenzen und fachliche Prüfung von Vorschlägen.
`SRC-149` bindet DMV-Felder, Gruppen und ihre flüchtige Lebensdauer.
`SRC-012` bleibt maßgeblich für Key-Reihenfolge, INCLUDE und Indextrade-offs.
Die Primärquellen stehen im
[Quellenregister](../Research/SOURCE_REGISTER.md#missing-index-request-dmvs--idx-005).
