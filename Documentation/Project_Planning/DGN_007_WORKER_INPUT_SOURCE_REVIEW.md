# DGN-007 – Workerquelle für vollständige Eingangsfolge

Stand: 20. Oktober 2026. Basis
`dcc5893af0c50c88aa0f848c3c908733c15dcbdc` nach vollständig geschlossenem PR268.
Status `CLOSED_PR269`.

## Priorität und gemeinsamer endlicher Rahmen

PR268: dreizehn finale PR-Checks/elf frische Main-Workflows SUCCESS, neue16 und
alte15 im Main ohne SKIP PASS, unabhängige Befundschließung, FullTree/Sync und
eigene lokale/Remote-Branchbereinigung bestätigt.
[Abschlussbindung PR268](https://github.com/gecompat/SQL_PerformanceSchulung/pull/268).
Der tatsächliche Report ist verbunden; §16.3 Schritte1–5 benötigen als nächste
zusammenhängende Quellenarbeit den Workerempfang samt Haltepunkten und EOF.

Ein Implementierungsowner, derselbe unabhängige Reviewer, höchstens sechs
stabile Source/Testkandidaten, Checkpoint2, harte Grenze6 einschließlich Auswahl-,
Source/Test-PRE, ausdrücklichem Lauf-GO, höchstens fünf gebündelter geänderter
Befundnachläufe, lokaler Tests, aktueller Gates, regulärer Integration und eigener
Branchbereinigung. Verbrauch UNKNOWN. Kein Reset früherer ausgeschöpfter Scopes,
keine Wiederholung der abgelehnten alten Fitroute oder unveränderter grüner Tests.

## Konkrete Sources und API

Neue reine Generatorquelle `Tests/Tools/dgn007_worker_input_source.py` mit
`build_worker_input_control_bootstrap(profile_raw, *, logical_profile,
expected_soabi, expected_destshared)`. Sie verwendet die feste siebzehnte Route
und ein neues festes Inlinefragment. Alle bisherigen siebzehn Generatorausgaben
bleiben byteidentisch. Kein weiterer Scriptimport oder Projektadapter: weiterhin
genau importlib.util/sys/sysconfig/json/struct und genau die beiden Controls.

Die neue endgültige Scriptquelle wird außerhalb des Workers mit ast.parse/
ast.unparse dargestellt. Nur die neue Route erhält diese Formatierung; keine
Umbenennung, Entfernung von Operationen/Docstrings oder Änderung von Literalen.
Eine unabhängige vollständige AST-Oracle prüft gegen die siebzehnte Quelle plus
Inlinefragment und explizite Mainfolge. Tatsächlicher vollständiger Rawliteral-
und131072-Byte-Fit bleiben zwingend. Kein Fallback auf andere Versionen oder Caps.

Main lädt gebunden die Kontrolle, bindet das Profil und initialisiert vor
Metadata einen eigenen privaten I/O-Owner. Danach bindet die bestehende Report-
Initialisierung die gesamte Scriptnamespace, ein einmaliger privater Sealer hält
deren tatsächliche Entryclosure und unveränderte Script-/Kontroll-/Provider-/
Encoderanker, und erst danach ruft Main die neue Eingangsfolge auf. Main erzeugt
nach dieser Bindung keine weiteren globalen Resultateinträge. Das Initialisieren
und Versiegeln ersetzt weder eine fehlgeschlagene Bindung noch einen Versuch.

Der I/O-Owner hält ursprüngliche ausführbare Helfer/Code/Globals sowie ausgewählte
os.read/os.write-Objekte aus der gebundenen Kontrollruntime, ausschließlich fd0
zum Lesen und fd1 zum Schreiben. Keine öffentlichen Read-/Write-Callbacks oder
fremden Receipts. Native Builtinprovider oder eigene quellengebundene Funktionen
werden exakt typisiert und unverändert gehalten; importierte Runtime-/OS-Provider
bleiben ausdrücklich angenommene Vertrauensgrenze, keine transitive Hostattestation.
Die bekannte FileFinder-Hookinstanz wird vor Metadata aus der festen Zweierstruktur
gehalten; deren Code-/Factory-/Closurekonformität prüft die vollständige bestehende
Profilaufnahme. Das wählt keine eigene Sollinventur aus dem aktuellen Cache.

## Einmalige vollständige Folge

Der private Owner reserviert den gesamten Eingangsversuch vor dem ersten Read.
Alle nachfolgenden Phasen verwenden dieselben privaten ursprünglichen Anker und
denselben nicht erneuerbaren Zustand; Reentranz, erneutes Seal/Init, Teilfehler
oder fehlgeschlagener Abschluss erlauben keinen Retry. Ersetzbare Globalmarker
haben keine eigene Prüfautorität, Fremdobjekte scheitern vor Attribut/Dispatch.

1. Genau16Headerbytes, danach ausschließlich die angekündigte vollständige M.
   Magic/Längen/Metadata-/Body-/Framecaps vor weiterem Read; kein Vorlesen eines
   Commands oder Bodybytes. Aus der vollständigen kanonischen Syntax wird die
   Nonce als privates32-Byte-Aufnahmetoken gewonnen. Die bestehende versiegelte
   Reportentry führt danach erneut den vollständigen Receiver inklusive I7/K8/
   W6/beider D9/Originaldigest und die tatsächliche Aufnahme aus. Der zusätzliche
   reine Syntaxvorlauf ist für Tokenwahl nötig; keine zweite Providerbaseline.
2. Ausschließlich deren tatsächliche vollständige Reportrecords mit bestätigten
   Writeoffsets schreiben. Danach genau eine gebundene BODY_RELEASE-Zeile lesen
   und mit bestehendem vollständigem Commandmatcher gegen denselben K8 prüfen.
3. Genau die neun angekündigten Bodies ohne Decode/Join/Normalisierung aufnehmen;
   Nullbodies führen zu keinem Read. Erst danach genau BODY_END lesen/prüfen.
   Bestehender vollständiger Rawbodyprüfer gegen dieselben gehaltenen M-/I7/W6/K8-
   Objekte prüft alle Längen, Descriptors, Originaldigest und Einzelrawhashes.
4. Tatsächliche frische lokale Profilaufnahme mit ursprünglichem Token/Hook und
   Workerwahl; vollständiger Vergleich aller tatsächlichen Scalars gegen den
   bereits gehaltenen Report. Erst danach kanonisches INPUT_COMPLETE mit exakt
   Ordinal/Nonce/eigenem vollständigem Kontextdigest, höchstens256Bytes
   einschließlich LF, schreiben. Kein zweiter PRE-/POST-Report auf Wire.
5. Genau die gebundene IMPORT_RELEASE-Zeile prüfen, dann genau EOF ohne Zusatzbyte
   verlangen. Erst danach private gehaltene geprüfte Bodies/Metadata/Profilwerte
   zurückgeben. Kein Kandidatencode, Modulimport oder Loaderdispatch erfolgt.

Commandaufnahme höchstens256Einzelbytes bis einschließlich LF, keine Readgröße
über die aktuelle Phase hinaus. Typen/Längen bestätigter Read-/Writeresultate
vor Operationen prüfen; Teilwrites halten ihren Offset, Nullfortschritt scheitert
fest. Jede syscallnahe Operation wird vor Aufruf gebucht, auch Fehler/Teilwrites.
Feste atomare Fehler ohne Rohtexte oder Teilprofil/Teilbodies; dominante letzte
Script-/Kontroll-/Provider-/Encoder-/I/O-Bindungsprüfungen auch nach Fehlern.

## Kosten und ausdrücklich offene native Aufnahme

Für diesen künftigen festen Worker höchstens1088 eigene Read-/Write-Aufrufe,
Chunks höchstens4096, bestätigte Eingangsbytes einschließlich dreier Commands
höchstens1064960, Ausgabe höchstens65536 und einzelne Zeilen höchstens1024.
Der Childrahmen ist eine konservative Teilzuweisung aus dem vorhandenen globalen
4096-I/O-Rahmen, kein zusätzliches Budget: vor einem späteren nativen Start muss
der Parent1088 je ausgewähltem Worker unwiderruflich reservieren; drei ergeben
3264, verbleiben832 für eigene Parent-I/O. Der heutige Parent hat diese neue
Reservierung noch nicht und darf die neue Quelle daher noch nicht operativ
auswählen. Konkrete gemeinsame Buchung/Admission bleibt ein eigenes Folgegate.
Keine Zählung tatsächlicher Workers aus einem synthetischen Ergebnis behaupten.

Die gemeinsame20s-Deadline, kumulativ10sCleanup,64No-progress-Schritte,65536globale
Ausgabebytes,43Zeilen je Slot, vollständige Gruppenabsenz/Exit/EOF bleiben beim
bestehenden äußeren Parent verbindlich. Die neue Quelle startet keine Timer,
Worker oder Ersatzcleanup. Blockierende OS-Aufrufe sind erst unter diesem separat
geprüften äußeren Owner zulässig. In diesem Schnitt gibt es ausschließlich eigene
Modellprovider und keinen echten Read/Write/Worker. SESSION_END/Loaderrecords und
tatsächliche Kandidatenoperationen bleiben getrennte Folgearbeit.

## Suite, unabhängige Gates und Grenze

Neue portable Suite `Tests/Static/test_dgn007_worker_input_source.py`, höchstens
16Methoden mit vollständig eigenen I/O-Queues/-Modulen und externen Zählern.
Sichere kleine PR268-Fixture darf optionale Builder-/Setupvorläufe erhalten,
bestehende Defaults bleiben unverändert. Setup nur vor Bindung auf eigenen
Objekten, keine echten Stdlib-/OS-/Cachepatches. Eigener vollständiger I7/D9/K8-
Oracle samt tatsächlichen Bodyrawbytes und unabhängigen Command-/R4-/INPUT_COMPLETE-
Bytes. Keine alten57-/Bootstrap-/Nativeharnessimporte. Eigene Modell-Compile-/
Execpfade definieren nur die neue Quelle ohne direkte Imports/Mainausführung.

Positive alle drei Rollen, binäre/CRLF-/Nullbodies, echte bestätigte Fakeprovider-
Teilreads/-writes, beide Haltepunkte, frische zweite tatsächliche Profilaufnahme,
exaktes EOF. Negative sämtliche frühen EOFs/Phasen/Command-/Nonceabweichungen,
späte Bodyhash-/Descriptorabweichung, Profil-/Hook-/Cacheverlust nach Report,
Provider-/Encoder-/Script-/I/O-Funktionsdrift auch nach Fehler, falsche Read-/Write-
Typen/Counts/Nullfortschritt, IO-/Byte-/Zeilencaps ohne Reset, Reentranz/Retry,
fremde Marker/Getter und keine Kandidatenoperation vor oder nach EOF. Mutations-
punkte, unverwendete fremde Callbacks und aktuelle Phase extern nachweisen.

Auswahl-PRE vor Implementierung, Source/Test-PRE samt ausdrücklichem einmaligem
Lauf-GO vor neuen Suiteimporten/Compile-/Execpfaden; danach neue16 Windows/Linux
und reguläre eng ausgewählte CI samt betroffenen bestehenden Fixtureconsumern.
Neuer Workflow für eigene Quelle/Suite/sichere Fixtures/Plan/sich selbst sowie
die feste Kontrollgenerator- und tatsächliche Profilraw-Abhängigkeit. Keine
SQL-/Scanner-Selbsttestauswahl oder Voll-Logs; kein zusätzliches Reviewmodell.

Keine generierte Mainausführung, physischen OS-I/O, Pipes, Workerstarts, operative
Installation/volle Inventur, Kandidaten-/DGN-Imports, Docker oder SQL in diesem
Schnitt. Source-Go ist kein natives Lauf-GO. Separater Scriptlocator, vollständige
separat quellenbegründete S15/P11, Fünf-Formen-/64KiB-Fit, Parent-Admission/IOreserve,
SourceLoader/SESSION_END und unabhängige native Gesamtabnahme bleiben offen.
Alle Runtime-/Worker-/Import-/UsedBytes-/Trust-/Methodenattestationsflags false.

## C1 und unabhängige Auswahl

Auswahl-GO auf Basis und Plan-SHA256
`619aacd73ee7733e0365fefac98c43b522f27b0064920e79ac3b0967fdf1f484` mit zwei
Auflagen: nach dem Report-Scriptsnapshot keine gehaltenen Globalwerte oder
Closurezell-Inhalte austauschen, keine neuen Ausnahmen/Rebaseline; beide
Workflowtrigger enthalten Generator- und Profilraw-Abhängigkeit.

C1 ergänzt neue separate Generatorquelle und16eigene Modellmethoden. Ausschließlich
die neue Ausgabe verwendet AST-Darstellung. Die alte siebzehnte Route erhält in
dieser neuen Ausgabe genau einen expliziten privaten Handoffaufruf unmittelbar
nach ihrer ursprünglichen Markersetzung und vor ihrem Scriptsnapshot. Er übergibt
die tatsächlichen Kernelanker, Markeridentität und Entryclosure direkt an den
vorher initialisierten I/O-Owner. Dessen betreffende Closurezelle erhält ihren
endgültigen Inhalt vor diesem Snapshot; Seal und Run tauschen danach keinen
gehaltenen Globalwert oder Zellinhalt aus. Nur privater eigener Listeninhalt für
Versuch/Status/Zähler schreitet fort. Keine neue Ausschlussliste oder Aufnahme
aktueller Ersatzreceipts. Die vollständige unabhängige AST-Oracle enthält diesen
einen Handoff und die explizite neue Mainfolge, sonst sämtliche bisherigen
Definitionen/Operationen/Literale unverändert.

Die kleine PR268-Fixture erhält optionale Builder-/Setup-Parameter; ihre Defaults
bleiben unverändert. Neues Setup erzeugt nur eigene OS-Modul-/Queueobjekte vor
Profilbindung. Read/Writeprovider sind eigene Funktionen in eigener OS-Namespace,
keine nativen Endpoints. Externe Traces prüfen tatsächliche Phasenoffsets und
Aufrufzahlen. Eingangs-/Ausgabecaps werden vor bestätigender Verwendung beziehungsweise
Write geprüft, EOFprobe bleibt genau ein Byte. Der feste Childrahmen wird vor
jedem Read/Write gebucht, auch Fehler/Teilwrites; keine Budgeterneuerung.

Neue CI enthält alle festen Generator-/Profil-/Fixtureabhängigkeiten in beiden
Triggern. Bestehende betroffene Fixtureconsumer bleiben erhalten. AST3 und
Methodenzählung16 PASS, gesamte bisherige Generatorquelle mit allen17Routen
gegen Basis byteidentisch. Noch keine neuen Suiteimporte oder Generierungs-/
Compile-/Exec-/Modellläufe. Unabhängiger Source/Test-PRE und ausdrückliches
Lauf-GO ausstehend. Ein Source/Testkandidat/max6, kein Nachlauf, Verbrauch UNKNOWN.
Keine echte OS-I/O/Main-/Worker-/Inventur-/SQLprobe; alle offenen Gates erhalten.

## C2 – geschlossener I/O-Providernamespace und Checkpoint2

C1 `b60ffcbacec68c006831b0a5bb4574d3c8757145` unabhängig vollständig geprüft:
ein P2, kein Lauf-GO. Die OS-Namespace wurde vor read/write-Lookups nicht auf
sämtliche Schlüssel geschlossen; ein kollidierender Fremdkey konnte fremden
Vergleich aufrufen. Nach einem Providercallback fehlte vor __dict__ außerdem
die erneute exakte Modultypprüfung bei veränderbarer ModuleType-Klasse.
Keine weiteren offenen Befunde, keine Suiteimporte oder Proben.

C2 prüft vor jedem solchen Namespacezugriff den exakten Modultyp und danach
exaktesdict, höchstens16368Einträge und alle exakten UTF8-/NUL-freien str-Keys
mit höchstens4096Bytes vor irgendeinem Lookup. Vorhandene 256er-Dictionary-
Grenzen werden nicht auf vollständige OS-Namespaces übertragen. Die bestehende
Methode erhält PRE- und Callback-POST-Gegenproben für Modulunterklasse und
jeweils read/write-kollidierenden Fremdkey: externe EQ-/Getattribute-Zähler null,
erreichte Mutation und null beziehungsweise genau ein I/O-Aufruf vor Ablehnung.
Weiterhin16Methoden, keine neue Fixture-/Workflowabhängigkeit.

Checkpoint2: zwei stabile Kandidaten/max6, ein gebündelter geänderter Nachlauf,
kein Lauf eines Kandidaten. Scope, Pflichtgates und offene native Grenzen
unverändert; unabhängiger Delta-PRE und ausdrückliches einmaliges Lauf-GO für
die neue16 auf Windows/Linux sowie selektierte CI ausstehend. Verbrauch UNKNOWN.
Keine Quellencapänderung, keine neue Ausschlussliste oder Baselineerneuerung.

## C3 – reine Einrückungsdarstellung nach tatsächlichem Fitfehler

C2 `33cc349a6f347e955919460732dfb9649ebfbcd8` unabhängig: P2 geschlossen,
keine offenen Deltabefunde, ausdrückliches einmaliges Lauf-GO. Danach neue16
Windows3.14.7 in1.599s mit16SCRIPT_LIMIT-Fehlern und einem zusätzlichen
Cache-Oraclefehler; Linux3.12.3 in1.488s mit16SCRIPT_LIMIT-Fehlern. Sämtliche
Modellfälle scheiterten bereits beim Quellenbau, keine innere Semantik abgenommen.
Der zusätzliche Windowsfehler stammt vom erstmals verzögert geladenen
Stdlibmodul _ast_unparse. Kein erfolgreich generierter Größen-/SHAwert behauptet.

C3 verkürzt ausschließlich führende Codeeinrückungen der neuen Ausgabe nach
AST-Darstellung von vier auf ein Space je Level. Der Tokenvorlauf bearbeitet
nur die erste Tokenstartposition einer Codezeile; Inhalte mehrzeiliger
STRING-Token bleiben unverändert. Alle AST-Operationen und Literale bleiben
über die vollständige unabhängige Oracle verpflichtend; zusätzliche eigene
mehrzeilige Docstring-Gegenprobe. Keine Capanhebung oder Änderung früherer
Quellenrouten. Vor der unveränderten Testcachebaseline bereitet ein neutrales
ast.Constant-Objekt den Standardbibliotheksdarsteller vor, keine neue Modulcache-
Ausnahme und kein Worker-/Kandidatenimport.

Drei Kandidaten/max6, zwei geänderte Nachläufe. Gezielter unabhängiger C3-Delta-
PRE und einmaliges Lauf-GO vor jeder neuen Probe ausstehend. Verbrauch UNKNOWN;
sämtliche nativen offenen Gates bleiben unverändert. Kein unveränderter Retry.

C3 `e2760c84bef51c8fd0c2c1b0017bf95bc7aea652` unabhängig ohne offene
Deltabefunde mit ausdrücklichem einmaligem Lauf-GO. Danach neue16 unter
Windows3.14.7 in36.223s und Linux3.12.3 in25.617s ohne SKIP PASS. Tatsächlicher
vollständiger Quellenfit höchstens131072Bytes, aktuelle vollständige Rawliteral-
gleichheit, alle fünf direkten Imports, ganze AST-Erhaltung einschließlich
mehrzeiligem Docstring, alle drei Rollen, echte bestätigte Fakeprovider-Teil-
transfers, frische zweite Aufnahme und sämtliche negativen Modelle ausgeführt.
Die sechs PRE-/POST-Modultyp-/Schlüsselgegenproben erreichen ihre Mutation bei
null Fremdvergleich/Getattribute und keinem Folgedispatch. Kein nativer Nachweis.

Unveränderte Produkt-/Suitequellen bleiben an C3 gebunden. Nur Ergebnisdokumentation
ergänzt; aktuelle Head-/Base-Gates, reguläre Integration, frische Main-Gates,
FullTree/Sync und eigene Branchbereinigung folgen. Drei Kandidaten/zwei Nachläufe
im bestehenden Rahmen, Verbrauch UNKNOWN. Keine weitere unveränderte Lokalprobe.

## Regulärer Abschluss

PR269 regulär in `e456c535bc7a75d72d5034587657f6bcb46a27dd` integriert:
neun finale PR-Checks SUCCESS/CLEAN an Headce35936 und unveränderter grüner
Basisdcc5893 mit elf Main-Workflows SUCCESS. Sieben frische Main-Workflows
SUCCESS, neue16 in24.385s und bestehende Report16 in3.514s ohne SKIP PASS.
Vollständiger Baumvergleich, sauberer Main-/origin-Sync und eindeutig eigene
lokale/Remote-Branchabwesenheit frisch bestätigt.
[Vollständige Abschlussbindung](https://github.com/gecompat/SQL_PerformanceSchulung/pull/269).
Drei Kandidaten/zwei Nachläufe geschlossen; kein nativer Erfolgsclaim. Die
offene gemeinsame Parentreserve wird separat endlich gewählt, kein Reset dieses
oder früherer Scopes. Sämtliche offenen nativen Gesamtgates bleiben erhalten.
