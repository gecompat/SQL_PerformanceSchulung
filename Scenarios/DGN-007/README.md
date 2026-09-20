# DGN-007 – Implementierungsschnitt A/B (Adapter und statischer Teilnehmerfluss)

| Merkmal | Wert |
|---|---|
| Status | `IMPLEMENTED_STATIC_SLICE_B` (Schnitt A-Adapter und statischer Teilnehmerfluss) |
| Stand | 2026-09-19 |
| Arbeitspaket | `LABSCN-005` |
| Task | `TSK-002` |
| Detailreview | [`LABSCN_005_DGN_007_DETAIL_REVIEW.md`](../../Documentation/Project_Planning/LABSCN_005_DGN_007_DETAIL_REVIEW.md) |
| interaktive Zielversion | SQL Server 2025 / Compatibility Level 170 |
| Safety | `YELLOW`, ausschließlich isolierte Wegwerfinstanz |

## Umfang dieses Schnitts

Schnitt A implementiert den Project Adapter `0.1` mit:

1. **Datenaufbau** (`DGN-007_DATA_MODEL`): die markergebundene Testdatenbank
   `SQLPERF_LAB_DGN007_LOCAL` mit den neutralen Objekten `dbo.CaseGroup`,
   `dbo.CaseItem`, `dbo.CaseItemDetail`, `dbo.CaseRequestLog` und der
   markierten Suchprozedur `dbo.usp_CaseSearch`. Die Verteilung entsteht
   deterministisch ohne Zufallswerte: vier häufige, drei mittlere und fünf
   seltene Gruppen. Die Gruppen 1–4 enthalten jeweils 4.000, 5–7 jeweils
   2.000 und 8–12 jeweils 400 `CaseItem`-Zeilen. Nummernbereiche und
   Modulo-Ableitungen ergeben insgesamt 24.000 Faktzeilen; `n % 7`
   bestimmt den Status. Jeder Faktzeile sind drei Detailzeilen zugeordnet.
2. **Query-Store-Fenster** (`DGN-007_QUERY_STORE_WINDOWS`): Query Store in
   `READ_WRITE` mit begrenztem Capture- und Größenvertrag (128 MB,
   1-Minuten-Intervalle, `MAX_PLANS_PER_QUERY=20`, `QUERY_CAPTURE_MODE=ALL`
   für die kurzen synthetischen Aufrufserien), Baselinefenster
   `T0_BASELINE` und markiertes Incidentfenster `T1_INCIDENT`. Beide Phasen
   bleiben mit Beginn und Ende in `lab.IncidentState` erhalten.
   `lab.IncidentQueryStoreProfile` speichert die zugehörigen Query-, Plan-
   und Intervall-IDs sowie Ausführungsanzahl und Ausführungszeitgrenzen.
3. **Incident-Erzeugung** (`DGN-007_INCIDENT_GENERATION`): kontrollierte
   Ausführungsreihenfolge der markierten Prozedur mit häufigen, mittleren und
   seltenen Parameterwerten. Die Cacheisolation bleibt objektgebunden; globale
   Cacheleerung bleibt verboten.

Der Adapter führt in T0 drei Aufrufe mit Gruppe 8/Status 3 aus. T1 enthält
drei Aufrufe mit Gruppe 1/Status 3 sowie je einen Aufruf mit Gruppe 5/Status 3
und Gruppe 1/Status 1. Zwischen den Phasen wartet er auf das Ende des letzten
tatsächlich belegten Baseline-Intervalls. Die Prüfung erfolgt im
Sekundentakt mit einer Grenze von 90 Sekunden. Ein Flush persistiert
Query-Store-Daten; er erzwingt keinen Intervallwechsel. Fehlt die erfasste
Ausführungsanzahl oder überlappen die belegten Intervalle, bricht der Aufbau
mit `SKIP_EVIDENCE_MISSING` ab. Ein Setup kann durch die Intervalltrennung
etwa eine zusätzliche Minute benötigen.

