#!/usr/bin/env python3
"""Validate the standardized interactive lifecycle and container quickstart."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "Documentation/HowTo/INTERACTIVE_SCENARIO_LIFECYCLE.md"
QUICKSTART = ROOT / "Documentation/HowTo/CONTAINER_QUICKSTART.md"
LOCAL = ROOT / "Documentation/HowTo/LOCAL_TEST_ENVIRONMENT.md"


def require(path: Path, markers: tuple[str, ...], findings: list[str]) -> None:
    if not path.is_file():
        findings.append(f"missing {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            findings.append(f"{path.name}: missing {marker}")


def main() -> int:
    findings: list[str] = []
    lifecycle_commands = (
        "Get-PerformanceTrainingScenario",
        "Start-PerformanceTrainingScenario",
        "Reset-PerformanceTrainingScenario",
        "Remove-PerformanceTrainingScenario",
        "READY_FOR_USER",
        "REMOVED",
        "Test-SqlServerLabPrerequisite",
        "-Provider docker",
        "-Provider podman",
        "SecureString",
    )
    require(LIFECYCLE, lifecycle_commands, findings)
    require(QUICKSTART, lifecycle_commands, findings)
    require(LOCAL, ("CONTAINER_QUICKSTART.md", "INF-002", "INF-003"), findings)

    for path in (LIFECYCLE, QUICKSTART):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for forbidden in ("docker run", "podman run", "--password", "-p sa", "sqlcmdpassword"):
            if forbidden in text:
                findings.append(f"{path.name}: forbidden direct/secret path {forbidden}")

    if findings:
        print(f"labscn004-inf002003: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn004-inf002003: PASS (selection/start/handoff/reset/remove; docker/podman quickstart)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
