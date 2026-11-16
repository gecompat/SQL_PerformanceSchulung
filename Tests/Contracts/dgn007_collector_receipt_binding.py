"""Bindet belegte Runner-Receipt-Felder an einen deklarativen Coordinator-Record.

Die sieben äußeren Phasenzeiten stammen aus dem privaten FWK-010-Zeitprotokoll;
Ressourcen und Source-Freeze bleiben Eingaben des Aufrufers. Lifecycle- und
Cleanup-Zeit stammen direkt aus dem internen Erfolgsreceipt. Das Modul attestiert
weder Quellherkunft noch Ressourcen oder eine SQL-Runtime.
"""
from __future__ import annotations

from dataclasses import dataclass

from Tests.Contracts.dgn007_collector_coordinator import (
    CoordinatedRun, CoordinatorError, EXPECTED_SEQUENCE, PHASES, TimedPhase,
    validate_sequence,
)
from Tests.Contracts.dgn007_collector_record_assembly import assemble_run, AssemblyError
from Tests.Contracts.dgn007_prospective_acceptance import (
    AcceptanceContract, PHASE_IDS, PhaseResult, _contract_valid,
)


@dataclass(frozen=True, slots=True)
class ReceiptObservation:
    """Callerangaben zu Lifecycle-ID und Ressourcen je Receipt."""

    lifecycle_id: int
    configured_cpus: int
    configured_memory_mb: int
    active_sql_sessions: int
    active_versions_on_host: int
    source_freeze_verified: bool


def bind_receipt(contract: AcceptanceContract, receipt, *, expected_major: int,
                 block: int, slot: int, lifecycle_id: int,
                 configured_cpus: int,
                 configured_memory_mb: int, active_sql_sessions: int,
                 active_versions_on_host: int, source_freeze_verified: bool) -> CoordinatedRun:
    """Erzeugt einen Coordinator-Record; Cleanup wird nie vom Caller geliefert."""
    from Tests.Runtime.run_dgn007_automated_setup import _CaptureReceipt

    if type(contract) is not AcceptanceContract or not _contract_valid(contract):
        raise CoordinatorError()
    if type(receipt) is not _CaptureReceipt:
        raise CoordinatorError()
    if (receipt.first_absence_outcome, receipt.first_absence_code) != ("PASS", "OK"):
        raise CoordinatorError("FAIL_CLEANUP")
    if (type(receipt.repetition) is not int or receipt.repetition <= 0
            or type(receipt.phases) is not tuple
            or len(receipt.phases) != len(PHASE_IDS)
            or any(type(row) is not tuple or len(row) != 3 for row in receipt.phases)
            or tuple(row[0] for row in receipt.phases) != PHASE_IDS
            or any(row[1:] != ("PASS", "OK") for row in receipt.phases)):
        raise CoordinatorError("FAIL_RESULT_CONTRACT")
    timing = receipt.phase_timing
    if (type(timing) is not tuple or len(timing) != len(PHASES) - 1
            or any(type(row) is not tuple or len(row) != 3 for row in timing)
            or tuple(row[0] for row in timing) != PHASES[:-1]):
        raise CoordinatorError()
    started = receipt.lifecycle_started_ns
    cleanup_started = receipt.cleanup_started_ns
    finished = receipt.lifecycle_finished_ns
    if (type(started) is not int or type(cleanup_started) is not int
            or type(finished) is not int
            or not (0 <= started < cleanup_started < finished)):
        raise CoordinatorError("FAIL_CLEANUP")
    observed_phases = tuple(TimedPhase(name, phase_started, phase_finished, "PASS", "OK")
                            for name, phase_started, phase_finished in timing)
    phases = (*observed_phases, TimedPhase("CLEANUP", cleanup_started, finished, "PASS", "OK"))
    run_phases = tuple(PhaseResult(name, outcome, code)
                       for name, outcome, code in receipt.phases)
    absence = PhaseResult("CLEANUP_ABSENCE", receipt.first_absence_outcome,
                          receipt.first_absence_code)
    try:
        record = assemble_run(receipt.body, contract, expected_major=expected_major,
                              block=block, slot=slot, lifecycle_id=lifecycle_id,
                              phases=run_phases, absence=absence)
    except AssemblyError as error:
        raise CoordinatorError(error.code) from None
    previous_finish = started
    for phase in observed_phases:
        if (type(phase.started_ns) is not int or type(phase.finished_ns) is not int
                or phase.started_ns < previous_finish
                or phase.finished_ns <= phase.started_ns
                or phase.finished_ns > cleanup_started
                or (phase.outcome, phase.code) != ("PASS", "OK")):
            raise CoordinatorError("FAIL_CONTRACT")
        previous_finish = phase.finished_ns
    if previous_finish - started > 180_000_000_000:
        raise CoordinatorError("FAIL_TIMEOUT")
    return CoordinatedRun(
        record, started, finished, phases, configured_cpus, configured_memory_mb,
        active_sql_sessions, active_versions_on_host, source_freeze_verified, True,
    )


def bind_sequence(contract: AcceptanceContract, receipts: tuple, *, expected_major: int,
                  observations: tuple[ReceiptObservation, ...]) -> tuple[CoordinatedRun, ...]:
    """Bindet exakt sechs Receipts positionsgebunden und prüft den Matrixvertrag."""
    if (type(receipts) is not tuple or type(observations) is not tuple
            or len(receipts) != len(EXPECTED_SEQUENCE)
            or len(observations) != len(EXPECTED_SEQUENCE)):
        raise CoordinatorError("SKIP_EVIDENCE_MISSING")
    if any(type(item) is not ReceiptObservation for item in observations):
        raise CoordinatorError()
    runs = []
    for receipt, observation, (block, slot, _label) in zip(
            receipts, observations, EXPECTED_SEQUENCE):
        runs.append(bind_receipt(
            contract, receipt, expected_major=expected_major, block=block, slot=slot,
            lifecycle_id=observation.lifecycle_id,
            configured_cpus=observation.configured_cpus,
            configured_memory_mb=observation.configured_memory_mb,
            active_sql_sessions=observation.active_sql_sessions,
            active_versions_on_host=observation.active_versions_on_host,
            source_freeze_verified=observation.source_freeze_verified,
        ))
    complete = tuple(runs)
    validate_sequence(contract, complete)
    return complete
