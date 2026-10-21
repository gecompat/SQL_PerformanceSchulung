# TSK-004: geänderte Loader-Auflösungsgegenprobe

PR232 ist vollständig geschlossen: neun erfolgreiche Head-Gates und sieben
erfolgreiche Main-Workflows, Main 6f3a116f81b7ee97e6d5441b9405c0e4255b41ca,
vollständiger Tree/FF-Synchronisierung und eigene Branches entfernt. SQL-CI (Continuous Integration; automatisierte Integrationsprüfungen)
wurde bei reiner Dokumentationsintegration nicht ausgelöst. 84 private Dateien
sind hashverifiziert gesichert und der eigene Worktree tatsächlich archiviert.
Der [erste Loadercheckpoint](SQL_SERVER_2025_AI_LOADER_DIAGNOSIS_REVIEW.md)
bleibt bekannter Loader-FAIL/COHERENT_DIAGNOSIS_STOP, nicht UNKNOWN:
Main und .NET 10.0.12 attestiert, LOAD_SQLCLIENT/FileNotFoundException/THREW,
MissingAssembly UNKNOWN und beide Typprüfungen nicht erreicht. Seine Quellen,
Originalbytes, Rawenden, Admissions und Stopdatei bleiben unverändert.

## Sichtbarer Folgeentscheid innerhalb der bestehenden Sechsergrenze

Der ursprüngliche Einzelvertrag hielt nach einem kohärenten Befund an. Dieser
Folgeentscheid erlaubt ausdrücklich die verbleibenden Kandidaten C2 bis C6;
C1 wird mitgezählt und nicht zurückgesetzt. Kumulativ höchstens sechs Compiler-
und sechs Probeprozesse, jeweils höchstens 60 Sekunden plus maximal fünf
Sekunden Reaping; Checkpoint nach C3, Abbruch nach C6. Tatsächlich bereits
verbraucht: ein Compiler und eine Probe. Ein unverändertes C#-Programm wird
nicht erneut kompiliert. Jeder neue Probeaufruf benötigt relevante geänderte
Eingaben, eigene feste Quellen-/Dateipins und vorherige Rootadmission.

Eine bekannte begrenzte Loaderexception darf nach Sicherung mit einem
konkret geänderten nächsten Kandidaten untersucht werden. Ein unklarer
Prozess-/API-Endzustand bleibt sticky UNKNOWN und stoppt den Folgeschnitt.
Nach kohärentem Loader-/Typmetadaten-PASS oder nach C6 hält er an. Der alte
VECTOR-FAIL_HARD6_UNKNOWN und alle anderen gestoppten Pakete bleiben unverändert;
diese lokale Gegenprobe erlaubt keine SQL- oder Cleanup-Wiederaufnahme.

## Kleine konkrete Änderungen

C2 ergänzt ausschließlich sichere Fehlermetadaten und tatsächlich gelesene
Host-Suchinformationen. Der bisherige FileName-Parser erlaubt nur bare Namen
oder vollständige Displaynames mit Version/Culture/PublicKeyToken. Ob dieser
enge Filter die neue UNKNOWN-Namensangabe verursacht hat, ist UNPROVEN.
Ein begrenzter BCL-Parser kann partielle legale Assembly-Displaynames prüfen,
darf ausschließlich feste einfache Namen ausgeben und verwirft Pfade,
Steuerzeichen, unbekannte Zusatzfelder und unbekannte Namen. Keine freie
FileName-, Message-, Stack- oder Fusionlog-Aufnahme.

