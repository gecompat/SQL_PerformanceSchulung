#!/usr/bin/env python3
"""Static boundary for the DGN-007 participant-flow slice B."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psm1"
FLOW = ROOT / "Documentation/HowTo/DGN_007_STATIC_PARTICIPANT_FLOW.md"
MITIGATION = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/50_Mitigation.sql"
CLEANUP = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/90_Cleanup.sql"
BASELINE = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/20_Baseline.sql"
OBSERVATION = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/40_Observation.sql"
COMPARISON = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/60_Comparison.sql"
SCENARIO_JSON = ROOT / "Scenarios/DGN-007/scenario.json"
MANIFEST = ROOT / "Scenarios/DGN-007/manifest.json"
ADAPTER = ROOT / "Scenarios/DGN-007/adapter/adapter.json"
INVENTORY = ROOT / "Documentation/Inventories/performance_scenario_inventory.json"
SCENARIO_ROOT = ROOT / "Scenarios/DGN-007"
README = ROOT / "Scenarios/DGN-007/README.md"
CURRENT_STATUS = ROOT / "Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md"
NEXT_WAVES = ROOT / "Documentation/Project_Planning/NEXT_DEVELOPMENT_WAVES.md"


def main() -> int:
    findings: list[str] = []
    for path in (MODULE, FLOW, BASELINE, OBSERVATION, MITIGATION, COMPARISON, CLEANUP, ADAPTER, INVENTORY, README, CURRENT_STATUS, NEXT_WAVES):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    for path in (SCENARIO_JSON, MANIFEST):
        if path.exists():
            findings.append(f"static participant flow must not add {path.relative_to(ROOT)}")
    if findings:
        print("labscn005-dgn007-slice-b: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    flow = FLOW.read_text(encoding="utf-8")
    for marker in (
        "IMPLEMENTED_STATIC_SLICE_B",
        "STATIC_PARTICIPANT_FLOW_ONLY",
        "MANUAL",
        "kein interaktives Szenario",
        "kein Runtime-Nachweis",
        "T0_BASELINE",
        "T1_INCIDENT",
        "T2_COMPARISON",
        "SKIP_QUERY_STORE_REQUIRED",
        "SKIP_INCIDENT_NOT_REPRODUCED",
        "SKIP_EVIDENCE_MISSING",
        "00_Preflight.sql",
        "20_Baseline.sql",
        "40_Observation.sql",
        "50_Mitigation.sql",
        "60_Comparison.sql",
        "90_Cleanup.sql",
    ):
        if marker not in flow:
            findings.append(f"participant flow marker missing: {marker}")
    phase_positions = [flow.index(marker) for marker in ("1. **PRECHECK", "2. **TIME_WINDOWS", "3. **EVIDENCE", "4. **HYPOTHESIS", "5. **REFERENCE_CHANGE", "6. **COMPARISON", "7. **RECOVERY")]
    if phase_positions != sorted(phase_positions):
        findings.append("participant phases must remain ordered")
    if "READY_FOR_USER" in flow and "keine Freigabe für `READY_FOR_USER`" not in flow:
        findings.append("participant flow must not imply READY_FOR_USER")

    mitigation = MITIGATION.read_text(encoding="utf-8")
    for marker in (
        "@ProcedurePosition=CHARINDEX(N'PROCEDURE',@Changed)",
        "SET @Changed=N'ALTER '+SUBSTRING(@Changed,@ProcedurePosition,LEN(@Changed))",
        "FAIL_CONTRACT: Der erwartete Prozedurkopf",
    ):
        if marker not in mitigation:
            findings.append(f"reversible mitigation marker missing: {marker}")

    cleanup = CLEANUP.read_text(encoding="utf-8")
    for marker in (
        "@ProcedurePosition=CHARINDEX(N'PROCEDURE',@Original)",
        "SET @Restore=N'ALTER '+SUBSTRING(@Original,@ProcedurePosition,LEN(@Original))",
        "FAIL_CLEANUP: Der erwartete Prozedurkopf",
        "DELETE FROM lab.IncidentQueryStoreProfile WHERE IncidentPhase=N'T2_COMPARISON'",
    ):
        if marker not in cleanup:
            findings.append(f"reversible cleanup marker missing: {marker}")

    baseline = BASELINE.read_text(encoding="utf-8")
    for marker in (
        "max_memory=1024",
        "MAX_MEMORY=1024 KB",
        "XeStartedUtc datetimeoffset(7)",
        "UPDATE lab.Dgn007ReferenceState SET XeStartedUtc=SYSUTCDATETIME()",
        "XE-Aufnahme beginnt erst nach T1",
    ):
        if marker not in baseline:
            findings.append(f"bounded XE marker missing: {marker}")

    observation = OBSERVATION.read_text(encoding="utf-8")
    for marker in (
        "q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')",
        "qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%'",
        "StrictParentQuery AS",
        "EffectiveQuery AS",
        "qv.query_variant_query_id",
        "parent.query_id=qv.parent_query_id",
        "FROM EffectiveQuery AS effective",
        "FROM lab.IncidentQueryStoreProfile AS e",
        "@XeStartedUtc=XeStartedUtc",
        "nur begrenzte Evidenz fuer nachfolgende Vergleichsausfuehrungen",
        "QueryVariantCount=",
        "IntervalStartUtc",
        "IntervalEndUtc",
    ):
        if marker not in observation:
            findings.append(f"observation scope marker missing: {marker}")

    comparison = COMPARISON.read_text(encoding="utf-8")
    for marker in (
        "@Phase nvarchar(32)=N'T2_COMPARISON'",
        "WHILE SYSUTCDATETIME() <= @T1IntervalEnd",
        "DATEADD(second,90,SYSUTCDATETIME())",
        "INSERT #Parameters(GroupKey,StatusCode) VALUES(8,3),(1,3),(5,3),(1,1)",
        "#Expected EXCEPT SELECT",
        "#Actual EXCEPT SELECT",
        "INSERT lab.IncidentQueryStoreProfile",
        "q.object_id=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')",
        "qt.query_sql_text LIKE N'%/* DGN007_CASE_SEARCH */%'",
        "StrictParentQuery AS",
        "EffectiveQuery AS",
        "qv.query_variant_query_id",
        "parent.query_id=qv.parent_query_id",
        "FROM EffectiveQuery AS effective",
        "ExpectedExecutions=",
        "ActualExecutions=",
        "QueryVariantCount=",
        "b.IncidentPhase IN(N'T0_BASELINE',N'T1_INCIDENT')",
        "AND i.end_time > s.MarkerUtc AND i.start_time <= s.CompletedUtc",
        "SKIP_EVIDENCE_MISSING",
    ):
        if marker not in comparison:
            findings.append(f"comparison evidence marker missing: {marker}")
    if "rs.last_execution_time<=s.CompletedUtc" in comparison:
        findings.append("T2 must not use exact phase completion timestamps as a Runtime filter")

    module = MODULE.read_text(encoding="utf-8")
    for marker in (
        "StaticParticipantFlow = @{",
        "Status = 'STATIC_PARTICIPANT_FLOW_ONLY'",
        "EntryDocument = 'Documentation\\HowTo\\DGN_007_STATIC_PARTICIPANT_FLOW.md'",
        "Role = 'PRECHECK'",
        "Role = 'RECOVERY'",
        "ParticipantPhases = if ($staticFlow)",
        "Where-Object { $_.Value.ScenarioPath }",
    ):
        if marker not in module:
            findings.append(f"module static handoff marker missing: {marker}")
    if module.count("[ValidateSet('CON-004','CON-006','DGN-005','DGN-007')]") != 1:
        findings.append("DGN-007 may be selectable only for targeted static metadata")
    if module.count("[ValidateSet('CON-004','CON-006','DGN-005')]") != 3:
        findings.append("lifecycle commands must keep the released scenario boundary")
    dgn007_start = module.find("    'DGN-007' = @{")
    dgn007_end = module.find("    }\n}", dgn007_start)
    if dgn007_start == -1 or dgn007_end == -1:
        findings.append("DGN-007 scenario definition boundary missing")
    else:
        dgn007_definition = module[dgn007_start:dgn007_end]
        if "ScenarioPath = $null" not in dgn007_definition:
            findings.append("DGN-007 must not receive a scenario path for READY_FOR_USER promotion")
        if "StaticParticipantFlow = @{" not in dgn007_definition:
            findings.append("DGN-007 must retain the static participant-flow metadata boundary")

    adapter = json.loads(ADAPTER.read_text(encoding="utf-8"))
    if adapter.get("supportedSqlVersions") != ["2025"]:
        findings.append("adapter must keep the exact 2025-only supportedSqlVersions contract")
    if "2025 auf Docker oder Podman" not in "\n".join(adapter.get("knownLimitations", [])):
        findings.append("adapter must document the 2025-only Docker/Podman contract")

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if any(item.get("demoId") == "DGN-007" for item in inventory.get("scenarios", [])):
        findings.append("static slice B must not add DGN-007 to the scenario inventory")
    if any("DGN-007" in path.name for path in SCENARIO_ROOT.glob("*manifest*.json")):
        findings.append("static slice B must not add a DGN-007 runtime manifest")

    status_documents = (README, CURRENT_STATUS, NEXT_WAVES)
    for path in status_documents:
        text = path.read_text(encoding="utf-8")
        if "IMPLEMENTED_STATIC_SLICE_B" not in text:
            findings.append(f"static readiness status missing: {path.relative_to(ROOT)}")
    for path in (README, CURRENT_STATUS, NEXT_WAVES):
        text = path.read_text(encoding="utf-8")
        for marker in ("2019", "2022", "ADAPTER_UNSUPPORTED_SQL_VERSION", "REMOVED"):
            if marker not in text:
                findings.append(f"controlled 2019/2022 skip or cleanup boundary missing in {path.relative_to(ROOT)}: {marker}")
        if "keine" not in text or "Promotion" not in text:
            findings.append(f"non-promotion boundary missing in {path.relative_to(ROOT)}")
    for path in (README, CURRENT_STATUS, NEXT_WAVES):
        text = path.read_text(encoding="utf-8")
        if "READY_FOR_USER" not in text or "keine" not in text:
            findings.append(f"READY_FOR_USER non-promotion boundary missing in {path.relative_to(ROOT)}")

    if findings:
        print(f"labscn005-dgn007-slice-b: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn005-dgn007-slice-b: PASS (PROJECT_SEMANTIC; IMPLEMENTED_STATIC_SLICE_B remains 2025-only, non-promoting, and cleanup-bounded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
