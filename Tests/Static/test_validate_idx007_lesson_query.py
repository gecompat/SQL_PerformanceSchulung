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

    def test_final_result_must_expose_page_partition_and_successor(self) -> None:
        broken = SOURCE.replace(
            "    index_id,\n    partition_id,\n    page_level,\n    next_page_file_id,\n    next_page_page_id,\n",
            "    index_id,\n",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("partition_id" in error for error in errors))
        self.assertTrue(any("next_page_file_id" in error for error in errors))

    def test_final_result_must_expose_capture_marker(self) -> None:
        broken = SOURCE.replace(
            "    @capture_started_at_utc AS capture_started_at_utc,\n", "", 1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("capture_started_at_utc" in error for error in errors))

    def test_capture_alias_must_project_the_declared_capture_value(self) -> None:
        broken = SOURCE.replace(
            "    @capture_started_at_utc AS capture_started_at_utc,",
            "    CONVERT(datetime2(7), 0) AS capture_started_at_utc,",
            1,
        )
        self.assertTrue(any("project the `@capture_started_at_utc` marker value" in error
                            for error in validate_lesson(broken)))

    def test_source_column_name_cannot_stand_in_for_a_renamed_output_alias(self) -> None:
        broken = SOURCE.replace(
            "    database_id,\n",
            "    database_id AS source_database_id,\n",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("final result must expose `database_id`" in error
                            for error in errors))

    def test_required_name_is_recognized_as_an_explicit_output_alias(self) -> None:
        equivalent = SOURCE.replace(
            "    database_id,\n",
            "    database_id AS database_id,\n",
            1,
        )
        self.assertEqual(validate_lesson(equivalent), ())

    def test_wait_filter_regression_is_rejected(self) -> None:
        broken = SOURCE.replace("r.wait_type = N'PAGELATCH_EX'", "r.wait_type = N'PAGEIOLATCH_EX'", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

    def test_line_comment_cannot_supply_the_page_latch_filter(self) -> None:
        broken = SOURCE.replace(
            "WHERE r.wait_type = N'PAGELATCH_EX'",
            "-- WHERE r.wait_type = N'PAGELATCH_EX'\nWHERE 1 = 1",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

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
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

    def test_unrelated_string_cannot_supply_the_expected_wait_type(self) -> None:
        broken = SOURCE.replace(
            "WHERE r.wait_type = N'PAGELATCH_EX'",
            "WHERE r.wait_type = N'PAGEIOLATCH_EX'",
            1,
        ).replace(
            "HAVING COUNT(DISTINCT session_id) >= 2;",
            "HAVING COUNT(DISTINCT session_id) >= 2; SELECT N'PAGELATCH_EX';",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

    def test_inert_wait_literal_cannot_replace_pagewaits_filter(self) -> None:
        broken = SOURCE.replace(
            "WHERE r.wait_type = N'PAGELATCH_EX'",
            "WHERE 1 = 1",
            1,
        ).replace(
            "        r.wait_time,",
            "        r.wait_time,\n"
            "        CASE WHEN r.wait_type = N'PAGELATCH_EX' "
            "THEN 1 ELSE 1 END AS wait_marker,",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

    def test_page_latch_literal_in_case_cannot_replace_parameterized_filter(self) -> None:
        broken = SOURCE.replace(
            "WHERE r.wait_type = N'PAGELATCH_EX'",
            "WHERE r.wait_type = @ExpectedWait",
            1,
        ).replace(
            "    SELECT\n        r.session_id,",
            "    SELECT\n        CASE WHEN r.wait_type = N'PAGELATCH_EX' "
            "THEN 1 ELSE 0 END AS decoy,\n        r.session_id,",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

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
