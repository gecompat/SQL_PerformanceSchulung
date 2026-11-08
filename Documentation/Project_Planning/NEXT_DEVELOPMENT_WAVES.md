# Nächste Entwicklungswellen

## Aktuelle autonome Fortsetzungsplanung vom 7. November 2026

Diese Planung konkretisiert den aktiven Auftrag in
[`CURRENT_EXECUTION_STATUS.md`](CURRENT_EXECUTION_STATUS.md). Sie ersetzt die
überholten Statusangaben der nachfolgenden historischen Planung, insbesondere
die dort genannten Pausen bis zum 20. Oktober. Sie setzt weder neue fachliche
Freigaben noch Laufrechte oder Budgets. Reihenfolge, Umfang und Status werden
vor jedem neuen Arbeitspaket gegen den aktuellen kanonischen Ausführungsstand,
die betroffenen Verträge und den verbleibenden Gesamtbudgetstand abgeglichen.

### Arbeitsfolge

| Schritt | Arbeit und Abschlusskriterium | Grenze / Folgeentscheidung |
|---|---|---|
| 1. DGN-004 statische Annahmeprüfung | Der reine Neun-Aufruf-/Statusprüfer und seine synthetischen Gegenfälle sind implementiert und unabhängig geprüft. Restgate: die unabhängige Methoden-/Quellenfreigabe vor SQL bleibt offen. | Keine SQL-/Lab-Ausführung. Der Review schließt nur die statische Gegenprobenlücke. Umsetzung und Laufqualifikation nur nach der dafür nötigen Freigabe; Zielbuilds bleiben 2022/16.0.4265.3 und 2025/17.0.4075.5, neun Aufrufe je Build, zwei eigene sequenzielle Container, 900 Sekunden gemeinsames Laufbudget plus je 60 Sekunden Cleanup. |
| 2. QRY-002 Lehrnotiz | PR #383 integrierte die quellengebundene Erklärung beider Konvertierungsrichtungen und trennt Typauflösung von konkreter Zugriffswirkung. | Menschliche Generalprobe bleibt ausgeschlossen. Kein Scan-/Seek- oder Leistungsclaim ohne konkrete Plan- und Messbelege. |
| 3. Lesepfade und Kerninhalte | QRY-003/RES-004-Pfade sowie QRY-007 und IDX-003/004/001/002 sind quellengebunden integriert. PR #394 integrierte STL-001, PR #395 STL-002, PR #396 QRY-005, PR #397/#398 OPT-004, PR #399 STL-003, PR #400 QRY-011, PR #401 IDX-005, PR #402 OPT-012, PR #403 STL-010, PR #405 QRY-003, PR #406 QRY-007, PR #408 IDX-003, PR #410 IDX-004, PR #412 IDX-001, PR #414 IDX-002, PR #416 STL-001 und PR #418 STL-002. STL-002 bindet vollständige Nutzdaten- und Padding-Formeln sowie Mengentupeloracles für alle drei Speicherprofile. | Keine SQL-/Runtimefreigabe. STL-001/002 enthalten synthetische Entwurfsoracles; reale Record-/Seiten- und Allocation-Unit-Evidenz sowie Lese-I/O bleiben offen. |
| 4. Diagnose- und vorhandene KI-Qualifikation | Jeweils nur den im aktiven Status ausgewählten, unabhängig prüfbaren Schnitt vorbereiten; Verträge, synthetische Prüfungen und erforderliche Reviews vor jeder Runtimephase abschließen. | Kein SQL-/Provider-/Netzwerk-/Lab-Effekt aus statischer Evidenz ableiten. Lauf-, Provider- und Datenfreigaben gelten pro konkretem Schnitt. |
| 5. CON-006- und IDX-007-Varianten | Der synthetisch geprüfte CON-006-Offline-Graph- und Capturevertrag sowie der IDX-007-Offlinevertrag für caller-supplied `PAGELATCH_EX`-Waits sind im Framework-Contracts-Workflow enthalten. PR #420 ergänzt die IDX-007-Prüfung: fehlender Rechtsaußenbeleg ist `NOT_PROVEN`, expliziter Gegenbeleg `FAIL`. PR #422 prüft den CON-006-Graph-/Capturevertrag lokal. Die aktuellen Herstellertexte spezifizieren das genaue `requestType="convert"`-Schema nicht; die Herkunftsbindung der zusammengefassten Capturefelder bleibt beim Producer. Offen bleiben unabhängige Methoden-/Quellenfreigabe und danach die empirische Darstellung bzw. echte IDX-007-Seitenkettenauflösung, bevor Laufvarianten umgesetzt werden. Anschließend den fairen IDX-007-Vergleich mit tatsächlichem Wait-/Page-Nachweis verfolgen. | Graph, Zeitfenster, Marker, Eventquelle, Actorresultate, Waits und Seitenfelder sind caller-geliefert und unauthentifiziert. Der statische `PASS` ist kein Laufzeit- oder Engpassnachweis. Range bleibt zurückgestellt. Kein SQL-/Lab-Lauf ohne konkreten Demo-Vertrag, Methodenfreigabe und Safety-/Cleanup-Gates. |
| 6. Nachgelagerte Erweiterungen | Der statische RES-001-Offlineschnitt und RES-003-Offlinevertrag samt quellengebundener Lehrnotiz sind integriert. Die Detailprüfung zu SQL-Server-2025-`OPTIMIZED_SP_EXECUTESQL` ist abgeschlossen; Aktivierung, Demo und Performanceclaim bleiben `DEFER`, weil die bestehende `QRY-004`-Abnahme keine zeitgleiche Kompilierung prüft. Die [Graph-Table-Quellen- und Abdeckungsprüfung](GRAPH_TABLES_SOURCE_COVERAGE_REVIEW.md) empfiehlt Graph Tables als ersten Offline-Entwurf; die [Versions- und Indexprüfung](GRAPH_TABLES_VERSION_INDEX_REVIEW.md) und die [2022/2025-Releaseübersichtenprüfung](GRAPH_TABLES_2022_2025_SOURCE_REVIEW.md) binden die begrenzte Versionssicht. `LO-M03-06`/`CLM-047` ist der bestehende Curriculum-Anker; [Demoentwurf und Vertrag](GRAPH_TABLES_DEMO_CONCEPT.md), [T-SQL-Syntaxreview](GRAPH_TABLES_TSQL_SYNTAX_REVIEW.md), [Messworkload](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md) und [Quellen-/Methodenreview](GRAPH_TABLES_METHOD_REVIEW.md) legen Korrektheitsoracle, 10.000-Pfade-Profil, `MATCH`, Kandidatenindizes und getrennte Mess-/Planevidenz dar. `QRY-023` ist unter `TSK-017` registriert und bleibt `PROPOSED`; Graph-Tabellen verlangen eine eigene markierte Testdatenbank. Das Framework-/Curriculumreview bindet die Zielmatrix 2019/150, 2022/160, 2025/170 und Plan-/Baseline-/Vergleichsmessung. Ein lokaler Harness-Codeentwurf ist vorhanden, aber nicht abgenommen oder katalogisiert. Unabhängige Methodenfreigabe, formale Vertrags-/T-SQL-Abnahme, konkrete Index-/Build-/CU-Definitionen und Runtimefreigaben bleiben offen. | RES-003 bleibt ein roter, nicht ausführbarer Druckversuch; `OPTIMIZED_SP_EXECUTESQL` erhält keine Runtimefreigabe. Graph Tables bleiben `PROPOSED`; `QRY-023` besitzt nur einen lokalen, nicht katalogisierten Codeentwurf und keine Runtimequalifikation und behauptet keine allgemeine Leistungsrangfolge. External Tables bleiben zurückgestellt bis zur Prüfung des konkreten Connectors, der Quelle und der Infrastruktur. Statische und quellengebundene Erklärung ersetzt weder authentische Runtime-Evidenz noch Kausalitätsnachweis. Weitere Ressourcen und Infrastruktur nur mit eigenem Methoden-, Versions-, Sicherheits- und Cleanupvertrag. |

Der aktive Offline-Teilschnitt für die unter Schritt 6 bereits beschriebenen
Graph-Tabellen-Arbeiten ist die lokale Coverage- und Widerspruchsprüfung des
QRY-023-Harnessentwurfs, des statischen Vertragsprüfers und der vorhandenen
Syntax-/Methodendokumente. Er erteilt weder formale T-SQL-Abnahme noch
Runtimefreigabe.

### DGN-007 getrenntes Qualifikationsband

Der am 4. November integrierte Import-only-Worker ist begrenzte lokale
Komponentenevidenz. Ein nächster DGN-007-Schritt darf nur aus dem aktiven
kanonischen Status gewählt und auf einen einzelnen, statisch prüfbaren
Quell-/Vertragsschnitt begrenzt werden. Loader-/Parentregistrierung,
SESSION_END, tatsächlicher Kanal, operative Inventur, UsedBytes, Trust,
Consumption, Replay, unabhängiger Worker-Cleanup, SQL und Methodenfreigabe
bleiben getrennte Gates. Jeder PASS einer Komponente ist ausschließlich für
deren festgelegten Scope gültig; keine Komponente aktiviert automatisch den
nächsten Lauf.

### Gemeinsame Autonomie- und Stopregeln

- Ein Owner, höchstens zwei zusammenhängende Arbeitspakete je Fortsetzung und
  Checkpoint spätestens am dritten Quellenkandidaten oder beim ersten Blocker.
