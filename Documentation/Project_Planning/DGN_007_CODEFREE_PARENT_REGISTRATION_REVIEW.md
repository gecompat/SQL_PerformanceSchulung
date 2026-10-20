# DGN-007 – codefreie kontrollierte Parentregistrierung

Stand: 20. Oktober 2026. Basis `4a165c20840193e26b05a789d8e6e067c0bca7b9`.
Status `C3_FIXTURE_DELTA_PRE_PENDING`; C2-Ergebnis mit Fixturefehler erhalten.

## Priorität und endlicher Umfang

PR272 ist vollständig integriert: neun finale PR-Checks und sieben frische
Main-Workflows SUCCESS, neue Harness16 und unveränderte Proxy16 ohne SKIP PASS.
Unabhängige Befundschließung, vollständiger Head-/Mergetreevergleich, sauberes
synchrones Main und eigene lokale/Remote-Branchabwesenheit bestätigt. Vier
Source/Testkandidaten erfolgreich geschlossen; kein weiterer Versuch dort.

Der noch fehlende Runnerpfad benötigt laut §33.1/33.2 des
[Importprofilvertrags](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#331-feste-zuordnung-und-prospektive-importfolge)
eine separat gewählte codefreie Registrierungsinvocation für Tests und
Tests.Contracts. Dieser abgegrenzte vorbereitende Funktionsschnitt implementiert
genau diese Komponente, bevor der vollständige Runnerloader sie anbinden kann.
Ein Implementierungsowner root, derselbe unabhängige Reviewer, höchstens vier
stabile Source/Testkandidaten, Checkpoint1, harte Grenze4 und höchstens drei
geänderte Nachläufe. Auswahl-/Source-/Test-/Deltareviews, ausdrückliche Lauf-GOs,
lokale Tests, Koordination, CI, regulärer Merge, Main-Gates, FullTree/Sync und
eigene Branchbereinigung gehören zum gemeinsamen Umfang. Verbrauch UNKNOWN.
An der harten Grenze keine neuen Kandidaten oder Umbenennung des Scopes.

## Gewählte API und Aussagegrenze

Neues eigenständiges Toolmodul mit make_codefree_parent_registry: explizit
gehaltene ModuleType-/ModuleSpec-Klassen, eigener Cache, voller Kontextdigest,
Guard- und bestätigter Writeprovider werden einmal vor Aufruf übergeben. Die
Factory liefert genau einen argumentlosen einmaligen Registrierungsaufruf.
Dieser bindet ausschließlich PARENT0/1 mit Importsequenz/Objektslot6/7 und
Originslot9/10, Ordinal1, Rawhashnull. Keine frei gewählten Namen, Indizes,
Sequenzen, Quellenbytes, Compile-/Execprovider, Finder oder Dateiauflösung.

Die expliziten Provider sind eine Komponentenschnittstelle und eigene
Vertrauensannahmen; sie sind keine operative Authority oder Attestation.
Kontextdigest wird als exakte primitive Lowerhex64 geprüft, kein vollständiger
K-Nachweis behauptet. Eine spätere tatsächliche Anbindung muss Factory/Provider
vor Reportsnapshot an die ursprünglichen Kontrollanker und den tatsächlichen
aktiven Runner-Source0-Frame vor Source6 binden. Diese Anbindung, echter
Wire-/I/O-/Budgetnachweis, vollständiger Inline-Scriptfit, Runner-/Quellen-/
Usedbytes-/Trust-/Methoden-/Gesamtgates bleiben offen. Kein Zusatzbudget.

Guard/Writer werden als ursprüngliche Pythonfunktionen samt Code-/Globals-/
Defaults-/Kwdefaults-/Closureidentitäten gehalten; Klassen und deren ursprüngliche
Rohattribute/Methodencode werden ebenfalls gehalten. Jede fremde Providerwirkung
wird durch PRE/POST umschlossen. Erneute Baseline nach Callback ist verboten.
Der Guard muss exakt None zurückgeben, der Writer ebenfalls erst nach vollständig
bestätigter Übergabe. Die Komponente selbst führt keine nativen Writes aus und
veröffentlicht keine privaten Callbackfehler. Bestätigte Bytes sind auch nach
fehlgeschlagenem POST nicht zurücknehmbar. Kein Erfolg nach Bindingverlust.

## Registrierungsfolge und Cleanup

Vor Len-/Membership-/Attributdispatch exakte Typen und primitive Keys prüfen:
Cache exaktdict, höchstens256 Einträge, Keys exakte NUL-freie UTF-8-Strings mit
höchstens4096Bytes. Fremde Objekte dürfen keine Getter/EQ/Len auslösen.
Beide Parents müssen vor Beginn abwesend sein und bis eigener Veröffentlichung
abwesend bleiben; späte Fremdbelegungen werden vor Überschreiben erkannt.

Pro Parent eigenes exaktes Modul/Spec, originNone, loaderNone, kein __file__
oder __cached__, eigene private leere PackageLocationsliste; Modul.__path__ und
Spec.submodule_search_locations halten exakt dieselbe Liste. Name/Package/Spec/
Cache und Klassenbindung werden vor und nach jedem fremden Callback geprüft.
Tests.Contracts wird als genau eigenes Kind am eigenen Tests-Modul gebunden.
Diese Bindung gehört vor dessen COMPLETE zur geprüften eigenen Invocation.

Feste Folge BEGIN P0, COMPLETE P0, BEGIN P1, COMPLETE P1. Publish und Prüfung
gehen BEGIN voraus; COMPLETE folgt erst nach tatsächlicher eigener Registrierung
und allen passenden Bindungen. Keine Compile-/Exec-/Loadercallbackinvocation.
Erfolg liefert atomar nur die zwei gehaltenen Modul-/Spec-/Locationsobjekte.
Fehler oder Reentranz sperrt die ganze Folge; Retry liefert keinen Erfolg.
Dominanter Bindingverlust vor sonstigem festem Issue. Cleanup entfernt rückwärts
nur eigene identische Cacheeinträge und die eigene identische Kindbindung;
fremde Ersetzungen, __main__ und fremde Ressourcen bleiben erhalten.

## Tests, Reviews und Integration

Zuerst unabhängiger Auswahl-PRE, dann stabiler Source/Test-PRE mit ausdrücklichem
einmaligem Lauf-GO. Eigene isolierte Module/Specs/Caches und feste Callbackmodelle;
tatsächliches sys.modules bleibt unverändert. Positive Identitäts-/Wireoracle
mit unabhängigem json.dumps, null-Hash und festen Slots; negative Primitive/
Fremdtypen, falsche Provider, ursprüngliche Code-/Closure-/Klassen-/Cache-/Spec-/
Locations-/Kindbindungsdrift, späte Fremdslots, Writefehler, Reentranz und Retry.
Tatsächlich erreichte Gegenproben, keine Zählerresets oder maskierten Fixtures.

Gezielte Windows3.14.7-/Linux3.12.3-Tests unter -I -S -B; enge neue CI nur für
Komponente, eigene Tests, Plan und Workflow. Bestehende Consumer unverändert,
keine Wiederholung ihrer grünen lokalen Tests. Vor jedem Commit Privacyprüfung
aller geänderten Dateien; zentraler CI-Vollscan bleibt einmalig. Danach aktuelle
grüne Head-/Base-Gates, regulärer Merge, frische Main-Gates, FullTree/Sync und
sicherer eigener lokaler/Remote-Branchcleanup. Keine nativen Worker, reale
DGN-Raw-, Installations-, SQL- oder sonstigen externen Wirkungen.

Primärquellen, geprüft am20.Oktober2026: Das
[Python-Importsystem](https://docs.python.org/3.12/reference/import.html#loading)
behandelt Namespacepackages ohne reguläre Sourceexecution.
[ModuleSpec](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec)
beschreibt Origin und PackageLocations; Modul- und Specattribute müssen separat
geprüft werden. Die engere codefreie Registrierung bleibt Projektvertrag.

## Auswahl-GO und C1

Plancommit b75eded84ac706cea402169383f4b5f77af80d05 unabhängig freigegeben,
mit zwei verbindlichen Präzisierungen: Kindslot Contracts am eigenen Tests-Modul
vor eigener Bindung abwesend, danach exakt gehaltenes eigenes Kind; späte fremde
Kindbelegung ablehnen und erhalten. Providerzustände vor Fremddispatch begrenzen,
Kwdefaults-Einträge und Closurezellinhalte zusätzlich zu Containeridentitäten
halten. Mutable Inhalte hinter gehaltenen Objekten bleiben Vertrauensannahmen.
Keine transitive Providerattestation; None bestätigt nur den Providervertrag.

C1 ergänzt Factory und zwölf isolierte Methoden. Providergrenzen32 Defaults/
Kwdefaults/Closurezellen, Namespace256 und Klassenrohattribute128; exakte Typen/
primitive Keys vor Vergleich/Dispatch. Eigene Modul-/Spec-/Locations- und
Kindbindung werden durchgehend geprüft. Fremde Callbacktexte bleiben privat.
Cleanup dispatcht nur in noch primitiven begrenzten eigenen Dictionaries;
bei fremden unzulässigen Keys bleibt der nicht sicher bereinigbare Zustand
abgelehnt, ohne behaupteten vollständigen Ressourcenabschluss.

Testoracles verwenden tatsächliche eigene Module/Specs und getrennte Caches,
unabhängige kanonische JSONbytes, erreichte späte Cache-/Kind-/Spec-/Locations-/
Klassen-/Code-/Kwdefaults-/Closureänderungen, Fehler/Returnwerte, Reentranz und
Retry. Eigener ursprünglicher sys.modules-Stand wird je Methode auf Keys und
Objektidentitäten geprüft. Kein Compile/Exec/Finder oder nativer I/O-Call in der
Komponente; ein AST-Negativcheck belegt diesen engen strukturellen Claim.

Checkpoint1: ein Source/Testkandidat/max4, keine Nachläufe, Verbrauch UNKNOWN.
Nur Text-AST-Syntaxprüfung vorgesehen; kein Kandidatenimport oder neue Probe.
Unabhängiger Source/Test-PRE und ausdrückliches einmaliges Windows-/Linux-
Lauf-GO ausstehend. Danach enge CI mit genau vier eigenen Abhängigkeiten;
keine alten Consumer betroffen, keine doppelten lokalen grünen Suites oder
Privacyvollscans. Ein Owner/ein Reviewer, begrenzte private Logs. Erforderliche
frische Head-/Base-/Main-Gates und vollständiger Integrationsabschluss bleiben.

## C2 – begrenzte Erfassung vor Kopie und dominante Guardoracle

C1 2f58dc10f57755f1d29899365a1957f0a1508330 unabhängig mit zwei P3 ohne
Lauf-GO: Klassenmapping vor Kopie begrenzen; die dauerhaft falsche Guardrückgabe
scheitert auch beim abschließenden close und muss deshalb BINDING erwarten.
Keine offenen P1/P2, keine Kandidatenimporte oder Ausführung.

C2 prüft exakten Mappingproxytyp, maximal128 Einträge und primitive begrenzte
Keys vor dict(view). Eine tatsächlich erreichte zusätzliche Klassenmutation
nach dem ersten BEGIN überschreitet diese Grenze; dieselbe Methode prüft
BINDING, ein bestätigtes Recordbytepräfix und eigene sichere Bereinigung,
danach exakte Rücknahme aller eigenen synthetischen Klassenattribute.
Guard-False erwartet ausschließlich den korrekten dominanten BINDING-Issue.
Weiterhin zwölf Methoden, keine schwächere Oracle. Zwei Kandidaten/max4,
ein Nachlauf, Verbrauch UNKNOWN. Gezielter unabhängiger Delta-PRE und
ausdrückliches einmaliges Lauf-GO weiter erforderlich; keine Probe bisher.

## C2-Ergebnis und C3-Fixturekorrektur

C2 ac908b36e94c9d94cbb16e9088bc5cf582ad823a unabhängig ohne offene Befunde
mit einmaligem Lauf-GO. Zwölf Methoden Windows3.14.7/0.126s und
Linux3.12.3/0.116s: jeweils genau ein FAIL, übrige elf PASS, kein SKIP.
Fehler ausschließlich im tearDown der strukturellen AST-Methode: ihr eigener
read_text(encoding='utf-8-sig') lädt encodings.utf_8_sig nach. Die strenge
ursprüngliche Modulcache-Key-/Identitätsoracle erkennt dies korrekt. Kein
Produktfehler oder privater Ressourcenrest; isolierte Testprozesse beendet.

C3 ändert ausschließlich diesen Fixturezugriff zu read_bytes; ast.parse erhält
die ursprünglichen eigenen Sourcebytes. Keine zusätzliche Importbaseline,
Whitelist, Rücknahme fremder Module oder Abschwächung der Cacheoracle. Produkt
und übrige elf Methoden unverändert. Drei Source/Testkandidaten/max4, zwei
Nachläufe, Verbrauch UNKNOWN. Enger unabhängiger Fixture-Delta-PRE und gezieltes
einmaliges Lauf-GO nur für die fehlgeschlagene Methode je Plattform erforderlich.
Elf unveränderte grüne lokale Methoden werden nicht wiederholt; volle zwölf
bleiben frische erforderliche CI-/Main-Gates.
