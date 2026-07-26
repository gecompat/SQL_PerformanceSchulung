#!/usr/bin/env python3
"""Validate the design contracts for ADV-004 and ADV-005."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "Documentation/Project_Planning/advanced_vp1_vp2_design.json"
DOC_VP1 = ROOT / "Documentation/Project_Planning/ADV_004_LAB_VP1_DESIGN.md"
DOC_VP2 = ROOT / "Documentation/Project_Planning/ADV_005_LAB_VP2_DESIGN.md"
BACKLOG = ROOT / ".ai/BACKLOG.md"

EXPECTED_PHASES = [
    "PREFLIGHT", "SETUP", "BASELINE", "PROBLEM_OR_CONTRAST", "EVIDENCE",
    "MITIGATION_OR_COUNTERPROBE", "COMPARISON", "CLEANUP",
]
EXPECTED_VP1 = ["OPT-001", "OPT-015", "OPT-012", "OPT-016", "OPT-011", "QRY-006", "OPT-013", "OPT-017"]
EXPECTED_VP2 = ["OPT-007", "OPT-008", "QRY-013", "QRY-004", "OPT-009", "OPT-010"]
REQUIRED_DEMOS = {"OPT-015", "OPT-016", "OPT-017", "QRY-013", "QRY-004"}
VALID_RISKS = {"GREEN", "YELLOW", "RED"}


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    if data.get("status") != "DESIGNED":
        fail("manifest status must be DESIGNED")
    if data.get("work_packages") != ["ADV-004", "ADV-005"]:
        fail("unexpected work package order")
    if data.get("required_phases") != EXPECTED_PHASES:
        fail("demo phases are incomplete or out of order")
    if data.get("target_versions") != [2019, 2022, 2025]:
        fail("target version matrix must be 2019/2022/2025")

    labs = data["labs"]
    if labs["LAB-VP1"]["sequence"] != EXPECTED_VP1:
        fail("LAB-VP1 sequence changed")
    if labs["LAB-VP2"]["sequence"] != EXPECTED_VP2:
        fail("LAB-VP2 sequence changed")
    if set(labs["LAB-VP1"]["claims"]) != {f"ADV-CLM-{i:03d}" for i in range(1, 13)}:
        fail("LAB-VP1 claim coverage must be ADV-CLM-001..012")
    if set(labs["LAB-VP2"]["claims"]) != {f"ADV-CLM-{i:03d}" for i in range(13, 21)}:
        fail("LAB-VP2 claim coverage must be ADV-CLM-013..020")

    demos = data["demos"]
    if set(demos) != REQUIRED_DEMOS:
        fail(f"demo set mismatch: {sorted(demos)}")
    for demo_id, demo in demos.items():
        if demo["risk"] not in VALID_RISKS:
            fail(f"{demo_id}: invalid risk")
        if demo["versions"] != [2019, 2022, 2025]:
            fail(f"{demo_id}: incomplete version list")
        if demo["minimum_cpu"] < 2 or demo["minimum_memory_gb"] < 4:
            fail(f"{demo_id}: invalid minimum resource contract")
        for field in ("claims", "sources", "evidence", "skip_codes"):
            if not demo.get(field):
                fail(f"{demo_id}: missing {field}")
        if not all(value.startswith("ADV-CLM-") for value in demo["claims"]):
            fail(f"{demo_id}: invalid claim id")
        if not all(value.startswith("SRC-") for value in demo["sources"]):
            fail(f"{demo_id}: invalid source id")
        if not all(value.startswith("SKIP_") for value in demo["skip_codes"]):
            fail(f"{demo_id}: invalid skip code")

    if demos["OPT-017"]["risk"] != "YELLOW" or demos["OPT-017"]["minimum_cpu"] < 4:
        fail("OPT-017 must remain a yellow parallel resource profile")
    if demos["QRY-013"]["sessions"] != 2:
        fail("QRY-013 must define two client-context sessions")
    required_strategies = {"CATCH_ALL", "OPTION_RECOMPILE", "PARAMETERIZED_DYNAMIC_SQL", "PSP_EQUALITY", "OPPO_OPTIONAL_PREDICATE"}
    if set(demos["QRY-004"]["strategies"]) != required_strategies:
        fail("QRY-004 strategy set is incomplete")

    prohibited = set(data["prohibited_actions"])
    for required in {
        "GLOBAL_PLAN_CACHE_CLEAR",
        "INSTANCE_WIDE_CONFIGURATION_CHANGE",
        "REAL_APPLICATION_DATA",
        "UNPARAMETERIZED_VALUE_CONCATENATION",
    }:
        if required not in prohibited:
            fail(f"missing prohibited action {required}")

    vp1 = DOC_VP1.read_text(encoding="utf-8")
    vp2 = DOC_VP2.read_text(encoding="utf-8")
    for marker in ("`ADV-004`", "`DESIGNED`", "OPT-015", "OPT-016", "OPT-017", "SKIP_PLAN_SHAPE_NOT_PRODUCED"):
        if marker not in vp1:
            fail(f"ADV-004 document missing {marker}")
    for marker in ("`ADV-005`", "`DESIGNED`", "QRY-013", "QRY-004", "sp_executesql", "SKIP_FEATURE_UNAVAILABLE", "SKIP_FEATURE_NOT_ELIGIBLE"):
        if marker not in vp2:
            fail(f"ADV-005 document missing {marker}")

    backlog = BACKLOG.read_text(encoding="utf-8")
    for package in ("ADV-004", "ADV-005"):
        if f"[x] `{package}`" not in backlog:
            fail(f"backlog does not mark {package} complete")

    print("ADV-004/005 design contracts: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError) as exc:
        print(f"ADV-004/005 design contracts: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
