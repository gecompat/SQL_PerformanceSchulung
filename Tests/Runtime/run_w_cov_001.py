#!/usr/bin/env python3
"""Run one W-COV-001 demo twice and preserve PASS/WARN/controlled SKIP."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
TOOLS = ROOT / "Demos" / "00_Framework" / "Tools"
sys.path.insert(0, str(RUNTIME))
import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402


@dataclass(frozen=True)
class Demo:
    manifest: Path
    safety: str


DEMOS = {
    "OPT-003": Demo(ROOT / "Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_Skew/manifest.json", "GREEN"),
    "OPT-005": Demo(ROOT / "Demos/04_Optimizer_Statistics_Plans/OPT-005_Ascending_Key/manifest.json", "GREEN"),
    "CON-006": Demo(ROOT / "Demos/07_Concurrency/CON-006_Deadlock_Cycle/manifest.json", "YELLOW"),
    "CON-009": Demo(ROOT / "Demos/05_Concurrency_Isolation_TempDB/CON-009_TempDB_Cost_Classes/manifest.json", "YELLOW"),
    "IDX-006": Demo(ROOT / "Demos/04_Rowstore_Columnstore/IDX-006_Page_Splits_Density/manifest.json", "YELLOW"),
    "IDX-010": Demo(ROOT / "Demos/04_Rowstore_Columnstore/IDX-010_Columnstore_Segments/manifest.json", "YELLOW"),
    "STL-008": Demo(ROOT / "Demos/01_Storage_Pages_Log/STL-008_VLF_Log_Growth/manifest.json", "RED"),
    "STL-009": Demo(ROOT / "Demos/01_Storage_Pages_Log/STL-009_Commit_Batching/manifest.json", "YELLOW"),
    "RES-007": Demo(ROOT / "Demos/06_CPU_Memory_IO_Waits/RES-007_Wait_Scope_Deltas/manifest.json", "YELLOW"),
}
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
ACCEPTED_SKIPS = {
    "SKIP_VERSION", "SKIP_PERMISSION", "SKIP_ISOLATION_REQUIRED",
    "SKIP_HIGH_IMPACT_CONFIRMATION_REQUIRED", "SKIP_RESOURCE_PROFILE",
    "SKIP_EVIDENCE_MISSING", "SKIP_TOOL_MISSING",
}


class CoverageFailure(RuntimeError):
    pass


def absent(target: ExecutionTarget, demo_id: str) -> None:
    database = f"SQLPERF_LAB_{demo_id.replace('-', '')}_LOCAL"
    result = execution_target.run_sql(
        target,
        database="master",
        sql_text=f"IF DB_ID(N'{database}') IS NOT NULL THROW 51004, 'FAIL_CLEANUP: database remains.', 1; SELECT N'ABSENT';",
        timeout_seconds=30,
    )
    if "ABSENT" not in result:
        raise CoverageFailure(f"{demo_id}: independent cleanup verification failed")


def run_once(target: ExecutionTarget, demo_id: str, spec: Demo, repetition: int) -> tuple[str, str]:
    command = [sys.executable, str(TOOLS / "run_demo.py"), str(spec.manifest), *target.connection_arguments(), "--show-output"]
    if spec.safety == "YELLOW":
        command.append("--confirm-isolated-lab")
    elif spec.safety == "RED":
        command.extend(("--confirm-isolated-lab", "--allow-red"))
    result = subprocess.run(
        command, check=False, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=target.child_environment(), timeout=900,
    )
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    summaries = SUMMARY.findall(combined)
    final = summaries[-1] if summaries else None
    accepted = bool(final) and (
        final[0] in {"PASS", "WARN"} or (final[0] == "SKIP" and final[1] in ACCEPTED_SKIPS)
    )
    if result.returncode != 0 or not accepted:
        raise CoverageFailure(
            f"{demo_id} repetition {repetition}: returncode={result.returncode}; "
            f"summary={final}; diagnostic={execution_target.redact(combined[-12000:])}"
        )
    absent(target, demo_id)
    outcome, code = final
    marker = demo_id.replace("-", "")
    print(f"{marker}_STAGE|RUN_{repetition}|{outcome}|{code}")
    return outcome, code


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Run one W-COV-001 demo twice.")
    parser.add_argument("--demo", choices=DEMOS, required=True)
    parser.add_argument("--target", choices=execution_target.TARGET_KINDS, default=execution_target.DOCKER)
    parser.add_argument("--container")
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--username", default="sa")
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--expected-major", type=int)
    args = parser.parse_args()
    major = args.expected_major
    marker = args.demo.replace("-", "")
    try:
        target = (
            execution_target.docker_target(container=args.container or "")
            if args.target == execution_target.DOCKER
            else execution_target.host_target(server=args.server, username=args.username or None)
        )
        execution_target.require_disposable_instance(target, args.confirm_disposable_instance)
        major = execution_target.verify_engine(target, expected_major=args.expected_major)
        outcomes = [run_once(target, args.demo, DEMOS[args.demo], repetition) for repetition in (1, 2)]
        rank = {"PASS": 0, "WARN": 1, "SKIP": 2}
        outcome, code = max(outcomes, key=lambda item: rank[item[0]])
        print(f"{marker}_SUMMARY|{outcome}|{code}|major={major}; repetitions=2; target={target.kind}")
        return 0
    except (ExecutionTargetError, CoverageFailure, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(f"{marker}_SUMMARY|FAIL|FAIL_EXECUTION|major={major}; target={args.target}; {execution_target.redact(str(exc))}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
