# IDX-012: eingeschränktes Ausführungsprofil mit tatsächlichen Rechtegegenproben

Stand: 2026-10-12. TSK-006/DEC-074; begrenzter Rollen-/Berechtigungsteil,
kein Manifest, Demo-Release oder vollständiger Runtime-/TP-PERF-Claim.
Die weitere lokale Wellenfreigabe und sechs Kandidaten je Schnitt stehen
im [Ausführungsstand](CURRENT_EXECUTION_STATUS.md).

## Methode und Effektgrenze

Der öffentliche Preflight prüft nach Versionsausschluss und vor der Host-DMV
VIEW SERVER PERFORMANCE STATE. Fehlt dieses Recht, liefert er SKIP_PERMISSION
mit MISSING_SERVER_PERFORMANCE_STATE; fehlendes DB-Erstellungsrecht erhält
MISSING_CREATE_DATABASE. Beide halten vor Setup an. 2019/2022 bleiben vor
diesen neuen Prüfungen SKIP_VERSION. Der übrige Controller/SQL-Pfad bleibt
unverändert; neue Rechte werden weder automatisch gewährt noch geraten.

Ein eigener frischer SQL-Login im neuen eigenen Container bekommt nur
CREATE ANY DATABASE und VIEW SERVER PERFORMANCE STATE; CONNECT SQL/public
bleiben normale Basis. Keine feste Serverrolle, CONTROL SERVER oder
ALTER ANY LOGIN. Frischer vollständiger Name/16-Byte-SID/Typ/Defaultdatabase
werden vor jeder Principaloperation tatsächlich geprüft; fremde Principals
oder zusätzliche Grants/Rollen werden abgewiesen. Secret ausschließlich ENV,
keine Passwortwerte in CLI/Quelldateien/Rohlog/PR. Der private feste
RoleFixture.sql erhält den generierten Secretwert nur durch native
SQLCMD-ENV-Substitution; die Quelldatei enthält lediglich den Platzhalter.

Vor dem positiven Lauf entzieht der Admin beide Rechte einzeln tatsächlich.
Je Negativfall: frischer öffentlicher Client ausschließlich PREFLIGHT/
SKIP_PERMISSION, kein Setup/SQL-Restoreclaim, tatsächliche neue read-only
DB-Abwesenheit; danach tatsächlicher Grantrestore und Login-Gegenprüfung.
Im aktuellen lokalen Split laufen DML, Drop/Commit, Beobachtung und Kosten-
frames im eingeschränkten Kontext. Genau die beiden CREATE VECTOR INDEX-
Aufrufe wechseln im festen nativen Input kurz in den Admin-Kontext; die
übrigen Clients authentifizieren unmittelbar als Operator. Nach Setup wird sein eigener
DB-Owner-SID durch eine neue Verbindung attestiert. Das eigene DB-Ownerrecht
ist Bestandteil dieses Setupmodells, kein behaupteter Verzicht auf DB-Rechte.

Originalrestores 0/0, neue markergebundene Dropattestation und neuer öffentlicher
DB-Abwesenheitsclient bleiben Pflicht. Admin entfernt anschließend nur den
vollständig gebundenen eigenen Login, wenn weder die eigene DB noch eine
weitere DB mit dessen SID vorhanden ist; neuer separater Client bestätigt
Principal-/SID-/DB-Abwesenheit. Vollständige eigene CID und Name werden
danach unabhängig abwesend geprüft. Admin wird für Fixture und dessen
Cleanup verwendet; kein stiller sa-Fallback im öffentlichen Demoablauf.
Bei unbestätigtem öffentlichem Clientende wird kein zusätzlicher SQL-Client
zum Principalcleanup gestartet: NOT_ESTABLISHED_CLIENT_END_UNKNOWN und
role_absent=false bleiben sichtbar, nur gebundener eigener Containerabbau.
Der öffentliche und der Rollenclaim bleiben FAIL.

