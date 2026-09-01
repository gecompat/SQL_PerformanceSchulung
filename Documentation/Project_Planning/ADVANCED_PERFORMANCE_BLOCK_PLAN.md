# Integrationsplan – Vertiefende SQL-Server-Performance-Blöcke

| Merkmal | Wert |
|---|---|
| Arbeitspakete | `ADV-001` bis `ADV-010` |
| Status | `VALIDATED` |
| Planversion | 1.5 |
| Stand | 2026-09-01 |
| Zielplattform | SQL Server 2019, 2022 und 2025 |
| Curriculumbezug | M02, M03, M06 und M07 |
| Standard-Ausführungspfad | T-SQL in einer isolierten synthetischen Testdatenbank |
| Quellenbasis | Microsoft Learn, SQLServerFast, Paul White, Erland Sommarskog, Brent Ozar und Erik Darling |
| Claim- und Quellenmatrix | [`ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md`](../Research/ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md) |
| Curriculum und Traceability | [`CURRICULUM_ARCHITECTURE.md`](../Curriculum/CURRICULUM_ARCHITECTURE.md), [`TRACEABILITY_MATRIX.md`](../Curriculum/TRACEABILITY_MATRIX.md) |
| Design LAB-VP1 | [`ADV_004_LAB_VP1_DESIGN.md`](ADV_004_LAB_VP1_DESIGN.md) |
| Design LAB-VP2 | [`ADV_005_LAB_VP2_DESIGN.md`](ADV_005_LAB_VP2_DESIGN.md) |
| Design LAB-VP3/VP4 | [`ADV_006_LAB_VP3_VP4_DESIGN.md`](ADV_006_LAB_VP3_VP4_DESIGN.md) |
| Design LAB-VP5 | [`ADV_007_LAB_VP5_DESIGN.md`](ADV_007_LAB_VP5_DESIGN.md) |

## 1. Zweck und Entscheidung

Die ausgewerteten Fachquellen rechtfertigen einen zusammenhängenden Vertiefungsstrang für Query Processing, Execution Plans, parameterabhängige Abfragen, Workspace Memory, Intelligent Query Processing und Incident-Diagnose. Es wird kein nach Autoren oder Websites benanntes Schulungsmodul aufgebaut. Die Inhalte werden nach technischen Fragestellungen strukturiert und in die bestehende Curriculumarchitektur integriert.

Ein zusätzliches Hauptmodul ist nicht erforderlich. Die Vertiefung erweitert die vorhandenen Module M02, M03, M06 und M07. Dadurch bleibt der Einsteigerpfad unverändert, während für fortgeschrittene Teilnehmer eine fachlich geschlossene Folge von Theorie, Plananalyse, reproduzierbarer Demo und Diagnosefall entsteht.

Die Quellen erfüllen unterschiedliche Rollen. Microsoft-Dokumentation bleibt maßgeblich für dokumentierte Produkteigenschaften, Versionsgrenzen, Compatibility Levels und Featurevoraussetzungen. SQLServerFast und die Beiträge von Paul White dienen der vertieften Beschreibung von Planoperatoren, Planattributen und Optimizer-Verhalten. Erland Sommarskog liefert belastbare anwendungsnahe Analysen zu Parameter Sensitivity, Plan Cache, SET-Optionen und dynamischen Suchbedingungen. Beiträge von Brent Ozar und Erik Darling werden als empirische Fall- und Diagnosequellen verwendet. Sie ersetzen keine Herstellerdokumentation und begründen keine universellen Schwellenwerte.

## 2. Verbindliche Quellen- und Evidenzregeln

Jede neue oder geänderte technische Aussage erhält mindestens eine Quellen-ID aus dem projektweiten Quellenregister. Eine Folie oder Teilnehmerunterlage darf eine Quelle nicht nur allgemein am Kapitelende nennen; die Quelle muss der konkreten Aussage, dem Lernziel und der Demo zugeordnet sein.

Für den Vertiefungsstrang gelten folgende Regeln:

