# QRY-013 – Anwendung langsam, SSMS schnell

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 gleichzeitige Session; zwei nacheinander ausgeführte Clientprofile |
| Laufzeitklasse | M |
| Testprofil | `TP-RUN` |
| Runtime-Abnahme | [Actions-Lauf 30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795): SQL Server 2019, 2022 und 2025 jeweils zweimal `PASS` |

## 1. Lernziel

Nach der Demo untersuchen die Teilnehmenden unterschiedliche Laufzeiten zweier Clients als Evidenzproblem entlang mindestens vier Kontextdimensionen – Datenbankkontext, SET-Optionen, Parameterwerte sowie Compile-Reihenfolge beziehungsweise Planidentität – und verwerfen eine plausible Ein-Ursachen-Hypothese anhand widersprechender Evidenz.

## 2. Fachliche Kernaussage

Gleicher Querytext garantiert keine identischen Ausführungsbedingungen. Ein abweichender Sessionkontext erzeugt einen zusätzlichen Cacheeintrag für dasselbe Objekt, obwohl das fachliche Ergebnis identisch bleibt. Derselbe Sessionkontext kann dennoch stark unterschiedliche Arbeitsmengen erzeugen, sobald ein wiederverwendeter Plan auf einen anderen Parameterwert trifft. Beide Dimensionen sind getrennt zu belegen.

## 3. Nichtziel

Die Demo behauptet nicht, dass ein bestimmter Client, Treiber oder SSMS die Ursache ist, und sie prüft keine realen Applikationen oder Treiberdefaults. Sie leitet keine pauschale Empfehlung wie „ARITHABORT immer auf ON setzen" ab. Die Profile heißen deshalb `CLIENT_PROFILE_A` und `CLIENT_PROFILE_B` und setzen ihre Optionen ausschließlich explizit.

## 4. Voraussetzungen

- SQL Server 2019 bis 2025 mit Compatibility Level 150, 160 oder 170.
- Berechtigung zum Anlegen der markergebundenen Testdatenbank.
- Versionsbewusste Server-State-Berechtigung: `VIEW SERVER PERFORMANCE STATE` ab SQL Server 2022, sonst `VIEW SERVER STATE`. Ohne diese Rechte endet der Preflight mit `SKIP_PERMISSION`.
- Mindestprofil zwei logische Kerne und 4 GB für die Instanz.

## 5. Sicherheits- und Abbruchrahmen

Sicherheitsstufe grün. Alle Objekte liegen in der markergebundenen Datenbank `SQLPERF_LAB_QRY013_<RunToken>`. Cachebereinigung erfolgt ausschließlich objektbezogen über `sp_recompile` auf das Demoobjekt; `DBCC FREEPROCCACHE` und `DBCC DROPCLEANBUFFERS` sind ausgeschlossen. Es werden keine Instanzeinstellungen verändert. Die Auswertung der Cacheattribute ist über `sys.dm_exec_procedure_stats` auf das Demoobjekt in der Demodatenbank eingegrenzt.

## 6. Synthetisches Datenmodell

`lab.SearchItem` mit 20 020 Zeilen und deterministisch schiefer Verteilung der `CategoryCode`-Werte: 20 Zeilen `RARE` und 20 000 Zeilen `CMMN`. `lab.SearchItemStatus` liefert den referenzierten Statusschlüssel. Ein nicht abdeckender nicht gruppierter Index auf `CategoryCode` macht die Selektivitätsdifferenz zwischen beiden Werten wirksam. `lab.Qry013Evidence` nimmt je Phase Sessionoptionen, Datenbankkontext, Cacheeintragszahl, Anzahl unterschiedlicher `set_options`, logische Lesevorgänge sowie Ergebnisumfang und Ergebnischecksumme auf.

