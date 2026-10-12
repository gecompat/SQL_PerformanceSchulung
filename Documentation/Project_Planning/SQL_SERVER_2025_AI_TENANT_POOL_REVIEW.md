# TSK-009 / CON-010: begrenzte Poolvorbereitung

Stand: 2026-10-12. Status: SOURCE_PLAN_ONLY; Scope-Review geschlossen,
Implementierung, Source-Abschluss und Native-Admission offen.

## Ausgangspunkt und konkrete Lücke

[PR220](https://github.com/gecompat/SQL_PerformanceSchulung/pull/220) ist auf
`a0b01f4515677a546841797a00c492a8dd695826` vollständig abgeschlossen: acht aktuelle
Head-/sechs Main-Workflows PASS, voller identischer Tree, main FF/synchron/sauber,
eigener lokaler und Remote-Branch entfernt. Die drei optionalen Leseaufgaben sind
integriert; Teilnehmererprobung und Generalprobe bleiben offen.

Der [begrenzte Serverlogin-PASS aus PR219](SQL_SERVER_2025_AI_TENANT_LOGIN_REVIEW.md)
prüfte neue getrennte Verbindungen. Er beweist keine Wiederverwendung einer
physischen Verbindung aus einem Clientpool. Die öffentliche CON-010-Demo bleibt
im bisherigen WITHOUT-LOGIN-/EXECUTE-AS-Scope. Die neue Frage betrifft genau
dieselbe synthetische Tenantzuordnung unter tatsächlich wiederverwendeten
Verbindungen, insbesondere einen Sessionkontext nach Rückgabe und erneutem Open.

## Tatsächlich vorhandene Oberfläche, keine Runtimeabnahme

Ein begrenzter read-only Metadatencheck fand die vorhandene öffentliche
System.Data.SqlClient-Assembly 4.6.1.6, FileVersion 4.900.126.11103,
TargetFramework .NETCoreApp 8.0, unter PowerShell 7.6.6/.NET 10.0.12.
ClientConnectionId, SqlCredential und ClearPool(SqlConnection) sind vorhanden.
Ein parameterloses geschlossenes Objekt wurde erstellt und disposed; kein Open,
SQL-Befehl oder Poolclear. Keine Installation, kein Download und kein Fallback.
Microsoft.Data.SqlClient war in diesem Prozess nicht auflösbar; das ist keine
Inventaraussage über alle Hostinstallationen.

Diese vorhandene Assembly ist ausschließlich der privat bytegebundene Testcaller.
Es gibt keine Providerempfehlung, Support-, Supply-Chain- oder TDS-Abnahme und
keine Redistribution. Alle Daten und Credentials bleiben synthetisch und privat;
Netzwerk ist auf den eigenen Loopback-Testcontainer begrenzt. Fehlender Transport
führt später zu FAIL und sicherem eigenen Cleanup, keiner neuen Dependency.

## Endlicher Effekt- und Ergebnisumfang

Sechs kohärente Quellenkandidaten, Checkpoint nach drei geschlossenen Kandidaten,
Hardstop sechs; je ein neuer eigener serieller Container/ein Profil, maximal sechs.
Festes vorhandenes Image, SQL 17.0.5005.3, EngineEdition 3, MSSQL_PID=Developer,
CL170, vier CPU/sechs GiB, vollständige CID-/Namens-/Owner-/Image-/Ressourcenbindung
und tatsächliche Mountabwesenheit. 300 Sekunden regulär einschließlich Startup,
danach einmalig gemeinsame maximal60 Sekunden für eigenen Cleanup.

Eigene DB SQLPERF_LAB_CON010_TENANTPOOL mit vier vollständigen bytegenauen
Eigentumsmarkern: Project SQL_PerformanceSchulung, ContractVersion 1.0,
DemoId CON-010 und RunToken TENANTPOOL. Initiale Abwesenheit vor Neuanlage;
Marker-, DBID-, Namens-/Klassenbindung vor jeder folgenden Mutation. Drei eigene
A/B/Unmapped-Logins mit vorher reservierten vollständigen SIDs und gehaltenen
Principal-/Permissionleases. Zwei synthetische Quellen/VECTOR(3), RLS und
CONNECT-/Objekt-SELECT-Rechte aus dem bestandenen begrenzten Authprofil.
CREATE/DROP LOGIN ist RED-isolated ausschließlich im neuen eigenen Wegwerfcontainer;
dessen eigener gebundener Abbau ist der Resetpfad. Keine Standard-CI-Ausführung
der roten privaten Komponente. Keine Preview-/MAXDOP-/Host-/Truststore-/globalen
ODBC-/Dienst-/Modell-/Cloud-/ONNX-Änderung.

Ein eigener PowerShellprozess soll sechs serielle Checkouts A1/B1/U1/A2/B2/U2
prüfen. Je Lane ein stabiles SqlCredential-Objekt aus SQLCMDPASSWORD in privater
ENV und Speicher, gleiche ConnectionStringbytes, eigener ApplicationName/Nonce.
Pooling true, MinPoolSize 0, MaxPoolSize 1, MARS/Enlist false, ConnectRetryCount 0.
Keine Passwortwerte in ConnectionString, Argumenten, Logs oder öffentlichen
Artefakten. Verschachtelte Credentialausgaben müssen vor Persistenz verworfen
oder redigiert sein. Lokales TrustServerCertificate betrifft nur den eigenen
Loopbackclient wie sqlcmd -C, keine allgemeine TLS-/Egressfreigabe.

Der zweite Checkout muss tatsächlich dieselbe physische Serververbindung derselben
Lane und die passende volle Login-/Original-/DBuser-/SID-/DBbindung besitzen.
Physische Verbindung bedeutet hier vollständiger eigener Owner-DMV-Beleg aus
connection_id/connect_time und Session-/SID-/DB-/ApplicationName-/Noncezuordnung
während der Tenantverbindung. Serverconnection_ids bleiben innerhalb einer Lane
gleich und unterscheiden sich zwischen Lanes. SPID allein ist kein Beleg.
ClientConnectionId wird nach erfolgreichem Open/Query vollständig erfasst und
zugeordnet; sie bezeichnet laut Primärquelle den letzten Verbindungsversuch.
Keine unbewiesene Client-GUID-Gleichheit oder Gleichsetzung mit Server-GUIDs als
Erfolgsoracle. login_time wird erhalten, ohne unbelegte Gleichheitsforderung.
Owner besitzt bereits die Harnessrechte, Tenant bekommt keine neue DMVberechtigung.

A/B liefern jeweils die eigene vollständige Quelle samt Vektor, Unmapped besitzt
positive Authentifizierung und null Rows. Der absichtlich vor Close nicht
zurückgesetzte CON010_TenantId-Spoof darf den Tenant nicht wechseln. Beim erneuten
Open muss der Sessionwert vor jeder Reparatur tatsächlich NULL sein. Ein späterer
manueller Reset wird nicht zum Poolreset-PASS umgedeutet. Native VECTORdekodierung
des Clients wird nicht behauptet; alle Koordinaten werden SQLseitig als JSON gelesen.
Volle Source-/RLS-/Principal-/Rechte-/Configzustände bleiben erhalten. Die bereits
bestandenen Policy-/Impersonation-/REVOKE-Gegenproben werden nicht wiederholt.

## Known End, eigener Cleanup und offene Gates

Alle Open-/Command-/Reader-/Close-/Disposeoperationen benötigen bestätigte Enden.
Positive Clientzeitlimits liegen innerhalb der Parentdeadline. Ein Timeout oder
unbestätigtes SQL-Requestende bleibt UNKNOWN, auch nach später bekanntem
Prozessende: kein Folge-SQL, keine Reparatur und kein Login-/DBdrop. Nur der
vollständig gebundene eigene Namespace ohne Mounts darf begrenzt entfernt werden;
SQL-Abwesenheit bleibt dann NOT_ESTABLISHED, kein erfundener SQL-Cleanup-PASS.

Regulär ClearPool ausschließlich für die drei eigenen Connectionreferenzen,
danach Close/Dispose eigener Verbindungen/Reader/Credentials. Kein ClearAllPools
oder fremder Pool. Frische Owner-Abwesenheit aller gehaltenen Serverconnection_ids
muss physischen Abbau belegen. Erst dann vollständige gehaltene eigene Login-Drops
vor DBdrop, neue getrennte LoginName-/SID-/DBabwesenheit, frische CID-/Namens- und
Inputabwesenheit. UNKNOWN-Inputs bleiben privat für Recovery erhalten.

Ein Implementierungsverantwortlicher, Root als enger unabhängiger Reviewer der
neuen Pool-/Request-/Credential-/Cleanupgrenzen. Das Scope-Review korrigierte vor
Code die unbelegte Client-GUID-Stabilitätsannahme. Vor Native bleiben gebundener
Source-/Scope-/Budget-/Review-Abschluss und exklusive Admission erforderlich.
Unveränderte erfolgreiche Auth-/Legacytests werden nicht wiederholt. Ein Retry
benötigt relevante geänderte Quellen oder neue Evidenz; historische FAILs bleiben.
Modell-/Reasoningtokenverbrauch unbekannt, null neue Inferenz-/Providerrequests.

## Primärquellen und Fortsetzung

SRC-115, gelesen 2026-10-12: [ClientConnectionId](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlconnection.clientconnectionid?view=netframework-4.8.1),
[ADO.NET SQL-Connection-Pooling](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/sql-server-connection-pooling),
[ClearPool](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlconnection.clearpool?view=netframework-4.8.1),
[SqlCredential](https://learn.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlcredential?view=netframework-4.8.1),
[sys.dm_exec_connections](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-connections-transact-sql?view=sql-server-ver17)
und [SESSION_CONTEXT](https://learn.microsoft.com/en-us/sql/t-sql/functions/session-context-transact-sql?view=sql-server-ver17).
Quellen- und Reflectionbefund ersetzen keine TDS-/Reuse-/Reset-/Cleanup-Runtime.

Nächster Schritt: kleinster eigener Caller-/SQL-/Oracle-/Fehlerprüfscope, dann enger
Source-Abschluss und vorab gebundene Native-Admission. Aktuelle Scopeintegration,
vollständige Übernahme, Synchronisierung und eigener Branchcleanup werden regulär
geschlossen; private Codevorbereitung darf parallel ohne Native beginnen.
Pooling anderer Provider/OS/Authformen, Performance, Passwort-/TLSintegrität,
Seitenkanäle und volle öffentliche CON-010-/TSK-009-/TP-CON-Abnahme bleiben offen.
Andere Repositories bleiben unverändert; allgemeine Entwicklung und DGN-007 pausiert.


## Quellenabschluss und erste Runtimequalifikation

[PR221](https://github.com/gecompat/SQL_PerformanceSchulung/pull/221) ist vollständig
integriert: acht aktuelle Head-/sechs Main-Gates PASS, vollständiger identischer
Tree, main synchron und sauber, eigener lokaler und Remote-Branch entfernt.
Der [Quellenreview](SQL_SERVER_2025_AI_TENANT_POOL_SOURCE_REVIEW.md) schließt die
neuen Request-, Credential-, Pool-, Ergebnis- und Cleanupgrenzen unabhängig ab.

Die Implementierung verwendet eine bewusst strengere Zeitgrenze: dieselbe einmalige
60-Sekunden-Cleanupdeadline beginnt bereits VOR dem Poolchild. Das Child erhält
höchstens 40 Sekunden und höchstens die verbleibende normale und Cleanupzeit.
Sechs Checkouts, OwnClearPool/Close, frische physische Abwesenheit, gehaltene
Login-/DB-Drops und eigener Containerabbau müssen innerhalb derselben verbleibenden
Zeit enden. Kein Reset und keine zusätzliche IPC-/Clock-Infrastruktur. Das hält
die Ausführung endlich; unzureichende Laufzeit bleibt ein tatsächlicher FAIL.

Bekannte vollständige, credential-geprüfte Childreceipts bleiben vor semantischer
Auswertung privat erhalten. Ein falsches Ergebnis ist FAIL mit Nachweis.
Unbestätigte Requestenden bleiben sticky UNKNOWN und erlauben kein Folge-SQL.
Die private Admission ist ein dauerhafter Nachweis; Inputabwesenheit bezeichnet
die eigenen temporären input-*.sql, nicht die erhaltenen Beweisdateien.
SQLcmd-Handles und der eine separate .NET-/PowerShell-Child werden getrennt gezählt.

Quellenkarte und alle vier Rootgates binden tatsächliche Bytes vor jedem Effekt.
Eine relevante Änderung am PowerShell-Caller zählt nun ebenfalls für den Retry;
eine bloße Planänderung autorisiert keine unveränderte Wiederholung. Exklusive
Admission ist kandidatbezogen, höchstens sechs Kandidaten/eigene Container,
Checkpoint nach drei, harter Stop nach sechs. Provider-/Host-/Cloud-/ONNX-Grenzen,
öffentliche CON-010- und vollständige TSK-009-Abnahme bleiben offen.


## Kandidat 1: bekanntes FAIL vor Checkoutnachweisen

Der neue eigene SQL-17.0.5005.3-Testcontainer erreichte Setup, drei Loginzuordnungen
und einen vollständigen Quellen-/Rechtezustand. Der separate PowerShell-Child
lieferte ein vollständiges credential-geprüftes FAIL-Receipt mit bekanntem Ende,
aber null Checkoutrecords und unbewiesenem Poolcleanup. Seine erste Fehlerbehandlung
erhielt keine konkrete Ursache; daraus folgt ausdrücklich kein Provider-/TDSbefund.
Zehn tatsächliche SQLcmd-Handles plus ein separater Poolchild; kein UNKNOWN.

Keine Login-/DB-Adoption bei fehlendem Poolcleanupleasing. Der vollständige eigene
Namespace ohne Mounts wurde innerhalb derselben Deadline entfernt. Root prüfte
die tatsächlichen Quellenbytes, den vollständigen Zustand, das Receipt und neue
CID-/Namens-/SQLinputabwesenheit unabhängig. SQL-Abwesenheit bleibt NOT_ESTABLISHED,
Poolreuse/Reset/Pool-Cleanup bleiben NOT_ESTABLISHED. Historisches FAIL bleibt erhalten.

Nächster zulässiger Kandidat ergänzt ausschließlich begrenzte credential-geprüfte
Fehlerdiagnose im Receipt. Er benötigt geänderte Quellen, neuen engen Sourceschluss
und kandidatbezogene Rootadmission; das gemeinsame Sechserbudget bleibt erhalten.


## Kandidat 2: Konstruktion vor Open fehlgeschlagen

Der korrigierte Diagnosecaller liefert ein bekanntes FAIL-Receipt mit
Phase OWNER_CONNECTION und Typ System.ArgumentException; null Checkoutrecords.
Das grenzt den Fehler auf die Verbindungskonstruktion ein, ohne Rohmeldungen oder
Secrets zu exportieren. Kein Provider-/TDS-/Authfehlernachweis. Wieder zehn
SQLcmd-Handles plus ein separater Child, ein vollständiger Zustand; Root prüfte
Quellen, Receipt und frische eigene CID-/Namens-/SQLinputabwesenheit unabhängig.
SQL-/Pool-Cleanup bleibt NOT_ESTABLISHED, kein UNKNOWN. Beide historische FAILs
bleiben erhalten. Eine geschlossene lokale Constructorgegenprobe mit synthetischen
Credentials und ohne Open/SQL/ClearPool soll die konkrete Clientkorrektur vor dem
nächsten eigenen Container prüfen. Dieselbe Sechserwelle bleibt maßgeblich.


## Kandidat 3: begrenzte private Poolkomponente PASS

Der korrigierte Caller bestand im neuen eigenen SQL-17.0.5005.3-Testcontainer
sechs Checkouts in A/B/U/A/B/U-Reihenfolge. Tatsächliche Owner-DMVconnection_ids
und connect_time belegen drei physische Wiederverwendungen innerhalb der Lanes;
die drei tatsächlichen Poolkeys und Serververbindungen sind zwischen Lanes getrennt.
ClientGUIDs bleiben typisierte Metadaten ohne Gleichheits-/Differenzoracle.

Zwölf vollständige Before-/After-Ergebnisse erhalten die tatsächlichen
Login-/User-/SID-/DBbindungen: A/B jeweils eigene komplette Quelle samt VECTOR(3),
positiv authentifiziertes Unmapped null Rows. Sechs manipulierte Kontextwerte
wechseln keinen Tenant; der zweite Checkout beobachtet NULL vor jeder Reparatur.
Zwei vollständige Quellen-/RLS-/Principal-/Rechte-/Configzustände sind identisch.
Die früheren grünen Policy-/Impersonation-/REVOKE-Negativtests wurden nicht wiederholt.

Tatsächliches OwnClearPool für drei gehaltene Referenzen, Close und neue physische
Abwesenheit im Child; eine zusätzliche frische Parentabfrage bestätigt den Abbau.
Erst danach gehaltene eigene Login-Drops vor DBdrop, neue getrennte SQL-Abwesenheiten,
eigener Containerabbau und frische CID-/Namens-/SQLinputabwesenheit. Bekannte
Request-/Childenden, kein UNKNOWN. Alle Aktionen blieben innerhalb derselben
60-Sekunden-Cleanupdeadline, die bereits vor dem höchstens 40-Sekunden-Child begann.

Root prüfte unabhängig tatsächliche Receipts, vollständige Rawstates und deren
Gleichheit mit dem Messrecord, alle archivierten Effektquellen sowie neue eigene
Namespace-/Inputabwesenheit. Checkpoint3 ist auf den abgeschlossenen Ledger gebunden.
Drei eigene Container, insgesamt 37 SQLcmd-Handles und drei separate Poolchildren;
C3 allein 17 SQLcmd-Handles. Beide historische FAILs erhalten, C1/C2 SQL-/Pool-Cleanup
NOT_ESTABLISHED; ihre bestätigte eigene Namespaceabwesenheit bleibt getrennt.
Keine weiteren Kandidaten nach erreichtem PASS und keine neue Modellinferenz.

Der PASS gilt ausschließlich für diesen privaten Caller, diese vorhandene
Assembly-/Host-/Enginekombination, drei synthetische Lanes und die feste serielle
Population. Allgemeine Provider-/OS-/Authformen, Performance, ANN/Tenantseitenkanäle,
Passwort-/TLSintegrität, öffentliche Poolconsumer und volle CON-010-/TSK-009-/TP-CON-
Abnahme bleiben offen. Andere Repositories unverändert; allgemeine Entwicklung
und DGN-007 bleiben pausiert. Aktuelle Head-/Main-Gates, PRintegration, Synchronisierung
und eigener Branchcleanup sind vor Schnittabschluss erforderlich.
