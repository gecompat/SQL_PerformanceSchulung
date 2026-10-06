#!/usr/bin/env python3
"""Prüft den neutralen DGN-007-Profilvergleich ohne Runtime-Ausführung."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
from run_dgn007_automated_setup import PROFILE_COMPARISON_CONTRACT, load_manifest  # noqa: E402
from validate_dgn007_automated_setup import ownership_findings, workflow_findings  # noqa: E402
from validate_dgn007_query_store_windows import uncomment  # noqa: E402
from validate_dgn007_query_store_windows import PARENT_QUERY_SELECTION  # noqa: E402

AUTO = PROFILE_COMPARISON_CONTRACT.manifest.parent
SQL = AUTO / "30_Profile_Comparison.sql"
WORKFLOW = ROOT / ".github/workflows/dgn007-automated-setup.yml"
REQUIRED_SQL = (
    "DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,8,SYSUTCDATETIME())",
    "@Major IS NULL OR @Major NOT IN (15,16,17)",
    "@EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663)",
    "$(ConfirmIsolatedLab)", "$(HighImpactConfirmed)", "$(MaximumRuntimeSeconds)",
    "SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID()", "@ActualCompatibility IS NULL",
    "@ActualCompatibility<>CASE @Major WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170 END",
    "DB_NAME()<>N'SQLPERF_LAB_DGN007_AUTO'", "database_id>4 AND database_id<>DB_ID()",
    "DECLARE @ObjectId int=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')",
    "OBJECT_DEFINITION(@ObjectId) IS NULL",
    "CHARINDEX(N'/* DGN007_CASE_SEARCH */',OBJECT_DEFINITION(@ObjectId) COLLATE Latin1_General_100_BIN2)=0",
    "INSERT #ExpectedParameters VALUES(8,3),(1,3),(5,3),(1,1)",
    "WindowId IS NULL OR WindowId NOT IN (0,1)", "RequestCount IS NULL OR RequestCount<>4",
    "CapturedExecutions IS NULL OR CapturedExecutions<>4", "a.IntervalEnd<=b.IntervalStart",
    "a.LastRequestLogId<b.FirstRequestLogId", "i.start_time<>w.IntervalStart OR i.end_time<>w.IntervalEnd",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>12",
    "GROUP BY w.WindowId,r.GroupKey,r.StatusCode HAVING COUNT_BIG(*)<>1",
    "p.RuntimeStatsIntervalId IS NULL OR p.RuntimeStatsIntervalId<>w.RuntimeStatsIntervalId",
    "p.ExecutionType IS NULL OR p.ExecutionType<>0 OR p.ExecutionCount IS NULL OR p.ExecutionCount<=0",
    "p.AvgDurationUs IS NULL OR p.AvgDurationUs<0", "p.AvgCpuUs IS NULL OR p.AvgCpuUs<0",
    "p.AvgLogicalReads IS NULL OR p.AvgLogicalReads<0", "p.AvgRowCount IS NULL OR p.AvgRowCount<0",
    "p.FirstExecutionTime IS NULL OR p.LastExecutionTime IS NULL",
    "p.FirstExecutionTime<w.IntervalStart OR p.LastExecutionTime>=w.IntervalEnd",
    "s.QueryId IS NULL OR q.plan_id IS NULL",
    "GROUP BY WindowId,PlanId,RuntimeStatsIntervalId,ExecutionType HAVING COUNT_BIG(*)<>1",
    "COALESCE((SELECT SUM(p.ExecutionCount) FROM lab.IncidentProfile p WHERE p.WindowId=w.WindowId),0)<>4",
    "p.is_forced_plan IS NULL OR p.is_forced_plan<>0",
    "IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_hints',N'V') IS NOT NULL",
    "JOIN #ScopedQueries s ON s.QueryId=h.query_id",
    "INTO #LiveRuntime", "GROUP BY w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,r.runtime_stats_interval_id,r.execution_type",
    "HAVING SUM(r.count_executions)>0", "FROM #LiveRuntime EXCEPT SELECT",
    "SUM(ExecutionCount) AS ExecutionCount", "COUNT(DISTINCT PlanId) AS ObservedPlanCount",
    "SUM(ExecutionCount*AvgDurationUs)/NULLIF(SUM(ExecutionCount),0) AS AvgDurationUs",
    "SUM(ExecutionCount*AvgCpuUs)/NULLIF(SUM(ExecutionCount),0) AS AvgCpuUs",
    "SUM(ExecutionCount*AvgLogicalReads)/NULLIF(SUM(ExecutionCount),0) AS AvgLogicalReads",
    "SUM(ExecutionCount*AvgRowCount)/NULLIF(SUM(ExecutionCount),0) AS AvgRowCount",
    "SUM(ExecutionCount*AvgRowCount) AS TotalRows", "INTO #WindowTotals",
    "ExecutionCount<>4 OR TotalRows IS NULL OR ABS(TotalRows-4229.0)>0.000001",
    "b.MetricValue-a.MetricValue AS DeltaT1MinusT0", "b.MetricValue/NULLIF(a.MetricValue,0) AS RatioT1ToT0",
    "CASE WHEN a.MetricValue=0 THEN 1 ELSE 0 END AS BaselineZero",
    "a.WindowId=0 AND b.WindowId=1", "N'Vergleichsevidenz; keine Regression' AS ScopeMessage",
    "SQLPERF_SUMMARY|PASS|OK",
)
FORBIDDEN_SQL = (
    r"\bDBCC\b", r"\bALTER\b", r"\bDROP\b", r"\bCREATE\s+(?:EVENT|DATABASE)\b",
    r"\bsp_configure\b", r"\bsp_recompile\b", r"\bsp_query_store_flush_db\b",
    r"\bsp_query_store_(?:force_plan|unforce_plan|set_hints|clear_hints|remove_plan|remove_query)\b",
    r"\bEXEC(?:UTE)?\s+dbo\.usp_CaseSearch\b", r"SQLPERF_LAB_DGN007_LOCAL",
    r"(?i:READY_FOR_USER|FAIL_INCIDENT|SKIP_INCIDENT|WARN_EMPIRICAL_VARIANCE)",
    r"\b(?:INSERT(?:\s+INTO)?|UPDATE|DELETE\s+FROM|MERGE(?:\s+INTO)?)\s+(?:lab|dbo)\.",
    r"\bINTO\s+(?:lab|dbo)\.", r"\bTHROW\s+51003\b",
)


def section(sql: str, name: str) -> str:
    """Exakt einen tatsächlich ausführbaren markierten SQL-Abschnitt lesen."""
    begin, end = f"/* DGN007_PROFILE_{name}_BEGIN */", f"/* DGN007_PROFILE_{name}_END */"
    if sql.count(begin) != 1 or sql.count(end) != 1 or sql.index(begin) >= sql.index(end):
        raise ValueError(f"Profilabschnitt fehlt oder ist mehrfach vorhanden: {name}")
    return uncomment(sql.split(begin, 1)[1].split(end, 1)[0]).strip()


def manifest_findings(manifest) -> list[str]:
    contract = PROFILE_COMPARISON_CONTRACT
    if (manifest.demo_id, manifest.run_token, manifest.safety_level, manifest.timeout_seconds,
            manifest.cleanup_timeout_seconds) != ("DGN-007", "AUTO", "YELLOW", 180, 60):
        return ["Profilmanifest benötigt den gelben AUTO-Vertrag mit unverändertem Budget 180/60"]
    phases = (*manifest.phases, manifest.cleanup)
    if any(phase is None for phase in phases) or tuple(phase.phase_id for phase in phases) != contract.expected_phases:
        return ["Profilmanifest benötigt exakt sechs Phasen einschließlich Fenster, Profilvergleich und Cleanup"]
    return [f"Profilphase weicht ab: {phase.phase_id}" for phase, (_, script, selector, timeout) in zip(phases, contract.phase_specs)
            if phase.kind != "sql" or phase.path != AUTO / script or phase.database_selector != selector
            or phase.timeout_seconds != timeout or not phase.required or not phase.require_summary]


def sql_findings(sql: str) -> list[str]:
    code = uncomment(sql)
    normalized = " ".join(code.split())
    findings = [f"Profilvertrag fehlt: {marker}" for marker in REQUIRED_SQL if marker not in normalized]
    first_read = code.find("FROM lab.IncidentState")
    findings.extend(ownership_findings(code[:first_read]))
    for name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD", "TOTALS_GUARD", "WEIGHTED", "DELTA"):
        try:
            section(sql, name)
        except ValueError as error:
            findings.append(str(error))
    selection = re.search(r"INSERT #ParentQueries\(QueryId\)\s+(.*?);", code, re.DOTALL)
    if selection is None or " ".join(selection[1].split()) != " ".join(PARENT_QUERY_SELECTION.split()):
        findings.append("Profilcapture benötigt exakt die eigene Suchprozedur mit ihrem Kommentar")
    if code.count("IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL") != 2:
        findings.append("Beide PSP-Zugriffe benötigen den versionsgebundenen View-Guard")
    static_code = re.sub(r"N?'(?:''|[^'])*'", "''", code)
    if re.search(r"sys\.query_store_query_(?:variant|hints)", static_code):
        findings.append("Neuere PSP-/Hintviews dürfen ausschließlich dynamisch gebunden werden")
    deadline = "IF SYSUTCDATETIME()>=@PhaseDeadline BEGIN PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN; END;"
    if normalized.count(deadline) != 2 or normalized.count("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;") != 2:
        findings.append("Profilvergleich benötigt genau zwei kontrollierte Deadline-Guards mit unmittelbarem RETURN")
    if normalized.find(deadline) > normalized.find("SELECT N'DGN007_PROFILE_WINDOW'"):
        findings.append("Deadline muss vor der ersten Vergleichsausgabe geprüft werden")
    for forbidden in FORBIDDEN_SQL:
        if re.search(forbidden, code, re.IGNORECASE):
            findings.append(f"Unzulässiger Eingriff oder Promotion im neutralen Profilvergleich: {forbidden}")
    return findings


def main() -> int:
    findings = []
    for path in (SQL, PROFILE_COMPARISON_CONTRACT.manifest, WORKFLOW):
        if not path.is_file():
            findings.append(f"Profilartefakt fehlt: {path.relative_to(ROOT)}")
    if not findings:
        sql = SQL.read_text(encoding="utf-8")
        findings.extend(sql_findings(sql))
        for marker in REQUIRED_SQL:
            mutation = re.sub(r"\s+".join(re.escape(part) for part in marker.split()), "", sql)
            if mutation == sql or not sql_findings(mutation):
                findings.append(f"Negative Profilkontrolle nicht erkannt: {marker}")
        for mutation in (sql.replace("@Project IS NULL", "", 1), sql.replace("@Run IS NULL", "", 1),
                         sql.replace("IF SYSUTCDATETIME()>=@PhaseDeadline", "IF 1=0", 1),
                         sql.replace("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;", "PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT';", 1),
                         sql + "\nSELECT * FROM sys.query_store_query_variant;",
                         sql + "\nUPDATE lab.IncidentProfile SET ExecutionCount=5;",
                         sql + "\nEXEC sys.sp_query_store_force_plan 1,1;",
                         sql + "\nSELECT N'READY_FOR_USER';"):
            if not sql_findings(mutation):
                findings.append("Negative Eigentums-/Deadline-/Scope-/Mutationskontrolle nicht erkannt")
        manifest = load_manifest(PROFILE_COMPARISON_CONTRACT.manifest)
        findings.extend(manifest_findings(manifest))
        for invalid in (replace(manifest, timeout_seconds=181), replace(manifest, cleanup_timeout_seconds=61),
                        replace(manifest, cleanup=None), replace(manifest, phases=manifest.phases[:-1]),
                        replace(manifest, phases=manifest.phases + (manifest.phases[-1],))):
            if not manifest_findings(invalid):
                findings.append("Negative Profilmanifestkontrolle nicht erkannt")
        findings.extend(workflow_findings(WORKFLOW.read_text(encoding="utf-8")))
        if (AUTO / "manifest.json").exists() or (AUTO.parent / "manifest.json").exists():
            findings.append("Profilvergleich darf keine Capstone-Promotion erzeugen")
    if findings:
        print("dgn007-profile-comparison: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-profile-comparison: PASS (PROJECT_SEMANTIC; neutraler Profilvergleich ohne Regressions- oder Incidentabnahme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
