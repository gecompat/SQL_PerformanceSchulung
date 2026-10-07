# Demos

Die Demos folgen [`.ai/DEMO_CONTRACT.md`](../.ai/DEMO_CONTRACT.md). Maßgeblich sind die stabile Demo-ID und der tatsächliche Manifestpfad. Die historisch entstandenen Ordnernummern entsprechen nicht durchgehend der Modulfolge der Präsentation.

## Einstieg ohne Repository-Vorwissen

1. Wählen Sie eine der 22 runtimevalidierten Demos im [Demo-Katalog](../Documentation/Demo_Catalog/README.md). Dort stehen Sicherheitsstufe, Ausführungspfad und der datierte Nachweis je Zielversion, einschließlich Skips und Warnungen.
2. Lesen Sie die verlinkte Demo-README für Lernziel, Rechte, Ressourcen und erwartete Beobachtung.
3. Folgen Sie dem [zentralen Ausführungsleitfaden](../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md): Instanz und Arbeitsplatz vorbereiten, Manifest ausführen, Ergebnis einordnen und Cleanup prüfen. Ohne vorhandenen SQL Server beginnt der unterstützende Bereitstellungspfad im [Container-Quickstart](../Documentation/HowTo/CONTAINER_QUICKSTART.md).

`QRY-006` ist zusätzlich implementiert, besitzt aber noch keine vollständige Runtime-Gate-Abnahme. Die Teilmanifeste von `DGN-007` sind Entwicklungsschnitte und keine freigegebene vollständige Schulungsdemo. Eine vorhandene Datei allein begründet keine Schulungsfreigabe.

Die konkrete Schritt-für-Schritt-Ausführung aller freigegebenen Demos steht in
[`Documentation/HowTo/DEMO_EXECUTION_GUIDE.md`](../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md).
Sie enthält je Demo den tatsächlichen Manifestpfad, die erforderliche
Sicherheitsbestätigung, die erwarteten Ausgaben sowie Cleanup und Recovery.

## Tatsächliche Ablage

| Ordner | Vorhandener Inhalt / nächster Einstieg |
|---|---|
| [`00_Framework/`](00_Framework/README.md) | Gemeinsame Verträge und Hilfswerkzeuge; keine eigenständige Fachdemoliste |
| `01_Storage_Pages_Log/` | `STL-008`, `STL-009` |
| [`02_Optimizer_Statistics_Plans/`](02_Optimizer_Statistics_Plans/README.md) | Historischer Platzhalter; ausführbare Optimizer-Demos stehen unter `04_Optimizer_Statistics_Plans/` |
| [`03_Query_Patterns/`](03_Query_Patterns/README.md) | Historischer Platzhalter; ausführbare Query-Patterns-Demos stehen unter `05_Query_Patterns/` |
| `04_Optimizer_Statistics_Plans/` | `OPT-002`, `OPT-003`, `OPT-005`, `OPT-009`, `OPT-010`, `OPT-013`, `OPT-015`, `OPT-016`, `OPT-017` |
| `04_Rowstore_Columnstore/` | `IDX-006`, `IDX-010` |
| `05_Concurrency_Isolation_TempDB/` | `CON-009`; Blocking und Deadlock stehen unter `07_Concurrency/` |
| `05_Query_Patterns/` | `QRY-001`, `QRY-004`, `QRY-013`; zusätzlich `QRY-006` mit offenem Runtime-Gate |
| `06_CPU_Memory_IO_Waits/` | `RES-007` |
| `07_Concurrency/` | `CON-004`, `CON-006` |
| `07_Query_Store_Extended_Events/` | `DGN-003`, `DGN-005`; zusätzlich begrenzte Entwicklungsschnitte für `DGN-007` |
| [`08_Infrastructure/`](08_Infrastructure/README.md) | Platzhalter; die vorhandenen Bereitstellungsanleitungen stehen unter `Documentation/HowTo/` |

Die Vorbereitung der didaktischen Prüfung steht im [Generalprobenplan](../Documentation/Project_Planning/PRS_010_REHEARSAL_PLAN.md). Dieser Plan ist kein Nachweis einer bereits durchgeführten Schulung.

Neue Demos werden erst nach Vergabe einer stabilen Demo-ID angelegt.
