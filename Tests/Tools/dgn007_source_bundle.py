#!/usr/bin/env python3
"""Begrenzte Offline-Prüfung eines Kandidatenbundles; keine Bundleausführung.

Git, Python/Stdlib und das aufrufende Dateisystem sind vertrauenswürdige Tools.
Lokale Git-Objektlesebefehle erzeugen keine Nachfahren mit geerbten Pipes;
Timer sind keine allgemeine Prozessketten- oder gesamte Verifier-Harddeadline.
Der gelesene Snapshot attestiert keine spätere Immutabilität oder Runtime.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import threading
import time
from types import MappingProxyType

DEMO = "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/"
PYTHON_MEMBERS = (
    "Tests/Runtime/run_dgn007_automated_setup.py",
    "Tests/Runtime/execution_target.py", "Tests/Runtime/docker_sqlcmd_proxy.py",
    "Demos/00_Framework/Tools/run_demo.py",
    "Demos/00_Framework/Tools/orchestrate_sessions.py",
    "Demos/00_Framework/Tools/sqlcmd_process.py",
    "Tests/Contracts/dgn007_capture_projection.py",
    "Tests/Contracts/dgn007_collector_transport.py",
    "Tests/Contracts/dgn007_prospective_acceptance.py",
)
DATA_MEMBERS = tuple(DEMO + "Automated/" + name for name in (
    "00_Preflight.sql", "10_Setup.sql", "15_Control_AB.sql", "15_Control_BA.sql",
    "15_Control_AA.sql", "20_Query_Store_Windows.sql",
    "21_Controlled_Query_Store_Windows.sql", "30_Profile_Comparison.sql",
    "35_Control_Evidence.sql", "40_Data_Assertion.sql", "90_Cleanup.sql",
    "setup.manifest.json", "windows.manifest.json", "profile-comparison.manifest.json",
    "control-ab.manifest.json", "control-ba.manifest.json", "control-aa.manifest.json",
)) + (DEMO + "Contracts/incident-acceptance.contract.json",)
STDLIB = frozenset(("__future__", "argparse", "ctypes", "dataclasses", "decimal",
                    "fractions", "hashlib", "json", "os", "pathlib", "re", "shutil",
                    "signal", "subprocess", "sys", "threading", "time", "typing"))
MODULES = tuple((Path(p).stem if "/Contracts/" not in p else
                 "Tests.Contracts." + Path(p).stem, p) for p in PYTHON_MEMBERS)
# Exakte AST-Bindung der bereits reviewten Suchpfadblöcke, keine Ausführung.
BOOTSTRAPS = (
    (PYTHON_MEMBERS[0], ("ROOT", "RUNTIME", "FRAMEWORK"),
     "f417ebb8396bfd9998fbf80e84a1313c5e310efb73516ea37b5a9d7dcd64812e"),
    (PYTHON_MEMBERS[1], ("ROOT", "RUNTIME", "FRAMEWORK_TOOLS"),
     "4c322b3e2ff26323eb731c63115a1c097c0ed83862969e339d4ed247ba8a5436"),
)


@dataclass(frozen=True)
class Policy:
    """Reviewter Kontrollinput; niemals aus Kandidatendateien laden."""
    members: tuple[str, ...]
    modules: tuple[tuple[str, str], ...]
    entrypoints: tuple[str, ...]
    stdlib: frozenset[str] = STDLIB
    bootstraps: tuple = ()
    file_bytes: int = 131072
    total_bytes: int = 1048576
    entries: int = 128
    ast_nodes: int = 100000


DGN007 = Policy(PYTHON_MEMBERS + DATA_MEMBERS, MODULES,
                (PYTHON_MEMBERS[0], PYTHON_MEMBERS[2], PYTHON_MEMBERS[3]),
                bootstraps=BOOTSTRAPS)


@dataclass(frozen=True)
class Report:
    status: str
    issue: str
    commit: str = ""
    raw_bytes_verified: bool = False
    logical_text_equivalent: bool = False
    declared_import_graph_verified: bool = False
    members: int = 0
    raw_binding: str = ""
    lf_binding: str = ""
    validation_scope: str = "PROJECT_SEMANTIC"
    runtime_attested: bool = False
    method_approved: bool = False


class Rejected(ValueError):
    pass


def _path(value: str) -> None:
    if type(value) is not str or not 1 <= len(value) <= 240:
        raise Rejected("INVALID_PATH")
    for part in value.split("/"):
        if (not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,127}", part)
                or part.endswith((".", " ")) or part.split(".")[0].upper() in
                {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                 *(f"LPT{i}" for i in range(1, 10))}):
            raise Rejected("INVALID_PATH")


def _regular(path: Path, directory: bool = False) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise Rejected("LINK_OR_REPARSE")
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise Rejected("INVALID_FILE_TYPE")
    if not directory and info.st_nlink != 1:
        raise Rejected("HARDLINK")
    return info


def _root(path: Path) -> Path:
    # Nicht vor lstat resolve(): eine Junction-/Symlinkkomponente wäre unsichtbar.
    absolute = Path(os.path.abspath(path))
    for parent in reversed((absolute, *absolute.parents)):
        _regular(parent, directory=True)
    return absolute


def _inventory(root: Path, policy: Policy) -> tuple[str, ...]:
    allowed_dirs = {p.rsplit("/", 1)[0] for p in policy.members if "/" in p}
    allowed_dirs |= {str(Path(p).parent).replace("\\", "/") for p in tuple(allowed_dirs)}
    for p in policy.members:
        allowed_dirs.update("/".join(p.split("/")[:i]) for i in range(1, len(p.split("/"))))
    found, seen, pending, count = [], set(), [root], 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as scan:
            for entry in scan:
                count += 1
                if count > policy.entries:
                    raise Rejected("ENTRY_LIMIT")
                p = Path(entry.path)
                rel = p.relative_to(root).as_posix()
                _path(rel)
                if rel.casefold() in seen:
                    raise Rejected("CASE_COLLISION")
                seen.add(rel.casefold())
                info = p.lstat()
                if stat.S_ISDIR(info.st_mode):
                    _regular(p, directory=True)
                    if rel not in allowed_dirs:
                        raise Rejected("EXTRA_MEMBER")
                    pending.append(p)
                else:
                    _regular(p)
                    found.append(rel)
    if set(found) != set(policy.members):
        raise Rejected("MEMBER_SET")
    return tuple(sorted(found))


def git_environment() -> dict[str, str]:
    """Keine Git-Umleitung, Credentials, globalen Configs oder Lazyfetch."""
    result = {k: v for k, v in os.environ.items()
              if k.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG"}}
    result.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                  GIT_CONFIG_SYSTEM=os.devnull, GIT_NO_REPLACE_OBJECTS="1",
                  GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    return result


def _git(repo: Path, args: tuple[str, ...], limit: int, deadline: float) -> bytes:
    executable = shutil.which("git")
    if not executable:
        raise Rejected("GIT_UNAVAILABLE")
    command = [executable, "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo), *args]
    output, overflow, errors = bytearray(), threading.Event(), threading.Event()
    with subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=False, env=git_environment()) as proc:
        def read(pipe, cap, save):
            size = 0
            try:
                while chunk := pipe.read(4096):
                    size += len(chunk)
                    if size > cap:
                        overflow.set()
                        return
                    if save:
                        output.extend(chunk)
            except OSError:
                errors.set()
        threads = [threading.Thread(target=read, args=(proc.stdout, limit, True), daemon=True),
                   threading.Thread(target=read, args=(proc.stderr, 4096, False), daemon=True)]
        for thread in threads:
            thread.start()
        end = min(deadline, time.monotonic() + 5)
        while proc.poll() is None and not overflow.is_set() and time.monotonic() < end:
            time.sleep(0.005)
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=2)
        for thread in threads:
            thread.join(timeout=1)
        if (proc.returncode != 0 or overflow.is_set() or errors.is_set()
                or any(t.is_alive() for t in threads) or time.monotonic() >= end):
            raise Rejected("GIT_READ_FAILED")
    return bytes(output)


def _git_blob(repo: Path, commit: str, member: str, cap: int, deadline: float) -> bytes:
    row = _git(repo, ("ls-tree", "-z", commit, "--", member), 512, deadline)
    match = re.fullmatch(rb"(100644|100755) blob ([0-9a-f]{40})\t([^\0]+)\0", row)
    if not match or match[3].decode("ascii") != member:
        raise Rejected("GIT_MEMBER_TYPE")
    oid = match[2].decode("ascii")
    size = _git(repo, ("cat-file", "-s", oid), 32, deadline).strip()
    if not size.isdigit() or int(size) > cap:
        raise Rejected("FILE_LIMIT")
    body = _git(repo, ("cat-file", "blob", oid), cap, deadline)
    if len(body) != int(size) or hashlib.sha1(b"blob " + size + b"\0" + body).hexdigest() != oid:
        raise Rejected("GIT_BLOB_BINDING")
    return body


def _imports(bodies: dict[str, bytes], policy: Policy) -> None:
    modules = dict(policy.modules)
    if len(modules) != len(policy.modules) or set(modules.values()) != {
            p for p in policy.members if p.endswith(".py")}:
        raise Rejected("MODULE_POLICY")
    if any(name.split(".")[0] in policy.stdlib for name in modules):
        raise Rejected("STDLIB_SHADOW")
    forbidden = {"__import__", "eval", "exec", "import_module", "find_spec",
                 "spec_from_file_location", "exec_module", "load_module", "run_module", "run_path"}
    total_nodes = 0
    for path in modules.values():
        try:
            tree = ast.parse(bodies[path].decode("utf-8"), filename="candidate")
        except (SyntaxError, UnicodeError, ValueError, RecursionError, MemoryError):
            raise Rejected("PYTHON_SYNTAX") from None
        nodes = list(ast.walk(tree))
        sys_names = {"sys"} | {a.asname or a.name for n in nodes if isinstance(n, ast.Import)
                               for a in n.names if a.name == "sys"}
        total_nodes += len(nodes)
        if total_nodes > policy.ast_nodes:
            raise Rejected("AST_LIMIT")
        bootstrap_nodes = []
        bootstrap = next((b for b in policy.bootstraps if b[0] == path), None)
        if bootstrap:
            for node in tree.body:
                if (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
                    t.id in bootstrap[1] for t in node.targets)) or (
                    isinstance(node, (ast.For, ast.If)) and any(
                        isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                        and n.value.id == "sys" and n.attr == "path" for n in ast.walk(node))):
                    bootstrap_nodes.append(node)
            digest = hashlib.sha256(ast.dump(ast.Module(body=bootstrap_nodes, type_ignores=[]),
                                            include_attributes=False).encode()).hexdigest()
            if digest != bootstrap[2]:
                raise Rejected("BOOTSTRAP_CHANGED")
        allowed = {id(n) for b in bootstrap_nodes for n in ast.walk(b)}
        for node in nodes:
            if isinstance(node, (ast.Name, ast.Attribute)) and (
                    getattr(node, "id", None) in forbidden or getattr(node, "attr", None) in forbidden):
                raise Rejected("DYNAMIC_IMPORT_OPEN")
            if isinstance(node, ast.Attribute) and node.attr in {"path", "meta_path", "path_hooks",
                    "path_importer_cache", "modules"} and isinstance(node.value, ast.Name) and (
                    node.value.id in sys_names) and id(node) not in allowed:
                raise Rejected("IMPORT_ENVIRONMENT_OPEN")
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.module == "sys" and any(a.name in {"path", "meta_path", "path_hooks",
                        "path_importer_cache", "modules"} for a in node.names):
                    raise Rejected("IMPORT_ENVIRONMENT_OPEN")
                if node.level or any(a.name == "*" or a.name in forbidden for a in node.names):
                    raise Rejected("UNRESOLVED_IMPORT")
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name not in modules and name not in policy.stdlib:
                    raise Rejected("UNRESOLVED_IMPORT")


def verify_bundle(repository: Path, commit: str, candidate: Path,
                  policy: Policy = DGN007, *, bound_validator=None) -> Report:
    """Nur Snapshot und deklarierte AST-Imports; kein allgemeiner Sandboxbeweis."""
    raw = logical = False
    try:
        if type(commit) is not str or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise Rejected("EXPLICIT_COMMIT_REQUIRED")
        if (not 1 <= len(policy.members) <= 32 or len(set(policy.members)) != len(policy.members)
                or len({p.casefold() for p in policy.members}) != len(policy.members)):
            raise Rejected("DUPLICATE_OR_MEMBER_LIMIT")
        for p in policy.members:
            _path(p)
        if not set(policy.entrypoints) <= {p for _, p in policy.modules}:
            raise Rejected("ENTRYPOINT_POLICY")
        repo, root = _root(repository), _root(candidate)
        members = _inventory(root, policy)
        deadline = time.monotonic() + 30
        actual_commit = _git(repo, ("rev-parse", "--verify", commit + "^{commit}"), 64, deadline)
        if actual_commit.strip().decode("ascii") != commit:
            raise Rejected("COMMIT_BINDING")
        bodies, raw_rows, lf_rows, total, equivalent, identical = {}, [], [], 0, True, True
        for member in members:
            blob = _git_blob(repo, commit, member, policy.file_bytes, deadline)
            file = root / member
            before = _regular(file)
            if before.st_size > policy.file_bytes:
                raise Rejected("FILE_LIMIT")
            with file.open("rb") as stream:
                body = stream.read(policy.file_bytes + 1)
            after = _regular(file)
            if (len(body) > policy.file_bytes or len(body) != before.st_size
                    or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)):
                raise Rejected("FILE_CHANGED_OR_LIMIT")
            total += len(body)
            if total > policy.total_bytes:
                raise Rejected("TOTAL_LIMIT")
            body.decode("utf-8")
            blob.decode("utf-8")
            equivalent &= body.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n")
            identical &= body == blob
            raw_rows.append([member, hashlib.sha256(body).hexdigest()])
            lf_rows.append([member, hashlib.sha256(body.replace(b"\r\n", b"\n")).hexdigest()])
            bodies[member] = body
        if not identical:
            logical = equivalent
            raise Rejected("RAW_BYTES_DIFFER")
        raw = logical = True
        _imports(bodies, policy)
        if bound_validator is not None:
            # Nur kontrollseitiger Code; exakt gelesene Bytes, keine Neuaufnahme.
            try:
                bound_validator(MappingProxyType(bodies))
            except Rejected:
                raise
            except Exception:
                raise Rejected("BOUND_VALIDATOR_FAILED") from None
        bind = lambda rows: hashlib.sha256(json.dumps(rows, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()
        return Report("PASS_STATIC_CANDIDATE", "NONE", commit, True, True, True,
                      len(members), bind(raw_rows), bind(lf_rows))
    except (Rejected, OSError, UnicodeError, subprocess.SubprocessError) as exc:
        issue = str(exc) if isinstance(exc, Rejected) else "LOCAL_READ_FAILED"
        return Report("FAIL_STATIC_CANDIDATE", issue, commit if re.fullmatch(
            r"[0-9a-f]{40}", str(commit)) else "", raw, logical)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args(argv)
    result = verify_bundle(args.repository, args.commit, args.candidate)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0 if result.status == "PASS_STATIC_CANDIDATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
