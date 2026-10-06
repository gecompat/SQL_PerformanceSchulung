#!/usr/bin/env python3
"""Prüft den begrenzten Query-Store-Fenstervertrag ohne SQL-Server-Ausführung."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
from run_dgn007_automated_setup import QUERY_STORE_WINDOWS_CONTRACT, load_manifest  # noqa: E402
from validate_dgn007_automated_setup import ownership_findings, workflow_findings  # noqa: E402

AUTO = QUERY_STORE_WINDOWS_CONTRACT.manifest.parent
SQL = AUTO / "20_Query_Store_Windows.sql"
WORKFLOW = ROOT / ".github/workflows/dgn007-automated-setup.yml"
SCHEMA_COLUMNS = {
    "IncidentState": {
        "WindowId", "RuntimeStatsIntervalId", "IntervalStart", "IntervalEnd",
        "ExecutionStarted", "ExecutionFinished", "FirstRequestLogId", "LastRequestLogId",
        "RequestCount", "CapturedExecutions",
    },
    "IncidentProfile": {
        "WindowId", "ParentQueryId", "QueryId", "PlanId", "RuntimeStatsIntervalId",
        "ExecutionType", "ExecutionCount", "AvgDurationUs", "AvgCpuUs", "AvgLogicalReads",
        "AvgRowCount", "FirstExecutionTime", "LastExecutionTime",
    },
}
REQUIRED_SQL = (
    "@Major IS NULL OR @Major NOT IN (15,16,17)",
    "@EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663)",
    "$(ConfirmIsolatedLab)", "$(HighImpactConfirmed)", "$(MaximumRuntimeSeconds)",
    "DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,145,SYSUTCDATETIME())",
    "SET @PollDeadline=DATEADD(second,90,SYSUTCDATETIME())",
    "IF @PollDeadline>@PhaseDeadline SET @PollDeadline=@PhaseDeadline",
    "IF SYSUTCDATETIME()>=@PhaseDeadline",
    "INTO lab.QueryStoreBaseline FROM sys.database_query_store_options",
    "desired_state IS NULL", "actual_state IS NULL", "query_capture_mode IS NULL",
    "flush_interval_seconds IS NULL", "interval_length_minutes IS NULL", "max_storage_size_mb IS NULL",
    "stale_query_threshold_days IS NULL", "max_plans_per_query IS NULL", "readonly_reason IS NULL",
    "ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET QUERY_STORE=ON",
    "OPERATION_MODE=READ_WRITE,QUERY_CAPTURE_MODE=ALL,MAX_STORAGE_SIZE_MB=128",
    "INTERVAL_LENGTH_MINUTES=1,DATA_FLUSH_INTERVAL_SECONDS=60",
    "(0,1,8,3,228),(0,2,1,3,2286),(0,3,5,3,1144),(0,4,1,1,571)",
    "(1,1,1,3,2286),(1,2,8,3,228),(1,3,5,3,1144),(1,4,1,1,571)",
    "(SELECT COUNT_BIG(*) FROM #Actual)<>@ExpectedCount",
    "EXCEPT SELECT ItemId,SearchValue,StatusCode,GroupLabel,DetailCount FROM #Actual",
    "EXCEPT SELECT i.ItemId,i.SearchValue,i.StatusCode,g.GroupLabel,CONVERT(int,3)",
    "DECLARE @WindowId tinyint=0", "WHILE @WindowId<=1", "SET @WindowId+=1",
    "WHILE @PreviousIntervalId IS NULL", "WHILE @IntervalId IS NULL",
    "DECLARE @Pulse bigint",
    "FROM sys.query_store_runtime_stats_interval",
    "runtime_stats_interval_id<>@PreviousIntervalId AND start_time>=@PreviousEnd",
    "SET @PreviousIntervalId=@IntervalId", "SET @PreviousEnd=@IntervalEnd",
    "IF @Started<@IntervalStart OR @Finished>=@IntervalEnd",
    "a.RuntimeStatsIntervalId<>b.RuntimeStatsIntervalId AND a.IntervalEnd<=b.IntervalStart",
    "a.LastRequestLogId<b.FirstRequestLogId",
    "EXEC sys.sp_recompile N'dbo.usp_CaseSearch'",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>12",
    "(SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog WHERE RequestLogId>@InitialRequestId)<>8",
    "q.object_id=@ObjectId",
    "DECLARE @ObjectId int=OBJECT_ID(N'dbo.usp_CaseSearch',N'P')",
    "CHARINDEX(N'/* DGN007_CASE_SEARCH */',t.query_sql_text COLLATE Latin1_General_100_BIN2)>0",
    "IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL",
    "EXEC sys.sp_executesql N'DELETE p FROM #ParentQueries p JOIN sys.query_store_query_variant",
    "SUM(r.count_executions)",
    "SUM(r.avg_duration*r.count_executions)/NULLIF(SUM(r.count_executions),0)",
    "SUM(r.avg_cpu_time*r.count_executions)/NULLIF(SUM(r.count_executions),0)",
    "SUM(r.avg_logical_io_reads*r.count_executions)/NULLIF(SUM(r.count_executions),0)",
    "SUM(r.avg_rowcount*r.count_executions)/NULLIF(SUM(r.count_executions),0)",
    "GROUP BY w.WindowId,s.ParentQueryId,s.QueryId,p.plan_id,r.runtime_stats_interval_id,r.execution_type",
    "WHERE r.execution_type=0",
    "COALESCE((SELECT SUM(p.ExecutionCount) FROM lab.IncidentProfile p WHERE p.WindowId=w.WindowId),0)<>4",
    "IF @Captured=0", "SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING", "IF @Ready<>1",
    "p.FirstExecutionTime<w.IntervalStart OR p.LastExecutionTime>=w.IntervalEnd",
    "SQLPERF_SUMMARY|PASS|OK",
)
FORBIDDEN_SQL = (
    r"\bDBCC\b", r"\bCREATE\s+EVENT\s+SESSION\b", r"\bALTER\s+SERVER\b",
    r"\bsp_configure\b", r"\bQUERY_STORE\s*(?:=\s*)?CLEAR\b",
    r"\bsp_query_store_(?:force_plan|unforce_plan|set_hints|clear_hints|remove_plan|remove_query)\b",
    r"\bQUERY_STORE\s*=\s*OFF\b", r"\bNEWID\s*\(", r"SQLPERF_LAB_DGN007_LOCAL",
    r"\bDATABASEPROPERTYEX\s*\(", r"\bREADY_FOR_USER\b", r"(?im)^\s*:r\b",
    r"\bQUERY_STORE_HINTS\b", r"\bDROP\s+DATABASE\b",
    r"\bTHROW\s+51003\b",
)
TIMEOUT_SUMMARY = "PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;"
TIMEOUT_LABELS = {
    "PollDeadline": ("INITIAL_INTERVAL", "NEXT_INTERVAL"),
    "PhaseDeadline": ("PHASE_BEFORE_WINDOW", "PHASE_BEFORE_REQUEST", "CAPTURE_DEADLINE", "FINAL_DEADLINE"),
}
NEXT_INTERVAL_DIAGNOSTIC = """
DECLARE @LatestIntervalId bigint,@LatestIntervalStart datetimeoffset(7),@LatestIntervalEnd datetimeoffset(7);
SELECT TOP(1) @LatestIntervalId=runtime_stats_interval_id,@LatestIntervalStart=start_time,@LatestIntervalEnd=end_time
FROM sys.query_store_runtime_stats_interval ORDER BY start_time DESC,runtime_stats_interval_id DESC;
PRINT CONCAT('DGN007_WINDOW_TIMEOUT_DETAIL|id=',COALESCE(CONVERT(varchar(20),@LatestIntervalId),'NONE'),
             '|start=',COALESCE(CONVERT(varchar(40),SWITCHOFFSET(@LatestIntervalStart,'+00:00'),127),'NONE'),
             '|end=',COALESCE(CONVERT(varchar(40),SWITCHOFFSET(@LatestIntervalEnd,'+00:00'),127),'NONE'));
