#!/usr/bin/env python3
"""Static contract validation for the implemented QRY-006 NULL-semantics demo."""
from __future__ import annotations

import json
import ast
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DEMO_ID = "QRY-006"
DEMO = ROOT / "Demos/05_Query_Patterns/QRY-006_NULL_Semantics"
REVIEW = ROOT / "Documentation/Project_Planning/QRY_006_NULL_SEMANTICS_DETAIL_REVIEW.md"
SOURCES = ROOT / "Documentation/Research/SOURCE_REGISTER.md"
EXPECTED_PHASES = ["PREFLIGHT", "SETUP", "DEMONSTRATION", "ASSERTION"]
EXPECTED_SCRIPTS = ["00_Preflight.sql", "10_Setup.sql", "30_Demonstration.sql", "40_Result_Assertion.sql", "90_Cleanup.sql"]
FORBIDDEN = ("CREATE INDEX", "ALTER INDEX", "DBCC ", "SHOWPLAN", "STATISTICS XML", "FREEPROCCACHE", "DROPCLEANBUFFERS", "SYS.DM_EXEC_QUERY_PLAN")
RUNNER = ROOT / "Tests/Runtime/run_qry006_null_semantics.py"
WORKFLOW = ROOT / ".github/workflows/qry006-null-semantics.yml"

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def ownership_findings(sql: str, script: str) -> list[str]:
    """Prüft die vollständige Marker-Lesekette und den Guard vor dem Eingriff."""
    findings: list[str] = []
    sql = re.sub(r"--[^\n]*|/\*.*?\*/", "", sql, flags=re.DOTALL)
    normalized = " ".join(sql.split())
    markers = (
        ("Project", "Project", "Project", "N'SQL_PerformanceSchulung'"),
        ("Contract", "Contract", "ContractVersion", "N'1.0'"),
        ("ExistingDemo", "Demo", "DemoId", "CONVERT(nvarchar(max), @DemoId)"),
        ("ExistingRun", "Run", "RunToken", "CONVERT(nvarchar(max), @RunToken)"),
    )
    conditions = []
    for variable, output, property_name, expected in markers:
        for fragment in (
            f"DECLARE @{variable} nvarchar(max);",
            f"@{output}Out=MAX(CASE WHEN name=N''SQLPERF.{property_name}'' THEN CONVERT(nvarchar(max), value) END)",
            f"@{output}Out nvarchar(max) OUTPUT",
            f"@{output}Out=@{variable} OUTPUT",
        ):
            if fragment not in normalized:
                findings.append(f"{script}: vollständiger Marker-Lesepfad fehlt: {variable}")
        conditions.append(
            f"@{variable} IS NULL OR @{variable} COLLATE Latin1_General_100_BIN2 <> {expected} "
            f"OR DATALENGTH(@{variable}) <> DATALENGTH({expected})"
        )
    error = "51002, 'FAIL_STATE:" if script == "10_Setup.sql" else "51004, 'FAIL_CLEANUP:"
    guard = "IF " + " OR ".join(conditions) + " THROW " + error
    if guard not in normalized:
        findings.append(f"{script}: fail-closed Marker-Guard fehlt oder ist unvollständig")
    elif normalized.index(guard) > normalized.index("SET @Sql = N'ALTER DATABASE"):
        findings.append(f"{script}: Marker-Guard muss vor ALTER/DROP DATABASE stehen")
    return findings

