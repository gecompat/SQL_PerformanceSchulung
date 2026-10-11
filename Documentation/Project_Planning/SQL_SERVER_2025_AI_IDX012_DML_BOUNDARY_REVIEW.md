# IDX-012 – öffentliche DML-Grenzenvorstufe

Stand: 2026-10-11. Begrenzter technischer Befund, keine vollständige Demoabnahme.
Autorität: TSK-006, DEC-074 und ausdrückliche weitere lokale Wellenfreigabe.
Frühere ANN-Kandidatenbudgets und FAIL-Checkpoints bleiben unverändert erhalten.

## Umfang und Quellenreview

Ein Implementierungsverantwortlicher, ein erforderlicher unabhängiger Review vor SQL.
Neuer Umfang: höchstens zwei kohärente Kandidaten und vier eigene serielle Container;
zwei vollständige Lifecycles je positivem stabilen Kandidaten. Tatsächlich verbraucht:
ein Kandidat, zwei Container, keine Runtimekorrektur oder Wiederholung alter Wellen.
Der Review schloss ohne offene P1/P2: gültige positive DML-Kontrollen vor Indexbau,
wirkliche Fehleraufnahme im unteren dynamischen SQL-Scope, Transaktionswerte vor
JSON, vollständige Quellen-/Indexmetadatenprüfung und eigener Recovery-/Admissionpfad.

Quellenbindung der tatsächlichen Läufe, SHA256:

- run_profile.py: 384d328519b5feeb543e33d4e6e1d5f92a913d9bc498055d7c377ff1080ea266
- 30_DmlBoundary.sql: c4f61c2992d26f66deab1331b19cc9e2199858576d5a7e56dbe10c9b6907c0bf
- 40_SourceAfter.sql: 5d9bef4a17742be9e2e252e05eaaf28dfc9a947d25026df18c8d6230f64194ea
- dml_boundary_evidence.py: e9a5eca06d62d1d4aa31fbd9add761a07d45bb3ea4055153c4cbd9a6963c8628
- lokaler Parent: bbe8b6c03d36e32a7b6e15d71f23de8fee308c48933c2ee800176696b3f5de47

Die vollständige Quellenliste und redigierten Rohoutputs bleiben lokal unter Runtime;
keine Zugangsdaten, realen Systemdaten oder Rohoutputs werden versioniert.

## Tatsächliche Runtime

Beide eigenen Container: SQL Server 17.0.5005.3, Developer/EngineEdition 3,
Compatibility Level 170, vier CPUs/sechs GiB, ausschließlich vorhandenes Image
78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726.
Kein Pull, Provider-, Cloud-, ONNX- oder Hostkonfigurationsaufruf.
Eigene IDX-012-DB mit vollständigen bytegenauen Project-/Contract-/Demo-/Tokenmarkern.
999 deterministische float32 VECTOR(3)-Rows; der fehlende Id-1000-Insert erreicht
innerhalb seiner Transaktion höchstens 1000 Rows. Alle DML werden zurückgerollt.

| Beobachtung | Lauf 1 | Lauf 2 |
|---|---|---|
| vollständiger eigener Token | CDC97E68E2114CE5 | 63AD6D8A17CE4FE9 |
| technischer Ausgang | WARN_OPTIONAL_EVIDENCE_SKIPPED | WARN_OPTIONAL_EVIDENCE_SKIPPED |
| erfolgreiche DML-Kontrollen ohne Index | 4/4 | 4/4 |
| tatsächliche Verweigerungen mit Index | 4/4, 42231/State 1 | 4/4, 42231/State 1 |
| Indexbuild-Wandzeit | 801,053 ms | 1130,006 ms |
| neue vollständige Quellenaufnahme | 999 Rows, alle Texte/Distanzen identisch | 999 Rows, alle Texte/Distanzen identisch |
| ursprüngliche Preview/MAXDOP und tatsächlicher Restore | 0/0 | 0/0 |
| gesamter eigener Cleanup ab erstem Restore | 12,180 s | 13,164 s |
| separate DB-/eigene CID-/Namensabwesenheit | bestanden | bestanden |

