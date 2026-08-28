# OPT-003 – Sampling, Skew und Histogrammgrenzen

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Versionen / CL | SQL Server 2019/150, 2022/160, 2025/170 |
| Sessions | 1 |
| Laufzeit / Profil | höchstens 300 Sekunden / `standard` |
| Infrastruktur | markierte Testdatenbank auf geteilter Testinstanz |

## Lernziel und Aussage

`LO-M02-02`, `CLM-023` und `CLM-024`: Eine Stichprobe, die Datenverteilung und die Begrenzung des Histogramms sind getrennte Einflussgrößen. Die Demo vergleicht dasselbe Statistikobjekt nach `SAMPLE 1 PERCENT` und `FULLSCAN`, prüft die Hot-Key-Verteilung und behauptet keine allgemeine Performanceüberlegenheit von `FULLSCAN`.

## Ablauf und Evidenz

Die Phasen bauen 200.000 deterministische Zeilen mit einem 90-Prozent-Hot-Key auf. Baseline und Demonstration sichern `rows`, `rows_sampled`, Histogrammschritte sowie die tatsächliche Hot-Key-Häufigkeit. Nach `FULLSCAN` müssen Stichprobenumfang und Tabellenumfang übereinstimmen; maximal 200 Histogrammschritte und die unveränderte Ergebniszeilenzahl bilden die Gegenprobe.

## Safety, Cleanup und Grenzen

Es werden weder Instanzoptionen noch globale Caches verändert. Das markergeprüfte Cleanup entfernt ausschließlich `SQLPERF_LAB_OPT003_<RunToken>`. Stichprobenschritte und einzelne Grenzwerte dürfen je Build variieren; nur Scope- und Mengeninvarianten werden abgenommen.

## Quellen und Traceability

`SRC-005` (`ACTIVE`, Abruf 2026-07-24) trägt Sampling, Header und Histogramm. Demo, Lernziel und Claims sind in der Traceability-Matrix verankert. Am 2026-08-29 liefen SQL Server 2019, 2022 und 2025 lokal in begrenzten Docker-Containern jeweils zweimal mit `PASS/OK`; Cleanup wurde nach jedem Lauf unabhängig geprüft.
