# DGN-010 – feste öffentliche Kostenproducer-Eingaben

Stand: 2026-10-12. TSK-011/CUR-021; DGN-010 PROPOSED, öffentlicher Producer WARN.
Dieser Schnitt bereitet ausschließlich SQLtexte vor. Er startet keine Clients,
provisioniert nichts und attestiert keine neue Nativeausführung.

## Ausgangsstand und Umfang

[PR207](https://github.com/gecompat/SQL_PerformanceSchulung/pull/207) ist vollständig
abgeschlossen: Head 58c9ab2d6239fd4d0205bfe5d4c6e49d0986a16f,
main f8b212f1e25370cda958892a53c75890a3e7367a, acht Head-/sechs Main-Workflows
PASS, ganzer Tree 2ed71dc79ff6c62c47cb0e13455b2b32c78e664e gleich,
FF-main sauber und eigener lokaler/Remote-Branch entfernt. Der Runtimejob wurde
aufgrund tatsächlicher Auswahl False übersprungen; dies ist kein Runtime-PASS.

Der [öffentliche Kostenrecordvertrag](SQL_SERVER_2025_AI_DGN010_COST_CONTRACT.md)
bleibt unverändert. Als erster Teil der Produceranbindung stellt
[dgn010_cost_inputs.py](../../Tests/Static/dgn010_cost_inputs.py) ausschließlich
`build_sql(...)` und `state_sql(...)` bereit. Noch kein ausführbarer Kostenrunner,
keine Integration in den bisherigen SELECT-/DML-Runner oder dessen Nativeclaim.

Ein Implementierungsverantwortlicher, enger unabhängiger Review der neuen
DB-/Marker-/Source-/Lease-/Inputkomposition; keine offenen P1/P2. Sechs kohärente
Quellenkandidaten, Checkpoint3/hard6; null neue SQLcalls/Container. Die ausdrückliche
Freigabe gewöhnlicher Folgeschritte besteht. Modell-/Tokenverbrauch bleibt unbekannt.

## Sicherheits- und Datenvertrag

DB-/Source-IDs sind echte SQL-int-Werte (keine Bool-/Float-/Stringaliase), DB-ID≥5,
Source-ID≥1. CREATE/DROP und Cycle1/2 sind fest; vollständige Lease-/Index-/Spalten-
Populationen werden vor Einbettung gegen den Recordvertrag geprüft. CREATE verlangt
exakte Abwesenheitslease, DROP genau die vollständige eigene Candidatelease.
Keine freien DDL-, Objekt-, Query- oder Modelltexte. Strings werden SQL-literalgebunden.

Der unveränderte vorhandene Markervertrag prüft die tatsächliche DB-ID, vollständigen
DB-Namensbytes und alle vier vollständigen Markername-/Wertbytes inklusive Längen,
Scope und Population vor Stateaufnahme oder DDL. Der tatsächliche Source-OID-Guard
weist nun auch OBJECT_ID-NULL ab (`ISNULL(...,-1)`); ein fehlendes Objekt kann den
SQLvergleich nicht als UNKNOWN umgehen. Gehaltene vollständige Index-/Spalten-Lease
und tatsächlicher CREATE-/DROP-Prestate werden vor dem EXEC geprüft.

Das feste DDL-Template stammt aus der bereits qualifizierten eigenen
[privaten Buildkostenquelle](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md).
Nach EOL-Normalisierung ist allein der genannte NULL-Guard geändert. Tatsächliche
Request-/Counter-/UTC-/DDLdigest-/Lease-/Chunkgrenzen bleiben erhalten. Die
Stateaufnahme nutzt den unveränderten bestehenden 13-Key-Snapshotvertrag mit
vollständigen Source-/Variant-/Markerbytes und begrenztem Transport.

Die API bestätigt keine vorhandene Version, Preflightfreigabe, Vollstatekontinuität,
Negativkontrolle, bekannten Clientendstatus oder Cleanup. Diese Pflichten gehören
zum späteren Runtimecontroller. Vor einem Aufruf bleiben die bereits dokumentierten
SQL17.0.5005.3/Developer/CL170-, eigene neue Instanz-, vier CPU/sechs GiB-, 1000-Row-,
300/60-Sekunden-, Marker-/KnownEnd-/Cleanupgrenzen maßgeblich. Es gibt keinen
generischen Fremdserver-/Cloud-/ONNX-/Hostpfad und keine neue Runtimefreigabe aus
einer rein synthetischen Eingabe oder bloßer Recordvalidierung.

## Tatsächliche Prüfung und Aufwand

[Sechs reine Tests](../../Tests/Static/test_dgn010_cost_inputs.py) PASS:
feste CREATE-/DROP-Eingaben, alle vier vollständigen Marker vor DDL, strikte IDs/
Cycle/Kind und Injectionabweisung, vollständige Leasepopulation, Source-/Stateform
und keine Prozessstarts beim Vorbereiten. Enger unabhängiger Quellenabschluss
ohne offene P1/P2; vorhandene Nativequellen nicht erneut analysiert oder ausgeführt.

Aktuelle Modul-/Test-SHA256:

- 155FBEBD6EB7904D1C157B245CF895593311F7FAADE8CEF0DD29F5F11E4C8AB5
- D52748DFF9AFC945D20DF86A4B7469A7AD70D4CA7B8D757DE92C822697291BB5

Die Komposition wurde zusätzlich rein gegen alle acht tatsächlichen gehaltenen
DDL-Leases der beiden exakt gebundenen vorhandenen Vollrecords geprüft. Caller-DB
jeweils aus separat vorhandenem Native-DBID-Frame; feste Vorlage/alte Quellen und
Recordhashes unverändert. Dies ist Quellen-/Kompositionsbindung, keine erneute
Nativequalifikation der öffentlichen API. Rohrecords und erzeugte SQLdigests privat.

Der bestehende AI-Workflow erhält zwei zusätzliche Triggerpfade und einen reinen
statischen Testschritt. Runtimejob/-Abhängigkeiten bleiben unverändert, tatsächliche
Base-/Head-/Main-Auswahl False erforderlich. Kein neuer Native-Matrixlauf, keine
zusätzliche Modell-/Reviewkette. Geänderter Datenschutzcheck, diff-check und aktuelle
Head-/Main-/PR-/Tree-/FF-/Ownbranchgates bleiben erhalten. DGN-010 PROPOSED,
Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED.

Nach Integration folgt der tatsächliche öffentliche begrenzte Kostencontroller mit
Vollstate-/Negativ-/KnownEnd-/Cleanupbindung und anschließend separat gebundener
Versions-/Runtimequalifikation. Ein bloßer Eingabe-PASS schließt diesen Schritt nicht.