"""
PARENT_QUERY_SELECTION = """
SELECT q.query_id FROM sys.query_store_query q JOIN sys.query_store_query_text t ON t.query_text_id=q.query_text_id
WHERE q.object_id=@ObjectId
  AND CHARINDEX(N'/* DGN007_CASE_SEARCH */',t.query_sql_text COLLATE Latin1_General_100_BIN2)>0
"""
PULSE_CALL = "EXEC sys.sp_executesql N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;', N'@Rows bigint OUTPUT',@Rows=@Pulse OUTPUT;"
POLL_PULSE = PULSE_CALL + """
IF @Pulse IS NULL OR @Pulse<>12
BEGIN
    PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;
END;
EXEC sys.sp_query_store_flush_db;
"""
POLL_CATALOG_PROBES = {
    "PreviousIntervalId": """
SELECT TOP(1) @PreviousIntervalId=runtime_stats_interval_id,@PreviousEnd=end_time
FROM sys.query_store_runtime_stats_interval
WHERE start_time<=TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
  AND end_time>TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
ORDER BY start_time DESC;
""",
    "IntervalId": """
SELECT TOP(1) @IntervalId=runtime_stats_interval_id,@IntervalStart=start_time,@IntervalEnd=end_time
FROM sys.query_store_runtime_stats_interval
WHERE runtime_stats_interval_id<>@PreviousIntervalId AND start_time>=@PreviousEnd
  AND start_time<=TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
  AND end_time>TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00')
