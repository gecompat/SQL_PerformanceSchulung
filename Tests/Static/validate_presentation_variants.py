#!/usr/bin/env python3
"""Read-only TST-011 validation for the master deck and schema-v1 manifest."""

from __future__ import annotations

import hashlib
import json
import posixpath
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "Presentations" / "variants" / "presentation_variants.json"
SCHEMA_PATH = ROOT / "Presentations" / "variants" / "presentation_variants.schema.json"
SOURCE_REGISTER = ROOT / "Documentation" / "Research" / "SOURCE_REGISTER.md"
TRACEABILITY = ROOT / "Documentation" / "Curriculum" / "TRACEABILITY_MATRIX.md"
SLIDE_REGISTER = ROOT / "Documentation" / "Inventories" / "SLIDE_STATEMENT_REGISTER.md"
IDENTIFIERS = ROOT / ".ai" / "identity" / "registry.json"

P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

SLIDE_KEY = re.compile(r"^SLD-M0[0-7]-[0-9]{3}$")
CLAIM = re.compile(r"^(?:CLM|ADV-CLM)-[0-9]{3}$")
SOURCE = re.compile(r"^SRC-[0-9]{3}$")
LEARNING_OBJECTIVE = re.compile(r"^LO-M0[0-7]-[0-9]{2}$")
DEMO = re.compile(r"^(?:FWK|STL|OPT|QRY|IDX|CON|RES|DGN|INF)-[0-9]{3}$")
DEPTHS = {"BASIS", "STANDARD", "VERTIEFUNG"}
ROLES = {
    "INTRO", "THEORY", "DEMO_INTRO", "DEMO_EXECUTION", "DEMO_RESULT",
    "LAB", "EXERCISE", "SOLUTION", "SUMMARY", "TRANSITION", "REFERENCE",
}
SLIDE_FIELDS = {
    "order", "module", "depth", "roles", "title", "claims", "sources",
    "learning_objectives", "demos", "requires", "paired_with", "links_to",
    "profile_overrides", "notes_required",
}


def normalize_part(base: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def relationships(archive: zipfile.ZipFile, part: str) -> dict[str, tuple[str, str]]:
    directory, name = posixpath.split(part)
    rels_part = posixpath.join(directory, "_rels", f"{name}.rels")
    if rels_part not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read(rels_part))
    return {
        node.get("Id"): (node.get("Type", ""), normalize_part(part, node.get("Target", "")))
        for node in root.findall(f"{R_NS}Relationship")
    }


def deck_state(deck: Path) -> tuple[list[str], dict[str, str], dict[str, list[str]]]:
    with zipfile.ZipFile(deck) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"corrupt ZIP member: {corrupt}")
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        rels = relationships(archive, "ppt/presentation.xml")
        slide_list = presentation.find(f"{P_NS}sldIdLst")
        if slide_list is None:
            raise ValueError("presentation has no slide list")
        order = [rels[node.get(R_ID)][1] for node in slide_list]

        notes: dict[str, str] = {}
        for slide_part in order:
            note_parts = [target for _rid, (kind, target) in relationships(archive, slide_part).items() if kind.endswith("/notesSlide")]
            if len(note_parts) != 1:
                raise ValueError(f"{slide_part} has {len(note_parts)} notes relationships")
            note_root = ET.fromstring(archive.read(note_parts[0]))
            notes[slide_part] = "\n".join(node.text or "" for node in note_root.iter(f"{A_NS}t"))

        shows: dict[str, list[str]] = {}
        show_list = presentation.find(f"{P_NS}custShowLst")
        if show_list is not None:
            for show in show_list.findall(f"{P_NS}custShow"):
                slide_ids = show.find(f"{P_NS}sldLst")
                shows[show.get("name", "")] = [
                    rels[node.get(R_ID)][1]
                    for node in ([] if slide_ids is None else list(slide_ids))
                ]
        return order, notes, shows


def expected_profile(manifest: dict, profile_name: str) -> list[str]:
    profile = manifest["profiles"][profile_name]
    result = []
    for key, slide in sorted(manifest["slides"].items(), key=lambda item: item[1]["order"]):
        include = (
            slide["depth"] in profile["include_depth"]
            and any(role in profile["include_roles"] for role in slide["roles"])
            and key not in profile.get("exclude_slide_keys", [])
        )
        for override in slide["profile_overrides"]:
            if override["profile"] == profile_name:
                include = override["include"]
        if include:
            result.append(key)
    return result


