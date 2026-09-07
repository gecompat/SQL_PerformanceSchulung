#!/usr/bin/env python3
"""Static contract for the CON-006 interactive lifecycle."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "Scenarios/CON-006/scenario.json"
ADAPTER = ROOT / "Scenarios/CON-006/adapter/adapter.json"
MODULE = ROOT / "Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psm1"
MODULE_MANIFEST = ROOT / "Tools/PerformanceTrainingScenario/PerformanceTrainingScenario.psd1"
HOWTO = ROOT / "Documentation/HowTo/CON_006_INTERACTIVE_SCENARIO.md"
REVIEW = ROOT / "Documentation/Project_Planning/LABSCN_005_CON_006_DETAIL_REVIEW.md"
SOURCES = ROOT / "Documentation/Research/SOURCE_REGISTER.md"
LIFECYCLE_TEST = ROOT / "Tests/Lab/Invoke-PerformanceTrainingScenarioLifecycleTest.ps1"
ENTRYPOINTS = ("preflight", "install", "validate", "cleanup")


def main() -> int:
    findings: list[str] = []
    for path in (SCENARIO, ADAPTER, MODULE, MODULE_MANIFEST, HOWTO, REVIEW, SOURCES, LIFECYCLE_TEST):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    if findings:
        print("labscn005-con006: FAIL")
        return 1

    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    if scenario.get("demoId") != "CON-006" or scenario.get("safetyLevel") != "YELLOW":
        findings.append("scenario identity or safety mismatch")
    if scenario.get("status") not in {"IMPLEMENTED", "VALIDATED"}:
        findings.append("scenario status must be IMPLEMENTED or VALIDATED")
    if scenario.get("interactive", {}).get("readyState") != "READY_FOR_USER":
        findings.append("scenario does not hand off READY_FOR_USER")
    if scenario.get("topology", {}).get("sessionModel") != "MULTI_SESSION":
        findings.append("scenario does not preserve the multi-session contract")
    roles = [item.get("role") for item in scenario["orchestration"]["manual"]["sessionScripts"]]
    expected_roles = [
        "ACTOR_A", "ACTOR_B", "OBSERVER", "EVIDENCE",
        "MITIGATION", "ORDERED_A", "ORDERED_B", "VERIFICATION",
    ]
    if roles != expected_roles:
        findings.append("manual deadlock and counterprobe phase order mismatch")
    if scenario.get("orchestration", {}).get("primaryMode") != "MANUAL":
        findings.append("interactive scenario must use MANUAL as primary mode")

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
    for marker in (
        "ADAPTER_ISOLATION_REQUIRED", "lab.DeadlockRows", "lab.Evidence",
        "fwk.SessionSignal", "fwk.USP_Signal", "fwk.USP_WaitForSignal",
        "FAIL_TIMEOUT", "READY_FOR_USER",
    ):
        if marker not in install:
            findings.append(f"install contract marker missing: {marker}")
    for forbidden in ("CREATE EVENT SESSION", "ALTER EVENT SESSION", "event_file"):
        if forbidden.lower() in install.lower():
            findings.append(f"adapter must not manage or export Extended Events: {forbidden}")

    cleanup = (ADAPTER.parent / "sql/cleanup.sql").read_text(encoding="utf-8")
    for marker in (
        "SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId",
        "SQLPERF.RunToken", "SINGLE_USER WITH ROLLBACK IMMEDIATE", "DROP DATABASE",
    ):
        if marker not in cleanup:
            findings.append(f"cleanup marker missing: {marker}")

    module = MODULE.read_text(encoding="utf-8")
    if "'CON-006'" not in module or "SQLPERF_LAB_CON006_LOCAL" not in module:
        findings.append("module does not publish CON-006")
    if "ModuleVersion = '1.2.0'" not in MODULE_MANIFEST.read_text(encoding="utf-8"):
        findings.append("module version was not advanced for CON-006 support")

    lifecycle = LIFECYCLE_TEST.read_text(encoding="utf-8")
    for marker in ("deadlock.json", "ordered.json", "40_Observation.sql", "50_Mitigation.sql", "70_Verification.sql"):
        if marker not in lifecycle:
            findings.append(f"lifecycle smoke marker missing: {marker}")
    source_text = SOURCES.read_text(encoding="utf-8")
    for source_id in ("SRC-066", "SRC-067", "SRC-068"):
        if source_id not in source_text:
            findings.append(f"source registration missing: {source_id}")
    review = REVIEW.read_text(encoding="utf-8")
    if "`APPROVED_FOR_IMPLEMENTATION`" not in review and "`VALIDATED`" not in review:
        findings.append("detail review has no implementation approval")

    if findings:
        print(f"labscn005-con006: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn005-con006: PASS (YELLOW; three-session deadlock; ordered counterprobe; marker-bound cleanup)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