- Die bisherigen kumulativen Obergrenzen von 15 Arbeitspaketen, 23 Pull
  Requests und 57 Quellenkandidaten bleiben als Verbrauchsbasis erhalten.
  Der Nutzer autorisierte am 2026-11-06 zwei begrenzte Fortsetzungserweiterungen
  für die autonome Entwicklung, jeweils um ein Arbeitspaket, einen Pull Request
  und zwei Quellen-/Testkandidaten. Die kumulative Obergrenze beträgt nun
  17/25/61; kein Reset. Diese aktuelle Erweiterung gilt für den RES-001-Schnitt
  und wird am PR-/Integrationscheckpoint gegen den Stand geprüft.
  Mit der Fortsetzungsanweisung vom 2026-11-07 gilt für den nächsten
  eigenständigen RES-003-Offlineschnitt eine begrenzte Erweiterung um ein
  Arbeitspaket, einen Pull Request und zwei Quellen-/Testkandidaten. Die
  kumulative Obergrenze beträgt 18/26/63; kein Reset. Sie gilt ausschließlich
  für diesen Offlinevertrag und wird am Integrationscheckpoint abgeglichen.
  Die Fortsetzungsanweisung vom 2026-11-07 autorisiert am nächsten Checkpoint
  einen zusätzlichen, eigenständigen Dokumentationsschnitt mit weiteren
  1/1/2 Einheiten; die kumulative Obergrenze beträgt nun 19/27/65. Diese
  Erweiterung gilt für die quellengebundene RES-003-Lehrergänzung.
  Für die anschließende Detailprüfung des SQL-Server-2025-`OPTIMIZED_SP_EXECUTESQL`
  gilt nach der Fortsetzungsanweisung vom 2026-11-07 eine weitere klar begrenzte
  Erweiterung um ein Arbeitspaket, einen PR und zwei Quellenkandidaten; kumulativ
  höchstens 20/28/67, kein Reset. Sie deckt nur Quellenprüfung und dokumentarische
  Entscheidung ab, keine Featureaktivierung oder Runtime.
  Die nächste autonome Fortsetzung erweitert den begrenzten Rahmen um genau ein
  Arbeitspaket, einen Pull Request und zwei Quellenkandidaten; kumulativ höchstens
  21/29/69, ohne Reset. Diese Erweiterung gilt für die Offline-Quellen- und
  Abdeckungsprüfung zu Graph Tables. Sie autorisiert weder SQL-/Lab-Ausführung
  noch Demo-Implementierung oder Performanceaussage.
  Für die anschließende getrennte Graph-Table-Versions- und Indexprüfung galt
  eine begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und
  2 Quellenkandidaten; kumulativ höchstens 22/30/71, kein Reset. Sie erfasste
  zwei weitere Microsoft-Primärquellen und eine Offline-Dokumentation, ohne
  SQL-/Runtimefreigabe. Der Schnitt ist über PR #365 vollständig integriert.
  Die Curriculum-Zuordnung erweiterte den Rahmen um ein Arbeitspaket,
  einen Pull Request und bis zu zwei Quellenkandidaten auf kumulativ 23/31/73.
  Sie verwendete bestehende Projektquellen und begründete keine neue Lernziel-ID.
  Der Schnitt ist über PR #366 vollständig integriert.
  Für die Quellenprüfung der 2022/2025-Releaseübersichten gilt die nächste
  begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und 2 Quellenkandidaten;
  kumulativ höchstens 24/32/75. Sie bewertet nur die beiden Versionsübersichten
  und erteilte keine Kompatibilitäts- oder Laufzeitfreigabe. Der Schnitt ist
  über PR #367 integriert.
  Der statische Graph-Demoentwurf erweitert den Rahmen um ein Arbeitspaket,
  einen Pull Request und bis zu zwei Quellenkandidaten auf kumulativ 25/33/77.
  Er erstellt keine Demo-ID und erteilt keine SQL-/Runtimefreigabe.
  Der Syntaxreview für `MATCH` und Edge-INSERT erweitert den endlichen Rahmen
  um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten; kumulativ höchstens 26/34/79.
  Er bleibt auf Primärquellen und statische Dokumentation begrenzt.
  Die Fortsetzung nach der Syntaxprüfung erweitert den endlichen Rahmen um 1 Arbeitspaket, 1 PR und 2 Quellen-/Vertragskandidaten auf höchstens 27/35/81. Sie gilt für die Registrierung von `QRY-023` und den vollständigen statischen Vertrag; keine SQL-/Lab-Ausführung.
  Das Framework-/Curriculumreview setzt die autonome Fortsetzung um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 28/36/83 fort. Es bindet die Projektprofile 2019/150, 2022/160, 2025/170 als Designziele und macht Plan-/Baseline-/Vergleichsmessung verpflichtend; keine Laufzeitfreigabe.
  Der Entwurf des deterministischen QRY-023-Messworkloads und die formale CLM-047-Traceabilityzuordnung erweitern die Obergrenze um 1 Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 29/37/85. Die Designprofile und Messmethodik sind weiterhin keine Graph-Runtimefreigabe.
  Das Quellen-/Methodenreview zu MATCH, Kandidatenindizes und getrennter Planevidenz erweitert die Obergrenze um 1 Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 30/38/87. Die unabhängige Methodenfreigabe bleibt ausdrücklich offen.
  Der initiale QRY-023-Harness-Codeentwurf erweitert die Obergrenze um 1 Arbeitspaket und 1 PR auf höchstens 31/39/89. Er bleibt nicht katalogisiert und ungefahren; statische Abnahme, unabhängige Methodenfreigabe und konkrete Runtimefreigabe sind getrennte weitere Gates.
  PR #374 integriert den QRY-023-Codeentwurf nach erfolgreichen Projektworkflows. Der statische allgemeine Cleanup-Eigentumstest lief in disposable SQL-Server-Containern für 2019, 2022 und 2025; QRY-023 selbst wurde nicht ausgeführt. Die nächste Welle ergänzt einen gezielten Offlinevertrag mit Regressionstests und eigenem nur statischen CI-Workflow. Die kumulative Obergrenze steigt um 1 Arbeitspaket, 1 PR und 2 Evidenzkandidaten auf 32/40/91. Diese Strukturprüfung schließt weder T-SQL-Kompilierbarkeit noch unabhängige Methodenfreigabe.
  PR #375 integriert den Offlinevalidator und seine Regressionstests; sämtliche PR-Gates waren grün. Die Editions-/Servicingprüfung für QRY-023 ergibt graphfähige Projekteditionen und bindet die zum 7.11.2026 neuesten dokumentierten Servicingbuilds als zeitgebundene Designpins ein. Preflight und Setup prüfen sie vor Mutation. Diese Fortsetzung erweitert den Rahmen um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 33/41/93. Image-Digests, unabhängige Methodenfreigabe und Ausführung bleiben offen.
  PR #376 integriert das Editions-/Buildreview und die vor Setup erzwungenen ProductVersion-Pins. Der nächste Offline-Schnitt ergänzt ScriptDom `170.191.0` mit Lockfile und grammatikgebundenem Parse der ausführbaren QRY-023-Dateien für SQL Server 2019/2022/2025. Er schließt keine Engine-Kompilierung und keinen Runtimegate. Obergrenze: 34 Arbeitspakete, 42 PRs und 95 Quellenkandidaten.
  Der read-only MCR-Abgleich bindet die tatsächlichen Buildlabels und Manifestdigests der vorgesehenen Linux/AMD64-Images. Er ersetzt zwei Produktservicingpins in Preflight/Setup durch die dazu passenden CU-Imagebuilds und dokumentiert, dass diese 2019/2022 nicht die separat veröffentlichten GDR-Builds enthalten. Für den statischen Abgleich gilt eine begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten; kumulativ höchstens 35/43/97. Kein Image wurde heruntergeladen oder gestartet.
  Der maschinenlesbare `container-images.proposed.json`-Lock und seine synthetischen Positiv-/Negativprüfungen erweitern den begrenzten Rahmen um weitere 1/1/2 Einheiten auf 36/44/99. Er bindet Profile, Labels und Digest-Referenzen statisch, ist noch nicht in einen Runtimeaufruf integriert und erteilt keine Laufberechtigung.
  Das vorgeschlagene Ressourcenprofil ergänzt Hersteller-Minimum, Hostreserve, harte Containergrenzen, SQL-Speicherlimit und bestehendes Zeit-/Cleanupbudget. Die zwei Microsoft-Quellen sowie die MCR-Layergrößen sind gebunden; die zusätzlichen 8/20-GiB-Host- und 4/3-GiB-Containerwerte bleiben ungemessene Projektannahmen. Begrenzte Erweiterung +1/1/2 auf kumulativ 37/45/101; kein Runtime- oder Ressourcenlauf.
  Der MCR-Tagabgleich findet GDR-spezifische Tags für 2019 und 2022, deren Image-Labels zu den neuesten Linux-CU+GDR-Builds passen. Lock und Preflight/Setup werden auf diese Tags und ihre neuen AMD64-Manifestdigests umgestellt; dies ist Registrymetadaten-, keine Engineevidenz. Begrenzte Erweiterung +1/1/2 auf kumulativ 38/46/103.
  PR #382 bindet QRY-023-Aufrufe, FWK-004-Prozedursignaturen und Messergebnis-Spalten mit zwei gezielten Offline-Regressionen an den bestehenden Framework-Contracts-Workflow. Alle zehn PR- und sieben relevanten Main-Workflows waren erfolgreich; kein QRY-023-SQL-Lauf. Begrenzte Erweiterung +1/1/2 auf 39/47/105.
  PR #383 integriert QRY-002-Lehrnotiz und Quellenregister nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die Lehre trennt beide Konvertierungsrichtungen von konkreter Plan-/Zugriffswirkung. Begrenzte Erweiterung +1/1/2 auf 40/48/107.
  Der folgende QRY-003-Schnitt präzisiert `datetime`- und `datetime2(7)`-Tagesgrenzen, `BETWEEN`-Inklusivität, typed `DATEADD` und die empirische SARGability-Grenze; `SRC-133` wird ergänzt. Kein SQL-Lauf. Begrenzte Erweiterung +1/1/2 auf 41/49/109.
  PR #384 ist integriert; fünf PR-Gates und drei Main-Workflows waren erfolgreich. Der folgende RES-004-Quellenabgleich bindet Lehrnotiz, `SRC-010`, `SRC-110` und die neue `SRC-134` ohne DMV-Lauf zusammen. Begrenzte Erweiterung +1/1/2 auf 42/50/111.
  PR #385 integriert die RES-004-Quellenregisterpflege nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der vollständige Lesepfad zeigt konsistente Lernziel-/Navigationsbezüge; der nächste Offlineentwurf konkretisiert QRY-003-Grenztupel und Ergebnisoracles. Begrenzte Erweiterung +1/1/2 auf 43/51/113.
  PR #386 integriert den QRY-003-Intervallentwurf nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Der nächste priorisierte Offlinekandidat ist QRY-007: Join-Kardinalität, `DISTINCT` und `EXISTS`, gebunden an `SRC-135`. Begrenzte Erweiterung +1/1/2 auf höchstens 44/52/115.
  PR #387 integriert QRY-007-Quellenbundle und Join-Kardinalitätsentwurf nach fünf erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. PR #388 ergänzt die quellengebundene Lehrnotiz mit Fixture, Ergebnis-/Multiplizitätsoracle und Curriculum-Navigation; vier PR-Gates und zwei Main-Workflows waren erfolgreich. Begrenzte Erweiterung +1/1/2 auf 45/53/117.
  Für den nächsten priorisierten IDX-003-Schnitt gilt eine begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Quellen-/Testkandidaten auf höchstens 46/54/119. Sie gilt für Key-Reihenfolge, INCLUDE, vier Ergebnisoracles und eine Seitengrößengegenprobe; keine Plan- oder Performancefreigabe.
  PR #389 integriert den IDX-003-Entwurf nach fünf erfolgreichen PR-Gates und drei betroffenen Main-Workflows. Der nächste priorisierte Schnitt ist die `IDX-004`-Lookup-Kurve mit abgestufter Trefferzahl, nicht abdeckendem/abdeckendem Index, vollständigem Tupeloracle und ohne allgemeine Prozentgrenze. Begrenzte Erweiterung +1/1/2 auf höchstens 47/55/121.
  PR #390 integriert das IDX-004-Quellenbundle und den Selektivitäts-/Oracleentwurf; fünf PR-Gates und drei Main-Workflows waren erfolgreich. Der folgende Schritt bindet die Lookup-Erklärung in den Curriculum-Lesepfad, ohne einen Kippunkt oder Performancevorteil zu behaupten. Begrenzte Erweiterung +1/1/2 auf höchstens 48/56/123.
  Der Nutzer hat die autonome Fortsetzung ausdrücklich angeordnet und darauf hingewiesen, dass begrenzte Budgets bei kontinuierlicher Entwicklung fortgeschrieben werden müssen. Für den folgenden klar isolierten IDX-001-Offlineentwurf gilt deshalb eine neue, begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und höchstens 2 Quellenkandidaten auf kumulativ 49/57/125. Sie autorisiert keine SQL-/Runtimeausführung oder menschliche Generalprobe.
  PR #392 integriert den IDX-001-Entwurf nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die fortlaufende autonome Entwicklung erhält für IDX-002 eine weitere begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 50/58/127. Diese gilt ausschließlich für den statischen Quellen-/Designschnitt zur Clustered-Key-Breite und erteilt keine SQL-/Runtimefreigabe.
  PR #393 integriert IDX-002 mit fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der folgende begrenzte Offlineentwurf STL-001 erweitert den fortlaufenden Auftrag um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 51/59/129. Es gibt keine SQL-/Runtimefreigabe oder Generalprobe.
  PR #394 integrierte STL-001 mit fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Für STL-002 galt eine weitere begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 52/60/131; PR #395 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert.
  PR #395 schloss den STL-002-Schnitt ab. Für QRY-005 galt eine Fortsetzungserweiterung um 1/1/2 auf kumulativ 53/61/133; PR #396 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert. Der nächste OPT-004-Teilschnitt erweitert den Rahmen um 1/1/2 auf kumulativ 54/62/135. Er gilt ausschließlich für die Korrelations-/Mehrspaltenstatistikfrage und keine SQL-/Runtimeausführung.
  PR #396 schloss den QRY-005-Offlineentwurf ab. Für den begrenzten OPT-004-Korrelationsschnitt galt eine Fortsetzungserweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 54/62/135; PR #397 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert.
  PR #397 schloss den OPT-004-Korrelations-/Mehrspaltenstatistikentwurf ab. Der noch offene Constraint-Vertrauens- und Eindeutigkeitsschnitt erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 55/63/137. Runtime, Cleanupqualifikation und menschliche Generalprobe bleiben ausgeschlossen.
  PR #398 integriert den getrennten OPT-004-Constraint-/Eindeutigkeitsschnitt nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die Fortsetzung zu STL-003 erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 56/64/139. Sie umfasst ausschließlich Quellen- und Offlineentwurf zum Forwarded-Record-Lifecycle; keine SQL-/Runtimeausführung oder menschliche Generalprobe.
  PR #399 integriert STL-003 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. QRY-011 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 57/65/141; Scope sind Quellenprüfung, synthetische vollständige Ergebnisoracles und ein statischer Entwurf zu Filtered Indexes, berechneter Spalte und einer SET-Option-Gegenprobe. Keine SQL-/Runtimeausführung, Planfreigabe oder menschliche Generalprobe.
  PR #400 integriert QRY-011 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. IDX-005 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 58/66/143; Scope sind aktuelle Primärquellen und ein statischer Entwurf zur Prüfung zweier überlappender Missing-Index-Vorschläge, Indexkonsolidierung und DML-Trade-offs. Keine SQL-/Runtimeausführung, Indeximplementierung oder menschliche Generalprobe.
  PR #401 integriert IDX-005 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. OPT-012 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 59/67/145; Scope ist ein quellengebundener Offlineentwurf zu Eligibility, Wiederverwendung desselben Plans, kleinem/großem Build-Input und Actual-Plan-Nachweisen. Keine SQL-/Runtimeausführung, adaptive Planformgarantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #402 integriert OPT-012 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. STL-010 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 60/68/147; Scope sind aktuelle Primärquellen und ein statischer Entwurf zum Abgleich synthetischer Kompressionsprofile, Schätzungen in `tempdb` und tatsächlicher Seitenbelegung. Keine SQL-/Runtimeausführung, pauschale Editionsannahme, Leistungsrangfolge oder menschliche Generalprobe.
  PR #403 integriert STL-010 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der nächste begrenzte QRY-003-Schnitt erweitert die kumulative Obergrenze um 1/1/2 auf 61/69/149; er prüft vorhandene Datumsquellen und vervollständigt bei Bedarf den statischen Entwurf samt Ergebnistupeln für `datetime` und `datetime2(7)`. Keine SQL-/Runtimeausführung, Plan-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #405 integriert QRY-003 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. QRY-007 erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 62/70/151; Umfang sind Quellenprüfung und vollständige statische Tupeloracles für One-to-many-Join, `DISTINCT`, `EXISTS` und angeforderte Kindaggregation. Keine SQL-/Runtimeausführung, pauschale `DISTINCT`-Empfehlung, Plan-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #406 integriert QRY-007 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. IDX-003 erhält eine begrenzte Fortsetzungserweiterung um 1/1/2 auf kumulativ 63/71/153; Scope sind Quellenabgleich, Prüfung der statischen Fixturezählwerte und vollständige Tupeloracles für Key-Reihenfolge-/INCLUDE-Profile. Keine SQL-/Runtimeausführung, Seek-Garantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #408 integriert IDX-003 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. IDX-004 erhält eine begrenzte Erweiterung um 1/1/2 auf kumulativ 64/72/155; Scope sind Quellenprüfung, deterministische Fixtureformeln und vollständige Tupeloracles für die Lookup-Treffermengen auf BASE-, LOOKUP- und COVERING-Profilen. Kein SQL-/Runtimelauf, garantierter Lookup-/Scan-Übergang, Leistungsclaim oder menschliche Generalprobe.
  PR #410 integriert IDX-004 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständige Fixtureformel, Bandintervalle und sortierten Tupeloracles sind gebunden; Plan-/Lookup-/Read-Befunde bleiben empirisch. IDX-001 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 65/74/157. Scope: aktuelle Quellenprüfung und vollständige Punkt-/Bereichsoracles für HEAP und CLUSTERED. Kein SQL-/Runtimelauf, keine Planformgarantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #412 integriert IDX-001 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständigen Punkt-/Bereichsoracles sind für beide Row-Locator-Profile gebunden; Enginequalifikation und Planwahl bleiben offen. IDX-002 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 66/76/159. Scope: aktuelle Quellenprüfung, exakte Fixtureformeln und vollständige Ergebnistupeloracles für `NARROW_UNIQUE` und `WIDE_NONUNIQUE`. Keine SQL-/Runtimeausführung, Größen-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #414 integriert IDX-002 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständigen Fixtureformeln und Band-37-Tupeloracles sind gebunden; Größenmodell und gemessene Seiten bleiben getrennt. STL-001 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 67/78/161. Scope: aktuelle Quellenprüfung, vollständige Tupeloracles der vier kumulativen Heapprofile und Nachrechnung des Größenmodells. Keine SQL-/Runtimeausführung, Page-Density- oder Leistungsbehauptung oder menschliche Generalprobe.
  PR #416 integriert STL-001 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Vollständige Ergebnistupeloracles, Verteilungen und Modellrechnungen sind gebunden; Heapseiten bleiben empirisch. STL-002 erhält eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 68/80/163. Scope: Quellenabgleich sowie exaktes Payload-/Padding-Oracle und kanonischer Tupelvergleich für INROW, ROW_OVERFLOW und LOB. Keine SQL-/Runtimeausführung, keine Allocation-Unit- oder Leistungsbehauptung und keine menschliche Generalprobe.
  Vor dem nächsten Start muss der Verbrauch anhand des aktuellen Status und
  der Integrationshistorie verifiziert werden; der zuletzt dokumentierte
  Startverbrauch 1/19/45 ist kein Nachweis des heutigen Restbudgets.
