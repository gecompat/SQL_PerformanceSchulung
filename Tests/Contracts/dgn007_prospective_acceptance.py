"""Reine prospektive DGN-007-Prädikatprüfung, keine Runtime-Abnahme.

Der Caller liefert bereits typisierte skalare Records. Herkunft, tatsächlicher
Vorabfreeze und frische Datenbank-Lifecycles bleiben Aufgabe eines späteren
Collectors. Hier werden ausschließlich deklarierte Bindungen und Invarianten
geprüft. Keine SQL-Verbindung, Prozesse, Dateien oder Textparser.
Block/Slot prüfen deklarierte Listenreihenfolge, keine Lifecycle-Chronologie.
Ressourcen und 180/60-Budgets werden festgelegt, aber hier nicht attestiert.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
import hashlib
import json


BLOCKS = (("AB", "BA", "AA"), ("AA", "BA", "AB"))
PHASE_IDS = ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "CONTROL_CONFIG",
             "CONTROL_WINDOWS", "PROFILE_COMPARISON", "CONTROL_EVIDENCE", "CLEANUP")
SOURCE_FILES = (
    "00_Preflight.sql", "10_Setup.sql", "15_Control_AB.sql", "15_Control_BA.sql",
    "15_Control_AA.sql", "20_Query_Store_Windows.sql",
    "21_Controlled_Query_Store_Windows.sql", "30_Profile_Comparison.sql",
    "35_Control_Evidence.sql", "40_Data_Assertion.sql", "90_Cleanup.sql",
    "control-ab.manifest.json", "control-ba.manifest.json", "control-aa.manifest.json",
)
REQUEST_MAPPING = (
    ((8, 3, 228), (1, 3, 2286), (5, 3, 1144), (1, 1, 571)),
    ((1, 3, 2286), (8, 3, 228), (5, 3, 1144), (1, 1, 571)),
)
MAX_SQL_TICKS = 3_155_378_975_999_999_999


@dataclass(frozen=True, slots=True)
class AcceptanceContract:
    schema: str
    contract_digest: str
    source_digest: str
    source_hashes: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class PhaseResult:
    phase_id: str
    outcome: str
    code: str


@dataclass(frozen=True, slots=True)
class QueryFamilyRecord:
    query_id: int
    parent_query_id: int
    parent_object_id: int
    parent_object_name: str
    statement_marker: str


@dataclass(frozen=True, slots=True)
class WindowRecord:
    window_id: int
    condition: str
    interval_id: int
    interval_start_ticks: int
    interval_end_ticks: int
    execution_started_ticks: int
    execution_finished_ticks: int
    first_request_log_id: int
    last_request_log_id: int
    request_count: int
    captured_executions: int
    execution_count: int
    observed_plan_count: int
    executed_plan_count: int
    avg_duration_us: Decimal
    avg_cpu_us: Decimal
    avg_logical_reads: Decimal
    avg_row_count: Decimal
    total_rows: Decimal


@dataclass(frozen=True, slots=True)
class ActivePlanRecord:
    window_id: int
    parent_query_id: int
    query_id: int
    plan_id: int
    interval_id: int
    execution_type: int
    execution_count: int
    first_execution_ticks: int
    last_execution_ticks: int
    query_plan_hash: bytes
    plan_type: int | None


@dataclass(frozen=True, slots=True)
class PlanUnionRecord:
    parent_query_id: int
    query_id: int
    plan_id: int
    query_plan_hash: bytes
    executed_in_t0: int
    executed_in_t1: int


@dataclass(frozen=True, slots=True)
class RequestRecord:
    window_id: int
    ordinal: int
    request_log_id: int
    group_key: int
    status_code: int
    returned_rows: int


@dataclass(frozen=True, slots=True)
class RunRecord:
    major: int
    compatibility: int
    block: int
    slot: int
    lifecycle_id: int
    scope: str
    contract_digest: str
    source_digest: str
    parent_object_id: int
    phases: tuple[PhaseResult, ...]
    absence_outcome: str
    absence_code: str
    requests: tuple[RequestRecord, ...]
    families: tuple[QueryFamilyRecord, ...]
    windows: tuple[WindowRecord, ...]
    plans: tuple[ActivePlanRecord, ...]
    plan_union: tuple[PlanUnionRecord, ...]


@dataclass(frozen=True, slots=True)
class Decision:
    outcome: str
    code: str
    contract_digest: str
    directed_symptom: bool | None = None
    plan_evidence: bool | None = None
    profile_evidence: bool | None = None
    duration_contrasts: tuple[Fraction, ...] = ()
    duration_aa_drift: Fraction | None = None
    reads_contrasts: tuple[Fraction, ...] = ()
    reads_aa_drift: Fraction | None = None

    @property
    def validation_scope(self) -> str:
        return "PROJECT_SEMANTIC"

    @property
    def claim_scope(self) -> str:
        return "Prospektive Prädikatprüfung; keine Runtime-Abnahme"

    @property
    def runtime_attested(self) -> bool:
        return False


class ContractError(ValueError):
    """Öffentliche Ausnahme enthält ausschließlich den festen FWK-Code."""

    def __init__(self) -> None:
        super().__init__("FAIL_CONTRACT")


def _policy(schema: str = "dgn007-prospective-acceptance/v2") -> dict:
    """Feste Regeln; JSON darf diese Version nicht stillschweigend umdefinieren."""
    policy = {
        "schema": schema,
        "decision_reference": "DEC-068",
        "status": "STATIC_PROSPECTIVE_CONTRACT",
        "demo_id": "DGN-007",
        "expected_versions": {"15": 150, "16": 160, "17": 170},
        "blocks": [list(block) for block in BLOCKS],
        "request_mapping": {condition: [list(row) for row in rows]
                            for condition, rows in zip(("A", "B"), REQUEST_MAPPING)},
        "resources_policy": {
            "minimum_logical_cpus": 4, "minimum_memory_mb": 8192,
            "maximum_concurrent_sql_sessions": 1, "lifecycles_per_version": "serial",
            "max_active_versions_per_physical_host": 1,
            "hosted_matrix": "separate_hosts_only", "attestation": "collector_pending",
        },
        "regular_budget_seconds": 180,
        "cleanup_budget_seconds": 60,
        "budget_and_sequence_attestation": "collector_pending_declared_order_only",
        "requests_per_window": 4,
        "total_rows_per_window": "4229",
        "row_rounding_tolerance": "0.000001",
        "primary_metric": "AvgDurationUs",
        "duration_rule": "all_b_minus_a_positive_and_min_gt_max_abs_aa_drift",
        "additional_evidence_rule": "all_four_plan_hash_sets_different_OR_reads_separated",
        "reads_rule": "all_same_nonzero_sign_AND_min_abs_gt_max_abs_aa_drift",
        "cpu_fallback": False,
        "ratio_gate": False,
        "plan_count_minimum": None,
        "plan_comparison_scope": "within_lifecycle_only",
        "decimal_input": {"max_digits": 34, "min_exponent": -30, "max_adjusted": 20},
        "arithmetic": "exact_fraction_from_decimal",
        "time_input": {"unit": "100ns", "origin": "0001-01-01T00:00:00Z",
                       "representation": "nonnegative_integer", "maximum": MAX_SQL_TICKS,
                       "attestation": "collector_pending"},
        "source_hash_normalization": "utf8_crlf_to_lf",
        "freeze_binding": "syntactic_and_internal_only_collector_attestation_pending",
        "claim_scope": "Prospektive Prädikatprüfung; keine Runtime-Abnahme",
    }
    if schema == "dgn007-prospective-acceptance/v2":
        policy["assignment_decision_reference"] = "DEC-072"
        policy["assignment_scope"] = "isolated_lab_observed_requests_and_query_store_intervals"
        policy["qs_sysutc_execution_envelope"] = "diagnostic_only_no_tolerance"
    elif schema != "dgn007-prospective-acceptance/v1":
        raise ContractError()
    return policy


def _digest(mapping: dict) -> str:
    encoded = json.dumps(mapping, sort_keys=True, ensure_ascii=True,
                         separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _sha256(value: object) -> bool:
    return (type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value))


def _plain_json(value: object, depth: int = 0) -> bool:
    if depth > 8:
        return False
    if type(value) in (str, int, bool) or value is None:
        return True
    if type(value) is list:
        return all(_plain_json(item, depth + 1) for item in value)
    if type(value) is dict:
        return all(type(key) is str and _plain_json(item, depth + 1)
                   for key, item in value.items())
    return False


def contract_from_mapping(mapping: dict) -> AcceptanceContract:
    """Bereits dekodiertes JSON streng prüfen und intern kanonisch binden.

    SHA256 über sortierte ASCII-JSON-Schlüssel ohne Whitespace, einschließlich
    source_sha256; source_digest bindet separat genau dieses Quellenobjekt.
    Es wird kein Dateiinhalt gelesen und keine Herkunft attestiert.
    """
    try:
        if type(mapping) is not dict or not _plain_json(mapping):
            raise ContractError()
        policy = _policy(mapping.get("schema"))
        if set(mapping) != set(policy) | {"source_sha256"}:
            raise ContractError()
        actual_policy = {key: mapping[key] for key in policy}
        if _digest(actual_policy) != _digest(policy):
            raise ContractError()
        sources = mapping["source_sha256"]
        if (type(sources) is not dict or set(sources) != set(SOURCE_FILES)
                or not all(_sha256(value) for value in sources.values())):
            raise ContractError()
        return AcceptanceContract(policy["schema"], _digest(mapping), _digest(sources),
                                  tuple(sorted(sources.items())))
    except (TypeError, ValueError, OverflowError, RecursionError):
        raise ContractError() from None


class _RecordError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _require(valid: bool, code: str = "FAIL_RESULT_CONTRACT") -> None:
    if not valid:
        raise _RecordError(code)


def _integer(value: object, low: int = 0, high: int = (1 << 63) - 1) -> bool:
    return type(value) is int and low <= value <= high


def _ticks(value: object) -> bool:
    return _integer(value, 0, MAX_SQL_TICKS)


def _metric(value: object) -> Fraction:
    # Technische Repräsentationsgrenzen begrenzen den Arithmetikaufwand;
    # sie sind keine Performance-Golden-Values oder Messseparationsschwellen.
    _require(type(value) is Decimal and value.is_finite())
    representation = value.as_tuple()
    _require(len(representation.digits) <= 34 and representation.exponent >= -30
             and value.adjusted() <= 20 and value >= 0)
    return Fraction(value)


def _status_failure(runs: tuple) -> str | None:
    """Bekannte Cleanup-/Timeoutfehler auch vor anderen Strukturfehlern sehen."""
    cleanup_failed = False
    timed_out = False
    other_failure = None
    for run in runs:
        if type(run) is not RunRecord:
            continue
        absence_outcome = getattr(run, "absence_outcome", None)
        absence_code = getattr(run, "absence_code", None)
        phases = getattr(run, "phases", None)
        if ((type(absence_outcome) is str and absence_outcome in ("FAIL", "WARN", "SKIP"))
                or (type(absence_code) is str and absence_code == "FAIL_CLEANUP")):
            cleanup_failed = True
        if type(phases) is not tuple:
            continue
        for phase in phases:
            if type(phase) is not PhaseResult:
                continue
            if not all(hasattr(phase, name) for name in ("phase_id", "outcome", "code")):
                continue
            if (type(phase.phase_id) is str and phase.phase_id == "CLEANUP"
                    and (type(phase.outcome) is not str or type(phase.code) is not str
                         or (phase.outcome, phase.code) != ("PASS", "OK"))):
                cleanup_failed = True
            if type(phase.code) is str and phase.code == "FAIL_CLEANUP":
                cleanup_failed = True
            if type(phase.code) is str and phase.code == "FAIL_TIMEOUT":
                timed_out = True
            if (type(phase.outcome) is str and phase.outcome == "FAIL"
                    and type(phase.code) is str and phase.code in
                    ("FAIL_CONTRACT", "FAIL_SAFETY", "FAIL_STATE", "FAIL_EXECUTION", "FAIL_RESULT_CONTRACT")):
                other_failure = other_failure or phase.code
    if cleanup_failed:
        return "FAIL_CLEANUP"
    if timed_out:
        return "FAIL_TIMEOUT"
    return other_failure


def _contract_valid(contract: AcceptanceContract) -> bool:
    if (type(contract) is not AcceptanceContract or type(contract.schema) is not str
            or not _sha256(contract.contract_digest) or not _sha256(contract.source_digest)
            or type(contract.source_hashes) is not tuple
            or len(contract.source_hashes) != len(SOURCE_FILES)
            or any(type(row) is not tuple or len(row) != 2 or type(row[0]) is not str
                   or not _sha256(row[1]) for row in contract.source_hashes)):
        return False
    try:
        mapping = _policy(contract.schema)
        mapping["source_sha256"] = dict(contract.source_hashes)
        return contract == contract_from_mapping(mapping)
    except ContractError:
        return False


def _run_valid(run: RunRecord, sequence: str, schema: str) -> None:
    """Last, Zeitgrenzen und gebundene aktive Mengen aus Records nachprüfen.

    SQL-Eigentum, tatsächliche Ausführung/Reihenfolge und frischer Lifecycle
    werden damit nicht attestiert. Die Metadatenanker sind deklarierte Inputs.
    """
    _require(_integer(run.parent_object_id, 1, (1 << 31) - 1))
    _require(type(run.phases) is tuple and len(run.phases) == len(PHASE_IDS), "FAIL_CONTRACT")
    _require(all(type(phase) is PhaseResult and type(phase.phase_id) is str
                 and type(phase.outcome) is str and type(phase.code) is str
                 for phase in run.phases), "FAIL_CONTRACT")
    _require(tuple(phase.phase_id for phase in run.phases) == PHASE_IDS, "FAIL_CONTRACT")
    _require(all((phase.outcome, phase.code) == ("PASS", "OK") for phase in run.phases), "FAIL_CONTRACT")
    _require(type(run.absence_outcome) is str and type(run.absence_code) is str
             and (run.absence_outcome, run.absence_code) == ("PASS", "OK"), "FAIL_CONTRACT")
    _require(type(run.windows) is tuple and len(run.windows) == 2
             and all(type(window) is WindowRecord for window in run.windows), "FAIL_CONTRACT")
    _require(tuple(window.window_id for window in run.windows) == (0, 1))
    for window, condition in zip(run.windows, sequence):
        _require(_integer(window.window_id, 0, 1) and type(window.condition) is str
                 and window.condition == condition)
        _require(_integer(window.interval_id, 1))
        _require(all(_ticks(value) for value in (window.interval_start_ticks, window.interval_end_ticks,
                     window.execution_started_ticks, window.execution_finished_ticks)))
        _require(window.interval_start_ticks <= window.execution_started_ticks
                 <= window.execution_finished_ticks < window.interval_end_ticks)
        _require(_integer(window.first_request_log_id, 1) and _integer(window.last_request_log_id, 1)
                 and window.last_request_log_id - window.first_request_log_id + 1 >= 4)
        _require(all(_integer(value, 4, 4) for value in
                     (window.request_count, window.captured_executions, window.execution_count)))
        _require(_integer(window.observed_plan_count, 1, 4)
                 and _integer(window.executed_plan_count, 1, 4))
        for value in (window.avg_duration_us, window.avg_cpu_us, window.avg_logical_reads):
            _metric(value)
        total_rows = _metric(window.total_rows)
        avg_rows = _metric(window.avg_row_count)
        tolerance = Fraction(1, 1_000_000)
        _require(abs(total_rows - 4229) <= tolerance
                 and abs(avg_rows * 4 - total_rows) <= tolerance)
    a, b = run.windows
    _require(a.interval_id != b.interval_id and a.interval_end_ticks <= b.interval_start_ticks
             and a.last_request_log_id < b.first_request_log_id)

    _require(type(run.requests) is tuple and len(run.requests) == 8
             and all(type(row) is RequestRecord for row in run.requests), "FAIL_CONTRACT")
    for index, window in enumerate(run.windows):
        requests = run.requests[index * 4:index * 4 + 4]
        expected = REQUEST_MAPPING[0 if window.condition == "A" else 1]
        for ordinal, (request, pair) in enumerate(zip(requests, expected), 1):
            _require(_integer(request.window_id, 0, 1) and request.window_id == window.window_id
                     and _integer(request.ordinal, ordinal, ordinal) and _integer(request.request_log_id, 1))
            _require(all(_integer(value) for value in
                         (request.group_key, request.status_code, request.returned_rows)))
            _require((request.group_key, request.status_code, request.returned_rows) == pair)
        ids = tuple(row.request_log_id for row in requests)
        _require(ids[0] == window.first_request_log_id and ids[-1] == window.last_request_log_id
                 and all(left < right for left, right in zip(ids, ids[1:]))
                 and sum(row.returned_rows for row in requests) == 4229)

    _require(type(run.families) is tuple and 1 <= len(run.families) <= 12
             and all(type(family) is QueryFamilyRecord for family in run.families), "FAIL_CONTRACT")
    families = {}
    for family in run.families:
        _require(_integer(family.query_id, 1) and _integer(family.parent_query_id, 1)
                 and _integer(family.parent_object_id, 1, (1 << 31) - 1)
                 and family.parent_object_id == run.parent_object_id)
        _require(type(family.parent_object_name) is str and family.parent_object_name == "dbo.usp_CaseSearch"
                 and type(family.statement_marker) is str and family.statement_marker == "/* DGN007_CASE_SEARCH */")
        _require(family.query_id not in families)
        _require(run.major >= 16 or family.query_id == family.parent_query_id)
        families[family.query_id] = family
    _require(all(family.parent_query_id in families
                 and families[family.parent_query_id].parent_query_id == family.parent_query_id
                 for family in families.values()))

    _require(type(run.plans) is tuple and 1 <= len(run.plans) <= 8
             and all(type(plan) is ActivePlanRecord for plan in run.plans), "FAIL_CONTRACT")
    plan_keys = set()
    plan_identity = {}
    active_union = {}
    for plan in run.plans:
        _require(_integer(plan.window_id, 0, 1))
        window = run.windows[plan.window_id]
        _require(all(_integer(value, 1) for value in (plan.parent_query_id, plan.query_id, plan.plan_id, plan.interval_id)))
        _require(_integer(plan.execution_type, 0, 0) and _integer(plan.execution_count, 1, 4))
        _require(plan.interval_id == window.interval_id and plan.query_id in families
                 and families[plan.query_id].parent_query_id == plan.parent_query_id)
        _require(_ticks(plan.first_execution_ticks) and _ticks(plan.last_execution_ticks)
                 and window.interval_start_ticks <= plan.first_execution_ticks
                 <= plan.last_execution_ticks < window.interval_end_ticks)
        if schema == "dgn007-prospective-acceptance/v1":
            _require(window.execution_started_ticks <= plan.first_execution_ticks
                     <= plan.last_execution_ticks <= window.execution_finished_ticks)
        _require(type(plan.query_plan_hash) is bytes and len(plan.query_plan_hash) == 8)
        _require((run.major == 15 and plan.plan_type is None)
                 or (run.major >= 16 and _integer(plan.plan_type, 0, 2) and plan.plan_type != 1))
        key = (plan.window_id, plan.plan_id)
        _require(key not in plan_keys)
        plan_keys.add(key)
        identity = (plan.parent_query_id, plan.query_id, plan.query_plan_hash, plan.plan_type)
        _require(plan.plan_id not in plan_identity or plan_identity[plan.plan_id] == identity)
        plan_identity[plan.plan_id] = identity
        union_key = (plan.parent_query_id, plan.query_id, plan.plan_id, plan.query_plan_hash)
        active_union.setdefault(union_key, set()).add(plan.window_id)
    used_queries = {plan.query_id for plan in run.plans} | {plan.parent_query_id for plan in run.plans}
    _require(set(families) == used_queries)
    for window in run.windows:
        plans = tuple(plan for plan in run.plans if plan.window_id == window.window_id)
        _require(sum(plan.execution_count for plan in plans) == 4
                 and len({plan.plan_id for plan in plans}) == window.observed_plan_count == window.executed_plan_count)
    _require({plan.parent_query_id for plan in run.plans if plan.window_id == 0}
             == {plan.parent_query_id for plan in run.plans if plan.window_id == 1})

    _require(type(run.plan_union) is tuple and 1 <= len(run.plan_union) <= 8
             and all(type(row) is PlanUnionRecord for row in run.plan_union), "FAIL_CONTRACT")
    reported_union = {}
    for row in run.plan_union:
        _require(all(_integer(value, 1) for value in (row.parent_query_id, row.query_id, row.plan_id))
                 and type(row.query_plan_hash) is bytes and len(row.query_plan_hash) == 8
                 and _integer(row.executed_in_t0, 0, 1) and _integer(row.executed_in_t1, 0, 1))
        key = (row.parent_query_id, row.query_id, row.plan_id, row.query_plan_hash)
        _require(key not in reported_union)
        reported_union[key] = {index for index, value in enumerate((row.executed_in_t0, row.executed_in_t1)) if value}
    _require(reported_union == active_union)


def evaluate_version(contract: AcceptanceContract, expected_major: int,
                     runs: tuple[RunRecord, ...]) -> Decision:
    """Genau eine vollständige Version bewerten; malformed Records bleiben FAIL.

    Alle vier AB-/BA-Planbelege werden global mit der vollständigen Reads-Route
    verknüpft. Keine per-Lifecycle-ODER-Auswahl, CPU-Ausweichroute oder Ratio.
    Fraction rechnet exakt und unabhängig vom ambient Decimal-Kontext.
    """
    candidate_digest = (getattr(contract, "contract_digest", None)
                        if type(contract) is AcceptanceContract else None)
    digest = candidate_digest if _sha256(candidate_digest) else ""
    if type(runs) not in (tuple, list):
        return Decision("FAIL", "FAIL_CONTRACT", digest)
    status_failure = _status_failure(runs)
    if status_failure in ("FAIL_CLEANUP", "FAIL_TIMEOUT"):
        return Decision("FAIL", status_failure, digest)
    if type(runs) is not tuple:
        return Decision("FAIL", "FAIL_CONTRACT", digest)
    try:
        _require(_contract_valid(contract) and _integer(expected_major, 15, 17), "FAIL_CONTRACT")
        _require(len(runs) == 6 and all(type(run) is RunRecord for run in runs), "FAIL_CONTRACT")
        _require(len({run.lifecycle_id for run in runs if _integer(run.lifecycle_id, 1)}) == 6,
                 "FAIL_CONTRACT")
        for index, run in enumerate(runs):
            block, slot = divmod(index, 3)
            sequence = BLOCKS[block][slot]
            _require(_integer(run.block, block + 1, block + 1) and _integer(run.slot, slot + 1, slot + 1)
                     and _integer(run.major, expected_major, expected_major)
                     and _integer(run.compatibility, expected_major * 10, expected_major * 10), "FAIL_CONTRACT")
            _require(type(run.scope) is str and run.scope == "DGN-007_CONTROL_" + sequence
                     and _sha256(run.contract_digest) and run.contract_digest == contract.contract_digest
                     and _sha256(run.source_digest) and run.source_digest == contract.source_digest,
                     "FAIL_CONTRACT")
        if status_failure is not None:
            raise _RecordError(status_failure)
        duration, reads, duration_drift, reads_drift, plan_differences = [], [], [], [], []
        for index, run in enumerate(runs):
            sequence = BLOCKS[index // 3][index % 3]
            _run_valid(run, sequence, contract.schema)
            first, second = run.windows
            if sequence == "AA":
                duration_drift.append(abs(_metric(second.avg_duration_us) - _metric(first.avg_duration_us)))
                reads_drift.append(abs(_metric(second.avg_logical_reads) - _metric(first.avg_logical_reads)))
            else:
                a, b = (first, second) if sequence == "AB" else (second, first)
                duration.append(_metric(b.avg_duration_us) - _metric(a.avg_duration_us))
                reads.append(_metric(b.avg_logical_reads) - _metric(a.avg_logical_reads))
                # Nur Hashmengen innerhalb desselben Lifecycles vergleichen.
                hashes_a = {plan.query_plan_hash for plan in run.plans if plan.window_id == a.window_id}
                hashes_b = {plan.query_plan_hash for plan in run.plans if plan.window_id == b.window_id}
                plan_differences.append(hashes_a != hashes_b)
        max_duration_drift, max_reads_drift = max(duration_drift), max(reads_drift)
        symptom = all(value > 0 for value in duration) and min(duration) > max_duration_drift
        plan_evidence = all(plan_differences)
        profile_evidence = (all(value > 0 for value in reads) or all(value < 0 for value in reads))
        profile_evidence = profile_evidence and min(abs(value) for value in reads) > max_reads_drift
        passed = symptom and (plan_evidence or profile_evidence)
        return Decision("PASS" if passed else "SKIP", "OK" if passed else "SKIP_EVIDENCE_MISSING",
                        digest, symptom, plan_evidence, profile_evidence, tuple(duration),
                        max_duration_drift, tuple(reads), max_reads_drift)
    except _RecordError as error:
        return Decision("FAIL", error.code, digest)
    except (AttributeError, TypeError):
        # Auch unvollständig konstruierte Recordobjekte geben keine Rohfehler aus.
        return Decision("FAIL", "FAIL_CONTRACT", digest)
