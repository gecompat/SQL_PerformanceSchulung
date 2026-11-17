# Buffer-Pool-Belegung und Speicherdruck unterscheiden

Diese Vertiefung zu `LO-M06-07` ergänzt die Diagnose von Abfragespeicherzuteilungen um den Datenseiten-Cache. Sie baut auf den in [STL-006](../../.ai/BACKLOG.md) behandelten Buffer-Pool- und Cold-/Warm-Cache-Grundlagen auf. Ziel ist, Cachebelegung, Low-Memory-Signale und Grant-Waits als unterschiedliche Beobachtungen einzuordnen.

## Was eine Cachemomentaufnahme zeigt

`sys.dm_os_buffer_descriptors` enthält einen Deskriptor für jede aktuell zwischengespeicherte Datenseite. Eine Momentaufnahme kann daher zeigen, wie viele Seiten einer Datenbank zu diesem Zeitpunkt im Buffer Pool liegen:

```sql
SELECT
    DB_NAME(database_id) AS database_name,
    COUNT_BIG(*) AS cached_pages,
    COUNT_BIG(*) * 8.0 / 1024 AS cached_mib
FROM sys.dm_os_buffer_descriptors
WHERE database_id = DB_ID(N'<Datenbankname>')
GROUP BY database_id;
```

Ersetze den Platzhalter durch den Namen einer vorhandenen Datenbank. Der Wert beschreibt Cachebelegung zum Abfragezeitpunkt. Er sagt allein nicht, ob Seiten unter Druck verdrängt wurden, ob eine Abfrage physische Reads ausführen musste oder ob Arbeitsspeicher die beobachtete Verzögerung verursacht hat. Ein hoher oder niedriger Wert besitzt ohne passenden Zeitraum, Workload und Vergleich keine allgemeingültige Bewertung.

Für die Sicht auf den gesamten Buffer Pool kann der Filter auf `database_id` entfallen. Das Ergebnis bleibt eine Seiteninventur, keine Druckmessung. Die DMV benötigt `VIEW SERVER STATE` auf SQL Server 2019 und `VIEW SERVER PERFORMANCE STATE` ab SQL Server 2022.

## Drei getrennte Beobachtungen

| Beobachtung | Aussage | Belegt für sich nicht |
|---|---|---|
| `sys.dm_os_buffer_descriptors` | aktuell zwischengespeicherte Datenseiten nach Datenbank | Verdrängungsdruck, physische Reads oder eine Ursache für langsame Abfragen |
| `process_physical_memory_low` und `system_low_memory_signal_state` | SQL-Prozess beziehungsweise Betriebssystem meldet einen Low-Memory-Zustand | welche Abfrage oder Cache-Seite den Zustand verursachte |
| Grant-DMV und `RESOURCE_SEMAPHORE` | Abfragespeicherzuteilungen und gegebenenfalls darauf wartende Anforderungen | Druck auf den Datenseiten-Cache |

Die Low-Memory-Spalten können in einer einzelnen lesenden Momentaufnahme betrachtet werden:

```sql
SELECT process_physical_memory_low, process_virtual_memory_low
FROM sys.dm_os_process_memory;

SELECT system_low_memory_signal_state, system_high_memory_signal_state
FROM sys.dm_os_sys_memory;
```

Diese Flags sind Signale mit Prozess- beziehungsweise Betriebssystem-Scope, keine Verlaufskurve. Für eine zeitliche Diagnose müssen wiederholte Beobachtungen mit Zeitraum und relevanter Workload zusammenpassen. Der bestehende [RES-003-Offlinevertrag](../../Tests/Static/res003_memory_signal_contract.py) prüft nur caller-gelieferte Zustände und attestiert keine echte DMV-Abfrage.

`RESOURCE_SEMAPHORE` gehört zum Warten auf Query Execution Memory. Auch `MIN_MEMORY_PERCENT` und `MAX_MEMORY_PERCENT` des Resource Governor beziehen sich bei normalen, nicht speicheroptimierten Tabellen auf Query-Workspace-Speicher; sie begrenzen nicht den gemeinsam genutzten Buffer Pool mit Daten- und Indexseiten. Die Konfiguration eines Ressourcenpools belegt zudem noch keine wirksame Zuordnung oder Begrenzung einer konkreten Session.

## Diagnosepfad

1. Frage und Zeitraum festlegen: Geht es um Datenseiten-Cache, ein Prozess-/Systemsignal oder eine wartende Grant-Anforderung?
2. Nur die dazu passende Sicht erheben. Eine Cacheinventur nicht als Drucknachweis und einen Grant-Wait nicht als Buffer-Pool-Befund behandeln.
3. Bei einer Leistungsbehauptung Zeitbezug, Workload und passende Gegenprobe ergänzen, zum Beispiel tatsächliche physische Reads und ihre zeitliche Beziehung zum untersuchten Zugriff. Ein einzelner Wert oder eine konfigurierte Grenze genügt nicht.
4. Ergebnis als Beobachtung, Hypothese oder bestätigte Ursache kennzeichnen. Ohne passende Verlaufsevidenz bleibt „Speicherdruck verursachte die Verzögerung“ unbestätigt.

Diese Notiz ist Erklärmaterial. Sie führt keine Last aus und qualifiziert weder Buffer-Pool-Druck noch Resource-Governor-Wirkung. Eine Druckdemonstration bleibt an die dedizierte Wegwerfinfrastruktur und die im RES-003-Plan beschriebenen Sicherheits-, Restore- und Abnahmenachweise gebunden.

## Quellen

- Microsoft Learn, [`sys.dm_os_buffer_descriptors`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-buffer-descriptors-transact-sql?view=sql-server-ver17): derzeit zwischengespeicherte Datenseiten und Diagnoseberechtigungen; geprüft am 2026-11-17; `SRC-134`.
- Microsoft Learn, [`sys.dm_os_process_memory`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-process-memory-transact-sql?view=sql-server-ver17) und [`sys.dm_os_sys_memory`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-sys-memory-transact-sql?view=sql-server-ver17): Prozess- und Betriebssystemspeichersignale; geprüft am 2026-11-17; `SRC-134`.
- Microsoft Learn, [Resource Governor resource pool](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/resource-governor-resource-pool?view=sql-server-ver17): Abgrenzung von Query-Workspace-Speicher und gemeinsamem Buffer Pool; geprüft am 2026-11-17; `SRC-134`.