`validate` akzeptiert nur Profile des markierten SELECT in
`dbo.usp_CaseSearch`, die über Query-, Plan- und Intervall-ID mit echten
Query-Store-Runtime-Daten verbunden sind. Mehrere Runtimezeilen eines
aktiven Intervalls werden nach Plan und Intervall aggregiert; berücksichtigt
werden ausschließlich erfolgreiche Ausführungen (`execution_type=0`).
Die Zuordnung verwendet die Überschneidung des belegten Query-Store-Intervalls
mit `MarkerUtc`/`CompletedUtc`, die exakte Aufrufanzahl und die getrennten
Intervall-IDs der Phasen. `first_execution_time` und `last_execution_time`
bleiben Diagnosewerte; sie werden nicht gegen millisekundengenaue
Phasenmarker gefiltert. Die Korrektur vom 2026-09-20 behandelt damit einen
beobachteten Runtime-Zeitstempel knapp nach `CompletedUtc`, ohne eine
Zeittoleranz einzuführen. Gemeinsame Intervalle bleiben unzulässig.
Diese Vorbedingung belegt die zeitliche Zuordnung, noch keine gemessene
Regression oder erfolgreiche Mitigation. Ein XE-Ringbuffer ist für diese
Vorbedingung nicht erforderlich und wird hier nicht eingerichtet.