1. `DOCUMENTED` wird ausschließlich verwendet, wenn die Aussage unmittelbar durch eine aktive Primärquelle getragen wird.
2. Aussagen über undokumentierte Operator- oder Optimizer-Interna werden als `EMPIRICAL` oder `INFERENCE` gekennzeichnet und durch eine reproduzierbare Demo oder einen klar begrenzten Messpfad abgesichert.
3. Community-Quellen werden nicht als Produktgarantie oder vollständige Versionsmatrix behandelt.
4. Texte, Diagramme und Beispiele externer Quellen werden nicht übernommen. Die Schulungsunterlagen verwenden eigenständige Erklärungen, eigene synthetische Testdaten und eigene Visualisierungen.
5. Ein Effekt aus einem Einzeltest wird nicht als allgemeine Regel formuliert. Erwartet werden Invarianten, Richtungen, Verhältnisse oder begründete Bandbreiten.
6. Bei Widerspruch zwischen Primärquelle, Community-Quelle und Runtime-Evidenz wird der Widerspruch im Konflikt- und Entscheidungslog dokumentiert. Eine stillschweigende Auflösung ist unzulässig.
7. Versionsabhängige Aussagen nennen Engine-Version, Compatibility Level, Datenbankkonfiguration und gegebenenfalls Query-Store-Voraussetzungen getrennt.

Die konkrete Einstufung der 39 geplanten Vertiefungsclaims ist seit `ADV-002` in der [Claim- und Quellenmatrix](../Research/ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md) verbindlich.

## 3. Fachliche Vertiefungsabschnitte

### 3.1 V-OPT-A – Execution Plan Mechanics

Dieser Abschnitt erweitert M02 um die interne Leselogik eines Execution Plans. Im Mittelpunkt stehen Datenfluss, Operatorhierarchie, planweite und operatorbezogene Eigenschaften, Estimated und Actual Values, Number of Executions, Rebinds, Rewinds, Outer References, Warnings sowie die Grenzen grafischer Kostenanteile.

Der Abschnitt wird nicht als Operatorlexikon vorgetragen. Die SQLServerFast Execution Plan Reference dient als Nachschlagebasis. In der Schulung werden Operatorfamilien ausgewählt, deren Verhalten eine Diagnoseentscheidung verändert: Access Methods, Joinoperatoren, Sorts, Hashes, Aggregates, Spools, Exchanges, Filter, Compute Scalar, Assert, Top und ausgewählte Window-Operatoren.

Primäre Zuordnung: `OPT-001`, `OPT-012`, `OPT-013`, `FWK-005`, `DGN-001`.

Neue Demo-Bündel:

| ID | Titel | Zweck | Risiko |
|---|---|---|---|
| `OPT-015` | Planweite und operatorbezogene Eigenschaften | Planwurzel, Datenfluss, Estimated/Actual Rows, Ausführungsanzahl, Warnings und Plan-XML konsistent lesen | Grün |
| `OPT-016` | Rebind, Rewind, Outer References und Spools | wiederholte innere Ausführung, Wiederverwendung und Worktable-Verhalten in Nested-Loops-/Apply-Plänen erklären | Grün |
| `OPT-017` | Parallele Planbereiche, Exchanges und Operatorzeiten | Branches, Threads, Exchanges, Parallel Skew und Grenzen operatorbezogener Zeitangaben untersuchen | Gelb |

Das vollständige Design einschließlich Datenmodell, Evidenz, Ressourcenprofil und Skip-Verträgen steht in [`ADV_004_LAB_VP1_DESIGN.md`](ADV_004_LAB_VP1_DESIGN.md).

### 3.2 V-OPT-B – Row Goals, APPLY sowie Semi- und Anti-Joins

Dieser Abschnitt verbindet die vorhandenen Themen `OPT-011`, `OPT-012`, `QRY-006` und `QRY-010`. Er erklärt, dass `TOP`, `FAST n`, `EXISTS` sowie bestimmte Semi-/Anti-Join-Transformationen die Optimierung auf eine erwartete Teilmenge ausrichten können. Untersucht werden sichtbare und indirekte Row Goals, Apply mit Outer References, der Unterschied zwischen logischer Form und physischer Planform sowie die mögliche Wechselwirkung mit Nested Loops, Scans und Spools.

Der Abschnitt vermittelt keine pauschale Empfehlung zum Deaktivieren von Row Goals. `DISABLE_OPTIMIZER_ROWGOAL` darf nur als kontrollierte Gegenprobe in einer synthetischen Testdatenbank verwendet werden. Die eigentliche Diagnosefrage lautet, welche Schätzung und welche Planannahme die frühe Zeilenfindung plausibel oder unplausibel macht.

