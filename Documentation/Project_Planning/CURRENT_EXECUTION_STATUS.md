# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-10-07 |
| geprüfter Repository-Basisstand | `25c9801e458ba124a8d4afc9e48655dc15fcbf51` auf `origin/main` (Pull Request 87); Codebasis `da7b0eb…` aus Pull Request 65 |
| geprüfter Runtime-Stand | `782799e` aus Pull Request 42; `OPT-017`-Matrix vollständig grün |
| Fachliche Hauptwelle | `ADV-008` und `W-COV-001` vollständig runtimevalidiert |
| Abgeschlossene Folgepakete | `W2-002`, `ADV-009`, `ADV-010`, `LABSCN-002`, `LABSCN-004`, `INF-002`, `INF-003`, `LABINT-003` und der `CON-006`-bezogene `LABINT-004`-Schnitt `VALIDATED` |
| Szenariowelle | `CON-004`, `DGN-005` und `CON-006` – Project Adapter `0.1` und vollständiger Docker-/Podman-Lifecycle auf SQL Server 2025 validiert |
| Folgeplanung | [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md) |
| Zweck | kanonischer operativer Einstiegspunkt für Nachweisstand, offene Gates und nächste Schnitte |

## 1. Verifizierter Repository-Stand

Der Repository-Basisstand war zu Beginn der Verarbeitung sauber. Für den korrigierten `OPT-017`-Stand liefen die betroffenen statischen Validatoren, Runner-Selbsttests, `git diff --check` und der Privacy-Scan erfolgreich; letzterer meldete `PASS (files=632; text=621; office=1; archives=0; approved_immutable=1)`.

Die bestehenden CI-Nachweise stammen aus den verlinkten GitHub-Actions-Läufen; ergänzende lokale Nachweise sind in der Tabelle ausdrücklich gekennzeichnet. Die Läufe 33222989681, 33222989682 und 33222989644 prüfen den in `origin/main` enthaltenen Commit `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7`. Pull Request 42 prüft `OPT-017` auf dem unveränderlichen Head `782799e`.