## 7. Ablauf

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte und Zielkennung prüfen |
| Setup | `10_Setup.sql` | Markergebundene Datenbank, Suchdatenmodell, Prüfprozedur und Evidenztabelle anlegen |
| Baseline | `20_Baseline.sql` | `CLIENT_PROFILE_A` mit seltenem Parameterwert nach objektbezogener Neukompilierung |
| Demonstration | `30_Demonstration.sql` | `CLIENT_PROFILE_B` mit identischem Text und identischem Parameterwert |
| Observation | `40_Observation.sql` | `CLIENT_PROFILE_A` mit häufigem Parameterwert; widerlegt die Ein-Ursachen-Hypothese |
| Mitigation | `50_Mitigation.sql` | Angleichung genau einer Kontextdimension für beide Profile |
| Comparison | `60_Comparison.sql` | Wiederholung nach Angleichung und Gesamtbewertung beider Dimensionen |
| Cleanup | `90_Cleanup.sql` | Markergeprüfter, idempotenter Abbau |

## 8. Erwartete Beobachtung

- Baseline: genau ein Cacheeintrag für `lab.usp_Qry013Probe`, 20 Trefferzeilen.
- Demonstration: zweiter Cacheeintrag mit abweichendem `set_options`-Wert bei identischer Ergebnischecksumme.
- Observation: unveränderter Sessionkontext, keine zusätzliche Cacheentität, aber deutlich höhere logische Lesevorgänge und 20 000 Trefferzeilen.
- Mitigation: nach Angleichung und objektbezogener Neukompilierung genau ein Cacheeintrag für beide Profile.
- Comparison: weniger Cacheeinträge als in der Demonstration, unveränderte Ergebnischecksumme, weiterhin sichtbare Parameterabhängigkeit.

## 9. Interpretation

Der zusätzliche Cacheeintrag folgt aus dem Sessionkontext, nicht aus dem Querytext. Er allein erklärt jedoch nicht jede Laufzeitdifferenz: Die Observation zeigt bei identischem Kontext eine andere Arbeitsmenge, weil ein wiederverwendeter Plan mit einem anderen Parameterwert ausgeführt wird. Die Angleichung des Kontexts beseitigt deshalb den zusätzlichen Cacheeintrag, nicht aber die Parameterabhängigkeit. Eine belastbare Diagnose benennt beide Dimensionen getrennt und weist zusätzlich Datenbankkontext und Compile-Reihenfolge nach.

## 10. Cleanup und Wiederherstellung

`90_Cleanup.sql` liest die vier Eigentumsmarker `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId` und `SQLPERF.RunToken` aus der Zieldatenbank und entfernt sie nur bei vollständiger Übereinstimmung. Fehlt die Datenbank, endet der Cleanup idempotent mit `PASS`.

## 11. Tests

`Tests/Static/validate_adv008_qry013.py` prüft Bündelstruktur, Manifestvertrag, Profiltrennung, Verbot globaler Cachebereinigung, Zusammenfassungszeilen und Cleanup-Idempotenz. Die Runtime-Abnahme erfolgt über `Tests/Runtime` auf SQL Server 2019, 2022 und 2025.

## 12. Bekannte Grenzen

Die Zuordnung eines Cacheeintrags zu einem Sessionkontext ist nur solange auswertbar, wie der Eintrag im Cache verbleibt; unter Speicherdruck endet die Phase mit `SKIP_EVIDENCE_MISSING`. Die logischen Lesevorgänge stammen aus `sys.dm_exec_procedure_stats` und sind eine Instanzsicht auf die letzte Ausführung, keine sessiongenaue Messung. Bleibt die Arbeitsmenge trotz Planwiederverwendung gleich, endet die Observation mit `WARN_EMPIRICAL_VARIANCE` statt mit einer behaupteten Verschlechterung.

## 13. Quellen

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-001` | Ausführungspläne und Sessionkontext |
| `SRC-027` | Kompilierung und Parameterverhalten |
| `SRC-040` | Planattribute und Cacheschlüssel |
| `SRC-046` | Unterschiedliche Laufzeit zwischen Anwendung und Werkzeug |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M03-07` |
| Claims | `ADV-CLM-013`, `ADV-CLM-014`, `ADV-CLM-015`, `ADV-CLM-016` |
| Demo-ID | `QRY-013` |
| Testprofil | `TP-RUN` |
| Folienspezifikation | `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03.md` |
