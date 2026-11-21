"""One-shot, bounded DGN-004 runtime qualification in owned Docker containers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
STATIC = ROOT / "Tests" / "Static"
FIXTURES = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair"
for location in (RUNTIME, STATIC):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from dgn004_candidate_runner import run_candidate_snapshot  # noqa: E402
from dgn004_capture_input import CaptureInput  # noqa: E402
from dgn004_capture_result import DecodedPlanCapture  # noqa: E402
from dgn004_capture_runner import (  # noqa: E402
    CaptureOutputLimitError,
    CaptureProcessEndUnknown,
    CaptureRunnerError,
    CaptureSqlcmdError,
    CaptureTimeoutError,
    collect_bounded_process,
    run_plan_capture,
)
from dgn004_container import (  # noqa: E402
    BUILD_PROFILES,
    BuildProfile,
    ContainerError,
    UncertainContainerStartError,
    OwnedContainer,
    cleanup_owned_container,
    sqlcmd_password,
    start_owned_container,
    wait_until_sql_server_ready,
)
from dgn004_identity_snapshot import registered_text_views  # noqa: E402
from dgn004_plan_candidates import (  # noqa: E402
    PlanCandidateError,
    PlanCandidateInput,
    bind_unique_execution,
)
from dgn004_plan_current import CurrentPlanError, inspect_current_form_a_plan  # noqa: E402
from dgn004_acceptance_contract import (  # noqa: E402
    BuildEvidence,
    CallEvidence,
    Verdict,
    evaluate_build,
    evaluate_matrix,
)
from execution_target import ExecutionTarget  # noqa: E402


TOTAL_BUDGET_SECONDS = 900.0
CHECKPOINT_SECONDS = 600.0
MIN_NEXT_BUILD_SECONDS = 180.0
CLEANUP_BUDGET_SECONDS = 60.0
SQL_TIMEOUT_SECONDS = 15.0
PROCESS_TIMEOUT_SECONDS = 20.0
SQLCMD_SERVER_ADDRESS = "127.0.0.1"
MAX_BATCHES_PER_BUILD = 100
MAX_FLUSHES_PER_BUILD = 9
MAX_POST_FLUSH_OBSERVATIONS = 3
CALL_SEQUENCE = (
    ("R", False), ("R", False), ("R", True),
    ("H", False), ("H", True), ("H", True),
    ("R", True), ("H", False), ("R", False),
)
EXPECTED_SERVER_FRAME = re.compile(
    r"\AENGINE\|([^|]+)\|([^|]+)\|([0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9]+)\Z"
)
_ID_FRAME = re.compile(r"\ADGN004_MODULE\|([1-9][0-9]*|NULL)\|([0-9]+)\|([0-9]+|NULL)\|([0-9A-F]+|NULL)\Z")
_META_FRAME = re.compile(r"\ADGN004_META\|([^|]*)\|([^|]*)\|([^|]*)\Z")
_META_CHUNK = re.compile(r"\ADGN004_META_CHUNK\|([1-9][0-9]*)\|([1-9][0-9]*)\|(.*)\Z")
_RESULT_ROW = re.compile(r"\A[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\|[0-9]+\Z")


class Dgn004RuntimeError(RuntimeError):
    """Fail-closed error. The source message is intentionally not retained."""


class Dgn004UnknownError(Dgn004RuntimeError):
    """The Docker/sqlcmd process or required stream completion is unknown."""


class Dgn004TimeoutError(Dgn004RuntimeError):
    """A bounded SQL or outer process deadline was exceeded."""


def _safe_sqlcmd_diagnostic(returncode: int, stderr: bytes) -> str:
    """Return only a coarse, allowlisted process category; never echo diagnostics."""
    if type(returncode) is not int or type(stderr) is not bytes:
        raise Dgn004RuntimeError("invalid sqlcmd process result")
    diagnostic = stderr.decode("utf-8", errors="replace").casefold()
    categories = (
        (("login timeout expired", "connection timeout", "connect timed out"), "connection-timeout"),
        (("login failed for user", "authentication failed"), "authentication-failed"),
        (("certificate verify failed", "certificate chain", "ssl provider"), "tls-diagnostic"),
        (("command timeout", "query timeout", "request timeout"), "query-timeout-diagnostic"),
        (("error:", "sqlcmd: error:"), "sqlcmd-error-diagnostic"),
    )
    for phrases, category in categories:
        if any(phrase in diagnostic for phrase in phrases):
            return category
    sql_error = re.search(r"\bmsg\s+([0-9]{1,5}),\s*level\s+[0-9]{1,2}\b", diagnostic)
    if sql_error is not None:
        if sql_error.group(1) == "207":
            invalid_column = re.search(r"invalid column name\s+'([A-Za-z_][A-Za-z0-9_]{0,127})'", diagnostic)
            if invalid_column is not None:
                return f"sql-server-error-207-column-{invalid_column.group(1).casefold()}"
        if sql_error.group(1) == "102":
            near = re.search(r"\bnear\s+(?:the keyword\s+)?'([^']{1,64})'", diagnostic)
            if near is not None:
                token = near.group(1).casefold()
                if re.fullmatch(r"[a-z_][a-z0-9_]{0,39}", token):
                    return f"sql-server-error-102-near-{token}"
                return "sql-server-error-102-near-nonidentifier"
        return f"sql-server-error-{sql_error.group(1)}"
    if returncode != 0:
        return f"nonzero-exit-{returncode}"
    if stderr:
        return f"unclassified-stderr-{len(stderr)}-bytes"
    return "success"


@dataclass(frozen=True)
class QueryIdentity:
    database_id: int
    object_id: int
    query_id: int
    query_text_id: int
    context_settings_id: int
    parameterization_type: int
    query_hash: bytes
    query_text_bytes: bytes
    compile_count: int
    last_compile_start_time: str
    engine_start_time: str


@dataclass(frozen=True)
class PlanState:
    plan_id: int
    is_forced: bool
    force_failure_count: int | None
    query_plan_hash: bytes


@dataclass(frozen=True)
class MetaSnapshot:
    queries: tuple[QueryIdentity, ...]
    plans: tuple[PlanState, ...]
    executions: tuple[tuple[int, int], ...]

    def identity(self) -> QueryIdentity:
        if len(self.queries) != 1:
            raise Dgn004RuntimeError("query identity is missing or ambiguous")
        return self.queries[0]

    def plan(self, plan_id: int) -> PlanState:
        matches = [item for item in self.plans if item.plan_id == plan_id]
        if len(matches) != 1:
            raise Dgn004RuntimeError("Query Store plan identity is missing or ambiguous")
        return matches[0]

    def execution_counts(self) -> dict[int, int]:
        return dict(self.executions)


class BuildBudget:
    def __init__(self, deadline: float):
        self.deadline = deadline
        self.batches = 0
        self.flushes = 0
        self.after_flush_observations = 0
        self.checkpoint_reported = False

    def reserve(self, batches: int = 1) -> None:
        if type(batches) is not int or batches < 1:
            raise Dgn004RuntimeError("invalid SQL batch reservation")
        if self.batches + batches > MAX_BATCHES_PER_BUILD:
            raise Dgn004RuntimeError("DGN-004 SQL batch budget exhausted")
        if time.monotonic() >= self.deadline:
            raise Dgn004TimeoutError("DGN-004 runtime budget exhausted")
        self.batches += batches

    def reserve_flush(self) -> None:
        if self.flushes >= MAX_FLUSHES_PER_BUILD:
            raise Dgn004RuntimeError("DGN-004 Query Store flush budget exhausted")
        self.flushes += 1

    def reserve_post_flush_observation(self) -> None:
        if self.after_flush_observations >= MAX_FLUSHES_PER_BUILD * MAX_POST_FLUSH_OBSERVATIONS:
            raise Dgn004RuntimeError("DGN-004 post-flush observation budget exhausted")
        self.after_flush_observations += 1


def _validate_run_token(value: str) -> None:
    if type(value) is not str or not re.fullmatch(r"[A-Z0-9]{12}", value):
        raise Dgn004RuntimeError("invalid generated run token")


def _database_name(run_token: str) -> str:
    _validate_run_token(run_token)
    return f"SQLPERF_LAB_DGN004_{run_token}"


def _sql_batches(source: str) -> int:
    pieces = re.split(r"(?im)^[ \t]*GO[ \t]*(?:--.*)?\r?$", source)
    return sum(bool(piece.strip()) for piece in pieces)


def _sql_command(
    target: ExecutionTarget,
    *,
    database: str,
    source: str,
    budget: BuildBudget,
    timeout_seconds: float = SQL_TIMEOUT_SECONDS,
    stdout_limit: int = 2 * 1024 * 1024,
) -> str:
    if (type(target) is not ExecutionTarget or target.kind != "docker"
            or type(database) is not str
            or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", database)
            or type(source) is not str or not source or "\x00" in source):
        raise Dgn004RuntimeError("invalid SQL invocation")
    count = _sql_batches(source)
    budget.reserve(count)
    env = target.child_environment()
    if not env.get("SQLCMDPASSWORD"):
        raise Dgn004RuntimeError("ephemeral SQL credential is unavailable")
    command = [
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", target.container or "",
        target.sqlcmd_path, "-S", SQLCMD_SERVER_ADDRESS, "-d", database, "-U", "sa", "-C",
        # -W is incompatible with -y, and sqlcmd also forbids -h with -y 0.
        # Use finite widths: Python trims frame whitespace and bounds total
        # output, while 8000 preserves the longest registered query hex text.
        "-b", "-r", "1", "-t", "15", "-s", "|", "-h", "-1", "-w", "65535", "-y", "8000",
    ]
    try:
        result = collect_bounded_process(
            command,
            input_bytes=source.encode("ascii", errors="strict"),
            environment=env,
            timeout_seconds=min(PROCESS_TIMEOUT_SECONDS, timeout_seconds,
                                max(0.1, budget.deadline - time.monotonic())),
            stdout_limit_bytes=stdout_limit,
            stderr_limit_bytes=64 * 1024,
        )
    except CaptureTimeoutError as exc:
        raise Dgn004TimeoutError("bounded SQL process timed out") from exc
    except CaptureProcessEndUnknown as exc:
        raise Dgn004UnknownError("bounded SQL process completion is unknown") from exc
    except (CaptureRunnerError, UnicodeError, OSError) as exc:
        raise Dgn004RuntimeError("bounded SQL process failed") from exc
    # sqlcmd -b gives severity-11+ SQL errors a nonzero exit status. With
    # -r 1, informational/warning diagnostics may be routed to stderr even on
    # a successful exit; stderr bytes alone do not make the SQL batch fail.
    if result.returncode != 0:
        category = _safe_sqlcmd_diagnostic(result.returncode, result.stderr + result.stdout)
        raise Dgn004RuntimeError(f"SQL process result: {category}")
    try:
        return result.stdout.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise Dgn004RuntimeError("SQL output was not ASCII") from exc


def _server_identity(target: ExecutionTarget, budget: BuildBudget) -> tuple[int, int]:
    sql = (
        "SET NOCOUNT ON; SELECT 'ENGINE|' + CONVERT(varchar(20),SERVERPROPERTY('ProductVersion'))"
        " + '|' + CONVERT(varchar(100),SERVERPROPERTY('Edition'))"
        " + '|' + CONVERT(varchar(10),SERVERPROPERTY('EngineEdition'))"
        " + '|' + CONVERT(varchar(10),SERVERPROPERTY('ProductMajorVersion'))"
        " + '|' + CONVERT(varchar(10),(SELECT CASE WHEN host_platform=N'Linux' THEN 1 ELSE 0 END FROM sys.dm_os_host_info))"
        " + '|' + CONVERT(varchar(10),SERVERPROPERTY('IsHadrEnabled'));"
    )
    output = _sql_command(target, database="master", source=sql, budget=budget, timeout_seconds=15)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1:
        raise Dgn004RuntimeError("engine identity is incomplete")
    match = EXPECTED_SERVER_FRAME.fullmatch(lines[0])
    if match is None:
        raise Dgn004RuntimeError("engine identity frame is malformed")
    version, edition, engine_edition, major, linux, _hadr = match.groups()
    profile = next((item for item in BUILD_PROFILES if item.product_version == version), None)
    if (profile is None or edition != profile.edition or int(major) not in (16, 17)
            or linux != "1" or engine_edition != "3"):
        raise Dgn004RuntimeError("owned engine does not match a registered Linux build")
    return int(major), int(profile.compatibility_level)


def _cleanup_is_sufficient(*, database_created: bool, database_cleanup_ok: bool,
                            container_cleanup_ok: bool) -> bool:
    # Before database creation, removal of the private, mount-free container
    # discards any partial server-setting change and is complete cleanup.
    return container_cleanup_ok and (not database_created or database_cleanup_ok)


def _server_config_sql() -> str:
    return (
        "SET NOCOUNT ON; SELECT 'DGN004_SERVER_CONFIG|' + name + '|'"
        " + CONVERT(varchar(20),value) + '|' + CONVERT(varchar(20),value_in_use)"
        " FROM sys.configurations WHERE name IN (N'show advanced options',N'max server memory (MB)')"
        " ORDER BY name;"
    )


def _read_server_config(target: ExecutionTarget, budget: BuildBudget) -> dict[str, tuple[int, int]]:
    output = _sql_command(target, database="master", source=_server_config_sql(), budget=budget)
    result: dict[str, tuple[int, int]] = {}
    for line in (item.strip() for item in output.splitlines() if item.strip()):
        fields = line.split("|")
        if len(fields) != 4 or fields[0] != "DGN004_SERVER_CONFIG" or fields[1] in result:
            raise Dgn004RuntimeError("server configuration baseline is ambiguous")
        if fields[1] not in {"show advanced options", "max server memory (MB)"}:
            raise Dgn004RuntimeError("unexpected server configuration field")
        try:
            result[fields[1]] = (int(fields[2]), int(fields[3]))
        except ValueError as exc:
            raise Dgn004RuntimeError("server configuration value is invalid") from exc
    if set(result) != {"show advanced options", "max server memory (MB)"}:
        raise Dgn004RuntimeError("server configuration baseline is incomplete")
    if any(configured != active for configured, active in result.values()):
        raise Dgn004RuntimeError("server has pending configuration changes outside this run")
    return result


def _set_server_memory(target: ExecutionTarget, budget: BuildBudget, memory: int) -> None:
    if type(memory) is not int or not 128 <= memory <= 2_147_483_647:
        raise Dgn004RuntimeError("invalid server memory configuration")
    sql = (
        "SET NOCOUNT ON; EXEC sys.sp_configure N'show advanced options',1; RECONFIGURE;"
        f" EXEC sys.sp_configure N'max server memory (MB)',{memory}; RECONFIGURE;"
    )
    _sql_command(target, database="master", source=sql, budget=budget)


def _restore_server_config(
    target: ExecutionTarget, budget: BuildBudget, original: dict[str, tuple[int, int]]
) -> None:
    show = original["show advanced options"][1]
    memory = original["max server memory (MB)"][1]
    sql = (
        "SET NOCOUNT ON; EXEC sys.sp_configure N'show advanced options',1; RECONFIGURE;"
        f" EXEC sys.sp_configure N'max server memory (MB)',{memory}; RECONFIGURE;"
        f" EXEC sys.sp_configure N'show advanced options',{show}; RECONFIGURE;"
    )
    _sql_command(target, database="master", source=sql, budget=budget)
    observed = _read_server_config(target, budget)
    if observed["show advanced options"][1] != show or observed["max server memory (MB)"][1] != memory:
        raise Dgn004RuntimeError("owned server configuration restore did not verify")


def _create_database_sql(database: str, compatibility: int) -> str:
    if not re.fullmatch(r"SQLPERF_LAB_DGN004_[A-Z0-9]{12}", database):
        raise Dgn004RuntimeError("invalid DGN-004 database name")
    if compatibility not in (160, 170):
        raise Dgn004RuntimeError("invalid DGN-004 compatibility level")
    qname = f"[{database}]"
    return f"""SET NOCOUNT ON;
