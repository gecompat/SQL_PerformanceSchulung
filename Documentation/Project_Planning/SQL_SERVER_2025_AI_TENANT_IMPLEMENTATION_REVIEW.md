# CON-010: öffentliche Gegenprobenqualifikation

Die öffentliche Einbindung übernimmt unveränderte SQL-Quellen des privaten C5-
Kandidaten. Die neue lokale Consumerqualifikation schließt bisher offene Gates:
zweimal tatsächliches 2019-/2022-SKIP vor Setup, 192 Markerabweisungen über alle
acht Phasen, 16 tatsächlich erzeugte Result-/Rechtemanipulationen gegen Baseline
und Comparison, tatsächliche Setupidempotenz und unabhängiger eigener Cleanup.
Die alten drei vollständigen FAILs, C4-Kollations-FAIL und C5-Positivläufe bleiben
im historischen Ledger/Nachweis erhalten und werden nicht erneut ausgeführt.

Benutzerautorität: sechs kohärente Test-/Korrekturkandidaten je lokalem Schnitt;
maximal 30 zusätzliche serielle eigene Container für fünf feste Qualifikations-
slots. Keine Wiederholung eines fehlgeschlagenen unveränderten SQL-/Pythoninputs.
Keine Auffüllung ungenutzter grüner Kandidaten. Ein Kandidat bindet alle Quellen.
Feste vorhandene 2019-/2022-/2025-Images, vier CPUs/sechs GiB, ausschließlich
Loopback, Passwort nur ENV, kein Pull oder fremder Container-/Repoeffekt.
300 s einschließlich Readiness; gemeinsame tatsächliche 60 s Cleanupdeadline
beginnt vor finalem SQL-Cleanup und bleibt für neue DB-/CID-/Namensabwesenheit
sowie eigene Containerentfernung erhalten. SQL-Datei exklusiv/geschlossen vor
native -i; kein -v, -r oder SQLCMDINI. Unbestätigtes natives Clientende sperrt
weitere SQL-Aufrufe und Input-Unlink, tatsächlicher eigener CID bleibt gebunden.

Ein Implementierungsverantwortlicher; enger unabhängiger Review der neuen
Consumer-/Input-/Marker-/Orakel-/Cleanupgrenzen. Zwei P2 vor Admission geschlossen:
Interrupt zwischen Start/Collectoreintritt und lose numerische Fehlerprüfung.
Finalguard prüft tatsächlichen strikten int-Endstatus auch bei Interrupt, fehlender
Handle nach Startversuch konservativ UNKNOWN. Fehleroracle prüft genau einen
vollständigen nativen Header mit exakter Nummer und unmittelbar zugehöriger
Nachricht; falsche und zusätzliche Msg-Header abgewiesen. Kein Review des Reviews.
Parent SHA 062DEA7040A2B6CED5E80885A0DEA24B9A132EE20B97817DAAC696CB61E020FB,
Controls F3961EF7D330D62C4096D38895A5F0E8E8CC68A27C0D706F84BB9B66D37C4087,
Setup unverändert 0D942FB328CE5D011A8ADC87877CC6BDD5E0BA04452537CEF495464074134790.
Sechs private rein synthetische Endstatustests PASS, neun öffentliche Runner-
Methoden PASS einschließlich falscher/mixed/unzugehöriger nativer Fehler.
Reviewer ohne Runtime/Testausführung. Modell-/Tokenverbrauch unbekannt.

Aktuelle CI (Continuous Integration; automatisierte Integrationsprüfungen) prüft auf PR-HEAD und integriertem main je zweimal öffentliche
Lifecycles auf drei Versionen und die betroffenen vorhandenen acht Demos.
Neue Controlsabhängigkeit steht in beiden Workflowpathsets. Mutierende CI
cancel-in-progress bleibt false; kein Repeat aufgrund eines Timerereignisses.
32 Demos/372 Runs sind ausschließlich geplanter gesamter Providerkatalog,
keine Behauptung dieser ganzen Matrixausführung. Kein Vollsuite-Lokaldoppel.
Die öffentliche Promotion ist keine Runtime-/Release-/TSK-009-Gesamtabnahme;
Pooling, Serverlogins, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren), Seitenkanäle und Modellprovider bleiben offen.

