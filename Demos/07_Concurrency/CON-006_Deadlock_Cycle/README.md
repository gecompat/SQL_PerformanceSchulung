# CON-006 – Reproduzierbarer Deadlock-Zyklus

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `YELLOW` |
| Versionen | SQL Server 2019, 2022 und 2025 |
| Sessions | 3 (`ACTOR_A`, `ACTOR_B`, `OBSERVER`) |
| Umgebung | frische Wegwerf-Instanz, höchstens 180 Sekunden |

## Detaildesign und Freigabe

`LO-M05-03` / `CLM-067`, Quelle `SRC-004` (`ACTIVE`): Blocking ist gerichtetes Warten; ein Deadlock ist ein Zyklus, den SQL Server durch Abbruch eines Opfers auflöst. Zwei Akteure sperren verschiedene Zeilen, synchronisieren sich über `fwk.USP_Signal` und greifen danach in Gegenreihenfolge zu. `DEADLOCK_PRIORITY LOW` macht `ACTOR_A` zum erwarteten Opfer; der Vertrag verlangt genau einen abgefangenen Fehler 1205 und einen erfolgreichen Gegenpart.

Die optionale Beobachtung liest nur die vorhandene `system_health`-Ringbuffer-Evidenz für die markergebundene Datenbank. Fehlt dort noch ein passender Graph, ergibt das `WARN_OPTIONAL_EVIDENCE_SKIPPED`, nicht einen erfundenen Nachweis. Die Gegenprobe greift in identischer Reihenfolge zu und muss ohne Opfer enden.

## Safety und Cleanup

Offene Transaktionen sind auf 15 Sekunden begrenzt und werden in jedem CATCH zurückgerollt. Das Szenario benötigt `--confirm-isolated-lab`; Cleanup entfernt nur die vierfach markierte Datenbank. Am 2026-08-29 erzeugten SQL Server 2019, 2022 und 2025 jeweils zweimal genau ein Opfer, einen Survivor, den markergebundenen Deadlock-Graph und eine erfolgreiche geordnete Gegenprobe; Cleanup war jeweils vollständig.
