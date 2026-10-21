# TSK-004: neue begrenzte VECTOR-Client-/SQL-Transportwelle

PR233 ist vollständig geschlossen: acht erfolgreiche Head-Gates und sechs
erfolgreiche Main-Workflows, Main 266e72984433d47c607af38e3ebc05912ee27419,
vollständiger Tree/FF-Synchronisierung, eigene Branches entfernt, 142 private
Dateien hashverifiziert gesichert und eigener Worktree tatsächlich archiviert.
Der [Loadervergleich](SQL_SERVER_2025_AI_LOADER_RESOLUTION_REVIEW.md) ist
nach tatsächlichem Checkpoint3/Loader-/Typmetadaten-PASS gestoppt. Die fünf
literal Runtimeassetpfade funktionieren im benannten Windows-Probehost;
Typed API (Application Programming Interface; Programmierschnittstelle), SNI, TDS (Tabular Data Stream; Übertragungsprotokoll zwischen SQL-Client und Server) und SQL wurden damit nicht geprüft.

## Explizit neue Welle, alte Fehler bleiben erhalten

Die ursprüngliche [VECTOR-Welle](SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md)
bleibt FAIL_HARD6_UNKNOWN. Keine erneute Ausführung ihres C6-Pakets, keine
weitere SQL- oder Cleanupaktion gegen seine alten Ressourcen und keine
Rekonstruktion seiner verlorenen Request-/FileNamefelder. Originale und
gestoppte Pakete aus PR229/232/233 bleiben unverändert gesichert.

Die neue Welle übernimmt ausschließlich nachweislich vorhandene Paket-/SDK-
Bytes und die belegten fünf relativen Runtimeassetpfade. Ein neuer eigener
Caller mit konkreter Quellen-/Gate-/Rootbindung verwendet diese geänderte
Grundlage und tatsächlich individuelle API-Enden. Ein Implementer, enger
unabhängiger Rootreview; sechs neue relevante Transportkandidaten, Checkpoint
nach drei, Abbruch nach sechs. Kumulativ höchstens sechs neue eigene serielle
Container, einer je Kandidat, sechs Compileprozesse bei tatsächlichen C#-
Änderungen und sechs Nativecallerprozesse. Unveränderte Programme werden nicht
erneut kompiliert. Nach erstem kohärent bestandenen begrenzten Roundtrip stoppt
die Welle; weitere Qualification bleibt ausdrücklich offen.

## Konkreter lokaler Effektumfang

Windows-Client mit den vorhandenen SDK-/Runtime-/SqlClientbytes;
SQL Server 2025/17.0.5005.3/Linux/Developer/CL170 in genau einer neuen eigenen
Testinstanz je Kandidat, nur zwei synthetische VECTOR(3)/FLOAT32-Rows und eigene
QRY-014-Testdatenbank. Das bestehende isolierte Namespacewerkzeug und die
nachweislich verfügbaren öffentlichen SQL_Server_Lab-Verträge werden vor
Ausführung lesend geprüft und konkret gepinnt. Andere Repositories bleiben
unverändert. Kein freier Providerendpoint, Download, Restore oder globaler
SDK-/Host-/Trust-/Serviceeffekt. Cloud, ONNX (Open Neural Network Exchange; Austauschformat für Modelle) und rote Hoständerungen ausgeschlossen.

Eine Read-only-Version-/Edition-/CL-/SQL-Metadatenaufnahme, native FLOAT32-
Parameterübertragung, tatsächliche typed VECTOR-Rückgabe und SQL-NULL-Kontrolle
sowie eine tatsächlich spezifische Dimensionsnegativkontrolle sind der endliche
fachliche Umfang. Native Fehlerfelder und komplette API-Enden werden erfasst;
eine beliebige Exception, DLL-/Encoding-/Prozessfehler oder leere Ausgabe
erfüllt keinen Dimensionsnegativnachweis. Fixture, konfigurierte Eingaben,
tatsächlich beobachtete API-/Serverantworten und Quellenprovenienz bleiben getrennt.
Kein float16-, Pooling-, Authrollen-, Performance- oder RAG-Abnahmeclaim.

SQLCMDPASSWORD nur als Environmentquelle; Read-only-SecureString/SqlCredential,
kein Passwort in argv, ConnectionString, Hash, Dateien oder Logs. Pooling=false,
verschlüsselte Verbindung und ausschließlich begrenztes TrustServerCertificate
für die eigene isolierte Labinstanz; keine Truststoreänderung. Vier vollständige
bytegenaue Eigentumsmarker, eigene Dateien/Objekte und tatsächliche Versions-/
Zustands-/Ergebniswitnesses vor jeder Mutation und jedem Cleanup.

Ein reguläres Lifecyclebudget von höchstens 300 Sekunden und genau ein separates
Cleanupbudget von höchstens 60 Sekunden; Compiler höchstens 60 Sekunden.
Vor Cleanup-SQL bleiben 17 Sekunden für Inspect, einmaliges Remove und frische
CID-/Namensabfragen reserviert; jede Folgeanfrage prüft ihr tatsächliches
Restbudget. Reaping bleibt innerhalb der jeweiligen absoluten Parentdeadline.
Diese konfigurierten Grenzen behaupten keine vorab garantierte Wallclockdauer.
Caller-/Request-/Namespace-/SQLcmd-PIDs beziehungsweise Sessionen und tatsächliche
Enden, configured Input-/argv-/Rawbindungen und volle Ausgangs-/Endzustände
bleiben Pflicht. Fehlende individuelle Enden, Timeout oder unklare Runtime
bleiben sticky UNKNOWN: keine folgende SQL-Anfrage und keine zweite mutierende
Recovery. Nur einmalige bereits autorisierte eigene, vollständig gebundene
Namespacecontainment darf das eigene unbekannte Szenario begrenzen; das ist
kein SQL-Cleanup-PASS. Bekannte Fehler dürfen ausschließlich bei geänderten
relevanten Eingaben innerhalb der Sechsergrenze weiter untersucht werden.
Tatsächlich erhaltene API-Exceptions erhalten eigene UTC-/Dauer-/Fehlerrecords;
ein belegtes API-THREW ist getrennt vom Server-/Transportende und räumt einen
unbekannten Serverzustand nicht aus. Sichere vollständige SqlErrorfelder bleiben
erhalten, ohne Secrets oder beliebige Exceptions als Dimensionsbeleg umzudeuten.

