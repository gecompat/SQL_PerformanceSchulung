# DGN-007 – quellenbegründete Auswahl frischer Workerprofile

## Aktueller siebter Stand: bereinigte Argumentübergabe

Der Mensch hat genau den siebten Quellen-/Teststand für die Argumentkorrektur,
Gegenprobe und offenen Paketprüfungen ausdrücklich freigegeben. Derselbe
Implementierungsverantwortliche root und derselbe unabhängige Reviewer führen
den bestehenden Rahmen weiter; sieben von hart sieben Ständen, Verbrauch
UNKNOWN. Der vorherige Diagnoseabschluss aus
[PR284](https://github.com/gecompat/SQL_PerformanceSchulung/pull/284) ist mit
unabhängigem Review, sieben grünen Head-, fünf grünen Base- und fünf frischen
grünen Main-Prüfungen, vollständiger Übernahme, Synchronisation und eigener
Branchbereinigung in `4d758c1f8c52a7dce621eafc838063524fcd5a28` abgeschlossen.
Die nachfolgenden Grenzen für frühere Stände sind historische Evidenz.

Die private Startbrücke speichert ihren Zielpfad und setzt `sys.argv`, also
die Programargumentliste, vor dem Scriptstart auf genau diesen einen
Programmeintrag. Das Transportargument wird nicht als Testauswahl weitergegeben.
Die Gegenprobe bestätigte diese tatsächliche Eintrittsform und lehnte die
frühere Doppelpfadform sowie eine leere Argumentliste ab. Anschließend liefen
genau beide Provider-Testmethoden erfolgreich, ohne Fehler oder Skip;
ein leerer oder nur teilweise ausgewählter Testlauf genügt nicht. Provider
bezeichnet hier den Prüfinterpreter. Alle neun falschen Providerkonfigurationen
wurden abgelehnt, der positive Syntaxbaum-Sentinel bestanden.

Der vollständige Ablauf behält die Deadlinefälle, beide synthetischen
Cleanup-Gegenproben und die eigene Windows-Jobabsenz bei. Erst danach folgen
die Argument-/Interpretergegenprobe und genau ein Paketlauf unter dem bereits
vorhandenen Windows-Prüfinterpreter CPython 3.12. Alle 37 Datengegenproben,
drei Fünfformenprüfungen und drei unveränderten Ganz-AST-/Fitmethoden bleiben
erforderlich; AST bedeutet Abstract Syntax Tree, abstrakter Syntaxbaum.
Originalprofilbytes, feste 3.12-Hashes, Quellenpins und Bytegrenzen bleiben
erhalten. Keine neue Installation, kein Linux-/WSL-, Worker-, Demo- oder
SQL-Start. Neue eigene Ziele erhalten die Ergebnisse; alte Quellen und
Fehlversuche bleiben unverändert privat erhalten.

Der unabhängige Delta-/Testreview schloss den siebten Stand ohne offene
priorisierte Befunde und erteilte genau ein gestuftes Lauf-GO. Dieser Aufruf
erfolgte einmal. Kein unveränderter Wiederholungsversuch und kein achter
Stand ohne neue ausdrückliche Entscheidung.

### Ergebnis: Eintritt korrigiert, zusätzlicher flacher Profilvergleich zu groß

Deadlinefälle und beide synthetischen Cleanup-Gegenproben bestanden erneut
an der geänderten Startbrücke. Argument- und Interpretergegenprobe liefen
anschließend vollständig durch. Der tatsächliche Pakethelfer unter isoliertem
Windows-CPython 3.12 erreichte die Quellenpin-, Installations- und vollständige
Eingangsprüfung mit 27 Git-Rohdateien. Der Kontrollfluss bis zur späteren
Fehlerstelle belegt außerdem die erfolgreiche Größen-, Encoder- und
Fünfformenvergleichsprüfung für den ersten Worker. Es gibt keine gespeicherten
Einzelgrößen dieses Zwischenstands und keine entsprechende Abnahme der beiden
anderen Worker.

Danach stoppte der Helfer bei `POSITIVE_MATCH`: Er ruft zusätzlich den älteren
flachen `match_reported_profile`-Vergleich auf. Dieser serialisiert Worker und
Kontext in einen einzelnen Datensatz unter unverändertem 16384-Byte-Limit.
Eine ausschließlich lesende Quellen-/Datenanalyse ergibt bereits eine
konservative Untergrenze von **17156 Bytes** für 85 Moduldatensätze und die
gebundenen Quelldeskriptoren. Dabei wurden zahlreiche tatsächliche Werte durch
kürzere Leerwerte ersetzt; der wirkliche Datensatz kann nicht kleiner sein.
Der [bestehende Vergleich](../../Tests/Tools/dgn007_import_profile_binding.py)
lehnt diese Überschreitung mit `METADATA_LIMIT` ab. Das ist eine aus Quellen
und Größenuntergrenze hergeleitete Ursache: Der tatsächliche fehlgeschlagene
Lauf speicherte nur das Helferlabel `POSITIVE_MATCH`, nicht den verworfenen
Vergleichsreport. Es gab keinen erneuten Helfer- oder Matcheraufruf.

Alle vier begonnenen Windows-Jobs endeten mit beendetem Hauptprozess,
abgeschlossenem Reader und geprüft null aktiven Jobprozessen. Eine negative
Kontrollbyte-Pinprobe im Paketlauf wurde erreicht; die übrigen 36 geplanten
Datengegenproben, Formgegenproben und alle drei Ganz-AST-/Fitmethoden wurden
nicht ausgeführt. Die neuen 27 Rohdateien bleiben privat erhalten; keine
Worker-Scriptdateien und kein fertiger Paketbericht. Die Argumentübergabe und
Interpreterzulassung sind lokal bestätigt; das vollständige Auswahlpaket
bleibt offen. Keine Worker-, Linux- oder SQL-Ausführung.

### Verbleibende Korrektur im bestehenden Poolverfahren

Vorgeschlagen ist ein ausdrücklich freizugebender achter Quellen-/Teststand,
der die zusätzlichen Profilgegenproben über den bereits vorhandenen
[Fünfformenvergleich mit Stringpools](../../Tests/Tools/dgn007_pooled_profile_codec.py)
führt. Ein Stringpool speichert wiederkehrende Texte einmal und verwendet
gebundene Referenzen. Der flache Vergleich ist für die vollständige große
Auswahl unter seinem Einzelrahmenlimit ungeeignet. Felder, Module,
Originalbytes, feste Hashes, Bytegrenzen und semantische positive/negative
Prüfpflichten bleiben vollständig erhalten. Keine Anhebung des Limits oder
Produktänderung allein für einen PASS. Vor Ausführung benötigt der konkrete
Korrekturstand unabhängigen Quellen-/Testreview und ein genaues Lauf-GO.
Dieser Vorschlag ist keine bereits erteilte Freigabe, keine neue Zählung und
keine operative Workerfreigabe. Sieben/hartsieben, Verbrauch UNKNOWN;
der sichere Diagnoseabschluss wird regulär integriert.

## Freigegebene Interpreterkorrektur nach dem Diagnoseabschluss

Dieser Abschnitt beschreibt den historischen Rahmen bis einschließlich sechs;
die ausdrücklich freigegebene siebte Fortsetzung steht oben.

Der Mensch hat den bestehenden Rahmen ausdrücklich auf höchstens sechs
Quellen-/Teststände mit Checkpoint nach Stand fünf erweitert. Das ist dieselbe
Auswahlaufgabe, kein neuer Scope oder Neustart der Zählung. Ein
Implementierungsverantwortlicher root und derselbe unabhängige Reviewer führen
Korrektur, Gegenprobe, lokale Prüfungen und vollständigen Integrationsabschluss;
Verbrauch UNKNOWN. Der Diagnoseabschluss aus
[PR283](https://github.com/gecompat/SQL_PerformanceSchulung/pull/283) ist mit
sieben grünen PR-Prüfungen, fünf grünen Basisprüfungen, fünf frischen grünen
Main-Prüfungen, vollständiger Baumübernahme, Synchronisation und eigener
Branchbereinigung in `e0cec9842971d0ecdf3f1604cdd5f59f3109a946` abgeschlossen.
Die nachfolgenden Abschnitte zum vierten Stand bewahren den damaligen Fehler.

### Ergebnis des sechsten Standes: Aufruffehler vor den Providerprüfungen

Der unabhängige Delta-/Testreview schloss beide Befunde des fünften Standes
statisch und erteilte genau ein gestuftes Lauf-GO für den sechsten Stand.
Dieser Aufruf erfolgte einmal. Die reinen Deadlinefälle sowie beide
synthetischen Cleanup-Gegenproben erfüllten die Erwartungen: Der erzwungene
Fehler nach Jobzuweisung und der Timeout mit eigenem Nachfahren endeten jeweils
mit beendeten Hauptprozessen, abgeschlossenem Reader und null aktiven
Jobprozessen. Der Timeout blieb als Fehler gesetzt. Diese erwarteten
Fehlerfälle sind Gegenprobenerfolge, kein erfolgreicher Paketlauf.

Der dritte begonnene Job scheiterte anschließend bei der Testauswahl. Die
Startbrücke übergab ihren Zielscriptpfad als zusätzliches Argument in
`sys.argv` an `runpy.run_path`. Dieser Aufruf passt nur den Programmeintrag
`sys.argv[0]` an; `unittest.main` verwendet ohne eigene Argumentliste die
gesamte `sys.argv`-Liste. Der transportierte Dateipfad wurde dadurch als
Testname ausgewertet. Ergebnis war ein fehlgeschlagener Loaderplatzhalter
`unittest.loader._FailedTest.Runtime` mit `AttributeError`, keine Ausführung
der beiden vorgesehenen Provider-Testmethoden. Die lokalen Standardbibliotheks-
quellen und die Primärdokumentation zu
[runpy.run_path](https://docs.python.org/3.14/library/runpy.html#runpy.run_path)
und [unittest.main](https://docs.python.org/3.14/library/unittest.html#unittest.main)
begründen diese Diagnose, gelesen am 21. Oktober 2026.

Der dritte Job endete mit Fehlercode und geprüft null aktiven Jobprozessen.
Alle drei begonnenen Jobs sind bereinigt. Der vierte geplante Job, also der
eigentliche Pakethelfer, wurde nicht gestartet. Keine neuen Rohdateien, kein
Paketbericht, keine Worker-Scriptdateien; die 37 Paketgegenproben, drei
Fünfformenprüfungen und drei Ganz-AST-/Fitmethoden sind in diesem Stand
sämtlich nicht ausgeführt. Die frühere negative Kontrollbyteprobe aus dem
vierten Stand bleibt erhalten; sie ist kein aktueller vollständiger Paket-PASS.
Die Interpreterkorrektur ist statisch geprüft, ihre beabsichtigte lokale
Providergegenprobe und das Paket sind noch nicht abgenommen.

Sechs von hart sechs Ständen, Verbrauch UNKNOWN. Der einmalige Aufruf wird
nicht wiederholt; Quellen, Logs, Jobeigentumsnachweise und alte Partialartefakte
bleiben unverändert privat erhalten. Zulässig ist jetzt der unabhängige
Diagnose-/Dispositionsabschluss samt regulärer Dokumentationsintegration.

### Konkreter Vorschlag zur weiteren Korrektur

Dieser Vorschlag aus PR284 wurde durch den aktuellen menschlichen Auftrag für
genau den siebten Stand freigegeben. Der frühere Entscheidungsvorbehalt ist
historisch; unabhängiger Quellen-/Testreview und konkretes Lauf-GO bleiben
vor Ausführung erforderlich.

Eine neue ausdrückliche Erweiterung um genau einen siebten Quellen-/Teststand
wäre ausschließlich für die Argumentübergabe der Startbrücke und die
Gegenprobe erforderlich: Transportargument vor dem Scriptstart entfernen,
die erwartete Ausführung beider Provider-Testmethoden ausdrücklich prüfen und
die noch unerledigten Paketpflichten mit unveränderten Oracles, Originalbytes,
3.12-Hashes und Größenlimits abschließen. Vor Ausführung bleiben unabhängiger
Quellen-/Testreview und konkretes Lauf-GO erforderlich. Dieser Vorschlag ist
keine Freigabe, kein Retry des unveränderten sechsten Standes und kein neuer
Scope. Keine Worker-, Linux-, Demo- oder SQL-Freigabe daraus ableiten.

Der fünfte Stand korrigierte die Interpreterzulassung vor allen weiteren
Imports und Datei-/Prozesseffekten. Er verlangt tatsächlich CPython 3.12 unter
Windows sowie die Isolationflags `-I -S -B` (isolierte Ausführung, kein
Site-Import, keine Bytecodedateien). Eine bereits vorhandene gebündelte
Windows-Laufzeit ermöglicht die Prüfung; eine neue Installation oder ein
Linux-Prozess ist dafür nicht nötig. Dieser Prüfinterpreter ist von der
vorgewählten Linux-Workerinstallation zu unterscheiden.

Zwei geplante Gegenprobemethoden prüfen neun falsche Providerkonfigurationen
einschließlich des tatsächlichen bisherigen Windows-Interpreters sowie die
positive Zulassung bis zum nächsten Import. Kontrollierte Imports und
beobachtete Dateizugriffsaufrufe sorgen dafür, dass eine falsche Voraussetzung vor
weiteren Wirkungen scheitert. Erst danach darf genau ein vollständiger
Paketlauf unter dem tatsächlichen 3.12-Prüfer folgen. Die 37 Datengegenproben,
drei vollständigen Fünfformenprüfungen und drei vorhandenen unveränderten
Ganz-AST-/Fitmethoden bleiben erforderlich; AST bezeichnet den Abstract Syntax
Tree, den abstrakten Syntaxbaum. Quellenpins, Originalprofilbytes, feste
3.12-Hashes und sämtliche Bytegrenzen bleiben unverändert.

Am Checkpoint nach fünf lehnte der unabhängige Review den Aufruf mit zwei
Befunden am Windows-Owner ab: Im Fehlercleanup fehlte die abschließende
Prüfung auf null aktive Jobprozesse; ein später Exit konnte die reguläre
Deadline umgehen und feste Cleanupwartezeiten konnten den gemeinsamen Rahmen
überschreiten. Interpreterzulassung, Gegenprobe, Rollen und Quellenpins waren
statisch geschlossen. Kein Aufruf des fünften Standes.

Der sechste Stand bündelt diese Korrekturen: ein gemeinsamer Abschluss für
Erfolg und Fehler, Reap des gehaltenen Hauptprozesses (dessen Beendigung
abwarten), Readerabschluss und abschließende Jobabsenz. Ein einmal erkannter
Timeout bleibt gesetzt; vor der Startfreigabe und nach jedem Exit wird die
Deadline geprüft. Jede Cleanupwartezeit verwendet nur die gemeinsame Restzeit.
Zwei vorgeschaltete synthetische Gegenproben erzwingen einen Fehler direkt
nach Jobzuweisung sowie einen Timeout mit eigenem Parent und eigenem Child.
Beide müssen ihre Prozesse vollständig abschließen, bevor die
Interpretergegenprobe und der vollständige Paketlauf folgen dürfen.

Der konkrete Aufrufplan umfasst damit höchstens vier eigene Windows-Aufrufe. Vor
dem Helfereintritt wartet jeder Prozess auf einer privaten Startbrücke, bis
sein gehaltener Prozesshandle einem eigenen Windows-Job zugeordnet ist. Ein
Job fasst diesen Prozess und seine Nachfahren für den eigenen Cleanup zusammen.
Maximal vier gleichzeitig aktive Prozesse je Job, je 65536 Ausgabebytes,
zehn Sekunden für die Gegenprobe und 120 Sekunden für das Paket; gemeinsamer
Rahmen 150 Sekunden einschließlich Cleanupreserve. Jobweites Beenden und
geprüfte null aktive Prozesse gehören zum Abschluss. Kein Linux-/WSL-,
Worker-, Demo- oder SQL-Start; neue eigene Ziele erhalten die Ergebnisse,
die alten Partialartefakte bleiben unverändert erhalten.

Der sechste Stand wurde genau einmal nach unabhängiger Quellen-/Test- und
Aufruffreigabe ausgeführt und stoppte wie oben beschrieben. Kein unveränderter
Wiederholungslauf. Sechs von hart sechs Ständen; kein siebter Stand oder
Budgetreset ohne neue ausdrückliche Entscheidung. Die Quellen des fünften
Standes und sämtliche vorherigen Fehlversuche bleiben erhalten.

## Auftrag und gemeinsamer Rahmen

DGN-007 bezeichnet die Diagnose-Demo mit getrenntem Quellen- und Laufnachweis.
Der [Auswahlplan aus PR282](DGN_007_WORKER_PROFILE_SELECTION_PLAN.md) ist in
`e4b373d679ef2f8670913239664e55623cf7caaa` vollständig integriert. Sieben grüne
Prüfungen des PR-Stands, drei der Main-Basis und fünf frische Main-Prüfungen,
unabhängiger Review, vollständige Baumübernahme, Synchronisation und eigene
Branchbereinigung sind im [PR282-Abschlussnachweis](https://github.com/gecompat/SQL_PerformanceSchulung/pull/282)
gebunden. Der kontinuierliche menschliche Auftrag führt jetzt zum konkreten
privaten Auswahlpaket für genau eine vorhandene Linux-Installation von CPython
3.12 und drei vollständige Workerdeklarationen.

Ein Implementierungsverantwortlicher root und derselbe unabhängige Reviewer
führen den Schnitt. Gemeinsame Einheit sind stabile Paket-/Quellen-Teststände:
Checkpoint nach dem ersten, harte Grenze vier einschließlich Rootarbeit,
Reviews, Korrekturen, lokaler Prüfungen, Koordination und vollständigem
Integrationsabschluss. Verbrauch UNKNOWN, nicht verlässlich gemessen. Ein alter
Runnerkandidat oder der historische native Metadatenversuch wird nicht unter
neuem Namen wiederholt. Quellenroute, Originalbytes und Größenlimits bleiben
unverändert. Eigener Branch: `codex/dgn007-worker-profile-selection`.

Das Paket wählt S15 (15 skalare Installationsfelder) und P11 (elf Felder je Modul,
etwa Name, Herkunft und Loader) vollständig vor. Ein Loader ist die zum Laden
eines Moduls gebundene Instanz. Private Locator, vollständige Werte, Rohdaten und
Quellenpins bleiben unversioniert; diese Dokumentation beschreibt Methode,
Prüfstatus und Grenzen.

## Ergebnis: Paketlauf am falschen Prüfinterpreter gestoppt

Der unabhängig freigegebene vierte Stand wurde genau einmal unter Windows mit
CPython 3.14.7 aufgerufen. Er brach bei `INPUT_PREPARATION` ab. Eine anschließende
rein lesende Diagnose mit dem bestehenden Eingangsprüfer meldete
`BOOTSTRAP_CHANGED`, obwohl die Git-Rohbytes vollständig übereinstimmten.
Der [Vertrag des statischen Eingangsprüfers](DGN_007_EXECUTION_EDGE_VERIFIER.md)
verlangt ausdrücklich Python 3.12 für die eingefrorenen Ganzdatei-AST-Hashes
(AST: Abstract Syntax Tree; abstrakter Syntaxbaum). Der Windows-Pakethelfer
hatte diese Interpretervoraussetzung nicht abgesichert. Das ist ein Fehler der
gewählten Prüfumgebung, kein nachgewiesener Bootstrap-Quellenwechsel.

Die rein lesende Ursachenprüfung reproduzierte für beide betroffenen
Bootstrapgruppen die gespeicherten Hashes ausschließlich mit
`ast.dump(show_empty=True)`; die Standardausgabe unter 3.14 wich ab. Die
[Python-Dokumentation zu ast.dump](https://docs.python.org/3.14/library/ast.html#ast.dump)
erläutert die inzwischen standardmäßig ausgelassenen optionalen leeren Listen.
Diese Übereinstimmung erklärt den konkreten Befund; sie ersetzt weder den
vorgeschriebenen 3.12-Prüfer noch belegt sie allgemeine AST-Gleichwertigkeit
zwischen Pythonversionen. Kein Hash, Prüfer oder AST-Verhalten wurde verändert;
kein erneuter Paketlauf.

Erreicht wurden die vier erfolgreichen Tabellenlesertests, der eine statische
Binärread und im Paketlauf eine negative Kontrollbyte-Pinprobe. Die übrigen
36 geplanten negativen Fälle, sämtliche Form-/Größenprüfungen und alle drei
Ganz-AST-/Fitmethoden wurden nicht ausgeführt. Die 27 eigenen Git-Rohdateien
bleiben als Partialartefakte erhalten. Kein fertiger Paketbericht und keine der
drei Worker-Scriptdateien entstanden. Es gibt keinen Paket-PASS und keine
native Ausführung.

Vier von hart vier Quellen-/Testständen sind verbraucht, Verbrauch UNKNOWN.
Der sichere Abschluss umfasst Diagnose, unabhängigen Befundreview und deren
Dokumentationsintegration. Das Auswahlpaket selbst bleibt unvollständig.
Kein fünfter Stand, Wiederholungsversuch oder Scopewechsel ohne ausdrückliche
begrenzte Erweiterung.

## Statische Tabellenfrage vor der Paketerzeugung

Die historische 85-Modul-Auswahl liefert nur Hinweise für Namen und Locator.
Sie ist keine neue Sollbaseline und wird vom neuen Pakethelfer nicht geladen.
Aktuelle Installations- und Bibliotheksdateien werden ausschließlich lesend
geprüft. Es gibt keinen Linux-/WSL-Aufruf (WSL: Windows Subsystem for Linux;
Linux-Umgebung unter Windows), keinen Probe- oder Workerstart.

Die offene Tabellenfrage wird mit einem begrenzten Windows-Helfer für ELF
(Executable and Linkable Format; Format der gewählten Linux-Executable)
beantwortet. Er unterstützt ausschließlich das geprüfte 64-Bit-Profil mit
kleiner Byteordnung und fester Executableform. Größengrenzen, eindeutige dateigedeckte
Adressbereiche, Symbolformen, Namen und endliche Tabellen mit Abschlussmarken
werden vor einer Rückgabe geprüft. Höchstens 16 MiB Bilddaten; keine Ausführung
oder Rekonstruktion von Pythoncode aus dem Binary.

Die Tabellenformen folgen den CPython-3.12.3-Primärquellen
[Importstrukturen](https://raw.githubusercontent.com/python/cpython/v3.12.3/Include/cpython/import.h)
und [Frozen-Tabellen](https://raw.githubusercontent.com/python/cpython/v3.12.3/Python/frozen.c),
gelesen am 21. Oktober 2026. Tabellenmitgliedschaft wird ausdrücklich von
aktivierter Frozen-Verfügbarkeit, tatsächlicher Cachemitgliedschaft und
ausgeführten Bytes getrennt.

Zwei eingefrorene Helferstände: Vor Ausführung wurde die explizite lokale
Importauflösung des isolierten Testharness ergänzt. Die unabhängige Prüfung
schloss priorisierte Befunde und erlaubte gestuft zunächst vier synthetische
Gegenproben, anschließend genau einen Read des separat gepinnten Byteobjekts.
Die vier Methoden bestanden ohne Fehler oder Skip. Erst danach erfolgte der
begrenzte Read mit exakter Längen- und Hashprüfung desselben Byteobjekts.
Ergebnis ausschließlich statisch: 60 Builtin-, drei Bootstrap-Frozen- und
15 weitere Frozen-Tabelleneinträge. Kein Wiederholungslauf.

## Paketprüfung und gebündelte Korrektur

Der dritte eingefrorene Quellen-/Teststand wurde unabhängig vor Ausführung mit
drei Befunden abgelehnt: vollständige Quellenpins vor Projektimport fehlten,
die Runnerroute wurde fälschlich auch für Proxy und Harness gewählt, und die
Gegenproben erfassten noch keine veränderten Kontrollbytes oder Form-/Bytegrenzen.
Kein Lauf oder Generierungsversuch dieses Standes. Der vierte Stand bündelt
diese Korrekturen. Seine unabhängige Delta-Prüfung schloss die drei Befunde und
erteilte genau ein Lauf-GO (Freigabe für den geprüften Windows-Aufruf). Der
freigegebene Lauf scheiterte anschließend wie oben beschrieben. Vier/hartvier
Stände, Verbrauch UNKNOWN; kein weiterer Stand unter einem neuen Namen.

Der Entwurf liest feste Installationsmember bis gemeinsam 32 MiB, bindet die
statischen Tabellen an dasselbe gepinnte Executablebild und prüft die konkrete
Sysconfig-Datenquelle. Paketmetadaten begründen eine deklarierte Version;
sie werden nicht als gemessene Runtimeversion ausgegeben. Die vollständige
85-Namen-Folge wird getrennt vorgewählt und gegen aktuelle Quellen begründet.
Weder ein beobachteter Cache noch ein erfolgreicher Bericht wird zum Soll.
Ein separat eingefrorenes Manifest bindet alle 21 lokalen Generator-/Codec-/
Oracle-/Fixturequellen an die Base und ihre tatsächlichen Arbeitsdateibytes
vor dem ersten Projektimport. Diese Quellenpinprüfung hat eine eigene
4-MiB-Grenze und wird vor Artefaktschreiben nochmals abgeschlossen.

Alle drei Workerdeklarationen verwenden dieselbe Installation, aber getrennte
Ordinal-/Einstiegs-/Kontrollkontexte und vorgewählte Scriptlocator. Die beiden
Kontrollrollen und fünf direkten Scriptimporte bleiben erhalten. Die bekannte
FileFinder-Hookbindung folgt der geprüften Kontroll-/Importlibquelle; daraus
folgt kein Nachweis eines tatsächlich gehaltenen Workerhooks.

Das geplante Verfahren kopiert exakt die 27 gebundenen Gitmember in ein neues
eigenes privates Ziel und verwendet den bestehenden statischen Bundle-/
Eingangsprüfer. Kein Kandidatenbody wird importiert oder ausgeführt. Pro Worker
werden sämtliche fünf Formen und ihr gemeinsames 65536-Byte-Limit vor
Encoderfreigabe geprüft; geplante Gegenproben prüfen fehlende/zusätzliche
Module, Versions-/Kontextabweichung, falsche Origins, Loadernamen, Aliase und
unvollständige Felder. Hinzu kommen geänderte aktuelle Kontrollbytes gegen den
eingefrorenen Pin, unvollständige Formsets, die Einzel- und Gesamtbytegrenzen
sowie semantisch gültige synthetische Langlocator-Auswahlen mit Größenoverflow
und Encoderablehnung. Geplant sind insgesamt 37 negative Datenfälle;
Langlocator-Auswahlen werden ausschließlich im Speicher verwendet.

Für den tatsächlichen neuen Profillocator bleibt das 131072-Byte-Scriptlimit
maßgeblich. Die vorhandene unabhängige Ganz-AST-Oracle (AST: Abstract Syntax
Tree; abstrakter Syntaxbaum) soll mit den neu gewählten Eingaben die gesamte
Quelle und unveränderte Originalprofilbytes prüfen. Runner und Harness prüfen
zusätzlich Unix-Zeilenenden (LF: Line Feed); die vorhandene Proxy-Methode prüft
nur die aktuelle Rohform.
Runner, Proxy und Harness erhalten jeweils den passenden vorhandenen Builder
und dessen eigene Fit-/Ganz-AST-Methode. Bestehende Assertions bleiben erhalten.
Erst nach Erfolg aller drei Routen und dem Quellenpin-Nachcheck dürfen die drei
vorher abwesenden eigenen Scriptdateien erzeugt werden. Eine reine Generierung
startet diese Dateien nicht.

## Claimgrenze und Abschluss

Das Paket ist **nicht vollständig validiert**; sein einziger Lauf ist vor den
Form-/Fitprüfungen fehlgeschlagen. Auch ein späterer reiner Paket-PASS belegt weder
frische Workeraufnahme noch verwendete Quellenbytes, SESSION_END
(Abschlussmeldung mit Counts und Kanalhash), nativen Exit/Cleanup oder die
Messmethode. DEC-076 (vertrauenswürdige Schulungsquellen ohne
Manipulationsisolation) bleibt maßgeblich. Keine Produktions- oder SQL-Freigabe.

Vor einem späteren nativen Lauf bleibt ein separat geprüfter konkreter
Prozess-/Kanalplan mit gemeinsamem Zeit-, Byte- und Schrittbudget sowie
gehaltenen eigenen Windows-/Linuxprozessen und unabhängiger Absenzprüfung
erforderlich. Ein Paketbericht oder Windows-Launcherexit ersetzt diese Gates
nicht. Fehler und Partialartefakte bleiben privat erhalten; kein blinder Retry,
keine fremde Bereinigung oder Budgeterneuerung.

Die öffentliche Diagnoseintegration erfolgt nach unabhängiger Befundschließung und lokalen
Dokumentations-/Datenschutzprüfungen über aktuelle grüne PR-/Base-Gates,
regulären Merge, frische Main-Gates, vollständige Übernahme, Synchronisation und
sichere eigene lokale/Remote-Branchbereinigung. Unveränderte grüne Runnermodelle
werden nicht erneut ausgeführt. Private Evidence und fremde Ressourcen bleiben
erhalten.

## Erforderliche Entscheidung zur Wiederaufnahme

Der folgende Vorschlag aus PR283 wurde durch den aktuellen menschlichen
Auftrag ausdrücklich freigegeben; sein damaliger Freigabevorbehalt ist
historisch. Die konkrete Ausführung verlangt weiterhin die oben beschriebene
unabhängige Quellen-/Testprüfung und das passende Lauf-GO.

Vorgeschlagen war eine ausdrückliche begrenzte Erweiterung für die Korrektur
der AST-Providerwahl, eine Gegenprobe zur Ablehnung des falschen Interpreters
vor weiteren Wirkungen und nötige unabhängige Reviewkorrekturen: denselben
Rahmen von vier auf höchstens sechs stabile Quellen-/Teststände erweitern,
mit Checkpoint nach Stand fünf. Dabei bleiben
die bisherigen Fehlversuche erhalten, die 3.12-Hashes und Bytegrenzen
unverändert. Die noch unerledigten Paketprüfungen benötigen erneut eine
konkrete Quellen-/Testprüfung vor Ausführung und ein passendes Lauf-GO.
Eine notwendige native 3.12-Prüferinvocation wäre vorher mit eigenem endlichen
Prozessplan zu prüfen; daraus folgt keine Worker-, Demo- oder SQL-Freigabe.

Dieser Vorschlag erteilte damals selbst keine Freigabe. Die
[gemeinsame Wellenbudgetregel](../../.ai/foundation/PROCESSING_EFFICIENCY_POLICY.md#shared-wave-budget)
verlangt an der harten Grenze: „admit no new work or agent“. Der kontinuierliche
menschliche Auftrag erneuerte diesen ausgeschöpften konkreten Rahmen nicht
automatisch. Bis zur jetzigen ausdrücklichen Entscheidung waren nur der
sichere Diagnoseabschluss und dessen reguläre Integration zulässig.

Der unabhängige Diagnose-/Dispositionsreview des Dokumentationsstands
`a683d743376f2bb25e39d9893acf08241492dd14` meldete keine offenen priorisierten
Befunde und bestätigte das Integrations-GO ausschließlich für diesen
Dokumentationsabschluss. Auch die Präzisierung auf höchstens sechs Stände mit
Checkpoint nach fünf wurde nur als noch nicht freigegebener
Entscheidungsvorschlag bestätigt.
