# DGN-007 – erste quellengebundene Loaderinvocation nach EOF

Stand: 20. Oktober 2026. Basis
`20549ae4e7dbb31c2ffb4d5b051395b8033db18e`, PR270 vollständig geschlossen.
Status `C4_SOURCE_TEST_DELTA_PRE_PENDING`.

## Priorität und gemeinsamer endlicher Rahmen

PR270 regulär geschlossen: zwölf finale PR-Checks/zehn frische Main-Workflows
SUCCESS, neue12 und bestehende Handshake12/28Native, Session16/Workerinput16
ohne SKIP PASS, unabhängiger Review, FullTree/Sync und eigene lokale/Remote-
Branchabwesenheit bestätigt. [Abschlussbindung](https://github.com/gecompat/SQL_PerformanceSchulung/pull/270).

Die tatsächliche Quellenverwendung ist der nächste offene Funktionsbereich.
Zuerst wird genau die einzige SOURCE-Invocation des Proxyworkers2/Index2 nach
§33 gebunden. Sie hat keine eigenen verschachtelten Projektimporte oder Parents.
Runner/Harness, Resolver-/Finderrouten und Parentregistrierung bleiben getrennte
Folgeschnitte. Die alte Memoryloader-Fixture führt lediglich ihre vier festen
synthetischen Quellen mit eigener Kontextdomain aus; sie wird weder als
Workerreceipt übernommen noch zu einer Quellenautorität umgedeutet.

Ein Implementierungsowner root, derselbe unabhängige Reviewer, höchstens sechs
stabile Source/Testkandidaten mit Checkpoint2 und harter Grenze6, höchstens fünf
gebündelte geänderte Nachläufe einschließlich Auswahl-, Source-/Testreview,
Lauf-GO, Tests/Koordination/CI, regulärem Merge, Main-Gates und Branchcleanup.
Verbrauch UNKNOWN. Kein Reset alter ausgeschöpfter Scopes oder Wiederholen
unveränderter grüner Tests. Quellenfitfehler gelten als Fehler, kein Capwechsel.

## Konkrete additive Quelle und Ownerroute

Neue reine Generatorquelle `Tests/Tools/dgn007_proxy_loader_source.py`, API
`build_proxy_loader_control_bootstrap(profile_raw, *, logical_profile,
expected_soabi, expected_destshared)`. Sie verwendet ausschließlich die bisherige
vollständige Eingangsquelle aus PR269 und ein festes neues Fragment. Frühere
Quellenrouten und deren Bytes bleiben unverändert. Kein zusätzlicher direkter
Scriptimport: importlib.util/sys/sysconfig/json/struct bleiben die fünf Imports.
Neue endgültige Quelle mit vollständigem aktuellem Profilrawliteral muss weiterhin
höchstens131072Bytes umfassen. Ganze unabhängige AST-Oracle beschreibt exakt
das bisherige Script plus neue Definitionen und ausdrücklich folgende Handoffs/
Mainfolge; Literale und sonstige Operationen bleiben erhalten. Ab C4 darf die
unten ausdrücklich begrenzte lokale Alpha-Umbenennung unabhängig rückgeführt
werden, bevor die vollständigen ASTs verglichen werden.

Vor I/O-Initialisierung erzeugt die neue Sourceinitialisierung einen privaten
einmaligen Sourceowner mit gebundenen ursprünglichen Compile-/Execprovidern,
Modul-/Specklassen und eigenem Loader. Danach übergibt die tatsächliche I/O-
Initialisierung ihren ursprünglichen privaten Owner und Entry direkt an diesen
Owner, noch vor dem bestehenden Report-Scriptsnapshot. Keine spätere neue
Baseline, Ausschlussliste oder Ersetzung gehaltenen Globals/Closurezell-Inhalts.
Private eigene einmalige Listenhalter dürfen Status/Invocation/Zähler fortschreiben.

Die neue Mainentry ruft ausschließlich die so gehaltene ursprüngliche I/O-Entry
einmal auf; keine öffentliche Received-/Loaderreceipt oder Callerstatuswahl.
Nur am erfolgreichen Ende der tatsächlichen vollständigen I/O-Folge, nach
IMPORT_RELEASE und bestätigtem exaktem EOF, führt deren eigener Code einen
direkten privaten Handoff der tatsächlichen gehaltenen M-/Body-/Profilwerte
sowie seines ursprünglichen privaten I/O-Owners und Frames durch. Der Handoff
bindet ursprüngliche Owneridentität und aktive private einmalige Invocation;
Typ-/Code-/Globals-/Closureidentitäten gehen Dispatch und Attributzugriff vor.
Keine frei wählbaren Writer-/Guardcallbacks oder anderswo aufgenommenen Receipts.
Feste neue Quellenwrites verwenden ausschließlich den darin schon gehaltenen
fd1-Provider sowie dieselben ursprünglichen I/O-/Ausgabezähler und Caps.
Die abschließende tatsächliche I/O-Rückgabe muss denselben privat übergebenen
Payload halten. Fehler, Reentranz, fehlender Handoff oder erneuter Aufruf sperrt
die Sourceinvocation; keine Recovery oder Compile aus bloßen Statusfeldern.

## Genau eine wirkliche SOURCE-Invocation

Nur vollständig empfangener/geprüfter Worker2 mit Einstieg docker_sqlcmd_proxy,
Index2 und derselben gehaltenen K8-/D5-Auswahl ist hier ausführbar. Unsupported
Runner/Harness liefern keinen Sourceerfolg und führen keine Kandidatenoperation
aus. Eigene Origin-/Objektslots sind feste2/1, Sequenz1; der vollständige eigene
K-Kontextdigest wird mit bestehenden gebundenen Helfern berechnet.

Vor BEGIN hält die private Invocation dieselben tatsächlichen Bodybytes2,
deren D5/K, eigenes exaktes Modul-/Spec-/Loaderobjekt, private logische Origin
und ursprünglichen Cache. Alle neun Kandidatennamen und beide Parents sind
vorher abwesend. Eigene Modul-/Spec-/Loader-/Name-/File-/Origin-/Cachebindungen
werden vor und nach jeder Wirkung geschlossen überprüft. Modul und Cacheplatz
werden innerhalb derselben reservierten Invocation vorbereitet; kein Suchpfad,
Finder oder fremder Loader wird zur Quellenauflösung verwendet.

BEGIN `["BEGIN",2,1,"SOURCE",2,context_digest,raw_sha256,2,1]` wird kanonisch
einschließlich LF über den tatsächlich gehaltenen bestätigten Writer geschrieben,
bevor genau diese gehaltenen Bytes mit compile(raw, origin, "exec",
dont_inherit=True, optimize=0) kompiliert werden. Keine get_code-/Dateiread-Route.
Der eigene direkte Loader führt ausschließlich dieses gehaltene tatsächliche
Codeobjekt im gehaltenen Modulnamespace aus. COMPLETE mit denselben acht Feldern
setzt zurückgekehrtes Exec genau dieses Codeobjekts und alle kohärenten POSTs
voraus. Vorherige Syntax-/Exec-/Cache-/Providerfehler verhindern den COMPLETE-
Versuch. Fehler während oder nach bestätigtem Write können Wirebytes nicht
rücknehmen; sie verhindern privaten bestätigten Loadererfolg und späteren Footer.
Private Exception-/Raw-/Locatorwerte bleiben aus öffentlichen Fehlern heraus.

Die ursprünglichen Script-/Kontroll-/Provider-/Encoder-/I/O-Pins dominieren auch
nach Fehlern. Runtime-/Builtin-/Importmechanik ist eine explizite angenommene
Vertrauensgrenze, keine Hostattestation oder Sandbox. Projektquellen müssen
weiter separat ausgewählt und geprüft werden. Hier werden tatsächlich nur die
vorab ausgewählten eigenen synthetischen Rawvarianten ausgeführt.

## Gemeinsame Kosten und offene Gesamtabnahme

Alle Loaderwrites verwenden denselben ursprünglichen I/O-/Ausgabebudgethalter,
keinen neuen Writerzähler oder Childrahmen.1088 je Worker aus PR269/PR270 bleiben
einschließlich dieser zusätzlichen Writes unverändert; ausgeschöpfte Reserve
lehnt vor dem Aufruf ab. Bestehende20s-/10s-/4096-/64-/65536-/Zeilencaps bleiben
unverändert. Diese Source bildet keinen SESSION_END-Footer und keinen ganzen
Workererfolg. Erfolg ist ausschließlich eine begrenzte private Quelleninvocation
für Proxy2; alle Attestationsflags bleiben false.

Kein nativer Start, keine operative Inventur/Installation/S15/P11-Auswahl, kein
Fünf-Formen-/64KiB-Gesamtnachweis, kein DGN-/Projektcodeimport oder SQL in diesem
Schnitt. Die neue Quelle wird nicht im operativen Parent ausgewählt. Runner/
Harness, Parents, vollständige Importfolge, Footer/Kanalhash, Replay-/Consumption-
und Gesamtlauf-/Trust-/Methodengates bleiben offen. Ein isolierter Quellenfit
oder synthetischer Loader-PASS ersetzt keinen dieser Nachweise.

## Konkrete portable Modelle und unabhängige Gates

Neue Suite `Tests/Static/test_dgn007_proxy_loader_source.py`, höchstens16Methoden.
Kleine eigene PR269-I/O-Fixture darf einen optionalen Builder mit unverändertem
Default erhalten; weiterhin eigene Fakecache-/OS-/Profil-/Encoder-/K-/Bodydaten.
Zusätzliche eigene Builtinprovider-Namespace nur vor Bindung, keine echten
Builtin-/Stdlib-/OS-/Cachepatches. Modellquellenstrip entfernt weiterhin direkte
Imports und generiertes Main; keine tatsächlichen Module im realen sys.modules.

Feste sichere eigene Body2-Varianten: LF/CRLF `SYNTHETIC_VALUE=7`, Syntaxfehler,
Execfehler und gezielte eigene Namespace-/Spek-/Cacheabweichungen ohne Imports,
Dateizugriff, Netzwerk, Subprozesse oder SQL. Sonstige acht Bodies bleiben opake
eigene Bytes. Externe Traces zeigen EOF vor BEGIN, bestätigten BEGIN vor Compile,
genau gehaltenen Rawinput/Codeobjekt/Modulnamespace bei Exec, COMPLETE danach
und vollen kanonischen unabhängigen Recordbytes. Vorzeitige/fehlende/forgierte
Handoffs, Reentranz/Retry, Fremdgetter/-Callbacks, Compile-/Exec-/Cache-/Spec-/
Origin-/Provider-/I/O-Drift sowie Budgeterschöpfung vor Dispatch scheitern fest.

Vor Implementierung unabhängiger Auswahl-PRE. Am stabilen Kandidaten vollständiger
Source/Test-PRE und ausdrückliches einmaliges Lauf-GO für neue16 Windows3.14.7/
Linux3.12.3 und reguläre selektierte CI samt tatsächlich betroffenen kleinen
Fixtureconsumern. Keine alten57-/Bootstrap-/Nativeharnessimporte. Keine native
oder echte DGN-Rawexecution. Enger Workflow mit vollständigen tatsächlichen
Quell-/Profil-/Fixture-/Planabhängigkeiten; Registry/Governance/Privacy unverändert.
Nach unabhängiger Befundschließung nur mit aktuellen grünen Head-/Base-Gates
regulär integrieren, danach frische Main-Gates, FullTree/Sync und sichere eigene
Branchbereinigung. Keine Gateumgehung oder zusätzlichen Modelle/Automationen.

## Auswahl und C1

Auswahl-GO unabhängig auf Basis und Plan-SHA256
`05f70536412bd36790220b79fc5c04a6c8ae6d521a55d609d1dd11a70991ee97`.
Auflagen: EOF-Handoff hält nur Daten/ursprüngliche Fähigkeiten; kein BEGIN oder
Compile vor tatsächlicher erfolgreicher I/O-Rückgabe und derselben Payloadidentität.
Kanonischer Cache-/Spec-/Modulname docker_sqlcmd_proxy, Bootstrap-__main__ erhalten,
Typen/Namespacekeys vor Zugriff; nur eigener identischer Cacheeintrag bei Fehler
entfernen. Wire-/POST-Grenze wie oben präzisiert. Keine offene Auswahlfrage.

C1 implementiert die feste additive Quelle mit zwei expliziten Handoffs und
neuer Mainfolge. Der EOF-Handoff übernimmt ausschließlich die Original-Owner- und
Frameidentitäten mit tatsächlichem Datenpayload. Lokale write/guard-Funktionen
werden weder angeboten noch später dispatcht. Der feste zusätzliche Quellenwriter
nutzt denselben bereits gebundenen fd1-Provider, state[3]/state[5] und dieselben
Caps; keine neue Budgetaufnahme. Ursprünglicher Kernelcheck sowie rohe gehaltene
Fn-/Code-/Globalsprüfungen gehen Helferdispatch vor/nach externen Aufrufen vor.
Einmaliges privates Execpermit wird erst nach bestätigtem vollständigem BEGIN
erteilt und vor Compile verbraucht; vorzeitiger direkter Loaderaufruf ist sticky.

Eigene Modul-/Spec-/Loader-/Code-/Rawinvocation bleibt privat und dieselbe.
ModuleSpec wird über die zuvor gehaltene Klasse erzeugt, deren Klassenmapping/
Methodenzustände vor/nach Wirkungen geprüft werden. Candidatebuiltins sind eine
eigene Kopie; die ursprüngliche Scriptbuiltin-Namespace bleibt separat gepinnt.
Nur der eigene identische fehlerhafte Cacheeintrag wird entfernt; fremde Slots
und Bootstrap-__main__ bleiben erhalten. Kein Resolver/Finder/Dateiread/PYC.

Neue16 Modelle mit eigenen Builtinproviderfunktionen, Fakecache/-I/O/-Profilen
und externen Compile-/Exec-/Wiretraces; nur vorgewählte sichere synthetische
Body2-Varianten. Bestehende kleine Eingangsfixture erhält nur optionalen Builder,
Default unverändert. Vollständige unabhängige AST-/Literaloracle und tatsächlicher
aktueller131072-Byte-Fit bleiben vor Semantik zwingend; bislang unbekannt.
Neue CI enthält sämtliche tatsächlichen Quell-/Profil-/Fixtureabhängigkeiten.
Noch keine Suiteimporte/Generierung/Compile-/Execprobe. Ein Kandidat/max6, kein
Nachlauf, Verbrauch UNKNOWN; Source/Test-PRE und ausdrückliches Lauf-GO ausstehend.

Primärquellen für die verwendete Python3.12-Schnittstelle, geprüft am20.Oktober2026:
[ModuleSpec](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec)
beschreibt getrennte Spec-/Modulattribute;
[Loading](https://docs.python.org/3.12/reference/import.html#loading) beschreibt
Cachepublikation vor Exec und Entfernung des fehlgeschlagenen Moduls;
[compile/exec](https://docs.python.org/3.12/library/functions.html#compile)
beschreibt gehaltene Bytes als Compileinput und Codeobjekte zur Ausführung.
Die engeren Handoffs/Identitäts-/Budget-/Recordbedingungen sind Projektvertrag.

## C2 und Checkpoint2

C1 `3934b44d783dd826f7beed586ac1625c7a590ed6` unabhängig vollständig geprüft:
ein P2, kein Lauf-GO. Der fortgesetzte I/O-Guard prüfte den ursprünglichen
Report-used-Zustand[6] und Eingangsbytezähler[4] nicht vollständig. Keine weiteren
offenen Befunde; weder Generator-/Suiteimporte noch Proben ausgeführt.

C2 prüft[6] vor Kernel-Dispatch mit isTrue und[4] als exakten Integer innerhalb
0..1064960. Dieselbe bestehende Post-Wire-Methode ergänzt sieben späte eigene
Callbackmutationen für Bool/negative/überschrittene/fremde Bytezähler sowie
falsche/fremde Report-used-Zustände. Mutation tatsächlich erreicht, private
Bindingablehnung und null Fremdgetter/-vergleich; bereits tatsächlich vollständig
geschriebene COMPLETE-Bytes bleiben erhalten. Kein zusätzlicher Source- oder
Wireerfolg daraus. Weiterhin16Methoden; keine neue Quell-/Workflowabhängigkeit.

Checkpoint2: zwei Kandidaten/max6, ein geänderter Nachlauf, Verbrauch UNKNOWN.
Unabhängiger Delta-PRE und ausdrückliches einmaliges Lauf-GO ausstehend; aktueller
vollständiger Quellenfit und sämtliche inneren Modelle weiterhin ungeprüft.
Kein Capwechsel, kein alter Scope-/Testrerun oder nativer/DGN-/SQLlauf.

## C3 – horizontale Darstellung nach bestätigtem Fitfehler

C2 `0b2b360953dea8a73a2ddb84ddb8a6e1afbf27b4` unabhängig ohne offene Befunde
mit einmaligem Source/Test-Lauf-GO. Danach neue16 unter Windows3.14.7 in4.588s
und Linux3.12.3 in3.895s jeweils16SCRIPT_LIMIT-Fehler vor Modellsemantik.
Kein semantischer PASS und keine tatsächlich erzeugte Sourceabnahme.

C3 entfernt ausschließlich überflüssige horizontale Abstände zwischen Tokens
in der neuen Ausgabe. Wort-/Zahl-/Stringnachbarn, Operatornachbarn sowie Zahl/
Punkt bleiben getrennt. Einrückungen, Zeilen, sämtliche Lexeme und Literale
bleiben erhalten; vollständige erneute Tokenisierung muss dieselben Typ-/Text-
Paare ergeben. Die vorhandene ganze unabhängige AST-/Rawliteraloracle bleibt
unverändert. Die bestehende Fitmethode ergänzt eine kleine eigene Gegenprobe
mit Zahl/Punkt, unären Operatoren, benachbarten Strings, Bytes und NULliteral.
Keine Funktions-/Variablenumbenennung, kein entfernter Prüfcode und kein Capwechsel.

Drei Kandidaten/max6, zwei geänderte Nachläufe; Verbrauch UNKNOWN. Erneuter
unabhängiger Delta-PRE und ausdrückliches einmaliges Lauf-GO ausstehend.
Quellenfit und innere Modelle bleiben ungeprüft. Keine alten Routen-/Native-/
DGN-Raw-/SQLläufe. Python-tokenize ist nur Generatorwerkzeug; die fünf Imports
im erzeugten Script und sämtliche Workflowabhängigkeiten bleiben unverändert.

## C4 – begrenzte lokale Alpha-Umbenennung

C3 `6eb4a194a15e42e3e77684eb6a91d9cce250b92d` unabhängig ohne offene Befunde
mit einmaligem Lauf-GO. Neue16 danach Windows3.14.7 in5.353s/Linux3.12.3
in4.763s jeweils16SCRIPT_LIMIT-Fehler vor Modellsemantik. Separates unabhängiges
einmaliges Windows-Diagnose-GO für reine Generierung und Größen aus dem eigenen
abgelehnten Generatorframe: Basis128046, formatiert142978, tokenverdichtet138588,
Überschreitung7516Bytes; Token-/Einrückungs-/Zeilenlexeme bereits133859Bytes.
Keine abgelehnte Quelle ausgeführt oder als erfolgreiche Ausgabe verwendet.
Statische Referenzsuche findet keine entbehrlichen Definitionen im nötigen Umfang.

Unabhängiger C4-Auswahl-PRE erlaubt deshalb ausschließlich nicht eingefangene
lokale Bindungen in Funktionskörpern der neuen endgültigen Ausgabe zu kürzen.
Das ist eine begrenzte AST-Transformation mit Alpha-Äquivalenz. Parameter,
Defaults, Dekoratoren, Annotationen, Funktions-/Klassen-/Attributnamen,
freie/globale/nonlocal Namen und sämtliche Literale bleiben unverändert.
Innere Function/Class/Lambda-Scopes und sämtliche Comprehensions werden beim
jeweiligen Körper nicht betreten; alle dort vorkommenden oder deklarierten Namen
sind für die äußere Umbenennung gesperrt. Das gilt ausdrücklich auch für bloße
Nonlocaldeklarationen und innerhalb von Comprehensions eingefangene Namen.
Funktionen mit Imports, Pattern-Matches, TypeAlias, NamedExpr oder direktem
locals/eval/exec/vars-Aufruf werden vollständig ausgelassen. Nur eigene lokale
Name(Store)- und ExceptHandler-Bindungen ab fünf Zeichen werden konsistent in
Load/Store/Del/Handlernamen ersetzt. Neue gültige kurze Namen kollidieren mit
keinem ursprünglichen Bezeichner des ganzen Scripts. Keine entfernte Operation.

Die unabhängige Oracle leitet pro Funktionsscope eine bijektive Zuordnung aus
beiden ASTs ab, prüft zulässige lokale Bindung, sämtliche Sperren und konsistente
Vorkommen, führt ausschließlich diese Namen zurück und vergleicht danach die
vollständigen ASTs. Sie verwendet weder den produktiven Transformer noch dessen
Auswahl oder Mapping. Eigene kleine Randprobe deckt äußere Bindung, bloßes
Nonlocal, Comprehension, Exceptionhandler und ausgeschlossenen Import ab.
Alle bestehenden PRE-/POSTs halten die tatsächlich transformierten Codeobjekte
einschließlich co_varnames; keine Rebaseline oder neue Ausschlussliste.

Vier Kandidaten/max6, drei geänderte Nachläufe, Verbrauch UNKNOWN. Quellenfit
und sämtliche inneren Modelle weiter offen. Stabiler Source/Test-Delta-PRE und
ausdrückliches einmaliges Lauf-GO für neue16 Windows/Linux ausstehend. Caps,
Profilrawbytes, ältere Quellenrouten und fünf Scriptimporte bleiben unverändert.
Keine operative/nativ wirkende Erweiterung; Gesamtgates bleiben offen.
