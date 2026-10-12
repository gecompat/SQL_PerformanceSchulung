# DGN-010 – begrenzte private Actual-Planqualifikation

Stand: 2026-10-12. TSK-011/CUR-021; DGN-010 weiterhin PROPOSED.
Gebundener Teilnachweis, kein öffentliches FWK-Demopaket oder voller TP-PERF-PASS.
Basis e7c407fe957245bcc83052ce266748fc19b1aa62.

## Ausgangsstand und konkreter Umfang

Die [frühere Ergebnis-/Storagevorbereitung](SQL_SERVER_2025_AI_INDEX_HYPOTHESIS_REVIEW.md)
belegte vollständige Rowsets und zusätzlichen Indexspeicher, noch keinen Actual-Plan.
Dieser neue Schnitt ergänzt ausschließlich repräsentative tatsächliche Ownerpläne
vor Build, mit Candidateindex und nach seinem Drop. Eine synthetische Advicefixture
bleibt eine Hypothese; es wurde kein Modell oder generiertes SQL aufgerufen.

[PR190](https://github.com/gecompat/SQL_PerformanceSchulung/pull/190) vollständig
abgeschlossen: Head 71aa155ad6e86fdd4490534e22969ddaf92f2089, acht Head-Workflows PASS;
Squash e7c407fe957245bcc83052ce266748fc19b1aa62, sechs Main-Workflows PASS;
ganzer Tree 95c407b5d74cf93fd7db942731385732dcc9b738 exakt übernommen,
FF-Synchronisierung/sauberer Stand und eigener lokaler/Remote-Branchcleanup bestätigt.

## Zwei tatsächliche lokale Lifecycles

C1 zweimal auf jeweils neuer eigener Podmaninstanz, festes bereits vorhandenes
Image 78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726;
SQL meldete 17.0.5005.3, EngineEdition 3. Vier CPU/sechs GiB, eigener Loopbackport,
300 Sekunden gemeinsames Laufbudget und anschließend insgesamt 60 Sekunden Cleanup.
SQLCMDPASSWORD ausschließlich über Umgebung; bekanntes tatsächliches Clientende
bleibt vor jedem Folgecall Voraussetzung. Keine weiteren Clients nach UNKNOWN.

Eigene Datenbank mit CL170/SIMPLE und 256-/64-MB-Dateilimits, MAXDOP/PREVIEW_FEATURES
beide 0. Keine Änderung dieser beiden Optionen. 1000 eindeutige IDs 1–1000,
Value=Id×3 und vollständiger 100-Byte-F-Payload. Setupidempotenz und acht vollständige
Sourceaufnahmen je Lifecycle, insgesamt 16000 Rows, mit nativen Frame-/Recordbindungen.
Tatsächliches DELETE von Id1000 verursacht exakt 51003/FAIL_RESULT_CONTRACT;
Setup stellt danach die vollständige Source wieder her. Configoracle bleibt erfüllt.

Ein WITHOUT LOGIN Reader besitzt unverändert CONNECT und ausschließlich Objekt-SELECT,
keine zusätzliche Rollenmitgliedschaft. Er führt in jeder Sourceaufnahme die feste
Query mit separaten int-Parametern 101/110 aus. Counts, vollständige Rowwerte und
fehlende IDs sind echte SQL-Oracles; REVERT schützt Erfolg und Fehler. Die drei
zusätzlichen Actual-Pläne werden unter Owner aufgenommen und qualifizieren keine
Readerpläne, Serverlogins oder minimalen Teilnehmerrollen.

Nur festes eigenes NONCLUSTERED-DDL mit MAXDOP1 erstellt den ID-INCLUDE(Value,Payload)-
Index; danach erfolgt sein tatsächlicher Drop. Drei vollständige native Ownerquery-
Rowsets je Lifecycle liefern IDs101–110, Value=Id×3 und vollständigen F-Payload.
XMLs binden Namespace/festen Build, exaktes Statement, eigenen DB-/Schema-/Tabellen-/
Indexbezug und tatsächliche Root-/Source-Counters mit je zehn Rows. Insgesamt sechs
Rawpläne exakt gegen die privaten vollständigen Records gebunden.

## Beobachtete repräsentative Pläne und Storage

Die Pagewerte gehören zum genannten tatsächlichen Index aus sys.dm_db_partition_stats.
Sie sind keine Query-I/O oder RAMgröße. Die 18 PK-Seiten bleiben auch während des
Candidateindex bestehen; seine 17 used pages sind zusätzlicher Indexspeicher.

| Lauf | Zustand | Tatsächlicher Operator | Tatsächlich verwendeter Index | Actual Rows | Indexrows | Used / reserved pages |
|---|---|---|---|---|---|---|
| 1 | baseline | Clustered Index Seek | DGN010_OwnPK | 10 | 1000 | 18 / 33 |
| 1 | candidate | Index Seek | DGN010_OwnCandidate | 10 | 1000 | 17 / 33 |
| 1 | post_drop | Clustered Index Seek | DGN010_OwnPK | 10 | 1000 | 18 / 33 |
| 2 | baseline | Clustered Index Seek | DGN010_OwnPK | 10 | 1000 | 18 / 33 |
| 2 | candidate | Index Seek | DGN010_OwnCandidate | 10 | 1000 | 17 / 33 |
| 2 | post_drop | Clustered Index Seek | DGN010_OwnPK | 10 | 1000 | 18 / 33 |

In beiden Lifecycles wechselt der tatsächliche Zugriff zum Candidateindex und
kehrt nach Drop zum Clustered-PK zurück. Beide Strukturen liefern denselben
vollständigen Rowset. Der Planwechsel und 17 zusätzliche Indexseiten belegen
allein weder einen Laufzeitgewinn noch eine Performancewiderlegung der Advicefixture.

Roher Plan-DOP 0 bleibt 0, NonParallelPlanReason=MaxDOPSetToOne.
In diesen sechs Plänen sind SerialRequiredMemory, SerialDesiredMemory, GrantedMemory
und MaxUsedMemory tatsächlich 0. RequiredMemory, DesiredMemory, RequestedMemory,
GrantWaitTime, MaxQueryMemory und LastRequestedMemory fehlen und bleiben None;
sie werden nicht als Nullmessung interpretiert. Waits/Warnings NOT_CAPTURED,
kein abgeleiteter Spill-/Waitfreiheitclaim. Nur repräsentative Ownerstatements,
keine vollständige Worker-/Last-/Batchqualifikation.

## Quellenreview, Prüfung und Cleanup

Ein Owner und ein enger unabhängiger Review der neuen SQL-/Reader-/Plan-/Adapter-
Risiken. Zwei P2 vor Native-Admission geschlossen: SELECT-Phasen direkt ausführen,
PRINT-Transformation nur für Cleanup; vollständige rawDemo/Run/Target- und bestehende
Viermarkerbindung vor erster Mutation, zusätzlich exakt LOCAL für Setup.
Keine neue vollständige Analyse der unveränderten Provider-/Endstatusbasis,
keine Reviewer-Tests oder Runtime. Fünf reine Testmethoden mit elf Source-, neun
Planidentitäts-/Counter- und neun Raw-/Query-/XML-Gegenfällen sowie positiven
Indexzuständen bestanden. Zwei anfängliche lokale Testtreiberfehler (Importpfad,
zu enger erwarteter Exceptiontyp) vor Admission korrigiert; keine SQL-Effekte dabei.

Alle 21 dokumentierten nativen Phasencalls je Lifecycle abgeschlossen. Vollständige
bytegenaue DATALENGTH-/VARBINARY-Bindung der vier Marker vor Mutation/DB-Abbau.
SQL-Cleanup und unabhängige DB-Abwesenheit, danach Owner-/Image-/CID-/Ressourcenbindung,
Entfernung nur des eigenen Containers und getrennte Namens-/CID-Abwesenheit bestanden.
Beide Cleanupfolgen innerhalb desselben 60-Sekunden-Budgets. Private Quellen,
Rawdaten und aktuelle ausgewählte Quellen-/Recordbindungen bleiben ignoriert;
keine behauptete vollständige transitive Import-DAG-Bindung.

Gebundene aktuelle UTF-8-Quellen:

| Quelle | SHA256 |
|---|---|
| private qualify.py | 4685A1ED99C88E0D7C016B770D0DCCD0F89C41D60D7AF2E9CC9FF715E9DA727D |
| private probe.py | 0418B5B3210BD84AFFD0C71F755D45ACBB46C7463A164E28EB9E937BF09ED62E |
| private plans.py | 661FC0A5BC88323CD6856DBD066246AF606F07B903120A8CB7F94C732F2CBC12 |
| private 10_Setup.sql | 9A462B1E805711D6254105EC5D84966943E6547703AB458386B89BFF7F06EA47 |

## Offene Grenzen und Integration

Keine ausgewertete Query-Reads-/CPU-/Elapsed- oder AB-/BA-/AA-Messung, keine
Insert-/Updatekosten oder Effektseparation. Die zusätzliche Indexstruktur ist
kein Performanceurteil. Voller TP-PERF-/FWK-/Demo-/Modulnachweis, ältere Engines,
öffentliche Versions-/Negativ-/Rollenqualifikation und Teilnehmererprobung offen.
TSK-011 insgesamt nicht abgeschlossen; DGN-010 bleibt PROPOSED.

Aktuelle Head-/Main-Gates, PR/Integration/volle Treeübernahme, FF-Synchronisierung
und eigener lokaler/Remote-Branchcleanup folgen vor Abschluss. Keine Cloud-/Bezahl-/
Modell-/ONNX-/Preview-/roten Hosteffekte oder andere Repositoryänderung.
Sechs kohärente Test-/Korrekturkandidaten je lokalem Schnitt sind autorisiert;
C1 mit zwei erforderlichen stabilen positiven Lifecycles bestanden, keine
unveränderten grünen Zusatzläufe. Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.
