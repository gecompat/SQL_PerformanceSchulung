"""Bounded prequalification of a complete prospective DGN-007 run sequence.

This module validates assembled records and coordinator-supplied observations.
It does not establish the trustworthiness of those observations, freeze source
bytes during execution, or attest a SQL Server runtime.
"""
from __future__ import annotations

from dataclasses import dataclass

from Tests.Contracts.dgn007_prospective_acceptance import (
    AcceptanceContract, BLOCKS, RunRecord, _contract_valid, _run_valid,
)


class CoordinatorError(ValueError):
    """Stable failure codes without payloads or exception context."""

    def __init__(self, code: str = "FAIL_CONTRACT") -> None:
        self.code = code if code in ("FAIL_CONTRACT", "FAIL_RESULT_CONTRACT",
                                     "FAIL_TIMEOUT", "FAIL_CLEANUP",
                                     "SKIP_EVIDENCE_MISSING") else "FAIL_CONTRACT"
        super().__init__(self.code)


@dataclass(frozen=True, slots=True)
class TimedPhase:
    phase_id: str
    started_ns: int
    finished_ns: int
    outcome: str
    code: str


@dataclass(frozen=True, slots=True)
class CoordinatedRun:
    record: RunRecord
    started_ns: int
    finished_ns: int
    phases: tuple[TimedPhase, ...]
    configured_cpus: int
    configured_memory_mb: int
    active_sql_sessions: int
    active_versions_on_host: int
    source_freeze_verified: bool
    cleanup_independently_confirmed: bool


EXPECTED_SEQUENCE = tuple((block, slot, label)
                          for block, labels in enumerate(BLOCKS, 1)
                          for slot, label in enumerate(labels, 1))
PHASES = ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "CONTROL_CONFIG",
          "CONTROL_WINDOWS", "PROFILE_COMPARISON", "CONTROL_EVIDENCE", "CLEANUP")


def validate_sequence(contract: AcceptanceContract,
                      runs: tuple[CoordinatedRun, ...]) -> tuple[RunRecord, ...]:
    """Check declared order, monotonic timing, budgets, resource bounds and cleanup.

    Values are accepted only as coordinator inputs. Passing this function is a
    PROJECT_SEMANTIC check, not evidence that the caller observed them correctly.
    """
    if type(contract) is not AcceptanceContract or not _contract_valid(contract):
        raise CoordinatorError()
    if type(runs) is not tuple or len(runs) != len(EXPECTED_SEQUENCE):
        raise CoordinatorError("SKIP_EVIDENCE_MISSING")
    previous_finish = -1
    lifecycle_ids = set()
    expected_major = None
    records = []
    for item, expected in zip(runs, EXPECTED_SEQUENCE):
        if type(item) is not CoordinatedRun or type(item.record) is not RunRecord:
            raise CoordinatorError()
        record = item.record
        block, slot, label = expected
        if ((record.block, record.slot, record.scope) !=
                (block, slot, "DGN-007_CONTROL_" + label)
                or record.contract_digest != contract.contract_digest
                or record.source_digest != contract.source_digest):
            raise CoordinatorError("FAIL_RESULT_CONTRACT")
        if (type(record.major) is not int or record.major not in (15, 16, 17)
                or (expected_major is not None and record.major != expected_major)
                or type(record.lifecycle_id) is not int or record.lifecycle_id <= 0
                or record.lifecycle_id in lifecycle_ids):
            raise CoordinatorError("FAIL_RESULT_CONTRACT")
        expected_major = record.major
        lifecycle_ids.add(record.lifecycle_id)
        if (type(item.started_ns) is not int or type(item.finished_ns) is not int
                or item.started_ns < 0 or item.finished_ns <= item.started_ns
                or item.started_ns < previous_finish):
            raise CoordinatorError("FAIL_CONTRACT")
        previous_finish = item.finished_ns
        if (type(item.configured_cpus) is not int or item.configured_cpus < 4
                or type(item.configured_memory_mb) is not int or item.configured_memory_mb < 8192
                or type(item.active_sql_sessions) is not int or item.active_sql_sessions != 1
                or type(item.active_versions_on_host) is not int or item.active_versions_on_host != 1
                or item.source_freeze_verified is not True):
            raise CoordinatorError("FAIL_CONTRACT")
        if item.cleanup_independently_confirmed is not True:
            raise CoordinatorError("FAIL_CLEANUP")
        if (type(item.phases) is not tuple or len(item.phases) != len(PHASES)
                or any(type(phase) is not TimedPhase for phase in item.phases)):
            raise CoordinatorError()
        if tuple(p.phase_id for p in item.phases) != PHASES:
            raise CoordinatorError()
        prior = item.started_ns
        cleanup_started = None
        for phase in item.phases:
            if (type(phase) is not TimedPhase or type(phase.started_ns) is not int
                    or type(phase.finished_ns) is not int or phase.started_ns < prior
                    or phase.finished_ns <= phase.started_ns
                    or phase.finished_ns > item.finished_ns
                    or (phase.outcome, phase.code) != ("PASS", "OK")):
                raise CoordinatorError("FAIL_CLEANUP" if phase.phase_id == "CLEANUP"
                                       and (phase.outcome, phase.code) != ("PASS", "OK")
                                       else "FAIL_CONTRACT")
            if phase.phase_id == "CLEANUP":
                cleanup_started = phase.started_ns
            prior = phase.finished_ns
        if (cleanup_started is None or item.phases[-1].finished_ns != item.finished_ns):
            raise CoordinatorError("FAIL_CLEANUP")
        regular_ns = cleanup_started - item.started_ns
        cleanup_ns = item.finished_ns - cleanup_started
        if regular_ns > 180_000_000_000 or cleanup_ns > 60_000_000_000:
            raise CoordinatorError("FAIL_TIMEOUT")
        try:
            _run_valid(record, label, contract.schema)
        except Exception:
            raise CoordinatorError("FAIL_RESULT_CONTRACT") from None
        records.append(record)
    return tuple(records)
