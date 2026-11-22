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
    request_id: int | None = None
    exec_context_id: int | None = None


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
    partition_id: int | None = None


@dataclass(frozen=True)
class PageLink:
    """Caller-supplied page header and neighbor pointers for one leaf page."""

    database_id: int
    file_id: int
    page_id: int
    object_id: int
    index_id: int
    partition_id: int
    page_level: int
    previous_address: tuple[int, int] | None
    next_address: tuple[int, int] | None


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    reasons: tuple[str, ...]


MAX_PAGE_CHAIN_RECORDS = 4096


def evaluate_rightmost_page_chain(
    pages: tuple[PageLink, ...] | None,
    *,
    database_id: int,
    object_id: int,
    index_id: int,
    partition_id: int,
    start_address: tuple[int, int],
    terminal_address: tuple[int, int] | None,
    max_pages: int,
) -> Result:
    """Check a supplied bounded forward chain without assuming terminal encoding.

    The caller must provide an explicit terminal address. This function checks
    only consistency of those values; it neither authenticates nor reads pages.
    """
    if pages is None or terminal_address is None:
        return Result(Verdict.NOT_PROVEN, ("page-chain records or explicit terminal marker are missing",))
    expected = (database_id, object_id, index_id, partition_id)
    if any(not _positive_int(value) for value in expected):
        return Result(Verdict.FAIL, ("expected page-chain identity is invalid",))
    if not _valid_page_address(start_address) or not _valid_page_address(terminal_address):
        return Result(Verdict.FAIL, ("start or terminal page address is invalid",))
    if type(max_pages) is not int or not 1 <= max_pages <= MAX_PAGE_CHAIN_RECORDS:
        return Result(Verdict.FAIL, ("page-chain cap is outside the fixed bound",))
    if type(pages) is not tuple or any(type(page) is not PageLink for page in pages):
        return Result(Verdict.FAIL, ("page-chain input must be a tuple of exact PageLink records",))
    if not pages:
        return Result(Verdict.NOT_PROVEN, ("page-chain records are empty",))
    if len(pages) > max_pages:
        return Result(Verdict.NOT_PROVEN, ("page-chain record cap was exceeded",))

    seen: set[tuple[int, int]] = set()
    addresses: list[tuple[int, int]] = []
    for page in pages:
        if (not _positive_int(page.database_id) or not _positive_int(page.object_id)
                or not _positive_int(page.index_id) or not _positive_int(page.partition_id)
                or not _positive_int(page.file_id) or not _positive_int(page.page_id)
                or type(page.page_level) is not int or page.page_level < 0
                or not _valid_optional_page_address(page.previous_address)
                or not _valid_optional_page_address(page.next_address)):
            return Result(Verdict.FAIL, ("page-chain record contains invalid identity, level, or link fields",))
        if (page.database_id, page.object_id, page.index_id, page.partition_id) != expected:
            return Result(Verdict.FAIL, ("page-chain record differs from the expected database/object/index/partition",))
        if page.page_level != 0:
            return Result(Verdict.FAIL, ("page-chain record is not a leaf page",))
        address = (page.file_id, page.page_id)
        if address in seen:
            return Result(Verdict.FAIL, ("page-chain contains a cycle or duplicate page",))
        seen.add(address)
        addresses.append(address)

    if addresses[0] != start_address:
        return Result(Verdict.FAIL, ("page-chain does not begin at the supplied wait page",))
    for index, page in enumerate(pages[:-1]):
        next_page = pages[index + 1]
        current_address = addresses[index]
        next_address = addresses[index + 1]
        if page.next_address != next_address or next_page.previous_address != current_address:
            return Result(Verdict.FAIL, ("forward and backward page links are inconsistent",))
    final_next = pages[-1].next_address
    if final_next in seen:
        return Result(Verdict.FAIL, ("terminal link loops to a previously visited page",))
    if final_next == terminal_address:
        return Result(Verdict.PASS, ())
    return Result(Verdict.NOT_PROVEN, ("supplied chain does not reach the explicit terminal marker",))


def _valid_page_address(value: object) -> bool:
    return (type(value) is tuple and len(value) == 2
            and all(_positive_int(part) for part in value))


