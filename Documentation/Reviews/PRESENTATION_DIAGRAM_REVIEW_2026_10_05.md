# Diagramm- und Inhaltsprüfung der Präsentation

Prüfdatum: 2026-10-05. Die aktuelle Beauftragung umfasst die Korrektur falsch
gerichteter Pfeile und weiterer gefundener Unstimmigkeiten im Masterdeck.
Die Folienanzahl und Reihenfolge bleiben bei 102. Die 102 SlideKeys und die
drei Custom Shows bleiben erhalten.

Ausgangsdeck: SHA-256
`85bd14e4fc91d148889e9ebaa7128f6e1a213366f389aa6e2053f46cc0890ad3`.
Korrigiertes Masterdeck: SHA-256
`f655bc850e6d1367f52c7485babc5ce76eb23e14f8c8a1592b847d111473d7c5`.

## Befunde und Korrekturen

| Folien | Befund | Korrektur |
|---|---|---|
| 4, 20, 22, 29, 31, 59, 78 | Pfeilspitzen am Ausgangspunkt kehren Ablauf beziehungsweise Datenfluss um | Spitzen zum Ziel verschoben |
| 14 | Lesepfad im Buffer-Pool-Diagramm war gegenläufig und semantisch nicht eindeutig | Data Files zum Buffer Pool zu Query-Operatoren, Beschriftung und Notes erläutern Physical und Logical Reads; genügend Texthöhe verhindert automatische Schriftverkleinerung beim Variantenexport |
| 16 | Gegenläufige Commit-Kette, voller Log Buffer als vermeintliche Voraussetzung, Checkpoint als Pflichtschritt nach Commit | Log Buffer nimmt Records auf, vollständige Durability ausdrücklich benannt, Checkpoint separat dargestellt |
| 27 | Gegenläufiger Datenfluss und lineare Seek/Lookup-Kette | Seek als Outer Input und Lookup als Inner Input führen getrennt in Nested Loops, anschließend in SELECT |
| 50 | Baumkanten zeigen von Child Pages zum Parent | Navigationsrichtung Root zum Leaf korrigiert und beschriftet |
| 51 | Lookup-Verweise zeigen zurück zum Nonclustered Index | Navigation zum Heap beziehungsweise Clustered Index korrigiert, RID Lookup und Key Lookup beschriftet |
| 66 | Richtige Wartekanten können als falsch gerichteter Datenfluss gelesen werden | Richtung unverändert, Legende erklärt wartende Session zur blockierenden Session |
| 17 | IFI für Logwachstum pauschal ausgeschlossen | Ausnahme für Log-Autogrowth bis einschließlich 64 MB seit SQL Server 2022 ergänzt |
| 29 | Used Memory und Spill als Alternativen, Spill und Concurrency-Verlust als sichere Folgen dargestellt | Used Memory und Spill getrennt prüfen, Undergrant als Spill-Risiko und Overgrant als gebundenen Workspace beschreiben |
| 39 | Untere und obere Datumsgrenze verwenden unterschiedliche Parameter | Beide Grenzen verwenden `@Date`, Notes nennen `date` beziehungsweise Tagesbeginn als Voraussetzung |
| 54 | Kostenachse fehlt, Trefferzahl und Selektivität bleiben mehrdeutig | Schematische relative Zugriffskosten und steigende Trefferzahl beschriftet |
| 78 | „teuerste Operatorzahl“ ist keine verständliche Diagnosegröße | Hohe geschätzte Operatorkosten als unzureichender Ursachenbeweis eingeordnet |

Von 48 ursprünglichen Pfeilen zeigen 45 in die falsche Richtung. Davon
wurden 44 korrigiert und die irreführende Commit-Checkpoint-Verbindung entfernt.
Die drei Wartekanten auf Folie 66 waren bereits korrekt. Insgesamt sind
16 Folien und zehn Notes-Teile geändert. Alle übrigen 399 ursprünglichen
Paketbestandteile bleiben byteweise erhalten, einschließlich Medien,
Dokumenteigenschaften, Master, Layouts, Beziehungen und Custom Shows.

