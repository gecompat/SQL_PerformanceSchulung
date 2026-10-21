# DGN-007 – gemeinsamer Kontrollanker für Sources und Parents

Stand: 21. Oktober 2026. Basis f30aebce18ec2902171210bdcc7f222eaa12d405.
Status DESIGNED; ausschließlich Architekturplan, keine Implementierung.

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
unveränderten131072-Byte-Scriptlimit. Seine globalen/lokalen Alpha- und
Raw-Literaländerungen sparten zusammen nur3065Bytes gegenüber C2. Reine Fehlerlabel-
Aliase und zusätzliche sichere Tokenabstände boten zusammen höchstens4443Bytes.
Der Parent-SESSION_END-Matcher steht bereits außerhalb der Workerbasis; dessen
Auslassung kann keine weitere Einsparung liefern. Keine Wiederholung zur Bestätigung.

Der verworfene Runner hat die komplette Standalone-Parentfactory zusätzlich zu
seinem eigenen Quellenkontrollanker eingebettet. Weil deren private Run-Closure
erst nach EOF (End of File; Ende eines Eingabestroms) erzeugt wurde, brauchte er zusätzliche ursprüngliche Factorycode-/
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
bleiben getrennt. Kein Parentcompile oder -exec und keine DGN-Methodenabnahme.
Die vertrauensabhängigen Providerkonstruktoren bleiben tatsächliche Aufrufe;
ihre Voraussetzungen und PRE/POST-Bindungen gelten weiterhin.

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

Die am Dokumentende konkretisierten Pin-/Zustands-/Dominanzregeln sind bereits
verbindlicher Entwurfsteil. Ein Source/Test-PRE muss ihre vollständige Umsetzung
nachweisen. Eine kürzere Quelle darf keine Prüfung unbewiesen als überflüssig
erklären. Kein behaupteter Fit aus Templategrößen oder neuer Benennung.

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
unveränderte Suiten werden lokal nicht wiederholt. Neue enge CI (Continuous Integration; automatisierte Integrationsprüfungen) erst mit
stabilem tatsächlichem Source/Testkandidaten und allen Abhängigkeiten.

## Claim- und Entscheidungsgrenze

Dieser Entwurf ist ausschließlich ein überprüfbarer Architekturvorschlag.
Keine Größen-, Funktions-, Runtime-/Trust-/Usedbytes-/Methoden-/SESSION_END-
oder SQLabnahme. Tatsächliche DGN-Quellen, Worker, EOF/Exit/Cleanup im nativen
Lauf und übrige reale Gates bleiben offen. Der nächste Schritt ist genau der
unabhängige Design-PRE, keine Probe. Der verbleibende C6-Versuch wird ohne
konkretes Folge-GO nicht verbraucht.

## Konkrete Pinbindung und dominante Prüforte

Die folgenden Prüforte bezeichnen verbindliche Rollen im künftigen Code,
keine bereits implementierten Funktionen. Exakte primitive Typen, bool ist
kein int. Frühe Erzeugung allein beweist keine Bindung eines Closurehelfers.