Eigener unveränderlicher 17.0.5005.3-Container/4 CPUs/6 GiB, Preview/MAXDOP
nur eigene DB, 999–1000 VECTOR(3)-Rows; 300 s einschließlich Startup,
20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup ab erstem Restore,
einschließlich anschließendem Login- und Containercleanup. Keine Pulls,
Host-/Cloud-/ONNX-/Fremdrepositoryänderung. Kein absoluter Minimalitätsclaim:
das Profil belegt ausschließlich die unten attestierte Kontexttrennung;
aufgeteilte Setup-/Messrollen oder geringere DMV-Rechte bleiben gesondert.

## Gemeinsames Budget und Aufwand

Root einziger Implementer. Enger unabhängiger Review nur für Principal-/
SID-/Secret-/Authentifizierungsbindung, tatsächliche Rechtegegenproben und
eigenen Cleanup. Kein Vollreview unveränderter DML-/Kosten-/Quellenoracles.
Privater Parent/Ledger Runtime/IDX012_ROLES: sechs Kandidaten/zwölf eigene
serielle Container, pro stabiler Quelle zwei vollständige Rollenlifecycles.
Nach tatsächlichem geschlossenem FAIL nur mit geändertem Ausführungsinput
weiter; kein stilles Ledgerreset. Nach zwei stabilen erfüllten Lifecycles
keine zusätzlichen identischen grünen Zyklen. Vorige Ledger bleiben geschlossen.

Ein neuer Controllergegenfall zu SKIP_PERMISSION vor Setup/Recovery;
betroffene Controllertests, Datenschutz und aktuelle Head-/Main-Gates bleiben
erforderlich. Unveränderte Kosten-/Storage-/DML-/Selektortests nicht nochmals
lokal ausgeführt. Keine zusätzliche Workflowdefinition/Reviewkette.
Tatsächlicher Modell-/Tokenverbrauch unbekannt.
31 betroffene Controllergegenproben bestanden. Eine zusätzliche enge
synthetische Parent-Gegenprobe bestand: bei simuliertem PublicClientEndUnknown
startet der tatsächliche Parentpfad keinen Principal-SQL-Cleanup, bewahrt
FAIL/NOT_ESTABLISHED und entfernt nur den vollständig gebundenen Fakecontainer.
Alle nativen Aufrufe ersetzt, keine tatsächliche SQL-/Containeradmission;
synthetischer temporärer Ledger danach entfernt.

Zwei Review-P2 vor der ersten Runtimeadmission korrigiert: tatsächliches
Phasentupel im Rechtegegenfall statt Listenvergleich; kein konkurrierender
Principal-SQL-Cleanup bei unbestätigtem Kostenclient. Keine verbrauchte
Runtimeadmission, kein stilles Löschen eines tatsächlichen FAIL-Ledgers.

## Quellen und ursprüngliche Vorbereitung

Primärquellen, Abruf 2026-10-12:
[sys.dm_os_host_info](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-host-info-transact-sql?view=sql-server-ver17)
verlangt seit SQL Server 2022 VIEW SERVER PERFORMANCE STATE;
[CREATE DATABASE](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-database-transact-sql?view=sql-server-ver17)
beschreibt die DB-Erstellungsrechte. Empirischer Nachweis ist separat
erforderlich; Dokumentation ersetzt keine tatsächliche Negativkontrolle.

Vor der ersten Admission war der Rollenpfad ausschließlich vorbereitet. Unabhängige
Quellenclosure, tatsächliche zwei Lifecycles und vollständiger
PR-/Head-/Main-/Tree-/Sync-/eigener Cleanupabschluss sind Abschlussgates.
Hard-Abort und vollständige Runtime-/TP-PERF-Abnahme bleiben offen.

Enge unabhängige Quellenclosure vor Admission erteilt: beide P2 geschlossen,
keine weiteren P1/P2 zu Login-/Secretbindung, tatsächlichen Rechtegegenproben,
Name-/SID-Cleanup und gemeinsamer Deadline; öffentliche Preflightpromotion
bytegleich bestätigt. Keine Runtime oder Tests durch den Reviewer.

