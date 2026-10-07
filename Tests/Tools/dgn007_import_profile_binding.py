"""Begrenzter deklarativer Parent-/Worker-Vergleich ohne Runtimebeobachtung.

Der separat gehaltene Kontrollkontext ist eine Callerannahme. Gleichheit
attestiert weder Herkunft noch Transfer, Consumption, Trust oder UsedBytes.
Keine Worker, Datei-/Runtimeabfragen oder Änderungen am Input82-Protokoll.
"""
from dataclasses import dataclass, field, fields
import hashlib
import json

import dgn007_import_probe_input as input82

MAX_RECORDS = 256
MAX_FIELD = 4096
MAX_METADATA = 16384
HEADER_SIZE = 16
ASSUMPTION = "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME"
ENTRIES = ("run_dgn007_automated_setup", "docker_sqlcmd_proxy", "run_demo")
OWN_NAMES = frozenset(name for name, _ in input82.MODULES) | {"Tests", "Tests.Contracts"}
FROZEN_NAMES = {
    "_frozen_importlib": ("importlib._bootstrap", "_frozen_importlib"),
    "importlib._bootstrap": ("importlib._bootstrap", "_frozen_importlib"),
    "_frozen_importlib_external": ("importlib._bootstrap_external", "_frozen_importlib_external"),
    "importlib._bootstrap_external": ("importlib._bootstrap_external", "_frozen_importlib_external"),
    "_collections_abc": ("collections.abc", "_collections_abc"),
    "collections.abc": ("collections.abc", "_collections_abc"),
    "os.path": ("posixpath", "posixpath"),
}
ALIAS_PAIRS = tuple(tuple(sorted(p)) for p in (
    ("_frozen_importlib", "importlib._bootstrap"),
    ("_frozen_importlib_external", "importlib._bootstrap_external"),
    ("_collections_abc", "collections.abc"), ("os.path", "posixpath")))


@dataclass(frozen=True, slots=True, repr=False)
class FileFingerprint:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True, slots=True, repr=False)
class ModuleDeclaration:
    name: str
    moduleName: str
    specName: str | None
    origin: str
    file: str
    kind: str
    locations: tuple
    loader: str
    loaderName: str = ""
    loaderPath: str = ""
    aliasGroup: tuple = ()


@dataclass(frozen=True, slots=True, repr=False)
class InstallationDeclaration:
    assumption: str
    platform: str
    implementation: str
    version: tuple
    executable: str
    executable_target: str
    prefixes: tuple
    abi: str
    paths: tuple
    roots: tuple
    inert_zip: str
    flags: tuple
    finders: tuple
    hooks: tuple
    files: tuple = ()


@dataclass(frozen=True, slots=True, repr=False)
class WorkerDeclaration:
    ordinal: int
    entry: str
    phase: str
    installation: InstallationDeclaration
    controls: tuple
    modules: tuple


@dataclass(frozen=True, slots=True, repr=False)
class SourceDescriptor:
    ordinal: int
    module: str
    member: str
    size: int
    sha256: str


@dataclass(frozen=True, slots=True, repr=False)
class BindingContext:
    commit: str
    raw27_binding: str
    source_profile: str
    nonce: bytes
    modules: tuple
    ordinal: int
    entry: str
    phase: str


@dataclass(frozen=True, slots=True, repr=False)
class ReportedProfile:
    context: BindingContext
    installation: InstallationDeclaration
    controls: tuple
    modules: tuple


