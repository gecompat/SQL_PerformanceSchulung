# TSK-004: eigener geänderter VECTOR-Caller mit Sessionreader-Vertrag

PR235 vollständig geschlossen: neun erfolgreiche Head-Gates/sieben erfolgreiche
Main-Workflows, Main d5ee1864c7cafdfdfc1b9b077c45a6efa5291ce3, voller Tree,
FF-Synchronisierung, eigene Branches entfernt, 39 private Dateien hashverifiziert
gesichert und eigener Worktree tatsächlich archiviert. Der reine
[Sessionreader-Vertrag](SQL_SERVER_2025_AI_SESSION_READER_REVIEW.md) ist nach
C1-Sourceabschluss gestoppt; er erteilt allein keinen Nativeentscheid.

## Geänderte Grundlage und gemeinsames Restbudget

Die [frühere Transportakte](SQL_SERVER_2025_AI_VECTOR_TRANSPORT_REVIEW.md)
bleibt C1 FAIL/UNKNOWN_STOP mit SQLcleanup NOT_ESTABLISHED und nicht attestierter
DB-/Inputabwesenheit. Kein weiterer Aufruf ihres gestoppten Pakets, keine SQL-
oder Cleanupaktion gegen ihre alten Ressourcen, keine Rekonstruktion ihrer
verlorenen Exception. PR229/234/235-Akten und Originale bleiben readonly.

Dieser eigene Caller übernimmt ausschließlich geänderte Source: explizite
passende Sessionprojektion, alle acht tatsächlich beobachteten Typ-/Getter-/
NULLfelder und getrennte Read-/Projektions-/Dispose-/Primaryfehlerrecords.
Neue Input-/Receipt-/Rootbindungen dürfen alte Records nicht als neue Proben
zulassen. Ein Implementer/enger unabhängiger Rootreview; sechs relevante
Sourcekandidaten, Sourcecheckpoint nach drei und Sourceabbruch nach sechs.

Das Nativebudget wird **nicht zurückgesetzt**: früherer Transport-C1 zählt
als ein Container/ein Compile/ein Caller. Für dieses geänderte eigene Profil
bleiben höchstens fünf zusätzliche serielle eigene Container, fünf Compiles
nur bei tatsächlichen C#-Änderungen und fünf Caller. Gemeinsame Grenze sechs;
Checkpoint nach insgesamt drei Transportkandidaten, Abbruch nach insgesamt
sechs. Neuer Profileversuch R1 entspricht dem insgesamt zweiten Kandidaten,
R2 dem dritten/Checkpoint. Nach erstem kohärenten begrenzten Roundtrip-PASS
Stop. Unveränderte Eingaben, Programme oder bereits grüne Tests werden nicht
wiederholt. UNKNOWN stoppt auch das neue Paket; keine folgende SQL-Anfrage und
keine zweite mutierende Recovery. Ein künftiger zusätzlicher Scope darf diese
gemeinsame Restgrenze nicht still erweitern.

## Konkreter bereits autorisierter lokaler Effektumfang

Nur bestehende gepinnte SDK10.0.401-/Runtime10.0.12-/SqlClient6.1.4-Bytes,
die fünf belegten literal Runtimeassetpfade und aktuelle öffentliche
SQL_Server_Lab-/Namespace-/SQLcmd-Verträge. Keine Downloads, Restore, globale
Installation oder Änderungen anderer Repositories. Ein neuer eigener
SQL17.0.5005.3/Linux/Developer-Container je Versuch, CL170 und nur zwei
synthetische VECTOR(3)/FLOAT32-Rows. Frischer 16Hex-RunToken, DBname
SQLPERF_LAB_QRY014_<TOKEN>, vollständige bytegenaue vier Eigentumsmarker,
eigene ganze CID/Name/Label/Image/Loopback-/Ressourcenbindung vor Mutationen.

SQLCMDPASSWORD nur ENV/readonly SecureString/SqlCredential, kein Credential
in argv/Connectionstring/Hashes/Rawfiles. Poolingfalse, verschlüsselte Verbindung
und nur eigener begrenzter Lab-TrustServerCertificate-Effekt. Compiler und
Nativecaller erhalten getrennte konkrete Rootadmissions erst nach aktuellem
Source-/Pure-/Pin-/Privacy-/Risikoabschluss. Compiler60s insgesamt einschließlich
Reaping; normal300s und genau eine Cleanupdeadline60s, 17s Namespace-Reserve
vor Cleanup-SQL und pro Call tatsächlicher Restbudgetcheck. Keine behauptete
Wallclockgarantie. Held PIDs/poll/rc/raw/Requestenden bleiben erforderlich.

Positive typisierte FLOAT32-Koordinaten/rückgelesene Werte, SQL-NULL und spezifische
tatsächliche Dimensionsabweisung mit vollen Fehlerfeldern. Acht Sessiontypen
sind tatsächliche Basistyp-/CLRnamen; konfigurierte nvarchar-Längen werden nicht
als beobachtete Größen ausgegeben. Source-delete/51003/Restore und vier Marker-
DML-/Cleanuprejections51004 mit tatsächlichen Vollstates/Restores. Frische SQL-
DBabwesenheit vor Setup und nach tatsächlichem guarded Drop, frische ganze
CID-/Namens-/Inputabwesenheit. Namespacecontainment nach UNKNOWN höchstens
einmal vollständig gebunden; niemals SQLcleanup-PASS aus Containerabwesenheit.

