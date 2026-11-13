# DGN-004 – R/H-Quellpaar

Dieses Verzeichnis enthält die zwei vollständigen textuellen
`CREATE PROCEDURE`-Quellwerte für den begrenzten DGN-004-Schnitt sowie einen
separaten SQL-Transportausschnitt für bereits extern gebundene Planhandles. `R`
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

`Tests/Static/dgn004_plan_transport.py` dekodiert bereits geparste Stücke;
`Tests/Static/dgn004_plan_frame.py` enthält einen reinen Serializer für
vorgelegte UTF-16-Planbytes sowie den Parser für das hier festgelegte
Textformat. `Tests/Static/dgn004_capture_result.py` bindet die decodierten
Bytes zusätzlich an die vom Aufrufer separat erwartete Run/Rollen/Aufruf-
Kombination und prüft ein vollständiges wohlgeformtes XML-Dokument mit
`ShowPlanXML`-Wurzelelement. Eine Rahmung besteht aus genau diesen ASCII-Zeilen:

```text
DGN004_PLAN_START|<run>|<role>|<call>|<byte_count>|<chunk_count>|<sha256>
DGN004_PLAN_CHUNK|<sequence>|<hex_payload>
...
DGN004_PLAN_END|<run>|<role>|<call>|<byte_count>|<chunk_count>|<sha256>
```

Zeilen werden durch LF oder CRLF getrennt; ein einzelner abschließender
Zeilenumbruch ist erlaubt. Leerzeilen, weitere Ausgabe, zusätzliche Felder,
Escaping und andere Zeilenumbrüche sind ungültig. `run` ist ein nichtleerer
ASCII-Token aus Buchstaben, Ziffern, Punkt, Unterstrich und Bindestrich
(1 bis 64 Zeichen);
`role` ist `R` oder `H`; `call` ist eine kanonische Dezimalzahl von 1 bis 9.
Der aufrufende Prüfer muss erwartetes Run, Rolle und Call separat liefern.
Start- und Endzeile müssen
diese Bindung sowie Bytezahl, Stückzahl und SHA-256 exakt wiederholen. Diese
Selbstdeklaration verbindet Daten nur mit der separat erwarteten Aufrufbindung;
sie belegt keine Query-, Plan- oder Engineidentität.

Die Bytezahl ist gerade und zwischen 1 und 512 KiB. Die Stückzahl ist exakt
`ceil(byte_count / 100)`. Sequenzen beginnen in diesem Format fest bei 1;
jeder Chunk ist eine Zeile mit kleingeschriebenem oder großgeschriebenem
Hex-Bytepaaren, genau 100 Bytes außer dem letzten Reststück. SHA-256 ist
64-stelliges ASCII-Hex. Die bestehende Transportfunktion prüft lückenlose
Reihenfolge, Stück- und Gesamtgrenzen, den Hash sowie strikte UTF-16LE- und
UTF-8-Dekodierung. Der Parser lehnt nachträglich gelesenen Text über 2 MiB ab;
das begrenzt keinen Prozesskanal während des Lesens. Diese statischen Helfer
belegen weder sqlcmd-Erfassung noch stderr-/stdout-Limits, XML-/Planqualität,
Planidentität, Laufzeitverhalten oder vollständige Transportsicherung. Diese
Erfassungs- und Ergebnisgates bleiben offen.

`Tests/Static/dgn004_acceptance_contract.py` prüft getrennt davon den
statischen Statusvertrag für die neun vorgesehenen Aufrufe auf den beiden
Zielbuilds. Synthetische Gegenfälle erzwingen vollständigen Quell-/Identitäts-/
Plan-/Kontext-/Transportbezug, 768 Solltupel unabhängig aus den registrierten
Form-A-ID-/Wertformeln mit den festgelegten Duplikaten,
Kompilierungs- und Ausführungszuwächse, Force-/Unforce-Zustände und eigene
Force-Fehlerzählepochen, den festen
H-Hint, den begrenzten `acceptance_scope` sowie Statusvorrang einschließlich
`FAIL_CLEANUP`. Replay-Markerwerte werden absichtlich nicht als Pflicht
verwendet. Der Prüfer bewertet ausschließlich caller-gelieferte Werte und
synthetische Fixtures; er erzeugt keine Runtimeevidenz und schließt weder
Methodenfreigabe noch SQL-/Versions-/Demoqualifikation.

