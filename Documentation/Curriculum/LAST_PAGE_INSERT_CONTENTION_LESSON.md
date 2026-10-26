# IDX-007: Einfügungen an einer heißen Indexseite einordnen

**Status:** kurze fachliche Erläuterung; keine neue Demo, kein Benchmark und
keine Runtimequalifikation.

## Was „Last-Page-Contention“ beschreibt

Wenn viele gleichzeitige Einfügungen denselben sequentiellen führenden
Indexschlüssel verwenden, gelangen neue Einträge häufig an dieselbe Randseite
des Indexes. Müssen gleichzeitig viele Worker genau diese im Buffer Pool
liegende Seite verwenden, kann ein exklusiver Page-Latch (`PAGELATCH_EX`) zum
Engpass werden. Ein Latch schützt kurzfristig eine In-Memory-Seitenstruktur;
er ist keine Transaktionssperre.

`PAGELATCH_EX` ist von `PAGEIOLATCH_EX` zu unterscheiden: Das erste Warten
betrifft die Synchronisierung einer Seite im Arbeitsspeicher, das zweite das
Warten auf eine Seiten-Ein-/Ausgabe. Ein `PAGELATCH_EX` allein zeigt noch
nicht, dass die letzte Seite eines bestimmten Indexes betroffen ist.
[Microsofts Diagnoseanleitung (SRC-072)](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/resolve-pagelatch-ex-contention) beschreibt
die Zuordnung des Wait-Resources zu Datenbank, Objekt und Index.

## Welche Beobachtung welche Frage beantwortet

- Ein positiver `leaf_insert_count` belegt erfasste Einfügungen, aber weder
  gleichzeitige Ausführung noch Latch-Konkurrenz.
- `page_latch_wait_count` und `page_latch_wait_in_ms` liefern indexbezogene
  Betriebszähler. Sie weisen ohne aktuelle Wait-Ressource keine einzelne Seite,
  Abfrage oder konkrete Insertphase nach. `page_io_latch_wait_*` beschreibt
  den getrennten I/O-Pfad.
- Eine Diagnose des Last-Page-Musters braucht tatsächliche `PAGELATCH_EX`-
  Waits, die sich während gleichzeitiger Aktivität derselben Zieldatenbank und
  desselben Indexes auf die betreffende Indexseite abbilden lassen. Fehlt diese
  Zuordnung, bleibt „Last Page“ eine Hypothese.

## Einordnung der Indexoption

`OPTIMIZE_FOR_SEQUENTIAL_KEY` ist ab SQL Server 2019 als Indexoption verfügbar.
Microsoft beschreibt sie als Engine-Optimierung, die bei hochkonkurrierenden
Einfügungen in einen sequentiellen Index den Durchsatz verbessern kann. Die
Option ist kein Beleg, dass die eigene Arbeitslast einen Last-Page-Engpass hat,
und keine Garantie für einen Leistungsvorteil. Ob sie hilft, muss für den
konkreten Workload gemessen werden.

Ein Wechsel zu verteilten Schlüsseln oder einem Heap verändert ebenfalls
Zugriffsmuster und Indexstruktur. Daraus folgt keine pauschale Empfehlung.
Eine quantitative Variante benötigt einen fairen, gleich belasteten
Vergleichsvertrag und eigene Messnachweise; diese kurze Notiz behauptet keinen.

## Prüffragen

1. Belegt ein positiver Insertzähler Last-Page-Contention? Nein; er belegt nur
   erfasste Einfügungen.
2. Reicht ein indexbezogener Page-Latch-Zähler? Nein; die aktuelle Wait-
   Ressource muss zum behaupteten Objekt, Index und zur betroffenen Seite passen.
3. Ist `OPTIMIZE_FOR_SEQUENTIAL_KEY = ON` ein universeller Fix? Nein; es ist
   eine verfügbare Option mit workloadabhängiger Wirkung.

Technische Quellen: [SRC-072 – Diagnose von `PAGELATCH_EX`](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/resolve-pagelatch-ex-contention),
[SRC-073 – Sequential keys](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver17#sequential-keys) und
[SRC-074 – Indexbetriebszähler](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-index-operational-stats-transact-sql?view=sql-server-ver17) aus dem
[Quellenregister](../Research/SOURCE_REGISTER.md). Der umfangreichere
IDX-007-Vergleich und eine tatsächliche Engpasszuordnung bleiben offen.
