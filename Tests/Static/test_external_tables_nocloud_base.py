from hashlib import sha256
from io import BytesIO
from pathlib import Path
from shutil import which
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from prepare_external_tables_nocloud_base import _copy_partition, _set_nocloud


class NoCloudBaseTests(unittest.TestCase):
    def test_partition_transfer_does_not_write_past_recorded_bounds(self):
        target = BytesIO(b"before-end-after")
        target.seek(7)
        _copy_partition(BytesIO(b"new-unused"), target, 3, monotonic() + 2)
        self.assertEqual(target.getvalue(), b"before-new-after")
        with self.assertRaisesRegex(ValueError, "unexpected end"):
            _copy_partition(BytesIO(b"x"), BytesIO(), 2, monotonic() + 2)

    @unittest.skipUnless(sys.platform == "linux" and which("mke2fs"), "requires Linux ext4 tools")
    def test_offline_ext4_preparation_preserves_package_inventory(self):
        package_status = b"Package: ubuntu-base\nArchitecture: amd64\nVersion: 1.0\nStatus: install ok installed\n"
        for digest in (sha256(package_status).hexdigest(), "0" * 64):
            with self.subTest(digest=digest), TemporaryDirectory(prefix="sqlperf-ext4-test-") as name:
                work = Path(name)
                volume = work / "root.ext4"
                tree = work / "tree"
                files = {
                    "etc/cloud/cloud.cfg.d/90_dpkg.cfg": b"datasource_list: [ Azure ]\n",
                    "etc/netplan/90-hotplug-azure.yaml": b"network:\n  dhcp4: true\n",
                    "etc/systemd/system/untouched.service": b"test\n",
                    "var/lib/dpkg/status": package_status,
                }
                for relative, payload in files.items():
                    path = tree / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
                with volume.open("wb") as image:
                    image.truncate(16 * 1024 * 1024)
                subprocess.run(
                    ["mke2fs", "-q", "-F", "-t", "ext4", "-d", tree, volume],
                    capture_output=True, check=True, timeout=10,
                )
                if digest == "0" * 64:
                    with self.assertRaisesRegex(ValueError, "pinned package inventory changed"):
                        _set_nocloud(volume, work, digest, monotonic() + 10)
                else:
                    _set_nocloud(volume, work, digest, monotonic() + 10)
                    self.assertEqual((work / "status").read_bytes(), package_status)


if __name__ == "__main__":
    unittest.main()
