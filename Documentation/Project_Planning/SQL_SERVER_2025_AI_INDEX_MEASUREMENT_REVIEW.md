# DGN-010 – begrenzte private Reader-Zugriffspfadmessung

Stand: 2026-10-12. TSK-011/CUR-021, DGN-010 weiterhin PROPOSED.
Basis 27ef0a118fb25a8ad00353ebd347fb1ad258db4c; private empirische Teilqualifikation, keine öffentliche
FWK-/Versions-/TP-PERF- oder Modulabnahme.

## Messfrage und vollständig abgeschlossene Basis

[PR191](https://github.com/gecompat/SQL_PerformanceSchulung/pull/191) ist vollständig
abgeschlossen: Head 4065d6a36dd45e04b261c0164ba153badd975de3, sieben aktuelle Head-Workflows PASS;
Squash 27ef0a118fb25a8ad00353ebd347fb1ad258db4c, fünf Main-Workflows PASS; ganzer Tree ab91c69b0de0d9f8c94fcccf0822518dd14a745d
exakt übernommen, main FF/sauber und eigener lokaler/Remote-Branch entfernt.
Die [vorherigen Ownerpläne](SQL_SERVER_2025_AI_INDEX_PLAN_REVIEW.md) werden nicht
unverändert wiederholt. Dieser Schnitt untersucht die tatsächlich erzwungenen
PK- und Candidate-Zugriffspfade derselben unveränderten 1000-Row-Quelle.

Beide eigenen Indizes bleiben während aller Warmups und AB-/BA-/AA-Fenster vorhanden.
Das ist ein Vergleich zweier fester Zugriffspfade, kein Vergleich Index-abwesend/
Index-vorhanden und kein Nettonutzen einschließlich Build, DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) oder Rückbau.
Die feste SELECT-Struktur enthält ausschließlich INDEX(DGN010_OwnPK) oder
INDEX(DGN010_OwnCandidate), gebundene int-Werte 101/110, ORDER BY Id und MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) 1.
Ein WITHOUT LOGIN Reader mit CONNECT und ausschließlich SourceRows-SELECT führt
die Messqueries tatsächlich aus. Zwei neue repräsentative Actual-Pläne je Profil
werden als Owner aufgenommen; diese qualifizieren keine Readerpläne.

## Vorab festgelegte Population und Messgrenzen

Je Profil fünf separate Warmuprequests pro Pfad, anschließend drei serielle
AB-/BA-/AA-Blöcke mit zwei Fenstern pro Reihenfolge: 18 Messfenster à 100 Queries.
AB/BA liefern sechs Samples pro Pfad. Die drei AA-Paare bleiben getrennt; Warmups
werden ausgeschlossen. Zehn Warmupqueries plus 1800 Messqueries ergeben 1810
vollständige Queryoracles mit je zehn Rows, also 18100 Rowkontrollen je Profil.
Eine zusätzliche positive Einquerykontrolle und eine tatsächliche negative
Einquerykontrolle sind getrennt. Keine nachträgliche Stichprobenauswahl.

Jedes Fenster besitzt eine vollständig gebundene eigene Session-/Request-/Startzeit-/
Connection-/DB-Identität. CPU (Central Processing Unit; Prozessor)/Reads/LogicalReads/Writes werden vor/nach dem Loop am
selben tatsächlichen Request aufgenommen, inklusive Countergrenzen. UTC-Elapsed
umfasst EXECUTE AS, den gesamten Queryloop, Ergebnisbuffer/Transfers/Deletes und
REVERT. Beide Grenzen sind datetime2(7) desselben SQL-UTC-Takts; der coarse
DMV-Requeststart wird ausschließlich als datetime-Identität verwendet, ohne
Crossclockreihenfolge. CPU-/I/O- und Elapsed-Grenzen sind nicht identisch.

