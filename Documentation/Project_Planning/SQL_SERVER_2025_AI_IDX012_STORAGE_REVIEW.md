# IDX-012 – Begrenzte DB-Speicheraufnahme

Stand: 2026-10-11. Teilnachweis zu TSK-006/DEC-074, keine Demo- oder
TP-PERF-Freigabe. Die weitere lokale Entwicklungswelle ist ausdrücklich
autorisiert; Cloud-/Bezahl-, ONNX- und rote Hosteffekte bleiben außerhalb.
Der [kanonische Ausführungsstand](CURRENT_EXECUTION_STATUS.md) führt den Auftrag.

## Fester Umfang und Admission

Ein Implementierungsverantwortlicher, ein unabhängiger Review der neuen
Katalog-/Parser-/Effektgrenzen. Neuer eigener Parent unter dem ignorierten
Runtime/IDX012_STORAGE: genau ein stabiler Kandidat und höchstens zwei serielle
eigene Container für zwei positive Lifecycles; keine Korrekturwelle. Bei FAIL
anhalten, Recovery und eigenen Cleanup abschließen, tatsächlichen Befund erhalten.
Kein Zurücksetzen oder Wiederverwenden früherer geschlossener Budgets.

Unveränderliches eigenes lokales Image, tatsächlicher SQL-17.0.5005.3-Build,
vier CPUs/sechs GiB, eigene volle Marker, 999 VECTOR(3)-Rows mit begrenztem
transaktionalem INSERT auf 1000 Rows. Ausschließlich eigene Preview/MAXDOP-
Optionen mit persistierten Baselines und tatsächlichen Originalrestores.
Kein Pull, Cacheflush, Modellaufruf oder fremder Container. Normalbudget 300 s
einschließlich Startup, SQL-Recovery 20 s innerhalb gemeinsamer 60 s ab erstem
Restore; tatsächliche vollständige CID-/Image-/Namens-/Label-/Ressourcenbindung
und unabhängige DB-/Containerabwesenheit bleiben Pflicht.

## Methode und Aussagegrenzen

Der neue explizite Controlleraufruf --mode drop-rebuild --capture-storage
erfasst über drei neue read-only Clients den vollständigen begrenzten eigenen
DB-Katalog: BASELINE nach Aufbau, INDEXED nach DML-Grenzen/erstem Indexbuild,
REBUILT nach dem geprüften Drop-/Commit-/Rebuild und neuer Quellenkontrolle.
Default und früherer DML-Modus erhalten keinen zusätzlichen SQL-Aufruf.

22_Storage.sql prüft vollständige Marker, persistierte Baselines, beide aktuellen
Optionen und feste volle Stagewerte vor Aufnahme. Tatsächliche Quellenzahl 999,
Indexcount 0/1/1 und Transaktionswerte 0/0 werden vor JSON erfasst. Alle zwei
Dateien, sämtliche sys.internal_tables und sys.dm_db_partition_stats der eigenen
DB werden aufgenommen; bei mehr als 64 internen Tabellen, 128 Partitionen oder
120000 UTF-16-Outputbytes FAIL statt Abschneiden. Namen/Hostpfade werden nicht
ausgegeben. Dateigrößen bleiben zusätzlich im bestehenden Setup begrenzt.

Der Parser bindet DB-ID, Namen, vollen Token und Fixtureobjekt exakt, prüft
Katalogabdeckung, eindeutige IDs, strikt tatsächliche Integer und dokumentierte
Seitenbilanzen. Nullable FILEPROPERTY-Werte bleiben null; fehlende Felder sind
FAIL und werden nicht zu null oder null Seiten umgedeutet. Seiten haben 8192
Bytes. DMV-row_count bleibt ausdrücklich APPROXIMATE und ersetzt nicht die
tatsächliche Quellenzahl aus der Tabelle oder die vollständige Quellenprüfung.

Dies sind DB-weite Punktaufnahmen. Die Spanne vor dem ersten Index enthält auch
vier zurückgerollte DML-Kontrollen; die Rebuildspanne enthält Drop und eine
committete Änderung. Ein Delta ist deshalb keine isolierte Indexbaukostenzahl.
Interne parent_id/parent_minor_id werden roh erhalten; ihre Zuordnung beweist
keine vollständige DiskANN-Storageattribuierung. Indexstorageattribuierung
NOT_ESTABLISHED; Writes-/TempDB-/Worker-Kosten NOT_CAPTURED. Freshness bleibt
OBSERVED_AFTER_REBUILD_ONLY, Generation UNKNOWN und Runtimequalifikation
NOT_ESTABLISHED. Minimalrollen, Hard-Abort und weitere Versionsläufe offen.

