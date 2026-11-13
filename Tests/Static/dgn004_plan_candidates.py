"""Bound and compare complete DGN-004 plan-cache candidate snapshots.

The SQL source and its outputs remain evidence supplied by the local runner.
This module validates that evidence and binds a unique execution delta; it does
not authenticate SQL Server, assign an invocation ID, or create runtime proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import re

from dgn004_identity_snapshot import registered_text_views
from dgn004_plan_frame import is_valid_run_token


MAX_FRAME_BYTES = 2 * 1024 * 1024
MAX_CANDIDATE_ROWS = 4096
MAX_MODULE_BYTES = 16 * 1024
_HEX_HANDLE = re.compile(r"\A(?:[0-9A-Fa-f]{2}){1,64}\Z")
_HEX_16 = re.compile(r"\A[0-9A-Fa-f]{16}\Z")
_HEX_64 = re.compile(r"\A[0-9A-Fa-f]{64}\Z")
_INTEGER = re.compile(r"\A(?:0|[1-9][0-9]*)\Z")
_SIGNED_INTEGER = re.compile(r"\A(?:-1|0|[1-9][0-9]*)\Z")
_TIMESTAMP = re.compile(r"\A[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}\Z")


class PlanCandidateError(ValueError):
    """Reject malformed, incomplete, ambiguous, or unrelated cache evidence."""


@dataclass(frozen=True)
class PlanCandidateInput:
    run: str
    role: str
    call: int
    database_id: int
    object_id: int


@dataclass(frozen=True)
class CacheCandidate:
    plan_handle: bytes
    sql_handle: bytes
    database_id: int
    object_id: int
    statement_start_offset: int
    statement_end_offset: int
    plan_generation_num: int
    creation_time: datetime
    last_execution_time: datetime
    execution_count: int
    query_hash: bytes
    query_plan_hash: bytes
    module_byte_count: int
    module_sha256: bytes

    @property
    def row_key(self) -> tuple[bytes, bytes, int, int, int, datetime]:
        return (
            self.plan_handle,
            self.sql_handle,
            self.statement_start_offset,
            self.statement_end_offset,
            self.plan_generation_num,
            self.creation_time,
        )


@dataclass(frozen=True)
class CandidateSnapshot:
    run: str
    role: str
    call: int
    database_id: int
    object_id: int
    module_byte_count: int
    module_sha256: bytes
    rows: tuple[CacheCandidate, ...]


@dataclass(frozen=True)
class BoundPlanHandle:
    """One candidate with a unique execution delta; not an authenticated receipt."""

    run: str
    role: str
    call: int
    candidate: CacheCandidate

    @property
    def plan_handle_hex(self) -> str:
        return self.candidate.plan_handle.hex().upper()


def _parse_int(value: str, label: str, *, signed: bool = False) -> int:
    pattern = _SIGNED_INTEGER if signed else _INTEGER
    if type(value) is not str or not pattern.fullmatch(value):
        raise PlanCandidateError(f"invalid {label}")
    return int(value)


def _parse_hex(value: str, pattern: re.Pattern[str], label: str) -> bytes:
    if type(value) is not str or not pattern.fullmatch(value):
        raise PlanCandidateError(f"invalid {label}")
    return bytes.fromhex(value)


def _parse_timestamp(value: str, label: str) -> datetime:
    if type(value) is not str or not _TIMESTAMP.fullmatch(value):
        raise PlanCandidateError(f"invalid {label}")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise PlanCandidateError(f"invalid {label}") from exc
    if result.tzinfo is not None:
        raise PlanCandidateError(f"invalid {label}")
    return result


def validate_snapshot_input(value: PlanCandidateInput) -> None:
    if type(value) is not PlanCandidateInput:
        raise PlanCandidateError("exact plan candidate input required")
    if type(value.run) is not str or not is_valid_run_token(value.run):
        raise PlanCandidateError("invalid run token")
    if type(value.role) is not str or value.role not in ("R", "H"):
        raise PlanCandidateError("invalid role")
    if type(value.call) is not int or not 1 <= value.call <= 9:
        raise PlanCandidateError("invalid call")
    if type(value.database_id) is not int or not 1 <= value.database_id <= 32767:
        raise PlanCandidateError("invalid database ID")
    if type(value.object_id) is not int or value.object_id <= 0:
        raise PlanCandidateError("invalid object ID")


def parse_candidate_snapshot(
    frame: str,
    *,
    expected: PlanCandidateInput,
) -> CandidateSnapshot:
    """Parse one complete bounded ASCII frame against registered module bytes."""
    validate_snapshot_input(expected)
    if type(frame) is not str:
        raise PlanCandidateError("snapshot frame must be text")
    try:
        frame_bytes = frame.encode("ascii", errors="strict")
    except UnicodeEncodeError as exc:
        raise PlanCandidateError("snapshot frame is not ASCII") from exc
    if not frame_bytes or len(frame_bytes) > MAX_FRAME_BYTES:
        raise PlanCandidateError("snapshot frame is empty or exceeds its byte limit")
    normalized = frame.replace("\r\n", "\n")
    if "\r" in normalized or not normalized.endswith("\n"):
        raise PlanCandidateError("snapshot frame line endings are incomplete")
    lines = normalized[:-1].split("\n")
    if any(not line for line in lines):
        raise PlanCandidateError("snapshot frame contains an empty record")

    views = registered_text_views()[expected.role]
    module_bytes = views.module_text.encode("utf-16le", errors="strict")
    if len(module_bytes) > MAX_MODULE_BYTES:
        raise PlanCandidateError("registered module exceeds its byte limit")
    module_digest = hashlib.sha256(module_bytes).digest()
    if len(lines) < 2:
        raise PlanCandidateError("snapshot frame is incomplete")

    start = lines[0].split("|")
    end = lines[-1].split("|")
    if len(start) != 7 or len(end) != 7 or start[0] != "DGN004_CACHE_START" or end[0] != "DGN004_CACHE_END":
        raise PlanCandidateError("snapshot start/end records are invalid")
    expected_binding = [expected.run, expected.role, str(expected.call)]
    if start[1:4] != expected_binding or end[1:4] != expected_binding:
        raise PlanCandidateError("snapshot does not match the expected run/role/call")
    row_count = _parse_int(start[4], "row count")
    module_byte_count = _parse_int(start[5], "module byte count")
    frame_module_digest = _parse_hex(start[6], _HEX_64, "module SHA-256")
    if end[4:] != start[4:]:
        raise PlanCandidateError("snapshot start/end records disagree")
    if row_count > MAX_CANDIDATE_ROWS or len(lines) != row_count + 2:
        raise PlanCandidateError("snapshot row count is incomplete or exceeds its limit")
    if (module_byte_count != len(module_bytes) or frame_module_digest != module_digest
            or module_byte_count % 2):
        raise PlanCandidateError("snapshot module binding differs from registered source bytes")

    expected_end_offsets = {
        views.statement_start_offset + views.statement_bytes - 2,
        views.statement_start_offset + len(views.statement_without_terminator.encode("utf-16le")) - 2,
    }
    candidates: list[CacheCandidate] = []
    seen: set[tuple[bytes, bytes, int, int, int, datetime]] = set()
    for line in lines[1:-1]:
        fields = line.split("|")
        if len(fields) != 15 or fields[0] != "DGN004_CACHE_ROW":
            raise PlanCandidateError("snapshot candidate record is malformed")
        row = CacheCandidate(
            plan_handle=_parse_hex(fields[1], _HEX_HANDLE, "plan handle"),
            sql_handle=_parse_hex(fields[2], _HEX_HANDLE, "SQL handle"),
            database_id=_parse_int(fields[3], "database ID"),
            object_id=_parse_int(fields[4], "object ID"),
            statement_start_offset=_parse_int(fields[5], "statement start offset"),
            statement_end_offset=_parse_int(fields[6], "statement end offset", signed=True),
            plan_generation_num=_parse_int(fields[7], "plan generation"),
            creation_time=_parse_timestamp(fields[8], "creation time"),
            last_execution_time=_parse_timestamp(fields[9], "last execution time"),
            execution_count=_parse_int(fields[10], "execution count"),
            query_hash=_parse_hex(fields[11], _HEX_16, "query hash"),
            query_plan_hash=_parse_hex(fields[12], _HEX_16, "query plan hash"),
            module_byte_count=_parse_int(fields[13], "row module byte count"),
            module_sha256=_parse_hex(fields[14], _HEX_64, "row module SHA-256"),
        )
        if (row.database_id != expected.database_id or row.object_id != expected.object_id
                or row.statement_start_offset != views.statement_start_offset
                or row.statement_end_offset not in expected_end_offsets
                or row.module_byte_count != module_byte_count
                or row.module_sha256 != frame_module_digest
                or row.plan_generation_num < 0 or row.execution_count < 1
                or row.last_execution_time < row.creation_time):
            raise PlanCandidateError("candidate row differs from its registered module binding")
        if row.row_key in seen:
            raise PlanCandidateError("snapshot contains a duplicate composite row key")
        seen.add(row.row_key)
        candidates.append(row)

    return CandidateSnapshot(
        run=expected.run,
        role=expected.role,
        call=expected.call,
        database_id=expected.database_id,
        object_id=expected.object_id,
        module_byte_count=module_byte_count,
        module_sha256=module_digest,
        rows=tuple(candidates),
    )


def bind_unique_execution(
    before: CandidateSnapshot,
    after: CandidateSnapshot,
) -> BoundPlanHandle:
    """Bind one exact execution-count delta; reject eviction or ambiguity."""
    if type(before) is not CandidateSnapshot or type(after) is not CandidateSnapshot:
        raise PlanCandidateError("exact before/after snapshots required")
    if (before.run, before.role, before.call, before.database_id, before.object_id,
            before.module_byte_count, before.module_sha256) != (
            after.run, after.role, after.call, after.database_id, after.object_id,
            after.module_byte_count, after.module_sha256):
        raise PlanCandidateError("before/after snapshot bindings differ")

    old = {row.row_key: row for row in before.rows}
    new = {row.row_key: row for row in after.rows}
    if set(old) - set(new):
        raise PlanCandidateError("a prior candidate disappeared between snapshots")

    changed: list[CacheCandidate] = []
    for key, row in new.items():
        previous = old.get(key)
        if previous is None:
            if row.execution_count != 1:
                raise PlanCandidateError("new candidate has an unexpected execution count")
            changed.append(row)
            continue
        if row == previous:
            continue
        if (row.execution_count != previous.execution_count + 1
                or row.last_execution_time < previous.last_execution_time
                or row.query_hash != previous.query_hash
                or row.query_plan_hash != previous.query_plan_hash
                or row.database_id != previous.database_id
                or row.object_id != previous.object_id
                or row.module_byte_count != previous.module_byte_count
                or row.module_sha256 != previous.module_sha256):
            raise PlanCandidateError("candidate changed outside one exact execution delta")
        changed.append(row)

    if len(changed) != 1:
        raise PlanCandidateError("snapshot delta does not identify exactly one plan candidate")
    selected = changed[0]
    return BoundPlanHandle(before.run, before.role, before.call, selected)
