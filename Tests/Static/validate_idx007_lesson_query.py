"""Check the documented IDX-007 snapshot query's bounded source contract.

This is a source-shape check, not a T-SQL parser, runtime test, DMV provenance
check, or proof that the observed page is the rightmost leaf.
"""
from __future__ import annotations

import re
from pathlib import Path


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

    sql = re.sub(r"\s+", " ", blocks[0]).casefold()
    required = {
        "request wait duration uses the documented DMV column": "r.wait_time",
        "page resource is decoded": "sys.fn_pagerescracker(r.page_resource)",
        "page header is read": "sys.dm_db_page_info(",
        "only page latch waits are selected": "r.wait_type = n'pagelatch_ex'",
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
