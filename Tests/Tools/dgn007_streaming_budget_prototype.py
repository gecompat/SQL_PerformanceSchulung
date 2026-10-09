"""Offline-Prototyp: begrenzte Aufnahme, kumulative Kosten und eigene Linux-Kinder.

PROJECT_SEMANTIC, keine SQL-/Bundle-/Launcherintegration oder Methodenattestation.
Limits sind Prototypgrenzen, keine Änderung eines SQL-Vertrags. Der private Linux-
Adapter darf nur im frischen --synthetic-worker-Testinterpreter laufen. Er begrenzt
User-space-Aufnahme; Popen-Erzeugung, Kernelpuffer und Scheduling sind nicht hart
zeit-/speicherbeschränkt. Synthetische Reports enthalten keine aufgenommenen Bytes.
"""

from dataclasses import dataclass
from enum import Enum
import codecs
import ctypes
import json
import os
import selectors
import signal
import subprocess
import sys
import threading
import time


NS = 1_000_000_000
MAX_INPUT = 16_384
MAX_READ = 16_384
MAX_OUTPUT = 131_072
_WORKER_AUTHORIZED = False


class _ClockError(Exception):
    pass


class _AdapterUnsupported(Exception):
    pass


class Exit(Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Issue(Enum):
    INVALID = "INVALID_RECORD"
    CLOCK = "INVALID_CLOCK"
    INPUT = "INPUT_LIMIT"
    OUTPUT = "OUTPUT_LIMIT"
    LINE = "LINE_LIMIT"
    TEXT = "INVALID_UTF8"
    STEPS = "IO_STEP_LIMIT"
    STALLED = "NO_PROGRESS_LIMIT"
    POLLS = "SEMANTIC_POLL_LIMIT"
    ATTEMPTS = "ACQUISITION_LIMIT"
    COST = "ACTIVE_COST_LIMIT"
    ACQUIRE_COST = "ACQUISITION_COST_LIMIT"
    TIMEOUT = "TIMEOUT"
    CHILD = "CHILD_FAILURE"
    ADAPTER = "ADAPTER_FAILURE"
    CLEANUP = "CLEANUP_FAILURE"
    UNSUPPORTED = "UNSUPPORTED_PLATFORM"
    ISOLATION = "WORKER_ISOLATION_FAILURE"


@dataclass(frozen=True)
class Limits:
    output_bytes: int = MAX_OUTPUT
    read_bytes: int = MAX_READ
    line_bytes: int = 8192
    io_steps: int = 4096
    no_progress_steps: int = 128
    phase_ns: int = 145 * NS
    regular_ns: int = 180 * NS
    active_ns: int = 20 * NS
    acquire_ns: int = 2 * NS
    cleanup_ns: int = 60 * NS


@dataclass(frozen=True)
class Step:
    channel: str = ""
    data: bytes = b""
    eof: bool = False
    exit: Exit = Exit.RUNNING
    input_complete: bool = False
    acquisition_stage: int = 0  # 0: IO only; 1..8: declared synthetic acquisition.
    semantic_poll: bool = False
    sleep_ns: int = 0


@dataclass(frozen=True)
class CleanupReceipt:
    initial_success: bool
    stopped: bool
    reaped: bool
    absent: bool
    pipes_closed: bool
    restored: bool


@dataclass(frozen=True)
class Report:
    success: bool
    issues: tuple[Issue, ...]
    observed_bytes: int = 0
    retained_bytes: int = 0
    input_written: bool = False
    stdout_eof: bool = False
    stderr_eof: bool = False
    io_steps: int = 0
    semantic_polls: int = 0
    acquisitions: int = 0
    active_ns: int = 0
    sleep_ns: int = 0
    elapsed_ns: int = 0
    cleanup_ns: int = 0
    scope: str = "PROJECT_SEMANTIC"
    runtime_attested: bool = False
    method_approved: bool = False
    cleanup_complete: bool = False


def _integer(value, lower, upper):
    return type(value) is int and lower <= value <= upper


def _limits(value):
    if type(value) is not Limits or set(vars(value)) != set(Limits.__dataclass_fields__):
        return False
    bounds = {"output_bytes": MAX_OUTPUT, "read_bytes": MAX_READ,
              "line_bytes": 8192, "io_steps": 4096, "no_progress_steps": 128,
              "phase_ns": 145 * NS, "regular_ns": 180 * NS,
              "active_ns": 20 * NS, "acquire_ns": 2 * NS, "cleanup_ns": 60 * NS}
    return all(_integer(getattr(value, key, None), 1, bound) for key, bound in bounds.items())


def _step(value, requested):
    return (type(value) is Step and set(vars(value)) == set(Step.__dataclass_fields__)
            and type(getattr(value, "channel", None)) is str
            and value.channel in ("", "stdout", "stderr")
            and type(getattr(value, "data", None)) is bytes and len(value.data) <= requested
            and type(getattr(value, "eof", None)) is bool
            and type(getattr(value, "input_complete", None)) is bool
            and type(getattr(value, "exit", None)) is Exit and value.exit in tuple(Exit)
            and _integer(getattr(value, "acquisition_stage", None), 0, 8)
            and type(getattr(value, "semantic_poll", None)) is bool
            and _integer(getattr(value, "sleep_ns", None), 0, NS)
            and (value.channel != "" or (not value.data and not value.eof)))


def run_budget(adapter, clock, input_bytes, limits=Limits()):
    """Trusted adapter.start/step(max_bytes)/pause(ns)/cleanup(deadline) protocol.

    A step cannot deliver more than its requested bytes, including one bounded
    overflow sentinel. Acquisitions are atomic synthetic steps; IO steps and sleeps
    are separate. Every attempted acquisition counts even if it fails afterwards.
    No adapter bytes, exception messages or decoded strings are returned.
    """
    if not _limits(limits):
        return Report(False, (Issue.INVALID,))
    if type(input_bytes) is not bytes or len(input_bytes) > MAX_INPUT:
        return Report(False, (Issue.INPUT,))
    issues = []
    last = None

    def now():
        nonlocal last
        value = clock()
        if not _integer(value, 0, 2**63 - 1) or (last is not None and value < last):
            raise _ClockError
        last = value
        return value

    def add(issue):
        if issue not in issues:
            issues.append(issue)

    try:
        start = now()
    except Exception:
        return Report(False, (Issue.CLOCK,))
    deadline = start + min(limits.phase_ns, limits.regular_ns)
    active = sleep = observed = retained = steps = polls = acquisitions = stalled = 0
    attempts = [0] * 8
    eof = {"stdout": False, "stderr": False}
    partial = {"stdout": 0, "stderr": 0}
    decoders = {key: codecs.getincrementaldecoder("utf-8")("strict") for key in eof}
    written = exited = False
    started = False
    finish = start
    cleanup_elapsed = 0
    pending_sleep = None
    try:
        started = True  # start may partially create resources; cleanup remains mandatory.
        adapter.start(input_bytes)
        after = now()
        active = after - start
        while not issues:
            before = now()
            active = before - start - sleep
            if before >= deadline:
                add(Issue.TIMEOUT)
                break
            if active > limits.active_ns:
                add(Issue.COST)
                break
            if steps >= limits.io_steps:
                add(Issue.STEPS)
                break
            requested = min(limits.read_bytes, limits.output_bytes - observed + 1)
            value = adapter.step(requested)
            after = now()
            cost = after - before
            active = after - start - sleep
            steps += 1
            if not _step(value, requested):
                add(Issue.INVALID)
                break
            if value.acquisition_stage:
                index = value.acquisition_stage - 1
                attempts[index] += 1
                acquisitions += 1
                if attempts[index] > 2:
                    add(Issue.ATTEMPTS)
                if cost > limits.acquire_ns:
                    add(Issue.ACQUIRE_COST)
            if value.semantic_poll:
                polls += 1
                if polls > 64:
                    add(Issue.POLLS)
            if (value.data or value.eof or (value.exit is Exit.SUCCESS and not exited)
                    or value.input_complete != written):
                stalled = 0
            else:
                stalled += 1
                if stalled > limits.no_progress_steps:
                    add(Issue.STALLED)
            if written and not value.input_complete:
                add(Issue.INVALID)
            if exited and value.exit is Exit.RUNNING:
                add(Issue.INVALID)
            written = written or value.input_complete
            if value.channel:
                channel = value.channel
                if eof[channel]:
                    add(Issue.INVALID)
                observed += len(value.data)
                if observed > limits.output_bytes:
                    add(Issue.OUTPUT)  # before decode/retention; no partial overflow retain.
                if not issues:
                    for byte in value.data:
                        partial[channel] = 0 if byte == 10 else partial[channel] + 1
                        if partial[channel] > limits.line_bytes:
                            add(Issue.LINE)
                            break
                    if not issues:
                        decoders[channel].decode(value.data, final=value.eof)
                        retained += len(value.data)
                        eof[channel] = value.eof
            if value.exit is Exit.FAILURE:
                add(Issue.CHILD)
            exited = exited or value.exit is Exit.SUCCESS
            parsed = now()
            active = parsed - start - sleep
            if value.acquisition_stage and parsed - before > limits.acquire_ns:
                add(Issue.ACQUIRE_COST)
            if parsed >= deadline:
                add(Issue.TIMEOUT)
            if active > limits.active_ns:
                add(Issue.COST)
            if issues:
                break
            if exited and written and all(eof.values()):
                # Separate final check, never infer drain from leader exit.
                if now() >= deadline:
                    add(Issue.TIMEOUT)
                active = last - start - sleep
                if active > limits.active_ns:
                    add(Issue.COST)
                break
            if value.sleep_ns:
                before_sleep = now()
                pending_sleep = before_sleep
                adapter.pause(value.sleep_ns)
                after_sleep = now()
                sleep += after_sleep - before_sleep
                pending_sleep = None
                active = after_sleep - start - sleep
                if after_sleep >= deadline:
                    add(Issue.TIMEOUT)
        finish = now()
        active = finish - start - sleep
        if finish >= deadline:
            add(Issue.TIMEOUT)
        if active > limits.active_ns:
            add(Issue.COST)
    except UnicodeError:
        add(Issue.TEXT)
    except _AdapterUnsupported:
        add(Issue.UNSUPPORTED)
    except _ClockError:
        add(Issue.CLOCK)
    except Exception:
        add(Issue.ADAPTER)
    finally:
        finish = max(finish, last if last is not None else start)
        if started:
            try:
                try:
                    cleanup_start = now()
                except Exception:
                    add(Issue.CLOCK)
                    add(Issue.CLEANUP)  # unverifiable clock; still attempt owned cleanup.
                    cleanup_start = last
                # Charge failed/aborted operations too, before the separate cleanup clock.
                finish = cleanup_start
                if pending_sleep is not None:
                    sleep += max(0, finish - pending_sleep)
                active = max(0, finish - start - sleep)
                if finish >= deadline:
                    add(Issue.TIMEOUT)
                if active > limits.active_ns:
                    add(Issue.COST)
                receipt = adapter.cleanup(cleanup_start + limits.cleanup_ns)
                cleanup_finish = now()
                cleanup_elapsed = cleanup_finish - cleanup_start
                fields = ("initial_success", "stopped", "reaped", "absent", "pipes_closed", "restored")
                if (type(receipt) is not CleanupReceipt
                        or set(vars(receipt)) != set(CleanupReceipt.__dataclass_fields__)
                        or not all(type(getattr(receipt, key, None)) is bool
                                   and getattr(receipt, key) for key in fields)
                        or cleanup_elapsed > limits.cleanup_ns):
                    add(Issue.CLEANUP)
            except Exception:
                add(Issue.CLEANUP)
    if Issue.CLEANUP in issues:
        issues.remove(Issue.CLEANUP)
        issues.insert(0, Issue.CLEANUP)
    return Report(not issues, tuple(issues), observed, retained, written, eof["stdout"],
                  eof["stderr"], steps, polls, acquisitions, active, sleep,
                  max(0, finish - start), cleanup_elapsed,
                  cleanup_complete=started and Issue.CLEANUP not in issues)


class Scenario(Enum):
    SPLIT = "split"
    BOTH = "both"
    FLOOD = "flood"
    INVALID = "invalid"
    BACKPRESSURE = "backpressure"
    INHERITED_PIPE = "inherited-pipe"


# Fixed source, not a candidate path/argv interpreter. Fork never changes session.
_CHILD = r"""
import os, sys, time
scenario = sys.argv[1]
if scenario == 'backpressure':
    time.sleep(3)
elif scenario == 'inherited-pipe':
    if os.fork() == 0:
        time.sleep(3)
        os._exit(0)
    os._exit(0)
else:
    while os.read(0, 4096):
        pass
    if scenario == 'split':
        for part in (b'\xe2', b'\x82', b'\xac\r', b'\n'):
            os.write(1, part)
            time.sleep(.005)
    elif scenario == 'both':
        os.write(1, b'out\r\n')
        os.write(2, b'err\n')
    elif scenario == 'flood':
        for i in range(64):
            os.write(1 if i % 2 else 2, b'x' * 4095 + b'\n')
    elif scenario == 'invalid':
        os.write(1, b'\xff')
"""


class _LinuxAdapter:
    """Single-threaded, private fresh-worker adapter; no descendant discovery."""

    def __init__(self, scenario):
        self.scenario = scenario
        self.process = None
        self.selector = selectors.DefaultSelector()
        self.offset = 0
        self.input = b""
        self.previous = None
        self.libc = None

    def start(self, input_bytes):
        if (not _WORKER_AUTHORIZED or __name__ != "__main__" or not sys.flags.isolated
                or not sys.flags.no_site or sys.platform != "linux" or type(self.scenario) is not Scenario
                or threading.active_count() != 1 or signal.getsignal(signal.SIGCHLD) is not signal.SIG_DFL):
            raise RuntimeError
        # ECHILD means no children; None is an existing running child. Never reap it.
        try:
            os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        except ChildProcessError:
            pass
        else:
            raise RuntimeError
        self.libc = ctypes.CDLL(None, use_errno=True)
        old = ctypes.c_int()
        if self.libc.prctl(37, ctypes.byref(old), 0, 0, 0) != 0:
            raise RuntimeError
        self.previous = old.value
        if self.libc.prctl(36, 1, 0, 0, 0) != 0:
            raise RuntimeError
        self.input = input_bytes
        self.process = subprocess.Popen(
            [sys.executable, "-I", "-S", "-c", _CHILD, self.scenario.value],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            bufsize=0, start_new_session=True, env={"LANG": "C", "LC_ALL": "C"})
        if self.scenario is Scenario.BACKPRESSURE:
            import fcntl
            # Own new pipe only; force backpressure below the validated 16KiB input.
            capacity = fcntl.fcntl(self.process.stdin.fileno(), fcntl.F_SETPIPE_SZ, 4096)
            if not _integer(capacity, 1, len(input_bytes) - 1):
                raise _AdapterUnsupported
        for stream, channel, event in ((self.process.stdout, "stdout", selectors.EVENT_READ),
                                       (self.process.stderr, "stderr", selectors.EVENT_READ),
                                       (self.process.stdin, "stdin", selectors.EVENT_WRITE)):
            os.set_blocking(stream.fileno(), False)
            self.selector.register(stream, event, channel)

    def _leader(self):
        # No poll/wait/communicate until cleanup's anchored group stop.
        info = os.waitid(os.P_PID, self.process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        if info is None:
            return Exit.RUNNING
        return Exit.SUCCESS if info.si_code == os.CLD_EXITED and info.si_status == 0 else Exit.FAILURE

    def step(self, requested):
        exited = self._leader()
        for key, _ in self.selector.select(0):
            if key.data == "stdin":
                if self.offset < len(self.input):
                    try:
                        self.offset += os.write(key.fd, self.input[self.offset:self.offset + 4096])
                    except BrokenPipeError:
                        self.selector.unregister(key.fileobj)
                        key.fileobj.close()
                        return Step(exit=Exit.FAILURE)
                if self.offset == len(self.input):
                    self.selector.unregister(key.fileobj)
                    key.fileobj.close()
                continue
            try:
                data = os.read(key.fd, requested)
            except BlockingIOError:
                continue
            end = not data
            if end:
                self.selector.unregister(key.fileobj)
                key.fileobj.close()
            return Step(key.data, data, end, exited, self.offset == len(self.input))
        return Step(exit=exited, input_complete=self.offset == len(self.input), sleep_ns=1_000_000)

    def pause(self, duration):
        time.sleep(duration / NS)

    def cleanup(self, deadline):
        stopped = reaped = absent = pipes = restored = False
        clean = True
        try:
            if self.process is None:
                stopped = reaped = absent = True
            else:
                pid = self.process.pid
                # WNOWAIT is also an identity proof for an already-exited leader.
                self._leader()
                if os.getpgid(pid) != pid:
                    raise RuntimeError
                os.killpg(pid, signal.SIGKILL)
                stopped = True
                self.process.wait(timeout=max(.001, (deadline - time.monotonic_ns()) / NS))
                for _ in range(4096):
                    if time.monotonic_ns() >= deadline:
                        break
                    try:
                        child, _ = os.waitpid(-pid, os.WNOHANG)
                    except ChildProcessError:
                        reaped = True
                        break
                    if child == 0:
                        time.sleep(.001)
                if reaped:
                    try:
                        os.killpg(pid, 0)  # presence check only; never signal after leader reap.
                    except ProcessLookupError:
                        absent = True
        except Exception:
            clean = False
        finally:
            try:
                self.selector.close()
                if self.process is not None:
                    for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
                        stream.close()
                pipes = True
            except Exception:
                clean = False
            try:
                if self.previous is None:
                    restored = True
                elif self.libc.prctl(36, self.previous, 0, 0, 0) == 0:
                    observed = ctypes.c_int()
                    restored = (self.libc.prctl(37, ctypes.byref(observed), 0, 0, 0) == 0
                                and observed.value == self.previous)
            except Exception:
                clean = False
        return CleanupReceipt(clean, stopped, reaped, absent, pipes, restored)


def _worker_entry(argv):
    global _WORKER_AUTHORIZED
    # Only fixed synthetics. Calling this module never runs repository candidates.
    if sys.platform != "linux":
        return Report(False, (Issue.UNSUPPORTED,))
    if len(argv) != 2 or argv[0] != "--synthetic-worker":
        return Report(False, (Issue.INVALID,))
    try:
        scenario = Scenario(argv[1])
    except ValueError:
        return Report(False, (Issue.INVALID,))
    _WORKER_AUTHORIZED = True
    limits = Limits(phase_ns=2 * NS, regular_ns=3 * NS, active_ns=NS, cleanup_ns=2 * NS,
                    no_progress_steps=128, io_steps=4096)
    data = b"i" * MAX_INPUT if scenario is Scenario.BACKPRESSURE else b"input\n"
    return run_budget(_LinuxAdapter(scenario), time.monotonic_ns, data, limits)


if __name__ == "__main__":
    result = _worker_entry(sys.argv[1:])
    # Fixed bounded metadata; no payload or exception detail in the outer worker pipe.
    print(json.dumps({"success": result.success, "issues": [item.value for item in result.issues],
                      "observed_bytes": result.observed_bytes, "retained_bytes": result.retained_bytes,
                      "stdout_eof": result.stdout_eof, "stderr_eof": result.stderr_eof,
                      "input_written": result.input_written, "scope": result.scope,
                      "runtime_attested": result.runtime_attested, "method_approved": result.method_approved,
                      "cleanup_complete": result.cleanup_complete},
                     separators=(",", ":")))
