# DGN-007 – Eingangsprotokoll der Importprobe

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Repositorybasis | `09608ec723c08e2be46cd1b3025817c402f674b1` nach PR81 |
| Status | `IMPLEMENTED_STATIC_INPUT_SLICE`; 27 Tests lokal PASS |
| Geltung | `PROJECT_SEMANTIC`; kontrollseitige Bytevorbereitung und Transportgegenproben |
| Grenze | keine Worker-, Loader-, Import-, SQL- oder Methodenattestation |

Der [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md)
wird in getrennt prüfbaren Teilen umgesetzt. Dieser erste Implementierungsteil
bereitet den kontrollseitigen Eingang vor. Er startet keinen Importworker und
führt keine Kandidatenbytes aus. Der vollständige Linux-/Python-3.12-Prototyp
bleibt offen. Die bestehenden neun Runtimequellen und alle 27 Bundlemember
bleiben unverändert.

## Eingang und Bindung

Der unveränderte [Bundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
prüft zunächst alle 27 Member gegen originale Gitblobs am ausdrücklich
angegebenen Commit. Sein Callback erhält die tatsächlich gelesenen,
unveränderlichen Bytes. Darauf läuft zuerst das unveränderte
[Ausführungskantenprofil](DGN_007_EXECUTION_EDGE_VERIFIER.md) unter Python 3.12.
Nur nach beiden Prüfungen darf ein vorbereiteter Eingang entstehen.

Die Vorbereitung hält die neun Pythonmember samt fester Modul-/Memberzuordnung,
Rohbytehashes, Commit, separater 27-Member-Rohbytebindung und einer frisch
erzeugten 256-Bit-Nonce fest. Sie liest keine Kandidatendatei erneut. Die
Nonce bindet einen Transport an den erwarteten kontrollseitigen Eingang;
sie ist keine Signatur, Actorattestation oder alleiniger Replaynachweis.
`PreparedInput` ist eine Kontrollstruktur, kein Vertrauensnachweis durch ihre
Klasse oder Feldwerte. Der Aufrufer muss den unveränderten erfolgreichen
`prepare_input`-Rückgabewert als Parent-Snapshot behalten. Encoder und Decoder
validieren Form und Gleichheit; manuell konstruierte Records durchlaufen damit
keinen zusätzlichen Git- oder AST-Vorcheck.

## Begrenzte binäre Rahmung

Ein Frame enthält feste Metadata und unveränderte Python-Rohbytes. Pro Member
gelten höchstens 128 KiB, für alle neun Bodies zusammen höchstens 1 MiB und
für Metadata einschließlich des 16-Byte-Headers höchstens 16 KiB. Die Rahmung
verwendet keine Base64-Darstellung.
Der Decoder erhält bereits endliche Bytes und prüft deren Gesamtgröße vor
Metadata-Decoding oder Bodyaufnahme. Er ist kein Streamreader: begrenzte
Pipeaufnahme, die gemeinsame 20-s-Deadline, kumulativer Cleanup und die drei
seriellen Worker gehören erst zum nachfolgenden Ausführungsteil.

Der Decoder vergleicht Form, Reihenfolge, exakte Zuordnung, Größen,
Rohbytehashes und Kontext mit dem kontrollseitigen eingefrorenen Eingang.
Ein geänderter Transport erzeugt keinen neuen vertrauenswürdigen Snapshot.
CRLF und LF bleiben für diese Rohbytebindung verschieden. Die getrennte
LF-Äquivalenz des bestehenden Bundle-Verifiers ersetzt die Rohbyteprüfung nicht.

## Validierung und Restumfang

Die ausführbaren Gegenproben liegen in
[`test_dgn007_import_probe_input.py`](../../Tests/Static/test_dgn007_import_probe_input.py).
Sie prüfen gültige Rahmung und manipulierte, übergroße, abgeschnittene oder
verlängerte Frames sowie falsche Kontext-, Hash- und Modulbindungen. Temporäre
Gitfixtures prüfen den tatsächlichen unveränderten Vorcheck; die Fixturebytes
werden nicht importiert oder ausgeführt.

```powershell
python -B -X utf8 Tests/Static/test_dgn007_import_probe_input.py
```

Der Befehl benötigt Python 3.12 für das bestehende AST-Profil. Lokale Windows-
und Linux-CI-Ergebnisse werden getrennt dokumentiert. Am 2026-10-07 liefen
alle 27 Methoden unter Python 3.12.14 auf Windows ohne SKIP erfolgreich:
21 Protokollgegenproben und sechs temporäre Git-/Vorbereitungsfixtures.
Die letzte vollständige Ausführung dauerte 28,514 s. Der Scope umfasst auch
einen tatsächlichen Dateiaustausch nach dem Freeze und ein commitgebundenes
zusätzliches ausführbares AST, das vor der Vorbereitung abgelehnt wird.
Der PR-/Main-CI-Nachweis steht für diesen Quellstand noch aus. Der Slice attestiert
weder verwendete Importbytes noch Importabschluss oder Prozesscleanup.
`runtime_attested`, `import_used_bytes_attested` und Methodenfreigabe bleiben
false. G13, v1, DEC-068, die offene PR68 und die zurückgestellte Capture-API
bleiben erhalten; es entsteht kein Incident- oder Capstonebeleg.

Als nächster Teil folgen das konkrete vertrauenswürdige Interpreter-/Stdlibprofil,
der kontrollierte Rohbyte-Loader, bindende Beginn-/Abschlussreceipts und eigene
Linux-Worker mit gemeinsam begrenzter Aufnahme und unabhängig überprüftem Cleanup.
Erst tatsächlich abgeschlossene Imports dürfen einen gesonderten Import-Only-Claim
tragen. Der Entwurf bleibt für diese noch nicht implementierten Grenzen maßgeblich.
