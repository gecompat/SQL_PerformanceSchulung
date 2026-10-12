# RES-008 – begrenzte öffentliche Aggregation

| Merkmal | Wert |
|---|---|
| Status | gebundener Teilnachweis; Demo weiterhin PROPOSED |
| Zuordnung | RES-008, CUR-020, TSK-010 |
| Profil | SQL 17.0.5005.3, LOCAL, 4 × 100 deterministische float32-Vektoren |

## Ausgangsstand

[Öffentlicher Consumer](SQL_SERVER_2025_AI_RESOURCE_PUBLIC_REVIEW.md) über
PR188 vollständig integriert: Head b2c55911994db6460a15e27e2b5b3ca32390ac0b,
zwölf aktuelle Head-Workflows PASS; Squash 192fcd945d1408bf6509263600af7beb2bb83c4d,
zehn aktuelle Main-Workflows PASS. Ganzer Tree
151bd6af448e7b6153b23c5a7b69f63d9f7353d6 exakt übernommen, lokales main per FF
sauber und eigener lokaler/Remote-Branch entfernt. CI-C1 auf allen drei Versionen
FAIL am Proxy erhalten, alle drei eigenen CI-Container entfernt. CI-C2 nutzt nur
den eigenen Adapter; aktuelle 2025-Consumerläufe WARN und erwarteter Setupfault
mit Recovery, 2019/2022 vor Setup SKIP. Gemeinsame API-/Proxydateien unverändert.

## Neuer begrenzter Consumer

[res008_summary.py](../../Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/res008_summary.py)
wertet ausschließlich einen vollständig positiven Controllerabschluss im Speicher
aus. Bekanntes Clientende, tatsächlich bestätigter Cleanup und native
Source-/Querygegenkontrollen bleiben Voraussetzung. Erneute reine Recordprüfung
bindet alle 20 Warmups und 54 Fenster an feste Labels, tatsächliche eigene
Request-/Counteridentität, serielle UTC-Fenster und alle 5420 Queryoracles.
Die vorhandene native Aufnahme und Provenienz werden dadurch nicht ersetzt.

Je Dimensionspaar sechs A- und sechs B-Fenster für 100 Queries, nur AB/BA.
20 Warmups ausgeschlossen; drei AA-Paare je Vergleich getrennt mit ihren
tatsächlichen Werten und Verhältnissen. Median/Min/Max/Stichprobengröße und
Nullzählung enthalten alle aufgenommenen Fenster, auch Ausreißer. Nullbaseline
ergibt N/A statt Division oder erfundenem Nullverhältnis. Sechs Batchfenster
belegen keine individuellen Querylatenzen, belastbaren Tails oder Signifikanz.
Gegenstand ist LIVE_REQUEST-Batchkosten einschließlich Counter-/Tempresult-
Overhead; vollständige Worker-I/O bleibt NOT_ESTABLISHED.

Vier repräsentative Planrecords bleiben an Dimension/Build/Quellenobjekt und
Scan100/Root1 gebunden. Nur numerische rohe Memoryattribute und roher DOP werden
ausgegeben; DOP 0 bleibt 0. Fehlendes Attribut bleibt None, keine Nullmessung.
Waits/Spills werden hier nicht ausgewertet. Keine Rawidentitäten, UTC-/Request-
oder Connectionwerte, Querytexte, Quellen-/Planstrings oder XMLs im Export.

## Feste numerische FWK-011-Invarianten

Drei feste eigene Expected-Verträge, höchstens 10000 Bytes je Datei, je zehn
EXACT/FAIL/on_missing=FAIL-Assertions. Jede ID bindet Phase/Metrik/Integer-Sollwert
und vollständige Pflichtfelder: 100 Source-Rows, feste tatsächliche Vektorbytes,
sechs Vergleichsfenster, 600 geprüfte Einzelqueries und genau eine Ergebnisrow.
Nur diese 30 numerischen Invarianten erhalten FWK-011-PASS. Gesamtergebnis bleibt
WARN_OPTIONAL_EVIDENCE_SKIPPED; volle FWK-/Demo-/TP-PERF-Abnahme wird nicht behauptet.

## Gebundene bereits vorhandene native Daten

