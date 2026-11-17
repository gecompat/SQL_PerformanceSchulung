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

    def test_ambiguous_or_duplicate_query_fence_fails(self) -> None:
        markdown = source_markdown()
        with self.assertRaises(ContractError):
            extract_query(markdown + "\n```sql\nDECLARE @OwnRequests TABLE (x int);\n```\n")


if __name__ == "__main__":
    unittest.main()
