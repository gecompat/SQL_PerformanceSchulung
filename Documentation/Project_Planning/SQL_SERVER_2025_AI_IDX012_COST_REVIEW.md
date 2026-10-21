# IDX-012: begrenzte tatsächliche Phasenkosten

Stand: 2026-10-11. TSK-006/DEC-074; öffentliche Implementierungsvorstufe,
kein Manifest, keine freigegebene Demo und keine vollständige TP-PERF-Abnahme.
Der [kanonische Ausführungsstand](CURRENT_EXECUTION_STATUS.md) autorisiert die
weitere lokale ANN-Welle. Abgeschlossene DML-/Rebuild-/Speicherbudgets bleiben
geschlossen; ihre Resultate attestieren diese neue Aufnahme nicht.

## Methode und Aussagegrenze

Der Default bleibt unverändert. Ausschließlich `--mode drop-rebuild
--capture-storage --capture-costs` verwendet die beiden Kostenphasen. Nach
den historischen Client-FAILs und der vollständig integrierten Sperre in
PR 177 bestand der dritte Kandidat mit geänderter Clientübergabe beide Lifecycles.
Er assembliert ausschließlich den festen Wrapper, 23_CostFrame und die
ursprüngliche öffentliche 30_DmlBoundary/50_DropRebuild als literalen
SQL-Text. Zeilenenden werden normalisiert; eine byteidentische Übernahme der
ursprünglichen Dateien wird dadurch nicht behauptet. Vier feste GO-Grenzen
trennen Kontext, ersten Kostenpunkt, vollständige Arbeitsphase und zweiten
Kostenpunkt. Beide Punkte stammen aus derselben tatsächlichen Verbindung;
eigener temporärer SQL-Kontext bindet Session/DB/Token/Stage und endet mit
der Verbindung, ohne neues dauerhaftes Objekt.

Die native Eingabe ist eine einzelne eigene temporäre Datei unter Runtime,
höchstens 160000 UTF-8-Bytes. Eingelesene Quellen dürfen keine SQLCMD-
Kommandos, freien GO-Grenzen oder Shellaufrufe enthalten. Der Controller
schließt die Datei vor Clientstart und entfernt ausschließlich diese Datei
im finally-Pfad nach bestätigtem Ende des gebundenen Clientprozesses, auch bei
Timeout oder Fehler. Ist das Prozessende ungeklärt, bleibt die eigene Datei
erhalten und der Cleanup meldet FAIL_CLEANUP. Weitere SQL-Recoveryclients
starten dann nicht gegen den ungeklärt lebenden Client. Der eigene Parent
behält seine begrenzte Containerrecovery; diese belegt keinen SQL-Restore.
Native `:r`-Dateinamenauflösung wird nicht verwendet. Geerbtes
SQLCMDINI wird in allen Phasen entfernt; keine ungebundene Startupquelle.
CostStage bleibt feste CLI-Variable. Eigene Executoradapter verwenden
`execution_input(command)` zusammen mit `client_environment(command,
environment)`; der Qualifikationsparent sichert die tatsächlich übergebene
Quelldatei und deren SHA256 ausschließlich im ignorierten Nachweisordner.
Das ist Quellenprovenienz, noch keine Runtimeattestation.

23_CostFrame prüft vollständige FWK-002-Marker, persistierte Originalbaselines,
tatsächlich Preview/MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) 1/1, 999 Quellenrows, Indexzahl und separat vor
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

## Ursprüngliches Zweikandidatenbudget und Checkpoints

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
Das ursprüngliche Budget endete nach höchstens vier eigenen Admissionen;
die spätere ausdrückliche Benutzererweiterung steht im folgenden Abschnitt.
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

## Benutzererweiterung und dritter Kandidat

Der Benutzer hat am 2026-10-11 ausdrücklich mehr als zwei Testzyklen für
diese lokale Entwicklungswelle verlangt. Die neue endliche Grenze beträgt
sechs kohärente Test-/Korrekturkandidaten je Schnitt. Im selben Kostenledger
zählen C1 und C2 weiterhin mit; die Grenze ist jetzt sechs Kandidaten und
höchstens zwölf serielle eigene Container. Ein FAIL hält den betroffenen
Kandidaten an; ein weiterer Kandidat benötigt geänderte Ausführungsquellen
und die gezielte Closure eines tatsächlich offenen Risikos. Zwei positive
Lifecycles müssen weiterhin vom selben stabilen Kandidaten stammen. Ein
unveränderter Fehlversuch wird nicht wiederholt. Alte FAILs, Cleanupwerte
und verbrauchte Admissionen bleiben erhalten. Provider-, Cloud-, ONNX- und
rote Hostgrenzen werden dadurch nicht erweitert.

