"""Check the simulated External Tables package plan and optional offline artifacts."""
from __future__ import annotations

import argparse
from hashlib import file_digest
import json
from pathlib import Path
import re


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


def select_role(lock: dict, role: str) -> dict:
    names = lock["roles"][role]
    want = set(names)
    packages = [entry for entry in lock["packages"] if entry["package"] in want]
    if len(want) != len(names) or {entry["package"] for entry in packages} != want:
        raise ValueError("APT role refers to duplicate or unknown packages")
    selected = {"packages": packages}
    if role == "query" and "python_wheel" in lock:
        selected["python_wheel"] = lock["python_wheel"]
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apt_plan", type=Path)
    parser.add_argument("--role", choices=("query", "source"), default="query")
    parser.add_argument("--payload-directory", type=Path, help="also verify all locked .deb files")
    parser.add_argument("--python-wheel", type=Path, help="also verify the query guest's CPython wheel")
    args = parser.parse_args()
    try:
        with args.apt_plan.open("rb") as stream:
            data = stream.read(128 * 1024 + 1)
        if len(data) > 128 * 1024:
            raise ValueError("APT plan exceeds the read limit")
        lock = select_role(json.loads(LOCK.read_text(encoding="utf-8")), args.role)
        count = check_plan(data.decode("utf-8"), lock)
        print(f"PASS {count} locked package transitions, no package removals")
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
