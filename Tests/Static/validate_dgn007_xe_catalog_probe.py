"""Static guard for the manual, read-only DGN-007 XE catalog probe."""
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "Tests/Runtime/dgn007_xe_catalog_probe.sql"
PAYLOAD_SQL = ROOT / "Tests/Runtime/dgn007_xe_payload_privacy_probe.sql"
RUNNER = ROOT / "Tests/Runtime/dgn007_xe_catalog_probe.py"
WORKFLOW = ROOT / ".github/workflows/dgn007-xe-metadata-probe.yml"
METHOD = ROOT / "Documentation/Project_Planning/DGN_007_XE_WINDOW_ATTRIBUTION_METHOD.md"


def validate() -> list[str]:
    errors: list[str] = []
    sql = SQL.read_text(encoding="utf-8").casefold()
    payload_sql = re.sub(r"\s+", " ", PAYLOAD_SQL.read_text(encoding="utf-8").casefold())
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
    if "create event session [dgn007_payloadgate]" not in payload_sql:
        errors.append("privacy probe must create only its fixed, disposable XE session")
    if ("add event sqlserver.sql_statement_starting ( set collect_statement = (0)" not in payload_sql
            or "add event sqlserver.sql_statement_completed ( set collect_statement = (0), collect_parameterized_plan_handle = (0)" not in payload_sql):
        errors.append("privacy probe must disable each event's supported statement collection controls")
    if "sqlserver.sql_text" in payload_sql or "sqlserver.tsql_stack" in payload_sql:
        errors.append("privacy probe must not configure SQL-text or stack actions")
    if ("package0.ring_buffer" not in payload_sql
            or "max_memory = 4096 kb" not in payload_sql
            or "max_memory = (1024)" not in payload_sql
            or "allow_single_event_loss" not in payload_sql
            or "startup_state = off" not in payload_sql):
        errors.append("privacy probe target and session must remain bounded and nonpersistent")
    if "dgn007_payload|event|" not in payload_sql or "dgn007_payload|end|1" not in payload_sql:
        errors.append("privacy probe must emit bounded event-summary and completion records")
    if "dgn007_payload|end|1" not in runner or "parse_payload_output" not in runner:
        errors.append("runner must reject incomplete or unsafe payload-gate results")
    if (re.search(r"event_node\.value\([^)]*(?:data|statement)", payload_sql)
            or "select target_data" in payload_sql):
        errors.append("privacy gate must inspect only field presence/text flags, never emit event values")
    if ("sum(convert(int, has_statement))" not in payload_sql
            or "sum(convert(int, has_statement_text))" not in payload_sql):
        errors.append("privacy gate must convert XML presence bits before SQL aggregation")
    if "select @synthetic_marker = convert(int, 7)" not in payload_sql:
        errors.append("privacy probe must use only its fixed synthetic statement")
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
    print("dgn007-xe-catalog-probe: PASS (catalog-only inventory; synthetic privacy gate; manual runtime; pinned images; owned cleanup)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
