from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
import sys
from time import monotonic
import unittest
from unittest.mock import MagicMock, Mock, patch
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_admin import (
    AdminAction, AdminCommand, _MAX_COMMAND, _SIZE, _receive_command, _send_command, invoke_guest_admin,
)
from external_tables_guest_identity import _QUERY, _REPLY, _REQUEST, _RESPONSE
from external_tables_odbc import OdbcPilotAdministration
from external_tables_pilot_sql import Role, database_name


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

    def round_trip(self, command, role=Role.SOURCE):
        left, right = socket.socketpair()
        with left, right, ThreadPoolExecutor(max_workers=1) as executor:
            guest = executor.submit(_receive_command, right, TOKEN, role, self.endpoint, self.deadline)
            try:
                return _send_command(left, command, self.deadline)
            finally:
                guest.result(timeout=3)

    def test_create_and_cleanup_regenerate_sql_for_the_verified_role(self):
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.CREATE_DATABASE)))
        self.endpoint.execute.assert_called_once()
        db, sql, deadline = self.endpoint.execute.call_args.args
        self.assertEqual((db, deadline), ("master", self.deadline))
        self.assertIn(f"CREATE DATABASE [{database_name(TOKEN, Role.SOURCE)}]", sql)
        self.endpoint.reset_mock()
        self.assertIsNone(self.round_trip(AdminCommand(AdminAction.DROP_LOGINS, ("SOURCE_READER", SID))))
        db, sql, _ = self.endpoint.execute.call_args.args
        self.assertEqual(db, "master")
        self.assertIn("0x" + SID.upper(), sql)

    def test_presence_results_are_distinct_from_completion_and_failure(self):
        for expected in (True, False):
            self.endpoint.database_exists.return_value = expected
            self.assertIs(self.round_trip(AdminCommand(AdminAction.DATABASE_EXISTS)), expected)
        self.endpoint.database_exists.assert_called_with(database_name(TOKEN, Role.SOURCE), self.deadline)
        self.endpoint.database_exists.side_effect = OSError("private driver data")
        with self.assertRaisesRegex(OSError, "^guest administration command was not confirmed$"):
            self.round_trip(AdminCommand(AdminAction.DATABASE_EXISTS))

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

    def test_incomplete_fixture_does_not_return_success_or_any_rows(self):
        self.endpoint.fixture_rows.return_value = ()
        with self.assertRaisesRegex(OSError, "was not confirmed"):
            self.round_trip(AdminCommand(AdminAction.VERIFY_FIXTURE, ("LOCAL",)))
        self.endpoint.fixture_rows.assert_called_once()

    def test_invalid_wire_frames_never_reach_sql(self):
        invalid = (
            _SIZE.pack(_MAX_COMMAND + 1),
            _SIZE.pack(20) + b"[]",
            _SIZE.pack(6) + b"[true]",
            _SIZE.pack(3) + b"SQL",
        )
        for wire in invalid:
            left, right = socket.socketpair()
            with left, right, ThreadPoolExecutor(max_workers=1) as executor:
                guest = executor.submit(_receive_command, right, TOKEN, Role.SOURCE, self.endpoint, self.deadline)
                left.sendall(wire)
                left.shutdown(socket.SHUT_WR)
                left.settimeout(2)
                self.assertEqual(left.recv(1), b"\x00")
                guest.result(timeout=3)
        self.assertFalse(self.endpoint.method_calls)

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
