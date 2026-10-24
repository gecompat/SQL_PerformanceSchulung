# Initialer Backlog

<!-- REGISTRY_BACKLOG_TSK_016:BEGIN -->
## DGN-004: QueryCompilationReplay und Gegenkennzeichnung dokumentieren

Der aktuelle Auftrag ergänzt bei TSK-016 die lesend geprüften Befunde zu
QueryCompilationReplay und zur Gegenkennzeichnung für DGN-004 (Planerzwingung). Replay bedeutet Wiederverwendung aufgezeichneter
Optimierungsschritte. Der positive Nutzungsnachweis und seine Gegenkennzeichnung
bleiben für SQL Server 2022/2025 offen. Nur Dokumentation und statische Prüfungen
im Pull-Request-Verfahren (Änderungsantrag); keine Umsetzung, Tests der Probe oder
SQL-/Lab-Läufe. Die übrige Verarbeitung bleibt pausiert.
Der [aktuelle Ausführungsstand](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md)
bindet Auftrag und Grenzen; bestehender Probenplan und frühere Befunde bleiben erhalten.

### TSK-016 – Analyze-Labs als gezielte Curriculum-Ergänzungen prüfen

Fachlicher Status: **in Arbeit** (`in_progress`); nur die Dokumentationsaufnahme der DGN-004-Marker-/Gegenkennzeichnungsbefunde ist aktuell autorisiert. Registrierungsstatus: `REGISTERED`.
Die Quellensichtungen für Schemasperren, Ad-hoc-Plancache, Deadlock-Varianten,
Planerzwingung, Last-Page-Inserts (Einfügungen auf der letzten Indexseite),
Memory Grants (Abfragespeicherzuteilungen), Buffer-Pool-Druck (Druck auf den
Datenseiten-Cache), Resource Governor (Ressourcensteuerung), Worker-Druck
(Druck auf Ausführungsthreads) und Log Shipping (Übertragung und
Wiederherstellung von Transaktionslog-Sicherungen) liegen mit Lücken vor.
Damit sind alle neun Kandidatenquellen gesichtet. CON-005 ist im begrenzten
Schemasperrenumfang validiert; OPT-007 ist im begrenzten Vollplanschnitt validiert. Sämtliche
weiteren Umsetzungen bleiben offen.
Keine neue Demo wird registriert.

Dieser Abschnitt ist die abgeleitete Ansicht von
[`artifacts.TSK-016` in der Registry](identity/registry.json). Fachliche Änderungen
werden dort gepflegt. Die übrigen historischen Backlogabschnitte bleiben erhalten.

Dokumentationsauftrag vom 24. Oktober 2026: die lesend geprüften DGN-004-Befunde zu QueryCompilationReplay, dem gepinnten Dokumentationskonflikt und einer belastbaren Gegenkennzeichnung bei TSK-016 ergänzen und per Pull Request nach origin/main integrieren. Nur statische CI (Continuous Integration; automatisierte Integrationsprüfungen) und lokale statische Dokumentationsprüfung. Keine Umsetzung, Tests der Probe oder SQL-/Lab-Läufe. Übrige Verarbeitung pausiert; bisherige Quellenbefunde und Probenplan unverändert erhalten.

**Prioritäten innerhalb dieser Planung:** P1 zuerst planen, P2 nachrangig beziehungsweise unter den genannten Bedingungen zurückgestellt, P3 gesonderte Infrastrukturentscheidung. Die Kandidatenreihenfolge gilt für dieses Planungspaket, nicht als Ausführungsfreigabe. Bestehende Sicherheitsprioritäten bleiben maßgeblich. Aufwand: M mittel, L groß, XL sehr groß; stets vorläufig.

**Quellenstand:** [Analyze-Szenariokatalog](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=6e557726a07ce7d389a36083c7e82d214b20822f),
Commit `6e557726a07ce7d389a36083c7e82d214b20822f`.
Die öffentliche Quelle wird neutral als Analyze-Quellprojekt über die verifizierte
GitHub-Repository-ID `1302553964` bezeichnet. Quellenlinks verwenden die offizielle
API (Application Programming Interface; Programmierschnittstelle). Commit,
Dateipfad und Linienzahl bleiben nachvollziehbar zugeordnet.
Am 22. Oktober 2026 ausschließlich lesend: Katalogzuordnungen und Szenariotitel geprüft; lokale Katalogbytes stimmen nach Zeilenendennormalisierung mit dem genannten Commit überein. Keine Skript-, Verify- oder Laufzeitqualifikation.

#### Statische Quellensichtung zu den ersten beiden Kandidaten

Erfasst am 2026-10-23. Statische, ausschließlich lesende Sichtung von Katalog, Szenariodefinitionen, Runbooks, gemeinsamen SQL-Bausteinen und dem zugehörigen Aufruf-/Verify-Pfad. Die Quellen stimmen mit dem unveränderten Analyze-Commit überein. Keine Tests, SQL- oder Lab-Ausführung; keine Laufzeitabnahme.

CON-005 (Schemasperren) und OPT-007 (Ad-hoc-Plancache) behalten ihre Reihenfolge als erste Prüfkandidaten. Auch die Sichtungen zu CON-006 (Deadlock-Varianten), DGN-004 (Planerzwingung), IDX-007 (Einfügungen auf der letzten Indexseite und Schlüsselvergleiche), RES-004 (Abfragespeicherzuteilungen), RES-003 (Buffer-Pool-Druck und Ressourcensteuerung), RES-001 (Worker-Druck und echte Erschöpfung) und INF-006 (Log Shipping als gesonderter Infrastrukturumfang) sind mit Nachweislücken abgeschlossen. Alle neun Kandidatenquellen sind damit gesichtet; sämtliche Erweiterungsideen bleiben offen und sind nicht direkt übernahmefähig. Die Sichtung ist keine Umsetzung, Laufzeitabnahme oder Freigabe zur weiteren autonomen Verarbeitung.

**Gemeinsame Befunde vor einer späteren Adaption:**

- **Variablenübergabe im vorhandenen Runner:** Der Aufrufpfad übergibt Szenario, Lauftoken und weitere Werte mit sqlcmd -v. Die unverändert kopierten SQL-Dateien setzen dieselben Variablen anschließend durch :setvar auf Vorgaben zurück, darunter LAB-INVALID-000. Nach der dokumentierten Variablenpriorität gewinnt :setvar; die beabsichtigte Szenario- und Laufbindung wird dadurch überschrieben. Statischer Ausführungspfadfehler; nicht als ausgeführter Fehlernachweis ausgeben. Vor späterer Wiederverwendung muss die tatsächliche Parameterbindung eindeutig geklärt und belegt sein. Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:1](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Orchestration/Modules/DiagnosticLab/Private/Installer.ps1:89](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/Installer.ps1?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1:63](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1?ref=6e557726a07ce7d389a36083c7e82d214b20822f). [Produktdokumentation](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-use-scripting-variables?view=sql-server-ver17#variable-precedence-low-to-high).

- **Fehlender Eigentumsmarker im Cleanup:** Die Eigentumsprüfung lautet IF @DatabaseOwner <> @LabRunId. Bei fehlendem Marker bleibt @DatabaseOwner NULL; der Vergleich liefert UNKNOWN (unbekannt) und löst die Abweisung nicht aus. Im folgenden Pfad wird die feste Datenbank Lab001Wave3 zur Löschung ausgewählt. Statisch erkennbare Schutzlücke. Vor einer Schulungsadaption sind die vollständigen markergebundenen Eigentumsprüfungen des Schulungsvertrags erforderlich; keine Laufzeitverletzung oder bereits erfolgte Korrektur behaupten. Quellen: [Lab/Scenarios/Performance/_Shared/Cleanup.sql:38](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:162](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f). [Produktdokumentation](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/null-and-unknown-transact-sql?view=sql-server-ver17).

- **Befundcode ist kein unabhängiger Analyzer-Nachweis:** Observe.sql bildet FindingCodes direkt aus dem Skriptwert @FindingCode; der Code wird nicht aus dem Analyzerergebnis abgeleitet. Test-LabScenario vergleicht anschließend die erzeugte Hülle mit dem erwarteten Code. Wegen des separat belegten :setvar-Konflikts ist im unveränderten Aufruf nicht nachgewiesen, dass der Runbookcode tatsächlich als SQL-Wert ankommt. Analyzer-Aufruf und Status werden berücksichtigt; der konkrete positive Analyzer-Befund und das in der Definition verlangte Mindestvertrauen HIGH werden dadurch nicht unabhängig geprüft. Eine erfolgreiche Hüllenprüfung genügt nicht als Ursachen- oder Diagnosebeleg. Der spätere Schulungsergebnisvertrag muss die tatsächlichen fachlichen Beobachtungen prüfen. Quellen: [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1?ref=6e557726a07ce7d389a36083c7e82d214b20822f).

- **Cachebereinigung ist nicht laufgenau:** Die Planselektion im Cleanup akzeptiert entweder die feste Datenbankkennung oder einen gemeinsamen Textmarker LAB001_WAVE3. Der Textpfad ist nicht an den einzelnen Lauf gebunden; anschließend wird DBCC FREEPROCCACHE für die ausgewählten Planhandles aufgerufen. Vor Wiederverwendung Abgrenzung auf tatsächlich eigene Pläne und die passende Sicherheitsstufe klären. Ein Planhandle begrenzt den einzelnen Eingriff, ersetzt aber keine hinreichende Eigentumsselektion. Quellen: [Lab/Scenarios/Performance/_Shared/Cleanup.sql:142](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f).

**Grenzen der Sichtung:**

- SQL Server 2019, 2022 und 2025 sind in den Szenariodefinitionen aufgeführt. Die Definitionen benennen native Plattformnachweise selbst als externes Gate; die statische Sichtung erbringt keine Versions- oder Laufzeitabnahme.
- Der ältere Analyze-Lernpfad bezeichnet LAB-CONC-002 als komplexes Blocking und LAB-PLAN-003 als allgemeine Plan-Cache-Analyse. Für diese Aufnahme wurden stattdessen der aktuelle Katalog und die tatsächlichen Szenariobausteine verwendet.
- Vor einer Codeübernahme ist die projektspezifische Analyze-Lizenz mit Urheberangabe und Weitergabebedingungen zu berücksichtigen. Die Quellensichtung ist keine pauschale Lizenz- oder Veröffentlichungsfreigabe.

Nachlesbare Quellen zu diesen Grenzen: [Lab/Scenarios/Performance/LAB-CONC-002/scenario.json:79](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-CONC-002/scenario.json?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/LAB-PLAN-003/scenario.json:81](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-PLAN-003/scenario.json?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/LEARNING_PATH.md:39](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/LEARNING_PATH.md?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/LEARNING_PATH.md:58](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/LEARNING_PATH.md?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [LICENSE.md:5](https://api.github.com/repositories/1302553964/contents/LICENSE.md?ref=6e557726a07ce7d389a36083c7e82d214b20822f).

#### Ergänzende Quellensichtung: Deadlock-Varianten und Planerzwingung

Erfasst am 2026-10-23; Quellenstand `fd18d829904b6b1631f385cfaad340ca3c72bcbb`. Ausschließlich lesende Sichtung von Katalog, drei Szenariodefinitionen und Runbooks, gemeinsamen SQL-Bausteinen, Analyzer- und Aufruf-/Verify-Pfad; Abgleich mit den bestehenden Schulungsinhalten. Keine Tests, SQL-, Lab- oder CI-Ausführung während der Quellensichtung. Statische Repositoryprüfungen zur Veröffentlichung sind davon getrennt; keine Laufzeitabnahme.

Die zunächst am Quellenstand add76bdefb3bdeeb3273cae16ecf4ee6bbe33c64 gelesenen Szenario- und Aufrufdateien wurden gegen fd18d829904b6b1631f385cfaad340ca3c72bcbb abgeglichen und waren unverändert. Die Fundstellen dieser ergänzenden Sichtung sind an fd18d829904b6b1631f385cfaad340ca3c72bcbb gebunden; der frühere Stand 6e557726a07ce7d389a36083c7e82d214b20822f bleibt für die erste Sichtung erhalten.

Die gemeinsamen Grenzen bei Variablenübergabe, Eigentumsprüfung im Cleanup und konfigurierten Befundcodes sind auch im ergänzend geprüften Aufrufpfad vorhanden. Sie ersetzen keine variantenspezifischen Konfliktgraphen oder tatsächlichen Forcing-Erfolgs-/Fehlernachweise. Der Analyze-Runner wird nicht zur Übernahme freigegeben.

Nachlesbare gemeinsame Fundstellen: [Lab/Scenarios/Performance/_Shared/Worker.sql:1](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Orchestration/Modules/DiagnosticLab/Private/Installer.ps1:89](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/Installer.ps1?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1:63](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb).

Die drei Runbooks wählen SQL_ONLY (vorgesehene SQL-Ausführung), keine reine CONTRACT_FIXTURE (Vertragsattrappe). Der Katalogstatus IMPLEMENTED_ACTIONS_GATE bezeichnet vorhandene Aktionsbausteine, keine Laufzeitqualifikation. Die Szenariodefinitionen führen SQL Server 2019, 2022 und 2025 auf, verlangen tatsächliche Plattformnachweise aber weiterhin außerhalb des Repositoryvertrags. Die Sichtung erteilt keine Versions-, Lizenz- oder Implementierungsfreigabe.

Quellen zur Szenarioreife: [Lab/Scenarios/Catalog/scenarios.json:233](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Catalog/scenarios.json:341](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-DEAD-002/scenario.json:79](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-DEAD-002/scenario.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-DEAD-003/scenario.json:79](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-DEAD-003/scenario.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-QS-002/scenario.json:81](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-QS-002/scenario.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb).

#### Ergänzende Quellensichtung: Einfügungen auf der letzten Indexseite

Erfasst am 2026-10-23; Quellenstand `00c52fdbd99288839cc570b58a3f2337e610740a`. Ausschließlich lesende Sichtung von Katalog, drei LAB-LATCH-Szenariodefinitionen und Runbooks, gemeinsamen SQL-Bausteinen, Analyzer und Aufruf-/Verify-Pfad; Abgleich mit vorhandenen Schulungsinhalten und Microsoft-Primärquellen. Keine Tests, SQL-, Lab- oder CI-Ausführung während der Quellensichtung. Statische Repositoryprüfungen zur Veröffentlichung sind davon getrennt; keine Laufzeitabnahme.

Die ergänzenden IDX-007-Fundstellen sind an den unveränderlichen Quellenstand 00c52fdbd99288839cc570b58a3f2337e610740a gebunden. Die bereits erfassten Sichtungen am Stand 6e557726a07ce7d389a36083c7e82d214b20822f und fd18d829904b6b1631f385cfaad340ca3c72bcbb bleiben mit ihrer bisherigen Quellenbindung erhalten.

Die gemeinsam verwendeten SQL- und Aufrufdateien sind gegenüber der vorherigen Sichtung am Stand fd18d829904b6b1631f385cfaad340ca3c72bcbb unverändert. Die bereits dokumentierten Grenzen bei Variablenübergabe, Eigentumsprüfung und konfigurierten Befundcodes gelten daher auch für diese Szenarien. Ein Katalog- oder Befundcode ersetzt keinen tatsächlichen Engpass- oder Leistungsnachweis; der Analyze-Runner wird nicht zur Übernahme freigegeben.

Nachlesbare gemeinsame Fundstellen: [Lab/Scenarios/Performance/_Shared/Worker.sql:1](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1?ref=00c52fdbd99288839cc570b58a3f2337e610740a).

Die Runbooks wählen SQL_ONLY (vorgesehene SQL-Ausführung), keine reine CONTRACT_FIXTURE (Vertragsattrappe). Der Katalogstatus IMPLEMENTED_ACTIONS_GATE bezeichnet vorhandene Aktionsbausteine, keine Laufzeitqualifikation. Die Szenariodefinitionen führen SQL Server 2019, 2022 und 2025 auf und benennen tatsächliche Plattformnachweise als externes Gate. Keine Versions-, Lizenz- oder Implementierungsfreigabe durch diese Sichtung; alle Kandidaten bleiben offene Arbeit.

Quellen zur Szenarioreife: [Lab/Scenarios/Catalog/scenarios.json:260](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/LAB-LATCH-001/scenario.json:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-LATCH-001/scenario.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/LAB-LATCH-002/scenario.json:81](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-LATCH-002/scenario.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/LAB-LATCH-003/scenario.json:81](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-LATCH-003/scenario.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a).

#### Ergänzende Quellensichtung: Abfragespeicherzuteilungen

Erfasst am 2026-10-23; Quellenstand `59e6c9cc8e786828bc710ca6963121511aedb07a`. Ausschließlich lesende Sichtung von LAB-MEM-001: Katalog, Szenariodefinition, Runbook, gemeinsame SQL-Bausteine, Memory-Grant-Analyzer und Aufruf-/Verify-Pfad; Abgleich mit vorhandenem Schulungsumfang und Microsoft-Primärquellen. Keine Tests, SQL-, Lab- oder CI-Ausführung während der Quellensichtung. Statische Repositoryprüfungen zur Veröffentlichung sind davon getrennt; keine Laufzeitabnahme.

Die ergänzenden RES-004-Fundstellen sind an den unveränderlichen Quellenstand 59e6c9cc8e786828bc710ca6963121511aedb07a gebunden. Die bereits erfassten Sichtungen an den früheren Ständen bleiben mit ihren bisherigen Quellenbindungen erhalten; spätere Änderungen des Quellprojekts sind nicht Gegenstand dieser Befunde.

Die bereits dokumentierten Grenzen bei Variablenübergabe, Eigentumsprüfung und konfigurierten Befundcodes bestehen im geprüften gemeinsamen Aufrufpfad weiter. Ein AVAILABLE-Status oder eine Befundhülle ist kein unabhängiger Nachweis einer wartenden eigenen Grant-Anforderung. Der Analyze-Runner wird nicht zur Übernahme freigegeben.

Nachlesbare gemeinsame Fundstellen: [Lab/Scenarios/Performance/_Shared/Worker.sql:1](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1?ref=59e6c9cc8e786828bc710ca6963121511aedb07a).

Das Runbook wählt SQL_ONLY (vorgesehene SQL-Ausführung), keine reine CONTRACT_FIXTURE (Vertragsattrappe). Der Katalogstatus IMPLEMENTED_ACTIONS_GATE bezeichnet vorhandene Aktionsbausteine, keine Laufzeitqualifikation. Die Szenariodefinition führt SQL Server 2019, 2022 und 2025 auf und benennt tatsächliche Plattformnachweise als externes Gate. Keine Versions-, Lizenz- oder Implementierungsfreigabe durch diese Sichtung; alle Kandidaten bleiben offene Arbeit.

Quellen zur Szenarioreife: [Lab/Scenarios/Catalog/scenarios.json:53](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/LAB-MEM-001/scenario.json:33](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-001/scenario.json?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/LAB-MEM-001/scenario.json:83](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-001/scenario.json?ref=59e6c9cc8e786828bc710ca6963121511aedb07a).

#### Ergänzende Quellensichtung: Buffer-Pool-Druck und Ressourcensteuerung

Erfasst am 2026-10-23; Quellenstand `ffb8ffa48b48fac025f47a2caea514c2f09d66ed`. Ausschließlich lesende Sichtung von LAB-MEM-002 und LAB-MEM-003: Katalog, Szenariodefinitionen, Runbooks, gemeinsame SQL-Bausteine, beide vorrangigen Analyzer und Aufruf-/Verify-Pfad; Abgleich mit vorhandenem Schulungsumfang und Microsoft-Primärquellen. Keine Tests, SQL-, Lab- oder CI-Ausführung während der Quellensichtung. Statische Repositoryprüfungen zur Veröffentlichung sind davon getrennt; keine Laufzeitabnahme.

Die ergänzenden RES-003-Fundstellen sind an den unveränderlichen Quellenstand ffb8ffa48b48fac025f47a2caea514c2f09d66ed gebunden. Frühere Sichtungen und ihre Quellenbindungen bleiben erhalten; spätere Änderungen des Quellprojekts sind nicht Gegenstand dieser Befunde.

Die gemeinsamen Szenario- und Aufrufdateien sind gegenüber dem vorherigen Quellenstand 59e6c9cc8e786828bc710ca6963121511aedb07a unverändert. Die erfassten Grenzen bei Variablenübergabe, Eigentumsprüfung und konfigurierten Befundcodes gelten weiter. Der Verify-Pfad (Ergebnisprüfung) prüft Status, konfigurierte Codes und Cleanup, aber keine fachlich abgeleitete hohe Befundzuverlässigkeit. Der Analyze-Runner wird nicht zur Übernahme freigegeben.

Nachlesbare gemeinsame Fundstellen: [Lab/Scenarios/Performance/_Shared/Worker.sql:1](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

Beide Runbooks wählen SQL_ONLY (vorgesehene SQL-Ausführung), keine reine CONTRACT_FIXTURE (Vertragsattrappe). IMPLEMENTED_ACTIONS_GATE im Katalog kennzeichnet vorhandene Aktionsbausteine. EMULATED_INFRASTRUCTURE bei LAB-MEM-002 und REAL bei LAB-MEM-003 sind Einordnungen, keine Laufzeitnachweise. Die Definitionen nennen SQL Server 2019, 2022 und 2025 sowie externe Plattformnachweise; die Sichtung erteilt keine Versions-, Lizenz- oder Implementierungsfreigabe. Ressourcenprofile und allgemeine Bereitstellung bleiben bei SQL_Server_Lab.

Quellen zur Szenarioreife: [Lab/Scenarios/Catalog/scenarios.json:62](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Catalog/scenarios.json:71](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-MEM-002/scenario.json:6](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-002/scenario.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-MEM-003/scenario.json:6](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-003/scenario.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/README.md:5](https://api.github.com/repositories/1302553964/contents/Lab/README.md?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

#### Ergänzende Quellensichtung: Worker-Druck und echte Erschöpfung

Erfasst am 2026-10-23; Quellenstand `ffb8ffa48b48fac025f47a2caea514c2f09d66ed`. Ausschließlich lesende Sichtung von LAB-CPU-003: Katalog, Szenariodefinition, Runbook, gemeinsame SQL-Bausteine, Worker-Pressure-Analyzer und Aufruf-/Verify-Pfad; Abgleich mit vorhandenem Schulungsumfang und Microsoft-Primärquellen. Keine Tests, SQL-, Lab- oder CI-Ausführung während der Quellensichtung. Statische Repositoryprüfungen zur Veröffentlichung sind davon getrennt; keine Laufzeitabnahme.

Die ergänzenden RES-001-Fundstellen sind an den unveränderlichen Quellenstand ffb8ffa48b48fac025f47a2caea514c2f09d66ed gebunden. Die vorherige RES-003-Sichtung verwendet denselben Stand; frühere Sichtungen und Quellenbindungen bleiben erhalten. Spätere Änderungen des Quellprojekts sind nicht Gegenstand dieser Befunde.

Die bereits dokumentierten Grenzen bei Variablenübergabe, Eigentumsprüfung und konfigurierten Befundcodes gelten weiter. Der Verify-Pfad (Ergebnisprüfung) bestätigt weder einen ausgewerteten Worker-Mangel noch hohe Befundzuverlässigkeit. Eine erfolgreiche Diagnoseabfrage, vier laufmarkierte Sessions oder ein konfigurierter Erfolgscode ersetzen diesen Nachweis nicht. Der Analyze-Runner wird nicht zur Übernahme freigegeben.

Nachlesbare gemeinsame Fundstellen: [Lab/Scenarios/Performance/_Shared/Worker.sql:1](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Test-LabScenario.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

Das Runbook wählt SQL_ONLY (vorgesehene SQL-Ausführung), keine reine CONTRACT_FIXTURE (Vertragsattrappe). IMPLEMENTED_ACTIONS_GATE und EMULATED_INFRASTRUCTURE im Katalog kennzeichnen vorhandene Aktionsbausteine und nachgebildete Infrastrukturbedingungen, keine praktische Qualifikation. Die Szenariodefinition nennt SQL Server 2019, 2022 und 2025 und externe Plattformnachweise. Die ältere Spinlock-Zuordnung wurde nicht übernommen. Keine Versions-, Lizenz- oder Implementierungsfreigabe; alle Erweiterungen bleiben offene Arbeit.

Quellen zur Szenarioreife: [Lab/Scenarios/Catalog/scenarios.json:44](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-CPU-003/scenario.json:6](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-CPU-003/scenario.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-CPU-003/scenario.json:79](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-CPU-003/scenario.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/LEARNING_PATH.md:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/LEARNING_PATH.md?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

#### Ergänzende Quellensichtung: Log Shipping als eigener Infrastrukturumfang

Erfasst am 2026-10-23; Analyze-Quellenstand `ffb8ffa48b48fac025f47a2caea514c2f09d66ed`, ergänzend SQL_Server_Lab `2423ac75d7b07d29adbb63a2c218a6669db8363c`. Ausschließlich lesende Sichtung von LAB-LS-001 und des geplanten LAB-LS-002-Katalogeintrags: Definition, Runbook, SQL-Bausteine, eigener Infrastruktur-/Verify-Pfad und Log-Shipping-Analyzer; ergänzender Abgleich mit SQL_Server_Lab, vorhandenem Schulungsumfang und Microsoft-Primärquellen. Keine Tests, SQL-, Lab- oder CI-Ausführung während der Quellensichtung. Statische Repositoryprüfungen zur Veröffentlichung sind davon getrennt; keine Laufzeitabnahme.

Die INF-006-Befunde sind an den Analyze-Quellenstand ffb8ffa48b48fac025f47a2caea514c2f09d66ed und ergänzend an SQL_Server_Lab 2423ac75d7b07d29adbb63a2c218a6669db8363c gebunden. Frühere Sichtungen und Quellenbindungen bleiben erhalten. Spätere Änderungen beider Quellprojekte sind nicht Gegenstand dieser Befunde.

LAB-LS-001 verwendet einen eigenen Infrastrukturpfad. Er verarbeitet die Analyzer-Ausgaben, verlangt neue erfolgreiche Agent-Jobabschlüsse und vergleicht Dateibeziehungen für den Normal- und Rückstandsfall. Die Grenzen dieses Pfads betreffen unter anderem Objektzuordnung, vollständige Wiederherstellbarkeitsaussagen, SQL-Eigentum und Abbau nach Teilschrittfehlern. Allgemeine Infrastruktur verbleibt in SQL_Server_Lab; der alte Analyze-Runner wird nicht zur Übernahme freigegeben.

Nachlesbare Fundstellen zum Infrastrukturpfad: [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:208](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:412](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabLogShippingScenario.ps1:82](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabLogShippingScenario.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/README.md:5](https://api.github.com/repositories/1302553964/contents/Lab/README.md?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

LAB-LS-001 besitzt Aktionsbausteine und einen Ergebnisvertrag, aber keine durch diese Sichtung erbrachte native Plattform- oder Versionsabnahme. LAB-LS-002 bleibt PLANNED_NOT_IMPLEMENTED (geplant, nicht implementiert). Der absichtlich erzeugte Rückstand in LAB-LS-001 ist keine ausgeführte Netzwerkstörung oder Wiederanlaufprüfung. Fehlende alte Provisionierungsdateien und unterschiedliche Zustands-/Eigentumsverträge verhindern eine ungeprüfte Gesamtübernahme. P3 (gesonderte Infrastrukturentscheidung) und XL (sehr großer Aufwand) bleiben vorläufig; alle neun Erweiterungen und TSK-016 bleiben offen.

Quellen zur Szenarioreife: [Lab/Scenarios/Catalog/scenarios.json:431](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Catalog/scenarios.json:440](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Catalog/scenarios.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/scenario.json:83](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/scenario.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

#### Gemeinsamer weiterer Prüfauftrag

- Für jeden Kandidaten Katalog, scenario.json, runbook.json, referenzierte SQL-Bausteine und Verify-Vertrag am selben Quellenstand lesen; geplante Szenarien, reine Fixtures (Testaufbauten), implementierte Abläufe und tatsächliche Laufnachweise auseinanderhalten. Ein Katalogstatus wie IMPLEMENTED_ACTIONS_GATE ist keine Schulungsabnahme.
- Abweichende ältere Lernpfade mit dem aktuellen Katalog abgleichen: LAB-MEM-002 bedeutet Buffer-Pool-Druck (Druck auf den Datenseiten-Cache), nicht überdimensionierte Memory Grants (Speicherzuteilungen für Abfragen).
- Schwache Alternativnachweise im Verify-Vertrag prüfen: aktive Sessions allein belegen weder RESOURCE_SEMAPHORE (Warten auf Abfragespeicher) noch Worker-Erschöpfung (Mangel an Ausführungsthreads).
- Vor jeder späteren Wiederverwendung Herkunft, Nutzungsbedingungen, Versions-/Editionsgrenzen und das tatsächlich fehlende Lernziel prüfen; allgemeine Lab-Infrastruktur bleibt in SQL_Server_Lab.

#### Grenzen jeder späteren Erweiterung

- Lernziele und geeignete SQL-Bausteine wiederverwenden; weder den Analyze-Runner noch dessen gesamten Frameworkumfang ungeprüft übernehmen.
- Spätere ausführbare Demos benötigen die Schulungsverträge für Sessionsteuerung, vollständige Eigentumsmarker, Cleanup (sicheres Aufräumen), Recovery (Wiederherstellung nach Fehlern), Versionsgrenzen und Ergebnisnachweise. Änderungen am gemeinsamen Instanzzustand nur in ausdrücklich isolierter Umgebung.
- Kurze Erklärungen und Diagnosebeispiele benötigen keinen pauschalen neuen Benchmark (systematischen Leistungsvergleich). Konkrete Mess- oder Leistungsbehauptungen benötigen passende Evidenz mit Bedingungen und Grenzen.
- Aufwand ist ausschließlich eine vorläufige qualitative Einschätzung: M mittel, L groß, XL sehr groß; keine Zusage von Dauer oder Kapazität. Alle Kandidaten bleiben offen; spätere Umsetzung und Ausführung sind gesondert zu autorisieren.

#### Vorhandene Inhalte berücksichtigen

- `CON-004`, `CON-006`: Blocking (Blockierungen) und Deadlocks (zyklische Sperrkonflikte).
- `OPT-002`, `OPT-003`, `OPT-005`: Statistiken und Skew (ungleiche Datenverteilung).
- `QRY-004`, `OPT-009`, `OPT-010`: Plansensitivität, PSP (Parameter Sensitive Plan; parameterabhängige Planvarianten) und OPPO (Optional Parameter Plan Optimization; Optimierung optionaler Parameter).
- `OPT-015`, `OPT-016`, `OPT-017`: Planeigenschaften, Spools (Zwischenspeicheroperatoren) und Parallelität.
- `OPT-013`, `CON-009`: Spills (Auslagerung von Arbeitsspeicherinhalten) und TempDB (temporäre Systemdatenbank).
- `DGN-003`, `DGN-005`: Query Store (Abfragehistorie) und XE (Extended Events; Ereigniserfassung).
- `STL-008`, `STL-009`: Transaktionslog, VLF (Virtual Log Files; virtuelle Logabschnitte) und Commit-Batching (gebündelte Transaktionsabschlüsse).
- `IDX-006`, `IDX-010`, `RES-007`: Seitendichte, Columnstore (spaltenweise Speicherung) und Wait-Deltas (Wartezeitdifferenzen).

#### Planungsentscheidung vom 23. Oktober 2026

Priorisierung anhand der bereits registrierten neun Quellenbefunde, vorhandener Curriculumabdeckung, Nachweisgüte, Sicherheits-/Infrastrukturbedarf und begrenzbarem Lernzuwachs. Keine erneute Quellenabnahme oder ausgeführte Demo. Grundlage ist der integrierte Schulungsstand `7f47a393732fa843c9c10620274490a86de14029` mit den unverändert erhaltenen Quellenbefunden.

**Verworfen werden folgende Übernahmeformen:**

- Unveränderte Übernahme des Analyze-Runners oder seines gesamten Frameworks.
- Zusätzliche allgemeine Demos zu CPU (Central Processing Unit; Prozessor), Cache, Deadlocks (zyklischen Sperrkonflikten) oder Spills (Auslagerung von Arbeitsspeicherinhalten) ohne neues Lernziel.
- Aktive Sessions als Ersatz für Grant-Warten oder Worker-Erschöpfung; Cachebelegung als Ersatz für Speicherdruck; bloße Einfügeaktivität als Ersatz für Last-Page-Contention (Konkurrenz um die letzte Indexseite).

Kein Lerngebiet und keine stabile Kennung wird gelöscht. Zurückstellung betrifft den beschriebenen Erweiterungsschnitt; alle neun Kandidaten und TSK-016 bleiben offen. Aufwand M mittel, L groß, XL sehr groß ist weiterhin vorläufig.

#### Priorisierte offene Kandidaten

##### 1. CON-005 – Schema- und Metadatensperren als Ergänzung zu Blocking

**P1 · Begrenzter Schemasperrenschnitt validiert; Integration über PR310 · Aufwand M – vorläufig.**

**Planungsentscheidung:** Begrenzter Schemasperrenschnitt auf SQL Server 2019/2022/2025 validiert; Sperreskalation und weitere Metadatenpfade bleiben offen.

**Begründung:** Eigenständiger, klar abgrenzbarer Lernzuwachs gegenüber CON-004 (Blockierungsketten). Der Quellenbaustein zeigt einen plausiblen Auslöser, sein Ergebnisnachweis ist zu schwach; die Schulung besitzt bereits einen passenden Mehrsessionpfad.

**Abhängigkeiten:**

- Vorhandene CON-004-Sitzungssteuerung und Frameworkverträge für Eigentum, Sicherheit, begrenzte Orchestrierung und Ergebnisse verwenden; keine neue Infrastruktur voraussetzen.
- Vor einer Implementierung den beschriebenen Ergebnisvertrag sowie Objektzuordnung, Signaltransaktionen, Berechtigungen und Abbruchpfad abschließend prüfen.

**Wiederaufnahmebedingung:** Der begrenzte Schemasperrenschnitt besitzt seinen Versionsnachweis; die Integration mit aktuellen Head- und Main-Prüfungen wird in PR310 belegt. Sperreskalation, weitere Metadatenpfade und andere Kandidaten benötigen einen neuen Auftrag; die übrige autonome Verarbeitung bleibt pausiert.

**Quellen:** `LAB-CONC-002` (Schema-, Metadaten- und Kompilierungssperren).

**Abgrenzung:** CON-004 behandelt Blockierungsketten; CON-005 ist bereits für Lock Escalation (Sperreskalation), Schema Locks und Metadatenzugriff vorgesehen. Diesen bestehenden Umfang ergänzen, keine zweite Blocking-Demo anlegen.

**Weiterer Prüfauftrag:** Konkrete Sperrmodi, auslösende Operationen, Kompilierungs-/Metadatenpfad und Verify-Alternativen prüfen; Abgrenzung zur Sperreskalation festhalten.

**Statischer Quellenbefund:** LAB-CONC-002 enthält zwei Worker: ALTER TABLE innerhalb einer offenen Transaktion und eine konkurrierende Leseabfrage. Der Worker hält die Transaktion mit einer festen Wartezeit und nimmt die Änderung danach zurück.

- Observe.sql prüft gemeinsam für LAB-CONC-001 und LAB-CONC-002 nur, ob mindestens ein laufzugeordneter Request einen blocking_session_id größer null besitzt. Schemasperrmodus, Objekt und exakte Blockerbeziehung werden nicht geprüft.
- Feste Verzögerungen im Worker und drei Sekunden Startvorlauf ersetzen keine deterministische fachliche Sessionsteuerung. Ein eigenständiger Nachweis für Kompilierungs- oder Metadatensperren fehlt.

Quellen: [Lab/Scenarios/Performance/_Shared/Worker.sql:196](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/_Shared/Observe.sql:260](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/LAB-CONC-002/runbook.json:14](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-CONC-002/runbook.json?ref=6e557726a07ce7d389a36083c7e82d214b20822f).

**Vor einer späteren Umsetzung erforderlich:**

- Für die spätere Schulung Sch-M (Schemaänderungssperre) und Sch-S (Schemastabilitätssperre), Objektbezug und Blocker-/Wartebeziehung passend zum Lernziel belegen.
- Vorhandenen signalfähigen Schulungs-Mehrsessionpfad sowie vollständige Eigentums-, Abbruch- und Cleanup-Verträge anwenden; vorhandenen CON-004-Grundfall und die Abgrenzung zur Sperreskalation erhalten.

**Spätere Abnahme:**

- Blockierer, wartende Session und tatsächliche Schema-/Metadatensperre dem Lernziel eindeutig zuordnen; bloße Laufzeit oder aktive Sessions reichen nicht.
- Ergänzung nutzt den vorhandenen Mehrsessionpfad mit begrenzter Steuerung und sicherem Abbau; bestehende CON-004-Aussage bleibt erhalten.

**Aktueller Umsetzungsschnitt:** Drei signalisierte Akteure; Sch-M/GRANT gegen Sch-S/WAIT am selben Tabellenobjekt mit exakter Blocker-/Laufbindung; Rücknahme, Vergleich und markergeprüfter Cleanup. Keine Sperreskalation oder allgemeine Kompilierungs-/Metadatenabnahme.

**Nachweisstand:** Am 2026-10-23 bestand der Implementierungsstand ab27d42214ab24b6b12b2189e5b5e32da535166e den Workflow CON-005 Schemasperren, Lauf 39981693499: statische Verträge sowie SQL Server 2019/150, 2022/160 und 2025/170, jeweils Developer auf Linux in eigenen Dockercontainern. Je Version bestanden zwei reguläre Lifecycles, 30 Setup- und 30 Cleanup-Eigentumsgegenproben, vollständige Datei-Ablehnung, Idempotenz, 28 ungültige Eingaben, Rechte-/Sicherheitsprüfungen, vollständiger Inventarvergleich, normalisierter Voll-Lifecycle mit 48 äußeren Leerzeichen, elf Evidenzmutationen und Timeout bei unabhängig beobachtetem Sch-M-/Sch-S-Konflikt. Eigene Datenbanken und CI-Container wurden erfolgreich entfernt. Der unabhängige Quellenreview und fünf Offline-Testmethoden zum Containerabbau sind abgeschlossen. Alle drei eigenen lokalen Prüfcontainer sind ebenfalls entfernt; andere Instanzen blieben unverändert. Frühe Fehlversuche bleiben private Evidenz. PR310 bindet die anschließenden aktuellen Head-/Main-Prüfungen und den Integrationsnachweis; Windows und andere Editionen sind nicht qualifiziert.

Paket: [`CON-005 – Schemasperren trotz NOLOCK`](../Demos/07_Concurrency/CON-005_Schema_Locks/README.md). Prüfpfad: [`run_con005.py`](../Tests/Runtime/run_con005.py). Die übrige autonome Verarbeitung bleibt pausiert.

###### Begrenzter Planungsschnitt und Abnahme: Schemasperren

Begrenzter Schemasperrenschnitt implementiert und am 2026-10-23 auf SQL Server 2019/2022/2025 validiert. Integrationsnachweis und aktuelle Head-/Main-Prüfungen: PR310. Der weitere CON-005-Umfang bleibt offen.

**Lernziel:** Sch-S (Schemastabilitätssperre) und Sch-M (Schemaänderungssperre) am selben synthetischen Tabellenobjekt unterscheiden. Eine Leseabfrage mit NOLOCK (Verzicht auf Datensperren für den Lesezugriff) kann weiter auf Sch-S warten, wenn eine andere Sitzung Sch-M hält.

**Umfang:** Erster Schnitt: begrenzter Schemaänderungs-/Lesekonflikt mit Vergleich ohne offene Schemaänderung. Sperreskalation bleibt ein getrennter späterer CON-005-Teil; keine eigenständige Abnahme sämtlicher Kompilierungs- oder Metadatenpfade und keine Leistungsbehauptung.

**Akteure und Freigaben:**

- BLOCKER (Blockierer): eigenes Startsignal vor der Transaktion bestätigen, dann reversible Schemaänderung in offener Transaktion halten. Auf getrennt bestätigtes Freigabesignal warten; anschließend Transaktion zurückrollen und Abschluss außerhalb der Transaktion signalisieren.
- READER (Leser): Bereitschaft außerhalb einer Transaktion signalisieren, auf Leserfreigabe warten, dann die abgegrenzte Leseabfrage mit NOLOCK ausführen. Nach Aufhebung der Schemasperre erwartetes Ergebnis und Abschluss melden.
- OBSERVER (Beobachter): Start und Bereitschaft erfassen; tatsächlich gewährtes Sch-M am erwarteten Objekt und Blockierer prüfen, erst dann Leser freigeben. Tatsächlich wartenden Leser mit Sch-S und exakter Blockerbeziehung erfassen; anschließend Blockierer freigeben und beide Abschlüsse prüfen.

**Sitzungssteuerung:**

- Vorhandenen FWK-006-Vertrag (Mehrsessionsteuerung) und fwk.USP_Signal/fwk.USP_WaitForSignal verwenden. Lauf- und Demo-Kennung sowie Sitzung und Signal eindeutig binden. Feste Wartezeiten ersetzen kein Bereitschafts- oder Beobachtungssignal.
- Signale sind gewöhnliche Datenänderungen ohne autonome Transaktion. Keine Sichtbarkeit eines Signals innerhalb der noch offenen Schemaänderung voraussetzen. Bereitschaft und Freigaben werden außerhalb dieser Transaktion durch den jeweiligen unabhängigen Akteur bestätigt.
- Datenbank- und Objektkennung vor dem Sperrkonflikt auflösen und laufgenau festhalten. Beobachtung über die Diagnosekennungen durchführen; sperranfällige Metadatenabfragen auf das blockierte Tabellenobjekt während des Konflikts vermeiden. Keine Eigentumsentscheidung allein aus einer Sitzungsnummer ableiten.

**Erwarteter Nachweis:**

- sys.dm_tran_locks (dynamische Verwaltungssicht für Sperren): gewährtes Sch-M des Blockierers und wartendes Sch-S des Lesers auf derselben Ressource. Ressourcen anhand aller relevanten Ressourcenspalten samt Datenbank-/Objektbindung zuordnen; Sessionanzahl oder irgendeine Blockierung genügt nicht.
- sys.dm_exec_requests (dynamische Verwaltungssicht für laufende Anforderungen): Leser, tatsächliche blocking_session_id des Blockierers und LCK_M_SCH_S (Warten auf Schemastabilität) während desselben beobachteten Konflikts. Flüchtige Sichtwerte begrenzt abfragen; Beobachtungszeitpunkt und Laufbindung erfassen, keine Transaktionssnapshot-Garantie behaupten.
- Nach Freigabe: Leser beendet sich mit erwarteten synthetischen Daten, Schemaänderung ist zurückgerollt, eigene Transaktionen/Sitzungen bleiben nicht offen. Kontrolllesung ohne gehaltenes Sch-M liefert das erwartete Ergebnis. Aus fehlender Momentaufnahme allein keinen Erfolg ableiten.

**Sicherheit, Abbruch und Entwurfsgrenzen:**

- Geplant YELLOW (isoliertes Labor ausdrücklich bestätigen), eine eigene kleine synthetische Datenbank und genau drei Akteure. Vor Änderungen und Cleanup (Aufräumen) alle vier Eigentumsmarker SQLPERF.Project, SQLPERF.ContractVersion, SQLPERF.DemoId und SQLPERF.RunToken exakt prüfen. Keine globalen Cache- oder Instanzoptionen ändern.
- Vorläufige Entwurfsgrenzen: höchstens 120 Sekunden für reguläre Phasen, höchstens 15 Sekunden je Signal-/Beobachtungsschritt sowie ein getrennt begrenzter Cleanup-Pfad von höchstens 30 Sekunden. Dies sind Planungsgrenzen, keine gemessenen Laufzeiten; tatsächliche Manifest-/Harness-Abbildung und Datenmengen-/Transaktionsgrenzen vor Implementierung abschließend festlegen.
- Bei Fehler oder Timeout eigene Akteure begrenzt beenden, offene eigene Transaktion zurückrollen und Cleanup nach gestarteter Setup-Phase versuchen. Fremde Sitzungen oder Datenbanken weder beenden noch verändern. Unklare Eigentumszuordnung stoppt den mutierenden Abbau; Restzustand und Wiederaufnahmebedarf sichtbar ausweisen. Timeout ist kein Cleanupnachweis.

**Voraussetzungen und Ergebnisvertrag:**

- Geplante Zielversionen SQL Server 2019, 2022 und 2025; Plattform- und Editionsumfang sowie Compatibility Level (Datenbank-Kompatibilitätsstufe) vor der ausführbaren Freigabe dokumentieren und tatsächlich prüfen. Die bestehende CON-004-Abnahme überträgt sich nicht auf CON-005.
- Vorab Eigentum, isolierte Umgebung, sqlcmd (Microsoft-Kommandozeilenwerkzeug), Rechte für die eigene Schemaänderung und serverweite Diagnose prüfen: VIEW SERVER STATE für SQL Server 2019, VIEW SERVER PERFORMANCE STATE ab SQL Server 2022 für sys.dm_tran_locks. Fehlende Voraussetzungen vor Zustandsänderungen nach FWK-012 (Status-, Fehler- und Skip-Vertrag) als SKIP_PERMISSION, SKIP_TOOL_MISSING oder passendem bestehenden Skip-Code ausweisen.
- Fehlendes erwartetes Sperrbild bei erfüllten Voraussetzungen führt zu FAIL_TIMEOUT oder FAIL_RESULT_CONTRACT, nicht zu einem nachträglichen Skip. Ausführungs- und Cleanupfehler getrennt erhalten; PASS setzt den fachlichen Nachweis und erfolgreichen Abbau voraus. Keine neuen Statuscodes erfinden.

**Spätere Abnahme:**

- Vor einer Umsetzung: Akteurs-/Signalfolge auf Transaktionssichtbarkeit und Selbstblockierung prüfen, Diagnosefilter und Rücknahmebedingungen konkretisieren sowie die vorhandenen Eigentums-, Sicherheits-, Orchestrierungs-, Assertion- und Ergebnisverträge auf den Entwurf abbilden.
- Die gesonderte Umsetzungsfreigabe wurde am 2026-10-23 für den begrenzten Schemasperrenschnitt erteilt. Statische Prüfung, unabhängiger Quellenreview, zwei reguläre Lifecycles je Version und negative Abbruch-/Eigentums-/Timeoutfälle sind durch den unten gebundenen Versionsnachweis belegt. Windows, andere Editionen, Sperreskalation und weitere Metadatenpfade bleiben offen.

**Entwurfsquellen:**

- [CON-004: vorhandene Mehrsessionsteuerung und Beobachtung](https://github.com/gecompat/SQL_PerformanceSchulung/blob/7f47a393732fa843c9c10620274490a86de14029/Demos/07_Concurrency/CON-004_Blocking_Chain/Sessions/10_Head.sql); Stand `7f47a393732fa843c9c10620274490a86de14029`.
- [CON-004: tatsächliches Blocking vor Freigabe beobachten](https://github.com/gecompat/SQL_PerformanceSchulung/blob/7f47a393732fa843c9c10620274490a86de14029/Demos/07_Concurrency/CON-004_Blocking_Chain/Sessions/40_Observer.sql); Stand `7f47a393732fa843c9c10620274490a86de14029`.
- [Signalimplementierung: gewöhnliche Transaktionssichtbarkeit](https://github.com/gecompat/SQL_PerformanceSchulung/blob/7f47a393732fa843c9c10620274490a86de14029/Demos/00_Framework/Sql/FWK_MultiSessionControl.sql); Stand `7f47a393732fa843c9c10620274490a86de14029`.
- [Schulungsvertrag: Eigentum, sichere Ausführung und Ergebnisabnahme](https://github.com/gecompat/SQL_PerformanceSchulung/blob/7f47a393732fa843c9c10620274490a86de14029/.ai/DEMO_CONTRACT.md); Stand `7f47a393732fa843c9c10620274490a86de14029`.
- [Microsoft: NOLOCK und weiterhin erforderliche Schemasperren](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver17); Abruf 2026-10-23.
- [Microsoft: Sperrressourcen, Modi, Status und Berechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-tran-locks-transact-sql?view=sql-server-ver17); Abruf 2026-10-23.

##### 2. OPT-007 – Begrenzte Diagnose von Ad-hoc-Plancache-Wachstum

**P1 · Begrenzter Diagnoseplan ausgearbeitet; Umsetzung offen · Aufwand M – vorläufig.**

**Planungsentscheidung:** Begrenzter Ad-hoc-Plancache-Plan anhand der Quellenbefunde präzisiert; Batchliteral, gebundener Parameter und Vollplan-Ergebnisvertrag festgelegt. Umsetzung und Ausführung bleiben gesperrt.

**Begründung:** Der vorhandene Literalansatz ist begrenzt und didaktisch anschlussfähig. Laufgenaue Cachezuordnung, Cachetyp, Bytes und Parameterisierungsvergleich fehlen; diese Lücken lassen sich vor einer Lastdemo gezielt planen.

**Abhängigkeiten:**

- Reihenfolge nach CON-005 (Schemasperren) ist eine Kapazitätsentscheidung, keine technische Abhängigkeit.
- Eigene Datenbank, Lauftoken und Abfragemarker, Vergleichsbedingungen und sichere Bereinigung festlegen; keine globale Cacheleerung und keine zweite Plansensitivitätsdemo.

**Wiederaufnahmebedingung:** Abfrageform und Ergebnisvertrag sind als quellenbasierter Entwurf präzisiert. Eine Umsetzung benötigt einen ausdrücklichen Auftrag einschließlich erforderlicher SQL-/Lab-Läufe und einen Quellen-/Ergebnisreview vor dem ersten Lauf. Die erwarteten 20/40 Literalpläne und der eine wiederverwendete Prepared-Plan sind erst danach je Zielversion empirisch zu bestätigen. Andere Kandidaten bleiben pausiert.

**Quellen:** `LAB-PLAN-003` (Ad-hoc-Plancache-Wachstum).

**Abgrenzung:** OPT-007 umfasst bereits Compilation (Planübersetzung), Recompilation, Planwiederverwendung und Ad-hoc-Cache-Pollution (unnötige Cachebelegung). Abgrenzen von Plansensitivität und den vorhandenen Parameterdemos.

**Weiterer Prüfauftrag:** Erzeugung verschiedener Ad-hoc-Pläne, Messumfang, wirksame Abbruchgrenzen und Parameterisierungsvergleich prüfen; globale Cache-Eingriffe im Quellenablauf identifizieren.

**Statischer Quellenbefund:** LAB-PLAN-003 erzeugt im Setup höchstens 40 dynamische Abfragen mit unterschiedlichen Literalen und statischen Textmarkern. Die Beobachtung verlangt mindestens 20 Cacheeinträge mit passendem Text.

- Der Beobachtungsfilter prüft weder Datenbank- und Laufzuordnung noch Cacheobjekttyp, Wiederverwendung oder belegte Bytes. Eine Anzahl passender Cacheeinträge ist kein Nachweis einer bestimmten Speicherzunahme.
- Es fehlen eine vergleichbare Ausgangsmessung und eine Gegenüberstellung mit Parameterisierung. Ein vorhandener Cacheeintrag wird nicht nach vollständigem Plan und kleinem Planstub (reduziertem Cacheeintrag) unterschieden; eine Leistungsverbesserung ist nicht belegt.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:443](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/_Shared/Observe.sql:416](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:142](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=6e557726a07ce7d389a36083c7e82d214b20822f).

**Vor einer späteren Umsetzung erforderlich:**

- Diagnoseumfang und tatsächlich eigene Cacheeinträge definieren; Versions-, Berechtigungs-, Parametrisierungs- und Cachekonfiguration berücksichtigen.
- Für behauptetes Wachstum einen begründeten Vorher-/Nachhervergleich mit Cachetyp und Bytes vorsehen; für behauptete Verbesserungen eine passende Vergleichsvariante. Keine pauschale Benchmarkpflicht für rein erklärenden Inhalt.
- Die gemeinsame, nicht laufgenaue Planbereinigung nicht ungeprüft übernehmen; keine globale Cacheleerung als allgemeine Voraussetzung einführen.

Produktdokumentation: [Referenz 1](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-cached-plans-transact-sql?view=sql-server-ver17), [Referenz 2](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/optimize-for-ad-hoc-workloads-server-configuration-option?view=sql-server-ver17).

**Spätere Abnahme:**

- Diagnoseübung begrenzt Zahl, Dauer und Ressourcen ihrer synthetischen Abfragen; Planzahl und Cachebelegung beziehen sich auf den erklärten Messumfang.
- Falls Wachstum oder Verbesserungen quantitativ behauptet werden, passenden Ausgangs-/Vergleichszustand und Evidenz ausweisen; keine unkontrollierte globale Cacheleerung.

###### Begrenzter Implementierungsnachweis vom 23. Oktober 2026

**Abnahmestatus:** `validated` – ausschließlich der unten beschriebene Vollplanschnitt.

**Freigabe:** 2026-10-23

**Paket:** Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache

**Versionsprüfung:** Tests/Runtime/run_opt007.py

**Workflow:** .github/workflows/opt007-adhoc-cache.yml

**Umfang:** Begrenzter Vergleich von 40 DECLARE-/SELECT-Batches mit eingebetteten Werten und 40 sp_executesql-Aufrufen mit gebundenem @Key int; gleiche Tupel (k,k), tatsächliche Vollpläne und eindeutig eigene Cachebelegung. Keine allgemeine Leistungs- oder Speicherersparnisbehauptung.

**Ergebnisvertrag:** Literal-Snapshots mit 20/40 vollständigen Adhoc-Plänen; Parameter-Snapshots mit einem stabilen Prepared-Plan und execution_count 20/40, gleicher creation_time und plan_generation_num. Exakte vollständige Batchtexte, tatsächliches dbid, genau ein passender SELECT-XML-Knoten und seine physische Planstruktur sowie gültige exakte Statistikgrenzen sind Pflicht. Je Arm 40 exakte Tupel, 40 Schlüssel und Summe 820; fehlende Metadaten, Shells, Stubs, Zusatzparameter und Templateverweise scheitern.

**Statementdarstellung:** Empirisch in allen drei Zielversionen: Die Engine-Statementgrenzen schließen den abschließenden Strichpunkt aus; Prepared-XML enthält zusätzlich die feste Deklaration (@Key int). Nur diese konkreten Darstellungen sind zugelassen; der vollständige Cachebatch bleibt einschließlich Strichpunkt binär und längengenau gebunden.

**Schutzgrenzen:** Eigene vollständig markierte Datenbank, maximal 40 Zeilen/80 Nutzabfragen, 4096 UTF-16-Bytes je Nutztext, 128 MiB je Datei, 16 MiB beobachtete gesamte eigene Cachemenge beider Arme als Abbruchschwelle nach jedem Aufruf; 120 Sekunden regulär, 15 Sekunden je Phase, separat 30 Sekunden Cleanup. Keine Optionsumschaltung und keine Cacheleerung. Markerungewissheit und gescheiterte Erstmarkierung behalten den Erhaltungsweg.

**Tatsächlich ausgeführte Prüfungen:**

- Je Version zwei vollständige Lifecycles mit frischen Lauftokens und unveränderten finalen SQL-Quellen, vollständigen Phasen, exakten Tupel-/Plan-/Statistikprüfungen, FWK-011-Ergebnisnormalisierung und unabhängig bestätigter Datenbankabwesenheit erfolgreich.
- Je Version 30 Setup- und 30 Cleanup-Eigentumsgegenproben mit vollständigem Katalog-/Modul-/Marker-/Sentinelvergleich, vollständige Datei-Ablehnung, Setup-/Cleanup-Idempotenz und 37 ungültige Rohwert-/Sicherheitsfälle erfolgreich.
- Je Version neun Evidenzmutationen einschließlich gleicher Summe bei anderen Tupeln sowie 18 Plan-/Statistik-/Cache-Gegenfälle erfolgreich. Zusätzliche automatische Parameter und ParameterizedPlanHandle werden synthetisch zurückgewiesen; die echte gemeinsame L+P-Summenprüfung wird mit beiden vorhandenen Armen gegen Rückfall auf nur einen Arm geprüft.
- Je Version Kontext-/Konfigurationsgegenfälle, synthetischer Textgrößenabbruch, tatsächlicher Berechtigungsskip und vollständiger Lifecycle mit 48 äußeren Leerzeichen im Lauftoken erfolgreich. Kein realer Stubvergleich und keine Konfigurationsumschaltung.
- Je Version Timeout während eines unabhängig beobachteten aktiven eigenen SQL-Aufrufs mit erfolgreichem Cleanup und unabhängiger Datenbankabwesenheit erfolgreich; sieben Offline-Testmethoden zu numerischer Normalisierung und tatsächlichem Container-Cleanup erfolgreich.

**Review:** Unabhängiger Quellen-/Ergebnisreview abgeschlossen. Vier anfängliche Quellen-/Vertragsbefunde und zwei abschließende Testlücken sind korrigiert und nachgeprüft; keine offenen priorisierten Befunde im begrenzten Schnitt. Der Review führte selbst keine SQL-Läufe aus.

**Cleanup:** Alle drei eigenen lokalen Prüfcontainer nach Identitäts-/Image-/Eigentumsprüfung entfernt; Abwesenheit nach ID, Name und Eigentumslabel bestätigt. Die fünf anderen vorhandenen Lab-Container blieben erhalten.

**Evidenz:** Private Laufbelege und Fehlversuche bleiben unter Runtime/Temp unversioniert erhalten. Aktuelle Head-/Main-Prüfungen, CI-Containerbereinigung und vollständige Integration werden im zugehörigen Pull Request gebunden.

**Offen und pausiert:** Nur der begrenzte Ad-hoc-Vollplanschnitt ist validiert. Weitere historische OPT-007-Themen, Windows, andere Editionen, Podman, reale Stubmodi und eine allgemeine Erstmarkierungs-/Recoveryfreigabe bleiben offen. TSK-016 bleibt in Arbeit; sämtliche anderen autonomen Aufgaben bleiben pausiert.

**Qualifizierte Umgebungen:**

| Engine | Build | Edition | Plattform | Kompatibilitätsstufe | Instanzprofil | Server-Ad-hoc-Option |
|---|---|---|---|---:|---|---:|
| 2025 | 17.0.4075.5 | Enterprise Developer Edition (64-bit) | Linux/Docker | 170 | 2 Kerne, 3 GiB | 0 |
| 2019 | 15.0.4480.2 | Developer Edition (64-bit) | Linux/Docker | 150 | 2 Kerne, 3 GiB | 0 |
| 2022 | 16.0.4265.3 | Developer Edition (64-bit) | Linux/Docker | 160 | 2 Kerne, 3 GiB | 0 |

Die eigene Datenbankoption OPTIMIZE_FOR_AD_HOC_WORKLOADS war jeweils OFF.

**Bindung der lokal qualifizierten SQL-Quellen (SHA-256, kryptografischer Inhaltsfingerabdruck):**

- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/00_Preflight.sql`: `77a66a4e7c828775d35ec13ba5cada156f40c7d0b8ba565343f1d4068150a644`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/10_Setup.sql`: `cef348d6f6c3b249250cbd9fe844146a9d03760d876a437c2a09fb82372a9bbe`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/20_Baseline.sql`: `ccb885e6f0dac671cc54843387ee40d9a0e24926bbfe33d7ffc71913ab353c0c`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/30_Demonstration.sql`: `1748dde008753f8cf5b9ad820bd2e5175cc5f460711643c71812dd4ee7f895a6`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/40_Observation.sql`: `5401fc3609fd3f56f80193bfc33f024ca82854b9e423fcccc309984dffda45b9`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/50_Mitigation.sql`: `f751138f8f69f0510add0599daf268589cba8b2bd6ec60669776943c4c3f4042`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/60_Comparison.sql`: `0fea16935c6b8a1691301605a337f0bda6ce575cd27a50bb4072c8740ecd80c6`
- `Demos/04_Optimizer_Statistics_Plans/OPT-007_Adhoc_Plan_Cache/90_Cleanup.sql`: `66d7d61ada2e36c560314d1220a1a7b98275d0392393156bbc14edd31cd4420f`

###### Historischer begrenzter Entwurf: Ad-hoc-Cachebelegung und Parameterisierung

HISTORICAL_DESIGN – Entwurfsstand vor dem Umsetzungsauftrag vom 23. Oktober 2026; aktueller begrenzter Implementierungs- und Prüfstand in implementation_record.

Der folgende Entwurf beschreibt den Stand vor dem Umsetzungsauftrag. Aussagen zu noch nicht ausgeführten Tests und späterer Implementierung sind historisch; der aktuelle begrenzte Nachweis steht oben.

**Ursprünglicher Entwurfsstatus:** DESIGNED – Abfrageform und Ergebnisvertrag quellenbasiert präzisiert; keine Implementierung, keine ausgeführten OPT-007-Demotests und kein Laufzeitnachweis.


**Lernziel:** Eingebettete Literalwerte im Batchtext mit gebundenen Parametern vergleichen: eigene Cacheobjekte und tatsächliche Pläne, Anzahl und belegte Bytes laufgenau zuordnen und Wiederverwendung prüfen. Der Schnitt erklärt Batchtext-Wiederverwendung; er behauptet keine allgemeine Wirkung aller Literalprädikate oder einen Leistungsgewinn.

**Umfang:** Eine eigene kleine synthetische Datenbank, ein sequenzieller Workload und Beobachtung durch den vorhandenen Harness. 40 Werte werden einmal in jeweils einen Literalbatch eingebettet und einmal an denselben konstanten SELECT-Text gebunden, insgesamt höchstens 80 Nutzabfragen. Erster Nachweisschnitt ausschließlich im vorhandenen Vollplanmodus; Stubmodi bleiben gesondert offen. Diagnose von Cachebelegung und Wiederverwendung, keine Last- oder Leistungsvergleichsdemo.

**Bestehende Abdeckung:** Bestehende OPT-007-Identität für Compilation (Planübersetzung), Recompilation, Plan Reuse (Planwiederverwendung) und Ad-hoc-Cache-Pollution (unnötige Cachebelegung) verwenden. Der Schnitt deckt davon nur den begrenzten Ad-hoc-Vergleich ab. QRY-004 (optionale Filter), QRY-013 (Anwendungs-/Werkzeugkontext), OPT-009 (parametersensitive Planoptimierung) und OPT-010 (Optimierung optionaler Parameter) nicht duplizieren. Vorhandene Zuordnung CLM-032 (Cache-Schlüssel und zusätzliche Einträge) / LO-M02-07 verwenden; keine neue Kennung oder zusätzliche Benchmarkbehauptung.

**Ergänzende lesende Quellenprüfung:** SOURCE_ONLY – lesende Quellenprüfung; kein SQL-, Test- oder Laufzeitnachweis.

Stand 2026-10-23 gegen `7d67464010e8d233661f1afc86507a12fc7d76a3`. Den vorhandenen OPT-007-Plan mit Microsoft-Primärquellen zu Parametrisierung, lokalen Variablen, Cache-/Planmetadaten und Ausführungsstatistik abgeglichen. Dokumentiertes Verhalten, Konzeptinferenz und offene empirische Abnahme getrennt; der ursprüngliche Analyze-Befund bleibt unverändert.

- DOKUMENTIERT: PARAMETERIZATION SIMPLE verhindert automatische Parametrisierung nicht. Auch eine Ausnahme von FORCED genügt als Ausschlussbeweis nicht, weil SQL Server danach noch einfache Parametrisierung versuchen kann. Eine einfache WHERE-Id-Literalform und 40 Texttreffer tragen den geplanten Ausschluss deshalb nicht.
- DOKUMENTIERT: Ein Adhoc-Cacheobjekt kann nur ein Shell-Eintrag mit Verweis auf einen automatisch parameterisierten Plan sein. objtype Adhoc und cacheobjtype Compiled Plan allein sind kein positiver Vollplannachweis; der konkrete SELECT-Planinhalt und mögliche zusätzliche Templates müssen berücksichtigt werden.
- DOKUMENTIERT: Ein Compiled Plan Stub (kleiner Cacheeintrag) besitzt keinen auslesbaren Ausführungsplan. Der erste Nachweisschnitt verwendet deshalb einen vorhandenen Vollplanmodus. Stubklassifikation und eine spätere reale Stubabnahme bleiben gesondert, ohne automatische Konfigurationsumschaltung.
- INFERENZ: Beim unten definierten Literalbatch steht der veränderliche Wert in DECLARE; der SELECT verwendet ausschließlich die lokale Variable. Das vermeidet einen zur Ersetzung angebotenen variierenden Literalwert im SELECT. Daraus folgt ein begründeter Konzeptkandidat für unterschiedliche Batchtexte, keine bereits bestätigte Anzahl gecachter Pläne.
- DOKUMENTIERT / GRENZE: Lokale Variablen und gebundene Parameter können dem Optimierer unterschiedliche Informationen liefern. Deshalb werden gleiche fachliche Ergebnisse und tatsächliche Cachebelegung verglichen, keine identische physische Planform oder allgemeine Speicher-/Laufzeitverbesserung zugesagt. usecounts ist kein verlässlicher Ausführungszähler.

**Konkrete Abfrageform als Konzept:** Konzeptvorlage für eine spätere Umsetzung; Platzhalter sind nicht ausführbar, keine SQL-Datei oder Demoimplementierung.

Vorgesehen ist dbo.CacheProbe mit Id int NOT NULL als eindeutigem Primärschlüssel und Payload int NOT NULL. Genau die Zeilen (k, k) für k = 1 bis 40; keine weiteren Nutzdaten oder Ergebniszeilen.

Literalbatch mit eingebettetem Wert (Platzhalter, nicht ausführen):

```sql
/* OPT-007:<RUN_TOKEN>:LITERAL */
DECLARE @Key int = <KEY>;
SELECT Id, Payload
FROM dbo.CacheProbe
WHERE Id = @Key;
```

Konstanter Parametertext, getrennte Bindung mit `@Key int`:

```sql
/* OPT-007:<RUN_TOKEN>:PARAMETER */
SELECT Id, Payload
FROM dbo.CacheProbe
WHERE Id = @Key;
```

Im Literalarm ausschließlich <KEY> durch den intern erzeugten Ganzzahlwert 1 bis 40 ersetzen; der normalisierte Lauftoken und der Armkommentar bleiben konstant. Den gesamten nicht parameterisierten Literalbatch in der eigenen Zieldatenbank ausführen. Im Parameterarm den konstanten Statementtext per sp_executesql mit unveränderter Deklaration @Key int und getrennt gebundenem Wert 1 bis 40 ausführen. Die lokale DECLARE-Anweisung gehört ausschließlich zum Literalbatch.

Der Lauftoken ist nach dem vollständigen Framework-Rohwertvertrag geprüft, normalisiert und für beide Arme derselbe. Beide vollständigen SQL-Vorlagen sind fest; gleiche Sessioneinstellungen, Datenbank und Datentypen. Bei der Prepared-Textprüfung die erwartete Parameterdeklaration berücksichtigen. Keine wechselnden Kommentare je Schlüssel, keine Textkürzung, keine permissive LIKE-Zuordnung und kein OPTION (RECOMPILE).

**Vor einer Umsetzung zu schließen:**

- LAB-PLAN-003 am registrierten Analyze-Stand 6e557726a07ce7d389a36083c7e82d214b20822f bleibt eine Ideenquelle mit Nachweislücken. Der unten definierte Schulungsschnitt verwendet eingebettete Batchwerte und gebundene Parameter; weder Runner noch gemeinsame Planbereinigung übernehmen.
- Die Konzeptvorlagen und den positiven Nicht-Shell-/Nicht-Template-Nachweis vor dem ersten späteren SQL-Lauf auf die konkrete Implementierung abbilden und unabhängig prüfen. Unterschiedliche Batchtexte sind kein eigener Nachweis fehlender automatischer Parametrisierung. Die erwartete Planmenge ist erst je Zielversion zu qualifizieren; bei Shells, Zusatztemplates oder verlorener Zuordnung stoppen statt die Abfragezahl oder den Infrastrukturumfang auszuweiten.
- Für den ersten Nachweisschnitt serverweites optimize for ad hoc workloads = 0 und datenbankbezogenes OPTIMIZE_FOR_AD_HOC_WORKLOADS = OFF verlangen; PARAMETERIZATION und alle relevanten Cache-/Parameter- und SET-Einstellungen aufnehmen. Keine Option umschalten, keine Cacheleerung. Bereits vor Setup erkennbare Abweichung als SKIP_CONFIGURATION; erst nach Neuanlage feststellbarer unerwarteter Zielzustand als FAIL_STATE mit Cleanup. Stubmodi bleiben außerhalb dieser ersten empirischen Abnahme.
- Quellen-/Vertragsreview von Cachefilter, flüchtigen Handles, Transaktions-/Sitzungsgrenzen, Eigentum, Eingaben, Ressourcen- und Cleanupbudgets vor dem ersten späteren SQL-Lauf abschließen. Den vorhandenen Frameworkpfad mit FWK-011 (Ergebnisnormalisierung) und FWK-012 (Status-, Fehler- und Skip-Vertrag) verwenden.

**Voraussetzungen und Versionsumfang:**

- Geplante Engine-/Datenbankpaare: SQL Server 2019 mit Compatibility Level 150, SQL Server 2022 mit 160 und SQL Server 2025 mit 170. Compatibility Level bezeichnet die Datenbank-Kompatibilitätsstufe. Erste empirische Qualifikation ausschließlich Developer unter Linux/Docker; Build, Edition, Plattform und tatsächlich vorhandene Konfigurationsmodi getrennt dokumentieren. Windows und andere Editionen bleiben offen.
- Der Login benötigt CREATE ANY DATABASE sowie Kontrolle über die eigene Datenbank und deren synthetische Objekte. Für die Diagnosesichten unter SQL Server 2019 VIEW SERVER STATE, ab SQL Server 2022 VIEW SERVER PERFORMANCE STATE prüfen. Fehlende Voraussetzungen müssen vor Setup zu einem passenden bestehenden Skip führen; ein später fehlender Pflichtnachweis bleibt ein Fehler.
- Vorhandenen manifestbasierten T-SQL-Harness (Transact-SQL; SQL-Server-Skriptsprache) und sqlcmd (Microsoft-Kommandozeilenwerkzeug) nutzen. Kennwörter bei SQL-Authentifizierung ausschließlich über SQLCMDPASSWORD, keine Verbindungsdaten in Sessionmanifesten oder Quelltexten. Keine neue Lab-Infrastruktur und keine Abhängigkeit von der Umsetzung einer anderen Demo.
- Zusätzliche Vorbedingung des ersten Schnitts: serverweite Ad-hoc-Option 0 und datenbankbezogene OPTIMIZE_FOR_AD_HOC_WORKLOADS-Option OFF, ohne Umschaltung. sys.dm_exec_query_plan (Diagnosefunktion für den Planinhalt) benötigt die schon genannten serverweiten Diagnoserechte. Vorhandene Konfigurationen werden aufgenommen, nicht aus Defaults abgeleitet; unbekannte Voraussetzungen ergeben keine Freigabe.

**Geplanter Ablauf:**

- Preflight: eigene isolierte Wegwerfinstanz, Version/Kompatibilitätsstufe, Rechte, Tool und Ressourcen bestätigen. Vollständige rohe Demo-/Lauf-/Datenbankwerte vor begrenzten Typen prüfen. Fehlende Rechte als SKIP_PERMISSION, vorher erkennbare ungeeignete Konfiguration als SKIP_CONFIGURATION vor Setup ausweisen. Server-Ad-hoc-Option sowie bei vorhandener Zieldatenbank deren Datenbankoption prüfen; keine Einstellungen automatisch korrigieren.
- Setup: die eigene vollständig markierte Datenbank und dbo.CacheProbe mit den 40 eindeutigen Zeilen (k, k), k = 1 bis 40, aufbauen. Nach Neuanlage die datenbankbezogene Ad-hoc-Option vor Nutzabfragen als OFF bestätigen; unerwarteter Zustand ergibt FAIL_STATE und Cleanup, keinen nachträglichen Skip. Daten, Schema, Statistiken, Sessioneinstellungen und Datentypen bleiben während beider Arme gleich. Keine Plan-Guides, Forcing-, Recompile- oder Warm-up-Eingriffe zwischen Messpunkten.
- Baseline: für beide Arme anhand frischem Lauftoken, Datenbankkennung und vollständiger erwarteter Abfragetexte einen leeren eigenen Cacheumfang bestätigen; unbekannte oder bereits vorhandene Einträge ergeben FAIL_STATE statt einer Cacheleerung. Messzeit und Konfigurationszustand aufnehmen.
- Literalarm: die festgelegte DECLARE-/SELECT-Batchvorlage für k = 1 bis 40 jeweils einmal ausführen. Nur der eingebettete Schlüsselwert variiert, Kommentar und Lauftoken bleiben konstant. Nach 20 und 40 abgeschlossenen SELECTs die vollständig zugeordneten Cacheobjekte und echten SELECT-Pläne aufnehmen; keine bloßen Shells oder zusätzlichen automatischen Templates als Erfolg akzeptieren.
- Parameterarm: denselben SELECT-Text 40-mal per sp_executesql mit konstanter Parameterdeklaration @Key int und getrennt gebundenen Werten 1 bis 40 ausführen. Nach 20 und 40 abgeschlossenen Aufrufen Cache- und Statementstatistik aufnehmen. Je Aufruf exakt eine Zeile mit Id = k und Payload = k verlangen; alle Ergebnismengen mit dem Literalarm abgleichen.
- Auswertung und Cleanup: Snapshotdifferenzen getrennt nach Arm, objtype und cacheobjtype darstellen. Nach fachlichem Erfolg oder Fehler markergeprüften Cleanup versuchen und die Abwesenheit der eigenen Datenbank unabhängig bestätigen. Vorher/nachher nur die tatsächlich eigene Cachemenge vergleichen; keine Aussage über freien Instanzspeicher oder allgemeinen Speicherdruck.

**Geplanter Ergebnisvertrag:**

- Cachezuordnung benötigt gleichzeitig bestätigtes Datenbankeigentum, tatsächliches dbid aus sys.dm_exec_plan_attributes, Lauftoken, Arm und vollständige exakte Abfragetexte. sys.dm_exec_sql_text(sql_handle).dbid allein genügt bei Ad-hoc-Abfragen nicht. Reine LIKE-Texttreffer, Query-Hash oder Sitzungszahl sind kein Ersatz; Beobachter-, Harness- und Wrappertexte ausschließen.
- Je plan_handle genau ein Cacheobjekt zählen und size_in_bytes einmal summieren; Attribut- und Statementjoins dürfen Werte nicht vervielfachen. Im ersten Nachweisschnitt im Literalarm Adhoc/Compiled Plan und im Parameterarm Prepared/Compiled Plan verlangen, zusätzlich für den exakten Soll-SELECT einen tatsächlichen QueryPlan mit physischem RelOp (Planoperator) nachweisen. Shelltexte ohne diesen Inhalt sowie zusätzliche automatisch erzeugte Parameter oder Templateverweise zurückweisen. Die erwartete lokale beziehungsweise gebundene Variable @Key nicht mit automatisch erzeugten Parametern verwechseln.
- Messpunkte enthalten vollständige eigene Handlemenge, Anzahl und Bytes je Typ sowie Zeitpunkt, Datenbank-/Lauf-/Armzuordnung und dokumentierten Cachekontext. Numerische Bytes sind beobachtete Belegung dieses Umfangs; Wachstum erfordert die entsprechende Baseline-/Folgedifferenz. Keine festen Bytewerte, Einsparquoten oder Laufzeitvorteile als Erfolg voraussetzen.
- Wiederverwendung im Parameterarm durch genau einen zugeordneten Prepared-Plan und denselben plan_handle, dieselbe creation_time sowie dieselbe plan_generation_num (Kompilierungsgeneration) an beiden Messpunkten belegen. Für die exakten SELECT-Statementgrenzen muss execution_count zuerst 20 und danach 40 sein, Differenz 20. usecounts weder als Ausführungszähler noch als Ausschlussbeweis für Recompile verwenden. Gelöschte, neu angelegte oder mehrdeutige Statistikzeilen erfüllen den Vertrag nicht.
- Die Cacheansichten sind flüchtige Momentaufnahmen. Verdrängung, Recompile, Kontextwechsel, NULL-Metadaten oder verlorene Zuordnung dürfen nicht als erfolgreicher Vergleich gelten. Bei erfüllten Voraussetzungen führen fehlende Pflichtbelege zu FAIL_RESULT_CONTRACT beziehungsweise FAIL_TIMEOUT; keine nachträgliche Umdeutung in einen optionalen Evidenz-Skip.
- Ergebnismenge je Schlüssel exakt (Id, Payload) = (k, k), k = 1 bis 40; damit je Arm 40 Einzelzeilen, 40 unterschiedliche Schlüssel und Summe(Payload) = 820. Zeilenzahl und Summe sind zusätzliche Invarianten, kein Ersatz für den vollständigen Wertevergleich. Baseline je Arm leer; Literal-Snapshots mit 20 beziehungsweise 40 unterschiedlichen, eindeutig den Sollbatches zugeordneten Handles, Parameter-Snapshots jeweils mit genau einem unveränderten vollständigen Plan. Pflichtbelege werden nach FWK-011 als EXACT (exakte Invarianten) mit Fehler bei fehlender Evidenz geprüft; Metadaten-/Planprüfung erfolgt vollständig vor der numerischen Ergebnisnormalisierung.

**Sicherheit und vorläufige Schutzgrenzen:**

- Vorläufig YELLOW (gelb; ausdrücklich isoliertes Labor erforderlich), eine eigene Wegwerfinstanz und ein sequenzieller Workload; kein Lasttreiber, keine parallele Flut und keine Fremddaten. Ausgangspunkt für die spätere Dockerqualifikation: zwei Prozessorkerne und 3 GiB Arbeitsspeicher; andere Plattformen/Editionen bleiben unqualifiziert.
- Harte Entwurfsobergrenzen: 40 Zeilen, 40 Literale plus 40 Parameteraufrufe, höchstens 4096 UTF-16-Bytes (Unicode-Textkodierung) je Nutzabfragetext und 128 MiB (Mebibyte) je Datenbankdatei. Für beobachtete eigene Cacheobjekte gilt 16 MiB als Abbruchschwelle, keine garantierte Spitzenspeichergrenze. Zeitbudgets höchstens 120 Sekunden regulär und separat 30 Sekunden Cleanup; jeder Einzelaufruf beziehungsweise jede Pollingphase höchstens 15 Sekunden und zusätzlich durch das Restbudget begrenzt. Nach jedem Nutzaufruf Restbudget und beobachtete Cachebelegung prüfen; die Messpunkte nach 20/40 Aufrufen ersetzen diese Schutzprüfung nicht. Eine Überschreitung stoppt die Folgeabfragen, sie vergrößert den Umfang nicht automatisch. Das sind Schutzgrenzen, keine gemessenen Laufzeiten oder Leistungswerte.
- Vor Wiederverwendung, Änderungen und Cleanup alle vier Marker SQLPERF.Project, SQLPERF.ContractVersion, SQLPERF.DemoId und SQLPERF.RunToken vollständig, binär und mit exakter Länge prüfen. Kein DROP DATABASE nur anhand des Namens, kein KILL anhand einer Sitzungsnummer, keine globale oder handlebasierte Planbereinigung und kein CLEAR PROCEDURE_CACHE.
- Bei Fehler oder Timeout eigene Prozesse begrenzt beenden, gestartetes Setup über den vorhandenen Cleanupvertrag abbauen und Restzustand unabhängig prüfen. Auch nach Datenbanklöschung die zuvor vollständig gebundenen eigenen Cacheobjekte begrenzt auf Restzustände prüfen; verbleibende Objekte sichtbar als Cleanupfehler behandeln, keine globale Leerung anschließen. Bei unklarem Eigentum erhalten und Diagnose-/Wiederaufnahmebedarf ausweisen. Gescheiterte Erstmarkierung erhält den allgemeinen offenen Erhaltungsweg.
- Diagnosesichten nur im erklärten synthetischen Umfang auswerten. Keine fremden Querytexte, Plan-XML-Dateien, Exporte oder echten Diagnosedaten publizieren. Private Laufbelege und Fehlversuche erhalten; Veröffentlichung nur nach Datenschutzprüfung.

**Später benötigte Tests – noch nicht ausgeführt:**

- Statisch vor Ausführung: Eigentums- und Rohwertprüfungen, Abfrage-/Zeilen-/Text-/Cache-/Zeitgrenzen, statusgebundene Abbrüche, eindeutige Cacheaggregation sowie Ausschluss globaler Eingriffe und unzulässiger Text-/Planexporte prüfen. Keine neue generische Framework- oder Infrastrukturkomponente als Voraussetzung.
- Positive Versionsqualifikation erst nach Umsetzungsauftrag: SQL Server 2019/150, 2022/160 und 2025/170, zunächst Developer/Linux/Docker und ausschließlich im vorhandenen Vollplanmodus. Je zwei vollständige Lifecycles mit frischen Lauftokens, gleichem finalen Quellenstand, allen Pflichtphasen und eigenem Cleanup. Pro Arm die vollständigen 40 Tupel (k, k) prüfen. Literal-Snapshots 20/40 reale SELECT-Pläne; Parameter-Snapshots ein stabiler Prepared-Plan mit execution_count 20/40 und unveränderter Kompilierung. Konkrete Builds und Konfiguration protokollieren; Stubmodi bleiben unqualifiziert.
- Negative Eigentums-/Eingabefälle: fehlende, NULL-, fremde, gekürzte und verlängerte Marker; ähnliche Datenbanknamen, überlange oder Unicode-Rohwerte, Leerzeichen-/Normalisierungsgegenfälle sowie fremder Lauftoken. Vollständige Ausführung der betroffenen Datei muss vor jeder Mutation stoppen; fremde Zustands-/Sentinelaufnahmen bleiben gleich. Bestehende Setup-/Cleanup-Oracles wiederverwenden.
- Negative Evidenzfälle: gleicher Marker in fremder Datenbank/anderem Lauf, Beobachter- und Wrappertexte, NULL-dbId oder -Text, fehlende Snapshots, doppelte Joinzeilen und verfälschte Bytes zurückweisen. Zusätzlich Adhoc/Compiled-Plan-Shell ohne physischen SELECT-Plan, Stub als Vollplan, automatisch erzeugte Parameter und nicht gebundene Templates als Fehler prüfen. Bloßer usecounts-Anstieg, wechselnder Handle, geänderte creation_time/plan_generation_num, falsche Statementgrenzen oder nur eine Differenz 20 bei falschen Gesamtzählern dürfen nicht bestehen. Gleich viele Zeilen und gleiche Summe bei anderen Tupeln müssen ebenfalls scheitern.
- Konfiguration und Vergleich: ungeeigneter serverweiter Ad-hoc-Modus vor Setup muss SKIP_CONFIGURATION ergeben; unerwarteter Datenbankmodus nach Neuanlage muss mit FAIL_STATE und Cleanup stoppen. Automatische Parametrisierung, wechselnde Sessioneinstellungen oder Parameterdeklarationen, Recompile, Cacheverdrängung und fehlende Metadaten sind negative Gegenfälle. Sowohl höhere als auch niedrigere gemessene Bytewerte dürfen keinen Leistungsclaim erzeugen. Stub-/Shell-Unterscheidung zunächst synthetisch prüfen; ein realer Stubvergleich benötigt einen gesonderten Auftrag.
- Abbruch/Recovery: ungültige oder ausgeschöpfte Budgets, versuchter 41. Aufruf je Arm, Text-/Cachegrößenüberschreitung und künstlicher Timeout während eines aktiven eigenen Aufrufs müssen weitere Arbeit stoppen. Setup-/Cleanup-Idempotenz, getrennte ursprüngliche Fehler und dominante FAIL_CLEANUP-Auswertung sowie unabhängige Datenbank-/Containerabwesenheit prüfen. Unklares Eigentum bleibt erhalten; keine unbegründete Erfolgs- oder Restlosigkeitsmeldung.

**Abnahmekriterien:**

- Planungsabnahme jetzt: Quellenbefunde, konkrete Konzeptvorlagen, abgegrenzter Vollplanmodus, Eigentums-/Ressourcen-/Cleanupgrenzen sowie positive und negative Ergebnisbedingungen sind bei TSK-016 nachvollziehbar. Nur statische Dokumentations-/Registry- und Integrationsprüfungen; keine ausführbaren OPT-007-Artefakte, keine Demotests und keine SQL-/Lab-Läufe.
- Spätere fachliche Abnahme: je Schlüssel exakt (k, k), insgesamt 40 Zeilen, 40 unterschiedliche Schlüssel und Summe 820 je Arm. Literalarm mit 20/40 eindeutig zugeordneten vollständigen SELECT-Plänen, Parameterarm mit genau einem unveränderten vollständigen Prepared-Plan und execution_count 20/40 bei gleicher creation_time/plan_generation_num. Shells, Stubs, zusätzliche automatische Parameter/Templates, verlorene Zuordnung oder fehlende Pflichtbelege schließen diese erste Abnahme aus. Cachebytes werden korrekt gemessen, ohne feste Einsparquote oder Richtungsbehauptung.
- Spätere Sicherheits-/Versionsabnahme: unabhängiger Quellen-/Ergebnisreview ohne offene priorisierte Befunde, zwei erfolgreiche vollständige Lifecycles je qualifizierter Version im festgelegten Vollplanmodus, relevante negative Eingabe-/Eigentums-/Evidenz-/Abbruchfälle und unabhängig bestätigter Cleanup. Unqualifizierte Stub-, Windows- und Editionsumfänge bleiben ausdrücklich offen.
- Späterer Dokumentations-/Integrationsabschluss: Demo-Einstieg, Katalog, Ausführungsleitfaden, Demo-README, Interpretation/Abbruch und bestehende Lernzielzuordnung konsistent aktualisieren; Registry und abgeleitete Backlogansicht fortführen. Aktuelle relevante PR-/Main-Gates und vollständige Übernahme per Pull Request (Änderungsantrag) nach origin/main sowie eigene Branch-/Containerbereinigung belegen. Keine pauschale Laufzeit-, Speicherersparnis- oder Modulfreigabe.

**Quellenbindung:** Ursprünglicher Plan am 2026-10-23 gegen Schulungsstand `8ebd12b48b338f06bddee9dbbc6bda3173a996bc`; Ergänzung gegen `7d67464010e8d233661f1afc86507a12fc7d76a3`. Ursprüngliche Quellenbefunde unverändert.

- Registrierte Analyze-Sichtung LAB-PLAN-003 einschließlich Setup, Observe und Cleanup, Stand `6e557726a07ce7d389a36083c7e82d214b20822f`; siehe den Quellenbefund oben.
- [Schulungs-Demovertrag: Sicherheit, Eigentum, Budgets und Ergebnisse](../.ai/DEMO_CONTRACT.md), Stand `8ebd12b48b338f06bddee9dbbc6bda3173a996bc`.
- [Vorhandene Curriculumzuordnung: Cache-Schlüssel und zusätzliche Einträge](../Documentation/Curriculum/TRACEABILITY_MATRIX.md), Stand `8ebd12b48b338f06bddee9dbbc6bda3173a996bc`.
- [Microsoft: Cacheobjekttypen, Bytes und Grenzen von usecounts](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-cached-plans-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: vollständiger Plan, Planstub und bestehende Konfiguration](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/optimize-for-ad-hoc-workloads-server-configuration-option?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: automatische Parametrisierung und Planwiederverwendung](https://learn.microsoft.com/en-us/sql/relational-databases/query-processing-architecture-guide?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: tatsächlicher Datenbank- und SET-Kontext eines Plans](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-plan-attributes-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: Ad-hoc-Datenbankzuordnung und vollständiger Abfragetext](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-sql-text-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: Ausführungszähler, Kompilierungszeit und Lebensdauer der Statistik](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: konstante Abfragetexte und Parameterdeklarationen mit sp_executesql](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-executesql-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: lokale Variablen im Batch](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: SIMPLE kann parameterisieren; Plan-Guide-Grenze](https://learn.microsoft.com/en-us/sql/relational-databases/performance/specify-query-parameterization-behavior-by-using-plan-guides?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: Shelltexte und tatsächlicher Planinhalt](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.
- [Microsoft: datenbankbezogener Ad-hoc-Modus ab SQL Server 2019](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-scoped-configuration-transact-sql?view=sql-server-ver17), gelesen am 2026-10-23.

Aufwand weiterhin **M (mittel), vorläufig**. Konzept und Quelleninferenz belegen weder eine ausführbare Demo noch die erwartete Planmenge oder Laufzeitabnahme.

##### 3. DGN-004 – Erfolgreiches und fehlgeschlagenes Plan Forcing

**P2 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand M – vorläufig.**

**Planungsentscheidung:** QueryCompilationReplay und Gegenkennzeichnung weiter quellenbasiert abgegrenzt: keine freigegebene Wertetabelle, gepinnter Konflikt zwischen Katalog und Abschaltbeispiel. Kontrollzustand und beobachtete Deaktivierung getrennt; Hint-Gegenkontrolle liegt außerhalb des unveränderten Textprotokolls. Methodengates für beide Builds bleiben offen. P2, Probenplan und ursprünglicher Demoschnitt unverändert; keine Umsetzung oder Laufzeitabnahme.

**Begründung:** Erfolgreiche und fehlgeschlagene Planerzwingung ergänzen die vorhandene Query-Store-Grundlage mit einem klaren Diagnoseziel. Die Quelle belegt weder tatsächliche Planverwendung noch den beabsichtigten Fehler; ihr Erfolgskriterium darf nicht übernommen werden.

**Abhängigkeiten:**

- DGN-003 (Query Store; persistente Abfrage- und Planhistorie) fachlich voraussetzen.
- Einen kontrollierten Forcing-Fehler samt Versionsgrenzen, tatsächlich verwendetem Plan, Fehlergrund und vollständiger Rücknahme entwerfen; keine technische Abhängigkeit von CON-005 (Schemasperren) oder OPT-007 (Ad-hoc-Plancache).

**Wiederaufnahmebedingung:** Vor Probe-Umsetzung die Gates im query_compilation_replay_counter_review_result unabhängig quellenbelegt klären: positive Markerbedeutung, belastbare Gegenkennzeichnung, frische Kompilierungs-/Ausführungsbindung und Erhalt des Quellenkonflikts. Kombinierte Zuordnung und Transport freigeben; erst danach neuer ausdrücklicher Umsetzungs-/Laufauftrag im unveränderten Budget. Hint-Gegenkontrolle nur nach gesonderter methodischer Planung/Freigabe; übrige Verarbeitung pausiert.

**Quellen:** `LAB-QS-002` (Forced and failed forced plan; erfolgreiche und gescheiterte Planerzwingung).

**Abgrenzung:** DGN-004 ist bereits für Plan Forcing (Erzwingen eines Plans), Query Store Hints und sichere Rücknahme geplant; DGN-003 liefert die vorhandene Query-Store-Grundlage.

**Weiterer Prüfauftrag:** Vorbedingungen und Versionsgrenzen des gewählten Forcing-Fehlers sowie tatsächlichen Erfolgs-/Fehlernachweis im Verify-Vertrag prüfen.

**Statischer Quellenbefund:** Stand `fd18d829904b6b1631f385cfaad340ca3c72bcbb`, erfasst am 2026-10-23. LAB-QS-002 aktiviert Query Store (persistente Abfragehistorie), erzeugt Abfrageausführungen und markiert anschließend einen erfassten Plan mit sp_query_store_force_plan zur Erzwingung. Das Runbook startet keine Worker; Observe.sql verlangt lediglich mindestens einen Plan der synthetischen Prozedur mit is_forced_plan = 1.

- Trotz des Titels Forced and failed forced plan fehlen nach dem Forcing eine erneute Ausführung der Zielabfrage, ein kontrolliert ausgelöster Forcing-Fehler, dessen Beobachtung und eine ausdrückliche Rücknahme mit sp_query_store_unforce_plan. Die Datenbanklöschung ersetzt keine Lehrsequenz zur sicheren Rücknahme.
- is_forced_plan kennzeichnet die angeforderte Planerzwingung und garantiert keine erfolgreiche Planverwendung. Observe.sql prüft weder die tatsächliche Ausführung nach dem Forcing noch force_failure_count (Anzahl fehlgeschlagener Erzwingungsversuche) oder last_force_failure_reason_desc (letzter Fehlergrund). Der Analyzer USP_QueryStoreForcedPlans stellt diese Felder bereit; der Szenariovertrag wertet sie nicht als fachliche Abnahme aus.
- Die Szenariodefinition nennt zusätzlich USP_QueryStoreHints und USP_QueryStoreAnalysis, der Aufrufpfad führt jedoch nur den PrimaryAnalyzer USP_QueryStoreForcedPlans aus. Daraus folgt kein Nachweis für Query Store Hints (gespeicherte Abfragehinweise) oder fehlgeschlagenes Forcing. Der bestehende Schulungsplan umfasst Force, Failure, Fallback und Unforce bereits ausdrücklich.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:521](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Setup.sql:549](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Observe.sql:472](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Observe.sql:624](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-QS-002/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-QS-002/runbook.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-QS-002/scenario.json:36](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-QS-002/scenario.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Code/05_QueryStore/060_USP_QueryStoreForcedPlans.sql:54](https://api.github.com/repositories/1302553964/contents/Code/05_QueryStore/060_USP_QueryStoreForcedPlans.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb).

Abgleich mit der Schulung: [Bestehender DGN-004-Planungsschnitt: Force, Failure und Unforce](https://github.com/gecompat/SQL_PerformanceSchulung/blob/0ea16ae8c3340ee37fc036e943017f938304c817/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L89), [Abgrenzung zur vorhandenen Query-Store-Historie](https://github.com/gecompat/SQL_PerformanceSchulung/blob/0ea16ae8c3340ee37fc036e943017f938304c817/Demos/07_Query_Store_Extended_Events/DGN-003_Query_Store_History/README.md#L25).

**Vor einer späteren Umsetzung erforderlich:**

- Im vorhandenen DGN-004-Planungsschnitt bleiben; DGN-003 (Query-Store-Historie) als Grundlage nutzen und keine zweite allgemeine Query-Store-Demo anlegen. Eine tatsächlich ausgeführte Zielabfrage nach dem Forcing mit zugeordneten Query-/Plan-Kennungen und passendem Beobachtungsfenster belegen.
- Für die spätere Fehlersequenz eine Planvoraussetzung kontrolliert entziehen und eine erneute Kompilierung mit anschließender Ausführung auslösen. Änderung des Fehlerzählers, konkreten Fehlergrund und beobachtete Ersatzplanung (Fallback) prüfen; Voraussetzungen und zulässige Abweichungen je unterstützter Version festlegen.
- Forcing und sonstige Zustandsänderungen ausdrücklich zurücknehmen und die Rücknahme prüfen; markergebundenes Cleanup erhalten. SQL Server 2019, 2022 und 2025 getrennt betrachten; Query Store Hints nur als Zusatzpfad ab SQL Server 2022 behandeln. Detailquellen vor einem späteren Design im regulären Quellenprozess registrieren.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Forcing-Status und Fehlergründe](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17), [Microsoft: Planerzwingung und Ersatzplanung](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver17), [Microsoft: Query Store Hints ab SQL Server 2022](https://learn.microsoft.com/en-us/sql/relational-databases/performance/query-store-hints?view=sql-server-ver17).

**Spätere Abnahme:**

- Erfolgreiches Forcing und begründet fehlgeschlagenes Forcing anhand des tatsächlichen Status und Fehlergrundes unterscheiden.
- Forcing und sonstige Zustandsänderungen rücknehmbar halten; keine zweite allgemeine Query-Store-Demo.

###### Lesende Planprüfung vom 24. Oktober 2026

**Status:** READ_ONLY_REVIEW_WITH_OPEN_GATES – Quellenprüfung und Herleitung; keine Implementierung, ausgeführten Tests, SQL-/Lab-Läufe oder Laufzeitabnahme.

**Basis:** `c9c75cefb30fc82aec33f67d9589670a877dd76b`. Den über PR314 integrierten Entwurf gegen vorhandene Framework-/Aufrufquellen und aktuelle Microsoft-Primärdokumentation gelesen. Der ursprüngliche Analyze-Befund bleibt unverändert. Dokumentierte Eigenschaften, statische Pfadbefunde, Designherleitung und spätere empirische Prüfung getrennt.

- Abfrageidentität: dieselbe parameterlose Prozedur mit unverändertem SELECT und Sitzungskontext beibehalten. Die dokumentierte datenbankweite Forced Parameterization (erzwungene Parametrisierung) nimmt Prozedurinhalte aus. Daraus folgt keine pauschale Garantie für jede Parametrisierungsdarstellung. DROP/CREATE der Prozedur erzeugt laut Query-Store-Dokumentation eine neue Query-Zuordnung und ist zwischen den Phasen ungeeignet.
- Planverwendung: sp_query_store_force_plan kann einen gleichen oder ähnlichen resultierenden Plan liefern. Erzwungenes Ziel und tatsächlich ausgeführter Plan erhalten getrennte Kennungen im Nachweis; weder identische Plan-ID noch Query-/Plan-Hash allein voraussetzen. Tatsächlicher Plan, vollständige Tupel und neue Ausführungszähler müssen demselben Aufruf zugeordnet sein.
- Erfassung: SET STATISTICS XML liefert tatsächliche Ausführungsinformationen. Der unveränderte lokale Aufrufpfad verwendet -W und -w 65535, setzt aber keine eigene Großtextanzeigegrenze. sqlcmd begrenzt große Text-/XML-Werte standardmäßig auf 256 Zeichen; -w ändert nur die Zeilenbreite. -W ist mit -y/-Y nicht kombinierbar, und der vorhandene Containerproxy akzeptiert -y derzeit nicht. Statische Nachweislücke, kein ausgeführter Trunkierungsfehler.
- Planattribute: Die veröffentlichten Showplan-Schemata für 2019/2022 führen UsePlan als optionales boolesches Attribut. Das Schema allein belegt weder seine alleinige Eignung als Query-Store-Erzwingungsnachweis noch die tatsächliche Ausgabe auf jedem Build. Ein 2022-RTM-Schema ist keine vollständige Versionsgarantie für 2025; RTM bedeutet Erstveröffentlichungsstand.
- Dokumentationskonflikt ab 2022: Die Katalogbeschreibung von is_optimized_plan_forcing_disabled ordnet 0 der Deaktivierung zu; Beispiel D der Optimierungsbeschreibung verwendet dafür 1. Die Force-Prozedurreferenz nennt als drittes Argument disable_optimized_plan_forcing und danach replica_group_id; Beispiel C der Optimierungsbeschreibung fordert replica_group_id an dritter Stelle und beschreibt es als zusätzlich erforderlich. Daraus wird keine ungeprüfte gemeinsame Aufruf- oder Flagvorlage abgeleitet.
- Fehlervertrag: 8712/NO_INDEX bezeichnet den fehlenden Index. force_failure_count steigt bei fehlgeschlagener Kompilierung, nicht bei jeder Ausführung, und wird beim Wechsel von ungezwungen zu erzwungen zurückgesetzt. Zählerzuwachs und letzter Grund müssen deshalb im eigenen neuen Beobachtungsfenster zusammen mit erfolgreicher tatsächlicher Ersatzplanung belegt werden. Die konkrete Reproduktion mit 1000 Zeilen und sechs Aufrufen ist weiterhin unbestätigt.

**Gelesene Projektquellen:**

- [Tests/Runtime/execution_target.py:47](https://github.com/gecompat/SQL_PerformanceSchulung/blob/c9c75cefb30fc82aec33f67d9589670a877dd76b/Tests/Runtime/execution_target.py#L47): Feste sqlcmd-Ausgabeoptionen; run_sql liefert Standardausgabe als Text.
- [Tests/Runtime/docker_sqlcmd_proxy.py:18](https://github.com/gecompat/SQL_PerformanceSchulung/blob/c9c75cefb30fc82aec33f67d9589670a877dd76b/Tests/Runtime/docker_sqlcmd_proxy.py#L18): Akzeptierte Proxyargumente enthalten -w und -W, aber kein -y/-Y.
- [Demos/00_Framework/Contracts/FWK-005_Plan_Statistics_Evidence_Contract.md:22](https://github.com/gecompat/SQL_PerformanceSchulung/blob/c9c75cefb30fc82aec33f67d9589670a877dd76b/Demos/00_Framework/Contracts/FWK-005_Plan_Statistics_Evidence_Contract.md#L22): Tatsächlichen Ausführungsplan, gespeicherten Plan und Exportgrenzen unterscheiden.
- [Demos/00_Framework/Templates/40_Plan_Statistics_Evidence.sql:162](https://github.com/gecompat/SQL_PerformanceSchulung/blob/c9c75cefb30fc82aec33f67d9589670a877dd76b/Demos/00_Framework/Templates/40_Plan_Statistics_Evidence.sql#L162): STATISTICS-XML-Prinzip; die Referenzabfrage mit OPTION RECOMPILE nicht als DGN-004-Abfrage übernehmen.

Primärquellen, gelesen am 2026-10-24; Registrierung und Aussagegrenzen im [bestehenden Quellenregister](../Documentation/Research/SOURCE_REGISTER.md#dgn-004--detailverweise-zum-bestehenden-query-store-quellenumfang-src-027):

- [SRC-001: Parametrisierung von Prozedurinhalten](https://learn.microsoft.com/en-us/sql/relational-databases/query-processing-architecture-guide?view=sql-server-ver17)
- [SRC-027: Query-Store-Identität und Schemaänderungen](https://learn.microsoft.com/en-us/sql/relational-databases/performance/best-practice-with-the-query-store?view=sql-server-ver17)
- [Query-Store-Abfragezuordnung](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver17)
- [Sitzungskontext](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-context-settings-transact-sql?view=sql-server-ver17)
- [SRC-031: tatsächliche Planerfassung](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-statistics-xml-transact-sql?view=sql-server-ver17)
- [sqlcmd-Ausgabegrenzen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17)
- [Showplan-Schema 2019](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2019/showplanxml.xsd)
- [Showplan-Schema 2022](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd)
- [Force-Prozedurreferenz](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver16)
- [Katalogbeschreibung und Fehlerzähler](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17)
- [Optimierte Planerzwingung, Beispiele C/D](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16)
- [Aggregierte Ausführungsstatistik](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17)

###### Engerer Erfassungsentwurf und offenes Versionsgate

Historischer Quellenstand vor der Versionsdiagnose; seine Anzeigeherleitung ist durch die folgenden Clientbefunde überholt.

**Stand:** 2026-10-24; Basis `5c0e5128293f7b7591adcbd3de31922fd8f007e4`. **Status:** READ_ONLY_WITH_OPEN_VERSION_GATE – ergänzende Quellenprüfung; engerer Erfassungsentwurf hergeleitet, keine Implementierung, ausgeführten Demotests oder Laufzeitfreigabe.

Bestehenden Plan und Prozessquellen lesend geprüft; veröffentlichte Microsoft-Systemreferenzen nur als ZIP-Archive (Archivformat) und XML-Text (strukturiertes Textformat) im Arbeitsspeicher gelesen, ohne Installation, Ausführung oder SQL-Verbindung. Der ursprüngliche Analyze-Befund und die frühere lesende Planprüfung bleiben unverändert. Primärquellen, Herleitung und fehlende Runtime-Evidenz getrennt.

- Erfassung: ein engerer erster Schnitt ist aus den sqlcmd-Ausgabeoptionen herleitbar: feste Anzeigegrenze -y 32768, Zeilenbreite -w 65535, kein -W und keine Entfernung/Ersetzung von Steuerzeichen. Der akzeptierte vollständige Plan bleibt strikt unter 32.768 UTF-8-Bytes. Diese zusätzliche Bytegrenze liegt unter der Anzeigegrenze und der früher vorgesehenen 256-KiB-Planobergrenze; tatsächliche Clientdarstellung und Plangröße sind nicht gemessen.
- Der vorhandene Ausführungs-/Prozesspfad puffert die Ausgabe vollständig und verwendet errors="replace". Ein eigener begrenzter Erfassungspfad muss deshalb Rohbytes während des Lesens begrenzen, strikt dekodieren, sämtliche Ergebnismengen erfassen und bei Fehler den eigenen Aufruf samt Cleanup (Aufräumen) beenden. Die bisherige -W/-w-Argumentliste und der Proxy werden dadurch nicht als bereits geeignet ausgegeben.
- Die veröffentlichten Systemreferenzpakete Microsoft.SqlServer.Dacpacs.Master 160.2.8 und 170.0.4 führen sp_query_store_force_plan sowie sp_query_store_unforce_plan als SqlExtendedProcedure ohne Parameterliste. is_optimized_plan_forcing_disabled ist nur als SqlComputedColumn ohne Bedeutungsdefinition enthalten. Die Pakete belegen die Schemaelemente, weder Argumentreihenfolge und Standardwerte noch Flagsemantik oder Verhalten eines laufenden Zielbuilds. Fehlende Parameterdefinitionen im Referenzmodell beweisen keine fehlenden Serverargumente.
- Die bekannten Widersprüche zwischen Force-Prozedurreferenz und Optimierungsbeispielen bleiben bestehen. Auch die zusätzlich gelesenen historischen Dokumentstände enthalten keine eindeutige gemeinsame Aufruf-/Flagvorlage. Ein altes Beispiel oder eine benannte, aber semantisch ungeklärte Statusspalte schließt das Versionsgate nicht.

**Erfassungsgate:** METHOD/INFERENCE (Methodik beziehungsweise Herleitung): enger Erfassungsentwurf ausgewählt. Technische Umsetzung, unabhängiger Quellen-/Ergebnisreview und spätere Laufzeitqualifikation des Adapters bleiben ausstehend.

**Versionsgate:** OPEN / REVIEW_REQUIRED (offen; erneute Quellenprüfung erforderlich): für 2022/2025 fehlen weiterhin belastbare buildbezogene Aufrufsignatur, Interpretation der Statusspalte und Nachweis der tatsächlich deaktivierten optimierten Planerzwingung am eigenen Plan.

**Gelesene Projektquellen:**

- [Demos/00_Framework/Tools/sqlcmd_process.py:241](https://github.com/gecompat/SQL_PerformanceSchulung/blob/5c0e5128293f7b7591adcbd3de31922fd8f007e4/Demos/00_Framework/Tools/sqlcmd_process.py#L241): Zeichenersetzung im bestehenden Prozessstart.
- [Demos/00_Framework/Tools/sqlcmd_process.py:249](https://github.com/gecompat/SQL_PerformanceSchulung/blob/5c0e5128293f7b7591adcbd3de31922fd8f007e4/Demos/00_Framework/Tools/sqlcmd_process.py#L249): collect_process sammelt Ausgabe über communicate; bestehender Timeoutpfad ist keine Bytebegrenzung.
- [Tests/Runtime/execution_target.py:47](https://github.com/gecompat/SQL_PerformanceSchulung/blob/5c0e5128293f7b7591adcbd3de31922fd8f007e4/Tests/Runtime/execution_target.py#L47): Bestehende Standardargumente mit -W/-w; getrennten Erfassungsmodus planen.
- [Tests/Runtime/docker_sqlcmd_proxy.py:18](https://github.com/gecompat/SQL_PerformanceSchulung/blob/5c0e5128293f7b7591adcbd3de31922fd8f007e4/Tests/Runtime/docker_sqlcmd_proxy.py#L18): Proxyargumentliste unterstützt -y derzeit nicht; keine pauschale Änderung der allgemeinen Ausgabepfade.

Gelesen: tools/master.dacpac und dessen model.xml. DACPAC (Data-tier Application Package) ist ein Datenbankschema-Referenzpaket. SHA-256-Werte sind Prüfsummen der Quellenbytes; sie ersetzen keinen Funktions- oder Versionsnachweis.

- Microsoft.SqlServer.Dacpacs.Master `160.2.8`: SQL Server 2022 / Sql160DatabaseSchemaProvider; [Paketquelle](https://api.nuget.org/v3-flatcontainer/microsoft.sqlserver.dacpacs.master/160.2.8/microsoft.sqlserver.dacpacs.master.160.2.8.nupkg). SHA-256 Paket `cf0bd041f52b61084cb85b52ea2283bf5fd824b43ca4b375b44f140edf974621`, Modell `2b4cd5f76f08c53f7979a3150540ce6ef1cfdf6cfa6963a3acd4d3a1707dea6c`.
- Microsoft.SqlServer.Dacpacs.Master `170.0.4`: SQL Server 2025 / Sql170DatabaseSchemaProvider; [Paketquelle](https://api.nuget.org/v3-flatcontainer/microsoft.sqlserver.dacpacs.master/170.0.4/microsoft.sqlserver.dacpacs.master.170.0.4.nupkg). SHA-256 Paket `4c5d1bcc0084fac2661a2b62251a85e24da809f03205a42830ab03ba4fcaea9e`, Modell `85b5e1e08e0ff35f55d6f7900eb9fac0550604ecba26777bf240a17ca678918a`.

Primärquellen, gelesen am 2026-10-24; Aussagegrenzen im [bestehenden Quellenregister](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-engerer-erfassungsentwurf-und-systemreferenzen-vom-24-oktober-2026):

- [sqlcmd-Ausgabeoptionen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#format-options)
- [Microsoft-Systemreferenzpakete](https://learn.microsoft.com/en-us/sql/tools/sql-database-projects/concepts/package-references?view=sql-server-ver17#system-databases)
- [Systemreferenz 2022 / 160.2.8](https://www.nuget.org/packages/Microsoft.SqlServer.Dacpacs.Master/160.2.8)
- [Systemreferenz 2025 / 170.0.4](https://www.nuget.org/packages/Microsoft.SqlServer.Dacpacs.Master/170.0.4)
- [Historischer Optimierungsbeispielstand](https://github.com/MicrosoftDocs/sql-docs/blob/3a69fbed7e840752b5a704d639931f5f82af3960/docs/relational-databases/performance/optimized-plan-forcing-query-store.md#c-force-a-plan-and-disable-optimized-plan-forcing-in-query-store)
- [Historische Force-Prozedurreferenz](https://github.com/MicrosoftDocs/sql-docs/blob/9385fea21808cf682650481315f6f4bde7c59d8e/docs/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql.md#syntax)

###### Begrenzte Versionsdiagnose und verbleibende Gates

Historischer Diagnose- und Aufnahmestand aus PR317; Laufbefunde unverändert erhalten. Die folgende lesende Hashanalyse präzisiert die Einordnung, die aktuellen Gates stehen im anschließend aktualisierten Plan.

**Stand:** 2026-10-24; Basis `2a111cda7bfcbf3218aaf0153678dbd64d3bbd40`. **Status:** EMPIRICAL_PARTIAL – begrenzte Versionsdiagnose ausgeführt; Versions- und Erfassungsgates offen. Keine Demo-Umsetzung oder Laufzeitabnahme.

Zuvor ausdrücklich autorisierte, begrenzte Diagnose auf eigenen Linux-Containern; historische Fehlversuche erhalten. Die aktuelle Dokumentationsaufnahme liest nur vorhandene lokale Evidenz und führt keine SQL-/Lab-Läufe aus. Tatsächliche Pläne, synthetische Sollresultate, Query-Store-Zähler und Rücknahme getrennt ausgewertet.

**Erfassung und erhaltene Fehlversuche:**

- C1: Der 2022-Client wies -y 65534 vor der Zielabfrage zurück und meldete den zulässigen Bereich 0 bis 8000. Daraus folgt, dass auch der frühere positive Anzeigeentwurf -y 32768 auf diesem Client nicht verwendbar ist; dieser Wert wurde nicht separat ausgeführt. C2: Der 2025-Client wies -h zusammen mit -y 0 vor der Zielabfrage zurück.
- C3: -y 0 ohne -h/-W funktionierte mit während des Lesens begrenzten Ausgabekanälen. Beim direkten 12-Tabellen-Plan fügte sqlcmd nach 65.535 Zeichen einen Umbruch innerhalb eines XML-Tokens ein; der strikte Parser lehnte das Dokument ab. Kein reparierter Plan wurde akzeptiert.
- C4/C5: Vollständige letzte tatsächliche Pläne über sys.dm_exec_query_plan_stats an genau einen Cacheeintrag der eigenen Prozedur und eine Ausführung gebunden. LAST_QUERY_PLAN_STATS nur in eigener markierter Datenbank gesichert, aktiviert und wiederhergestellt. Nummerierte 100-Byte-Stücke als 200 Hexadezimalzeichen übertragen; Bytezahl und SHA-256-Prüfsumme (256-Bit-Integritätsprüfwert), strikte UTF-16-Dekodierung, vollständiges XML (Extensible Markup Language; strukturiertes Planformat), unveränderter Statementtext und echte Laufzeitzähler geprüft.
- 18 vollständige letzte tatsächliche Plan-Dateien aus C4/C5 liegen privat vor. Grenzen des Diagnosewegs: 256 KiB (Kibibyte) Plantext in UTF-8, 2 MiB (Mebibyte) Standardausgabe und 64 KiB Fehlerausgabe. Das ist keine Umsetzung oder Qualifikation des direkten SET STATISTICS XML-Demo-Adapters; weder größere Demo-Pläne noch LAST_QUERY_PLAN_STATS werden dadurch freigegeben.

**SQL Server 2022 / 16.0.4265.3 – Developer Edition (64-bit), Linux, Compatibility Level 160:**

- Standardaufruf mit zwei Argumenten erfolgreich: Rückgabewert 0, is_forced_plan = 1, UsePlan = 1, korrektes synthetisches Ergebnis und Ausführungsdifferenz eins. Danach stoppte die zusätzliche Hashinvariante des Diagnosecodes; erweiterte Aufrufformen und Anforderungsflag nicht geprüft.
- QueryHash (Abfragehash) wechselte von 0xA3EEC222B4E92764 auf 0xD7181702D1C14CFD; der neue Wert entspricht dem unveränderten QueryPlanHash (Planhash). Vollständiger Statementtext, Statement-SQL-Handle, eigene Prozedur und Kontext blieben gleich. Ursache offen; weder als Produktfehler diagnostiziert noch durch Lockerung des Diagnosecodes übergangen.
- NOT_PROVEN – tatsächliche Abschaltung nicht belegt; kein gespeicherter Optimierungs-Replay.

**SQL Server 2025 / 17.0.4075.5 – Enterprise Developer Edition (64-bit), Linux, Compatibility Level 170:**

- Zehn Aufruffälle, sieben erfolgreiche Erzwingungen mit vollständigem zugeordnetem Plan, Sollresultat, Ausführungsdifferenz eins, UsePlan = 1 und ohne Force-Fehler; drei Aufrufe mit Rollenfehler 12463 zurückgewiesen. Bei allen zehn Fällen war is_forced_plan nach Unforce (Aufheben der Erzwingung) null.
- Vierargument-Reihenfolge query_id, plan_id, replica_group_id = 1, disable_optimized_plan_forcing = 0 beziehungsweise 1 erfolgreich; das Anforderungsflag is_optimized_plan_forcing_disabled wurde entsprechend 0 beziehungsweise 1. Der dritte benannte Deaktivierungsparameter mit Wert 1 ließ das anfänglich nullwertige Flag auf 0; Wert 0 an dritter Stelle führte zu Rollenfehler 12463 (zulässiger Rollenwert 1 bis 4). Ein angenommener Parametername beweist keine passende Positionsbedeutung.
- Nach vorherigem Flagwert 1 ließ Unforce diesen Wert bestehen. Dreiparameteraufrufe mit drittem Wert 1 hielten dann den bereits vorhandenen Wert 1; daraus darf keine durch den dritten Parameter bewirkte Deaktivierung abgeleitet werden.
- NOT_PROVEN – beobachtete Anforderung und Flagzuordnung sind kein Nachweis tatsächlich abgeschalteter Replay-Nutzung.

**Aufruffälle auf SQL Server 2025:**

Die Fallnamen sind technische Diagnosebezeichner, keine neuen Arbeitspakete. `CALL 0` bedeutet angenommener Aufruf, `CALL_ERROR 12463` Rollenfehler; die Spalte Flag bezeichnet nur die Deaktivierungsanforderung. Die vollständige Bindung bleibt im privaten Bericht.

| Fall und Aufrufform | Rückgabe | Anforderungsflag | neue Ausführungen | Force-Flag nach Unforce |
|---|---|---|---|---|
| `TWO_DEFAULT`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>` | CALL 0 | 0 | 1 | 0 |
| `NAMED_DISABLE_1`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@disable_optimized_plan_forcing=1` | CALL 0 | 0 | 1 | 0 |
| `NAMED_DISABLE_0`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@disable_optimized_plan_forcing=0` | CALL_ERROR 12463 | 0 | nicht ausgeführt | 0 |
| `DOC_ORDER_DISABLE_0`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@replica_group_id=1,@disable_optimized_plan_forcing=0` | CALL 0 | 0 | 1 | 0 |
| `REF_ORDER_DISABLE_0`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@disable_optimized_plan_forcing=0,@replica_group_id=1` | CALL_ERROR 12463 | 0 | nicht ausgeführt | 0 |
| `DOC_ORDER_DISABLE_1`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@replica_group_id=1,@disable_optimized_plan_forcing=1` | CALL 0 | 1 | 1 | 0 |
| `REF_ORDER_DISABLE_1`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@disable_optimized_plan_forcing=1,@replica_group_id=1` | CALL 0 | 1 | 1 | 0 |
| `POSITIONAL_DISABLE_1`: `<eigene Query>,<eigener Plan>,1` | CALL 0 | 1 | 1 | 0 |
| `NAMED_DISABLE_1_REPEAT`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@disable_optimized_plan_forcing=1` | CALL 0 | 1 | 1 | 0 |
| `NAMED_DISABLE_0_REPEAT`: `@query_id=<eigene Query>,@plan_id=<eigener Plan>,@disable_optimized_plan_forcing=0` | CALL_ERROR 12463 | 1 | nicht ausgeführt | 0 |

Alle Warm-ups mit abgeschlossener Planbindung meldeten has_compile_replay_script = 0 (kein gespeicherter Optimierungs-Replay); QueryCompilationReplay fehlte in den tatsächlichen Plänen. Formen mit 8/12 Primärschlüsseltabellen sowie 24 × 32 und 32 × 24 Zeilen mit nicht eindeutigen Id-/V-Indizes lieferten keine positive Replay-Ausgangslage. Die letzten beiden Formen haben jeweils exakt 768 Datenzeilen. Fehlendes optionales Replay-Merkmal beweist keine Deaktivierung.

Alle sechs eigenen Container und sämtliche eigenen Datenbanken entfernt; vorher vollständige vier Eigentumsmarker geprüft und ursprüngliche Query-Store-/Datenbankoptionen exakt wiederhergestellt. Containerabwesenheit unabhängig nach Kennung, Name und Eigentumslabel geprüft. Letzte Freigabe: zwei zusätzliche Quellenstände und höchstens vier weitere Container, maximal zwei je Version, 15 Minuten regulär plus je 60 Sekunden Cleanup; verwendet zwei Quellenstände und drei weitere Container. Frühere Versuche, Quellen und Bereinigung bleiben erhalten.

**Offene Gates:**

- Erfassung: den mit dem Client unverträglichen -y-32768-Entwurf vor Umsetzung ersetzen und den ausgewählten Adapter unabhängig gegen vollständige Ergebnis-/Planzuordnung, Kodierung, beide während des Lesens begrenzten Ausgabekanäle und Abbruch/Cleanup prüfen. Die private Stückübertragung bleibt Diagnoseevidenz; keine automatische Adapterübernahme oder Erweiterung der Demo-Grenzen.
- SQL Server 2022: Hashmetadatenabweichung und eine belastbare Zuordnung des tatsächlich ausgeführten eigenen Statements klären; danach die erweiterten Aufrufformen und das Anforderungsflag buildbezogen prüfen. Weder alleinige Hashzuordnung noch ungeprüftes Verwerfen beziehungsweise Invertieren eines Merkmals.
- Beide Zielbuilds: eine nachweislich gespeicherte und tatsächlich verwendete Optimierungs-Replay-Ausgangslage herstellen und derselben eigenen Abfrage eine belegte Deaktivierung gegenüberstellen. Der 2025-Anforderungs-/Flagbefund allein schließt dieses Gate nicht; veröffentlichte Dokumentationswidersprüche nicht pauschal auflösen.
- Demo: weiterhin ausdrücklicher Umsetzungsauftrag, unabhängiger Quellen-/Ergebnisreview und vollständige Qualifikation des entworfenen Erfolgs-/NO_INDEX-/Ersatzplan-/Rücknahmeschnitts auf allen Zielversionen erforderlich. Keine weiteren SQL-/Lab-Läufe oder Demo-Umsetzung im aktuellen Auftrag; übrige Verarbeitung pausiert.

**Evidenzbindung und Grenze:**

Private, unversionierte Evidenz unter Runtime/Temp/dgn004-version-gate-20261024; Rohlogs, vollständige Pläne, Containerkennungen und Diagnoseskripte werden nicht versioniert.

Privater `report.json`: SHA-256 `e81f450c574a64dbf6f2e6393bbc80cad3f44bda4fb78e16abbce27a1abe09c5`.

- Diagnosequelle C1: SHA-256 `d7181937ec78d64c7d6818a28029323b36b8c7ea99771c4f5b7132b929bf4a10`.
- Diagnosequelle C2: SHA-256 `ccbaef7a7d9ee5c9eaad01a38063946b2a9233b62baa465f2a91cfc231f7cf94`.
- Diagnosequelle C3: SHA-256 `3e49b6ed7cbeae04269b9f9cdcd7d021972ecea15cd03dbdf6f5228b271afcbf`.
- Diagnosequelle C4: SHA-256 `9593387d65b9a776d41dd635a590ab724b5585275d6971f3823b9860b207ebb6`.
- Diagnosequelle C5: SHA-256 `5924b221e1bc0195e48beb6f5095695d1f5f5495239b3aeba7956f1ea69d7e9e`.

Prüfsummen binden die lokal erhaltenen Rohbefunde; sie ersetzen keine reproduzierbare Demo-Quelle, unabhängigen Review oder Laufzeitqualifikation. Die 2025-Hälfte von C5 wurde mit unveränderten Diagnosefunktionen innerhalb derselben freigegebenen Runde fortgesetzt.

Registrierte Einordnung: [Versionsbefunde zu SRC-027/SRC-031](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-begrenzte-versionsdiagnose-vom-24-oktober-2026).

###### Lesende Hashanalyse und Replay-Referenz

Historischer Lesestand aus PR318; die Befunde bleiben unverändert, die anschließend folgende Planung konkretisiert die nächsten Gates.

**Stand:** 2026-10-24; Basis `a87d1d7e68679238b766fb31a399b46825f14efd`. **Status:** READ_ONLY_WITH_OPEN_GATES – vorhandene Planbelege und Originalquellen geprüft; Hashmuster eingeordnet und Replay-Referenz ausgewählt. Keine neue SQL-Ausführung oder Demo-Freigabe.

Ausschließlich lesende Auswertung vorhandener privater Plan-XML-Dateien (Extensible Markup Language; strukturiertes Planformat) und öffentlicher Originalquellen. Attribute und vollständiger Text sowie Operatorfolge, Objektdeskriptoren und Prädikat-XML paarweise verglichen. Keine Ausführung historischer Skripte, Tests, SQL-/Lab- oder CI-Läufe während dieser Sichtung; statische Veröffentlichungsprüfungen sind davon getrennt.

**Hashbefunde und Aussagegrenzen:**

- SQL Server 2022/16.0.4265.3: In den unveränderten Rohplänen wechselt QueryHash (Abfragehash) von 0xA3EEC222B4E92764 auf 0xD7181702D1C14CFD und entspricht danach dem unveränderten QueryPlanHash (Planhash). Der Wert steht bereits im XML; keine erst durch den Auswertungsparser erzeugte Vertauschung.
- Vollständiger Statementtext, StatementSqlHandle, ParentObjectId, DatabaseContextSettingsId, Sitzungsoptionen, Reihenfolge der 65 physischen/logischen Operatoren, 32 Objektdeskriptoren und Prädikat-XML sind vor/nach dem Standard-Forcing gleich. Derselbe Vergleich auf SQL Server 2025/17.0.4075.5 lässt auch beide Hashwerte unverändert. Diese vorhandenen Belege sprechen für dasselbe eigene Statement; die Listenvergleiche sind kein vollständiger semantischer Planäquivalenznachweis.
- Das Muster passt genau zu veröffentlichten Originalreproduktionen der Hashüberschreibung bei Planerzwingung: eine USE-PLAN-Reproduktion und eine Query-Store-Reproduktion (persistente Abfrage-/Planhistorie). Die Quellen sind eigenständige experimentelle Primärbefunde, keine Hersteller-Fixbestätigung für den hier betrachteten 2022-Build. Dessen konkrete Produktursache oder ein verfügbarer Fix wurden nicht nachgewiesen.
- Die Query-Store-Originalreproduktion zeigt zusätzlich spätere Änderungen von sys.query_store_query.query_hash. Der lokale Diagnosebericht enthält diesen Kataloghash nicht vor/nach dem Forcing; eine solche lokale Katalogänderung darf deshalb nicht behauptet werden. Alleiniges Ausweichen vom XML-Hash auf den Kataloghash ist ebenfalls keine belastbare Zuordnung.
- Eine unveränderte QueryHash-Gleichheit ist unter Forcing keine geeignete alleinige Identitätsbedingung. Vor späterer Umsetzung die kombinierte Bindung an eigene Datenbank/Prozedur, vollständigen Text, Kontext, Query-/Planrollen und tatsächliche Ergebnis-/Ausführungszuwächse unabhängig prüfen. Handles und Hashes bleiben ergänzende Beobachtungen; kein Fehler darf pauschal ignoriert, invertiert oder durch einen neuen Alleinschlüssel ersetzt werden.

**Vorhandene private Planbelege:**

Die Dateien bleiben unversioniert; SHA-256-Prüfsummen binden die gelesenen Bytes, nicht eine neue Ausführung.

- 2022 vor Erzwingung: `Runtime/Temp/dgn004-version-gate-20261024/C5-2022-04-initial-2.plan.xml`; SHA-256 `42ddbcdc4a5979473e9e6010c72dd129bb2d995023df17b6e6aad8525c5ef913`.
- 2022 unter Standard-Erzwingung: `Runtime/Temp/dgn004-version-gate-20261024/C5-2022-05-TWO_DEFAULT.plan.xml`; SHA-256 `1a0cc10982d8c167f8a2a1439e3a846443298654822cb407d396cd06492f714b`.
- 2025 vor Erzwingung: `Runtime/Temp/dgn004-version-gate-20261024/C5-2025-04-initial-2.plan.xml`; SHA-256 `3032545ee9c5611851d290c9f13a8ad3309f5c24e5836df20b878be2f63fcb1d`.
- 2025 unter Standard-Erzwingung: `Runtime/Temp/dgn004-version-gate-20261024/C5-2025-05-TWO_DEFAULT.plan.xml`; SHA-256 `49b26f95709a0d6dd7d95952fc1c0baf874e1181797486e804db2b80f45e0c87`.

**Experimentelle Originalquellen:**

- [ORIGINAL_EXPERIMENT – veröffentlichte eigene Reproduktion](https://www.sql.kiwi/2024/11/forced-plans-query-hash/), veröffentlicht am 2024-11-28: USE PLAN führt im reproduzierten Beispiel zur Überschreibung des Abfragehashs durch den Planhash; historische Untersuchung bis einschließlich SQL Server 2022 CU16. CU bedeutet Cumulative Update, kumulatives Produktupdate; keine allgemeine Aussage über spätere Builds daraus ableiten.
- [ORIGINAL_EXPERIMENT – veröffentlichte eigene Reproduktion](https://kendralittle.com/2024/11/24/query-hash-values-meaningless-same-as-query-plan-hash-sql-server/), veröffentlicht am 2024-11-24: Query-Store-Forcing zeigt zunächst die Hashüberschreibung im Plan und später einen geänderten Kataloghash für dieselbe Query-Kennung. Belegt eine mögliche Fehlerausprägung, nicht deren Auftreten in unseren nicht erfassten Katalogwerten.

**Replay-Referenz:**

REFERENCE_CANDIDATE_NOT_ADAPTED – quellenbasierte Referenz, keine angepasste Abfrage oder Versionsqualifikation.

Repository `microsoft/bobsql`, Commit `8a6ade5ae3008e68d072e7346bc00e171097f519`. Git-Blob-Prüfwerte der Quellen: `demos/sqlserver2022/IQP/opf/bigjoin.sql` = `ba8e46ff75a9508585d2e18f9ec29cb57fbf5267`; `demos/sqlserver2022/IQP/opf/readme.md` = `d1498eee25536cf53df830ca187da706217a0131`.

Zwei mit UNION ALL verbundene SELECT-Zweige mit jeweils zehn WideWorldImporters-Tabellen und neun Joins, projizierten Detailtupeln und abschließendem ORDER BY OrderID. WideWorldImporters ist eine Microsoft-Beispieldatenbank; UNION ALL erhält Duplikate. Die Form unterscheidet sich vom bisher untersuchten einzelnen COUNT_BIG-/SUM-Sternjoin mit gleichförmigen Id-Verknüpfungen.

Die Microsoft-Repository-Anleitung erwartet has_compile_replay_script = 1 (gespeicherte wiederverwendbare Kompilierungsschritte vorhanden) und beschreibt danach geringeren Kompilierungsaufwand bei Erzwingung. Das ist ein dokumentierter Referenzablauf für SQL Server 2022, kein Laufnachweis dieses Projekts, kein garantierter Leistungsgewinn und keine 2025-Qualifikation.

Replay-Eignung hängt laut Hersteller von Optimierungsaufwand, internem Suchbaum und dem Nutzen gegenüber Speicherkosten ab; Joinzahl und FULL-Optimierung allein garantieren keinen Replay. Die Anleitung verlangt eine größere Beispieldatenbank und ein anderes Ressourcenprofil. Eine kleine synthetische Variante innerhalb der später ausdrücklich beauftragten Daten-/Plan-/Zeitgrenzen kann die Eignung verlieren und ist unbestätigt.

Nur als Referenz für eine spätere gesondert freizugebende begrenzte Diagnose-Ausgangsabfrage prüfen. Der vorhandene DGN-004-Demoschnitt mit fester ForceProbe-Abfrage und sechs Nutzaufrufen wird nicht ersetzt. Keine Anpassung, Bereitstellung oder SQL-Ausführung in diesem Auftrag.

**Ausgeschlossene Steuerteile:**

- bigjoin.sql leert den datenbankbezogenen Prozedurcache; dieser Steuerteil wird nicht als Schulungsbaustein übernommen.
- restorewwi.sql entfernt eine feste Datenbank, stellt die Beispielsicherung wieder her und leert Query Store. Diese Bereitstellungs-/Historienoperationen erfüllen nicht den eigenen markergebundenen Lifecycle und werden ausgeschlossen.
- forceplan.sql verwendet nur zwei Argumente; find_query_in_query_store.sql liest die Plansicht ungefiltert. Weder Deaktivierungssignatur noch eindeutige Zielbindung aus diesen Hilfsskripten übernehmen.

**Gepinnte Microsoft-Quellen:**

- [Referenzabfrage](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/bigjoin.sql)
- [Referenzanleitung](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/readme.md)
- [Wiederherstellungsskript – ausgeschlossen](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/restorewwi.sql)
- [Force-Aufruf – keine Deaktivierungsvorlage](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/forceplan.sql)
- [Plansicht – keine eindeutige Zielselektion](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/find_query_in_query_store.sql)

StatementOptmEarlyAbortReason = TimeOut in vorhandenen Warm-up-Plänen bezeichnet ein internes Such-/Aufgabenlimit des Optimierers, keinen nachgewiesenen Client- oder SQL-Aufruftimeout. Daraus weder Replay-Eignung noch fehlgeschlagene Ausführung ableiten.

**Herstellergrundlagen:**

- [Replay-Eignung und Speicherung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16)
- [Internes Optimierer-Suchlimit](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/troubleshoot-optimizer-timeout-performance)
- [Query-Store-Abfrageidentität](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-transact-sql?view=sql-server-ver16)

**Offene Gates:**

- Zuordnung und 2022-Signatur: Hashmuster quellenbasiert eingeordnet; kombinierte Text-/Modul-/Kontext-/Ergebnis-/Planbindung einschließlich ergänzender Hash-/Handlewerte unabhängig prüfen. Ein früherer Diagnoseabbruch ist damit erklärt, nicht nachträglich bestanden. Erweiterte 2022-Aufrufformen und Anforderungsflag bleiben ungeprüft; keine Hersteller-Fixbehauptung für 16.0.4265.3.
- Replay auf beiden Builds: Referenz erst nach neuem ausdrücklichem Auftrag als begrenzte synthetische Diagnoseform entwerfen und qualifizieren. Gespeicherten Replay und tatsächliche Wiederverwendung derselben eigenen Abfrage positiv belegen; anschließend tatsächliche Deaktivierung gegenüberstellen. Flagwechsel oder fehlendes optionales Replay-Merkmal allein reichen nicht. Keine Laufzeitfreigabe für den verkleinerten Kandidaten oder 2025.
- Erfassung: überholten -y-32768-Entwurf vor Umsetzung ersetzen und den ausgewählten Adapter unabhängig gegen vollständige Zuordnung, Kodierung, Ausgabegrenzen sowie Abbruch/Cleanup prüfen. Private große Diagnosepläne und Stückübertragung erweitern den geplanten Demoschnitt nicht.
- Demo: ausdrücklicher Umsetzungsauftrag, unabhängiger Quellen-/Ergebnisreview und vollständige Erfolgs-/NO_INDEX-/Ersatzplan-/Rücknahmequalifikation auf allen Zielversionen bleiben erforderlich. Nur statische Integration dieser Befunde; keine Umsetzung oder SQL-/Lab-Läufe und keine Wiederaufnahme übriger Verarbeitung.

Registrierte Einordnung: [Hashzuordnung und Replay-Referenz zu SRC-027/SRC-031](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-hashzuordnung-und-replay-referenz-vom-24-oktober-2026).

###### QueryCompilationReplay und Gegenkennzeichnung – ergänzender Quellenreview

**Stand:** 2026-10-24; Basis `c8069016aa00a6804ed608f22447e5c2a9a18251`. **Status:** REVIEWED_WITH_OPEN_GATES – Bedeutung von QueryCompilationReplay und belastbare beobachtete Gegenkennzeichnung auf beiden Zielbuilds weiterhin NOT_PROVEN (nicht nachgewiesen).

Ergänzender ausschließlich lesender Quellenreview vom 2026-10-24; Hersteller-Dokumentation und deren zwei zusammen gepinnte Quelldateien mit den bestehenden historischen Befunden abgeglichen. Nur Dokumentationsaufnahme und statische Integration autorisiert. Keine Umsetzung, Tests der Probe, SQL-/Lab-Läufe oder neue Messung; übrige Verarbeitung pausiert.

**Bedeutung und Aussagegrenzen:**

- QueryCompilationReplay ist im Hersteller-XSD (XML Schema Definition; Schemadefinition des Planformats) eine optionale Ganzzahl. Keine belastbare Wertetabelle gefunden, die Speicherung, Versuch und erfolgreiche Replay-Kompilierung für unsere Zielbuilds trennt. Weder 0 noch Abwesenheit noch ein anderer ungeklärter Rohwert wird als aus interpretiert.
- QueryCompilationReplay = 1 wird in der eigenen SQLServerFast-Fachreferenz als Nutzung beschrieben; das bleibt ein Markerkandidat. Kein hinreichend nachvollziehbarer Nachweis für beide exakten Builds, den vorgesehenen Erfassungsweg und die Gegenkennzeichnung. Kein freigegebener PASS-Wert und keine automatische Umdeutung zum booleschen Zustand.
- Ein zwischengespeichertes Kompilierungsmerkmal beweist keine neue Replay-Kompilierung beim aktuellen Nutzaufruf. Speicherung, Abschaltanforderung, erfolgreiche Kompilierung und tatsächliche Ausführung mit vollständigen Ergebnissen bleiben getrennt zuzuordnen.

**Gepinnter Dokumentationskonflikt:**

Gemeinsamer Quellencommit `b6fe4934643919b28ddea54ad04c66ff1b2a82d1`.

- [Microsoft-Katalogtabelle](https://github.com/MicrosoftDocs/sql-docs/blob/b6fe4934643919b28ddea54ad04c66ff1b2a82d1/docs/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql.md#L55-L57), Git-Blob `a7fc21cff62f67111f293cfa71de5af885e6524b`: Die Katalogtabelle beschreibt is_optimized_plan_forcing_disabled mit 0 als deaktiviert und 1 als nicht deaktiviert.
- [Microsoft-Funktionsbeschreibung, Beispiele C/D](https://github.com/MicrosoftDocs/sql-docs/blob/b6fe4934643919b28ddea54ad04c66ff1b2a82d1/docs/relational-databases/performance/optimized-plan-forcing-query-store.md#L118-L156), Git-Blob `027099d57a33a44ce88df09af35f4c447a34a215`: Die Funktionsbeschreibung zeigt in Beispiel C replica_group_id = 1 an dritter und disable_optimized_plan_forcing = 1 an vierter Stelle zur Abschaltung. Beispiel D bezeichnet is_optimized_plan_forcing_disabled = 1 als deaktiviert und filtert genau diesen Zustand. Das widerspricht der Katalogtabelle am selben Quellencommit.

DOKUMENTIERTER Quellenwiderspruch, keine bestätigte Herstellerkorrektur oder Produktfehlerdiagnose. Die bereits erhaltenen 2025-Anforderungsbeobachtungen passen zu Beispiel D; sie belegen ohne positiven Replay-Ausgangszustand keine tatsächliche Abschaltung. Keine zusätzliche 2022-Signaturprüfung erfolgt.

**Kontrollweg und Grenzen einer Gegenkennzeichnung:**

- Der bestehende Parameterweg bleibt ein dokumentierter Kontrollweg: eigene Query-/Planbindung, passende Replikatkennung und Abschaltanforderung vor frischer eigener Kompilierung prüfen; anschließend erfolgreiche klassische Planerzwingung, vollständigen Plan, Tupel und aktuelle reguläre Ausführung zusammenführen. Ein angezeigter Kontrollzustand allein ist weiterhin kein beobachteter Gegenmarker für zuvor positiv belegte Replay-Nutzung.
- DISABLE_OPTIMIZED_PLAN_FORCING ist als Query Hint (Abfragehinweis) ab SQL Server 2022 dokumentiert. Eine gesonderte spätere Negativkontrolle könnte diesen dokumentierten Abschaltweg untersuchen. Seine Aufnahme oder Entfernung im Statement verändert jedoch den Abfragetext und möglicherweise die Query-Store-Identität; sie verletzt damit die unveränderte Textbindung des bestehenden Ein–Aus–Ein-Plans.
- Der Hintweg ist eine methodische Alternative außerhalb des unveränderten Vergleichsprotokolls, keine jetzt freigegebene Ersatzphase. Kein Hint einfügen, Modul ändern, Quellen-/Aufrufbudget vergrößern oder zusätzliche Laufvariante automatisch beginnen. Auch dieser Kontrollweg liefert ohne positive Ausgangslage und freigegebenen Beobachtungsvertrag keinen direkten Deaktivierungsnachweis.
- Fehlendes optionales Attribut, QueryCompilationReplay = 0, bloßer Anforderungsflagwechsel, UsePlan allein, kein Replay-Fehler oder kürzere Kompilierungszeit schließen das Gate nicht. Bei unbekannter Markersemantik oder nicht beobachtbarer Nutzung bleibt NOT_PROVEN; keine Ersatztelemetrie oder gelockerten Kriterien.

**Einordnung je Zielbuild:**

- SQL Server 2022/16.0.4265.3, Developer/Linux, Compatibility Level 160: positive Wertsemantik und beobachtete Gegenkennzeichnung weiterhin offen; erweiterte Aufrufsignatur zusätzlich empirisch ungeprüft. Keine Laufzeitabnahme aus dem allgemeinen Herstellerbeispiel.
- SQL Server 2025/17.0.4075.5, Enterprise Developer/Linux, Compatibility Level 170: historische Signatur-/Anforderungsflagbefunde bleiben Teilnachweis. Ohne positiv gespeicherten und tatsächlich verwendeten Replay weiterhin kein Nutzungs- oder Abschaltungsnachweis; keine Übernahme einer 2022-Referenz als 2025-Abnahme.

**Offene Freigabegates:**

- Primärquellenvertrag für erfolgreiche Replay-Kompilierung und belastbare Gegenkennzeichnung auf beiden exakten Builds unabhängig klären; Quellenwiderspruch und Markerkandidat ausdrücklich erhalten. 0, 1 oder Abwesenheit ohne diesen Vertrag nicht zum Erfolgskriterium erklären.
- Marker und Gegenbeleg zur frischen eigenen Kompilierung sowie derselben aktuellen Query-/Plan-/Kontext-/Ergebnisbindung unabhängig prüfen. Die Aus-Phase verlangt weiterhin erfolgreiche klassische Erzwingung, eine vorab freigegebene Gegenkennzeichnung und danach erneut positiv belegte Ein-Phase; Kontrollzustand allein genügt nicht.
- Der bestehende Probenplan und seine Budgets bleiben unverändert. Eine methodische Änderung zugunsten einer Hint-Gegenkontrolle müsste gesondert geplant und freigegeben werden. Umsetzung und SQL-/Lab-Läufe benötigen nach Methodenfreigabe einen neuen ausdrücklichen Auftrag; Zuordnungs-/Transportreview und empirische Versionsgates bleiben offen.

**Weitere Quellen:**

- [Offizielles Planformat-Schema](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd)
- [Originale Fachreferenz zu Planeigenschaften](https://sqlserverfast.com/epr/plan-properties/)
- [Dokumentierter Abschaltweg](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver17#c-force-a-plan-and-disable-optimized-plan-forcing-in-query-store)
- [Dokumentierter Abfragehinweis](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17#disable_optimized_plan_forcing)

Abgeschlossen ist der ergänzende lesende Quellenreview; offen bleiben Markersemantik, beobachtete Gegenkennzeichnung und sämtliche Methoden-/Versionsfreigaben. Voriger Quellenreview aus PR320, Probenplan aus PR319, alte Fehlversuche und alle Kennungen bleiben erhalten. Keine neue Demo, Planungsliste, technische Implementierung oder Laufzeitbehauptung.

Registrierte Quelleneinordnung: [QueryCompilationReplay und Gegenkennzeichnung zu SRC-027/SRC-031](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-querycompilationreplay-und-gegenkennzeichnung-vom-24-oktober-2026).

Der folgende Quellenreview aus [PR320](https://github.com/gecompat/SQL_PerformanceSchulung/pull/320) bleibt mit seinen ursprünglichen Befunden erhalten.

###### Lesender Quellenreview zum tatsächlichen Replay-Nutzungsnachweis

**Stand:** 2026-10-24; Basis `5ac459b83688a366a03396292faf41441f18f315`. **Status:** REVIEWED_WITH_OPEN_GATES – Quellenreview abgeschlossen; tatsächliche Replay-Nutzung und Deaktivierung auf beiden Zielbuilds weiterhin NOT_PROVEN (nicht nachgewiesen).

Ausschließlich lesende Prüfung der bestehenden Planung und privaten historischen Befunde sowie öffentlicher Herstellerquellen und einer ausdrücklich als Fachreferenz eingeordneten Originaldarstellung. Abruf am 2026-10-24; das Hersteller-XSD wurde im Speicher gelesen, kein SQL ausgeführt. Die jetzt autorisierte Ergänzung und Integration betrifft nur Dokumentation und statische Prüfung. Keine Umsetzung, Tests der Probe, SQL-/Lab-Läufe oder Wiederaufnahme übriger Verarbeitung.

Speicherung, Forcing-Anforderung, Replay-Versuch, erfolgreiche Replay-Kompilierung und anschließende tatsächliche Abfrageausführung sind getrennte Nachweise. Für die vorgesehenen Zielbuilds ist weiterhin kein hinreichend belegter Vertrag aus positivem Nutzungsmarker, Gegenkennzeichnung und eindeutiger Zuordnung im vorgesehenen Erfassungsweg verfügbar. QueryCompilationReplay = 1 bleibt ein Quellenkandidat, kein freigegebenes Erfolgskriterium.

**Einordnung je Zielbuild:**

- SQL Server 2022/16.0.4265.3, Developer/Linux, Compatibility Level 160: allgemeines Funktionsverhalten dokumentiert; positive Nutzungs-/Gegenkennzeichnung und deren Erhaltung über sys.dm_exec_query_plan_stats für diesen Build ungeklärt. Erweiterte Aufrufsignatur bleibt zusätzlich empirisch offen. Kein neuer Lauf oder bestandener Versionsnachweis.
- SQL Server 2025/17.0.4075.5, Enterprise Developer/Linux, Compatibility Level 170: allgemeines Verhalten ab SQL Server 2022 und historische Anforderungsflagbefunde sind kein positiver Replay-Nachweis für diesen Build. Kein gesonderter belastbarer Werte-/Gegenkennzeichnungsvertrag gefunden; keine Übertragung einer 2022-Referenz als 2025-Abnahme.

**Quellenbefunde und Grenzen:**

- [Microsoft-Katalogvertrag für Query Store (persistente Abfrage-/Planhistorie)](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17): DOKUMENTIERT für Spalten-/Fehlerbedeutungen; INFERENZ für die Nachweisgrenze. has_compile_replay_script = 1 bezeichnet ein aufgezeichnetes Replay-Skript. is_forced_plan = 1 markiert die Forcing-Anforderung und garantiert keinen exakt verwendeten Plan. Fehler 8675 / OPTIMIZATION_REPLAY_FAILED bedeutet, dass die Ausführung des Replay-Skripts gescheitert ist. Ein fehlender Fehler oder unveränderter Fehlerzähler beweist für sich keinen erfolgreichen Replay; Anforderungs- und Fehlerzählerepochen bleiben getrennt.
- [Microsoft-Funktionsbeschreibung: Capture und Replay](https://www.microsoft.com/en-us/sql-server/blog/2022/09/15/intelligent-query-processing-feature-family-additions/): DOKUMENTIERTES allgemeines Design von 2022; kein buildbezogener Beobachtungsvertrag. Capture zeichnet nützliche Optimierungsschritte auf. Replay wird bei anschließender Kompilierung eines erzwungenen Plans mit gespeichertem Skript und ohne bereits vorhandenen Cacheplan verwendet, wenn die Voraussetzungen erfüllt sind. Eine Ausführung mit zwischengespeichertem Plan belegt keine neue Replay-Kompilierung; Kompilierungsnachweis und Ausführungsnachweis müssen ausdrücklich zum selben Nutzaufruf gebunden werden.
- [Offizielles 2022-Showplan-XSD (XML Schema Definition; Schemadefinition des Planformats)](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd): DOKUMENTIERTES Format; keine dokumentierte Wertsemantik. Direkt gelesene Deklaration: QueryCompilationReplay ist optional und vom Typ xsd:int. Sie definiert weder zulässige semantische Zustände noch Erfolg, Versuch, Speicherung oder eine Gegenkennzeichnung. OptimizationReplayType enthält ein erforderliches Script-Textattribut; das Vorhandensein einer Skriptrepräsentation ist ebenfalls kein aktueller Nutzungsbeweis.
- [Öffentlicher Microsoft-Showplan-Schemaindex](https://schemas.microsoft.com/sqlserver/2004/07/showplan/): DOKUMENTIERTER Abrufstand mit begrenztem Umfang. Der abgerufene Index führt SQL Server 2022 RTM (Release to Manufacturing; ursprünglicher Veröffentlichungsstand) als jüngsten Schemaeintrag. Er liefert keinen gesonderten 2025-Wertevertrag. Das ist eine Grenze dieser veröffentlichten Quelle, keine Behauptung, SQL Server 2025 unterstütze Replay nicht.
- [SQLServerFast: eigene Fachreferenz zu Planeigenschaften](https://sqlserverfast.com/epr/plan-properties/): Originale Fachreferenz, keine Herstellerzusage oder reproduzierbare Abnahme unserer Builds. Die Referenz beschreibt QueryCompilationReplay = 1 als Verwendung optimierter Planerzwingung und nennt die Eigenschaft im Änderungsverlauf vom 2025-07-06. Ein Nachweis für 16.0.4265.3 beziehungsweise 17.0.4075.5, den geplanten Erfassungsweg und eine eindeutige Gegenkennzeichnung fehlt in dieser Darstellung. Die Aussage begründet einen zu klärenden Markerkandidaten, keinen pauschalen PASS-Wert.
- [Microsoft-Vertrag der letzten tatsächlichen Planerfassung](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17): DOKUMENTIERT für Erfassungsinhalt; METHODE/INFERENZ für notwendige Korrelation. sys.dm_exec_query_plan_stats verbindet Kompilierungsinformationen des Cacheplans mit letzten bekannten Laufzeitinformationen. Ein dort gelesenes Kompilierungsmerkmal beschreibt deshalb nicht automatisch eine gerade neu erfolgte Replay-Kompilierung. Frische eigene Kompilierung, vollständige Planbindung, eigene Ergebnistupel und regulärer Ausführungszuwachs bleiben gemeinsam Pflicht; Root-only-, alte oder mehrdeutige Pläne genügen nicht.
- [Gepinnte Microsoft-Referenzanleitung für SQL Server 2022](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/readme.md): Originaler Demoablauf am gepinnten Quellenstand; keine eigene Messung. Die Anleitung bezeichnet has_compile_replay_script = 1 als Kandidateneignung und vergleicht anschließend Kompilierungszeiten. Sie definiert keinen unabhängigen direkten Nutzungs-/Gegenmarker für unsere kleine synthetische Probe und keine 2025-Abnahme. Der Quellablauf wird nicht ausgeführt und seine Leistungswerte werden nicht als eigene Ergebnisse übernommen.

**Unzureichende Alleinnachweise:**

- Speicherflag, Forcing- oder Deaktivierungs-Anforderungsflag, StatementOptmLevel = FULL und UsePlan allein beweisen keine erfolgreiche Replay-Kompilierung.
- Fehlendes optionales QueryCompilationReplay, ein ungeklärter Wert 0 oder 1, kein Fehler 8675 oder bloßer Flagwechsel sind kein vollständiger Nutzungs-/Abschaltungsnachweis.
- Kürzere Kompilierungszeit ist höchstens ergänzende Diagnose. Sie ersetzt weder direkte Nutzungsevidenz noch vollständige Query-/Plan-/Ausführungsbindung; keine Mess- oder Leistungsbehauptung aus Quellenbeispielen.
- Die bestehende publizierte Flag-Wertetabelle und historische 2025-Anforderungsbeobachtungen bleiben als getrennte Quellen mit ihrem Konflikt erhalten. Eine Konfigurations- oder Anforderungsanzeige wird dadurch nicht zum tatsächlich beobachteten Replay.

**Offene Freigabegates:**

- Vor Umsetzung den positiven Erfolg von Speicherung und gescheitertem Versuch abgrenzen: Wertsemantik und Gegenkennzeichnung für beide exakten Builds mit nachvollziehbarer Primärquelle klären und unabhängig prüfen. Die SQLServerFast-Aussage zu Wert 1 allein schließt dieses Gate nicht.
- Den Erfassungs-/Korrelationsvertrag unabhängig prüfen: Quelle und frische Kompilierungsepoche des Markers, vollständiger eigener Text-/Modul-/Kontext-/Planbezug, vollständige Ergebnistupel und genau eine aktuelle reguläre Ausführung. Ein bloß wiederverwendeter Cacheplan darf keine neue Replay-Nutzung vortäuschen.
- Die Aus-Phase braucht erfolgreiche klassische Planerzwingung und eine vorab begründet festgelegte Gegenkennzeichnung; die anschließende Ein-Phase muss tatsächliche Nutzung erneut positiv belegen. Optionales Attribut fehlt allein genügt nicht. Unbekannte oder nicht beobachtbare Zustände bleiben NOT_PROVEN und beenden die Folge geregelt.
- Kombinierte Strukturzuordnung und begrenzten Transport weiterhin unabhängig freigeben; 2022-Signatur, Replay-Eignung beider Formen, tatsächliche Nutzung/Deaktivierung und Cleanup bleiben anschließend empirisch offen. Kein nachträgliches Bestehen früherer Fehlversuche.
- Erst ein neuer ausdrücklicher Auftrag darf Probe-Implementierung und SQL-/Lab-Runde innerhalb des unveränderten Plans erlauben. Keine Zusatzcontainer, weiteren Abfrageformen, serverweiten Ereignissessions, undokumentierten Traceflags oder gelockerten Kriterien als automatischer Ersatz. Die übrige Verarbeitung bleibt pausiert.

Abgeschlossen ist ausschließlich die lesende Quellenprüfung mit dokumentierten Grenzen. Nicht abgeschlossen sind Methodengate, unabhängige Freigabe, technische Umsetzung, Laufzeit-/Versionsabnahme oder Demoqualifikation. Der vorhandene Probenplan und alle früheren Befunde bleiben erhalten; keine zusätzliche Planungsliste oder Kennung.

Registrierte Quelleneinordnung: [Replay-Nutzungsnachweis zu SRC-027/SRC-031](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-quellenreview-zum-tatsächlichen-replay-nutzungsnachweis-vom-24-oktober-2026).

Der folgende Planstand aus [PR319](https://github.com/gecompat/SQL_PerformanceSchulung/pull/319) bleibt erhalten. Der aktuelle Quellenreview schließt sein Methodengate nicht.

###### Kombinierte Planzuordnung und begrenzte synthetische Replay-Probe

**Stand:** 2026-10-24; Basis `c238ba5c6e4b00782fd9fbc37d7c87333880823c`. **Status:** DESIGNED_WITH_METHOD_GATES – kombinierte Zuordnung und begrenzte synthetische Replay-Probe geplant; keine Implementierung, Tests der Probe, SQL-/Lab-Läufe oder Laufzeitfreigabe.

Aktueller Auftrag autorisiert ausschließlich Planung und deren Dokumentation. Frühere Genehmigungen und Budgets für SQL-/Lab-Diagnosen werden nicht wiederverwendet. Die übrige Verarbeitung bleibt pausiert; eine spätere Ausführung benötigt einen neuen ausdrücklichen Auftrag.

Separater Versionsdiagnose-Entwurf innerhalb DGN-004 (Planerzwingung), keine neue Demo oder Kennung. Gemeinsame kombinierte Planzuordnung für SQL Server 2022/2025 konkretisieren; Replay-Speicherung, tatsächliche Nutzung und tatsächliche Deaktivierung getrennt prüfen. Der bestehende ForceProbe-Demoschnitt mit sechs Nutzaufrufen, Indexentzug und NO_INDEX-Fehler bleibt unverändert und unimplementiert.

**Geplantes erstes Versionsprofil:**

- SQL Server 2022/16.0.4265.3, Developer/Linux, Compatibility Level 160; vorhandene Imagebindung sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89 als späteres erstes Prüfprofil. Erweiterte Aufrufsignatur ist hier weiterhin ungeprüft.
- SQL Server 2025/17.0.4075.5, Enterprise Developer/Linux, Compatibility Level 170; vorhandene Imagebindung sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1. Frühere Aufruf-/Anforderungsflagbefunde sind Teilnachweis, keine Replay-Abnahme. Keine Images jetzt laden oder starten und kein Wechsel auf neuere Builds innerhalb eines später freigegebenen Laufs.

**Kombinierte Zuordnung und Fehlerzählerepochen:**

- Jeder spätere Nutzaufruf besitzt eine unveränderliche Hülle aus Quellenprüfsumme, Version/Build/Edition/Compatibility Level, vollständigem normalisiertem Lauftoken, tatsächlicher Datenbank, eigener Modulkennung, Abfrageform A/B, Aufrufnummer, Phase und Start/Ende. Vier vollständige Eigentumsmarker vor jeder Mutation ausdrücklich auf NULL, binäre Gleichheit und Bytelänge prüfen; kein passender Name als Eigentumsbeleg.
- Pro Abfrageform genau eine eigene parameterlose Prozedur mit genau einem Nutzstatement. Bei Anlage und Ausführung dasselbe dokumentierte Sitzungsprofil verwenden: ANSI_NULLS, ANSI_PADDING, ANSI_WARNINGS, ARITHABORT, CONCAT_NULL_YIELDS_NULL und QUOTED_IDENTIFIER ON, NUMERIC_ROUNDABORT OFF, Sprache us_english, Datumsformat mdy und DATEFIRST 7. Ganze Engine-Textdarstellung, object_id, context_settings_id, Kontextwerte und Parametrisierungsart erfassen; keine freie Textnormalisierung, Textmarkerwechsel oder Modulanpassung zwischen Vergleichsphasen.
- Query Store (persistente Abfrage-/Planhistorie) über eigene Datenbank, object_id, vollständigen Statementtext und Kontext eindeutig auflösen. Genau eine eigene query_id und eine dazugehörige ausgewählte Force-Ziel-plan_id binden. Beide Rollen unverändert über die Folge führen; neue oder mehrdeutige Query-Kennung, verlorener Kontext oder fremdes Objekt beendet die Probe. Keine Zuordnung allein über Hash, LIKE oder TOP 1.
- QueryHash (Abfragehash), QueryPlanHash (Planhash), Statement-SQL-Handle und Cachehandle roh protokollieren. Hashwechsel allein ist weder Erfolg noch Fehler und kein Ersatz für die anderen Pflichtbezüge. Insbesondere die bekannte 2022-Überschreibung darf die eigene, anderweitig vollständig gebundene Abfrage nicht allein verwerfen. Eine Katalog- oder Handle-Konstanz wird nicht ungeprüft zum universellen Ersatzschlüssel erklärt.
- Force-Zielplan, tatsächlich ausgeführtes Statement und dessen beobachtete Query-Store-plan_id getrennt führen. Vor/nach jedem Nutzaufruf eigene reguläre Ausführungen über alle Pläne und Intervalle derselben query_id aggregieren; Mehrfachzeilen vor Joins nach plan_id, execution_type und runtime_stats_interval_id zusammenfassen. Genau eine neue reguläre Ausführung und genau einen durch Struktur und Ausführungszuwachs passenden tatsächlichen Plan verlangen; Mehrdeutigkeit oder negativer Zählerzuwachs ist Fehler.
- Nach ausschließlich eigener objektbezogener Neukompilierung die neue Cache-/Zählerepoche erfassen. Über einen Reset von DMV-Zählern (Dynamic Management Views; dynamische Diagnoseansichten) nicht blind subtrahieren. Ein Compile, Cachetreffer, neues Handle oder Zeitstempel allein beweist keine Ausführung; vollständige Ergebnistupel, echte Laufzeitzähler und Query-Store-Zuwachs müssen zum selben sequenziellen Nutzaufruf gehören.
- Den tatsächlichen Plan aus genau einem Cacheeintrag der eigenen Datenbank/Prozedur und der aktuellen Ausführung lesen; vollständigen XML-Namensraum, ein eindeutiges passendes Nutzstatement und echte Laufzeitzähler verlangen. Root-only-, alte, unvollständige oder mehrere passende Pläne zurückweisen. Zusätzliche Steuer-/Beobachtungsstatements dürfen keinen Nutzplan vortäuschen; keine Reparatur eines abgeschnittenen Plans.
- Strukturvergleich als vollständigen gerichteten Operatorbaum mit Kindreihenfolge, physischen/logischen Operatoren, eigenen Datenbank-/Schema-/Tabellen-/Indexbezügen, Join-/Seek-/Residualprädikaten, skalaren Ausdrücken, Datentypen, Sortier-/Gruppierungsschlüsseln und Projektionen entwerfen. Technische Knotennummern nur durch konsistente bijektive Referenzabbildung normalisieren. Kosten/Schätzungen, Zeiten/Laufzeitzähler und Kompilierungsmetadaten einschließlich Replay-Kennzeichnung getrennt beobachten. Kein flacher Operatorlisten- oder Hashvergleich als vollständiger Äquivalenzbeweis; unbekannte strukturelle Abweichung bleibt Fehler.
- Jede Force-Anforderung eröffnet eine eigene Fehlerzählerepoche, weil erneutes Force den Fehlerzähler zurücksetzt. Rückgabewert 0, is_forced_plan = 1 und Anforderungsflag vor Ausführung kontrollieren; danach keine neue Force-Fehlermeldung und regulären Ausführungszuwachs verlangen. Ergebnis und Fehlerbefund vor Unforce (Aufheben der Erzwingung) sichern; Unforce durch is_forced_plan = 0 prüfen. Ein verbleibendes Deaktivierungs-Anforderungsflag 1 nach Unforce ist kein verbleibendes Force-Flag.

**Deterministischer synthetischer Aufbau und Tupelorakel:**

- Genau zehn eigene synthetische Tabellen mit jeweils materialisierten int-Spalten ohne NULL: Orders 96, OrderLines 192, Customers 48, Categories 4, Contacts 24, Cities 12, Regions 6, Countries 3, Items 48 und ItemGroups 96. Insgesamt exakt 529 Datenzeilen. Pro Tabelle Id von 1 bis zur genannten Anzahl als eindeutiger Primärschlüssel; keine Views, Funktionen, berechneten Spalten oder zusätzlichen Datenquellen.
- Geschlossene Beziehungen: Orders.CustomerId = 1 + ((OrderId-1) modulo 48), Orders.ContactId = 1 + ((OrderId-1) modulo 24); OrderLines.OrderId = 1 + floor((LineId-1)/2), OrderLines.ItemId = 1 + ((LineId-1) modulo 48). Customers.CategoryId = 1 + ((CustomerId-1) modulo 4), Customers.CityId = 1 + ((CustomerId-1) modulo 12); Cities.RegionId = 1 + ((CityId-1) modulo 6), Regions.CountryId = 1 + ((RegionId-1) modulo 3). ItemGroups.ItemId = 1 + floor((MapId-1)/2), GroupNo = 1 + ((MapId-1) modulo 2). floor bedeutet Abrunden; modulo liefert den Rest einer Division.
- Nichtschlüsselwerte materialisieren: CustomerValue = 3000 + CustomerId, CategoryValue = 1000 + CategoryId, ContactValue = 2000 + ContactId, CityValue = 4000 + CityId, RegionValue = 5000 + RegionId, CountryValue = 6000 + CountryId und ItemValue = 7000 + ItemId. Diese Werte aus den jeweils verbundenen Tabellen projizieren, nicht durch Konstanten oder aus Fremdschlüsseln berechnete Ausdrücke ersetzen. Keine Fremdschlüssel-Constraints als zusätzliche Optimiererannahme.
- Genau neun vorher festgelegte sekundäre Indizes vor dem ersten Nutzaufruf: Orders(CustomerId), Orders(ContactId), OrderLines(OrderId), OrderLines(ItemId), Customers(CategoryId), Customers(CityId), Cities(RegionId), Regions(CountryId), ItemGroups(ItemId, GroupNo). Keine zusätzliche Indexkalibrierung, kein Indexentzug und keine Statistik-/Schemaänderung innerhalb der Vergleichsfolge; NO_INDEX gehört zum späteren ursprünglichen Demoschnitt.
- Vollständiger Ergebnissatz je Nutzaufruf: zehn int-Werte (OrderId, LineId, CustomerValue, CategoryValue, ContactValue, CityValue, RegionValue, CountryValue, ItemValue, GroupNo), geordnet nach OrderId, LineId, GroupNo. Erwartung unabhängig aus den geschlossenen Id-Abbildungen für jede LineId und GroupNo erzeugen; vollständige Tupel und Duplikatmultiplizitäten vergleichen. Zeilenzahl, Summen oder Prüfsummen allein genügen nicht.

**Zwei vorab begrenzte Abfrageformen:**

- Form A: zwei identische SELECT-Joinzweige mit je zehn Tabellen und neun Joins gemäß dem gepinnten Microsoft-bigjoin-Muster; Orders verbindet Customers und Contacts, Customers verbindet Categories und Cities, Cities/Regions/Countries bilden die Ortskette, OrderLines verbindet Orders mit Items und ItemGroups. Zweige durch UNION ALL verbinden und die gesamte Ausgabe nach OrderId, LineId, GroupNo sortieren. Alle 192 Lines mit je zwei Gruppen ergeben 384 verschiedene Tupel, jedes zweimal: exakt 768 Ergebnistupel.
- Form B: dieselben Tabellen, Daten, Indizes, Projektionen und Beziehungen, aber vier identische UNION-ALL-Zweige mit festem Filter LineId <= 96 je Zweig. 96 Lines mit je zwei Gruppen ergeben 192 verschiedene Tupel, jedes viermal: ebenfalls exakt 768 Ergebnistupel. Form B ist nur vorab begrenzter Ersatzkandidat, falls A nach zwei gültigen Aufwärmaufrufen keinen gespeicherten Replay liefert; keine Zusage, dass A oder B die Eignungsschwelle erreicht.
- Vor späterer Ausführung genau einen final geprüften Quellenstand mit beiden Formen und vollständigem Text festschreiben. Jede Form erhält eine frische eigene markierte Datenbank und Prozedur; die untereinander verschiedenen Texte sind keine Varianten derselben Query-Store-query_id. Kein OPTION RECOMPILE, Query Store Hint, wechselnder Kommentar, allgemeines Cacheleeren oder automatisches Wachsen der Daten/Pläne. Quelle A vollständig bereinigen, bevor B angelegt wird.

**Begrenzte Planerfassung als Entwurf:**

- Für die separate Probe begrenzte letzte-tatsächliche-Planerfassung über sys.dm_exec_query_plan_stats entwerfen, nicht den überholten -y-32768-Aufruf. LAST_QUERY_PLAN_STATS nur in der eigenen Datenbank nach vollständiger Eigentumsprüfung sichern, aktivieren und wiederherstellen. Der gemeinsame Demo-Adapter und dessen 32.767-UTF-8-Byte-Vertrag bleiben unverändert ungeklärt; dieser private Diagnoseweg wird nicht zur Schulungsimplementierung erklärt.
- Vorläufiger Transportentwurf: vollständige serverseitige XML-Darstellung als UTF-16-Bytes in nummerierten Stücken zu höchstens 100 Bytes, entsprechend höchstens 200 Hexadezimalzeichen je normaler sqlcmd-Spalte. Start-/Endrahmen, Stückzahl, lückenlose Reihenfolge, exakte Bytezahl und server-/clientseitige SHA-256-Prüfsumme prüfen; danach strikt UTF-16 dekodieren und das vollständige XML unverändert parsen. Zeichenersetzung, abgeschnittene Werte, doppelte/fehlende Stücke oder künstliche Zeilenumbrüche dürfen keinen Plan erzeugen.
- Grenzen des Probeentwurfs: höchstens 512 KiB UTF-16-Rohplan und nach Dekodierung höchstens 256 KiB UTF-8-Plantext; KiB bedeutet 1024 Bytes. Gesamte Standardausgabe einschließlich 768 Tupeln und Stückrahmen höchstens 2 MiB (2.097.152 Bytes), Fehlerausgabe zusätzlich höchstens 64 KiB. Beide Kanäle während des Lesens begrenzen und leeren. Grenzverletzung oder Dekodierungs-/XML-Fehler beendet den eigenen Aufruf und löst Cleanup aus. Keine pauschale Übernahme der bisherigen privaten Python-Prototypen.

**Offenes Methodengate für tatsächliche Replay-Nutzung:**

- Speicherung und Nutzung sind getrennte Prüfaussagen: has_compile_replay_script = 1 belegt einen gespeicherten Replay, nicht allein dessen tatsächliche Verwendung. StatementOptmLevel = FULL und reduzierte Compilezeit reichen ebenfalls nicht als Nutzungsnachweis; Zeit-/Speicherwerte nur als beschreibende Diagnose erfassen, keinen Leistungsgewinn behaupten.
- Das offizielle 2022-Showplan-XSD deklariert QueryCompilationReplay nur als optionales xsd:int; daraus folgt keine belastbare Wertsemantik. Vor dem ersten mutierenden Probelauf eine buildbezogen quellenbelegte positive Nutzungskennzeichnung und ihre Gegenkennzeichnung im vollständig erfassten tatsächlichen Plan festlegen und unabhängig prüfen. Kein konkreter Rohwert, insbesondere nicht pauschal 1, wird in diesem Plan als fertiger Nutzungsbeweis freigegeben. Ein fehlendes optionales Attribut ist für sich kein Deaktivierungsbeweis.
- Bis diese Interpretation feststeht, bleibt das Methoden-Gate OPEN: Implementierung und SQL-Freigabe dürfen nicht daraus abgeleitet werden. Ein später zugelassener Lauf muss die gewählte Markersemantik und deren unveränderte Erfassung vorab binden. Wenn der positive Nutzungsbeleg in einer Ein-Phase fehlt, keine Aus-Phase oder alternative Telemetriemethode nachschieben; Ergebnis NOT_PROVEN und geregelter Abbruch. Keine serverweiten Ereignissessions oder undokumentierten Traceflags als automatischer Ersatz.

**Geplante Folge – noch nicht ausgeführt:**

- Vorbereitung nach neuer Freigabe: Quellen-/Methodenreview, negative Parser-/Zuordnungsfälle und erwartete vollständige Tupel prüfen; anschließend genaue Image-/Containeridentität, Ressourcen, Edition, Version, Rechte und isolierte Wegwerfumgebung vor jeder Datenbankänderung prüfen. Für die Probe mindestens YELLOW-Schutz (kontrollierte Optimiererlast) mit expliziten Isolations-/Lastbestätigungen; eigene Containerdienstaktionen zusätzlich eindeutig an die bestätigte Wegwerfumgebung binden. Keine Sicherheitsstufe allein aus der kleinen Zeilenzahl ableiten.
- Quelle A in eigener Datenbank aufbauen, Ausgangsoptionen rekonstruierbar sichern; Query Store READ_WRITE, Capture ALL, 64 MiB Obergrenze, Intervall eine Minute und Flushintervall 60 Sekunden. OPTIMIZED_PLAN_FORCING muss bereits ON sein und bleibt unverändert; keine Datenbank-/Instanzumschaltung dieses Merkmals. LAST_QUERY_PLAN_STATS nur für die eigene Erfassung aktivieren. Höchstens zwei Aufwärmaufrufe je Form, vor jedem nur die eigene Prozedur per sp_recompile neu kompilieren; vollständiges Ergebnis und Plan erfassen, einmal explizit flushen und höchstens dreimal begrenzt den eigenen Zustand lesen.
- Falls nach zwei gültig zugeordneten Aufwärmaufrufen von A kein gespeicherter Replay vorliegt, A innerhalb des regulären Budgets vollständig bereinigen und höchstens B in einer neuen eigenen Datenbank versuchen. Erfassungs-, Sicherheits-, Signatur-, Struktur- oder Ergebnisfehler erlauben diesen Wechsel nicht. Liefert auch B keinen gespeicherten Replay, Version mit NOT_PROVEN beenden; kein dritter Kandidat oder Zusatzaufruf.
- Bei genau einem passenden Replay-Plan dessen eigene query_id/Force-plan_id binden und zwei feste Folgen Ein–Aus–Ein ausführen. Jede der sechs Phasen beginnt mit explizitem Unforce und bestätigtem is_forced_plan = 0, einem neuen Zählerschnappschuss und anschließend genau einem Force-Aufruf: query_id, plan_id, replica_group_id = 1 an dritter Stelle, disable_optimized_plan_forcing = 0 für Ein beziehungsweise 1 für Aus an vierter Stelle. Dies ist auf 2022 noch zu prüfen, auf 2025 nur vorläufig quellen-/befundgestützt. Fehler bedeutet Abbruch dieser Version; keine Signaturpermutationen oder Dreiparameter-Rückfälle.
- Nach angenommener Anforderung und passendem Anforderungsflag genau einen tatsächlichen Nutzaufruf mit eigener Neukompilierung ausführen, vollständige Tupel und Plan binden, eigene Query-Store-Zähler/Fehler sowie Markerrohwerte sichern und ausdrücklich Unforce prüfen. Ein verlangt gespeicherten Replay und den vorher freigegebenen positiven Nutzungsbeleg. Aus verlangt Anforderungsflag 1, weiterhin erfolgreiche klassische Erzwingung am zugeordneten Plan einschließlich positivem UsePlan-Merkmal sowie die freigegebene Gegenkennzeichnung. Die folgende Ein-Phase muss die positive Nutzung wieder belegen; keine Abschaltungsbehauptung aus Aus-Abwesenheit allein.
- Alle sechs Vergleichsphasen behalten Text, Modul, Kontext, Daten, Indizes, ausgewählten Zielplan und Datenbankkonfiguration unverändert; nur die Deaktivierungsanforderung wechselt. Vorhandensein/Verlust des gespeicherten Replay und beobachtete Planrollen vollständig protokollieren. Verlust der positiven Ausgangslage oder nicht eindeutig zugeordneter Replay-/Forcingfehler beendet die Folge, statt nachträglich einen einfacheren Nachweis zu wählen.
- Nach beiden gültigen Folgen ein letzter regulärer Nutzaufruf unter ausdrücklich aufgehobener Erzwingung, weiterhin korrekte Tupel/Zuordnung und is_forced_plan = 0 belegen. Danach Originaloptionen exakt wiederherstellen, eigene Datenbank entfernen und Abwesenheit unabhängig prüfen. Versionsspezifischer offener Befund darf nach sauberem Cleanup die schon eingeplante andere Version mit demselben Quellenstand nicht automatisch qualifizieren; ein gemeinsamer Sicherheits-/Erfassungs-/Quellenfehler stoppt die gesamte Runde.

**Harte Aufruf-, Zeit- und Ressourcengrenzen:**

- Höchstens zwei neue eigene Prüfcontainer insgesamt, je einer für die genannten 2022-/2025-Builds, sequenziell mit höchstens einem aktiven Container und einer eigenen Datenbank. Je Container zwei Prozessorkerne, 3 GiB (Gibibyte) Containerobergrenze und 2048 MiB SQL-Speicherlimit; keine Hostports, fremden Mounts oder fremden Container. Kein Download oder neuer Provider als automatischer Ersatz. Höchstens zwei gleichzeitig aktive eigene SQL-Sessions: ein Nutzworker und bei Bedarf ein Beobachter/Cleanupkanal; keine parallele Nutzlast.
- Je Version maximal zwei vorab festgelegte Abfrageformen A/B, je Form eine frische eigene Datenbank, 529 Nutzdatenzeilen und 768 Ergebnistupel je Aufruf. Höchstens acht gespeicherte Pläne der einen eigenen Nutzabfrage und 16 KiB UTF-16 je vollständigem Probetext. Jede Datenbankdatei höchstens 128 MiB; Query Store höchstens 64 MiB. Diese Probegrenzen erweitern weder die 1000-Zeilen-/4096-Byte-/32-MiB-Grenzen noch die sechs Aufrufe des ursprünglichen Demoschnitts. Für TempDB (temporäre Systemdatenbank) ist keine Last beabsichtigt; Bedarf noch ungemessen. Eigene Sessionallokationen innerhalb der Aufrufepoche beobachten und bei 64 MiB keine weitere Nutzphase zulassen beziehungsweise den belegten eigenen Worker abbrechen. Das ist ein vorläufiger Abbruchschutzwert, keine Zusage über den tatsächlichen Spitzenbedarf und keine Änderung der TempDB-Dateien.
- Maximal elf geplante Nutzaufrufe je Version: zwei Aufwärmaufrufe für A, bei fehlender Eignung höchstens zwei für B, sechs Aufrufe für zwei Ein–Aus–Ein-Folgen und ein letzter unforced Vergleich. Ohne B sind es höchstens neun. Keine Wiederholung fehlgeschlagener Phasen und keine Reserveaufrufe bis zufällig grün. Höchstens elf explizite Query-Store-Flushes und 100 reguläre SQL-Batches je Version einschließlich begrenzter Beobachtungen; vollständige Aufrufzählung vor Start reservieren.
- Gemeinsames reguläres Zeitbudget höchstens 900 Sekunden ab erstem Containerstart einschließlich beider Versionen, Kandidatenwechsel und Zwischenbereinigung; Kontrollpunkt bei 600 Sekunden. Kein neuer Kandidat oder Versionsstart mit weniger als 180 Sekunden Restbudget. Je SQL-Aufruf höchstens 15 Sekunden, äußerer Prozess höchstens 20 Sekunden und stets auf Restbudget begrenzt; abschließendes Cleanup zusätzlich höchstens 60 Sekunden je Container. Kein Zurücksetzen dieser Budgets bei Quellwechsel, Fehler oder Wiederaufnahme; frühere C1–C5-Befunde bleiben historische Evidenz, keine neuen Freigaben.

**Eigentum, Wiederherstellung und Abbruch:**

- Vor jeder Änderung vollständige FWK-002-Marker- und Rohwertprüfung (Namens-/Eigentumsvertrag für Testdatenbanken); FWK-007 nur als Query-Store-Lifecycle-Vertrag verwenden, keinen älteren verkürzenden/NULL-anfälligen Guard ungeprüft übernehmen. Baseline vor ENABLE/Optionänderung rekonstruierbar sichern; CUSTOM oder nicht rekonstruierbare Konfiguration vor Mutation ablehnen. Kein Query-Store-CLEAR, globales Cacheleeren, Datenbank-Recoveryexperiment oder Eingriff in Bestandsdatenbanken.
- Cleanup unabhängig vom Ergebnis: eigene Sessions/Transaktionen beenden, eindeutige Force-Bindungen aufheben, ursprüngliche Query-Store- und LAST_QUERY_PLAN_STATS-Optionen exakt wiederherstellen und prüfen, danach nur vollständig markergebundene Datenbank entfernen. Abschließend eigene Containeridentität samt Kennung, Name, Image und Eigentumslabel erneut prüfen, eigenen Wegwerfcontainer entfernen und Abwesenheit unabhängig nach Kennung/Name/Label belegen. Fremde Zustände unverändert lassen. Abbruchsignal sind Benutzerabbruch, Gesamt-/Schrittbudget oder Ausgabegrenze. Eigene Prozessgruppe beenden; SQL-KILL nur bei vorher belegter eigener Sessionlease aus Container-/Laufbindung, session_id und login_time mit erneuter Identitätsprüfung. Bei unbekannter Lease keinen fremden Sessionzustand erzwingen, sondern den eindeutig eigenen Wegwerfcontainer-Recoverypfad verwenden.
- Bei unbekanntem Datenbankeigentum keine SQL-Löschung erzwingen; nur bei weiterhin vollständig nachgewiesenem eigenen Wegwerfcontainer dessen vereinbarten Recoverypfad verwenden und den Eigentums-/Cleanupfehler erhalten. Timeout ist kein Bereinigungsbeweis. Fehlender Cleanup bleibt FAIL_CLEANUP und darf nicht als erfolgreicher oder ausgelassener Fachnachweis enden. Private Logs/Pläne behalten, Datenschutz vor jeder späteren Veröffentlichung prüfen; keine Secrets oder realen Diagnosedaten versionieren.

**Spätere Prüfungen – noch nicht ausgeführt:**

- Vor SQL: unabhängiger Review von vollständigem tatsächlichem Statement-/Kontextbezug, gerichteter Struktur-/Referenznormalisierung, optionalen Metadaten und Zählerepochen. Lokale Gegenfälle: gleicher Hash bei fremdem Text/Objekt/Index/Prädikat, falscher Kontext und alte oder mehrere passende Pläne müssen scheitern. Bekannte Hashüberschreibung bei vollständig erfüllter übriger Bindung muss als Metadatenbefund erhalten bleiben, ohne allein Erfolg oder Fehler zu entscheiden.
- Transportfälle vor SQL: fehlende, doppelte, vertauschte oder übergroße Stücke, falsche Bytezahl/Digest, ungültiges UTF-16, unvollständiges XML, künstlicher Clientumbruch, Root-only-Plan, fehlende Laufzeitzähler und zusätzliches passendes Nutzstatement zurückweisen; beide Ausgabekanäle während des Lesens begrenzen. Grenzen genau bei/oberhalb Rohplan-, UTF-8-, Gesamtausgabe- und Fehlerausgabelimit prüfen.
- Tupelorakel: Form A mit Multiplizität zwei gegen Form B mit Multiplizität vier unterscheiden, obwohl beide 768 Zeilen liefern. Gleiche Anzahl oder Summen mit anderen Werten/Duplikaten muss scheitern. Die schmale Detailprojektion darf nicht zu COUNT/SUM oder TOP geändert werden, um eine andere Planform zu erzeugen.
- Zählerfälle: Intervallwechsel und mehrere Speicher-/Persistenzzeilen korrekt aggregieren, Wrapper/Beobachter und nicht reguläre Ausführungen ausschließen; Query-/Planwechsel, negative Deltas und verlorene Neukompilierungs-/Force-Epochen zurückweisen. Keine Zählersubtraktion über einen ungeklärten Reset hinweg.
- Replayfälle: gespeicherter Replay ohne positiven Nutzungsbeleg, fehlendes Attribut oder bloßer Flagwechsel darf keinen Nutzungs-/Deaktivierungsnachweis liefern. Ein-Phase ohne bestätigte Nutzung stoppt, Aus-Phase ohne erfolgreiche klassische Erzwingung oder nachfolgende positive Ein-Phase bleibt unbelegt. Unbekannte Markerwerte niemals automatisch als aus interpretieren.
- Sicherheits-/Abbruchfälle: fehlende, fremde, zu lange, Unicode-abweichende oder gekürzte Marker; fehlende Rechte; nicht rekonstruierbare Ausgangsoptionen; Timeout/Outputlimit nach Setup und zwischen Vergleichsphasen; doppelte Cleanup-Anforderung und unabhängige Abwesenheit. Fehlversuche und Zähler/Budgets bleiben erhalten. Keine dieser Prüfungen oder SQL-Proben wurde in diesem Planungsauftrag ausgeführt.

**Abnahmekriterien:**

- Planungsabnahme jetzt: kombinierte Bindung, deterministische Daten-/Tupelformeln, zwei begrenzte Formen, Abfolge, Marker-Methodengate, harte Ressourcen-/Aufruf-/Zeitgrenzen, Abbruch/Cleanup und spätere Gegenfälle kanonisch dokumentiert. Nur statische Dokumentations-/Registryprüfung, keine Probe-Implementierung oder Laufzeitbehauptung.
- Spätere Teilabnahme pro Zielbuild nur nach neuer Freigabe und bestandenem Methoden-/Quellenreview: eindeutige Query-/Planrollen, tatsächliche reguläre Ausführung und vollständige Tupel, zwei vollständige Ein–Aus–Ein-Folgen mit positiv belegter Replay-Nutzung in beiden Ein-Phasen und belegter Deaktivierung dazwischen sowie unforced Abschluss und vollständig geprüfter Cleanup. Fehlende Replay-Eignung oder Nutzungsbeobachtbarkeit ist NOT_PROVEN/offenes Gate, kein grünes PASS und keine pauschale Versionsfreigabe.
- Auch eine später erfolgreiche private Probe belegt nur die bezeichneten Builds und den abgegrenzten Diagnosevertrag. Kein Leistungsbenchmark, keine 2019-Abnahme und keine Implementierungs-/Releasefreigabe der eigentlichen Erfolgs-/NO_INDEX-/Ersatzplan-Demo. Die ursprüngliche vollständige Demoqualifikation einschließlich ihrer Wiederholungen und Plattformgrenzen bleibt offen.

**Verbleibende Freigabegates:**

- Vor Umsetzung Nutzungsmarker und Gegenkennzeichnung buildbezogen quellenbelegen und unabhängig freigeben; optionales xsd:int oder Katalogflag allein genügt nicht. Der geplante Ein–Aus–Ein-Vergleich ist ohne dieses Methodengate nicht zur Mutation freigegeben.
- Kombinierte Zuordnungs-/Struktur- und Transportumsetzung einschließlich aller statischen Gegenfälle unabhängig prüfen; bestehende private Prototypen sind keine bereits freigegebene Implementierung. Eigentliche Demo-Erfassung unter 32.768 UTF-8-Bytes bleibt gesondert zu entwerfen.
- Neuer ausdrücklicher Auftrag für Implementierung der begrenzten Probe und anschließend erlaubte SQL-/Lab-Läufe innerhalb der festgelegten Gesamtrunde erforderlich. Nicht allein aus dem jetzigen Plan oder früheren SQL-Freigaben ableiten; übrige Verarbeitung pausiert.
- Erweiterte 2022-Signatur, Replay-Eignung von A/B, tatsächlich gespeicherter und genutzter Replay, Deaktivierung und Cleanup auf beiden Builds bleiben empirisch offen. Bei Grenz- oder Methodenfehlern stoppen statt Daten, Queryformen oder Nachweisregeln automatisch zu erweitern.

**Primärquellen der Herleitung:**

- [Gepinnte Microsoft-Referenzabfrage](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/bigjoin.sql)
- [Gepinnte Referenzanleitung](https://github.com/microsoft/bobsql/blob/8a6ade5ae3008e68d072e7346bc00e171097f519/demos/sqlserver2022/IQP/opf/readme.md)
- [Replay-Eignung und Grenzen](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-plan-forcing-query-store?view=sql-server-ver16)
- [Letzter tatsächlicher Plan](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17)
- [Offizielles 2022-Showplan-XSD – XML-Schemadefinition](https://schemas.microsoft.com/sqlserver/2004/07/showplan/sql2022/showplanxml.xsd)

Registrierte Einordnung: [Zuordnungs- und Replay-Probenentwurf zu SRC-027/SRC-031](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-plan-für-kombinierte-zuordnung-und-begrenzte-replay-probe-vom-24-oktober-2026).

###### Begrenzter Planungsschnitt: Planerzwingung

**Stand:** 2026-10-23; ursprüngliche Basis `4bab78cc321970c014784602f8ba068e38efd70d`. Präzisiert am 2026-10-24 gegen `c238ba5c6e4b00782fd9fbc37d7c87333880823c`; frühere Entwürfe und Befunde über [PR315](https://github.com/gecompat/SQL_PerformanceSchulung/pull/315), [PR316](https://github.com/gecompat/SQL_PerformanceSchulung/pull/316), [PR317](https://github.com/gecompat/SQL_PerformanceSchulung/pull/317) und [PR318](https://github.com/gecompat/SQL_PerformanceSchulung/pull/318) erhalten. **Status:** DESIGNED_WITH_OPEN_GATES – ursprünglicher Sechs-Aufruf-Demoschnitt erhalten; kombinierte Zuordnung und separate begrenzte Replay-Probe unter mapping_replay_probe_plan entworfen. Nutzungsmarker, Umsetzung und Versionsnachweise offen.

**Lernziel:**

Angeforderte Planerzwingung, tatsächlich ausgeführten Plan, gescheiterte Erzwingung mit erfolgreicher Ersatzplanung (Fallback) und ausdrückliche Rücknahme (Unforce) anhand getrennter Nachweise erklären. Kein allgemeiner Leistungsgewinn wird behauptet.

**Umfang:**

Eine eigene synthetische Datenbank, eine feste Abfrage in einer eigenen parameterlosen Prozedur, zwei physisch unterschiedliche Query-Store-Pläne derselben Abfrage und genau ein absichtlich entzogener sekundärer Index. Sequenzieller Ablauf im vorhandenen Framework, keine Übernahme des Analyze-Runners oder allgemeiner Lab-Infrastruktur.

**Abgrenzung und Abhängigkeiten:**

DGN-003 liefert Query Store (persistente Abfrage- und Planhistorie) als fachliche Grundlage. Dessen optionale Zweiplan-/Warnpfade erfüllen DGN-004 nicht. DGN-005 behandelt Extended Events (gezielte Ereigniserfassung); ein neuer allgemeiner Ereignispfad ist nicht Teil dieses Schnitts. Keine technische Abhängigkeit von CON-005 oder OPT-007. Für die spätere Unterrichtsfreigabe die konkrete Zuordnung zu LO-M06-04/08 (Lernziele zur Auswahl und Einordnung der Diagnosequellen) in der vorhandenen Traceability-Matrix ergänzen; CLM-076 bleibt die Aussage zur Query-Store-Historie.

**Quellenbasis und Aussagegrenzen:**

- SRC-027: datierte Detailverweise im bestehenden Quellenregister. is_forced_plan = 1 kennzeichnet den Auftrag; sp_query_store_force_plan versucht den Plan bei einer Kompilierung zu erzwingen. Beides allein belegt keine erfolgreiche Ausführung dieses Plans.
- force_failure_count zählt fehlgeschlagene Kompilierungsversuche, nicht jede Ausführung, und wird beim Wechsel von ungezwungen zu erzwungen auf null gesetzt. Deshalb erst nach dem Force-Aufruf eine neue Zählerepoche beginnen und vor Rücknahme Fehlerbefund sichern. NO_INDEX (8712) bezeichnet einen entfernten Index; die konkrete Erzeugung im entworfenen Ablauf ist noch unbestätigt.
- Bei fehlgeschlagener Erzwingung kann der Optimierer regulär einen Ersatzplan erzeugen. Laufzeitstatistik des aktiven Query-Store-Intervalls kann mehrere Speicher-/Persistenzzeilen enthalten; vor weiteren Joins nach plan_id, execution_type und runtime_stats_interval_id aggregieren. Nur regulär abgeschlossene Ausführungen der eigenen Abfrage zählen.
- Optimized Plan Forcing (optimierte Planerzwingung durch Wiederverwendung von Optimierungsschritten) existiert ab SQL Server 2022. Sein Einfluss und eine versionsgebundene Abgrenzung müssen vor Umsetzung geklärt sein; 2019 erhält keine neueren Prozedurargumente.

**Begrenzter Daten-/Abfrageentwurf:**

- METHOD/INFERENCE – Abfrageform quellenbasiert präzisiert; Planwahl und konkrete Engine-Darstellung noch nicht empirisch qualifiziert.
- Eigene lab.ForceProbe: Id = 1 bis 1000 als eindeutiger Primärschlüssel, GroupId = ((Id - 1) modulo 10) + 1 und Payload = 10 * Id. Anfänglich kein sekundärer Index; später genau einen eigenen abdeckenden Index auf (GroupId, Id) mit Payload anlegen und wieder entfernen.
- Fester vollständiger Statemententwurf: SELECT Id, Payload FROM lab.ForceProbe WHERE GroupId = 7 ORDER BY Id; Innerhalb derselben eigenen parameterlosen Prozedur ausführen, keine direkt eingereichten Ad-hoc-Varianten dieses SELECT. Prozedur zwischen den Phasen weder neu anlegen noch verändern; kein OPTION RECOMPILE, kein Query Store Hint und kein wechselnder Text-/Sessionmarker. Erfassung und Beobachtung liegen außerhalb des Nutzstatements.
- Bei jeder der sechs geplanten Nutzabfragen genau die 100 geordneten Tupel (7 + 10*j, 10*(7 + 10*j)) für j = 0 bis 99; zusätzlich Summe Id = 50200 und Summe Payload = 502000. Vollständiger Tupelvergleich ist Pflicht; Anzahl und Summen allein reichen nicht.
- Ohne sekundären Index einen Scanplan und mit dem Index einen physisch anderen, diesen Index tatsächlich nutzenden Plan für dieselbe Query-Kennung erfassen. Ob der kleine Entwurf dies je Zielversion liefert, bleibt empirisch offen; kein automatisches Datenwachstum, Hintwechsel oder unbegrenztes Wiederholen bei Abweichung.

**Präzisierte Abfrageidentität:**

- Eigene Modulkennung und unveränderter vollständiger Statementtext bleiben über alle sechs Nutzaufrufe gebunden. Objektbezogene Neukompilierung per sp_recompile nur für die eigene Prozedur; kein DROP/CREATE des Moduls, keine globale Cacheleerung. Eigene Indexänderungen sind die beabsichtigte Änderung der Planvoraussetzung.
- Dasselbe fest dokumentierte Sitzungsprofil bei Modulanlage und Nutzaufrufen verwenden: ANSI_NULLS, ANSI_PADDING, ANSI_WARNINGS, ARITHABORT, CONCAT_NULL_YIELDS_NULL und QUOTED_IDENTIFIER ON, NUMERIC_ROUNDABORT OFF; Sprache us_english, Datumsformat mdy und erster Wochentag 7. Tatsächliches context_settings_id samt relevanten Werten und query_parameterization_type erfassen. Keine stillschweigende Zusammenlegung verschiedener Kontext- oder Parametrisierungsformen.
- Die Query-Store-Zuordnung über tatsächliche Datenbank, eigene object_id, vollständigen Text und Kontext eindeutig auflösen und über die Indexphasen gegenprüfen. Genau eine eigene Query-Kennung für das Nutzstatement; Mehrdeutigkeit oder verlorene Zuordnung ist Fehler. Konkrete Engine-Text-/Parameterdarstellung später je Zielversion prüfen; keine beliebige Textnormalisierung zur Erzeugung eines passenden Ergebnisses.
- Lesende Hashanalyse: QueryHash unter Forcing nicht als zwingend unveränderten Alleinschlüssel voraussetzen; auch sys.query_store_query.query_hash kann laut Originalreproduktion betroffen sein. Unveränderte eigene Datenbank/Prozedur, vollständigen Text, Kontext und eindeutige Query-Kennung mit tatsächlichen Ausführungs-/Ergebnisbelegen kombinieren. Beobachtete Handle-Konstanz ist ein ergänzendes Merkmal, kein ungeprüfter universeller Ersatzschlüssel; unabhängiger Review bleibt offen.

**Geplanter Ablauf:**

- Vorprüfung: vollständige Rohwerte vor jeder Längenbegrenzung prüfen, eigenes isoliertes Ziel und Berechtigungen feststellen. Fehlende bekannte Voraussetzungen vor Mutation ergeben einen begründeten Framework-Skip; nach Beginn fehlende Pflichtnachweise ergeben Fehler. Setup nur mit vollständigem FWK-002-Eigentumsschutz (vier Marker, binärer Vergleich und exakte Bytelänge). Ursprüngliche Query-Store-Konfiguration erfassen, erst dann in der eigenen Datenbank begrenzt READ_WRITE und Capture ALL aktivieren.
- Zwei Ausgangspläne: Abfrage ohne sekundären Index einmal ausführen und tatsächlichen Scanplan sowie Query-Store-Zuordnung erfassen. Eigenen abdeckenden Index anlegen, nur die eigene Prozedur gezielt mit sp_recompile für eine erneute Kompilierung markieren und dieselbe Abfrage einmal ausführen. Zweite physische Planvariante mit Indexnutzung ist Pflicht; gespeicherte Historie allein genügt nicht.
- Erfolg: genau den zugeordneten Indexplan einmal manuell erzwingen, Rückgabestatus und Zähler unmittelbar danach sichern. Zwei weitere Ausführungen müssen jeweils exakte Tupel, tatsächliche passende Indexpläne und zusammen eine Query-Store-Ausführungszählerdifferenz von zwei belegen; keine neue Force-Fehlerzählung. Ein gleiches oder ähnliches tatsächlich verwendetes Planmuster muss nach einem vorab festgelegten Vergleich zuordenbar sein.
- Fehler und Ersatzplanung: Zähler und Zeitfenster sichern, nur den eigenen sekundären Index entfernen, nur die eigene Prozedur zur Neukompilierung markieren und einmal ausführen. Pflicht: Zählerdifferenz größer null, letzter Grund 8712/NO_INDEX, erfolgreiche vollständige Tupel, tatsächlicher Ersatzplan ohne entfernten Index und genau eine neue regulär abgeschlossene Query-Store-Ausführung. Keine Forderung nach exakt einem Fehlversuch und kein erneutes Force, das den Zähler zurücksetzt. Andere Fehlergründe sind keine stillschweigend gleichwertigen Alternativen.
- Ausdrückliche Rücknahme: Fehlernachweis vor möglichem Zustandswechsel sichern, sp_query_store_unforce_plan für exakt das eigene Query-/Plan-Paar ausführen, Rückgabestatus und aufgehobene Erzwingung prüfen. Eine letzte Ausführung muss die vollständigen Tupel, normalen tatsächlichen Plan und eine weitere Query-Store-Ausführung belegen. Sekundärindex bleibt wie im Anfangsschema abwesend; eigene Konfigurationsänderungen ausdrücklich zurücknehmen und prüfen. Datenbanklöschung ersetzt weder Unforce noch diese Prüfung.
- Cleanup (Aufräumen): auch nach Abbruch mit eigenem Zeitbudget, vollständiger Eigentumsprüfung und unabhängig bestätigter Datenbankabwesenheit. Ein Cleanupfehler bleibt maßgeblich sichtbar und erhält den ursprünglichen Fachfehler. Bei unklaren Markern oder gescheiterter Erstmarkierung gilt der dokumentierte Erhaltungsweg; keine fremde Datenbank oder Ressource löschen.

**Verbindlicher späterer Ergebnisvertrag:**

- Jeden Nachweis an Lauf, tatsächliche Datenbankkennung, eigene Prozedurkennung, vollständigen Abfragetext, Query-Store-query_id und Kontext der Sessioneinstellungen binden; Planidentitäten und Beobachtungsfenster vollständig dokumentieren. Kein TOP-1-/LIKE-/Hash-Alleinnachweis und keine hart codierten Query-/Plan-Kennungen.
- Tatsächlichen Ausführungsplan nach FWK-005 (Planbelegvertrag) aus demselben Aufruf wie die vollständigen Ergebnistupel prüfen. Erzwungenes Ziel und tatsächlich ausgeführten Plan getrennt führen; tatsächliche Ausführungszähler dem ausgeführten Plan zuordnen. Gespeicherter Plan, Force-Flag, Hash oder optionales UsePlan-Attribut allein reichen nicht. Der konkretisierte Zuordnungs- und Strukturvergleich unten ist Pflicht.
- Query-Store-Zähler vor/nach jeder Phase aus allen relevanten Intervallen der begrenzten Epoche bilden, Mehrfachzeilen vor Joins aggregieren und Intervallwechsel berücksichtigen. Beobachtungsabfragen, DDL (Data Definition Language; Schemaänderungen), Wrapper, abgebrochene und fehlerhafte Ausführungen ausschließen. Alte Historie oder ein neuer Kompilierungsversuch ohne belegte Ausführung darf nicht bestehen.
- Fehlende Pflichtpläne, Zähler, Tupel, Kontextbindung, NO_INDEX-Grund oder Rücknahmen nach erfüllter Vorprüfung führen zu FAIL_RESULT_CONTRACT oder FAIL_TIMEOUT nach bestehendem Statusvertrag. Kein WARN/SKIP als Ersatz für Pflichtnachweise. FWK-011-Normalisierung erst nach vollständiger Prüfung der Plan- und Metadatenbelege; bestehende FWK-012-Status- und Ergebnisfelder verwenden.

**Zuordnung des tatsächlich ausgeführten Plans:**

- Jeder der sechs sequenziellen Nutzaufrufe erhält einen eigenen Aufruf-/Phasenrecord mit Lauftoken, tatsächlicher Datenbank, eigener Modul-/Query-Kennung, Kontext, Beginn/Ende, vollständigen Ergebnistupeln und vollständigem tatsächlichem Showplan. STATISTICS XML ausschließlich um diesen Nutzaufruf aktivieren; zusätzliche Beobachtungs- und Steueranweisungen dürfen keine passenden Nutzpläne vortäuschen.
- Den angeforderten Force-Zielplan getrennt vom tatsächlich ausgeführten Plan führen. Dessen Query-Store-Zuordnung aus derselben Query-/Kontextbindung, neuem Ausführungszuwachs und passender physischer Planstruktur ermitteln; einen vorhandenen QueryPlanHash (Planprüfwert) ergänzend gegen die gespeicherte Kandidatenstruktur prüfen. Keine alleinige Hashzuordnung und kein TOP 1 bei mehreren Kandidaten. Nicht eindeutige Zuordnung ist Fehler.
- Der erste begrenzte Schnitt erlaubt für den Erfolgsvergleich nur dieselbe relevante Operatorstruktur mit denselben eigenen Datenbank-/Tabellen-/Indexzugriffen und Prädikaten wie im Force-Zielplan. Lediglich technische Knotennummern, Kosten-/Schätzwerte, Zeit-/Laufzeitzähler und Kompilierungsmetadaten sind vom Strukturvergleich ausgenommen. Keine pauschale Gleichsetzung aller Indexpläne; andere strukturelle Abweichung führt zum dokumentierten Abbruch statt automatischer Vertragslockerung.
- XML (Extensible Markup Language; strukturiertes Textformat) vollständig und ohne Ersetzungs-/Trunkierungszeichen lesen; passende Statementtexte, eigene Objekt-/Indexbindung und echte Laufzeitzähler müssen vorhanden sein. Alle Plan-Ergebnismengen und Wrapper berücksichtigen, unerwartete zusätzliche Nutzstatements zurückweisen. Die 2019-/2022-RTM-Schemata dienen als Referenz, nicht als vollständige Schemafreigabe für 2025.
- Die Erfolgsepoche verlangt zwei neue reguläre Ausführungen der eindeutig zugeordneten tatsächlichen Indexpläne und keinen neuen Force-Fehler. Nach Indexentzug verlangt die Fehlerepoche Zählerzuwachs größer null und 8712/NO_INDEX am Force-Ziel sowie eine neue reguläre Ausführung mit tatsächlichem Ersatzplan ohne entfernten Index. Der Ersatzplan darf einen schon bekannten Plan wiederverwenden; weder neue Plan-ID noch exakt ein Kompilierungsfehler sind Pflicht.
- Planstruktur und vollständige Werte belegen die beobachtete Verwendung unter der Erzwingungspolitik. Sie belegen weder, dass der Optimierer ohne Forcing anders gewählt hätte, noch einen Leistungsgewinn. Query-Store-Zähler weiterhin vor Joins nach Plan, Ausführungstyp und Intervall aggregieren und über Intervallgrenzen als Vorher-/Nachherdifferenz auswerten.
- Lesende Vertiefung der vorhandenen 2022-Pläne: Hashwechsel bei gleichem vollständigem Text, Modul, Kontext, Statement-SQL-Handle, Operatorfolge, Objektdeskriptoren und Prädikaten passt zu Originalreproduktionen der Forcing-Hashüberschreibung. Die zusätzliche Hashstabilitätsannahme des privaten Diagnosecodes ist als alleinige Identitätsbedingung ungeeignet. Vollständigen Struktur-/Objekt-/Ergebnisvertrag beibehalten und kombinierte Zuordnung unabhängig prüfen; weder neuen Lauf noch vollständige semantische Planäquivalenz oder Hersteller-Fix behaupten.

**Vollständige und begrenzte Planübertragung:**

- Der frühere Anzeigeentwurf -y 32768/-w 65535 ist für den geprüften sqlcmd-Client überholt: dessen Fehlermeldung begrenzt positive -y-Werte auf 8000. Kein aktiver ausführbarer Erfassungsadapter ist ausgewählt oder implementiert. Vor Umsetzung einen passenden Weg neu entwerfen und unabhängig prüfen; den privaten sys.dm_exec_query_plan_stats-Stücktransport nicht automatisch übernehmen. Allgemeine Standardargumente und Proxyregeln bleiben unverändert.
- Für den späteren ersten Demoschnitt bleibt die Annahmegrenze bei höchstens 32.767 UTF-8-Bytes je vollständigem tatsächlichem XML-Plan (Extensible Markup Language; strukturiertes Planformat). Diese Inhaltsgrenze ist keine gültige sqlcmd-Anzeigeoption und kein Nachweis der Machbarkeit. Größere private Diagnosepläne ändern sie nicht; eine neue Erfassungsmethode ist vor Umsetzung zu prüfen.
- Gesamte Standardausgabe je Nutzaufruf weiterhin höchstens 2 MiB (Mebibyte; 2.097.152 Bytes), Fehlerausgabe zusätzlich höchstens 64 KiB (65.536 Bytes). Beide Kanäle während des Einlesens begrenzen und leeren; kein unbeschränktes communicate/capture_output und keine Zeichenersetzung. Kodierungsfehler, Ausgabelimit oder Timeout beenden den eigenen Aufruf mit Fehler und führen in den separat begrenzten Cleanup.
- Vollständigen XML-Wurzelabschluss, passenden Namensraum, Pflichtknoten und echte Laufzeitzähler verlangen. Sämtliche Ergebnis-/Planmengen und die vollständigen 100 Ergebnistupel demselben Nutzaufruf zuordnen. Formatpadding außerhalb des XML-Dokuments darf entfernt werden; Inhalt, echte Zeilenumbrüche, Sonderzeichen und Statementtexte innerhalb des Dokuments bleiben erhalten. Keine Reparatur eines abgeschnittenen Plans, kein Zusammenkleben fremder Planfragmente und kein Auswählen nur des ersten passenden Plans.
- Der neu zu prüfende Adapter muss Kürzung und künstliche Zeilenumbrüche vermeiden. Ein Plan oberhalb der Annahmegrenze führt zum dokumentierten Abbruch, nicht zu automatischer Grenzerhöhung, -y 0, Wechsel auf den privaten Diagnoseweg oder Zusatz-Workload. Die sechs Nutzaufrufe, 180-/15-Sekunden-Budgets und 45 Sekunden Cleanup bleiben erhalten; keine automatische Planpersistenz.

**Versionsvertrag und offene Dokumentationskonflikte:**

- SQL Server 2019/Compatibility Level 150 (Datenbank-Kompatibilitätsstufe): klassische manuelle Erzwingung mit den eigenen Query-/Plan-Kennungen; keine nur ab 2022 vorhandenen Argumente oder Katalogspalten referenzieren. Für Query-Store-Plan-/Kontextsicht VIEW DATABASE STATE vorsehen.
- SQL Server 2022/160 und 2025/170: optimierte Planerzwingung als zusätzlichen Einfluss protokollieren. Ziel bleibt der klassische manuelle Schnitt mit einer nur auf den eigenen Force-Plan begrenzten Deaktivierung; weder neue Abfragehinweise noch Datenbank-/Instanzumschaltung. Konkrete buildbezogene Aufrufsignatur und belastbare Interpretation der Statusspalte müssen vor dieser Mutation geklärt sein. Für Plan-/Kontextsicht VIEW DATABASE PERFORMANCE STATE vorsehen.
- Die widersprüchlichen Angaben zur 0/1-Bedeutung von is_optimized_plan_forcing_disabled und zum zusätzlichen replica_group_id-Argument sind REVIEW_REQUIRED (erneute Quellenprüfung erforderlich). Kein blindes Kopieren von Beispiel C/D, keine bloße Invertierung der Flagprüfung und kein Rückfall auf optimierte Erzwingung oder einen anderen Fehlergrund, nur um ein positives Ergebnis zu erhalten.
- Zusätzliche reine Quellenprüfung: die Microsoft-Systemreferenzpakete 160.2.8/170.0.4 enthalten die Force-Prozeduren ohne Parameterliste und die fragliche Statusspalte ohne Bedeutungsdefinition. Daraus folgt keine Auflösung des Aufruf-/Flagkonflikts und keine Aussage zur Vollständigkeit laufender Serverkataloge. Die Quelle ist für Schemaexistenz verwendbar; die strittigen Detailaussagen bleiben REVIEW_REQUIRED.
- 2025 ausschließlich im eigenen lokalen Primär-/Einzelinstanzumfang betrachten; keine sekundären Replikate und keine Replikatmetadaten als pauschale Voraussetzung. ALTER-Recht auf der eigenen Datenbank für Force/Unforce/Flush, ALTER am eigenen Modul für sp_recompile und SHOWPLAN auf allen referenzierten Datenbanken getrennt prüfen. Zusätzliche Versionsfelder nur in tatsächlich unterstützten Abfragezweigen referenzieren; keine ungültigen Spalten in scheinbar geschützten statischen Ausdrücken.
- Neue Build-/Konfigurationsbelege können spätere ausdrücklich autorisierte lesende SQL-Metadatenabfragen erfordern. Dieser Dokumentationsauftrag autorisiert sie nicht. Auch nach Quellenklärung bleiben tatsächliche Parametrisierungs-/Textdarstellung, Scan-/Indexwahl, Erfolgs-/NO_INDEX-/Ersatzplansequenz und Rücknahme auf allen drei Zielversionen empirisch offen.
- Zum Schließen des Versionsgates ist eine eindeutige Herstellerklärung oder ein später ausdrücklich autorisierter gezielter Nachweis am festgelegten 2022-/2025-Build nötig: akzeptierte Aufrufform, tatsächlich am eigenen Plan deaktivierte optimierte Erzwingung und belastbar interpretierter Status. Das engere Erfassungsprofil allein erteilt diese Freigabe nicht.
- Begrenzte Versionsdiagnose vom 24. Oktober 2026: 2025/17.0.4075.5 bestätigt die Vierargument-Reihenfolge mit Replikatkennung an dritter und Deaktivierungsanforderung an vierter Stelle sowie passende 0/1-Flagwerte; tatsächliche Replay-Abschaltung bleibt unbelegt. 2022/16.0.4265.3 bestätigt nur den Standardaufruf; Hashmetadatenabweichung blockierte die weiteren Varianten. Vollständiger Befund unter version_probe_result, keine pauschale Versionsfreigabe.
- Lesende Hash-/Replay-Sichtung: das 2022-Hashmuster ist quellenbasiert eingeordnet, die erweiterte Signatur und belastbare kombinierte Zuordnung bleiben zu prüfen. Microsoft-bigjoin liefert eine dokumentierte 2022-Replay-Referenz, keine Zusage für verkleinerte synthetische Daten oder 2025. Gespeicherter Replay, tatsächliche Nutzung und tatsächliche Deaktivierung müssen getrennt am eigenen Statement belegt werden; hash_replay_review_result bindet Quellen und Grenzen.

**Schutz- und Abbruchgrenzen:**

- Entwurfsobergrenzen je Lauf: 1000 Nutzzeilen, genau sechs geplante Nutzabfrageaufrufe ohne Wiederholungsschleife, höchstens acht gespeicherte Pläne dieser Abfrage, 4096 UTF-16-Bytes (Unicode-Zeichenkodierung) je Nutztext, 32 MiB (Mebibyte) Query-Store-Obergrenze und 128 MiB je Datenbankdatei. Abweichende Planwahl führt zum dokumentierten Abbruch statt zusätzlicher Nutzabfragen.
- Höchstens 180 Sekunden regulär, 15 Sekunden pro SQL-/Beobachtungsschritt innerhalb des verbleibenden Gesamtbudgets, maximal 30 begrenzte Abfragen pro Beobachtungsphase und acht explizite Query-Store-Flushes (Übertragung in persistente Historie) insgesamt; separat höchstens 45 Sekunden Cleanup. Kein pauschales Warten als Erfolgsbeleg, keine automatische Korrektur eines READ_ONLY-Zustands. Das sind vorläufige Schutzgrenzen, keine gemessenen Laufzeiten oder Speicherverbrauchsbehauptungen.
- Keine globale Cacheleerung, kein Query-Store-CLEAR, keine instanzweite Optionsumschaltung und keine Änderungen an Bestandsdatenbanken. Neue Kompilierungen nur für das eigene Modul; alle Marker-/Rohwert-, Timeout-, Berechtigungs- und Abbruchverträge des aktuellen Frameworks übernehmen. Vorhandenen Harness und FWK-007 (Query-Store-/Ereignisvertrag) verwenden.

**Spätere Demo-Tests – noch nicht ausgeführt:**

- Vor SQL: statische Prüfung auf vollständige Rohwert-/Markerprüfung vor Änderungen, begrenzte Aufruf-/Zeit-/Ressourcenpfade, korrekte versionsabhängige Argumente, Zählerepochen und explizite Rücknahme; unabhängiger Quellen-/Ergebnisreview des konkreten Abfrage- und Plannachweisvertrags.
- Spätere Ergebnisgegenfälle: bloßes Force-Flag, gespeicherter statt tatsächlichem Plan, falsche Datenbank/Query/Plan/Kontext, alte Historie, Kompilierung ohne Ausführung und fehlende Pflichtmetadaten müssen scheitern. Gleich viele Tupel mit gleichen Summen, aber anderen Werten müssen scheitern.
- Spätere Statistikgegenfälle: Speicher-/Persistenzmehrfachzeilen und Intervallgrenzen korrekt aggregieren; Beobachter, Wrapper sowie abgebrochene/fehlerhafte Ausführungen ausschließen. Zählerreset durch erneutes Force und Verlust des vorigen Fehlerbefunds zurückweisen.
- Spätere Fehlergegenfälle: NO_INDEX ohne tatsächliche erfolgreiche Ersatzplanung, Ersatzplanung ohne erhöhten Force-Fehlerzähler und anderer Fehlergrund dürfen nicht bestehen. Fehlendes Unforce oder nicht zurückgenommene Konfiguration ebenfalls ablehnen.
- Spätere Sicherheits-/Abbruchfälle: fehlende, fremde, gekürzte und Unicode-abweichende Marker/Rohwerte; Setup-/Cleanup-Idempotenz; bekannte fehlende Rechte vor Mutation; nachträglicher Captureverlust oder READ_ONLY als Fehler. Timeout während eigener erzwungener Ausführung und nach Indexentzug; unabhängige Bereinigungs-/Abwesenheitsprüfung und Erhalt unklarer Eigentumszustände.
- Spätere Qualifikation: SQL Server 2019 mit Compatibility Level 150, 2022/160 und 2025/170, jeweils Developer/Linux/Docker, zwei Kerne und 3 GiB (Gibibyte) Instanzspeicher als erstes Prüfprofil. Je Version zwei vollständige Läufe mit frischen Lauftokens aus demselben finalen Quellenstand; Build, Edition, Rechte, Konfiguration, alle Phasen und Cleanup protokollieren. Private Logs und vollständige Pläne nicht ungeprüft versionieren.
- Spätere Zuordnungsgegenfälle: Force-Ziel und ausgeführten Plan als getrennte Rollen prüfen; eindeutigen passenden tatsächlichen Plan bei abweichender Plan-ID korrekt zuordnen, falschen Hash-/Struktur-/Indexkandidaten und mehrdeutige Treffer zurückweisen. Schon bekannte Ersatzplan-ID darf gültig sein, fehlende neue tatsächliche Ausführung nicht.
- Spätere Erfassungsgegenfälle: 256-Zeichen-Kürzung, fehlendes XML-Ende, falsche Kodierung, fehlende Laufzeitzähler, zusätzliche Nutzstatements und Plan-/Gesamtausgabeüberschreitung ablehnen. Begrenzung während des Lesens und Cleanup nach Abbruch prüfen. Ungeklärte Signatur oder Flaginterpretation darf keinen mutierenden Versionspfad freigeben.
- Nach neuer Erfassungsentscheidung weiterhin 32.767/32.768 UTF-8-Bytes, Mehrbytezeichen, echte Zeilenumbrüche, äußeres Padding und künstliche Clientumbrüche prüfen. Grenze bei/oberhalb 32.768 Bytes ablehnen, beide Ausgabekanäle während des Lesens begrenzen, falsche Kodierung und fehlenden XML-Abschluss zurückweisen. -y 32768 nicht als gültige Clientoption verwenden. Die privaten Proben ersetzen diese späteren Demo-Gegenfälle nicht.
- Späterer Zuordnungsgegenfall aus der Hashsichtung: bekannte Hashüberschreibung bei weiterhin belegter eigener Text-/Modul-/Kontext-/Plan-/Ergebnisbindung von einer fremden oder mehrdeutigen Abfrage unterscheiden. Hashgleichheit allein darf keinen Erfolg erzeugen; fehlender Pflichtbezug muss scheitern. Replay-Kandidat benötigt positiven Speicher-/Nutzungsnachweis vor dem Deaktivierungsvergleich sowie vollständige Tupel einschließlich UNION-ALL-Duplikaten. Diese Fälle sind nur geplant; keine Probe oder Implementierung jetzt.

**Abnahmekriterien:**

- Dokumentationsabnahme jetzt: ursprüngliche Analyze-, Design-, Gate- und Versionsbefunde unverändert erhalten. Lesende Hashanalyse mit lokalen Planprüfsummen und Originalreproduktionen, gepinnte Replay-Referenz samt ausgeschlossenen Steuerteilen und offene Gates separat aufnehmen. Die private Diagnose wird nicht nachträglich bestanden, die Referenz nicht als angepasste Abfrage ausgegeben. Nur statische Integration, keine Umsetzung, SQL-/Lab-Läufe oder VALIDATED-Einstufung.
- Spätere fachliche Abnahme: zwei tatsächlich ausgeführte Planvarianten derselben Abfrage; danach tatsächliche erfolgreiche Erzwingung, genau abgegrenzter NO_INDEX-Fehler samt erfolgreicher Ersatzplanung und ausdrückliche Rücknahme jeweils mit vollständigem Ergebnisvertrag. Alle genannten Pflicht- und Gegenfälle sowie zwei vollständige Läufe je Zielversion bestehen; unabhängiger Review ohne offene priorisierte Befunde und erfolgreiche Bereinigung. Zusätzlich vollständige begrenzte Planübertragung und eindeutige Zuordnung zum tatsächlich ausgeführten Plan belegen; widersprüchliche Aufruf-/Flagdetails je Zielbuild vorher belastbar klären. Kein erfolgreicher Status durch gekürzte Pläne oder gelockerte Ähnlichkeitsregeln. Für den engeren ersten Schnitt gelten höchstens 32.767 UTF-8-Bytes je tatsächlichem Plan, die begrenzten beiden Ausgabekanäle und strikte Dekodierung; eine größere Planmenge ist keine akzeptierte Variante dieses Schnitts.
- Spätere Dokumentation/Integration: vollständiger deutscher Lesepfad für Vorbereitung, Erfolg, Fehlerdeutung, Rücknahme und Erhaltungsweg mit kurzen Begriffserklärungen; bestehende Lernziel-/Demokatalog-/Testabdeckungszuordnung gezielt ergänzen. Erst nach tatsächlichen Nachweisen Versionsstatus ändern und erforderliche aktuelle PR-/Main-Prüfungen binden; kein pauschaler Benchmark für diese qualitative Diagnoseübung.

**Verbleibende Freigabegates:**

- Vor Umsetzung Nutzungsmarker und Gegenkennzeichnung buildbezogen quellenbelegen und unabhängig freigeben; optionales xsd:int oder Katalogflag allein genügt nicht. Der geplante Ein–Aus–Ein-Vergleich ist ohne dieses Methodengate nicht zur Mutation freigegeben.
- Kombinierte Zuordnungs-/Struktur- und Transportumsetzung einschließlich aller statischen Gegenfälle unabhängig prüfen; bestehende private Prototypen sind keine bereits freigegebene Implementierung. Eigentliche Demo-Erfassung unter 32.768 UTF-8-Bytes bleibt gesondert zu entwerfen.
- Neuer ausdrücklicher Auftrag für Implementierung der begrenzten Probe und anschließend erlaubte SQL-/Lab-Läufe innerhalb der festgelegten Gesamtrunde erforderlich. Nicht allein aus dem jetzigen Plan oder früheren SQL-Freigaben ableiten; übrige Verarbeitung pausiert.
- Erweiterte 2022-Signatur, Replay-Eignung von A/B, tatsächlich gespeicherter und genutzter Replay, Deaktivierung und Cleanup auf beiden Builds bleiben empirisch offen. Bei Grenz- oder Methodenfehlern stoppen statt Daten, Queryformen oder Nachweisregeln automatisch zu erweitern.

**Zurückgestellt:**

Query Store Hints (gespeicherte Abfragehinweise; Zusatzpfad ab 2022), automatische Plansteuerung, Replikate, Vergleich optimierter Replay-Verfahren, Leistungsbenchmarks, PSP/OPPO (versionsabhängige Planvarianten für sensible beziehungsweise optionale Parameter), weitere Forcing-Fehlerklassen und andere Plattform-/Editionsfreigaben bleiben offen und benötigen einen eigenen Auftrag.

**Aufwand:**

M (mittel) – ausschließlich vorläufige Einschätzung; offene Plannachweis-/Versionsfragen können den Umfang ändern. Bei Überschreitung nicht autonom erweitern.

Registrierte Detailquellen: [DGN-004-Zuordnungs- und Replay-Probenentwurf](../Documentation/Research/SOURCE_REGISTER.md#dgn-004-plan-für-kombinierte-zuordnung-und-begrenzte-replay-probe-vom-24-oktober-2026).

##### 4. RES-004 – Lückenprüfung für Memory Grants und konkurrierende Zuteilungen

**P2 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand M – vorläufig.**

**Planungsentscheidung:** Danach gezielt planen; Schwerpunkt auf konkurrierenden Abfragespeicherzuteilungen.

**Begründung:** Echtes Warten auf Abfragespeicher ist ein sinnvoller Zusatz; eine weitere allgemeine Spill-Demo würde OPT-013 (Auslagerung von Arbeitsspeicherinhalten) wiederholen. Der Quellen-Alternativnachweis über aktive Sessions genügt nicht.

**Abhängigkeiten:**

- Anforderung, Gewährung, Nutzung und tatsächlich wartende Abfrage laufgenau verbinden; RESOURCE_SEMAPHORE bedeutet Warten auf Abfragespeicher.
- Begrenztes Ressourcenprofil und sichere Erholung festlegen; Resource Governor (Ressourcensteuerung) ist keine Voraussetzung für den ersten Schnitt.

**Wiederaufnahmebedingung:** Gezielter Planungsauftrag für einen tatsächlichen Grant-Wartefall mit überprüfbarem Ergebnisvertrag und ohne Verdopplung der Spill-Inhalte.

**Quellen:** `LAB-MEM-001` (Competing memory grants; konkurrierende Abfragespeicherzuteilungen).

**Abgrenzung:** RES-004 umfasst bereits Overgrant (zu hohe Zuteilung), Undergrant (zu geringe Zuteilung), Spills und konkurrierende Grants; OPT-013 behandelt bereits Spills. Nur eine tatsächliche Curriculumlücke ergänzen.

**Weiterer Prüfauftrag:** Anforderung, Gewährung und Nutzung des Abfragespeichers sowie echte Wartebeobachtung prüfen; Alternativnachweis über aktive Sessions ausdrücklich bewerten.

**Statischer Quellenbefund:** Stand `59e6c9cc8e786828bc710ca6963121511aedb07a`, erfasst am 2026-10-23. LAB-MEM-001 enthält eine ORDER-BY-Abfrage über höchstens 16384 Zeilen, die in eine temporäre Tabelle schreibt. Sie verwendet MAXDOP 2 (höchstens Parallelitätsgrad 2) und MAX_GRANT_PERCENT = 1 (Grant-Obergrenze); danach folgt eine feste Wartezeit von 15 Sekunden. Das Runbook sieht drei Worker und drei Sekunden Startvorlauf vor. Das sind vorgesehene Abläufe, keine beobachtete Speicherknappheit oder Laufzeitabnahme.

- Observe.sql akzeptiert irgendeine Grant-Anforderung einer laufzugeordneten Session, unabhängig davon, ob sie wartet oder bereits gewährt wurde. Fehlt auch diese, genügt mindestens eine Session mit passendem Lauftoken als Alternativnachweis. Die Existenz einer solchen Session belegt weder konkurrierende Zuteilungen noch RESOURCE_SEMAPHORE (Warten auf Abfragespeicher).
- Die nachgelagerte WAITFOR-Verzögerung beginnt erst nach der Abfrageausführung und ist kein Nachweis eines fortbestehenden Grants. Laut Produktdokumentation wird Abfragespeicher nach Abschluss der Abfrageausführung freigegeben. MAX_GRANT_PERCENT = 1 begrenzt die Zuteilung unter den dokumentierten Poolbedingungen; der Hint und drei vorgesehene Worker allein erzeugen keinen belegten Grant-Engpass.
- Die Szenariodefinition nennt fünf Diagnoseprozeduren, der generische Aufrufpfad verwendet jedoch nur USP_CurrentMemoryGrants. Diese Prozedur unterstützt @SessionIds als Sessionfilter; Observe.sql setzt ihn nicht. Der Analyzer kann deshalb Grants anderer Sessions ausgeben, obwohl das fachliche Prädikat einen Lauftokenfilter verwendet.
- USP_CurrentMemoryGrants liefert angeforderten, erforderlichen, gewährten, genutzten und maximal genutzten Speicher sowie Grant- und Warteinformationen. Der Szenariovertrag prüft diese Werte nicht als fachliche Abnahme. AVAILABLE ist bei null passenden Grants zulässig und bestätigt dann eine erfolgreiche Diagnoseabfrage, keinen positiven Engpassbefund. Die konfigurierte Befundhülle ersetzt diesen Nachweis nicht.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:66](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/_Shared/Worker.sql:68](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/_Shared/Observe.sql:44](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/_Shared/Observe.sql:624](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql:43](https://api.github.com/repositories/1302553964/contents/Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql:467](https://api.github.com/repositories/1302553964/contents/Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql:586](https://api.github.com/repositories/1302553964/contents/Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql:620](https://api.github.com/repositories/1302553964/contents/Code/02_CurrentState/060_USP_CurrentMemoryGrants.sql?ref=59e6c9cc8e786828bc710ca6963121511aedb07a), [Lab/Scenarios/Performance/LAB-MEM-001/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-001/runbook.json?ref=59e6c9cc8e786828bc710ca6963121511aedb07a).

Abgleich mit der Schulung: [Vorhandener RES-004-Planungsumfang mit konkurrierenden Grants und Wartebeobachtung](https://github.com/gecompat/SQL_PerformanceSchulung/blob/b5074accb314ac32c64e53adb24829a30731b15b/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L69), [OPT-013: vorhandene Demo für einen kontrollierten Sort-Spill](https://github.com/gecompat/SQL_PerformanceSchulung/blob/b5074accb314ac32c64e53adb24829a30731b15b/Demos/04_Optimizer_Statistics_Plans/OPT-013_Controlled_Spill/README.md#L15), [RES-003: getrennter Umfang für instanzweiten Speicherdruck](https://github.com/gecompat/SQL_PerformanceSchulung/blob/b5074accb314ac32c64e53adb24829a30731b15b/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L75).

**Vor einer späteren Umsetzung erforderlich:**

- Eigenständigen Lernzuwachs innerhalb von RES-004 begründen oder auf eine zusätzliche Demo verzichten. Die vorhandene OPT-013-Demo behandelt bereits einen kontrollierten Sort-Spill (Auslagerung nach TempDB). Der mögliche Zusatz ist die Diagnose konkurrierender Zuteilungen und wartender Anforderungen; allgemeiner Instanzspeicherdruck bleibt beim getrennten RES-003-Umfang.
- Eigene Session- und Request-Kennungen sowie Messzeitpunkte eindeutig zuordnen und die Diagnose auf diese Anforderungen begrenzen. Erforderlichen, angeforderten, gewährten, genutzten und maximal genutzten Speicher passend zur Aussage erfassen. Overgrant (zu hohe Zuteilung) oder Undergrant (zu geringe Zuteilung) nicht aus einem einzelnen frühen Nutzungsschnappschuss ableiten; behauptete Spills gesondert nachweisen.
- Falls RESOURCE_SEMAPHORE-Warten behauptet wird, es während der eigenen Abfrageausführung tatsächlich beobachten und mit einer noch nicht gewährten Anforderung, grant_time IS NULL (fehlender Gewährungszeitpunkt), sowie passenden Warteinformationen verbinden. Grants, wartende Anforderungen und bloß vorhandene Sessions getrennt behandeln. Eine dreisekündige Verzögerung und nachgelagertes WAITFOR ersetzen keine signalgesteuerte Beobachtungsphase.
- Begrenzten Ressourcen- und Zeitrahmen, vollständigen Worker-Erfolg, eine passende Gegenprobe und das Ende des Wartezustands vorsehen. Bei ausbleibendem Effekt einen kontrollierten Skip (nicht demonstrierbarer Effekt) liefern; allgemeine Speicherknappheit oder einen Leistungsgewinn nicht aus dem Szenariotitel ableiten.
- Vorhandene Schulungsverträge für Eigentumsmarker, Sessionsteuerung, Abbruch, Cleanup (sicheres Aufräumen) und Wiederherstellung anwenden. Versionen, Edition und Rechte vor späterer Ausführung festlegen: die Memory-Grant-Sicht erfordert unter SQL Server 2019 VIEW SERVER STATE und ab SQL Server 2022 VIEW SERVER PERFORMANCE STATE. Die genannten Versionen 2019, 2022 und 2025 sind durch die Quellensichtung nicht praktisch abgenommen.
- Qualitative Erklärungen benötigen keinen pauschalen neuen Benchmark (systematischen Leistungsvergleich). Konkrete Mess- oder Leistungsbehauptungen benötigen passende Evidenz. M (mittel) bleibt eine vorläufige Aufwandseinschätzung; eine spätere Umsetzung und Ausführung benötigen einen eigenen Auftrag.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Grant-Lebensdauer und tatsächliches Speicherwarten](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/troubleshoot-memory-grant-issues), [Microsoft: Anforderung, Gewährung, Nutzung und Rechte](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-memory-grants-transact-sql?view=sql-server-ver17), [Microsoft: Grant-Obergrenze und Poolbedingungen](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver17).

**Spätere Abnahme:**

- Dokumentierter Lernzieldelta oder begründeter Verzicht auf weitere Demo; keine Wiederholung vorhandener Spill-Inhalte.
- Falls RESOURCE_SEMAPHORE-Warten behauptet wird, dieses tatsächlich nachweisen; aktive Sessions allein bleiben unzureichend.

##### 5. CON-006 – Conversion- und Range-Deadlocks als optionale Varianten

**P2 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand M – vorläufig.**

**Planungsentscheidung:** Zusätzliche Deadlock-Varianten zurückstellen; Conversion vor Range prüfen.

**Begründung:** Ein reproduzierbarer Grundfall mit Konfliktgraph ist vorhanden. Der zusätzliche Lernzuwachs ist kleiner; die Quellenprüfung unterscheidet die konkrete Variante nicht. Conversion betrifft Sperrumwandlung, Range den geschützten Schlüsselbereich.

**Abhängigkeiten:**

- Vorhandenen CON-006-Grundfall erhalten und für jede zusätzliche Variante einen eigenen belegbaren Konfliktgraph verlangen.
- Range-Variante mit CON-002 (Schlüsselbereichssperren) abgleichen; erst nach eigenständigem Lernziel und deterministischer Auslösereihenfolge planen.

**Wiederaufnahmebedingung:** Konkreter Curriculumbedarf an einer zusätzlichen Ursache und ein nachvollziehbarer Variantenvertrag; bis dahin keine Erweiterung des vorhandenen Grundfalls.

**Quellen:** `LAB-DEAD-002` (Conversion Deadlock; Konflikt bei Sperrumwandlung); `LAB-DEAD-003` (Range Deadlock; Konflikt um Schlüsselbereiche).

**Abgrenzung:** CON-006 zeigt bereits einen reproduzierbaren Deadlock mit Deadlock Graph (Konfliktgraph). Nur zusätzliche Ursachenvarianten prüfen; CON-002 deckt Schlüsselbereichssperren fachlich ab.

**Weiterer Prüfauftrag:** Sperrkonvertierung, Isolation, Schlüsselbereich und auslösende Reihenfolge gegen die vorhandene Deadlock-Demo prüfen; unabhängigen Lernzuwachs begründen.

**Statischer Quellenbefund:** Stand `fd18d829904b6b1631f385cfaad340ca3c72bcbb`, erfasst am 2026-10-23. LAB-DEAD-002 liest in beiden Transaktionen dieselbe Zeile mit HOLDLOCK und versucht nach einer festen Verzögerung die Änderung dieser Zeile; der beabsichtigte Zusatz ist eine Sperrumwandlung vom Lesen zum Schreiben. LAB-DEAD-003 liest unter SERIALIZABLE zwei leere Schlüsselbereiche und fügt anschließend jeweils im Bereich der anderen Session ein.

- Observe.sql akzeptiert gemeinsam für die Deadlock-Szenarien irgendein xml_deadlock_report-Ereignis in der festen XE-Session (Extended Events; Ereigniserfassung). Datenbank- und Laufzuordnung, Teilnehmer, Ressourcen, Sperrmodi und konkrete Deadlock-Variante werden in diesem Prädikat nicht geprüft.
- DeadlockRange enthält anfangs nur die Schlüssel 10 und 90. Die gelesenen Leerbereiche 20 bis 40 und 60 bis 80 liegen damit zwischen denselben benachbarten Indexschlüsseln. Fachliche Ableitung: unterschiedliche logische Suchbereiche belegen hier keine getrennten Sperrressourcen; tatsächliche Bereichssperren und Umwandlungen müssen am Konfliktgraphen nachgewiesen werden.
- Die Worker verwenden feste Verzögerungen; das Runbook ergänzt drei Sekunden Startvorlauf und akzeptiert die Prozesscodes 0 und 1. Das ersetzt weder eine signalgesteuerte Abfolge noch den eindeutigen Nachweis eines Deadlockopfers mit Fehler 1205 und eines erfolgreichen Gegenparts.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:113](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Worker.sql:230](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Worker.sql:246](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/_Shared/Observe.sql:272](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-DEAD-002/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-DEAD-002/runbook.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb), [Lab/Scenarios/Performance/LAB-DEAD-003/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-DEAD-003/runbook.json?ref=fd18d829904b6b1631f385cfaad340ca3c72bcbb).

Abgleich mit der Schulung: [Vorhandener Deadlock-Grundfall mit Gegenprobe](https://github.com/gecompat/SQL_PerformanceSchulung/blob/0ea16ae8c3340ee37fc036e943017f938304c817/Demos/07_Concurrency/CON-006_Deadlock_Cycle/README.md#L13), [CON-002: Isolation und Schlüsselbereichssperren](https://github.com/gecompat/SQL_PerformanceSchulung/blob/0ea16ae8c3340ee37fc036e943017f938304c817/Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md#L971).

**Vor einer späteren Umsetzung erforderlich:**

- Eigenständigen Lernzuwachs gegenüber CON-006 (vorhandener Deadlock-Zyklus) und CON-002 (Isolation und Schlüsselbereichssperren) begründen; nur ausgewählte Ursachenvarianten ergänzen und den vorhandenen Grundfall erhalten.
- Je ausgewählter Variante tatsächlichen Konfliktgraphen mit Ressourcen, gehaltenen und angeforderten Sperrmodi, laufzugeordneten Teilnehmern sowie Opfer-/Gegenpartnachweis vorsehen. Für die Range-Variante den Indexbereich fachlich erklären; keinen bestimmten Graphen aus dem Szenariotitel ableiten.
- Vorhandene signalgesteuerte Schulungs-Sessionsteuerung, begrenzte Warte- und Abbruchpfade, vollständige Eigentumsmarker, passende Gegenprobe und sicheres Cleanup (Aufräumen) anwenden.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Schlüsselbereichssperren](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17#key-range-locking), [Microsoft: Deadlock-Diagnose](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide?view=sql-server-ver17).

**Spätere Abnahme:**

- Je ausgewählter Variante belegt der tatsächliche Konfliktgraph die erwarteten Ressourcen, Modi und Teilnehmer; allgemeines Blocking gilt nicht als Deadlock-Nachweis.
- Vorhandenen CON-006-Grundfall und seinen Abnahmestand erhalten; neue Varianten getrennt kennzeichnen und vollständig aufräumen.

##### 6. IDX-007 – Last-Page-Inserts und Sequential-Key-Vergleiche

**P2 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand L – vorläufig.**

**Planungsentscheidung:** Ausführbaren Vergleich zurückstellen.

**Begründung:** Einfügeaktivität und eine aktivierte Indexoption belegen keinen Engpass an der letzten Indexseite. Ein fairer Vergleich fortlaufender und verteilter Schlüssel benötigt größere Laststeuerungs- und Messarbeit.

**Abhängigkeiten:**

- Reproduzierbare Konkurrenz um die letzte Indexseite von Sperren und Ein-/Ausgabewarten unterscheiden; mit RES-005 (Seiten-Latches und Ein-/Ausgabewarten) abstimmen.
- Identische Last, Datenmenge, Parallelität und Messfenster sowie Versionsgrenzen der Sequential-Key-Optimierung (Optimierung fortlaufender Schlüssel) festlegen.

**Wiederaufnahmebedingung:** Geeignete isolierte Lastumgebung und belegbarer Engpass sowie fairer Vergleichsvertrag; keine pauschale Empfehlung anderer Schlüssel oder Heaps (Tabellen ohne Clustered Index).

**Quellen:** `LAB-LATCH-001` (Last-page insert contention; Konkurrenz um die letzte Indexseite); `LAB-LATCH-002` (Sequential-key optimization comparison; Vergleich der Optimierung fortlaufender Schlüssel); `LAB-LATCH-003` (Distributed-key and heap comparison; verteilte Schlüssel und Tabellen ohne Clustered Index).

**Abgrenzung:** IDX-007 ist bereits für Sequential-Key-Insert und Last-Page-Contention vorgesehen. IDX-006 behandelt Seitendichte; RES-005 unterscheidet Seiten-Latches (kurze interne Seitensperren) und Ein-/Ausgabewartezeiten.

**Weiterer Prüfauftrag:** Gleichen Workload und Datenumfang, Schlüsselverteilung, wirksame Parallelität, Feature-/Versionsgrenzen und Messreichweite der drei Szenarien prüfen.

**Statischer Quellenbefund:** Stand `00c52fdbd99288839cc570b58a3f2337e610740a`, erfasst am 2026-10-23. Die drei LAB-LATCH-Szenarien enthalten SQL-Bausteine für Einfügungen mit fortlaufendem Schlüssel, OPTIMIZE_FOR_SEQUENTIAL_KEY (Indexoption zur Optimierung konkurrierender Einfügungen) sowie einen Vergleich mit anderem Clustered Index und Heap (Tabelle ohne Clustered Index). Die Runbooks sehen je vier Worker mit höchstens 3000 Schleifendurchläufen vor. Das sind vorgesehene Abläufe, keine beobachteten Lauf- oder Leistungsnachweise.

- LAB-LATCH-001 verlangt in Observe.sql nur leaf_insert_count > 0, also mindestens eine erfasste Einfügung. Das belegt weder PAGELATCH_EX (exklusives Warten auf eine Seite im Arbeitsspeicher), die tatsächlich betroffene letzte Indexseite noch ausreichende gleichzeitige Zugriffe.
- LAB-LATCH-002 schreibt je Worker abwechselnd in LatchSequential und LatchOptimized. Geprüft werden lediglich gleiche positive Zeilenzahlen und optimize_for_sequential_key = 1 für die optimierte Variante. Getrennte Vergleichsläufe, Laufzeiten, Durchsatz und Wartezeitdifferenzen fehlen; auch gleiche Teilstände können die Zählbedingung erfüllen.
- LAB-LATCH-003 schreibt innerhalb derselben Schleife in LatchDistributed und LatchHeap. Der Schlüssel WorkerId * 1000000 + InsertOrdinal * 7919 steigt je Worker monoton. Fachliche Ableitung: arithmetische Schlüssellücken belegen keine gleichmäßige Verteilung auf physische Indexseiten. Die Prüfung verlangt nur gleiche positive Zeilenzahlen und trägt keine Leistungsüberlegenheit des Heaps oder der anderen Schlüsselwahl.
- Der generische Analyzer-Aufruf untersucht für LAB-LATCH-001/002 ausschließlich LatchSequential und für LAB-LATCH-003 ausschließlich LatchDistributed. Die Betriebszähler der jeweils zweiten Vergleichsvariante werden nicht abgefragt. Der bei LAB-LATCH-001 zusätzlich genannte USP_InternalContentionAnalysis wird über diesen PrimaryAnalyzer-Pfad nicht ausgeführt. USP_IndexOperationalStats stellt kumulative Lock-, Latch- und Ein-/Ausgabezähler bereit; diese werden im Szenarioprädikat nicht als Engpass- oder Vergleichsnachweis geprüft.
- Drei Sekunden Startvorlauf, verzögerter Workerstart und acht Sekunden Leerlauf nach den Einfügungen ersetzen keine signalgesteuerte Messphase. Die Runbooks akzeptieren die Prozesscodes 0 und 1; Complete-LabSqlWorkers verwirft den Worker-Ausgabetext. Damit fehlt ein eindeutiger Erfolgs- und Vollständigkeitsnachweis aller vorgesehenen Worker. Vier gestartete Worker allein garantieren keine tatsächliche Konkurrenz während der Beobachtung.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:323](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Worker.sql:274](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Observe.sql:306](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Observe.sql:325](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Observe.sql:361](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Observe.sql:624](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/_Shared/Observe.sql:649](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Code/03_ObjectIndex/025_USP_IndexOperationalStats.sql:253](https://api.github.com/repositories/1302553964/contents/Code/03_ObjectIndex/025_USP_IndexOperationalStats.sql?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1:152](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/LAB-LATCH-001/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-LATCH-001/runbook.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/LAB-LATCH-002/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-LATCH-002/runbook.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a), [Lab/Scenarios/Performance/LAB-LATCH-003/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-LATCH-003/runbook.json?ref=00c52fdbd99288839cc570b58a3f2337e610740a).

Abgleich mit der Schulung: [Vorhandener IDX-007-Planungsschnitt mit Engpassnachweis und kontrolliertem Skip](https://github.com/gecompat/SQL_PerformanceSchulung/blob/feb10f4d0c82b7331aa63890d3a251e55a6498ea/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L90), [Vorhandene Abgrenzung von Seitenaufteilungen und Seitendichte](https://github.com/gecompat/SQL_PerformanceSchulung/blob/feb10f4d0c82b7331aa63890d3a251e55a6498ea/Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density/README.md#L10), [RES-005: Seiten-Latches gegenüber Ein-/Ausgabewartezeiten](https://github.com/gecompat/SQL_PerformanceSchulung/blob/feb10f4d0c82b7331aa63890d3a251e55a6498ea/Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md#L989).

**Vor einer späteren Umsetzung erforderlich:**

- Im vorhandenen IDX-007-Planungsschnitt bleiben. IDX-006 (Seitendichte und Seitenaufteilungen) sowie RES-005 (Seiten-Latches gegenüber Ein-/Ausgabewartezeiten) fachlich abgrenzen; keine zweite Demo für diese bereits zugeordneten Lernziele anlegen.
- Für einen späteren Engpassnachweis PAGELATCH_EX der eigenen Datenbank, dem Zielindex und der tatsächlich umkämpften letzten Seite zuordnen; Transaktionssperren und PAGEIOLATCH_* (Warten bei Seiten-Ein-/Ausgabe) getrennt ausweisen. Fehlende Konkurrenz kontrolliert als Skip (nicht demonstrierbarer Effekt) behandeln, statt bloße Einfügeaktivität als Engpass zu bestätigen.
- Für einen späteren Messvergleich identische Datenmenge, Nutzdaten, Konkurrenz und Messdauer beziehungsweise klar definierten Arbeitsumfang vorsehen. Vergleichsvarianten getrennt und mit gleicher Messreichweite auswerten; Zählerdifferenzen samt möglicher Rücksetzungen, tatsächlichen Worker-Erfolg, Durchsatz und Wartezeiten passend zur Aussage belegen. Heap- und Schlüsselalternativen mit ihren Strukturunterschieden erklären; keine allgemeine Überlegenheit ableiten.
- OPTIMIZE_FOR_SEQUENTIAL_KEY ist ab SQL Server 2019 verfügbar; die aufgeführten Versionen 2019, 2022 und 2025 sind damit keine bereits geprüfte Laufzeitmatrix. Zielrechte, Edition und Feature-Voraussetzungen vor späterer Ausführung festlegen und Detailquellen im regulären Quellenprozess registrieren. Eine aktivierte Option allein beweist keinen Leistungsgewinn.
- Vorhandene Schulungsverträge für Sessionsteuerung, vollständige Eigentumsmarker, begrenzte Abbruchpfade und Cleanup (sicheres Aufräumen) anwenden. Fehlende Zielobjekte vor Statistikabfragen abweisen: Die lokale Einfügeprüfung übergibt OBJECT_ID ohne NULL-Abweisung; NULL (fehlender Wert) kann bei sys.dm_db_index_operational_stats den Objektumfang erweitern. Die bereits dokumentierten gemeinsamen Runner-Grenzen bleiben ebenfalls vor einer Wiederverwendung zu klären.
- Kurze qualitative Erklärungen benötigen keinen pauschalen neuen Benchmark (systematischen Leistungsvergleich). Quantitative Wachstums- oder Leistungsbehauptungen benötigen passende Messnachweise; die vorläufige Aufwandseinschätzung L (groß) bleibt eine Schätzung.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Diagnose von Last-Page-Contention](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/resolve-pagelatch-ex-contention), [Microsoft: fortlaufende Schlüssel und Indexoption ab SQL Server 2019](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver17#sequential-keys), [Microsoft: Betriebszähler, Messgrenzen und sichere Zielauflösung](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-index-operational-stats-transact-sql?view=sql-server-ver17).

**Spätere Abnahme:**

- Tatsächliche Konkurrenz um die letzte Seite von gewöhnlichen Sperren und Speichergerätezugriffen unterscheiden.
- Vergleiche verwenden erklärten identischen Messrahmen; andere Schlüssel und Heap-Varianten nicht pauschal als bessere Lösung ausgeben. Leistungsbehauptungen separat belegen.

##### 7. RES-001 – Lückenprüfung für Worker-Druck und echte Erschöpfung

**P2 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand L – vorläufig.**

**Planungsentscheidung:** Demo echter Worker-Erschöpfung zurückstellen; fachliche Unterscheidung erhalten.

**Begründung:** Vier aktive Sessions und Prozessorlast belegen keine Erschöpfung von Ausführungsthreads. Die vorhandenen CPU- und Wait-Inhalte decken Grundlagen bereits ab; ein Erschöpfungsversuch hat höhere Anforderungen an Kontrolle und Erholung.

**Abhängigkeiten:**

- CPU (Central Processing Unit; Prozessor), Worker (Ausführungsthreads) und Scheduler (Ausführungsplaner) getrennt erklären; RES-007 (Wartezeitdifferenzen) weiterverwenden.
- Tatsächliche Thread-/Warte-Evidenz, begrenzte Laststeuerung, vollständigen Worker-Abschluss und nachweisbare Erholung vor einer ausführbaren Demo planen.

**Wiederaufnahmebedingung:** Eigenständiger Lernbedarf an echter Erschöpfung und ein isoliertes, begrenztes Sicherheits- und Nachweiskonzept; kurze Erklärungen benötigen keinen pauschalen Benchmark.

**Quellen:** `LAB-CPU-003` (Worker-thread pressure; Druck auf Ausführungsthreads).

**Abgrenzung:** RES-001 behandelt bereits CPU (Central Processing Unit; Prozessor), Worker und Scheduler (Ausführungsplaner). RES-007 liefert vorhandene Wait-Deltas. Worker-Druck ist keine neue allgemeine CPU-Demo.

**Weiterer Prüfauftrag:** Emuliertes Ressourcenprofil, Sessionsteuerung, Grenzen und schwache Verify-Alternativen prüfen; Druck von tatsächlicher Erschöpfung unterscheiden.

**Statischer Quellenbefund:** Stand `ffb8ffa48b48fac025f47a2caea514c2f09d66ed`, erfasst am 2026-10-23. LAB-CPU-003 (Worker-thread pressure; Druck auf Ausführungsthreads) sieht acht Lastverbindungen vor. Jede führt innerhalb eines eigenen 18-Sekunden-Zeitbudgets wiederholt eine Aggregation über die synthetische Workloadtabelle mit 16384 Zeilen aus; MAXDOP 1 bedeutet serielle Abfrageausführung. Das Runbook nennt drei Sekunden Startvorlauf, 90 Sekunden Worker-Timeout und 300 Sekunden Szenario-Timeout. Diese statisch gelesenen Vorgaben sind kein beobachteter Worker-Engpass und keine Laufzeitabnahme.

- Observe.sql verlangt für LAB-CPU-003 nur mindestens vier Sessions mit passendem Lauftoken. Weder eine laufende eigene Anforderung noch work_queue_count (Aufgaben, die erst einen Worker benötigen), THREADPOOL (Warten auf einen Ausführungsthread) oder tatsächlich fehlende Worker-Kapazität werden verlangt. Acht vorgesehene Lastverbindungen mit seriellen Abfragen und das Profil Compact belegen allein keine kontrollierte Erschöpfung.
- USP_WorkerPressureAnalysis unterscheidet WORKER_QUEUE_PRESSURE_VISIBLE (sichtbarer Bedarf an Workern), CPU_RUNNABLE_QUEUE_VISIBLE (bereits zugewiesene Worker warten auf Prozessorzeit) und NO_WORKER_PRESSURE_VISIBLE_IN_SAMPLE (im Messfenster kein Worker-Druck sichtbar). AVAILABLE (Diagnose verfügbar) bleibt auch ohne Druckbefund zulässig. Observe.sql wertet diese fachliche Unterscheidung nicht aus, sondern gibt den konfigurierten Code BOUNDED_WORKER_PRESSURE_OBSERVED aus. Der Verify-Pfad prüft Status, konfigurierte Codes und Cleanup, aber keine daraus abgeleitete Worker-Erschöpfung oder hohe Befundzuverlässigkeit.
- Der generische Aufruf setzt @SampleSeconds = 0 und macht aus dem standardmäßig einsekündigen Schedulervergleich eine Momentaufnahme. Die in der Szenariodefinition genannten 30 Sekunden Beobachtungsfenster werden dadurch nicht als zeitlicher Vergleich umgesetzt. Drei Sekunden Startverzögerung sind keine Bestätigung, dass alle Lastverbindungen laufen und die Beobachtung in die behauptete Druckphase fällt.
- Der Analyzer besitzt keinen Datenbank- oder Sessionfilter. Scheduler, Worker und THREADPOOL-Waits werden instanzweit gelesen; der Requestkontext schließt lediglich die eigene Beobachtersession aus und begrenzt auffällige Anforderungen. Das separate Lauftoken-Prädikat begrenzt diese Diagnose nicht auf den eigenen Lastfall. Ein beobachtetes Signal könnte daher von fremder Last stammen; ein fehlendes Signal in einem Snapshot beweist keine generelle Abwesenheit.
- Das Runbook erlaubt Worker-Prozessendecodes 0 und 1. Complete-LabSqlWorkers akzeptiert diese Codes und verwirft die eingesammelte Standardausgabe; ein fachlich erfolgreicher Abschluss aller acht Lastverbindungen wird damit nicht verlangt. Cleanup läuft vor diesem Prozessabschluss und kann noch laufende Lastsessions beenden. Welche Ursache ein Endecode 1 im Einzelfall hätte, wurde nicht ausgeführt oder diagnostiziert.
- Der aktuelle Katalog nennt Worker-thread pressure unter EMULATED_INFRASTRUCTURE (nachgebildete Infrastrukturbedingungen). Der ältere Lernpfad bezeichnet LAB-CPU-003 dagegen als Spinlock-Szenario (Konkurrenz um kurze interne Synchronisation). Für diese Aufnahme gelten aktueller Katalog und tatsächliche Bausteine. IMPLEMENTED_ACTIONS_GATE kennzeichnet vorhandene Aktionsbausteine, keine praktische Qualifikation; die Definition benennt native Plattformnachweise weiterhin als externes Gate.
- Die gemeinsamen Dateien verwenden weiterhin :setvar-Vorgaben trotz sqlcmd -v im Aufrufpfad; dadurch wird die beabsichtigte Szenario-, Worker- und Laufbindung überschrieben. Die bekannte Eigentumslücke im Cleanup bei fehlendem Marker besteht ebenfalls weiter. Die gelesenen Last- und Ergebnisbausteine dürfen deshalb nicht als Nachweis eines erfolgreich ausgeführten unveränderten Gesamtpfads ausgegeben werden.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:66](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Worker.sql:57](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-CPU-003/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-CPU-003/runbook.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:30](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:793](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:930](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql:20](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql:275](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql:334](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql:422](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql:443](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/180_USP_WorkerPressureAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1:152](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/ScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabScenario.ps1:169](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabScenario.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabScenario.ps1:198](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabScenario.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabScenario.ps1:213](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Public/Invoke-LabScenario.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/LEARNING_PATH.md:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/LEARNING_PATH.md?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

Abgleich mit der Schulung: [RES-001: geplanter Umfang für Prozessorlast, Worker und Scheduler](https://github.com/gecompat/SQL_PerformanceSchulung/blob/d7c89b34333ccc078f4bb1c82fed023c5299567f/Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md#L988), [RES-001: begrenzte CPU-Last mit Zeitbudget und fehlender Nachweisevidenz als Abbruchgrund](https://github.com/gecompat/SQL_PerformanceSchulung/blob/d7c89b34333ccc078f4bb1c82fed023c5299567f/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L185), [RES-007: vorhandene Demo mit Task-, Request- und zeitbezogener Instanz-Warteanalyse](https://github.com/gecompat/SQL_PerformanceSchulung/blob/d7c89b34333ccc078f4bb1c82fed023c5299567f/Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas/README.md#L11).

**Vor einer späteren Umsetzung erforderlich:**

- Begründeten Lernzuwachs oder Verzicht innerhalb von RES-001 dokumentieren. Der vorhandene Plan umfasst bereits begrenzte CPU-Last (Central Processing Unit; Prozessor), Worker, Scheduler und SOS_SCHEDULER_YIELD (Abgabe von Prozessorzeit). RES-007 vermittelt bereits Task-, Request- und instanzweite Wait-Deltas (zeitbezogene Unterschiede von Wartezählern). Eine zusätzliche allgemeine CPU-Demo oder Wiederholung des Wait-Scope-Vergleichs vermeiden.
- Für eine spätere Aussage über Worker-Mangel tatsächlich wartende Aufgaben ohne verfügbaren Worker beobachten, etwa THREADPOOL und passende work_queue_count-Werte, und sie zeitlich mit der eigenen begrenzten Last korrelieren. Konfigurierte und effektive Workergrenzen, Belegung und CPU-Runnable-Queue getrennt erfassen. Eine Sessionzahl, hohe Prozessorlast oder ein positiver runnable_tasks_count genügen nicht. Eine dauerhafte Erschöpfung nicht aus einem einzelnen flüchtigen Signal ableiten.
- Vorher-, Last- und Erholungsphase signalgesteuert abgrenzen, erfolgreiche eigene Lastverbindungen und den passenden Beobachtungszeitraum nachweisen. Tatsächliche Analyzerbefunde auswerten; konfigurierte Befundcodes, AVAILABLE und MinimumConfidence = HIGH (hohe Mindestzuverlässigkeit) sind kein Ersatz. Bei ausbleibendem Engpass kontrolliert abbrechen oder SKIP_EVIDENCE_MISSING (fehlender Nachweis) melden; keine Erschöpfung behaupten.
- Einen isolierten Ressourcenrahmen, harte Zeit- und Lastgrenzen, unabhängigen Notabbruch und nachweisbare Wiederherstellung festlegen. Eine echte Erschöpfungsdemo erhält vor Ausführung eine eigene Sicherheitsbewertung; der bestehende gelbe CPU-Plan ist keine Freigabe dafür. Der Beobachtungs- und Abbauweg muss auch bei fehlenden normalen Workern erreichbar bleiben; eine DAC (Dedicated Administrator Connection; besondere Administratorverbindung) ist kein garantierter Rückfall unter allen Extrembedingungen. Allgemeine Lab-Infrastruktur bleibt in SQL_Server_Lab.
- Vollständige Eigentumsmarker, korrekte Parameterbindung und Schulungsverträge für Sessionsteuerung, Worker-Ergebnisprüfung, Abbruch und Cleanup (sicheres Aufräumen) anwenden. Erlaubte Endecodes müssen einem erklärten Ergebnis zugeordnet sein; alle eigenen Prozesse und Sessions müssen nachweisbar beendet sein. Falls eine spätere Demo Instanzkonfiguration ändert, Ausgangswerte sichern und vollständig zurücknehmen. max worker threads nicht allein aufgrund hoher Belegung ändern; zuerst Ursachen wie Blocking, lange Anforderungen und Parallelität prüfen.
- Versionen, Edition, Plattform und Diagnoseberechtigungen vor späterer Ausführung festlegen. Die Scheduler-Sicht benötigt unter SQL Server 2019 VIEW SERVER STATE und ab SQL Server 2022 VIEW SERVER PERFORMANCE STATE (Berechtigungen zum Lesen instanzweiter Diagnoseinformationen). Die im Szenario aufgeführten Versionen 2019, 2022 und 2025 sind durch diese Quellensichtung nicht praktisch abgenommen.
- Qualitative Erklärungen benötigen keinen pauschalen neuen Benchmark (systematischen Leistungsvergleich). Mess- oder Leistungsbehauptungen benötigen passende Evidenz. L (groß) bleibt eine vorläufige Aufwandseinschätzung; eine spätere Umsetzung und SQL-/Lab-Ausführung benötigen einen eigenen Auftrag.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Worker-Warteschlange, CPU-Warteschlange und Diagnoseberechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-schedulers-transact-sql?view=sql-server-ver17), [Microsoft: Worker-Zuordnung, effektive Grenzen und Konfigurationshinweise](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-the-max-worker-threads-server-configuration-option?view=sql-server-ver17), [Microsoft: THREADPOOL und Grenzen kumulativer Wartezähler](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-wait-stats-transact-sql?view=sql-server-ver17), [Microsoft: besondere Administratorverbindung und ihre Grenzen](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/diagnostic-connection-for-database-administrators?view=sql-server-ver17).

**Spätere Abnahme:**

- Begründete Curriculumlücke oder Verzicht festhalten; Druck und Erschöpfung eindeutig unterschiedlich benennen.
- Behauptete Worker-Erschöpfung benötigt tatsächliche Thread-/Warte-Evidenz; aktive Sessions oder hohe Prozessorlast allein genügen nicht. Begrenzte Steuerung und gesicherter Abbau sind Voraussetzung.

##### 8. RES-003 – Lückenprüfung für Buffer-Pool-Druck und Resource Governor

**P2 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand L – vorläufig.**

**Planungsentscheidung:** Inhaltlich aufteilen; instanzweiten Speicherdruck zurückstellen.

**Begründung:** Datenseiten im Cache sind kein Drucknachweis. Cachegrundlagen liegen in STL-006 (Buffer Pool; Datenseiten-Cache). Resource Governor steuert Ressourcenpools; seine hier relevanten Grenzen betreffen Abfragearbeitsspeicher und verdienen eine eigene Erklärung statt der falschen Buffer-Pool-Zuordnung.

**Abhängigkeiten:**

- Cachegrundlagen bei STL-006 belassen; vorhandene RES-003-Kennung erhalten, keine neue Demo registrieren.
- Resource-Governor-Erklärung fachlich nach RES-004 (Abfragespeicherzuteilungen) einordnen. Für spätere ausführbare Poolbegrenzung Edition, Version, Klassifizierung, Wirksamkeit und vollständige Rücknahme mit INF-005 (Ressourcenlimits) klären.

**Wiederaufnahmebedingung:** Resource-Governor-Erklärung bei bestätigter Curriculumlücke; ausführbarer Instanzdruck erst nach eigenem Sicherheits- und Drucknachweiskonzept. Keine zusätzliche allgemeine Cache-Demo.

**Quellen:** `LAB-MEM-002` (Bounded buffer-pool pressure; begrenzter Druck auf den Datenseiten-Cache); `LAB-MEM-003` (Resource Governor pool limit; Begrenzung eines Ressourcenpools).

**Abgrenzung:** RES-003 trennt Instanzspeicherdruck von Query Execution Memory (Abfragearbeitsspeicher); STL-006 behandelt den Buffer Pool. Resource Governor (Steuerung von Ressourcenpools) nur bei neuem Lernziel ergänzen; notwendige Limits berühren INF-005.

**Weiterer Prüfauftrag:** LAB-MEM-002 gemäß aktuellem Katalog als Buffer-Pool-Druck einordnen; ältere Overgrant-Zuordnung verwerfen. Bei Resource Governor Edition, Version, Klassifizierung, Poolgrenzen und sicheren Restore prüfen.

**Statischer Quellenbefund:** Stand `ffb8ffa48b48fac025f47a2caea514c2f09d66ed`, erfasst am 2026-10-23. LAB-MEM-002 (Buffer-Pool-Druck; Druck auf den Datenseiten-Cache) legt eine Tabelle mit 32768 Zeilen und je 8000 Zeichen Nutzlast an. Zwei vorgesehene Worker lesen sie wiederholt mit jeweils einem 18-Sekunden-Zeitbudget. LAB-MEM-003 (Resource-Governor-Poolgrenze; Begrenzung eines Ressourcenpools) konfiguriert einen Pool mit MAX_MEMORY_PERCENT = 25 und eine Workloadgruppe mit REQUEST_MAX_MEMORY_GRANT_PERCENT = 10; sein Runbook startet null Worker. Das sind statisch gelesene Abläufe, keine beobachteten Druck- oder Begrenzungseffekte.

- LAB-MEM-002 verlangt in Observe.sql lediglich mindestens 16384 zwischengespeicherte Seiten der synthetischen Datenbank. Eine Vorhermessung, Verdrängung, physische Nachlesevorgänge oder tatsächliche Speicherdrucksignale werden nicht verlangt. Aus dem Code ist ableitbar, dass bereits das Befüllen der Tabelle den Cachebelegungsnachweis erfüllen könnte; dies wurde nicht ausgeführt. Cachebelegung ist kein Nachweis eines Speicherengpasses.
- Der aktuelle Katalog ordnet LAB-MEM-002 dem Buffer-Pool-Druck zu; der ältere Lernpfad nennt dagegen überdimensionierte Grants (zu hohe Abfragespeicherzuteilungen). Für die Zuordnung gelten aktueller Katalog und tatsächliche Bausteine. Die Kennzeichnung EMULATED_INFRASTRUCTURE (nachgebildete Infrastrukturbedingungen) ist keine Laufzeitqualifikation.
- USP_BufferPoolAnalysis liefert bei erkannten Prozessspeicherdrucksignalen oder wartenden Abfragespeicherzuteilungen AVAILABLE_WITH_FINDING (verfügbar mit Befund). Observe.sql weist diesen Status zurück; auch die Szenariodefinition erwartet nur AVAILABLE oder AVAILABLE_LIMITED. Ein tatsächlicher Befund könnte deshalb die Szenarioauswertung scheitern lassen. Diese Schlussfolgerung stammt aus dem Codevergleich, nicht aus einem Lauf.
- LAB-MEM-003 prüft nur das Vorhandensein der benannten Gruppe im benannten Pool und REQUEST_MAX_MEMORY_GRANT_PERCENT = 10. Die konfigurierte Poolgrenze von 25 Prozent, klassifizierte eigene Sessions und eine tatsächlich wirksame Begrenzung unter Last werden nicht nachgewiesen. Im Szenario fehlt eine Klassifizierungsfunktion zur Zuordnung neuer Verbindungen; ohne vorhandene Klassifizierung landen Benutzersessions gemäß Produktvertrag in der default-Gruppe. Null Worker und das Katalogmerkmal REAL (als reales Szenario eingeordnet) belegen keine wirksame Ressourcenbegrenzung.
- Bei normalen, nicht speicheroptimierten Tabellen begrenzen MIN_MEMORY_PERCENT und MAX_MEMORY_PERCENT den Query Execution Memory (Abfragearbeitsspeicher). Der Buffer Pool mit Daten- und Indexseiten wird gemeinsam genutzt und dadurch nicht begrenzt. Resource Governor darf deshalb nicht als Buffer-Pool-Obergrenze erklärt werden. MAX_CPU_PERCENT = 50 ist zudem eine weiche Prozessorgrenze bei Konkurrenz, keine harte Begrenzung.
- Beide Definitionen nennen jeweils zwei Analyzer, der generische Ablauf ruft nur den jeweiligen PrimaryAnalyzer (vorrangig ausgewählte Diagnoseprozedur) auf. Beide verwendeten Analyzer besitzen keinen Datenbank- oder Sessionfilter. Die Buffer-Pool-Verteilung ist im Buffer-Pool-Analyzer standardmäßig ausgeschaltet und wird vom Aufrufpfad nicht eingeschaltet. Beim Resource-Governor-Analyzer fehlt @StatusCodeOut; Observe.sql ersetzt den nicht gelieferten Status durch AVAILABLE (verfügbar). Die konfigurierte Befundhülle und MinimumConfidence = HIGH (hohe Mindestzuverlässigkeit) werden nicht aus einem passenden fachlichen Analyzerbefund nachgewiesen.
- Setup speichert den vorherigen Aktivierungszustand von Resource Governor. Cleanup (sicheres Aufräumen) deaktiviert die Funktion instanzweit, entfernt die festen Gruppen-/Poolnamen, wendet die Konfiguration erneut an und deaktiviert sie wieder, falls sie vorher ausgeschaltet war. Die Rücknahme ist damit grundsätzlich vorgesehen, aber kein bewiesener vollständiger Restore. Ein fehlender Datenbank-Eigentumsmarker wird durch IF @DatabaseOwner <> @LabRunId wegen NULL nicht sicher abgewiesen; die bereits erfassten Grenzen der Variablenübergabe und festen Objektnamen bleiben bestehen.

Quellen: [Lab/Scenarios/Performance/_Shared/Setup.sql:160](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Setup.sql:184](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Worker.sql:83](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Worker.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:65](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:75](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:624](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Observe.sql:915](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Observe.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/160_USP_BufferPoolAnalysis.sql:21](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/160_USP_BufferPoolAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/08_ServerHealth/160_USP_BufferPoolAnalysis.sql:216](https://api.github.com/repositories/1302553964/contents/Code/08_ServerHealth/160_USP_BufferPoolAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/07_Infrastructure/030_USP_ResourceGovernorAnalysis.sql:33](https://api.github.com/repositories/1302553964/contents/Code/07_Infrastructure/030_USP_ResourceGovernorAnalysis.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-MEM-002/runbook.json:16](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-002/runbook.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/LAB-MEM-003/runbook.json:16](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/LAB-MEM-003/runbook.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/LEARNING_PATH.md:41](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/LEARNING_PATH.md?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Setup.sql:62](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Setup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:82](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Performance/_Shared/Cleanup.sql:119](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Performance/_Shared/Cleanup.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

Abgleich mit der Schulung: [STL-006: geplanter Buffer-Pool-, Cold/Warm- und Read-Vergleich](https://github.com/gecompat/SQL_PerformanceSchulung/blob/17fd242f55b32bcae80918da3c848bbbc3e5fd3a/Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md#L903), [RES-004: geplanter Umfang für Abfragespeicherzuteilungen und Wartebeobachtung](https://github.com/gecompat/SQL_PerformanceSchulung/blob/17fd242f55b32bcae80918da3c848bbbc3e5fd3a/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L69), [RES-003: getrennter Umfang auf einer dedizierten Wegwerfinstanz](https://github.com/gecompat/SQL_PerformanceSchulung/blob/17fd242f55b32bcae80918da3c848bbbc3e5fd3a/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L75), [INF-005: bedarfsabhängige Prozessor- und Arbeitsspeicherlimits](https://github.com/gecompat/SQL_PerformanceSchulung/blob/17fd242f55b32bcae80918da3c848bbbc3e5fd3a/Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md#L1035).

**Vor einer späteren Umsetzung erforderlich:**

- Lernzuwachs oder begründeten Verzicht dokumentieren: STL-006 umfasst Buffer Pool, Cold/Warm Cache und logische/physische Reads; RES-004 umfasst Abfragespeicherzuteilungen und konkurrierende Grants. RES-003 bleibt der getrennte Umfang für isolierten Instanzspeicherdruck. Resource Governor nur mit eigenständigem Lernziel ergänzen; notwendige Ressourcenlimits gehören zum bedarfsabhängigen INF-005-Umfang.
- Für eine spätere Druckdemo Ressourcenprofil, Arbeitsmenge, Zeitbudget und eigene Beobachtungsphase ausdrücklich festlegen. Eine passende Vorher-/Last-/Erholungsbeobachtung und Gegenprobe müssen den behaupteten Druck oder Cacheeffekt tragen; Seitenzahl allein genügt nicht. Instanzspeicherdruck, Cachebelegung und RESOURCE_SEMAPHORE (Warten auf Abfragespeicher) getrennt ausweisen. Bei ausbleibendem Effekt kontrolliert abbrechen oder den Effekt als nicht demonstrierbar kennzeichnen.
- Falls eine wirksame Resource-Governor-Begrenzung gezeigt werden soll, eigene neue Verbindungen gezielt klassifizieren und ihre tatsächliche Gruppen-/Poolzuordnung prüfen. Wirksame Konfiguration und passende Laufzeitwerte mit begrenzter Last vergleichen; bloß angelegte Katalogeinträge genügen dafür nicht. Abfragearbeitsspeicher, Buffer Pool und weiche gegenüber harten Prozessorgrenzen verständlich trennen.
- Statusvertrag und fachlichen Befund vor späterer Adaption zusammenführen: AVAILABLE_WITH_FINDING ausdrücklich behandeln, eigene relevante Diagnosedaten auswerten und keine Erfolgsaussage aus konfigurierten Befundcodes oder einem ersetzten Status ableiten. Die Beobachtung muss zur Behauptung passen; Analyzer- und Szenariostatus ersetzen keine Druckmessung.
- Edition, Version, Rechte und Plattform vor Ausführung festlegen: Resource Governor ist in SQL Server 2019/2022 für Enterprise und Developer verfügbar; SQL Server 2025 ergänzt Standard und Standard Developer neben Enterprise und Enterprise Developer. Die Buffer-Descriptor-Sicht benötigt unter SQL Server 2019 VIEW SERVER STATE und ab 2022 VIEW SERVER PERFORMANCE STATE (Berechtigungen zum Lesen instanzweiter Diagnoseinformationen). Die Versionsliste der Szenarien ist keine praktische Abnahme.
- Nur eine dedizierte Wegwerfinstanz mit festem Ressourcenprofil, hartem Zeitbudget, Notabbruch und überprüfbarer Erholung vorsehen. Vorherige wirksame Konfiguration und gegebenenfalls Klassifizierung sichern und vollständig wiederherstellen; vollständige Eigentumsmarker und Schulungsverträge für Sessionsteuerung, Cleanup und Abbruch anwenden. Allgemeine Lab-Infrastruktur bleibt in SQL_Server_Lab; den Analyze-Runner nicht übernehmen.
- Qualitative Erklärungen benötigen keinen pauschalen neuen Benchmark (systematischen Leistungsvergleich). Mess- und Leistungsbehauptungen benötigen passende Evidenz. L (groß) bleibt eine vorläufige Aufwandseinschätzung; Umsetzung, SQL- und Lab-Ausführung benötigen einen eigenen Auftrag.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Cachebelegung und Diagnoseberechtigungen](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-os-buffer-descriptors-transact-sql?view=sql-server-ver17), [Microsoft: Abfragearbeitsspeicher, Buffer Pool und Prozessorgrenzen](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/resource-governor-resource-pool?view=sql-server-ver17), [Microsoft: Klassifizierung neuer Verbindungen](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/resource-governor-classifier-function?view=sql-server-ver17), [Microsoft: Resource Governor und Editionsgrenzen](https://learn.microsoft.com/en-us/sql/relational-databases/resource-governor/resource-governor?view=sql-server-ver17).

**Spätere Abnahme:**

- Abfragespeicher und Datenseiten-Cache fachlich getrennt behandeln; tatsächlich fehlendes Lernziel oder Verzicht dokumentieren.
- Bei einer späteren Übung tatsächlichen Druck beziehungsweise wirksame Poolbegrenzung passend nachweisen und alle Instanzänderungen sicher zurücknehmen; allgemeine Infrastruktur bleibt extern.

##### 9. INF-006 – Log Shipping als gesonderten Infrastrukturumfang bewerten

**P3 · Quellensichtung mit Lücken abgeschlossen; Adaption offen · Aufwand XL – vorläufig, eigenständiger Infrastrukturumfang.**

**Planungsentscheidung:** Separater Infrastrukturentscheidung vorbehalten; nicht in die nächste Schulungswelle aufnehmen.

**Begründung:** Log Shipping erfordert mehrere Instanzen sowie Sicherungs-, Übertragungs- und Wiederherstellungspfade. LAB-LS-002 ist lediglich geplant; die gesichteten Bausteine sind keine geprüfte Störungs- oder Wiederanlaufübung. Aufwand bleibt XL (sehr groß), vorläufig.

**Abhängigkeiten:**

- Eigenständiges Lernziel gegenüber STL-008 und STL-009 (Transaktionslog und Commit-Batching; gebündelte Transaktionsabschlüsse) begründen.
- Topologie, Zuständigkeit, Kosten/Ressourcen, Eigentum, Rückstände, Störfall und sicherer Abbau mit SQL_Server_Lab festlegen; allgemeine Infrastruktur verbleibt dort.

**Wiederaufnahmebedingung:** Eigener menschlicher Infrastrukturauftrag mit begründetem Lernziel und Betriebsverantwortung; keine Abhängigkeit der vorherigen Kandidaten von Log Shipping.

**Quellen:** `LAB-LS-001` (Log Shipping; Sicherung, Kopieren und Wiederherstellen mit Rückstand); `LAB-LS-002` (Unterbrochene Log-Shipping-Übertragung; laut Katalog noch geplant).

**Abgrenzung:** INF-006 enthält bereits begründete Mehrinstanz- und Netzwerktopologien. STL-008 und STL-009 behandeln das Transaktionslog und Commit-Batching; daraus folgt keine Log-Shipping-Infrastrukturfreigabe.

**Weiterer Prüfauftrag:** Lernziel, Mehrinstanztopologie, Sicherungs-/Übertragungs-/Restorepfad und insbesondere den geplanten Status von LAB-LS-002 prüfen; Aufwand und Zuständigkeit mit SQL_Server_Lab abgrenzen.

**Statischer Quellenbefund:** Stand `ffb8ffa48b48fac025f47a2caea514c2f09d66ed`, erfasst am 2026-10-23; ergänzende Infrastrukturquelle SQL_Server_Lab `2423ac75d7b07d29adbb63a2c218a6669db8363c`. LAB-LS-001 (Log Shipping; Sicherung, Kopieren und Wiederherstellen mit Rückstand) enthält einen eigenen Infrastrukturablauf für CTR-PAIR (zwei SQL-Server-Container), das Quellenprofil Standard und Linux. Er sieht SQL Server Agent (Jobsteuerung), eine primäre Datenbank im vollständigen Wiederherstellungsmodell, eine zweite Datenbank in NORECOVERY (bereit für weitere Wiederherstellungen), drei Agent-Jobs sowie Transferdateien vor. Nach einem vorgesehenen erfolgreichen Sicherungs-/Kopier-/Restorezyklus folgt eine weitere Sicherung ohne erneutes Kopieren oder Wiederherstellen. LAB-LS-002 (unterbrochene Übertragung) ist weiterhin nur geplant. Dies ist eine statische Quellenbeschreibung, kein ausgeführter Zyklus oder Laufzeitnachweis.

- LAB-LS-001 ist im Katalog als IMPLEMENTED_ACTIONS_GATE (vorhandene Aktionsbausteine) und REAL (als reales Szenario eingeordnet) geführt; Szenariodefinition, Runbook und acht SQL-Dateien sind vorhanden. Die Definition nennt SQL Server 2019, 2022 und 2025 sowie native Plattformnachweise als externes Gate. LAB-LS-002 ist dagegen PLANNED_NOT_IMPLEMENTED (geplant, nicht implementiert); am geprüften Stand fehlt seine Szenariodefinition. Daraus folgt keine praktische Versions- oder Störfallabnahme.
- Der eigene Infrastrukturpfad prüft neue Agent-Jobhistorieneinträge für den jeweiligen Job mit step_id = 0 (Gesamtergebnis) und run_status = 1 (erfolgreicher Jobabschluss). Jeder Joblauf besitzt ein 120-Sekunden-Zeitbudget. Anschließend müssen die zuletzt gesicherte, kopierte und wiederhergestellte Datei im vorgesehenen gesunden Zyklus denselben Dateinamen tragen. Der Vertrag enthält damit konkrete Job- und Dateibeziehungen; diese wurden in der Sichtung nicht ausgeführt.
- Der Rückstand wird absichtlich durch einen zweiten Backupzyklus ohne nachfolgenden Copy-/Restorezyklus erzeugt. Die neue Sicherungsdatei muss von der vorherigen abweichen; kopierte und wiederhergestellte Datei müssen auf dem vorherigen Stand bleiben. Das ist eine begrenzte Diagnose eines ausstehenden Verarbeitungsschritts, kein Nachweis eines Netzwerkfehlers, einer anschließenden Störungsbehebung oder automatischen Failovers. Minutenwerte dürfen dabei null bleiben; eine exakte Verzögerung oder Übertragungsleistung wird nicht nachgewiesen.
- USP_LogShippingStatus liest Konfiguration und Monitorzustände ohne Datenbankfilter. Der Infrastrukturpfad wählt aus Primary- und Secondary-Ergebnissen jeweils die erste Zeile statt einer eindeutigen Zuordnung zur synthetischen Datenbank und ihrer Serverbeziehung. Er vergleicht Dateinamen, nicht wiederhergestellte Nutzdaten oder Dateiinhalte. BackupChain-Summary mit mindestens einer Zeile bedeutet Sichtbarkeit, keine bestätigte intakte Sicherungskette. Der Code kann damit keine vollständige Wiederherstellbarkeitsprüfung ersetzen.
- Der Runner prüft registrierte Containerkennungen und Analyze-eigene Labels; das Transferverzeichnis erhält einen Lauf-/Szenariomarker mit Pfadgrenzenprüfung beim Löschen. Die SQL-Bereinigung entfernt Datenbank, Jobs und Log-Shipping-Metadaten jedoch anhand fester Namen und Beziehungen, ohne deren Laufzugehörigkeit zu prüfen. Der in der Primärdatenbank vorhandene Datenmarker wird vor dem Löschen nicht ausgewertet. Die initiale Bereinigung läuft bereits vor Setup; Containerzugehörigkeit ersetzt keinen Eigentumsnachweis für darin vorhandene SQL-Objekte.
- Im finally-Block (abschließende Bereinigung) stehen Secondary-Cleanup, Primary-Cleanup und Dateiabbaumethode in derselben try-Sequenz. Schlägt die erste Bereinigung fehl, werden die nachfolgenden Schritte übersprungen; der Fehler wird gemeldet. Ein umfassender unabhängiger Abwesenheitsnachweis für Datenbank, Jobs, Metadaten und Transferdateien ist damit noch nicht gegeben.
- Der alte Analyze-Provisionierer erwartet Lab/Containers/wave4.compose.yaml sowie Lab/Config/resource-profiles.json. Beide Dateien fehlen am geprüften Commit und im damals gelesenen Checkout. Der bisherige Bereitstellungspfad ist dadurch nicht als eigenständig lauffähiger Umfang belegt. Seine Registry-, Rollen- und Eigentumsverträge sind zudem nicht direkt mit SQL_Server_Lab austauschbar; der Analyze-Runner wird nicht zur Übernahme freigegeben.
- SQL_Server_Lab aktiviert SQL Server Agent bereits in seinen Docker- und Podman-Containerprovidern und führt eigene Lauf-, Scope- und Instanzlabels. Seine Architekturdokumentation behandelt Log Shipping als eigene zusammengesetzte SQL-Topologie. Das belegt vorhandene Infrastrukturbausteine und die Zuständigkeit, aber keine abgenommene Log-Shipping-Gesamttopologie. Transferpfade, Berechtigungen, Ressourcenprofile und Zustandsanbindung müssen für einen späteren Schulungsfall konkret zugeordnet werden.

Quellen: [Lab/Scenarios/Infrastructure/LAB-LS-001/scenario.json:15](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/scenario.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/runbook.json:11](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/runbook.json?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Setup_Primary.sql:25](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Setup_Primary.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Setup_Secondary.sql:12](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Setup_Secondary.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Primary_Backup_Cycle.sql:18](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Primary_Backup_Cycle.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Secondary_Copy_Restore_Cycle.sql:34](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Secondary_Copy_Restore_Cycle.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Observe_Primary.sql:7](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Observe_Primary.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Observe_Secondary.sql:4](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Observe_Secondary.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/07_Infrastructure/060_USP_LogShippingStatus.sql:26](https://api.github.com/repositories/1302553964/contents/Code/07_Infrastructure/060_USP_LogShippingStatus.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Code/07_Infrastructure/060_USP_LogShippingStatus.sql:71](https://api.github.com/repositories/1302553964/contents/Code/07_Infrastructure/060_USP_LogShippingStatus.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:345](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:382](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:412](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:450](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1:479](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/InfrastructureScenarioRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Cleanup_Primary.sql:23](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Cleanup_Primary.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Scenarios/Infrastructure/LAB-LS-001/Cleanup_Secondary.sql:8](https://api.github.com/repositories/1302553964/contents/Lab/Scenarios/Infrastructure/LAB-LS-001/Cleanup_Secondary.sql?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/MultiContainerRuntime.ps1:61](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/MultiContainerRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/MultiContainerRuntime.ps1:246](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/MultiContainerRuntime.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed), [Lab/Orchestration/Modules/DiagnosticLab/Private/ResourceMeasurement.ps1:43](https://api.github.com/repositories/1302553964/contents/Lab/Orchestration/Modules/DiagnosticLab/Private/ResourceMeasurement.ps1?ref=ffb8ffa48b48fac025f47a2caea514c2f09d66ed).

Abgleich mit der Schulung: [INF-006: Mehrinstanz- und Netzwerktopologien nur nach fachlicher Begründung](https://github.com/gecompat/SQL_PerformanceSchulung/blob/f20fff956858d769e823acdef4fc28d41b2511af/Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md#L1039), [Zuständigkeit: Lab-Lifecycle und Infrastruktur gegenüber Schulungsablauf und Abnahme](https://github.com/gecompat/SQL_PerformanceSchulung/blob/f20fff956858d769e823acdef4fc28d41b2511af/Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md#L54), [STL-008: vorhandene Demo für virtuelle Logabschnitte und Logwachstum](https://github.com/gecompat/SQL_PerformanceSchulung/blob/f20fff956858d769e823acdef4fc28d41b2511af/Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth/README.md#L1), [STL-009: vorhandene Demo für Commit-Batching und Logschreibvorgänge](https://github.com/gecompat/SQL_PerformanceSchulung/blob/f20fff956858d769e823acdef4fc28d41b2511af/Demos/01_Storage_Pages_Log/STL-009_Commit_Batching/README.md#L1).

Ergänzende Infrastrukturquellen am gebundenen Lab-Stand: [Lab-Dockerprovider: Agent-Aktivierung und eigene Ressourcenlabels](https://github.com/gecompat/SQL_Server_Lab/blob/2423ac75d7b07d29adbb63a2c218a6669db8363c/Providers/Docker/DockerProvider.ps1#L456), [Lab-Podmanprovider: Agent-Aktivierung](https://github.com/gecompat/SQL_Server_Lab/blob/2423ac75d7b07d29adbb63a2c218a6669db8363c/Providers/Podman/PodmanProvider.ps1#L343), [Log Shipping als zusammengesetzte SQL-Topologie mit eigenen Pfaden und Assertions](https://github.com/gecompat/SQL_Server_Lab/blob/2423ac75d7b07d29adbb63a2c218a6669db8363c/Documentation/Architecture/FUTURE_USE_CASES_AND_EXTENSION_GUARDRAILS.md#L89).

**Vor einer späteren Umsetzung erforderlich:**

- Eigenständiges Lernziel und Infrastrukturdesign für INF-006 begründen oder auf eine zusätzliche Demo verzichten. STL-008 (VLF, Virtual Log Files; virtuelle Abschnitte im Transaktionslog, und Logwachstum) und STL-009 (Commit-Batching und Logschreibvorgänge) behandeln bereits das Transaktionslog; daraus folgt kein Mehrinstanz- oder Log-Shipping-Lernziel. Allgemeine Bereitstellung und Betrieb bleiben in SQL_Server_Lab; Lernablauf, Beobachtung und fachliche Abnahme gehören zur Schulung.
- Zwei isolierte Instanzen, unterstützte Kombination aus SQL-Version, Edition und Betriebssystem, Agent-Betrieb, Initialsicherung und durchgängige Sicherungs-/Transfer-/Restorepfade festlegen. Lauf-, Rollen- und Zustandsbindung an SQL_Server_Lab, Verzeichnisberechtigungen, Speicherkapazität sowie harte Zeit- und Ressourcenbudgets nachweisen. Das gleichnamige Quellenprofil Standard nicht ungeprüft mit einem Lab-Profil gleichsetzen.
- Konfiguration und Beobachtung eindeutig an die eigene Datenbank, beide Serverrollen und die tatsächlich gestarteten Jobs binden. Für die behauptete Aussage passende Jobhistorie, Sicherungs-/Kopier-/Restoredateien und gegebenenfalls Ketten- oder Datenstandnachweise kombinieren. Ein sichtbarer Monitorwert, erste Ergebniszeile, AVAILABLE (Diagnose verfügbar) oder eine vorhandene Summary-Zeile reichen nicht für eine umfassende Wiederherstellbarkeitsbehauptung.
- Normalbetrieb, absichtlich ausstehende Verarbeitung und echten Störfall getrennt festlegen. Für eine spätere Übertragungsstörung Fehlergrenze, begrenzten Eingriff, passenden Nachweis sowie Wiederanlauf und Aufholen des Rückstands definieren. LAB-LS-002 besitzt dafür noch keine implementierten Bausteine. Log Shipping bietet keinen automatischen Failover; ein gegebenenfalls gewünschter Rollenwechsel erhält einen eigenen Ergebnis- und Wiederaufbauvertrag.
- Vor jedem Reset und Cleanup (sicheres Aufräumen) vollständige SQL-Eigentumsmarker und genaue Objektkennungen prüfen. Bestehende fremde Datenbanken und Jobs müssen zur Abweisung führen. Alle Rollen und Transferdateien auch nach Teilschrittfehlern kontrolliert behandeln; anschließend Abwesenheit beziehungsweise gesicherten Recoverybedarf unabhängig feststellen. Containerlabels und ein Dateimarker allein erfüllen den Schulungsvertrag für SQL-Objekte nicht.
- Produktvoraussetzungen und Aussagegrenzen dokumentieren: Log Shipping benötigt das vollständige oder massenprotokollierte Wiederherstellungsmodell sowie erreichbare Sicherungsdateien; die Einrichtung über die dokumentierten Prozeduren erfordert sysadmin (feste Serverrolle mit Verwaltungsrechten). SQL Server Agent muss auf beiden Instanzen verfügbar sein. Falls später ein entfernter Monitor oder gemischte Versionen vorgesehen werden, die SQL-Server-2025-Verschlüsselungs- und Monitorgrenzen gesondert prüfen.
- Qualitative Erklärungen benötigen keinen pauschalen neuen Benchmark (systematischen Leistungsvergleich). Behauptete Übertragungszeiten, Wiederherstellungsziele oder Leistungswerte brauchen passende Evidenz. P3 (gesonderte Infrastrukturentscheidung) und XL (sehr großer Aufwand) bleiben vorläufig; weitere Umsetzung oder SQL-/Lab-Ausführung benötigt einen eigenen Auftrag.

Produktdokumentation, gelesen am 2026-10-23: [Microsoft: Log Shipping unter Linux und Agent-Voraussetzungen](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-use-log-shipping?view=sql-server-ver17), [Microsoft: Wiederherstellungsmodell, Rechte und Versionsgrenzen](https://learn.microsoft.com/en-us/sql/database-engine/log-shipping/configure-log-shipping-sql-server?view=sql-server-ver17), [Microsoft: Backup-/Copy-/Restoreablauf und manueller Rollenwechsel](https://learn.microsoft.com/en-us/sql/database-engine/log-shipping/about-log-shipping-sql-server?view=sql-server-ver17).

**Spätere Abnahme:**

- Eigenständige fachliche und Infrastrukturentscheidung mit Zuständigkeit, Ressourcenbedarf und realistischem Abnahmeumfang; keine Einstufung als kleine Szenarioübernahme.
- Allgemeine Bereitstellung und Betrieb bleiben in SQL_Server_Lab. Eine spätere Schulungsintegration benötigt passende Nachweise für Übertragungs-/Restore-Rückstand, Störfall und vollständig sicheren Abbau.

<!-- REGISTRY_BACKLOG_TSK_016:END -->

## Wiederaufnahme vom 22. Oktober 2026: Eigentumsprüfungen zuerst

Der neue menschliche Auftrag autorisiert die vollständige Korrektur der
22 Cleanup-Eigentumskandidaten einschließlich Tests, Dokumentation und
Integration per Pull Request nach `origin/main`. Anschließend wird autonom mit
den nächsten priorisierten Punkten fortgefahren; der historische Arbeitsstopp
unten ist aufgehoben. Es wurde keine Automation aktiviert.

1. Die bestätigte Fehlerklasse in allen 22 Cleanupquellen ist abgeschlossen;
   der verlinkte Ausführungsstand führt Integration und tatsächliche Nachweise.
   FWK-002 bezeichnet den Schutzvertrag für synthetische Testdatenbanken.
2. Zehn weitere Setups sind über PR297, der Markerschutz der Frameworkreferenz
   über PR299 vollständig geprüft und integriert. Als Nächstes vollständige
   Rohparameter vor der Namens- und Aktionsableitung prüfen, danach Recovery
   bei fehlgeschlagener Erstmarkierung.
   Recovery bedeutet Wiederherstellung nach einem Fehler oder Abbruch.
3. Anschließend vollständige menschliche Lesepfade und gezieltere Testauswahl
   bearbeiten. Teilnehmerpiloten benötigen eine tatsächliche Durchführung.

Verbindlicher Arbeitsstand, endlicher Aufgabenrahmen, Prüfgates und Grenzen:
[aktueller Ausführungsstand](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md). Der erste
[abgegrenzte Nachweis](../Documentation/Project_Planning/FWK_002_CLEANUP_OWNERSHIP_REVIEW.md)
enthält die 22 Quellen und die tatsächliche Evidenz. Eine Cleanupabnahme ist
keine globale Freigabe des gesamten Ausführungspfads.

## Aktuelle Priorität nach abgeschlossenem Foundation-Upgrade

Der Benutzerauftrag vom 22. Oktober 2026 beendet die autonome Fortsetzung nach
Abschluss der aktuellen Demos. PR293 schließt die letzte Demo-Implementierung
vollständig ab; der 30-Minuten-Heartbeat ist gelöscht. Offene Aufgaben unten
bleiben erhalten, werden in diesem Chat aber nicht begonnen. Eine Wiederaufnahme
erfordert einen neuen menschlichen Auftrag. Maßgeblich ist der
[Benutzerabschluss im Ausführungsstand](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md#benutzerabschluss-vom-22-oktober-2026-keine-autonome-fortsetzung).

- [x] Runner-Dateieinstieg und Profilbeobachtung: PR289 vollständig integriert, geprüft und eigene Branches bereinigt; der alte native Rahmen bleibt geschlossen.
- [x] Foundation 1.25.0: PR290 vollständig in Main `2f4c427b3da36ae3c5f24770aeaee75ce3488ea0`, unabhängig geprüft, lokale sowie Head-/Base-/Main-Gates grün, vollständige Übernahme und eigene Branchbereinigung. Head ist der geprüfte Pull-Request-Commit, Base dessen Main-Basis.
- [x] TSK-015 – Erster menschlicher Demo-Ausführungspfad: PR291 vollständig in Main `65089ac2c42a47fe961a1de7dc04d1e41da78f31`, unabhängiger Review, lokale Prüfungen, 48 Head-, fünf Base- und 46 frische Main-Prüfungen grün, Übernahme und eigene Branchbereinigung. Unsichere manuelle Löschanweisung und unbelegte Gesamtgarantie entfernt.
- [x] **FWK-002 – QRY-001-Cleanupkorrektur:** PR292 vollständig in Main `0558add5d2d030fd0b19829c5f8e4150ee05a234`, unabhängig geprüft, lokale positive und negative Gegenproben, 48 Head-, 46 Base- und 46 frische Main-Prüfungen grün, vollständige Übernahme und eigene Branchbereinigung. Vier Quellenstände/vier lokale Prüfläufe geschlossen; keine globale Frameworkabnahme.
- [x] **FWK-002 – QRY-001-Setupkorrektur:** Schutzvertrag für Testdatenbanken bei indexfreundlichen Suchbedingungen: PR293 vollständig in Main `6407a105e656bd0669c81a1921265c292dc622cd`, unabhängiger Ergebnisreview, lokale Gegenproben, 48 Head-, 46 Base- und 46 frische Main-Prüfungen grün. Vollständige Baumübernahme, Synchronisation und eigene lokale sowie Remote-Branchbereinigung bestätigt. Vier Quellenstände/vier lokale Prüfläufe geschlossen; keine globale Freigabe des Schutzvertrags.
- [ ] **FWK-002 – weitere Eigentumslücken:** Weitere 22 negative Cleanup-Markerbedingungen sind Textkandidaten aus 37 Cleanupdateien, noch keine vollständige Laufzeitqualifikation. Recovery nach gescheiterter erstmaliger Markierung einer neuen Datenbank bleibt offen. Durch den Benutzerabschluss zurückgestellt; Wiederaufnahme nur nach neuem menschlichem Auftrag mit begrenztem Schnitt und unabhängigem Review. Bis dahin nur eigene Wegwerfinstanz, nach Abbruch Daten erhalten.
- [ ] TSK-015 – Verbleibende menschliche Lesepfade: Historische Planungsabschnitte nach den priorisierten Eigentumslücken von aktueller Steuerung trennen, ohne Kennungen oder Nachweise zu entfernen. Verantwortlich ist die Dokumentationsrolle der Projektpflege mit unabhängigem Review. Jede wesentliche Änderung weiterer Lern- oder Präsentationspfade löst deren Prüfung mit notwendigen Folgeseiten aus. Keine pauschale Altbestandskonformität.
- [ ] Effizienz der Katalogselektoren: Die reine Katalogkorrektur löst bestehende SQL-Matrizen aus. Nach den Eigentumslücken eine kleinere, aus tatsächlichen Abhängigkeiten belegte Auswahl unabhängig prüfen; bestehende Qualifikationsgates und sicherer Cleanup bleiben bis dahin erhalten. Ein Implementierungsverantwortlicher, keine parallele Workflowkorrektur im aktuellen Schnitt.

Die folgenden datierten Einträge sind historische Teilstände. Für die aktuelle
Fortsetzung gilt der [Ausführungsstand](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md).

## Menschlicher Projekteinstieg und Lehrmaßstab vom 20. Oktober 2026

- [x] [README und menschliche Einstiege](../Documentation/Project_Planning/PROJECT_ENTRY_AND_TEACHING_SCOPE_REVIEW.md): PR264 in Main5bf9d14,13PR-/11Main-Checks SUCCESS, unabhängiger Review und FullTree/Sync/Branchcleanup. Keine allgemeine Benchmarkpflicht; erhaltene Archivquellen und historische Migrationskennzeichnungen klar eingeordnet.

## DGN-007: kontinuierlicher operativer Auftrag vom 20. Oktober 2026

- [x] Vollständiger deklarativer SESSION_END-Matcher aus PR259: Main `d4151093bdd4de115b660352345f3e5c47e9b650`, acht PR-/sechs Main-Gates grün, FullTree/Sync/Branchcleanup bestätigt.
- [x] [Operativer Abschlussweg](../Documentation/Project_Planning/DGN_007_NATIVE_SESSION_CHANNEL_REVIEW.md): PR260 in Main256e43d, acht PR-/sechs Main-Gates SUCCESS, native16/16 ohne SKIP, FullTree/Sync/Branchcleanup bestätigt. Historische C3-FAIL und ausdrückliche C4-Freigabe erhalten.
- [x] [Gehaltener Handshakeeingang](../Documentation/Project_Planning/DGN_007_HANDSHAKE_INPUT_PLAN_REVIEW.md): PR261 in Main0d851dc, acht PR-/sechs Main-Gates SUCCESS,16/16 neue Methoden Windows/Linux/Main ohne SKIP, unabhängiger Review und FullTree/Sync/Branchcleanup; ein Quellenstand, keine Nachläufe.
- [x] [Nativer bidirektionaler Phasenowner](../Documentation/Project_Planning/DGN_007_BIDIRECTIONAL_HANDSHAKE_REVIEW.md): PR262 in Main9938091, zehn PR-/acht Main-Gates SUCCESS, neue12/alte Kanal16/pure Eingangsplan16 ohne SKIP in CI/Main, unabhängiger Review und FullTree/Sync/Branchcleanup. Ein Quellenstand, keine Nachläufe; echte Import-/Loaderclaims offen.
- [x] [Vollständige Profilauswahl an lokale Anker](../Documentation/Project_Planning/DGN_007_SELECTED_PROFILE_ANCHORS_REVIEW.md): PR263 in Main4a8d5aa, neun PR-/sieben Main-Gates SUCCESS, unabhängiger Review, FullTree/Sync/Branchcleanup; neue16 Windows/Linux und alte57 Linux ohne SKIP PASS. Historischer alter Windows57-Fixture-FAIL erhalten. Keine operative Aufnahme.
- [x] [Vorgewählte Profilanker und frische lokale Aufnahme](../Documentation/Project_Planning/DGN_007_SELECTED_PROFILE_OBSERVATION_REVIEW.md): PR265 Main966f225, zehn PR-/acht Main-Gates SUCCESS, unabhängiger Review und FullTree/Sync/Branchcleanup. Neue16/Binder16 Windows/Linux und alte57 Linux ohne SKIP PASS; keine operative Installation/Workerbaseline.
- [x] [Aktuelle vollständige Kontrollquelle im bestehenden Inlinegenerator](../Documentation/Project_Planning/DGN_007_CURRENT_CONTROL_SOURCE_FIT_REVIEW.md): PR266 Mainded09f6, sieben PR-/fünf Main-Gates SUCCESS, unabhängige Einordnung/FullTree/Sync/Branchcleanup. Vollständige alte Route bleibt SCRIPT_LIMIT/operativerFitFAIL; max3 geschlossen, kein Rerun oder Capwechsel.
- [x] [Workerquelle mit gebundener Profilaufnahme](../Documentation/Project_Planning/DGN_007_WORKER_PROFILE_SOURCE_REVIEW.md): PR267 Main84272af, zwölf PR-/zehn Main-Gates SUCCESS, unabhängiger Review, neue15 Windows/Linux und bestehende Consumer ohne SKIP PASS, FullTree/Sync/Branchcleanup. Keine operative Inventur oder Ausführung.
- [x] [Empfangene Metadata und tatsächlicher Workerreport](../Documentation/Project_Planning/DGN_007_OBSERVED_WORKER_REPORT_REVIEW.md): PR268 Maindcc5893, dreizehn PR-/elf Main-Gates SUCCESS, neue16/alte15 ohne SKIP PASS, unabhängige Schließung, FullTree/Sync/eigene Branches bereinigt. Vier Sourcekandidaten/drei Nachläufe, operative Claims offen.
- [x] [Workerquelle für vollständige Eingangsfolge](../Documentation/Project_Planning/DGN_007_WORKER_INPUT_SOURCE_REVIEW.md): PR269 Maine456c53, neun PR-/sieben Main-Gates SUCCESS, neue16 Windows/Linux/Main und Report16 ohne SKIP PASS, unabhängige Befundschließung/FullTree/Sync/eigene Branchbereinigung. Drei Kandidaten/zwei Nachläufe, voller Quellenfit/AST-/Literalerhalt; keine native Quellenwahl oder Inventur.
- [x] [Gemeinsame Child-I/O-Reserve vor Parentstart](../Documentation/Project_Planning/DGN_007_CHILD_IO_RESERVATION_REVIEW.md): PR270 Main20549ae, zwölf PR-/zehn Main-Gates SUCCESS, neue12/Handshake12/28Native/Session16/Workerinput16 ohne SKIP PASS, unabhängiger Review/FullTree/Sync/eigene Branchbereinigung. Ein Sourcekandidat/keine Nachläufe; keine neue operative Quellenwahl oder SQL.
- [x] [Erste direkte Proxyquelleninvocation nach EOF](../Documentation/Project_Planning/DGN_007_PROXY_LOADER_SOURCE_REVIEW.md): PR271 Main3387e30, zehn PR-/acht Main-Gates SUCCESS, neue16/Eingangs16/Budget12 ohne SKIP PASS, unabhängige Befundschließung/FullTree/Sync/eigene Branchbereinigung. Sechs Kandidaten geschlossen; keine native/DGN-Raw-/SQL- oder Gesamtfreigabe.
- [x] [Verschachtelte Harness-Quellenfolge](../Documentation/Project_Planning/DGN_007_HARNESS_LOADER_SOURCE_REVIEW.md): PR272 Main4a165c2, neun PR-/sieben Main-Gates SUCCESS, neue Harness16/Proxy16 ohne SKIP PASS, unabhängige Befundschließung/FullTree/Sync/eigene Branchbereinigung. Vier Kandidaten/drei Nachläufe erfolgreich geschlossen, Verbrauch UNKNOWN; keine tatsächliche DGN-Raw-/Native-/Gesamtfreigabe.
- [x] [Codefreie Parentregistrierung](../Documentation/Project_Planning/DGN_007_CODEFREE_PARENT_REGISTRATION_REVIEW.md): PR273 Mainb00418c, neun PR-/sieben Main-Gates SUCCESS, Parent12/Harness16 ohne SKIP PASS, unabhängige Schließung/FullTree/Sync/eigene Branchbereinigung. Drei Kandidaten/zwei Nachläufe erfolgreich geschlossen. Tatsächliche operative Anbindungen und reale Gesamtgates offen.
- [x] [Runner-Quellenfit-Diagnose](../Documentation/Project_Planning/DGN_007_RUNNER_LOADER_SOURCE_REVIEW.md): PR274 vollständig Mainf30aebc, acht Head-/sieben Base-/sechs frische Main-Gates SUCCESS, unabhängige Schließung/FullTree/Sync/eigene Branchbereinigung. CLOSED_REJECTED_SOURCE_FIT, fünf/max6 Kandidaten, vier Nachläufe, Verbrauch UNKNOWN; keine neue Runnerquelle/Tests/CI zugelassen.
- [x] [Gemeinsamer Rootkontrollanker – Architekturplan](../Documentation/Project_Planning/DGN_007_RUNNER_SHARED_CONTROL_DESIGN.md): PR275 vollständig Main750844b, sieben Head-/sechs Base-/fünf frische Main-Gates SUCCESS, unabhängige Schließung/FullTree/Sync/eigene Branchbereinigung. DESIGNED, zwei/hartzwei Entwurfsstände geschlossen; keine Source-/Runtimeabnahme.
- [x] [Funktionaler Runnerabschluss](../Documentation/Project_Planning/DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md#abschluss-des-funktionalen-schnitts): PR281 vollständig in Main `f143c968f5fec26c60fcc8b32e8baac637fdbcd1`, unabhängiger Review ohne offene priorisierte Befunde, je 21 lokale Windows-/Linuxmethoden, aktuelle grüne PR-/Main-Prüfungen, vollständige Übernahme und eigene Branchbereinigung. Vollständige Profilfixture bei 129679/127911 Bytes unter unverändertem 131072-Limit; kein nativer Runtime- oder SQL-Nachweis. Historische C6-/C7-/C8-Ablehnungen und ihre damaligen Grenzen bleiben im Quellenreview erhalten, keine aktuellen neuen Sperren.
- [x] [Auswahlplan für frische Workerprofile](../Documentation/Project_Planning/DGN_007_WORKER_PROFILE_SELECTION_PLAN.md): PR282 vollständig in Main `e4b373d679ef2f8670913239664e55623cf7caaa`, unabhängiger Review, lokale Dokumentationsprüfungen, sieben Head-/drei Base-/fünf frische Main-Prüfungen grün, vollständige Übernahme und eigene Branchbereinigung. Ein Entwurfsstand, keine Nacharbeit; keine native Lauffreigabe.
- [x] [Quellenbegründetes Auswahlpaket mit bestehendem Poolvergleich](../Documentation/Project_Planning/DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#ergebnis-des-achten-standes-vollständiges-auswahlpaket): PR286 vollständig in Main `a714c7d578a18d2fa31fe862bc1e184ed1037444`, unabhängige Reviews ohne offene Befunde, alle 40 Datengegenproben, drei Fünfformenvergleiche und drei ursprüngliche Ganz-AST-/Fitmethoden bestanden; AST bezeichnet den abstrakten Syntaxbaum. Argument-/Provider-/Cleanupgegenproben bestanden, vier Jobs bereinigt, 22 Quellenpins bestätigt. Script- und Formgrenzen unverändert eingehalten. Sieben grüne Head-, fünf Base- und fünf frische Main-Prüfungen, vollständige Übernahme, Synchronisation und eigene Branchbereinigung. Acht/hart acht geschlossen, Verbrauch UNKNOWN; private Fehler erhalten, kein neunter Stand oder Retry. Keine Installation oder Linux-/Worker-/SQL-Ausführung, Runtime/Trust/Importbyte-/Methodennachweis offen.
- [x] [Plan für die erste native Runnerprofilaufnahme](../Documentation/Project_Planning/DGN_007_NATIVE_PROFILE_OBSERVATION_PLAN.md): PR287 vollständig in Main `3266c4763c0e452f8752cd792473308f87ef25df`, unabhängiger Review ohne offene Befunde, lokale Dokumentationsprüfung und aktuelle grüne Head-/Base-/Main-Gates, vollständige Übernahme und eigene Branchbereinigung. Ein Dokumentationsentwurf von höchstens zwei; keine native Ausführung oder Lauf-GO durch diesen Plan, alter Auswahlrahmen bleibt geschlossen.
- [ ] [Erste frische Runnerprofilaufnahme](../Documentation/Project_Planning/DGN_007_RUNNER_PROFILE_OBSERVATION_REVIEW.md#tatsächliches-ergebnis-des-dritten-standes): Runner ist die vollständige Ausführungssteuerung. Nach unabhängigem Quellen-/Test-/Aufruf-GO bestanden 19 portable Methoden und sechs native Gegenfälle ohne übersprungene Tests. Genau ein unveränderter Runnerstart endet vor jedem Profilreport mit EARLY_EOF (frühem Ausgabestromende); konkrete Ursache UNKNOWN, mit dieser Evidenz unbekannt. Eigener Cleanup, beide Datenstromabschlüsse, unabhängige Prozessabsenz und Wiederherstellung belegt, alle vier Windows-Jobs beendet. Drei/max6 Quellenstände, Checkpoint2, ein Prüflauf mit sieben synthetischen Prozessen; einziger ausgewählter Versuch ausgeschöpft, kein Retry oder neue Auswahl. Unabhängiger Ergebnisreview und lokale Dokumentationsprüfung abgeschlossen; [PR288](https://github.com/gecompat/SQL_PerformanceSchulung/pull/288) bindet den regulären Dokumentationsabschluss mit Gates und Übernahmenachweis. Weitere native Diagnose benötigt eine ausdrückliche neue Versuchsgrenze; kein Runtime-/Trust-/SQL-Nachweis.
- [ ] Frische vollständige Workerprofile und tatsächliche Quellenloader-/Importprovenienz belegen. Kontinuierlicher Auftrag und bestehender 30-Minuten-Heartbeat aktiv; ungelöste fachliche und operative Freigabegrenzen bleiben erhalten.
- [x] Menschliche Priorität vor der nächsten technischen Welle: README als Projekteinstieg mit Lernwegen/Unterlagen/Beispielen, interne Entwicklungsstände ausgelagert und erhaltenes Referenzarchiv erläutert. PR264 abgeschlossen; fehlende Messbarkeit ist kein allgemeines Ausschlusskriterium.

## VERTIEFUNG Kurswelle vom 18. Oktober 2026

- [x] VERTIEFUNG-Teilprodukt TSK-012: [Zweitageskurs mit 61 Folien](../Documentation/HowTo/SQL_SERVER_2025_AI_VERTIEFUNG_COURSE.md), vollständigem STANDARD-Tag, konkreten Tag-2-Beleg-/Entwurfsaufgaben und zentralen Musterlösungen; 840+120 Planminuten.
- [x] VERTIEFUNG-Teilprodukt TSK-014: [technische/redaktionelle Generalprobe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VERTIEFUNG_REHEARSAL.md), 16 SQL-Lifecycles/76 erfüllte Assertions, unabhängiger Cleanup, Tag-2-Rechen-/Belegprüfung und PowerPoint-Anwendungstest. Optionaler Full-Text-WARN bleibt erhalten.
- [ ] VERTIEFUNG-Teilnehmerpilot: tatsächliche Gruppe/Lehrperson, Verständlichkeit, Lernerfolg und Soll-/Ist-Zeiten beider Tage prüfen. Wiederaufnahme bei moderierter Durchführung; kein eigener offener Codebranch.

Der neue Benutzerauftrag betrifft dieses Kurspaket. Andere technische Wellen
und Automation bleiben pausiert; volle TSK-012-/TSK-014-/Streamfreigabe bleibt offen.

## STANDARD Kurswelle vom 18. Oktober 2026

- [x] STANDARD-Teilprodukt TSK-012: [45-Folien-Tageskurs](../Documentation/HowTo/SQL_SERVER_2025_AI_STANDARD_COURSE.md) mit acht Offline-Aufgaben, 420+60 Planminuten, Transfer, vorhandener Rubrik und sicherem Ausfallpfad.
- [x] STANDARD-Teilprodukt TSK-014: [technische und redaktionelle Generalprobe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_STANDARD_REHEARSAL.md), 16 SQL-Lifecycles und 76 Ergebnisassertionen, PowerPoint-Anwendungstest und unabhängiger Cleanup. Optionaler Full-Text-WARN bleibt erhalten.
- [ ] STANDARD-Teilnehmerpilot: reale Gruppe mit Lehrperson, Soll-/Ist-Zeiten und Verständnisbelegen. Wiederaufnahme bei tatsächlicher moderierter Durchführung; kein eigener offener Codebranch.

Dies ist die im neuen Auftrag ausgewählte Folgewelle nach BASIS/PR250.
Die übrigen pausierten technischen Arbeiten und Automationen werden nicht
aktiviert; volle TSK-012-/TSK-014-/Streamfreigabe bleibt offen.

## BASIS Kurswelle vom 18. Oktober 2026

- [x] BASIS-Teilprodukt TSK-012: [39-Folien-Kurspaket](../Documentation/HowTo/SQL_SERVER_2025_AI_BASIS_COURSE.md), Ablauf, zwei Praxisaufgaben, RAG-Leseaufgabe, Ausfallpfad und Beobachtungsbogen.
- [x] BASIS-Teilprodukt TSK-014: [technische und redaktionelle Generalprobe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_BASIS_REHEARSAL.md), sechs vollständige SQL-Lifecycles, Rechte-/Markergegenfälle und PowerPoint-Anwendungstest bestanden.
- [ ] Teilnehmerpilot: tatsächliche Lehrperson/Gruppe, Soll-/Ist-Zeiten und Verständnisbelege. Grund: diese Human-Evidenz entsteht nicht durch den technischen Lauf. Wiederaufnahme bei realer Kursdurchführung; kein eigener offener Codebranch.

Die volle TSK-012-/TSK-014-/Workstreamabnahme bleibt offen. Der neue Auftrag
gilt für den BASIS-Abschluss; der folgende Stopp vom 14. Oktober ist historisch.

## Benutzerabschluss der Entwicklungswelle: keine autonome Fortsetzung

Am 14. Oktober 2026 hat der Benutzer ausdrücklich angeordnet, die aktuelle
Entwicklungswelle vollständig abzuschließen, keine neue Welle zu starten und
nach der Integration nach origin/main den Orchestrator-Chat zu beenden.
Diese Anweisung beendet die bisherige autonome Fortsetzung. Der zugehörige
Heartbeat ist tatsächlich PAUSED; andere Automationen bleiben unverändert.

Der letzte fachliche Schnitt ist über PR248 vollständig geschlossen:
Main9ab1c2255cc0c4a8b9f3b45a094bd2863b961fc7, acht erfolgreiche Head- und
sechs erfolgreiche Main-Checks, vollständiger gleicher Tree, synchrones
sauberes Main und eigene Branches entfernt.148 private Belegdateien sind
bytegenau gesichert und nach tatsächlicher Worktreearchivierung erneut geprüft.
Der historische öffentliche V2-Record ist kohärent mit WARN; der frühere FAIL
und sämtliche offenen Qualifikationsgrenzen bleiben unverändert erhalten.

Der ausschließlich leer vorbereitete Float16-Worktree erhält keine fachliche
Implementierung oder Runtimeadmission. Er dient nur dieser abschließenden
Stoppdokumentation und wird nach deren PR-Integration vollständig bereinigt.
Keine neuen SQL-, Container-, Modell-, Provider-, Compiler- oder Hosteffekte.
Keine neue Entwicklungswelle, keine automatische Wiederaufnahme. Offene
TSK-004–TSK-014-/Release- und Humanqualifikationen bleiben im Backlog offen;
dieser Benutzerabschluss erklärt sie nicht nachträglich als bestanden.

[Letzter fachlicher Nachweis und verbleibende Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md).

## C1: historischer öffentlicher V2-Record kohärent mit WARN

Der erste neue Kandidat hat den unveränderten tatsächlich gesicherten C3-Record
mit dem veröffentlichten korrigierten Consumer vollständig ausgewertet:
SOURCE_COHERENT_OVERALL_WARN, COHERENT_PUBLIC_V2, attempted1/completed1.
Driver-PID68696 und Reportchild-PID32960 endeten bestätigt mit Poll/Returncode0,
ohne Timeout oder UNKNOWN. Alle56 festen Eingangsdateien und neun Authority-
dateien blieben vor/nach bytegleich. Root hat Originalkanäle, Quellen, vollständige
Prozessenden, Ergebnisform, Ledger und STOP unabhängig geprüft.

Feste Counts: drei Profile,25 Clientcaptures, acht Rollenkontexte, zwei Kostenpaare,
zwei Rechtegegenfälle sowie vier positive und vier abgewiesene DML-Fälle.
Die unveränderten Profile wurden vollständig geprüft; keine neuen SQLergebnisse
oder Runtimecapturen erzeugt. SQLcleanup bleibt lediglich TEXTS_COHERENT,
Herkunft und Credentiallisten-Vollständigkeit bleiben deklarativ. Bei secrets=[]
bleibt NOT_CHECKED_FOR_UNAVAILABLE_SECRETS; Generation UNKNOWN und die offenen
Ownerquery-/TDS-/vollständigen DML-Error-/Parentcleanup-/Runtime-/TP-PERF-Claims
werden nicht hochgestuft. Dies ist ein begrenzter Recordnachweis.

Neue Welle: ein Quellenstand und ein erfolgreicher kohärenter Report mit WARN,
keine zusätzlichen Unit-/Syntaxproben oder Domainaufrufe. Beim ersten kohärenten
Befund tatsächlich STOP; keine weiteren Kandidaten oder Budgetausschöpfung.
Zusammen mit der früheren Welle zwei historische Versuche: der erste FAIL
V2_RECORD_BINDING bleibt unverändert mit seinem verbrauchten Max1 und STOP.
Die vor dem neuen Report abgewiesene Rootmetadatenassertion mit falsch
übertragenem Preparedhash ist separat erhalten; nach direkter Aufnahme des
vollständigen Hashs korrigiert, kein Report vor dieser Korrektur und keine
Umzählung als Runtime-/Quellen-Syntaxfehler. Ihr PID bleibt NOT_CAPTURED.

Alle56 tatsächlich verwendeten Eingangsbytes sind flach gesichert, dazu23 feste
Authority-/Ergebnis-/Raw-/Ledger-/Rootreviewdateien; bytegenau erneut verglichen.
Originalmanifest und Admission bleiben unverändert. Nach dem tatsächlichen
Report werden ausschließlich HowTo und kanonischer Dokumentstand aktualisiert;
die Dokumentdeltas werden getrennt vom unveränderten Ausführungsbeleg gebunden.
Aktuelle lokale Dokumentprüfungen, PR-/Head-/Main-Gates, origin/main-Integration,
FullTree, Synchronisierung und eigener Cleanup folgen. Modell-/Tokenverbrauch UNKNOWN.

[Konkreter Nachweis und offene Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md).

## TSK-006: getrennte historische V2-Requalifikation in Vorbereitung

PR247 vollständig geschlossen: zehn Head- und acht Main-Checks erfolgreich,
je ein Runtimejob nicht ausgewählt; Main67d83316722e396624ba77db2c51d66ff43b9b93,
FullTree/Sync/Branchcleanup bestanden,876 private Dateien bytegenau erhalten,
Worktree tatsächlich archiviert. Der ursprüngliche V2-Report bleibt FAIL
V2_RECORD_BINDING, attempted1/completed0; sein Max1 und STOP bleiben erhalten.

Der veröffentlichte Source5-Consumer korrigiert den tatsächlich gefundenen
vollständigen NOT_STARTED-Vertrag. Darauf folgt eine getrennte historische
Offlinewelle: maximal sechs relevante Quellen-/Adapterstände und sechs Reports,
ActualCheckpoint3/Hard6/UNKNOWN-/erster kohärenter Stop. Weitere Versuche nur
mit verändertem Input/Source oder neuer Evidenz, keine alten grünen Wiederholungen.
Ein Implementer, enger Rootreview; Null Domain-/Modell-/Hosteffekte. Alte Counts,
Claims, V1 und Originalprofile unverändert. Zunächst keine Reportadmission.

[Konkreter Scope und aktuelle Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md).

## TSK-006: V2-Rechtegegenfälle korrigiert; historischer Report bleibt FAIL

Der einmalige historische Offlinebericht scheiterte mit V2_RECORD_BINDING:
attempted1, completed0, keine Summary. Driver-PID8276 und Child-PID72048
endeten bestätigt mit Poll/Returncode1, ohne Timeout oder UNKNOWN. Alle51
festen Eingangsdateien und acht Authoritydateien blieben vor/nach bytegleich.
Root hat den Fehler und die Originalkanäle unabhängig geprüft.

Der konkrete Fehler betrifft die beiden Rechtegegenfälle: Die tatsächliche
öffentliche API liefert für das noch nicht gestartete Cleanupfenster vier
Felder, während Consumer und Fixture nur Status erwarteten. Source5 fordert
jetzt exakt Status=NOT_STARTED, Seconds als int60 sowie beide Zeitfelder=None.
Fehlende, zusätzliche und widersprüchliche Felder werden abgewiesen. Der neue
betroffene Gegenfall bestand normal PID11964 und optimiert PID16700, jeweils
Poll/Returncode0; alle31 Quellen blieben unverändert. Enger Rootreview bestanden.

Fünf geprüfte Quellenstände,21 Methodeninvokationen/19 PASS/zwei erhaltene FAIL,
zusätzlich erster Driver-SyntaxFAIL; acht bestätigte Unitprozessenden. Keine
alte grüne Suite lokal wiederholt. Der ursprüngliche historische Report bleibt
FAIL; das maximale Einzelreportbudget ist verbraucht und wird nicht zurückgesetzt.
Null Native-, SQL-, Container-, Provider- oder Modellaufrufe in diesem Schnitt.
V1, alte Evidenz und Claims unverändert; Runtime-/Herkunfts-/Credentialgrenzen
bleiben offen. Modell-/Tokenverbrauch UNKNOWN.

Dieser Schnitt wird mit aktuellem Quellen-/Dokumentfreeze, PR-/Head-/Main-Gates,
Integration nach origin/main, Synchronisierung und eigenem Cleanup geschlossen.
Erst anschließend darf eine getrennte begründete Folgewelle einen weiteren
historischen Bericht zulassen; kein Wiederholungs-PASS in dieser Welle.

[Konkrete Belege und Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: V2-Source4 Fixturekorrektur gezielt bestanden

Source4 ändert nur den Helperfixture-Pfadvergleich; Produktguards Source3-gleich.
Betroffener Fall1N/1O bestanden, alle Helpernegativzweige erstmals erreicht.
VierStände/19Invokationen/17PASS2FAIL plus ersterDriverSyntaxFAIL, sechs bekannte
Testenden. PrivacyN/O-BelegeSource3 unverändert, keinealte7/6-Wiederholung.
HistorischerOfflineReport/Domain0; freshRootabnahme nochvorReport erforderlich.
[Konkrete aktuelle Belege und verbleibende Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: V2 tatsächlicher Checkpoint3 geschlossen

Source3-Privacycluster normal/optimiert bestanden; Helperfixture beide FAIL
am Extended-/Normalpfadvergleich, negativeHelperzweige NOT_REACHED.
RootactualCP3: dreiStände/17Invokationen/15PASS2FAIL plusSource1SyntaxFAIL,
vier bekannteTestenden. Source4 ausschließlich betroffeneFixtureBytevergleich-
Korrektur mit1N/1O; keinealtegrüneSuite/Privacywiederholung. Offline-/Domain0,
keinehistorischeReportadmission. [Konkreter Checkpoint und Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: V2-Source2 enger Rootreview verlangt Guardkorrektur

Source1 privater Driver-SyntaxFAIL vor Child bleibt; Source2 erstmals7N/6O
bestanden,13 Methoden/2 bekannte Testenden. Root reproduzierte zwei neue reine
Privacyfindings: gemischte bekannte Hexformen und verschachtelte PART-Frames
passieren vor Digests. Zusätzlich feste vier Pure-Modulnamen vor Import begrenzen.
Source3 gezielt, kein alter7/6-Replay; tatsächlicherCP3 erst nach Source3.
Offline-/Native-/SQL-/Host-/Modelleffekte0, Originale/aktuellerDocstand vorher
gesichert. [Aktueller Befund und unveränderte Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: öffentliche V2-Recordauswertung als nächster Offline-Schritt

PR246 ist vollständig geschlossen: Head13/Main11 erfolgreich, Main e3d8d61e,
voller Tree, synchrones sauberes Main, eigene Branches entfernt;439 private
Originale hashgesichert und Worktree tatsächlich archiviert. PublicRole-C3 bleibt
begrenzter Teilnachweis mit WARN/offenen Owner-/TDS-/Runtime-/TP-PERF-Grenzen.
Der separate V2-Consumer nimmt die neue Public-Resultform auf; V1-CapturesNone und
historische Inputpins bleiben unverändert. Ein Implementer, enger Rootreview,
max6 Source/ActualCP3/Hard6 und höchstens ein gebundener Offline-C3-Report nach Freeze.
Neue Runtime-/SQL-/Modelleffekte0, keine Wiederaufnahme alter Native-/V1-Wellen.
[Endlicher Scope, Prüf- und Claimgrenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: öffentlicher Rollenmodus tatsächlich begrenzt bestanden

C3/insgesamt Rollenkandidat6 bestand den abgegrenzten öffentlichen APIvertrag
auf 17.0.5005.3/Engine3/Linux. 39 bestätigte SQLprozessenden, davon drei erwartete
Startupverbindungs-FAILs vor Bootstrap; 25 bekannte Namespaceprozesse, ein eigener
Container angelegt und entfernt. Zwei tatsächliche Rechteentzüge führten exakt
zu PREFLIGHT/SKIP_PERMISSION, frische DBabwesenheit und vollständiger Grantrestore.
Positiver Produktstatus bleibt WARN_OPTIONAL_EVIDENCE_SKIPPED: 23 Phasen,
acht Rollenkontexte, zwei Kostenclients, drei Storageaufnahmen und vollständiger
999-Row-Text-/Distanz-/Rebuildvergleich. Preview/MAXDOP zurückgesetzt, DB/Login/
CID/Name/Inputs frisch abwesend; Closedtrue/Unknownfalse. RootactualReview bestanden.
Sechs Quellenstände/28 Invokationen/26 PASS/zwei erhaltene ERROR und elf bekannte
Testenden. C1/C2-FAILs bleiben unverändert; Welle nach finalem Teilnachweis gestoppt.
Generation UNKNOWN, separater Ownerreceipt und Server-/TDS-Enden unqualifiziert;
Runtime/TP-PERF/Release offen, historische Dokumentprovenienz-WARN erhalten.
[Originalbefund, aktuelle Grenzen und Abschlussvertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).

## TSK-006: C2 geschlossen FAIL, Source6 letzter Quellenstand

C2/insgesamt Rollenkandidat5 endete vor Create bekannt FAIL und geschlossen:
drei sichere Namespaceclients bestätigt, null Container/SQL/Profile/Inputs;
eigener Name frisch abwesend, keine SQL-/Principalabwesenheitsattestation.
Die tatsächliche volle Image-ID ohne sha256-Präfix stimmt exakt mit der
freigegebenen ID überein; Source6 erlaubt ausschließlich beide vollständigen
Darstellungen derselben ID. Neuer Gegenfall normal/optimiert bestanden.
Sechs Quellenstände, 28 Invokationen, 26 PASS/zwei erhaltene ERROR, elf bekannte
Testenden. Originale und aktuelle Canonicalbytes vorher gesichert; historische
Dokumentprovenienz-WARN bleibt. C3/insgesamt6 ist nach frischer Rootadmission
der letzte Nativekandidat; kein Source7/Native4. [Nachweis und Grenzen](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).

## TSK-006: öffentlicher Rollenlauf C1-FAIL, gezielte Source5-Korrektur

NativeC1/insgesamt Rollenkandidat4 ist bekannt FAIL vor Domainaufrufen,
null neue Container/SQLkontexte. OriginalClosedfalse und UrsacheUNPROVEN bleiben.
Eine separate spätere schreibgeschützte Prüfung bestätigt den aktuell abwesenden
eigenen Namen und schließt ausschließlich den aktuellen kontextlosen Stand;
kein ursprünglicher Cleanupfenster-/SQL-Abwesenheits-PASS und kein Zählerreset.
Source5 trennt feste Command-/SQLinputs von strikten empfangenen JSON-/Wirekanälen;
neuer Gegenfall normal/optimiert bestanden. Fünf Quellenstände, 26 Invokationen,
24 PASS/zwei erhaltene ERROR. Neue Rootadmission nach aktuellem Freeze steht aus.
Historische Dokumentprovenienz-WARN bleibt sichtbar; Originale und aktuelle
Dokumente vor Änderung gesichert. [Konkreter Nachweis](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).

## TSK-006: öffentliche Rollenprobe nach abgeschlossenem Budget-Schnitt

Der private Caller hat vier gezielt geprüfte Quellenstände: 24 Methoden-
invokationen in sieben bekannten Testprozessen, 22 PASS und zwei erhaltene
Source1-ERROR. Der tatsächliche unabhängige Checkpoint3 verlangte eine
Namespace-Countreserve für Cleanup. Source4 reserviert sechs der insgesamt
32 Aufrufe; Normalaufrufe enden bei26 ohne Zählerreset. Die neue Gegenprobe
bestand normal und optimiert. Öffentliche API unverändert, Domainaufrufe0;
aktueller Doc-/Host-/Quellenabschluss und ausdrückliche Root-Nativeadmission
stehen vor jeder Runtimewirkung noch aus.

PR245 ist vollständig geschlossen: 13 Head- und sieben Main-Checks bestanden,
Main1fbd339f, voller Tree, synchrones sauberes Main und eigene Branches entfernt.
585 private Belegdateien sind bytegenau gesichert, der Worktree tatsächlich
archiviert. Vier Quellenstände mit 18 Methodeninvokationen in sieben Prozessen;
17 PASS und ein archivierter ursprünglicher Fixture-FAIL bleiben sichtbar.

Der [öffentliche Rollennachweis](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md) wird im neuen eigenen Worktree zunächst
als private Callergrundlage umgesetzt. Aktuelle öffentliche API einschließlich
SharedCleanupWindow unverändert; neue Quellen-/Input-/History-/Hostbindung und
unabhängiges Rootreview vor Nativeadmission. CallerSource6/Checkpoint3/Hard6,
historische drei Rollenkandidaten/vier Container plus höchstens drei neue
geänderte Kandidaten mit je einem eigenen Container. Noch keine neuen Caller-
oder Domainaufrufe; volle Runtime-/TP-PERF-Abnahme und Tokenverbrauch bleiben offen.


## TSK-006: gemeinsames öffentliches Cleanupbudget vor Runtime

Vier Quellenstände sind gezielt geprüft: 18 Methodeninvokationen in sieben
gehaltenen Prozessen, 17 PASS und ein archivierter Source1-Fixture-FAIL.
Der tatsächliche unabhängige Checkpoint3 verlangte Korrekturen für erneute
Windowinitialisierung und veränderbare Fristenkonstanten. Source4 schließt beide
mit einem neuen Gegenfall normal und optimiert; frühere grüne Suiten wurden
lokal nicht wiederholt. Domainaufrufe0. Aktuelle PR-/Head-/Main-Integration,
Synchronisierung und eigene Archivierung folgen vor neuer Calleradmission.

Der öffentliche Rollennachweis ist vor Callerumsetzung zurückgestellt: seine
20s-Recovery meldet keinen Cleanupstart, konfigurierte Windows-Nachläufe passen
nicht in eine ehrlich gekoppelte äußere60s-Uhr. Boundaryproof erhalten,
Caller/Pure/Native/Domain0, historische3Rollenkandidaten/4Container unverändert.

Aktueller unabhängiger Schnitt: [typisierte Budgetübergabe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_CLEANUP_BUDGET_REVIEW.md).
Einmaliger tatsächlicher Cleanupstart, gemeinsame absolute Deadline und fester
Collector mit Kill-/Reapreserve; keine freien Callbacks oder globalen Collector-/
Hoständerungen. SOURCE_ONLY, neue6Quellenstände/Checkpoint3/Hard6; vorherige
RoleSourceHard6 unverändert gestoppt. Enger Rootreview und betroffene Gegenfälle
vor PR/Head/Main/Tree/FF/eigenem Cleanup. Danach aktuellen Caller fortsetzen,
vor Native neue Admission; Runtime-/TP-PERF-Abnahme und Tokens UNKNOWN.

## TSK-006: öffentliche Rollen-API, tatsächlicher Nachweis in Vorbereitung

PR244 geschlossen: aktueller Head13/Main7, Main3a558cf0, voller Tree/FF/
sauberes Main, eigene Branches entfernt, 327 private Dateien gesichert und
Worktree tatsächlich archiviert. SourceHard6 bleibt gestoppt; alte Syntax-,
CI-FAIL- und UNKNOWN-Records unverändert. Der historische Squash-Commit
verfehlte das Codex-Präfix; Abweichung erhalten, keine Historienumschreibung.

Aktueller Schnitt: [begrenzter öffentlicher Rollennachweis](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).
Zunächst private Caller-/Capturevorbereitung ohne Domainaufrufe; unveränderte
öffentliche API, vollständige Credentials-/SID-/Principal-/Session-/Marker-/
Restore-/Cleanupbindung. Historische drei Rollenkandidaten/vier Container plus
höchstens drei neue Kandidaten/je einen eigenen Container = maximal6/7.
Stop nach erstem kohärenten öffentlichen API-Teilnachweis oder sofort UNKNOWN.
Sechs getrennte Callerquellenstände/Checkpoint3/Hard6; aktuelle Rootadmission
vor Native bleibt erforderlich, volle Runtime-/TP-PERF-Abnahme offen.

## TSK-006: öffentlicher IDX-012-Rollenmodus in Vorbereitung

PR243 vollständig geschlossen: 14 Head-/acht Main-Gates, Maine63cd1fc,
voller Tree, FF/sauberes Main, eigene Branches entfernt, 81 private Dateien
gesichert und Worktree tatsächlich archiviert. Poolsource Hard6 bleibt
gestoppt; alte UNKNOWNs und Ursachen UNPROVEN werden nicht geändert.

Nächster unabhängiger Schnitt: [öffentlicher Rollenmodus](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_API_REVIEW.md).
Der vorhandene historische IDX-012-Rollensplit wird als ausdrücklich gewählte
öffentliche API vorbereitet: feste Credentials-/SID-/Kontextbindung, je
Kostenphase dieselbe Session, Admin nur am Build, danach gleicher Operator.
SOURCE_ONLY, sechs Quellenkandidaten/Checkpoint3/Hard6, keine Runtimezulassung
oder Rechtevergabe. Betroffene Gegenfälle und enger Rootreview vor Integration;
volle TSK-006-/Runtime-/TP-PERF-Abnahme offen, Tokenverbrauch UNKNOWN.

Aktueller Quellenstand: Labels Source1–4, insgesamt fünf tatsächlich geprüfte
Zustände einschließlich initialem Syntaxpreflight-FAIL mit abweichenden Bytes.
Die Zählung wurde korrigiert; Rootcheckpoint3 wurde tatsächlich nach vier
Zuständen und vor dem fünften geschlossen, ohne rückwirkenden Rechtzeitigkeitsclaim.
Vorherige 18 reine Methodeninvokationen/ sechs gehaltene Pythonprozesse bleiben
unverändert. Source4 schließt den konkreten Cleanup-UNKNOWN-Rückgabeverlust mit
nur einem neuen vollständigen Controllergegenfall normal und unter `-O`:
beide bestanden, insgesamt 20 Invokationen/acht gehaltene Prozesse. UNKNOWN im
Restore liefert FAIL_CLEANUP und NOT_ESTABLISHED mit vollständigen sicheren
Captures/zurückgehaltenen Inputs zurück; kein weiterer Recovery-SQLclient.
Vor der CI-Imagekorrektur waren fünf von sechs Quellenständen verbraucht; einer verblieb. Root hat Source4/overall5 semantisch und mechanisch abgeschlossen;
CLEANUP_UNKNOWN_RESULT_LOST ist geschlossen. Der Quellenstand wird über PR
integriert; Native-/Server-/TDS-Abnahme bleibt offen, Domainaufrufe bleiben null.

Der erste PR244-Headlauf blieb tatsächlich FAIL: Der SQL2025-Kostenconsumer
verwarf SKIP_CONFIGURATION; die vier vorangehenden DGN-010-Lifecycles hatten
bereits SKIP_CONFIGURATION mit bestätigtem Cleanup geliefert. Der ursprüngliche
CI-Namespacecleanup bestand. Die Logdigests belegen, dass `2025-latest` gegenüber
dem erfolgreichen Mainlauf38415812533 ein anderes Image auflöste: vorher
`sha256:2b5b581621126574f3d1f75e78d3eebe8d05aedb59ad0cfdf9aa42cb0634d726`,
im fehlgeschlagenen Headlauf38427774683 dagegen
`sha256:742481d1b1186cccc81220a1eaacef244ca8d0f7d19c8e5c70df8ae541ffbab2`.
Image-Drift ist belegt; die tatsächliche neue Build-/Editionabweichung ist
UNPROVEN, weil der SKIP keine abweichenden Werte ausgibt.

Der sechste und letzte Quellenstand CI_IMAGE_INPUT_CORRECTION pinnt nur den
SQL2025-Matrixeintrag auf den tatsächlich erfolgreichen RegistryDigest.
2019/2022, Laufskripte, Testoracles und Rollenproduktbytes bleiben unverändert;
keine SKIP- oder FAIL-Umdeutung und kein unveränderter CI-Rerun. Source4-Freeze,
Rootreview, 20 Methodeninvokationen/acht gehaltene Testprozesse sowie die beiden
Original-CI-Logs bleiben erhalten. Keine lokale Purewiederholung oder neue
Domainaufrufe. Jetzt sechs von sechs Quellenständen/Hard6, kein Reset oder
Source7. Die neue geänderte CI-Eingabe erhält aktuelle Head-/Main-Gates vor
Integration; PR244 bleibt bis dahin ungemergt. Öffentliche Rollenruntime und
vollständige Demo-/Server-/TDS-/TP-PERF-Abnahme bleiben NOT_ESTABLISHED.

## TSK-009: reiner Poolchild-Capture nach vollständigem PR242-Abschluss

PR242 geschlossen: 14 Head-/acht Main-Gates, Mainee3777fd, Tree/FF/Branches,
338 private Dateien gesichert und Worktree tatsächlich archiviert. Aktueller
Schnitt: [Poolchild-Capturevertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_CHILD_CAPTURE_REVIEW.md). Source5/6, geschlossenerSourceCP3,
hard6 ohne Reset. Sichere tatsächliche Child-Prozess-/Kanalbelege vor fehlerhafter
Klassifikation erhalten, Privacy vor Raw/Digests; unbeobachtete Werte nicht
erfinden und alte UNKNOWN-Ursache nicht rekonstruieren. Nur neue Puregegenfälle
normal/-O, keine lokale Native-/Provider-/SQL-/Container-/Modellprobe.
Gestoppte Welle bleibt bei insgesamt vier Nativeversuchen/drei Containern;
SQLcleanup/Inputs/Poolchildqualifikation offen, vorhandene Originale read-only.
Aktuelle PR-/Head-/Main-/Tree-/FF-/Branch-/Beleg-/Archivgates vollständig schließen.
Tokenverbrauch UNKNOWN.

Source5 ist rein mit vier neuen Methoden normal und vier unter `-O` bestanden.
Source6 beseitigt einen verbliebenen Source-read vor der Transportzuweisung:
der tatsächlich vor Start gehaltene öffentliche Collector-Returntyp wird verwendet.
Nur die betroffene Methode wurde normal und unter `-O` erneut geprüft; beide
Läufe bestanden. Tatsächliche Prozessenden und unveränderte Rawkanäle sind privat
gebunden. Source5-Bytes und sämtliche früheren Prüfbelege bleiben archiviert;
keine alte grüne Suite oder Runtime wurde wiederholt.

Der separate Childtransport hält bekannte Prozessfakten vor Ergebniszuordnung,
auch bei malformed Receipt, fehlgeschlagener Sourcebeobachtung oder UNKNOWN.
Unsichere Kanäle erhalten keine Rawdaten oder Digests. Unbeobachtete Werte bleiben
null; bekannte Prozessenden ersetzen weder die 57 API-Records noch Server-/TDS-
Endbelege. Der unabhängige Rootreview hat den konkreten Capture-/Privacy-/
Endtrennungsdelta ohne offenes semantisches Finding gelesen. Mechanische
Freezeprüfung und aktuelle Integrationsgates stehen noch aus.

Hard6 ist erreicht, Sourceentwicklung gestoppt; keine neue Native-, Provider-,
CLR-, Compiler-, SQL-, Container-, Modell- oder Metadatenausführung. Bestehender
Sourcecheckpoint3 bleibt geschlossen, alte UNKNOWNs und Ursache UNPROVEN bleiben
unverändert. Kumulativ weiterhin vier Nativeversuche/drei Container, keine neue
Zulassung der gestoppten Welle. Runtime-/Pooling-/TSK-009-/TP-CON-Abnahme bleibt
NOT_ESTABLISHED. CI erweitert nur den bestehenden statischen Schritt um vier
Schutzmethoden: 39 normal/18 optimiert in denselben zwei Pythonprozessen;
Runtimejob und Selector sind bytegleich, Default-CI startet kein RED-Profil.


## TSK-009: begrenzter Owner-Teilnachweis, Poolwelle bei UNKNOWN gestoppt

Aktueller Schnitt: [Poolqualifikationswelle](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md).
Vier Sourcezustände sind ehrlich gezählt: initial neun betroffene Methoden,
Checkpoint-Dateibindung zwei, tatsächlicher Checkpointvertrag zwei und getrennte
Setupkanäle zwei, jeweils normal/-O mit gehaltenen Enden und sicheren Raws.
Sourcecheckpoint3 geschlossen und für Source4 ausdrücklich neu gebunden;
keine alte grüne Vollsuite wiederholt. Standard-UNKNOWN-Sperre unverändert.

Native1/insgesamt3 bleibt bekannt FAIL_SETUP_SUMMARY + FAIL_SQL_CLEANUP,
UNKNOWNfalse: vier SQLcmd- und dreizehn gehaltene Namespaceenden. Frische
CID-/Namens-/Inputabwesenheit belegt Resourceclosure; SQLcleanup NOT_ESTABLISHED.
Der unabhängige verpflichtende Nativegesamtcheckpoint3 ist geschlossen.
Source4 korrigierte den konkret erfassten getrennten Setupkanal.

Native2/insgesamt4 endet UNKNOWN_STOP. 39 bekannte SQLcmd-Enden, 48 gehaltene
Namespaceenden, Setup/Logins/Baseline sowie sechs tatsächliche Owner-SQLabweisungen,
fünf vollständige Negativzustandswitnesses und sieben geordnete Controls sind
belegt. Einzelne Poolchild-/.NET-Enden, A/B/U-Checkouts, physische Poolreuse und
Ursache bleiben NOT_ESTABLISHED beziehungsweise UNPROVEN. Nach UNKNOWN kein
Folge-SQL; genau ein vollständig gebundener eigener Remove und frische leere
CID-/Namensabfragen. SQLcleanup NOT_ESTABLISHED; ein ursprünglicher Childplan
bleibt erhalten, inputsAbsentfalse und ledgerClosedfalse. Kein zweiter Remove.

Kumulativ vier Nativeversuche/drei Container einschließlich der unveränderten
PR226-Welle. Aktuelle Welle STOP; keine Native3-Zulassung trotz verbleibender
rechnerischer Slots. Kein Runtime-/TSK-009-/TP-CON-PASS. Quellen, Hostbytes,
Authorities und ursprüngliche Ausführungssnapshots bleiben erhalten;
Dokumentstatusänderungen sind getrennte DocOnly-Deltas, keine rückwirkend neuen
Ausführungspins. Head-/Main-Gates, Integration und eigener Branch-/Worktreeabschluss
folgen durch Root. Modell-/Tokenverbrauch UNKNOWN.

Nach vollständiger Integration folgt ausschließlich ein unabhängiger SOURCE_ONLY-
Capturevertrag: vollständige sichere Poolchild-Kanäle und individuelle Endrecords
vor Malformed-/UNKNOWN-Klassifikation erhalten. Keine Wiederaufnahme dieser oder
älterer UNKNOWN-Wellen, kein Native-/Ressourcenreplay und kein Ursachennachweis
allein aus neuer Source.

## TSK-009: neue eigene öffentliche Poolqualifikation nach PR241

PR241 vollständig geschlossen: sieben Head-/fünf Main-Gates, Mainaf7d3d3a,
Tree/FF/Branches, 1467 private Dateien gesichert und Worktree tatsächlich archiviert.
Aktueller Schnitt: [neue Poolqualifikationsgrundlage](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md).
Alte PR226-Welle bleibt STOPPED_NATIVE_UNKNOWN, zwei Nativeversuche/einContainer/
SQL0/Poolchild0; aktuelle korrigierte Sources werden an neue eigene Wave-/Input-/
Control-/Historybindungen gebunden. Kein Replay, alte UNKNOWN niemals löschen.
Zunächst SOURCE_ONLY ohne Effekte. Neue Nativeadmission nur nach aktuellem Review;
alte zwei Versuche plus höchstens vier neue Gesamtmax6, alte einContainer plus
höchstens vier neue Gesamtmax5, seriell. Erster neuer Nativeversuch verlangt
Gesamtcheckpoint3. Eigene Marker-/SID-/Credential-/Requestende-/RLS-/Cleanupfloors
und unveränderte Host-/Cloud-/ONNX-/Releasegrenzen; Tokenverbrauch UNKNOWN.


## Eigenständiger KI-Workstream – Planung vom 2026-10-11

Aktueller Schnitt: [beobachtbare Routeignung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ROUTE_ELIGIBILITY_REVIEW.md).
PR240 vollständig geschlossen: sieben Head- und fünf Main-Gates, Main dee36a7b,
vollständiger Tree, FF-Synchronisierung und eigene Branches bereinigt;
1.534 Dateien gesichert und eigener Worktree archiviert. C2 bleibt kohärent
UNAVAILABLE, ohne Unterscheidung zwischen fehlendem Tag und Mindestversion.
Die neue Beobachtungsgrundlage trennt tatsächliche Version, Mindestversions-
entscheidung, Tag-Präsenz und Ursachen; alte Records werden nicht ergänzt.
C3 tatsächlich COHERENT_DIAGNOSTIC_ONLY/UNAVAILABLE: Runtimeversion0.40.2
ist mindestens0.11.10, version_supported=true. Exakte gemma3:1b-Tagmatches0,
tag_present=false; tag_missing=true und version_below_minimum=false.
Zwei neue bekannte HTTP200-Responses (version/tags), kumulativ vier Metadata;
Show/WhatIf/Inferenz0. Top-/Childenden bekannt, kein Timeout/UNKNOWN,
elf Quellenbindungen, vollständiger eigener Snapshot und129 historische
Dateien unverändert; kein Inventar gespeichert. Alte C2-Ursache bleibt
NOT_DISTINGUISHED, kein rückwirkender Versions- oder Tagbefund.
Pflichtcheckpoint3 anhand C1/C2/C3 unabhängig geschlossen: PASS_DIAGNOSIS_ONLY.
Gesamte Diagnosewelle STOP; keine vierte Probe oder weitere Metadaten/Inferenz
auch bei rechnerisch verbleibendem Budget. Fünf neue Puremethoden normal/-O
bestanden; keine alten grünen Suiten wiederholt. Keine Modelle, Downloads oder
Hoständerungen; Lizenzinferenz NOT_ADMITTED/Gewichte und volle Gates offen.

Nach vollständiger Integration dieses Nachweises folgt eine unabhängige
TSK-009-Poolgrundlage zunächst SOURCE_ONLY auf aktuellen korrigierten
öffentlichen Quellen. Bekannte Namespacekorrekturen nicht erneut analysieren;
Delta zum tatsächlich gestoppten PR226-Stand und neue eigene Input-/Scope-/
Rootbindungen prüfen. Alte zwei Nativeversuche/ein Container/SQL0/Poolchild0
transparent weiterzählen; alle alten UNKNOWNs und Stops erhalten. Kein C3 der
alten Welle, kein Ressourcenreplay oder Recovery. Neue Nativeeffekte erst nach
separatem aktuellen Quellen-/Sicherheitsreview und konkreter Rootadmission.

Aktueller Schnitt: [lokaler Completionbestand](../Documentation/Project_Planning/SQL_SERVER_2025_AI_COMPLETION_ROUTE_REVIEW.md).
PR239 vollständig geschlossen: neun Head-/sieben Main-Gates, Main63640639,
voller Tree/FF/Branches, 36 private Dateien gesichert/eigener Worktree archiviert.
Öffentliche VECTOR-Lesehilfen fertig; alte Qwen-Hard6-Welle bleibt gestoppt.
Aktueller öffentlicher Lab-Katalog bietet zusätzlich die lokale generation-Route
ollama-gemma3-1b-local; bisher nur Quellenbefund, keine Live-/Antwortqualifikation.
Neue gebundene read-only Bestandsprüfung, zuerst Sourcevorbereitung mit null
neuen Effekten. Nach eigener Rootadmission maximal drei Loopback-Metadata-
Requests/ein lokaler WhatIf-Plan, keine Inferenz/Downloads/Hoständerungen.
Source6/Checkpoint3/hard6, UNKNOWNStop, Lizenz-/Capability-/Livegrenzen offen.

C1-Sourcefreeze erreicht das Ausführungsgate nicht: unabhängige Root-
Byteprüfung meldet tatsächlichen Source-Drift vor Admission. Der fremde
Lab-Arbeitsstand wurde parallel weiterentwickelt; drei loadergebundene
SMTP-Quellen unterscheiden sich, aktueller fremder Arbeitsstand ist sauber.
Keine Rootadmission, keine Metadaten-/WhatIf-/Inferenzaufrufe. C1-Sourcekarte,
Raws und ursprüngliche Bindungen bleiben unverändert; ursprüngliche individuelle
PID der Root-Validierung nicht erfasst, keine Rekonstruktion.

C2 verändert ausschließlich die Abhängigkeitsbindung: eine eigene unveränderte
Kopie des ausgewählten committed Lab-Trees statt Import aus einem fremden
veränderlichen Arbeitsbaum. Read-only Git-Export in eigenes ignoriertes Runtime,
maximal30MB/2000Files, keine Fremdrepo-/Gitconfigänderung. Vor Extraktion sichere
Pfade, keine Links/Casekollisionen/zusätzlichen Dateien; vollständige Git-Blob-/
SHA-/Byte-/Datei-/Directorypopulation binden und vor jedem Domainaufruf erneut
prüfen. Öffentliche CommandInfo-/Modul-/Scriptpfade aus genau dieser eigenen
Kopie, keine Bearbeitung exportierter Bibliotheksbytes. Die ausgewählte
Commit-/Treeidentität wird bei Export belegt; eine spätere fremde HEAD-Bewegung
ändert die eingefrorene Kopie nicht. Kein nachträglicher alter Qwen-Replay.
Aktuelle relevante API-/Catalog-/Schema-/Loaderdeltas prüfen, belegte identische
Quellenanalyse wiederverwenden. Nur neue Snapshot-/Sourcebinding-Gegenfälle,
alte grüne Suiten nicht wiederholen. Source2/6, Checkpoint3/hard6; Domainbudget
höchstens drei Metadata/ein lokaler WhatIf, Inferenz0 unverändert. Neue Root-
Admission nach aktuellem Freeze/Privacy/engem Risikoreview, keine Effekte vorher.

C2 tatsächlich COHERENT_DIAGNOSTIC_ONLY/UNAVAILABLE; Stop ohne Retry.
Top48172/poll0/rc0/3,066943s und PS-Child67040/poll0/rc0/2,603143s,
kein Timeout/Collectorfehler/UNKNOWN. Zwei tatsächliche Metadatenrequests
version/tags, beide HTTP200/RESPONSE_RECEIVED; Show0/WhatIf0/Inferenz0.
SelectedIdentity und Plan null, keine vollständige Inventarpersistenz.
Die UNAVAILABLE-Verzweigung fasst fehlenden Tag und unterschrittene Mindest-
version zusammen; der Receipt unterscheidet diese Ursachen nicht. Weder
„Gemma fehlt“ noch konkrete Liveversion wird nachträglich rekonstruiert.
Lizenzinferenz NOT_ADMITTED/Gewichtsattestation offen/Tokenverbrauch UNKNOWN.
Zehn Callerquellen und gesamter eigener Snapshot1404Files/19.529.256Bytes
vor/nach identisch; C1-Drift/Originale erhalten. RootactualReview von Raws,
individuellen Antwort-/Prozessenden und aktuellen Bindungen bestanden.
Aktuelle vollständige Integration/Head-/Main-/Tree-/FF-/Branches/Belegsicherung/
Worktreearchiv folgt. Danach ausschließlich neuer beobachtbarer Versions-/
Tag-/Ursachenvertrag für gezielte Diagnose. Beide tatsächlichen alten Metadata-
Calls zählen weiter; konkrete geänderte Folgegrundlage mit maximal drei weiteren
Metadata, Gesamtmax5 statt ursprünglichemMax3 explizit vor Admission, kein
stiller Reset. Sourcekandidat3 erreicht verpflichtenden Rootcheckpoint3.
Keine alte Paketausführung oder Inferenz aus unbekannter Ursache; Download,
Lizenzinferenz und Host-/Cloud-/ONNX-/Antwortgates bleiben unverändert offen.

Aktueller Schnitt: [VECTOR-Clientlesehilfe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VECTOR_CLIENT_GUIDE_REVIEW.md).
PR238 vollständig geschlossen: sieben Head-/fünf Main-Gates, Maind0528ad4,
voller Tree/FF/Branches, 129 private Dateien gesichert/eigener Worktree archiviert.
Begrenzter Gesamt4-Roundtrip-PASS gestoppt, keine weiteren Proben; alte UNKNOWN
und Wire-/volle Abnahmegrenzen erhalten. Öffentliche Lesehilfe beginnt mit
Begriffen und Datenfluss, erklärt synthetische VECTOR-Zahlen, native API
gegenüber JSON, Voraussetzungen, NULL/Dimension und TLS-/Versionsgrenzen.
Bestehende Kompatibilitäts-/Sessionreadertexte an tatsächlichen neuen Beleg
anpassen, keine alte UNKNOWN-Auflösung oder pauschale Qualification.
Ein Implementer/enger Rootreview, höchstens sechs Textkandidaten/Checkpoint3,
Stop nach kohärentem Sourceabschluss; keine neuen Runtime-/Modell-/Hosteffekte.

SOURCE_ONLY abgeschlossen nach zwei Textkandidaten. Neue anwendergerechte
VECTOR-Clientlesehilfe mit Begriffen/Datenfluss und nummeriertem Offline-
Einstieg vor drei ausdrücklich gekennzeichneten APIfragmenten; drei Lese-
Entscheidungsfälle. Bestehende Kompatibilitäts-/Sessionreadertexte unterscheiden
jetzt den tatsächlich belegten API-/SQL-Roundtrip vom fehlenden unabhängigen
Wire-/TLS-/vollen TSK-004-Beleg. Ausdrückliche DB-ID-int-Projektion und heutiger
int/Int32-Befund ohne Umdeutung früherer Fehlerursachen oder UNKNOWN-Akten.
SRC-121 bindet Herstellerquellstand6.1.4/API6.1 für Mandatory/True.
49 gezielte Links/30 lokale Targets, Originale129 readonly einmal byteverifiziert;
enger unabhängiger Root-Aussage-/Code-/Versions-/TLS-/Belegreview und Privacy
aller acht öffentlichen Dateien bestanden. C1-Originale und einziges kleine
C2-Sprachdelta erhalten. Keine Textspiegeltests/alten Suiten oder neue Compiler-/
CLR-/SQL-/Container-/Provider-/Modell-/Download-/Hosteffekte. Source-STOP,
aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach schmale read-only Bestandsprüfung für einen anderen
bereits vorhandenen öffentlichen lokalen Completionpfad; alte Qwen-Hard6-
Generationswelle bleibt gestoppt. Keine Inferenz aus Katalog-/Metadatenbefund,
keine Downloads oder Cloudfallbacks; neue Admission vor späterer Inferenz.

Aktueller TSK-004-Schnitt: [präzise OPEN-Serialisierung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_OPEN_SERIALIZATION_REVIEW.md).
PR237 vollständig geschlossen: sieben Head-/fünf Main-Gates, Main7b9e1908,
voller Tree/FF/Branches, 128 private Dateien gesichert/eigener Worktree archiviert.
Gesamt3 bleibt UNKNOWN_STOP; Pflichtcheckpoint3 anhand tatsächlicher Originale
unabhängig geschlossen. Neue eigene V4-Grundlage korrigiert nur den erwarteten
OPEN-Encrypt-Serialisierungswert der gepinnten SqlClient6.1.4-Bytes auf True.
Herstellerquelle/6.1-Dokumentation stützen die Zuordnung; falsche/fehlende/
doppelte/zusätzliche Werte weiterhin ablehnen, TLS unverändert. Drei vorherige
Compiler/Container/Caller zählen weiter, höchstens drei zusätzliche Gesamt4–6.
Source6/Checkpoint3/hard6, zunächst null neue Effekte, getrennte Rootgates
vor Compiler/Native. Alte gestoppte Pakete/Ressourcen nie replay, UNKNOWN
bleibt sticky; volle Wire-/Runtime-/TSK-004-Abnahme offen.

Gesamt4 tatsächlich BOUNDED_ROUNDTRIP_PASS; STOP_AFTER_ROUNDTRIP_PASS,
keine fünfte oder sechste Probe. Compiler57768/poll0/rc0/0,648789s,
91.136-Byte-Artefakt und zwei erhaltene CS1701-WARNs. Top36268/poll0/rc0/
33,569191s und Child63688/poll0/rc0, kein Timeout oder UNKNOWN.
Acht tatsächliche SQL-/CLRtypfelder, 31 vollständig beendete Readerteilschritte
und zehn API-Enden; zwei Native-/JSON-FLOAT32-Vektoren vor/nach unverändert,
NULL(3) und spezifischer SQL-Dimensionsfehler42204/16/1/Line1/ProcedureNULL
mit vollständiger Nachricht. 52 bekannte SQLcmdenden/24 Vollstates,
Source-delete51003/Restore und vier vollständige bytegenaue Markercontrols:
je tatsächliche DML- und Cleanup-Abweisung51004, unveränderte Vollstates
nach Abweisung und vollständiger Restore. Echte markergebundene DB-Löschung,
frische DB-/ganze CID-/Name-/Inputabwesenheit; SQLcleanup
ACTUAL_DROP_AND_FRESH_ABSENCE, UNKNOWNfalse/Ledgerclosedtrue.
Alle 71 Quellen vor/nach identisch und unabhängiger Root-Originalreview bestanden.
Nachgelagerte reine Recordlese scheiterte an 1-MB-Grenze; dieser Befund bleibt
erhalten. Ausschließlich geänderte begrenzte 10-MB-Lese, kein neuer Nativeaufruf,
unverändertes 6.461.458-Byte-Original. Kumulativ vier Compiler/Container/Caller;
zwei ungenutzte Kandidaten werden nach dem ersten kohärenten PASS nicht verbraucht.
Alte UNKNOWN/fehlende SQLcleanups und geschlossener Pflichtcheckpoint3 bleiben.
Wire-/ausgehandelte TLS-/allgemeine Runtime-/float16-/TSK-004-Abnahme offen.
Aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach unabhängige öffentliche Lesehilfe für den tatsächlich
belegten Clientweg und seine Versions-/TLS-/Abnahmegrenzen, ohne neue Runtime.

Aktueller TSK-004-Schnitt: [explizite DB-ID-Projektion im gemeinsamen Restbudget](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DBID_PROJECTION_REVIEW.md).
PR236 vollständig geschlossen: acht Head-/sechs Main-Gates, Main11ec85c1,
Tree/FF/Branches, 125 private Dateien gesichert/eigener Worktree archiviert.
Alte R1/Gesamt2-Welle bleibt UNKNOWN_STOP, kein Aufruf alter Pakete/Ressourcen.
Neue eigene Source mit explizitem CONVERT(int,DB_ID()), geänderten Bindungen
und vor Native geprüftem Dimensions-TRY/CATCH-Scope. Prior2Compiler/Container/
Caller zählen weiter, höchstens vier zusätzliche Gesamt3–6; erster Gesamt3
erzwingt Rootcheckpoint. Source-/Purevorbereitung, neue Effekte null;
Source6/CP3/hard6 und getrennte Rootadmissions vor Compiler/Native.

Gesamt3 tatsächlich FAIL/UNKNOWN_STOP; Pflichtcheckpoint3 durch unabhängigen
Rootreview geschlossen. Compiler46412/poll0/rc0/0,712391s, zwei CS1701-WARNs;
Top57876/poll1/rc1/12,640812s, Child65112/poll0/rc0, kein Timeout.
Child meldet acht tatsächliche Typfelder einschließlich DB-ID-int/Int32,
31 vollständig beendete Readerteilschritte und zehn API-Enden, zwei Native-/
JSON-Vektoren vor/nach unverändert, NULL(3) und spezifische SQL-Abweisung42204
mit allen sechs Fehlerfeldern. Der Parent verwirft bereits OPEN:
tatsächliches Encrypt=True, eingefrorenes Oracle erwartet Encrypt=Mandatory.
Die isolierte In-Memory-Gegenprüfung aller übrigen Recordfloors ist kein
geänderter tatsächlicher Lauf oder Runtime-PASS; Originale/UNKNOWN bleiben.
Sechs bekannte SQLcmdenden/ein Vollstate/keine Controls, null Folge-SQL;
eine volle eigene Containment und frische ganze CID-/Namensabwesenheit.
SQLcleanup NOT_ESTABLISHED/DB- und Inputabwesenheit false/closed false.
Alle 71 Sources und Originalbytes erhalten. Kumulativ drei Compiler/Container/
Caller, drei verbleibende Gesamt4–6; kein automatischer vierter Versuch.
Aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach ausschließlich neue eigene Source-/Scopebasis mit
quellengeprüfter präziser OPEN-Auswertung, fortgeführten prior3/rest3 und
neuen Rootgates; kein Aufruf des gestoppten Pakets oder alter Ressourcen.
Volle Runtime-/Wire-/TSK-004-/Workstreamabnahme bleibt offen.

Aktueller TSK-004-Schnitt: [eigener geänderter Caller mit Sessionreader](../Documentation/Project_Planning/SQL_SERVER_2025_AI_READER_TRANSPORT_REVIEW.md).
PR235 vollständig geschlossen: neun Head-/sieben Main-Gates, Maind5ee1864,
Tree/FF/Branches, 39 private Files gesichert/eigener Worktree archiviert.
Alter Transport-C1 bleibt UNKNOWN_STOP, Originale/alte Ressourcen readonly.
Neue V2-Sourcebasis mit acht tatsächlichen Readerfeldern/Einzelenden;
gemeinsames Nativebudget zählt alten C1 weiter, höchstens fünf zusätzliche
eigene Kandidaten/Container/Compiles/Caller, Gesamtcheckpoint3/hard6.
Jetzt Source-/Purevorbereitung; neue Effekte null, getrennte Rootgates vor Effekten.
R1/Gesamt2 tatsächlich FAIL/UNKNOWN_STOP: Compiler2/WARNs erhalten,
Caller/Container2 und ChildknownEnds. Acht Driver-Typmetadaten/22 Readersteps;
GetInt32(1) wirft InvalidCastException bei gemeldetem DB_ID-smallint/System.Int16,
gegenüber dokumentiertem int. Null Folge-SQL, eine volle eigene Containment/
frische CID-/Namensabwesenheit; SQLcleanup/DB-/Inputabwesenheit nicht belegt,
closed false/71 Sources und Originale erhalten. Keine typed/Controls-Qualification.
Aktuelle Integration, danach geänderte DB_ID-int-Sourceprojektion; gemeinsames
Restbudget vier Kandidaten/Gesamt3–6, nächster Gesamt3 ist Checkpoint, kein Reset.

Aktueller TSK-004-Schnitt: [unabhängiger Sessionreader-/Fehlervertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_SESSION_READER_REVIEW.md).
PR234 vollständig geschlossen: sieben Head-/fünf Main-Gates, Main24478d42,
voller Tree/FF/Branches, 122 private Dateien gesichert/eigener Worktree archiviert.
VECTOR-C1 bleibt FAIL/UNKNOWN_STOP/SQLcleanup nicht belegt, kein weiterer Lauf.
Jetzt ausschließlich Quellen-/Source-/Fixtureprüfung für acht strikte Reader-
Typbindungen und sichere Fehlerenden; sechs Sourcekandidaten/Checkpoint3,
keine Compiler-/CLR-/SQL-/Container-/Modell- oder Hosteffekte. Öffentliche
Lesehilfe und gezielte Purekontrollen vor Rootreview/Privacy/Integration.
C1 SOURCE_ONLY kohärent: acht Projektions-/Getter-/NULLbindungen,
sieben neue normale/fünf geschützte Puremethoden mit bekannten PID-/Rawenden,
16 Guidelinks und enger unabhängiger Rootreview bestanden. Originale8Pins
unverändert, keine neuen Runtimeeffekte oder Rekonstruktion alter Exception.
STOP_AFTER_COHERENT_SOURCE_ONLY_PASS; Privacy und vollständige Integration folgen.

Aktueller TSK-004-Schnitt: [neue begrenzte VECTOR-Transportwelle](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VECTOR_TRANSPORT_REVIEW.md).
PR233 vollständig geschlossen, 142 private Dateien gesichert, eigener Worktree
tatsächlich archiviert. Loader-/Typmetadaten-PASS nach Checkpoint3 bleibt
gestoppt, alte VECTOR-Hard6/UNKNOWN-Welle unverändert. Neue geänderte Callerbasis
mit fünf literal Assetpfaden; sechs Kandidaten/Checkpoint nach drei, maximal
sechs eigene serielle Container, zwei synthetische Rows und native FLOAT32-/
NULL-/Dimensionskontrollen. Initiale Sourcevorbereitung vor Rootadmissions;
C1 danach tatsächlicher FAIL/UNKNOWN_STOP: ein Compile mit zwei CS1701-WARNs,
ein Container/sechs bekannte SQLcmdenden/ein Client, OPEN beendet,
Sessionreader-Ende unvollständig. Null Folge-SQL, einmal eigene gebundene
Containment und frische ganze CID-/Namensabwesenheit; SQLcleanup nicht belegt,
DB-/Inputabwesenheit false/closed false. Source-/Originalpins unverändert,
typed/NULL/Dimensions-/Controls nicht qualifiziert. Keine weiteren C2–C6;
vollständige Integration und danach unabhängiger reiner Reader-/Fehlervertrag.

Aktueller TSK-004-Folgeschnitt: [geänderte Loader-Auflösungsgegenprobe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_LOADER_RESOLUTION_REVIEW.md).
PR232 vollständig geschlossen, 84 private Dateien gesichert, eigener Worktree
tatsächlich archiviert. C1 bekannter Loader-FAIL bleibt erhalten. Sichtbarer
Folgeentscheid erlaubt C2–C6 innerhalb der bestehenden kumulativen Sechsergrenze,
Checkpoint nach C3; neue sichere Host-/Fehlermetadaten und gezielte eigene
Dateivarianten, ohne SQL oder globale Hoständerungen. Kein unveränderter Retry.
C2 tatsächlich bekannter Loader-FAIL, sicher erfasster Name Microsoft.Data.SqlClient:
DLL vorhanden, OwnClientInTpa false/TpaCount 201/APP_PATHS null. Vier Hostphasen
und Load-Exception beendet, C1-86-Pins unverändert, kumulativ zwei Compiler/zwei
Proben. C3 bereitet fünf literal eigene Unterpfade mit identischem C2-Build vor;
keine neue Kompilierung oder SQL-Verbindung, neue Rootgates vor der Einzelprobe.
C3 ist tatsächlich Loader-/Typmetadaten-PASS: identischer C2-Build, fünf
literal Dateien, acht API-Enden, eigene geladene SqlClient-SHA und beide Typen
belegt. C1-86-/C2-69-Pins unverändert; Checkpoint3, kumulativ zwei Compiler/drei
Proben, STOP_AFTER_LOADER_METADATA_PASS. C4–C6 nicht ausgeführt, SQL und volle
Treiberqualifikation weiterhin offen; kein Loader-PASS für den alten C6-Client.

Aktueller TSK-004-Schnitt: [getrennte lokale Assembly-Ladediagnose](../Documentation/Project_Planning/SQL_SERVER_2025_AI_LOADER_DIAGNOSIS_REVIEW.md).
PR231 vollständig integriert, synchronisiert und bereinigt; 138 private Dateien
gesichert und eigener Worktree tatsächlich archiviert. Neuer eigener Probehost
prüft ausschließlich benannte Assembly-/Typmetadaten, ohne SQL-Verbindung.
Sechs neue Diagnosekandidaten mit Checkpoint nach drei; frühere Hardstops bleiben
erhalten. Der Schnitt begann mit Sourcevorbereitung und getrennten Ausführungsgates.
C1 tatsächlich beendet: ein Compiler PASS und eine CLR-Probe mit bekanntem
Loader-FAIL/FileNotFoundException bei LOAD_SQLCLIENT, MissingAssembly UNKNOWN.
Runtime .NET 10.0.12 attestiert, Typprüfungen nicht erreicht, SQL null;
COHERENT_DIAGNOSIS_STOP, ursprüngliche C6-Ursache UNPROVEN. Keine volle Abnahme.

Aktueller unabhängiger TSK-004-Schnitt: [reiner Clientlayoutvertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_CLIENT_LAYOUT_REVIEW.md).
PR230 ist vollständig integriert, synchronisiert und bereinigt; 121 private
Dateien sind gesichert und der eigene Worktree tatsächlich archiviert.
ANN-Records bleiben COHERENT/WARN, das Replaypaket ist gestoppt.
Die neue reine Deps-/RID-/Pfad-/Hash-/Kollisionsprüfung erlaubt sechs
Sourcekandidaten mit Checkpoint nach drei Kandidaten, ohne neue Laufzeitwirkungen.
FileNotFound-Ursprung UNPROVEN; VECTOR FAIL_HARD6_UNKNOWN bleibt gestoppt. Volle
TSK-004/006-/Workstreamabnahmen und Human-/Providergrenzen bleiben offen.
C1-Bestandsauswertung FAIL wegen des nicht abgebildeten `resources`-Abschnitts;
Originale und FAIL gesichert. Konkreter C2-Sourcefolgeentscheid mit kumulativ
höchstens zwei Offlineprozessen/Reportversuchen, danach anhalten; Laufzeitbudget null.
C2 ist nach Ressourcenmetadatenkorrektur tatsächlich COHERENT/WARN abgeschlossen:
31 Dateien/28 Runtimeassets, fünf fehlende wörtliche Unterpfade bei vorhandenen
flachen DLLs. Originale und C1-Archiv51 unverändert, Paket STOPPED_AFTER_C2;
FileNotFound-Ursprung und Runtimequalifikation weiterhin nicht nachgewiesen.

Aktueller unabhängiger TSK-006-Schnitt: [reiner IDX-012-DML-/Rollenrecordvertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_RECORD_CONTRACT_REVIEW.md).
PR229 vollständig integriert/synchronisiert/bereinigt, tatsächlicher eigener
Worktreearchiv nach 391 gesicherten privaten Dateien. VECTOR Hard6UNKNOWN bleibt
gestoppt. Neuer Sourcevertrag6/CP3/hard6/0 neue Laufzeiteffekte; vorhandene Records
streng binden und fehlende Captures sichtbar lassen. Runtimejob/Selector unverändert,
volle TSK-006-/Workstreamabnahme offen.

C1-Offline-FAIL erhalten; C2 nach ausdrücklicher kumulativer Budgeterweiterung
bindet Base64-Marker-/Dateinamensbytes korrekt.13normal/3protected-O, anschließend
zwei historische Akten tatsächlich COHERENT/WARN;80Aktenfiles/Source5/Prepared2
unverändert,0Native. Captures NOT_ESTABLISHED, Paket STOPPED_AFTER_C2, keine
Runtimepromotion. Aktuelle Integration, danach unabhängiger statischer Driver-
Dependency-Pfadplan; volle TSK-004/006-Abnahmen offen.

`TSK-003` ist der gesondert autorisierte Planungsschnitt. Der Folgeauftrag autorisiert
die Umsetzung des Workstreams; konkrete Teilnachweise und offene Gates stehen in den
folgenden Einträgen und im kanonischen Ausführungsstand. Allgemeine Entwicklung bleibt `PAUSED`.
Umfang, Abhängigkeiten, Aufwand und Abnahme werden im
[Workstream-Plan §12](../Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md#12-priorisierte-arbeitspakete-und-abhängigkeiten)
gepflegt. Registry-REGISTERED bezeichnet Identität, keine Umsetzung.

Aktueller TSK-004-Teilschnitt: [nativer VECTOR-Caller](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md).
C5 bekannter State-FAIL vor typisiertem Client; eigener DB-/SQL-/CID-/Namens-/
Inputcleanup tatsächlich bestanden, UNKNOWN=false. C6 letzte Producerkorrektur
mit unverändert strengem Oracle und neuen gezielten reinen Tests vor Admission.
Nach C6 STOP dieses Sechserbudgets und PR-Integration; volle TSK-004-Abnahme offen.
C6 tatsächlich FAIL_HARD6_UNKNOWN: Statekorrektur bestanden, Child rc1 mit
FileNotFoundException und fehlenden individuellen Requests. Kein Folge-SQL/
SQLcleanup-PASS, Nativeinput erhalten; einmaliger gebundener Namespaceabbau
und frische ganze CID-/Namensabwesenheit bestätigt. Keine weitere Probe/Fix.
Unabhängig folgt reiner TSK-006-ANN-DML-/Rollenvertrag auf vorhandener Evidenz.

- [ ] `TSK-004`: Feature-/Build-/Providerqualifikation; lokale Docker-Qualifikation und [Podmanproben für alle acht implementierten Offline-Demos](../Documentation/Project_Planning/SQL_SERVER_2025_AI_PROVIDER_REVIEW.md) bestanden; [CL-Slice nach zwei Korrekturwellen FAIL](../Documentation/Project_Planning/SQL_SERVER_2025_AI_COMPATIBILITY_REVIEW.md), weitere Syntax-/Treiber-/Feature-/Providerpfade offen. [Neue begrenzte CL-Istwertqualifikation](../Documentation/Project_Planning/SQL_SERVER_2025_AI_CL_RESULT_REVIEW.md) vorAdmission: alte dreiContainer/FAILs bleiben erhalten; sechs neue Kandidaten/max12 zusätzliche eigene Container, Checkpoint3/hard6, zwei stabile Profile. Tatsächliche Skalare/24 NULL-Rejections jeProfil, tatsächliche Chunkrows/volleErrorfelder, kompletter CL170BaselineRestore/DB-/CIDcleanup. Acht reine Methoden/enger unabhängiger Quellenabschluss nach Dependency-P2-Closure PASS; Native zunächst offen, öffentlicheCL170Profile unverändert. NeueCL-C1 danach zweimal nativ bestanden:96 protokolliertePhasen ohneBootstrapqueries, sechs vollständigeSkalarrecords/48 nativeNULL-Rejections/sechsChunkrecords/16Vollstates/zweiBaselineRestores, eigeneDB/CID/Namen/Inputs abwesend/keinUNKNOWN. LowCL150/160 tatsächlicherError102/Severity15/State38/Line3/ProcedureNULL near= statt erzwungenem208, keinVerfügbarkeitsclaim; CL170 vollezweiChunks. AlleNativeframes/Caller/Quellen/Restores/Cleanup rein gebunden, keine SQLwiederholung. AlteFAILs und öffentlicheCL170Grenzen erhalten; aktuelleIntegration/volleTSK004Abnahme offen. Unabhaengiger [Engine-/CL-/Client-Dokumentschnitt](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY_REVIEW.md) im eigenenWorktreeSOURCE_ONLYvorbereitet; Quelle/empirischerTeilnachweis/UNQUALIFIEDtrennen,6/CP3/hard6,0neueSQL/CLR/Provider/Modelle/Container/Installs. PublikationerstnachvollstaendigemPR226-/Main-/Tree-/FF-/Cleanupabschluss; PoolUNKNOWNwellebleibtgestoppt,volleTSK004offen. PR226 vollständig geschlossen (10Head/8Main/Runtime, Tree/FF/Branches/eigener Worktree nach Belegsicherung). Unmittelbarer Engine-/CL-/Client-Dokumentschnitt: zwei Textkandidaten, drei Entscheidungsfälle, 15 lokale Links und enger Root-Aussage-/Produktprivacyabschluss; keine neuen Runtime-/Provider-/Modell-/Container-/Installwirkungen. Gesamte aktuelle Privacy-/PR-/Main-/Tree-/FF-/Cleanupgates folgen; native Binärbindung/float16/volle TSK004 offen. PR227 vollständig geschlossen (8Head/6Main/Tree/FF/Branches/gesicherte Belege/eigener Worktree archiviert). [Isolierte native VECTOR-Clientvorbereitung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VECTOR_CLIENT_REVIEW.md) mit vorhandenen SDK10.0.401 und projektlokalen SqlClient6.1.4: MATERIAL-Lizenz/Hash/Lock/Audit und Sourcegates vor Native, keine globale Installation/Host-/Fremdrepo-/Modelleffekte, ein Restore120s/40Pakete/150MB+Compile90s,6/CP3/hard6.0Native jetzt; volle Typ-/Wire-/Treiberabnahme offen, PoolUNKNOWNwelle gestoppt. Checkpoint3: C1-Konfigurations- und C2-150MB-FAIL erhalten; C2-SDK-Ende nur quellengestützt, fehlende individuelle Felder nicht rekonstruiert. C3 mit eigenem300MB-Scope/einem Compile ohne Restore in3,3033s/poll0/rc0 SOURCE_ONLY bestanden.31 gehaltene/27 ausgewählte Pakete, Lizenzen/Audit/Hashes und vier reine Gegenfälle normal/-O/enger Rootreview; null Provider-/SQL-/Container-/Modelle. Aktuelle Integrationsgates und unmittelbarer eigenständiger Nativecaller offen. PR228 vollständig geschlossen (8Head/6Main/Tree/FF/Branches/916 gesicherteFiles/Worktreearchiv). [Unmittelbarer Nativecaller](../Documentation/Project_Planning/SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md) SOURCE_ONLYvorbereitet: SourceC4–C6/hard6 ohneReset, max3neue eigene serielle Container/einer je Kandidat; vorhandenePackages, keine neuenDownloads/Restore/Hosteffekte. Aktuelle Source-/Oracle-/Request-/Input-/Deadline-/Test-/Rootgates vorNative; jetzt0Native/Modelle. VolleTSK004offen, PoolUNKNOWNgestoppt. C4 Source/Compile mit zwei CS1701-Warnungen vorbereitet; erster Namespaceversuch tatsächlicher FAIL vorCreate (USERPROFILE fehlte),2bekannteCLI-Enden/0SQL/Client/UNKNOWNfalse. OriginalclosedFalse/SQLcleanupNOT_ESTABLISHED erhalten. Root frische Namens-/Inputabwesenheit als No-create-Proof separat belegt, Temp-WARN/erste stderr-Grenze erhalten; C5 nur geänderte ENV-/Proof-Source vor neuerAdmission, C6 letzte Reserve, kein weitererCompile.
- [ ] `TSK-005`: lokaler Pfad und synthetisches Korpus; QRY-014 bis QRY-017 implementiert, Runtime-/Integrationsgate im aktuellen Nachweis.
- [ ] `TSK-006`: ANN-/Index-Lifecycle; nach `TSK-005`. [Konkretes lokales Freigabepaket](../Documentation/Project_Planning/SQL_SERVER_2025_AI_PREVIEW_DECISION.md) ausdrücklich genehmigt; [erster privater Prototyp nach zwei Korrekturwellen FAIL](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PREVIEW_REVIEW.md). [Begrenztes Zusatzbudget](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_RESUME_DECISION.md) ausdrücklich genehmigt, [beide zusätzlichen Kandidaten FAIL](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_RESUME_REVIEW.md); SQL-Restore und eigene DB-/Containerabwesenheit diesmal belegt. Ausdrücklich genehmigte einzelne [Parserdiagnose FAIL vor Setup](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PARSER_REVIEW.md), eigener Container abwesend, SQL-Recovery/SQL-Abwesenheit FAIL. Ausdrücklich genehmigter [Clientkorrekturkandidat FAIL vor Setup](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_REVIEW.md), separate SQL-DB-/Containerabwesenheit bestanden. Ausdrücklich genehmigte [einzelne Parser-/Previewdiagnose bestanden](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PARSER_PASS_REVIEW.md), tatsächlicher Restore 0 und separate DB-/Containerabwesenheit belegt. [Begrenzter ANN-Build-/Suchentscheid](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md) ausdrücklich genehmigt; [beide neuen Kandidaten FAIL](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_BUILD_REVIEW.md), eigener Index im zweiten Kandidaten erstellt, Generation UNKNOWN und vor Search angehalten. Beide tatsächlichen Restores und separate DB-/Containerabwesenheit bestanden. [Einzelner Metadatenentscheid](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_METADATA_DECISION.md) ausdrücklich genehmigt und [Metadatenaufnahme bestanden](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_METADATA_REVIEW.md): Version-Feld fehlt, Generation UNKNOWN. Zusätzlicher Benutzerauftrag autorisiert [begrenzten privaten Legacy-Signaturversuch](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_DECISION.md); [zweiter Kandidat mit zwei Ergebnislifecycles bestanden](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_REVIEW.md), je fünf distanzgeprüfte Rows und 5/5 Exact-Schnittmenge. Erster Kandidat FAIL erhalten; Generation UNKNOWN, Indexnutzung UNPROVEN. [Tatsächliche Planausgabe bestanden](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md): eigener Vector Index Seek mit fünf tatsächlichen Rows am festen ungefilterten Suchaufruf; Generation UNKNOWN. [Filter-/Ergebnisdiagnose zweimal bestanden](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_FILTER_REVIEW.md): breite Fenster Recall@5 1, enges Fenster null ANN- gegen fünf Exact-Rows und Recall@5 0/ROWS_BELOW_K. Gefilterte Indexnutzung UNPROVEN; begrenzter Messfolgeschnitt im kanonischen Ausführungsstand autorisiert. Historische Kandidatenbudgets bleiben verbraucht; neue Umfänge endlich begrenzen. IDX-011/IDX-012-Abnahme offen. [Begrenzte Messdiagnose](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_MEASUREMENT_REVIEW.md): Session-Nulldeltas WARN; zwei aktive Live-Request-Lifecycles ohne belegten ANN-Vorteil, Zeitquantisierung/Workergrenzen sichtbar; vollständige Demoabnahme offen. [Einzelne UPDATE-Diagnose](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_DML_REVIEW.md): zwei aktuelle Lifecycles mit tatsächlicher Verweigerung 42231/State 1 und Source-/Transaktionsrestore, erster Evidenz-FAIL erhalten; Freshness/allgemeine DML-Unterstützung offen. [DEC-074](../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md) qualifiziert den engen 17.0.5005.3-Profilpfad mit Generation UNKNOWN/WARN fachlich; öffentliche Implementierung und alle übrigen Abnahmegates bleiben offen. [Offlinevorbereitung des öffentlichen IDX-011-Benchmarkvertrags](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX011_BENCHMARK_CONTRACT.md) mit je fünf getrennten Warm-up-Requests, drei seriellen AB-/BA-/AA-Blöcken, 100 Queries je Messfenster und Qualität je Query; keine öffentliche Runtime-/TP-PERF-Abnahme. [Öffentlicher IDX-011-Controller und Runtimebefund](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX011_RUNTIME_REVIEW.md): erster Quellenoracle-FAIL erhalten; korrigierter stabiler Kandidat mit zwei vollständigen 2025-Läufen, je zwei 2019/2022-SKIPs und zwei kontrollierten Fehler-/Recoveryfällen; neun eigene Container vollständig entfernt, je positivem Lauf 1810 Einzelquerykontrollen. Generation UNKNOWN/WARN und enger Filterverlust bleiben; TP-PERF, fehlende Kosten-/Rollen-/Hard-Abortabnahme und IDX-012 offen. [Öffentliche IDX-012-DML-Grenzenvorstufe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md): zwei vollständige eigene Lifecycles, je vier erfolgreiche Kontrollen ohne Index und vier tatsächliche Verweigerungen 42231/State 1 mit Index; vollständige 999-Row-Quellen-/Metadatenprüfung und Restores/DB-/Containerabwesenheit bestanden. Freshness, Storage, Rollen, Hard-Abort und vollständige IDX-012-Abnahme bleiben offen. [IDX-012-Rebuildcheckpoint](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_REBUILD_REVIEW.md): beide begrenzten Kandidaten FAIL (Aliasparser, anschließend 42231 am statischen UPDATE); beide Restores/DB-/Containerabwesenheit bestanden. Ursprüngliches Budget beendet, tatsächliche Drop-/Compilegrenze und Freshness unbewiesen. Getrennte dynamische Compile-Folge nach vollständiger Checkpointintegration und Quellenclosure: einziger stabiler Kandidat mit beiden vollständigen Lifecycles erfüllt, tatsächlicher Drop/Commit Id 999/Rebuild, fünf distanzgeprüfte Suchkontrollen, Recall@5 1, übrige 998 Vektortexte unverändert und voller Cleanup. Freshness ausschließlich OBSERVED_AFTER_REBUILD_ONLY; vollständige Runtime-/TP-PERF-/Kosten-/Rollen-/Hard-Abortabnahme offen. [DB-Speicherfolge](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md) behält zwei FAIL-Ledger und belegt danach zwei vollständige Katalog-/DML-/Rebuild-Lifecycles, Originalrestores und unabhängigen eigenen Cleanup. DB-weite Seiten-/Dateipunktaufnahmen vorhanden; isolierte Indexkosten, Writes/TempDB/Worker sowie vollständige TP-PERF-Abnahme offen. [Phasenkostencheckpoint](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md): zwei native Client-FAILs vor Kosten-SQL, beide Originalrestores und unabhängiger eigener Cleanup bestanden; Ursprüngliches Zweikandidatenbudget geschlossen und Sperre über PR 177 integriert. Der Benutzer erweitert dieselbe lokale Kostenfolge auf sechs Kandidaten/zwölf serielle Container einschließlich C1/C2; C3 mit begrenzter literaler SQL-Eingabe bestand danach zwei vollständige eigene Lifecycles mit tatsächlichen Session-/TempDB-/DB-Dateikostenframes, allen DML-/Rebuild-/Source-/Storagekontrollen und vollständigem eigenem Cleanup. Quellenreview-P2 zum ungeklärten Prozessende vor Admission geschlossen; reine Index-/vollständige Workerkosten bleiben NOT_ESTABLISHED. [IDX-012-Versionsgrenze](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_VERSION_REVIEW.md) je zweimal auf tatsächlichem SQL2019/2022 vor Setup bestanden, neue read-only DB-Abwesenheit und unabhängiger eigener Containercleanup belegt. [Kontrollierte IDX-012-Recovery](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_RECOVERY_REVIEW.md) nach Setup und qualifiziertem Index-/Quellencheckpoint je zweimal bestanden: erwartetes FAIL_EXECUTION, tatsächliche Originalrestores 0/0, neue DB-Abwesenheit und eigener vollständiger Containercleanup. [Begrenzter IDX-012-Rollensplit](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md): zwei tatsächliche FAIL-Kandidaten erhalten, C3 mit zwei stabilen vollständigen Lifecycles nach Rechtegegenproben, Admin ausschließlich an beiden Indexbuilds und tatsächliche Operatorrückkehr, voller eigener DB-/Login-/SID-/Containercleanup. [Eigener idle Container-SIGKILL](../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_HARD_ABORT_REVIEW.md) zweimal nach fertig qualifiziertem Index-/Sourcecheckpoint bestanden: tatsächlicher Exit 137 ohne OOM, Wiederanlauf desselben CID, neue vollständige Snapshot-/999-Row-Sourcechecks und Originalrestores/DB-/CID-/Namenscleanup unter derselben 60-s-Deadline ab Kill. Öffentliche Multi-Login-API, absolute Minimalrollen, aktive Build-/DML-Unterbrechung, vollständiger Hard-Abort sowie Gesamt- und TP-PERF-Abnahme offen.
- [ ] `TSK-007`: Lokale öffentliche AiModel-Embeddingkomponente und fester Korpus bestanden ([Modellpfad](../Documentation/HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md), PR 215/216); SQL-Korpus tatsächlich gespeichert, vollständig zurückgelesen und mit Exact Top1 geprüft (PR 217). [Generatorwelle](../Documentation/Project_Planning/SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md) abgeschlossen als FAIL: sechs Kandidaten, 5 Inferenz-/31 Metadatenrequests, keine korrekte positive Antwort, Negativcases nicht gestartet, eigene Caller beendet und kein UNKNOWN. Hardstop; kein weiterer unveränderter Versuch. Öffentliches RAG bleibt an DEC-033/-P blockiert, allgemeiner SQL-HTTPS-Vertrag sowie optionale Cloud-/ONNX-Pfade offen; vollständige Provider-/TSK-Abnahme offen.
- [ ] `TSK-008`: QRY-018 Offline-Replay über PR 137 integriert. [Lokaler Modellkorpus](../Documentation/Project_Planning/SQL_SERVER_2025_AI_MODEL_CORPUS_REVIEW.md) und [SQL-Korpuskomponente](../Documentation/Project_Planning/SQL_SERVER_2025_AI_CORPUS_SQL_REVIEW.md) über PR 216/217 vollständig integriert: vier tatsächliche Vektoren, alle Koordinaten/Cosines und Top1 A unabhängig geprüft, Negativ-/Ownership-/Cleanupbelege. [Generatorwelle](../Documentation/Project_Planning/SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md) nach sechs Kandidaten FAIL und Hardstop; 5 Inferenz-/31 Metadatenrequests, kein positiver Antwort-PASS oder ausgeführter Enthaltungsfall, bekannte eigene Enden und kein UNKNOWN. C6 ergänzt deklarierte Glossarnormalisierung, ohne Oracles anzupassen. Voller Live-RAG, allgemeine Qualität und TSK-Abnahme bleiben offen.
- [ ] `TSK-009`: QRY-019, DGN-009 und DGN-008 integriert über PR 138/141/143 mit grünen Head-/Main-Gates; CON-010 unter der erweiterten lokalen Wellenfreigabe mit zwei stabilen privaten C5-Lifecycles und sechs genau gebundenen CONNECT-/SELECT-Grants wiederaufgenommen ([Teilnachweis](../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_RESUME_REVIEW.md)); drei historische FAILs und C4-Kollations-FAIL bleiben erhalten. Öffentliche CON-010-Demo jetzt IMPLEMENTED mit [lokalem Consumer-/Versionsnachweis](../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md): C1-Gegenproben-FAIL erhalten, C2 mit 192 Markerabweisungen und 16 tatsächlich erzeugten Fixturemanipulationen je gegen Baseline/Comparison sowie Setupidempotenz bestanden; je zwei aktuelle 2019-/2022-SKIPs vor Setup und vollständiger eigener Cleanup. C2-Head-CI-FAIL durch PRINT-/stderr und anschließender C3-CI-FAIL an eingefrorener gemeinsamer API bleiben sichtbar. C4 stellt gemeinsame API wieder her und projiziert nur feste positive Consumersummary als SELECT; sämtliche tatsächlichen Gegenproben/Versions-SKIPs und eigener Cleanup lokal bestanden. PR 184 mit aktuellen Head-/Main-Gates vollständig integriert, vollständige Treeübernahme, lokales main synchronisiert und eigener lokaler/Remote-Branch bereinigt; Pooling, Serverlogins, ANN und Seitenkanäle weiterhin UNQUALIFIED. DGN-008-Offline-Metadatenrechte sind [ohne Inferenz qualifiziert](../Documentation/Project_Planning/SQL_SERVER_2025_AI_EXTERNAL_MODEL_REVIEW.md). Tenant-/Datenschutz-/Providerfälle bleiben offen. Nach vollständig geschlossenem PR218 bestand die [begrenzte private Serverlogin-Komponente](../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_LOGIN_REVIEW.md) nativ in C5: echte drei Login-/User-/SIDbindungen, A/B/Unmapped, Spoof/Reset, drei Rechtefehler, fünf Eigentumsabweisungen, 23 Vollstates/Restore und tatsächlicher Login-/DB-/SQL-/CID-/Namens-/Inputcleanup; kein UNKNOWN. Fünf eigene Container/95 Clienthandles insgesamt, C5 60; vier historische FAILs erhalten, C1–C3 SQL-Abwesenheit NOT_ESTABLISHED. Checkpoint3/Budget eingehalten; PR219 mit acht aktuellen Head-/sechs Main-Gates, vollständigem Tree, FF-Synchronisierung und eigenem lokalem/Remote-Branchcleanup abgeschlossen. Öffentliche WITHOUT-LOGIN-Demo, Passwortintegrität/Pooling/ANN/volle Abnahme unverändert offen; danach unabhängige TSK-012-Belegleseaufgaben ohne neue Native. Unmittelbare [private Poolvorbereitung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_POOL_REVIEW.md): vorhandene öffentliche SqlClient-Oberfläche read-only bestätigt, kein Open/SQL/Poolclear; physische Server-DMV-/SID-/Session-/Noncebindung statt unbelegter Client-GUID-Stabilität. Sechs Kandidaten/max6 neue eigene serielle Container, CP3/hard6, je sechs Checkouts/300+ein60; Scope-Review geschlossen, private Codevorbereitung ohne Native, Source-/Review-/Admissiongate vor Native offen. Keine Installation, KI-Provider-/Cloud-/Hoständerung oder rote Standard-CI; volle Pool-/CON-010-/TSK-009-Abnahme offen. PR221 vollständig integriert (8 Head/6 Main, Tree/FF/Branches geschlossen). [Unabhängiger Poolquellenabschluss](../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_POOL_SOURCE_REVIEW.md): elf reine Pythonmethoden/drei AST-Helpergruppen sowie optimierte Gates PASS; C1 nativ FAIL mit bekanntem Childende/null Checkoutrecords, zehn SQLcmd-Handles plus ein separater Child; Namespace/CID/Name/SQLinputs abwesend, SQL-/Pool-Cleanup NOT_ESTABLISHED. Begrenzte Receiptdiagnose folgt unter neuer Admission. Dieselbe einmalige 60s-Cleanupdeadline beginnt vor dem höchstens 40s-Child; kein Clockreset. Die begrenzte private Poolkomponente bestand in C3: sechs Checkouts, drei physische Wiederverwendungen/getrennte Poolkeys, zwölf vollständige Before-/After-Ergebnisse, Reset vor Reparatur, zwei identische Vollstates und tatsächlicher Pool-/Login-/DB-/SQL-/Container-/Inputcleanup; kein UNKNOWN. Drei eigene Container/37 SQLcmd-Handles plus drei separate Poolchildren, C3 17; beide historische FAILs und C1/C2 SQL-/Pool-Cleanup NOT_ESTABLISHED erhalten. Rootsource-/Recordreview und Checkpoint3 geschlossen; keine weitere Probe nach PASS. Aktuelle PR-/Main-Gates/Integration/FF/Branches vor Abschluss; volle öffentliche Pool-/CON-010-/TSK-009-Abnahme offen. PR222 vollständig integriert (7 Head/5 Main, Tree/FF/Branches geschlossen). [Reiner öffentlicher Poolrecordvertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_RECORD_REVIEW.md) folgt mit 6/CP3/hard6, null neuen SQL-/Container-/Modell-/Metadatenaufrufen, C1-Offline-C3Replay FAIL wegen zusätzlichem nicht erfasstem predicates.operation; transparenter Wechsel auf max6 geänderte Quellenkandidaten/je1Replay/insgesamt6/CP3/hard6 unter den erweiterten lokalen Benutzerfreigaben, C1 verbraucht, keine Originaländerung; fehlende individuelle Request-/Returncode-/Inputcaptures NOT_ESTABLISHED, kein öffentlicher Runtime-PASS. Öffentlicher reiner Poolrecordconsumer implementiert:14 gezielte reine Methoden/optimierte Schutzgates PASS; C1-OfflineFAIL an nicht erfasstem predicates.operation erhalten, C2 unveränderter C3-Payload kohärent PASS/Gesamtstatus WARN mit zwei fehlenden individuellen Request-/Inputcapturegates NOT_ESTABLISHED und nicht unabhängig attestierter Callerprovenienz. Zwei Quellenkandidaten/zwei Reports, null neue SQL-/Container-/Modell-/Metadatenaufrufe; aktuelle PR-/Main-Gates/Integration/FF/Branches vor Abschluss. Öffentlicher authentifizierter Producer/Admission/Capture/Recovery und volle CON-010-/TSK-009-/TP-CON-Abnahme offen. PR223 vollständig geschlossen (8 Head/6 Main, Tree/FF/Branches). [Öffentliche V2-Capturevorstufe](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_CAPTURE_REVIEW.md) SOURCE_ONLY: tatsächliche öffentliche Sources, Processende≠TDS, InputSHA vorENVExpansion und Credentialprüfung vorDigests;6/CP3/hard6, null neue Prozesse/SQL/Container/Modell-/Metadatenaufrufe, V1 unverändert. Öffentlicher RED-Producer/Nativeadmission separat offen. PR224 vollständig geschlossen (8 Head/6 Main, Tree/FF/Branches). [Öffentlicher SQLcmd-Clientadapter](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_CLIENT_REVIEW.md) SOURCE_ONLY: tatsächliche API-/Handlebindung, sticky UNKNOWN, Privacy/Deadlines;6/CP3/hard6, null lokale echte Prozess-/SQL-/CLR-/Container-/Modell-/Provideraufrufe, betroffene CI bleibt Pflicht. Voller Producer/Runtime offen. PR225 gemergt/10 Head PASS, Main-/Sync-/Cleanupabschluss läuft im Orchestrator. [Öffentlicher opt-in Poolproducer](../Documentation/Project_Planning/SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md) im eigenen Worktree SOURCE_ONLY vor lokaler Nativeadmission: drei neue eigene Logins/zwei VECTOR(3)-Rows/sechs Checkouts, vollständige tatsächliche Evidenz-/Privacy-/Cleanupverträge;6/CP3/hard6, null lokale Domainprozesse/SQL/Container/Provider-/Modelle. Native erst nach PR225-Gesamtclosure und aktueller Quellenabnahme; max6 neue eigene serielle Container/einer je Kandidat, keine Host-/Cloud-/ONNX-/Fremdrepo-/Default-RED-Effekte. PR225 jetzt vollständig geschlossen (10 Head/8 Main/Runtime, Tree/FF/Branches). Öffentliche Poolproducer-Sourcevorbereitung im eigenen Worktree bleibt vor lokaler Nativeadmission: aktuelle Source-/Privacy-/Test-/Rootgates nötig, 6/CP3/hard6/max6 eigene serielle Container, voller Runtime-/TP-CON-Nachweis offen. Öffentlicher Producer C1 known FAIL vor Create an beschränkter Podman-CLIumgebung; Source18/Privacy11/AST3 geschlossen, null neue Container/SQLcmd-/Poolchildren, CID NOT_CREATED/SQLcleanup NOT_ESTABLISHED, historische closedFalse bleibt. Neue reine Namensdiagnose tatsächlich leer; enge geänderte Source-/No-create-Failkorrektur vor C2, keine Native ohne neue Rootadmission. Öffentliche Pool-Nativewelle STOP nach C2: ein eigener Container,0SQLcmd/Poolchildren/Modelle; C2-FeldcaseFAIL und urspr. SQL-/Namespacecleanup NOT_ESTABLISHED. Gebundener Root-rm-TimeouteffektUNKNOWN sticky, frische ganze CID/Name/Inputs abwesend ohne zweitesrm/FolgeSQL. KeinC3, reine betroffene Sourcekorrektur/Integration geht weiter; öffentlicheRuntime/TSK009/TP-CONoffen. Korrigierter öffentlicher SOURCE_ONLY-Schnitt:25neueMethoden,zuletzt4betroffene normal/-O Originalkanäle PASS, aktuelle15Sources/AST3/Privacy11/Rootreview geschlossen; .ID/no-trunc/time0/stickyRemoveUNKNOWN und expliziteStoppsperre. C1/C2FAIL/RecoveryUNKNOWN erhalten, öffentlicheRuntimeNOT_ESTABLISHED; aktuellePR/Head/Main/Tree/FF/Branches/eigenerWorktreeabschluss folgt.
- [ ] `TSK-010`: Benchmarks/Diagnose; nach `TSK-006` und `TSK-009`, Inferenz zusätzlich `TSK-007`. [Private RES-008-Quellen-/Dimensions-/Storagevorbereitung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_DIMENSION_REVIEW.md): C1-nativer Oracle-FAIL erhalten; C2 mit zwei vollständigen stabilen Lifecycles, je 400 vollständigen Quellen, tatsächlicher DELETE-Gegenprobe und Restore sowie unabhängigem eigenem Cleanup bestanden. RES-008 bleibt PROPOSED; Performance, TP-PERF, ältere Engines und öffentliche Demoqualifikation offen. [Begrenzte private Messfolge](../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_MEASUREMENT_REVIEW.md): C1-Zeit-FAIL erhalten; C2 mit je 20 Warmups, 54 seriellen AB-/BA-/AA-Fenstern und 5420 Queryoracles, tatsächlicher Querynegative und vollem Source-/Config-/Cleanupnachweis zweimal bestanden. [Repräsentative Actual-Pläne](../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_PLAN_REVIEW.md): C1-Root-FAIL erhalten, C2 zweimal vier tatsächliche eigene Scans100/Ergebnisroot1 mit Memoryattributen und vollständigem Source-/Config-/Cleanupnachweis bestanden; 24 synthetische Gegenfälle und enger Quellenabschluss. Waits/Warnings NOT_CAPTURED; öffentliche Qualifikation, vollständige Worker-/Spill- und TP-PERF-Abnahme offen.
  - [Öffentlicher begrenzter RES-008-Consumer](../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_PUBLIC_REVIEW.md): zwei Vollprofile, vier Versions-SKIPs vor Setup und eindeutig attestierter Setupfault mit vollständigem eigenem Cleanup lokal bestanden. Beobachtungs-WARNs bleiben sichtbar, Status PROPOSED; öffentliche FWK-011-Aggregation, vollständige Demo-/TP-PERF-/Modulabnahme weiterhin offen.
  - [Begrenzte öffentliche RES-008-Aggregation](../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md): zwei vorhandene native Profile ohne SQL-Retry, je 30 numerische FWK-011-Invarianten, 25 reine und drei CLI-Gegenfälle sowie enger P2-Abschluss bestanden; Warmups/AA getrennt, N/A/Nullwerte/Ausreißer sichtbar. Gesamt-WARN/PROPOSED und volle Worker-/TP-PERF-/Modulabnahme offen.
- [ ] `TSK-011`: SQL-Assistenz/Gegenmessung; nach `TSK-005` und `TSK-009`. [Private DGN-010-Ergebnis-/Storagevorbereitung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_INDEX_HYPOTHESIS_REVIEW.md) bestand ohne Performanceclaim; vollständige TP-PERF-Abnahme bleibt offen, Demo PROPOSED. [Private Actual-Ownerpläne](../Documentation/Project_Planning/SQL_SERVER_2025_AI_INDEX_PLAN_REVIEW.md) zweimal mit tatsächlichem Planwechsel/Build/Drop, vollständigen Source-/Query-/Readeroracles und eigenem Cleanup bestanden; Ownerpläne ersetzen keine Reader-/Performance-/DML-/AB/BA/AA-Qualifikation. [Private feste Readerbatchmessung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_INDEX_MEASUREMENT_REVIEW.md): C1-Counter-FAIL erhalten, C2 zweimal je zehn Warmups/18 AB-/BA-/AA-Fenster und 1810 vollständige Queryoracles mit unveränderter Quelle/Config/Rechten sowie eigenem Cleanup bestanden; beide Indizes während Messung vorhanden, erzwungene Pfade mit Buffer-/Impersonationaufwand, AA separat. Kein Indexabwesenheits-Nettonutzen/isolierte Query-/DML-/vollständige Workerkosten oder voller TP-PERF-/Modulnachweis; DGN-010 PROPOSED. [Private DML-Effektseparation](../Documentation/Project_Planning/SQL_SERVER_2025_AI_INDEX_DML_REVIEW.md) C1 zweimal mit je 1810 tatsächlichen UPDATEs/18100 vollständigen OUTPUT-Rowkontrollen ohne/mit Candidateindex, getrennten AB/BA-/AA-Samples, vier Build-/Dropzyklen außerhalb Messung und 46 vollständigen Source-/Config-/Reader-/Indexprüfungen bestanden; eigener Rollback, Source-/OUTPUTnegative/Restore und vollständiger Cleanup gebunden. OUTPUT-/Transaktions-/Rollbackaufwand enthalten; ungezwungener SELECTvergleich, Nettonutzen, weitere Kosten und öffentliche/full-TP-PERF-Abnahme offen. [Privater ungezwungener SELECTvergleich](../Documentation/Project_Planning/SQL_SERVER_2025_AI_INDEX_SELECT_REVIEW.md) C1 zweimal mit je zehn Warmups/18 AB-/BA-/AA-Fenstern, 1810 vollständigen Queryoracles, vier Build-/Dropzyklen außerhalb Messung und vollem Source-/Config-/Reader-/Negativ-/Cleanupnachweis bestanden. Kein INDEX-Hint, Buffer-/Impersonationaufwand enthalten; aktuelle Readerpläne/Indexnutzung, Indexnettonutzen, weitere Kosten und öffentliche/full-TP-PERF-Abnahme offen. DGN-010 PROPOSED; öffentliche Paketvorbereitung folgt. [Öffentlicher reiner Auswertungsvertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_BENCHMARK_CONTRACT.md) mit vollständiger SELECT-/DML-/Source-/Request-/Ordinal-/Rollbackdepthbindung, getrennten Warmups/AA und zwei festen FWK-Verträgen; 20 synthetische Methoden und enger unabhängiger Quellenabschluss bestanden, vier vorhandene gebundene Native-Records mit 48 numerischen FWK-PASSs rein erneut geprüft, null SQLwiederholungen. Runtime-/TP-PERF NOT_ESTABLISHED; öffentlicher Producer/Versions-/Marker-/Recoveryqualifikation folgt. [Öffentlicher begrenzter Producer](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_PUBLIC_REVIEW.md) C2 mit je zwei SELECT-/DML-Profilen, acht Versions-SKIPs und zwei Setupfaults/Recovery; C1-Editions-FAIL erhalten, alle 23 eigenen Container geschlossen. 184000 Source-Rows/116 positive Fensterframes/acht Native-Negative/48 numerische FWK-PASSs gebunden. Gesamt-WARN/NOT_ESTABLISHED und PROPOSED; vollständige Marker-Manipulationsqualifikation, Readerpläne/weitere Kosten/full-TP-PERF-/Nettonutzen-/Modulabnahme offen. PR196 vollständig integriert und bereinigt; [vollständige native Markerqualifikation](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md) vor Admission vorbereitet: sechs Quellenkandidaten/zwölf lokale Container, 192 Abweisungen/24 Restores je Lifecycle; native Resultate noch offen. Native C4 danach zweimal vollständig bestanden: 384 echte Markerabweisungen/482 Vollstates/48 Restores, fünf eigene Container geschlossen und drei historische FAILs erhalten. Aktuelle Head-/Main-/Integrationsgates folgen; Readerpläne/weitere Kosten/full-TP-PERF offen. Unmittelbare Folge: [begrenzte tatsächliche private Reader-Indexnutzung](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_USAGE_REVIEW.md), C1 zweimal nativ bestanden: sechs Queryfenster mit tatsächlichen PK→Candidate→PK-Seeks, voller Source-/State-/Negativ-/Cleanupnachweis; PR-/Main-Gates folgen, anschließend begrenzte INSERT-/Rollbackkosten. Readerpläne/Nettonutzen/full Runtime offen. Nächster [begrenzter privater INSERT-/Rollbackkosten-Schnitt](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_INSERT_REVIEW.md), C1 zweimal nativ bestanden, 3620 Benchmark-INSERTs plus2 Controls/3622 tatsächliche Rollbacks, vollständige Source-/State-/Negativ-/Cleanuporacles; höhere Candidate-Batchmediane, kein Nettonutzenclaim. PR-/Main-Gates und volleAbnahme offen. Nächster [begrenzter Readerplanschnitt](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md): C1–C6 FAIL, harte Grenze erreicht; alle sechs eigenen DB-/Containerlifecycles sicher geschlossen, kein UNKNOWN. C6-Sourcebindung erreicht, Ereigniszeitvergleich offen; kein Native-PASS. FAIL-Checkpoint PR200 vollständig integriert und bereinigt. [UTC-Folgewelle](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md) registriert: kumulativ C7–C12/max18 Container einschließlich alter sechs, Checkpoint C9/hard C12, C7 zweimal nativ bestanden, sechs tatsächliche Originalreaderpläne/Root10+Source10/Runtime101110, volle Source-/State-/Negativ-/XE-/DB-/Containeroracles; historische FAILs erhalten. Private Beobachtung PASS, PR-/Main-Gates und volle Abnahme offen. Nächste [getrennte Build-/Dropkostenfrage](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md) vor Admission gebunden: sechs Kandidaten/max12 serielle eigene Container, zwei stabile Profile, volle Request-/DDL-/Lease-/Source-/State-/Negativ-/Cleanuporacles. C1 zweimal nativ bestanden: acht DDL-Fenster, 16000 Source-Rows, 20000 Vollstate-Rows, vier echte Negativen und beide eigene Container abwesend/kein UNKNOWN; aktuelle PR-/Head-/Main-/Integrationsgates folgen. Nettonutzen/volle Abnahme bleiben offen. PR205 vollständig integriert und bereinigt. Unmittelbare [reine Indexseitenfolge](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_INDEX_PAGES_REVIEW.md) auf exakt gebundenen vorhandenen Records: PK18/33, Candidate17/33 Used/Reserved Pages, fünf A/B/A/B/A-Aufnahmen je Profil, drei Gegenproben und null neue SQLcalls/Container; keine volle Speicher-/Nettonutzenabnahme. PR206 vollständig integriert und bereinigt. [Öffentlicher reiner Kostenrecordvertrag](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_CONTRACT.md): 15 synthetische Gegenproben/enger unabhängiger Quellenabschluss PASS, zwei vorhandene vollständige Native-Records rein neu gebunden, volle datetime2(7)-Ordnung/nullable Typen/Statekontinuität. Beide Samples/Nullen/exakte Mediane und A/B/A/B/A-Indexallokationen getrennt; keine neue SQL-/Containerausführung oder Runtime-/Nettonutzenabnahme. Producerintegration folgt. PR207 vollständig integriert und bereinigt. [Feste öffentliche Kostenproducer-Eingaben](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_INPUT_REVIEW.md): reine SQLtextkomposition, sechs Gegenproben und enger unabhängiger Quellenabschluss PASS; vollständige DB-/Marker-/Source-/Held-Leasebindung, acht vorhandene Native-Leases rein angebunden. Kein Client/SQL/Container, kein neuer Nativeclaim; tatsächlicher Kostencontroller/Versions-/Runtimequalifikation folgt. PR208 vollständig integriert und bereinigt. [Öffentlicher begrenzter Kostencontroller](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_CONTROLLER_REVIEW.md): elf synthetische Controller-/sieben Eingabemethoden und enger unabhängiger Quellenabschluss PASS; volle Source-/State-/Lease-/Negativ-/KnownEnd-/Parentdeadline-/Owninput-/Cleanupbindung. Neue Controller-Nativequalifikation offen, keine lokalen Qualifikationscontainer; tatsächliche Integrations-CI mit bestehender Versionsmatrix erforderlich. Producer WARN/DGN-010 PROPOSED; getrennte Nativequalifikation folgt. PR209 vollständig integriert und bereinigt. [Separate native öffentliche Kostenqualifikation](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_PUBLIC_REVIEW.md) vor Admission registriert: sechs Quellenkandidaten/max12 neue eigene serielle Container, Checkpoint3/hard6; zwei2025positive, je zwei2019/22-SKIPs vorSetup, ein2025Setupfault mitRecovery. Enger unabhängiger neuer Adapterabschluss/aktuelle EOL-Quellenbindung bestanden; Native zunächst offen, WARN/PROPOSED/volle Abnahme erhalten. Öffentliche Kosten-C1 danach nativ vollständig bestanden: zwei2025positive/WARN, vier Versions-SKIPs vorSetup und ein erwarteter Setupfault/Recovery; 97 protokollierte Nativephasen ohne Bootstrapqueries, acht DDL-Fenster, 16000 Source-/20000 Vollstate-Rows, vier echteNegativen/Restore und alle sieben eigenen Lifecycles/Inputs geschlossen. Native-Vollframes/Records/Caller/Quellen/Aggregate/Cleanup rein gebunden, keine zusätzliche SQLwiederholung; EOL-Helfer-Ablaufbefund erhalten. Begrenzte QualifikationPASS, PROPOSED/WARN/volle Abnahme offen; aktuelle Integrationsgates folgen.
- [ ] `TSK-012`: Curriculum/Masterdeck/Notes/Lehrmaterial; nach `TSK-008`–`TSK-011` und Demoabnahmen. [Offline-Arbeitsheft](../Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md), Glossar und [Trainerleitfaden](../Documentation/HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md) als begrenzte Teilentwürfe für acht qualifizierte Basisdemos plus getrennte RES-008-Ergebnisleseaufgabe aus gebundenen Aggregaten; einzige Lösung/Rubrik im Arbeitsheft, keine neuen SQL-Läufe oder gemessene Lehrzeiten. Der [eigenständige KI-Foliensatz](../Presentations/AI_SQL_Server_2025/README.md) enthält nach dem erweiterten Einsteigerauftrag jetzt 61 editierbare Folien und 61 Sprechernotizen, davon 27 neue Einführungsfolien mit einem durchgehenden Wissensbasisfall, erklärten Einstiegshürden und einer angeleiteten read-only Vektorvorführung, konkrete Demoaufträge, Quellen und alle 18 registrierten Demoentwürfe; Paket-/Privacy-/Renderprüfung bestanden, reproduzierbare Masterquelle vorhanden. Nach ursprünglicher Office-Ablehnung Datumsnamespace korrigiert und tatsächliches Öffnen, Text-/Tabellen-/Notizenbearbeitung sowie Speichern/erneutes Öffnen in PowerPoint 16.0 bestanden; negative Regression ergänzt. Neun IMPLEMENTED/neun PROPOSED, historische Quellenbindung und nachfolgender privater Readerplannachweis bleiben getrennt. RES-008 PROPOSED; vollständiges Curriculum, Teaching Paths, Teilnehmererprobung und Generalprobe bleiben offen. [Konkrete Teaching Paths des 61-Folien-Decks](../Documentation/HowTo/SQL_SERVER_2025_AI_TEACHING_PATHS.md) vorbereitet: gemeinsamer90-Minuten-Einstieg, BASIS240brutto/210netto/30Pause, STANDARD480/420/60 mit acht Offlineaufgaben, VERTIEFUNG960/840/120 über zwei Tage. Aktuelle kanonische Fenster ersetzen150/390/640 als Lehrplanung des erweiterten Decks; alte Modulgewichte nurhistorisch. Trainer-/Folienmaterialauswahl abgeglichen; keine neuen Lösungen/Rubrik, keine Deck-/SQLausführung oder Teilnehmerabnahme. TSK012/014 bleiben offen. Nach vollständig geschlossenem PR219 folgen drei optionale Evidenzleseaufgaben in Arbeitsheft/Trainerleitfaden zu tatsächlichem lokalem Embedding/SQL-Retrieval, gescheiterter Generation und begrenzter authentifizierter Tenant-Trennung. Einsteigerfolge Zweck/Erwartung/Beobachtung/Grenze, Lösungen und getrennte optionale 0–2-Punkte-Rubrik nur im Arbeitsheft; Basis16 und RES-008 unverändert. Keine neue Modell-/SQL-/Container-/Office-Ausführung oder Unterrichts-/Lernwirksamkeitsabnahme. Ein Owner/enges Rootreview, sechs Textkandidaten/CP3/hard6; PR220 mit acht aktuellen Head-/sechs Main-Gates, voller Treeübernahme, FF-Synchronisierung und eigenem lokalem/Remote-Branchcleanup abgeschlossen.
- [ ] `TSK-013`: Runtime-/Negativ-/Cleanupqualifikation; nach `TSK-005`–`TSK-011`. [Getrennte Kostencontroller-CI-Abnahme](../Documentation/Project_Planning/SQL_SERVER_2025_AI_DGN010_COST_CI_REVIEW.md) vorbereitet: zwei2025WARN, je zwei2019/22Versions-SKIPs und eine2025Setup-Recovery verpflichtend; reine Consumer-/Selectortests PASS, tatsächliche aktuelle Matrizen noch offen. Keine neue lokale SQLwiederholung; PROPOSED/WARN/volle Abnahme erhalten.
- [ ] `TSK-014`: Generalprobe/Workstreamabnahme; nach `TSK-012` und `TSK-013`.

Der gezielte Benutzerauftrag vom 2026-10-09 nimmt ausschließlich Prüfung und
Abschluss der bestehenden G13-Reporterarbeit in PR 68 sowie den vollständigen
Arbeitsabschluss nach DEC-069 wieder auf. Der
[G13-/PR-Review](../Documentation/Project_Planning/DGN_007_G13_PR_REVIEW.md) ist
für diesen Schnitt maßgeblich. Allgemeine Entwicklung, Automation und ausdrücklich
zurückgestellte Arbeiten bleiben pausiert. Historische HOLD-/CI-Befunde weiter
unten bleiben Nachweise ihrer jeweiligen Version und ersetzen keine aktuelle CI.
Die neue CI am Reporter-Head `f9ec582…` scheiterte auf 2022 an SQL20 und auf
2025 an G13 (−0,8298 ms). Der Code ist technisch blockiert; PR68 ist für den
getrennten Dokumentationsabschluss vorübergehend geschlossen, sein Branch bleibt
wegen nicht übernommener Arbeit erhalten. Der zusätzliche Scopeentscheid ist
beim Benutzer angefragt. Der vorherige Matrix-PASS wird nicht als Freigabe oder
Behebung umgedeutet.

## Aktueller operativer Einstiegspunkt

Die Entwicklung wurde am 2026-10-07 nach der über PR 92 dokumentierten Pause
ausdrücklich mit den bisherigen Regeln wieder aufgenommen. Diese Wiederaufnahme ist
seit dem Benutzerstopp vom 2026-10-08 abgelöst: Die Automation ist `PAUSED`;
ausschließlich der bereits laufende §33-DESIGN-/PR-Abschluss und eigener Cleanup
werden beendet. Neue Aufgaben einschließlich SESSION_END beginnen erst nach
neuem ausdrücklichem Auftrag. Der Orchestrator und seine Subagents werden danach
beendet;
offene Schritte, erhaltene ungemergte Arbeit und Startverfahren stehen in
[CURRENT_EXECUTION_STATUS.md §0](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Die separat vorgewählte vollständige Bootstrapfixture und reine Größenprüfung
sind in [§11 des Profilbindungsentwurfs](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture)
belegt: Die gemeinsame Metadata des Tupelkandidaten überschreitet das unveränderte
Cap bei allen drei Ordinals. Der getrennte [Stringpoolentwurf §12](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf)
liegt als `DESIGNED` vor. Der eigene [reine Pool-Sizer §13](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer)
bestand 37/37 isolierte Gegenproben ohne SKIP und eine vollständige neue
3×5-Größenprüfung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte,
unabhängig vollständig nachgerechnet und rückgewonnen. Keine erneute Aufnahme
oder Nonce. Der eigene experimentelle Codec-/Digestpfad nach dem konkreten
[Vertrag §14](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests)
bestand 41/41 isolierte Gegenproben ohne SKIP, unabhängigen Quell-/Testreview
und die vollständige Originalfixture: 3×5 Frames, Feldrückgewinnung,
kanonischer Repack und neun eigene Digestwerte, Gesamtausgabe
28.264/28.257/28.246 Bytes. Unabhängige Nachrechnung aus unveränderten Eingaben
bestätigt, ohne Codec-/Helper-Replay. Der eigene reine
[kombinierte Eingangsprototyp §15](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen)
bestand 34/34 isolierte Gegenproben ohne SKIP und die vollständige Originalfixture:
drei Frames zu jeweils 140.226 Bytes, davon 9.389 Metadata einschließlich Header
und 130.837 unveränderte Bodybytes. Vollständige tatsächliche Rückgewinnung,
Repack und unabhängige Stdlib-Nachrechnung ohne Replay bestätigt.
Die konkrete operative Format-/Bootstrap-/Kanalreihenfolge liegt getrennt in
[§16](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
als `DESIGNED` vor. Der reine [Kontrollbootstrapquellengenerator §17](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen)
bestand 32/32 isolierte synthetische Gegenproben ohne SKIP. Die getrennte [Sysconfig-Vorinitialisierung §18](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Frische operative Auswahl, inline Empfang und Reporting, Parent-/Worker-Anbindung,
Loader, Consumption, Replay und unabhängiger Cleanup bleiben getrennte Gates;
die charakterisierte Fixture ist keine operative Workerbaseline.

Der kanonische aktuelle Fortschritt, die Abhängigkeiten und der nächste ausführbare Schritt stehen in [`Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md`](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md). Die priorisierte Folgeplanung steht in [`Documentation/Project_Planning/NEXT_DEVELOPMENT_WAVES.md`](../Documentation/Project_Planning/NEXT_DEVELOPMENT_WAVES.md). Historische Fortschrittsmarker im Masterplan dürfen diesen Status nicht widersprechen.

Der reine begrenzte Header-/Metadata-Vorschnitt aus gehaltenen Chunks nach
[§23](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme)
ist implementiert und unabhängig geprüft: einziger isolierter Lauf mit
174/174 PASS ohne SKIP; fünf bisherige Builder und 149 alte Tests erhalten.
Die reine [K-Domain-/Commandquelle §24](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands)
ist im einzigen isolierten Lauf mit 209/209 PASS ohne SKIP geprüft;
sechs bisherige Builder und 174 alte Tests bleiben erhalten.
Die reine [Inline-Metadata-Callerquelle §25](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich)
ist nach zwei engen Fixturekorrekturen mit 243/243 PASS ohne SKIP geprüft;
sieben bisherige Builder und 209 alte Tests bleiben erhalten.
Die reine [Inline-Rawbodyaufnahme §26](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies)
ist nach einer Fixturelabelkorrektur mit 272/272 PASS ohne SKIP geprüft;
acht bisherige Builder und 243 alte Tests bleiben erhalten.
Die reine [Profilrecord-Reassemblierung §27](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords)
ist im einzigen isolierten Lauf mit 304/304 PASS ohne SKIP geprüft;
neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei neue
Fixturelabelkorrekturen wurden vor dem ersten Lauf geprüft.
Die reine [Inline-Profil-Callerquelle §28](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich)
ist im einzigen isolierten Lauf mit 341/341 PASS ohne SKIP geprüft;
zehn bisherige Builder und 304 alte Tests bleiben erhalten.
Die additive reine [R→BODY_RELEASE-Planquelle §29](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#29-deklarativer-rbody_release-plan)
ist im einzigen isolierten Lauf mit 378/378 PASS ohne SKIP synthetisch geprüft:
vollständige Actual-/Caller-R4- und unabhängige K8-Bindung vor Command-SHA,
gehaltene äußere Anker und atomare reine Rückgabe; elf alte Builder und
341 alte Methoden bleiben erhalten. Phasenlabels attestieren weder vorherige
Übergänge noch Einmalverbrauch. Der separate
[INPUT_COMPLETE-Recordvertrag §30](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#30-deklarativer-input_complete-rückkanalrecord)
ist als reine additive Quelle implementiert und im einzigen isolierten Lauf mit
413/413 PASS ohne SKIP geprüft: vollständige Caller-/Receivedformen und Semantik,
kanonische Actualbytes, eigene vollständige K-Domainbindung und dominante POSTs.
Zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige
[Record-/Footer→R-Calleradapter §31](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#31-vollständiger-deklarativer-profilrecord-callerabgleich)
ist rein additiv implementiert und im isolierten synthetischen Lauf mit
460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden
bleiben erhalten. PR 118 ist vollständig integriert; geprüfte Basis ist
`f6559e084ebd660a41a503129f1a28c32be8848b`. Die getrennten CI-/Übernahme-/Cleanupbelege
stehen in [CURRENT_EXECUTION_STATUS.md §0](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Die eigene lokale [Ledgerkomponente §32.5](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente)
ist mit 66/66 isolierten synthetischen Methoden ohne SKIP geprüft.
Der vollständige [Loaderrecordvertrag §33](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Operativer Workerbetrieb und Ressourcen-Cleanup bleiben getrennte Gates.

## Welle 0 - Fachliche Konsolidierung

- [x] `W0-001` Quellenmanifest für Folien, Dokumente und vorhandene Demo-Artefakte erstellen.
- [x] `W0-002` Privacy- und Metadaten-Prüfverfahren definieren.
- [x] `W0-003` Folien- und Aussagenregister erstellen.
- [x] `W0-004` Kritische Bestandsaussagen gegen aktuelle Primärquellen prüfen.
- [x] `W0-005` Fehlende Themen nach Lernwert, Demo-Eignung, Aufwand, Risiko und Versionsbezug priorisieren.
- [x] `W0-006` Projektweites Quellenregister mit Pflege- und Gültigkeitsfeldern strukturieren.
- [x] `W0-007` Verbindlichen Terminologie- und Schreibstandard festlegen.
- [x] `W0-008` Konflikt- und Entscheidungslog mit Blockerwirkung und Folgearbeit einführen.
- [x] Gate A fachlich abnehmen.

## P0 - Voraussetzung

- [x] Folien, Dokumente und vorhandene Demo-Artefakte vollständig inventarisieren.
- [x] Jede fachliche Aussage der Welle 0 gegen aktuelle Primärquellen prüfen.
- [x] Curriculum-Themen, Folien und geplante Demo-IDs eindeutig zuordnen.
- [x] Kanonisches Namensschema der Demo-IDs festlegen.
- [x] Namens-, Eigentums- und Schutzschema für synthetische Testdatenbanken festlegen.
- [x] Wiederverwendbares Preflight-, Mess-, Cleanup-, Orchestrierungs- und Runtime-Framework implementieren und auf SQL Server 2019, 2022 und 2025 validieren.
- [x] `TST-002` automatisierte Privacy-Prüfung für Text-, Office-, Archiv- und Medienmetadaten implementieren; visuelle/OCR-/Renderprüfung bleibt getrennt verpflichtend.
- [x] Entscheidungspfad T-SQL/Testdatenbank vor zusätzlicher Infrastruktur im Demo-Katalog abbilden.
- [x] Baseline-Review der vorhandenen Präsentationen als Review-Artefakt pflegen.
- [x] Sanitizing-Regeln für Bestandsunterlagen anwenden; nur `Gerhard Pisch` bleibt als reale Namensangabe zulässig.
- [x] Sämtliche veralteten Verweise auf externe Vorlage-Repositories entfernen.
- [x] Das bezeichnete Firmenlogo und die dazugehörigen Firmen- und Markenkennzeichen aus den geprüften Schulungsartefakten entfernen.
- [x] Bildbasierte Branding-Prüfung zusätzlich zur Text- und Metadatensuche definieren.
- [x] Projektweites Quellenregister, Terminologiestandard und Konfliktlog bereitstellen.

## P1 - Erste Umsetzung

- [x] `FWK-001` Preflight-Vertrag und Vorlage implementieren.
- [x] `FWK-002` Namens-, Schutz- und Lifecycle-Vertrag implementieren.
- [x] `FWK-003` deterministischen synthetischen Datengenerator implementieren.
- [x] `FWK-004` sessionbezogenen Messrahmen implementieren.
- [x] `FWK-005` Plan- und Statistikevidenz implementieren.
- [x] `FWK-006` deterministische Multi-Session-Orchestrierung implementieren.
- [x] `FWK-007` Query-Store- und Extended-Events-Helfer implementieren.
- [x] `FWK-008` Sicherheits- und Abbruchvertrag implementieren.
- [x] `FWK-009` vollständige Demo-Dokumentvorlage implementieren.
- [x] `FWK-010` vollständigen Runtime-Harness implementieren.
- [x] `FWK-011` Ergebnisnormalisierung und maschinenunabhängige Erwartungsverträge implementieren.
- [x] `FWK-012` Status-, Fehler- und Skip-Vertrag implementieren.
- [x] Framework-SQL auf SQL Server 2019, 2022 und 2025 parsen, deployen und im Lifecycle testen.
- [x] Zwei grüne T-SQL-Pilotdemos nach vollständigem Demo-Vertrag umsetzen und auf SQL Server 2019, 2022 und 2025 validieren (`QRY-001`, `OPT-002`).
- [x] Eine Multi-Session-Pilotdemo mit kontrolliertem Blocking in einer Testdatenbank umsetzen und validieren (`CON-004`).
- [x] Eine gelbe Ressourcen-Pilotdemo mit definierten Abbruchkriterien umsetzen und validieren (`OPT-013`).
- [x] Gate B mit statischer Prüfung und 24 vollständigen Pilotläufen abnehmen.
- [x] Query Store und Extended Events als zentrale Diagnosepfade in Pilotdemos validieren.
- [x] `W2-001` Bestandsbeispiele vollständig als `REUSE`, `REFACTOR`, `REBUILD`, `DIAGNOSTIC_ONLY` oder `REMOVE` klassifizieren und kanonischen Demo-IDs zuordnen.
- [x] `W2-002` interne und externe Datenabhängigkeiten der priorisierten Migrationskandidaten entfernen; die neun `W2-A`-Altquellen sind aus dem Runtimeumfang ausgeschlossen, vier aktive Ersatzdemos sind synthetisch gebunden und alle verbleibenden Neuaufbauten besitzen einen neutralen Datenvertrag.
- [x] Diagnoseleitfaden als roten Faden von Symptom über Messung und Hypothese bis zum Vorher-Nachher-Vergleich integrieren.
- [x] Rollenmodell für Projektionsfolie, Sprecherhinweis, Teilnehmerunterlage und Demo-Evidenz festlegen.
- [x] Die vier aktiven `REFINE`-Claims in `W2-007` fachlich korrigieren, mit Notes/Quellen synchronisieren und gegen den aktiven Foliensatz validieren.

## P1 - Vertiefungsstrang Query Processing und Diagnose

- [x] `ADV-001` Quellenbasierten Integrationsplan mit fachlichen Blöcken, LAB-Serien, Gates und Mindestanforderungen erstellen.
- [x] `ADV-002` Claim- und Quellenmatrix für Planmechanik, Parameter Sensitivity, Workspace Memory, IQP und Incident-Diagnose erstellen.
- [x] `ADV-003` Curriculum um neun Vertiefungslernziele erweitern und alle 39 Claims in der Traceability-Matrix zuordnen.
- [x] `ADV-004` LAB-VP1 sowie `OPT-015` bis `OPT-017` vollständig entwerfen und den Designvertrag statisch validieren.
- [x] `ADV-005` LAB-VP2, `QRY-013` und die Erweiterung von `QRY-004` vollständig entwerfen und den Designvertrag statisch validieren.
- [x] `ADV-006` LAB-VP3 und LAB-VP4 einschließlich Ressourcen-, Versions-, Compatibility-Level-, Query-Store- und Skip-Matrix vollständig entwerfen und statisch validieren.
- [x] `ADV-007` LAB-VP5 und `DGN-007` als vollständigen Diagnose- und Capstone-Fall mit Hypothesen-, Evidenz-, Vergleichs- und Rückfallvertrag entwerfen und statisch validieren.
- [x] `ADV-008` freigegebene Vertiefungsdemos in kleinen, unabhängigen PRs implementieren und validieren.
  - [x] `OPT-015` Planweite und operatorbezogene Eigenschaften implementieren und auf SQL Server 2019, 2022 und 2025 jeweils zweimal validieren.
  - [x] `OPT-016` Rebind, Rewind, Outer References und Spools implementieren und auf SQL Server 2019, 2022 und 2025 jeweils zweimal validieren.
  - [x] `QRY-013` Client- und Sessionkontext auf SQL Server 2019, 2022 und 2025 jeweils zweimal validieren.
  - [x] `OPT-009` Parameter Sensitive Plan Optimization mit kontrolliertem `SKIP_VERSION` auf 2019 sowie Runtime-Evidenz auf 2022 und 2025 validieren.
  - [x] `OPT-010` Optional Parameter Plan Optimization mit kontrolliertem `SKIP_VERSION` auf 2019/2022 sowie Runtime-Evidenz auf 2025 validieren.
  - [x] `QRY-004_CLASSIC_AND_DYNAMIC` Runtime-Runner für `WARN_EMPIRICAL_VARIANCE` korrigieren oder die Evidenzstrecke stabilisieren und anschließend auf SQL Server 2019, 2022 und 2025 jeweils zweimal validieren.
  - [x] `OPT-017` mit begrenztem gelbem Ressourcenprofil implementieren und mit zweifacher 2019/2022/2025-Runtime-Matrix einschließlich Kernevidenz validieren.
- [x] `ADV-009` Masterdeck, Speaker Notes und Teilnehmerunterlage quellengebunden integrieren und jede neue Folie einem Tiefenprofil zuordnen; die `QRY-004`-Sprechernotiz ist mit Lauf 33222989681 synchronisiert und das 102-Folien-Deck vollständig visuell abgenommen.
- [x] `ADV-010` Vertiefungsstrang fachlich, didaktisch und technisch abnehmen; Quellen-, Runtime-, Deck-, Notes-, Varianten- und Folgearbeitsgrenzen stehen im Endabnahmereview.

## P1 - Interaktive Schulungsszenarien mit SQL_Server_Lab

- [x] `LABSCN-001` Ziel, Verantwortungsgrenze und Lifecycle interaktiver Schulungsszenarien verbindlich festlegen.
- [x] `LABSCN-002` vollständig abschließen: alle 22 produktiven Demos sind gegen den aktiven Katalog mit Lifecycle, Providergrenze, Mindestressourcen, Resetstrategie und Runtimeevidenz inventarisiert; der Validator erzwingt die vollständige Übereinstimmung.
- [x] `LABSCN-003` ersten vollständigen Vertical Slice umsetzen: `CON-004` wird über den Project Adapter `0.1` auf SQL Server 2025 Linux provisioniert, fachlich vorbereitet, als `READY_FOR_USER` übergeben, zurückgesetzt und entfernt; der vollständige Lifecycle ist mit Docker und Podman praktisch validiert.
- [x] `LABSCN-004` Benutzerbedienung und How-to für Auswahl, Start, Übergabe, Reset und Remove standardisieren.
- [ ] `LABSCN-005` weitere Container- und Hyper-V-Szenarien anhand konkreter Beispielanforderungen umsetzen. Die priorisierten sofortigen, bedingten und zukünftigen Kandidaten stehen in [`Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md`](../Documentation/Project_Planning/LABSCN_005_SCENARIO_CANDIDATE_ANALYSIS.md); jeder Kandidat benötigt vor der Umsetzung eine eigene Detailanalyse und Quellenfreigabe.
  - [x] `DGN-005` nach eigenem Detailreview als zweiten interaktiven Slice über Project Adapter `0.1` implementieren und den vollständigen SQL-Server-2025-Lifecycle auf Docker und Podman praktisch validieren.
  - [x] `CON-006` nach eigenem Quellen- und Detailreview als dritten interaktiven Slice über Project Adapter `0.1` implementieren; Deadlock-, Gegenproben-, Reset- und Remove-Vertrag auf SQL Server 2025 mit Docker und Podman praktisch validieren.
  - [x] `DGN-007` als Capstone-Planungsschnitt durch eigenes Detailreview (`TSK-002`, [`LABSCN_005_DGN_007_DETAIL_REVIEW.md`](../Documentation/Project_Planning/LABSCN_005_DGN_007_DETAIL_REVIEW.md)) entscheiden; daraus folgt kein Implementierungsauftrag.
  - [x] `DGN-007` Implementierungsschnitt A (Adapter-Datenaufbau, Query-Store-Fenster und Incident-Erzeugung) als eigenen Pull Request umsetzen; ohne `READY_FOR_USER`-Teilnehmerablauf, ohne Mitigationsmarker und ohne Runtimestatus.
  - [x] `DGN-007` Schnitt-A-Adapter-Lifecycle auf SQL Server 2025 mit Docker (RunId `9ac100f8-…`) und Podman (RunId `e06e9ec9-…`) praktisch abnehmen: Start und Reset endeten als `READY_FOR_USER`, Remove endete als `REMOVED`.
  - [ ] `DGN-007` Implementierungsschnitt B (Evidenz-, Hypothesen-, Mitigations- und Orchestrierungsschnitte) umsetzen.
  - [ ] `DGN-007` Runtime-Matrix auf SQL Server 2019, 2022 und 2025 je zweimal validieren und anschließend die interaktive Docker-/Podman-Abnahme nachweisen.
  - [x] Den getrennten `DGN-007_DATA_MODEL`-Vertrag auf Docker für SQL Server 2019/150, 2022/160 und 2025/170 jeweils zweimal praktisch prüfen, mit unabhängiger Datenbankabwesenheit je Lauf; Runner, begrenzter CI-Workflow und [lokaler Nachweis](../Documentation/Project_Planning/DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md) vorhanden. Keine vollständige Capstone- oder Szenariofreigabe.
  - [x] Den getrennten `DGN-007_QUERY_STORE_WINDOWS`-Vertrag auf Docker für SQL Server 2019/150, 2022/160 und 2025/170 jeweils zweimal praktisch prüfen: zwei disjunkte Katalogintervalle, gleiche vier Parameterklassen, je vier QS-Suchausführungen und unabhängiger Cleanup; [lokaler Nachweis](../Documentation/Project_Planning/DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md). Kein Incident- oder Regressionsnachweis.
  - [x] Ältere DGN-007-Compatibility-Abfrage auf `sys.databases.compatibility_level` umstellen und fehlende Werte im Teilnehmerpfad und in der Adaptervalidierung ablehnen; begrenzter Vorfix ohne Incident- oder Teilnehmerfreigabe.
  - [x] Den getrennten neutralen `DGN-007_PROFILE_COMPARISON`-Vertrag auf Docker für SQL Server 2019/150, 2022/160 und 2025/170 je zweimal praktisch prüfen: gewichtete T0/T1-Mittelwerte, Deltas und tatsächlich ausgeführte Plananzahl ohne Richtungs- oder Mindestplangate; Zero-Baseline gesondert mit numerischer Fixture geprüft. Unabhängiger Cleanup und [lokaler Nachweis](../Documentation/Project_Planning/DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md) vom 2026-10-07. Kein Incident- oder Ursachennachweis.
  - [x] Neutrale `DGN-007_CONTROL_AB`-/`BA`-/`AA`-Captures auf Docker für 2019/150, 2022/160 und 2025/170 je zweimal praktisch prüfen: feste tatsächliche Requestfolge, gleicher Vierermix, aktive Plan-ID-/Hash-Mengen und unabhängiger Cleanup; vollständige neue Reihenfolge mit 36 Lifecycles und [Kontrollnachweis](../Documentation/Project_Planning/DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md) vom 2026-10-07. Die 2019-AA-Variation überlappt einen BA-Zeitkontrast; keine Incident- oder Ursachenfreigabe.
  - [x] Prospektiven DGN-007-Prüfvertrag vor frischen Bestätigungsläufen festlegen (`DEC-068`): reiner Record-/Separations-Evaluator, 34 synthetische Tests und Validator für 14 gebundene SQL-/Manifestquellen lokal PASS. [Vertrag](../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md), Status `STATIC_PROSPECTIVE_CONTRACT`; keine SQL-Runtime- oder Incidentfreigabe.
  - [x] Reinen skalaren DGN-007-Transportdecoder als begrenzten Collector-Vorschnitt implementieren: 19 Transporttests und beide Validatoren lokal PASS; 34 Prospektivtests bleiben grün. [Transportgrenze](../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md), Status `STATIC_COLLECTOR_TRANSPORT`; fehlende Request-Ergebniszeilen bleiben `NOT_CAPTURED`/`None`, keine SQL-Erfassung oder Runtimefreigabe.
  - [x] DGN-007-SQL-Producer mit tatsächlich gezählten Ergebniszeilen je Request und vollständiger skalarer Projektion vor Cleanup implementieren; neue lokale 2019/150-, 2022/160- und 2025/170-Matrix am 2026-10-07 je zweimal AB/BA/AA, insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder und unabhängigem Cleanup PASS. Alle drei eigenen Container unabhängig abwesend bestätigt; [Producernachweis](../Documentation/Project_Planning/DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md). 156 lokale Testmethoden der Phasendiagnostikrevision: 155 PASS, ein Linux-spezifischer SKIP unter Windows. Kein vollständiger Coordinator oder Incidentnachweis.
  - [ ] Verlustfreien Collector-Coordinator für den prospektiven DGN-007-Vertrag implementieren: integrierten Freeze, Quellen, Ressourcen, Budgets und tatsächliche Reihenfolge prüfen, vollständige Request-/Familienrecords und präzise Metriken/Zeitangaben übernehmen sowie Cleanup unabhängig bestätigen.
  - [x] Producer-Integration über [Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65) abschließen: Head `20a867e…` gegen Base `94ed561b…`, Integration `df78cb0…`, alle 14 Workflows und 22 Jobs SUCCESS. Je Version zwölf Lifecycles, sechs Decoder-Captures und unabhängiger Cleanup PASS; Linux 156 Tests ohne SKIP. Squash `da7b0eb…`, vollständige unabhängige Übernahme, Main-Synchronisierung und eigene lokale/remote Branchbereinigung bestätigt. Historische CI-Fehler bleiben ohne behauptete Ursache oder Behebung im [Producernachweis](../Documentation/Project_Planning/DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md) dokumentiert.
  - [ ] Neuen Main-Push-CI-Fehler am Squash `da7b0eb…` klären: [Lauf 37570814577](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37570814577), 2022 BA2 `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`; 47/48 Jobs SUCCESS, alle zehn 2022-Abwesenheitsprüfungen und own-CID-Abwesenheit PASS. Die getrennte private 2022-Gegenprobe bestand zehn Präfix-Lifecycles, vier Captures und unabhängigen Cleanup; G13 wurde nicht reproduziert. Zwei frühere synthetische Vorcheckfehler bleiben getrennt dokumentiert. Nächster eigener Schnitt: begrenzter kanonischer Bericht gespeicherter G13-Grenzabstände mit strenger Failure-/Kanalbindung, unveränderten Prädikaten/Last/Budgets und Ausgabe nach Cleanup. Ursache und Behebung offen; kein Bypass oder Wiederholen bis grün.
  - [ ] Begrenzten kanonischen G13-Grenzabstandsbericht integrieren: lokal implementiert und unabhängig geprüft; 43 Runner- und 37 Producer-/Reporter-Methoden (ein Linux-spezifischer SKIP unter Windows), sieben Validatoren und acht echte temporäre SQL-Branchfixtures auf einer neuen eigenen 2022-Instanz PASS. Unveränderter Freeze und unabhängiger eigener Containerabbau bestätigt. Strikter Ganzdatei-Stripnachweis, unveränderte Guards/Last/Budgets und atomare Ausgabe innerhalb 24 Zeilen nach Cleanup; PR68-Head `27a9b5c…` gegen Base `12b130f…` vollständig geprüft: 13/14 Workflows und 20/22 Jobs SUCCESS, 2019 AA1 und 2022 BA1 FAIL/G13. First−Start −0,4263/−0,951 ms, nur untere Grenze verletzt; 2025 PASS. Alle 32 ersten DB-Abwesenheitsprüfungen und neun SQL-Containerabbauten PASS, Linux 163 Methoden PASS. PR offen, keine Mergefreigabe. Private Originalmaterialisierungsprobe auf neuer eigener 2022-Instanz reproduziert AB1-G13 mit First−Start −0,2609 ms; jeweils eine positive Row/Count vier ohne Zero-/NULL-/Negative-Rows. Zero-Extremum erklärt diesen lokalen Fehler nicht. Elf SQL-Tempfixtures PASS, sechs Präfix-Lifecycles PASS und AB1 FAIL/Stop; sieben erste DB-Abwesenheitsprüfungen, unveränderter 27-Dateien-Freeze und unabhängiger eigener Containerabbau PASS. Kein erfolgreicher AB-Capture/AB2/BA/AA. Der [Mess-/Zuordnungsgegenentwurf](../Documentation/Project_Planning/DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md) liegt als PROPOSED vor; Methodenentscheidung, Baseline-/Intervall- und Herkunftsbelege bleiben offen. Getrenntes [deklaratives Voraussetzungenmodell](../Documentation/Project_Planning/DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md) implementiert, ohne SQL-/v1-Änderung oder Runtimeattestation. Getrennte [Quellen-/Ausführungspfadprüfung](../Documentation/Project_Planning/DGN_007_PREMISE_SOURCE_REVIEW.md) abgeschlossen, konkrete Voraussetzungen weiterhin offen. Konkreter [Beobachtungs-/Herkunftsvertrag](../Documentation/Project_Planning/DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md) als PROPOSED ausgearbeitet; Bounds nicht runtimevalidiert. Der [Suffizienzreview](../Documentation/Project_Planning/DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) und das getrennte [synthetische Gegenmodell](../Documentation/Project_Planning/DGN_007_SATURATION_COUNTERMODEL.md) liegen vor. Das [Methodenentscheidungspaket](../Documentation/Project_Planning/DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet; alle Methodengates bleiben offen. Der [Offline-Verifier](../Documentation/Project_Planning/DGN_007_SOURCE_BUNDLE_VERIFIER.md) ist statisch implementiert; die getrennte [Kantenprüfung](../Documentation/Project_Planning/DGN_007_EXECUTION_EDGE_VERIFIER.md) ebenfalls. Import-/Launcherentwurf PROPOSED, tatsächliche Importumgebung und Runtimebytes offen; der getrennte [synthetische Streaming-/Budgetprototyp](../Documentation/Project_Planning/DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert, ohne Integration in Runtimequellen. Die getrennte [numerische Pipelinegegenprobe](../Documentation/Project_Planning/DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist mit 28 synthetischen Tests implementiert, ohne SQL-Konversionsemulation oder Methodenwahl. Der [Import-/UsedBytes-Entwurf](../Documentation/Project_Planning/DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor, ohne Probeimplementierung oder Importausführung. Nächste Folgearbeit: separater begrenzter Linux-/Python-3.12-Import-Only-Prototyp mit kontrolliertem Rohbyte-Loader, festem Vertrauensprofil, Shadowing-/Austausch-/Alias-/Replay-Gegenfällen und eigenem Cleanup; kein vollständiger UsedBundle-, SQL- oder Methodenclaim. Statische Byteprüfung attestiert keine tatsächliche Ausführung. Guards und bisherige Fehler erhalten. [Nachweis](../Documentation/Project_Planning/DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md). Ursache und Behebung offen; kein Toleranzfix.
  - [x] Quellenbasierten [DGN-007-Mess-/Zuordnungsgegenentwurf](../Documentation/Project_Planning/DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md) als PROPOSED ausarbeiten: getrennte Beweisarten, vollständige Familienbaseline B und Stagebilanz, T0-Capture vor T1, Herkunftsgrenze und synthetische Gegenproben. Keine Methodenentscheidung, Implementierung oder Runtime-Abnahme; v1/G13/DEC-068 unverändert.
  - [x] Getrenntes [deklaratives DGN-007-Voraussetzungenmodell](../Documentation/Project_Planning/DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md) implementieren: 42 synthetische Modellmethoden und unveränderte 34 v1-Fixtures lokal PASS; reine bedingte Konsistenz mit expliziten Annahmen, keine Herkunfts-/Runtime-/Methodenattestation. Die getrennte Quellen-/Ausführungspfadprüfung ist nachfolgend abgeschlossen; tatsächliche Voraussetzungen bleiben offen. G13, v1 und DEC-068 unverändert.
  - [x] [DGN-007-Quellen-/Ausführungspfadprüfung](../Documentation/Project_Planning/DGN_007_PREMISE_SOURCE_REVIEW.md) abschließen: Procedure-Erfassung unter AUTO und Persistenz-/Publikationsgrenze präzisiert; tatsächliche Calls/Ergebnisse/erster Cleanup nutzbar, sechs Modellvoraussetzungen nicht vollständig attestiert. Keine SQL-Runtime, Methodenentscheidung oder v1/G13/DEC-068-Änderung.
  - [x] Begrenzten [DGN-007-Beobachtungs-/Herkunftsvertrag](../Documentation/Project_Planning/DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md) als PROPOSED entwerfen: acht Stages, konkrete Raw-/Gruppen-/Coverage-/Callrecords, getrennte Pulsgrenze, Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Observerkosten innerhalb bestehender Budgets. Keine Runtimevalidierung, Methodenfreigabe oder v1/G13/DEC-068-Änderung.
  - [x] [DGN-007-Suffizienzreview](../Documentation/Project_Planning/DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) abschließen: injektive Sättigung unter geschlossenem tatsächlichem Callumfang kann Callerfassung und keyweise Stageledger können kollektive QS-Buckets tragen; kein Beleg kontinuierlichen RW/ALL. Heutiger Pfad hat Live-Imports/Namenszugriff und keinen vollständigen Freeze-/Zugangs-/Hostbeleg. Keine Methoden-/Runtimefreigabe.
  - [x] Reines begrenztes [DGN-007-Sättigungs-/Acquisition-Gegenmodell](../Documentation/Project_Planning/DGN_007_SATURATION_COUNTERMODEL.md) implementieren: Fremdkompensation, Doppelzählung, Stage-/Generation-/Replaymix, Intervallsplit, Pulsgrenze, Coverage, Metrikdrift und ungültige Zustandsanker gegen synthetische Ausführungstokens geprüft. Getrennte bedingte Claims; keine QS-Einzelidentitäten, Runtimeattestation oder v1/G13-Änderung. Bestehende 42 Voraussetzungstests bleiben erhalten.
  - [x] Konkretes [DGN-007-Methodenentscheidungspaket](../Documentation/Project_Planning/DGN_007_METHOD_DECISION_PACKAGE.md) mit Gate-Matrix vorbereiten: tatsächliche Acquisition-/Countsemantik und Floatstabilität, Freeze-/Actor-/Host-/Zugangsmechanik sowie Streaming-/Poll-/Observerkosten innerhalb bestehender Budgets je Gate belegen oder ausdrücklich offen lassen. Keine impliziten OFF-/CLEAR-/Laständerungen, Methodenfreigabe oder gemeinsame SQL-/Transport-/Coordinator-Umsetzung aus synthetischem PASS.
  - [x] Getrennten [synthetischen Streaming-/Budgetprototyp](../Documentation/Project_Planning/DGN_007_STREAMING_BUDGET_PROTOTYPE.md) mit portablen Budgetgegenproben und festen eigenen Linux-Kindfällen implementieren; Aufnahme vor Decode, gemeinsame Caps, Deadline-/Retry-/Kostenkopplung und sticky eigener Cleanup. Keine Integration in die neun Runtimequellen, reale Laufzeitmachbarkeit oder Methoden-/Launcherattestation.
  - [x] Getrennte [numerische Pipelinegegenprobe](../Documentation/Project_Planning/DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) implementieren: 28 synthetische Tests unter Python 3.12.14 PASS. Endliche Oraclepopulation, deklarierte Fragmentrundung, separat vorgegebener Text und tatsächliche bestehende Consumergewichtung getrennt; exakte Partition, Rundungsabweichung und nicht injektives Ergebnis. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe.
  - [x] Konkreten [Import-/UsedBytes-Probeentwurf](../Documentation/Project_Planning/DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) als `DESIGNED` ausarbeiten: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, bindende Loaderreceipts, endliche Grenzen und eigener Cleanup. Keine Probeimplementierung, Importausführung, vollständige Closure- oder Methodenattestation.
  - [x] Kontrollseitiges [Eingangsprotokoll der Importprobe](../Documentation/Project_Planning/DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md) als getrennten statischen Vorbereitungsteil implementieren: unveränderter 27-Member-Git-/Kantenvorcheck, unveränderliche neun Python-Rohbytes, frische Nonce und streng begrenzte binäre Rahmung mit Kontext-/Manipulationsgegenproben. Keine Kandidatenimporte, Worker, Loaderreceipts oder UsedBytes-/Cleanupattestation. Vollständiger Linux-Importprototyp bleibt offen.
  - [x] Getrennte [synthetische Memory-Loader-Komponente](../Documentation/Project_Planning/DGN_007_MEMORY_LOADER_FIXTURE.md) implementieren: ausschließlich feste harmlose Fixturebytes, tatsächliches Compile/Exec und liveobjektgebundene Beginn-/Abschlussreceipts mit Manipulationsgegenproben. Kein DGN-Import, Finder, Suchpfad-/Cacheumbau oder Worker-/Cleanup-/Methodenclaim; alle DGN-Attestationsflags bleiben false.
  - [x] Getrennten [Interpreter-/Stdlib-Profilvorschnitt](../Documentation/Project_Planning/DGN_007_IMPORT_RUNTIME_PROFILE.md) implementieren: begrenzte tatsächliche Linux-/Python-3.12-Bootstrapmetadaten und Vergleich gegen separat deklarierte unveränderliche Baseline. Kontrollruntime ausdrücklich angenommen, kein Trust aus Pfad/Version/Hash/Label oder eigenen Beobachtungsdaten. Keine DGN-Imports, bereits ausgeführte Bibliotheksbyteattestation, Worker-/Cleanup-/Methodenfreigabe; getrennte Parent-/Workerbindung bleibt offen.
  - [x] [Skalaren Parent-/Worker-Profilbindungsvertrag](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) als `DESIGNED` ausarbeiten: vorab separat gewählte Workerinventur, unveränderter PreparedInput-Kontext, deklarierter Workerordinal und Phase sowie gemeinsame Metadatengrenzen. Reiner Vergleich inzwischen separat implementiert; tatsächlicher Transfer oder Worker, Liveadapter, Kanal-/Verbrauchsbindung und DGN-Importevidenz bleiben offen.
  - [x] Getrennten [reinen deklarativen Profilvergleich](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) implementieren: 38 synthetische Tests unter Python 3.12.14 PASS; exakte DTOs und gemeinsame 16-KiB-Metadatengrenze einschließlich unveränderter Input82-Metadata, Kontrolle aller Formen vor Vergleich und feste öffentliche Reports. Keine tatsächliche Beobachtung, Worker-, Trust-, Replay-/Consumption-, Import-/Cleanup- oder Methodenattestation; kombinierter Codec und tatsächlicher Adapter bleiben offen.
  - [x] Lokale Record-Rückgabe im [Interpreter-/Stdlib-Profilvorschnitt](../Documentation/Project_Planning/DGN_007_IMPORT_RUNTIME_PROFILE.md) implementieren: tatsächlich aufgenommene Abschlussrecords erst nach vollständigen Vor-/Nachprüfungen und optionalen Rohhashreads; jede Ablehnung ohne Observation. 38 Testmethoden unter Python 3.12.14: 36 PASS und zwei begründete Linux-SKIPs unter Windows. Legacyreports und Bounds unverändert; gehaltene Objekte belegen keine spätere aktuelle Cachemitgliedschaft. Keine Worker-, Trust-, UsedBytes-, Codec-, Consumption- oder Methodenattestation.
  - [x] Konkreten [Bootstrap- und Projektionsvorschnitt](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt) als Design festlegen: geplante Scriptquelle, unveränderte zwei Controls, Sysconfigvorinitialisierung, getrennte Feldherkunft und frische Livekohärenz. Keine Implementierung oder Ausführung; vollständige separat gewählte Workerinventur und gemeinsame 16-KiB-Darstellbarkeit bleiben Abnahmegates.
  - [x] Getrennte importneutrale [skalare Profilprojektion](../Documentation/Project_Planning/DGN_007_IMPORT_RUNTIME_PROFILE.md) im bestehenden Profilmodul implementieren: frische Aufnahme, private exakte primitive Tupel und engere Formen, tatsächliche Modul-/Spec-/Loaderfelder, feste livegebundene Frozenpaare sowie zusätzliche separat gewählte FileFinder-Hookbindung mit Factory-/Closuregegenproben. Lokal CPython 3.12.14: 54 PASS von 57 Methoden, genau 3 ausdrücklich begründete Linux-SKIPs. Keine Matcher-/Input82imports, Worker-, Trust-, UsedBytes-, Codec-, Consumption- oder Methodenattestation; konkrete Bootstrapinventur und gemeinsame 16-KiB-Darstellbarkeit bleiben offen.
  - [x] Getrennte lokale [Bootstrap-Charakterisierung und konservative Größenuntergrenze](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze) prüfen: 85 Namen unter CPython 3.12.3, keine operative Sollinventur. Vollständiges verkleinertes Modularray mindestens 16.449 Bytes; gemeinsame Input82-/Worker-/Kontextform mit Header mindestens 21.108 bis 21.144 Bytes. Zwei zusätzliche portable Gegenproben, lokal 40 Matcher-Methoden PASS. Keine Worker-, Trust-, UsedBytes-, Codec-, SQL- oder Methodenattestation.
  - [x] Getrennten vollständig erhaltenden [Darstellungs- und Digestentwurf](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#10-vollständig-erhaltender-darstellungs--und-digestentwurf) als `DESIGNED` festlegen: geschlossene Positionen und Arity, vollständige Felder und beide Neuner-Deskriptorarrays, separate künftige Digestdomains und unveränderte Caps. Keine implementierte Codec-/v1-Migration oder vollständige Darstellbarkeits-, Worker-, Trust- oder UsedBytesattestation.
  - [x] Konkrete [vollständige Bootstrapfixture und reine Größenprüfung](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture) belegen: 85 vorab separat gewählte Records, vollständige Gegenaufnahme und alle fünf Größen je Ordinal einschließlich tatsächlicher Locator, Header und beider Neunerarrays. Gemeinsame Metadata 17.127/17.113/17.091 Bytes überschreitet 16.384; negativer Nachweis für den Tupelkandidaten, kein Fit oder operative Workerbaseline. Neuer Sizer mit 34/34 Gegenproben, Legacy27/40 ohne SKIP; keine Filterung, Capanhebung, Codec-/Digestmigration oder Attestation.
  - [x] Separaten [verlustfreien Stringpoolentwurf](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf) als `DESIGNED` festlegen: lokale eindeutige sortierte Stringpools je Form, exakte schemafeste Referenzen und beide Arrayvorkommen in gemeinsamer Metadata, eigene Design-/Digestdomains, höchstens 256 Poolwerte und begrenzte Rekonstruktion. Keine Codecimplementierung oder positive Größenbehauptung; Tupel-Negativbefund, Legacy, Input82, Inhalte und Caps bleiben erhalten.
  - [x] Eigenen [reinen Pool-Sizer und vollständigen Größenbeleg](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer) implementieren und unabhängig prüfen: 37/37 isolierte Gegenproben ohne SKIP, vollständige neue 3×5-Rechnung mit Originalauswahl und Inputrahmen. Alle Formen passen einschließlich Header, maximal 9.389 Bytes und 204 Poolwerte; unabhängige vollständige Feldrückgewinnung und Nachrechnung. Keine erneute Aufnahme oder Nonce, kein Codec-, Worker-, Trust-, UsedBytes- oder Methodenclaim.
  - [x] Eigenen [experimentellen Formcodec und Design-Digests §14](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests) separat implementieren und unabhängig prüfen: 41/41 isolierte Gegenproben ohne SKIP, ausdrückliche Version-/Rollenauswahl, begrenzte Aufnahme vor Rekonstruktion und kanonischer Repack. Vollständige Originalfixture mit 3×5 Frames, sämtlichen Feldern/beiden D9 und neun eigenen Digestwerten bestätigt; Gesamtausgabe 28.264/28.257/28.246 Bytes und vollständige unabhängige Nachrechnung ohne Replay. Alle fünf Formen und gemeinsames 64-KiB-Gate vor Encoder-/Digestfreigabe, Singledecoder auf seine tatsächliche Rolle begrenzt. Input82/DGNI001, Legacy-API und historische Größenbefunde unverändert; keine operative Workerbaseline, produktive Migration oder Runtime-/Methodenfreigabe.
  - [x] Eigenen [reinen experimentellen kombinierten Eingangsprototyp §15](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen) implementieren und unabhängig prüfen: 34/34 isolierte Gegenproben ohne SKIP; tatsächliche vollständige Originalfixture mit drei Frames zu jeweils 140.226 Bytes, davon 9.389 Metadata einschließlich Header und 130.837 unveränderte Rawbodybytes. Vollständige Empfangsfelder/beide D9/Original-Input82-SHA/neun Rawhashes/Repack und unabhängige Stdlib-Nachrechnung ohne Replay bestätigt. Gleichzeitig 16-KiB-/128-KiB-/1-MiB-/Gesamtframecaps; alle fünf erzeugten Metadataformen samt 64-KiB-Gate vor Encoderfreigabe, eigener tatsächlicher Empfang vor Callerabgleich. Keine produktive Workerroute, operative Baseline, Transfer-, Trust-, Replay-, Consumption- oder Methodenattestation.
  - [x] Konkrete operative [Bootstrap-/Kanalreihenfolge §16](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge) als `DESIGNED` festlegen: Profilaufnahme gemäß §8 bleibt importneutral, zwei Controls und inline Empfang/Reporting; vollständiger PRE-Vergleich vor Rawbodyfreigabe, vollständige Eingangsprüfung vor Importfreigabe und stdin-EOF. Kontrollquellen aus gehaltenen Rawbytes statt ungeprüftem pyc-Pfad; unveränderte gemeinsame Caps und endliche Records. Keine Implementierung, operative Auswahl oder Workerattestation.
  - [x] Reinen [Generator gehaltener Kontrollbootstrapquellen §17](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen) in `Tests/Tools/dgn007_control_bootstrap_source.py` mit `Tests/Static/test_dgn007_control_bootstrap_source.py` als kleinem ausschließlich synthetischen Vorschnitt implementiert und unabhängig vor Ausführung geprüft: dritter isolierter Lauf mit 32/32 PASS ohne SKIP unter CPython 3.12.14; zwei vorherige Fixture-Fehlläufe in §17 erhalten, Produktionsquelle unverändert. Erzeugte private Scriptbytes sind keine operative Workerroute; der geplante §8-Workerlocator bleibt Folgearbeit. Frische operative S15-/P11-Auswahl, inline Receiver/Reporter, Parentadapter, Loader-/Consumption-/Replaybindung und unabhängig bereinigte eigene Worker anschließend getrennt belegen; charakterisierte Kontrollfixture nicht als operative Baseline übernehmen.
  - [x] Getrennte reine [Sysconfig-Vorinitialisierung §18](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) implementiert und unabhängig vor Ausführung geprüft: 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; Legacy-Scriptbytes unverändert. Separat gewählte exakte Erwartungswerte, gehaltene Anker vor Profilexec sowie erneute Bindungs-/Kohärenzprüfung um beide Calls, vollständige Formen vor Vergleich und eigener dominanter Cleanup. Keine tatsächliche Profilaufnahme oder Workerattestation.
  - [x] Private begrenzte native Installationsauswahl nach [§19](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) separat source-/aufrufgebunden geprüft und genau einmal ausgeführt: 20 native Felder, 60 Builtin-Verfügbarkeiten und vier feste Frozenfragen; 2.403 gemeinsame Pipebytes, regulär 3,937 Sekunden. Vollständiger unabhängiger Record-/Prozess-POST ohne Replay bestanden; alle eigenen Windows-/Linux-PIDs abwesend. Private Records unversioniert, keine operative S15/P11-Sollinventur oder Workerattestation.
  - [x] Additive reine [Inline-Metadata-Syntaxquelle §20](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) implementiert und unabhängig vor Ausführung geprüft: korrigierter isolierter Lauf 80/80 PASS ohne SKIP unter CPython 3.12.14; erster Fixture-Label-Fehllauf in §20 erhalten. Vollständige E4-/Pool-/Positionsprüfung samt beiden D9 und kanonischem Repack, ältere Generatorbytes unverändert. Keine Metadata-Semantik, Originaldigest-, Caller-, Body- oder Workerfreigabe.
  - [x] Additive reine [Inline-Metadata-Semantikquelle §21](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) und Originaldigestbindung implementiert und vor jedem Lauf unabhängig geprüft: korrigierter isolierter Lauf 108/108 PASS ohne SKIP unter CPython 3.12.14; erster 106/108-Lauf und zwei enge Testkorrekturen in §21 erhalten. Vollständige deklarative Installation-/Modul-/Alias-/D9-Formen, Original Input82-Präbild und Provider-POSTbindung; ältere Generatorbytes erhalten. Keine operative Inventur, Body-/Caller-/Workerfreigabe.
  - [x] Additiven reinen [Inline-Profilreporter §22](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) implementiert und vor dem einzigen isolierten Lauf unabhängig geprüft: 149/149 PASS ohne SKIP unter CPython 3.12.14, Vor-/Nachpins unverändert. Vollständige tatsächliche Scalarfelder, eigener begrenzter REPORTED-Pool und atomare BEGIN-/Fragment-/END-Records; Provider-/Encoder-/Instanz-POST und reale Testsentinels bestanden. Vier frühere Generatorrouten erhalten; keine operative Inventur, Kanal-/Worker-/Trustfreigabe.
  - [ ] Reine Receiver-/Kanalteile nach §16 als nächsten ausschließlich synthetischen Offline-Schnitt ergänzen; erst danach endgültige Quelle mit separat vorgewählter operativer S15-/P11-Inventur und gemeinsamem Fünf-Formen-/64-KiB-Gate abnehmen.
  - [ ] Frische separat vorgewählte operative Installation und vollständige S15-/P11-Inventur für die konkrete gehaltene Bootstraproute nach §17/§18 belegen; alle fünf Darstellungen einschließlich des gemeinsamen 64-KiB-Gates und die tatsächlichen Script-/Profilbytes vor jeder späteren Workerfreigabe prüfen. Keine Übernahme der charakterisierten historischen Kontrollfixture als operative Baseline.
  - [ ] Separaten begrenzten Linux-/Python-3.12-Import-Only-Prototyp nach dem Entwurf vervollständigen: vorbereitetes Eingangsprotokoll verwenden, tatsächliche Loaderverwendung und Importabschluss getrennt bestätigen, Shadowing-/Austausch-/Alias-/Replay-/Cleanupgegenproben. Bestehende neun Runtimequellen unverändert; Claim ausschließlich für tatsächlich abgeschlossene Top-Level-Imports, keine SQL-/Acquisition-/Methodenattestation.
  - [x] [Prozess-/Manifestkanten](../Documentation/Project_Planning/DGN_007_EXECUTION_EDGE_VERIFIER.md) getrennt offline prüfen: festes Python-3.12-AST-Profil, sechs SQL-only-Manifeste, 14 Quellenhashes und SQLCMD-Gegenproben. Importumgebungs-/Launcherentwurf PROPOSED; tatsächliche Importumgebung und Runtimebytes bleiben offen, kein Launcherstart oder Methodenentscheid.
  - [x] [Offline-Quellenbundle-Verifier](../Documentation/Project_Planning/DGN_007_SOURCE_BUNDLE_VERIFIER.md) im bestehenden DGN-007-Scope statisch implementieren: exakter Commit, Gitblobs und feste Mitglieder-/Importclosure; temporäre Manipulationsfixtures für fehlende/zusätzliche/doppelte Mitglieder, Byte-/Pfad-/Importänderung, EOL, Exportattribute und Overflow. Keine Bundleausführung, SQL-/Docker-Runtime, tatsächliche Quellen-/Actor-/Zugangs-/Hostattestation oder Methodenfreigabe.
  - [x] Internen verlustfreien Capture-Vorschnitt unter DEC-072/v2 über PR255 integrieren: [Quellenreview und Nachweis](../Documentation/Project_Planning/DGN_007_INTERNAL_CAPTURE_RECEIPT_REVIEW.md), 14 grüne PR-Gates einschließlich SQL2019/2022/2025, vollständiger Treevergleich und beide lokalen Capture-Branches samt eigenem Remote-Branch bereinigt. Body und tatsächliche Phasen erst nach erfolgreichem Lifecycle und erster unabhängiger Datenbankabwesenheit; Counts/CLI/Fehlerprioritäten erhalten, kein Recovery-PASS oder RunRecord-/Runtimeattestations-/Incidentclaim.
  - [x] Separaten [SESSION_END-Vertragsentwurf §34](../Documentation/Project_Planning/DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild) zu Loaderrecords §33 ausarbeiten und unabhängig ohne Befunde reviewen: Recordform, exakte Counts und nicht selbstreferentielles Kanalhashpräbild; 57 Literalrechnungen und synthetische Hashreferenz unabhängig bestätigt. Acht Dokumentationsgates zum Erststand grün; [PR256](https://github.com/gecompat/SQL_PerformanceSchulung/pull/256) bindet abschließende Head-/Base-Gates und Main-Integration. Kein Parser, Kanal, Loader, Worker oder SQLlauf; keine Wiederaufnahme ausgeschöpfter Versuche.
  - [x] [Reine SESSION_END-Komponenten](../Documentation/Project_Planning/DGN_007_SESSION_END_COMPONENTS.md) getrennt implementieren und isoliert prüfen: gemeinsamer unabhängiger Auswahl-PRE ohne Befunde, je zwei Quellenkandidaten mit erstem Checkpoint. Footer-Codec über PR257 mit 13 isolierten lokalen Testmethoden unter Python 3.12/3.14, unabhängigem Review ohne Befunde, acht verschiedenen grünen finalen PR-Gates, sechs erfolgreichen Main-Workflows, Treevergleich und Branchbereinigung integriert. Kanalhash-Erststand mit 22 Testmethoden einschließlich aller Footergegenproben auf beiden Pythonversionen, eigenem unabhängigem Review ohne Befunde und acht grünen CI-Gates bestanden; PR258 bindet finale Head-/Base-Gates, Main-Integration und Bereinigung vor Integrationsabschluss. Kein vollständiger Matcher, Worker, Kanal-/EOF-/Runtime- oder Trustnachweis.
  - [x] [Vollständigen deklarativen SESSION_END-Matcher](../Documentation/Project_Planning/DGN_007_SESSION_END_MATCHER_REVIEW.md) als getrennte fünfzehnte Kontrollquellenroute implementieren und isoliert prüfen: Profil, INPUT_COMPLETE, vollständiger Loaderstack, Footer und Rohbytehash; ganze Actual-/Caller-R4/K8/D9 und äußere dominante Guardanker. Auswahl-/Quellenreview, P2-Korrektur und gezielter C3-Harnessreview mit Lauf-GO abgeschlossen; keine offenen Befunde. C2-Fixture-FAIL erhalten, C3 30 Methoden unter Python 3.12/Linux und 3.14/Windows ohne SKIP bestanden, 460 bisherige Kontrollquellenmethoden unter Windows auf unveränderter Quelle grün. PR259 bindet finale Head-/Base-Gates, Main-Integration und Bereinigung vor Integrationsabschluss. Kein operativer Kanal-, EOF-, Exit-, Cleanup-, Runtime- oder Trustclaim.
  - [ ] Kontrollierten DGN-007-Incidentnachweis unter dem festgelegten prospektiven Prüfvertrag mit frischen Bestätigungsläufen auf gleicher Parameterlast implementieren; ältere Beobachtungsbedingung und LOCAL-Lastmix gegen den Designvertrag korrigieren.
- [ ] `LABSCN-006` gemischte Topologien erst für ein fachlich begründetes Beispiel mit nachgewiesenem Bedarf umsetzen.
- [x] Für jedes produktive Szenario Mindestanforderungen an Hosthardware, Providergrenzen, Versionen und Resetstrategie dokumentieren und statisch gegen den Demo-Katalog absichern.
- [ ] Zusätzliche Funktionalität in `SQL_Server_Lab` nur nach konkretem Szenariobefund benennen und erst nach ausdrücklicher Freigabe dort umsetzen.

## P1 - Nachgeordnete SQL_Server_Lab-Qualitätssicherung

- [x] `LABINT-001` automatisierten Testkatalog, JSON-Schema und statische Vollständigkeitsprüfung erstellen.
- [x] `LABINT-002` Smoke-/Core-Test für Aufbau, Vorbereitung, Reset und Abbau des ersten interaktiven Vertical Slice implementieren.
  - [x] Technischen QRY-001-Vorläufer auf Docker und Podman mit SQL Server 2025 über öffentliche `SQL_Server_Lab`-Commands implementieren und je Provider mit zwei vollständigen Demoläufen, unabhängiger Datenbank-Cleanup-Prüfung und Infrastrukturabbau lokal validieren.
  - [x] Den Test auf den vollständigen `CON-004`-Lifecycle `READY_FOR_USER` -> Reset -> `READY_FOR_USER` -> Remove erweitern und auf SQL Server 2025 mit Docker und Podman praktisch validieren.
- [x] `LABINT-003` Docker-/Podman-Parität für die freigegebenen Szenarioslices praktisch prüfen.
  - [x] Provider-Parität für `QRY-001` auf SQL Server 2025 mit jeweils zwei vollständigen Läufen lokal nachweisen.
  - [x] Provider-Parität für den versionierten `CON-004`-Adapter-Lifecycle auf SQL Server 2025 mit vollständigem Start-, Reset- und Remove-Lauf nachweisen.
  - [x] `DGN-005` als weiteres geeignetes Szenario auf Docker und Podman praktisch prüfen; die automatisierte Demo besitzt zusätzlich die freigegebene 2019/2022/2025-Matrix aus Lauf 33222989682.
  - [x] `CON-006` als neuen gelben Mehrsession-Slice in seiner vollständigen freigegebenen Provider-/Versionsmatrix auf Docker und Podman prüfen.
- [x] `LABINT-004` für den freigegebenen `CON-006`-Slice aktivieren: SQL Server 2025, Docker/Podman, fachliche Deadlock- und Gegenprobe sowie vollständiger Reset/Remove sind praktisch validiert.

## P1 - Masterdeck und Präsentationsvarianten

- [x] `DEC-043` Kanonisches Masterdeck und reproduzierbar abgeleitete Tiefenprofile verbindlich entscheiden.
- [x] Architekturplan für `BASIS`, `STANDARD` und `VERTIEFUNG` einschließlich Custom Shows, eigenständiger `.pptx`-Ableitung und Qualitätsgates erstellen.
- [x] `PRS-011` SlideKey- und JSON-Variantenmanifest-Vertrag definieren.
- [x] `PRS-012` Masterdeck mit stabilen SlideKeys und den Custom Shows `BASIS`, `STANDARD` und `VERTIEFUNG` ausstatten.
- [x] `PRS-013` kontrollierten interaktiven Build eigenständiger `.pptx`-Varianten aus einer Kopie des Masterdecks implementieren.
- [x] `TST-011` statischen Validator für Manifest, SlideKeys, Custom Shows, Abhängigkeiten, Links, Quellen und Demo-IDs implementieren.
- [x] `TST-012` Render-, Notes-, Metadaten-, Privacy- und Branding-Abnahme für jede freigegebene Variante implementieren.
- [x] Trainer-Runbook um Auswahl und Start der Custom Shows sowie Erzeugung eigenständiger Varianten ergänzen.
- [x] Orientierung und Ergebnisdarstellung der vorhandenen Demo-Einstiege korrigieren; historische Runtime-Nachweise der 22 katalogisierten Demos mit Datum, Run-Commit, Versions-Skips und empirischen Warnungen im bestehenden Katalog einordnen.
- [x] `PRS-010`, `CUR-007`, `CUR-008`, `DOC-002` und `DOC-003`: [repräsentative Generalprobe](../Documentation/Project_Planning/PRS_010_REHEARSAL_PLAN.md) mit Ablauf, Aufgaben, Musterantworten, Beobachtungsbogen und Abbruch-/Cleanup-Pfad vorbereiten; neun ausgewählte Folien und Notes am aktuellen Deck-Hash prüfen. Dies erledigt ausschließlich die Vorbereitung.
- [ ] Die vorbereitete Teilnehmer-Generalprobe tatsächlich durchführen, Istzeiten und selbstständigen Transfer datensparsam auswerten sowie verbleibende Projektions- und Recoveryprüfungen belegen.
- [ ] `PRS-010` anschließend durch eine dokumentierte Generalprobe des vollständigen gewählten Kursprofils abschließen; der repräsentative Pilot allein ist keine vollständige Schulungs- oder Releaseabnahme.

## P2 - External Tables und Graph Tables

Beide Themen sind offene Vormerkungen mit Status `PROPOSED`. Die fachliche
Zuordnung beginnt in Welle 5 und berührt Optimizer-/Planmechanik in Welle 4
sowie Indizes in Welle 6. Priorisierung, Lernziel-/Folienzuordnung und ein
konkreter Demo-Schnitt werden nach Quellen- und Abdeckungsprüfung festgelegt;
die aktuelle DGN-007-Folgearbeit behält ihre Priorität.

- [ ] **External Tables:** Einsatzgrenzen, konkrete externe Datenquelle und Zugriffsweg einschließlich gegebenenfalls PolyBase für die SQL-Server-2019/2022/2025-Matrix recherchieren. Statistiken, Cardinality Estimates, Predicate-/Projection-Pushdown, lokale gegenüber externer Verarbeitung sowie Datenübertragungs- und I/O-Kosten anhand vergleichbarer synthetischer Abfragen untersuchen. Version, Edition, Betriebssystem, Compatibility Level, Rechte und Connectorvoraussetzungen vor dem Demoentwurf prüfen; zusätzliche Infrastruktur auf den gewählten Zugriffsweg begrenzen und isolierten Aufbau, bestätigte Ausführung sowie unabhängigen Cleanup vorsehen. Einstieg: [PolyBase-Pushdown](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-pushdown-computation?view=sql-server-ver17).
- [ ] **Graph Tables:** Node-/Edge-Tabellen, `MATCH`, Graph-Indizes und passende Anwendungsfälle aufbereiten. Eine synthetische Graph-Abfrage mit einer semantisch gleichwertigen relationalen Modellierung vergleichen und Execution Plans, Cardinality Estimates, Logical Reads, CPU und Duration unter gleichen Bedingungen messen. Featuregrenzen nach Version, Edition und Compatibility Level für SQL Server 2019/2022/2025 prüfen; reproduzierbares T-SQL-Setup und Cleanup in einer isolierten Testdatenbank entwerfen. Einstieg: [SQL-Graph-Architektur](https://learn.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-architecture?view=sql-server-ver17).

Die Quellenlinks sind Rechercheeinstiege, abgerufen am 2026-10-07. Eine
Performanceüberlegenheit oder vollständige Feature-/Versionsfreigabe ist
damit nicht festgestellt. Finale Task-/Demo-Kennungen werden erst bei der
konkreten Zuordnung über die bestehende Registrierungsautorität vergeben.

## P2 - Reproduktion und Testmatrix

- [x] Weitere SQL-Server-Beispielkategorien über Query Tuning hinaus systematisch recherchieren, gegen vorhandene Demo- und Folienabdeckung deduplizieren und im [Recherchekatalog](../Documentation/Project_Planning/SQL_SERVER_EXAMPLE_CATEGORY_RESEARCH_CATALOG.md) einem vorhandenen Owner, einer späteren Eigentümerentscheidung, Infrastruktur oder einem Ausschluss zuordnen. Die Recherche legt noch keine neuen IDs oder Implementierungswellen fest.
- [x] `W-COV-001` neun verbleibende Demos in der Reihenfolge `OPT-003`, `OPT-005`, `CON-006`, `CON-009`, `IDX-006`, `IDX-010`, `STL-008`, `STL-009`, `RES-007` als source-, safety- und curriculumgebundene Pakete implementieren.
- [x] `W-COV-001` Runtimefreigabe für alle neun Demos nach je zwei 2019/2022/2025-Läufen abschließen; Cleanup unabhängig prüfen.

- [x] SQL-Server-2019/2022/2025-Testmatrix definieren und erfolgreich ausführen.
- [x] How-to für vorhandene SQL-Server-Instanz plus isolierte synthetische Testdatenbank erstellen. Der Laufnachweis gegen eine vorhandene Instanz steht noch aus.
- [x] Kompakten Docker-/Podman-Bereitstellungspfad für Personen ohne verfügbaren SQL Server dokumentieren; beide Provider-Preflights melden `RESOURCE_OK`, und der vollständige SQL-Server-2025-Lifecycle ist praktisch validiert.
- [ ] Docker-/Podman-Ressourcen- oder Netzwerkfunktionen nur für konkret abhängige Demos prüfen.
- [ ] Hyper-V nur für nachweislich Windows-, Storage- oder OS-nahe Demos planen.
- [x] Wiederholbare Concurrency-Prozesssteuerung ohne proprietäre Abhängigkeiten implementieren und mit realen parallelen SQL-Sessions validieren.
- [x] Hardwareabhängige Erwartungswerte als Invarianten, Richtungen, Verhältnisse oder begründete Bandbreiten statt Fixwerte definieren.
- [x] Vorhandene Präsentationsmodule fachlich modernisieren und mit Demo-Katalog, Quellenregister, Lernzielen und Tiefenprofilen synchronisieren; Masterdeck und 41/66/102-Profile sind fachlich, technisch und visuell abgenommen.
- [x] Branding-bereinigte Repository-Fassung der Schulungsunterlagen bereitstellen.

## Erledigungsregel

Ein Punkt gilt nur dann als erledigt, wenn Artefakt, Quellenprüfung und zutreffende Validierung im Repository nachvollziehbar vorhanden sind. `IMPLEMENTED` ersetzt keine Runtime-Validierung ausführbarer SQL-Artefakte. Ein interaktives Szenario gilt erst als vollständig, wenn Aufbau, Vorbereitung, Benutzerübergabe, Reset und Abbau praktisch nutzbar sind.
