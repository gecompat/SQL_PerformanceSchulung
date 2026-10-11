# IDX-012: begrenzte tatsächliche Phasenkosten

Stand: 2026-10-11. TSK-006/DEC-074; öffentliche Implementierungsvorstufe,
kein Manifest, keine freigegebene Demo und keine vollständige TP-PERF-Abnahme.
Der [kanonische Ausführungsstand](CURRENT_EXECUTION_STATUS.md) autorisiert die
weitere lokale ANN-Welle. Abgeschlossene DML-/Rebuild-/Speicherbudgets bleiben
geschlossen; ihre Resultate attestieren diese neue Aufnahme nicht.

## Methode und Aussagegrenze

Der Default bleibt unverändert. Der Entwurf sieht ausschließlich `--mode
drop-rebuild --capture-storage --capture-costs` für 30_CostBoundary und
50_CostRebuild vor. Dieser Modus ist nach den unten dokumentierten Client-FAILs
vor jedem SQL-Aufruf gesperrt; die folgenden Absätze beschreiben den Entwurf.
Feste absolute SQLCMD-`:r`-Pfade lesen die unveränderten öffentlichen
30_DmlBoundary/50_DropRebuild ein. Vor und nach der jeweils vollständigen
Phase steht eine eigene Kostenaufnahme. `GO` beendet die vorherige Batch,
bevor der nächste Sessioncounterpunkt gelesen wird. Beide Punkte stammen
aus derselben tatsächlichen Verbindung; eigener temporärer Kontext bindet
Session/DB/Token/Stage und endet mit der Verbindung, ohne neues dauerhaftes
Objekt. Die Pfade/Stages sind ausschließlich feste Controllerauswahl und
können nicht durch freie Caller-Variablen überschrieben werden.
Die zwei Include-Pfade werden ausschließlich als feste Prozess-ENV-Werte
übergeben; geerbte gleichnamige Werte werden ersetzt, die Elternumgebung bleibt
unverändert. CostStage bleibt feste CLI-Variable. Eigene Executor-Adapter müssen
den öffentlichen `client_environment(command, environment)`-Helper beim
start_sqlcmd-Aufruf verwenden; sonst ist der Kostenpfad nicht attestiert.

23_CostFrame prüft vollständige FWK-002-Marker, persistierte Originalbaselines,
tatsächlich Preview/MAXDOP 1/1, 999 Quellenrows, Indexzahl und separat vor
Katalogsubqueries erfasste Transaktionswerte 0/0. Tatsächliche COST_GUARD-Werte
werden vor einem Grenzfehler ausgegeben; sie ersetzen keine vollständige
PHASE_COST-Aufnahme. Genau eine eigene Session-/TempDB-Row und beide eigenen
Dateistatistiken sind erforderlich. Der Client gleicht die Datei-IDs mit der
vorherigen vollständigen Storage-Baseline ab, prüft sämtliche inneren
Identitäten/Counts/strikten Integer und monotone Counter. Fehlend, null, bool,
Reset und gemessene null bleiben verschieden; keine Ersatzwerte. Scalarlimit
120000 UTF-16-Bytes und native Clientbreite 65535, unverändert `-y 0` ohne
`-W/-h`; Grenzüberschreitung ist FAIL, keine Trunkierung.

- Session: cpu_time in Millisekunden sowie reads, logical_reads und writes.
  `writes` zählt Dirty-Page-Markierungen, auch mehrfach derselben Seite,
  **keine tatsächlichen Datei-Writes**. Aggregation am Batchende; deshalb GO.
- TempDB: getrennte User-/Internal-Alloc-/Dealloc-Seiten, je 8192 Bytes.
  Ausschließlich abgeschlossene Tasks der eigenen Session, ohne IAM-Seiten
  und laufende Tasks. Null beweist keine vollständige TempDB-Kostenfreiheit.
- Dateien: eigene DB/Datei, sample_ms, tatsächliche num_of_writes,
  num_of_bytes_written und io_stall_write_ms als Counterdifferenzen.
  Kumulative Dateipunkte aller Writer einschließlich Hintergrundarbeit;
  keine exklusive Zuordnung zum Index oder zur eigenen Session.

