"""Read-only source-byte freeze checks for a DGN-007 execution window.

This helper proves only that the contract-pinned files matched at two local
filesystem observations. It does not prove which bytes a child process read.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from Tests.Contracts.dgn007_prospective_acceptance import (
    AcceptanceContract, SOURCE_FILES, _contract_valid,
)


class SourceFreezeError(ValueError):
    """Stable source-freeze failure without paths or file contents."""

    def __init__(self) -> None:
        super().__init__("FAIL_CONTRACT")


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    source_digest: str
    hashes: tuple[tuple[str, str], ...]


def capture_source_snapshot(root: Path, contract: AcceptanceContract) -> SourceSnapshot:
    """Hash the exact contract source set using its LF-normalized UTF-8 rule."""
    if not isinstance(root, Path) or type(contract) is not AcceptanceContract or not _contract_valid(contract):
        raise SourceFreezeError() from None
    expected = dict(contract.source_hashes)
    captured = []
    try:
        for name in SOURCE_FILES:
            path = root / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated" / name
            if path.is_symlink() or not path.is_file():
                raise SourceFreezeError()
            content = path.read_bytes().decode("utf-8").replace("\r\n", "\n").encode("utf-8")
            digest = hashlib.sha256(content).hexdigest()
            if digest != expected[name]:
                raise SourceFreezeError()
            captured.append((name, digest))
    except (OSError, UnicodeError, KeyError):
        raise SourceFreezeError() from None
    return SourceSnapshot(contract.source_digest, tuple(captured))


def verify_source_freeze(before: SourceSnapshot, after: SourceSnapshot,
                         contract: AcceptanceContract) -> bool:
    """Accept only matching complete snapshots bound to the contract digest."""
    return (type(before) is SourceSnapshot and type(after) is SourceSnapshot
            and type(contract) is AcceptanceContract and _contract_valid(contract)
            and before.source_digest == after.source_digest == contract.source_digest
            and before.hashes == after.hashes
            and tuple(name for name, _digest in before.hashes) == SOURCE_FILES
            and all(type(digest) is str and len(digest) == 64
                    for _name, digest in before.hashes))
