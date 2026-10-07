#!/usr/bin/env python3
"""Prüft neutrale Kontrollcaptures; keine Performance- oder Incidentfreigabe."""
from __future__ import annotations

from dataclasses import replace
import re

from validate_dgn007_profile_comparison import (
    AUTO, SQL as PROFILE_SQL, REQUIRED_SQL, FORBIDDEN_SQL, section as profile_section,
    ROOT, WORKFLOW, ownership_findings, workflow_findings, load_manifest,
)
from validate_dgn007_query_store_windows import sql_findings as window_findings, uncomment
from run_dgn007_automated_setup import CONTROL_AB_CONTRACT, CONTROL_BA_CONTRACT, CONTROL_AA_CONTRACT

CONTRACTS = (CONTROL_AB_CONTRACT, CONTROL_BA_CONTRACT, CONTROL_AA_CONTRACT)
WINDOWS = AUTO / "21_Controlled_Query_Store_Windows.sql"
EVIDENCE = AUTO / "35_Control_Evidence.sql"
BASE_WINDOWS = AUTO / "20_Query_Store_Windows.sql"


def normalized(sql: str) -> str:
    return " ".join(uncomment(sql).split())


def section(sql: str, name: str) -> str:
    prefix = "DGN007_CONTROL_" if name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD") else "CONTROL_"
    begin, end = f"/* {prefix}{name}_BEGIN */", f"/* {prefix}{name}_END */"
    if sql.count(begin) != 1 or sql.count(end) != 1 or sql.index(begin) >= sql.index(end):
        raise ValueError(f"Kontrollabschnitt fehlt oder ist mehrfach vorhanden: {name}")
    return uncomment(sql.split(begin, 1)[1].split(end, 1)[0]).strip()


def replace_section(sql: str, name: str, replacement: str = "") -> str:
    section(sql, name)
    return re.sub(r"/\* CONTROL_" + name + r"_BEGIN \*/.*?/\* CONTROL_" + name + r"_END \*/",
                  lambda _: replacement, sql, flags=re.DOTALL)


