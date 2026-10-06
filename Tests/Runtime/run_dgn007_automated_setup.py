#!/usr/bin/env python3
"""Den ausgewählten DGN-007-AUTO-Schnitt zweimal auf einem Docker-Ziel prüfen.

180 Sekunden reguläres Budget und 60 Sekunden Cleanup werden durch FWK-010
erzwungen. Der äußere Prozessschutz lässt dafür 20 Sekunden Start-/Abbruchzeit.
Nach jedem Lauf folgt eine unabhängige Abwesenheitsprüfung (30 Sekunden).
Bei unbestätigtem Abbau wird genau einmal der vorhandene, markerprüfende
AUTO-Cleanup-Batch versucht (60 Sekunden), danach erneut geprüft (30 Sekunden).
Recovery macht einen fehlgeschlagenen Lauf niemals erfolgreich. Rohoutput und
Exception-Texte verlassen den Prozess nicht und werden nicht persistiert.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK = ROOT / "Demos" / "00_Framework" / "Tools"
for directory in (RUNTIME, FRAMEWORK):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402
from run_demo import load_manifest  # noqa: E402
from sqlcmd_process import SqlcmdResult, build_sqlcmd_command, run_sqlcmd  # noqa: E402

AUTOMATED = (ROOT / "Demos" / "07_Query_Store_Extended_Events"
             / "DGN-007_Time_Bounded_Search_Incident" / "Automated")
MANIFEST = AUTOMATED / "setup.manifest.json"
DATABASE = "SQLPERF_LAB_DGN007_AUTO"
SCOPE = "DGN-007_DATA_MODEL"
EXPECTED_PHASES = ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "CLEANUP")
HARNESS_TIMEOUT = 180 + 60 + 20
RECOVERY_TIMEOUT = 60
VERIFY_TIMEOUT = 30
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
PHASE = re.compile(r"^([A-Z][A-Z0-9_]*): (PASS|WARN|SKIP|FAIL)/([A-Z][A-Z0-9_]*) \(", re.MULTILINE)


@dataclass(frozen=True)
class RunContract:
    """Unveränderlicher Scope mit eigenem Manifest und exakter Phasenmetadatenfolge."""

    scope: str
    manifest: Path
    phase_specs: tuple[tuple[str, str, str, int], ...]

    @property
    def expected_phases(self) -> tuple[str, ...]:
        return tuple(spec[0] for spec in self.phase_specs)


DATA_MODEL_CONTRACT = RunContract(
    scope=SCOPE,
    manifest=MANIFEST,
    phase_specs=(
        ("PREFLIGHT", "00_Preflight.sql", "master", 30),
        ("SETUP", "10_Setup.sql", "master", 90),
        ("DATA_ASSERTION", "40_Data_Assertion.sql", "target", 30),
        ("CLEANUP", "90_Cleanup.sql", "master", 60),
    ),
)
QUERY_STORE_WINDOWS_CONTRACT = RunContract(
    scope="DGN-007_QUERY_STORE_WINDOWS",
    manifest=AUTOMATED / "windows.manifest.json",
    phase_specs=(
        *DATA_MODEL_CONTRACT.phase_specs[:-1],
        ("QUERY_STORE_WINDOWS", "20_Query_Store_Windows.sql", "target", 150),
        DATA_MODEL_CONTRACT.phase_specs[-1],
    ),
)
PROFILE_COMPARISON_CONTRACT = RunContract(
    scope="DGN-007_PROFILE_COMPARISON",
    manifest=AUTOMATED / "profile-comparison.manifest.json",
    phase_specs=(
        *QUERY_STORE_WINDOWS_CONTRACT.phase_specs[:-1],
        ("PROFILE_COMPARISON", "30_Profile_Comparison.sql", "target", 10),
        QUERY_STORE_WINDOWS_CONTRACT.phase_specs[-1],
    ),
)


def scope_contract(scope: str) -> RunContract:
    if scope == "data-model":
        return DATA_MODEL_CONTRACT
    if scope == "query-store-windows":
        return QUERY_STORE_WINDOWS_CONTRACT
    if scope == "profile-comparison":
        return PROFILE_COMPARISON_CONTRACT
    raise ValueError("Unbekannter DGN-007-AUTO-Scope")


class RunnerFailure(RuntimeError):
    """Nur ein fest definierter, datenschutzneutraler Fehlercode wird ausgegeben."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class RunResult:
    repetition: int
    outcome: str = "PASS"
    code: str = "OK"


