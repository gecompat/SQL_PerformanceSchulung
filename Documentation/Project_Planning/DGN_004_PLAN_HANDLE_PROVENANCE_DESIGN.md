# DGN-004: plan_handle-Herkunft und vollständige Cachekandidaten

Stand: 2026-11-13. Dieser begrenzte Methodenschnitt bearbeitet ausschließlich
die offene Frage, wie der vorhandene Plan-Capture-Transport einen
`plan_handle` an genau einen eigenen DGN-004-Nutzaufruf binden kann. Er enthält
keine ausführbare SQL-Änderung und keine Laufzeitaussage.

## Befund am vorhandenen Quellstand

`CapturePlanFrame.sql` nimmt einen 64-Byte-`plan_handle` entgegen und liest
damit `sys.dm_exec_query_plan_stats`. Der Wert wird lexical sicher geprüft,
aber vom Aufrufer geliefert. `dgn004_identity_snapshot.py` prüft
caller-gelieferte R/H-Quell-, Modul-, Cache- und Query-Store-Felder offline;
es bindet weder die Aufzählung sämtlicher Serverzeilen noch einen Planhandle.
Beide Komponenten warnen ausdrücklich vor diesem fehlenden Provenienznachweis.

## Quellenbasierter Kandidat

Microsoft beschreibt `sys.dm_exec_query_stats` als eine Zeile pro
Abfragestatement in einem gecachten Plan. Die Sicht enthält nur beendete
Abfragen; ihre Zeilen verschwinden mit dem Cacheplan. Sie stellt unter anderem
`plan_handle`, `sql_handle`, Statementoffsets, `plan_generation_num`,
`creation_time`, `last_execution_time`, `execution_count` und die
Query-/Planhashes bereit. `sql_handle` plus Start-/Endoffset bindet den
Statementtext über `sys.dm_exec_sql_text`. Der dokumentierte `plan_handle`
identifiziert dagegen den Plan des Batches beziehungsweise Moduls, nicht
allein ein Statement. [`sys.dm_exec_query_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver17)

Der vorgeschlagene Locator erfasst daher vor und unmittelbar nach genau einem
Nutzaufruf den vollständigen Satz der Cachezeilen, die durch Datenbank-ID,
Modul-ID, exakte Modulbytes und registrierte M/S/T-Statementoffsets begrenzt
sind. Er erhält jede Zeile, nicht nur einen Handle. Die beiden Snapshots werden
zeilenweise über `plan_handle`, `sql_handle`,
`statement_start_offset`, `statement_end_offset`, `plan_generation_num` und
`creation_time` verglichen. Diese zusammengesetzte Identität ist nötig, weil
ein `plan_handle` den Batchplan bezeichnet und die DMV mehrere Statementzeilen
für einen Plan enthalten kann. Doppelte zusammengesetzte Zeilenschlüssel machen
den Snapshot ungültig; sie dürfen nicht zusammengefasst werden. Für
die aktuelle Phase muss genau eine Zeile neu sein oder ihren
`execution_count` exakt um eins erhöht haben; alle weiteren Kandidaten müssen
unverändert sein. Null, mehrere geänderte Kandidaten, mehr als ein zusätzlicher
Aufruf, fehlende Zeilen oder ein unvollständiger Snapshot ergeben
`NOT_PROVEN` (nicht nachgewiesen), ohne `TOP`, Hash-Alleinauswahl oder
Fallback-Handle.

`sys.dm_exec_query_plan_stats` liefert für einen vorhandenen gecachten Handle
den letzten bekannten tatsächlichen Showplan. Der Funktionsaufruf kann null
oder einen vereinfachten Root-Plan liefern; ein Plan entsteht je Batch. Der
anschließende XML-Prüfer muss deshalb im Plan die exakt registrierte
R/H-Nutzstatementquelle, das Objekt und die zugehörigen Laufzeitinformationen
finden. Fehlender, veralteter, vereinfachter, mehrdeutiger oder nicht
vollständig transportierter Plan bleibt Nichtabnahme. [`sys.dm_exec_query_plan_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-stats-transact-sql?view=sql-server-ver17)

Der isolierte Ablauf benötigt einen vollständig erfassten Vorher-Snapshot,
genau einen vom Orchestrator markierten Aufruf und einen vollständigen
Nachher-Snapshot ohne konkurrierende Nutzaufrufe. `last_execution_time` und
die Plan-/Queryhashes sind ergänzende Kandidatenfelder, keine Identitätsschlüssel.
Die Planhashes und vollständige Struktur-/Objekt-/Prädikatevidenz dürfen nur
zusammen mit Datenbank, Objekt, Query-Store-Identität, exaktem Statementtext,
Offsets und der Snapshotdifferenz verwendet werden. [`sys.dm_exec_requests`](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-requests-transact-sql?view=sql-server-ver17)
stellt Session, Request und Planhandle für aktuell laufende Requests bereit;
die Werte sind teilweise nullable und sind kein Ersatz für den
Nachher-Snapshot eines bereits beendeten Nutzaufrufs.

## Grenzen und notwendige Reviewfragen

- Die Snapshots belegen vollständige Ergebnisse nur für die tatsächlich
  zurückgegebenen DMV-Zeilen und die konkret angewandten Filter. Die spätere
  Umsetzung muss nachweisen, dass Transport- und Zeilengrenzen keine
  Kandidaten abschneiden und dass die exakte R/H-Statementextraktion mit
  UTF-16-Offsets auf beiden festgelegten Builds übereinstimmt.
- `execution_count`-Delta ordnet eine zusätzliche Ausführung dem einzigen
  kontrollierten Aufruf nur unter dem isolierten Ein-Writer-Vertrag zu. Eine
  externe Ausführung, Zeitüberlappung, Statistikresets, Cacheeviktion oder
  Änderung der Planerzeugung muss fail-closed erkannt werden. Der Datensatz
  enthält keine eigene Invocation-ID; die Kausalzuordnung bleibt eine
  begrenzte Inferenz aus Isolation und Vorher-/Nachherzustand.
- Der Locator darf einen gefundenen Handle erst ausgeben, nachdem genau ein
  passender vollständiger Kandidat festgestellt wurde. Die Auswahl wird nicht
  anhand `query_hash`, `query_plan_hash`, `plan_handle`, Textfragment oder
  `TOP 1` allein getroffen.
- Der Inhalt von `query_plan` muss danach unabhängig gegen registriertes
  Statement, Query-Store-Planrolle und aktuelle Laufzeitmerkmale geprüft
  werden. Ein erfolgreicher Transport beweist weder Force-Erfolg noch
  Engineidentität, Kompilierungszuwachs oder vollständige Lifecycleabnahme.

Diese Strategie ist ein Kandidat, kein freigegebener Implementierungsvertrag.
Vor ausführbarer Umsetzung sind ein unabhängiger Methoden-/Quellenreview,
synthetische Fälle für Cache-Neuanlage, Delta 0/1/>1, konkurrierende
Kandidaten, Eviktion, Offset-/M/S/T-Abweichung, unvollständigen Snapshot und
falsche tatsächliche Statementrolle sowie ScriptDom-Prüfung erforderlich.
Vor SQL-Ausführung bleiben sämtliche YELLOW-, Ressourcen-, Rechte-,
Image-/Build- und Ausgangszustandsgates bindend. Am 2026-11-13 waren fünf
fremde SQL-Server-Container aktiv; ein read-only `docker stats`-Snapshot zeigte
für sie zusammen rund 5,6 GiB Speicher und etwa 5 % CPU. Das ist keine
kontrollierte Optimiererlast und keine Freigabe, diese Container zu verändern.
