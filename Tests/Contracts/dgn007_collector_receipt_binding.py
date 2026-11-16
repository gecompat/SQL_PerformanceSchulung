"""Bindet belegte Runner-Receipt-Felder an einen deklarativen Coordinator-Record.

Die ersten sieben äußeren Phasen, Ressourcen und Source-Freeze bleiben Eingaben
des Aufrufers. Nur Lifecycle- und Cleanup-Zeit stammen direkt aus dem internen
Erfolgsreceipt. Das Modul attestiert weder deren Herkunft noch eine SQL-Runtime.
"""
from __future__ import annotations

from Tests.Contracts.dgn007_collector_coordinator import (
    CoordinatedRun, CoordinatorError, PHASES, TimedPhase,
)
from Tests.Contracts.dgn007_collector_record_assembly import assemble_run, AssemblyError
from Tests.Contracts.dgn007_prospective_acceptance import (
    AcceptanceContract, PHASE_IDS, PhaseResult, _contract_valid,
)


def bind_receipt(contract: AcceptanceContract, receipt, *, expected_major: int,
                 block: int, slot: int, lifecycle_id: int,
                 observed_phases: tuple[TimedPhase, ...], configured_cpus: int,
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
    if (type(observed_phases) is not tuple or len(observed_phases) != len(PHASES) - 1
            or any(type(row) is not TimedPhase for row in observed_phases)
            or tuple(row.phase_id for row in observed_phases) != PHASES[:-1]):
        raise CoordinatorError()
    started = receipt.lifecycle_started_ns
    cleanup_started = receipt.cleanup_started_ns
    finished = receipt.lifecycle_finished_ns
    if (type(started) is not int or type(cleanup_started) is not int
            or type(finished) is not int
            or not (0 <= started < cleanup_started < finished)):
        raise CoordinatorError("FAIL_CLEANUP")
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
    return CoordinatedRun(
        record, started, finished, phases, configured_cpus, configured_memory_mb,
        active_sql_sessions, active_versions_on_host, source_freeze_verified, True,
    )
