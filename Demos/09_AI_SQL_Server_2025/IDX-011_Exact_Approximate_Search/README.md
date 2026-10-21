# IDX-011 – Exact gegen Approximate Search

Implementierungsstand: öffentliche Quellen in Entwicklung, noch keine freigegebene
Demo und keine TP-PERF-Abnahme. Generation bleibt UNKNOWN. Ein technisch bestandener
Lauf erhält WARN_OPTIONAL_EVIDENCE_SKIPPED; fehlende Performanceevidenz wird nicht
durch einen grünen Controllerstatus ersetzt. Es gibt bewusst noch kein manifest.json:
der allgemeine FWK-010-Runner unterstützt die drei unabhängigen Recoveryclients
und den vollständigen JSON-/XML-Output dieses Profils nicht.

Das Lernziel ist der Vergleich von Exact Top-5 und approximate cosine-Suche auf
demselben synthetischen VECTOR(3)-Korpus. Jede Query muss fünf unterschiedliche IDs
mit tatsächlichen Distanzen liefern. Exact erfüllt die vollständige Ground Truth,
ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren) mindestens Recall@5 0,8. Die zusätzliche enge Postfilterprobe 501–510 liefert
im gebundenen Profil null ANN-Rows bei fünf Exact-Rows: dieser Qualitätsverlust
bleibt sichtbar. Ein schneller Lauf mit unzureichender Qualität ist kein Erfolg.

## Profil, Rechte und Sicherheit

[DEC-074 – Gebundenes ANN-Legacyprofil mit Generation UNKNOWN/WARN](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md)
begrenzt die Ausführung auf SQL Server 17.0.5005.3, Linux Ubuntu 24.04,
Developer/EngineEdition 3, Compatibility Level 170. SQL Server 2019 und 2022
liefern SKIP_VERSION vor Setup; andere 2025-Profile SKIP_CONFIGURATION mit
PROFILE_UNQUALIFIED. Keine Übertragung auf Azure oder eine numerische Generation.

Ein eigenes isoliertes, verfügbares Lab ist Voraussetzung. Der Controller
provisioniert nichts. SQLCMDPASSWORD wird ausschließlich über die Prozessumgebung
übergeben. Erforderlich sind CREATE DATABASE, Zugriff auf eigene DB-Kataloge und
DMVs (Dynamic Management Views; dynamische Verwaltungssichten für Diagnoseinformationen) sowie Rechte zum Erstellen, Konfigurieren und Löschen der eigenen Testdatenbank.
Das Qualifikationsprofil verwendet den eigenen Containeradministrator; eine
Minimalrollenabnahme bleibt offen. ODBC-sqlcmd muss bereits installiert sein.

Sicherheitsstufe YELLOW: beide Bestätigungen sind zwingend. Das lokale
Qualifikationsprofil ist auf vier Container-CPUs und sechs GiB begrenzt; der Host
muss diese Ressourcen zusätzlich zu seinem bestehenden Bedarf bereitstellen.
Eine Session, ausschließlich 1000 synthetische Quellenrows, kein Cacheleeren,
keine Hostoption, kein fremdes Objekt, kein Netzwerkprovider und kein Modellaufruf.
Datafile maximal 256 MiB, Logfile 64 MiB, Wachstum jeweils 16 MiB, SIMPLE.
Temporäre Ergebnisablage höchstens 500 Rows gleichzeitig. Regulärer Ablauf
höchstens 300 Sekunden; DB-Recovery separat höchstens 20 Sekunden. Beim lokalen
Qualifikationsrunner bleiben weitere 40 Sekunden des gemeinsamen 60-Sekunden-
Cleanupbudgets für vollständige Containerbindung, Removal und Abwesenheitsprüfung.

## Ausführung und Phasen

Nur der mitgelieferte Controller führt den vollständigen Ablauf aus. Beispiel
für ein zuvor bereitgestelltes eigenes Lab, nachdem SQLCMDPASSWORD außerhalb der
Kommandozeile gesetzt wurde:

```powershell
python Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search/run_profile.py `
  --server localhost,1433 --username sa --run-token ABCDEF0123456789 `
  --confirm-isolated-lab --high-impact-confirmed
```

Ein neuer Run benötigt einen neuen 16-stelligen Großbuchstaben-Hex-Token.
Die daraus abgeleitete eigene DB heißt SQLPERF_LAB_IDX011_<RunToken>.
Ein bereits vorhandenes Ziel wird vor Setup abgewiesen, auch bei passenden
Eigentumsmarkern. Diese strengere FWK-002-Abweichung verhindert eine versehentliche
Wiederverwendung; Recovery ist wiederholbar, vorhandene fremde Marker verbieten Drop.

1. 00_Preflight prüft Eingaben, Bestätigungen, tatsächliches Buildprofil, Rechte
   und die Abwesenheit des Zielnamens ohne Änderungen.
2. 10_Setup erstellt ausschließlich die eigene DB mit vier vollständigen
   Eigentumsmarkern und persistiert beide tatsächlichen Optionsbaselines.
   Ein neuer Client attestiert diese Baselines und die tatsächliche eigene DB-ID.
3. 11 und 12 aktivieren getrennt PREVIEW_FEATURES und MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad)=1 ausschließlich
   in der eigenen DB. Neue Clients vergleichen den vollständigen vorherigen
   Host-/Scoped-/Marker-/Baseline-/Options-/Dateistand mit der erlaubten Änderung.
