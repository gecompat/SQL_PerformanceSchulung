# DGN-007 – vollständige Profilauswahl an lokale Anker binden

Stand 20. Oktober 2026, Basis `9938091d7de38bb95152cc06e055470e5fb8b7cc`
nach vollständig abgeschlossenem PR262. Status `LOCAL_PASS_PR_GATES_PENDING`.
Kontinuierlicher menschlicher Auftrag; ein Implementierungsowner, unabhängiger
Auswahl- und Source/Test-PRE mit ausdrücklichem Lauf-GO. Höchstens sechs stabile
Quellen-/Testkandidaten, Checkpoint nach zwei, harte Grenze sechs einschließlich
aller Reviews, höchstens fünf geänderter Befundnachläufe, Tests, CI und Abschluss.
Token-/Kostenverbrauch UNKNOWN; keine Wiederaufnahme ausgeschöpfter Scopes.

## Konkrete Lücke und Schnitt

§16.1/16.2 des [Profilvertrags](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md)
verlangt eine unabhängig vorgewählte vollständige S15-/P11-Auswahl. Die vorhandene
frische Aufnahme `observe_current_interpreter_scalars` benötigt dafür eine
`DeclaredProfile` mit lokalen Modul-/Spec-/Loaderidentitäten. Es fehlt die
begrenzte Brücke von sämtlichen separat gewählten Wirefeldern zu diesen Ankern.
Ein aktueller Cache darf dabei niemals seine eigene Sollauswahl erzeugen.

Additiv in der vorhandenen allein zulässigen Profilkontrollquelle
`Tests/Tools/dgn007_import_runtime_profile.py`:
`bind_selected_profile(installation, controls, modules, *, token, cache,
finders, hooks)`. Installation ist exakt S15, modules sind sämtliche P11,
controls die vollständige separate Auswahl. Alle primitiven Felder und Caps
werden vor Metadatenbindung geprüft; keine Defaults oder Ergänzung aus Istwerten.
Das Ergebnis hält privat die `DeclaredProfile`; ein fester Report unterscheidet
`BOUND_SELECTED_PROFILE` von Ablehnung. Es ist keine Observation/Receipt.

Der Caller übergibt ausdrücklich den lokalen exakten Cache und Finder-/Hookanker.
Kein impliziter Zugriff auf `sys.modules`, `sys.path` oder aktuelle Installation,
kein Dateiread/-write, kein Hashing, kein Import, kein Workerstart und keine
Hookausführung im neuen API. Vorhandene Imports und APIs bleiben unverändert.
Ausgewählte Cachekeys müssen vollständig und exakt dem übergebenen Cache
entsprechen. Ganze ausgewählte P11-Felder werden an tatsächliche lokale
Modul-/Spec-/Loaderfelder gebunden, einschließlich aller Frozenpartner,
Package-Locations, Loadernamen/-pfade und Kontrollmodule. S15-Felder bleiben
unverändert ausgewählte Werte; physische Existenz/Trust/aktuelle Flags werden
erst von der späteren vorhandenen frischen Aufnahme geprüft. Ein lokales
Ankermatch darf diese spätere Aufnahme nicht ersetzen.

Alle Felder werden vor Verwendung exakt typisiert, inklusive bool/int-Trennung,
begrenzter primitiver verschachtelter Tupel, Strings und bekannter Labelwerte.
Späte ungültige Auswahlfelder dürfen nicht hinter einem frühen Ankermismatch
verschwinden. Keine fremden Iteratoren, Deskriptoren oder Rohfehlertexte werden
als Auswahl akzeptiert. Atomare Ablehnung ohne Teilprofil, versteckte Locator/
Nonce/Anker in repr, alle Attestationsflags false, Scope PROJECT_SEMANTIC.

Auswahl-PRE fand eine relevante Asymmetrie im bisherigen `_records`-Guard:
Ein Frozen-Alias fordert dieselbe Modul-/Specidentität auch bei einem Source-
Partner. §16.1 und die vorhandene Projektion verlangen dies nur bei zwei
Frozenpartnern; Mixedpartner bleiben mit vollständigen Records und `()`.
Der erste C1 korrigiert ausschließlich diesen engen Guard und deckt beide
Mixedorientierungen sowie echte Frozenverbände unabhängig ab. Das erweitert
keine API-/I/O-Wirkung und setzt keinen alten Scope zurück.

## Abnahme und Aufwand

Auswahl-PRE auf obiger Basis und Plan-SHA256
`9083ca5a5d39d5e742ed0b2bd8d6cb291b76de8cf041bb03c36bbbc455c7e083`
ausdrücklich freigegeben. C1 enthält die additive API, den engen Aliasguardfix,
15 portable Methoden mit vollständig eigenen synthetischen Metadaten und den
gezielten Workflow. Gültige abweichende S15-Auswahlen werden unverändert
gehalten; alle elf P11-Felder an lokale Anker gebunden. Keine Testvererbung
von Fixtures mit echten Stdlibpatches; eigene Builtins-/Ambient-Stubs und
reversible Änderungen nur im eigenen Subject-/Fixturescope. AST/diffcheck
bestanden, noch keine Suiteimporte/-läufe. Source/Test-PRE mit Lauf-GO offen.

