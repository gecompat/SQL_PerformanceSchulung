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
