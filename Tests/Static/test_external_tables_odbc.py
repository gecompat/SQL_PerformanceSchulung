from datetime import timedelta
from hashlib import sha256
from ipaddress import IPv4Address, IPv4Interface
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from threading import Event
from time import monotonic
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_network import GuestNetwork
from external_tables_measurement import MeasurementResult, UnconfirmedRequestCleanup
from external_tables_odbc import (
    OdbcMeasurementTransport, OdbcPilotAdministration, REQUEST_IDENTITY, load_pinned_pyodbc, run_guest_measurement,
    verify_guest_principal, verify_source_tls,
)
from external_tables_pilot_sql import (
    DAY_ZERO, EXPECTED, ROWS, Role, Route, aggregate_batch, database_name, fixture_read_batch, verify_fixture,
)
from external_tables_principals import Principal, principal_name
from external_tables_pushdown_evidence import PUSHDOWN_FILTER_EVIDENCE


TOKEN = "TEST0002"
LAB_BLOCK = 0xC0A86300
NETWORK = GuestNetwork(IPv4Interface((LAB_BLOCK + 2, 29)), IPv4Interface((LAB_BLOCK + 3, 29)))
SOURCE_IP = str(NETWORK.source.ip)
QUERY_IP = str(NETWORK.query.ip)
WRONG_IP = str(NETWORK.query.ip + 1)
SQL = aggregate_batch(TOKEN, Route.PUSHDOWN_ON)


class PinnedPyodbcTests(unittest.TestCase):
    def test_checks_native_bytes_before_load_and_disables_pooling(self):
        filename = "pyodbc.cpython-312-x86_64-linux-gnu.so"
        data = b"synthetic native extension"
        wheel = {
            "version": "5.5.0",
            "installed_extension": {"filename": filename, "size": len(data), "sha256": sha256(data).hexdigest()},
        }
        runtime = SimpleNamespace(
            implementation=SimpleNamespace(name="cpython"), version_info=(3, 12),
            platform="linux", modules={},
        )
        loader = Mock()
        spec = SimpleNamespace(loader=loader)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / filename
            file.write_bytes(b"!" * len(data))
            module = SimpleNamespace(version="5.5.0", __file__=str(file.resolve()), pooling=True)
            with (
                patch("external_tables_odbc.sys", runtime),
                patch("external_tables_odbc.os", SimpleNamespace(uname=lambda: SimpleNamespace(machine="x86_64"))),
                patch("external_tables_odbc.EXTENSION_SUFFIXES", [filename.removeprefix("pyodbc")]),
                patch("external_tables_odbc.spec_from_file_location", return_value=spec) as resolve,
                patch("external_tables_odbc.module_from_spec", return_value=module),
            ):
                with self.assertRaisesRegex(ValueError, "differs from the wheel lock"):
                    load_pinned_pyodbc(root, wheel)
                resolve.assert_not_called()
                file.write_bytes(data)
                self.assertIs(load_pinned_pyodbc(root, wheel), module)
                resolve.assert_called_once_with("pyodbc", file.resolve())
                loader.exec_module.assert_called_once_with(module)
                self.assertFalse(module.pooling)
                with self.assertRaisesRegex(ValueError, "before loading"):
                    load_pinned_pyodbc(root, wheel)


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
        if self.fail_close and self.executed[-1] != REQUEST_IDENTITY:
            raise RuntimeError("unfiltered secret")


class Connection:
    def __init__(self, cursor):
        self.bound_cursor = cursor
        self.timeout = 0
        self.closed = False
        self.cursor_timeouts = []

    def cursor(self):
        self.cursor_timeouts.append(self.timeout)
        return self.bound_cursor

    def close(self):
        self.closed = True


