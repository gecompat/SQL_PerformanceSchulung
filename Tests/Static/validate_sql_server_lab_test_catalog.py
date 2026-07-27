#!/usr/bin/env python3
"""Validate the SQL_Server_Lab integration catalog.

The validator is standard-library-only. It discovers every productive demo
manifest, requires an exact catalog mapping, and checks infrastructure and
safety invariants without starting SQL Server or a container runtime.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Tests" / "Lab" / "performance-lab-matrix.json"
SCHEMA_PATH = ROOT / "Tests" / "Lab" / "performance-lab-matrix.schema.json"
ARCHITECTURE_PATH = ROOT / "Documentation" / "Architecture" / "SQL_SERVER_LAB_TEST_AUTOMATION.md"
INFRASTRUCTURE_README = ROOT / "Infrastructure" / "README.md"
BACKLOG = ROOT / ".ai" / "BACKLOG.md"

DEMO_ID = re.compile(r"^(STL|OPT|QRY|IDX|CON|RES|DGN)-[0-9]{3}$")
CAPABILITY = re.compile(r"^[A-Z][A-Z0-9_]+$")
ALLOWED_PROVIDERS = {"docker", "podman"}
ALLOWED_VERSIONS = {"2019", "2022", "2025"}
ALLOWED_SAFETY = {"GREEN", "YELLOW", "RED"}
ALLOWED_PROFILES = {"compact", "standard", "performance"}
ALLOWED_ISOLATION = {"SHARED_PROVIDER_VERSION", "FRESH_INSTANCE", "DEDICATED_DISPOSABLE"}
ALLOWED_OUTCOMES = {"PASS", "WARN", "SKIP"}
REQUIRED_LANES = {"SMOKE", "CORE", "PROVIDER_PARITY", "FULL_CONTAINER_MATRIX", "RED_DISPOSABLE"}


class ContractError(RuntimeError):
    """Raised for a catalog contract violation."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"{path.relative_to(ROOT)}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"{path.relative_to(ROOT)}: JSON root must be an object")
    return payload


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def productive_manifests(exclude_prefixes: list[str]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for manifest_path in sorted((ROOT / "Demos").rglob("manifest.json")):
        rel = relative(manifest_path)
        if any(rel.startswith(prefix) for prefix in exclude_prefixes):
            continue
        manifest = read_json(manifest_path)
        demo_id = manifest.get("demo_id")
        if not isinstance(demo_id, str) or not DEMO_ID.fullmatch(demo_id):
            raise ContractError(f"{rel}: invalid or missing demo_id")
        if demo_id in found:
            raise ContractError(f"duplicate productive demo_id {demo_id}: {relative(found[demo_id])} and {rel}")
        found[demo_id] = manifest_path
    return found


def validate_lane(name: str, lane: Any) -> None:
    if not isinstance(lane, dict):
        raise ContractError(f"lane {name} must be an object")
    if lane.get("providerMode") not in {"FIRST_AVAILABLE", "SELECTED", "ALL"}:
        raise ContractError(f"lane {name}: invalid providerMode")
    versions = lane.get("versions")
    safety = lane.get("safetyLevels")
    repetitions = lane.get("repetitions")
    if not isinstance(versions, list) or not versions or set(versions) - ALLOWED_VERSIONS:
        raise ContractError(f"lane {name}: invalid versions")
    if len(versions) != len(set(versions)):
        raise ContractError(f"lane {name}: duplicate versions")
    if not isinstance(safety, list) or not safety or set(safety) - ALLOWED_SAFETY:
        raise ContractError(f"lane {name}: invalid safetyLevels")
    if len(safety) != len(set(safety)):
        raise ContractError(f"lane {name}: duplicate safetyLevels")
    if not isinstance(repetitions, int) or not 1 <= repetitions <= 5:
        raise ContractError(f"lane {name}: repetitions must be 1 through 5")

    if "YELLOW" in safety and lane.get("requiresYellowConfirmation") is not True:
        raise ContractError(f"lane {name}: YELLOW requires explicit confirmation")
    if "RED" in safety and lane.get("requiresRedConfirmation") is not True:
        raise ContractError(f"lane {name}: RED requires explicit confirmation")
    if name == "FULL_CONTAINER_MATRIX" and "RED" in safety:
        raise ContractError("FULL_CONTAINER_MATRIX must never include RED")
    if name == "RED_DISPOSABLE" and safety != ["RED"]:
        raise ContractError("RED_DISPOSABLE must contain RED only")


def validate_demo(entry: Any, manifests: dict[str, Path], global_providers: set[str], global_versions: set[str]) -> None:
    if not isinstance(entry, dict):
        raise ContractError("each demos entry must be an object")

    demo_id = entry.get("demoId")
    if not isinstance(demo_id, str) or not DEMO_ID.fullmatch(demo_id):
        raise ContractError(f"invalid demoId: {demo_id!r}")
    if demo_id not in manifests:
        raise ContractError(f"catalog contains unknown productive demo {demo_id}")

    manifest_value = entry.get("manifest")
    if not isinstance(manifest_value, str) or Path(manifest_value).is_absolute() or ".." in Path(manifest_value).parts:
        raise ContractError(f"{demo_id}: manifest path is invalid")
    expected_manifest = relative(manifests[demo_id])
    if manifest_value != expected_manifest:
        raise ContractError(f"{demo_id}: manifest path mismatch; expected {expected_manifest}")

    manifest = read_json(manifests[demo_id])
    if manifest.get("contract_version") != "1.0":
        raise ContractError(f"{demo_id}: demo manifest contract_version must be 1.0")
    if manifest.get("run_token") != "LOCAL":
        raise ContractError(f"{demo_id}: checked-in run_token must be LOCAL")
    if not isinstance(manifest.get("phases"), list) or not manifest["phases"]:
        raise ContractError(f"{demo_id}: phases missing")
    if not isinstance(manifest.get("cleanup"), dict):
        raise ContractError(f"{demo_id}: cleanup contract missing")

    safety = entry.get("safetyLevel")
    if safety not in ALLOWED_SAFETY or safety != manifest.get("safety_level"):
        raise ContractError(f"{demo_id}: catalog and manifest safety levels differ")
    status = entry.get("implementationStatus")
    if status not in {"IMPLEMENTED", "VALIDATED"}:
        raise ContractError(f"{demo_id}: invalid implementationStatus")

    sessions = entry.get("sessions")
    if not isinstance(sessions, int) or not 1 <= sessions <= 200:
        raise ContractError(f"{demo_id}: sessions must be 1 through 200")

    providers = entry.get("providers")
    versions = entry.get("versions")
    if not isinstance(providers, list) or not providers or set(providers) - global_providers:
        raise ContractError(f"{demo_id}: invalid providers")
    if len(providers) != len(set(providers)):
        raise ContractError(f"{demo_id}: duplicate providers")
    if not isinstance(versions, list) or not versions or set(versions) - global_versions:
        raise ContractError(f"{demo_id}: invalid versions")
    if len(versions) != len(set(versions)):
        raise ContractError(f"{demo_id}: duplicate versions")

    profile = entry.get("resourceProfile")
    isolation = entry.get("environmentIsolation")
    if profile not in ALLOWED_PROFILES:
        raise ContractError(f"{demo_id}: invalid resourceProfile")
    if isolation not in ALLOWED_ISOLATION:
        raise ContractError(f"{demo_id}: invalid environmentIsolation")
    if safety == "YELLOW" and isolation == "SHARED_PROVIDER_VERSION":
        raise ContractError(f"{demo_id}: YELLOW must not share a provider/version environment")
    if safety == "RED" and isolation != "DEDICATED_DISPOSABLE":
        raise ContractError(f"{demo_id}: RED requires DEDICATED_DISPOSABLE")

    capabilities = entry.get("requiredCapabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise ContractError(f"{demo_id}: requiredCapabilities missing")
    if len(capabilities) != len(set(capabilities)) or any(not isinstance(value, str) or not CAPABILITY.fullmatch(value) for value in capabilities):
        raise ContractError(f"{demo_id}: invalid or duplicate requiredCapabilities")
    if sessions > 1 and "MULTI_SESSION_SQLCMD" not in capabilities:
        raise ContractError(f"{demo_id}: multi-session demo lacks MULTI_SESSION_SQLCMD")

    outcomes = entry.get("expectedOutcomes")
    if not isinstance(outcomes, list) or not outcomes or set(outcomes) - ALLOWED_OUTCOMES:
        raise ContractError(f"{demo_id}: invalid expectedOutcomes")
    repetitions = entry.get("defaultRepetitions")
    if not isinstance(repetitions, int) or not 1 <= repetitions <= 5:
        raise ContractError(f"{demo_id}: defaultRepetitions must be 1 through 5")

    forbidden_keys = {"password", "secret", "hostname", "hostPath", "connectionString", "username"}
    if forbidden_keys.intersection(entry):
        raise ContractError(f"{demo_id}: catalog contains runtime or secret fields")


def main() -> int:
    try:
        catalog = read_json(CATALOG_PATH)
        schema = read_json(SCHEMA_PATH)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ContractError("catalog schema must use JSON Schema draft 2020-12")
        if catalog.get("contractVersion") != "1.0":
            raise ContractError("catalog contractVersion must be 1.0")
        if catalog.get("labRepository") != "gecompat/SQL_Server_Lab":
            raise ContractError("catalog must reference gecompat/SQL_Server_Lab")
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(catalog.get("minimumLabModuleVersion", ""))):
            raise ContractError("minimumLabModuleVersion is invalid")

        global_providers = set(catalog.get("providers", []))
        global_versions = set(catalog.get("targetVersions", []))
        if global_providers != ALLOWED_PROVIDERS:
            raise ContractError("provider matrix must contain docker and podman")
        if global_versions != ALLOWED_VERSIONS:
            raise ContractError("targetVersions must contain 2019, 2022 and 2025")

        discovery = catalog.get("discovery")
        if not isinstance(discovery, dict):
            raise ContractError("discovery contract missing")
        if discovery.get("include") != "Demos/**/manifest.json":
            raise ContractError("unexpected discovery include pattern")
        if discovery.get("missingCatalogEntry") != "FAIL" or discovery.get("unknownCatalogEntry") != "FAIL":
            raise ContractError("discovery mismatch policies must be FAIL")
        exclude_prefixes = discovery.get("excludePrefixes")
        if not isinstance(exclude_prefixes, list) or "Demos/00_Framework/" not in exclude_prefixes:
            raise ContractError("framework examples must be excluded")

        lanes = catalog.get("lanes")
        if not isinstance(lanes, dict) or set(lanes) != REQUIRED_LANES:
            raise ContractError(f"lane set mismatch: expected {sorted(REQUIRED_LANES)}")
        for name, lane in lanes.items():
            validate_lane(name, lane)

        manifests = productive_manifests(exclude_prefixes)
        entries = catalog.get("demos")
        if not isinstance(entries, list):
            raise ContractError("demos must be a list")
        catalog_ids = [entry.get("demoId") for entry in entries if isinstance(entry, dict)]
        if len(catalog_ids) != len(set(catalog_ids)):
            raise ContractError("duplicate demoId in catalog")
        if set(catalog_ids) != set(manifests):
            missing = sorted(set(manifests) - set(catalog_ids))
            unknown = sorted(set(catalog_ids) - set(manifests))
            raise ContractError(f"catalog discovery mismatch; missing={missing}; unknown={unknown}")
        for entry in entries:
            validate_demo(entry, manifests, global_providers, global_versions)

        architecture = ARCHITECTURE_PATH.read_text(encoding="utf-8")
        for marker in ("`LABINT-001`", "Project Adapter und Lab Package Engine", "Invoke-LabCleanup", "Providerneutraler Orphan-Cleanup", "AllowResourceDeficit"):
            if marker not in architecture:
                raise ContractError(f"architecture document missing marker {marker}")
        infrastructure = INFRASTRUCTURE_README.read_text(encoding="utf-8")
        if "SQL_SERVER_LAB_TEST_AUTOMATION.md" not in infrastructure:
            raise ContractError("Infrastructure/README.md does not link the automation architecture")
        backlog = BACKLOG.read_text(encoding="utf-8")
        if "`LABINT-001`" not in backlog or "`LABINT-002`" not in backlog:
            raise ContractError("backlog lacks LABINT work packages")

        full_lane = lanes["FULL_CONTAINER_MATRIX"]
        eligible = [entry for entry in entries if entry["safetyLevel"] in full_lane["safetyLevels"]]
        full_run_count = len(eligible) * len(global_providers) * len(full_lane["versions"]) * full_lane["repetitions"]
        if full_run_count != 72:
            raise ContractError(f"current full matrix must contain 72 runs, got {full_run_count}")

        print(
            "sql-server-lab-test-catalog: PASS "
            f"({len(entries)} demos, {len(global_providers)} providers, "
            f"{len(global_versions)} versions, full_runs={full_run_count})"
        )
        return 0
    except (ContractError, KeyError, TypeError) as exc:
        print(f"sql-server-lab-test-catalog: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
