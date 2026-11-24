"""Read-only evidence for the ODBC driver loaded in a dedicated PolyBase guest."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import file_digest
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from time import monotonic

from verify_external_tables_packages import VERSION


SERVICES = ("mssql-ees.service", "mssql-server.service")
LIBRARY = re.compile(r"libmsodbcsql[-.]([0-9]+)(?:\.[0-9]+)*\.so(?:\.[0-9]+)*", re.ASCII)
SHA256 = re.compile(r"[0-9a-f]{64}", re.ASCII)


@dataclass(frozen=True)
class Mapping:
    path: Path
    major: int
    minor: int
    inode: int


def select_driver_mapping(maps: str) -> Mapping:
    drivers: set[Mapping] = set()
    for line in maps.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6:
            continue
        path = fields[5]
        if "libmsodbcsql" not in path:
            continue
        name = LIBRARY.fullmatch(Path(path).name)
        if not path.startswith("/") or name is None or name[1] != "18":
            raise ValueError("a mapped SQL Server driver has an unexpected name or major version")
        major, minor = (int(value, 16) for value in fields[3].split(":"))
        inode = int(fields[4])
        if inode <= 0:
            raise ValueError("mapped ODBC driver does not have a file identity")
        drivers.add(Mapping(Path(path), major, minor, inode))
    if len(drivers) != 1:
        raise ValueError("expected one mapped Microsoft ODBC Driver 18 file")
    return drivers.pop()


def in_service_group(cgroup: str, expected: str) -> bool:
    if not expected.startswith("/") or expected == "/" or expected.endswith("/"):
        return False
    unified_paths = [line[3:] for line in cgroup.splitlines() if line.startswith("0::")]
    return len(unified_paths) == 1 and (
        unified_paths[0] == expected or unified_paths[0].startswith(expected + "/")
    )


def observe(pid: int, service: str, *, deadline: float | None = None) -> dict[str, str]:
    if service not in SERVICES or not 1 <= pid <= 2**31 - 1:
        raise ValueError("invalid pilot service or process ID")
    if subprocess.run(
        ["systemctl", "is-active", "--quiet", service], capture_output=True, timeout=_timeout(deadline), check=False,
    ).returncode:
        raise ValueError("selected SQL Server service is inactive")
    group = _command("systemctl", "show", service, "--property=ControlGroup", "--value", deadline=deadline)
    for package in ("mssql-server", "mssql-server-polybase"):
        installed = _command("dpkg-query", "-W", "-f=${Status}|${Version}|${Architecture}", package, deadline=deadline)
        if installed != f"install ok installed|{VERSION}|amd64":
            raise ValueError(f"unexpected installed version or architecture for {package}")

    proc = Path("/proc") / str(pid)
    before = _read(proc / "stat", 8192)
    start = _start_time(before)
    if not in_service_group(_read(proc / "cgroup", 8192), group):
        raise ValueError("process does not belong to the selected service cgroup")
    mapping = select_driver_mapping(_read(proc / "maps", 2 * 1024 * 1024))
    digest = _mapped_digest(mapping)
    if (
        start != _start_time(_read(proc / "stat", 8192))
        or not in_service_group(_read(proc / "cgroup", 8192), group)
        or mapping != select_driver_mapping(_read(proc / "maps", 2 * 1024 * 1024))
    ):
        raise ValueError("process identity or driver mapping changed during inspection")
    _timeout(deadline)
    return {"service": service, "version": VERSION, "driver_file": mapping.path.name, "sha256": digest}


def _mapped_digest(mapping: Mapping) -> str:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    with os.fdopen(os.open(mapping.path, flags), "rb") as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or not 0 < info.st_size <= 64 * 1024 * 1024
            or (os.major(info.st_dev), os.minor(info.st_dev), info.st_ino)
            != (mapping.major, mapping.minor, mapping.inode)
        ):
            raise ValueError("driver file differs from the mapped device and inode")
        digest = file_digest(stream, "sha256").hexdigest()
        final = os.fstat(stream.fileno())
        if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (final.st_size, final.st_mtime_ns, final.st_ctime_ns):
            raise ValueError("driver file changed during inspection")
        return digest


def _start_time(proc_stat: str) -> str:
    # The executable name in parentheses may itself include spaces or ")".
    fields = proc_stat.rpartition(")")[2].split()
    if len(fields) < 20 or not fields[19].isdigit():
        raise ValueError("process start time could not be resolved")
    return fields[19]


def _read(path: Path, limit: int) -> str:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if not data or len(data) > limit:
        raise ValueError("process evidence is absent or exceeds the read limit")
    return data.decode("utf-8")


def _timeout(deadline: float | None) -> float:
    if deadline is None:
        return 5
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise TimeoutError("connector observation deadline exceeded")
    return min(5, remaining)


def _command(*argv: str, deadline: float | None = None) -> str:
    result = subprocess.run(argv, capture_output=True, timeout=_timeout(deadline), check=False, text=True)
    if result.returncode or result.stderr:
        raise ValueError("guest service or package metadata query failed")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--service", required=True, choices=SERVICES)
    parser.add_argument("--expected-sha256", help="compare with a separately reviewed driver digest")
    args = parser.parse_args()
    try:
        if args.expected_sha256 is not None and not SHA256.fullmatch(args.expected_sha256):
            raise ValueError("expected driver SHA-256 must be 64 lowercase hexadecimal characters")
        evidence = observe(args.pid, args.service)
        if args.expected_sha256 is not None and evidence["sha256"] != args.expected_sha256:
            raise ValueError("mapped ODBC driver differs from the reviewed build")
        status = "MATCHED" if args.expected_sha256 is not None else "OBSERVED"
        print(json.dumps(evidence | {"status": status}, sort_keys=True))
    except (AttributeError, OSError, ValueError, subprocess.TimeoutExpired):
        print("NOT_PROVEN: guest package, service or mapped driver identity could not be confirmed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