4. 20_Baseline erzeugt Id 1–1000, deterministische float32-Vektoren, clustered
   INT-PK (Primary Key; Primärschlüssel), vollständigen eingefrorenen Quellenbestand und Exact-Oracle. Python
   prüft unabhängig alle Vektoren und Distanzen; keine Stichprobenabnahme.
   Für ausschließlich dieses gebundene Profil wird die dritte Koordinate vor
   float32 durch die rationale Ganzzahlrechnung floor(((Id*17)%97)*10^6/97)/10^6
   geprüft. Der erste vollständige Quellenoutput belegt diese sechsstellige
   Darstellung an allen 1000 Rows. Dies ist keine allgemeine Rundungsregel für SQL.
5. 30_Demonstration baut den eigenen DiskANN/cosine-Index mit MAXDOP=1.
   Buildzeit, vollständige Metadaten, repräsentativer tatsächlicher Suchplan,
   Ergebnisse und Filtergegenproben entstehen außerhalb des Benchmarks.
   Baseline-, Marker-, Quellen-, Typ- und Ergebnisgegenfixtures müssen scheitern.
6. 40_Observation wird in 28 frischen Requests gemäß dem eingefrorenen
   [Benchmarkvertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX011_BENCHMARK_CONTRACT.md)
   aufgerufen: zehn Warm-ups, anschließend drei AB-/BA-/AA-Blöcke mit je
   100 Queries pro Fenster. Ergebnisablage und Zähleraufnahme gehören zum Aufwand.
7. 50_Mitigation entfernt nur den vollständig gebundenen eigenen Index und
   wählt Exact als qualitätserhaltenden Fallback. 60_Comparison vergleicht die
   identischen Parameter und tatsächlichen Top-5-Distanzen mit dem ursprünglichen
   Exact-Oracle. Dies behauptet keinen Geschwindigkeitsvorteil.
8. Der finally-Pfad führt 90_Restore, 91_AttestDrop und 92_Absence in getrennten
   Clients aus, auch nach Fehler oder Ctrl+C. Vor Drop müssen beide tatsächlichen
   Optionen wieder ihren persistierten, extern festgehaltenen Baselines entsprechen.

## Recovery, Grenzen und Evidenz

Der gemeinsame normale Deadline begrenzt alle SQL-Phasen einschließlich
Beobachtungssnapshots; ein Timeout beendet den SQL-Clientprozessbaum vor Recovery.
Restorefehler oder unbekannte Baseline verhindern Drop. Die reine Abwesenheitsprobe
wird trotzdem versucht. FAIL_CLEANUP überlagert keinen historischen Fehler als PASS.
Bei bereits abwesender DB sind Recoverybatches idempotent; ALREADY_ABSENT ersetzt
im Controller keine verlorene tatsächliche Restore-/Dropattestation.

Bei hartem Prozess-/Hostabbruch kann finally nicht laufen. Mit dem ursprünglichen
Token und den tatsächlich festgehaltenen Baselines sind die drei Recoverybatches
in dieser Reihenfolge auszuführen; alle sqlcmd-Variablen aus phase_command müssen
unverändert gesetzt werden. Eine unbekannte Baseline darf nicht geraten werden.
Die öffentliche vollständige Hard-Abort-/Minimalrollenabnahme bleibt offen.

Der Controller zeigt ausschließlich normalisierte eigene synthetische Ergebnisse;
Rohoutput, Plan-XML (Extensible Markup Language; Format zur strukturierten Darstellung von Daten) und Geheimnisse werden nicht automatisch gespeichert. Vollständige
JSON-/XML-Spalten benötigen -y 0 ohne -W/-h; dies ist die begründete stärkere
FWK-010-Abweichung mit eigenen Gegenproben. Tatsächliche aktive Requestidentitäten,
Counterdeltas und UTC-Grenzen ersetzen keine vollständige Worker-I/O-, Such-DOP-,
Waits-, Memory-Grant- oder Spillabnahme. Fehlendes heißt NOT_CAPTURED oder UNPROVEN,
niemals Null. Ein tatsächlicher eigener Indexoperator beweist nur seine konkrete
repräsentative Query, keine generische Nutzung aller Mess- oder Filterqueries.

statement_metrics enthält ausschließlich rohe Showplanattribute des eindeutig
gebundenen repräsentativen Suchstatements: direktes MemoryGrantInfo, DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung) und
NonParallelPlanReason sowie die Struktur von Warnings/WaitStats. Fehlende Werte
bleiben null/NOT_CAPTURED; ein vorhandener DOP-Rohwert 0 wird nicht in 1
umgedeutet. Fehlende Warnings oder WaitStats belegen keine Spill-/Waitfreiheit.
Die tatsächlichen Werte zweier vorhandener Pläne stehen im
[Runtimebefund](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX011_RUNTIME_REVIEW.md).

Tests: `python Tests/Static/test_idx011_profile.py` prüft Controller-/Recovery-/
Quellengegenproben; `python Tests/Static/test_idx011_benchmark.py` prüft den
Benchmarkvertrag. `python Tests/Static/test_idx011_plan.py` prüft die begrenzte
repräsentative Planauswertung. Alle drei sind Offlineprüfungen und keine Runtimequalifikation.
Die lokale Versions-/Fehler-/Recoverymatrix wird im kanonischen
[Ausführungsstand](../../../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md)
geführt. Traceability: TSK-006, IDX-011, CUR-019, DEC-074, FWK-001–005/008–012,
TP-RUN und TP-PERF; offene Abnahmen bleiben offen.

## Quellen

Microsoft-Primärquellen und Abrufdatum 2026-10-11 stehen im
[Quellenregister](../../../Documentation/Research/SOURCE_REGISTER.md), insbesondere
CREATE VECTOR INDEX, VECTOR_SEARCH, sys.vector_indexes, VECTOR_DISTANCE und
sys.dm_exec_requests. Das konkrete Profil folgt zusätzlich den dokumentierten
lokalen Beobachtungen von DEC-074; ein beobachteter Build ist keine allgemeine
Produktgarantie.