IF DB_ID(N'{database}') IS NOT NULL THROW 51030,'DGN-004 database name is already occupied.',1;
DECLARE @CreateSql nvarchar(512)=N'CREATE DATABASE {qname}';
EXEC sys.sp_executesql @CreateSql;
ALTER DATABASE {qname} SET COMPATIBILITY_LEVEL = {compatibility};
DECLARE @LogicalName sysname, @FileSql nvarchar(1000);
DECLARE DGN004_Files CURSOR LOCAL FAST_FORWARD FOR
    SELECT name FROM sys.master_files WHERE database_id=DB_ID(N'{database}');
OPEN DGN004_Files;
FETCH NEXT FROM DGN004_Files INTO @LogicalName;
WHILE @@FETCH_STATUS=0
BEGIN
    SET @FileSql=N'ALTER DATABASE {qname} MODIFY FILE (NAME='+QUOTENAME(@LogicalName,N'''')+N',MAXSIZE=128MB)';
    EXEC sys.sp_executesql @FileSql;
    FETCH NEXT FROM DGN004_Files INTO @LogicalName;
END;
CLOSE DGN004_Files;
DEALLOCATE DGN004_Files;
"""


def _add_markers_sql(database: str, run_token: str) -> str:
    _validate_run_token(run_token)
    expected = {
        "SQLPERF.Project": "SQL_PerformanceSchulung",
        "SQLPERF.ContractVersion": "1.0",
        "SQLPERF.DemoId": "DGN-004",
        "SQLPERF.RunToken": run_token,
    }
    calls = "\n".join(
        "EXEC sys.sp_addextendedproperty @name=N'" + key + "',@value=N'" + value + "';"
        for key, value in expected.items()
    )
    return f"""SET NOCOUNT ON;
IF (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0)<>0
    THROW 51031,'DGN-004 new database is not empty of database markers.',1;
{calls}
"""


def _baseline_sql(database: str) -> str:
    qname = f"[{database}]"
    return f"""SET NOCOUNT ON;
SELECT 'DGN004_BASE|' + (SELECT
    (SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID()) AS compatibility_level,
    (SELECT CONVERT(int,value) FROM sys.database_scoped_configurations WHERE name=N'LAST_QUERY_PLAN_STATS') AS last_query_plan_stats,
    (SELECT CONVERT(int,value) FROM sys.database_scoped_configurations WHERE name=N'OPTIMIZED_PLAN_FORCING') AS optimized_plan_forcing,
    JSON_QUERY((SELECT desired_state_desc,actual_state_desc,max_storage_size_mb,flush_interval_seconds,
        interval_length_minutes,stale_query_threshold_days,size_based_cleanup_mode_desc,
        query_capture_mode_desc,wait_stats_capture_mode_desc
        FROM sys.database_query_store_options FOR JSON PATH,INCLUDE_NULL_VALUES)) AS query_store,
    JSON_QUERY((SELECT file_id,name,type,CASE WHEN max_size=-1 THEN -1 ELSE CONVERT(int,max_size/128) END AS max_size
        FROM sys.database_files ORDER BY file_id FOR JSON PATH)) AS files
    FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
"""


def _configure_database_sql(database: str, compatibility: int) -> str:
    qname = f"[{database}]"
    return f"""SET NOCOUNT ON;
ALTER DATABASE {qname} SET QUERY_STORE = ON;
ALTER DATABASE {qname} SET QUERY_STORE
(
    OPERATION_MODE = READ_WRITE,
    QUERY_CAPTURE_MODE = ALL,
    MAX_STORAGE_SIZE_MB = 64,
    SIZE_BASED_CLEANUP_MODE = AUTO
);
ALTER DATABASE {qname} SET COMPATIBILITY_LEVEL = {compatibility};
USE {qname};
ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON;
IF NOT EXISTS (SELECT 1 FROM sys.database_query_store_options
               WHERE actual_state_desc=N'READ_WRITE' AND desired_state_desc=N'READ_WRITE')
    THROW 51032,'DGN-004 Query Store is not writable.',1;
"""


def _configure_scoped_database_sql() -> str:
    return "SET NOCOUNT ON; ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = ON;"


def _restore_database_sql(database: str, baseline: dict[str, object]) -> str:
    qname = f"[{database}]"
    if type(baseline) is not dict or set(baseline) != {
        "compatibility_level", "last_query_plan_stats", "optimized_plan_forcing", "query_store", "files",
    }:
        raise Dgn004RuntimeError("database option baseline is incomplete")
    compatibility = baseline["compatibility_level"]
    last_stats = baseline["last_query_plan_stats"]
    opt_force = baseline["optimized_plan_forcing"]
    if (type(compatibility) is not int or compatibility not in (150, 160, 170)
            or type(last_stats) is not int or last_stats not in (0, 1)
            or type(opt_force) is not int or opt_force not in (0, 1)):
        raise Dgn004RuntimeError("database option baseline contains an invalid value")
    try:
        qs_rows = baseline["query_store"]
        if type(qs_rows) is not list or len(qs_rows) != 1:
            raise ValueError
        qs = qs_rows[0]
        required = {
            "desired_state_desc", "actual_state_desc", "max_storage_size_mb",
            "flush_interval_seconds", "interval_length_minutes", "stale_query_threshold_days",
            "size_based_cleanup_mode_desc", "query_capture_mode_desc", "wait_stats_capture_mode_desc",
        }
        if type(qs) is not dict or set(qs) != required:
            raise ValueError
        desired = qs["desired_state_desc"]
        if desired not in {"OFF", "READ_WRITE", "READ_ONLY"}:
            raise ValueError
        ints = [qs[k] for k in ("max_storage_size_mb", "flush_interval_seconds", "interval_length_minutes", "stale_query_threshold_days")]
        if any(type(value) is not int or value <= 0 for value in ints):
            raise ValueError
        cleanup = qs["size_based_cleanup_mode_desc"]
        capture = qs["query_capture_mode_desc"]
        wait_stats = qs["wait_stats_capture_mode_desc"]
        if cleanup not in {"AUTO", "MANUAL"} or capture not in {"ALL", "AUTO", "CUSTOM"} or wait_stats not in {"ON", "OFF"}:
            raise ValueError
        files = baseline["files"]
        if type(files) is not list or not files:
            raise ValueError
        for row in files:
            if type(row) is not dict or set(row) != {"file_id", "name", "type", "max_size"}:
                raise ValueError
            if (type(row["file_id"]) is not int or type(row["name"]) is not str
                    or not re.fullmatch(r"[A-Za-z0-9_]{1,128}", row["name"])
                    or type(row["type"]) is not int or type(row["max_size"]) is not int):
                raise ValueError
    except (KeyError, ValueError, TypeError) as exc:
        raise Dgn004RuntimeError("database restore baseline cannot be safely rendered") from exc

    if desired == "OFF":
        query_store_restore = f"ALTER DATABASE {qname} SET QUERY_STORE = OFF;"
    else:
        query_store_restore = f"""ALTER DATABASE {qname} SET QUERY_STORE = ON;
ALTER DATABASE {qname} SET QUERY_STORE
(
    OPERATION_MODE = {desired},
    QUERY_CAPTURE_MODE = {capture},
    MAX_STORAGE_SIZE_MB = {qs['max_storage_size_mb']},
    DATA_FLUSH_INTERVAL_SECONDS = {qs['flush_interval_seconds']},
    INTERVAL_LENGTH_MINUTES = {qs['interval_length_minutes']},
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = {qs['stale_query_threshold_days']}),
    SIZE_BASED_CLEANUP_MODE = {cleanup},
    WAIT_STATS_CAPTURE_MODE = {wait_stats}
);"""
    file_restore = "\n".join(
        (f"ALTER DATABASE {qname} MODIFY FILE (NAME=N'{row['name']}',MAXSIZE=UNLIMITED);"
         if row["max_size"] == -1 else
         f"ALTER DATABASE {qname} MODIFY FILE (NAME=N'{row['name']}',MAXSIZE={row['max_size']}MB);")
        for row in files
    )
    return f"""SET NOCOUNT ON;
ALTER DATABASE SCOPED CONFIGURATION SET LAST_QUERY_PLAN_STATS = {('ON' if last_stats else 'OFF')};
ALTER DATABASE SCOPED CONFIGURATION SET OPTIMIZED_PLAN_FORCING = {('ON' if opt_force else 'OFF')};
{query_store_restore}
ALTER DATABASE {qname} SET COMPATIBILITY_LEVEL={compatibility};
{file_restore}
"""


def _read_json_frame(output: str, prefix: str) -> dict[str, object]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].startswith(prefix):
        raise Dgn004RuntimeError("SQL metadata frame is missing or ambiguous")
    try:
        value = json.loads(lines[0][len(prefix):])
    except (json.JSONDecodeError, UnicodeError) as exc:
        if isinstance(exc, json.JSONDecodeError):
            sample = lines[0][len(prefix):]
            left, right = max(0, exc.pos - 12), min(len(sample), exc.pos + 12)
            shape = "".join(
                char if char in '{}[]:,"' else "_" if char.isspace()
                else "#" if char.isdigit() else "a" if char.isalpha() else "x"
                for char in sample[left:right]
            )
            detail = (f"SQL metadata JSON parse failure at line {exc.lineno}, "
                      f"column {exc.colno}: {exc.msg}; redacted-shape={shape}")
        else:
            detail = "SQL metadata frame is malformed"
        raise Dgn004RuntimeError(detail) from exc
    if type(value) is not dict:
        raise Dgn004RuntimeError("SQL metadata object has the wrong shape")
    return value


def _decode_meta(output: str) -> MetaSnapshot:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if not lines:
        raise Dgn004RuntimeError("Query Store metadata frame is incomplete")
    if lines[0].startswith("DGN004_META_CHUNK|"):
        chunks: list[str] = []
        expected_count: int | None = None
        for line in lines:
            chunk_match = _META_CHUNK.fullmatch(line)
            if chunk_match is None:
                raise Dgn004RuntimeError("Query Store metadata chunk frame is malformed")
            ordinal, count = int(chunk_match.group(1)), int(chunk_match.group(2))
            if expected_count is None:
                expected_count = count
            if (count != expected_count or ordinal != len(chunks) + 1
                    or len(chunk_match.group(3)) > 3000
                    or (ordinal < count and len(chunk_match.group(3)) != 3000)
                    or not chunk_match.group(3)):
                raise Dgn004RuntimeError("Query Store metadata chunk sequence is incomplete")
            chunks.append(chunk_match.group(3))
        if expected_count != len(chunks):
            raise Dgn004RuntimeError("Query Store metadata chunk sequence is incomplete")
        frame = "".join(chunks)
    elif len(lines) == 1:
        frame = lines[0]
    else:
        raise Dgn004RuntimeError("Query Store metadata frame is incomplete")
    match = _META_FRAME.fullmatch(frame)
    if match is None:
        raise Dgn004RuntimeError("Query Store metadata frame is malformed")
    try:
        queries_raw, plans_raw, executions_raw = (json.loads(item) for item in match.groups())
        if type(queries_raw) is not list or type(plans_raw) is not list or type(executions_raw) is not list:
            raise ValueError
        queries = tuple(QueryIdentity(
            database_id=row["database_id"], object_id=row["object_id"], query_id=row["query_id"],
            query_text_id=row["query_text_id"], context_settings_id=row["context_settings_id"],
            parameterization_type=row["parameterization_type"], query_hash=bytes.fromhex(row["query_hash"]),
            query_text_bytes=bytes.fromhex(row["query_text_hex"]), compile_count=row["count_compiles"],
            last_compile_start_time=row["last_compile_start_time"],
            engine_start_time=row["engine_start_time"],
        ) for row in queries_raw)
        plans = tuple(PlanState(
            plan_id=row["plan_id"], is_forced=bool(row["is_forced_plan"]),
            force_failure_count=row["force_failure_count"],
            query_plan_hash=bytes.fromhex(row["query_plan_hash"]),
        ) for row in plans_raw)
        executions = tuple((row["plan_id"], row["execution_count"]) for row in executions_raw)
    except (ValueError, TypeError, KeyError) as exc:
        raise Dgn004RuntimeError("Query Store metadata values are invalid") from exc
    if (any(len(item.query_hash) != 8 or item.parameterization_type != 0 for item in queries)
            or any(len(item.query_plan_hash) != 8
                   or (item.force_failure_count is not None and item.force_failure_count < 0) for item in plans)
            or any(type(plan_id) is not int or plan_id <= 0 or type(count) is not int or count < 0
                   for plan_id, count in executions)):
        raise Dgn004RuntimeError("Query Store metadata violates the registered value bounds")
    return MetaSnapshot(queries, plans, executions)


def _metadata_sql(role: str) -> str:
    schema, module, _ = ("dgn004", "ReplayReference", "") if role == "R" else ("dgn004", "ReplayHintControl", "")
    object_name = f"[{schema}].[{module}]"
    return f"""SET NOCOUNT ON;
DECLARE @ObjectId int=OBJECT_ID(N'{object_name}');
DECLARE @Queries nvarchar(max), @Plans nvarchar(max), @Executions nvarchar(max);
SELECT @Queries=(SELECT DB_ID() AS database_id,q.object_id,q.query_id,q.query_text_id,q.context_settings_id,
    q.query_parameterization_type AS parameterization_type,
    UPPER(CONVERT(varchar(16),q.query_hash,2)) AS query_hash,
    UPPER(CONVERT(varchar(max),CONVERT(varbinary(max),qt.query_sql_text),2)) AS query_text_hex,
    q.count_compiles,CONVERT(varchar(33),q.last_compile_start_time,126) AS last_compile_start_time,
    CONVERT(varchar(33),si.sqlserver_start_time,126) AS engine_start_time
    FROM sys.query_store_query AS q
    INNER JOIN sys.query_store_query_text AS qt ON qt.query_text_id=q.query_text_id
    CROSS JOIN sys.dm_os_sys_info AS si
    WHERE q.object_id=@ObjectId FOR JSON PATH,INCLUDE_NULL_VALUES);
SELECT @Plans=(SELECT p.plan_id,p.is_forced_plan,p.force_failure_count,
    UPPER(CONVERT(varchar(16),p.query_plan_hash,2)) AS query_plan_hash
    FROM sys.query_store_plan AS p
    INNER JOIN sys.query_store_query AS q ON q.query_id=p.query_id
    WHERE q.object_id=@ObjectId FOR JSON PATH,INCLUDE_NULL_VALUES);
SELECT @Executions=(SELECT p.plan_id,SUM(CONVERT(bigint,rs.count_executions)) AS execution_count
    FROM sys.query_store_plan AS p
    INNER JOIN sys.query_store_query AS q ON q.query_id=p.query_id
    INNER JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id=p.plan_id
    WHERE q.object_id=@ObjectId AND rs.execution_type=0
    GROUP BY p.plan_id FOR JSON PATH,INCLUDE_NULL_VALUES);
DECLARE @Frame nvarchar(max) = N'DGN004_META|' + COALESCE(@Queries,N'[]') + N'|'
    + COALESCE(@Plans,N'[]') + N'|' + COALESCE(@Executions,N'[]');
DECLARE @ChunkChars int=3000;
;WITH ChunkNumbers AS
(
    SELECT CONVERT(int,1) AS Ordinal
    UNION ALL
    SELECT Ordinal+1 FROM ChunkNumbers WHERE Ordinal*@ChunkChars < LEN(@Frame)
)
SELECT CONVERT(varchar(max),'DGN004_META_CHUNK|')
    + CONVERT(varchar(10),Ordinal) + '|'
    + CONVERT(varchar(10),(LEN(@Frame)+@ChunkChars-1)/@ChunkChars) + '|'
    + CONVERT(varchar(3000),SUBSTRING(@Frame,((Ordinal-1)*@ChunkChars)+1,@ChunkChars))
FROM ChunkNumbers ORDER BY Ordinal OPTION (MAXRECURSION 0);
"""


def _module_probe_sql(role: str) -> str:
    views = registered_text_views()[role]
    module_literal = f"[{views.module_name[0]}].[{views.module_name[1]}]"
    return f"""SET NOCOUNT ON;
DECLARE @ObjectId int=OBJECT_ID(N'{module_literal}');
DECLARE @Definition nvarchar(max)=(SELECT definition FROM sys.sql_modules WHERE object_id=@ObjectId);
SELECT 'DGN004_MODULE|' + COALESCE(CONVERT(varchar(20),@ObjectId),'NULL') + '|'
    + CONVERT(varchar(20),(SELECT COUNT(*) FROM sys.sql_modules WHERE object_id=@ObjectId)) + '|'
    + COALESCE(CONVERT(varchar(20),DATALENGTH(@Definition)),'NULL') + '|'
    + COALESCE(UPPER(CONVERT(varchar(max),CONVERT(varbinary(max),@Definition),2)),'NULL');
"""


def _module_definition_matches(actual: str, expected: str) -> bool:
    # SQL Server stores the submitted module batch with one terminal LF.
    return actual == expected or actual == expected + "\n"


def _assert_sources_and_overrides(
    target: ExecutionTarget,
    *,
    database: str,
    role: str,
    run_token: str,
    budget: BuildBudget,
) -> tuple[int, int]:
    views = registered_text_views()[role]
    control_sql = """SET NOCOUNT ON;
SELECT 'DGN004_CONTROLS|' + CONVERT(varchar(10),
    (SELECT COUNT(*) FROM sys.plan_guides)) + '|'
    + CONVERT(varchar(10),(SELECT COUNT(*) FROM sys.query_store_query_hints)) + '|'
    + CONVERT(varchar(10),(SELECT COUNT(*) FROM sys.extended_properties
        WHERE class=0 AND major_id=0 AND minor_id=0));
"""
    output = _sql_command(
        target, database=database,
        source=_module_probe_sql(role) + "\n" + control_sql,
        budget=budget, stdout_limit=64 * 1024,
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 2:
        raise Dgn004RuntimeError("module source observation is incomplete")
    match = _ID_FRAME.fullmatch(lines[0])
    if match is None:
        frame = lines[0]
        prefix = "DGN004_MODULE|"
        payload = frame[len(prefix):] if frame.startswith(prefix) else ""
        raise Dgn004RuntimeError(
            "module source observation is malformed "
            f"(characters={len(frame)}, prefix={frame.startswith(prefix)}, "
            f"pipes={frame.count('|')}, hex_payload={bool(payload) and re.fullmatch(r'[0-9A-F]+', payload) is not None})"
        )
    if match.group(1) == "NULL":
        raise Dgn004RuntimeError("module object identity is missing")
    if match.group(2) != "1" or match.group(3) == "NULL" or match.group(4) == "NULL":
        raise Dgn004RuntimeError(
            f"module definition unavailable (catalog_rows={match.group(2)}, bytes={match.group(3)})"
        )
    try:
        actual_module = bytes.fromhex(match.group(4)).decode("utf-16le", errors="strict")
    except (ValueError, UnicodeError) as exc:
        raise Dgn004RuntimeError("module source bytes are invalid") from exc
    if not _module_definition_matches(actual_module, views.module_text):
        mismatch = next((index for index, pair in enumerate(zip(actual_module, views.module_text))
                         if pair[0] != pair[1]), min(len(actual_module), len(views.module_text)))
        actual_codepoint = ord(actual_module[mismatch]) if mismatch < len(actual_module) else None
        expected_codepoint = ord(views.module_text[mismatch]) if mismatch < len(views.module_text) else None
        raise Dgn004RuntimeError(
            "module definition differs from its registered source "
            f"(actual_chars={len(actual_module)}, expected_chars={len(views.module_text)}, "
            f"first_difference={mismatch}, actual_codepoint={actual_codepoint}, "
            f"expected_codepoint={expected_codepoint})"
        )

    # A newly created, owned database must contain no alternate plan controls.
    fields = lines[1].split("|")
    if (len(fields) != 4 or fields[0] != "DGN004_CONTROLS"
            or tuple(int(value) for value in fields[1:]) != (0, 0, 4)):
        raise Dgn004RuntimeError("owned database has an unexpected plan override or ownership state")
    expected_db = _database_name(run_token)
    if target.server != "localhost" or target.container is None or database != expected_db:
        raise Dgn004RuntimeError("SQL target is not the uniquely owned DGN-004 database")
    return 1, 1


def _engine_preflight(target: ExecutionTarget, profile: BuildProfile, budget: BuildBudget) -> None:
    sql = (
        "SET NOCOUNT ON; SELECT 'ENGINE|' + CONVERT(varchar(20),SERVERPROPERTY('ProductVersion'))"
        " + '|' + CONVERT(varchar(100),SERVERPROPERTY('Edition'))"
        " + '|' + CONVERT(varchar(10),SERVERPROPERTY('EngineEdition'))"
        " + '|' + CONVERT(varchar(10),SERVERPROPERTY('ProductMajorVersion'))"
        " + '|' + CONVERT(varchar(10),(SELECT CASE WHEN host_platform=N'Linux' THEN 1 ELSE 0 END FROM sys.dm_os_host_info))"
        " + '|' + CONVERT(varchar(10),SERVERPROPERTY('IsHadrEnabled'));"
    )
    output = _sql_command(target, database="master", source=sql, budget=budget)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1:
        raise Dgn004RuntimeError("engine identity is incomplete")
    match = EXPECTED_SERVER_FRAME.fullmatch(lines[0])
    if match is None:
        raise Dgn004RuntimeError("engine identity frame is malformed")
    version, edition, engine_edition, major, linux, hadr = match.groups()
    mismatches = _engine_mismatch_fields(
        (version, edition, engine_edition, major, linux, hadr), profile
    )
    if mismatches:
        raise Dgn004RuntimeError(
            "engine profile mismatch: " + ",".join(mismatches)
        )


def _engine_mismatch_fields(
    fields: tuple[str, str, str, str, str, str], profile: BuildProfile
) -> tuple[str, ...]:
    version, edition, engine_edition, major, linux, hadr = fields
    expected_major = profile.product_version.split(".", 1)[0]
    expected = (
        (version == profile.product_version, "product-version"),
        (edition == profile.edition, "edition"),
        (engine_edition == "3", "engine-edition"),
        (major == expected_major, "product-major-version"),
        (linux == "1", "host-platform"),
        (hadr == "0", "hadr-enabled"),
    )
    return tuple(label for matches, label in expected if not matches)


def _json_baseline(output: str) -> dict[str, object]:
    obj = _read_json_frame(output, "DGN004_BASE|")
    if set(obj) != {"compatibility_level", "last_query_plan_stats", "optimized_plan_forcing", "query_store", "files"}:
        raise Dgn004RuntimeError("database option baseline is incomplete")
    return obj


def _query_store_enabled(target: ExecutionTarget, database: str, budget: BuildBudget) -> bool:
    sql = "SET NOCOUNT ON; SELECT 'DGN004_QS|' + actual_state_desc + '|' + desired_state_desc FROM sys.database_query_store_options;"
    output = _sql_command(target, database=database, source=sql, budget=budget)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1:
        raise Dgn004RuntimeError("Query Store state observation is incomplete")
    fields = lines[0].split("|")
    if len(fields) != 3 or fields[0] != "DGN004_QS" or fields[1] != "READ_WRITE" or fields[2] != "READ_WRITE":
        raise Dgn004RuntimeError("Query Store is not writable in the owned database")
    return True


def _setup_sql_source() -> str:
    setup = (FIXTURES / "SetupSchemaAndData.sql").read_bytes().decode("ascii", errors="strict")
    source_views = registered_text_views()
    if "\r" in setup or not setup.endswith("\n"):
        raise Dgn004RuntimeError("DGN-004 setup SQL has an unsupported line ending")
    source = setup + "GO\n"
    for role in ("R", "H"):
        source += source_views[role].module_text + "\nGO\n"
    return source


def _validate_setup_output(output: str, profile: BuildProfile) -> None:
    rows = [line.strip() for line in output.splitlines() if line.strip()]
    frames = [line for line in rows if line.count("|") == 5]
    if len(frames) != 1:
        raise Dgn004RuntimeError("fixture setup summary is missing or ambiguous")
    parts = frames[0].split("|")
    if (parts[0] != profile.product_version or parts[1] != profile.edition
            or int(parts[2]) != profile.compatibility_level
            or int(parts[3]) != 529 or int(parts[4]) != 10 or int(parts[5]) != 9):
        raise Dgn004RuntimeError("fixture setup shape or engine identity differs")


def _call_sql(role: str, call_number: int) -> str:
    module = "ReplayReference" if role == "R" else "ReplayHintControl"
    context = """SET NOCOUNT ON;
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
SET LANGUAGE us_english;
SET DATEFORMAT mdy;
SET DATEFIRST 7;
IF @@LANGUAGE<>N'us_english' OR @@DATEFIRST<>7
   OR SESSIONPROPERTY('ANSI_NULLS')<>1 OR SESSIONPROPERTY('ANSI_PADDING')<>1
   OR SESSIONPROPERTY('ANSI_WARNINGS')<>1 OR SESSIONPROPERTY('ARITHABORT')<>1
   OR SESSIONPROPERTY('CONCAT_NULL_YIELDS_NULL')<>1 OR SESSIONPROPERTY('QUOTED_IDENTIFIER')<>1
   OR SESSIONPROPERTY('NUMERIC_ROUNDABORT')<>0
   OR CONVERT(char(8),CONVERT(date,'01/02/2024'),112)<>'20240102'
    THROW 51060,'DGN-004 call context differs from its registered session contract.',1;
"""
    return context + f"""SELECT 'DGN004_EXEC_START|{role}|{call_number}|' + CONVERT(varchar(10),@@SPID);
EXEC [dgn004].[{module}];
SELECT 'DGN004_EXEC_END|{role}|{call_number}|' + CONVERT(varchar(10),@@SPID);
"""


def _parse_call_output(output: str, role: str, call_number: int) -> tuple[tuple[int, ...], ...]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    start = f"DGN004_EXEC_START|{role}|{call_number}|"
    end = f"DGN004_EXEC_END|{role}|{call_number}|"
    if len(lines) != 770 or not lines[0].startswith(start) or not lines[-1].startswith(end):
        raise Dgn004RuntimeError("actual call frame is incomplete or has extra output")
    if (not lines[0][len(start):].isdigit() or not lines[-1][len(end):].isdigit()
            or lines[0][len(start):] != lines[-1][len(end):]):
        raise Dgn004RuntimeError("actual call session identity changed inside the phase")
    rows: list[tuple[int, ...]] = []
    for line in lines[1:-1]:
        # sqlcmd right-aligns integer result columns. Normalize only the
        # whitespace around each delimiter before enforcing the numeric frame.
        fields = [field.strip() for field in line.split("|")]
        normalized = "|".join(fields)
        if not _RESULT_ROW.fullmatch(normalized):
            raise Dgn004RuntimeError("actual result contains a malformed or non-tuple row")
        rows.append(tuple(int(value) for value in fields))
    if len(rows) != 768:
        raise Dgn004RuntimeError("actual call returned an unexpected tuple count")
    return tuple(rows)


def _force_sql(query_id: int, plan_id: int) -> str:
    if type(query_id) is not int or query_id <= 0 or type(plan_id) is not int or plan_id <= 0:
        raise Dgn004RuntimeError("invalid own Query Store target")
    return f"""SET NOCOUNT ON;
DECLARE @ReturnCode int;
EXEC @ReturnCode=sys.sp_query_store_force_plan @query_id={query_id},@plan_id={plan_id};
DECLARE @Forced bit;
SELECT @Forced=is_forced_plan FROM sys.query_store_plan WHERE query_id={query_id} AND plan_id={plan_id};
IF @ReturnCode<>0 OR @Forced<>1 THROW 51040,'DGN-004 standard Force request failed.',1;
SELECT 'DGN004_FORCE|{query_id}|{plan_id}|' + CONVERT(varchar(10),@ReturnCode) + '|' + CONVERT(varchar(1),@Forced);
"""


def _unforce_sql(query_id: int, plan_id: int, role: str, call_number: int) -> str:
    if type(query_id) is not int or query_id <= 0 or type(plan_id) is not int or plan_id <= 0:
        raise Dgn004RuntimeError("invalid own Query Store target")
    return f"""SET NOCOUNT ON;
DECLARE @ReturnCode int;
EXEC @ReturnCode=sys.sp_query_store_unforce_plan @query_id={query_id},@plan_id={plan_id};
DECLARE @Forced bit;
SELECT @Forced=is_forced_plan FROM sys.query_store_plan WHERE query_id={query_id} AND plan_id={plan_id};
IF @ReturnCode<>0 OR COALESCE(@Forced,0)<>0 THROW 51041,'DGN-004 explicit Unforce failed.',1;
SELECT 'DGN004_UNFORCE|{role}|{call_number}|{query_id}|{plan_id}|'
    + CONVERT(varchar(10),@ReturnCode) + '|' + CONVERT(varchar(1),COALESCE(@Forced,0));
"""


def _flush_sql() -> str:
    return "SET NOCOUNT ON; EXEC sys.sp_query_store_flush_db; SELECT 'DGN004_FLUSH|PASS';"


def _recompile_sql(role: str) -> str:
    module = "ReplayReference" if role == "R" else "ReplayHintControl"
    return f"SET NOCOUNT ON; EXEC sys.sp_recompile N'[dgn004].[{module}]'; SELECT 'DGN004_RECOMPILE|{role}|PASS';"


def _assert_exact_frame(output: str, expected: str) -> None:
    if [line.strip() for line in output.splitlines() if line.strip()] != [expected]:
        raise Dgn004RuntimeError("server control response differs from its exact expected frame")


def _metadata_after_control(lines: list[str], expected_control: str, label: str) -> MetaSnapshot:
    if len(lines) < 2 or lines[0] != expected_control:
        raise Dgn004RuntimeError(f"{label} response or immediate Query Store baseline is incomplete")
    return _decode_meta("\n".join(lines[1:]))


def _snapshot(
    target: ExecutionTarget, database: str, role: str, budget: BuildBudget, *, post_flush: bool = False
) -> MetaSnapshot:
    if post_flush:
        budget.reserve_post_flush_observation()
    return _decode_meta(_sql_command(
        target, database=database, source=_metadata_sql(role), budget=budget, stdout_limit=256 * 1024
    ))


def _flush_snapshot(target: ExecutionTarget, database: str, role: str,
                    budget: BuildBudget) -> MetaSnapshot:
    budget.reserve_flush()
    budget.reserve_post_flush_observation()
    output = _sql_command(
        target, database=database,
        source=_flush_sql() + "\n" + _metadata_sql(role),
        budget=budget, stdout_limit=256 * 1024,
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) < 2 or lines[0] != "DGN004_FLUSH|PASS":
        raise Dgn004RuntimeError("Query Store flush and immediate state observation are incomplete")
    return _decode_meta("\n".join(lines[1:]))


def _read_force_state(target: ExecutionTarget, database: str, query_id: int, plan_id: int,
                      role: str, call_number: int, budget: BuildBudget) -> bool:
    sql = f"""SET NOCOUNT ON;
SELECT 'DGN004_UNFORCE_STATE|{role}|{call_number}|' + CONVERT(varchar(20),query_id) + '|'
    + CONVERT(varchar(20),plan_id) + '|' + CONVERT(varchar(1),is_forced_plan)
FROM sys.query_store_plan WHERE query_id={query_id} AND plan_id={plan_id};
"""
    output = _sql_command(target, database=database, source=sql, budget=budget)
    fields = [line.strip().split("|") for line in output.splitlines() if line.strip()]
    if len(fields) != 1 or len(fields[0]) != 6:
        raise Dgn004RuntimeError("post-Unforce state is missing or ambiguous")
    row = fields[0]
    if row[:5] != ["DGN004_UNFORCE_STATE", role, str(call_number), str(query_id), str(plan_id)]:
        raise Dgn004RuntimeError("post-Unforce state is misbound")
    if row[5] not in {"0", "1"}:
        raise Dgn004RuntimeError("post-Unforce state value is invalid")
    return row[5] == "0"


def _identity_matches(identity: QueryIdentity, *, dbid: int, object_id: int,
                      expected: QueryIdentity | None, role: str) -> bool:
    views = registered_text_views()[role]
    text = identity.query_text_bytes.decode("utf-16le", errors="strict")
    allowed = {
        views.statement_text.encode("utf-16le"),
        views.statement_without_terminator.encode("utf-16le"),
    }
    if (identity.database_id != dbid or identity.object_id != object_id
            or identity.query_text_bytes not in allowed or identity.query_id <= 0
            or identity.query_text_id <= 0 or identity.context_settings_id < 0
            or identity.parameterization_type != 0 or len(identity.query_hash) != 8
            or identity.compile_count <= 0 or not identity.last_compile_start_time
            or not identity.engine_start_time):
        return False
    if expected is not None and (
        identity.database_id, identity.object_id, identity.query_id, identity.query_text_id,
        identity.context_settings_id, identity.parameterization_type, identity.query_text_bytes
    ) != (
        expected.database_id, expected.object_id, expected.query_id, expected.query_text_id,
        expected.context_settings_id, expected.parameterization_type, expected.query_text_bytes
    ):
        return False
    if expected is not None and identity.engine_start_time != expected.engine_start_time:
        return False
    return bool(text)


def _get_object_id(target: ExecutionTarget, database: str, role: str, budget: BuildBudget) -> int:
    module = "ReplayReference" if role == "R" else "ReplayHintControl"
    sql = f"SET NOCOUNT ON; SELECT 'DGN004_OBJECT|' + CONVERT(varchar(20),OBJECT_ID(N'[dgn004].[{module}]'));"
    output = _sql_command(target, database=database, source=sql, budget=budget)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1 or not re.fullmatch(r"DGN004_OBJECT\|[1-9][0-9]*", lines[0]):
        raise Dgn004RuntimeError("own object identity is missing")
    return int(lines[0].split("|")[1])


def _execution_delta(before: MetaSnapshot | None, after: MetaSnapshot) -> tuple[int, int]:
    counts_after = after.execution_counts()
    counts_before = {} if before is None else before.execution_counts()
    delta = {plan_id: counts_after.get(plan_id, 0) - counts_before.get(plan_id, 0)
             for plan_id in set(counts_after) | set(counts_before)}
    changed = [(plan_id, value) for plan_id, value in delta.items() if value != 0]
    if len(changed) != 1 or changed[0][1] != 1:
        raise Dgn004RuntimeError("exactly one current regular Query Store plan execution was not observed")
    return changed[0]


def _run_call(
    owned: OwnedContainer,
    database: str,
    database_id: int,
    role: str,
    call_number: int,
    forced: bool,
    role_identity: QueryIdentity | None,
    object_id: int,
    target_plan_id: int | None,
    budget: BuildBudget,
) -> tuple[CallEvidence, QueryIdentity, int]:
    target = owned.target
    if role_identity is None:
        _assert_sources_and_overrides(
            target, database=database, role=role, run_token=owned.run_token, budget=budget
        )
    role_state = None if forced else _snapshot(target, database, role, budget)
    if role_identity is not None and role_state is not None:
        observed = role_state.identity()
        if not _identity_matches(observed, dbid=database_id, object_id=object_id,
                                 expected=role_identity, role=role):
            raise Dgn004RuntimeError("query identity drifted before the call")
    elif role_state is not None and (role_state.queries or role_state.plans or role_state.executions):
        raise Dgn004RuntimeError("first role call unexpectedly has Query Store history")

    force_accepted: bool | None = None
    is_forced_after: bool | None = None
    force_failure_after_request: int | None = None
    force_epoch: str | None = None
    if forced:
        if role_identity is None or target_plan_id is None:
            raise Dgn004RuntimeError("forced phase lacks its own pre-bound target")
        force_output = _sql_command(
            target, database=database,
            source=_force_sql(role_identity.query_id, target_plan_id) + "\n" + _metadata_sql(role),
            budget=budget, stdout_limit=256 * 1024,
        )
        force_lines = [line.strip() for line in force_output.splitlines() if line.strip()]
        force_control = f"DGN004_FORCE|{role_identity.query_id}|{target_plan_id}|0|1"
        b0 = _metadata_after_control(force_lines, force_control, "Force")
        force_accepted, is_forced_after = True, True
        identity_b0 = b0.identity()
        if not _identity_matches(identity_b0, dbid=database_id, object_id=object_id,
                                 expected=role_identity, role=role):
            raise Dgn004RuntimeError("query identity changed at forced B0")
        target_state = b0.plan(target_plan_id)
        if not target_state.is_forced or target_state.force_failure_count != 0:
            raise Dgn004RuntimeError("Force request did not open a zero-count failure epoch")
        force_failure_after_request = target_state.force_failure_count
        force_epoch = hashlib.sha256(
            f"{owned.run_token}|{role}|{call_number}|{identity_b0.query_id}|{target_plan_id}".encode("ascii")
        ).hexdigest()
    else:
        b0 = role_state if role_identity is not None else None

    if call_number > 1:
        recompile_output = _sql_command(
            target, database=database, source=_recompile_sql(role), budget=budget
        )
        _assert_exact_frame(recompile_output, f"DGN004_RECOMPILE|{role}|PASS")

    # The plan-cache before-snapshot follows the own recompile marker so the
    # complete delta binds one subsequent user execution.
    identity_for_cache = role_identity or (b0.identity() if b0 is not None else None)
    cache_object_id = object_id
    budget.reserve(1)
    before_cache = run_candidate_snapshot(
        target, database=database,
        inputs=PlanCandidateInput(owned.run_token, role, call_number, database_id, cache_object_id),
        timeout_seconds=min(PROCESS_TIMEOUT_SECONDS, max(0.1, budget.deadline-time.monotonic())),
    )
    call_output = _sql_command(
        target, database=database, source=_call_sql(role, call_number), budget=budget
    )
    rows = _parse_call_output(call_output, role, call_number)
    budget.reserve(1)
    after_cache = run_candidate_snapshot(
        target, database=database,
        inputs=PlanCandidateInput(owned.run_token, role, call_number, database_id, cache_object_id),
        timeout_seconds=min(PROCESS_TIMEOUT_SECONDS, max(0.1, budget.deadline-time.monotonic())),
    )
    try:
        bound_handle = bind_unique_execution(before_cache, after_cache)
    except PlanCandidateError as exc:
        raise Dgn004RuntimeError("current call did not bind to one complete cache candidate") from exc
    budget.reserve(1)
    capture = run_plan_capture(
        target, database=database,
        inputs=CaptureInput(owned.run_token, role, call_number, bound_handle.plan_handle_hex),
        timeout_seconds=min(PROCESS_TIMEOUT_SECONDS, max(0.1, budget.deadline-time.monotonic())),
    )
    try:
        plan_summary = inspect_current_form_a_plan(
            capture.xml_text, role=role, database_name=database, expected_use_plan=forced
        )
    except CurrentPlanError as exc:
        # CurrentPlanError messages are fixed allowlisted categories and carry
        # no SQL text, handles, or database contents.
        raise Dgn004RuntimeError(
            f"captured actual plan is not the current registered Form-A plan: {exc}"
        ) from exc

    b1 = _flush_snapshot(target, database, role, budget)
    identity_b1 = b1.identity()
    if not _identity_matches(identity_b1, dbid=database_id, object_id=object_id,
                             expected=role_identity, role=role):
        raise Dgn004RuntimeError("query identity is missing or changed after the call")
    if role_identity is not None and identity_for_cache != role_identity:
        raise Dgn004RuntimeError("role identity was rebound during the call")
    actual_plan_id, actual_execution_delta = _execution_delta(b0, b1)
    if actual_execution_delta != 1:
        raise Dgn004RuntimeError("Query Store did not attribute exactly one plan execution")
    if target_plan_id is None:
        target_plan_id = actual_plan_id
    if actual_plan_id != target_plan_id:
        raise Dgn004RuntimeError("actual Query Store plan differs from the role target plan")
    actual_plan_state = b1.plan(actual_plan_id)
    if actual_plan_state.query_plan_hash != bound_handle.candidate.query_plan_hash:
        # Hashes supplement the full object/query/plan binding and are retained
        # raw. A known version-specific hash override is not a sole identity test.
        hash_matches = False
    else:
        hash_matches = True
    # Keep the raw Query Store and cache plan hashes in the evidence. Their
    # equality is not a prerequisite because the registered 2022 caveat permits
    # a hash override; the plan_id/runtime-stat mapping is the primary binding.
    _ = hash_matches

    compile_before = None if b0 is None else b0.identity().compile_count
    compile_after = identity_b1.compile_count
    compile_epoch_before = None if compile_before is None else (
        f"{identity_b1.engine_start_time}:{identity_b1.database_id}:{identity_b1.query_id}:"
        f"{identity_b1.context_settings_id}"
    )
    compile_epoch_after = compile_epoch_before
    compile_required = call_number in (2, 3, 5, 6, 7, 8, 9)
    compile_delta = (
        compile_before is not None and compile_after - compile_before > 0
    ) if compile_required else True
    if compile_required and not compile_delta:
        raise Dgn004RuntimeError("fresh Query Store compilation was not observed")
    if call_number in (2, 3, 5, 6, 7) and compile_after - (compile_before or 0) != 1:
        raise Dgn004RuntimeError("strict Query Store compilation delta is not exactly one")
    if forced:
        failure_after = b1.plan(target_plan_id).force_failure_count
        if failure_after != force_failure_after_request:
            raise Dgn004RuntimeError("a new Query Store force failure occurred during execution")
    else:
        failure_after = None

    unforce_confirmed: bool | None = None
    final_is_forced: bool
    if forced:
        assert role_identity is not None
        unforce_output = _sql_command(
            target, database=database,
            source=_unforce_sql(role_identity.query_id, target_plan_id, role, call_number)
                + "\n" + _metadata_sql(role),
            budget=budget, stdout_limit=256 * 1024,
        )
        unforce_lines = [line.strip() for line in unforce_output.splitlines() if line.strip()]
        expected_unforce = f"DGN004_UNFORCE|{role}|{call_number}|{role_identity.query_id}|{target_plan_id}|0|0"
        after_unforce = _metadata_after_control(unforce_lines, expected_unforce, "Unforce")
        budget.reserve_post_flush_observation()
        unforce_confirmed = not after_unforce.plan(target_plan_id).is_forced
        final_is_forced = not unforce_confirmed
    else:
        final_is_forced = any(item.is_forced for item in b1.plans)
        if final_is_forced:
            raise Dgn004RuntimeError("unforced phase observed a forced role plan")

    views = registered_text_views()[role]
    hint_state = "FIXED_TERMINAL" if role == "H" else "ABSENT"
    evidence = CallEvidence(
        role=role,
        call_number=call_number,
        database_id=database_id,
        object_id=object_id,
        query_id=identity_b1.query_id,
        query_text_id=identity_b1.query_text_id,
        context_settings_id=identity_b1.context_settings_id,
        query_hash=identity_b1.query_hash,
        query_plan_hash=actual_plan_state.query_plan_hash,
        parameterization_type=identity_b1.parameterization_type,
        target_plan_id=target_plan_id,
        actual_plan_id=actual_plan_id,
        source_bound=True,
        # Form-A plan identity is established by the uniquely bound plan/cache
        # candidate and Query Store plan_id. UsePlan is a separate phase claim
        # and is intentionally false for the unforced calls.
        current_plan=actual_plan_id == target_plan_id,
        fresh_compilation_proven=compile_delta,
        compile_count_before=compile_before,
        compile_count_after=compile_after,
        compile_epoch_before=compile_epoch_before,
        compile_epoch_after=compile_epoch_after,
        recompile_marked=(call_number > 1),
        compile_flush_complete=True,
        context_bound=True,
        transport_complete=True,
        rows=rows,
        execution_delta=actual_execution_delta,
        force_accepted=force_accepted,
        is_forced_plan_after_request=is_forced_after,
        use_plan=plan_summary.use_plan if forced else None,
        force_error_epoch=force_epoch,
        force_failure_count_after_request=force_failure_after_request,
        force_failure_count_after_execution=failure_after,
        unforce_confirmed=unforce_confirmed,
        is_forced_plan=final_is_forced,
        hint_state=hint_state,
        external_override_absent=True,
    )
    if identity_b1.query_text_bytes not in {
        views.statement_text.encode("utf-16le"),
        views.statement_without_terminator.encode("utf-16le"),
    }:
        raise Dgn004RuntimeError("Query Store text is outside the registered S/T forms")
    return evidence, identity_b1, target_plan_id


def _drop_database_sql(database: str, run_token: str) -> str:
    return f"""SET NOCOUNT ON;
DECLARE @Database sysname=N'{database}';
IF DB_ID(@Database) IS NULL THROW 51050,'DGN-004 owned database is already absent.',1;
DECLARE @MarkerCount int=0;
DECLARE @Project nvarchar(128),@Contract nvarchar(128),@Demo nvarchar(128),@Run nvarchar(128);
DECLARE @MarkerSql nvarchar(max)=N'SELECT
 @MarkerCount=COUNT(*),
 @Project=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),
 @Contract=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(128),value) END),
 @Demo=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(128),value) END),
 @Run=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(128),value) END)
 FROM ' + QUOTENAME(@Database) + N'.sys.extended_properties
 WHERE class=0 AND major_id=0 AND minor_id=0
 AND name IN (N''SQLPERF.Project'',N''SQLPERF.ContractVersion'',N''SQLPERF.DemoId'',N''SQLPERF.RunToken'')';
EXEC sys.sp_executesql @MarkerSql,
    N'@MarkerCount int OUTPUT,@Project nvarchar(128) OUTPUT,@Contract nvarchar(128) OUTPUT,@Demo nvarchar(128) OUTPUT,@Run nvarchar(128) OUTPUT',
    @MarkerCount OUTPUT,@Project OUTPUT,@Contract OUTPUT,@Demo OUTPUT,@Run OUTPUT;
IF @MarkerCount<>4
   OR @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung'
   OR DATALENGTH(@Project)<>DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2<>N'1.0'
   OR DATALENGTH(@Contract)<>DATALENGTH(N'1.0')
   OR @Demo IS NULL OR @Demo COLLATE Latin1_General_100_BIN2<>N'DGN-004'
   OR DATALENGTH(@Demo)<>DATALENGTH(N'DGN-004')
   OR @Run IS NULL OR @Run COLLATE Latin1_General_100_BIN2<>N'{run_token}'
   OR DATALENGTH(@Run)<>DATALENGTH(N'{run_token}')
    THROW 51051,'DGN-004 owned database markers do not match.',1;
ALTER DATABASE {f'[{database}]'} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE {f'[{database}]'};
SELECT 'DGN004_DB_DROPPED|{run_token}';
"""


def _database_absent_sql(database: str) -> str:
    return f"SET NOCOUNT ON; IF DB_ID(N'{database}') IS NOT NULL THROW 51052,'DGN-004 database remains after cleanup.',1; SELECT 'DGN004_DB_ABSENT';"


def run_build(profile: BuildProfile, *, deadline: float) -> tuple[BuildEvidence, dict[str, object]]:
    budget = BuildBudget(deadline)
    container: OwnedContainer | None = None
    database: str | None = None
    baseline: dict[str, object] | None = None
    server_baseline: dict[str, tuple[int, int]] | None = None
    server_changed = False
    database_created = False
    setup_started = False
    cleanup_ok = False
    container_start_cleanup_ok = True
    cleanup_failure_phase = "not-started"
    cleanup_failures: list[str] = []
    evidence: BuildEvidence | None = None
    run_token = secrets.token_hex(6).upper()
    _validate_run_token(run_token)
    database = _database_name(run_token)
    calls: list[CallEvidence] = []
    ids: dict[str, QueryIdentity] = {}
    objects: dict[str, int] = {}
    target_plans: dict[str, int] = {}
    verdict = Verdict.NOT_PROVEN
    reasons: list[str] = []
    started = time.monotonic()
    cleanup_deadline: float | None = None
    phase = "container-startup"
    try:
        container = start_owned_container(profile, deadline=deadline, run_token=run_token)
        if container.run_token != run_token:
            raise Dgn004RuntimeError("container and database run tokens differ")
        with sqlcmd_password(container.sa_password):
            # Read only the owned container's startup log; issue SQL exactly
            # once, after the engine advertises readiness.
            wait_until_sql_server_ready(name=container.name, deadline=deadline)
            phase = "engine-preflight"
            _engine_preflight(container.target, profile, budget)
            phase = "server-config-read"
            server_baseline = _read_server_config(container.target, budget)
            if server_baseline["show advanced options"][1] not in (0, 1):
                raise Dgn004RuntimeError("server advanced-options baseline is invalid")
            server_changed = True
            phase = "server-memory-set"
            _set_server_memory(container.target, budget, 2048)
            phase = "database-create"
            _sql_command(
                container.target, database="master",
                source=_create_database_sql(database, profile.compatibility_level), budget=budget,
            )
            database_created = True
            phase = "database-markers"
            marker_output = _sql_command(
                container.target, database=database,
                source=_add_markers_sql(database, container.run_token), budget=budget,
            )
            if marker_output.strip():
                raise Dgn004RuntimeError("database marker setup emitted unexpected output")
            phase = "database-baseline"
            baseline = _json_baseline(_sql_command(
                container.target, database=database,
                source=_baseline_sql(database), budget=budget, stdout_limit=256 * 1024,
            ))
            if baseline["optimized_plan_forcing"] != 1:
                raise Dgn004RuntimeError("baseline optimized plan forcing option is not ON")
            setup_started = True
            phase = "database-configure"
            configure_output = _sql_command(
                container.target, database="master",
                source=_configure_database_sql(database, profile.compatibility_level), budget=budget,
            )
            if configure_output.strip():
                raise Dgn004RuntimeError("database option configuration emitted unexpected output")
            phase = "fixture-setup"
            setup_output = _sql_command(
                container.target, database=database, source=_setup_sql_source(), budget=budget,
                stdout_limit=2 * 1024 * 1024,
            )
            _validate_setup_output(setup_output, profile)
            phase = "database-identities"
            ids_output = _sql_command(
                container.target, database=database,
                source="""SET NOCOUNT ON;
SELECT 'DGN004_IDS|' + CONVERT(varchar(20),DB_ID()) + '|'
    + CONVERT(varchar(20),OBJECT_ID(N'[dgn004].[ReplayReference]')) + '|'
    + CONVERT(varchar(20),OBJECT_ID(N'[dgn004].[ReplayHintControl]'));
""",
                budget=budget,
            )
            ids_lines = [line.strip() for line in ids_output.splitlines() if line.strip()]
            if len(ids_lines) != 1:
                raise Dgn004RuntimeError("DGN-004 database/object identity frame is incomplete")
            ids_fields = ids_lines[0].split("|")
            if len(ids_fields) != 4 or ids_fields[0] != "DGN004_IDS" or any(
                not value.isdigit() or int(value) <= 0 for value in ids_fields[1:]
            ):
                raise Dgn004RuntimeError("DGN-004 database/object identity is invalid")
            database_id, objects["R"], objects["H"] = map(int, ids_fields[1:])
            if objects["R"] == objects["H"]:
                raise Dgn004RuntimeError("R and H modules did not receive distinct object IDs")
            for call_number, (role, forced) in enumerate(CALL_SEQUENCE, 1):
                phase = f"demo-call-{call_number}-{role}"
                evidence_call, identity, target_plan = _run_call(
                    container, database, database_id,
                    role, call_number, forced, ids.get(role), objects[role],
                    target_plans.get(role), budget,
                )
                if role not in ids:
                    ids[role] = identity
                elif not _identity_matches(
                    identity, dbid=database_id, object_id=objects[role],
                    expected=ids[role], role=role,
                ):
                    raise Dgn004RuntimeError("role identity changed during the nine-call sequence")
                if role in target_plans and target_plans[role] != target_plan:
                    raise Dgn004RuntimeError("target plan identity changed within a role")
                target_plans[role] = target_plan
                calls.append(evidence_call)
            evidence = BuildEvidence(
                build=f"{profile.name}/{profile.product_version}",
                acceptance_scope="CLASSICAL_FORCING_AND_HINT_CONTROL",
                calls=tuple(calls), cleanup_ok=None,
            )
            checked = evaluate_build(evidence)
            verdict, reasons = checked.verdict, list(checked.reasons)
            if verdict is not Verdict.PASS:
                raise Dgn004RuntimeError("DGN-004 acceptance contract did not pass")
    except CaptureTimeoutError as exc:
        verdict, reasons = Verdict.NOT_PROVEN, [f"bounded SQL process timeout during {phase}"]
    except (CaptureProcessEndUnknown, Dgn004UnknownError) as exc:
        verdict, reasons = Verdict.NOT_PROVEN, ["SQL or Docker process completion is unknown"]
    except (Dgn004RuntimeError, CaptureRunnerError, ContainerError, PlanCandidateError,
            CurrentPlanError, OSError, ValueError, UnicodeError) as exc:
        if isinstance(exc, UncertainContainerStartError):
            container_start_cleanup_ok = exc.cleanup_ok
        detail = str(exc) if isinstance(exc, (Dgn004RuntimeError, CaptureSqlcmdError, ContainerError)) else type(exc).__name__
        verdict, reasons = Verdict.NOT_PROVEN, [f"{phase}: {detail}"]
    except KeyboardInterrupt:
        verdict, reasons = Verdict.NOT_PROVEN, ["runtime interrupted"]
    finally:
        cleanup_deadline = time.monotonic() + CLEANUP_BUDGET_SECONDS
        if container is not None:
            cleanup_budget = BuildBudget(cleanup_deadline)
            database_cleanup_ok = not database_created
            try:
                with sqlcmd_password(container.sa_password):
                    if database_created and database is not None:
                        if setup_started and baseline is not None:
                            cleanup_failure_phase = "database-options-restore"
                            _sql_command(
                                container.target, database=database,
                                source=_restore_database_sql(database, baseline),
                                budget=cleanup_budget, timeout_seconds=SQL_TIMEOUT_SECONDS,
                            )
                        cleanup_failure_phase = "database-drop"
                        dropped = _sql_command(
                            container.target, database="master",
                            source=_drop_database_sql(database, container.run_token),
                            budget=cleanup_budget, timeout_seconds=SQL_TIMEOUT_SECONDS,
                        )
                        _assert_exact_frame(dropped, f"DGN004_DB_DROPPED|{container.run_token}")
                        cleanup_failure_phase = "database-absence-check"
                        absent = _sql_command(
                            container.target, database="master", source=_database_absent_sql(database),
                            budget=cleanup_budget, timeout_seconds=SQL_TIMEOUT_SECONDS,
                        )
                        _assert_exact_frame(absent, "DGN004_DB_ABSENT")
                        database_cleanup_ok = True
                    if server_changed and server_baseline is not None:
                        cleanup_failure_phase = "server-config-restore"
                        _restore_server_config(container.target, cleanup_budget, server_baseline)
            except (Exception, KeyboardInterrupt) as exc:
                database_cleanup_ok = False
                detail = str(exc) if type(exc) is Dgn004RuntimeError else type(exc).__name__
                cleanup_failures.append(f"{cleanup_failure_phase}/{detail}")
            container_cleanup_ok = False
            try:
                cleanup_failure_phase = "container-removal"
                cleanup_owned_container(
                    name=container.name, expected_id=container.container_id,
                    run_token=container.run_token, profile=container.profile,
                    deadline=cleanup_deadline,
                )
                container_cleanup_ok = True
            except (Exception, KeyboardInterrupt) as exc:
                container_cleanup_ok = False
                cleanup_failures.append(f"{cleanup_failure_phase}/{type(exc).__name__}")
            cleanup_ok = _cleanup_is_sufficient(
                database_created=database_created,
                database_cleanup_ok=database_cleanup_ok,
                container_cleanup_ok=container_cleanup_ok,
            )
        else:
            cleanup_ok = container_start_cleanup_ok
        if not cleanup_ok:
            prior_reasons = ",".join(reasons) if reasons else "no prior runtime error recorded"
            cleanup_detail = ",".join(cleanup_failures) if cleanup_failures else cleanup_failure_phase
            verdict = Verdict.FAIL_CLEANUP
            reasons = [f"cleanup failed during {cleanup_detail}; prior result: {prior_reasons}"]
        elif evidence is None:
            evidence = BuildEvidence(
                build=f"{profile.name}/{profile.product_version}",
                acceptance_scope="CLASSICAL_FORCING_AND_HINT_CONTROL",
                calls=tuple(calls), cleanup_ok=True,
            )
        else:
            evidence = BuildEvidence(
                build=evidence.build, acceptance_scope=evidence.acceptance_scope,
                calls=evidence.calls, cleanup_ok=True,
            )
            checked = evaluate_build(evidence)
            verdict, reasons = checked.verdict, list(checked.reasons)
    summary: dict[str, object] = {
        "build": profile.name,
        "product_version": profile.product_version,
        "verdict": verdict.value,
        "reasons": reasons[:20],
        "calls_observed": len(calls),
        "sql_batches": budget.batches,
        "query_store_flushes": budget.flushes,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "cleanup_ok": cleanup_ok,
    }
    return evidence or BuildEvidence(
        build=f"{profile.name}/{profile.product_version}",
        acceptance_scope="CLASSICAL_FORCING_AND_HINT_CONTROL",
        calls=tuple(calls), cleanup_ok=cleanup_ok,
    ), summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", choices=("2022", "2025", "matrix"), default="matrix")
    args = parser.parse_args(argv)
    started = time.monotonic()
    deadline = started + TOTAL_BUDGET_SECONDS
    selected = BUILD_PROFILES if args.build == "matrix" else tuple(
        profile for profile in BUILD_PROFILES if profile.name == args.build
    )
    build_results: list[BuildEvidence] = []
    summaries: list[dict[str, object]] = []
    for index, profile in enumerate(selected):
        if index > 0 and deadline - time.monotonic() < MIN_NEXT_BUILD_SECONDS:
            summaries.append({
                "build": profile.name, "verdict": Verdict.NOT_PROVEN.value,
                "reasons": ["less than the reserved 180-second next-build budget remains"],
            })
            break
        build, summary = run_build(profile, deadline=deadline)
        build_results.append(build)
        summaries.append(summary)
        # A non-pass may advance to the explicitly selected next build only
        # after verified cleanup and while the reserved minimum remains.
        # Cleanup failure and an exhausted matrix budget always stop.
        if summary["verdict"] == Verdict.FAIL_CLEANUP.value or summary.get("cleanup_ok") is not True:
            break
    matrix = evaluate_matrix(tuple(build_results)) if len(selected) > 1 else None
    print(json.dumps({
        "acceptance_scope": "CLASSICAL_FORCING_AND_HINT_CONTROL",
        "builds": summaries,
        "matrix_verdict": None if matrix is None else matrix.verdict.value,
        "matrix_reasons": [] if matrix is None else list(matrix.reasons[:20]),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }, sort_keys=True, separators=(",", ":")))
    if any(item.get("verdict") in {Verdict.FAIL.value, Verdict.FAIL_CLEANUP.value} for item in summaries):
        return 1
    if any(item.get("verdict") != Verdict.PASS.value for item in summaries):
        return 2
    if matrix is not None and matrix.verdict is not Verdict.PASS:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