Der Probehost liest nur begrenzte Counts und feste Ownfile-/Namensflags aus
den dokumentierten Host-Suchinformationen (SRC-118/119). Rohpfade und fremde
Namen werden nicht ausgegeben. Die unveränderte flache C2-Ausgangslage dient
der tatsächlich geänderten Fehlermetadaten-/Hostwitness-Frage, kein unveränderter
Retry von C1. Typmetadaten bleiben auf SqlConnection und SqlVector`1 begrenzt.

Bei bekanntem C2-FAIL dürfen zwei gezielte eigene Dateivarianten folgen:
erstens die fünf ausgewählten runtimeTargets an ihre wörtlichen relativen
Pfade kopieren und dort ausschließlich bereithalten (keine flachen Duplikate
dieser fünf Dateien), zweitens ein neuer eigener flacher Bestand ohne eigene
Depsdatei. Originale und frühere Kandidaten werden dafür weder geändert noch
gelöscht. Der gleiche tatsächlich gebundene C2-Programmbuild wird wiederverwendet,
sofern seine Quellen unverändert bleiben. Erwarteter eigener Clientpfad und
Depspräsenz sind feste, pinpflichtige Kandidatenparameter; keine freien Pfade.
Weitere C5/C6-Korrekturen benötigen konkrete neue Evidenz innerhalb derselben
Grenze und dürfen Oracles, Fehlzustände oder Versionsgrenzen nicht abschwächen.

Kein benutzerdefinierter Resolve-Handler, kein zusätzlicher Depspfad, keine
globalen Runtime-, PATH-, Cache-, Trust-, Registry- oder Serviceänderungen.
Keine Installation, Restore, Downloads, Netzwerk-, Connection-/Command-/
Credential-Erstellung, Open/Execute/Invoke, direkte SNI-Ladeprobe, SQL-,
Container-, Providerendpoint-, Modell- oder ONNX-Aufrufe. Ein Owner und enger
unabhängiger Rootreview; Quellen, Fixtures, tatsächliche Prozessenden,
SDK-/Runtime-/Refs-/App-/Originalpins und safe ENV bleiben bindend.

Ein positives Ergebnis gilt ausschließlich für den benannten Probehost,
sein Dateilayout und seine Typmetadaten. Typed API (Application Programming Interface; Programmierschnittstelle), SNI, TDS (Tabular Data Stream; Übertragungsprotokoll zwischen SQL-Client und Server), SQL, Provider,
Performance, volle TSK-004-Qualifikation und ursprüngliche C6-Ursache bleiben
offen. Keine universelle Deploymentempfehlung aus einem einzelnen Vergleich.
## C2 tatsächlich abgeschlossen, C3 vorbereitet

Sechs neue Puremethoden normal und vier optimiert bestanden, Raw-/Endpins
erhalten (PID (Process Identifier; Prozesskennung) 20952/50532). Das sind Spezifikations-/Fakegatetests, keine
ausgeführten BCL-Parsergegenfälle. Sourceänderung/86 erhaltene C1-Bytepins,
31 relevante Originaldateien, eigene App30, SDK-/Version-/167-Ref-/Inputpins
und aktueller enger Rootreview vor getrennten Compiler-/Probeadmissions.

Ein geänderter Programmbuild: PID 48964/poll 0/rc 0, 0,624011 Sekunden,
kein Timeout/UNKNOWN, Compilerstdout ohne Warnungen und stderr leer.
24576 Bytes, SHA256
`69112acc0812aa5e9f8b5af91224239d7691a4c4b6654ffeb26f3469c8aed442`.
Danach eine Probe: PID 61144/poll 1/rc 1, 0,102510 Sekunden,
kein Timeout/UNKNOWN, stderr leer. Main und .NET 10.0.12 attestiert;
vier HostGetData-Phasen RETURNED und LOAD_SQLCLIENT THREW/FileNotFoundException.
Tatsächlich sicher erfasster MissingAssembly Microsoft.Data.SqlClient,
Formatklasse PARTIAL_DISPLAY. C1s frühere nicht erhaltene FileNamebytes werden
dadurch nicht rekonstruiert; sein UNKNOWN-Name bleibt historisch bestehen.

Hostwitness: TpaCount 201, OwnClientInTpa false, AppPathsCount null,
NativePathsCount 2, DepsFilesCount 2, eigene Depsdatei und erwartete flache
DLL vorhanden. Keine Typprüfung erreicht, keine geladene Dateibindung.
COHERENT_KNOWN_DIAGNOSTIC_FAIL, eigener C2-Stop erhalten. Originale,
Sources, SDK-/Ref-/App-/Inputpins und alle 86 C1-Pins nach Ausführung aktuell.
Kumulativ zwei Compiler und zwei Proben; null SQL-/Container-/Modellaufrufe.

Als konkret geänderte C3-Variante entsteht ein neuer eigener Bestand mit den
fünf Dateien ausschließlich an ihren wörtlichen runtimeTargets-Unterpfaden,
23 anderen DLLs flach, Originaldeps/config und identischem C2-Programmbuild.
Keine erneute Kompilierung. Erwarteter Clientpfad ist der feste relative
SqlClient-Unterpfad. Neue Sources-/Pins-/Negativkontrollen und Rootadmission
vor höchstens einer C3-Probe; danach tatsächlicher Checkpoint3. Kein C2-Retry.

## Checkpoint3: Loader-/Typmetadaten-PASS, Paket gestoppt

Sechs gezielte C3-Layout-/Borrowed-Compile-/NoCompile-/Typ-/SHA-Methoden
normal und optimiert bestanden, tatsächliche PIDs 39804/38920, bekannte Enden
und Rawkanäle. Program.cs und Oracle sowie der 24576-Byte-Programmbuild sind
bytegleich C2. Die neue eigene App enthält 23 flache DLLs und fünf ausschließlich
an den festen Unterpfaden; insgesamt 31 Dateien einschließlich Deps/config/Programm.
Alle 69 C2-Dateien und 86 erhaltenen C1-Pins vor/nach unverändert.

Nach aktueller enger Rootadmission genau eine C3-Probe, null Kompilierungen:
PID 58712, final poll/Returncode 0, 0,126375 Sekunden, kein Timeout/UNKNOWN,
stderr leer. Main und .NET 10.0.12 attestiert, alle acht Phasen vollständig
beendet; Load und beide GetType-Aufrufe RETURNED. Tatsächlich geladen:
Microsoft.Data.SqlClient/Assemblyversion 6.0.0.0 aus dem erwarteten eigenen
relativen Pfad, vollständiger Datei-SHA256
`15cf9fd194927cca11e0d3e8289b85f965712f1bf7d359ebda2c537c7e9e8409`.
SqlConnection- und SqlVector`1-Typmetadaten aus genau dieser Assembly bestätigt.

