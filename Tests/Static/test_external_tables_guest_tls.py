from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from hashlib import sha256
from ipaddress import IPv4Interface
from pathlib import Path
from shutil import which
import socket
import sys
from tempfile import TemporaryDirectory
from time import monotonic
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

import external_tables_guest_tls as tls
from external_tables_guest_identity import GuestPhase, _reply_to_probe, linux_service_id
from external_tables_guest_network import GuestNetwork
from external_tables_pilot_sql import Role, source_host
from external_tables_tls_material import issue_source_tls


TOKEN = "TEST0193"
PORT = 2763
NETWORK = GuestNetwork(IPv4Interface((0xC0A8FD02, 29)), IPv4Interface((0xC0A8FD03, 29)))
STATUS = b"Package: ubuntu-base\nArchitecture: amd64\nVersion: 1\nStatus: install ok installed\n\n"
LOCK = {"dpkg_status_sha256": sha256(STATUS).hexdigest(), "roles": {"source": [], "query": []}, "packages": []}


class GuestTlsTests(unittest.TestCase):
    def test_rejects_oversized_frames_and_non_certificate_payloads(self):
        left, right = socket.socketpair()
        with left, right:
            left.sendall(tls._FRAME.pack(tls._CERT, tls._PUBLIC_CA_LIMIT + 1))
            with self.assertRaisesRegex(ValueError, "unexpected public CA frame"):
                tls._receive_ca(right, monotonic() + 3)
            with self.assertRaisesRegex(ValueError, "one bounded public CA"):
                tls._send_ca(left, b"not a public certificate", monotonic() + 3)

    @unittest.skipUnless(sys.platform == "linux" and which("openssl"), "requires OpenSSL on Linux")
    def test_actual_ca_is_relayed_between_role_proofs_and_acknowledged_after_install(self):
        source_vm, query_vm = uuid4(), uuid4()
        deadline = monotonic() + 12
        with TemporaryDirectory(prefix="sqlperf-ca-relay-") as name:
            root = Path(name)
            status = root / "status"
            status.write_bytes(STATUS)
            with issue_source_tls(TOKEN, root, deadline) as material:
                certificate = material.ca_certificate
            for fail in (False, True):
                with self.subTest(fail=fail), ThreadPoolExecutor(max_workers=2) as executor:
                    source_host_socket, source_guest_socket = socket.socketpair()
                    query_host_socket, query_guest_socket = socket.socketpair()
                    sockets = {str(source_vm): source_host_socket, str(query_vm): query_host_socket}
                    ordered = []
                    installer = Mock(side_effect=ValueError("synthetic trust installation failure") if fail else None)

                    @contextmanager
                    def connect(family, protocol, endpoint, bound, wait):
                        vm, service = endpoint
                        self.assertEqual(service, str(linux_service_id(PORT)))
                        self.assertEqual(bound, deadline)
                        self.assertTrue(wait)
                        ordered.append(vm)
                        with sockets[vm] as channel:
                            yield channel

                    def send_from_source():
                        with source_guest_socket as channel:
                            _reply_to_probe(channel, TOKEN, Role.SOURCE, deadline, phase=GuestPhase.TLS)
                            tls._send_ca(channel, certificate, deadline)

                    def receive_on_query():
                        with query_guest_socket as channel:
                            tls._receive_query_trust(channel, TOKEN, deadline, installer)

                    with (
                        patch.object(socket, "AF_HYPERV", 34, create=True),
                        patch.object(socket, "HV_PROTOCOL_RAW", 1, create=True),
                        patch("external_tables_guest_identity._connect_hyperv", connect),
                        patch("external_tables_guest_identity._GUEST_STATUS_PATH", status),
                    ):
                        source_job = executor.submit(send_from_source)
                        query_job = executor.submit(receive_on_query)
                        arguments = (source_vm, query_vm, PORT, TOKEN, deadline)
                        if fail:
                            with self.assertRaises(OSError):
                                tls.relay_guest_ca(*arguments, base_status=STATUS, package_lock=LOCK)
                            with self.assertRaisesRegex(ValueError, "trust installation failure"):
                                query_job.result(timeout=3)
                        else:
                            tls.relay_guest_ca(*arguments, base_status=STATUS, package_lock=LOCK)
                            query_job.result(timeout=3)
                        source_job.result(timeout=3)
                    installer.assert_called_once_with(certificate)
                    self.assertEqual(ordered, list(sockets))

    @unittest.skipUnless(sys.platform == "linux" and which("openssl"), "requires OpenSSL on Linux")
    def test_source_keeps_the_private_key_in_the_sql_account_directory(self):
        account = SimpleNamespace(pw_uid=30001, pw_gid=30002)
        with TemporaryDirectory(prefix="sqlperf-source-config-") as name:
            root = Path(name)
            with (
                patch.object(tls, "_SQL_DIRECTORY", root),
                patch("pwd.getpwnam", return_value=account),
                patch.object(tls.os, "chown") as chown,
                patch.object(tls, "_run_linux") as linux,
            ):
                deadline = monotonic() + 12
                certificate = tls._configure_source_tls(TOKEN, deadline)
            tls._validate_pem(certificate)
            directory = root / f"{source_host(TOKEN)}-tls"
            leaf, key = directory / "source.crt", directory / "source.key"
            self.assertEqual(set(directory.iterdir()), {leaf, key})
            self.assertEqual(key.stat().st_mode & 0o777, 0o400)
            left, right = socket.socketpair()
            with left, right, self.assertRaisesRegex(ValueError, "one bounded public CA"):
                tls._send_ca(left, key.read_bytes(), deadline)
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
            self.assertEqual(chown.call_args_list, [call(path, 30001, 30002) for path in (leaf, key, directory)])
            self.assertEqual([item.args[0][2:] for item in linux.call_args_list], [
                ["network.tlscert", str(leaf)], ["network.tlskey", str(key)], ["network.forceencryption", "1"],
            ])

    @unittest.skipUnless(
        sys.platform == "linux" and which("openssl") and which("update-ca-certificates"),
        "requires Linux trust store tools",
    )
    def test_query_store_accepts_only_the_expected_run_ca_and_source_address(self):
        deadline = monotonic() + 12
        host = source_host(TOKEN)
        with TemporaryDirectory(prefix="sqlperf-ca-store-") as name:
            root = Path(name)
            with issue_source_tls(TOKEN, root, deadline) as pair:
                certificate = pair.ca_certificate
                leaf = pair.certificate.read_bytes()
            local_ca = root / "store"
            local_ca.mkdir()
            hosts = root / "hosts"
            hosts.write_text("127.0.0.1 localhost\n", encoding="ascii")
            source_address = str(NETWORK.source.ip)
            getent_output = f"{source_address} STREAM {host}\n".encode()
            paths = {name: root / name for name in ("system-ca", "bundle", "hooks")}
            for path in paths.values():
                path.mkdir()
            config = root / "certs.conf"
            config.touch()
            run_linux = tls._run_linux

            def run_with_private_store(command, bound):
                if command[0].endswith("update-ca-certificates"):
                    return run_linux([
                        *command, "--certsconf", str(config), "--certsdir", str(paths["system-ca"]),
                        "--localcertsdir", str(local_ca), "--etccertsdir", str(paths["bundle"]),
                        "--hooksdir", str(paths["hooks"]),
                    ], bound)
                return getent_output

            with (
                patch.object(tls, "_CA_DIRECTORY", local_ca),
                patch.object(tls, "_HOSTS", hosts),
                patch.object(tls, "_run_linux", side_effect=run_with_private_store) as linux,
            ):
                for token, payload in (("TEST0247", certificate), (TOKEN, leaf)):
                    with self.subTest(token=token), self.assertRaisesRegex(ValueError, "does not match"):
                        tls._install_query_trust(token, NETWORK, payload, deadline)
                linux.assert_not_called()
                tls._install_query_trust(TOKEN, NETWORK, certificate, deadline)
            self.assertEqual((local_ca / f"{host}.crt").read_bytes(), certificate)
            self.assertEqual((paths["bundle"] / "ca-certificates.crt").read_bytes(), certificate)
            self.assertIn(f"\n{source_address} {host}\n", hosts.read_text(encoding="ascii"))
            self.assertEqual([item.args[0] for item in linux.call_args_list], [
                ["/usr/sbin/update-ca-certificates"], ["/usr/bin/getent", "ahostsv4", host],
            ])


if __name__ == "__main__":
    unittest.main()