C1 nativer Consumer-FAIL bleibt geschlossen im gemeinsamen Ledger: vier
Versions-SKIPs PASS und 192 tatsächliche Markerabweisungen PASS; bei der
15. Fixturegegenprobe erzeugte GRANT SELECT(Id) unter vorhandenem Tabellen-
SELECT keine zusätzliche Katalogpermission. Baseline akzeptierte die unveränderte
Fixture, Consumerwertung FAIL statt falscher Gegenprobenabnahme. FullCleanup
13,5734131 s; neue DB-/vollständige CID-/Namensabwesenheit PASS, Clientstatus
bekannt. C1Controlsbytes F396... archiviert in candidate1/frozen-controls.py.
C2 ändert ausschließlich die Spaltenprobe auf DENY SELECT(Id) und bindet vor
jeder Fixturemutation einen vollständigen Snapshot: ohne tatsächliche Änderung
stoppt der Consumer vor der Fehleroracleprüfung. SQL-/RLS-/Grantoracles bleiben
unverändert. Budget bleibt C1–C6/maximal 30 Container, C1 wird nicht zurückgesetzt.

C2-Delta unabhängig geschlossen: ausschließlich DENY SELECT(Id) und volle
Snapshotdifferenz vor jeder Manipulationsoracle, keine geänderten SQL-/RLS-/
Grantoracles. Controls 2EE181FE55DCF4C57B07485243B164A165499A74FFB20FBF06DF4543C5751165,
Parent unverändert062DEA..., C1Archiv F396...; Reviewer ohne Runtime/Tests.
Feste Versionsslots werden am stabilen C2-Quellenkandidaten erneut qualifiziert,
keine zusätzliche unveränderte Korrektur-/Vollanalyse oder grüne Alttests.


## Tatsächliche öffentliche Consumerqualifikation

| Fester Slot | Synthetischer Token | Tatsächlicher Build | Ergebnis | Gesamter eigener Cleanup | Neue DB/CID/Name abwesend |
|---|---|---|---|---|---|
| C1 / 2019-skip-1 | `39D0E1312858435A` | 15.0.4490.9 | SKIP_VERSION vor Setup | 11.2372871 s | PASS |
| C1 / 2019-skip-2 | `8D53E2F1512A432F` | 15.0.4490.9 | SKIP_VERSION vor Setup | 10.8404157 s | PASS |
| C1 / 2022-skip-1 | `459C457835C44C76` | 16.0.4295.3 | SKIP_VERSION vor Setup | 12.7381196 s | PASS |
| C1 / 2022-skip-2 | `6388BFBA21F1420C` | 16.0.4295.3 | SKIP_VERSION vor Setup | 12.1950135 s | PASS |
| C1 / 2025-controls | `23071DA0531444FC` | 17.0.5005.3 | FAIL: redundanter Spaltengrant erzeugte keine Änderung; 192 Marker-/28 Resultabweisungen bestanden | 13.5734131 s | PASS |
| C2 / 2019-skip-1 | `E824F2DCB90D4384` | 15.0.4490.9 | SKIP_VERSION vor Setup | 10.6781441 s | PASS |
| C2 / 2019-skip-2 | `9FDDA4B59D3741EF` | 15.0.4490.9 | SKIP_VERSION vor Setup | 10.7622471 s | PASS |
| C2 / 2022-skip-1 | `06CB4F6CB9434420` | 16.0.4295.3 | SKIP_VERSION vor Setup | 12.3446414 s | PASS |
| C2 / 2022-skip-2 | `4783A5AA1C22411F` | 16.0.4295.3 | SKIP_VERSION vor Setup | 12.1865993 s | PASS |
| C2 / 2025-controls | `93D84E55E209443B` | 17.0.5005.3 | 192 Markerabweisungen; 16 tatsächliche Manipulationen je zweimal abgewiesen; Setupidempotenz | 12.7900275 s | PASS |

