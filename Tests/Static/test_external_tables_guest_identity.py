from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import socket
import sys
from tempfile import TemporaryDirectory
from time import monotonic
import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_identity import (
    _DETACHED_QUERY, _DETACHED_REPLY, _REQUEST, _RESPONSE, _QUERY, _REPLY, _receive, _reply_to_probe,
    linux_service_id, serve_guest_identity, verify_guest,
)
from external_tables_package_state import installed_package_digest
from external_tables_pilot_sql import Role


VM_ID = UUID("9584674e-d3c6-460b-9004-f311fd2a6f0a")
TOKEN = "TEST0007"
PORT = 2761
NONCE = b"a" * 16
BASE_STATUS = b"Package: ubuntu-base\nArchitecture: amd64\nVersion: 1.0\nStatus: install ok installed\n\n"
QUERY_PACKAGE = b"Package: polybase\nArchitecture: amd64\nVersion: 2.0\nStatus: install ok installed\n\n"
PACKAGE_LOCK = {
    "dpkg_status_sha256": sha256(BASE_STATUS).hexdigest(),
    "roles": {"source": [], "query": ["polybase"]},
    "packages": [{"package": "polybase", "architecture": "amd64", "version": "2.0"}],
}
SOURCE_DIGEST = installed_package_digest(BASE_STATUS)


class GuestIdentityTests(unittest.TestCase):
    def test_service_guid_and_nonprivileged_port_validation(self):
        self.assertEqual(str(linux_service_id(PORT)), "00000ac9-facb-11e6-bd58-64006a7986d3")
        for invalid in (True, 22, 65536, "2761"):
            with self.subTest(port=invalid), self.assertRaises(ValueError):
                linux_service_id(invalid)

    def test_guest_reads_fragmented_probe_and_returns_correlated_identity(self):
        deadline = monotonic() + 4
        request = _REQUEST.pack(_QUERY, TOKEN.encode(), 1, NONCE)
        left, right = socket.socketpair()
        with left, right, TemporaryDirectory() as directory, ThreadPoolExecutor(max_workers=1) as worker:
            status_path = Path(directory) / "status"
            status_path.write_bytes(BASE_STATUS)
            fragmented = MagicMock(wraps=right)
            fragmented.recv.side_effect = lambda length: right.recv(min(7, length))
            with patch("external_tables_guest_identity._GUEST_STATUS_PATH", status_path):
                response = worker.submit(_reply_to_probe, fragmented, TOKEN, Role.SOURCE, deadline)
                left.sendall(request)
                expected = _RESPONSE.pack(_REPLY, TOKEN.encode(), 1, NONCE, SOURCE_DIGEST)
                self.assertEqual(_receive(left, _RESPONSE.size, deadline), expected)
                response.result(timeout=2)
            self.assertGreater(fragmented.recv.call_count, 1)

    def test_wrong_role_or_run_marker_is_refused(self):
        for token, role in ((b"OLD00007", 1), (TOKEN.encode(), 2)):
            with self.subTest(token=token, role=role):
                left, right = socket.socketpair()
                with left, right:
                    left.sendall(_REQUEST.pack(_QUERY, token, role, NONCE))
                    with self.assertRaisesRegex(ValueError, "configured run"):
                        _reply_to_probe(right, TOKEN, Role.SOURCE, monotonic() + 2)

    def test_short_frame_and_expired_deadline_fail_without_an_identity(self):
        left, right = socket.socketpair()
        with left, right:
            with self.assertRaises(TimeoutError):
                _receive(left, _REQUEST.size, monotonic() - 1)
            right.sendall(b"short")
            right.shutdown(socket.SHUT_WR)
            with self.assertRaisesRegex(OSError, "closed before"):
                _receive(left, _REQUEST.size, monotonic() + 2)

    def test_host_binds_exact_vm_nonce_base_and_role_specific_inventory(self):
        channel = MagicMock()
        channel.__enter__.return_value = channel

        with (
            patch.object(socket, "AF_HYPERV", 34, create=True),
            patch.object(socket, "HV_PROTOCOL_RAW", 1, create=True),
            patch.object(socket, "socket", return_value=channel) as factory,
            patch("external_tables_guest_identity.token_bytes", return_value=NONCE),
        ):
            def probe(vm_id=VM_ID, base_status=BASE_STATUS, role=Role.SOURCE, *, detached=False):
                verify_guest(vm_id, PORT, TOKEN, role, monotonic() + 4,
                             base_status=base_status, package_lock=PACKAGE_LOCK, detached=detached)

            with self.assertRaisesRegex(ValueError, "exact Hyper-V guest ID"):
                probe(UUID(int=0))
            with self.assertRaisesRegex(ValueError, "pinned image"):
                probe(base_status=BASE_STATUS + b"\n")
            factory.assert_not_called()

            channel.recv.return_value = _RESPONSE.pack(_REPLY, TOKEN.encode(), 1, NONCE, SOURCE_DIGEST)
            probe()
            channel.connect.assert_called_once_with((str(VM_ID), str(linux_service_id(PORT))))
            channel.sendall.assert_called_once_with(_REQUEST.pack(_QUERY, TOKEN.encode(), 1, NONCE))

            channel.recv.return_value = _RESPONSE.pack(_REPLY, TOKEN.encode(), 1, b"b" * 16, SOURCE_DIGEST)
            with self.assertRaisesRegex(ValueError, "current probe"):
                probe()
            channel.recv.return_value = _RESPONSE.pack(_REPLY, TOKEN.encode(), 2, NONCE, SOURCE_DIGEST)
            with self.assertRaisesRegex(ValueError, "locked role"):
                probe(role=Role.QUERY)
            query_digest = installed_package_digest(BASE_STATUS + QUERY_PACKAGE)
            channel.recv.return_value = _RESPONSE.pack(_REPLY, TOKEN.encode(), 2, NONCE, query_digest)
            probe(role=Role.QUERY)

            channel.recv.return_value = _RESPONSE.pack(_REPLY, TOKEN.encode(), 1, NONCE, SOURCE_DIGEST)
            with self.assertRaisesRegex(ValueError, "current probe"):
                probe(detached=True)
            channel.sendall.assert_called_with(_REQUEST.pack(_DETACHED_QUERY, TOKEN.encode(), 1, NONCE))
            channel.recv.return_value = _RESPONSE.pack(_DETACHED_REPLY, TOKEN.encode(), 1, NONCE, SOURCE_DIGEST)
            with self.assertRaisesRegex(ValueError, "current probe"):
                probe()
            probe(detached=True)

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
