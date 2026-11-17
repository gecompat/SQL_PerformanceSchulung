from __future__ import annotations

import unittest

from validate_res001_lesson_query import LESSON, validate_lesson


SOURCE = LESSON.read_text(encoding="utf-8")


class Res001LessonQueryTests(unittest.TestCase):
    def test_documented_scheduler_query_meets_source_contract(self) -> None:
        self.assertEqual(validate_lesson(SOURCE), ())

    def test_worker_queue_column_is_required(self) -> None:
        broken = SOURCE.replace("       work_queue_count\n", "", 1)
        self.assertTrue(any("worker queue count" in error for error in validate_lesson(broken)))

    def test_cpu_runnable_and_worker_queue_metrics_stay_distinct(self) -> None:
        broken = SOURCE.replace("       runnable_tasks_count,\n", "", 1)
        self.assertTrue(any("runnable-task count" in error for error in validate_lesson(broken)))

    def test_only_online_user_schedulers_are_included(self) -> None:
        broken = SOURCE.replace("  AND is_online = 1\n", "", 1)
        self.assertTrue(any("offline schedulers" in error for error in validate_lesson(broken)))

    def test_comment_cannot_supply_online_scheduler_filter(self) -> None:
        broken = SOURCE.replace(
            "  AND is_online = 1",
            "  -- AND is_online = 1\n  AND 1 = 1",
            1,
        )
        self.assertTrue(any("offline schedulers" in error for error in validate_lesson(broken)))

    def test_block_comment_cannot_supply_user_scheduler_filter(self) -> None:
        broken = SOURCE.replace(
            "WHERE scheduler_id < 255",
            "WHERE /* scheduler_id < 255 */ 1 = 1",
            1,
        )
        self.assertTrue(any("hidden schedulers" in error for error in validate_lesson(broken)))

    def test_string_literal_cannot_supply_online_scheduler_filter(self) -> None:
        broken = SOURCE.replace("  AND is_online = 1", "  AND N'is_online = 1' = N'no'", 1)
        self.assertTrue(any("offline schedulers" in error for error in validate_lesson(broken)))

    def test_scheduler_scope_text_in_case_cannot_replace_where_filters(self) -> None:
        broken = SOURCE.replace("  AND is_online = 1", "", 1).replace(
            "WHERE scheduler_id < 255",
            "WHERE 1 = 1",
            1,
        ).replace(
            "       active_workers_count,",
            "       CASE WHEN scheduler_id < 255 AND is_online = 1 "
            "THEN 1 ELSE 1 END AS scope_marker,\n"
            "       active_workers_count,",
            1,
        )
        self.assertTrue(any(
            "scheduler scope filters constrain" in error
            for error in validate_lesson(broken)
        ))

    def test_ambiguous_duplicate_sql_block_is_rejected(self) -> None:
        section_start = SOURCE.index("## Workerbedarf und CPU-Warteschlange sind verschiedene Signale")
        fence = SOURCE.index("```sql", section_start)
        close = SOURCE.index("```", fence + 6)
        duplicate = SOURCE[:close + 3] + "\n```sql\nSELECT 1;\n```" + SOURCE[close + 3:]
        self.assertTrue(any("exactly one SQL block" in error for error in validate_lesson(duplicate)))


if __name__ == "__main__":
    unittest.main()
