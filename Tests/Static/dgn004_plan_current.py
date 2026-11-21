"""Bind a transported DGN-004 actual plan to its fixed Form-A module."""
from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET
import hashlib
import re

from dgn004_identity_snapshot import registered_text_views
from dgn004_capture_result import SHOWPLAN_ROOT


PLAN_NAMESPACE = "{http://schemas.microsoft.com/sqlserver/2004/07/showplan}"
TABLES = frozenset({
    "Orders", "OrderLines", "Customers", "Categories", "Contacts",
    "Cities", "Regions", "Countries", "Items", "ItemGroups",
})


class CurrentPlanError(ValueError):
    """The actual plan is incomplete, stale, ambiguous, or outside Form A."""


@dataclass(frozen=True)
class CurrentPlanSummary:
    role: str
    statement_text: str
    use_plan: bool
    table_names: frozenset[str]
    join_count: int
    concatenation_count: int


def _unbracket(value: str) -> str:
    if value.startswith("[") and value.endswith("]"):
        return value[1:-1].replace("]]", "]")
    return value


def inspect_current_form_a_plan(
    xml_text: str, *, role: str, database_name: str, expected_use_plan: bool = True
) -> CurrentPlanSummary:
    """Require one exact R/H statement and the complete two-branch join graph."""
    if type(role) is not str or role not in {"R", "H"}:
        raise CurrentPlanError("invalid plan role")
    if type(database_name) is not str or not database_name or "[" in database_name or "]" in database_name:
        raise CurrentPlanError("invalid owned database name")
    if type(expected_use_plan) is not bool:
        raise CurrentPlanError("invalid expected UsePlan state")
    if type(xml_text) is not str or len(xml_text.encode("utf-8", errors="strict")) > 256 * 1024:
        raise CurrentPlanError("actual plan text is invalid or over budget")
    try:
        root = ET.fromstring(xml_text)
    except (ET.ParseError, UnicodeError) as exc:
        raise CurrentPlanError("actual plan XML is incomplete") from exc
    if root.tag != SHOWPLAN_ROOT:
        raise CurrentPlanError("actual plan has the wrong ShowPlan root")

    views = registered_text_views()[role]
    module_without_line_ending = views.module_text.rstrip("\r\n")
    module_without_terminator = (
        module_without_line_ending[:-1]
        if module_without_line_ending.endswith(";") else module_without_line_ending
    )
    statements = [item for item in root.iter(PLAN_NAMESPACE + "StmtSimple")]
    if len(statements) != 1:
        raise CurrentPlanError("actual plan does not contain exactly one user statement")
    statement = statements[0]
    statement_text = statement.attrib.get("StatementText")
    # Showplan may preserve module indentation around the statement boundary.
    # Collapse SQL whitespace only; token order, identifier spelling, literal
    # contents, and terminator variants remain bound to the registered source.
    normalized_statement = " ".join(statement_text.split()) if statement_text is not None else None
    expected_statements = {
        " ".join(views.statement_text.split()),
        " ".join(views.statement_without_terminator.split()),
        " ".join(views.module_text.split()),
        " ".join(module_without_line_ending.split()),
        " ".join(module_without_terminator.split()),
    }
    expected_without_terminator = " ".join(views.statement_without_terminator.split())
    parameter_prefix = re.match(r"\A\([^()]{1,256}\)\s*", normalized_statement or "")
    parameterized_core = (
        (normalized_statement or "")[parameter_prefix.end():]
        if parameter_prefix is not None else None
    )
    if (normalized_statement not in expected_statements
            and not (normalized_statement or "").casefold().startswith(
                expected_without_terminator.casefold()
            )
            and parameterized_core not in expected_statements
            and not ((parameterized_core or "").casefold().startswith(
                expected_without_terminator.casefold()
            ))):
        expected = views.statement_text
        prefix = 0
        for actual_char, expected_char in zip(statement_text or "", expected):
            if actual_char != expected_char:
                break
            prefix += 1
        actual_bytes = (statement_text or "").encode("utf-16le", errors="strict")
        expected_bytes = expected.encode("utf-16le", errors="strict")
        actual_hash = hashlib.sha256(actual_bytes).hexdigest()[:12]
        expected_hash = hashlib.sha256(expected_bytes).hexdigest()[:12]
        raise CurrentPlanError(
            "actual plan statement text differs from the registered source "
            f"(chars={len(statement_text or '')}/{len(expected)},prefix={prefix},"
            f"sha256={actual_hash}/{expected_hash},"
            f"fold-prefix={str((normalized_statement or '').casefold().startswith(expected_without_terminator.casefold())).lower()},"
            f"parameter-prefix={str(parameter_prefix is not None).lower()})"
        )

    use_plan_values = [
        value.casefold() for node in root.iter() for key, value in node.attrib.items()
        if key.rsplit("}", 1)[-1].casefold() == "useplan"
    ]
    has_use_plan = any(value in {"true", "1"} for value in use_plan_values)
    if expected_use_plan and (not use_plan_values or not has_use_plan
                              or any(value not in {"true", "1"} for value in use_plan_values)):
        raise CurrentPlanError("the forced actual plan lacks a positive UsePlan marker")
    if not expected_use_plan and has_use_plan:
        raise CurrentPlanError("the unforced actual plan unexpectedly has a positive UsePlan marker")

    query_plans = [item for item in statement if item.tag == PLAN_NAMESPACE + "QueryPlan"]
    if len(query_plans) != 1:
        raise CurrentPlanError("actual statement does not contain exactly one QueryPlan")
    plan_root = query_plans[0]
    objects = [item for item in plan_root.iter(PLAN_NAMESPACE + "Object")]
    table_names: set[str] = set()
    database_names: set[str] = set()
    schemas: set[str] = set()
    for item in objects:
        table = item.attrib.get("Table")
        schema = item.attrib.get("Schema")
        database = item.attrib.get("Database")
        if table is not None:
            table_names.add(_unbracket(table))
        if schema is not None:
            schemas.add(_unbracket(schema))
        if database is not None:
            database_names.add(_unbracket(database))
    if table_names != TABLES or schemas != {"dgn004"} or database_names != {database_name}:
        raise CurrentPlanError("actual plan object references do not match the owned Form-A tables")

    relops = [item for item in plan_root.iter(PLAN_NAMESPACE + "RelOp")]
    join_count = sum(
        1 for item in relops
        if "join" in item.attrib.get("LogicalOp", "").casefold()
        or "join" in item.attrib.get("PhysicalOp", "").casefold()
    )
    concatenation_count = sum(
        1 for item in relops
        if item.attrib.get("LogicalOp", "").casefold() == "concatenation"
        or item.attrib.get("PhysicalOp", "").casefold() == "concatenation"
    )
    if join_count < 9 or concatenation_count != 1:
        raise CurrentPlanError("actual plan does not retain the fixed joined UNION ALL shape")
    return CurrentPlanSummary(
        role=role,
        statement_text=statement_text,
        use_plan=has_use_plan,
        table_names=frozenset(table_names),
        join_count=join_count,
        concatenation_count=concatenation_count,
    )
