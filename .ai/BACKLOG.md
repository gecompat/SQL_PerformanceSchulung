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
