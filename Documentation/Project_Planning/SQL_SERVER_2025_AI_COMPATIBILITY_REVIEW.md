# TSK-004 – angehaltener Compatibility-Level-Slice

Stand: 2026-10-11. Basis `63f256fcbca522fa3ed7c2fdd6fee564c83381f1`.
Der private Slice ist nach zwei Korrekturwellen mit FAIL angehalten. Er erweitert
keine Demo-, Versions-, CL- oder Funktionsfreigabe; TSK-004 bleibt offen.

## Ausführung und begrenzte Beobachtungen

Drei neue eigene Podmancontainer verwendeten den vorhandenen Tag
2025-CU9-ubuntu-24.04 mit vollständiger lokaler Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`.
SQL meldete jeweils 17.0.5005.3, Enterprise Developer/EngineEdition 3, Ubuntu 24.04.
4 CPU (Central Processing Unit; Prozessor)/6 GB, eigener Loopbackport, zeitbegrenzte native SQLCMD-Aufrufe und
SQLCMDPASSWORD ausschließlich in der Umgebung begrenzten die private Probe.
Nur die eigene frische Datenbank SQLPERF_AI_CL_PROBE wurde verändert: SIMPLE,
256/64-MB-Dateilimits und vier vollständige Eigentumsmarker. Kein Preview,
Modellcall oder Hostkonfigurationseffekt gehörte dazu.

Der erste Einbatchversuch schlug fehl; dessen konkrete SQL-Fehlerausgabe wurde vom
Helper nicht erhalten. Welle 1 korrigierte die Chunkfixture anhand der bestehenden
QRY-016-Oracle auf 1-basierte Reihenfolge/Offsets und gab Fehlerstdout aus. Dieser
Versuch scheiterte an der erwarteten niedrigen-CL-Denialkontrolle. Sein Chunk-PASS-
Marker trug einen konstanten CL170-Text und ist kein belegter niedriger-CL-Claim.

Welle 2 trennte Setup, ALTER DATABASE, jede Probe und Cleanup in frische SQLCMD-
Verbindungen. Der DB-Metadatencheck band jeweils CL150, CL160 und CL170. Bei allen
drei liefen VECTOR(3)/float32, NORM/NORMALIZE und drei DISTANCE-Ausdrücke ohne
SQL-Fehler durch den privaten Skalarharness. Dessen IF-Vergleiche besitzen jedoch
keine expliziten NULL-Gegenkontrollen und drucken Sollwerte statt Istwerte. Deshalb
sind die Skalar-PASSmarker keine vollständige Ergebnisqualifikation.

Bei CL150/160 schlug die vorab fixierte Chunking-Denialoracle mit Fehler 51003 fehl.
Der intern gefangene tatsächliche Fehlercode und Text wurden nicht ausgegeben;
weder erfolgreiche niedrige-CL-Verfügbarkeit noch ein bestimmter Unsupportedfehler
ist damit nachgewiesen. Bei CL170 bestand die positive Chunkfixture: zwei vollständige
Rows mit Reihenfolge/Offset/Länge/Textbytes (1/1/4/ABCD und 2/5/4/EFGH).
Die vorhandene Quellenmatrix und das CL170-Demoprofil werden nicht gelockert.

## Cleanup, Budget und Wiederaufnahme

Alle drei eigenen Container wurden nach exakter Ownerprüfung entfernt und ihre
Abwesenheit separat geprüft. In den ersten beiden Fehlversuchen wurde kein separater
SQL-DB-Abwesenheitsnachweis erreicht; der eigene wegwerfbare Containerabbau beseitigte
den Bestand. Im letzten Versuch bestanden zusätzlich voller bytegenauer Viermarker-
Check, SQL-DB-Drop und unabhängige DB-Abwesenheitskontrolle in master.

Der enge unabhängige Quellenreview bestätigte den P2-NULL-Oraclefehler der
Skalarprüfung. Die volle positive CL170-Chunkfixture und die marker-/ownergebundenen
Cleanupquellen waren nachvollziehbar; der Reviewer führte keine eigene Runtime aus.
Ein Owner, dieser Review und höchstens zwei Korrekturwellen begrenzen den Slice.
Keine dritte Korrektur oder Runtimewiederholung folgt aus
dem fehlgeschlagenen Nachweis. Private Quellen bleiben ignoriert unter Runtime;
Modell-/Tokenverbrauch bleibt unbekannt. Wiederaufnahme benötigt einen ausdrücklich
neu abgegrenzten Qualifikationsschnitt mit vollständigen positiven Skalar-Istwerten,
NULL-Gegenkontrollen und erhaltenen tatsächlichen Chunkfehlern, keine unveränderte
Wiederholung. Der separat konkret freigegebene ANN-Slice kann unabhängig beginnen.
