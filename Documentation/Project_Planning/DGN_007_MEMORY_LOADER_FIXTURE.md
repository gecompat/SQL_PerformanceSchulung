# DGN-007 – synthetische Memory-Loader-Komponente

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Repositorybasis | `a4d5645a828de59b2aad8e28e10fcaa789df69ee` nach PR83 |
| Status | `IMPLEMENTED_SYNTHETIC_LOADER_COMPONENT`; Validierung siehe unten |
| Claim | `SYNTHETIC_LOADER_COMPONENT_ONLY` |
| Geltung | `PROJECT_SEMANTIC`; feste synthetische Loaderfälle |
| Grenze | keine DGN-Import-, Worker-, SQL-, Cleanup- oder Methodenattestation |

Diese getrennte Komponente erprobt einen Teil des
[Import-/UsedBytes-Entwurfs](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md).
Sie führt ausschließlich vier im Tool festgelegte harmlose synthetische Fälle
über `create_module` und einen direkten `exec_module`-Aufruf aus. Das
[Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md) wird dabei nicht
als ausführbare Quelle verwendet. Die neun DGN-Pythonquellen und das vollständige
27-Member-Bundle bleiben unverändert; der vollständige Importprototyp bleibt offen.

## Ausführung und Bindung

Der einzige öffentliche Ausführungseinstieg
[`exercise_fixture(FixtureCase)`](../../Tests/Tools/dgn007_memory_loader_fixture.py)
nimmt einen festen Enumfall an. Er akzeptiert keine Quellbytes, Dateipfade,
`PreparedInput`-Records oder Callbacks. Die zwei Erfolgsfälle setzen lediglich
`SYNTHETIC_VALUE = 7` mit LF beziehungsweise CRLF. Zwei getrennte Fälle erzeugen
einen Compile- beziehungsweise Execfehler. Es gibt keine Fixture mit I/O,
Imports, Prozessstart oder Endlosschleife.

Eine private Session hält die tatsächlichen Modul- und Specobjekte sowie die
unveränderlichen Fixturebytes. `BEGIN` entsteht unmittelbar vor `compile`
der gehaltenen Rohbytes. Nach tatsächlichem `exec` entsteht `COMPLETE` nur bei
unveränderter Objektidentität, Modul-/Specbindung, Kontext und erwartetem Effekt.
Name, synthetischer Member, Rohbytehash, frische 256-Bit-Nonce, Kontextdigest,
Sequenz und Objektplatz binden die beiden Receipts. Der Objektplatz ist keine
Objektattestation; die private Session vergleicht die gehaltenen Liveobjekte mit
`is`. LF und CRLF bleiben in Rohbytes und SHA-256 verschieden.

Jeder Fixturebody ist auf 4 KiB und jede Session auf acht Receipts begrenzt.
Erfolg verlangt genau `BEGIN` und `COMPLETE` in dieser Reihenfolge. Compile-
und Execfehler liefern keinen Abschlussbeleg. Doppelte Aufrufe, fremde
Objekte, geänderte Bindungen und fehlende oder manipulierte Receipts werden
abgelehnt. Öffentliche Fehlerberichte enthalten feste Fehlercodes und keine
Quellbytes oder ungefilterten Exceptions. Die Nonce ist keine Signatur und
kein alleiniger Replay- oder Actornachweis.

Der direkte Loaderaufruf prüft keine Importauflösung. Es gibt keinen Finder,
keine Eintragung in `sys.modules`, keinen Suchpfadumbau und keinen Source-/PYC-
Fallback für diese Fixturebytes. Der kontrollseitige Code und Interpreter
bleiben vorausgesetzt vertrauenswürdig. Der Loader ist keine Sandbox.
Es gibt keine Zeit-, Prozess- oder Cleanupattestation. Öffentliche Reportflags
`runtime_attested`, `import_used_bytes_attested` und `method_approved` bleiben
auch bei synthetischem Erfolg false.

## Validierung und Restumfang

Die Gegenproben stehen in
[`test_dgn007_memory_loader_fixture.py`](../../Tests/Static/test_dgn007_memory_loader_fixture.py).

```powershell
python -B -X utf8 Tests/Static/test_dgn007_memory_loader_fixture.py
```

Am 2026-10-07 bestanden alle 27 Methoden unter Python 3.12.14 auf Windows ohne
SKIP; die letzte vollständige Root-Ausführung dauerte 0,013 s. Geprüft wurden
unter anderem tatsächlicher Byteinput an `compile`, fehlende Ausführung trotz
passendem Effekt, Modul-/Spec-/Loaderaustausch, Alias-/Kontext-/Receiptänderung,
mehrfache Aufrufe, RNG-Ausfall und unveränderte globale Importstrukturen. Der
unabhängige Review fand einen finalen Objektaustausch zwischen `COMPLETE` und
Berichterstellung; die korrigierte Reportprüfung verwirft auch diesen Fall.
Zusätzlich bestanden die elf projektbezogenen Validatoren und fünf betroffenen
Frameworkbefehle. PR84 integrierte den Slice als Squash
`457288472e53bb8cda2cc74d2921fd29a570e4b5`. Die getrennten Linux-Runs
[PR84](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37633080400)
und [Main](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37633600019)
bestanden jeweils Bundle36, Edge26, Input27 und Loader27 ohne SKIP. Der
PR-Checkout war `94fe4e016bb6aa3dd8b600651ba2d990a7571f6d` am exakten Head/Base;
der Main-Checkout war der genannte Squash. Keine DGN-Importausführung daraus.
Ein synthetischer Erfolg ist kein erfolgreicher DGN-Import.
Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md)
nimmt inzwischen begrenzte Bootstrapmetadaten auf und vergleicht sie mit
einer separat deklarierten Baseline, ohne Trustattestation. Als nächste Teile
bleiben getrennte Parent-/Worker-Profilbindung, feste Auflösung und tatsächliche
Verwendung der vorbereiteten neun Quellen,
vollständige Importabschlussreceipts sowie drei begrenzte eigene Linux-Worker
mit unabhängig geprüftem Cleanup offen. G13, v1, DEC-068 und die zurückgestellte
Capture-API bleiben unverändert; kein Incident-, Capstone- oder Szenariobeleg.

Quelle für die Python-Schnittstellen, geprüft am 2026-10-07:
[Python 3.12: Loader.create_module und Loader.exec_module](https://docs.python.org/3.12/library/importlib.html#importlib.abc.Loader).
Die Quelle beschreibt Modulinitialisierung und Ausführung; die engere Fixture-
und Receiptbindung ist projektspezifischer Code und separat zu prüfen.
