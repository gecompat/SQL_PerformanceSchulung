# DGN-007 – Offline-Quellenbundle-Verifier

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Status | `IMPLEMENTED_STATIC` |
| Geltung | feste Kandidatenbytes und deklarierte AST-Imports; keine Ausführung |
| Methodenentscheidung | offen; [Gate-Matrix](DGN_007_METHOD_DECISION_PACKAGE.md) |

## Implementierter Umfang

[`dgn007_source_bundle.py`](../../Tests/Tools/dgn007_source_bundle.py) prüft
einen bereits bereitgestellten Kandidatenordner gegen einen ausdrücklich
angegebenen vollständigen lokalen SHA-1-Commit. Die kontrollseitige Policy ist
fest im Verifier definiert und wird niemals aus dem Kandidaten geladen.
Git liest originale Blobs ohne Replaceobjects, Lazyfetch, Textconv, Filter oder
Archiveexport. Kandidaten werden weder importiert noch ausgeführt.

Die reviewte Vereinigung umfasst 27 Mitglieder: neun Pythonquellen
(Runner, Target, Proxy, Harness, Sessionorchestrator, Prozesshelper,
Projection, Transportdecoder und Prospektivevaluator), elf SQLquellen,
sechs Manifeste und den Incidentvertrag. Die vollständigen relativen Pfade
stehen in `PYTHON_MEMBERS` und `DATA_MEMBERS`; die drei Einstiege sind Runner,
Proxy und Harness. `orchestrate_sessions.py` gehört wegen des unbedingten
Harnessimports auch zum SQL-only-Pfad. Dies ist die derzeit reviewte Vereinigung,
kein automatisch ermittelter Nachweis aller später tatsächlich verwendeten
Dateien. SQL-/Manifestinhalte werden bytegebunden, nicht neu semantisch bewertet.

```powershell
python -B Tests/Tools/dgn007_source_bundle.py --repository . --commit FULL_SHA1 --candidate CANDIDATE_DIRECTORY
python -B Tests/Static/test_dgn007_source_bundle.py
```

`FULL_SHA1` und `CANDIDATE_DIRECTORY` sind explizit zu ersetzende Platzhalter.
Ein normaler Checkout kann durch CRLF-Konvertierung abweichende Rohbytes besitzen.
Der Verifier erstellt und extrahiert selbst keine Archive oder Bundles.

## Bindung und Ablehnung

`PASS_STATIC_CANDIDATE` verlangt genau die feste Mitgliederliste, reguläre
Dateien und bytegleiche Gitblobs, danach die deklarierte Importprüfung.
`FAIL_STATIC_CANDIDATE` liefert einen festen Fehlercode. Exitcodes sind 0/1.
Ausgabe enthält keine Kandidateninhalte, lokalen Pfade oder Gitfehlermeldungen.
`runtime_attested` und `method_approved` sind stets `false`.

`raw_binding` bindet die sortierten `[relativer Pfad, SHA256(Rohbytes)]`-Zeilen
als kompaktes ASCII-JSON; `lf_binding` verwendet separat ausschließlich
CRLF→LF-normalisierte Bytes. Beide Bindungen erscheinen nur nach vollständigem
PASS. LF-Gleichheit erlaubt keinen Byte-PASS: EOL-Abweichung ergibt
`RAW_BYTES_DIFFER`, gegebenenfalls mit `logical_text_equivalent=true`.
BOM, einzelnes CR und fehlender Schlusszeilenumbruch sind Inhaltsänderungen.
Bei frühzeitigem Lese-/Limitfehler wird keine vollständige Textgleichheit behauptet.

ASCII-Pfade sind relativ, kanonisch und portabel; Traversal, absolute Pfade,
Backslashes, leere Komponenten, Windowsgerätenamen, ADS, abschließende Punkte
oder Leerzeichen werden abgelehnt. Casekollisionen und doppelte Policyeinträge
scheitern vor Set-Konversion. Zusätzliche Dateien und leere Verzeichnisse sind
unzulässig. Alle Root-/Elternkomponenten werden vor Auflösung per `lstat`
auf Links/Reparsepoints geprüft; Dateien dürfen keine Hardlinks sein.
Git-Symlinks und Submodule sind keine zulässigen Quellmitglieder.
Vor-/Nachstat und begrenztes Lesen erkennen bestimmte Änderungen während des
Snapshots; sie attestieren weder einen atomaren Snapshot noch spätere Immutabilität.

## Deklarierte Imports und Grenzen

Nur absolute literal deklarierte Imports auf exakt erlaubte Module und
reviewte Stdlibnamen werden akzeptiert. Relative/Wildcardimports, unbekannte
Module, bekannte dynamische Import-/Execmuster sowie direkte und importierte
`sys.path`-/Hook-/Modulezugriffe bleiben geschlossen abgelehnt.
Zwei vorhandene Suchpfadbootstrapblöcke sind separat durch exakte AST-Digests
gebunden; Änderungen daran werden abgelehnt. Kein `find_spec`, Parentimport
oder Kandidateninterpreter wird zur Prüfung ausgeführt.

