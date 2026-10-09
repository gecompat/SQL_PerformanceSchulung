# Foundation 1.21.0 – Upgrade und tatsächlicher Testaufwand

Stand: 2026-10-09. Geltungsbereich: Foundation-Integration und projektweite
Testauswahl. Keine DGN-007-Reporter- oder Incidentfreigabe.

## Quelle, Delta und Semantik

`origin/main` von `gecompat/AI_Repository_Foundation` wurde einmal auf
`d720db4f2f0d043756a958d5195d0e62090b1c8f` aufgelöst und als Quelle
gepinnt. Das Manifest dieses Commits bestimmt `1.21.0` und hat den portablen
SHA-256 `5c4268140ba8cb6c3c38ce42cdd1ebecd8d5c3db23309bb90c77bc8b38ebf2f6`.
Der Feature-Katalog ergibt gegenüber der installierten `1.20.0` genau sieben
Kandidaten (ein neues, sechs materiell geänderte Features). Jeder Kandidat ist
im [Assessment](FOUNDATION_UPGRADE_1_21_0_ASSESSMENT.json) klassifiziert.

Die Manifest-Whitelist erhält 107 ausgewählte Dateien, zehn Capabilities und
drei Discovery-Adapter. Zehn Foundation-Ziele haben neue Inhalte; ihre Quellen
wurden vor der Übernahme gegen die Hashes des gepinnten Manifests geprüft.
`AGENTS.md` erhält die projektgeführte Discovery-Sektion als begründeten
`INTENTIONAL_OVERRIDE`; die übrigen ausgewählten Ziele bleiben Foundation-
Baseline. Die aktualisierte Provenienz enthält weder Hostpfade noch Promptdaten.
Historische Kennungen, die zentrale Registry und die Methodenentscheidung
bleiben Projektsteuerung; `DEC-071` registriert ausschließlich diese neue
Upgrade- und Testauswahlentscheidung.

## Aufwandassessment nach tatsächlichem Ausführungspfad

| Bereich | Vorheriger Auslöser/Aufwand | Korrektur oder begründete Grenze |
|---|---|---|
| Regeln und Adapter | `DEC-070` hatte die breite Pflichtlektüre bereits entfernt; drei Adapter führen nur zu `AGENTS.md`. | Scope-Router und geprüfte Sessionwiederverwendung bleiben. Native Discovery und relevante Quellprüfung sind die geschützte Grenze. |
| Vollständiger Datenschutzscan | 23 von 36 Workflows enthielten den Scanner; bis zu 22 fachliche Workflows wiederholten ihn zusätzlich zum zentralen PR-/Main-Workflow, wenn ihre Pfade betroffen waren. | Nur `privacy-metadata.yml` führt den vollständigen Repositoryscan pro PR/Main-Push aus. Der Commitautor prüft weiter alle geänderten Dateien, einschließlich nichttextueller Artefakte. |
| Scanner-Selbsttest | Im zentralen Workflow bei jedem PR/Main-Push. | Eigener pfadbegrenzter Workflow für Scanner, Selbsttest und Workflowdefinition; der zentrale Lauf prüft weiterhin aktuelle Repositoryeingaben. |
| SQL-Matrizen | Elf Runtime-Workflows wurden auch durch reine statische oder Workflow-Verwaltungsänderungen ausgelöst. DGN-007 umfasst bei tatsächlicher Qualifikation sechs Scopes, zweimal je Version 2019/2022/2025, also 36 Lifecycles. | Ein revisionsgebundener Selektor prüft alte und neue Pfade sowie den tatsächlichen Runtime-Job. Statische Änderungen behalten ihre statischen Jobs und beanspruchen keine neue Runtime-Qualifikation. Geänderte SQL-/Runner-/gemeinsame Runtime-Eingaben, manuelle Qualifikation und unbekannte Revisionen führen weiterhin zur Matrix. |
| Zu breite Pfadfilter | `framework-sql-matrix` reagierte auf ganz `Tests/Runtime/**`; DGN-003/005 auf ganz `Demos/07_Query_Store_Extended_Events/**`; `w-cov-001` nach Main-Push auf `Demos/**`; `framework-contracts` auf alle statischen Tests. | Pfade sind auf tatsächliche Verbraucher und gemeinsame Abhängigkeiten eingegrenzt. Alte und neue Filter werden beim Integrationsdiff gemeinsam betrachtet, damit entfernte Pfade nicht stillschweigend übergangen werden. |
| Ausführungsstatus | Zwei Validatoren liefen bei jeder Änderung von `CURRENT_EXECUTION_STATUS.md`, obwohl sie diese Datei nicht lesen; der VP3–VP5-Validator liest sie tatsächlich. | Die beiden falschen Trigger sind entfernt; die echte Statusabhängigkeit bleibt. |
| Logs und Modelle | SQL-CI bewahrt bei Bedarf vollständige Laufdiagnosen; pauschale Modelllektüre oder neue Reviewketten sind weder für Routine noch für unveränderte Fehler vorgeschrieben. | Zuerst kleine redigierte Fundstellen und Phasenstatus deterministisch auswerten, Originalrun verlinkt erhalten. Der dreitägige Framework-Diagnoseartefakt bleibt wegen nachträglicher SQL-Fehleranalyse; ein Voll-Log kommt nur bei konkreter offener Frage in den Modellkontext. Ein Implementierungsverantwortlicher; zusätzliche Reviews nur für eigenes Risiko und Abnahmekriterium. |
| Wiederholungen und Wartezustand | DGN-007-Qualifikation schreibt zwei Lifecycles je Scope/Version vor; SQL-Container dürfen wegen nicht nachgewiesenem Cleanup nach hartem Abbruch nicht automatisch beendet werden. Die allgemeine Entwicklungsautomation ist pausiert. | Wiederholungen bleiben ausschließlich beim finalen fachlichen Claim erforderlich. Diagnose kann kleiner sein und erhält keinen `VALIDATED`-Status. Laufende mutierende CI-Runs werden zum sicheren Cleanup erhalten; unveränderte Blocker lösen keine neuen Versuche oder Modellreviews aus. |

