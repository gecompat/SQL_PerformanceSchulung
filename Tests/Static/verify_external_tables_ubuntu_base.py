"""Check the pinned Ubuntu VHD manifest for the External Tables pilot."""
from __future__ import annotations

import argparse
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re


RELEASE = "20261017"
BASENAME = "ubuntu-24.04-server-cloudimg-amd64-azure.vhd"
MANIFEST_SHA256 = "68444fae3ee6e566917b9f4aec6bf94154d532cd3bd51ed63e308a56ece7d60a"
ARCHIVE_SHA256 = "cde3ca6a5aabe89702456cc5af69e2336600ce13c18898aba27e7212e3474e3f"
DIRECT_PACKAGES = (
    "adduser", "debconf", "gawk", "gdb", "hostname", "libatomic1", "libc++1", "libc6",
    "libgssapi-krb5-2", "libnuma1", "libpam0g", "libsasl2-2", "libsasl2-modules-gssapi-mit",
    "libsss-nss-idmap0", "libunwind8", "lsof", "openssl", "procps", "python3", "sed", "tzdata",
)
PACKAGE_NAME = re.compile(r"[a-z0-9][a-z0-9+.-]*(?::[a-z0-9][a-z0-9-]*)?", re.ASCII)


def parse_manifest(text: str) -> dict[str, str]:
    packages: dict[str, str] = {}
    seen: set[str] = set()
    for line in text.splitlines():
        fields = line.split()
        if len(fields) != 2 or not PACKAGE_NAME.fullmatch(fields[0]):
            raise ValueError("invalid Ubuntu manifest record")
        name, version = fields
        package, separator, architecture = name.partition(":")
        if name in seen:
            raise ValueError("duplicate package record in Ubuntu manifest")
        seen.add(name)
        if separator and architecture not in ("amd64", "all"):
            continue
        if package in packages:
            raise ValueError("ambiguous native package identity in Ubuntu manifest")
        packages[package] = version
    if not packages:
        raise ValueError("Ubuntu manifest has no native packages")
    return packages


def compare_direct_packages(packages: dict[str, str]) -> dict[str, object]:
    """Compare names only; the guest APT solver still resolves versions and dependencies."""
    return {
        "present": {name: packages[name] for name in DIRECT_PACKAGES if name in packages},
        "absent_from_base": [name for name in DIRECT_PACKAGES if name not in packages],
    }


def verify_manifest(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        manifest = stream.read(65_537)
    if len(manifest) > 65_536 or sha256(manifest).hexdigest() != MANIFEST_SHA256:
        raise ValueError("manifest does not match the pinned Canonical release")
    return compare_direct_packages(parse_manifest(manifest.decode("utf-8")))


def verify_archive(path: Path) -> None:
    if not 0 < path.stat().st_size <= 1024**3:
        raise ValueError("Ubuntu VHD archive has an unexpected size")
    with path.open("rb") as stream:
        if file_digest(stream, "sha256").hexdigest() != ARCHIVE_SHA256:
            raise ValueError("VHD archive does not match the pinned Canonical release")


def verify_derived_vhdx(path: Path) -> None:
    evidence_path = (
        Path(__file__).resolve().parents[2] / "Documentation" / "Project_Planning"
        / "external_tables_vhdx_evidence.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence["source_archive_sha256"] != ARCHIVE_SHA256 or evidence["derived_virtual_bytes"] != 24 * 1024**3:
        raise ValueError("derived VHDX evidence differs from the source or resource profile")
    with path.open("rb") as stream:
        if path.stat().st_size != evidence["derived_file_bytes"] or file_digest(stream, "sha256").hexdigest() != evidence["derived_sha256"]:
            raise ValueError("VHDX bytes do not match the locally verified candidate")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--archive", type=Path, help="also verify the downloaded Canonical VHD archive")
    parser.add_argument("--derived-vhdx", type=Path, help="also check the locally derived Hyper-V candidate")
    args = parser.parse_args()
    try:
        comparison = verify_manifest(args.manifest)
        if args.archive is not None:
            verify_archive(args.archive)
        if args.derived_vhdx is not None:
            verify_derived_vhdx(args.derived_vhdx)
        print(json.dumps({
            "release": RELEASE, "image": BASENAME, "archive_verified": args.archive is not None,
            "derived_vhdx_verified": args.derived_vhdx is not None, **comparison,
        }, sort_keys=True))
    except (OSError, ValueError) as exc:
        print(f"FAIL {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
