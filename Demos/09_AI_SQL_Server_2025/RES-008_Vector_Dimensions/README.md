# RES-008 – Vektordimensionen und Ressourcenbedarf

Status: PROPOSED; öffentlich ausführbares begrenztes float32-Profil.
Die vollständige Demo-, Versions-, TP-PERF- und Modulabnahme bleibt offen.

## 1. Lernziel

CUR-020/TSK-010: Vektordimension, tatsächlich belegten Storage und beobachtete
CPU-/I/O-/Zeit-/Planattribute bei gleicher synthetischer Population verbinden.

## 2. Fachliche Kernaussage

Größere Dimensionen verändern den Aufwand dieser Fixture. Die Nutzdatenrechnung
ersetzt keine tatsächliche Page- oder Memorymessung. Zero-Padding bewahrt hier
die Cosinegeometrie; es ist kein Nachweis für Modellkompression oder semantische
Qualität. Zeitquantisierung und fehlende Beobachtung bleiben sichtbar.

## 3. Evidenzklasse und Plattform

Das Profil erfasst tatsächliche eigene SQL-Requestdeltas und vier repräsentative
Actual-Pläne. Unterstütztes Entwicklungsprofil: SQL 17.0.5005.3, Enterprise
Developer, CL 170, float32. SQL 2019/2022 enden vor Setup mit SKIP_VERSION;
andere 2025-Builds mit SKIP_CONFIGURATION. Keine float16-/Preview-/ONNX-Inferenz.

## 4. Voraussetzungen

Dediziertes isoliertes SQL-Lastlab, sysadmin für Setup/SHOWPLAN und tatsächliche
DMV-Sichtbarkeit, Python 3.12 oder neuer und Microsoft sqlcmd. Der Aufrufer
provisioniert die Instanz. Qualifikationsprofil: vier CPU/sechs GiB für den
eigenen Container, zusätzliche Hostreserven; die Instanz darf verworfen werden.
Nur eine Session gleichzeitig. Datenbank SQLPERF_LAB_RES008_LOCAL muss zunächst
fehlen. SQLCMDPASSWORD ist ausschließlich eine Umgebungsvariable.

## 5. Sicherheits- und Abbruchrahmen

YELLOW: `--confirm-isolated-lab` und `--high-impact-confirmed` sind erforderlich.
Maximal 300 Sekunden regulär, separate 60 Sekunden für Cleanup. Eigene Daten-/
Logdateien maximal 256/64 MB, vier Tabellen mit je 100 Rows; kein globales Cache-
leeren, keine Instanz-/DB-MAXDOP-/Previewänderung. Statements verwenden MAXDOP 1.
Native Requests haben maximal 30 Sekunden und vollständige Ausgabe höchstens 1 MB.
Ctrl+C beendet den eigenen Client; Recovery erst nach bekanntem Clientende.
Unbekannter Endstatus sperrt alle weiteren SQL-Aufrufe und ergibt FAIL_CLEANUP.

## 6. Synthetisches Datenmodell

Vier float32-VECTOR-Populationen mit Dimension 32/384/768/1536 und jeweils 100
Rows `[Id,1,0,...,0]`, Id 1 bis 100. Fester Queryvektor `[1,1,0,...,0]`;
jede Suchabfrage muss genau Id 1 mit Cosinedistanz 0 liefern. Vollständige Quellen-
SHA2_256/Längen/IDs, Dimensionen/Precision und tatsächliche Storagepages werden
vor und nach Setup, Restore, Messung und Planaufnahme geprüft.

## 7. Ablauf

`run_profile.py` steuert den festen Lifecycle. Die einzelnen SQL-Dateien sind
keine frei kombinierbare Produktionseingabe. Es gibt noch kein FWK-010-Manifest;
der Controller verwendet dessen globale Phasen-/Cleanupbudgets und die öffentlichen
sqlcmd-Prozess-APIs. Abweichung: Request-/Planoracles erfolgen im Controller;
kein Manifest behauptet eine vollständige TP-PERF-Qualifikation.

