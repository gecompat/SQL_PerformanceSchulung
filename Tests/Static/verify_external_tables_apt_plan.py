"""Verify External Tables package plans, offline artifacts and guest package state."""
from __future__ import annotations

import argparse
from hashlib import file_digest
import json
from pathlib import Path
import re
import sys
from zipfile import BadZipFile, ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_package_state import read_dpkg_status, select_role, verify_guest_state


INSTALL = re.compile(
    r"Inst ([a-z0-9][a-z0-9+.-]*)(?::amd64)?(?: \[([^\s\]]+)\])? \(([^\s()]+) .+\)",
    re.ASCII,
)

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
    extension = entry["installed_extension"]
    try:
        with ZipFile(path) as wheel:
            entries = [member for member in wheel.infolist() if member.filename.endswith(".so")]
            if len(entries) != 1 or entries[0].filename != extension["filename"] or entries[0].file_size != extension["size"]:
                raise ValueError("Python wheel extension differs from the query role lock")
            with wheel.open(entries[0]) as binary:
                if file_digest(binary, "sha256").hexdigest() != extension["sha256"]:
                    raise ValueError("Python wheel extension differs from the query role lock")
    except BadZipFile:
        raise ValueError("Python wheel is not a valid archive") from None


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
            base_status = read_dpkg_status(args.base_status)
            guest_status = read_dpkg_status(args.guest_status)
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
