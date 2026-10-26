"""Bounded sqlcmd runner for the DGN-004 plan-frame transport fragment.

This runner transports a caller-supplied plan handle only. It does not resolve
the handle to a query, statement, module, or intended execution.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
SQL_SOURCE = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair" / "CapturePlanFrame.sql"
RUNTIME = ROOT / "Tests" / "Runtime"
STATIC = ROOT / "Tests" / "Static"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))
if str(STATIC) not in sys.path:
    sys.path.insert(0, str(STATIC))

from dgn004_capture_input import CaptureInput, build_sqlcmd_variables  # noqa: E402
from dgn004_capture_result import DecodedPlanCapture, decode_plan_capture_result  # noqa: E402
from execution_target import DOCKER, ExecutionTarget  # noqa: E402


STDOUT_LIMIT_BYTES = 2 * 1024 * 1024
STDERR_LIMIT_BYTES = 64 * 1024
PROCESS_TIMEOUT_SECONDS = 20.0
SQL_TIMEOUT_SECONDS = 15.0
_READ_BLOCK_BYTES = 64 * 1024
_PIPE_EOF_GRACE_SECONDS = 1.0


class CaptureRunnerError(RuntimeError):
    """Reject process, stream, or decoded-result failures without raw output."""


class CaptureOutputLimitError(CaptureRunnerError):
    """One captured output channel exceeded its while-reading limit."""


class CaptureTimeoutError(CaptureRunnerError):
    """The local sqlcmd/docker process exceeded its process deadline."""


class CaptureProcessEndUnknown(CaptureRunnerError):
    """Local process/pipe completion could not be established; do not retry."""


class CaptureSqlcmdError(CaptureRunnerError):
    """The bounded process ended unsuccessfully or wrote diagnostic output."""


@dataclass(frozen=True)
class BoundedProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    duration_seconds: float


def _read_bounded(
    stream,
    limit: int,
    channel: str,
    overflow: threading.Event,
    overflow_channel: list[str],
    overflow_lock: threading.Lock,
    result: dict[str, bytes],
    reader_errors: list[BaseException],
) -> None:
    captured = bytearray()
    try:
        while True:
            remaining = max(0, limit - len(captured))
            # Read no more than the remaining allowance plus one sentinel byte.
            size = min(_READ_BLOCK_BYTES, remaining + 1) if not overflow.is_set() else _READ_BLOCK_BYTES
            chunk = stream.read(max(1, size))
            if not chunk:
                break
            if not overflow.is_set():
                if len(chunk) > remaining:
                    captured.extend(chunk[:remaining])
                    with overflow_lock:
                        if not overflow_channel:
                            overflow_channel.append(channel)
                    overflow.set()
                else:
                    captured.extend(chunk)
            # After the first overflow, keep draining and discarding until the
            # coordinator terminates the process tree, so neither pipe blocks.
    except (OSError, ValueError) as exc:
        # Pipe closure during process termination is expected. Completion is
        # still checked by joining this reader before returning a result.
        reader_errors.append(exc)
    finally:
        result[channel] = bytes(captured)
        try:
            stream.close()
        except OSError:
            pass


def _write_stdin(stream, payload: bytes, result: list[BaseException]) -> None:
    try:
        if payload:
            stream.write(payload)
            stream.flush()
    except (BrokenPipeError, OSError) as exc:
        result.append(exc)
    finally:
        try:
            stream.close()
        except OSError as exc:
            result.append(exc)


def _terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    if os.name == "nt":
        # Best-effort tree stop. Windows taskkill cannot prove that descendants
        # of an already-exited launcher were found; an open pipe becomes
        # CaptureProcessEndUnknown and the caller must not retry SQL.
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                capture_output=True,
                timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        if process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            if process.poll() is None:
                process.kill()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired as exc:
        raise CaptureProcessEndUnknown("process end remains unknown after termination") from exc


def collect_bounded_process(
    command: Sequence[str],
    *,
    input_bytes: bytes,
    environment: Mapping[str, str],
    timeout_seconds: float = PROCESS_TIMEOUT_SECONDS,
    stdout_limit_bytes: int = STDOUT_LIMIT_BYTES,
    stderr_limit_bytes: int = STDERR_LIMIT_BYTES,
) -> BoundedProcessResult:
    """Stream both channels concurrently, retain only their fixed allowances."""
    if type(command) not in (list, tuple) or not command or any(
        type(item) is not str or not item or "\x00" in item for item in command
    ):
        raise CaptureRunnerError("invalid process argument vector")
    if type(input_bytes) is not bytes:
        raise CaptureRunnerError("process input must be bytes")
    if (type(timeout_seconds) not in (int, float) or not 0 < timeout_seconds <= PROCESS_TIMEOUT_SECONDS
            or type(stdout_limit_bytes) is not int or stdout_limit_bytes < 0
            or type(stderr_limit_bytes) is not int or stderr_limit_bytes < 0):
        raise CaptureRunnerError("invalid process limits")
    if type(environment) is not dict or any(
        type(key) is not str or type(value) is not str or "\x00" in key or "\x00" in value
        for key, value in environment.items()
    ):
        raise CaptureRunnerError("invalid process environment")

    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            list(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(environment),
            shell=False,
            bufsize=0,
            start_new_session=(os.name != "nt"),
            creationflags=creationflags,
        )
    except OSError as exc:
        raise CaptureSqlcmdError("could not start the capture process") from exc

    if process.stdin is None or process.stdout is None or process.stderr is None:
        _terminate_process_tree(process)
        raise CaptureProcessEndUnknown("required process pipes were not created")

    overflow = threading.Event()
    overflow_channel: list[str] = []
    overflow_lock = threading.Lock()
    channels: dict[str, bytes] = {}
    reader_errors: list[BaseException] = []
    writer_errors: list[BaseException] = []
    out_reader = threading.Thread(
        target=_read_bounded,
        args=(process.stdout, stdout_limit_bytes, "stdout", overflow, overflow_channel, overflow_lock, channels, reader_errors),
        daemon=True,
    )
    err_reader = threading.Thread(
        target=_read_bounded,
        args=(process.stderr, stderr_limit_bytes, "stderr", overflow, overflow_channel, overflow_lock, channels, reader_errors),
        daemon=True,
    )
    writer = threading.Thread(
        target=_write_stdin,
        args=(process.stdin, input_bytes, writer_errors),
        daemon=True,
    )
    out_reader.start()
    err_reader.start()
    writer.start()

    deadline = started + float(timeout_seconds)
    timed_out = False
    while process.poll() is None:
        if overflow.is_set():
            _terminate_process_tree(process)
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            _terminate_process_tree(process)
            break
        overflow.wait(min(remaining, 0.025))

    # A fast process can exit at the same instant as the cap is crossed.
    if overflow.is_set() and not overflow_channel:
        raise CaptureProcessEndUnknown("output overflow channel was not recorded")
    for thread in (writer, out_reader, err_reader):
        wait_seconds = 5 if thread is writer else _PIPE_EOF_GRACE_SECONDS
        thread.join(timeout=wait_seconds)
        if thread.is_alive():
            _terminate_process_tree(process)
            thread.join(timeout=2)
            raise CaptureProcessEndUnknown("process stream reader did not complete")
    if timed_out:
        raise CaptureTimeoutError("capture process exceeded its deadline")
    if overflow_channel:
        raise CaptureOutputLimitError(f"{overflow_channel[0]} exceeded its byte limit")
    if writer_errors:
        raise CaptureSqlcmdError("capture input could not be delivered completely")
    if reader_errors:
        raise CaptureProcessEndUnknown("capture output reader did not complete cleanly")
    return BoundedProcessResult(
        returncode=process.returncode if process.returncode is not None else -1,
        stdout=channels.get("stdout", b""),
        stderr=channels.get("stderr", b""),
        duration_seconds=time.monotonic() - started,
    )


def build_capture_command(
    target: ExecutionTarget,
    *,
    database: str,
    inputs: CaptureInput,
) -> tuple[list[str], bytes, dict[str, str]]:
    """Build direct Docker `exec` argv, avoiding the buffering sqlcmd proxy."""
    if type(target) is not ExecutionTarget or target.kind != DOCKER:
        raise CaptureRunnerError("DGN-004 capture requires its disposable Docker target")
    if (target.auth != "sql" or target.username != "sa" or target.server != "localhost"
            or type(target.container) is not str
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", target.container)
            or type(target.sqlcmd_path) is not str or not target.sqlcmd_path):
        raise CaptureRunnerError("invalid DGN-004 Docker target")
    if (type(database) is not str
            or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", database)):
        raise CaptureRunnerError("invalid target database")
    environment = target.child_environment()
    if not environment.get("SQLCMDPASSWORD"):
        raise CaptureRunnerError("SQLCMDPASSWORD is required in the process environment")
    variables = build_sqlcmd_variables(inputs)
    command = [
        shutil.which("docker") or "docker",
        "exec", "-i", "-e", "SQLCMDPASSWORD", target.container,
        target.sqlcmd_path,
        "-S", "localhost", "-d", database, "-U", "sa", "-C",
        "-b", "-r", "1", "-t", "15", "-W", "-s", "|", "-h", "-1", "-w", "65535",
        "-v", *(f"{name}={value}" for name, value in sorted(variables.items())),
    ]
    try:
        sql_source = SQL_SOURCE.read_bytes()
    except OSError as exc:
        raise CaptureRunnerError("DGN-004 capture SQL source is unreadable") from exc
    return command, sql_source, environment


def run_plan_capture(
    target: ExecutionTarget,
    *,
    database: str,
    inputs: CaptureInput,
) -> DecodedPlanCapture:
    """Run the bounded read-only transport and bind only invocation labels."""
    command, sql_source, environment = build_capture_command(
        target, database=database, inputs=inputs
    )
    result = collect_bounded_process(
        command,
        input_bytes=sql_source,
        environment=environment,
    )
    if result.returncode != 0:
        raise CaptureSqlcmdError("sqlcmd ended unsuccessfully")
    if result.stderr:
        raise CaptureSqlcmdError("sqlcmd wrote diagnostic output")
    try:
        frame_text = result.stdout.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise CaptureSqlcmdError("sqlcmd frame output is not ASCII") from exc
    return decode_plan_capture_result(
        frame_text,
        expected_run=inputs.run,
        expected_role=inputs.role,
        expected_call=inputs.call,
    )
