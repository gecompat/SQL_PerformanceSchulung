"""Run the three External Tables measurement routes on an admitted transport."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from time import monotonic, sleep
from typing import ContextManager, Protocol

from external_tables_driver_evidence import DriverEvidence
from external_tables_pilot_sql import Role, Route, aggregate_batch, database_name, verify_aggregate
from external_tables_pushdown_evidence import Work, active_request_batch, external_work_batch, verify_pushdown


AggregateRows = tuple[tuple[int, int, int], ...]


class UnconfirmedRequestCleanup(OSError):
    """The transport could not confirm closure of its owned request."""


class PendingAggregate(Protocol):
    session_id: int
    request_id: int

    def finished(self) -> bool:
        """Check completion without releasing the dedicated Reader connection."""

    def result(self, deadline: float) -> AggregateRows:
        """Read all rows and confirm successful completion before the deadline."""


class MeasurementTransport(Protocol):
    """Provide owned Reader and separate observer connections on the query guest."""

    def aggregate(self, sql: str, deadline: float) -> ContextManager[PendingAggregate]:
        """Submit once on a fresh connection with no other requests.

        Exit must close the connection and confirm the request has ended,
        cancelling only that request on error. Unconfirmed exit raises
        UnconfirmedRequestCleanup.
        """

    def active_handles(self, sql: str, deadline: float) -> tuple[str, ...]:
        """Return the complete handle result of the exact observer statement."""

    def external_work(self, sql: str, deadline: float) -> tuple[Work, ...]:
        """Return the bounded records of the exact observer statement."""


@dataclass(frozen=True)
class MeasurementResult:
    status: str
    stage: str
    filters: tuple[str, str] | None = None
    driver: DriverEvidence | None = None


def measure_pushdown(
    transport: MeasurementTransport, token: str, deadline: float, *,
    observe_driver: Callable[[Callable[[], bool], float], DriverEvidence] | None = None,
) -> MeasurementResult:
    """Use once per fresh run token, after fixture and statistics verification.

    The pilot owns the enclosing deadline and SQL/guest teardown. This function
    keeps payloads local and reports only the completed comparison.
    """
    database_name(token, Role.QUERY)
    records: list[tuple[Work, ...]] = []
    witnessed_handles: set[str] = set()
    driver = None
    driver_unconfirmed = False
    stage = Route.LOCAL.name
    try:
        for route in Route:
            stage = route.name
            _check_deadline(deadline)
            with transport.aggregate(aggregate_batch(token, route), deadline) as request:
                if route is Route.LOCAL:
                    verify_aggregate(request.result(deadline))
                    continue

                statement = active_request_batch(token, route, request.session_id, request.request_id)
                handle = _observe_handle(transport, request, statement, deadline)
                work_sql = external_work_batch(token, handle)
                if handle.upper() in witnessed_handles:
                    raise ValueError("measurement routes share a SQL handle")
                witnessed_handles.add(handle.upper())
                if observe_driver is not None:
                    try:
                        current_driver = observe_driver(request.finished, deadline)
                    except UnconfirmedRequestCleanup:
                        raise
                    except (OSError, ValueError):
                        driver_unconfirmed = True
                    else:
                        if driver is not None and driver != current_driver:
                            driver_unconfirmed = True
                        driver = current_driver
                verify_aggregate(request.result(deadline))
                _check_deadline(deadline)
                records.append(_read_completed_work(transport, work_sql, deadline))
        stage = "comparison"
        _check_deadline(deadline)
        filters = verify_pushdown(token, records[0], records[1])
        if driver_unconfirmed:
            return MeasurementResult("NOT_PROVEN", "driver_unconfirmed", filters)
        return MeasurementResult("PASS", stage, filters, driver)
    except UnconfirmedRequestCleanup:
        return MeasurementResult("FAIL_CLEANUP", stage)
    except (OSError, ValueError):
        return MeasurementResult("NOT_PROVEN", stage)


def _observe_handle(
    transport: MeasurementTransport,
    request: PendingAggregate,
    statement: str,
    deadline: float,
) -> str:
    while not request.finished():
        _check_deadline(deadline)
        handles = transport.active_handles(statement, deadline)
        if len(handles) > 1:
            raise ValueError("live request identity is ambiguous")
        if handles:
            return handles[0]
        sleep(max(0, min(0.025, deadline - monotonic())))
    raise ValueError("measurement request was never witnessed active")


def _read_completed_work(transport: MeasurementTransport, sql: str, deadline: float) -> tuple[Work, ...]:
    # A completed Reader can precede publication of the distributed terminal state.
    settle = min(deadline, monotonic() + 5)
    records = transport.external_work(sql, deadline)
    while len(records) == 1 and records[0].request_status in {
        "Pending", "Authorizing", "AcquireSystemResources", "Initializing",
        "Plan", "Parsing", "AcquireResources", "Running",
    }:
        remaining = settle - monotonic()
        if remaining <= 0:
            break
        sleep(min(0.05, remaining))
        _check_deadline(deadline)
        records = transport.external_work(sql, deadline)
    return records


def _check_deadline(deadline: float) -> None:
    if not isfinite(deadline) or monotonic() >= deadline:
        raise TimeoutError("measurement deadline exceeded")
