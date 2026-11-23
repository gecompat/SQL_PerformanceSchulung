from pathlib import Path
import sys
from threading import Event
from time import monotonic
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_measurement import UnconfirmedRequestCleanup
from external_tables_odbc import OdbcMeasurementTransport, REQUEST_IDENTITY
from external_tables_pilot_sql import EXPECTED, Route, aggregate_batch


TOKEN = "TEST0002"
SQL = aggregate_batch(TOKEN, Route.PUSHDOWN_ON)


class Cursor:
    def __init__(self, outputs, gate=None, fail_close=False):
        self.outputs = iter(outputs)
        self.gate = gate
        self.fail_close = fail_close
        self.closed = False
        self.executed = []

    def execute(self, sql):
        self.executed.append(sql)
        if sql != REQUEST_IDENTITY and self.gate is not None:
            assert self.gate.wait(1)
            self.gate = None
        self.current = next(self.outputs)

    def fetchmany(self, size):
        return self.current[:size]

    def nextset(self):
        self.current = next(self.outputs, None)
        return self.current is not None

    def close(self):
        self.closed = True
        if self.fail_close:
            raise RuntimeError("unfiltered secret")


class Connection:
    def __init__(self, cursor):
        self.bound_cursor = cursor
        self.timeout = 0
        self.closed = False

    def cursor(self):
        return self.bound_cursor

    def close(self):
        self.closed = True


class OdbcTransportTests(unittest.TestCase):
    def test_identity_is_issued_on_the_reader_before_the_aggregate_and_observer_is_independent(self):
        gate = Event()
        reader = Connection(Cursor((((51, 0),), None, EXPECTED), gate=gate))
        observer = Connection(Cursor(((("1234",),),)))
        transport = OdbcMeasurementTransport(TOKEN, lambda _: reader, observer)
        deadline = monotonic() + 4
        with transport.aggregate(SQL, deadline) as request:
            self.assertEqual((request.session_id, request.request_id), (51, 0))
            self.assertFalse(request.finished())
            self.assertEqual(transport.active_handles("read owned handle", deadline), ("1234",))
            gate.set()
            self.assertEqual(request.result(deadline), EXPECTED)
        self.assertEqual(reader.bound_cursor.executed, [REQUEST_IDENTITY, SQL])
        self.assertTrue(reader.closed)
        self.assertTrue(reader.bound_cursor.closed)
        self.assertFalse(observer.closed)
        self.assertEqual(observer.bound_cursor.executed, ["read owned handle"])

    def test_unexpected_request_id_prevents_aggregate(self):
        reader = Connection(Cursor((((51, 1),), None)))
        transport = OdbcMeasurementTransport(TOKEN, lambda _: reader, Connection(None))
        with self.assertRaisesRegex(OSError, "Reader request failed"):
            with transport.aggregate(SQL, monotonic() + 4):
                self.fail("unexpectedly started an aggregate")
        self.assertEqual(reader.bound_cursor.executed, [REQUEST_IDENTITY])
        self.assertTrue(reader.closed)

    def test_untrusted_or_repeated_reader_commands_are_rejected(self):
        reader = Connection(Cursor((((51, 0),), None, EXPECTED)))
        transport = OdbcMeasurementTransport(TOKEN, lambda _: reader, Connection(None))
        deadline = monotonic() + 4
        for invalid in ("SELECT 1", aggregate_batch("TEST0003", Route.PUSHDOWN_ON)):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                with transport.aggregate(invalid, deadline):
                    self.fail("unexpectedly started an unowned query")
        with transport.aggregate(SQL, deadline) as request:
            self.assertEqual(request.result(deadline), EXPECTED)
        with self.assertRaises(ValueError):
            with transport.aggregate(SQL, deadline):
                self.fail("unexpectedly re-ran the route")

    def test_extra_results_and_unconfirmed_cleanup_fail_closed(self):
        for outputs, close_failure, error, message in (
            ((((51, 0),), None, EXPECTED, ((1,),)), False, OSError, "Reader request failed"),
            ((((51, 0),), None, EXPECTED), True, UnconfirmedRequestCleanup, "closure was not confirmed"),
        ):
            with self.subTest(close_failure=close_failure):
                reader = Connection(Cursor(outputs, fail_close=close_failure))
                transport = OdbcMeasurementTransport(TOKEN, lambda _: reader, Connection(None))
                deadline = monotonic() + 4
                with self.assertRaisesRegex(error, message):
                    with transport.aggregate(SQL, deadline) as request:
                        request.result(deadline)
                self.assertTrue(reader.closed)

    def test_observer_records_are_bounded_and_preserve_the_remote_command_in_memory(self):
        row = ("E1", "Complete", "Done", "owned input", "owned remote SQL")
        observer = Connection(Cursor(((row,),)))
        transport = OdbcMeasurementTransport(TOKEN, lambda _: None, observer)
        (work,) = transport.external_work("read work", monotonic() + 4)
        self.assertEqual(work.read_command, row[-1])
        self.assertNotIn(row[-1], repr(work))
        observer = Connection(Cursor(((row,) * 6,)))
        transport = OdbcMeasurementTransport(TOKEN, lambda _: None, observer)
        with self.assertRaisesRegex(OSError, "observer request failed"):
            transport.external_work("oversized work", monotonic() + 4)
        self.assertTrue(observer.bound_cursor.closed)


if __name__ == "__main__":
    unittest.main()
