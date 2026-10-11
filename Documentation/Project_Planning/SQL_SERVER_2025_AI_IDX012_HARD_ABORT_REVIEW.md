# IDX-012: begrenzter eigener Containerabbruch nach fertigem Indexcheckpoint

Stand 2026-10-12. TSK-006/DEC-074, weitere lokale Wellenfreigabe einschließlich
sechs Korrekturkandidaten. Nur zwei identische stabile Lifecycles des festen
Falls IDLE_INDEX_SIGKILL; höchstens sechs Kandidaten/zwölf serielle neue eigene
Container im eigenen Ledger. Retry nach geschlossenem FAIL nur mit geänderter
SQL-/Python-Ausführungsquelle, alte Fehler zählen weiter. Kein automatischer
Reset oder Ausschöpfen verbleibender grüner Zyklen.

## Konkreter Abbruch und erwartete Evidenz

Öffentlicher IDX-012-Controller unverändert aus dem vollständig integrierten
Rollenstand; sa nur im neuen eigenen isolierten Developer-Testcontainer.
Nach erfolgreichem Indexbau, vier positiven DML-Kontrollen, vier tatsächlichen
Verweigerungen, allen 999 Vektortexten/Distanzkontrollen/Indexmetadaten und
anschließendem tatsächlichem Snapshot ist der native SQL-Client bestätigt
beendet. Der öffentliche Ablauf erreicht diesen Snapshot erst nach seinem
vollständigen unabhängigen Quellenabgleich. Vor dem Signal attestiert der
Parent nochmals genau den eigenen aktuellen Snapshot, vollständige Marker,
persistierte Preview-/MAXDOP-Originalbaseline 0/0 und erwartete aktuelle 1/1.
Keine aktive DDL, kein künstliches WAITFOR als angeblicher laufender Build.

Ausschließlich der vollständige eigene CID nach Name-/Ownerlabel-/Image-/
4CPU-/6GiB-Bindung erhält podman kill --signal KILL. Kein --all/--latest,
kein fremder Container/Host-/VM-Neustart oder Änderung anderer Repositories.
Danach erneut vollständige Eigentumsbindung und tatsächlicher stopped-State:
Running=false, OOMKilled=false, ExitCode=137, gleiches vorheriges StartedAt
und neues nichtleeres FinishedAt. Fehlende/falsche Werte stoppen vor Restart.
Genau derselbe vollständig gebundene CID wird einmal gestartet; neue tatsächliche
StartedAt-/Running-Bindung, unveränderte Loopback-Portbindung und neuer nativer
SQL-Readinessclient erforderlich. Inspect-Rohdaten mit Container-ENV werden
nicht persistiert; nur ausgewählte Statewerte, keine Secrets.

Neue read-only Clients aus unveränderten öffentlichen 21-/40-Quellen prüfen
danach vollständigen identischen Snapshot samt persistierter Baseline/Markern,
aktuellem 1/1, eigener DB-/Tabellen-/Indexidentität sowie alle 999 Vektortexte,
Distanzen und vollständigen Indexmetadaten gegen die tatsächlichen vorherigen
Records. Bestätigtes Clientende ist Voraussetzung weiterer SQL-Aufrufe.
Ungeklärtes Clientende löst den bestehenden ClientEndUnknown-Floor aus: kein
konkurrierender SQL-Recoveryclient, FAIL sichtbar, nur gebundener Containerabbau.

Erst nach dieser Folge liefert der öffentliche feste after_index_build-Fall
erwartetes FAIL_EXECUTION/AFTER_INDEX_BUILD_AND_SOURCE_CHECK. Native
Originalrestores 0/0, neuer Attestationsclient mit vollständigen Eigentumsmarkern
und DROP_CONFIRMED, neuer DB-Abwesenheitsclient sowie vollständige eigene CID-
und Namensabwesenheit bleiben erforderlich. Parent-PASS gilt ausschließlich
für tatsächlichen eigenen idle Container-SIGKILL samt Wiederanlauf und Recovery;
öffentliches FAIL und Generation UNKNOWN/runtime_qualification NOT_ESTABLISHED
werden erhalten. Fehlgeschlagener Restart, Marker-/Quellenabgleich oder SQL-
Restore bleibt FAIL, auch nach vollständig entferntem eigenen Container.

