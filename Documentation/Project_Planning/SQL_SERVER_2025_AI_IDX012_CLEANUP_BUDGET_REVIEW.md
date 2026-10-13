# TSK-006: öffentliche Übergabe eines gemeinsamen Cleanupbudgets

## Tatsächlicher Quellenstand vor Integration

Vier Quellenstände wurden gezielt geprüft. Source1 hatte fünf bestandene und
eine fehlgeschlagene Methode: Der Fake-Prozess der Testfixture griff auf ein
nicht vorhandenes Secretmember zu. Die Originalbytes und Kanäle sind archiviert;
der Fehler wird nicht als bestandener Lauf umgedeutet. Source2 korrigierte die
Fixture und hielt nicht beobachtete Collectorkanäle ausdrücklich als UNOBSERVED
mit Nullwerten. Zwei betroffene normale und erstmals sechs optimierte Methoden
bestanden. Source3 band zusätzlich den tatsächlichen Deadlinegetter und
verweigerte fremde Getter, Setter, Reset- und Modulcallbacks; der neue Gegenfall
bestand normal und optimiert.

Der unabhängige Checkpoint nach tatsächlich drei Quellenständen schloss mit
FIX_REQUIRED: Ein erneuter Konstruktoraufruf konnte die Uhr zurücksetzen;
veränderte Modulkonstanten konnten die Frist beziehungsweise Reapreserve ändern.
Source4 verweigert die erneute Initialisierung vor jeder Feldänderung und prüft
die festen Werte mit ihren tatsächlichen Typen vor Windowoperationen und
budgetierten Clientstarts. Der neue zusammenhängende Gegenfall bestand normal
(PID31092) und optimiert (PID29636), jeweils mit bestätigtem Poll/Returncode0.

Insgesamt 18 Methodeninvokationen in sieben gehaltenen Testprozessen:
17 bestanden, eine ursprüngliche Fehlprobe bleibt sichtbar. Keine alte grüne
Vollsuite lokal wiederholt. SQL-, Principal-, Container-, Provider-, Compiler-
und Modellaufrufe0. Historische Runtime-UNKNOWNs und der gestoppte vorherige
Rollen-API-Schnitt bleiben unverändert. Die aktuelle PR-/Head-/Main-Integration,
Synchronisierung und eigene Belegsicherung/Archivierung stehen noch aus.

Der [vorbereitete Rollennachweis](SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md)
ist vor Callerumsetzung an einer konkreten APIgrenze zurückgestellt. Öffentlich
ist normal_deadline; der interne Beginn der20s-Recovery wird nicht übergeben.
Ohne Callback kann der Parent seine gemeinsame60s-Uhr nicht genau vor erstem
Restore beginnen. Ein vorgezogener Start lässt bei konfigurierten externen37s
und Windows-Collector-Nachlauf26s keine positive Normalzeit übrig. Das ist ein
Quellenbefund, keine gemessene Runtimeabweichung. Private Boundarybytes bleiben
erhalten; Caller/Pure/Native/Domain0.

## Konkreter unabhängiger Produktschnitt

Vor Native folgt eine ausdrücklich gewählte typisierte Budgetübergabe. Ein fester
öffentlicher Budgettyp besitzt einen einmaligen tatsächlich beobachteten
Cleanupstart und daraus eine gemeinsame absolute Deadline. Kein Reset oder
frei austauschbarer Executor-/Cleanupcallback. Der Controller beginnt diese Uhr
vor dem ersten Recovery-/Restoreversuch; seine20s-Recovery bleibt darin.
Nach Rückgabe kann der Parent denselben Budgetzustand für Principal- und
Namespaceabbau verwenden. Fehlender/unbestätigter Start bleibt sichtbar.
Bei UNKNOWN ohne Restore kann der Parent erst vor erlaubtem Namespacecleanup
dieselbe bisher ungestartete Uhr beginnen, ohne Folge-SQL.

Nur der neue ausdrücklich gewählte Budgetmodus verwendet einen festen eigenen
Collector mit absoluter Callfrist inklusive begrenzter Kill-/Reapreserve.
Öffentliches Framework-start_sqlcmd und tatsächlicher SqlcmdResult bleiben
gebunden; keine freien Commands/SQL-/ENV-/Collectoroverrides. Role-/SID-/Marker-/
Session-/DML-/Kosten-/Restoreoracles bleiben bestehen. Vor Start sind Timeout,
Restbudget und Reapreserve endlich typisiert zu prüfen; fehlendes Budget verhindert
Start. Jeder Nachlauf erhält denselben absoluten Rest, keinen neuen Volltimeout.
Beobachteter Timeout, unbestätigter Rücklauf oder tatsächliche Überschreitung
bleiben sticky UNKNOWN und FAIL. Keine behauptete OS-Wallclock-/Server-/TDS-
Endgarantie durch konfigurierte Caps. Tatsächliche gehaltene Prozess-/Input-/
Source-/sichere Kanalfakten bleiben erhalten.

Kein stiller Effekt auf den bisherigen Ein-Kontext-Pfad oder Rollenmodus ohne
neue Budgetauswahl; beide behalten ihre erklärten Grenzen. Keine Änderung des
globalen Frameworkcollectors, anderer Demos, CI-Imagepins, Runtime-/Default-
RED-Selektion oder anderer Repositories.

## Endliche Vorbereitung und Abnahme

Neuer API-/Collector-Deadlinevertrag: vorige sechs Quellenstände der Rollen-API
bleiben gestoppt; kein Reset oder rückwirkender Claim. Neuer Vertrag höchstens
sechs tatsächlich geprüfte Quellenstände einschließlich SyntaxFAIL, verpflichtender
Checkpoint3/Hard6. Ein Implementer, enger unabhängiger Rootreview für Zeit-/
Cleanup-/Prozessende-/Privacygrenzen. Neue betroffene Gegenfälle normal/-O mit
tatsächlichen Testenden/Source-/Rawbindungen, keine alte grüne Vollsuite lokal
wiederholen. Erforderliche Fälle in bestehende CI-Prozesse integrieren; keine
zusätzlichen Runtime-/Modellprozesse.

SOURCE_ONLY: kein SQL, Principal, Container, Provider, Compiler/Download oder
Hosteffekt. Historische3Rollenkandidaten/4Container, Nativeadmission und alle alten
FAILs/UNKNOWNs unverändert. Rollennachweis bleibt zurückgestellt bis vollständiger
Budget-APIintegration und neuer konkreter Caller-/Admissionbindung an aktuelle
Quellen. Kein Runtime-/TP-PERF-/Modulabschluss; Modell-/Tokenverbrauch UNKNOWN.

Privacy, betroffene Tests, aktueller Head/Main, PR nach origin/main, voller
Tree/FF/eigene Branches, private Belegsicherung und tatsächliche eigene Archivierung.
Danach unmittelbar den zurückgestellten zulässigen Caller fortsetzen. Alle
AI-Commits einschließlich Squash erhalten explizit das Codex-Präfix.
