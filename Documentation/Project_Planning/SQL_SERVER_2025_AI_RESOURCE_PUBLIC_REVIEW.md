# RES-008 – öffentlicher begrenzter Consumer

Stand: 2026-10-12, TSK-010/CUR-020, Basis
`1891b35d81dcdc61274a4a738994c3b25aa09dd4`, Branch
`codex/sql2025-ai-res008-public`. Das
[öffentliche Profil](../../Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/README.md)
ist ausführbar; RES-008 bleibt PROPOSED. Die vollständige Demo-/TP-PERF-/Modul-
abnahme ist weiterhin offen, neun übrige lokale Demopakete bleiben IMPLEMENTED.

Der [vorherige Planteilnachweis](SQL_SERVER_2025_AI_RESOURCE_PLAN_REVIEW.md)
ist über PR187 vollständig abgeschlossen: Head 334f91f743081c7c73ff1d823715e011227dec6c
mit sieben aktuellen Head-Workflows, Squash 1891b35d81dcdc61274a4a738994c3b25aa09dd4
mit fünf aktuellen Main-Workflows PASS. Vollständiger Tree
`d516ca9e6fc919c5c05bc8bf4a83fe32e5871b04` übernommen; lokales main sauber per FF
synchronisiert und eigener lokaler/Remote-Branch entfernt. Historische Quellen-,
Mess- und Plan-FAILs bleiben in ihren Nachweisen erhalten.

## Öffentliches Verhalten und begrenzte Abdeckung

Sechs vorhandene Setup-/Source-/Cleanup-/Guard-/Mess-/Plan-SQLs exakt bytegleich
übernommen; neue read-only Preflight-/Abwesenheits-/DB-ID-Phasen und feste eigene
DELETE-Gegenprobe. Reine Parser übernehmen vorhandene Source-/Fenster-/Plan-
oracles ohne private Runtimeimports oder automatische Rohpersistierung.
Feste Demo-/Run-/DB-Werte und Messvariablenwhitelist; öffentliche sqlcmd-Prozess-
APIs mit kompatiblen Vollscalaroptionen nur für Planrequests. Gemeinsame API (Application Programming Interface; Programmierschnittstelle)
exakt unverändert; kein DGN-007- oder anderer Workstream wiederaufgenommen.

Ein Owner, sechs Kandidaten/maximal 42 zusätzliche serielle eigene Container
für sieben feste Slots. C1 bestand alle sieben Slots. Kein weiterer unveränderter
grüner Lauf. Ein privater Launcherimportfehler vor Admission wurde korrigiert;
dabei liefen weder SQL noch Container. Kein nativer FAIL verschwiegen oder Budgetreset.
Alle sieben Container kamen aus festen bereits gecachten 2019-/2022-/2025-Images,
vier CPU (Central Processing Unit; Prozessor)/sechs GiB, Loopback, Passwort nur ENV, kein Pull. Reguläres Gesamtbudget
300 Sekunden einschließlich Readiness, gleiche 60 Sekunden Cleanup ab Beginn
der finalen SQL-/Abwesenheitsphase bis unabhängiger DB-/CID-/Namensabwesenheit.

Tatsächliches SQL 2019/2022: je zwei SKIP_VERSION vor Setup, keine Lastphase.
Tatsächliches SQL 17.0.5005.3: zwei vollständige öffentliche Consumerlifecycles,
je 20 Warmups, 54 AB-/BA-/AA-Requests, 5420 einzelne Id 1-/Distanz 0-Oracles und
vier repräsentative Actual-Pläne. Alle 148 Raw-Requestframes und acht Raw-Pläne
exakt mit gespeicherten Records abgeglichen; je Request tatsächliche vollständige
Identität/Counters/Chronologie und unabhängig guardattestierte eigene DB-ID.
Zehn vollständige 400-Row-Aufnahmen über beide Läufe gleich, tatsächliche
SourceDELETE-/Querymutationsnegative mit exakt 51003, Restore und Setupidempotenz.
DB-MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad)/PREVIEW_FEATURES 0/0 erhalten; eigenes YELLOW-Profil, kein Previeweffekt.

Die tatsächlichen öffentlichen Vollprofile liefern WARN_OPTIONAL_EVIDENCE_SKIPPED:
fehlende Wait-/Warning-/vollständige Worker-/Spillbeobachtung bleibt offen;
keine künstliche Null oder vollständige Performancefreigabe. Zeitquantisierung
und Elapsed 0-WARNs der Messfolge bleiben sichtbar. Weitere 2025-Builds enden
vor Setup mit SKIP_CONFIGURATION und sind nicht Teil dieser lokalen Qualifikation.

Der zusätzliche tatsächliche Fault erfolgte nach PASS-Setup und vor Quellen-
aufnahme. Eindeutiger AFTER_PASS_SETUP_BEFORE_SOURCE-Checkpoint, exakt sechs
Publicphasen und unabhängiger Cleanup bestanden; Publicstatus bleibt korrekt
FAIL_EXECUTION, ausschließlich der erwartete Recoverytest ist bestanden.
Früher Interrupt ohne PASS-Setup kann diese Gegenprobe nicht qualifizieren.

## Review, Gegenfälle, Cleanup und Aufwand

