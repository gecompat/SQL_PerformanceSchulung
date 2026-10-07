# Initialer Backlog

## Aktueller operativer Einstiegspunkt

Der kanonische aktuelle Fortschritt, die Abhängigkeiten und der nächste ausführbare Schritt stehen in [`Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md`](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md). Die priorisierte Folgeplanung steht in [`Documentation/Project_Planning/NEXT_DEVELOPMENT_WAVES.md`](../Documentation/Project_Planning/NEXT_DEVELOPMENT_WAVES.md). Historische Fortschrittsmarker im Masterplan dürfen diesen Status nicht widersprechen.

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
  - [ ] Separaten begrenzten Linux-/Python-3.12-Import-Only-Prototyp nach dem Entwurf vervollständigen: vorbereitetes Eingangsprotokoll verwenden, tatsächliche Loaderverwendung und Importabschluss getrennt bestätigen, Shadowing-/Austausch-/Alias-/Replay-/Cleanupgegenproben. Bestehende neun Runtimequellen unverändert; Claim ausschließlich für tatsächlich abgeschlossene Top-Level-Imports, keine SQL-/Acquisition-/Methodenattestation.
  - [x] [Prozess-/Manifestkanten](../Documentation/Project_Planning/DGN_007_EXECUTION_EDGE_VERIFIER.md) getrennt offline prüfen: festes Python-3.12-AST-Profil, sechs SQL-only-Manifeste, 14 Quellenhashes und SQLCMD-Gegenproben. Importumgebungs-/Launcherentwurf PROPOSED; tatsächliche Importumgebung und Runtimebytes bleiben offen, kein Launcherstart oder Methodenentscheid.
  - [x] [Offline-Quellenbundle-Verifier](../Documentation/Project_Planning/DGN_007_SOURCE_BUNDLE_VERIFIER.md) im bestehenden DGN-007-Scope statisch implementieren: exakter Commit, Gitblobs und feste Mitglieder-/Importclosure; temporäre Manipulationsfixtures für fehlende/zusätzliche/doppelte Mitglieder, Byte-/Pfad-/Importänderung, EOL, Exportattribute und Overflow. Keine Bundleausführung, SQL-/Docker-Runtime, tatsächliche Quellen-/Actor-/Zugangs-/Hostattestation oder Methodenfreigabe.
  - [ ] Internen verlustfreien Capture-Vorschnitt integrieren (lokal vorbereitet und geprüft, Veröffentlichung bis zur G13-Klärung zurückgestellt): vollständigen Body und tatsächlich geprüfte Phasen über den vorhandenen Harness erhalten, Rückgabe erst nach erfolgreichem Lifecycle und erster unabhängiger Datenbankabwesenheitsprüfung. Bekannte Kontrollverträge, Counts-/CLI-Ausgabe und Fehlerprioritäten bewahren; Recovery liefert keinen erfolgreichen Beleg. Keine RunRecords, Runtimeattestation oder Incidentbewertung.
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
