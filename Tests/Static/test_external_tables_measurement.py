from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
import sys
from time import monotonic
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_driver_evidence import DriverEvidence
from external_tables_measurement import MeasurementResult, UnconfirmedRequestCleanup, measure_pushdown
from external_tables_pilot_sql import EXPECTED, Role, Route, aggregate_batch, database_name, measurement_marker
from external_tables_pushdown_evidence import PUSHDOWN_FILTER_EVIDENCE, Work


TOKEN = "TEST0001"
SOURCE = database_name(TOKEN, Role.SOURCE)
LOCATION = f"sqlserver://pbs-{TOKEN.lower()}:1433/{SOURCE}.dbo.Facts"
COMMAND = f"SELECT * FROM [{SOURCE}].[dbo].[Facts]"
REMOTE_FILTER = " WHERE [EventDate] >= '20260117' AND [EventDate] < '20260125'"


@dataclass
class Request:
    session_id: int
    request_id: int = 0
    rows: tuple = EXPECTED
    done: bool = False

    def finished(self):
        return self.done

    def result(self, deadline):
        assert monotonic() < deadline
        self.done = True
        return self.rows


class Transport:
    def __init__(self):
        self.requests = [Request(51), Request(52), Request(53)]
        self.handles = iter((("01",), ("02",)))
        self.work = iter((
            (Work("E1", LOCATION, COMMAND + REMOTE_FILTER, "Complete", "Done"),),
            (Work("E2", LOCATION, COMMAND, "Complete", "Done"),),
        ))
        self.events = []
        self.route = None
        self.fail_exit = False

    @contextmanager
    def aggregate(self, sql, deadline):
        assert monotonic() < deadline and self.route is None
        index = len([event for event in self.events if event[0] == "open"])
        self.route = tuple(Route)[index]
        assert sql == aggregate_batch(TOKEN, self.route)
        self.events.append(("open", self.route))
        try:
            yield self.requests[index]
        finally:
            self.events.append(("close", self.route))
            self.route = None
            if self.fail_exit:
                raise UnconfirmedRequestCleanup("request completion unconfirmed")

    def active_handles(self, sql, deadline):
        assert monotonic() < deadline and self.route in (Route.PUSHDOWN_ON, Route.PUSHDOWN_OFF)
        request = self.requests[tuple(Route).index(self.route)]
        assert not request.done and self.route is not None
        assert f"req.session_id = {request.session_id}" in sql and "req.request_id = 0" in sql
        assert measurement_marker(TOKEN, self.route) in sql
        self.events.append(("active", self.route))
        return next(self.handles)

    def external_work(self, sql, deadline):
        assert monotonic() < deadline
        assert self.requests[tuple(Route).index(self.route)].done
        handle = "01" if self.route is Route.PUSHDOWN_ON else "02"
        assert f"dr.sql_handle = 0x{handle}" in sql
        self.events.append(("work", self.route))
        return next(self.work)


