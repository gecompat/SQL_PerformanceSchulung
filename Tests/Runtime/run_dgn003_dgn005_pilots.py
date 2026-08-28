#!/usr/bin/env python3
"""Run DGN-003 and DGN-005 twice against one disposable target."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK = ROOT / "Demos" / "00_Framework" / "Tools"
sys.path.insert(0, str(RUNTIME))
import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402

DEMOS = {
    "DGN-003": ROOT / "Demos" / "07_Query_Store_Extended_Events" / "DGN-003_Query_Store_History" / "manifest.json",
    "DGN-005": ROOT / "Demos" / "07_Query_Store_Extended_Events" / "DGN-005_Bounded_Extended_Events" / "manifest.json",
}
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
ACCEPTED_SKIPS = {"SKIP_VERSION", "SKIP_PERMISSION", "SKIP_EVIDENCE_MISSING", "SKIP_TOOL_MISSING"}


class PilotFailure(RuntimeError):
    pass


def assert_absent(target: ExecutionTarget, demo_id: str) -> None:
    database = f"SQLPERF_LAB_{demo_id.replace('-', '')}_LOCAL"
    output = execution_target.run_sql(target, database="master", sql_text=f"IF DB_ID(N'{database}') IS NOT NULL THROW 51004,'FAIL_CLEANUP: Pilotdatenbank vorhanden.',1; SELECT N'ABSENT';", timeout_seconds=30)
    if "ABSENT" not in output:
        raise PilotFailure(f"{demo_id}: cleanup verification did not return ABSENT")


def run_one(target: ExecutionTarget, demo_id: str, repetition: int) -> tuple[str, str]:
    command = [sys.executable, str(FRAMEWORK / "run_demo.py"), str(DEMOS[demo_id]), *target.connection_arguments(), "--show-output"]
    if demo_id == "DGN-005":
        command.append("--confirm-isolated-lab")
    completed = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace", env=target.child_environment(), timeout=900)
    combined = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    summaries = SUMMARY.findall(combined)
    final = summaries[-1] if summaries else None
    accepted = bool(final) and (final[0] in {"PASS", "WARN"} or (final[0] == "SKIP" and final[1] in ACCEPTED_SKIPS))
    if completed.returncode != 0 or not accepted:
        raise PilotFailure(f"{demo_id} repetition {repetition}: returncode={completed.returncode}; summary={final}; diagnostic={execution_target.redact(combined[-12000:])}")
    assert_absent(target, demo_id)
    print(f"DGN_STAGE|{demo_id}|RUN_{repetition}|{final[0]}|{final[1]}")
    return final


def main() -> int:
    parser = argparse.ArgumentParser()
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
        outcomes = [run_one(target, demo_id, repetition) for demo_id in DEMOS for repetition in (1, 2)]
        aggregate = max(outcomes, key=lambda item: {"PASS": 0, "WARN": 1, "SKIP": 2}[item[0]])
        print(f"DGN_SUMMARY|{aggregate[0]}|{aggregate[1]}|major={major}; demos=2; repetitions=2; target={target.kind}")
        return 0
    except (ExecutionTargetError, PilotFailure, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(f"DGN_SUMMARY|FAIL|FAIL_EXECUTION|major={major}; target={args.target}; {execution_target.redact(str(exc))}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
