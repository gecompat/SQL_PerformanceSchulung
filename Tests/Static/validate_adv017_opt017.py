#!/usr/bin/env python3
"""Static contract for the W-ADV-017 OPT-017 slice."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "Demos" / "04_Optimizer_Statistics_Plans" / "OPT-017_Parallelism_Skew"
RUNNER = ROOT / "Tests" / "Runtime" / "run_adv017_opt017.py"
WORKFLOW = ROOT / ".github" / "workflows" / "adv017-opt017.yml"
EXPECTED = ["PREFLIGHT", "SETUP", "BASELINE", "DEMONSTRATION", "OBSERVATION", "MITIGATION", "COMPARISON"]


def main() -> int:
    findings: list[str] = []
    required = ["manifest.json", "README.md", "00_Preflight.sql", "10_Setup.sql", "20_Baseline.sql", "30_Demonstration.sql", "40_Observation.sql", "50_Mitigation.sql", "60_Comparison.sql", "90_Cleanup.sql"]
    for name in required:
        if not (DEMO / name).is_file():
            findings.append(f"missing {name}")
    if (DEMO / "manifest.json").is_file():
        manifest = json.loads((DEMO / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("demo_id") != "OPT-017" or manifest.get("safety_level") != "YELLOW":
            findings.append("manifest identity or safety mismatch")
        if [phase["id"] for phase in manifest.get("phases", [])] != EXPECTED:
            findings.append("phase order mismatch")
        if manifest.get("timeout_seconds", 0) <= 0:
            findings.append("positive runtime budget missing")
    sql = "\n".join(path.read_text(encoding="utf-8") for path in DEMO.glob("*.sql")) if DEMO.is_dir() else ""
    for marker in ("VisibleCpu", "SKIP_RESOURCE_PROFILE", "SKIP_EVIDENCE_MISSING", "WARN_EMPIRICAL_VARIANCE", "LAST_QUERY_PLAN_STATS", "DegreeOfParallelism", "Repartition Streams", "RunTimeCountersPerThread", "SkewRatio", "MAXDOP 4", "MAXDOP 1", "[RowCount]", "StopRequested", "SQLPERF.Project", "DROP DATABASE"):
        if marker.lower() not in sql.lower():
            findings.append(f"SQL marker missing: {marker}")
    for forbidden in ("DBCC FREEPROCCACHE", "DBCC DROPCLEANBUFFERS", "sp_configure", "ALTER SERVER CONFIGURATION", "KILL "):
        if forbidden.lower() in sql.lower():
            findings.append(f"forbidden server-wide action: {forbidden}")
    if RUNNER.is_file():
        try:
            ast.parse(RUNNER.read_text(encoding="utf-8"), filename=str(RUNNER))
        except SyntaxError as exc:
            findings.append(f"runner syntax: {exc}")
        runner = RUNNER.read_text(encoding="utf-8")
        for marker in ("OPT017_STAGE", "OPT017_SUMMARY", "SKIP_RESOURCE_PROFILE", "SKIP_EVIDENCE_MISSING", "WARN"):
            if marker not in runner:
                findings.append(f"runner marker missing: {marker}")
    else:
        findings.append("runtime runner missing")
    if not WORKFLOW.is_file():
        findings.append("workflow missing")
    else:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for marker in ("login_ready=0", 'docker exec -e "SQLCMDPASSWORD=${password}"', 'SELECT 1;'):
            if marker not in workflow:
                findings.append(f"workflow login-readiness probe missing: {marker}")
    if findings:
        print(f"adv017-opt017: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("adv017-opt017: PASS (YELLOW PARALLEL profile; Actual DOP; exchanges; thread skew; serial counterprobe)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
