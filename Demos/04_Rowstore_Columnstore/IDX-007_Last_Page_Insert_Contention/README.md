# IDX-007 – Einfügungen an einer heißen letzten Indexseite

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` für je einen gebundenen Build auf SQL Server 2019, 2022 und 2025; die allgemeine Methode bleibt `METHOD_DRAFT` |
| Sicherheit | `YELLOW`; eigener, netzwerkloser Wegwerfcontainer |
| Zielversionen | SQL Server 2019, 2022 und 2025; jeweils ein konkreter Build |
| Ressourcen | Container auf 2 CPUs und 4 GiB begrenzt; ein Lauf, zwei Insertschübe |
| Ausführung | `run_demo.py` mit `--confirm-isolated-lab` und `--idx007-major` |

## Lernziel

Die Gruppe unterscheidet einen exklusiven Buffer-Pool-Seiten-Latch (`PAGELATCH_EX`) von einer Transaktionssperre und von einem Ein-/Ausgabewarten (`PAGEIOLATCH_EX`). Sie sieht, wie mehrere gleichzeitig laufende Inserts auf dieselbe Blattseite warten können und wie die Beobachtung an eine zeitlich geklammerte Blattkettenprobe gebunden wird.

Der Lauf erzeugt ausschließlich synthetische Daten in einem frischen offiziellen Microsoft SQL-Server-Container ohne Netzwerk, Host-Port oder persistentes Volume. Er misst nicht die allgemeine Leistung sequentieller Schlüssel und behauptet keine universelle DMV-Atomizität oder allgemeine Garantie zum Verhalten gleichzeitiger Seitenaufteilungen. `WARN_NOT_PROVEN` bedeutet, dass diese konkrete Ausführung die erwartete Überlappung nicht belegt hat; die fachliche Aussage darf dann nicht als beobachtet vorgeführt werden.

## Voraussetzungen

- Windows oder Linux mit Python 3.12+, Docker Engine mit Linux-Containern und mindestens 4 GiB für den Container verfügbarer Arbeitsspeicher.
- Die unten angegebene, digest-gepinnte SQL-Server-Edition-Developer-Image-Version muss lokal verfügbar sein. Der Lauf verwendet absichtlich `--pull=never`.
- Es wird weder eine vorhandene SQL-Server-Instanz noch `sqlcmd` auf dem Host benötigt; `sqlcmd` wird im Container verwendet.
- Die Gruppe muss vor dem Start bestätigen, dass die Laufumgebung als isoliertes, wegwerfbares Lab vorgesehen ist.

| Major | Build | Image digest |
|---:|---|---|
| 15 (SQL Server 2019) | `15.0.4500.2` | `sha256:07d7dedecdbfcf6776035dc5eefb5bfd9aa1804b2f6b99f7dedb397d8a599069` |
| 16 (SQL Server 2022) | `16.0.4305.5` | `sha256:cf8f0ab2ebe61feec2eed2629061a07d247f791c2a8ddda74a4ac9f06a291718` |
| 17 (SQL Server 2025) | `17.0.5035.5` | `sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f` |

## Vorbereitung und Ausführung

### 7.1 Schritt-für-Schritt-Anleitung

1. Wechseln Sie in den Repository-Stamm und prüfen Sie Docker sowie Python: `docker info` und `python --version`.
2. Laden Sie genau das gewählte Image vorab, zum Beispiel für SQL Server 2025: `docker pull mcr.microsoft.com/mssql/server@sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f`. Für 2019 oder 2022 verwenden Sie den Digest aus der Tabelle.
3. Starten Sie den manifestbasierten Katalogrunner genau einmal und wählen Sie die Version: `python Demos/00_Framework/Tools/run_demo.py Demos/04_Rowstore_Columnstore/IDX-007_Last_Page_Insert_Contention/manifest.json --confirm-isolated-lab --idx007-major 17`. Die Sicherheitsbestätigung heißt in PowerShell-Funktionen `-ConfirmIsolatedLab`.
4. Erläutern Sie die beiden `WAIT_OVERLAP`-Zeilen sowie die dazugehörigen `CHAIN_BRACKET`-Zeilen. Beide Bursts müssen ihre Wait-Überlappung auf derselben Seite zeigen, die als terminales Blatt des Zielindexes geprüft wird.
5. Beenden Sie die Vorführung mit der `SQLPERF_SUMMARY`. `PASS / OK` belegt den Lauf für den ausgewählten gepinnten Build. Bei `WARN_NOT_PROVEN` oder einem Fehler zeigen Sie die Ausgabe als nicht bewiesenen Lauf, nicht als bestätigtes Ergebnis.

### Ablauf für die Lehrperson

**Vor dem Start:** „Wir erzeugen keine künstliche Serverlast außerhalb eines Wegwerfcontainers. Die Inserts sind synchronisiert, damit wir gleichzeitig laufende Einfügungen gezielt beobachten können. Das ist ein Mechanismusnachweis, kein Leistungsvergleich.“ Lassen Sie die Lernenden `PAGELATCH_EX` und `PAGEIOLATCH_EX` unterscheiden.

**Während des Laufs:** Der Reader erfasst Extended-Events-Latchintervalle und klammert einen begrenzten Scan der Blattkette zwischen Start- und Endmarker. Die beiden Insertschübe sind getrennte Beobachtungen; ein Split darf die Zielseite zwischen den Schüben ändern. Fragen Sie, warum die Page-Adresse allein nicht genügt und warum Session-/Request-Bindung wichtig ist.

**Nach dem Lauf:** `WAIT_OVERLAP` zeigt zwei überlappende exklusive Buffer-Latch-Waits verschiedener Requests auf derselben Seite. `CHAIN_BRACKET` zeigt, dass dieselbe Seite im jeweiligen Capture als rechtes Blatt des Zielindexes geprüft wurde. Die Demo misst keine End-to-End-Latenz und isoliert keine allgemeine Performanceursache.

## Grenzen und Fehlerbehandlung

- Der Ablauf verwendet pro Aufruf einen frischen Container, höchstens 80 Actors (SQL Server 2019/2022) beziehungsweise 56 (2025), zwei Inserts je Actor über zwei Bursts und insgesamt höchstens einen Versuch.
- Datenbank und Container tragen Eigentumsmarker. Das normale Cleanup entfernt Extended-Events-Sessions, die markergebundene synthetische Datenbank und den eigenen Container. Bei Harness-Timeout versucht der Frameworkrunner, ausschließlich IDX-007-markierte netzwerklose Container zu entfernen.
- Bei verbleibendem Container prüfen Sie zuerst `docker ps -a --filter label=sqlperf.demo.id=IDX-007`. Prüfen Sie das Label und `NetworkMode=none`, bevor Sie einen liegengebliebenen IDX-007-Wegwerfcontainer entfernen. Löschen Sie keine Ressource allein aufgrund ihres Namens.
- Wenn der Image-Digest fehlt, laden Sie ihn mit dem Pull-Befehl nach. Wenn Docker, Speicher oder CPU nicht verfügbar sind, starten Sie den Demoaufruf nicht auf einer geteilten SQL-Server-Instanz.

## Evidenz und weiterführende Lernpfade

Die ausführliche Methodik, XE-Bindungen, Grenzen und Build-spezifischen Einstellungen stehen im [Rechtsaußen-Methodenentwurf](../../../Documentation/Project_Planning/IDX007_RIGHTMOST_PAGE_METHOD.md) und im [Lernblatt zu Last-Page-Contention](../../../Documentation/Curriculum/LAST_PAGE_INSERT_CONTENTION_LESSON.md). Der Pilot- und Runtimevertrag ist in [Tests/Runtime/README.md](../../../Tests/Runtime/README.md) dokumentiert. Übergreifende Sicherheits- und Recoveryregeln stehen im [Demo-Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md).