def _valid_optional_page_address(value: object) -> bool:
    return value is None or _valid_page_address(value)


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _capture_instant(value: object) -> tuple[datetime, Decimal] | None:
    if type(value) is not str or len(value) > 128:
        return None
    match = _RFC3339.fullmatch(value)
    if match is None:
        return None
    base, fraction, offset = match.groups()
    # RFC 3339 -00:00 means the local offset is unknown, not known UTC.
    if offset == "-00:00":
        return None
    try:
        parsed = datetime.fromisoformat(base + ("+00:00" if offset == "Z" else offset))
        fractional_second = Decimal("0." + fraction) if fraction is not None else Decimal(0)
    except (ValueError, InvalidOperation):
        return None
    if parsed.utcoffset() is None:
        return None
    try:
        normalized = parsed.astimezone(timezone.utc)
    except OverflowError:
        return None
    return normalized, fractional_second


def evaluate_last_page_contention(
    waits: tuple[PageWait, ...] | None,
    target: PageTarget | None,
    *,
    expected_actor_requests: tuple[tuple[str, int, int], ...] | None,
    page_chain: tuple[PageLink, ...] | None = None,
    terminal_address: tuple[int, int] | None = None,
    max_pages: int | None = None,
) -> Result:
    """Require page waits bound to two expected actor requests and distinct tasks."""
    if waits is None or target is None:
        return Result(Verdict.NOT_PROVEN, ("wait snapshot or target page evidence is missing",))
    if expected_actor_requests is None:
        return Result(Verdict.NOT_PROVEN, ("expected actor request bindings are missing",))
    if (type(expected_actor_requests) is not tuple or len(expected_actor_requests) != 2
            or any(type(item) is not tuple or len(item) != 3 for item in expected_actor_requests)):
        return Result(Verdict.FAIL, ("exactly two actor/request bindings are required",))
    expected_roles = [item[0] for item in expected_actor_requests]
    expected_sessions = [item[1] for item in expected_actor_requests]
    expected_requests = [item[2] for item in expected_actor_requests]
    if (any(type(role) is not str for role in expected_roles)
            or set(expected_roles) != {"ACTOR_A", "ACTOR_B"}
            or len(set(expected_roles)) != 2
            or any(type(session_id) is not int or session_id <= 0 for session_id in expected_sessions)
            or len(set(expected_sessions)) != 2
            or any(type(request_id) is not int or request_id < 0 for request_id in expected_requests)):
        return Result(Verdict.FAIL, ("actor/request bindings are invalid",))
    expected_by_session = dict((session_id, request_id)
                               for _, session_id, request_id in expected_actor_requests)
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
        or type(wait.request_id) is not int
        or wait.request_id < 0
        or type(wait.exec_context_id) is not int
        or wait.exec_context_id < 0
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
    if any(expected_by_session.get(wait.session_id) != wait.request_id for wait in latches):
        return Result(Verdict.FAIL, ("PAGELATCH_EX waits differ from the expected actor requests",))
    observed_requests = {(wait.session_id, wait.request_id) for wait in latches}
    expected_pairs = set(expected_by_session.items())
    if observed_requests != expected_pairs:
        return Result(Verdict.NOT_PROVEN, ("both expected actor requests must be observed waiting",))
    observed_tasks = [(wait.session_id, wait.request_id, wait.exec_context_id) for wait in latches]
    if len(set(observed_tasks)) != len(observed_tasks):
        return Result(Verdict.FAIL, ("PAGELATCH_EX task records must be unique",))
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
    if not _positive_int(target.partition_id):
        return Result(Verdict.NOT_PROVEN, ("target page partition binding is absent",))
    chain_result = evaluate_rightmost_page_chain(
        page_chain,
        database_id=target.database_id,
        object_id=target.object_id,
        index_id=target.index_id,
        partition_id=target.partition_id,
        start_address=(target.file_id, target.page_id),
        terminal_address=terminal_address,
        max_pages=max_pages,
    )
    if chain_result.verdict is not Verdict.PASS:
        return chain_result
    return Result(Verdict.PASS, ())