Die Phasen enthalten positive/negative DML-Kontrollen, Indexbau beziehungsweise
Drop/Commit/Rebuild/Suchkontrollen sowie Beobachtung und Instrumentierung.
Somit WHOLE_PHASE_INCLUDING_CONTROLS_AND_OBSERVATION, isolated_build_costs
NOT_ESTABLISHED und full_worker_costs NOT_ESTABLISHED. Keine Benchmarkserie,
Wait-, vollständige Worker- oder allgemeine Freshness-/Generationsabnahme.
Alle bisherigen Quellen-, Distanz-, Metadaten-, Restore- und Abwesenheits-
kontrollen bleiben erforderlich.

## Endliches Budget und Checkpoints

Ein Implementierungsverantwortlicher und ein enger unabhängiger Quellenreview
für Countersemantik, Batch-/Includebindung, Eigentum, Budget und Cleanup.
Keine administrative Reviewkette. Neuer eigener Parent im ignorierten
Runtime/IDX012_COSTS: höchstens zwei stabile Kandidaten/vier **serielle** neue
eigene 17.0.5005.3-Container. Zwei positive vollständige Lifecycles desselben
stabilen Kandidaten sind erforderlich. FAIL schließt den Kandidaten; keine
unveränderte Wiederholung. Kandidat 2 benötigt geschlossenen FAIL, semantisch
geänderte ausführbare Eingaben und Closure des betroffenen neuen Befunds.
Nach weiterem ungelösten Fehler: anhalten und tatsächlichen Checkpoint über
PR integrieren. Kein stilles Zurücksetzen alter oder dieses Budgets.

Unveränderte Effekte: ausschließlich unveränderliches lokales 2025-Image,
vier CPUs/sechs GiB, eigene markierte DB, float32 VECTOR(3), 999 Rows und
höchstens 1000 innerhalb der zurückgerollten INSERT-Kontrolle. Nur eigene
Preview/MAXDOP mit persistierter tatsächlicher Originalbaseline. Keine Pulls,
Host-/Cloud-/Modell-/ONNX-Wirkung. Ein Arbeitsclient nach dem anderen.
300-s-Deadline einschließlich Startup; SQL-Recovery 20 s innerhalb gesamter
60 s ab erstem Restoreclient. Neue Clients restaurieren beide Optionen,
attestieren unabhängig vor markergebundenem Drop und prüfen DB-Abwesenheit.
Parent bindet eigene CID/Image/Name/Label/Ressourcen vollständig und prüft
tatsächliche CID-/Namensabwesenheit. sa nur im eigenen Container; Secret nur
ENV, nie Passwortargv. Minimalrollen-/Hard-Abort-Abnahme bleiben offen.

Admission erst nach Quellenclosure und öffentlicher Pfad-/Hashbindung.
Checkpoints: reine Gegenproben, stabiler Review, tatsächliche Runtime,
aktuelle Head-/Main-Gates, kompletter Treevergleich, Synchronisierung und
eigener lokaler/remote Branchabbau. Begonnener Schnitt wird über PR integriert.
Modell-/Tokenverbrauch unbekannt.

## Aktueller Nachweisstand

Kosten-Slice FAIL, nach zwei Kandidaten angehalten und öffentlicher Kostenmodus
vor jedem SQL-Aufruf gesperrt. Keine tatsächliche SQL-Kostenaufnahme oder Kostenclaim.
Private synthetische Proben ersetzen weder öffentliche Bindung noch Runtime.

Erste öffentliche Gegenproben: 19 Controller-/12 Kosten-/10 CI-Auswahltests PASS.
Enger unabhängiger Quellenreview ohne offene P1/P2 abgeschlossen; keine eigene
SQL-/Runtimeattestation des Reviewers. Öffentliche Ausführungs-SHA256:

| Quelle | SHA256 |
|---|---|
| 23_CostFrame.sql | 90F9945846691D3EA8B39917ECA1202097A046B6D6561135AC01A1C66DC937D7 |
| 30_CostBoundary.sql / 50_CostRebuild.sql | D6E37506EE9B4D61C5AEEDE276FD05EF02C029D1A029A1D085D51C00FCD582E3 |
| cost_evidence.py | EB41A866190C673523D1070F85741E1C3FB60B6EDA919E72A814077A9E2F60FE |
| run_profile.py | 0247223D0EB00594FDC38F28BE06F6A20267C6D861205E631A0B56CA9E038250 |
| eigener ignorierter Parent | CCAFC9F3E45328647BD630C8E653B58D05CAC918BE0D31FB451DD7E9A320C71E |

