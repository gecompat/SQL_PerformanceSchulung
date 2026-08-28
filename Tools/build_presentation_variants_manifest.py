#!/usr/bin/env python3
"""Build the schema-v1 presentation variant manifest from project registers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECK = ROOT / "Presentations" / "Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx"
DEFAULT_OUTPUT = ROOT / "Presentations" / "variants" / "presentation_variants.json"
REGISTER = ROOT / "Documentation" / "Inventories" / "SLIDE_STATEMENT_REGISTER.md"
TRACEABILITY = ROOT / "Documentation" / "Curriculum" / "TRACEABILITY_MATRIX.md"

P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

MODULES = {
    "Einstieg": "M00",
    "Storage": "M01",
    "Query Processing": "M02",
    "Query Patterns": "M03",
    "Indexes": "M04",
    "Columnstore": "M04",
    "Concurrency": "M05",
    "Diagnose": "M06",
    "Abschluss": "M07",
}

INTRO_CLAIMS = {"CLM-001", "CLM-007", "CLM-019", "CLM-036", "CLM-048", "CLM-063", "CLM-071"}
SUMMARY_CLAIMS = {"CLM-018", "CLM-035", "CLM-047", "CLM-062", "CLM-070", "CLM-080", "CLM-081", "CLM-084"}
BASIS_TECHNICAL_CLAIMS = {
    "CLM-008", "CLM-010", "CLM-014", "CLM-015",
    "CLM-020", "CLM-022", "CLM-026", "CLM-027",
    "CLM-037", "CLM-039", "CLM-049", "CLM-052",
    "CLM-064", "CLM-066", "CLM-072", "CLM-076", "CLM-077",
}

ALL_ROLES = [
    "INTRO", "THEORY", "DEMO_INTRO", "DEMO_EXECUTION", "DEMO_RESULT",
    "LAB", "EXERCISE", "SOLUTION", "SUMMARY", "TRANSITION", "REFERENCE",
]


def cells(line: str) -> list[str]:
    return [cell.strip().replace("`", "") for cell in line.strip().strip("|").split("|")]


def ids(value: str, pattern: str) -> list[str]:
    if value in {"", "–", "-"}:
        return []
    return list(dict.fromkeys(re.findall(pattern, value)))


def learning_objectives(value: str) -> list[str]:
    result: list[str] = []
    for module, start, end in re.findall(r"LO-(M0[0-7])-(\d{2})(?:\.\.(\d{2}))?", value):
        last = int(end or start)
        result.extend(f"LO-{module}-{number:02d}" for number in range(int(start), last + 1))
    return list(dict.fromkeys(result))


def display_order(deck: Path) -> list[str]:
    with zipfile.ZipFile(deck) as archive:
        relationships = {
            node.get("Id"): node.get("Target").lstrip("/")
            for node in ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
        }
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        slide_list = presentation.find(f"{P_NS}sldIdLst")
        if slide_list is None:
            raise ValueError("presentation has no slide list")
        return [relationships[node.get(R_ID)] for node in slide_list]


def trace_rows() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in TRACEABILITY.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| `(CLM|ADV-CLM)-\d{3}` \|", line):
            row = cells(line)
            rows[row[0]] = row
    return rows


def register_rows() -> tuple[list[list[str]], list[list[str]]]:
    base: list[list[str]] = []
    deep: list[list[str]] = []
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| CLM-\d{3} \|", line):
            base.append(cells(line))
        elif re.match(r"^\| SLD-M0[0-7]-\d{3} \|", line):
            deep.append(cells(line))
    return base, deep


def slide_depth(claim: str, evidence: str, path: str) -> str:
    if path == "VERTIEFUNG":
        return "VERTIEFUNG"
    if claim in BASIS_TECHNICAL_CLAIMS or "DIDACTIC" in evidence or "METHOD" in evidence:
        return "BASIS"
    return "STANDARD"


def slide_role(claim: str) -> str:
    if claim in INTRO_CLAIMS:
        return "INTRO"
    if claim in SUMMARY_CLAIMS:
        return "SUMMARY"
    if claim == "CLM-082":
        return "EXERCISE"
    if claim == "CLM-083":
        return "REFERENCE"
    return "THEORY"


def build(deck: Path) -> dict:
    order = display_order(deck)
    if len(order) != 102:
        raise ValueError(f"expected 102 slides, found {len(order)}")
    trace = trace_rows()
    base_rows, deep_rows = register_rows()
    slides: dict[str, dict] = {}
    module_sequences = {module: 0 for module in MODULES.values()}

    for row in base_rows:
        claim, _position, stable_id, module_label, evidence, title, _boundary, sources, _decision, demos = row
        module = MODULES[module_label]
        module_sequences[module] += 1
        slide_key = f"SLD-{module}-{module_sequences[module]:03d}"
        tr = trace[claim]
        path = tr[4]
        slides[slide_key] = {
            "order": 102 if claim == "CLM-084" else int(claim[-3:]),
            "module": module,
            "depth": slide_depth(claim, evidence, path),
            "roles": [slide_role(claim)],
            "title": re.sub(r"\s+", " ", title)[:160],
            "claims": [claim],
            "sources": ids(sources, r"SRC-\d{3}"),
            "learning_objectives": learning_objectives(tr[3]),
            "demos": ids(demos, r"(?:FWK|STL|OPT|QRY|IDX|CON|RES|DGN|INF)-\d{3}"),
            "requires": [],
            "paired_with": [],
            "links_to": [],
            "profile_overrides": [],
            "notes_required": True,
            "_stable_id": stable_id,
        }

    for row in deep_rows:
        slide_key, position, _part, claims, module_label, _evidence, title, _boundary, sources, _decision, demos = row
        claim_ids = ids(claims, r"ADV-CLM-\d{3}")
        learning = []
        for claim in claim_ids:
            learning.extend(learning_objectives(trace[claim][3]))
        if not learning:
            learning = ["LO-M03-07"] if slide_key < "SLD-M03-111" else ["LO-M03-08"]
        slides[slide_key] = {
            "order": int(position),
            "module": MODULES[module_label],
            "depth": "VERTIEFUNG",
            "roles": ["THEORY"],
            "title": re.sub(r"\s+", " ", title)[:160],
            "claims": claim_ids,
            "sources": ids(sources, r"SRC-\d{3}"),
            "learning_objectives": list(dict.fromkeys(learning)),
            "demos": ids(demos, r"(?:FWK|STL|OPT|QRY|IDX|CON|RES|DGN|INF)-\d{3}"),
            "requires": [],
            "paired_with": [],
            "links_to": [],
            "profile_overrides": [],
            "notes_required": True,
        }

    for value in slides.values():
        value.pop("_stable_id", None)
    slides = dict(sorted(slides.items(), key=lambda item: item[1]["order"]))
    if len(slides) != 102 or sorted(value["order"] for value in slides.values()) != list(range(1, 103)):
        raise ValueError("manifest slide inventory is incomplete or has duplicate order values")

    return {
        "schema_version": 1,
        "master_deck": str(deck.relative_to(ROOT)).replace("\\", "/"),
        "master_sha256": hashlib.sha256(deck.read_bytes()).hexdigest(),
        "profiles": {
            "BASIS": {
                "custom_show": "SQL Performance – Basis",
                "include_depth": ["BASIS"],
                "include_roles": ALL_ROLES,
                "exclude_slide_keys": [],
                "rationale": "Gemeinsamer Kernpfad mit Diagnosemethode und sicheren Grundbegriffen.",
            },
            "STANDARD": {
                "custom_show": "SQL Performance – Standard",
                "include_depth": ["BASIS", "STANDARD"],
                "include_roles": ALL_ROLES,
                "exclude_slide_keys": [],
                "rationale": "Regulaere Schulung mit technischer Herleitung ueber den Kernpfad hinaus.",
            },
            "VERTIEFUNG": {
                "custom_show": "SQL Performance – Vertiefung",
                "include_depth": ["BASIS", "STANDARD", "VERTIEFUNG"],
                "include_roles": ALL_ROLES,
                "exclude_slide_keys": [],
                "rationale": "Vollstaendiger freigegebener Bestand einschliesslich Optimizer-Internals und IQP.",
            },
        },
        "slides": slides,
        "build": {
            "output_directory": "Presentations/variants/build",
            "filename_pattern": "SQL_PerformanceSchulung_{PROFILE}_{MASTER_SHORT_HASH}.pptx",
            "preserve_master": True,
            "delete_excluded_descending": True,
            "fail_on_broken_links": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck", type=Path, default=DEFAULT_DECK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.deck.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"presentation-variant-manifest: PASS ({len(payload['slides'])} slides; {args.output})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
