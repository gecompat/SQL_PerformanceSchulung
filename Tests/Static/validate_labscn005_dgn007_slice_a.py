#!/usr/bin/env python3
"""Static contract for the DGN-007 implementation slice A (data model, Query Store windows, incident generation)."""
from __future__ import annotations

import json
import re
import sqlite3
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


def check_distribution(install: str, findings: list[str]) -> None:
    """Den portablen CASE-Ausdruck des SQL-Generators auf allen 24.000 Nummern pruefen."""
    sql = "".join(part.replace("''", "'") for part in re.findall(r"N'((?:[^']|'')*)'", install))
    expression = re.search(r"(CASE WHEN n\b.*? END) AS GroupKey", sql, re.DOTALL)
    bounds = re.search(r"FROM Numbers WHERE n BETWEEN (\d+) AND (\d+)\)INSERT dbo.CaseItem\(", sql)
    if expression is None or bounds is None or bounds.groups() != ("1", "24000"):
        findings.append("data generator must declare a bounded 1..24000 GroupKey CASE expression")
        return
    expected = [(group, 4000 if group <= 4 else 2000 if group <= 7 else 400) for group in range(1, 13)]
    try:
        with sqlite3.connect(":memory:") as connection:
            actual = connection.execute(
                "WITH RECURSIVE Numbers(n) AS (VALUES(1) UNION ALL SELECT n+1 FROM Numbers WHERE n<24000) "
                f"SELECT {expression.group(1)} AS GroupKey,COUNT(*) FROM Numbers GROUP BY GroupKey ORDER BY GroupKey"
            ).fetchall()
        if actual != expected:
            findings.append("data distribution must be four groups of 4000, three of 2000 and five of 400 rows")
    except sqlite3.Error as error:
        findings.append(f"bounded generator CASE could not be checked: {error}")


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
    check_distribution(install, findings)
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
        "QUERY_CAPTURE_MODE = ALL",
        "CREATE TABLE lab.IncidentQueryStoreProfile",
        "IncidentPhase nvarchar(32) NOT NULL PRIMARY KEY",
        "CompletedUtc datetimeoffset(7)",
        "EXEC sys.sp_query_store_flush_db",
        "MAX(i.end_time)",
        "DATEADD(second,90,SYSUTCDATETIME())",
        "WHILE SYSUTCDATETIME() <= @IntervalEnd",
        "bi.end_time > ti.start_time",
        "SKIP_EVIDENCE_MISSING",
        "WHERE IncidentPhase = @Phase",
    ):
        if marker not in install:
            findings.append(f"install safety marker missing: {marker}")
    if "SET IncidentPhase" in install or "WAITFOR DELAY ''00:00:02''" in install:
        findings.append("phase evidence must not be overwritten or separated by a fixed two-second wait")

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
    for name, text in (("install", install), ("validate", validate_sql)):
        for marker in (
            "q.object_id = OBJECT_ID(N''dbo.usp_CaseSearch'',N''P'')",
            "qt.query_sql_text LIKE N''%/* DGN007_CASE_SEARCH */%''",
            "rs.execution_type = 0 AND rs.count_executions > 0",
            "SUM(rs.count_executions)",
            "GROUP BY q.query_id,p.plan_id,rs.runtime_stats_interval_id",
            "bi.end_time > ti.start_time",
        ):
            if marker not in text:
                findings.append(f"{name} must bind phase evidence to the marked search: {marker}")
        for marker in (
            "StrictParentQuery AS",
            "EffectiveQuery AS",
            "sys.query_store_query_variant AS qv",
            "qv.query_variant_query_id",
            "parent.query_id = qv.parent_query_id",
            "FROM EffectiveQuery AS effective",
            "JOIN sys.query_store_query AS q ON q.query_id",
        ):
            if marker not in text:
                findings.append(f"{name} must include PSP variant query IDs in the effective Query Store set: {marker}")
    for marker in (
        "ExpectedExecutions=",
        "ActualExecutions=",
        "QueryVariantCount=",
        "DGN007_QUERY_STORE_DIAGNOSTIC_COUNTS",
        "DGN007_QUERY_STORE_DIAGNOSTIC_GROUP",
        "TOP (32)",
        "QueryStoreActualState",
        "QueryStoreCaptureMode",
        "QueryStoreReadOnlyReason",
        "ParentQueryCount",
        "EffectiveQueryCount",
        "PlanCount",
        "RuntimeGroupCount",
        "IntervalStartUtc",
        "IntervalEndUtc",
        "PhaseMarkerUtc",
        "PhaseCompletedUtc",
        "FirstBeforeMarker",
        "LastAfterCompleted",
        "sys.database_query_store_options AS state",
    ):
        if marker not in install:
            findings.append(f"install must diagnose phase evidence counts: {marker}")
    diagnostic_position = install.find("DGN007_QUERY_STORE_DIAGNOSTIC_COUNTS")
    skip_position = install.find("SET @EvidenceMessage=CONCAT(N''SKIP_EVIDENCE_MISSING")
    if diagnostic_position == -1 or skip_position == -1 or diagnostic_position > skip_position:
        findings.append("bounded Query Store diagnostics must precede SKIP_EVIDENCE_MISSING")
    for marker in (
        "(SELECT COUNT(*) FROM lab.IncidentState) <> 2",
        "LEFT JOIN #SearchRuntime r ON r.query_id = e.QueryId AND r.plan_id = e.PlanId",
        "r.runtime_stats_interval_id = e.RuntimeStatsIntervalId",
        "r.CountExecutions < e.CountExecutions",
        "i.end_time <= s.MarkerUtc OR i.start_time > s.CompletedUtc",
        "CASE WHEN g.GroupKey <= 4 THEN 4000 WHEN g.GroupKey <= 7 THEN 2000 ELSE 400 END",
    ):
        if marker not in validate_sql:
            findings.append(f"validate phase/data assertion missing: {marker}")
    if "AND i.end_time > s.MarkerUtc AND i.start_time <= s.CompletedUtc" not in install:
        findings.append("install must associate real Query Store intervals with the phase window")
    if "rs.last_execution_time <= s.CompletedUtc" in install or "e.LastExecutionUtc > s.CompletedUtc" in validate_sql:
        findings.append("Query Store timestamps must not be filtered by exact phase completion timestamps")
    for name, text in (("validate", validate_sql), ("cleanup", cleanup)):
        for marker in ("COALESCE(@Project,N'')", "COALESCE(@Contract,N'')", "COALESCE(@Demo,'')", "COALESCE(@Run,'')"):
            if marker not in text:
                findings.append(f"{name} ownership check must reject NULL: {marker}")

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
    for marker in (
        "'DGN-007'",
        "SQLPERF_LAB_DGN007_LOCAL",
        "Scenarios\\DGN-007\\sql-server-lab.json",
        "StaticSliceContract = 'DESIGNED_SLICE_A'",
    ):
        if marker not in module:
            findings.append("module does not publish DGN-007 with the static slice contract")

    readme = README.read_text(encoding="utf-8")
    for marker in (
        "IMPLEMENTED_STATIC_SLICE_B",
        "TSK-002",
        "LABSCN_005_DGN_007_DETAIL_REVIEW.md",
        "SKIP_QUERY_STORE_REQUIRED",
        "SKIP_INCIDENT_NOT_REPRODUCED",
        "9ac100f8-f24f-420e-949c-943e35b9bcda",
        "e06e9ec9-d239-4cd0-b9a7-0050dc574180",
    ):
        if marker not in readme:
            findings.append(f"README marker missing: {marker}")

    if findings:
        print(f"labscn005-dgn007-slice-a: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn005-dgn007-slice-a: PASS (PROJECT_SEMANTIC; distribution, scoped Query Store intervals and NULL-safe ownership; no runtime evidence)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