Ergebnisse jedes einzelnen Loops werden vollständig gegen Ordinal, zehn eindeutige
IDs 101–110, Value=Id×3 und alle 100 Payloadbytes geprüft. Native SHA256-Digests
aller vollständigen zehn Rows je Ordinal werden zusätzlich gegen die feste
UTF-16LE-Referenz gebunden. Fehlende Counter/Identitäten/JSON-Felder, bool- oder
Floataliaswerte, Trunkierung, doppelte Felder/Parts und unvollständige Population
führen zu FAIL. Fehlende Werte werden nicht zu Null gemacht.

## Tatsächliche Profile und Gegenproben

Zwei stabile C2-Lifecycles auf jeweils neuem eigenem
Container, SQL 17.0.5005.3/EngineEdition3, cached Image
78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
vier CPU/sechs GiB, eigener Loopbackport. CL170/SIMPLE, 256-/64-MB-Dateilimits,
MAXDOP/PREVIEW_FEATURES beide 0 und unverändert. Normalbudget 300 Sekunden,
anschließend gemeinsame Cleanupdeadline 60 Sekunden. Keine Host-/Cloud-/Modell-/
ONNX-/Previewänderung oder Änderung eines anderen Repositories.

Je Profil elf vollständige Quellen-/Reader-/Indexaufnahmen, zweimal Setup und
tatsächliches DELETE Id1000 → 51003/FAIL_RESULT_CONTRACT → vollständiger Setuprestore.
Negative Querykontrolle mutiert nach Messende Value von Id101 im Ergebnisbuffer
und erreicht ebenfalls exakt 51003/FAIL_RESULT_CONTRACT; Source bleibt unverändert.
Beide eigene Indizes sind in allen aktiven Messphasen vorhanden; abschließender
Candidate-Drop und voller PK-/1000-Row-Sourcecheck bestanden.

22 vollständige Sourceframes/22000 Rows, vier neue tatsächliche Ownerpläne,
58 positive Fensterframes einschließlich zwei separater Kontrollen und vier native
Negativframes sind vollständig an private Rawframes und Recordhashes gebunden.
Je Profil 54 beziehungsweise
54 dokumentierte native Phasencalls;
SQL-Markercleanup und neue unabhängige DB-/Namens-/CID-Abwesenheit bestanden,
Cleanup 12.796/13.068 Sekunden.
Tatsächliches Clientende bekannt, UNKNOWN false; kein weiterer Client nach UNKNOWN.
Eigener Zusatzindex bleibt 1000 Rows/17 used/25 reserved pages, PK (Primary Key; Primärschlüssel) 18/25.

## Tatsächliche AB/BA-Batchwerte

ElapsedUs in Mikrosekunden, CpuMs in Millisekunden; I/O-Werte sind Requestdeltas.
Median, Min/Max und alle sechs Rohzahlen bleiben sichtbar. Kein individuelles
Query-p95/p99, Durchsatz, isolierter Indexgewinn oder statistischer Nachweis.

