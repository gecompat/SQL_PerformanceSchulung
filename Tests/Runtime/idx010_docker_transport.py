"""Docker and sqlcmd transport for the IDX-010 pilot.

The reviewable transport has no CLI and is not invoked by offline CI.
"""
from __future__ import annotations

import json
import os
import re
import secrets
from time import monotonic, sleep
from collections.abc import Iterator, Sequence

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from idx010_index_metadata import decode_index_evidence, index_evidence_batch
from idx010_pilot_sequence import IndexEvidence, QueryCapture, Target, WORK_SECONDS
from idx010_pilot_setup import Arm, FIXTURE_ROWS, fixture_identity_batch, fixture_setup_batch, target_database
from idx010_provision_sql import (
    DB_FILE_LIMIT_MIB,
    TEMPDB_CAPS,
    TEMPDB_DATA_LIMIT_MIB,
    TEMPDB_LOG_LIMIT_MIB,
    create_reader_batch,
    drop_database_batch,
    drop_reader_batch,
    grant_reader_batch,
    provision_database_batch,
    reader_login,
)
from idx010_sqlcmd_capture import CONTAINER_ID, MeasurementConnection, capture_query

IMAGE = "mcr.microsoft.com/mssql/server@sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9"
PROFILE = "17.0.5065.9|Enterprise Developer Edition (64-bit)"
PROFILE_SQL = (
    "SET NOCOUNT ON; SELECT CONCAT("
    "CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion')), '|', "
    "CONVERT(nvarchar(128), SERVERPROPERTY('Edition')));"
)
OWNER_LABEL = "com.sqlperf.idx010.owner"
MEMORY = 4 * 1024**3
CPU_NANOS = 2 * 10**9
# Two databases with a data and a log file each, plus TempDB.
MIN_DATA_AVAILABLE_KIB = (4 * DB_FILE_LIMIT_MIB + TEMPDB_DATA_LIMIT_MIB + TEMPDB_LOG_LIMIT_MIB) * 1024
PAGE_ROWS = 262_144
CATALOG_JOIN_WARNING = b"Warning: The join order has been enforced because a local join hint is used."
ROW = re.compile(rb" *([0-9]{1,7}) *\| *([0-9]{1,7}) *")


