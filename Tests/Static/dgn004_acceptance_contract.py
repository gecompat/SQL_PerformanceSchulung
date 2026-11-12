"""Pure acceptance gate for the narrowed DGN-004 nine-call contract.

This compares explicitly supplied evidence values only. It neither acquires
SQL Server evidence nor attests to the truth or provenance of caller claims.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias
import json
from pathlib import Path


EXPECTED_SCOPE = "CLASSICAL_FORCING_AND_HINT_CONTROL"
TARGET_BUILDS = ("2022/16.0.4265.3", "2025/17.0.4075.5")
CALL_SEQUENCE = (
    ("R", False), ("R", False), ("R", True),
    ("H", False), ("H", True), ("H", True),
    ("R", True), ("H", False), ("R", False),
)
ROWS_PER_CALL = 768
UNIQUE_ROWS_PER_CALL = 384
ROW_WIDTH = 10
ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ai" / "identity" / "registry.json"
FIXTURE_FORMULAS = (
    "Orders.CustomerId = 1 + ((OrderId-1) modulo 48)",
    "Orders.ContactId = 1 + ((OrderId-1) modulo 24)",
    "OrderLines.OrderId = 1 + floor((LineId-1)/2)",
    "OrderLines.ItemId = 1 + ((LineId-1) modulo 48)",
    "Customers.CategoryId = 1 + ((CustomerId-1) modulo 4)",
    "Customers.CityId = 1 + ((CustomerId-1) modulo 12)",
    "Cities.RegionId = 1 + ((CityId-1) modulo 6)",
    "Regions.CountryId = 1 + ((RegionId-1) modulo 3)",
    "ItemGroups.ItemId = 1 + floor((MapId-1)/2)",
    "GroupNo = 1 + ((MapId-1) modulo 2)",
    "CustomerValue = 3000 + CustomerId",
    "CategoryValue = 1000 + CategoryId",
    "ContactValue = 2000 + ContactId",
    "CityValue = 4000 + CityId",
    "RegionValue = 5000 + RegionId",
    "CountryValue = 6000 + CountryId",
    "ItemValue = 7000 + ItemId",
)

Cell: TypeAlias = int
Rows: TypeAlias = tuple[tuple[Cell, ...], ...]


class Verdict(str, Enum):
    PASS = "PASS"
    NOT_PROVEN = "NOT_PROVEN"
    FAIL = "FAIL"
    FAIL_CLEANUP = "FAIL_CLEANUP"


@dataclass(frozen=True)
class CallEvidence:
    """One caller-supplied summary of a planned call, never runtime authority."""

    role: str
    call_number: int
    database_id: int | None
    object_id: int | None
    query_id: int | None
    query_text_id: int | None
    context_settings_id: int | None
    parameterization_type: int | None
    target_plan_id: int | None
    actual_plan_id: int | None
    source_bound: bool | None
    current_plan: bool | None
    fresh_compilation_proven: bool | None
    compile_count_before: int | None
    compile_count_after: int | None
    compile_epoch_before: str | None
    compile_epoch_after: str | None
    recompile_marked: bool | None
    compile_flush_complete: bool | None
    context_bound: bool | None
    transport_complete: bool | None
    rows: Rows | None
    execution_delta: int | None
    force_accepted: bool | None
    is_forced_plan_after_request: bool | None
    use_plan: bool | None
    force_error_epoch: str | None
    force_failure_count_after_request: int | None
    force_failure_count_after_execution: int | None
    unforce_confirmed: bool | None
    is_forced_plan: bool | None
    hint_state: str | None
    external_override_absent: bool | None
    replay_marker: object = None  # deliberately ignored by this narrowed scope


@dataclass(frozen=True)
class BuildEvidence:
    build: str
    acceptance_scope: str | None
    calls: tuple[CallEvidence, ...]
    cleanup_ok: bool | None


@dataclass(frozen=True)
class AcceptanceResult:
    verdict: Verdict
    reasons: tuple[str, ...]


def _valid_rows(rows: Rows) -> bool:
    if type(rows) is not tuple or len(rows) != ROWS_PER_CALL:
        return False
    if any(type(row) is not tuple or len(row) != ROW_WIDTH for row in rows):
        return False
    if any(type(cell) is not int for row in rows for cell in row):
        return False
    try:
        counts = Counter(rows)
    except TypeError:
        return False
    return len(counts) == UNIQUE_ROWS_PER_CALL and set(counts.values()) == {2}


def _require_active_formulas() -> None:
    document = json.loads(REGISTRY.read_text(encoding="utf-8"))
    candidates = document["artifacts"]["TSK-016"]["candidates"]
    candidate = next(item for item in candidates if item["target"] == "DGN-004")
    if candidate.get("active_plan") != "classical_forcing_hint_control_plan":
        raise ValueError("active DGN-004 acceptance plan changed")
    fixture = "\n".join(candidate["mapping_replay_probe_plan"]["fixture_model"])
    if any(formula not in fixture for formula in FIXTURE_FORMULAS):
        raise ValueError("Form A ID/value formulas differ from the registered source")


def form_a_expected_rows() -> Rows:
    """Derive the complete Form A output from the registered closed ID formulas."""
    _require_active_formulas()
    rows: list[tuple[int, ...]] = []
    for line_id in range(1, 193):
        order_id = 1 + (line_id - 1) // 2
        customer_id = 1 + (order_id - 1) % 48
        contact_id = 1 + (order_id - 1) % 24
        category_id = 1 + (customer_id - 1) % 4
        city_id = 1 + (customer_id - 1) % 12
        region_id = 1 + (city_id - 1) % 6
        country_id = 1 + (region_id - 1) % 3
        item_id = 1 + (line_id - 1) % 48
        for group_no in (1, 2):
            row = (
                order_id, line_id, 3000 + customer_id, 1000 + category_id,
                2000 + contact_id, 4000 + city_id, 5000 + region_id,
                6000 + country_id, 7000 + item_id, group_no,
            )
            # The identical UNION ALL branches produce each complete tuple twice.
            rows.extend((row, row))
    return tuple(rows)


def _compile_count(value: int | None, label: str, *, missing: list[str], failures: list[str]) -> None:
    if value is None:
        missing.append(label)
    elif type(value) is not int or value <= 0:
        failures.append(f"{label} must be a positive exact compile count")


def evaluate_build(evidence: BuildEvidence) -> AcceptanceResult:
    """Apply deterministic status and nine-call acceptance rules to supplied evidence."""
    if type(evidence) is not BuildEvidence:
        return AcceptanceResult(Verdict.FAIL, ("build evidence must use the exact contract record",))
    failures: list[str] = []
    missing: list[str] = []

    def require_true(value: object, label: str) -> None:
        if value is None:
            missing.append(label)
        elif type(value) is not bool or not value:
            failures.append(label)

    if evidence.acceptance_scope is None:
        missing.append("acceptance_scope")
    elif evidence.acceptance_scope != EXPECTED_SCOPE:
        failures.append("acceptance_scope is outside the active narrowed contract")
    if type(evidence.build) is not str or evidence.build not in TARGET_BUILDS:
        failures.append("build is outside the two registered target profiles")
    expected_rows = form_a_expected_rows()

    if type(evidence.calls) is not tuple:
        failures.append("calls must be an immutable ordered tuple")
        calls: tuple[CallEvidence, ...] = ()
    else:
        calls = evidence.calls
    if len(calls) < len(CALL_SEQUENCE):
        missing.append("one or more of the nine required calls")
    elif len(calls) > len(CALL_SEQUENCE):
        failures.append("additional calls are outside the fixed nine-call sequence")

    role_identities: dict[str, set[tuple[int, ...]]] = {"R": set(), "H": set()}
    target_plans: dict[str, set[int]] = {"R": set(), "H": set()}
    force_error_epochs: set[str] = set()
    for index, call in enumerate(calls[:len(CALL_SEQUENCE)]):
        expected_role, forced = CALL_SEQUENCE[index]
        label = f"call {index + 1}"
        if type(call) is not CallEvidence:
            failures.append(f"{label} is not an exact CallEvidence")
            continue
        if type(call.role) is not str or type(call.call_number) is not int:
            failures.append(f"{label} role and ordinal must have exact primitive types")
            continue
        if (call.role, call.call_number) != (expected_role, index + 1):
            failures.append(f"{label} does not match the fixed R/H role and ordinal")
        if call.role not in role_identities:
            failures.append(f"{label} has an unknown role")
            continue

        for name, value, positive in (
            ("database_id", call.database_id, True),
            ("object_id", call.object_id, True),
            ("query_id", call.query_id, True),
            ("query_text_id", call.query_text_id, True),
            ("context_settings_id", call.context_settings_id, False),
            ("parameterization_type", call.parameterization_type, False),
            ("target_plan_id", call.target_plan_id, True),
            ("actual_plan_id", call.actual_plan_id, True),
        ):
            if value is None:
                missing.append(f"{label} {name}")
            elif type(value) is not int or (positive and value <= 0) or (not positive and value < 0):
                failures.append(f"{label} {name} is invalid")

        required_ids = (call.database_id, call.object_id, call.query_id, call.query_text_id,
                        call.context_settings_id, call.parameterization_type)
        if all(type(value) is int for value in required_ids):
            role_identities[call.role].add(required_ids)  # type: ignore[arg-type]
        if type(call.parameterization_type) is int and call.parameterization_type != 0:
            failures.append(f"{label} parameterization type differs from the active contract")
        if type(call.target_plan_id) is int and call.target_plan_id > 0:
            target_plans[call.role].add(call.target_plan_id)

        for attribute in (
            "source_bound", "current_plan", "fresh_compilation_proven",
            "context_bound", "transport_complete",
        ):
            require_true(getattr(call, attribute), f"{label} {attribute}")

        if call.rows is None:
            missing.append(f"{label} complete result tuples")
        elif not _valid_rows(call.rows) or call.rows != expected_rows:
            failures.append(f"{label} complete result tuples differ from the Form A oracle")

        if call.execution_delta is None:
            missing.append(f"{label} execution delta")
        elif type(call.execution_delta) is not int or call.execution_delta != 1:
            failures.append(f"{label} must have exactly one own regular execution")

        _compile_count(call.compile_count_after, f"{label} compile count after", missing=missing, failures=failures)
        count_increase_required = index in (1, 2, 4, 5, 6, 7, 8)
        strict_compile_contract = index in (1, 2, 4, 5, 6)
        if count_increase_required:
            _compile_count(call.compile_count_before, f"{label} compile count before", missing=missing, failures=failures)
            if (type(call.compile_count_before) is int and call.compile_count_before > 0
                    and type(call.compile_count_after) is int and call.compile_count_after > 0):
                delta = call.compile_count_after - call.compile_count_before
                if strict_compile_contract:
                    if delta != 1:
                        failures.append(f"{label} compile count delta must be exactly +1")
                elif delta <= 0:
                    failures.append(f"{label} requires a fresh positive compile count increase")
        if strict_compile_contract:
            if call.compile_epoch_before is None or call.compile_epoch_after is None:
                missing.append(f"{label} compile epoch binding")
            elif (type(call.compile_epoch_before) is not str or type(call.compile_epoch_after) is not str
                  or not call.compile_epoch_before or call.compile_epoch_before != call.compile_epoch_after):
                failures.append(f"{label} compile epoch changed or is invalid")
            require_true(call.recompile_marked, f"{label} own recompile marker")
            require_true(call.compile_flush_complete, f"{label} single budgeted compile flush")

        if call.is_forced_plan is None:
            missing.append(f"{label} final is_forced_plan state")
        elif type(call.is_forced_plan) is not bool or call.is_forced_plan:
            failures.append(f"{label} did not end with forcing explicitly cleared")

        if call.role == "H":
            if call.hint_state is None:
                missing.append(f"{label} fixed terminal H hint")
            elif call.hint_state != "FIXED_TERMINAL":
                failures.append(f"{label} H hint is changed, missing, duplicated, or misplaced")
        else:
            if call.hint_state is None:
                missing.append(f"{label} R hint state")
            elif call.hint_state != "ABSENT":
                failures.append(f"{label} R must remain the no-hint reference")
        require_true(call.external_override_absent, f"{label} external overriding control absent")

        if forced:
            require_true(call.force_accepted, f"{label} standard Force accepted")
            require_true(call.is_forced_plan_after_request, f"{label} is_forced_plan after Force")
            require_true(call.use_plan, f"{label} UsePlan observed")
            if call.force_error_epoch is None:
                missing.append(f"{label} force failure epoch")
            elif type(call.force_error_epoch) is not str or not call.force_error_epoch:
                failures.append(f"{label} force failure epoch is invalid")
            elif call.force_error_epoch in force_error_epochs:
                failures.append(f"{label} force failure epoch is not unique to its request")
            else:
                force_error_epochs.add(call.force_error_epoch)
            for name, value in (
                ("after-request force failure count", call.force_failure_count_after_request),
                ("after-execution force failure count", call.force_failure_count_after_execution),
            ):
                if value is None:
                    missing.append(f"{label} {name}")
                elif type(value) is not int or value < 0:
                    failures.append(f"{label} {name} is invalid")
            if (type(call.force_failure_count_after_request) is int
                    and call.force_failure_count_after_request != 0):
                failures.append(f"{label} force failure count is nonzero in the new request epoch")
            if (type(call.force_failure_count_after_request) is int
                    and type(call.force_failure_count_after_execution) is int
                    and call.force_failure_count_after_execution != call.force_failure_count_after_request):
                failures.append(f"{label} has a new force failure in its own request epoch")
            if call.actual_plan_id is None or call.target_plan_id is None:
                missing.append(f"{label} target/actual plan identity")
            elif (type(call.actual_plan_id) is int and type(call.target_plan_id) is int
                  and call.actual_plan_id != call.target_plan_id):
                failures.append(f"{label} actual plan differs from the forced target")
            require_true(call.unforce_confirmed, f"{label} explicit Unforce confirmed")
        else:
            if (call.force_accepted is not None or call.is_forced_plan_after_request is not None
                    or call.use_plan is not None or call.force_error_epoch is not None
                    or call.force_failure_count_after_request is not None
                    or call.force_failure_count_after_execution is not None
                    or call.unforce_confirmed is not None):
                failures.append(f"{label} has Force-only evidence in an unforced phase")

    for role, identities in role_identities.items():
        if len(identities) == 0 and len(calls) < len(CALL_SEQUENCE):
            continue
        if len(identities) != 1:
            failures.append(f"{role} source/query/context identity changes within its role")
    if role_identities["R"] and role_identities["H"]:
        r_identity = next(iter(role_identities["R"]))
        h_identity = next(iter(role_identities["H"]))
        if r_identity[0] != h_identity[0]:
            failures.append("R/H must share the same owned database identity")
        if any(r_identity[position] == h_identity[position] for position in (1, 2, 3)):
            failures.append("R/H object, query, and query-text identities must remain distinct")
    for role, plans in target_plans.items():
        if plans and len(plans) != 1:
            failures.append(f"{role} target plan changes within its role")
    if target_plans["R"] and target_plans["H"] and target_plans["R"] == target_plans["H"]:
        failures.append("R/H target plan identities must remain distinct")

    if evidence.cleanup_ok is False:
        return AcceptanceResult(Verdict.FAIL_CLEANUP, tuple(["owned cleanup failed", *failures, *missing]))
    if evidence.cleanup_ok is None:
        missing.append("owned cleanup evidence")
    elif type(evidence.cleanup_ok) is not bool:
        failures.append("owned cleanup evidence is invalid")

    if failures:
        return AcceptanceResult(Verdict.FAIL, tuple(failures + missing))
    if missing:
        return AcceptanceResult(Verdict.NOT_PROVEN, tuple(missing))
    return AcceptanceResult(Verdict.PASS, ())


def evaluate_matrix(
    builds: tuple[BuildEvidence, ...],
) -> AcceptanceResult:
    """PASS only when both fixed target builds independently pass this contract."""
    failures: list[str] = []
    missing: list[str] = []
    if type(builds) is not tuple:
        return AcceptanceResult(Verdict.FAIL, ("build matrix must be an immutable tuple",))
    by_build: dict[str, BuildEvidence] = {}
    for build in builds:
        if type(build) is not BuildEvidence or build.build not in TARGET_BUILDS or build.build in by_build:
            failures.append("unknown, duplicate, or invalid target build")
        else:
            by_build[build.build] = build
    for target in TARGET_BUILDS:
        evidence = by_build.get(target)
        if evidence is None:
            missing.append(f"target build {target}")
            continue
        result = evaluate_build(evidence)
        if result.verdict is Verdict.FAIL_CLEANUP:
            failures.extend(f"{target}: {reason}" for reason in result.reasons)
        elif result.verdict is Verdict.FAIL:
            failures.extend(f"{target}: {reason}" for reason in result.reasons)
        elif result.verdict is Verdict.NOT_PROVEN:
            missing.extend(f"{target}: {reason}" for reason in result.reasons)
    if any("owned cleanup failed" in reason for reason in failures):
        return AcceptanceResult(Verdict.FAIL_CLEANUP, tuple(failures + missing))
    if failures:
        return AcceptanceResult(Verdict.FAIL, tuple(failures + missing))
    if missing:
        return AcceptanceResult(Verdict.NOT_PROVEN, tuple(missing))
    return AcceptanceResult(Verdict.PASS, ())