| Profil | erzwungener Pfad | Metrik | n | Median | Min–Max | alle Samples |
|---|---|---|---:|---:|---|---|
| 1 | PK | CpuMs | 6 | 25.5 | 23–30 | 30, 23, 26, 24, 25, 27 |
| 1 | PK | ElapsedUs | 6 | 28657.5 | 24506–33003 | 33003, 24506, 28685, 28614, 28630, 28752 |
| 1 | PK | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 1 | PK | LogicalReads | 6 | 10996.0 | 10993–11011 | 10995, 10995, 10997, 10993, 11010, 11011 |
| 1 | PK | Writes | 6 | 32.0 | 23–110 | 110, 61, 30, 34, 23, 29 |
| 1 | Candidate | CpuMs | 6 | 23.0 | 21–35 | 24, 22, 21, 21, 33, 35 |
| 1 | Candidate | ElapsedUs | 6 | 26664.0 | 24493–41346 | 28544, 24493, 24784, 24532, 32787, 41346 |
| 1 | Candidate | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 1 | Candidate | LogicalReads | 6 | 10998.0 | 10991–11039 | 11039, 11001, 11030, 10995, 10991, 10994 |
| 1 | Candidate | Writes | 6 | 33.5 | 22–95 | 95, 94, 31, 33, 22, 34 |
| 2 | PK | CpuMs | 6 | 26.5 | 25–32 | 28, 32, 25, 25, 25, 29 |
| 2 | PK | ElapsedUs | 6 | 26673.5 | 24517–32861 | 28793, 32844, 24554, 24551, 24517, 32861 |
| 2 | PK | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 2 | PK | LogicalReads | 6 | 10996.0 | 10993–11011 | 10995, 10995, 10997, 10993, 11010, 11011 |
| 2 | PK | Writes | 6 | 32.0 | 23–110 | 110, 61, 30, 34, 23, 29 |
| 2 | Candidate | CpuMs | 6 | 28.0 | 24–43 | 25, 32, 43, 24, 30, 26 |
| 2 | Candidate | ElapsedUs | 6 | 30682.5 | 24642–45063 | 28780, 32585, 45063, 24642, 33164, 28626 |
| 2 | Candidate | Reads | 6 | 0.0 | 0–0 | 0, 0, 0, 0, 0, 0 |
| 2 | Candidate | LogicalReads | 6 | 10998.0 | 10991–11039 | 11039, 11001, 11030, 10995, 10991, 10994 |
| 2 | Candidate | Writes | 6 | 33.5 | 22–95 | 95, 94, 31, 33, 22, 34 |

## Getrennte AA-Kontrollpaare

Beide Slots erzwingen PK. Ihre drei Samples je Slot werden weder AB/BA zugeschlagen
noch zur nachträglichen Baselinekorrektur verwendet.

| Profil | AA-Slot | Metrik | n | Median | Min–Max | alle Samples |
|---|---:|---|---:|---:|---|---|
| 1 | 1 | CpuMs | 3 | 24 | 22–51 | 22, 24, 51 |
| 1 | 1 | ElapsedUs | 3 | 24655 | 24543–61545 | 24543, 24655, 61545 |
| 1 | 1 | LogicalReads | 3 | 11025 | 11001–11039 | 11039, 11025, 11001 |
| 1 | 2 | CpuMs | 3 | 24 | 20–26 | 20, 24, 26 |
| 1 | 2 | ElapsedUs | 3 | 24566 | 24410–28677 | 24410, 24566, 28677 |
| 1 | 2 | LogicalReads | 3 | 10994 | 10993–11001 | 11001, 10994, 10993 |
| 2 | 1 | CpuMs | 3 | 41 | 27–51 | 27, 51, 41 |
| 2 | 1 | ElapsedUs | 3 | 41140 | 28680–53653 | 28680, 53653, 41140 |
| 2 | 1 | LogicalReads | 3 | 11026 | 11000–11039 | 11039, 11026, 11000 |
| 2 | 2 | CpuMs | 3 | 26 | 24–27 | 26, 24, 27 |
| 2 | 2 | ElapsedUs | 3 | 28767 | 28502–28841 | 28767, 28841, 28502 |
| 2 | 2 | LogicalReads | 3 | 10994 | 10993–11001 | 11001, 10994, 10993 |

## Erhaltene Fehler, Review und Quellenbindung

Vor Admission wurde ein konkreter P2 geschlossen: Candidate-XML (Extensible Markup Language; Format zur strukturierten Darstellung von Daten) durfte bislang
PK10 plus Candidate0/fehlende Counter akzeptieren. Der Candidate-Parser erlaubt
jetzt ausschließlich den geforderten Candidateindex mit tatsächlicher Source-/
Root-Threadsumme10. Acht reine Methoden bestanden einschließlich dieser positiven
und negativen Fixtures. Ein anfänglicher reiner XML-Fixture-Namespacefehler wurde
behoben; er führte zu keinem nativen Versuch.

