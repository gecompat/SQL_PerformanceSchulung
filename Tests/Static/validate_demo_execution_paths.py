#!/usr/bin/env python3
"""Validate the execution path decision recorded for every implemented demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Documentation/Demo_Catalog/demo_execution_paths.json"
CATALOG_README = ROOT / "Documentation/Demo_Catalog/README.md"
LAB_MATRIX_PATH = ROOT / "Tests/Lab/performance-lab-matrix.json"
SCENARIO_INVENTORY_PATH = ROOT / "Documentation/Inventories/performance_scenario_inventory.json"
DEMO_ROOT = ROOT / "Demos"
FRAMEWORK_PREFIX = "Demos/00_Framework/"

STAGE_PATHS = {
    1: "TSQL_TESTDB",
    2: "TSQL_TESTDB",
    3: "CONTAINER",
    4: "HYPERV",
    5: "MULTI_INSTANCE",
}
ESCALATION_THRESHOLD = 2
SAFETY_LEVELS = {"GREEN", "YELLOW", "RED"}
DISPOSABLE_SAFETY_LEVELS = {"YELLOW", "RED"}
INSTANCE_REQUIREMENTS = {"SHARED_TEST_INSTANCE", "DISPOSABLE_INSTANCE"}
REQUIRED_FIELDS = (
    "demoId",
    "title",
    "path",
    "manifest",
    "implementationStatus",
    "safetyLevel",
    "sessions",
    "stage",
    "executionPath",
    "instanceRequirement",
    "rationale",
    "escalation",
)


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"Cannot read valid JSON from {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"Top-level JSON must be an object: {path.relative_to(ROOT)}")
    return value


def implemented_demos() -> dict[str, str]:
    result: dict[str, str] = {}
    for manifest in sorted(DEMO_ROOT.glob("**/manifest.json")):
        relative = manifest.relative_to(ROOT).as_posix()
        if relative.startswith(FRAMEWORK_PREFIX):
            continue
        document = load(manifest)
        demo_id = document.get("demo_id")
        if not isinstance(demo_id, str) or not demo_id:
            raise AssertionError(f"Manifest without demo_id: {relative}")
        if demo_id in result:
            raise AssertionError(f"Duplicate demo_id across manifests: {demo_id}")
        result[demo_id] = relative
    if not result:
        raise AssertionError("No productive demo manifests found")
    return result


def reference(path: Path, key: str) -> dict[str, dict[str, Any]]:
    document = load(path)
    entries = document.get(key)
    if not isinstance(entries, list) or not entries:
        raise AssertionError(f"Missing '{key}' list in {path.relative_to(ROOT)}")
    result: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict):
            raise AssertionError(f"Entries of '{key}' must be objects: {path.relative_to(ROOT)}")
        demo_id = item.get("demoId")
        if isinstance(demo_id, str):
            result[demo_id] = item
    return result


def escalation(entry: dict[str, Any], demo_id: str, findings: list[str]) -> None:
    stage = entry["stage"]
    value = entry.get("escalation")
    if stage <= ESCALATION_THRESHOLD:
        if value is not None:
            findings.append(f"{demo_id}: stage {stage} must not carry an escalation justification")
        return
    if not isinstance(value, dict):
        findings.append(f"{demo_id}: stage {stage} requires an escalation object")
        return
    rejected = value.get("rejectedStage")
    reason = value.get("reason")
    if not isinstance(rejected, int) or not 1 <= rejected < stage:
        findings.append(f"{demo_id}: escalation must name a rejected lower stage below {stage}")
    if not isinstance(reason, str) or len(reason.strip()) < 20:
        findings.append(f"{demo_id}: escalation requires a technical reason why the lower stage is insufficient")


def entry_checks(entry: dict[str, Any], findings: list[str]) -> None:
    demo_id = entry["demoId"]

    stage = entry["stage"]
    if not isinstance(stage, int) or stage not in STAGE_PATHS:
        findings.append(f"{demo_id}: stage must be one of {sorted(STAGE_PATHS)}")
        return

    if entry["executionPath"] != STAGE_PATHS[stage]:
        findings.append(
            f"{demo_id}: stage {stage} requires execution path {STAGE_PATHS[stage]}, found {entry['executionPath']}"
        )

    if entry["safetyLevel"] not in SAFETY_LEVELS:
        findings.append(f"{demo_id}: unknown safety level {entry['safetyLevel']}")

    if entry["instanceRequirement"] not in INSTANCE_REQUIREMENTS:
        findings.append(f"{demo_id}: unknown instance requirement {entry['instanceRequirement']}")
    elif entry["safetyLevel"] in DISPOSABLE_SAFETY_LEVELS and entry["instanceRequirement"] != "DISPOSABLE_INSTANCE":
        findings.append(f"{demo_id}: safety level {entry['safetyLevel']} requires a disposable instance")

    if not isinstance(entry["sessions"], int) or entry["sessions"] < 1:
        findings.append(f"{demo_id}: sessions must be a positive integer")

    if not isinstance(entry["rationale"], str) or len(entry["rationale"].strip()) < 20:
        findings.append(f"{demo_id}: rationale must explain why the stage is sufficient")

    escalation(entry, demo_id, findings)


def cross_check(entry: dict[str, Any], other: dict[str, Any], source: str, findings: list[str]) -> None:
    demo_id = entry["demoId"]
    # Das Szenarioinventar benennt die Sitzungszahl als sessionCount.
    aliases = {"sessions": ("sessions", "sessionCount")}
    for field in ("safetyLevel", "sessions", "implementationStatus"):
        expected = next((other[name] for name in aliases.get(field, (field,)) if name in other), None)
        if expected is not None and entry[field] != expected:
            findings.append(f"{demo_id}: {field} is {entry[field]} but {source} states {expected}")
    manifest = other.get("manifest")
    if isinstance(manifest, str) and manifest != entry["manifest"]:
        findings.append(f"{demo_id}: manifest path differs from {source}")


def catalog(findings: list[str]) -> list[dict[str, Any]]:
    document = load(CATALOG_PATH)
    if document.get("contractVersion") != "1.0":
        findings.append("catalogue contractVersion must be 1.0")
    if set(document.get("stageModel", {})) != {str(stage) for stage in STAGE_PATHS}:
        findings.append("catalogue stageModel must describe the stages 1 to 5")

    entries = document.get("demos")
    if not isinstance(entries, list) or not entries:
        findings.append("catalogue contains no demo entries")
        return []

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            findings.append("catalogue entries must be objects")
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in entry]
        if missing:
            findings.append(f"catalogue entry misses required fields: {', '.join(missing)}")
            continue
        demo_id = entry["demoId"]
        if demo_id in seen:
            findings.append(f"{demo_id}: duplicate catalogue entry")
            continue
        seen.add(demo_id)
        result.append(entry)
    return result


def main() -> int:
    findings: list[str] = []

    try:
        manifests = implemented_demos()
        entries = catalog(findings)
        lab = reference(LAB_MATRIX_PATH, "demos")
        scenarios = reference(SCENARIO_INVENTORY_PATH, "scenarios")
    except AssertionError as exc:
        print(f"demo-execution-paths: FAIL ({exc})")
        return 1

    if not CATALOG_README.exists():
        findings.append("Documentation/Demo_Catalog/README.md is missing")
    else:
        readme = CATALOG_README.read_text(encoding="utf-8")
        if "demo_execution_paths.json" not in readme:
            findings.append("catalogue README does not reference demo_execution_paths.json")

    for entry in entries:
        entry_checks(entry, findings)

        demo_id = entry["demoId"]
        manifest = manifests.get(demo_id)
        if manifest is None:
            findings.append(f"{demo_id}: catalogue entry without a productive demo manifest")
        elif manifest != entry["manifest"]:
            findings.append(f"{demo_id}: manifest path is {entry['manifest']} but the demo lives at {manifest}")

        if not (ROOT / entry["path"]).is_dir():
            findings.append(f"{demo_id}: demo path does not exist")

        if demo_id in lab:
            cross_check(entry, lab[demo_id], "the lab matrix", findings)
        if demo_id in scenarios:
            cross_check(entry, scenarios[demo_id], "the scenario inventory", findings)

    catalogued = {entry["demoId"] for entry in entries}
    for demo_id in sorted(set(manifests) - catalogued):
        findings.append(f"{demo_id}: implemented demo without an execution path entry")

    if findings:
        print(f"demo-execution-paths: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    escalated = sum(1 for entry in entries if entry["stage"] > ESCALATION_THRESHOLD)
    print(f"demo-execution-paths: PASS ({len(entries)} demos, {escalated} above stage {ESCALATION_THRESHOLD})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