Es werden zunächst keine zusätzlichen IDs vergeben. Die vorhandenen Bündel werden fachlich erweitert und in einer gemeinsamen LAB-Serie ausgeführt.

### 3.3 V-APP-C – Parameter-sensitive Anwendungsabfragen

Dieser Abschnitt erweitert M03 um den Unterschied zwischen einer Abfrage als isoliertem Text und derselben Abfrage im Anwendungskontext. Behandelt werden Plan Cache Keys, relevante SET-Optionen, unterschiedliche Cacheeinträge, kompilierte Parameterwerte, Parameter Sensitivity, lokale Variablen, `OPTION (RECOMPILE)`, parameterisiertes dynamisches SQL, optionale Suchparameter, mehrwertige Parameter und die Abgrenzung zu PSP und OPPO.

Die vorhandenen Demo-Bündel `OPT-007` bis `OPT-010`, `QRY-004`, `QRY-008` und `QRY-009` werden in einer durchgängigen Serie verbunden. Ergänzt wird folgender bisher nicht ausreichend repräsentierter Diagnosefall:

| ID | Titel | Zweck | Risiko |
|---|---|---|---|
| `QRY-013` | Anwendung langsam, SSMS schnell | SET-Optionen, Cache Keys, kompilierte Parameterwerte, Datenbankkontext und Planvergleich als Evidenzkette untersuchen | Grün |

`QRY-004` wird so erweitert, dass mindestens folgende Varianten unter identischer Datenverteilung verglichen werden: Catch-all-Prädikat, statisches SQL mit `OPTION (RECOMPILE)`, sicher parameterisiertes dynamisches SQL, PSP-fähige Gleichheitssuche und OPPO-fähiges optionales Prädikat. SQL-Injection-Sicherheit und Plan-Cache-Wiederverwendung sind eigenständige Abnahmekriterien.

Das vollständige Design einschließlich neutraler Clientprofile, Plan-Cache-Grenzen, PSP-/OPPO-Matrix und Sicherheitsvertrag steht in [`ADV_005_LAB_VP2_DESIGN.md`](ADV_005_LAB_VP2_DESIGN.md).

### 3.4 V-MEM-D – Workspace Memory, Spills und Parallelität

Dieser Abschnitt verbindet `OPT-013`, `OPT-014`, `RES-002`, `RES-003`, `RES-004`, `RES-007`, `DGN-002` und `DGN-005`. Er trennt die folgenden Sachverhalte:

- speicherverbrauchende Operatoren innerhalb eines Plans,
- Required, Desired, Requested, Granted, Max Used und tatsächlich verwendete Speicheranteile,
- Undergrant und operatorbezogenen Spill,
- Overgrant und reduzierte Nebenläufigkeit,
- wartende Grants und `RESOURCE_SEMAPHORE`,
- Memory Grant Feedback einschließlich versionsabhängiger Persistenz,
- Parallelität, Exchanges und Speicheraufteilung,
- TempDB-Auswirkung als Folge, nicht als alleinige Ursachenklassifikation.

Die vorhandenen IDs reichen für die technische Abdeckung aus. `RES-003` bleibt eine optionale rote Erweiterung auf einer dedizierten Wegwerfinstanz. Der normale LAB-VP3-Pfad darf ohne rote Speicherlast vollständig durchgeführt werden. Das vollständige Ressourcen-, Evidenz-, Timeout-, Kill-Switch- und Skip-Design steht in [`ADV_006_LAB_VP3_VP4_DESIGN.md`](ADV_006_LAB_VP3_VP4_DESIGN.md).

### 3.5 V-IQP-E – Versionsabhängige adaptive Verarbeitung

Dieser Abschnitt fasst die bereits verteilten IQP-Themen zu einem reproduzierbaren Versionsvergleich zusammen. Er umfasst mindestens:

- Batch Mode on Rowstore,
- Table Variable Deferred Compilation,
- Interleaved Execution für Multi-Statement TVFs,
- Scalar UDF Inlining,
- Row- und Batch-Mode Memory Grant Feedback,
- persistentes beziehungsweise perzentilbasiertes Memory Grant Feedback,
- Parameter Sensitive Plan Optimization,
- Cardinality Estimation Feedback,
- Degree of Parallelism Feedback,
- Optional Parameter Plan Optimization.

