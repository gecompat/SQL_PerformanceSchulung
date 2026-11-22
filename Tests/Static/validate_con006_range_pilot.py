"""Static guard for the manual, container-owned CON-006 range pilot."""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Tests/Runtime/con006_range_pilot.py"
WORKFLOW = ROOT / ".github/workflows/con006-range-pilot.yml"
EXECUTION_TARGET = ROOT / "Tests/Runtime/execution_target.py"


def validate() -> list[str]:
    errors: list[str] = []
    runner = RUNNER.read_text(encoding="utf-8").casefold()
    workflow = re.sub(r"\s+", " ", WORKFLOW.read_text(encoding="utf-8").casefold())
    execution_target = EXECUTION_TARGET.read_text(encoding="utf-8")
    for marker in ("serializable", "forceSeek", "lck_m%", "system_health",
                   "xml_deadlock_report", "evaluate_range_capture",
                   "evaluate_range_control", "1205", "single_user with rollback immediate"):
        if marker.casefold() not in runner:
            errors.append(f"pilot runner must retain the reviewed range gate ({marker})")
    if "sqlperf.ci.owner" not in runner or "con006-range-pilot" not in runner:
        errors.append("pilot must bind inspection and cleanup to its exact owned container")
    if "isoptimizedlockingon" not in runner:
        errors.append("SQL Server 2025 optimized-locking state must be observed without mutation")
    if '"127.0.0.1"' not in runner or '"127.0.0.1"' not in execution_target:
        errors.append("container SQL probes must use explicit IPv4 loopback")
    if "-s 127.0.0.1" not in workflow:
        errors.append("login readiness must use the same explicit IPv4 loopback")
    if 'host.get("networkmode") != "none"' not in runner:
        errors.append("pilot must refuse a container with network connectivity")
    if "workflow_dispatch" not in workflow:
        errors.append("empirical range runs must require manual dispatch")
    if "--expected-product-build" not in workflow:
        errors.append("each pinned image run must verify its exact expected engine build")
    if "if: ${{ github.event_name == 'workflow_dispatch' }}" not in workflow:
        errors.append("runtime matrix must be conditional on manual dispatch")
    if "max-parallel: 1" not in workflow:
        errors.append("pinned build probes must run serially")
    if "mcr.microsoft.com/mssql/server@sha256:" not in workflow:
        errors.append("runtime matrix must use digest-pinned image references")
    if ("--network none" not in workflow or "--cpus=2" not in workflow
            or "--memory=4g" not in workflow or "--memory-swap=4g" not in workflow):
        errors.append("runtime container must remain isolated and resource bounded")
    if "cleanup_ci_container.sh" not in workflow or "retention-days: 3" not in workflow:
        errors.append("workflow must verify owner cleanup and keep only short-lived aggregate output")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("con006-range-pilot: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("con006-range-pilot: PASS (manual; pinned; isolated; bounded; graph and cleanup checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
