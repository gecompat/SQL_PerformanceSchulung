# OPT-005 – Ascending Key und Statistikpflege

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Versionen / CL | SQL Server 2019/150, 2022/160, 2025/170 |
| Sessions | 1 |
| Laufzeit / Profil | höchstens 300 Sekunden / `standard` |

## Vertrag

`LO-M02-02`, `CLM-023` und `CLM-024`: Neue Schlüsselwerte können außerhalb der zuletzt materialisierten Histogrammgrenze liegen. Die Demo hält Baseline, Out-of-range-Inserts, Änderungszähler, Datenbankoption `AUTO_UPDATE_STATISTICS_ASYNC` und explizite Aktualisierung getrennt fest. Sie lehrt keine universelle Aktualisierungsschwelle und behauptet nicht, asynchrone Pflege sei stets schneller.

Die Option wird ausschließlich in der markergebundenen Testdatenbank gesetzt; Cleanup entfernt die Datenbank. Der beobachtete Hintergrundzeitpunkt ist build- und lastabhängig. Deshalb ist er keine PASS-Bedingung. `SRC-005` ist `ACTIVE`. Am 2026-08-29 liefen SQL Server 2019, 2022 und 2025 lokal jeweils zweimal mit `PASS/OK` und unabhängiger Cleanup-Prüfung.
