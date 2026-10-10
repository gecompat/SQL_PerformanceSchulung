#!/usr/bin/env python3
"""Den ausgewählten DGN-007-AUTO-Schnitt zweimal auf einem Docker-Ziel prüfen.

180 Sekunden reguläres Budget und 60 Sekunden Cleanup werden durch FWK-010
erzwungen. Der äußere Prozessschutz lässt dafür 20 Sekunden Start-/Abbruchzeit.
Nach jedem Lauf folgt eine unabhängige Abwesenheitsprüfung (30 Sekunden).
Bei unbestätigtem Abbau wird genau einmal der vorhandene, markerprüfende
AUTO-Cleanup-Batch versucht (60 Sekunden), danach erneut geprüft (30 Sekunden).
Recovery macht einen fehlgeschlagenen Lauf niemals erfolgreich. Rohoutput und
Exception-Texte verlassen den Prozess nicht und werden nicht persistiert.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "Tests" / "Runtime"
FRAMEWORK = ROOT / "Demos" / "00_Framework" / "Tools"
for directory in (ROOT, RUNTIME, FRAMEWORK):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import execution_target  # noqa: E402
from execution_target import ExecutionTarget, ExecutionTargetError  # noqa: E402
from run_demo import load_manifest  # noqa: E402
from sqlcmd_process import SqlcmdResult, build_sqlcmd_command, run_sqlcmd  # noqa: E402
from sqlcmd_process import start_sqlcmd, _terminate_process_tree  # noqa: E402
from sqlcmd_process import _linux_descendants, _linux_process_identity  # noqa: E402
from Tests.Contracts.dgn007_capture_projection import decode_projection, ProjectionError  # noqa: E402
from Tests.Contracts.dgn007_prospective_acceptance import contract_from_mapping  # noqa: E402

AUTOMATED = (ROOT / "Demos" / "07_Query_Store_Extended_Events"
             / "DGN-007_Time_Bounded_Search_Incident" / "Automated")
MANIFEST = AUTOMATED / "setup.manifest.json"
DATABASE = "SQLPERF_LAB_DGN007_AUTO"
SCOPE = "DGN-007_DATA_MODEL"
EXPECTED_PHASES = ("PREFLIGHT", "SETUP", "DATA_ASSERTION", "CLEANUP")
HARNESS_TIMEOUT = 180 + 60 + 20
RECOVERY_TIMEOUT = 60
VERIFY_TIMEOUT = 30
SUMMARY = re.compile(r"^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$", re.MULTILINE)
PHASE = re.compile(r"^([A-Z][A-Z0-9_]*): (PASS|WARN|SKIP|FAIL)/([A-Z][A-Z0-9_]*) \(", re.MULTILINE)
CAPTURE_CONTRACT = AUTOMATED.parent / "Contracts" / "incident-acceptance.contract.json"
MAX_CAPTURE_OUTPUT_BYTES = 262144
MAX_CAPTURE_LINE_CHARS = 8192
RAW_PHASE = re.compile(r"^\[([A-Z][A-Z0-9_]*):(stdout|stderr)\] (.*)$")
CONTROL_SCOPES = frozenset(("DGN-007_CONTROL_AB", "DGN-007_CONTROL_BA", "DGN-007_CONTROL_AA"))
FAILURE_CODES = {
    "FAIL": frozenset(("FAIL_CONTRACT", "FAIL_SAFETY", "FAIL_STATE", "FAIL_TIMEOUT",
                       "FAIL_EXECUTION", "FAIL_CLEANUP", "FAIL_RESULT_CONTRACT")),
    "WARN": frozenset(("WARN_ENVIRONMENT_DETAIL_SUPPRESSED", "WARN_RESOURCE_PROBE_APPROXIMATE",
                       "WARN_EMPIRICAL_VARIANCE", "WARN_OPTIONAL_EVIDENCE_SKIPPED")),
    "SKIP": frozenset(("SKIP_VERSION", "SKIP_COMPATIBILITY_LEVEL", "SKIP_EDITION", "SKIP_PLATFORM",
                       "SKIP_PERMISSION", "SKIP_CONFIGURATION", "SKIP_RESOURCE_PROFILE",
                       "SKIP_MANUAL_APPROVAL", "SKIP_EVIDENCE_MISSING", "SKIP_TOOL_MISSING")),
}
FAILURE_PHASE = re.compile(r"([A-Z][A-Z0-9_]*): (FAIL|WARN|SKIP)/([A-Z][A-Z0-9_]*) "
                           r"\([0-9]{1,6}(?:\.[0-9]{1,6})?s\) - [^\r\n]*")
SQL_MESSAGE = re.compile(r"Msg ([1-9][0-9]{0,9}), Level ([0-9]{1,2}), State ([0-9]{1,3}), "
                         r"(?:Server [^,\r\n]{1,256}, )?(?:Procedure [^,\r\n]{1,256}, )?"
                         r"Line ([1-9][0-9]{0,6})(?: \[Batch Start Line [0-9]{1,7}\])?")
MAX_FAILURE_DIAGNOSTICS = 24


@dataclass(frozen=True)
class RunContract:
    """Unveränderlicher Scope mit eigenem Manifest und exakter Phasenmetadatenfolge."""

    scope: str
    manifest: Path
    phase_specs: tuple[tuple[str, str, str, int], ...]

    @property
    def expected_phases(self) -> tuple[str, ...]:
        return tuple(spec[0] for spec in self.phase_specs)


DATA_MODEL_CONTRACT = RunContract(
    scope=SCOPE,
    manifest=MANIFEST,
    phase_specs=(
        ("PREFLIGHT", "00_Preflight.sql", "master", 30),
        ("SETUP", "10_Setup.sql", "master", 90),
        ("DATA_ASSERTION", "40_Data_Assertion.sql", "target", 30),
        ("CLEANUP", "90_Cleanup.sql", "master", 60),
    ),
)
QUERY_STORE_WINDOWS_CONTRACT = RunContract(
    scope="DGN-007_QUERY_STORE_WINDOWS",
    manifest=AUTOMATED / "windows.manifest.json",
    phase_specs=(
        *DATA_MODEL_CONTRACT.phase_specs[:-1],
        ("QUERY_STORE_WINDOWS", "20_Query_Store_Windows.sql", "target", 150),
        DATA_MODEL_CONTRACT.phase_specs[-1],
    ),
)
PROFILE_COMPARISON_CONTRACT = RunContract(
    scope="DGN-007_PROFILE_COMPARISON",
    manifest=AUTOMATED / "profile-comparison.manifest.json",
    phase_specs=(
        *QUERY_STORE_WINDOWS_CONTRACT.phase_specs[:-1],
        ("PROFILE_COMPARISON", "30_Profile_Comparison.sql", "target", 10),
        QUERY_STORE_WINDOWS_CONTRACT.phase_specs[-1],
    ),
)
CONTROL_AB_CONTRACT = RunContract(
    scope="DGN-007_CONTROL_AB", manifest=AUTOMATED / "control-ab.manifest.json",
    phase_specs=(*DATA_MODEL_CONTRACT.phase_specs[:-1],
                 ("CONTROL_CONFIG", "15_Control_AB.sql", "target", 5),
                 ("CONTROL_WINDOWS", "21_Controlled_Query_Store_Windows.sql", "target", 150),
                 ("PROFILE_COMPARISON", "30_Profile_Comparison.sql", "target", 10),
                 ("CONTROL_EVIDENCE", "35_Control_Evidence.sql", "target", 10),
                 DATA_MODEL_CONTRACT.phase_specs[-1]),
)
CONTROL_BA_CONTRACT = RunContract(
    scope="DGN-007_CONTROL_BA", manifest=AUTOMATED / "control-ba.manifest.json",
    phase_specs=(*DATA_MODEL_CONTRACT.phase_specs[:-1],
                 ("CONTROL_CONFIG", "15_Control_BA.sql", "target", 5),
                 ("CONTROL_WINDOWS", "21_Controlled_Query_Store_Windows.sql", "target", 150),
                 ("PROFILE_COMPARISON", "30_Profile_Comparison.sql", "target", 10),
                 ("CONTROL_EVIDENCE", "35_Control_Evidence.sql", "target", 10),
                 DATA_MODEL_CONTRACT.phase_specs[-1]),
)
CONTROL_AA_CONTRACT = RunContract(
    scope="DGN-007_CONTROL_AA", manifest=AUTOMATED / "control-aa.manifest.json",
    phase_specs=(*DATA_MODEL_CONTRACT.phase_specs[:-1],
                 ("CONTROL_CONFIG", "15_Control_AA.sql", "target", 5),
                 ("CONTROL_WINDOWS", "21_Controlled_Query_Store_Windows.sql", "target", 150),
                 ("PROFILE_COMPARISON", "30_Profile_Comparison.sql", "target", 10),
                 ("CONTROL_EVIDENCE", "35_Control_Evidence.sql", "target", 10),
                 DATA_MODEL_CONTRACT.phase_specs[-1]),
)


KNOWN_CONTRACTS = (DATA_MODEL_CONTRACT, QUERY_STORE_WINDOWS_CONTRACT, PROFILE_COMPARISON_CONTRACT,
                   CONTROL_AB_CONTRACT, CONTROL_BA_CONTRACT, CONTROL_AA_CONTRACT)


def scope_contract(scope: str) -> RunContract:
    if scope == "data-model":
        return DATA_MODEL_CONTRACT
    if scope == "query-store-windows":
        return QUERY_STORE_WINDOWS_CONTRACT
    if scope == "profile-comparison":
        return PROFILE_COMPARISON_CONTRACT
    if scope == "control-ab":
        return CONTROL_AB_CONTRACT
    if scope == "control-ba":
        return CONTROL_BA_CONTRACT
    if scope == "control-aa":
        return CONTROL_AA_CONTRACT
    raise ValueError("Unbekannter DGN-007-AUTO-Scope")


class RunnerFailure(RuntimeError):
    """Nur ein fest definierter, datenschutzneutraler Fehlercode wird ausgegeben."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class RunResult:
    repetition: int
    outcome: str = "PASS"
    code: str = "OK"


