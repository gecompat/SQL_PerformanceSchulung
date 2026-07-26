#!/usr/bin/env python3
"""Synthetic self-tests for validate_privacy_metadata.py."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

MODULE_PATH = Path(__file__).with_name("validate_privacy_metadata.py")
SPEC = importlib.util.spec_from_file_location("privacy_scanner", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
privacy_scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(privacy_scanner)


class PrivacyScannerTests(unittest.TestCase):
    def scan(self, root: Path):
        scanner = privacy_scanner.Scanner(root)
        scanner.scan()
        return scanner

    def categories(self, scanner) -> set[str]:
        return {finding.category for finding in scanner.findings}

    def test_clean_text_and_placeholders_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "clean.md").write_text(
                "Öffentliche Dokumentation unter https://learn.microsoft.com/ und "
                "Password=<LOCAL_SECRET> sowie person@example.com.",
                encoding="utf-8",
            )
            scanner = self.scan(root)
            self.assertFalse(scanner.findings)

    def test_sensitive_values_are_categorized_but_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            email = "real.user" + "@" + "private.invalid-domain.at"
            token = "ghp_" + "A" * 36
            private_ip = "10." + "12.34.56"
            (root / "finding.txt").write_text(
                f"Kontakt {email}; Token {token}; Server {private_ip}",
                encoding="utf-8",
            )
            scanner = self.scan(root)
            categories = self.categories(scanner)
            self.assertIn("email_address", categories)
            self.assertIn("github_token", categories)
            self.assertIn("private_ip_address", categories)

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = scanner.report()
            report = output.getvalue()
            self.assertEqual(1, exit_code)
            self.assertNotIn(email, report)
            self.assertNotIn(token, report)
            self.assertNotIn(private_ip, report)
            self.assertIn("Matched values are intentionally omitted", report)

    def test_office_metadata_macro_and_media_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "sample.pptx"
            metadata_value = "Other Person"
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr(
                    "docProps/core.xml",
                    "<?xml version='1.0' encoding='UTF-8'?>"
                    "<cp:coreProperties "
                    "xmlns:cp='http://schemas.openxmlformats.org/package/2006/metadata/core-properties' "
                    "xmlns:dc='http://purl.org/dc/elements/1.1/'>"
                    f"<dc:creator>{metadata_value}</dc:creator>"
                    "</cp:coreProperties>",
                )
                archive.writestr("ppt/vbaProject.bin", b"synthetic")
                archive.writestr("ppt/media/image1.png", b"synthetic")
            scanner = self.scan(root)
            categories = self.categories(scanner)
            self.assertIn("unapproved_office_identity_metadata", categories)
            self.assertIn("office_macro", categories)
            self.assertIn("office_media_requires_manual_review", categories)

    def test_archive_path_traversal_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "unsafe.zip"
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("../outside.txt", "synthetic")
            scanner = self.scan(root)
            self.assertIn("archive_path_traversal", self.categories(scanner))


if __name__ == "__main__":
    unittest.main()
