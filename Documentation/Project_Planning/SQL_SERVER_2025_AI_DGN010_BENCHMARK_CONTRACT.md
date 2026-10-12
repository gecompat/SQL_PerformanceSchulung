# DGN-010 – öffentlicher Auswertungsvertrag der getrennten Messscopes

Stand: 2026-10-12. TSK-011/CUR-021, DGN-010 weiterhin PROPOSED.
Reine öffentliche Implementierungsvorbereitung; kein SQLaufruf oder Provisioning.

## Abgeschlossene private Grundlagen

[PR194](https://github.com/gecompat/SQL_PerformanceSchulung/pull/194) vollständig
abgeschlossen: Head f30021a308bbd1bc6571ccd0d375330daabb839b mit sieben aktuellen
Head-Workflows PASS; Squash abd392c63d7b89421df91f27626261f942ebe494 mit fünf
Main-Workflows PASS; ganzer Tree 32d8d00dca6f1f7d49ed6b3967ac3cc745edea26
exakt übernommen, main FF/sauber und eigener lokaler/Remote-Branch entfernt.

Die [erzwungenen Readerpfade](SQL_SERVER_2025_AI_INDEX_MEASUREMENT_REVIEW.md),
[DML-Effektseparation](SQL_SERVER_2025_AI_INDEX_DML_REVIEW.md) und
[ungezwungenen SELECT-Batches](SQL_SERVER_2025_AI_INDEX_SELECT_REVIEW.md)
beantworten unterschiedliche Fragen. Dieser Vertrag bereitet ausschließlich
die öffentlichen ungezwungenen SELECT- und DML-Scopes vor. Frühere Ownerpläne
qualifizieren keine aktuellen Readerpläne oder Indexnutzung aller Messfenster.

## Vor Ausführung feste Profilgrenzen

Ein späterer Runner verwendet nur SQL17.0.5005.3/Developer/CL170 auf einer eigenen
neuen markierten Instanz, vier CPU/sechs GiB, 1000 synthetische IDs 1–1000,
Value=Id×3 und 100 F-Payloadbytes. SIMPLE, Dateilimits 256/64 MB und unveränderte
MAXDOP/PREVIEW_FEATURES 0. Höchstens sechs kohärente Korrekturkandidaten je
Implementierungsschnitt; gemeinsame Ledger zählen alle historischen FAILs.
Ein Retry braucht geänderte Ausführungsquellen oder neue konkrete Evidenz.
300 Sekunden reguläres Profilbudget, anschließend insgesamt 60 Sekunden Cleanup.
Das konkrete öffentliche Versions-/Fehlerlaufbudget wird vor Admission im
kanonischen Ausführungsstand gebunden; dieser reine Schnitt erzeugt keine Container.

SELECT: identische ungezwungene Readerquery mit int-Parametern 101/110,
ORDER BY Id und MAXDOP1 ohne INDEX-Hints. DML: Owner-UPDATE der IDs 101–110
mit Value+1/OUTPUT und tatsächlichem Rollback der eigenen Transaktion pro Batch.
Keine freien Modellqueries, Provider-/Cloudaufrufe, ONNX- oder Hoständerungen.
Eine gespeicherte Advicefixture muss ausdrücklich synthetisch bleiben.

Je Scope fünf separate Einstatement-Warmuprequests pro Indexzustand, anschließend
drei serielle AB-/BA-/AA-Blöcke mit jeweils zwei Fenstern und 100 Statements:
18 Messfenster, sechs AB/BA-Samples je Zustand, drei AA-Paare separat.
A ohne/B mit Candidateindex; vier Build-/Dropzyklen pro Profil außerhalb Messung.
1810 vollständige Statementoracles/18100 Rowkontrollen, zusätzliche positive
Einstatementkontrolle sowie tatsächliche Source-/Resultgegenprobe getrennt.
46 vollständige 1000-Row-Source-/Indexaufnahmen mit vorab festgelegtem Zustandsablauf.

## Öffentlicher Recordvalidator

[Fensterparser](../../Tests/Static/dgn010_window_evidence.py) und
[Benchmarkauswertung](../../Tests/Static/dgn010_benchmark_evidence.py) führen kein SQL
aus. Sie prüfen vollständige eigene Request-/DB-Identität, eindeutige serielle
UTC-Fenster, tatsächlich monotone CPU-/I/O-Deltas, gleiche Counteridentitäten,
die gesamte vorab feste Population sowie vollständige Source-/Indexzustände.
Der eigene DB-ID-Caller muss unabhängig attestiert sein. Bool-/Floataliaswerte,
fehlende Werte, Trunkierung, doppelte JSON-Felder/Parts und fremde Präfixe sind FAIL.

SELECT prüft alle zehn IDs/Werte/Payloadbytes pro Query gegen die feste Referenz.
DML bindet jeden OUTPUT-Digest an Value=Id×3+Ordinal und verlangt vor/nach dem
Rollback Transaktionsdepth0. Ein unveränderter Sourcewert ersetzt kein UPDATE.
Native Gegenproben/Restore, Config- und Readerrechteattestationen bleiben beim
späteren Runtimeproducer; ein bloßes Flag oder synthetisches Fixture belegt sie nicht.

CPU/I/O misst denselben tatsächlichen Request einschließlich Countergrenzen;
UTC-Elapsed enthält für SELECT Impersonation/Query-/Buffer-/Transfer-/Delete-/REVERT-
Aufwand und für DML BEGIN TRAN/UPDATE-/OUTPUT-/Rollbackaufwand. Diese Grenzen sind
nicht identisch. Coarse DMV-datetime-Requeststart ist ausschließlich Identität,
keine Crossclockordnung gegen datetime2(7)-UTC-Grenzen. Vollständige Source-/
Resultoracles und JSONaufbereitung liegen außerhalb des berichteten Messfensters.

Die Ausgabe enthält alle sechs AB/BA-Zahlen, n, Min/Max, Nullanzahl und exakten
dezimalen Mediantext; große gültige Zähler werden nicht durch Floatmediane gerundet.
Warmups bleiben ausgeschlossen, AA-Paare separat. Keine Requestidentitäten, UTCs,
Source-/Querypayloads oder Plantexte in der aggregierten Ausgabe.
Fehlende Werte werden niemals zu Null; kleine Batchpopulationen liefern keinen
p95/p99, Durchsatz, statistischen Nachweis oder allgemeine Speedupgarantie.

## Getrennte numerische FWK-011-Invarianten

Die festen Verträge für
[SELECT](../../Tests/Static/Fixtures/dgn010/DGN010_SELECT.result-contract.json) und
[DML](../../Tests/Static/Fixtures/dgn010/DGN010_DML.result-contract.json)
prüfen je zwölf tatsächliche numerische Invarianten: pro Baseline/Comparison
1000 Source-Rows, sechs Messfenster, 600 Statementoracles, 6000 Rowkontrollen,
zehn Rows pro Statement und 100 Statements je Messfenster. Vollständige
ID-/Phase-/Metrik-/Sollwert-/FAIL-/on_missing-Bindung verhindert Aliasverträge
oder eine stille Herabstufung. Ein numerischer PASS ersetzt keinen Runtime-PASS.

`record_validation=PASS` ist reine Recordkonsistenz. `runtime_qualification`,
`tp_perf`, vollständige Workerkosten und statistische Signifikanz bleiben
NOT_ESTABLISHED; aktuelle Indexnutzung NOT_CAPTURED. Der spätere positive
Runtimeproducer muss KnownEnd, natives Ergebnis, Cleanup und Provenienz selbst
nachweisen. Voller Indexnettonutzen einschließlich Build/Commit/DML bleibt offen.

## Prüfung und Verarbeitung

[Gegenproben](../../Tests/Static/test_dgn010_benchmark.py):
`python Tests/Static/test_dgn010_benchmark.py` – 20 synthetische Methoden bestanden,
einschließlich Sourcewerte/Bytes/Population, Index-/DB-/Requestbindung, DML-Ordinal/
Rollbackdepth, Warmup-/AA-Ausschluss, Nullen/Ausreißer, exakte große Mediane,
fehlende Felder und vollständige FWK-Vertragsbindung. Enger unabhängiger Review
des neuen öffentlichen Schemas ohne offene P1/P2 abgeschlossen; Reviewer ohne
Tests/Runtime. Vier bereits gebundene tatsächliche SELECT-/DML-Records wurden
gegen unveränderte ausgewählte Nativequellen/Recordhashes und den unabhängig
erfassten DB-ID-Frame erneut rein ausgewertet: 48 numerische FWK-PASSs, gleiche
Samples/Median/Min/Max, null zusätzliche native Ausführungen. Diese neue reine
Auswertung erweitert keine Runtime-, Herkunfts-, Versions- oder TP-PERF-Abnahme.

Ein Owner, ein Reviewer allein für das neue konkrete Record-/FWK-Risiko; keine
Reviewkette oder Wiederholung unveränderter grüner SQLprofile. Statische KI-CI
nimmt nur neue Tests und ihre Abhängigkeiten auf. Runtimejob und native gemeinsame
API bleiben unverändert; der bestehende Revisionselector muss am aktuellen
Head/Main ausdrücklich NOT_APPLICABLE für diese rein statischen Eingaben nachweisen.
Keine zweite lokale Vollprivacyprüfung; geänderte Dateien vor jedem Commit und
zentrale aktuelle Head-/Main-Gates bleiben erforderlich. Modell-/Tokenverbrauch
unbekannt. Nächster kanonischer Schritt ist der öffentliche bounded Runtimeproducer
mit Versions-/Fehler-/Recovery-/Markerqualifikation, weiterhin kein Gesamtabschluss.
