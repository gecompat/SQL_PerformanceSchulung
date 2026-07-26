# ADV-005 – Design LAB-VP2: Parameter Sensitivity und dynamische Suchbedingungen

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `ADV-005` |
| Status | `DESIGNED` |
| Stand | 2026-07-26 |
| LAB-Serie | `LAB-VP2` |
| Curriculum | `LO-M03-07`, `LO-M03-08`, ergänzend `LO-M02-07` |
| Claims | `ADV-CLM-013` bis `ADV-CLM-020` |
| Zielversionen | SQL Server 2019, 2022 und 2025 |
| Standardpfad | isolierte synthetische Testdatenbank; Clientkontext über neutrale Sessionsimulation |

## 1. Ziel und Abgrenzung

LAB-VP2 trennt Datenverteilung, Compilekontext, Planwiederverwendung, Client- beziehungsweise Sessionkontext und versionsabhängige adaptive Funktionen. Die Lernenden wählen keine pauschale Maßnahme gegen Parameter Sensitivity, sondern begründen zwischen wiederverwendetem Plan, `OPTION (RECOMPILE)`, sicher parameterisiertem dynamischem SQL, Parameter Sensitive Plan Optimization und Optional Parameter Plan Optimization.

Die Reihe behauptet nicht, dass SSMS, ein bestimmter Treiber oder `ARITHABORT` allein eine Laufzeitdifferenz verursachen. Der Anwendungskontext wird durch explizit dokumentierte Sessionprofile simuliert. Proprietäre Treiber, reale Anwendungscodes, globale Cacheleerung und Stringkonkatenation von Eingabewerten sind ausgeschlossen.

## 2. Didaktische Reihenfolge

`OPT-007` → `OPT-008` → `QRY-013` → `QRY-004` → `OPT-009` → `OPT-010`

`OPT-007` und `OPT-008` liefern Plan-Cache- und klassische Parameter-Sensitivity-Grundlagen. `QRY-013` verbindet diese Grundlagen mit dem Clientkontext. `QRY-004` vergleicht sichere Implementierungsstrategien. `OPT-009` und `OPT-010` ordnen PSP und OPPO in die Versionen 2022 beziehungsweise 2025 ein. Die gesamte Serie wird auf 90 bis 125 Minuten geplant.

## 3. Gemeinsames synthetisches Datenmodell

Die Serie verwendet eine markergebundene Datenbank mit folgenden neutralen Objekten:

- `dbo.SearchItem`: Faktentabelle mit deterministisch schiefer `CategoryCode`-Verteilung,
- `dbo.SearchItemStatus`: kleine Statusdimension,
- `dbo.SearchItemTag`: optionale Mehrfachzuordnung für zusätzliche Prädikate,
- `dbo.SearchItemDate`: beziehungsweise eine persistierte Datumsspalte im Faktmodell,
- dedizierte Prozeduren und Querymarker je Strategie.

Das Standardprofil enthält mindestens eine sehr häufige, eine mittlere und mehrere seltene Kategorien. Zeilenbreite, Datenmenge und Selektivität sind skalierbar. Die Ergebnisequivalenz wird über Zeilenanzahl, fachlichen Schlüsselbereich und stabile Checksumme geprüft. Zufallsdaten, öffentliche Beispieldatenbanken und Systemkataloge als Zeilengenerator sind unzulässig.

## 4. QRY-013 – Anwendung langsam, SSMS schnell

### 4.1 Lernziel

Unterschiedliche Laufzeit zwischen zwei Clients wird als Evidenzproblem untersucht. Zu prüfen sind mindestens Datenbankkontext, SET-Optionen, Parameterwerte und Compile-Reihenfolge beziehungsweise Planidentität. Die Demo muss mindestens eine plausible Ein-Ursachen-Hypothese verwerfen.

### 4.2 Clientkontext-Simulator

Zwei neutrale Sessionprofile werden über das vorhandene Prozess- und `sqlcmd`-Framework ausgeführt:

- `CLIENT_PROFILE_A`: dokumentierter Satz expliziter SET-Optionen,
- `CLIENT_PROFILE_B`: davon abweichender, ebenfalls expliziter Satz.

Die Profile heißen bewusst nicht `SSMS` oder `APPLICATION`, weil konkrete Clients und Treiberversionen andere Defaults besitzen können. Beide Profile rufen dieselbe synthetische Prozedur mit denselben und anschließend mit unterschiedlichen Parameterwerten auf.

### 4.3 Plan- und Cacheisolation

- Jede Demo verwendet eine dedizierte Prozedur und eindeutige Marker.
- Cachebereinigung erfolgt ausschließlich objektbezogen, beispielsweise durch `sp_recompile` auf das Demoobjekt oder durch Neuanlage im markergebundenen Setup.
- `DBCC FREEPROCCACHE` ohne spezifischen Planbezug ist verboten.
- `sys.dm_exec_plan_attributes`, Query Stats und Plan XML werden nur für die markierten synthetischen Statements ausgewertet.

