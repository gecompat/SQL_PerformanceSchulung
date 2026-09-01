# W-COV-001 – Verbleibende curriculare Demoabdeckung

## Ergebnis

Die neun vorgesehenen Demos sind in der verbindlichen Reihenfolge als eigenständige, runtimefähige Pakete implementiert und nach je zwei Docker-Läufen auf SQL Server 2019, 2022 und 2025 `VALIDATED`.

| Reihenfolge | Demo | Status | Quellenstatus | Safety | Infrastruktur | Curriculum | Scopeentscheidung |
|---:|---|---|---|---|---|---|---|
| 1 | `OPT-003` | `VALIDATED` | `SRC-005` `ACTIVE` | `GREEN` | T-SQL-Testdatenbank | `LO-M02-02`, `CLM-023/024` | Sample, Fullscan, Skew und Histogrammgrenze |
| 2 | `OPT-005` | `VALIDATED` | `SRC-005` `ACTIVE` | `GREEN` | T-SQL-Testdatenbank | `LO-M02-02`, `CLM-023/024` | Ascending Key, Änderungszähler, Sync-/Async-Konfiguration |
| 3 | `CON-006` | `VALIDATED` | `SRC-004` `ACTIVE` | `YELLOW` | frische Instanz, drei Sessions | `LO-M05-03`, `CLM-067` | Fehler 1205, Opfervertrag, Deadlock-XML-Evidenz, geordnete Gegenprobe |
| 4 | `CON-009` | `VALIDATED` | `SRC-029`, `SRC-004`, `SRC-031` `ACTIVE` | `YELLOW` | frische Performance-Instanz | `LO-M05-04`, `CLM-068`, `ADV-CLM-027` | User-/Internal-Objects und Version Store; Instanzkonfiguration zurückgestellt |
| 5 | `IDX-006` | `VALIDATED` | `SRC-014/015` `ACTIVE` | `YELLOW` | frische Instanz | `LO-M04-05`, `CLM-057/058` | Splits, Density, Fragmentierung und Workloadwirkung ohne feste Schwelle |
| 6 | `IDX-010` | `VALIDATED` | `SRC-016/017/015` `ACTIVE` | `YELLOW` | begrenztes Performance-Containerprofil | `LO-M04-06/07`, `CLM-060/061` | klassische CCI-Segmente; Ordered NCCI bleibt `DEFER` |
| 7 | `STL-008` | `VALIDATED` | `SRC-033` `ACTIVE` | `RED` | dedizierte Wegwerf-Containerinstanz | Storage-/Log-Block | VLF und Growth; keine Storage-Latenzbehauptung |
| 8 | `STL-009` | `VALIDATED` | `SRC-033` `ACTIVE` | `YELLOW` | frische Instanz | Storage-/Log-Block | Einzelcommit/Batch, Log-File-Delta, zeitgebundenes `WRITELOG`-Delta |
| 9 | `RES-007` | `VALIDATED` | `SRC-035/036/051` `ACTIVE` | `YELLOW` | frische Instanz, drei Sessions | `LO-M06-01/08`, `CLM-073`, `ADV-CLM-037` | Task-/Request-/Instanzscope mit Freigabe-Gegenprobe |

## Abnahmevertrag

`Tests/Runtime/run_w_cov_001.py` führt genau eine ausgewählte Demo zweimal aus, erhält `PASS`, `WARN` und kontrollierte `SKIP`-Codes wahrheitsgetreu und prüft das Cleanup unabhängig. `.github/workflows/w-cov-001.yml` bildet neun Demos auf drei Zielversionen ab. Der rote Schnitt durchläuft ausschließlich die bestätigte, dedizierte Wegwerf-Lane.

`Tests/Static/validate_w_cov_001.py` prüft Dateien, Phasenreferenzen, Kennung, Safety, aktive Quellen, Eigentumsmarker, Cleanup, Kataloge und die Deferred-Grenzen. Zusätzlich bleiben Registry-, Governance-, Privacy-, Metadaten- und Diff-Prüfungen verbindlich.

`Tests/Static/test_w_cov_001_runner.py` deckt `PASS`, `WARN_EMPIRICAL_VARIANCE`, kontrollierten `SKIP`, `FAIL`, fehlende Summary, nonzero Exitcode sowie die Weitergabe der gelben und roten Bestätigungsflags ab.

## Runtime-Evidenz vom 2026-08-29

Die Läufe verwendeten Docker 29.7.2, die lokalen Microsoft-Images `2019-latest`, `2022-latest` und `2025-latest`, vier CPUs und 8 GB RAM. Jeder Runner führte zwei Wiederholungen aus und prüfte nach jeder Wiederholung aus `master`, dass die erwartete `SQLPERF_LAB_*`-Datenbank nicht mehr existiert. Rohoutput und Zugangsdaten wurden nicht persistiert.

| Demo | 2019 | 2022 | 2025 | Bewertung |
|---|---|---|---|---|
| `OPT-003`, `OPT-005`, `CON-006`, `IDX-010`, `STL-008`, `STL-009`, `RES-007` | 2× `PASS/OK` | 2× `PASS/OK` | 2× `PASS/OK` | Kernevidenz vollständig |
| `IDX-006` | 2× `WARN_EMPIRICAL_VARIANCE` | 2× `WARN_EMPIRICAL_VARIANCE` | 2× `WARN_EMPIRICAL_VARIANCE` | Ergebnis, Split-/Density-/Fragmentierungsmessung und Cleanup vollständig; keine universelle Fill-Factor-Richtung behauptet |
| `CON-009` | 2× `PASS/OK` | 2× `PASS/OK` | 2× `PASS/OK` | Kernevidenz nach Stabilisierung der internen Task-Allokation vollständig |

## GitHub-Actions-Nachweis

[Actions-Lauf 33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644) bestätigte für alle neun Demos die vollständige 2019/2022/2025-Matrix. `CON-009` endete dabei auf allen drei Zielversionen jeweils zweimal mit `PASS/OK`; die unabhängigen Cleanup-Prüfungen waren erfolgreich.