Der erste neue Consumerkandidat blieb FAIL; C2 korrigierte ausschließlich die
wirkungslose Spaltengegenprobe und fügte tatsächliche Snapshot-Differenz vor
jeder Manipulationsoracleprüfung hinzu. Enger Deltaquellenreview geschlossen,
keine geänderten SQL-/RLS-/Grantoracles oder verlorene historische FAILs.

Die vier Markerfälle je vollständigem Eigenschaftsnamen waren fehlender Wert,
fremder Wert, angehängtes Blank und 256 angehängte Zeichen; zusätzlich wurden
kleingeschriebener und um ein Blank verlängerter Name geprüft. Jede der sechs
Varianten je vier Marker wurde gegen alle acht Phasen tatsächlich attestiert,
mit exakt 51004/FAIL_STATE abgewiesen und anschließend mit vollständigem Daten-/
Policy-/Funktions-/Rechte-/Rollen-/Konfigurationssnapshot auf unveränderte
Fixture geprüft. Reparatur war an die drei anderen Marker und den vollständig
tatsächlich manipulierten vierten Marker gebunden, anschließend alle vier
Eigenschaften erneut geprüft. Cleanup der manipulierten Fixture wurde abgewiesen.

Die 16 Source-/Tenant-/Vektor-/Policy-/Funktions-/CONNECT-/SELECT-/zusätzlichen
Grant-/Rollen-/Impersonationsmanipulationen wurden jeweils tatsächlich erzeugt;
Baseline und Comparison verweigerten jede mit exakt 51003/FAIL_RESULT_CONTRACT.
Vor jeder Mutation war Comparison positiv, anschließend eigener Setupreset.
Genau 224 native Fehlerbelege und 35 positive Phasensummaries im Rawnachweis,
keine Ablehnung aufgrund beliebiger Fehlertexte. Setup wurde zweimal ausgeführt;
der vollständige semantische Snapshot blieb gleich. Objekt-/Principal-IDs und
Erstellungszeiten durften nur bei ausdrücklich neu erzeugtem Setup wechseln;
die 192 Markergegenproben banden zusätzlich diese tatsächlichen Metadaten.

Die beiden stabilen privaten C5-Positivlifecycles bleiben im
[Wiederaufnahmenachweis](SQL_SERVER_2025_AI_TENANT_RESUME_REVIEW.md) erhalten.
Die öffentliche CI verlangt jetzt zwei aktuelle reguläre Lifecycles und denselben
Marker-/Resultconsumer auf jedem zulässigen PR-/Main-Head. Kein lokales Duplikat
der bereits grünen privaten C5-Kontrollen. Öffentlicher Ausführungspfad ist
[manifestbasiert](../../Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/README.md);
FWK-001–012, bestehende CON-010-Registryidentität und sechs Expectedassertions
bleiben gebunden. Die neun lokalen KI-Demos sind Teil eines 32-Demo-/372-Run-
Providerplans; dieser Plan wurde dadurch nicht vollständig ausgeführt.

