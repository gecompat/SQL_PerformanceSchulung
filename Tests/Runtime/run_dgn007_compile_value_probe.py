"""Run the bounded compile-value probe against a dedicated empty DGN-007 container."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess

from Tests.Runtime import execution_target
from Tests.Runtime import run_dgn007_automated_setup as runner
from Tests.Runtime.dgn004_capture_runner import CaptureRunnerError, collect_bounded_process


PROBE = Path(__file__).with_name("dgn007_compile_value_probe.sql")
SUMMARY = "DGN007_COMPILE_VALUE|PASS|two_compile_values;two_plan_hashes;two_reused_executions;logical_reads_follow_compile_context"
SETUP_SUMMARY = "SQLPERF_SUMMARY|PASS|OK"
PREFLIGHT = """SET NOCOUNT ON;
IF COALESCE(TRY_CONVERT(int, SERVERPROPERTY('EditionID')), 0) NOT IN (-2117995310,-1785266663)
   OR COALESCE(CONVERT(varchar(128),SERVERPROPERTY('ProductVersion')),'') <> '17.0.5065.9'
   OR EXISTS (SELECT 1 FROM sys.databases WHERE database_id>4)
    THROW 51080,'FAIL_SAFETY',1;
SELECT 'EMPTY_DEVELOPER';"""
ABSENCE = """SET NOCOUNT ON;
IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id>4)
    THROW 51084,'FAIL_CLEANUP',1;
SELECT 'ABSENT';"""


def _batch(target: execution_target.ExecutionTarget, sql: str, database: str, timeout: int) -> str:
    command = [
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", target.container or "", target.sqlcmd_path,
        "-S", "127.0.0.1", "-d", database, "-U", "sa", "-C", "-b", "-x", "-r", "1",
        "-h", "-1", "-W", "-l", "5", "-t", str(timeout),
    ]
    result = collect_bounded_process(
        command, input_bytes=(sql.rstrip() + "\nGO\n").encode("utf-8"), environment=os.environ.copy(),
        timeout_seconds=timeout, timeout_ceiling_seconds=90, stdout_limit_bytes=65_536, stderr_limit_bytes=16_384,
    )
    if result.returncode:
        raise runner.RunnerFailure("NOT_PROVEN")
    return (result.stdout + b"\n" + result.stderr).decode("utf-8")


def _file(script: Path) -> str:
    source = script.read_text(encoding="utf-8")
    for key, value in {
        "DemoId": "DGN-007", "RunToken": "AUTO", "TargetDatabase": runner.DATABASE,
        "ConfirmIsolatedLab": "1", "HighImpactConfirmed": "1", "MaximumRuntimeSeconds": "120",
    }.items():
        source = source.replace(f"$({key})", value)
    if "$(" in source:
        raise runner.RunnerFailure("FAIL_CONTRACT")
    return source


def _expect(output: str, summary: str) -> None:
    if sum(line.strip() == summary for line in output.splitlines()) != 1:
        raise runner.RunnerFailure("NOT_PROVEN")


def run_probe(container: str) -> None:
    if not os.environ.get("SQLCMDPASSWORD") or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container):
        raise runner.RunnerFailure("FAIL_SAFETY")
    target = runner.resolve_target(container)
    setup = _file(runner.AUTOMATED / "10_Setup.sql")
    probe = _file(PROBE)
    cleanup = _file(runner.AUTOMATED / "90_Cleanup.sql")
    _expect(_batch(target, PREFLIGHT, "master", 10), "EMPTY_DEVELOPER")
    try:
        _expect(_batch(target, setup, "master", 90), SETUP_SUMMARY)
        _expect(_batch(target, probe, runner.DATABASE, 30), SUMMARY)
    finally:
        try:
            try:
                _expect(_batch(target, cleanup, "master", 40), SETUP_SUMMARY)
            finally:
                _expect(_batch(target, ABSENCE, "master", 10), "ABSENT")
        except (runner.RunnerFailure, CaptureRunnerError, OSError, ValueError):
            raise runner.RunnerFailure("FAIL_CLEANUP") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", required=True)
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--confirm-isolated-lab", action="store_true")
    args = parser.parse_args()
    try:
        if not args.confirm_disposable_instance or not args.confirm_isolated_lab:
            raise runner.RunnerFailure("FAIL_SAFETY")
        run_probe(args.container)
    except runner.RunnerFailure as error:
        print(f"DGN007_COMPILE_VALUE|FAIL|{error.code}")
        return 1
    except (execution_target.ExecutionTargetError, CaptureRunnerError, OSError, ValueError, subprocess.TimeoutExpired):
        print("DGN007_COMPILE_VALUE|FAIL|NOT_PROVEN")
        return 1
    print(SUMMARY + ";cleanup=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