PARAMETERS = """CREATE TABLE #Parameters(WindowId tinyint NOT NULL,Sequence int NOT NULL,GroupKey int NOT NULL,StatusCode tinyint NOT NULL,ExpectedCount int NOT NULL,PRIMARY KEY(WindowId,Sequence));
INSERT #Parameters(WindowId,Sequence,GroupKey,StatusCode,ExpectedCount)
SELECT c.WindowId,p.Sequence,p.GroupKey,p.StatusCode,p.ExpectedCount
FROM lab.ControlSequence c JOIN
(VALUES('A',1,8,3,228),('A',2,1,3,2286),('A',3,5,3,1144),('A',4,1,1,571),
('B',1,1,3,2286),('B',2,8,3,228),('B',3,5,3,1144),('B',4,1,1,571))
p(ConditionCode,Sequence,GroupKey,StatusCode,ExpectedCount) ON p.ConditionCode=c.ConditionCode;"""
SEQUENCE_MARKERS = (
    "(SELECT COUNT_BIG(*) FROM lab.ControlSequence)<>2",
    "WindowId IS NULL OR WindowId NOT IN (0,1)",
    "ConditionCode IS NULL OR ConditionCode COLLATE Latin1_General_100_BIN2 NOT IN ('A','B')",
    "DATALENGTH(ConditionCode)<>1",
    "NOT EXISTS(SELECT 1 FROM lab.ControlSequence WHERE WindowId=0)",
    "NOT EXISTS(SELECT 1 FROM lab.ControlSequence WHERE WindowId=1)",
    "a.ConditionCode='B' AND b.ConditionCode='B'",
    "PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN;",
)
EVIDENCE_MARKERS = (
    "ROW_NUMBER() OVER(PARTITION BY w.WindowId ORDER BY r.RequestLogId) AS Sequence",
    "r.RequestLogId BETWEEN w.FirstRequestLogId AND w.LastRequestLogId",
    "FROM #OrderedRequests EXCEPT SELECT WindowId,Sequence,GroupKey,StatusCode FROM #Parameters",
    "FROM #Parameters EXCEPT SELECT WindowId,Sequence,GroupKey,StatusCode FROM #OrderedRequests",
    "q.query_plan_hash IS NULL OR DATALENGTH(q.query_plan_hash)<>8",
    "JOIN sys.query_store_plan q ON q.plan_id=p.PlanId AND q.query_id=p.QueryId",
    "WHERE p.ExecutionType=0 AND p.ExecutionCount>0",
    "GROUP BY p.WindowId,p.ParentQueryId,p.QueryId,p.PlanId,q.query_plan_hash",
    "DECLARE @InvalidPlanType bit=0; IF @Major>=16 EXEC sys.sp_executesql",
    "p.plan_type IS NULL OR p.plan_type NOT IN (0,2)",
    "SET @Invalid=1;',N'@Invalid bit OUTPUT',@Invalid=@InvalidPlanType OUTPUT",
    "IF @InvalidPlanType=1 BEGIN PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT'; RETURN; END;",
    "(SELECT COUNT_BIG(*) FROM #ExecutedPlans)=0",
    "COALESCE((SELECT SUM(p.ExecutionCount) FROM #ExecutedPlans p WHERE p.WindowId=w.WindowId),0)<>4",
    "COUNT(DISTINCT p.PlanId) AS ExecutedPlanCount",
    "CONVERT(varchar(18),p.QueryPlanHash,1) AS QueryPlanHashHex,p.ExecutionCount",
    "MAX(CASE WHEN WindowId=0 THEN 1 ELSE 0 END) AS ExecutedInT0",
    "MAX(CASE WHEN WindowId=1 THEN 1 ELSE 0 END) AS ExecutedInT1",
    "GROUP BY ParentQueryId,QueryId,PlanId,QueryPlanHash",
    "N'Kontrollcapture; keine Incidentfreigabe' AS ScopeMessage",
)
REPORTS = {
    "SEQUENCE_REPORT": """SELECT N'DGN007_CONTROL_WINDOW' AS ReportKind,c.WindowId,c.ConditionCode,
    w.RequestCount,w.CapturedExecutions,COUNT(DISTINCT p.PlanId) AS ExecutedPlanCount
    FROM lab.ControlSequence c JOIN lab.IncidentState w ON w.WindowId=c.WindowId
    JOIN #ExecutedPlans p ON p.WindowId=c.WindowId
    GROUP BY c.WindowId,c.ConditionCode,w.RequestCount,w.CapturedExecutions ORDER BY c.WindowId;""",
    "PLAN_REPORT": """SELECT N'DGN007_CONTROL_PLAN' AS ReportKind,p.WindowId,c.ConditionCode,p.ParentQueryId,p.QueryId,p.PlanId,
    CONVERT(varchar(18),p.QueryPlanHash,1) AS QueryPlanHashHex,p.ExecutionCount
    FROM #ExecutedPlans p JOIN lab.ControlSequence c ON c.WindowId=p.WindowId
    ORDER BY p.WindowId,p.ParentQueryId,p.QueryId,p.PlanId;""",
    "PLAN_UNION": """SELECT N'DGN007_CONTROL_PLAN_UNION' AS ReportKind,ParentQueryId,QueryId,PlanId,
    CONVERT(varchar(18),QueryPlanHash,1) AS QueryPlanHashHex,
    MAX(CASE WHEN WindowId=0 THEN 1 ELSE 0 END) AS ExecutedInT0,
    MAX(CASE WHEN WindowId=1 THEN 1 ELSE 0 END) AS ExecutedInT1
    FROM #ExecutedPlans GROUP BY ParentQueryId,QueryId,PlanId,QueryPlanHash
    ORDER BY ParentQueryId,QueryId,PlanId;""",
}