### 4.4 Verbindliche Evidenz

- `@@OPTIONS` und die explizit gesetzten Optionen,
- Datenbank-ID und Objektbezug,
- Plan Handle beziehungsweise Planidentität,
- `set_options` und weitere relevante Planattribute,
- kompilierter und ausgeführter Parameterwert, soweit im Plan verfügbar,
- Estimated/Actual Rows, Reads, CPU, Duration und Ergebnischecksumme,
- Zuordnung, ob die Abweichung aus getrenntem Cacheeintrag, Compilewert, Datenzustand oder einer anderen beobachteten Dimension folgt.

### 4.5 Abnahme

Die Demo gilt als bestanden, wenn sie zeigt, dass gleiche Querytexte allein keine identischen Ausführungsbedingungen garantieren. Sie darf nicht mit der Aussage enden, eine einzelne SET-Option sei allgemein die Ursache oder Lösung.

**Sicherheitsstufe:** Grün. **Sessions:** 2 nacheinander oder kontrolliert parallel. **Mindestprofil:** 2 Kerne, 4 GB. **Berechtigungen:** versionsbewusst `VIEW SERVER STATE` beziehungsweise `VIEW SERVER PERFORMANCE STATE`, sofern Cache-DMVs ausgewertet werden; sonst begründeter Skip. **Quellen:** `SRC-001`, `SRC-027`, `SRC-040`, `SRC-046`.

## 5. Erweiterung QRY-004 – Optionale Parameter und Strategieauswahl

### 5.1 Getrennte Queryfamilien

Die Demo vergleicht nicht künstlich alle Funktionen mit demselben Statement, sondern unterscheidet:

1. optionales Catch-all-Prädikat,
2. statisches SQL mit `OPTION (RECOMPILE)`,
3. sicher parameterisiertes dynamisches SQL,
4. PSP-fähige Gleichheitssuche,
5. OPPO-fähiges optionales Prädikat.

PSP und OPPO lösen unterschiedliche Problemformen. Ihre Ergebnisse werden deshalb in derselben Datenbasis, aber in getrennten Queryfamilien beurteilt.

### 5.2 Catch-all-Baseline

Die Baseline verwendet optionale Prädikate der Form `@CategoryCode IS NULL OR CategoryCode = @CategoryCode` und optional einen Datums- oder Statusfilter. Seltene, häufige und nicht eingeschränkte Ausführungen werden mit identischem Ergebnisvertrag gemessen. Die Baseline ist keine absichtlich semantisch falsche Abfrage.

### 5.3 `OPTION (RECOMPILE)`

Die Recompile-Variante verwendet denselben statischen Querytext und dieselben Parameter. Gemessen werden Planqualität, Reads, CPU, Duration und Compilearbeit über mehrere Ausführungen. Eine einzelne schnelle Ausführung reicht nicht als Abnahme.

### 5.4 Sicher parameterisiertes dynamisches SQL

Prädikatsfragmente stammen ausschließlich aus einer festen Whitelist. Alle Werte werden über `sp_executesql`-Parameter gebunden. Verboten sind direkte Wertkonkatenation, dynamische Objektbezeichner ohne `QUOTENAME` und das Protokollieren beliebiger Benutzereingaben.

Pflichtprüfungen:

- Ergebnisgleichheit zu den statischen Varianten,
- keine Werte im generierten SQL-Text,
- erwartete Wiederverwendung je Prädikatsform,
- begrenzte Zahl unterschiedlicher Queryformen,
- fehlerhafte oder unbekannte Filterdefinition führt zu kontrolliertem Abbruch.

### 5.5 PSP

PSP wird nur für geeignete Gleichheitsprädikate geprüft. Voraussetzungen und Abnahme:

- SQL Server 2022 oder 2025,
- zutreffender Compatibility Level und Datenbankkonfiguration,
- ausreichende Schiefe und tatsächliche Eligibility,
- Dispatcher-/Variant-Evidenz im Plan oder Query Store,
- SQL Server 2019 liefert `SKIP_FEATURE_UNAVAILABLE`.

Eine ausbleibende Variantenbildung trotz korrekter Version ist als `SKIP_FEATURE_NOT_ELIGIBLE` mit Evidenz zu behandeln und nicht durch undokumentierte Tricks zu erzwingen.

### 5.6 OPPO

OPPO wird nur in SQL Server 2025 mit Compatibility Level 170 und aktivierter zutreffender Konfiguration geprüft. Ältere Versionen liefern `SKIP_FEATURE_UNAVAILABLE`. Nachzuweisen sind Dispatcher- und Query-Variant-Struktur sowie getrennte Behandlung relevanter optionaler Prädikatszustände. OPPO wird nicht als Ersatz für beliebig komplexe dynamische Suchbedingungen dargestellt.