def validate_manifest(*, contract: RunContract = DATA_MODEL_CONTRACT) -> None:
    """Ein geänderter Schnitt benötigt eine bewusste Anpassung des Runners."""
    manifest = load_manifest(contract.manifest)
    phases = (*manifest.phases, manifest.cleanup)
    if (manifest.demo_id != "DGN-007" or manifest.run_token != "AUTO"
            or manifest.safety_level != "YELLOW"
            or manifest.timeout_seconds != 180 or manifest.cleanup_timeout_seconds != 60
            or any(phase is None for phase in phases)):
        raise RunnerFailure("FAIL_CONTRACT")
    if tuple(phase.phase_id for phase in phases) != contract.expected_phases:
        raise RunnerFailure("FAIL_CONTRACT")
    for phase, (_, script, selector, timeout) in zip(phases, contract.phase_specs):
        if (phase.kind != "sql" or not phase.required or not phase.require_summary
                or phase.path != AUTOMATED / script or phase.database_selector != selector
                or phase.timeout_seconds != timeout):
            raise RunnerFailure("FAIL_CONTRACT")


def resolve_target(container: str) -> ExecutionTarget:
    """Bounded sqlcmd-Erkennung; kein implizites Ziel aus der Umgebung."""
    result = subprocess.run(
        ["docker", "exec", container, "sh", "-lc",
         "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then printf /opt/mssql-tools18/bin/sqlcmd; "
         "elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then printf /opt/mssql-tools/bin/sqlcmd; else exit 127; fi"],
        check=False, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=VERIFY_TIMEOUT,
    )
    if result.returncode != 0 or result.stdout.strip() not in {
        "/opt/mssql-tools18/bin/sqlcmd", "/opt/mssql-tools/bin/sqlcmd"
    }:
        raise RunnerFailure("FAIL_EXECUTION")
    return execution_target.docker_target(container=container, sqlcmd_path=result.stdout.strip())


