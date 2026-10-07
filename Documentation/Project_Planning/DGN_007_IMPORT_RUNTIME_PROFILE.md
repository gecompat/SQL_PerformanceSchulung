# DGN-007 – Interpreter-/Stdlib-Profilvorschnitt

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Repositorybasis | `457288472e53bb8cda2cc74d2921fd29a570e4b5` nach PR84 |
| Status | `IMPLEMENTED_PROFILE_METADATA_SLICE`; Validierung siehe unten |
| Claim | `MATCHED_DECLARED_BASELINE`; keine Trustattestation |
| Geltung | `PROJECT_SEMANTIC`; gesonderte tatsächliche Linux-Bootstrapbeobachtung |
| Grenze | keine DGN-Import-, Resolver-, Worker-/Cleanup-, SQL- oder Methodenattestation |

Der [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md)
verlangt vor einer späteren Importausführung ein konkret gewähltes
Interpreter-/Stdlibprofil. Dieser Vorschnitt nimmt begrenzte tatsächliche
Metadaten des laufenden Kontrollinterpreters auf und vergleicht sie mit einer
separat deklarierten unveränderlichen Baseline. Er erzeugt kein Vertrauen aus
seiner eigenen Beobachtung. Das [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md)
und die [synthetische Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md)
bleiben getrennt; die neun DGN-Quellen und alle 27 Bundlemember unverändert.

## Deklaration, Beobachtung und Vertrauensgrenze

[`dgn007_import_runtime_profile.py`](../../Tests/Tools/dgn007_import_runtime_profile.py)
trennt `DeclaredProfile`, `Observation` und `ProfileReport`. Der reine
`validate_profile`-Vergleich prüft Form, Vollständigkeit und Gleichheit.
`observe_current_interpreter` beobachtet den aktuellen Linux-/CPython-3.12-
Kontrollbootstrap mit `-I -S -B`. Es gibt keinen Workerstart, PATH-Fallback,
Download, Kandidatenimport oder Finderaufruf.

