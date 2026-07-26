# ADV-004 – Design LAB-VP1: Planmechanik und Operatorinteraktion

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-004` |
| Status | `DESIGNED` |
| Stand | 2026-07-26 |
| LAB-Serie | `LAB-VP1` |
| Curriculum | `LO-M02-08`, `LO-M02-09`, `LO-M02-10` |
| Claims | `ADV-CLM-001` bis `ADV-CLM-012` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Standardpfad | isolierte synthetische Testdatenbank |

## 1. Ziel und Abgrenzung

LAB-VP1 vermittelt eine reproduzierbare Lesemethode für Execution Plans. Der Plan wird entlang Datenfluss, Kardinalitäten, Ausführungsanzahl, Prädikaten, Warnungen, Wiederverwendung und Threadverteilung untersucht. Grafische Kostenanteile werden als Optimizer-Kostenwerte und nicht als gemessene Laufzeit interpretiert.

Der Block ist kein vollständiges Operatorlexikon. Operatoren werden nur dort vertieft, wo ihre Interaktion eine Diagnoseentscheidung verändert. Nicht Bestandteil sind undokumentierte Optimizer-Regeln als Produktgarantie, universelle Kostenschwellen, erzwungene Planformen als Best Practice oder die pauschale Bewertung von Spools, Row Goals und Parallelität als Fehler.

## 2. Didaktische Reihenfolge

`OPT-001` → `OPT-015` → `OPT-012` → `OPT-016` → `OPT-011` → `QRY-006` → `OPT-013` → `OPT-017`

Die vorhandenen Demos liefern Kardinalitäts-, Join-, Row-Goal-, Semi-/Anti-Join- und Spill-Kontext. `OPT-015` bis `OPT-017` ergänzen die bisher fehlende planweite und operatorübergreifende Evidenz. Die Serie wird als vollständiger Block auf 80 bis 110 Minuten geplant. Einzelne Demos bleiben separat ausführbar.

## 3. Gemeinsames synthetisches Datenmodell

Die drei neuen Demos verwenden eine markergebundene Datenbank und ein gemeinsames, skalierbares Modell:

- `dbo.EntityGroup`: kleine Dimension mit neutralen Gruppenkennungen,
- `dbo.WorkItem`: Faktentabelle mit deterministischer Gruppenverteilung, Zeitstempel, Status und Payload-Breite,
- `dbo.ProbeRequest`: wiederholte Suchschlüssel zur kontrollierten inneren Wiederverwendung,
- `dbo.WorkItemDetail`: Detailzeilen mit einstellbarer Kardinalität und sortierbarer Sequenz.

Der Datengenerator verwendet feste Seeds und mindestens drei Profile: `SMALL`, `STANDARD` und `PARALLEL`. Verteilung, Zeilenbreite und Wiederholungsgrad sind getrennt einstellbar. Systemkataloge werden nicht als Zeilengenerator verwendet. Alle Ergebnismengen besitzen Count- und Checksum-Evidenz.

## 4. OPT-015 – Planweite und operatorbezogene Eigenschaften

### 4.1 Lernziel

Planwurzel, Statementscope, Parameter, SET-Kontext, Statistics Usage, Estimated/Actual Rows, Actual Rows Read, Number of Executions, Prädikate und Warnings werden in einer konsistenten Reihenfolge untersucht.

### 4.2 Design

Die Baseline verwendet eine selektive, statistisch plausible Abfrage. Der Problemzustand verwendet dasselbe Datenmodell mit bewusst veränderter Verteilung beziehungsweise veralteter lokaler Statistik, ohne globale Cache- oder Servereingriffe. Die Gegenmaßnahme korrigiert ausschließlich die für die Hypothese relevante Statistik oder den Prädikatszuschnitt. Der Vergleich hält Ergebnismenge und Messpfad konstant.

### 4.3 Verbindliche Evidenz

- Actual Plan und Plan XML derselben Ausführung,
- Statementmarker und Query Hash,
- Estimated Rows, Actual Rows, Actual Rows Read und Number of Executions,
- Statistics Usage und kompilierte Parameterwerte, soweit im Plan vorhanden,
- Logical Reads, CPU, Duration und Result Checksum,
- explizite Trennung von Estimated Cost und gemessenen Laufzeitwerten.

### 4.4 Abnahme

Die Demo gilt fachlich als bestanden, wenn ein unbekannter Plan anhand der ersten relevanten Abweichung entlang des Datenflusses eingeordnet werden kann. Ein Test darf nicht verlangen, dass ein bestimmter Operator den höchsten grafischen Kostenanteil besitzt.

**Sicherheitsstufe:** Grün. **Sessions:** 1. **Mindestprofil:** 2 logische CPU-Kerne, 4 GB SQL-Server-Speicher. **Quellen:** `SRC-001`, `SRC-031`, `SRC-037` bis `SRC-040`.

## 5. OPT-016 – Rebind, Rewind, Outer References und Spools

### 5.1 Lernziel

Die Demo zeigt wiederholte innere Ausführung und Wiederverwendung in einem Nested-Loops-/APPLY-Kontext. Rebind, Rewind, Outer References und Spools werden als Eigenschaften einer Planform und nicht als pauschale Fehlerindikatoren interpretiert.

### 5.2 Design

`ProbeRequest` enthält viele Zeilen, aber deutlich weniger unterschiedliche Suchschlüssel. Die innere Abfrage greift korreliert auf `WorkItemDetail` zu. Zwei Datenprofile variieren den Wiederholungsgrad der äußeren Schlüssel. Eine kontrollierte Gegenprobe darf `NO_PERFORMANCE_SPOOL` verwenden, sofern die Zielversion den Hint akzeptiert. Der Hint ist ausschließlich Diagnoseinstrument; die primäre Variante bleibt hintfrei.

Da der Optimizer keine konkrete Spoolform garantiert, besitzt die Demo einen planformabhängigen Ergebnisvertrag:

- Wird eine geeignete Spool-/Reuse-Planform erzeugt, werden Aufbau, Rebinds, Rewinds und tatsächliche Arbeit ausgewertet.
- Wird trotz geeignetem Datenprofil keine solche Planform erzeugt, endet der betreffende Teil mit `SKIP_PLAN_SHAPE_NOT_PRODUCED`; dies ist kein Fehler der SQL-Server-Version.

### 5.3 Verbindliche Evidenz

- Outer References und Number of Executions,
- Actual Rebinds und Actual Rewinds, soweit ausgegeben,
- Worktable-/Spool-Warnings beziehungsweise Planattribute,
- Reads, CPU, Duration und identische Ergebnischecksumme,
- Vergleich der tatsächlichen inneren Arbeit bei hohem und niedrigem Schlüsselwiederholungsgrad.

**Sicherheitsstufe:** Grün. **Sessions:** 1. **Mindestprofil:** 2 Kerne, 4 GB. **Quellen:** `SRC-039`, `SRC-042`; Produktgrenzen zusätzlich über `SRC-001` und Runtime-Evidenz.

## 6. OPT-017 – Parallele Planbereiche, Exchanges und Operatorzeiten

### 6.1 Lernziel

Die Demo untersucht parallele Branches, Exchanges, DOP, Threadverteilung und Parallel Skew. Operatorbezogene CPU- und Elapsed-Werte werden nicht ungeprüft summiert oder mit der gesamten Querydauer gleichgesetzt.

### 6.2 Design

Das `PARALLEL`-Profil enthält eine ausreichend große Faktentabelle und zwei deterministische Verteilungen mit identischer Zeilenzahl: eine annähernd gleichmäßige und eine stark konzentrierte Gruppenverteilung. Eine Hash-Aggregation oder ein Hash-Join erzeugt bei geeigneter Umgebung einen parallelen Plan. `MAXDOP` wird querylokal auf den kleineren Wert aus 4 und der verfügbaren DOP-Grenze beschränkt. Instanzweite Konfigurationen werden nicht verändert.

Die Gegenmaßnahme ist keine pauschale DOP-Reduktion. Abhängig von der erzeugten Evidenz wird entweder die Datenaufteilung beziehungsweise Voraggregation geändert oder eine serielle Gegenprobe ausgeführt. Ergebnisgleichheit und Gesamtarbeit bleiben die Bewertungsgrundlage.

### 6.3 Preflight und Skip

- weniger als 4 sichtbare logische Kerne: `SKIP_CPU_PROFILE_INSUFFICIENT`,
- effektive DOP-Grenze kleiner 2: `SKIP_PARALLELISM_UNAVAILABLE`,
- kein paralleler Plan trotz geeignetem Profil: `SKIP_PLAN_SHAPE_NOT_PRODUCED`,
- unzureichender TempDB- oder Datenbankplatz: `SKIP_STORAGE_PROFILE_INSUFFICIENT`.

### 6.4 Verbindliche Evidenz

- Actual DOP, Exchanges und parallele Planbereiche,
- Zeilen und Ausführungsanzahl je Thread, soweit im Plan XML verfügbar,
- Verhältnis größte zu kleinste relevante Threadarbeit statt fixer Schwelle,
- CPU, Duration, Reads und Ergebnisequivalenz,
- serieller Vergleich nur als kontrollierte Gegenprobe.

**Sicherheitsstufe:** Gelb. **Sessions:** 1. **Mindestprofil:** 4 Kerne und 8 GB empfohlen. **Quellen:** `SRC-001`, `SRC-031`, `SRC-043`, `SRC-044`.

## 7. Phasenvertrag je neuer Demo

Jede Implementierung enthält in dieser Reihenfolge:

1. Preflight mit Version, Compatibility Level, Berechtigungen und Ressourcenprofil,
2. markergeprüftes Setup,
3. Baseline,
4. kontrollierter Problem- oder Kontrastzustand,
5. technische Evidenz,
6. genau eine Gegenmaßnahme beziehungsweise Gegenprobe,
7. Vergleich mit Ergebnisgleichheit,
8. markergeprüftes Cleanup.

Ein Plan-Screenshot ist keine Golden-Evidenz. Tests werten Plan XML, normalisierte Eigenschaften, relationale Erwartungen und begründete Skips aus.

## 8. Test- und Versionsvertrag

`OPT-015` und `OPT-016` werden als grüne Demos auf SQL Server 2019, 2022 und 2025 validiert. `OPT-017` wird in einem gelben, ausreichend parallelen Profil getestet. Operatornamen dürfen geprüft werden, wenn sie für die Kernaussage notwendig sind; vollständige Planbäume und exakte Kostenwerte sind keine stabilen Golden Values.

Zulässige Erwartungen sind beispielsweise:

- Ergebnischecksumme bleibt gleich,
- Actual Rows und Number of Executions sind vorhanden,
- Wiederholungsprofil erhöht die innere Arbeit in der erwarteten Richtung,
- Skew-Profil erzeugt ungleichere Threadarbeit als das balancierte Profil,
- Cleanup entfernt die markierte Testdatenbank nach jedem Lauf.

## 9. Implementierungsschnitte

1. `OPT-015` einschließlich statischem Vertrag und 2019/2022/2025-Matrix,
2. `OPT-016` einschließlich planformabhängigem Skip-Vertrag,
3. `OPT-017` einschließlich gelbem Ressourcenprofil,
4. LAB-VP1-Orchestrierung und didaktische Übergänge.

Jeder Schnitt bleibt ein eigener Pull Request oder ein klar isolierter Commit mit vollständiger Demo-Dokumentation und Tests.

## 10. Designfreigabe

`ADV-004` erreicht `VALIDATED`, wenn dieses Design, der maschinenlesbare Vertrag und die statische Prüfung konsistent sind. Dies ist keine Runtimefreigabe der späteren SQL-Demos. Die Runtimefreigabe erfolgt erst in `ADV-008` und Gate V3.