# TSK-009: neue eigene Qualifikationswelle des öffentlichen Poolprofils

PR241 ist vollständig geschlossen: sieben Head-/fünf Main-Gates, Main
af7d3d3af66dda0e300ef7bafc196fc92eec16c8, voller Tree, synchrones sauberes
Main, eigene Branches entfernt, 1467 private Dateien hashverifiziert gesichert
und eigener Worktree tatsächlich archiviert. Die lokale Gemma-Diagnose endet
mit fehlendem ausgewähltem Tag bei ausreichender Runtimeversion; keine Inferenz.

## Geänderte Grundlage und unveränderte historische Grenzen

Die alte [öffentliche Poolwelle](SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md)
bleibt STOPPED_NATIVE_UNKNOWN. Zwei Nativeversuche, ein tatsächlich erzeugter
eigener Container, SQLcmd0 und Poolchild0 bleiben gezählt. C1 fehlte der
Namespace-Konfigurationspfad; C2 traf den falschen Container-Feldcase. Der
getrennte eigene Remove-Aufruf überschritt seinen Cap und bleibt UNKNOWN.
Tatsächliche frische CID-/Namens-/Inputabwesenheit ist nur Resourceclosure,
kein nachträglicher SQL-/Requestende-/Profil-PASS.

Die öffentlichen Quellen enthalten bereits APPDATA, Container-/ps-.ID,
--no-trunc und --time=0. Das konkrete Delta zum tatsächlichen C2-Sourcebestand
ist vor neuer Admission bytegenau zu binden. Keine erneute Ursachenanalyse,
keine Ausführung alter Pakete, keine Folge-SQL-/Recovery-/Remove-Aufrufe an
alten Ressourcen und kein C3 der gestoppten Welle.

Eine neue explizite Wave-/Input-/Scope-/Controlbindung ermöglicht ausschließlich
neue eigene Ressourcen. Der alte Standardpfad und seine UNKNOWN-Sperre bleiben
wirksam. Historie bleibt read-only mit Originalhashes, Stop, Closure und
tatsächlichen Counts gebunden. Weder leeres altes Controlverzeichnis noch
umbenannte alte Ledger dürfen ein Budget oder UNKNOWN zurücksetzen.

## Endlicher gemeinsamer Umfang und aktueller Review

Ein Implementer und enger unabhängiger Rootreview für Wave-/History-/Budget-
Bindung, Credentialprivacy, tatsächliche Requestenden, Rollen-/RLS-/Resetdaten,
vollständige bytegenaue Eigentumsmarker und Cleanup. Zunächst SOURCE_ONLY:
keine Container, SQL, CLRprobe, Compiler, Modelle, Downloads oder Hoständerungen.
Neue Sourcekandidaten höchstens sechs, Sourcecheckpoint3/hard6. Betroffene
neue Wave-/History-/Sharedbudgetgegenfälle normal/-O; alte grüne Suiten und
alte Diagnoseanalysen bei belegten identischen Bytes wiederverwenden.

Vor jedem tatsächlichen neuen Nativecaller separate aktuelle Rootadmission.
Die zwei alten Nativeversuche zählen weiter: höchstens vier zusätzliche,
insgesamt sechs. Der alte Container zählt weiter: höchstens vier zusätzliche
serielle eigene Container, insgesamt fünf; jeweils höchstens einer je neuem
Kandidaten. Erster tatsächlicher neuer Versuch erreicht Gesamtcheckpoint3;
vor einem weiteren Versuch anhand der Originale unabhängig abschließen.
Nur relevante geänderte Sources/Inputs oder neue Evidenz rechtfertigen Retry.
Erster kohärenter begrenzter PASS beendet die Welle, UNKNOWN sofort STOP.

## Zulässige neue lokale Effekte nach Admission

Unveränderte fachliche Grenzen des öffentlichen Poolprofils: SQL17.0.5005.3,
CL170, Developer/Linux im neuen eigenen Wegwerfcontainer, fest vorhandenes
Image, vier CPUs/sechs GiB, Loopback, keine Mounts. Genau drei neue eigene
synthetische Logins/SID-Leases, zwei VECTOR(3)-Rows, sechs A/B/U/A/B/U-Checkouts.
Keine Adoption bestehender Instanzen, Datenbanken, Principals oder Inputs.
Explizite RED-/Lab-/Scopebindung, Providerfähigkeit vor Effekten; keine
Installation bei fehlenden vorhandenen Bytes, sondern ehrlicher SKIP.

Normaldeadline300s, einmalige Cleanupdeadline60s ohne Reset, vor Childstart
laufende Cleanupuhr, Childcap40s und tatsächliche Restreserve/Startup/Reaping
berücksichtigen. Konfigurierte Caps sind keine Wallclockgarantie. Vollständige
State-/Principal-/Rechte-/Source-/Markeroracles, echte Rollen-/Spoof-/Reset-
Negativen mit unverändertem State/Restore. Individuelle bekannte API-/Client-
Prozessenden, physische Poolreuse über Owner-DMV statt GUID-Ersatzoracle.
Secrets nur gehaltene Credentialobjekte/ENV, keine CredentialderivedHashes
oder Passwordconnectionstrings; sichere Raws vor Digests/Persistierung.

