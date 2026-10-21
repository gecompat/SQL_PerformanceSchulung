# TSK-006 – Begrenzte ANN-Messdiagnose

Stand: 2026-10-11. Private Diagnose gemäß dem vor SQL festgelegten Messscope
in [Aktueller Ausführungsstand](CURRENT_EXECUTION_STATUS.md). Die ausdrückliche
Benutzerfreigabe umfasst die weiteren notwendigen lokalen Schritte dieser Welle;
frühere FAIL-Checkpoints und verbrauchte Budgets bleiben erhalten.

## Messmethode und Grenzen

Fester 1000-Row-VECTOR(3)-float32-Korpus, gleicher Queryvektor, cosine/K=5 und
identische temporäre Ergebnisspeicherung. Je Pfad ein ausgeschlossener Warm-up
und fünf gemessene Batches mit zehn Queries; alternierende Paarreihenfolge und
keine Cacheleerung. Jeder Query muss fünf gültige Id-/Distanzrows liefern;
Exact fünf Oracle-Treffer, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren) mindestens vier. Das ausgewiesene Recallminimum
ist das Minimum der Batchmittelwerte, kein Minimum einzelner Queries.

Maximal zwei Kandidaten/vier serielle eigene Container; zwei Lifecycles je
positivem stabilem Kandidaten. Ein ungeeignetes Zählerfenster wird ohne geänderte
Evidenz nicht nochmals ausgeführt. Die unveränderten Eigentums-/Source-/Baseline-
und Cleanupkontrollen des Legacy-Probes bleiben erforderlich. Kein DML-/Stale-,
Host-, Cloud- oder ONNX-Effekt und keine vollständige FWK-/TP-PERF-/Demoabnahme.

Kandidat 01 erfasst Session-Deltas (SRC-111). Kandidat 02 erfasst ausdrücklich
LIVE_REQUEST-Deltas (SRC-110), an Session, Request-ID, Startzeit, Connection-ID
und eigene DB gebunden. Nicht-NULL, nichtnegative Zähler und dieselbe Identität
vor/nach jedem Batch sind Pflicht. Nach Warm-up-Ausschluss muss jeder Pfad ein
positives Logical-Read-Delta enthalten. Dies prüft ein aktives Fenster;
vollständige Worker-IO und tatsächlicher Such-DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung) bleiben UNPROVEN. SRC-110
begrenzt die Koordinatorzähler paralleler Row-Mode-Requests und schließt
preemptive Zeit aus. Zeitquantisierung, Ergebnisspeicherung und Zähleraufnahme
bleiben sichtbar; Waits nicht erfasst. Generation UNKNOWN, neue Indexnutzung
UNPROVEN, kein allgemeines Speedupversprechen.

## Erster Kandidat: ungeeignetes Sessionfenster

Ein Lifecycle: technische Capture-/Ergebnis-/Cleanupkontrollen PASS, sämtliche
CPU-/Read-/Logical-Read-/Write-Deltas null. Das belegt keine ressourcenfreie Suche.
Messqualifikation WARN: inaktives oder ungeeignetes Zählerfenster und begrenzte
Zeitauflösung. Kein zweiter unveränderter Lauf.

| Sessionaufnahme, fünf Batches je Pfad | CPU-Median ms | Elapsed-Median µs | Elapsed Min/Max µs | Logical-Read-Deltas |
|---|---|---|---|---|
| EXACT | 0 | 0 | 0 / 4085 | ausschließlich 0 |
| VECTOR_SEARCH | 0 | 8185 | 4084 / 12252 | ausschließlich 0 |

Alle gemessenen Batches tatsächlich 50 Rows und 50 Oracle-Treffer. Restore beider
persistierten Baselines 0/0, neue Attestierung vor DB-Drop und separate SQL-DB-/
Containerabwesenheit bestanden; Cleanup 12,385 Sekunden, Prozesscode 0.
Ausgeführte Quellen und ursprünglicher Capture-PASS bleiben unverändert.

## Zweiter Kandidat: aktive Requestaufnahme