Zwei vollständige lokale C1-Profile aus PR188, je 74 Raw-Windowframes und vier
Raw-Pläne exakt gegen deren vollständige Records erneut gebunden; insgesamt
148 Fenster/acht native Pläne, 60 aktuelle numerische Assertions PASS.
Diese neue Auswertung benötigt keine erneuten unveränderten SQL-Läufe,
neuen DBs/Container, Preview-/MAXDOP-/Query-Store- oder Hosteffekte.
Privat bleiben ursprüngliche Rawdaten, Lifecycle-/Sourcebindungen, frühere reine
Consumerstände und die aktuelle C3-Source-/Record-/Ausgabebindung ignoriert.

Batchwerte, jeweils A=32 / B=angegebene Dimension; n=6 je Spalte:

| Lauf | B-Dimension | CPU-Median ms A/B | Elapsed-Median µs A/B | Elapsed-Nullfenster A/B | Logical-Reads-Median A/B |
|---|---|---|---|---|---|
| 1 | 384 | 6.5 / 7.0 | 8169.0 / 6151.0 | 0 / 0 | 615.0 / 2415.0 |
| 1 | 768 | 5.5 / 8.0 | 4118.5 / 8189.0 | 0 / 0 | 615.0 / 5415.0 |
| 1 | 1536 | 6.0 / 15.0 | 4094.5 / 14483.0 | 1 / 0 | 615.0 / 10415.0 |
| 2 | 384 | 6.0 / 7.0 | 8200.0 / 8190.0 | 0 / 0 | 615.0 / 2415.0 |
| 2 | 768 | 6.0 / 8.5 | 8192.5 / 8193.5 | 1 / 0 | 615.0 / 5415.0 |
| 2 | 1536 | 6.0 / 12.0 | 8178.0 / 12280.0 | 0 / 0 | 615.0 / 10415.0 |

Diese Beobachtungen begründen keine monotone CPU-/Elapsedwirkung, keine
allgemeine Dimensionswahl und keinen Speedup. Tatsächliche physische Reads und
Writes, AA-Werte und Maxima bleiben in der kontrolliert ausgegebenen Aggregation
sichtbar; diese kleine Tabelle ist keine vollständige Recorddarstellung.

## Prüfung und Aufwand

25 synthetische Gegenfälle plus drei öffentliche CLI-Gegenfälle bestanden.
Der enge unabhängige Review fand einen P2 bei der nur über IDs gebundenen
FWK-Assertion. Kanonische Phase-/Metrik-/Expected-/Zahltypbindung und fünf
Driftgegenfälle schließen ihn am Core
5664786b54cc8f4aa1e4fea5eb41675e1b311d8d28ef6b965e6c123c1d04cd2e.
Keine weiteren konkreten P1/P2; Quellenclosure, keine Reviewer-Runtime oder
Reviewer-Tests. Historische SQL-/Zeit-/Plan-/CI-FAILs bleiben erhalten.

Ein Owner, höchstens sechs kohärente Kandidaten für diesen reinen Folgeschritt;
keine zusätzlichen lokalen SQL-Qualifikationscontainer. Neue CI bewertet die
Aggregation an tatsächlich aufgenommenen Daten des öffentlichen Consumerpfads
und behält zwei Lifecycles/Versions-SKIPs/Setupfault/Cleanup. Bestehende Native-
Inputs und SQL-/Quellen-/Mess-/Planvalidatoren unverändert; kein unveränderter
lokaler SQL-Retry. Neue Testpfade in beiden CI-Triggern, nur betroffene lokale
Checks; aktuelle tatsächliche Head-/Main-Gates bleiben Pflicht. Kein zusätzliches
Review eines Reviews, keine Vollsuite-Lokaldoppelprüfung; Modell-/Tokens unbekannt.

## Noch offen und nächster Schritt

Aktuelle Head-/Main-Gates, PR/Integration, ganzer Tree, FF-Sync und eigener
Branchcleanup folgen vor Abschluss. RES-008 PROPOSED, TSK-010 offen; volle
Worker-/Wait-/Spill-/TempDB-/TP-PERF- und Größen-/Loader-/Modellqualität offen.
Keine Cloud-/Bezahl-/Modell-/ONNX-/roten Hostaufrufe, andere Repositories unverändert.
Danach begrenzte Teilnehmer-/Traineraufgabe zur korrekten Interpretation dieses
öffentlichen Teilprofils unter TSK-012, ohne zusätzliche SQL-Wiederholung oder
Behauptung einer vollständigen didaktischen/Modulabnahme.
