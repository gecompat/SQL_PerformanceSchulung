from __future__ import annotations

import unittest

from sql_lexical_utils import (
    split_tsql_projection_items,
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

    def test_unbalanced_projection_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unbalanced"):
            split_tsql_projection_items("COALESCE(a, b AS value")


if __name__ == "__main__":
    unittest.main()