UNKNOWN sperrt Folge-SQL und zweiten Remove; ausschließlich gebundener neuer
eigener Namespaceabbau und frische tatsächliche Abwesenheitsabfragen. Bekannter
Abschluss verlangt eigene ClearPool-/Close-/Dispose-Reihenfolge, frische
physische Abwesenheit und State vor Login-Drops, Login-Drops vor DB-Drop sowie
frische SQL-/ganze CID-/Namens-/Inputabwesenheit. Alte UNKNOWN bleibt erhalten.

Keine Änderung der GREEN-/LOCAL-Default-CI, keine Default-RED-Ausführung,
keine Fremdrepo-/Trust-/Cloud-/Bezahl-/ONNX-/Modell-/globalen Hosteffekte.
FAIL/WARN/SKIP und fehlende unabhängige TDS-/Wire-/Sidechannel-/Performance-/
Versions-/volle TSK009-/Releasebelege bleiben sichtbar. Modell-/Tokenverbrauch
UNKNOWN. Aktuelle lokale betroffene Checks, PR, Head-/Main-/Tree-/FF-/Branch-
Abschluss, private Belegsicherung und tatsächliche eigene Archivierung sind
vor Schnittabschluss Pflicht. Danach nächster unabhängiger autorisierter Schritt.

## Tatsächlicher Native1-Abschluss und gezielte Source4-Korrektur

Der erste neue Versuch ist insgesamt Native3: bekanntes FAIL_SETUP_SUMMARY
mit getrenntem FAIL_SQL_CLEANUP, UNKNOWNfalse. Der eigene Child endete mit
PID/poll/rc1, kein Timeout oder Collectorfehler. Vier vollständige SQLcmd-Enden
(ein bekannter Startupfehler, danach drei rc0), dreizehn gehaltene Namespace-
enden mit PID/poll/rc0. Ein neuer Container; kumulativ drei Nativeversuche und
zwei Container. Baseline, Negativkontrollen und Poolchild nicht erreicht.

Die tatsächlichen Setupkanäle enthalten zwei erwartete stdout-Erfolgsmarker
und genau die bekannte Datenbank-Kontextmeldung auf stderr. Die bisherige
zusammengeführte Auswertung akzeptierte die dadurch entstehende Reihenfolge
nicht. Das ist ein konkreter Parserbefund, kein behaupteter Rollen-/Poolfehler.
SQLcleanup bleibt NOT_ESTABLISHED. Tatsächlich vollständig gebundener eigener
Remove mit --time=0 und frische leere ganze CID-/Namensabfragen sowie eigene
Inputabwesenheit belegen Resourceclosure. Sie ersetzen keinen SQL-Dropbeleg.
Alle fünf Hostpins, fünfzehn Sources und ursprünglichen Authorities vor/nach
gleich. Originale und sichere getrennte Kanäle privat erhalten; die individuelle
äußere Launcher-PID wurde nicht erfasst und wird nicht rekonstruiert.

Unabhängiger Actualreview und verpflichtender Nativegesamtcheckpoint3 sind
bekannt geschlossen. Der einzelne Lauf bleibt STOP; keine automatische Probe.
Die alte PR226-UNKNOWN-Welle bleibt unverändert. Native1-Originale und Source3-
Authority werden vor einer neuen Korrektur byteverifiziert archiviert.

Source4 korrigiert ausschließlich die Setupkanalauswertung: letzter tatsächlich
captured SETUPcall, getrennte stdout/stderr und vollständige Input-/Output-/
PID-/Returncodebindung. Genau bekannte Erfolgsmarker und höchstens die exakte
Kontextmeldung zulassen; unerwartete, doppelte, fremde, fehlende oder fehlerhafte
Kanäle und UNKNOWN ablehnen. Zwei betroffene neue Methoden normal/-O bestanden,
keine alte grüne Suite oder Nativeprobe wiederholt. Neue eigene Caller-/Input-/
Snapshot-/Authoritybindung für Native2/insgesamt4, höchstens ein neuer eigener
Container, vor Wirkung aktuelle unabhängige Rootadmission. Sourcecheckpoint3-
Original bleibt erhalten; aktuelle Source4-Bindung wird ausdrücklich erneuert.
Drei Nativeversuche/zwei Container sind bereits verbraucht; drei zusätzliche
Native-/Containerslots bleiben, Gesamtmax6/5 unverändert. Noch kein neuer
Rollen-/Pooling-/SQLcleanup-/Runtime-PASS, kein Modell-/Host-/Cloudwechsel.

