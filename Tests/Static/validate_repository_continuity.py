#!/usr/bin/env python3
"""Validate the project-owned repository-continuity contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def fail(message: str) -> None:
    print(f"repository-continuity: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_text(path: Path, values: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for value in values:
        if value not in text:
            fail(f"{path.relative_to(ROOT)} is missing {value!r}")


def main() -> None:
    assessment = json.loads(
        (ROOT / ".ai" / "FOUNDATION_UPGRADE_1_7_0_ASSESSMENT.json").read_text(
            encoding="utf-8"
        )
    )
    continuity = next(
        (
            row
            for row in assessment["assessments"]
            if row["feature_id"] == "repository-continuity-break-glass"
        ),
        None,
    )
    if continuity is None or continuity.get("classification") != "APPLY_DEFAULT":
        fail("upgrade assessment must select the continuity feature")

    require_text(
        ROOT / ".ai" / "REPOSITORY_CONTINUITY.md",
        (
            "DEC-063",
            "Repository Core Safety",
            "Repository CI Gates",
            "INFRASTRUCTURE_UNAVAILABLE",
            "VALIDATION_FAILURE",
            "UNKNOWN",
            "pull_request",
            "gecompat",
            "PENDING",
            "21754402",
            "21754415",
            "15368",
        ),
    )
    require_text(
        ROOT / ".github" / "pull_request_template.md",
        (
            "Actions-Ausfall / Break-glass",
            "INFRASTRUCTURE_UNAVAILABLE",
            "Restrisiko",
            "Nachprüfung",
        ),
    )
    require_text(
        ROOT / ".github" / "workflows" / "repository-governance.yml",
        (
            "pull_request:",
            "repository-governance:",
            "validate_identifier_registration.py",
            "validate_repository_continuity.py",
            "registry_semantic.py",
        ),
    )
    require_text(ROOT / ".ai" / "README.md", ("REPOSITORY_CONTINUITY.md",))
    require_text(ROOT / ".ai" / "DECISIONS.md", ("| DEC-063 |",))
    require_text(ROOT / ".ai" / "DECISIONS.md", ("| DEC-067 |",))
    require_text(ROOT / ".ai" / "REPOSITORY_CONTINUITY.md", (
        "DEC-067", "cancel-in-progress: false", "aktuellen PR-Head",
        "Abgebrochene, ersetzte oder nie gestartete Runs",
    ))
    checked = 0
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "docker run" not in text:
            continue
        checked += 1
        if unsafe_runtime_cancellation(text):
            fail(f"{path.name}: automatic SQL-runtime cancellation lacks a hard-interruption recovery contract")
    if checked == 0:
        fail("no SQL-container runtime workflows were discovered")
    print(f"repository-continuity: PASS ({checked} SQL-runtime workflows retain in-progress runs)")


def unsafe_runtime_cancellation(text: str) -> bool:
    """Reject true or dynamic cancellation at workflow or job scope."""
    values = re.findall(r"^\s*cancel-in-progress:\s*([^\n#]+)", text, re.MULTILINE)
    return any(value.strip().lower() != "false" for value in values)


if __name__ == "__main__":
    main()
