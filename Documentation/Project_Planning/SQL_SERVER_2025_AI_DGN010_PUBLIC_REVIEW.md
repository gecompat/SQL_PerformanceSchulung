# DGN-010 – öffentlicher begrenzter SELECT-/DML-Producer

Stand: 2026-10-12, TSK-011/CUR-021; Demo weiterhin PROPOSED.
Der [öffentliche Runner](../../Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/README.md)
führt getrennte ungezwungene Reader-SELECTs und Owner-UPDATE/Rollback-Batches
ohne/mit eigenem Candidateindex aus. Der [Auswertungsvertrag](SQL_SERVER_2025_AI_DGN010_BENCHMARK_CONTRACT.md)
bleibt für feste Population, Ergebnisdigests und numerische FWK-Invarianten maßgeblich.

## Quellen und Grenzen

Nur feste eigene SQLphasen, keine freien Queries/Modellausgabe, keine Provider-,
Cloud-, ONNX-, Host- oder anderen Repositoryeffekte. SQL17.0.5005.3, CL170,
Developer Enterprise mit dokumentierter EditionID -2117995310/EngineEdition3,
vier CPU (Central Processing Unit; Prozessor)/sechs GiB, 1000 synthetische Rows, 100 F-Payloadbytes, SIMPLE 256/64 MB,
unveränderte MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad)/PREVIEW_FEATURES=0. Native Scopegrenzen sind keine isolierten
Query-/Worker-/Indexkosten. Keine garantierte Indexnutzung, Signifikanz oder
vollständige TP-PERF-/Nettonutzen-/Modulabnahme.

Setup und jede Mutation/Drop verlangen alle vier vollständigen bytegenauen
Eigentumsmarker. Vorhandene Datenbanken werden abgewiesen. Öffentlich kein
Rawexport oder Provisioning; nur geprüfte begrenzte Aggregate nach bekanntem
Clientende und tatsächlichem Cleanup. Native Manipulationsgegenproben der
vollständigen Marker und harte Unterbrechung während Build/DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) bleiben separat
offen. Dieser Schnitt beansprucht ausschließlich regulären Lifecycle und
kontrollierten Fehler unmittelbar nach PASS-Setup mit anschließender Recovery.

## Entwicklung und unabhängiger Review

20 reine Controllermethoden bestanden: beide vollständigen festen Scopes,
Source-/Candidatebindung, Versions-SKIP vor Setup, exakte Fehlerframes,
Bestätigungen, Inputbindung, gemeinsames Cleanupbudget, tatsächlicher lokaler
Endstatus und Remote-Waitframe. Elf Selektormethoden bestanden; bestehende
20 reine Recordmethoden unverändert aus PR195 wiederverwendet, keine lokale
Wiederholung. Neue reine Fixtureoptionenauswertung zunächst FAIL, korrigiert;
ein privater Dispatcherimport kollidierte vor NativeAdmission mit dem bestehenden
Readinessmodul, korrigiert. Beide Fehler sind reine Vorbereitung, keine Native-PASSs.

Ein Reviewer ausschließlich für neues Producer-/Marker-/Endstatus-/Messscope-
und Selektorrisiko. Zwei P2 vor Admission geschlossen: vollständiger Native-
Negativfehlerframe ohne gemischte Client-/Proxyfehler, tatsächlicher Remote-Endframe
des eigenen Dockeradapters. Ein lokaler Proxy-Poll ist kein Remote-Endnachweis;
Timeout/Collectorabbruch oder fehlender/inkohärenter Frame führen sticky UNKNOWN
und sperren weitere SQLclients. Kein weiterer Review eines Reviews.

Vor Admission sechs Quellenkandidaten, 14 neue eigene serielle Container je
Kandidat, insgesamt höchstens 84, reguläres 300-/gemeinsames Cleanup 60-Sekundenbudget.
Retry nur bei relevant geändertem Nativeinput oder neuer Evidenz; historische
FAILs bleiben im gemeinsamen privaten Ledger. Modell-/Tokenverbrauch unbekannt.

Kandidat1 bestand acht Versions-SKIPs, verfehlte dann das erste SQL2025-Profil
vor Setup mit SKIP_CONFIGURATION: der Preflight erwartete einen alten Edition-
Anzeigenamen. Qualifikation FAIL; alle neun DB-/CID-/Namensabwesenheiten bestätigt,
kein unbekannter Clientendstatus. Kandidat2 bindet stattdessen die dokumentierte
EditionID und explizite NULLabwehr sowie tatsächlichen Versions-/Editionsframe.
Der geänderte gemeinsame SQLpreflight wird auf allen drei Engineversionen geprüft.
Kein Retry unveränderter Quellen, kein Zurücksetzen des historischen Fehlers.

Native Ergebnisse und aktuelle Head-/Main-Gates folgen vor Abschluss. Numerische
FWK-PASSs werden weiterhin von Gesamt-WARN und NOT_ESTABLISHED getrennt.

## Verarbeitung und CI-Aufwand