class MeasurementTests(unittest.TestCase):
    def test_comparison_binds_results_and_work_to_each_live_request(self):
        transport = Transport()
        result = measure_pushdown(transport, TOKEN, monotonic() + 2)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.filters, ("REMOTE_DATE_FILTER", "NO_REMOTE_FILTER"))
        self.assertEqual(transport.events, [
            ("open", Route.LOCAL), ("close", Route.LOCAL),
            ("open", Route.PUSHDOWN_ON), ("active", Route.PUSHDOWN_ON),
            ("work", Route.PUSHDOWN_ON), ("close", Route.PUSHDOWN_ON),
            ("open", Route.PUSHDOWN_OFF), ("active", Route.PUSHDOWN_OFF),
            ("work", Route.PUSHDOWN_OFF), ("close", Route.PUSHDOWN_OFF),
        ])

    def test_connector_evidence_belongs_to_both_live_external_routes(self):
        evidence = DriverEvidence("mssql-ees.service", "17.0.5065.9-3", "libmsodbcsql-18.5.so.1.1", "a" * 64)
        for same in (True, False):
            with self.subTest(same=same):
                transport = Transport()
                observed = []

                def observe(finished, bound):
                    self.assertTrue(monotonic() < bound)
                    self.assertFalse(finished())
                    self.assertEqual(transport.events[-1], ("active", transport.route))
                    observed.append(transport.route)
                    if transport.route is Route.PUSHDOWN_OFF and not same:
                        return replace(evidence, sha256="b" * 64)
                    return evidence

                result = measure_pushdown(transport, TOKEN, monotonic() + 3, observe_driver=observe)
                self.assertEqual(observed, [Route.PUSHDOWN_ON, Route.PUSHDOWN_OFF])
                self.assertEqual((result.status, result.driver), ("PASS", evidence) if same else ("NOT_PROVEN", None))
                self.assertIsNone(transport.route)

    def test_filter_comparison_completes_without_promoting_unavailable_driver_evidence(self):
        transport = Transport()

        def missing_driver(finished, bound):
            raise ValueError("the mapped file is unavailable")

        result = measure_pushdown(transport, TOKEN, monotonic() + 3, observe_driver=missing_driver)
        self.assertEqual(result, MeasurementResult("NOT_PROVEN", "driver_unconfirmed", PUSHDOWN_FILTER_EVIDENCE))
        self.assertIn(("work", Route.PUSHDOWN_OFF), transport.events)
        self.assertIsNone(transport.route)

    def test_distributed_completion_can_settle_after_the_reader_without_reissuing_the_query(self):
        transport = Transport()
        pending, other = tuple(transport.work)
        transport.work = iter(((replace(pending[0], request_status="Running"),), pending, other))
        with patch("external_tables_measurement.sleep") as pause:
            result = measure_pushdown(transport, TOKEN, monotonic() + 2)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(transport.events.count(("open", Route.PUSHDOWN_ON)), 1)
        self.assertEqual(transport.events.count(("work", Route.PUSHDOWN_ON)), 2)
        pause.assert_called_once()

    def test_empty_observation_can_retry_within_the_same_request(self):
        transport = Transport()
        transport.handles = iter(((), ("01",), ("02",)))
        with patch("external_tables_measurement.sleep") as pause:
            self.assertEqual(measure_pushdown(transport, TOKEN, monotonic() + 2).status, "PASS")
        pause.assert_called_once()
        self.assertEqual(transport.events.count(("active", Route.PUSHDOWN_ON)), 2)
        self.assertEqual(transport.events.count(("open", Route.PUSHDOWN_ON)), 1)

    def test_request_ending_before_first_observation_closes_without_work_lookup(self):
        transport = Transport()
        transport.requests[1].done = True
        result = measure_pushdown(transport, TOKEN, monotonic() + 2)
        self.assertEqual((result.status, result.stage, result.filters), ("NOT_PROVEN", "PUSHDOWN_ON", None))
        self.assertEqual(transport.events[-1], ("close", Route.PUSHDOWN_ON))
        self.assertFalse(any(event[0] == "work" for event in transport.events))

    def test_ambiguous_or_reused_handles_and_wrong_result_are_rejected(self):
        for handles, rows, stage in (
            ((("01", "ff"),), EXPECTED, "PUSHDOWN_ON"),
            ((("01",), ("01",)), EXPECTED, "PUSHDOWN_OFF"),
            ((("01",),), (), "PUSHDOWN_ON"),
        ):
            with self.subTest(stage=stage, handles=handles):
                transport = Transport()
                transport.handles = iter(handles)
                transport.requests[1].rows = rows
                result = measure_pushdown(transport, TOKEN, monotonic() + 2)
                self.assertEqual((result.status, result.stage, result.filters), ("NOT_PROVEN", stage, None))
                self.assertIsNone(transport.route)

    def test_deadline_and_unconfirmed_reader_close_cannot_pass(self):
        transport = Transport()
        for deadline in (monotonic() - 1, float("inf")):
            self.assertEqual(measure_pushdown(transport, TOKEN, deadline).status, "NOT_PROVEN")
            self.assertEqual(transport.events, [])
        transport.fail_exit = True
        result = measure_pushdown(transport, TOKEN, monotonic() + 2)
        self.assertEqual(result.status, "FAIL_CLEANUP")
        self.assertEqual(transport.events[-1], ("close", Route.LOCAL))


if __name__ == "__main__":
    unittest.main()
