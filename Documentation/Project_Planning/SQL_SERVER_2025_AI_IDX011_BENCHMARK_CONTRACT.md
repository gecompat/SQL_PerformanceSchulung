# IDX-011 – Auswertungsvertrag des gebundenen Benchmarks

Stand: 2026-10-11. Implementierungsvorbereitung innerhalb TSK-006 und DEC-074.
Der versionierte Validator ist ein offline geprüfter Teil der öffentlichen
Demoimplementierung. Der anschließende
[öffentliche Controller und Runtimebefund](SQL_SERVER_2025_AI_IDX011_RUNTIME_REVIEW.md)
belegen inzwischen begrenzte tatsächliche Requests und Lifecycle-Erwartungen;
die vollständige Demo-/TP-PERF-Abnahme bleibt offen. Synthetische Fixtures ersetzen keine
tatsächlichen Requests, Ergebnisse, Quellen-, Index- oder Cleanupnachweise.

## Vor SQL fixierte Umfangs- und Ergebnisgrenzen

Der spätere Runner verwendet ausschließlich den vollständig attestierten
SQL-17.0.5005.3-Linux-/Developer-/CL-170-Pfad von
[DEC-074 – Gebundenes ANN-Legacyprofil mit Generation UNKNOWN/WARN](SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md). Unverändert bleiben
1000 synthetische float32-VECTOR(3)-Quellenrows, clustered INT-PK (Primary Key; Primärschlüssel), cosine,
Queryvektor `[1,0,0]`, K=5, eigene markierte DB, vier CPUs, sechs GiB,
300 Sekunden regulärer Gesamtablauf und ein separates 60-Sekunden-Cleanupbudget.
Es werden keine neuen Container oder SQL-Aufrufe durch diesen Offline-Schnitt erzeugt.
Die höchstens zwei kohärenten Kandidaten und 16 seriellen eigenen Container des
kanonischen Ausführungsstands bleiben das gemeinsame öffentliche Runtimebudget.

Je Pfad werden zuerst fünf einzelne Warm-up-Requests mit jeweils genau einem
Suchstatement und vollständiger Ergebnisprüfung protokolliert. Ein einzelner
Request mit fünf Queries erfüllt diesen Vertrag nicht. Erst nach sämtlichen
zehn Warm-ups beginnen drei Blöcke in unveränderter Reihenfolge:

| Block | Reihenfolge | Slot 1 | Slot 2 |
|---|---|---|---|
| 1, 2 und 3 | AB | Exact | VECTOR_SEARCH |
| 1, 2 und 3 | BA | VECTOR_SEARCH | Exact |
| 1, 2 und 3 | AA | Exact | Exact |

Jedes der 18 Messfenster enthält genau 100 Suchstatements. Jeder Aufruf liefert
fünf eindeutige tatsächliche Ergebnisrows in derselben temporären Ablage.
Maximal 500 Ergebnisrows werden gleichzeitig gespeichert; dies erweitert
nicht den 1000-Row-Quellenkorpus. Je Lifecycle sind damit 1205 Exact- und 605
ANN-Suchstatements im Benchmark begrenzt. Quellenaufbau, Indexbuild, Oracle,
repräsentative Planaufnahme und Filtergegenproben gehören in eigene Fenster.
Es gibt kein Cacheleeren und keinen zusätzlichen Concurrencylauf.

Exact muss bei jeder Query das vollständige Top-5-Oracle erfüllen, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren) mindestens
vier seiner fünf IDs. Die Ground Truth entsteht aus allen unabhängig geprüften
Quellendistanzen, sortiert nach Distanz und danach Id; die Distanzabweichung ist
höchstens 0,0001. Ein hoher Batchmittelwert verdeckt keine einzelne Query unter
Recall 0,8. Fehlende, fremde oder doppelte IDs, nicht endliche Distanzen und eine
unvollständige Queryabdeckung sind Fehler. Filterverlust bleibt getrennte Evidenz;
die enge Postfilterprobe mit null Rows bekommt keinen Retrieval-PASS.

## Tatsächliche Messfenster und Interpretation

