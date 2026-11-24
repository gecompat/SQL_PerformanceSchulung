"""Run the admitted External Tables pilot from the provider's verified host inputs."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from time import monotonic
from typing import BinaryIO
from uuid import uuid4

from external_tables_guest_identity import _remaining, linux_service_id, require_registered_hyperv_ports
from external_tables_hyperv_host import (
    BootstrapMedia, HyperVPreparedTransport, provision_detached_hyperv, recover_partial_hyperv, run_prepared_hyperv_pilot,
)
from external_tables_package_state import read_dpkg_status
from external_tables_pilot import CLEANUP_SECONDS, WORK_SECONDS, PilotResult
from external_tables_pilot_sql import Role, database_name


_LOCK = Path(__file__).resolve().parents[2] / "Documentation/Project_Planning/external_tables_apt_lock.json"


@dataclass(frozen=True)
class PilotInputs:
    token: str
    directory: Path
    template: Path
    template_sha256: str
    source_iso: Path
    query_iso: Path
    media: BootstrapMedia
    base_status: Path
    bootstrap_port: int
    sql_port: int
    expected_driver_sha256: str | None = None


def run_hyperv_lab(inputs: PilotInputs, *, apply: bool = False) -> PilotResult:
    """Validate host and artifacts before any effect; then run exactly one owned pilot."""
    deadline = monotonic() + WORK_SECONDS
    try:
        database_name(inputs.token, Role.SOURCE)
        linux_service_id(inputs.bootstrap_port)
        linux_service_id(inputs.sql_port)
        if inputs.bootstrap_port == inputs.sql_port:
            raise ValueError("expected distinct Hyper-V service ports")
        require_registered_hyperv_ports(inputs.bootstrap_port, inputs.sql_port)
    except (OSError, ValueError):
        return PilotResult("NOT_PROVEN", "host_services", None, False, False)
    try:
        directory = inputs.directory.resolve(strict=True)
        if not directory.is_dir() or any(directory.iterdir()):
            raise ValueError("expected the empty provider run directory")
        if inputs.expected_driver_sha256 is not None and re.fullmatch(r"[0-9a-f]{64}", inputs.expected_driver_sha256) is None:
            raise ValueError("expected a reviewed lowercase driver SHA-256")
        lock = json.loads(_LOCK.read_bytes())
        base_status = read_dpkg_status(inputs.base_status)
        if sha256(base_status).hexdigest() != lock["dpkg_status_sha256"]:
            raise ValueError("the base package state differs from the lock")
        _check_input(inputs.template, ".vhdx", inputs.template_sha256, deadline)
        media = (
            (inputs.source_iso, directory / "source.iso", inputs.media.source_sha256),
            (inputs.query_iso, directory / "query.iso", inputs.media.query_sha256),
        )
        for source, _, digest in media:
            _check_input(source, ".iso", digest, deadline)
    except (KeyError, OSError, ValueError):
        return PilotResult("NOT_PROVEN", "host_inputs", None, False, False)
    if not apply:
        return PilotResult("VERIFIED", "host_preflight", None, False, False)

    attempt = uuid4()
    try:
        journal = provision_detached_hyperv(
            directory, inputs.token, inputs.sql_port, deadline,
            source_template=inputs.template, source_sha256=inputs.template_sha256,
            query_template=inputs.template, query_sha256=inputs.template_sha256, attempt_id=attempt,
        )
    except (OSError, ValueError):
        try:
            recover_partial_hyperv(directory, inputs.token, attempt, monotonic() + CLEANUP_SECONDS)
        except (OSError, ValueError):
            return PilotResult("FAIL_CLEANUP", "guest_provisioning", None, True, False)
        return PilotResult("NOT_PROVEN", "guest_provisioning", None, True, True)

    stage = "host_media_staging"
    try:
        for source, destination, digest in media:
            _stage_iso(source, destination, digest, deadline)
        stage = "host_handoff"
        return run_prepared_hyperv_pilot(
            journal, base_status, lock, bootstrap_port=inputs.bootstrap_port, boot_media=inputs.media,
            expected_driver_sha256=inputs.expected_driver_sha256,
        )
    except (OSError, ValueError):
        cleanup = HyperVPreparedTransport(journal, base_status, lock)
        try:
            absent = cleanup.discard_unstarted_guests(monotonic() + CLEANUP_SECONDS)
        except (OSError, ValueError):
            absent = False
        return PilotResult("NOT_PROVEN" if absent else "FAIL_CLEANUP", stage, None, True, absent)


def _check_input(path: Path, suffix: str, expected: str, deadline: float) -> None:
    if path.suffix.lower() != suffix or not path.is_file():
        raise ValueError("unexpected input file type")
    with path.open("rb") as source:
        _copy_verified(source, expected, deadline)


def _stage_iso(path: Path, destination: Path, expected: str, deadline: float) -> None:
    with NamedTemporaryFile(prefix=".external-tables-media-", dir=destination.parent, delete=False) as temporary:
        staging = Path(temporary.name)
        try:
            with path.open("rb") as source:
                _copy_verified(source, expected, deadline, temporary)
            temporary.close()
            os.link(staging, destination)
        finally:
            temporary.close()
            staging.unlink()


def _copy_verified(
    source: BinaryIO, expected: str, deadline: float, destination: BinaryIO | None = None,
) -> None:
    if re.fullmatch(r"[0-9a-fA-F]{64}", expected) is None:
        raise ValueError("expected one SHA-256 value")
    digest = sha256()
    size = 0
    while data := source.read(4 * 1024 * 1024):
        _remaining(deadline)
        size += len(data)
        digest.update(data)
        if destination is not None:
            destination.write(data)
    if not size or digest.hexdigest() != expected.lower():
        raise ValueError("host artifact bytes do not match the expected SHA-256")
    _remaining(deadline)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--token", required=True)
    parser.add_argument("--run-directory", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--template-sha256", required=True)
    parser.add_argument("--source-iso", required=True, type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--query-iso", required=True, type=Path)
    parser.add_argument("--query-sha256", required=True)
    parser.add_argument("--base-status", required=True, type=Path)
    parser.add_argument("--bootstrap-port", required=True, type=int)
    parser.add_argument("--sql-port", required=True, type=int)
    parser.add_argument("--driver-sha256", help="reviewed Connector Driver 18 digest")
    parser.add_argument("--apply-owned-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        media = BootstrapMedia(args.source_sha256, args.query_sha256)
        inputs = PilotInputs(
            args.token, args.run_directory, args.template, args.template_sha256, args.source_iso, args.query_iso, media,
            args.base_status, args.bootstrap_port, args.sql_port, args.driver_sha256,
        )
    except ValueError:
        result = PilotResult("NOT_PROVEN", "host_inputs", None, False, False)
    else:
        result = run_hyperv_lab(inputs, apply=args.apply_owned_run)
    print(json.dumps(asdict(result)))
    return 0 if result.status in ("VERIFIED", "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
