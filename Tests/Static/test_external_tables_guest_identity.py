from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
import sys
from time import monotonic
import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_identity import (
    _PACKET, _QUERY, _REPLY, _receive, _reply_to_probe, linux_service_id, serve_guest_identity, verify_guest,
)
from external_tables_pilot_sql import Role


VM_ID = UUID("9584674e-d3c6-460b-9004-f311fd2a6f0a")
TOKEN = "TEST0007"
PORT = 2761
NONCE = b"a" * 16


class GuestIdentityTests(unittest.TestCase):
    def test_service_guid_and_nonprivileged_port_validation(self):
        self.assertEqual(str(linux_service_id(PORT)), "00000ac9-facb-11e6-bd58-64006a7986d3")
        for invalid in (True, 22, 65536, "2761"):
            with self.subTest(port=invalid), self.assertRaises(ValueError):
                linux_service_id(invalid)

    def test_guest_reads_fragmented_probe_and_returns_correlated_identity(self):
        deadline = monotonic() + 4
        request = _PACKET.pack(_QUERY, TOKEN.encode(), 1, NONCE)
        left, right = socket.socketpair()
        with left, right, ThreadPoolExecutor(max_workers=1) as worker:
            fragmented = MagicMock(wraps=right)
            fragmented.recv.side_effect = lambda length: right.recv(min(7, length))
            response = worker.submit(_reply_to_probe, fragmented, TOKEN, Role.SOURCE, deadline)
            left.sendall(request)
            self.assertEqual(_receive(left, deadline), _PACKET.pack(_REPLY, TOKEN.encode(), 1, NONCE))
            response.result(timeout=2)
            self.assertGreater(fragmented.recv.call_count, 1)

    def test_wrong_role_or_run_marker_is_refused(self):
        for token, role in ((b"OLD00007", 1), (TOKEN.encode(), 2)):
            with self.subTest(token=token, role=role):
                left, right = socket.socketpair()
                with left, right:
                    left.sendall(_PACKET.pack(_QUERY, token, role, NONCE))
                    with self.assertRaisesRegex(ValueError, "configured run"):
                        _reply_to_probe(right, TOKEN, Role.SOURCE, monotonic() + 2)

    def test_short_frame_and_expired_deadline_fail_without_an_identity(self):
        left, right = socket.socketpair()
        with left, right:
            with self.assertRaises(TimeoutError):
                _receive(left, monotonic() - 1)
            right.sendall(b"short")
            right.shutdown(socket.SHUT_WR)
            with self.assertRaisesRegex(OSError, "closed before"):
                _receive(left, monotonic() + 2)

    def test_host_binds_exact_vm_and_rejects_a_stale_nonce(self):
        channel = MagicMock()
        channel.__enter__.return_value = channel
        channel.recv.return_value = _PACKET.pack(_REPLY, TOKEN.encode(), 1, b"b" * 16)
        with (
            patch.object(socket, "AF_HYPERV", 34, create=True),
            patch.object(socket, "HV_PROTOCOL_RAW", 1, create=True),
            patch.object(socket, "socket", return_value=channel) as factory,
            patch("external_tables_guest_identity.token_bytes", return_value=NONCE),
        ):
            with self.assertRaisesRegex(ValueError, "current probe"):
                verify_guest(VM_ID, PORT, TOKEN, Role.SOURCE, monotonic() + 4)
            with self.assertRaisesRegex(ValueError, "exact Hyper-V guest ID"):
                verify_guest(UUID(int=0), PORT, TOKEN, Role.SOURCE, monotonic() + 4)
            factory.assert_called_once_with(34, socket.SOCK_STREAM, 1)
        channel.connect.assert_called_once_with((str(VM_ID), str(linux_service_id(PORT))))
        channel.sendall.assert_called_once_with(_PACKET.pack(_QUERY, TOKEN.encode(), 1, NONCE))

    def test_guest_refuses_non_parent_peer_before_receiving(self):
        listener, channel = MagicMock(), MagicMock()
        listener.__enter__.return_value = listener
        channel.__enter__.return_value = channel
        listener.accept.return_value = (channel, (3, PORT))
        with (
            patch.object(socket, "AF_VSOCK", 40, create=True),
            patch.object(socket, "VMADDR_CID_ANY", 0xFFFFFFFF, create=True),
            patch.object(socket, "VMADDR_CID_HOST", 2, create=True),
            patch.object(socket, "socket", return_value=listener),
        ):
            with self.assertRaisesRegex(ValueError, "did not come from the parent"):
                serve_guest_identity(PORT, TOKEN, Role.SOURCE, monotonic() + 4)
        channel.recv.assert_not_called()


if __name__ == "__main__":
    unittest.main()
