#!/usr/bin/env python3
"""TST-012 static and render evidence validation for built presentation profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def normalize(base: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def rels(archive: zipfile.ZipFile, part: str) -> dict[str, tuple[str, str, str]]:
    directory, name = posixpath.split(part)
    rels_part = posixpath.join(directory, "_rels", f"{name}.rels")
    if rels_part not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read(rels_part))
    return {
        node.get("Id"): (node.get("Type", ""), normalize(part, node.get("Target", "")), node.get("TargetMode", "Internal"))
        for node in root.findall(f"{R_NS}Relationship")
    }


def expected_keys(manifest: dict, profile_name: str) -> list[str]:
    profile = manifest["profiles"][profile_name]
    keys = []
    for key, slide in sorted(manifest["slides"].items(), key=lambda item: item[1]["order"]):
        include = slide["depth"] in profile["include_depth"] and any(role in profile["include_roles"] for role in slide["roles"])
        include = include and key not in profile.get("exclude_slide_keys", [])
        for override in slide["profile_overrides"]:
            if override["profile"] == profile_name:
                include = override["include"]
        if include:
            keys.append(key)
    return keys


def inspect_deck(path: Path, expected: list[str], findings: list[str], label: str) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            corrupt = archive.testzip()
            if corrupt:
                findings.append(f"{label}: corrupt ZIP member {corrupt}")
            presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
            relationships = rels(archive, "ppt/presentation.xml")
            slide_list = presentation.find(f"{P_NS}sldIdLst")
            order = [
                relationships[node.get(R_ID)][1]
                for node in ([] if slide_list is None else list(slide_list))
            ]
            if len(order) != len(expected):
                findings.append(f"{label}: expected {len(expected)} slides, found {len(order)}")
                return
            actual: list[str] = []
            visible_text: list[str] = []
            for part in order:
                visible_text.append(" ".join(node.text or "" for node in ET.fromstring(archive.read(part)).iter(f"{A_NS}t")))
                slide_rels = rels(archive, part)
                note_parts = [target for kind, target, mode in slide_rels.values() if kind.endswith("/notesSlide") and mode == "Internal"]
                if len(note_parts) != 1:
                    findings.append(f"{label}: {part} has {len(note_parts)} notes parts")
                    continue
                note_text = " ".join(node.text or "" for node in ET.fromstring(archive.read(note_parts[0])).iter(f"{A_NS}t"))
                markers = re.findall(r"\[SLIDE-ID: (SLD-M0[0-7]-[0-9]{3})\]", note_text)
                if len(markers) != 1:
                    findings.append(f"{label}: {part} has {len(markers)} SlideKey markers")
                else:
                    actual.append(markers[0])
                for kind, target, mode in slide_rels.values():
                    if mode == "Internal" and kind.endswith("/slide") and target not in names:
                        findings.append(f"{label}: broken internal slide target {target}")
            if actual != expected:
                findings.append(f"{label}: SlideKey membership or order differs")
            if not visible_text or "SQL SERVER PERFORMANCE" not in visible_text[0].upper():
                findings.append(f"{label}: title-slide branding marker missing")
            if not visible_text or "Performance wird erklärbar" not in visible_text[-1]:
                findings.append(f"{label}: closing-slide branding marker missing")
    except (OSError, zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
        findings.append(f"{label}: cannot inspect deck: {exc}")


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "Presentations" / "variants" / "presentation_variants.json")
    parser.add_argument("--build-directory", type=Path, default=ROOT / "Presentations" / "variants" / "build")
    parser.add_argument("--render-directory", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    build_log_path = args.build_directory / "presentation-variant-build.json"
    findings: list[str] = []
    if not build_log_path.is_file():
        findings.append("build log is missing")
    else:
        build_log = json.loads(build_log_path.read_text(encoding="utf-8-sig"))
        if not build_log.get("preserve_master") or build_log.get("master_sha256_before") != build_log.get("master_sha256_after"):
            findings.append("build log does not prove an unchanged master deck")

    short_hash = manifest["master_sha256"][:8]
    for profile_name in ("BASIS", "STANDARD", "VERTIEFUNG"):
        filename = manifest["build"]["filename_pattern"].replace("{PROFILE}", profile_name).replace("{MASTER_SHORT_HASH}", short_hash)
        deck = args.build_directory / filename
        if not deck.is_file():
            findings.append(f"{profile_name}: output deck is missing")
            continue
        inspect_deck(deck, expected_keys(manifest, profile_name), findings, profile_name)
        if args.render_directory is not None:
            render_path = args.render_directory / profile_name
            pngs = sorted(render_path.glob("*.PNG"))
            expected_count = len(expected_keys(manifest, profile_name))
            if len(pngs) != expected_count:
                findings.append(f"{profile_name}: expected {expected_count} renders, found {len(pngs)}")
            for png in pngs:
                try:
                    if png_size(png) != (1280, 720) or png.stat().st_size < 1000:
                        findings.append(f"{profile_name}: invalid render {png.name}")
                except (OSError, ValueError) as exc:
                    findings.append(f"{profile_name}: cannot inspect render {png.name}: {exc}")

    if findings:
        print(f"presentation-variant-outputs: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    render_text = " with renders" if args.render_directory is not None else ""
    print(f"presentation-variant-outputs: PASS (41/66/102 slides{render_text}; master preserved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
