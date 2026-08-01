#!/usr/bin/env python3
"""Validate the ADV-010 deck integration using Python standard library only.

Der Pruefer bindet die vier Vertiefungsfolien zur parametersensitiven
Planoptimierung an ihre Spezifikation, an das Folien- und Aussagenregister
sowie an die Traceability-Matrix. Er prueft Struktur und Zuordnung, nicht
Layoutqualitaet.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DECK = (
    ROOT
    / "Presentations"
    / "Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx"
)
REGISTER = ROOT / "Documentation" / "Inventories" / "SLIDE_STATEMENT_REGISTER.md"
TRACEABILITY = ROOT / "Documentation" / "Curriculum" / "TRACEABILITY_MATRIX.md"
MANIFEST = ROOT / "Documentation" / "Inventories" / "SOURCE_MANIFEST.md"
PRIVACY = ROOT / "Tests" / "Static" / "validate_privacy_metadata.py"
SPEC = (
    ROOT
    / "Documentation"
    / "Curriculum"
    / "ADV_010_SLIDE_SPECIFICATION_M03_LO08_PSP.md"
)
BUILDER = ROOT / "Tools" / "build_adv010_slides.py"

P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

TOTAL_SLIDES = 98
BASE_SLIDES = 94
MODULE_LABEL = "3 · QUERY PATTERNS · VERTIEFUNG"

# Folien-ID -> (Folienteil, Anzeigeposition, Pflichtfragment im sichtbaren Text)
SLIDES = {
    "SLD-M03-121": (
        "ppt/slides/slide95.xml",
        94,
        "genau eine zwischengespeicherte Planform",
    ),
    "SLD-M03-122": (
        "ppt/slides/slide96.xml",
        95,
        "QueryVariantID",
    ),
    "SLD-M03-123": (
        "ppt/slides/slide97.xml",
        96,
        "nur Gleichheitsprädikate kommen infrage",
    ),
    "SLD-M03-124": (
        "ppt/slides/slide98.xml",
        97,
        "DISABLE_PARAMETER_SENSITIVE_PLAN",
    ),
}

INTEGRATED_CLAIMS = {
    "ADV-CLM-019": "95, 96, 97",
}

# Keine unerlaubte Vermischung dokumentierter und empirischer Aussagen.
FORBIDDEN_FRAGMENTS = (
    "immer schneller",
    "grundsätzlich schneller",
    "in jedem Fall schneller",
    "Best Practice",
)


def shape_texts(data: bytes) -> dict[str, list[str]]:
    root = ET.fromstring(data)
    tree = root.find(f"{P_NS}cSld/{P_NS}spTree")
    texts: dict[str, list[str]] = {}
    if tree is None:
        return texts
    for shape in tree.findall(f"{P_NS}sp"):
        name = shape.find(f"{P_NS}nvSpPr/{P_NS}cNvPr").get("name")
        paragraphs = [
            "".join(node.text or "" for node in paragraph.iter(f"{A_NS}t"))
            for paragraph in shape.findall(f"{P_NS}txBody/{A_NS}p")
        ]
        texts[name] = [paragraph for paragraph in paragraphs if paragraph]
    return texts


def display_order(archive: zipfile.ZipFile) -> list[str]:
    relationships = {
        node.get("Id"): node.get("Target").lstrip("/")
        for node in ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
    }
    presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
    slide_list = presentation.find(f"{P_NS}sldIdLst")
    return [relationships[node.get(R_ID)] for node in slide_list]


def check_deck(findings: list[str]) -> str:
    digest = hashlib.sha256(DECK.read_bytes()).hexdigest()
    with zipfile.ZipFile(DECK) as archive:
        corrupt = archive.testzip()
        if corrupt:
            findings.append(f"corrupt ZIP member: {corrupt}")
        names = set(archive.namelist())
        order = display_order(archive)
        if len(order) != TOTAL_SLIDES:
            findings.append(f"expected {TOTAL_SLIDES} slides in order, found {len(order)}")

        for slide_id, (part, position, fragment) in SLIDES.items():
            if part not in names:
                findings.append(f"{slide_id}: slide part {part} missing")
                continue
            notes_part = part.replace("slides/slide", "notesSlides/notesSlide")
            for required in (
                f"ppt/slides/_rels/{part.rsplit('/', 1)[1]}.rels",
                notes_part,
                f"ppt/notesSlides/_rels/{notes_part.rsplit('/', 1)[1]}.rels",
            ):
                if required not in names:
                    findings.append(f"{slide_id}: package part {required} missing")

            if position <= len(order) and order[position - 1] != part:
                findings.append(
                    f"{slide_id}: expected {part} at display position {position}, "
                    f"found {order[position - 1]}"
                )

            texts = shape_texts(archive.read(part))
            if texts.get("module-label") != [MODULE_LABEL]:
                findings.append(f"{slide_id}: module label is not the deep-dive label")
            if len(texts.get("points", [])) != 4:
                findings.append(f"{slide_id}: expected exactly four bullet points")
            if len(texts.get("lead", [])) != 1:
                findings.append(f"{slide_id}: expected exactly one lead paragraph")
            if texts.get("footer-page") != [f"{position} / {TOTAL_SLIDES}"]:
                findings.append(f"{slide_id}: footer pagination is not {position} / {TOTAL_SLIDES}")
            visible = " | ".join(part_text for values in texts.values() for part_text in values)
            if fragment not in visible:
                findings.append(f"{slide_id}: missing visible fragment: {fragment}")
            for forbidden in FORBIDDEN_FRAGMENTS:
                if forbidden in visible:
                    findings.append(f"{slide_id}: forbidden generalisation: {forbidden}")

            if notes_part in names:
                notes = shape_texts(archive.read(notes_part))
                note_text = " | ".join(notes.get("Notes Placeholder 2", []))
                if f"[SLIDE-ID: {slide_id}]" not in note_text:
                    findings.append(f"{slide_id}: speaker note marker missing")
                if "Kennzeichnung:" not in note_text:
                    findings.append(f"{slide_id}: speaker note classification line missing")
                if "Tiefe: VERTIEFUNG" not in note_text:
                    findings.append(f"{slide_id}: speaker note depth profile missing")
                if "Demo: OPT-009" not in note_text:
                    findings.append(f"{slide_id}: speaker note does not name the canonical demo")

        # Die Schlussfolie bleibt letzte Anzeigeposition.
        if order and order[-1] != "ppt/slides/slide84.xml":
            findings.append("closing slide is no longer the last display position")

        # Der ADV-009-Block behaelt seine Anzeigepositionen 84 bis 93.
        for offset in range(10):
            expected = f"ppt/slides/slide{85 + offset}.xml"
            position = 84 + offset
            if position <= len(order) and order[position - 1] != expected:
                findings.append(
                    f"ADV-009 slide {position} moved to {order[position - 1]}"
                )
                break

        # Bestehende Basisfolien behalten ihre Anzeigeposition.
        for position in range(1, 84):
            expected = f"ppt/slides/slide{position}.xml"
            if position <= len(order) and order[position - 1] != expected:
                findings.append(f"base slide {position} moved to {order[position - 1]}")
                break
    return digest


def check_documents(findings: list[str], digest: str) -> None:
    register = REGISTER.read_text(encoding="utf-8")
    traceability = TRACEABILITY.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")
    privacy = PRIVACY.read_text(encoding="utf-8")
    builder = BUILDER.read_text(encoding="utf-8")

    if f'"{digest}"' not in privacy:
        findings.append("privacy scanner does not approve the current deck hash")
    if f"`{digest}`" not in register:
        findings.append("statement register does not carry the current deck hash")
    if f"`{digest}`" not in manifest:
        findings.append("source manifest does not carry the current deck hash")
    if f"SHA-256 {digest}" in builder:
        findings.append("builder must not hard-code the deck hash")
    if f"BASE_SLIDE_COUNT = {BASE_SLIDES}" not in builder:
        findings.append("builder does not start from the registered base slide count")

    for slide_id, (part, position, _) in SLIDES.items():
        row = next(
            (line for line in register.splitlines() if line.startswith(f"| {slide_id} |")), ""
        )
        if not row:
            findings.append(f"{slide_id}: no row in statement register")
            continue
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) != 11:
            findings.append(f"{slide_id}: register row has {len(cells)} cells instead of 11")
            continue
        if cells[1] != str(position):
            findings.append(f"{slide_id}: register slide number is {cells[1]}, expected {position}")
        if cells[2] != f"`{part.rsplit('/', 1)[1]}`":
            findings.append(f"{slide_id}: register slide part is {cells[2]}")
        if cells[9] != "KEEP":
            findings.append(f"{slide_id}: register decision is {cells[9]} instead of KEEP")

    for claim, slides in INTEGRATED_CLAIMS.items():
        row = next(
            (line for line in traceability.splitlines() if line.startswith(f"| `{claim}` |")), ""
        )
        if not row:
            findings.append(f"{claim}: no traceability row")
            continue
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if cells[1] != slides:
            findings.append(f"{claim}: traceability slides are {cells[1]}, expected {slides}")
        if cells[8] != "KEEP":
            findings.append(f"{claim}: traceability decision is {cells[8]} instead of KEEP")

    text = SPEC.read_text(encoding="utf-8")
    if "| Status | `INTEGRATED` |" not in text:
        findings.append(f"{SPEC.name}: status is not INTEGRATED")
    for number in range(121, 125):
        if f"SLD-M03-{number}" not in text:
            findings.append(f"{SPEC.name}: missing slide specification SLD-M03-{number}")
    if re.search(r"Bis dahin bleiben die Claims", text):
        findings.append(f"{SPEC.name}: obsolete pre-integration wording remains")


def main() -> int:
    findings: list[str] = []
    if not DECK.is_file():
        print("adv010-deck-integration: FAIL (deck missing)")
        return 1
    try:
        digest = check_deck(findings)
        check_documents(findings, digest)
    except (zipfile.BadZipFile, ET.ParseError, OSError, KeyError) as exc:
        findings.append(f"deck or documents cannot be evaluated: {exc}")

    if findings:
        print(f"adv010-deck-integration: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(
        f"adv010-deck-integration: PASS ({len(SLIDES)} deep-dive slides, "
        f"{len(INTEGRATED_CLAIMS)} claim, {TOTAL_SLIDES} slides total)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
