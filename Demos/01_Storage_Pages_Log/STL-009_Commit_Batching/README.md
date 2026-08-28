# STL-009 – Commit-Batching und WRITELOG

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheit | `YELLOW`, frische Wegwerf-Instanz |
| Versionen | SQL Server 2019, 2022, 2025 |
| Profil / Budget | `standard`, 360 Sekunden |

`SRC-033` (`ACTIVE`) trägt Write-ahead Logging und Log Flush. Identische 4.000 Zeilen werden einmal mit Einzelcommits und einmal in einer Transaktion geschrieben. `sys.dm_io_virtual_file_stats` liefert datenbankbezogene Write-Deltas; `sys.dm_os_wait_stats` liefert ausschließlich ein zeitgebundenes, instanzweites `WRITELOG`-Delta. Ergebnisgleichheit ist exakt, die Richtung der Writeanzahl empirisch.

Die Demo setzt keine Delayed-Durability- oder Instanzoption, leert keine Wait-Statistik und behauptet keine absolute Laufzeit. Sie benötigt das gelbe Safety-Gate und markergeprüftes Cleanup. Am 2026-08-29 liefen SQL Server 2019, 2022 und 2025 je zweimal mit `PASS/OK`, ergebnisgleicher Gegenprobe und vollständigem Cleanup.