### 5.7 Mess- und Ergebnisvertrag

Für jede Strategie werden erfasst:

- Zeilenanzahl und Checksumme,
- Estimated/Actual Rows,
- Logical Reads, CPU und Duration,
- Compile- und Planwiederverwendungsindikatoren,
- Zahl und Identität relevanter Planvarianten,
- Versions-, Compatibility-Level-, Query-Store- und Konfigurationszustand,
- Nebenwirkungen auf Kompilierung und Cachebestand.

Die Bewertung verwendet Richtungen und Verhältnisse, keine universellen Millisekunden- oder Zeilenschwellen.

## 6. LAB-VP2-Ablauf

| Schritt | Demo | Beobachtungsauftrag |
|---:|---|---|
| 1 | `OPT-007` | Cachekontext, Compile und Reuse trennen |
| 2 | `OPT-008` | Schiefe, kompilierter Wert und ungeeignete Wiederverwendung nachweisen |
| 3 | `QRY-013` | Clientkontext systematisch untersuchen und voreilige Ursache verwerfen |
| 4 | `QRY-004` Catch-all | einheitliche Planform gegen unterschiedliche Selektivität prüfen |
| 5 | `QRY-004` Recompile/Dynamic SQL | Planqualität, Compilearbeit, Sicherheit und Wiederverwendung vergleichen |
| 6 | `OPT-009` | PSP-Voraussetzungen und Variantenbildung prüfen |
| 7 | `OPT-010` | OPPO-Voraussetzungen und Grenzen prüfen |
| 8 | Transfer | Strategie anhand Verteilung, Version, Sicherheit und Workload auswählen |

## 7. Preflight, Sicherheit und Cleanup

Der Preflight prüft Engine-Version, Compatibility Level, Query Store, Datenbankkonfiguration, Cache-DMV-Berechtigungen und verfügbaren Speicher. Query Store darf nur über `FWK-007` mit rekonstruierbarem Ausgangszustand aktiviert werden. Cleanup stellt die ursprüngliche Query-Store- und Datenbankkonfiguration wieder her und entfernt die markergebundene Testdatenbank.

Verboten sind:

- globale Cacheleerung,
- instanzweite Konfigurationsänderungen,
- reale Anwendungs- oder Diagnosedaten,
- proprietäre Treiber als Pflichtabhängigkeit,
- Stringkonkatenation von Eingabewerten,
- feste Behauptung, ein bestimmter Client oder SET-Schalter sei generell schneller.

## 8. Test- und Versionsmatrix

| Funktion | SQL 2019 / CL150 | SQL 2022 / CL160 | SQL 2025 / CL170 |
|---|---|---|---|
| klassischer Planreuse-/Skew-Fall | PASS | PASS | PASS |
| QRY-013 Clientkontext | PASS | PASS | PASS |
| Catch-all, Recompile, Dynamic SQL | PASS | PASS | PASS |
| PSP | `SKIP_FEATURE_UNAVAILABLE` | PASS oder `SKIP_FEATURE_NOT_ELIGIBLE` | PASS oder `SKIP_FEATURE_NOT_ELIGIBLE` |
| OPPO | `SKIP_FEATURE_UNAVAILABLE` | `SKIP_FEATURE_UNAVAILABLE` | PASS oder `SKIP_FEATURE_NOT_ELIGIBLE` |

Die Zielmatrix verwendet aktuelle Engine- und Compatibility-Level-Kombinationen. Zusätzliche CL-Gegenproben werden nur implementiert, wenn sie eine konkrete Lernentscheidung unterstützen.

## 9. Implementierungsschnitte

1. gemeinsames deterministisches Skew- und Suchdatenmodell,
2. `QRY-013` mit neutralem Clientkontext-Simulator,
3. `QRY-004` Catch-all, Recompile und sicheres dynamisches SQL,
4. `OPT-009` PSP-Variante und kontrollierte Skips,
5. `OPT-010` OPPO-Variante und kontrollierte Skips,
6. LAB-VP2-Orchestrierung und Transferaufgabe.

Jeder Schnitt erhält vollständige Demo-Metadaten, statische Prüfung, Runtime-Tests und Cleanup-Nachweis. Query-Store-/XE-Pilotvalidierung darf parallel erfolgen, wird aber nicht stillschweigend als durch dieses Design erledigt markiert.

## 10. Designfreigabe

`ADV-005` erreicht `VALIDATED`, wenn Design, maschinenlesbarer Vertrag und statische Prüfung konsistent sind. Der Status bestätigt keine implementierte SQL-Demo. Runtimefreigabe und Planvariantennachweis folgen in `ADV-008` und Gate V3.