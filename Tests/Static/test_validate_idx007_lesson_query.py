from __future__ import annotations

import unittest
from pathlib import Path

from validate_idx007_lesson_query import LESSON, validate_lesson


SOURCE = LESSON.read_text(encoding="utf-8")


class Idx007LessonQueryTests(unittest.TestCase):
    def test_documented_query_meets_source_contract(self) -> None:
        self.assertEqual(validate_lesson(SOURCE), ())

    def test_additional_result_statement_before_cte_is_rejected(self) -> None:
        broken = SOURCE.replace(
            "DECLARE @capture_started_at_utc datetime2(7) = SYSUTCDATETIME();",
            "DECLARE @capture_started_at_utc datetime2(7) = SYSUTCDATETIME();\n\n"
            "SELECT CAST(0 AS int) AS unintended_result;",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("capture marker declaration" in error for error in errors))

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

    def test_aggregate_results_must_be_final_output_columns(self) -> None:
        broken = SOURCE.replace(
            "    COUNT(DISTINCT session_id) AS waiting_sessions,\n",
            "    (SELECT COUNT(DISTINCT session_id) AS waiting_sessions "
            "FROM (VALUES (1)) AS Waits(session_id)) AS decoy_waiting_sessions,\n",
            1,
        ).replace(
            "    MIN(wait_time) AS shortest_wait_time_ms,\n",
            "    (SELECT MIN(wait_time) AS shortest_wait_time_ms "
            "FROM (VALUES (1)) AS Waits(wait_time)) AS decoy_shortest_wait_time_ms,\n",
            1,
        ).replace(
            "    MAX(wait_time) AS longest_wait_time_ms\n",
            "    (SELECT MAX(wait_time) AS longest_wait_time_ms "
            "FROM (VALUES (1)) AS Waits(wait_time)) AS decoy_longest_wait_time_ms\n",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("waiting_sessions" in error for error in errors))
        self.assertTrue(any("shortest_wait_time_ms" in error for error in errors))
        self.assertTrue(any("longest_wait_time_ms" in error for error in errors))

    def test_aggregate_output_aliases_must_use_the_aggregate_values(self) -> None:
        broken = SOURCE.replace(
            "    COUNT(DISTINCT session_id) AS waiting_sessions,\n",
            "    (SELECT COUNT(DISTINCT session_id) AS waiting_sessions "
            "FROM (VALUES (1)) AS Waits(session_id)) AS decoy_waiting_sessions,\n"
            "    CONVERT(bigint, 0) AS waiting_sessions,\n",
            1,
        ).replace(
            "    MIN(wait_time) AS shortest_wait_time_ms,\n",
            "    (SELECT MIN(wait_time) AS shortest_wait_time_ms "
            "FROM (VALUES (1)) AS Waits(wait_time)) AS decoy_shortest_wait_time_ms,\n"
            "    CONVERT(bigint, 0) AS shortest_wait_time_ms,\n",
            1,
        ).replace(
            "    MAX(wait_time) AS longest_wait_time_ms\n",
            "    (SELECT MAX(wait_time) AS longest_wait_time_ms "
            "FROM (VALUES (1)) AS Waits(wait_time)) AS decoy_longest_wait_time_ms,\n"
            "    CONVERT(bigint, 0) AS longest_wait_time_ms\n",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("aggregate value" in error for error in errors))

    def test_final_page_filters_must_restrict_returned_rows(self) -> None:
        broken = SOURCE.replace(
            "WHERE index_id > 0\n  AND page_level = 0",
            "WHERE 1 = 1\n  AND CASE WHEN page_level = 0 THEN 1 ELSE 1 END = 1",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("final result must apply" in error for error in errors))

    def test_two_session_threshold_must_apply_to_final_groups(self) -> None:
        broken = SOURCE.replace(
            "HAVING COUNT(DISTINCT session_id) >= 2",
            "HAVING COUNT(DISTINCT session_id) >= 1",
            1,
        ).replace(
            "    page_level, next_page_file_id, next_page_page_id\n"
            "HAVING COUNT(DISTINCT session_id) >= 1;",
            "    page_level, next_page_file_id, next_page_page_id\n"
            "HAVING COUNT(DISTINCT session_id) >= 1\n"
            "  AND CASE WHEN COUNT(DISTINCT session_id) >= 2 THEN 1 ELSE 1 END = 1;",
            1,
        )
        self.assertIn(
            "AND CASE WHEN COUNT(DISTINCT session_id) >= 2 THEN 1 ELSE 1 END = 1",
            broken,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("final result must apply" in error for error in errors))

    def test_additional_result_statement_after_diagnostic_is_rejected(self) -> None:
        broken = SOURCE.replace(
            "HAVING COUNT(DISTINCT session_id) >= 2;",
            "HAVING COUNT(DISTINCT session_id) >= 2; "
            "SELECT CAST(0 AS int) AS decoy WHERE 1 = 0;",
            1,
        )
        self.assertTrue(any(
            "single final page-diagnostic result statement" in error
            for error in validate_lesson(broken)
        ))

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

    def test_page_chain_alias_must_project_the_source_value(self) -> None:
        broken = SOURCE.replace(
            "    next_page_page_id,",
            "    CASE WHEN next_page_page_id IS NULL THEN NULL ELSE 1 END "
            "AS next_page_page_id,",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("project the `next_page_page_id` source value" in error
                            for error in errors))

    def test_page_header_lookup_must_use_decoded_request_page(self) -> None:
        broken = SOURCE.replace(
            "pr.db_id, pr.file_id, pr.page_id, N'DETAILED'",
            "DB_ID(), pr.file_id, pr.page_id, N'DETAILED'",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("decoded request database, file, and page" in error
                            for error in errors))

    def test_page_header_lookup_must_not_use_a_different_page(self) -> None:
        broken = SOURCE.replace(
            "pr.db_id, pr.file_id, pr.page_id, N'DETAILED'",
            "pr.db_id, pr.file_id, 1, N'DETAILED'",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("decoded request database, file, and page" in error
                            for error in errors))

    def test_page_resource_decoder_must_use_the_request_resource(self) -> None:
        broken = SOURCE.replace(
            "sys.fn_PageResCracker(r.page_resource) AS pr",
            "sys.fn_PageResCracker(0x00) AS pr",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("bind the request page_resource" in error
                            for error in errors))

    def test_unused_correct_decoder_cannot_mask_a_wrong_active_decoder(self) -> None:
        broken = SOURCE.replace(
            "CROSS APPLY sys.fn_PageResCracker(r.page_resource) AS pr",
            "CROSS APPLY sys.fn_PageResCracker(r.page_resource) AS decoy\n"
            "    CROSS APPLY sys.fn_PageResCracker(0x00) AS pr",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("bind the request page_resource" in error
                            for error in errors))

    def test_extra_inner_join_cannot_suppress_page_wait_rows(self) -> None:
        broken = SOURCE.replace(
            "    ) AS info\n    WHERE r.wait_type = N'PAGELATCH_EX'",
            "    ) AS info\n"
            "    INNER JOIN sys.objects AS decoy ON 1 = 0\n"
            "    WHERE r.wait_type = N'PAGELATCH_EX'",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("only the bound request" in error for error in errors))

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

    def test_extra_conjunct_cannot_suppress_all_page_wait_rows(self) -> None:
        broken = SOURCE.replace(
            "      AND pr.db_id = DB_ID()\n)",
            "      AND pr.db_id = DB_ID()\n      AND 1 = 0\n)",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("PageWaits must restrict" in error for error in errors))

    def test_comment_markers_inside_bracketed_identifiers_are_preserved(self) -> None:
        with_identifier = SOURCE.replace(
            "    @capture_started_at_utc AS capture_started_at_utc,\n",
            "    1 AS [label--/* identifier */],\n"
            "    @capture_started_at_utc AS capture_started_at_utc,\n",
            1,
        )
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
