# Initialer Backlog

## Aktueller operativer Einstiegspunkt

Der kanonische aktuelle Fortschritt, die Abhängigkeiten und der nächste ausführbare Schritt stehen in [`Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md`](../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md). Historische Fortschrittsmarker im Masterplan dürfen diesem Status nicht widersprechen.

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
- [ ] Query Store und Extended Events als zentrale Diagnosepfade in Pilotdemos validieren.
- [x] `W2-001` Bestandsbeispiele vollständig als `REUSE`, `REFACTOR`, `REBUILD`, `DIAGNOSTIC_ONLY` oder `REMOVE` klassifizieren und kanonischen Demo-IDs zuordnen.
- [ ] `W2-002` interne und externe Datenabhängigkeiten der priorisierten Migrationskandidaten entfernen.
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
- [ ] `ADV-008` freigegebene Vertiefungsdemos in kleinen, unabhängigen PRs implementieren und validieren.
  - [x] `OPT-015` Planweite und operatorbezogene Eigenschaften implementieren und auf SQL Server 2019, 2022 und 2025 jeweils zweimal validieren.
  - [x] `OPT-016` Rebind, Rewind, Outer References und Spools implementieren und auf SQL Server 2019, 2022 und 2025 jeweils zweimal validieren.
  - [ ] Nächste Schnitte: `QRY-013` und `QRY-004_CLASSIC_AND_DYNAMIC`.
- [ ] `ADV-009` Masterdeck, Speaker Notes und Teilnehmerunterlage quellengebunden integrieren und jede neue Folie einem Tiefenprofil zuordnen.
- [ ] `ADV-010` Vertiefungsstrang fachlich, didaktisch und technisch abnehmen.

## P1 - Interaktive Schulungsszenarien mit SQL_Server_Lab

- [x] `LABSCN-001` Ziel, Verantwortungsgrenze und Lifecycle interaktiver Schulungsszenarien verbindlich festlegen.
- [ ] `LABSCN-002` vorhandene und geplante Beispiele inventarisieren und als interaktiv geeignet, nur automatisiert prüfbar oder nicht anwendbar klassifizieren; Schema für Szenariodefinitionen erstellen.
- [ ] `LABSCN-003` ersten vollständigen Vertical Slice umsetzen: Beispiel auswählen, über `SQL_Server_Lab` provisionieren, fachlich vorbereiten, als `READY_FOR_USER` übergeben, zurücksetzen und entfernen.
- [ ] `LABSCN-004` Benutzerbedienung und How-to für Auswahl, Start, Übergabe, Reset und Remove standardisieren.
- [ ] `LABSCN-005` weitere Container- und Hyper-V-Szenarien anhand konkreter Beispielanforderungen umsetzen.
- [ ] `LABSCN-006` gemischte Topologien erst für ein fachlich begründetes Beispiel mit nachgewiesenem Bedarf umsetzen.
- [ ] Für jedes Szenario Mindestanforderungen an Hosthardware, Providergrenzen, Versionen und Resetstrategie dokumentieren.
- [ ] Zusätzliche Funktionalität in `SQL_Server_Lab` nur nach konkretem Szenariobefund benennen und erst nach ausdrücklicher Freigabe dort umsetzen.

## P1 - Nachgeordnete SQL_Server_Lab-Qualitätssicherung

- [x] `LABINT-001` automatisierten Testkatalog, JSON-Schema und statische Vollständigkeitsprüfung erstellen.
- [ ] `LABINT-002` Smoke-/Core-Test für Aufbau, Vorbereitung, Reset und Abbau des ersten interaktiven Vertical Slice implementieren.
- [ ] `LABINT-003` Docker-/Podman-Parität für geeignete Szenarien praktisch prüfen.
- [ ] `LABINT-004` gelbe und vollständige Container-Matrix nach Safety- und Szenariofreigabe aktivieren.

## P1 - Masterdeck und Präsentationsvarianten

- [x] `DEC-043` Kanonisches Masterdeck und reproduzierbar abgeleitete Tiefenprofile verbindlich entscheiden.
- [x] Architekturplan für `BASIS`, `STANDARD` und `VERTIEFUNG` einschließlich Custom Shows, eigenständiger `.pptx`-Ableitung und Qualitätsgates erstellen.
- [x] `PRS-011` SlideKey- und JSON-Variantenmanifest-Vertrag definieren.
- [ ] `PRS-012` Masterdeck mit stabilen SlideKeys und den Custom Shows `BASIS`, `STANDARD` und `VERTIEFUNG` ausstatten.
- [ ] `PRS-013` kontrollierten interaktiven Build eigenständiger `.pptx`-Varianten aus einer Kopie des Masterdecks implementieren.
- [ ] `TST-011` statischen Validator für Manifest, SlideKeys, Custom Shows, Abhängigkeiten, Links, Quellen und Demo-IDs implementieren.
- [ ] `TST-012` Render-, Notes-, Metadaten-, Privacy- und Branding-Abnahme für jede freigegebene Variante implementieren.
- [ ] Trainer-Runbook um Auswahl und Start der Custom Shows sowie Erzeugung eigenständiger Varianten ergänzen.

## P2 - Reproduktion und Testmatrix

- [x] SQL-Server-2019/2022/2025-Testmatrix definieren und erfolgreich ausführen.
- [x] How-to für vorhandene SQL-Server-Instanz plus isolierte synthetische Testdatenbank erstellen. Der Laufnachweis gegen eine vorhandene Instanz steht noch aus.
- [ ] Kompakten Docker-/Podman-Bereitstellungspfad für Personen ohne verfügbaren SQL Server planen.
- [ ] Docker-/Podman-Ressourcen- oder Netzwerkfunktionen nur für konkret abhängige Demos prüfen.
- [ ] Hyper-V nur für nachweislich Windows-, Storage- oder OS-nahe Demos planen.
- [x] Wiederholbare Concurrency-Prozesssteuerung ohne proprietäre Abhängigkeiten implementieren und mit realen parallelen SQL-Sessions validieren.
- [x] Hardwareabhängige Erwartungswerte als Invarianten, Richtungen, Verhältnisse oder begründete Bandbreiten statt Fixwerte definieren.
- [ ] Vorhandene Präsentationsmodule fachlich modernisieren und mit Demo-Katalog, Quellenregister, Lernzielen und Tiefenprofilen synchronisieren.
- [x] Branding-bereinigte Repository-Fassung der Schulungsunterlagen bereitstellen.

## Erledigungsregel

Ein Punkt gilt nur dann als erledigt, wenn Artefakt, Quellenprüfung und zutreffende Validierung im Repository nachvollziehbar vorhanden sind. `IMPLEMENTED` ersetzt keine Runtime-Validierung ausführbarer SQL-Artefakte. Ein interaktives Szenario gilt erst als vollständig, wenn Aufbau, Vorbereitung, Benutzerübergabe, Reset und Abbau praktisch nutzbar sind.