def safety_prefix_findings(sql: str, end: str, *, config: bool = False) -> list[str]:
    """Identische Eingangs-/Eigentumsprüfung übernehmen; nur feste Diagnose und Config-Deadline unterscheiden sich."""
    profile = PROFILE_SQL.read_text(encoding="utf-8")
    expected = profile[:profile.index("DECLARE @ObjectId")]
    actual = sql[:sql.index(end)]
    actual = actual.replace("Unerwartetes Ziel der Kontrollkonfiguration.", "Unerwartetes Ziel des Profilvergleichs.")
    actual = actual.replace("Unerwartetes Ziel der Kontrollevidenz.", "Unerwartetes Ziel des Profilvergleichs.")
    if config:
        actual = actual.replace("DATEADD(second,3,SYSUTCDATETIME())", "DATEADD(second,8,SYSUTCDATETIME())")
    return [] if normalized(actual) == normalized(expected) else ["Kontrollscope benötigt unveränderte Ziel-/Edition-/Isolation-/Budget-/Eigentumsprüfung vor dem ersten Zugriff"]


def sequence_findings(sql: str) -> list[str]:
    code = normalized(section(sql, "SEQUENCE_GUARD"))
    return [f"Kontrollsequenzschutz fehlt: {marker}" for marker in SEQUENCE_MARKERS if marker not in code]


def window_sql_findings(sql: str) -> list[str]:
    """Nur zwei freigegebene Blöcke ersetzen; sämtliche Schutzprüfungen aus 20 wiederverwenden."""
    try:
        findings = sequence_findings(sql)
        if normalized(section(sql, "PARAMETERS")) != normalized(PARAMETERS):
            findings.append("Kontrollparameter benötigen exakt A/B, feste vier Paare und Condition-Join")
        base = BASE_WINDOWS.read_text(encoding="utf-8")
        parameter_block = base[base.index("CREATE TABLE #Parameters"):base.index("CREATE TABLE #Actual")]
        canonical = replace_section(replace_section(sql, "SEQUENCE_GUARD"), "PARAMETERS", parameter_block)
        # Der Producer-Validator prüft diese neuen Abschnitte zusätzlich streng.
        # Außerhalb davon bleibt die vollständige Gleichheit zu 20 erhalten.
        from validate_dgn007_capture_projection import capture_section, request_capture_findings
        findings.extend(request_capture_findings(sql))
        for name in ("FRESH_GUARD", "REQUEST_SCHEMA", "REQUEST_MEASUREMENT"):
            capture_section(canonical, name)
            canonical = re.sub(r"/\* CAPTURE_" + name + r"_BEGIN \*/.*?/\* CAPTURE_" + name + r"_END \*/",
                               "", canonical, flags=re.DOTALL)
        if normalized(canonical) != normalized(base):
            findings.append("Kontrollfenster ändern ausführbaren Code außerhalb der beiden erlaubten Blöcke")
        findings.extend(window_findings(canonical))
        if sql.index("/* CONTROL_SEQUENCE_GUARD_BEGIN */") > sql.index("INTO lab.QueryStoreBaseline"):
            findings.append("Sequenzschutz muss vor Snapshot und erster Query-Store-Mutation stehen")
        return findings
    except (ValueError, IndexError) as error:
        return [str(error)]


