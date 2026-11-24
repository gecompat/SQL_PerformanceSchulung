"""Prepare a pilot guest and attest readiness before network attachment."""

from __future__ import annotations

import argparse
from ipaddress import IPv4Interface
import json
from pathlib import Path
import sys
from time import monotonic

from external_tables_guest_apt import install_verified_guest_packages, require_guest_detached
from external_tables_guest_identity import linux_service_id, serve_detached_guest_ready
from external_tables_guest_network import GuestNetwork
from external_tables_pilot import WORK_SECONDS
from external_tables_pilot_sql import Role, database_name
from external_tables_source_firewall import SOURCE_INTERFACE, install_source_firewall, verify_source_firewall


_LOCK = Path(__file__).resolve().parents[2] / "Documentation/Project_Planning/external_tables_apt_lock.json"


def prepare_detached_guest(
    token: str, role: Role, port: int, network: GuestNetwork, staging: Path, wheel_directory: Path, deadline: float,
) -> None:
    """Publish one phase-specific reply only after successful offline preparation."""
    database_name(token, role)
    linux_service_id(port)
    package_lock = json.loads(_LOCK.read_text(encoding="utf-8"))
    install_verified_guest_packages(staging, package_lock, role, deadline, wheel_install_dir=wheel_directory)
    if role is Role.SOURCE:
        install_source_firewall(network, SOURCE_INTERFACE, deadline)

    def verify_ready() -> None:
        if role is Role.SOURCE:
            verify_source_firewall(network, SOURCE_INTERFACE, deadline)
        require_guest_detached()

    serve_detached_guest_ready(port, token, role, deadline, verify_ready=verify_ready)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--token", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--source-address", required=True, type=IPv4Interface)
    parser.add_argument("--query-address", required=True, type=IPv4Interface)
    parser.add_argument("--staging", required=True, type=Path)
    parser.add_argument("--wheel-directory", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        network = GuestNetwork(args.source_address, args.query_address)
        prepare_detached_guest(
            args.token, Role(args.role), args.port, network, args.staging, args.wheel_directory,
            monotonic() + WORK_SECONDS,
        )
    except (KeyError, OSError, ValueError):
        print("EXTERNAL_TABLES_GUEST_BOOTSTRAP|FAIL", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
