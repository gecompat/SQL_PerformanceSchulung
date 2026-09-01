# OPT-010 – Optional Parameter Plan Optimization

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019 und 2022 (kontrollierter `SKIP_VERSION`), 2025 |
| Compatibility Level | 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 gleichzeitige Session; vier nacheinander verglichene Planformen |
| Laufzeitklasse | M |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Runtime-Abnahme | [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969): SQL Server 2025 zweimal `PASS`; 2019 und 2022 jeweils zweimal kontrolliert `SKIP_VERSION` |

## 1. Lernziel

Nach der Demo erklären die Teilnehmenden, warum ein optionales Parameterprädikat der Form `(Spalte = @p OR @p IS NULL)` ohne zusätzliche Optimierung genau eine Planform erzwingt, wodurch sich Optional Parameter Plan Optimization von der parametersensitiven Planoptimierung unterscheidet und wie sich Dispatcherplan, optionales Parameterprädikat und Query Variants im Plancache nachweisen lassen.

## 2. Fachliche Kernaussage

Ein optionales Parameterprädikat ist kein Sonderfall des Parameter Sniffing. Für den belegten Parameter wäre eine Suche gültig, für den offenen Parameter nicht; da beide Zustände denselben Querytext teilen, muss die eine zwischengespeicherte Planform die volle Prüfbreite abdecken. Der belegte Aufruf zahlt deshalb den Aufwand des offenen Aufrufs mit, und zwar unabhängig von der Kompilierungsreihenfolge. Optional Parameter Plan Optimization ersetzt in SQL Server 2025 unter Compatibility Level 170 diese eine Planform durch einen Dispatcherplan mit einer Query Variant je NULL-Zustand der optionalen Parameter; nach der Variantenauswahl wird das Prädikat konstant gefaltet. Das Verfahren verändert die Kosten, niemals das Ergebnis.

## 3. Nichtziel

Die Demo bewertet weder `OPTION (RECOMPILE)` noch sicher parameterisiertes dynamisches SQL als Alternative; dieser Vergleich gehört zu `QRY-004`. Die parametersensitive Planoptimierung für schiefe Gleichheitsprädikate bleibt `OPT-009` vorbehalten; OPT-010 arbeitet bewusst mit einer gleichmäßigen Verteilung, damit die beobachtete Wirkung nicht der Schiefe zugeschrieben werden kann. Die Demo behauptet nicht, dass die Optimierung Abfragen allgemein beschleunigt, und sie erzwingt die Variantenbildung nicht durch undokumentierte Eingriffe. Erweiterte Ereignisse und Query-Store-Sichten sind kein Bestandteil dieses abgegrenzten Schnitts.

## 4. Voraussetzungen

- SQL Server 2025 mit Compatibility Level 170. SQL Server 2019 und 2022 enden im Preflight mit `SKIP_VERSION`.
- Datenbankbezogene Konfiguration `OPTIONAL_PARAMETER_OPTIMIZATION`; sie ist unter Compatibility Level 170 standardmäßig eingeschaltet und wird für die Baseline ausdrücklich abgeschaltet.
- Berechtigung zum Anlegen der markergebundenen Testdatenbank.
- `VIEW SERVER PERFORMANCE STATE`; ohne diese Berechtigung endet der Preflight mit `SKIP_PERMISSION`.
- Mindestprofil zwei logische Kerne und 4 GB für die Instanz.

## 5. Sicherheits- und Abbruchrahmen

Sicherheitsstufe grün. Alle Objekte liegen in der markergebundenen Datenbank `SQLPERF_LAB_OPT010_<RunToken>`. Die Einstellung `OPTIONAL_PARAMETER_OPTIMIZATION` wird ausschließlich als datenbankbezogene Konfiguration dieser Testdatenbank verändert; Instanzeinstellungen bleiben unberührt. Die Einstellung `PARAMETER_SENSITIVE_PLAN_OPTIMIZATION` wird bewusst nicht angefasst, weil beide Verfahren dieselbe Mehrplaninfrastruktur nutzen; die Zuordnung erfolgt stattdessen über die Elementnamen im Ausführungsplan. Planentwertung erfolgt ausschließlich objektbezogen über `sp_recompile`; `DBCC FREEPROCCACHE` und `DBCC DROPCLEANBUFFERS` sind ausgeschlossen. Die Planauswertung liest ausschließlich Einträge, die über einen Kommentarmarker im Anweisungstext oder über den Namen der Demotabelle eindeutig dieser Demo zuzuordnen sind.

