# DGN-007 – Implementierungsschnitt A (Datenaufbau, Query-Store-Fenster, Incident-Erzeugung)

| Merkmal | Wert |
|---|---|
| Status | `DESIGNED` (Schnitt A als Adaptervertrag implementiert) |
| Stand | 2026-09-14 |
| Arbeitspaket | `LABSCN-005` |
| Task | `TSK-002` |
| Detailreview | [`LABSCN_005_DGN_007_DETAIL_REVIEW.md`](../../Documentation/Project_Planning/LABSCN_005_DGN_007_DETAIL_REVIEW.md) |
| interaktive Zielversion | SQL Server 2025 / Compatibility Level 170 |
| Safety | `YELLOW`, ausschließlich isolierte Wegwerfinstanz |

## Umfang dieses Schnitts

Schnitt A ist der erste von drei Folgeschnitten aus dem Detailreview und
implementiert ausschließlich den Project Adapter `0.1` mit:

1. **Datenaufbau** (`DGN-007_DATA_MODEL`): die markergebundene Testdatenbank
   `SQLPERF_LAB_DGN007_LOCAL` mit den neutralen Objekten `dbo.CaseGroup`,
   `dbo.CaseItem`, `dbo.CaseItemDetail`, `dbo.CaseRequestLog` und der
   markierten Suchprozedur `dbo.usp_CaseSearch`. Die Verteilung entsteht
   deterministisch ohne Zufallswerte: vier häufige, drei mittlere und fünf
   seltene Gruppen über `n % 5` beziehungsweise `n % 7`-Ableitung,
   24.000 Faktzeilen, je drei Detailzeilen.
2. **Query-Store-Fenster** (`DGN-007_QUERY_STORE_WINDOWS`): Query Store in
   `READ_WRITE` mit begrenztem Capture- und Größenvertrag (128 MB,
   1-Minuten-Intervalle, `MAX_PLANS_PER_QUERY=20`), Baselinefenster
   `T0_BASELINE` und markiertes Incidentfenster `T1_INCIDENT`.
3. **Incident-Erzeugung** (`DGN-007_INCIDENT_GENERATION`): kontrollierte
   Ausführungsreihenfolge der markierten Prozedur mit häufigen, mittleren und
   seltenen Parameterwerten. Die Cacheisolation bleibt objektgebunden; globale
   Cacheleerung bleibt verboten.

Schnitt A integriert außerdem das Szenario in das
Orchestrierungsmodul `PerformanceTrainingScenario.psm1` und den zugehörigen
statischen Validator, ohne die Lifecycle-Abnahme der bisherigen vier Slices
zu verändern.

## Statusgrenze

Die interaktive `scenario.json` ist bewusst **nicht** Bestandteil dieses
Schnitts: Der Szenario-Inventar-Validator verlangt für jede
`Scenarios/*/scenario.json` einen vollständigen Inventareintrag mit
`VALIDATED`-Demo-Contract und Runtime-Manifest. Beides folgt erst mit der
Runtime-Matrix (Schnitt C). Der Adapter besitzt deshalb in diesem Schnitt
keinen `READY_FOR_USER`-Teilnehmerablauf; sein `validate`-Entrypoint belegt
ausschließlich den fachlichen Zustand nach Datenaufbau und Incident-Erzeugung.

Dieser Schnitt enthält **keinen** Mitigationsmarker, keine Referenzlösung,
keine Evidenzstufen und keine Teilnehmerphasen – diese folgen in Schnitt B.
Die interaktive Docker-/Podman-Lifecycle-Abnahme und die automatisierte
2019/2022/2025-Matrix sind Folgeschnitte. Eine Statusanhebung über diesen
Schnitt hinaus erfordert konkrete Laufnachweise gemäß
[`DEMO_CONTRACT.md`](../../.ai/DEMO_CONTRACT.md).

## Vertragsmarker

- Datenbank- und Eigentumsmarker: `SQLPERF.Project`, `SQLPERF.ContractVersion`,
  `SQLPERF.DemoId`, `SQLPERF.RunToken`
- Incidentphasen: `T0_BASELINE`, `T1_INCIDENT` (in `lab.IncidentState`)
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

## Praktische Lifecycle-Abnahme (2026-09-14)

Die vollständige Adapter-Lifecycle-Abnahme lief über
`Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1` mit
`-ScenarioId DGN-007` je Provider auf SQL Server 2025:

| Provider | RunId | Start | Reset | Remove |
|---|---|---|---|---|
| Docker | `9ac100f8-f24f-420e-949c-943e35b9bcda` | `READY_FOR_USER` | `READY_FOR_USER` | `REMOVED` |
| Podman | `e06e9ec9-d239-4cd0-b9a7-0050dc574180` | `READY_FOR_USER` | `READY_FOR_USER` | `REMOVED` |

Beide Läufe bestätigten install (Datenaufbau, 24.000 Faktzeilen, Incident-Marker
`T1_INCIDENT`) und validate (Query Store `READ_WRITE`, zwei erfasste
Query-Pläne). Da die interaktive `scenario.json` erst mit der Runtime-Matrix
(Schnitt C) in den Inventar kommt, arbeitet das Orchestrierungsmodul für
`DGN-007` mit dem statischen Vertrag `DESIGNED_SLICE_A`: Start und Reset
erzeugen und prüfen den fachlichen Zustand vollständig, es existieren aber
keine Teilnehmerphasen. Der Podman-Lauf ließ die vorhandene, nicht zum Run
gehörende Altressource unverändert.