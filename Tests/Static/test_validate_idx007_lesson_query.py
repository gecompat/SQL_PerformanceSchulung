from __future__ import annotations

import unittest
from pathlib import Path

from validate_idx007_lesson_query import LESSON, validate_lesson


SOURCE = LESSON.read_text(encoding="utf-8")


class Idx007LessonQueryTests(unittest.TestCase):
    def test_documented_query_meets_source_contract(self) -> None:
        self.assertEqual(validate_lesson(SOURCE), ())

    def test_missing_wait_duration_capture_is_rejected(self) -> None:
        broken = SOURCE.replace("r.wait_time,\n", "", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("documented DMV column" in error for error in errors))

    def test_undocumented_wait_duration_column_is_rejected(self) -> None:
        broken = SOURCE.replace("r.wait_time,\n", "r.wait_duration_ms,\n", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("not `wait_duration_ms`" in error for error in errors))

    def test_missing_wait_duration_range_is_rejected(self) -> None:
        broken = SOURCE.replace("MIN(wait_time) AS shortest_wait_time_ms,\n", "", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("minimum wait duration" in error for error in errors))

    def test_wait_filter_regression_is_rejected(self) -> None:
        broken = SOURCE.replace("r.wait_type = N'PAGELATCH_EX'", "r.wait_type = N'PAGEIOLATCH_EX'", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("only page latch waits" in error for error in errors))

    def test_ambiguous_duplicate_sql_block_is_rejected(self) -> None:
        section_start = SOURCE.index("## Lesende Zuordnung einer aktuellen Request-Seite")
        fence = SOURCE.index("```sql", section_start)
        close = SOURCE.index("```", fence + 6)
        duplicate = SOURCE[:close + 3] + "\n```sql\nSELECT 1;\n```" + SOURCE[close + 3:]
        self.assertTrue(any("exactly one SQL block" in error for error in validate_lesson(duplicate)))


if __name__ == "__main__":
    unittest.main()