### 7.1 Schritt-für-Schritt-Anleitung

1. Eigenes isoliertes Lab bereitstellen und SQLCMDPASSWORD sicher in dessen
   Prozessumgebung setzen. Aus dem Repositoryroot starten:

   ```powershell
   python Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/run_profile.py `
     --server '<eigener Labendpoint>' --username sa `
     --confirm-isolated-lab --high-impact-confirmed
   ```

2. Der Controller prüft unabhängige Zielabwesenheit, Version, Rechte und Safety.
   Bei erforderlichem SKIP folgen weder Setup noch Lastphasen.
3. Setup und zweites idempotentes Setup erzeugen dieselben 400 Quellen. Eine
   tatsächliche DELETE-Gegenprobe muss nativen 51003 liefern; Setup stellt die
   vollständige Population wieder her.
4. Fünf eigene Warmuprequests je Dimension folgen getrennt. Danach 54 serielle
   Messrequests: Paare 32:384/32:768/32:1536, je drei Blöcke mit AB, BA und AA,
   jeweils zwei Slots und 100 Queries. Warmup und AA gehören nicht zum A/B-Median.
   Jedes der 5420 Ergebnisse wird einzeln geprüft. Identität und Delta sind an
   dieselbe tatsächliche Session/Request/Connection und separat attestierte DB-ID
   gebunden; grober DMV-Identitätsstart ist kein feiner Messzeitstempel.
5. Eine tatsächliche Mutation einer erzeugten temporären Queryrow muss 51003
   liefern. Danach vier feste Actual-Pläne mit Quellen-/Root-/Threadbindung
   aufnehmen und vollständige Quellen sowie DB-Konfiguration erneut vergleichen.
6. Markergebundenes Cleanup und neue unabhängige DB-Abwesenheit abschließen.
   Erwartet: WINDOWS_74, PLANS_4, CLEANUP_True und WARN_OPTIONAL_EVIDENCE_SKIPPED.
   WARN bezeichnet die begrenzte Beobachtung; FAIL darf nicht als WARN gelten.

Der öffentliche Aufruf schreibt weder vollständige Quellen noch Rawoutput,
Pläne oder Diagnosewerte auf Datenträger. Ergebnisse liegen während des Aufrufs
im Speicher; die CLI zeigt standardmäßig Counts/Status. Optional `--summary`
zum obigen Aufruf hinzufügen: erst nach positivem bekanntem Abschluss und Cleanup
folgt ein JSON-Frame `RES008_AGGREGATE` mit geprüften aggregierten Zahlen und
30 numerischen FWK-011-Assertions. Keine Rawidentitäten, Request-/UTC-/Connection-
werte, Querytexte, Quellen-/Planstrings oder XMLs werden ausgegeben.

Die Auswertung trennt 20 Warmups und AA von den sechs A/B-Batchfenstern je Pfad
und Paar. Median/Min/Max/n/Nullzählung enthalten auch Ausreißer; Nullbaseline
ergibt N/A (`null` im JSON), keine Division. Jeder Batch enthält 100 Queries.
CPU/I/O stammen aus eigenen Request-Counters vor/nach der Schleife einschließlich
des Overheads an diesen Messgrenzen. Elapsed umfasst die UTC-Zeit der Schleife
einschließlich Tempresult-Inserts; beide Messgrenzen sind nicht identisch.
Sechs Batchfenster
belegen keine individuellen Querylatenzen, belastbare Tails oder Signifikanz.
Vier repräsentative Planrecords liefern ausschließlich rohe numerische
Memory-/DOP-Attribute; fehlend bleibt `null`, roher DOP 0 bleibt 0.

Die drei [Expected-Verträge](Expected/RES008_D384.result-contract.json) prüfen
je zehn feste EXACT/FAIL-Invarianten zu Quellen, Vektorbytes und vollständiger
Query-/Fensterabdeckung. FWK-011-PASS für diese Invarianten verändert weder
Gesamt-WARN noch PROPOSED oder die offene volle TP-PERF-/Demo-/Modulabnahme.
[Gebundener Aggregationsnachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md).

