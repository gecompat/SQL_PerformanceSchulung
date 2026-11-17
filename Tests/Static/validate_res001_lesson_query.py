"""Check the documented RES-001 scheduler snapshot query's source shape only."""
from __future__ import annotations

import re
from pathlib import Path


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

    sql = re.sub(r"\s+", " ", blocks[0]).casefold()
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
    }
    return tuple(
        f"{label}: expected `{fragment}`"
        for label, fragment in required.items()
        if fragment not in sql
    )


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
