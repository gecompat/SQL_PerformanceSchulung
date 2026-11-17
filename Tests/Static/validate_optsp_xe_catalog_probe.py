"""Static guardrails for the read-only SQL Server 2025 XE metadata probe."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "Tests" / "Runtime" / "optsp_xe_catalog_probe.sql"
WORKFLOW = ROOT / ".github" / "workflows" / "optsp-xe-catalog-probe.yml"


def validate(sql: str, workflow: str) -> list[str]:
    findings: list[str] = []
    if "SERVERPROPERTY('ProductMajorVersion')" not in sql or "IF @ProductMajorVersion <> 17" not in sql:
        findings.append("probe must stop unless the engine is SQL Server 2025")
    for catalog in ("sys.dm_xe_objects", "sys.dm_xe_object_columns", "sys.dm_xe_packages"):
        if catalog not in sql:
            findings.append(f"probe must read {catalog}")
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
    if "mcr.microsoft.com/mssql/server:2025-latest" not in workflow:
        findings.append("runtime workflow must use the official SQL Server 2025 container")
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
