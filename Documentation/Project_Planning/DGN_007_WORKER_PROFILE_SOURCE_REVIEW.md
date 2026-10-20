# DGN-007 – Workerquelle mit gebundener Profilaufnahme

Stand: 20. Oktober 2026. Basis
`ded09f685f747bb614c68c0fa78a6e54be7514be` nach vollständig geschlossenem PR266.
Status `C1_SOURCE_TEST_PRE_PENDING`.

## Priorität und endlicher Rahmen

PR266 belegt SCRIPT_LIMIT der vollständigen fünfzehnten Referenzroute mit
aktuellen vollständigen Profilbytes. Diese abgelehnte Route und ihr
ausgeschöpfter Nachweisscope werden weder wiederholt noch umbenannt.
Neue tatsächliche Implementierung: eine additive Workerquellenroute im
vorhandenen Generator, die den vorhandenen neunten vollständigen Metadata-/
Report-/Command-/Rawbody-Unterbau mit einer neuen lokalen Aufnahmeverbindung
zusammensetzt. Parentseitige Report-/SESSION_END-Matcher verbleiben beim
Parent; ihre Quellen, Regeln und Consumer werden nicht geändert. Die neue
Route ist keine kleinere gleichnamige Version der fünfzehnten Referenzroute.

Ein Implementierungsowner, derselbe unabhängige Reviewer, höchstens sechs
stabile Source/Testkandidaten, Checkpoint nach zwei, harte Grenze sechs
einschließlich Auswahl-PRE, Source/Test-PRE und ausdrücklichem Lauf-GO,
höchstens fünf gebündelter geänderter Befundnachläufe, lokaler Tests,
aktueller Gates, regulärer Integration, FullTree/Sync und eigener Branch-
bereinigung. Verbrauch UNKNOWN. Keine zusätzliche Automation oder Owner.

## Konkrete API und Quellenauswahl

Additive API `build_inline_worker_profile_control_bootstrap(profile_raw, *,
logical_profile, expected_soabi, expected_destshared)` im vorhandenen
`Tests/Tools/dgn007_control_bootstrap_source.py`. Wiederverwendung von
`build_inline_body_control_bootstrap` mit unveränderten Prüfungen. Einfügen
eines neuen festen Inlinefragments vor demselben einzigen Mainanker. Direkt
nach dem gebundenen Kontrollladen initialisiert Main einmal eine private
Kontrollpfadbindung, bevor Metadata angenommen wird. Erneute Initialisierung
scheitert dauerhaft; keine neue Bindung nach einer Abweichung.
Alle bisherigen fünfzehn Builder und ihre Bytes für dieselben Inputs bleiben
unverändert. Das neue Ergebnis bleibt reine `BootstrapSource` mit privaten
Bytes und unveränderten Attestationsflags false.

Neue private Inline-API `_inline_observe_selected_worker_profile(worker, *,
token, separately_known_filefinder_hook)`: komplette W6-Form und Semantik
einschließlich S15/Controls/P11 vor Kontrollmodulzugriff, genaue Token-/Hook-
Typformen. Danach ausschließlich die vorab gehaltene private Kontrollpfadbindung
gegen `_SEMANTIC_CONTROL_ANCHOR` und bestehende Kohärenz prüfen. Bei deren
einmaliger Aufnahme alle direkten Quellenfunktionen anhand des ursprünglichen
gehaltenen compile-Codes prüfen, nicht nur den Entrycode. Code/Globals/Defaults/
Keyworddefaults/Closurezustand, begrenzte Modul-/Quellenklassennamespaces
einschließlich erzeugter Methoden und die bekannte mutable FROZEN_NAMES-
Konfiguration halten; vor/nach Aufruf und nach Fehlern gegen dieselben Anker
schließen. Die Helferkette `_selected_shapes`/`_bind_selected`/`_capture` und
`observe_current_interpreter_scalars` darf nicht unbemerkt ausgetauscht werden.
Importierte Interpreter-/Stdlib-/OS-Provider bleiben die ausdrücklich angenommene
Kontrollruntimegrenze, keine transitive Host- oder Trustattestation.
Keine fremde Funktion oder öffentliche Ergebnisreceipt als Dispatchautorität.

Dieselbe vollständig ausgewählte Installation/Controls/Inventur unverändert
an PR265-API übergeben. Nur tatsächliche private Aufnahme zurückgeben, nach
striktem Resultat-/Report-/Scalarformcheck und vollständigem Vergleich mit W6.
Kontrollmodul-/Cache-/Funktions-/Codeanker vor/nach und auch nach Fehlern
dominant schließen. Keine Selbstbaseline, kein Auffüllen aus Sollwerten,
feste atomare Ablehnung ohne Rohfehler, Teilprofil oder Teilscalars.

## Abnahmen und Ausführungsgrenze

