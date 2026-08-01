#!/usr/bin/env python3
"""Validate ADV-003 curriculum and traceability integration."""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CURRICULUM = ROOT / "Documentation" / "Curriculum" / "CURRICULUM_ARCHITECTURE.md"
TRACEABILITY = ROOT / "Documentation" / "Curriculum" / "TRACEABILITY_MATRIX.md"
CLAIM_MATRIX = ROOT / "Documentation" / "Research" / "ADVANCED_PERFORMANCE_CLAIM_SOURCE_MATRIX.md"

EXPECTED_NEW_LOS = {
    "LO-M02-08",
    "LO-M02-09",
    "LO-M02-10",
    "LO-M02-11",
    "LO-M03-07",
    "LO-M03-08",
    "LO-M06-07",
    "LO-M06-08",
    "LO-M07-04",
}

CLAIM_TO_LO = {
    **{f"ADV-CLM-{number:03d}": "LO-M02-08" for number in range(1, 5)},
    **{f"ADV-CLM-{number:03d}": "LO-M02-09" for number in range(5, 9)},
    **{f"ADV-CLM-{number:03d}": "LO-M02-10" for number in range(9, 13)},
    **{f"ADV-CLM-{number:03d}": "LO-M03-07" for number in range(13, 17)},
    **{f"ADV-CLM-{number:03d}": "LO-M03-08" for number in range(17, 21)},
    **{f"ADV-CLM-{number:03d}": "LO-M06-07" for number in range(21, 28)},
    **{f"ADV-CLM-{number:03d}": "LO-M02-11" for number in range(28, 34)},
    **{f"ADV-CLM-{number:03d}": "LO-M06-08" for number in range(34, 38)},
    **{f"ADV-CLM-{number:03d}": "LO-M07-04" for number in range(38, 40)},
}

# Durch ADV-009, ADV-010 und ADV-011 in das aktive Deck uebernommene
# Vertiefungsclaims
# mit ihren Anzeigepositionen. Alle uebrigen ADV-Claims bleiben ohne aktive
# Folie.
INTEGRATED_CLAIMS = {
    "ADV-CLM-013": "85, 88",
    "ADV-CLM-014": "84, 88",
    "ADV-CLM-015": "86, 88",
    "ADV-CLM-016": "87, 88",
    "ADV-CLM-017": "90, 93",
    "ADV-CLM-018": "91, 92, 93",
    "ADV-CLM-019": "95, 96, 97",
    "ADV-CLM-020": "99, 100, 101",
}


def read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    findings: list[str] = []
    try:
        curriculum = read(CURRICULUM)
        traceability = read(TRACEABILITY)
        claim_matrix = read(CLAIM_MATRIX)
    except (OSError, UnicodeError) as exc:
        print(f"adv-003-curriculum: FAIL (read error: {exc})")
        return 1

    for fragment in (
        "| Arbeitspakete | `CUR-001`, `CUR-002`, `CUR-003`, `CUR-004`, `CUR-009`, `CUR-010`, `ADV-003` |",
        "| Beobachtbare Lernziele | 52 |",
        "| Geplante Vertiefungsclaims | 39 |",
        "| Davon aktiv im Deck | 8 |",
        "| Vertiefungsfolien im Deck | 18 |",
        "`ADV-003` ergänzt neun beobachtbare Vertiefungslernziele",
    ):
        if fragment not in curriculum:
            findings.append(f"curriculum missing contract fragment: {fragment}")

    found_new_los = set(re.findall(r"`(LO-M(?:02|03|06|07)-\d{2})`", curriculum)) & EXPECTED_NEW_LOS
    if found_new_los != EXPECTED_NEW_LOS:
        missing = sorted(EXPECTED_NEW_LOS - found_new_los)
        extra = sorted(found_new_los - EXPECTED_NEW_LOS)
        findings.append(f"new learning-objective set mismatch; missing={missing}; extra={extra}")
    for learning_objective in EXPECTED_NEW_LOS:
        if curriculum.count(f"`{learning_objective}`") != 1:
            findings.append(f"{learning_objective} must occur exactly once in curriculum")

    source_claims = set(re.findall(r"`(ADV-CLM-\d{3})`", claim_matrix))
    expected_claims = set(CLAIM_TO_LO)
    if source_claims != expected_claims:
        findings.append("ADV-002 claim set is not exactly ADV-CLM-001..039")

    trace_rows: dict[str, list[str]] = {}
    for line in traceability.splitlines():
        if not line.startswith("| `ADV-CLM-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 9:
            findings.append(f"invalid ADV traceability row shape: {line[:80]}")
            continue
        claim = cells[0].strip("`")
        if claim in trace_rows:
            findings.append(f"duplicate traceability row: {claim}")
        trace_rows[claim] = cells

    if set(trace_rows) != expected_claims:
        missing = sorted(expected_claims - set(trace_rows))
        extra = sorted(set(trace_rows) - expected_claims)
        findings.append(f"traceability claim set mismatch; missing={missing}; extra={extra}")

    for claim, expected_lo in CLAIM_TO_LO.items():
        cells = trace_rows.get(claim)
        if not cells:
            continue
        expected_slides = INTEGRATED_CLAIMS.get(claim)
        if expected_slides is None:
            if cells[1] != "–":
                findings.append(f"{claim} must not claim an active slide before ADV-009/PRS-012")
            if cells[8] != "PLANNED":
                findings.append(f"{claim} must remain PLANNED before implementation")
        else:
            if cells[1] != expected_slides:
                findings.append(
                    f"{claim} must reference deck slides {expected_slides}, found {cells[1]}"
                )
            if cells[8] != "KEEP":
                findings.append(f"{claim} must be KEEP after deck integration")
        if cells[3] != f"`{expected_lo}`":
            findings.append(f"{claim} maps to {cells[3]} instead of {expected_lo}")
        if cells[4] != "VERTIEFUNG":
            findings.append(f"{claim} must remain VERTIEFUNG")

    active_claims = re.findall(r"^\| `(CLM-\d{3})` \|", traceability, flags=re.MULTILINE)
    if active_claims != [f"CLM-{number:03d}" for number in range(1, 85)]:
        findings.append("active claim sequence is not exactly CLM-001..084")

    for fragment in (
        "| Arbeitspakete | `CUR-005`, `ADV-003` |",
        "| Aktive Claims/Folien | 84 |",
        "| Geplante Vertiefungsclaims | 39 |",
        "| Davon aktiv im Deck | 8 |",
        "| Vertiefungsfolien im Deck | 18 |",
        "| Beobachtbare Lernziele | 52 |",
        "| `TP-CAPSTONE` |",
    ):
        if fragment not in traceability:
            findings.append(f"traceability missing contract fragment: {fragment}")

    if findings:
        print(f"adv-003-curriculum: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(
        "adv-003-curriculum: PASS (84 active claims; 39 planned claims, "
        f"{len(INTEGRATED_CLAIMS)} integrated; 52 learning objectives)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