class DockerPilotTransport:
    def __init__(self) -> None:
        self._owner = secrets.token_hex(16)
        self._sa_password = "Idx9!" + secrets.token_hex(16)
        self._reader_password = "Idx9!" + secrets.token_hex(16)
        self._reader_sid = secrets.token_hex(16)
        self._reader_attempted = False
        self._run_token: str | None = None
        self._name: str | None = None
        self._container: str | None = None
        self._ready = False

    def start_verified_instance(self, run_token: str, deadline: float) -> None:
        target_database(run_token, Arm.CONTROL)
        if self._run_token is not None:
            raise ValueError("pilot transport is single use")
        image_id = _docker(["image", "inspect", "--format", "{{.Id}}", IMAGE], deadline).strip()
        if not re.fullmatch(rb"sha256:[0-9a-f]{64}", image_id):
            raise OSError("pinned image is not locally available")
        self._run_token = run_token
        self._name = f"sqlperf-idx010-{self._owner}"
        environment = os.environ.copy()
        environment["MSSQL_SA_PASSWORD"] = self._sa_password
        result = _docker([
            "create", "--pull", "never", "--name", self._name, "--label", f"{OWNER_LABEL}={self._owner}",
            "--network", "none", "--cpus", "2", "--memory", "4g", "--memory-swap", "4g",
            "-e", "ACCEPT_EULA=Y", "-e", "MSSQL_PID=Developer", "-e", "MSSQL_SA_PASSWORD", IMAGE,
        ], deadline, environment).strip().decode("ascii")
        if not CONTAINER_ID.fullmatch(result) or self._find_owned(deadline) != result:
            raise OSError("pilot container ownership cannot be established")
        self._container = result
        shape = _docker([
            "inspect", "--format",
            "{{.Image}}|{{.HostConfig.NetworkMode}}|{{.HostConfig.NanoCpus}}|"
            "{{.HostConfig.Memory}}|{{.HostConfig.MemorySwap}}|{{json .Mounts}}|{{json .HostConfig.PortBindings}}|"
            "{{.State.Status}}",
            result,
        ], deadline).strip().split(b"|")
        if (
            len(shape) != 8
            or shape[:5] != [image_id, b"none", str(CPU_NANOS).encode(), str(MEMORY).encode(), str(MEMORY).encode()]
            or json.loads(shape[5]) not in ([], None)
            or json.loads(shape[6]) not in ({}, None)
            or shape[7] != b"created"
        ):
            raise OSError("pilot container limits differ from the profile")
        _docker(["start", result], deadline)
        ready_deadline = min(deadline, monotonic() + 90)
        while True:
            try:
                profile = self._sql(
                    "master", PROFILE_SQL,
                    min(ready_deadline, monotonic() + 12),
                )
                break
            except (OSError, TimeoutError):
                if monotonic() + 2 >= ready_deadline:
                    raise TimeoutError("owned SQL instance did not become ready") from None
                sleep(1)
        if profile.strip().decode("ascii") != PROFILE:
            raise OSError("SQL Server build or edition does not match the profile")
        capacity = _docker(
            ["exec", "-e", "LC_ALL=C", result, "df", "-k", "--output=avail", "/var/opt/mssql/data"],
            deadline,
        )
        match = re.fullmatch(rb" *Avail\r?\n *([0-9]{1,19}) *\r?\n?", capacity)
        if match is None or int(match[1]) < MIN_DATA_AVAILABLE_KIB:
            raise OSError("pilot data filesystem does not have confirmed free capacity")
        self._sql("master", TEMPDB_CAPS, deadline)
        self._reader_attempted = True
        self._sql("master", create_reader_batch(run_token, self._reader_password, self._reader_sid), deadline)
        self._ready = True

    def provision(self, target: Target, deadline: float) -> None:
        self._require_target(target)
        self._sql("master", provision_database_batch(target), deadline)

    def execute(self, target: Target, sql: str, deadline: float) -> None:
        self._require_target(target)
        self._sql(target.database_name, sql, deadline)
        if sql == fixture_setup_batch(target.run_token, target.arm):
            self._sql(target.database_name, grant_reader_batch(target), deadline)

    def stream_rows(self, target: Target, sql: str, deadline: float) -> Iterator[tuple[int, int]]:
        self._require_target(target)
        if sql != fixture_identity_batch(target.run_token, target.arm):
            raise ValueError("identity stream requires the fixed pilot query")
        for start in range(0, FIXTURE_ROWS, PAGE_ROWS):
            page = sql.replace(
                "FROM dbo.Events\nORDER BY EventId",
                f"FROM dbo.Events\nWHERE EventId >= {start} AND EventId < {start + PAGE_ROWS}\nORDER BY EventId",
                1,
            )
            # Each row is two fixed-width bigint fields and the column separator.
            data = self._sql(target.database_name, page, deadline, output_limit=PAGE_ROWS * 48)
            count = 0
            for line in data.splitlines():
                if not line.strip():
                    continue
                fields = ROW.fullmatch(line)
                if fields is None or count == PAGE_ROWS:
                    raise ValueError("identity stream page has unexpected rows")
                count += 1
                yield int(fields[1]), int(fields[2])
            if count != PAGE_ROWS:
                raise ValueError("identity stream page is incomplete")

    def index_evidence(self, target: Target, deadline: float) -> IndexEvidence:
        self._require_target(target)
        payload = self._sql(
            target.database_name, index_evidence_batch(target), deadline,
            allowed_warning=CATALOG_JOIN_WARNING,
        )
        return decode_index_evidence(payload, target)

    def capture_query(self, target: Target, sql: str, deadline: float) -> QueryCapture:
        self._require_target(target)
        assert self._container is not None
        connection = MeasurementConnection(self._container, reader_login(target.run_token), self._reader_password)
        return capture_query(connection, target, sql, deadline)

    def cleanup(self, run_token: str, attempted: tuple[Target, ...], deadline: float) -> bool:
        if self._name is None:
            return not attempted
        if self._run_token != run_token or any(target.run_token != run_token for target in attempted):
            return False
        owned = self._find_owned(deadline)
        if owned is None:
            # A timed-out create can finish on the daemon after an empty listing.
            return self._container is not None and not attempted and not self._reader_attempted
        self._container = owned
        sql_confirmed = True
        for target in reversed(attempted):
            try:
                db_check = (
                    "SET NOCOUNT ON; SELECT CASE WHEN "
                    f"DB_ID(N'{target.database_name}') IS NULL THEN 0 ELSE 1 END;"
                )
                db_exists = self._sql("master", db_check, min(deadline - 10, monotonic() + 15)).strip()
                if db_exists == b"1":
                    self._sql(target.database_name, drop_database_batch(target), min(deadline - 10, monotonic() + 20))
                elif db_exists != b"0":
                    sql_confirmed = False
            except (OSError, TimeoutError, ValueError):
                sql_confirmed = False
        if self._reader_attempted:
            try:
                self._sql(
                    "master",
                    drop_reader_batch(run_token, self._reader_sid),
                    min(deadline - 10, monotonic() + 10),
                )
            except (OSError, TimeoutError, ValueError):
                sql_confirmed = False
        if self._find_owned(deadline) != owned:
            return False
        _docker(["rm", "--force", "--volumes", owned], deadline)
        return self._find_owned(deadline) is None and sql_confirmed

    def _find_owned(self, deadline: float) -> str | None:
        assert self._name is not None
        base = ["container", "ls", "--all", "--quiet", "--no-trunc", "--filter"]
        by_label = _docker([*base, f"label={OWNER_LABEL}={self._owner}"], deadline).strip().decode("ascii")
        by_name = _docker([*base, f"name=^/{self._name}$"], deadline).strip().decode("ascii")
        if not by_label and not by_name:
            return None
        if by_label != by_name or not CONTAINER_ID.fullmatch(by_name):
            raise OSError("pilot container identity is ambiguous")
        if self._container is not None and by_name != self._container:
            raise OSError("pilot container ID changed")
        return by_name

    def _require_target(self, target: Target) -> None:
        if not self._ready or self._run_token != target.run_token:
            raise OSError("target does not belong to this ready pilot")

    def _sql(
        self, database: str, sql: str, deadline: float, output_limit: int = 65_536,
        *, allowed_warning: bytes | None = None,
    ) -> bytes:
        if self._container is None:
            raise OSError("no verified pilot container")
        remaining = deadline - monotonic()
        if remaining < 2:
            raise TimeoutError("SQL pilot deadline exceeded")
        environment = os.environ.copy()
        environment["SQLCMDPASSWORD"] = self._sa_password
        command = [
            "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", "-e", "SQLCMDINI=",
            self._container, "/opt/mssql-tools18/bin/sqlcmd", "-S", "127.0.0.1",
            "-d", database, "-U", "sa", "-C", "-b", "-x", "-r", "1", "-h", "-1", "-s", "|",
            "-y", "4096", "-w", "8192", "-l", str(min(5, int(remaining))),
            "-t", str(min(65534, int(remaining))),
        ]
        return _run(
            command, (sql.rstrip() + "\nGO\n").encode("ascii"), environment, deadline, output_limit,
            allowed_warning=allowed_warning,
        )


