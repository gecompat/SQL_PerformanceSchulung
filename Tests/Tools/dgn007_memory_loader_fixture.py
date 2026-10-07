#!/usr/bin/env python3
"""Tatsächlicher Loader-Komponententest ausschließlich fester synthetischer Bytes.

Kein PreparedInput, DGN-Import, Finder, Suchpfad- oder Modulcacheumbau. Die
kontrollseitigen Objekte und der Interpreter sind vertrauenswürdig; Receipts
sind keine Signatur und der Loader ist keine Sandbox. Es gibt keine Prozess-,
Cleanup- oder Harddeadlinezusage. DGN-Attestationsflags bleiben false.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec
import json
import secrets
from types import CodeType, ModuleType

MAX_SOURCE_BYTES = 4096
MAX_RECEIPTS = 8


class FixtureCase(Enum):
    LF_SUCCESS = "LF_SUCCESS"
    CRLF_SUCCESS = "CRLF_SUCCESS"
    COMPILE_FAILURE = "COMPILE_FAILURE"
    EXEC_FAILURE = "EXEC_FAILURE"


@dataclass(frozen=True, slots=True)
class _Source:
    case: FixtureCase
    module: str
    member: str
    body: bytes = field(repr=False)
    sha256: str


def _source(case, suffix, body):
    return _Source(case, "dgn007_synthetic_" + suffix, "Synthetic/" + suffix + ".py",
                   body, hashlib.sha256(body).hexdigest())


_SOURCES = (
    _source(FixtureCase.LF_SUCCESS, "lf", b"SYNTHETIC_VALUE = 7\n"),
    _source(FixtureCase.CRLF_SUCCESS, "crlf", b"SYNTHETIC_VALUE = 7\r\n"),
    _source(FixtureCase.COMPILE_FAILURE, "compile_failure", b"return\n"),
    _source(FixtureCase.EXEC_FAILURE, "exec_failure", b"raise RuntimeError('Synthetic fixture failure')\n"),
)


@dataclass(frozen=True, slots=True)
class LoaderReceipt:
    sequence: int
    phase: str
    fixture: str
    module: str
    member: str
    raw_sha256: str
    nonce: bytes = field(repr=False)
    context_digest: str
    object_slot: int


@dataclass(frozen=True, slots=True)
class FixtureReport:
    status: str
    issue: str
    receipts: tuple[LoaderReceipt, ...] = ()
    claim: str = field(default="SYNTHETIC_LOADER_COMPONENT_ONLY", init=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


class _Rejected(ValueError):
    pass


def _require(condition, issue):
    if not condition:
        raise _Rejected(issue)


def _catalog(case):
    _require(type(case) is FixtureCase and any(case is item for item in FixtureCase), "FIXTURE_CASE")
    return next(s for s in _SOURCES if s.case is case)


def _checked_source(source):
    _require(type(source) is _Source, "SOURCE_SHAPE")
    expected = _catalog(getattr(source, "case", None))
    module, member = getattr(source, "module", None), getattr(source, "member", None)
    body, digest = getattr(source, "body", None), getattr(source, "sha256", None)
    _require(type(module) is str and module == expected.module
             and type(member) is str and member == expected.member, "SOURCE_MAPPING")
    _require(type(body) is bytes and len(body) <= MAX_SOURCE_BYTES, "SOURCE_LIMIT")
    _require(type(digest) is str and digest == expected.sha256
             and hashlib.sha256(body).hexdigest() == expected.sha256
             and body == expected.body, "SOURCE_BYTES")
    return source


def _context(source, nonce):
    _checked_source(source)
    _require(type(nonce) is bytes and len(nonce) == 32, "NONCE_SHAPE")
    value = ["dgn007-synthetic-loader/v1", source.case.value, source.module,
             source.member, source.sha256, nonce.hex()]
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")).hexdigest()


def _receipt_equal(actual, expected):
    _require(type(actual) is LoaderReceipt, "RECEIPT_BINDING")
    for name in ("sequence", "phase", "fixture", "module", "member", "raw_sha256",
                 "nonce", "context_digest", "object_slot"):
        value, required = getattr(actual, name, None), getattr(expected, name)
        _require(type(value) is type(required) and value == required, "RECEIPT_BINDING")


class _MemoryLoader(Loader):
    """Privater direct-exec_module-Pfad, kein aufrufbarer Quellenresolver."""
    def __init__(self, session):
        _require(type(session) is _Session, "SESSION_SHAPE")
        self._session = session
        self._created = False

    def create_module(self, spec):
        session = self._session
        _require(type(session) is _Session, "SESSION_SHAPE")
        _require(spec is session._spec and type(spec) is ModuleSpec, "SPEC_BINDING")
        _require(self._created is False, "DUPLICATE_CREATE")
        self._created = True
        return None

    def exec_module(self, module):
        session = self._session
        _require(type(session) is _Session, "SESSION_SHAPE")
        session._begin(module)
        # Derselbe gehaltene bytes-Input wie im unmittelbar vorherigen BEGIN.
        try:
            code = compile(session._begin_bytes, session._origin, "exec", dont_inherit=True, optimize=0)
        except Exception:
            session._state = "FAILED"
            code = None
        if code is None:
            raise _Rejected("FIXTURE_COMPILE_FAILED")
        session._compiled_code = code
        execution_failed = False
        try:
            exec(code, module.__dict__)
        except Exception:
            session._state = "FAILED"
            execution_failed = True
        if execution_failed:
            raise _Rejected("FIXTURE_EXEC_FAILED")
        session._executed_code = code
        session._complete(module)


class _Session:
    def __init__(self, case):
        self._source = _catalog(case)
        self._nonce = secrets.token_bytes(32)
        self._digest = _context(self._source, self._nonce)
        self._origin = "synthetic:/" + self._source.member
        self._state = "NEW"
        self._receipts = []
        self._loader = _MemoryLoader(self)
        self._spec = ModuleSpec(self._source.module, self._loader, origin=self._origin)
        self._module = module_from_spec(self._spec)
        self._module.__file__ = self._origin
        self._begin_object = None
        self._begin_bytes = None
        self._begin_spec = None
        self._begin_loader = None
        self._compiled_code = None
        self._executed_code = None
        self._completed_code = None

    def _binding(self, module):
        source = _checked_source(self._source)
        _require(type(self._origin) is str and self._origin == "synthetic:/" + source.member,
                 "SPEC_BINDING")
        _require(type(module) is ModuleType and module is self._module, "OBJECT_BINDING")
        namespace = module.__dict__
        _require(type(self._loader) is _MemoryLoader and self._loader._session is self
                 and type(self._spec) is ModuleSpec and namespace.get("__spec__") is self._spec
                 and namespace.get("__loader__") is self._loader and self._spec.loader is self._loader, "SPEC_BINDING")
        for actual, expected in ((namespace.get("__name__"), source.module), (self._spec.name, source.module),
                                 (namespace.get("__file__"), self._origin), (self._spec.origin, self._origin)):
            _require(type(actual) is str and actual == expected, "SPEC_BINDING")
        _require(type(self._digest) is str and _context(source, self._nonce) == self._digest, "CONTEXT_BINDING")

    def _receipt(self, phase):
        _require(type(self._receipts) is list and len(self._receipts) < MAX_RECEIPTS, "RECEIPT_LIMIT")
        source = self._source
        return LoaderReceipt(len(self._receipts) + 1, phase, source.case.value, source.module,
                             source.member, source.sha256, self._nonce, self._digest, 1)

    def _begin(self, module):
        _require(type(self._state) is str and self._state == "NEW"
                 and type(self._receipts) is list and len(self._receipts) == 0, "LIFECYCLE_BEGIN")
        self._binding(module)
        self._begin_object = module
        self._begin_bytes = self._source.body
        self._begin_spec = self._spec
        self._begin_loader = self._loader
        self._receipts.append(self._receipt("BEGIN"))
        self._state = "BEGUN"

    def _complete(self, module):
        _require(type(self._state) is str and self._state == "BEGUN"
                 and type(self._receipts) is list and len(self._receipts) == 1, "LIFECYCLE_COMPLETE")
        self._binding(module)
        _require(type(self._compiled_code) is CodeType and self._executed_code is self._compiled_code,
                 "MISSING_EXECUTION")
        begin = self._receipts[0]
        expected = LoaderReceipt(1, "BEGIN", self._source.case.value, self._source.module,
                                 self._source.member, self._source.sha256, self._nonce, self._digest, 1)
        _receipt_equal(begin, expected)
        _require(module is self._begin_object and self._source.body is self._begin_bytes
                 and self._spec is self._begin_spec and self._loader is self._begin_loader, "RECEIPT_BINDING")
        _require(self._source.case in (FixtureCase.LF_SUCCESS, FixtureCase.CRLF_SUCCESS)
                 and type(module.__dict__.get("SYNTHETIC_VALUE")) is int
                 and module.__dict__["SYNTHETIC_VALUE"] == 7, "FIXTURE_EFFECT")
        self._receipts.append(self._receipt("COMPLETE"))
        self._completed_code = self._executed_code
        self._state = "COMPLETED"

    def _report(self):
        _require(type(self._state) is str and self._state == "COMPLETED"
                 and type(self._receipts) is list and len(self._receipts) == 2, "MISSING_COMPLETE")
        self._binding(self._module)
        _require(self._module is self._begin_object and self._source.body is self._begin_bytes
                 and self._spec is self._begin_spec and self._loader is self._begin_loader,
                 "RECEIPT_BINDING")
        _require(type(self._compiled_code) is CodeType and self._executed_code is self._compiled_code
                 and self._executed_code is self._completed_code,
                 "MISSING_EXECUTION")
        _require(type(self._module.__dict__.get("SYNTHETIC_VALUE")) is int
                 and self._module.__dict__["SYNTHETIC_VALUE"] == 7, "FIXTURE_EFFECT")
        expected = self._receipt_end()
        _receipt_equal(self._receipts[0], LoaderReceipt(1, "BEGIN", expected.fixture, expected.module,
                        expected.member, expected.raw_sha256, expected.nonce, expected.context_digest, 1))
        _receipt_equal(self._receipts[1], expected)
        return FixtureReport("PASS_SYNTHETIC_LOADER", "NONE", tuple(self._receipts))

    def _receipt_end(self):
        source = self._source
        return LoaderReceipt(2, "COMPLETE", source.case.value, source.module,
                             source.member, source.sha256, self._nonce, self._digest, 1)


def exercise_fixture(case: FixtureCase) -> FixtureReport:
    """Einziger öffentlicher Ausführungseinstieg; nimmt niemals Quellbytes an."""
    session = None
    try:
        _catalog(case)
        try:
            session = _Session(case)
        except (OSError, ValueError, TypeError):
            return FixtureReport("FAIL_SYNTHETIC_LOADER", "PREPARE_FIXTURE")
        session._loader.exec_module(session._module)
        return session._report()
    except _Rejected as error:
        issue = str(error)
    except Exception:
        issue = "INVALID_FIXTURE_RECORD"
    receipts = tuple(session._receipts) if session is not None else ()
    return FixtureReport("FAIL_SYNTHETIC_LOADER", issue, receipts)