class OdbcAdministrationTests(unittest.TestCase):
    def setUp(self):
        self.factory = Mock()
        self.admin = OdbcPilotAdministration(TOKEN, Role.QUERY, self.factory)
        self.database = database_name(TOKEN, Role.QUERY)
        self.deadline = monotonic() + 20

    def connection_for(self, outputs, *, has_rows=False):
        cursor = Cursor(outputs)
        cursor.description = ("result",) if has_rows else None
        connection = Connection(cursor)
        self.factory.return_value = connection
        return connection, cursor

    def test_setup_targets_the_expected_database_with_a_fresh_bounded_local_session(self):
        connection, cursor = self.connection_for((None,))
        self.admin.execute(self.database, "SYNTHETIC SETUP", self.deadline)
        target, timeout = self.factory.call_args.args
        self.assertEqual(target, self.database)
        self.assertGreater(timeout, 0)
        self.assertLessEqual(timeout, 20)
        self.assertTrue(connection.closed and cursor.closed)
        self.assertGreater(connection.cursor_timeouts[0], 0)
        self.assertTrue(cursor.executed[0].endswith("SYNTHETIC SETUP"))
        for check in (
            self.database, "ProductVersion", "Edition", "@@TRANCOUNT", "sysadmin",
            "CONNECTIONPROPERTY('local_net_address')", "CONNECTIONPROPERTY('client_net_address')",
        ):
            self.assertIn(check, cursor.executed[0])
        self.assertEqual(cursor.executed[0].count("127.0.0.1"), 2)

    def test_foreign_database_and_other_role_queries_are_rejected_before_connection(self):
        source_db = database_name(TOKEN, Role.SOURCE)
        with self.assertRaises(ValueError):
            self.admin.execute(source_db, "FOREIGN SETUP", self.deadline)
        with self.assertRaises(ValueError):
            self.admin.database_exists(source_db, self.deadline)
        source = OdbcPilotAdministration(TOKEN, Role.SOURCE, self.factory)
        with self.assertRaises(ValueError):
            source.fixture_rows(fixture_read_batch(TOKEN, Role.QUERY, Route.PUSHDOWN_ON), self.deadline)
        self.factory.assert_not_called()

    def test_exact_fixture_requires_all_rows_and_a_single_result(self):
        rows = []
        for key in range(ROWS):
            day, remainder = divmod(key, 64)
            category, ordinal = divmod(remainder, 16)
            rows.append((key, DAY_ZERO + timedelta(days=day), category, 100 * day + 10 * category + ordinal))
        query = fixture_read_batch(TOKEN, Role.QUERY, Route.PUSHDOWN_ON)
        self.connection_for((rows,), has_rows=True)
        verify_fixture(self.admin.fixture_rows(query, self.deadline))
        for result in ((rows[:-1],), (rows + rows[:1],), (rows, rows[:1])):
            with self.subTest(result_sets=len(result), rows=len(result[0])):
                connection, cursor = self.connection_for(result, has_rows=True)
                with self.assertRaisesRegex(OSError, "could not be confirmed"):
                    self.admin.fixture_rows(query, self.deadline)
                self.assertTrue(connection.closed and cursor.closed)

    def test_exact_existence_result_distinguishes_malformed_responses_from_absence(self):
        for value, expected in ((0, False), (1, True)):
            connection, cursor = self.connection_for((((value,),),), has_rows=True)
            self.assertIs(self.admin.database_exists(self.database, self.deadline), expected)
            self.assertEqual(self.factory.call_args.args[0], "master")
            self.assertIn(f"DB_ID(N'{self.database}')", cursor.executed[0])
            self.assertTrue(connection.closed and cursor.closed)
        for result in (((),), (((False,),),), (((0,),), ((1,),))):
            self.connection_for(result, has_rows=True)
            with self.assertRaisesRegex(OSError, "could not be confirmed"):
                self.admin.database_exists(self.database, self.deadline)

    def test_unexpected_results_and_unconfirmed_closure_prevent_success(self):
        self.connection_for((((1,),),), has_rows=True)
        with self.assertRaisesRegex(OSError, "could not be confirmed"):
            self.admin.execute("master", "SYNTHETIC SETUP", self.deadline)
        connection, cursor = self.connection_for((None,))
        cursor.fail_close = True
        with self.assertRaisesRegex(OSError, "^guest administration could not be confirmed$"):
            self.admin.execute("master", "SYNTHETIC SETUP", self.deadline)
        self.assertTrue(connection.closed)

    def test_non_row_status_results_are_drained_and_late_errors_fail(self):
        self.connection_for((None,))
        cursor = self.factory.return_value.bound_cursor
        cursor.nextset = Mock(side_effect=[True, True, False])
        self.admin.execute("master", "SYNTHETIC SETUP", self.deadline)
        self.assertEqual(cursor.nextset.call_count, 3)

        for outcomes in ((True, OSError("synthetic late error")), (True,) * 32):
            self.connection_for((None,))
            cursor = self.factory.return_value.bound_cursor
            cursor.nextset = Mock(side_effect=outcomes)
            with self.assertRaisesRegex(OSError, "could not be confirmed"):
                self.admin.execute("master", "SYNTHETIC SETUP", self.deadline)
            self.assertTrue(cursor.closed)

    def test_expired_deadline_prevents_opening_a_connection(self):
        with self.assertRaisesRegex(OSError, "could not be confirmed"):
            self.admin.execute("master", "SYNTHETIC SETUP", monotonic() - 1)
        self.factory.assert_not_called()