Für jedes Feature werden Engine-Version, Compatibility Level, Datenbankkonfiguration, Query-Store-Anforderung und Eligibility als getrennte Vorbedingungen erfasst. Ein neueres Feature wird nicht automatisch als bessere Lösung bewertet; maßgeblich sind Eignung, beobachtete Planänderung, Stabilität und Nebenwirkungen.

Primäre Zuordnung: `OPT-006`, `OPT-009`, `OPT-010`, `OPT-014`, `QRY-004`, `QRY-008`, `QRY-009`, `RES-002` und `DGN-003`.

Die verbindliche Feature- und Skip-Matrix steht in [`ADV_006_LAB_VP3_VP4_DESIGN.md`](ADV_006_LAB_VP3_VP4_DESIGN.md). Unterschiedliche Featurefamilien erhalten getrennte Datenmodelle, wenn ein gemeinsamer Vergleich Eligibility oder Ursache-Wirkung verfälschen würde.

### 3.6 V-DGN-F – Performance-Incident-Diagnose

Dieser Abschnitt erweitert M06 und M07 um vollständige Diagnosefälle. Ausgangspunkt ist nicht ein bekannter Operator, sondern ein beobachtetes Symptom. Die Teilnehmer müssen die Evidenzkette selbst aufbauen: Zeitpunkt und Workload abgrenzen, geeignete Historie bestimmen, gute und schlechte Pläne vergleichen, Parameter- und Kontextinformationen sichern, Statistiken und Verteilung prüfen, Waits und Grants korrelieren, genau eine Änderung auswählen und die Wirkung unter vergleichbaren Bedingungen messen.

Neues Demo-Bündel:

| ID | Titel | Zweck | Risiko |
|---|---|---|---|
| `DGN-007` | Zeitabhängige Regression eines Suchworkloads | Query Store, Plan Cache, Plan-XML, Runtime-/Wait-Historie und Parameterkontext zu einer vollständigen Ursachenhypothese verbinden | Gelb |

`DGN-007` wird als Capstone-LAB ausgeführt. Der sichtbare Teilnehmerfall darf die Lösung nicht im Titel, Dateinamen, Querykommentar oder Marker vorwegnehmen. Mindestens zwei plausible, aber falsche Hypothesen müssen anhand fehlender oder widersprechender Evidenz verworfen werden. Das vollständige Incident-, Evidenzfreigabe-, Vergleichs- und Rückfalldesign steht in [`ADV_007_LAB_VP5_DESIGN.md`](ADV_007_LAB_VP5_DESIGN.md).

## 4. LAB-Serien

Die Vertiefung wird in fünf LAB-Serien gegliedert. Eine Serie ist eine didaktische Reihenfolge vorhandener und neuer Demo-Bündel; sie erzeugt nicht automatisch neue technische Artefakte.

### LAB-VP1 – Planmechanik und Operatorinteraktion

Reihenfolge: `OPT-001` → `OPT-015` → `OPT-012` → `OPT-016` → `OPT-011` → `QRY-006` → `OPT-013` → `OPT-017`.

Ergebnis: Ein Plan wird nicht anhand des optisch teuersten Operators beurteilt, sondern entlang Datenfluss, Schätzungen, Ausführungsanzahl, Prädikaten, Wiederverwendung, Warnings und Laufzeitevidenz.

### LAB-VP2 – Parameter Sensitivity und dynamische Suchbedingungen

Reihenfolge: `OPT-007` → `OPT-008` → `QRY-013` → `QRY-004` → `OPT-009` → `OPT-010`.

Ergebnis: Die Teilnehmer können Parameter Sensitivity nachweisen, Anwendungskontext und SSMS-Kontext trennen und zwischen Recompile, sicherem dynamischem SQL, PSP und OPPO anhand konkreter Voraussetzungen wählen.

### LAB-VP3 – Workspace Memory und Spills

Reihenfolge: `OPT-014` → `OPT-013` → `RES-004` → `RES-003` → `RES-007` → `DGN-005`.

Ergebnis: Spill, Undergrant, Overgrant, wartender Grant, Query Execution Memory und allgemeiner Memory Pressure werden nicht miteinander verwechselt. `RES-003` bleibt optional und rot.

