#!/usr/bin/env python3
"""Verify that every released demo has a reproducible execution guide."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
DEMOS = ROOT / "Demos"
GUIDE = ROOT / "Documentation" / "HowTo" / "DEMO_EXECUTION_GUIDE.md"
DEMO_ENTRYPOINT = DEMOS / "README.md"
GUIDE_LINK = "Documentation/HowTo/DEMO_EXECUTION_GUIDE.md"
README_GUIDE_LINK = "../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md"
README_GUIDE_HEADING = "Schritt-für-Schritt-Anleitung"
README_REQUIRED_TOKENS = ("manifestbasiert", "markergebunden")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    findings: list[str] = []
    if not GUIDE.is_file():
        findings.append("Documentation/HowTo/DEMO_EXECUTION_GUIDE.md fehlt")
    if not DEMO_ENTRYPOINT.is_file():
        findings.append("Demos/README.md fehlt")
    if findings:
        print(f"demo-execution-guide: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    guide = read(GUIDE)
    entrypoint = read(DEMO_ENTRYPOINT)
    if GUIDE_LINK not in entrypoint:
        findings.append("Demos/README.md verweist nicht auf den Ausführungsleitfaden")

    manifests = sorted(
        path for path in DEMOS.rglob("manifest.json") if "00_Framework" not in path.parts
    )
    if not manifests:
        findings.append("keine Fachdemo-Manifeste gefunden")

    for manifest_path in manifests:
        try:
            manifest = json.loads(read(manifest_path))
        except json.JSONDecodeError as exc:
            findings.append(f"{manifest_path.relative_to(ROOT)}: ungültiges JSON ({exc.msg})")
            continue
        demo_id = manifest.get("demo_id")
        safety_level = manifest.get("safety_level")
        if not isinstance(demo_id, str) or not demo_id:
            findings.append(f"{manifest_path.relative_to(ROOT)}: demo_id fehlt")
            continue
        if f"`{demo_id}`" not in guide:
            findings.append(f"{manifest_path.relative_to(ROOT)}: {demo_id} fehlt im Ausführungsleitfaden")
        manifest_reference = manifest_path.relative_to(ROOT).as_posix()
        if manifest_reference not in guide:
            findings.append(f"{manifest_path.relative_to(ROOT)}: Manifestpfad fehlt im Ausführungsleitfaden")
        readme_path = manifest_path.with_name("README.md")
        if not readme_path.is_file():
            findings.append(f"{manifest_path.relative_to(ROOT)}: Demo-README fehlt")
            continue
        readme = read(readme_path)
        if README_GUIDE_HEADING not in readme or README_GUIDE_LINK not in readme:
            findings.append(
                f"{readme_path.relative_to(ROOT)}: eigene Schritt-für-Schritt-Anleitung fehlt"
            )
        for token in README_REQUIRED_TOKENS:
            if token not in readme:
                findings.append(
                    f"{readme_path.relative_to(ROOT)}: Anleitung benennt {token} nicht"
                )
        if safety_level == "YELLOW" and "-ConfirmIsolatedLab" not in guide:
            findings.append(f"{manifest_path.relative_to(ROOT)}: gelbe Sicherheitsbestätigung fehlt")
        if safety_level == "RED" and "-AllowRed" not in guide:
            findings.append(f"{manifest_path.relative_to(ROOT)}: rote Sicherheitsbestätigung fehlt")
        if safety_level == "YELLOW" and "-ConfirmIsolatedLab" not in readme:
            findings.append(f"{readme_path.relative_to(ROOT)}: gelbe Sicherheitsbestätigung fehlt")
        if safety_level == "RED" and "-AllowRed" not in readme:
            findings.append(f"{readme_path.relative_to(ROOT)}: rote Sicherheitsbestätigung fehlt")

    if findings:
        print(f"demo-execution-guide: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"demo-execution-guide: PASS ({len(manifests)} guided demo manifest(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
