#!/usr/bin/env python3
"""Prüft den begrenzten DGN-007-Datenmodellvertrag ohne SQL-Server-Ausführung."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident"
AUTO = DEMO / "Automated"
sys.path.insert(0, str(ROOT / "Demos/00_Framework/Tools"))
from run_demo import load_manifest  # noqa: E402


def ownership_findings(sql: str) -> list[str]:
    """Erzwingt NULL-, Case- und Längenschutz vor jedem destruktiven Statement."""
    findings = []
    guard = sql.split("ALTER DATABASE", 1)[0]
    for variable, expected in (("Project", "SQL_PerformanceSchulung"), ("Contract", "1.0"), ("Demo", "DGN-007"), ("Run", "AUTO")):
        for marker in (
            f"@{variable} nvarchar(max)",
            f"@{variable} IS NULL",
            f"@{variable} COLLATE Latin1_General_100_BIN2<>N'{expected}'",
            f"DATALENGTH(@{variable})<>DATALENGTH(N'{expected}')",
        ):
            if marker not in guard:
                findings.append(f"Eigentumsschutz fehlt: {marker}")
    if sql.count("CONVERT(nvarchar(max),value)") != 4:
        findings.append("Markerwerte dürfen nicht gekürzt werden")
    return findings


def main() -> int:
    findings = []
    manifest = load_manifest(AUTO / "setup.manifest.json")
    if (manifest.demo_id, manifest.run_token, manifest.safety_level) != ("DGN-007", "AUTO", "YELLOW"):
        findings.append("Manifest muss getrennten gelben AUTO-Vertrag verwenden")
    if [phase.phase_id for phase in manifest.phases] != ["PREFLIGHT", "SETUP", "DATA_ASSERTION"]:
        findings.append("Setup-Phasenfolge weicht ab")
    if manifest.timeout_seconds != 180 or manifest.cleanup_timeout_seconds != 60 or manifest.cleanup is None:
        findings.append("Zeit- oder Cleanup-Vertrag weicht ab")
    for phase in (*manifest.phases, manifest.cleanup):
        if not phase.required or not phase.require_summary or not phase.timeout_seconds:
            findings.append("Jede Phase benötigt Statusauswertung und Zeitbudget")
    sql = {path.name: path.read_text(encoding="utf-8") for path in AUTO.glob("*.sql")}
    cleanup = sql["90_Cleanup.sql"]
    findings.extend(ownership_findings(cleanup))
    # Negative Kontrollen: eine entfernte Schutzbedingung darf nicht grün bleiben.
    for marker in ("@Project IS NULL", "@Run IS NULL", " COLLATE Latin1_General_100_BIN2", "DATALENGTH(@Contract)<>DATALENGTH(N'1.0')", "CONVERT(nvarchar(max),value)"):
        if not ownership_findings(cleanup.replace(marker, "")):
            findings.append(f"Negative Eigentumskontrolle nicht erkannt: {marker}")
    combined = "\n".join(sql.values())
    for forbidden in (r"(?im)^\s*:r\b", r"(?i)DBCC\s+(?:FREEPROCCACHE|DROPCLEANBUFFERS)", r"(?i)NEWID\s*\(", r"SQLPERF_LAB_DGN007_LOCAL", r"CREATE\s+EVENT\s+SESSION"):
        if re.search(forbidden, combined):
            findings.append(f"Unzulässige Abhängigkeit oder Operation: {forbidden}")
    for filename in ("00_Preflight.sql", "10_Setup.sql", "90_Cleanup.sql"):
        for marker in ("$(ConfirmIsolatedLab)", "$(HighImpactConfirmed)", "SQLPERF_LAB_DGN007_AUTO"):
            if marker not in sql[filename]:
                findings.append(f"Sicherheitsmarker fehlt: {filename}: {marker}")
    setup = sql["10_Setup.sql"]
    for marker in ("WHEN 15 THEN 150 WHEN 16 THEN 160 WHEN 17 THEN 170", "INSERT dbo.CaseItem(ItemId,", "BETWEEN 1 AND 24000", "BETWEEN 1 AND 3", "DGN007_CASE_SEARCH"):
        if marker not in setup:
            findings.append(f"Datenmodellmarker fehlt: {marker}")
    assertion = sql["40_Data_Assertion.sql"]
    for marker in ("<>24000", "<>72000", "EXCEPT SELECT", "(8,3),(1,3),(5,3),(1,1)"):
        if marker not in assertion:
            findings.append(f"Ergebnisinvariante fehlt: {marker}")
    if (DEMO / "manifest.json").exists() or (AUTO / "manifest.json").exists():
        findings.append("Setup-Schnitt darf keine freigegebene Demo vortäuschen")
    adapter = json.loads((ROOT / "Scenarios/DGN-007/adapter/adapter.json").read_text(encoding="utf-8"))
    if adapter["supportedSqlVersions"] != ["2025"]:
        findings.append("Bestehende Adapter-Versionsgrenze wurde verändert")
    readme = (AUTO / "README.md").read_text(encoding="utf-8")
    for marker in ("Runtime noch nicht ausgeführt", "kein freigegebenes", "AUTO", "LOCAL", "FWK-010", "180 Sekunden"):
        if marker not in readme:
            findings.append(f"Status-/Vertragsgrenze fehlt: {marker}")
    if findings:
        print("dgn007-automated-setup: FAIL\n" + "\n".join(findings))
        return 1
    print("dgn007-automated-setup: PASS (PROJECT_SEMANTIC; keine Runtime- oder Capstone-Abnahme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
