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

    def test_scheduler_identity_and_counts_must_be_projected(self) -> None:
        broken = SOURCE.replace("       scheduler_id,\n", "", 1).replace(
            "       work_queue_count\n", "", 1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("expose `scheduler_id`" in error for error in errors))
        self.assertTrue(any("expose `work_queue_count`" in error for error in errors))

    def test_scheduler_count_alias_must_project_the_dmv_column(self) -> None:
        broken = SOURCE.replace(
            "       current_workers_count,",
            "       CASE WHEN current_workers_count > 0 THEN 0 ELSE 0 END "
            "AS current_workers_count,",
            1,
        )
        self.assertTrue(any("project the `current_workers_count` DMV column" in error
                            for error in validate_lesson(broken)))

    def test_capture_marker_must_be_projected(self) -> None:
        broken = SOURCE.replace("SELECT @CapturedUtc AS captured_utc,\n", "SELECT\n", 1)
        errors = validate_lesson(broken)
        self.assertTrue(any("captured_utc" in error for error in errors))

    def test_capture_alias_must_project_the_declared_capture_value(self) -> None:
        broken = SOURCE.replace(
            "SELECT @CapturedUtc AS captured_utc,",
            "SELECT CONVERT(datetime2(7), 0) AS captured_utc,",
            1,
        )
        self.assertTrue(any("project the `@CapturedUtc` marker value" in error
                            for error in validate_lesson(broken)))

    def test_nested_capture_alias_cannot_replace_output_marker(self) -> None:
        broken = SOURCE.replace(
            "SELECT @CapturedUtc AS captured_utc,",
            "SELECT CASE WHEN scheduler_id > 0 THEN "
            "(SELECT @CapturedUtc AS captured_utc) END AS nested_marker,",
            1,
        )
        errors = validate_lesson(broken)
        self.assertTrue(any("captured_utc" in error for error in errors))

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

    def test_extra_conjunct_cannot_hide_all_online_schedulers(self) -> None:
        broken = SOURCE.replace(
            "  AND is_online = 1\nORDER BY scheduler_id;",
            "  AND is_online = 1\n  AND 1 = 0\nORDER BY scheduler_id;",
            1,
        )
        self.assertTrue(any(
            "only the required user/online filters" in error
            for error in validate_lesson(broken)
        ))

    def test_zero_row_fetch_cannot_suppress_the_scheduler_snapshot(self) -> None:
        broken = SOURCE.replace(
            "ORDER BY scheduler_id;",
            "ORDER BY scheduler_id OFFSET 0 ROWS FETCH NEXT 0 ROWS ONLY;",
            1,
        )
        self.assertTrue(any(
            "row-suppressing clauses" in error
            for error in validate_lesson(broken)
        ))

    def test_row_multiplying_source_join_is_rejected(self) -> None:
        broken = SOURCE.replace(
            "FROM sys.dm_os_schedulers\nWHERE scheduler_id < 255",
            "FROM sys.dm_os_schedulers\n"
            "CROSS JOIN (VALUES (1), (2)) AS duplicate(row_id)\n"
            "WHERE scheduler_id < 255",
            1,
        )
        self.assertTrue(any(
            "without row-multiplying joins" in error
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