def validate_manifest(*, contract: RunContract = DATA_MODEL_CONTRACT) -> None:
    """Ein geänderter Schnitt benötigt eine bewusste Anpassung des Runners."""
    manifest = load_manifest(contract.manifest)
    phases = (*manifest.phases, manifest.cleanup)
    if (manifest.demo_id != "DGN-007" or manifest.run_token != "AUTO"
            or manifest.safety_level != "YELLOW"
            or manifest.timeout_seconds != 180 or manifest.cleanup_timeout_seconds != 60
            or any(phase is None for phase in phases)):
        raise RunnerFailure("FAIL_CONTRACT")
    if tuple(phase.phase_id for phase in phases) != contract.expected_phases:
        raise RunnerFailure("FAIL_CONTRACT")
    for phase, (_, script, selector, timeout) in zip(phases, contract.phase_specs):
        if (phase.kind != "sql" or not phase.required or not phase.require_summary
                or phase.path != AUTOMATED / script or phase.database_selector != selector
                or phase.timeout_seconds != timeout):
            raise RunnerFailure("FAIL_CONTRACT")


def resolve_target(container: str) -> ExecutionTarget:
    """Bounded sqlcmd-Erkennung; kein implizites Ziel aus der Umgebung."""
    result = subprocess.run(
        ["docker", "exec", container, "sh", "-lc",
         "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then printf /opt/mssql-tools18/bin/sqlcmd; "
         "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then printf /opt/mssql-tools/bin/sqlcmd; else exit 127; fi"],
        check=False, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=VERIFY_TIMEOUT,
    )
    if result.returncode != 0 or result.stdout.strip() not in {
        "/opt/mssql-tools18/bin/sqlcmd", "/opt/mssql-tools/bin/sqlcmd"
    }:
        raise RunnerFailure("FAIL_EXECUTION")
    return execution_target.docker_target(container=container, sqlcmd_path=result.stdout.strip())


def assert_empty_instance(target: ExecutionTarget) -> None:
    output = execution_target.run_sql(
        target, database="master", timeout_seconds=VERIFY_TIMEOUT,
        sql_text="SET NOCOUNT ON; "
        "DECLARE @EditionId int=TRY_CONVERT(int,SERVERPROPERTY('EditionID')); "
        "IF @EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663) "
        "THROW 51001,'FAIL_SAFETY',1; "
        "IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4) "
        "THROW 51001,'FAIL_SAFETY',1; SELECT N'EMPTY_DEVELOPER';",
    )
    if output.strip() != "EMPTY_DEVELOPER":
        raise RunnerFailure("FAIL_SAFETY")


def assert_absent(target: ExecutionTarget) -> None:
    """Abwesenheit unabhängig von Harness-Summaries bestätigen."""
    output = execution_target.run_sql(
        target, database="master", timeout_seconds=VERIFY_TIMEOUT,
        sql_text=f"SET NOCOUNT ON; IF DB_ID(N'{DATABASE}') IS NOT NULL "
        "THROW 51004,'FAIL_CLEANUP',1; SELECT N'ABSENT';",
    )
    if output.strip() != "ABSENT":
        raise RunnerFailure("FAIL_CLEANUP")


def run_harness(target: ExecutionTarget, *, contract: RunContract = DATA_MODEL_CONTRACT) -> SqlcmdResult:
    command = [sys.executable, str(FRAMEWORK / "run_demo.py"), str(contract.manifest),
               *target.connection_arguments(), "--confirm-isolated-lab"]
    return run_sqlcmd(command, timeout_seconds=HARNESS_TIMEOUT,
                      environment=target.child_environment())


def check_harness(result: SqlcmdResult, *, contract: RunContract = DATA_MODEL_CONTRACT) -> None:
    combined = "\n".join((result.stdout, result.stderr)).replace("\r\n", "\n")
    phases = PHASE.findall(combined)
    # Cleanup hat Vorrang, auch wenn der Harness einen früheren Fehler aggregiert.
    if any(phase == "CLEANUP" and (outcome, code) != ("PASS", "OK")
           for phase, outcome, code in phases):
        raise RunnerFailure("FAIL_CLEANUP")
    summaries = SUMMARY.findall(combined)
    if any(code == "FAIL_CLEANUP" for _, code in summaries):
        raise RunnerFailure("FAIL_CLEANUP")
    if result.timed_out or any(code == "FAIL_TIMEOUT" for _, code in summaries + [(o, c) for _, o, c in phases]):
        raise RunnerFailure("FAIL_TIMEOUT")
    if result.returncode != 0:
        raise RunnerFailure("FAIL_EXECUTION")
    if summaries != [("PASS", "OK")] or phases != [
        (phase, "PASS", "OK") for phase in contract.expected_phases
    ]:
        raise RunnerFailure("FAIL_CONTRACT")


