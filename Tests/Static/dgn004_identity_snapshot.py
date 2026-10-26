"""Offline consistency checks for caller-supplied DGN-004 identity rows.

This module does not query SQL Server, choose server candidates, or establish
that supplied values came from the current execution. Its output is not a
bound identity receipt and cannot be passed to the capture runner.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from collections.abc import Iterable


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ai" / "identity" / "registry.json"
PAIR_DIRECTORY = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair"
MAX_SOURCE_UTF16_BYTES = 16 * 1024
ROLES = ("R", "H")
EXPECTED_MODULES = {
    "R": ("dgn004", "ReplayReference", "ReplayReference.sql"),
    "H": ("dgn004", "ReplayHintControl", "ReplayHintControl.sql"),
}
MODULE_ORIGIN = "sys.objects+sys.schemas+sys.sql_modules"
CACHE_ORIGIN = "sys.dm_exec_query_stats+sys.dm_exec_sql_text"
QUERY_STORE_ORIGIN = "sys.query_store_query+sys.query_store_query_text"


class IdentitySnapshotError(ValueError):
    """Reject inconsistent caller-supplied identity values."""


@dataclass(frozen=True)
class RegisteredTextViews:
    """Finite M/S/T text forms copied from the active registry source."""

    role: str
    module_name: tuple[str, str]
    module_text: str
    statement_text: str
    statement_without_terminator: str
    statement_start_offset: int
    statement_bytes: int


@dataclass(frozen=True)
class ModuleRecord:
    """Caller-supplied module name, object ID, and definition snapshot."""

    origin: str
    database_id: int
    schema_name: str
    module_name: str
    object_id: int
    definition: str


@dataclass(frozen=True)
class CacheRecord:
    """Caller-supplied cache text and raw inclusive statement byte offsets."""

    origin: str
    database_id: int
    object_id: int
    batch_text: str
    statement_start_offset: int
    statement_end_offset: int


@dataclass(frozen=True)
class QueryStoreRecord:
    """Caller-supplied Query Store identity and text snapshot."""

    origin: str
    database_id: int
    object_id: int
    query_id: int
    query_text_id: int
    context_settings_id: int
    parameterization_type: int
    query_text: str


@dataclass(frozen=True)
class SuppliedIdentityCandidate:
    """One pre-grouped R or H record; grouping and origins remain caller claims."""

    role: str
    module: ModuleRecord
    cache: CacheRecord
    query_store: QueryStoreRecord


@dataclass(frozen=True)
class RecordConsistencySummary:
    """Offline consistency summary; deliberately contains no plan handle."""

    scope: str
    role: str
    object_id: int
    query_id: int
    query_text_id: int
    context_settings_id: int
    parameterization_type: int
    cache_statement_variant: str
    query_store_text_variant: str


def registered_text_views() -> dict[str, RegisteredTextViews]:
    """Load the exact bounded M/S/T values from the active registry and fixtures."""
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        candidates = registry["artifacts"]["TSK-016"]["candidates"]
        candidate = next(item for item in candidates if item.get("target") == "DGN-004")
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, StopIteration, TypeError) as exc:
        raise IdentitySnapshotError("active DGN-004 source registry is unavailable") from exc
    if candidate.get("active_plan") != "classical_forcing_hint_control_plan":
        raise IdentitySnapshotError("active DGN-004 plan identity changed")
    plan = candidate.get("rh_source_text_plan")
    if type(plan) is not dict or type(plan.get("module_sources")) is not list:
        raise IdentitySnapshotError("registered R/H module sources are unavailable")
    entries_list = plan["module_sources"]
    entries = {entry.get("role"): entry for entry in entries_list if type(entry) is dict}
    if len(entries_list) != len(ROLES) or set(entries) != set(ROLES):
        raise IdentitySnapshotError("registered R/H role set is not exact")

    result: dict[str, RegisteredTextViews] = {}
    for role in ROLES:
        entry = entries[role]
        schema_name, module_name, file_name = EXPECTED_MODULES[role]
        if entry.get("module_name") != f"[{schema_name}].[{module_name}]":
            raise IdentitySnapshotError(f"{role}: registered module role mapping changed")
        try:
            with (PAIR_DIRECTORY / file_name).open("rb") as source_file:
                source_bytes = source_file.read(MAX_SOURCE_UTF16_BYTES // 2 + 1)
            expected_source_text = entry["module_source"]
            if type(expected_source_text) is not str or len(expected_source_text) > MAX_SOURCE_UTF16_BYTES // 2:
                raise IdentitySnapshotError(f"{role}: registered M source exceeds the source limit")
            expected_source = expected_source_text.encode("ascii", errors="strict")
            module_text = source_bytes.decode("ascii", errors="strict")
            module_bytes = module_text.encode("utf-16le", errors="strict")
        except (OSError, UnicodeError, KeyError, AttributeError) as exc:
            raise IdentitySnapshotError(f"{role}: registered module source is unreadable") from exc
        if len(source_bytes) > MAX_SOURCE_UTF16_BYTES // 2:
            raise IdentitySnapshotError(f"{role}: fixture source exceeds the source limit")
        if source_bytes != expected_source:
            raise IdentitySnapshotError(f"{role}: fixture does not match the registered M source")
        if (len(module_bytes) != entry.get("module_utf16_bytes")
                or hashlib.sha256(module_bytes).hexdigest() != entry.get("module_sha256_utf16le")):
            raise IdentitySnapshotError(f"{role}: registered M byte binding is inconsistent")
        start = entry.get("statement_start_utf16_bytes")
        size = entry.get("statement_utf16_bytes")
        if (type(start) is not int or type(size) is not int or start < 0 or size < 2
                or start % 2 or size % 2 or start + size != len(module_bytes)):
            raise IdentitySnapshotError(f"{role}: registered M/S byte offsets are invalid")
        statement_bytes = module_bytes[start:start + size]
        if len(statement_bytes) != size:
            raise IdentitySnapshotError(f"{role}: registered S byte range is truncated")
        statement_text = statement_bytes.decode("utf-16le", errors="strict")
        if (len(statement_bytes) != entry.get("statement_utf16_bytes")
                or hashlib.sha256(statement_bytes).hexdigest() != entry.get("statement_sha256_utf16le")
                or not statement_text.endswith(";")):
            raise IdentitySnapshotError(f"{role}: registered S byte binding is inconsistent")
        without_terminator = statement_text[:-1]
        without_bytes = without_terminator.encode("utf-16le", errors="strict")
        if hashlib.sha256(without_bytes).hexdigest() != entry.get("without_terminator_sha256_utf16le"):
            raise IdentitySnapshotError(f"{role}: registered T byte binding is inconsistent")
        result[role] = RegisteredTextViews(
            role=role,
            module_name=(schema_name, module_name),
            module_text=module_text,
            statement_text=statement_text,
            statement_without_terminator=without_terminator,
            statement_start_offset=start,
            statement_bytes=size,
        )
    return result


def _bounded_utf16_bytes(value: str, label: str) -> bytes:
    if type(value) is not str or len(value) > MAX_SOURCE_UTF16_BYTES // 2:
        raise IdentitySnapshotError(f"{label}: text type or length is outside the source limit")
    try:
        encoded = value.encode("utf-16le", errors="strict")
    except UnicodeError as exc:
        raise IdentitySnapshotError(f"{label}: text cannot be encoded as strict UTF-16LE") from exc
    if len(encoded) > MAX_SOURCE_UTF16_BYTES:
        raise IdentitySnapshotError(f"{label}: UTF-16LE text exceeds the source limit")
    return encoded


def _require_positive_int(value: int, label: str) -> None:
    if type(value) is not int or value <= 0:
        raise IdentitySnapshotError(f"{label}: expected a positive exact integer")


def _cache_statement_variant(cache: CacheRecord, views: RegisteredTextViews) -> str:
    batch = _bounded_utf16_bytes(cache.batch_text, "cache batch")
    registered_module = _bounded_utf16_bytes(views.module_text, "registered M")
    if batch != registered_module:
        raise IdentitySnapshotError("cache batch text does not equal registered M")
    start = cache.statement_start_offset
    end = cache.statement_end_offset
    if (type(start) is not int or type(end) is not int or start % 2
            or (end != -1 and (end < 0 or end % 2))):
        raise IdentitySnapshotError("cache statement offsets must be exact integers on UTF-16 boundaries")
    if start != views.statement_start_offset:
        raise IdentitySnapshotError("cache statement start offset differs from registered M/S")
    if end == -1:
        variant = "S"
        observed = batch[start:]
        expected = _bounded_utf16_bytes(views.statement_text, "registered S")
        if observed != expected:
            raise IdentitySnapshotError("cache M-end sentinel does not yield registered S")
        return variant
    statement_bytes = _bounded_utf16_bytes(views.statement_text, "registered S")
    no_terminator_bytes = _bounded_utf16_bytes(views.statement_without_terminator, "registered T")
    allowed_ends = {
        start + len(statement_bytes) - 2: ("S", statement_bytes),
        start + len(no_terminator_bytes) - 2: ("T", no_terminator_bytes),
    }
    selected = allowed_ends.get(end)
    if selected is None:
        raise IdentitySnapshotError("cache statement end offset is outside registered S/T byte ranges")
    variant, expected = selected
    if batch[start:end + 2] != expected:
        raise IdentitySnapshotError("cache statement bytes differ from the registered offset slice")
    return variant


def check_supplied_record_consistency(
    records: Iterable[SuppliedIdentityCandidate], *, expected_database_id: int,
) -> tuple[RecordConsistencySummary, ...]:
    """Compare caller-supplied R/H records to finite M/S/T forms without binding them.

    The function rejects duplicate roles instead of selecting a row. It does
    not establish that the caller enumerated every server row, that origin
    labels are truthful, or that any value belongs to the current execution.
    """
    _require_positive_int(expected_database_id, "expected database_id")
    if type(records) not in (list, tuple) or len(records) != len(ROLES):
        raise IdentitySnapshotError("exactly one caller-supplied record per R/H role is required")
    by_role: dict[str, SuppliedIdentityCandidate] = {}
    for record in records:
        if type(record) is not SuppliedIdentityCandidate or type(record.role) is not str:
            raise IdentitySnapshotError("record must be an exact caller-supplied R/H candidate")
        if record.role not in ROLES or record.role in by_role:
            raise IdentitySnapshotError("duplicate or unknown caller-supplied role")
        by_role[record.role] = record
    if set(by_role) != set(ROLES):
        raise IdentitySnapshotError("caller-supplied records must contain exactly R and H")

    views_by_role = registered_text_views()
    summaries: list[RecordConsistencySummary] = []
    for role in ROLES:
        record = by_role[role]
        views = views_by_role[role]
        if type(record.module) is not ModuleRecord or type(record.cache) is not CacheRecord:
            raise IdentitySnapshotError(f"{role}: exact module and cache records are required")
        if type(record.query_store) is not QueryStoreRecord:
            raise IdentitySnapshotError(f"{role}: exact Query Store record is required")
        module, cache, query = record.module, record.cache, record.query_store
        if type(module.origin) is not str or module.origin != MODULE_ORIGIN:
            raise IdentitySnapshotError(f"{role}: module origin label is not the required source")
        if type(cache.origin) is not str or cache.origin != CACHE_ORIGIN:
            raise IdentitySnapshotError(f"{role}: cache origin label is not the required source")
        if type(query.origin) is not str or query.origin != QUERY_STORE_ORIGIN:
            raise IdentitySnapshotError(f"{role}: Query Store origin label is not the required source")
        if type(module.schema_name) is not str or type(module.module_name) is not str:
            raise IdentitySnapshotError(f"{role}: schema and module names must be exact strings")
        if (module.schema_name, module.module_name) != views.module_name:
            raise IdentitySnapshotError(f"{role}: module name does not match the registered role mapping")

        module_ids = (module.database_id, module.object_id)
        cache_ids = (cache.database_id, cache.object_id)
        query_ids = (query.database_id, query.object_id)
        for value, label in zip(module_ids, ("module database_id", "module object_id"), strict=True):
            _require_positive_int(value, f"{role}: {label}")
        for value, label in zip(cache_ids, ("cache database_id", "cache object_id"), strict=True):
            _require_positive_int(value, f"{role}: {label}")
        for value, label in zip(query_ids, ("Query Store database_id", "Query Store object_id"), strict=True):
            _require_positive_int(value, f"{role}: {label}")
        if (module.database_id != expected_database_id
                or cache.database_id != expected_database_id
                or query.database_id != expected_database_id):
            raise IdentitySnapshotError(f"{role}: supplied records do not share the expected database_id")
        if not (module.object_id == cache.object_id == query.object_id):
            raise IdentitySnapshotError(f"{role}: object_id differs across supplied module/cache/Query Store records")
        if _bounded_utf16_bytes(module.definition, f"{role} module definition") != _bounded_utf16_bytes(
            views.module_text, f"{role} registered M"
        ):
            raise IdentitySnapshotError(f"{role}: module definition does not equal registered M")
        cache_variant = _cache_statement_variant(cache, views)
        query_text_bytes = _bounded_utf16_bytes(query.query_text, f"{role} Query Store text")
        query_variants = {
            _bounded_utf16_bytes(views.statement_text, f"{role} registered S"): "S",
            _bounded_utf16_bytes(views.statement_without_terminator, f"{role} registered T"): "T",
        }
        query_variant = query_variants.get(query_text_bytes)
        if query_variant is None:
            raise IdentitySnapshotError(f"{role}: Query Store text does not equal registered S or T")
        _require_positive_int(query.query_id, f"{role}: query_id")
        _require_positive_int(query.query_text_id, f"{role}: query_text_id")
        if type(query.context_settings_id) is not int or query.context_settings_id < 0:
            raise IdentitySnapshotError(f"{role}: context_settings_id must be retained as a nonnegative exact integer")
        if type(query.parameterization_type) is not int or query.parameterization_type != 0:
            raise IdentitySnapshotError(f"{role}: parameterization_type must be the planned exact value 0")
        summaries.append(RecordConsistencySummary(
            scope="OFFLINE_SUPPLIED_RECORD_CONSISTENCY_ONLY",
            role=role,
            object_id=module.object_id,
            query_id=query.query_id,
            query_text_id=query.query_text_id,
            context_settings_id=query.context_settings_id,
            parameterization_type=query.parameterization_type,
            cache_statement_variant=cache_variant,
            query_store_text_variant=query_variant,
        ))

    for name, values in (
        ("object_id", [item.object_id for item in summaries]),
        ("query_id", [item.query_id for item in summaries]),
        ("query_text_id", [item.query_text_id for item in summaries]),
    ):
        if len(set(values)) != len(ROLES):
            raise IdentitySnapshotError(f"R and H must have distinct supplied {name} values")
    return tuple(summaries)
