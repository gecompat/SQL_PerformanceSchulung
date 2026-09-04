#!/usr/bin/env python3
"""Validate the project-owned AI Repository Foundation integration contract."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VERSION = "1.8.0"
EXPECTED_SOURCE_REF = "7ddc29988b23570f462e46ebf527f8dfdd05fd75"
EXPECTED_CACHE_CAPABILITY_SHA256 = (
    "77ace825963862fd387ef37ac3b105abc95c652049fbf72855e205ab0455295b"
)
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
    registry = load_json(ROOT / ".ai" / "identity" / "registry.json")
    repo_map = (ROOT / ".ai" / "foundation" / "repo_map.yaml").read_text(
        encoding="utf-8"
    )
    ruleset = (
        ROOT / ".ai" / "foundation" / "FOUNDATION_RULESET.md"
    ).read_text(encoding="utf-8")
    project_rules = (ROOT / ".ai" / "PROJECT_RULES.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    decisions = (ROOT / ".ai" / "DECISIONS.md").read_text(encoding="utf-8")
    runtime_readme = (ROOT / "Runtime" / "README.md").read_text(encoding="utf-8")

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
    if row.get("decision_required") is not None:
        fail("rule-context-cache selection must not retain an unresolved decision")
    if row.get("selected_capabilities") != ["rule-context-cache"]:
        fail("upgrade assessment must select the rule-context-cache capability")
    capability = (
        ROOT
        / ".ai"
        / "foundation"
        / "rule_context_cache"
        / "rule_context_cache.py"
    )
    if not capability.is_file():
        fail("selected rule-context-cache capability payload is missing")
    capability_text = capability.read_text(encoding="utf-8")
    capability_sha256 = hashlib.sha256(
        capability_text.replace("\r\n", "\n").encode("utf-8")
    ).hexdigest()
    if capability_sha256 != EXPECTED_CACHE_CAPABILITY_SHA256:
        fail("rule-context-cache capability differs from the reviewed source payload")
    try:
        compile(capability_text, str(capability), "exec")
    except SyntaxError as exc:
        fail(f"rule-context-cache capability has invalid Python syntax: {exc}")
    for marker in (
        'CONTRACT = "foundation-rule-context-cache/v1"',
        'GENERATOR_VERSION = "1.0.0"',
        '"CACHE_HIT"',
        '"PARTIAL_INVALIDATION"',
        '"CACHE_MISS"',
    ):
        if marker not in capability_text:
            fail(f"rule-context-cache capability is missing {marker!r}")

    ignored_probe = "Runtime/.foundation-rule-cache/foundation-cache-probe.json"
    ignored = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", "--quiet", ignored_probe],
        check=False,
    )
    if ignored.returncode != 0:
        fail("configured rule-context cache record path is not ignored by Git")

    decision = registry.get("artifacts", {}).get("DEC-064")
    if not isinstance(decision, dict) or decision.get("kind") != "decision":
        fail("DEC-064 is not registered as a decision")
    if decision.get("registration_state") != "REGISTERED":
        fail("DEC-064 must be registered")
    if "| DEC-064 |" not in decisions:
        fail("DEC-064 is missing from .ai/DECISIONS.md")
    for marker in (
        "Runtime/.foundation-rule-cache/",
        "rule_context_cache.py record",
        "rule_context_cache.py check",
    ):
        if marker not in runtime_readme:
            fail(f"Runtime/README.md is missing {marker!r}")

    for text, source_name in (
        ("RULE_CONTEXT_CACHE_POLICY.md", "AGENTS.md"),
        ("Projektspezifische Steuerung", "AGENTS.md"),
        ("Foundation `1.8.0`", ".ai/PROJECT_RULES.md"),
        ("`DEC-064`", ".ai/PROJECT_RULES.md"),
        ("`Runtime/.foundation-rule-cache/`", ".ai/PROJECT_RULES.md"),
    ):
        content = agents if source_name == "AGENTS.md" else project_rules
        if text not in content:
            fail(f"{source_name} is missing {text!r}")

    print(
        "foundation-integration: PASS "
        "(1.8.0; complete 1-candidate delta; cache capability selected)"
    )


if __name__ == "__main__":
    main()
