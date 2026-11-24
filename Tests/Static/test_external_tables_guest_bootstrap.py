from contextlib import contextmanager
from ipaddress import IPv4Interface
from pathlib import Path
import socket
import sys
from tempfile import TemporaryDirectory
from time import monotonic
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

import external_tables_guest_bootstrap as bootstrap
from external_tables_guest_identity import _DETACHED_QUERY, _DETACHED_REPLY, _QUERY, _REQUEST, _RESPONSE, _receive
from external_tables_guest_network import GuestNetwork
from external_tables_package_state import installed_package_digest
from external_tables_pilot_sql import Role


TOKEN = "TEST0089"
PORT = 2760
NETWORK = GuestNetwork(IPv4Interface((0xC0A8FD02, 29)), IPv4Interface((0xC0A8FD03, 29)))
STATUS = b"Package: ubuntu-base\nArchitecture: amd64\nVersion: 1.0\nStatus: install ok installed\n\n"
NONCE = b"q" * 16


class GuestBootstrapTests(unittest.TestCase):
    def run_preparation(self, role, phase, *, fail=None):
        calls = Mock()
        if fail is not None:
            getattr(calls, fail).side_effect = OSError("synthetic failure")
        deadline = monotonic() + 4
        role_id = 1 if role is Role.SOURCE else 2
        left, right = socket.socketpair()

        @contextmanager
        def accept(port, limit):
            self.assertEqual((port, limit), (PORT, deadline))
            calls.accept()
            yield right

        with left, right, TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "status").write_bytes(STATUS)
            left.sendall(_REQUEST.pack(phase, TOKEN.encode(), role_id, NONCE))
            with (
                patch.object(bootstrap, "install_verified_guest_packages", calls.install_packages),
                patch.object(bootstrap, "install_source_firewall", calls.install_firewall),
                patch.object(bootstrap, "verify_source_firewall", calls.verify_firewall),
                patch.object(bootstrap, "require_guest_detached", calls.detached),
                patch("external_tables_guest_identity.accept_parent_connection", accept),
                patch("external_tables_guest_identity._GUEST_STATUS_PATH", path / "status"),
            ):
                args = (TOKEN, role, PORT, NETWORK, path, path, deadline)
                if fail is not None or phase != _DETACHED_QUERY:
                    error = OSError if fail is not None else ValueError
                    message = "synthetic failure" if fail is not None else "configured run"
                    with self.assertRaisesRegex(error, message):
                        bootstrap.prepare_detached_guest(*args)
                    right.close()
                    # A peer that still has an unread request may reset instead of ending cleanly.
                    try:
                        self.assertEqual(left.recv(1), b"")
                    except ConnectionResetError:
                        pass
                else:
                    bootstrap.prepare_detached_guest(*args)
                    expected = _RESPONSE.pack(
                        _DETACHED_REPLY, TOKEN.encode(), role_id, NONCE, installed_package_digest(STATUS),
                    )
                    self.assertEqual(_receive(left, _RESPONSE.size, deadline), expected)
                self.assertEqual(calls.install_packages.call_args.args[2:], (role, deadline))
                self.assertEqual(calls.install_packages.call_args.kwargs, {"wheel_install_dir": path})
                if role is Role.SOURCE and fail != "install_packages":
                    calls.install_firewall.assert_called_once_with(NETWORK, "sqlperf0", deadline)
        return [event[0] for event in calls.mock_calls]

    def test_source_proves_packages_and_firewall_while_detached(self):
        self.assertEqual(
            self.run_preparation(Role.SOURCE, _DETACHED_QUERY),
            ["install_packages", "install_firewall", "accept", "verify_firewall", "detached"],
        )

    def test_query_proves_its_role_inventory_without_source_rules(self):
        self.assertEqual(
            self.run_preparation(Role.QUERY, _DETACHED_QUERY), ["install_packages", "accept", "detached"],
        )

    def test_fails_closed_before_or_during_readiness(self):
        for expected in (
            ["install_packages"],
            ["install_packages", "install_firewall"],
            ["install_packages", "install_firewall", "accept", "verify_firewall"],
            ["install_packages", "install_firewall", "accept", "verify_firewall", "detached"],
        ):
            fail = expected[-1]
            with self.subTest(fail=fail):
                self.assertEqual(self.run_preparation(Role.SOURCE, _DETACHED_QUERY, fail=fail), expected)

    def test_sql_probe_cannot_use_detached_endpoint(self):
        self.assertEqual(
            self.run_preparation(Role.SOURCE, _QUERY), ["install_packages", "install_firewall", "accept"],
        )


if __name__ == "__main__":
    unittest.main()
