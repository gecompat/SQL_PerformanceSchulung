#!/usr/bin/env python3
"""Repository consistency checks for performance-training scenarios."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "Documentation/Inventories/performance_scenario_inventory.json"
CATALOG_PATH = ROOT / "Documentation/Demo_Catalog/README.md"
SCENARIO_ROOT = ROOT / "Scenarios"
MODES = {"MANUAL", "RUNNER_ASSISTED", "AUTOMATED_VERIFY"}
REQUIRED_LIFECYCLE_FIELDS = {
    "sessionCount",
    "environmentIsolation",
    "requiredCapabilities",
    "hostMinimum",
    "forcedCondition",
    "verification",
    "resetStrategy",
}


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"Cannot read valid JSON from {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"Top-level JSON must be an object: {path.relative_to(ROOT)}")
    return value


def repo_path(value: str, owner: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise AssertionError(f"Unsafe path in {owner.relative_to(ROOT)}: {value}")
    resolved = ROOT / candidate
    if not resolved.exists():
        raise AssertionError(f"Missing referenced path in {owner.relative_to(ROOT)}: {value}")
    return resolved


def modes(primary: Any, supported: Any, owner: str) -> set[str]:
    if primary not in MODES:
        raise AssertionError(f"Invalid primary orchestration mode for {owner}: {primary}")
    if not isinstance(supported, list) or not supported:
        raise AssertionError(f"Missing supported orchestration modes for {owner}")
    result = set(supported)
    if result - MODES or primary not in result:
        raise AssertionError(f"Invalid orchestration mode combination for {owner}: {sorted(result)}")
    return result


def inventory() -> dict[str, dict[str, Any]]:
    document = load(INVENTORY_PATH)
    if document.get("contractVersion") != "1.1":
        raise AssertionError("Inventory contractVersion must be 1.1")
    if set(document.get("orchestrationModel", {})) != MODES:
        raise AssertionError("Inventory must define MANUAL, RUNNER_ASSISTED and AUTOMATED_VERIFY")

    result: dict[str, dict[str, Any]] = {}
    for item in document.get("scenarios", []):
        if not isinstance(item, dict):
            raise AssertionError("Inventory entries must be objects")
        demo_id = item.get("demoId")
        if not isinstance(demo_id, str) or demo_id in result:
            raise AssertionError(f"Invalid or duplicate inventory demoId: {demo_id}")
        if item.get("inventoryStatus") != "ASSESSED":
            raise AssertionError(f"Complete inventory requires ASSESSED status: {demo_id}")
        if item.get("implementationStatus") != "VALIDATED":
            raise AssertionError(f"Complete inventory requires VALIDATED implementation: {demo_id}")
        missing = sorted(field for field in REQUIRED_LIFECYCLE_FIELDS if field not in item)
        if missing:
            raise AssertionError(f"Missing lifecycle fields for {demo_id}: {', '.join(missing)}")
        modes(item.get("primaryOrchestrationMode"), item.get("supportedOrchestrationModes"), demo_id)
        if item.get("inventoryStatus") == "ASSESSED":
            demo_path = item.get("path")
            if not isinstance(demo_path, str):
                raise AssertionError(f"ASSESSED entry requires path: {demo_id}")
            repo_path(demo_path, INVENTORY_PATH)
            repo_path(f"{demo_path}/manifest.json", INVENTORY_PATH)
        result[demo_id] = item

    if document.get("status") != "ASSESSED_COMPLETE":
        raise AssertionError("Inventory status must be ASSESSED_COMPLETE")
    catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
    catalog_ids = set(re.findall(r"^\| `([A-Z]+-\d+)`", catalog_text, re.MULTILINE))
    if set(result) != catalog_ids:
        raise AssertionError(
            "Inventory/catalog mismatch: "
            f"missing={sorted(catalog_ids - set(result))}, extra={sorted(set(result) - catalog_ids)}"
        )
    validated = set(document.get("wave2Decisions", {}).get("validatedContainerSet", []))
    if validated != set(result):
        raise AssertionError("validatedContainerSet must contain every active catalog demo exactly once")
    return result


def referenced_paths(scenario: dict[str, Any]) -> list[str]:
    values: list[str] = []
    values += scenario.get("preparation", {}).get("scripts", [])
    values += scenario.get("reset", {}).get("scripts", [])
    values += scenario.get("remove", {}).get("cleanupScripts", [])
    for value in (
        scenario.get("runtimeManifest"),
        scenario.get("labManifest"),
        scenario.get("interactive", {}).get("entryDocument"),
        scenario.get("verification", {}).get("script"),
        scenario.get("orchestration", {}).get("runnerAssisted", {}).get("sessionManifest"),
        scenario.get("orchestration", {}).get("automatedVerify", {}).get("runtimeManifest"),
    ):
        if isinstance(value, str):
            values.append(value)
    for item in scenario.get("orchestration", {}).get("manual", {}).get("sessionScripts", []):
        if isinstance(item, dict) and isinstance(item.get("script"), str):
            values.append(item["script"])
    return values


def scenario(path: Path, items: dict[str, dict[str, Any]]) -> None:
    document = load(path)
    if document.get("contractVersion") != "1.1":
        raise AssertionError(f"Scenario contractVersion must be 1.1: {path.relative_to(ROOT)}")
    demo_id = document.get("demoId")
    if demo_id not in items:
        raise AssertionError(f"Scenario absent from inventory: {demo_id}")

    entry = items[demo_id]
    orchestration = document.get("orchestration", {})
    active = modes(orchestration.get("primaryMode"), orchestration.get("supportedModes"), str(demo_id))
    if orchestration.get("primaryMode") != entry.get("primaryOrchestrationMode"):
        raise AssertionError(f"Primary mode mismatch: {demo_id}")
    if active != set(entry.get("supportedOrchestrationModes", [])):
        raise AssertionError(f"Supported modes mismatch: {demo_id}")

    if orchestration.get("primaryMode") == "MANUAL":
        scripts = orchestration.get("manual", {}).get("sessionScripts", [])
        if not scripts or document.get("interactive", {}).get("readyState") != "READY_FOR_USER":
            raise AssertionError(f"MANUAL scenario needs session scripts and READY_FOR_USER: {demo_id}")
        orders = [item.get("startOrder") for item in scripts if isinstance(item, dict)]
        if len(orders) != len(set(orders)) or any(not isinstance(value, int) or value < 1 for value in orders):
            raise AssertionError(f"Invalid manual start order: {demo_id}")

    if "RUNNER_ASSISTED" in active:
        runner = orchestration.get("runnerAssisted", {})
        if runner.get("readyState") != "READY_FOR_OBSERVATION":
            raise AssertionError(f"RUNNER_ASSISTED needs READY_FOR_OBSERVATION: {demo_id}")

    if "AUTOMATED_VERIFY" in active:
        if not orchestration.get("automatedVerify", {}).get("runtimeManifest"):
            raise AssertionError(f"AUTOMATED_VERIFY needs runtimeManifest: {demo_id}")

    for value in referenced_paths(document):
        repo_path(value, path)


def main() -> int:
    try:
        items = inventory()
        files = sorted(SCENARIO_ROOT.glob("*/scenario.json"))
        if not files:
            raise AssertionError("No scenario definitions found")
        for path in files:
            scenario(path, items)
            print(f"PASS: {path.relative_to(ROOT)}")
        print(f"PASS: validated {len(items)} inventory entries and {len(files)} scenario definition(s)")
        return 0
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
