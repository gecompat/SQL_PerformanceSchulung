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

    def test_line_comment_cannot_supply_the_page_latch_filter(self) -> None:
        broken = SOURCE.replace(
            "WHERE r.wait_type = N'PAGELATCH_EX'",
            "-- WHERE r.wait_type = N'PAGELATCH_EX'\nWHERE 1 = 1",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("only page latch waits" in error for error in errors))

    def test_block_comment_cannot_supply_the_wait_duration(self) -> None:
        broken = SOURCE.replace(
            "        r.wait_time,",
            "        /* r.wait_time, */",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("documented DMV column" in error for error in errors))

    def test_string_literal_cannot_supply_the_page_latch_filter(self) -> None:
        broken = SOURCE.replace(
            "WHERE r.wait_type = N'PAGELATCH_EX'",
            "WHERE N'r.wait_type = N''PAGELATCH_EX''' = N'no'",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("only page latch waits" in error for error in errors))

    def test_comment_markers_inside_bracketed_identifiers_are_preserved(self) -> None:
        section_start = SOURCE.index("## Lesende Zuordnung einer aktuellen Request-Seite")
        fence = SOURCE.index("```sql", section_start)
        injected = "SELECT 1 AS [label--/* identifier */];\n"
        insert_at = fence + len("```sql\n")
        with_identifier = SOURCE[:insert_at] + injected + SOURCE[insert_at:]
        self.assertEqual(validate_lesson(with_identifier), ())

    def test_unterminated_comment_is_rejected(self) -> None:
        broken = SOURCE.replace("        r.wait_time,", "        r.wait_time, /* unfinished", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("malformed lexical structure" in error for error in errors))

    def test_unterminated_string_is_rejected(self) -> None:
        broken = SOURCE.replace(
            "HAVING COUNT(DISTINCT session_id) >= 2;",
            "HAVING COUNT(DISTINCT session_id) >= 2;\nSELECT N'unfinished",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("malformed lexical structure" in error for error in errors))

    def test_unterminated_bracket_identifier_is_rejected(self) -> None:
        broken = SOURCE.replace(
            "HAVING COUNT(DISTINCT session_id) >= 2;",
            "HAVING COUNT(DISTINCT session_id) >= 2;\nSELECT [unfinished",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("malformed lexical structure" in error for error in errors))

    def test_ambiguous_duplicate_sql_block_is_rejected(self) -> None:
        section_start = SOURCE.index("## Lesende Zuordnung einer aktuellen Request-Seite")
        fence = SOURCE.index("```sql", section_start)
        close = SOURCE.index("```", fence + 6)
        duplicate = SOURCE[:close + 3] + "\n```sql\nSELECT 1;\n```" + SOURCE[close + 3:]
        self.assertTrue(any("exactly one SQL block" in error for error in validate_lesson(duplicate)))


if __name__ == "__main__":
    unittest.main()
