# RES-008 – private Messfenster für vier Vektordimensionen

Stand: 2026-10-12, TSK-010/CUR-020. Basis
`a3bfb66fb032c292b604fa939d27a211ded19ecb`, Branch
`codex/sql2025-ai-res008-measurement`. RES-008 bleibt PROPOSED.
Der [vorherige Quellen-/Storagevorschnitt](SQL_SERVER_2025_AI_RESOURCE_DIMENSION_REVIEW.md)
ist über PR 185 vollständig integriert: sieben Head-/fünf Main-Workflows PASS,
vollständiger Tree `f7ce3e181fdfdba2c916e828061bdda2db76a8cd` übernommen,
lokales main FF-synchronisiert und sauber, eigene lokale/Remote-Branches entfernt.

## Fixierte Methode und tatsächliche Abdeckung

Unverändert wurden drei neue eigene serielle Container aus dem gecachten Image
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`
verwendet. Alle meldeten exakt SQL Server 17.0.5005.3; vier CPU, sechs GiB, Loopback,
300 Sekunden reguläres Gesamtbudget und dieselbe separate 60-Sekunden-
Cleanupdeadline ohne Reset. Die eigene CL170-/SIMPLE-Datenbank hatte
256/64-MB-Dateilimits, vier vollständig bytegenaue Eigentumsmarker und vier
float32-VECTOR-Tabellen mit jeweils 100 synthetischen Rows `[Id,1,0,...,0]`.
Datenbank-MAXDOP/PREVIEW_FEATURES blieben tatsächlich 0/0, nur Suchstatements
verwendeten OPTION(MAXDOP 1). Kein Cacheleeren oder Concurrencylauf.

Der stabile C2 bestand zwei vollständige Lifecycles. Je Lifecycle liefen
20 getrennte Warmuprequests, fünf für jede der Dimensionen 32, 384, 768 und 1536.
Anschließend folgten 54 getrennte Messrequests: Paare 32:384, 32:768 und 32:1536,
je drei Blöcke mit AB, BA und AA in fester Reihenfolge, jeweils zwei Slots
mit 100 Queries. Warmup und AA sind aus den A/B-Auswertungen ausgeschlossen.
Für jeden Pfad eines Paars ergeben sich sechs AB-/BA-Fenster; jede der
5420 tatsächlichen Queries musste einzeln Id 1 und Cosinedistanz 0 liefern.
Quelle und Setuporacles liefen getrennt; kein Cold-Cache-Claim.

Jeder Request erfasste seine tatsächliche Session-/Request-/Connection-/DB-
Identität einschließlich rohem DMV-Requeststart. Vorher-/Nachherzähler waren
exakt an dieselbe Identität gebunden, DB-ID separat gegen den eigenen Kontext
attestiert. CPU, Reads, LogicalReads und Writes sind tatsächliche monotone
Live-Request-Deltas; Elapsed folgt exakt den tatsächlichen datetime2(7)-UTC-
Fenstern. Alle 74 Requests waren eindeutig und zeitlich seriell. Der bounded
ASCII-Chunktransport verlangt vollständige Reihenfolge/Anzahl/Teil-/Gesamtlänge
vor JSON-Auswertung; öffentliche SQLCMD-Optionen und gemeinsame API unverändert.

## Beobachtete Fensterwerte

Jede Zelle enthält Median [Minimum–Maximum] aus sechs AB-/BA-Fenstern mit
je 100 Queries. Elapsed ist in Mikrosekunden, CPU in Millisekunden. Gemessen
wurde das gesamte SQL-Fenster mit temporärer Ergebnisablage, Schleife und
Countererfassung; Verbindung, Quellenaufbau und Ausgabe liegen außerhalb.
Diese kleinen Populationen begründen keine universelle Skalierungs- oder
Speedupaussage. Reads 0 und Millisekundenquantisierung bleiben Beobachtungen,
kein Beweis vollständiger Worker-I/O oder kostenloser Ausführung.
WARN: Lauf 1 enthält 3 und Lauf 2 1 vollständige Messfenster
mit tatsächlich Elapsed=0 trotz positiver CPU-Zähler. Diese Werte werden
weder verworfen noch durch Schätzungen ersetzt; die Timer-/Fenstergrenze
verhindert eine vollständige Zeit- oder Speedupabnahme.

| Lauf | Paar | Dimension | CPU ms | Elapsed µs | LogicalReads | Reads | Writes |
|---|---|---|---|---|---|---|---|
| 1 | 32:384 | 32 | 6.5 [6–7] | 4091 [4072–8231] | 615 [612–649] | 0 [0–0] | 1 [0–1] |
| 1 | 32:384 | 384 | 8.5 [8–12] | 8198.5 [0–12377] | 2415 [2415–2449] | 0 [0–0] | 1 [1–1] |
| 1 | 32:768 | 32 | 5 [5–6] | 6151.5 [4100–8219] | 615 [615–615] | 0 [0–0] | 1 [1–1] |
| 1 | 32:768 | 768 | 8.5 [7–10] | 8195 [4093–8234] | 5415 [5412–5446] | 0 [0–0] | 1 [0–1] |
| 1 | 32:1536 | 32 | 6 [6–7] | 8193 [4097–8487] | 615 [612–615] | 0 [0–0] | 1 [0–1] |
| 1 | 32:1536 | 1536 | 11 [10–13] | 12264 [8186–12311] | 10415 [10415–10449] | 0 [0–0] | 1 [0–1] |
| 2 | 32:384 | 32 | 6 [5–17] | 6143.5 [4092–16644] | 615 [612–649] | 0 [0–0] | 1 [0–1] |
| 2 | 32:384 | 384 | 8.5 [7–12] | 8228.5 [8198–12646] | 2415 [2415–2449] | 0 [0–0] | 1 [1–1] |
| 2 | 32:768 | 32 | 6 [6–7] | 8220 [4121–8272] | 615 [615–615] | 0 [0–0] | 1 [1–1] |
| 2 | 32:768 | 768 | 8.5 [8–13] | 8226.5 [8158–12616] | 5415 [5412–5446] | 0 [0–0] | 1 [0–1] |
| 2 | 32:1536 | 32 | 6 [6–7] | 4116.5 [4084–8194] | 615 [612–615] | 0 [0–0] | 1 [0–1] |
| 2 | 32:1536 | 1536 | 11 [11–54] | 12348.5 [8218–54776] | 10415 [10415–10449] | 0 [0–0] | 1 [0–1] |

Die folgenden AA-Paare bleiben tatsächliche einzelne Elapsed-Rohwerte in µs,
getrennt vom A/B-Median; beide Slots messen jeweils Dimension 32.

| Lauf | Paar | Block1 A/A | Block2 A/A | Block3 A/A |
|---|---|---|---|---|
| 1 | 32:384 | 4107/0 | 4089/8228 | 4100/8179 |
| 1 | 32:768 | 4103/8280 | 4096/8177 | 8174/8239 |
| 1 | 32:1536 | 8372/4085 | 4131/8309 | 4104/8196 |
| 2 | 32:384 | 8217/4099 | 8191/8210 | 8200/8333 |
| 2 | 32:768 | 4098/4090 | 8224/4111 | 8207/4095 |
| 2 | 32:1536 | 8213/4117 | 4117/0 | 4134/4095 |

## Gegenproben, FAIL und Recovery

Je Lifecycle entfernte eine tatsächliche DELETE-Gegenprobe eine eigene
Quellenrow, forderte exakt nativen 51003/FAIL_RESULT_CONTRACT und stellte alle
400 Quellen wieder her. Nach der Messung wurde zusätzlich eine tatsächlich
erzeugte temporäre Queryrow von Id 1 auf Id 2 geändert; exakt derselbe native
Resultfehler musste eintreten. Je vier vollständige 400-Row-Aufnahmen vor/nach
Setup, Restore und Benchmark waren gleich, auch über beide Wiederholungen;
Dimensionen, float32, Storage und DB-Konfigurationen wurden erneut erfasst.

C1 bleibt FAIL nach 20 positiven nativen Warmups und 31 nativen Messfenstern:
das 31. Messfenster scheiterte in Python am Vergleich groben DMV-datetime-
Requeststarts mit feinerem datetime2(7)-Fensterstart. Die tatsächliche
Zeitdifferenz 8262 µs war korrekt; der gerundete Identitätswert lag 679 µs voraus.
Kein vollständiger C1-Benchmark-PASS. C2 änderte ausschließlich diesen
unbegründeten Cross-Type-Zeitvergleich: rohe Requeststartidentität weiterhin
exakt/typgebunden, gleichartige Fensterdeltas und Nichtüberlappung unverändert.
Microsoft dokumentiert `start_time` als datetime und dessen gröbere Rundung:
[sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17),
[datetime](https://learn.microsoft.com/en-us/sql/t-sql/data-types/datetime-transact-sql?view=sql-server-ver17),
abgerufen am 2026-10-12. Identität und präziser Messzeitstempel werden getrennt behandelt.

Ein Owner, sechs Kandidaten/maximal zwölf serielle eigene Container. C1 zählt
weiter; beide grünen C2-Pflichtwiederholungen abgeschlossen, keine weitere
unveränderte Wiederholung. Enger unabhängiger Quellenreview schloss zwei P2
vor Admission (DB-Namenbindung und max-Scalartransport) sowie das C2-Zeitdelta.
Reviewer ohne Runtime/Tests; keine Performance- oder TP-PERF-Abnahme.
18 betroffene synthetische Evidenz-/Transport-/Zeitgegenfälle PASS; private
Vorbereitungsskript-/Testklassenfehler vor Admission korrigiert. Alle 14
Ausführungsabhängigkeiten und archivierten C1-/C2-Bytes sind tatsächlich gebunden.
Native Clientenden bekannt; tatsächlicher markergebundener SQL-Cleanup,
neue DB-Abwesenheit sowie vollständige CID-/Namensabwesenheit aller drei
eigenen Container unter derselben 60-Sekunden-Deadline bestanden.
C1 FAIL: Cleanup 12,8358 Sekunden.
C2 Lauf 1: Cleanup 13,3560 Sekunden.
C2 Lauf 2: Cleanup 13,2670 Sekunden.

Rohdiagnosen, Session-/Connection-/Containerwerte und vollständige Fenster-
JSONs bleiben privat ignoriert. Passwort nur Umgebung; keine andere Ressource
oder anderes Repository verändert. Keine Inferenz-/Provider-/Preview-/Host-
Wirkung, Modell-/Tokenverbrauch unbekannt. Öffentliche Änderungen betreffen
ausschließlich diesen Teilnachweis und kanonische Verweise; aktuelle Head-/
Main-Gates, Integration, Treeübernahme, Sync und eigener Cleanup folgen.

## Verbleibende Grenzen

Zero-Padding bewahrt diese Fixturegeometrie, belegt keine reale Modellkompression
oder semantische Qualität. Größere Profile, Pläne/Grants/Spills/Memory/Waits,
vollständige Worker-I/O, Loader-/Modelspacevertrag, ältere Engines und öffentlich
ausführbare Demo-/Negativ-/Recoveryqualifikation bleiben offen. Fehlende Werte
bleiben NOT_CAPTURED; tatsächliche Null-/Quantisierungs-/Messgrenzen bleiben WARN.
Keine vollständige TP-PERF- oder TSK-010-Abnahme, keine weitere Demoimplementierung.
Nächster zulässiger lokaler Schritt nach vollständig abgeschlossener Integration:
begrenzte RES-008-Plan-/Memoryaufnahme unter unveränderten Effektgrenzen.
