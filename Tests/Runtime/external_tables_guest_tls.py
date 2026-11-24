"""Set up source TLS and forward only the role-bound public trust anchor."""

from __future__ import annotations

from collections.abc import Callable
from hashlib import sha256
import os
from pathlib import Path
import re
import socket
from ssl import PEM_cert_to_DER_cert
from struct import Struct
import sys
from tempfile import TemporaryDirectory
from uuid import UUID

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from external_tables_guest_identity import (
    GuestPhase, _receive, _remaining, _reply_to_probe, _send, accept_parent_connection, connect_verified_guest,
)
from external_tables_guest_network import GuestNetwork
from external_tables_pilot_sql import Role, source_host
from external_tables_tls_material import _PUBLIC_CA_LIMIT, _openssl, issue_source_tls


_FRAME = Struct("!4sH")
_ACK = Struct("!4s32s")
_CERT = b"CA01"
_INSTALLED = b"CAOK"
_PEM = re.compile(rb"-----BEGIN CERTIFICATE-----\n(?:[A-Za-z0-9+/=]+\n)+-----END CERTIFICATE-----\n")
_SQL_DIRECTORY = Path("/var/opt/mssql")
_CA_DIRECTORY = Path("/usr/local/share/ca-certificates")
_HOSTS = Path("/etc/hosts")
_MSSQL_CONF = "/opt/mssql/bin/mssql-conf"


def relay_guest_ca(
    source_vm: UUID, query_vm: UUID, port: int, token: str, deadline: float, *,
    base_status: bytes, package_lock: dict,
) -> None:
    """Receive and install one public CA on the two separately verified guest channels."""
    options = dict(base_status=base_status, package_lock=package_lock, phase=GuestPhase.TLS, wait=True)
    with connect_verified_guest(source_vm, port, token, Role.SOURCE, deadline, **options) as channel:
        certificate = _receive_ca(channel, deadline)
    with connect_verified_guest(query_vm, port, token, Role.QUERY, deadline, **options) as channel:
        _send_ca(channel, certificate, deadline)
        if _receive(channel, _ACK.size, deadline) != _ACK.pack(_INSTALLED, sha256(certificate).digest()):
            raise ValueError("query guest did not confirm installation of the source CA")


def prepare_guest_tls(port: int, token: str, role: Role, network: GuestNetwork, deadline: float) -> None:
    """Configure the source certificate or confirm the query guest's verified trust store."""
    if sys.platform != "linux" or os.geteuid() != 0:
        raise ValueError("TLS preparation requires the prepared Linux guest")
    if role is Role.SOURCE:
        certificate = _configure_source_tls(token, deadline)
        with accept_parent_connection(port, deadline) as channel:
            _reply_to_probe(channel, token, role, deadline, phase=GuestPhase.TLS)
            _send_ca(channel, certificate, deadline)
    else:
        with accept_parent_connection(port, deadline) as channel:
            _receive_query_trust(channel, token, deadline, lambda ca: _install_query_trust(token, network, ca, deadline))


def _receive_query_trust(
    channel: socket.socket, token: str, deadline: float, install: Callable[[bytes], None],
) -> None:
    _reply_to_probe(channel, token, Role.QUERY, deadline, phase=GuestPhase.TLS)
    certificate = _receive_ca(channel, deadline)
    install(certificate)
    _send(channel, _ACK.pack(_INSTALLED, sha256(certificate).digest()), deadline)


def _send_ca(channel: socket.socket, certificate: bytes, deadline: float) -> None:
    _validate_pem(certificate)
    _send(channel, _FRAME.pack(_CERT, len(certificate)) + certificate, deadline)


def _receive_ca(channel: socket.socket, deadline: float) -> bytes:
    tag, size = _FRAME.unpack(_receive(channel, _FRAME.size, deadline))
    if tag != _CERT or not 0 < size <= _PUBLIC_CA_LIMIT:
        raise ValueError("unexpected public CA frame")
    certificate = _receive(channel, size, deadline)
    _validate_pem(certificate)
    return certificate


def _validate_pem(certificate: bytes) -> None:
    if not 0 < len(certificate) <= _PUBLIC_CA_LIMIT or not _PEM.fullmatch(certificate):
        raise ValueError("expected exactly one bounded public CA certificate")
    try:
        PEM_cert_to_DER_cert(certificate.decode("ascii"))
    except (UnicodeError, ValueError):
        raise ValueError("invalid public CA certificate") from None


def _configure_source_tls(token: str, deadline: float) -> bytes:
    from pwd import getpwnam

    host = source_host(token)
    account = getpwnam("mssql")
    directory = _SQL_DIRECTORY / f"{host}-tls"
    directory.mkdir(mode=0o700)
    with issue_source_tls(token, directory, deadline) as material:
        certificate = directory / "source.crt"
        key = directory / "source.key"
        # Transfer namespace ownership inside the same disposable source guest only.
        material.certificate.replace(certificate)
        material.private_key.replace(key)
        for path in (certificate, key, directory):
            os.chown(path, account.pw_uid, account.pw_gid)
        for setting, value in (
            ("network.tlscert", str(certificate)),
            ("network.tlskey", str(key)),
            ("network.forceencryption", "1"),
        ):
            _run_linux([_MSSQL_CONF, "set", setting, value], deadline)
        return material.ca_certificate


def _install_query_trust(token: str, network: GuestNetwork, certificate: bytes, deadline: float) -> None:
    host = source_host(token)
    expected_subject = f"subject=CN=SQLPERF Lab CA {host}".encode("ascii")
    with TemporaryDirectory(prefix="sqlperf-query-ca-") as folder:
        staging = Path(folder) / "ca.crt"
        staging.write_bytes(certificate)
        subject = _openssl(["x509", "-in", str(staging), "-noout", "-subject", "-nameopt", "RFC2253"], deadline)
        constraints = _openssl(["x509", "-in", str(staging), "-noout", "-ext", "basicConstraints"], deadline)
        if subject.strip() != expected_subject or b"CA:TRUE, pathlen:0" not in constraints:
            raise ValueError("source CA certificate does not match the run profile")
        _openssl(["verify", "-CAfile", str(staging), "-no-CApath", "-no-CAstore", "-check_ss_sig", str(staging)], deadline)
        destination = _CA_DIRECTORY / f"{host}.crt"
        with destination.open("xb") as output:
            output.write(certificate)
    _run_linux(["/usr/sbin/update-ca-certificates"], deadline)
    address = str(network.source.ip)
    with _HOSTS.open("r+", encoding="utf-8") as hosts:
        original = hosts.read()
        if any(host in line.split("#", 1)[0].lower().split()[1:] for line in original.splitlines()):
            raise ValueError("source name already exists in the query guest resolver")
        hosts.write(f"\n{address} {host}\n")
    result = _run_linux(["/usr/bin/getent", "ahostsv4", host], deadline)
    addresses = {line.split()[0].decode("ascii") for line in result.splitlines() if line.split()}
    if addresses != {address}:
        raise ValueError("query guest resolver did not return the exact source address")


def _run_linux(command: list[str], deadline: float) -> bytes:
    try:
        result = collect_bounded_process(
            command, input_bytes=b"", environment={"LC_ALL": "C", "PATH": "/usr/sbin:/usr/bin:/sbin:/bin"},
            timeout_seconds=min(20, _remaining(deadline)), stdout_limit_bytes=65536, stderr_limit_bytes=65536,
        )
    except CaptureRunnerError:
        raise OSError("guest TLS setup command did not complete") from None
    if result.returncode:
        raise OSError("guest TLS setup command failed")
    return result.stdout