def evidence_sql_findings(sql: str) -> list[str]:
    try:
        from validate_dgn007_capture_projection import projection_sql_findings, capture_section
        projection_findings = projection_sql_findings(sql)
        capture_section(sql, "PROJECTION")
        sql = re.sub(r"/\* CAPTURE_PROJECTION_BEGIN \*/.*?/\* CAPTURE_PROJECTION_END \*/",
                     "", sql, flags=re.DOTALL)
        capture_section(sql, "REQUIRED_GUARD")
        sql = re.sub(r"/\* CAPTURE_REQUIRED_GUARD_BEGIN \*/.*?/\* CAPTURE_REQUIRED_GUARD_END \*/",
                     "", sql, flags=re.DOTALL)
        code = normalized(sql)
        findings = [*projection_findings, *sequence_findings(sql)]
        findings.extend(safety_prefix_findings(sql, "DECLARE @ObjectId"))
        findings.extend(ownership_findings(uncomment(sql)[:uncomment(sql).find("DECLARE @ObjectId")]))
        for marker in (*REQUIRED_SQL[:16], *EVIDENCE_MARKERS):
            if marker not in code:
                findings.append(f"Kontrollevidenzvertrag fehlt: {marker}")
        for name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD", "ORDER_ROWS", "ORDER_GUARD",
                     "HASH_GUARD", "ACTIVE_PLANS", "SEQUENCE_REPORT", "PLAN_REPORT", "PLAN_UNION"):
            section(sql, name)
        for name, expected_report in REPORTS.items():
            if normalized(section(sql, name)) != normalized(expected_report):
                findings.append(f"Kontrollreport benötigt exakt begrenzte skalare Spalten aus der aktiven Menge: {name}")
        if normalized(section(sql, "PARAMETERS")) != normalized(PARAMETERS):
            findings.append("Kontrollevidenz muss dieselbe feste Parameterzuordnung validieren")
        profile = PROFILE_SQL.read_text(encoding="utf-8")
        for name in ("WINDOW_GUARD", "REQUEST_GUARD", "METRIC_GUARD"):
            if normalized(section(sql, name)) != normalized(profile_section(profile, name)):
                findings.append(f"Kontrollevidenz muss den bestehenden Profilguard übernehmen: {name}")
        common = sql
        for name in ("SEQUENCE_GUARD", "PARAMETERS", "ORDER_ROWS", "ORDER_GUARD"):
            common = replace_section(common, name)
        expected = profile[profile.index("DECLARE @ObjectId"):profile.index("/* DGN007_PROFILE_WEIGHTED_BEGIN */")]
        actual = common[common.index("DECLARE @ObjectId"):common.index("/* CONTROL_HASH_GUARD_BEGIN */")]
        if normalized(actual) != normalized(expected):
            findings.append("Eigene Parent-/Variantenauswahl und Live-IDs/Counts/Grenzen müssen unverändert erneut geprüft werden")
        deadline = "IF SYSUTCDATETIME()>=@PhaseDeadline BEGIN PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN; END;"
        if "DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,8,SYSUTCDATETIME())" not in code or code.count(deadline) != 2:
            findings.append("Kontrollevidenz benötigt zwei bounded Deadline-Guards mit RETURN")
        if code.find(deadline) > code.find("SELECT N'DGN007_CONTROL_WINDOW'"):
            findings.append("Deadline muss vor der Kontrollausgabe geprüft werden")
        for forbidden in FORBIDDEN_SQL:
            if re.search(forbidden, uncomment(sql), re.IGNORECASE):
                findings.append(f"Unzulässiger Eingriff oder Promotion: {forbidden}")
        static_code = re.sub(r"N?'(?:''|[^'])*'", "''", uncomment(sql))
        if re.search(r"\bplan_type\b", static_code):
            findings.append("PlanType darf ausschließlich dynamisch ab SQL Server 2022 gebunden werden")
        if re.search(r"\bSELECT\s+(?:\w+\.)?\*\s+FROM\b", static_code, re.IGNORECASE):
            findings.append("Kontrollevidenz darf keine unbeschränkten Spalten ausgeben")
        for projection in re.findall(r"\bSELECT\b((?:(?!\bFROM\b).)*)(?:\bFROM\b|;)", static_code, re.DOTALL | re.IGNORECASE):
            if re.search(r"\b(?:query_sql_text|query_plan)\b|^\s*\*\s*$", projection, re.IGNORECASE):
                findings.append("Kontrollevidenz darf keine Querytexte, Plan-XML oder unbeschränkte Spalten ausgeben")
        if re.search(r"(?:ExecutedPlanCount|COUNT\(DISTINCT\s+(?:p\.)?PlanId\))\s*[<>]=?", code):
            findings.append("Planzahl ist ein neutraler Bericht und kein Mindest-/Incidentgate")
        return findings
    except (ValueError, IndexError) as error:
        return [str(error)]