def main() -> int:
    findings: list[str] = []
    if not DEMO.is_dir(): findings.append("QRY-006 demo directory is missing")
    for path in (REVIEW, SOURCES):
        if not path.is_file(): findings.append(f"missing {path.relative_to(ROOT)}")
    manifest_path, readme_path = DEMO / "manifest.json", DEMO / "README.md"
    if not manifest_path.is_file() or not readme_path.is_file():
        findings.append("QRY-006 manifest or README is missing")
    else:
        manifest = json.loads(read(manifest_path))
        if manifest.get("contract_version") != "1.0" or manifest.get("demo_id") != DEMO_ID: findings.append("manifest identity is invalid")
        if manifest.get("run_token") != "LOCAL" or manifest.get("safety_level") != "GREEN": findings.append("manifest safety or checked-in token is invalid")
        if [item.get("id") for item in manifest.get("phases", [])] != EXPECTED_PHASES: findings.append("manifest phase order is invalid")
        if manifest.get("cleanup", {}).get("id") != "CLEANUP": findings.append("cleanup phase is missing")
        scripts = [item.get("script") for item in manifest.get("phases", [])] + [manifest.get("cleanup", {}).get("script")]
        if scripts != EXPECTED_SCRIPTS: findings.append("manifest scripts are not the minimal QRY-006 phase set")
        readme = read(readme_path)
        for marker in ("`IMPLEMENTED`", "lokale Docker-Runtime-Matrix bestanden", "Runtime-Gate noch ausstehend", "`TSQL_TESTDB`", "`GREEN`", "2019", "150", "2022", "160", "2025", "170", "keine Aussage über Performance", "Eine Mitigation-Phase ist absichtlich nicht vorhanden", "`SRC-069`", "`SRC-070`", "`SRC-071`"):
            if marker not in readme: findings.append(f"README marker missing: {marker}")
    for script in EXPECTED_SCRIPTS:
        if not (DEMO / script).is_file(): findings.append(f"phase script missing: {script}")
    if not findings:
        combined = "\n".join(read(DEMO / script) for script in EXPECTED_SCRIPTS)
        for marker in ("(1), (2), (3)", "(1), (NULL)", "NOT IN", "NOT EXISTS", "ChildKey IS NOT NULL", "(VALUES (2), (3))", "SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId", "SQLPERF.RunToken", "DB_ID(@TargetDatabase) IS NULL", "SINGLE_USER WITH ROLLBACK IMMEDIATE", "DROP DATABASE"):
            if marker not in combined: findings.append(f"SQL contract marker missing: {marker}")
        for forbidden in FORBIDDEN:
            if forbidden in combined.upper(): findings.append(f"forbidden performance or plan token: {forbidden}")
        for script in ("10_Setup.sql", "90_Cleanup.sql"):
            findings.extend(ownership_findings(read(DEMO / script), script))
        if (DEMO / "50_Mitigation.sql").exists(): findings.append("QRY-006 must not add a mitigation phase")
    if SOURCES.is_file():
        sources = read(SOURCES)
        for source_id in ("SRC-069", "SRC-070", "SRC-071"):
            rows = [line for line in sources.splitlines() if f"| `{source_id}` |" in line]
            if len(rows) != 1 or "| PRIMARY |" not in rows[0] or "`QRY-006`" not in rows[0]: findings.append(f"source binding invalid: {source_id}")
    if not RUNNER.is_file():
        findings.append("runtime runner missing")
    else:
        runner = read(RUNNER)
        try:
            ast.parse(runner, filename=str(RUNNER))
        except SyntaxError as exc:
            findings.append(f"runtime runner syntax: {exc}")
        for marker in ("QRY006_SUMMARY", "repetition in (1, 2)", "assert_database_absent", "child_environment", "execution_target.redact", "expected-major"):
            if marker not in runner:
                findings.append(f"runtime runner marker missing: {marker}")
    if not WORKFLOW.is_file():
        findings.append("runtime workflow missing")
    else:
        workflow = read(WORKFLOW)
        for marker in ("2019", "compatibility_level: 150", "2022", "compatibility_level: 160", "2025", "compatibility_level: 170", "run_qry006_null_semantics.py", "SQLCMDPASSWORD"):
            if marker not in workflow:
                findings.append(f"runtime workflow marker missing: {marker}")
        for forbidden in ("SQL_Server_Lab", "READY_FOR_USER", "DGN-007"):
            if forbidden in workflow:
                findings.append(f"runtime workflow must not promote an interactive scenario: {forbidden}")
    if findings:
        print(f"qry006-null-semantics: FAIL ({len(findings)} finding(s))")
        print("\n".join(f"- {item}" for item in findings))
        return 1
    print("qry006-null-semantics: PASS (implemented GREEN result contract; local Docker matrix passed; runtime gate pending)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
