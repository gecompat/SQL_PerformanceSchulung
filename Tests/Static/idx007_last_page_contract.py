"""Offline checker for caller-supplied IDX-007 last-page latch evidence.

The checker validates scalar consistency only. It does not collect, authenticate,
or attest to SQL Server waits, page metadata, or page-chain observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import re


_RFC3339 = re.compile(
    r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?:\.([0-9]+))?(Z|[+-][0-9]{2}:[0-9]{2})\Z"
)


class Verdict(str, Enum):
    PASS = "PASS"
    NOT_PROVEN = "NOT_PROVEN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class PageWait:
    wait_type: str
    session_id: int
    database_id: int
    file_id: int
    page_id: int
    wait_ms: int
    captured_at: str


@dataclass(frozen=True)
class PageTarget:
    database_id: int
    file_id: int
    page_id: int
    object_id: int
    index_id: int
    page_level: int
    rightmost_leaf: bool | None
    captured_at: str


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    reasons: tuple[str, ...]


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _capture_instant(value: object) -> tuple[datetime, Decimal] | None:
    if type(value) is not str or len(value) > 128:
        return None
    match = _RFC3339.fullmatch(value)
    if match is None:
        return None
    base, fraction, offset = match.groups()
    try:
        parsed = datetime.fromisoformat(base + ("+00:00" if offset == "Z" else offset))
        fractional_second = Decimal("0." + fraction) if fraction is not None else Decimal(0)
    except (ValueError, InvalidOperation):
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc), fractional_second


def evaluate_last_page_contention(
    waits: tuple[PageWait, ...] | None,
    target: PageTarget | None,
) -> Result:
    """Require matching PAGELATCH_EX waits by distinct sessions on a supplied leaf page."""
    if waits is None or target is None:
        return Result(Verdict.NOT_PROVEN, ("wait snapshot or target page evidence is missing",))
    if type(waits) is not tuple or any(type(wait) is not PageWait for wait in waits):
        return Result(Verdict.FAIL, ("waits must be a tuple of exact PageWait records",))
    if type(target) is not PageTarget:
        return Result(Verdict.FAIL, ("target must be an exact PageTarget record",))

    fields = (target.database_id, target.file_id, target.page_id, target.object_id, target.index_id)
    if any(not _positive_int(value) for value in fields) or type(target.page_level) is not int or target.page_level < 0:
        return Result(Verdict.FAIL, ("target page identity or level is invalid",))
    target_instant = _capture_instant(target.captured_at)
    if target_instant is None:
        return Result(Verdict.FAIL, ("target capture timestamp is invalid",))
    if target.rightmost_leaf is not None and type(target.rightmost_leaf) is not bool:
        return Result(Verdict.FAIL, ("rightmost-leaf assertion must be boolean or missing",))

    if not waits:
        return Result(Verdict.NOT_PROVEN, ("no waits were supplied",))
    if any(
        type(wait.wait_type) is not str
        or _capture_instant(wait.captured_at) is None
        or not _positive_int(wait.session_id)
        or not _positive_int(wait.database_id)
        or not _positive_int(wait.file_id)
        or not _positive_int(wait.page_id)
        or type(wait.wait_ms) is not int
        or wait.wait_ms <= 0
        for wait in waits
    ):
        return Result(Verdict.FAIL, ("wait record contains invalid scalar values",))

    latches = tuple(wait for wait in waits if wait.wait_type == "PAGELATCH_EX")
    if not latches:
        return Result(Verdict.NOT_PROVEN, ("no PAGELATCH_EX waits were supplied",))
    if any(_capture_instant(wait.captured_at) != target_instant for wait in latches):
        return Result(Verdict.FAIL, ("waits and target page do not share one capture timestamp",))
    if any(
        (wait.database_id, wait.file_id, wait.page_id)
        != (target.database_id, target.file_id, target.page_id)
        for wait in latches
    ):
        return Result(Verdict.FAIL, ("PAGELATCH_EX waits do not resolve to the supplied target page",))
    sessions = {wait.session_id for wait in latches}
    if len(sessions) < 2:
        return Result(Verdict.NOT_PROVEN, ("fewer than two distinct waiting sessions were supplied",))
    if target.page_level != 0:
        return Result(Verdict.FAIL, ("target page is not declared as a leaf page",))
    if target.rightmost_leaf is False:
        return Result(Verdict.FAIL, ("target page is explicitly not the rightmost leaf",))
    if target.rightmost_leaf is None:
        return Result(Verdict.NOT_PROVEN, ("rightmost-leaf page-chain evidence is absent",))
    return Result(Verdict.PASS, ())
