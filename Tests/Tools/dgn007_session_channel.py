"""Eigener Linux-Abschlussweg mit echten Pipes; keine Import-/Ledgerfreigabe.

Nur im frischen privaten isolierten CPython-3.12-Worker verwenden. Geprüfte
nicht ausbrechende Programme und die Kontrollruntime sind Callerannahmen.
Öffentliche Reports sind Diagnosen, keine Ereignis- oder Replay-Authority.
"""
from dataclasses import dataclass, field
import ctypes
import os
import selectors
import signal
import subprocess
import sys
import threading
import time
from types import FunctionType

NS = 1_000_000_000
_ISSUES = frozenset(("CHANNEL_FORM", "CHANNEL_OWNER", "CHANNEL_PLATFORM", "CHANNEL_ISOLATION",
    "CHANNEL_BYTES", "CHANNEL_LINE", "CHANNEL_RECORDS", "CHANNEL_LINE_EOF", "CHANNEL_IO",
    "CHANNEL_STALLED", "CHANNEL_TIMEOUT", "CHANNEL_EXIT", "CHANNEL_MATCH", "CHANNEL_START_UNKNOWN",
    "CHANNEL_CLEANUP", "CHANNEL_INTERNAL", "HASH_PROVIDER_BINDING", "REPORT_ENCODER_BINDING"))


@dataclass(frozen=True, slots=True)
class ChannelLimits:
    output_bytes: int = 65536
    read_bytes: int = 4096
    io_steps: int = 4096
    no_progress: int = 64
    regular_ns: int = 20 * NS
    cleanup_ns: int = 10 * NS


@dataclass(frozen=True, slots=True, repr=False)
class ChannelSelection:
    program: bytes
    reported: tuple
    context: tuple


@dataclass(frozen=True, slots=True, repr=False)
class ChannelReport:
    status: str
    issue: str
    first_issue: str
    start_attempts: int = 0
    started: int = 0
    matched: int = 0
    closed: int = 0
    observed_bytes: int = 0
    io_steps: int = 0
    cleanup_attempts: int = 0
    cleanup_complete: bool = True
    stdout_eofs: int = 0
    stderr_eofs: int = 0
    zero_exits: int = 0
    eof_before_exit: int = 0
    exit_before_eofs: int = 0
    matches: tuple = field(default=(), repr=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)

    def __repr__(self):
        return "ChannelReport(PROJECT_SEMANTIC)"


class _Rejected(Exception):
    pass


def _need(ok, issue="CHANNEL_FORM"):
    if not ok:
        raise _Rejected(issue)


def _issue(error, fallback="CHANNEL_INTERNAL"):
    args = BaseException.__dict__["args"].__get__(error, BaseException)
    if (type(args) is tuple and len(args) == 1 and type(args[0]) is str
            and len(args[0]) <= 32 and args[0] in _ISSUES):
        return args[0]
    return fallback


def _dominant(first, later):
    priority = {"NONE": 0, "REPORT_ENCODER_BINDING": 2, "HASH_PROVIDER_BINDING": 3,
                "CHANNEL_CLEANUP": 4}
    return later if priority.get(later, 1) > priority.get(first, 1) else first


def _mapping(mapping):
    _need(type(mapping) is dict and len(mapping) <= 256, "CHANNEL_OWNER")
    keys = tuple(mapping)
    _need(all(type(key) is str for key in keys), "CHANNEL_OWNER")
    return tuple((key, mapping[key]) for key in keys)


def _same_mapping(mapping, snapshot):
    actual = _mapping(mapping)
    _need(len(actual) == len(snapshot) and all(a[0] == b[0] and a[1] is b[1]
          for a, b in zip(actual, snapshot)), "CHANNEL_OWNER")


