# IDX-012: kontrollierte Fehler und tatsächliche Recovery

Stand: 2026-10-12. TSK-006/DEC-074; begrenzter Teilnachweis, kein Manifest,
kein Demo-Release und keine vollständige Runtime-/TP-PERF-Abnahme.
Die ausdrücklich autorisierte lokale Entwicklungswelle und die erweiterte
Grenze von sechs Kandidaten bleiben im [Ausführungsstand](CURRENT_EXECUTION_STATUS.md)
maßgeblich. Die vollständig abgeschlossene [Versionsfolge](SQL_SERVER_2025_AI_IDX012_VERSION_REVIEW.md)
attestiert diese Fehlerfälle nicht.

## Methode und Effektgrenze

Der öffentliche Default bleibt unverändert. Nur die feste Python-API-Option
fault='after_setup' oder fault='after_index_build' aktiviert einen
kontrollierten PhaseStop/FAIL_EXECUTION; keine freie Callback- oder SQL-Eingabe.
Nach Setup ist die eigene DB-ID, persistierte Originalbaseline und vollständige
Snapshotbindung geprüft; Preview/MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) wurden noch nicht aktiviert.
Nach Indexbau steht der Fehlerpunkt erst nach vier positiven DML-Kontrollen,
vier tatsächlichen 42231-Verweigerungen, vollständigen eigenen Indexmetadaten,
aktuellem Snapshot und unabhängiger 999-Row-Quellen-/Distanzprüfung.
Der neue Tag lautet AFTER_INDEX_BUILD_AND_SOURCE_CHECK. Es wird kein Rebuild
gestartet. Dies ist eine kontrollierte weiche Unterbrechung, kein Hard-Abort.

Der Parent verlangt erwartetes FAIL_EXECUTION mit genau einem passenden
kontrollierten Fehlercheckpoint, tatsächlich drei erfolgreichen Recovery-
Phasen und cleanup_ok=true. Ein früherer SQL-/Quellen-/Vertragsfehler,
fehlende Metadaten oder fehlende Quellenkontrolle erfüllen den Fehlerfall
nicht. FAIL_CLEANUP, Timeout oder ein unbekanntes Clientende bleiben FAIL.
Tatsächliche Markergebundene Restores von Preview/MAXDOP auf 0/0, neue
Attestation vor Drop und ein neuer DB-Abwesenheitsclient sind erforderlich.
Danach eigene vollständige CID-/Namensabwesenheit nach Eigentumsprüfung.

Ausschließlich neue eigene lokale unveränderliche 17.0.5005.3-Container,
vier CPUs/sechs GiB, eigene markierte DB, VECTOR(3), 999 Rows und höchstens
1000 innerhalb zurückgerollter Kontrollen. 300 s einschließlich Startup,
20 s gesamte SQL-Recovery innerhalb 60 s gesamtem Cleanup ab erstem Restore.
Secret ausschließlich ENV, geerbtes SQLCMDINI entfernt; keine Pulls,
Host-/Cloud-/ONNX-/Fremdrepositoryänderung. Minimalrollen und Hard-Abort
sind weitere Aufgaben, keine impliziten Claims dieses Schnitts.

## Gemeinsames Budget und Prüfaufwand

Root einziger Implementer; ein enger unabhängiger Delta-Review für neuen
Fehlerpunkt, Fehlerklassifikation, tatsächliche Recovery-/Eigentums-/Budget-
Bindung. Frühere abgeschlossene Default-/Counter-/Quellenreviews werden
nicht vollständig wiederholt. Eigener ignorierter Parent/Ledger unter
Runtime/IDX012_RECOVERY: maximal sechs stabile Kandidaten/24 serielle eigene
Container, je Kandidat zwei Setup- und zwei Buildfehler in fester Reihenfolge.
Ein nicht erfüllter Fehlerfall hält den Kandidaten an; nächster Kandidat nur
nach geschlossenem tatsächlichem FAIL und geändertem Ausführungsinput.
Vorherige Kosten-/Versionsledger bleiben abgeschlossen. Nach einem stabilen
vollständigen Vier-Slot-Nachweis kein unnötiger Verbrauch freier Kandidaten.