Lokale Framework-, Guide-, Executionpaths-/Labkatalog- und Selektorgates bestanden;
sechs synthetische Endstatus- und neun öffentliche Runnerregressionen PASS.
Aktuelle PR-HEAD-/Main-Gates und vollständige Übernahme/Synchronisierung/eigener
Branchcleanup werden im PR nachgewiesen. Offene Integrationsgates dürfen bis dahin
nicht als erfüllt gelten. Pooling, authentifizierte Serverlogins, mehrere Sessions,
ANN-/Postfilter, Seitenkanäle, Modellprovider und TSK-009-Gesamtabnahme bleiben offen.
Keine Performance-/TP-PERF-Abnahme oder Privilegschutz vor dem Owner.
Rohdaten und vollständige Principal-/SID-Metadaten bleiben im ignorierten privaten
Runtimepfad. Öffentliche Tokens sind ausschließlich frische synthetische Kennungen;
kein Passwort, Hostendpoint, kompletter CID oder reale Benutzer-/Umgebungsdiagnose.


## C3: tatsächlicher öffentlicher Ausgabekanal

Die öffentliche CI auf PR-184-Head 4c28f5d2f0c10efd1cc1af80bc1ea4a35a677a7c
ist im SQL-AI-Run 38188982540 tatsächlich FAIL. Beide regulären CON-010-
Lifecycles bestanden; danach scheiterte die neue Consumer-Abwesenheitsprüfung
vor Setup. Die öffentliche sqlcmd-Option -r 1 routete PRINT nach stderr,
die API (Application Programming Interface; Programmierschnittstelle) lieferte ausschließlich stdout. Eigener CI-Container tatsächlich
bereinigt. Dieser Head wurde nicht gemergt; native C2-Positivbelege bleiben
unverändert und ersetzen keine fehlgeschlagene CI-Qualifikation.

C3 fügt der API ein optionales include_diagnostics hinzu. Nur tatsächliche
PRINT-Summaries und Abwesenheitsmeldungen nutzen stdout plus stderr; Default,
Snapshots, Fehlerstatus und SQL-/RLS-/Grantoracles bleiben unverändert.
ValueError im Consumer wird im Runner als FAIL_RESULT_CONTRACT abgeschlossen.
Der private C3-Parent verwendet jetzt exakt die öffentlichen Ausgabeoptionen
einschließlich -r 1; seine unabhängige Root-Abwesenheit liefert SELECT, die
Versions-SKIPs lesen ausdrücklich stderr. Enger unabhängiger Deltaquellenreview
vor Admission geschlossen, kein P1/P2; Reviewer ohne Runtime-/Testausführung.
Sieben synthetische Endstatus- und elf öffentliche Runnermethoden PASS.

| Fester Slot | Synthetischer Token | Tatsächlicher Build | Ergebnis | Gesamter eigener Cleanup | Neue DB/CID/Name abwesend |
|---|---|---|---|---|---|
| C3 / 2019-skip-1 | `4544348AF532489F` | 15.0.4490.9 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 11.0590221 s | PASS |
| C3 / 2019-skip-2 | `FA65A61D067F4741` | 15.0.4490.9 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 10.7648486 s | PASS |
| C3 / 2022-skip-1 | `7EBEB7A78B104FA0` | 16.0.4295.3 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 12.5672187 s | PASS |
| C3 / 2022-skip-2 | `986AA867F1414046` | 16.0.4295.3 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 12.5430919 s | PASS |
| C3 / 2025-controls | `86136B96B04F4E0F` | 17.0.5005.3 | 192 Marker-/32 Resultabweisungen; 16 sichtbare Mutationen; tatsächliches -r 1 | 13.0742035 s | PASS |

Alle fünf C3-Slots bestanden am selben gebundenen Quellenkandidaten. Insgesamt
15 eigene Qualifikationscontainer samt DB, vollständiger CID und Name abwesend;
Cleanup jeweils unter derselben 60-s-Deadline, kein UNKNOWN. Alle historischen
FAILs bleiben erhalten. Der dritte von maximal sechs Kandidaten/maximal 30
Containern schließt die lokale Ausgabekanalqualifikation; ungenutzte Kandidaten
werden nach PASS nicht als weitere identische Läufe verbraucht. C1/C2/C3-
Quellenbytes und Rawnachweise sind im ignorierten Runtimepfad archiviert.
Aktuelle korrigierte PR-Head-/Main-Gates und vollständige Integration bleiben
bis tatsächlichem Abschluss erforderlich. Keine Gesamtabnahme von TSK-009.


