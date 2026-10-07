# Nächste Entwicklungswellen

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-10-07 |
| Ausgangsstand | Produktive Runtimeevidenz bis Pull Request 42; begrenzte DGN-007-Kontrollcaptures bis Pull Request 62 und prospektiver Prüfvertrag aus Pull Request 63 und skalarer Transport aus Pull Request 64 sowie begrenzter SQL-Producer aus Pull Request 65; Detailstand in `CURRENT_EXECUTION_STATUS.md` |
| Bezug | [CURRENT_EXECUTION_STATUS.md](CURRENT_EXECUTION_STATUS.md), `.ai/BACKLOG.md`, `MASTER_IMPLEMENTATION_PLAN.md` |
| Zweck | priorisierte, kleine Folgepakete; keine Aussage, dass die beschriebenen Inhalte bereits umgesetzt sind |

## 1. Planungsgrundlagen

- `QRY-004`, `DGN-003`, `DGN-005`, `OPT-017` und alle neun Demos aus `W-COV-001` besitzen aktuelle Matrixnachweise aus GitHub Actions.
- `WARN_EMPIRICAL_VARIANCE` ist nur dort als Freigabeausgang zulässig, wo der Demo-Vertrag die empirische Abweichung ausdrücklich beschreibt und alle invarianten Ergebnis-, Sicherheits- und Cleanup-Verträge erfüllt sind.
- Die Curriculum-Analyse verlangt kein neues Hauptmodul. Neue Arbeit erweitert deshalb nur bestehende Lernziele und Demo-IDs.
- Jede Welle ist ein eigenständiger, kleiner Pull Request mit klarer Runtime-, Quellen- und Safety-Grenze. Öffentliche Herstellerdokumentation wird erst nach dem Source-Register-Delta-Review zu Lehrinhalt.

## 2. Priorisierte Wellen

| Reihenfolge | Welle | Ziel und abgegrenzter Umfang | Akzeptanzkriterium |
|---:|---|---|---|
| 1 | `LABSCN-005/DGN-007` | Capstone erst als eigenen Schnitt planen, nachdem Query-Store-/XE-Pilot und `CON-006` praktisch wiederverwendbare Evidenz- und Mehrsession-Verträge liefern. | Incident, Alternativhypothesen, Zeitfenster, Reset, Quellen und Teilnehmerübergabe sind vollständig; keine versteckte Lösung in Teilnehmerartefakten. |
| 2 | nächster `LABSCN-005`-Einzelslice | Nur einen Kandidaten mit eigenem Quellen-, Safety- und Detailreview auswählen; keine pauschale Infrastrukturwelle. | Lernmehrwert, Providerbedarf, Reset, Cleanup und versionsgebundene Aussage sind vor Implementierung eindeutig. |
| 3 | weitere `LABINT-004`-Matrix | Nur für einen neu freigegebenen gelben Szenarioslice aktivieren. | Matrix und Cleanup prüfen ausschließlich die neue freigegebene Aussage. |

## 2.1 Umsetzungsstand der Wellen