## Quellenprüfung

Die am 2026-10-05 geprüften Primärquellen bestätigen:

- [Instant File Initialization](https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-instant-file-initialization?view=sql-server-ver17):
  die seit SQL Server 2022 vorhandene Log-Autogrowth-Ausnahme und ihre 64-MB-Grenze (`SRC-034`).
- [Transaction Durability](https://learn.microsoft.com/en-us/sql/relational-databases/logs/control-transaction-durability?view=sql-server-ver17):
  Commit-Bestätigung nach Log-Persistierung bei vollständiger Durability und die getrennte Delayed-Durability-Semantik.
- [Transaction Log Architecture](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide?view=sql-server-ver17):
  WAL, Log Flush und Checkpoint als unterschiedliche Vorgänge (`SRC-033`).
- [Joins](https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17):
  getrennte Outer- und Inner-Inputs für Nested Loops.

Die Diagramme sind didaktische Schemata, keine gemessenen Pläne oder Benchmarks.
Die Notes führen Datenfluss, Navigation und Wartebeziehung ausdrücklich getrennt.

## Erzeugung und Prüfung

`Tools/repair_presentation_diagrams.mjs` nimmt ausschließlich gezielte
Open-XML-Korrekturen vor. Der Probeexport über Artifact Tool verlor die drei
Custom Shows und wurde verworfen. Die gezielte Paketbearbeitung bewahrt diese
Funktion. Ein erneuter Import des korrigierten Pakets in Artifact Tool wurde
durch die Finalisierung geprüft. Die Paket-, Layout-, Referenzfont- und
Tabellenprüfungen der Präsentationswerkzeuge waren erfolgreich.

Zwei Läufe des Korrekturwerkzeugs aus derselben Quelle ergaben identische Bytes.
PowerPoint Desktop renderte alle 102 Folien. Die 16 geänderten Folien wurden
einzeln visuell geprüft. Der Bildvergleich zeigt ausschließlich diese 16
Änderungen; die übrigen 86 Renderbilder stimmen exakt mit dem Ausgangsdeck
überein. Die Gesamtfolge wurde zusätzlich anhand der Renderübersicht geprüft.
Es wurden keine neuen Medien oder Office-Metadaten übernommen.

Die abschließende Abnahme ist erfolgreich:

- `validate_presentation_diagrams.py`: alle 13 Pfeildiagramme, Topologie und Klarstellungen.
- `validate_presentation_variants.py` und `validate_presentation_variant_outputs.py`:
  102 SlideKeys, drei Custom Shows und Varianten mit 41/66/102 Folien einschließlich Rendernachweisen.
- `validate_w2_007_presentation.py`, `validate_adv009_deck_integration.py`,
  `validate_adv010_deck_integration.py`, `validate_adv011_deck_integration.py`
  und `validate_adv_003_curriculum.py`: Claims und bestehende Integration erhalten.
- `validate_privacy_metadata.py .`: Repositoryprüfung erfolgreich. Die drei
  erzeugten PPTX wurden zusätzlich einzeln mit demselben Scanner geprüft, ohne Befunde.
- `Build-PresentationVariants.ps1 -Profile ALL` und
  `Test-PresentationVariantRenders.ps1`: alle Profile erfolgreich, Master beim Build unverändert.
- Alle 209 Variantenfolien rendern pixelgleich zur jeweiligen Masterfolie.
  `git diff --check` meldet keine Formatfehler.

Der neue Diagrammvalidator erkennt die Fehler im ursprünglichen Deck und besteht
mit dem korrigierten Deck. Die Erzeugungs- und Renderartefakte bleiben im
ignorierten Build-Verzeichnis. SQL-Server-Runtime-Tests sind für diesen
Präsentationsschnitt nicht erforderlich, da keine Demo verändert wurde.
