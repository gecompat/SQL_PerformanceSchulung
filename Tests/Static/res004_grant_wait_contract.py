"""Offline checker for caller-supplied RES-004 grant-wait evidence.

This validates only scalar bindings from one supplied snapshot. It does not
collect or authenticate SQL Server requests, grants, waits, or memory pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


_RFC3339 = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z"
)


class Verdict(str, Enum):
    PASS = "PASS"
    NOT_PROVEN = "NOT_PROVEN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class RequestWait:
    session_id: int
    request_id: int
    wait_type: str
    wait_ms: int
    captured_at: str


@dataclass(frozen=True)
class Grant:
    session_id: int
    request_id: int
    grant_time: str | None
    wait_time_ms: int | None
    requested_memory_kb: int
    granted_memory_kb: int | None
    pool_id: int
    resource_semaphore_id: int
    captured_at: str


@dataclass(frozen=True)
class SemaphoreSnapshot:
    pool_id: int
    resource_semaphore_id: int
    grantee_count: int
    waiter_count: int
    captured_at: str


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    reasons: tuple[str, ...]


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _valid_timestamp(value: object) -> bool:
    if type(value) is not str or not _RFC3339.fullmatch(value):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None
    except ValueError:
        return False


def evaluate_grant_wait(
    request: RequestWait | None,
    grants: tuple[Grant, ...] | None,
    semaphore: SemaphoreSnapshot | None,
) -> Result:
    """Bind a live wait, grant rows, and positive counts to one pool/semaphore snapshot."""
    if request is None or grants is None or semaphore is None:
        return Result(Verdict.NOT_PROVEN, ("request, grant, or semaphore snapshot is missing",))
    if type(request) is not RequestWait:
        return Result(Verdict.FAIL, ("request must use the exact RequestWait record",))
    if type(grants) is not tuple or any(type(grant) is not Grant for grant in grants):
        return Result(Verdict.FAIL, ("grants must be a tuple of exact Grant records",))
    if type(semaphore) is not SemaphoreSnapshot:
        return Result(Verdict.FAIL, ("semaphore must use the exact SemaphoreSnapshot record",))
    if (
        not _positive_int(request.session_id)
        or not _nonnegative_int(request.request_id)
        or type(request.wait_type) is not str
        or request.wait_type != "RESOURCE_SEMAPHORE"
        or not _positive_int(request.wait_ms)
        or not _valid_timestamp(request.captured_at)
    ):
        return Result(Verdict.FAIL, ("request wait record is invalid or is not RESOURCE_SEMAPHORE",))
    if not grants:
        return Result(Verdict.NOT_PROVEN, ("no memory grant rows were supplied",))

    if (
        not _positive_int(semaphore.pool_id)
        or not _nonnegative_int(semaphore.resource_semaphore_id)
        or not _nonnegative_int(semaphore.grantee_count)
        or not _nonnegative_int(semaphore.waiter_count)
        or not _valid_timestamp(semaphore.captured_at)
    ):
        return Result(Verdict.FAIL, ("resource semaphore snapshot contains invalid scalar values",))
    if semaphore.captured_at != request.captured_at:
        return Result(Verdict.FAIL, ("request and semaphore rows do not share one capture timestamp",))
    if semaphore.grantee_count <= 0 or semaphore.waiter_count <= 0:
        return Result(Verdict.NOT_PROVEN, ("resource semaphore counts do not show both grantees and waiters",))

    for grant in grants:
        if (
            not _positive_int(grant.session_id)
            or not _nonnegative_int(grant.request_id)
            or (grant.grant_time is not None and (type(grant.grant_time) is not str or not grant.grant_time))
            or (grant.wait_time_ms is not None and not _nonnegative_int(grant.wait_time_ms))
            or not _positive_int(grant.requested_memory_kb)
            or (grant.granted_memory_kb is not None and not _nonnegative_int(grant.granted_memory_kb))
            or not _positive_int(grant.pool_id)
            or not _nonnegative_int(grant.resource_semaphore_id)
            or not _valid_timestamp(grant.captured_at)
        ):
            return Result(Verdict.FAIL, ("memory grant row contains invalid scalar values",))
        if ((grant.grant_time is None and grant.granted_memory_kb not in (None, 0))
                or (grant.grant_time is not None and not _positive_int(grant.granted_memory_kb))):
            return Result(Verdict.FAIL, ("grant_time and granted memory amount contradict each other",))
        if grant.captured_at != request.captured_at:
            return Result(Verdict.FAIL, ("request and grant rows do not share one capture timestamp",))

    matching = tuple(
        grant for grant in grants
        if (grant.session_id, grant.request_id) == (request.session_id, request.request_id)
    )
    if len(matching) != 1:
        return Result(Verdict.FAIL, ("request must bind to exactly one grant row by session and request ID",))
    waiting = matching[0]
    if (semaphore.pool_id, semaphore.resource_semaphore_id) != (
        waiting.pool_id, waiting.resource_semaphore_id
    ):
        return Result(Verdict.FAIL, ("resource semaphore does not match the waiting request grant",))
    if waiting.grant_time is not None or waiting.granted_memory_kb not in (None, 0):
        return Result(Verdict.FAIL, ("matching request is already granted",))
    if waiting.wait_time_ms is None or waiting.wait_time_ms <= 0:
        return Result(Verdict.NOT_PROVEN, ("matching grant row lacks a positive wait duration",))
    concurrent = tuple(
        grant for grant in grants
        if (grant.session_id, grant.request_id) != (request.session_id, request.request_id)
        and grant.grant_time is not None
        and grant.granted_memory_kb > 0
        and (grant.pool_id, grant.resource_semaphore_id)
        == (waiting.pool_id, waiting.resource_semaphore_id)
    )
    if not concurrent:
        return Result(Verdict.NOT_PROVEN, ("no granted request in the same pool and semaphore was supplied",))
    return Result(Verdict.PASS, ())
