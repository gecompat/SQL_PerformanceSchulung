"""Validate the DGN-004 one-attempt-per-build CI qualification boundary."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "dgn004-runtime-qualification.yml"
CONTAINER = ROOT / "Tests" / "Runtime" / "dgn004_container.py"


def validate(workflow: str, container_source: str) -> list[str]:
    errors: list[str] = []
    required = (
        "workflow_dispatch:",
        "permissions:\n  contents: read",
        "cancel-in-progress: false", "fail-fast: false", "max-parallel: 1",
        "timeout-minutes: 30", "python Tests/Runtime/dgn004_runtime_runner.py --build \"$BUILD\"",
        "retention-days: 3", "if: always()", "docker pull \"$SQL_IMAGE\"",
        "python -m unittest Tests.Static.test_dgn004_runtime_runner",
    )
    if any(item not in workflow for item in required):
        errors.append("workflow does not retain all bounded DGN-004 CI controls")
    if re.search(r"(?m)^  (?:pull_request|push):\s*$", workflow):
        errors.append("runtime qualification must require explicit manual dispatch")
    if "sql-server-2019" in workflow.casefold() or "build: '2019'" in workflow:
        errors.append("workflow must not run the SQL Server 2019 unsupported scope")
    if workflow.count("python Tests/Runtime/dgn004_runtime_runner.py --build") != 1:
        errors.append("workflow must execute exactly one bounded trial per matrix job")
    for build, digest in (
        ("2022", "ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89"),
        ("2025", "4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1"),
    ):
        if f"build: '{build}'" not in workflow or digest not in workflow:
            errors.append(f"workflow is missing the pinned SQL Server {build} build")
        if digest not in container_source:
            errors.append(f"workflow image digest differs from the runtime profile for {build}")
    if re.search(r"docker\s+(?:rm|stop)\b", workflow):
        errors.append("workflow must leave ownership-checked container cleanup to the runner")
    return errors


def main() -> int:
    try:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        container_source = CONTAINER.read_text(encoding="utf-8")
    except OSError:
        print("dgn004-runtime-workflow: FAIL (required source unavailable)")
        return 1
    errors = validate(workflow, container_source)
    if errors:
        for error in errors:
            print(f"dgn004-runtime-workflow: {error}")
        return 1
    print("dgn004-runtime-workflow: PASS (pinned builds, sequential, bounded, runner-owned cleanup)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
