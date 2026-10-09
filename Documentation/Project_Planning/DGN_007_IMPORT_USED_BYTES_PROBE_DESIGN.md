# DGN-007 – Entwurf einer Importauflösungs-/UsedBytes-Probe

| Merkmal | Wert |
|---|---|
| Stand / Quellenabruf | 2026-10-07 |
| Repositorybasis | `fe5bdd25af429de347a7cdd75376d84eed9f6105` |
| Status | `DESIGNED`; nicht implementiert oder ausgeführt |
| Geltung | `PROJECT_SEMANTIC`; kontrollierter Import-Only-Entwurf |
| Grenze | keine vollständige Runtimeclosure, SQL-Runtime oder Methodenfreigabe |

## 1. Ziel und Aussagegrenze

Die Probe soll später belegen, welche bereits gebundenen Pythonbytes ihr
vertrauenswürdiger Loader bei drei festen Top-Level-Imports tatsächlich
kompiliert und ausgeführt hat. Ein Kandidatenhash oder eine nachträglich
ausgelesene Modul-Origin allein trägt diesen begrenzten Verwendungsbeleg nicht.
Dieser Entwurf erzeugt noch keinen solchen Beleg. `runtime_attested=false` und
`method_approved=false` bleiben für den heutigen Dokumentationsstand erhalten.

Grundlagen sind der [Bundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md), das
[Kantenprofil](DGN_007_EXECUTION_EDGE_VERIFIER.md) und das
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md).
Der neue technische Schnitt verändert weder die neun Runtimequellen noch
deren CLI. Top-Level-Ausführung ist von späteren Funktionsaufrufen getrennt;
auch erfolgreich importierte Funktionsdefinitionen sind keine ausgeführten
SQL-, Cleanup-, Parser- oder Evaluatorpfade.

## 2. Beobachtete feste Quellen und Einstiege

`PYTHON_MEMBERS`, `MODULES` und `DGN007.entrypoints` in
[`dgn007_source_bundle.py`](../../Tests/Tools/dgn007_source_bundle.py), Zeilen
27–75, sind die kontrollseitige feste Zuordnung. Sie wird nicht aus dem
Kandidaten übernommen. Die drei Einstiege werden jeweils in einem neuen
Worker unter ihrem Modulnamen importiert, niemals als `__main__` gestartet.

| Modulname | Repositorymember |
|---|---|
| `run_dgn007_automated_setup` | `Tests/Runtime/run_dgn007_automated_setup.py` |
| `execution_target` | `Tests/Runtime/execution_target.py` |
| `docker_sqlcmd_proxy` | `Tests/Runtime/docker_sqlcmd_proxy.py` |
| `run_demo` | `Demos/00_Framework/Tools/run_demo.py` |
| `orchestrate_sessions` | `Demos/00_Framework/Tools/orchestrate_sessions.py` |
| `sqlcmd_process` | `Demos/00_Framework/Tools/sqlcmd_process.py` |
| `Tests.Contracts.dgn007_capture_projection` | `Tests/Contracts/dgn007_capture_projection.py` |
| `Tests.Contracts.dgn007_collector_transport` | `Tests/Contracts/dgn007_collector_transport.py` |
| `Tests.Contracts.dgn007_prospective_acceptance` | `Tests/Contracts/dgn007_prospective_acceptance.py` |

Die feste Reihenfolge ist Runner, Proxy, Harness. Runner Zeilen 27–41 und
Target Zeilen 22–29 enthalten die vorhandenen Suchpfadbootstrapblöcke.
Harness Zeilen 22–23 importiert den Sessionorchestrator auch im SQL-only-Pfad.
Aus diesen Top-Level-Kanten werden acht eigene Module für Runner, eines für
Proxy und drei für Harness erwartet; spätere Imports dürfen diese Sollmengen
nicht stillschweigend erweitern. Die tatsächlichen Receipts müssen sie prüfen.
Die Wiederverwendung desselben Moduls zwischen verschiedenen Workers ist zulässig.
Die erwartete Vereinigung enthält neun importierte Pythonmember, kein UsedBundle
aller 27 Member und keinen Nachweis späterer Funktionspfade.

