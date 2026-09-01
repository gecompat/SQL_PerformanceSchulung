#!/usr/bin/env python3
"""Validate the W2-002 dependency-neutralization contract."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
CLASSIFICATION = ROOT / "Documentation/Inventories/legacy_example_classification.json"
CONTRACT = ROOT / "Documentation/Inventories/w2_002_dependency_neutralization.json"
REVIEW = ROOT / "Documentation/Project_Planning/W2_002_DEPENDENCY_NEUTRALIZATION_REVIEW.md"

EXPECTED_SOURCE_IDS = {
    "SRC-LEGACY-008", "SRC-LEGACY-011", "SRC-LEGACY-012",
    "SRC-LEGACY-013", "SRC-LEGACY-014", "SRC-LEGACY-018",
    "SRC-LEGACY-020", "SRC-LEGACY-022", "SRC-LEGACY-028",
}
FORBIDDEN_RUNTIME_PATTERNS = {
    "public sample database": re.compile(
        r"(?i)adventureworks|wideworldimporters|northwind|stack(?:overflow|exchange)"
    ),
    "external row source": re.compile(r"(?i)\b(?:openrowset|openquery|bulk\s+insert)\b"),
    "linked server": re.compile(r"(?i)\bsp_addlinkedserver\b|\blinked\s+server\b"),
    "host command": re.compile(r"(?i)\bxp_cmdshell\b"),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    findings: list[str] = []
    classification = load_json(CLASSIFICATION)
    contract = load_json(CONTRACT)

    wave_entries = {
        entry["source_id"]: entry
        for entry in classification["entries"]
        if entry["migration_wave"] == "W2-A"
    }
    if set(wave_entries) != EXPECTED_SOURCE_IDS:
        findings.append("authoritative W2-A source set differs from the expected nine entries")

    if contract.get("work_package") != "W2-002" or contract.get("status") != "VALIDATED":
        findings.append("contract work package or status is invalid")
    guarantees = contract.get("guarantees", {})
    expected_guarantees = {
        "legacy_source_execution_allowed": False,
        "dataset_origin": "SYNTHETIC_REPOSITORY_OWNED",
        "external_data_sources_allowed": False,
        "neutral_identifiers_required": True,
        "database_name_pattern": "SQLPERF_LAB_<DEMOID>_<RUNTOKEN>",
    }
    for key, value in expected_guarantees.items():
        if guarantees.get(key) != value:
            findings.append(f"guarantee differs: {key}")

    entries = contract.get("entries", [])
    by_source = {entry.get("source_id"): entry for entry in entries}
    if len(entries) != len(by_source) or set(by_source) != EXPECTED_SOURCE_IDS:
        findings.append("contract must contain each W2-A source exactly once")

    active_demo_ids: set[str] = set()
    for source_id in sorted(EXPECTED_SOURCE_IDS & set(by_source)):
        source = wave_entries[source_id]
        entry = by_source[source_id]
        if source.get("source_execution_allowed") is not False:
            findings.append(f"{source_id}: legacy source execution is not forbidden")
        if entry.get("legacy_runtime") != "EXCLUDED":
            findings.append(f"{source_id}: legacy runtime must be EXCLUDED")
        if entry.get("disposition") not in {"ACTIVE_REPLACEMENT", "EXCLUDED_PENDING_REBUILD"}:
            findings.append(f"{source_id}: invalid disposition")
        if not entry.get("future_demo_ids") or not entry.get("future_data_contract"):
            findings.append(f"{source_id}: neutral future-data contract is incomplete")

        replacements = entry.get("active_replacements", [])
        if entry.get("disposition") == "ACTIVE_REPLACEMENT" and not replacements:
            findings.append(f"{source_id}: active replacement is missing")
        if entry.get("disposition") == "EXCLUDED_PENDING_REBUILD" and replacements:
            findings.append(f"{source_id}: pending rebuild unexpectedly names an active replacement")

        for replacement in replacements:
            demo_id = replacement.get("demo_id", "")
            relative = replacement.get("path", "")
            if demo_id in active_demo_ids:
                findings.append(f"active replacement is duplicated: {demo_id}")
            active_demo_ids.add(demo_id)
            path = ROOT / relative
            manifest_path = path / "manifest.json"
            if not path.is_dir() or not manifest_path.is_file():
                findings.append(f"{source_id}: active replacement path is incomplete: {relative}")
                continue
            manifest = load_json(manifest_path)
            if manifest.get("demo_id") != demo_id:
                findings.append(f"{source_id}: manifest demo_id mismatch for {relative}")
            sql_text = "\n".join(
                sql.read_text(encoding="utf-8", errors="replace")
                for sql in path.rglob("*.sql")
            )
            if "SQLPERF_LAB_" not in sql_text:
                findings.append(f"{source_id}: {demo_id} does not use a neutral SQLPERF_LAB_ database")
            for label, pattern in FORBIDDEN_RUNTIME_PATTERNS.items():
                if pattern.search(sql_text):
                    findings.append(f"{source_id}: {demo_id} contains forbidden {label}")

    review = REVIEW.read_text(encoding="utf-8")
    for required in ("| Status | `VALIDATED` |", "neun Kandidaten", "nicht ausführbare Quellen"):
        if required not in review:
            findings.append(f"review misses required fragment: {required}")

    if findings:
        print(f"w2-002-dependency-neutralization: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(
        "w2-002-dependency-neutralization: PASS "
        f"({len(entries)} legacy sources excluded; {len(active_demo_ids)} active neutral replacements)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
