# DGN-007 – gemeinsamer Kontrollanker für Sources und Parents

Stand: 21. Oktober 2026. Basis f30aebce18ec2902171210bdcc7f222eaa12d405.
Status DESIGN_PRE_PENDING; ausschließlich Architekturplan, keine Implementierung.

## Anlass, Abschluss und gemeinsamer Rahmen

[PR274](https://github.com/gecompat/SQL_PerformanceSchulung/pull/274) ist regulär
integriert: acht finale Head-/sieben Base-/sechs frische Main-Gates SUCCESS,
unabhängiger Abschlussreview ohne offene Befunde, vollständiger Head-/Merge-
Baumvergleich, sauberes synchronisiertes Main und eigene lokale/Remote-
Branchabwesenheit belegt. [Historische Quellenfit-Diagnose](DGN_007_RUNNER_LOADER_SOURCE_REVIEW.md)
ist sachlich verworfen; keine Runnerimplementierung wurde aufgenommen.

Der kontinuierliche Auftrag umfasst die Bearbeitung dieses Architekturblockers.
Ein Owner root und derselbe unabhängige Reviewer; genau ein konkreter Entwurf
und höchstens eine geänderte Entwurfsnacharbeit einschließlich Review,
Koordination, lokaler Dokumentationsprüfung und regulärem Git-/CI-Abschluss.
Quellen-/Versuchsverbrauch UNKNOWN. Der gemeinsame ursprüngliche Quellenrahmen
bleibt bei fünf von sechs Kandidaten und vier geänderten Quellen-/Testnachläufen.
Dieser Plan setzt ihn nicht zurück. Ein C6-Kandidat, Generatorlauf, Compile/Exec,
Modelltest oder Native-/SQL-Lauf ist hierdurch nicht freigegeben. Vor einem
solchen Schritt braucht es unabhängig bestätigte tragfähige Auswahl, stabilen
Source/Test-PRE und ausdrückliches einmaliges Lauf-GO. Bei fehlender Auswahl
bleibt der Architekturblocker offen; kein neuer Name schafft einen neuen Versuch.

## Geprüfte Ausgangslage

Der letzte zulässige Größenbefund C4 beträgt140097Bytes, also9025 über dem
unveränderten131072-Byte-Scriptlimit. Seine neuen lokalen Namenskürzungen und
Raw-Literalform sparten zusammen nur3065Bytes gegenüber C2. Reine Fehlerlabel-
Aliase und zusätzliche sichere Tokenabstände boten zusammen höchstens4443Bytes.
Der Parent-SESSION_END-Matcher steht bereits außerhalb der Workerbasis; dessen
Auslassung kann keine weitere Einsparung liefern. Keine Wiederholung zur Bestätigung.

Der verworfene Runner hat die komplette Standalone-Parentfactory zusätzlich zu
seinem eigenen Quellenkontrollanker eingebettet. Weil deren private Run-Closure
erst nach EOF erzeugt wurde, brauchte er zusätzliche ursprüngliche Factorycode-/
Namespace-/Nachkommenbindungen, eine begrenzte spät erzeugte Helfergraphaufnahme
und einen weiteren Root-Parentbinder. Die tatsächliche Größe einer neuen
Komposition ist unbekannt; daraus folgt keine bereits belegte Einsparung.

## Zur Auswahl: ein eigener gemeinsamer Rootanker

Der neue Entwurf führt acht Sources und zwei codefreie Parents im selben
privaten Runneranker. Die vorhandene Standalone-Parentfactory aus PR273 bleibt
unverändert erhalten. Sie dient als fachliche Referenz für Parentform und
Negativfälle, wird in dieser alternativen Workerroute jedoch nicht eingebettet
oder aufgerufen. Damit entfällt der Anspruch, dass diese Route denselben
Standalone-Factorycode tatsächlich verwendet. Ihre Abnahme beweist die neue
Route nicht; die neue Komposition muss eigenständig geprüft werden.

Alle Rootfunktionen und tatsächlich verwendeten Parenthelfer entstehen vor dem
Reportsnapshot. Es gibt keine späte Parentfactory und keinen erst nach EOF
entstehenden Funktionsgraphen. Der tatsächliche K-Digest wird ausschließlich
aus dem ursprünglichen geprüften Input nach tatsächlichem EOF in einem vorher
angelegten privaten Einmalhalter aufgenommen. Keine neue Funktions-/Code-/
Globals-/Closurebaseline aus späteren Werten. Root-Inputentry, EOFhandoff,
Kernel, ursprüngliche Provider-/Klassen-/Spec-/Cache-/Compiler-/Execanker und
Budgethalter bleiben vor diesem Übergang ursprünglich gehalten.
Nicht als globale Scriptfunktion erfasste Closurehelfer erhalten ebenfalls vor
Reportsnapshot vollständige ursprüngliche Funktions-/Code-/Globals-/Defaults-/
Kwdefaults-/Closurezellbindungen. Frühe Erzeugung allein ist kein Bindungsbeweis.

Ein schmaler privater Parentpfad erzeugt ausschließlich Tests und Tests.Contracts
aus den bereits gehaltenen ursprünglichen ModuleType-/ModuleSpec-Klassen und
eigenen leeren Locationslisten. Der bestehende dominante Rootguard prüft vor
und nach jedem tatsächlich bestätigten Writer-/Compiler-/Exec-/Importercallback
dieselben ursprünglichen Anker sowie alle bereits erzeugten Source- und
Parentobjekte. Die Parentprüfung ist rein und ruft keinen äußeren Guard zurück;
dadurch darf keine Guardrekursion entstehen. Keine zweite freie Klassen-, Cache-
oder Writerauswahl innerhalb des Parentpfads.

Parentzustand ist vorab endlich vorgegeben: nicht begonnen, eigene erste
Invocation aktiv, vollständig registriert oder sticky fehlgeschlagen. Der
erreichbare nächste Schritt und alle noch freien Namen/Childslots werden vor
Effekten geprüft. Teilweise erzeugte eigene Objekte sind ab Veröffentlichung
gehalten und werden bereits innerhalb der aktiven Invocation geprüft, bevor
eine neue fremde Wirkung möglich ist. Kein pauschales Aussetzen der Parent-
oder Sourceprüfungen während dieser Invocation.
Der Parentpfad ist ausschließlich über die tatsächliche ursprüngliche Root0-
Execinvocation und deren geschlossene Importkante0→6 erreichbar, nachdem
Sources1/5/3/4 vollständig abgeschlossen sind. Diese Präcondition dominiert
bereits den ersten Parent-/Writeraufruf. Keine Caller-Tupel oder bloßen
Statuswerte als Ersatz für tatsächlichen Stack und ursprünglichen EOFhandoff.
Parentobjekte werden vor Veröffentlichung in eigenen Haltern aufgenommen,
vor BEGIN veröffentlicht und nach vollständig bestätigtem BEGIN erneut geprüft;
Parent1 wird vor seinem BEGIN nur am eigenen vollständig geprüften Parent0
verknüpft. Schrittflags haben exakte primitive Typen und endliche Werte.

## Erhaltene Formen und tatsächliche Wirkungen

Die vollständige Reihenfolge bleibt unverändert: Sources BEGIN0/1/5,
COMPLETE5/1, BEGIN3/4, COMPLETE4/3; Parent0 BEGIN/COMPLETE mit Sequenz6,
Parent1 BEGIN/COMPLETE mit Sequenz7; Sources BEGIN6/7/8, COMPLETE8/7/6/0.
Die vollständigen20 Records bleiben durch tatsächlichen Input-/EOF-/K-Digest,
bestätigten ursprünglichen Writer und dieselben I/O-/Bytezähler gebunden.
Parentrecords enthalten null statt Rawhash, Source-/Parentorigin und -seq
bleiben getrennt. Kein Parentcompile oder -exec und keine Methodeninvocation.

Parents haben exakt eigene Module-/Specobjekte, origin/loader None, dieselbe
private leere Liste in __path__/submodule_search_locations, keine __file__/
__cached__ und _set_fileattr False. Tests.Contracts verknüpft nur den eigenen
Tests-Parent mit dem eigenen Kind. Source6/7/8 verknüpfen nur ihre jeweils
ursprünglich gehaltenen Module im eigenen Tests.Contracts. Fremde frühe/späte
Cache-/Parent-/Childslots bleiben erhalten; spätes Ersetzen wird dominant vor
weiterem Record/Sourceeffekt abgelehnt. Bei Fehler nur eigene identische Slots/
Links rückwärts entfernen; kein Cleanup-Gesamtclaim bei ungültigem Fremdcache.

Acht tatsächliche Originalraw-/Compile-/Code-/Exec-/Namespacebindungen,
geschlossene tatsächliche Projekt-/Stdlibimportkanten, fremde Mainabsenz und
alle bisherigen Input-/Provider-/Grenz-/Reentranz-/Retryanforderungen bleiben.
Voller Profilraw einschließlich CRLF/LF, fünf direkte Scriptimporte,131072Cap,
20-s-/10-s-/I/O-/Bytegrenzen und sämtliche false-Claims werden nicht geändert.
Keine Quellenkompression mit zusätzlichem Runtimecompile: deren Behandlung
der vollständig expandierten Quelle wäre eine andere Vertragsentscheidung.

## Noch zu beweisender Quellen- und Testplan

Vor Sourceauswahl benötigt der Entwurf eine unabhängige vollständige Prüfung
der Zustandsübergänge und dominanten PRE/POST-/Fehlerpfade. Eine kürzere Quelle
darf keine doppelte Sicherheitsprüfung bloß unbewiesen als überflüssig erklären.
Jeder ursprüngliche Pin muss genau einem tatsächlich dominanten Prüfort
zugeordnet sein. Erst dann ist ein konkreter C6-Source/Testkandidat auswählbar.
Kein behaupteter Fit aus formatierten Templategrößen oder neuer Benennung.

Eine künftige unabhängige Ganz-ASToracle müsste den neuen Parentadapter selbst
aus dem ausgewählten festen Template rekonstruieren; alle übrigen Source-/
Inputknoten bleiben erhalten. Keine allgemeine Deadcode-/Präfixentfernung.
Zusätzliche Alpha-Kürzungen dürfen externe Fixture-/Callback-/Closurenamen
nicht verändern; der tatsächliche Inputfixturezugriff auf co_freevars['owner']
muss erhalten bleiben. Die bestehenden konservativen lokalen Alpha-/Literal-
Nachweise allein ersetzen keine neue Kompositions- oder Runtimeprüfung.

Test-GO bleibt gestuft: zuerst tatsächlicher voller CRLF-/LF-Rawfit und
unabhängiger Ganz-ASTnachweis Windows/Linux; erst beidseitiges vollständiges
PASS erlaubt eigene sichere synthetische acht-Source-/zwei-Parentmodelle.
Positive ganze20-Recordfolge, echte Code-/Raw-/Namespaceidentitäten und spätes
Source8-Paket; negative ursprüngliche Provider-/Code-/Klassendrift, Parent-
Spec/Locations/Childdrift an jeder aktiven Veröffentlichung, Fremdtypen ohne
Getter/Equalityeffekt, bestätigte Teilwrites, Limits, Fehler, Reentranz/Retry
und identitätsbezogener Cleanup müssen tatsächlich erreicht sein. Bestehende
unveränderte Suiten werden lokal nicht wiederholt. Neue enge CI erst mit
stabilem tatsächlichem Source/Testkandidaten und allen Abhängigkeiten.

## Claim- und Entscheidungsgrenze

Dieser Entwurf ist ausschließlich ein überprüfbarer Architekturvorschlag.
Keine Größen-, Funktions-, Runtime-/Trust-/Usedbytes-/Methoden-/SESSION_END-
oder SQLabnahme. Tatsächliche DGN-Quellen, Worker, EOF/Exit/Cleanup im nativen
Lauf und übrige reale Gates bleiben offen. Der nächste Schritt ist genau der
unabhängige Design-PRE, keine Probe. Der verbleibende C6-Versuch wird ohne
konkretes Folge-GO nicht verbraucht.
