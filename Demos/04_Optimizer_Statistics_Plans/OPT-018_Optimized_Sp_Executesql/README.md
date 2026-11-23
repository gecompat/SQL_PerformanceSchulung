# OPT-018 – Gleichzeitige Kompilierung mit OPTIMIZED_SP_EXECUTESQL

Die Demo zeigt, was beim ersten Aufruf desselben parametrisierten dynamischen
Batches aus zwei Sitzungen geschieht. Sie vergleichen überlappende
Kompilierungen bei ausgeschalteter Option mit der Compile-Sperre und
anschließenden Wiederverwendung desselben Plans bei eingeschalteter Option.

## Schritt-für-Schritt-Anleitung

Benötigt werden Python 3.12+, PowerShell 7.2+, ein lokaler Docker-kompatibler
Linux-Containerkontext und das bereits lokal vorhandene AMD64-Image
`mcr.microsoft.com/mssql/server@sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9`.
Der Runner prüft SQL Server 2025 Enterprise Developer Edition Build
`17.0.5065.9`. Die Bestätigung gilt für die SQL Server Developer EULA und
für einen eigenen Wegwerfcontainer mit 2 CPUs, 4 GiB RAM und sechs markierten
Versuchsdatenbanken. Die beiden Clients verbinden sich über einen dynamischen
IPv4-Loopback-Port. Starten Sie den Versuch manifestbasiert aus dem Repository-Stamm.
Der Runner erfasst die Versuchsdatenbanken und den Abbau markergebunden.

```text
python Demos/00_Framework/Tools/run_demo.py Demos/04_Optimizer_Statistics_Plans/OPT-018_Optimized_Sp_Executesql/manifest.json --confirm-isolated-lab
```

Bei Podman wählen Sie vor dem Aufruf den lokalen Docker-kompatiblen Kontext
Ihrer Installation. Der Runner verwendet das vorhandene Image.

## Beobachten

1. `OFF_ON` und `ON_OFF` prüfen dieselbe Arbeitslast in umgekehrter
   Reihenfolge. Bei `OFF` muss Extended Events zwei zeitlich überlappende
   Erstkompilierungen belegen. Bei `ON` muss eine Sitzung nachweisbar auf die
   Compile-Sperre warten. Beide Ausführungen müssen denselben Plan verwenden.
2. `SEQUENTIAL` und `DISTINCT` prüfen, ob das Auswerteverfahren die erwartete
   Evidenz bei sequenziellen Aufrufen und geändertem Batchtext zurückweist.
   `DISTINCT_PAIR` prüft zusätzlich die Arbeitslastbindung auf Paarebene.
3. `SQLPERF_SUMMARY|PASS|OK` bestätigt die beiden Paare, die erwarteten
   Gegenproben und den geprüften Abbau. `FAIL_NOT_PROVEN` bezeichnet
   unvollständige Versuchsevidenz. Bei `FAIL_CLEANUP` bleibt der Abbau zu
   prüfen. Die Fehlermeldung nennt den synthetischen Besitzmarker für das
   Containerlabel `com.sqlperf.optsp.owner`.

Die Beobachtungen gelten für diese Arbeitslast und diesen Build. Weitere
Details stehen in der
[Versuchsmethode zu OPTIMIZED_SP_EXECUTESQL](../../../Documentation/Project_Planning/OPTIMIZED_SP_EXECUTESQL_CONCURRENT_COMPILE_DESIGN.md#gebundenen-vergleich-ausführen)
und im [Demo-Katalog](../../../Documentation/Demo_Catalog/README.md).
Der [Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md)
führt zu den weiteren Optimizer-Demos.