- Token- und Geldverbrauch bleiben unbekannt. Die endlichen Kandidaten-/PR-
  Obergrenzen begrenzen die Arbeit, sind aber keine behauptete Kostenmessung
  oder Provider-Ausgabensperre.
- Aufwand für den RES-003-Offlineschnitt: ein Prüfer und eine gezielte
  Testdatei wurden lokal einmal ausgeführt und im passenden PR- und
  Main-Workflow erneut geprüft; kein SQL-Lab-Trigger. Für die aktuelle
  Lehrergänzung werden die zwei direkt betroffenen Markdown-Lesepfade und ihre
  Microsoft-Quellen geprüft; keine Code- oder SQL-Ausführung.
  Für die `OPTIMIZED_SP_EXECUTESQL`-Detailprüfung wurden zwei Microsoft-
  Quellenstellen geprüft und die vorhandene `QRY-004`-Abnahme als Curriculum-
  Verbraucher abgeglichen; keine Code-, SQL- oder Runtimeausführung.
  Für den Graph-Table-Schnitt wurden die aktuelle Curriculum-Abdeckung und zwei
  Microsoft-Primärquellen geprüft; ein Planungsdokument und zwei bestehende
  Index-/Statuspfade wurden angepasst. Keine Code-, SQL- oder Runtimeausführung.
  Für die getrennte Graph-Versions-/Indexwelle wurden zwei Microsoft-Quellen,
  Review- und Statusnotiz sowie Backlog-/Planungspfade geprüft; kein Code-,
  SQL- oder Runtimeaufruf.
  Die Curriculum-Zuordnung glich `CURRICULUM_ARCHITECTURE.md`,
  `TRACEABILITY_MATRIX.md`, `SLIDE_STATEMENT_REGISTER.md` und den
  Masterimplementierungsplan ab; keine neuen Produktquellen, Code- oder
  SQL-Ausführung.
  Die 2022/2025-Übersichten werden auf Graph-Einträge geprüft; Abwesenheit in
  der Änderungsübersicht wird nicht als Abwesenheits- oder Paritätsbeweis
  ausgelegt. Keine Code- oder SQL-Ausführung.
  Der Graph-Demoentwurf wird an den zwei vorhandenen Microsoft-Einstiegsquellen
  und am Framework-Demovertrag abgeglichen; keine SQL-/Runtimeausführung und
  kein zusätzlicher Testlauf.
  Fehlende/fehlgeschlagene
  Evidenz wird lokal nur bei neuem Befund weiter untersucht. Ein Owner, keine
  zusätzliche Reviewkette und keine Subagenten; reale Token-/Geldmessung bleibt
  unbekannt.
