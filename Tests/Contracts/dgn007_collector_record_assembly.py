"""Verlustfreie Abbildung eines geprüften Capture-Bodys auf einen RunRecord.

Der Mapper validiert deklarierte Metadaten und Phasen, attestiert aber weder
deren Herkunft noch Freeze, Ressourcen, echte Lifecycle-Chronologie oder
Budgets. Nur der spätere vertrauensgebundene Coordinator darf diese Eingaben
aus tatsächlichen Aktionen liefern.
"""
from __future__ import annotations

from Tests.Contracts.dgn007_collector_transport import CaptureBody, RequestCapture, SCHEMA
from Tests.Contracts.dgn007_prospective_acceptance import (
    AcceptanceContract, BLOCKS, PHASE_IDS, PhaseResult, RequestRecord, RunRecord, _RecordError,
    _contract_valid, _run_valid,
)


class AssemblyError(ValueError):
    """Feste Vertragscodes ohne Rohdaten oder interne Exceptionkette."""

    def __init__(self, code: str = "FAIL_CONTRACT") -> None:
        self.code = code if code in ("FAIL_CONTRACT", "FAIL_RESULT_CONTRACT") else "FAIL_CONTRACT"
        super().__init__(self.code)


def assemble_run(body: CaptureBody, contract: AcceptanceContract, *, expected_major: int,
                 block: int, slot: int, lifecycle_id: int, phases: tuple[PhaseResult, ...],
                 absence: PhaseResult) -> RunRecord:
    """Mappt genau einen vollständigen Body und Callerbelege in Evaluatorrecords.

    `block` und `slot` sind 1-basiert. Callerbelege werden strikt geprüft,
    aber nicht als unabhängig beobachtet attestiert.
    """
    if type(contract) is not AcceptanceContract or not _contract_valid(contract):
        raise AssemblyError()
    if type(body) is not CaptureBody or body.schema != SCHEMA:
        raise AssemblyError()
    if (type(block) is not int or block not in (1, 2)
            or type(slot) is not int or slot not in (1, 2, 3)
            or type(lifecycle_id) is not int or lifecycle_id <= 0):
        raise AssemblyError()
    sequence = BLOCKS[block - 1][slot - 1]
    if (type(expected_major) is not int or expected_major not in (15, 16, 17)
            or type(body.major) is not int or body.major != expected_major
            or body.compatibility != body.major * 10
            or body.scope != "DGN-007_CONTROL_" + sequence
            or body.contract_digest != contract.contract_digest
            or body.source_digest != contract.source_digest
            or not body.row_evidence_complete):
        raise AssemblyError("FAIL_RESULT_CONTRACT")
    if (type(phases) is not tuple or len(phases) != len(PHASE_IDS)
            or any(type(row) is not PhaseResult for row in phases)
            or tuple(row.phase_id for row in phases) != PHASE_IDS
            or any((row.outcome, row.code) != ("PASS", "OK") for row in phases)
            or type(absence) is not PhaseResult
            or absence.phase_id != "CLEANUP_ABSENCE"
            or (absence.outcome, absence.code) != ("PASS", "OK")):
        raise AssemblyError()
    requests = tuple(RequestRecord(
        window_id=row.window_id, ordinal=row.ordinal, request_log_id=row.request_log_id,
        group_key=row.group_key, status_code=row.status_code, returned_rows=row.returned_rows,
    ) for row in body.requests if type(row) is RequestCapture and row.row_evidence == "MEASURED")
    if len(requests) != len(body.requests):
        raise AssemblyError("FAIL_RESULT_CONTRACT")
    run = RunRecord(
        major=body.major, compatibility=body.compatibility, block=block, slot=slot,
        lifecycle_id=lifecycle_id, scope=body.scope,
        contract_digest=body.contract_digest, source_digest=body.source_digest,
        parent_object_id=body.parent_object_id, phases=phases,
        absence_outcome=absence.outcome, absence_code=absence.code,
        requests=requests, families=body.families, windows=body.windows,
        plans=body.plans, plan_union=body.plan_union,
    )
    failure_code = None
    try:
        _run_valid(run, sequence, contract.schema)
    except _RecordError as error:
        failure_code = error.args[0] if error.args else "FAIL_RESULT_CONTRACT"
    if failure_code is not None:
        raise AssemblyError(failure_code)
    return run