| Ursprünglich gehaltener Pin | Dominante Prüfung vor Dispatch und nach Rückkehr |
| --- | --- |
| Rootentry/Rootguard und sämtliche tatsächlich verwendeten Closurehelfer: Funktion, Code, Globals, Defaults, vollständige primitive Kwdefaults, Closuretuple und Zellinhaltsidentitäten | Vor Reportsnapshot einmal halten. Gehaltener Caller prüft Entry vor Dispatch; aktive ursprüngliche Entry prüft ursprüngliche Guard-/Helferbindungen vor jedem Folgedispatch. Jeder Guard startet mit geschlossenem Bootstrap vor weiterer Scripthelperauswahl. Keine bloße nachträgliche Prüfung. |
| Guardbootstrap: ursprüngliche type/len, erforderliche dict-/tuple-/str-Primitiven, Funktions-/Code-/Celltypen und Builtinsdict samt Einträgen | Privat gehaltene primitive Referenzen verwenden. Erst tatsächlichen Dict-/Keytyp und endliche Schlüsselmenge prüfen, danach Lookups. Keine ForeignKey-Hash/Equality oder Fremdgetter. Builtins vor originalem Kernelcheck prüfen; keine primitive Auswahl aus spätem Namespace. |
| Ursprünglicher Inputowner, Kernel-Funktion/Code/Globals/Defaults/Closure, tatsächliche Reportentry und Scriptsnapshot | Bootstrap prüft volle Kernelbindung vor Dispatch; derselbe originale Kernel prüft Originalsnapshot/Provider. Danach ursprüngliche Inputentry/Owner/Reporthandshake vor und nach jedem äußeren Aufruf. Keine späte Kernel-/Reportauswahl. |
| Compiler, Exec, Importer, tatsächlicher Writer und ursprünglicher I/O-Owner | Ursprüngliche Funktionszustände vor Reportsnapshot; Rootguard vor jedem Call und finally-POST auch bei Exception oder ungültiger Rückgabe. Writer ausschließlich ursprünglicher durch Input bestätigter Kanal, gleiche Budgethalter. |
| ModuleType/ModuleSpec, MRO/Bases, Klassendicts/Deskriptoren, Methoden-/Closurezustände und Encoder-/Provideranker | Nach originalem Kernelcheck ursprüngliche Klassen-/Providerpins vor Konstruktor und Feldzugriff prüfen; POST prüft sie vor Zugriff auf Rückgabeobjekte. Erst genaue Typen/gebundene Deskriptoren, danach eigene Namespaces; keine Getterauswahl aus mutierter Klasse. |
| ActualInput-/EOFpaket, ursprüngliche private Handoffs, tatsächlicher K-Digest | Handoff-Funktion/Code vor Reportsnapshot halten. Einmaliges Paket ausschließlich aus tatsächlichem vollständigem Input/EOF; Digest erst danach im vorherigen Halter. Rootguard vergleicht tatsächlichen Owner-/Paket-/Digestszustand vor Parent-/Sourceinvocation; Callerreceipts/Statuswerte sind keine Authority. |
| Tatsächlicher Source-/Importstack und Parentpräcondition | Vor erster Konstruktion und jedem weiteren Record/Effekt: ursprüngliche Root0-Exec aktiv, tatsächliche Kante0→6, Sources1/5/3/4 vollständig und zulässiger nächster Parentzustand. Reentranz eröffnet keinen zweiten Pfad. |
| Zurückgegebene Module/Specs, eigene Locations-/Namespacedicts, Cache-/Parent-/Childlinks | Rückgabe sofort vor nächstem äußeren Call aufnehmen, auch ohne Partnerobjekt. Phasengenauer Parentcheck vor/nach Folgeschritt und in allen anderen Sourceguards. Freie Slots bleiben frei; veröffentlichte Slots halten eigene ursprüngliche Identitäten. |
| Ursprüngliche I/O-/Inbytes-/Outbytes-/Offset-/Source-/Parentzähler und Einmal-/Fehlerflags | Root-/Inputguard vor Budgetreservierung und nach äußeren Calls; bestehende1088/4096-/Bytegrenzen und endliche Schritt-/Offsetformen. Nur bestätigte Writes verbrauchen Offset, keine Ersatzhalter oder Wiederholung nach Fehler. |

Die reine Parentprüfung ruft weder Rootguard noch Provider/Writer zurück.
Auch sie und jeder verwendete private Closurehelfer werden vor Dispatch an
ihre ursprünglichen Zustände gebunden geprüft. Unveränderte Halteridentität
attestiert nicht deren veränderliche Inhalte.

## Endliche Parent-Unterzustände

Jeder Parent besitzt vorab eigene Halter für Modul, Spec, beide Namespaces und
Locations sowie genaue Schritt-/Recordoffset-/Fehlerflags. Ausschließlich diese
Übergänge sind in fester Parent0-/Parent1-Reihenfolge zulässig; jeder Fehler
führt nach FAILED und bleibt dort.

