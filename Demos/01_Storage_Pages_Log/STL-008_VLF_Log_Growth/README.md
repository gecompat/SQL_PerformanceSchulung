# STL-008 – VLF-Struktur und Logwachstum

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheit | `RED` |
| Umgebung | dedizierte Wegwerf-Containerinstanz |
| Versionen | SQL Server 2019, 2022, 2025 |
| Profil / Budget | `performance`, 600 Sekunden, mindestens 2 GB frei |

## Roter Detailvertrag

`SRC-033` ist `ACTIVE`. Die Demo benötigt `--allow-red`, High-Impact-, Disposable- und Recovery-Bestätigung. Eine kleine Logdatei mit 1-MB-Growth wird durch eine begrenzte, synthetische Transaktion erweitert. `sys.dm_db_log_info` und `sys.database_files` liefern VLF-, Größen- und Growth-Evidenz. Danach wird nur der zukünftige Growth-Schritt auf 64 MB geplant; kein `SHRINK`, Cache-Flush, Restart oder fremder Dateipfad wird verwendet.

Die Kernaussage ist Struktur, nicht Storage-Latenz: Mehr kleinteilige Growth-Ereignisse können mehr VLFs erzeugen; daraus folgt keine universelle Zeitgrenze. Der externe Harness ist der Kill-Switch, jede Transaktion hat ein positives Budget, Cleanup entfernt die markierte Datenbank. Am 2026-08-29 lief die bestätigte rote Lane auf SQL Server 2019, 2022 und 2025 je zweimal mit `PASS/OK`, VLF-/Growth-Evidenz und unabhängiger Cleanup-Prüfung.
