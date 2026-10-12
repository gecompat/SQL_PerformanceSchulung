# DGN-010 – öffentlicher begrenzter Kostencontroller

Stand: 2026-10-12. TSK-011/CUR-021; DGN-010 PROPOSED/Producer WARN.
Quellen-/Controller-Vorbereitung. Noch keine Nativequalifikation dieses Controllers.

## Abgeschlossener Ausgangsstand

[PR208](https://github.com/gecompat/SQL_PerformanceSchulung/pull/208) vollständig
abgeschlossen: Head e86b78e75c996b96a1d70a7e287f5f6ae5c178fe,
main 40d56069f28e4add5e2380fd2c3cd2ec93853afe, acht Head-/sechs Main-Workflows
PASS, Tree 533e209505d0544f9bc180aec2db46a0bf843d8a gleich, FF-main sauber,
eigener lokaler/Remote-Branch entfernt. Tatsächlicher Runtimejob aufgrund
Auswahl False SKIPPED, kein Runtime-PASS.

Der [feste Eingabevertrag](SQL_SERVER_2025_AI_DGN010_COST_INPUT_REVIEW.md) und
[numerische Kostenrecordvertrag](SQL_SERVER_2025_AI_DGN010_COST_CONTRACT.md)
werden hier erstmals durch einen öffentlichen begrenzten Controller verbunden.
Ein Implementierungsverantwortlicher, enger unabhängiger Review der neuen Ablauf-/
Negativ-/KnownEnd-/Input-/Deadline-/Cleanupgrenzen; keine offenen P1/P2.
Sechs kohärente Quellenkandidaten, Checkpoint3/hard6; dieser Vorbereitungsschnitt
führt den neuen Controller ausschließlich mit synthetischen Clients aus.
Modell-/Tokenverbrauch bleibt unbekannt. Gewöhnliche Folgeschritte sind freigegeben.

## Fester Ablauf und echte Resultkontrollen

[run_cost_profile.py](../../Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/run_cost_profile.py)
provisioniert nichts. Zwei YELLOW-Bestätigungen und bestehender read-only Preflight
gelten vor Setup. Nur eigene neue SQL17.0.5005.3/Developer/CL170-Instanz, vier CPU/
sechs GiB, 1000 synthetische Rows und unveränderte bestehende Konfigurationsgrenzen.
Keine neuen Provider-/Cloud-/ONNX-/Hosteffekte.

Initiale Abwesenheit, Preflight, Setup, vollständige Sourceaufnahme, idempotentes
Setup und erneute Sourceaufnahme. Tatsächliche Löschung von Row1000 muss die echte
20_Probe-51003-Abweisung auslösen; Setup stellt die Source wieder her. Native DB-ID
wird separat gelesen. Erster markergebundener Vollstate liefert die tatsächliche
Source-OID; alle folgenden Vollstates/DDL-Eingaben sind an beide IDs gebunden.

Eine separate feste DROP-Abwesenheitsprobe verlangt tatsächliches 51003 vor DDL.
Die neue `drop_absent_sql` akzeptiert ausschließlich DB-/Source-ID und erzeugt
fest DROP/Cycle1/EMPTY. Kein frei schaltbarer Negativeparameter oder Fremdtext.
Before-/After-Vollstate dieser Probe muss identisch bleiben. Erst nach tatsächlichen
Abweisungen werden die beiden Controllerflags gesetzt.

Zwei eigene CREATE-/DROP-Zyklen, je getrennt: Before-Vollstate, festes marker-/
Source-/gehaltene-Lease-gebundenes DDL-Fenster, vollständiger Recordvalidator,
After-Vollstate und Source-/Indexaufnahme. Der gesamte Record prüft danach alle
vier Fenster, acht Sourceaufnahmen, zehn Vollstates, echte Request-/Counter-/UTC-
Ordnung und vollständige Zwischenfensterkontinuität. Kein bloßer Controllerflag
ersetzt Nativeabweisung oder tatsächlichen State. Gesamtergebnis bleibt WARN,
Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED.

## Clients, Zeitbudgets, Inputs und Cleanup

Der bestehende tatsächliche sqlcmd-/Remote-Endvertrag bleibt unverändert. UNKNOWN
ist sticky: kein weiterer SQLclient, kein SQLcleanup und Erhalt des eigenen
SQLinputs. Ein lokaler Transportendstatus ersetzt keinen nativen Remote-Endframe.
Eigenes Instanzcleanup bleibt Aufgabe des separat gebundenen Qualifikationsharness.

Alle normalen Requests teilen höchstens 300 Sekunden, Parentdeadline kann nur
verkürzen. Cleanup hat einmal insgesamt höchstens 60 Sekunden; Parentcleanup-
Deadline verkürzt dasselbe Budget. Fehlende/ungültige Parentbindung ist kein Reset.
Nach gestarteter Setup-Phase eigener markergebundener SQLcleanup und neue read-only
DB-Abwesenheit. Kontrollierter Fault nach PASS-Setup muss FAIL_EXECUTION mit
tatsächlichem Cleanup ergeben. Fehlgeschlagener Cleanup bleibt FAIL_CLEANUP.

Feste rohe SQLinputs werden exklusiv unter privatem Runtime erstellt, auf 160000
UTF-8-Bytes begrenzt und nur nach bekanntem Clientende entfernt. Vollständige skalare
Transportoption `-y 0` erhält die bis zu 800 HEXzeichen langen Statechunks; incompatible
Header-/Whitespaceoptionen werden vorher entfernt. Unlinkfehler oder verbleibende
eigene Inputs bleiben FAIL_CLEANUP, auch wenn die DB bereits abwesend ist.
Bei UNKNOWN keine automatische Inputentfernung oder neue SQL-Recovery.

Der Runner persistiert keine Rohrecords. API-Evidenz enthält synthetische vollständige
Nativepayloads und gehört ausschließlich in privaten Runtime-Nachweis. CLI `--summary`
exportiert nur geprüfte Aggregate bei WARN und bestätigtem vollständigem Cleanup;
bei FAIL/SKIP kein Aggregatexport, keine Rohidentitäten, UTCs, Markerbytes oder Payloads.

## Tatsächlich geprüfte Vorbereitung und Aufwand

[Elf reine Controllermethoden](../../Tests/Static/test_dgn010_cost_profile.py) PASS:
vollständiger WARN-Ablauf, echte erwartete synthetische Nativeframes, falsche DDL-/
State-/Allokationsrecords, UNKNOWN bei Raw-/Setupclient, alle drei Preflight-SKIPs
vor Setup, tatsächlicher kontrollierter Setupfault, Cleanup-/Unlinkfehler,
Parentdeadline, Bestätigungsgrenzen und CLI-Exportgrenze. Sieben aktuelle
[Eingabemethoden](../../Tests/Static/test_dgn010_cost_inputs.py) PASS, einschließlich
fester DROP-Abwesenheitsprobe. CLI-help startet keine Clients. Kein Native-PASS
aus diesen synthetischen Methoden oder aus dem Quellenreview.

Enger unabhängiger Quellenabschluss ohne offene P1/P2; SHA256:

- Controller BFFFF603E0468A0122161959B3CE7DE3CAC39AE0C3D7BB7AA158811679C97F24
- Controllertests 9F51AAC4E0F1F86CFEF19521179D24B1974888E643A9FB418D4F999098E5E689
- Inputs 20E7C39FE59A979A9DE156BB5111EACE9529F94AC5CB9844DDE0727E43DB45A1
- Inputtests 674BD99DB8699D73DC88F5AAD2581A753FB49BB7717822FBA73AEB30EC76515B

Der bestehende AI-Workflow erhält einen zusätzlichen Testtrigger und einen statischen
Controller-Testschritt. Runtimejob/-Abhängigkeiten bleiben unverändert; wegen neuer
öffentlicher Demosource wählt der bestehende konservative Selector tatsächlich Runtime
True. Aktuelle Head-/Main-Gates müssen daher auch die vorhandene isolierte Drei-
Versionsmatrix mit eigenem CI-Cleanup regulär bestehen. Diese Matrix prüft bisherige
Scopes, keine Nativequalifikation des neuen Kostencontrollers. Kein eigener neuer
Qualifikationscontainer in diesem Vorbereitungsschnitt; zusätzliche lokale Controller-
SQLcalls0. CI-Arbeit ist ein erforderliches aktuelles Integrationsgate, kein freiwilliger
Retry bereits grüner lokaler Profile. Keine zusätzliche Review-/Modellkette.

Nach PR-/Head-/Main-/Tree-/FF-/Ownbranchabschluss folgt die getrennte konkrete
Nativequalifikation des neuen Kostencontrollers mit vor Admission festem Version-/
Fehlerlauf-/Owncontainerbudget. DGN-010 bleibt PROPOSED und die volle Abnahme offen.
