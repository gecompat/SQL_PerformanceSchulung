# DGN-010 – private Ergebnis- und Storagevorbereitung

Stand: 2026-10-11. TSK-011/CUR-021. Basis
`acd88e25e15932ff42154a7c40e436d8837aaee8`. DGN-010 bleibt PROPOSED;
kein ausführbares FWK-Demopaket oder vollständiger TP-PERF-Nachweis.
Diese Vorbereitung belegt nur die neue konkrete Ergebnis-/Storagefrage.

## Tatsächlich ausgeführter Umfang

Eine neue eigene Podmaninstanz verwendete das bereits vorhandene Microsoft-Image
2025-CU9-ubuntu-24.04 mit exakt gebundener lokaler Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`.
SQL meldete 17.0.5005.3, Enterprise Developer/EngineEdition 3, Ubuntu 24.04.
4 CPU/6 GB, ein zufälliger eigener Loopbackport, 60 Sekunden SQL-Prozessbudget und
getrennte begrenzte Cleanupcalls blieben erhalten. Native ODBC-SQLCMD.EXE verwendete
SQLCMDPASSWORD ausschließlich über Umgebung, keine Passwortwerte in Argumenten.

Die neue eigene Datenbank SQLPERF_DGN010_PROBE hatte 256/64-MB-Dateilimits,
Kompatibilität 170, SIMPLE und vier vollständige Eigentumsmarker. Eine feste Quelle
enthielt 1000 Rows mit eindeutigen IDs 1–1000, Value=Id×3 und vollständigem 100-Byte-
Payload aus F-Zeichen. Ein WITHOUT LOGIN Reader erhielt CONNECT und ausschließlich
SELECT auf dieser Quelle. Die feste Query hatte separate int-Parameter 101/110.

Unter Reader wurden tatsächlich je zehn vollständige Rows vor dem Index, mit dem
Index und nach seinem Drop erfasst. Zweiwegige EXCEPT-Vergleiche, Counts und die
anfängliche Oraclefixture banden Id/Value/Payload. Der tatsächliche eigene feste
NONCLUSTERED ID-INCLUDE(Value,Payload)-Index hatte 1000 Indexrows und 17 used pages;
die bestehende Clustered-PK-Struktur hatte 18 used pages. Die Pagezahlen stammen aus
sys.dm_db_partition_stats, keine geschätzte Bytes-/RAM-/DMLkostenzahl.

Eine rein synthetische deklarierte Advice-Zeichenfolge behauptete einen Queryvorteil.
Sie wurde niemals als SQL ausgeführt. Ausschließlich festes Owner-DDL erstellte und
entfernte den eigenen Candidateindex. Anschließend waren die drei Queryrowsets gleich,
die volle 1000-Row-Quelle unverändert, der Candidateindex abwesend und die vollständige
direkte Readerrechtefixture samt fehlender Rollenmitgliedschaft erhalten. REVERT
schützte Erfolg und Fehler.

Vier volle bytegenaue Marker banden den eigenen DB-Abbau. DB-Abwesenheit wurde danach
unabhängig in master geprüft; der eigene Container wurde nach Ownerprüfung entfernt
und seine Abwesenheit separat geprüft. Keine fremde Instanz, kein anderes Repository,
Modell, Providerendpoint, Preview- oder Hostkonfiguration wurde verändert.

## Review und offene Abnahme

Ein enger unabhängiger Quellenreview prüfte ausschließlich die neue private SQL-Probe
und das native -i-/Timeoutdelta des bereits korrigierten Podmanadapters. Er fand keine
konkreten P1/P2-Befunde, führte keine eigene Runtime aus und attestierte keinen
Performance-/LLM-/Preview- oder vollständigen Demo-PASS. Der bestehende Provideradapter
wurde nicht erneut vollständig analysiert. Ein Owner, ein erforderlicher Review,
maximal zwei Korrekturwellen; kein Runtimefehler und keine Korrekturwelle verbraucht.
Private Quellen bleiben ignoriert unter Runtime, keine kanonische Backlogduplikation.
Modell-/Tokenverbrauch bleibt unbekannt; es wurden keine Modellcalls ausgeführt.

Keine tatsächlichen Pläne, Query-Reads/CPU/Elapsed, DMLkosten, A/B/BA/AA- oder
Effektseparationsmessung wurden ausgeführt. 17 zusätzliche Indexseiten widerlegen
allein keinen Performancevorteil. Das vollständige DGN-010-Paket benötigt diese
TP-PERF-Mess-/Oracle-/Negativ-/Versions-/Cleanupqualifikation vor Registrierung und
didaktischer Freigabe. Ältere Versionen wurden in dieser Vorbereitung nicht ausgeführt.
CON-010-FAIL sowie Live-/Cloud-/ONNX- und der ausstehende Previewentscheid bleiben
erhalten. Die Vorbereitung ist unabhängig davon zulässig; TSK-011 bleibt insgesamt offen.
