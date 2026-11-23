from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
from unittest import TestCase, main

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_pilot_sql import (
    EXPECTED, Role, Route, aggregate_batch, database_name, external_tables_batch, fixture_batch,
    fixture_read_batch, measurement_marker, statistics_batch, verify_aggregate, verify_fixture,
)


TOKEN = "RUN12345"


def fixture():
    return tuple(
        (64 * d + 16 * c + r, date(2026, 1, 1) + timedelta(days=d), c, 100 * d + 10 * c + r)
        for d in range(64) for c in range(4) for r in range(16)
    )


class PilotSqlTests(TestCase):
    def test_exact_fixture_and_oracle(self):
        rows = fixture()
        verify_fixture(rows)
        subset = [row for row in rows if date(2026, 1, 17) <= row[1] < date(2026, 1, 25)]
        result = tuple(
            (category, len(values), sum(values))
            for category in range(4)
            for values in [[row[3] for row in subset if row[2] == category]]
        )
        verify_aggregate(result)
        self.assertEqual(result, EXPECTED)

    def test_fixture_rejects_missing_extra_duplicate_and_wrong_values(self):
        rows = fixture()
        corrupt = (rows[0][0], rows[0][1], rows[0][2], 1)
        for candidate in (rows[:-1], rows + rows[:1], rows[:1] + rows[:-1], (corrupt,) + rows[1:]):
            with self.assertRaises(ValueError):
                verify_fixture(candidate)

    def test_routes_share_predicate_and_only_remote_sources_differ_in_pushdown(self):
        statements = [
            aggregate_batch(TOKEN, route).replace(f"FROM dbo.{route.value}", "FROM dbo.Placeholder")
            .replace(measurement_marker(TOKEN, route), "ROUTE_MARKER")
            for route in Route
        ]
        self.assertTrue(all(statement == statements[0] for statement in statements))
        sql = external_tables_batch(TOKEN)
        self.assertEqual(sql.count("LOCATION = 'sqlserver://pbs-run12345:1433'"), 2)
        self.assertEqual(sql.count("LOCATION = 'SQLPERF_LAB_EXT_RUN12345_SOURCE.dbo.Facts'"), 2)
        self.assertEqual(sql.count("CREDENTIAL = PilotSourceReader"), 2)
        self.assertEqual(sql.count("Encrypt=Yes;TrustServerCertificate=No;"), 2)
        self.assertIn("PUSHDOWN = ON", sql)
        self.assertIn("PUSHDOWN = OFF", sql)
        self.assertLess(sql.index("FAIL_OWNERSHIP"), sql.index("CREATE EXTERNAL DATA SOURCE"))

    def test_dangerous_or_wrong_role_inputs_do_not_generate_sql(self):
        for invalid in ("abc12345", "A" * 7, "A" * 9, "AB';--12"):
            with self.subTest(token=invalid), self.assertRaises(ValueError):
                external_tables_batch(invalid)
        with self.assertRaises(ValueError):
            fixture_read_batch(TOKEN, Role.SOURCE, Route.PUSHDOWN_ON)

    def test_mutating_fixtures_and_statistics_are_owned_and_symmetric(self):
        for role in Role:
            sql = fixture_batch(TOKEN, role)
            self.assertIn(database_name(TOKEN, role), sql)
            self.assertLess(sql.index("FAIL_OWNERSHIP"), sql.index("CREATE TABLE"))
        sql = statistics_batch(TOKEN)
        self.assertEqual(sql.count("WITH FULLSCAN;"), 6)
        self.assertLess(sql.index("FAIL_OWNERSHIP"), sql.index("CREATE STATISTICS"))


if __name__ == "__main__":
    main()
