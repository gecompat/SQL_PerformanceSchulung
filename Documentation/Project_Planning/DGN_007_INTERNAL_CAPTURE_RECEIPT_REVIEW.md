# DGN-007 – interne Capture-Rückgabe nach DEC-072

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-20 |
| geprüfte Basis | `52351588632c3ad7bbc33cd46cbc5e0d959fe354` |
| erhaltener Entwurf | `codex/dgn007-internal-capture-receipt`, `83f08fb71446445e70fb6227e442ed7109637de6` |
| Umfang | interne Body-/Phasenrückgabe; bestehender DGN-007-Backlogpunkt |
| Integrationsentscheidung | fünf brauchbare Entwurfsänderungen auf aktueller Basis übernehmen und gegen v2 prüfen; kein unveränderter Branchmerge |
| aktueller Abschluss | [PR255](https://github.com/gecompat/SQL_PerformanceSchulung/pull/255) integriert; Main `b3f023ad66f8c4aa16a7c6fe73e42615818cbd90`; beide lokalen Capture-Branches und eigener Remote-Branch bereinigt |

Der Benutzerauftrag vom 20. Oktober 2026 nimmt die allgemeine Entwicklung nach
Bestandsprüfung ausdrücklich wieder auf. Zu Beginn waren Main und origin/main
synchron und sauber, kein PR offen und nur der alte lokale Capture-Branch neben
Main vorhanden. Ein anderer Chat bearbeitete dieses Repository nicht aktiv.
Die pausierten Scheduler werden durch diesen Auftrag nicht aktiviert. Laufende
Lab-CI und fremde Ressourcen bleiben unberührt.

## Quellenabgleich und Entscheidung

Der Entwurf ist weder ancestral noch patchäquivalent in Main integriert. Seine
fünf Zieldateien haben sich seit dem Entwurf weiterentwickelt. Die Übernahme
erfolgt deshalb auf einem neuen Branch vom aktuellen Main; spätere Diagnostik,
Grenzen und Decoderänderungen werden erhalten. Der alte Branch bleibt bis zur
unabhängig bestätigten vollständigen Übernahme seiner Änderungen erhalten.

[DEC-072](../../.ai/DECISIONS.md) und der Merge von
[PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132) bei
`113648c4884fe788797c5f0c3788a54f74ecfc9c` haben die frühere G13-/Zeitquellensperre
für den begrenzten kontrollierten Schulungslauf abgelöst. Die älteren Aussagen
im [G13-Review](DGN_007_G13_PR_REVIEW.md) und
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) bleiben als
historische Befunde erhalten; ihre offene größere Provenienzarchitektur ist
keine zusätzliche Voraussetzung für diese interne Rückgabe.

Maßgeblich sind der aktuelle
[prospektive v2-Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md),
sein VertragsJSON, der [Capture-Transport](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md),
der tatsächliche Decoder und der aktuelle Runner. Der Decoder bewahrt
Originalzeiten einschließlich diagnostischer QS↔SYSUTC-Abweichungen. Counts,
Intervalle, Requests, Ergebnisse, Familien, Planmengen und vollständige
Zeilenevidenz bleiben verpflichtend. Historische FAILs werden nicht umgedeutet.

## Rückgabe und Fehlergrenze

`_check_capture_body` decodiert einmal und liefert den vollständigen
unveränderlichen Body sowie die tatsächlich geprüften Harness-Phasenstatus.
Die bestehende Counts-API verwendet dieselbe Prüfung. `_run_one` führt den
gemeinsamen Lifecycle einschließlich unveränderter Fehlerprioritäten aus.
`run_one` behält die öffentliche `RunResult`-Rückgabe und CLI-Ausgabe.

`_run_capture_one` ist eine interne API für die unveränderten AB-/BA-/AA-Verträge.
Ihr `_CaptureReceipt` entsteht ausschließlich nach vollständiger Bodyprüfung,
erfolgreichen Harnessphasen einschließlich Cleanup und der ersten erfolgreichen
unabhängigen Datenbankabwesenheitsprüfung. Fehlende Phasen, Decoderfehler,
Timeout, Ergebnisfehler, Cleanupfehler oder eine fehlgeschlagene erste Absenz
verhindern die Rückgabe. Eine erfolgreiche Recovery hebt den Fehler nicht auf.
Ungültige direkte API-Eingaben werden vor Zieloperationen zurückgewiesen.

Der Body wird weder in `repr` noch in CLI-Ausgabe oder Dateien veröffentlicht.
Die bisherige Capture-Countszeile vor der Absenz bleibt ein Teilergebnis;
maßgeblich für den Lifecycle sind nachfolgender Cleanup- und Stage-Status.
Der Body behält `runtime_attested=False` und `PROJECT_SEMANTIC`. Der interne
Beleg bestätigt keine Ressourcen, Budgets, Vorabfreeze, vollständige Herkunft,
Lifecycle-Reihenfolge oder Incidentbewertung und erzeugt keine `RunRecord`s.

Nur die Runner-AST-Bindung des bestehenden CPython-3.12-Kantenprofils wird
nach dem Quellenreview erneuert; die acht anderen ASTs und der SQL-Vertrag
bleiben unverändert. Eine erneuerte statische Bindung ist keine Runtimeattestation.

