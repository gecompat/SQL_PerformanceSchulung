#!/usr/bin/env python3
"""Begrenzter Linux-Worker für die tatsächliche Ausführung fester Modulbytes.

Der Schnitt kann nur die neun gebundenen Python-Member in drei frischen
CPython-3.12-Linux-Workern importieren und BEGIN/COMPLETE-Belege für tatsächlich
kompilierte Bytes zurückgeben. Kontrollruntime, Betriebssystem, Parent und
Installationsprofil bleiben angenommene Vertrauensgrenzen. Keine SQL-,
Cleanup-, Methoden-, Host- oder vollständige Runtimeattestation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
import threading
import time

import dgn007_import_probe_input as input_protocol
import dgn007_source_bundle as bundle

MAX_OUTPUT_BYTES = 64 * 1024
MAX_LINE_BYTES = 1024
REGULAR_SECONDS = 20.0
CLEANUP_SECONDS = 10.0
_ENTRY_NAMES = tuple(member.rsplit("/", 1)[-1][:-3] for member in bundle.DGN007.entrypoints)
WORKERS = (
    (_ENTRY_NAMES[0], (
        "run_dgn007_automated_setup", "execution_target", "sqlcmd_process",
        "run_demo", "orchestrate_sessions", "Tests.Contracts.dgn007_capture_projection",
        "Tests.Contracts.dgn007_collector_transport",
        "Tests.Contracts.dgn007_prospective_acceptance")),
    (_ENTRY_NAMES[1], ("docker_sqlcmd_proxy",)),
    (_ENTRY_NAMES[2], ("run_demo", "orchestrate_sessions", "sqlcmd_process")),
)


@dataclass(frozen=True, slots=True, repr=False)
class ImportReceipt:
    sequence: int
    phase: str
    module: str
    member: str
    size: int
    sha256: str


@dataclass(frozen=True, slots=True)
class WorkerObservation:
    entry: str
    status: str
    issue: str
    imports: tuple[ImportReceipt, ...] = ()


@dataclass(frozen=True, slots=True)
class ProbeReport:
    status: str
    issue: str
    workers: tuple[WorkerObservation, ...] = ()
    claim: str = field(default="DGN007_IMPORT_ONLY_SOURCE_CANDIDATE", init=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


class ProbeRejected(ValueError):
    """Feste Labels ohne Kandidatenoutput oder Exceptiontext."""


def _reject(issue):
    raise ProbeRejected(issue)


def _worker_source(ordinal: int, worker_nonce: bytes) -> str:
    entry, expected = WORKERS[ordinal - 1]
    mapping = repr(bundle.MODULES)
    expected_literal = repr(expected)
    worker_nonce_hex = worker_nonce.hex()
    return f'''\
import hashlib, importlib.abc, importlib.machinery, json, struct, sys
MAGIC = {input_protocol.MAGIC!r}
MODULES = {mapping}
ENTRY = {entry!r}
EXPECTED = {expected_literal}
WORKER_NONCE = {worker_nonce_hex!r}
HEADER = struct.Struct(">8sII")
MAX_FRAME = {input_protocol.MAX_FRAME_BYTES}
MAX_META = {input_protocol.MAX_METADATA_BYTES}
MAX_BODY = {input_protocol.MAX_BODY_BYTES}
def fail(label): raise RuntimeError(label)
def canonical(value): return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")
def unique_pairs(rows):
    value = {{}}
    for key, item in rows:
        if key in value: fail("FRAME_DUPLICATE_KEY")
        value[key] = item
    return value
def parse():
    frame = sys.stdin.buffer.read(MAX_FRAME + 1)
    if len(frame) > MAX_FRAME or len(frame) < HEADER.size: fail("FRAME_LIMIT")
    magic, msize, bsize = HEADER.unpack_from(frame)
    if magic != MAGIC or not (0 < msize <= MAX_META - HEADER.size and bsize <= MAX_BODY): fail("FRAME_HEADER")
    if HEADER.size + msize + bsize != len(frame): fail("FRAME_LENGTH")
    meta = json.loads(frame[HEADER.size:HEADER.size + msize].decode("ascii"), object_pairs_hook=unique_pairs)
    if type(meta) is not dict or set(meta) != {{"protocol", "commit", "raw27_binding", "source_profile", "nonce", "modules", "context_sha256"}}: fail("FRAME_META")
    digest = meta.pop("context_sha256")
    if hashlib.sha256(canonical(meta)).hexdigest() != digest: fail("FRAME_CONTEXT")
    meta["context_sha256"] = digest
    if meta["protocol"] != "dgn007-import-input/v1" or meta["source_profile"] != "dgn007-docker-sql-only/v1": fail("FRAME_CONTEXT")
    if type(meta["modules"]) is not list or len(meta["modules"]) != len(MODULES): fail("FRAME_MAPPING")
    body = memoryview(frame)[HEADER.size + msize:]
    sources, offset = {{}}, 0
    for i, (row, pair) in enumerate(zip(meta["modules"], MODULES)):
        if type(row) is not dict or set(row) != {{"ordinal", "module", "member", "size", "sha256"}}: fail("FRAME_MAPPING")
        name, member = pair
        if (type(row["ordinal"]) is not int or row["ordinal"] != i
                or type(row["module"]) is not str or row["module"] != name
                or type(row["member"]) is not str or row["member"] != member): fail("FRAME_MAPPING")
        size = row["size"]
        if type(size) is not int or not (0 <= size <= 131072) or offset + size > len(body): fail("FRAME_SIZE")
        raw = bytes(body[offset:offset + size]); offset += size
        sha = hashlib.sha256(raw).hexdigest()
        if row["sha256"] != sha: fail("FRAME_HASH")
        sources[name] = (member, raw, sha)
    if offset != len(body) or sum(len(v[1]) for v in sources.values()) > MAX_BODY: fail("FRAME_LENGTH")
    return meta, sources
class MemoryLoader(importlib.abc.Loader):
    def __init__(self, finder, name): self.finder, self.name = finder, name
    def exec_module(self, module):
        f = self.finder; item = f.sources[self.name]
        if f.position >= len(EXPECTED) or EXPECTED[f.position] != self.name: fail("IMPORT_ORDER")
        if module.__spec__ is None or module.__spec__.loader is not self: fail("MODULE_SPEC")
        sequence = f.position + 1
        receipt = {{"sequence": sequence, "phase": "BEGIN", "module": self.name,
                   "member": item[0], "size": len(item[1]), "sha256": item[2]}}
        f.receipts.append(receipt); f.position += 1
        code = compile(item[1], f.origin(item[0]), "exec", dont_inherit=True, optimize=0)
        exec(code, module.__dict__)
        if (module.__spec__ is None or module.__spec__.loader is not self
                or module.__loader__ is not self or module.__spec__.origin != f.origin(item[0])
                or module.__file__ != f.origin(item[0])): fail("MODULE_ORIGIN")
        f.receipts.append(dict(receipt, sequence=sequence + len(EXPECTED), phase="COMPLETE"))
class Finder(importlib.abc.MetaPathFinder):
    def __init__(self, sources, trusted_path): self.sources, self.trusted_path = sources, trusted_path; self.receipts=[]; self.position=0
    def origin(self, member): return "/__dgn007_memory__" + "/" + member
    def find_spec(self, fullname, path=None, target=None):
        if target is not None: fail("RELOAD")
        if fullname in self.sources:
            if fullname in sys.modules or self.position >= len(EXPECTED) or EXPECTED[self.position] != fullname: fail("IMPORT_ORDER")
            spec = importlib.machinery.ModuleSpec(fullname, MemoryLoader(self, fullname), origin=self.origin(self.sources[fullname][0]))
            spec.has_location = True
            return spec
        if fullname in ("Tests", "Tests.Contracts"):
            spec = importlib.machinery.ModuleSpec(fullname, loader=None, is_package=True)
            spec.submodule_search_locations = []
            return spec
        if fullname == "Tests" or fullname.startswith("Tests."): fail("UNKNOWN_PROJECT_MODULE")
        return None
def main():
    meta, sources = parse()
    if {ordinal} not in (1,2,3) or ENTRY != ("run_dgn007_automated_setup", "docker_sqlcmd_proxy", "run_demo")[{ordinal}-1]: fail("WORKER_CONTEXT")
    if sys.version_info[:2] != (3,12) or sys.implementation.name != "cpython" or not sys.flags.isolated or not sys.flags.no_site or not sys.flags.dont_write_bytecode: fail("CONTROL_RUNTIME")
    expected_names = {{name for name, _ in MODULES}}
    if expected_names & set(sys.modules): fail("OWN_MODULE_PRELOADED")
    trusted_path = tuple(p for p in sys.path if type(p) is str and p)
    original_hooks = tuple(sys.path_hooks)
    builtin, frozen = importlib.machinery.BuiltinImporter, importlib.machinery.FrozenImporter
    finder = Finder(sources, trusted_path)
    class RestrictedPathFinder:
        @staticmethod
        def find_spec(fullname, path=None, target=None):
            def trusted_location(item):
                return any(item == root or item.startswith(root.rstrip("/") + "/")
                           for root in trusted_path)
            chosen = trusted_path if path is None else tuple(p for p in path if trusted_location(p))
            if path is not None and not chosen: fail("PATH_ESCAPE")
            return importlib.machinery.PathFinder.find_spec(fullname, chosen, target)
    sys.meta_path = [finder, builtin, frozen, RestrictedPathFinder]
    importlib.import_module(ENTRY)
    if finder.position != len(EXPECTED) or [r["module"] for r in finder.receipts if r["phase"] == "BEGIN"] != list(EXPECTED): fail("IMPORT_SET")
    if tuple(sys.path_hooks) != original_hooks or sys.meta_path != [finder, builtin, frozen, RestrictedPathFinder]: fail("IMPORT_HOOKS_CHANGED")
    if expected_names & set(sys.modules) != set(EXPECTED): fail("IMPORT_SET")
    print(json.dumps({{"status":"OBSERVED_IMPORTS","entry":ENTRY,
                      "context_sha256":meta["context_sha256"],
                      "worker_nonce":WORKER_NONCE}}, sort_keys=True, separators=(",", ":")))
    for receipt in finder.receipts:
        print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
main()
'''


def _read_bounded(pipe, buffer, budget, lock, overflow):
    try:
        while True:
            with lock:
                remaining = budget[0] - budget[1]
            chunk = pipe.read(min(4096, max(1, remaining + 1)))
            if not chunk:
                return
            with lock:
                remaining = budget[0] - budget[1]
                kept = chunk[:max(0, remaining + 1)]
                buffer.extend(kept)
                budget[1] += len(kept)
                if len(kept) > remaining:
                    overflow.set()
                    return
    except (OSError, ValueError):
        overflow.set()


def _collect_process(command, input_bytes, deadline, output_limit):
    if os.name != "posix":
        return "PROCESS_SCOPE_UNKNOWN", b"", b""
    try:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False, close_fds=True,
                                start_new_session=True)
    except (OSError, ValueError):
        return "PROCESS_START_FAILED", b"", b""
    out, err = bytearray(), bytearray()
    limit = [output_limit, 0]
    lock, overflow = threading.Lock(), threading.Event()
    readers = [threading.Thread(target=_read_bounded, args=(stream, dest, limit, lock, overflow), daemon=True)
               for stream, dest in ((proc.stdout, out), (proc.stderr, err))]
    for reader in readers: reader.start()
    def write_input():
        try:
            proc.stdin.write(input_bytes); proc.stdin.flush(); proc.stdin.close()
        except (OSError, ValueError):
            pass
    writer = threading.Thread(target=write_input, daemon=True); writer.start()
    state = "PROCESS_END_UNKNOWN"
    while time.monotonic() < deadline:
        if overflow.is_set():
            state = "OUTPUT_LIMIT"; break
        if proc.poll() is not None:
            for reader in readers: reader.join(timeout=0.05)
            if all(not t.is_alive() for t in readers) and not writer.is_alive():
                state = "PROCESS_EXIT_0" if proc.returncode == 0 else "PROCESS_EXIT_NONZERO"
                break
            state = "PROCESS_END_UNKNOWN"; break
        time.sleep(0.01)
    if state in ("PROCESS_END_UNKNOWN", "OUTPUT_LIMIT"):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            state = "PROCESS_END_UNKNOWN"
        cleanup_deadline = time.monotonic() + CLEANUP_SECONDS
        try: proc.wait(timeout=max(0.0, cleanup_deadline - time.monotonic()))
        except subprocess.TimeoutExpired: state = "PROCESS_END_UNKNOWN"
        for thread in [writer, *readers]:
            thread.join(timeout=max(0.0, cleanup_deadline - time.monotonic()))
        if any(t.is_alive() for t in [writer, *readers]): state = "PROCESS_END_UNKNOWN"
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        try: stream.close()
        except (OSError, ValueError): pass
    return state, bytes(out), bytes(err)


def _decode_worker_output(stdout, stderr, expected, prepared, worker_nonce):
    if stderr or len(stdout) > MAX_OUTPUT_BYTES:
        _reject("WORKER_OUTPUT")
    try:
        lines = stdout.decode("ascii").splitlines()
        if not lines or any(not row or len(row.encode("ascii")) > MAX_LINE_BYTES for row in lines):
            _reject("WORKER_OUTPUT")
        records = [json.loads(row, object_pairs_hook=lambda pairs: _unique_pairs(pairs)) for row in lines]
    except (ValueError, UnicodeError, RecursionError):
        _reject("WORKER_REPORT")
    if len(records) != len(expected[1]) * 2 + 1:
        _reject("WORKER_REPORT")
    value = records[0]
    expected_entry = expected[0]
    meta = input_protocol._metadata(prepared)
    if (type(value) is not dict or set(value) != {"status", "entry", "context_sha256", "worker_nonce"}
            or type(value["status"]) is not str or type(value["entry"]) is not str
            or type(value["context_sha256"]) is not str or type(value["worker_nonce"]) is not str
            or value["status"] != "OBSERVED_IMPORTS" or value["entry"] != expected_entry
            or value["context_sha256"] != meta["context_sha256"]
            or value["worker_nonce"] != worker_nonce.hex()):
        _reject("WORKER_BINDING")
    receipts = records[1:]
    by_name = dict(bundle.MODULES)
    actual = []
    stack, begun, completed = [], 0, set()
    source_by_name = {s.module: s for s in prepared.sources}
    for row in receipts:
        if type(row) is not dict or set(row) != {"sequence", "phase", "module", "member", "size", "sha256"}:
            _reject("WORKER_RECEIPT_BINDING")
        phase, module = row["phase"], row["module"]
        if (type(row["sequence"]) is not int or type(phase) is not str
                or type(module) is not str or type(row["member"]) is not str
                or type(row["size"]) is not int or type(row["sha256"]) is not str):
            _reject("WORKER_RECEIPT_BINDING")
        if phase == "BEGIN":
            if begun >= len(expected[1]) or module != expected[1][begun]:
                _reject("WORKER_RECEIPT_BINDING")
            index = begun
            stack.append(module)
            begun += 1
            sequence = index + 1
        elif phase == "COMPLETE":
            if not stack or module != stack.pop() or module in completed:
                _reject("WORKER_RECEIPT_BINDING")
            index = expected[1].index(module)
            completed.add(module)
            sequence = index + 1 + len(expected[1])
        else:
            _reject("WORKER_RECEIPT_BINDING")
        source = source_by_name[module]
        core = {"module": module, "member": by_name[module], "size": len(source.body), "sha256": source.sha256}
        if row != dict(core, sequence=sequence, phase=phase):
            _reject("WORKER_RECEIPT_BINDING")
        actual.append(ImportReceipt(sequence, phase, module, core["member"], core["size"], core["sha256"]))
    if begun != len(expected[1]) or stack or completed != set(expected[1]):
        _reject("WORKER_RECEIPT_BINDING")
    return WorkerObservation(expected_entry, "OBSERVED_IMPORTS", "NONE", tuple(actual))


def _unique_pairs(rows):
    result = {}
    for key, value in rows:
        if key in result: raise ValueError("duplicate")
        result[key] = value
    return result


def run_import_only(preparation: input_protocol.PreparationResult) -> ProbeReport:
    """Importiert die festen Runtimemember in drei frischen begrenzten Workern.

    Diese lokale Quellkomponente wird nicht vom DGN-007-Runner aufgerufen. Ein
    erfolgreiches Ergebnis wäre eine begrenzte Importverwendungsbeobachtung,
    keine Trust-, Runtime- oder Methodengatefreigabe.
    """
    if type(preparation) is not input_protocol.PreparationResult:
        return ProbeReport("FAIL_IMPORT_ONLY", "INPUT_NOT_PREPARED")
    verification = preparation.verification
    prepared = preparation.prepared
    if (type(preparation.status) is not str or preparation.status != "PREPARED_INPUT_ONLY"
            or type(preparation.issue) is not str or preparation.issue != "NONE"
            or preparation.runtime_attested is not False
            or preparation.import_used_bytes_attested is not False
            or preparation.method_approved is not False
            or type(prepared) is not input_protocol.PreparedInput
            or type(prepared.commit) is not str
            or type(prepared.raw27_binding) is not str
            or type(verification) is not bundle.Report
            or type(verification.status) is not str
            or verification.status != "PASS_STATIC_CANDIDATE"
            or type(verification.raw_bytes_verified) is not bool
            or verification.raw_bytes_verified is not True
            or type(verification.declared_import_graph_verified) is not bool
            or verification.declared_import_graph_verified is not True
            or type(verification.members) is not int
            or verification.members != len(bundle.DGN007.members)
            or type(verification.raw_binding) is not str
            or type(verification.commit) is not str
            or type(verification.validation_scope) is not str
            or verification.validation_scope != "PROJECT_SEMANTIC"
            or verification.runtime_attested is not False
            or verification.method_approved is not False
            or verification.raw_binding != prepared.raw27_binding
            or verification.commit != prepared.commit):
        return ProbeReport("FAIL_IMPORT_ONLY", "INPUT_NOT_PREPARED")
    if os.name != "posix" or sys.platform != "linux":
        return ProbeReport("FAIL_IMPORT_ONLY", "LINUX_REQUIRED")
    if sys.version_info[:2] != (3, 12) or sys.implementation.name != "cpython":
        return ProbeReport("FAIL_IMPORT_ONLY", "CPYTHON_312_REQUIRED")
    try:
        frame = input_protocol.encode_input(prepared)
    except input_protocol.InputRejected:
        return ProbeReport("FAIL_IMPORT_ONLY", "INPUT_REJECTED")
    deadline = time.monotonic() + REGULAR_SECONDS
    observed = []
    output_used = 0
    for ordinal, expected in enumerate(WORKERS, 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0: return ProbeReport("UNKNOWN_IMPORT_ONLY", "REGULAR_DEADLINE", tuple(observed))
        try:
            worker_nonce = secrets.token_bytes(32)
        except (OSError, ValueError, TypeError):
            return ProbeReport("FAIL_IMPORT_ONLY", "WORKER_NONCE", tuple(observed))
        if type(worker_nonce) is not bytes or len(worker_nonce) != 32:
            return ProbeReport("FAIL_IMPORT_ONLY", "WORKER_NONCE", tuple(observed))
        command = [sys.executable, "-I", "-S", "-B", "-c", _worker_source(ordinal, worker_nonce)]
        state, stdout, stderr = _collect_process(command, frame, deadline, MAX_OUTPUT_BYTES - output_used)
        output_used += len(stdout) + len(stderr)
        if state != "PROCESS_EXIT_0":
            return ProbeReport("UNKNOWN_IMPORT_ONLY" if state == "PROCESS_END_UNKNOWN" else "FAIL_IMPORT_ONLY",
                               state, tuple(observed))
        try:
            observation = _decode_worker_output(stdout, stderr, expected, prepared, worker_nonce)
        except ProbeRejected as error:
            return ProbeReport("FAIL_IMPORT_ONLY", str(error), tuple(observed))
        observed.append(observation)
    return ProbeReport("OBSERVED_IMPORT_BYTES", "NONE", tuple(observed))
