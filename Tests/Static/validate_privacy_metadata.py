#!/usr/bin/env python3
"""Repository-wide privacy and metadata scanner using Python standard library only.

The scanner never prints matched values. Findings are aggregated by repository path
and category so that CI logs do not become a secondary disclosure channel.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import io
import ipaddress
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Iterable
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]

TEXT_SUFFIXES = {
    ".bat", ".cmd", ".conf", ".csv", ".ini", ".json", ".md", ".ps1",
    ".properties", ".py", ".rels", ".sh", ".sql", ".toml", ".txt",
    ".xml", ".yaml", ".yml",
}
OFFICE_SUFFIXES = {".pptx", ".docx", ".xlsx"}
ARCHIVE_SUFFIXES = {".zip"}
MEDIA_SUFFIXES = {
    ".bmp", ".gif", ".jpeg", ".jpg", ".mov", ".mp3", ".mp4", ".mpeg",
    ".png", ".svg", ".tif", ".tiff", ".webm", ".webp", ".wmv",
}
BINARY_REVIEW_SUFFIXES = {".pdf", ".ttf", ".otf", ".woff", ".woff2"}
SKIP_DIR_NAMES = {".git", ".venv", "__pycache__", "node_modules"}
MAX_TEXT_BYTES = 5 * 1024 * 1024
MAX_ARCHIVE_ENTRY_BYTES = 25 * 1024 * 1024
MAX_ARCHIVE_TOTAL_BYTES = 250 * 1024 * 1024
MAX_ARCHIVE_DEPTH = 2

APPROVED_IMMUTABLE_FILES = {
    "Presentations/old/Performance Grundlagen V-2024.zip":
        "78e3d1d708758d1115a066eca1df2c66d6f26ba57903b764c98e901506892041",
}
APPROVED_ACTIVE_DECK = {
    "Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx":
        "85bd14e4fc91d148889e9ebaa7128f6e1a213366f389aa6e2053f46cc0890ad3",
}
FORBIDDEN_REFERENCE_EXCEPTIONS = {
    "Tests/Static/validate_w2_007_presentation.py",
}
ALLOWED_METADATA_VALUES = {
    "",
    "Gerhard Pisch",
    "Microsoft Office User",
    "LibreOffice",
    "python-pptx",
}
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "invalid"}
ALLOWED_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
INTERNAL_HOST_SUFFIXES = (".corp", ".internal", ".intra", ".lan", ".local")
PLACEHOLDER_WORDS = {
    "changeme", "dummy", "example", "placeholder", "replace", "sample", "secret_here",
}

# Construct legacy identifiers from fragments so the scanner source is not its own match.
FORBIDDEN_TERMS = (
    "BI" + "-Automation",
    "SQL_Server" + "_Analyze",
)

EMAIL_RE = re.compile(r"(?i)(?<![\w.+-])([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])")
URL_RE = re.compile(r"(?i)\b(?:https?|ftp)://[^\s<>\"']+")
IPV4_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
PHONE_INTERNATIONAL_RE = re.compile(r"(?<!\w)\+\d{1,3}(?:[\s()./-]*\d){6,14}(?!\w)")
PHONE_LABEL_RE = re.compile(
    r"(?i)\b(?:tel(?:efon)?|phone|mobile|mobil|fax)\s*[:=]\s*(?:\+?\d[\d\s()./-]{5,}\d)"
)
UNC_RE = re.compile(r"(?i)(?<!\\)\\\\[A-Z0-9._-]+\\[A-Z0-9$_. -]+")
WINDOWS_USER_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+")
UNIX_USER_PATH_RE = re.compile(r"(?<![\w/])/(?:home|Users)/[^/\s]+")
PRIVATE_KEY_RE = re.compile(re.escape("BEGIN " + "PRIVATE KEY"), re.IGNORECASE)
GITHUB_TOKEN_RE = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")
AWS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
PASSWORD_LITERAL_RE = re.compile(
    r"(?i)\b(?:password|pwd|client_secret|api[_-]?key)\s*[:=]\s*[\"']([^\"'\n]{6,})[\"']"
)
CONNECTION_PASSWORD_RE = re.compile(
    r"(?i)(?:password|pwd)\s*=\s*([A-Za-z0-9!@#$%^&*._-]{6,})(?=;|[\"'\s])"
)

SUSPICIOUS_OFFICE_PARTS = {
    "macro": ("vbaproject.bin",),
    "activex": ("/activex/",),
    "embedded_object": ("/embeddings/",),
    "digital_signature": ("_xmlsignatures/",),
    "custom_xml": ("/customxml/",),
}
IDENTITY_METADATA_NAMES = {
    "creator", "lastmodifiedby", "company", "manager", "hyperlinkbase",
}


@dataclass(frozen=True)
class Finding:
    path: str
    category: str


@dataclass
class ScanStats:
    files: int = 0
    text_files: int = 0
    packages: int = 0
    archives: int = 0
    approved_immutable: int = 0


class Scanner:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.findings: Counter[Finding] = Counter()
        self.stats = ScanStats()

    def add(self, path: str, category: str, count: int = 1) -> None:
        self.findings[Finding(path=path, category=category)] += count

    @staticmethod
    def _decode_text(data: bytes) -> str | None:
        if not data:
            return ""
        if b"\x00" in data[:4096] and not data.startswith((b"\xff\xfe", b"\xfe\xff")):
            return None
        for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return None

    @staticmethod
    def _placeholder(value: str) -> bool:
        lowered = value.strip().lower()
        return (
            not lowered
            or any(marker in value for marker in ("${", "{{", "<", ">"))
            or any(word in lowered for word in PLACEHOLDER_WORDS)
        )

    def scan_text(self, label: str, text: str, *, allow_forbidden_reference: bool = False) -> None:
        email_count = 0
        for match in EMAIL_RE.finditer(text):
            domain = match.group(2).lower()
            if domain not in ALLOWED_EMAIL_DOMAINS:
                email_count += 1
        if email_count:
            self.add(label, "email_address", email_count)

        phone_count = len(PHONE_INTERNATIONAL_RE.findall(text)) + len(PHONE_LABEL_RE.findall(text))
        if phone_count:
            self.add(label, "phone_number", phone_count)

        private_ip_count = 0
        for candidate in IPV4_RE.findall(text):
            try:
                address = ipaddress.ip_address(candidate)
            except ValueError:
                continue
            if address.is_private and not address.is_loopback:
                private_ip_count += 1
        if private_ip_count:
            self.add(label, "private_ip_address", private_ip_count)

        if UNC_RE.search(text):
            self.add(label, "unc_path", len(UNC_RE.findall(text)))
        if WINDOWS_USER_PATH_RE.search(text):
            self.add(label, "windows_user_profile_path", len(WINDOWS_USER_PATH_RE.findall(text)))
        if UNIX_USER_PATH_RE.search(text):
            self.add(label, "unix_user_profile_path", len(UNIX_USER_PATH_RE.findall(text)))

        internal_url_count = 0
        for raw_url in URL_RE.findall(text):
            host = (urlsplit(raw_url.rstrip(".,);]")).hostname or "").lower()
            if not host or host in ALLOWED_LOOPBACK_HOSTS:
                continue
            is_internal = host.endswith(INTERNAL_HOST_SUFFIXES)
            try:
                address = ipaddress.ip_address(host)
            except ValueError:
                address = None
            if is_internal or (address is not None and address.is_private and not address.is_loopback):
                internal_url_count += 1
        if internal_url_count:
            self.add(label, "internal_url", internal_url_count)

        if PRIVATE_KEY_RE.search(text):
            self.add(label, "private_key_material", len(PRIVATE_KEY_RE.findall(text)))
        if GITHUB_TOKEN_RE.search(text):
            self.add(label, "github_token", len(GITHUB_TOKEN_RE.findall(text)))
        if AWS_KEY_RE.search(text):
            self.add(label, "aws_access_key", len(AWS_KEY_RE.findall(text)))

        literal_secret_count = 0
        for match in PASSWORD_LITERAL_RE.finditer(text):
            if not self._placeholder(match.group(1)):
                literal_secret_count += 1
        for match in CONNECTION_PASSWORD_RE.finditer(text):
            if not self._placeholder(match.group(1)):
                literal_secret_count += 1
        if literal_secret_count:
            self.add(label, "literal_secret_or_password", literal_secret_count)

        if not allow_forbidden_reference:
            for term in FORBIDDEN_TERMS:
                count = text.lower().count(term.lower())
                if count:
                    self.add(label, "forbidden_legacy_identifier", count)

    def _scan_identity_metadata(self, label: str, xml_text: str) -> None:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            self.add(label, "invalid_xml")
            return
        for element in root.iter():
            local_name = element.tag.rsplit("}", 1)[-1].lower()
            if local_name not in IDENTITY_METADATA_NAMES:
                continue
            value = (element.text or "").strip()
            if value not in ALLOWED_METADATA_VALUES:
                self.add(label, "unapproved_office_identity_metadata")

    @staticmethod
    def _safe_archive_name(name: str) -> bool:
        pure = PurePosixPath(name)
        return not pure.is_absolute() and ".." not in pure.parts and "\\" not in name

    @staticmethod
    def _active_deck_hash_approved(outer_label: str, outer_sha256: str) -> bool:
        return APPROVED_ACTIVE_DECK.get(outer_label) == outer_sha256

    def _media_allowed(self, outer_label: str, outer_sha256: str, member_name: str) -> bool:
        if not self._active_deck_hash_approved(outer_label, outer_sha256):
            return False
        lowered = member_name.lower()
        return lowered.startswith("docprops/thumbnail.") or lowered.startswith("ppt/media/")

    def scan_zip_bytes(self, label: str, data: bytes, *, depth: int, office_package: bool) -> None:
        if depth > MAX_ARCHIVE_DEPTH:
            self.add(label, "archive_nesting_limit")
            return
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                bad_member = archive.testzip()
                if bad_member:
                    self.add(label, "corrupt_archive_member")
                outer_sha256 = hashlib.sha256(data).hexdigest()
                approved_active_deck = self._active_deck_hash_approved(label, outer_sha256)
                total_uncompressed = 0
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    member_name = info.filename
                    member_label = f"{label}!/{member_name}"
                    if not self._safe_archive_name(member_name):
                        self.add(label, "archive_path_traversal")
                        continue
                    if info.flag_bits & 0x1:
                        self.add(member_label, "encrypted_archive_entry")
                        continue
                    total_uncompressed += info.file_size
                    if info.file_size > MAX_ARCHIVE_ENTRY_BYTES:
                        self.add(member_label, "archive_entry_too_large")
                        continue
                    if total_uncompressed > MAX_ARCHIVE_TOTAL_BYTES:
                        self.add(label, "archive_expansion_limit")
                        break

                    lowered = "/" + member_name.lower()
                    if office_package:
                        for category, fragments in SUSPICIOUS_OFFICE_PARTS.items():
                            if any(fragment in lowered for fragment in fragments):
                                self.add(member_label, f"office_{category}")
                        if PurePosixPath(member_name).suffix.lower() in MEDIA_SUFFIXES:
                            if not self._media_allowed(label, outer_sha256, member_name):
                                self.add(member_label, "office_media_requires_manual_review")
                            continue

                    suffix = PurePosixPath(member_name).suffix.lower()
                    if suffix in TEXT_SUFFIXES or member_name.lower().endswith(".rels"):
                        raw = archive.read(info)
                        text = self._decode_text(raw)
                        if text is None:
                            self.add(member_label, "text_decode_failed")
                            continue
                        self.scan_text(member_label, text)
                        if (
                            office_package
                            and not approved_active_deck
                            and member_name.lower() in {
                                "docprops/core.xml", "docprops/app.xml", "docprops/custom.xml"
                            }
                        ):
                            self._scan_identity_metadata(member_label, text)
                    elif suffix in OFFICE_SUFFIXES:
                        self.scan_zip_bytes(
                            member_label,
                            archive.read(info),
                            depth=depth + 1,
                            office_package=True,
                        )
                    elif suffix in ARCHIVE_SUFFIXES:
                        self.scan_zip_bytes(
                            member_label,
                            archive.read(info),
                            depth=depth + 1,
                            office_package=False,
                        )
                    elif suffix in MEDIA_SUFFIXES:
                        self.add(member_label, "archive_media_requires_manual_review")
                    elif suffix in BINARY_REVIEW_SUFFIXES:
                        self.add(member_label, "archive_binary_requires_manual_review")
        except (OSError, zipfile.BadZipFile, RuntimeError):
            self.add(label, "invalid_or_unreadable_archive")

    def scan_file(self, path: Path) -> None:
        relative = path.relative_to(self.root).as_posix()
        self.stats.files += 1
        try:
            data = path.read_bytes()
        except OSError:
            self.add(relative, "file_read_failed")
            return

        approved_hash = APPROVED_IMMUTABLE_FILES.get(relative)
        if approved_hash is not None:
            if hashlib.sha256(data).hexdigest() == approved_hash:
                self.stats.approved_immutable += 1
                return
            self.add(relative, "approved_immutable_hash_mismatch")
            return

        suffix = path.suffix.lower()
        if suffix in OFFICE_SUFFIXES:
            self.stats.packages += 1
            self.scan_zip_bytes(relative, data, depth=0, office_package=True)
            return
        if suffix in ARCHIVE_SUFFIXES:
            self.stats.archives += 1
            self.scan_zip_bytes(relative, data, depth=0, office_package=False)
            return
        if suffix in MEDIA_SUFFIXES:
            self.add(relative, "media_requires_manual_review")
            return
        if suffix in BINARY_REVIEW_SUFFIXES:
            self.add(relative, "binary_asset_requires_manual_review")
            return
        if suffix in TEXT_SUFFIXES:
            self.stats.text_files += 1
            if len(data) > MAX_TEXT_BYTES:
                self.add(relative, "text_file_too_large")
                return
            text = self._decode_text(data)
            if text is None:
                self.add(relative, "text_decode_failed")
                return
            self.scan_text(
                relative,
                text,
                allow_forbidden_reference=relative in FORBIDDEN_REFERENCE_EXCEPTIONS,
            )

    def scan(self) -> None:
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            try:
                relative_parts = path.relative_to(self.root).parts
            except ValueError:
                continue
            if any(part in SKIP_DIR_NAMES for part in relative_parts):
                continue
            if relative_parts[:3] == ("Presentations", "variants", "build"):
                continue
            self.scan_file(path)

    def report(self) -> int:
        if self.findings:
            print(f"privacy-metadata: FAIL ({sum(self.findings.values())} finding(s))")
            for finding, count in sorted(
                self.findings.items(), key=lambda item: (item[0].path, item[0].category)
            ):
                print(f"- {finding.path}: {finding.category} ({count})")
            print("Matched values are intentionally omitted from this report.")
            return 1
        print(
            "privacy-metadata: PASS "
            f"(files={self.stats.files}; text={self.stats.text_files}; "
            f"office={self.stats.packages}; archives={self.stats.archives}; "
            f"approved_immutable={self.stats.approved_immutable})"
        )
        return 0


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan repository content for privacy and metadata risks.")
    parser.add_argument("root", nargs="?", default=str(ROOT), help="Repository root to scan.")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    scanner = Scanner(Path(args.root))
    scanner.scan()
    return scanner.report()


if __name__ == "__main__":
    sys.exit(main())