| Welle | Status | Evidenzgrenze |
|---|---|---|
| `TSK-002` | `DECIDED_PLANNING` | Detailreview [`LABSCN_005_DGN_007_DETAIL_REVIEW.md`](LABSCN_005_DGN_007_DETAIL_REVIEW.md) entscheidet den Capstone-Planungsschnitt; daraus folgt kein Implementierungsauftrag und kein Runtimestatus. |
|---|---|---|
| `W-STA-001` | `VALIDATED` | Lauf 33222989681 belegt die vollständige Matrix einschließlich der erwarteten empirischen Warnungen. |
| `W-DGN-001` | `VALIDATED` | Lauf 33222989682 belegt alle zwölf Query-Store-/XE-Pilotläufe mit `PASS/OK`. |
| `W-SCN-001` | `VALIDATED` | Project Adapter `0.1` und vollständiger SQL-Server-2025-Lifecycle sind auf Docker und Podman praktisch validiert. |
| `W-ADV-017` | `VALIDATED` | Lauf 33447840232 belegt Actual DOP, Exchange, positive Threadarbeit und Cleanup auf allen drei Zielversionen. |
| `W-SQL25-001` | `VALIDATED` | Quellen-, Claim- und Entscheidungsgrundlage ist abgeschlossen; daraus folgt keine neue Featuredemo. |
| `W-PRS-001` | `VALIDATED` | 102 SlideKeys, drei Custom Shows, Build 41/66/102 und vollständige Master-/Profilrender liegen vor. |
| `W-COV-001` | `VALIDATED` | Lauf 33222989644 belegt alle neun Demos; `CON-009` endet auch auf SQL Server 2019 zweimal mit `PASS/OK`. |
| `W2-002` | `VALIDATED` | Neun `W2-A`-Altquellen sind nicht ausführbar; vier aktive Ersatzdemos und alle künftigen Neuaufbauten sind an synthetische, neutrale Datenverträge gebunden. |
| `ADV-009` | `VALIDATED` | Runtimewarnung, Masterdeck, Notes, Hashbindung, vollständiger Render und Privacy-Freigabe sind synchron. |
| `ADV-010` | `VALIDATED` | Fachliche, didaktische und technische Endabnahme grenzt verbleibende Designs ausdrücklich als Folgearbeit ab. |
| `LABSCN-002` | `VALIDATED` | 22 produktive Demos sind vollständig mit Lifecycle, Provider, Ressourcen, Versionen, Reset und Evidenz inventarisiert. |
| `LABSCN-004` | `VALIDATED` | Der generische Benutzerablauf für Auswahl, Start, Übergabe, Reset und Remove ist dokumentiert und statisch geprüft. |
| `INF-002`/`INF-003` | `VALIDATED` | Docker und Podman melden `RESOURCE_OK`; der kompakte SQL-Server-2025-Lifecycle und Recovery-Pfad sind dokumentiert. |
| `LABINT-003` | `VALIDATED` | Provider-Parität ist für `QRY-001`, `CON-004` und `DGN-005` praktisch belegt. |
| `LABSCN-005/DGN-005` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `d5143f2a-…` und Podman-Run `82791985-…` führten die Teilnehmerphasen aus und endeten nach Start und Reset vollständig als `REMOVED`. |
| `LABSCN-005/CON-006` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `76cff6ed-…` und Podman-Run `6d2d0a51-…` belegten Opfer 1205, Survivor, Deadlock-Graph, geordnete Gegenprobe, Reset und `REMOVED`. |
| `LABSCN-005/DGN-007` | `IMPLEMENTED_STATIC_SLICE_B` | Der nicht-promotende statische Teilnehmerfluss bestand am 2026-09-19 auf SQL Server 2025/Linux mit Docker (`ea802c20-…`) und Podman (`fba84720-…`): Adapter-Preflight, Install/Validate, alle sechs Teilnehmerstufen, Cleanup und Lab-Remove (`PASS`/`REMOVED`). Kontrollierte Negativtests auf Docker mit SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`) ergaben kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, im Lab-Core `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und `REMOVED`. Das ist keine 2019/2022-Fachunterstützung und keine Promotion, sondern ausschließlich der erwartete 2025-only-Skip-/Cleanup-Nachweis. Weiterhin keine `READY_FOR_USER`-Übergabe, keine Szenariopromotion und kein Nachweis für `scenario.json`, Manifest, Inventar oder vollständige Lifecycle-/Versionsmatrix. |
| `LABINT-004/CON-006` | `VALIDATED` | Die vollständige freigegebene Matrix SQL Server 2025 × Docker/Podman ist praktisch belegt und prüft ausschließlich den neuen gelben Slice. |
| `DGN-007_DATA_MODEL` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; unabhängiger Datenbankabbau und eigene Container entfernt. [Nachweis](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md). Der Datenmodell-Scope bleibt begrenzt und unverändert als Default. |
| `DGN-007_QUERY_STORE_WINDOWS` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; zwei disjunkte Katalogintervalle, gleiche Parameterlast, je vier Suchausführungen und unabhängiger Cleanup. [Nachweis](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md). Runner und CI prüfen diesen Scope getrennt; kein Incident- oder Regressionsnachweis. |
| `DGN-007_PROFILE_COMPARISON` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden gewichtete T0/T1-Metrikvergleiche auf allen drei Versionen je zweimal, einschließlich unabhängigem Cleanup. [Nachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md). Ohne Richtungsgate oder Incidentpromotion. |
| `DGN-007_CONTROL_AB` / `BA` / `AA` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden alle drei neutralen Kontrollfolgen auf jeder Version je zweimal; vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Abbau aller drei eigenen Instanzen. Tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Variation im [Nachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md). Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation; keine Incidentfreigabe. |
| prospektiver `DGN-007`-Prüfvertrag | `STATIC_PROSPECTIVE_CONTRACT` | `DEC-068`, reine Record-/Separationsprüfung, 34 synthetische Tests und Quellenvalidator lokal PASS. [Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md). Keine SQL-Runtime-Abnahme; Collector und frische Bestätigungsläufe bleiben offen. |
| skalarer `DGN-007`-Collector-Transport | `STATIC_COLLECTOR_TRANSPORT` | Reiner JSON-Decoder mit genauer Decimal-/100-ns-Darstellung, 19 Transporttests und beide Validatoren lokal PASS; 34 Prospektivtests bleiben grün. [Transportgrenze](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md). Keine SQL-Erfassung oder vollständigen RunRecords; fehlende Request-Ergebniszeilen bleiben `NOT_CAPTURED`/`None`. |