Enger unabhängiger Quellenabschluss vor Admission für drei konkrete P2:
Pollausnahmen müssen UNKNOWN setzen, der Setupfault muss exakt attestiert sein,
und auch Versions-SKIPs müssen dieselbe Parent-Cleanupdeadline teilen.
15 betroffene Controller-, 24 Plan-, 18 Mess-/Transportfälle PASS, darunter
Collector-/Pollausnahmen, Bool-Endstatus, früher Interrupt, verzögerte
SKIP-Abwesenheit sowie manipulierte Rows/XML (Extensible Markup Language; Format zur strukturierten Darstellung von Daten)/Identitäts-/Counter-/Chunkdaten.
Reviewer ohne Tests oder Runtime; keine Reviewkette oder Performanceabnahme.
Frameworkvalidator und 11 betroffene bestehende Runnerfälle PASS.

20 ausgewählte SQL-/Controller-/APIquellen tatsächlich bytegebunden und vor
Promotion archiviert. Privater Lifecycleadapter bestätigt zusätzlich die volle
CID-/Name-/Image-/Owner-/Ressourcenbindung; Native Clientenden bekannt.
Markergebundener SQL-Cleanup und unabhängige neue DB-/CID-/Namensabwesenheit
aller sieben eigenen Container innerhalb derselben 60-Sekunden-Deadline:

| Slot | Native Calls | Öffentlicher Status | Cleanup Sekunden |
|---|---|---|---|
| 2019-skip-1 | 5 | SKIP | 11.5463 |
| 2019-skip-2 | 5 | SKIP | 10.8242 |
| 2022-skip-1 | 5 | SKIP | 12.6353 |
| 2022-skip-2 | 5 | SKIP | 12.5027 |
| 2025-profile-1 | 96 | WARN | 12.9793 |
| 2025-profile-2 | 96 | WARN | 13.0816 |
| 2025-fault | 7 | FAIL | 13.0945 |

Der neue CI-Consumer benutzt die unveränderten öffentlichen Ausführungsziele
und den öffentlichen Prozesspfad: zweimal Profil je tatsächlicher Version,
danach nur bei vollständig qualifiziertem 2025-Profil der erwartete Setupfault.
Alle Pflicht-SKIPs/WARNs bleiben im Lauf sichtbar. Neue Source-/Test-/Runnerpfade
stehen in beiden Workflowpathsets; mutierende CI-Cancellation bleibt false.
CI (Continuous Integration; automatisierte Integrationsprüfungen) ergänzt den tatsächlich anderen Consumer-/Shim-/Plattformpfad; keine lokale
Wiederholung bereits abgeschlossener privater grüner Messschnitte. Statische
Gegenfälle werden nur bei geänderten Inputs wiederholt. Aktuelle Head-/Main-Gates
bleiben Pflicht; tatsächliche Auswahl wird aus den betroffenen Pfaden gebunden.
Größere Runtime-/Reviewbudgets werden nicht aus unbekannten Modell-/Tokenkosten
abgeleitet; Verbrauch unbekannt. Keine Vollsuite-Lokaldoppelprüfung.

CI-C1 am Head ba65cf386e028cb2e8e2b5efcc91142b146d1726 bleibt FAIL:
Run 38199574328 verweigert die RES-008-Optionen `-C`/`-l` im bisherigen
Containerproxy auf 2019/2022. Die unabhängige Containerentfernung besteht;
die öffentliche SQL-Abwesenheit dieses CI-Aufrufs ist damit nicht qualifiziert.
Die vorherigen lokalen C1-Nachweise bleiben separat gebunden. CI-C2 ergänzt
ausschließlich einen eigenen dünnen RES-008-Adapter für `-C`/`-l`/`-y` und
wählt diesen im neuen Runner. Gemeinsame API-/Proxydateien und alle öffentlichen
SQL-/Controllerbytes bleiben unverändert. Drei neue synthetische Adaptertests
prüfen sämtliche tatsächlich erzeugten Phasenargumente, Ablehnung von Passwort-/
freien SQL-Optionen sowie Native-ENV-/stdin-/Exitcodeweitergabe. Der geänderte
CI-Eingang benötigt neue aktuelle Head-/Main-Gates; kein unveränderter Retry.

Private Rawdaten, Session-/Connection-/Containerwerte und vollständige XMLs
bleiben ignoriert. Öffentlicher Aufruf zeigt Counts/Status und persistiert keine
Rohdiagnosen; gültige Ergebnisse stehen im Speicher zur kontrollierten weiteren
Auswertung bereit. Keine Cloud-/Modell-/ONNX-/rote Hostwirkung, keine anderen
Repositories verändert. Aktuelle Head-/Main-Gates, PR/Integration, ganze
Treeübernahme, FF-Sync und eigener Branchcleanup folgen vor Abschluss.

## Offene Freigabegates und Folgearbeit

RES-008 bleibt PROPOSED: vollständige öffentliche FWK-011-Aggregation und
maschinenunabhängige Interpretation/Ergebnisfreigabe, vollständige Worker-/
Wait-/Spill-/TempDBbeobachtung, größere Profile, reale Modellqualität und
TP-PERF-/Modul-/Gesamtabnahme offen. Kein 32-Demo-/372-Run-Gesamtkatalogclaim.
Nächster zulässiger lokaler Schritt nach vollständig abgeschlossener Integration:
begrenzte öffentliche RES-008-Aggregation/Ergebnisinterpretation aus den schon
vollständig validierten Records, ohne erneute unveränderte SQL-Läufe.