- Nach jedem kohärenten Schnitt: relevante lokale Prüfungen und erforderliche
  unabhängige Prüfung, PR- und Main-Gates gemäß Projektregeln, Integration,
  Main-Synchronisierung und Branchbereinigung. Begonnene Arbeit nicht als
  abgeschlossen melden, solange diese Integrationsschritte offen sind.
- Bei FAIL, fehlender Evidenz, unbekanntem Zustand, veraltetem Quellenbinder,
  verbrauchter Obergrenze oder nicht erfülltem Gate: keine Folgeausführung.
  Fehler nicht weginterpretieren und unveränderte Kandidaten nicht wiederholen.
  Den Blocker mit Wiederaufnahmebedingung im kanonischen Ausführungsstand
  vermerken.

Die Umsetzung dieser Planung selbst ist keine Aufforderung, nach Abschluss
dieses Planungsdokuments autonom mit Arbeitspaket 1 fortzufahren. Eine spätere
Fortsetzung muss am dann aktuellen Status und der dort wirksamen Autorisierung
ansetzen.

## Historischer Planungsstand vom 20. Oktober 2026

Der damalige Benutzerauftrag nahm nach Bestandsprüfung die
allgemeine Entwicklung wieder auf. Der interne Capture-Vorschnitt war nach
[unabhängigem Review und aktueller CI](DGN_007_INTERNAL_CAPTURE_RECEIPT_REVIEW.md)
über PR255 integriert und vollständig bereinigt. Danach ist ausschließlich der
[SESSION_END-Entwurf §34](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild)
aufgenommen: maximal zwei Entwurfsstände, Checkpoint nach dem ersten,
ein unabhängiger Designreview und aktuelle Dokumentationsgates. Frühere
ausgeschöpfte Quell-/Import-/Generatorwellen erhalten keine neuen Versuche.
Der Erststand `a6ca3f5…` ist unabhängig ohne Befunde geprüft, alle acht
Dokumentationsgates sind grün. PR256 führt den endgültigen Head-/Base- und
Main-Abschluss; der nächste Implementierungskandidat wäre erst danach ein
separat gewählter reiner Footer-/Trace-Matcher mit eigenen Quellen- und Testgates.
Die folgenden älteren Pausen-/G13-Planungsstände sind insoweit historisch.
Keine Automationaktivierung und keine operative Kanal-/Loader-/Worker- oder
SQLimplementierung in dieser Designwelle.

| Merkmal | Wert |
|---|---|
| Historischer Status zum damaligen Planungsstand | allgemeine Entwicklung `PAUSED`; PR68-Code `BLOCKED` durch damalige Runtimefehler; Prüfbericht und Abschlussprozess getrennt |
| Historischer Bezugsstand | 2026-10-08 |
| Ausgangsstand | Produktive Runtimeevidenz bis Pull Request 42; begrenzte DGN-007-Kontrollcaptures bis Pull Request 62 und prospektiver Prüfvertrag aus Pull Request 63 und skalarer Transport aus Pull Request 64 sowie begrenzter SQL-Producer aus Pull Request 65; Detailstand in `CURRENT_EXECUTION_STATUS.md` |
| Bezug | [Aktueller Ausführungsstand](CURRENT_EXECUTION_STATUS.md), `.ai/BACKLOG.md`, `MASTER_IMPLEMENTATION_PLAN.md` |
| Zweck | priorisierte, kleine Folgepakete; keine Aussage, dass die beschriebenen Inhalte bereits umgesetzt sind |

## 1. Planungsgrundlagen

Der gezielte Benutzerauftrag vom 2026-10-09 betrifft Prüfung und Abschluss von
PR 68 sowie DEC-069; der [G13-/PR-Review](DGN_007_G13_PR_REVIEW.md) führt diesen
isolierten Diagnoseschnitt. Er verlangt erfolgreiche relevante aktuelle CI (Continuous Integration; automatisierte Integrationsprüfungen),
ohne G13 oder die offene Methodenentscheidung zu ändern. Die nachfolgende
allgemeine Folgeplanung und die interne Capture-Rückgabe bleiben ausdrücklich
zurückgestellt.
Der aktuelle Reporter-Head `f9ec582…` scheiterte auf 2022 an SQL20 und auf
2025 an G13. Deshalb wird nur der geprüfte Befund und Abschlussprozess getrennt
integriert; der Code-PR ist vorübergehend geschlossen und sein Branch wegen
nicht übernommener Änderungen erhalten. Zusätzlicher Scopeentscheid angefragt;
kein Bypass und kein Wiederholen unveränderter Kandidaten bis grün.

