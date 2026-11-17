from __future__ import annotations

import unittest

from sql_lexical_utils import (
    split_tsql_projection_items,
    tsql_projection_has_direct_column_binding,
    tsql_projection_has_exact_item,
    tsql_projection_output_names,
)


class TsqlProjectionTests(unittest.TestCase):
    def test_split_ignores_nested_commas_and_quoted_commas(self) -> None:
        items = split_tsql_projection_items(
            "id, COALESCE(a, b) AS value, N'left,right' AS label, [name,part]"
        )
        self.assertEqual(len(items), 4)

    def test_output_names_use_top_level_aliases(self) -> None:
        names = tsql_projection_output_names(
            "dbo.scheduler_id, COUNT(DISTINCT session_id) AS total, "
            "@captured AS [captured_utc], [name,part]"
        )
        self.assertEqual(
            names,
            frozenset({"scheduler_id", "total", "captured_utc", "name,part"}),
        )

    def test_nested_subquery_alias_is_not_an_outer_output_name(self) -> None:
        names = tsql_projection_output_names(
            "CASE WHEN scheduler_id > 0 THEN "
            "(SELECT @captured AS captured_utc) END AS nested_marker"
        )
        self.assertEqual(names, frozenset({"nested_marker"}))

    def test_exact_item_binds_capture_expression_to_top_level_alias(self) -> None:
        self.assertTrue(tsql_projection_has_exact_item(
            "@captured AS captured_utc, scheduler_id",
            "@captured AS captured_utc",
        ))
        self.assertFalse(tsql_projection_has_exact_item(
            "CONVERT(datetime2(7), 0) AS captured_utc",
            "@captured AS captured_utc",
        ))
        self.assertFalse(tsql_projection_has_exact_item(
            "CASE WHEN x = 1 THEN (SELECT @captured AS captured_utc) END AS nested_marker",
            "@captured AS captured_utc",
        ))

    def test_direct_column_binding_rejects_constant_and_expression_substitutes(self) -> None:
        self.assertTrue(tsql_projection_has_direct_column_binding(
            "s.scheduler_id, current_workers_count AS current_workers_count",
            "current_workers_count",
        ))
        self.assertTrue(tsql_projection_has_direct_column_binding(
            "s.scheduler_id AS scheduler_id", "scheduler_id",
        ))
        self.assertFalse(tsql_projection_has_direct_column_binding(
            "CASE WHEN current_workers_count > 0 THEN 0 ELSE 0 END AS current_workers_count",
            "current_workers_count",
        ))
        self.assertFalse(tsql_projection_has_direct_column_binding(
            "0 AS scheduler_id", "scheduler_id",
        ))

    def test_unbalanced_projection_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unbalanced"):
            split_tsql_projection_items("COALESCE(a, b AS value")


if __name__ == "__main__":
    unittest.main()
