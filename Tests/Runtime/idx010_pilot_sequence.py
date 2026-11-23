"""Orchestration for the ordered NCCI pilot, independent of the SQL transport."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from time import monotonic
from typing import Protocol

from idx010_pilot_setup import (
    Arm,
    INDEX_NAME,
    ROWGROUP_COUNT,
    ROWGROUP_ROWS,
    fixture_chunk_batch,
    fixture_identity_batch,
    fixture_setup_batch,
    index_build_batch,
    target_database,
    verify_fixture_identity,
)
from idx010_query_evidence import QUERY, SegmentCounts, verify_query_evidence


WORK_SECONDS = 900
CLEANUP_SECONDS = 90


@dataclass(frozen=True)
class Target:
    run_token: str
    arm: Arm

    @property
    def database_name(self) -> str:
        return target_database(self.run_token, self.arm)


@dataclass(frozen=True)
class IndexEvidence:
    database_name: str
    index_name: str
    order_ordinal: int
    rowgroup_sizes: tuple[int, ...]
    has_delta_or_deleted_rows: bool
    eligible_segments: int
    overlapping_pairs: int  # From complete segment evidence with unique endpoints.


@dataclass(frozen=True)
class QueryCapture:
    """All outputs from one request in a dedicated measurement session."""

    plan_xml: str
    info_messages: tuple[str, ...]
    result_rows: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class ArmEvidence:
    arm: Arm
    overlapping_pairs: int
    segments: SegmentCounts


@dataclass(frozen=True)
class PilotResult:
    status: str
    stage: str
    arms: tuple[ArmEvidence, ...] = ()


class PilotTransport(Protocol):
    """All operations use the owned SQL instance and honor absolute deadlines."""

    def start_verified_instance(self, run_token: str, deadline: float) -> None:
        """Start with a registered owner and check image, build and resource limits."""

    def provision(self, target: Target, deadline: float) -> None:
        """Create a new database with the exact profile markers and cap file sizes."""

    def execute(self, target: Target, sql: str, deadline: float) -> None:
        """Execute setup as a single batch in the intended database."""

    def stream_rows(self, target: Target, sql: str, deadline: float) -> Iterable[tuple[int, int]]:
        """Read in bounded chunks and close the cursor when the iterator closes."""

    def index_evidence(self, target: Target, deadline: float) -> IndexEvidence:
        """Resolve catalog identities and complete Microsoft order-quality evidence."""

    def capture_query(self, target: Target, sql: str, deadline: float) -> QueryCapture:
        """Bind result, actual plan and InfoMessages to one read-only request."""

    def cleanup(self, run_token: str, attempted: tuple[Target, ...], deadline: float) -> bool:
        """Verify owner markers before deletion and confirm resource absence.

        Handle partly completed provisioning. A resource whose ownership
        cannot be proved must not be deleted. Return False if the SQL or
        container cleanup cannot be confirmed.
        """


def run_pilot(transport: PilotTransport, run_token: str) -> PilotResult:
    targets = tuple(Target(run_token, arm) for arm in Arm)
    for target in targets:
        target_database(target.run_token, target.arm)

    deadline = monotonic() + WORK_SECONDS
    attempted: list[Target] = []
    evidence: list[ArmEvidence] = []
    stage = "preflight"
    status = "NOT_PROVEN"
    cleaned = False
    try:
        transport.start_verified_instance(run_token, deadline)
        stage = "fixture"
        for target in targets:
            _check_deadline(deadline)
            attempted.append(target)
            transport.provision(target, deadline)
            transport.execute(target, fixture_setup_batch(run_token, target.arm), deadline)
            for chunk in range(ROWGROUP_COUNT):
                _check_deadline(deadline)
                transport.execute(target, fixture_chunk_batch(run_token, target.arm, chunk), deadline)

        stage = "identity"
        for target in targets:
            _check_deadline(deadline)
            rows = iter(transport.stream_rows(target, fixture_identity_batch(run_token, target.arm), deadline))
            try:
                verify_fixture_identity(rows)
            finally:
                close = getattr(rows, "close", None)
                if close is not None:
                    close()

        stage = "index"
        for target in targets:
            _check_deadline(deadline)
            transport.execute(target, index_build_batch(run_token, target.arm), deadline)

        stage = "metadata"
        indexes: list[IndexEvidence] = []
        for target in targets:
            _check_deadline(deadline)
            index = transport.index_evidence(target, deadline)
            _verify_index(target, index)
            indexes.append(index)

        control_index, ordered_index = indexes
        if control_index.overlapping_pairs <= ordered_index.overlapping_pairs:
            raise ValueError("index layouts do not provide an ordered NCCI comparison")

        stage = "query"
        for target, index in zip(targets, indexes, strict=True):
            _check_deadline(deadline)
            capture = transport.capture_query(target, QUERY, deadline)
            counts = verify_query_evidence(
                plan_xml=capture.plan_xml,
                info_messages=capture.info_messages,
                result_rows=capture.result_rows,
                database_name=target.database_name,
                index_name=INDEX_NAME,
            )
            evidence.append(ArmEvidence(target.arm, index.overlapping_pairs, counts))

        stage = "comparison"
        _check_deadline(deadline)
        control, ordered = evidence
        if ordered.segments.skipped > control.segments.skipped:
            status = "PASS"
    except (TimeoutError, ValueError, OSError):
        # SQL adapters translate operational errors to OSError; raw payloads stay local.
        status = "NOT_PROVEN"
    finally:
        cleanup_deadline = monotonic() + CLEANUP_SECONDS
        try:
            cleaned = transport.cleanup(run_token, tuple(attempted), cleanup_deadline) is True
            _check_deadline(cleanup_deadline)
        except (TimeoutError, ValueError, OSError):
            cleaned = False

    if not cleaned:
        return PilotResult("FAIL_CLEANUP", stage, tuple(evidence))
    return PilotResult(status, stage, tuple(evidence))


def _check_deadline(deadline: float) -> None:
    if monotonic() >= deadline:
        raise TimeoutError("pilot deadline exceeded")


def _verify_index(target: Target, index: IndexEvidence) -> None:
    ordinal = 1 if target.arm is Arm.ORDERED else 0
    max_pairs = ROWGROUP_COUNT * (ROWGROUP_COUNT - 1) // 2
    if (
        index.database_name != target.database_name
        or index.index_name != INDEX_NAME
        or type(index.order_ordinal) is not int
        or index.order_ordinal != ordinal
        or index.rowgroup_sizes != (ROWGROUP_ROWS,) * ROWGROUP_COUNT
        or index.has_delta_or_deleted_rows is not False
        or index.eligible_segments != ROWGROUP_COUNT
        or type(index.overlapping_pairs) is not int
        or not 0 <= index.overlapping_pairs <= max_pairs
    ):
        raise ValueError("catalog evidence does not match the fixed index profile")
