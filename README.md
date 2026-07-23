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
- [Planergänzung zur Qualität der Schulungsunterlagen](Documentation/Project_Planning/PRESENTATION_QUALITY_INTEGRATION_PLAN.md)
- [Baseline-Review der vorhandenen Präsentationen](Documentation/Reviews/PRESENTATION_BASELINE_REVIEW_2024.md)

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

Das Repository befindet sich im strukturellen Aufbau. Die vorhandenen Schulungsinhalte werden zunächst fachlich konsolidiert; anschließend entstehen die Demos modular nach der dokumentierten Roadmap.

## Lizenz

Dieses Projekt verwendet eine eigene Lizenz und ist nicht als Open-Source-Projekt lizenziert. Maßgeblich ist [LICENCE.md](LICENCE.md).