class _Control:
    def __init__(self, namespace):
        self.namespace = namespace
        self.snapshot = _mapping(namespace)
        required = ("_inline_match_session_end", "_report_shape", "_command_context", "_semantic_worker",
                    "_report_encoder_anchor", "_semantic_provider_anchor", "_report_encoder_check",
                    "_semantic_provider_check")
        _need(all(type(namespace.get(key)) is FunctionType and namespace[key].__globals__ is namespace
                  for key in required), "CHANNEL_OWNER")
        self.functions, self.classes = [], []
        for _, value in self.snapshot:
            if type(value) is type and value.__module__ == "__main__":
                row = tuple(value.__dict__.items())
                self.classes.append((value, row, value.__bases__, value.__mro__))
                for _, method in row:
                    if type(method) is FunctionType:
                        self.functions.append(method)
            elif type(value) is FunctionType and value.__globals__ is namespace:
                self.functions.append(value)
        self.states = tuple((fn, fn.__code__, fn.__globals__, fn.__defaults__, fn.__kwdefaults__,
            None if fn.__kwdefaults__ is None else _mapping(fn.__kwdefaults__), fn.__closure__,
            tuple(cell.cell_contents for cell in fn.__closure__ or ())) for fn in self.functions)
        self.encoder = self.provider = None

    def pins(self):
        _same_mapping(self.namespace, self.snapshot)
        for cls, row, bases, mro in self.classes:
            actual = tuple(cls.__dict__.items())
            _need(cls.__bases__ is bases and cls.__mro__ is mro and len(actual) == len(row)
                  and all(a[0] == b[0] and a[1] is b[1] for a, b in zip(actual, row)), "CHANNEL_OWNER")
        for fn, code, glob, defaults, keywords, kw_values, closure, cells in self.states:
            _need(fn.__code__ is code and fn.__globals__ is glob and fn.__defaults__ is defaults
                  and fn.__kwdefaults__ is keywords and fn.__closure__ is closure, "CHANNEL_OWNER")
            if keywords is not None:
                _same_mapping(keywords, kw_values)
            _need(all(cell.cell_contents is old for cell, old in zip(closure or (), cells)), "CHANNEL_OWNER")

    def capture(self):
        self.pins()
        self.encoder = self.namespace["_report_encoder_anchor"]()
        self.provider = self.namespace["_semantic_provider_anchor"]()
        self.check()

    def check(self):
        # Bei verlorenen Kontrollpins keine fremden Helper mehr dispatchen.
        self.pins()
        encoder_lost = False
        if self.encoder is not None:
            try:
                self.namespace["_report_encoder_check"](self.encoder)
            except BaseException:
                encoder_lost = True
        if self.provider is not None:
            try:
                self.namespace["_semantic_provider_check"](self.provider)
            except BaseException:
                raise _Rejected("HASH_PROVIDER_BINDING") from None
        _need(not encoder_lost, "REPORT_ENCODER_BINDING")


class _Budget:
    def __init__(self, limits, start):
        self.limits, self.deadline = limits, start + limits.regular_ns
        self.bytes = self.io = self.quiet = self.cleanup = 0

    def check(self):
        _need(time.monotonic_ns() < self.deadline, "CHANNEL_TIMEOUT")

    def step(self):
        self.check()
        _need(self.io < self.limits.io_steps, "CHANNEL_IO")
        self.io += 1

    def book(self, data):
        self.bytes += len(data)
        _need(self.bytes <= self.limits.output_bytes, "CHANNEL_BYTES")

    def progress(self, progress):
        self.quiet = 0 if progress else self.quiet + 1
        _need(self.quiet < self.limits.no_progress, "CHANNEL_STALLED")


def _no_children():
    try:
        os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    except ChildProcessError:
        return True
    return False


def _platform():
    _need(sys.platform == "linux" and sys.version_info[:2] == (3, 12)
          and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, "CHANNEL_PLATFORM")
    _need(threading.active_count() == 1 and signal.getsignal(signal.SIGCHLD) is signal.SIG_DFL
          and _no_children(), "CHANNEL_ISOLATION")


class _Reaper:
    def __init__(self):
        self.libc = ctypes.CDLL(None, use_errno=True)
        self.previous = None

    def enable(self):
        old = ctypes.c_int()
        _need(self.libc.prctl(37, ctypes.byref(old), 0, 0, 0) == 0, "CHANNEL_ISOLATION")
        self.previous = old.value
        _need(self.libc.prctl(36, 1, 0, 0, 0) == 0, "CHANNEL_ISOLATION")

    def restore(self):
        if self.previous is None:
            return True
        if self.libc.prctl(36, self.previous, 0, 0, 0) != 0:
            return False
        observed = ctypes.c_int()
        return self.libc.prctl(37, ctypes.byref(observed), 0, 0, 0) == 0 and observed.value == self.previous


def _launch(program):
    return subprocess.Popen([sys.executable, "-I", "-S", "-B", "-u", "-c", program],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
        shell=False, start_new_session=True, env={"LANG": "C", "LC_ALL": "C"})


def _exit(process):
    info = os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    if info is None:
        return None
    _need(info.si_pid == process.pid, "CHANNEL_OWNER")
    return 0 if info.si_code == os.CLD_EXITED and info.si_status == 0 else 1