Neuer eigener portabler Harness mit höchstens 16 Methoden: vollständiger
Erfolg samt identischen gewählten S15/P11 und gehaltenen Ankern; Mutationen
aller S15-/P11-Felder; fehlender/zusätzlicher Cache, umgestellte P11-Auswahl,
unbeachtliche Cacheinsertionsreihenfolge bei identischen Keys/Ankern, fremde Typen,
späte Formfehler vor frühem Bindungsfehler, Frozenaliase einschließlich
Mixedpartnern, Package-/Loader-/Controlsdrift, Caps, kein I/O/Hash/Hook-/
Observation-/Prozessaufruf, keine Änderung an übergebenen oder echten Globals.
Nur synthetische Module/Specs/Loader und Locator. Keine neue operative
Charakterisierung oder Ableitung der Sollinventur aus der aktuellen Installation.

Nach unabhängigem C1-Lauf-GO lokal neue Suite auf Windows und Linux sowie
vorhandene57-Methoden-Profilregression unter Windows. Deren historische direkte
Linux-Kontrollruntimecharakterisierung bleibt separat bezeichnet; im bestehenden
CI-Gate mit `-I -S -B` enthalten, kein operativer Auswahlbeleg. Das bestehende
Sourcebundle-CI erfasst geänderte Profilquelle ohnehin. Neuer gezielter portabler
Workflow nur für neue Tests/Profilquelle/eigenen Plan; kein weiterer Vollscan,
keine Erweiterung von SQL-/Offline-/nativen Kanalselektoren. Die unveränderten
Kanal- und Eingangsplansuites werden lokal nicht wiederholt. Frische erforderliche
PR-/Main-Gates, unabhängige Befundschließung, reguläre Integration, FullTree/Sync
und eigene Branchbereinigung schließen diesen Schnitt vollständig ab.

Dies wählt noch keine reale Installation, operative Bootstrapquelle oder volle
neue Workerbaseline. Keine Änderung an den15 Inlinebuildern, Kanalownern, neun
Runtimequellen, SQL oder Registry. Nachfolgend bleiben vorgewählte tatsächliche
Installation/Inventur und Fünf-Formen-Gate, Einbindung der frischen Aufnahme in
den Worker sowie tatsächliche Loader-/Import-/UsedBytes-Provenienz offen.

Die primitive Vorprüfung hält die bestehenden E4-Obergrenzen16368 Knoten,
Tiefe8, Sequenz256 und4096UTF-8-Bytes je Text. Sie ist kein Fünf-Formen-Fitbeleg.

C1 `07daf827ab9025b546687940c839a3d3463ed677` unabhängig vollständig geprüft:
Aliasguard-P2 geschlossen, ein neuer P2 zu unbeschränkten lokalen Keytexten;
kein Lauf-GO und keine Testausführung. C2 schließt diesen Befund gebündelt:
Cache-/Modul-/Spec-/Loaderkeys vor Sort/Lookup bis4096UTF-8-Bytes ohne NUL,
gemeinsam höchstens16368 tatsächlich geprüfte Keys je Bindungs-/POST-Pass.
Erneute physische Scans gemeinsamer Aliasnamespaces zählen erneut; POST hat
einen eigenen begrenzten Counter. Keine fremden Globalvalues traversiert.
Das ist eine zusätzliche lokale Ankergrenze, kein E4-/Fünf-Formen-Fit und keine
Qualifikation einer realen Inventur. Die16.Methoden-Gegenprobe hält Cachecounts
konstant, trägt Sort-/Lookup-Traps und prüft globale Grenze, Aliasmehrfachscan
und den separat begrenzten POST. Checkpoint2: zwei Kandidaten, ein gebündelter
Befundnachlauf; harte Grenze6 unverändert, Verbrauch UNKNOWN.

C2 `a5bfb11c1484913f804a88d368dcfb50793948cf` unabhängig ohne offene P1/P2/P3
mit ausdrücklichem einmaligem Lauf-GO bestätigt. Neue16/16 Methoden unter
Windows3.14.7 in0,162s und Linux3.12.3 in0,079s ohne SKIP PASS.
Der freigegebene alte Windows57-Lauf scheitert mit24 FAIL/fünf ERROR/drei SKIP
an der unveränderten POSIX-Pfadfixture: `ntpath.isabs('/declared/lib')` ist seit
Python3.13 auf Windows false. Basiscode und Fixture sind diesbezüglich unverändert;
kein Produktions-/Oraclefix oder grüner Wiederholungslauf. Unabhängige Diagnose
und ausdrückliches einmaliges Plattform-Lauf-GO für unveränderten C2: bestehende
57/57 Methoden lokal unter WSL/Linux3.12.3 mit `-I -S -B` in0,067s ohne SKIP
PASS. Die historische Kontrollcharakterisierung wird nicht zur operativen
Workerbaseline. [CPython-isabs-Änderung](https://docs.python.org/3.14/library/os.path.html#os.path.isabs),
geprüft20.Oktober2026. Die neue portable API ist auf beiden Plattformen geprüft;
die vorhandene physische Profilaufnahme und ihr CI-Gate bleiben Linux3.12.
Aktuelle finale PR-/Main-Gates, reguläre Integration, FullTree/Sync und eigene
Branchbereinigung folgen vor Abschluss.

Primärquellen, geprüft20.Oktober2026: [CPython3.12 ModuleSpec](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec),
[Modulcache](https://docs.python.org/3.12/reference/import.html#the-module-cache),
[ModuleType](https://docs.python.org/3.12/library/types.html#types.ModuleType).
Spec- und Modulfelder müssen separat gebunden werden; ihre Gleichheit ist
keine automatisch dauerhaft gehaltene Eigenschaft.
