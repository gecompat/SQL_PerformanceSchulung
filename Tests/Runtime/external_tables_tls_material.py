"""Issue run-bound TLS material on the disposable External Tables source guest."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path
from secrets import randbits
from tempfile import TemporaryDirectory
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from external_tables_pilot_sql import source_host


_OPENSSL = "/usr/bin/openssl"
_PUBLIC_CA_LIMIT = 16 * 1024


@dataclass(frozen=True)
class SourceTlsMaterial:
    certificate: Path = field(repr=False)
    private_key: Path = field(repr=False)
    ca_certificate: bytes = field(repr=False)


@contextmanager
def issue_source_tls(token: str, work_root: Path, deadline: float) -> Iterator[SourceTlsMaterial]:
    """Keep the leaf key on the source guest and return only the public trust anchor for transfer."""
    host = source_host(token)
    root = work_root.resolve(strict=True)
    with TemporaryDirectory(prefix="sqlperf-source-tls-", dir=root) as directory:
        work = Path(directory)
        leaf_cert = work / "source.crt"
        leaf_key = work / "source.key"
        with TemporaryDirectory(prefix="signing-", dir=work) as signing_directory:
            signing = Path(signing_directory)
            config = signing / "openssl.cnf"
            ca_cert = signing / "ca.crt"
            ca_key = signing / "ca.key"
            request = signing / "source.csr"
            config.write_text(_config(host), encoding="ascii", newline="\n")
            _openssl([
                "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-sha256", "-days", "1",
                "-config", str(config), "-extensions", "issuer", "-subj", f"/CN=SQLPERF Lab CA {host}",
                "-keyout", str(ca_key), "-out", str(ca_cert),
            ], deadline)
            _openssl([
                "req", "-new", "-newkey", "rsa:2048", "-nodes", "-sha256", "-config", str(config),
                "-subj", f"/CN={host}", "-keyout", str(leaf_key), "-out", str(request),
            ], deadline)
            _openssl([
                "x509", "-req", "-in", str(request), "-CA", str(ca_cert), "-CAkey", str(ca_key),
                "-set_serial", f"0x{randbits(158) + (1 << 158):x}", "-days", "1", "-sha256",
                "-extfile", str(config), "-extensions", "server", "-out", str(leaf_cert),
            ], deadline)
            _openssl([
                "verify", "-CAfile", str(ca_cert), "-no-CApath", "-no-CAstore",
                "-purpose", "sslserver", "-verify_hostname", host, str(leaf_cert),
            ], deadline)
            san = _openssl(["x509", "-in", str(leaf_cert), "-noout", "-ext", "subjectAltName"], deadline)
            san_lines = san.decode("ascii").splitlines()
            if len(san_lines) != 2 or san_lines[1].strip() != f"DNS:{host}":
                raise ValueError("source certificate does not contain exactly the run-bound DNS SAN")

            key_public = _openssl(["pkey", "-in", str(leaf_key), "-pubout"], deadline)
            cert_public = _openssl(["x509", "-in", str(leaf_cert), "-pubkey", "-noout"], deadline)
            if key_public != cert_public:
                raise ValueError("source private key does not match the leaf certificate")
            with ca_cert.open("rb") as public:
                ca_certificate = public.read(_PUBLIC_CA_LIMIT + 1)
            if not ca_certificate or len(ca_certificate) > _PUBLIC_CA_LIMIT:
                raise ValueError("source CA certificate exceeds the PEM profile")
        leaf_key.chmod(0o400)
        leaf_cert.chmod(0o400)
        _remaining(deadline)
        yield SourceTlsMaterial(leaf_cert, leaf_key, ca_certificate)


def _config(host: str) -> str:
    return f"""[req]
distinguished_name = distinguished_name
[distinguished_name]
[issuer]
basicConstraints = critical,CA:TRUE,pathlen:0
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
[server]
basicConstraints = critical,CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
authorityKeyIdentifier = keyid
subjectAltName = DNS:{host}
"""


def _remaining(deadline: float) -> float:
    remaining = deadline - monotonic()
    if not isfinite(remaining) or remaining <= 0:
        raise TimeoutError("source TLS material deadline exceeded")
    return remaining


def _openssl(options: list[str], deadline: float) -> bytes:
    try:
        result = collect_bounded_process(
            [_OPENSSL, *options], input_bytes=b"", environment={"LC_ALL": "C"},
            timeout_seconds=min(12, _remaining(deadline)), stdout_limit_bytes=32_768, stderr_limit_bytes=32_768,
        )
    except CaptureTimeoutError:
        raise TimeoutError("source TLS material deadline exceeded") from None
    except CaptureRunnerError:
        raise OSError("could not confirm the OpenSSL operation") from None
    if result.returncode:
        raise OSError("could not confirm the OpenSSL operation")
    _remaining(deadline)
    return result.stdout
