"""Beobachtung eines ausdrücklich deklarierten Linux-Kontrollruntimeprofils.

Der Caller setzt Interpreter/Stdlib/OS-Vertrauen voraus. Ein Match belegt keine
Herkunft oder geladenen Dateibytes. Keine Kandidatenimporte oder Prozessstarts.
"""
from dataclasses import dataclass, field
import hashlib
from importlib.machinery import (BuiltinImporter, FrozenImporter, PathFinder,
                                SourceFileLoader, ExtensionFileLoader, ModuleSpec)
import os
import sys
import sysconfig
from types import ModuleType, FunctionType
from zipimport import zipimporter

MAX_RECORDS = 256
MAX_FIELD = 4096
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024
ASSUMPTION = "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME"
# Feste CPython-3.12-Bootstrapcachealiases; keine Kandidaten-/freien Aliase.
FROZEN_NAMES = {
    "_frozen_importlib": ("importlib._bootstrap", "_frozen_importlib"),
    "importlib._bootstrap": ("importlib._bootstrap", "_frozen_importlib"),
    "_frozen_importlib_external": ("importlib._bootstrap_external", "_frozen_importlib_external"),
    "importlib._bootstrap_external": ("importlib._bootstrap_external", "_frozen_importlib_external"),
    "_collections_abc": ("collections.abc", "_collections_abc"),
    "collections.abc": ("collections.abc", "_collections_abc"),
    "os.path": ("posixpath", "posixpath"),
}


@dataclass(frozen=True)
class ModuleRecord:
    name: str
    origin: str = field(repr=False)
    file: str = field(repr=False)
    kind: str
    locations: tuple = field(repr=False)
    module: object = field(repr=False)
    spec: object = field(repr=False)
    loader: object = field(repr=False)


@dataclass(frozen=True)
class FileDigest:
    path: str = field(repr=False)
    size: int
    sha256: str


@dataclass(frozen=True)
class DeclaredProfile:
    assumption: str
    token: bytes = field(repr=False)
    implementation: str
    version: tuple
    executable: str = field(repr=False)
    executable_target: str = field(repr=False)
    prefixes: tuple = field(repr=False)
    abi: str
    paths: tuple = field(repr=False)
    roots: tuple = field(repr=False)
    inert_zip: str = field(repr=False)
    controls: tuple
    finders: tuple = field(repr=False)
    hooks: tuple = field(repr=False)
    modules: tuple = field(repr=False)
    files: tuple = field(repr=False)


@dataclass(frozen=True)
class Observation:
    token: bytes = field(repr=False)
    platform: str
    implementation: str
    version: tuple
    executable: str = field(repr=False)
    executable_target: str = field(repr=False)
    prefixes: tuple = field(repr=False)
    abi: str
    flags: tuple
    paths: tuple = field(repr=False)
    finders: tuple = field(repr=False)
    hooks: tuple = field(repr=False)
    modules: tuple = field(repr=False)
    files: tuple = field(repr=False)


