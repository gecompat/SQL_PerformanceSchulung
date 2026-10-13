# TSK-004: begrenzter nativer VECTOR-Caller

PR228 ist vollständig geschlossen: acht aktuelle Head- und sechs Main-Gates,
Main48d4e187b5b949fe816eb28717c194f6ce846a40, vollständiger Tree,
FF-Synchronisierung und eigene Branches bereinigt.916 private Dateien sind vor
der tatsächlichen Worktreearchivierung kopiert und hashverifiziert. Der erste
Windows-Pfadfehler der Belegsicherung bleibt erhalten; der geänderte Copy mit
expliziten eigenen erweiterten Pfaden ist abgeschlossen. Kein SQL-Effekt dabei.

## Fortgeführte Grenze und Quellen

Die [Dependencyvorbereitung](SQL_SERVER_2025_AI_VECTOR_CLIENT_REVIEW.md) endete
am Checkpoint3 SOURCE_ONLY. C1-Konfigurations- und C2-150MB-FAIL bleiben erhalten;
C2-Ende nur quellengestützt, fehlende individuelle SDK-Felder bleiben fehlend.
Jetzt folgen C4 bisC6 innerhalb desselben endlichen Sourcebudgets, ohne Reset.
Höchstens drei zusätzliche eigene serielle Container, einer je Kandidat.
Ein Implementierungsverantwortlicher und enger unabhängiger Rootreview.

Der vorhandene gepinnte SqlClient6.1.4- und net10.0-Bestand wird unverändert aus
den verifizierten privaten Belegen gelesen (SRC072/SRC116). Kein weiterer
Paketdownload oder Restore, keine globale SDK-/Cache-/Hostinstallation. Ein
konkreter lokaler Compilerplan wird vor Ausführung geprüft; pro geändertem
Kandidaten höchstens90s und300MB eigene Dateien. Neue Source-/Inputpins werden
vor Ausführung erfasst. Das ist kein Provider-CLR- oder SQL-PASS.

Root hat den kleinsten Offlineplan für C4 angenommen: vorhandenes `csc.dll`
aus SDK10.0.401,167 vorhandene net10.0-Frameworkreferenzen und passende
Runtime10.0.12. Eigene Main-/Receiptquellen erhalten einen festen Assemblynamen
und Version1.0.0; die vorhandene SDK-erzeugte Dependencydatei bleibt unverändert.
Die eigene Runtimeconfig pinnt10.0.12 mit RollForward=Disable. Ausschließlich
aus dem tatsächlichen Lock-/Assetsgraph gewählte Windows-Runtime- und SNI-x64-
Dateien werden vor und nach der lokalen Übernahme gegen ihre Hashes geprüft.
Compilerzulassung ist Sourcevorbereitung; der Client darf damit noch nicht laufen.

C4 bestand in genau einem Offline-Compile: gehaltene PID/finales poll0/rc0 und
0,5911s sind erfasst. Zwei CS1701-Warnungen für net9-Referenzen gegen net10
bleiben sichtbar; die Runtimebindung ist erst im folgenden eigenen Lauf prüfbar.
65 aktuelle eigene Dateien,168 Referenzen und28 kopierte Runtimeassets sind
gebunden. Die ersten14 reinen Methoden wurden als PASS gemeldet, ihr initialer
Rawkanal wurde nicht separat erhalten. Vier gezielte Schutzmethoden unter `-O`
haben Originalbelege. Dieser Stand enthält weiterhin null Nativeaufrufe.

