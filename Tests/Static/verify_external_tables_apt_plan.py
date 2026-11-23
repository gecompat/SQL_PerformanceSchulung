"""Verify External Tables package plans, offline artifacts and guest package state."""
from __future__ import annotations

import argparse
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re


INSTALL = re.compile(
    r"Inst ([a-z0-9][a-z0-9+.-]*)(?::amd64)?(?: \[([^\s\]]+)\])? \(([^\s()]+) .+\)",
    re.ASCII,
)
PACKAGE_NAME = re.compile(r"[a-z0-9][a-z0-9+.-]*", re.ASCII)
PACKAGE_VERSION = re.compile(r"[0-9A-Za-z.+:~\-]+", re.ASCII)
STATUS_FIELDS = frozenset({"Package", "Architecture", "Version", "Status"})
STATUS_LIMIT_BYTES = 2 * 1024 * 1024

LOCK = (
    Path(__file__).resolve().parents[2] / "Documentation" / "Project_Planning" / "external_tables_apt_lock.json"
)


def parse_install_plan(text: str) -> dict[str, tuple[str | None, str]]:
    result = {}
    for line in text.splitlines():
        if line.startswith(("Remv ", "Purg ")):
            raise ValueError("APT plan would remove existing packages")
        if not line.startswith("Inst "):
            continue
        match = INSTALL.fullmatch(line)
        if match is None:
            raise ValueError("APT plan includes an unexpected installation record")
        package, old, new = match.groups()
        if package in result:
            raise ValueError("APT plan includes a duplicate package")
        result[package] = (old, new)
    if not result:
        raise ValueError("APT plan contains no installation records")
    return result


def check_plan(text: str, lock: dict) -> int:
    expected = {
        entry["package"]: (entry.get("previous_version"), entry["version"])
        for entry in lock["packages"]
    }
    if len(expected) != len(lock["packages"]):
        raise ValueError("APT lock contains duplicate packages")
    actual = parse_install_plan(text)
    if actual != expected:
        raise ValueError("APT plan differs from the locked names or version transitions")
    return len(actual)


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


def verify_guest_state(base_status: bytes, guest_status: bytes, base_digest: str, role_lock: dict) -> int:
    """Require exactly the pinned base packages plus the selected role transitions."""
    if sha256(base_status).hexdigest() != base_digest:
        raise ValueError("base dpkg status differs from the pinned image")
    expected = parse_dpkg_status(base_status)
    for entry in role_lock["packages"]:
        identity = (entry["package"], entry["architecture"])
        if expected.get(identity) != entry.get("previous_version"):
            raise ValueError("locked transition differs from the pinned base package")
        expected[identity] = entry["version"]

    actual = parse_dpkg_status(guest_status)
    if actual != expected:
        missing = expected.keys() - actual.keys()
        extra = actual.keys() - expected.keys()
        changed = sum(expected[key] != actual[key] for key in expected.keys() & actual.keys())
        raise ValueError(f"guest package inventory differs (missing={len(missing)}, extra={len(extra)}, changed={changed})")
    return len(actual)



def _matches_file(path: Path, entry: dict) -> bool:
    with path.open("rb") as stream:
        return path.stat().st_size == entry["size"] and file_digest(stream, "sha256").hexdigest() == entry["sha256"]


def verify_packages(directory: Path, lock: dict) -> int:
    for entry in lock["packages"]:
        path = directory / Path(entry["path"]).name
        if not _matches_file(path, entry):
            raise ValueError(f"package bytes differ from lock: {entry['package']}")
    return len(lock["packages"])


def verify_python_wheel(path: Path, lock: dict) -> None:
    entry = lock.get("python_wheel")
    if entry is None:
        raise ValueError("Python wheel is only part of the query role")
    if path.name != entry["filename"] or not _matches_file(path, entry):
        raise ValueError("Python wheel differs from the query role lock")


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apt_plan", nargs="?", type=Path)
    parser.add_argument("--role", choices=("query", "source"), default="query")
    parser.add_argument("--payload-directory", type=Path, help="also verify all locked .deb files")
    parser.add_argument("--python-wheel", type=Path, help="also verify the query guest's CPython wheel")
    parser.add_argument("--base-status", type=Path, help="raw dpkg status from the pinned base image")
    parser.add_argument("--guest-status", type=Path, help="raw dpkg status captured from the prepared guest")
    args = parser.parse_args()
    try:
        lock_manifest = json.loads(LOCK.read_text(encoding="utf-8"))
        lock = select_role(lock_manifest, args.role)
        if bool(args.base_status) != bool(args.guest_status):
            raise ValueError("base and guest dpkg status must be supplied together")
        if args.apt_plan is None and args.guest_status is None:
            raise ValueError("expected an APT plan or the base and guest dpkg status files")
        if args.apt_plan is not None:
            with args.apt_plan.open("rb") as stream:
                data = stream.read(128 * 1024 + 1)
            if len(data) > 128 * 1024:
                raise ValueError("APT plan exceeds the read limit")
            count = check_plan(data.decode("utf-8"), lock)
            print(f"PASS {count} locked package transitions, no package removals")
        if args.guest_status is not None:
            with args.base_status.open("rb") as stream:
                base_status = stream.read(STATUS_LIMIT_BYTES + 1)
            with args.guest_status.open("rb") as stream:
                guest_status = stream.read(STATUS_LIMIT_BYTES + 1)
            count = verify_guest_state(base_status, guest_status, lock_manifest["dpkg_status_sha256"], lock)
            print(f"PASS {count} installed packages match the {args.role} role")
        if args.payload_directory is not None:
            print(f"PASS {verify_packages(args.payload_directory, lock)} locked package payloads")
        if args.python_wheel is not None:
            verify_python_wheel(args.python_wheel, lock)
            print("PASS locked query-guest Python wheel")
    except (OSError, ValueError) as exc:
        print(f"FAIL {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