C3 auf codex/sql2025-ai-idx012-cost-bundle, Basis
4dc956df3f66c21c672e9add30405853bc1e4ca8, ersetzt die gescheiterte native
Includeübergabe durch die oben begrenzte literale Eingabe. Countersemantik,
SQL-Effektgrenzen, Originalrestores, 300 s einschließlich Startup und 20 s
SQL-Recovery innerhalb 60 s gesamtem Cleanup bleiben unverändert.
28 geänderte Controllergegenproben bestanden vor Admission; unveränderte
Kosten-, Storage-, DML-, Lifecycle- und Selektortests werden ohne neuen
Anlass nicht nochmals lokal ausgeführt. Ein enger unabhängiger Quellenreview
prüft Clientinput, Batchbindung, eigenen Dateicleanup, Quellenprovenienz und
das erweiterte gemeinsame Ledger. Keine neue administrative Reviewkette
oder Runtimejobdefinition. Die bestehenden Head-/Integrationsgates bleiben
verpflichtend; Modell-/Tokenverbrauch ist unbekannt.

Der enge Review fand einen P2: Der alte Collector garantiert bei erfolgloser
Prozessbeendigung auf dem Ausnahmeweg kein bestätigtes Clientende. Die neue
ExecutionInput-Lease bindet deshalb den tatsächlichen gestarteten Prozess
an den Dateicleanup. Nur ein Integer-Endstatus erlaubt die Entfernung;
fehlender oder nicht prüfbarer Endstatus erhält die Quelle und meldet
ClientEndUnknown/FAIL_CLEANUP. Der Controller unterbindet dann konkurrierende
SQL-Recovery, cleanup_ok bleibt false. Beide Executorpfade verwenden dieselbe
Lease. Gegenproben decken lebenden und beendeten Client sowie fehlende
SQL-Recovery im Unbekanntfall ab. Die enge unabhängige P2-Closure ist vor
Admission erforderlich und jetzt ohne weitere Befunde erteilt; kein
Runtimeversuch durch den Reviewer. Aktuelle geprüfte SHA256-Bindungen:
Controller 5D7964A85FE8041726901A66BA4629633119BDB97491972E25F82F41CF685705,
Parent EBF13336594B74558567F331E5A7A7BD87C128D47B6388946461067B5E47BB36,
beide Wrapper 6937A20A397C9AA159EDC3F21E5F3F0913A89F7830E867B195DB144E29527BC8.

Status: C3 mit zwei vollständigen positiven Lifecycles qualifiziert für die
begrenzten Phasenkosten; konsistenter PR-/Integrationsabschluss folgt.
C1/C2 besitzen weiterhin keine Kostenframes. Isolierte Index-/vollständige
Workerkosten sowie vollständige TP-PERF- oder Demoabnahme bleiben offen.

## C3: zwei vollständige tatsächliche Kostenlifecycles

Tokens 3E2901DC14FA4A4E und 064EB3DBC5FC4B54, tatsächlicher SQL-Build
17.0.5005.3, beide WARN_OPTIONAL_EVIDENCE_SKIPPED. Alle bisherigen Kontrollen
bestanden: vier positive zurückgerollte DML-Kontrollen ohne Index und vier
tatsächliche 42231/State1-Verweigerungen mit Index; vollständige 999-Row-
Quelle und unabhängige Distanzen; eigener Drop mit Indexbestand null vor
Commit Id999; übrige 998 Vektortexte unverändert; vollständige neue Metadaten,
fünf tatsächliche Suchkontrollen mit ANN-Recall@5 1 und geändertem Id999 auf
Rang1/Distanz0 nach Rebuild. Generation UNKNOWN und Freshness ausschließlich
OBSERVED_AFTER_REBUILD_ONLY. Drei vollständige Storagepunkte pro Lauf.