class OdbcGuestMeasurementTests(unittest.TestCase):
    @staticmethod
    def fresh_connection():
        cursor = Cursor((None,))
        cursor.description = None
        return Connection(cursor)

    def setUp(self):
        self.reader_secret = "Ext9!" + "a" * 32
        self.observer_secret = "Ext9!" + "b" * 32
        self.deadline = monotonic() + 12

    def test_standalone_principal_check_requires_local_scope_and_verified_close(self):
        source = self.fresh_connection()
        opener = Mock(return_value=source)
        verify_guest_principal(TOKEN, Principal.SOURCE_READER, self.reader_secret, self.deadline, opener)
        self.assertTrue(source.closed and source.bound_cursor.closed)
        self.assertIn(principal_name(TOKEN, Principal.SOURCE_READER), source.bound_cursor.executed[0])
        self.assertIn("127.0.0.1", source.bound_cursor.executed[0])

        bad = self.fresh_connection()
        bad.close = Mock(side_effect=OSError("private error"))
        with self.assertRaises(UnconfirmedRequestCleanup):
            verify_guest_principal(TOKEN, Principal.SOURCE_READER, self.reader_secret, self.deadline, Mock(return_value=bad))

    def test_fresh_verified_reader_and_observer_are_used_locally(self):
        observer, reader = self.fresh_connection(), self.fresh_connection()
        opener = Mock(side_effect=[observer, reader])
        expected = MeasurementResult("PASS", "comparison", PUSHDOWN_FILTER_EVIDENCE)

        def compare(transport, token, deadline):
            self.assertEqual((token, deadline), (TOKEN, self.deadline))
            self.assertIs(transport._observer, observer)
            connection = transport._reader(5)
            self.assertIs(connection, reader)
            connection.close()
            return expected

        with patch("external_tables_odbc.measure_pushdown", side_effect=compare):
            self.assertEqual(
                run_guest_measurement(TOKEN, self.reader_secret, self.observer_secret, self.deadline, opener),
                expected,
            )
        self.assertEqual(
            [event.args[:2] for event in opener.call_args_list],
            [(Principal.OBSERVER, self.observer_secret), (Principal.QUERY_READER, self.reader_secret)],
        )
        for principal, connection in ((Principal.OBSERVER, observer), (Principal.QUERY_READER, reader)):
            self.assertTrue(connection.closed and connection.bound_cursor.closed)
            sql = connection.bound_cursor.executed[0]
            self.assertIn(principal_name(TOKEN, principal), sql)
            self.assertIn("127.0.0.1", sql)
            self.assertIn("ORIGINAL_LOGIN()", sql)

    @patch("external_tables_odbc.measure_pushdown", return_value=MeasurementResult("PASS", "comparison", PUSHDOWN_FILTER_EVIDENCE))
    def test_observer_close_failure_suppresses_the_positive_result(self, compare):
        observer = self.fresh_connection()
        observer.close = Mock(side_effect=OSError("driver detail"))
        outcome = run_guest_measurement(
            TOKEN, self.reader_secret, self.observer_secret, self.deadline, Mock(return_value=observer),
        )
        self.assertEqual(outcome, MeasurementResult("FAIL_CLEANUP", "query_connection"))
        compare.assert_called_once()
        observer.close.assert_called_once()

    @patch("external_tables_odbc.measure_pushdown")
    def test_unverified_observer_stops_before_measurement(self, compare):
        observer = self.fresh_connection()
        observer.bound_cursor.nextset = Mock(side_effect=OSError("private driver detail"))
        outcome = run_guest_measurement(
            TOKEN, self.reader_secret, self.observer_secret, self.deadline, Mock(return_value=observer),
        )
        self.assertEqual(outcome, MeasurementResult("NOT_PROVEN", "query_connection"))
        self.assertTrue(observer.closed)
        compare.assert_not_called()


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
        self.assertEqual(len(reader.cursor_timeouts), 2)
        self.assertGreaterEqual(reader.cursor_timeouts[0], reader.cursor_timeouts[1])
        self.assertGreater(reader.cursor_timeouts[1], 0)
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


class DriverError(Exception):
    pass


