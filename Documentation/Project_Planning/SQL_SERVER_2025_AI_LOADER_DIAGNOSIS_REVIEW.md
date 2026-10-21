# TSK-004: getrennte lokale Assembly-Ladediagnose

PR231 ist vollständig geschlossen: zehn erfolgreiche Head-Gates und ein
bewusster SQL-Runtime-SKIP, sieben erfolgreiche Main-Workflows mit bestätigtem
Runtime-SKIP, Main ee6e0cecfe24cf08f6284ba32bf475e15577f410, vollständiger
Tree/FF-Synchronisierung und eigene Branches entfernt. 138 private Dateien sind
hashverifiziert gesichert; eigener Worktree tatsächlich archiviert. Der
[Clientlayoutvertrag](SQL_SERVER_2025_AI_CLIENT_LAYOUT_REVIEW.md) bleibt
COHERENT/WARN und STOPPED_AFTER_C2, FileNotFound-Ursprung UNPROVEN.

## Konkrete unabhängige Frage

Der Depsgraph nennt relative Assetpfade. Der .NET-Host bildet daraus
Suchinformationen für AssemblyLoadContext.Default. Ein fehlender wörtlicher
Unterpfad beweist deshalb allein noch keinen tatsächlichen Auflösungsfehler.
Dokumentiert: [Microsoft Learn: Default probing](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/default-probing)
und [Managed assembly loading algorithm](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/loading-managed),
abgerufen am 2026-10-13. Statische Referenzen können zu unterschiedlichen
Zeitpunkten geladen werden; eine getrennte Diagnose ist kein Replay des alten
SQL-Clients und rekonstruiert dessen verlorene Exceptiondetails nicht.

Eine neue kleine lokale Diagnose lädt ausschließlich die fest gepinnte
Microsoft.Data.SqlClient-Assembly im Default-Kontext und prüft benannte
Typmetadaten. Sie erstellt keine Connection, keinen SqlCommand und keinen
SqlCredential, ruft kein Open/Execute und keinen nativen SNI-Loader auf.
Sie nimmt keine Credentials entgegen. Die alte VECTOR-Welle bleibt
FAIL_HARD6_UNKNOWN; keine SQL- oder Cleanup-Wiederaufnahme.

## Endlicher Umfang und tatsächliche Grenzen

Ein Implementierungsverantwortlicher, enger unabhängiger Rootreview für
Load-/Dateibindung, sichere Fehlermetadaten, Prozessenden und Effektgrenzen.
Sechs relevante neue Diagnosekandidaten, Checkpoint nach drei und Abbruch nach
sechs. Je Kandidat höchstens ein tatsächlich gehaltener Compilerprozess bei
geänderten C#-Eingaben und ein Diagnoseprozess, jeweils höchstens 60 Sekunden.
Keine erneute Kompilierung unveränderter Programme. Jede weitere Diagnose
braucht geänderte relevante Eingaben oder neue konkrete Evidenz; kein
unveränderter Retry. Nach erstem kohärentem Diagnoseergebnis hält der Schnitt an.

Nur erhaltene lokale SDK-/Framework-/Paketbytes in einer neuen eigenen privaten
Kandidatenakte; vollständige SHA-/Versions-/Quellen-/Apppins vor Ausführung.
Originale aus PR229 und PR231 bleiben unverändert. Keine Installation, Restore,
Downloads, Netzwerk-, SQL-, Container-, Providerendpoint-, Modell-, ONNX- oder
globalen Hoständerungen. Ein Prozess verwendet einen begrenzten eigenen
Environmentbestand ohne Credentials, Startuphooks oder zusätzliche Depspfade.
SDK-Paketmetadaten und die tatsächlich verwendeten Compilerbytes werden gelesen
und vollständig gebunden; das ist kein ausgeführter SDK-CLI-Versionsnachweis.
Der Diagnoseprozess attestiert seine tatsächliche Runtime separat. Eine
Versionsannahme aus einem Verzeichnisnamen genügt nicht.

Der neue Probehost verwendet einen eigenen geänderten Programmeinstieg mit
äußeren Catchgrenzen vor dem Typzugriff. Phasen und tatsächliche API-Enden
bleiben getrennt sichtbar. Fehlermetadaten enthalten ausschließlich feste
Fehlertypen und eine geprüfte Allowlist einfacher Assemblynamen. Keine Messages,
Stacktraces, freien FileName-/Hostpfade oder Fusionlogs in öffentlichen Artefakten.
Unbekannte Namen bleiben ausdrücklich unbekannt. Tatsächlich geladene Dateien
müssen zur eigenen Kandidatenakte und deren vollständigen Pins passen.

