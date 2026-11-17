# IDX-007: Einfügungen an einer heißen Indexseite einordnen

**Status:** kurze fachliche Erläuterung; keine neue Demo, kein Benchmark und
keine Runtimequalifikation.

Der [Offline-Prüfer](../../Tests/Static/idx007_last_page_contract.py) prüft
ergänzend caller-supplied Wait- und Seitenfelder: mindestens zwei verschiedene
Sessions mit `PAGELATCH_EX`, dieselbe Datenbank-/Datei-/Seitenadresse, denselben
gültigen RFC-3339-Zeitpunkt, eine als Blatt deklarierte Zielseite und eine positive
Rechtsaußen-Aussage. `PAGEIOLATCH_EX` allein und fehlende Konkurrenz ergeben
`NOT_PROVEN`; inkonsistente Zuordnungen ergeben `FAIL`. Der Prüfer sammelt oder
authentifiziert keine DMV-Werte und bestätigt nicht selbst die Seitenkette.
Insbesondere ist sein `PASS` kein SQL-Server-Lauf, kein unabhängiger
Rechtsaußen-Nachweis und keine Engpass- oder Leistungsqualifikation.

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

## Lesende Zuordnung einer aktuellen Request-Seite

SQL Server 2019 und neuer stellen für aktive Requests `page_resource` bereit.
`sys.fn_PageResCracker` zerlegt diesen Wert in Datenbank-, Datei- und
Seitennummer; `sys.dm_db_page_info` ergänzt die Seitenkopfdaten. Die folgende
Momentaufnahme zeigt nur Requests, die gerade auf `PAGELATCH_EX` warten, und
meldet Seiten, auf denen mindestens zwei verschiedene Sessions warten:

```sql
DECLARE @capture_started_at_utc datetime2(7) = SYSUTCDATETIME();

;WITH PageWaits AS
(
    SELECT
        r.session_id,
        pr.db_id AS database_id,
        pr.file_id,
        pr.page_id,
        info.object_id,
        info.index_id,
        info.partition_id,
        info.page_level,
        info.next_page_file_id,
        info.next_page_page_id
    FROM sys.dm_exec_requests AS r
    CROSS APPLY sys.fn_PageResCracker(r.page_resource) AS pr
    CROSS APPLY sys.dm_db_page_info(
        pr.db_id, pr.file_id, pr.page_id, N'DETAILED'
    ) AS info
    WHERE r.wait_type = N'PAGELATCH_EX'
      AND r.page_resource IS NOT NULL
      AND r.database_id = DB_ID()
      AND pr.db_id = DB_ID()
)
SELECT
    @capture_started_at_utc AS capture_started_at_utc,
    database_id,
    file_id,
    page_id,
    object_id,
    index_id,
    partition_id,
    page_level,
    next_page_file_id,
    next_page_page_id,
    COUNT(DISTINCT session_id) AS waiting_sessions
FROM PageWaits
WHERE index_id > 0
  AND page_level = 0
GROUP BY
    database_id, file_id, page_id, object_id, index_id, partition_id,
    page_level, next_page_file_id, next_page_page_id
HAVING COUNT(DISTINCT session_id) >= 2;
```

Führe die Abfrage im Kontext der Zieldatenbank aus. Der Zeitwert markiert den
Abfragestart; er ist keine atomare Uhrzeit für jede gelesene DMV-Zeile. Die
Abfrage ist eine Momentaufnahme der Request-Sicht, kein Verlauf und keine
vollständige Warteschlangenaufnahme.
Kein Ergebnis heißt nur, dass diese Abfrage in diesem Moment keine passende
Request-Gruppe erfasst hat. Ab SQL Server 2022 benötigen die Server-DMVs
`VIEW SERVER PERFORMANCE STATE` und `sys.dm_db_page_info`
`VIEW DATABASE PERFORMANCE STATE`; auf SQL Server 2019 sind die entsprechenden
Rechte `VIEW SERVER STATE` und `VIEW DATABASE STATE`.

`page_level = 0` identifiziert eine Blattseite, aber nicht die Rechtsaußen-Seite.
Prüfe Objekt, Index und Partition gegen das synthetische Ziel und untersuche die
ausgegebenen Vor-/Nachfolgerfelder in einer zur Wait-Beobachtung passenden
Momentaufnahme. Die fehlende Nachfolgeradresse muss als Seitenkettenbefund für
den konkreten Enginezustand bestätigt werden. `sys.dm_db_page_info` liefert
Kopfdaten, nicht den Seiteninhalt oder den Schlüsselwert. Wenn Wait-, Header-
und Kettenbefund zeitlich nicht zusammenpassen oder die Kette unklar bleibt,
bleibt das Ergebnis `NOT_PROVEN`.

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