## Zeit, Daten und Sicherheitsgrenze

Eigener unveränderlicher vorhandener 17.0.5005.3-Container ohne Pull, 999–1000
synthetische VECTOR(3)-Rows, 4CPU/6GiB, eigene DB-Dateigrenzen unverändert.
Preview/MAXDOP ausschließlich eigene DB mit tatsächlicher persistierter
Baseline. Normal 300 s einschließlich ursprünglichem Startup. Die gesamte
Cleanupdeadline beginnt vor dem ersten SIGKILL/zugehörigem Inspect und bleibt
60 s über Kill, Restart, Readiness, beide neue read-only Prüfungen, SQL-
Recovery und CID-/Namenscleanup hinweg; kein Reset nach Wiederanlauf.
Restart/Readiness/Read-only-Folge teilt zusätzlich die tatsächlich verbliebene
normale Phasen-/300-s-Deadline und endet spätestens 36 s vor Cleanupende.
Öffentlicher 20-s-SQL-Recoveryvertrag mit 6/6/4-s-Phasencaps bleibt unverändert.
Ein Fehler vor Admission gibt keine zusätzliche Containeradmission; tatsächliche
FAILs bleiben im gleichen privaten Ledger. Kein Cloud-/ONNX-/roter Hosteffekt.

Dieser enge Fall belegt weder Abbruch während aktivem Index-DDL, laufender
Transaktion oder Rebuild noch vollständige Hard-Abort-/Minimalrollen-/Runtime-/
TP-PERF-/Demoabnahme. Diese Claims bleiben offen. Die beiden vorbereiteten
Quellen sind privat unter Runtime/IDX012_HARD_ABORT; kein neuer öffentlicher
Controllerparameter oder frei wählbarer Signal-/Source-/Zielpfad.

## Betroffene Prüfung und Integration

Root einziger Implementer. Fünf enge synthetische Restart-Gegenproben PASS:
feste tatsächliche Reihenfolge, fremde Eigentumsbindung ohne Signal, ungeklärtes/
boolesches Clientende ohne Inspect/Signal, OOM/falscher stopped-State ohne
Restart, geänderter Endpoint ohne SQL. Keine SQL-/Containeradmission dieser
Tests; keine Wiederholung unveränderter Controller-/DML-/Kosten-/Storagetests.
Enge unabhängige Quellenclosure für die neue Signal-/Restart-/Deadline-/
ClientEndUnknown-Grenze vor tatsächlicher Admission erforderlich. Keine
Reviewkette oder Runtime durch Reviewer. Modell-/Tokenverbrauch unbekannt.
Nach tatsächlich geschlossenen zwei Lifecycles oder begründetem FAILcheckpoint:
Privacy vor Commit, aktuelle Head-/Main-Gates, PR nach origin/main,
vollständiger Tree-/FF-Sync-Nachweis und eigener lokaler/Remote-Branchcleanup.

