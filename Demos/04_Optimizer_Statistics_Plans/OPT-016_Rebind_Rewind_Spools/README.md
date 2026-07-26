# OPT-016 – Rebind, Rewind, Outer References und Spools

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Sicherheitsstufe | `GREEN` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Compatibility Level | 150, 160 und 170 |
| Edition / Plattform | Database Engine; Windows oder Linux |
| Sessions | 1 |
| Laufzeitklasse | M |
| Testprofil | `TP-ADV-PLAN` |
| Runtime-Abnahme | SQL Server 2019, 2022 und 2025; je Version zwei vollständige Läufe |

## 1. Lernziel

Nach Abschluss kann die lernende Person Outer References, wiederholte innere Ausführung, Actual Rebinds, Actual Rewinds und eine Spool-Planform gemeinsam interpretieren. Eine Spool wird weder automatisch als Fehler noch automatisch als Verbesserung bewertet.

## 2. Fachliche Kernaussage

**Evidenzklasse:** `EMPIRISCH` und `INFERENCE`

Eine korrelierte APPLY-/Nested-Loops-Form kann innere Ergebnisse wiederholt aufbauen oder wiederverwenden. Ob SQL Server dafür eine Performance Spool erzeugt, ist eine Optimizerentscheidung. Die Demo verwendet deshalb einen planformabhängigen Vertrag: Eine erzeugte Spool wird anhand von Outer References, Executions, Rebinds, Rewinds und tatsächlicher Arbeit analysiert. Baseline und Vergleich verwenden `NO_PERFORMANCE_SPOOL` ausschließlich als kontrollierte Gegenprobe; der Problemzustand bleibt hintfrei.

## 3. Nichtziel

Die Demo garantiert keine bestimmte Spoolart, definiert keine universelle Rebind-/Rewind-Schwelle und empfiehlt den Hint `NO_PERFORMANCE_SPOOL` nicht als Tuningregel. Die fachliche Gegenmaßnahme besteht im passenden Zugriffspfad; der Hint dient nur dazu, denselben Queryvertrag ohne Performance Spool vergleichbar zu machen.

## 4. Voraussetzungen

Erforderlich sind SQL Server 2019 bis 2025, Compatibility Level 150 bis 170, `CREATE DATABASE`, versionsgerechte Server-State-Sichtbarkeit und Plananzeigerechte. Das Mindestprofil umfasst zwei logische CPU-Kerne, 4 GB für die SQL-Server-Instanz und etwa 500 MB freien Datenträgerspeicher.

## 5. Sicherheits- und Abbruchrahmen

Die Demo ist grün. Alle Objekte liegen in einer markergebundenen Testdatenbank. `LAST_QUERY_PLAN_STATS` wird nur in dieser Datenbank aktiviert. Globale Cacheleerungen und Instanzänderungen sind verboten; Recompilation erfolgt objektbezogen. Die Datenmenge ist begrenzt, jede Abfrage verwendet `MAXDOP 1`, und Cleanup folgt dem gemeinsamen Marker- und Timeoutvertrag.

## 6. Synthetisches Datenmodell

`lab.WorkItemDetail` enthält 20.000 Detailzeilen in 20 Gruppen. `lab.ProbeRequest` enthält ein Profil `H` mit 5.000 Anforderungen, aber nur zehn unterschiedlichen Gruppenschlüsseln, sowie ein Profil `L` mit 20 jeweils unterschiedlichen Schlüsseln. Die Baseline verwendet den Index `IX_WorkItemDetail_Group_Sequence` und eine kontrollierte `NO_PERFORMANCE_SPOOL`-Gegenprobe. Der Problemzustand entfernt nur diesen Index und verwendet die hintfreie Abfrage; die äußere Eingabe bleibt nach Profil und Gruppe geordnet. Normalisierte Evidenz wird in `lab.Opt016Evidence` gespeichert, Plan XML nicht.

## 7. Ablauf

| Phase | Datei | Zweck |
|---|---|---|
| Preflight | `00_Preflight.sql` | Version, Rechte, Zielkennung und Actual-Plan-Voraussetzungen prüfen |
| Setup | `10_Setup.sql` | markergebundene Datenbank, Datenprofile, Zugriffspfad und Hilfsprozeduren anlegen |
| Baseline | `20_Baseline.sql` | Profil `H` mit passendem Index und kontrollierter No-Spool-Gegenprobe erfassen |
| Demonstration | `30_Demonstration.sql` | Index entfernen und die hintfreie optimizergewählte Wiederverwendung ausführen |
| Observation | `40_Observation.sql` | dieselbe kompilierte Planform mit Profil `L` ausführen und Rebind-/Rewind-Richtung vergleichen |
| Mitigation | `50_Mitigation.sql` | passenden Index und kontrollierte No-Spool-Gegenprobe wiederherstellen |
| Comparison | `60_Comparison.sql` | Profil `H` erneut mit identischem Ergebnis und direktem Zugriffspfad messen |
| Cleanup | `90_Cleanup.sql` | Datenbank nach vollständiger Markerprüfung entfernen |

