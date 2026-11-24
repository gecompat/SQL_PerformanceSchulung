from hashlib import sha512
from io import BytesIO
from pathlib import Path
import sys
from tarfile import TarInfo, open as open_tar
from tempfile import TemporaryDirectory
from time import monotonic
import unittest
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

import external_tables_polybase_service as polybase


class PolyBaseServiceTests(unittest.TestCase):
    def test_sdk_extraction_verifies_exact_payload_and_runtime_inventory(self):
        for case in ("correct", "hash", "runtime", "escape"):
            with self.subTest(case=case), TemporaryDirectory(prefix="sqlperf-sdk-test-") as name:
                staging = Path(name)
                archive = staging / "sdk.tar.gz"
                destination = staging / "installed"
                binary = b"synthetic executable"
                path = "../outside" if case == "escape" else "dotnet"
                member = TarInfo(path)
                member.size = len(binary)
                member.mode = 0o755
                with open_tar(archive, "w:gz") as packed:
                    packed.addfile(member, BytesIO(binary))
                entry = {
                    "filename": archive.name, "size": archive.stat().st_size,
                    "sha512": "0" * 128 if case == "hash" else sha512(archive.read_bytes()).hexdigest(),
                    "sdk_version": "8.0.418", "runtime_version": "8.0.24",
                }
                sdk = f"8.0.418 [{destination / 'sdk'}]\n".encode()
                runtimes = f"Microsoft.NETCore.App 8.0.24 [{destination / 'shared' / 'Microsoft.NETCore.App'}]\n"
                if case != "runtime":
                    runtimes += f"Microsoft.AspNetCore.App 8.0.24 [{destination / 'shared' / 'Microsoft.AspNetCore.App'}]\n"
                with patch.object(polybase, "_command", side_effect=[sdk, runtimes.encode()]) as command:
                    deadline = monotonic() + 5
                    if case == "correct":
                        polybase.verify_dotnet_archive(archive, entry)
                        polybase.install_dotnet_sdk(staging, entry, deadline, destination=destination)
                        self.assertEqual((destination / "dotnet").read_bytes(), binary)
                        self.assertEqual([item.args for item in command.call_args_list], [
                            ([str(destination / "dotnet"), "--list-sdks"], deadline),
                            ([str(destination / "dotnet"), "--list-runtimes"], deadline),
                        ])
                    else:
                        with self.assertRaises(ValueError):
                            polybase.install_dotnet_sdk(staging, entry, deadline, destination=destination)
                        if case != "runtime":
                            command.assert_not_called()
                        if case == "hash":
                            self.assertFalse(destination.exists())
                        self.assertFalse((staging / "outside").exists())

    def test_readiness_checks_service_process_and_loopback_before_sql(self):
        binary = MagicMock(spec=Path)
        process = MagicMock(spec=Path)
        binary.__truediv__.return_value.resolve.return_value = Path("/fake/dotnet")
        process.__truediv__.return_value.__truediv__.return_value.resolve.return_value = Path("/fake/dotnet")
        for end_pid in (b"123\n", b"124\n"):
            with (
                self.subTest(end_pid=end_pid),
                patch.object(polybase, "_DOTNET_HOME", binary),
                patch.object(polybase, "_PROC_ROOT", process),
                patch.object(polybase, "_command", side_effect=[b"", b"", b"123\n", end_pid]) as command,
                patch.object(polybase.socket, "create_connection") as connect,
            ):
                deadline = monotonic() + 4
                if end_pid == b"123\n":
                    polybase.verify_polybase_service(deadline)
                else:
                    with self.assertRaisesRegex(ValueError, "changed during"):
                        polybase.verify_polybase_service(deadline)
                self.assertEqual(command.call_args_list[:2], [
                    call(["/usr/bin/systemctl", "start", "mssql-ees.service"], deadline),
                    call(["/usr/bin/systemctl", "is-active", "--quiet", "mssql-ees.service"], deadline),
                ])
                self.assertEqual(connect.call_args.args[0], ("127.0.0.1", 25100))


if __name__ == "__main__":
    unittest.main()