Zwei unveränderte Lifecycles bestanden. Je Pfad und Lifecycle fünf gemessene
Batches mit tatsächlich 50 Rows/50 Oracle-Treffern; Warm-ups ausgeschlossen.
CPU-Deltas positiv, Logical-Read-Deltas je gemessenem Batch EXACT 171 und
VECTOR_SEARCH 7551. Dies sind die beobachteten begrenzten Requestzähler einschließlich
Mess-/Speicheraufwand, keine vollständige Worker-IO oder isolierte Suchkosten.

| Lifecycle/Pfad, zehn Queries je Batch | CPU-Median (Min/Max) ms | Elapsed-Median (Min/Max) µs |
|---|---|---|
| 1 EXACT | 4 (2/4) | 0 (0/4084) |
| 1 VECTOR_SEARCH | 6 (6/7) | 8200 (4097/8417) |
| 2 EXACT | 3 (3/3) | 4112 (0/4126) |
| 2 VECTOR_SEARCH | 6 (6/6) | 8199 (4118/8248) |

Physische Reads und Writes in allen gemessenen Batches null; dies betrifft das
beobachtete Fenster, keine Garantie für andere Läufe. EXACT-Elapsed enthält in
beiden Lifecycles null; keine belastbare Speedupratio aus diesen quantisierten
Kleinstmessungen. Am festen kleinen Korpus ist kein ANN-Performancevorteil belegt.

Alle vollständigen Marker-/Baseline-/Source-/Metadaten-/Konfigurationskontrollen,
tatsächlicher Own-Index-Drop, Restores 0/0, neue Attestierung und separate DB-/
Containerabwesenheit bestanden. Cleanup 12,386/12,299 Sekunden, beide Prozesscode 0.
Zwei Kandidaten/drei Container insgesamt, Umfang regulär abgeschlossen. Kandidat01-
WARN bleibt erhalten; Generation UNKNOWN, neue Indexnutzung/DOP UNPROVEN.

## Quellen- und Prüfbindung

Kandidat 01: fünf bestehende Grenztests und zunächst fünf neue Messgegenproben
bestanden. Ein unabhängiger P2 zur falschen Queryminimumbezeichnung wurde vor SQL
korrigiert; sechs betroffene Tests und der enge Nachreview schlossen ihn.
Kandidat 02: 13 betroffene Grenz-/Messgegenproben bestanden; enger unabhängiger
Methoden-/Quellenreview vor SQL schloss ohne offene P1/P2. Ein Owner, ein erforderlicher
Reviewer; Modell-/Tokenverbrauch unbekannt. Rohwerte bleiben privat/unversioniert.

| Private Quelle unter ANN_MEASURE_CANDIDATE01 | SHA-256 |
|---|---|
| qualify_build.py | 72286DAD6FCBF69F0B734A861BA2A7EE62393923AEFA97C0072138E6356EE670 |
| sql_build.py | 4CD78F1DCD3A2C35D080F898BABDDE494533D60592BF7B43D17C9C2DA9A54056 |
| measure_evidence.py | 3958DD909B30F6F3727B9FFEF182D45A99462C5AEA0889E98650D1DEF0ABB666 |
| test_measure.py | 4B45F9EF9E25746E1079ACA1F1D2D2968C7CDD9942FF8CF67D79D9AEB9E8DE08 |
| lifecycle01.log | E16AE22C1A3323E1D8FCDC6CD085B56D739803552898FCAE8414A4C30B49A2FC |

| Private Quelle unter ANN_MEASURE_CANDIDATE02 | SHA-256 |
|---|---|
| qualify_build.py | A78C9744BCFF96CB413C1C7358B0E9AC49894425E9D0999976F01F91986271F7 |
| sql_build.py | 21CC3EAA13923A44B7B95BC57FA7F6B7C810C78A377F1F12936DA39D977CB93C |
| measure_evidence.py | 780F7D7FFC47D2694446E664E454EC6F9D2A1F124AFF3D533AA03B6B05C64B1B |
| test_measure.py | A7F7A2211FB603292FCBBC48D854E33782D3A9A65EDC7A666A6778347FB04CD2 |
| lifecycle01.log | FB50EEBE8CF77F516E88BE32C031C8E256E82BE583575F671938F44AEB4B0330 |
| lifecycle02.log | 0BC1263CE2ACD4B59526046488C3F4C591EF1B1FC87553F2303A6B2CC3295D5E |
