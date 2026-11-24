from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr
from io import StringIO
from ipaddress import IPv4Interface
import os
from pathlib import Path
import socket
import sys
from time import monotonic
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, Mock, call, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_admin import AdminAction, AdminCommand, _send_command, serve_guest_admin
from external_tables_guest_identity import _QUERY, _REQUEST, _RESPONSE, _receive
from external_tables_guest_network import GuestNetwork
from external_tables_guest_service import LocalGuestConnections, _configure_engine, main, read_startup_secret, run_guest_engine
from external_tables_odbc import OdbcPilotAdministration
from external_tables_pilot_sql import Role, database_name
from external_tables_principals import Principal


TOKEN = "TEST0041"
SECRET = "Ext9!" + "a" * 32
SID = "b" * 32
PORT = 2762
BASE = b"Package: ubuntu-base\nArchitecture: amd64\nVersion: 1\nStatus: install ok installed\n\n"
ARGV = (
    "--token", TOKEN, "--role", "SOURCE", "--port", str(PORT),
    "--source-address", str(IPv4Interface((0xC0A8FD02, 29))),
    "--query-address", str(IPv4Interface((0xC0A8FD03, 29))), "--wheel-directory", ".",
)


class GuestServiceTests(unittest.TestCase):
    def test_listener_retains_cleanup_state_across_parent_connections(self):
        deadline = monotonic() + 8
        wrong_peer, wrong_guest = socket.socketpair()
        pairs = [socket.socketpair() for _ in range(4)]
        listener = Mock()
        listener.accept.side_effect = [
            (wrong_guest, (17, PORT)), *((guest, (2, PORT)) for _, guest in pairs), TimeoutError(),
        ]
        opened = MagicMock()
        opened.__enter__.return_value = listener, 2
        endpoint = Mock()
        with (
            wrong_peer, wrong_guest,
            patch("external_tables_guest_admin.open_parent_listener", return_value=opened) as bind,
            patch("external_tables_guest_admin.OdbcPilotAdministration", return_value=endpoint),
            patch("external_tables_guest_identity.read_dpkg_status", return_value=BASE),
            ThreadPoolExecutor(max_workers=1) as worker,
        ):
            run = worker.submit(serve_guest_admin, PORT, TOKEN, Role.SOURCE, Mock(), deadline)
            commands = [
                AdminCommand(AdminAction.CREATE_DATABASE),
                AdminCommand(AdminAction.QUIESCE, ("SOURCE_READER", SID)),
                AdminCommand(AdminAction.CREATE_FIXTURE),
                AdminCommand(AdminAction.DROP_DATABASE),
            ]
            try:
                for (host, _), command in zip(pairs, commands, strict=True):
                    host.sendall(_REQUEST.pack(_QUERY, TOKEN.encode(), 1, b"n" * 16))
                    _receive(host, _RESPONSE.size, deadline)
                    if command.action is AdminAction.CREATE_FIXTURE:
                        with self.assertRaises(OSError):
                            _send_command(host, command, deadline)
                    else:
                        self.assertIsNone(_send_command(host, command, deadline))
                run.result(timeout=2)
            finally:
                for host, guest in pairs:
                    host.close()
                    guest.close()
        bind.assert_called_once_with(PORT)
        self.assertEqual(endpoint.execute.call_count, 3)
        self.assertIn("ALTER LOGIN", endpoint.execute.call_args_list[1].args[1])

    def test_connection_factories_use_fixed_loopback_role_and_do_not_expose_driver_errors(self):
        driver = Mock(pooling=False)
        connections = LocalGuestConnections(driver, TOKEN, Role.SOURCE, SECRET)
        connections.principal(Principal.SOURCE_READER, SECRET, 12)
        args, options = driver.connect.call_args
        self.assertIn("Server=tcp:127.0.0.1,1433;", args[0])
        self.assertIn(f"Database={database_name(TOKEN, Role.SOURCE)};", args[0])
        self.assertIn("MARS_Connection=No;ConnectRetryCount=0;", args[0])
        self.assertEqual(options, {"timeout": 12, "autocommit": True})
        for operation in (
            lambda: connections.principal(Principal.OBSERVER, SECRET, 12),
            lambda: connections.admin(database_name(TOKEN, Role.QUERY), 12),
        ):
            with self.assertRaises(ValueError):
                operation()
        driver.connect.assert_called_once()
        driver.connect.side_effect = OSError(SECRET)
        with self.assertRaisesRegex(OSError, "^local guest ODBC connection failed$"):
            connections.admin("master", 12)

    @unittest.skipUnless(os.name == "posix", "requires a Linux input pipe")
    def test_private_pipe_accepts_exactly_one_generated_secret_and_eof(self):
        for payload in (SECRET.encode(), SECRET.encode() + b"extra", b"short"):
            reader, writer = os.pipe()
            try:
                os.write(writer, payload)
            finally:
                os.close(writer)
            try:
                if payload == SECRET.encode():
                    self.assertEqual(read_startup_secret(reader, monotonic() + 2), SECRET)
                else:
                    with self.assertRaisesRegex(ValueError, "^invalid guest startup input$"):
                        read_startup_secret(reader, monotonic() + 2)
            finally:
                os.close(reader)

    def test_owned_engine_opens_service_only_after_engine_profile_check(self):
        network = GuestNetwork(IPv4Interface((0xC0A8FD02, 29)), IPv4Interface((0xC0A8FD03, 29)))
        for invalid in (False, True):
            with self.subTest(invalid=invalid):
                events = Mock()
                events.open.return_value = events.driver, events.connections
                events.connections.admin.side_effect = [OSError("not ready"), events.session]
                events.admin.return_value = events.preflight
                if invalid:
                    events.polybase.side_effect = OSError("wrong engine or unavailable PolyBase")
                deadline = monotonic() + 10
                with (
                    patch("external_tables_guest_service.sys.platform", "linux"),
                    patch.object(os, "geteuid", create=True, return_value=0),
                    patch("external_tables_guest_service.token_hex", return_value="a" * 32),
                    patch("external_tables_guest_service._open_guest_connections", events.open),
                    patch("external_tables_guest_service._configure_engine", events.setup),
                    patch("external_tables_guest_service.sleep"),
                    patch("external_tables_guest_service.OdbcPilotAdministration", events.admin),
                    patch("external_tables_guest_service.verify_polybase_service", events.polybase),
                    patch("external_tables_guest_service.serve_guest_admin", events.serve),
                ):
                    args = (PORT, TOKEN, Role.QUERY, network, Path("wheel"), deadline)
                    if invalid:
                        with self.assertRaisesRegex(OSError, "wrong engine"):
                            run_guest_engine(*args)
                    else:
                        run_guest_engine(*args)
                expected = [
                    call.open(TOKEN, Role.QUERY, network, Path("wheel"), SECRET, deadline),
                    call.setup(SECRET, deadline), call.connections.admin("master", 2),
                    call.connections.admin("master", 2), call.session.close(),
                    call.admin(TOKEN, Role.QUERY, events.connections.admin),
                    call.preflight.prepare_instance(deadline), call.polybase(deadline),
                ]
                if not invalid:
                    expected.append(call.serve(
                        PORT, TOKEN, Role.QUERY, events.connections.admin, deadline + 120,
                        open_principal=events.connections.principal, source_driver=events.driver, network=network,
                    ))
                self.assertEqual(events.mock_calls, expected)

    def test_local_setup_uses_fixed_command_and_does_not_emit_child_output(self):
        result = SimpleNamespace(returncode=1, stderr=SECRET.encode(), stdout=SECRET.encode())
        with patch("external_tables_guest_service.collect_bounded_process", return_value=result) as setup:
            with self.assertRaisesRegex(OSError, "^local SQL engine setup failed$"):
                _configure_engine(SECRET, monotonic() + 4)
        self.assertEqual(setup.call_args.args[0], ["/opt/mssql/bin/mssql-conf", "-n", "setup"])
        self.assertEqual(setup.call_args.kwargs["environment"]["MSSQL_PID"], "EnterpriseDeveloper")
        self.assertEqual(setup.call_args.kwargs["environment"]["MSSQL_SA_PASSWORD"], SECRET)
        self.assertNotIn(SECRET, setup.call_args.args[0])

    def test_only_the_query_role_activates_and_checks_polybase(self):
        for role in Role:
            with self.subTest(role=role):
                cursor = Mock(description=None)
                cursor.nextset.return_value = None
                connection = Mock()
                connection.cursor.return_value = cursor
                admin = OdbcPilotAdministration(TOKEN, role, Mock(return_value=connection))
                admin.prepare_instance(monotonic() + 4)
                batch = cursor.execute.call_args.args[0]
                self.assertIn("CONNECTIONPROPERTY('local_net_address')", batch)
                self.assertIn("SERVERPROPERTY(N'Edition')", batch)
                self.assertEqual("sp_configure N'polybase enabled'" in batch, role is Role.QUERY)
                self.assertEqual("IsPolyBaseInstalled" in batch, role is Role.QUERY)
                self.assertEqual("value_in_use" in batch, role is Role.QUERY)
                connection.close.assert_called_once()

    def test_entrypoint_requires_network_and_pinned_driver_before_listening(self):
        driver = Mock(pooling=False)
        with (
            patch("external_tables_guest_service.sys.platform", "linux"),
            patch("external_tables_guest_service.read_startup_secret", return_value=SECRET) as read_secret,
            patch("external_tables_guest_service.verify_guest_network", return_value="sqlperf0") as verify_network,
            patch("external_tables_guest_service.verify_source_firewall") as verify_firewall,
            patch("external_tables_guest_service.load_pinned_pyodbc", return_value=driver) as load,
            patch("external_tables_guest_service.serve_guest_admin") as serve,
        ):
            self.assertEqual(main(list(ARGV), secret_fd=7), 0)
            self.assertEqual(read_secret.call_args.args[0], 7)
            self.assertEqual(verify_network.call_args.args[1], Role.SOURCE)
            verify_firewall.assert_called_once()
            self.assertEqual(verify_firewall.call_args.args[1], "sqlperf0")
            load.assert_called_once()
            self.assertEqual(serve.call_args.args[:3], (PORT, TOKEN, Role.SOURCE))
            self.assertIsNone(serve.call_args.kwargs["source_driver"])
            serve.reset_mock()
            verify_network.return_value = "unknown"
            with redirect_stderr(StringIO()):
                self.assertEqual(main(list(ARGV), secret_fd=7), 1)
            serve.assert_not_called()
            verify_network.return_value = "sqlperf0"
            verify_firewall.side_effect = OSError(SECRET)
            with redirect_stderr(StringIO()):
                self.assertEqual(main(list(ARGV), secret_fd=7), 1)
            serve.assert_not_called()
            verify_network.side_effect = OSError(SECRET)
            with redirect_stderr(StringIO()) as diagnostic:
                self.assertEqual(main(list(ARGV), secret_fd=7), 1)
            self.assertEqual(diagnostic.getvalue(), "EXTERNAL_TABLES_GUEST_SERVICE|FAIL\n")
            serve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