### LAB-VP4 – Intelligent Query Processing 2019–2025

Reihenfolge: `QRY-008` → `QRY-009` → `OPT-014` → `OPT-009` → `OPT-006` → `RES-002` → `OPT-010`.

Ergebnis: Featurewirkung und Featurevoraussetzung werden getrennt. Ein kontrollierter `SKIP` auf einer älteren Version oder bei fehlender Eligibility ist ein erwartetes Testergebnis und kein Fehler.

### LAB-VP5 – Diagnosefall und Transfer

Reihenfolge: `DGN-001` → `DGN-003` → `QRY-013` → `DGN-007` → M07-Transferaufgabe.

Ergebnis: Eine vollständige Diagnosekette führt von einem zeitlichen Symptom zu einer messbaren, quellengebundenen und reversiblen Änderung. Mindestens zwei Alternativhypothesen werden begründet verworfen.

## 5. Lernziele der Vertiefung

`ADV-003` hat neun zusätzliche Lernziele festgelegt. Sie sind ausschließlich `VERTIEFUNG` und verändern den gemeinsamen Kernpfad nicht.

| ID | Zielbereich | Beobachtbares Lernziel |
|---|---|---|
| `LO-M02-08` | Planmechanik | planweite und operatorbezogene Eigenschaften sowie Kostenmodell und Runtime-Evidenz unterscheiden |
| `LO-M02-09` | Operatorinteraktion | Rebinds, Rewinds, Outer References, Spools und parallele Planbereiche anhand tatsächlicher Ausführung erklären |
| `LO-M02-10` | Row Goals | Row Goals und logische Semi-/Anti-Join-Formen von ihrer physischen Planumsetzung trennen |
| `LO-M02-11` | IQP | Engine-Version, Compatibility Level, Konfiguration, Query Store und Eligibility als getrennte Featurevoraussetzungen prüfen |
| `LO-M03-07` | Anwendungskontext | Anwendung-/SSMS-Unterschiede über Cache-, Parameter-, Datenbank- und Datenkontext untersuchen |
| `LO-M03-08` | Parametrisierung | Recompile, sicher parameterisiertes dynamisches SQL, PSP und OPPO nach Information, Sicherheit und Wiederverwendung vergleichen |
| `LO-M06-07` | Workspace Memory | Grantstufen, Spills, Under-/Overgrant und Grant-Warten mit Plan-, DMV-, Wait- und TempDB-Evidenz trennen |
| `LO-M06-08` | Evidenz-Scope | Livezustand, kumulative Werte, Query-Store-Historie und XE-Ereignisse nach Zeitraum und Aussageebene kombinieren |
| `LO-M07-04` | Incident-Diagnose | mehrere plausible Ursachen priorisieren, Alternativhypothesen verwerfen und genau eine reversible Änderung vergleichen |

Die vollständigen Abnahmenachweise stehen in der [Curriculumarchitektur](../Curriculum/CURRICULUM_ARCHITECTURE.md); alle 39 Claims sind in der [Traceability-Matrix](../Curriculum/TRACEABILITY_MATRIX.md) genau einem dieser Lernziele zugeordnet.

## 6. Arbeitspakete und Reihenfolge

