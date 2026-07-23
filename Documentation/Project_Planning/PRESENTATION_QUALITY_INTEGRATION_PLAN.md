# Planergänzung – Qualität der Schulungsunterlagen

| Merkmal | Wert |
|---|---|
| Status | `PLANNED` |
| Geltung | verbindliche Ergänzung des Master-Umsetzungsplans |
| Stand | 2026-07-23 |
| Baseline | [`PRESENTATION_BASELINE_REVIEW_2024.md`](../Reviews/PRESENTATION_BASELINE_REVIEW_2024.md) |

## 1. Zweck und Geltung

Diese Planergänzung integriert die Ergebnisse der Bestandsprüfung in den bestehenden Master-Umsetzungsplan. Sie konkretisiert Welle 0, den Curriculum-Workstream und Welle 2. Bei Abweichungen zwischen allgemeinen Formulierungen und dieser Ergänzung gilt für die Überarbeitung der vorhandenen Schulungsunterlagen die präzisere Regel dieses Dokuments.

## 2. Ergänzungen zu Welle 0

| ID | Größe | Arbeit | Ergebnis / Abnahme |
|---|---:|---|---|
| `W0-009` | M | Baseline-Review der vorhandenen Präsentationen pflegen | modulweise Qualitätsbewertung, fachliche Befunde, Priorisierung und Maßnahmen dokumentiert |
| `W0-010` | M | Sanitizing-Regeln für Bestandsunterlagen anwenden | unzulässige Logos, Organisationskennzeichen, Kontaktdaten, Metadaten und interne Hinweise entfernt; freigegebene Ausnahmen dokumentiert |
| `W0-011` | L | Folienbezogenes Aussagenregister erstellen | jede kritische Aussage besitzt Modul-/Folienbezug, Quelle, Versionsgrenze, Schweregrad und Entscheidung `KEEP`, `REFINE`, `REPLACE` oder `REMOVE` |
| `W0-012` | M | Visuelle Branding-Prüfung definieren | Masterfolien, Layouts, Bilder, Notes, Exporte und eingebettete Medien werden zusätzlich zur Textsuche visuell geprüft |

Besonders zu prüfen sind CTE, Table Variables, Heaps, RID Lookup, Forwarded Records, Filegroups, physische I/O-Trennung, Plan Cache, Recompilation, Adaptive Join, Batch Mode on Rowstore, Columnstore-Maintenance, Remote Pushdown, Linked Server, Partitionierung, Worker/Tasks/Threads sowie Hash-basierte Eindeutigkeitsmuster.

## 3. Ergänzungen zum Curriculum-Workstream

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `CUR-009` | M | Diagnoseleitfaden als roten Faden definieren | Symptom → Messung → Hypothese → Maßnahme → Vergleich ist modulübergreifend konsistent |
| `CUR-010` | M | Rollenmodell der Unterlagen festlegen | Projektionsfolie, Sprecherhinweis, Teilnehmerunterlage und Demo-Evidenz sind klar abgegrenzt |
| `CUR-011` | M | Zusammenfassungen und Wissenskontrollen integrieren | jedes Kernmodul enthält Zusammenfassung, typische Fehlinterpretationen und mindestens eine überprüfbare Transferaufgabe |
| `CUR-012` | M | Folienlast und Informationsdichte begrenzen | technische Tiefendetails werden in Notes oder Teilnehmerunterlagen verschoben; die Projektionsfolie bleibt auf Kernaussage und Evidenz fokussiert |

## 4. Verbindlicher Diagnoseleitfaden

1. Symptom, Bezugszeitraum und betroffene Workload bestimmen.
2. CPU, Duration, Reads, Writes, Rows und Waits erfassen.
3. Blocking und Ressourcengrenzen klassifizieren.
4. Actual Execution Plan und tatsächliche Kardinalitäten prüfen.
5. Schätzfehler, Zugriffspfade, Memory Grants, Parallelität und Spills untersuchen.
6. Eine überprüfbare Hypothese formulieren.
7. Genau eine begründete Änderung durchführen.
8. Vorher-Nachher-Vergleich unter vergleichbaren Bedingungen erstellen.
9. Nebenwirkungen, Wartungskosten und Versionsgrenzen bewerten.

## 5. Ergänzungen zu Welle 2

| ID | Größe | Arbeit | Abschlusskriterium |
|---|---:|---|---|
| `W2-007` | M | Präsentationsmodule fachlich überarbeiten | falsche, veraltete oder zu absolute Aussagen korrigiert oder ersetzt; Quellen und Versionsgrenzen dokumentiert |
| `W2-008` | M | Unterlagenrollen trennen | Projektionsfolien reduziert, Sprecherhinweise vertieft, Teilnehmerunterlagen ergänzt und Demo-Zuordnungen hergestellt |
| `W2-009` | M | moderne Diagnose- und Optimierungsfunktionen ergänzen | relevante Funktionen von SQL Server 2019, 2022 und 2025 sind versionsbewusst integriert |
| `W2-010` | S | freigegebene Namensausnahme anwenden | Nur `Gerhard Pisch` darf im vorgesehenen Kontext vorkommen; nicht freigegebenes Branding ist entfernt |
| `W2-011` | M | Bestandsbeispiele fachlich neu messen | jede übernommene Kernaussage besitzt reproduzierbare Evidenz und dokumentierte Messgrenzen |

## 6. Pilotdemos als Qualitätsgate

Vor einer breiten Überarbeitung dienen folgende vier Demos als Qualitätsmaßstab:

1. SARGable gegenüber Non-SARGable Predicate,
2. Statistik-Skew und Kardinalitätsfehler,
3. kontrollierte Blocking Chain mit Head Blocker,
4. Memory Grant mit Spill oder vergleichbarem kontrollierten Ressourceneffekt.

Jede Pilotdemo erfüllt den vollständigen Demo-Vertrag einschließlich Setup, Baseline, Evidenz, Gegenmaßnahme, Vergleich, Cleanup, Versionsgrenzen, Mindestressourcen und Abbruchbedingungen.

## 7. Sanitizing- und Branding-Vertrag

- `Gerhard Pisch` ist als Namensangabe freigegeben.
- Das vom Auftraggeber bezeichnete Firmenlogo sowie die dazugehörigen Firmen- und Markenkennzeichen werden aus allen Präsentationen, Masterfolien, Layouts, Bildern, Notes, Begleitdokumenten und Exporten entfernt.
- Weitere nicht freigegebene Firmeninformationen, Kontaktdaten, interne Pfade und interne Systembezeichnungen werden entfernt oder neutralisiert.
- Office-Metadaten und eingebettete Medien werden vor der Übernahme geprüft.
- Textsuche allein gilt nicht als ausreichender Branding-Nachweis.

## 8. Abnahme

Die Planergänzung gilt als umgesetzt, wenn:

- das folienbezogene Aussagenregister vollständig ist,
- alle Findings des Baseline-Reviews einer Maßnahme zugeordnet sind,
- die vier Pilotdemos validiert sind,
- die Präsentationsmodule fachlich und didaktisch überarbeitet wurden,
- Quellen, Sprecherhinweise, Teilnehmerunterlagen und Demo-Katalog konsistent sind,
- die visuelle und technische Branding-Prüfung keine unzulässigen Kennzeichen findet,
- die SQL-Server-Versionen 2019, 2022 und 2025 entsprechend den jeweiligen Featuregrenzen geprüft wurden.