## 8. Erwartete Beobachtung

Vier vollständige Source-/Storageprofile; je Plan eigener Clustered Index Scan
mit 100 tatsächlichen Rows und direkter Ergebnisroot mit einer Row. Tatsächliche
Memoryattribute bleiben roh; fehlende Wait-/Warning-/Operatorattribute bleiben
NOT_CAPTURED. Roh-DOP 0 bedeutet keinen gemessenen Workerwert 1. Elapsed 0 trotz
positiver CPU ist eine sichtbare Messgrenze, kein Geschwindigkeitserfolg.

## 9. Gegenmaßnahme und Vergleich

Dimension 32 bildet A, größere Dimension B. AB/BA vergleichen dieselbe Frage-
geometrie, AA macht Baselinevarianz sichtbar. Kleinere Dimension oder anderer
Typ sind erst nach eigener Modellqualitätsprüfung eine mögliche Gegenmaßnahme.
Hier erfolgt keine reale Modelltrunkierung oder behauptete Speedup-Abnahme.

## 10. Cleanup und Wiederherstellung

Der Controller prüft vor Drop alle vier vollständigen bytegenauen Eigentumsmarker.
DB-MAXDOP/PREVIEW_FEATURES bleiben 0/0; keine Instanzoption verändert. Nach bekanntem
Abbruchende darf die eigene Datenbank markergebunden erneut bereinigt werden:

```powershell
sqlcmd -S '<eigener Labendpoint>' -U sa -C -b `
  -i Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/90_Cleanup.sql `
  -v DemoId=RES-008 RunToken=LOCAL TargetDatabase=SQLPERF_LAB_RES008_LOCAL
sqlcmd -S '<eigener Labendpoint>' -U sa -C -b `
  -i Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/91_Absence.sql
```

Bei fehlenden oder falschen Markern abbrechen und den tatsächlichen Zustand
prüfen. Kein Drop anhand des Namens. UNKNOWN benötigt erst unabhängig bestätigtes
Ende des eigenen Clients; keine automatisierte Folgemutation. Der Controller
entfernt keine vom Aufrufer provisionierten Container oder fremden Sessions.

## 11. Tests

Reine XML-/Transport-/Controllergegenfälle stehen unter Tests/Static/test_res008_*.
Sie prüfen keine echte SQL-Ausführung. Quellen-, Mess- und Planteilnachweise:
[Dimensionen](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_DIMENSION_REVIEW.md),
[Messung](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_MEASUREMENT_REVIEW.md),
[Pläne](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_PLAN_REVIEW.md).
Die neue öffentliche Consumerqualifikation, aktuelle Head-/Main-Gates und
Integration werden getrennt nachgewiesen; historische FAILs bleiben erhalten.

## 12. Grenzen

Kleine synthetische Population, feste Version und Ressourcen. Vollständige
Worker-I/O, Waits/Spills/TempDB, größere Profile, Loader-/Modellqualität,
vollständige FWK-/TP-PERF-/Demo-/Versionsabnahme offen. Die begrenzte Aggregation
prüft ausschließlich den dokumentierten Teilumfang.
Keine Inferenz, Cloud-, Bezahl-API, ONNX oder rote Hostwirkung.

## 13. Quellen

Microsoft Learn, abgerufen 2026-10-12:
[VECTOR](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17),
[sys.columns](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-columns-transact-sql?view=sql-server-ver17),
[sqlcmd](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17),
[sys.dm_exec_requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17),
[datetime](https://learn.microsoft.com/en-us/sql/t-sql/data-types/datetime-transact-sql?view=sql-server-ver17).
Projektverträge: FWK-001/002/003/004/005/008/010/011/012.

## 14. Traceability

RES-008, CUR-020, TSK-010, DEC-073; begrenzte TP-RUN-/TP-PERF-Entwicklung.
Die vorhandene registrierte Kennung bleibt erhalten. PROPOSED wird nicht durch
einen einzelnen PASS oder die Verfügbarkeit dieses Controllers aufgehoben.
