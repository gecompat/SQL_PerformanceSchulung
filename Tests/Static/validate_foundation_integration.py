#!/usr/bin/env python3
"""Validate the project-owned AI Repository Foundation integration contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VERSION = "1.8.0"
EXPECTED_SOURCE_REF = "7ddc29988b23570f462e46ebf527f8dfdd05fd75"
VALID_CLASSIFICATIONS = {
    "NOT_APPLICABLE",
    "ALREADY_EQUIVALENT",
    "PROJECT_STRONGER",
    "APPLY_DEFAULT",
    "RECOMMENDED",
    "DECISION_REQUIRED",
    "CONFLICT",
}


def fail(message: str) -> None:
    print(f"foundation-integration: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def version_tuple(value: str) -> tuple[int, int, int]:
    try:
        parts = tuple(int(part) for part in value.split("."))
    except (AttributeError, ValueError):
        fail(f"invalid semantic version: {value!r}")
    if len(parts) != 3:
        fail(f"invalid semantic version: {value!r}")
    return parts


def main() -> None:
    catalog = load_json(ROOT / ".ai" / "foundation" / "feature_catalog.json")
    assessment = load_json(
        ROOT / ".ai" / "FOUNDATION_UPGRADE_1_8_0_ASSESSMENT.json"
    )
    repo_map = (ROOT / ".ai" / "foundation" / "repo_map.yaml").read_text(
        encoding="utf-8"
    )
    ruleset = (
        ROOT / ".ai" / "foundation" / "FOUNDATION_RULESET.md"
    ).read_text(encoding="utf-8")
    project_rules = (ROOT / ".ai" / "PROJECT_RULES.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    if catalog.get("ruleset_version") != EXPECTED_VERSION:
        fail("feature catalog does not carry Foundation 1.8.0")
    if f"foundation_ruleset_version: {EXPECTED_VERSION}" not in repo_map:
        fail("Foundation repo map version is stale")
    if f"Ruleset version: {EXPECTED_VERSION}" not in ruleset:
        fail("Foundation ruleset version is stale")
    for required_path in (
        ROOT / ".ai" / "foundation" / "RULE_CONTEXT_CACHE_POLICY.md",
        ROOT / ".ai" / "foundation" / "schemas" / "rule-context-cache.schema.json",
    ):
        if not required_path.is_file():
            fail(f"missing Foundation 1.8 core file {required_path.relative_to(ROOT)}")

    if assessment.get("schema_version") != 1:
        fail("upgrade assessment schema version must be 1")
    if assessment.get("installed_version") != "1.7.0":
        fail("upgrade assessment installed version must be 1.7.0")
    if assessment.get("source_version") != EXPECTED_VERSION:
        fail("upgrade assessment source version must be 1.8.0")
    if assessment.get("source_ref") != EXPECTED_SOURCE_REF:
        fail("upgrade assessment source ref does not match the reviewed commit")

    installed = version_tuple(assessment["installed_version"])
    source = version_tuple(assessment["source_version"])
    candidates: set[str] = set()
    for feature_id, feature in catalog.get("features", {}).items():
        introduced = version_tuple(feature["introduced_in"])
        material_change = any(
            change.get("impact") == "MATERIAL"
            and installed < version_tuple(change["version"]) <= source
            for change in feature.get("change_history", [])
        )
        if installed < introduced <= source or material_change:
            candidates.add(feature_id)

    rows = assessment.get("assessments")
    if not isinstance(rows, list) or len(rows) != len(candidates):
        fail("upgrade assessment does not contain exactly the complete feature delta")
    assessed_ids = {row.get("feature_id") for row in rows}
    if assessed_ids != candidates or candidates != {"rule-context-cache"}:
        fail(f"unexpected upgrade candidates: {sorted(candidates)}")

    row = rows[0]
    if row.get("classification") not in VALID_CLASSIFICATIONS:
        fail("upgrade assessment uses an invalid classification")
    if row.get("classification") != "RECOMMENDED":
        fail("rule-context-cache must remain an explicit recommendation")
    if row.get("candidate_reasons") != ["introduced_in:1.8.0"]:
        fail("rule-context-cache candidate reason is incomplete")
    if not row.get("evidence") or not row.get("rationale") or not row.get("recommendation"):
        fail("rule-context-cache assessment lacks evidence, rationale or recommendation")
    if row.get("decision_required") is not None or row.get("selected_capabilities") != []:
        fail("optional rule-context-cache capability must remain unselected")
    if (ROOT / ".ai" / "foundation" / "rule_context_cache").exists():
        fail("unselected rule-context-cache capability payload is present")

    for text, source_name in (
        ("RULE_CONTEXT_CACHE_POLICY.md", "AGENTS.md"),
        ("Projektspezifische Steuerung", "AGENTS.md"),
        ("Foundation `1.8.0`", ".ai/PROJECT_RULES.md"),
        ("optionale Capability `rule-context-cache` ist nicht ausgewählt", ".ai/PROJECT_RULES.md"),
    ):
        content = agents if source_name == "AGENTS.md" else project_rules
        if text not in content:
            fail(f"{source_name} is missing {text!r}")

    print(
        "foundation-integration: PASS "
        "(1.8.0; complete 1-candidate delta; cache capability unselected)"
    )


if __name__ == "__main__":
    main()
