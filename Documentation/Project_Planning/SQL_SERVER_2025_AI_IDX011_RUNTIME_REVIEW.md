# IDX-011 – Öffentlicher Controller und begrenzter Runtimebefund

Stand: 2026-10-11, TSK-006/DEC-074. Öffentliche Implementierungsvorstufe,
keine freigegebene Demo und keine TP-PERF-Abnahme. Der kanonische Backlog
und CURRENT_EXECUTION_STATUS.md bleiben die ausführungssteuernden Quellen.

## Quellen- und Sicherheitsgate vor Runtime

Ein Implementierungsverantwortlicher und ein erforderlicher unabhängiger
Quellen-/Sicherheits-/Methodenreview prüften den öffentlichen Controller, seine
SQL-Phasen, Plan-/Filterparser, zwölf Controllergegenproben und den begrenzten
lokalen Provisionierungsrunner. Der bereits geprüfte Benchmarkvalidator aus
PR169 bleibt unverändert; seine zwölf Gegenproben ersetzen keine Runtime.

Fünf konkrete P2 wurden in einer zusammenhängenden Korrektur vor dem ersten
SQL-Lauf geschlossen: eigene Datenbankbindung der Arbeitsclients; Kennwort-
Umgebungsvertrag mit tatsächlichem Restore der vorherigen Prozessumgebung;
vollständige begrenzte Quellenblöcke; Recall des ursprünglichen repräsentativen
Suchlaufs samt unabhängiger Clientprüfung; globale Sperre bei nicht abgeschlossenem
Containercleanup vor jeder weiteren Admission. Eingabe-, vollständige Marker-
und Quellstrukturguards sowie dynamische Recoveryquotes waren Teil derselben
engen Closure. Keine offenen P1/P2, kein SQL oder Container durch den Reviewer.

Vor erster Runtime: Controller-SHA256
A2422C0BFFDDBB53B25BE3FB2402838FF939FCA34CAA10050A93AE5F845A1A4A;
lokaler Qualifikationsrunner-SHA256
6B746E9A12ABA7C7AA40314A6B857336D8BBF95A8B0E88DE9962E4F827AA46B9.
Diese Bindung ist historische Evidenz des ersten Kandidaten, kein Nachweis für
anschließende Quelländerungen.

## Kandidat 1 – Tatsächlicher FAIL nach vollständiger Quellenaufnahme

Ein eigener serieller Testcontainer, lokales vollständiges Image
78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
kein Pull, vier CPUs/sechs GiB, tatsächliches SQL 17.0.5005.3.
RunToken F01FF5A7FE634752. Preflight WARN wegen Generation UNKNOWN;
Setup, neue vollständige Snapshots, separate Preview-/MAXDOP-Enable und
SQL-Baseline PASS. Tatsächliche eigene DB-ID 5, beide Originalbaselines 0.

Die Python-Auswertung scheiterte als FAIL_RESULT_CONTRACT nach dem vollständigen
Output von 1000 Distanzen und zehn Vektorblöcken à 100 Rows. Indexbuild, Suche,
repräsentativer Plan, Filter und Benchmark wurden noch nicht erreicht. Die
Python-Rezeptur verwendete für die dritte Koordinate round(...,6), während der
vollständige konkrete T-SQL-Korpus sechsstellige Werte gemäß der rationalen
Ganzzahlrechnung floor(((Id*17)%97)*10^6/97)/10^6 zeigte. 330 Rows überschritten
gegen das falsche Python-Oracle die unveränderte 10^-6-Toleranz, maximal
1,03×10^-6. Der Befund ist kein Vektortyp- oder Indexfehler.

