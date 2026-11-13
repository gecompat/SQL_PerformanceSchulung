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
MODULE_HEX_TOKEN = "__DGN004_EXPECTED_MODULE_UTF16_HEX__"
if str(STATIC) not in sys.path:
    sys.path.insert(0, str(STATIC))
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

from dgn004_capture_runner import (  # noqa: E402
    CaptureRunnerError,
    CaptureSqlcmdError,
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
        module_source = registered_text_views()[inputs.role].module_text
        module_bytes = module_source.encode("utf-16le", errors="strict")
    except (OSError, UnicodeError, PlanCandidateError, ValueError) as exc:
        raise CandidateRunnerError("registered DGN-004 source or snapshot SQL is unavailable") from exc
    if template.count(MODULE_HEX_TOKEN) != 1:
        raise CandidateRunnerError("snapshot SQL module-byte token is not unique")
    rendered_sql = template.replace(MODULE_HEX_TOKEN, module_bytes.hex().upper())
    if MODULE_HEX_TOKEN in rendered_sql:
        raise CandidateRunnerError("snapshot SQL contains an unresolved module-byte token")
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
        "-S", "localhost", "-d", database, "-U", "sa", "-C",
        "-b", "-r", "1", "-t", "15", "-W", "-s", "|", "-h", "-1", "-w", "65535",
        "-v", *(f"{name}={value}" for name, value in sorted(variables.items())),
    ]
    return command, sql_source, environment


def run_candidate_snapshot(
    target: ExecutionTarget,
    *,
    database: str,
    inputs: PlanCandidateInput,
) -> CandidateSnapshot:
    """Capture and strictly parse one complete plan-cache candidate snapshot."""
    command, sql_source, environment = build_candidate_command(
        target, database=database, inputs=inputs
    )
    result = collect_bounded_process(
        command,
        input_bytes=sql_source,
        environment=environment,
    )
    if result.returncode != 0:
        raise CaptureSqlcmdError("sqlcmd ended unsuccessfully during candidate snapshot")
    if result.stderr:
        raise CaptureSqlcmdError("sqlcmd wrote diagnostics during candidate snapshot")
    try:
        frame = result.stdout.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise CaptureSqlcmdError("candidate snapshot output is not ASCII") from exc
    try:
        return parse_candidate_snapshot(frame, expected=inputs)
    except PlanCandidateError as exc:
        raise CandidateRunnerError("candidate snapshot frame is incomplete or misbound") from exc
