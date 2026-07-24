#!/usr/bin/env python3
"""Static validation for the Wave-1 framework foundation.

The validator uses only the Python standard library. It reports paths and
aggregate findings, but never copies matched environment or secret values into
artifacts.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = ROOT / "Demos" / "00_Framework"

REQUIRED_FILES = {
    FRAMEWORK / "README.md",
    FRAMEWORK / "Contracts" / "FWK-001_Preflight_Contract.md",
    FRAMEWORK / "Contracts" / "FWK-002_TestDatabase_Lifecycle_Contract.md",
    FRAMEWORK / "Contracts" / "FWK-008_Safety_Abort_Contract.md",
    FRAMEWORK / "Contracts" / "FWK-012_Status_Error_Skip_Contract.md",
    FRAMEWORK / "Templates" / "README_TEMPLATE.md",
    FRAMEWORK / "Templates" / "00_Preflight.sql",
    FRAMEWORK / "Sql" / "FWK_TestDatabaseLifecycle.sql",
}

OUTCOMES = {"PASS", "WARN", "SKIP", "FAIL"}
STATUS_CODES = {
    "OK",
    "WARN_ENVIRONMENT_DETAIL_SUPPRESSED",
    "WARN_RESOURCE_PROBE_APPROXIMATE",
    "WARN_EMPIRICAL_VARIANCE",
    "SKIP_VERSION",
    "SKIP_COMPATIBILITY_LEVEL",
    "SKIP_EDITION",
    "SKIP_PLATFORM",
    "SKIP_PERMISSION",
    "SKIP_CONFIGURATION",
    "SKIP_RESOURCE_PROFILE",
    "SKIP_MANUAL_APPROVAL",
    "FAIL_CONTRACT",
    "FAIL_SAFETY",
    "FAIL_STATE",
    "FAIL_EXECUTION",
    "FAIL_CLEANUP",
}

README_SECTIONS = {
    "## 1. Lernziel",
    "## 2. Fachliche Kernaussage",
    "## 4. Voraussetzungen",
    "## 5. Sicherheits- und Abbruchrahmen",
    "## 6. Synthetisches Datenmodell",
    "## 7. Ablauf",
    "## 8. Erwartete Beobachtung",
    "## 10. Cleanup und Wiederherstellung",
    "## 11. Tests",
    "## 13. Quellen",
    "## 14. Traceability",
}

LIFECYCLE_MARKERS = {
    "SQLPERF.Project",
    "SQLPERF.ContractVersion",
    "SQLPERF.DemoId",
    "SQLPERF.RunToken",
    "SQLPERF.CreatedUtc",
}

FORBIDDEN_GLOBAL_PATTERNS = {
    r"\bTRUSTWORTHY\s+ON\b": "TRUSTWORTHY ON",
    r"\bDBCC\s+FREEPROCCACHE\b": "DBCC FREEPROCCACHE",
    r"\bDBCC\s+DROPCLEANBUFFERS\b": "DBCC DROPCLEANBUFFERS",
    r"\bxp_cmdshell\b": "xp_cmdshell",
    r"\bSHUTDOWN\b": "SHUTDOWN",
    r"\bALTER\s+SERVER\s+CONFIGURATION\b": "ALTER SERVER CONFIGURATION",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    findings: list[str] = []

    missing = sorted(path for path in REQUIRED_FILES if not path.is_file())
    findings.extend(f"missing required file: {relative(path)}" for path in missing)

    if missing:
        print(f"framework-contracts: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    preflight = read_text(FRAMEWORK / "Templates" / "00_Preflight.sql")
    lifecycle = read_text(FRAMEWORK / "Sql" / "FWK_TestDatabaseLifecycle.sql")
    status_contract = read_text(
        FRAMEWORK / "Contracts" / "FWK-012_Status_Error_Skip_Contract.md"
    )
    readme_template = read_text(FRAMEWORK / "Templates" / "README_TEMPLATE.md")

    for outcome in sorted(OUTCOMES):
        if outcome not in preflight or outcome not in status_contract:
            findings.append(f"outcome not consistently defined: {outcome}")

    for code in sorted(STATUS_CODES):
        if code not in status_contract:
            findings.append(f"status contract missing code: {code}")

    required_preflight_tokens = {
        "SERVERPROPERTY('ProductMajorVersion')",
        "sys.databases",
        "HAS_PERMS_BY_NAME",
        "@ConfirmIsolatedLab",
        "@HighImpactConfirmed",
        "@DisposableEnvironmentConfirmed",
        "@RecoveryPlanConfirmed",
        "WARN_ENVIRONMENT_DETAIL_SUPPRESSED",
        "CheckId, Outcome, Code",
        "'SUMMARY'",
        "THROW 51000",
    }
    for token in sorted(required_preflight_tokens):
        if token not in preflight:
            findings.append(f"preflight missing required token: {token}")

    for marker in sorted(LIFECYCLE_MARKERS):
        if marker not in lifecycle:
            findings.append(f"lifecycle missing ownership marker: {marker}")

    required_lifecycle_tokens = {
        "SQLPERF_LAB_",
        "@ConfirmLabUse",
        "@ConfirmDrop",
        "CREATE DATABASE",
        "SINGLE_USER WITH ROLLBACK IMMEDIATE",
        "DROP DATABASE",
        "sys.extended_properties",
        "@CreatedInThisBatch",
        "FAIL_CLEANUP",
    }
    for token in sorted(required_lifecycle_tokens):
        if token not in lifecycle:
            findings.append(f"lifecycle missing required token: {token}")

    # DROP must stay confined to the marker-protected lifecycle implementation.
    for sql_path in FRAMEWORK.rglob("*.sql"):
        text = read_text(sql_path)
        if "DROP DATABASE" in text and sql_path.name != "FWK_TestDatabaseLifecycle.sql":
            findings.append(f"DROP DATABASE outside lifecycle implementation: {relative(sql_path)}")

    for section in sorted(README_SECTIONS):
        if section not in readme_template:
            findings.append(f"README template missing section: {section}")

    for path in FRAMEWORK.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".sql", ".md", ".py", ".yml", ".yaml"}:
            continue
        text = read_text(path)
        for pattern, label in FORBIDDEN_GLOBAL_PATTERNS.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(f"forbidden high-risk pattern {label}: {relative(path)}")

    # Detect unresolved authoring placeholders in executable SQL only.
    for sql_path in FRAMEWORK.rglob("*.sql"):
        text = read_text(sql_path)
        if re.search(r"<[A-Z][A-Z0-9_| -]{2,}>", text):
            findings.append(f"unresolved placeholder in executable SQL: {relative(sql_path)}")

    if findings:
        print(f"framework-contracts: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(
        "framework-contracts: PASS "
        f"({len(REQUIRED_FILES)} required files, "
        f"{len(STATUS_CODES)} status codes, "
        f"{len(LIFECYCLE_MARKERS)} ownership markers)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