## Prüfung und Aufwand

Vor Runtime: 16 Controller-, zunächst zwölf Speicherparser- und zehn Selektorgegenproben
PASS. Die Gegenproben unterscheiden null/fehlend/null Seiten, falsche Eigentums-
und Stagebindung, Transaktions-/Indexcounts, doppelte/unvollständige Kataloge,
überzählige Rows, Seitenbilanzfehler und tatsächliche statt coerzierte Integer.
Die bereits grünen DML-/Lifecycle-Parser wurden nicht verändert oder lokal
wiederholt. Der unabhängige Review fand eine P2-Abdeckungslücke: Caps allein
erkannten fehlende einzelne Katalogrows und eine fehlende eigene Fixturepartition
nicht. Vor erster Admission wurden tatsächliche drei Katalogcounts vor JSON
aufgenommen und Parserlängen exakt daran gebunden; genau eine eigene unpartitionierte
Fixture-PK (object_id, index_id=1, partition_number=1) ist Pflicht. Systempartitionen
werden zusätzlich erhalten. Die 13 aktualisierten Speichergegenproben bestanden;
unveränderte Controller-/Selektortests wurden nicht wiederholt. Enge unabhängige
Closure ist bestanden, keine weiteren P1/P2; kein Runtimekandidat wurde bis
zu diesem Quellencheckpoint verbraucht. Der Reviewer führte keine Runtime aus.

Geprüfte Originalbytes vor Admission (SHA256):

| Quelle | Hash |
|---|---|
| 22_Storage.sql | 915D7EFFD20D1BDB686736BC8E49CE38D222CD0FD444E53246934765DB8713E9 |
| storage_evidence.py | 0C715B7F6E5F939329426B9BAAC54376073A3F5D10CF1CE66EC0189ED34AB63B |
| run_profile.py | 8ED9B9AA426A6462D70D1CC165D664492291CBDD25281196986ACEE3E9EC9940 |
| lokaler qualify_storage.py | B20CA3B0A486453610A6FD3FBC6C62C0C669E57736EE8946D96294BABA6B17DF |

Öffentlicher tatsächlicher Importpfad und 19 gemeinsame Kandidatenquellen
sind vor Admission geprüft.

## Erster tatsächlicher Runtimecheckpoint: FAIL

Der einzige zugelassene Kandidat erreichte am 11.10.2026 mit Token
0B6514D624F84921 und tatsächlichem 17.0.5005.3-Build den vollständigen Baseline-
Aufbau und alle bisherigen Snapshots. 22_Storage.sql lieferte an seinem ersten
Grenzguard Msg 51003/State 1/Zeile 59. Kein vollständiger STORAGE-Datensatz wurde
ausgegeben; welche tatsächliche Guardgröße abwich, ist damit UNKNOWN. Es wurde
kein Index gebaut, keine neue DML-/Suchfolge erreicht. Die Fehlerursache ist
nicht durch die vorherigen positiven Rebuildläufe bewiesen.

Der Controller meldet FAIL_EXECUTION; der Parent PUBLIC_CONTRACT_NOT_ESTABLISHED.
Tatsächliche Originalrestores Preview/MAXDOP 0/0, unabhängige Attestation vor
markergebundenem Drop, separate DB-/eigene CID-/Namensabwesenheit bestanden.
Gesamter Cleanup 12,353 s ab erstem Restore. Admission geschlossen mit FAIL;
kein zweiter Lifecycle und keine Korrekturwelle in diesem Budget. Rohoutput und
vollständige Quellenbindungen bleiben ausschließlich im ignorierten lokalen
Nachweisordner. Speicheraufnahme und ihre Runtimequalifikation bleiben offen.

## Getrennte Capturefolge: vorbereitet, noch nicht ausgeführt