@dataclass(frozen=True, slots=True)
class BindingReport:
    status: str
    issue: str
    assumption: str = ""
    installation_digest: str = ""
    worker_digest: str = ""
    context_digest: str = ""
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    trust_attested: bool = field(default=False, init=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


class BindingRejected(ValueError):
    """Nur feste technische Labels; keine Rohfehlerkette."""


def _need(ok, label="INVALID_RECORD"):
    if not ok:
        raise BindingRejected(label)


def _text(v):
    _need(type(v) is str and len(v) <= MAX_FIELD)
    _need("\0" not in v and len(v.encode("utf-8")) <= MAX_FIELD)


def _integer(v, lower, upper):
    _need(type(v) is int and lower <= v <= upper)


def _tuple(v, count=None):
    _need(type(v) is tuple and len(v) <= MAX_RECORDS and (count is None or len(v) == count))


def _strings(v, count=None):
    _tuple(v, count)
    for s in v:
        _text(s)


def _hex(v, n):
    _text(v)
    _need(len(v) == n and all(c in "0123456789abcdef" for c in v))


def _absolute(v):
    _text(v)
    _need(v.startswith("/") and "//" not in v and (v == "/" or not v.endswith("/"))
          and all(p not in (".", "..") for p in v.split("/")), "PATH_FORM")


def _under(v, roots):
    return any(v == root or v.startswith(root.rstrip("/") + "/") for root in roots)


def _selector(ordinal, entry, phase):
    _integer(ordinal, 1, 3)
    _text(entry)
    _text(phase)
    _need(entry == ENTRIES[ordinal - 1] and phase == "PRE_IMPORT", "CONTEXT_FORM")


def _installation(v):
    _need(type(v) is InstallationDeclaration)
    for key in ("assumption", "platform", "implementation", "abi"):
        _text(getattr(v, key))
    _need(v.assumption == ASSUMPTION and v.platform == "linux" and v.implementation == "cpython"
          and v.abi != "", "INSTALLATION_FORM")
    _tuple(v.version, 3)
    for n in v.version:
        _integer(n, 0, 999)
    _need(v.version[:2] == (3, 12), "INSTALLATION_FORM")
    _strings(v.prefixes, 4)
    _strings(v.roots, 2)
    _strings(v.paths)
    _need(len(set(v.roots)) == 2, "INSTALLATION_FORM")
    for path in v.prefixes + v.roots + v.paths + (v.executable, v.executable_target, v.inert_zip):
        _absolute(path)
    _need(all(p in v.roots or p == v.inert_zip for p in v.paths), "PATH_FORM")
    _tuple(v.flags, 6)
    for n in v.flags:
        _integer(n, 0, 1)
    _strings(v.finders, 3)
    _strings(v.hooks, 2)
    _need(v.flags == (1, 1, 1, 1, 1, 0) and v.finders == ("BUILTIN", "FROZEN", "PATH")
          and v.hooks == ("ZIPIMPORTER", "FILEFINDER"), "INSTALLATION_FORM")
    _tuple(v.files)
    _need(len(v.files) <= 2, "FILE_FORM")
    total, names = 0, []
    for index, row in enumerate(v.files):
        _need(type(row) is FileFingerprint)
        _absolute(row.path)
        _integer(row.size, 0, 33554432)
        _hex(row.sha256, 64)
        _need(row.path == v.executable_target if index == 0 else _under(row.path, v.roots), "FILE_FORM")
        total += row.size
        names.append(row.path)
    _need(total <= 67108864 and len(set(names)) == len(names), "FILE_FORM")


def _module(row, roots):
    _need(type(row) is ModuleDeclaration)
    for key in ("name", "moduleName", "origin", "file", "kind", "loader", "loaderName", "loaderPath"):
        _text(getattr(row, key))
    if row.specName is not None:
        _text(row.specName)
    _strings(row.locations)
    _strings(row.aliasGroup)
    if row.file:
        _absolute(row.file)
    for path in row.locations:
        _absolute(path)
    _need(row.name != "" and row.name not in OWN_NAMES, "OWN_MODULE_CACHED")
    _need(row.kind in ("BUILTIN", "FROZEN", "SOURCE", "EXTENSION", "CONTROL"), "MODULE_FORM")
    _need(row.loader in ("NONE", "BUILTIN", "FROZEN", "SOURCE", "EXTENSION"), "MODULE_FORM")
    module_name, spec_name = FROZEN_NAMES.get(row.name, (row.name, row.name)) if row.kind == "FROZEN" else (row.name, row.name)
    _need(row.moduleName == module_name, "MODULE_FORM")
    if row.specName is None:
        _need(row.kind == "CONTROL" and row.origin == "" and row.locations == (), "MODULE_FORM")
    else:
        _need(row.specName == spec_name, "MODULE_FORM")
    if row.loader in ("SOURCE", "EXTENSION"):
        _need(row.loaderName == row.name and row.loaderPath == row.file, "MODULE_FORM")
        _absolute(row.file)
    else:
        _need(row.loaderName == row.loaderPath == "", "MODULE_FORM")
    if row.kind == "BUILTIN":
        _need(row.loader == "BUILTIN" and row.origin == "built-in" and row.locations == (), "MODULE_FORM")
    elif row.kind == "FROZEN":
        _need(row.loader == "FROZEN" and row.origin == "frozen", "MODULE_FORM")
    elif row.kind in ("SOURCE", "EXTENSION"):
        _need(row.loader == row.kind and row.origin == row.file, "MODULE_FORM")
        for path in (row.origin, row.file) + row.locations:
            _absolute(path)
            _need(_under(path, roots), "PATH_FORM")
    else:
        _need(row.loader in ("NONE", "SOURCE"), "MODULE_FORM")
        if row.file:
            _absolute(row.file)
        if row.specName is not None:
            _absolute(row.origin)
        for path in row.locations:
            _absolute(path)
    _need(row.aliasGroup == () or (row.kind == "FROZEN" and row.aliasGroup in ALIAS_PAIRS
          and row.name in row.aliasGroup), "ALIAS_FORM")


def _inventory(controls, modules, roots):
    _strings(controls)
    _tuple(modules)
    _need(len(modules) > 0, "INVENTORY_FORM")
    names = []
    for row in modules:
        _module(row, roots)
        names.append(row.name)
    _need(names == sorted(set(names)), "INVENTORY_FORM")
    _need(len(set(controls)) == len(controls), "CONTROL_FORM")
    by_name = {row.name: row for row in modules}
    _need(set(controls) == {row.name for row in modules if row.kind == "CONTROL"}, "CONTROL_FORM")
    for row in modules:
        if row.aliasGroup:
            for name in row.aliasGroup:
                _need(name in by_name and by_name[name].kind == "FROZEN"
                      and by_name[name].aliasGroup == row.aliasGroup, "ALIAS_FORM")


def _worker(v):
    _need(type(v) is WorkerDeclaration)
    _selector(v.ordinal, v.entry, v.phase)
    _installation(v.installation)
    _inventory(v.controls, v.modules, v.installation.roots)


def _context(v):
    _need(type(v) is BindingContext)
    _hex(v.commit, 40)
    _hex(v.raw27_binding, 64)
    _text(v.source_profile)
    _need(v.source_profile == "dgn007-docker-sql-only/v1", "CONTEXT_FORM")
    _need(type(v.nonce) is bytes and len(v.nonce) == 32)
    _selector(v.ordinal, v.entry, v.phase)
    _tuple(v.modules, 9)
    total = 0
    for index, (row, (module, member)) in enumerate(zip(v.modules, input82.MODULES)):
        _need(type(row) is SourceDescriptor)
        _integer(row.ordinal, 0, 8)
        _text(row.module)
        _text(row.member)
        _hex(row.sha256, 64)
        _integer(row.size, 0, 131072)
        _need((row.ordinal, row.module, row.member) == (index, module, member), "CONTEXT_FORM")
        total += row.size
    _need(total <= 1048576, "CONTEXT_FORM")


def _reported(v):
    _need(type(v) is ReportedProfile)
    _context(v.context)
    _installation(v.installation)
    _inventory(v.controls, v.modules, v.installation.roots)


def _value(v):
    # Nur nach vollständig erfolgreicher Formprüfung aufrufen.
    if type(v) is bytes:
        return v.hex()
    if type(v) is tuple:
        return tuple(_value(item) for item in v)
    if type(v) in (FileFingerprint, ModuleDeclaration, InstallationDeclaration,
                   WorkerDeclaration, SourceDescriptor, BindingContext, ReportedProfile):
        return {f.name: _value(getattr(v, f.name)) for f in fields(type(v))}
    return v


def _canonical(v):
    chunks, size = [], HEADER_SIZE
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    for piece in encoder.iterencode(v):
        # Keine vollständige dumps-Aufnahme des potentiell großen Profils.
        size += len(piece)
        _need(size <= MAX_METADATA, "METADATA_LIMIT")
        chunks.append(piece.encode("ascii"))
    return b"".join(chunks)


def _input_metadata(context):
    v = dict(protocol=input82.PROTOCOL, commit=context.commit, raw27_binding=context.raw27_binding,
             source_profile=context.source_profile, nonce=context.nonce.hex(), modules=list(_value(context.modules)))
    v["context_sha256"] = hashlib.sha256(input82._canonical(v)).hexdigest()
    return v


def _derive(prepared, ordinal):
    _integer(ordinal, 1, 3)
    metadata = input82._metadata(prepared)  # Rein: vollständige Form und tatsächliche gehaltene Rawhashes.
    result = BindingContext(metadata["commit"], metadata["raw27_binding"], metadata["source_profile"],
                            prepared.nonce, tuple(SourceDescriptor(**r) for r in metadata["modules"]),
                            ordinal, ENTRIES[ordinal - 1], "PRE_IMPORT")
    _context(result)
    return result


def derive_binding_context(prepared: input82.PreparedInput, ordinal: int) -> BindingContext:
    """Kontext aus geprüftem Parentinput; kein früherer PASS-/Herkunftsnachweis."""
    issue = None
    try:
        return _derive(prepared, ordinal)
    except (BindingRejected, input82.InputRejected):
        issue = "PARENT_INPUT_INVALID"
    except (AttributeError, TypeError, ValueError, UnicodeError):
        issue = "INVALID_RECORD"
    # Außerhalb des except: keine Payload in context/cause der öffentlichen Ausnahme.
    raise BindingRejected(issue)


def match_reported_profile(expected: WorkerDeclaration, reported: ReportedProfile,
                           context: BindingContext) -> BindingReport:
    """Nur skalarer Match gegen getrennte Callerwahl; Replay bleibt möglich."""
    issues = []
    for operation, value in ((_worker, expected), (_reported, reported), (_context, context)):
        try:
            operation(value)
        except BindingRejected as error:
            issues.append(str(error))
        except (AttributeError, TypeError, ValueError, UnicodeError):
            issues.append("INVALID_RECORD")
    if issues:
        return BindingReport("REJECTED_REPORTED_PROFILE", issues[0])
    try:
        ew, rp, bc = _value(expected), _value(reported), _value(context)
        _canonical(dict(input=_input_metadata(context), worker=ew, context=bc))
        _canonical(rp)
        _need((expected.ordinal, expected.entry, expected.phase) ==
              (context.ordinal, context.entry, context.phase), "CONTEXT_MISMATCH")
        _need(reported.context == context, "CONTEXT_MISMATCH")
        _need(reported.installation == expected.installation and reported.controls == expected.controls
              and reported.modules == expected.modules, "PROFILE_MISMATCH")
        installation_digest = hashlib.sha256(_canonical(["installation-declaration", ew["installation"]])).hexdigest()
        worker_digest = hashlib.sha256(_canonical(["worker-declaration", ew])).hexdigest()
        context_digest = hashlib.sha256(_canonical(["profile-binding-context", bc])).hexdigest()
    except BindingRejected as error:
        return BindingReport("REJECTED_REPORTED_PROFILE", str(error))
    return BindingReport("MATCHED_REPORTED_DECLARATION", "NONE", ASSUMPTION,
                         installation_digest, worker_digest, context_digest)