Die Entwicklung wurde am 2026-10-07 nach der über PR 92 dokumentierten Pause
ausdrücklich mit den bisherigen Regeln wieder aufgenommen. Seit dem Benutzerstopp
vom 2026-10-08 gilt `PAUSED`: nur den bereits laufenden §33-DESIGN-/PR-Schnitt
vollständig integrieren und seinen eigenen Branch unabhängig bereinigen; danach
Orchestrator und Subagents beenden. Alle hier genannten Folgepakete einschließlich
SESSION_END sind bis zu einer neuen ausdrücklichen Wiederaufnahme zurückgestellt.
Der vollständige Einstieg samt offener Reihenfolge und geschützter ungemergter
Arbeit steht in [CURRENT_EXECUTION_STATUS.md §0](CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Der getrennte [Darstellungs- und Digestentwurf §10](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#10-vollständig-erhaltender-darstellungs--und-digestentwurf)
liegt als `DESIGNED` vor. Die separat vorgewählte vollständige Kontrollfixture
und reine Größenprüfung in [§11](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture)
belegen 85 Records und gemeinsame Metadata von 17.127/17.113/17.091 Bytes:
Der Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap bei allen Ordinals.
Der separate [Stringpoolentwurf §12](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf)
liegt als `DESIGNED` vor, mit eigenen lokalen Pools, vollständigen Formfeldern und
unveränderten Caps einschließlich höchstens 256 Poolwerten. Der eigene
[reine Pool-Sizer §13](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer)
bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue
3×5-Größenprüfung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte.
Unabhängige vollständige Nachrechnung und Feldrückgewinnung bestätigt; keine
erneute Aufnahme oder Nonce. Der getrennte experimentelle Codec-/Digestpfad im
[Vertrag §14](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests)
bestand 41/41 isolierte Gegenproben ohne SKIP, unabhängigen Quell-/Testreview
und die vollständige Originalfixture: alle 3×5 Frames, Feldrückgewinnung,
kanonischer Repack und neun eigene Digestwerte. Gesamtausgabe
28.264/28.257/28.246 Bytes; unabhängig aus unveränderten Eingaben nachgerechnet,
ohne Codec-/Helper-Replay. Der eigene reine
[kombinierte Eingangsprototyp §15](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen)
bestand 34/34 isolierte Gegenproben ohne SKIP und die vollständige Originalfixture
mit drei Frames zu jeweils 140.226 Bytes: 9.389 Metadata einschließlich Header,
130.837 unveränderte Rawbodybytes. Vollständige tatsächliche Rückgewinnung,
Repack und unabhängige Stdlib-Nachrechnung ohne Replay bestanden.
Die konkrete operative [Bootstrap-/Kanalreihenfolge §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
liegt als `DESIGNED` vor. Der reine [Kontrollbootstrapquellengenerator §17](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen)
bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Frische operative Auswahl, inline Empfang und Reporting, Parent-/Worker-Anbindung,
Loader, Consumption, Replay und unabhängig bereinigte eigene Worker bleiben
getrennte Gates; die charakterisierte Fixture ist keine operative Workerbaseline.
Die Wiederaufnahme ändert keine fachliche Freigabe oder offenen Methodengates.

- `QRY-004` (Optionale Filter, Recompile und dynamisches SQL), `DGN-003` (Abfragehistorie mit Query Store), `DGN-005` (Gezielte Ereigniserfassung mit Extended Events), `OPT-017` (Ungleich verteilte parallele Arbeit) und alle neun Demos aus `W-COV-001` besitzen aktuelle Matrixnachweise aus GitHub Actions.
- `WARN_EMPIRICAL_VARIANCE` ist nur dort als Freigabeausgang zulässig, wo der Demo-Vertrag die empirische Abweichung ausdrücklich beschreibt und alle invarianten Ergebnis-, Sicherheits- und Cleanup-Verträge erfüllt sind.
- Die Curriculum-Analyse verlangt kein neues Hauptmodul. Neue Arbeit erweitert deshalb nur bestehende Lernziele und Demo-IDs.
- Jede Welle ist ein eigenständiger, kleiner Pull Request mit klarer Runtime-, Quellen- und Safety-Grenze. Öffentliche Herstellerdokumentation wird erst nach dem Source-Register-Delta-Review zu Lehrinhalt.

Der reine begrenzte Header-/Metadata-Vorschnitt aus gehaltenen Chunks nach
[§23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme)
ist implementiert und unabhängig geprüft: einziger isolierter Lauf mit
174/174 PASS ohne SKIP; fünf bisherige Builder und 149 alte Tests erhalten.
Die reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands)
ist im einzigen isolierten Lauf mit 209/209 PASS ohne SKIP geprüft;
sechs bisherige Builder und 174 alte Tests bleiben erhalten.
Die reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich)
ist nach zwei engen Fixturekorrekturen mit 243/243 PASS ohne SKIP geprüft;
sieben bisherige Builder und 209 alte Tests bleiben erhalten.
Die reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies)
ist nach einer Fixturelabelkorrektur mit 272/272 PASS ohne SKIP geprüft;
acht bisherige Builder und 243 alte Tests bleiben erhalten.
Die reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords)
ist im einzigen isolierten Lauf mit 304/304 PASS ohne SKIP geprüft;
neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei neue
Fixturelabelkorrekturen wurden vor dem ersten Lauf geprüft.
Die reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich)
ist im einzigen isolierten Lauf mit 341/341 PASS ohne SKIP geprüft;
zehn bisherige Builder und 304 alte Tests bleiben erhalten.
Die additive reine [R→BODY_RELEASE-Planquelle §29](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#29-deklarativer-rbody_release-plan)
ist im einzigen isolierten Lauf mit 378/378 PASS ohne SKIP synthetisch geprüft:
vollständige Actual-/Caller-R4- und unabhängige K8-Bindung vor Command-SHA,
gehaltene äußere Anker und atomare reine Rückgabe; elf alte Builder und
341 alte Methoden bleiben erhalten. Phasenlabels attestieren weder vorherige
Übergänge noch Einmalverbrauch. Der separate
[INPUT_COMPLETE-Recordvertrag §30](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#30-deklarativer-input_complete-rückkanalrecord)
ist als reine additive Quelle implementiert und im einzigen isolierten Lauf mit
413/413 PASS ohne SKIP geprüft: vollständige Caller-/Receivedformen und Semantik,
kanonische Actualbytes, eigene vollständige K-Domainbindung und dominante POSTs.
Zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige
[Record-/Footer→R-Calleradapter §31](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#31-vollständiger-deklarativer-profilrecord-callerabgleich)
ist rein additiv implementiert und im isolierten synthetischen Lauf mit
460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden
bleiben erhalten. PR 118 ist vollständig integriert; geprüfte Basis ist
`f6559e084ebd660a41a503129f1a28c32be8848b`. Die getrennten CI-/Übernahme-/Cleanupbelege
stehen in [CURRENT_EXECUTION_STATUS.md §0](CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente)
ist mit 66/66 isolierten synthetischen Methoden ohne SKIP geprüft.
Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Operativer Workerbetrieb und Ressourcen-Cleanup bleiben getrennte Gates.

## 2. Priorisierte Wellen

| Reihenfolge | Welle | Ziel und abgegrenzter Umfang | Akzeptanzkriterium |
|---:|---|---|---|
| 1 | `LABSCN-005/DGN-007` | Capstone erst als eigenen Schnitt planen, nachdem Query-Store-/XE-Pilot und `CON-006` (Zyklische Sperrkonflikte erkennen) praktisch wiederverwendbare Evidenz- und Mehrsession-Verträge liefern. | Incident, Alternativhypothesen, Zeitfenster, Reset, Quellen und Teilnehmerübergabe sind vollständig; keine versteckte Lösung in Teilnehmerartefakten. |
| 2 | nächster `LABSCN-005`-Einzelslice | Nur einen Kandidaten mit eigenem Quellen-, Safety- und Detailreview auswählen; keine pauschale Infrastrukturwelle. | Lernmehrwert, Providerbedarf, Reset, Cleanup und versionsgebundene Aussage sind vor Implementierung eindeutig. |
| 3 | weitere `LABINT-004`-Matrix | Nur für einen neu freigegebenen gelben Szenarioslice aktivieren. | Matrix und Cleanup prüfen ausschließlich die neue freigegebene Aussage. |

## 2.1 Umsetzungsstand der Wellen

| Welle | Status | Evidenzgrenze |
|---|---|---|
| `TSK-002` (Detailreview LABSCN-005/DGN-007: Capstone-Planungsschnitt mit Incident-, Hypothesen-, Zeitfenster-, Reset- und Teilnehmeruebergabevertrag) | `DECIDED_PLANNING` | Detailreview [LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md) entscheidet den Capstone-Planungsschnitt; daraus folgt kein Implementierungsauftrag und kein Runtimestatus. |
|---|---|---|
| `W-STA-001` | `VALIDATED` | Lauf 33222989681 belegt die vollständige Matrix einschließlich der erwarteten empirischen Warnungen. |
| `W-DGN-001` | `VALIDATED` | Lauf 33222989682 belegt alle zwölf Query-Store-/XE-Pilotläufe mit `PASS/OK`. |
| `W-SCN-001` | `VALIDATED` | Project Adapter `0.1` und vollständiger SQL-Server-2025-Lifecycle sind auf Docker und Podman praktisch validiert. |
| `W-ADV-017` | `VALIDATED` | Lauf 33447840232 belegt Actual DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung), Exchange, positive Threadarbeit und Cleanup auf allen drei Zielversionen. |
| `W-SQL25-001` | `VALIDATED` | Quellen-, Claim- und Entscheidungsgrundlage ist abgeschlossen; daraus folgt keine neue Featuredemo. |
| `W-PRS-001` | `VALIDATED` | 102 SlideKeys, drei Custom Shows, Build 41/66/102 und vollständige Master-/Profilrender liegen vor. |
| `W-COV-001` | `VALIDATED` | Lauf 33222989644 belegt alle neun Demos; `CON-009` (Kosten in tempdb unterscheiden) endet auch auf SQL Server 2019 zweimal mit `PASS/OK`. |
| `W2-002` | `VALIDATED` | Neun `W2-A`-Altquellen sind nicht ausführbar; vier aktive Ersatzdemos und alle künftigen Neuaufbauten sind an synthetische, neutrale Datenverträge gebunden. |
| `ADV-009` (Folienspezifikation Modul M03, Lernziel LO-M03-07) | `VALIDATED` | Runtimewarnung, Masterdeck, Notes, Hashbindung, vollständiger Render und Privacy-Freigabe sind synchron. |
| `ADV-010` (Folienspezifikation Modul M03, Lernziel LO-M03-08, Parametersensitive Planoptimierung) | `VALIDATED` | Fachliche, didaktische und technische Endabnahme grenzt verbleibende Designs ausdrücklich als Folgearbeit ab. |
| `LABSCN-002` | `VALIDATED` | 22 produktive Demos sind vollständig mit Lifecycle, Provider, Ressourcen, Versionen, Reset und Evidenz inventarisiert. |
| `LABSCN-004` | `VALIDATED` | Der generische Benutzerablauf für Auswahl, Start, Übergabe, Reset und Remove ist dokumentiert und statisch geprüft. |
| `INF-002`/`INF-003` | `VALIDATED` | Docker und Podman melden `RESOURCE_OK`; der kompakte SQL-Server-2025-Lifecycle und Recovery-Pfad sind dokumentiert. |
| `LABINT-003` | `VALIDATED` | Provider-Parität ist für `QRY-001` (Indexfreundliche Suchbedingungen), `CON-004` (Blockierungsketten verfolgen) und `DGN-005` praktisch belegt. |
| `LABSCN-005/DGN-005` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `d5143f2a-…` und Podman-Run `82791985-…` führten die Teilnehmerphasen aus und endeten nach Start und Reset vollständig als `REMOVED`. |
| `LABSCN-005/CON-006` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `76cff6ed-…` und Podman-Run `6d2d0a51-…` belegten Opfer 1205, Survivor, Deadlock-Graph, geordnete Gegenprobe, Reset und `REMOVED`. |
| `LABSCN-005/DGN-007` | `IMPLEMENTED_STATIC_SLICE_B` | Der nicht-promotende statische Teilnehmerfluss bestand am 2026-09-19 auf SQL Server 2025/Linux mit Docker (`ea802c20-…`) und Podman (`fba84720-…`): Adapter-Preflight, Install/Validate, alle sechs Teilnehmerstufen, Cleanup und Lab-Remove (`PASS`/`REMOVED`). Kontrollierte Negativtests auf Docker mit SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`) ergaben kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, im Lab-Core `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und `REMOVED`. Das ist keine 2019/2022-Fachunterstützung und keine Promotion, sondern ausschließlich der erwartete 2025-only-Skip-/Cleanup-Nachweis. Weiterhin keine `READY_FOR_USER`-Übergabe, keine Szenariopromotion und kein Nachweis für `scenario.json`, Manifest, Inventar oder vollständige Lifecycle-/Versionsmatrix. |
| `LABINT-004/CON-006` | `VALIDATED` | Die vollständige freigegebene Matrix SQL Server 2025 × Docker/Podman ist praktisch belegt und prüft ausschließlich den neuen gelben Slice. |
| `DGN-007_DATA_MODEL` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; unabhängiger Datenbankabbau und eigene Container entfernt. [Nachweis](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md). Der Datenmodell-Scope bleibt begrenzt und unverändert als Default. |
| `DGN-007_QUERY_STORE_WINDOWS` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; zwei disjunkte Katalogintervalle, gleiche Parameterlast, je vier Suchausführungen und unabhängiger Cleanup. [Nachweis](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md). Runner und CI prüfen diesen Scope getrennt; kein Incident- oder Regressionsnachweis. |
| `DGN-007_PROFILE_COMPARISON` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden gewichtete T0/T1-Metrikvergleiche auf allen drei Versionen je zweimal, einschließlich unabhängigem Cleanup. [Nachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md). Ohne Richtungsgate oder Incidentpromotion. |
| `DGN-007_CONTROL_AB` / `BA` / `AA` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden alle drei neutralen Kontrollfolgen auf jeder Version je zweimal; vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Abbau aller drei eigenen Instanzen. Tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Variation im [Nachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md). Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation; keine Incidentfreigabe. |
| prospektiver `DGN-007` (Zeitabhängige Regression eines Suchworkloads)-Prüfvertrag | `STATIC_PROSPECTIVE_CONTRACT` | `DEC-068` (Prospektive Duration- und Kontrollseparation für DGN-007 festlegen), reine Record-/Separationsprüfung, 34 synthetische Tests und Quellenvalidator lokal PASS. [Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md). Keine SQL-Runtime-Abnahme; Collector und frische Bestätigungsläufe bleiben offen. |
| skalarer `DGN-007`-Collector-Transport | `STATIC_COLLECTOR_TRANSPORT` | Reiner JSON-Decoder mit genauer Decimal-/100-ns-Darstellung, 19 Transporttests und beide Validatoren lokal PASS; 34 Prospektivtests bleiben grün. [Transportgrenze](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md). Keine SQL-Erfassung oder vollständigen RunRecords; fehlende Request-Ergebniszeilen bleiben `NOT_CAPTURED`/`None`. |

## 3. SQL-Server-2025-Delta: abgeschlossene Entscheidungen

Der abgeschlossene Delta-Review dokumentiert folgende Zuordnung:

| Herstellerfunktion | bestehende Anknüpfung | Entscheidung |
|---|---|---|
| Cardinality Estimation Feedback für Ausdrücke | `OPT-006` | `ADOPT`; keine neue Demo, spätere Evidenz im bestehenden Schnitt |
| Optimiertes `sp_executesql` | `QRY-004`, `OPT-007` | `DEFER`; eine spätere Concurrent-Compile-Detailanalyse ist nach der nun belegten `QRY-004`-Freigabe zulässig |
| zeitgebundene Extended-Events-Sessions | `DGN-005` | `ADOPT`; optionaler Engine-17-Schutzpfad |
| TempDB Space Resource Governance | `CON-009`, `RES-004` | `DEFER`; roter Safety- und Infrastrukturvertrag erforderlich |
| Ordered nonclustered Columnstore | `IDX-010` (Columnstore-Segmente gezielt überspringen) | `DEFER`; gelbes Detaildesign erforderlich |
| Query Store auf lesbaren Secondary Replicas | kein unmittelbarer Slice | `DEFER`; Preview- und Mehrinstanzabhängigkeit |

Vector- und KI-Funktionen liegen außerhalb des derzeitigen Curriculumzuschnitts. Der Review verwendet als Ausgangspunkt die offiziellen Microsoft-Dokumentationen zu [SQL Server 2025](https://learn.microsoft.com/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17), [Extended Events](https://learn.microsoft.com/sql/relational-databases/extended-events/sql-server-extended-events-sessions?view=sql-server-ver17) und [Query Store auf Secondary Replicas](https://learn.microsoft.com/sql/relational-databases/performance/query-store-for-secondary-replicas?view=sql-server-ver17); vor einer Inhaltsübernahme muss der Projekt-Quellenregisterprozess durchlaufen werden.

## 4. Abhängigkeits- und Stop-Regeln

```text
LABSCN-002 + LABSCN-004 -> DGN-005 + CON-006 validiert -> weiterer Kandidat nur nach Einzelreview
Query Store/XE-Pilot + Mehrsession-Vertrag validiert -> DGN-007 als eigener Folgeschnitt zulässig
```

- Kein `DGN-007` ohne validierten Query-Store-/XE-Pilot.
- Keine rote oder gelbe Lastdemo ohne bestehende Safety-Gates, Wegwerfinfrastruktur, Kill-Switch und Laufzeitbudget.
- Keine Änderung an `SQL_Server_Lab` ohne dokumentierte Fähigkeitslücke und ausdrückliche Freigabe.
- Keine Statusanhebung aus statischem Testbestand allein; Runtime-Status benötigt einen konkreten Laufnachweis.

## 5. Nächster belegpflichtiger Schritt

Der eigenständige automatisierte Datenmodellvertrag ist auf Docker für alle
drei Zielversionen jeweils zweimal praktisch belegt. Seine Prüfungen enthalten
keine Incident-, Query-Store-, XE-, Hypothesen-, Mitigations- oder interaktive
Teilnehmerabnahme. Der anschließend getrennt implementierte
`DGN-007_QUERY_STORE_WINDOWS`-Vertrag ist auf allen drei Versionen je zweimal
praktisch belegt. Er prüft ausschließlich disjunkte T0/T1-Capture-Fenster mit
gleicher Parameterlast. Der getrennte neutrale `DGN-007_PROFILE_COMPARISON`-
Vertrag bestand am 2026-10-07 ebenfalls je zweimal auf allen drei Versionen:
gewichtete Mittelwerte, T1-T0-Deltas und tatsächlich ausgeführte Plananzahl;
kein Richtungs- oder Mindestplangate. Die NULL-Ratio bei Null-Baseline wurde
gesondert mit numerischer Fixture geprüft. Lokale Matrix,
skalare Messwerte und unabhängiger Cleanup stehen im
[Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md).
Die zusätzlichen neutralen AB-/BA-/AA-Kontrollcaptures sind auf jeder Version
je zweimal praktisch belegt. Sie prüfen denselben Vierermix in fester tatsächlicher
Reihenfolge und unterscheiden ausgeführte Planmengen über beide Fenster.
AB/BA zeigten zwei aktive Plan-IDs/Hashes, AA dieselbe Plan-ID in beiden Fenstern.
Die vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Cleanup
steht im [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md).
Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation;
positives Vorzeichen allein trägt deshalb keine versionsübergreifende
Separation. Diese Captures sind explorative Voraussetzungen, keine
prospektiven Bestätigungsläufe einer Incidentregel. Der getrennte reine
[Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
legt diese Regel jetzt vorab fest (`DEC-068`): gewichtete Statement-Duration
als primäre zeitbezogene Metrik, alle vier B-A-Kontraste unter AB/BA strikt
positiv und oberhalb beider absoluter AA-Drifts; zusätzlich global entweder
vier unterschiedliche aktive Hashmengen oder einheitlich gerichtete Reads-
Kontraste oberhalb beider absoluter AA-Reads-Drifts. 34 synthetische Tests und
der Quellenvalidator bestanden lokal. Der Status ist ausschließlich
`STATIC_PROSPECTIVE_CONTRACT`, keine Runtime-Abnahme. Der getrennte
[Transport-Vorschnitt](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: 19 tatsächliche
Decoderfixtures, beide Validatoren und die 34 Prospektivtests lokal PASS.
Decimal-Text und UTC-100-ns-Integer bleiben präzise. Fehlende Request-
Ergebniszeilen bleiben `NOT_CAPTURED`/`None`; deklarierte `MEASURED`-Werte
attestieren keine Herkunft. Der Body enthält keine erfundenen Phasen-,
Cleanup-, Lifecycle- oder Ressourcenangaben. Der getrennte SQL-Producer
speichert jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
die vollständige skalare Projektion vor Cleanup bereit. Seine neue lokale
2019/150-, 2022/160- und 2025/170-Matrix bestand je zweimal AB/BA/AA,
insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder und unabhängigem
Cleanup. Alle drei eigenen Container sind unabhängig abwesend bestätigt.
Der [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md)
bindet konkrete Versionen, Images und Quellenfreeze und hält frühere
Fehlversuche getrennt fest. 156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und
einen Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
[Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
ist abgeschlossen: 14 Workflows und alle 22 Jobs SUCCESS am Head
`20a867e…` gegen Base `94ed561b…`, Integration `df78cb0…`.
Je Version bestanden zwölf Lifecycles mit sechs tatsächlichen Decoder-
Captures und unabhängigem Cleanup; Linux führte alle 156 Methoden ohne
SKIP aus. Der Squash `da7b0eb…`, vollständige Übernahme, synchronisiertes
Main und lokale/remote Bereinigung des eigenen Branches sind bestätigt.
Die zwei historischen CI-Fehler bleiben getrennt dokumentiert, ohne
behauptete Ursache oder Behebung. SQL-Prädikate und Budgets bleiben gleich.

Die getrennte Main-Push-CI am Squash `da7b0eb…` ist danach vollständig
beendet: 12/13 Workflows und 47/48 Jobs SUCCESS, ausschließlich SQL Server
2022 im zweiten BA-Lifecycle `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`.
Alle zehn begonnenen 2022-Abwesenheitsprüfungen und der ownergebundene
Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
2019/2025 bestanden je zwölf Lifecycles und sechs Captures. Der neue Fehler
ist von der erfolgreichen PR65-Integration und den zwei historischen
CI-Fehlern getrennt zu bewerten; seine skalare Ursache ist offen.

Die private skalare Probe ist als begrenzte Gegenprobe abgeschlossen: auf
neuer eigener 2022-Instanz mit CI-Imagebindung und tatsächlicher Version
`16.0.4295.3` bestanden Datenmodell, Fenster, Profil, AB und BA jeweils zweimal,
insgesamt zehn Lifecycles und vier Decoder-Captures. Zehn unabhängige
Datenbankabwesenheitsprüfungen, fünf Gruppen-Leerheitsprüfungen, Quellenfreeze
mit 21 Dateien und unabhängiger own-CID-/Namensabbau bestanden. G13 wurde
nicht reproduziert; es liegen keine tatsächlichen verletzten Grenzabstände vor.
Zwei frühere private synthetische Vorchecks scheiterten vor jedem Lifecycle;
Defekte und unabhängiger Cleanup bleiben im Producernachweis getrennt.
Kein Main-, Incident- oder Behebungsnachweis; AA wurde nicht ausgeführt.

Nächster belegpflichtiger Schnitt ist ein eigener kanonischer Diagnosebericht,
keine identische Wiederholung: maximal acht gespeicherte verletzte
Profilgruppen, exakte UTC-Ticks und Grenzabstände ausschließlich im bereits
ausgelösten G13-Fehlerzweig. Der Runner bindet diese Metadaten an tatsächliches
stderr, die eindeutige fehlgeschlagene Kontroll-Evidenzphase und den
unveränderten Guard-/Summary-Abschluss; Ausgabe erst nach Cleanup.
Keine zusätzliche Query-Store-Sicht, keine Prädikat-, Last-, Zeitbudget- oder
Outcomeänderung. Der Reporter ist inzwischen lokal implementiert und
unabhängig geprüft: exakt validiertes Entfernen ergibt den ganzen bisherigen
SQL35, Quellenbindung ist erneuert, 43 Runner- und 37 Producer-/Reporter-
Methoden (ein Linux-spezifischer Windows-SKIP) sowie sieben Validatoren
bestanden. Acht tatsächliche temporäre SQL-Branchfixtures auf einer neuen
eigenen 2022-Instanz bestanden, einschließlich Ein-Tick-Abständen, gleicher
Requestgrenzen, UTC-Offset, acht Gruppen und ausdrücklichem Overflow.
Unveränderter Freeze und eigener Containerabbau sind unabhängig bestätigt.
Der ganze Report bleibt atomar innerhalb 24 Diagnosezeilen. Als nächster
Schritt wurde die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, vollständig
beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1 und 2022 BA1
scheiterten an G13. First−Start beträgt −0,4263 beziehungsweise −0,951 ms;
Last liegt jeweils innerhalb der oberen Grenze. 2025 bestand zwölf Lifecycles
und sechs Captures. Alle 32 ersten Datenbankabwesenheitsprüfungen und neun
SQL-Containerabbauten bestanden; Linux 163 Methoden PASS. Der PR bleibt
unmerged und ohne CI-Freigabe. Der Reporter schließt die Messlücke, belegt
aber keine Ursache oder Behebung. Das beobachtete Millisekundenraster ist
keine zugesagte QS-Auflösung oder Toleranz.

Die einmalige private Originalmaterialisierungsprobe auf neuer eigener 2022-
Instanz reproduzierte G13 bereits in AB1: First−Start −0,2609 ms. Die verletzte
Gruppe enthält in Captureversuch 1 und im getrennten Live-SELECT jeweils genau
eine positive Raw-Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen.
Ein Zero-Extremum erklärt diesen lokalen Fehler nicht. Elf temporäre SQL-
Fixtures PASS; sechs Präfix-Lifecycles PASS, AB1 FAIL mit sofortigem Stop,
keine AB2/BA/AA oder erfolgreiche AB-Capture. Sieben erste DB-Abwesenheits-
prüfungen, vier Gruppen-Leerheitsprüfungen und eigener Containerabbau PASS;
CID/Name unabhängig abwesend, Freeze mit 27 Dateien unverändert. Zusätzliche
Projektion/DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) sind Beobachterinstrumentierung, keine identische kanonische
Timingprüfung und kein historischer CI-Ursachenbeweis.

Der quellenbasierte [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md)
liegt jetzt als `PROPOSED` vor. Er trennt exakten zeitlichen Einschluss und
kontrollierte Kollektivzuordnung. Der ausgearbeitete Kandidat benötigt eine
belegte vollständige Familienbasis B, T0-Capture vor T1, Bilanz B→B+4→B+8
über alle Familien-/Intervallgruppen sowie vertrauenswürdig attestierten
Ausführungsumfang. Die vier Vorabrequests laufen vor der expliziten QS-
Konfiguration; frische Datenbank und beobachtete Nullcounts beweisen keine
QS-OFF-Basis oder fehlende nachlaufende Statistik. Konkrete Baseline-,
Intervallaktivierungs- und Herkunftsbelege bleiben offen. Die Vergleichbarkeit
von QS-Endzeiten und SYSUTC-Requestklammer auf exakten 100-ns-Grenzen bleibt
ungeklärt. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
prüft die vorab festgehaltenen synthetischen Gegenbeispiele und bedingte
Konsistenz; keine Prozesse im Modell, SQL-/v1-Änderung oder Runtimeattestation.
Die Prüfung ersetzt insbesondere keine tatsächliche Herkunft trotz passender
Counts. Die [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
ist abgeschlossen: Procedure-Queries unter AUTO werden erfasst; dokumentierte
asynchrone Persistenz belegt keine verzögerte Publikation. Der tatsächliche
Pfad prüft eigene Calls und Ergebnisse, attestiert aber weder vollständigen
Basisabschluss noch interne Aktivierung, kontinuierlichen Zustand oder
geschlossene Coordinatorherkunft. Der konkrete
[Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
liegt als PROPOSED vor: acht Acquisitionstages, vollständige Raw-/Gruppen-/
Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze, überprüfte
Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Observerkosten.
Bounds und deren Durchführbarkeit sind noch nicht runtimevalidiert.
Punktweise QSStates beweisen keine Kontinuität; Sättigung bleibt bedingt.
Die äußere Pipegrenze begrenzt heute nicht das Vorpuffern im Proxy.
Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: injektive kohärente
Zählung aus einem unabhängig geschlossenen tatsächlichen Calluniversum kann
Callerfassung tragen; vollständige keyweise Stageledger zusätzlich kollektive
QS-Buckets. Counts beweisen kein kontinuierliches RW/ALL; dieses gesonderte
konservative Methodengate bleibt vorgeschlagen. Heutige Live-Dateizugriffe
und Zielnamen binden keinen vollständigen unveränderlichen Ausführungspfad.
Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
implementiert die synthetischen Gegenproben mit getrennten Teilclaims.
Kein Token ist eine reale QS-Einzelidentität. Das konkrete
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
Gate-Matrix mit Acquisition-/Count- und konservativem Floatkandidaten, tatsächlicher
Freeze-/Actor-/CID-/Host-/Zugangsgrenze und Kostenplan innerhalb 145/180/60 Sekunden
und 4 CPU (Central Processing Unit; Prozessor)/8 GiB. Alle Methodengates bleiben offen; Einzelmaxima sind keine
gemeinsame Machbarkeitsevidenz. Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
ist statisch implementiert: feste 27 Mitglieder, Gitblob-/Rohbytebindung,
separate LF-Äquivalenz und deklarierte AST-Imports samt Manipulationsfixtures.
Statischer Kandidaten-PASS attestiert keine verwendeten Runtimebytes.
Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
ist statisch implementiert: Python-3.12-Ganz-AST-Profil, sechs SQL-only-Manifeste,
14 Quellenhashes und SQLCMD-Gegenproben. Import-/Launcherentwurf PROPOSED,
tatsächliche Importumgebung und verwendete Runtimebytes offen. Der getrennte
[synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
portable Budgetgegenproben und feste eigene Linux-Kindfälle; keine Integration
in die neun Runtimequellen oder reale Laufzeitmachbarkeit. Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Der erste Implementierungsteil ist das getrennte [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md): unveränderter 27-Member-Git-/Kantenvorcheck, eingefrorene neun Python-Rohbytes und begrenzte binäre Rahmung mit Kontext- und Manipulationsgegenproben. Keine Worker- oder Kandidatenimportausführung und kein UsedBytes-Claim. Die getrennte [synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md) ist implementiert: ausschließlich feste Fixturebytes, tatsächliches Compile/Exec und objektgebundene Beginn-/Abschlussreceipts. Kein DGN-Import oder Importauflösungsnachweis; DGN-Attestationsflags bleiben false. Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) ist implementiert: begrenzte aktuelle Bootstrapmetadaten und Vergleich gegen separat deklarierte Baseline. Keine Trust- oder bereits ausgeführte Bibliotheksbyteattestation; die gewählte Kontrollruntime bleibt eine ausdrücklich benannte Annahme. Der [skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) liegt als `DESIGNED` vor. Der getrennte [reine Profilvergleich](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert: 38 synthetische Tests prüfen exakte deklarierte Installation und Workerinventur, eingefrorenen Eingangs-/Ordinal-/Phasenkontext sowie gemeinsame Metadatengrenzen. Sein Match attestiert keine tatsächliche Workerbeobachtung, Herkunft oder Consumption. Die tatsächliche Prozessanbindung bleibt unimplementiert. Die getrennte lokale Record-Rückgabe des Profilvorschnitts ist jetzt implementiert: `observe_current_interpreter_records` liefert ausschließlich die tatsächlich aufgenommene und vollständig geprüfte Abschlussaufnahme, bei Ablehnung keine Records. Gehaltene Liveanker sind kein dauerhaft gültiger Zustand des Modulcaches; spätere aktuelle Runtimeverwendung braucht eine frische Aufnahme. Legacyreports, Bootstrapimports und Grenzen bleiben erhalten. Die konkrete Bootstraproute ist jetzt im [Profilbindungsentwurf §8](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt) festgelegt: geplante Scriptquelle als `__main__`, unveränderter Profilmodulname, benannte direkte Stdlibimports und Vorinitialisierung der Sysconfigwerte ohne zusätzliche Projektimports. Feldherkunft, frische Aufnahme, erneute Livekohärenz und engere Scalarformen sind getrennt beschrieben. Die getrennte importneutrale skalare Projektion ist jetzt im bestehenden Profilmodul implementiert: frische Aufnahme, vollständige private primitive Tupel, erneute Livekohärenz vor und nach Projektion sowie zusätzliche separat gewählte und gegen Factorycode/Closure geprüfte FileFinder-Hookbindung; bei Ablehnung keine Skalare. Dies attestiert keine unabhängige Factoryherkunft oder tatsächlichen Worker. Eine getrennte lokale Bootstrap-Charakterisierung unter CPython 3.12.3 erfasste 85 Modulnamen mit genau zwei Controls; dies ist keine operative Sollinventur. Der [konservative Größenbeleg](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze) zeigt bereits mindestens 16.449 Bytes für das vollständige Modularray und 21.108 bis 21.144 Bytes für die gemeinsame Metadata einschließlich Header, unverändertem Input82 und Kontext. Die heutige benannte JSON-Form ist damit für diesen vollständigen charakterisierten Namenumfang nicht darstellbar; andere Routen und Installationen sind dadurch nicht ausgeschlossen. Keine Capanhebung, Filterung oder Digestersetzung ist freigegeben. Der vollständige Linux-/Python-3.12-Import-Only-Prototyp bleibt offen; der getrennte Darstellungs- und Digestentwurf aus Profilbindungsentwurf §10 liegt als DESIGNED vor. Die separat vorgewählte vollständige Kontrollfixture und reine Größenprüfung in §11 belegen gemeinsame Metadata von 17.127/17.113/17.091 Bytes; der §10-Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap. Neuer Sizer34/34 und Legacy27/40 ohne SKIP. Der getrennte verlustfreie Stringpoolentwurf in §12 liegt als DESIGNED vor, mit eigenen lokalen Pools je Form und unveränderten Inhalten/Caps einschließlich höchstens 256 Poolwerten. Der eigene reine Pool-Sizer in §13 bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue 3×5-Rechnung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte, vollständig unabhängig nachgerechnet und rückgewonnen. Der getrennte experimentelle Formcodec in §14 bestand 41/41 isolierte Gegenproben ohne SKIP; die vollständige Originalfixture bestand alle 3×5 Frames, Feldrückgewinnung, kanonischen Repack und drei eigene Digestdomains je Ordinal. Das gesamte Fünf-Formen-Set umfasst 28.264/28.257/28.246 Bytes. Originalauswahl und Inputrahmen bleiben unverändert, keine neue Aufnahme oder Nonce. Der unabhängige Nachreview bestätigte sämtliche Frames, Feldrückgewinnung und Digests aus den unveränderten Originaleingaben ohne Codec-/Helper-Replay. Der eigene reine kombinierte Eingangsprototyp in §15 bestand 34/34 isolierte Gegenproben ohne SKIP und die neue vollständige Originalfixtureprüfung: drei Frames mit jeweils 9.389 Metadata-/Headerbytes und 130.837 unveränderten Bodybytes, insgesamt 140.226 Bytes. Tatsächliche vollständige Feld-/Rawbyterückgewinnung und Repack sowie unabhängige Stdlib-Nachrechnung ohne Replay bestanden. Alle gleichzeitig geltenden Caps bleiben erhalten; 64 KiB begrenzen ausschließlich die fünf Metadataausgaben. Die konkrete operative Bootstrap-/Kanalreihenfolge in §16 liegt als DESIGNED vor: importneutraler PRE-Vorschnitt, vollständiger Profilvergleich vor Bodyfreigabe und vollständige Eingangsprüfung vor Importfreigabe, unveränderte gemeinsame Caps und gehaltene Kontrollquellenführung. Der reine Kontrollbootstrapquellengenerator in §17 bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14; er ist keine operative Workerroute. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen. Frische operative Auswahl, inline Empfang/Reporting, tatsächliche Parent-/Worker-Anbindung, feste Quellenauflösung, tatsächliche DGN-Loaderverwendung und Importabschluss sowie begrenzte eigene Worker mit unabhängigem Cleanup bleiben getrennte Gates. Die charakterisierte Kontrollfixture ist keine operative Workerbaseline; Migration bleibt offen. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation.
Normative Methoden-/Grenzänderungen brauchen eine ausdrückliche neue Entscheidung.
Keine implizite OFF-/CLEAR-/Laständerung. Erst eine tragfähige explizite
Methodenentscheidung erlaubt gemeinsam versionierte
SQL-/Transport-/Record-/Evaluator-/Coordinator-Umsetzung. Bestehende Guards,
Fehlerklassifikation, DEC-068, Last und Budgets bleiben erhalten; keine
pauschale 1-ms-Toleranz, Abrundung oder Wiederholen bis grün. Die alternative
Methode ist weder entschieden noch implementiert oder abgenommen. Der frühere Acht-Fixture-Vorcheck enthält keine vollständige
Lifecycle-/Versionsmatrix oder Reproduktion des Main-G13.

Die interne verlustfreie Capture-Rückgabe ist lokal vorbereitet und geprüft;
Veröffentlichung und Integration sind bis zur G13-Klärung zurückgestellt.
Danach folgt der geplante API-Schnitt:
Body, tatsächlich geprüfte Phasen und erfolgreiche erste unabhängige
Datenbankabwesenheit über denselben Harness erhalten. Rückgabe erfolgt
nur nach erfolgreichem Lifecycle und Cleanup; erfolgreiche Recovery
ändert einen ersten Abwesenheitsfehler nicht in PASS. Der direkte Helper
akzeptiert ausschließlich unveränderte bekannte Kontrollverträge.
Counts-/CLI-Ausgabe und Fehlerprioritäten bleiben erhalten; keine
RunRecords, Incidentbewertung oder `runtime_attested=True`.
Danach muss der Collector-Coordinator den integrierten Freeze und Quellen,
Ressourcen, präzise Budgets und tatsächliche serielle Reihenfolge attestieren
und Cleanup unabhängig bestätigen. Die interne Capture-Rückgabe allein
ist kein vollständiger RunRecord oder Coordinator-Nachweis.
Erst danach folgen frische Bestätigungsläufe unter
der festgelegten Regel. CPU bleibt ergänzend, ohne Fallback. Keine
nachträglich ausgewählte Ratio oder statistische Signifikanzbehauptung;
fehlende tragfähige Evidenz bleibt `SKIP_EVIDENCE_MISSING`.
Plan- beziehungsweise klar unterscheidbare Runtimeprofile sind zusätzlich
gegen den Designvertrag zu begründen; Planunterschiede ersetzen kein Symptom
und isolieren keine Kompilierungsursache. Unterschiedliche Parameterlast
allein ist kein Regressionsnachweis. Als begrenzte Voraussetzung verwendet der
ältere Teilnehmerpfad jetzt `sys.databases.compatibility_level` mit NULL-Guard
und prüft vor der Evidenzausgabe den bestehenden 2025-/170-Vertrag; auch die
Adaptervalidierung lehnt fehlende Compatibility-Werte ab. Die
Beobachtungsbedingung muss weiterhin auf den Designvertrag (Plan- oder
Laufzeitprofilevidenz) abgeglichen werden. Der Compatibility-Vorfix belegt
weder den Incident noch eine vollständige Teilnehmerabnahme.
Für die ältere Beobachtungsbedingung sind ausschließlich erfolgreich
ausgeführte T0/T1-Pläne und ihre validierten Profile maßgeblich; historische
oder ungenutzte Planzeilen und bloße Counts 3/5 genügen nicht. Ihr bisheriger
unterschiedlicher Lastmix ist zuerst gegen den gleichen Parameterlastvertrag
abzugleichen. Live-Mittelwerte dürfen keine nachträglichen Zusatzrequests
enthalten; Plan-/Profilunterscheidbarkeit und Verschlechterung sind getrennt
zu begründen. Die jetzt gemessenen unterschiedlichen Richtungen für CPU und
Reads erfüllen allein keine Incidentfreigabe.
Danach folgen die vollständige Capstone-Matrix und die
interaktive Docker-/Podman-Abnahme; deren offene Gates bleiben bestehen.

Der Capstone-Planungsschnitt ist mit `TSK-002` entschieden
(`DECIDED_PLANNING`, Detailreview
[LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md)).
Implementierungsschnitt A (Project Adapter `0.1` mit Datenaufbau,
Query-Store-Zeitfenstern und Incident-Erzeugung ohne Mitigationsmarker) besitzt
seit dem 2026-09-14 die praktische Docker-/Podman-Lifecycle-Abnahme: Docker-Run
`9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run
`e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`,
Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die
verbleibende Gesamtabnahme umfasst den vollständigen Lifecycle dieser
Schnitt-B-Fassung und die begrenzte Provider-/Versionsmatrix. Der manuelle Teilnehmerablauf sowie
die Evidenz-, Hypothesen- und Mitigationsartefakte sind statisch geprüft.
Frische SQL-Server-2025/Linux-Runs bestanden am 2026-09-19 auf Docker
(`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman
(`fba84720-5f0b-4537-bc98-75bbad37a85b`) Adapter-Install/Validate, alle sechs
Demo-Stufen, Teilnehmer- und Adapter-Cleanup sowie Lab-Remove. Das belegt die
aktuelle Linux-Providerparität, ist aber keine Szenariopromotion und keine
vollständige Lifecycle-/Versionsmatrix. Ressourcen-, Netzwerk-, Hyper-V- und
gemischte Topologien bleiben ohne konkreten fachlichen Bedarf gestoppt.
