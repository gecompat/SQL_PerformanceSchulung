# ADV-002 – Claim- und Quellenmatrix für den Vertiefungsstrang

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-002` |
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Geltungsbereich | M02, M03, M06, M07 sowie LAB-VP1 bis LAB-VP5 |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Quellenregister | [`SOURCE_REGISTER.md`](SOURCE_REGISTER.md) |
| Folgearbeit | `ADV-003` bis `ADV-007` |

## 1. Zweck

Die Matrix legt fest, welche technischen Aussagen in den geplanten Vertiefungsabschnitten zulässig sind, welche Evidenzklasse sie besitzen und mit welchen Quellen, Demos und Versionsprüfungen sie abgesichert werden müssen. Sie ist kein Folientext und kein Demo-Design. Sie bildet das fachliche Eingabemodell für Curriculum, Traceability, LAB-Design und spätere Präsentationsarbeit.

## 2. Evidenzregeln

`DOCUMENTED` bezeichnet unmittelbar durch aktive Microsoft-Primärquellen gestütztes Produktverhalten. `EMPIRICAL` bezeichnet beobachtbares Verhalten, dessen konkrete Ausprägung in der Zielversion reproduziert werden muss. `INFERENCE` bezeichnet eine begrenzte Herleitung aus mehreren Quellen und Messungen. `METHOD` bezeichnet einen Diagnose- oder Unterrichtsablauf und keine Produktgarantie.

Community-Quellen dürfen Begriffe, Planattribute, beobachtete Transformationen und Diagnosemethoden vertiefen, ersetzen jedoch keine Primärquelle für Featureverfügbarkeit, Compatibility Level, Konfigurationsvoraussetzungen oder Editionsgrenzen. Für undokumentierte Optimizer-Interna ist eine eigene synthetische Runtime-Reproduktion zwingend.

## 3. Claim-Matrix

### 3.1 V-OPT-A – Execution Plan Mechanics

| Claim-ID | Zulässige Kernaussage | Evidenz | Primärquelle | Ergänzung | Demo-/Testbezug | Gültigkeit und Abnahme |
|---|---|---|---|---|---|---|
| `ADV-CLM-001` | Ein Actual Execution Plan ergänzt den kompilierten Plan um Laufzeitinformationen; er ist keine vollständige Zeitreihe des Workloads. | `DOCUMENTED` | `SRC-031` | `SRC-038` | `OPT-001`, `DGN-001` | 2019–2025; Plan-XML und Clientdarstellung getrennt prüfen. |
| `ADV-CLM-002` | Estimated Cost ist ein Optimizer-Kostenwert und darf nicht als gemessene Laufzeit oder Ressourcenrangliste interpretiert werden. | `DOCUMENTED` + `INFERENCE` | `SRC-001` | `SRC-037`, `SRC-038` | `OPT-015` | Folie muss Kostenmodell und Runtime-Metrik ausdrücklich trennen. |
| `ADV-CLM-003` | Ein Plan wird entlang Datenfluss, Zeilen, Ausführungsanzahl, Prädikaten und Warnungen untersucht; der grafisch teuerste Operator ist kein belastbarer Startpunkt. | `METHOD` | `SRC-031` | `SRC-037` bis `SRC-040` | `OPT-015`, LAB-VP1 | Abnahme durch unbekannten Beispielplan mit begründetem ersten Untersuchungspunkt. |
| `ADV-CLM-004` | Estimated und Actual Rows sind im Kontext von Ausführungsanzahl und Operatorseite zu lesen; isolierte Prozentabweichungen können irreführen. | `EMPIRICAL` | `SRC-031` | `SRC-039` | `OPT-001`, `OPT-015` | Plan-XML-Auswertung mit mindestens einer mehrfach ausgeführten inneren Eingabe. |
| `ADV-CLM-005` | Rebinds, Rewinds und Outer References beschreiben die wiederholte Verwendung innerer Planbereiche, sind jedoch keine pauschale Fehlerkennzeichnung. | `EMPIRICAL` | – | `SRC-039`, `SRC-042` | `OPT-016` | In 2019/2022/2025 mit identischem synthetischem Datenmodell revalidieren. |
| `ADV-CLM-006` | Ein Spool ist eine vom Optimizer gewählte Planstruktur; sein Nutzen oder Schaden ergibt sich aus Wiederverwendung, Aufbaukosten und tatsächlicher Zeilenverarbeitung. | `EMPIRICAL` | – | `SRC-042` | `OPT-016` | Vergleichsplan mit und ohne wiederverwendbaren inneren Bereich; keine pauschale Spool-Vermeidung. |
| `ADV-CLM-007` | Exchanges teilen parallele Planbereiche und verbinden Producer und Consumer; Parallelität garantiert keine gleichmäßige Arbeitsverteilung. | `DOCUMENTED` + `EMPIRICAL` | `SRC-001` | `SRC-043` | `OPT-017`, `RES-002` | Thread- und Zeilenverteilung in einem parallelen Actual Plan nachweisen. |
| `ADV-CLM-008` | Operatorbezogene CPU- und Elapsed-Werte besitzen in parallelen und Batch-Mode-Plänen Interpretationsgrenzen. | `EMPIRICAL` | `SRC-031` | `SRC-044` | `OPT-017`, `DGN-001` | Client-/CU-Ausgabe dokumentieren; Summen nicht ungeprüft mit Querydauer gleichsetzen. |

### 3.2 V-OPT-B – Row Goals, APPLY sowie Semi- und Anti-Joins

| Claim-ID | Zulässige Kernaussage | Evidenz | Primärquelle | Ergänzung | Demo-/Testbezug | Gültigkeit und Abnahme |
|---|---|---|---|---|---|---|
| `ADV-CLM-009` | `TOP`, `FAST n`, `EXISTS` und bestimmte Planformen können die Optimierung auf frühe Zeilenfindung ausrichten. | `EMPIRICAL` | – | `SRC-041` | `OPT-011` | Sichtbares oder aus Planform abgeleitetes Row Goal mit synthetischer Reproduktion. |
| `ADV-CLM-010` | Ein Row Goal kann Join-, Zugriffs- und Spoolentscheidungen beeinflussen, ist aber nicht ohne Prüfung die Ursache eines schlechten Plans. | `INFERENCE` | `SRC-001` | `SRC-041`, `SRC-042` | `OPT-011`, `OPT-012`, `OPT-016` | Schätzungen, frühe Trefferwahrscheinlichkeit und tatsächliche Arbeit gemeinsam vergleichen. |
| `ADV-CLM-011` | Semi- und Anti-Semi-Joins beschreiben logische Existenzprüfungen; die physische Planform kann davon abweichen. | `DOCUMENTED` + `EMPIRICAL` | `SRC-001` | `SRC-041` | `QRY-006`, `OPT-012` | `EXISTS`, `NOT EXISTS` und NULL-sensitive Gegenbeispiele verwenden. |
| `ADV-CLM-012` | `DISABLE_OPTIMIZER_ROWGOAL` ist nur eine kontrollierte Gegenprobe und keine allgemeine Tuningmaßnahme. | `METHOD` | – | `SRC-041` | `OPT-011` | Nur Testdatenbank; Ergebnisgleichheit, Planänderung und Nebenwirkung dokumentieren. |

### 3.3 V-APP-C – Parameter-sensitive Anwendungsabfragen

| Claim-ID | Zulässige Kernaussage | Evidenz | Primärquelle | Ergänzung | Demo-/Testbezug | Gültigkeit und Abnahme |
|---|---|---|---|---|---|---|
| `ADV-CLM-013` | Planwiederverwendung hängt von Cachekontext und Cache-Schlüsseln ab; unterschiedliche SET-Optionen können zusätzliche Cacheeinträge erzeugen. | `DOCUMENTED` + `EMPIRICAL` | `SRC-001` | `SRC-040`, `SRC-046` | `OPT-007`, `QRY-013` | Anwendung-/SSMS-Kontext anhand Planattribute und Cacheeinträge vergleichen. |
| `ADV-CLM-014` | Unterschiedliche Laufzeit zwischen Anwendung und SSMS ist eine Diagnosefrage zu Kontext, Parametern, Plan und Datenzustand, kein Beleg für einen einzelnen SET-Schalter. | `METHOD` | `SRC-001`, `SRC-027` | `SRC-046` | `QRY-013` | Mindestens vier Kontextdimensionen prüfen und voreilige Hypothese verwerfen. |
| `ADV-CLM-015` | Parameter Sensitivity entsteht, wenn ein wiederverwendeter Plan für relevante Werteverteilungen unterschiedlich geeignet ist. | `DOCUMENTED` + `EMPIRICAL` | `SRC-007` | `SRC-047` | `OPT-008` | Deterministischer Skew, kompilierter Wert und zwei gegensätzliche Laufzeitprofile. |
| `ADV-CLM-016` | Lokale Variablen, Parameter, Literale und Recompile liefern dem Optimizer unterschiedliche Informationen und dürfen nicht als semantisch gleichwertige Tuningtricks behandelt werden. | `DOCUMENTED` + `EMPIRICAL` | `SRC-001`, `SRC-007` | `SRC-045`, `SRC-046` | `QRY-004`, `OPT-008` | Identische Ergebnismenge, unterschiedliche Compile-/Reuse-Bedingungen dokumentieren. |
| `ADV-CLM-017` | `OPTION (RECOMPILE)` kann parameter- und laufzeitnahe Optimierung ermöglichen, tauscht jedoch Planwiederverwendung gegen zusätzliche Compilearbeit. | `DOCUMENTED` + `EMPIRICAL` | `SRC-001` | `SRC-045` | `QRY-004` | Compilekosten und Planqualität unter mehreren Ausführungen messen. |
| `ADV-CLM-018` | Parameterisiertes dynamisches SQL kann optionale Suchbedingungen gezielt formulieren; Werte werden als Parameter und nicht durch Stringkonkatenation eingebunden. | `METHOD` | `SRC-001` | `SRC-045` | `QRY-004` | SQL-Injection-Sicherheit, Ergebnisgleichheit und Cachewiederverwendung als Pflichtabnahme. |
| `ADV-CLM-019` | PSP erzeugt bei geeigneten Gleichheitsprädikaten mehrere Query Variants; Eligibility und tatsächliche Variantenbildung müssen im Plan beziehungsweise Query Store nachgewiesen werden. | `DOCUMENTED` + `EMPIRICAL` | `SRC-007`, `SRC-008` | `SRC-048` | `OPT-009` | SQL Server 2022/2025; ältere Versionen liefern begründeten `SKIP`. |
| `ADV-CLM-020` | OPPO verwendet Dispatcher- und Variant-Pläne für geeignete optionale Prädikate und setzt SQL Server 2025, CL 170 sowie die zutreffende Datenbankkonfiguration voraus. | `DOCUMENTED` | `SRC-026` | `SRC-049` | `OPT-010`, `QRY-004` | SQL Server 2025/CL170; 2019/2022 kontrolliert `SKIP`. |

### 3.4 V-MEM-D – Workspace Memory, Spills und Parallelität

| Claim-ID | Zulässige Kernaussage | Evidenz | Primärquelle | Ergänzung | Demo-/Testbezug | Gültigkeit und Abnahme |
|---|---|---|---|---|---|---|
| `ADV-CLM-021` | Required, Desired, Requested, Granted und Used Memory bezeichnen unterschiedliche Stufen des Query Execution Memory. | `DOCUMENTED` | `SRC-009`, `SRC-010` | `SRC-050` | `OPT-014`, `RES-004` | Planattribute und Grant-DMV derselben Ausführung zuordnen. |
| `ADV-CLM-022` | Ein Spill belegt unzureichend nutzbaren Workspace für einen Operator, aber nicht automatisch allgemeinen Instanzspeicherdruck. | `DOCUMENTED` + `INFERENCE` | `SRC-009`, `SRC-029`, `SRC-031` | `SRC-050` | `OPT-013`, `RES-004` | Spill-Warning, TempDB-Arbeit und fehlenden beziehungsweise vorhandenen `RESOURCE_SEMAPHORE` trennen. |
| `ADV-CLM-023` | Undergrant und Overgrant sind unterschiedliche Probleme: Undergrant kann Spills erzeugen, Overgrant kann Nebenläufigkeit reduzieren. | `DOCUMENTED` + `EMPIRICAL` | `SRC-009`, `SRC-010` | `SRC-050` | `OPT-014`, `RES-004` | Einzelquery und konkurrierenden Workload getrennt messen. |
| `ADV-CLM-024` | `RESOURCE_SEMAPHORE` beschreibt Warten auf Query Execution Memory und ist nicht mit Buffer-Pool-Druck gleichzusetzen. | `DOCUMENTED` | `SRC-010`, `SRC-035`, `SRC-036` | – | `RES-003`, `RES-007` | Wartender Grant, Wait-Scope und gleichzeitige Grants gemeinsam nachweisen. |
| `ADV-CLM-025` | Memory Grant Feedback verändert Grants über wiederholte Ausführungen; Modus, Persistenz und Voraussetzungen sind versionsabhängig. | `DOCUMENTED` | `SRC-009` | – | `OPT-014`, LAB-VP4 | 2019/2022/2025 mit CL und Query-Store-Zustand getrennt testen. |
| `ADV-CLM-026` | Parallelität kann Grantbedarf und Speicheraufteilung verändern; DOP allein erklärt weder Grantgröße noch Spill. | `DOCUMENTED` + `EMPIRICAL` | `SRC-001`, `SRC-009` | `SRC-043`, `SRC-050` | `OPT-017`, `RES-002`, `RES-004` | Seriellen und parallelen Plan unter gleichem Datenmodell vergleichen. |
| `ADV-CLM-027` | TempDB-Nutzung ist bei Sort-/Hash-Spills eine Folge der Plan- und Grantsituation und keine hinreichende Ursachenklassifikation. | `DOCUMENTED` + `INFERENCE` | `SRC-029`, `SRC-031` | `SRC-050` | `OPT-013`, `CON-009` | Planwarning, TempDB-Evidenz und Gegenmaßnahme als Kette darstellen. |

### 3.5 V-IQP-E – Versionsabhängige adaptive Verarbeitung

| Claim-ID | Zulässige Kernaussage | Evidenz | Primärquelle | Ergänzung | Demo-/Testbezug | Gültigkeit und Abnahme |
|---|---|---|---|---|---|---|
| `ADV-CLM-028` | IQP-Verfügbarkeit wird durch Engine-Version, Compatibility Level, Datenbankkonfiguration, Query Store und Eligibility gemeinsam bestimmt. | `DOCUMENTED` | `SRC-007`, `SRC-008`, `SRC-009`, `SRC-026` | – | LAB-VP4 | Featurematrix muss jede Voraussetzung als eigenes Feld führen. |
| `ADV-CLM-029` | Table Variable Deferred Compilation verwendet die bei der ersten Compilation beobachtete Kardinalität, erzeugt jedoch keine klassischen Spaltenhistogramme. | `DOCUMENTED` | `SRC-007`, `SRC-008` | – | `QRY-008`, `OPT-013` | CL150+; Wiederverwendung und Verteilungswechsel mitprüfen. |
| `ADV-CLM-030` | Interleaved Execution kann für geeignete MSTVFs die tatsächliche Kardinalität vor der weiteren Optimierung bereitstellen. | `DOCUMENTED` | `SRC-007`, `SRC-008` | – | `QRY-009` | CL140+ und Eligibility im Actual Plan nachweisen. |
| `ADV-CLM-031` | Scalar UDF Inlining ist eligibility- und planabhängig; `is_inlineable` allein garantiert keine tatsächliche Inlining-Entscheidung. | `DOCUMENTED` | `SRC-007`, `SRC-008` | – | `QRY-009` | CL150+; Planform und Ergebnisgleichheit prüfen. |
| `ADV-CLM-032` | Batch Mode on Rowstore kann geeignete Rowstore-Pläne im Batch Mode ausführen; tatsächliche Operatorausführung und Eligibility sind nachzuweisen. | `DOCUMENTED` + `EMPIRICAL` | `SRC-007`, `SRC-008` | – | `OPT-006`, `RES-002` | CL150+; keine pauschale Performancezusage. |
| `ADV-CLM-033` | CE Feedback und DOP Feedback sind getrennte Feedbackmechanismen mit eigenen Voraussetzungen und beobachtbaren Zuständen. | `DOCUMENTED` | `SRC-007`, `SRC-008` | – | `OPT-006`, `RES-002`, `DGN-003` | SQL Server 2022/2025 gemäß Featurematrix; 2019 `SKIP`. |

### 3.6 V-DGN-F – Performance-Incident-Diagnose

| Claim-ID | Zulässige Kernaussage | Evidenz | Primärquelle | Ergänzung | Demo-/Testbezug | Gültigkeit und Abnahme |
|---|---|---|---|---|---|---|
| `ADV-CLM-034` | DMVs zeigen überwiegend aktuellen oder kumulativen Zustand; Query Store und Extended Events liefern andere zeitliche und semantische Sichten. | `DOCUMENTED` | `SRC-027`, `SRC-028`, `SRC-035`, `SRC-036` | `SRC-051` | `DGN-002`, `DGN-003`, `DGN-005` | Diagnosefrage muss Scope, Zeitraum und Evidenzquelle nennen. |
| `ADV-CLM-035` | Query Store kann mehrere Pläne sowie Runtime- und Wait-Historie für dieselbe Query erfassen; Konfiguration und Erfassungsstatus begrenzen die Aussage. | `DOCUMENTED` | `SRC-027` | – | `DGN-003`, `DGN-007` | Query Store `READ_WRITE`, Capture Policy und Zeitraum dokumentieren. |
| `ADV-CLM-036` | Extended Events liefern ereignisbezogene Evidenz; Event-, Action-, Predicate- und Targetwahl bestimmen Kosten und Aussage. | `DOCUMENTED` + `METHOD` | `SRC-028` | `SRC-051` | `DGN-005`, `DGN-007` | begrenzte Ring-Buffer-Session, Cleanup und fehlende Ereignisse korrekt interpretieren. |
| `ADV-CLM-037` | Waits sind ein Hypothesenstart und benötigen Scope, Delta beziehungsweise Zeitbezug und eine bestätigende Gegenprobe. | `DOCUMENTED` + `METHOD` | `SRC-035`, `SRC-036` | `SRC-051` | `RES-007`, `DGN-007` | Task-, Request- und Instanzscope in derselben Fallstudie unterscheiden. |
| `ADV-CLM-038` | Eine belastbare Incident-Analyse verändert genau eine begründete Variable und wiederholt dieselbe Messung unter vergleichbaren Bedingungen. | `METHOD` | `SRC-028` | – | `DGN-001`, `DGN-007`, M07 | Baseline, Hypothese, Änderung, Vergleich, Nebenwirkung und Rückfallplan vollständig. |
| `ADV-CLM-039` | Ein Capstone-Fall muss plausible Alternativhypothesen durch fehlende oder widersprechende Evidenz verwerfen können. | `DIDACTIC` + `METHOD` | – | `SRC-046`, `SRC-047`, `SRC-051` | `DGN-007` | mindestens zwei falsche Hypothesen; Lösung darf nicht im Titel vorweggenommen werden. |

## 4. Zuordnung zu LAB-Serien

| LAB-Serie | Verbindliche Claim-Gruppen | Designpaket |
|---|---|---|
| `LAB-VP1` | `ADV-CLM-001` bis `ADV-CLM-012` | `ADV-004` |
| `LAB-VP2` | `ADV-CLM-013` bis `ADV-CLM-020` | `ADV-005` |
| `LAB-VP3` | `ADV-CLM-021` bis `ADV-CLM-027`, `ADV-CLM-037` | `ADV-006` |
| `LAB-VP4` | `ADV-CLM-019`, `ADV-CLM-020`, `ADV-CLM-025`, `ADV-CLM-028` bis `ADV-CLM-033` | `ADV-006` |
| `LAB-VP5` | `ADV-CLM-013` bis `ADV-CLM-015`, `ADV-CLM-034` bis `ADV-CLM-039` | `ADV-007` |

## 5. Offene Designfragen für Folgepakete

Die Matrix löst die fachliche Quellenfrage, nicht das konkrete Demo-Design. Folgende Entscheidungen bleiben bewusst für `ADV-003` bis `ADV-007` offen:

1. Welche Claims werden eigenständige Lernziele und welche bleiben Unterkriterien bestehender Lernziele?
2. Welche Planattribute sind in allen drei Zielversionen stabil genug für Golden-Metadaten?
3. Welche LAB-VP1-Schritte können dieselbe synthetische Datenbank und denselben Baseline-Plan verwenden?
4. Wie wird der Anwendungskontext in `QRY-013` ohne proprietären Treiber reproduziert?
5. Welche IQP-Funktionen benötigen getrennte Datenmodelle statt eines künstlich überladenen Versionsvergleichs?
6. Welche Memory-Demos bleiben Grün beziehungsweise Gelb und welcher Teil von `RES-003` bleibt Rot?
7. Welche Query-Store- und XE-Evidenz wird für `DGN-007` vorab erzeugt, ohne die Lösung vorwegzunehmen?

## 6. Abnahme ADV-002

`ADV-002` ist abgeschlossen, wenn diese Matrix im Repository vorliegt, alle Claims eine Evidenzklasse besitzen, Primär- und Ergänzungsquellen getrennt sind, versionsabhängige Aussagen eigene Abnahmebedingungen nennen und keine Community-Quelle als Produktgarantie verwendet wird. Diese Kriterien sind mit der vorliegenden Fassung erfüllt.

Der nächste fachliche Schritt ist `ADV-003`: Die Claims werden in beobachtbare Lernziele, Curriculumabschnitte und Traceability-Zeilen überführt. Erst anschließend werden die LAB-Serien vollständig entworfen.
