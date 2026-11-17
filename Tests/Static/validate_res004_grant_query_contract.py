#!/usr/bin/env python3
"""Validate the teaching query's RES-004 identity and semaphore bindings.

This checks source structure only after lexically removing T-SQL comments. It
does not parse T-SQL or authenticate a query result, DMV snapshot, SQL Server
version, or runtime behavior.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

from sql_lexical_utils import (
    extract_tsql_cte_body,
    tsql_projection_has_direct_column_binding,
    tsql_projection_has_exact_item,
    tsql_projection_output_names,
    without_tsql_comments,
    without_tsql_comments_or_literals,
)

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / "Documentation/Curriculum/COMPETING_MEMORY_GRANTS_LESSON.md"


class ContractError(ValueError):
    pass


def extract_query(markdown: str) -> str:
    blocks = re.findall(r"```sql\s*(.*?)```", markdown, flags=re.IGNORECASE | re.DOTALL)
    candidates = [block for block in blocks
                  if "declare @ownrequests table" in block.casefold()]
    if len(candidates) != 1:
        raise ContractError("expected exactly one RES-004 diagnostic query")
    return candidates[0]


def validate_sql(sql: str) -> None:
    try:
        uncommented = without_tsql_comments(sql)
    except ValueError as exc:
        raise ContractError(str(exc)) from exc
    normalized = " ".join(without_tsql_comments_or_literals(sql).split()).casefold()
    try:
        own_waits = extract_tsql_cte_body(sql, "OwnWaits")
    except ValueError as exc:
        raise ContractError("expected one balanced RES-004 OwnWaits CTE") from exc
    own_waits_normalized = " ".join(
        without_tsql_comments_or_literals(own_waits).split()
    ).casefold()
    own_waits_with_literals = " ".join(without_tsql_comments(own_waits).split()).casefold()
    required = (
        "primary key (session_id, request_id)",
        "declare @capturedat datetime2(7) = sysutcdatetime()",
        "@capturedat as captured_at_utc",
        "mg.session_id = own.session_id",
        "mg.request_id = own.request_id",
        "r.session_id = mg.session_id",
        "r.request_id = mg.request_id",
        "mg.grant_time is null",
        "select distinct pool_id, resource_semaphore_id from ownwaits",
        "mg.pool_id = observed.pool_id",
        "mg.resource_semaphore_id = observed.resource_semaphore_id",
        "own.session_id = mg.session_id",
        "own.request_id = mg.request_id",
        "rs.pool_id = observed.pool_id",
        "rs.resource_semaphore_id = observed.resource_semaphore_id",
        "mg.wait_time_ms",
        "r.wait_time as request_wait_time_ms",
        "rs.grantee_count",
        "rs.waiter_count",
    )
    missing = tuple(fragment for fragment in required if fragment not in normalized)
    if missing:
        raise ContractError("diagnostic query is missing required RES-004 bindings")
    projection_match = re.search(
        r"\)\s*select\s+(.*?)\s+from\s+observedsemaphores\s+as\s+observed\b",
        normalized,
    )
    if projection_match is None:
        raise ContractError("diagnostic query has no recognizable final projection")
    try:
        output_names = tsql_projection_output_names(projection_match.group(1))
    except ValueError as exc:
        raise ContractError(f"diagnostic final projection is malformed: {exc}") from exc
    if "captured_at_utc" not in output_names:
        raise ContractError("diagnostic result must expose captured_at_utc")
    if not tsql_projection_has_exact_item(
        projection_match.group(1), "@capturedat as captured_at_utc",
    ):
        raise ContractError("diagnostic result must project the @CapturedAt marker value")
    if "grant_time" not in output_names:
        raise ContractError("diagnostic result must expose grant_time to distinguish granted peers")
    if not tsql_projection_has_direct_column_binding(
        projection_match.group(1), "grant_time",
    ):
        raise ContractError("diagnostic result must project the DMV grant_time value")
    if "is_mapped_own_request" not in output_names:
        raise ContractError("diagnostic result must identify mapped own requests")
    if not tsql_projection_has_exact_item(
        projection_match.group(1),
        "CASE WHEN own.session_id IS NULL THEN CONVERT(bit, 0) "
        "ELSE CONVERT(bit, 1) END AS is_mapped_own_request",
    ):
        raise ContractError("diagnostic result must derive own-request mapping from the matched session")
    if ("where mg.grant_time is null and r.wait_type =" not in own_waits_normalized
            or "where mg.grant_time is null and r.wait_type = n'resource_semaphore'"
            not in own_waits_with_literals):
        raise ContractError("own-wait grant and wait-type filters must constrain OwnWaits")
    if normalized.count("sysutcdatetime()") != 1 or normalized.count("@capturedat") != 2:
        raise ContractError("query must use exactly one capture marker for the complete observation")
    for binding in (
        "r.session_id = mg.session_id",
        "r.request_id = mg.request_id",
    ):
        if normalized.count(binding) != 2:
            raise ContractError("both request joins must retain session and request identity")


def validate_markdown(markdown: str) -> None:
    validate_sql(extract_query(markdown))


def main() -> int:
    validate_markdown(LESSON.read_text(encoding="utf-8"))
    print("RES-004 grant query contract: PASS (source structure only)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, OSError) as exc:
        print(f"RES-004 grant query contract: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
