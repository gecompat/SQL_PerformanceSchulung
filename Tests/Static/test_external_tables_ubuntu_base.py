from __future__ import annotations

from hashlib import sha256
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


if __name__ == "__main__":
    main()
