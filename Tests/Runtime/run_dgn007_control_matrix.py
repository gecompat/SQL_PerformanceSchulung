#!/usr/bin/env python3
"""Run and bind the six real DGN-007 control captures in DEC-068 order.

Only compact outcome codes are written to stdout. Capture bodies and assembled
records remain in memory and are never persisted. Host inventory is checked at
each lifecycle boundary; this does not prove continuous host exclusivity.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Tests.Contracts.dgn007_collector_coordinator import EXPECTED_SEQUENCE, CoordinatorError
from Tests.Contracts.dgn007_collector_receipt_binding import (
    ReceiptObservation, bind_sequence,
)
from Tests.Contracts.dgn007_prospective_acceptance import contract_from_mapping, evaluate_version
from Tests.Runtime import run_dgn007_automated_setup as runner
from Tests.Runtime import execution_target

CONTROL_CONTRACTS = {
    "AB": runner.CONTROL_AB_CONTRACT,
    "BA": runner.CONTROL_BA_CONTRACT,
    "AA": runner.CONTROL_AA_CONTRACT,
}
ACCEPTANCE_CONTRACT = (
    ROOT / "Demos/07_Query_Store_Extended_Events/"
    "DGN-007_Time_Bounded_Search_Incident/Contracts/incident-acceptance.contract.json"
)
MAX_CONTAINERS = 8
DOCKER_ID = re.compile(r"[0-9a-f]{64}")
SQLSERVER_COMM = frozenset(("sqlservr", "sqlservr.exe"))


class CoordinatorRuntimeError(RuntimeError):
    """A bounded, payload-free failure from the runtime coordinator."""

    def __init__(self, code: str = "FAIL_CONTRACT") -> None:
        self.code = code if code in (
            "FAIL_CONTRACT", "FAIL_RESULT_CONTRACT", "FAIL_TIMEOUT",
            "FAIL_CLEANUP", "FAIL_EXECUTION", "FAIL_SAFETY",
            "FAIL_DOCKER_INSPECT", "FAIL_DOCKER_INVENTORY", "FAIL_DOCKER_TOP",
            "FAIL_SQLCMD_RESOLUTION",
        ) else "FAIL_CONTRACT"
        super().__init__(self.code)


def _docker(command: list[str], *, timeout: int = 10,
            failure_code: str = "FAIL_EXECUTION") -> str:
    try:
        result = subprocess.run(command, check=False, capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=timeout)
    except subprocess.TimeoutExpired:
        raise CoordinatorRuntimeError("FAIL_TIMEOUT") from None
    except OSError:
        raise CoordinatorRuntimeError("FAIL_EXECUTION") from None
    if result.returncode != 0:
        raise CoordinatorRuntimeError(failure_code)
    return result.stdout


def observe_sqlserver_processes(target_container: str) -> tuple[tuple[str, int], ...]:
    """Return container-ID/PID pairs for active SQL Server processes.

    Every running Docker container is inspected. An uninspectable container or
    an ambiguous SQL process inventory fails closed; no container output is
    forwarded to the caller.
    """
    if (type(target_container) is not str or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", target_container)):
        raise CoordinatorRuntimeError()
    target_id = _docker(
        ["docker", "inspect", "--format", "{{.Id}}", target_container],
        failure_code="FAIL_DOCKER_INSPECT",
    ).strip()
    if DOCKER_ID.fullmatch(target_id) is None:
        raise CoordinatorRuntimeError()
    container_text = _docker(
        ["docker", "ps", "--no-trunc", "--quiet"],
        failure_code="FAIL_DOCKER_INVENTORY",
    )
    container_ids = tuple(line.strip() for line in container_text.splitlines() if line.strip())
    if (not container_ids or len(container_ids) > MAX_CONTAINERS
            or any(DOCKER_ID.fullmatch(value) is None for value in container_ids)
            or target_id not in container_ids):
        raise CoordinatorRuntimeError()
    sql_processes: list[tuple[str, int]] = []
    for container_id in container_ids:
        output = _docker(
            ["docker", "top", container_id],
            failure_code="FAIL_DOCKER_TOP",
        )
        for line in output.splitlines():
            fields = line.strip().split(None, 7)
            if len(fields) != 8 or not fields[1].isdecimal():
                continue
            command = fields[7].split(None, 1)[0].replace("\\", "/").rsplit("/", 1)[-1].casefold()
            if command in SQLSERVER_COMM:
                sql_processes.append((container_id, int(fields[1])))
    if (len(sql_processes) != 1 or sql_processes[0][0] != target_id
            or sql_processes[0][1] <= 0):
        raise CoordinatorRuntimeError()
    return tuple(sql_processes)


def load_acceptance_contract():
    try:
        mapping = json.loads(ACCEPTANCE_CONTRACT.read_text(encoding="utf-8"))
        return contract_from_mapping(mapping)
    except (OSError, ValueError, TypeError):
        raise CoordinatorRuntimeError("FAIL_CONTRACT") from None


def resolve_target(container: str):
    """Resolve the in-container sqlcmd path with a bounded Docker call."""
    output = _docker([
        "docker", "exec", container, "sh", "-lc",
        "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then "
        "printf /opt/mssql-tools18/bin/sqlcmd; "
        "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then "
        "printf /opt/mssql-tools/bin/sqlcmd; "
        "else exit 127; fi",
    ], failure_code="FAIL_SQLCMD_RESOLUTION").strip()
    if output not in ("/opt/mssql-tools18/bin/sqlcmd", "/opt/mssql-tools/bin/sqlcmd"):
        raise CoordinatorRuntimeError("FAIL_EXECUTION")
    return execution_target.docker_target(container=container, sqlcmd_path=output)


def run_control_matrix(container: str, expected_major: int):
    """Capture six lifecycles, bind actual receipts, and evaluate one version."""
    if type(expected_major) is not int or expected_major not in (15, 16, 17):
        raise CoordinatorRuntimeError()
    if not os.environ.get("SQLCMDPASSWORD"):
        raise CoordinatorRuntimeError("FAIL_SAFETY")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container):
        raise CoordinatorRuntimeError()

    try:
        contract = load_acceptance_contract()
        initial_processes = observe_sqlserver_processes(container)
        target = resolve_target(container)
        execution_target.verify_engine(target, expected_major=expected_major)
        runner.assert_empty_instance(target)

        receipts = []
        observations = []
        for index, (_block, _slot, label) in enumerate(EXPECTED_SEQUENCE, 1):
            run_contract = CONTROL_CONTRACTS[label]
            runner.validate_manifest(contract=run_contract)
            before = observe_sqlserver_processes(container)
            if before != initial_processes:
                raise CoordinatorRuntimeError("FAIL_CONTRACT")
            runner.assert_empty_instance(target)
            receipt = runner._run_capture_one(
                target, index, contract=run_contract, expected_major=expected_major,
                expected_contract=contract,
            )
            after = observe_sqlserver_processes(container)
            if after != before:
                raise CoordinatorRuntimeError("FAIL_CONTRACT")
            receipts.append(receipt)
            observations.append(ReceiptObservation(
                lifecycle_id=receipt.lifecycle_started_ns,
                active_versions_on_host=1,
            ))
        bound = bind_sequence(
            contract, tuple(receipts), expected_major=expected_major,
            observations=tuple(observations),
        )
        records = tuple(item.record for item in bound)
        decision = evaluate_version(contract, expected_major, records)
        if decision.outcome not in ("PASS", "SKIP"):
            raise CoordinatorRuntimeError(decision.code)
        return decision
    except CoordinatorRuntimeError:
        raise
    except (CoordinatorError, runner.RunnerFailure) as error:
        code = getattr(error, "code", "FAIL_CONTRACT")
        raise CoordinatorRuntimeError(code) from None
    except (execution_target.ExecutionTargetError, OSError, ValueError,
            subprocess.TimeoutExpired):
        raise CoordinatorRuntimeError("FAIL_EXECUTION") from None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Führe sechs isolierte DGN-007-Control-Lifecycles in DEC-068-Reihenfolge aus."
    )
    parser.add_argument("--container", required=True)
    parser.add_argument("--expected-major", required=True, type=int, choices=(15, 16, 17))
    parser.add_argument("--confirm-disposable-instance", action="store_true")
    parser.add_argument("--confirm-isolated-lab", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    code = "OK"
    decision_outcome = "NOT_RUN"
    decision_code = "NOT_RUN"
    try:
        if not args.confirm_disposable_instance or not args.confirm_isolated_lab:
            raise CoordinatorRuntimeError("FAIL_SAFETY")
        decision = run_control_matrix(args.container, args.expected_major)
        decision_outcome, decision_code = decision.outcome, decision.code
    except CoordinatorRuntimeError as error:
        code = error.code
    except KeyboardInterrupt:
        code = "FAIL_EXECUTION"
    outcome = "PASS" if code == "OK" else "FAIL"
    print(
        f"DGN007_COORDINATOR|{outcome}|{code}|major={args.expected_major}; "
        f"captures={len(EXPECTED_SEQUENCE) if code == 'OK' else 0}; "
        f"decision={decision_outcome}; decision_code={decision_code}"
    )
    return 0 if code == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