30 betroffene Controllergegenproben bestanden. Die neuen Gegenproben lehnen
freie Fehleroptionen vor SQL ab und verhindern einen Buildfehlertag vor
qualifiziertem Index-/Quellencheckpoint. Tatsächliche positive Fehlerpunkte
werden durch die vier Runtimefälle belegt. Unveränderte Kosten-/DML-/Storage-
und Selektortests lokal nicht nochmals ausgeführt. Bestehende Head-/Main-
Gates bleiben unverändert; keine neue Workflowdefinition oder Reviewkette.
Modell-/Tokenverbrauch unbekannt.

## Quellenbindung und aktueller Stand

Basis 99b8df923f144f6e915ff3718addf24582de7224, Branch
codex/sql2025-ai-idx012-recovery. Aktuelle SHA256:

| Quelle | SHA256 |
|---|---|
| öffentlicher run_profile.py | DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1 |
| eigener ignorierter qualify_recovery.py | F9EB8B93AC5AB947EF2F7B09D3F21E916A5A2A3623B56129735748333C1B2A8D |

Enge unabhängige Quellenclosure ohne neue P1/P2 erteilt; beide Hashes und
Fehler-/Recovery-/Budgetbindungen bestätigt. Keine Runtime oder Tests durch
den Reviewer. Alle vier Admissionen erfolgten nach dieser Closure. Vollständige
PR-/Head-/Main-/Tree-/Sync-/eigene Branchbereinigung bleiben Abschlussgates.


## Tatsächliche vier Fehler- und Recoverylifecycles

| Slot | synthetischer Token | Indexbau µs | gesamtes Cleanup s |
|---|---|---:|---:|
| 2025-fault-setup-1 | 0D5DA53FBF6B43CE | nicht begonnen | 12.6183559 |
| 2025-fault-setup-2 | D86B5FF43CC246A5 | nicht begonnen | 13.0445620 |
| 2025-fault-build-1 | 3C04F622FC6D4E14 | 780302 | 12.7929698 |
| 2025-fault-build-2 | 47C9D7AA36DF4A74 | 868304 | 12.8262864 |

Ein stabiler C1, alle vier eigenen seriellen Admissionen closed=true ohne
failure; tatsächliches 17.0.5005.3, sämtliche Demoquellen und Parent innerhalb
dieser vier Läufe bytegleich. Nach Setup kein Preview-/MAXDOP-Enable und
kein Indexbau; nach Indexbau jeweils vier positive DML-Kontrollen und vier
tatsächliche Verweigerungen 42231/State 1, vollständige eigene Indexmetadaten,
neuer Snapshot und unabhängiger Abgleich aller 999 Vektortexte/Cosinedistanzen.
Kein Drop-/Commit-/Rebuildschritt begonnen.

Alle vier öffentlichen Ergebnisse bleiben erwartetes FAIL/FAIL_EXECUTION
mit exakt passendem kontrolliertem Fehlercheckpoint. Der Parent-PASS
attestiert ausschließlich den nachgewiesenen Fehlerfall samt Recovery.
RESTORE, ATTEST_DROP und ABSENCE jeweils tatsächlich PASS: native
ANN_RESTORE/ANN_ATTEST mit tokengebundenen Originalwerten 0/0,
DROP_CONFIRMED und ANN_DB|ABSENT aus neuem Client. cleanup_ok=true;
vollständige eigene CID und Name unabhängig abwesend. Rohdaten und Ledger
bleiben privat unter Runtime/IDX012_RECOVERY; keine Secrets oder Hostdaten
werden veröffentlicht. Der fremde vorhandene Container wurde nicht geändert.

Damit ist der begrenzte kontrollierte Recoveryteil belegt. Kein Hard-Abort,
kein Minimalrollen-, Kosten- oder vollständiger Runtime-/TP-PERF-Claim;
Generation UNKNOWN/WARN und runtime_qualification=NOT_ESTABLISHED bleiben.
Vier Slots sind vollständig geschlossen; keine zusätzlichen identischen
grünen Läufe zum Ausschöpfen des Sechskandidatenbudgets.