| ID | Größe | Status | Arbeit | Abschlusskriterium |
|---|---:|---|---|---|
| `ADV-001` | M | `VALIDATED` | quellenbasierten Integrationsplan erstellen und im Repository verankern | Plan, Quellenregister und Backlog sind konsistent verknüpft |
| `ADV-002` | M | `VALIDATED` | Aussagen- und Quellenmatrix für alle Vertiefungsabschnitte erstellen | 39 Claims besitzen Evidenzklasse, Quellen, Versionsgrenze und Abnahmebedingung |
| `ADV-003` | M | `VALIDATED` | Curriculum, Lernziele und Traceability-Matrix erweitern | 39 Claims sind neun beobachtbaren Vertiefungslernzielen zugeordnet; Kernpfad und 84 aktive Claims bleiben unverändert |
| `ADV-004` | L | `VALIDATED` | LAB-VP1 und neue Demos `OPT-015` bis `OPT-017` entwerfen | Datenmodell, Phasen, Evidenz, Sicherheitsgrenzen, Skips und Tests sind festgelegt |
| `ADV-005` | L | `VALIDATED` | LAB-VP2 einschließlich `QRY-013` und Erweiterung von `QRY-004` entwerfen | Clientkontext, Strategievarianten, Sicherheit, Versionsmatrix und Tests sind festgelegt |
| `ADV-006` | L | `VALIDATED` | LAB-VP3 und LAB-VP4 versionsbewusst entwerfen | Ressourcen-, Feature-, Query-Store-, Eligibility- und Skip-Matrix sind vollständig |
| `ADV-007` | L | `VALIDATED` | LAB-VP5 und `DGN-007` als Capstone-Fall entwerfen | mindestens zwei falsche Hypothesen sind kontrolliert widerlegbar; Vergleich und Recovery sind vollständig |
| `ADV-008` | XL | `VALIDATED` | Demos in kleinen unabhängigen PRs implementieren und testen | implementierte Demos besitzen statische Verträge und die zutreffende zweifache Zielmatrix; verbleibende Designs bleiben ausdrücklich Folgearbeit |
| `ADV-009` | L | `VALIDATED` | Masterdeck, Speaker Notes und Teilnehmerunterlage integrieren | jede sichtbare technische Aussage besitzt Quellen-ID, Demo-Bezug, Versionsgrenze und Tiefenprofil |
| `ADV-010` | M | `VALIDATED` | Vertiefungsstrang fachlich und didaktisch abnehmen | Quellenreview, Runtime-Evidenz, Material-Generalprobe und Traceability sind im Endabnahmereview vollständig |

## 7. Gates

### Gate V0 – Quellenfreigabe: `VALIDATED`

- Primär- und Ergänzungsquellen sind getrennt.
- Copyright- und Wiederverwendungsgrenzen sind dokumentiert.
- Jede undokumentierte Internalaussage besitzt die Evidenzklasse `EMPIRICAL` oder `INFERENCE`.
- Veraltete versionsbezogene Beiträge sind gegen aktuelle Microsoft-Dokumentation geprüft.
- Jeder Claim besitzt seit `ADV-003` Lernziel und Traceability-Eintrag.

### Gate V1 – Curriculumfreigabe: `VALIDATED`

- Der Kernpfad bleibt ohne Vertiefung vollständig verständlich.
- Die neuen Lernziele setzen nur im Kern eingeführte Begriffe voraus.
- Bestehende Demo-Bündel werden erweitert, bevor neue IDs entstehen.
- Jede LAB-Serie besitzt einen klaren Transfer in eine Diagnoseentscheidung.
- Die 39 geplanten Claims erhalten erst durch `ADV-009` und `PRS-012` aktive Folien und SlideKeys.

### Gate V2 – Designfreigabe: `VALIDATED`

- LAB-VP1 bis LAB-VP5 besitzen vollständige und statisch prüfbare Designverträge.
- Synthetische Datenprofile, erwartete Evidenz, Abbruch, Cleanup und Wiederholung sind festgelegt.
- Planform-, Feature-, Versions-, Compatibility-Level-, Query-Store- und Eligibility-Abhängigkeiten besitzen kontrollierte Skip-Codes.
- Erwartete Resultate werden als Richtung, Verhältnis, Eigenschaft oder begründeter Skip beschrieben.
- Rote Schritte sind von grünen und gelben Pfaden getrennt und benötigen dedizierte Infrastruktur sowie ausdrückliche Bestätigung.
- Der Capstone besitzt eine gestufte Evidenzfreigabe, mindestens zwei falsifizierbare Alternativhypothesen und genau eine reversible Referenzänderung.

### Gate V3 – Runtimefreigabe: `VALIDATED`

- Grüne Demos wurden auf SQL Server 2019, 2022 und 2025 ausgeführt.
- Featuregebundene Demos liefern auf nicht unterstützten Kombinationen einen begründeten `SKIP`.
- Gelbe Demos wurden im tatsächlich benötigten Ressourcenprofil validiert.
- Query Store, Extended Events und Plan-XML liefern die im Design erwartete Evidenz.
- Rote Demos wurden ausschließlich auf der dafür vorgesehenen isolierten Infrastruktur geprüft.

### Gate V4 – Lehrmittelfreigabe: `VALIDATED`

