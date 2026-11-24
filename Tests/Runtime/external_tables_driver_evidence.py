"""Bind the loaded Driver 18 library to an active External Tables request."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import re
from subprocess import TimeoutExpired
from time import sleep

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from external_tables_guest_identity import _remaining
from external_tables_guest_network import GuestNetwork
from external_tables_pilot_sql import SOURCE_PORT
from inspect_external_tables_driver import LIBRARY, SERVICES, SHA256, VERSION, _read, _start_time, observe


_USERS = re.compile(r'users:\((?:\("[^"\r\n]*",pid=[1-9][0-9]{0,9},fd=[0-9]+\),?)+\)')
_PID = re.compile(r"pid=([1-9][0-9]{0,9}),fd=")
_PROC = Path("/proc")


@dataclass(frozen=True)
class DriverEvidence:
    service: str
    version: str
    driver_file: str
    sha256: str

    def __post_init__(self) -> None:
        values = (self.service, self.version, self.driver_file, self.sha256)
        if any(type(value) is not str for value in values):
            raise ValueError("malformed normalized driver evidence")
        name = LIBRARY.fullmatch(self.driver_file)
        if self.service not in SERVICES or self.version != VERSION or name is None or name[1] != "18":
            raise ValueError("driver evidence differs from the pinned SQL and ODBC profile")
        if SHA256.fullmatch(self.sha256) is None:
            raise ValueError("invalid mapped driver digest")


def observe_connector_driver(network: GuestNetwork, finished: Callable[[], bool], deadline: float) -> DriverEvidence:
    """Capture a unique outbound connector PID while the exact measured SQL request is active."""
    while not finished():
        pid = _live_pid(network, deadline)
        if pid is not None:
            stat = _PROC / str(pid) / "stat"
            started = _start_time(_read(stat, 8192))
            if finished():
                break
            driver = _inspect_driver(pid, deadline)
            if _start_time(_read(stat, 8192)) != started:
                raise ValueError("connector process changed after the live socket observation")
            return driver
        sleep(min(0.01, _remaining(deadline)))
    raise ValueError("no connector process was confirmed during the active request")


def _inspect_driver(pid: int, deadline: float) -> DriverEvidence:
    groups = _read(_PROC / str(pid) / "cgroup", 8192)
    paths = [line[3:] for line in groups.splitlines() if line.startswith("0::")]
    if len(paths) != 1:
        raise ValueError("connector process has no unique service cgroup")
    services = [unit for unit in SERVICES if unit in paths[0].split("/")]
    if len(services) != 1:
        raise ValueError("connector process is outside the expected pilot services")
    try:
        return DriverEvidence(**observe(pid, services[0], deadline=deadline))
    except TimeoutExpired:
        raise TimeoutError("connector driver inspection exceeded the deadline") from None


def _live_pid(network: GuestNetwork, deadline: float) -> int | None:
    command = [
        "/usr/bin/ss", "-4", "-H", "-n", "-t", "-p", "-O", "state", "established",
        "src", str(network.query.ip), "dst", str(network.source.ip), "dport", "=", f":{SOURCE_PORT}",
    ]
    try:
        result = collect_bounded_process(
            command, input_bytes=b"", environment={"LC_ALL": "C"},
            timeout_seconds=min(1, _remaining(deadline)), stdout_limit_bytes=16384, stderr_limit_bytes=4096,
        )
    except CaptureRunnerError:
        raise OSError("live connector sockets could not be read") from None
    if result.returncode or result.stderr:
        raise OSError("live connector sockets could not be read")
    return _unique_pid(result.stdout.decode("ascii"))


def _unique_pid(output: str) -> int | None:
    if not output.strip():
        return None
    processes: set[int] = set()
    for line in output.splitlines():
        fields = line.split(maxsplit=4)
        if len(fields) != 5 or _USERS.fullmatch(fields[-1].strip()) is None:
            raise ValueError("an observed connector socket has no recognized process owner")
        processes.update(int(pid) for pid in _PID.findall(fields[-1]))
    if len(processes) != 1:
        raise ValueError("the active connector socket owner is ambiguous")
    return processes.pop()