`CapturePlanFrame.sql` liest den `query_plan`-Wert für ein vom Aufrufer
übergebenes Handle aus `sys.dm_exec_query_plan_stats`, serialisiert das XML in
UTF-16-Bytes und gibt die festgelegten Start-/Chunk-/End-Zeilen als einzelne
Textspalte aus. Der Runner muss die Run-/Rollen-/Call-Werte und den 1–64 Byte
langen Handle vor der sqlcmd-Substitution validieren; `dgn004_capture_input.py`
stellt dafür nur die enge Token-/Hex-Prüfung bereit. `varbinary(64)` bezeichnet
eine Höchstlänge, keine feste Handlelänge. Der DGN-Runner liest stdout und
stderr parallel mit den festen 2-MiB-/64-KiB-Grenzen und führt den lokalen
Docker-Client direkt aus, damit kein innerer Shim die SQL-Ausgabe vorher
vollständig puffert. Der Runner muss außerdem die vorangegangene
Quellen-/Query-/Ausführungsbindung bereits belegt haben. Das SQL kann weder
beweisen, dass das Handle zum beabsichtigten aktuellen Aufruf gehört, noch
Plan- oder Engineidentität herstellen. Es prüft die 512-KiB-Grenze erst nach
der XML-Serialisierung. Die Prozessgrenzen sind mit synthetischen lokalen
Prozessen geprüft, aber nicht gegen SQL Server ausgeführt; SQL-Syntax-/Build-
Qualifikation bleibt offen. Auf POSIX beendet der Runner seine eigene
Prozessgruppe. Unter Windows ist die Baumbeendigung nach Ende des Launchers
nicht nachgewiesen; bleibt ein Pipe-Reader offen, endet der Aufruf mit
`CaptureProcessEndUnknown` und darf nicht wiederholt werden. Das Fixture ist
keine freigegebene Demo und nicht selbstständig auszuführen.

`Tests/Static/dgn004_identity_snapshot.py` vergleicht separat vom Aufrufer
gelieferte R/H-Rohdatensätze mit den endlichen registrierten M/S/T-Texten,
UTF-16LE-Offsets, Modulnamen und getrennten Objekt-/Query-IDs. Die Herkunftslabels
und die Gruppierung als R/H-Rolle sind Eingabebehauptungen; der Prüfer ermittelt
keine Serverzeilen und prüft nicht, ob ihre Aufzählung vollständig war. Sein
Offline-Konsistenzresultat enthält keinen `plan_handle` und kann den Capture-
Runner nicht freigeben. Damit bleiben die Zuordnung eines Handles zu genau der
aktuellen Nutzstatementausführung, vollständige Serverkandidatenaufzählung,
Kontextprofil-/Plan-StatementText-Bindung sowie Ausführung auf SQL Server offene
Gates.

`SnapshotPlanCandidates.sql` erfasst als begrenzte Source-only-Vorstufe alle
gecachten Statementzeilen, deren Datenbank-/Objektbindung, vollständige
Modulbytes und registrierter Statementstart exakt passen. Es verwendet keine
`TOP`-Auswahl, prüft die aktuelle Modulquelle im Katalog und gibt einen
nummerierten, an Run/Rolle/Call gebundenen Rahmen mit jedem Kandidaten aus. Der
Runner liefert die unveränderten Moduleinbytes als Hex über stdin, begrenzt
Prozesskanäle und SQL-Timeout wie der bestehende Plan-Capture-Runner und
verlangt vollständige Frames. `dgn004_plan_candidates.py` vergleicht die
zusammengesetzten Zeilenschlüssel aus Planhandle, SQLhandle, Start-/Endoffset,
Generation und Erstellungszeit. Der Binder lässt nur genau eine neue Zeile mit
Ausführungszähler 1 oder genau eine bestehende Zeile mit Zählerdelta 1 durch;
Löschung, Mehrdeutigkeit, mehrere Änderungen, unvollständige Frames und
zusätzliche Ausführungen werden abgewiesen. Die Tests verwenden ausschließlich
synthetische Frames und Prozesse. Der Cache-Locator ist nicht SQL-kompiliert
oder live ausgeführt; seine Ein-Writer-Kausalzuordnung bleibt Inferenz und ist
keine authentifizierte Invocation-ID. Die drei vorhandenen
Metadatenbeobachtungen pro Flush und alle DGN-Budgets bleiben bindend.
