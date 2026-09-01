#!/usr/bin/env python3
"""Static contract for the DGN-005 interactive lifecycle."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "Scenarios/DGN-005/scenario.json"
ADAPTER = ROOT / "Scenarios/DGN-005/adapter/adapter.json"
MODULE = ROOT / "Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psm1"
HOWTO = ROOT / "Documentation/HowTo/DGN_005_INTERACTIVE_SCENARIO.md"
ENTRYPOINTS = ("preflight", "install", "validate", "cleanup")


def main() -> int:
    findings: list[str] = []
    for path in (SCENARIO, ADAPTER, MODULE, HOWTO):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    if findings:
        print("labscn005-dgn005: FAIL")
        return 1

    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    if scenario.get("demoId") != "DGN-005" or scenario.get("safetyLevel") != "YELLOW":
        findings.append("scenario identity or safety mismatch")
    if scenario.get("interactive", {}).get("readyState") != "READY_FOR_USER":
        findings.append("scenario does not hand off READY_FOR_USER")
    roles = [item.get("role") for item in scenario["orchestration"]["manual"]["sessionScripts"]]
    if roles != ["DEMONSTRATION", "OBSERVATION", "MITIGATION", "COMPARISON"]:
        findings.append("manual phase order mismatch")

    adapter = json.loads(ADAPTER.read_text(encoding="utf-8"))
    if adapter.get("adapterContractVersion") != "0.1" or adapter.get("supportedSqlVersions") != ["2025"]:
        findings.append("adapter version boundary mismatch")
    if adapter.get("dataClassification") != "SYNTHETIC" or adapter.get("privacyExportPolicy") != "NO_AUTOMATIC_EXPORT":
        findings.append("adapter privacy boundary mismatch")
    for name in ENTRYPOINTS:
        path = ADAPTER.parent / "sql" / f"{name}.sql"
        if not path.is_file():
            findings.append(f"missing adapter entrypoint {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if "$(" in text or ":r " in text.lower() or ":!!" in text.lower():
            findings.append(f"forbidden sqlcmd scripting in {name}")
    install = (ADAPTER.parent / "sql/install.sql").read_text(encoding="utf-8")
    for marker in ("ADAPTER_ISOLATION_REQUIRED", "lab.XeEvidence", "ring_buffer", "MAX_EVENTS_LIMIT=(100)", "MAX_MEMORY=(1024)", "MAX_DURATION=300 SECONDS", "STARTUP_STATE=OFF"):
        if marker not in install:
            findings.append(f"install safety marker missing: {marker}")
    if "event_file" in install.lower():
        findings.append("adapter must not create event_file output")
    cleanup = (ADAPTER.parent / "sql/cleanup.sql").read_text(encoding="utf-8")
    for marker in ("SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId", "SQLPERF.RunToken", "DROP EVENT SESSION", "DROP DATABASE"):
        if marker not in cleanup:
            findings.append(f"cleanup marker missing: {marker}")
    module = MODULE.read_text(encoding="utf-8")
    if "'DGN-005'" not in module or "SQLPERF_LAB_DGN005_LOCAL" not in module:
        findings.append("module does not publish DGN-005")

    if findings:
        print(f"labscn005-dgn005: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn005-dgn005: PASS (YELLOW; bounded in-memory XE; marker-bound cleanup)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