## 8. Erwartete Beobachtung

Die kontrollierte Baseline besitzt Outer References und einen seekfähigen inneren Zugriff ohne Performance Spool. Nach Entfernen des Indexes erzeugt die Referenzmatrix hintfrei eine Spool-Planform. Das stark wiederholte Profil besitzt mehr Rewind-Ereignisse als das Profil mit eindeutigen Schlüsseln. Nach Wiederherstellung des Indexes bleiben Zeilenzahl und Checksumme des Profils `H` identisch; die kontrollierte Vergleichsabfrage verwendet wieder den direkten Zugriffspfad ohne Spool.

## 9. Interpretation

Rebind bedeutet, dass die innere Seite für einen neuen korrelierten Wert neu initialisiert wird. Rewind beschreibt die Wiederverwendung eines bereits aufgebauten Zustands. Diese Zähler sind nur zusammen mit Outer References, Eingabereihenfolge, Number of Executions, tatsächlichen Zeilen und Zugriffspfad interpretierbar. Der Nutzen einer Spool hängt vom Wiederholungsprofil und den Aufbaukosten ab. `NO_PERFORMANCE_SPOOL` ist in dieser Demo kein empfohlener Fix, sondern eine kontrollierte A/B-Grenze.

## 10. Cleanup und Wiederherstellung

Alle Daten, Prozeduren und Evidenzzeilen liegen in der markergebundenen Testdatenbank. `90_Cleanup.sql` prüft Projekt, Vertragsversion, Demo-ID und Run-Token und entfernt ausschließlich diese Datenbank. Der Cleanup ist idempotent und wird auch nach einem planformabhängigen Skip ausgeführt.

## 11. Tests

Die statische Prüfung kontrolliert Phasenvertrag, Quellen, planformabhängigen Skip, Outer-Reference- und Rebind-/Rewind-Evidenz, verbotene globale Aktionen und die Nichtpersistenz von Plan XML. Die Runtime-Matrix führte die Demo auf SQL Server 2019, 2022 und 2025 jeweils zweimal aus und bestätigte die hintfreie Spool-Planform, die Reuse-Richtung, Ergebnisequivalenz und vollständiges Cleanup.

## 12. Bekannte Grenzen

Performance Spools und konkrete Rebind-/Rewind-Zähler sind plan- und buildabhängig. Der Runtimevertrag darf `SKIP_PLAN_SHAPE_NOT_PRODUCED` ausgeben, wenn trotz geeignetem Datenprofil keine Spool entsteht. Eine solche Abweichung muss dokumentiert werden und darf nicht durch undokumentierte Trace Flags oder erzwungene interne Planformen kaschiert werden. Die validierte Referenzmatrix 2019/2022/2025 erzeugte die erwartete Spool-Planform.

## 13. Quellen

| Quellen-ID | Aussagebezug | Gültigkeitsbereich | Abrufdatum |
|---|---|---|---|
| `SRC-001` | Nested Loops, Tasks und Planverarbeitung | SQL Server 2019–2025 | 2026-07-26 |
| `SRC-031` | Actual Execution Plan als Runtime-Evidenz | SQL Server 2019–2025 | 2026-07-26 |
| `SRC-039` | gemeinsame Planattribute, Rebinds und Rewinds | versionsabhängig empirisch zu prüfen | 2026-07-26 |
| `SRC-042` | Nested Loops, Apply und Performance Spools | Optimizer-Interna; eigene Reproduktion erforderlich | 2026-07-26 |
| Microsoft Learn: [`sys.dm_exec_query_plan_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17) | letzter bekannter Actual Plan; datenbankbezogenes opt-in | SQL Server 2019–2025 | 2026-07-26 |

## 14. Traceability

| Element | Zuordnung |
|---|---|
| Lernziel | `LO-M02-09` |
| Claims | `ADV-CLM-005`, `ADV-CLM-006`, `ADV-CLM-010` |
| Demo-ID | `OPT-016` |
| Testprofil | `TP-ADV-PLAN` |
