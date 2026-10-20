# DGN-007 – gebundene verschachtelte Harness-Quellenfolge

Stand: 20. Oktober 2026. Basis `3387e308c8ae4f45d1cf8eb56176666e9e9355d4`.
Status `C2_SOURCE_TEST_DELTA_PRE_PENDING`; noch kein Kandidatenimport oder Lauf.

## Abgeschlossener Vorgänger und endlicher Umfang

[PR271](https://github.com/gecompat/SQL_PerformanceSchulung/pull/271) ist regulär
integriert. Zehn finale PR-Checks und acht frische Main-Workflows sind erfolgreich.
Neue16, bestehende Eingangs16 und Budget12 bestanden ohne SKIP; unabhängige
Befundschließung, vollständiger Head-/Mergetreevergleich, sauberes synchrones
Main und Abwesenheit beider eigenen Branches sind bestätigt. Der Sechserumfang
ist geschlossen und wird nicht zurückgesetzt. Reale Worker-/Usedbytes-/Trust-/
Methoden- und übrige Gesamtgates bleiben offen.

Der nächste Funktionsschnitt erweitert die tatsächliche Projektquellenfolge
auf Worker3 nach §33.1 des Importprofilvertrags. Genau drei SOURCES beginnen
in der Reihenfolge3/4/5 und schließen5/4/3; keine Parents. Ein Implementierungsowner
root, derselbe unabhängige Reviewer, höchstens sechs stabile Source/Testkandidaten,
Checkpoint2, harte Grenze6 und höchstens fünf geänderte Nachläufe. Auswahl-,
Source-/Test-/Deltareviews, explizite Lauf-GOs, Tests, Koordination, CI, regulärer
Merge, Main-Gates und eigene Branchbereinigung gehören zum gemeinsamen Umfang.
Verbrauch UNKNOWN. Bei ausgeschöpfter Grenze kein neuer Kandidat oder Umbenennen
des Scopes. Unveränderte erfolgreiche Prüfungen werden nicht wiederholt.

## Quelle, Handoffs und gehaltene Invocation

Neue additive API `build_harness_loader_control_bootstrap` im eigenen Toolmodul.
Unterbau ist die vollständige Eingangsquelle aus PR269; bestehende Proxyroute
und ältere Generatoren bleiben unverändert. Die neue Ausgabe darf die bereits
reviewten Tokenabstands-/lokalen Alpha-Transformationen wiederverwenden. Vor
Semantik bleiben aktueller vollständiger Profilrawliteral, fünf Scriptimporte,
131072-Byte-Cap und unabhängig rückgeführte Gesamt-AST-Oracle zwingend.

Sourceinitialisierung vor I/O-Initialisierung hält ursprüngliche Compile-/Exec-/
Importprovider, Modul-/Specklassen und privaten Sourceowner. Direkter einmaliger
I/O-Owner-/Entryhandoff vor Reportsnapshot und tatsächlicher EOF-/Payloadhandoff
entsprechen dem abgeschlossenen Proxyschnitt. Keine fremden Receipts als Authority,
keine spätere Global-/Closurebaseline oder zusätzliche Ausschlussliste. Die
gehaltene I/O-Entry muss erfolgreich denselben privat übergebenen Payload liefern.
Sourceauswahl ist ausschließlich Worker3/run_demo/PRE_IMPORT mit D5-Indizes3/4/5
und deren festen Modul-/Membernamen aus §33.1. Runner/Proxy bleiben abgelehnt.

Jede eigene Sourceinvocation hält dieselben empfangenen Rawbytes, D5/K, eigenes
exaktes Modul-/Spec-/Loaderobjekt, festen logischen Origin und ursprünglichen
Cache. Tatsächlicher Source-BEGIN muss vollständig bestätigt sein, bevor genau
diese Bytes mit dont_inherit=True/optimize=0 kompiliert werden. Exec erhält exakt
dieses Codeobjekt und denselben Modulnamespace. COMPLETE folgt erst nach eigener
Rückkehr und geschlossenen PRE-/POST-Bindungen. Gemeinsamer Writer, I/O-/Bytezähler
und Caps bleiben unverändert; kein neues Budget oder getrenntes Fehlerbudget.

## Privates Importgateway und verschachtelte Reihenfolge

Eine eigene vor Reportsnapshot gebundene Importfunktion wird ausschließlich in
die eigenen Candidatebuiltins eingesetzt. Die übrigen Builtinwerte entsprechen
der gehaltenen ursprünglichen Map. Die Gatewayfunktion und ihre Code-/Globals-/
Closureidentität werden mitgebunden; ursprüngliche Scriptbuiltins bleiben separat.
Ein privater Stack tatsächlicher Sourceinvocations bindet jeden Projektimport
an den aktiven gehaltenen Modulnamespace. Vor Keys/Attributen/Dispatch sind exakte
Typen, primitive Namen/Level/Fromlist und Namespaceidentitäten geschlossen.

Erlaubte Projektkanten sind run_demo→orchestrate_sessions/sqlcmd_process und
orchestrate_sessions→sqlcmd_process. Root3 startet einmal; neue Source4 nur unter3,
neue Source5 nur unter4. Nach vollständig bestätigtem Source5-COMPLETE darf der
spätere Import aus3 ausschließlich dasselbe gehaltene geprüfte Cachemodul5
wiederverwenden, ohne Compile/Exec oder zusätzliche Records. Fremde, vorbestehende,
halb initialisierte, wiederholte oder umgestellte Projektmodule und alle anderen
neun Kandidatennamen/Parents liefern keinen Sourceerfolg. Alle Kandidatenslots
sind vor Rootbeginn abwesend. Importargumente oder Cachelabels wählen keine Rawbytes.

Sonstige absolute Stdlibimporte dürfen ausschließlich über den vorher gebundenen
ursprünglichen Importprovider mit geschlossenen PRE-/POSTs gehen. Das ist eine
ausdrückliche Runtime-/Importer-Vertrauensannahme, kein Nachweis von Stdlibsource
oder Importneutralität. Die Modelle verwenden dafür nur einen eigenen festen
Provider ohne tatsächliche Imports. Neue reale Imports, DGN-Rawexecution und
operative Admission erfordern weiter separate Plattform-/S15-/P11-/Installations-/
Trustprüfungen und ausdrückliches Lauf-GO. Keine Finder-/Datei-/PYC-Projektauflösung.

Fehler, Reentranz, vorzeitiger direkter Loaderaufruf oder Wiederholung sperren
die ganze eigene Folge. Dominanter Bindingverlust geht sonstigen festen Issues
vor. Cleanup entfernt in umgekehrter Reihenfolge ausschließlich eigene identische
Cacheeinträge, erhält fremde Ersetzungen und __main__. Bereits geschriebene Bytes
sind nicht zurücknehmbar; ein fehlgeschlagener POST liefert keinen privaten Erfolg
und darf vor COMPLETE dessen Versuch nicht beginnen. Nach einem Fehler während
des COMPLETE-Writes können dessen Bytes auf dem Draht stehen, ohne Sourceerfolg.

## Eigene Tests und Abnahme

Vor Sourceänderung unabhängiger Auswahl-PRE; danach stabiler Source/Test-PRE mit
ausdrücklichem einmaligem Lauf-GO. Nur eigene sichere drei Bodyvarianten mit
festen from-import-Kanten und Konstanten; übrige sechs Bodies opak. Keine echten
Projektquellen ausführen. Eigene Import-/Compile-/Exec-/Wiretraces belegen echte
Verschachtelung, genau gehaltene Bytes/Code/Namespaces, bestätigte Recordordnung
und genau einen Cachehit5. Negative Fälle: falsche Rolle/Kante/Level/Fromlist,
Fremdtypen/-Namespaces vor Dispatch, vorzeitige/reentrante Loader, Bindungsdrift
vor/nach Import/Compile/Exec/Write, Syntax-/Exec-/Importfehler, falsche Cache-/Spec-/
Originidentität, unvollständige Writes, Budgeterschöpfung und Retry. Unabhängige
Wireoracle und volle AST-/Literal-/Alpha-Prüfung bleiben erforderlich.

Gezielte Windows3.14.7-/Linux3.12.3-Modelle unter -I -S -B, enge CI mit allen
tatsächlichen Quell-/Profil-/Fixtureabhängigkeiten; vorhandene Consumer nur bei
betroffener Änderung. Danach frische grüne Head-/Base-Gates, reguläre Integration,
frische Main-Gates, FullTree/Sync und eindeutiger eigener Branchcleanup.
Keine native Worker-/OS-I/O-/SQLprobe. Runner/Parents, Footer/SESSION_END-Sender,
operative Quellenwahl, vollständige Import-/Usedbytes-/Runtime-/Trust-/Methoden-
und Gesamtfreigabe bleiben offen. Kein solcher Claim aus einem Modell-PASS.

## Auswahl-GO und C1

Unabhängiges Auswahl-GO auf Plan-SHA256
`77d27a56e091af3f912d09433fe4f36844e0506dcff2b6bf4e20b40ea1fd9859`.
Verbindliche Präzisierungen in C1: geschlossene Tabelle aus aktivem Sourceindex,
exaktem Namen, level0 und genauer Fromlist. Die konkrete Stdlibtabelle folgt nur
den statisch gelesenen Top-Level-Imports der drei ausgewählten Projektdateien;
unbekannte Namen werden abgelehnt. Projektkanten werden vor Wirkungen einmalig
reserviert. Cachehit5 erfordert bestätigten COMPLETE und erneute volle Bindung;
Fromlistnamen müssen im geschlossenen eigenen Modulnamespace vorhanden sein.
Kein __getattr__-/Stern-/Submodulfallback. Sequenz-/Objektslots bleiben1/2/3,
Originslots3/4/5. Abgeschlossene Module werden beim gesamten Unwinding mitgeprüft.

C1 ergänzt additive Quelle und16 eigene Methoden. Sechs bestehende kleine
Proxyhelfer werden AST-genau unter eigenen privaten Namen übernommen: Namespace,
Specklassenstate, Originalfunktion, Guard, bestätigter Writer und Compile/Exec.
Der Guard ergänzt die originale Importprovider-/Gatewaybindung und prüft alle
eigenen Invocations; Compile/Exec wählt die tatsächliche private Stackspitze.
Übrige Operationen dieser Helfer bleiben erhalten. Die unabhängige ganze AST-
Oracle konstruiert diese begrenzten Änderungen separat und führt ausschließlich
zulässige lokale Alpha-Umbenennung zurück. Alte Generatoren/Tests unverändert.

Der Gateway hält tatsächliche Callerframes über seine Aufrufe: derselbe Caller
darf während eines laufenden Imports nicht reentrant dispatchen, ein tatsächlich
aktiver verschachtelter Kindsourcecaller bleibt erlaubt. Vor Compileabschluss
existiert kein Gatewaydispatch. Alle festen Stdlibkanten werden ebenfalls vor
Delegateaufruf einmalig reserviert. Die eigene Testdelegatefunktion liefert nur
ein festes eigenes os-Modul und führt keinen tatsächlichen Import aus.

Laufplanung nach unabhängigem Source/Test-PRE mit ausdrücklichem GO: zuerst
ausschließlich die Quellenfit-/Gesamt-AST-Methode unter Windows3.14.7 und
Linux3.12.3 (-I -S -B), einschließlich vollständigem tatsächlichem CRLF- und
separatem LF-Profilrawliteral. Nur bei beidseitigem PASS die übrigen15 Methoden
einmal auf beiden Plattformen. Bei Fitfehler keine innere Suite; keine blinde
Wiederholung oder Capanhebung. Die16 Methoden behandeln echte eigene verschachtelte
Compile-/Exec-/Importtraces, LF/CRLF, Cachehit, Partialwrites, Auswahl/Inputfehler,
geschlossene Projekt-/Stdlibkanten, tatsächlich ausgeführte Fremdargumentfälle,
fehlende Fromlistwerte ohne Getterfallback, Syntax/Exec/Provider-/Moduldrift,
fremde Modulklasse, Reentranz, Budgets und Retry.

Aufwandseinordnung: ein Owner/ein unabhängiger Reviewer, genau eine neue enge
CI mit vollständigen direkten und transitiven Generator-/Profil-/Fixturequellen.
Keine doppelten Privacyvollscans oder zusätzlichen Native-/SQLjobs. Alte Consumer
werden nicht verändert und nicht separat erneut ausgeführt; ihre Definitionen
sind lediglich ausgewählte Fixture-/Oraclereferenzen. CI führt neue16 am Head
und frisch auf Main aus. Lokale Logs bleiben privat, nur Status/Counts/enge
Fehlerstellen werden ausgewertet. Keine zusätzlichen Modelle/Automationen.

Ein Source/Testkandidat/max6, keine Nachläufe, Verbrauch UNKNOWN. Quellenfit und
Modellsemantik unbekannt. Source/Test-PRE und ausdrückliches gestuftes Lauf-GO
ausstehend; bisher nur Text-AST-/Inline-AST-Syntaxprüfung, keine Generierung.

Primärquellen, geprüft am20.Oktober2026:
[Python-Importsystem](https://docs.python.org/3.12/reference/import.html)
trennt Importaufruf und Namensbindung;
[__import__](https://docs.python.org/3.12/library/functions.html#__import__)
beschreibt Globals/Locals/Fromlist/Level. Die engere geschlossene Auswahl und
die tatsächlichen Code-/Raw-/Recordbindungen sind Projektvertrag.

## C2 und Checkpoint2

C1 `2dec1b3164edb074fce25bb755078b2ccd9760cb` unabhängig geprüft, noch kein
Lauf-GO: ein P2 für späte Fremdbelegung noch nicht veröffentlichter Slots4/5 und
ein P3 für nicht eindeutig erreichte Primitive-Typgrenzen. Sonstige Source-/
Gateway-/Wire-/Budget-/Oraclebedingungen nachvollziehbar; keine Proben ausgeführt.

C2 prüft in jedem Guard zusätzlich die Abwesenheit sämtlicher neun Kandidaten
und beider Parents, soweit nicht dieselbe tatsächliche eigene Invocation bereits
veröffentlicht wurde. Veröffentlichte Invocations müssen weiter die vollständige
eigene Modul-/Spec-/Loader-/Cachebindung erfüllen. Dadurch wird eine spätere
Fremdbelegung vor weiteren Wirkungen erkannt und niemals überschrieben.
Die bestehende Auswahl-/Cachemethode ergänzt tatsächliche Compilecallbacks nach
bestätigtem BEGIN3 beziehungsweise BEGIN4: Fremdslot4/5 gesetzt, vor dessen Compile
abgelehnt, exakte frühere Compileanzahl und fremde Eintragsidentität erhalten.

Primitive-Gegenproben übergeben den Fremdnamen mit gültigem Caller und Fromlist;
ein externer __len__-Trap bleibt ebenso wie Getter/EQ unaufgerufen. levelFalse
statt True beweist die exakte Integerprüfung unabhängig vom Wertvergleich0.
Das ursprüngliche Source-EXEC muss tatsächlich erreicht sein. Keine schwächere
Oracle und kein Zählerreset; weiterhin16Methoden. Ganze AST-Oracle um genau die
zusätzliche Abwesenheitsinvariante ergänzt.

Checkpoint2: zwei Source/Testkandidaten/max6, ein geänderter Nachlauf, Verbrauch
UNKNOWN. Gezielter unabhängiger Delta-PRE und ausdrücklich gestuftes Lauf-GO
ausstehend; vollständiger Fit und innere Modelle weiterhin ungeprüft.