Operationen in beiden Stages: UPDATE Id 23, DELETE Id 23, gültiger INSERT Id 1000
und MERGE mit UPDATE Id 23. Ohne Index sind Erfolg, genau eine betroffene Row,
tatsächlicher Zielzustand und unveränderte übrige Quellen vor Rollback geprüft.
Während DELETE/INSERT sind tatsächlich 998/1000 Rows vorhanden; UPDATE/MERGE
haben 999. Nach jedem Rollback: 999 vollständige originale Quellbytes,
@@TRANCOUNT=0 und XACT_STATE()=0, vor dem JSON-SELECT aufgenommen.
Mit Index stammen ERROR_NUMBER/ERROR_STATE/ERROR_MESSAGE aus dem tatsächlichen
CATCH; kein clientseitig erfundener Fehler. Indexmetadaten bleiben nach jeder
Verweigerung und in einer neuen Verbindung vollständig identisch.

Der eigene Index ist tatsächlich type 8/VECTOR, DiskANN/COSINE, aktiv und nicht
hypothetisch. Die tatsächlichen build_parameters bleiben in der lokalen Aufnahme;
keine numerische Generation wird daraus abgeleitet. Generation UNKNOWN,
Freshness NOT_TESTED und Runtimequalifikation NOT_ESTABLISHED bleiben erhalten.
Keine VECTOR_SEARCH oder Benchmarkserie in diesem Scope.

Recovery verwendet neue Clients für beide tatsächlichen Restores, vollständige
Attestation vor markergebundenem Drop und unabhängige DB-Abwesenheit. Der Parent
prüft zusätzlich eigene CID, Name, Image, Ownerlabel, CPU-/Memorygrenzen und
unabhängige Abwesenheit nach Entfernung. Beide Lifecycles sind im lokalen
Admissionledger geschlossen; kein weiterer unveränderter Lauf ist erforderlich.

## Grenzen, Tests und Aufwand

Dies attestiert vier konkrete DML-Verweigerungen in diesem festen Profil. Kein
allgemeiner DML-/Freshness-/Generationsbeweis, keine vollständigen Build-/Storage-
kosten, keine Minimalrollen-, Hard-Abort-, 2019-/2022- oder TP-PERF-Abnahme.
Der öffentliche Ordner bleibt ohne Manifest eine Vorstufe; TSK-006 bleibt offen.

Zwölf synthetische Controller-/Recoverytests, elf DML-Evidenzgegenproben und zehn
CI-Selectortests bestanden. Demoausführungspfade und Kennungsregistrierung bestanden.
Zwei anfängliche reine Controllerfixtureläufe waren jeweils 11/12 wegen übernommener
fehlender IDX-011-Dateinamen; die feste Testdateiliste wurde vor SQL korrigiert.
Kein Container- oder SQLbudgetverbrauch durch diese Offlinefehler.

Aufwandassessment: zwei neue statische Tests im vorhandenen KI-Job; Runtime-
Jobdefinition unverändert. Der öffentliche Demopfad wählt konservativ die
bestehende acht-Demo-KI-Matrix als Head-/Integrationsgate. Dies ist keine IDX-012-
Runtimeabnahme. Nur ein erforderlicher enger Review, keine Reviewkette und keine
Wiederholung alter Runtimewellen. Modell-/Tokenverbrauch bleibt unbekannt.

Fachliche Quelle SRC-077: [CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17),
Abruf 2026-10-11. Neuere Herstellerangaben zur DML-Unterstützung werden nicht auf
den tatsächlich geprüften 17.0.5005.3-Build übertragen. Das nächste getrennte
Arbeitspaket betrifft Indexdrop, tatsächliche Änderung und erneuten Aufbau;
keine weitere Scoped-Option oder stilles Wiederöffnen dieses Kandidatenbudgets.