ORDER BY start_time;
""",
}


def uncomment(sql: str) -> str:
    """Entfernt Kommentare und erhält SQL-Literale einschließlich Kommentar-Suchtag."""
    return re.sub(r"N?'(?:''|[^'])*'|/\*.*?\*/|--[^\n]*",
                  lambda match: " " if match[0].startswith(("/*", "--")) else match[0],
                  sql, flags=re.DOTALL)


def sql_findings(sql: str) -> list[str]:
    code = uncomment(sql)
    normalized = " ".join(code.split())
    findings = [f"Fenstervertrag fehlt: {marker}" for marker in REQUIRED_SQL if marker not in normalized]
    # Snapshot ist die erste Mutation; der vollständige Eigentumsschutz muss davor stehen.
    guard = code.split("INTO lab.QueryStoreBaseline", 1)[0]
    findings.extend(ownership_findings(guard))
    snapshot = re.search(r"SELECT\s+([^;]+?)\s+INTO\s+lab\.QueryStoreBaseline\s+FROM\s+sys\.database_query_store_options", code, re.IGNORECASE)
    required_snapshot = {
        "desired_state", "actual_state", "readonly_reason", "flush_interval_seconds", "interval_length_minutes",
        "max_storage_size_mb", "stale_query_threshold_days", "max_plans_per_query", "query_capture_mode",
        "size_based_cleanup_mode", "wait_stats_capture_mode", "capture_policy_execution_count",
        "capture_policy_total_compile_cpu_time_ms", "capture_policy_total_execution_cpu_time_ms", "capture_policy_stale_threshold_hours",
    }
    if snapshot is None or {item.strip() for item in snapshot[1].split(",")} != required_snapshot:
        findings.append("Ausgangssnapshot muss ausschließlich die vollständige explizite QS-Konfiguration enthalten")
    for name, expected_columns in SCHEMA_COLUMNS.items():
        table = re.search(rf"CREATE TABLE lab\.{name}\((.*?)\n\);", code, re.DOTALL)
        columns = set(re.findall(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s+(?:tinyint|bigint|datetimeoffset|float|nvarchar|varchar|xml)\b", table[1], re.IGNORECASE)) if table else set()
        if columns != expected_columns:
            findings.append(f"lab.{name} muss ausschließlich die vereinbarten skalaren Fenster-/Aggregatspalten enthalten")
        if table and re.search(r"\b(?:nvarchar|varchar|xml|varbinary)\b", table[1], re.IGNORECASE):
            findings.append(f"lab.{name} darf keine Querytexte oder Planinhalte persistieren")
    if code.count("IF @Major>=16 AND OBJECT_ID(N'sys.query_store_query_variant',N'V') IS NOT NULL") != 2:
        findings.append("Beide Variantenzugriffe benötigen den expliziten versionsgebundenen View-Guard")
    # Nach dem Entfernen aller Stringliterale darf die jüngere View nur im OBJECT_ID-Guard verbleiben.
    static_code = re.sub(r"N?'(?:''|[^'])*'", "''", code)
    if "sys.query_store_query_variant" in static_code:
        findings.append("Variantenzugriff muss vollständig in dynamischem SQL verbleiben")
    parent_selection = re.search(r"INSERT #ParentQueries\(QueryId\)\s+(.*?);", code, re.DOTALL)
    if parent_selection is None or " ".join(parent_selection[1].split()) != " ".join(PARENT_QUERY_SELECTION.split()):
        findings.append("Capture-Scope darf ausschließlich die eigene Suchprozedur mit ihrem exakten Kommentar enthalten")
    # Der Kontrollquery darf keine Suchrequests erzeugen. Exakte Poll-Körper
    # binden den festen separaten Batch mit beiden OUTPUT-Bindungen an zwölf
    # Gruppen, eigenen Flush und Deadline vor und nach Probe.
    for variable, probe in POLL_CATALOG_PROBES.items():
        label = "INITIAL_INTERVAL" if variable == "PreviousIntervalId" else "NEXT_INTERVAL"
        before = f"IF SYSUTCDATETIME()>=@PollDeadline BEGIN PRINT 'DGN007_WINDOW_TIMEOUT|{label}'; {TIMEOUT_SUMMARY} END;"
        diagnostic = NEXT_INTERVAL_DIAGNOSTIC if variable == "IntervalId" else ""
        after = f"IF SYSUTCDATETIME()>=@PollDeadline BEGIN PRINT 'DGN007_WINDOW_TIMEOUT|{label}'; {diagnostic} {TIMEOUT_SUMMARY} END;"
        expected = f"{before} {POLL_PULSE} {probe} {after} IF @{variable} IS NOT NULL BREAK;"
        loops = re.findall(rf"WHILE @{variable} IS NULL\s+BEGIN\s+(.*?)\s+WAITFOR DELAY '00:00:01';\s+END;", code, re.DOTALL)
        if len(loops) != 1 or " ".join(loops[0].split()) != " ".join(expected.split()):
            findings.append(f"Poll @{variable} benötigt den exakten isolierten COUNT_BIG-/Flush-/Deadline-Pfad")
    pulse_calls = tuple(re.finditer(r"\s+".join(re.escape(part) for part in PULSE_CALL.split()), code))
    setup_position = code.find("ALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET QUERY_STORE=ON")
    if len(pulse_calls) != 2 or setup_position < 0 or any(call.start() <= setup_position for call in pulse_calls):
        findings.append("Genau zwei feste dynamische Kontrollbatches müssen erst nach dem eigenen Query-Store-Setup ausgeführt werden")
    if len(re.findall(r"\bALTER\s+DATABASE\b", code, re.IGNORECASE)) != 1:
        findings.append("Fensterschnitt darf nur das eigene begrenzte QUERY_STORE-Setup ändern")
    # Nur die fest definierten skalaren Diagnosen zulassen. Zwischen Diagnose und
    # Summary bleiben weitere Statements, insbesondere Mutationen, ausgeschlossen.
    allowed_timeout_bodies = {
        deadline: {TIMEOUT_SUMMARY} | {
            f"PRINT 'DGN007_WINDOW_TIMEOUT|{label}'; {TIMEOUT_SUMMARY}" for label in labels
        }
        for deadline, labels in TIMEOUT_LABELS.items()
    }
    detail = " ".join(NEXT_INTERVAL_DIAGNOSTIC.split())
    allowed_timeout_bodies["PollDeadline"].add(
        f"PRINT 'DGN007_WINDOW_TIMEOUT|NEXT_INTERVAL'; {detail} {TIMEOUT_SUMMARY}")
    timeout_blocks = re.findall(
        r"IF SYSUTCDATETIME\(\)>=@(PollDeadline|PhaseDeadline)\s+BEGIN\s+(.*?)\s+END;", code, re.DOTALL)
    timeout_guards = [deadline for deadline, body in timeout_blocks
                      if " ".join(body.split()) in allowed_timeout_bodies[deadline]]
    if timeout_guards.count("PollDeadline") != 4 or timeout_guards.count("PhaseDeadline") != 4:
        findings.append("Alle vier Poll- und vier Phasengrenzen müssen FAIL_TIMEOUT ausgeben und unmittelbar RETURN ausführen")
    if code.count("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;") != 8:
        findings.append("Fensterschnitt benötigt exakt acht kontrollierte FAIL_TIMEOUT-Zweige")
    for forbidden in FORBIDDEN_SQL:
        if re.search(forbidden, code, re.IGNORECASE):
            findings.append(f"Unzulässiger Fenstereingriff: {forbidden}")
    return findings


def manifest_findings(manifest) -> list[str]:
    contract = QUERY_STORE_WINDOWS_CONTRACT
    if (manifest.demo_id, manifest.run_token, manifest.safety_level, manifest.timeout_seconds, manifest.cleanup_timeout_seconds) != ("DGN-007", "AUTO", "YELLOW", 180, 60):
        return ["Fenstermanifest muss den gelben AUTO-Vertrag mit 180/60 Sekunden verwenden"]
    phases = (*manifest.phases, manifest.cleanup)
    if any(phase is None for phase in phases) or tuple(phase.phase_id for phase in phases) != contract.expected_phases:
        return ["Fenstermanifest benötigt exakt fünf Phasen einschließlich QUERY_STORE_WINDOWS und Cleanup"]
    return [f"Fensterphase weicht ab: {phase.phase_id}" for phase, (_, script, selector, timeout) in zip(phases, contract.phase_specs)
            if phase.kind != "sql" or phase.path != AUTO / script or phase.database_selector != selector
            or phase.timeout_seconds != timeout or not phase.required or not phase.require_summary]


def main() -> int:
    findings = []
    for path in (SQL, QUERY_STORE_WINDOWS_CONTRACT.manifest, WORKFLOW):
        if not path.is_file():
            findings.append(f"Fensterartefakt fehlt: {path.relative_to(ROOT)}")
    if findings:
        print("dgn007-query-store-windows: FAIL\n" + "\n".join(findings))
        return 1
    sql = SQL.read_text(encoding="utf-8")
    findings.extend(sql_findings(sql))
    code = uncomment(sql)
    for marker in REQUIRED_SQL:
        pattern = r"\s+".join(re.escape(part) for part in marker.split())
        mutated = re.sub(pattern, "", code)
        if mutated == code or not sql_findings(mutated):
            findings.append(f"Negative Fensterkontrolle nicht erkannt: {marker}")
    for marker in ("@Project IS NULL", "@Run IS NULL", "DATALENGTH(@Contract)<>DATALENGTH(N'1.0')"):
        if not sql_findings(sql.replace(marker, "")):
            findings.append(f"Negative Eigentumskontrolle nicht erkannt: {marker}")
    for mutation in (
        "\nDBCC FREEPROCCACHE;", "\nALTER DATABASE [SQLPERF_LAB_DGN007_AUTO] SET QUERY_STORE CLEAR;",
        "\nSELECT query_variant_query_id FROM sys.query_store_query_variant;",
        "\nEXEC sys.sp_query_store_force_plan 1,1;",
    ):
        if not sql_findings(sql + mutation):
            findings.append("Negative Eingriffs-/Versionskontrolle nicht erkannt")
    if not sql_findings(sql.replace("WHERE q.object_id=@ObjectId", "WHERE q.object_id=@ObjectId OR q.object_id=0", 1)):
        findings.append("Negative Kontrollquery-Capture-Abgrenzung nicht erkannt")
    for variable in POLL_CATALOG_PROBES:
        loop_start = sql.index(f"WHILE @{variable} IS NULL")
        before, loop_and_after = sql[:loop_start], sql[loop_start:]
        for original, replacement in (
            (PULSE_CALL, ""),
            (PULSE_CALL, "SELECT @Pulse=COUNT_BIG(*) FROM dbo.CaseGroup;"),
            (PULSE_CALL, "EXEC dbo.usp_CaseSearch 8,3;"),
            ("N'@Rows bigint OUTPUT',@Rows=@Pulse OUTPUT", ""),
            ("N'@Rows bigint OUTPUT'", "N'@Rows bigint'"),
            ("@Rows=@Pulse OUTPUT", ""),
            ("@Rows=@Pulse OUTPUT", "@Rows=@Pulse"),
            ("@Rows=@Pulse OUTPUT", "@Rows=@Unbound OUTPUT"),
            ("N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;'", "@UnboundSql"),
            ("N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;'", "N'SELECT COUNT_BIG(*) FROM dbo.CaseGroup;'"),
            ("N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;'", "N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;' + @UnboundSql"),
            ("N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup;'", "N'SELECT @Rows=COUNT_BIG(*) FROM dbo.CaseGroup; DELETE FROM dbo.CaseRequestLog;'"),
            ("@Pulse IS NULL OR @Pulse<>12", "@Pulse IS NULL OR @Pulse<>13"),
            ("@Pulse IS NULL OR @Pulse<>12", "@Pulse<>12"),
            ("EXEC sys.sp_query_store_flush_db;", ""),
            ("EXEC sys.sp_query_store_flush_db;", "DELETE FROM dbo.CaseRequestLog; EXEC sys.sp_query_store_flush_db;"),
            ("IF SYSUTCDATETIME()>=@PollDeadline", "IF 1=0"),
        ):
            pattern = r"\s+".join(re.escape(part) for part in original.split())
            mutated = before + re.sub(pattern, lambda match: replacement, loop_and_after, count=1)
            if mutated == sql or not sql_findings(mutated):
                findings.append(f"Negative Pulse-/Pollkontrolle nicht erkannt: @{variable}: {original}")
    if not sql_findings(sql.replace("AvgCpuUs float NOT NULL", "AvgCpuUs nvarchar(max) NOT NULL")):
        findings.append("Negative Textpersistenzkontrolle nicht erkannt")
    for mutation in (
        sql.replace("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;", "PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT';", 1),
        sql.replace("IF SYSUTCDATETIME()>=@PhaseDeadline", "IF 1=0", 1),
        sql.replace("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;", "THROW 51003,'FAIL_TIMEOUT',1;", 1),
        sql.replace("PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN;", "DELETE FROM lab.IncidentProfile; " + TIMEOUT_SUMMARY, 1),
    ):
        if not sql_findings(mutation):
            findings.append("Negative Timeoutklassifikationskontrolle nicht erkannt")
    manifest = load_manifest(QUERY_STORE_WINDOWS_CONTRACT.manifest)
    findings.extend(manifest_findings(manifest))
    for invalid in (replace(manifest, timeout_seconds=181), replace(manifest, phases=manifest.phases[:3]),
                    replace(manifest, cleanup=None), replace(manifest, phases=manifest.phases + (manifest.phases[-1],))):
        if not manifest_findings(invalid):
            findings.append("Negative Fenstermanifestkontrolle nicht erkannt")
    findings.extend(workflow_findings(WORKFLOW.read_text(encoding="utf-8")))
    if (AUTO / "manifest.json").exists() or (AUTO.parent / "manifest.json").exists():
        findings.append("Fensterschnitt darf keine Capstone-Promotion erzeugen")
    if findings:
        print("dgn007-query-store-windows: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-query-store-windows: PASS (PROJECT_SEMANTIC; keine Incident- oder Capstone-Abnahme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
