"""Start the bounded SQL command service inside a prepared pilot guest."""

from __future__ import annotations

import argparse
from ipaddress import IPv4Interface
import json
import os
from pathlib import Path
from select import select
import sys
from time import monotonic

from external_tables_guest_admin import serve_guest_admin
from external_tables_guest_identity import _remaining, linux_service_id
from external_tables_guest_network import GuestNetwork, verify_guest_network
from external_tables_odbc import LocalGuestConnections, load_pinned_pyodbc
from external_tables_pilot import CLEANUP_SECONDS, WORK_SECONDS
from external_tables_pilot_sql import Role, database_name
from external_tables_source_firewall import SOURCE_INTERFACE, verify_source_firewall
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
        interface = verify_guest_network(network, role, deadline)
        if role is Role.SOURCE:
            if interface != SOURCE_INTERFACE:
                raise ValueError("guest interface does not match its source firewall")
            verify_source_firewall(network, SOURCE_INTERFACE, deadline)
        wheel_lock = json.loads(_LOCK.read_text(encoding="utf-8"))["python_wheel"]
        driver = load_pinned_pyodbc(Path(args.wheel_directory), wheel_lock)
        connections = LocalGuestConnections(driver, args.token, role, admin_secret)
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