Der enge Rootreview fand vor Admission zwei Python-Grenzen: ungültiges UTF8
und nur behauptete aggregierte Requestenden konnten den UNKNOWN-Status
verlieren; außerdem genügte ein beliebiger SQLerror als Dimensionserror.
Die geänderte Endprüfung bindet nun vollständige individuelle Requestnachweise
vor der Resultatsemantik. Decoder-/Teilnachweisfehler bleiben UNKNOWN und sperren
Folge-SQL. Bekannte vollständige Enden mit falschem Resultat bleiben FAIL.
Das eingefrorene Dimensionsoracle verlangt Severity16 und einen tatsächlichen
Vector-/Dimensions-/Typinkompatibilitätsbezug, keine erfundene positive Errornummer.
Vier neue Gegenfälle normal und `-O` bestanden mit Originalkanälen und Quellenpins;
der vorherige Freeze bleibt archiviert. C#-/Compiler-/Appbytes unverändert,
keine Compile- oder Nativewiederholung. Aktuelle Bindungs-/Privacy-/Rootgates
schließen Sourceadmission; tatsächliche Ergebnisse und Cleanup folgen getrennt.

## Vor Native zu schließen

Der Caller benötigt tatsächliche individuelle Requeststart-/End-, Source-/
Input- und Deadlinebindung. Erfolgsoracle: zwei kleine synthetische float32-
VECTOR(3)-Rows, typisierte Parameter und Reader sowie alle sechs Koordinaten
gegen JSON. Zusätzlich tatsächlicher typisierter Nullwert der Dimension3,
Dimensionsabweisung mit vollständigen Fehlerfeldern und unverändertem Vollstate.
Ein akzeptierter und zurückgerollter Dimensionsfall ist kein Negativ-PASS.

Nur ein neuer eigener fester17.0.5005.3-Container mit ganzer CID, Ownerbindung,
4CPUs/6GiB, Loopback und ohne Mounts. Eine neue vierfach bytegenau markierte DB;
Marker-/Kontextguards vor Mutationen und Cleanup, negative Kontrollen und
tatsächlicher Restore. Pooling=False, ReadOnly-SecureString/SqlCredential aus
SQLCMDPASSWORD; kein Kennwort als Argument, Hash oder persistierter Output.
Keine Indizes, Previewänderungen, zusätzlichen Logins, Modelle oder Hosteffekte.

300s regulär und eine60s-Cleanupdeadline. UNKNOWN bleibt sticky und sperrt
Folge-SQL sowie einen zweiten mutativen Recoveryversuch. Ganze eigene DB-/
SQL-/CID-/Namens-/Inputabwesenheit muss tatsächlich erhoben werden; alleinige
Namespaceabwesenheit ist kein SQL-Cleanup-PASS. Die alte Pool-UNKNOWNwelle
wird nicht wiederaufgenommen. Typisierte APIs belegen weder unabhängig
aufgenommenen TDS-Wireverkehr noch einen allgemeinen Performancegewinn.

Historischer Stand vor C4: SOURCE_PREPARATION_ONLY, null neue Provider-CLR-/Open-/SQL-/
Container-/Modellaufrufe. Rootadmission erst nach aktuellem Code-, Oracle-,
Privacy-, betroffenen Test- und Dependencyabschluss. Anschließend aktuelle
PR-/Main-Gates, voller Tree, Synchronisierung und eigener Cleanup.
Volle TSK004-/Workstreamabnahme bleibt offen; Modell-/Tokenverbrauch UNKNOWN.

## C4: tatsächlicher FAIL vor Create

C4 erreichte zwei bekannte Podman-CLI-Enden mit Returncode1. Bereits der erste
Imageinspect scheiterte an `could not get either XDG_DATA_HOME or HOME`; Create,
SQL und der typisierte Client wurden nicht erreicht. UNKNOWN=false, aktive
Inputs abwesend. Ursprüngliche DB-/CID-/Namensabwesenheit und SQLcleanup sind
NOT_ESTABLISHED; der ursprüngliche Ledger bleibt ausdrücklich closed=false.

