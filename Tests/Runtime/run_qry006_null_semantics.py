#!/usr/bin/env python3
"""Run QRY-006 twice against one disposable SQL Server execution target."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK_TOOLS = ROOT / "Demos" / "00_Framework" / "Tools"
MANIFEST = ROOT / "Demos" / "05_Query_Patterns" / "QRY-006_NULL_Semantics" / "manifest.json"
DEMO_ID = "QRY-006"
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
COMPATIBILITY_LEVELS = {15: 150, 16: 160, 17: 170}

sys.path.insert(0, str(RUNTIME))
import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402


class Qry006Failure(RuntimeError):
    """QRY-006 did not satisfy its deterministic runtime contract."""


def target_database() -> str:
    return f"SQLPERF_LAB_{DEMO_ID.replace('-', '')}_LOCAL"


def assert_target_contract(target: ExecutionTarget, major: int) -> None:
    expected_level = COMPATIBILITY_LEVELS.get(major)
    if expected_level is None:
        raise Qry006Failure(f"unsupported SQL Server major version: {major}")
    print(f"QRY006_STAGE|ENGINE_{major}|COMPATIBILITY_TARGET_{expected_level}|PASS|OK")


def assert_target_database_compatibility(output: str, major: int) -> None:
    """Validate the live database evidence emitted by ASSERTION before cleanup."""
    expected_level = COMPATIBILITY_LEVELS.get(major)
    if expected_level is None:
        raise Qry006Failure(f"unsupported SQL Server major version: {major}")
    levels = [
        int(match) for match in re.findall(
            r"(?m)^\[ASSERTION:(?:stdout|stderr)\] QRY006_DATABASE_CL\|(\d+)\s*$", output
        )
    ]
    if levels != [expected_level]:
        raise Qry006Failure(
            "target database compatibility level mismatch: "
            f"expected {expected_level}, observed {levels or 'missing'}"
        )
    print(f"QRY006_STAGE|DATABASE_CL_{expected_level}|PASS|OK")


def assert_database_absent(target: ExecutionTarget) -> None:
    database = target_database()
    output = execution_target.run_sql(
        target,
        database="master",
        sql_text=(
            f"IF DB_ID(N'{database}') IS NOT NULL "
            "THROW 51004, 'FAIL_CLEANUP: QRY-006-Testdatenbank ist nach dem Harness-Lauf noch vorhanden.', 1; "
            "SELECT N'ABSENT';"
        ),
        timeout_seconds=30,
    )
    if "ABSENT" not in output:
        raise Qry006Failure("independent cleanup verification did not return ABSENT")


def run_demo(*, target: ExecutionTarget, repetition: int, major: int) -> None:
    if not MANIFEST.is_file():
        raise Qry006Failure("manifest missing")
    command = [
        sys.executable,
        str(FRAMEWORK_TOOLS / "run_demo.py"),
        str(MANIFEST),
        *target.connection_arguments(),
        "--show-output",
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=target.child_environment(),
        timeout=900,
    )
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    summaries = SUMMARY.findall(combined)
    final_summary = summaries[-1] if summaries else None
    if result.returncode != 0 or final_summary != ("PASS", "OK"):
        diagnostic = execution_target.redact(combined[-12000:])
        raise Qry006Failure(
            f"repetition {repetition}: returncode={result.returncode}; "
            f"summary={final_summary}; diagnostic={diagnostic}"
        )
    assert_target_database_compatibility(combined, major)
    assert_database_absent(target)
    print(f"QRY006_STAGE|RUN_{repetition}|PASS|OK")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QRY-006 twice.")
    parser.add_argument("--target", choices=execution_target.TARGET_KINDS, default=execution_target.DOCKER)
    parser.add_argument("--container", help="only for --target docker")
    parser.add_argument("--server", default="localhost", help="only for --target host")
    parser.add_argument("--username", default="sa", help="empty uses Windows authentication")
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--expected-major", type=int)
    args = parser.parse_args()
    major = args.expected_major
    try:
        target = (
            execution_target.docker_target(container=args.container or "")
            if args.target == execution_target.DOCKER
            else execution_target.host_target(server=args.server, username=args.username or None)
        )
        execution_target.require_disposable_instance(target, args.confirm_disposable_instance)
        major = execution_target.verify_engine(target, expected_major=args.expected_major)
        assert_target_contract(target, major)
        for repetition in (1, 2):
            run_demo(target=target, repetition=repetition, major=major)
        print(f"QRY006_SUMMARY|PASS|OK|major={major}; repetitions=2; target={target.kind}")
        return 0
    except (ExecutionTargetError, Qry006Failure, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(
            f"QRY006_SUMMARY|FAIL|FAIL_EXECUTION|major={major}; target={args.target}; "
            f"{execution_target.redact(str(exc))}"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