def _docker(args: Sequence[str], deadline: float, environment: dict[str, str] | None = None) -> bytes:
    return _run(["docker", *args], b"", environment or os.environ.copy(), deadline, 65_536)


def _run(
    command: list[str], payload: bytes, environment: dict[str, str], deadline: float, limit: int,
    *, allowed_warning: bytes | None = None,
) -> bytes:
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise TimeoutError("pilot process deadline exceeded")
    try:
        result = collect_bounded_process(
            command, input_bytes=payload, environment=environment, timeout_seconds=remaining,
            stdout_limit_bytes=limit, stderr_limit_bytes=16_384, timeout_ceiling_seconds=WORK_SECONDS,
        )
    except CaptureTimeoutError:
        raise TimeoutError("pilot process deadline exceeded") from None
    except CaptureRunnerError:
        raise OSError("pilot process could not be completed") from None
    if result.returncode or result.stderr:
        # USE and ALTER DATABASE can emit an informational database-context line.
        messages = result.stderr.splitlines()
        if result.returncode or any(
            message != allowed_warning and not message.startswith(b"Changed database context to '")
            for message in messages
        ):
            raise OSError("pilot process failed")
    if monotonic() >= deadline:
        raise TimeoutError("pilot process deadline exceeded")
    return result.stdout
