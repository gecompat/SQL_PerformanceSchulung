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

    def test_ambiguous_duplicate_sql_block_is_rejected(self) -> None:
        section_start = SOURCE.index("## Workerbedarf und CPU-Warteschlange sind verschiedene Signale")
        fence = SOURCE.index("```sql", section_start)
        close = SOURCE.index("```", fence + 6)
        duplicate = SOURCE[:close + 3] + "\n```sql\nSELECT 1;\n```" + SOURCE[close + 3:]
        self.assertTrue(any("exactly one SQL block" in error for error in validate_lesson(duplicate)))


if __name__ == "__main__":
    unittest.main()