def assert_empty_instance(target: ExecutionTarget) -> None:
    output = execution_target.run_sql(
        target, database="master", timeout_seconds=VERIFY_TIMEOUT,
        sql_text="SET NOCOUNT ON; "
        "DECLARE @EditionId int=TRY_CONVERT(int,SERVERPROPERTY('EditionID')); "
        "IF @EditionId IS NULL OR @EditionId NOT IN (-2117995310,-1785266663) "
        "THROW 51001,'FAIL_SAFETY',1; "
        "IF EXISTS(SELECT 1 FROM sys.databases WHERE database_id>4) "
        "THROW 51001,'FAIL_SAFETY',1; SELECT N'EMPTY_DEVELOPER';",
    )
    if output.strip() != "EMPTY_DEVELOPER":
        raise RunnerFailure("FAIL_SAFETY")


def assert_absent(target: ExecutionTarget) -> None:
    """Abwesenheit unabhängig von Harness-Summaries bestätigen."""
    output = execution_target.run_sql(
        target, database="master", timeout_seconds=VERIFY_TIMEOUT,
        sql_text=f"SET NOCOUNT ON; IF DB_ID(N'{DATABASE}') IS NOT NULL "
        "THROW 51004,'FAIL_CLEANUP',1; SELECT N'ABSENT';",
    )
    if output.strip() != "ABSENT":
        raise RunnerFailure("FAIL_CLEANUP")


def run_harness(target: ExecutionTarget, *, contract: RunContract = DATA_MODEL_CONTRACT,
                check_capture_projection: bool = False,
                check_phase_diagnostics: bool = False) -> SqlcmdResult:
    command = [sys.executable, str(FRAMEWORK / "run_demo.py"), str(contract.manifest),
               *target.connection_arguments(), "--confirm-isolated-lab"]
    if check_capture_projection or check_phase_diagnostics:
        if (contract not in KNOWN_CONTRACTS
                or (check_capture_projection and contract.scope not in CONTROL_SCOPES)):
            raise RunnerFailure("FAIL_CONTRACT")
        command.append("--show-output")
        command.insert(1, "-u")
        environment = dict(target.child_environment())
        environment["PYTHONUNBUFFERED"] = "1"
        process = start_sqlcmd(command, environment=environment)
        return collect_capture_process(process, command, contract=contract)
    return run_sqlcmd(command, timeout_seconds=HARNESS_TIMEOUT,
                      environment=target.child_environment())