Ein bekannter Loader-FAIL ist kein SQL-FAIL; ein unbekanntes Prozessende bleibt
UNKNOWN und stoppt den Schnitt. Ein Loader-PASS gilt ausschließlich für diesen
benannten Probehost und seine Typmetadaten. Typed API (Application Programming Interface; Programmierschnittstelle), native SNI-/TDS-/SQL-
Transport, Provider, Performance und volle TSK-004-Abnahme bleiben
NOT_ESTABLISHED. Keine Behauptung über die alte FileNotFound-Ursache ohne deren
tatsächlich erhaltene Fehlermetadaten.

## C1 tatsächlich abgeschlossen: bekannter Loader-FAIL

Die drei vor Ausführung gefundenen Reviewlücken wurden geschlossen:
case-insensitive ENV-Auswahl mit tatsächlichem Pflicht-SystemRoot, vollständige
Ownfile-/Name-/Version-/SHA-Bindung bei PASS und feste sichere Postend-Fehlercodes
mit erreichter Phase. Neun neue Puremethoden normal und sechs optimiert
bestanden; tatsächliche Test-PIDs 42400/13944, bekannte Enden und Rawkanäle.
Keine unveränderten alten Suites wiederholt.

Getrennte Rootadmissions für Compiler und Probe. Genau eine Kompilierung:
PID (Process Identifier; Prozesskennung) 38628, final poll/Returncode 0, 0,602529 Sekunden, kein Timeout/UNKNOWN;
Compilerstdout ohne Warnungen, stderr leer. Eigenes Artefakt 18432 Bytes,
SHA256 `5acdd5a6a6ee32048bf0dc92866bd62cd84aae04c8fe4b9766b95a4399440498`.
Tatsächlich verwendete Compilerbytes und 167 BCL-Refs vollständig gepinnt.
SDK-Paketmetadaten 10.0.401; kein ausgeführter SDK-CLI-Versionsnachweis.

Genau eine Probe: PID 68400, final poll/Returncode 1, 0,102786 Sekunden,
kein Timeout/UNKNOWN und leeres stderr. Tatsächliche Runtimeversion und
Frameworkbeschreibung .NET 10.0.12. HOST_ENTRY/Main-Einstieg und LOAD_SQLCLIENT
mit individueller API-Exception/FileNotFoundException/THREW und Start-/Endzeiten
erfasst. MissingAssembly UNKNOWN; keine freie FileName-Aufnahme. Geladene
Assembly-/Dateibindung nicht hergestellt, beide Typprüfungen nicht erreicht.
Der kohärente Status COHERENT_KNOWN_DIAGNOSTIC_FAIL bedeutet einen bekannten
Loader-FAIL; der erfolgreiche Python-Auswerter ist kein Loader-PASS.

Originale, Quellen, SDK-/Ref-/Asset-/Version-/Inputpins nach Ausführung aktuell.
Ein Compiler und ein CLR-Prozess; null Connection-/Command-/Credential-
Erstellungen, SQL-, Container-, Providerendpoint-, Modell- oder Downloadaufrufe.
Keine direkte SNI-Ladeprobe. Die private Feldangabe native_calls=0 beschreibt
diese SQL-/SNI-Grenze und ersetzt nicht die tatsächlich erfolgte CLR-Probe.
Gemäß dem konkreten Einzelvertrag nach erstem kohärentem Befund gestoppt:
COHERENT_DIAGNOSIS_STOP. Kein unveränderter Retry und keine Wiederaufnahme der
alten Hard6-/UNKNOWN-Welle. Eine geänderte Auflösungsgegenprobe benötigt einen
sichtbaren eigenen Folgevertrag; die sechs Kandidaten werden nicht still neu
gezählt oder die Stopgrenze übergangen.

Die [anwender:innenorientierte Einordnung](../HowTo/SQL_SERVER_2025_AI_LOADER_DIAGNOSIS.md)
trennt Dateibestand, tatsächliches Laden, Typ-/API- und SQL-Transportnachweis.
Aktuell KNOWN_LOADER_FAIL_STOPPED. Alte FileNotFound-Ursache UNPROVEN;
Typ-/API-/SNI-/TDS-/SQL-/Provider-/Performance-/TSK-004-Abnahme NOT_ESTABLISHED.
Modell-/Tokenverbrauch UNKNOWN.
Integration erfolgt per PR mit aktuellen Head-/Main-Gates, voller Treeprüfung,
Synchronisierung, Sicherung und eigenem Cleanup. Keine neue CI-Runtimematrix.
