# DGN-010 – begrenzte private DML-Effektseparation

Stand: 2026-10-12. TSK-011/CUR-021, DGN-010 weiterhin PROPOSED.
Basis 2bef37419d9399cb5fc49658592de351b16815e5; empirischer Teilnachweis, kein öffentliches FWK-Paket,
Versions-/TP-PERF- oder Modulabschluss.

## Vollständig abgeschlossene Basis und neue Messfrage

[PR192](https://github.com/gecompat/SQL_PerformanceSchulung/pull/192) vollständig
abgeschlossen: Head 003bad4017233091f560752e93d2420b00c2f764, sieben aktuelle Head-Workflows PASS;
Squash 2bef37419d9399cb5fc49658592de351b16815e5, fünf Main-Workflows PASS; ganzer Tree a6dc9110a041c9c8be37c64aa9f41959e5efec81
exakt übernommen, main FF/sauber und eigener lokaler/Remote-Branch entfernt.
Die [Readerpfadmessung](SQL_SERVER_2025_AI_INDEX_MEASUREMENT_REVIEW.md) hielt beide
Indizes gleichzeitig vorhanden. Sie wird nicht unverändert wiederholt oder als
Indexabwesenheitsvergleich umgedeutet.

Dieser Folgeschnitt vergleicht dieselbe feste UPDATE-Struktur auf derselben
synthetischen Quelle ohne und mit eigenem Candidateindex. Build/Drop und vollständige
Quellen-/Config-/Readerprüfungen liegen außerhalb der DML-Messfenster. Eine feste
Advicefixture bleibt Hypothese; kein Modellaufruf oder Ausführen generierten SQLs.

## Vorab fester DML-Vertrag

Je Profil fünf separate Ein-UPDATE-Warmups pro Indexzustand und drei serielle
AB-/BA-/AA-Blöcke mit jeweils zwei Fenstern: 18 Messfenster à 100 UPDATEs.
AB/BA liefern sechs Samples pro Zustand; drei AA-Paare ohne Candidateindex separat.
1810 UPDATEs mit insgesamt 18100 vollständigen Rowkontrollen pro Profil. Eine weitere
positive Ein-UPDATE-Kontrolle und eine tatsächliche negative Kontrolle sind getrennt.
Keine Warmups in den Medianen, keine nachträgliche Sample-/Ausreißerauswahl.

Eigener Owner führt ausschließlich `UPDATE lab.SourceRows SET Value=Value+1`
für IDs 101–110 mit MAXDOP1 aus. Eine eigene explizite Transaktion umschließt jeden
Batch und wird tatsächlich zurückgenommen. Vor Eintritt und nach Rücknahme ist
@@TRANCOUNT=0 erforderlich; ein Fehlerpfad rollt eine noch aktive eigene Transaktion
ebenfalls zurück. Es werden keine fremden Transaktionen übernommen.

Jedes UPDATE liefert alle tatsächlichen INSERTED-IDs/Werte/100 Payloadbytes über
OUTPUT in eine eigene Tablevariable. Je Ordinal werden zehn eindeutige IDs 101–110,
Value=Id×3+Ordinal und vollständige F-Payloadbytes geprüft. Der native SHA256 über
alle zehn vollständigen Rows ist an eine getrennte feste UTF-16LE-Referenz gebunden.
Nach Rollback prüft SQL zusätzlich alle 1000 Source-Rows einschließlich Werte/
Payloadbytes; die separate Reader-/Config-/Indexprobe bestätigt den Nachbestand.
Tablevariableinhalte bleiben nach Rollback erhalten, wie
[Microsoft Learn](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/rollback-transaction-transact-sql?view=sql-server-ver17)
dokumentiert (abgerufen 2026-10-12); die tatsächlichen beiden Lifecycles belegen
hier zusätzlich vollständige OUTPUT- und Sourcekontrollen.

CPU/Reads/LogicalReads/Writes sind tatsächliche monotone Vorher-/Nachherdeltas
desselben vollständig gebundenen eigenen Session-/Request-/Startzeit-/Connection-/
DB-Requests. UTC-Elapsed umfasst BEGIN TRAN, UPDATEloop/OUTPUTbuffer und ROLLBACK.
Countergrenzen sind zusätzlich enthalten; UTC-/CPU-I/O-Grenzen sind nicht identisch.
Der coarse datetime-Requeststart ist allein Identität; UTC-Grenzen stammen vom
selben datetime2(7)-Takt. Vollständige Row-/Sourceprüfungen und JSON-Aufbereitung
folgen außerhalb des Messfensters. Fehlende Counter/Fields sind FAIL, keine Null.

Das ist ein Owner-UPDATEbatch einschließlich OUTPUT-/Transaktions-/Rollbackkosten.
Keine isolierte Indexwartung, Commitlatenz, individuelle Statementlatenz, reine
Log-/TempDB-/vollständige Workerkosten oder gesamter Indexnettonutzen.

## Zwei tatsächlich qualifizierte eigene Lifecycles

C1 zweimal bestanden, SQL 17.0.5005.3/EngineEdition3, eigenes bereits vorhandenes
Image 78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
vier CPU/sechs GiB und eigener Loopbackport. CL170/SIMPLE, Dateilimits 256/64 MB,
MAXDOP/PREVIEW_FEATURES beide 0 unverändert. Normalbudget 300 Sekunden,
anschließend gemeinsame Cleanupdeadline 60 Sekunden. Vollständige bytegenaue vier
Eigentumsmarker vor jedem effectful Statement, tatsächliches Clientende bekannt;
UNKNOWN false und keine Folgeclients bei UNKNOWN. Passwort allein über Umgebung.

Je Profil 46 vollständige 1000-Row-Source-/Reader-/Indexaufnahmen, Setupidempotenz,
tatsächliches DELETE Id1000 → 51003/FAIL_RESULT_CONTRACT → vollständiger Restore.
Negative OUTPUT-Kontrolle mutiert Id101/Ordinal1 nach Rollback zu Value0 und erreicht
ebenfalls exakt 51003/FAIL_RESULT_CONTRACT; vollständige separate Sourceprüfung
danach bestanden. Unveränderte Readerrechte CONNECT+Objekt-SELECT, keine Extra-Rolle.
Vier tatsächliche eigene Candidatebuilds und vier Drops pro Profil, jeweils durch
native vollständige Source-/Indexzustände getrennt bestätigt. Abschließend PK allein.

92 vollständige Sourceframes/92000 Rows, 58 positive Fensterframes einschließlich
zwei separater Kontrollen und vier native Negativframes vollständig an private
Rawframes/Recordhashes gebunden. Je Profil 93/
93 dokumentierte native Phasencalls. Markergebundener
SQLcleanup und neue unabhängige DB-/Namens-/CID-Abwesenheit bestanden;
Cleanup 12.831/13.383 Sekunden.

## Tatsächliche AB/BA-DML-Batchwerte

ElapsedUs in Mikrosekunden, CpuMs in Millisekunden; I/O-Werte sind Requestdeltas.
Alle Samples einschließlich Nullen/Ausreißern bleiben sichtbar. Kein p95/p99,
Durchsatz oder statistischer Nachweis aus sechs kleinen Batchsamples.

| Profil | Candidateindex | Metrik | n | Median | Min–Max | alle Samples |
|---|---|---|---:|---:|---|---|
| 1 | abwesend | CpuMs | 6 | 6.0 | 5–7 | 7, 6, 5, 6, 7, 5 |
| 1 | abwesend | ElapsedUs | 6 | 6202.0 | 4090–8179 | 8173, 8179, 8176, 4090, 4121, 4231 |
| 1 | abwesend | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 1 | abwesend | LogicalReads | 6 | 6363.0 | 6363–6363 | 6363, 6363, 6363, 6363, 6363, 6363 |
| 1 | abwesend | Writes | 6 | 13.0 | 2–18 | 16, 18, 9, 17, 2, 10 |
| 1 | vorhanden | CpuMs | 6 | 12.5 | 12–22 | 13, 13, 12, 12, 12, 22 |
| 1 | vorhanden | ElapsedUs | 6 | 16353.0 | 12257–35212 | 35212, 16406, 16300, 12257, 12280, 24446 |
| 1 | vorhanden | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 1 | vorhanden | LogicalReads | 6 | 19367.5 | 19367–19370 | 19370, 19367, 19367, 19370, 19367, 19368 |
| 1 | vorhanden | Writes | 6 | 9.5 | 3–16 | 10, 16, 9, 16, 3, 7 |
| 2 | abwesend | CpuMs | 6 | 6.0 | 6–7 | 6, 6, 7, 6, 6, 7 |
| 2 | abwesend | ElapsedUs | 6 | 8162.0 | 4083–8253 | 8253, 8184, 8183, 8141, 4083, 4318 |
| 2 | abwesend | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 2 | abwesend | LogicalReads | 6 | 6363.0 | 6363–6363 | 6363, 6363, 6363, 6363, 6363, 6363 |
| 2 | abwesend | Writes | 6 | 13.0 | 2–18 | 16, 18, 9, 17, 2, 10 |
| 2 | vorhanden | CpuMs | 6 | 14.0 | 13–44 | 13, 14, 14, 17, 13, 44 |
| 2 | vorhanden | ElapsedUs | 6 | 16359.5 | 16327–49241 | 16330, 16337, 16327, 20738, 16382, 49241 |
| 2 | vorhanden | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 2 | vorhanden | LogicalReads | 6 | 19367.5 | 19367–19370 | 19370, 19367, 19367, 19370, 19367, 19368 |
| 2 | vorhanden | Writes | 6 | 9.5 | 3–18 | 10, 16, 9, 18, 3, 5 |

## Getrennte AA-Kontrollpaare

Beide AA-Slots ohne Candidateindex. Ihre Samples werden weder AB/BA zugeschlagen
noch als nachträgliche Baselinekorrektur genutzt.

| Profil | AA-Slot | Metrik | n | Median | Min–Max | alle Samples |
|---|---:|---|---:|---:|---|---|
| 1 | 1 | CpuMs | 3 | 6 | 5–15 | 5, 15, 6 |
| 1 | 1 | ElapsedUs | 3 | 4154 | 4034–16345 | 4034, 16345, 4154 |
| 1 | 1 | LogicalReads | 3 | 6363 | 6363–6366 | 6363, 6363, 6366 |
| 1 | 2 | CpuMs | 3 | 8 | 6–8 | 8, 8, 6 |
| 1 | 2 | ElapsedUs | 3 | 8175 | 4099–8325 | 8175, 8325, 4099 |
| 1 | 2 | LogicalReads | 3 | 6366 | 6363–6366 | 6366, 6366, 6363 |
| 2 | 1 | CpuMs | 3 | 6 | 6–6 | 6, 6, 6 |
| 2 | 1 | ElapsedUs | 3 | 4283 | 4083–35171 | 4083, 35171, 4283 |
| 2 | 1 | LogicalReads | 3 | 6363 | 6363–6366 | 6363, 6363, 6366 |
| 2 | 2 | CpuMs | 3 | 7 | 6–8 | 7, 6, 8 |
| 2 | 2 | ElapsedUs | 3 | 8278 | 8168–8300 | 8278, 8168, 8300 |
| 2 | 2 | LogicalReads | 3 | 6366 | 6363–6366 | 6366, 6366, 6363 |

## Enger Review und gebundene Quellen

Keine konkreten P1/P2 im unabhängigen neuen Mutations-/Rollback-/Indexzustandsdelta;
Reviewer führt keine Tests oder Runtime aus. Acht reine Methoden mit Gegenfällen
zu Transaktionsdepth, bool-/Floataliasen, fehlenden Feldern, ordinalfalschen Digests,
unveränderten statt tatsächlich inkrementierten Werten und vollständigen Counter-/
Transport-/Populationbindungen bestanden. Keine Reviewkette, keine Wiederholung
unveränderter früherer nativer Pläne oder Readerfenster. Sechs kohärente Kandidaten
je Schnitt autorisiert; C1 genügte, historische frühere FAILs bleiben erhalten.

Ausgewählte Ausführungsquellen vor jedem Lauf gehasht und nach beiden Lifecycles
unverändert geprüft; keine vollständige transitive Importattestation:

| Quelle | SHA256 |
|---|---|
| `Runtime/DGN010_DML/sources/10_Setup.sql` | `9a462b1e805711d6254105ec5d84966943e6547703ab458386b89bff7f06ea47` |
| `Runtime/DGN010_DML/sources/20_Probe.sql` | `5b5a52e1059beeb053d565a9310a0a254c6d44b75164caa3880e1ca16ea8c862` |
| `Runtime/DGN010_DML/sources/50_Window.sql` | `ec49cd18e715a86116b82829e03cabd946df5c5634958c70b7044151979ccb35` |
| `Runtime/DGN010_DML/sources/90_Cleanup.sql` | `129894ffc2a7eea35f5c26bbe40d0b328674329e344e72929922abfa029c1b84` |
| `Runtime/DGN010_DML/sources/guard.sql` | `69ab06578c30d17432bc335b7c5ec399ab1d137d1260de016e65c139f881a9e2` |
| `Runtime/DGN010_DML/qualify.py` | `accaf3b69882c25b15633a2e95083cf8ee2478ad912d5e939d047cd8b4470a40` |
| `Runtime/DGN010_DML/probe.py` | `53a59167e0eea394511097840a2eb35e16720534fc3d38b78652ee813f1ae9c7` |
| `Runtime/DGN010_DML/source_evidence.py` | `b51a7d2a65eae1a12561b00bed4e962a88a0abdf47a8d5ee58cecf4b0a461211` |
| `Runtime/DGN010_DML/measurement.py` | `052be4a1e3277836ef2ab4e6911c50b263469ae8ef9256e54248d3860cd3c74e` |

Diese Batchwerte ergänzen die Adviceprüfung um tatsächliche DML-Folgen in einem
engen Rollbackszenario. Ungezwungener SELECTvergleich ohne/mit Index, Nettonutzen,
Commit-/Build-/reine Index-/vollständige Workerkosten, öffentliche FWK-/Versions-/
Recoveryqualifikation und vollständige TP-PERF-/TSK-011-/Modulabnahme bleiben offen.
DGN-010 PROPOSED. Kein Modell-/Cloud-/ONNX-/Preview-/roter Hosteffekt oder andere
Repositoryänderung; Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.

Aktuelle Head-/Main-Gates, PR/Integration, ganze Treeübernahme, FF-Sync und eigener
lokaler/Remote-Branchcleanup folgen vor Abschluss. Nächster begrenzter kanonischer
Schritt ergänzt DGN-010 durch einen ungezwungenen SELECTvergleich ohne/mit Index.
