# CON-006 – Deadlock-Zyklen durch Zugriffreihenfolge und Sperrumwandlung

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `YELLOW` |
| Versionen | SQL Server 2019, 2022 und 2025 |
| Sessions | 3 (`ACTOR_A`, `ACTOR_B`, `OBSERVER`) |
| Umgebung | frische Wegwerf-Instanz, höchstens 180 Sekunden |

## Detaildesign und Freigabe

`LO-M05-03` / `CLM-067`, Quelle `SRC-004` (Transaction locking and row versioning guide) (`ACTIVE`): Blocking ist gerichtetes Warten; ein Deadlock ist ein Zyklus, den SQL Server durch Abbruch eines Opfers auflöst. Der erste Ablauf sperrt zwei Zeilen in Gegenreihenfolge. Der zusätzliche Konversionsablauf liest denselben Datensatz in beiden Transaktionen unter `REPEATABLE READ`; nach einer signalgesteuerten Barriere fordern beide `X` an. `DEADLOCK_PRIORITY LOW` macht jeweils `ACTOR_A` zum erwarteten Opfer; der Vertrag verlangt genau einen abgefangenen Fehler 1205 und einen erfolgreichen Gegenpart.

Die optionale Beobachtung des Grundfalls liest die vorhandene `system_health`-Ringbuffer-Evidenz für die markergebundene Datenbank. Fehlt dort noch ein passender Graph, ergibt das `WARN_OPTIONAL_EVIDENCE_SKIPPED`, nicht einen erfundenen Nachweis. Die zusätzliche Konversionsphase verlangt genau einen Graphen aus dem Laufzeitfenster mit denselben zwei SPIDs und derselben Datenbank. SQL Server stellt den Zyklus als zwei `keylock`-Einträge derselben Datenbank, desselben Objekts, Indexes und HoBTs dar: jeder Eintrag zeigt für einen Actor dessen `S`-Besitz und `X`-Konversionsanforderung sowie die `X`-Konversionswarteanfrage des Gegenactors. Beide Richtungen müssen vorhanden sein. Die `UPDLOCK`-Gegenprobe verwendet denselben Datensatz und muss ohne Opfer enden. Die neue Variante ist durch die SQL-Matrix auf 2019, 2022 und 2025 buildqualifiziert.

Die [Lehrnotiz zu Deadlockvarianten](../../../Documentation/Curriculum/DEADLOCK_VARIANTS_LESSON.md)
ordnet Gegenreihenfolge und Sperrumwandlung fachlich ein. Die zwei Demoszenarien
bleiben getrennte Phasen; der synthetische Graphvertrag ergänzt, aber ersetzt
nicht den buildgebundenen Graphnachweis der Konversionsphase.

## Safety und Cleanup

Offene Transaktionen und Signalschleifen sind zeitlich begrenzt; jeder Actor rollt eine offene Transaktion im CATCH zurück. `UPDLOCK` wird ausschließlich im markierten Demo-Datensatz verwendet. Das Szenario benötigt `--confirm-isolated-lab`; Cleanup entfernt nur die vierfach markierte Datenbank. Am 2026-08-29 erzeugten SQL Server 2019, 2022 und 2025 im Grundfall jeweils zweimal genau ein Opfer, einen Survivor, einen markergebundenen Deadlock-Graph und eine erfolgreiche geordnete Gegenprobe; Cleanup war jeweils vollständig. Die zusätzliche Konversions- und `UPDLOCK`-Gegenprobe wird erst durch den aktuellen PR-Lauf qualifiziert.

## Schritt-für-Schritt-Anleitung

Die vollständige Ausführung steht im [Ausführungsleitfaden für die katalogisierten Demos](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md): `CON-006` (Zyklische Sperrkonflikte erkennen) auswählen und den manifestbasierten Aufruf nur auf einer Wegwerfinstanz mit `-ConfirmIsolatedLab` ausführen. Für den Grundfall und die Konversionsvariante sind jeweils genau ein Opfer mit Fehler 1205 und ein Survivor zu prüfen. Die Konversionsphase verlangt zusätzlich den an beide Sessions gebundenen `S`-zu-`X`-Graphen auf derselben Schlüsselressource; die `UPDLOCK`-Gegenprobe muss mit zwei abgeschlossenen Sessions ohne Deadlock enden. Nach Abbruch ausschließlich den markergebundenen Cleanup aus dem Leitfaden verwenden.