| Quelle | SHA256 |
|---|---|
| öffentlicher 00_Preflight.sql | 7FC2A900E2419CDF10590145270F3A06377CBB6A8A49E6E6836860EEE36DB684 |
| öffentlicher run_profile.py unverändert | DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1 |
| eigener ignorierter qualify_roles.py | 59B6EF00AFF65FF42B8FD6BFE6EE84AB475E8223BCC32594739B1F9C02C81736 |

## Tatsächlicher erster FAIL und begrenzte Kontexttrennung

C1/803B41BD338040B1 auf tatsächlichem 17.0.5005.3 ist geschlossenes
FAIL_EXECUTION/PUBLIC_CONTRACT_NOT_ESTABLISHED, kein Rollen-PASS.
Beide einzeln entzogenen Rechte lieferten vor Setup ausschließlich
PREFLIGHT/SKIP_PERMISSION mit den passenden nativen Detailmarkern;
neue DB-Abwesenheit und tatsächliche Grantrestores vorhanden.
Eigenes Login ohne feste Serverrolle, tatsächliche eigene DB-Ownerbindung,
Setup/Preview/MAXDOP/Baseline/Storage und der vollständige BEFORE-Kostenframe
bestanden. Alle vier NO_INDEX-DML-Kontrollen waren tatsächlich erfolgreich.
Der anschließende Indexbau lieferte native Fehler 2571/State 3:
User 'dbo' does not have permission to run DBCC TRACEON, anschließend
42234/State 1: Internal SQL error during DiskANN graph build.
Kein AFTER-Kostenframe, kein qualifizierter Index, kein Rebuild-/Suchclaim.
Native Originalrestores/Attestation 0/0, neuer DB-Abwesenheitsclient,
gebundener eigener Login-Drop/neue SID-/Principalabwesenheit und vollständige
eigene CID-/Namensabwesenheit bestanden; gesamtes Cleanup 13,0928537 s.
Eine tatsächliche Admission verbraucht; zweiter unveränderter Slot nicht gestartet.

[CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
dokumentiert ALTER auf der Tabelle; der tatsächliche alte gebundene Linux-
Buildpfad stößt zusätzlich auf die beobachtete interne TRACEON-Grenze.
[DBCC TRACEON](https://learn.microsoft.com/en-us/sql/t-sql/database-console-commands/dbcc-traceon-transact-sql?view=sql-server-ver17)
verlangt sysadmin. Dies ist ein empirischer Befund für 17.0.5005.3,
keine allgemeine Behauptung über alle Vector-Index-Versionen. Kein manuelles
Traceflag-Enable, kein CONTROL SERVER-/sysadmin-Grant an den Operator.

C2 bleibt im selben Sechskandidaten-/Zwölfcontainerledger. Der geänderte feste
lokale Parent trennt genau die beiden vorhandenen CREATE VECTOR INDEX-Aufrufe
vom eingeschränkten Ausführungskontext. Ausschließlich die zwei festen nativen
Kostenclients verbinden als eigener sa; sie wechseln vor Beginn in den
eigenen Operator-Login, REVERT ausschließlich unmittelbar vor dem exakten
Indexbuild, wechseln danach wieder in denselben Operator und attestieren
dessen Kontext vor Ende. Alle übrigen öffentlichen Clients authentifizieren
weiterhin als Operator. Keine IMPERSONATE-/Serverrollengrants an ihn.
Vier tatsächlich geordnete Kontextrecords je Kostenphase sind erforderlich:
ROLE_START/ADMIN_BUILD/ROLE_RESTORED/ROLE_END mit OriginalLogin sa,
Sysadmin-/ControlServerwerten und vollständiger eigener Operator-SID.
Der Parent akzeptiert weder versteckte Admin-DML noch falsche/redundante/
fehlende Kontextchecks. Vollständige tatsächliche native SQL-Bytes/Hashes
werden vor Start privat gesichert. RunToken bleibt native -v-Bindung,
RoleSid ausschließlich bereinigte eigene ENV-Bindung; die Kontextquelle
enthält nur feste Platzhalter und bleibt innerhalb C2 bytegleich.
Die literale Eingabe ist deshalb ausdrücklich
kein unveränderter öffentlicher Einzel-Login-Aufruf. Der öffentliche Controller
und die öffentlichen SQL-Quellen bleiben außerhalb des Preflightdeltas gleich.

Das belegt gegebenenfalls eine begrenzte lokale Aufgabentrennung, keinen
vollständigen Nicht-sysadmin-Build und keine öffentliche Multi-Login-API.
Phasenkosten/Buildzeiten enthalten zusätzlich die Kontextinstrumentierung,
kein isolierter Performancevergleich. Die alte C1-FAILquelle bleibt erhalten;
neue Admission erst nach engem Delta-Review. Drei neue synthetische
Quellen-/Identitätsgegenproben bestanden ohne SQL, keine unveränderte
Controllertestwiederholung. ClientEndUnknown verhindert weiterhin jeden
zusätzlichen Principal-SQL-Cleanup; eigene Deadlines/Effektgrenzen unverändert.

Aktuelle C2 SHA256: Parent F0341668E58E5FD6C0E00E09DA21579F5B694D8F6C2E44A0944C77E20FA0451A,
feste Kontextquelle E320B1D61E1599C6A63017D15D40575D19D1548FFB5DA0DF42F61272979E3E76.

Enge unabhängige C2-Quellenclosure vor Admission erteilt, keine P1/P2:
privilegierter Kontext ausschließlich der einmal exakt erkannte Index-DDL;
DML/übrige Guards im Operator-Kontext und geordnete tatsächliche Rückkehr-
records, feste Token-/SID-/Secretbindung, 160000-Byte-Limit und bestehender
Leasevertrag bestätigt. Beide aktuellen Hashes bestätigt; keine Runtime
oder Tests durch den Reviewer. Diese Closure erfolgte vor der C2-Admission.

## Zweiter tatsächlicher FAIL und Syntaxkorrektur C3

C2/A16779D9D401423E ist geschlossen FAIL_EXECUTION/
PUBLIC_CONTRACT_NOT_ESTABLISHED. Beide Rechtegegenproben, ihre Grantrestores
und die eigene DB-Ownerbindung bestanden. Die erste tatsächliche native
Kostenquelle (28412 UTF-8-Bytes, SHA256
7788A94B8B30C9D3647232DC64CCB5EAB1E77581BC8FC2833D09B2DB406714EB)
scheiterte mit SQL Msg 156 an dem unquotierten reservierten Alias Checkpoint.
Keine tatsächlichen Kontextrecords, kein Kosten-/DML-/Index-/Rebuild-PASS.
Originalrestores/Attestation 0/0, neuer DB-Abwesenheitsclient, eigener
Login-Drop mit neuer Principal-/SID-Abwesenheit und vollständige
CID-/Namensabwesenheit bestanden; gesamtes Cleanup 13,0965515 s.
Zwei geschlossene Fehlkandidaten zählen weiter im selben Ledger.

C3 ändert ausschließlich den SQL-Alias zu [Checkpoint]. JSON-Feldname und
Identitäts-/Privileg-/Lease-/Cleanupsemantik bleiben gleich. Aktuelle feste
Kontextquelle SHA256
F78446CF632378D3A2CE31357D2E75879765B75AC9459C8C9161878D3C4B89D0;
Parent F0341668E58E5FD6C0E00E09DA21579F5B694D8F6C2E44A0944C77E20FA0451A
unverändert. Drei betroffene synthetische Quellen-/Identitätsgegenproben PASS.
Enge unabhängige Syntaxdelta-Closure vor Admission erteilt: Rücknahme genau
dieser Quotierung ergibt bytegenau den geprüften C2-Hash; keine weiteren
Delta-Befunde, keine Runtime oder Tests durch den Reviewer. Der nächste
eigene Lauf beginnt als C3, bei Erfolg folgt derselbe stabile zweite Slot.


## Tatsächliche zwei stabile Rollenlifecycles C3

| Slot | synthetischer Token | Indexbau µs | Rebuild µs | gesamtes Cleanup s |
|---|---|---:|---:|---:|
| 2025-happy-1 | F2BED8B1B7FB4008 | 872078 | 827937 | 13.4958547 |
| 2025-happy-2 | CA7DFACE4C9F47D3 | 1071815 | 937912 | 13.7201669 |

Beide tatsächlichen 17.0.5005.3-Läufe desselben C3 sind geschlossen ohne
failure. Sämtliche Demo-/Parent-/Kontext-/Fixturequellen und beide tatsächlichen
nativen Eingaben innerhalb C3 bytegleich: DML 28420 UTF-8-Bytes/SHA256
9C9F9614F52D4D769C0B59E5CAA95B15DE327DE59F94DCD3EB6952A734548BF6;
Rebuild 27610 UTF-8-Bytes/SHA256
557A2B256FF88A8582D1D5AB24209F4E851896FE04AACB03C870ED12846C8217.
Die Inputquelle enthält feste RunToken-/RoleSid-Platzhalter; tatsächliche
frische Login-/SID-Werte sind über die nativen Bindungen in den Records belegt.

Je Lauf beide einzeln entzogenen Rechte mit tatsächlichen Detailmarkern und
ausschließlich PREFLIGHT/SKIP_PERMISSION vor Setup, neue DB-Abwesenheit,
tatsächliche Grantrestores, Login ohne feste Serverrolle und eigene DB-
Ownerbindung bestanden. Acht geordnete tatsächliche Kontextrecords belegen
für beide Kostenphasen Operator mit Sysadmin/ControlServer 0/0, Admin 1/1
ausschließlich am Indexbuild, danach Rückkehr in dieselbe vollständige
Operator-SID bis zum Phasenende. DML-Kontrollen liefern vier Erfolge ohne
Index und vier tatsächliche 42231/State-1-Verweigerungen mit Index; vollständige
999-Row-Quellen-/Distanzprüfung, Commit ausschließlich Id 999 nach Drop,
übrige 998 Vektortexte unverändert, fünf distanzgeprüfte Suchkontrollen und
Recall@5 1 nach Rebuild. Drei tatsächliche Speicherpunkte und zwei vollständige
BEFORE-/AFTER-Kostenfolgen vorhanden, mit den bestehenden Session-/TempDB-/
DB-Datei- und Instrumentierungsgrenzen.

Öffentliche Resultate bleiben WARN_OPTIONAL_EVIDENCE_SKIPPED, Generation
UNKNOWN und runtime_qualification NOT_ESTABLISHED. Parent-PASS belegt nur
diesen lokalen Kontext-/Rechte-/Lifecyclevertrag. Originalrestores und neue
Dropattestation tatsächlich 0/0, neuer DB-Abwesenheitsclient, eigener Login-
Drop mit neuem unabhängigem Principal-/SID-Abwesenheitsclient, vollständige
CID-/Namensabwesenheit und entfernte native temporäre Eingaben bestanden.
Keine Secrets/SIDs/Hostdaten veröffentlicht; Rohdaten und gleicher Ledger
bleiben ignoriert unter Runtime/IDX012_ROLES. C1 und C2 bleiben tatsächliche
FAILs; vier eigene Container insgesamt verbraucht und entfernt. Keine weiteren
identischen grünen Läufe zur Ausschöpfung des Budgets.

Damit ist der begrenzte lokale Split belegt. Öffentliche Multi-Login-API,
vollständiger Nicht-sysadmin-Indexbuild, absolute Minimalrollen, Hard-Abort,
Demo-Release sowie vollständige Runtime-/TP-PERF-Abnahme bleiben offen.
PR-/Head-/Main-/Tree-/Sync-/eigener Branchcleanup sind Integrationsgates.