@dataclass(frozen=True)
class ProfileReport:
    status: str
    issue: str
    trust_assumed: bool = False
    trust_attested: bool = field(default=False, init=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


class _Failure(ValueError):
    pass


def _need(condition, issue="INVALID_RECORD"):
    if not condition:
        raise _Failure(issue)


def _text(value):
    _need(type(value) is str and len(value) <= MAX_FIELD)
    _need(len(value.encode("utf-8")) <= MAX_FIELD)


def _strings(value):
    _need(type(value) is tuple and len(value) <= MAX_RECORDS)
    for item in value:
        _text(item)


def _absolute(value):
    _text(value)
    _need(value.startswith("/") and "//" not in value and "\x00" not in value
          and (value == "/" or not value.endswith("/"))
          and all(p not in (".", "..") for p in value.split("/")), "PATH_MISMATCH")


def _records(value):
    _need(type(value) is tuple and 0 < len(value) <= MAX_RECORDS)
    names = []
    for row in value:
        _need(type(row) is ModuleRecord)
        for item in (row.name, row.origin, row.file, row.kind):
            _text(item)
        _strings(row.locations)
        _need(type(row.module) is ModuleType and (row.spec is None or type(row.spec) is ModuleSpec))
        _need(row.loader is None or row.loader is BuiltinImporter or row.loader is FrozenImporter
              or type(row.loader) in (SourceFileLoader, ExtensionFileLoader))
        _need(row.kind in ("BUILTIN", "FROZEN", "SOURCE", "EXTENSION", "CONTROL"))
        if type(row.loader) in (SourceFileLoader, ExtensionFileLoader):
            _need(type(row.loader.name) is str and row.loader.name == row.name
                  and type(row.loader.path) is str and row.loader.path == row.file,
                  "MODULE_COHERENCY")
        d = row.module.__dict__
        module_name, spec_name = FROZEN_NAMES.get(row.name, (row.name, row.name)) if row.loader is FrozenImporter else (row.name, row.name)
        _need(type(d.get("__name__")) is str and d["__name__"] == module_name
              and d.get("__spec__") is row.spec and d.get("__loader__") is row.loader
              and type(d.get("__file__", "")) is str and d.get("__file__", "") == row.file,
              "MODULE_COHERENCY")
        if row.spec is not None:
            _need(type(row.spec.name) is str and row.spec.name == spec_name
                  and type(row.spec.origin) is str and row.spec.origin == row.origin
                  and row.spec.loader is row.loader, "MODULE_COHERENCY")
            locations = row.spec.submodule_search_locations
            _need(locations is None or (type(locations) in (tuple, list) and len(locations) <= MAX_RECORDS))
            actual_locations = () if locations is None else tuple(locations)
            _strings(actual_locations)
            _need(actual_locations == row.locations, "MODULE_COHERENCY")
        else:
            _need(row.kind == "CONTROL" and row.origin == "" and row.locations == (), "MODULE_COHERENCY")
        if row.kind == "CONTROL":
            _need(row.name in ("__main__", "dgn007_import_runtime_profile")
                  and (row.loader is None or type(row.loader) is SourceFileLoader), "CONTROL_MISMATCH")
        if row.kind == "BUILTIN":
            _need(row.loader is BuiltinImporter and row.origin == "built-in" and row.locations == (), "MODULE_COHERENCY")
        elif row.kind == "FROZEN":
            _need(row.loader is FrozenImporter and row.origin == "frozen", "MODULE_COHERENCY")
        elif row.kind in ("SOURCE", "EXTENSION"):
            _need(type(row.loader) is (SourceFileLoader if row.kind == "SOURCE" else ExtensionFileLoader)
                  and row.origin == row.file, "MODULE_COHERENCY")
            _absolute(row.origin)
            for p in row.locations:
                _absolute(p)
        names.append(row.name)
    _need(names == sorted(set(names)))
    by_name = {row.name: row for row in value}
    for row in value:
        if row.loader is FrozenImporter and row.name in FROZEN_NAMES:
            companion = FROZEN_NAMES[row.name][1]
            if companion in by_name:
                _need(row.module is by_name[companion].module and row.spec is by_name[companion].spec,
                      "MODULE_COHERENCY")


def _files(value):
    _need(type(value) is tuple and len(value) <= 2)
    total, paths = 0, []
    for row in value:
        _need(type(row) is FileDigest)
        _text(row.path)
        _absolute(row.path)
        _need(type(row.size) is int and 0 <= row.size <= MAX_FILE)
        _need(type(row.sha256) is str and len(row.sha256) == 64
              and all(c in "0123456789abcdef" for c in row.sha256))
        total += row.size
        paths.append(row.path)
    _need(total <= MAX_TOTAL and len(paths) == len(set(paths)))


def _shape(value, expected):
    _need(type(value) is (DeclaredProfile if expected else Observation))
    _need(type(value.token) is bytes and len(value.token) == 32)
    for item in (value.implementation, value.executable, value.abi):
        _text(item)
    _need(type(value.version) is tuple and len(value.version) == 3
          and all(type(n) is int and 0 <= n <= 999 for n in value.version))
    _strings(value.prefixes)
    _need(value.abi != "", "INTERPRETER_MISMATCH")
    _need(len(value.prefixes) == 4)
    _strings(value.paths)
    _absolute(value.executable)
    _absolute(value.executable_target)
    for p in value.paths + value.prefixes:
        _absolute(p)
    _need(type(value.finders) is tuple and len(value.finders) == 3
          and all(a is b for a, b in zip(value.finders, (BuiltinImporter, FrozenImporter, PathFinder))))
    _need(type(value.hooks) is tuple and len(value.hooks) == 2
          and value.hooks[0] is zipimporter and type(value.hooks[1]) is FunctionType)
    _records(value.modules)
    _files(value.files)
    if expected:
        _text(value.assumption)
        _need(value.assumption == ASSUMPTION, "TRUST_UNDECLARED")
        _strings(value.roots)
        _strings(value.controls)
        _need(len(value.controls) <= 2 and all(n in ("__main__", "dgn007_import_runtime_profile")
              for n in value.controls) and len(value.controls) == len(set(value.controls)), "CONTROL_MISMATCH")
        _text(value.inert_zip)
        _need(len(value.roots) == 2 and len(set(value.roots)) == 2)
        for p in value.roots + (value.inert_zip,):
            _absolute(p)
        _need(not value.files or value.files[0].path == value.executable_target, "HASH_PATH_MISMATCH")
        _need(len(value.files) < 2 or _under(value.files[1].path, value.roots), "HASH_PATH_MISMATCH")
    else:
        _text(value.platform)
        _need(type(value.flags) is tuple and len(value.flags) == 6
              and all(type(n) is int and 0 <= n <= 1 for n in value.flags))


def _under(path, roots):
    return (path.startswith("/") and all(part not in (".", "..") for part in path.split("/"))
            and any(path == root or path.startswith(root.rstrip("/") + "/") for root in roots))


def _compare(expected, obs):
    _shape(expected, True)
    _shape(obs, False)
    _need(obs.platform == "linux", "UNSUPPORTED_PLATFORM")
    _need(expected.implementation == obs.implementation == "cpython"
          and expected.version == obs.version and expected.version[:2] == (3, 12), "INTERPRETER_MISMATCH")
    _need(obs.flags == (1, 1, 1, 1, 1, 0), "FLAGS_MISMATCH")
    for name in ("token", "executable", "executable_target", "prefixes", "abi", "paths", "files"):
        _need(getattr(expected, name) == getattr(obs, name), "PROFILE_MISMATCH")
    _need(all(a is b for a, b in zip(expected.finders, obs.finders))
          and all(a is b for a, b in zip(expected.hooks, obs.hooks)), "HOOK_MISMATCH")
    _need(len(expected.modules) == len(obs.modules), "MODULE_MISMATCH")
    for a, b in zip(expected.modules, obs.modules):
        _need((a.name, a.origin, a.file, a.kind, a.locations) ==
              (b.name, b.origin, b.file, b.kind, b.locations)
              and a.module is b.module and a.spec is b.spec and a.loader is b.loader, "MODULE_MISMATCH")
        _need(not (b.name == "Tests" or b.name.startswith("Tests.") or b.name in (
            "run_dgn007_automated_setup", "execution_target", "docker_sqlcmd_proxy", "run_demo",
            "orchestrate_sessions", "sqlcmd_process")), "OWN_MODULE_CACHED")
        if b.kind == "CONTROL":
            _need(b.name in expected.controls, "CONTROL_MISMATCH")
        elif b.kind in ("SOURCE", "EXTENSION"):
            _need(_under(b.origin, expected.roots) and _under(b.file, expected.roots)
                  and all(_under(p, expected.roots) for p in b.locations), "ORIGIN_MISMATCH")
    _need(all(p in expected.roots or p == expected.inert_zip for p in obs.paths), "PATH_MISMATCH")


def validate_profile(expected: DeclaredProfile, observation: Observation) -> ProfileReport:
    """Reiner Vergleich; Vertrauen und echte Observation werden nicht hergestellt."""
    try:
        _compare(expected, observation)
    except _Failure as error:
        return ProfileReport("REJECTED_PROFILE", str(error))
    except (AttributeError, TypeError, ValueError, UnicodeError):
        return ProfileReport("REJECTED_PROFILE", "INVALID_RECORD")
    return ProfileReport("MATCHED_DECLARED_BASELINE", "NONE", True)


def _module(name, module, controls):
    _need(type(name) is str and type(module) is ModuleType)
    d = module.__dict__
    spec, loader = d.get("__spec__"), d.get("__loader__")
    _need(spec is None or type(spec) is ModuleSpec)
    origin = "" if spec is None else spec.origin
    file = d.get("__file__", "")
    _text(origin)
    _text(file)
    _text(d.get("__name__"))
    if spec is not None:
        _text(spec.name)
    module_name, spec_name = FROZEN_NAMES.get(name, (name, name)) if loader is FrozenImporter else (name, name)
    _need(d.get("__name__") == module_name and (spec is None or
          (spec.name == spec_name and spec.loader is loader)), "MODULE_COHERENCY")
    raw_locations = None if spec is None else spec.submodule_search_locations
    _need(raw_locations is None or (type(raw_locations) in (tuple, list)
          and len(raw_locations) <= MAX_RECORDS))
    locations = () if raw_locations is None else tuple(raw_locations)
    _strings(locations)
    if name in controls:
        kind = "CONTROL"
    elif loader is BuiltinImporter:
        kind = "BUILTIN"
    elif loader is FrozenImporter:
        kind = "FROZEN"
    elif type(loader) is SourceFileLoader:
        kind = "SOURCE"
        _need(origin == file, "MODULE_COHERENCY")
    elif type(loader) is ExtensionFileLoader:
        kind = "EXTENSION"
        _need(origin == file, "MODULE_COHERENCY")
    else:
        raise _Failure("UNKNOWN_LOADER")
    return ModuleRecord(name, origin, file, kind, locations, module, spec, loader)


def _capture(expected, files):
    _need(type(sys.modules) is dict and len(sys.modules) <= MAX_RECORDS, "RECORD_LIMIT")
    snapshot = sys.modules.copy()
    _need(len(snapshot) <= MAX_RECORDS, "RECORD_LIMIT")
    for name in snapshot:
        _text(name)
    for sequence in (sys.path, sys.meta_path, sys.path_hooks):
        _need(type(sequence) in (list, tuple) and len(sequence) <= MAX_RECORDS)
    for path in sys.path:
        _text(path)
    modules = tuple(_module(n, m, expected.controls) for n, m in sorted(snapshot.items()))
    return Observation(expected.token, sys.platform, sys.implementation.name, tuple(sys.version_info[:3]),
                       sys.executable, os.path.realpath(sys.executable),
                       (sys.prefix, sys.exec_prefix, sys.base_prefix, sys.base_exec_prefix),
                       sysconfig.get_config_var("SOABI") or "", (sys.flags.isolated, sys.flags.no_site,
                       int(sys.dont_write_bytecode), sys.flags.ignore_environment, int(sys.flags.safe_path),
                       sys.flags.optimize), tuple(sys.path), tuple(sys.meta_path), tuple(sys.path_hooks), modules, files)


def observe_current_interpreter(expected: DeclaredProfile) -> ProfileReport:
    """Nur aktuelle Kontrollruntime; kein Start, Resolver oder Import eines Kandidaten."""
    if type(sys.platform) is not str:
        return ProfileReport("REJECTED_PROFILE", "INVALID_RECORD")
    if sys.platform != "linux":
        return ProfileReport("REJECTED_PROFILE", "UNSUPPORTED_PLATFORM")
    try:
        _shape(expected, True)
        _need(all(os.path.isabs(p) and os.path.isdir(p) for p in expected.roots), "ROOT_MISMATCH")
        _need(all(os.path.realpath(p) == p for p in expected.roots), "ROOT_MISMATCH")
        _need(os.path.isabs(expected.executable) and os.path.isfile(expected.executable), "INTERPRETER_MISMATCH")
        _need(os.path.realpath(expected.executable) == expected.executable_target, "INTERPRETER_MISMATCH")
        _need(os.path.isabs(expected.inert_zip) and not os.path.lexists(expected.inert_zip), "ZIP_MISMATCH")
        before = _capture(expected, expected.files)
        _compare(expected, before)
        rows, total = [], 0
        for item in expected.files:
            _need(item.path == expected.executable_target or _under(item.path, expected.roots), "HASH_PATH_MISMATCH")
            _need(not os.path.islink(item.path) and os.path.isfile(item.path), "HASH_FILE_MISMATCH")
            _need(os.path.realpath(item.path) == item.path, "HASH_FILE_MISMATCH")
            digest, size = hashlib.sha256(), 0
            with open(item.path, "rb") as stream:
                while True:
                    chunk = stream.read(min(65536, MAX_FILE - size + 1, MAX_TOTAL - total + 1))
                    if not chunk:
                        break
                    size += len(chunk)
                    total += len(chunk)
                    _need(size <= MAX_FILE and total <= MAX_TOTAL, "FILE_LIMIT")
                    digest.update(chunk)
            rows.append(FileDigest(item.path, size, digest.hexdigest()))
        after = _capture(expected, tuple(rows))
        _compare(expected, after)
    except _Failure as error:
        return ProfileReport("REJECTED_PROFILE", str(error))
    except (OSError, AttributeError, TypeError, ValueError, UnicodeError):
        return ProfileReport("REJECTED_PROFILE", "OBSERVATION_FAILED")
    return ProfileReport("MATCHED_DECLARED_BASELINE", "NONE", True)
