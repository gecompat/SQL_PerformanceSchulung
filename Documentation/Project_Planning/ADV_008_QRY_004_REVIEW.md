# ADV-008 – Review `QRY-004`

| Merkmal | Wert |
|---|---|
| Paket | `ADV-008` |
| Schnitt | `QRY-004_CLASSIC_AND_DYNAMIC` |
| Status | `IMPLEMENTED_FOR_REVIEW` |
| Lernziel | `LO-M03-08` |
| Claims | `ADV-CLM-016`, `ADV-CLM-017`, `ADV-CLM-018` |
| Testprofil | `TP-RUN`, `TP-PERF` |
| Runtime-Abnahme | offen |

## 1. Umfang

Der Schnitt liefert die Demo `QRY-004` als vollständiges Bündel nach `FWK-001`, den parallel ausgearbeiteten Folienteil zu `LO-M03-08` als Spezifikation sowie die zugehörige statische und laufzeitbezogene Prüfstrecke.

| Artefakt | Pfad |
|---|---|
| Demobündel | `Demos/05_Query_Patterns/QRY-004_Classic_And_Dynamic/` |
| Folienspezifikation | `Documentation/Curriculum/ADV_009_SLIDE_SPECIFICATION_M03_LO08.md` |
| Statischer Vertrag | `Tests/Static/validate_adv008_qry004.py` |
| Runtime-Runner | `Tests/Runtime/run_adv008_qry004.py` |
| Runtime-Workflow | `.github/workflows/adv008-qry004.yml` |

## 2. Fachliche Abgrenzung

Verglichen werden genau drei Strategien für optionale Suchbedingungen: der statische Catch-all-Querytext, derselbe Text mit `OPTION (RECOMPILE)` und sicher parameterisiertes dynamisches SQL. Parameter Sensitive Plan Optimization und Optional Parameter Plan Optimization bleiben `OPT-009` und `OPT-010` vorbehalten; die Trennung ist als `DEC-056` festgehalten.

Der Vergleich stellt keine Rangfolge auf. Er belegt drei voneinander unabhängige Eigenschaften: die Bindung des Catch-all-Texts an eine einzige Planform, den Tausch von Wiederverwendung gegen Compilearbeit bei `OPTION (RECOMPILE)` und die Begrenzung der Statementformen bei parameterisiertem dynamischem SQL.

## 3. Sicherheitsentscheidung

Dynamisches SQL wird ausschließlich aus der Positivliste `lab.Qry004AllowedFilter` zusammengesetzt; Werte werden über `sys.sp_executesql` gebunden. Ein unsicheres Gegenbeispiel existiert bewusst nicht, weil es kopierbarer Schadcode wäre. Stattdessen wird die Sicherheitsaussage messbar geprüft: Der zwischengespeicherte Statementtext darf keinen Filterwert enthalten, und eine Filterdefinition außerhalb der Positivliste wird mit `THROW 51000` abgewiesen. Der statische Vertrag verbietet zusätzlich `EXEC(...)` und die Konkatenation von Filterwerten. Die Entscheidung ist als `DEC-055` festgehalten.

## 4. Evidenz- und Abbruchvertrag

| Phase | Nachweis | Kontrollierter Ausgang |
|---|---|---|
| BASELINE | genau eine Planform über drei Selektivitäten; 20, 19 980 und 4 000 Zeilen | `SKIP_EVIDENCE_MISSING`, `THROW 51006` |
| DEMONSTRATION | Ergebnis- und Prüfsummenequivalenz zur Baseline; geringere Lesevorgänge für den selektiven Wert | `WARN_EMPIRICAL_VARIANCE` |
| OBSERVATION | je 25 gezählte Ausführungen bei identischer Arbeitsmenge; höhere CPU je Ausführung der neu optimierten Variante | `WARN_EMPIRICAL_VARIANCE` |
| MITIGATION | zwei Statementformen für drei Ausführungen; literalfreier Statementtext; abgewiesene Positivlistenverletzung | `THROW 51006` |
| COMPARISON | durchgängige Ergebnisgleichheit; unveränderte Catch-all-Planform | `THROW 51006` |

Empirische Richtungsaussagen führen zu `WARN`, nie zu einem behaupteten Ergebnis. Vertragsverletzungen führen zu `FAIL_RESULT_CONTRACT`.

## 5. Prüfnachweis

Alle statischen Prüfer des Repositorys laufen grün. Maßgebliche Zeilen:

```
adv008-qry004: PASS (7 phases, 3 strategies, 5 slide specifications, 2 claims)
demo-execution-paths: PASS (8 demos, 0 above stage 2)
sql-server-lab-scenario-contract: PASS (8 automated demos, interactive scenario goal anchored, full_runs=96)
inf-001-execution-path: PASS (4 demo runners, 9 how-to topics, 5 runtime workflows)
privacy-metadata: PASS (files=288; text=279; office=1; archives=0; approved_immutable=1)
```

Der neue Prüfer wurde negativ getestet. Fünf gezielte Mutationen wurden jeweils erkannt: entfernter `OPTION (RECOMPILE)`-Hinweis, konkatenierter Filterwert, direkte Stringausführung über `EXEC(...)`, ungleiche Wiederholungszahl in der Beobachtungsphase und fehlender Folienmarker.

## 6. Offene Punkte

1. Die Runtime-Abnahme über SQL Server 2019, 2022 und 2025 steht aus; sie läuft ausschließlich auf GitHub-gehosteten Runnern. Der Status bleibt bis dahin `IMPLEMENTED`, nicht `VALIDATED`.
2. Die Übernahme der fünf Folien in das Deck ist nach `DEC-057` erfolgt und in `Documentation/Project_Planning/ADV_009_DECK_INTEGRATION_REVIEW.md` dokumentiert. `ADV-CLM-017` und `ADV-CLM-018` stehen auf `KEEP` und tragen die Anzeigepositionen 90 bis 93.
3. `OPT-009` und `OPT-010` schließen den Bogen fachlich ab und sind noch nicht implementiert.