def validate() -> list[str]:
    findings: list[str] = []
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest or schema cannot be read: {exc}"]

    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        findings.append("schema is not JSON Schema Draft 2020-12")
    if set(manifest) != {"schema_version", "master_deck", "master_sha256", "profiles", "slides", "build"}:
        findings.append("manifest root fields differ from schema version 1")
        return findings
    if manifest["schema_version"] != 1:
        findings.append("schema_version must be 1")
    if set(manifest["profiles"]) != DEPTHS:
        findings.append("profiles must be exactly BASIS, STANDARD and VERTIEFUNG")

    deck = ROOT / manifest["master_deck"]
    if not deck.is_file():
        findings.append(f"master deck missing: {manifest['master_deck']}")
        return findings
    digest = hashlib.sha256(deck.read_bytes()).hexdigest()
    if digest != manifest["master_sha256"]:
        findings.append(f"master_sha256 mismatch: manifest={manifest['master_sha256']}; deck={digest}")

    known_claims = set(re.findall(r"(?:ADV-)?CLM-[0-9]{3}", SLIDE_REGISTER.read_text(encoding="utf-8") + TRACEABILITY.read_text(encoding="utf-8")))
    known_sources = set(re.findall(r"SRC-[0-9]{3}", SOURCE_REGISTER.read_text(encoding="utf-8")))
    known_objectives = set(re.findall(r"LO-M0[0-7]-[0-9]{2}", TRACEABILITY.read_text(encoding="utf-8")))
    registry = json.loads(IDENTIFIERS.read_text(encoding="utf-8"))
    known_demos = set(registry["artifacts"])

    slides = manifest["slides"]
    if len(slides) != 102:
        findings.append(f"expected 102 manifest slides, found {len(slides)}")
    orders: list[int] = []
    for key, slide in slides.items():
        if not SLIDE_KEY.fullmatch(key):
            findings.append(f"invalid SlideKey: {key}")
        if set(slide) != SLIDE_FIELDS:
            findings.append(f"{key}: fields differ from schema version 1")
            continue
        orders.append(slide["order"])
        if slide["module"] != key[4:7]:
            findings.append(f"{key}: module does not match SlideKey")
        if slide["depth"] not in DEPTHS:
            findings.append(f"{key}: invalid depth")
        if not slide["roles"] or len(slide["roles"]) != len(set(slide["roles"])) or not set(slide["roles"]) <= ROLES:
            findings.append(f"{key}: invalid roles")
        for field, pattern, known in (
            ("claims", CLAIM, known_claims),
            ("sources", SOURCE, known_sources),
            ("learning_objectives", LEARNING_OBJECTIVE, known_objectives),
            ("demos", DEMO, known_demos),
        ):
            values = slide[field]
            if len(values) != len(set(values)):
                findings.append(f"{key}: duplicate {field}")
            for value in values:
                if not pattern.fullmatch(value) or value not in known:
                    findings.append(f"{key}: unknown {field} identifier {value}")
        if slide["claims"] and not slide["sources"] and not set(slide["roles"]) <= {"INTRO", "SUMMARY", "TRANSITION", "EXERCISE"}:
            findings.append(f"{key}: technical claim has no source")
        for field in ("requires", "paired_with", "links_to"):
            for target in slide[field]:
                if target not in slides:
                    findings.append(f"{key}: {field} references unknown SlideKey {target}")
        for target in slide["paired_with"]:
            if key not in slides[target]["paired_with"]:
                findings.append(f"{key}: pairing with {target} is not symmetric")

    if sorted(orders) != list(range(1, len(slides) + 1)):
        findings.append("slide order is not unique and contiguous")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(key: str) -> None:
        if key in visiting:
            findings.append(f"requires cycle reaches {key}")
            return
        if key in visited:
            return
        visiting.add(key)
        for target in slides[key]["requires"]:
            visit(target)
        visiting.remove(key)
        visited.add(key)
    for key in slides:
        visit(key)

    inclusions = {profile: expected_profile(manifest, profile) for profile in DEPTHS}
    if not set(inclusions["BASIS"]) <= set(inclusions["STANDARD"]) <= set(inclusions["VERTIEFUNG"]):
        findings.append("profiles are not cumulative")
    for profile_name, keys in inclusions.items():
        for key in keys:
            missing = set(slides[key]["requires"]) - set(keys)
            if missing:
                findings.append(f"{profile_name}/{key}: missing prerequisites {sorted(missing)}")

    try:
        order, notes, shows = deck_state(deck)
    except (OSError, zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as exc:
        findings.append(f"deck cannot be inspected: {exc}")
        return findings
    if len(order) != len(slides):
        findings.append(f"deck has {len(order)} slides, manifest has {len(slides)}")
        return findings
    key_by_order = {slide["order"]: key for key, slide in slides.items()}
    key_by_part = {part: key_by_order[index] for index, part in enumerate(order, 1)}
    for index, part in enumerate(order, 1):
        expected = key_by_order[index]
        markers = re.findall(r"\[SLIDE-ID: (SLD-M0[0-7]-[0-9]{3})\]", notes[part])
        if markers != [expected]:
            findings.append(f"slide {index}: expected exactly [{expected}], found {markers}")
        if slides[expected]["notes_required"] and not notes[part].strip():
            findings.append(f"slide {index}/{expected}: required notes are empty")

    expected_show_names = {manifest["profiles"][profile]["custom_show"] for profile in DEPTHS}
    if set(shows) != expected_show_names:
        findings.append(f"custom show names differ: {sorted(shows)}")
    for profile_name, expected_keys in inclusions.items():
        name = manifest["profiles"][profile_name]["custom_show"]
        actual_keys = [key_by_part[part] for part in shows.get(name, []) if part in key_by_part]
        if actual_keys != expected_keys:
            findings.append(f"{profile_name}: custom show membership or order differs")

    return findings


def main() -> int:
    findings = validate()
    if findings:
        print(f"presentation-variants: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("presentation-variants: PASS (schema v1; 102 SlideKeys; custom shows 41/66/102)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