## 6. Synthetisches Datenmodell

`lab.OppoListing` mit 100 000 Zeilen und bewusst gleichmäßiger Verteilung: 2 000 Agenten zu je genau 50 Zeilen. Die Gleichverteilung ist Teil der Aussage, denn sie schließt aus, dass die parametersensitive Planoptimierung greift; jede beobachtete Variantenbildung ist damit dem optionalen Prädikat zuzuordnen. Der nicht abdeckende nicht gruppierte Index `IX_Opt010_OppoListing_AgentId` macht den Unterschied zwischen Suche mit Schlüsselsuche und vollständiger Prüfung wirksam. Die Statistik wird mit `FULLSCAN` aktualisiert. `lab.Opt010Evidence` nimmt je Phase und Parameterbelegung Ergebnisumfang, Ergebnischecksumme, logische Lesevorgänge, Zahl der zwischengespeicherten Planformen, Zahl der Dispatcherpläne, Zahl der Query Variants, Zahl der Pläne mit optionalem beziehungsweise parametersensitivem Prädikat, die Anzahl optionaler Prädikate im Dispatcher und die beobachtete `QueryVariantID` auf.

## 7. Ablauf

Vier Prozeduren tragen denselben Querytext und unterscheiden sich nur im Kommentarmarker beziehungsweise im Abwahlhinweis:

| Objekt | Kennzeichnung |
|---|---|
| `lab.usp_Opt010SearchSelectiveFirst` | Baseline; belegter Parameter kompiliert zuerst, Optimierung abgeschaltet |
| `lab.usp_Opt010SearchNullFirst` | Demonstration; offener Parameter kompiliert zuerst, Optimierung abgeschaltet |
| `lab.usp_Opt010SearchOppo` | Gegenmaßnahme; eingeschaltete Optional Parameter Plan Optimization |
| `lab.usp_Opt010SearchOptOut` | Vergleich; `USE HINT ('DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION')` |

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte und Zielkennung prüfen |
| Setup | `10_Setup.sql` | Markergebundene Datenbank, gleichverteiltes Modell, vier Abfrageobjekte und Evidenztabelle anlegen; Optimierung abschalten |
| Baseline | `20_Baseline.sql` | belegter Parameter zuerst; eine Planform mit voller Prüfbreite |
| Demonstration | `30_Demonstration.sql` | offener Parameter zuerst; identische Planform, wirkungslose Reihenfolge |
| Observation | `40_Observation.sql` | Kostengleichheit beider Parameterzustände, Reihenfolgeunabhängigkeit, Ergebnisgleichheit |
| Mitigation | `50_Mitigation.sql` | Optimierung einschalten; Dispatcherplan, optionales Parameterprädikat und Query Variants nachweisen |
| Comparison | `60_Comparison.sql` | Ergebnisvertrag über alle Phasen, dokumentierte Abwahl auf Abfrageebene und dokumentierte Ausschlussgründe |
| Cleanup | `90_Cleanup.sql` | Markergeprüfter, idempotenter Abbau |

## 8. Erwartete Beobachtung

- Baseline: genau eine Planform, 50 und 100 000 Trefferzeilen, vergleichbare logische Lesevorgänge für beide Parameterbelegungen, kein Dispatcherplan.
- Demonstration: unverändert eine Planform bei identischen Ergebnissen; die Lesevorgänge des belegten Parameters weichen um höchstens fünf Prozent von der Baseline ab.
- Observation: Kostenverhältnis zwischen belegtem und offenem Parameter nahe eins bei identischen Prüfsummen und ohne jeden Dispatcherplan.
- Mitigation: mindestens ein Dispatcherplan mit mindestens einem optionalen Parameterprädikat, mindestens zwei Query Variants, ausgewiesene `QueryVariantID` und niedrigere Lesevorgänge des belegten Parameters als in der Baseline.
- Comparison: je Parameterbelegung genau eine Trefferzahl und eine Prüfsumme über vier Phasen sowie kein Dispatcherplan für die ausdrücklich abgewählte Abfrage.

## 9. Interpretation