def collect_capture_process(process, command: Sequence[str], *,
                            contract: RunContract = CONTROL_AB_CONTRACT) -> SqlcmdResult:
    """Beide private Harness-Pipes begrenzt im Speicher lesen.

    Höchstens 256 KiB UTF-8-Textausgabe über beide Pipes bleiben im Speicher;
    der Windows-Textreader normalisiert CRLF zu LF. Die Kindprozessausgabe
    erreicht weder Konsole noch Datei. Das gleiche
    äußere Zeitbudget und der vorhandene Prozessbaumabbruch bleiben wirksam.
    Ein Überschreiten der Grenze beendet den Kindprozess; die unabhängige
    Abwesenheits-/Recovery-Prüfung bleibt Aufgabe von run_one.
    """
    started = time.monotonic()
    output = {"stdout": [], "stderr": []}
    lock = threading.Lock()
    stopped = threading.Event()
    size = 0
    limited = False
    owned_descendants = set()

    def read_pipe(channel):
        nonlocal size, limited
        stream = getattr(process, channel)
        try:
            if os.name != "nt":
                descriptor = stream.fileno()
                os.set_blocking(descriptor, False)
                pending = b""
                while not stopped.is_set():
                    try:
                        chunk = os.read(descriptor, 1024)
                    except BlockingIOError:
                        stopped.wait(0.05)
                        continue
                    if not chunk:
                        if pending:
                            record(channel, pending.decode("utf-8", errors="replace"))
                        return
                    pending += chunk
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        record(channel, (line + b"\n").decode("utf-8", errors="replace"))
                    if len(pending) > MAX_CAPTURE_LINE_CHARS:
                        with lock:
                            limited = True
                            stopped.set()
                        return
                return
            while True:
                line = stream.readline(MAX_CAPTURE_LINE_CHARS + 1)
                if not line:
                    break
                record(channel, line)
                if stopped.is_set():
                    return
        except (OSError, ValueError):
            with lock:
                limited = True
                stopped.set()
        finally:
            stream.close()

    def record(channel, line):
        nonlocal size, limited
        with lock:
            size += len(line.encode("utf-8"))
            if len(line) > MAX_CAPTURE_LINE_CHARS or size > MAX_CAPTURE_OUTPUT_BYTES:
                limited = True
                stopped.set()
                return
            output[channel].append(line)

    readers = [threading.Thread(target=read_pipe, args=(channel,), daemon=True)
               for channel in ("stdout", "stderr")]
    timed_out = False
    def stop_owned_pipes():
        stopped.set()
        _terminate_process_tree(process)
        if sys.platform.startswith("linux"):
            # Nur zuvor beobachtete eigene Nachfahren mit gleicher Startzeit.
            # Keine PID-/PGID-Verwendung nach ungeprüftem Root-Ende.
            for pid, started in owned_descendants:
                identity = _linux_process_identity(pid)
                if identity is not None and identity[1] == started:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        if os.name == "nt":
            # Blockierte Windows-ReadFile-Aufrufe der eigenen Reader abbrechen.
            # Dies betrifft nur Threadhandles dieses Prozesses, keine Fremdziele.
            import ctypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.OpenThread.restype = ctypes.c_void_p
            kernel.OpenThread.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
            kernel.CancelSynchronousIo.argtypes = (ctypes.c_void_p,)
            kernel.GetProcessIdOfThread.argtypes = (ctypes.c_void_p,)
            kernel.GetProcessIdOfThread.restype = ctypes.c_uint32
            kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
            for reader in readers:
                if reader.is_alive() and reader.native_id is not None:
                    handle = kernel.OpenThread(0x0801, False, reader.native_id)
                    if handle:
                        try:
                            if kernel.GetProcessIdOfThread(handle) == os.getpid():
                                kernel.CancelSynchronousIo(handle)
                        finally:
                            kernel.CloseHandle(handle)

    try:
        for reader in readers:
            reader.start()
        while True:
            if sys.platform.startswith("linux"):
                owned_descendants.update(_linux_descendants(process.pid))
            if process.poll() is not None:
                break
            if stopped.is_set() or time.monotonic() - started >= HARNESS_TIMEOUT:
                timed_out = not stopped.is_set()
                stop_owned_pipes()
                break
            stopped.wait(0.05)
        process.wait(timeout=5)
        for reader in readers:
            reader.join(timeout=5)
        if any(reader.is_alive() for reader in readers):
            limited = True
            stop_owned_pipes()
            stopped.set()
            for reader in readers:
                reader.join(timeout=5)
    except BaseException:
        stop_owned_pipes()
        try:
            process.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            pass
        for reader in readers:
            reader.join(timeout=5)
        raise
    finally:
        if not any(reader.is_alive() for reader in readers):
            for channel in ("stdout", "stderr"):
                getattr(process, channel).close()
    if limited:
        known = reported_capture_failure("".join(output["stdout"]), "".join(output["stderr"]), contract=contract)
        if known == "FAIL_CLEANUP":
            raise RunnerFailure(known)
        if timed_out or known == "FAIL_TIMEOUT":
            raise RunnerFailure("FAIL_TIMEOUT")
        raise RunnerFailure("FAIL_CONTRACT")
    return SqlcmdResult(tuple(command), process.returncode, "".join(output["stdout"]),
                        "".join(output["stderr"]), timed_out, time.monotonic() - started)


def reported_capture_failure(stdout: str, stderr: str, *,
                             contract: RunContract = CONTROL_AB_CONTRACT) -> str | None:
    """Bekannte Statuscodes ausschließlich aus echten Statuskanälen gewinnen."""
    if contract not in KNOWN_CONTRACTS:
        return None
    phases = [phase for phase in PHASE.findall(stdout.replace("\r\n", "\n"))
              if phase[0] in contract.expected_phases]
    summaries = SUMMARY.findall(stdout.replace("\r\n", "\n"))
    for line in stderr.splitlines():
        match = RAW_PHASE.fullmatch(line)
        if match and match[1] in contract.expected_phases and match[2] == "stderr":
            summary = SUMMARY.fullmatch(match[3])
            if summary:
                phases.append((match[1], *summary.groups()))
    if any(phase == "CLEANUP" and (outcome, code) != ("PASS", "OK") for phase, outcome, code in phases):
        return "FAIL_CLEANUP"
    codes = [code for _, code in summaries] + [code for _, _, code in phases]
    if "FAIL_CLEANUP" in codes:
        return "FAIL_CLEANUP"
    if "FAIL_TIMEOUT" in codes:
        return "FAIL_TIMEOUT"
    return None


