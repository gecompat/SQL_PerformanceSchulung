from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

from verify_external_tables_ubuntu_base import compare_direct_packages, parse_manifest, verify_archive, verify_manifest


class BaseImageTests(TestCase):
    def test_native_architecture_and_package_aliases(self):
        packages = parse_manifest("libc6:amd64 2.39\nlibc6:i386 2.39\nopenssl 3.0.13\ngdb:arm64 15.1\n")
        result = compare_direct_packages(packages)
        self.assertEqual(result["present"], {"libc6": "2.39", "openssl": "3.0.13"})
        self.assertIn("gdb", result["absent_from_base"])

    def test_rejects_ambiguous_and_invalid_manifest(self):
        for contents in (
            "", "libc6:amd64", "libc6 2.39\nlibc6:amd64 2.39", "libc6 2.39\nlibc6 2.40",
        ):
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                parse_manifest(contents)

    def test_requires_digest_before_using_manifest_or_archive(self):
        manifest = b"openssl 3.0.13\n"
        archive = b"synthetic archive"
        with TemporaryDirectory() as folder:
            source = Path(folder) / "manifest"
            image = Path(folder) / "vhd.tar.gz"
            source.write_bytes(manifest)
            image.write_bytes(archive)
            with patch("verify_external_tables_ubuntu_base.MANIFEST_SHA256", sha256(manifest).hexdigest()):
                self.assertEqual(verify_manifest(source)["present"], {"openssl": "3.0.13"})
                source.write_bytes(manifest + b"gdb 15.1\n")
                with self.assertRaises(ValueError):
                    verify_manifest(source)
            with patch("verify_external_tables_ubuntu_base.ARCHIVE_SHA256", sha256(archive).hexdigest()):
                verify_archive(image)
                image.write_bytes(archive + b"x")
                with self.assertRaises(ValueError):
                    verify_archive(image)

    def test_derived_evidence_respects_disk_cap_and_partition_geometry(self):
        base = Path(__file__).resolve().parents[2] / "Documentation" / "Project_Planning"
        evidence = json.loads((base / "external_tables_vhdx_evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["guest_boot"], "NOT_RUN")
        self.assertEqual(evidence["derived_virtual_bytes"], 24 * 1024**3)
        self.assertGreater(evidence["source_virtual_bytes"], evidence["derived_virtual_bytes"])
        self.assertTrue(evidence["hyper_v_test_vhd"])
        partitions = evidence["partitions_before_and_after"]
        self.assertEqual({entry["number"] for entry in partitions}, {1, 14, 15, 16})
        self.assertEqual(len({entry["uuid"] for entry in partitions}), 4)
        for entry in partitions:
            self.assertLess(
                (entry["first_lba"] + entry["sectors"] + 34) * evidence["logical_sector_bytes"],
                evidence["derived_virtual_bytes"],
            )
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")



if __name__ == "__main__":
    main()