Die Query-Store-Semantik wurde am 2026-09-19 gegen
[`sys.query_store_runtime_stats`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[`sys.query_store_runtime_stats_interval`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-interval-transact-sql?view=sql-server-ver17)
und [`sp_query_store_flush_db`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17)
geprüft. Die Umsetzung benötigt einen eigenen Runtime-Nachweis.

Schnitt A integriert außerdem das Szenario in das
Orchestrierungsmodul `PerformanceTrainingScenario.psm1` und den zugehörigen
statischen Validator, ohne die Lifecycle-Abnahme der bisherigen vier Slices
zu verändern.

## Schnitt-B-Erweiterung und Statusgrenze

Schnitt B ergänzt den Adapter um einen statischen, nicht promotenden
Teilnehmerfluss mit sechs dokumentierten SQL-Stufen. Dieser Ablauf wird auf
einer frischen SQL-Server-2025-Linux-Instanz über Docker oder Podman
ausgeführt, verlangt je Stufe eine `SQLPERF_SUMMARY|PASS|OK`-Zeile und räumt
Teilnehmerartefakte, Adapterdatenbank und Lab auch bei Fehlern im
`finally`-Pfad zurück. Er ist ein Qualitäts- und Lehrablauf, aber kein
interaktiver Szenariovertrag.

Der Adapter und der statische Teilnehmerfluss unterstützen ausschließlich SQL
Server 2025 auf Docker oder Podman. SQL Server 2019 und 2022 sind daher keine
alternativen Zielversionen; ein Preflight endet dort erwartungsgemäß mit
`ADAPTER_UNSUPPORTED_SQL_VERSION`.

Die aktuelle Fassung wurde am 2026-09-19 auf frischen Linux-Läufen geprüft. Der
Harness ist ein statischer Qualitätslauf; seine automatische Entfernung ist
kein interaktiver Übergabepunkt:

| Provider | RunId | Ergebnis |
|---|---|---|
| Docker | `ea802c20-4820-4007-a441-43a74a89c8fc` | `PASS`, anschließend `REMOVED` |
| Podman | `fba84720-5f0b-4537-bc98-75bbad37a85b` | `PASS`, anschließend `REMOVED` |

Die Nachweise belegen Adapter-Install/Validate, Preflight, Baseline,
Evidenz, reversible Mitigation, Vergleich, Teilnehmer-Cleanup,
Adapter-Cleanup und Lab-Remove sowie die Docker-/Podman-Parität. Sie belegen
keine vollständige interaktive Lifecycle-Matrix.

Die interaktive `scenario.json` ist bewusst **nicht** Bestandteil dieses
Schnitts: Für eine Promotion verlangt der Szenario-Inventar-Validator für jede
`Scenarios/*/scenario.json` einen vollständigen Inventareintrag mit
`VALIDATED`-Demo-Contract und Runtime-Manifest. Beides folgt erst mit der
Runtime-Matrix (Schnitt C). Es existieren deshalb weiterhin weder
`scenario.json` noch ein Szenario-Manifest oder Inventareintrag für DGN-007.
Der statische Teilnehmerfluss darf nicht als `READY_FOR_USER`-Übergabe oder
als interaktive Promotion interpretiert werden.

Eine Statusanhebung über den statischen Schnitt hinaus erfordert konkrete
Laufnachweise gemäß
[`DEMO_CONTRACT.md`](../../.ai/DEMO_CONTRACT.md).

## Vertragsmarker

- Datenbank- und Eigentumsmarker: `SQLPERF.Project`, `SQLPERF.ContractVersion`,
  `SQLPERF.DemoId`, `SQLPERF.RunToken`
- Incidentphasen: `T0_BASELINE`, `T1_INCIDENT` (in `lab.IncidentState`)
- Neutrale Querymarkierung: `DGN007_CASE_SEARCH`; persistierte
  Phasenzuordnung in `lab.IncidentQueryStoreProfile`
- Kontrollierte Abbruchausgänge: `SKIP_QUERY_STORE_REQUIRED`,
  `SKIP_INCIDENT_NOT_REPRODUCED`, `SKIP_EVIDENCE_MISSING`
- Kein `OPTION (RECOMPILE)`, keine Query-Store-Hints, keine erzwungenen Pläne
  und keine Event-Session in diesem Schnitt

## Lifecycle

Der Adapter besitzt die vier verbindlichen Entrypoints `preflight`, `install`,
`validate` und `cleanup`. `install` endet mit `READY_FOR_USER`; `cleanup` ist
markergebunden und entfernt Datenbank inklusive Query-Store-Zustand
vollständig. Reset und Remove folgen dem standardisierten Lifecycle aus
[`INTERACTIVE_SCENARIO_LIFECYCLE.md`](../../Documentation/HowTo/INTERACTIVE_SCENARIO_LIFECYCLE.md).

## Historische Adapter-Lifecycle-Abnahme (2026-09-14)

Die vollständige Adapter-Lifecycle-Abnahme lief über
`Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1` mit
`-ScenarioId DGN-007` je Provider auf SQL Server 2025:

| Provider | RunId | Start | Reset | Remove |
|---|---|---|---|---|
| Docker | `9ac100f8-f24f-420e-949c-943e35b9bcda` | `READY_FOR_USER` | `READY_FOR_USER` | `REMOVED` |
| Podman | `e06e9ec9-d239-4cd0-b9a7-0050dc574180` | `READY_FOR_USER` | `READY_FOR_USER` | `REMOVED` |

Beide Läufe bestätigten install (Datenaufbau, 24.000 Faktzeilen, Incident-Marker
`T1_INCIDENT`) und validate (Query Store `READ_WRITE`, zwei erfasste
Query-Pläne). Sie waren ein Adapter-Lifecycle-Nachweis für den damaligen
Schnitt-A-Stand und keine interaktive Promotion. Der Podman-Lauf ließ die
vorhandene, nicht zum Run gehörende Altressource unverändert.

Die Laufnachweise vom 2026-09-14 gelten für den damaligen Schnitt-A-Stand.
Die Korrektur vom 2026-09-19 ändert Datenverteilung, Capture-Modus,
Intervalltrennung und Validierung. Der geänderte Stand ist durch die oben
genannten frischen Docker-/Podman-Läufe vom 2026-09-19 belegt; die historischen
Läufe bleiben davon getrennt und validieren diese Korrektur nicht.
