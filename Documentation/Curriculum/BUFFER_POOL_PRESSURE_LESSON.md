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
| `process_physical_memory_low` | SQL Server reagiert auf eine Meldung über wenig physischen Arbeitsspeicher für den Prozess | welche Abfrage oder Cache-Seite den Zustand verursachte |
| `process_virtual_memory_low` | für den SQL-Server-Prozess wurde eine Bedingung mit wenig virtuellem Speicher erkannt | ein Mangel an physischem Arbeitsspeicher oder eine konkrete Ursache |
| `system_low_memory_signal_state` und `system_high_memory_signal_state` | Betriebssystemsignale zum verfügbaren physischen Arbeitsspeicher | welche Abfrage oder Cache-Seite den Zustand verursachte |
| Grant-DMV und `RESOURCE_SEMAPHORE` | Abfragespeicherzuteilungen und gegebenenfalls darauf wartende Anforderungen | Druck auf den Datenseiten-Cache |

Die Speichersignalspalten können in einzelnen lesenden Momentaufnahmen betrachtet werden:

```sql
SELECT process_physical_memory_low, process_virtual_memory_low
FROM sys.dm_os_process_memory;

SELECT system_low_memory_signal_state, system_high_memory_signal_state
FROM sys.dm_os_sys_memory;
```

Die beiden Prozessflags beschreiben verschiedene Bedingungen: `process_physical_memory_low` folgt einer Benachrichtigung über knappen physischen Speicher; `process_virtual_memory_low` meldet eine erkannte Bedingung mit wenig virtuellem Speicher. Sie sind keine austauschbaren Kennzeichen und ordnen den Zustand keiner Abfrage zu.

Die Betriebssystemflags bilden gemeinsam den Signalzustand ab. `system_low_memory_signal_state = 1` meldet wenig verfügbaren physischen Speicher. Bei `system_high_memory_signal_state = 1` und Low = 0 meldet das Betriebssystem viel verfügbaren Speicher; bei beiden Werten 0 wird die Speichernutzung als stabil beschrieben. Sind beide Signale 1, kann das bei raschem Wechsel einen Übergangszustand anzeigen. Deshalb bedeutet Low = 0 allein nicht in jedem Fall, dass viel physischer Speicher verfügbar ist.

Der bestehende [RES-003-Offlinevertrag](../../Tests/Static/res003_memory_signal_contract.py) verfolgt absichtlich nur `process_physical_memory_low` und `system_low_memory_signal_state` als getrennte Drucksignale in einer Vorher-/Druck-/Erholungsfolge. Er wertet weder `process_virtual_memory_low` noch das High-Signal aus, authentifiziert keine DMV-Aufnahme und attestiert keine echte Runtimeprobe. Die Beispielabfrage zeigt die zusätzlichen Flags zur Einordnung; sie erweitern den Offlinevertrag nicht.

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