Jeder Warm-up und jedes Messfenster trägt seine vollständige tatsächliche
Session-/Request-/Requeststart-/Connection-/DB-ID. Eine mehrfach verwendete
Identität darf nicht als mehrere Requests gezählt werden. Die DB-ID muss mit
der unabhängig vom Runner attestierten eigenen Ziel-ID übereinstimmen; ein in
sich konsistenter fremder DB-Bezug genügt nicht. Tatsächliche UTC-Grenzen aller
Warm-up- und Messrequests müssen chronologisch sein und dürfen nicht überlappen.
Die Labelreihenfolge allein ist kein zeitlicher Ausführungsnachweis. CPU (Central Processing Unit; Prozessor), Reads,
Logical Reads und Writes ergeben sich aus den tatsächlich erfassten
sys.dm_exec_requests-Zählern vor/nach dem Fenster. Beide Snapshotidentitäten
müssen exakt die Fensteridentität haben; fehlende Werte, Boolwerte, negative
oder fallende Zähler und abweichende Deltas werden abgewiesen. Elapsed ergibt
sich aus den tatsächlich erfassten datetime2-UTC-Grenzen; Null und Quantisierung
bleiben sichtbar. Das Erfassungsformat bleibt begrenzt und enthält ausschließlich
die eigene synthetische Quelle und tatsächliche Messwerte.

Warm-ups und AA-Kontrollen gehen nicht in den A/B-Vergleich ein. Je Suchpfad
werden Median/Minimum/Maximum aus seinen sechs AB-/BA-Fenstern ausgegeben.
Die drei AA-Paare bleiben separat als Rohwerte sichtbar. Keine feste Speedupratio,
keine universelle Optimierungsfreigabe und keine behauptete Indexnutzung aller
gemessenen oder gefilterten Queries. Temp-Ergebnisablage und Zähleraufnahme
gehören zum beobachteten Aufwand. Vollständige Worker-I/O (Input/Output; Ein- und Ausgabezugriffe) und tatsächlicher
Such-DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung) bleiben UNPROVEN; fehlende Memory Grants, Spills, Waits und preemptive
Zeit heißen NOT_CAPTURED, niemals Null. Generation bleibt UNKNOWN.

## Offlinevalidierung und verbleibende öffentliche Abnahme

[Validator](../../Tests/Static/idx011_benchmark_evidence.py) und
[Gegenproben](../../Tests/Static/test_idx011_benchmark.py) prüfen Reihenfolge,
Abdeckung, Warm-up-/AA-Ausschluss, jede Querys Qualität, Distanz, Requestbindung,
tatsächliche Counter-/Zeitdeltas und falsche Null-/Platzhalterwerte.
Aufruf: `python Tests/Static/test_idx011_benchmark.py`.
Zwölf synthetische Gegenproben bestanden. Der notwendige unabhängige
Quellen-/Methodenreview schloss nach einer kohärenten Korrekturwelle für die
globale zeitliche Serienbindung ohne offene P1/P2; die zusätzliche vollständige
DB-ID-Bindung ist geprüft. Der konkrete Integrationsabschluss steht im
kanonischen Ausführungsstand.

Das Modul führt kein SQL aus und attestiert nicht selbst Quelle, Eigentum,
Build-/Indexprofil, tatsächliche Pläne oder Lifecycle. Diese vorgelagerten und
nachgelagerten Pflichten bleiben beim öffentlichen Runner. Der anschließende
Runtimebefund belegt den konkreten repräsentativen Plan sowie begrenzte
Versions-/Fehler-/Recoveryfälle. Memory-/Spill-/vollständige Build-/Storagekosten-,
Rollen- und Hard-Abortabnahme bleiben offen. Der Validator gibt weiterhin
runtime_qualification NOT_ESTABLISHED aus;
ein Offline-PASS qualifiziert weder IDX-011 noch TP-PERF.

Verarbeitungsaufwand: ein Owner und ein notwendiger Reviewer für den konkreten
Ergebnisvertrag, höchstens eine kohärente Korrekturwelle. Keine erneute private
SQL-Diagnose, keine Testmatrix für unveränderte acht öffentliche Demos durch
diesen reinen Tests/Static-Schnitt. Der bestehende CI-Selector erkennt nur
statische Eingaben und eine unveränderte Runtime-Jobdefinition. Die beiden
neuen Dateipfade und der eine betroffene Test werden in den bestehenden
statischen KI-Job aufgenommen. Seine tatsächliche Head-/Main-Auswahl wird bei
Integration belegt; keine Änderung an Runtime-, Cleanup- oder Mergegates.
Modell-/Tokenverbrauch bleibt unbekannt.
