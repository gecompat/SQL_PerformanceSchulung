# IDX-003 – Entwurf für Key-Reihenfolge und INCLUDE

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Kandidat | `IDX-003` – Key-Reihenfolge, Left-Based Prefix und INCLUDE |
| Quellen | `SRC-012`, `SRC-136` |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Fragestellung und Grenze

Der Entwurf trennt zwei Fragen: Welche Abfragen verwenden eine Spalte als
Suchprädikat und profitieren möglicherweise von ihrer Position im Indexschlüssel?
Welche weiteren Spalten werden nur ausgegeben und können als nichtschlüsselbasierte
`INCLUDE`-Spalten den Zugriff abdecken? Die Microsoft-Indexleitlinie beschreibt
die Schlüsselreihenfolge und deren Anwendungsfälle; `INCLUDE`-Spalten liegen
auf der Blattebene. Die konkrete Planwahl und Wirkung bleiben empirisch.

Es wird weder ein Seek noch ein residualfreies Prädikat, eine kleinere
Indexgröße oder ein Performancevorteil als festes Ergebnis behauptet.

## Gemeinsame Fixture

Eine vorgeschlagene Tabelle `SearchFact` hat den eindeutigen, schmalen
Clustered Key `RowId`, die Attribute `TenantId`, `Status` und einen festen
Ausgabewert `Payload`. Die Fixture umfasst 120.000 Zeilen mit deterministisch
balancierter Verteilung: 100 Mandanten und 6 Statuswerte, je 200 Zeilen pro
Mandant-/Statuskombination. `Payload` enthält einen für jede Zeile
deterministischen, 64 Zeichen langen synthetischen Wert. Kein Skew oder
selektiver Spezialfall wird als repräsentativer Produktworkload ausgegeben.

Verglichen werden die folgenden sekundären, nicht eindeutigen
Nonclustered-Indexprofile jeweils allein auf derselben unveränderten Tabelle;
der Clustered Key und die Eindeutigkeitssemantik bleiben konstant. `RowId` ist
dadurch als Row Locator in jedem sekundären Index verfügbar und Teil der
vollständigen Ergebnistupel:

| Profil | Schlüssel | Nichtschlüsselspalten | Isolierte Frage |
|---|---|---|---|
| `IX_Tenant_Status` | `(TenantId, Status)` | `Payload` | Mandant vor Status |
| `IX_Status_Tenant` | `(Status, TenantId)` | `Payload` | Status vor Mandant |
| `IX_Tenant_Status_Payload` | `(TenantId, Status, Payload)` | keine | Ausgabeattribut als Schlüssel gegenüber `INCLUDE` |
| `BASE` | nur der konstante Clustered Index | – | gemeinsame Ergebnismengen-Baseline |

Jedes sekundäre Profil ist einzeln angelegt und vor dem nächsten Profil
entfernt. So kann kein konkurrierender Vergleichsindex die dokumentierte
Zugriffswahl verdecken. Seitenzählungen werden je Profil nach Build aus
`sys.dm_db_partition_stats` über alle zugehörigen Partitionen summiert. Der
Bericht unterscheidet genutzte von reservierten Seiten und hält die jeweilige
Berechtigungsanforderung fest. `row_count` bleibt ein Näherungswert, kein
Ergebnisoracle.

## Vier ausgerichtete Abfragefälle

Alle Abfrageprofile projizieren dieselben vollständigen Zeilen
`RowId, TenantId, Status, Payload`. Pro Fall werden die Ergebnistupel und
`RowId`-Multiplizitäten gegen `BASE` und jeden sekundären Index verglichen.
Die Ergebnismenge eines Falles muss unter allen Indexvarianten gleich sein;
die vier Fälle untereinander haben absichtlich unterschiedliche Filter.

| Fall | Prädikat | Geprüfte Indexfrage |
|---|---|---|
| `Q1` | `TenantId = 37` | beginnt die Schlüsselreihenfolge mit dem Mandanten? |
| `Q2` | `Status = 5` | beginnt die Schlüsselreihenfolge mit dem Status? |
| `Q3` | `TenantId = 37 AND Status = 5` | beide Gleichheitsprädikate; Schlüsselreihenfolge gegen gleiche Ergebnisoracles halten |
| `Q4` | `TenantId = 37 AND Status BETWEEN 4 AND 6` | Gleichheit gefolgt von Statusbereich gegen umgekehrte Reihenfolge und INCLUDE-Profil |

Die Sollmengen folgen direkt aus der festgelegten Verteilung: `Q1` hat 1.200
Zeilen, `Q2` 20.000, `Q3` 200 und `Q4` 600. Diese Zählwerte kontrollieren nur
die Fixture und werden vor einer späteren SQL-Umsetzung am konkreten Generator
zu verifizieren sein. Für jeden Fall gilt zusätzlich der vollständige Oracle
über `RowId` und alle projizierten Werte; gleiche Zeilenzahl allein genügt
nicht.

## Beobachtung und Abnahmegrenzen

Falls eine spätere Implementierung dafür freigegeben wird, werden geschätzter
und tatsächlicher Plan getrennt ausgewiesen. Seek-Prädikate,
Residual-Prädikate, Lookup/Abdeckung, Logical Reads sowie genutzte und
reservierte Indexseiten sind getrennte Beobachtungen. Keine Abfrage erzwingt
einen Indexhinweis, einen Seek, eine bestimmte Planform oder einen Grenzwert.
Ein tatsächlicher Seek wäre kein selbständiger Leistungsnachweis.

Die Korrektheitsabnahme besteht aus identischen vollständigen Ergebnistupeln
je Query-Fall und passender Zeilenmultiplizität. Die Indexgröße wird separat
als gemessene, partitionsaggregierte Seitenzahl berichtet. Schreibkosten,
Konkurrenz, Cachezustand und Laufzeitvariabilität sind nicht qualifiziert.
Vor einer Umsetzung bleiben ein eigener Demo-/Setup-/Cleanupvertrag,
Versions-/Berechtigungsprüfung, vollständiges SQL-Oracle, Methodenreview und
konkrete Ausführungsfreigabe erforderlich.

`SRC-012` bindet Indexstruktur und Key-Reihenfolge, `SRC-136` die
INCLUDE- und Seitennutzungsquellen. Der Entwurf ändert keine Lernziel- oder
Demo-ID, keinen Katalog und keine Runtime. Menschliche Generalprobe bleibt
ausgeschlossen.
