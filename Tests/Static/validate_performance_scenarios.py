#!/usr/bin/env python3
"""Validate the performance-training scenario inventory and scenario definitions.

The validator intentionally uses only the Python standard library. JSON Schema files
remain the editor and contract reference; this script enforces repository-specific
cross-file invariants that JSON Schema cannot verify on its own.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "Documentation/Inventories/performance_scenario_inventory.json"
SCENARIO_ROOT = ROOT / "Scenarios"
VALID_PROVIDERS = {"docker", "podman", "hyperv", "mixed"}
VALID_VERSIONS = {"2019", "2022", "2025"}
VALID_CLASSES = {"A", "B", "C", "D"}
VALID_SAFETY = {"GREEN", "YELLOW", "RED"}
REQUIRED_SCENARIO_KEYS = {
    "contractVersion",
    "scenarioId",
    "demoId",
    "title",
    "status",
    "classification",
    "safetyLevel",
    "platforms",
    "sqlVersions",
    "topology",
    "preparation",
    "interactive",
    "verification",
    "reset",
    "remove",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise AssertionError(f"Missing required JSON file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Invalid JSON in {path.relative_to(ROOT)} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise AssertionError(f"Top-level JSON value must be an object: {path.relative_to(ROOT)}")
    return value


def require_repo_path(value: str, owner: Path) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise AssertionError(f"Unsafe repository path in {owner.relative_to(ROOT)}: {value}")
    resolved = ROOT / path
    if not resolved.exists():
        raise AssertionError(f"Referenced path does not exist in {owner.relative_to(ROOT)}: {value}")
    return resolved


def validate_inventory() -> dict[str, dict[str, Any]]:
    inventory = load_json(INVENTORY)
    if inventory.get("contractVersion") != "1.0":
        raise AssertionError("Inventory contractVersion must be 1.0")

    scenarios = inventory.get("scenarios")
    if not isinstance(scenarios, list):
        raise AssertionError("Inventory scenarios must be an array")

    by_demo: dict[str, dict[str, Any]] = {}
    for entry in scenarios:
        if not isinstance(entry, dict):
            raise AssertionError("Every inventory scenario must be an object")
        demo_id = entry.get("demoId")
        if not isinstance(demo_id, str) or not demo_id:
            raise AssertionError("Every inventory scenario needs a non-empty demoId")
        if demo_id in by_demo:
            raise AssertionError(f"Duplicate inventory demoId: {demo_id}")
        if entry.get("classification") not in VALID_CLASSES:
            raise AssertionError(f"Invalid classification for {demo_id}")
        if entry.get("safetyLevel") not in VALID_SAFETY:
            raise AssertionError(f"Invalid safetyLevel for {demo_id}")

        providers = set(entry.get("supportedProviders", []))
        versions = set(entry.get("sqlVersions", []))
        if not providers or not providers <= VALID_PROVIDERS:
            raise AssertionError(f"Invalid supportedProviders for {demo_id}: {sorted(providers)}")
        if not versions or not versions <= VALID_VERSIONS:
            raise AssertionError(f"Invalid sqlVersions for {demo_id}: {sorted(versions)}")

        path_value = entry.get("path")
        if entry.get("inventoryStatus") == "ASSESSED":
            if not isinstance(path_value, str) or not path_value:
                raise AssertionError(f"ASSESSED inventory entry requires a repository path: {demo_id}")
            require_repo_path(path_value, INVENTORY)
            manifest = ROOT / path_value / "manifest.json"
            if not manifest.exists():
                raise AssertionError(f"ASSESSED inventory entry has no manifest.json: {demo_id}")

        by_demo[demo_id] = entry

    return by_demo


def validate_scenario(path: Path, inventory: dict[str, dict[str, Any]]) -> None:
    scenario = load_json(path)
    missing = REQUIRED_SCENARIO_KEYS - scenario.keys()
    if missing:
        raise AssertionError(f"Missing scenario keys in {path.relative_to(ROOT)}: {sorted(missing)}")
    if scenario.get("contractVersion") != "1.0":
        raise AssertionError(f"Scenario contractVersion must be 1.0: {path.relative_to(ROOT)}")

    demo_id = scenario.get("demoId")
    scenario_id = scenario.get("scenarioId")
    if demo_id not in inventory:
        raise AssertionError(f"Scenario demoId is absent from inventory: {demo_id}")
    if not isinstance(scenario_id, str) or not scenario_id.startswith("PTS-"):
        raise AssertionError(f"Invalid scenarioId in {path.relative_to(ROOT)}")

    entry = inventory[demo_id]
    if scenario.get("classification") != entry.get("classification"):
        raise AssertionError(f"Classification mismatch between scenario and inventory: {demo_id}")
    if scenario.get("safetyLevel") != entry.get("safetyLevel"):
        raise AssertionError(f"Safety-level mismatch between scenario and inventory: {demo_id}")
    if set(scenario.get("platforms", [])) - set(entry.get("supportedProviders", [])):
        raise AssertionError(f"Scenario declares unsupported platform for {demo_id}")
    if set(scenario.get("sqlVersions", [])) - set(entry.get("sqlVersions", [])):
        raise AssertionError(f"Scenario declares unsupported SQL version for {demo_id}")

    for key in ("runtimeManifest", "labManifest"):
        value = scenario.get(key)
        if value is not None:
            if not isinstance(value, str):
                raise AssertionError(f"{key} must be a string in {path.relative_to(ROOT)}")
            require_repo_path(value, path)

    preparation = scenario.get("preparation", {})
    reset = scenario.get("reset", {})
    remove = scenario.get("remove", {})
    verification = scenario.get("verification", {})
    interactive = scenario.get("interactive", {})

    referenced_paths: list[str] = []
    referenced_paths.extend(preparation.get("scripts", []))
    referenced_paths.extend(reset.get("scripts", []))
    referenced_paths.extend(remove.get("cleanupScripts", []))
    for key in ("script",):
        value = verification.get(key)
        if isinstance(value, str):
            referenced_paths.append(value)
    for key in ("entryDocument", "sessionManifest"):
        value = interactive.get(key)
        if isinstance(value, str):
            referenced_paths.append(value)

    for value in referenced_paths:
        require_repo_path(value, path)

    topology = scenario.get("topology")
    if not isinstance(topology, dict) or not topology.get("instances"):
        raise AssertionError(f"Scenario topology needs at least one instance: {demo_id}")
    if topology.get("sessionModel") == "MULTI_SESSION" and len(topology.get("sessionRoles", [])) < 2:
        raise AssertionError(f"MULTI_SESSION scenario needs at least two session roles: {demo_id}")
    if interactive.get("readyState") != "READY_FOR_USER":
        raise AssertionError(f"Interactive scenario must hand over READY_FOR_USER: {demo_id}")


def main() -> int:
    errors: list[str] = []
    try:
        inventory = validate_inventory()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1

    scenario_files = sorted(SCENARIO_ROOT.glob("*/scenario.json")) if SCENARIO_ROOT.exists() else []
    if not scenario_files:
        print("FAIL: No Scenarios/*/scenario.json files found")
        return 1

    seen_scenario_ids: set[str] = set()
    for path in scenario_files:
        try:
            scenario = load_json(path)
            scenario_id = scenario.get("scenarioId")
            if scenario_id in seen_scenario_ids:
                raise AssertionError(f"Duplicate scenarioId: {scenario_id}")
            seen_scenario_ids.add(str(scenario_id))
            validate_scenario(path, inventory)
            print(f"PASS: {path.relative_to(ROOT)}")
        except AssertionError as exc:
            errors.append(str(exc))
            print(f"FAIL: {exc}")

    if errors:
        print(f"FAIL: {len(errors)} scenario validation error(s)")
        return 1

    print(f"PASS: validated {len(scenario_files)} scenario definition(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
