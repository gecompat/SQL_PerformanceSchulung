# CON-010: öffentliche V2-Capturevorbereitung

Dieser SOURCE_ONLY-Schnitt enthält einen [reinen Capturehelper](../../Tests/Static/con010_pool_capture.py),
[fokussierte synthetische Gegenfälle](../../Tests/Static/test_con010_pool_capture.py)
und einen [festen V2-Vertrag](../../Tests/Static/Fixtures/con010/pool-capture-contract-v2.json).
Es gibt keine Prozesse, SQL-, Container-, Modell-, CLR- oder Providermetadatenaufrufe.
Der V1-Poolrecordconsumer und seine Private42-Sourcepopulation bleiben unverändert.
V2 bindet ausschließlich die fünf bereits vorhandenen öffentlichen Dateien dieses
Schnitts und des Framework-Collectors; es gibt keine erfundenen Producerpins.

## Capturegrenze

`capture_sqlcmd` nimmt einen tatsächlichen öffentlichen `SqlcmdResult`, die dazugehörige
PID (Process Identifier; Prozesskennung), den tatsächlichen finalen Pollstatus, die eigenen ursprünglichen UTF8-Inputbytes,
die ausschließlich private Callercredentialliste und die vorher gepinnte öffentliche
Quellenkarte entgegen. Der Helper startet oder pollt selbst keinen Prozess.
Boolaliases, fehlende oder inkohärente Daten werden verworfen. Das Ergebnis enthält
nur Capturemetadaten/Digests im privaten Caller; `summary` exportiert feste Statuswerte
und begrenzte Counts. Rohtexte, PIDs, Credentials und Digests werden nicht exportiert.
Der Caller muss die Werte vom selben tatsächlich gehaltenen Prozessobjekt beziehen;
synthetische Inputs und Callerangaben werden nicht unabhängig attestiert.

`InputFileSha256` bezeichnet ausdrücklich die ursprüngliche Datei vor SQLcmd-ENV-
Expansion. Er ist kein Hash des serverseitig ausgeführten SQLtexts. Platzhalternamen
wie `$(TenantSecretA)` sind erlaubt, Credentialwerte nicht. Es werden keine Secrets,
ENVwerte oder Passwort-/SecretderivedHashes gespeichert. Eine zwingende private
Liste der vier eigenen Credentials wird vor jedem Input-/Output-/ConfiguredText-
Digest geprüft; Treffer erzeugen nur `FAIL_CREDENTIAL_OUTPUT`, ohne Rawdaten oder
Digests. Plaintext, UTF8-/UTF16LE-Hex sowie vollständig zusammengesetzte äußere
UTF16LE-Hexframes des einen unterstützten `CON010_POOL_CAPTURE_PART`-Formats werden
geprüft; ein Secret im inneren Hexfeld darf nicht an Chunkgrenzen vorbeigehen.
Keine allgemeine Decoder- oder Encodingpipeline wird eingeführt.

Der öffentliche Collector arbeitet mit `text=True`, UTF8 und `errors=replace`.
Stdout-/Stderr-Digests binden daher den tatsächlich zurückgegebenen dekodierten Text,
erneut UTF8-kodiert. Sie belegen keine unverändert erhaltenen ursprünglichen Pipebytes
oder serverseitigen Texte. Empfangene Texte bleiben vollständig in der privaten
Callerakte, mit diesen separat erfassten Digests und ausdrücklicher Transportgrenze.

Ein bekannter SQLcmd-Prozessabschluss und dessen echter Returncode belegen nicht
automatisch ein bestätigtes Ende sämtlicher Serverrequests. Das normale Serverende
bleibt `NOT_CAPTURED`. Timeout, unbekannter/inkohärenter Pollstatus oder negatives
Signalende setzen Serverende `UNKNOWN` und eine sticky Sperre: kein Folge-SQL.
Ein später bestätigtes Childende löscht diese Sperre nicht. Ein normaler bestätigter
Clientabschluss verlangt weiterhin eigene Semantik-, Scope- und Recoverygates.

`capture_dotnet`/`validate_dotnet_record` bilden ausschließlich die deklarierte
OPEN-/SCALAR-/CLOSE-Sourceform ab. Ein SCALAR-Digest wird nach Credentialprüfung aus
dem konfigurierten geheimenfreien Clienttext erzeugt; kein Server-Executedtextclaim.
Ein zurückgekehrter APIcall ist `RETURNED_TO_CALLER`; fehlendes Ende ist `UNKNOWN`.
In dieser Vorstufe wird kein .NET-/TDSrequest gestartet. Alle Ergebnisse bleiben
WARN, Callerprovenienz `NOT_INDEPENDENTLY_ATTESTED`, Runtime und TP-CON offen.

## Vorhandener Collector und gemeinsames Budget

Die tatsächlich gebundene öffentliche Quelle
[`sqlcmd_process.py`](../../Demos/00_Framework/Tools/sqlcmd_process.py)
enthält `build_sqlcmd_command`, `start_sqlcmd` und `collect_process`. Ein späterer
Producer kann diese APIs verwenden, ohne die gemeinsame Frameworkdatei zu ändern.
Der Commandbuilder nimmt SQL-Passwörter ausschließlich aus SQLCMDPASSWORD und
setzt kein -P. Der neue Helper weist Credentialargumente zusätzlich ab.

