#!/usr/bin/env python3
"""Static contract for the non-promoting DGN-007 runtime harness."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "Tests/Lab/Invoke-DGN007StaticParticipantFlowTest.ps1"
FORBIDDEN = (ROOT / "Scenarios/DGN-007/scenario.json", ROOT / "Scenarios/DGN-007/manifest.json")

def main() -> int:
    findings: list[str] = []
    if not HARNESS.is_file(): findings.append(f"missing {HARNESS.relative_to(ROOT)}")
    for path in FORBIDDEN:
        if path.exists(): findings.append(f"static runtime harness must not add {path.relative_to(ROOT)}")
    if findings:
        print("dgn007-static-participant-flow-harness: FAIL"); print("\n".join(f"- {item}" for item in findings)); return 1
    harness = HARNESS.read_text(encoding="utf-8")
    required = ("STATIC_PARTICIPANT_FLOW_ONLY", "Test-SqlServerLabManifest", "New-SqlServerLab", "Get-SqlServerLab", "Test-SqlServerLabAdapter", "Install-SqlServerLabAdapter", "Remove-SqlServerLab", "SQLCMDPASSWORD", "SQLPERF_SUMMARY\\|(PASS|SKIP)\\|([A-Z0-9_]+)", "SKIP_QUERY_STORE_REQUIRED", "SKIP_INCIDENT_NOT_REPRODUCED", "SKIP_EVIDENCE_MISSING", "CONTROLLED_SKIP_NO_EVIDENCE_CLAIM", "COMPLETED_WITHOUT_PROMOTION", "ParticipantStageResults", "RECOVERY_FINALLY", "-Entrypoint cleanup", "-SkipPreflight")
    for marker in required:
        if marker not in harness: findings.append(f"harness marker missing: {marker}")
    stages = [harness.index(marker) for marker in ("00_Preflight.sql", "20_Baseline.sql", "40_Observation.sql", "50_Mitigation.sql", "60_Comparison.sql", "90_Cleanup.sql")]
    if stages != sorted(stages): findings.append("documented SQL stages must remain ordered")
    expected_skips = {
        "PRECHECK": "@('SKIP_QUERY_STORE_REQUIRED')",
        "TIME_WINDOWS": "@('SKIP_INCIDENT_NOT_REPRODUCED')",
        "EVIDENCE": "@('SKIP_INCIDENT_NOT_REPRODUCED','SKIP_EVIDENCE_MISSING')",
        "COMPARISON": "@('SKIP_EVIDENCE_MISSING')",
    }
    for stage, codes in expected_skips.items():
        if f"Name = '{stage}'" not in harness or f"AllowedSkipCodes = {codes}" not in harness:
            findings.append(f"controlled skip contract missing for {stage}")
    for required_pass_stage in ("REFERENCE_CHANGE", "RECOVERY"):
        marker = f"Name = '{required_pass_stage}';"
        start = harness.find(marker)
        end = harness.find("},", start)
        if start == -1 or "AllowedSkipCodes = @()" not in harness[start:end]:
            findings.append(f"{required_pass_stage} must remain PASS-only")
    if "$controlledSkip = $result" not in harness or "break" not in harness or "$participantCleanupAttempted = $true" not in harness:
        findings.append("controlled skip must stop the participant flow and retain mandatory recovery")
    if "New-Item" in harness or "Set-Content" in harness or "Out-File" in harness:
        findings.append("harness must not create or promote a scenario contract")
    if findings:
        print(f"dgn007-static-participant-flow-harness: FAIL ({len(findings)} finding(s))"); print("\n".join(f"- {item}" for item in findings)); return 1
    print("dgn007-static-participant-flow-harness: PASS (PROJECT_SEMANTIC; 2025-only static participant-flow harness without scenario promotion)")
    return 0

if __name__ == "__main__": raise SystemExit(main())
