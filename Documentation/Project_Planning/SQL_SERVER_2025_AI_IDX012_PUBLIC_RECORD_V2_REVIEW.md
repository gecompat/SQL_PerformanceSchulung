# TSK-006: öffentliche Rollenrecords getrennt als V2 prüfen

## TSK-006: V2-Rechtegegenfälle korrigiert; historischer Report bleibt FAIL

Der einmalige historische Offlinebericht scheiterte mit V2_RECORD_BINDING:
attempted1, completed0, keine Summary. Driver-PID8276 und Child-PID72048
endeten bestätigt mit Poll/Returncode1, ohne Timeout oder UNKNOWN. Alle51
festen Eingangsdateien und acht Authoritydateien blieben vor/nach bytegleich.
Root hat den Fehler und die Originalkanäle unabhängig geprüft.

Der konkrete Fehler betrifft die beiden Rechtegegenfälle: Die tatsächliche
öffentliche API liefert für das noch nicht gestartete Cleanupfenster vier
Felder, während Consumer und Fixture nur Status erwarteten. Source5 fordert
jetzt exakt Status=NOT_STARTED, Seconds als int60 sowie beide Zeitfelder=None.
Fehlende, zusätzliche und widersprüchliche Felder werden abgewiesen. Der neue
betroffene Gegenfall bestand normal PID11964 und optimiert PID16700, jeweils
Poll/Returncode0; alle31 Quellen blieben unverändert. Enger Rootreview bestanden.

Fünf geprüfte Quellenstände,21 Methodeninvokationen/19 PASS/zwei erhaltene FAIL,
zusätzlich erster Driver-SyntaxFAIL; acht bestätigte Unitprozessenden. Keine
alte grüne Suite lokal wiederholt. Der ursprüngliche historische Report bleibt
FAIL; das maximale Einzelreportbudget ist verbraucht und wird nicht zurückgesetzt.
Null Native-, SQL-, Container-, Provider- oder Modellaufrufe in diesem Schnitt.
V1, alte Evidenz und Claims unverändert; Runtime-/Herkunfts-/Credentialgrenzen
bleiben offen. Modell-/Tokenverbrauch UNKNOWN.

Dieser Schnitt wird mit aktuellem Quellen-/Dokumentfreeze, PR-/Head-/Main-Gates,
Integration nach origin/main, Synchronisierung und eigenem Cleanup geschlossen.
Erst anschließend darf eine getrennte begründete Folgewelle einen weiteren
historischen Bericht zulassen; kein Wiederholungs-PASS in dieser Welle.

## Source4: betroffene Helperfixture vollständig bestanden

Source4 änderte ausschließlich den positiven Fixture-Pfadvergleich auf vollständige
identische Dateibytes mit korrekten ExtendedReads. Consumer-, Expected-, HowTo- und
Workflowbytes sind Source3-gleich. Der betroffene Helperfall bestand normal
PID70092 und optimiert PID47924, jeweils Poll/Returncode0; alle negativen Typ-/
Namen-/Fremdpfad-/Symlinkzweige wurden erstmals erreicht, vor Fremdimport abgewiesen.
Keine Privacycluster- oder alte7/6-Suite wiederholt. Source3-Originale samt tatsächlichem
Rootcheckpoint sind vollständig vor dem Fixturedelta archiviert.

Vier geprüfte Stände,19 Methodeninvokationen/17 PASS/zwei erhaltene FAIL,
zusätzlich erster Driver-SyntaxFAIL; sechs bestätigte Unitprozessenden.
Die konkrete Privacykorrektur ist aus Source3 normal/optimiert belegt und bleibt
bytegleich; die Importgrenze ist nun einschließlich Gegenfällen belegt.
Ausgabe weiterhin WARN mit festen Counts/Claims, Herkunft deklarativ und leere
Secretliste ausdrücklich ungeprüft. Kein historischer Report oder Domainaufruf.
Frische Rootabnahme mit vollständigen aktuellen Quellen-/Original-/Canonicalpins
bleibt vor dem einmaligen abgegrenzten Offline-Report erforderlich.

## Tatsächlicher Checkpoint3: Privacy bestanden, Helperfixture korrigieren

Source3 korrigiert gemischte bekannte Hexformen, JSONdecodierte verschachtelte
PART-Frames und die vier festen Pure-Modulnamen mit Typ-/Pfad-/Symlinkguard.
Der betroffene Privacycluster bestand normal und optimiert. Die neue Helperfixture
scheiterte in beiden Prozessen an ihrem positiven Windows-Pfadvergleich:
dieselben Dateibytes wurden als ExtendedPath und unpräfixierter Pfad verschieden
verglichen. Helper-Negativzweige wurden deshalb NOT_REACHED, nicht als bestanden
gezählt. Prozesse PID66616/23996 Poll/Returncode1, Originalkanäle vollständig erhalten.
Die optimierte Prüfung war vor dem Hinweis auf vermeidbare Wiederholung bereits
abgeschlossen; kein weiterer identischer Lauf.

