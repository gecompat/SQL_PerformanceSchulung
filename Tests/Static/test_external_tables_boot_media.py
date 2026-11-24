from hashlib import sha256
from ipaddress import IPv4Interface
import json
import os
from pathlib import Path
from shutil import copyfile
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

import external_tables_boot_media as media
from external_tables_guest_network import GuestNetwork
from external_tables_pilot_sql import Role


TOKEN = "TEST0067"
PORT = 2760
NETWORK = GuestNetwork(IPv4Interface((0xC0A8FD02, 29)), IPv4Interface((0xC0A8FD03, 29)))
IMAGE = b"synthetic image"


def file_lock(path):
    payload = path.read_bytes()
    return {"size": len(payload), "sha256": sha256(payload).hexdigest()}


class BootMediaTests(unittest.TestCase):
    def setUp(self):
        work = TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name)
        self.cache = self.root / "packages"
        self.cache.mkdir()
        self.program = self.root / "xorriso"
        self.program.touch()
        extension = b"synthetic extension"
        extension_name = "pyodbc.cpython-312-x86_64-linux-gnu.so"
        wheel = self.cache / "pinned.whl"
        with ZipFile(wheel, "w") as archive:
            archive.writestr(extension_name, extension)
        packages = []
        for name in ("base", "polybase"):
            path = self.cache / f"{name}.deb"
            path.write_bytes(name.encode())
            packages.append({"package": name, "path": f"pool/{path.name}", **file_lock(path)})
        self.repository = self.root / "repository"
        (self.repository / media._LOCK_PATH).parent.mkdir(parents=True)
        (self.repository / media._LOCK_PATH).write_text(json.dumps({
            "packages": packages, "roles": {"source": ["base"], "query": ["base", "polybase"]},
            "python_wheel": {
                "filename": wheel.name, **file_lock(wheel), "installed_extension": {
                    "filename": extension_name, "size": len(extension), "sha256": sha256(extension).hexdigest(),
                },
            },
        }), encoding="utf-8")
        for item in media._GUEST_FILES:
            (self.repository / item).parent.mkdir(parents=True, exist_ok=True)
            copyfile(media._REPOSITORY / item, self.repository / item)

    def test_packaging_keeps_role_packages_and_uses_one_fail_closed_command(self):
        for role in Role:
            with self.subTest(role=role):
                output = self.root / f"{role.value}.iso"

                def compile_iso(command, **options):
                    self.assertEqual(command[:8], [str(self.program), "-as", "mkisofs", "-quiet", "-r", "-J", "-V", "CIDATA"])
                    self.assertLessEqual(options["timeout_seconds"], options["timeout_ceiling_seconds"])
                    seed = Path(command[-1])
                    files = {item.name for item in (seed / "packages").iterdir()}
                    expected = {"base.deb", "pinned.whl"}
                    if role is Role.QUERY:
                        expected.add("polybase.deb")
                    self.assertEqual(files, expected)
                    self.assertEqual(json.loads((seed / "network-config").read_bytes()), {"config": "disabled"})
                    self.assertEqual(
                        json.loads((seed / "meta-data").read_bytes())["instance-id"],
                        f"sqlperf-external-{TOKEN}-{role.value.lower()}",
                    )
                    user = (seed / "user-data").read_text(encoding="utf-8")
                    self.assertTrue(user.startswith("#cloud-config\n"))
                    [action] = json.loads(user.split("\n", 1)[1])["runcmd"]
                    self.assertEqual(action[:2], ["/bin/sh", "-ec"])
                    self.assertIn("ro,nodev,nosuid,noexec LABEL=CIDATA", action[2])
                    self.assertIn(f"--role {role.value} --port {PORT}", action[2])
                    self.assertIn("external_tables_guest_bootstrap.py", action[2])
                    self.assertEqual((seed / media._LOCK_PATH).read_bytes(), (self.repository / media._LOCK_PATH).read_bytes())
                    self.assertEqual(set(path.relative_to(seed) for path in seed.rglob("*.py")), set(media._GUEST_FILES))
                    if role is Role.SOURCE:
                        result = subprocess.run(
                            [sys.executable, "-B", str(seed / media._RUNTIME / "external_tables_guest_bootstrap.py"), "--help"],
                            capture_output=True, cwd=seed, env={**os.environ, "PYTHONPATH": ""}, timeout=10,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                        self.assertIn(b"--wheel-directory", result.stdout)
                    Path(command[-2]).write_bytes(IMAGE)
                    return SimpleNamespace(returncode=0)

                with (
                    patch.object(media, "_REPOSITORY", self.repository),
                    patch.object(media, "collect_bounded_process", side_effect=compile_iso),
                ):
                    digest = media.build_bootstrap_iso(output, self.cache, TOKEN, role, PORT, NETWORK, xorriso=self.program)
                    self.assertEqual(output.read_bytes(), IMAGE)
                    self.assertEqual(digest, sha256(IMAGE).hexdigest())
                    with self.assertRaisesRegex(ValueError, "new ISO"):
                        media.build_bootstrap_iso(output, self.cache, TOKEN, role, PORT, NETWORK, xorriso=self.program)

    def test_wrong_package_prevents_generation_and_publishing(self):
        (self.cache / "base.deb").write_bytes(b"changed")
        output = self.root / "source.iso"
        with (
            patch.object(media, "_REPOSITORY", self.repository),
            patch.object(media, "collect_bounded_process") as compiler,
        ):
            with self.assertRaisesRegex(ValueError, "package bytes differ"):
                media.build_bootstrap_iso(output, self.cache, TOKEN, Role.SOURCE, PORT, NETWORK, xorriso=self.program)
        compiler.assert_not_called()
        self.assertFalse(output.exists())

    def test_compiler_failure_cannot_publish_an_image(self):
        output = self.root / "broken.iso"
        with (
            patch.object(media, "_REPOSITORY", self.repository),
            patch.object(media, "collect_bounded_process", return_value=SimpleNamespace(returncode=1)),
        ):
            with self.assertRaisesRegex(OSError, "could not be confirmed"):
                media.build_bootstrap_iso(output, self.cache, TOKEN, Role.QUERY, PORT, NETWORK, xorriso=self.program)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
