#!/usr/bin/env python3
"""Validate source, decision and claim anchors for W-SQL25-001."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "Documentation" / "Project_Planning" / "SQL_SERVER_2025_DELTA_REVIEW.md"
SOURCES = ROOT / "Documentation" / "Research" / "SOURCE_REGISTER.md"
CLAIMS = ROOT / "Documentation" / "Research" / "ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md"
DGN005 = ROOT / "Demos" / "07_Query_Store_Extended_Events" / "DGN-005_Bounded_Extended_Events" / "10_Setup.sql"


def main() -> int:
    findings: list[str] = []
    for path in (REVIEW, SOURCES, CLAIMS, DGN005):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    if findings:
        print("sql25-delta: FAIL")
        return 1
    review = REVIEW.read_text(encoding="utf-8")
    sources = SOURCES.read_text(encoding="utf-8")
    claims = CLAIMS.read_text(encoding="utf-8")
    dgn005 = DGN005.read_text(encoding="utf-8")
    for source_id in (f"SRC-{number:03d}" for number in range(58, 66)):
        if f"| `{source_id}` | PRIMARY |" not in sources:
            findings.append(f"source missing: {source_id}")
        if source_id not in review:
            findings.append(f"review source link missing: {source_id}")
    expected = {
        "CE Feedback für Ausdrücke": "ADOPT",
        "Optimiertes `sp_executesql`": "DEFER",
        "Zeitgebundene XE-Sessions": "ADOPT",
        "TempDB Space Resource Governance": "DEFER",
        "Ordered nonclustered Columnstore": "DEFER",
        "Query Store auf lesbaren Secondary Replicas": "DEFER",
        "Vector- und KI-Funktionen": "OUT_OF_SCOPE",
    }
    for feature, decision in expected.items():
        pattern = rf"\| {re.escape(feature)} \|.*\| `{decision}` \|"
        if not re.search(pattern, review):
            findings.append(f"decision mismatch: {feature} -> {decision}")
    for marker in ("ADV-CLM-033", "SRC-061", "ADV-CLM-036", "SRC-060", "MAX_DURATION"):
        if marker not in claims:
            findings.append(f"claim marker missing: {marker}")
    for marker in ("@Major>=17", "MAX_DURATION=300 SECONDS", "STARTUP_STATE=OFF"):
        if marker not in dgn005:
            findings.append(f"DGN-005 version guard missing: {marker}")
    if findings:
        print(f"sql25-delta: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("sql25-delta: PASS (2 ADOPT; 4 DEFER; 1 OUT_OF_SCOPE; 8 primary sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
