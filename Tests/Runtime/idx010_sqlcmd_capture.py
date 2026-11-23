"""Capture the fixed IDX-010 measurement with one sqlcmd batch in a private container."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
import os
import re
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, CaptureTimeoutError, collect_bounded_process
from idx010_pilot_sequence import QueryCapture, Target, WORK_SECONDS
from idx010_query_evidence import QUERY


PLAN_DISPLAY_WIDTH = 60_000
STDOUT_BYTES = 256 * 1024
STDERR_BYTES = 16 * 1024
COMPLETE = "IDX010_CAPTURE_COMPLETE"
LANGUAGE_MESSAGE = "Changed language setting to us_english."
RESULT_ROW = re.compile(r"[ ]*([0-9]{1,19})[ ]*\|[ ]*([0-9]{1,19})[ ]*", re.ASCII)
CONTAINER_ID = re.compile(r"[0-9a-f]{64}", re.ASCII)
LOGIN = re.compile(r"idx010_reader_[A-Z0-9]{1,20}", re.ASCII)


@dataclass(frozen=True)
class MeasurementConnection:
    """Container and reading credentials established by the owned provisioner."""

    container_id: str
    login: str
    password: str = field(repr=False)


def capture_query(connection: MeasurementConnection, target: Target, sql: str, deadline: float) -> QueryCapture:
    if sql != QUERY:
        raise ValueError("capture is only defined for the fixed pilot query")
    if (
        CONTAINER_ID.fullmatch(connection.container_id) is None
        or LOGIN.fullmatch(connection.login) is None
        or connection.login != f"idx010_reader_{target.run_token}"
        or not connection.password
        or "\x00" in connection.password
    ):
        raise ValueError("capture requires an owned container ID and run-bound reader")

    database = target.database_name
    remaining = deadline - monotonic()
    if remaining < 2:
        raise TimeoutError("not enough time to start measurement")
    command = [
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", "-e", "SQLCMDINI=",
        connection.container_id, "/opt/mssql-tools18/bin/sqlcmd", "-S", "127.0.0.1",
        "-d", database, "-U", connection.login, "-C", "-b", "-r", "1", "-x",
        "-h", "-1", "-y", str(PLAN_DISPLAY_WIDTH), "-w", "65535", "-s", "|",
        "-l", str(min(10, floor(remaining))), "-t", str(min(65534, floor(remaining))),
    ]
    batch = (
        "SET NOCOUNT ON;\n"
        "SET LANGUAGE us_english;\n"
        "SET STATISTICS IO ON;\n"
        "SET STATISTICS XML ON;\n"
        f"{QUERY};\n"
        "SET STATISTICS XML OFF;\n"
        "SET STATISTICS IO OFF;\n"
        f"SELECT CAST('{COMPLETE}' AS varchar(32));\n"
        "GO\n"
    )
    environment = os.environ.copy()
    environment["SQLCMDPASSWORD"] = connection.password
    try:
        process = collect_bounded_process(
            command,
            input_bytes=batch.encode("ascii"),
            environment=environment,
            timeout_seconds=remaining,
            stdout_limit_bytes=STDOUT_BYTES,
            stderr_limit_bytes=STDERR_BYTES,
            timeout_ceiling_seconds=WORK_SECONDS,
        )
    except CaptureTimeoutError:
        raise TimeoutError("SQL measurement deadline exceeded") from None
    except CaptureRunnerError:
        raise OSError("SQL measurement transport failed") from None
    if monotonic() >= deadline:
        raise TimeoutError("SQL measurement deadline exceeded")
    if process.returncode != 0:
        raise OSError("SQL measurement request failed")
    return decode_capture(process.stdout, process.stderr)


def decode_capture(stdout: bytes, stderr: bytes) -> QueryCapture:
    if len(stdout) > STDOUT_BYTES or len(stderr) > STDERR_BYTES:
        raise ValueError("measurement output exceeds the capture limits")
    try:
        rows = [line.strip() for line in stdout.decode("utf-8").splitlines() if line.strip()]
        diagnostics = [line.strip() for line in stderr.decode("utf-8").splitlines() if line.strip()]
    except UnicodeDecodeError:
        raise ValueError("measurement output is not UTF-8") from None
    if len(rows) != 3 or rows[-1] != COMPLETE:
        raise ValueError("expected one result, one plan and the completion record")
    result = RESULT_ROW.fullmatch(rows[0])
    plan = rows[1]
    if (
        result is None
        or len(plan) >= PLAN_DISPLAY_WIDTH
        or not plan.startswith("<ShowPlanXML")
        or not plan.endswith("</ShowPlanXML>")
    ):
        raise ValueError("result or Showplan does not match the bounded sqlcmd profile")
    if diagnostics and diagnostics[0] == LANGUAGE_MESSAGE:
        diagnostics.pop(0)
    if len(diagnostics) != 1 or not diagnostics[0].startswith("Table 'Events'."):
        raise ValueError("expected a single Events information message without diagnostics")
    return QueryCapture(plan, tuple(diagnostics), ((int(result[1]), int(result[2])),))
