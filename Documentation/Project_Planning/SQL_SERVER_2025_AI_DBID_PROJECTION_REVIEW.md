# TSK-004: explizite DB-ID-Projektion innerhalb des gemeinsamen Restbudgets

PR236 vollständig geschlossen: acht Head-/sechs Main-Gates, Main
11ec85c16f2a8232f0cd28aa16bb0dde9f19f0b2, vollständiger Tree/FF/Branches,
125 private Dateien hashverifiziert gesichert und eigener Worktree archiviert.
Die [R1/Gesamt2-Akte](SQL_SERVER_2025_AI_READER_TRANSPORT_REVIEW.md) bleibt
FAIL/UNKNOWN_STOP; Originale, Stop, Eingaben und alte Ressourcen unverändert,
kein weiterer Aufruf ihres Pakets oder SQL-/Cleanup gegen alte Ressourcen.

## Geänderter eigener Caller, kein Budgetreset

Nur explizite `CONVERT(int,DB_ID())`-Projektion statt der im Driver als smallint/
System.Int16 beobachteten ursprünglichen DB_ID-Spalte. Microsoft dokumentiert
int; Ursachen der Dokumentations-/Driverabweichung bleiben unbewiesen. Alle
acht tatsächlichen Basistyp-/CLRfelder, getrennte Reader-Read-/Projektions-/
Dispose-/Fehlerenden und vollständige Gesamt-API-Enden bleiben Pflicht.
Eigene neue Input-/Receipt-/Scope-/Rootbindungen dürfen alte Records nicht
als neue Proben zulassen. Keine native Typattestierung aus reinen Fixtures.

Ein Implementer/enger unabhängiger Rootreview, sechs relevante Sourcekandidaten,
Sourcecheckpoint3/hard6. Das gemeinsame Nativebudget behält beide früheren
Compiler/Container/Caller: höchstens vier zusätzliche Gesamt3–6, keine neue
Sechserwelle. Der erste eigene Lauf entspricht fortgeführtem R2/Gesamt3 und
erreicht den vorgeschriebenen Gesamtcheckpoint3. Rootcheckpoint mit tatsächlicher
Evidenz danach, keine automatische vierte Probe. Nach erstem kohärentem
begrenztem Roundtrip-PASS Stop; UNKNOWN stoppt auch dieses neue Paket,
keine Folge-SQL und höchstens eine vollständig gebundene eigene Containment.
Alte Server-UNKNOWN-Zustände bleiben sichtbar und werden dadurch nicht gelöst.

## Endlicher lokaler Effekt- und Prüfumfang

Nur vorhandene gepinnte SDK10.0.401-/Runtime10.0.12-/SqlClient6.1.4-Bytes mit
fünf belegten literal Assetpfaden, aktuelle öffentliche SQL_Server_Lab-/
Namespace-/SQLcmd-Verträge; andere Repositories unverändert. Keine Downloads,
Restore, Installation, Cloud, ONNX, Modelle oder globale Host-/Trusteffekte.
Ein neuer eigener SQL17.0.5005.3/Linux/Developer-Container je Versuch, CL170,
zwei synthetische VECTOR(3)/FLOAT32-Rows, frischer 16Hex-RunToken und
SQLPERF_LAB_QRY014_<TOKEN> mit vier vollständigen bytegenauen Markern.
Volle eigene CID-/Name-/Owner-/Image-/Loopback-/Ressourcenbindung vor Effekten.
SQLCMDPASSWORD nur ENV/readonly SecureString/SqlCredential, Poolingfalse/TLS
und ausschließlich eigene begrenzte Lab-TrustServerCertificate-Ausnahme.

Die konkrete Dimensionsnegative bleibt ein VECTOR(2)-Parameter gegen VECTOR(3)
mit tatsächlicher spezifischer SQL-Abweisung, vollständigen Fehlerfeldern und
unveränderten zwei Ausgangsrows. Ihre TRY/CATCH-Ausführungsebene wird vor Native
an der Primärquelle geprüft: gegebenenfalls feste parametrisierte untere
sp_executesql-Ebene innerhalb desselben eigenen Guards/Transactions/Rollback,
keine frei vorgegebenen Texte, neuen Objekte oder erweiterten Seiteneffekte.
Sourceprüfung ist kein Beweis eines zuvor tatsächlich beobachteten Compilefehlers.
Beliebige Exceptions, Encoding-/Loader-/Prozess-/Rechtefehler erfüllen die
Dimensionsnegative weiterhin nicht.

