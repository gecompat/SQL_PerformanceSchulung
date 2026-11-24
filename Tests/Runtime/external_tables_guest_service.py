"""Start the bounded SQL command service inside a prepared pilot guest."""

from __future__ import annotations

import argparse
from ipaddress import IPv4Interface
import json
import os
from pathlib import Path
from secrets import token_hex
from select import select
import sys
from time import monotonic, sleep

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from external_tables_guest_admin import serve_guest_admin
from external_tables_guest_identity import _remaining, linux_service_id
from external_tables_guest_network import PILOT_INTERFACE, GuestNetwork, verify_guest_network
from external_tables_odbc import LocalGuestConnections, OdbcDriver, OdbcPilotAdministration, load_pinned_pyodbc
from external_tables_pilot import CLEANUP_SECONDS, WORK_SECONDS
from external_tables_pilot_sql import SOURCE_PORT, Role, database_name
from external_tables_polybase_service import verify_polybase_service
from external_tables_source_firewall import verify_source_firewall
from external_tables_principals import PASSWORD


_LOCK = Path(__file__).resolve().parents[2] / "Documentation/Project_Planning/external_tables_apt_lock.json"
_SECRET_BYTES = len("Ext9!") + 32


def read_startup_secret(fd: int, deadline: float) -> str:
    """Read exactly one generated secret and EOF from the private input pipe."""
    payload = bytearray()
    while len(payload) <= _SECRET_BYTES:
        ready, _, _ = select((fd,), (), (), _remaining(deadline))
        if not ready:
            raise TimeoutError("guest startup input was not completed")
        chunk = os.read(fd, _SECRET_BYTES + 1 - len(payload))
        if not chunk:
            break
        payload.extend(chunk)
    try:
        secret = payload.decode("ascii")
    except UnicodeError:
        raise ValueError("invalid guest startup input") from None
    if not PASSWORD.fullmatch(secret):
        raise ValueError("invalid guest startup input")
    return secret


def run_guest_engine(
    port: int, token: str, role: Role, network: GuestNetwork, wheel_directory: Path, deadline: float,
) -> None:
    """Start the fresh role instance, prove it locally, then expose its fixed SQL service."""
    database_name(token, role)
    linux_service_id(port)
    if sys.platform != "linux" or os.geteuid() != 0:
        raise ValueError("SQL setup requires the prepared Linux guest")
    secret = "Ext9!" + token_hex(16)
    driver, connections = _open_guest_connections(token, role, network, wheel_directory, secret, deadline)
    _configure_engine(secret, deadline)
    while True:
        limit = min(2, int(_remaining(deadline)))
        if limit < 1:
            raise TimeoutError("local SQL startup deadline exceeded")
        try:
            ready = connections.admin("master", limit)
        except OSError:
            sleep(min(0.25, _remaining(deadline)))
        else:
            ready.close()
            break
    OdbcPilotAdministration(token, role, connections.admin).prepare_instance(deadline)
    if role is Role.QUERY:
        verify_polybase_service(deadline)
    serve_guest_admin(
        port, token, role, connections.admin, deadline + CLEANUP_SECONDS, open_principal=connections.principal,
        source_driver=driver if role is Role.QUERY else None, network=network,
    )


def _configure_engine(secret: str, deadline: float) -> None:
    try:
        result = collect_bounded_process(
            ["/opt/mssql/bin/mssql-conf", "-n", "setup"], input_bytes=b"",
            environment={
                "PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL": "C", "ACCEPT_EULA": "Y",
                "MSSQL_PID": "EnterpriseDeveloper", "MSSQL_SA_PASSWORD": secret, "MSSQL_TCP_PORT": str(SOURCE_PORT),
            },
            timeout_seconds=min(WORK_SECONDS, _remaining(deadline)), timeout_ceiling_seconds=WORK_SECONDS,
            stdout_limit_bytes=65536, stderr_limit_bytes=65536,
        )
    except CaptureRunnerError:
        raise OSError("local SQL engine setup did not complete") from None
    if result.returncode:
        raise OSError("local SQL engine setup failed")


def _open_guest_connections(
    token: str, role: Role, network: GuestNetwork, wheel_directory: Path, admin_secret: str, deadline: float,
) -> tuple[OdbcDriver, LocalGuestConnections]:
    interface = verify_guest_network(network, role, deadline)
    if role is Role.SOURCE:
        if interface != PILOT_INTERFACE:
            raise ValueError("guest interface does not match its source firewall")
        verify_source_firewall(network, PILOT_INTERFACE, deadline)
    wheel_lock = json.loads(_LOCK.read_text(encoding="utf-8"))["python_wheel"]
    driver = load_pinned_pyodbc(wheel_directory, wheel_lock)
    return driver, LocalGuestConnections(driver, token, role, admin_secret)


def main(argv: list[str] | None = None, *, secret_fd: int = 0) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--token", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--source-address", required=True)
    parser.add_argument("--query-address", required=True)
    parser.add_argument("--wheel-directory", required=True)
    args, unknown = parser.parse_known_args(argv)
    deadline = monotonic() + WORK_SECONDS + CLEANUP_SECONDS
    try:
        if unknown or sys.platform != "linux":
            raise ValueError("invalid guest service startup")
        port = int(args.port)
        linux_service_id(port)
        role = Role(args.role)
        database_name(args.token, role)
        network = GuestNetwork(IPv4Interface(args.source_address), IPv4Interface(args.query_address))
        admin_secret = read_startup_secret(secret_fd, min(deadline, monotonic() + 5))
        driver, connections = _open_guest_connections(
            args.token, role, network, Path(args.wheel_directory), admin_secret, deadline,
        )
        serve_guest_admin(
            port, args.token, role, connections.admin, deadline, open_principal=connections.principal,
            source_driver=driver if role is Role.QUERY else None, network=network,
        )
    except (KeyError, OSError, ValueError):
        print("EXTERNAL_TABLES_GUEST_SERVICE|FAIL", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