## Fairer OFF/ON-Vergleich: Mindestvertrag

Vergleiche `OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF` und `ON` als getrennte,
gepaarte Varianten. Der Index muss bis auf diese Option identisch sein:
Tabellen- und Indexdefinition, Datentyp und Breite des sequentiellen
Schlüssels, Nutzdaten, Füllfaktor, weitere Indizes, Datenbankoptionen und
Kompatibilitätsgrad. Jede Variante startet mit demselben leeren beziehungsweise
gleichwertig vorbereiteten Datenbestand. Innerhalb eines Messarms darf keine
Variante Inserts in den Index der anderen Variante schreiben.

Lege vor dem Lauf für beide Arme dieselbe Zahl von erfolgreichen Inserts je
Worker, Batch- und Transaktionsgrenzen, Workerzahl und Startbarriere fest.
Verwende denselben Messablauf mit gleicher Aufwärmphase und gleicher
Messreichweite; führe mehrere gepaarte Wiederholungen durch und wechsle die
Reihenfolge OFF/ON, damit Reihenfolgeeffekte sichtbar werden. Verändere nicht
zwischen Armen globale Instanzlast oder Cachezustand. Definiere ein endliches
Arbeits- oder Zeitlimit und Abbruch-/Cleanupverhalten im späteren Laufvertrag,
statt hardwareabhängige absolute Durchsatzschwellen vorzugeben.

Prüfe pro Arm Worker-Erfolg, tatsächliche Zeilenzahl und identische
Endergebnisse. Berichte erfolgreiche Inserts pro Messdauer, Latenzverteilung
und Wait-Differenzen samt Messfenster und Zählergrenzen. Ordne einen
Last-Page-Befund nur zu, wenn gleichzeitig beobachtete `PAGELATCH_EX`-Waits
derselben Zielseite und der für diesen Enginezustand bestätigten Rechtsaußen-
Seitenkette zugeordnet sind. Ohne diese Evidenz bleiben Seitenzähler und
Durchsatzunterschiede Messbeobachtungen, kein Nachweis, dass die Option einen
Last-Page-Engpass behoben hat.

Zeigt der OFF-Arm keine Konkurrenz auf derselben Seite, lautet das Ergebnis
„Engpass nicht demonstriert“; der Lauf wird kontrolliert übersprungen oder als
nicht aussagekräftig beendet. Ein Vergleich mit verteiltem Schlüssel oder Heap
ist ein eigener Strukturvergleich mit eigener Erfolgs- und Messauswertung und
begründet keine allgemeine Überlegenheit.

Dieser Mindestvertrag beschreibt die Methodik, keinen ausführbaren Benchmark.
Konkrete Wiederholungszahl, Zeit-/Arbeitslimit, Rechte, Zielbuilds,
Isolationsprüfung und sichere Bereinigung müssen vor einer späteren Ausführung
im Laufvertrag festgelegt werden.

## Prüffragen

1. Belegt ein positiver Insertzähler Last-Page-Contention? Nein; er belegt nur
   erfasste Einfügungen.
2. Reicht ein indexbezogener Page-Latch-Zähler? Nein; die aktuelle Wait-
   Ressource muss zum behaupteten Objekt, Index und zur betroffenen Seite passen.
3. Ist `OPTIMIZE_FOR_SEQUENTIAL_KEY = ON` ein universeller Fix? Nein; es ist
   eine verfügbare Option mit workloadabhängiger Wirkung.

Technische Quellen: [SRC-072 – Diagnose von `PAGELATCH_EX`](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/resolve-pagelatch-ex-contention),
[Microsoft: `sys.dm_exec_requests`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-requests-transact-sql?view=sql-server-ver17), [`sys.fn_PageResCracker`](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-pagerescracker-transact-sql?view=sql-server-ver17) und [`sys.dm_db_page_info`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-page-info-transact-sql?view=sql-server-ver17): Request-Seitenressource, Seitenkopfdaten und versionsabhängige Berechtigungen; geprüft am 2026-11-17;
[SRC-073 – Sequential keys](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver17#sequential-keys) und
[SRC-074 – Indexbetriebszähler](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-index-operational-stats-transact-sql?view=sql-server-ver17) aus dem
[Quellenregister](../Research/SOURCE_REGISTER.md). Der umfangreichere
IDX-007-Vergleich und eine tatsächliche Engpasszuordnung bleiben offen.