def config_findings(sql: str, order: str) -> list[str]:
    try:
        expected = """CREATE TABLE lab.ControlSequence(
        WindowId tinyint NOT NULL PRIMARY KEY,
        ConditionCode char(1) COLLATE Latin1_General_100_BIN2 NOT NULL,
        CHECK(WindowId IN (0,1)), CHECK(ConditionCode IN ('A','B')) );
        INSERT lab.ControlSequence(WindowId,ConditionCode) VALUES(0,'%s'),(1,'%s');""" % tuple(order)
        block = section(sql, "CONFIG")
        findings = [] if normalized(block) == normalized(expected) else ["Konfiguration benötigt exakt zwei feste AB/BA/AA-Zeilen und Schema-Constraints"]
        guard = uncomment(sql).split("CREATE TABLE lab.ControlSequence", 1)[0]
        findings.extend(safety_prefix_findings(sql, "IF SCHEMA_ID", config=True))
        findings.extend(ownership_findings(guard))
        for marker in (*REQUIRED_SQL[1:10], "DECLARE @PhaseDeadline datetime2(7)=DATEADD(second,3,SYSUTCDATETIME())",
                       "OBJECT_ID(N'lab.ControlSequence') IS NOT NULL", "(SELECT COUNT_BIG(*) FROM dbo.CaseRequestLog)<>4"):
            if marker not in normalized(guard):
                findings.append(f"Konfigurationsschutz fehlt: {marker}")
        code = normalized(sql)
        if code.count("IF SYSUTCDATETIME()>=@PhaseDeadline BEGIN PRINT 'SQLPERF_SUMMARY|FAIL|FAIL_TIMEOUT'; RETURN; END;") != 2:
            findings.append("Konfiguration benötigt zwei kontrollierte Deadline-Guards")
        if f"SELECT N'DGN007_CONTROL_CONFIG' AS ReportKind,'{order}' AS ControlSequence;" not in code:
            findings.append("Konfigurationsreport muss die tatsächliche feste Sequenz ausgeben")
        outside = replace_section(sql, "CONFIG")
        for pattern in (r"\bALTER\b", r"\bDROP\b", r"\b(?:INSERT|UPDATE|DELETE|MERGE|CREATE TABLE)\b", r"\bEXEC\b"):
            if re.search(pattern, uncomment(outside), re.IGNORECASE):
                findings.append("Konfiguration enthält eine nicht freigegebene Mutation")
        return findings
    except ValueError as error:
        return [str(error)]


def manifest_findings(manifest, contract) -> list[str]:
    if (manifest.demo_id, manifest.run_token, manifest.safety_level, manifest.timeout_seconds,
            manifest.cleanup_timeout_seconds) != ("DGN-007", "AUTO", "YELLOW", 180, 60):
        return ["Kontrollmanifest benötigt unverändert AUTO/YELLOW/180/60"]
    phases = (*manifest.phases, manifest.cleanup)
    if any(phase is None for phase in phases) or tuple(phase.phase_id for phase in phases) != contract.expected_phases:
        return ["Kontrollmanifest benötigt exakt acht Phasen einschließlich Cleanup"]
    return [f"Kontrollphase weicht ab: {phase.phase_id}" for phase, (_, script, selector, timeout) in zip(phases, contract.phase_specs)
            if phase.kind != "sql" or phase.path != AUTO / script or phase.database_selector != selector
            or phase.timeout_seconds != timeout or not phase.required or not phase.require_summary]


def main() -> int:
    findings = []
    try:
        findings.extend(window_sql_findings(WINDOWS.read_text(encoding="utf-8")))
        findings.extend(evidence_sql_findings(EVIDENCE.read_text(encoding="utf-8")))
        for order, contract in zip(("AB", "BA", "AA"), CONTRACTS):
            findings.extend(config_findings((AUTO / f"15_Control_{order}.sql").read_text(encoding="utf-8"), order))
            manifest = load_manifest(contract.manifest)
            findings.extend(manifest_findings(manifest, contract))
            for invalid in (replace(manifest, timeout_seconds=181), replace(manifest, cleanup_timeout_seconds=61),
                            replace(manifest, cleanup=None), replace(manifest, phases=manifest.phases[:-1])):
                if not manifest_findings(invalid, contract):
                    findings.append("Negative Kontrollmanifestprüfung nicht erkannt")
        findings.extend(workflow_findings(WORKFLOW.read_text(encoding="utf-8")))
        if (AUTO / "manifest.json").exists() or (AUTO.parent / "manifest.json").exists():
            findings.append("Kontrollcaptures dürfen keine Capstone-Promotion erzeugen")
    except (OSError, ValueError) as error:
        findings.append(str(error))
    if findings:
        print("dgn007-control-capture: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-control-capture: PASS (PROJECT_SEMANTIC; neutrale AB/BA/AA-Captures ohne Incidentgate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
