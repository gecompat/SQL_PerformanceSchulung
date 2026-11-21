"""Bounded read-only Docker runner for DGN-004 plan-cache snapshots."""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "Tests" / "Static"
RUNTIME = ROOT / "Tests" / "Runtime"
SQL_SOURCE = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair" / "SnapshotPlanCandidates.sql"
MODULE_SOURCE_TOKEN = "CONVERT(varbinary(max), N'DGN004_MODULE_SOURCE_TOKEN')"
SQLCMD_SERVER_ADDRESS = "127.0.0.1"
if str(STATIC) not in sys.path:
    sys.path.insert(0, str(STATIC))
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

from dgn004_capture_runner import (  # noqa: E402
    CaptureRunnerError,
    CaptureSqlcmdError,
    _safe_sqlcmd_failure_category,
    collect_bounded_process,
)
from dgn004_identity_snapshot import registered_text_views  # noqa: E402
from dgn004_plan_candidates import (  # noqa: E402
    CandidateSnapshot,
    PlanCandidateInput,
    PlanCandidateError,
    parse_candidate_snapshot,
    validate_snapshot_input,
)
from execution_target import DOCKER, ExecutionTarget  # noqa: E402


class CandidateRunnerError(CaptureRunnerError):
    """Reject candidate enumeration failures without exposing raw diagnostics."""


def build_candidate_command(
    target: ExecutionTarget,
    *,
    database: str,
    inputs: PlanCandidateInput,
) -> tuple[list[str], bytes, dict[str, str]]:
    """Build a bounded direct Docker/sqlcmd invocation with validated literals."""
    validate_snapshot_input(inputs)
    if type(target) is not ExecutionTarget or target.kind != DOCKER:
        raise CandidateRunnerError("plan candidate snapshot requires its disposable Docker target")
    if (target.auth != "sql" or target.username != "sa" or target.server != "localhost"
            or type(target.container) is not str
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", target.container)
            or type(target.sqlcmd_path) is not str or not target.sqlcmd_path):
        raise CandidateRunnerError("invalid DGN-004 Docker target")
    if (type(database) is not str
            or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", database)):
        raise CandidateRunnerError("invalid target database")

    environment = target.child_environment()
    if not environment.get("SQLCMDPASSWORD"):
        raise CandidateRunnerError("SQLCMDPASSWORD is required in the process environment")
    try:
        template = SQL_SOURCE.read_bytes().decode("ascii", errors="strict")
        # SQL Server stores each submitted module batch with one terminal LF.
        module_source = registered_text_views()[inputs.role].module_text + "\n"
        module_source.encode("utf-16le", errors="strict")
    except (OSError, UnicodeError, PlanCandidateError, ValueError) as exc:
        raise CandidateRunnerError("registered DGN-004 source or snapshot SQL is unavailable") from exc
    if template.count(MODULE_SOURCE_TOKEN) != 1:
        raise CandidateRunnerError("snapshot SQL module-source token is not unique")
    if not module_source or len(module_source) > 4000:
        raise CandidateRunnerError("registered DGN-004 module source exceeds Unicode literal bound")
    # The registered source is under SQL Server's 4,000-character Unicode
    # literal limit. Escaping quotes preserves its exact UTF-16LE bytes without
    # relying on binary literal parsing or varchar truncation behavior.
    module_expression = "CONVERT(varbinary(max), N'" + module_source.replace("'", "''") + "')"
    rendered_sql = template.replace(MODULE_SOURCE_TOKEN, module_expression)
    if MODULE_SOURCE_TOKEN in rendered_sql:
        raise CandidateRunnerError("snapshot SQL contains an unresolved module-source token")
    try:
        sql_source = rendered_sql.encode("ascii", errors="strict")
    except UnicodeEncodeError as exc:
        raise CandidateRunnerError("snapshot SQL source is not ASCII") from exc

    variables = {
        "DGN004_RUN": inputs.run,
        "DGN004_ROLE": inputs.role,
        "DGN004_CALL": str(inputs.call),
        "DGN004_DATABASE_ID": str(inputs.database_id),
        "DGN004_OBJECT_ID": str(inputs.object_id),
        "DGN004_STATEMENT_START_OFFSET": str(
            registered_text_views()[inputs.role].statement_start_offset
        ),
    }
    command = [
        shutil.which("docker") or "docker",
        "exec", "-i", "-e", "SQLCMDPASSWORD", target.container,
        target.sqlcmd_path,
        "-S", SQLCMD_SERVER_ADDRESS, "-d", database, "-U", "sa", "-C",
        "-b", "-r", "1", "-t", "15", "-W", "-s", "|", "-h", "-1", "-w", "65535",
        "-v", *(f"{name}={value}" for name, value in sorted(variables.items())),
    ]
    return command, sql_source, environment


def run_candidate_snapshot(
    target: ExecutionTarget,
    *,
    database: str,
    inputs: PlanCandidateInput,
    timeout_seconds: float = 20.0,
) -> CandidateSnapshot:
    """Capture and strictly parse one complete plan-cache candidate snapshot."""
    command, sql_source, environment = build_candidate_command(
        target, database=database, inputs=inputs
    )
    result = collect_bounded_process(
        command,
        input_bytes=sql_source,
        environment=environment,
        timeout_seconds=timeout_seconds,
    )
    if result.returncode != 0:
        category = _safe_sqlcmd_failure_category(result.returncode, result.stdout, result.stderr)
        raise CaptureSqlcmdError(f"sqlcmd ended unsuccessfully during candidate snapshot: {category}")
    if result.stderr:
        category = _safe_sqlcmd_failure_category(result.returncode, result.stdout, result.stderr)
        raise CaptureSqlcmdError(f"sqlcmd wrote diagnostics during candidate snapshot: {category}")
    try:
        frame = result.stdout.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise CaptureSqlcmdError("candidate snapshot output is not ASCII") from exc
    try:
        return parse_candidate_snapshot(frame, expected=inputs)
    except PlanCandidateError as exc:
        raise CandidateRunnerError("candidate snapshot frame is incomplete or misbound") from exc
