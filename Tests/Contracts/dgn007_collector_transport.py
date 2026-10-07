"""Begrenzter JSON-Transport eines skalaren DGN-007-Capture-Bodys.

decode_capture(text, expected_contract) prüft ausschließlich PROJECT_SEMANTIC.
Schema dgn007-capture-body/v1 bindet Major/Compatibility, Control-Scope,
Parent-Objekt und deklarierte Digests; Herkunft und Vorabfreeze sind unbelegt.
Die JSON-Arrays windows/families/plans/plan_union verwenden exakt die Felder
der vorhandenen frozen Recordtypen. Metriken sind Decimal-Text, Planhashes
16 Hexzeichen ohne Präfix, UTC-Zeiten Integer-100ns-Ticks ab 0001-01-01.
requests enthält zusätzlich row_evidence: MEASURED mit returned_rows als
Integer oder NOT_CAPTURED mit null. Fehlende Messwerte werden nie ergänzt.
Keine SQL-Verbindung, Prozesse, Dateien, RunRecords oder Incidentbewertung.
Phasen, Cleanup, Reihenfolge, Ressourcen und Runtime bleiben unbestätigt.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import Decimal
from fractions import Fraction
import json
import re

from Tests.Contracts.dgn007_prospective_acceptance import (
    AcceptanceContract, ActivePlanRecord, MAX_SQL_TICKS, PlanUnionRecord,
    QueryFamilyRecord, REQUEST_MAPPING, WindowRecord, _contract_valid,
)

SCHEMA = "dgn007-capture-body/v1"
MAX_PAYLOAD_BYTES = 32768
MAX_JSON_DEPTH = 8
MAX_INTEGER_DIGITS = 19
MAX_METRIC_TEXT = 64
MAX_SQL_ID = (1 << 63) - 1
_TOP_FIELDS = frozenset(("schema", "major", "compatibility", "scope",
                        "contract_digest", "source_digest", "parent_object_id",
                        "windows", "requests", "families", "plans", "plan_union"))
_METRICS = ("avg_duration_us", "avg_cpu_us", "avg_logical_reads",
            "avg_row_count", "total_rows")
_METRIC_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]{1,3})?")
_HEX_PATTERN = re.compile(r"[0-9a-fA-F]{16}")


class TransportError(ValueError):
    """Öffentliche Fehler enthalten ausschließlich einen festen FWK-Code."""

    def __init__(self, code: str = "FAIL_CONTRACT"):
        self.code = code if code in ("FAIL_CONTRACT", "FAIL_RESULT_CONTRACT") else "FAIL_CONTRACT"
        super().__init__(self.code)


@dataclass(frozen=True, slots=True)
class RequestCapture:
    window_id: int
    ordinal: int
    request_log_id: int
    group_key: int
    status_code: int
    returned_rows: int | None
    row_evidence: str


@dataclass(frozen=True, slots=True)
class CaptureBody:
    schema: str
    major: int
    compatibility: int
    scope: str
    contract_digest: str
    source_digest: str
    parent_object_id: int
    windows: tuple[WindowRecord, ...]
    requests: tuple[RequestCapture, ...]
    families: tuple[QueryFamilyRecord, ...]
    plans: tuple[ActivePlanRecord, ...]
    plan_union: tuple[PlanUnionRecord, ...]

    @property
    def row_evidence_complete(self) -> bool:
        """Nur deklarierte Messwertvollständigkeit, keine Herkunftsattestation."""
        return len(self.requests) == 8 and all(row.row_evidence == "MEASURED" for row in self.requests)

    @property
    def runtime_attested(self) -> bool:
        return False

    @property
    def validation_scope(self) -> str:
        return "PROJECT_SEMANTIC"

    @property
    def claim_scope(self) -> str:
        return "Skalarer Capture-Body; keine Runtime-Abnahme"


def _require(condition: bool, code: str = "FAIL_RESULT_CONTRACT") -> None:
    if not condition:
        raise TransportError(code)


def _bounded_text(text: str) -> None:
    """Größe und Verschachtelung vor dem JSON-Parser begrenzen."""
    _require(type(text) is str and 0 < len(text) <= MAX_PAYLOAD_BYTES, "FAIL_CONTRACT")
    _require(len(text.encode("utf-8")) <= MAX_PAYLOAD_BYTES, "FAIL_CONTRACT")
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            _require(depth <= MAX_JSON_DEPTH, "FAIL_CONTRACT")
        elif char in "]}":
            depth -= 1
            _require(depth >= 0, "FAIL_CONTRACT")
    _require(depth == 0 and not quoted, "FAIL_CONTRACT")


def _json_integer(text: str) -> int:
    _require(len(text.lstrip("-")) <= MAX_INTEGER_DIGITS, "FAIL_CONTRACT")
    return int(text)


def _reject_number(_text: str) -> None:
    # JSON-Floats sowie NaN/Infinity dürfen nie Python-Floats erzeugen.
    raise TransportError()


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, "FAIL_CONTRACT")
        result[key] = value
    return result


def _object(value: object, expected_fields) -> dict:
    _require(type(value) is dict and set(value) == set(expected_fields), "FAIL_CONTRACT")
    return dict(value)


def _rows(value: object, minimum: int, maximum: int) -> list:
    _require(type(value) is list and minimum <= len(value) <= maximum, "FAIL_CONTRACT")
    return value


def _integer(value: object, minimum: int = 0, maximum: int = MAX_SQL_ID) -> int:
    _require(type(value) is int, "FAIL_CONTRACT")
    _require(minimum <= value <= maximum)
    return value


def _metric(value: object) -> Decimal:
    _require(type(value) is str, "FAIL_CONTRACT")
    _require(0 < len(value) <= MAX_METRIC_TEXT and _METRIC_PATTERN.fullmatch(value) is not None)
    result = Decimal(value)
    representation = result.as_tuple()
    _require(result.is_finite() and result >= 0 and len(representation.digits) <= 34
             and representation.exponent >= -30 and result.adjusted() <= 20)
    return result


def _hash(value: object) -> bytes:
    _require(type(value) is str, "FAIL_CONTRACT")
    _require(_HEX_PATTERN.fullmatch(value) is not None)
    return bytes.fromhex(value)


def _window(value: object) -> WindowRecord:
    row = _object(value, (field.name for field in fields(WindowRecord)))
    for key in row:
        if key in _METRICS:
            row[key] = _metric(row[key])
        elif key == "condition":
            _require(type(row[key]) is str, "FAIL_CONTRACT")
            _require(row[key] in ("A", "B"))
        elif key.endswith("_ticks"):
            row[key] = _integer(row[key], 0, MAX_SQL_TICKS)
        else:
            row[key] = _integer(row[key])
    window = WindowRecord(**row)
    _require(window.window_id in (0, 1) and window.interval_id > 0
             and window.interval_start_ticks <= window.execution_started_ticks
             <= window.execution_finished_ticks < window.interval_end_ticks
             and window.first_request_log_id > 0
             and window.last_request_log_id - window.first_request_log_id + 1 >= 4)
    _require((window.request_count, window.captured_executions, window.execution_count) == (4, 4, 4)
             and 1 <= window.observed_plan_count <= 4 and 1 <= window.executed_plan_count <= 4)
    tolerance = Fraction(1, 1_000_000)
    _require(abs(Fraction(window.total_rows) - 4229) <= tolerance
             and abs(Fraction(window.avg_row_count) * 4 - Fraction(window.total_rows)) <= tolerance)
    return window


def _request(value: object) -> RequestCapture:
    row = _object(value, (field.name for field in fields(RequestCapture)))
    for key in ("window_id", "ordinal", "request_log_id", "group_key", "status_code"):
        row[key] = _integer(row[key])
    _require(type(row["row_evidence"]) is str, "FAIL_CONTRACT")
    _require(row["row_evidence"] in ("MEASURED", "NOT_CAPTURED"), "FAIL_CONTRACT")
    if row["row_evidence"] == "NOT_CAPTURED":
        _require(row["returned_rows"] is None)
    else:
        row["returned_rows"] = _integer(row["returned_rows"])
    return RequestCapture(**row)


def _family(value: object) -> QueryFamilyRecord:
    row = _object(value, (field.name for field in fields(QueryFamilyRecord)))
    for key in ("query_id", "parent_query_id", "parent_object_id"):
        row[key] = _integer(row[key], 1, (1 << 31) - 1 if key == "parent_object_id" else MAX_SQL_ID)
    _require(type(row["parent_object_name"]) is str and type(row["statement_marker"]) is str, "FAIL_CONTRACT")
    _require(row["parent_object_name"] == "dbo.usp_CaseSearch"
             and row["statement_marker"] == "/* DGN007_CASE_SEARCH */")
    return QueryFamilyRecord(**row)


def _plan(value: object, major: int) -> ActivePlanRecord:
    row = _object(value, (field.name for field in fields(ActivePlanRecord)))
    for key in row:
        if key == "query_plan_hash":
            row[key] = _hash(row[key])
        elif key == "plan_type":
            if major == 15:
                _require(row[key] is None)
            else:
                row[key] = _integer(row[key], 0, 2)
                _require(row[key] in (0, 2))
        elif key.endswith("_ticks"):
            row[key] = _integer(row[key], 0, MAX_SQL_TICKS)
        else:
            row[key] = _integer(row[key])
    plan = ActivePlanRecord(**row)
    _require(plan.window_id in (0, 1) and plan.execution_type == 0 and 1 <= plan.execution_count <= 4
             and min(plan.parent_query_id, plan.query_id, plan.plan_id, plan.interval_id) > 0)
    return plan


def _union(value: object) -> PlanUnionRecord:
    row = _object(value, (field.name for field in fields(PlanUnionRecord)))
    for key in row:
        if key == "query_plan_hash":
            row[key] = _hash(row[key])
        else:
            row[key] = _integer(row[key], 0 if key.startswith("executed_in_") else 1,
                                1 if key.startswith("executed_in_") else MAX_SQL_ID)
    return PlanUnionRecord(**row)


def _bindings(body: CaptureBody) -> None:
    sequence = body.scope.rsplit("_", 1)[1]
    _require(tuple(window.window_id for window in body.windows) == (0, 1)
             and tuple(window.condition for window in body.windows) == tuple(sequence))
    a, b = body.windows
    _require(a.interval_id != b.interval_id and a.interval_end_ticks <= b.interval_start_ticks
             and a.last_request_log_id < b.first_request_log_id)
    for index, window in enumerate(body.windows):
        requests = body.requests[index * 4:index * 4 + 4]
        expected = REQUEST_MAPPING[0 if window.condition == "A" else 1]
        for ordinal, (request, pair) in enumerate(zip(requests, expected), 1):
            _require(request.window_id == index and request.ordinal == ordinal
                     and request.request_log_id > 0 and (request.group_key, request.status_code) == pair[:2])
            if request.row_evidence == "MEASURED":
                _require(request.returned_rows == pair[2])
        ids = tuple(request.request_log_id for request in requests)
        _require(ids[0] == window.first_request_log_id and ids[-1] == window.last_request_log_id
                 and all(left < right for left, right in zip(ids, ids[1:])))

    families = {}
    for family in body.families:
        _require(family.parent_object_id == body.parent_object_id and family.query_id not in families
                 and (body.major >= 16 or family.query_id == family.parent_query_id))
        families[family.query_id] = family
    _require(all(family.parent_query_id in families
                 and families[family.parent_query_id].parent_query_id == family.parent_query_id
                 for family in families.values()))

    keys = set()
    identities = {}
    active_union = {}
    for plan in body.plans:
        window = body.windows[plan.window_id]
        _require(plan.interval_id == window.interval_id and plan.query_id in families
                 and families[plan.query_id].parent_query_id == plan.parent_query_id
                 and window.interval_start_ticks <= plan.first_execution_ticks
                 <= plan.last_execution_ticks < window.interval_end_ticks
                 and window.execution_started_ticks <= plan.first_execution_ticks
                 <= plan.last_execution_ticks <= window.execution_finished_ticks)
        key = (plan.window_id, plan.plan_id)
        identity = (plan.parent_query_id, plan.query_id, plan.query_plan_hash, plan.plan_type)
        _require(key not in keys and (plan.plan_id not in identities or identities[plan.plan_id] == identity))
        keys.add(key)
        identities[plan.plan_id] = identity
        union_key = (plan.parent_query_id, plan.query_id, plan.plan_id, plan.query_plan_hash)
        active_union.setdefault(union_key, set()).add(plan.window_id)
    used_queries = {plan.query_id for plan in body.plans} | {plan.parent_query_id for plan in body.plans}
    _require(set(families) == used_queries)
    _require({plan.parent_query_id for plan in body.plans if plan.window_id == 0}
             == {plan.parent_query_id for plan in body.plans if plan.window_id == 1})
    for window in body.windows:
        active = tuple(plan for plan in body.plans if plan.window_id == window.window_id)
        _require(sum(plan.execution_count for plan in active) == 4
                 and len({plan.plan_id for plan in active}) == window.observed_plan_count == window.executed_plan_count)
    declared_union = {}
    for row in body.plan_union:
        key = (row.parent_query_id, row.query_id, row.plan_id, row.query_plan_hash)
        _require(key not in declared_union)
        declared_union[key] = {window_id for window_id, flag in
                               ((0, row.executed_in_t0), (1, row.executed_in_t1)) if flag == 1}
    _require(declared_union == active_union)


def _decode(text: str, expected_contract: AcceptanceContract) -> CaptureBody:
    _bounded_text(text)
    _require(_contract_valid(expected_contract), "FAIL_CONTRACT")
    value = json.loads(text, object_pairs_hook=_unique_object, parse_int=_json_integer,
                       parse_float=_reject_number, parse_constant=_reject_number)
    header = _object(value, _TOP_FIELDS)
    _require(type(header["schema"]) is str and header["schema"] == SCHEMA, "FAIL_CONTRACT")
    major = _integer(header["major"])
    compatibility = _integer(header["compatibility"])
    _require(major in (15, 16, 17) and compatibility == major * 10, "FAIL_CONTRACT")
    _require(type(header["scope"]) is str
             and header["scope"] in ("DGN-007_CONTROL_AB", "DGN-007_CONTROL_BA", "DGN-007_CONTROL_AA"), "FAIL_CONTRACT")
    _require(type(header["contract_digest"]) is str and type(header["source_digest"]) is str
             and header["contract_digest"] == expected_contract.contract_digest
             and header["source_digest"] == expected_contract.source_digest, "FAIL_CONTRACT")
    body = CaptureBody(
        schema=SCHEMA, major=major, compatibility=compatibility, scope=header["scope"],
        contract_digest=header["contract_digest"], source_digest=header["source_digest"],
        parent_object_id=_integer(header["parent_object_id"], 1, (1 << 31) - 1),
        windows=tuple(_window(row) for row in _rows(header["windows"], 2, 2)),
        requests=tuple(_request(row) for row in _rows(header["requests"], 8, 8)),
        families=tuple(_family(row) for row in _rows(header["families"], 1, 12)),
        plans=tuple(_plan(row, major) for row in _rows(header["plans"], 1, 8)),
        plan_union=tuple(_union(row) for row in _rows(header["plan_union"], 1, 8)),
    )
    _bindings(body)
    return body


def decode_capture(text: str, expected_contract: AcceptanceContract) -> CaptureBody:
    """Genau ein JSON-Dokument prüfen; Fehler geben keine Payloadteile zurück.

    Digests binden nur deklarierte Inputs. MEASURED ist eine transportierte
    Angabe, keine überprüfte Runtimeherkunft. Auch ein vollständiger Body hat
    runtime_attested=False und wird nicht in einen RunRecord umgewandelt.
    """
    failure = "FAIL_CONTRACT"
    try:
        return _decode(text, expected_contract)
    except TransportError as exc:
        failure = exc.code
    except (ValueError, TypeError, AttributeError, RecursionError, OverflowError):
        pass
    # Außerhalb des except-Blocks entsteht keine rohe Parser-Fehlerkette.
    raise TransportError(failure) from None