## Wellenumfang und Prüfungen

Ein Implementierungsowner, höchstens drei Kandidatenstände mit Checkpoint nach
dem zweiten, ein unabhängiger Quellenreview mit gezielter Befundnachprüfung.
Ein unveränderter fehlgeschlagener Kandidat wird nicht erneut ausgeführt.
Die Grenze umfasst Korrekturen, Review und Koordination; verlässliche
Modellverbrauchsmessung ist nicht verfügbar. Bisherige ausgeschöpfte
Import-/Generations-/Providerwellen erhalten hierdurch keine neuen Versuche.

Die ersten 47 Runner- und 37 Projektionsmethoden bestanden unter Windows mit
einem ausdrücklich Linux betreffenden SKIP. Beide betroffenen Validatoren
bestanden. Das ist der Ausgangstest des übertragenen Entwurfs, keine finale
Qualifikation. Zusätzliche v2-Gegenproben prüfen alle neun Major-/Kontrollpaare
mit unveränderten diagnostischen Zeiten sowie Ergebnis-, Count- und
Intervallfehler trotz erfolgreicher Absenz. Der vollständige betroffene Lauf
aus sieben Suites bestand anschließend unter Linux/CPython 3.12 mit 172/172
Methoden ohne SKIP; alle sieben DGN-007-Validatoren bestanden. Die tatsächlichen
Working-Tree-Bytes bestanden das CPython-3.12-Kantenprofil mit neun ASTs und
allen Manifest-/Policyprüfungen. Registry v2 mit 266 Artefakten,
Kennungsregistrierung, Repositorykontinuität und `git diff --check` bestanden.
Alle 14 geänderten Dateien bestanden die Privacy-Prüfung. Der lokale Vollscan
brach an einer ungültigen URL ab; daraus wird kein Privacy-PASS abgeleitet.
Der frische CI-Checkout bleibt für den vollständigen Scan maßgeblich.
Die Prüfung des gesamten versionierbaren Bestands bestand anschließend für
1205 Dateien. Die vollständige
[Privacy-CI](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39339866436)
und die [commitgebundenen Offline-Gegenproben](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39339866471)
bestanden am aktuellen PR-Head.

Der ausdrücklich autorisierte unabhängige lesende Quellenreview bestätigte
Basis `5235158…` → Head `e43111d083162a5b10ca5cc7e99653ca48e313bb` ohne offene
P1/P2/P3-Befunde. Alle 18 hinzugefügten/geänderten AST-Knoten der fünf alten
Entwurfsdateien und erforderliche Imports sind unverändert übernommen;
spätere Diagnosepfade bleiben erhalten. Alle neun AST-Digests wurden unter
CPython 3.12 unabhängig nachgerechnet; acht Pythonquellen, SQL, Manifeste und
Akzeptanzvertrag sind gegenüber der Basis identisch.

Alle 14 PR-Gates einschließlich
[SQL2019/2022/2025](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39339866415)
bestanden: je zwei Lifecycles aller sechs Scopes, unabhängige DB-Prüfung und
eigener erfolgreicher Container-/Volumecleanup. Die Compatibility-Gegenprobe
gilt nur für 2025 und bestand dort; die vorgesehenen 2019-/2022-SKIPs sind
keine zusätzliche Versionsqualifikation.

Der serverseitige Squash-Merge ist bestätigt. Vollständiger Treevergleich
`e43111d…` gegen `b3f023ad…`, Main-FF und saubere Synchronität bestanden.
Vor der Entfernung wurden beide exakten Branchstände und der einzige eigene
Worktree erneut geprüft. Der Altbranch enthielt genau einen zusätzlichen
Commit; seine vollständige Übernahme ist unabhängig bestätigt. Beide lokalen
Capture-Branches und `origin/codex/dgn007-capture-receipt-v2` sind entfernt.
Der automatisch gestartete
[Main-Lauf](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39387949894)
bleibt eigener aktueller Nachweis; sein endgültiges Ergebnis ist noch offen.

Die bestehende DGN-007-CI führt für den betroffenen Runner die 2019-/2022-/2025-
Matrix mit je zwei Lifecycles der sechs vorhandenen Scopes, unabhängigen
Datenbankprüfungen und eigenem Containercleanup aus. Kein zusätzlicher lokaler
SQL-Lauf und keine Änderung ihrer Oracles oder Budgets sind vorgesehen.
Erforderliche Registry-, Governance- und Privacy-Gates bleiben erhalten.

## Anschließender Scope

Nach Integration und sicherer Branchbereinigung ist ausschließlich der separate
[SESSION_END-Entwurf §34](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild)
zu Loaderrecordvertrag §33 aufgenommen: ein Owner, höchstens zwei
Entwurfsstände und ein unabhängiger Designreview. Frühere ausgeschöpfte
Runtime-/Quellwellen erhalten keine neuen Versuche. Collector, operative
Workerfreigabe und frische prospektive Bestätigungsläufe bleiben eigene
Aufgaben mit ihren offenen Gates.