Vier tatsächliche PHASE_COST-Frames pro Lauf, jeweils BEFORE/AFTER in der
gleichen tatsächlichen Session pro Phase. Guards bestätigen eigene DB/Token,
999 Rows, Transaktion 0/0, eine Session-/TempDB-Row und beide eigenen Dateien.
Es werden Counterdifferenzen ganzer Phasen einschließlich Kontrollen,
Beobachtung und Instrumentierung berichtet; keine reinen Indexbaukosten.

| Lauf / Phase | Session CPU (Central Processing Unit; Prozessor) ms | Session Reads | Dirty-Page-Markierungen | Session Logical Reads | TempDB User Alloc/Dealloc Seiten | TempDB Internal Alloc/Dealloc Seiten |
|---|---:|---:|---:|---:|---:|---:|
| 1 / DML_BOUNDARY | 1676 | 40 | 234 | 1111374 | 0/0 | 80/64 |
| 1 / REBUILD | 1142 | 8 | 87 | 1062750 | 8/0 | 0/0 |
| 2 / DML_BOUNDARY | 1650 | 40 | 234 | 1111368 | 0/0 | 80/64 |
| 2 / REBUILD | 1083 | 8 | 87 | 1062754 | 8/0 | 0/0 |

| Lauf / Phase | Datei-ID | Sampledelta ms | Writes | Geschriebene Bytes | Write-Stall ms |
|---|---:|---:|---:|---:|---:|
| 1 / DML_BOUNDARY | 1 | 1833 | 2 | 663552 | 1 |
| 1 / DML_BOUNDARY | 2 | 1833 | 34 | 692224 | 15 |
| 1 / REBUILD | 1 | 1271 | 2 | 655360 | 1 |
| 1 / REBUILD | 2 | 1271 | 23 | 610304 | 10 |
| 2 / DML_BOUNDARY | 1 | 1788 | 2 | 663552 | 1 |
| 2 / DML_BOUNDARY | 2 | 1788 | 34 | 692224 | 19 |
| 2 / REBUILD | 1 | 1213 | 2 | 655360 | 1 |
| 2 / REBUILD | 2 | 1213 | 23 | 610304 | 11 |

Dateipunkte umfassen alle Writer der eigenen DB einschließlich Hintergrundarbeit.
TempDB-Seiten umfassen ausschließlich abgeschlossene Tasks; null ist ein
tatsächlich gemessener Delta und beweist weder vollständige Worker- noch
TempDB-Kostenfreiheit. Session Reads null beziehungsweise die hier erfassten
Reads sind keine vollständigen Worker-Reads. Buildzeiten 1109590/973468 µs,
Rebuildzeiten 1054882/962357 µs; diese getrennten Walltimepunkte besitzen keine
exklusive Zuordnung zu den oben ausgewiesenen Counterdifferenzen.

Die tatsächlich an den NativeClient übergebenen Quellen sind in beiden
Läufen identisch: DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) 25325 UTF-8-Bytes/SHA256
1917145B7762B977CC3D568BF0F26A987B5EF231DC4D9EA6F1675FA2A1F65DE5,
Rebuild 24535 Bytes/SHA256
962DB15772A1060C066090581C96DD668B89AAA35B8762208C734C77872AA7C7.
Beide Quelldateien wurden vor Clientstart lokal gesichert und pro Admission
gehasht; keine zusätzliche Diagnoseprobe. Quellen und rohe Resultate bleiben
im ignorierten Nachweisordner. Öffentliche SQL-/Controller-/Parentquellen
sind innerhalb C3 bytegleich; spätere README-Ergebnisnachträge ändern keine
ausgeführten Quellen.

Tatsächlicher Restore und neue unabhängige Attestation bestätigen jeweils
die Originalwerte Preview/MAXDOP 0/0. Markergebundener Drop und neuer
DB-Abwesenheitsclient bestanden. Eigene vollständige CID und eigener Name
sind unabhängig abwesend; gesamter Cleanup 13,7552919/13,3577670 s.
Beide Admissionen closed=true ohne failure. Kein temporärer eigener
idx012-cost-Input verblieben. C1/C2 bleiben unverändert geschlossene FAILs.
Die Folge schließt nach drei Kandidaten/vier tatsächlichen Admissionen mit
zwei stabilen positiven C3-Lifecycles; weitere Zyklen werden nicht allein
wegen des noch freien Budgets ausgelöst. Versions-SKIPs, Minimalrollen,
Hard-Abort und vollständige Runtime-/TP-PERF-Abnahme bleiben Folgearbeit.
