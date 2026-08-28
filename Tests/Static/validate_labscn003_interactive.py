#!/usr/bin/env python3
"""Static contract for the CON-004 interactive lifecycle."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "Tools" / "PerformanceTrainingScenario" / "PerformanceTrainingScenario.psm1"
MANIFEST = ROOT / "Tools" / "PerformanceTrainingScenario" / "PerformanceTrainingScenario.psd1"
SCENARIO = ROOT / "Scenarios" / "CON-004" / "scenario.json"


def main() -> int:
    findings: list[str] = []
    for path in (MODULE, MANIFEST, SCENARIO):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    if findings:
        print("labscn003: FAIL")
        return 1
    text = MODULE.read_text(encoding="utf-8")
    for marker in (
        "Get-PerformanceTrainingScenario", "Start-PerformanceTrainingScenario",
        "Reset-PerformanceTrainingScenario", "Remove-PerformanceTrainingScenario",
        "READY_FOR_USER", "Test-SqlServerLabManifest", "New-SqlServerLab",
        "Get-SqlServerLab", "Remove-SqlServerLab", "SQLCMDPASSWORD",
    ):
        if marker not in text:
            findings.append(f"module marker missing: {marker}")
    for forbidden in ("docker run", "podman run", "-P',", '"-P"'):
        if forbidden.lower() in text.lower():
            findings.append(f"forbidden provisioning/password path: {forbidden}")
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    if scenario.get("safetyLevel") != "YELLOW" or scenario.get("interactive", {}).get("readyState") != "READY_FOR_USER":
        findings.append("CON-004 safety or ready state mismatch")
    roles = [item["role"] for item in scenario["orchestration"]["manual"]["sessionScripts"]]
    if roles != ["HEAD", "MIDDLE", "LEAF", "OBSERVER"]:
        findings.append("manual four-session order mismatch")
    if findings:
        print(f"labscn003: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn003: PASS (CON-004 YELLOW; READY_FOR_USER; four manual sessions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
