# DGN-007 – Offline-Prozess- und Manifestkanten

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Status | `IMPLEMENTED_STATIC` für das Kantenprofil; Launcherentwurf `PROPOSED` |
| Profil | `dgn007-docker-sql-only/v1`, Prüfinterpreter Python 3.12 |
| Geltung | neun Pythonquellen, sechs SQL-only-Manifeste, elf SQLquellen und Incidentvertrag |
| Methodenentscheidung | offen; [Gate-Matrix](DGN_007_METHOD_DECISION_PACKAGE.md) |

## Statische Kontrolle bereits gebundener Bytes

[`dgn007_execution_edges.py`](../../Tests/Tools/dgn007_execution_edges.py)
ergänzt den [Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md).
Ein fester kontrollseitiger Callback erhält erst nach vollständiger Gitblob-/
Rohbytebindung und erfolgreicher Importprüfung dieselben gelesenen Bytes als
unveränderliches Mapping. Er liest keine Kandidatendateien erneut und führt
keinen Kandidatencode aus. Der bisherige Default-Report und die Bundle-CLI
bleiben erhalten; die neue CLI wählt ausschließlich diesen festen Callback.
Die Mappingansicht schützt hier unveränderliche `bytes`-Werte; sie ist kein
allgemeiner rekursiver Freeze beliebiger Pythonobjekte.
[Python MappingProxyType](https://docs.python.org/3/library/types.html#types.MappingProxyType).

```powershell
python -B Tests/Tools/dgn007_execution_edges.py --repository . --commit FULL_SHA1 --candidate CANDIDATE_DIRECTORY
python -B Tests/Static/test_dgn007_execution_edges.py
```

Die Platzhalter müssen ausdrücklich ersetzt werden. Der Prüfinterpreter muss
Python 3.12 sein. Ganzdatei-AST-Digests binden alle neun Pythonquellen an das
reviewte Profil; Kommentare und Layout dürfen bei neuer expliziter Commitbindung
abweichen, ausführbare AST-Änderungen scheitern geschlossen. UTF-8 wird separat
gegen die Python-Encodingdeklaration geprüft. AST-Schemata und Dumpdarstellung
sind versionsabhängig; es gibt keinen 3.13-/3.14-Äquivalenzclaim.
Auch die vorhandene Bundle-Bootstrapprüfung bleibt unverändert.
[Python AST](https://docs.python.org/3/library/ast.html),
[Python Encodingerkennung](https://docs.python.org/3/library/tokenize.html#tokenize.detect_encoding).

Ein `EdgeReport` ergänzt `declared_execution_edges_verified` und das feste
`source_profile`. Nur vollständiger statischer PASS setzt das Kantenflag.
`validation_scope=PROJECT_SEMANTIC`, `runtime_attested=false` und
`method_approved=false` bleiben explizit. Rohbyte-/LF-Bindungen behalten ihren
bisherigen Sinn. Feste Fehlercodes enthalten keine Kandidateninhalte.

## Reviewte deklarierte Kanten

| Quelle | Deklarierter Ziel-/Datenpfad im ausgewählten Profil |
|---|---|
| Runner `run_harness` | aktueller `sys.executable`, Harness, festes Manifest und Docker-Targetargumente |
| Docker-Target | feste Proxydatei als SQLcmd-Shim; externe Docker-/Shell-/SQLcmd-Auflösung |
| Harness SQLphase | lokaler Manifest-SQLpfad, Prozesshelper und Proxy |
| Proxy | live gelesene SQLdatei → Docker-stdin; externe SQLcmd-Datei im Container |
| Runner Recovery | fester `90_Cleanup.sql`-Pfad über denselben Prozesshelper |
| Runner Capture | fester Incidentvertrag → bestehender Vertragsparser |
| Prozesshelper | vorhandene OS-Prozesssteuerung einschließlich Windows-/POSIX-Grenzen |

Die Tabelle und `DECLARED_EDGES` sind reviewte Deklarationen, keine automatisch
berechnete Reachability oder tatsächliche Prozessbeobachtung. Der vorhandene
Host-Targetpfad mit `host_sqlcmd_target.py` und generische Sessionmanifeste gehören
nicht zum ausgewählten Docker-/SQL-only-Profil. Der Sessionorchestrator bleibt
wegen des unbedingten Harnessimports als Quelle gebunden. Python-Ganz-AST-Bindung
ist ein konservatives Änderungsprofil, kein Interpreter oder allgemeiner
Sandbox-/I/O-Sicherheitsbeweis.

Die sechs Manifeste sind strukturell exakt gebunden: Phasenreihenfolge,
SQL-only-Art, relative SQLpfade, Datenbankrolle, Required-/Summarypflicht und
Phasenbudgets sowie 180 Sekunden reguläres und 60 Sekunden Cleanupbudget.
Mit Cleanup sind es 4/5/6/8/8/8 Phasen für Setup/Fenster/Profil/AB/BA/AA.
Unbekannte Felder, doppelte JSONkeys, nicht erlaubte Zahlenformen und abweichende
Projektionen werden abgelehnt. JSON verwendet die bestehenden begrenzten
Dateibytes und zusätzliche Struktur-/Zahlengrenzen; ein Knotencheck nach Parse
ist kein allgemeiner harter Parser-Speicherbeweis.
[Python JSON](https://docs.python.org/3/library/json.html).

Der unveränderte v1-Incidentvertrag ist außerhalb `source_sha256` durch seine
kanonische Policy gebunden. Die exakt 14 bestehenden Schlüssel werden gegen
LF-normalisierte Quellenbytes geprüft: elf SQLdateien und drei Kontrollmanifeste.
Die älteren Setup-/Fenster-/Profilmanifeste liegen weiterhin außerhalb dieses
14er-Vertrags, sind aber Kandidatenbyte- und Projektionsgebunden.
Alle elf SQLdateien werden auf SQLCMD-Zeilenbefehle einschließlich unbekannter
Colonbefehle und `!!` geprüft; BOM/NUL scheitern geschlossen. Das ist keine
allgemeine semantische T-SQL- oder externe-I/O-Prüfung. Geändertes T-SQL kann
nach neuer Gitcommit- und passender Contract-Rebindung statisch akzeptiert werden;
die Fixtures zeigen diese Grenze ausdrücklich. Die Quellenfreigabe eines neuen
Commits bleibt eine unabhängige fachliche Aufgabe.

## Importumgebung und Launcher – ausdrücklich vorgeschlagen

Ein späterer Launcher müsste vor jedem Start mindestens folgende Grenzen
schließen; dieser Schnitt implementiert oder startet ihn nicht:

1. Kontrollseitigen Launcher und festgelegten Python-3.12-Interpreter samt
   Stdlib und tatsächlichen Toolidentitäten unabhängig vertrauen und binden.
   `PATH`, `sys.executable`, Dockerdaemon, Container-Shell und SQLcmd-Suche sind
   heute externe Vertrauensgrenzen, kein Nachweis ihrer verwendeten Identität.
2. Kandidatenbytes vor und während ihrer Verwendung unveränderlich halten und
   tatsächliche Code-/SQL-/Contractlesezugriffe an das freigegebene Bundle binden.
   Vor-/Nachstat, Kandidaten-PASS und aktuelle live gelesene Pfade ersetzen das
   nicht. Actor, Rechte, Zugang, CID vor jeder Aktion, Datenbankgeneration und
   physischer Host brauchen unabhängige Belege.
3. Eine minimale kontrollierte Importumgebung entwerfen: expliziter Einstieg,
   frischer Interpreterzustand, kein fremdes `Tests`-Package, keine übernommenen
   `sys.modules`-/Hook-/Suchpfadsubstitutionen. `-I -S` ist ein zu prüfender
   Startkandidat: isolierter Modus und abgeschaltete `site`-Initialisierung.
   Die vorhandenen Bootstrapblöcke und Namespacepackages müssen dann trotzdem
   gegen die tatsächliche Auflösung geprüft werden. Flags allein attestieren
   keine verwendete Closure.
4. Start-, Rückgabe-, Stop-/Drain- und Cleanupreihenfolge kontrollseitig
   begrenzen und unabhängig prüfen. Die heutige Proxy-/Target-Vorpufferung und
   erneut gesuchte SQLcmd-Datei bleiben offen; der äußere Outputcap ist kein
   durchgängiger Byte-/Prozesskettenbound.

Dies ist ein Entwurf, keine normative Methodenwahl oder zusätzliche
Runtimeautorisierung. Die Flagsemantik ist dokumentiert in
[Python Kommandozeile](https://docs.python.org/3/using/cmdline.html#cmdoption-I)
und [site](https://docs.python.org/3/library/site.html).

## Gegenproben und verbleibender Schnitt

Die 26 [Edge-Testmethoden](../../Tests/Static/test_dgn007_execution_edges.py) verändern
auch den referenzierten synthetischen Commit: Manifest-/AST-/Contractabweichungen
erreichen dadurch die neue Kontrolle statt nur die vorgelagerte Byteprüfung.
Callbackreihenfolge, unveränderliche Bodies, Defaultkompatibilität,
Encoding-/SQLCMDgrenzen, Quellenhash-Rebindung und ein Ausführungssentinel
werden getrennt geprüft. Bestehende 36 Bundle-Gegenproben bleiben im
[statischen Workflow](../../.github/workflows/dgn007-source-bundle.yml) erhalten;
die neuen Tests kommen additiv hinzu. Kein SQL-/Docker-/Launcherstart.

Der getrennte [synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
portable Budgetgegenproben und feste eigene Linux-Kindfälle. Die neun heutigen
Laufzeitquellen und v1/G13 bleiben erhalten; keine reale Laufzeitmachbarkeit.
Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Noch keine Probeimplementierung oder Importausführung. Nächster kleiner Schnitt ist ein separater begrenzter Linux-/Python-3.12-Import-Only-Prototyp mit Shadowing-/Austausch-/Alias-/Replay- und Cleanupgegenproben. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation. Alle Methodengates,
Import-/Actor-/CID-/Zugangs-/Hostgrenzen und Acquisition bleiben offen.
PR68 und der zurückgestellte API-Schnitt behalten ihre Grenze. Keine Incident-,
Ursachen-, Mitigations-, Capstone- oder Szenariopromotion.