## Aktueller Stand und offene Qualification

Der Schnitt begann SOURCE_PREPARATION_ONLY mit null zusätzlichen Effekten.
Nur neue betroffene Puretests normal/geschützt unter `-O`, unveränderte
historische Tests und Diagnosen nicht wiederholen. API-/SQL-Kohärenz ist kein
unabhängiger TDS-Wiretokenbeleg. float16, andere Versionen/OS (Operating System; Betriebssystem)/Editionen, Provider,
Pooling/Rollen/Performance/RAG (Retrieval-Augmented Generation; Antworterzeugung mit zuvor ausgewählten Quellen), volle TSK-004-/Workstream-/Releaseabnahme offen.
Cloud-/Bezahl-API-/ONNX-/rote Hosteffekte ausgeschlossen. Modell-/Tokenverbrauch
UNKNOWN. Aktuelle PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktreeclosure
und unmittelbarer nächster zulässiger Schritt bleiben erforderlich.

## R1 / Gesamt2: tatsächlicher FAIL / UNKNOWN_STOP

67 Precompile-Sources, 168 Refs, 28 Assets/fünf literal Pfade, drei C#-Quellen
und 22 SQLs gebunden. Erster neuer Purelauf: sechs PASS/ein bekannter
History-Readcap-FAIL, PID53536/poll1/rc1; Raw erhalten. Ausschließlich die
korrigierte Historymethode erneut PASS/PID17292 und fünf neue geschützte
Methoden PASS/PID11472. Keine alte Suite oder historische Runtime wiederholt.
Enge unabhängige Source-/Privacyprüfung und getrennte Rootadmissions bestanden.

Ein zusätzlicher Compiler PID29456/poll0/rc0/0,637039s, kein Timeout/UNKNOWN,
91136-Byte-Artefakt; beide CS1701-WARNs für Assemblyrefs9→10 erhalten.
Ein zusätzlicher Container/Caller: TopPID62976/poll1/rc1/11,574684s und
ChildPID35344/poll1/rc1, kein Timeout. Tatsächliche .NET10.0.12/eigene literal
SqlClientdatei/Assemblyversion6.0.0.0 und alle 71 Sources bestätigt.

OPEN vollständig beendet, acht tatsächliche Driver-Typmetadaten erhalten:
Ordinal0 `CONVERT(int,@@SPID)` meldet int/System.Int32 und GetInt32(0) endet.
Ordinal1 `DB_ID()` meldet smallint/System.Int16; GetInt32(1) wirft tatsächlich
System.InvalidCastException, Readerstep21 mit UTC-/Dauerende. Dispose endet
in Step22 RETURNED, PrimaryError bleibt InvalidCastException, DisposeError
null/Value null/ServerUnknown true. Zwei Aggregate-Requests, der Sessionreader
bleibt UNKNOWN. Keine VECTOR-/NULL-/Dimensions- oder Source-/Markercontrols
erreicht, kein vollständiger Sessionwert oder typisierter Roundtrip-PASS.

Die aktuelle Microsoft-[DB_ID-Primärquelle](https://learn.microsoft.com/en-us/sql/t-sql/functions/db-id-transact-sql?view=sql-server-ver17)
dokumentiert int. Der konkrete Driver meldet smallint/System.Int16. Das ist
eine offene Dokumentations-/Driverbeobachtungsgrenze; ohne unabhängigen
Server-/Wiretypcapture wird keine Ursache oder allgemeine Produkteigenschaft
behauptet. Eine explizite int-Projektion ist der nächste geänderte Sourcepfad,
kein rückwirkender Beweis der früheren unklassifizierten Exception.

Sechs bekannte SQLcmdenden und ein Vollstate vor dem Child, danach null SQL.
Genau einmal volle eigene Namespacecontainment, RemovePID48744/poll0/rc0
mit `--time=0`, danach frische ganze CID-/Namensabfragen leer; acht bekannte
Namespaceprozessenden. SQLcleanup NOT_ESTABLISHED/DatabaseAbsent false/
InputsAbsent false/Ledgerclosed false, Eingaben und Originale erhalten.
Root hat Originalresultat, tatsächliche Teilenden/Typen/Fehler, volle
Namespacebindung, Abwesenheitswitnesses und alle 71 Sourcepins geprüft.

UNKNOWN_STOP dieses R1-Pakets, keine weitere Ausführung oder Aktion gegen
seine alten Ressourcen. Gemeinsame Zähler jetzt zwei Compiler/zwei Container/
zwei Caller, höchstens vier weitere Gesamt3–6 bleiben; Gesamt3 ist Checkpoint.
Vollständige aktuelle Integration folgt, danach geänderte eigene Source-
vorbereitung mit expliziter DB_ID-int-Projektion und sichtbarer Bindung dieser
Restgrenze. Alte Stops bleiben, kein Runtime-PASS und kein stiller Budgetreset.
