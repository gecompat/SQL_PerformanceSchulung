#!/usr/bin/env python3
"""Static contract for the non-promoting DGN-007 unsupported-version gate."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "Tests/Lab/Invoke-DGN007UnsupportedVersionGateTest.ps1"
FORBIDDEN = (
    ROOT / "Scenarios/DGN-007/scenario.json",
    ROOT / "Scenarios/DGN-007/manifest.json",
)


def main() -> int:
    findings: list[str] = []
    if not HARNESS.is_file():
        findings.append(f"missing {HARNESS.relative_to(ROOT)}")
    for path in FORBIDDEN:
        if path.exists():
            findings.append(f"unsupported-version gate must not add {path.relative_to(ROOT)}")
    if findings:
        print("dgn007-unsupported-version-gate-harness: FAIL")
        print("\n".join(f"- {item}" for item in findings))
        return 1

    harness = HARNESS.read_text(encoding="utf-8")
    required = (
        "ValidateSet('docker', 'podman')",
        "ValidateSet('2019', '2022')",
        "New-SqlServerLab -Version $SqlVersion -Provider $Provider",
        "Get-SqlServerLab",
        "Test-SqlServerLabAdapter",
        "ADAPTER_UNSUPPORTED_SQL_VERSION",
        "ADAPTER_UNSUPPORTED_CONTRACT",
        "DGN007_DATABASE_ABSENT",
        "SQLCMDPASSWORD",
        "Remove-SqlServerLab",
        "finally",
    )
    for marker in required:
        if marker not in harness:
            findings.append(f"harness marker missing: {marker}")
    forbidden = ("Install-SqlServerLabAdapter", "New-Item", "Set-Content", "Out-File")
    for marker in forbidden:
        if marker in harness:
            findings.append(f"unsupported-version gate must not contain: {marker}")
    if "if ($lab)" not in harness or harness.index("if ($lab)") < harness.index("finally"):
        findings.append("lab removal must be guarded in the finally path")

    if findings:
        print(f"dgn007-unsupported-version-gate-harness: FAIL ({len(findings)} finding(s))")
        print("\n".join(f"- {item}" for item in findings))
        return 1
    print("dgn007-unsupported-version-gate-harness: PASS (PROJECT_SEMANTIC; 2019/2022 adapter rejection without scenario promotion)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
