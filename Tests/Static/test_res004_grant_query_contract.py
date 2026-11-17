from __future__ import annotations

from pathlib import Path
import unittest

from validate_res004_grant_query_contract import (
    ContractError,
    extract_query,
    validate_markdown,
    validate_sql,
)


LESSON = Path(__file__).resolve().parents[2] / "Documentation/Curriculum/COMPETING_MEMORY_GRANTS_LESSON.md"


def source_markdown() -> str:
    return LESSON.read_text(encoding="utf-8")


class GrantQueryContractTests(unittest.TestCase):
    def test_current_teaching_query_is_bound(self) -> None:
        validate_markdown(source_markdown())

    def test_request_join_must_match_request_id(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace("AND r.request_id = mg.request_id", "AND r.request_id = 0", 1)
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_ownwaits_grant_join_must_match_both_own_request_keys(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "ON mg.session_id = own.session_id",
            "ON 1 = 1",
            1,
        ).replace(
            "LEFT JOIN OwnWaits AS own\n"
            "    ON own.session_id = mg.session_id\n"
            "   AND own.request_id = mg.request_id",
            "LEFT JOIN OwnWaits AS own\n"
            "    ON own.session_id = mg.session_id\n"
            "   AND own.request_id = mg.request_id\n"
            "   AND mg.session_id = own.session_id",
            1,
        )
        with self.assertRaisesRegex(ContractError, "bind its grant and request sources"):
            validate_sql(altered)

    def test_later_correct_join_cannot_mask_a_broken_ownwaits_join(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "INNER JOIN sys.dm_exec_query_memory_grants AS mg",
            "INNER JOIN sys.dm_exec_query_stats AS mg",
            1,
        )
        with self.assertRaisesRegex(ContractError, "bind its grant and request sources"):
            validate_sql(altered)

    def test_additional_ownwaits_join_cannot_filter_or_multiply_wait_rows(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "    WHERE mg.grant_time IS NULL",
            "    INNER JOIN sys.objects AS decoy ON 1 = 0\n"
            "    WHERE mg.grant_time IS NULL",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_block_comment_cannot_replace_request_id_binding(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "AND mg.request_id = own.request_id",
            "/* AND mg.request_id = own.request_id */",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_line_comment_cannot_replace_request_id_binding(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "AND mg.request_id = own.request_id",
            "-- AND mg.request_id = own.request_id\nAND mg.session_id = own.session_id",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_string_literal_cannot_supply_resource_semaphore_filter(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "r.wait_type = N'RESOURCE_SEMAPHORE'",
            "N'r.wait_type = N''RESOURCE_SEMAPHORE''' = N'no'",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_resource_semaphore_literal_in_case_cannot_replace_own_wait_filter(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "WHERE mg.grant_time IS NULL\n      AND r.wait_type = N'RESOURCE_SEMAPHORE'",
            "WHERE mg.grant_time IS NULL\n      AND r.wait_type = @ExpectedWait",
            1,
        ).replace(
            "    SELECT own.session_id, own.request_id, mg.pool_id,",
            "    SELECT CASE WHEN r.wait_type = N'RESOURCE_SEMAPHORE' "
            "THEN 1 ELSE 0 END AS decoy, own.session_id, own.request_id, mg.pool_id,",
            1,
        )
        with self.assertRaisesRegex(ContractError, "constrain OwnWaits"):
            validate_sql(altered)

    def test_unrelated_string_cannot_supply_expected_wait_type(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "r.wait_type = N'RESOURCE_SEMAPHORE'",
            "r.wait_type = N'OTHER_WAIT'",
            1,
        ) + "\nSELECT N'RESOURCE_SEMAPHORE';"
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_nested_block_comments_are_removed(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "AND mg.request_id = own.request_id",
            "/* outer /* AND mg.request_id = own.request_id */ still comment */",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_comment_markers_inside_string_literals_are_preserved(self) -> None:
        query = extract_query(source_markdown())
        altered = "DECLARE @CommentText nvarchar(40) = N'-- /* text */';\n" + query
        validate_sql(altered)

    def test_cte_declaration_text_inside_string_is_ignored(self) -> None:
        query = extract_query(source_markdown())
        altered = "DECLARE @Text nvarchar(80) = N'OwnWaits AS (not a CTE)';\n" + query
        validate_sql(altered)

    def test_unterminated_block_comment_fails_closed(self) -> None:
        query = extract_query(source_markdown()) + "\n/* unfinished"
        with self.assertRaises(ContractError):
            validate_sql(query)

    def test_semaphore_join_must_match_pool_and_semaphore(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "AND rs.resource_semaphore_id = observed.resource_semaphore_id;",
            "AND rs.resource_semaphore_id = observed.pool_id;",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_only_one_utc_capture_call_is_allowed(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "DECLARE @CapturedAt datetime2(7) = SYSUTCDATETIME();",
            "DECLARE @CapturedAt datetime2(7) = SYSUTCDATETIME(); "
            "DECLARE @OtherAt datetime2(7) = SYSUTCDATETIME();",
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_request_and_grant_wait_durations_must_be_exposed(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace("mg.wait_time_ms,", "mg.wait_order,", 1)
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_result_must_expose_grant_time_for_peer_state(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace("    mg.grant_time,\n", "", 1)
        with self.assertRaisesRegex(ContractError, "expose grant_time"):
            validate_sql(altered)

    def test_grant_time_alias_must_project_the_dmv_value(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "    mg.grant_time,\n",
            "    CONVERT(bigint, 0) AS grant_time,\n",
            1,
        )
        with self.assertRaisesRegex(ContractError, "DMV grant_time value"):
            validate_sql(altered)

    def test_result_must_expose_own_request_mapping(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace("         ELSE CONVERT(bit, 1) END AS is_mapped_own_request,\n", "", 1)
        with self.assertRaisesRegex(ContractError, "mapped own requests"):
            validate_sql(altered)

    def test_mapping_alias_must_reflect_matched_own_session(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "    CASE WHEN own.session_id IS NULL THEN CONVERT(bit, 0)\n"
            "         ELSE CONVERT(bit, 1) END AS is_mapped_own_request,",
            "    CONVERT(bit, 1) AS is_mapped_own_request,",
            1,
        )
        with self.assertRaisesRegex(ContractError, "derive own-request mapping"):
            validate_sql(altered)

    def test_nested_alias_cannot_replace_final_grant_time_column(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "    mg.grant_time,\n",
            "    (SELECT mg.grant_time AS grant_time) AS nested_grant,\n",
            1,
        )
        with self.assertRaisesRegex(ContractError, "expose grant_time"):
            validate_sql(altered)

    def test_nested_alias_cannot_replace_final_own_request_mapping(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "         ELSE CONVERT(bit, 1) END AS is_mapped_own_request,\n",
            "         (SELECT CONVERT(bit, 1) AS is_mapped_own_request) AS nested_mapping,\n",
            1,
        )
        with self.assertRaisesRegex(ContractError, "mapped own requests"):
            validate_sql(altered)

    def test_capture_alias_in_cte_cannot_replace_final_result_column(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "    SELECT own.session_id, own.request_id, mg.pool_id,\n",
            "    SELECT @CapturedAt AS captured_at_utc, own.session_id, "
            "own.request_id, mg.pool_id,\n",
            1,
        ).replace(
            "    @CapturedAt AS captured_at_utc,\n",
            "    CONVERT(datetime2(7), 0) AS captured_at_utc,\n",
            1,
        )
        with self.assertRaisesRegex(ContractError, "CapturedAt.*marker value"):
            validate_sql(altered)

    def test_wait_filters_must_constrain_the_ownwaits_cte(self) -> None:
        query = extract_query(source_markdown())
        cte_filter = (
            "       AND r.request_id = mg.request_id\n"
            "    WHERE mg.grant_time IS NULL\n"
            "      AND r.wait_type = N'RESOURCE_SEMAPHORE'\n),"
        )
        altered = query.replace(
            cte_filter,
            "       AND r.request_id = mg.request_id\n),",
            1,
        )
        left_join = (
            "LEFT JOIN sys.dm_exec_requests AS r\n"
            "    ON r.session_id = mg.session_id\n"
            "   AND r.request_id = mg.request_id\n"
            "INNER JOIN sys.dm_exec_query_resource_semaphores AS rs"
        )
        altered = altered.replace(
            left_join,
            left_join.replace(
                "INNER JOIN sys.dm_exec_query_resource_semaphores AS rs",
                "   AND mg.grant_time IS NULL\n"
                "   AND r.wait_type = N'RESOURCE_SEMAPHORE'\n"
                "INNER JOIN sys.dm_exec_query_resource_semaphores AS rs",
            ),
            1,
        )
        with self.assertRaises(ContractError):
            validate_sql(altered)

    def test_or_cannot_widen_the_own_wait_filter(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "      AND r.wait_type = N'RESOURCE_SEMAPHORE'\n),",
            "      AND r.wait_type = N'RESOURCE_SEMAPHORE' OR 1 = 1\n),",
            1,
        )
        with self.assertRaisesRegex(ContractError, "must not contain OR"):
            validate_sql(altered)

    def test_or_in_sql_comment_does_not_change_the_own_wait_filter(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "    WHERE mg.grant_time IS NULL",
            "    -- OR 1 = 1 is an inactive comment\n"
            "    WHERE mg.grant_time IS NULL",
            1,
        )
        validate_sql(altered)

    def test_extra_conjunct_cannot_suppress_all_own_wait_rows(self) -> None:
        query = extract_query(source_markdown())
        altered = query.replace(
            "      AND r.wait_type = N'RESOURCE_SEMAPHORE'\n),",
            "      AND r.wait_type = N'RESOURCE_SEMAPHORE' AND 1 = 0\n),",
            1,
        )
        with self.assertRaisesRegex(ContractError, "only the required"):
            validate_sql(altered)

    def test_ambiguous_or_duplicate_query_fence_fails(self) -> None:
        markdown = source_markdown()
        with self.assertRaises(ContractError):
            extract_query(markdown + "\n```sql\nDECLARE @OwnRequests TABLE (x int);\n```\n")


if __name__ == "__main__":
    unittest.main()
