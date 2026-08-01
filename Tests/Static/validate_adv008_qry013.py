#!/usr/bin/env python3
"""Static contract validation for the ADV-008 QRY-013 slice."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DEMO_ID = "QRY-013"
DEMO = ROOT / "Demos" / "05_Query_Patterns" / "QRY-013_Client_Session_Context"
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
    "lab.usp_Qry013Probe",
    "lab.usp_Qry013Capture",
    "lab.Qry013Evidence",
    "sys.dm_exec_procedure_stats",
    "sys.dm_exec_plan_attributes",
    "set_options",
    "sp_recompile",
    "SKIP_EVIDENCE_MISSING",
    "WARN_EMPIRICAL_VARIANCE",
}
# The two client profiles must differ in exactly one documented SET option.
PROFILE_OPTIONS = (
    "SET ANSI_NULLS ON;",
    "SET ANSI_PADDING ON;",
    "SET ANSI_WARNINGS ON;",
    "SET CONCAT_NULL_YIELDS_NULL ON;",
    "SET QUOTED_IDENTIFIER ON;",
    "SET NUMERIC_ROUNDABORT OFF;",
)
SLIDE_SPEC = ROOT / "Documentation" / "Curriculum" / "ADV_009_SLIDE_SPECIFICATION_M03.md"
SLIDE_IDS = ("SLD-M03-101", "SLD-M03-102", "SLD-M03-103", "SLD-M03-104", "SLD-M03-105")
SLIDE_CLAIMS = ("ADV-CLM-013", "ADV-CLM-014", "ADV-CLM-015", "ADV-CLM-016")
RUNNER = ROOT / "Tests" / "Runtime" / "run_adv008_qry013.py"
WORKFLOW = ROOT / ".github" / "workflows" / "adv008-qry013.yml"


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
            if ch == "'":
                state = "string"
            elif ch == "[":
                state = "bracket"
            elif ch == "-" and nxt == "-":
                state = "line"
                i += 1
            elif ch == "/" and nxt == "*":
                state = "block"
                depth = 1
                i += 1
            elif ch == "(":
                parens += 1
            elif ch == ")":
                parens -= 1
                if parens < 0:
                    return "closing parenthesis without opening parenthesis"
        elif state == "string":
            if ch == "'" and nxt == "'":
                i += 1
            elif ch == "'":
                state = "normal"
        elif state == "bracket":
            if ch == "]" and nxt == "]":
                i += 1
            elif ch == "]":
                state = "normal"
        elif state == "line":
            if ch in "\r\n":
                state = "normal"
        elif state == "block":
            if ch == "/" and nxt == "*":
                depth += 1
                i += 1
            elif ch == "*" and nxt == "/":
                depth -= 1
                i += 1
                if depth == 0:
                    state = "normal"
        i += 1
    if state in {"string", "bracket", "block"}:
        return f"unterminated lexical state: {state}"
    if parens:
        return f"unbalanced parentheses: {parens}"
    return None


def check_bundle(findings: list[str]) -> None:
    if not DEMO.is_dir():
        findings.append(f"{DEMO_ID}: directory missing")
        return

    readme = DEMO / "README.md"
    manifest = DEMO / "manifest.json"
    if not readme.is_file():
        findings.append(f"{DEMO_ID}: README missing")
    if not manifest.is_file():
        findings.append(f"{DEMO_ID}: manifest missing")
        return

    readme_text = read(readme)
    for heading in sorted(README_HEADINGS):
        if heading not in readme_text:
            findings.append(f"{DEMO_ID}: README heading missing {heading}")
    if f"| Demo-ID | `{DEMO_ID}` |" not in readme_text:
        findings.append(f"{DEMO_ID}: traceability missing")
    if "| Sicherheitsstufe | `GREEN` |" not in readme_text:
        findings.append(f"{DEMO_ID}: safety mismatch")
    if "CLIENT_PROFILE_A" not in readme_text or "CLIENT_PROFILE_B" not in readme_text:
        findings.append(f"{DEMO_ID}: neutral client profiles are not documented")
    for claim in SLIDE_CLAIMS:
        if claim not in readme_text:
            findings.append(f"{DEMO_ID}: README claim reference missing {claim}")

    payload = json.loads(read(manifest))
    if payload.get("contract_version") != "1.0" or payload.get("demo_id") != DEMO_ID:
        findings.append(f"{DEMO_ID}: manifest identity invalid")
    if payload.get("run_token") != "LOCAL" or payload.get("safety_level") != "GREEN":
        findings.append(f"{DEMO_ID}: manifest safety or token invalid")
    phases = payload.get("phases", [])
    if [phase.get("id") for phase in phases] != EXPECTED_PHASES:
        findings.append(f"{DEMO_ID}: phase order invalid")
    if payload.get("cleanup", {}).get("id") != "CLEANUP":
        findings.append(f"{DEMO_ID}: cleanup contract missing")
    for phase in [*phases, payload.get("cleanup", {})]:
        script = phase.get("script")
        if not isinstance(script, str) or not (DEMO / script).is_file():
            findings.append(f"{DEMO_ID}: phase script missing: {script}")


def check_sql(findings: list[str]) -> None:
    sql_files = sorted(DEMO.glob("*.sql"))
    if not sql_files:
        findings.append(f"{DEMO_ID}: no SQL phases found")
        return

    combined = "\n".join(read(path) for path in sql_files)
    for marker in sorted(REQUIRED_MARKERS):
        if marker not in combined:
            findings.append(f"{DEMO_ID}: marker missing {marker}")

    for path in sql_files:
        text = read(path)
        error = lexical_error(text)
        if error:
            findings.append(f"{path.relative_to(ROOT).as_posix()}: {error}")
        upper = text.upper()
        for token in sorted(FORBIDDEN_SQL):
            if token in upper:
                findings.append(f"{path.relative_to(ROOT).as_posix()}: forbidden token {token}")

    baseline = read(DEMO / "20_Baseline.sql")
    demonstration = read(DEMO / "30_Demonstration.sql")
    observation = read(DEMO / "40_Observation.sql")
    mitigation = read(DEMO / "50_Mitigation.sql")

    for name, text in (("20_Baseline.sql", baseline), ("40_Observation.sql", observation),
                       ("50_Mitigation.sql", mitigation)):
        if "SET ARITHABORT ON;" not in text:
            findings.append(f"{DEMO_ID}: {name} does not pin the reference session context")
    if "SET ARITHABORT OFF;" not in demonstration:
        findings.append(f"{DEMO_ID}: 30_Demonstration.sql does not use a deviating session context")
    for option in PROFILE_OPTIONS:
        for name, text in (("20_Baseline.sql", baseline), ("30_Demonstration.sql", demonstration)):
            if option not in text:
                findings.append(f"{DEMO_ID}: {name} sets no explicit {option}")

    if "'CMMN'" not in observation:
        findings.append(f"{DEMO_ID}: observation does not switch the parameter value")
    if "'RARE'" not in demonstration:
        findings.append(f"{DEMO_ID}: demonstration must keep the baseline parameter value")

    cleanup_text = read(DEMO / "90_Cleanup.sql")
    for marker in ("SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId", "SQLPERF.RunToken"):
        if marker not in cleanup_text:
            findings.append(f"{DEMO_ID}: cleanup marker missing {marker}")
    if "SINGLE_USER WITH ROLLBACK IMMEDIATE" not in cleanup_text or "DROP DATABASE" not in cleanup_text:
        findings.append(f"{DEMO_ID}: protected removal missing")
    if "DB_ID(@TargetDatabase) IS NULL" not in cleanup_text:
        findings.append(f"{DEMO_ID}: cleanup is not idempotent")


def check_slide_specification(findings: list[str]) -> None:
    if not SLIDE_SPEC.is_file():
        findings.append("slide specification missing")
        return
    text = read(SLIDE_SPEC)
    for slide_id in SLIDE_IDS:
        if f"[SLIDE-ID: {slide_id}]" not in text:
            findings.append(f"slide specification: speaker-note marker missing {slide_id}")
    for claim in SLIDE_CLAIMS:
        if claim not in text:
            findings.append(f"slide specification: claim missing {claim}")
    if "SHA-256" not in text:
        findings.append("slide specification: deck approval constraint not documented")
    if "`PLANNED`" not in text:
        findings.append("slide specification: claim status before deck integration not documented")
    if DEMO_ID not in text:
        findings.append(f"slide specification: canonical demo {DEMO_ID} missing")


def check_runtime(findings: list[str]) -> None:
    if not RUNNER.is_file():
        findings.append("runtime runner missing")
    else:
        text = read(RUNNER)
        try:
            ast.parse(text, filename=str(RUNNER))
        except SyntaxError as exc:
            findings.append(f"runtime runner syntax: {exc}")
        if "QRY013_SUMMARY" not in text:
            findings.append("runtime runner summary prefix missing")
    if not WORKFLOW.is_file():
        findings.append("runtime workflow missing")


def main() -> int:
    findings: list[str] = []
    check_bundle(findings)
    if DEMO.is_dir():
        check_sql(findings)
    check_slide_specification(findings)
    check_runtime(findings)

    if findings:
        print(f"adv008-qry013: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(
        f"adv008-qry013: PASS ({len(EXPECTED_PHASES)} phases, "
        f"{len(SLIDE_IDS)} slide specifications, {len(SLIDE_CLAIMS)} claims)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
