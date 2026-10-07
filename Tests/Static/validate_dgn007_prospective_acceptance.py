#!/usr/bin/env python3
"""Prüft die reine Evaluator-/JSON-/CI-Grenze; kein SQL- oder Incidentnachweis."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "Tests/Contracts/dgn007_prospective_acceptance.py"
CONTRACT = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/incident-acceptance.contract.json"
WORKFLOW = ROOT / ".github/workflows/dgn007-prospective-acceptance.yml"
TRIGGER_PATHS = {
    str(MODULE.relative_to(ROOT)).replace("\\", "/"),
    str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
    "Tests/Static/test_dgn007_prospective_acceptance.py",
    "Tests/Static/validate_dgn007_prospective_acceptance.py",
    str(WORKFLOW.relative_to(ROOT)).replace("\\", "/"),
}
SOURCE_FILES = (
    "00_Preflight.sql", "10_Setup.sql", "15_Control_AB.sql", "15_Control_BA.sql", "15_Control_AA.sql",
    "20_Query_Store_Windows.sql", "21_Controlled_Query_Store_Windows.sql", "30_Profile_Comparison.sql",
    "35_Control_Evidence.sql", "40_Data_Assertion.sql", "90_Cleanup.sql",
    "control-ab.manifest.json", "control-ba.manifest.json", "control-aa.manifest.json",
)
AUTOMATED = CONTRACT.parent.parent / "Automated"
TRIGGER_PATHS.update(str((AUTOMATED / name).relative_to(ROOT)).replace("\\", "/") for name in SOURCE_FILES)


def source_findings(mapping: dict) -> list[str]:
    """Nur tatsächliche UTF-8-CRLF→LF-Bytes prüfen; Hashes attestieren keinen Vorabfreeze."""
    hashes = mapping.get("source_sha256", {})
    if type(hashes) is not dict or set(hashes) != set(SOURCE_FILES):
        return ["Quellenbindung benötigt exakt die 14 bestehenden SQL-/Manifestdateien"]
    findings = []
    for name in SOURCE_FILES:
        text = (AUTOMATED / name).read_bytes().decode("utf-8").replace("\r\n", "\n")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != hashes[name]:
            findings.append(f"Normalisierte Quellenbindung stimmt nicht: {name}")
    return findings


def pure_findings(source: str) -> list[str]:
    tree = ast.parse(source)
    findings = []
    allowed = {"__future__", "dataclasses", "decimal", "fractions", "hashlib", "json", "re", "typing", "collections", "enum", "math", "functools"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if any(name.split(".", 1)[0] not in allowed for name in names):
                findings.append("Der reine Evaluator darf keine I/O-/SQL-/Prozessmodule importieren")
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in {"open", "print", "input", "eval", "exec", "__import__", "read_text", "read_bytes", "write_text", "write_bytes", "write", "system", "Popen", "run_sql", "run_sqlcmd"}:
                findings.append("Der reine Evaluator darf keine Dateien, Prozesse, SQL oder Konsolenausgaben verwenden")
    return findings


def workflow_findings(source: str) -> list[str]:
    findings = []
    for event in ("pull_request", "push"):
        match = re.search(rf"(?ms)^  {event}:\n(.*?)(?=^  [a-z_]+:|^permissions:|\Z)", source)
        paths = set(re.findall(r"^      - '([^']+)'$", match[1], re.MULTILINE)) if match else set()
        if paths != TRIGGER_PATHS:
            findings.append(f"Prospektive {event}-CI muss exakt auf Modul, Vertrag, Fixtures und eigenen Workflow begrenzt sein")
        if event == "push" and (match is None or "branches: [main]" not in match[1]):
            findings.append("Prospektiver Push-Workflow muss auf main begrenzt sein")
    for marker in ("  workflow_dispatch:", "  contents: read", "    runs-on: ubuntu-latest", "    timeout-minutes: 5",
                   "  group: dgn007-prospective-acceptance-", "  cancel-in-progress: true",
                   "run: python Tests/Static/validate_dgn007_prospective_acceptance.py",
                   "run: python Tests/Static/test_dgn007_prospective_acceptance.py"):
        if marker not in source:
            findings.append(f"Reiner CI-Vertrag fehlt: {marker}")
    if re.search(r"\bdocker\b|\bpodman\b|run_dgn007_automated_setup|SQLCMDPASSWORD|upload-artifact|--show-output|workflow_run:|pull_request_target:", source, re.IGNORECASE):
        findings.append("Prospektive Statik-CI darf keine SQL-Runtime, Exporte oder fremden Workflows starten")
    return findings


def main() -> int:
    findings = pure_findings(MODULE.read_text(encoding="utf-8"))
    workflow = WORKFLOW.read_text(encoding="utf-8")
    findings.extend(workflow_findings(workflow))
    sys.path.insert(0, str(MODULE.parent))
    import dgn007_prospective_acceptance as acceptance
    mapping = json.loads(CONTRACT.read_text(encoding="utf-8"))
    try:
        acceptance.contract_from_mapping(mapping)
    except (acceptance.ContractError, ValueError, TypeError):
        findings.append("Prospektiver JSON-Vertrag wird vom tatsächlichen Evaluator nicht akzeptiert")
    findings.extend(source_findings(mapping))
    for before, after in (("timeout-minutes: 5", "timeout-minutes: 0"),
                          ("cancel-in-progress: true", "cancel-in-progress: false"),
                          ("Tests/Contracts/dgn007_prospective_acceptance.py", "Tests/Runtime/**"),
                          ("run: python Tests/Static/test_dgn007_prospective_acceptance.py", "run: true")):
        if not workflow_findings(workflow.replace(before, after)):
            findings.append("Negative prospektive CI-Kontrolle wurde nicht erkannt")
    for mutation in ("import subprocess\n", "open('synthetic')\n", "print('synthetic')\n"):
        if not pure_findings(mutation):
            findings.append("Negative Evaluator-I/O-Kontrolle wurde nicht erkannt")
    if findings:
        print("dgn007-prospective-acceptance: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-prospective-acceptance: PASS (PROJECT_SEMANTIC; reine Policy-/Fixturegrenze, keine Runtime-Abnahme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