Root hat den tatsächlichen Checkpoint nach drei geprüften Ständen geschlossen:
17 Methodeninvokationen,15 PASS/zwei FAIL, dazu Source1-Driver-SyntaxFAIL;
vier bekannte Unitprozessenden. Source-/Raw-/History-/Canonicalpins aktuell,
Privacykorrektur in Code und N/O belegt. Source4 ändert ausschließlich die
Helperfixture auf gleichwertige volle Dateibytes mit korrektem ExtendedRead;
eine betroffene normale und optimierte Prüfung, keine Privacy-/7+6-Wiederholung.
Keine Produktguardabschwächung, historische Offlineadmission weiterhin ausstehend.

## Source2-Checkpoint: konkrete Privacy-/Modulgrenzen korrigieren

Source1 privater Puredriver-SyntaxFAIL vor Testchild bleibt erhalten:0 Methoden,
TopPID NOT_CAPTURED. Source2 änderte ausschließlich die Driverformatierung;
erstmals sieben neue normale und sechs optimierte Fälle bestanden, tatsächliche
PIDs37980/69828 mit Poll/Returncode0 und gehaltenen Raw-/Input-/Quellenbindungen.
V1-Consumer, Expectedvertrag und alter Testprefix bleiben bytegleich.

Der enge Rootreview hält FIX_REQUIRED: bekannte UTF-8-/UTF-16-Hexformen werden
nur vollständig groß/klein erkannt; gemischte Hexschreibweise kann vor Inputdigest
passieren. Außerdem werden PART-Frames nur in äußeren Kanallines abgewiesen;
aufgeteilte Frames in einem decodierten JSON-ErrorMessage können passieren.
Beides ist mit je einem neuen unabhängigen reinen Probeaufruf tatsächlich
reproduziert. ToolExit0 bedeutet hier bestätigten Findingpfad, keinen Product-PASS.
Probe-PIDs und eigene Vor-/Nach-Sourcehashes wurden nicht erfasst und werden
nicht rückwirkend behauptet; eingefrorene Source2-Karte und gelesener Quellkontext
bleiben erhalten. Eine statisch belegte dritte Scopegrenze betrifft pure_helper:
vier reine Modulnamen müssen vor Import fest begrenzt sein; kein Fremdimport erfolgte.

Source3 korrigiert diese zusammengehörigen Guards mit gezielten neuen/betroffenen
N-/O-Gegenfällen. Keine alte grüne7/6-Suite wiederholen; aktuelle Source2-Originale
und Canonicalbytes vor Änderung vollständig sichern. Der tatsächliche Checkpoint3
wird erst nach dem dritten tatsächlich geprüften Stand geschlossen. Historischer
Report und sämtliche Native-/SQL-/Host-/Modellaufrufe0, keine Offlineadmission.

## Ausgangspunkt und begrenzter Nutzen

PR246 ist vollständig geschlossen:13 aktuelle Head- und11 Main-Checks bestanden,
Main e3d8d61e63a7661ccd6a06e5ba6136f57945ca69, voller gleicher Tree, sauberes
synchrones Main und eigene Branches entfernt.439 private Originaldateien sind
bytegenau gesichert; der Worktree ist tatsächlich archiviert. Ein HTTP502 des
Main-CLI-Watchers blieb separat erhalten; die tatsächlichen GitHub-Checks sind
direkt erfolgreich verifiziert, kein CI-Rerun. Der öffentliche Rollenlauf bleibt
ein begrenzter Teilnachweis mit positivem Produkt-WARN und offenen Qualifikationen.

Der bisherige [V1-Vertrag](SQL_SERVER_2025_AI_IDX012_RECORD_CONTRACT_REVIEW.md)
friert individuelle Captures ausdrücklich auf None und zwei historische Inputs
ein. Er darf die neue öffentliche Resultform mit25 Clientrecords, acht Kontexten
und zwei Kostenclients nicht durch Umdeutung aufnehmen. Ein eigener V2-Consumer
macht genau diese öffentliche Resultform für Anwender prüfbar. V1 und seine
historischen Pins/Claims bleiben unverändert; seine Welle wird nicht wiederaufgenommen.

## Endlicher SOURCE_ONLY-Schnitt

Ein Implementer und enger unabhängiger Rootreview für tatsächliche Typ-, Byte-,
Rollen-/SID-/Quellen-, Datenschutz- und Claimgrenzen. Höchstens sechs tatsächlich
geprüfte Quellenstände einschließlich relevanter SyntaxFAILs, Checkpoint nach
tatsächlich drei Zuständen und Hard6; kein Ausschöpfen mit identischen grünen Tests.
Betroffene normale Tests und erstmals betroffene Schutzfälle optimiert; neue
Fehlschläge nur mit verändertem Input oder neuer Evidenz korrigieren. Kein zusätzlicher
Planner, keine zweite Backlogwahrheit oder dauerhafte Cachebehauptung.