| Zustand | Zulässiger Inhalt und nächster Schritt |
| --- | --- |
| WAIT | Keine Objekte, eigene Cache-/Childslots frei. Tatsächliche Rootpräcondition prüfen und einzigen Konstruktionsversuch reservieren. |
| MODULE_CALL | Ursprünglicher ModuleType-Konstruktor läuft, kein Specaufruf oder veröffentlichter Slot. |
| MODULE_HELD | Modulrückgabe sofort halten, Spec ausstehend. POST zuerst Klassen, dann tatsächlichen Modul-/Namespacezustand prüfen; erst danach Specversuch reservieren. |
| SPEC_CALL | Spec-Konstruktor läuft; ursprüngliches Modul bleibt in zulässigem unveröffentlichtem Zustand gebunden. |
| BOTH_HELD | Specrückgabe sofort halten. POST zuerst Klassen, dann beide Objekte; Locations nur aus eigenem geprüften Spec oder eigener vorheriger Liste aufnehmen. Noch kein Cache-/Childlink. |
| PREPARED | Vollständige endgültige Metadaten geprüft, Locations genau eigene leere Liste; Cache-/Childslots frei. |
| PUBLISHED | Eigenes Modul im zuvor freien eigenen Cache-Namen, weiterhin vollständig gebunden. |
| LINKED | Parent1 nur am eigenen bereits vollständig registrierten Parent0.Contracts verknüpft. Parent0 hat keinen Vorgängerlink. Alle weiteren Childslots phasengenau frei/eigen. |
| BEGIN_PENDING / BEGIN_CALL / BEGIN_PARTIAL / BEGIN_DONE | Fester kanonischer BEGIN, Offset0 / laufender Write / bestätigter Offset zwischen0 und Länge / genau volle Länge. POST vor Übernahme der Rückgabe. Kein COMPLETE vor BEGIN_DONE. |
| COMPLETE_PENDING / COMPLETE_CALL / COMPLETE_PARTIAL / COMPLETE_DONE | Derselbe tatsächliche Writer, fester COMPLETE und bestätigte Offsets. Kein weiterer Parent/Source vor vollständig bestätigtem COMPLETE. |
| REGISTERED | Vollständige Records und unveränderte Objekte/Links. Beide Parents müssen REGISTERED sein, bevor Source6 beginnen darf. |
| FAILED | Sticky Fehler; kein neuer Konstruktor/Record/Import-/Sourceversuch, ausschließlich sicherer identitätsbezogener Fehlerabschluss. |

Jedes zurückgegebene Teilobjekt wird vor einem weiteren Provider-/Writeraufruf
gehalten. Bei gescheitertem POST bleibt es nur für sichere eigene Bereinigung
erfasst, nicht als gültig zugelassen. Vorbereitungszustände dürfen nur tatsächlich
noch nicht gesetzte endgültige Felder offen lassen; Typ, eigener Namespace,
vorgesehener Name und bereits gesetzte Felder bleiben geprüft. Konstruktorinterne
Anfangswerte verlangen eine getrennte Zustandsoracle im Source/Test-PRE,
keine globale Lockerung aller Parentprüfungen.

## Vollständige Metadaten, POST und Fehlerabschluss

Ab PREPARED gelten Modul.__name__ und spec.name genau Tests beziehungsweise
Tests.Contracts; __package__ ist derselbe Paketname, __spec__ das eigene Spec,
__loader__ None. spec.origin/loader/loader_state sind None, _set_fileattr False.
__path__ und submodule_search_locations sind dieselbe eigene Liste mit genauer
list-Klasse und Länge0. Modul.__file__/__cached__ fehlen; Speccache höchstens
der geprüfte unveränderte Nonewert. Eigene Namespacedicts haben nur primitive
begrenzte Stringkeys; Klassen-/Getter-/Keyprüfung geht jedem Lookup voraus.

