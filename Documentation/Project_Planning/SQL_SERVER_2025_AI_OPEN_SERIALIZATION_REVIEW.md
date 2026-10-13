# TSK-004: präzise OPEN-Serialisierung innerhalb Gesamt4–6

PR237 ist vollständig geschlossen: sieben Head-/fünf Main-Gates, Main
7b9e19086d4453440fa698233168ab8ae0b3caaa, voller Tree/FF/Branches,
128 private Dateien hashverifiziert gesichert, eigener Worktree tatsächlich
archiviert. Gesamt3 bleibt FAIL/UNKNOWN_STOP; sein Pflichtcheckpoint3 ist
an tatsächlichen Originalen unabhängig geschlossen. Alte Pakete/Originale/
Ressourcen bleiben unverändert und werden nicht erneut aufgerufen.

## Konkret geänderte eigene Grundlage

Der Parent von Gesamt3 verwirft OPEN ausschließlich am eingefrorenen
Encrypt=Mandatory-Vergleich, während der tatsächliche Client Encrypt=True
serialisiert. Der Herstellerquellstand [SqlConnectionEncryptOption v6.1.4](https://github.com/dotnet/SqlClient/blob/v6.1.4/src/Microsoft.Data.SqlClient/src/Microsoft/Data/SqlClient/SqlConnectionEncryptOption.cs)
hält Mandatory intern als True und gibt diesen Wert bei ToString zurück.
Die [API-Dokumentation 6.1](https://learn.microsoft.com/en-us/dotnet/api/microsoft.data.sqlclient.sqlconnectionencryptoption?view=sqlclient-dotnet-core-6.1)
beschreibt die boolsche Zuordnung true zu Mandatory. Für genau die gepinnten
6.1.4-Bytes wird deshalb der erwartete serialisierte Wert auf True korrigiert.
Kein permissiver beliebiger Encrypt-Wert: fehlend, False, Optional, Strict,
unbekannt, zusätzliche oder doppelte Schlüssel sowie andere Verbindungs-
und Kontextwerte werden weiterhin abgewiesen. Keine Abschwächung von TLS
oder der bereits auf eigene lokale Tests begrenzten TrustServerCertificate-Ausnahme.
Sourcevertrag ist kein unabhängiger Nachweis tatsächlich ausgehandelter TLS-/TDS-Wiretoken.

Neue eigene V4-Input-/Receipt-/Scopebindungen, frische Source-/Root-/Raws und
neue Ressourcen; originale V3-Belege niemals ändern oder nachträglich als
PASS behandeln. Der bereits tatsächlich beobachtete Clientteil – acht Typfelder,
31 Readerteilschritte, zehn API-Enden, zwei Native-/JSON-Vektoren, NULL(3) und
spezifische Dimensionsabweichung42204 – bleibt vom Parent-Gesamt-PASS getrennt.
Neue betroffene Purekontrollen müssen die konkrete Serialisierung, manipulierte
Verschlüsselungs-/Schlüssel-/Kontextwerte und alte Receipt-/Scopeformen prüfen.
Alte grüne Suiten oder Runtimeproben nicht wiederholen. Ein Implementer und
enger unabhängiger Rootreview, höchstens sechs Sourcekandidaten/Checkpoint3/hard6.

## Fortgeführtes Gesamtbudget und Effekte

Drei vorherige Compiler/Container/Caller und geschlossener Pflichtcheckpoint3
werden unverändert weitergezählt. Höchstens drei zusätzliche eigene Gesamt4–6,
keine neue Sechserwelle. Zuerst eine neue Sourcevorbereitung mit null neuen
Compiler-/CLR-/SQL-/Container-/Modellaufrufen; separate Root-Compiler- und
Nativegates vor jedem tatsächlichen Effekt. Nach erstem kohärenten begrenzten
Roundtrip-PASS stoppen. UNKNOWN stoppt das neue Paket sofort, null Folge-SQL,
höchstens eine vollständig gebundene eigene Containment. Bekannter FAIL darf
nur mit neuer konkreter Ursache/geänderter eigener Grundlage innerhalb Restbudget
fortgeführt werden; nach Gesamt6 harter Stop ohne stilles Zurücksetzen.

Nur vorhandene gepinnte SDK10.0.401/Runtime10.0.12/SqlClient6.1.4-Bytes und
fünf literal Assets; aktuelle öffentliche SQL_Server_Lab-Verträge. Keine
Downloads/Restore/Installation/globalen Host-/Trust-/Cloud-/ONNX-/Modellwirkungen,
andere Repositories bleiben unverändert. Neue eigene SQL17.0.5005.3/Linux/
Developer-Container, CL170, zwei synthetische VECTOR(3)/FLOAT32-Rows, 16Hex-
RunToken und eigene SQLPERF_LAB_QRY014_<TOKEN>-DB. Ganze CID/Name/Owner/Image/
Loopback/4CPU/6GiB/keine Mounts, vier vollständige bytegenaue Eigentumsmarker
vor mutierenden Effekten. SQLCMDPASSWORD nur ENV/readonly SecureString/
SqlCredential, keine Secrets in Argv/ConnectionString/Raw/Hashes.

Explizite int-Projektionen/acht tatsächliche SQL-/CLRtypen und 31 tatsächliche
Readerenden, unabhängige Parent-DB-ID, zehn Gesamt-API-Enden und sichere
Fehler-/Dispose-/stickyUNKNOWN-Auswertung bleiben vollständig erhalten.
Feste parametrisierte untere sp_executesql-Dimensionsnegative mit Guard/
Transaction/Rollback/sechs Fehlerfeldern; tatsächliche spezifische Abweisung
und unveränderte Rows. Source-delete51003/Restore, vier Marker-DML-/Cleanup-
Rejections51004/volle States/Restores und tatsächlicher markergebundener Drop/
frische DB-, ganze CID-/Name-/Inputabwesenheit bleiben erforderlich.

Compiler60s inklusive Reaping; Normal300s plus genau eine Cleanupdeadline60s,
17s Namespace-Reserve und jeder Aufruf nur im tatsächlichen Restbudget.
Keine vorab garantierte Wallclockzeit. Beide CS1701-WARNs sichtbar.
Volle TSK-004-/Wire-/float16-/andere OS/Build/Edition-/Provider/Rollen/Pooling/
Performance/RAG-/Releaseabnahmen bleiben offen; Modell-/Tokenverbrauch UNKNOWN.
Vollständige aktuelle PR-/Head-/Main-/Tree-/FF-/Branch-/Belegsicherungs-/Worktree-
Integration und unmittelbarer nächster zulässiger Schritt bleiben Pflicht.

## Tatsächlicher Gesamt4-PASS und Stop

Gesamt4 tatsächlich BOUNDED_ROUNDTRIP_PASS; STOP_AFTER_ROUNDTRIP_PASS,
keine fünfte oder sechste Probe. Compiler57768/poll0/rc0/0,648789s,
91.136-Byte-Artefakt und zwei erhaltene CS1701-WARNs. Top36268/poll0/rc0/
33,569191s und Child63688/poll0/rc0, kein Timeout oder UNKNOWN.
Acht tatsächliche SQL-/CLRtypfelder, 31 vollständig beendete Readerteilschritte
und zehn API-Enden; zwei Native-/JSON-FLOAT32-Vektoren vor/nach unverändert,
NULL(3) und spezifischer SQL-Dimensionsfehler42204/16/1/Line1/ProcedureNULL
mit vollständiger Nachricht. 52 bekannte SQLcmdenden/24 Vollstates,
Source-delete51003/Restore und vier vollständige bytegenaue Markercontrols:
je tatsächliche DML- und Cleanup-Abweisung51004, unveränderte Vollstates
nach Abweisung und vollständiger Restore. Echte markergebundene DB-Löschung,
frische DB-/ganze CID-/Name-/Inputabwesenheit; SQLcleanup
ACTUAL_DROP_AND_FRESH_ABSENCE, UNKNOWNfalse/Ledgerclosedtrue.
Alle 71 Quellen vor/nach identisch und unabhängiger Root-Originalreview bestanden.
Nachgelagerte reine Recordlese scheiterte an 1-MB-Grenze; dieser Befund bleibt
erhalten. Ausschließlich geänderte begrenzte 10-MB-Lese, kein neuer Nativeaufruf,
unverändertes 6.461.458-Byte-Original. Kumulativ vier Compiler/Container/Caller;
zwei ungenutzte Kandidaten werden nach dem ersten kohärenten PASS nicht verbraucht.
Alte UNKNOWN/fehlende SQLcleanups und geschlossener Pflichtcheckpoint3 bleiben.
Wire-/ausgehandelte TLS-/allgemeine Runtime-/float16-/TSK-004-Abnahme offen.
Aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach unabhängige öffentliche Lesehilfe für den tatsächlich
belegten Clientweg und seine Versions-/TLS-/Abnahmegrenzen, ohne neue Runtime.
