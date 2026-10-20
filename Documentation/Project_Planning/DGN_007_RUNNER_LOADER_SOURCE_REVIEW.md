# DGN-007 – vollständige gehaltene Runner-Quellenfolge

Stand: 20. Oktober 2026. Basis `b00418ca74cd6ff4a0d194f8276ca365f9558f56`.
Status `SELECTION_PRE_PENDING`; keine Implementierung oder neue Probe.

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

Parentfactory und eigener Aufruf werden vor Reportsnapshot gehalten. Tatsächlicher
Aufruf ausschließlich beim einmal reservierten Root0→Source6-Import nach den
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