1 tatsächlicher fehlgeschlagener Kandidat bleibt im gemeinsamen Ledger:
C1 erreicht beim Querynegativaufruf 51003/FAIL_STATE, tatsächliche initiale Counter
fehlen. 18 native Calls, SQL-/DB-/Containercleanup bestanden; keine Messwerte aus C1
veröffentlicht. C2 ändert ausschließlich den Requeststartspeichertyp datetime2(7)
zu DMV-kompatiblem datetime, die vollständige fünfteilige Identitätsbindung bleibt.
Die darauf folgenden vollständigen Lifecycles bestehen. Ein enger unabhängiger
Quellenreview und Fixabschluss meldet keine offenen P1/P2; Reviewer führt keine
Tests/Runtime und keine Reviewkette aus. Sechs kohärente Kandidaten je Schnitt
bleiben autorisiert; kein unveränderter Retry, kein Zurücksetzen historischer FAILs.

Ausgewählte Ausführungsquellen sind vor jedem Lauf gehasht und nach beiden Läufen
unverändert geprüft; keine vollständige transitive Python-Importattestation:

| Quelle | SHA256 |
|---|---|
| `Runtime/DGN010_MEASUREMENT/sources/10_Setup.sql` | `9a462b1e805711d6254105ec5d84966943e6547703ab458386b89bff7f06ea47` |
| `Runtime/DGN010_MEASUREMENT/sources/20_Probe.sql` | `5b5a52e1059beeb053d565a9310a0a254c6d44b75164caa3880e1ca16ea8c862` |
| `Runtime/DGN010_MEASUREMENT/sources/30_Plan.sql` | `be6fd088797cefe6f9be311da693a53571c8624aefb9ac7d5adcecf87ef5050b` |
| `Runtime/DGN010_MEASUREMENT/sources/40_Window.sql` | `04b99071cb3dcba02b0809db8d56096a75ccfe9c6661a8b8583d683322ddde14` |
| `Runtime/DGN010_MEASUREMENT/sources/90_Cleanup.sql` | `129894ffc2a7eea35f5c26bbe40d0b328674329e344e72929922abfa029c1b84` |
| `Runtime/DGN010_MEASUREMENT/sources/guard.sql` | `69ab06578c30d17432bc335b7c5ec399ab1d137d1260de016e65c139f881a9e2` |
| `Runtime/DGN010_MEASUREMENT/qualify.py` | `077c589833f2d09a8659b05c6edf9ce70b0b3e98afd07f501d9ebbb015ced4f5` |
| `Runtime/DGN010_MEASUREMENT/probe.py` | `c619884326644839ca5d9ad181a1042c5d8ece27d24a8c288e63e3b8ebde649f` |
| `Runtime/DGN010_MEASUREMENT/plans.py` | `d48d0d23b07a46f3850f4b63a1132746d172cb0bb58b20f2a93839aedeb9889e` |
| `Runtime/DGN010_MEASUREMENT/source_evidence.py` | `b51a7d2a65eae1a12561b00bed4e962a88a0abdf47a8d5ee58cecf4b0a461211` |
| `Runtime/DGN010_MEASUREMENT/measurement.py` | `8df0292a0aefc23457d3ac970e510b690404c4847ac1bb2c3f90c2011dc6b405` |

Die numerischen Daten erlauben allein Aussagen über diesen festen Readerbatch mit
Buffer-/Impersonationaufwand. Ein Indexseek oder ein kleinerer Einzelmedian bestätigt
keine LLM-Advicehypothese. Nutzen gegen Indexabwesenheit, isolierte SELECT-/DML-/
Buildkosten, vollständige Worker-/TempDBkosten, Readerpläne, ältere Engines,
öffentlicher FWK-/Versionsconsumer und vollständige TP-PERF-/Modulabnahme bleiben
offen. DGN-010 PROPOSED; Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.

Aktuelle Head-/Main-Gates, PR/Integration, ganze Treeübernahme, FF-Sync und eigener
lokaler/Remote-Branchcleanup folgen vor Abschluss. Nächster begrenzter kanonischer
Schritt ergänzt DGN-010-DML-/Effektseparation; keine unveränderte Messwiederholung.