Nach Rootfund bestätigt der Parent neben Name zusätzlich bekannte vollständige
CID-Abwesenheit mit eigener read-only Prüfung innerhalb derselben Deadline.
Kein Runtimefehler oder zusätzlicher Kandidat durch diese vorbereitende Korrektur.

### Geschlossener erster Kandidat und feste Clientkorrektur

Der erste tatsächlich zugelassene Lauf 448381C255F044D1 auf 17.0.5005.3
scheiterte beim Start von 30_CostBoundary. Native Windows-ODBC-sqlcmd
15.0.1300.359 verwirft die unquotiert als `-v` übergebenen absoluten Drivepfade
mit `Invalid argument`. Kein Kosten-SQL erreicht, keine Kostenframes und kein
erster Indexbau in diesem Lauf attestiert. Keine Umdeutung in SQL-Guardfehler.
Setup/Enable/Baseline und vollständige Storage-Baseline waren erfolgreich.
Tatsächliche Preview-/MAXDOP-Originalrestores 0/0, neue DB-Abwesenheit,
unabhängige Namens- und vollständige CID-Abwesenheit bestanden. Gesamter
Cleanup 13,2039358 s; Ledger closed=true/FAIL. Keine zweite Admission dieses
Kandidaten und keine unveränderte Clientprobe.

Der vorgesehene zweite Kandidat ändert ausschließlich die Include-Pfadübergabe:
feste geprüfte absolute Pfade als frische native Prozess-ENV statt `-v`.
Shell-Code, generierte SQL-Dateien oder CWD-Abhängigkeit werden nicht
eingeführt. SQL, Kostenhelper, Optionen, Ressourcen und Cleanupgrenzen bleiben
unverändert. Erste korrigierte öffentliche Controllergegenproben: 21 PASS einschließlich
geerbter ENV-Überschreibung und tatsächlichem Native-Executor-Aufrufvertrag;
unveränderte Kosten-/Selektortests lokal nicht erneut ausgeführt.

Neue ausführbare SHA256 vor Admission/erforderlicher enger Befundclosure:
vorbereiteter run_profile.py 4F4D32A6370563FFF6B0E4AB390E89578FD7A63CBC8365F43AE9B4221797982B;
Parent 9EB95FAA41269BC4A3CD239067D05183813269E40DA5CBFBDDD6129BA8AA291F.
Die erste Tabelle bindet den geschlossenen C1, nicht diese neuen Bytes.
Die zwei vorgesehenen Slots des C2 bleiben innerhalb des Gesamtbudgets vier; maximal
zwei positive Lifecycles, keine weitere Korrektur bei ungelöstem C2-Fehler.

Der enge Review des neuen ENV-Deltas fand vor C2-Admission einen P2:
Windows normalisiert os.environ-Schlüssel auf Großschreibung; eine einfache
dict-Kopie/update kann geerbte PHASEWORKFILE/COSTFRAMEFILE neben gemischten
eigenen Schreibweisen behalten. Der Controller entfernt deshalb sämtliche
casefold-gleichen Varianten der beiden reservierten Namen vor dem Update.
Die neue Fixture mit uppercase/mixed/lower Duplikaten prüft eindeutige eigene
Pfade, unveränderte Elternumgebung und erhaltene Secret-ENV. 22 aktualisierte
Controllergegenproben PASS; kein zusätzlicher Runtimeversuch für diese
vorbereitende Korrektur. Enge unabhängige P2-Closure ohne neue Befunde, keine
Runtimeattestation des Reviewers. Finaler öffentlicher Controller-SHA256:
4C138E920E97811185749E58D08F4559F9B05161D70ED01B0B21FD49805112A4;
Parent unverändert 9EB95FAA41269BC4A3CD239067D05183813269E40DA5CBFBDDD6129BA8AA291F.

### Zweiter Kandidat FAIL und regulärer Abbruch

Der zweite tatsächliche Lauf C7273FFC05C04F70 auf 17.0.5005.3 erreichte erneut
die Kosten-SQL nicht. Native sqlcmd meldet beim ersten `:r` wörtlich
`'$(CostFrameFile)': Invalid filename.` Die Variable steht damit im tatsächlich
erhaltenen Dateinamen unverarbeitet. Kein nachträglicher Kostenframe, kein
Indexbuild-/DML-/Rebuildclaim aus diesem Versuch. Ob dies eine allgemeine
Variablen-/ENV- oder spezifische Includegrenze ist, bleibt ohne getrennte
Clientdiagnose UNKNOWN; Dokumentation/Quellenreview ersetzen diese nicht.