Der Graphnachweis ist kein allgemeiner Python-Sandbox- oder Resolverbeweis.
Indirekte dynamische Konstruktionen lassen sich damit nicht allgemein ausschließen.
Insbesondere `Tests`/`Tests.Contracts` sind Namespacepfade: fremde reguläre
Packages, `sys.modules`, `PYTHONPATH`, Site-/`.pth`-Verarbeitung und die tatsächliche
Bootstrapumgebung bleiben für einen späteren Launcher zu schließen. Auch
Prozessaufrufe, manifestgesteuerte Datenkanten und vertrauenswürdige Tools werden
hier nicht als tatsächlich verwendete Runtimeclosure attestiert.

Gitbinary, Python/Stdlib, Hostbetriebssystem und das aufrufende Dateisystem
sind ausdrückliche Vertrauensgrenzen. Die Prüfung schützt nicht gegen einen
feindlichen Administrator oder Gitbinary. Gitumgebungsumleitungen und globale/
systemweite Konfiguration werden entfernt; lokale Repositorykonfiguration und
Objektdateien gehören weiterhin zum vertrauenswürdigen Kontrollinput. Die
Prozessgrenze setzt voraus, dass diese lokalen Git-Objektlesebefehle keine
Nachfahren mit geerbten Pipes erzeugen. Sie ist kein allgemeiner harter
Prozessketten-/Drainbound für fremde Programme.
[Git](https://git-scm.com/docs/git),
[Windows-Pfadregeln](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file),
[Python-Importauflösung](https://docs.python.org/3/library/importlib.html#importlib.util.find_spec).

## Bounds und Gegenproben

Maximal 32 Mitglieder, 128 Verzeichniseinträge, 128 KiB je Datei,
1 MiB Gesamtinhalt und 100000 AST-Knoten. AST wird erst nach Rohbytebindung
geparst; das Knotenlimit ist nach dem begrenzten Parse kein allgemeiner
Hard-Sandbox-Speichernachweis. Git hat eine gemeinsame 30-Sekunden-Deadline,
je Aufruf höchstens fünf Sekunden plus begrenzte Stop-/Joinzeit. Stdout hat
aufrufspezifische Caps, Stderr 4096 Bytes; Überlauf wird verworfen und abgelehnt.
Diese lokalen Prüfgrenzen ersetzen keine Coordinator-/Observerbudgets.

Die 36 Testmethoden verwenden eigene temporäre Git-/Dateifixtures: veränderte
Executorbytes bei unverändertem Manifest, fehlende/zusätzliche/doppelte Mitglieder,
Pfadalias und Casekollision, CRLF und echte Inhaltsänderung, Exportattribute,
Gitreplace-/Umleitungsversuch, Hardlinks und Git-Symlink-/Submodulemodes,
Import-/Bootstrapmutation, NUL-Syntax,
Größen-/Eintrags-/AST-/Gitoutputlimits und einen Ausführungssentinel.
Darunter bindet ein Fall die tatsächlichen 27 Quellen am lokalen HEAD.
Unter Windows benötigen zwei echte Symlinkfälle OS-Berechtigung und werden
bei deren Fehlen ausdrücklich als SKIP ausgewiesen; Linux-CI führt sie aus.
Reparseattribute besitzen zusätzlich eine kontrollierte Gegenprobe.
Keine SQL-, Docker- oder Launcher-Runtime ist beteiligt. Der eigene
[Workflow](../../.github/workflows/dgn007-source-bundle.yml) ist statisch und
auf die sieben konkreten Verifier-/Dokumentpfade und die 27 exakten Quellmember begrenzt;
spätere Änderungen dieser Quellen lösen damit die Closuregegenprobe aus.

## Nächster begrenzter Schnitt

Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
ist statisch implementiert; der Import-/Launcherentwurf bleibt PROPOSED.
Ein kontrollseitiger Callback erhält optional erst nach Bytebindung und
Importprüfung die bereits gelesenen unveränderlichen Bytes. Der Default-Report
und die CLI dieses Verifiers bleiben unverändert. Der getrennte
[synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert,
ohne Integration in die neun Runtimequellen. Nächster kleiner Schnitt: getrennte numerische Gegenprobe von endlicher Oraclepopulation
über ausdrücklich deklarierte Fragmentrundung und separat vorgegebenen synthetischen
Style3-Text bis zur bestehenden Consumergewichtung. Keine SQL-Konversionsemulation,
Epsilon- oder Methodenfreigabe. Kein Launcherstart:
UsedBundle, Actor/CID, Datenbankgeneration, Zugang, physischer Host,
Acquisition, Kosten und kontinuierlicher Zustand bleiben offene Gates.
Normative Methoden-/Grenzänderungen benötigen eine ausdrückliche neue
Entscheidung. v1/G13/DEC-068, PR68 und der zurückgestellte interne API-Schnitt
bleiben erhalten; keine Incident-, Ursachen-, Mitigations- oder Capstonefreigabe.