Die weitere lokale Wellenfreigabe gilt auch hier. Vor einer neuen Admission
wird dieser FAIL-Checkpoint über PR vollständig integriert, synchronisiert und
bereinigt. Ein neuer eigener Parent Runtime/IDX012_STORAGE_CAPTURE gestattet
genau einen stabilen Kandidaten/maximal zwei eigene serielle Container, keine
Korrekturwelle, dieselben Effekt-/Versions-/Ressourcen-/Recoverygrenzen. Der
geschlossene erste Ledger bleibt erhalten und wird nicht wiederverwendet.

Der vorbereitete neue SQL-Input erfasst @@TRANCOUNT/XACT_STATE vor allen
Katalogsubqueries in einer getrennten Deklaration. Bisher standen sie in
derselben Deklaration wie subquerygestützte Counts; ein dadurch beobachteter
Statement-Transaktionsstatus ist nur eine Hypothese. Zusätzlich werden alle
tatsächlich erfassten Guardcounts/Transaktionswerte als fest gebundener
STORAGE_GUARD-Datensatz vor dem unveränderten FAIL-Guard ausgegeben. Dieser
Diagnosedatensatz ist kein vollständiger STORAGE-Erfolg und schwächt keine
bestehende Assertion ab.

Neuer 22_Storage.sql SHA256
FCD650AB7FF643BF88C8C13B351144BAB69FDCC18A884DAAFB9BFCA6CECAB068;
neuer lokaler qualify_capture.py SHA256
20F4B09BAE3E034579F2F11230B8B8040E5304EF961EE748F89FC2DA842E0DFF.
Controller/Storageparser bleiben auf ihren oben geprüften Bytes unverändert.
Der enge unabhängige Review dieses tatsächlichen neuen Inputs ist bestanden:
keine P1/P2; beide neuen Quellenhashes stimmen, übrige Controller-/Parserbytes
unverändert. Der Consumer akzeptiert ausschließlich kind=STORAGE; Diagnose-
Guardrecord ersetzt keine Aufnahme. Keine zusätzliche Runtime durch den Reviewer.
Keine erneute unveränderte Runtime, kein neuer Runtimeerfolg behauptet.

## Tatsächliche Capturefolge und neue Kataloggrenze

PR175 ist vollständig integriert: Head 7a27ba984834a8d75f5d3d7a39db178c6f2fb29b
gegen Basis 2d8a6005a9300094af573ae05e30b9dea69192e6, alle 13 Headchecks SUCCESS;
Squash 36c2d7aacd4a27185968128f72ae4a8164e120b1, alle sieben ausgewählten
Main-Workflows einschließlich KI-Runtime/Cleanup SUCCESS. Vollständiger Tree
ee6fb8ab17ed0e1de9cc017d95523af66f2a9617 identisch, main synchronisiert und
eigener Storage-Branch lokal/remote entfernt. Danach tatsächlicher öffentlicher
Pfad-/Originalbyteschluss für die Capturefolge.

Token DCC9B668B1234055, tatsächlich 17.0.5005.3: erneut FAIL vor Indexbau,
diesmal mit vollständigem tatsächlichem STORAGE_GUARD. Baseline: 999 Rows,
Indexcount 0, Transaktion 0/0, zwei Dateien, 43 interne Tabellen, 199 Partitionen.
199 überschreitet das angesetzte Limit 128. Alle übrigen Guardwerte stimmen.
Der erste historische FAIL enthielt keine Counts; seine einzelne Ursache bleibt
unbewiesen. Die Transaktionshypothese ist kein nachgewiesener Erstfehler.

Tatsächliche Originalrestores 0/0, unabhängige Attestation/DB-/eigene CID-/
Namensabwesenheit bestanden; gesamter Cleanup 12,658 s. Captureledger geschlossen
FAIL, kein zweiter Lauf/keine Korrektur darin. Keine vollständige STORAGE-Aufnahme
oder Parser-/Index-/Rebuild-Runtimeattestation aus dieser Folge.