Ein Owner, ein Reviewer für konkrete Risiken mit enger Closure nach geänderten
Inputs. SQL- und Ergebnisquellen aus den bereits geprüften getrennten privaten
Scopes übernommen; gemeinsame Prozess-/Container-API (Application Programming Interface; Programmierschnittstelle) bleibt unverändert.
Neue Produktionsabhängigkeiten unter Tests/Static und ihre beiden Fixtures
wählen jetzt ausdrücklich die native KI-Matrix. Ein alleiniger Controller-
Testdateiwechsel bleibt statisch; andere Workflowentscheidungen unverändert.

Die bestehende KI-Matrix erhält einen neuen begrenzten Consumerstep: zwei
Lifecycles je Scope und unterstützter Version, tatsächliche Setupfaults separat.
Keine zusätzliche Matrix/Instanz für jeden einzelnen Test; die drei schon
wegwerfbaren CI-Instanzen werden seriell verwendet und unabhängig bereinigt.
Aktuelle Head- und Main-Gates sind erforderliche frische Integrationsevidenz.
Es gibt keinen Vollprivacy-Scan je Fachworkflow; geänderte Dateien vor jedem
Commit und ein zentraler Vollscan am aktuellen Head/Main bleiben verpflichtend.
Keine automatische Cancellation mutierender Runs oder unveränderte Vollanalysen.

## Quellen und nächste Abnahme

[Microsoft SERVERPROPERTY](https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver17),
Abruf 2026-10-12, dokumentiert EditionID -2117995310 für Developer vor 2025 und
Developer Enterprise ab 2025. Dieser feste Metadatenvertrag ersetzt weder
Versions-/CL- noch Rechte-/Ressourcenprüfung.

Nach Integration/Synchronisierung/eigenem Cleanup folgt die getrennte begrenzte
native Marker-Manipulationsqualifikation des öffentlichen Pakets. Aktuelle
Readerpläne/Indexnutzung, INSERT-/Commit-/Build-/Worker-/weitere DMLkosten,
vollständige TP-PERF-Abnahme, Lehrmaterial und Modulabnahme bleiben offen.

## Tatsächlicher begrenzter öffentlicher Nachweis

Kandidat2 vollständig geschlossen: acht tatsächliche Versions-SKIPs vor Setup
(je Scope zweimal 2019/2022), SELECT und DML jeweils zweimal vollständig SQL2025,
zwei kontrollierte Fehler nach PASS-Setup mit anschließender eigener Recovery.
14 neue eigene Container dieses Kandidaten, alle DB-/CID-/Namensabwesenheiten
unabhängig bestätigt, kein unbekannter Clientendstatus. Einschließlich C1 sind
23 Container geschlossen; der Editions-FAIL bleibt erhalten, vier Kandidaten
des gemeinsamen Sechserbudgets verbleiben, kein Budgetreset.

Vier vollständige öffentliche Profile an tatsächliche Nativeframes gebunden:
184000 Source-Rows in 184 Vollsnapshots, 116 positive Fensterframes einschließlich
vier separater Kontrollen, acht echte 51003-Negativframes, 32 Indexübergänge,
7240 vollständige Statementoracles/72400 Rowkontrollen und 48 numerische FWK-PASSs.
Jeder tatsächliche Versions-/Editionsframe ist 17/17.0.5005.3/3/-2117995310;
unabhängige DB-ID, komplette Rawhashes und ausgewählte Ausführungsquellen gebunden.
Source-/Querynegative/Restore/Idempotenz, Config-/Readerrechte, eigener Rollback
und markergebundener regulärer SQLcleanup bestanden. Zehn Warmups/18 Messfenster
je Profil; sechs AB-/BA-Samples je Zustand, drei AA-Paare separat. Alle Samples,
Nullen/Ausreißer/exakte Mediantexte erhalten. Kein Rawausgabeclaim aus CLI/Repository.

Öffentlicher Gesamtstatus WARN_OPTIONAL_EVIDENCE_SKIPPED; reine Recordvalidierung
und numerische FWK-Invarianten PASS, Runtime-/TP-PERF-Abnahme NOT_ESTABLISHED und
aktuelle Indexnutzung NOT_CAPTURED. Keine vollen Worker-/Indexnettonutzen-/Modulclaims.
Separate vollständige Marker-Manipulationsgegenproben, harte DML-/Buildunterbrechung,
Readerpläne, Insert-/Commit-/Buildkosten und vollständige TP-PERF-Abnahme offen.

Aktuelle Head-/Main-Gates mit tatsächlicher Consumer-Matrix, PR/Integration,
ganze Treeübernahme/FF-Synchronisierung/eigener lokaler und Remote-Branchcleanup
folgen vor Abschluss. Danach native Marker-Manipulationsqualifikation desselben
öffentlichen Pakets. Allgemeine Entwicklung/DGN-007/andere Automationen pausiert;
keine Provider-/roten Hosteffekte oder andere Repositoryänderung, Verbrauch unbekannt,
Heartbeat aktiv.
