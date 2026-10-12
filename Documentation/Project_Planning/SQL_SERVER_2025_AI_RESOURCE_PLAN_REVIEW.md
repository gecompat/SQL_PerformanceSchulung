# RES-008 – repräsentative tatsächliche Pläne und Memoryattribute

Stand: 2026-10-12, TSK-010/CUR-020. Basis
`e8fb5d801464e5e2acb37fdeef5f7d203c048cb3`, Branch
`codex/sql2025-ai-res008-plans`. RES-008 bleibt PROPOSED.
Die [private Messfolge](SQL_SERVER_2025_AI_RESOURCE_MEASUREMENT_REVIEW.md)
ist über PR186 vollständig integriert: sieben aktuelle Head-/fünf Main-Workflows
PASS, vollständiger Tree `e0ab4de7a0cca55a92bdc91909dfebdc469cc47f`
übernommen, lokales main FF-synchronisiert und sauber, eigene lokale/Remote-Branches
entfernt. Frühere Quellen- und Mess-FAILs bleiben in ihren Nachweisen erhalten.

## Fixiertes Profil und tatsächlicher Nachweis

Ein Owner, sechs Kandidaten und höchstens zwölf serielle eigene Container.
Drei Container aus dem gecachten Image
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`
meldeten exakt SQL 17.0.5005.3. Unverändert vier CPU/sechs GiB, Loopback,
Passwort nur Umgebung, 300 Sekunden reguläres Gesamtbudget und dieselbe separate
60-Sekunden-Cleanupdeadline ohne Reset. Eigene CL170-/SIMPLE-Datenbank mit
256/64-MB-Dateilimits, vollständigen bytegenauen Eigentumsmarkern und vier
float32-Populationen mit je 100 Rows `[Id,1,0,...,0]` in Dimension 32/384/768/1536.
DB-MAXDOP/PREVIEW_FEATURES tatsächlich 0/0; nur Statement-OPTION(MAXDOP 1).

Der stabile C2 bestand zwei vollständige Lifecycles. Je Dimension wurde ein
fester Exact-Cosine-Top1-Request unter STATISTICS XML ON/OFF in der eigenen
Session ausgeführt. Die tatsächliche eigene zweispaltige Ergebnisrow musste
genau Id 1/Distanz 0 liefern. Das vollständige tatsächliche XML war an Build,
Namespace und exakten Statementtext gebunden, höchstens 120k UTF8 und 100 Operatoren;
DOCTYPE/ENTITY, unvollständige oder mehrdeutige Pläne wurden abgewiesen.
Der einzige direkte Planroot musste mit eindeutigen numerischen Thread-IDs
tatsächlich eine Row melden. Der unmittelbar zugeordnete eigene
DB-/Schema-/Tabellenscan musste tatsächlich 100 Rows liefern.

In allen acht tatsächlichen Plänen war Node 0 Sort/TopN Sort mit 1 tatsächlicher
Row, Node 1 Compute Scalar ohne erfasste RuntimeRows und Node 2 eigener Clustered
Index Scan mit 100 tatsächlichen Rows. Fehlende Compute-Scalar-Zähler bleiben
NOT_CAPTURED, keine Null. Roher Statement-DOP war 0, NonParallelPlanReason
`MaxDOPSetToOne`; DOP 0 wird nicht als gemessener Workerwert 1 umgedeutet.
Die Pläne gelten ausschließlich den vier repräsentativen Statements je Lauf,
nicht den 54 Messfenstern oder allen 5420 Queries des vorherigen Messschnitts.

## Tatsächliche Memoryattribute

Alle folgenden Zahlen sind rohe Showplanattribute (`RAW_SHOWPLAN_ATTRIBUTES`),
keine zusätzliche Umrechnung oder geschätzte instanzweite Memorynutzung.
Je Plan waren SerialRequiredMemory 16, SerialDesiredMemory 24 und
LastRequestedMemory 0 tatsächlich erfasst. Warnings und WaitStats waren in
allen acht Plänen NOT_CAPTURED/None; daraus folgt kein Nachweis fehlender
Spills oder Waits. GrantWaitTime 0 ist dagegen ein tatsächlich erfasstes Attribut.

| Lauf | Dimension | RequiredMemory | DesiredMemory | RequestedMemory | GrantedMemory | MaxUsedMemory | GrantWaitTime | MaxQueryMemory |
|---|---|---|---|---|---|---|---|---|
| 1 | 32 | 16 | 24 | 1024 | 1024 | 16 | 0 | 758840 |
| 1 | 384 | 16 | 24 | 1024 | 1024 | 16 | 0 | 758840 |
| 1 | 768 | 16 | 24 | 1024 | 1024 | 16 | 0 | 758840 |
| 1 | 1536 | 16 | 24 | 1024 | 1024 | 16 | 0 | 758840 |
| 2 | 32 | 16 | 24 | 1024 | 1024 | 16 | 0 | 755016 |
| 2 | 384 | 16 | 24 | 1024 | 1024 | 16 | 0 | 755016 |
| 2 | 768 | 16 | 24 | 1024 | 1024 | 16 | 0 | 755016 |
| 2 | 1536 | 16 | 24 | 1024 | 1024 | 16 | 0 | 755016 |

## FAIL, Gegenproben und Cleanup

C1 bleibt FAIL: Die ursprüngliche Stringframeprojektion erzeugte einen äußeren
Compute-Scalar-Root ohne erfasste RuntimeRows. Ein innerer TopN Sort meldete 1
und der eigene Scan 100 Rows; das genügte nicht für den strengen Ergebnisrootnachweis.
Nach dem ersten Plan wurde angehalten; die übrigen drei Planrequests liefen nicht.
C2 änderte ausschließlich die repräsentative Projektion auf direkte Id/DistanceValue
und deren exakte Statement-/native Rowauswertung. Root-/Scan-/Threadguards
blieben erhalten; kein Ersatz durch beliebige innere Einrowoperatoren.

Vor Admission schloss der enge unabhängige Quellenreview konkrete P2 zu
Thread-/Rootbindung und zum C2-Ergebnisparser. Dieser erfasst alle Datenframes
außerhalb des vollständigen XML-Blocks, nimmt nur bekannte einmalige Header,
gebundene Trennlinien und den festen PASS-Summary aus und verlangt genau eine
strikt gültige Ergebnisrow. Zusätzliche NULL-, fehlerhafte oder dreispaltige
Rows werden abgewiesen. 24 betroffene synthetische XML-/Kontext-/Oraclegegenfälle
PASS; synthetische Fixtures sind keine tatsächliche SQL-Evidenz. Reviewer
ohne Tests oder Runtime. Alle 15 tatsächlichen Ausführungsabhängigkeiten sind
bytegebunden; C1-Bytes vor Korrektur und C2-Bytes vor Veröffentlichung archiviert.

In jedem Lifecycle entfernte eine tatsächliche DELETE-Gegenprobe eine eigene
Quellenrow, forderte exakt nativen 51003/FAIL_RESULT_CONTRACT und stellte alle 400
Quellen wieder her. Elf vollständige 400-Row-Aufnahmen über C1 und beide C2-Läufe
waren gleich; tatsächliche Dimensions-/Storage-/Such-/Konfigurationsdaten
erneut geprüft. Kein zusätzlicher nativer Planmutations- oder Enginefehlerclaim.
Alle acht gespeicherten positiven Planrecords sind mit vollständigen nativen
Rawframes exakt abgeglichen. Zweites Setup idempotent, vollständige Quellen und
DB-Optionen nach allen vier Planrequests unverändert.

Native Clientenden bekannt; markergebundener SQL-Cleanup, unabhängige neue
DB-Abwesenheit sowie vollständige CID-/Namensabwesenheit aller drei eigenen
Container unter derselben 60-Sekunden-Deadline bestanden.

- C1 FAIL: 12 native Calls, Cleanup 12.8819 Sekunden.
- C2 Lauf 1: 16 native Calls, Cleanup 13.1646 Sekunden.
- C2 Lauf 2: 16 native Calls, Cleanup 12.9237 Sekunden.

Private Rohdiagnosen, vollständige XMLs, dynamische Index-/Containerwerte und
Ledger bleiben ignoriert. Keine Cloud-/Modell-/Preview-/ONNX-/rote Hostwirkung,
kein anderes Repository verändert; Modell-/Tokenverbrauch unbekannt.
Keine weitere grüne Wiederholung. Aktuelle Head-/Main-Gates, PR/Integration,
vollständige Treeübernahme, FF-Sync und eigener Branchcleanup folgen vor Abschluss.

## Verbleibende Grenzen

Größere Profile, vollständige Worker-/I/O-/TempDB-/Wait-/Spillbeobachtung,
Loader-/Modellqualität, ältere Engines und öffentliche Demo-/Negativ-/Recovery-
qualifikation bleiben offen. Keine vollständige TP-PERF- oder TSK-010-Abnahme,
keine weitere Demoimplementierung. Zero-Padding ist weiterhin ausschließlich
synthetische Geometrie; die Zeit-/Quantisierungs-WARNs der Messfolge bleiben sichtbar.
Nächster zulässiger lokaler Schritt nach vollständiger Integration:
begrenzte öffentliche RES-008-Demoqualifikation mit getrennten Performancegrenzen.