Die strukturellen Zählungen sind keine behauptete CI-Minuten- oder
Tokenersparnis. Ein vollständiger lokaler Scan des aktuellen Arbeitsbaums
dauerte 2,229 s (Python `perf_counter`, 961 Dateien, PASS); einzelne CI-Jobs
haben andere Start- und Laufzeitkosten. Die 22 Fachworkflows starten nicht
bei jedem PR gleichzeitig, sodass `22 × 2,229 s` keine beobachtete Ersparnis
ist. Der vorherige G13-Review belegt einen vollständigen grünen Lauf
mit 36 Lifecycles sowie spätere echte Fehler; sie werden nicht durch einen
Selektor umgedeutet. Die lokalen Selektortests prüfen positive, negative,
gemeinsame und unbekannte Eingaben. CI muss die aktuellen statischen und
Pflichtchecks am finalen PR-Head/Base erst noch bestätigen.

## Erhaltene strengere Projektgrenzen

Die beiden erforderlichen Checks `registry-integrity` und
`repository-governance` laufen weiterhin auf jedem PR. Sie prüfen teils dieselbe
Registry aus unterschiedlichem Zweck: Head-Semantik einerseits und
Cross-PR-/Drei-Wege-Merge andererseits. Ihre getrennten Status sind durch das
aktive Ruleset gebunden; ein Überspringen wäre keine zulässige Optimierung.
Auch der zentrale Datenschutzscan über den gesamten veröffentlichten Baum ist
wegen möglicher Alt- oder Binärartefakte strenger als ein reiner Diff-Scan.
Current-Head-/Integrationsbindung, SQL-Versionen, exakte G13- und Count-Oracles,
unabhängiger Cleanup und erforderliche Methodenentscheide bleiben erhalten.
Ein früherer PASS ersetzt einen aktuellen fachlichen Fehler nicht.

Die doppelte Ausführung eines relevanten statischen Checks auf PR und Main ist
durch verschiedene Git-Integrationsstände gebunden. Eine Wiederverwendung
bedarf einer nachgewiesenen Äquivalenz von Eingaben, Umgebung und Frische;
allein gleiche Produktdateien genügen nicht. Kein CI-Gate wird durch einen
übersprungenen Runtime-Job als bestanden ausgewiesen.
