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
    has_tsql_literal_comparison,
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


def extract_cte_body(sql: str, name: str) -> str:
    """Return one balanced, comment-free CTE body without parsing T-SQL."""
    uncommented = without_tsql_comments(sql)
    matches = list(re.finditer(
        rf"\b{re.escape(name)}\s+AS\s*\(", uncommented, flags=re.IGNORECASE,
    ))
    if len(matches) != 1:
        raise ContractError("expected exactly one required RES-004 CTE")
    opening = matches[0].end() - 1
    depth = 0
    quote: str | None = None
    bracketed = False
    index = opening
    while index < len(uncommented):
        char = uncommented[index]
        if quote is not None:
            if char == quote:
                if index + 1 < len(uncommented) and uncommented[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if bracketed:
            if char == "]":
                if index + 1 < len(uncommented) and uncommented[index + 1] == "]":
                    index += 2
                    continue
                bracketed = False
            index += 1
            continue
        if char in "'\"":
            quote = char
        elif char == "[":
            bracketed = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return uncommented[opening + 1:index]
        index += 1
    raise ContractError("required RES-004 CTE is not balanced")


def validate_sql(sql: str) -> None:
    try:
        uncommented = without_tsql_comments(sql)
    except ValueError as exc:
        raise ContractError(str(exc)) from exc
    normalized = " ".join(without_tsql_comments_or_literals(sql).split()).casefold()
    own_waits = extract_cte_body(uncommented, "OwnWaits")
    own_waits_normalized = " ".join(
        without_tsql_comments_or_literals(own_waits).split()
    ).casefold()
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
    if not has_tsql_literal_comparison(sql, "r.wait_type", "RESOURCE_SEMAPHORE"):
        raise ContractError("diagnostic query must filter on RESOURCE_SEMAPHORE")
    if ("where mg.grant_time is null and r.wait_type =" not in own_waits_normalized
            or not has_tsql_literal_comparison(
                own_waits, "r.wait_type", "RESOURCE_SEMAPHORE",
            )):
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
