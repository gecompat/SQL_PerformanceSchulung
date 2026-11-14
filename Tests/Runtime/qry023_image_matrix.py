#!/usr/bin/env python3
"""Resolve the fixed QRY-023 proposed image lock into a GitHub matrix."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/container-images.proposed.json"
EXPECTED = ((2019, 15, 150), (2022, 16, 160), (2025, 17, 170))


def resolve(document: Any) -> list[dict[str, Any]]:
    if type(document) is not dict:
        raise ValueError("image lock root must be an object")
    if (document.get("contract_version") != "1.0"
            or document.get("status") != "PROPOSED"
            or document.get("runtime_authorized") is not False):
        raise ValueError("only the non-authorizing QRY-023 proposed lock is accepted")
    profiles = document.get("profiles")
    if type(profiles) is not list or len(profiles) != len(EXPECTED):
        raise ValueError("image lock must contain exactly three profiles")

    matrix: list[dict[str, Any]] = []
    seen_majors: set[int] = set()
    for profile, (year, major, compatibility_level) in zip(profiles, EXPECTED, strict=True):
        if type(profile) is not dict:
            raise ValueError("each image profile must be an object")
        digest = profile.get("manifest_digest")
        image = profile.get("image")
        if (profile.get("product_major_version") != major
                or profile.get("compatibility_level") != compatibility_level
                or profile.get("platform") != "linux/amd64"
                or type(digest) is not str
                or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None
                or image != f"mcr.microsoft.com/mssql/server@{digest}"
                or type(profile.get("product_version_label")) is not str
                or not profile["product_version_label"].startswith(f"{major}.")):
            raise ValueError(f"SQL Server {year} image profile does not match the fixed product contract")
        if major in seen_majors:
            raise ValueError(f"duplicate SQL Server product major {major}")
        seen_majors.add(major)
        matrix.append({"year": year, "major": major, "image": image})
    return matrix


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: qry023_image_matrix.py GITHUB_OUTPUT", file=sys.stderr)
        return 2
    try:
        document = json.loads(LOCK.read_text(encoding="utf-8"))
        matrix = resolve(document)
        output = Path(argv[1])
        with output.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("matrix=" + json.dumps({"include": matrix}, separators=(",", ":")) + "\n")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"QRY-023 image lock resolution failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
