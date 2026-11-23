"""Run the bounded compile-value probe against a dedicated empty DGN-007 container."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import secrets
import subprocess

from Tests.Runtime import execution_target
from Tests.Runtime import run_dgn007_automated_setup as runner
from Tests.Runtime.dgn004_capture_runner import CaptureRunnerError, collect_bounded_process


PROBE = Path(__file__).with_name("dgn007_compile_value_probe.sql")
SUMMARY = "DGN007_COMPILE_VALUE|PASS|two_compile_values;two_plan_hashes;two_reused_executions;logical_reads_follow_compile_context"
MITIGATION_PROBE = Path(__file__).with_name("dgn007_recompile_mitigation_probe.sql")
MITIGATION_SUMMARY = "DGN007_MITIGATION|PASS|fewer_logical_reads;equal_results;restored_definition"
MITIGATION_SQL_SUMMARY = "DGN007_MITIGATION|RESULTS_AND_RESTORE|PASS"
_MITIGATION_STAGES = ("BASELINE1", "BASELINE2", "MITIGATION1", "MITIGATION2", "RESTORE")
_STAGE_MARKER = re.compile(r"DGN007_IO_(BEGIN|END)\|([A-Z]+[0-9]?(?:_[1-4])?)")
_SOURCE_IO = re.compile(
    r"Table '(CaseItem|CaseGroup|CaseItemDetail)'\. Scan count [0-9]+, logical reads ([0-9]+), .+"
)
_COMPILER_SLOT = re.compile(r"DGN007_COMPILER_SLOT\|([1-9][0-9]?)\|([01])\|([0-9]{1,18})\|([0-9]{1,18})")
_COMPILER_ROSTER = "DGN007_COMPILER_EVENTS|22|10"
_SOURCE_TABLES = {"CaseItem", "CaseGroup", "CaseItemDetail"}
_WAIT_CONTEXT = re.compile(
    r"DGN007_WAIT_CONTEXT\|4\|(no_grant_wait|grant_wait_present)"
    r"\|(no_page_io_wait|io_wait_present)\|(no_physical_reads|physical_reads_present)"
)
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


def _batch(target: execution_target.ExecutionTarget, sql: str, database: str, timeout: int, *, stderr_limit: int = 16_384) -> str:
    command = [
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", target.container or "", target.sqlcmd_path,
        "-S", "127.0.0.1", "-d", database, "-U", "sa", "-C", "-b", "-x", "-r", "1",
        "-h", "-1", "-W", "-l", "5", "-t", str(timeout),
    ]
    result = collect_bounded_process(
        command, input_bytes=(sql.rstrip() + "\nGO\n").encode("utf-8"), environment=os.environ.copy(),
        timeout_seconds=timeout, timeout_ceiling_seconds=90, stdout_limit_bytes=65_536, stderr_limit_bytes=stderr_limit,
    )
    if result.returncode:
        raise runner.RunnerFailure("NOT_PROVEN")
    return (result.stdout + b"\n" + result.stderr).decode("utf-8")


def _file(script: Path, *, parameter_mix: bool = False, compile_session: str | None = None) -> str:
    source = script.read_text(encoding="utf-8")
    for key, value in {
        "DemoId": "DGN-007", "RunToken": "AUTO", "TargetDatabase": runner.DATABASE,
        "CompareParameterMix": "1" if parameter_mix else "0",
        "MeasureCompileCost": "1" if compile_session else "0",
        "CompileSession": compile_session or "SQLPERF_DGN007_COMPILE_DISABLED",
        "ConfirmIsolatedLab": "1", "HighImpactConfirmed": "1", "MaximumRuntimeSeconds": "120",
    }.items():
        source = source.replace(f"$({key})", value)
    if "$(" in source:
        raise runner.RunnerFailure("FAIL_CONTRACT")
    return source


def _expect(output: str, summary: str) -> None:
    if sum(line.strip() == summary for line in output.splitlines()) != 1:
        raise runner.RunnerFailure("NOT_PROVEN")


def _read_mitigation(output: str, expected: tuple[str, ...]) -> dict[str, int]:
    _expect(output, MITIGATION_SQL_SUMMARY)
    stages: dict[str, int] = {}
    active = None
    reads: dict[str, int] = {}
    for line in output.splitlines():
        line = line.strip()
        if mark := _STAGE_MARKER.fullmatch(line):
            boundary, stage = mark.groups()
            if boundary == "BEGIN":
                if active is not None or len(stages) == len(expected) or stage != expected[len(stages)]:
                    raise runner.RunnerFailure("NOT_PROVEN")
                active, reads = stage, {}
            else:
                if active != stage or reads.keys() != _SOURCE_TABLES:
                    raise runner.RunnerFailure("NOT_PROVEN")
                stages[stage] = sum(reads.values())
                active = None
        elif source := _SOURCE_IO.fullmatch(line):
            table, count = source.groups()
            if active is None or table in reads or len(count) > 19:
                raise runner.RunnerFailure("NOT_PROVEN")
            reads[table] = int(count)
        elif line.startswith("DGN007_IO_"):
            raise runner.RunnerFailure("NOT_PROVEN")

    if active is not None or tuple(stages) != expected:
        raise runner.RunnerFailure("NOT_PROVEN")
    return stages


def _verify_mitigation(output: str) -> None:
    stages = _read_mitigation(output, _MITIGATION_STAGES)
    baseline = stages["BASELINE1"]
    if (
        baseline <= 0 or not baseline == stages["BASELINE2"] == stages["RESTORE"]
        or not all(0 < stages[stage] < baseline for stage in ("MITIGATION1", "MITIGATION2"))
    ):
        raise runner.RunnerFailure("NOT_PROVEN")


def _mitigation_mix_report(output: str) -> str:
    slots = range(1, 5)
    expected = tuple(f"{stage}_{slot}" for stage in _MITIGATION_STAGES for slot in slots)
    reads = _read_mitigation(output, expected)
    by_stage = tuple(tuple(reads[f"{stage}_{slot}"] for slot in slots) for stage in _MITIGATION_STAGES)
    lines = [
        "DGN007_MIX_READS|TOTAL|" + "|".join(str(sum(values)) for values in by_stage),
    ]
    for (group, status), values in zip(((1, 1), (1, 3), (5, 3), (8, 3)), zip(*by_stage), strict=True):
        lines.append(f"DGN007_MIX_READS|{group},{status}|" + "|".join(map(str, values)))
    return "\n".join(lines)


def _compile_cost_report(output: str) -> str:
    _expect(output, _COMPILER_ROSTER)
    values = []
    for line in output.splitlines():
        marker = line.strip()
        if marker.startswith("DGN007_COMPILER_EVENTS|") and marker != _COMPILER_ROSTER:
            raise runner.RunnerFailure("NOT_PROVEN")
        if not marker.startswith("DGN007_COMPILER_SLOT"):
            continue
        match = _COMPILER_SLOT.fullmatch(marker)
        if match is None:
            raise runner.RunnerFailure("NOT_PROVEN")
        slot, count, cpu, duration = map(int, match.groups())
        if slot != len(values) + 1 or (count == 0 and (cpu != 0 or duration != 0)):
            raise runner.RunnerFailure("NOT_PROVEN")
        values.append((count, cpu, duration))
    # Two explicit seed requests precede BASELINE1 and RESTORE respectively.
    expected_counts = (1,) + (0,) * 8 + (1,) * 8 + (1,) + (0,) * 4
    if tuple(row[0] for row in values) != expected_counts:
        raise runner.RunnerFailure("NOT_PROVEN")

    by_stage = []
    observed = values[1:17] + values[18:22]
    for offset, stage in enumerate(_MITIGATION_STAGES):
        total = [sum(column) for column in zip(*observed[offset * 4:offset * 4 + 4], strict=True)]
        by_stage.append(f"DGN007_COMPILE_COST|{stage}|" + "|".join(map(str, total)))
    return "\n".join(by_stage)


def _xe_absence(name: str) -> str:
    return f"""SET NOCOUNT ON;
IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=N'{name}')
   OR EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name=N'{name}')
    THROW 51098,'FAIL_XE_ABSENCE',1;
SELECT 'XE_ABSENT';"""


def _read_wait_context(output: str) -> str:
    markers = [line.strip() for line in output.splitlines() if line.strip().startswith("DGN007_WAIT_CONTEXT|")]
    if len(markers) != 1 or _WAIT_CONTEXT.fullmatch(markers[0]) is None:
        raise runner.RunnerFailure("NOT_PROVEN")
    return markers[0]


def run_probe(
    container: str, *, mitigation: bool = False, parameter_mix: bool = False, compile_cost: bool = False,
) -> str | None:
    if compile_cost and not parameter_mix:
        raise runner.RunnerFailure("FAIL_CONTRACT")
    if not os.environ.get("SQLCMDPASSWORD") or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container):
        raise runner.RunnerFailure("FAIL_SAFETY")
    target = runner.resolve_target(container)
    setup = _file(runner.AUTOMATED / "10_Setup.sql")
    compile_session = f"SQLPERF_DGN007_COMPILE_{secrets.token_hex(16)}" if compile_cost else None
    probe = _file(
        MITIGATION_PROBE if mitigation or parameter_mix else PROBE,
        parameter_mix=parameter_mix, compile_session=compile_session,
    )
    cleanup = _file(runner.AUTOMATED / "90_Cleanup.sql")
    _expect(_batch(target, PREFLIGHT, "master", 10), "EMPTY_DEVELOPER")
    if compile_session:
        _expect(_batch(target, _xe_absence(compile_session), "master", 10), "XE_ABSENT")
    report = None
    try:
        _expect(_batch(target, setup, "master", 90), SETUP_SUMMARY)
        if parameter_mix:
            output = _batch(target, probe, runner.DATABASE, 30, stderr_limit=49_152)
            report = _mitigation_mix_report(output)
            if compile_session:
                report += "\n" + _compile_cost_report(output)
        else:
            output = _batch(target, probe, runner.DATABASE, 30)
            if mitigation:
                _verify_mitigation(output)
            else:
                _expect(output, SUMMARY)
                report = _read_wait_context(output)
    finally:
        try:
            try:
                if compile_session:
                    stop = (
                        f"IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=N'{compile_session}') "
                        f"DROP EVENT SESSION [{compile_session}] ON SERVER;"
                    )
                    _expect(_batch(target, stop + "\n" + _xe_absence(compile_session), "master", 10), "XE_ABSENT")
            finally:
                try:
                    _expect(_batch(target, cleanup, "master", 40), SETUP_SUMMARY)
                finally:
                    _expect(_batch(target, ABSENCE, "master", 10), "ABSENT")
        except (runner.RunnerFailure, CaptureRunnerError, OSError, ValueError):
            raise runner.RunnerFailure("FAIL_CLEANUP") from None
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", required=True)
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--confirm-isolated-lab", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--mitigation", action="store_true", help="compare query-only recompile, including rollback")
    mode.add_argument("--mitigation-mix", action="store_true", help="report the four parameter classes separately")
    parser.add_argument("--compile-cost", action="store_true", help="add per-phase XE compile totals to --mitigation-mix")
    args = parser.parse_args()
    if args.compile_cost and not args.mitigation_mix:
        parser.error("--compile-cost requires --mitigation-mix")
    prefix, summary = ("DGN007_MITIGATION", MITIGATION_SUMMARY) if args.mitigation else ("DGN007_COMPILE_VALUE", SUMMARY)
    if args.mitigation_mix:
        prefix = "DGN007_MITIGATION_MIX"
        summary = f"{prefix}|PASS|20_equal_result_sets;restored_definition"
    try:
        if not args.confirm_disposable_instance or not args.confirm_isolated_lab:
            raise runner.RunnerFailure("FAIL_SAFETY")
        report = run_probe(
            args.container, mitigation=args.mitigation, parameter_mix=args.mitigation_mix, compile_cost=args.compile_cost,
        )
    except runner.RunnerFailure as error:
        print(f"{prefix}|FAIL|{error.code}")
        return 1
    except (execution_target.ExecutionTargetError, CaptureRunnerError, OSError, ValueError, subprocess.TimeoutExpired):
        print(f"{prefix}|FAIL|NOT_PROVEN")
        return 1
    print(summary + ";cleanup=PASS")
    if report is not None:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
