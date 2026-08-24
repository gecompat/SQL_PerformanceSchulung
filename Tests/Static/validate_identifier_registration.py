#!/usr/bin/env python3
"""Validate the project-owned identifier registration contract without external dependencies."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / ".ai" / "identity" / "registry.json"
ARTIFACTS_DIR = ROOT / ".ai" / "identity" / "artifacts"
POLICY_PATH = ROOT / ".ai" / "IDENTIFIER_REGISTRATION.md"

MINIMUM_NEXT_SEQUENCE = {
    "TSK": 1,
    "DEC": 62,
    "FWK": 13,
    "CUR": 13,
    "ADV": 12,
    "PRS": 14,
    "TST": 13,
    "LABSCN": 7,
    "LABINT": 5,
    "STL": 11,
    "OPT": 18,
    "QRY": 14,
    "IDX": 11,
    "CON": 10,
    "RES": 8,
    "DGN": 8,
    "INF": 7,
}


def fail(message: str) -> None:
    print(f"identifier-registration: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def main() -> None:
    registry = load_json(REGISTRY_PATH)
    if registry.get("schema_version") != 1:
        fail("unsupported registry schema version")
    if registry.get("profile") != "foundation-artifact-registry/v1":
        fail("unexpected registry profile")

    prefixes = registry.get("prefixes")
    if not isinstance(prefixes, dict) or set(prefixes) != set(MINIMUM_NEXT_SEQUENCE):
        fail("registry prefixes do not match the project nomenclature")
    if any(prefix.startswith("W") for prefix in prefixes):
        fail("waves must remain metadata, not newly allocatable prefixes")

    kinds = []
    for prefix, minimum in MINIMUM_NEXT_SEQUENCE.items():
        entry = prefixes[prefix]
        if not isinstance(entry, dict) or entry.get("next_sequence", 0) < minimum:
            fail(f"{prefix} counter is below the preserved published inventory")
        if entry.get("width") != 3 or not entry.get("kind"):
            fail(f"{prefix} has an incomplete allocation definition")
        kinds.append(entry["kind"])
    if len(kinds) != len(set(kinds)):
        fail("prefix kinds must be unique for deterministic allocation")

    allocations = registry.get("allocations")
    if not isinstance(allocations, dict) or len(allocations) != registry.get("registry_revision"):
        fail("registry revision and allocation count must match this append-only registry")
    if "DEC-061" not in allocations:
        fail("the adoption decision is not registered")

    record = load_json(ARTIFACTS_DIR / "DEC-061.json")
    if record.get("human_ref") != "DEC-061" or record.get("artifact_uid") != allocations["DEC-061"]:
        fail("DEC-061 record does not match the registry allocation")
    if record.get("registration_state") != "REGISTERED" or record.get("kind") != "decision":
        fail("DEC-061 record is not a registered decision")

    policy = POLICY_PATH.read_text(encoding="utf-8")
    for required_text in ("`TSK-###`", "`PRESERVE`", "als Metadatum"):
        if required_text not in policy:
            fail(f"policy is missing required rule: {required_text}")

    print(
        "identifier-registration: PASS "
        f"(prefixes={len(prefixes)}; allocations={len(allocations)}; "
        f"revision={registry['registry_revision']})"
    )


if __name__ == "__main__":
    main()
