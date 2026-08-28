#!/usr/bin/env python3
"""Regression tests for truthful W-COV-001 runner result handling."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Tests/Runtime/run_w_cov_001.py"
spec = importlib.util.spec_from_file_location("run_w_cov_001", MODULE_PATH)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


class FakeTarget:
    kind = "docker"

    def connection_arguments(self) -> list[str]:
        return ["--server", "localhost", "--auth", "sql", "--username", "sa", "--sqlcmd", "proxy"]

    def child_environment(self) -> dict[str, str]:
        return {}


def completed(output: str, code: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["python"], code, output, "")


def expect_accept(summary: str) -> None:
    with patch.object(runner.subprocess, "run", return_value=completed(summary)), patch.object(runner, "absent"):
        outcome, code = runner.run_once(FakeTarget(), "OPT-003", runner.DEMOS["OPT-003"], 1)
    assert (outcome, code) == tuple(summary.strip().split("|")[1:])


def expect_reject(output: str, returncode: int = 0) -> None:
    with patch.object(runner.subprocess, "run", return_value=completed(output, returncode)), patch.object(runner, "absent"):
        try:
            runner.run_once(FakeTarget(), "OPT-003", runner.DEMOS["OPT-003"], 1)
        except runner.CoverageFailure:
            return
    raise AssertionError(f"runner accepted invalid result: {output!r}, returncode={returncode}")


def main() -> int:
    expect_accept("SQLPERF_SUMMARY|PASS|OK\n")
    expect_accept("SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE\n")
    expect_accept("SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING\n")
    expect_reject("SQLPERF_SUMMARY|FAIL|FAIL_EXECUTION\n")
    expect_reject("no summary\n")
    expect_reject("SQLPERF_SUMMARY|PASS|OK\n", returncode=2)
    expect_reject("SQLPERF_SUMMARY|SKIP|SKIP_UNCONTROLLED\n")

    calls: list[list[str]] = []

    def capture(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return completed("SQLPERF_SUMMARY|PASS|OK\n")

    with patch.object(runner.subprocess, "run", side_effect=capture), patch.object(runner, "absent"):
        runner.run_once(FakeTarget(), "CON-006", runner.DEMOS["CON-006"], 1)
        runner.run_once(FakeTarget(), "STL-008", runner.DEMOS["STL-008"], 1)
    assert "--confirm-isolated-lab" in calls[0] and "--allow-red" not in calls[0]
    assert "--confirm-isolated-lab" in calls[1] and "--allow-red" in calls[1]
    print("w-cov-001-runner: PASS (7 outcomes; yellow/red safety forwarding)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