Die neue, weiterhin ausdrücklich autorisierte lokale Katalogfolge begrenzt die
vollständige DB-Aufnahme auf 512 Partitionen und unverändert 120000 UTF-16-Outputbytes; 64
interne Tabellen, zwei Dateien, exakte Counts/Fixturepartition und sämtliche
anderen Guards bleiben erhalten. Die tatsächlich beobachteten 199 Partitionen
werden vollständig aufgenommen; keine Filterung oder Trunkierung. Der unabhängige Review wies die vorbereitete Erweiterung auf 400000 UTF-16-Bytes
als P2 zurück: der native Client -w 65535 würde einen solchen Scalar umbrechen.
Deshalb bleibt das ursprüngliche Scalarmaximum 120000 UTF-16-Bytes (höchstens
60000 Codeunits) erhalten; gleichzeitig müssen Count- und Outputgrenze erfüllt
sein. Größere Aufnahmen bleiben FAIL ohne Trunkierung. Keine neue Blockreassemblierung
oder Änderung der Clientbreite erforderlich. Der Collector bleibt unverändert.
Die DB-/Dateimaxima, synthetischen Rows, Optionen und Zeitgrenzen ändern sich
nicht. Es wird kein externer Datenbestand oder neuer Hosteffekt aufgenommen.

Neuer Parent/Ledger Runtime/IDX012_STORAGE_CATALOG: genau ein stabiler Kandidat,
maximal zwei eigene serielle Container, keine Korrekturwelle. Admission erst
nach engem unabhängigem Quellenreview und aktuellem öffentlichen Pfad-/Hashschluss;
beide bisherigen FAIL-Ledger bleiben geschlossen. Diese Katalogfolge gehört zum
laufenden zusammenhängenden Capture-/Grenzenschnitt; sein vollständiger PR-/
Integrationsabschluss bleibt Pflicht. 14 aktualisierte Storagegegenproben PASS,
darunter vollständige 512-Partitionen-Aufnahme mit eigener Fixture und Abweisung
der 513. Partition. Unveränderte Controller-/Selektortests nicht wiederholt.

Vorbereitete neue Originalbytes (SHA256): 22_Storage.sql
A206AEBAC505D72C4DC620091254A3083B70D61DE916126EA07BA3ED417A2D7C;
storage_evidence.py
1117135BC156B325EFA265A61B5F1777983EEA30E89AFE9D3A1D2B6D38B253C4;
lokaler qualify_catalog.py
F0D3C2E3BF87BC9FE56842324E7169F12659776D1C207B37799C950F950303D5.
Controller bleibt unverändert auf 8ED9B9AA426A6462D70D1CC165D664492291CBDD25281196986ACEE3E9EC9940.

Die enge unabhängige Closure des Transport-P2 ist bestanden: alle aktuellen
Quellenhashes stimmen, keine weiteren Befunde. Das Scalarmaximum schützt die
unveränderte Clientbreite; keine größere Aufnahme wird still abgeschnitten.
Keine Runtime durch den Reviewer. Erst danach Admission der Katalogfolge.

## Katalogfolge: zwei vollständige positive Lifecycles

Nach tatsächlichem öffentlichen Import-/Pfad-/Hashschluss der 19 gemeinsamen
Kandidatenquellen bestanden beide Admissionen des einzigen stabilen Kandidaten.
Die Codebytes entsprechen exakt den oben zuletzt unabhängig geprüften Quellen.
Der Ledger ist mit zwei geschlossenen Lifecycles ohne Fehler ausgeschöpft;
keine Korrekturwelle oder weitere Admission.

| Beobachtung | Lauf 1 | Lauf 2 |
|---|---|---|
| vollständiger eigener Token | 2D00C5B617964E25 | B249FF1FEB194EC3 |
| tatsächlicher Build | 17.0.5005.3 | 17.0.5005.3 |
| Ausgang | WARN_OPTIONAL_EVIDENCE_SKIPPED | WARN_OPTIONAL_EVIDENCE_SKIPPED |
| erster Indexbuild / Rebuild | 896,459 / 996,664 ms | 944,009 / 1038,306 ms |
| tatsächlich restaurierte Originaloptionen Preview/MAXDOP | 0/0 | 0/0 |
| gesamter Cleanup ab erstem Restore | 12,686 s | 12,624 s |
| unabhängige DB-/eigene CID-/Namensabwesenheit | bestanden | bestanden |

Alle drei neuen Storageclients liefern tatsächliche 999 SourceRows, Indexcount
0/1/1 und vor JSON erfasste Transaktionswerte 0/0. Vollständige Counts/Arrays,
einzigartige IDs, Fixture-PK-Partition, Numerik/Seitenbilanzen und sämtliche
Marker-/Baseline-/Options-/Host-/Quellensnapshots bestanden. Beide vollständigen
Katalogmengen wurden ohne Filterung und ohne Wrapped-JSON-Decoder transportiert:

