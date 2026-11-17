# Worker-Warteschlange von CPU-Druck unterscheiden

Diese Lehrnotiz ergänzt die Lernziele zu aktuellen Waits und Wait-Kategorien
im [Diagnosemodul](CURRICULUM_ARCHITECTURE.md). Sie zeigt einen rein lesenden
Startpunkt für die Frage, ob Aufgaben auf einen Worker warten oder ob bereits
zugewiesene Worker auf CPU-Zeit warten. Sie erzeugt keine Last und qualifiziert
keine Demo.

## Workerbedarf und CPU-Warteschlange sind verschiedene Signale

`sys.dm_os_schedulers.work_queue_count` zählt Aufgaben, die in der
Scheduler-Warteschlange auf einen Worker warten. `runnable_tasks_count` zählt
dagegen bereits ausführbare Aufgaben, die einem Scheduler zugeordnet sind und
auf CPU-Zeit warten. Eine volle Runnable-Warteschlange ohne `work_queue_count`
ist deshalb CPU-Druck, aber für sich kein Worker-Erschöpfungsnachweis.

Eine lesende Momentaufnahme kann beide Zähler nebeneinander zeigen:

```sql
DECLARE @CapturedUtc datetime2(7) = SYSUTCDATETIME();

SELECT @CapturedUtc AS captured_utc,
       scheduler_id,
       current_workers_count,
       active_workers_count,
       runnable_tasks_count,
       work_queue_count
FROM sys.dm_os_schedulers
WHERE scheduler_id < 255
  AND is_online = 1
ORDER BY scheduler_id;
```

`work_queue_count > 0` ist ein Signal dafür, dass im erfassten Scheduler
Aufgaben auf einen Worker warten. Für einen konkreten Workload muss zusätzlich
eine aktuelle `THREADPOOL`-Wartezeit dem eigenen Request und demselben
Beobachtungsfenster zugeordnet werden. Eine passende Gegenprobe ist eine
Warteschlange ohne belegte Worker-Wartezeit, aber mit vielen Runnable-Aufgaben:
Sie weist eher auf CPU-Konkurrenz als auf fehlende Workerzuweisung hin.

## Livezustand und Wait-Historie auseinanderhalten

`sys.dm_os_waiting_tasks` zeigt aktuelle Task-Waits. `sys.dm_os_wait_stats`
enthält dagegen abgeschlossene, seit Engine-Start oder letztem Reset
kumulierte Waits und zeigt keine derzeit wartenden Tasks. Für historische
Vergleiche müssen Vorher-/Nachher-Deltas mit bekanntem Engine- und Resetzeitpunkt
gebildet werden. Die drei DMVs liefern unabhängig gelesene Momentaufnahmen und
keinen atomaren Gesamtzustand.

Aktive Sessions, ein hoher CPU-Wert oder ein positiver kumulativer
`THREADPOOL`-Zähler allein belegen keine Erschöpfung. Eine belastbare Diagnose
bindet wiederholte Livebeobachtungen, tatsächliche `THREADPOOL`-Wartezeiten,
den eigenen markierten Request und eine begrenzte Lastphase an denselben Lauf.
Zur Erholung gehören der bestätigte Abschluss der eigenen Lastrequests und
eine erneute Beobachtung der Worker-Warteschlange. Ein einzelner leerer
Snapshot widerlegt keinen Druck außerhalb dieses Zeitpunkts.

`max worker threads` sollte nicht aufgrund einer hohen Sessionzahl oder CPU-Last
erhöht werden. Lange Anforderungen, Blocking, Latch-, I/O- und Netzwerk-Waits
können Worker belegen; zuerst ist die Ursache dieser Belegung zu untersuchen.
Eine ausführbare Erschöpfungsprobe erfordert eine isolierte Wegwerfinstanz,
strenge Last- und Zeitgrenzen sowie einen getesteten Abbruch- und Cleanup-Pfad.

## Quellen und Berechtigungen

- Microsoft Learn, [`sys.dm_os_schedulers`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-schedulers-transact-sql?view=sql-server-ver17): Schedulerzähler, darunter `work_queue_count` und `runnable_tasks_count`.
- Microsoft Learn, [`sys.dm_os_waiting_tasks`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-waiting-tasks-transact-sql?view=sql-server-ver17): aktuelle wartende Tasks.
- Microsoft Learn, [`sys.dm_os_wait_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-wait-stats-transact-sql?view=sql-server-ver17): kumulative abgeschlossene Waits und Resetgrenzen.
- Microsoft Learn, [max worker threads](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-the-max-worker-threads-server-configuration-option?view=sql-server-ver17): automatische Voreinstellung und Ursachenprüfung vor einer Änderung.

Das Lesen instanzweiten Zustands erfordert versionsabhängige Rechte: Microsoft
dokumentiert `VIEW SERVER STATE` für SQL Server 2019 und `VIEW SERVER PERFORMANCE
STATE` ab SQL Server 2022. Die [RES-001-Offlineprüfung](../../Tests/Static/test_res001_worker_queue_contract.py)
prüft nur caller-gelieferte Werte synthetisch; sie authentifiziert keine
DMV-Abfrage und qualifiziert keine Runtime.