Primärquellen, Abruf 2026-10-12:
[podman kill](https://docs.podman.io/en/stable/markdown/podman-kill.1.html)
dokumentiert das Signal an den Hauptprozess des exakt angegebenen Containers;
[podman start](https://docs.podman.io/en/stable/markdown/podman-start.1.html)
startet den bezeichneten vorhandenen Container. Tatsächliche Zustandswerte,
SQL-Dauerhaftigkeit und Cleanup benötigen die separate empirische Attestation.

## Quellenbindung vor Admission

Parent SHA256 2A7DF31DB4C573248B3B51C5E5D56762FDD0A13E1CAB56F49D1C86BED4503454;
Restartquelle 27858DFD1D2050E3E4A1DD8E4D27765E29B9C84EE7DF7316E69734C144C52D9B.
Controller unverändert DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1.
Vor Admission ein Review-P2 korrigiert: tatsächliche Prozess-Endprüfung auch
bei Collector-Ausnahmen und Pollausnahmen; unbekanntes/nicht-integer Ende
verwendet immer ClientEndUnknown. Verbliebene Deadline wird vor jedem neuen
read-only Clientstart geprüft. Vier zusätzliche enge synthetische Gegenproben
PASS aus den tatsächlichen Parentfunktionen, einschließlich tatsächlich
unverändertem öffentlichen Recovery-finally: Unknown an 90-Restore oder
91-AttestDrop propagiert ohne späteren SQL-Start zum Parent; kein 92-Client.
Dieser Finally-Pfad fängt RuntimeError ausdrücklich nicht ab. Keine SQL-/
Containeradmission der Gegenproben; keine Wiederholung unveränderter Prüfungen.

Enge unabhängige Quellenclosure vor Admission erteilt, keine weiteren P1/P2:
ursprünglicher Collector-P2 geschlossen. Ein zunächst behaupteter zweiter
Recovery-Catch-Befund anhand der tatsächlich unveränderten Quelle und der
neuen Gegenprobe zurückgezogen; kein RuntimeError-Catch, kein Sticky-Latch
erforderlich. Alle drei aktuellen Hashes bestätigt. Keine SQL-/Container-/
Testausführung durch den Reviewer, kein allgemeiner Hard-Abortclaim.


## Tatsächliche zwei stabile Containerabbruch-Lifecycles

| Slot | synthetischer Token | vorheriger Indexbau µs | gesamtes Cleanup einschließlich Kill/Restart s |
|---|---|---:|---:|
| 2025-idle-index-kill-1 | F92CEAC8A7614EAB | 776456 | 19.4342235 |
| 2025-idle-index-kill-2 | 3EF8E51FAD3B4BE8 | 796142 | 19.3921410 |

Beide eigenen seriellen Fälle desselben C1 geschlossen ohne failure, alle
Ausführungsquellen und Parent/Restarthelper bytegleich. Tatsächliches
17.0.5005.3; je vier positive Kontrollen ohne Index, vier tatsächliche
42231/State-1-Verweigerungen mit Index und vollständiger unabhängiger
999-Row-Quellen-/Distanz-/Indexmetadatenabgleich vor dem Signal bestanden.
Eigener aktueller vollständiger Snapshot/Marker/Baseline 0/0 und laufende
eigene DB-Optionen 1/1 attestiert; Arbeitsclient vor Kill bestätigt beendet.

Tatsächlicher SIGKILL am vollständig gebundenen eigenen CID: stopped mit
ExitCode 137/OOMKilled false, anschließender Start desselben CID mit anderem
StartedAt, gleicher Image-/Ressourcen-/Loopbackbindung und neuer nativer
Readiness. Beide neuen read-only Clients bestätigten identischen vollständigen
Snapshot einschließlich persistierter Originalbaseline und sämtliche
999 Vektortexte/Distanzen/Indexmetadaten gegenüber der Aufnahme vor Kill.
Keine aktive DDL oder unterbrochene native SQL-Phase behauptet.

Öffentliche Resultate bleiben erwartetes FAIL_EXECUTION mit dem festen
AFTER_INDEX_BUILD_AND_SOURCE_CHECK-Tag. RESTORE/ATTEST_DROP/ABSENCE tatsächlich
PASS, Originalwerte 0/0, neuer markergebundener Drop und DB-Abwesenheit,
vollständige eigene CID-/Namensabwesenheit bestanden. Ganze 60-s-Deadline
beginnt bereits vor Kill und umfasst Wiederanlauf/read-only Prüfungen/SQL-
Restore/Containercleanup; kein nachträglicher Reset. Parent-PASS gilt nur für
diesen begrenzten tatsächlichen idle Container-SIGKILL samt Recovery.

Zwei eigene Container verbraucht und vollständig entfernt. Rohrecords,
Zustandstimestamps und gemeinsamer Ledger privat unter Runtime/IDX012_HARD_ABORT,
keine Secrets oder Hostdaten veröffentlicht. Neun betroffene synthetische
Gegenproben und enge unabhängige Quellenclosure vor Admission bestanden.
Kein zusätzlicher unveränderter grüner Lauf. Aktive Build-/DML-/Rebuild-
Unterbrechung, vollständige Hard-Abort-/Minimalrollen-/Runtime-/TP-PERF-Abnahme
bleiben offen; Generation UNKNOWN und runtime_qualification NOT_ESTABLISHED.
