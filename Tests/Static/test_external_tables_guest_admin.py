from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
import sys
from time import monotonic
import unittest
from unittest.mock import ANY, MagicMock, Mock, patch
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_admin import (
    AdminAction, AdminCommand, _MAX_COMMAND, _COMMAND_HEADER, _receive_command, _send_command, invoke_guest_admin,
    GuestSqlAccess, GuestSqlChannel, invoke_guest_measurement,
)
from external_tables_guest_identity import _QUERY, _REPLY, _REQUEST, _RESPONSE
from external_tables_driver_evidence import DriverEvidence
from external_tables_measurement import MeasurementResult
from external_tables_odbc import OdbcPilotAdministration
from external_tables_pilot_sql import Role, database_name
from external_tables_principals import Principal
from external_tables_pushdown_evidence import PUSHDOWN_FILTER_EVIDENCE


TOKEN = "TEST0011"
PORT = 2762
VM_ID = UUID("9584674e-d3c6-460b-9004-f311fd2a6f0a")
NONCE = bytes(range(16))
DIGEST = bytes(range(32))
SECRET = "Ext9!" + "a" * 32
SID = "b" * 32


class GuestAdminChannelTests(unittest.TestCase):
    def setUp(self):
        self.endpoint = Mock(spec=OdbcPilotAdministration)
        self.deadline = monotonic() + 5

    def round_trip(self, command, role=Role.SOURCE, *, access=None, **capabilities):
        if access is None:
            access = GuestSqlAccess(TOKEN, role)
        left, right = socket.socketpair()
        with left, right, ThreadPoolExecutor(max_workers=1) as executor:
            guest = executor.submit(
                _receive_command, right, TOKEN, role, self.endpoint, self.deadline, access=access, **capabilities,
            )
            try:
                return _send_command(left, command, self.deadline)
            finally:
                guest.result(timeout=3)

    def test_create_and_cleanup_regenerate_sql_for_the_verified_role(self):
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.CREATE_DATABASE)))
        self.endpoint.execute.assert_called_once()
        db, sql, deadline = self.endpoint.execute.call_args.args
        self.assertEqual(db, "master")
        self.assertLessEqual(deadline, self.deadline)
        self.assertIn(f"CREATE DATABASE [{database_name(TOKEN, Role.SOURCE)}]", sql)
        self.endpoint.reset_mock()
        access = GuestSqlAccess(TOKEN, Role.SOURCE)
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.QUIESCE, ("SOURCE_READER", SID)), access=access))
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.DROP_LOGINS, ("SOURCE_READER", SID)), access=access))
        db, sql, _ = self.endpoint.execute.call_args.args
        self.assertEqual(db, "master")
        self.assertIn("0x" + SID.upper(), sql)

    def test_presence_results_are_distinct_from_completion_and_failure(self):
        for expected in (True, False):
            self.endpoint.database_exists.return_value = expected
            self.assertIs(self.round_trip(AdminCommand(AdminAction.DATABASE_EXISTS)), expected)
        self.endpoint.database_exists.assert_called_with(database_name(TOKEN, Role.SOURCE), ANY)
        self.endpoint.database_exists.side_effect = OSError("private driver data")
        with self.assertRaisesRegex(OSError, "^guest administration command was not confirmed$"):
            self.round_trip(AdminCommand(AdminAction.DATABASE_EXISTS))

    def test_expired_work_does_not_use_the_cleanup_window(self):
        access = GuestSqlAccess(TOKEN, Role.SOURCE)
        budget = {"access": access, "work_deadline": monotonic() - 1}
        with self.assertRaises(OSError):
            self.round_trip(AdminCommand(AdminAction.CREATE_DATABASE), **budget)
        self.endpoint.execute.assert_not_called()
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.QUIESCE), **budget))
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.DROP_DATABASE), **budget))
        self.assertEqual(self.endpoint.execute.call_count, 2)

    def test_guest_budget_stays_within_the_shorter_host_window(self):
        left, right = socket.socketpair()
        initial = monotonic()
        with left, right, ThreadPoolExecutor(max_workers=1) as executor:
            guest = executor.submit(
                _receive_command, right, TOKEN, Role.SOURCE, self.endpoint, initial + 60,
                work_deadline=initial + 30, access=GuestSqlAccess(TOKEN, Role.SOURCE),
            )
            self.assertIsNone(_send_command(left, AdminCommand(AdminAction.CREATE_DATABASE), initial + 2))
            guest.result(timeout=3)
        _, _, deadline = self.endpoint.execute.call_args.args
        self.assertGreater(deadline, initial)
        self.assertLess(deadline, initial + 2.2)

    def test_rejects_foreign_operations_and_invalid_fields_before_sql(self):
        for command in (
            AdminCommand(AdminAction.CREATE_STATISTICS),
            AdminCommand(AdminAction.CREATE_DATABASE, ("arbitrary requested payload",)),
            AdminCommand(AdminAction.CREATE_PRINCIPAL, ("QUERY_READER", SECRET, SID)),
            AdminCommand(AdminAction.CREATE_PRINCIPAL, ("SOURCE_READER", SECRET, "0" * 32)),
            AdminCommand(AdminAction.DROP_LOGINS, ("SOURCE_READER", SID, "SOURCE_READER", SID)),
            AdminCommand(AdminAction.VERIFY_FIXTURE, ("PUSHDOWN_ON",)),
        ):
            with self.subTest(command=command), self.assertRaisesRegex(OSError, "was not confirmed"):
                self.round_trip(command)
        self.endpoint.assert_not_called()
        self.assertFalse(self.endpoint.method_calls)

    def test_cleanup_blocks_new_operations_even_before_session_absence_is_confirmed(self):
        access = GuestSqlAccess(TOKEN, Role.SOURCE)
        cleanup = AdminCommand(AdminAction.QUIESCE, ("SOURCE_READER", SID))
        drop = AdminCommand(AdminAction.DROP_DATABASE)
        create = AdminCommand(AdminAction.CREATE_DATABASE)
        with self.assertRaises(OSError):
            self.round_trip(drop, access=access)
        self.endpoint.execute.assert_not_called()
        self.endpoint.execute.side_effect = OSError("recorded session still connected")
        with self.assertRaises(OSError):
            self.round_trip(cleanup, access=access)
        self.endpoint.execute.reset_mock(side_effect=True)
        for command in (create, drop):
            with self.assertRaises(OSError):
                self.round_trip(command, access=access)
        self.endpoint.execute.assert_not_called()
        self.assertIsNone(self.round_trip(cleanup, access=access))
        self.assertIsNone(self.round_trip(drop, access=access))
        with self.assertRaises(OSError):
            self.round_trip(create, access=access)
        self.assertEqual(self.endpoint.execute.call_count, 2)

    @patch("external_tables_guest_admin.invoke_guest_admin")
    def test_host_attempts_both_guests_and_passes_only_their_recorded_sids(self, invoke):
        query_vm = UUID(int=VM_ID.int + 1)
        channel = GuestSqlChannel(TOKEN, VM_ID, query_vm, PORT, b"base", {})
        source_sid, observer_sid = bytes.fromhex(SID), bytes.fromhex("c" * 32)
        invoke.side_effect = [OSError("pending query session"), None]
        self.assertFalse(channel.close_data_connections(
            TOKEN, {Principal.SOURCE_READER: source_sid, Principal.OBSERVER: observer_sid}, self.deadline,
        ))
        first, second = (call.args for call in invoke.call_args_list)
        self.assertEqual((first[0], first[3], first[4].fields), (query_vm, Role.QUERY, ("OBSERVER", observer_sid.hex())))
        self.assertEqual((second[0], second[3], second[4].fields), (VM_ID, Role.SOURCE, ("SOURCE_READER", SID)))

    def test_incomplete_fixture_does_not_return_success_or_any_rows(self):
        self.endpoint.fixture_rows.return_value = ()
        with self.assertRaisesRegex(OSError, "was not confirmed"):
            self.round_trip(AdminCommand(AdminAction.VERIFY_FIXTURE, ("LOCAL",)))
        self.endpoint.fixture_rows.assert_called_once()

    def test_invalid_wire_frames_never_reach_sql(self):
        invalid = (
            _COMMAND_HEADER.pack(1000, _MAX_COMMAND + 1),
            _COMMAND_HEADER.pack(1000, 20) + b"[]",
            _COMMAND_HEADER.pack(1000, 6) + b"[true]",
            _COMMAND_HEADER.pack(1000, 3) + b"SQL",
            _COMMAND_HEADER.pack(0, 20) + b'["create_database"]',
        )
        for wire in invalid:
            left, right = socket.socketpair()
            with left, right, ThreadPoolExecutor(max_workers=1) as executor:
                guest = executor.submit(
                    _receive_command, right, TOKEN, Role.SOURCE, self.endpoint, self.deadline,
                    access=GuestSqlAccess(TOKEN, Role.SOURCE),
                )
                left.sendall(wire)
                left.shutdown(socket.SHUT_WR)
                left.settimeout(2)
                self.assertEqual(left.recv(1), b"\x00")
                guest.result(timeout=3)
        self.assertFalse(self.endpoint.method_calls)

    @patch("external_tables_guest_admin.verify_guest_principal")
    def test_principal_check_uses_only_the_matching_guest(self, probe):
        source = AdminCommand(AdminAction.CHECK_PRINCIPAL, ("SOURCE_READER", SECRET))
        opener = Mock()
        for role, factory in ((Role.QUERY, opener), (Role.SOURCE, None)):
            with self.subTest(role=role), self.assertRaises(OSError):
                self.round_trip(source, role, open_principal=factory)
        probe.assert_not_called()
        self.assertIsNone(self.round_trip(source, Role.SOURCE, open_principal=opener))
        probe.assert_called_once_with(TOKEN, Principal.SOURCE_READER, SECRET, ANY, opener)
        self.assertFalse(self.endpoint.method_calls)

    @patch("external_tables_guest_admin.verify_source_tls")
    def test_tls_check_uses_only_the_query_guest_and_its_preconfigured_network(self, probe):
        command = AdminCommand(AdminAction.CHECK_SOURCE_TLS, (SECRET,))
        driver, network = Mock(), Mock()
        for role, endpoint in ((Role.SOURCE, network), (Role.QUERY, None)):
            with self.subTest(role=role), self.assertRaises(OSError):
                self.round_trip(command, role, source_driver=driver, network=endpoint)
        probe.assert_not_called()
        self.assertIsNone(self.round_trip(command, Role.QUERY, source_driver=driver, network=network))
        probe.assert_called_once_with(driver, TOKEN, SECRET, ANY, network=network)
        probe.side_effect = OSError("private driver message")
        with self.assertRaisesRegex(OSError, "^guest administration command was not confirmed$"):
            self.round_trip(command, Role.QUERY, source_driver=driver, network=network)

    @patch("external_tables_guest_admin.invoke_guest_measurement")
    @patch("external_tables_guest_admin.invoke_guest_admin", return_value=None)
    def test_host_channel_dispatches_to_the_recorded_ids_and_rejects_a_foreign_run(self, invoke, measure):
        query_vm = UUID(int=VM_ID.int + 1)
        package_lock = {}
        channel = GuestSqlChannel(TOKEN, VM_ID, query_vm, PORT, b"base", package_lock)
        channel.probe_principal(Principal.SOURCE_READER, SECRET, self.deadline)
        args = invoke.call_args.args
        self.assertEqual(args[:4], (VM_ID, PORT, TOKEN, Role.SOURCE))
        self.assertEqual(args[4], AdminCommand(AdminAction.CHECK_PRINCIPAL, ("SOURCE_READER", SECRET)))
        channel.verify_source_tls(TOKEN, SECRET, self.deadline)
        args = invoke.call_args.args
        self.assertEqual(args[:4], (query_vm, PORT, TOKEN, Role.QUERY))
        self.assertEqual(args[4], AdminCommand(AdminAction.CHECK_SOURCE_TLS, (SECRET,)))
        with self.assertRaises(ValueError):
            channel.verify_source_tls("TEST1000", SECRET, self.deadline)
        self.assertEqual(invoke.call_count, 2)
        observer = "Ext9!" + "c" * 32
        channel.measure(TOKEN, SECRET, observer, self.deadline)
        measure.assert_called_once_with(
            query_vm, PORT, TOKEN, SECRET, observer, self.deadline, base_status=b"base", package_lock=package_lock,
        )
        with self.assertRaises(ValueError):
            GuestSqlChannel(TOKEN, VM_ID, VM_ID, PORT, b"base", package_lock)

    @patch("external_tables_guest_admin.run_guest_measurement")
    def test_measurement_is_query_only_and_returns_only_fixed_results(self, measure):
        opener = Mock()
        observer = "Ext9!" + "c" * 32
        command = AdminCommand(AdminAction.MEASURE, (SECRET, observer))
        for role, open_principal in ((Role.SOURCE, opener), (Role.QUERY, None)):
            with self.subTest(role=role), self.assertRaises(OSError):
                self.round_trip(command, role, open_principal=open_principal)
        measure.assert_not_called()
        for expected in (
            MeasurementResult(
                "PASS", "comparison", PUSHDOWN_FILTER_EVIDENCE,
                DriverEvidence("mssql-ees.service", "17.0.5065.9-3", "libmsodbcsql-18.5.so.1.1", "f" * 64),
            ),
            MeasurementResult("NOT_PROVEN", "PUSHDOWN_OFF"),
            MeasurementResult("FAIL_CLEANUP", "query_connection"),
        ):
            measure.return_value = expected
            self.assertEqual(self.round_trip(command, Role.QUERY, open_principal=opener), expected)
            measure.assert_called_with(TOKEN, SECRET, observer, ANY, opener, network=None)
        measure.return_value = MeasurementResult("PASS", "comparison", ("unbound filter", "unbound filter"))
        with self.assertRaises(OSError):
            self.round_trip(command, Role.QUERY, open_principal=opener)
        self.assertFalse(self.endpoint.method_calls)

    @patch("external_tables_guest_admin.invoke_guest_admin")
    def test_measurement_host_pins_query_role_and_requires_the_right_response(self, invoke):
        expected = MeasurementResult("NOT_PROVEN", "LOCAL")
        invoke.return_value = expected
        result = invoke_guest_measurement(
            VM_ID, PORT, TOKEN, SECRET, "Ext9!" + "c" * 32, self.deadline, base_status=b"base", package_lock={},
        )
        self.assertEqual(result, expected)
        self.assertIs(invoke.call_args.args[3], Role.QUERY)
        self.assertIs(invoke.call_args.args[4].action, AdminAction.MEASURE)
        invoke.return_value = False
        with self.assertRaises(OSError):
            invoke_guest_measurement(
                VM_ID, PORT, TOKEN, SECRET, "Ext9!" + "c" * 32, self.deadline, base_status=b"base", package_lock={},
            )

    def test_secret_fields_are_sent_only_after_the_same_channel_verifies_package_identity(self):
        channel = MagicMock()
        channel.__enter__.return_value = channel
        command = AdminCommand(AdminAction.CREATE_PRINCIPAL, ("SOURCE_READER", SECRET, SID))
        self.assertNotIn(SECRET, repr(command))
        kwargs = dict(base_status=b"base", package_lock={})
        with (
            patch.object(socket, "AF_HYPERV", 34, create=True),
            patch.object(socket, "HV_PROTOCOL_RAW", 1, create=True),
            patch.object(socket, "socket", return_value=channel),
            patch("external_tables_guest_identity.token_bytes", return_value=NONCE),
            patch("external_tables_guest_identity.expected_package_digest", return_value=DIGEST),
        ):
            channel.recv.return_value = _RESPONSE.pack(_REPLY, TOKEN.encode(), 1, NONCE, b"z" * 32)
            with self.assertRaisesRegex(ValueError, "locked role"):
                invoke_guest_admin(VM_ID, PORT, TOKEN, Role.SOURCE, command, self.deadline, **kwargs)
            challenge = _REQUEST.pack(_QUERY, TOKEN.encode(), 1, NONCE)
            channel.sendall.assert_called_once_with(challenge)
            channel.sendall.reset_mock()
            channel.recv.side_effect = [_RESPONSE.pack(_REPLY, TOKEN.encode(), 1, NONCE, DIGEST), b"\x01"]
            self.assertIsNone(invoke_guest_admin(VM_ID, PORT, TOKEN, Role.SOURCE, command, self.deadline, **kwargs))
            sends = channel.sendall.call_args_list
            self.assertEqual(len(sends), 2)
            self.assertEqual(sends[0].args[0], challenge)
            self.assertIn(SECRET.encode(), sends[1].args[0])


if __name__ == "__main__":
    unittest.main()