Die [offizielle Windows-Homedir-Quelle](https://github.com/containers/storage/blob/main/pkg/homedir/homedir_windows.go)
leitet diesen Pfad über USERPROFILE ab; der [GetDataHome-Pfad](https://github.com/containers/storage/blob/main/pkg/homedir/homedir.go)
enthält die tatsächlich erhaltene Fehlermeldung. Die bisherige Namespace-ENV
ließ USERPROFILE weg. Das erklärt die beobachtete Grenze, attestiert aber nicht
den exakten Build des vorhandenen Podman-Binaries.

Eine neue Root-Namensabfrage mit ausschließlich zusätzlich übergebenem tatsächlichem
USERPROFILE endete mit gehaltenem PID/poll0/rc0 und leerem Ergebnis. Die aktuellen
eigenen Inputs sind ebenfalls abwesend. Der zusätzliche Temp-Verzeichnis-WARN
bleibt erhalten: rc0 und frische Namensabwesenheit werden getrennt davon geführt.
Der erste zu strenge Root-stderr-Gatefehler ist erhalten; keine Abfragewiederholung.
Der gebundene No-create-Abschluss erklärt CID=NOT_CREATED und behauptet weder
einen ursprünglichen CID-Abwesenheitsbeleg noch SQLcleanup-PASS.

C5 darf genau diesen belegten Vor-Create-Fall über einen vollständigen Rootproof
fortsetzen; die historische closed=false-Zeile bleibt unverändert. Der geänderte
Namespace-ENV-Vertrag ergänzt USERPROFILE und eigene absolute TEMP/TMP-Pfade
aus den neuen Befunden. SQL-/Child-ENV-Quellen, C#-/App-/Compilerbytes bleiben
unverändert; kein neuer Compile oder Download. C4-Originalquellen, Resultate,
Authorities und Belege bleiben archiviert. C6 bleibt die letzte Reserve des
Sechserbudgets. C5-Native erst nach neuen aktuellen Source-/Test-/Rootgates.

C5-Sourceabschluss: ausschließlich Namespace-USERPROFILE und eigene absolute
TEMP/TMP ergänzt. Zwei neue ENV-/No-create-Proof-Gegenfälle normal und `-O`
bestanden mit Rawkanälen, gehaltenen PID/poll0/rc0 und aktuellen Quellenpins.
Originale C4-Zeile,84 archivierte Belegdateien und alle65 ursprünglichen
Quellen bleiben gebunden; die Ausnahme prüft genau diesen Vor-Create-Fall.
SQL-/Childfunktionen, C#-/App-/Compiler-/22 SQLbytes sind unverändert.
Kein weiterer Compile, Paketdownload oder eigener Podman-/SQL-Probelauf.

## C5: bekannter State-FAIL und tatsächlicher Cleanup

C5 startete einen eigenen Container. Acht SQLcmd-Aufrufe einschließlich dreier
Startbereitschaftsabfragen endeten bekannt; Setup und feste Buildprüfung bestanden.
Die erste State-Aufnahme enthält vollständig 221 Hexframes und 44050 UTF16-
Einheiten, 14 Schlüssel, 41 Konfigurationen, vier Marker und zwei Dateien.
Objects, Columns, Indexes und Principals sind jedoch null statt Arrays. Das
unveränderte Listenoracle weist dies ab. Der typisierte Client und die weiteren
Negativkontrollen wurden nicht aufgerufen; kein nativer VECTOR-API-PASS.

Root hat den Originalkanal unabhängig dekodiert. Der eigentumsgebundene DB-Drop
und die frische SQLabwesenheit bestanden tatsächlich. Ganze eigene CID, Name
und Inputs sind ebenfalls abwesend; UNKNOWN=false, C5-Ledger closed=true.
C4 bleibt historisch closed=false mit seinem separat gebundenen No-create-
Abschluss. Kein neuer Modellcall und keine Umdeutung historischer Fehler.

## C6: letzte Producerkorrektur vor Admission

Nur die fünf State-Eingaben ändern sich: neun Katalogarrays erhalten innerhalb
JSON_QUERY einen expliziten COALESCE-Fallback N'[]'; ebenso das dynamische
Rows-Array. Die Projektionen, Ordnungen, Guards und 17 übrigen SQL-Eingaben
sind unverändert. Null wird im Oracle weiterhin abgewiesen; kein nachträgliches
Normalisieren erhaltener Records. C#, App, Compiler und Qualifier unverändert.
93 originale C5-Dateien bleiben archiviert und vollständig hashgebunden.

Zwei neue reine Methoden prüfen den reversiblen Sourceunterschied und eine
ausdrücklich synthetische leere Arrayfixture bei unveränderten nichtleeren
Vollrecords. Der erste Normalversuch hatte einen Fixture-Lesecapfehler; Beleg
erhalten. Nach Änderung ausschließlich dieses eigenen Fixture-Lesecaps bestand
die betroffene Methode normal und beide Methoden unter -O mit Originalkanälen
und bekannten Prozessenden. Kein zusätzlicher Compile oder Nativeaufruf.

Die [JSON_QUERY-Dokumentation](https://learn.microsoft.com/en-us/sql/t-sql/functions/json-query-transact-sql?view=sql-server-ver17)
beschreibt die unveränderte JSONfragment-Einbettung; [COALESCE](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/coalesce-transact-sql?view=sql-server-ver17)
die erste nicht-NULL-Expression und mögliche Mehrfachauswertung. Abgerufen am
2026-10-13. Das begründet die geplante Korrektur, kein tatsächliches C6-Ergebnis.
Aktuelle Source-/Privacy-/Rootadmission folgt. Nach C6 endet dieses Sechserbudget
unabhängig von PASS oder FAIL; keine zusätzliche Probe oder Korrekturwelle.

## C6: FAIL mit sticky UNKNOWN; Welle beendet

C6 startete genau einen eigenen Container. Sechs SQLcmd-Enden sind bestätigt;
die korrigierte erste vollständige State-Aufnahme bestand tatsächlich das
unveränderte Oracle. Der .NET-Child endete bekannt mit Returncode1 ohne Timeout.
Er liefert ein vollständiges FAIL_COMPONENT-Envelope mit ErrorType
System.IO.FileNotFoundException, aber keine individuellen Requests. Eine konkrete
fehlende Assembly oder ein tatsächlicher SQL-Open wird dadurch nicht attestiert.
Der strenge individuelle Endgate setzt deshalb UNKNOWN; kein weiterer SQLaufruf,
keine typisierte Ergebnis-, Null- oder Dimensionsabnahme und keine Negativkontrolle.

SQLcleanup und eigene DB-Abwesenheit bleiben NOT_ESTABLISHED. Ein vollständig
gebundener eigener Namespaceabbau wurde genau einmal tatsächlich durchgeführt;
sein Ende und frische ganze CID-/Namensabwesenheit sind bestätigt. Dies ist nur
Containment, kein SQLcleanup-PASS. Der Nativeinput bleibt als Beleg erhalten,
InputsAbsent=false, Ledger closed=false und UNKNOWN=true. Die exakte gesamte
Cleanupdauer wurde nicht erfasst; Einzelaufrufdauern ergeben keinen solchen Beleg.
Root hat Originalrecords, State, Childende, fehlende Requests, ganzen CID-/
Ownerbound und einmaligen Abbau unabhängig geprüft. Keine weitere Probe oder
Korrektur dieser Welle; alle sechs fortgeführten Kandidaten bleiben gezählt.

Aktuell: FAIL_HARD6_UNKNOWN. Zwei eigene Container wurden erstellt und sind
abwesend, 14 SQLcmd-Aufrufe und ein .NET-Child tatsächlich beobachtet; keine neuen
Modelle oder Downloads. C4-/C5-FAIL, Compilerwarnungen und offene Runtime-/Wire-/
TSK-004-Grenzen bleiben erhalten. Integration dieses Fehlercheckpoints folgt
mit aktuellen PR-/Main-Gates, vollständigem Tree, Synchronisierung und eigener
Belegsicherung/Worktreearchivierung. Wiederaufnahme benötigt geänderte Evidenz,
einen eigenen endlichen Folgeentscheid und geschlossene UNKNOWN-Grenzen; kein
unveränderter Retry. Unabhängige autorisierte Workstreamarbeit läuft weiter.
