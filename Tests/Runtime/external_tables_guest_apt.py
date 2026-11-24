"""Install the exact package lock in a detached, disposable External Tables guest."""

from __future__ import annotations

from hashlib import file_digest, sha256
from math import isfinite
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from external_tables_odbc import read_pinned_pyodbc_wheel, stage_pinned_pyodbc
from external_tables_package_state import read_dpkg_status, select_role, verify_guest_state
from external_tables_pilot_sql import Role
from external_tables_polybase_service import ensure_polybase_service_setup, install_dotnet_sdk


_DPKG_STATUS = Path("/var/lib/dpkg/status")
_NET_INTERFACES = Path("/sys/class/net")
_APT_SECONDS = 600
_APT_ENV = {
    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
    "LC_ALL": "C",
    "DEBIAN_FRONTEND": "noninteractive",
    "ACCEPT_EULA": "Y",
}

INSTALL = re.compile(
    r"Inst ([a-z0-9][a-z0-9+.-]*)(?::amd64)?(?: \[([^\s\]]+)\])? \(([^\s()]+) .+\)",
    re.ASCII,
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


def matches_locked_file(path: Path, entry: dict) -> bool:
    with path.open("rb") as stream:
        return path.stat().st_size == entry["size"] and file_digest(stream, "sha256").hexdigest() == entry["sha256"]


def verify_packages(directory: Path, lock: dict) -> int:
    for entry in lock["packages"]:
        path = directory / Path(entry["path"]).name
        if not matches_locked_file(path, entry):
            raise ValueError(f"package bytes differ from lock: {entry['package']}")
    return len(lock["packages"])


def install_verified_guest_packages(
    staging: Path, package_lock: dict, role: Role, deadline: float, *, wheel_install_dir: Path | None = None,
) -> int:
    """Apply a role lock once on a freshly booted, detached pilot guest."""
    _remaining(deadline)
    if sys.platform != "linux" or os.geteuid() != 0:
        raise ValueError("offline package installation requires the prepared Linux guest")
    require_guest_detached()
    stage = staging.resolve(strict=True)
    if not os.statvfs(stage).f_flag & os.ST_RDONLY:
        raise ValueError("the guest package staging volume must be read-only")

    base_status = read_dpkg_status(_DPKG_STATUS)
    base_digest = package_lock["dpkg_status_sha256"]
    if sha256(base_status).hexdigest() != base_digest:
        raise ValueError("guest is not at the pinned base package state")

    role_lock = select_role(package_lock, role.value.lower())
    verify_packages(stage, role_lock)
    wheel = role_lock.get("python_wheel")
    if (wheel is None) != (wheel_install_dir is None):
        raise ValueError("guest wheel installation requires its role lock and private directory")
    if wheel_install_dir is not None and not wheel_install_dir.is_dir():
        raise ValueError("guest wheel installation requires an existing private directory")
    wheel_payload = None if wheel is None else read_pinned_pyodbc_wheel(stage / wheel["filename"], wheel)
    package_paths = tuple(stage / Path(entry["path"]).name for entry in role_lock["packages"])
    with TemporaryDirectory(prefix="external-tables-apt-") as directory:
        apt_state = Path(directory)
        (apt_state / "sources.list").touch()
        for folder in ("sources.list.d", "lists", "archives"):
            (apt_state / folder).mkdir()
        plan = _run_apt(apt_install_command(package_paths, apt_state, simulate=True), deadline)
        check_plan(plan.decode("utf-8"), role_lock)

        require_guest_detached()
        if read_dpkg_status(_DPKG_STATUS) != base_status:
            raise ValueError("guest package state changed after the APT simulation")
        if role is Role.QUERY:
            install_dotnet_sdk(stage, package_lock["dotnet_sdk"], deadline)
            require_guest_detached()
        _run_apt(apt_install_command(package_paths, apt_state, simulate=False), deadline)
    require_guest_detached()
    installed = verify_guest_state(base_status, read_dpkg_status(_DPKG_STATUS), base_digest, role_lock)
    if role is Role.QUERY:
        ensure_polybase_service_setup(package_lock["dotnet_sdk"]["sdk_version"], deadline)
        require_guest_detached()
    if wheel_payload is not None:
        _remaining(deadline)
        stage_pinned_pyodbc(wheel_install_dir, wheel, wheel_payload)
    _remaining(deadline)
    return installed


def apt_install_command(package_paths: tuple[Path, ...], apt_state: Path, *, simulate: bool) -> list[str]:
    """Use the same closed package inputs and APT options for both phases."""
    if not package_paths or any(not path.is_absolute() or path.suffix != ".deb" for path in package_paths):
        raise ValueError("offline APT requires absolute package paths")
    return [
        "/usr/bin/apt-get", "--simulate" if simulate else "--assume-yes",
        "--no-remove", "--no-install-recommends",
        "-o", f"Dir::Etc::sourcelist={apt_state / 'sources.list'}",
        "-o", f"Dir::Etc::sourceparts={apt_state / 'sources.list.d'}",
        "-o", f"Dir::State::lists={apt_state / 'lists'}",
        "-o", f"Dir::Cache::archives={apt_state / 'archives'}",
        "install", *(str(path) for path in package_paths),
    ]


def require_guest_detached() -> None:
    """Require a guest with no IP interfaces besides loopback."""
    if {entry.name for entry in _NET_INTERFACES.iterdir()} != {"lo"}:
        raise ValueError("the pilot guest must have only its loopback interface during installation")


def _remaining(deadline: float) -> float:
    remaining = deadline - monotonic()
    if not isfinite(remaining) or remaining <= 0:
        raise TimeoutError("offline guest package installation deadline exceeded")
    return remaining


def _run_apt(command: list[str], deadline: float) -> bytes:
    try:
        result = collect_bounded_process(
            command, input_bytes=b"", environment=_APT_ENV,
            timeout_seconds=min(_remaining(deadline), _APT_SECONDS),
            timeout_ceiling_seconds=_APT_SECONDS,
            stdout_limit_bytes=128 * 1024, stderr_limit_bytes=64 * 1024,
        )
    except CaptureTimeoutError:
        raise TimeoutError("offline guest package installation deadline exceeded") from None
    except CaptureRunnerError:
        raise OSError("offline guest package process could not be confirmed") from None
    if result.returncode:
        raise OSError("offline guest package process failed")
    _remaining(deadline)
    return result.stdout