## Tatsächlicher Native2-Teilnachweis und endgültiger UNKNOWN-Stop

Source1–4 bilden vier verschiedene tatsächlich geprüfte Code-/Testzustände:
initial neun Methoden normal/-O; Checkpoint-Datei-/Inputbindung zwei;
strikter tatsächlicher Checkpointvertrag zwei; Setupkanalhelper zwei.
Alle acht gehaltenen reinen Prozessenden/Raws/Quellenpins sind erhalten.
Sourcecheckpoint3 anhand der ersten drei Zustände geschlossen; Source4-Ledger
und aktuelle Rootproofs ausdrücklich neu gebunden, ursprüngliche Source3-
Authorities unverändert archiviert. Keine unveränderte Vollsuite wiederholt.

Nach getrenntem aktuellem Source-/Caller-/Privacyreview und exklusiver Admission
lief genau Native2/insgesamt4. Source4-Setupkanalprüfung bestand, eigene Logins und
vollständige Baseline wurden erreicht. 39 vollständige bekannte SQLcmd-Enden und
48 gehaltene Namespaceenden sind vor/nach an die aktuellen Quellen gebunden.
Eine tatsächliche Quellenabweisung51003, Held-SID51004 und vier Marker51004
mit Restores, fünf vollständige Vorher-/Nachher-/Restorezustandswitnesses sowie
sieben geordnete Controls sind geprüft. Diese Owner-DDL-/DML-/Metadatenkontrollen
belegen keine authentifizierten A/B/U-Checkouts oder physische Poolreuse.

Der tatsächliche Topchild ist bekannt beendet, ohne Timeout oder Collectorfehler.
Inneres CLIENT_END_UNKNOWN bleibt sticky: vollständige Poolchild-/individuelle
.NET-Endrecords sind NOT_ESTABLISHED; die Ursache ist aus den unveränderten
Originalrecords UNPROVEN. Die äußere Launcher-PID wurde nicht erfasst. Kein
Rekonstruktionsclaim aus Source, keine Interpretation fehlender Captures als null
Operationen und kein allgemeiner Transport-/Runtime-PASS.

Nach UNKNOWN erfolgte kein Folge-SQL. Ausschließlich ein vollständig gebundener
neuer eigener Namespaceabbau, dessen Remove-Ende bekannt ist, und frische leere
ganze CID-/Namensabfragen belegen tatsächliche Resourceabwesenheit. SQL-Drop und
frische SQLabwesenheit bleiben NOT_ESTABLISHED. Ein eigener ursprünglicher
Childplan bleibt als Recoveryinput erhalten: inputsAbsentfalse, ledgerClosedfalse.
Der unmodifizierte Plan und vollständige sichere Ergebnisrecord sind zusätzlich
privat byteverifiziert vor späterer Worktreebereinigung gespiegelt; dies ändert
keine ursprünglichen Input-/Closureflags. Kein zweiter Remove und kein Cleanup-
Clockreset. Alte PR226-UNKNOWN und Native1-KnownFAIL/Checkpoint bleiben erhalten.

Kumulativ vier Nativeversuche und drei eigene Container; zwei neue Versuche und
zwei neue Container in dieser getrennten Welle. Ursprüngliche Max6/Max5 und
Source6/CP3/hard6 bleiben, die aktuelle Welle ist jedoch STOPPED_AFTER_NATIVE2_UNKNOWN.
Keine Native3-Admission, keine weitere Probe/Korrekturwelle an alten Ressourcen,
keine Modelle/Cloud-/Hoständerung. Alle fünf Hostbytes, fünfzehn ausgeführten
öffentlichen Sourcepins, Authorities und 19 Native2-Executionsnapshots bleiben
unverändert. Aktuelle fünf Dokumentänderungen sind ausdrücklich DocOnly gegenüber
diesen Ausführungssnapshots; Code-/Test-/Workflowbytes werden gesondert unverändert
gebunden. Kein erneuter Native-/Purelauf aufgrund von Statusprosa.

Öffentliche Qualifikation bleibt NOT_ESTABLISHED für Poolchild, einzelne .NET-
Enden, authentifizierte Checkoutpopulation, Poolreuse, vollständigen SQL-/Input-
Cleanup, TDS, Seitenkanäle, Performance, ganze CON-010-/TSK-009-/TP-CON-Abnahme.
Aktuelle PR-/Head-/Main-/Tree-/FF-/Branch-/Archivgates folgen vor Schnittabschluss.
Erst nach vollständig geschlossener Integration folgt ein unabhängiger reiner
SOURCE_ONLY-Capturevertrag für sichere tatsächliche Childkanäle und Endrecords
vor einer fehlgeschlagenen Klassifikation. Dieser nächste Schnitt darf die
Originalursache nicht ohne ursprüngliche Evidenz erklären und führt keinen
Native-/Provider-/Modellaufruf oder Resume dieser Welle aus.
