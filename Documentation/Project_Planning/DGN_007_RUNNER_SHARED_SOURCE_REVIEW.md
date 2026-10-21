# DGN-007 – Quellenprüfung der vollständigen Runnerroute

## C8 fortgesetzt: vertrauenswürdige Quellen nach DEC-076

Der Mensch hat am 21. Oktober 2026 die offene Vertragsfrage ausdrücklich
entschieden: vertrauenswürdige Schulungsquellen; gezielte Kontrollmanipulationen
sind vom Prüfversprechen ausgeschlossen. [DEC-076 im Kontrollvertrag](DGN_007_RUNNER_SHARED_CONTROL_DESIGN.md#vertrauensmodell-für-schulungsquellen-dec-076)
präzisiert diese Grenze und erhält die Daten-/Provider-/Reihenfolge-/Identitäts-/
Budget-/Fehler-/Cleanupanforderungen. Die historischen Auswahl-No-GOs unten
bleiben als Befunde des früheren stärkeren Manipulationsmodells erhalten.

Fortsetzung des unverbrauchten einzelnen C8, kein neuer Versuch oder Reset:
Basis 4e738ae nach vollständig abgeschlossenem PR279, ein Owner root und derselbe
unabhängige Reviewer. Bisher sieben Kandidaten/sechs geänderte Nachläufe,
Verbrauch UNKNOWN; ein stabiler C8 erreicht acht/hartacht und sieben Nachläufe.
Kein C9. Der gemeinsame Rahmen umfasst Vertragskorrektur, Auswahl, Umsetzung,
alle Reviews, Koordination, lokale Tests, CI (Continuous Integration;
automatisierte Integrationsprüfungen), reguläre Integration und eigene Bereinigung.

### Konkrete Auswahl und Prüfversprechen

Die bisher inline vervielfältigten Checkpoints werden einmal als gemeinsamer
Python-Helfer vor Reportsnapshot definiert. Unter der ausdrücklich gewählten
Vertrauensannahme darf dieser ursprüngliche Helfer als Kontrollcode aufgerufen
werden; er behauptet keine Selbstabsicherung gegen vorher veränderten eigenen
Code. Die tatsächlich ausgeführten PRE-/finally-POST-Stellen bleiben bestehen.
Aktive Frames halten Kontext, Primitiven und D1-Record lokal; D1 bezeichnet den
vor Reportsnapshot einmal versiegelten Zustand.

Ursprüngliche Primitiven werden bei Initialisierung getrennt vom zu prüfenden
`_kernel`-Kontext gehalten und an die Wrapper/Fabrik übergeben. Der gemeinsame
Checkpoint erhält beide gehaltenen Referenzen ausdrücklich. Zuerst prüft er
Kontexttyp, Länge und Identität des primitiven Teilankers; erst danach verwendet
er Kontextfelder. Die C7-Kontextkopie mit fremdem Feld0 darf keinen Iterator
aufrufen. Das ist eine gezielte Integritätsdiagnose unter vertrauenswürdigem
Kontrollcode, kein wieder eingeführtes Versprechen gegen gleichzeitiges Fälschen
aller Kontrollanker. Ganze Root-/Input-/Providerprüfungen und endliche
Versiegelung bleiben vorhanden. Es gibt keine späte Baseline oder Rawauslassung.

Die unabhängige Ganz-AST-Oracle (AST: Abstract Syntax Tree; abstrakter Syntaxbaum)
rekonstruiert den einmaligen festen Checkpoint und seine tatsächlichen Aufruf-
und Framebindungen getrennt vom produktiven Transformationshelfer. Alle übrigen
fest ausgewählten Source-/Parent-/Inputknoten bleiben vollständig. Die eigenen
positiven und negativen Modelle einschließlich tatsächlich erreichter Daten-/
Provider-/Cache-/Child-/Write-/Limit-/Fehlerfälle bleiben erhalten. Fälle mit
Code-/Closure-/Defaultaustausch sind ausschließlich begrenzte Diagnosefälle.
Kein allgemeiner Foreignoperations- oder Manipulationssicherheitsclaim für
gezielt veränderten Kontrollcode.

### Checkpoints, Aufwand und harte Grenze

Vor Umsetzung unabhängige Auswahl-/Vertragsprüfung. Danach genau ein stabiler
Quellen-/Teststand und unabhängiger PRE vor Kandidatenimport, Generierung,
Kompilierung oder Ausführung. Nur ausdrückliches gestuftes Lauf-GO erlaubt
Fit/Ganz-AST genau einmal auf Windows 3.14.7/Linux 3.12.3 mit -I -S -B; nur
beidseitiges vollständiges PASS erlaubt die übrigen eigenen Modelle einmal je
Plattform. Ein weiterer notwendiger Quellen-/Fixturefix nach stabilem C8 oder
ein Fitfehler bedeutet STOP, sichere Disposition und regulären Abschluss;
kein C9 oder Capanhebung. Reale DGN-Bodies, native Worker und SQL werden nicht
ausgeführt. Ergebnisreview und aktuelle grüne Head-/Base-/Main-Gates bleiben
vor Abschluss erforderlich.

Aufwandsbewertung dieser Vertragskorrektur: ein Implementer, derselbe unabhängige
Reviewer mit getrennten Auswahl-, Quellen-/Test- und Ergebnisfragen; keine
zusätzliche Modellkette. Die gemeinsame Funktion vermeidet vervielfältigten
Kontrollcode, keine Sicherheitsdatenprüfung. Unveränderte alte lokale Suiten
werden nicht wiederholt; die neue enge CI-Suite enthält sämtliche direkten und
transitiven Abhängigkeiten und führt ihre positiven/negativen Modelle aus.
Lokale und CI-Läufe bleiben mangels geschützter Evidenzanerkennung getrennte
Nachweise. Verbrauch UNKNOWN; keine behauptete Einsparungsmessung. Neue globale
Regel-/Registryänderungen durchlaufen zusätzlich die regulären Governance-Gates.

Auswahl-/Vertrags-GO an 408691b ohne offene priorisierte Befunde erteilt.
Der jetzt stabil vorgelegte C8 enthält 20 Methoden: eine Fit-/Ganz-AST-Methode
und 19 eigene synthetische Modelle beziehungsweise begrenzte Diagnosen. Der
gezielte C7-Feld-0-Fall hält seinen Reachedmarker außerhalb des Kandidaten und
verlangt null Fremdoperationen. Genau ein gemeinsam genutzter Checkpoint und
alle Callassignments/Frameprefixe werden vollständig rekonstruiert. Die übrige
C7-Semantik benötigt weiterhin den vollständigen unabhängigen Quellen-/Test-PRE.

Damit sind acht/hartacht Quellen-/Testkandidaten und sieben geänderte Nachläufe
erreicht, Verbrauch UNKNOWN. Quellen-/Test-GO sowie jedes Generierungs-/Lauf-GO
sind noch offen. Bisher kein Kandidatenimport, keine Generierung, AST-Analyse,
Kompilierung, Ausführung oder Modelle. Eigener Branch
`codex/dgn007-trusted-sources-c8`. Die alte ABI-Auswahlsperre wird nur durch die
hier ausdrücklich getroffene Vertragsentscheidung behandelt.

## C8: ausdrückliche Freigabe zur Bootstrap-Korrektur

Am 21. Oktober 2026 hat der Mensch genau einen weiteren stabilen C8
(den achten Quellen-/Testkandidaten) zur Bootstrap-Korrektur freigegeben.
Ausgangsbasis ist 095c813605bec4ce4e06ebfdf6652cbc8370565a nach abgeschlossenem
[PR278](https://github.com/gecompat/SQL_PerformanceSchulung/pull/278).
Ein Implementierungsverantwortlicher root und derselbe unabhängige Reviewer;
Auswahl, Umsetzung, Quellen-/Testprüfung, Koordination, lokale Tests, CI
(Continuous Integration; automatisierte Integrationsprüfungen), Integration
und sichere Bereinigung gehören zu diesem gemeinsamen Schnitt. Verbrauch
UNKNOWN. Bisher sieben Kandidaten/sechs geänderte Nachläufe; mit stabilem C8
höchstens acht Kandidaten/sieben geänderte Nachläufe. Kein C9 oder Reset.

Der konkrete Schnitt korrigiert ausschließlich die vor jedem Kontextzugriff
fehlende unabhängige ursprüngliche Bootstrapautorität aus C7 und ergänzt die
passende tatsächlich erreichte Gegenprobe: vor Aufruf ersetzte 17-elementige
Kontextkopie mit fremdem Feld0 samt Iterationssentinel. Eine zweite veränderbare
Zelle mit bloßer Formprüfung wäre keine Lösung. Ursprüngliche Primitiven und
ursprünglicher Kernel samt vollständigen Metadaten müssen unabhängig vom zu
prüfenden Kontext gehalten und vor dessen Verwendung geschlossen werden.
Aktive Frames behalten ihre ursprünglichen Referenzen über Callbacks hinweg.
Der vollständige DESIGNED-Vertrag bleibt unverändert; die übrigen C7-Änderungen
sind wegen dessen frühem STOP weiterhin nicht vollständig abgenommen.

Checkpoint vor Umsetzung: genau eine konkrete Auswahl unabhängig prüfen.
Danach genau ein stabiler Quellen-/Teststand und unabhängiger PRE (Prüfung
vor dem Lauf) vor jedem Kandidatenimport, jeder Generierung, AST-Analyse
(Abstract Syntax Tree; abstrakter Syntaxbaum), Kompilierung oder Ausführung.
Nur ausdrückliches gestuftes Lauf-GO erlaubt die Fit-/Ganz-AST-Methode jeweils
einmal auf Windows 3.14.7 und Linux 3.12.3 mit -I -S -B. Nur beidseitiges PASS
erlaubt einmal die übrigen ausgewählten eigenen synthetischen Modelle je
Plattform. Kein nativer DGN-Body, Worker oder SQL-Lauf; keine Capanhebung oder
Rawauslassung. Bei weiterer notwendiger Quellen-/Fixturekorrektur nach dem
stabilen C8 oder fehlgeschlagenem Fit: kein C9, sondern sichere Disposition
und belegter regulärer Abschluss. Nach erfolgreichem Ergebnisreview folgen
aktuelle Head-/Base-Gates, regulärer Merge, frische Main-Gates, vollständige
Übernahme, Sync und sichere Bereinigung genau des eigenen Branches.

### Unabhängiges Auswahl-No-GO: synchroner ABI-Einstieg

Auswahlbindung 841b3953ec96eb7cd01b5a9ac70e56e3efcce9b4: Der unabhängige
Reviewer bestätigt einen konkreten ABI-/Trustblocker (ABI: Application Binary
Interface; hier die feste Aufrufschnittstelle des Python-Importmechanismus).
Status BLOCKED_SELECTION_ABI_TRUST. Noch kein C8-Quellenfreeze und kein Lauf-GO;
C8 ist als Quellen-/Testkandidat nicht verbraucht. Der tatsächliche Verbrauch
bleibt sieben Kandidaten/sechs geänderte Nachläufe, UNKNOWN.

Ein ursprünglicher Controllerframe könnte Primitiven, vollständige Kernelpins
und ursprünglichen Inputframe von der Initialisierung bis zum Fehlerabschluss
lokal halten und vor eigenen Dispatchs ausdrücklich weitergeben. Das reicht
für die synchrone Importkante nicht: Während der Controller in `exec` wartet,
kann der Sourcebody direkt den Python-Importmechanismus auslösen. Dessen
`__import__`-Aufruf hat keine zusätzlichen Autoritätsargumente des Controllers.
Wählt das Gateway sie aus Closure, Defaults oder Globals, bleibt der erste
Zugriff unbewiesen. Eine lokale Kopie entsteht erst nach diesem Zugriff.

Bereits der Gatewaydispatch müsste dominant geschützt sein. Wird der Python-
Gatewaycode vor dem ABI-Einstieg geändert, kann seine eigene Prüfung vollständig
entfallen. Ein äußerer finally-POST erkennt die Änderung erst nach möglichen
Wirkungen. Dasselbe Problem betrifft entsprechende Loader-Dispatchs. Eine
zweite Kontextzelle, ein weiterer Python-Wrapper oder ein zusätzlicher
Kontextspeicher liefern für sich keine unveränderbare Vertrauenswurzel.

Der gewählte unveränderte DESIGNED-Vertrag verlangt diese ursprüngliche
Bindung vor Dispatch. Eine vollständige Übergabekette ist für die ABI-Kante
nicht belegt. Neue Runtimevermittlung oder eine bewusste Einschränkung des
Manipulationsmodells wären Vertrags-/Architekturänderungen; die C8-Freigabe
entscheidet keine dieser Alternativen und wird dafür nicht umgedeutet.

### Entscheidung und sichere Disposition

Zur Wiederaufnahme ist eine ausdrückliche fachliche Entscheidung nötig:

- Das Manipulationsmodell für vertrauenswürdige Schulungsquellen und die
  synchronen ABI-Einstiege begrenzen. Die dann tatsächlich bewiesene Integrität
  und verbleibenden Grenzen müssten präzise im Vertrag und in Tests stehen;
  keine Sandbox-, Host- oder Trustattestation daraus ableiten.
- Einen vor dem ABI-Einstieg wirksamen, unabhängig vertrauenswürdigen Vermittler
  als gesonderten Architektur-/Runtimescope auswählen und qualifizieren. Ein
  weiterer ungeschützter Python-Wrapper wäre dafür kein Nachweis.

Bis zu dieser Entscheidung keine Umsetzung, kein Quellenfreeze, kein Import,
keine Kandidatengenerierung, AST-Analyse, Kompilierung, Ausführung oder Modell-
beziehungsweise Fitlauf. Es gibt keine neuen Source-/Test-/Workflowdateien im
finalen Diff. Historische C7-Quellen wurden ausschließlich privat aus ihren
Gitbytes gelesen; private Evidence, bestehende Komponenten und fremde Ressourcen
bleiben erhalten. Der DESIGNED-Vertrag wird durch diesen Diagnoseeintrag nicht
geändert. Sämtliche Runtime-/Trust-/Usedbytes-/Methoden-/SESSION_END-/SQL-Gates
und das Scriptlimit bleiben offen beziehungsweise unverändert.

Der reine Auswahl-/Diagnoseabschluss gehört zu
[PR279](https://github.com/gecompat/SQL_PerformanceSchulung/pull/279), eigener
Branch `codex/dgn007-runner-c8`. Der dortige Abschlussnachweis bindet die
unabhängige Disposition, lokale Dokumentationsprüfung, aktuelle Head-/Base-Gates,
den regulären Merge, frische Main-Gates, vollständige Übernahme, Synchronisation
und eigene lokale/Remote-Branchbereinigung an die tatsächlich belegten Ergebnisse.
Ein unveränderter Heartbeat startet weder dieselbe Auswahlprüfung erneut noch
einen Quellenversuch.

## C7: abgelehnt; erweiterte harte Grenze erreicht

Stand: 21. Oktober 2026. Ausgangsbasis 347c231bcc5d5318a779100e0677cde2e49e3adb
nach abgeschlossenem [PR277](https://github.com/gecompat/SQL_PerformanceSchulung/pull/277).
Status CLOSED_REJECTED_C7_PRE: Der stabile Quellen-/Testkandidat
559f09cc35dd22a2fd073641401c23517114e031 wurde unabhängig vor jeder Generierung
abgelehnt. Es gab keinen Kandidatenimport, keine Generierung, keinen Fitlauf,
keine AST-Analyse (Abstract Syntax Tree; abstrakter Syntaxbaum), Kompilierung,
Ausführung oder Modelllauf. Größenfit und übrige Befundschließung sind unbekannt.
Die Prüfung endete am zwingenden STOP; es liegt keine vollständige Abnahme vor.

### Freigabe und gemeinsamer Verbrauch

Der Mensch hat am 21. Oktober 2026 genau einen weiteren stabilen Kandidaten C7
(den siebten Quellen-/Teststand)
freigegeben: Korrektur der drei C6-Befunde und der UTF-8-Textkorruption, passende
Negativfälle, unabhängiges Review, lokale Tests, grüne Gates, regulärer Merge
und eigene Branchbereinigung. Ein Implementierungsverantwortlicher root und
derselbe unabhängige Reviewer. Der gemeinsame Rahmen umfasst Auswahl,
Umsetzung, Quellen-/Testprüfung, Koordination, lokale Prüfungen, CI (Continuous
Integration; automatisierte Integrationsprüfungen), Integration und Bereinigung.
Quellen-/Versuchsverbrauch UNKNOWN; sieben/hartsieben stabile Kandidaten und
sechs geänderte Nachläufe sind erreicht. Keine erfundene Verbrauchsmessung.

Unabhängiges Auswahl-GO auf Basis 347c231 erlaubte die Umsetzung, aber keinen
Lauf. Vor Generierung war ein stabiler Quellen-/Test-PRE (unabhängige Prüfung
vor dem Lauf) mit ausdrücklichem gestuftem Lauf-GO erforderlich: zuerst die
Fit-/Ganz-AST-Methode jeweils einmal auf Windows 3.14.7 und Linux 3.12.3 mit
-I -S -B; nur beidseitiges PASS hätte einmal die übrigen eigenen Modelle je
Plattform erlaubt. Die Interpreterversionen wurden lesend bestätigt. Wegen
des Quellenbefunds wurde keine dieser Methoden gestartet.

### Konkreter unabhängiger Befund

P2 – Der Bootstrap übernimmt seine Primitiven erneut aus einer veränderbaren
Closurezelle. Im verworfenen Stand prüft die Callfunktion `_kernel` lediglich
auf exaktes Tuple und Länge 17 (Sourcezeile 500). Der eingefügte Frameprefix
übernimmt diesen Zellinhalt; der Checkpoint entpackt dessen Feld 0 vor dem
ursprünglichen Kernelcheck (Sourcezeile 720).

Statischer Gegenfall: Vor dem Aufruf wird die `_kernel`-Zelle durch eine
17-elementige Kontextkopie ersetzt, deren Feld 0 ein fremdes Objekt mit
Iterationssentinel enthält. Die Vorprüfung passiert; das Entpacken würde den
fremden Iterator aufrufen. Eine spätere feste Ablehnung beseitigt die bereits
erfolgte Fremdoperation nicht. Die neue Closuregegenprobe verändert `_kernel`
erst während Parent-BEGIN (Testzeile 901); dieser Einstiegspfad fehlt.

Erforderlich wäre eine vor Kontextzugriff unabhängig gebundene ursprüngliche
Kontext-/Primitivenautorität und eine Gegenprobe genau dieses Einstiegspfads.
Das verlangt einen weiteren Quellen-/Fixturefix. Der unabhängige Review hat
559f09c deshalb ausdrücklich ohne Fit-GO abgelehnt und am STOP beendet.
Die übrigen C7-Änderungen sind damit weder vollständig geprüft noch freigegeben.

### Sichere Disposition und Abschluss

Der verworfene Stand enthielt eine neue Runnerquelle, 19 eigene Testmethoden
(eine Fit-/Ganz-AST-Methode und 18 synthetische Positiv-/Negativmethoden) und
einen engen Workflow. Diese drei neuen Dateien sind aus dem finalen Diff
entfernt. Vorhandene Workerinput-, Proxy-, Harness- und Parentkomponenten samt
Tests bleiben erhalten. Kein nativer DGN-Body, Worker oder SQL-Lauf wurde
hierdurch gestartet; keine Plattform-, Trust-, Methoden- oder SQL-Freigabe.
Das unveränderte Scriptlimit 131072 und der volle Rawumfang werden nicht
abgeschwächt. Größenersparnis und Laufzeitverhalten bleiben unbekannt.

Der abgelehnte Commit ist vor dem Entfernen in einem privaten, lokal geprüften
vollständigen Gitbundle gesichert. Private Evidence und fremde Ressourcen
bleiben erhalten. Die Versionshistorie ist kein ausführbarer Freigabestand.
Der [DESIGNED-Vertrag](DGN_007_RUNNER_SHARED_CONTROL_DESIGN.md) bleibt unverändert.
Der reine Diagnoseabschluss gehört zu
[PR278](https://github.com/gecompat/SQL_PerformanceSchulung/pull/278), eigener
Branch `codex/dgn007-runner-c7`. Der dortige Abschlussnachweis bindet den
unabhängigen Dispositionsreview, lokale Dokumentationsprüfungen, aktuelle
Head-/Base-Gates, reguläre Integration, frische Main-Gates, vollständige Übernahme
und sichere eigene Branchbereinigung an die tatsächlich belegten Ergebnisse.

Nächste Quellenarbeit ist blockiert. Kein C8, kein Budget-/Scope-/Namensreset
und kein weiterer Lauf innerhalb dieser Freigabe. Eine Wiederaufnahme benötigt
eine ausdrückliche neue begrenzte Entscheidung zur vor Kontextzugriff tragfähigen
Bootstrap-Korrektur sowie erneut unabhängige Auswahl-/Quellen-/Testprüfung und
Lauf-GO. Unveränderte Heartbeats starten keine Wiederholungsanalyse. Tatsächliche
Runtime-, Trust-, Usedbytes-, Methoden-, SESSION_END- und SQL-Gates bleiben offen.

## Historischer C6-Auswahl- und Ablehnungsstand

Stand: 21. Oktober 2026. Basis750844bbfe61f6b12c98354c034ea3441abbde91.
Status CLOSED_REJECTED_C6_PRE. Auswahl37f27e4 war unabhängig freigegeben;
C6 d0470fc ist im Source-/Test-PRE abgelehnt. Keine Generierung oder Ausführung.

## Abschluss und verbleibender gemeinsamer Rahmen

[PR275](https://github.com/gecompat/SQL_PerformanceSchulung/pull/275) ist regulär
integriert: sieben finale Head-/sechs Base-/fünf frische Main-Gates SUCCESS,
unabhängiger Design-/Deltareview, FullTree/Sync und eigene lokale/Remote-
Branchabwesenheit bestätigt. [DESIGNED-Vertrag](DGN_007_RUNNER_SHARED_CONTROL_DESIGN.md)
bleibt unverändert; seine zwei/hartzwei Entwurfsstände sind geschlossen.
Dieser konkrete Auswahlplan zielte auf seine Implementierung, ohne dritte
Designnacharbeit. Der unten gebundene C6 ist inzwischen verworfen.

Vor C6 waren fünf von sechs Source/Testkandidaten und vier geänderte Nachläufe
verbraucht. Der stabil vorgelegte C6 erreicht sechs/hartsechs sowie fünf
geänderte Nachläufe, Verbrauch UNKNOWN. Genau dieser letzte stabile C6-
Source/Testkandidat, ein Implementierungsowner root und derselbe unabhängige
Reviewer. Auswahl-/Source-/Test-/Befundreviews, Koordination, lokale Tests,
CI (Continuous Integration; automatisierte Integrationsprüfungen), Integration, frische Main-Gates, FullTree/Sync und eigene Branchbereinigung
zählen gemeinsam. Kein siebter Kandidat oder sechster geänderter Nachlauf.
Bei Source/Testbefund, Fit-/Modell-/CIfehler mit notwendiger Code-/Fixturekorrektur
nach diesem stabilen C6 gilt die harte Grenze; keine Reparatur unter neuem Namen,
kein weiterer Quellen-/Versuchsrahmen ohne echte Entscheidung.

Auswahl-PRE37f27e4 war unabhängig freigegeben. Vor einem Lauf war Source/Test-PRE
verpflichtend;
keine Kandidatenimporte, Generierung, Compile/Exec oder Modelle davor. Auch die
verbleibende eine Version rechtfertigt keinen ausgelassenen Prüfschritt.

## Konkrete additive Komposition

Eigene Dateien Tests/Tools/dgn007_runner_loader_source.py,
Tests/Static/test_dgn007_runner_loader_source.py und enger gleichnamiger neuer
CI-Workflow. Vorhandene Workerinput-/Proxy-/Harnessgeneratoren, Parentfactory
und deren Tests bleiben unverändert. Die verworfenen Kandidaten sind ausschließlich
gelesene historische Source-/Testentwürfe aus PR274, keine bereits zugelassene
Implementierung oder Modellabnahme. Neue Sourceauswahl ist vollständig zu prüfen.

Unveränderter Workerinputunterbau, sechs genau bezeichnete Proxyguard-/Writer-/
Exec-/Spec-/Namespace-/Bindingadapter und vollständiges festes Runnerimporttemplate.
Alle Source-/Inputfunktionen bleiben erhalten. Keine SESSION_END-Auslassung,
keine generische Deadcode-/Präfixkürzung, keine Runtime-Quellenkompression und
kein zusätzliches Controlcompile. Standalone-Parentfactory wird ausdrücklich
nicht eingebettet/aufgerufen. Keine Behauptung ihrer ursprünglichen Codeidentität
in der alternativen Route. Ganze acht Sources/zwei Parents/same20 Records aus §33.

Eine gemeinsame private Objektaufnahme unterstützt Module-/Spec-Teilergebnisse
für Sources und Parents, damit die tatsächlichen Rückgaben bereits vor dem
nächsten äußeren Aufruf gehalten werden. Endliche Zustände aus dem DESIGNED-
Vertrag, keine dynamische Baseline. Parentobjekte benutzen ausschließlich die
vorher gehaltenen Rootklassen, den selben Cache, denselben Writer/K-Digest und
dieselben Budgethalter. Source-/Parentbinder prüfen ihre jeweilige vollständige
Form und alle ausstehenden/eigenen Cache-/Childslots dominant in jedem Rootguard.

Rootowner ist vor Reportsnapshot einmal als ursprünglicher unveränderlicher
Tupleanker im eigenen Scriptnamespace gehalten. Bootstrap hält primitive Referenzen
vorher, prüft Namespace-/Builtins-/Keyformen vor Lookups und tatsächliche Owner-
Identität vor Vertrauen auf einen übergebenen Zustand. Sämtliche veränderbaren
Helper-/Kernel-Funktionen werden an ursprüngliche vollständige Zustände gebunden
geprüft, bevor sie aufgerufen werden. Alle Closurehelfer entstehen vor Snapshot,
keine späte Graphaufnahme oder Factory-/Run-/Namespacekopie. ActualEOF/K-Digest
werden nur einmal im vorherigen privaten Datenhalter aufgenommen.

Guards und Parentcheck bleiben getrennte Rollen: Parentcheck ruft nicht Rootguard
zurück. Endliche PRE/POSTs bei Konstruktor/Writer/Compiler/Exec/Importer einschließlich
Exception und falscher Rückgabe. Aktiver ursprünglicher Fehlerframe hält sichere
Primitiven selbst und dispatcht keine möglicherweise mutierten Cleanuphelper.
Bindungsverlust dominiert, sticky Fehler/Retry und rückwärtiger eigener
identitätsbezogener Cleanup bleiben gemäß Entwurf verpflichtend.

## Unabhängige Source-/Testabnahme

Fitvorstufe mit tatsächlichem vollständigem CRLF- und LF-Profilraw, fünf direkten
Importen und131072Cap. Unabhängige Oracle rekonstruiert den ganzen unveränderten
Input-/Adapter-/neuen festen Runnertemplate-AST getrennt; kein Aufruf produktiver
Kompositions-/Auswahl-/Alphahelfer. Neue Parent-/Objekt-/Bootstraprollen sind
Teil dieses fest ausgewählten Templates und separat auf den DESIGNED-Vertrag
zu prüfen. Keine bloße ASTgleichheit als Ersatz für dessen semantische Prüfung.

Konservative globale/lokale Alpha-/Rawliteralpässe nur mit vollständigen inversen
AST-/Literalnachweisen. Externe Helper-/Fixture-/Callbacknamen und tatsächliche
co_freevars['owner'] bleiben geschützt; reine Deklarationen, Keywords, Attribute,
Reflexion und globale Ursprünge bleiben gesperrt. Keine weitere Namenskürzung
ohne geprüften inversen Nachweis. Profilraw bleibt ein einzelnes wertgleiches
Bytesliteral, keine Inlinekodierung oder Änderung seiner ursprünglichen Bytes.

Zuerst ausschließlich Fit-/Ganz-AST-Methode je einmal Windows 3.14.7/Linux 3.12.3
mit -I -S -B nach ausdrücklichem Source/Test-GO. Die eine Fitmethode darf bei
SCRIPT_LIMIT ausschließlich im eigenen verworfenen Generatorframe Quellenlänge/
Exzess aggregieren und dann unverändert fehlschlagen; kein separater Nachlauf,
keine verworfene Quelle speichern/ausgeben/kompilieren/ausführen.
Erst beidseitiges vollständiges PASS erlaubt einmal die restlichen ausgewählten
eigenen Modelle je Plattform. Kein erneuter lokaler Fit in derselben Suite.

Erforderliche positive/negative Modelle: volle20 bestätigte Wire-Records,
acht Raw-/Code-/Namespaceidentitäten, tatsächliche verschachtelte Rückkehr,
gemeinsame Objektaufnahme und tatsächlicher Root0→6-Parentpfad, vollständige
Metadaten/Childlinks. Guard-/Kernel-/Closure-/Builtin-/Klassen-/Spec-/Encoder-/
Providerdrifts müssen vor veränderbarem Helperdispatch beziehungsweise als
dominante POSTs tatsächlich erreicht werden. Module-returned/Spec-missing,
Spec-returned/noch unvorbereitet, Veröffentlichung, Childlink und laufende/
teilweise/voll bestätigte BEGIN/COMPLETE benötigen eigene Reachedmarker.
Fremdtypen dürfen keine Getter-/Hash-/Equality-/Len-/Callsentinels erreichen.
Zusätzlich falsche Rollen/EOF (End of File; Ende eines Eingabestroms), späte fremde Slots, falsche Typen/Fromlists,
ursprüngliche Writerteilrückgaben/-fehler, Limits, Reentranz/Retry und sichere
eigene Bereinigung bei normalem sowie beschädigtem Cache. Kein Raw-DGN-Body
oder anderer operativer/nativer Prozess in diesen Modellen.

Neue enge CI führt die vollständig ausgewählte neue Suite mit allen tatsächlichen
direkten/transitiven Abhängigkeiten aus. Alte grüne lokale Suiten nicht wiederholen.
Nur nach unabhängig geschlossenen Befunden und aktuellen Head-/Base-Gates
regulärer Merge; danach frische Main-Gates, vollständige Übernahme, Sync und
sichere eigene lokale/Remote-Branchbereinigung. Fremde Ressourcen/Evidence erhalten.

## Offene Gates

Auswahl-PRE37f27e4 GO, insbesondere private ursprüngliche Owneridentität und
Gegenprobe einer ersetzten Ownerkopie mit unveränderten Checkerfunktionen.
Source/Test-PRE für C6 No-GO; kein Generierungs-/Lauf-GO. Tatsächliche
Größenersparnis und Fit unbekannt. Source/Teststand sechs/hartsechs;
kein weiterer geänderter Code-/Fixturekandidat ohne Entscheidung.
Alle tatsächlichen DGN-Raw-/Worker-/EOF-/Exit-/Cleanup-/Trust-/Usedbytes-/
Methoden-/SQL- und Gesamtgates bleiben offen. Kein Quellen-/Scope-/Budgetreset.

## Beabsichtigter stabiler C6 vor Source-/Test-PRE

Die folgenden Absätze halten den vorgelegten Entwurf und die ausgewählten
Oracles fest. Sie sind keine bestätigte Implementierung; die nachfolgenden
P2-Befunde widerlegen insbesondere Bootstrap- und Cleanupannahmen.

Die additive Quelle verwendet einen ursprünglichen privaten Rootowner-Tuple,
einen vor Reportsnapshot gebildeten Bootstrap und vollständige Funktionspins.
Sechs effektführende Adapter erhalten ihren ursprünglichen Guard über vorher
erzeugte Wrapper; feste Checkpointstellen werden als ausgewähltes ASTtemplate
eingefügt. Der Bootstrap prüft primitive Namespace-/Builtinsformen, tatsächliche
Owneridentität, vollständige Helperzustände und ursprünglichen Kernel vor dem
reinen Root-/Parentbinder. Ursprüngliche Zustandslisten bleiben identisch.
Die alternative Route bettet die Standalone-Parentfactory nicht ein.

Gemeinsame21-Feld-Invocation für Sources/Parents hält Module und Specs sofort,
noch vor Partnerkonstruktion oder POST. Konstruktorphasen0–6 und beide
Recordphasen0–4 mit bestätigten Offsets sind ausdrücklich dargestellt.
Writer/Compile/Exec/Importer erhalten finally-POSTs. Der aktive Entryframe hält
Cleanupprimitiven und ursprüngliche Source-/Parentlisten vor äußeren Effekten.
Nur primitive Cachekeys und identische eigene Werte erlauben Löschung; bei
beschädigtem Cache wird kein vollständiger Cleanup behauptet.

Sechzehn eigene Testmethoden einschließlich genau einer Fit-/Ganz-AST-Vorstufe.
Neue Gegenproben erfassen tatsächlich erreichte Source-/Parent-Teilergebnis-
und Recordphasen, Rootownerersetzung und Kopie mit Originalcheckern, Kernel-/
Guard-/Closure-/Builtinänderung vor Dispatch sowie Parent-BEGIN-POSTdrift.
Foreignobjekte und beschädigte Cachekeys erhalten Getter-/Hash-/Equality-/
Len-/Callsentinels. Writerzero/bool/overflow/error und Budgetdrift werden erst
im tatsächlichen Parent-BEGIN-Call injiziert. Vorhandene vollständige Wire-/
Raw-/Code-/Namespace-, Rollen-/EOF-/Import-/Child-/Retrymodelle bleiben erhalten.
Das sind ausgewählte Oracles, bisher keine bestandenen Tests.

Die CI wählt nur die neue vollständige Suite und deren tatsächliche direkte/
transitive Quellen und Fixturedateien; die unveränderte Standalone-Parentfactory
ist keine Abhängigkeit dieser Route. Zentraler Privacycheck bleibt unverändert.
Keine doppelten alten lokalen Suiten, keine neue Automation oder Modellkette.
Quelltexte und feste Template-Literale sind bisher ausschließlich als AST
bearbeitet/gelesen. Der unabhängige PRE muss den ganzen Code und alle Oracles
prüfen und gegebenenfalls ein ausdrückliches gestuftes Lauf-GO erteilen.

## Eigener Textbefund vor Lauf-GO

Nach Vorlage des stabilen C6 d0470fc wurde eine falsche Windows-Textdekodierung
festgestellt. Sie beschädigte deutsche Kommentare/Moduldocstrings neuer Dateien
und erzeugte einen unerwünschten Gesamtdiff im Ausführungsstand. Keine Probe
oder Generierung lief. Reviewer informiert; der Code-/Fixturekandidat bleibt
unverändert. Die Planungsdokumente werden ausschließlich aus ursprünglichen
UTF-8-Gitbytes wiederhergestellt und mit den belegten neuen Fakten ergänzt.
Keine Korrektur eines siebten Sourcekandidaten und kein Lauf-GO daraus ableiten.

## Unabhängiges No-GO und sichere Disposition

Der unabhängige Source-/Test-PRE ist an den eingefrorenen C6
`d0470fcaf3445a9ea68ef253a08930669a69424d` gebunden. Drei belastbare P2-Befunde
reichen für den STOP; keine vollständige Abnahme oder darüber hinausgehende
Modellprüfung wird behauptet:

1. Die neue `_rl_binding`-Funktion liest `parent` vor seiner lokalen Zuweisung.
   Bereits die erste Invocationprüfung würde mit `UnboundLocalError` scheitern.
2. Das feste `_CHECKPOINT`-Template entpackt `_guard[0]` und liest
   `_gf.__code__` vor primitiver Typ-/Identitätsprüfung. Ersetzte Slotinhalte
   können fremde Iterator-/Getteroperationen vor dem Bootstrap auslösen.
3. Der Entryfehlerabschluss liest nach Callbackfehlern erneut `o[11]` und
   setzt später `st[2]`. Veränderbare ursprüngliche Closurezellen sind keine
   sicheren lokalen Cleanupanker; ihr Austausch kann fremde Indexoperationen
   oder einen entweichenden Fehler statt der festen Ablehnung auslösen.

Zeilenbindung im verworfenen C6: Generator116/122, Checkpoint550 und Cleanup410.
Zusätzlich echte UTF-8-Textkorruption in deutschen Kommentaren/Moduldocstrings;
kein bloßer Zeilenendenbefund. Die ursprünglichen UTF-8-Planungsdokumente sind
wiederhergestellt; die verworfene Source-/Fixtureversion wurde nicht repariert.

Sechs/hartsechs Kandidaten und fünf geänderte Nachläufe sind erreicht,
Verbrauch UNKNOWN. Kein Fit-, Generator-, Compile-/Exec- oder Modelllauf,
keine tatsächliche Größenmessung, kein Native-/SQLlauf. Die übrigen15 Modelle
wurden nicht gestartet. Drei neue Runnerdateien einschließlich Tests und
Workflow werden aus dem finalen Integrationsdiff entfernt; bestehende Quellen,
Standalone-Parentfactory, deren Tests und der DESIGNED-Vertrag bleiben erhalten.
Die Git-Historie bewahrt den eingefrorenen abgelehnten C6 für die Befundbindung.
Nur der belegte Dokumentations-/Recoveryabschluss wird regulär integriert.

## Erforderliche Entscheidung für eine weitere Sourceversion

Offener Blocker ist die ausgeschöpfte konkrete Source-/Versuchsgrenze bei
notwendiger Code-/Fixturekorrektur. Kontinuierliche Entwicklung erlaubt keinen
stillen C7, Budgetreset, neuen Namen für denselben Scope oder unkontrollierte
Generatorprobe. Bis zu einer ausdrücklichen Entscheidung bleibt dieser Zustand
ruhig; ein Heartbeat allein löst keine Wiederholungsprüfung aus.

Konkreter Vorschlag zur Entscheidung: genau eine zusätzliche stabile C7-
Source-/Testversion innerhalb desselben ursprünglichen Rahmens zulassen,
Gesamtstand dann höchstens sieben Kandidaten/sechs geänderte Nachläufe,
Checkpoint vor Generierung und harte Grenze nach diesem einen Nachlauf.
Ein Implementierungsowner und derselbe unabhängige Reviewer; Verbrauch
weiter UNKNOWN. Koordination, Auswahl-/Source-/Testreviews, lokale Tests,
CI, Mainintegration und sichere eigene Bereinigung zählen gemeinsam.

Der vorgeschlagene Korrekturschnitt schließt ausschließlich die drei P2-
Befunde und die UTF-8-Textkorruption: korrekte Initialisierungsreihenfolge,
ursprünglich privat gehaltene primitive Typ-/Funktions-/Metadatenanker vor
Slot-/Fremdzugriff und tatsächliche lokale Cache-/State-/Cleanupanker im
aktiven ursprünglichen Fehlerframe. Er ergänzt eigene tatsächlich erreichte
Gegenproben für Slotersetzung und Closureaustausch. Keine Abschwächung des
DESIGNED-Vertrags, Rawumfangs, Scriptcaps oder anderer Gates. Die konkrete
Auswahl und der stabile Code benötigen erneut unabhängigen PRE; zuerst
Fit/Ganz-AST Windows/Linux, nur beidseitiges PASS erlaubt die übrigen Modelle.
Bei weiterem notwendigen Fix oder fehlgeschlagenem Fit kein C8. Dieser
Vorschlag ist nicht autorisiert und keine neue Implementierung.

Alle echten Runtime-/Trust-/Usedbytes-/Methoden-/SESSION_END-/SQL- und
Gesamtgates bleiben offen. Der reine Befundabschluss gehört zu
[PR276](https://github.com/gecompat/SQL_PerformanceSchulung/pull/276). Sein
Abschlussnachweis bindet den unabhängigen Dispositionsreview, passende lokale
Dokumentationschecks, tatsächliche Head-/Base-/Main-Gates, FullTree/Sync und
eigene Branchbereinigung. Das schließt keinen Sourcebefund durch Umsetzung.