Der lokale Windows-Import `ctypes` in Runner Zeile 349 liegt im Funktionskörper
und wird durch diese Probe nicht ausgeführt. Die 18 Datenmember sind weiter
bytegebunden, aber nicht als gelesen oder verwendet belegt. Host-Target,
generische Sessionausführung und subprocessgestützte Hauptfunktionen bleiben
unaufgerufen; es gibt keinen `RunRecord` oder Incidentvergleich.

## 3. Dokumentierte Python-Fakten und Vertrauensannahmen

Die folgenden Fakten wurden am 2026-10-07 in der Python-3.12-Dokumentation
geprüft; deren Seitenkopf nennt aktuell 3.12.15. Das ist keine Prüfung eines
konkreten lokal installierten Interpreters oder seiner Bibliotheksbytes.

- `sys.modules` wird vor Findern geprüft. Namespacepackages können mehrere
  Suchpfadanteile besitzen und bei Pfadänderungen erneut suchen.
  Nach einem Importfehler können erfolgreich geladene Nebenmodule im Cache bleiben.
  [Python-Importsystem](https://docs.python.org/3.12/reference/import.html).
- `-I` entfernt unter anderem Scriptdirectory und User-Site aus dem Suchpfad
  und ignoriert `PYTHON*`; `-S` unterbindet die `site`-Initialisierung. Diese
  Flags ersetzen keine Kontrolle der tatsächlichen Finder und Modulcaches.
  [Python-Kommandozeile](https://docs.python.org/3.12/using/cmdline.html).
- `exec_module` führt Modulcode aus. `__file__` und `__spec__.origin` werden
  nicht automatisch synchronisiert. `LazyLoader` kann Ausführung verzögern;
  `find_spec` eines Untermoduls kann bereits dessen Parent importieren.
  [Python-Importlib](https://docs.python.org/3.12/library/importlib.html).

ENTWURFSANNAHME: Kontrollprogramm, Workerbootstrap, Interpreter, Stdlib und OS
sind vertrauenswürdig und während der Probe nicht durch fremde Akteure ersetzbar.
Vor einem späteren Start ist ein konkretes Python-3.12-Installationsprofil mit
Interpreteridentität, Version, erlaubten Bibliotheksroots und Erweiterungen
festzuhalten. Pfad, Versionsstring und Datei-SHA allein attestieren diesen Trust
nicht. Feindliche Administratoren und fremde Reaper sind keine geschlossene Grenze.
Ohne geeignetes Profil bleibt die Probe nicht ausführbar; kein PATH-Fallback.
Erster Kandidat ist CPython 3.12 auf Linux mit frischen isolierten Workers und
festem `-I -S -B`-Start; portable Formprüfungen sind davon getrennt.
Flags und reviewtes AST-Profil sind keine allgemeine Python-Sandbox. Nach einem
Importfehler wird derselbe Worker niemals für einen neuen Versuch wiederverwendet.

## 4. Gebundener Eingang und kontrollierte Auflösung

Der vertrauenswürdige Callback aus Bundle Zeilen 332–336 erhält ausschließlich
die schon gelesenen unveränderlichen `bytes`, nachdem alle 27 Member gegen
Gitblobs gebunden und Imports geprüft wurden. Derselbe Callback prüft zuerst
das unveränderte vollständige Kantenprofil. Erst danach darf er die Probe starten.
Kein Kandidatenimport, `find_spec` oder Workerstart gehört in den statischen Vorcheck.

Der Parent friert Commit, Rohbytebindung, Kontrollprofil und einen frischen
256-Bit-Nonce vor Transfer ein. Der feste Transfer enthält genau neun
Name/Member/Byte-Zuordnungen mit Einzelhashes; die gesamte 27er-Bindung bleibt
separater Kontext. Der Worker prüft Form, Duplikate, Größen und neun Hashes erneut.
Nonce ist Frischebindung zwischen vertrauenswürdigem Parent und Worker, keine
Signatur oder unabhängige Herkunftsattestation. Kandidaten liefern keine Receipts.

Ein eigener MemoryLoader kompiliert exakt die empfangenen Rohbytes, ohne
Live-Datei, `.pyc`, `SourceFileLoader`-Fallback oder nachträgliche LF-Konversion.
Alle Modulnamen sind exakt `MODULES`; Alias, Reload, doppelte Ausführung unter
anderem Namen und unbekannte Parentpackages werden geschlossen abgelehnt.
`Tests` und `Tests.Contracts` erhalten kontrollierte codefreie Packagespecs
ohne externe Namespaceanteile. Keine Kandidaten-`__init__.py` wird ergänzt.

Für `__file__` und `co_filename` dient eine eigene leere absolute Pfadstruktur
mit derselben relativen Tiefe. Sie enthält keinen Kandidatencode. Dadurch kann
der vorhandene `Path(__file__).resolve()`-Bootstrap berechnen, ohne den Loader
auf Live-Dateien umzulenken. Diese Origin ist ein kontrollierter Locator,
kein Beleg einer gelesenen Datei. Die beiden Bootstrapblöcke und ihre erwarteten sys.path-Zustände werden beobachtet und exakt geprüft; ein bereits vorhandener Eintrag bleibt ohne erneute Einfügung erhalten.

Der Resolver bedient eigene Module nur aus dem Mapping. Builtin-/Frozen-Module
und transitive Stdlibabhängigkeiten kommen ausschließlich aus dem vorab benannten
vertrauenswürdigen Installationsprofil; der globale geänderte `sys.path` wird
nicht als Suchraum verwendet. Das heutige `STDLIB` benennt direkte Importwurzeln,
nicht alle transitiven Bibliotheksmodule. Deren gemessene Origins bleiben getrennt
von den eigenen Byte-Receipts. Unbekannte Hooks, Roots oder Erweiterungen scheitern.
Das Profil benennt ausdrücklich verwendete Stdlibdirectories, gegebenenfalls
genau eine vertrauenswürdige Stdlibzipdatei und native Extensionloader/-dateien;
kein beliebiges Zip-/Site-Verzeichnis oder späterer Live-Pfad wird ergänzt.

Vor Import dürfen keine eigenen Namen/Parentpackages in `sys.modules` stehen.
Vertrauenswürdige vorab geladene Kontroll-/Stdlibmodule werden separat inventarisiert;
sie sind keine neuen Loader-Verwendungen. Kontrollierte Cachehits später im
selben Worker sind zulässig, müssen auf genau das bereits quittierte Modulobjekt
zeigen. Finder, Hooks, Modulcache und Packages werden vor und nach Import geprüft.
Keine LazyLoader: sämtliche begonnenen eigenen Imports müssen abgeschlossen sein.
Nach Abschließen der Sollmenge wird keine weitere eigene Ladung zugelassen und
kein Kandidatenfunktionsaufruf ausgeführt; unaufgerufene Funktionsimports bleiben offen.

## 5. Receipts und begrenzter Ergebnisclaim

Der vertrauenswürdige Loader erfasst vor `compile/exec` Workerordinal,
Importsequenz, Modulname, Member, Rohbytehash und kontrollierte Originbindung.
Nach vollständigem `exec_module` quittiert er Abschluss und Objektbindung;
nicht nur den Ursprungstext des Moduls. Beginn ohne Abschluss ist kein PASS.
Der Parent prüft sämtliche Receipts gegen seinen eingefrorenen Eingang,
Nonce, feste Einstiegsfolge und Sollmengen; manipulierte, doppelte oder
unvollständige Receipts sind Fehler. Ein Workerexitcode allein genügt nicht.

Nur ein später tatsächlich vollständig ausgeführter Import-Only-Versuch könnte
diesen Teilclaim liefern. Er würde weder Funktionsausführung, 27 verwendete
Member, Interpreter-/OS-Unangreifbarkeit noch vollständige Closure attestieren.
Das bestehende pauschale `runtime_attested` bleibt für die DGN-007-Runtime false;
ein späterer Bericht muss die beobachtete Importverwendung ausdrücklich separat
benennen. Methoden-, Actor-/CID-/Host-, SQL-, Acquisition- und Zustandsgates bleiben offen.
Öffentliche Reports enthalten feste Fehlerlabels und relative Member/Hashes;
absolute Origins bleiben privat, keine Rohfehler, Quelltexte oder Secrets persistieren.

## 6. Vorgeschlagene endliche Bounds und eigener Cleanup

Diese Grenzen gelten nur für die spätere Probe; sie sind nicht runtimevalidiert:

| Grenze | Vorschlag |
|---|---|
| Eingangsbytes | höchstens 128 KiB pro Member, neun Pythonmember zusammen höchstens 1 MiB |
| Transfer | je Worker binäre Längenrahmung, höchstens 1 MiB Bodies plus 16 KiB feste Metadata; zusammen höchstens 3 MiB plus 48 KiB |
| Workers | genau drei seriell, kein Retry; erste Pflichtverletzung stoppt weitere Starts |
| Records | je Worker höchstens neun eigene Modulabschlüsse plus zwei codefreie Parents und 256 Stdlib-/Kontrollmodule; insgesamt höchstens 768 Stdlib-/Kontrollmodule |
| Ausgabe | alle drei Workers/stdout+stderr zusammen höchstens 64 KiB, jede Scalarzeile höchstens 1024 Bytes; begrenzter Read vor Decode/Pufferung |
| reguläre Zeit | einmalige gemeinsame monotone 20-s-Deadline ab Callback-Probenbeginn einschließlich Trustcheck, Transfer, Import, Drain und Receiptprüfung |
| Cleanup | kumulativ höchstens 10 s gemessene Cleanupzeit für sämtliche eigenen Worker-/Pfadreste; jedes Segment erhält nur das verbleibende Budget |
| Gesamtfortschritt | höchstens 4096 I/O-Schritte, höchstens 64 aufeinanderfolgende Schritte ohne neue Bytes/EOF/Zustandsänderung |

Der vorhandene statische Vorcheck behält sein eigenes 30-s-Gitbudget; dies ist
keine harte 50-s-Wallclockzusage. Alle Caps gelten gleichzeitig; der globale
64-KiB-Cap dominiert auch 768 erlaubte Records mit jeweils höchstens 1024 Bytes.
Probenzeit darf weder je Worker, Poll noch Drain neu beginnen; letzte reguläre Prüfung erfolgt vor Erfolg.
Ein neuer Worker startet erst nach beendetem Cleanup des vorherigen. Die reguläre
20-s-Wallclock läuft auch während dieser Zwischen-Cleanups unverändert weiter.
Cleanupsegmente messen ihre gesamte monotone Laufzeit; ihre Summe reduziert den
10-s-Rest, niemals ein neues 10-s-Budget. Das Ergebnis folgt erst nach finalem Cleanup.
Erster Cleanupfehler bleibt dominant, spätere Recovery erzeugt keinen PASS.

Erster Implementierungskandidat ist ausschließlich Linux mit identitätsgebundener eigener
Prozessgruppe. Kein Reap des Leaders vor erforderlichem Gruppenstop; keine
PID-/Namenssuche fremder Prozesse. Ein möglicherweise nötiger Subreaper gehört
nur in den frisch gestarteten Kontrollworker mit Vorwert/Restoreprüfung.
Eigene Kinder-, Pipe-, Thread- und Pfadabwesenheit müssen tatsächlich geprüft
werden. Kill-Erfolg, Rootexit oder Ablauf des äußeren Workers beweisen sie nicht.
Windows bleibt für diese Prozessgrenze zunächst nicht unterstützt.
Der bestehende Streamingprototyp liefert Mechanismenkandidaten und begrenzte
eigene Linux-Evidenz, keine automatische Garantie für diesen anderen Worker.
Ununterbrechbarer Prozessstart, OS-/Hostverlust und harte Unterbrechung können
Cleanup UNKNOWN lassen; kein allgemeiner Kernel-, Speicher- oder Harddeadlineclaim.

## 7. Vorgesehene Gegenproben und Folgescope

Der erste Implementierungsteil ist jetzt das getrennte
[Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md). Es bereitet nur
gebundene Bytes und binäre Rahmung vor. Die getrennte
[synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md)
erprobt inzwischen tatsächliches Compile/Exec ausschließlich fester harmloser
Fixturebytes und ihre objektgebundenen Beginn-/Abschlussreceipts. Sie ist kein
DGN-Import- oder Auflösungsnachweis. Der getrennte
[Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md)
beobachtet inzwischen begrenzte aktuelle Kontrollbootstrapmetadaten und prüft
Übereinstimmung mit einer separat deklarierten Baseline. Die ausdrücklich
angenommene Kontrollruntime erhält dadurch keine Trustattestation. Der getrennte
[skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md)
ist `DESIGNED`: separat vorab gewählte Workerinventur und gemeinsamer
Eingangs-/Ordinal-/Phasenkontext. Der getrennte
[reine Matcher](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert.
Tatsächlicher Beobachtungsadapter, kombinierter Codec, Kanal- und Verbrauchsbindung
bleiben unimplementiert; die tatsächliche Parent-/Workerbindung ist noch nicht belegt. Die folgenden vollständigen Worker-/Loadergrenzen,
tatsächliche DGN-Importreceipts und Cleanup bleiben unimplementierter Folgescope.

| Gegenprobe | Erforderliches Ergebnis |
|---|---|
| fremdes `Tests`-/`json`-Package, CWD/PYTHONPATH/.pth, fremder Hook | kein Fremdimport; keine Suchpfaderweiterung als erfolgreiche Lösung |
| eigener Name schon gecacht oder eigenes Modulobjekt ausgetauscht | geschlossen ablehnen, auch bei gleicher Origin |
| Kandidat nach Byteprüfung ersetzt, Transferbyte geändert | Loader bleibt an alten Bytes gebunden beziehungsweise Hashfehler; keine Neuaufnahme |
| Aliasname, falscher Member, Replay/alter Nonce, doppelte Abschlussreceipt | kein PASS |
| zusätzliches ausführbares AST oder Top-Level-Sentinel | Ablehnung vor Workerstart am unveränderten Kantenprofil |
| Lazy-/unvollständiger Import, Outputoverflow, Timeout/Exit vor Pipe-EOF | kein Import-Only-PASS; eigener Cleanup bleibt Pflicht |
| fehlender Reap/Restore/Pfadabbau oder harter Parentabbruch | FAIL beziehungsweise UNKNOWN, niemals Cleanup aus Exit ableiten |

Vorgeschlagene spätere Dateien (NICHT VORHANDEN):
`Tests/Tools/dgn007_import_used_bytes_probe.py` und
`Tests/Static/test_dgn007_import_used_bytes_probe.py`. Kleine feste Fixtures und
die drei kontrollierten Imports bilden nach Review einen kleinen gewöhnlichen
Offlineimplementierungsscope, keine Aktivität dieses Docs-only-Schnitts.
Die bestehende Entwicklungsautorisierung umfasst diesen begrenzten technischen Offline-Schnitt.
SQL-/Docker-/Collector-Ausführung ist daraus nicht mitautorisiert; normative
Beweisart-, G13- oder Methodengrenzänderungen brauchen die bestehende materielle
Entscheidung. v1, DEC-068, historische FAILs, offene PR68 und API83f bleiben erhalten.
Kein RunRecord, Evaluatoraufruf, Incident-, Ursachen-, Mitigations- oder Capstoneclaim.
