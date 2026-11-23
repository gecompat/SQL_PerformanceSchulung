from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
import ssl
from stat import S_IMODE
import sys
from tempfile import TemporaryDirectory
from time import monotonic
from unittest import TestCase, main, skipUnless
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_pilot_sql import source_host
from external_tables_tls_material import issue_source_tls


TOKEN = "TLS00001"


class SourceTlsMaterialTests(TestCase):
    def test_partial_issue_cleans_its_private_files(self):
        def fail_after_first_write(args, _deadline):
            Path(args[args.index("-keyout") + 1]).write_bytes(b"partial synthetic key")
            raise OSError("synthetic issuer failure")

        with TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("external_tables_tls_material._openssl", side_effect=fail_after_first_write):
                with self.assertRaisesRegex(OSError, "synthetic issuer failure"):
                    with issue_source_tls(TOKEN, root, monotonic() + 3):
                        self.fail("partially issued material was returned")
            self.assertEqual(list(root.iterdir()), [])

    @skipUnless(sys.platform == "linux" and Path("/usr/bin/openssl").is_file(), "requires Linux OpenSSL")
    def test_native_tls_accepts_the_run_name_and_rejects_other_identities(self):
        with TemporaryDirectory() as directory, ThreadPoolExecutor(max_workers=1) as worker:
            root = Path(directory)
            with issue_source_tls(TOKEN, root, monotonic() + 30) as material:
                work = material.private_key.parent
                self.assertEqual({entry.name for entry in work.iterdir()}, {"source.crt", "source.key"})
                self.assertEqual(S_IMODE(material.private_key.stat().st_mode), 0o400)
                self.assertTrue(material.ca_certificate.startswith(b"-----BEGIN CERTIFICATE-----"))
                server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                server.load_cert_chain(material.certificate, material.private_key)
                client = ssl.create_default_context(cadata=material.ca_certificate.decode("ascii"))

                def reply(channel):
                    try:
                        with server.wrap_socket(channel, server_side=True) as tls:
                            tls.sendall(b"ok")
                    except ssl.SSLError:
                        # The client aborts the handshake after a failed certificate check.
                        pass

                for host in (source_host(TOKEN), source_host("TLS00002"), "127.0.0.1"):
                    with self.subTest(host=host):
                        left, right = socket.socketpair()
                        with left, right:
                            left.settimeout(3)
                            right.settimeout(3)
                            completed = worker.submit(reply, right)
                            if host == source_host(TOKEN):
                                with client.wrap_socket(left, server_hostname=host) as tls:
                                    self.assertEqual(tls.recv(16), b"ok")
                            else:
                                with self.assertRaises(ssl.SSLCertVerificationError):
                                    client.wrap_socket(left, server_hostname=host)
                            completed.result(timeout=4)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    main()