- Folie, Speaker Notes, Teilnehmerunterlage und Demo verwenden dieselben Begriffe und Quellen-IDs.
- Planabbildungen stammen aus den eigenen synthetischen Demos.
- Quellen sind an der Aussage und zusätzlich im Quellenverzeichnis nachvollziehbar.
- Die Generalprobe bestätigt Zeitbedarf, Übergänge, Recovery und Verständlichkeit.

## 8. Priorisierung

`ADV-001` bis `ADV-010` sowie Gate V0 bis Gate V4 sind abgeschlossen. `OPT-015`, `OPT-016`, `QRY-013`, `QRY-004`, `OPT-009`, `OPT-010` und `OPT-017` besitzen die zutreffenden Runtime-Nachweise. Die `QRY-004`-Runtimewarnung ist mit der Sprechernotiz synchronisiert; Deck, Notes und Tiefenprofile sind vollständig gerendert und abgenommen. Die Query-Store-/XE-Piloten sind ebenfalls runtimevalidiert; `DGN-007` bleibt ein eigener Folgeschnitt. Der rote Schnitt `RES-003` wird zuletzt und separat bearbeitet. Der Endabnahmenachweis steht in `ADV_010_FINAL_ACCEPTANCE_REVIEW.md`.

## 9. Mindestanforderungen an die Testumgebung

Normale Demos aus LAB-VP1, LAB-VP2 und große Teile von LAB-VP4 verwenden eine einzelne SQL-Server-Instanz und eine isolierte synthetische Testdatenbank. Als Mindestprofil werden zwei logische CPU-Kerne, 4 GB für die SQL-Server-Instanz und ausreichend freier Speicher für Testdatenbank und TempDB vorgesehen. Die konkrete Datenmenge wird skalierbar erzeugt.

LAB-VP3, LAB-VP5 und `OPT-017` benötigen für stabile Effekte gegebenenfalls vier logische CPU-Kerne und 8 GB für die Instanz. Ein künstlich begrenztes Container- oder VM-Profil ist nur zulässig, wenn ein Memory- oder Parallelitätsengpass mit einer normalen Testdatenbank nicht reproduzierbar ist. `RES-003` bleibt wegen instanzweiter Speicherwirkung Rot und darf nicht auf einer gemeinsam genutzten Instanz ausgeführt werden.

Die Werte sind Planungsuntergrenzen und keine Zusage bestimmter Laufzeiten. Jede Demo enthält einen Preflight, der Datenmenge, DOP, verfügbaren Speicher, Query-Store-Zustand und TempDB-Platz prüft und bei ungeeigneter Umgebung kontrolliert abbricht oder einen begründeten Skip liefert.

## 10. Quellenbasis des Plans

Die verbindlichen projektweiten Quellen-IDs werden in `Documentation/Research/SOURCE_REGISTER.md` gepflegt. Für diesen Plan sind insbesondere folgende Quellen relevant:

- `SRC-001`, `SRC-005` bis `SRC-010`, `SRC-026`, `SRC-027`, `SRC-031`, `SRC-035` und `SRC-036` als Microsoft-Primärquellen.
- `SRC-037` bis `SRC-040` für Execution-Plan-Referenz, gemeinsame Eigenschaften und planweite Eigenschaften bei SQLServerFast.
- `SRC-041` bis `SRC-044` für Row Goals, Spools, parallele Planbereiche und Operatorzeiten nach Paul White.
- `SRC-045` und `SRC-046` für dynamische Suchbedingungen sowie Anwendung-/SSMS-Kontext nach Erland Sommarskog.
- `SRC-047` bis `SRC-051` als empirische Fall- und Diagnosequellen zu Parameter Sensitivity, PSP, optionalen Parametern, Memory Grants und Wait-Scope.

## 11. Nächster ausführbarer Schritt

Der definierte Vertiefungsstrang ist bis Gate V4 abgenommen. Folgearbeit beginnt nicht durch pauschale Ausweitung dieses Blocks, sondern durch ein eigenständiges Demo- oder Szenariopaket mit Quellen-, Safety-, Lifecycle- und Runtimevertrag. Priorisiert werden die noch offenen interaktiven Szenario- und Bereitstellungspfade; `RES-003` bleibt rot und benötigt eine gesonderte Freigabe.
