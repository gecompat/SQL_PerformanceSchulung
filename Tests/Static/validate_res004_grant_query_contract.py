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

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / "Documentation/Curriculum/COMPETING_MEMORY_GRANTS_LESSON.md"


class ContractError(ValueError):
    pass


def _without_sql_comments(sql: str) -> str:
    """Remove T-SQL comments while preserving quoted text and token spacing."""
    output: list[str] = []
    index = 0
    block_depth = 0
    quote: str | None = None
    bracketed = False
    while index < len(sql):
        if block_depth:
            if sql.startswith("/*", index):
                block_depth += 1
                output.extend("  ")
                index += 2
            elif sql.startswith("*/", index):
                block_depth -= 1
                output.extend("  ")
                index += 2
            else:
                output.append("\n" if sql[index] == "\n" else " ")
                index += 1
            continue
        if quote is not None:
            output.append(sql[index])
            if sql[index] == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    output.append(sql[index + 1])
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if bracketed:
            output.append(sql[index])
            if sql[index] == "]":
                if index + 1 < len(sql) and sql[index + 1] == "]":
                    output.append(sql[index + 1])
                    index += 2
                    continue
                bracketed = False
            index += 1
            continue
        if sql.startswith("--", index):
            while index < len(sql) and sql[index] not in "\r\n":
                output.append(" ")
                index += 1
            continue
        if sql.startswith("/*", index):
            block_depth = 1
            output.extend("  ")
            index += 2
            continue
        char = sql[index]
        output.append(char)
        if char == "'":
            quote = char
        elif char == '"':
            quote = char
        elif char == "[":
            bracketed = True
        index += 1
    if block_depth:
        raise ContractError("query contains an unterminated block comment")
    return "".join(output)


def extract_query(markdown: str) -> str:
    blocks = re.findall(r"```sql\s*(.*?)```", markdown, flags=re.IGNORECASE | re.DOTALL)
    candidates = [block for block in blocks
                  if "declare @ownrequests table" in block.casefold()]
    if len(candidates) != 1:
        raise ContractError("expected exactly one RES-004 diagnostic query")
    return candidates[0]


def validate_sql(sql: str) -> None:
    normalized = " ".join(_without_sql_comments(sql).split()).casefold()
    required = (
        "primary key (session_id, request_id)",
        "declare @capturedat datetime2(7) = sysutcdatetime()",
        "@capturedat as captured_at_utc",
        "mg.session_id = own.session_id",
        "mg.request_id = own.request_id",
        "r.session_id = mg.session_id",
        "r.request_id = mg.request_id",
        "mg.grant_time is null",
        "r.wait_type = n'resource_semaphore'",
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
