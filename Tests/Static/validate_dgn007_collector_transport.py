#!/usr/bin/env python3
"""Prüft die reine Transport-/CI-Grenze; keine SQL- oder Herkunftsattestation."""
from __future__ import annotations

import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "Tests/Contracts/dgn007_collector_transport.py"
WORKFLOW = ROOT / ".github/workflows/dgn007-collector-transport.yml"
TRIGGER_PATHS = {
    "Tests/Contracts/dgn007_collector_transport.py",
    "Tests/Static/test_dgn007_collector_transport.py",
    "Tests/Static/validate_dgn007_collector_transport.py",
    ".github/workflows/dgn007-collector-transport.yml",
    "Tests/Contracts/dgn007_prospective_acceptance.py",
    "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/incident-acceptance.contract.json",
    "Tests/Static/test_dgn007_prospective_acceptance.py",
    "Tests/Static/validate_dgn007_prospective_acceptance.py",
    ".github/workflows/dgn007-prospective-acceptance.yml",
}
COMMANDS = (
    "python Tests/Static/validate_dgn007_collector_transport.py",
    "python Tests/Static/test_dgn007_collector_transport.py",
    "python Tests/Static/validate_dgn007_prospective_acceptance.py",
    "python Tests/Static/test_dgn007_prospective_acceptance.py",
)


def pure_findings(source: str) -> list[str]:
    """Schmale Statikgrenze; zusätzlich prüfen tatsächliche Fixtures die API."""
    tree = ast.parse(source)
    findings = []
    allowed = {"__future__", "dataclasses", "decimal", "fractions", "hashlib", "json", "re", "typing", "Tests.Contracts.dgn007_prospective_acceptance"}
    forbidden = {"open", "print", "input", "eval", "exec", "__import__", "read_text", "read_bytes", "write_text", "write_bytes", "write", "system", "Popen", "run_sql", "run_sqlcmd", "RunRecord", "PhaseResult", "evaluate_version"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if any(name not in allowed for name in names):
                findings.append("Transportdecoder darf keine I/O-/SQL-/Prozessmodule importieren")
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in forbidden:
                findings.append("Transportdecoder darf weder I/O noch künstliche Lifecycle-/Akzeptanzrecords erzeugen")
    return findings


def workflow_findings(source: str) -> list[str]:
    findings = []
    for event in ("pull_request", "push"):
        match = re.search(rf"(?ms)^  {event}:\n(.*?)(?=^  [a-z_]+:|^permissions:|\Z)", source)
        paths = set(re.findall(r"^      - '([^']+)'$", match[1], re.MULTILINE)) if match else set()
        if paths != TRIGGER_PATHS:
            findings.append(f"Transport-{event}-CI benötigt exakt eigene und prospektive Abhängigkeitspfade")
        if event == "push" and (match is None or "branches: [main]" not in match[1]):
            findings.append("Transport-Push-CI muss auf main begrenzt bleiben")
    for marker in ("  workflow_dispatch:", "  contents: read", "    runs-on: ubuntu-latest", "    timeout-minutes: 5",
                   "  group: dgn007-collector-transport-", "  cancel-in-progress: true", *COMMANDS):
        if marker not in source:
            findings.append(f"Reiner Transport-CI-Vertrag fehlt: {marker}")
    if re.search(r"\bdocker\b|\bpodman\b|Tests/Runtime/|SQLCMDPASSWORD|upload-artifact|--show-output|workflow_run:|pull_request_target:", source, re.IGNORECASE):
        findings.append("Transport-Statik-CI darf keine SQL-Runtime, Exporte oder fremden Workflows starten")
    return findings


def main() -> int:
    findings = pure_findings(MODULE.read_text(encoding="utf-8"))
    workflow = WORKFLOW.read_text(encoding="utf-8")
    findings.extend(workflow_findings(workflow))
    for before, after in (("timeout-minutes: 5", "timeout-minutes: 0"),
                          ("cancel-in-progress: true", "cancel-in-progress: false"),
                          ("Tests/Contracts/dgn007_collector_transport.py", "Tests/Runtime/**"),
                          (COMMANDS[-1], "true")):
        if not workflow_findings(workflow.replace(before, after)):
            findings.append("Negative Transport-CI-Kontrolle wurde nicht erkannt")
    for mutation in ("import subprocess", "print('synthetic')", "open('synthetic')", "RunRecord()", "PhaseResult()", "evaluate_version()"):
        if not pure_findings(mutation):
            findings.append("Negative Transport-Scope-Kontrolle wurde nicht erkannt")
    if findings:
        print("dgn007-collector-transport: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-collector-transport: PASS (PROJECT_SEMANTIC; reine Transportgrenze, keine Runtime-Abnahme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