Eigene neue portable Suite mit höchstens16Methoden, ohne Import des alten57-
oder großen Bootstrap-Harness. Eigene Sys-/OS-/Sysconfig-/Modul-/Spec-/Loader-
Modelle; sichere reine Fixturebausteine aus den kleinen Profiltests dürfen
wiederverwendet werden. Keine echten Stdlib-Patches. Neue Inlinefunktionen
werden aus der erzeugten Quelle nur in eigener begrenzter Modellnamespace
ohne direkte Imports/Mainaufruf definiert. Die Profilaufnahme darf dort den
tatsächlichen PR265-Code auf eigenen Daten prüfen. Kontrollquellenkohärenz ist
bereits im unveränderten alten Harness abgedeckt; gezielte eigene Modelle
weisen neue PRE-/POST-Aufrufe und Bindungsverluste nach, keine neue Byte-/Trust-
Attestation aus einem künstlichen Codeanker.

Positive Fälle: unveränderte volle Workerwerte gehen an dieselbe echte lokale
Aufnahme; tatsächliche Scalars/Profil bleiben privat. Negative Fälle: späte
W6-/S15-/P11-Formfehler vor Kontrollzugriff, fremde Code-/Globals-/Defaults- oder
Closurebindung, fehlerhafte/gefälschte Resultate, volle Feldabweichung, später
Kontroll-/Cache-/Funktionsverlust auch nach Fehlerrückgabe, kein Rebaselining.
Mutationspunkte und ausbleibende fremde Callbacks außerhalb Fehlerhüllen
nachweisen; fixtureeigene Änderungen restaurieren.

Tatsächlicher Quellengrößencheck der neuen Zusammensetzung mit vollständigen
aktuellen Arbeitsdatei-/kanonischen Profilbytes, separat gebunden und nicht
normalisiert. Das unveränderte131072-Byte-Cap und Rawliteralgleichheit müssen
halten; auch negative Größen-/Locator-/Configformen prüfen. Kein Rerun der
abgelehnten fünfzehnten vollständigen Route. Fünf direkte Scriptimports,
vollständige Closure der vorhandenen benötigten Helpers und Erhalt bisheriger
Builder deterministisch prüfen. Neue gezielte CI-Suite; bestehende Bootstrap-
Consumer-Gates bleiben erhalten, keine neue SQL-/Kanal-Suiteauswahl.

Erst nach unabhängigem Source/Test-PRE mit Lauf-GO neue Suite Windows/Linux.
Keine generierte Mainausführung, echte Workerinventur, neuen Runtimeprozesse,
Kandidatenimporte, SQL oder zusätzliche physische Reads auswählen. Neue
Workerquelle bleibt noch ohne operativen stdin-/stdout-Phasenowneraufruf.
Konkreter operativer Scriptlocator, separat quellenbegründete Installation und
volle S15/P11-Inventur sowie Fünf-Formen-/64KiB-Fit bleiben Folgearbeit.
Worker-/Loader-/Import-/UsedBytes-/Trust-/Methodenqualifikation bleiben offen.

## C1 und unabhängige Auswahl

Auswahl-GO auf Basis und Plan-SHA256
`da3cbbf7ccec8c4d8e7e7482bba58a5a9c018b4f6c337e208279a01ca1e52465`.
Die konkretisierte Auflage bindet die gesamte Kontrollfunktionskette vor
Metadata, nicht nur den Entrycode. C1 ergänzt einmalige Maininitialisierung,
Compilecodeprüfung aller direkten Kontrollfunktionen, Funktionszustände,
Modul-/Klassenwerte und bekannte Frozenkonfiguration sowie dominante PRE/POSTs.
Jede Initialisierungswiederholung und jede fehlgeschlagene Aufnahme verwerfen
die private Bindung; sie wird nicht erneut aus dem aktuellen Zustand gebildet.

Neue zwölf portable Modellmethoden, neue eng ausgewählte CI-Suite. Die tatsächliche
Kontrollquelle wird nur im eigenen Kontrollmodul ausgeführt, ohne neue
Cacheeinträge oder reale Stdlibänderungen; generierte Quelle nur als Definitionen
ohne Imports/Main. Direkte Kontrolllade-Kohärenz wird im neuen Modell begrenzt
vertreten und bleibt durch unveränderte alte Consumer-Gates abgedeckt.
Noch keine Suiteimporte oder Läufe; AST/Methodenzählung sind reine Quellenchecks.
Source/Test-PRE und ausdrückliches Lauf-GO stehen aus. Ein Kandidat/max6,
kein Befundnachlauf; Verbrauch UNKNOWN.

Der neue Workflow wählt nur Generator, Profilkontrolle, sichere Fixturequellen,
neue Suite, konkreten Plan und sich selbst. Er führt ausschließlich neue zwölf
Methoden aus. Bestehende Bootstrap-/Sourceconsumer-Gates bleiben erhalten;
keine SQL-/Kanal-Suite oder Scanner-Selbsttestauswahl und keine weitere
Reviewkette. Keine vollständigen grünen Logs oder Telemetrie.