Der entscheidende Unterschied zu `OPT-009` liegt im Auswahlkriterium. Die parametersensitive Planoptimierung entscheidet anhand geschätzter Kardinalitätsunterschiede bei Gleichheits- oder Bereichsprädikaten; Optional Parameter Plan Optimization entscheidet anhand der Frage, ob ein Parameter `NULL` ist. Deshalb hilft bei einem optionalen Prädikat auch keine andere Kompilierungsreihenfolge: Es gibt keine Suchplanform, die für beide Parameterzustände gültig wäre. Erst eine zweite Planform löst das Problem. Beide Verfahren nutzen dieselbe Mehrplaninfrastruktur, sind aber unabhängig voneinander; eine Abfrage kann von beiden, von einem oder von keinem profitieren. Ob die Optimierung greift, entscheidet der Optimierer, weshalb die Variantenbildung nachgewiesen und nicht vorausgesetzt wird.

## 10. Cleanup und Wiederherstellung

`90_Cleanup.sql` liest die vier Eigentumsmarker `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId` und `SQLPERF.RunToken` aus der Zieldatenbank und entfernt sie nur bei vollständiger Übereinstimmung. Fehlt die Datenbank, endet der Cleanup idempotent mit `PASS`. Die datenbankbezogene Konfiguration wird nicht zurückgesetzt, weil die gesamte Datenbank entfernt wird.

## 11. Tests

`Tests/Static/validate_adv008_opt010.py` prüft Bündelstruktur, Manifestvertrag, Phasenzuordnung, Markertrennung, das Verbot instanzweiter Planentwertung, die ausschließliche Verwendung vertraglicher Statuscodes, Zusammenfassungszeilen und Cleanup-Idempotenz. Die Runtime-Abnahme erfolgt über `Tests/Runtime/run_adv008_opt010.py` auf SQL Server 2019, 2022 und 2025; auf 2019 und 2022 wird der kontrollierte `SKIP_VERSION` erwartet.

## 12. Bekannte Grenzen

Dispatcher- und Variantenevidenz stammt aus `sys.dm_exec_cached_plans`, `sys.dm_exec_query_plan` und `sys.dm_exec_query_stats`. Das ist eine Instanzsicht auf den aktuellen Cacheinhalt und keine sessiongenaue Messung; unter Speicherdruck endet die betroffene Phase mit `SKIP_EVIDENCE_MISSING`. Die Zahl der Query Variants wird über den Namen der Demotabelle bestimmt und ist deshalb datenbankweit, nicht phasenbezogen; die Abwahl auf Abfrageebene wird daher über die markerbezogene Zahl der Dispatcherpläne belegt. Stuft der Optimierer die Abfrage trotz passender Version nicht als geeignet ein, endet die Gegenmaßnahme mit `SKIP_EVIDENCE_MISSING` und ausgewiesener Evidenz. Enthält der Dispatcherplan zusätzlich ein parametersensitives Prädikat, endet die Phase mit `WARN_EMPIRICAL_VARIANCE`, weil die Wirkung dann nicht eindeutig zuzuordnen ist. Laut Produktdokumentation wird die Optimierung außerdem nicht angewendet bei Verwendung lokaler Variablen statt Parameter, bei `OPTION (RECOMPILE)`, bei `SET ANSI_NULLS OFF` und bei automatisch parametrisierten Anweisungen; die Demo arbeitet daher durchgängig mit `SET ANSI_NULLS ON` und echten Prozedurparametern. Die erweiterten Ereignisse zur Übersprungsbegründung werden bewusst nicht ausgewertet, solange die Pilotabnahme der Ereignisspur offen ist.

## 13. Quellen

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-007` | Funktionsmatrix der intelligenten Abfrageverarbeitung, Versions- und Compatibility-Level-Grenzen |
| `SRC-026` | Optional Parameter Plan Optimization: Voraussetzungen, Dispatcherplan, optionales Parameterprädikat, Abwahlhinweis und Ausschlussgründe |
| `SRC-049` | empirische Einordnung optionaler Parameter und ihrer Behandlungsmuster |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-020` |
| Demo-ID | `OPT-010` |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Folienspezifikation | `Documentation/Curriculum/ADV_011_SLIDE_SPECIFICATION_M03_LO08_OPPO.md` |
| Folien im aktiven Deck | Anzeigepositionen 98 bis 101 (`SLD-M03-131` bis `SLD-M03-134`) |
| Abnahmestand | `Documentation/Project_Planning/ADV_008_OPT_010_REVIEW.md` |
