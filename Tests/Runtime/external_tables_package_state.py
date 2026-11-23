"""Shared External Tables Debian package inventory checks for host and guest."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

PACKAGE_NAME = re.compile(r"[a-z0-9][a-z0-9+.-]*", re.ASCII)
PACKAGE_VERSION = re.compile(r"[0-9A-Za-z.+:~\-]+", re.ASCII)
STATUS_FIELDS = frozenset({"Package", "Architecture", "Version", "Status"})
STATUS_LIMIT_BYTES = 2 * 1024 * 1024


def parse_dpkg_status(data: bytes) -> dict[tuple[str, str], str]:
    if not data or len(data) > STATUS_LIMIT_BYTES:
        raise ValueError("dpkg status is empty or exceeds the read limit")
    installed = {}
    for paragraph in data.decode("utf-8").replace("\r\n", "\n").split("\n\n"):
        if not paragraph.strip():
            continue
        fields = {}
        for line in paragraph.splitlines():
            key, separator, value = line.partition(": ")
            if separator and key in STATUS_FIELDS:
                if key in fields:
                    raise ValueError("ambiguous dpkg status fields")
                fields[key] = value
        if fields.keys() != STATUS_FIELDS or fields["Status"] != "install ok installed":
            raise ValueError("dpkg status contains an incomplete or non-installed package")
        name, architecture, version = fields["Package"], fields["Architecture"], fields["Version"]
        identity = (name, architecture)
        if (
            PACKAGE_NAME.fullmatch(name) is None
            or architecture not in ("amd64", "all")
            or PACKAGE_VERSION.fullmatch(version) is None
            or identity in installed
        ):
            raise ValueError("invalid or duplicate native package identity in dpkg status")
        installed[identity] = version
    if not installed:
        raise ValueError("dpkg status has no installed packages")
    return installed


def _expected_guest_state(base_status: bytes, base_digest: str, role_lock: dict) -> dict[tuple[str, str], str]:
    if sha256(base_status).hexdigest() != base_digest:
        raise ValueError("base dpkg status differs from the pinned image")
    expected = parse_dpkg_status(base_status)
    for entry in role_lock["packages"]:
        name, architecture, version = entry["package"], entry["architecture"], entry["version"]
        if (
            PACKAGE_NAME.fullmatch(name) is None
            or architecture not in ("amd64", "all")
            or PACKAGE_VERSION.fullmatch(version) is None
        ):
            raise ValueError("invalid package identity in the role lock")
        identity = (name, architecture)
        if expected.get(identity) != entry.get("previous_version"):
            raise ValueError("locked transition differs from the pinned base package")
        expected[identity] = version

    return expected


def verify_guest_state(base_status: bytes, guest_status: bytes, base_digest: str, role_lock: dict) -> int:
    """Require exactly the pinned base packages plus the selected role transitions."""
    expected = _expected_guest_state(base_status, base_digest, role_lock)
    actual = parse_dpkg_status(guest_status)
    if actual != expected:
        missing = expected.keys() - actual.keys()
        extra = actual.keys() - expected.keys()
        changed = sum(expected[key] != actual[key] for key in expected.keys() & actual.keys())
        raise ValueError(f"guest package inventory differs (missing={len(missing)}, extra={len(extra)}, changed={changed})")
    return len(actual)


def select_role(lock: dict, role: str) -> dict:
    names = lock["roles"][role]
    want = set(names)
    packages = [entry for entry in lock["packages"] if entry["package"] in want]
    if (
        len(want) != len(names)
        or len(packages) != len(want)
        or {entry["package"] for entry in packages} != want
    ):
        raise ValueError("APT role refers to duplicate or unknown packages")
    selected = {"packages": packages}
    if role == "query" and "python_wheel" in lock:
        selected["python_wheel"] = lock["python_wheel"]
    return selected


def read_dpkg_status(path: Path) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(STATUS_LIMIT_BYTES + 1)
    if not data or len(data) > STATUS_LIMIT_BYTES:
        raise ValueError("dpkg status is empty or exceeds the read limit")
    return data


def _inventory_digest(packages: dict[tuple[str, str], str]) -> bytes:
    digest = sha256(b"SQLPERF-EXTERNAL-DPKG-V1\n")
    for (name, architecture), version in sorted(packages.items()):
        digest.update(f"{name}\t{architecture}\t{version}\n".encode("ascii"))
    return digest.digest()


def installed_package_digest(guest_status: bytes) -> bytes:
    """Fingerprint the complete installed Debian package inventory."""
    return _inventory_digest(parse_dpkg_status(guest_status))


def expected_package_digest(base_status: bytes, package_lock: dict, role: str) -> bytes:
    """Derive the expected fingerprint from the pinned base and exact role transitions."""
    try:
        role_lock = select_role(package_lock, role)
        packages = _expected_guest_state(base_status, package_lock["dpkg_status_sha256"], role_lock)
    except (KeyError, TypeError):
        raise ValueError("invalid role or package lock") from None
    return _inventory_digest(packages)
