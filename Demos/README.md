# Demos

Die Demos folgen [`.ai/DEMO_CONTRACT.md`](../.ai/DEMO_CONTRACT.md). Maßgeblich sind die stabile Demo-ID und der tatsächliche Manifestpfad. Die historisch entstandenen Ordnernummern entsprechen nicht durchgehend der Modulfolge der Präsentation.

## Einstieg ohne Repository-Vorwissen

1. Wählen Sie eine der 23 runtimevalidierten Demos im [Demo-Katalog](../Documentation/Demo_Catalog/README.md). Dort stehen Sicherheitsstufe, Ausführungspfad und der datierte Nachweis je Zielversion, einschließlich Skips und Warnungen.
2. Lesen Sie die verlinkte Demo-README für Lernziel, Rechte, Ressourcen und erwartete Beobachtung.
3. Folgen Sie dem [zentralen Ausführungsleitfaden](../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md): Instanz und Arbeitsplatz vorbereiten, Manifest ausführen, Ergebnis einordnen und Cleanup prüfen. Ohne vorhandenen SQL Server beginnt der unterstützende Bereitstellungspfad im [Container-Quickstart](../Documentation/HowTo/CONTAINER_QUICKSTART.md).

`QRY-006` (NULL bei NOT IN und NOT EXISTS) ist zusätzlich implementiert, besitzt aber noch keine vollständige Runtime-Gate-Abnahme. Die Teilmanifeste von `DGN-007` (Zeitabhängige Regression eines Suchworkloads) sind Entwicklungsschnitte und keine freigegebene vollständige Schulungsdemo. Eine vorhandene Datei allein begründet keine Schulungsfreigabe.

Die konkrete Schritt-für-Schritt-Ausführung aller freigegebenen Demos steht in
[Ausführungsleitfaden für die katalogisierten Demos](../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md).
Er enthält je Demo den tatsächlichen Manifestpfad, die erforderliche
Sicherheitsbestätigung, die erwarteten Ausgaben sowie Cleanup und Recovery.

## Tatsächliche Ablage

| Ordner | Vorhandener Inhalt / nächster Einstieg |
|---|---|
| [`00_Framework/`](00_Framework/README.md) | Gemeinsame Verträge und Hilfswerkzeuge; keine eigenständige Fachdemoliste |
| `01_Storage_Pages_Log/` | `STL-008` (Transaktionslog und Dateiwachstum)<br>`STL-009` (Mehrere Änderungen gemeinsam bestätigen) |
| [`02_Optimizer_Statistics_Plans/`](02_Optimizer_Statistics_Plans/README.md) | Historischer Platzhalter; ausführbare Optimizer-Demos stehen unter `04_Optimizer_Statistics_Plans/` |
| [`03_Query_Patterns/`](03_Query_Patterns/README.md) | Historischer Platzhalter; ausführbare Query-Patterns-Demos stehen unter `05_Query_Patterns/` |
| `04_Optimizer_Statistics_Plans/` | `OPT-002` (Statistiken lesen)<br>`OPT-003` (Stichproben und ungleiche Datenverteilung)<br>`OPT-005` (Wachsende Schlüssel und Statistikpflege)<br>`OPT-009` (Parametersensitive Planoptimierung)<br>`OPT-010` (Planoptimierung für optionale Parameter)<br>`OPT-013` (Sortieren mit zu wenig Arbeitsspeicher)<br>`OPT-015` (Ausführungspläne systematisch lesen)<br>`OPT-016` (Wiederholte Operatorausführung und Zwischenspeicherung)<br>`OPT-017` (Ungleich verteilte parallele Arbeit) |
| `04_Rowstore_Columnstore/` | `IDX-006` (Seitenaufteilungen und Seitenbelegung)<br>`IDX-010` (Columnstore-Segmente gezielt überspringen) |
| `05_Concurrency_Isolation_TempDB/` | `CON-009` (Kosten in tempdb unterscheiden); Blocking und Deadlock stehen unter `07_Concurrency/` |
| `05_Query_Patterns/` | `QRY-001` (Indexfreundliche Suchbedingungen)<br>`QRY-004` (Optionale Filter, Recompile und dynamisches SQL)<br>`QRY-013` (Anwendung langsam, Verwaltungswerkzeug schnell); zusätzlich `QRY-006` mit offenem Runtime-Gate |
| `06_CPU_Memory_IO_Waits/` | `RES-007` (Wartezeiten im richtigen Messbereich) |
| `07_Concurrency/` | `CON-004` (Blockierungsketten verfolgen)<br>`CON-005` (Schemasperren trotz NOLOCK; begrenzter Schnitt validiert)<br>`CON-006` (Zyklische Sperrkonflikte erkennen) |
| `07_Query_Store_Extended_Events/` | `DGN-003` (Abfragehistorie mit Query Store)<br>`DGN-005` (Gezielte Ereigniserfassung mit Extended Events); zusätzlich begrenzte Entwicklungsschnitte für `DGN-007` |
| [`08_Infrastructure/`](08_Infrastructure/README.md) | Platzhalter; die vorhandenen Bereitstellungsanleitungen stehen unter `Documentation/HowTo/` |

Die Vorbereitung der didaktischen Prüfung steht im [Generalprobenplan](../Documentation/Project_Planning/PRS_010_REHEARSAL_PLAN.md). Dieser Plan ist kein Nachweis einer bereits durchgeführten Schulung.

Neue Demos werden erst nach Vergabe einer stabilen Demo-ID angelegt.