def _query_store_raw_diagnostics(result: SqlcmdResult, *, contract: RunContract) -> tuple[str, ...]:
    """Begrenzte numerische Rohfragmente nur aus einem tatsächlich fehlgeschlagenen SQL-Pfad."""
    if len((result.stdout + result.stderr).encode('utf-8')) > MAX_CAPTURE_OUTPUT_BYTES:
        return ()
    failures = {phase for phase, outcome, _ in PHASE.findall(result.stdout) if outcome == 'FAIL'}
    if contract.scope in CONTROL_SCOPES and failures == {'CONTROL_EVIDENCE'}:
        prefix, phase, label = 'DGN007_G13_RAW', 'CONTROL_EVIDENCE', 'G13_RAW'
        if result.stderr.count('DGN007_CONTROL_GUARD|G13') != 1:
            return ()
    elif failures in ({'QUERY_STORE_WINDOWS'}, {'CONTROL_WINDOWS'}):
        phase = next(iter(failures))
        if phase not in contract.expected_phases:
            return ()
        prefix, label = 'DGN007_SQL20_RAW', 'SQL20_RAW'
    else:
        return ()
    records = []
    for line in result.stderr.splitlines():
        if prefix not in line:
            continue
        raw = RAW_PHASE.fullmatch(line)
        if (raw is None or raw.groups()[:2] != (phase, 'stderr')
                or not raw[3].startswith(prefix + '|1|') or not raw[3].isascii()
                or len(raw[3]) > 512):
            return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
        records.append(raw[3].split('|'))
    if len(records) < 2 or records[0][:3] != [prefix, '1', 'BEGIN']:
        return ()
    begin, end = records[0], records[-1]
    if (len(begin) != 5 or len(end) != 4 or end[:3] != [prefix, '1', 'END']
            or begin[3] not in ('COMPLETE', 'OVERFLOW', 'INSUFFICIENT')
            or not re.fullmatch(r'[0-9]{1,2}', begin[4])
            or not re.fullmatch(r'[0-9]{1,2}', end[3])):
        return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    declared = int(begin[4])
    if begin[3] == 'INSUFFICIENT':
        if declared == 0 and int(end[3]) == 0 and len(records) == 2:
            return (f'DGN007_FAILURE|{label}|INSUFFICIENT|SOURCE',)
        return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    if begin[3] == 'OVERFLOW':
        if declared != 17 or int(end[3]) != 0 or len(records) != 18 + (2 if label == 'SQL20_RAW' else 0):
            return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
        return (f'DGN007_FAILURE|{label}|INSUFFICIENT|OVERFLOW',)
    if declared > 16 or int(end[3]) != declared:
        return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    middle = records[1:-1]
    windows = []
    if label == 'SQL20_RAW':
        windows, middle = middle[:2], middle[2:]
        if (len(windows) != 2 or any(len(row) != 7 or row[:3] != [prefix, '1', 'WINDOW']
                                     or row[3] != str(index)
                                     or any(not re.fullmatch(r'(?:N|[0-9]{1,19})', value)
                                            for value in row[4:])
                                     for index, row in enumerate(windows))):
            return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    if len(middle) != declared:
        return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    for index, row in enumerate(middle, 1):
        if (len(row) != 13 or row[:3] != [prefix, '1', 'ROW'] or row[3] != str(index)
                or row[4] not in ('0', '1')
                or any(not re.fullmatch(r'[0-9]{1,19}', value) for value in row[5:11])
                or any(not re.fullmatch(r'(?:N|[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{7})?(?:Z|\+00:00))', value) for value in row[11:])):
            return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    if windows:
        for window in (0, 1):
            regular_count = sum(int(row[10]) for row in middle if row[4] == str(window) and row[9] == '0')
            if int(windows[window][6]) != regular_count:
                return (f'DGN007_FAILURE|{label}|INSUFFICIENT|MALFORMED',)
    return (f'DGN007_FAILURE|{label}|COMPLETE|rows={declared}',
            *(f'DGN007_FAILURE|{label}|' + '|'.join(row[2:]) for row in (*windows, *middle)))