## 2. Runtime-Nachweisstand der produktiven Demos

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` | Plan- und Statistikevidenz, zwei vollständige Läufe auf SQL Server 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und Performance Spool, zwei vollständige Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `QRY-013` | [Actions-Lauf 30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795): zwei Docker-basierte Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-009` | [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564): 2022/2025 erfolgreich, 2019 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-010` | [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969): 2025 erfolgreich, 2019/2022 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-013` | Gate-B-Nachweis | `VALIDATED` |
| `QRY-001` | Framework- und Lab-Nachweis | `VALIDATED` |
| `OPT-002` | Framework- und Lab-Nachweis | `VALIDATED` |
| `CON-004` | fachliche Demo und Szenariokandidat | `VALIDATED` |
| `QRY-004` | [Actions-Lauf 33222989681](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989681): je zwei vollständige Läufe auf 2019/2022/2025; erwartete `WARN_EMPIRICAL_VARIANCE` ohne Vertrags- oder Cleanup-Fehler | `VALIDATED` |
| `DGN-003`, `DGN-005` | [Actions-Lauf 33222989682](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989682): je zwei `PASS/OK` auf 2019/2022/2025 | `VALIDATED` |
| `OPT-017` | [Actions-Lauf 33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232): je zwei `PASS/OK` auf 2019/2022/2025 mit Actual DOP, Exchange, positiver Threadarbeit, serieller Gegenprobe und Cleanup | `VALIDATED` |
| `OPT-003`, `OPT-005` | Statistik-Sampling/Skew sowie Ascending-Key-/Pflegevertrag; je zwei lokale Docker-Läufe auf 2019/2022/2025 mit `PASS` | `VALIDATED` |
| `CON-006` | Deadlock-Zyklus, Fehler 1205, Graph und geordnete Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `CON-009` | [Actions-Lauf 33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644): TempDB-Kostenklassen auf 2019/2022/2025 jeweils zweimal `PASS/OK` | `VALIDATED` |
| `IDX-006`, `IDX-010` | Rowstore-Messkette je zweimal mit fachlich akzeptierter Warnung; klassische Columnstore-Segmente je zweimal `PASS` auf allen Zielversionen | `VALIDATED` |
| `STL-008`, `STL-009` | rote VLF-/Growth-Lane und gelber Commit-/WRITELOG-Schnitt; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `RES-007` | Task-, Request- und Instanz-Waitscope mit Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `QRY-006` | Lokaler Docker-Nachweis: SQL Server 2019/150, 2022/160 und 2025/170, je zwei vollständige Manifestläufe `PASS`; siehe [QRY_006_RUNTIME_EVIDENCE.md](QRY_006_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – Runtime-Gate und SQL_Server_Lab-Szenariopromotion bleiben offen |
| `DGN-007_DATA_MODEL` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Datenmodell-Lifecycles `PASS/OK`, unabhängiger Datenbankabbau nach jedem Lauf und Entfernung aller eigenen Container; siehe [DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzter Datenmodellvertrag; vollständige Capstone-Abnahme und Szenariopromotion bleiben offen |
| `DGN-007_QUERY_STORE_WINDOWS` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Fenster-Lifecycles `PASS/OK`; disjunkte Katalogintervalle, gleiche vier Parameterklassen und je vier erfasste Suchausführungen, unabhängiger Datenbankabbau und Entfernung aller eigenen Container; siehe [DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzte Capture-Evidenz; kein Incident-, Regressions- oder Capstone-Nachweis |

`QRY-004` bleibt fachlich bewusst warnungsfähig. `WARN_EMPIRICAL_VARIANCE` behauptet keinen nicht gemessenen Performancevorteil und verhindert die Runtimefreigabe nicht, sofern die Matrix vollständig läuft und Ergebnis-, Sicherheits-, Wiederverwendungs- und Cleanup-Verträge erfüllt sind. Genau diesen Zustand belegt Lauf 33222989681.

## 3. Lab-Integration und Szenarien

`LABSCN-001` und `DEC-044` bleiben verbindlich:

- `SQL_Server_Lab` provisioniert die technische Umgebung; dieses Repository beschreibt Lernziel, Setup, synthetische Daten, Benutzeraktionen, Beobachtungen und Reset.
- Ein interaktives Szenario endet nach der Vorbereitung in `READY_FOR_USER`; Reset und Entfernen sind getrennte, bewusste Benutzeraktionen.
- Die automatisierte Matrix ist ein Qualitätssicherungsinstrument und kein Ersatz für den Benutzerworkflow.
- Änderungen an `SQL_Server_Lab` benötigen eine konkret nachgewiesene fehlende Fähigkeit und ausdrückliche Freigabe.

`LABSCN-002` inventarisiert alle 22 produktiven Demos vollständig und wird
gegen den aktiven Demo-Katalog validiert. `LABSCN-003` setzt `CON-004` als
ersten vollständigen Vertical Slice um; `LABSCN-005` ergänzt `DGN-005` und
`CON-006` als zweiten und dritten freigegebenen Slice. Alle drei versionierten
Project Adapter `0.1` begrenzen ihren interaktiven Pfad auf SQL Server 2025 Linux in einer isolierten
Docker- oder Podman-Wegwerfumgebung und besitzen getrennte Preflight-, Install-,
Validate- und Cleanup-Entrypoints.

```text
Auswahl -> Provisionierung -> fachliche Vorbereitung -> READY_FOR_USER
        -> interaktive Durchführung -> Reset -> Remove
```

Die lokalen Nachweise vom 2026-08-30 bestätigten denselben vollständigen
Lifecycle auf Docker (RunId `30b69f0b-b140-47e6-8c90-c05e38bd7c99`) und Podman
(RunId `f80f7d82-934b-4c7c-9d2a-a80e975d92d5`): Start und Reset endeten
jeweils als `READY_FOR_USER`; der anschließende markergebundene Datenbank-,
Container- und Volume-Abbau einschließlich Abschluss des aktiven
Szenario-States endete als `REMOVED`. Der Lab-Core behält ausschließlich den
nicht aktiven Auditdatensatz des entfernten Runs. Der Podman-Cleanup ließ eine
bereits vorhandene, nicht zum Run gehörende Ressource unverändert gesund.

Der `DGN-005`-Folgeslice bestand am 2026-09-01 denselben Lifecycle auf Docker
(RunId `d5143f2a-9f18-49fa-8e9f-b91604993252`) und Podman (RunId
`82791985-b76a-4594-a5be-bab014907f7d`). Beide Provider führten Demonstration,
Observation, Mitigation und Comparison mit `PASS/OK` aus und erreichten nach
dem Reset erneut `READY_FOR_USER`; die markergefilterte, speicherbegrenzte
Extended-Events-Session sowie Datenbank, Container und Volume wurden danach
vollständig entfernt.

Der `CON-006`-Folgeslice bestand am 2026-09-01 den vollständigen Lifecycle auf
Docker (RunId `76cff6ed-a714-44e6-beda-6b916600cb98`) und Podman (RunId
`6d2d0a51-1915-4e65-a380-baec715fc676`). Beide Provider belegten genau ein
Opfer mit Fehler 1205, genau einen Survivor, einen Deadlock-Graph sowie zwei
erfolgreiche Akteure in der geordneten Gegenprobe. Start und Reset endeten als
`READY_FOR_USER`; Cleanup und Infrastrukturabbau endeten als `REMOVED`. Der
Podman-Lauf nutzte wegen einer fremden aktiven Altressource ein isoliertes
Ausweichnetz und ließ die fremde Ressource unverändert.

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `VALIDATED`; alle freigegebenen `ADV-008`- und `W-COV-001`-Demos besitzen den zutreffenden Matrixnachweis.
- Gate V4 – Lehrmittelfreigabe: `VALIDATED`; Masterdeck und Profile bestanden Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy- und Branding-Abnahme.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: `VALIDATED`; 22 von 22 produktiven Demos besitzen den vollständigen Inventarvertrag.
- `LABSCN-003`: `VALIDATED` für den vollständigen SQL-Server-2025-Lifecycle auf Docker und Podman.
- `LABSCN-004`: `VALIDATED`; Auswahl, Start, Übergabe, Reset und Remove sind standardisiert dokumentiert und statisch abgesichert.
- `LABSCN-005/DGN-005`: `VALIDATED` als zweiter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABSCN-005/CON-006`: `VALIDATED` als dritter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABSCN-005/DGN-007`: `IMPLEMENTED_STATIC_SLICE_B` mit praktischer Adapter-Lifecycle-Abnahme vom 2026-09-14: Docker-Run `9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run `e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`, Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die aktuelle Fassung bestand am 2026-09-19 zusätzlich vollständig auf frischen SQL-Server-2025/Linux-Runs: Docker (`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman (`fba84720-5f0b-4537-bc98-75bbad37a85b`). Jeweils endeten Adapter-Install/Validate, Preflight, Baseline, Evidenz, reversible Mitigation, Vergleich, Teilnehmer-Cleanup, Adapter-Cleanup und Lab-Remove mit `PASS` beziehungsweise `REMOVED`. Als kontrollierter Negativtest des 2025-only-Vertrags liefen auf Docker außerdem SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und SQL Server 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`): kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, tatsächlicher Lab-Core-Status `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und abschließend `REMOVED`. Diese Läufe belegen ausdrücklich keine fachliche Unterstützung von 2019/2022 und keine Promotion; sie bestätigen nur den kontrollierten Skip-/Cleanup-Pfad. Die positive Evidenz belegt die aktuelle Linux-Providerparität, aber weder eine vollständige Lifecycle-Matrix noch eine Szenariopromotion. Teilnehmerorchestrierung als interaktives Szenario und `scenario.json` bleiben offen.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.
- `LABINT-002`: `VALIDATED` für Start, `READY_FOR_USER`, Reset und Remove von `CON-004` auf Docker.
- `LABINT-003`: `VALIDATED` für die freigegebenen Slices `QRY-001`, `CON-004` und `DGN-005`; Docker-/Podman-Parität ist praktisch belegt.
- `LABINT-004`: `VALIDATED` für die vollständige freigegebene SQL-Server-2025-/Docker-/Podman-Matrix des gelben `CON-006`-Slices einschließlich fachlicher Gegenprobe und Cleanup.
- `INF-002`/`INF-003`: `VALIDATED`; beide Provider-Preflights melden `RESOURCE_OK`, Quickstart und Recovery sind dokumentiert.

`ADV-006` und `ADV-007` bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. `DGN-007` Capstone-Planungsschnitt ist mit `TSK-002` entschieden
   (`DECIDED_PLANNING`, Stand 2026-09-14); der Detailreviewvertrag steht in
   [LABSCN_005_DGN_007_DETAIL_REVIEW.md](LABSCN_005_DGN_007_DETAIL_REVIEW.md).
2. Implementierungsschnitt A ist umgesetzt und adapterseitig abgenommen:
   Project Adapter `0.1` mit Datenaufbau, Query-Store-Zeitfenstern und
   Incident-Erzeugung ohne Mitigationsmarker; die Docker-/Podman-Lifecycle-Abnahme
   bestand am 2026-09-14 mit RunId `9ac100f8-…` (Docker) und `e06e9ec9-…`
   (Podman) jeweils über Start, Reset und Remove bis `REMOVED`.
3. Implementierungsschnitt B besitzt einen nicht-promotenden statischen
   Teilnehmerablauf und ist auf frischen SQL-Server-2025/Linux-Läufen mit Docker
   und Podman praktisch belegt. Der Ablauf endet nach Cleanup mit
   `REMOVED`; er erzeugt keine interaktive `READY_FOR_USER`-Übergabe. Offen
   bleiben die vollständige Lifecycle-/Versionsmatrix sowie die für eine
   Promotion erforderlichen `scenario.json`-, Manifest- und Inventareinträge.
   Der getrennte Datenmodellvertrag ist am 2026-10-06 auf Docker für alle drei
   Zielversionen je zweimal praktisch belegt. Der getrennte Query-Store-
   Fenstervertrag bestand anschließend ebenfalls je zweimal auf allen drei
   Versionen. Der neutrale `DGN-007_PROFILE_COMPARISON`-Vertrag bestand am
   2026-10-07 ebenfalls je zweimal auf allen drei Versionen. Die vollständige
   Reihenfolge ergab 18 erfolgreiche lokale Lifecycles, vier zusätzliche
   Ausgabekontrollen bestanden auf 2019/2022. Datenbankabwesenheit je Lauf und
   Abbau aller fünf eigenen Container wurden unabhängig bestätigt. Der
   [Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md) dokumentiert
   gewichtete CPU-/Duration-/Reads-/Rows-Metriken ohne Incidentpromotion.
   Die anschließend getrennten neutralen AB-/BA-/AA-Kontrollcaptures bestanden
   am 2026-10-07 auf allen drei Versionen je zweimal. Die vollständige neue
   Reihenfolge ergab 36 erfolgreiche lokale Lifecycles und unabhängigen Abbau
   aller drei eigenen Container. Der
   [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md) dokumentiert
   tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Metrikvariation.
   Auf 2019 überlappt eine AA-Schwankung einen BA-Duration-Kontrast.
   Der getrennte [prospektive Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
   liegt jetzt als `STATIC_PROSPECTIVE_CONTRACT` vor (`DEC-068`): reine
   Recordprüfung, gerichtete Duration-Separation gegenüber AA und globaler
   Planfingerprint- oder Reads-Zweig. 34 synthetische Tests und der Validator
   für 14 gebundene SQL-/Manifestquellen bestanden lokal. Das ist ausschließlich
   `PROJECT_SEMANTIC`, keine SQL-Runtime-Abnahme. Der getrennte
   [skalare Collector-Transport](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
   ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: reiner begrenzter
   JSON-Decoder, genaue Decimal-/100-ns-Übertragung und gebundene Records.
   19 Transporttests und beide Validatoren bestanden lokal, ebenso die
   34 Prospektivtests. Fehlende Ergebniszeilen je Request bleiben ausdrücklich
   `NOT_CAPTURED`/`None`; auch `MEASURED` ist nur eine Eingabedeklaration.
   Dieser reine Decoder bildet keinen vollständigen RunRecord. Der getrennte
   [SQL-Producer](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/SQL_CAPTURE_PRODUCER.md)
   erfasst jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
   die vollständige skalare Projektion vor Cleanup bereit. Die neue lokale
   Matrix bestand am 2026-10-07 auf 2019/150, 2022/160 und 2025/170 je zweimal
   AB/BA/AA: insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder
   und unabhängiger Datenbankabwesenheit. Alle drei eigenen Container sind
   unabhängig abwesend bestätigt. Quellenfreeze, genaue Versions-/Imagebindung
   und getrennte frühere Fehlversuche stehen im
   [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
   156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und einen ausdrücklich
   Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
   [Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
   ist abgeschlossen: Head `20a867e…` gegen Base `94ed561b…`, geprüfter
   Integrationscommit `df78cb0…`, 14 Workflows und alle 22 Jobs SUCCESS.
   Linux führte alle 156 Methoden ohne SKIP aus. Je Version bestanden zwölf
   Lifecycles, sechs Decoder-Captures und zwölf unabhängige Datenbank-
   abwesenheitsprüfungen; die drei DGN-007-CIDs sind explizit abwesend bestätigt.
   Der Squash `da7b0eb…` wurde am 2026-10-07 um 04:18:12 UTC integriert;
   vollständige Tree-Gleichheit, Main-Synchronisierung und lokale/remote
   Bereinigung des eigenen Arbeitsbranches sind unabhängig bestätigt.
   Die zwei historischen CI-Fehler bleiben im Producernachweis getrennt
   dokumentiert; ihre Ursache ist unbekannt. Die Diagnostik ändert weder
   SQL-Prädikate noch Budgets und behauptet keine Fehlerbehebung.
   Die anschließend getrennte Main-Push-CI am Squash `da7b0eb…` ist vollständig
   beendet: 12 von 13 Workflows und 47 von 48 Jobs SUCCESS. Im
   [DGN-007-Lauf 37570814577](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37570814577)
   scheiterte SQL Server 2022 im zweiten BA-Lifecycle mit
   `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`; dieser Guard prüft
   gespeicherte Query-Store-Zeiten gegen `ExecutionStarted/ExecutionFinished`.
   Alle zehn begonnenen 2022-Datenbankabwesenheitsprüfungen und der eigene
   Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
   2019/2025 bestanden jeweils zwölf Lifecycles und sechs Decoder-Captures.
   Das ist ein neuer tatsächlicher Runtime-Vertragsfehler, keine vollständige
   Main-CI-Freigabe und keine Aufhebung der erfolgreichen PR65-Abnahme.
   Welche Grenze verletzt wurde und weshalb, ist noch nicht belegt.
   Die getrennte private 2022-Gegenprobe bestand anschließend den CI-Präfix
   Datenmodell, Fenster, Profil, AB und BA je zweimal: zehn Lifecycles,
   vier Decoder-Captures, zehn Abwesenheitsprüfungen und fünf zusätzliche
   Gruppen-Leerheitsprüfungen PASS. Die eigene Instanz ist unabhängig abwesend;
   alle 21 Freeze-Dateien blieben gleich. G13 wurde nicht reproduziert und
   es liegen keine tatsächlichen G13-Zeitwerte vor. Zwei vorherige synthetische
   Probe-Vorchecks scheiterten vor jedem Lifecycle; ihre Defekte und ihr
   unabhängig bestätigter Cleanup stehen im Producernachweis getrennt.
   Nächster Schnitt ist der begrenzte kanonische G13-Grenzabstandsbericht,
   ausschließlich im bereits verletzten Fehlerzweig, mit strenger Kanalbindung
   und Ausgabe erst nach Cleanup. Guards, Last und Budgets bleiben gleich.
   Dieser begrenzte kanonische Reporter ist jetzt lokal implementiert und
   unabhängig geprüft. 43 Runner-Tests, 37 Producer-/Reporter-Methoden
   (36 PASS, ein Linux-spezifischer SKIP unter Windows) und sieben
   DGN-007-Validatoren bestanden. Acht tatsächliche temporäre SQL-Branchfixtures
   bestanden auf einer neuen eigenen 2022-Instanz `16.0.4295.3`:
   beide Ein-Tick-Verletzungen, beide Seiten, Gleichheit, gleiche Requestgrenzen,
   UTC-Offset, acht Gruppen und ausdrücklicher Overflow bei neun.
   Quellenfreeze unverändert; eigene CID und Name nach Entfernung unabhängig
   abwesend bestätigt. Der ganze vorherige SQL35 ergibt sich nach exakt
   validierter Reporterentfernung unverändert. Der Report bleibt atomar
   innerhalb 24 Diagnosezeilen und wird erst nach Cleanup ausgegeben.
   Die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
   am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, ist
   vollständig beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1
   und 2022 BA1 scheiterten an G13; 2025 bestand zwölf Lifecycles und sechs
   Captures. Der Reporter erfasste jeweils genau eine vollständige verletzte
   Gruppe: First−Start beträgt −4.263 beziehungsweise −9.510 100-ns-Ticks,
   entsprechend −0,4263 beziehungsweise −0,951 ms; nur die untere Grenze
   ist verletzt. Alle 32 begonnenen Lifecycles bestanden die erste unabhängige
   Datenbankabwesenheitsprüfung, alle neun SQL-Containerabbauten bestanden;
   DGN-007 mit expliziter eigener CID-Abwesenheit. Linux 163 Methoden PASS.
   Der PR bleibt ohne Mergefreigabe offen. Beide QS-Zeitwerte liegen in diesen
   zwei Beobachtungen auf einem Millisekundenraster; daraus folgt keine
   allgemeine Auflösung, Clockursache oder Toleranzfreigabe. Die getrennte private
   Originalmaterialisierungsprobe reproduzierte G13 auf einer neuen eigenen
   2022-Instanz in AB1: First−Start −0,2609 ms. Die verletzte Gruppe enthält im
   tatsächlich übernommenen Captureversuch und im Live-SELECT jeweils eine
   positive Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen. Ein
   Zero-Extremum erklärt diese lokale Verletzung nicht. Elf temporäre SQL-
   Fixtures bestanden; sechs Präfix-Lifecycles PASS, AB1 FAIL, sofortiger Stop.
   Alle sieben ersten DB-Abwesenheitsprüfungen und unabhängiger eigener
   Containerabbau bestanden; Freeze mit 27 Dateien unverändert. Kein AB2/BA/AA
   und kein erfolgreicher AB-Capture. Die Messvertragsgrenze zwischen QS-Endzeit
   und SYSUTC-Requestklammer bleibt ungeklärt. Der quellenbasierte
   [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md) liegt
   jetzt als `PROPOSED` vor: exakter Einschluss und kontrollierte
   Kollektivzuordnung sind getrennte Alternativen. Der Kandidat verlangt
   eine belegte Familienbasis B, sequenziellen T0-Capture vor T1,
   vollständige Bilanz B→B+4→B+8 und vertrauenswürdig attestierten
   Ausführungsumfang. Vorabrequests erfolgen vor der expliziten QS-
   Konfiguration; eine frische Datenbank garantiert kein QS-OFF oder
   Nullbaseline. Konkrete Baseline-/Intervall- und Herkunftsbelege bleiben
   offen. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
   prüft jetzt synthetische Gegenbeispiele und bedingte Konsistenz, ohne
   SQL-/v1-Änderung oder Runtimeattestation. Passende Counts allein belegen
   keine Herkunft; fehlende Annahmen und Widersprüche bleiben getrennt.
   Die getrennte [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
   ist abgeschlossen: Procedure-Queries werden auch unter AUTO erfasst;
   asynchrone Persistenz ist keine belegte Publikationsverzögerung. Eigene
   Calls, Ergebnismessung und erster Cleanupabschluss sind nutzbar, aber
   kontinuierlicher QS-Zustand, vollständiger Basisabschluss, interne
   Intervallaktivierung und geschlossene Coordinatorherkunft bleiben offen.
   Der konkrete [Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
   liegt jetzt als `PROPOSED` vor: acht Stages, vollständige Raw-/Gruppen-/
   Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze,
   Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Kostenlimits.
   Diese Obergrenzen sind vorgeschlagen, nicht runtimevalidiert; Sättigung
   bleibt bedingt, punktweise States belegen keine Kontinuität. Die äußere
   256-KiB-Grenze belegt heute keine Gesamtgrenze im vorher puffernden Proxy.
   Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: unter unabhängig
   geschlossenem Callumfang und injektiver kohärenter Zählung trägt Sättigung
   Callerfassung; vollständige keyweise Stageledger tragen kollektiv I0/I1.
   Durchgängiges RW/ALL ist ein getrenntes konservatives Methodengate,
   aus Counts nicht bewiesen und hier nicht aufgehoben. Der heutige Pfad
   liest Live-Dateien und adressiert Namen; Bundle-/Zugangs-/Hostgrenze,
   Acquisition-/Floatregel und Kostenmachbarkeit bleiben tatsächlich offen.
   Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
   prüft jetzt den Zählschluss mit synthetischen Ausführungstokens und getrennten
   Claims für Callerfassung, Bucketzuordnung und QS-Zustand. Die alte 42-Test-
   Voraussetzungssuite bleibt erhalten. Keine reale QS-Einzelidentität oder
   Runtime-/Methodenfreigabe. Das konkrete
   [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
   Acquisition-/Count- und Floatkandidat, ausführbare Freeze-/Actor-/CID-/
   Host-/Zugangsgrenzen sowie gleichzeitige Streaming-/Poll-/Kostenlimits.
   Alle Methodengates bleiben offen; normative Auswahl braucht eine ausdrückliche
   neue Entscheidung. Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
   ist statisch implementiert: feste 27 Mitglieder, originale Gitblobs,
   getrennte Rohbyte-/LF-Bindung und deklarierte AST-Imports mit Manipulationsfixtures.
   Keine SQL-/Launcher-Runtime oder tatsächliche Ausführungsattestation.
   Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
   ist statisch implementiert: Python-3.12-Ganz-AST-Profil, sechs SQL-only-Manifeste,
   14 Quellenhashes und SQLCMD-Gegenproben. Import-/Launcherentwurf PROPOSED,
   tatsächliche Importumgebung und verwendete Runtimebytes offen. Der getrennte
   [synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
   portable Budgetgegenproben und feste eigene Linux-Kindfälle, ohne Integration
   in Runtimequellen oder Methoden-/Runtimeattestation. Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Der erste Implementierungsteil ist das getrennte [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md): unveränderter 27-Member-Git-/Kantenvorcheck, eingefrorene neun Python-Rohbytes und begrenzte binäre Rahmung mit Kontext- und Manipulationsgegenproben. Keine Worker- oder Kandidatenimportausführung und kein UsedBytes-Claim. Die getrennte [synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md) ist implementiert: ausschließlich feste Fixturebytes, tatsächliches Compile/Exec und objektgebundene Beginn-/Abschlussreceipts. Kein DGN-Import oder Importauflösungsnachweis; DGN-Attestationsflags bleiben false. Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) ist implementiert: begrenzte aktuelle Bootstrapmetadaten und Vergleich gegen separat deklarierte Baseline. Keine Trust- oder bereits ausgeführte Bibliotheksbyteattestation; die gewählte Kontrollruntime bleibt eine ausdrücklich benannte Annahme. Der [skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) liegt als `DESIGNED` vor. Der getrennte [reine Profilvergleich](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert: 38 synthetische Tests prüfen exakte deklarierte Installation und Workerinventur, eingefrorenen Eingangs-/Ordinal-/Phasenkontext sowie gemeinsame Metadatengrenzen. Sein Match attestiert keine tatsächliche Workerbeobachtung, Herkunft oder Consumption. Die tatsächliche Prozessanbindung bleibt unimplementiert. Die getrennte lokale Record-Rückgabe des Profilvorschnitts ist jetzt implementiert: `observe_current_interpreter_records` liefert ausschließlich die tatsächlich aufgenommene und vollständig geprüfte Abschlussaufnahme, bei Ablehnung keine Records. Gehaltene Liveanker sind kein dauerhaft gültiger Zustand des Modulcaches; spätere aktuelle Runtimeverwendung braucht eine frische Aufnahme. Legacyreports, Bootstrapimports und Grenzen bleiben erhalten. Der vollständige Linux-/Python-3.12-Import-Only-Prototyp bleibt offen; als nächste Teile folgen konkrete Workerbootstrapauswahl, skalare Projektion und kombinierter Codec, tatsächliche Parent-/Worker-Anbindung, feste Quellenauflösung, tatsächliche DGN-Loaderverwendung und Importabschluss sowie begrenzte eigene Worker samt unabhängigem Cleanup. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation.
   Erst nach
   tragfähiger Methodenentscheidung gemeinsam versionierte Umsetzung.
   Keine implizite OFF-/CLEAR-/Laständerung.
   Bestehende Guards, Fehler und DEC-068 bleiben erhalten;
   Ursache und Behebung offen.
   Einzelheiten stehen im
   [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
   Keine identische Wiederholung oder Toleranzkorrektur ohne neue Evidenz.
   Die interne Capture-Rückgabe ist lokal vorbereitet und unabhängig
   geprüft, ihre Veröffentlichung und Integration sind zunächst zurückgestellt.
   Nach der G13-Klärung folgt die interne verlustfreie Capture-Rückgabe:
   den vollständigen Body und tatsächlich geprüfte Phasen übernehmen,
   Rückgabe erst nach erfolgreichem Harness-Cleanup und erstem erfolgreichen
   unabhängigen Abwesenheitscheck. Counts, CLI und Fehlerprioritäten bleiben
   gleich; Recovery liefert niemals einen erfolgreichen Capture-Beleg.
   Dies erzeugt keine RunRecords oder Runtimeattestation. Danach folgen
   Coordinator-Freeze, Ressourcen, tatsächliche serielle Reihenfolge und
   präzise Budgets; erst danach frische prospektive Bestätigungsläufe.
   Die bisherigen Captures belegen keine Regression, Ursache, Mitigation oder
   Capstone-Freigabe.
   Der Compatibility-Vorfix ersetzt im älteren Teilnehmerpfad die ungültige
   Property-Abfrage durch den Katalogwert und lehnt NULL oder Werte ungleich
   170 vor der Evidenzausgabe ab. Die Adaptervalidierung besitzt denselben
   NULL-Schutz. Die Plan- oder Laufzeitprofilbedingung bleibt Folgearbeit.
   Die acht statischen Compatibility-Tests bestanden. Am 2026-10-06 bestanden
   zusätzlich acht T-SQL-Guard-Fixtures (170, 160, NULL und fehlende Zeile je
   SQL-Quelle), die echte Abfrage eines fehlenden Zielnamens sowie die
   Kontextprojektion mit synthetischen Query-Store-Optionen und echtem
   `master`-Katalogwert auf SQL Server 2025 Developer `17.0.4075.5`.
   Aufruf: `python Tests/Static/test_dgn007_compatibility.py --container NAME
   --confirm-disposable-instance`. Die frische eigene Instanz war vor und
   nach den lesenden Prüfungen leer und wurde anschließend nach
   Eigentumsprüfung entfernt; ihre Abwesenheit wurde unabhängig bestätigt.
   Die ersten Versuche scheiterten an der fehlenden Query-Store-Optionszeile
   in `master` und zählen nicht als erfolgreiche Evidenz. Der Nachweis gilt
   nur für Katalogzugriff, Guard- und Projektionsfixtures; er enthält keine
   echte Compatibility-Änderung und keinen vollständigen Teilnehmerlauf.
4. Eine weitere `LABINT-004`-Matrixaussage erst aktivieren, wenn ein zusätzlicher gelber Slice samt Safety- und Szenariofreigabe sie benötigt.
5. Docker-/Podman-Ressourcen-, Netzwerk-, Hyper-V- oder gemischte Topologien nur bei einer konkret nachgewiesenen fachlichen Abhängigkeit bearbeiten.
6. Änderungen an `SQL_Server_Lab` bleiben ohne konkrete Fähigkeitslücke und ausdrückliche Freigabe gesperrt.

## 6. Sicherheits-, Datenschutz- und Quellenstatus

- Szenariodefinitionen enthalten nur synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen.
- Gelbe und rote Szenarien behalten ihre bestehenden Safety-Gates; `RES-003` benötigt zusätzlich dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget.
- `DGN-007` setzt validierte Query-Store- und Extended-Events-Evidenz voraus.
- Der SQL-Server-2025-Delta-Review ist in `SQL_SERVER_2025_DELTA_REVIEW.md` abgeschlossen: CE Feedback für Ausdrücke und zeitgebundene XE-Sessions sind in bestehende Verträge übernommen; vier Infrastruktur-/Abhängigkeitsthemen bleiben zurückgestellt, Vector/KI außerhalb des Curriculums.
- Aktuelle Herstellerdokumentation allein ist weiterhin kein Implementierungs- oder Runtime-Nachweis.
