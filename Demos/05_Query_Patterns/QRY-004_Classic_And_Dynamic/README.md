# QRY-004 – Catch-all, `OPTION (RECOMPILE)` und sicheres dynamisches SQL

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED` |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 gleichzeitige Session; drei nacheinander verglichene Strategien |
| Laufzeitklasse | M |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Runtime-Abnahme | offen; SQL Server 2019, 2022 und 2025 |

## 1. Lernziel

Nach der Demo wählen die Teilnehmenden für optionale Suchbedingungen eine Implementierungsstrategie anhand von Verteilung, Wiederverwendung, Compilearbeit und Sicherheit aus und begründen die Wahl an gemessener Evidenz statt an einer allgemeinen Rangfolge.

## 2. Fachliche Kernaussage

Ein einziger statischer Querytext mit optionalen Prädikaten erzeugt eine einzige Planform, die für alle Selektivitäten wiederverwendet wird. `OPTION (RECOMPILE)` gibt diese Wiederverwendung auf und erhält dafür eine je Ausführung passende Optimierung. Sicher parameterisiertes dynamisches SQL erzeugt je Filterform genau eine Statementform, bindet alle Werte als Parameter und bleibt damit sowohl wiederverwendbar als auch injektionssicher. Alle drei Strategien liefern dasselbe fachliche Ergebnis.

## 3. Nichtziel

Die Demo stellt keine Rangfolge der drei Strategien auf und behauptet nicht, `OPTION (RECOMPILE)` sei allgemein schnell oder allgemein teuer. Sie bewertet weder Parameter Sensitive Plan Optimization noch Optional Parameter Plan Optimization; diese Verfahren gehören zu `OPT-009` und `OPT-010`. Sie verwendet keine absichtlich fehlerhafte Abfrage und keine unsichere Stringkonkatenation als Gegenbeispiel.

## 4. Voraussetzungen

- SQL Server 2019 bis 2025 mit Compatibility Level 150, 160 oder 170.
- Berechtigung zum Anlegen der markergebundenen Testdatenbank.
- Versionsbewusste Server-State-Berechtigung: `VIEW SERVER PERFORMANCE STATE` ab SQL Server 2022, sonst `VIEW SERVER STATE`. Ohne diese Rechte endet der Preflight mit `SKIP_PERMISSION`.
- Mindestprofil zwei logische Kerne und 4 GB für die Instanz.

## 5. Sicherheits- und Abbruchrahmen

Sicherheitsstufe grün. Alle Objekte liegen in der markergebundenen Datenbank `SQLPERF_LAB_QRY004_<RunToken>`. Planentwertung erfolgt ausschließlich objektbezogen über `sp_recompile`; `DBCC FREEPROCCACHE` und `DBCC DROPCLEANBUFFERS` sind ausgeschlossen. Instanzeinstellungen werden nicht verändert. Dynamisches SQL wird ausschließlich aus einer Positivliste zusammengesetzt; Werte werden nie in den Statementtext geschrieben, sondern über `sys.sp_executesql` gebunden. Eine unbekannte Filterdefinition führt zu einem kontrollierten Abbruch mit `THROW 51000`.

## 6. Synthetisches Datenmodell

`lab.SearchOrder` mit 20 000 Zeilen: 20 Zeilen `RARE` und 19 980 Zeilen `CMMN` im Feld `CategoryCode`, dazu ein gleichverteilter `StatusCode` mit je 4 000 Zeilen. `lab.SearchStatus` liefert den referenzierten Statusschlüssel. Zwei nicht abdeckende nicht gruppierte Indizes auf `CategoryCode` und `StatusCode` machen den Selektivitätsunterschied wirksam. `lab.Qry004AllowedFilter` enthält die zwei zugelassenen Prädikatsbausteine. `lab.Qry004Evidence` nimmt je Phase, Strategie und Filterkombination Ergebnisumfang, Ergebnischecksumme, logische Lesevorgänge, Zahl der Planformen, Ausführungszahl, CPU-Zeit und die Literalfreiheit des zwischengespeicherten Statementtexts auf.

## 7. Ablauf

Die Evidenztabelle unterscheidet die drei Strategien über die Werte `CATCHALL`, `RECOMPILE` und `DYNAMIC`:

| Strategie | Objekt | Kennzeichnung |
|---|---|---|
| `CATCHALL` | `lab.usp_Qry004CatchAll` | statischer Querytext mit optionalen Prädikaten |
| `RECOMPILE` | `lab.usp_Qry004Recompile` | identischer Querytext mit `OPTION (RECOMPILE)` |
| `DYNAMIC` | `lab.usp_Qry004Dynamic` | Positivliste plus Parameterbindung über `sys.sp_executesql` |

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte und Zielkennung prüfen |
| Setup | `10_Setup.sql` | Markergebundene Datenbank, Suchdatenmodell, Positivliste, drei Strategieprozeduren und Evidenztabelle anlegen |
| Baseline | `20_Baseline.sql` | Catch-all-Prädikat mit drei Selektivitäten nach objektbezogener Neukompilierung |
| Demonstration | `30_Demonstration.sql` | identischer Querytext mit `OPTION (RECOMPILE)` und denselben drei Kombinationen |
| Observation | `40_Observation.sql` | 25 ungefilterte Wiederholungen je Variante; Preis der Neuoptimierung bei identischer Arbeitsmenge |
| Mitigation | `50_Mitigation.sql` | sicher parameterisiertes dynamisches SQL einschließlich abgewiesener Positivlistenverletzung |
| Comparison | `60_Comparison.sql` | Strategievergleich, fortbestehende Wiederverwendung und Ergebnisvertrag |
| Cleanup | `90_Cleanup.sql` | Markergeprüfter, idempotenter Abbau |

## 8. Erwartete Beobachtung

- Baseline: genau eine Planform für drei Kombinationen; 20, 19 980 und 4 000 Trefferzeilen.
- Demonstration: identische Ergebnisse und Checksummen wie die Baseline, jedoch weniger logische Lesevorgänge für den selektiven Wert.
- Observation: je 25 gezählte Ausführungen, unveränderte Planformzahl für die Catch-all-Variante und höhere CPU je Ausführung für die neu optimierte Variante.
- Mitigation: zwei Statementformen für drei Ausführungen, keine Filterwerte im zwischengespeicherten Statementtext, kontrollierte Abweisung einer unbekannten Filterdefinition.
- Comparison: durchgängige Ergebnisgleichheit über alle drei Strategien bei unverändert einer Catch-all-Planform.

## 9. Interpretation

Die Catch-all-Formulierung ist nicht falsch, sondern bindet sich an eine einzige Planform, die für alle Selektivitäten gleich gut oder gleich schlecht passt. `OPTION (RECOMPILE)` löst diese Bindung und zahlt dafür mit Compilearbeit je Ausführung; das lohnt sich bei stark schwankender Selektivität und seltenen Ausführungen, nicht bei hoher Ausführungsfrequenz. Sicheres dynamisches SQL trennt die Filterform von den Werten: Es begrenzt die Zahl der Statementformen auf die Zahl der Filterformen und bleibt durch Parameterbindung injektionssicher. Die Strategiewahl folgt damit Verteilung, Ausführungsfrequenz, Wartbarkeit und Sicherheit.

## 10. Cleanup und Wiederherstellung

`90_Cleanup.sql` liest die vier Eigentumsmarker `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId` und `SQLPERF.RunToken` aus der Zieldatenbank und entfernt sie nur bei vollständiger Übereinstimmung. Fehlt die Datenbank, endet der Cleanup idempotent mit `PASS`.

## 11. Tests

`Tests/Static/validate_adv008_qry004.py` prüft Bündelstruktur, Manifestvertrag, Strategietrennung, das Verbot von Wertkonkatenation und direkter Stringausführung, Zusammenfassungszeilen und Cleanup-Idempotenz. Die Runtime-Abnahme erfolgt über `Tests/Runtime/run_adv008_qry004.py` auf SQL Server 2019, 2022 und 2025.

## 12. Bekannte Grenzen

Die Planform- und Lesewerte stammen aus `sys.dm_exec_procedure_stats` beziehungsweise aus markerbezogenen Einträgen in `sys.dm_exec_cached_plans` und `sys.dm_exec_query_stats`. Sie sind eine Instanzsicht auf die jeweils letzte Ausführung und keine sessiongenaue Messung; unter Speicherdruck endet die betroffene Phase mit `SKIP_EVIDENCE_MISSING`. Wählt die Neuoptimierung keine günstigere Zugriffsform für den selektiven Wert, endet die Demonstration mit `WARN_EMPIRICAL_VARIANCE` statt mit einer behaupteten Verbesserung. Ist der Compilierungsanteil nicht von der Messstreuung zu trennen, endet die Observation ebenfalls mit `WARN_EMPIRICAL_VARIANCE`.

## 13. Quellen

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-001` | Ausführungspläne, Kompilierung und Planwiederverwendung |
| `SRC-007` | Parameter, Variablen und Optimiererinformation |
| `SRC-045` | Dynamische Suchbedingungen, Recompile und parameterisiertes dynamisches SQL |
| `SRC-049` | Catch-all-Prädikate und Schätzfehler bei optionalen Parametern |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-016`, `ADV-CLM-017`, `ADV-CLM-018` |
| Demo-ID | `QRY-004` |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Folienspezifikation | `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03_LO08.md` |
