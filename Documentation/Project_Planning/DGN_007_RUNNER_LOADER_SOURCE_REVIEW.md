# DGN-007 – vollständige gehaltene Runner-Quellenfolge

Stand: 21. Oktober 2026. Basis `b00418ca74cd6ff4a0d194f8276ca365f9558f56`.
Status `C2_DELTA_PRE_PENDING`; noch kein Kandidatenimport oder neue Probe.

## Abschlussbindung und endlicher Umfang

PR273 ist vollständig integriert: neun finale PR-/sieben frische Main-Gates
SUCCESS, neue Parent12 und unveränderte Harness16 ohne SKIP PASS. Unabhängige
Befundschließung, FullTree/Sync und eigene lokale/Remote-Branchabwesenheit
bestätigt. Drei Source/Testkandidaten erfolgreich geschlossen, kein Reset.

Der nächste Funktionsschnitt ergänzt ausschließlich die noch fehlende komplette
Runnerfolge nach [Importprofilvertrag §33.1/33.2](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#331-feste-zuordnung-und-prospektive-importfolge).
Ein Implementierungsowner root, derselbe unabhängige Reviewer, höchstens sechs
stabile Source/Testkandidaten, Checkpoint2, harte Grenze6, höchstens fünf
geänderte Nachläufe. Auswahl-/Source-/Test-/Deltareviews, explizite Lauf-GOs,
Tests, Fit-/Transformationskorrekturen, Koordination, CI, regulärer Merge,
frische Main-Gates, FullTree/Sync und eigene Branchbereinigung zählen gemeinsam.
Verbrauch UNKNOWN. Am Hardstop kein neuer Kandidat, Reset oder umbenannter Scope.
Alte ausgeschöpfte vollständige Matcher-/Generatorversuche bleiben geschlossen.

## Additive Auswahl und feste tatsächliche Reihenfolge

Neue API build_runner_loader_control_bootstrap im eigenen Toolmodul auf dem
vollständigen Eingangsunterbau aus PR269, mit privaten Runnernamen. Proxy- und
Harnessrouten sowie ältere Generatoren unverändert. Vor Reportsnapshot gebundene
ursprüngliche Inputentry/Owner, tatsächlicher EOF-/Payloadhandoff, Kernel, volle
Profilrawbytes und sämtliche ursprünglichen Budgethalter bleiben erhalten.

Nur Worker1/run_dgn007_automated_setup/PRE_IMPORT. SOURCES beginnen0/1/5/3/4/6/7/8
und schließen5/1/4/3/8/7/6/0. Sequenzen/Objektslots1/2/3/4/5/8/9/10; Origins
gleich jeweiligem Sourceindex. Dazwischen codefreie PARENT0/1 mit Sequenzen6/7,
Origins9/10, je BEGIN/COMPLETE vor Source6. Alle20 Records aus tatsächlicher
eigener gehaltenen Invocation und vollständig bestätigtem gemeinsamen Writer.
Vor jedem Compile bestätigter BEGIN, dieselben empfangenen Rawbytes, festes
logisches Origin; Exec exakt gehaltenes Codeobjekt/Namespace, COMPLETE erst
nach Rückkehr und vollen PRE/POSTs. Keine Finder-/Datei-/PYC-Projektauflösung.

Privates Gateway bindet jede Kante an aktive eigene Sourceinvocation, exakten
Namen/level0/Fromlist und Modulnamespace. Die geschlossene Tabelle folgt den
statisch gelesenen tatsächlichen Top-Level-Imports aller acht Sources. Keine
Alternative für unbekannte Namen, Stern-, Getter- oder Submodulfallback. Kanten
vor Wirkungen einmalig reservieren; Sourcecachehits nur bereits vollständig
abgeschlossener eigener Module, danach erneute vollständige Bindung. Typen und
primitive Keys/Argumente vor Fremddispatch. Parentpakete erhalten nur eigene
Childmodule; alle Parent-/Childbindungen beim Unwinding erneut prüfen.

Stdlib wird ausschließlich über den vor Reportsnapshot gehaltenen ursprünglichen
Importer mit vollen PRE/POSTs delegiert; genaue statische Fromlisttabelle je
Caller, kein tatsächlicher Import im eigenen Modellprovider. Importer/OS/Runtime
bleiben Vertrauensannahmen, keine Stdlibsource- oder Importneutralitätsattestation.

## Tatsächliche Parentkomponente und privater Namespace

Die validierte Factory aus PR273 wird als volle unveränderte FunctionDef-AST
in die neue Quelle aufgenommen; keine zusätzlichen Scriptimporte. Ein privater
FunctionType-Aufbau hält denselben ursprünglichen Factorycode und einen eigenen
exakten kleinen Namespace mit ursprünglichen Builtins, ModuleType-/ModuleSpec-/
Mappingproxyklassen und Factoryselbstbindung. Keine weitere Modulregistrierung,
Pythonmember oder erneute Globalsbaseline. Damit bleibt der Parentnamespace
nach Initialisierung unverändert, während legitime spätere Input-/Report-
Initialisierung die separaten Scriptglobals vervollständigt.

Factorycode, privater Namespace, Klassen und ursprüngliche Guard-/Writerzustände
werden vor Reportsnapshot gehalten. Der tatsächliche Kontextdigest steht erst
nach geprüftem Input/EOF fest. Ausschließlich daraus wird beim einmaligen
Factoryaufruf eine neue private Run-Closure erzeugt, nach erneutem Vergleich aller
Originalanker und mit geschlossenen PRE/POSTs. Vor ihrem ersten Dispatch exakten
Funktionstyp, den zuvor gehaltenen verschachtelten Run-Code und denselben privaten
Globalsnamespace prüfen und halten. Ablage nur in schon angelegten privaten
Haltern, keine späte Global-/Closurezellbaseline. Tatsächlicher Run-Aufruf
ausschließlich beim einmal reservierten Root0→Source6-Import nach den
bereits abgeschlossenen Sources1/5/3/4, mit aktivem ursprünglichen Root0-Exec.
Privater exklusiver Parentaufruf umschließt ausschließlich die gehaltene originale
Parententry; tatsächlicher Callbackguard prüft aktive Rootinvocation und alle
Sourcebindungen. Während dieser begrenzten Invocation schließt die Parentkomponente
ihre eigenen noch nicht öffentlich zurückgegebenen Parentobjekte/Slots; keine
pauschale Parentausnahme außerhalb dieses Aufrufs. Writer verwendet denselben
ursprünglichen I/O-Owner und Zähler. Nach erfolgreicher Rückgabe werden exakt die
gehaltenen Parentobjekte zusätzlich in jeden Runnerguard aufgenommen. Sources6/7/8
binden __package__ Tests.Contracts und ihre eigene identische Childverknüpfung.
Keine Parent-Compile-/Execinvocation oder fremde Receipts als Authority.

Gesamtfehler, Reentranz oder Wiederholung sperrt die Folge. Cleanup rückwärts
nur eigene identische Source-/Parentcacheeinträge und eigene identische Links;
fremde Ersetzungen und __main__ erhalten. Kein privater Exceptiontext oder
Teil-Erfolg. Bestätigte Recordbytes bleiben auch nach fehlgeschlagenem POST
auf dem Draht; daraus entsteht kein erfolgreicher Record-/Sessionclaim.

## Quellenfit und unabhängige Oracles

Unverändert fünf Scriptimporte, vollständiger tatsächlicher Profilraw und
131072-Byte-Cap. Die bereits bewiesenen Tokenabstands-/lokalen Alpha-Pässe sind
zulässig; zusätzlich nur in dieser neuen Route eine kollisionsfreie konsistente
Kürzung privater globaler FunctionDefs samt sämtlichen direkten Name(Load)-
Referenzen. Auswahl deterministisch aus den vorhandenen privaten internen
Helperdefinitionen; externe Fixture-/Entry-/Initialisierungsnamen bleiben erhalten.
Jeder gewählte Name muss eine einzige Top-Level-Definition besitzen, ausschließlich
Loadreferenzen und keinerlei Bindungs-/Parameter-/Global-/Nonlocal-/Attribut-/
Stringreflexion. Byte-Literale bleiben unangetastet. Neue Namen disjunkt zu allen
ursprünglichen bindenden/freien Namen und sämtlichen Attribut-/Stringreferenzen.
Keine Aliaszellen oder zusätzlichen Namespaceeinträge. Nicht geeignete Definitionen
werden nicht gekürzt; keine Änderung an Funktionskörpern oder Operationen.

Der ganze Parentfactory-AST einschließlich sämtlicher verschachtelter Funktionen
bleibt von globaler und lokaler Kürzung ausgenommen; unveränderte Übernahme separat
beweisen. Codeidentität bezeichnet das vorab gehaltene eingebettete Codeobjekt,
keine Identität mit dem separat kompilierten Standalone-Modul.

Die getrennte Oracle rekonstruiert die erwartete ganze AST samt genau beschriebenem
Runner-/Parentadapter und beweist eine bijektive globale Def-/Loadzuordnung,
verbietet jede weitere Bindungs-/Reflexionsänderung, führt diese zurück und danach
die bestehenden konservativen lokalen Umbenennungen. Vollständige AST-/Literal-/
Operationsgleichheit und tatsächliche ursprüngliche Code-/Globals-/Closurepins
bleiben Pflicht. Keine nachträgliche Baseline. Quellenfit erst nach Beweis unter
tatsächlichem vollständigem CRLF- und separat LF-Profilraw; keine Capanhebung.

## Testauswahl und Grenzen

Auswahl-PRE vor Implementierung; stabiler Source/Test-PRE und ausdrückliches
gestuftes einmaliges Lauf-GO. Zuerst nur Fit/Ganz-AST unter Windows3.14.7 und
Linux3.12.3 -I -S -B. Erst bei beidseitigem PASS eigene sichere synthetische acht
Bodies mit tatsächlichen geschlossenen Importkanten. Unabhängige20-Recordoracle,
acht Compile-/Execidentitäten, verschachtelte Rückkehr, Parentregistrierung und
Cachehits. Negative Rollen/Source-/Fromlist-/Typgrenzen, späte Source-/Parent-/
Childslots, Provider-/Spec-/Class-/Origin-/Locationsdrift, Fehler, Partialwrites,
Budgets, Reentranz/Retry und Identitätscleanup müssen tatsächlich erreicht sein.

Neue enge CI hält alle direkten/transitiven Generator-/Profil-/Parent-/Fixture-
Abhängigkeiten. Alte Consumer nur bei Betroffenheit; unveränderte grüne lokale
Suites nicht wiederholen. Ein Owner/ein Reviewer, private begrenzte Logs,
Privacy aller geänderten Dateien vor jedem Commit und einmaliger zentraler
Vollscan. Reguläre aktuelle Head-/Base-/Main-Gates und kompletter Abschluss.

Keine tatsächlichen DGN-Quellen, Worker, neuen Imports, nativen Prozesse, SQL
oder Ressourcenwirkungen. Vollständiger Runtime-/Usedbytes-/Trust-/Methoden-/
SESSION_END-/Gesamtclaim bleibt offen. Der Schnitt belegt zunächst ausschließlich
Quellenfit und eigene synthetische Runner-/Parentmodelle, keine operative Admission.

## Unabhängige Auswahlbindung

Plan89c62c75dfeab74191960f1727f5a34f38d1d111 unabhängig freigegeben mit den
vorstehend eingearbeiteten verbindlichen Präzisierungen: Digest erst nach
tatsächlichem geprüftem Input, ursprüngliche Factory-/Provideranker davor halten;
neu erzeugte Run-Closure vor Dispatch an ursprünglichen eingebetteten Code und
privaten Namespace binden, vorhandene private Halter; kompletter Parent-AST
von sämtlichen Alpha-Pässen ausnehmen. Temporäre Parentfreigabe ausschließlich
in der tatsächlichen originalen Invocation, alle Source-Abwesenheitsregeln
weiter aktiv, danach volle Parent-/Childbindung. Kein Teilaufnahme- oder Cleanup-
Gesamtclaim bei Fehler. Kein weiterer Auswahlreview nötig, noch kein Lauf-GO.

## C1 – konkrete Quelle und Testauswahl

C1 ergänzt die additive Runnerquelle und16 eigene Methoden. Sechs vorhandene
Proxyhelfer werden über den bewiesenen Harnessadapter übernommen, eigene private
Runnernamen und vollständiger Parentguard ergänzt. Tatsächliche Compilerinvocation
bleibt unverändert aus dem tatsächlichen privaten Sourceframe. Geschlossene16
Projektkanten folgen den statisch gelesenen tatsächlichen Top-Level-Imports;
Stdlibtabelle separat pro Source. Keine Änderungen an bestehenden Generatoren,
Parentfactory oder Fixturedateien.

Originale Parentfactory-AST wird separat aus ihren vollständigen eigenen
Dateibytes gewählt und nach beiden Alpha-Pässen unverändert eingefügt. Alle
ursprünglichen Parentbezeichner bleiben bei globaler Kollisionsprüfung belegt.
Private Klasse-/Builtin-/Factoryselbstbindungen vor Reportsnapshot, tatsächlicher
K-Digest erst nach EOF; Factory-/Run-Code und eigener Namespace bleiben getrennt
vom Standalone-Modulcode. Neu erzeugte Run-Closure nur in vorab angelegtem
privatem Halter. Ausschließlich aktive originale Root0→Source6-Parentinvocation
gestattet noch nicht zurückgegebene Parentobjekte; Source-Abwesenheitsregeln
bleiben dabei aktiv und zurückgegebene Parent-/Childobjekte danach voll geprüft.

Globaler Alpha-Pass wählt nur interne Helperpräfixe und geschlossene Def-/Load-
Formen, erhält ausdrücklich externe Entry-/Fixture-/Kernel-/Sealnamen. Ganze
ursprüngliche Identifikator-/Attribut-/Stringmengen einschließlich Parentfactory
sperren Kollisionen; Parentreferenzen sperren eine solche Helperkürzung vollständig.
Keine Namen-/Aliasliste wird als Runtimebaseline eingeführt. Unabhängige Oracle
rekonstruiert den ganzen Basis-/Helper-/Runner-/Parent-AST getrennt, beweist jede
globale Umbenennung, führt diese und lokale Alpha-Zuordnungen zurück und vergleicht
alles. Voller unveränderter Parent-AST wird zusätzlich exakt verglichen.

Nach Source/Test-PRE ausschließlich Fitmethode Windows3.14.7/Linux3.12.3 mit
vollständigem CRLF-/LF-Raw. Erst bei beidseitigem PASS die übrigen15 Methoden
einmal je Plattform: volle20-Recordfolge, acht Raw-/Code-/Namespaceidentitäten,
Codefreie Parents/Childlinks, originaler Factory-/Digesthandoff, geschlossene
Kanten und Delegation, Rollen/EOF, fremde frühe/späte Slots, originale Parent-
Factory-/Namespace-/Callback-/Run-Codepins, Parent-/Childdrift, Compile-/Execfehler,
ursprüngliche Provider, Teilwrites/Budgethalter, erreichte Fremdtypen, Reentranz/
Retry, Cacheersatz und fehlende Attribute ohne Getterfallback.

Ein Source/Testkandidat/max6, keine Nachläufe, Verbrauch UNKNOWN. Nur Text-AST-
Syntaxprüfung vor Review; keine Generierung, Candidateimporte oder Modelle.
Neue CI mit allen tatsächlichen direkten/transitiven Abhängigkeiten; zehn Minuten
äußerer Jobbound für die ausführliche synthetische acht-Source-Suite, kein geänderter
nativer20-s- oder anderer Laufzeitclaim. Keine unveränderten alten lokalen Suites,
keine doppelten Privacyvollscans, begrenzte private Logs, ein Owner/ein Reviewer.
Unabhängiger Source/Test-PRE und ausdrücklich gestuftes einmaliges Lauf-GO offen.

## C2 und Checkpoint2

C1 0bc7d1347597c325269d982d0a402239d6b9d39f unabhängig mit vier Befunden
ohne Lauf-GO. Ein P2: neu erzeugte Parent-Closurehelfer/Zellen nicht gebunden.
Drei P3: unsortierte positive Ankeroracle, Rootpräcondition erst nach Factory-
dispatch und falscher nicht ausgeführter kanonischer Source2-Member. Übriger
Quellen-/Harnessumfang geprüft; keine Kandidatenimporte oder Ausführung.

C2 nimmt ausschließlich die tatsächlich aus ursprünglichem eingebettetem
Factorycode erzeugte eigene private Helferkette vor ihrem ersten Dispatch auf.
Vor Reportsnapshot begrenzte ursprüngliche Codekonstanten (max64, je max256
Konstanten); nach ursprünglichem Factorycall höchstens16 neu erzeugte eigene
Funktionen, je höchstens32 Defaults/Kwdefaults/Closurezellen. Worklisten vor
Erweiterung begrenzen und nach Identität deduplizieren. Nur ursprünglicher
privater Namespace und ursprüngliche verschachtelte Codeobjekte zulässig.
Ursprüngliche Factory/Guard/Writer werden nicht spät neu gebaselined; ihre
bereits gehaltenen Zustände bleiben maßgeblich. Neue tatsächliche Invocation-
Helfer halten Funktions-/Code-/Globals-/Defaults-/Kwdefaults-/Closurezellwerte
einmal im vorhandenen privaten Halter. Alle späteren Guards vergleichen diese
dominant, auch nach Fehler; keine erneute Aufnahme einer mutierten Kette.

Gegenproben im vorhandenen Run-Code-Test tauschen nach tatsächlichem erstem
Parent-BEGIN-Versuch die close-Zelle beziehungsweise den Code desselben
Helferobjekts aus; Erreichtmarker, fünf Compileinvocations und Ablehnung vor
Source6 werden geprüft. Originale komplette Parent-AST bleibt unverändert.

Volle Root0-/bereits abgeschlossene1/5/3/4-Präcondition jetzt vor Factoryaufruf
und nochmals vor Entrydispatch. Ein temporärer rein prozesseigener Python-
Profilecallback beobachtet ausschließlich Identitäten der zwei gehaltenen
Codeobjekte: positiver Fall genau Factory/Run; vorgezogener Source6-Import
erreicht tatsächlichen Source0-Exec, aber keine dieser beiden Calls. Vorherigen
Profiler im finally exakt wiederherstellen; keine Runtime-/Auditfreigabe daraus.
Positive Namespaceoracle sortiert primitive Keys und prüft Wertidentitäten.
Source2-Member zu Tests/Runtime/docker_sqlcmd_proxy.py korrigiert.

Weiterhin16 Methoden, zwei Source/Testkandidaten/max6, ein Nachlauf, Verbrauch
UNKNOWN. Checkpoint2; unabhängiger Delta-PRE hat die vier Befunde geschlossen
und das gestufte einmalige Fit-vor-Modell-GO für
6a66a8661e7a9bf8b6332519104f3530ba52b421 erteilt. Harte Grenze6 unverändert.

## C2-Fitbefund und Auswahl der C3-Korrektur vom 21. Oktober 2026

Einmalige Fitprobe Windows1/2,939s und Linux1/4,136s jeweils SCRIPT_LIMIT.
Die übrigen15 Methoden wurden nicht gestartet. Eine separat unabhängig
freigegebene einmalige reine Windows-Generatordiagnose hat ausschließlich
eigene verworfene Generatorframes ausgewertet: tatsächlicher Profilraw44542,
Basisquelle128046, neue Quelle143162, Exzess12090 Bytes. Keine verworfene
Quelle verwendet, kompiliert oder ausgeführt; keine zusätzlichen Modelle.
Tokenaggregate: STRING67288 (davon Raw-repr46477), NAME49534. Eine weitere
gewöhnliche Helperkürzung allein reicht voraussichtlich nicht aus. Der
Receiver ohne statische Namensreferenz ist über Stringdispatch tatsächlich
gebunden und bleibt erhalten. Keine vermeintliche Deadcodeentfernung.

Zur unabhängigen Auswahl steht eine ausschließlich reversible Alpha-/Literal-
Kürzung innerhalb derselben Welle, ohne neue Runtime-Datenslots. Der vorhandene
globale Def-/Loadpass darf zusätzlich interne _rl_-/ _worker_report_-Helper
und die genau bezeichneten _require/_dictionary erfassen; sämtliche bisherigen
Schnittstellen-, Binding-, Attribut-, Keyword- und Reflexionssperren bleiben.

Zusätzlich eine uniforme bijektive Schreibweisenmap für lokale Name-/Argument-/
ExceptHandler-/Nonlocalfelder über alle Scopes außerhalb der vollständig
unveränderten Parentfactory. Nur Schreibweisen ab vier Zeichen. Globale
Ursprünge/Modulbindungen, Funktions-/Klassennamen, Importalias-/Pattern-/
TypeAliasfelder, Attribute, Keywordparameter und sämtliche in Stringliteralen
referenzierten Schreibweisen bleiben gesperrt. Bei dynamischer Namensreflexion
(locals/vars/eval/exec) sämtliche betroffenen Identifier ausschließen.
Neue Ziele müssen gegen alle ursprünglichen Identifier, Attribute, Keywords
und Strings einschließlich Parent disjunkt sein. Keine partiellen gleichnamigen
Scopeänderungen: eine uniforme Map und vollständige inverse ASToracle müssen
Capture, Shadowing und Closurebindungen erhalten. Externe Schnittstellen und
ursprüngliche gehaltene Objekt-/Code-/Globals-/Closurezustände bleiben gleich.

Optional rein lexikalische Darstellung des einen vollständigen Raw-Bytesliterals:
kürzeste zulässige repr-/Triplequoteform, tatsächliche LF erlaubt, CR immer
escaped, ebenso Backslash, Delimiter und Nicht-ASCIIbytes. Nach Einrückung und
vor Tokengap-Kürzung einsetzen; einzelner gleicher ast.Constant(bytes) und
vollständige ASTgleichheit sind Pflicht. Kein encode/decode, keine Kompression,
kein zusätzlicher Runtimecall. Rawbytes, Parent-AST, fünf Importe und131072Cap
bleiben unverändert. Grundlagen: [Python-Bytesliterale](https://docs.python.org/3.12/reference/lexical_analysis.html#string-and-bytes-literals).

Getrennte Testoracle darf weder die Produktmaps noch deren Auswahlhelfer
aufrufen. Maps aus erwarteter/tatsächlicher Struktur ableiten, alle Sperren
separat beweisen, exakt zurückführen und ganzen AST vergleichen. Neue enge
Gegenproben müssen Keywords, reflektierte Namen, Closures, Shadowing und
Comprehensions sowie CRLF/LF und Literal-Escapes erfassen. Vor Umsetzung
unabhängige Auswahlfreigabe; danach stabiler Source/Test-PRE mit ausdrücklichem
Lauf-GO. Weiter zuerst Fit Windows/Linux je einmal, erst beide PASS erlauben
die übrigen15. Zwei/max6 bisherige Kandidaten, ein Nachlauf, Verbrauch UNKNOWN;
keine Budgeterneuerung und keine unveränderten Testwiederholungen.
