# SQL Server Performance Schulung

Dieses Repository enthält herstellernahe, reproduzierbare Schulungsunterlagen und Demonstrationen zur Performanceanalyse und -optimierung mit Microsoft SQL Server.

## Ziel

Die Schulung soll technische Ursache-Wirkungs-Zusammenhänge sichtbar machen. Jede Demonstration verbindet ein klar definiertes Lernziel mit reproduzierbarem Setup, messbarer Baseline, kontrollierter Problemursache, Diagnose-Evidenz, Gegenmaßnahme und Cleanup.

## Zielplattformen

- SQL Server 2019
- SQL Server 2022
- SQL Server 2025 als primäre Entwicklungs- und Demonstrationsplattform

Versions-, Compatibility-Level- und Edition-Abhängigkeiten werden je Demo ausdrücklich dokumentiert.

## Grundsätze

- T-SQL ist das bevorzugte Demonstrationsmittel.
- Infrastruktur wird nur eingesetzt, wenn T-SQL den Effekt nicht realistisch erzeugen kann.
- Alle Beispiele verwenden ausschließlich synthetische Labordaten.
- Präsentationen und weitere Schulungsartefakte enthalten keine nicht freigegebenen Firmeninformationen, Logos, Kontaktdaten oder internen Systembezeichnungen.
- Nur `Gerhard Pisch` ist als ausdrücklich freigegebene reale Namensangabe zulässig.
- Bildbasierte Logos und Markenkennzeichen werden zusätzlich zur Text- und Metadatensuche visuell geprüft.
- Risikoreiche Eingriffe sind eindeutig gekennzeichnet und ausschließlich für isolierte Laborsysteme vorgesehen.
- Aussagen werden gegen aktuelle Primärdokumentation geprüft; versionsabhängige Aussagen werden nicht pauschalisiert.

## Verbindliche Planung

- [Master-Umsetzungsplan](Documentation/Project_Planning/MASTER_IMPLEMENTATION_PLAN.md)
- [Gate-A-Review](Documentation/Project_Planning/GATE_A_REVIEW.md)
- [Review der Welle-1-Framework-Basis](Documentation/Project_Planning/WAVE_1_FRAMEWORK_FOUNDATION_REVIEW.md)
- [Review der Welle-1-Daten-, Mess- und Ergebnisbasis](Documentation/Project_Planning/WAVE_1_DATA_MEASUREMENT_REVIEW.md)
- [Konflikt- und Entscheidungslog](Documentation/Project_Planning/CONFLICT_AND_DECISION_LOG.md)
- [Planergänzung zur Qualität der Schulungsunterlagen](Documentation/Project_Planning/PRESENTATION_QUALITY_INTEGRATION_PLAN.md)
- [Baseline-Review der vorhandenen Präsentationen](Documentation/Reviews/PRESENTATION_BASELINE_REVIEW_2024.md)
- [Priorisierte Inhalts- und Evidenzlücken](Documentation/Reviews/CONTENT_GAP_ANALYSIS.md)
- [Quellenmanifest der Schulungsartefakte](Documentation/Inventories/SOURCE_MANIFEST.md)
- [Folien- und Aussagenregister](Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md)
- [Curriculumarchitektur und Lernzielmodell](Documentation/Curriculum/CURRICULUM_ARCHITECTURE.md)
- [Traceability-Matrix](Documentation/Curriculum/TRACEABILITY_MATRIX.md)
- [Kritische Aussagenprüfung](Documentation/Reviews/CRITICAL_CLAIMS_REVIEW.md)
- [Projektweites Quellenregister](Documentation/Research/SOURCE_REGISTER.md)
- [Primärquellenregister für W0](Documentation/Research/PRIMARY_SOURCES_W0.md)
- [Primärquellen für die Welle-1-Framework-Basis](Documentation/Research/FRAMEWORK_SOURCES_W1.md)
- [Terminologie- und Schreibstandard](Documentation/Standards/TERMINOLOGY_AND_STYLE_STANDARD.md)
- [Privacy- und Metadaten-Prüfverfahren](Documentation/Quality/PRIVACY_METADATA_REVIEW_PROCEDURE.md)

## Repository-Struktur

| Pfad | Zweck |
|---|---|
| `.ai/` | Verbindlicher Projektkontext, Entscheidungen, Roadmap und AI-Arbeitsregeln |
| `Assets/` | Firmenneutrale, wiederverwendbare Abbildungen und Quelldateien |
| `Documentation/` | Curriculum, fachliche Vertiefungen, Demo-Katalog, Reviews und Recherche |
| `Demos/` | Modulare, bevorzugt T-SQL-basierte Demonstrationen |
| `Infrastructure/` | Reproduzierbare Docker-, Podman- und Hyper-V-Laborszenarien |
| `Presentations/` | Firmenneutrale Präsentationsquellen und Exporte |
| `Tests/` | Statische Prüfungen und SQL-Server-Versionsmatrix |
| `Tools/` | Unterstützende, nicht demo-spezifische Werkzeuge |

Details zur Ausführung und zu Voraussetzungen werden mit den jeweiligen Demos ergänzt.

## Sicherheitsstufen für Demos

- **Grün:** normale, lokal begrenzte T-SQL-Demo.
- **Gelb:** kontrollierte CPU-, RAM-, TempDB-, I/O- oder Concurrency-Last.
- **Rot:** Instanzkonfiguration, Cache-Eingriff, Dienstneustart oder Infrastrukturmanipulation; nur in einer isolierten Lab-Instanz.

## Status

Welle 0 und Gate A sind fachlich validiert. In Welle 1 sind `FWK-001` bis `FWK-005`, `FWK-008`, `FWK-009`, `FWK-011` und `FWK-012` implementiert und statisch prüfbar. Die Basis umfasst Preflight, markergeprüften Testdatenbank-Lifecycle, deterministische synthetische Daten, sessionbezogene Messung, Plan-/Statistikevidenz, Safety-Gates, Demo-Dokumentation sowie einheitliche Status-, Fehler-, Skip- und Ergebnisverträge.

Die SQL-Runtime-Validierung gegen SQL Server 2019, 2022 und 2025 ist noch offen, da derzeit kein SQL-Server-Host zur Verfügung steht. Als Nächstes folgen `FWK-006`, `FWK-007` und `FWK-010` für Multi-Session-Orchestrierung, Query-Store-/Extended-Events-Helfer und den vollständigen Runtime-Harness. Danach folgen Versionsmatrix und vier Gate-B-Pilotdemos. Der Gesamtstatus des Projekts bleibt `PLANNED`.

## Lizenz

Dieses Projekt verwendet eine eigene Lizenz und ist nicht als Open-Source-Projekt lizenziert. Maßgeblich ist [LICENCE.md](LICENCE.md).
