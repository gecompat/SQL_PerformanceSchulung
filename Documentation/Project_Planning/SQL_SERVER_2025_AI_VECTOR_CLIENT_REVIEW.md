# TSK-004: isolierte native VECTOR-Clientkomponente

PR227 vollständig geschlossen:8Head/6Main, Main
dd77b60a5483951e27b3dbc256744e5265fd3d55, voller Tree/FF/Branches,
Belege gesichert und eigener Worktree archiviert. Unmittelbar folgt ein
begrenzter neuer Clientpfad; die Pool-UNKNOWNwelle wird nicht wiederaufgenommen.

## Abhängigkeit und Quellenvorbereitung

Zwei begrenzte vorhandene Cacheorte und der eigene Repositoryscope enthalten
keinen verfügbaren Microsoft.Data.SqlClient ab6.1; nur ein bestehendes5.2.2-Paket
wurde über Nuspecmetadaten gelesen, ohne Assemblyload. Vorhandenes .NET-SDK (Software Development Kit; Entwicklungswerkzeuge und Bibliotheken)
10.0.401 ist read-only bestätigt. SRC072 dokumentiert getrennt native
float32-Clienttypen ab6.1 und ältere JSON-Kompatibilität.

Gemäß DEPENDENCY_POLICY wird die etablierte Laufzeitabhängigkeit als MATERIAL
behandelt. Version6.1.4 wird fest auf offizielle NuGet-/Releasequellen gebunden;
MIT-Hauptlizenz, transitive Lizenzen, Paket-/Dateihashes, Lockgraph und vorhandene
Auditbefunde werden vor tatsächlichem Treiberlauf geprüft. Compiler-/Cache-/
CLIhome-/HTTPcachedateien bleiben im eigenen ignorierten Runtimeverzeichnis.
Keine globale NuGet-/SDK-/Treiberinstallation, PATH-/Service-/Truststore-/
Hostkonfiguration, keine redistribuierten Paket-/DLLartefakte.

Ein initialer Restoreversuch/max120s, höchstens40Pakete/150MB; fehlgeschlagene
oder unklare Netzwerk-/Audit-/Lizenzprüfung stoppt den betroffenen Pfad statt
eines unkontrollierten Retry. Ein Compileraufruf/max90s ohne Treiber-Open/SQL.
Nur Paketidentitäten werden an die offizielle NuGetquelle gesendet; keine
Labordaten/Secrets/Modelle, keine bezahlte API (Application Programming Interface; Programmierschnittstelle). Exit: eigener Quell-/Lock-/
Provenienzvertrag und eigene lokale Dateien, kein Host-Rollback nötig.

Der initiale Restore C1 endete nach 0,974s mit Returncode1 und null Paketen:
`NuGet.Configuration.ConfigurationDefaults` meldete einen fehlenden `path1`.
Die vollständigen Originalkanäle bleiben privat erhalten; Compile, Lockgraph,
Lizenz-/Auditprüfung und Provider-/SQL-/Containerläufe wurden nicht erreicht.
Die Ursache ist zunächst nicht belegt. Unter der erweiterten lokalen
Wellenfreigabe ist genau ein geänderter C2-Restore nach Quellenbegründung einer
fehlenden Konfigurationswurzel zulässig. Zusätzliche ENV-Wurzeln zeigen dabei
ausschließlich auf eigene Runtimeverzeichnisse. Grenzen je Restore bleiben
120s/40Pakete/150MB; kein unveränderter Retry und keine globale Konfiguration.

C2 erreichte laut tatsächlichem SDK-Output 31 installierte Pakete und einen
Restore ohne Warnungen oder Fehler. Die eigenen Dateien überschritten jedoch
die 150MB-Grenze: Root beobachtete 166144217Bytes. C2 bleibt deshalb FAIL;
sein Prozessendnachweis ist vor weiterer Ausführung erforderlich. Der geänderte
C3 erweitert ausschließlich den eigenen lokalen
Dateiscope auf 300MB einschließlich vorhandener Caches, Belege und Compileroutput.
Max40Pakete bleiben erhalten. Nach bekanntem C2-Ende darf der vorhandene
Lock-/Paketbestand geprüft und einmal ohne Restore kompiliert werden. Kein
weiterer Download, keine Löschung zur nachträglichen Umdeutung des C2-FAIL.