Setup/Enable/Source-/vollständige Storagebaseline bestanden. Tatsächlicher
Restore und unabhängige Attestation bestätigen Preview/MAXDOP 0/0, der
markergebundene Drop wurde bestätigt und neuer Client meldet DB-Abwesenheit.
Eigener Parent bestätigt Name und vollständige bekannte CID abwesend;
gesamter Cleanup 13,5870011 s, Ledger closed=true/FAIL. Beide Kandidaten sind
geschlossen nach zusammen zwei eigenen Containern; die unbenutzten Slots
werden nicht nachträglich als Korrekturwelle verwendet. Kein weiterer Lauf.

Der öffentliche Controller sperrt `capture_costs=True` mit FAIL_CLIENT_INCLUDE
bereits vor jedem Client/Setup, auch bei ansonsten gültigen Storage-/Rebuild-
Optionen. Die neue Gegenprobe bestätigt keine Executoraufrufe; aktuell 23
Controllergegenproben PASS. Dieser sichere Checkpoint ändert keine SQL-Wirkung
und ist keine Kostenruntimeattestation. C2-Hash oben bindet die gescheiterten
Runtimebytes vor dieser Sperre. Andere bekannte Modi bleiben erhalten.

Wiederaufnahme benötigt getrennten endlichen Clientvertrag mit tatsächlich
geänderten Eingaben und eigener Quellenclosure nach vollständiger Integration
dieses Checkpoints. Keine unveränderte SQL-/Clientprobe, keine stille
Budgetrücksetzung, keine erneute allgemeine Freigabefrage innerhalb der bereits
autorisierten lokalen Welle. Unabhängige autorisierte Arbeit wird fortgesetzt.
Generation UNKNOWN, Freshness OBSERVED_AFTER_REBUILD_ONLY und vollständige
Runtimequalifikation NOT_ESTABLISHED bleiben erhalten. Writes-/TempDB-/Worker-
Abnahme offen; bisherige Storagewerte bleiben gültige eigene DB-Katalogpunkte.

## Prüfaufwand

Ein neuer reiner Kostentest im vorhandenen statischen KI-Job und sechs neue
Controllergegenproben einschließlich der geänderten Clientgrenze, zusätzlich
eine reine Sperrgegenprobe nach dem regulären FAIL-Checkpoint. Keine neue
Runtimejobdefinition. Konservative Auswahl
führt weiterhin acht freigegebene Offline-Demos auf drei Versionen je zweimal
am aktuellen Head und auf main aus; sie attestiert diesen Prototyp nicht.
Lokale Kostenruntime endet spätestens nach vier eigenen Admissionen.
Unveränderte DML-/Lifecycle-/Storagetests und frühere Reviews werden lokal
nicht ohne neuen Anlass wiederholt; keine vollständige Analyse-/Reviewkette.

## Primärquellen

Abruf 2026-10-11; keine tatsächliche Buildattestation durch Dokumentation:

- [sys.dm_exec_sessions](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-sessions-transact-sql?view=sql-server-ver17): Sessioncounter, Batchende und Bedeutung von writes.
- [sys.dm_db_session_space_usage](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-session-space-usage-transact-sql?view=sql-server-ver17): abgeschlossene Tasks, Seiten und IAM-Grenze.
- [sys.dm_io_virtual_file_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-io-virtual-file-stats-transact-sql?view=sql-server-ver17): kumulative Datei-Writes/-Bytes/-Stallzeit.
- [SQLCMD-Kommandos](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-commands?view=sql-server-ver17): Includes und GO.
- [SQLCMD-Scriptingvariablen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-use-scripting-variables?view=sql-server-ver17): Prozess-ENV, Präzedenz und Fehlverhalten bei fehlender Variable.
- [Python os.environ](https://docs.python.org/3/library/os.html#os.environ): case-insensitive Windows-Umgebung und Uppercase-Normalisierung.
- [SQLCMD-Utility](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#-w-screen_width): maximale Clientbreite 65535.
