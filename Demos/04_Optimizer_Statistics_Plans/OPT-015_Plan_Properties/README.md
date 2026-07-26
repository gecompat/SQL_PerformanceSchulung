# OPT-015 – Planweite und operatorbezogene Eigenschaften

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED` |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 |
| Laufzeitklasse | M |
| Testprofil | `TP-ADV-PLAN` |

## 1. Lernziel

Nach Abschluss kann die lernende Person einen Actual Execution Plan systematisch vom Statement zur ersten fachlich relevanten Operatorabweichung lesen. Planweite Eigenschaften, Schätzwerte, Laufzeitwerte, Statistics Usage, Prädikate und Warnungen werden getrennt ausgewertet.

## 2. Fachliche Kernaussage

**Evidenzklasse:** `DOKUMENTIERT` und `EMPIRISCH`

Geschätzte Kosten und Kardinalitäten entstehen während der Optimierung. Actual-Plan-Informationen ergänzen diese Werte um Daten der betrachteten Ausführung. Die Demo vergleicht deshalb nicht den optisch teuersten Operator, sondern Estimated Rows, Actual Rows, Actual Rows Read, Number of Executions, Statistics Usage, Query Hash, Logical Reads, CPU und Duration derselben markierten Abfrage.

## 3. Nichtziel

Die Demo definiert keine universelle Fehlerschwelle, bewertet keinen Operator allein aufgrund seines Kostenanteils und behauptet nicht, dass eine Statistikaktualisierung jede Planabweichung löst. Der erzeugte Out-of-range-Fall ist ein synthetisches Lehrmodell.

## 4. Voraussetzungen

Erforderlich sind SQL Server 2019 bis 2025, Compatibility Level 150 bis 170, `CREATE DATABASE`, versionsgerechte Server-State-Sichtbarkeit und die Datenbankberechtigung zur Plananzeige. Das Mindestprofil umfasst zwei logische CPU-Kerne, 4 GB für die SQL-Server-Instanz und etwa 500 MB freien Datenträgerspeicher.

## 5. Sicherheits- und Abbruchrahmen

Die Demo ist grün. Sie erzeugt ausschließlich eine markergebundene Testdatenbank und verändert darin die datenbankbezogene Einstellung `LAST_QUERY_PLAN_STATS`. Globale Caches, Instanzoptionen und fremde Objekte bleiben unverändert. Recompilation erfolgt ausschließlich objektbezogen über `sys.sp_recompile`. Timeout und Cleanup folgen dem gemeinsamen Frameworkvertrag.

## 6. Synthetisches Datenmodell

`lab.EntityGroup` enthält 20 neutrale Gruppen. `lab.WorkItem` enthält zunächst 200.000 deterministische Zeilen mit gleichmäßiger Gruppenverteilung. Der Index `IX_WorkItem_EntityGroupId` wird per Fullscan erfasst und zunächst mit `NORECOMPUTE` stabilisiert. Der Problemzustand ergänzt 60.000 Zeilen für die bisher nicht vorhandene Gruppe 999. Baseline und Vergleich besitzen normalisierte Evidenz in `lab.Opt015Evidence`; Plan XML wird nicht persistiert.

## 7. Ablauf

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte, Zielkennung und Plan-Evidenzvoraussetzungen prüfen |
| Setup | `10_Setup.sql` | markergebundene Datenbank, deterministische Daten, Index und Hilfsprozeduren anlegen |
| Baseline | `20_Baseline.sql` | bekannte Gruppe mit plausibler Kardinalität erfassen |
| Demonstration | `30_Demonstration.sql` | neue Gruppe bei unveränderter Statistik abfragen |
| Observation | `40_Observation.sql` | Planwurzel, Zugriffsoperator, Schätzfehler, Statistics Usage und Laufzeitwerte vergleichen |
| Mitigation | `50_Mitigation.sql` | ausschließlich die relevante Indexstatistik aktualisieren |
| Comparison | `60_Comparison.sql` | dieselbe Gruppe mit aktualisierter Statistik und identischer Ergebnismenge erneut messen |
| Cleanup | `90_Cleanup.sql` | Datenbank nach vollständiger Markerprüfung entfernen |

## 8. Erwartete Beobachtung

Die Baseline besitzt eine Operator-Kardinalität in derselben Größenordnung wie 10.000 tatsächliche Zeilen. Der Problemzustand liefert 60.000 Zeilen, während die veraltete Statistik die neue Gruppe noch nicht abbildet. Nach dem Fullscan ist der absolute Schätzfehler kleiner, Problem- und Vergleichschecksumme sind identisch und Statistics Usage verweist weiterhin auf die untersuchte Indexstatistik.

## 9. Interpretation

Eine Estimate-/Actual-Abweichung ist ein Diagnosehinweis, kein vollständiger Ursachenbeweis. Aussagekräftig wird sie erst zusammen mit Statistics Usage, Prädikat, Ausführungsanzahl, tatsächlich gelesenen Zeilen, Ergebnisvertrag und Laufzeitmessung. Die Demonstration verändert deshalb nur die lokale Datenverteilung und anschließend genau die dazugehörige Statistik.

## 10. Cleanup und Wiederherstellung

Alle Daten, Prozeduren und Evidenzzeilen liegen in der markergebundenen Testdatenbank. `90_Cleanup.sql` prüft Projekt, Vertragsversion, Demo-ID und Run-Token, setzt ausschließlich diese Datenbank auf `SINGLE_USER` und entfernt sie. Der Cleanup ist idempotent.

## 11. Tests

Die statische Prüfung kontrolliert Phasenvertrag, Marker, Quellen, Plan-Evidenz, verbotene globale Aktionen und die Nichtpersistenz von Plan XML. Die Runtime-Matrix führt die Demo auf SQL Server 2019, 2022 und 2025 wiederholt aus und prüft Kardinalitätsrichtung, Statistics Usage, Query Hash, Ergebnisequivalenz und vollständiges Cleanup.

## 12. Bekannte Grenzen

Die konkrete Out-of-range-Schätzung, der Zugriffsoperator sowie CPU- und Laufzeitwerte hängen von Engine-Build und Umgebung ab. Golden Values sind nur Zeilenzahlen, Ergebnisequivalenz, vorhandene normalisierte Planattribute und die Richtung der Schätzfehlerverbesserung. Der vollständige Planbaum wird nicht als unveränderliche Referenz behandelt.

## 13. Quellen

| Quellen-ID | Aussagebezug | Gültigkeitsbereich | Abrufdatum |
|---|---|---|---|
| `SRC-001` | Query Processing, Optimierung und Plan Cache | SQL Server 2019–2025 | 2026-07-26 |
| `SRC-005` | Statistik, Histogramm und Aktualität | SQL Server 2019–2025 | 2026-07-26 |
| `SRC-031` | Actual Execution Plan als Runtime-Evidenz | SQL Server 2019–2025 | 2026-07-26 |
| `SRC-037` bis `SRC-040` | Planleselogik, gemeinsame und planweite Eigenschaften | versionsabhängig empirisch zu prüfen | 2026-07-26 |
| Microsoft Learn: [`sys.dm_exec_query_plan_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17) | letzter bekannter Actual Plan; datenbankbezogenes opt-in | SQL Server 2019–2025 | 2026-07-26 |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M02-08` |
| Claims | `ADV-CLM-001`, `ADV-CLM-002`, `ADV-CLM-003`, `ADV-CLM-004` |
| Demo-ID | `OPT-015` |
| Testprofil | `TP-ADV-PLAN` |
