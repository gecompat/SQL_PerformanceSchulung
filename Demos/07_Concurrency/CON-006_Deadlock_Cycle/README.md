# CON-006 – Deadlock-Zyklen durch Zugriffreihenfolge, Sperrumwandlung und Schlüsselbereiche

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `YELLOW` |
| Versionen | SQL Server 2019, 2022 und 2025 |
| Sessions | 3 (`ACTOR_A`, `ACTOR_B`, `OBSERVER`) |
| Umgebung | frische Wegwerf-Instanz, höchstens 180 Sekunden |

## Detaildesign und Freigabe

`LO-M05-03` / `CLM-067`, Quelle `SRC-004` (Transaction locking and row versioning guide) (`ACTIVE`): Blocking ist gerichtetes Warten; ein Deadlock ist ein Zyklus, den SQL Server durch Abbruch eines Opfers auflöst. Der erste Ablauf sperrt zwei Zeilen in Gegenreihenfolge. Der zusätzliche Konversionsablauf liest denselben Datensatz in beiden Transaktionen unter `REPEATABLE READ`; nach einer signalgesteuerten Barriere fordern beide `X` an. `DEADLOCK_PRIORITY LOW` macht jeweils `ACTOR_A` zum erwarteten Opfer; der Vertrag verlangt genau einen abgefangenen Fehler 1205 und einen erfolgreichen Gegenpart.

Die optionale Beobachtung des Grundfalls liest die vorhandene `system_health`-Ringbuffer-Evidenz für die markergebundene Datenbank. Fehlt dort noch ein passender Graph, ergibt das `WARN_OPTIONAL_EVIDENCE_SKIPPED`, nicht einen erfundenen Nachweis. Die zusätzliche Konversionsphase verlangt genau einen Graphen aus dem Laufzeitfenster mit denselben zwei SPIDs und derselben Datenbank. Die beiden Session-Skripte lesen und ändern dieselbe Zeile (`RowId=1`); der Deadlockgraph bindet die gegenläufigen S-zu-X-Konversionsanforderungen an Datenbank, Objekt, Index und HoBT. Er enthält keinen separat ausgewerteten Schlüsselwert, daher stammt die konkrete Zeilenbindung aus dem fixierten Szenario-SQL und nicht allein aus dem Graphen. Beide Richtungen müssen vorhanden sein. Die `UPDLOCK`-Gegenprobe verwendet denselben Datensatz und muss ohne Opfer enden. Die neue Variante ist durch die SQL-Matrix auf 2019, 2022 und 2025 buildqualifiziert.

Die [Lehrnotiz zu Deadlockvarianten](../../../Documentation/Curriculum/DEADLOCK_VARIANTS_LESSON.md)
ordnet Gegenreihenfolge und Sperrumwandlung fachlich ein. Die zwei Demoszenarien
bleiben getrennte Phasen; der synthetische Graphvertrag ergänzt, aber ersetzt
nicht den buildgebundenen Graphnachweis der Konversionsphase.

Die dritte Variante zeigt einen Deadlock aus gekreuzten Einfügungen in zwei
leere, durch den Schlüssel `50` getrennte Indexbereiche. Actor A liest unter
`SERIALIZABLE` den Bereich `(20, 40)`, Actor B `(60, 80)`; beide lesen gezielt
über den Primärschlüsselindex. Der Beobachter wartet, bis beide Sessions ihre
`RangeS-S`- oder `RangeS-U`-Sperre auf dem tatsächlichen HoBT halten. Er gibt
dann A frei, prüft, dass A beim Einfügen von `70` auf B wartet, und startet erst
danach B mit dem Einfügen von `30`. Der Deadlockgraph muss genau zwei
verschiedene KEY-Ressourcen desselben Indexes zeigen, die durch inkompatible
gekreuzte `requestType=wait`-Kanten den Zyklus schließen. Genau ein Actor muss
mit Fehler 1205 zurückgerollt werden; der Survivor fügt seinen Schlüssel ein.
Der Deadlock-Endbestand enthält daher vier Schlüssel: `10`, `50`, `90` und den
Schlüssel des Survivors.

Die serielle Gegenprobe verwendet zwei getrennte Sessions. A fügt `70` ein;
B hält seine eigene Session bereit und fügt `30` erst nach A's bestätigtem
Abschluss ein. Beide Inserts müssen erfolgreich sein, der Endbestand muss
genau `10`, `30`, `50`, `70`, `90` enthalten und in diesem Kontrollzeitfenster
darf kein passendes Deadlockereignis auftreten. Damit lernen Teilnehmende den
Unterschied zwischen einem beobachteten Blockingrand und einem vollständigen
Deadlockzyklus sowie die Bedeutung der konkreten KEY-Ressourcen im Graphen.

Die vollständige Variante ist in den manifestbasierten Ablauf integriert und
auf den gepinnten Builds SQL Server 2019 `15.0.4500.2`, 2022 `16.0.4305.5` und
2025 `17.0.5035.5` qualifiziert. Alle drei vollständigen Läufe bestanden
Graph-, Opfer-/Survivor-, Kontrollarm-, Endzustands- und Cleanupprüfung. Sie
liefen in netzwerkisolierten Wegwerfcontainern mit 2 CPUs und 4 GiB Speicher;
der manifeste Gesamtablauf ist auf 180 Sekunden, Cleanup auf 60 Sekunden und
jede Mehrsessionphase auf 45 Sekunden begrenzt.

## Safety und Cleanup

Offene Transaktionen und Signalschleifen sind zeitlich begrenzt; jeder Actor rollt eine offene Transaktion im CATCH zurück. `UPDLOCK` wird ausschließlich im markierten Demo-Datensatz verwendet. Das Szenario benötigt `--confirm-isolated-lab`; Cleanup entfernt nur die vierfach markierte Datenbank. Am 2026-08-29 erzeugten SQL Server 2019, 2022 und 2025 im Grundfall jeweils zweimal genau ein Opfer, einen Survivor, einen markergebundenen Deadlock-Graph und eine erfolgreiche geordnete Gegenprobe; Cleanup war jeweils vollständig. Die zusätzliche Konversions- und `UPDLOCK`-Gegenprobe wird erst durch den aktuellen PR-Lauf qualifiziert.

## Schritt-für-Schritt-Anleitung

Die vollständige Ausführung steht im [Ausführungsleitfaden für die katalogisierten Demos](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md): `CON-006` (Zyklische Sperrkonflikte erkennen) auswählen und den manifestbasierten Aufruf nur auf einer Wegwerfinstanz mit `-ConfirmIsolatedLab` ausführen. Für den Grundfall und die Konversionsvariante sind jeweils genau ein Opfer mit Fehler 1205 und ein Survivor zu prüfen. Die Konversionsphase verlangt zusätzlich den an beide Sessions gebundenen `S`-zu-`X`-Graphen auf derselben Schlüsselressource; die `UPDLOCK`-Gegenprobe muss mit zwei abgeschlossenen Sessions ohne Deadlock enden. Nach Abbruch ausschließlich den markergebundenen Cleanup aus dem Leitfaden verwenden.