def recover(target: ExecutionTarget) -> None:
    """Ausschließlich den bestehenden, vollständig markergebundenen Batch verwenden."""
    command = build_sqlcmd_command(
        executable=str(target.shim), server=target.server, database="master",
        script=AUTOMATED / "90_Cleanup.sql", auth=target.auth, username=target.username,
        variables={"DemoId": "DGN-007", "RunToken": "AUTO", "TargetDatabase": DATABASE,
                   "ConfirmIsolatedLab": "1", "HighImpactConfirmed": "1"},
    )
    result = run_sqlcmd(command, timeout_seconds=RECOVERY_TIMEOUT,
                      environment=target.child_environment())
    summaries = SUMMARY.findall("\n".join((result.stdout, result.stderr)).replace("\r\n", "\n"))
    if not result.succeeded or summaries != [("PASS", "OK")]:
        raise RunnerFailure("FAIL_CLEANUP")


def run_one(target: ExecutionTarget, repetition: int, *, contract: RunContract = DATA_MODEL_CONTRACT) -> RunResult:
    failure: RunnerFailure | None = None
    try:
        check_harness(run_harness(target, contract=contract), contract=contract)
    except RunnerFailure as exc:
        failure = exc
    except subprocess.TimeoutExpired:
        failure = RunnerFailure("FAIL_TIMEOUT")
    except (ExecutionTargetError, OSError, ValueError, KeyboardInterrupt):
        failure = RunnerFailure("FAIL_EXECUTION")
    finally:
        cleanup_failed = False
        try:
            assert_absent(target)
        except (RunnerFailure, ExecutionTargetError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt):
            cleanup_failed = True
            # Auch bei fehlgeschlagener Recovery die unabhängige Prüfung ausführen.
            try:
                recover(target)
            except (RunnerFailure, ExecutionTargetError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt):
                pass
            finally:
                try:
                    assert_absent(target)
                except (RunnerFailure, ExecutionTargetError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt):
                    pass
        if cleanup_failed or (failure is not None and failure.code == "FAIL_CLEANUP"):
            failure = RunnerFailure("FAIL_CLEANUP")
        cleanup_outcome = "FAIL|FAIL_CLEANUP" if failure and failure.code == "FAIL_CLEANUP" else "PASS|OK"
        print(f"DGN007_CLEANUP|RUN_{repetition}|{cleanup_outcome}")
    if failure:
        print(f"DGN007_STAGE|{contract.scope}|RUN_{repetition}|FAIL|{failure.code}")
        raise failure
    print(f"DGN007_STAGE|{contract.scope}|RUN_{repetition}|PASS|OK")
    return RunResult(repetition)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ausgewählten DGN-007-AUTO-Schnitt zweimal auf einer leeren Docker-Wegwerfinstanz prüfen.")
    parser.add_argument("--scope", choices=("data-model", "query-store-windows", "profile-comparison"), default="data-model")
    parser.add_argument("--target", choices=(execution_target.DOCKER,), default=execution_target.DOCKER)
    parser.add_argument("--container", required=True)
    parser.add_argument("--expected-major", type=int, choices=(15, 16, 17), required=True)
    parser.add_argument("--confirm-disposable-instance", action="store_true",
                        help="Isolierte Wegwerfinstanz, gelben Lab-Lauf und markergebundenen AUTO-Datenbankabbau bestätigen.")
    parser.add_argument("--confirm-isolated-lab", action="store_true",
                        help="Zusätzliche Lab-Bestätigung; --confirm-disposable-instance bleibt erforderlich.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    contract = scope_contract(args.scope)
    runs = 0
    code = "OK"
    try:
        if not args.confirm_disposable_instance:
            raise RunnerFailure("FAIL_SAFETY")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", args.container):
            raise RunnerFailure("FAIL_CONTRACT")
        if not os.environ.get("SQLCMDPASSWORD"):
            raise RunnerFailure("FAIL_SAFETY")
        validate_manifest(contract=contract)
        target = resolve_target(args.container)
        execution_target.verify_engine(target, expected_major=args.expected_major)
        assert_empty_instance(target)
        for repetition in (1, 2):
            run_one(target, repetition, contract=contract)
            runs += 1
    except RunnerFailure as exc:
        code = exc.code
    except subprocess.TimeoutExpired:
        code = "FAIL_TIMEOUT"
    except (ExecutionTargetError, OSError, ValueError, KeyboardInterrupt):
        code = "FAIL_EXECUTION"
    outcome = "PASS" if code == "OK" and runs == 2 else "FAIL"
    print(f"DGN007_SUMMARY|{outcome}|{code}|major={args.expected_major}; runs={runs}; target=docker; scope={contract.scope}")
    return 0 if outcome == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