Hostwitness: TpaCount weiterhin 201, OwnClientInTpa jetzt true,
AppPathsCount null, NativePathsCount 2, DepsFilesCount 2, erwartete DLL und eigene
Deps vorhanden, flache SqlClient-DLL nicht vorhanden. OwnClientInTpa prüft
ausschließlich den deklarierten eigenen erwarteten Pfad; C2s false beweist
keine vollständige Abwesenheit eines anderen gleichnamigen TPA-Eintrags.

COHERENT_LOADER_METADATA_ONLY und tatsächlicher Checkpoint3. Kumulativ zwei
Compiler und drei Proben; C1/C2-FAIL bleiben erhalten. Gemäß Folgeentscheid
nach Loader-/Typmetadaten-PASS angehalten: STOP_AFTER_LOADER_METADATA_PASS.
C4 ohne eigene Deps und C5/C6 wurden nicht ausgeführt und sind für diesen
abgeschlossenen Diagnosevergleich nicht mehr erforderlich. Keine pauschale
Deploymentregel und keine Rekonstruktion der ursprünglichen C6-Exception.
Native SNI-, lokale Typed-API-, TDS-/SQL-/Provider-/Performance-/volle
TSK-004-Qualifikation bleiben NOT_ESTABLISHED; null SQL-/Container-/Modellaufrufe.

Aktuell CHECKPOINT3_LOADER_METADATA_PASS_STOPPED. Modell-/Tokenverbrauch UNKNOWN. PR/Main/Tree/FF/
Branch-/Sicherung-/Worktreeclosure bleiben erforderlich.
