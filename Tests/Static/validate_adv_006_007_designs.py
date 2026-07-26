#!/usr/bin/env python3
"""Validate the design contracts for ADV-006 and ADV-007."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "Documentation/Project_Planning/advanced_vp3_vp5_design.json"
DOC_ADV006 = ROOT / "Documentation/Project_Planning/ADV_006_LAB_VP3_VP4_DESIGN.md"
DOC_ADV007 = ROOT / "Documentation/Project_Planning/ADV_007_LAB_VP5_DESIGN.md"
BACKLOG = ROOT / ".ai/BACKLOG.md"
STATUS = ROOT / "Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md"

EXPECTED_PHASES = [
    "PREFLIGHT", "SETUP", "BASELINE", "PROBLEM_OR_CONTRAST", "EVIDENCE",
    "MITIGATION_OR_COUNTERPROBE", "COMPARISON", "CLEANUP",
]
EXPECTED_VP3 = ["OPT-014", "OPT-013", "RES-004", "RES-003", "RES-007", "DGN-005"]
EXPECTED_VP3_STANDARD = ["OPT-014", "OPT-013", "RES-004", "RES-007", "DGN-005"]
EXPECTED_VP4 = ["QRY-008", "QRY-009", "OPT-014", "OPT-009", "OPT-006", "RES-002", "OPT-010"]
EXPECTED_VP5 = ["DGN-001", "DGN-003", "QRY-013", "DGN-007", "M07-TRANSFER"]
EXPECTED_FEATURES = {
    "INTERLEAVED_EXECUTION_MSTVF",
    "TABLE_VARIABLE_DEFERRED_COMPILATION",
    "SCALAR_UDF_INLINING",
    "BATCH_MODE_ON_ROWSTORE",
    "ROW_MODE_MEMORY_GRANT_FEEDBACK",
    "PERSISTED_PERCENTILE_MEMORY_GRANT_FEEDBACK",
    "PARAMETER_SENSITIVE_PLAN_OPTIMIZATION",
    "CARDINALITY_ESTIMATION_FEEDBACK",
    "DEGREE_OF_PARALLELISM_FEEDBACK",
    "OPTIONAL_PARAMETER_PLAN_OPTIMIZATION",
}
REQUIRED_DEMOS = {"OPT-014", "RES-004", "RES-003", "RES-007", "DGN-005", "DGN-007"}
VALID_RISKS = {"GREEN", "YELLOW", "RED"}


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    if data.get("status") != "DESIGNED":
        fail("manifest status must be DESIGNED")
    if data.get("work_packages") != ["ADV-006", "ADV-007"]:
        fail("unexpected work package order")
    if data.get("target_versions") != [2019, 2022, 2025]:
        fail("target version matrix must be 2019/2022/2025")
    if data.get("required_phases") != EXPECTED_PHASES:
        fail("demo phases are incomplete or out of order")

    labs = data["labs"]
    if labs["LAB-VP3"]["sequence"] != EXPECTED_VP3:
        fail("LAB-VP3 sequence changed")
    if labs["LAB-VP3"]["standard_sequence"] != EXPECTED_VP3_STANDARD:
        fail("LAB-VP3 standard sequence must exclude only RES-003")
    if labs["LAB-VP3"]["optional_red_step"] != "RES-003":
        fail("RES-003 must remain the explicit optional red step")
    if labs["LAB-VP4"]["sequence"] != EXPECTED_VP4:
        fail("LAB-VP4 sequence changed")
    if labs["LAB-VP5"]["sequence"] != EXPECTED_VP5:
        fail("LAB-VP5 sequence changed")

    expected_vp3_claims = {f"ADV-CLM-{i:03d}" for i in range(21, 28)} | {"ADV-CLM-037"}
    expected_vp4_claims = {"ADV-CLM-019", "ADV-CLM-020", "ADV-CLM-025"} | {
        f"ADV-CLM-{i:03d}" for i in range(28, 34)
    }
    expected_vp5_claims = {"ADV-CLM-013", "ADV-CLM-014", "ADV-CLM-015"} | {
        f"ADV-CLM-{i:03d}" for i in range(34, 40)
    }
    if set(labs["LAB-VP3"]["claims"]) != expected_vp3_claims:
        fail("LAB-VP3 claim coverage is incomplete")
    if set(labs["LAB-VP4"]["claims"]) != expected_vp4_claims:
        fail("LAB-VP4 claim coverage is incomplete")
    if set(labs["LAB-VP5"]["claims"]) != expected_vp5_claims:
        fail("LAB-VP5 claim coverage is incomplete")
    if labs["LAB-VP5"].get("minimum_false_hypotheses", 0) < 2:
        fail("LAB-VP5 must require at least two rejected hypotheses")

    features = data["feature_matrix"]
    if set(features) != EXPECTED_FEATURES:
        fail(f"feature matrix mismatch: {sorted(features)}")
    for feature_id, feature in features.items():
        if feature["minimum_engine"] not in {2019, 2022, 2025}:
            fail(f"{feature_id}: invalid minimum engine")
        if feature["minimum_compatibility_level"] not in {140, 150, 160, 170}:
            fail(f"{feature_id}: invalid compatibility level")
        if set(feature["versions"]) != {"2019", "2022", "2025"}:
            fail(f"{feature_id}: incomplete version outcomes")
        if not feature.get("demos") or not feature.get("query_store"):
            fail(f"{feature_id}: incomplete feature contract")

    if features["PARAMETER_SENSITIVE_PLAN_OPTIMIZATION"]["versions"]["2019"] != "SKIP_FEATURE_UNAVAILABLE":
        fail("PSP must be unavailable on SQL Server 2019")
    if features["OPTIONAL_PARAMETER_PLAN_OPTIMIZATION"]["versions"] != {
        "2019": "SKIP_FEATURE_UNAVAILABLE",
        "2022": "SKIP_FEATURE_UNAVAILABLE",
        "2025": "TEST",
    }:
        fail("OPPO version contract is incorrect")
    for feature_id in ("CARDINALITY_ESTIMATION_FEEDBACK", "DEGREE_OF_PARALLELISM_FEEDBACK"):
        if features[feature_id]["query_store"] != "READ_WRITE_REQUIRED":
            fail(f"{feature_id}: Query Store READ_WRITE is required")

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

    red = demos["RES-003"]
    if red["risk"] != "RED" or red["execution_path"] != "DEDICATED_RESOURCE_INSTANCE":
        fail("RES-003 must remain isolated and red")
    if not red.get("requires_high_impact_confirmation") or not red.get("external_kill_switch"):
        fail("RES-003 requires confirmation and external kill switch")
    if red.get("maximum_runtime_seconds", 9999) > 180:
        fail("RES-003 runtime budget exceeds 180 seconds")

    capstone = demos["DGN-007"]
    if capstone["risk"] != "YELLOW" or capstone["sessions"] > 3:
        fail("DGN-007 resource contract changed")
    if len(capstone.get("false_hypotheses", [])) < 2:
        fail("DGN-007 must contain at least two false hypotheses")
    if capstone.get("reference_change") != "QUERY_LOCAL_OPTION_RECOMPILE":
        fail("DGN-007 reference change must remain query-local and cross-version")
    if any(word in capstone["title"].lower() for word in ("sniff", "parameter", "recompile", "lösung")):
        fail("DGN-007 participant title reveals the solution")
    for required_evidence in {
        "query_store_plans", "runtime_intervals", "plan_xml", "compiled_parameter",
        "statistics_usage", "request_waits", "xe_categories", "rollback_confirmation",
    }:
        if required_evidence not in capstone["evidence"]:
            fail(f"DGN-007 missing evidence {required_evidence}")

    prohibited = set(data["prohibited_actions"])
    for required in {
        "GLOBAL_PLAN_CACHE_CLEAR",
        "INSTANCE_WIDE_MEMORY_CONFIGURATION_CHANGE",
        "UNBOUNDED_MEMORY_PRESSURE_ON_SHARED_INSTANCE",
        "REAL_APPLICATION_DATA",
        "RAW_PARAMETER_VALUE_LOGGING",
        "HIDDEN_SOLUTION_MARKERS",
        "UNDISCLOSED_PLAN_FORCING",
    }:
        if required not in prohibited:
            fail(f"missing prohibited action {required}")

    adv006 = DOC_ADV006.read_text(encoding="utf-8")
    adv007 = DOC_ADV007.read_text(encoding="utf-8")
    for marker in (
        "`ADV-006`", "`DESIGNED`", "LAB-VP3", "LAB-VP4", "RES-003",
        "SKIP_MEMORY_PRESSURE_NOT_PRODUCED", "SKIP_FEATURE_NOT_ELIGIBLE",
    ):
        if marker not in adv006:
            fail(f"ADV-006 document missing {marker}")
    for marker in (
        "`ADV-007`", "`DESIGNED`", "DGN-007", "T0_BASELINE", "T1_INCIDENT",
        "T2_COMPARISON", "SKIP_INCIDENT_NOT_REPRODUCED", "OPTION (RECOMPILE)",
    ):
        if marker not in adv007:
            fail(f"ADV-007 document missing {marker}")

    backlog = BACKLOG.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    for package in ("ADV-006", "ADV-007"):
        if f"[x] `{package}`" not in backlog:
            fail(f"backlog does not mark {package} complete")
        if package not in status:
            fail(f"current status does not mention {package}")

    print("ADV-006/007 design contracts: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ADV-006/007 design contracts: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
