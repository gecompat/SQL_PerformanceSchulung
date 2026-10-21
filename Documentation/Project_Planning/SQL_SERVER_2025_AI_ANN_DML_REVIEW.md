# TSK-006 – Einzelne UPDATE-/Rollback-Diagnose

Stand: 2026-10-11. Privater begrenzter Diagnosescope aus der ausdrücklich erteilten
weiteren lokalen Wellenfreigabe; vor SQL in
[Aktueller Ausführungsstand](CURRENT_EXECUTION_STATUS.md) festgelegt. Höchstens
zwei Kandidaten/vier eigene serielle Container, zwei Lifecycles je positivem
stabilem Kandidaten. Die früheren FAIL-Checkpoints/Budgets bleiben unverändert.

## Ergebnisvertrag

Fester Build 17.0.5005.3, 1000 VECTOR(3)-float32-Rows und eigener DiskANN/COSINE-
Index. Die vollständige DB-Konfigurationsaufnahme zeigt keine
ALLOW_STALE_VECTOR_INDEX-Row; der Guard verlangt dieses ABSENT-Profil, keine
erfundene OFF-Attestierung und kein Set. Ein bereits vorhandener Target Id 23
wird mit einem gültigen, vorher tatsächlich abweichenden VECTOR(3) genau einmal
parameterisiert aktualisiert. Kein INSERT/DELETE/MERGE und kein Stalepfad.

SQL-Erfolg und tatsächliche Fehlernummer/-State/-Text werden aufgenommen, ohne
eine Fehlernummer oder Read-only-/Generationsklassifikation zu erfinden. Bei
Erfolg müssen eine tatsächlich veränderte Row und die vollständige Zielbyteform
innerhalb der Transaktion belegt sein. Transaktion immer zurückrollen, danach
vollständiger beidseitiger Sourcebytevergleich, vollständige Own-Indexmetadaten-
und Konfigurations-/Marker-/Baselinebindung. Kein Commit/Freshnesstest und keine
allgemeine DML-Unterstützung aus dem technischen Diagnoseergebnis ableiten.

Unveränderte Image-/Versions-/Ressourcen-/300-Sekunden-/60-Sekunden-Cleanupgrenzen,
tatsächliche duale Restores, neue Attestierung und separate DB-/Containerabwesenheit.
Keine Host-/Cloud-/ONNX-Wirkung. Quellen SRC-077/078/097; Generation UNKNOWN.

Elf betroffene lokale Grenz-/Manipulationstests bestanden. Der erforderliche enge
unabhängige Quellen-/Methodenreview schloss vor SQL ohne offene P1/P2; unveränderte Safety-/Helperanalysen
bleiben am aktuellen Sourcebinding nutzbar. Ein Owner und ein erforderlicher
Reviewer; Modell-/Tokenverbrauch unbekannt. Keine vollständige IDX-012-Abnahme.

## Erster Kandidat: widersprüchliche Transaktionsausgabe

Ein tatsächlicher Lifecycle FAIL. Das feste gültige UPDATE wurde mit SQL-Fehler
42231, State 1 verweigert; der synthetische Fehlertext benennt den Vectorindex
auf der eigenen Tabelle. Der vollständige Sourcebytevergleich nach Rollback,
Own-Indexmetadaten und Konfigurations-/Marker-/Baselineprüfungen bestanden.
Die JSON-Ausgabe meldete dennoch RolledBack=false, obwohl der frühere SQL-Guard
keine offene Transaktion attestierte. Der Client verwarf diese widersprüchliche
Evidenz. Keine vollständige Diagnose-/Transaktionsabnahme dieses Kandidaten und
keine unbelegte Aussage zur Ursache des Auswertungsunterschieds.

Tatsächliche Restores 0/0, neue Attestierung und unabhängige DB-/Containerabwesenheit
bestanden in 12,253 Sekunden; Prozesscode 1. Die ausgeführten Quellen bleiben
unverändert. Der zweite bereits budgetierte Kandidat sichert @@TRANCOUNT und
XACT_STATE() unmittelbar nach Rollback in Variablen und gibt diese tatsächlichen
Zahlen mit dem daraus abgeleiteten RolledBack aus. Beide Zahlen müssen 0 sein;
Parser verwirft fehlende, negative, offene oder boolesche Werte. Sieben betroffene
Tests bestanden; enger Befundnachreview vor SQL schloss ohne offene P1/P2. Kein Budgetreset.

## Zweiter Kandidat: begrenzte Diagnose bestanden

Zwei unveränderte Lifecycles bestanden. Der gültige parameterisierte UPDATE wurde
jeweils mit tatsächlichem SQL-Fehler 42231/State 1 wegen des Vectorindexes auf der
eigenen Tabelle verweigert. Der vor JSON (JavaScript Object Notation; strukturiertes Textformat) gesicherte Transaktionssnapshot enthielt
TransactionCount=0 und TransactionState=0, RolledBack=true. Vollständige Quellbytes
und Indexmetadaten blieben unverändert. Dies belegt die einzelne UPDATE-Verweigerung
am festen Build/Profil; kein allgemeiner INSERT-/DELETE-/MERGE- oder numerischer
Generationsbeweis. Keine Datenänderung wurde committed; Freshness NOT_TESTED.

Alle vollständigen Source-/Metadaten-/Marker-/Baseline-/Konfigurationskontrollen,
tatsächlicher Own-Index-Drop und duale Restores 0/0 bestanden. Neue Attestierung
und separate DB-/Containerabwesenheit bestanden; Cleanup 12,391/12,323 Sekunden,
beide Prozesscode 0. Zwei Kandidaten/drei Container, Scope regulär abgeschlossen.
Kandidat01-FAIL bleibt erhalten; Ursache der alten JSON-Auswertung nicht bewiesen.

| Private Quelle unter ANN_DML_CANDIDATE01 | SHA-256 |
|---|---|
| qualify_build.py | 3926286D885A07618482897FEF6AF83D21503D510D1C53C97F5C29643164016D |
| sql_build.py | C75376A3A6BEEC97692F8B2A1FA547B87A2D53D41DF0A5BCB57D3045CBAC046A |
| dml_evidence.py | 2735DF1266D985B2CE0456389900B89FB16E0D055CC20386CC0B17E02602F537 |
| test_dml.py | 5A03D9E0DD0FE2A557C8D25A8D5FBC947BFC0226A0EF529656F57447B05574CC |
| lifecycle01.log | AD58532AC75F9E0729CFECBC513B0A6A23912AE968AAF69ADF512E7489F85159 |

| Private Quelle unter ANN_DML_CANDIDATE02 | SHA-256 |
|---|---|
| qualify_build.py | 5142919355817A2866EBDA9A1C35E7CB57D5989432A70F9917C6491245CAA9AA |
| sql_build.py | 43F29045E6DFB617B8300EA631C63ACCFEA0A86EBD2010EA3FADF8BA0850A2A3 |
| dml_evidence.py | 4A7765629B0BECD60AD269CE882104B1C0BA0EFA98AC323B980BC9C698B6A4DB |
| test_dml.py | BB529020933695604C266D4EE1F4C2288C61BC3C4BAC69AB9F485BC525F092AC |
| lifecycle01.log | 05D93292BBB4C5762C7747CA8F6F1FD02EB93EDB512CE603CF4B90F612DAB4B6 |
| lifecycle02.log | 1A0FA5FB6F9A765E6B65BA78D10005F531EC7162400EA2D39E0E649480541918 |
