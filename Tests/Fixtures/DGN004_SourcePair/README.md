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

Nächste Schritte sind vollständige statische Prüfung der Originalbytes,
Projektionen, Paarung, terminalen Hintposition und endlichen M/S/T-Offsets sowie
negative Source-/Textmutationen. Erst danach kommen die bestehenden Review- und
Matrixgates für spätere technische Qualifikation.
