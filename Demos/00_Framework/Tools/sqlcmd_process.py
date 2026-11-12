#!/usr/bin/env python3
"""Shared process wrapper for the external Microsoft sqlcmd command-line tool.

The module never writes captured output to disk. Callers decide whether raw
interactive output may be shown. Passwords are accepted only through the
SQLCMDPASSWORD environment variable and are never placed on the command line.
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
import time
from typing import Mapping, Sequence


SUMMARY_PATTERN = re.compile(
    r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$",
    flags=re.MULTILINE,
)
RESULTSET_SUMMARY_PATTERN = re.compile(
    r"^\s*\d+\|[^|]*\|SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)\|",
    flags=re.MULTILINE,
)


@dataclass(frozen=True)
class SqlcmdResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_seconds: float

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def resolve_sqlcmd(explicit_path: str | None = None) -> str:
    """Resolve sqlcmd without invoking a shell."""

    if explicit_path:
        candidate = Path(explicit_path).expanduser()
        if not candidate.is_file():
            raise FileNotFoundError(f"sqlcmd executable not found: {candidate}")
        return str(candidate.resolve())

    discovered = shutil.which("sqlcmd")
    if discovered is None:
        raise FileNotFoundError("sqlcmd executable not found in PATH")
    return discovered


def _launcher(executable: str) -> list[str]:
    """Resolve the argument prefix that starts the resolved sqlcmd endpoint."""

    # Ein Python-Shim ist unter Windows nicht direkt als Prozess startbar.
    if Path(executable).suffix.lower() == ".py":
        return [sys.executable, executable]
    return [executable]


def _validate_connection_text(value: str, field_name: str) -> str:
    value = value.strip()
    if not value or any(ch in value for ch in "\r\n\x00"):
        raise ValueError(f"invalid {field_name}")
    return value


def build_sqlcmd_command(
    *,
    executable: str,
    server: str,
    database: str,
    script: Path,
    auth: str,
    username: str | None = None,
    variables: Mapping[str, str] | None = None,
) -> list[str]:
    """Build a sqlcmd command as an argument vector."""

    server = _validate_connection_text(server, "server")
    database = _validate_connection_text(database, "database")
    script = script.resolve()

    if not script.is_file() or script.suffix.lower() != ".sql":
        raise ValueError(f"SQL script does not exist or is not .sql: {script}")

    command = [
        *_launcher(executable),
        "-b",
        "-r",
        "1",
        "-W",
        "-s",
        "|",
        "-h",
        "-1",
        "-w",
        "65535",
        "-S",
        server,
        "-d",
        database,
        "-i",
        str(script),
    ]

    normalized_auth = auth.strip().lower()
    if normalized_auth == "integrated":
        command.append("-E")
    elif normalized_auth == "sql":
        if not username:
            raise ValueError("SQL authentication requires --username")
        if not os.environ.get("SQLCMDPASSWORD"):
            raise ValueError(
                "SQL authentication requires SQLCMDPASSWORD in the process environment"
            )
        command.extend(["-U", _validate_connection_text(username, "username")])
    elif normalized_auth == "aad":
        command.append("-G")
    else:
        raise ValueError("auth must be integrated, sql, or aad")

    if variables:
        normalized: list[str] = []
        for name, value in sorted(variables.items()):
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", name):
                raise ValueError(f"invalid sqlcmd variable name: {name}")
            if any(ch in value for ch in "\r\n\x00"):
                raise ValueError(f"invalid sqlcmd variable value for {name}")
            normalized.append(f"{name}={value}")
        if normalized:
            command.extend(["-v", *normalized])

    return command


def _linux_process_identity(pid: int) -> tuple[int, str] | None:
    """Parent und Startzeit lesen; wiederverwendete PIDs bleiben geschützt."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()
        return int(fields[1]), fields[19]
    except (OSError, ValueError, IndexError):
        return None


def _linux_descendants(parent_pid: int) -> list[tuple[int, str]]:
    """Nachfahren einschließlich eigener Sessions vor dem Abbruch erfassen."""
    identities: dict[int, tuple[int, str]] = {}
    try:
        entries = list(Path("/proc").iterdir())
    except OSError:
        return []
    for entry in entries:
        if entry.name.isdecimal():
            pid = int(entry.name)
            identity = _linux_process_identity(pid)
            if identity is not None:
                identities[pid] = identity
    descendants: list[tuple[int, str]] = []
    parents = {parent_pid}
    while parents:
        children = {pid for pid, (parent, _) in identities.items() if parent in parents}
        descendants.extend((pid, identities[pid][1]) for pid in sorted(children))
        for pid in children:
            del identities[pid]
        parents = children
    return descendants


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    """Hard-stop sqlcmd and any descendants after timeout or fail-fast."""

    # Ein bereits beendeter/reapter Root darf nicht über eine inzwischen
    # möglicherweise wiederverwendete PID erneut adressiert werden.
    if process.poll() is not None:
        return

    try:
        if os.name == "nt":
            # process.kill() allein lässt Harness-/Shim-Nachfahren weiterlaufen.
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    check=False, capture_output=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
            if process.poll() is None:
                process.kill()
        else:
            descendants = _linux_descendants(process.pid) if sys.platform.startswith("linux") else []
            for pid, started in reversed(descendants):
                identity = _linux_process_identity(pid)
                if identity is not None and identity[1] == started:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError, OSError):
                        pass
            os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            process.kill()
        except (ProcessLookupError, PermissionError, OSError):
            pass

    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass


def start_sqlcmd(
    command: Sequence[str],
    *,
    environment: Mapping[str, str] | None = None,
) -> subprocess.Popen[str]:
    """Start sqlcmd in a separate process group."""

    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    child_environment = dict(environment) if environment is not None else os.environ.copy()
    # Python-Shims schreiben in denselben UTF-8-Kanal, den dieser Prozess dekodiert.
    child_environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.Popen(
        list(command),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=child_environment,
        shell=False,
        start_new_session=(os.name != "nt"),
        creationflags=creationflags,
    )


def collect_process(
    process: subprocess.Popen[str],
    command: Sequence[str],
    *,
    timeout_seconds: float,
) -> SqlcmdResult:
    """Collect output and enforce a hard timeout."""

    started = time.monotonic()
    timed_out = False
    try:
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process_tree(process)
            stdout, stderr = process.communicate(timeout=5)
    except BaseException:
        # Auch Ctrl+C/SystemExit muss den Prozess des Setups vor der
        # unabhängigen Prüfung des Cleanups vollständig beenden.
        try:
            _terminate_process_tree(process)
        except BaseException:
            pass
        try:
            process.communicate(timeout=5)
        except BaseException:
            try:
                process.wait(timeout=2)
            except BaseException:
                pass
        raise

    return SqlcmdResult(
        command=tuple(command),
        returncode=process.returncode if process.returncode is not None else -1,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        duration_seconds=time.monotonic() - started,
    )


def run_sqlcmd(
    command: Sequence[str],
    *,
    timeout_seconds: float,
    environment: Mapping[str, str] | None = None,
) -> SqlcmdResult:
    process = start_sqlcmd(command, environment=environment)
    return collect_process(process, command, timeout_seconds=timeout_seconds)


def extract_summary(*texts: str) -> tuple[str, str] | None:
    """Return the last machine-readable summary marker."""

    matches: list[tuple[str, str]] = []
    for text in texts:
        matches.extend(SUMMARY_PATTERN.findall(text))
        matches.extend(RESULTSET_SUMMARY_PATTERN.findall(text))
    return matches[-1] if matches else None
