#!/usr/bin/env python3
"""Static contract for the DGN-007 implementation slice A (data model, Query Store windows, incident generation)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Scenarios/DGN-007/adapter/adapter.json"
MODULE = ROOT / "Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psm1"
README = ROOT / "Scenarios/DGN-007/README.md"
REVIEW = ROOT / "Documentation/Project_Planning/LABSCN_005_DGN_007_DETAIL_REVIEW.md"
SCENARIO_JSON = ROOT / "Scenarios/DGN-007/scenario.json"
ENTRYPOINTS = ("preflight", "install", "validate", "cleanup")

FORBIDDEN_SOLUTION_MARKERS = (
    "OPTION (RECOMPILE)",
    "OPTION(RECOMPILE)",
    "sp_recompile",
    "sp_query_store_force_plan",
    "sp_query_store_unforce",
    "sp_force_show_query_store_plan_for_query",
    "query_store_force",
    "FORCE_PLAN",
    "event_file",
    "CREATE EVENT SESSION",
)


def main() -> int:
    findings: list[str] = []
    for path in (ADAPTER, MODULE, README, REVIEW):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    if SCENARIO_JSON.exists():
        findings.append("slice A must not add Scenarios/DGN-007/scenario.json; the inventory contract requires it only with the validated runtime manifest in slice B")
    if findings:
        print("labscn005-dgn007-slice-a: FAIL")
        return 1

    adapter = json.loads(ADAPTER.read_text(encoding="utf-8"))
    if adapter.get("adapterContractVersion") != "0.1" or adapter.get("supportedSqlVersions") != ["2025"]:
        findings.append("adapter version boundary mismatch")
    if adapter.get("dataClassification") != "SYNTHETIC" or adapter.get("privacyExportPolicy") != "NO_AUTOMATIC_EXPORT":
        findings.append("adapter privacy boundary mismatch")

    install = (ADAPTER.parent / "sql/install.sql").read_text(encoding="utf-8")
    for marker in (
        "ADAPTER_ISOLATION_REQUIRED",
        "SQLPERF_LAB_DGN007_LOCAL",
        "SQLPERF.Project",
        "SQLPERF.ContractVersion",
        "SQLPERF.DemoId",
        "SQLPERF.RunToken",
        "dbo.CaseGroup",
        "dbo.CaseItem",
        "dbo.CaseItemDetail",
        "dbo.CaseRequestLog",
        "dbo.usp_CaseSearch",
        "T0_BASELINE",
        "T1_INCIDENT",
        "OPERATION_MODE = READ_WRITE",
        "MAX_STORAGE_SIZE_MB = 128",
        "INTERVAL_LENGTH_MINUTES = 1",
        "MAX_PLANS_PER_QUERY = 20",
    ):
        if marker not in install:
            findings.append(f"install safety marker missing: {marker}")

    cleanup = (ADAPTER.parent / "sql/cleanup.sql").read_text(encoding="utf-8")
    for marker in (
        "SQLPERF.Project",
        "SQLPERF.ContractVersion",
        "SQLPERF.DemoId",
        "SQLPERF.RunToken",
        "DROP DATABASE",
        "PROJECT_CLEANUP_FAILED",
    ):
        if marker not in cleanup:
            findings.append(f"cleanup marker missing: {marker}")

    validate_sql = (ADAPTER.parent / "sql/validate.sql").read_text(encoding="utf-8")
    if "READ_WRITE" not in validate_sql or "database_query_store_options" not in validate_sql:
        findings.append("validate must assert the Query Store contract")

    for name in ENTRYPOINTS:
        path = ADAPTER.parent / "sql" / f"{name}.sql"
        if not path.is_file():
            findings.append(f"missing adapter entrypoint {name}")
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SOLUTION_MARKERS:
            if forbidden in text:
                findings.append(f"forbidden solution or export marker {forbidden} in {name}")
        if re.search(r"DROP DATABASE", text) is not None and name not in ("cleanup", "install"):
            findings.append(f"unexpected DROP DATABASE in {name}")

    module = MODULE.read_text(encoding="utf-8")
    for marker in ("'DGN-007'", "SQLPERF_LAB_DGN007_LOCAL", "Scenarios\\DGN-007\\scenario.json"):
        if marker not in module:
            findings.append("module does not publish DGN-007")

    readme = README.read_text(encoding="utf-8")
    for marker in ("DESIGNED", "TSK-002", "LABSCN_005_DGN_007_DETAIL_REVIEW.md", "SKIP_QUERY_STORE_REQUIRED", "SKIP_INCIDENT_NOT_REPRODUCED"):
        if marker not in readme:
            findings.append(f"README marker missing: {marker}")

    if findings:
        print(f"labscn005-dgn007-slice-a: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn005-dgn007-slice-a: PASS (YELLOW; DESIGNED contract, RUNNER_ASSISTED boundary; marker-bound data model, Query Store windows and incident generation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())