def capture_failure_diagnostics(result: SqlcmdResult, *, contract: RunContract) -> tuple[str, ...]:
    """Nur feste Statusfelder und positive Msg/Line-Zahlen; keine Rohtexte.

    Ausschließlich bekannte nicht erfolgreiche Harnessstatuszeilen öffnen die
    Diagnose. SQL-Zahlen benötigen zusätzlich dieselbe fehlgeschlagene Phase
    und den tatsächlichen stderr-Kanal. Die Funktion verändert keine Bewertung.
    """
    if (contract not in KNOWN_CONTRACTS
            or len((result.stdout + result.stderr).encode("utf-8")) > MAX_CAPTURE_OUTPUT_BYTES):
        return ()
    diagnostics: list[str] = []
    structured: list[str] = []
    messages: list[str] = []
    failed_phases: set[str] = set()
    guard_phase_failed = False

    def append(line):
        bucket = messages if '|SQL_MESSAGE|' in line else structured
        if line not in bucket:
            if '|SQL_GUARD|' in line:
                bucket.insert(0, line)
                del bucket[MAX_FAILURE_DIAGNOSTICS:]
            elif len(bucket) < MAX_FAILURE_DIAGNOSTICS:
                bucket.append(line)
        if line not in diagnostics and len(diagnostics) < MAX_FAILURE_DIAGNOSTICS:
            diagnostics.append(line)

    for line in result.stdout.splitlines():
        if len(line) > MAX_CAPTURE_LINE_CHARS:
            continue
        phase = FAILURE_PHASE.fullmatch(line)
        if phase and phase[1] in contract.expected_phases and phase[3] in FAILURE_CODES[phase[2]]:
            if phase[2] == "FAIL":
                failed_phases.add(phase[1])
            if contract.scope in CONTROL_SCOPES and phase[1] == "CONTROL_EVIDENCE" and phase[2] == "FAIL":
                guard_phase_failed = True
            append(f"DGN007_FAILURE|OUTER_PHASE|{phase[1]}|{phase[2]}|{phase[3]}")
        summary = SUMMARY.fullmatch(line)
        if summary and summary[1] in FAILURE_CODES and summary[2] in FAILURE_CODES[summary[1]]:
            append(f"DGN007_FAILURE|OUTER_SUMMARY|{summary[1]}|{summary[2]}")
    if not diagnostics:
        return ()
    raw_lines = result.stderr.splitlines()
    guards = []
    for position, line in enumerate(raw_lines):
        if len(line) > MAX_CAPTURE_LINE_CHARS:
            continue
        raw = RAW_PHASE.fullmatch(line)
        if raw and raw[3].startswith("DGN007_CONTROL_GUARD"):
            guards.append((position, raw))
        if not raw or raw[1] not in failed_phases or raw[2] != "stderr":
            continue
        summary = SUMMARY.fullmatch(raw[3])
        if summary and summary[1] in FAILURE_CODES and summary[2] in FAILURE_CODES[summary[1]]:
            append(f"DGN007_FAILURE|SQL_STATUS|{raw[1]}|{summary[1]}|{summary[2]}")
        message = SQL_MESSAGE.fullmatch(raw[3])
        if message:
            number, level, state, line_number = (int(value) for value in message.groups())
            if number <= 2147483647 and 1 <= level <= 25 and state <= 255 and line_number <= 1000000:
                append(f"DGN007_FAILURE|SQL_MESSAGE|{raw[1]}|msg={number}; line={line_number}")
    if (guard_phase_failed and len(guards) == 1
            and result.stderr.count("DGN007_CONTROL_GUARD") == 1
            and "DGN007_CONTROL_GUARD" not in result.stdout
            and all(len(line) <= MAX_CAPTURE_LINE_CHARS for line in raw_lines)):
        position, raw = guards[0]
        guard = re.fullmatch(r"DGN007_CONTROL_GUARD\|(G(?:0[1-9]|1[0-7]))", raw[3])
        following = None
        for line in raw_lines[position + 1:]:
            following = RAW_PHASE.fullmatch(line) if len(line) <= MAX_CAPTURE_LINE_CHARS else None
            if (following is None or following.groups()[:2] != ("CONTROL_EVIDENCE", "stderr")
                    or following[3] != ""):
                break
        if (guard and raw.groups()[:2] == ("CONTROL_EVIDENCE", "stderr") and following
                and following.groups()[:2] == ("CONTROL_EVIDENCE", "stderr")
                and following[3] == "SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT"):
            append(f"DGN007_FAILURE|SQL_GUARD|CONTROL_EVIDENCE|{guard[1]}")
    raw = _query_store_raw_diagnostics(result, contract=contract)
    if raw:
        # Feste Statusfelder und begrenzte Rohbelege vor Msg/Line reservieren.
        diagnostics = structured[:MAX_FAILURE_DIAGNOSTICS - len(raw)] + list(raw)
        diagnostics.extend(messages[:MAX_FAILURE_DIAGNOSTICS - len(diagnostics)])
    return tuple(diagnostics)


