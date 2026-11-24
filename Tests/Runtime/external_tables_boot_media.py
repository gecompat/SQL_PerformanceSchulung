"""Build the two-role NoCloud input for an offline External Tables guest."""

from __future__ import annotations

import argparse
from hashlib import file_digest
from ipaddress import IPv4Interface
import json
import os
from pathlib import Path, PurePosixPath
import shlex
from shutil import copyfile
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from external_tables_guest_apt import verify_packages
from external_tables_guest_identity import _remaining, linux_service_id
from external_tables_guest_network import GuestNetwork
from external_tables_odbc import read_pinned_pyodbc_wheel
from external_tables_package_state import select_role
from external_tables_pilot_sql import Role, database_name


_REPOSITORY = Path(__file__).resolve().parents[2]
_LOCK_PATH = Path("Documentation/Project_Planning/external_tables_apt_lock.json")
_RUNTIME = Path("Tests/Runtime")
_MODULES = (
    "dgn004_capture_runner", "execution_target", "external_tables_cleanup", "external_tables_guest_admin",
    "external_tables_guest_apt", "external_tables_guest_bootstrap", "external_tables_guest_identity",
    "external_tables_guest_network", "external_tables_measurement", "external_tables_odbc",
    "external_tables_package_state", "external_tables_pilot", "external_tables_pilot_sql",
    "external_tables_principals", "external_tables_pushdown_evidence", "external_tables_source_firewall",
)
_GUEST_FILES = (
    *(_RUNTIME / f"{module}.py" for module in _MODULES),
    *(Path(f"Tests/Static/{module}.py") for module in (
        "dgn004_capture_input", "dgn004_capture_result", "dgn004_plan_frame", "dgn004_plan_transport",
    )),
    Path("Demos/00_Framework/Tools/sqlcmd_process.py"),
)
_LABEL = "CIDATA"
_MEDIA = PurePosixPath("/run/sqlperf-external-media")
_WHEEL_DIRECTORY = PurePosixPath("/opt/sqlperf-external/wheel")
_BUILD_SECONDS = 120


def cloud_seed(token: str, role: Role, port: int, network: GuestNetwork) -> dict[str, str]:
    """Return fixed role-bound NoCloud configuration without any credential input."""
    database_name(token, role)
    linux_service_id(port)
    bootstrap = [
        "/usr/bin/python3", "-B", str(_MEDIA / "Tests/Runtime/external_tables_guest_bootstrap.py"),
        "--token", token, "--role", role.value, "--port", str(port),
        "--source-address", str(network.source), "--query-address", str(network.query),
        "--staging", str(_MEDIA / "packages"), "--wheel-directory", str(_WHEEL_DIRECTORY),
    ]
    commands = [
        ["/usr/bin/install", "-d", "-m", "0700", str(_MEDIA), str(_WHEEL_DIRECTORY)],
        ["/usr/bin/mount", "-t", "iso9660", "-o", "ro,nodev,nosuid,noexec", f"LABEL={_LABEL}", str(_MEDIA)],
        bootstrap,
    ]
    user = {
        "package_update": False,
        "package_upgrade": False,
        "runcmd": [["/bin/sh", "-ec", "\n".join(shlex.join(command) for command in commands)]],
    }
    return {
        "meta-data": json.dumps({"instance-id": f"sqlperf-external-{token}-{role.value.lower()}"}) + "\n",
        "network-config": '{"config":"disabled"}\n',
        "user-data": "#cloud-config\n" + json.dumps(user, indent=2) + "\n",
    }


def build_bootstrap_iso(
    destination: Path, packages: Path, token: str, role: Role, port: int, network: GuestNetwork, *,
    xorriso: Path = Path("/usr/bin/xorriso"),
) -> str:
    """Publish one ISO and return its SHA-256 for the provider's attachment check."""
    config = cloud_seed(token, role, port, network)
    output = destination.parent.resolve(strict=True) / destination.name
    if output.suffix.lower() != ".iso" or os.path.lexists(output):
        raise ValueError("expected a new ISO in the private run directory")
    cache = packages.resolve(strict=True)
    executable = xorriso.resolve(strict=True)
    deadline = monotonic() + _BUILD_SECONDS
    lock_source = _REPOSITORY / _LOCK_PATH
    lock_bytes = lock_source.read_bytes()
    role_lock = select_role(json.loads(lock_bytes), role.value.lower())
    wheel = role_lock["python_wheel"]
    names = [Path(entry["path"]).name for entry in role_lock["packages"]] + [wheel["filename"]]
    if len(set(names)) != len(names) or any(not name or Path(name).name != name for name in names):
        raise ValueError("expected unique package filenames")
    with TemporaryDirectory(prefix=".sqlperf-ext-media-", dir=output.parent) as folder:
        temporary = Path(folder)
        seed = temporary / "seed"
        stage = seed / "packages"
        stage.mkdir(parents=True)
        for name in names:
            _remaining(deadline)
            copyfile(cache / name, stage / name)
        verify_packages(stage, role_lock)
        read_pinned_pyodbc_wheel(stage / wheel["filename"], wheel)
        (seed / _LOCK_PATH).parent.mkdir(parents=True)
        (seed / _LOCK_PATH).write_bytes(lock_bytes)
        for item in _GUEST_FILES:
            (seed / item).parent.mkdir(parents=True, exist_ok=True)
            copyfile(_REPOSITORY / item, seed / item)
        for name, text in config.items():
            (seed / name).write_bytes(text.encode("utf-8"))
        image = temporary / "seed.iso"
        _write_iso(executable, seed, image, deadline)
        with image.open("rb") as stream:
            digest = file_digest(stream, "sha256").hexdigest()
        _remaining(deadline)
        os.link(image, output)
    return digest


def _write_iso(executable: Path, seed: Path, image: Path, deadline: float) -> None:
    try:
        result = collect_bounded_process(
            [str(executable), "-as", "mkisofs", "-quiet", "-r", "-J", "-V", _LABEL, "-o", str(image), str(seed)],
            input_bytes=b"", environment={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            timeout_seconds=_remaining(deadline), timeout_ceiling_seconds=_BUILD_SECONDS,
            stdout_limit_bytes=4096, stderr_limit_bytes=16384,
        )
    except CaptureTimeoutError:
        raise TimeoutError("External Tables boot media generation exceeded its deadline") from None
    except CaptureRunnerError:
        raise OSError("External Tables boot media generation could not be confirmed") from None
    if result.returncode or not image.is_file() or image.stat().st_size == 0:
        raise OSError("External Tables boot media generation could not be confirmed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--token", required=True)
    parser.add_argument("--role", required=True, choices=[role.value for role in Role])
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--source-address", required=True, type=IPv4Interface)
    parser.add_argument("--query-address", required=True, type=IPv4Interface)
    parser.add_argument("--packages", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--xorriso", type=Path, default=Path("/usr/bin/xorriso"))
    args = parser.parse_args(argv)
    try:
        digest = build_bootstrap_iso(
            args.output, args.packages, args.token, Role(args.role), args.port,
            GuestNetwork(args.source_address, args.query_address), xorriso=args.xorriso,
        )
    except (KeyError, OSError, ValueError):
        print("EXTERNAL_TABLES_BOOT_MEDIA|FAIL", file=sys.stderr)
        return 1
    print(json.dumps({"sha256": digest}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