Source-delete/51003/Restore und vier vollständige Marker-DML-/Cleanup-
Rejections51004 mit tatsächlichen Vollstates/Restores, frische SQL-Abwesenheit
vor Setup und nach tatsächlichem markergebundenem Drop, ganze CID-/Name-/Input-
Abwesenheit. Kein SQLcleanup-PASS aus bloßer Containerabwesenheit. Alle tatsächlichen
PID-/poll-/rc-/Raw-/Input-/Requestenden und Privacy vor Speicherung bleiben Pflicht.
Normal300s plus genau eine Cleanupdeadline60s/17s Namespace-Reserve/pro Call
tatsächlicher Restbudgetcheck; Compiler60s inklusive Reaping, kein Reset oder
vorab garantierter Wallclockclaim. Beide alten Compilerwarnungen bleiben erhalten.

Jetzt SOURCE_PREPARATION_ONLY, zusätzliche Compiler/Container/SQL/Caller null.
Nur neue betroffene Purekontrollen normal/geschützt unter `-O`; alte grüne Suiten
und historische Runtime nicht wiederholen. Getrennte Root-Compiler-/Native-
Admissions nach aktuellen Source-/Pin-/Test-/Privacy-/Risikonachweisen.
API-/SQL-Kohärenz ersetzt keinen unabhängigen Wiretoken-/TDS-Beleg; float16,
andere Versionen/Editionen/OS, Provider/Rollen/Pooling/Performance/RAG und volle
TSK-004-/Workstream-/Releaseabnahmen bleiben offen. Modell-/Tokenverbrauch UNKNOWN.
Aktuelle PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktreeclosure und
unmittelbarer nächster zulässiger Schritt bleiben verbindlich.

## Tatsächlicher Gesamtcheckpoint3 und Paketstop

Gesamt3 tatsächlich FAIL/UNKNOWN_STOP; Pflichtcheckpoint3 durch unabhängigen
Rootreview geschlossen. Compiler46412/poll0/rc0/0,712391s, zwei CS1701-WARNs;
Top57876/poll1/rc1/12,640812s, Child65112/poll0/rc0, kein Timeout.
Child meldet acht tatsächliche Typfelder einschließlich DB-ID-int/Int32,
31 vollständig beendete Readerteilschritte und zehn API-Enden, zwei Native-/
JSON-Vektoren vor/nach unverändert, NULL(3) und spezifische SQL-Abweisung42204
mit allen sechs Fehlerfeldern. Der Parent verwirft bereits OPEN:
tatsächliches Encrypt=True, eingefrorenes Oracle erwartet Encrypt=Mandatory.
Die isolierte In-Memory-Gegenprüfung aller übrigen Recordfloors ist kein
geänderter tatsächlicher Lauf oder Runtime-PASS; Originale/UNKNOWN bleiben.
Sechs bekannte SQLcmdenden/ein Vollstate/keine Controls, null Folge-SQL;
eine volle eigene Containment und frische ganze CID-/Namensabwesenheit.
SQLcleanup NOT_ESTABLISHED/DB- und Inputabwesenheit false/closed false.
Alle 71 Sources und Originalbytes erhalten. Kumulativ drei Compiler/Container/
Caller, drei verbleibende Gesamt4–6; kein automatischer vierter Versuch.
Aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach ausschließlich neue eigene Source-/Scopebasis mit
quellengeprüfter präziser OPEN-Auswertung, fortgeführten prior3/rest3 und
neuen Rootgates; kein Aufruf des gestoppten Pakets oder alter Ressourcen.
Volle Runtime-/Wire-/TSK-004-/Workstreamabnahme bleibt offen.
