"""Static guard for the manual, read-only DGN-007 XE catalog probe."""
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "Tests/Runtime/dgn007_xe_catalog_probe.sql"
RUNNER = ROOT / "Tests/Runtime/dgn007_xe_catalog_probe.py"
WORKFLOW = ROOT / ".github/workflows/dgn007-xe-metadata-probe.yml"
METHOD = ROOT / "Documentation/Project_Planning/DGN_007_XE_WINDOW_ATTRIBUTION_METHOD.md"


def validate() -> list[str]:
    errors: list[str] = []
    sql = SQL.read_text(encoding="utf-8").casefold()
    runner = RUNNER.read_text(encoding="utf-8").casefold()
    workflow = WORKFLOW.read_text(encoding="utf-8").casefold()
    method = re.sub(r"\s+", " ", METHOD.read_text(encoding="utf-8").casefold())

    required_views = ("sys.dm_xe_objects", "sys.dm_xe_object_columns", "sys.dm_xe_packages")
    if any(view not in sql for view in required_views):
        errors.append("probe SQL must read all three XE metadata catalogs")
    if re.search(r"\b(create|alter|drop)\s+event\s+session\b", sql):
        errors.append("probe SQL must not create, alter, or drop an XE session")
    if re.search(r"\b(insert|update|delete|merge|truncate|execute|exec)\b", sql):
        errors.append("probe SQL must remain read-only")
    if any(source in sql for source in (
        "sys.fn_xe_file_target_read_file", "ring_buffer", "sys.dm_exec_input_buffer",
        "sys.dm_exec_query_plan", "sys.dm_exec_sql_text",
    )):
        errors.append("probe SQL must not read event payload, input buffers, plans, or SQL text")
    if "sql_statement_starting" not in sql or "sql_statement_completed" not in sql:
        errors.append("probe SQL must inventory only the selected start/completion event family")
    if "dgn007_xe|engine|" not in sql or "dgn007_xe|event|" not in sql or "dgn007_xe|action|" not in sql:
        errors.append("probe output must have fixed, non-payload metadata records")
    if "dgn007_xe|end|1" not in sql or "dgn007_xe|end|1" not in runner:
        errors.append("probe output must include and require a completion marker")

    if "runtime_authorized" not in runner or '"proposed"' not in runner:
        errors.append("runner must preserve the shared image lock's PROPOSED status")
    if ("validate_image_identity" not in runner
            or 'item.get("architecture") == "amd64"' not in runner
            or 'item.get("os") == "linux"' not in runner):
        errors.append("runner must bind the pinned image reference and Linux/AMD64 platform")
    for marker in ("--internal", "--cpus=2", "--memory=4g", "--restart=no", "--pull=never"):
        if marker not in runner:
            errors.append(f"runner must preserve the bounded owned-container boundary ({marker})")
    if "--network" not in runner or "--internal" not in runner:
        errors.append("container must be attached only to an owned internal network")
    if "--interactive" not in runner or "sqlcmdpassword" not in runner:
        errors.append("runner must send the fixed SQL through the owned container's SQLCMD")
    if "set nocount on; select 1;" not in runner:
        errors.append("SQL readiness probe must suppress row-count output for exact readiness parsing")
    if "event session" in runner and any(word in runner for word in ("create event session", "alter event session")):
        errors.append("runner must not start an XE session")
    if "katalogabfrage und eine xe-session liefen nicht" not in method:
        errors.append("method must keep probe distinct from runtime qualification")

    if "workflow_dispatch" not in workflow:
        errors.append("empirical SQL work must require workflow_dispatch")
    if "pull_request:" not in workflow or "push:" not in workflow:
        errors.append("static probe contracts must run for pull requests and main pushes")
    if "if: ${{ github.event_name == 'workflow_dispatch' }}" not in workflow:
        errors.append("runtime matrix must be conditional on manual dispatch")
    if "max-parallel: 1" not in workflow:
        errors.append("build probes must be serialized")
    if "2025-latest" in workflow or "2019-latest" in workflow or "2022-latest" in workflow:
        errors.append("runtime matrix must use digest-pinned image references from the lock")
    if "retention-days: 3" not in workflow:
        errors.append("metadata inventory artifact retention must be bounded")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("dgn007-xe-catalog-probe: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("dgn007-xe-catalog-probe: PASS (read-only SQL; manual runtime; pinned images; owned cleanup)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
