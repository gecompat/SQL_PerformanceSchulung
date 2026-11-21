# QRY-006 – Runtime-Nachweis

| Merkmal | Wert |
|---|---|
| Status der Demo | `VALIDATED` – abgegrenzte SQL-Server-2019/2022/2025-Matrix |
| Nachweisart | lokaler Docker-Nachweis und GitHub-Actions-Runtimegate auf ephemeren Containern |
| Ausführungsdatum | 2026-11-21 |
| Workflow-/Actions-Nachweis | [Lauf 44896346186](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/44896346186), `workflow_dispatch`, Head `bbe60b8413c10c65f7facd365cf3188d8ee779ef`, alle statischen und Runtimejobs erfolgreich |
| SQL_Server_Lab-Szenario | nicht promotet |

## Matrix

Der vorhandene Runner `Tests/Runtime/run_qry006_null_semantics.py` wurde je Zielversion in einem frischen lokalen Docker-Container ausgeführt. Jeder Lauf führte das vollständige Manifest zweimal aus und prüfte zusätzlich den Compatibility-Level vor dem Cleanup sowie die unabhängige Abwesenheit der Testdatenbank nach jedem Lauf.

| SQL Server | Engine Major | Compatibility Level | Manifestläufe | Ergebnis | Cleanup |
|---|---:|---:|---:|---|---|
| 2019 | 15 | 150 | 2 | `PASS` | Container und Testdatenbank entfernt |
| 2022 | 16 | 160 | 2 | `PASS` | Container und Testdatenbank entfernt |
| 2025 | 17 | 170 | 2 | `PASS` | Container und Testdatenbank entfernt |

Damit bestanden lokal und im Runtimegate je sechs vollständige Manifestausführungen. Im Actions-Lauf wurde pro Engine ein frischer Linux-Container gestartet, die statischen Verträge liefen erfolgreich, und die beiden vollständigen Manifestausführungen bestanden. Die vorgesehenen Cleanup-Schritte entfernten alle drei Container erfolgreich. Das qualifiziert den abgegrenzten Demo-Vertrag als `VALIDATED` für die geprüften Linux-/Docker-Profile; es belegt keine Windows- oder SQL_Server_Lab-Szenariopromotion. Es wurde kein `scenario.json` und kein `READY_FOR_USER` erzeugt.

## Reproduzierbarkeit

Die lokale Ausführung erfolgt je Zielversion mit einem zufälligen Containernamen und einem temporären SQL-Login. Der GitHub-Actions-Workflow verwendet ebenfalls eigene ephemere Container und entfernt diese im Cleanup-Schritt. Zugangsdaten werden nicht protokolliert oder im Repository gespeichert.
