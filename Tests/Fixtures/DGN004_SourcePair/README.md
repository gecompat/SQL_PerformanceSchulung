# DGN-004 – R/H-Quellpaar

Dieses Verzeichnis enthält ausschließlich die zwei vollständigen textuellen
`CREATE PROCEDURE`-Quellwerte für den begrenzten DGN-004-Schnitt. `R`
(`ReplayReference`) ist die Referenz ohne Hint. `H` (`ReplayHintControl`) ist
die getrennte Kontrolle mit genau einem terminalen
`DISABLE_OPTIMIZED_PLAN_FORCING`-Hint. Die Texte übernehmen die Form A und die
M/S/T-Bytebindungen des registrierten `rh_source_text_plan`.

Die Dateien enthalten weder Schema-/Tabellenaufbau noch Daten, Cleanup,
Query-Store-Steuerung oder Frameworkphasen. Sie sind keine freigegebene Demo und
wurden nicht auf SQL Server ausgeführt. Führe sie nicht gegen eine Instanz aus,
bevor Datenbank, Schema, Tabellen, Eigentumsmarker und der spätere Lifecycle
separat freigegeben und bereitgestellt sind.

Der aktive Aussageumfang bleibt klassische Standard-Planerzwingung mit
`sys.sp_query_store_force_plan`/`sys.sp_query_store_unforce_plan` und H als
`CONTROL_ONLY` (nur Kontrollzustand belegt). Diese Quellen allein belegen keine
Planbindung, Hintwirkung, Replay-Nutzung oder -Nichtnutzung, Leistung oder
Kausalität.

Die statische Prüfung der Originalbytes, Projektionen, Paarung, terminalen
Hintposition und endlichen M/S/T-Offsets sowie negative Source-/Textmutationen
sind vorhanden. Vollständige Erfassung, unabhängiger Quellen-/Ergebnisreview
und die bestehenden Matrixgates bleiben für spätere technische Qualifikation
erforderlich.

`Tests/Static/dgn004_plan_transport.py` enthält den begrenzten Offline-Decoder
für bereits geparste (Sequenznummer, Hex-Payload)-Stücke. Er prüft lückenlose
Reihenfolge, Stück- und Gesamtbytegrenzen, die als serverseitig deklarierte
SHA-256-Prüfsumme sowie
strikte UTF-16LE-Dekodierung und die UTF-8-Textgrenze. Da der Capture-Entwurf
keine konkreten Start-/End-Zeilen oder deren Feldsyntax festlegt, parst dieser
Helper keine sqlcmd-Ausgabe und behauptet keine vollständige Transportsicherung,
Kanalbegrenzung, Planidentität oder XML-/Planqualifikation. Die Wire-Frame-Form
und ihre End-to-End-Erfassung bleiben ein separates Gate. Die interne
Decoder-API akzeptiert Startindizes 0 oder 1; das legt die Basis der späteren
Wire-Frames nicht fest.
