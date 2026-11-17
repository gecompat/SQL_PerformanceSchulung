"""Check the documented IDX-007 snapshot query's bounded source contract.

This is a source-shape check, not a T-SQL parser, runtime test, DMV provenance
check, or proof that the observed page is the rightmost leaf.
"""
from __future__ import annotations

import re
from pathlib import Path

from sql_lexical_utils import (
    extract_tsql_cte_body,
    tsql_projection_has_direct_column_binding,
    tsql_projection_has_exact_item,
    tsql_projection_output_names,
    without_tsql_comments,
    without_tsql_comments_or_literals,
)


ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / "Documentation/Curriculum/LAST_PAGE_INSERT_CONTENTION_LESSON.md"
SECTION_HEADING = "## Lesende Zuordnung einer aktuellen Request-Seite"


def validate_lesson(text: str) -> tuple[str, ...]:
    section_match = re.search(
        rf"(?ms)^{re.escape(SECTION_HEADING)}\s*\n(.*?)(?=^###?\s|\Z)", text
    )
    if section_match is None:
        return ("IDX-007 request-page query section is missing",)
    section = section_match.group(1)
    blocks = re.findall(r"(?ms)^```sql\s*\n(.*?)^```\s*$", section)
    if len(blocks) != 1:
        return ("IDX-007 request-page section must contain exactly one SQL block",)

    try:
        uncommented = without_tsql_comments(blocks[0])
    except ValueError as exc:
        return (f"IDX-007 query has malformed lexical structure: {exc}",)
    sql = re.sub(r"\s+", " ", without_tsql_comments_or_literals(blocks[0])).casefold()
    try:
        page_waits = extract_tsql_cte_body(blocks[0], "PageWaits")
    except ValueError as exc:
        return (f"IDX-007 PageWaits CTE is malformed: {exc}",)
    page_waits_sql = re.sub(
        r"\s+", " ", without_tsql_comments_or_literals(page_waits),
    ).casefold()
    page_waits_with_literals = " ".join(without_tsql_comments(page_waits).split()).casefold()
    required = {
        "request wait duration uses the documented DMV column": "r.wait_time",
        "page resource is decoded": "sys.fn_pagerescracker(r.page_resource)",
        "missing page resources are excluded": "r.page_resource is not null",
        "distinct waiting sessions are counted": "count(distinct session_id) as waiting_sessions",
        "the minimum wait duration is reported": "min(wait_time) as shortest_wait_time_ms",
        "the maximum wait duration is reported": "max(wait_time) as longest_wait_time_ms",
        "only leaf index pages are reported": "page_level = 0",
        "the result requires at least two sessions": "having count(distinct session_id) >= 2",
    }
    errors = []
    for label, fragment in required.items():
        if fragment not in sql:
            errors.append(f"{label}: expected `{fragment}`")
    page_resource_decoder = re.compile(
        r"sys\.fn_pagerescracker\s*\(\s*r\.page_resource\s*\)\s+as\s+pr\b",
    )
    if (page_waits_sql.count("sys.fn_pagerescracker") != 1
            or page_resource_decoder.search(page_waits_sql) is None):
        errors.append(
            "page resource decoder must bind the request page_resource to alias `pr`"
        )
    page_info_call = re.compile(
        r"sys\.dm_db_page_info\s*\(\s*pr\.db_id\s*,\s*pr\.file_id\s*,\s*"
        r"pr\.page_id\s*,\s*n?__tsql_literal_\d+__\s*\)",
    )
    page_info_detailed_call = re.compile(
        r"sys\.dm_db_page_info\s*\(\s*pr\.db_id\s*,\s*pr\.file_id\s*,\s*"
        r"pr\.page_id\s*,\s*n?'detailed'\s*\)",
    )
    if (page_waits_sql.count("sys.dm_db_page_info") != 1
            or page_info_call.search(page_waits_sql) is None
            or page_info_detailed_call.search(page_waits_with_literals) is None):
        errors.append(
            "page header lookup must use the decoded request database, file, and page"
        )
    expected_page_waits_source = re.compile(
        r"\bfrom\s+sys\.dm_exec_requests\s+as\s+r\s+"
        r"cross\s+apply\s+sys\.fn_pagerescracker\s*\(\s*r\.page_resource\s*\)\s+as\s+pr\s+"
        r"cross\s+apply\s+sys\.dm_db_page_info\s*\(\s*pr\.db_id\s*,\s*"
        r"pr\.file_id\s*,\s*pr\.page_id\s*,\s*n?__tsql_literal_\d+__\s*\)\s+"
        r"as\s+info\s+where\b",
    )
    if expected_page_waits_source.search(page_waits_sql) is None:
        errors.append(
            "PageWaits must use only the bound request, resource decoder, and page-header sources"
        )
    page_wait_filters = (
        "where r.wait_type =",
        "and r.page_resource is not null",
        "and r.database_id = db_id()",
        "and pr.db_id = db_id()",
    )
    page_wait_where = re.search(r"\bwhere\b(.*)$", page_waits_sql)
    expected_page_wait_where = (
        "r.wait_type = n__tsql_literal_1__ and r.page_resource is not null "
        "and r.database_id = db_id() and pr.db_id = db_id()"
    )
    if (any(fragment not in page_waits_sql for fragment in page_wait_filters)
            or re.search(r"\bor\b", page_waits_sql)
            or page_wait_where is None
            or page_wait_where.group(1).strip() != expected_page_wait_where
            or "where r.wait_type = n'pagelatch_ex'" not in page_waits_with_literals):
        errors.append("PageWaits must restrict the target database to PAGELATCH_EX requests")
    projection_match = re.search(
        r"\)\s*select\s+(.*?)\s+from\s+pagewaits\b", sql,
    )
    if projection_match is None:
        errors.append("IDX-007 query has no recognizable final result projection")
    else:
        try:
            output_names = tsql_projection_output_names(projection_match.group(1))
        except ValueError as exc:
            errors.append(f"IDX-007 final result projection is malformed: {exc}")
            output_names = frozenset()
        if "capture_started_at_utc" not in output_names:
            errors.append("final result must expose `capture_started_at_utc` for page-chain inspection")
        if not tsql_projection_has_exact_item(
            projection_match.group(1),
            "@capture_started_at_utc AS capture_started_at_utc",
        ):
            errors.append("final result must project the `@capture_started_at_utc` marker value")
        for field in (
            "database_id",
            "file_id",
            "page_id",
            "object_id",
            "index_id",
            "partition_id",
            "page_level",
            "next_page_file_id",
            "next_page_page_id",
        ):
            if field not in output_names:
                errors.append(f"final result must expose `{field}` for page-chain inspection")
            elif not tsql_projection_has_direct_column_binding(
                projection_match.group(1), field,
            ):
                errors.append(f"final result must project the `{field}` source value")
    if "wait_duration_ms" in sql:
        errors.append("query must use documented `wait_time`, not `wait_duration_ms`")
    return tuple(errors)


def main() -> int:
    errors = validate_lesson(LESSON.read_text(encoding="utf-8"))
    for error in errors:
        print(error)
    if errors:
        return 1
    print("IDX-007 lesson query source contract: PASS (static shape only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
