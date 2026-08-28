#!/usr/bin/env python3
"""Validate the project-owned central identifier registry without external dependencies."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / ".ai" / "identity" / "registry.json"
LEGACY_ARTIFACTS_DIR = ROOT / ".ai" / "identity" / "artifacts"
POLICY_PATH = ROOT / ".ai" / "IDENTIFIER_REGISTRATION.md"
SEMANTIC_TOOL = (
    ROOT
    / ".ai"
    / "foundation"
    / "artifact_registry_github"
    / "registry_semantic.py"
)
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "artifact-registry-integrity.yml"

PRESERVED_MAX_SEQUENCE = {
    "TSK": 0,
    "DEC": 62,
    "FWK": 12,
    "CUR": 12,
    "ADV": 11,
    "PRS": 13,
    "TST": 12,
    "LABSCN": 6,
    "LABINT": 4,
    "STL": 10,
    "OPT": 17,
    "QRY": 13,
    "IDX": 10,
    "CON": 9,
    "RES": 7,
    "DGN": 7,
    "INF": 6,
}

PRESERVED_UIDS = {
    "DEC-061": "urn:uuid:01a03379-e43c-7fbc-8b44-fb156fb2c205",
    "DEC-062": "urn:uuid:01a0499c-af28-7779-bb1c-1b70e49597a3",
}


def fail(message: str) -> None:
    print(f"identifier-registration: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def validate_uid(ref: str, value: object) -> str:
    if not isinstance(value, str) or not value.startswith("urn:uuid:"):
        fail(f"{ref} has no valid artifact UID")
    try:
        parsed = uuid.UUID(value.removeprefix("urn:uuid:"))
    except ValueError as exc:
        fail(f"{ref} has no valid artifact UID: {exc}")
    if parsed.version not in {4, 7}:
        fail(f"{ref} uses unsupported UUID version {parsed.version}")
    return f"urn:uuid:{parsed}"


def main() -> None:
    registry = load_json(REGISTRY_PATH)
    if registry.get("schema_version") != 2:
        fail("registry must use schema version 2")
    if registry.get("profile") != "foundation-artifact-registry/v2":
        fail("registry must use the selected v2 profile")
    for forbidden in ("registry_revision", "allocations"):
        if forbidden in registry:
            fail(f"v1 field {forbidden} must not remain in the v2 registry")

    prefixes = registry.get("prefixes")
    if not isinstance(prefixes, dict) or set(prefixes) != set(PRESERVED_MAX_SEQUENCE):
        fail("registry prefixes do not match the project nomenclature")
    if any(prefix.startswith("W") for prefix in prefixes):
        fail("waves must remain metadata, not newly allocatable prefixes")

    kinds: list[str] = []
    expected_refs: set[str] = set()
    for prefix, maximum in PRESERVED_MAX_SEQUENCE.items():
        entry = prefixes[prefix]
        if not isinstance(entry, dict) or set(entry) != {"kind", "width"}:
            fail(f"{prefix} must contain exactly kind and width")
        if entry.get("width") != 3 or not isinstance(entry.get("kind"), str):
            fail(f"{prefix} has an incomplete v2 prefix definition")
        kinds.append(entry["kind"])
        expected_refs.update(f"{prefix}-{sequence:03d}" for sequence in range(1, maximum + 1))
    if len(kinds) != len(set(kinds)):
        fail("prefix kinds must be unique for deterministic allocation")

    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != expected_refs:
        missing = sorted(expected_refs - set(artifacts or {}))
        extra = sorted(set(artifacts or {}) - expected_refs)
        fail(f"historical inventory mismatch; missing={missing}; extra={extra}")

    seen_uids: set[str] = set()
    for ref, record in artifacts.items():
        prefix = ref.split("-", 1)[0]
        if not isinstance(record, dict):
            fail(f"{ref} record must be an object")
        if "human_ref" in record:
            fail(f"{ref} redundantly stores human_ref")
        if record.get("kind") != prefixes[prefix]["kind"]:
            fail(f"{ref} kind does not match its prefix")
        if record.get("registration_state") != "REGISTERED":
            fail(f"{ref} is not registered")
        if not isinstance(record.get("title"), str) or not record["title"].strip():
            fail(f"{ref} has no title")
        for list_field in ("aliases", "relations"):
            if not isinstance(record.get(list_field), list):
                fail(f"{ref} field {list_field} must be a list")
        uid = validate_uid(ref, record.get("artifact_uid"))
        if uid in seen_uids:
            fail(f"artifact UID is duplicated: {uid}")
        seen_uids.add(uid)

    for ref, uid in PRESERVED_UIDS.items():
        if artifacts[ref]["artifact_uid"] != uid:
            fail(f"{ref} did not preserve its v1 artifact UID")

    if LEGACY_ARTIFACTS_DIR.exists() and any(LEGACY_ARTIFACTS_DIR.glob("*.json")):
        fail("split v1 artifact records must not remain active")
    if not SEMANTIC_TOOL.is_file():
        fail("selected v2 semantic tool is missing")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "vars.ARTIFACT_REGISTRY_PATH" not in workflow:
        fail("GitHub registry workflow does not support the configured project registry path")

    policy = POLICY_PATH.read_text(encoding="utf-8")
    for required_text in (
        "`TSK-###`",
        "`PRESERVE`",
        "als Metadatum",
        "foundation-artifact-registry/v2",
        "Drei-Wege-Merge",
    ):
        if required_text not in policy:
            fail(f"policy is missing required rule: {required_text}")

    print(
        "identifier-registration: PASS "
        f"(profile=v2; prefixes={len(prefixes)}; artifacts={len(artifacts)})"
    )


if __name__ == "__main__":
    main()