def _cleanup(process, selector, deadline):
    stopped = reaped = absent = pipes = False
    try:
        if process is None:
            stopped = reaped = absent = True
        else:
            _exit(process)  # WNOWAIT bleibt vor dem einzigen Signal erhalten.
            _need(os.getpgid(process.pid) == process.pid, "CHANNEL_OWNER")
            os.killpg(process.pid, signal.SIGKILL)
            stopped = True
            process.wait(timeout=max(0, (deadline - time.monotonic_ns()) / NS))
            for _ in range(4096):
                if time.monotonic_ns() >= deadline:
                    break
                try:
                    child, _ = os.waitpid(-process.pid, os.WNOHANG)
                except ChildProcessError:
                    reaped = True
                    break
                if child == 0:
                    time.sleep(.001)
            if reaped:
                try:
                    os.killpg(process.pid, 0)  # Nach Reap nur Anwesenheitsprüfung.
                except ProcessLookupError:
                    absent = True
    except BaseException:
        pass
    finally:
        try:
            if selector is not None:
                selector.close()
            if process is not None:
                process.stdout.close(); process.stderr.close()
                pipes = process.stdout.closed and process.stderr.closed
            else:
                pipes = True
        except BaseException:
            pass
    return stopped and reaped and absent and pipes


def _drain(process, selector, budget, control, observed):
    rows, pending, err = [], bytearray(), bytearray()
    eof = {"stdout": False, "stderr": False}
    seen_exit = None
    early_eof = early_exit = False
    while True:
        budget.check(); control.check()
        budget.step()
        code = _exit(process)
        progress = code is not None and seen_exit is None
        if code is not None:
            seen_exit = code
            observed["zero_exit"] = code == 0
            _need(code == 0, "CHANNEL_EXIT")
        early_exit |= seen_exit is not None and not all(eof.values())
        observed["exit_before_eofs"] = early_exit
        if all(eof.values()) and seen_exit is not None:
            break
        budget.step()
        events = selector.select(min(.02, max(0, (budget.deadline - time.monotonic_ns()) / NS)))
        if not selector.get_map():
            time.sleep(min(.02, max(0, (budget.deadline - time.monotonic_ns()) / NS)))
        for key, _ in events:
            budget.step()
            maximum = min(budget.limits.read_bytes, budget.limits.output_bytes - budget.bytes + 1)
            try:
                data = os.read(key.fd, maximum)
            except BlockingIOError:
                continue
            if not data:
                _need(not eof[key.data], "CHANNEL_OWNER")
                eof[key.data] = True; progress = True
                observed[key.data] = True
                selector.unregister(key.fileobj)
                if key.data == "stdout":
                    _need(not pending, "CHANNEL_LINE_EOF")
                continue
            progress = True
            budget.book(data)  # Vor Retention, Framing und jeder Dekodierung.
            if key.data == "stderr":
                err.extend(data)
            else:
                for byte in data:
                    _need(len(pending) < 1024, "CHANNEL_LINE")
                    pending.append(byte)
                    if byte == 10:
                        _need(len(rows) < 43, "CHANNEL_RECORDS")
                        rows.append(bytes(pending)); pending.clear()
        early_eof |= all(eof.values()) and seen_exit is None
        observed["eof_before_exit"] = early_eof
        budget.progress(progress)
    control.check(); budget.check()
    received = tuple(rows)
    result = control.namespace["_inline_match_session_end"](received, bytes(err), expected_format=
        "pooled-combined-input-design/v1", expected_phase="AWAIT_SESSION_END",
        expected_reported=control.reported, expected_context=control.context)
    control.check(); budget.check()
    _need(type(result) is tuple and len(result) == 3 and type(result[0]) is str
          and type(result[1]) is str, "CHANNEL_MATCH")
    _need(result[:2] == ("MATCHED_DECLARED_SESSION_END", "NONE"), "CHANNEL_MATCH")
    _need(type(result[2]) is tuple and len(result[2]) == 2 and received
          and result[2][0] is received[-1] and type(result[2][1]) is tuple, "CHANNEL_MATCH")
    return result[2]