def check_capture(result: SqlcmdResult, *, contract: RunContract, expected_major: int,
                  expected_contract) -> tuple[int, int, int, int, int]:
    """Nur CONTROL_EVIDENCE-stderr-Frames decodieren; keine RunRecords bilden.

    Der Harness verpackt jede SQL-Zeile mit Phase und Kanal. Alle zusätzlichen
    SQL-Summaries werden exakt an ihre Phase gebunden und ebenfalls geprüft.
    Der Body bleibt lokal; ausgegeben werden ausschließlich feste Counts.
    """
    combined = "\n".join((result.stdout, result.stderr)).replace("\r\n", "\n")
    # Die bestehende Terminalprüfung bewahrt Cleanup-/Timeoutpriorität.
    raw_summaries = []
    frames = []
    invalid = False
    frame_started = False
    frame_finished = False
    harness_failure = None
    try:
        check_harness(result, contract=contract)
    except RunnerFailure as error:
        harness_failure = error.code
    if len(combined.encode("utf-8")) > MAX_CAPTURE_OUTPUT_BYTES:
        known = reported_capture_failure(result.stdout, result.stderr, contract=contract)
        if known == "FAIL_CLEANUP":
            raise RunnerFailure(known)
        if known == "FAIL_TIMEOUT" or result.timed_out:
            raise RunnerFailure("FAIL_TIMEOUT")
        raise RunnerFailure("FAIL_CONTRACT")
    for pipe_channel, line in [(channel, line) for channel, output in (("stdout", result.stdout), ("stderr", result.stderr))
                               for line in output.splitlines()]:
        match = RAW_PHASE.fullmatch(line)
        if match is None:
            if "DGN007_CAPTURE_FRAME" in line or line.startswith("["):
                invalid = True
            continue
        phase, channel, payload = match.groups()
        if channel != pipe_channel:
            invalid = True
        if phase not in contract.expected_phases:
            invalid = True
        summary = SUMMARY.fullmatch(payload) if phase in contract.expected_phases and channel == pipe_channel else None
        if summary is not None:
            if channel != "stderr":
                invalid = True
            raw_summaries.append((phase, *summary.groups()))
            if phase == "CONTROL_EVIDENCE":
                frame_finished = True
        if "DGN007_CAPTURE_FRAME" in payload:
            if (phase != "CONTROL_EVIDENCE" or channel != "stderr"
                    or not payload.startswith("DGN007_CAPTURE_FRAME|") or frame_finished):
                invalid = True
            frames.append(payload)
            frame_started = True
        elif phase == "CONTROL_EVIDENCE" and frame_started and summary is None:
            invalid = True
    if any(phase == "CLEANUP" and (outcome, code) != ("PASS", "OK")
           for phase, outcome, code in raw_summaries):
        raise RunnerFailure("FAIL_CLEANUP")
    if harness_failure == "FAIL_CLEANUP":
        raise RunnerFailure("FAIL_CLEANUP")
    if harness_failure == "FAIL_TIMEOUT" or any(code == "FAIL_TIMEOUT" for _, _, code in raw_summaries):
        raise RunnerFailure("FAIL_TIMEOUT")
    if harness_failure is not None:
        raise RunnerFailure(harness_failure)
    if (invalid or contract.scope not in CONTROL_SCOPES or raw_summaries != [
            (phase, "PASS", "OK") for phase in contract.expected_phases]):
        raise RunnerFailure("FAIL_CONTRACT")
    failure = None
    try:
        body = decode_projection(tuple(frames), expected_contract)
    except ProjectionError as error:
        failure = error.code
    if failure is not None:
        raise RunnerFailure(failure)
    if (body.major != expected_major or body.compatibility != expected_major * 10
            or body.scope != contract.scope or not body.row_evidence_complete):
        raise RunnerFailure("FAIL_RESULT_CONTRACT")
    return (len(body.windows), len(body.requests), len(body.families), len(body.plans), len(body.plan_union))


def check_harness(result: SqlcmdResult, *, contract: RunContract = DATA_MODEL_CONTRACT) -> None:
    combined = "\n".join((result.stdout, result.stderr)).replace("\r\n", "\n")
    phases = PHASE.findall(combined)
    # Cleanup hat Vorrang, auch wenn der Harness einen früheren Fehler aggregiert.
    if any(phase == "CLEANUP" and (outcome, code) != ("PASS", "OK")
           for phase, outcome, code in phases):
        raise RunnerFailure("FAIL_CLEANUP")
    summaries = SUMMARY.findall(combined)
    if any(code == "FAIL_CLEANUP" for _, code in summaries):
        raise RunnerFailure("FAIL_CLEANUP")
    if result.timed_out or any(code == "FAIL_TIMEOUT" for _, code in summaries + [(o, c) for _, o, c in phases]):
        raise RunnerFailure("FAIL_TIMEOUT")
    if result.returncode != 0:
        raise RunnerFailure("FAIL_EXECUTION")
    if summaries != [("PASS", "OK")] or phases != [
        (phase, "PASS", "OK") for phase in contract.expected_phases
    ]:
        raise RunnerFailure("FAIL_CONTRACT")


def recover(target: ExecutionTarget) -> None:
    """Ausschließlich den bestehenden, vollständig markergebundenen Batch verwenden."""
    command = build_sqlcmd_command(
        executable=str(target.shim), server=target.server, database="master",
        script=AUTOMATED / "90_Cleanup.sql", auth=target.auth, username=target.username,
        variables={"DemoId": "DGN-007", "RunToken": "AUTO", "TargetDatabase": DATABASE,
                   "ConfirmIsolatedLab": "1", "HighImpactConfirmed": "1"},
    )
    result = run_sqlcmd(command, timeout_seconds=RECOVERY_TIMEOUT,
                      environment=target.child_environment())
    summaries = SUMMARY.findall("\n".join((result.stdout, result.stderr)).replace("\r\n", "\n"))
    if not result.succeeded or summaries != [("PASS", "OK")]:
        raise RunnerFailure("FAIL_CLEANUP")


