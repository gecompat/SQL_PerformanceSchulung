# QRY-006 – lokaler Runtime-Nachweis

| Merkmal | Wert |
|---|---|
| Status der Demo | `IMPLEMENTED` |
| Nachweisart | lokaler empirischer Nachweis auf ephemeren Docker-Containern |
| Ausführungsdatum | 2026-09-20 |
| Workflow-/Actions-Nachweis | nicht ausgeführt |
| SQL_Server_Lab-Szenario | nicht promotet |

## Matrix

Der vorhandene Runner `Tests/Runtime/run_qry006_null_semantics.py` wurde je Zielversion in einem frischen lokalen Docker-Container ausgeführt. Jeder Lauf führte das vollständige Manifest zweimal aus und prüfte zusätzlich den Compatibility-Level vor dem Cleanup sowie die unabhängige Abwesenheit der Testdatenbank nach jedem Lauf.

| SQL Server | Engine Major | Compatibility Level | Manifestläufe | Ergebnis | Cleanup |
|---|---:|---:|---:|---|---|
| 2019 | 15 | 150 | 2 | `PASS` | Container und Testdatenbank entfernt |
| 2022 | 16 | 160 | 2 | `PASS` | Container und Testdatenbank entfernt |
| 2025 | 17 | 170 | 2 | `PASS` | Container und Testdatenbank entfernt |

Damit sind für den lokalen Docker-Nachweis alle sechs vollständigen Manifestausführungen bestanden. Der Nachweis ändert den Implementierungsstatus nicht in `VALIDATED`: Für diese Einstufung ist weiterhin der im Projektvertrag vorgesehene Runtime-Gate-Nachweis maßgeblich. Es wurde kein Eintrag in `SQL_Server_Lab`, kein `scenario.json` und kein `READY_FOR_USER` erzeugt.

## Reproduzierbarkeit

Die Ausführung erfolgt je Zielversion mit einem zufälligen Containernamen und einem temporären SQL-Login. Der Container wird auch bei Fehlern im `finally`-Pfad entfernt; Zugangsdaten werden nicht protokolliert oder im Repository gespeichert. Der dokumentierte Nachweis behauptet keinen Lauf des GitHub-Actions-Workflows.
