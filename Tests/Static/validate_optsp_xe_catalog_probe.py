"""Static guardrails for the read-only SQL Server 2025 XE metadata probe."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "Tests" / "Runtime" / "optsp_xe_catalog_probe.sql"
WORKFLOW = ROOT / ".github" / "workflows" / "optsp-xe-catalog-probe.yml"


def validate(sql: str, workflow: str) -> list[str]:
    findings: list[str] = []
    if "SERVERPROPERTY('ProductMajorVersion')" not in sql or "IF @ProductMajorVersion IS NULL OR @ProductMajorVersion <> 17" not in sql:
        findings.append("probe must stop unless the engine is SQL Server 2025")
    if "SERVERPROPERTY('ProductVersion')), N'') <> N'17.0.5065.9'" not in sql:
        findings.append("probe must stop unless the exact engine build matches")
    for catalog in ("sys.dm_xe_objects", "sys.dm_xe_object_columns", "sys.dm_xe_packages"):
        if catalog not in sql:
            findings.append(f"probe must read {catalog}")
    wait_event = "package.name = N'sqlos' AND event_object.name = N'wait_info'"
    if wait_event not in sql:
        findings.append("probe must select wait_info from the sqlos package")
    wait_map_markers = (
        "sys.dm_xe_map_values AS wait_map",
        "package.guid = wait_map.object_package_guid",
        "wait_map.name = N'wait_types'",
        "wait_map.map_value = N'LCK_M_X'",
    )
    if any(marker not in sql for marker in wait_map_markers):
        findings.append("probe must bind the LCK_M_X map key through the package GUID")
    field_map_markers = (
        "event_column.object_package_guid = event_object.package_guid",
        "field_map.object_package_guid = event_column.type_package_guid",
        "field_map.name = event_column.type_name",
        "event_package.name = N'sqlserver' AND event_object.name = N'compile_synchronization'",
        "event_column.name IN (N'query_type', N'step')",
        "event_package.name = N'sqlos' AND event_object.name = N'wait_info'",
        "event_column.name = N'opcode'",
        "N'lock_released'",
    )
    if any(marker not in sql for marker in field_map_markers):
        findings.append("probe must bind field maps by event and type packages and inventory both lock edges")
    for marker in ("FOR JSON PATH", "sql_text", "session_id", "database_id", "query_hash", "query_plan_hash"):
        if marker not in sql:
            findings.append(f"probe metadata marker missing: {marker}")

    scrubbed = re.sub(r"--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'", " ", sql, flags=re.DOTALL)
    forbidden = re.search(
        r"\b(?:CREATE|ALTER|DROP|INSERT|UPDATE|DELETE|MERGE|EXEC(?:UTE)?|GRANT|REVOKE|DBCC|BACKUP|RESTORE)\b",
        scrubbed,
        re.IGNORECASE,
    )
    if forbidden:
        findings.append("probe SQL must remain read-only and must not execute dynamic SQL")
    if "optsp_xe_catalog_probe.sql" not in workflow:
        findings.append("runtime workflow must execute the probe SQL")
    if "mcr.microsoft.com/mssql/server@sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9" not in workflow:
        findings.append("runtime workflow must use the digest-pinned SQL Server 2025 container")
    if "cleanup_ci_container.sh" not in workflow or "if: always()" not in workflow:
        findings.append("runtime workflow must always use the ownership-checked container cleanup")
    if "-h -1 -y 8000 -w 8000" not in workflow:
        findings.append("sqlcmd output must suppress headers and retain bounded JSON width")
    if re.search(r"(?:--publish|\s-p\s|--volume|\s-v\s)", workflow):
        findings.append("runtime container must not publish ports or mount host volumes")
    return findings


def main() -> int:
    findings = validate(SQL.read_text(encoding="utf-8"), WORKFLOW.read_text(encoding="utf-8"))
    if findings:
        print(f"optsp-xe-catalog-probe: FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("optsp-xe-catalog-probe: PASS (SQL Server 2025 metadata-only, read-only, owned-container cleanup)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
