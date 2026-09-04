#!/usr/bin/env python3
"""Static contract validation for the ADV-008 OPT-010 slice."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DEMO_ID = "OPT-010"
DEMO = ROOT / "Demos" / "04_Optimizer_Statistics_Plans" / "OPT-010_Optional_Parameter_Plans"
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
    "SYS.QUERY_STORE_PLAN", "SYS.QUERY_STORE_QUERY_VARIANT",
    "SET ANSI_NULLS OFF", "PARAMETER_SENSITIVE_PLAN_OPTIMIZATION",
}
DIRECT_EXECUTION = re.compile(r"\bEXEC(?:UTE)?\s*\(", re.IGNORECASE)
# Only the codes of FWK-012 are admissible; feature-specific inventions are rejected.
ALLOWED_STATUS_CODES = {
    "OK",
    "WARN_ENVIRONMENT_DETAIL_SUPPRESSED",
    "WARN_RESOURCE_PROBE_APPROXIMATE",
    "WARN_EMPIRICAL_VARIANCE",
    "WARN_OPTIONAL_EVIDENCE_SKIPPED",
    "SKIP_VERSION",
    "SKIP_COMPATIBILITY_LEVEL",
    "SKIP_EDITION",
    "SKIP_PLATFORM",
    "SKIP_PERMISSION",
    "SKIP_CONFIGURATION",
    "SKIP_RESOURCE_PROFILE",
    "SKIP_MANUAL_APPROVAL",
    "SKIP_EVIDENCE_MISSING",
    "SKIP_TOOL_MISSING",
    "FAIL_CONTRACT",
    "FAIL_SAFETY",
    "FAIL_STATE",
    "FAIL_TIMEOUT",
    "FAIL_EXECUTION",
    "FAIL_CLEANUP",
    "FAIL_RESULT_CONTRACT",
}
SUMMARY_LINE = re.compile(r"SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z_]+)")
REQUIRED_MARKERS = {
    "lab.usp_Opt010SearchSelectiveFirst",
    "lab.usp_Opt010SearchNullFirst",
    "lab.usp_Opt010SearchOppo",
    "lab.usp_Opt010SearchOptOut",
    "lab.usp_Opt010Capture",
    "lab.Opt010Evidence",
    "lab.OppoListing",
    "OPTIONAL_PARAMETER_OPTIMIZATION",
    "DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION",
    "sys.dm_exec_cached_plans",
    "sys.dm_exec_sql_text",
    "sys.dm_exec_query_plan",
    "sys.dm_exec_query_stats",
    "sp_recompile",
    "OptionalParameterPredicate",
    "SensitivePredicatePlanCount",
    "QueryVariantID",
    "SET ANSI_NULLS ON",
    "SKIP_EVIDENCE_MISSING",
    "WARN_EMPIRICAL_VARIANCE",
}
PHASE_PROCEDURES = {
    "20_Baseline.sql": "lab.usp_Opt010SearchSelectiveFirst",
    "30_Demonstration.sql": "lab.usp_Opt010SearchNullFirst",
    "50_Mitigation.sql": "lab.usp_Opt010SearchOppo",
    "60_Comparison.sql": "lab.usp_Opt010SearchOptOut",
}
SLIDE_SPEC = ROOT / "Documentation" / "Curriculum" / "ADV_011_SLIDE_SPECIFICATION_M03_LO08_OPPO.md"
SLIDE_IDS = ("SLD-M03-131", "SLD-M03-132", "SLD-M03-133", "SLD-M03-134")
SLIDE_CLAIMS = ("ADV-CLM-020",)
RUNNER = ROOT / "Tests" / "Runtime" / "run_adv008_opt010.py"
WORKFLOW = ROOT / ".github" / "workflows" / "adv008-opt010.yml"


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
    if "| Status | `VALIDATED` |" not in readme_text or "Actions-Lauf 30702590969" not in readme_text:
        findings.append(f"{DEMO_ID}: validated runtime evidence is not synchronized")
    for claim in SLIDE_CLAIMS:
        if claim not in readme_text:
            findings.append(f"{DEMO_ID}: README claim reference missing {claim}")
    if "QRY-004" not in readme_text or "OPT-009" not in readme_text:
        findings.append(f"{DEMO_ID}: README does not delimit the neighbouring demos")
    if "Compatibility Level | 170" not in readme_text:
        findings.append(f"{DEMO_ID}: README does not pin the required compatibility level")
    if "gleichm" not in readme_text:
        findings.append(f"{DEMO_ID}: README does not state the uniform distribution rationale")
    if "ANSI_NULLS" not in readme_text or "RECOMPILE" not in readme_text:
        findings.append(f"{DEMO_ID}: README does not document the documented exclusion reasons")
    if "SKIP_VERSION" not in readme_text:
        findings.append(f"{DEMO_ID}: README does not document the controlled version skip")

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
        if phase and phase.get("require_summary") is not True:
            findings.append(f"{DEMO_ID}: phase without summary requirement: {phase.get('id')}")


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
        name = path.relative_to(ROOT).as_posix()
        error = lexical_error(text)
        if error:
            findings.append(f"{name}: {error}")
        upper = text.upper()
        for token in sorted(FORBIDDEN_SQL):
            if token in upper:
                findings.append(f"{name}: forbidden token {token}")
        if DIRECT_EXECUTION.search(text):
            findings.append(f"{name}: dynamic SQL must run through sys.sp_executesql only")
        if "SQLPERF_SUMMARY" not in text:
            findings.append(f"{name}: summary line missing")
        for _, code in SUMMARY_LINE.findall(text):
            if code not in ALLOWED_STATUS_CODES:
                findings.append(f"{name}: status code outside FWK-012: {code}")

    preflight = read(DEMO / "00_Preflight.sql")
    setup = read(DEMO / "10_Setup.sql")
    observation = read(DEMO / "40_Observation.sql")
    mitigation = read(DEMO / "50_Mitigation.sql")
    comparison = read(DEMO / "60_Comparison.sql")

    if "@MajorVersion < 17" not in preflight or "SKIP_VERSION" not in preflight:
        findings.append(f"{DEMO_ID}: preflight does not skip versions without the feature")
    if "SKIP_PERMISSION" not in preflight:
        findings.append(f"{DEMO_ID}: preflight does not guard the diagnostic permission")

    if "COMPATIBILITY_LEVEL" not in setup or "WHEN 17 THEN 170" not in setup:
        findings.append(f"{DEMO_ID}: setup does not pin the compatibility level")
    if "OPTIONAL_PARAMETER_OPTIMIZATION = OFF" not in setup:
        findings.append(f"{DEMO_ID}: setup does not establish the disabled start state")
    if "WITH FULLSCAN" not in setup:
        findings.append(f"{DEMO_ID}: setup does not refresh the statistics deterministically")
    if setup.count("CREATE PROCEDURE lab.usp_Opt010Search") != 4:
        findings.append(f"{DEMO_ID}: exactly four comparison procedures are expected")
    if setup.count("USE HINT ('DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION')") != 1:
        findings.append(f"{DEMO_ID}: exactly one procedure must opt out at query level")
    if setup.count("OR @AgentId IS NULL") != 4:
        findings.append(f"{DEMO_ID}: all four comparison objects must share the optional predicate")
    if "THROW 51002" not in setup:
        findings.append(f"{DEMO_ID}: setup does not verify the synthetic distribution")

    for script, procedure in PHASE_PROCEDURES.items():
        text = read(DEMO / script)
        if procedure not in text:
            findings.append(f"{DEMO_ID}: {script} must execute {procedure}")
        for other in set(PHASE_PROCEDURES.values()) - {procedure}:
            if other in text:
                findings.append(f"{DEMO_ID}: {script} must not mix in {other}")

    if "OPTIONAL_PARAMETER_OPTIMIZATION = ON" not in mitigation:
        findings.append(f"{DEMO_ID}: mitigation does not enable the optimisation")
    if "@Variants < 2" not in mitigation:
        findings.append(f"{DEMO_ID}: mitigation does not require at least two query variants")
    if "@OptionalPredicatePlans = 0" not in mitigation:
        findings.append(f"{DEMO_ID}: mitigation does not require an optional parameter predicate")
    if "@SensitivePredicatePlans > 0" not in mitigation:
        findings.append(f"{DEMO_ID}: mitigation does not separate the two multi-plan features")
    if "SKIP_EVIDENCE_MISSING" not in mitigation:
        findings.append(f"{DEMO_ID}: mitigation does not degrade controlled when the feature does not apply")

    if "DispatcherPlanCount" not in observation:
        findings.append(f"{DEMO_ID}: observation does not prove the absence of a dispatcher plan")
    if "COMPILE_ORDER_NEUTRALITY" not in observation:
        findings.append(f"{DEMO_ID}: observation does not evaluate the compile order neutrality")

    demonstration = read(DEMO / "30_Demonstration.sql")
    if "@BaselineSelectiveReads" not in demonstration:
        findings.append(f"{DEMO_ID}: demonstration does not compare against the baseline compile order")

    for name, text in (("20_Baseline.sql", read(DEMO / "20_Baseline.sql")),
                       ("30_Demonstration.sql", demonstration),
                       ("40_Observation.sql", observation),
                       ("50_Mitigation.sql", mitigation),
                       ("60_Comparison.sql", comparison)):
        if "THROW 51006" not in text:
            findings.append(f"{DEMO_ID}: {name} does not enforce the result contract")
    if "ResultChecksum" not in comparison:
        findings.append(f"{DEMO_ID}: comparison does not verify result equality")
    if "@OptOutDispatchers" not in comparison:
        findings.append(f"{DEMO_ID}: comparison does not verify the query level opt out")
    if "DOCUMENTED_LIMITS" not in comparison:
        findings.append(f"{DEMO_ID}: comparison does not name the documented exclusion reasons")

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
    if DEMO_ID not in text:
        findings.append(f"slide specification: canonical demo {DEMO_ID} missing")
    if "OPT-009" not in text:
        findings.append("slide specification: delimitation against the PSP block missing")
    if "QRY-004" not in text:
        findings.append("slide specification: link to the preceding deep-dive block missing")


def check_runtime(findings: list[str]) -> None:
    if not RUNNER.is_file():
        findings.append("runtime runner missing")
    else:
        text = read(RUNNER)
        try:
            ast.parse(text, filename=str(RUNNER))
        except SyntaxError as exc:
            findings.append(f"runtime runner syntax: {exc}")
        if "OPT010_SUMMARY" not in text:
            findings.append("runtime runner summary prefix missing")
        if "SKIP_VERSION" not in text:
            findings.append("runtime runner does not accept the controlled version skip")
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
        print(f"adv008-opt010: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(
        f"adv008-opt010: PASS ({len(EXPECTED_PHASES)} phases, {len(PHASE_PROCEDURES)} comparison objects, "
        f"{len(SLIDE_IDS)} slide specifications, {len(SLIDE_CLAIMS)} claim)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
