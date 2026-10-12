# DGN-010 – separate native öffentliche Kostenqualifikation

Stand: 2026-10-12. TSK-011/CUR-021; DGN-010 PROPOSED/Producer WARN.
Vor erster Admission feste eigene lokale Welle. Native Resultate zunächst offen.

## Integrierte Quellen und Scope

[PR209](https://github.com/gecompat/SQL_PerformanceSchulung/pull/209) vollständig
abgeschlossen: Head e457849133963ce73dada4cdce8e68a0baa848b4,
main bf206ccbb1b0892773b9b0ef785b85e80b1ba9d0, neun Head-/sieben Main-Workflows
PASS, Tree 9402d91653a3fce44000b68dc1d62142bb5b4b9b gleich, FF-main sauber,
eigener lokaler/Remote-Branch entfernt. Die vorhandenen drei Versionsjobs samt
eigenem CI-Cleanup sind an Head/Main jeweils bestanden; keine Kostencontroller-
Nativequalifikation daraus ableiten.

Der [öffentliche Kostencontroller](SQL_SERVER_2025_AI_DGN010_COST_CONTROLLER_REVIEW.md)
und seine ausführungsrelevanten Abhängigkeiten sind integriert. Der enge unabhängige
Controller-/Inputreview und engste Owninput-Deltaabschluss sind geschlossen.
Aktuelle Working-tree-Quellen sind nach ausschließlich EOL-Normalisierung exakt
an die geprüften öffentlichen Quellen gebunden. Tatsächlich ausgeführte Rohbytes
werden zusätzlich je Admission vollständig gehasht.

Der neue private Qualifikationsadapter übernimmt die bereits geprüfte eigene
Public-Qualifikationsbasis. Neues Delta: Kostencontroller, feste eigene Rawinput-
Unterpfade sowie neue ausgeführte Kosten-/Markerabhängigkeiten. Server, DB, Executable
und Public-/Rawinputpfade sind gebunden. Enger unabhängiger Adapterabschluss ohne
offene P1/P2; SHA256 1D7EDFCC1E0C8FD5A5076DA66DBC4076425ADDA9FF8C4FDAFA4C3C865D0BBF60.
Keine weitere Vollanalyse alter Endstatus-/Containerhelpers und kein Review einer
Reviewkette. Ein Implementierungsverantwortlicher; Modell-/Tokenverbrauch unbekannt.

## Vor Admission endlicher Ablauf

Sechs kohärente Korrekturkandidaten, insgesamt höchstens zwölf neue eigene serielle
Container. Gemeinsamer Ledger zählt alle historischen FAILs dieser Welle, kein Reset.
Checkpoint3/hard6. Retry nur bei geänderten ausführungsrelevanten Quellen oder neuer
konkreter Evidenz; unveränderte grüne Profile werden nicht freiwillig wiederholt.
Gewöhnliche Folgefreigaben sind durch den Benutzer bereits erteilt.

Feste sieben Slots in dieser Reihenfolge:

1. Zwei stabile neue vollständige SQL2025-Kostenprofile.
2. Zwei SQL2019- und zwei SQL2022-Versions-SKIPs, jeweils vor Setup.
3. Ein kontrollierter SQL2025-Fault direkt nach PASS-Setup mit tatsächlicher Recovery.

Jeder Slot verwendet eine neue eigene vollständig markierte Developerinstanz,
vier CPU/sechs GiB, eindeutigen Voll-CID, loopbackgebundenen dynamischen Port und
bereits vorhandenes fixes Image. SQL2025 exakt17.0.5005.3; SQL2019/2022 tatsächlicher
Major15/16 und feste vorhandene Imagebytes. Keine Pulls oder Installationen.
Tatsächliche Image-/CID-/Name-/Ownerlabel-/Memory-/CPUbindung vor eigener Entsorgung.
Nur eigene Datenbank SQLPERF_LAB_DGN010_LOCAL; andere Repositories/Instanzen unverändert.

Alle Normalphasen einschließlich Readiness teilen 300 Sekunden; anschließend einmal
insgesamt höchstens 60 Sekunden für SQL-/frische DB-Abwesenheits-/CID-/Namenscleanup.
Controller-/Adapter-Parentbudget kann nur verkürzen. Host-sqlcmd mit Secret ausschließlich
im Environment, kein Passwortargument oder SQLCMDINI. UNKNOWN sperrt neue SQLclients
und erhält eigene SQLinputs; keine ungebundene SQL-Rettung oder Budgetverlängerung.

## Native Acceptance und Grenzen

Positive Slots müssen den tatsächlichen öffentlichen Controller mit vier eigenen
DDL-Fenstern, acht vollständigen 1000-Row-Sourceaufnahmen, zehn unabhängigen 1000-Row-
Vollstates, tatsächlich abgewiesener Source- und DROP-Abwesenheitsprobe sowie Restore
durchlaufen. Volle DB-/Marker-/Source-/gehaltene Index-/Spalten-Lease-/Request-/Counter-
UTC-/Zwischenfensterbindung vor Aggregation. Öffentlicher Ausgang bleibt WARN,
geprüfte Aggregate behalten Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED.

Versions-SKIPs verlangen tatsächliche eigene Instanzmajorversion, SKIP_VERSION vor
Setup und neue DB-Abwesenheit. Fault verlangt die vollständige bekannte feste
AFTER_PASS_SETUP_BEFORE_SOURCE-Sequenz, FAIL_EXECUTION, tatsächlichen SQLcleanup und
neue DB-/CID-/Namensabwesenheit. Kein allgemeiner harter Build-/DML-Abbruchclaim.

Alle Inputs/Logs/Vollrecords/Identitäten bleiben privat unter Runtime; kein Rohrecord
in Git. Vor Publikation werden neue tatsächliche Records rein an ausgeführte Quellen,
separate Caller-DB-Frames und vollständige Cleanupbelege gebunden. FAIL/WARN/SKIP bleiben
wahrheitsgemäß sichtbar. Source-/API-/Version-/Cleanup-Qualifikation ist keine gesamte
Performance-, Commit-, Worker-, Nettonutzen-, Teaching-Path- oder Modulabnahme.

Dieser Nativeschnitt ändert zunächst ausschließlich kanonische Nachweisdokumente.
Keine neue CI-Runtimequelle oder Workflowänderung; die tatsächliche Auswahl für
Head/Main muss False bleiben. Aktuelle betroffene Projektgates/Privacy, PR-Integration,
Treegleichheit, FF-Synchronisierung und Ownbranchcleanup bilden seinen Abschluss.
Keine Wiederholung der zuvor grünen Pflichtmatrix ohne neue betroffene Quelle.

Native Resultate, lokale Ownership-/Cleanupclosure und aktuelle Integrationsgates
werden nach tatsächlichem Ablauf ergänzt. Bis dahin kein Native-PASS.

## Native C1 vollständig bestanden

Alle sieben festen Slots bestanden ohne neue Korrekturwelle. Zwei stabile
SQL2025-Profile mit tatsächlichem öffentlichen Ausgang WARN, vier tatsächliche
SKIP_VERSION vor Setup (je zweimal Major15/16) und ein tatsächlich erwarteter
FAIL_EXECUTION nach PASS-Setup mit vollständiger Recovery. Alle sieben eigenen
DB-/CID-/Namenslifecycles geschlossen, zusätzliche Ownerlabel-Inventur leer,
keine verbleibenden eigenen SQLinputs und kein UNKNOWN.

97 protokollierte tatsächliche Nativephasen: je35 pro positivem Profil, je5 pro
Versions-SKIP und7 für den Setupfault. Readiness-/separate Engineversionqueries
sind darin nicht enthalten; diese Zahl ist kein Total aller SQLrequests.
Acht vollständige DDL-Fenster, 16000 vollständige Source-/20000 Vollstate-Rows,
vier echte 51003-Abweisungen und vollständiger Source-Restore gebunden.

| Profil | Cycle | DDL | ElapsedUs | CpuMs | Reads | LogicalReads | Writes |
|---|---:|---|---:|---:|---:|---:|---:|
| 1 | 1 | CREATE | 12317 | 8 | 0 | 263 | 18 |
| 1 | 1 | DROP | 4097 | 2 | 0 | 105 | 0 |
| 1 | 2 | CREATE | 49211 | 46 | 0 | 228 | 16 |
| 1 | 2 | DROP | 4093 | 2 | 0 | 105 | 0 |
| 2 | 1 | CREATE | 12292 | 10 | 0 | 263 | 18 |
| 2 | 1 | DROP | 4105 | 3 | 0 | 105 | 0 |
| 2 | 2 | CREATE | 8195 | 7 | 0 | 228 | 16 |
| 2 | 2 | DROP | 4123 | 2 | 0 | 105 | 0 |

Der größere zweite CREATE-Wert von Profil1 bleibt erhalten; kein stilles Entfernen
als Warmup/Ausreißer oder Ersatz durch das private frühere Profil. Beide Samples,
Nullwerte und exakte Mediane werden je Profil getrennt ausgegeben. Die fünf
A/B/A/B/A-Allokationsaufnahmen je Profil bleiben separat im geprüften Aggregate.
Keine isolierten Worker-/Compile-/Log-/Commit-/ganzen Lifecycle-/Nettonutzenclaims.

Private Vollrecords und alle tatsächlich protokollierten Nativeframes anschließend
rein neu gebunden: vollständige Source-/State-/DDL-Frames, tatsächliche Fehlerframes,
separate native Caller-DB/OID, aktuelle ausgeführte Quellen, Phasenpopulation,
Aggregate und frische externe Abwesenheit. Null zusätzliche SQLcalls für diesen
Nachweis. Positive profile.json-SHA256:

- 2b21ce563a0d233c7a7f1b82b5a65e974c7abf35098f64bea384a5f9a9686e2e
- cef90dd40051e03ed9bdecbe983a6da70c2d59e081b202e74fd8dc7185fbea5b

Der zusätzliche reine Vorab-EOL-Helfer war zunächst zu eng: Er normalisierte auch
die bereits byteidentischen CRLF-Eingabemodule gegen deren unnormalisierte Review-
Hashes. Die erste Admission startete nach diesem Helfer-FAIL; die bereits zuvor
kanonisch registrierten und im Adapter fest durchgesetzten Scope-/Budget-/Safetygrenzen
blieben unverändert. Anschließend wurden alle vier Quellen korrekt als raw-identisch
oder ausschließlich EOL-identisch an den Review gebunden; keine ausführungsrelevante
Codeänderung oder verlorene Sourcebindung. Der private zusätzliche Budgetreceipt
wurde dadurch erst nach erster Admission erstellt. Dieser Ablaufbefund bleibt
sichtbar; er ist keine neue Native-Korrekturwelle und kein zusätzlicher SQLretry.

Ein Quellenkandidat/sieben eigene Container verbraucht. Begrenzte öffentliche
Kosten-/Versions-/Setuprecoveryqualifikation bestanden; öffentlicher Gesamtstatus
WARN und DGN-010 PROPOSED. Vollständige Runtime/TP-PERF/Worker/Commit/Nettonutzen/
Teaching-Path-/Modulabnahme bleiben offen. Aktuelle Head-/Main-/PR-/Tree-/FF-/
Ownbranchgates schließen diesen Schnitt, danach die nächste unabhängige offene
Kosten-/Lehrpfadfrage fortsetzen; keine unveränderte grüne Profilwiederholung.