## 3. SQL-Server-2025-Delta: abgeschlossene Entscheidungen

Der abgeschlossene Delta-Review dokumentiert folgende Zuordnung:

| Herstellerfunktion | bestehende Anknüpfung | Entscheidung |
|---|---|---|
| Cardinality Estimation Feedback für Ausdrücke | `OPT-006` | `ADOPT`; keine neue Demo, spätere Evidenz im bestehenden Schnitt |
| Optimiertes `sp_executesql` | `QRY-004`, `OPT-007` | `DEFER`; eine spätere Concurrent-Compile-Detailanalyse ist nach der nun belegten `QRY-004`-Freigabe zulässig |
| zeitgebundene Extended-Events-Sessions | `DGN-005` | `ADOPT`; optionaler Engine-17-Schutzpfad |
| TempDB Space Resource Governance | `CON-009`, `RES-004` | `DEFER`; roter Safety- und Infrastrukturvertrag erforderlich |
| Ordered nonclustered Columnstore | `IDX-010` | `DEFER`; gelbes Detaildesign erforderlich |
| Query Store auf lesbaren Secondary Replicas | kein unmittelbarer Slice | `DEFER`; Preview- und Mehrinstanzabhängigkeit |

Vector- und KI-Funktionen liegen außerhalb des derzeitigen Curriculumzuschnitts. Der Review verwendet als Ausgangspunkt die offiziellen Microsoft-Dokumentationen zu [SQL Server 2025](https://learn.microsoft.com/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17), [Extended Events](https://learn.microsoft.com/sql/relational-databases/extended-events/sql-server-extended-events-sessions?view=sql-server-ver17) und [Query Store auf Secondary Replicas](https://learn.microsoft.com/sql/relational-databases/performance/query-store-for-secondary-replicas?view=sql-server-ver17); vor einer Inhaltsübernahme muss der Projekt-Quellenregisterprozess durchlaufen werden.

## 4. Abhängigkeits- und Stop-Regeln

```text
LABSCN-002 + LABSCN-004 -> DGN-005 + CON-006 validiert -> weiterer Kandidat nur nach Einzelreview
Query Store/XE-Pilot + Mehrsession-Vertrag validiert -> DGN-007 als eigener Folgeschnitt zulässig
```

- Kein `DGN-007` ohne validierten Query-Store-/XE-Pilot.
- Keine rote oder gelbe Lastdemo ohne bestehende Safety-Gates, Wegwerfinfrastruktur, Kill-Switch und Laufzeitbudget.
- Keine Änderung an `SQL_Server_Lab` ohne dokumentierte Fähigkeitslücke und ausdrückliche Freigabe.
- Keine Statusanhebung aus statischem Testbestand allein; Runtime-Status benötigt einen konkreten Laufnachweis.

## 5. Nächster belegpflichtiger Schritt

Der eigenständige automatisierte Datenmodellvertrag ist auf Docker für alle
drei Zielversionen jeweils zweimal praktisch belegt. Seine Prüfungen enthalten
keine Incident-, Query-Store-, XE-, Hypothesen-, Mitigations- oder interaktive
Teilnehmerabnahme. Der anschließend getrennt implementierte
`DGN-007_QUERY_STORE_WINDOWS`-Vertrag ist auf allen drei Versionen je zweimal
praktisch belegt. Er prüft ausschließlich disjunkte T0/T1-Capture-Fenster mit
gleicher Parameterlast. Der getrennte neutrale `DGN-007_PROFILE_COMPARISON`-
Vertrag bestand am 2026-10-07 ebenfalls je zweimal auf allen drei Versionen:
gewichtete Mittelwerte, T1-T0-Deltas und tatsächlich ausgeführte Plananzahl;
kein Richtungs- oder Mindestplangate. Die NULL-Ratio bei Null-Baseline wurde
gesondert mit numerischer Fixture geprüft. Lokale Matrix,
skalare Messwerte und unabhängiger Cleanup stehen im
[Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md).
Die zusätzlichen neutralen AB-/BA-/AA-Kontrollcaptures sind auf jeder Version
je zweimal praktisch belegt. Sie prüfen denselben Vierermix in fester tatsächlicher
Reihenfolge und unterscheiden ausgeführte Planmengen über beide Fenster.
AB/BA zeigten zwei aktive Plan-IDs/Hashes, AA dieselbe Plan-ID in beiden Fenstern.
Die vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Cleanup
steht im [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md).
Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation;
positives Vorzeichen allein trägt deshalb keine versionsübergreifende
Separation. Diese Captures sind explorative Voraussetzungen, keine
prospektiven Bestätigungsläufe einer Incidentregel. Der getrennte reine
[Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
legt diese Regel jetzt vorab fest (`DEC-068`): gewichtete Statement-Duration
als primäre zeitbezogene Metrik, alle vier B-A-Kontraste unter AB/BA strikt
positiv und oberhalb beider absoluter AA-Drifts; zusätzlich global entweder
vier unterschiedliche aktive Hashmengen oder einheitlich gerichtete Reads-
Kontraste oberhalb beider absoluter AA-Reads-Drifts. 34 synthetische Tests und
der Quellenvalidator bestanden lokal. Der Status ist ausschließlich
`STATIC_PROSPECTIVE_CONTRACT`, keine Runtime-Abnahme. Der getrennte
[Transport-Vorschnitt](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: 19 tatsächliche
Decoderfixtures, beide Validatoren und die 34 Prospektivtests lokal PASS.
Decimal-Text und UTC-100-ns-Integer bleiben präzise. Fehlende Request-
Ergebniszeilen bleiben `NOT_CAPTURED`/`None`; deklarierte `MEASURED`-Werte
attestieren keine Herkunft. Der Body enthält keine erfundenen Phasen-,
Cleanup-, Lifecycle- oder Ressourcenangaben. Der getrennte SQL-Producer
speichert jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
die vollständige skalare Projektion vor Cleanup bereit. Seine neue lokale
2019/150-, 2022/160- und 2025/170-Matrix bestand je zweimal AB/BA/AA,
insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder und unabhängigem
Cleanup. Alle drei eigenen Container sind unabhängig abwesend bestätigt.
Der [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md)
bindet konkrete Versionen, Images und Quellenfreeze und hält frühere
Fehlversuche getrennt fest. 156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und
einen Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
[Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
ist abgeschlossen: 14 Workflows und alle 22 Jobs SUCCESS am Head
`20a867e…` gegen Base `94ed561b…`, Integration `df78cb0…`.
Je Version bestanden zwölf Lifecycles mit sechs tatsächlichen Decoder-
Captures und unabhängigem Cleanup; Linux führte alle 156 Methoden ohne
SKIP aus. Der Squash `da7b0eb…`, vollständige Übernahme, synchronisiertes
Main und lokale/remote Bereinigung des eigenen Branches sind bestätigt.
Die zwei historischen CI-Fehler bleiben getrennt dokumentiert, ohne
behauptete Ursache oder Behebung. SQL-Prädikate und Budgets bleiben gleich.

Die getrennte Main-Push-CI am Squash `da7b0eb…` ist danach vollständig
beendet: 12/13 Workflows und 47/48 Jobs SUCCESS, ausschließlich SQL Server
2022 im zweiten BA-Lifecycle `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`.
Alle zehn begonnenen 2022-Abwesenheitsprüfungen und der ownergebundene
Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
2019/2025 bestanden je zwölf Lifecycles und sechs Captures. Der neue Fehler
ist von der erfolgreichen PR65-Integration und den zwei historischen
CI-Fehlern getrennt zu bewerten; seine skalare Ursache ist offen.

Die private skalare Probe ist als begrenzte Gegenprobe abgeschlossen: auf
neuer eigener 2022-Instanz mit CI-Imagebindung und tatsächlicher Version
`16.0.4295.3` bestanden Datenmodell, Fenster, Profil, AB und BA jeweils zweimal,
insgesamt zehn Lifecycles und vier Decoder-Captures. Zehn unabhängige
Datenbankabwesenheitsprüfungen, fünf Gruppen-Leerheitsprüfungen, Quellenfreeze
mit 21 Dateien und unabhängiger own-CID-/Namensabbau bestanden. G13 wurde
nicht reproduziert; es liegen keine tatsächlichen verletzten Grenzabstände vor.
Zwei frühere private synthetische Vorchecks scheiterten vor jedem Lifecycle;
Defekte und unabhängiger Cleanup bleiben im Producernachweis getrennt.
Kein Main-, Incident- oder Behebungsnachweis; AA wurde nicht ausgeführt.

Nächster belegpflichtiger Schnitt ist ein eigener kanonischer Diagnosebericht,
keine identische Wiederholung: maximal acht gespeicherte verletzte
Profilgruppen, exakte UTC-Ticks und Grenzabstände ausschließlich im bereits
ausgelösten G13-Fehlerzweig. Der Runner bindet diese Metadaten an tatsächliches
stderr, die eindeutige fehlgeschlagene Kontroll-Evidenzphase und den
unveränderten Guard-/Summary-Abschluss; Ausgabe erst nach Cleanup.
Keine zusätzliche Query-Store-Sicht, keine Prädikat-, Last-, Zeitbudget- oder
Outcomeänderung. Der Reporter ist inzwischen lokal implementiert und
unabhängig geprüft: exakt validiertes Entfernen ergibt den ganzen bisherigen
SQL35, Quellenbindung ist erneuert, 43 Runner- und 37 Producer-/Reporter-
Methoden (ein Linux-spezifischer Windows-SKIP) sowie sieben Validatoren
bestanden. Acht tatsächliche temporäre SQL-Branchfixtures auf einer neuen
eigenen 2022-Instanz bestanden, einschließlich Ein-Tick-Abständen, gleicher
Requestgrenzen, UTC-Offset, acht Gruppen und ausdrücklichem Overflow.
Unveränderter Freeze und eigener Containerabbau sind unabhängig bestätigt.
Der ganze Report bleibt atomar innerhalb 24 Diagnosezeilen. Als nächster
Schritt wurde die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, vollständig
beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1 und 2022 BA1
scheiterten an G13. First−Start beträgt −0,4263 beziehungsweise −0,951 ms;
Last liegt jeweils innerhalb der oberen Grenze. 2025 bestand zwölf Lifecycles
und sechs Captures. Alle 32 ersten Datenbankabwesenheitsprüfungen und neun
SQL-Containerabbauten bestanden; Linux 163 Methoden PASS. Der PR bleibt
unmerged und ohne CI-Freigabe. Der Reporter schließt die Messlücke, belegt
aber keine Ursache oder Behebung. Das beobachtete Millisekundenraster ist
keine zugesagte QS-Auflösung oder Toleranz.

Die einmalige private Originalmaterialisierungsprobe auf neuer eigener 2022-
Instanz reproduzierte G13 bereits in AB1: First−Start −0,2609 ms. Die verletzte
Gruppe enthält in Captureversuch 1 und im getrennten Live-SELECT jeweils genau
eine positive Raw-Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen.
Ein Zero-Extremum erklärt diesen lokalen Fehler nicht. Elf temporäre SQL-
Fixtures PASS; sechs Präfix-Lifecycles PASS, AB1 FAIL mit sofortigem Stop,
keine AB2/BA/AA oder erfolgreiche AB-Capture. Sieben erste DB-Abwesenheits-
prüfungen, vier Gruppen-Leerheitsprüfungen und eigener Containerabbau PASS;
CID/Name unabhängig abwesend, Freeze mit 27 Dateien unverändert. Zusätzliche
Projektion/DML sind Beobachterinstrumentierung, keine identische kanonische
Timingprüfung und kein historischer CI-Ursachenbeweis.

Der quellenbasierte [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md)
liegt jetzt als `PROPOSED` vor. Er trennt exakten zeitlichen Einschluss und
kontrollierte Kollektivzuordnung. Der ausgearbeitete Kandidat benötigt eine
belegte vollständige Familienbasis B, T0-Capture vor T1, Bilanz B→B+4→B+8
über alle Familien-/Intervallgruppen sowie vertrauenswürdig attestierten
Ausführungsumfang. Die vier Vorabrequests laufen vor der expliziten QS-
Konfiguration; frische Datenbank und beobachtete Nullcounts beweisen keine
QS-OFF-Basis oder fehlende nachlaufende Statistik. Konkrete Baseline-,
Intervallaktivierungs- und Herkunftsbelege bleiben offen. Die Vergleichbarkeit
von QS-Endzeiten und SYSUTC-Requestklammer auf exakten 100-ns-Grenzen bleibt
ungeklärt. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
prüft die vorab festgehaltenen synthetischen Gegenbeispiele und bedingte
Konsistenz; keine Prozesse im Modell, SQL-/v1-Änderung oder Runtimeattestation.
Die Prüfung ersetzt insbesondere keine tatsächliche Herkunft trotz passender
Counts. Die [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
ist abgeschlossen: Procedure-Queries unter AUTO werden erfasst; dokumentierte
asynchrone Persistenz belegt keine verzögerte Publikation. Der tatsächliche
Pfad prüft eigene Calls und Ergebnisse, attestiert aber weder vollständigen
Basisabschluss noch interne Aktivierung, kontinuierlichen Zustand oder
geschlossene Coordinatorherkunft. Der konkrete
[Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
liegt als PROPOSED vor: acht Acquisitionstages, vollständige Raw-/Gruppen-/
Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze, überprüfte
Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Observerkosten.
Bounds und deren Durchführbarkeit sind noch nicht runtimevalidiert.
Punktweise QSStates beweisen keine Kontinuität; Sättigung bleibt bedingt.
Die äußere Pipegrenze begrenzt heute nicht das Vorpuffern im Proxy.
Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: injektive kohärente
Zählung aus einem unabhängig geschlossenen tatsächlichen Calluniversum kann
Callerfassung tragen; vollständige keyweise Stageledger zusätzlich kollektive
QS-Buckets. Counts beweisen kein kontinuierliches RW/ALL; dieses gesonderte
konservative Methodengate bleibt vorgeschlagen. Heutige Live-Dateizugriffe
und Zielnamen binden keinen vollständigen unveränderlichen Ausführungspfad.
Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
implementiert die synthetischen Gegenproben mit getrennten Teilclaims.
Kein Token ist eine reale QS-Einzelidentität. Das konkrete
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
Gate-Matrix mit Acquisition-/Count- und konservativem Floatkandidaten, tatsächlicher
Freeze-/Actor-/CID-/Host-/Zugangsgrenze und Kostenplan innerhalb 145/180/60 Sekunden
und 4 CPU/8 GiB. Alle Methodengates bleiben offen; Einzelmaxima sind keine
gemeinsame Machbarkeitsevidenz. Nächster ausführbarer kleiner Schnitt ist ein
Offline-Bundle-/Importpfad-Verifier samt Manipulationsfixtures, ohne SQL oder
Launcher. Statischer Kandidaten-PASS attestiert keine verwendeten Runtimebytes.
Normative Methoden-/Grenzänderungen brauchen eine ausdrückliche neue Entscheidung.
Keine implizite OFF-/CLEAR-/Laständerung. Erst eine tragfähige explizite
Methodenentscheidung erlaubt gemeinsam versionierte
SQL-/Transport-/Record-/Evaluator-/Coordinator-Umsetzung. Bestehende Guards,
Fehlerklassifikation, DEC-068, Last und Budgets bleiben erhalten; keine
pauschale 1-ms-Toleranz, Abrundung oder Wiederholen bis grün. Die alternative
Methode ist weder entschieden noch implementiert oder abgenommen. Der frühere Acht-Fixture-Vorcheck enthält keine vollständige
Lifecycle-/Versionsmatrix oder Reproduktion des Main-G13.

Die interne verlustfreie Capture-Rückgabe ist lokal vorbereitet und geprüft;
Veröffentlichung und Integration sind bis zur G13-Klärung zurückgestellt.
Danach folgt der geplante API-Schnitt:
Body, tatsächlich geprüfte Phasen und erfolgreiche erste unabhängige
Datenbankabwesenheit über denselben Harness erhalten. Rückgabe erfolgt
nur nach erfolgreichem Lifecycle und Cleanup; erfolgreiche Recovery
ändert einen ersten Abwesenheitsfehler nicht in PASS. Der direkte Helper
akzeptiert ausschließlich unveränderte bekannte Kontrollverträge.
Counts-/CLI-Ausgabe und Fehlerprioritäten bleiben erhalten; keine
RunRecords, Incidentbewertung oder `runtime_attested=True`.
Danach muss der Collector-Coordinator den integrierten Freeze und Quellen,
Ressourcen, präzise Budgets und tatsächliche serielle Reihenfolge attestieren
und Cleanup unabhängig bestätigen. Die interne Capture-Rückgabe allein
ist kein vollständiger RunRecord oder Coordinator-Nachweis.
Erst danach folgen frische Bestätigungsläufe unter
der festgelegten Regel. CPU bleibt ergänzend, ohne Fallback. Keine
nachträglich ausgewählte Ratio oder statistische Signifikanzbehauptung;
fehlende tragfähige Evidenz bleibt `SKIP_EVIDENCE_MISSING`.
Plan- beziehungsweise klar unterscheidbare Runtimeprofile sind zusätzlich
gegen den Designvertrag zu begründen; Planunterschiede ersetzen kein Symptom
und isolieren keine Kompilierungsursache. Unterschiedliche Parameterlast
allein ist kein Regressionsnachweis. Als begrenzte Voraussetzung verwendet der
ältere Teilnehmerpfad jetzt `sys.databases.compatibility_level` mit NULL-Guard
und prüft vor der Evidenzausgabe den bestehenden 2025-/170-Vertrag; auch die
Adaptervalidierung lehnt fehlende Compatibility-Werte ab. Die
Beobachtungsbedingung muss weiterhin auf den Designvertrag (Plan- oder
Laufzeitprofilevidenz) abgeglichen werden. Der Compatibility-Vorfix belegt
weder den Incident noch eine vollständige Teilnehmerabnahme.
Für die ältere Beobachtungsbedingung sind ausschließlich erfolgreich
ausgeführte T0/T1-Pläne und ihre validierten Profile maßgeblich; historische
oder ungenutzte Planzeilen und bloße Counts 3/5 genügen nicht. Ihr bisheriger
unterschiedlicher Lastmix ist zuerst gegen den gleichen Parameterlastvertrag
abzugleichen. Live-Mittelwerte dürfen keine nachträglichen Zusatzrequests
enthalten; Plan-/Profilunterscheidbarkeit und Verschlechterung sind getrennt
zu begründen. Die jetzt gemessenen unterschiedlichen Richtungen für CPU und
Reads erfüllen allein keine Incidentfreigabe.
Danach folgen die vollständige Capstone-Matrix und die
interaktive Docker-/Podman-Abnahme; deren offene Gates bleiben bestehen.

Der Capstone-Planungsschnitt ist mit `TSK-002` entschieden
(`DECIDED_PLANNING`, Detailreview
[`LABSCN_005_DGN_007_DETAIL_REVIEW.md`](LABSCN_005_DGN_007_DETAIL_REVIEW.md)).
Implementierungsschnitt A (Project Adapter `0.1` mit Datenaufbau,
Query-Store-Zeitfenstern und Incident-Erzeugung ohne Mitigationsmarker) besitzt
seit dem 2026-09-14 die praktische Docker-/Podman-Lifecycle-Abnahme: Docker-Run
`9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run
`e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`,
Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die
verbleibende Gesamtabnahme umfasst den vollständigen Lifecycle dieser
Schnitt-B-Fassung und die begrenzte Provider-/Versionsmatrix. Der manuelle Teilnehmerablauf sowie
die Evidenz-, Hypothesen- und Mitigationsartefakte sind statisch geprüft.
Frische SQL-Server-2025/Linux-Runs bestanden am 2026-09-19 auf Docker
(`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman
(`fba84720-5f0b-4537-bc98-75bbad37a85b`) Adapter-Install/Validate, alle sechs
Demo-Stufen, Teilnehmer- und Adapter-Cleanup sowie Lab-Remove. Das belegt die
aktuelle Linux-Providerparität, ist aber keine Szenariopromotion und keine
vollständige Lifecycle-/Versionsmatrix. Ressourcen-, Netzwerk-, Hyper-V- und
gemischte Topologien bleiben ohne konkreten fachlichen Bedarf gestoppt.