## C4: gemeinsame API-Baseline und begrenzte Summaryprojektion

C3-Nativqualifikation bleibt PASS. Die anschließende CI auf Head
c720508483b7e6ff1d20acb5eee03ad3f475a495 scheiterte im abgeschlossenen
Offline-Run 38190655438 mit PYTHON_PROFILE_CHANGED: die gemeinsame API besitzt
eine eingefrorene AST-Ausführungskante. Kein Merge oder Bypass; alle mutierenden
Runs bleiben bis zum eigenen Cleanup erhalten. Dieser CI-FAIL ist source- und
rawhashgebunden im selben Ledger; kein umdeklarierter nativer C3-FAIL.

C4 stellt execution_target.py exakt auf die gemeinsame Baseline zurück,
kein eingefrorenes Profil oder pausierter Workstream wird migriert. Ausschließlich
der CON-010-Consumer verlangt genau eine feste positive Phasensummary und ersetzt
deren PRINT durch SELECT vor dem tatsächlichen SQLlauf. Eigene Abwesenheit ist
ebenfalls SELECT. Nur diese Ausgaben gehen dadurch bei -r 1 nach stdout; alle
SQL-/RLS-/Grant-/Errororacles und die regulären Demo-SQLdateien bleiben bytegleich.
Der reguläre manifestbasierte Demorunner verwendet seinen bisherigen stderr-
Vertrag. Fehlende/doppelte positive Summary ist FAIL, keine erfundene Summary.
Strukturierter ValueError-FAIL bleibt im KI-Runner erhalten. Enger unabhängiger
C4-Quellenreview vor Admission geschlossen, kein P1/P2, keine Runtime des Reviewers.
Elf öffentliche Runnermethoden einschließlich tatsächlicher Ausgabetransformation
und Missing/Duplicate-Guards sowie sieben private Endstatustests PASS.

| Fester Slot | Synthetischer Token | Tatsächlicher Build | Ergebnis | Gesamter eigener Cleanup | Neue DB/CID/Name abwesend |
|---|---|---|---|---|---|
| C4 / 2019-skip-1 | `AE270E743BC64A1B` | 15.0.4490.9 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 11.4641215 s | PASS |
| C4 / 2019-skip-2 | `451B4DB817544F58` | 15.0.4490.9 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 11.1417999 s | PASS |
| C4 / 2022-skip-1 | `2D7DC9D4FD6B465E` | 16.0.4295.3 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 12.5165042 s | PASS |
| C4 / 2022-skip-2 | `F19A93F2C0FE44C8` | 16.0.4295.3 | SKIP_VERSION vor Setup, tatsächlicher stderr-Ausgabekanal | 12.5446963 s | PASS |
| C4 / 2025-controls | `54B4A45FBE8D4BC5` | 17.0.5005.3 | 192 Marker-/32 Resultabweisungen; 16 tatsächliche Mutationen; nur feste PASS-Summary SELECT | 13.3312633 s | PASS |

Alle fünf C4-Slots am selben gebundenen Quellenkandidaten bestanden, insgesamt
20 eigene Qualifikationscontainer samt DB/CID/Name neu abwesend, kein UNKNOWN,
gemeinsames Cleanup jeweils unter 60 s. Vier von sechs Kandidaten verbraucht,
keine zusätzlichen identischen grünen Kandidaten. Sämtliche C1–C4-Quellenbytes
und Rawbelege archiviert. Aktuelle C4-Head-/Main-Gates und vollständige Integration,
FF-Sync und eigener Branchcleanup bleiben bis tatsächlichem Abschluss erforderlich.
TSK-009-/Pooling-/Provider-/ANN-/Gesamtabnahme weiterhin offen.
