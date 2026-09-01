# OPT-009 – Parameter Sensitive Plan Optimization

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019 (kontrollierter `SKIP_VERSION`), 2022 und 2025 |
| Compatibility Level | 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 gleichzeitige Session; vier nacheinander verglichene Planformen |
| Laufzeitklasse | M |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Runtime-Abnahme | [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564): SQL Server 2022 und 2025 jeweils zweimal `PASS`; 2019 zweimal kontrolliert `SKIP_VERSION` |

## 1. Lernziel

Nach der Demo erklären die Teilnehmenden, unter welchen dokumentierten Voraussetzungen SQL Server für ein schiefes Gleichheitsprädikat mehrere Planformen desselben Querytexts vorhält, wie Dispatcherplan und Query Variants im Plancache nachweisbar sind und warum die Eignung einer Abfrage nachgewiesen und nicht angenommen wird.

## 2. Fachliche Kernaussage

Ohne Parametersensitivität besitzt ein Querytext genau eine zwischengespeicherte Planform. Bei stark schiefer Verteilung entscheidet allein die Kompilierungsreihenfolge, welche Parameterbelegung benachteiligt wird; die Wahl einer anderen ersten Belegung verschiebt den Schaden, sie behebt ihn nicht. Parameter Sensitive Plan Optimization ersetzt diese eine Planform durch einen Dispatcherplan und mehrere Query Variants, die anhand von Kardinalitätsgrenzen ausgewählt werden. Das Verfahren gilt ausschließlich für Gleichheitsprädikate, für höchstens drei Prädikate je Abfrage und für je drei Kardinalitätsbänder; es verändert die Kosten, niemals das Ergebnis.

## 3. Nichtziel

Die Demo behauptet nicht, dass Parameter Sensitive Plan Optimization Abfragen allgemein beschleunigt oder Parameter Sniffing vollständig auflöst. Sie bewertet weder `OPTION (RECOMPILE)` noch sicher parameterisiertes dynamisches SQL; dieser Vergleich gehört zu `QRY-004`. Optional Parameter Plan Optimization bleibt `OPT-010` vorbehalten. Sie erzwingt die Variantenbildung nicht durch undokumentierte Eingriffe und verwendet in diesem abgegrenzten Schnitt keine Query-Store-Sichten.

## 4. Voraussetzungen

- SQL Server 2022 oder 2025 mit Compatibility Level 160 beziehungsweise 170. SQL Server 2019 endet im Preflight mit `SKIP_VERSION`.
- Berechtigung zum Anlegen der markergebundenen Testdatenbank.
- `VIEW SERVER PERFORMANCE STATE`; ohne diese Berechtigung endet der Preflight mit `SKIP_PERMISSION`.
- Mindestprofil zwei logische Kerne und 4 GB für die Instanz.

## 5. Sicherheits- und Abbruchrahmen

Sicherheitsstufe grün. Alle Objekte liegen in der markergebundenen Datenbank `SQLPERF_LAB_OPT009_<RunToken>`. Die Einstellung `PARAMETER_SENSITIVE_PLAN_OPTIMIZATION` wird ausschließlich als Datenbankeinstellung dieser Testdatenbank verändert; Instanzeinstellungen bleiben unberührt. Planentwertung erfolgt ausschließlich objektbezogen über `sp_recompile`; `DBCC FREEPROCCACHE` und `DBCC DROPCLEANBUFFERS` sind ausgeschlossen. Die Planauswertung liest ausschließlich Einträge, die über einen Kommentarmarker im Anweisungstext oder über den Namen der Demotabelle eindeutig dieser Demo zuzuordnen sind.

## 6. Synthetisches Datenmodell

`lab.PspOrder` mit 100 000 Zeilen und ausgeprägter Schiefe: `OwnerId = 1` trägt 99 000 Zeilen, die `OwnerId`-Werte 2 bis 201 tragen je fünf Zeilen. Der nicht abdeckende nicht gruppierte Index `IX_Opt009_PspOrder_OwnerId` macht den Selektivitätsunterschied wirksam, weil die Nutzlast nur über eine Schlüsselsuche erreichbar ist. Die Statistik wird mit `FULLSCAN` aktualisiert, damit die Schiefe im Histogramm sichtbar ist. `lab.Opt009Evidence` nimmt je Phase und Parameterwert Ergebnisumfang, Ergebnischecksumme, logische Lesevorgänge, Zahl der zwischengespeicherten Planformen, Zahl der Dispatcherpläne, Zahl der Query Variants, die beobachtete `QueryVariantID` sowie die untere und obere Kardinalitätsgrenze auf.

## 7. Ablauf

Vier Prozeduren tragen denselben Querytext und unterscheiden sich nur im Kommentarmarker beziehungsweise im Abwahlhinweis:

| Objekt | Kennzeichnung |
|---|---|
| `lab.usp_Opt009SearchSelectiveFirst` | Baseline; selektiver Wert kompiliert zuerst |
| `lab.usp_Opt009SearchCommonFirst` | Demonstration; dominanter Wert kompiliert zuerst |
| `lab.usp_Opt009SearchPsp` | Gegenmaßnahme; eingeschaltete Parametersensitivität |
| `lab.usp_Opt009SearchOptOut` | Vergleich; `USE HINT ('DISABLE_PARAMETER_SENSITIVE_PLAN')` |

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte und Zielkennung prüfen |
| Setup | `10_Setup.sql` | Markergebundene Datenbank, schiefes Verteilungsmodell, vier Abfrageobjekte und Evidenztabelle anlegen; Parametersensitivität abschalten |
| Baseline | `20_Baseline.sql` | selektiver Wert zuerst; eine Planform, dominanter Wert benachteiligt |
| Demonstration | `30_Demonstration.sql` | dominanter Wert zuerst; eine Planform, selektiver Wert benachteiligt |
| Observation | `40_Observation.sql` | beidseitige Mehrkosten, Ergebnisgleichheit und Abwesenheit jedes Dispatcherplans |
| Mitigation | `50_Mitigation.sql` | Parametersensitivität einschalten; Dispatcherplan, Query Variants und Kardinalitätsgrenzen nachweisen |
| Comparison | `60_Comparison.sql` | Ergebnisvertrag über alle Phasen und dokumentierte Abwahl auf Abfrageebene |
| Cleanup | `90_Cleanup.sql` | Markergeprüfter, idempotenter Abbau |

