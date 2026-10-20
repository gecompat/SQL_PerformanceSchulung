# DGN-007 – vorgewählte Profilanker und frische lokale Aufnahme verbinden

Stand20.Oktober2026, Basis `5bf9d14a46b0fba1184f6a5a6dc3772c6278cb17` nach
vollständig abgeschlossenem PR264. Status `C1_SOURCE_TEST_PRE_PENDING`.
Der kontinuierliche menschliche Auftrag gilt weiter; die korrigierten
didaktischen Regeln bleiben unverändert. Dieser technische Schnitt beansprucht
eine begrenzte lokale Aufnahmefunktion, keine neue Schulungs- oder Importabnahme.

## Gemeinsamer endlicher Rahmen

Ein Implementierungsowner und ein unabhängiger Reviewer. Höchstens sechs
stabile Quellen-/Testkandidaten, Checkpoint nach zwei, harte Grenze sechs
einschließlich Auswahl-PRE, Source/Test-PRE mit ausdrücklichem Lauf-GO,
höchstens fünf gebündelter geänderter Befundnachläufe, lokaler Checks,
aktueller PR-/Main-Gates und regulärer Integration/FullTree/Sync/Branchcleanup.
Verbrauch UNKNOWN; keine pauschale Geld-/Tokenbegrenzung behauptet. Kein
alter ausgeschöpfter Scope oder unveränderter grüner Lauf wird neu benannt.

## Gewählter Schnitt

PR263 bindet volle S15-/P11-Auswahl rein an explizite lokale Anker. Die
vorhandene `observe_current_interpreter_scalars` nimmt dagegen frisch gegen
eine bereits gebundene DeclaredProfile auf. Eine private durchgehende Funktion
zur Verbindung beider Wege und zum vollständigen abschließenden Scalarvergleich
fehlt. Neue additive API in der vorhandenen Profilkontrollquelle:
`observe_selected_profile_scalars(installation, controls, modules, *, token,
separately_known_filefinder_hook)`.

Vollständige primitive Vorprüfung vor lokaler Aufnahme. Danach tatsächlichen
aktuellen Cache und begrenzte Finder-/Hookcontainer lokal halten, gesamte
Auswahl an deren Identitäten binden und dieselbe DeclaredProfile an die
vorhandene frische Aufnahme übergeben. Ein privater gemeinsamer Bindungskern
vermeidet die doppelte primitive Vorprüfung; öffentliche reine Bindungs-API
und ihre Reports bleiben kompatibel. Alte15Inlinebuilder, Kanalowner und
Runtime-/SQLquellen bleiben unverändert.

Die Rückgabe hält privat vollständige tatsächlich projizierte Scalars sowie
dieselbe erwartete DeclaredProfile für eine spätere erneute Aufnahme gegen
dieselben Anker. Kein Rebaselining nach einer Abweichung. Alle ausgewählten
S15-/Control-/P11-Felder werden nach exakter Typ-/Formprüfung vollständig mit
der tatsächlichen Scalarprojektion verglichen. Der beobachtete Bericht oder
ein Bool allein ist keine Übergangs-, Worker- oder Consumptionauthority.

Cacheidentität, vollständige aktuelle Mitgliedschaft und gehaltene Modul-/
Spec-/Loaderanker sowie aktuelle Finder-/Hookcontainer bleiben bis zum letzten
POST gebunden. Cacheaustausch nach der letzten inneren Aufnahme, zusätzliche
Einträge, Hook-/Metadatendrift oder unklare Ausnahme liefern atomar feste
Ablehnung ohne Teilscalars/Teilprofil. Die bestehenden lokalen Keygrenzen
(16368 je Bindungs-/POST-Pass,4096UTF8 ohne NUL) und primitive Formcaps gelten.
Keine atomare dauerhafte Snapshotgarantie und keine neuen Host-/Thread-/
Sandboxversprechen; keine öffentlich akzeptierten Ereignis-/Reportreceipts.

## Ausführung und Tests