Fünf Sekunden sind ein tatsächlich konfigurierter `communicate(timeout=5)`-Nachlauf,
keine ausreichende Gesamtreapinggarantie. Auf Windows enthält
`_terminate_process_tree` zusätzlich `taskkill(timeout=5)` und `wait(timeout=2)`.
Wenn nach erstem Timeout auch das erste Nachlesen scheitert, läuft der äußere
Fehlerpfad erneut über Terminierung und Nachlesen, zuletzt `wait(timeout=2)`.
Der konservative konfigurierte Reservewert beträgt deshalb
2×(5+2)+2×5+2=26 Sekunden. `collector_wait_seconds` reserviert diese 26 innerhalb
des bereits verbleibenden gemeinsamen Budgets und verlangt zusätzlich eine explizite
erforderliche eigene Cleanupreserve. Ein fehlender/Nullreservewert wird abgewiesen.
Bei 60s verbleibender Gesamtzeit, 20s deklarierter Cleanupreserve und einer
40s-Gesamtphase bleiben
höchstens14s primärer Collectorwait. Die 20s hier sind nur ein Rechenbeispiel; der
künftige Producer muss seine tatsächlich erforderliche eigene Restreserve begründen.
Bei Restbudget<=26s+Cleanupreserve oder Phasecap<=26s wird kein Collector zugelassen.
Dies ist eine Source-/Caprechnung, keine empirische OS-/Laufzeitgarantie. Eine
ausdrückliche Grenze lautet `NO_WALLCLOCK_GUARANTEE`; der bloße Exceptionpfad
enthält 14s konfigurierte Waitcaps. Scheduling-/OSoverhead ist zusätzlich möglich.
Eine frische tatsächliche Deadlineprüfung nach jedem Rücklauf bleibt Pflicht; ein
überzogenes oder unbekanntes Ende darf keine nächste Aktion autorisieren.

## Begrenzter späterer Producer

Die nächste eigenständige Runtimegrenze ist ein opt-in RED-Profil mit drei eigenen
Logins, zwei synthetischen VECTOR(3)-Rows und sechs A/B/U/A/B/U-Checkouts. Bestehende
Green-CON-010-Manifeste und Default-CI (Continuous Integration; automatisierte Integrationsprüfungen) führen keine Login-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten)/RED-Profile aus.
Providerfähigkeit wird vor Container-/DB-/Loginwirkungen geprüft; fehlende vorhandene
Windowsassembly bzw. Linuxprovider ergibt SKIP vor Effekten. Kein Download, Install,
Cloudfallback oder Hosttrustwechsel.

Nur ein eigener voll gebundener Wegwerfcontainer ist zulässig: ganze CID, Name,
Image, Ownerlabel, NoMounts, Loopback, vierCPUs/sechsGiB und exklusive Scopeadmission.
Vier bytegenaue eigene DBmarker und vollständige Held-SID-/Principal-Leases müssen
vor Mutationen und Cleanup greifen. Client/Poolabwesenheit liegt vor Login-Drops,
diese liegen vor DBdrop; danach frische SQL-, CID-/Namens-/Inputabwesenheit.
UNKNOWN erlaubt nur vollständig gebundenen OwnNamespaceabbau, keine SQL-Adoption.
Die 300s-Normaldeadline und einmalige60s-Cleanupdeadline werden nicht neu gestartet;
Cleanup beginnt vor dem höchstens40s-Child einschließlich konfigurierter Reserve.

Diese Vorstufe hat sechs Quellenkandidaten/Checkpoint3/hard6 und Nativebudget0.
Ein späterer separat zugelassener Producer hat höchstens einen neuen eigenen
Container je Quellenkandidat, maximal sechs. Keine private Runtimeimporte oder
allgemeine Provisionierung. Tatsächliche Ausführung und Producer-/Provider-/
CON-010-/TSK-009-/TP-CON-Abnahme bleiben offen. Keine Rawcaptures werden aus privaten
C3-Records kopiert; Gegenfälle sind ausschließlich synthetisch.


## Zwei geprüfte Collector-Checkoutvarianten

Die unveränderte öffentliche Collectorquelle ist separat als tatsächlicher LF-Blob
(SHA256 ef33fbeb4436044ac2fd490b90b0608e4743f0f8accbbd3e3a2ee762fc2ac09d)
und Windows-CRLF-Checkout (d8b553419bb34e4bafe7d0a7baee55ca28a5b97d1ad64710e131674aa6ca9757)
gebunden. Beide konkreten Bytes wurden sourcegeprüft; der Helper normalisiert nichts
und akzeptiert keine weitere Variante. Quellenkarte und Capture bewahren den
jeweils tatsächlich gelesenen Rawbyte-SHA. Das erweitert keine Provider-/OS-/Runtime-
Abnahme; der historische PR224-Windows-Nachweis bleibt korrekt. Der feste aktuelle
V2-Vertrag führt genau beide Werte unter `collector_sha256_variants`. Der Helper
übernimmt keine freien Zulassungen aus dieser Liste; beide zulässigen SHAs sind
zusätzlich ausdrücklich im Code gebunden.