def _prepare(control, selections, limits):
    _need(type(limits) is ChannelLimits)
    for name, maximum in (("output_bytes", 65536), ("read_bytes", 4096), ("io_steps", 4096),
                          ("no_progress", 64), ("regular_ns", 20 * NS), ("cleanup_ns", 10 * NS)):
        value = getattr(limits, name)
        _need(type(value) is int and 1 <= value <= maximum)
    _need(type(selections) is tuple and 1 <= len(selections) <= 3)
    _need(all(type(item) is ChannelSelection for item in selections))
    _need(all(type(item.program) is bytes for item in selections))
    for item in selections:
        control.namespace["_report_shape"](control.namespace["_REPORT_R"], item.reported)
        control.namespace["_report_shape"](control.namespace["_INLINE_K"], item.context)
    for item in selections:
        _need(0 < len(item.program) <= 131072 and b"\0" not in item.program)
        item.program.decode("utf-8", "strict")
        for context in (item.context, item.reported[0]):
            control.namespace["_command_context"](context)
        control.namespace["_semantic_worker"](item.reported[0][5:] + item.reported[1:])
    for ordinal, item in enumerate(selections, 1):
        _need(item.context[5] == ordinal and item.reported[0] == item.context)
        _need(item.context[:5] == selections[0].context[:5])


def run_session_channels(control_namespace, selections, *, limits=ChannelLimits()):
    """Ein eigener serieller Abschlussversuch; keine öffentliche Ledger-Receipt-API."""
    start = time.monotonic_ns()
    control = budget = None
    first = issue = "NONE"
    start_attempts = started = closed = attempts = 0
    cleanup_ok = True
    matches, observations = [], []
    try:
        control = _Control(control_namespace)
        control.capture()
        _prepare(control, selections, limits)
        budget = _Budget(limits, start)
        control.check(); budget.check(); _platform()
        for selection in selections:
            budget.check(); control.check(); _need(_no_children(), "CHANNEL_ISOLATION")
            control.reported, control.context = selection.reported, selection.context
            process = selector = None
            reaper = _Reaper()
            attempted = False
            failure = None
            observed = dict(stdout=False, stderr=False, zero_exit=False,
                            eof_before_exit=False, exit_before_eofs=False)
            observations.append(observed)
            try:
                reaper.enable()
                budget.check(); control.check()
                attempted = True; start_attempts += 1  # Reservierung vor Launcher.
                process = _launch(selection.program.decode("utf-8", "strict"))
                started += 1
                control.check(); budget.check()
                selector = selectors.DefaultSelector()
                for stream, channel in ((process.stdout, "stdout"), (process.stderr, "stderr")):
                    os.set_blocking(stream.fileno(), False)
                    selector.register(stream, selectors.EVENT_READ, channel)
                matches.append(_drain(process, selector, budget, control, observed))
            except BaseException as error:
                failure = _issue(error)
                if attempted and process is None:
                    failure = "CHANNEL_START_UNKNOWN"
            finally:
                attempts += 1
                cleanup_start = time.monotonic_ns()
                deadline = cleanup_start + max(0, limits.cleanup_ns - budget.cleanup)
                physical = restored = absent = False
                try:
                    physical = _cleanup(process, selector, deadline)
                except BaseException:
                    pass
                try:
                    restored = reaper.restore()
                except BaseException:
                    pass
                try:
                    absent = _no_children()
                except BaseException:
                    pass
                budget.cleanup += time.monotonic_ns() - cleanup_start
                complete = (physical and restored and absent and budget.cleanup <= limits.cleanup_ns
                            and not (attempted and process is None))
                cleanup_ok &= complete
                if failure is not None and first == "NONE":
                    first = failure
                issue = failure or "NONE"
                try:
                    control.check(); budget.check()
                except BaseException as error:
                    post = _issue(error)
                    if first == "NONE": first = post
                    issue = _dominant(issue, post)
                if not complete:
                    issue = "CHANNEL_CLEANUP"
            _need(issue == "NONE", issue)
            closed += 1
    except BaseException as error:
        issue = _dominant(issue, _issue(error, "CHANNEL_FORM"))
        if first == "NONE": first = issue
    if control is not None:
        try:
            control.check()
        except BaseException as error:
            post = _issue(error)
            if first == "NONE": first = post
            issue = _dominant(issue, post)
    if not cleanup_ok:
        issue = "CHANNEL_CLEANUP"
    return ChannelReport("CLOSED_SESSION_CHANNELS" if issue == "NONE" else "REJECTED_SESSION_CHANNELS",
        issue=issue, first_issue=first, start_attempts=start_attempts, started=started,
        matched=len(matches), closed=closed, observed_bytes=0 if budget is None else budget.bytes,
        io_steps=0 if budget is None else budget.io, cleanup_attempts=attempts, cleanup_complete=cleanup_ok,
        stdout_eofs=sum(row["stdout"] for row in observations),
        stderr_eofs=sum(row["stderr"] for row in observations),
        zero_exits=sum(row["zero_exit"] for row in observations),
        eof_before_exit=sum(row["eof_before_exit"] for row in observations),
        exit_before_eofs=sum(row["exit_before_eofs"] for row in observations), matches=tuple(matches))
