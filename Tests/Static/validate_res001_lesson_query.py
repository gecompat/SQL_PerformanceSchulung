"""Check the documented RES-001 scheduler snapshot query's source shape only."""
from __future__ import annotations

import re
from pathlib import Path

from sql_lexical_utils import (
    tsql_projection_has_direct_column_binding,
    tsql_projection_has_exact_item,
    tsql_projection_output_names,
    without_tsql_comments,
    without_tsql_comments_or_literals,
)


ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / "Documentation/Curriculum/WORKER_QUEUE_PRESSURE_LESSON.md"
SECTION_HEADING = "## Workerbedarf und CPU-Warteschlange sind verschiedene Signale"


def validate_lesson(text: str) -> tuple[str, ...]:
    section_match = re.search(
        rf"(?ms)^{re.escape(SECTION_HEADING)}\s*\n(.*?)(?=^##\s|\Z)", text
    )
    if section_match is None:
        return ("RES-001 worker-scheduler section is missing",)
    blocks = re.findall(r"(?ms)^```sql\s*\n(.*?)^```\s*$", section_match.group(1))
    if len(blocks) != 1:
        return ("RES-001 worker-scheduler section must contain exactly one SQL block",)

    try:
        uncommented = without_tsql_comments(blocks[0])
    except ValueError as exc:
        return (f"RES-001 query has malformed lexical structure: {exc}",)
    executable = without_tsql_comments_or_literals(uncommented)
    marker_match = re.match(
        r"\s*DECLARE\s+@CapturedUtc\s+datetime2\(7\)\s*=\s*"
        r"SYSUTCDATETIME\(\)\s*;",
        executable,
        flags=re.IGNORECASE,
    )
    snapshot_after_marker = (
        re.match(r"\s*SELECT\b", executable[marker_match.end():], re.IGNORECASE)
        if marker_match is not None else None
    )
    select_statements = re.findall(
        r"(?:^|;)\s*SELECT\b", executable, flags=re.IGNORECASE | re.MULTILINE,
    )
    if (marker_match is None or snapshot_after_marker is None
            or len(select_statements) != 1):
        return (
            "query must start with the capture marker declaration followed "
            "directly by the scheduler snapshot",
        )
    sql = re.sub(r"\s+", " ", without_tsql_comments_or_literals(blocks[0])).casefold()
    required = {
        "snapshot marker uses datetime2(7)": "declare @capturedutc datetime2(7) = sysutcdatetime()",
        "scheduler DMV is queried": "from sys.dm_os_schedulers",
        "scheduler identifier is returned": "scheduler_id",
        "current worker count is returned": "current_workers_count",
        "active worker count is returned": "active_workers_count",
        "runnable-task count is returned": "runnable_tasks_count",
        "worker queue count is returned": "work_queue_count",
        "hidden schedulers are excluded": "scheduler_id < 255",
        "offline schedulers are excluded": "is_online = 1",
        "results are ordered by scheduler": "order by scheduler_id",
        "scheduler scope filters constrain the returned rows":
            "where scheduler_id < 255 and is_online = 1 order by scheduler_id",
    }
    errors = [
        f"{label}: expected `{fragment}`"
        for label, fragment in required.items()
        if fragment not in sql
    ]
    scheduler_scope = re.search(
        r"\bwhere\b(.*?)\border\s+by\s+scheduler_id\b", sql,
    )
    if (scheduler_scope is None
            or scheduler_scope.group(1).strip()
            != "scheduler_id < 255 and is_online = 1"):
        errors.append(
            "scheduler WHERE must contain only the required user/online filters"
        )
    if (sql.count(" from ") != 1
            or re.search(
                r"\bfrom\s+sys\.dm_os_schedulers\s+where\s+scheduler_id\s*<\s*255\b",
                sql,
            ) is None):
        errors.append(
            "scheduler snapshot must read directly from sys.dm_os_schedulers without row-multiplying joins"
        )
    if not sql.rstrip().endswith("order by scheduler_id;"):
        errors.append(
            "scheduler final clause must not add pagination or other row-suppressing clauses"
        )
    projection_match = re.search(
        r"\bselect\s+(.*?)\s+from\s+sys\.dm_os_schedulers\b", sql,
    )
    if projection_match is None:
        errors.append("RES-001 query has no recognizable scheduler result projection")
    else:
        try:
            output_names = tsql_projection_output_names(projection_match.group(1))
        except ValueError as exc:
            errors.append(f"RES-001 result projection is malformed: {exc}")
            output_names = frozenset()
        if "captured_utc" not in output_names:
            errors.append("scheduler result must expose the `captured_utc` marker")
        if not tsql_projection_has_exact_item(
            projection_match.group(1), "@capturedutc AS captured_utc",
        ):
            errors.append("scheduler result must project the `@CapturedUtc` marker value")
        for field in (
            "scheduler_id",
            "current_workers_count",
            "active_workers_count",
            "runnable_tasks_count",
            "work_queue_count",
        ):
            if field not in output_names:
                errors.append(f"scheduler result must expose `{field}`")
            elif not tsql_projection_has_direct_column_binding(
                projection_match.group(1), field,
            ):
                errors.append(f"scheduler result must project the `{field}` DMV column")
    return tuple(errors)


def main() -> int:
    errors = validate_lesson(LESSON.read_text(encoding="utf-8"))
    for error in errors:
        print(error)
    if errors:
        return 1
    print("RES-001 lesson query source contract: PASS (static shape only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