Alle 1000 vorhandenen Vektoren passen zur konkreten floor-Rezeptur mit maximal
3,0×10^-8 float32-Darstellungsabweichung. Die unabhängige Cosineberechnung aus
allen tatsächlich ausgegebenen Vektoren und sämtliche 1000 SQL-Distanzen bestehen
unter der ursprünglichen Toleranz. Dies wurde ausschließlich aus dem bereits
vorhandenen vollständigen Output geprüft, ohne neue SQL-Probe. Die
[Microsoft-Regeln zu Precision und Scale](https://learn.microsoft.com/en-us/sql/t-sql/data-types/precision-scale-and-length-transact-sql?view=sql-server-ver17)
erklären die Bedeutung der arithmetischen Zwischentypen; die konkrete beobachtete
floor-Rezeptur bleibt eine Bindung dieses Korpus, keine allgemeine Rundungsregel.

Frischer Restore bestätigte tatsächlich PREVIEW_FEATURES=0/MAXDOP=0; neuer
Attestationsclient bestätigte beide Werte vor markergebundenem Drop; eine weitere
SQL-Verbindung bestätigte DB-Abwesenheit. Vollständige eigene Name-/CID-/Image-/
Label-/Ressourcenbindung vor Removal und unabhängiges Lookup bestätigten
Containerabwesenheit. Gemeinsamer SQL-/Containercleanup: 12,41 Sekunden.
Kandidat 1 hält als FAIL an und wird nicht unverändert wiederholt.

## Enger Korrekturkandidat und offene Abnahme

Die Korrektur betrifft das Python-Oracle und seine Offlinefixtures; SQL-Rezeptur,
1000 Rows, float32-Dimension, Originaltoleranzen, K=5, Recallgrenze 0,8,
Benchmarkreihenfolge und normale/Recoverybudgets bleiben unverändert. Der
zusätzliche unabhängige Review betrifft ausschließlich die semantische
Oraclekorrektur und die vollständige vorhandene Evidenz, keine Vollanalyse.
Die ursprüngliche Gesamtgrenze bleibt zwei kohärente Kandidaten und maximal
16 eigene serielle Container. Der enge unabhängige Methodenreview bestätigte
die Erwartungswertkorrektur ohne Toleranzlockerung: maximale unabhängig
nachgerechnete Cosine-Distanzabweichung 1,05×10^-7; SQL-Quellen hashgleich.
Keine offenen P1/P2. Korrigierter Controller-SHA256:
9C5CFAC605987C912FA04CC8087755C1F91EA045897ECC5F93029FE82CC83FA0.

## Kandidat 2 – Acht serielle Lifecycle-Erwartungen erfüllt

Ein stabiler korrigierter Kandidat, acht neue eigene Container, neun insgesamt.
Der ursprüngliche FAIL bleibt unverändert; kein dritter Kandidat und keine
unveränderte Wiederholung. Alle Container verwendeten vollständige eigene
Name-/CID-/Image-/Label-/4CPU-/6GiB-Bindung, ohne Pull oder Fremdmutation.

| Fall | Tatsächliche Version | RunToken | Ergebnis | Gemeinsamer Cleanup |
|---|---|---|---|---|
| 2025 vollständig 1 | 17.0.5005.3 | DF7932CB575744BB | WARN, technische Erwartung erfüllt | 12,706 s |
| 2025 vollständig 2 | 17.0.5005.3 | BDECC8A3E6084BEC | WARN, technische Erwartung erfüllt | 12,418 s |
| 2019 Skip 1 | 15.0.4490.9 | B69377F0BFAC4310 | SKIP_VERSION vor Setup | 10,939 s |
| 2019 Skip 2 | 15.0.4490.9 | D69AF96DE5834C01 | SKIP_VERSION vor Setup | 10,334 s |
| 2022 Skip 1 | 16.0.4295.3 | F4A598203BDA47F9 | SKIP_VERSION vor Setup | 12,129 s |
| 2022 Skip 2 | 16.0.4295.3 | 947F45EB13A642A5 | SKIP_VERSION vor Setup | 12,068 s |
| Fehler nach Setup | 17.0.5005.3 | 782F7F67C9A9471A | kontrollierter FAIL_EXECUTION, Recovery erfüllt | 12,370 s |
| Fehler nach Indexbuild/vor Suche | 17.0.5005.3 | 52165B59173F4824 | kontrollierter FAIL_EXECUTION, Recovery erfüllt | 12,241 s |

Alle vier 2019-/2022-Fälle führten ausschließlich den öffentlichen Preflight aus;
eine separate SQL-Verbindung bestätigte Ziel-DB-Abwesenheit. Alle vier neuen
2025-Fälle persistierten beide tatsächlichen Baselines 0/0 und bestätigten Restore,
unabhängige Attestation vor Drop und getrennte DB-Abwesenheit. Alle neun
Containerabwesenheiten sind unabhängig bestätigt; keine eigenen Restcontainer.

Beide vollständigen Läufe attestierten alle 1000 Vektoren/Distanzen, eigene
Metadaten und den konkreten tatsächlichen Planoperator am eigenen Vektorindex.
Je Lauf zehn Warm-up-Requests plus 18 AB-/BA-/AA-Fenster, insgesamt 1810 einzeln
geprüfte Benchmarkqueries mit minimalem Recall@5 1,0. Warm-ups und AA bleiben
vom A/B-Vergleich ausgeschlossen. Breite Filterfälle lieferten je fünf ANN-Rows
bei Recall 1,0; 501–510 weiterhin null ANN-Rows/Recall 0 bei fünf Exact-Rows.
Qualitätsverlust bleibt sichtbar, keine Retrievalfreigabe für den engen Postfilter.
Eigener Indexdrop und identischer Exact-Fallback bestanden in beiden vollständigen
Läufen. SQL-Gegenfixtures bestätigten je 24 Marker-, neun Baseline-, drei Ergebnis-,
drei Quellen-, zehn Typ-/Metric- und vier Filterablehnungen.

| Beobachtung je 100-Query-AB-/BA-Fenster | Lauf 1 Exact / ANN | Lauf 2 Exact / ANN |
|---|---|---|
| CPU-Median | 30,5 / 66 ms | 36 / 97 ms |
| UTC-Elapsed-Median | 32,740 / 71,864 ms | 35,140 / 107,160 ms |
| Logical-Reads-Median des aktiven Requests | 1762 / 75583,5 | 1762 / 75583,5 |
| getrennte Indexbuild-Wandzeit | 866,814 ms | 971,195 ms |

Das sind gebundene lokale Messungen einschließlich temporärer Ergebnisablage
und Zähleraufnahme. Kein ANN-Geschwindigkeitsvorteil im kleinen Korpus belegt,
keine universelle Speedupratio. Physische Request-Reads tatsächlich null;
CPU-/Elapsed-Null wurde in diesen gemessenen Fenstern nicht beobachtet.
Vollständige Rohwerte und AA-Paare bleiben lokal unter der Quellenbindung erhalten.

Öffentliche Runtimequalifikation bleibt NOT_ESTABLISHED. Vollständige Worker-I/O,
tatsächlicher DOP aller Suchen, Memory-/Spill-/Waits-/Build-/Storagekosten,
Minimalrollen- und Hard-Abort-Abnahme sind offen. Keine Speedupratio, keine
pauschale Indexnutzung aller gemessenen/gefilterten Queries und keine numerische
Generation. IDX-012 sowie Provider-/Cloud-/ONNX-Grenzen sind getrennte Schritte.

Verarbeitungsaufwand: ein Owner, ein notwendiger konkreter Reviewer, lokale
betroffene Offline-Gegenproben und der begrenzte Runtimekandidat. Der CI-Zusatz
führt einen neuen statischen Controllertest aus; Runtime-Jobdefinition unverändert.
Der neue öffentliche Demopfad wird vom bestehenden konservativen Selector als
Runtimeeingabe gewählt und löst die bestehenden acht-Demo-Matrizen als
Integrationsgates aus. Die Workflowdatei kann zusätzlich Legacy-Matrizen auslösen;
deren tatsächliche Head-/Main-Auswahl wird im PR belegt. Diese Prüfungen sind
keine ANN-Abnahme und keine Wiederaufnahme anderer Workstreams. Modell-/
Tokenverbrauch bleibt unbekannt.

## Vorhandene repräsentative Pläne – begrenzte Memory-Evidenz

Der anschließende Parserzusatz wertet ausschließlich das eindeutig gebundene
Suchstatement des bereits aufgenommenen Actual Plans aus. Build 17.0.5005.3,
vollständiger Statementtext und eigene Objekt-/Index-/Actual-Rows-Bindung bleiben
erhalten. Direkte MemoryGrantInfo-Attribute werden als rohe Showplanwerte
ausgegeben; fehlende Attribute bleiben null/NOT_CAPTURED. Die Strukturaufnahme
von Warnings und WaitStats ist kein Spill- oder Waitkosten-Oracle. Der DOP-Rohwert
0 wird weder zu 1 korrigiert noch auf andere Queries übertragen.

Aus beiden vollständigen vorhandenen Rohoutputs wurde der neue Parser rein lokal
ausgeführt. Sämtliche bisherigen Planassertions blieben inhaltlich identisch;
kein zusätzlicher SQL-, Container-, Benchmark- oder Provideraufruf. Die Quellen
stammen aus Kandidat 2 der abgeschlossenen öffentlichen Runtimewelle:

| Rohes Attribut des repräsentativen Suchstatements | Lauf 1 | Lauf 2 |
|---|---|---|
| DegreeOfParallelism | 0 | 0 |
| NonParallelPlanReason | MaxDOPSetToOne | MaxDOPSetToOne |
| SerialRequiredMemory / RequiredMemory | 512 / 512 | 512 / 512 |
| SerialDesiredMemory / DesiredMemory | 552 / 552 | 552 / 552 |
| RequestedMemory / GrantedMemory | 1024 / 1024 | 1024 / 1024 |
| MaxUsedMemory | 32 | 32 |
| GrantWaitTime / LastRequestedMemory | 0 / 0 | 0 / 0 |
| MaxQueryMemory | 758528 | 757616 |
| Warnings / WaitStats | NOT_CAPTURED / NOT_CAPTURED | NOT_CAPTURED / NOT_CAPTURED |

Diese Werte sind unmittelbare Attribute genau zweier repräsentativer Aufnahmen.
Sie sind keine Memory-/DOP-Abnahme aller 1810 Benchmarkqueries je Lauf, keine
gemessene Spill-/Waitfreiheit und keine vollständigen Build-/Storagekosten.
Die Rohattribute behalten ihre Originalnamen; das Parserformat führt keine
Einheitenumrechnung oder abgeleiteten Nullwerte durch. Zur Einordnung der
MemoryGrantInfo-Felder dienen SRC-009 und die
[Microsoft-Diagnose zu Memory Grants](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/performance/troubleshoot-memory-grant-issues)
(Abruf 2026-10-11); der konkrete numerische Befund stammt aus den eigenen Plänen.

Vollständige Rohquellen-SHA256, ohne Übernahme der XML-Outputs ins Repository:
Lauf 1 f587f1461f09839e3218bac26be5ddf43fda9910195e65bbba2a58dc974d912e;
Lauf 2 291f1cf22e496cf11e456ec546d5df8c7abfd9a5229e4a4fe262579450949faf.
Zwölf neue synthetische Parsergegenproben trennen fehlend/Null, direkte/nested
Memoryknoten, andere Statements, doppelte Plan-/Memory-/Waitknoten, ungültige
Numericformen, Build-/Statement-/Tokenbindung und fremde Indexobjekte.

Verarbeitungsumfang dieses Zusatzes: ein Owner, ein erforderlicher enger
Methodenreview, höchstens eine kohärente Quellenkorrektur. Rein vorhandene
Planquellen und synthetische Gegenproben; keine Wiederholung der abgeschlossenen
lokalen Runtimewelle. Der bestehende konservative CI-Selector wählt wegen der
geänderten öffentlichen Parserquelle die acht-Demo-KI-Matrix. Der neue statische
Test wird in denselben vorhandenen statischen Job aufgenommen; Runtimegates und
andere Workstreamgrenzen bleiben erhalten. Modell-/Tokenverbrauch unbekannt.

Der erforderliche enge unabhängige Methodenreview schloss ohne offene P1/P2.
Parser-SHA256 DD3771E53FC3E9FDD10165FF692A72D520BD640FFCCF608B2F9ADF7C0DDE49F2;
keine Runtime durch den Reviewer und keine Erweiterung der Abnahme.