## 8. Erwartete Beobachtung

- Baseline: genau eine Planform, 5 und 99 000 Trefferzeilen, deutlich höhere logische Lesevorgänge für den dominanten Wert, kein Dispatcherplan.
- Demonstration: unverändert eine Planform bei identischen Ergebnissen, nun jedoch höhere Lesevorgänge für den selektiven Wert als in der Baseline.
- Observation: für beide Parameterwerte ein Faktor größer als eins zwischen günstiger und ungünstiger Reihenfolge bei identischen Prüfsummen.
- Mitigation: mindestens ein Dispatcherplan, mindestens zwei Query Variants, ausgewiesene untere und obere Kardinalitätsgrenze und für beide Werte niedrigere Lesevorgänge als im jeweils ungünstigen Fall.
- Comparison: je Parameterwert genau eine Trefferzahl und eine Prüfsumme über vier Phasen sowie kein Dispatcherplan für die ausdrücklich abgewählte Abfrage.

## 9. Interpretation

Parameter Sniffing ist kein Fehler, sondern die Folge einer einzigen wiederverwendbaren Planform. Solange nur eine Planform existiert, ist jede Reihenfolgeentscheidung eine Wette auf eine Parameterbelegung. Parameter Sensitive Plan Optimization löst diese Wette auf, indem der Dispatcherplan gleiche Anweisungen anhand der Kardinalitätsbänder auf eigene Planformen verteilt. Das Verfahren ist eng begrenzt: Es greift nur bei Gleichheitsprädikaten mit ausreichender Schiefe, wählt höchstens drei Prädikate aus und bildet je Prädikat drei Bänder. Ob es greift, entscheidet der Optimierer; deshalb wird die Variantenbildung nachgewiesen und nicht vorausgesetzt. Wo es nicht greift, bleiben die in `QRY-004` verglichenen Strategien die tragfähige Antwort.

## 10. Cleanup und Wiederherstellung

`90_Cleanup.sql` liest die vier Eigentumsmarker `SQLPERF.Project`, `SQLPERF.ContractVersion`, `SQLPERF.DemoId` und `SQLPERF.RunToken` aus der Zieldatenbank und entfernt sie nur bei vollständiger Übereinstimmung. Fehlt die Datenbank, endet der Cleanup idempotent mit `PASS`. Die Datenbankeinstellung wird nicht zurückgesetzt, weil die gesamte Datenbank entfernt wird.

## 11. Tests

`Tests/Static/validate_adv008_opt009.py` prüft Bündelstruktur, Manifestvertrag, Phasenzuordnung, Markertrennung, das Verbot instanzweiter Planentwertung, die ausschließliche Verwendung vertraglicher Statuscodes, Zusammenfassungszeilen und Cleanup-Idempotenz. Die Runtime-Abnahme erfolgt über `Tests/Runtime/run_adv008_opt009.py` auf SQL Server 2019, 2022 und 2025.

## 12. Bekannte Grenzen

Dispatcher- und Variantenevidenz stammt aus `sys.dm_exec_cached_plans`, `sys.dm_exec_query_plan` und `sys.dm_exec_query_stats`. Das ist eine Instanzsicht auf den aktuellen Cacheinhalt und keine sessiongenaue Messung; unter Speicherdruck endet die betroffene Phase mit `SKIP_EVIDENCE_MISSING`. Die Zahl der Query Variants wird über den Namen der Demotabelle bestimmt und ist deshalb datenbankweit, nicht phasenbezogen; die Abwahl auf Abfrageebene wird daher über die markerbezogene Zahl der Dispatcherpläne belegt. Stuft der Optimierer die Abfrage trotz passender Version nicht als parametersensitiv ein, endet die Gegenmaßnahme mit `SKIP_EVIDENCE_MISSING` und ausgewiesener Evidenz. Lässt sich der Nutzen der Varianten nicht von der Messstreuung trennen, endet die Phase mit `WARN_EMPIRICAL_VARIANCE`. Die Sichten `sys.query_store_plan` und `sys.query_store_query_variant` werden bewusst nicht verwendet, solange die Query-Store-Pilotabnahme offen ist.

## 13. Quellen

| Quellen-ID | Aussagebezug |
|---|---|
| `SRC-007` | Funktionsmatrix der intelligenten Abfrageverarbeitung, Versions- und Compatibility-Level-Grenzen |
| `SRC-008` | Detailgrenzen der parametersensitiven Planoptimierung, Dispatcherplan und Query Variants |
| `SRC-048` | empirische Grenzfälle der Variantenbildung |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-019` |
| Demo-ID | `OPT-009` |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Folienspezifikation | `Documentation/Curriculum/ADV_010_SLIDE_SPECIFICATION_M03_LO08_PSP.md` |
| Folien im aktiven Deck | Anzeigepositionen 94 bis 97 (`SLD-M03-121` bis `SLD-M03-124`) |
| Abnahmestand | `Documentation/Project_Planning/ADV_008_OPT_009_REVIEW.md` |
