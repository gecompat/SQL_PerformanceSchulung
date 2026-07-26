#!/usr/bin/env python3
"""Static contract validation for the first ADV-008 runtime slice."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DEMOS = {
    "OPT-015": ROOT / "Demos" / "04_Optimizer_Statistics_Plans" / "OPT-015_Plan_Properties",
    "OPT-016": ROOT / "Demos" / "04_Optimizer_Statistics_Plans" / "OPT-016_Rebind_Rewind_Spools",
}
EXPECTED_PHASES = ["PREFLIGHT", "SETUP", "BASELINE", "DEMONSTRATION", "OBSERVATION", "MITIGATION", "COMPARISON"]
README_HEADINGS = {
    "## 1. Lernziel", "## 2. Fachliche Kernaussage", "## 3. Nichtziel",
    "## 4. Voraussetzungen", "## 5. Sicherheits- und Abbruchrahmen",
    "## 6. Synthetisches Datenmodell", "## 7. Ablauf", "## 8. Erwartete Beobachtung",
    "## 9. Interpretation", "## 10. Cleanup und Wiederherstellung", "## 11. Tests",
    "## 12. Bekannte Grenzen", "## 13. Quellen", "## 14. Traceability",
}
FORBIDDEN_SQL = {
    "DBCC FREEPROCCACHE", "DBCC DROPCLEANBUFFERS", "DBCC FLUSHPROCINDB",
    "DBCC SQLPERF", "XP_CMDSHELL", "SHUTDOWN", "ALTER SERVER CONFIGURATION",
    "SP_CONFIGURE", "EVENT_FILE", "KILL ", "WITH (NOLOCK)", "WITH(NOLOCK)", "QUERYTRACEON",
}
REQUIRED_MARKERS = {
    "OPT-015": {"LAST_QUERY_PLAN_STATS", "sys.dm_exec_query_plan_stats", "OptimizerStatsUsage", "ActualRowsRead", "UPDATE STATISTICS", "NORECOMPUTE"},
    "OPT-016": {"LAST_QUERY_PLAN_STATS", "sys.dm_exec_query_plan_stats", "OuterReferences", "ActualRebinds", "ActualRewinds", "SKIP_PLAN_SHAPE_NOT_PRODUCED", "IX_WorkItemDetail_Group_Sequence"},
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def lexical_error(text: str) -> str | None:
    state = "normal"
    parens = 0
    depth = 0
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if state == "normal":
            if ch == "'": state = "string"
            elif ch == "[": state = "bracket"
            elif ch == "-" and nxt == "-": state = "line"; i += 1
            elif ch == "/" and nxt == "*": state = "block"; depth = 1; i += 1
            elif ch == "(": parens += 1
            elif ch == ")":
                parens -= 1
                if parens < 0: return "closing parenthesis without opening parenthesis"
        elif state == "string":
            if ch == "'" and nxt == "'": i += 1
            elif ch == "'": state = "normal"
        elif state == "bracket":
            if ch == "]" and nxt == "]": i += 1
            elif ch == "]": state = "normal"
        elif state == "line":
            if ch in "\r\n": state = "normal"
        elif state == "block":
            if ch == "/" and nxt == "*": depth += 1; i += 1
            elif ch == "*" and nxt == "/":
                depth -= 1; i += 1
                if depth == 0: state = "normal"
        i += 1
    if state in {"string", "bracket", "block"}: return f"unterminated lexical state: {state}"
    if parens: return f"unbalanced parentheses: {parens}"
    return None


def validate_demo(demo_id: str, root: Path) -> list[str]:
    findings: list[str] = []
    readme = root / "README.md"
    manifest = root / "manifest.json"
    if not root.is_dir(): return [f"{demo_id}: directory missing"]
    if not readme.is_file(): findings.append(f"{demo_id}: README missing")
    if not manifest.is_file(): findings.append(f"{demo_id}: manifest missing"); return findings
    readme_text = read(readme)
    for heading in README_HEADINGS:
        if heading not in readme_text: findings.append(f"{demo_id}: README heading missing {heading}")
    if f"| Demo-ID | `{demo_id}` |" not in readme_text: findings.append(f"{demo_id}: traceability missing")
    if "| Sicherheitsstufe | `GREEN` |" not in readme_text: findings.append(f"{demo_id}: safety mismatch")
    if "sys.dm_exec_query_plan_stats" not in readme_text: findings.append(f"{demo_id}: official actual-plan source missing")

    payload = json.loads(read(manifest))
    if payload.get("contract_version") != "1.0" or payload.get("demo_id") != demo_id: findings.append(f"{demo_id}: manifest identity invalid")
    if payload.get("run_token") != "LOCAL" or payload.get("safety_level") != "GREEN": findings.append(f"{demo_id}: manifest safety or token invalid")
    phases = payload.get("phases", [])
    if [p.get("id") for p in phases] != EXPECTED_PHASES: findings.append(f"{demo_id}: phase order invalid")
    if payload.get("cleanup", {}).get("id") != "CLEANUP": findings.append(f"{demo_id}: cleanup contract missing")
    for phase in [*phases, payload.get("cleanup", {})]:
        script = phase.get("script")
        if not isinstance(script, str) or not (root / script).is_file(): findings.append(f"{demo_id}: phase script missing: {script}")

    combined = "\n".join(read(path) for path in sorted(root.glob("*.sql")))
    for marker in REQUIRED_MARKERS[demo_id]:
        if marker not in combined: findings.append(f"{demo_id}: marker missing {marker}")
    if "ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON" not in combined: findings.append(f"{demo_id}: scoped plan stats opt-in missing")
    for sql_file in sorted(root.glob("*.sql")):
        text = read(sql_file)
        error = lexical_error(text)
        if error: findings.append(f"{sql_file.relative_to(ROOT)}: {error}")
        upper = text.upper()
        for token in FORBIDDEN_SQL:
            if token in upper: findings.append(f"{sql_file.relative_to(ROOT)}: forbidden token {token}")
    cleanup_text = read(root / "90_Cleanup.sql")
    for marker in ("SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId", "SQLPERF.RunToken"):
        if marker not in cleanup_text: findings.append(f"{demo_id}: cleanup marker missing {marker}")
    if "SINGLE_USER WITH ROLLBACK IMMEDIATE" not in cleanup_text or "DROP DATABASE" not in cleanup_text: findings.append(f"{demo_id}: protected removal missing")
    return findings


def main() -> int:
    findings: list[str] = []
    for demo_id, root in DEMOS.items(): findings.extend(validate_demo(demo_id, root))
    runner = ROOT / "Tests" / "Runtime" / "run_adv008_opt015_opt016.py"
    workflow = ROOT / ".github" / "workflows" / "adv008-opt015-opt016.yml"
    if not runner.is_file(): findings.append("runtime runner missing")
    else:
        try: ast.parse(read(runner), filename=str(runner))
        except SyntaxError as exc: findings.append(f"runtime runner syntax: {exc}")
    if not workflow.is_file(): findings.append("runtime workflow missing")
    if findings:
        print(f"ADV-008 OPT-015/016 static contracts: FAIL ({len(findings)} finding(s))")
        for finding in findings: print(f"- {finding}")
        return 1
    print("ADV-008 OPT-015/016 static contracts: PASS (2 demos, 16 SQL files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
