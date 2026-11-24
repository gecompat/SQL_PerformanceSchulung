"""Prepare the pinned offline .NET SDK and verify the query guest execution service."""

from __future__ import annotations

from hashlib import file_digest
import os
from pathlib import Path
import re
import socket
import tarfile
from time import sleep
from typing import BinaryIO

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from external_tables_guest_identity import _remaining


_DOTNET_HOME = Path("/opt/mssql-ees-dotnet")
_EXECUTION_SERVICE = "mssql-ees.service"
_SERVICE_PORT = 25100
_SYSTEMCTL = "/usr/bin/systemctl"
_PROC_ROOT = Path("/proc")


def _verify_payload(payload: BinaryIO, entry: dict) -> None:
    if (
        os.fstat(payload.fileno()).st_size != entry["size"]
        or file_digest(payload, "sha512").hexdigest() != entry["sha512"]
    ):
        raise ValueError(".NET SDK archive bytes differ from the locked artifact")


def verify_dotnet_archive(archive: Path, entry: dict) -> None:
    """Reject media whose SDK differs from the pinned archive."""
    with archive.open("rb") as payload:
        _verify_payload(payload, entry)


def install_dotnet_sdk(staging: Path, entry: dict, deadline: float, *, destination: Path = _DOTNET_HOME) -> None:
    """Install the verified archive in the vendor directory before PolyBase package configuration."""
    archive = staging / entry["filename"]
    _remaining(deadline)
    with archive.open("rb") as payload:
        _verify_payload(payload, entry)
        _remaining(deadline)
        payload.seek(0)
        destination.mkdir(mode=0o755)
        try:
            with tarfile.open(fileobj=payload, mode="r|gz") as sdk:
                for member in sdk:
                    _remaining(deadline)
                    sdk.extract(member, path=destination, filter="data")
        except tarfile.TarError:
            raise ValueError("could not extract the pinned .NET SDK") from None

    sdk_version = entry["sdk_version"]
    runtime_version = entry["runtime_version"]
    dotnet = str(destination / "dotnet")
    if _command([dotnet, "--list-sdks"], deadline).splitlines() != [
        f"{sdk_version} [{destination / 'sdk'}]".encode()
    ]:
        raise ValueError("installed .NET SDK does not match the locked version")
    runtimes = set(_command([dotnet, "--list-runtimes"], deadline).splitlines())
    frameworks = ("Microsoft.NETCore.App", "Microsoft.AspNetCore.App")
    expected = {f"{name} {runtime_version} [{destination / 'shared' / name}]".encode() for name in frameworks}
    if runtimes != expected:
        raise ValueError("installed .NET runtimes do not match the locked versions")


def ensure_polybase_service_setup(sdk_version: str, deadline: float) -> None:
    """Complete the offline vendor setup if the package hook skipped the service account."""
    _remaining(deadline)
    if _execution_account_present():
        return
    if _command([str(_DOTNET_HOME / "dotnet"), "--version"], deadline).strip() != sdk_version.encode("ascii"):
        raise ValueError("the PolyBase installer requires the locked local .NET SDK")
    _command(["/usr/bin/bash", "/opt/mssql/bin/installexecutionservice.sh", "--non-interactive"], deadline)
    if not _execution_account_present():
        raise ValueError("the PolyBase installer did not create the service account")


def _execution_account_present() -> bool:
    import grp
    import pwd

    try:
        account = pwd.getpwnam("mssql_ees")
    except KeyError:
        return False
    try:
        engine_group = grp.getgrnam("mssql").gr_gid
    except KeyError:
        raise ValueError("the PolyBase execution account has no SQL Server group") from None
    if account.pw_uid <= 0 or engine_group <= 0 or engine_group not in os.getgrouplist(account.pw_name, account.pw_gid):
        raise ValueError("the PolyBase execution account or SQL Server group is invalid")
    return True


def verify_polybase_service(deadline: float) -> None:
    """Confirm the official query-node service and its local listener before SQL admission."""
    _command([_SYSTEMCTL, "start", _EXECUTION_SERVICE], deadline)
    _command([_SYSTEMCTL, "is-active", "--quiet", _EXECUTION_SERVICE], deadline)
    pid = _service_pid(deadline)
    process = _PROC_ROOT / str(pid)
    if (process / "exe").resolve(strict=True) != (_DOTNET_HOME / "dotnet").resolve(strict=True):
        raise ValueError("PolyBase execution service does not run the prepared .NET binary")
    while True:
        try:
            with socket.create_connection(("127.0.0.1", _SERVICE_PORT), timeout=min(1, _remaining(deadline))):
                break
        except (ConnectionRefusedError, TimeoutError):
            sleep(min(0.25, _remaining(deadline)))
    if _service_pid(deadline) != pid:
        raise ValueError("PolyBase execution service changed during local readiness verification")


def _service_pid(deadline: float) -> int:
    value = _command([_SYSTEMCTL, "show", "--property=MainPID", "--value", _EXECUTION_SERVICE], deadline).strip()
    if re.fullmatch(rb"[1-9][0-9]{0,9}", value) is None:
        raise ValueError("PolyBase execution service did not return one active process")
    return int(value)


def _command(arguments: list[str], deadline: float) -> bytes:
    try:
        result = collect_bounded_process(
            arguments, input_bytes=b"", timeout_seconds=min(60, _remaining(deadline)), timeout_ceiling_seconds=60,
            environment={
                "LC_ALL": "C", "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
                "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1",
            },
            stdout_limit_bytes=65536, stderr_limit_bytes=65536,
        )
    except CaptureRunnerError:
        raise OSError("offline PolyBase preparation command did not complete") from None
    if result.returncode:
        raise OSError("offline PolyBase preparation command failed")
    return result.stdout
