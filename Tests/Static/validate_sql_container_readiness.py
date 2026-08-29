#!/usr/bin/env python3
"""Require authenticated readiness probes for SQL Server container workflows."""
from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
READY_LOG = "SQL Server is now ready for client connections"
REQUIRED = (
    "login_ready=0",
    'docker exec -e "SQLCMDPASSWORD=${password}"',
    'SELECT 1;',
)


def main() -> int:
    findings: list[str] = []
    checked = 0
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if READY_LOG not in text:
            continue
        checked += 1
        for marker in REQUIRED:
            if marker not in text:
                findings.append(f"{path.name}: authenticated readiness marker missing: {marker}")
        if re.search(r"grep[^\n]+SQL Server is now ready for client connections[^\n]+&&\s*exit\s+0", text):
            findings.append(f"{path.name}: log readiness must not exit before login verification")

    if checked == 0:
        findings.append("no SQL Server container workflows were discovered")
    if findings:
        print(f"sql-container-readiness: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"sql-container-readiness: PASS ({checked} authenticated workflows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