Die erste Testauswahl ist die bereits vorhandene GitHub-Actions-Kontrollruntime
mit `actions/setup-python` und Python `3.12`. Der Test deklariert ihre exakte
Patchversion, Executable, Roots und ABI vor der Beobachtung. Dies ist eine
ausdrückliche Kontrollannahme (`DECLARED_SETUP_PYTHON_CONTROL_RUNTIME`), keine
unabhängige Herkunftsattestation. Die Baselinewahl bleibt Verantwortung des
Kontrollaufrufers; eine Klasse oder ein Authoritylabel verleiht keine Rechte
und ist kein Trustbeleg. Ein Worker darf später nicht sein eigenes Ergebnis
als unabhängige Auswahlquelle verwenden. Die konkrete getrennte Parent-/Worker-
Baselineübertragung und ihre Ausführungsbindung bleiben offen. Der getrennte
[skalare Bindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) legt
deren Formen als `DESIGNED` fest. Der getrennte
[reine Matcher](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist jetzt implementiert;
er vergleicht deklarierte Records, keine tatsächliche Workerbeobachtung.

Beobachtet werden tatsächliche Startflags, Interpreter-/Installationsmetadaten,
Finder-/Hookidentitäten und der vollständige begrenzte vorbeladene Modulbestand.
Die gehaltenen Liveobjekte werden von ihren skalaren Metadaten getrennt und
auf Kohärenz geprüft. Reguläre feste Frozen-Bootstrapaliases müssen dasselbe
Modul-/Specobjekt wie ihr kanonischer Eintrag halten; dies erlaubt keine
DGN-Aliases. Builtin und Frozen sind keine Dateibytes. Directory-/
Extensionorigins müssen zur ausdrücklich benannten Auswahl passen; ein
standardmäßiger, tatsächlich nicht vorhandener Zip-Suchpfadeintrag ist von
einem verwendeten Ziploader getrennt. Site-, Namespace-, Lazy- und unbekannte
Loader sind für diesen ersten Zuschnitt nicht zulässig. Die Inventur betrifft
vorhandene Kontroll-/Stdlibmodule, keine vollständige transitive Stdlibclosure.

Pfade, Versionsstrings und optionale Dateihashes bestätigen ausschließlich
Metadaten beziehungsweise gelesene Dateien. Sie attestieren weder die bereits
ausgeführten Modulbytes noch Interpreter-, Bibliotheks- oder OS-Vertrauen.
Das gilt auch für Isolationflags. `trust_assumed` benennt die deklarierte
Annahme; `trust_attested`, `runtime_attested`, `import_used_bytes_attested` und
`method_approved` bleiben false. Absolute Origins und Liveanker bleiben privat;
öffentliche Reports enthalten feste Status-/Fehlercodes und Claimflags.

## Bounds, Validierung und Restumfang

Es gelten höchstens 256 Modulrecords, 4096 UTF-8-Bytes je Metadatenfeld,
höchstens zwei ausdrücklich benannte Hashfiles, akzeptierte Dateigrößen von
32 MiB je Datei und 64 MiB kumulativ. Der Leser verwendet feste 64-KiB-Chunks
und höchstens ein zusätzliches Grenzbyte, um Überschreitung geschlossen
abzuweisen; dieses Byte wird nicht als akzeptierter Hashinhalt verwendet.
Keine Verzeichnisinventur, Sourceausführung oder automatische Persistierung.
Diese Aufnahmegrenzen sind keine Sandbox oder harte Wallclockzusage. Ihre
spätere Einbindung muss die gemeinsame 20-s-Probenzeit und kumulativ 10-s-
Cleanupgrenze des vollständigen Entwurfs weiterhin einhalten.

Die Gegenproben liegen in
[`test_dgn007_import_runtime_profile.py`](../../Tests/Static/test_dgn007_import_runtime_profile.py).

```powershell
python -I -S -B Tests/Static/test_dgn007_import_runtime_profile.py
```

Portable Vertragsgegenproben und die tatsächliche Linux-Bootstrapbeobachtung
werden getrennt ausgewiesen. Die Linuxbeobachtung liegt im direkten
Skripteinstieg vor dem `unittest.mock`-Bootstrap: dessen `typing`-Cache enthält
auch Nichtmodulobjekte, die dieser enge Beobachter geschlossen ablehnt.
Windows bleibt für diese tatsächliche Beobachtungsroute nicht unterstützt.
Lokal unter Python 3.12.14: 24 Testmethoden, davon 23 PASS und genau ein
ausdrücklicher Linux-SKIP (0,042 s). In der Linux-CI muss auch diese Methode
PASS erreichen. Die elf Projektvalidatoren und fünf Frameworkprüfungen
bestanden separat mit Exit 0 (Privacy: 909 Dateien; Result-Evaluator: vier
Tests). PR85 integrierte den Vorschnitt als Squash
`e75baeb811c1a9973198200c94aa37a795d64b1a`. Die getrennten Linux-Runs
[PR85](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37638549160)
und [Main](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37639021867)
bestanden jeweils Bundle36, Edge26, Input27, Loader27 und Profil24 ohne SKIP.
Der PR-Checkout war `f6ff05aa1cae9ca149a624a360bcce23558eb7c9` am exakten
Head/Base; der Main-Checkout war der genannte Squash. Der begrenzte tatsächliche
Linux-Bootstrapmatch wurde damit getrennt von portablen Fixtures geprüft.
Ein Metadatenmatch
ist kein erfolgreicher DGN-Import. Feste Quellenauflösung, tatsächliche
Loaderverwendung und Importabschluss sowie drei begrenzte eigene Linux-Worker
mit unabhängig geprüftem Cleanup bleiben offen. G13, v1, DEC-068 und die
zurückgestellte Capture-API bleiben unverändert.

Primärquellen, geprüft am 2026-10-07:
[Python 3.12: sys-Metadaten](https://docs.python.org/3.12/library/sys.html)
und [Isolation-/Site-/Bytecodeflags](https://docs.python.org/3.12/using/cmdline.html).
`sys.stdlib_module_names` ist eine plattformübergreifende Namensliste, kein
Inventar installierter oder tatsächlich verwendeter Bibliotheksbytes.

## Getrennte lokale Record-Rückgabe

Die Erweiterung auf Basis `25c9801e458ba124a8d4afc9e48655dc15fcbf51` nach PR87
liegt als `IMPLEMENTED_LOCAL_OBSERVATION_RECORDS` vor. Die neue API
`observe_current_interpreter_records(expected) -> ObservationResult` enthält
den bisherigen `ProfileReport` und ein privates Feld `observation`. Der
bisherige Aufruf `observe_current_interpreter(expected)` liefert weiterhin
ausschließlich den Report desselben Beobachtungspfads. `validate_profile`
bleibt der reine Vergleich. Es gibt keine neue Bootstrapquelle oder neue
Controlnamen, Importkanten, Finder, Suchpfade oder Worker.

Die Record-API gibt ausschließlich das tatsächlich durch `_capture` erzeugte
`after`-Objekt zurück, nachdem die vorherige Aufnahme, die unveränderten
optionalen Rohhashreads und die vollständige Abschlussprüfung erfolgreich
waren. Keine Recordwerte werden aus dem Soll ergänzt oder aus einem PASS-Flag
rekonstruiert. Jede regulär behandelte Ablehnung liefert `observation=None`,
auch vor der Aufnahme, beim Dateilesen und bei einer Abschlussabweichung.
Plattform-/Form-/I/O-Fehler behalten feste öffentliche Codes. Harte
Unterbrechungen liefern keine erfolgreiche Rückgabe oder neue Cleanupzusage.

`ObservationResult` ist frozen; `observation` ist von seiner Repräsentation
ausgeschlossen. Dies verhindert weder eine spätere Veränderung gehaltener
Module-/Spec-/Loaderobjekte noch ein bewusstes Auslesen privater Felder. Die
Rückgabe beschreibt die lokal geprüfte Aufnahme beim Abschlussvergleich,
keinen dauerhaft gültigen Zustand. Erneutes `validate_profile` prüft gehaltene
Objektkohärenz und Skalare, aber keine heutige `sys.modules`-Mitgliedschaft,
keine aktuellen Suchpfade, Finder oder Hooks. Ein ausgetauschter Cacheeintrag
kann bei unverändertem gehaltenem Objekt weiter rein matchen. Für eine spätere
aktuelle Runtimeverwendung ist eine frische Aufnahme nötig; auch diese ist
keine atomare Runtime- oder Herkunftsattestation. Die gewählte Kontrollruntime
bleibt ausdrücklich angenommen.

Der vorhandene direkte Testskriptbootstrap nimmt auf Linux mit `-I -S -B`
die Records vor `unittest.mock` auf und prüft den begrenzten tatsächlichen
Pfad gesondert. Portable Fixtures testen Abschlussobjektidentität, tatsächlich
gelesene Hashrecords, Fehler jeder Phase ohne Records, Legacykompatibilität,
private frozen Rückgabe und spätere Objekt-/Cacheveränderungen. Lokal auf
Windows mit CPython 3.12.14 bestanden 36 von 38 Methoden; genau zwei
Linux-Methoden wurden ausdrücklich übersprungen (0.040 s). Die Linux-CI
muss alle 38 Methoden ohne SKIP ausführen. Dieser lokale Nachweis ist kein
Linux-Runtimeerfolg.

Die Caps aus dem Profilvorschnitt und sämtliche false-Attestationsflags
bleiben erhalten. Konkrete Workerinventur, Scalarprojektion, kombinierter
Codec mit gemeinsamem 16-KiB-Budget und tatsächliche Kanal-/Consumptionbindung
bleiben offen. Ebenso offen bleiben DGN-Loaderverwendung, Importabschluss und
unabhängiger eigener Worker-Cleanup. Keine SQL-Ausführung, G13-/v1-/DEC-068-
Änderung, Incident- oder Capstonepromotion.

Primärquellen, geprüft am 2026-10-07: Python 3.12 beschreibt
[frozen Records und Repräsentation](https://docs.python.org/3.12/library/dataclasses.html),
[den veränderbaren Modulcache](https://docs.python.org/3.12/library/sys.html#sys.modules)
und [unabhängige Module-/Specmetadaten](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec).
Die engeren API- und Fehlergrenzen sind Projektimplementierung.
