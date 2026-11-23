from __future__ import annotations

from hashlib import sha256
from unittest import TestCase, main

from verify_external_tables_packages import INDEX_PATH, PACKAGES, VERSION, check_signed_index


def package_record(package) -> str:
    return "\n".join((
        f"Package: {package.name}", f"Version: {VERSION}", "Architecture: amd64",
        f"Filename: pool/main/m/{package.name}/{package.filename}",
        f"Size: {package.size}", f"SHA256: {package.digest}",
    ))


def release(index: bytes) -> str:
    return f"Suite: noble\nCodename: noble\nSHA256:\n {sha256(index).hexdigest()} {len(index)} {INDEX_PATH}\n"


INDEX = "\n\n".join(package_record(package) for package in PACKAGES).encode()


class ExternalTablesPackageTests(TestCase):
    def test_accepts_exact_index_and_both_package_records(self):
        check_signed_index(release(INDEX), INDEX)

    def test_rejects_wrong_signed_scope_or_index_bytes(self):
        for metadata in (
            release(INDEX).replace("Codename: noble", "Codename: jammy"),
            release(INDEX).replace(INDEX_PATH, "main/binary-arm64/Packages"),
            release(INDEX).replace(str(len(INDEX)), "0"),
            release(INDEX) + release(INDEX).split("SHA256:\n")[1],
        ):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                check_signed_index(metadata, INDEX)
        with self.assertRaises(ValueError):
            check_signed_index(release(INDEX), INDEX + b"x")

    def test_signed_metadata_must_still_match_fixed_package_pins(self):
        for candidate in (
            package_record(PACKAGES[0]).encode(),
            INDEX + b"\n\n" + package_record(PACKAGES[0]).encode(),
            INDEX.replace(b"Architecture: amd64", b"Architecture: arm64"),
            INDEX.replace(PACKAGES[0].digest.encode(), b"0" * 64),
            INDEX.replace(b"_amd64.deb", b"_unexpected.deb"),
        ):
            with self.subTest(candidate=candidate[:38]), self.assertRaises(ValueError):
                check_signed_index(release(candidate), candidate)


if __name__ == "__main__":
    main()
