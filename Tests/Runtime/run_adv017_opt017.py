#!/usr/bin/env python3
"""Run OPT-017 twice and preserve PASS/WARN/controlled SKIP outcomes."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK_TOOLS = ROOT / "Demos" / "00_Framework" / "Tools"
sys.path.insert(0, str(RUNTIME))
import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402

DEMO_ID = "OPT-017"
MANIFEST = ROOT / "Demos" / "04_Optimizer_Statistics_Plans" / "OPT-017_Parallelism_Skew" / "manifest.json"
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
ACCEPTED_SKIPS = {"SKIP_VERSION", "SKIP_PERMISSION", "SKIP_RESOURCE_PROFILE", "SKIP_EVIDENCE_MISSING", "SKIP_TOOL_MISSING"}


class Opt017Failure(RuntimeError):
    pass


def assert_database_absent(target: ExecutionTarget) -> None:
    database = "SQLPERF_LAB_OPT017_LOCAL"
    output = execution_target.run_sql(
        target, database="master",
        sql_text=f"IF DB_ID(N'{database}') IS NOT NULL THROW 51004, 'FAIL_CLEANUP: OPT-017 database remains.', 1; SELECT N'ABSENT';",
        timeout_seconds=30,
    )
    if "ABSENT" not in output:
        raise Opt017Failure("cleanup verification did not return ABSENT")


def run_demo(target: ExecutionTarget, repetition: int) -> tuple[str, str]:
    command = [sys.executable, str(FRAMEWORK_TOOLS / "run_demo.py"), str(MANIFEST), *target.connection_arguments(), "--confirm-isolated-lab", "--show-output"]
    result = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace", env=target.child_environment(), timeout=900)
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    summaries = SUMMARY.findall(combined)
    final_summary = summaries[-1] if summaries else None
    accepted = bool(final_summary) and (final_summary[0] in {"PASS", "WARN"} or (final_summary[0] == "SKIP" and final_summary[1] in ACCEPTED_SKIPS))
    if result.returncode != 0 or not accepted:
        raise Opt017Failure(f"repetition {repetition}: returncode={result.returncode}; summary={final_summary}; diagnostic={execution_target.redact(combined[-12000:])}")
    assert_database_absent(target)
    outcome, code = final_summary
    print(f"OPT017_STAGE|{DEMO_ID}|RUN_{repetition}|{outcome}|{code}")
    return outcome, code


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OPT-017 twice.")
    parser.add_argument("--target", choices=execution_target.TARGET_KINDS, default=execution_target.DOCKER)
    parser.add_argument("--container")
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--username", default="sa")
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--expected-major", type=int)
    args = parser.parse_args()
    major = args.expected_major
    try:
        target = execution_target.docker_target(container=args.container or "") if args.target == execution_target.DOCKER else execution_target.host_target(server=args.server, username=args.username or None)
        execution_target.require_disposable_instance(target, args.confirm_disposable_instance)
        major = execution_target.verify_engine(target, expected_major=args.expected_major)
        print(f"OPT017_STAGE|ENGINE_{major}|IDENTITY|PASS|OK")
        outcomes = [run_demo(target, repetition) for repetition in (1, 2)]
        rank = {"PASS": 0, "WARN": 1, "SKIP": 2}
        outcome, code = max(outcomes, key=lambda item: rank[item[0]])
        print(f"OPT017_SUMMARY|{outcome}|{code}|major={major}; repetitions=2; target={target.kind}")
        return 0
    except (ExecutionTargetError, Opt017Failure, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(f"OPT017_SUMMARY|FAIL|FAIL_EXECUTION|major={major}; target={args.target}; {execution_target.redact(str(exc))}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
