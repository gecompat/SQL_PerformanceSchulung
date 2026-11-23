"""Verify the fixed Microsoft artifacts for the External Tables pilot proposal."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import file_digest, sha256
from pathlib import Path
import re
import subprocess
import tempfile


SIGNER = "BC528686B50D79E339D3721CEB3E94ADBE1229CF"
INDEX_PATH = "main/binary-amd64/Packages"
VERSION = "17.0.5065.9-3"
SDK_FILE = "dotnet-sdk-8.0.418-linux-x64.tar.gz"
SDK_SHA512 = (
    "fbd9fc9f0bca73f771e79c12d721a18da97ba23c43794b941b110ccaac0fcd1615"
    "6c996a5b9cfc0650120601791f2909e93ecb268f687c7b82889934c766c2b9"
)


@dataclass(frozen=True)
class Package:
    name: str
    size: int
    digest: str

    @property
    def filename(self) -> str:
        return f"{self.name}_{VERSION}_amd64.deb"


PACKAGES = (
    Package("mssql-server", 297677914, "1174d93bf5384b45ef528353cc8f6829aa0ab12669700e96bfd4e2959a0de3ff"),
    Package("mssql-server-polybase", 51433158, "302acda716e373d785dc8f1c394d762deb498010cbf96f10af679bba08b2c32a"),
)


def _read_bounded(path: Path, maximum: int) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    if not data or len(data) > maximum:
        raise ValueError(f"invalid size for {path.name}")
    return data


def open_signed_release(directory: Path) -> str:
    key = _read_bounded(directory / "microsoft.asc", 32_768)
    envelope = _read_bounded(directory / "InRelease", 65_536)
    with tempfile.TemporaryDirectory(prefix="polybase-keyring-") as home:
        command = ["gpg", "--no-options", "--homedir", ".", "--batch", "--no-auto-key-retrieve"]
        imported = subprocess.run(
            [*command, "--import"], cwd=home, input=key, capture_output=True, timeout=15, check=False,
        )
        if imported.returncode:
            raise ValueError("repository key could not be imported into the isolated keyring")
        verified = subprocess.run(
            [*command, "--status-fd", "2", "--decrypt"], cwd=home, input=envelope,
            capture_output=True, timeout=15, check=False,
        )
        signatures = re.findall(rb"^\[GNUPG:\] VALIDSIG ([0-9A-F]+) ", verified.stderr, re.MULTILINE)
        if verified.returncode or signatures != [SIGNER.encode("ascii")]:
            raise ValueError("InRelease does not have the expected Microsoft signer")
        return verified.stdout.decode("utf-8")


def check_signed_index(release: str, index: bytes) -> None:
    if any(f"{key}: noble" not in release.splitlines() for key in ("Codename", "Suite")):
        raise ValueError("signed release is not for Ubuntu Noble")
    sections = re.findall(r"^SHA256:\n((?:[ \t]+[^\n]+\n?)+)", release, re.MULTILINE)
    if len(sections) != 1:
        raise ValueError("expected one SHA256 section in the signed release")
    entries = [line.split() for line in sections[0].splitlines()]
    matches = [fields for fields in entries if len(fields) == 3 and fields[2] == INDEX_PATH]
    expected = [sha256(index).hexdigest(), str(len(index)), INDEX_PATH]
    if matches != [expected]:
        raise ValueError("apt index does not match the signed SHA-256 and size")

    seen: set[str] = set()
    pins = {package.name: package for package in PACKAGES}
    for stanza in index.decode("utf-8").split("\n\n"):
        fields = [line.split(": ", 1) for line in stanza.splitlines() if line and not line[0].isspace()]
        record = dict(fields)
        name = record.get("Package", "")
        if name not in pins or record.get("Version") != VERSION:
            continue
        package = pins[name]
        expected_path = f"pool/main/m/{name}/{package.filename}"
        if (
            len(record) != len(fields)
            or name in seen
            or record.get("Architecture") != "amd64"
            or record.get("Filename") != expected_path
            or record.get("Size") != str(package.size)
            or record.get("SHA256") != package.digest
        ):
            raise ValueError(f"unexpected signed record for {name}")
        seen.add(name)
    if seen != pins.keys():
        raise ValueError("signed index is missing an exact package pin")


def check_payloads(directory: Path) -> None:
    for package in PACKAGES:
        path = directory / package.filename
        if path.stat().st_size != package.size:
            raise ValueError(f"unexpected size for {package.name}")
        _check_file(path, "sha256", package.digest)
    _check_file(directory / SDK_FILE, "sha512", SDK_SHA512)


def _check_file(path: Path, algorithm: str, expected: str) -> None:
    with path.open("rb") as stream:
        if file_digest(stream, algorithm).hexdigest() != expected:
            raise ValueError(f"unexpected digest for {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index_directory", type=Path, help="directory with microsoft.asc, InRelease and Packages")
    parser.add_argument("--payload-directory", type=Path, help="also check both .deb files and the .NET SDK archive")
    args = parser.parse_args()
    try:
        index = _read_bounded(args.index_directory / "Packages", 2 * 1024 * 1024)
        check_signed_index(open_signed_release(args.index_directory), index)
        print("PASS signed Ubuntu Noble index and both exact SQL package records")
        if args.payload_directory is not None:
            check_payloads(args.payload_directory)
            print("PASS two SQL packages and .NET SDK archive bytes")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"FAIL {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