Contracts ist vor Parent1-Link am eigenen Parent0 frei, danach genau eigener
Parent1. Die drei Source6/7/8-Kindnamen am Parent1 bleiben bis ihrer jeweiligen
ursprünglichen Quellenveröffentlichung frei, danach jeweils tatsächliches eigenes
gebundenes Modul. Kein Getter-/Importfallback oder Ersatzlink. Jeder Rootguard
prüft alle bereits veröffentlichten Objekte/Links und noch ausstehenden Slots.

Jeder Konstruktor-/Writer-/Compiler-/Exec-/Importercall hat denselben originalen
endlich gebundenen POST im finally-Pfad, auch bei Exception, falschem Typ,
Zero-/Teil-/Overflowwrite oder Unterbruch. Rückgabe vor Folgedispatch halten;
erst erfolgreicher POST und streng gültige Rückgabe erlauben Zustands-/Offset-
fortschritt. Fehlgeschlagener Teilwrite ist kein bestätigter BEGIN/COMPLETE.

Bindungsverlust dominiert mit festem RUNNER_SOURCE_BINDING; andernfalls führen
Providerfehler, ungültige Rückgabe oder Limitverletzung zu festem
RUNNER_SOURCE_REJECTED. Öffentliche Ablehnung ohne private Fehlermeldung und
Teilresultat. Keine Reparatur/Rebaseline durch weiteren normalen Helperaufruf,
kein Reentranz-/Retrypfad nach sticky Fehler.

Fehlerabschluss ausschließlich mit bereits im aktiven ursprünglichen Frame
gehaltenen primitiven Referenzen und eigenen Objekt-/Namespaceidentitäten;
kein Dispatch möglicherweise veränderter normaler Cleanup-/Guardhelfer. Die
Primitiven dürfen keine später fremd ersetzbaren Closure-/Globalwerte sein.
Cache-/Linklöschung nur bei exaktem Dict, zuvor vollständig geprüften primitiven
Keys und aktuell identischem eigenen Wert, rückwärts Source-/Child-/Parent1-/
Parent0-bezogen. Fremde Werte erhalten. Bei ungültigem Cache oder verlorener
sicherer Primitive keine riskante Lookup-/Getteroperation und kein Cleanup-
Gesamtclaim. Daraus folgt kein nativer Exit-/Gruppen-/Ressourcenabschluss.

## Unabhängiger Design-PRE und einzige Nacharbeit

Entwurf1dac51cbc3cc7244f6807a97392e61ac35fb1dbe unabhängig grundsätzlich tragfähig
und mit §33 vereinbar, aber noch nicht vollständig DESIGNED: P2 für konkrete
Pin-/Dominanz-/Zwischenzustands-/POST-/Metadatenregeln, P3 für Trennung von
DGN-Methodenabnahme und tatsächlichen Provideraufrufen. Die einzige zulässige
Entwurfsnacharbeit ergänzt genau diese verbindlichen Regeln und berichtigt
die3065-Byte-Zuordnung. Checkpoint erster Review erreicht; zwei/hartzwei
Entwurfsstände einschließlich gemeinsamer Koordination/Abschluss, Verbrauch
UNKNOWN. Ursprünglicher Sourceversuchsstand unverändert fünf/max6. Enger
unabhängiger Delta-PRE210f8e2cdd550b45e24f259039903e41875ed37b schließt P2/P3;
keine offenen priorisierten Designbefunde. DESIGNED-GO ausschließlich für den
Architekturentwurf und regulären reinen Dokumentationsabschluss. Keine Source-,
Test-, Generierungs- oder Lauf-Freigabe; tatsächlicher Fit weiter unbekannt.
Lokale Privacy aller vier betroffenen Dokumente sowie zwei Dokumentationsdeltas
PASS, fünf neue relative Markdownziele vorhanden, Whitespace PASS. Unveränderte
Runtime-/SQLtests nicht wiederholt. Aktuelle Head-/Base-/Main-Gates, Merge,
FullTree/Sync und eigene Branchbereinigung bis zum tatsächlichen Nachweis offen.
