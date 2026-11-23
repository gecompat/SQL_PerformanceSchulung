from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
from unittest import TestCase, main

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_pilot_sql import Role, Route, aggregate_batch, database_name, measurement_marker
from external_tables_pushdown_evidence import Work, active_request_batch, external_work_batch, verify_pushdown


TOKEN = "RUN12345"
SOURCE = database_name(TOKEN, Role.SOURCE)
LOCATION = f"sqlserver://pbs-run12345:1433/{SOURCE}.dbo.Facts"
SELECT = f"SELECT [t].[CategoryId], [t].[EventDate], [t].[Amount] FROM [{SOURCE}].[dbo].[Facts] AS [t]"
FILTER = " WHERE (([t].[EventDate] >= {d '2026-01-17'}) AND ([t].[EventDate] < '20260125'))"
ON = Work("D1", LOCATION, SELECT + FILTER, "Complete", "Done")
OFF = Work("D2", LOCATION, SELECT, "Complete", "Done")


class PushdownEvidenceTests(TestCase):
    def test_accepts_only_correct_bounded_on_and_off_work(self):
        self.assertEqual(verify_pushdown(TOKEN, (ON,), (OFF,)), ("REMOTE_DATE_FILTER", "NO_REMOTE_FILTER"))

    def test_rejects_ambiguous_wrong_or_partial_work(self):
        for rows in (
            (), (ON, ON), (replace(ON, execution_id=OFF.execution_id),),
            (replace(ON, input_name=LOCATION + "Other"),),
            (replace(ON, request_status="Running"),), (replace(ON, work_status="Failed"),),
            (replace(ON, read_command=None),), (replace(ON, read_command="x" * 4000),),
        ):
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                verify_pushdown(TOKEN, rows, (OFF,))

    def test_rejects_decoy_predicates_mismatched_bounds_and_extra_scans(self):
        for text in (
            SELECT, SELECT + FILTER.replace("20260125", "20260126"),
            SELECT + " /*" + FILTER + " */",
            SELECT + FILTER.replace("AND", "OR"),
            SELECT + FILTER.replace("2026-01-17", "20-2601-17"),
            SELECT + FILTER + " UNION ALL " + SELECT,
            SELECT.replace("[dbo].[Facts]", "[dbo].[Other]") + FILTER,
            SELECT + FILTER.replace("[t].[EventDate]", "[wrong].[EventDate]"),
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                verify_pushdown(TOKEN, (replace(ON, read_command=text),), (OFF,))
        with self.assertRaises(ValueError):
            verify_pushdown(TOKEN, (ON,), (replace(OFF, read_command=SELECT + FILTER),))

    def test_dmv_contract_binds_measurement_marker_session_and_handle(self):
        route = Route.PUSHDOWN_ON
        marker = measurement_marker(TOKEN, route)
        self.assertIn(marker, aggregate_batch(TOKEN, route))
        query = active_request_batch(TOKEN, route, 72, 0)
        self.assertIn(marker, query)
        self.assertIn("req.session_id = 72 AND req.request_id = 0 AND req.database_id = DB_ID()", query)
        self.assertIn("req.statement_start_offset", query)
        lookup = external_work_batch(TOKEN, "12AB")
        self.assertIn("WHERE dr.sql_handle = 0x12AB", lookup)
        self.assertIn("w.execution_id = dr.execution_id", lookup)
        self.assertIn("TOP (5)", lookup)
        with self.assertRaises(ValueError):
            external_work_batch(TOKEN, "123")
        with self.assertRaises(ValueError):
            active_request_batch(TOKEN, Route.LOCAL, 1, 0)


if __name__ == "__main__":
    main()