def run_one(target: ExecutionTarget, repetition: int, *, contract: RunContract = DATA_MODEL_CONTRACT,
            check_capture_projection: bool = False, expected_major: int | None = None,
            expected_contract=None, check_phase_diagnostics: bool = False) -> RunResult:
    failure: RunnerFailure | None = None
    result: SqlcmdResult | None = None
    try:
        if check_capture_projection:
            if contract.scope not in CONTROL_SCOPES or expected_major not in (15, 16, 17) or expected_contract is None:
                raise RunnerFailure("FAIL_CONTRACT")
            if check_phase_diagnostics:
                result = run_harness(target, contract=contract, check_capture_projection=True,
                                     check_phase_diagnostics=True)
            else:
                result = run_harness(target, contract=contract, check_capture_projection=True)
            counts = check_capture(result, contract=contract, expected_major=expected_major,
                                   expected_contract=expected_contract)
            print(f"DGN007_CAPTURE|{contract.scope}|RUN_{repetition}|PASS|OK|windows={counts[0]}; requests={counts[1]}; families={counts[2]}; plans={counts[3]}; union={counts[4]}")
        else:
            if check_phase_diagnostics:
                result = run_harness(target, contract=contract, check_phase_diagnostics=True)
            else:
                result = run_harness(target, contract=contract)
            check_harness(result, contract=contract)
    except RunnerFailure as exc:
        failure = exc
    except subprocess.TimeoutExpired:
        failure = RunnerFailure("FAIL_TIMEOUT")
    except (ExecutionTargetError, OSError, ValueError, KeyboardInterrupt):
        failure = RunnerFailure("FAIL_EXECUTION")
    finally:
        cleanup_failed = False
        try:
            assert_absent(target)
        except (RunnerFailure, ExecutionTargetError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt):
            cleanup_failed = True
            # Auch bei fehlgeschlagener Recovery die unabhängige Prüfung ausführen.
            try:
                recover(target)
            except (RunnerFailure, ExecutionTargetError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt):
                pass
            finally:
                try:
                    assert_absent(target)
                except (RunnerFailure, ExecutionTargetError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt):
                    pass
        if cleanup_failed or (failure is not None and failure.code == "FAIL_CLEANUP"):
            failure = RunnerFailure("FAIL_CLEANUP")
        cleanup_outcome = "FAIL|FAIL_CLEANUP" if failure and failure.code == "FAIL_CLEANUP" else "PASS|OK"
        print(f"DGN007_CLEANUP|RUN_{repetition}|{cleanup_outcome}")
    if failure:
        if result is not None:
            for diagnostic in capture_failure_diagnostics(result, contract=contract):
                print(diagnostic)
        print(f"DGN007_STAGE|{contract.scope}|RUN_{repetition}|FAIL|{failure.code}")
        raise failure
    print(f"DGN007_STAGE|{contract.scope}|RUN_{repetition}|PASS|OK")
    return RunResult(repetition)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ausgewählten DGN-007-AUTO-Schnitt zweimal auf einer leeren Docker-Wegwerfinstanz prüfen.")
    parser.add_argument("--scope", choices=("data-model", "query-store-windows", "profile-comparison", "control-ab", "control-ba", "control-aa"), default="data-model")
    parser.add_argument("--target", choices=(execution_target.DOCKER,), default=execution_target.DOCKER)
    parser.add_argument("--check-capture-projection", action="store_true",
                        help="Skalare SQL-Projektion nur bei control-ab/ba/aa intern prüfen; keine Incidentbewertung oder Rohoutputausgabe.")
    parser.add_argument("--check-phase-diagnostics", action="store_true",
                        help="SQL-Phasenausgabe für alle sechs Scopes privat begrenzt lesen; bei Fehler nur geprüfte Status-/Msg-/Line-Metadaten ausgeben.")
    parser.add_argument("--container", required=True)
    parser.add_argument("--expected-major", type=int, choices=(15, 16, 17), required=True)
    parser.add_argument("--confirm-disposable-instance", action="store_true",
                        help="Isolierte Wegwerfinstanz, gelben Lab-Lauf und markergebundenen AUTO-Datenbankabbau bestätigen.")
    parser.add_argument("--confirm-isolated-lab", action="store_true",
                        help="Zusätzliche Lab-Bestätigung; --confirm-disposable-instance bleibt erforderlich.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    contract = scope_contract(args.scope)
    runs = 0
    code = "OK"
    try:
        if not args.confirm_disposable_instance:
            raise RunnerFailure("FAIL_SAFETY")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", args.container):
            raise RunnerFailure("FAIL_CONTRACT")
        if not os.environ.get("SQLCMDPASSWORD"):
            raise RunnerFailure("FAIL_SAFETY")
        expected_contract = None
        if args.check_capture_projection:
            if contract.scope not in CONTROL_SCOPES:
                raise RunnerFailure("FAIL_CONTRACT")
            try:
                expected_contract = contract_from_mapping(json.loads(CAPTURE_CONTRACT.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                raise RunnerFailure("FAIL_CONTRACT") from None
        validate_manifest(contract=contract)
        target = resolve_target(args.container)
        execution_target.verify_engine(target, expected_major=args.expected_major)
        assert_empty_instance(target)
        for repetition in (1, 2):
            if args.check_capture_projection:
                if args.check_phase_diagnostics:
                    run_one(target, repetition, contract=contract, check_capture_projection=True,
                            expected_major=args.expected_major, expected_contract=expected_contract,
                            check_phase_diagnostics=True)
                else:
                    run_one(target, repetition, contract=contract, check_capture_projection=True,
                            expected_major=args.expected_major, expected_contract=expected_contract)
            elif args.check_phase_diagnostics:
                run_one(target, repetition, contract=contract, check_phase_diagnostics=True)
            else:
                run_one(target, repetition, contract=contract)
            runs += 1
    except RunnerFailure as exc:
        code = exc.code
    except subprocess.TimeoutExpired:
        code = "FAIL_TIMEOUT"
    except (ExecutionTargetError, OSError, ValueError, KeyboardInterrupt):
        code = "FAIL_EXECUTION"
    outcome = "PASS" if code == "OK" and runs == 2 else "FAIL"
    print(f"DGN007_SUMMARY|{outcome}|{code}|major={args.expected_major}; runs={runs}; target=docker; scope={contract.scope}")
    return 0 if outcome == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
