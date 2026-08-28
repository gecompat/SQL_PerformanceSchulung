#!/usr/bin/env python3
"""Static contracts for the W-DGN-001 Query Store and XE pilots."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Demos" / "07_Query_Store_Extended_Events"
DEMOS = {
    "DGN-003": (BASE / "DGN-003_Query_Store_History", "GREEN"),
    "DGN-005": (BASE / "DGN-005_Bounded_Extended_Events", "YELLOW"),
}
ALLOWED_CODES = {
    "OK", "WARN_EMPIRICAL_VARIANCE", "SKIP_VERSION", "SKIP_PERMISSION",
    "SKIP_EVIDENCE_MISSING", "FAIL_CONTRACT", "FAIL_SAFETY", "FAIL_STATE",
    "FAIL_CLEANUP", "FAIL_RESULT_CONTRACT",
}
SUMMARY = re.compile(r"SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)")


def main() -> int:
    findings: list[str] = []
    for demo_id, (directory, safety) in DEMOS.items():
        manifest_path = directory / "manifest.json"
        readme_path = directory / "README.md"
        if not manifest_path.is_file() or not readme_path.is_file():
            findings.append(f"{demo_id}: manifest or README missing")
            continue
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if payload.get("demo_id") != demo_id or payload.get("safety_level") != safety:
            findings.append(f"{demo_id}: identity or safety mismatch")
        phases = [*payload.get("phases", []), payload.get("cleanup", {})]
        for phase in phases:
            script = phase.get("script")
            path = directory / str(script)
            if not path.is_file():
                findings.append(f"{demo_id}: phase script missing: {script}")
                continue
            if phase.get("require_summary") is not True:
                findings.append(f"{demo_id}: summary not required for {phase.get('id')}")
            text = path.read_text(encoding="utf-8")
            summaries = SUMMARY.findall(text)
            if not summaries:
                findings.append(f"{demo_id}: summary missing in {script}")
            for _, code in summaries:
                if code not in ALLOWED_CODES:
                    findings.append(f"{demo_id}: non-FWK-012 code {code} in {script}")
        readme = readme_path.read_text(encoding="utf-8")
        for heading in range(1, 15):
            if f"## {heading}." not in readme:
                findings.append(f"{demo_id}: README section {heading} missing")

    dgn003 = "\n".join(path.read_text(encoding="utf-8") for path in DEMOS["DGN-003"][0].glob("*.sql"))
    for marker in ("QUERY_STORE = ON", "sys.query_store_query", "sys.query_store_plan", "sys.query_store_runtime_stats", "sys.query_store_wait_stats"):
        if marker not in dgn003:
            findings.append(f"DGN-003: marker missing {marker}")
    if "sp_query_store_force_plan" in dgn003.lower() or "sys.sp_query_store_set_hints" in dgn003.lower():
        findings.append("DGN-003: DGN-004 plan-control scope leaked into pilot")

    dgn005 = "\n".join(path.read_text(encoding="utf-8") for path in DEMOS["DGN-005"][0].glob("*.sql"))
    for marker in ("sqlserver.error_reported", "package0.ring_buffer", "MAX_MEMORY=(1024)", "STARTUP_STATE=OFF", "MAX_DURATION=300 SECONDS", "@Major>=17", "SQLPERF_"):
        if marker not in dgn005:
            findings.append(f"DGN-005: marker missing {marker}")
    if "event_file" in dgn005.lower() or ".xel" in dgn005.lower():
        findings.append("DGN-005: persistent XE target is forbidden")

    if findings:
        print(f"dgn-pilots: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("dgn-pilots: PASS (DGN-003 GREEN; DGN-005 YELLOW; 15 SQL phases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