Scope: separater reiner Staticconsumer und fester Expected-V2-Vertrag, neue gezielte
Gegenfälle im bestehenden Testmodul, bestehendes [HowTo](../HowTo/SQL_SERVER_2025_AI_IDX012_DML_ROLE_RECORDS.md)
und exakt notwendige Auswahl innerhalb der bereits vorhandenen normalen/optimierten
CI-Prozesse. Keine zusätzlichen CI-/Review-/Modellprozesse. Kanonischer Backlog,
Ausführungsstand und Workstreamplan zeigen diesen separaten Schnitt.

Null neue SQL-, Container-, Provider-, Modell-, Compiler-, Download- oder Hosteffekte.
Keine Producer-/Selector-/Runtimejobänderung und keine Private-Runtimeimporte.
Nach vollständigem Sourcefreeze und Rootreview höchstens ein gebundener Offline-
Report aus dem unveränderten tatsächlich gesicherten Public-C3-Record; ursprüngliche
Nativewelle bleibt gestoppt. Dieser Read-/Reportentscheid ist keine Nativeadmission.

## Prüf- und Exportgrenzen

Verarbeitungsaufwand: Neue V2-Fälle nutzen die vorhandenen normalen und
optimierten Prozesse des bestehenden IDX-012-Testmoduls. Keine zusätzliche
Prozess-/Job-/Reviewkette oder Modellroute; alte grüne V1-Fälle werden lokal
nicht wiederholt. Die vorhandene Auswahl in select_runtime_workflow.py trennt
Tests/Static von den expliziten DGN-010-Runtimeabhängigkeiten und vergleicht den
tatsächlichen Runtimejobkörper bei Workflowänderungen. Runtimejob, Matrix und
Selector bleiben byte-/semantisch unverändert; die konkrete finale Auswahl wird
am eingefrorenen Diff mit dem tatsächlichen Readervertrag geprüft. Aktuelle
Head-/Main-Gates bleiben erforderlich. Logs werden gezielt an neuen Findings
gelesen; Verbrauch und Zeit werden nur bei tatsächlicher Messung angegeben.

In-Memory-Eingaben ausschließlich einfache feste Python-Typen; vollständige
fest begrenzte Strukturpopulation, sichere Inputs/Kanäle und kohärente UTF-8-SHAs,
tatsächliche Client-/Input-/Quellenfelder, zwei unverwechselbare Rechtegegenfälle,
acht geordnete Rollenkontexte und zwei zusammengehörige Kostenframepaare.
Öffentliche ExecutionSourcepopulation24 mit festen Pfaden/currentBytes binden;
kein frei wählbarer Record-/Modul-/Sourcepfad, Callback oder importierbarer Input.
Fremde Operator-/Admin-/DB-/Sessionbindungen, fehlende Captures, Typalias, widersprüchliche
Enden und behauptete Qualifikation dürfen keine kohärente Warn-Ausgabe erhalten.

Die Ausgabe enthält ausschließlich feste Status-/Claimgrenzen und begrenzte Counts.
Keine Tokens, SIDs, Pfade, Rohkanäle, Vektoren, Zeitstempel oder Credentials exportieren.
PID/Poll/Returncode/Input-/Sourcekohärenz ist ein Recordcheck, keine unabhängige
Attestation seiner Herkunft: DECLARED_NOT_INDEPENDENTLY_ATTESTED bleibt.
Die private Secretliste ist ein ausdrücklicher Pflichtparameter. Ihre Herkunft
und Vollständigkeit sind nicht unabhängig attestierbar. Bei leerer Liste bleibt
die Prüfung unbekannter ursprünglicher Credentials ausdrücklich
NOT_CHECKED_FOR_UNAVAILABLE_SECRETS; daraus entsteht kein SAFE-Default. Bekannte
Secretformen werden vor weiterer Verarbeitung abgewiesen, ohne Secret-/Password-
Digests oder Rohwerte zu exportieren. Fehlercodes enthalten keine Inputwerte.
Der historische Offline-Read bindet zusätzlich den vorhandenen tatsächlichen
Producer-Privacy-/Quellen-/Rootreviewbeleg; die ursprünglichen Credentials werden
nicht rekonstruiert. Das ersetzt keine unabhängige Consumer-Privacyprüfung.
Fehlende Ownerquery-, Server-/TDS-, vollständige DML-Error- und TP-PERF-/allgemeine
Runtimebelege bleiben NOT_ESTABLISHED; Generation UNKNOWN und Produkt-WARN bleiben.
Historische fünf Dokumentzwischenstände bleiben als Provenienz-WARN erhalten;
unbekannter Modell-/Tokenverbrauch bleibt UNKNOWN.

Stop beim ersten kohärenten abgegrenzten Source-/Offlinebefund oder Hard6/UNKNOWN.
Anschließend aktuelle lokale Prüfungen, PR-/Head-/Main-Gates, Integration in
origin/main, Synchronisierung und vollständige eigene Belegsicherung/Archivierung.