| DB-weite Aufnahme, beide Läufe | BASELINE | INDEXED | REBUILT |
|---|---:|---:|---:|
| interne Tabellen / Partitionen | 43 / 199 | 45 / 203 | 45 / 203 |
| Summe verwendeter Partitionsseiten | 369 | 427 | 430 |
| Summe reservierter Partitionsseiten | 487 | 607 | 615 |
| Fixture-PK verwendet / reserviert | 7 / 9 | 7 / 9 | 7 / 9 |
| data-Dateigröße / FILEPROPERTY SpaceUsed, Seiten | 1024 / 496 | 1024 / 616 | 1024 / 624 |
| log-Dateigröße / FILEPROPERTY SpaceUsed, Seiten, Lauf 1 | 1024 / 119 | 1024 / 204 | 1024 / 279 |
| log-Dateigröße / FILEPROPERTY SpaceUsed, Seiten, Lauf 2 | 1024 / 120 | 1024 / 205 | 1024 / 279 |
| vollständiger Scalar, Codeunits / UTF-16-Bytes | 51219 / 102438 | 52454 / 104908 | 52454 / 104908 |

Damit liegen alle tatsächlichen Scalars unter 60000 Codeunits/120000 UTF-16-
Bytes und der Clientbreite 65535. Die Tabelle enthält rohe DB-/Katalogpunkte,
keine isolierte Indexstorage- oder Buildkostenrechnung. FILEPROPERTY-Werte
werden nicht in aktive Logbelegung oder tatsächliche Datei-Writes umgedeutet.
DMV-row_count ist auch bei hier tatsächlich 999 ausdrücklich APPROXIMATE;
die unabhängige vollständige Quellenprüfung bleibt das Ergebnisoracle.

Beide Läufe bestanden zusätzlich die vier positiven/vier tatsächlich 42231-
verweigerten DML-Kontrollen, tatsächlichen eigenen Drop, Commit allein Id 999,
fünf distanzgeprüfte Suchkontrollen und neue vollständige Quellen-/Indexmetadaten.
Id 999 bleibt neuer Top-1 mit Distanz null; beide ANN-Aufnahmen Recall@5 1,
übrige 998 Vektortexte unverändert. Freshness OBSERVED_AFTER_REBUILD_ONLY,
Generation UNKNOWN und Runtimequalifikation NOT_ESTABLISHED bleiben bestehen.

Die beiden vorherigen FAIL-Ledger und der zurückgewiesene Transportentwurf
bleiben erhalten. Vollständige Writes-/TempDB-/Worker-/Plan-/Minimalrollen-/
Hard-Abort-/Versions-/TP-PERF-Abnahme offen. Kein neuer Provider-/Modellaufruf.
Head-/Main-Gates, vollständige Treebindung, Synchronisierung und eigener
Branchabbau sind zusätzliche Integrationspflichten dieses Ergebnisstands.

Der vorhandene statische KI-Job erhält genau einen zusätzlichen reinen Test.
Runtimejobdefinition bleibt unverändert. Die konservative vorhandene Auswahl
führt weiterhin die acht freigegebenen Offline-Demos auf drei Versionen je
zweimal aus, am Head und auf main; sie attestiert diesen IDX-012-Prototyp nicht.
Der neue lokale Runtimeumfang beträgt höchstens zwei eigene Lifecycles.
Keine Reviewkette oder wiederholte Vollanalyse; Modell-/Tokenverbrauch unbekannt.

## Primärquellen

Abruf 2026-10-11:

- [sys.dm_db_partition_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-partition-stats-transact-sql?view=sql-server-ver17): Näherungs-row_count und Bilanz der verwendeten Seiten.
- [sys.internal_tables](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-internal-tables-transact-sql?view=sql-server-ver17): vollständige interne Objekt- und Parentmetadaten.
- [sys.database_files](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-files-transact-sql?view=sql-server-ver17): Dateigrößen in Seiten und FILEPROPERTY-Beispiel.

Diese Quellen ersetzen keine konkrete Runtimeattestation am festen Build.