## Gates und verbleibende Grenzen

Quellen, tatsächliche Dependency-/Layout-/SDK-/Ref-/Containerbild-/Umgebungs-
Pins, positive/negative Purekontrollen, enge unabhängige Rootprüfung und konkrete
Admitbindungen vor Kompilierung beziehungsweise Nativeausführung. Vor einem
ersten Setup eigene frische Abwesenheit und versionsgebundener Preflight;
nach bekanntem Lauf tatsächlicher markergebundener Restore/Cleanup und frische
SQL-/CID-/Namespace-/Inputabwesenheit. Kein früheres PASS als Ersatz für einen
aktuell fehlgeschlagenen oder unbekannten Zustand.

Typed API und tatsächlicher SQL-Roundtrip können separat qualifiziert werden.
Ohne unabhängigen Transportcapture wird kein spezifischer TDS-Wiretoken
behauptet. Andere Builds, Editionen, Client-/Server-OS (Operating System; Betriebssystem), float16, Provider,
Performance, volle TSK-004-/Workstream-/Releaseabnahme bleiben offen.
Der Schnitt begann SOURCE_PREPARATION_ONLY mit null neuen Effekten.
Modell-/Tokenverbrauch UNKNOWN. Vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/
Sicherungs-/Worktreeclosure und unmittelbarer nächster zulässiger Schritt bleiben
verbindlich; keine neue breite CI- oder Runtime-Matrix aufgrund dieses Diagnoseplans.

## Tatsächlicher C1-Befund: FAIL / UNKNOWN_STOP

64 Precompile-Sourcepins, 168 bestehende Refs und 28 Runtimeassets geprüft;
neun neue reine Methoden normal und sechs geschützt unter `-O` bestanden.
Danach ausschließlich zwei betroffene Gateprüfungen je normal/`-O` bestanden;
ursprüngliche Rawbelege erhalten. Enge unabhängige Source-/Privacyprüfung und
getrennte konkrete Compiler-/Nativeadmissions vor beiden Effekten abgeschlossen.

Ein Compiler PID (Process Identifier; Prozesskennung) 40932/poll 0/rc 0 in 0,586720 Sekunden, kein Timeout/UNKNOWN;
69632-Byte-Artefakt und alle Sources aktuell. Zwei tatsächliche CS1701-Warnungen
für `System.Data.Common` und `System.Runtime` 9→10 bleiben erhalten. Sie werden
nicht als fehlerfreie Versionsqualifikation oder aufgehobene Supportgrenze behandelt.

Ein neuer eigener Container und ein Topcaller PID 55512/poll 1/rc 1 in
11,305835 Sekunden, kein Top-Timeout/Collector-UNKNOWN. Sechs bekannte SQLcmd-
Prozessenden, ein vollständiger Ausgangszustand und Child PID 57608/poll 1/rc 1
ohne Child-Timeout. Tatsächliche Runtime .NET 10.0.12 und eigene literal
SqlClientdatei/Assemblyversion 6.0.0.0 bestätigt. OPEN endet API_RETURNED;
der anschließende Session-READER hat ApiEnd RETURNED, aber End UNKNOWN und
keinen Endzeitpunkt. Der Topreceipt hält REQUEST_END_UNKNOWN und
UNKNOWN_OR_UNCLASSIFIED/SqlErrors[]; der konkrete ursprüngliche Exceptiontyp
und die Fehlerstelle werden nicht nachträglich als gemessen rekonstruiert.

Keine VECTOR-Rows, NULL-/Dimensionskontrolle oder Source-/Markernegativkontrolle
qualifiziert. Nach dem Child null weitere SQL-Aufrufe. Genau eine vollständig
gebundene eigene Namespaceentfernung `rm --time=0`, tatsächlicher PID 66400/
poll 0/rc 0; anschließend frische ganze CID- und Namensabfragen leer. Insgesamt
acht gehaltene Namespaceprozesse mit bekannten Enden. Das begrenzt den eigenen
Container, belegt aber keinen SQL-Drop oder SQL-Datenbankabwesenheitsnachweis:
SQLcleanup NOT_ESTABLISHED, DatabaseAbsent false, InputsAbsent false,
Ledger closed false/unknown true. Eingaben, Originalresultat und alle 68
Native-Sourcepins bleiben unverändert gesichert; Root hat die tatsächlichen
Resultat-/Namespace-/End-/Scopebindungen geprüft, ohne einen SQL-Replay.

UNKNOWN_STOP nach C1, C2–C6 dieser Welle nicht zugelassen. Keine weitere SQL-
oder Cleanupaktion gegen ihre alten Ressourcen, kein stiller Budgetreset.
Nach vollständiger Integration folgt ausschließlich eine unabhängige
quellengebundene Prüfung der Sessionreader-Typen und der Fehlererfassung;
Compiler-/SQL-/Container-/Caller-/Modelleffekte sind in diesem Folgeschritt null.
Die ursprüngliche Fehlerursache bleibt unbewiesen; typisierte API-, TDS-,
SQL-, volle TSK-004- und Workstreamabnahmen bleiben offen.
