# RES-007 – Wait-Scope und zeitbezogene Deltas

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheit | `YELLOW`, frische Wegwerf-Instanz |
| Versionen | SQL Server 2019, 2022, 2025 |
| Sessions | 3 (`BLOCKER`, `WAITER`, `OBSERVER`) |
| Profil / Budget | `standard`, 180 Sekunden |

`LO-M06-01`, `LO-M06-08`, `CLM-073` und `ADV-CLM-037`: aktuelle Task-Waits, Request-Waits und instanzweite kumulative Waits haben verschiedene Scopes. Ein kontrollierter Row-Lock erzeugt einen `LCK_M_*`-Wait. Der Observer bindet Task und Request an die gespeicherten Session-IDs, bildet für denselben Zeitabschnitt ein `sys.dm_os_wait_stats`-Delta und bestätigt die Hypothese durch Freigabe des Blockers.

`SRC-035`, `SRC-036` und `SRC-051` sind `ACTIVE`. Waits starten eine Hypothese; sie beweisen allein keine Ursache. `ASYNC_NETWORK_IO` ist ohne gepaceten Client keine Kernevidenz und wird in diesem Schnitt nicht künstlich erzeugt. Keine Wait-Statistik wird geleert. Am 2026-08-29 liefen alle Zielversionen je zweimal mit `PASS/OK`, vollständiger Task-/Request-/Delta-Evidenz, Freigabe-Gegenprobe und Cleanup.