class SourceTlsTests(unittest.TestCase):
    def setUp(self):
        self.secret = "Ext9!" + "a" * 32
        self.database = database_name(TOKEN, Role.SOURCE)
        self.login = principal_name(TOKEN, Principal.SOURCE_READER)
        self.positive = Connection(Cursor((((self.database, self.login, SOURCE_IP, 1433, QUERY_IP),),)))
        self.driver = Mock(Error=DriverError, pooling=False)

    def test_requires_certificate_name_rejection_at_the_same_endpoint(self):
        self.driver.connect.side_effect = [
            self.positive, DriverError("08001", "SSL Provider: certificate verify failed:subject name does not match host name"),
        ]
        verify_source_tls(self.driver, TOKEN, self.secret, monotonic() + 4, network=NETWORK)
        positive, negative = self.driver.connect.call_args_list
        self.assertEqual(
            negative.args[0],
            positive.args[0].replace("tcp:pbs-test0002,1433", f"tcp:{SOURCE_IP},1433")
            + "HostnameInCertificate=pbn-test0002;",
        )
        self.assertIn("Server=tcp:pbs-test0002,1433;", positive.args[0])
        self.assertIn("Encrypt=Yes;TrustServerCertificate=No;", positive.args[0])
        self.assertGreater(positive.kwargs["timeout"], 0)
        self.assertTrue(self.positive.closed)
        self.assertTrue(self.positive.bound_cursor.closed)

    def test_timeout_or_untrusted_ca_is_not_a_name_rejection(self):
        for state, detail in (
            ("HYT00", "login timeout"),
            ("08001", "SSL Provider: certificate verify failed:unable to get local issuer certificate"),
            ("28000", "login rejected"),
        ):
            with self.subTest(state=state):
                positive = Connection(Cursor((((self.database, self.login, SOURCE_IP, 1433, QUERY_IP),),)))
                self.driver.connect.side_effect = [positive, DriverError(state, detail + self.secret)]
                with self.assertRaisesRegex(OSError, "could not be attributed") as error:
                    verify_source_tls(self.driver, TOKEN, self.secret, monotonic() + 4, network=NETWORK)
                self.assertNotIn(self.secret, str(error.exception))
                self.assertTrue(positive.closed)

    def test_unverified_tcp_address_does_not_receive_a_second_connection(self):
        for address, port, client in (
            (None, 1433, QUERY_IP), ("::1", 1433, QUERY_IP), (WRONG_IP, 1433, QUERY_IP),
            (SOURCE_IP, 1434, QUERY_IP), (str(IPv4Address(0)), 1433, QUERY_IP),
            (SOURCE_IP, 1433, WRONG_IP), (SOURCE_IP, 1433, None),
        ):
            with self.subTest(address=address, port=port):
                self.driver.reset_mock()
                connection = Connection(Cursor((((self.database, self.login, address, port, client),),)))
                self.driver.connect.return_value = connection
                with self.assertRaisesRegex(OSError, "trusted source TLS connection was not confirmed"):
                    verify_source_tls(self.driver, TOKEN, self.secret, monotonic() + 4, network=NETWORK)
                self.driver.connect.assert_called_once()
                self.assertTrue(connection.closed)


    def test_wrong_name_connection_is_closed_and_fails_probe(self):
        negative = Connection(None)
        self.driver.connect.side_effect = [self.positive, negative]
        with self.assertRaisesRegex(ValueError, "accepted the wrong certificate name"):
            verify_source_tls(self.driver, TOKEN, self.secret, monotonic() + 4, network=NETWORK)
        self.assertTrue(negative.closed)
        self.assertTrue(self.positive.closed)

    def test_pooled_driver_and_wrong_endpoint_identity_fail_closed(self):
        self.driver.pooling = True
        with self.assertRaisesRegex(ValueError, "disabled pooling"):
            verify_source_tls(self.driver, TOKEN, self.secret, monotonic() + 4, network=NETWORK)
        self.driver.connect.assert_not_called()
        self.driver.pooling = False
        unexpected = Connection(Cursor(((("master", self.login, SOURCE_IP, 1433, QUERY_IP),),)))
        self.driver.connect.return_value = unexpected
        with self.assertRaisesRegex(OSError, "trusted source TLS connection was not confirmed"):
            verify_source_tls(self.driver, TOKEN, self.secret, monotonic() + 4, network=NETWORK)
        self.driver.connect.assert_called_once()
        self.assertTrue(unexpected.closed)



if __name__ == "__main__":
    unittest.main()