Neue Quelle/Testoberfläche bleibt im Kontrollmodul und einem eigenen portablen
Harness mit höchstens16Methoden. Neue Fixtures verwenden ausschließlich eigene
synthetische Sys-/OS-/Sysconfigdaten, Module/Specs/Loader und FileFinder-Hook-
Metadaten; keine echten Stdlibmodule patchen. Der tatsächliche vorhandene
Aufnahme-/Vergleichscode wird gegen diese begrenzte lokale Modellumgebung
ausgeführt. Kein realer Kandidatenimport, Worker, SQL, eigener physischer
Inventurlauf oder neue native operative Installation wird dadurch ausgewählt.

Gegenproben: vollständiger Erfolg ohne Synthese und mit gehaltenem Profil,
späte Formfehler vor lokaler Aufnahme, unpassende komplette Scalarfelder,
falscher Hook, Unsupported-/Containerformen, Cacheaustausch/-zugang nach letzter
Aufnahme, Module-/Spec-/Loader-/Finder-/Hookdrift, feste Fehler ohne Payload,
keine Fortschreibung nach Fehler und kein Input-/Realcache-/Providerverlust.
Keine zusätzliche Hash-/Dateibeobachtung im neuen Wrapper: physische Reads
bleiben ausschließlich der unveränderten bestehenden Aufnahme und deren
separat ausgewählten höchstens zwei F3 mit32/64MiB-Grenzen vorbehalten; die
neuen synthetischen Tests wählen keine physischen Files.

Erst nach unabhängigem Source/Test-Lauf-GO neue Suite auf Windows/Linux und
betroffene bestehende16-Methoden-Bindungsregression auf beiden Plattformen.
Alte57-Profiltests laufen im bestehenden Linux-CI-Gate; kein alter Windows-
Fixtureretry. Die unabhängige Diagnose dieses Plattformfehlers bleibt erhalten.
Eigener gezielter Workflow für neue Suite plus bestehende Modulconsumer-
Selektoren; kein neuer Vollscan oder SQL-/Kanaltestselector. Frische Pflicht-
gates regulär erfüllen, keine unveränderten grünen lokalen Suites wiederholen.

Die operative vorab quellenbegründete neue Installation/volle Worker-S15/P11-
Inventur, konkrete Bootstrapdatei und Fünf-Formen-/64KiB-Fit sowie tatsächliche
Worker-/Loader-/Import-/UsedBytes-/Trust-/Methodenqualifikation bleiben offen.
Alle Attestationsflags false, Scope PROJECT_SEMANTIC. Diese neue Verbindung
darf die fehlende tatsächliche Worker-/Quellenprovenienz nicht verdecken.

## C1 und Reviewbindung

Die unabhängige Auswahl-PRE auf Basis und Plan-SHA256
`21e6950e872d1532264f9f4ea9e9659a63fccab37ea386c3cd7c3e48ccc11364`
erteilt Auswahl-GO ohne offene P1/P2/P3. C1 hält Hook-/Factory-/Code-/Closure-
und Detailsanker bereits vor der frischen Aufnahme. Nach der vollständigen
Scalarprüfung folgen ein zusätzlicher begrenzter Metadaten-Capture ohne neue
Dateihashes sowie dominante Container-/Provider-/Anker-POSTs. Feste atomare
Fehler ohne Rohmeldung oder Teilwerte. Reiner Binder nutzt denselben privaten
Kern bei unveränderter öffentlicher Semantik.

Neue16Methoden mit eigenen Modellobjekten; kein alter Runtime-Harnessimport.
Noch keine Suiteimporte oder Testläufe. Source/Test-PRE und ausdrückliches
Lauf-GO stehen aus. Ein Kandidat/max6, kein Befundnachlauf; Verbrauch UNKNOWN.

Der neue gezielte Workflow wählt nur Kontrollmodul, betroffene Fixturequelle,
neue Suite, konkreten Plan und sich selbst. Er führt ausschließlich neue16
Methoden unter Linux3.12 aus. Bestehende Bindungs-/Sourceconsumer-Gates bleiben
erhalten. Keine SQL-/Kanal- oder Scanner-Selbsttests werden neu ausgewählt;
lokale Windows-/Linuxläufe prüfen die portable Modellgrenze, keine zusätzliche
Reviewkette, kein voller Logtransfer oder Telemetrieaufbau.