Die C2-Endbindung ist ausdrücklich quellengestützt: Der gehaltene Helper endete
mit Returncode1; der SDK-Output wurde erst nach erfolgreicher Rückkehr von
`Popen.communicate()` geschrieben. Root prüfte die tatsächlichen Wrapper-, Raw-
und Standardbibliotheks-Hashes sowie deren `wait`-Pfad. Die ursprüngliche SDK-PID (Process Identifier; Prozesskennung),
sein Returncode und eine separate finale `poll`-Aufnahme fehlen und wurden nicht
rekonstruiert. Diese eng begrenzte Endbindung ersetzt keine entsprechende
Native- oder TDS-Attestierung. Die Konfigurationsursache ist durch den offiziellen
[ConfigurationDefaults-Code](https://github.com/NuGet/NuGet.Client/blob/dev/src/NuGet.Core/NuGet.Configuration/Settings/ConfigurationDefaults.cs)
und den [NuGetEnvironment-Pfad](https://github.com/NuGet/NuGet.Client/blob/dev/src/NuGet.Core/NuGet.Common/PathUtil/NuGetEnvironment.cs)
belegt; deren aktueller Stand ist keine Attestierung des installierten SDK-Binaries.

## Tatsächlicher Sourceabschluss am Checkpoint3

C3 bestand mit einem einzigen Compile `--no-restore`: tatsächliche SDK-PID,
finales `poll=0`, Returncode0 und 3,3033s wurden am gehaltenen Prozess erfasst.
Der eigene Dateiscope betrug 166584595Bytes, bei31 gehaltenen Paketversionen.
27 davon sind im net10.0-Lockgraph ausgewählt; zusätzliche aufgelöste Versionen
werden davon getrennt geführt. Kein weiterer Restore oder Paketdownload.

Paket-, Nuspec-, Lock-/Assets-, Lizenz-/Notice- und758 Paketdateihashes sind privat
gebunden. Raw-ZIP-SHA512 und NuGet-ContentHash sind getrennte Formate: ersterer
passt zur gehaltenen `.nupkg.sha512`, letzterer zum Lockgraph. Alle31 Pakete
enthalten Signaturbytes; eine unabhängige Zertifikatskettenprüfung ist damit
nicht bewiesen. Tatsächliche Audit-GET-/OK-Kanäle für Index, Basis und Update und
null SDK-Warnungen sind erhalten; das ist keine allgemeine Sicherheitsgarantie.

29 Nuspecs nennen MIT. Die zusätzlich geladene, für net10.0 nicht ausgewählte
ProtectedData4.5.0-Version enthält einen tatsächlich gelesenen MIT-Lizenztext.
SNI6.0.2 enthält eigene Microsoft-Lizenzbedingungen für Entwicklung und Test;
die drei nativen Windows-DLLs sind mit Größe und Hash gebunden. Es werden keine
Pakete, fremden DLLs oder Lizenztexte redistribuiert. Der begrenzte eigene
Source-/Compilepfad folgt den [NuGet-Supply-Chain-Regeln](https://learn.microsoft.com/en-us/nuget/concepts/security-best-practices).

Die private C#-Library hat keinen Main-/CLI-Einstieg und wurde nicht ausgeführt.
Sie übersetzt die tatsächlichen SqlVector-/Parameter-/Reader-APIs, volle eigene
Eigentumsmarker und einen Vergleich aller sechs float32-Koordinaten mit JSON (JavaScript Object Notation; strukturiertes Textformat).
Null-/Dimensionsbeobachtungen sind vorbereitet, noch nicht empirisch bestanden.
Eine angenommene Dimensionsabweisung oder ein aggregierter Await-/Close-Record
ersetzt kein eingefrorenes Negativoracle und keine individuelle Requestendbindung.

Vier neue reine SDK-ENV-/Handle-/Budget-/Reservationsgegenfälle bestanden normal
und unter `-O`; ausschließlich Fakeprozesse. Root las Quellen, Oracles und
Originalkanäle unabhängig für die konkreten Dependency-/Credential-/Endrisiken.
Kein unveränderter Compile oder Test wurde für dieses Review wiederholt.
C1/C2 bleiben FAIL; C3 ist nur SOURCE_ONLY-PASS. Provider-CLR, Open, SQL,
Container und Modelle: null. Der Pool-UNKNOWN-Pfad bleibt gestoppt.

Aktuelle Fünf-Dateien-Privacy, PR-/Main-Gates, vollständige Übernahme,
FF-Synchronisierung, eigene Branches und gesicherter Worktreeabschluss sind
die verbleibenden Integrationsgates. Die betroffenen Änderungen sind
Planungs-/Quellennachweisdokumente; keine neue rote CI (Continuous Integration; automatisierte Integrationsprüfungen) oder SQL-Matrix.
Unmittelbarer Folgeschritt ist ein eigener begrenzter Nativecaller mit aktuellen
Oracles, Deadline-, Source-/Input- und tatsächlichen Cleanupgates vor Admission.

## Endliche spätere Nativegrenze

Ein Implementierungsowner, enger unabhängiger Rootreview für Supply Chain,
Credential-/Typ-/Resultat-/UNKNOWN-/Eigentums-/Cleanupbindung.6relevante
Quellen-/Nativekandidaten/Checkpoint3/hard6, nach gesonderter tatsächlicher
Rootadmission maximal6neue eigene serielle Container/je1Kandidat. Erst werden
Abhängigkeiten und Code ohne CLRproviderprobe oder SQL vorbereitet.

Ziel: eigener fester17.0.5005.3-Container mit ganzen CID/Owner/Ressourcen/Loopback/
NoMounts und eine neue eigene vierfach bytegebundene DB. Nur drei synthetische
float32-Koordinaten je kleinem Record, native SqlVector-/Parameter-/Reader-APIs
getrennt von JSONvergleich; konkrete Negativen und echte Restore-/Cleanupbelege.
Keine Index-/Preview-/Model-/Login-/Hosteffekte.300snormal/einmal60sCleanup,
UNKNOWNsticky/keine Folge-SQL, tatsächliche eigene Pool-/DB-/SQL-/CID-/Namens-/
Inputclosure. Native Typ-API ist keine unabhängige TDS-Wireattestierung oder
Performancegarantie. Die genauen Oracles werden vor Native eingefroren.

Aktuelle Source-/Dependency-/Privacy-/betroffene Checks/Rootgates zuerst;
Nativequalifikation bleibt NOT_ESTABLISHED. Integration über aktuellenPR/Main/
vollenTree/FF/eigeneBranches/gesicherteBelege/Worktreecleanup. Keine Änderungen
an anderen Repositories, keine Cloud-/ONNX-/roten Hosteffekte. Unbekannter
Modell-/Tokenverbrauch bleibt UNKNOWN; volleTSK004-/Workstreamabnahme offen.
