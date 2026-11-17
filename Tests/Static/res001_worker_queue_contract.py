"""Offline checker for caller-supplied RES-001 worker-queue evidence.

It checks only scalar bindings in one supplied capture window; it neither
collects nor authenticates SQL Server requests, scheduler queues, or exhaustion.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import re


_RFC3339 = re.compile(
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"(?:\.(\d{1,7}))?(Z|[+-]\d{2}:\d{2})\Z"
)
MAX_VISIBLE_SCHEDULER_ID = 254


class Verdict(str, Enum):
    PASS = "PASS"
    NOT_PROVEN = "NOT_PROVEN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class WorkerWait:
    expected_run_token: str
    observed_run_token: str
    session_id: int
    request_id: int
    wait_type: str
    wait_ms: int
    captured_at: str


@dataclass(frozen=True)
class SchedulerSample:
    scheduler_id: int
    work_queue_count: int
    runnable_tasks_count: int
    captured_at: str


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    reasons: tuple[str, ...]
    worker_queue_visible: bool
    cpu_runnable_visible: bool


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _timestamp(value: object) -> tuple[datetime, Decimal] | None:
    if type(value) is not str:
        return None
    match = _RFC3339.fullmatch(value)
    if match is None:
        return None
    base, fraction, offset = match.groups()
    try:
        parsed = datetime.fromisoformat(base + ("+00:00" if offset == "Z" else offset))
        fractional_second = Decimal("0." + fraction) if fraction is not None else Decimal(0)
        if parsed.utcoffset() is None:
            return None
        instant = parsed.astimezone(timezone.utc)
    except (ValueError, InvalidOperation, OverflowError):
        return None
    return instant, fractional_second


def _valid_timestamp(value: object) -> bool:
    return _timestamp(value) is not None


def evaluate_worker_queue(
    wait: WorkerWait | None,
    samples: tuple[SchedulerSample, ...] | None,
    run_started_at: str | None,
    run_finished_at: str | None,
) -> Result:
    """Bind an owned THREADPOOL request to same-time scheduler queue evidence."""
    if wait is None or samples is None or run_started_at is None or run_finished_at is None:
        return Result(Verdict.NOT_PROVEN, ("wait, scheduler samples, or run window is missing",), False, False)
    if type(wait) is not WorkerWait:
        return Result(Verdict.FAIL, ("wait must use the exact WorkerWait record",), False, False)
    if type(samples) is not tuple or any(type(sample) is not SchedulerSample for sample in samples):
        return Result(Verdict.FAIL, ("samples must be a tuple of exact SchedulerSample records",), False, False)
    if not samples:
        return Result(Verdict.NOT_PROVEN, ("no scheduler samples were supplied",), False, False)
    if (
        type(wait.expected_run_token) is not str or not wait.expected_run_token.strip()
        or type(wait.observed_run_token) is not str or not wait.observed_run_token.strip()
        or wait.observed_run_token != wait.expected_run_token
        or not _positive_int(wait.session_id)
        or not _nonnegative_int(wait.request_id)
        or type(wait.wait_type) is not str or wait.wait_type != "THREADPOOL"
        or not _positive_int(wait.wait_ms)
        or not _valid_timestamp(wait.captured_at)
        or not _valid_timestamp(run_started_at)
        or not _valid_timestamp(run_finished_at)
    ):
        return Result(Verdict.FAIL, ("worker wait identity, type, duration, or timestamp is invalid",), False, False)

    captured = _timestamp(wait.captured_at)
    started = _timestamp(run_started_at)
    finished = _timestamp(run_finished_at)
    if captured is None or started is None or finished is None:
        return Result(Verdict.FAIL, ("run window timestamp is invalid",), False, False)
    if started >= finished or not started <= captured <= finished:
        return Result(Verdict.FAIL, ("THREADPOOL capture lies outside the ordered run window",), False, False)

    scheduler_ids: set[int] = set()
    for sample in samples:
        if (
            not _nonnegative_int(sample.scheduler_id)
            or sample.scheduler_id > MAX_VISIBLE_SCHEDULER_ID
            or not _nonnegative_int(sample.work_queue_count)
            or not _nonnegative_int(sample.runnable_tasks_count)
            or not _valid_timestamp(sample.captured_at)
        ):
            return Result(Verdict.FAIL, ("scheduler sample contains invalid scalar values",), False, False)
        if sample.scheduler_id in scheduler_ids:
            return Result(Verdict.FAIL, ("scheduler IDs must be unique in a capture",), False, False)
        scheduler_ids.add(sample.scheduler_id)
        if sample.captured_at != wait.captured_at:
            return Result(Verdict.FAIL, ("wait and scheduler samples do not share one capture timestamp",), False, False)

    worker_queue = any(sample.work_queue_count > 0 for sample in samples)
    cpu_runnable = any(sample.runnable_tasks_count > 0 for sample in samples)
    if not worker_queue:
        return Result(
            Verdict.NOT_PROVEN,
            ("no pending scheduler worker queue accompanies the supplied THREADPOOL wait",),
            False,
            cpu_runnable,
        )
    return Result(Verdict.PASS, (), True, cpu_runnable)
