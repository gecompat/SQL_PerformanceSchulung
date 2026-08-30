#!/usr/bin/env python3
"""Static contract for the CON-004 interactive lifecycle."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "Tools" / "PerformanceTrainingScenario" / "PerformanceTrainingScenario.psm1"
MANIFEST = ROOT / "Tools" / "PerformanceTrainingScenario" / "PerformanceTrainingScenario.psd1"
SCENARIO = ROOT / "Scenarios" / "CON-004" / "scenario.json"
ADAPTER = ROOT / "Scenarios" / "CON-004" / "adapter" / "adapter.json"
LIFECYCLE_TEST = ROOT / "Tests" / "Lab" / "Invoke-PerformanceTrainingScenarioLifecycleTest.ps1"


def main() -> int:
    findings: list[str] = []
    for path in (MODULE, MANIFEST, SCENARIO, ADAPTER, LIFECYCLE_TEST):
        if not path.is_file():
            findings.append(f"missing {path.relative_to(ROOT)}")
    if findings:
        print("labscn003: FAIL")
        return 1
    text = MODULE.read_text(encoding="utf-8")
    for marker in (
        "Get-PerformanceTrainingScenario", "Start-PerformanceTrainingScenario",
        "Reset-PerformanceTrainingScenario", "Remove-PerformanceTrainingScenario",
        "READY_FOR_USER", "Test-SqlServerLabManifest", "New-SqlServerLab",
        "Get-SqlServerLab", "Remove-SqlServerLab", "Test-SqlServerLabAdapter",
        "Install-SqlServerLabAdapter", "AdapterContractVersion", "SqlcmdVariables",
    ):
        if marker not in text:
            findings.append(f"module marker missing: {marker}")
    for forbidden in ("docker run", "podman run", "Invoke-ScenarioSql", "SQLCMDPASSWORD", "-P',", '"-P"'):
        if forbidden.lower() in text.lower():
            findings.append(f"forbidden provisioning/password path: {forbidden}")
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    if scenario.get("safetyLevel") != "YELLOW" or scenario.get("interactive", {}).get("readyState") != "READY_FOR_USER":
        findings.append("CON-004 safety or ready state mismatch")
    roles = [item["role"] for item in scenario["orchestration"]["manual"]["sessionScripts"]]
    if roles != ["HEAD", "MIDDLE", "LEAF", "OBSERVER"]:
        findings.append("manual four-session order mismatch")
    adapter = json.loads(ADAPTER.read_text(encoding="utf-8"))
    if adapter.get("adapterContractVersion") != "0.1":
        findings.append("CON-004 adapter contract version must be 0.1")
    if adapter.get("supportedSqlVersions") != ["2025"]:
        findings.append("CON-004 adapter must be restricted to SQL Server 2025")
    if set(adapter.get("requiredCapabilities", [])) != {"container-linux", "sqlcmd"}:
        findings.append("CON-004 adapter capability contract mismatch")
    if adapter.get("dataClassification") != "SYNTHETIC" or adapter.get("privacyExportPolicy") != "NO_AUTOMATIC_EXPORT":
        findings.append("CON-004 adapter privacy contract mismatch")
    expected_entrypoints = {
        "preflight": "sql/preflight.sql", "install": "sql/install.sql",
        "validate": "sql/validate.sql", "cleanup": "sql/cleanup.sql",
    }
    if adapter.get("entrypoints") != expected_entrypoints:
        findings.append("CON-004 adapter entrypoint contract mismatch")
    for name, relative_path in expected_entrypoints.items():
        path = ADAPTER.parent / relative_path
        if not path.is_file():
            findings.append(f"missing adapter entrypoint: {relative_path}")
            continue
        sql = path.read_text(encoding="utf-8")
        if "$(" in sql or ":r " in sql.lower() or ":!!" in sql.lower():
            findings.append(f"adapter entrypoint uses forbidden sqlcmd scripting: {relative_path}")
        if name == "cleanup" and not all(marker in sql for marker in ("SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId", "SQLPERF.RunToken", "DROP DATABASE")):
            findings.append("adapter cleanup is not fully marker-bound")
        if name == "install" and "ADAPTER_ISOLATION_REQUIRED" not in sql:
            findings.append("adapter install does not enforce the disposable-instance boundary")
    lifecycle_text = LIFECYCLE_TEST.read_text(encoding="utf-8")
    for marker in ("Start-PerformanceTrainingScenario", "Reset-PerformanceTrainingScenario", "Remove-PerformanceTrainingScenario", "READY_FOR_USER", "REMOVED"):
        if marker not in lifecycle_text:
            findings.append(f"lifecycle smoke marker missing: {marker}")
    if findings:
        print(f"labscn003: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("labscn003: PASS (CON-004 YELLOW; READY_FOR_USER; four manual sessions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
