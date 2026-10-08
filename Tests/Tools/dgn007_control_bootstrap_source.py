"""Erzeugung einer gebundenen Kontrollquelle, ohne Aufnahme oder Ausführung.

Profilbytes und Locator sind separat ausgewählte, vertraute Kontrollinputs.
Das Template ist keine Sandbox, kein Worker und kein Herkunftsbeleg. Erst
synthetische Tests prüfen seinen einzelnen Read-/Compile-/Exec-Vorschnitt.
"""
from dataclasses import dataclass, field
import hashlib

MAX_PROFILE_BYTES = 131072
MAX_SCRIPT_BYTES = 131072
MAX_LOCATOR_BYTES = 4096
CONTROL_NAME = "dgn007_import_runtime_profile"


@dataclass(frozen=True, slots=True, repr=False)
class BootstrapSource:
    source: bytes = field(repr=False)
    profile_raw: bytes = field(repr=False)
    logical_profile: str = field(repr=False)
    source_sha256: str
    profile_sha256: str
    source_size: int
    status: str = field(default="BUILT_CONTROL_BOOTSTRAP_SOURCE", init=False)
    claim: str = field(default="GENERATED_CONTROL_SOURCE_ONLY", init=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    trust_assumed: bool = field(default=True, init=False)
    trust_attested: bool = field(default=False, init=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)

    def __repr__(self):
        return "BootstrapSource(GENERATED_CONTROL_SOURCE_ONLY)"


class BootstrapSourceRejected(ValueError):
    """Fester Fehlercode ohne Locator, Rawbytes oder Exceptionkette."""


def _need(value, label):
    if not value:
        raise BootstrapSourceRejected(label) from None


def _locator(value):
    _need(type(value) is str, "LOCATOR_FORM")
    _need(0 < len(value) <= MAX_LOCATOR_BYTES, "LOCATOR_FORM")
    issue = None
    try:
        size = len(value.encode("utf-8", "strict"))
    except UnicodeError:
        issue = "LOCATOR_FORM"
    if issue is not None:
        raise BootstrapSourceRejected(issue) from None
    _need(size <= MAX_LOCATOR_BYTES and "\0" not in value, "LOCATOR_FORM")
    _need(value.startswith("/") and not value.endswith("/")
          and "\\" not in value and "//" not in value
          and all(part not in ("", ".", "..") for part in value[1:].split("/")),
          "LOCATOR_FORM")


# Ausschließlich diese fünf direkten Imports; keine Projektmodule im Template.
_PREFIX = '''"""Gebundener Kontrollquellenvorschnitt; keine Profilaufnahme oder Workerroute."""
import importlib.util
import sys
import sysconfig
import json
import struct
'''

_BODY = '''
_CONTROL_NAME = "dgn007_import_runtime_profile"
_SOURCE_CAP = 131072
_CONTROL_ATTEMPTED = False
_MODULE_CLASS = type(sys)


class _ControlRejected(ValueError):
    pass


def _require(condition, label):
    if not condition:
        raise _ControlRejected(label)


def _text(value, expected, label):
    _require(type(value) is str and value == expected, label)


def _dictionary(value):
    if type(value) is not dict or len(value) > 256:
        return False
    for key in value:
        if type(key) is not str or len(key) > 4096:
            return False
        try:
            if len(key.encode("utf-8", "strict")) > 4096:
                return False
        except UnicodeError:
            return False
    return True


def _coherent(module, spec, loader, loader_class, spec_class, cache, main,
              raw, code, module_class, name, filename):
    _require(type(sys) is module_class, "CONTROL_CACHE")
    _require(_dictionary(sys.modules) and sys.modules is cache, "CONTROL_CACHE")
    _require(type(main) is module_class and _dictionary(main.__dict__), "CONTROL_CACHE")
    _require(cache.get("__main__") is main and main.__dict__ is globals(), "CONTROL_CACHE")
    _require(cache.get(name) is module, "CONTROL_CACHE")
    _require(type(module) is module_class and type(spec) is spec_class
             and type(loader) is loader_class, "CONTROL_COHERENCY")
    md, sd, ld = module.__dict__, spec.__dict__, loader.__dict__
    _require(_dictionary(md) and _dictionary(sd) and _dictionary(ld), "CONTROL_COHERENCY")
    _text(md.get("__name__"), name, "CONTROL_COHERENCY")
    _text(md.get("__file__"), filename, "CONTROL_COHERENCY")
    _text(md.get("__package__"), "", "CONTROL_COHERENCY")
    _require(md.get("__spec__") is spec and md.get("__loader__") is loader
             and "__path__" not in md, "CONTROL_COHERENCY")
    _text(sd.get("name"), name, "CONTROL_COHERENCY")
    _text(sd.get("origin"), filename, "CONTROL_COHERENCY")
    _require(sd.get("loader") is loader and sd.get("submodule_search_locations") is None
             and sd.get("_set_fileattr") is True, "CONTROL_COHERENCY")
    _text(ld.get("name"), name, "CONTROL_COHERENCY")
    _text(ld.get("path"), filename, "CONTROL_COHERENCY")
    cached, spec_cached = md.get("__cached__"), sd.get("_cached")
    _require((cached is None or type(cached) is str)
             and (spec_cached is None or type(spec_cached) is str), "CONTROL_COHERENCY")
    _require(cached == spec_cached, "CONTROL_COHERENCY")
    _require(_EXPECTED_PROFILE_RAW is raw and type(code) is type(_load_bound_control.__code__),
             "CONTROL_COHERENCY")


def _load_bound_control():
    global _CONTROL_ATTEMPTED
    cache = module = spec = loader = main = None
    inserted = False
    issue = "NONE"
    phase = "CONTROL_EXEC"
    module_class = _MODULE_CLASS
    name, filename = _CONTROL_NAME, _PROFILE_FILE
    try:
        _require(_CONTROL_ATTEMPTED is False, "CONTROL_ALREADY_ATTEMPTED")
        _CONTROL_ATTEMPTED = True
        _require(type(sys) is module_class and _dictionary(sys.modules), "CONTROL_CACHE")
        cache = sys.modules
        _require(name not in cache, "CONTROL_CACHE_PRESENT")
        main = cache.get("__main__")
        _require(type(main) is module_class and _dictionary(main.__dict__)
                 and main.__dict__ is globals(), "CONTROL_CACHE")
        _text(main.__dict__.get("__name__"), "__main__", "CONTROL_CACHE")
        external = cache.get("_frozen_importlib_external")
        bootstrap = cache.get("_frozen_importlib")
        _require(type(external) is module_class and type(bootstrap) is module_class
                 and _dictionary(external.__dict__) and _dictionary(bootstrap.__dict__),
                 "CONTROL_LOADER")
        loader_class = external.__dict__.get("SourceFileLoader")
        spec_class = bootstrap.__dict__.get("ModuleSpec")
        _require(type(loader_class) is type and type(spec_class) is type, "CONTROL_LOADER")
        _text(loader_class.__name__, "SourceFileLoader", "CONTROL_LOADER")
        _text(spec_class.__name__, "ModuleSpec", "CONTROL_LOADER")
        _require(type(importlib) is module_class and _dictionary(importlib.__dict__), "CONTROL_LOADER")
        util = importlib.__dict__.get("util")
        _require(type(util) is module_class and _dictionary(util.__dict__), "CONTROL_LOADER")
        spec_factory = util.__dict__.get("spec_from_file_location")
        module_factory = util.__dict__.get("module_from_spec")
        _require(type(spec_factory) is type(_load_bound_control)
                 and type(module_factory) is type(_load_bound_control), "CONTROL_LOADER")
        _require(_dictionary(spec_factory.__globals__) and _dictionary(module_factory.__globals__),
                 "CONTROL_LOADER")
        _require(spec_factory.__globals__.get("SourceFileLoader") is loader_class
                 and module_factory.__globals__.get("ModuleSpec") is spec_class,
                 "CONTROL_LOADER")
        expected = _EXPECTED_PROFILE_RAW
        _require(type(expected) is bytes and 0 < len(expected) <= _SOURCE_CAP, "CONTROL_SOURCE_LIMIT")
        phase = "CONTROL_READ"
        with open(filename, "rb") as handle:
            raw = handle.read(_SOURCE_CAP + 1)
        _require(type(raw) is bytes and len(raw) <= _SOURCE_CAP, "CONTROL_SOURCE_LIMIT")
        _require(raw == expected, "CONTROL_SOURCE_MISMATCH")
        # Die tatsächlichen gehaltenen Readbytes werden ohne LF-/Encodingumformung kompiliert.
        phase = "CONTROL_COMPILE"
        code = compile(raw, filename, "exec", dont_inherit=True, optimize=0)
        _require(type(code) is type(_load_bound_control.__code__), "CONTROL_COMPILE")
        phase = "CONTROL_EXEC"
        loader = loader_class(name, filename)
        spec = spec_factory(name, filename, loader=loader)
        _require(type(spec) is spec_class, "CONTROL_COHERENCY")
        module = module_factory(spec)
        _require(type(module) is module_class, "CONTROL_COHERENCY")
        _require(type(sys) is module_class and _dictionary(sys.modules) and sys.modules is cache
                 and name not in cache and cache.get("__main__") is main,
                 "CONTROL_CACHE")
        cache[name] = module
        inserted = True
        _coherent(module, spec, loader, loader_class, spec_class, cache, main,
                  expected, code, module_class, name, filename)
        exec(code, module.__dict__, module.__dict__)
        _coherent(module, spec, loader, loader_class, spec_class, cache, main,
                  expected, code, module_class, name, filename)
    except _ControlRejected as error:
        labels = ("CONTROL_ALREADY_ATTEMPTED", "CONTROL_CACHE", "CONTROL_CACHE_PRESENT",
                  "CONTROL_LOADER", "CONTROL_SOURCE_LIMIT", "CONTROL_SOURCE_MISMATCH",
                  "CONTROL_COHERENCY", "CONTROL_COMPILE")
        value = error.args[0] if type(error) is _ControlRejected and len(error.args) == 1 else None
        issue = value if type(value) is str and value in labels else "CONTROL_EXEC"
    except (OSError, SyntaxError, UnicodeError):
        issue = phase
    except BaseException:
        issue = "CONTROL_EXEC"
    if issue != "NONE":
        if inserted:
            # Niemals einen fremden Ersatz oder eine fremde Cacheinstanz abbauen.
            if type(sys) is not module_class or not _dictionary(sys.modules) or sys.modules is not cache:
                issue = "CONTROL_CLEANUP"
            elif cache.get(name) is module:
                del cache[name]
                if name in cache:
                    issue = "CONTROL_CLEANUP"
            else:
                issue = "CONTROL_CLEANUP"
        return ("REJECTED_CONTROL_SOURCE", issue, None)
    return ("LOADED_BOUND_CONTROL_SOURCE", "NONE", module)


if __name__ == "__main__":
    _CONTROL_RESULT = _load_bound_control()
'''


def build_control_bootstrap(profile_raw, *, logical_profile) -> BootstrapSource:
    """Reine Erzeugung aus gewählten Kontrollbytes; kein Read, Compile oder Exec."""
    _need(type(profile_raw) is bytes, "PROFILE_TYPE")
    _need(0 < len(profile_raw) <= MAX_PROFILE_BYTES, "PROFILE_SIZE")
    _locator(logical_profile)
    # Höchstens vier Literalzeichen je Rawbyte; kein rekursiver Templateersatz.
    source = (_PREFIX + "\n_EXPECTED_PROFILE_RAW = " + repr(profile_raw)
              + "\n_PROFILE_FILE = " + ascii(logical_profile) + "\n" + _BODY).encode("utf-8")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


# Eigene additive Syntaxquelle. Kein Import des Codecs und keine Semantikroute.
_INLINE_SYNTAX = r'''
_INLINE_TAG = "pooled-binding-design/v1"
_INLINE_ROLE = "METADATA"
_INLINE_HEADER = struct.Struct(">8sII")
_INLINE_MAGIC = b"DGNC001\0"
_INLINE_METADATA_CAP = 16384
_INLINE_BODY_CAP = 1048576
_INLINE_FRAME_CAP = 1064960
_INLINE_NODES = 16368
_INLINE_DEPTH = 8
_INLINE_SEQUENCE = 256
_INLINE_TEXT = 4096


class _InlineSyntaxRejected(ValueError):
    pass


def _inline_need(ok, issue):
    if not ok:
        raise _InlineSyntaxRejected(issue) from None


class _InlineParser:
    """Begrenzte ASCIIarrays; kein allgemeiner JSONdecoder."""
    def __init__(self, data):
        self.data, self.pos, self.nodes = data, 0, 0

    def _take(self, byte):
        _inline_need(self.pos < len(self.data) and self.data[self.pos] == byte, "JSON_FORM")
        self.pos += 1

    def _hex4(self):
        _inline_need(self.pos + 4 <= len(self.data), "JSON_TEXT")
        value = 0
        for offset in range(4):
            ch = self.data[self.pos + offset]
            _inline_need(ch in b"0123456789abcdefABCDEF", "JSON_TEXT")
            value = value * 16 + int(chr(ch), 16)
        self.pos += 4
        return value

    def _string(self):
        self._take(34)
        chars, utf8 = [], 0
        escapes = {34: '"', 92: "\\", 47: "/", 98: "\b", 102: "\f",
                   110: "\n", 114: "\r", 116: "\t"}
        while True:
            _inline_need(self.pos < len(self.data), "JSON_TEXT")
            ch = self.data[self.pos]
            self.pos += 1
            if ch == 34:
                return "".join(chars)
            if ch == 92:
                _inline_need(self.pos < len(self.data), "JSON_TEXT")
                esc = self.data[self.pos]
                self.pos += 1
                if esc == 117:
                    cp = self._hex4()
                    if 0xD800 <= cp <= 0xDBFF:
                        self._take(92)
                        self._take(117)
                        low = self._hex4()
                        _inline_need(0xDC00 <= low <= 0xDFFF, "JSON_TEXT")
                        cp = 0x10000 + ((cp - 0xD800) << 10) + low - 0xDC00
                    else:
                        _inline_need(not 0xDC00 <= cp <= 0xDFFF, "JSON_TEXT")
                    char = chr(cp)
                else:
                    _inline_need(esc in escapes, "JSON_TEXT")
                    char = escapes[esc]
            else:
                _inline_need(32 <= ch < 128, "JSON_TEXT")
                char = chr(ch)
            _inline_need(char != "\0", "JSON_TEXT")
            utf8 += len(char.encode("utf-8"))
            _inline_need(utf8 <= _INLINE_TEXT, "TEXT_LIMIT")
            chars.append(char)

    def value(self, depth=1):
        self.nodes += 1
        _inline_need(self.nodes <= _INLINE_NODES, "NODE_LIMIT")
        _inline_need(self.pos < len(self.data), "JSON_FORM")
        ch = self.data[self.pos]
        if ch == 91:
            _inline_need(depth <= _INLINE_DEPTH, "DEPTH_LIMIT")
            self.pos += 1
            rows = []
            if self.pos < len(self.data) and self.data[self.pos] == 93:
                self.pos += 1
                return ()
            while True:
                _inline_need(len(rows) < _INLINE_SEQUENCE, "SEQUENCE_LIMIT")
                rows.append(self.value(depth + 1))
                _inline_need(self.pos < len(self.data), "JSON_FORM")
                if self.data[self.pos] == 93:
                    self.pos += 1
                    return tuple(rows)
                self._take(44)
        if ch == 34:
            return self._string()
        if ch == 110:
            _inline_need(self.data[self.pos:self.pos + 4] == b"null", "JSON_FORM")
            self.pos += 4
            return None
        _inline_need(48 <= ch <= 57, "JSON_FORM")
        start = self.pos
        while self.pos < len(self.data) and 48 <= self.data[self.pos] <= 57:
            self.pos += 1
            _inline_need(self.pos - start <= 8, "INTEGER_LIMIT")
        _inline_need(self.pos - start == 1 or self.data[start] != 48, "JSON_FORM")
        return int(self.data[start:self.pos])


def _inline_seq(schema, count=None):
    return ("sequence", schema, count)


# n: semantischer Integer; t: Textreferenz; z: Textreferenz oder None.
# Die Formen bewahren alle Positionen; deren fachliche Werte sind ungeprüft.
_INLINE_D = ("n", "t", "t", "n", "t")
_INLINE_F = ("t", "n", "t")
_INLINE_S = ("t", "t", "t", _inline_seq("n", 3), "t", "t", _inline_seq("t", 4), "t",
             _inline_seq("t"), _inline_seq("t", 2), "t", _inline_seq("n", 6),
             _inline_seq("t", 3), _inline_seq("t", 2), _inline_seq(_INLINE_F))
_INLINE_P = ("t", "t", "z", "t", "t", "t", _inline_seq("t"), "t", "t", "t", _inline_seq("t"))
_INLINE_W = ("n", "t", "t", _INLINE_S, _inline_seq("t"), _inline_seq(_INLINE_P))
_INLINE_K = ("t", "t", "t", "t", _inline_seq(_INLINE_D, 9), "n", "t", "t")
_INLINE_I = ("t", "t", "t", "t", "t", _inline_seq(_INLINE_D, 9), "t")
_INLINE_M = (_INLINE_I, _INLINE_W, _INLINE_K)


def _inline_resolve(form):
    _inline_need(type(form) is tuple and len(form) == 4, "SCHEMA_FORM")
    _inline_need(type(form[0]) is str and form[0] == _INLINE_TAG, "VERSION_MISMATCH")
    _inline_need(type(form[1]) is str and form[1] == _INLINE_ROLE, "ROLE_MISMATCH")
    pool = form[2]
    _inline_need(type(pool) is tuple and len(pool) <= _INLINE_SEQUENCE, "POOL_LIMIT")
    for text in pool:
        _inline_need(type(text) is str, "POOL_FORM")
        _inline_need(len(text) <= _INLINE_TEXT, "TEXT_LIMIT")
        _inline_need("\0" not in text and len(text.encode("utf-8", "strict")) <= _INLINE_TEXT,
                     "TEXT_LIMIT")
    _inline_need(pool == tuple(sorted(set(pool))), "POOL_FORM")
    used = set()

    def walk(value, schema):
        if type(schema) is str:
            if schema == "z" and value is None:
                return None
            _inline_need(type(value) is int and 0 <= value <= 99999999, "POSITION_TYPE")
            if schema == "n":
                return value
            _inline_need(value < len(pool), "REFERENCE_RANGE")
            used.add(value)
            return pool[value]
        _inline_need(type(value) is tuple and len(value) <= _INLINE_SEQUENCE, "SCHEMA_FORM")
        if schema[0] == "sequence":
            _inline_need(schema[2] is None or len(value) == schema[2], "SCHEMA_FORM")
            return tuple(walk(v, schema[1]) for v in value)
        _inline_need(len(value) == len(schema), "SCHEMA_FORM")
        return tuple(walk(v, sc) for v, sc in zip(value, schema))

    payload = walk(form[3], _INLINE_M)
    _inline_need(used == set(range(len(pool))), "POOL_UNUSED")
    return payload


def _inline_canonical(form):
    pieces, size = [], _INLINE_HEADER.size
    encoder = json.JSONEncoder(ensure_ascii=True, sort_keys=True,
                              separators=(",", ":"), allow_nan=False)
    for piece in encoder.iterencode(form):
        size += len(piece)
        _inline_need(size <= _INLINE_METADATA_CAP, "METADATA_LIMIT")
        pieces.append(piece.encode("ascii"))
    return b"".join(pieces)


def _inline_metadata_syntax(header, metadata):
    """Private Payload: Syntax allein; keine Semantik, Aufnahme oder Freigabe."""
    try:
        _inline_need(type(header) is bytes and type(metadata) is bytes, "INPUT_TYPE")
        _inline_need(len(header) == _INLINE_HEADER.size, "HEADER_FORM")
        magic, metadata_size, body_size = _INLINE_HEADER.unpack(header)
        _inline_need(magic == _INLINE_MAGIC, "HEADER_FORM")
        _inline_need(0 < metadata_size <= _INLINE_METADATA_CAP - _INLINE_HEADER.size,
                     "METADATA_LIMIT")
        _inline_need(body_size <= _INLINE_BODY_CAP, "BODY_LIMIT")
        _inline_need(_INLINE_HEADER.size + metadata_size + body_size <= _INLINE_FRAME_CAP,
                     "FRAME_LIMIT")
        _inline_need(len(metadata) == metadata_size, "METADATA_LENGTH")
        parser = _InlineParser(metadata)
        form = parser.value()
        _inline_need(parser.pos == len(metadata), "JSON_END")
        payload = _inline_resolve(form)
        _inline_need(_inline_canonical(form) == metadata, "NONCANONICAL")
        return ("VALID_METADATA_SYNTAX", "NONE", payload)
    except _InlineSyntaxRejected as error:
        return ("REJECTED_METADATA_SYNTAX", error.args[0], None)
    except BaseException:
        return ("REJECTED_METADATA_SYNTAX", "SYNTAX_INTERNAL", None)
'''


def build_inline_syntax_control_bootstrap(profile_raw, *, logical_profile,
                                          expected_soabi, expected_destshared) -> BootstrapSource:
    """Reine dritte Quellenroute; inline Header-/E4-Syntax ohne Empfang/Semantik."""
    selected = build_sysconfig_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    source_text = selected.source.decode("utf-8", "strict")
    anchor = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(source_text.count(anchor) == 1, "TEMPLATE_FORM")
    source = source_text.replace(anchor, "\n" + _INLINE_SYNTAX + anchor, 1).encode("utf-8")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_SYSCONFIG_HELPERS = '''
def _config_text(value, locator=False):
    _require(type(value) is str and len(value) <= 4096, "CONTROL_SYSCONFIG_FORM")
    valid = True
    try:
        valid = len(value.encode("utf-8", "strict")) <= 4096 and "\\0" not in value
    except UnicodeError:
        valid = False
    _require(valid, "CONTROL_SYSCONFIG_FORM")
    if locator:
        _require(value.startswith("/") and not value.endswith("/")
                 and "\\\\" not in value and "//" not in value
                 and all(part not in ("", ".", "..") for part in value[1:].split("/")),
                 "CONTROL_SYSCONFIG_FORM")


def _config_anchor(cache, module_class, spec_class, loader_class):
    label = "CONTROL_SYSCONFIG_BINDING"
    _require(type(sys) is module_class and _dictionary(sys.modules)
             and sys.modules is cache, label)
    _require(type(sysconfig) is module_class and cache.get("sysconfig") is sysconfig, label)
    md = sysconfig.__dict__
    _require(_dictionary(md), label)
    _text(md.get("__name__"), "sysconfig", label)
    _text(md.get("__package__"), "", label)
    filename = md.get("__file__")
    _config_text(filename, True)
    spec, loader = md.get("__spec__"), md.get("__loader__")
    _require(type(spec) is spec_class and type(loader) is loader_class
             and "__path__" not in md, label)
    sd, ld = spec.__dict__, loader.__dict__
    _require(_dictionary(sd) and _dictionary(ld), label)
    _text(sd.get("name"), "sysconfig", label)
    _text(sd.get("origin"), filename, label)
    _require(sd.get("loader") is loader and sd.get("submodule_search_locations") is None
             and sd.get("_set_fileattr") is True, label)
    _text(ld.get("name"), "sysconfig", label)
    _text(ld.get("path"), filename, label)
    cached, spec_cached = md.get("__cached__"), sd.get("_cached")
    _require((cached is None or type(cached) is str)
             and (spec_cached is None or type(spec_cached) is str), label)
    if cached is not None:
        _config_text(cached)
    if spec_cached is not None:
        _config_text(spec_cached)
    _require(cached == spec_cached, label)
    function = md.get("get_config_var")
    _require(type(function) is type(_load_bound_control), label)
    _require(function.__globals__ is md and type(function.__code__) is type(_load_bound_control.__code__)
             and function.__defaults__ is None and function.__kwdefaults__ is None
             and function.__closure__ is None, label)
    return (sysconfig, md, function, function.__code__, spec, sd, loader, ld, filename, cached)


def _config_check(anchor, cache, module_class, spec_class, loader_class):
    current = _config_anchor(cache, module_class, spec_class, loader_class)
    _require(all(current[index] is anchor[index] for index in range(8))
             and current[8:] == anchor[8:], "CONTROL_SYSCONFIG_BINDING")


def _initialize_config(anchor, chosen, cache, module_class, spec_class, loader_class, coherence):
    _require(_EXPECTED_SOABI is chosen[0] and _EXPECTED_DESTSHARED is chosen[1],
             "CONTROL_SYSCONFIG_BINDING")
    _config_check(anchor, cache, module_class, spec_class, loader_class)
    _coherent(*coherence)
    actual_soabi = anchor[2]("SOABI")
    _config_check(anchor, cache, module_class, spec_class, loader_class)
    _coherent(*coherence)
    actual_destshared = anchor[2]("DESTSHARED")
    _config_check(anchor, cache, module_class, spec_class, loader_class)
    _coherent(*coherence)
    _require(_EXPECTED_SOABI is chosen[0] and _EXPECTED_DESTSHARED is chosen[1],
             "CONTROL_SYSCONFIG_BINDING")
    # Beide Formen sind vollständig geprüft, bevor ein Erwartungsvergleich erfolgt.
    try:
        _config_text(actual_soabi)
        _config_text(actual_destshared, True)
    except UnicodeError:
        raise _ControlRejected("CONTROL_SYSCONFIG_FORM") from None
    _require(actual_soabi == chosen[0] and actual_destshared == chosen[1],
             "CONTROL_SYSCONFIG_MISMATCH")


'''


def _config_expected(value, *, locator):
    label = "DESTSHARED_FORM" if locator else "SOABI_FORM"
    _need(type(value) is str and len(value) <= MAX_LOCATOR_BYTES, label)
    valid = True
    try:
        valid = len(value.encode("utf-8", "strict")) <= MAX_LOCATOR_BYTES and "\0" not in value
    except UnicodeError:
        valid = False
    _need(valid, label)
    if locator:
        _need(value.startswith("/") and not value.endswith("/")
              and "\\" not in value and "//" not in value
              and all(part not in ("", ".", "..") for part in value[1:].split("/")), label)


def build_sysconfig_control_bootstrap(profile_raw, *, logical_profile,
                                     expected_soabi, expected_destshared) -> BootstrapSource:
    """Separate reine Quellenroute für zwei vorab gewählte Sysconfigtexte."""
    _need(type(profile_raw) is bytes, "PROFILE_TYPE")
    _need(0 < len(profile_raw) <= MAX_PROFILE_BYTES, "PROFILE_SIZE")
    _locator(logical_profile)
    _config_expected(expected_soabi, locator=False)
    _config_expected(expected_destshared, locator=True)
    # Nur feste, eindeutig vorhandene Templateanker; die Legacykonstanten bleiben erhalten.
    changes = (
        ("def _load_bound_control():", _SYSCONFIG_HELPERS + "def _load_bound_control():"),
        ("        exec(code, module.__dict__, module.__dict__)",
         "        config_anchor = _config_anchor(cache, module_class, spec_class, loader_class)\n"
         "        chosen = (_EXPECTED_SOABI, _EXPECTED_DESTSHARED)\n"
         "        coherence = (module, spec, loader, loader_class, spec_class, cache, main,\n"
         "                     expected, code, module_class, name, filename)\n"
         "        exec(code, module.__dict__, module.__dict__)"),
        ("    except _ControlRejected as error:",
         "        phase = \"CONTROL_SYSCONFIG_CALL\"\n"
         "        _initialize_config(config_anchor, chosen, cache, module_class, spec_class, loader_class, coherence)\n"
         "        _coherent(module, spec, loader, loader_class, spec_class, cache, main,\n"
         "                  expected, code, module_class, name, filename)\n"
         "    except _ControlRejected as error:"),
        ('"CONTROL_COHERENCY", "CONTROL_COMPILE")',
         '"CONTROL_COHERENCY", "CONTROL_COMPILE", "CONTROL_SYSCONFIG_BINDING",\n'
         '                  "CONTROL_SYSCONFIG_FORM", "CONTROL_SYSCONFIG_MISMATCH", "CONTROL_SYSCONFIG_CALL")'),
        ('    except BaseException:\n        issue = "CONTROL_EXEC"',
         '    except BaseException:\n        issue = phase if phase == "CONTROL_SYSCONFIG_CALL" else "CONTROL_EXEC"'),
    )
    body = _BODY
    for old, new in changes:
        _need(body.count(old) == 1, "TEMPLATE_FORM")
        body = body.replace(old, new, 1)
    source = (_PREFIX + "\n_EXPECTED_PROFILE_RAW = " + repr(profile_raw)
              + "\n_PROFILE_FILE = " + ascii(logical_profile)
              + "\n_EXPECTED_SOABI = " + ascii(expected_soabi)
              + "\n_EXPECTED_DESTSHARED = " + ascii(expected_destshared) + "\n" + body).encode("utf-8")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


# Deklarative Semantik separat; keine Bodyaufnahme oder Callerfreigabe.
_INLINE_SEMANTICS = r'''
_SEMANTIC_CONTROL_ANCHOR = None
_SEMANTIC_ENTRIES = ("run_dgn007_automated_setup", "docker_sqlcmd_proxy", "run_demo")
_SEMANTIC_MODULES = (
    ("run_dgn007_automated_setup", "Tests/Runtime/run_dgn007_automated_setup.py"),
    ("execution_target", "Tests/Runtime/execution_target.py"),
    ("docker_sqlcmd_proxy", "Tests/Runtime/docker_sqlcmd_proxy.py"),
    ("run_demo", "Demos/00_Framework/Tools/run_demo.py"),
    ("orchestrate_sessions", "Demos/00_Framework/Tools/orchestrate_sessions.py"),
    ("sqlcmd_process", "Demos/00_Framework/Tools/sqlcmd_process.py"),
    ("Tests.Contracts.dgn007_capture_projection", "Tests/Contracts/dgn007_capture_projection.py"),
    ("Tests.Contracts.dgn007_collector_transport", "Tests/Contracts/dgn007_collector_transport.py"),
    ("Tests.Contracts.dgn007_prospective_acceptance", "Tests/Contracts/dgn007_prospective_acceptance.py"),
)
_SEMANTIC_OWN = tuple(row[0] for row in _SEMANTIC_MODULES) + ("Tests", "Tests.Contracts")
_SEMANTIC_FROZEN = {
    "_frozen_importlib": ("importlib._bootstrap", "_frozen_importlib"),
    "importlib._bootstrap": ("importlib._bootstrap", "_frozen_importlib"),
    "_frozen_importlib_external": ("importlib._bootstrap_external", "_frozen_importlib_external"),
    "importlib._bootstrap_external": ("importlib._bootstrap_external", "_frozen_importlib_external"),
    "_collections_abc": ("collections.abc", "_collections_abc"),
    "collections.abc": ("collections.abc", "_collections_abc"),
    "os.path": ("posixpath", "posixpath"),
}
_SEMANTIC_PAIRS = tuple(tuple(sorted(pair)) for pair in (
    ("_frozen_importlib", "importlib._bootstrap"),
    ("_frozen_importlib_external", "importlib._bootstrap_external"),
    ("_collections_abc", "collections.abc"), ("os.path", "posixpath")))


def _semantic_hex(value, width):
    _inline_need(type(value) is str and len(value) == width
                 and all(c in "0123456789abcdef" for c in value), "CONTEXT_FORM")


def _semantic_absolute(value):
    _inline_need(type(value) is str and value.startswith("/") and "//" not in value
                 and (value == "/" or not value.endswith("/"))
                 and all(p not in (".", "..") for p in value.split("/")), "PATH_FORM")


def _semantic_under(value, roots):
    return any(value == root or value.startswith(root.rstrip("/") + "/") for root in roots)


def _semantic_selector(ordinal, entry, phase):
    _inline_need(type(ordinal) is int and 1 <= ordinal <= 3
                 and entry == _SEMANTIC_ENTRIES[ordinal - 1] and phase == "PRE_IMPORT",
                 "CONTEXT_FORM")


def _semantic_installation(row):
    assumption, platform, implementation, version, exe, target, prefixes, abi, paths, roots, inert, flags, finders, hooks, files = row
    _inline_need(assumption == "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME" and platform == "linux"
                 and implementation == "cpython" and abi != "" and version[:2] == (3, 12)
                 and all(n <= 999 for n in version), "INSTALLATION_FORM")
    _inline_need(len(set(roots)) == 2, "INSTALLATION_FORM")
    for path in prefixes + roots + paths + (exe, target, inert):
        _semantic_absolute(path)
    _inline_need(all(path in roots or path == inert for path in paths), "PATH_FORM")
    _inline_need(flags == (1, 1, 1, 1, 1, 0) and finders == ("BUILTIN", "FROZEN", "PATH")
                 and hooks == ("ZIPIMPORTER", "FILEFINDER"), "INSTALLATION_FORM")
    _inline_need(len(files) <= 2, "FILE_FORM")
    total, names = 0, []
    for index, (path, size, digest) in enumerate(files):
        _semantic_absolute(path)
        _semantic_hex(digest, 64)
        _inline_need(size <= 33554432 and (path == target if index == 0 else _semantic_under(path, roots)),
                     "FILE_FORM")
        total += size
        names.append(path)
    _inline_need(total <= 67108864 and len(set(names)) == len(names), "FILE_FORM")


def _semantic_module(row, roots):
    name, module_name, spec_name, origin, filename, kind, locations, loader, loader_name, loader_path, aliases = row
    if filename:
        _semantic_absolute(filename)
    for path in locations:
        _semantic_absolute(path)
    _inline_need(name != "" and name not in _SEMANTIC_OWN, "OWN_MODULE_CACHED")
    _inline_need(kind in ("BUILTIN", "FROZEN", "SOURCE", "EXTENSION", "CONTROL")
                 and loader in ("NONE", "BUILTIN", "FROZEN", "SOURCE", "EXTENSION"), "MODULE_FORM")
    expected_names = _SEMANTIC_FROZEN.get(name, (name, name)) if kind == "FROZEN" else (name, name)
    _inline_need(module_name == expected_names[0], "MODULE_FORM")
    if spec_name is None:
        _inline_need(kind == "CONTROL" and origin == "" and locations == (), "MODULE_FORM")
    else:
        _inline_need(spec_name == expected_names[1], "MODULE_FORM")
    if loader in ("SOURCE", "EXTENSION"):
        _inline_need(loader_name == name and loader_path == filename, "MODULE_FORM")
        _semantic_absolute(filename)
    else:
        _inline_need(loader_name == loader_path == "", "MODULE_FORM")
    if kind == "BUILTIN":
        _inline_need(loader == "BUILTIN" and origin == "built-in" and locations == (), "MODULE_FORM")
    elif kind == "FROZEN":
        _inline_need(loader == "FROZEN" and origin == "frozen", "MODULE_FORM")
    elif kind in ("SOURCE", "EXTENSION"):
        _inline_need(loader == kind and origin == filename, "MODULE_FORM")
        for path in (origin, filename) + locations:
            _semantic_absolute(path)
            _inline_need(_semantic_under(path, roots), "PATH_FORM")
    else:
        _inline_need(loader in ("NONE", "SOURCE"), "MODULE_FORM")
        if spec_name is not None:
            _semantic_absolute(origin)
    _inline_need(aliases == () or (kind == "FROZEN" and aliases in _SEMANTIC_PAIRS
                 and name in aliases), "ALIAS_FORM")


def _semantic_worker(row):
    ordinal, entry, phase, installation, controls, modules = row
    _semantic_selector(ordinal, entry, phase)
    _semantic_installation(installation)
    _inline_need(len(modules) > 0, "INVENTORY_FORM")
    for module in modules:
        _semantic_module(module, installation[9])
    names = tuple(module[0] for module in modules)
    _inline_need(names == tuple(sorted(set(names))), "INVENTORY_FORM")
    _inline_need(len(set(controls)) == len(controls)
                 and set(controls) == {module[0] for module in modules if module[5] == "CONTROL"},
                 "CONTROL_FORM")
    by_name = {module[0]: module for module in modules}
    for module in modules:
        for name in module[10]:
            _inline_need(name in by_name and by_name[name][5] == "FROZEN"
                         and by_name[name][10] == module[10], "ALIAS_FORM")


def _semantic_descriptors(rows):
    total = 0
    for index, (row, mapping) in enumerate(zip(rows, _SEMANTIC_MODULES)):
        ordinal, module, member, size, digest = row
        _semantic_hex(digest, 64)
        _inline_need((ordinal, module, member) == (index,) + mapping and size <= 131072,
                     "CONTEXT_FORM")
        total += size
    _inline_need(total <= _INLINE_BODY_CAP, "CONTEXT_FORM")
    return total


def _semantic_inputs(ip, context):
    _inline_need(ip[0] == "dgn007-import-input/v1"
                 and ip[3] == context[2] == "dgn007-docker-sql-only/v1", "CONTEXT_FORM")
    for value, width in ((ip[1], 40), (ip[2], 64), (ip[4], 64), (ip[6], 64),
                         (context[0], 40), (context[1], 64), (context[3], 64)):
        _semantic_hex(value, width)
    _semantic_selector(*context[5:])
    totals = (_semantic_descriptors(ip[5]), _semantic_descriptors(context[4]))
    return totals


def _semantic_provider_text(value):
    label = "HASH_PROVIDER_BINDING"
    _inline_need(type(value) is str and len(value) <= 4096 and "\0" not in value, label)
    try:
        size = len(value.encode("utf-8", "strict"))
    except UnicodeError:
        raise _InlineSyntaxRejected(label) from None
    _inline_need(size <= 4096, label)


def _semantic_namespace(module, cache, name, spec_class, loader_class):
    label = "HASH_PROVIDER_BINDING"
    _inline_need(type(module) is _MODULE_CLASS and _dictionary(module.__dict__), label)
    md = module.__dict__
    _inline_need(cache.get(name) is module, label)
    _inline_need(type(md.get("__name__")) is str and md.get("__name__") == name, label)
    _inline_need(type(md.get("__package__")) is str and md.get("__package__") == ""
                 and "__path__" not in md, label)
    spec, loader = md.get("__spec__"), md.get("__loader__")
    _inline_need(type(spec) is spec_class and type(loader) is loader_class, label)
    sd, ld = spec.__dict__, loader.__dict__
    _inline_need(_dictionary(sd) and _dictionary(ld), label)
    for value in (sd.get("name"), sd.get("origin"), ld.get("name"), ld.get("path"), md.get("__file__")):
        _semantic_provider_text(value)
    _inline_need(sd["name"] == ld["name"] == name and sd["origin"] == ld["path"] == md["__file__"]
                 and sd.get("loader") is loader and sd.get("submodule_search_locations") is None
                 and sd.get("_set_fileattr") is True, label)
    cached, spec_cached = md.get("__cached__"), sd.get("_cached")
    for value in (cached, spec_cached):
        _inline_need(value is None or type(value) is str, label)
        if value is not None:
            _semantic_provider_text(value)
    _inline_need(cached == spec_cached, label)
    return (module, md, spec, sd, loader, ld, sd["origin"], cached)


def _semantic_class_namespace(value):
    label = "HASH_PROVIDER_BINDING"
    _inline_need(type(value) is type, label)
    namespace = value.__dict__
    _inline_need(type(namespace) is type(type.__dict__) and len(namespace) <= 256, label)
    for key in namespace:
        _semantic_provider_text(key)
    return namespace


def _semantic_provider_anchor():
    label = "HASH_PROVIDER_BINDING"
    a = _SEMANTIC_CONTROL_ANCHOR
    _inline_need(type(a) is tuple and len(a) == 12, label)
    try:
        _coherent(*a)
    except BaseException:
        raise _InlineSyntaxRejected(label) from None
    module, spec, loader, loader_class, spec_class, cache = a[:6]
    provider = module.__dict__.get("hashlib")
    pa = _semantic_namespace(provider, cache, "hashlib", spec_class, loader_class)
    native = pa[1].get("_hashlib")
    # Bekannte vorhandene Extensionklasse aus dem gehaltenen Profilnamespace.
    extension_class = module.__dict__.get("ExtensionFileLoader")
    _semantic_class_namespace(extension_class)
    _inline_need(type(extension_class.__name__) is str
                 and extension_class.__name__ == "ExtensionFileLoader", label)
    na = _semantic_namespace(native, cache, "_hashlib", spec_class, extension_class)
    factory, object_class = pa[1].get("sha256"), na[1].get("HASH")
    cd = _semantic_class_namespace(object_class)
    _inline_need(type(object_class.__module__) is str and type(object_class.__name__) is str
                 and object_class.__module__ == "_hashlib" and object_class.__name__ == "HASH", label)
    update, hexdigest = cd.get("update"), cd.get("hexdigest")
    _inline_need(type(update) is type(bytes.hex) and type(hexdigest) is type(bytes.hex)
                 and update.__objclass__ is object_class and hexdigest.__objclass__ is object_class
                 and object_class.__getattribute__ is object.__getattribute__, label)
    code = None
    if type(factory) is type(_semantic_provider_anchor):
        _inline_need(factory.__globals__ is pa[1] and factory.__defaults__ is None
                     and factory.__kwdefaults__ is None and factory.__closure__ is None, label)
        _inline_need(type(factory.__name__) is str and factory.__name__ == "sha256", label)
        code = factory.__code__
        _inline_need(type(code) is type(_semantic_provider_anchor.__code__), label)
    else:
        _inline_need(type(factory) is type(struct.pack) and factory is na[1].get("openssl_sha256"), label)
    return (a, pa, na, extension_class, factory, code, object_class, update, hexdigest)


def _semantic_provider_check(anchor):
    current = _semantic_provider_anchor()
    _inline_need(current[0] is anchor[0]
                 and all(current[index] is anchor[index] for index in range(3, 9))
                 and all(current[group][index] is anchor[group][index] for group in (1, 2) for index in range(6))
                 and current[1][6:] == anchor[1][6:] and current[2][6:] == anchor[2][6:],
                 "HASH_PROVIDER_BINDING")


def _semantic_original_digest(ip):
    anchor = _semantic_provider_anchor()
    issue, digest = None, None
    try:
        obj = anchor[4]()
        _inline_need(type(obj) is anchor[6], "HASH_PROVIDER_OBJECT")
        # Lesbare Methoden erst nach Bindung an die gehaltene native Hashklasse.
        update, finish = obj.update, obj.hexdigest
        _inline_need(type(update) is type(struct.pack) and update.__self__ is obj
                     and type(finish) is type(struct.pack) and finish.__self__ is obj,
                     "HASH_PROVIDER_OBJECT")
        value = dict(protocol=ip[0], commit=ip[1], raw27_binding=ip[2], source_profile=ip[3], nonce=ip[4],
                     modules=[dict(zip(("ordinal", "module", "member", "size", "sha256"), row)) for row in ip[5]])
        encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
        size = 16
        for piece in encoder.iterencode(value):
            _inline_need(type(piece) is str, "HASH_PROVIDER_CALL")
            size += len(piece)
            _inline_need(size <= _INLINE_METADATA_CAP, "METADATA_LIMIT")
            data = piece.encode("ascii", "strict")
            update(data)
        digest = finish()
        _semantic_hex(digest, 64)
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except BaseException:
        issue = "HASH_PROVIDER_CALL"
    # Bindungsverlust dominiert einen Providerfehler; keine Reparatur fremder Caches.
    _semantic_provider_check(anchor)
    if issue is not None:
        raise _InlineSyntaxRejected(issue) from None
    return digest


def _inline_metadata_semantics(header, metadata):
    """Private deklarative Metadata; keine Bodies, Inventur oder Freigabe."""
    syntax = _inline_metadata_syntax(header, metadata)
    if syntax[0] != "VALID_METADATA_SYNTAX":
        return ("REJECTED_METADATA_SEMANTICS", syntax[1], None)
    try:
        ip, worker, context = syntax[2]
        _semantic_worker(worker)
        totals = _semantic_inputs(ip, context)
        body_size = _INLINE_HEADER.unpack(header)[2]
        _inline_need(body_size == totals[0] == totals[1], "DECLARED_BODY_LENGTH")
        # Sämtliche Formen vor Originaldigest und vor jedem Bindungsvergleich.
        digest = _semantic_original_digest(ip)
        _inline_need(digest == ip[6], "INPUT_DIGEST")
        _inline_need(ip[1:5] == context[:4] and ip[5] == context[4], "INPUT_BINDING")
        _inline_need(worker[:3] == context[5:], "CONTEXT_MISMATCH")
        return ("VALID_METADATA_SEMANTICS", "NONE", syntax[2])
    except _InlineSyntaxRejected as error:
        return ("REJECTED_METADATA_SEMANTICS", error.args[0], None)
    except BaseException:
        return ("REJECTED_METADATA_SEMANTICS", "SEMANTICS_INTERNAL", None)
'''


def build_inline_semantics_control_bootstrap(profile_raw, *, logical_profile,
                                             expected_soabi, expected_destshared) -> BootstrapSource:
    """Vierte reine Quellenroute; deklarative Metadata ohne Body-/Callerclaim."""
    selected = build_inline_syntax_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    changes = (
        ('    global _CONTROL_ATTEMPTED\n', '    global _CONTROL_ATTEMPTED, _SEMANTIC_CONTROL_ANCHOR\n'),
        ('    return ("LOADED_BOUND_CONTROL_SOURCE", "NONE", module)',
         '    _SEMANTIC_CONTROL_ANCHOR = coherence\n'
         '    return ("LOADED_BOUND_CONTROL_SOURCE", "NONE", module)'),
        ('\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n',
         '\n' + _INLINE_SEMANTICS + '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'),
    )
    for old, new in changes:
        _need(text.count(old) == 1, "TEMPLATE_FORM")
        text = text.replace(old, new, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


# Gegebene Scalarformen und private Records; keine Aufnahme oder Pipeausgabe.
_INLINE_REPORT = r'''
_REPORT_SELECTION = ("t", _inline_seq("t", 2), "t", _inline_seq("t"))
_REPORT_INSTALLATION = ("t", "t", _inline_seq("n", 3), "t", "t", _inline_seq("t", 4),
                        "t", _inline_seq("n", 6), _inline_seq("t"), _inline_seq("t", 3),
                        _inline_seq("t", 2), _inline_seq(_INLINE_F))
_REPORT_SCALARS = (_REPORT_SELECTION, _REPORT_INSTALLATION, _inline_seq(_INLINE_P))
_REPORT_R = (_INLINE_K, _INLINE_S, _inline_seq("t"), _inline_seq(_INLINE_P))


def _report_shape(schema, value, depth=1, counter=None):
    if counter is None:
        counter = [0]
    counter[0] += 1
    _inline_need(counter[0] <= _INLINE_NODES, "NODE_LIMIT")
    if schema in ("t", "z"):
        if schema == "z" and value is None:
            return
        _inline_need(type(value) is str and len(value) <= _INLINE_TEXT, "SCALAR_FORM")
        _inline_need("\0" not in value and len(value.encode("utf-8", "strict")) <= _INLINE_TEXT,
                     "TEXT_LIMIT")
    elif schema == "n":
        _inline_need(type(value) is int and 0 <= value <= 99999999, "SCALAR_FORM")
    else:
        _inline_need(type(value) is tuple and len(value) <= _INLINE_SEQUENCE, "SCALAR_FORM")
        _inline_need(depth <= _INLINE_DEPTH, "DEPTH_LIMIT")
        if schema[0] == "sequence":
            _inline_need(schema[2] is None or len(value) == schema[2], "SCALAR_FORM")
            for child in value:
                _report_shape(schema[1], child, depth + 1, counter)
        else:
            _inline_need(len(value) == len(schema), "SCALAR_FORM")
            for field, child in zip(schema, value):
                _report_shape(field, child, depth + 1, counter)


def _report_encoder_anchor():
    label = "REPORT_ENCODER_BINDING"
    a = _SEMANTIC_CONTROL_ANCHOR
    _inline_need(type(a) is tuple and len(a) == 12 and _dictionary(a[5]), label)
    cache = a[5]
    _inline_need(type(json) is _MODULE_CLASS and _dictionary(json.__dict__)
                 and cache.get("json") is json, label)
    module = cache.get("json.encoder")
    _inline_need(type(module) is _MODULE_CLASS and _dictionary(module.__dict__), label)
    md = module.__dict__
    _inline_need(type(md.get("__name__")) is str and md.get("__name__") == "json.encoder", label)
    cls = json.__dict__.get("JSONEncoder")
    try:
        cd = _semantic_class_namespace(cls)
    except _InlineSyntaxRejected:
        raise _InlineSyntaxRejected(label) from None
    _inline_need(md.get("JSONEncoder") is cls and type(cls.__module__) is str
                 and cls.__module__ == "json.encoder", label)
    bases, mro = cls.__bases__, cls.__mro__
    _inline_need(type(bases) is tuple and len(bases) == 1 and bases[0] is object
                 and type(mro) is tuple and len(mro) == 2 and mro[0] is cls and mro[1] is object
                 and cd.get("__getattribute__", object.__getattribute__) is object.__getattribute__
                 and cd.get("__new__", object.__new__) is object.__new__, label)
    functions = tuple(cd.get(name) for name in ("__init__", "iterencode", "default"))
    for function in functions:
        _inline_need(type(function) is type(_report_encoder_anchor) and function.__globals__ is md
                     and type(function.__code__) is type(_report_encoder_anchor.__code__), label)
    functions += (md.get("_make_iterencode"),)
    _inline_need(type(functions[3]) is type(_report_encoder_anchor)
                 and functions[3].__globals__ is md, label)
    states = []
    for function in functions:
        defaults, keywords = function.__defaults__, function.__kwdefaults__
        _inline_need(function.__closure__ is None and (defaults is None or
                     type(defaults) is tuple and len(defaults) <= 256)
                     and (keywords is None or _dictionary(keywords)), label)
        states.append((function.__code__, defaults, keywords,
                       () if keywords is None else tuple(sorted(keywords.items()))))
    return (json, json.__dict__, module, md, cls, functions, tuple(states), tuple(sorted(md.items())),
            tuple(sorted(cd.items())), cls.__bases__, cls.__mro__)


def _report_encoder_check(anchor):
    current = _report_encoder_anchor()
    _inline_need(all(current[index] is anchor[index] for index in range(5))
                 and all(current[5][index] is anchor[5][index] for index in range(4))
                 and all(current[6][index][field] is anchor[6][index][field]
                         for index in range(4) for field in range(3))
                 and all(len(current[6][index][3]) == len(anchor[6][index][3])
                         and all(a[0] == b[0] and a[1] is b[1]
                                 for a, b in zip(current[6][index][3], anchor[6][index][3]))
                         for index in range(4))
                 and all(len(current[group]) == len(anchor[group])
                         and all(a[0] == b[0] and a[1] is b[1]
                                 for a, b in zip(current[group], anchor[group])) for group in (7, 8))
                 and current[9] is anchor[9] and current[10] is anchor[10],
                 "REPORT_ENCODER_BINDING")


def _report_pack(payload):
    # Die E4-Vorkommen werden vor Pool-/Positionsaufnahme begrenzt.
    texts, nodes = set(), [4]
    def collect(value, depth):
        nodes[0] += 1
        _inline_need(nodes[0] <= _INLINE_NODES, "NODE_LIMIT")
        if type(value) is tuple:
            _inline_need(depth <= _INLINE_DEPTH and len(value) <= _INLINE_SEQUENCE, "DEPTH_LIMIT")
            for child in value:
                collect(child, depth + 1)
        elif type(value) is str:
            texts.add(value)
            _inline_need(len(texts) <= 256, "POOL_LIMIT")
    collect(payload, 2)
    _inline_need(nodes[0] + len(texts) <= _INLINE_NODES, "NODE_LIMIT")
    pool = tuple(sorted(texts))
    positions = {value: index for index, value in enumerate(pool)}
    def project(value):
        if type(value) is str:
            return positions[value]
        if type(value) is tuple:
            return tuple(project(child) for child in value)
        return value
    return (_INLINE_TAG, "REPORTED", pool, project(payload))


def _report_encoder_instance(encoder, anchor):
    label = "REPORT_ENCODER_BINDING"
    _inline_need(type(encoder) is anchor[4] and _dictionary(encoder.__dict__), label)
    values = encoder.__dict__
    names = ("skipkeys", "ensure_ascii", "check_circular", "allow_nan", "sort_keys", "indent",
             "item_separator", "key_separator")
    _inline_need(len(values) == len(names) and all(name in values for name in names), label)
    for name, expected in (("skipkeys", False), ("ensure_ascii", True), ("check_circular", True),
                           ("allow_nan", False), ("sort_keys", True)):
        _inline_need(type(values[name]) is bool and values[name] is expected, label)
    _inline_need(values["indent"] is None, label)
    for name, expected in (("item_separator", ","), ("key_separator", ":")):
        _inline_need(type(values[name]) is str and values[name] == expected, label)
    method = encoder.iterencode
    _inline_need(type(method) is type(_report_json.__get__(encoder, anchor[4]))
                 and method.__self__ is encoder and method.__func__ is anchor[5][1], label)


def _report_json(form, encoder_anchor):
    issue, data, encoder = None, None, None
    try:
        _report_encoder_check(encoder_anchor)
        encoder = encoder_anchor[4](sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
        _report_encoder_check(encoder_anchor)
        _report_encoder_instance(encoder, encoder_anchor)
        parts, size = [], 16
        # Keine Schattenfunktion aus dem Instanznamespace als Dispatchquelle.
        for piece in encoder_anchor[5][1](encoder, form):
            _report_encoder_check(encoder_anchor)
            _report_encoder_instance(encoder, encoder_anchor)
            _inline_need(type(piece) is str, "REPORT_ENCODER_CALL")
            size += len(piece)
            _inline_need(size <= _INLINE_METADATA_CAP, "METADATA_LIMIT")
            parts.append(piece.encode("ascii", "strict"))
        data = b"".join(parts)
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except BaseException:
        issue = "REPORT_ENCODER_CALL"
    _report_encoder_check(encoder_anchor)
    if encoder is not None:
        _report_encoder_instance(encoder, encoder_anchor)
    if issue is not None:
        raise _InlineSyntaxRejected(issue) from None
    return data


def _report_sha(data, anchor):
    issue, digest = None, None
    try:
        _semantic_provider_check(anchor)
        obj = anchor[4]()
        _semantic_provider_check(anchor)
        _inline_need(type(obj) is anchor[6], "HASH_PROVIDER_OBJECT")
        update, finish = obj.update, obj.hexdigest
        _inline_need(type(update) is type(struct.pack) and update.__self__ is obj
                     and type(finish) is type(struct.pack) and finish.__self__ is obj,
                     "HASH_PROVIDER_OBJECT")
        _semantic_provider_check(anchor)
        update(data)
        _semantic_provider_check(anchor)
        digest = finish()
        _semantic_hex(digest, 64)
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except BaseException:
        issue = "HASH_PROVIDER_CALL"
    _semantic_provider_check(anchor)
    if issue is not None:
        raise _InlineSyntaxRejected(issue) from None
    return digest


def _report_records(data, ordinal, digest, encoder_anchor):
    _inline_need(type(data) is bytes and 0 < len(data) <= _INLINE_METADATA_CAP - 16
                 and type(ordinal) is int and 1 <= ordinal <= 3, "REPORT_FRAME")
    _semantic_hex(digest, 64)
    total = (len(data) + 895) // 896
    _inline_need(1 <= total <= 19, "REPORT_FRAME")
    begin = _report_json(("PROFILE_BEGIN", ordinal, len(data), total), encoder_anchor) + b"\n"
    end = _report_json(("PROFILE_END", ordinal, len(data), total, digest), encoder_anchor) + b"\n"
    _inline_need(len(begin) <= 256 and len(end) <= 256, "REPORT_FRAME")
    rows = [begin]
    for sequence in range(1, total + 1):
        piece = data[(sequence - 1) * 896:sequence * 896]
        envelope = ("P|%d|%d|%d|" % (ordinal, sequence, total)).encode("ascii")
        _inline_need(len(envelope) + 1 <= 32 and len(piece) <= 896
                     and len(envelope) + len(piece) + 1 <= 1024, "REPORT_FRAME")
        rows.append(envelope + piece + b"\n")
    rows.append(end)
    return tuple(rows)


def _inline_profile_report(header, metadata, scalars):
    """Gegebene Scalarfelder als private Records; keine Aufnahme oder Freigabe."""
    syntax = _inline_metadata_syntax(header, metadata)
    if syntax[0] != "VALID_METADATA_SYNTAX":
        return ("REJECTED_PROFILE_REPORT", syntax[1], None)
    anchor, encoder_anchor = None, None
    try:
        _report_shape(_REPORT_SCALARS, scalars)
        selection, installation, modules = scalars
        assumption, roots, inert, controls = selection
        platform, implementation, version, exe, target, prefixes, abi, flags, paths, finders, hooks, files = installation
        chosen = (assumption, platform, implementation, version, exe, target, prefixes, abi,
                  paths, roots, inert, flags, finders, hooks, files)
        # Auch die vollständigen gegebenen Inventurformen werden vor allen Digests geprüft.
        worker = syntax[2][1]
        _semantic_worker(worker)
        totals = _semantic_inputs(syntax[2][0], syntax[2][2])
        _semantic_worker(worker[:3] + (chosen, controls, modules))
        _inline_need(_INLINE_HEADER.unpack(header)[2] == totals[0] == totals[1], "DECLARED_BODY_LENGTH")
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        ip, _, context = syntax[2]
        original = dict(protocol=ip[0], commit=ip[1], raw27_binding=ip[2], source_profile=ip[3], nonce=ip[4],
                        modules=[dict(zip(("ordinal", "module", "member", "size", "sha256"), row)) for row in ip[5]])
        # Unverändertes benanntes Originalpräbild; unmittelbare PRE vor jedem Constructor.
        original_digest = _report_sha(_report_json(original, encoder_anchor), anchor)
        _inline_need(original_digest == ip[6], "INPUT_DIGEST")
        _inline_need(ip[1:5] == context[:4] and ip[5] == context[4], "INPUT_BINDING")
        _inline_need(worker[:3] == context[5:], "CONTEXT_MISMATCH")
        # K stammt aus M; S15 und Inventur ausschließlich aus den gegebenen Scalars.
        payload = (syntax[2][2], chosen, controls, modules)
        _report_shape(_REPORT_R, payload)
        form = _report_pack(payload)
        data = _report_json(form, encoder_anchor)
        digest = _report_sha(data, anchor)
        records = _report_records(data, payload[0][5], digest, encoder_anchor)
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("FORMATTED_PROFILE_REPORT", "NONE", records)
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "REPORT_INTERNAL"
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_PROFILE_REPORT", issue, None)
'''


def build_inline_report_control_bootstrap(profile_raw, *, logical_profile,
                                         expected_soabi, expected_destshared) -> BootstrapSource:
    """Fünfte reine Quellenroute für gegebene Scalarformen und private Reportrecords."""
    selected = build_inline_semantics_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_REPORT + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_RECEIVER = r'''
_RECEIVE_FORMAT = "pooled-combined-input-design/v1"
_RECEIVE_CHUNKS = 256
_RECEIVE_CHUNK_BYTES = 1024


def _inline_receive_metadata_chunks(chunks, *, expected_format):
    """Nur gegebene Chunks aufnehmen; keine Pipe, Bodies oder Freigabe."""
    try:
        _inline_need(type(expected_format) is str
                     and expected_format == _RECEIVE_FORMAT, "FORMAT_SELECTION")
        _inline_need(type(chunks) is tuple, "CHUNKS_TYPE")
        _inline_need(len(chunks) <= _RECEIVE_CHUNKS, "CHUNKS_LIMIT")
        # Alle Typen vor Längen, Kopien, Headerauslegung oder Provideraktivität.
        for chunk in chunks:
            _inline_need(type(chunk) is bytes, "CHUNK_TYPE")
        total, oversized = 0, False
        for chunk in chunks:
            oversized = oversized or len(chunk) > _RECEIVE_CHUNK_BYTES
            total += len(chunk)
        _inline_need(not oversized, "CHUNK_LIMIT")
        _inline_need(total <= _INLINE_METADATA_CAP, "METADATA_LIMIT")
        _inline_need(total >= _INLINE_HEADER.size, "HEADER_LENGTH")
        # Leere Stücke sind zulässig und zählen zur endlichen Chunkgrenze.
        pieces, missing = [], _INLINE_HEADER.size
        for chunk in chunks:
            if missing:
                piece = chunk[:missing]
                pieces.append(piece)
                missing -= len(piece)
        header = b"".join(pieces)
        magic, metadata_size, body_size = _INLINE_HEADER.unpack(header)
        _inline_need(magic == _INLINE_MAGIC, "HEADER_FORM")
        _inline_need(0 < metadata_size <= _INLINE_METADATA_CAP - _INLINE_HEADER.size,
                     "METADATA_LIMIT")
        _inline_need(body_size <= _INLINE_BODY_CAP, "BODY_LIMIT")
        _inline_need(_INLINE_HEADER.size + metadata_size + body_size <= _INLINE_FRAME_CAP,
                     "FRAME_LIMIT")
        # Erst das exakte Ende prüfen: kein Suffix und keine Body-/Commandaufnahme.
        _inline_need(total == _INLINE_HEADER.size + metadata_size, "METADATA_LENGTH")
        received = b"".join(chunks)
        metadata = received[_INLINE_HEADER.size:]
        semantic = _inline_metadata_semantics(header, metadata)
        if semantic[0] != "VALID_METADATA_SEMANTICS":
            return ("REJECTED_RECEIVED_METADATA", semantic[1], None)
        return ("VALID_RECEIVED_METADATA", "NONE", (header, metadata, semantic[2]))
    except _InlineSyntaxRejected as error:
        return ("REJECTED_RECEIVED_METADATA", error.args[0], None)
    except BaseException:
        return ("REJECTED_RECEIVED_METADATA", "RECEIVE_INTERNAL", None)
'''


def build_inline_receive_control_bootstrap(profile_raw, *, logical_profile,
                                          expected_soabi, expected_destshared) -> BootstrapSource:
    """Sechste reine Quellenroute für gehaltene Header-/Metadata-Chunks."""
    selected = build_inline_report_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_RECEIVER + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_COMMAND = r'''
_COMMAND_FORMAT = "pooled-combined-input-design/v1"
_COMMAND_DOMAIN = "pooled-profile-binding-context/v1"
_COMMAND_KINDS = ("BODY_RELEASE", "BODY_END", "IMPORT_RELEASE")
_COMMAND_SHAPE = ("t", "n", "t", "t")
_COMMAND_LIMIT = 256


def _command_kind(kind):
    _inline_need(type(kind) is str and kind in _COMMAND_KINDS, "COMMAND_KIND")


def _command_context(context):
    # Aufruf ausschließlich nach dem vollständigen K8-/D9-Typvorlauf.
    _semantic_hex(context[0], 40)
    _semantic_hex(context[1], 64)
    _semantic_hex(context[3], 64)
    _inline_need(context[2] == "dgn007-docker-sql-only/v1", "CONTEXT_FORM")
    _semantic_descriptors(context[4])
    _semantic_selector(*context[5:])


def _command_received(line):
    _inline_need(type(line) is bytes, "COMMAND_TYPE")
    _inline_need(0 < len(line) <= _COMMAND_LIMIT, "COMMAND_LIMIT")
    _inline_need(line[-1:] == b"\n" and line.count(b"\n") == 1 and b"\r" not in line,
                 "COMMAND_FORM")
    parser = _InlineParser(line[:-1])
    actual = parser.value()
    _inline_need(parser.pos == len(parser.data), "COMMAND_FORM")
    _report_shape(_COMMAND_SHAPE, actual)
    return actual


def _command_k_json(context, encoder_anchor):
    # Eigener vollständiger Pool, Payload (Kp,), keine REPORTED-/Input82-Domain.
    packed = _report_pack((context,))
    form = (packed[0], _COMMAND_DOMAIN, packed[2], packed[3])
    return _report_json(form, encoder_anchor)


def _command_compute(context, kind, line, operation, expected_format):
    anchor, encoder_anchor = None, None
    status = {"digest": "REJECTED_CONTEXT_DIGEST", "encode": "REJECTED_BOUND_COMMAND",
              "match": "REJECTED_BOUND_COMMAND"}[operation]
    try:
        _inline_need(type(expected_format) is str and expected_format == _COMMAND_FORMAT,
                     "FORMAT_SELECTION")
        if operation != "digest":
            _command_kind(kind)
        _report_shape(_INLINE_K, context)
        actual = _command_received(line) if operation == "match" else None
        _command_context(context)
        if operation == "match":
            _command_kind(actual[0])
            _inline_need(1 <= actual[1] <= 3, "COMMAND_FORM")
            _semantic_hex(actual[2], 64)
            _semantic_hex(actual[3], 64)
        # Sämtliche Caller-/Receivedformen vor Encoderaufnahme oder Hashdispatch.
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        if operation == "match":
            canonical = _report_json(actual, encoder_anchor) + b"\n"
            _inline_need(len(canonical) <= _COMMAND_LIMIT, "COMMAND_LIMIT")
            _inline_need(canonical == line, "COMMAND_CANONICAL")
        data = _command_k_json(context, encoder_anchor)
        digest = _report_sha(data, anchor)
        if operation == "digest":
            result = ("FORMATTED_CONTEXT_DIGEST", "NONE", digest)
        elif operation == "encode":
            command = (kind, context[5], context[3], digest)
            encoded = _report_json(command, encoder_anchor) + b"\n"
            _inline_need(len(encoded) <= _COMMAND_LIMIT, "COMMAND_LIMIT")
            result = ("FORMATTED_BOUND_COMMAND", "NONE", encoded)
        else:
            _inline_need(actual == (kind, context[5], context[3], digest), "COMMAND_MISMATCH")
            result = ("MATCHED_DECLARED_COMMAND", "NONE", actual)
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return result
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "COMMAND_INTERNAL"
    # Feste dominante POST-Priorität: Providerverlust > Encoderverlust > sonstiger Fehler.
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return (status, issue, None)


def _inline_context_digest(context, *, expected_format):
    """Einzelnes gegebenes K; kein Fünf-Formen-Gate, Caller-/Herkunftsclaim."""
    return _command_compute(context, None, None, "digest", expected_format)


def _inline_command_encode(kind, context, *, expected_format):
    """Private kanonische Commandbytes; keine operative Freigabe."""
    return _command_compute(context, kind, None, "encode", expected_format)


def _inline_command_match(line, *, expected_kind, expected_context, expected_format):
    """Vollständig empfangene Form gegen getrennt gewählte deklarative Werte."""
    return _command_compute(expected_context, expected_kind, line, "match", expected_format)
'''


def build_inline_command_control_bootstrap(profile_raw, *, logical_profile,
                                          expected_soabi, expected_destshared) -> BootstrapSource:
    """Siebte reine Quellenroute für K-Domain und deklarativ gebundene Commands."""
    selected = build_inline_receive_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_COMMAND + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_MATCH = r'''
def _match_intake(chunks):
    # Alle Typen wurden vor diesem begrenzten Längen-/Kopierpfad geprüft.
    total, oversized = 0, False
    for chunk in chunks:
        oversized = oversized or len(chunk) > _RECEIVE_CHUNK_BYTES
        total += len(chunk)
    _inline_need(not oversized, "CHUNK_LIMIT")
    _inline_need(total <= _INLINE_METADATA_CAP, "METADATA_LIMIT")
    _inline_need(total >= _INLINE_HEADER.size, "HEADER_LENGTH")
    pieces, missing = [], _INLINE_HEADER.size
    for chunk in chunks:
        if missing:
            piece = chunk[:missing]
            pieces.append(piece)
            missing -= len(piece)
    header = b"".join(pieces)
    magic, metadata_size, body_size = _INLINE_HEADER.unpack(header)
    _inline_need(magic == _INLINE_MAGIC, "HEADER_FORM")
    _inline_need(0 < metadata_size <= _INLINE_METADATA_CAP - _INLINE_HEADER.size,
                 "METADATA_LIMIT")
    _inline_need(body_size <= _INLINE_BODY_CAP, "BODY_LIMIT")
    _inline_need(_INLINE_HEADER.size + metadata_size + body_size <= _INLINE_FRAME_CAP,
                 "FRAME_LIMIT")
    _inline_need(total == _INLINE_HEADER.size + metadata_size, "METADATA_LENGTH")
    received = b"".join(chunks)
    metadata = received[_INLINE_HEADER.size:]
    parser = _InlineParser(metadata)
    form = parser.value()
    _inline_need(parser.pos == len(metadata), "JSON_END")
    return header, metadata, form, _inline_resolve(form), body_size


def _match_original(ip):
    # Vollständiges benanntes Input82-Präbild, nicht E4/K oder context_sha256.
    return dict(protocol=ip[0], commit=ip[1], raw27_binding=ip[2], source_profile=ip[3], nonce=ip[4],
                modules=[dict(zip(("ordinal", "module", "member", "size", "sha256"), row))
                         for row in ip[5]])


def _match_intrinsic(payload, digest):
    ip, worker, context = payload
    _inline_need(digest == ip[6], "INPUT_DIGEST")
    _inline_need(ip[1:5] == context[:4] and ip[5] == context[4], "INPUT_BINDING")
    _inline_need(worker[:3] == context[5:], "CONTEXT_MISMATCH")


def _inline_match_metadata_chunks(chunks, *, expected_format, expected_input,
                                  expected_worker, expected_context):
    """Gehaltene Metadata gegen getrennte Vollformen; keine operative Freigabe."""
    anchor, encoder_anchor = None, None
    try:
        _inline_need(type(expected_format) is str and expected_format == _RECEIVE_FORMAT,
                     "FORMAT_SELECTION")
        _inline_need(type(chunks) is tuple, "CHUNKS_TYPE")
        _inline_need(len(chunks) <= _RECEIVE_CHUNKS, "CHUNKS_LIMIT")
        for chunk in chunks:
            _inline_need(type(chunk) is bytes, "CHUNK_TYPE")
        expected = (expected_input, expected_worker, expected_context)
        _report_shape(_INLINE_M, expected)
        header, metadata, form, actual, body_size = _match_intake(chunks)
        _report_shape(_INLINE_M, actual)
        # Beide vollständigen Semantiken vor Repack, SHA oder Bindungsvergleich.
        for payload in (actual, expected):
            _semantic_worker(payload[1])
            totals = _semantic_inputs(payload[0], payload[2])
            _inline_need(totals[0] == totals[1], "DECLARED_BODY_LENGTH")
            if payload is actual:
                _inline_need(body_size == totals[0], "DECLARED_BODY_LENGTH")
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        _inline_need(_report_json(form, encoder_anchor) == metadata, "NONCANONICAL")
        # Zwei eigenständige Präbilder; unmittelbare gehaltene Provider-PRE je SHA.
        actual_digest = _report_sha(_report_json(_match_original(actual[0]), encoder_anchor), anchor)
        expected_digest = _report_sha(_report_json(_match_original(expected[0]), encoder_anchor), anchor)
        _match_intrinsic(actual, actual_digest)
        _match_intrinsic(expected, expected_digest)
        _inline_need(actual == expected, "METADATA_DECLARATION_MISMATCH")
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("MATCHED_DECLARED_METADATA", "NONE", (header, metadata, actual))
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "METADATA_MATCH_INTERNAL"
    # Beide POSTs auch nach Fehlern; Providerverlust hat die höchste Priorität.
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_DECLARED_METADATA", issue, None)
'''


def build_inline_match_control_bootstrap(profile_raw, *, logical_profile,
                                        expected_soabi, expected_destshared) -> BootstrapSource:
    """Achte reine Quellenroute für vollständigen deklarativen Metadata-Abgleich."""
    selected = build_inline_command_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_MATCH + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_BODY = r'''
def _inline_receive_declared_bodies(metadata_chunks, bodies, *, expected_format,
                                    expected_input, expected_worker, expected_context):
    """Gehaltene neun Rawbodies; keine Kanalphase, Quellenverwendung oder Herkunft."""
    anchor, encoder_anchor = None, None
    try:
        _inline_need(type(expected_format) is str and expected_format == _RECEIVE_FORMAT,
                     "FORMAT_SELECTION")
        _inline_need(type(metadata_chunks) is tuple, "CHUNKS_TYPE")
        _inline_need(len(metadata_chunks) <= _RECEIVE_CHUNKS, "CHUNKS_LIMIT")
        for chunk in metadata_chunks:
            _inline_need(type(chunk) is bytes, "CHUNK_TYPE")
        _inline_need(type(bodies) is tuple, "BODIES_TYPE")
        _inline_need(len(bodies) == 9, "BODIES_COUNT")
        for body in bodies:
            _inline_need(type(body) is bytes, "BODY_TYPE")
        expected = (expected_input, expected_worker, expected_context)
        _report_shape(_INLINE_M, expected)
        header, metadata, form, actual, body_size = _match_intake(metadata_chunks)
        _report_shape(_INLINE_M, actual)
        # Beide Vollsemantiken und sämtliche tatsächlichen Größen vor jedem SHA.
        for payload in (actual, expected):
            _semantic_worker(payload[1])
            totals = _semantic_inputs(payload[0], payload[2])
            _inline_need(totals[0] == totals[1], "DECLARED_BODY_LENGTH")
        sizes = tuple(len(body) for body in bodies)
        _inline_need(all(size <= 131072 for size in sizes), "MEMBER_LIMIT")
        _inline_need(sum(sizes) <= _INLINE_BODY_CAP, "BODY_LIMIT")
        _inline_need(body_size == sum(sizes), "DECLARED_BODY_LENGTH")
        for index, size in enumerate(sizes):
            _inline_need(actual[0][5][index][3] == size
                         and actual[2][4][index][3] == size, "BODY_SIZE")
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        _inline_need(_report_json(form, encoder_anchor) == metadata, "NONCANONICAL")
        actual_digest = _report_sha(_report_json(_match_original(actual[0]), encoder_anchor), anchor)
        expected_digest = _report_sha(_report_json(_match_original(expected[0]), encoder_anchor), anchor)
        _match_intrinsic(actual, actual_digest)
        _match_intrinsic(expected, expected_digest)
        # Kein Join, Decode oder LF-Normalisieren; jedes gehaltene Rawobjekt einzeln.
        hashes = tuple(_report_sha(body, anchor) for body in bodies)
        for index, digest in enumerate(hashes):
            _inline_need(digest == actual[0][5][index][4]
                         and digest == actual[2][4][index][4], "BODY_HASH")
        _inline_need(actual == expected, "METADATA_DECLARATION_MISMATCH")
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("RECEIVED_DECLARED_BODIES", "NONE", (header, metadata, actual, bodies))
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "BODY_RECEIVE_INTERNAL"
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_DECLARED_BODIES", issue, None)
'''


def build_inline_body_control_bootstrap(profile_raw, *, logical_profile,
                                       expected_soabi, expected_destshared) -> BootstrapSource:
    """Neunte reine Quellenroute für begrenzte deklarativ gebundene Rawbodyaufnahme."""
    selected = build_inline_match_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_BODY + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_REASSEMBLE = r'''
def _reassemble_control(line, schema):
    parser = _InlineParser(line[:-1])
    value = parser.value()
    _inline_need(parser.pos == len(line) - 1, "JSON_FORM")
    _report_shape(schema, value)
    return value


def _reassemble_decimal(token):
    _inline_need(1 <= len(token) <= 8 and 49 <= token[0] <= 57
                 and all(48 <= byte <= 57 for byte in token), "FRAGMENT_FORM")
    return int(token)


def _inline_reassemble_profile_records(records, *, expected_ordinal):
    """Gehaltene ASCII-Fragmente und Footer; keine R-Semantik oder Kanalaufnahme."""
    anchor, encoder_anchor = None, None
    try:
        _inline_need(type(expected_ordinal) is int and 1 <= expected_ordinal <= 3,
                     "ORDINAL_SELECTION")
        _inline_need(type(records) is tuple, "RECORDS_TYPE")
        _inline_need(3 <= len(records) <= 21, "RECORDS_LIMIT")
        for line in records:
            _inline_need(type(line) is bytes, "RECORD_TYPE")
        sizes = tuple(len(line) for line in records)
        _inline_need(all(0 < size <= 1024 for size in sizes), "RECORD_LIMIT")
        _inline_need(sum(sizes) <= 17488, "RECORDS_BYTES_LIMIT")
        _inline_need(sizes[0] <= 256 and sizes[-1] <= 256, "CONTROL_LIMIT")
        for line in records:
            _inline_need(line[-1] == 10 and all(0 < byte < 128 and byte not in (10, 13)
                         for byte in line[:-1]), "RECORD_ASCII")
        # Beide vollständigen Primitiveformen vor Feldbindungen und Callerabgleich.
        begin = _reassemble_control(records[0], ("t", "n", "n", "n"))
        end = _reassemble_control(records[-1], ("t", "n", "n", "n", "t"))
        fragments = []
        for line in records[1:-1]:
            fields = line[:-1].split(b"|", 4)
            _inline_need(len(fields) == 5 and fields[0] == b"P", "FRAGMENT_FORM")
            ordinal, sequence, total = tuple(_reassemble_decimal(token) for token in fields[1:4])
            payload = fields[4]
            _inline_need(1 <= ordinal <= 3 and 1 <= sequence <= 19 and 1 <= total <= 19,
                         "FRAGMENT_FORM")
            _inline_need(1 <= len(payload) <= 896 and len(line) - len(payload) <= 32,
                         "FRAGMENT_LIMIT")
            fragments.append((ordinal, sequence, total, payload))
        _inline_need(begin[0] == "PROFILE_BEGIN" and end[0] == "PROFILE_END", "CONTROL_FORM")
        for control in (begin, end):
            _inline_need(1 <= control[1] <= 3 and 1 <= control[2] <= 16368
                         and 1 <= control[3] <= 19, "CONTROL_FORM")
        _inline_need(len(end[4]) == 64 and all(char in "0123456789abcdef" for char in end[4]),
                     "FOOTER_FORM")
        _inline_need(begin[1:] == end[1:4], "RECORD_BINDING")
        ordinal, length, total = begin[1:]
        _inline_need(total == len(fragments) == (length + 895) // 896, "FRAGMENT_BINDING")
        for index, fragment in enumerate(fragments, 1):
            _inline_need(fragment[:3] == (ordinal, index, total), "FRAGMENT_BINDING")
            expected_size = 896 if index < total else length - 896 * (total - 1)
            _inline_need(len(fragment[3]) == expected_size, "FRAGMENT_BINDING")
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        _inline_need(_report_json(begin, encoder_anchor) + b"\n" == records[0], "NONCANONICAL")
        _inline_need(_report_json(end, encoder_anchor) + b"\n" == records[-1], "NONCANONICAL")
        data = b"".join(fragment[3] for fragment in fragments)
        digest = _report_sha(data, anchor)
        _inline_need(digest == end[4], "FOOTER_HASH")
        _inline_need(ordinal == expected_ordinal, "REPORT_ORDINAL_MISMATCH")
        header = _INLINE_HEADER.pack(b"DGNP001\0", 2, len(data))
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("REASSEMBLED_PROFILE_RECORDS", "NONE", (header, data, records))
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "REASSEMBLE_INTERNAL"
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_PROFILE_RECORDS", issue, None)
'''


def build_inline_reassemble_control_bootstrap(profile_raw, *, logical_profile,
                                             expected_soabi, expected_destshared) -> BootstrapSource:
    """Zehnte reine Quellenroute für gehaltene PROFILE-Records ohne Kanal- oder R-Claim."""
    selected = build_inline_body_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_REASSEMBLE + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_PROFILE_MATCH = r'''
def _profile_resolve(form):
    _inline_need(type(form) is tuple and len(form) == 4, "SCHEMA_FORM")
    _inline_need(type(form[0]) is str and form[0] == _INLINE_TAG, "VERSION_MISMATCH")
    _inline_need(type(form[1]) is str and form[1] == "REPORTED", "ROLE_MISMATCH")
    pool = form[2]
    _inline_need(type(pool) is tuple and len(pool) <= _INLINE_SEQUENCE, "POOL_LIMIT")
    for text in pool:
        _inline_need(type(text) is str, "POOL_FORM")
        _inline_need(len(text) <= _INLINE_TEXT and "\0" not in text
                     and len(text.encode("utf-8", "strict")) <= _INLINE_TEXT, "TEXT_LIMIT")
    _inline_need(pool == tuple(sorted(set(pool))), "POOL_FORM")
    used = set()

    def walk(value, schema):
        if type(schema) is str:
            if schema == "z" and value is None:
                return None
            _inline_need(type(value) is int and 0 <= value <= 99999999, "POSITION_TYPE")
            if schema == "n":
                return value
            _inline_need(value < len(pool), "REFERENCE_RANGE")
            used.add(value)
            return pool[value]
        _inline_need(type(value) is tuple and len(value) <= _INLINE_SEQUENCE, "SCHEMA_FORM")
        if schema[0] == "sequence":
            _inline_need(schema[2] is None or len(value) == schema[2], "SCHEMA_FORM")
            return tuple(walk(v, schema[1]) for v in value)
        _inline_need(len(value) == len(schema), "SCHEMA_FORM")
        return tuple(walk(v, sc) for v, sc in zip(value, schema))

    payload = walk(form[3], _REPORT_R)
    _inline_need(used == set(range(len(pool))), "POOL_UNUSED")
    return payload


def _inline_match_profile_report(header, metadata, *, expected_version, expected_reported):
    """Vollständiger deklarativer R-Abgleich; kein Footer-, Herkunfts- oder Runtimebeleg."""
    anchor, encoder_anchor = None, None
    try:
        _inline_need(type(expected_version) is str and expected_version == _INLINE_TAG,
                     "VERSION_SELECTION")
        _inline_need(type(header) is bytes and type(metadata) is bytes, "INPUT_TYPE")
        _report_shape(_REPORT_R, expected_reported)
        _inline_need(len(header) == _INLINE_HEADER.size, "HEADER_FORM")
        _inline_need(0 < len(metadata) <= _INLINE_METADATA_CAP - _INLINE_HEADER.size,
                     "METADATA_LIMIT")
        magic, role, length = _INLINE_HEADER.unpack(header)
        _inline_need(magic == b"DGNP001\0" and role == 2, "HEADER_FORM")
        _inline_need(length == len(metadata), "METADATA_LENGTH")
        parser = _InlineParser(metadata)
        form = parser.value()
        _inline_need(parser.pos == len(metadata), "JSON_END")
        actual = _profile_resolve(form)
        _report_shape(_REPORT_R, actual)
        # Jede vollständige Form und Semantik vor Encoding und inhaltlichem Vergleich.
        for reported in (actual, expected_reported):
            _command_context(reported[0])
            _semantic_worker(reported[0][5:] + reported[1:])
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        _inline_need(_report_json(_report_pack(actual), encoder_anchor) == metadata, "NONCANONICAL")
        _inline_need(actual == expected_reported, "REPORTED_MISMATCH")
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("MATCHED_REPORTED_DECLARATION", "NONE", (header, metadata, actual))
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "PROFILE_MATCH_INTERNAL"
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_PROFILE_REPORT", issue, None)
'''


def build_inline_profile_match_control_bootstrap(profile_raw, *, logical_profile,
                                                expected_soabi, expected_destshared) -> BootstrapSource:
    """Elfte additive Quellenroute für den reinen deklarativen R-Callerabgleich."""
    selected = build_inline_reassemble_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_PROFILE_MATCH + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_PROFILE_BODY_RELEASE = r'''
def _inline_plan_profile_body_release(header, metadata, *, expected_format, expected_phase,
                                      expected_reported, expected_context):
    """Atomarer deklarativer Plan; kein Send, Phasenübergang oder Einmalverbrauch."""
    anchor, encoder_anchor = None, None
    try:
        _inline_need(type(expected_format) is str and expected_format == _COMMAND_FORMAT,
                     "FORMAT_SELECTION")
        _inline_need(type(expected_phase) is str and expected_phase == "AWAIT_PROFILE",
                     "PHASE_SELECTION")
        _inline_need(type(header) is bytes and type(metadata) is bytes, "INPUT_TYPE")
        # Beide vollständigen Callerformen vor Parsing; keinerlei Callerdefaults.
        _report_shape(_REPORT_R, expected_reported)
        _report_shape(_INLINE_K, expected_context)
        _inline_need(len(header) == _INLINE_HEADER.size, "HEADER_FORM")
        _inline_need(0 < len(metadata) <= _INLINE_METADATA_CAP - _INLINE_HEADER.size,
                     "METADATA_LIMIT")
        magic, role, length = _INLINE_HEADER.unpack(header)
        _inline_need(magic == b"DGNP001\0" and role == 2, "HEADER_FORM")
        _inline_need(length == len(metadata), "METADATA_LENGTH")
        parser = _InlineParser(metadata)
        form = parser.value()
        _inline_need(parser.pos == len(metadata), "JSON_END")
        actual = _profile_resolve(form)
        _report_shape(_REPORT_R, actual)
        # Sämtliche Vollformen vor sämtlichen Semantiken, diese vor Encoding/SHA.
        for reported in (actual, expected_reported):
            _command_context(reported[0])
            _semantic_worker(reported[0][5:] + reported[1:])
        _command_context(expected_context)
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        _inline_need(_report_json(_report_pack(actual), encoder_anchor) == metadata,
                     "NONCANONICAL")
        _inline_need(actual == expected_reported, "REPORTED_MISMATCH")
        _inline_need(actual[0] == expected_reported[0] == expected_context, "CONTEXT_MISMATCH")
        # Innere frische Anker dürfen einen äußeren Bindungsverlust nicht neu baselinen.
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        command = _inline_command_encode("BODY_RELEASE", actual[0], expected_format=expected_format)
        _inline_need(type(command) is tuple and len(command) == 3
                     and type(command[0]) is str and type(command[1]) is str,
                     "PROFILE_BODY_RELEASE_INTERNAL")
        if command[0] != "FORMATTED_BOUND_COMMAND":
            _inline_need(command[0] == "REJECTED_BOUND_COMMAND" and command[2] is None,
                         "PROFILE_BODY_RELEASE_INTERNAL")
            raise _InlineSyntaxRejected(command[1]) from None
        _inline_need(command[1] == "NONE" and type(command[2]) is bytes
                     and 0 < len(command[2]) <= _COMMAND_LIMIT,
                     "PROFILE_BODY_RELEASE_INTERNAL")
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("PLANNED_DECLARED_BODY_RELEASE", "NONE",
                (header, metadata, actual, command[2], "BODY_RELEASE_READY"))
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "PROFILE_BODY_RELEASE_INTERNAL"
    # Auch nach Unterfunktionsfehler: Providerverlust > Encoderverlust > Fehler.
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_PROFILE_BODY_RELEASE_PLAN", issue, None)
'''


def build_inline_profile_body_release_control_bootstrap(profile_raw, *, logical_profile,
                                                       expected_soabi, expected_destshared) -> BootstrapSource:
    """Zwölfte additive Quellenroute für den reinen deklarativen BODY_RELEASE-Plan."""
    selected = build_inline_profile_match_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_PROFILE_BODY_RELEASE + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))


_INLINE_INPUT_COMPLETE = r'''
_INPUT_COMPLETE_SHAPE = ("t", "n", "t", "t")
_INPUT_COMPLETE_LIMIT = 256


def _input_complete_received(line):
    _inline_need(type(line) is bytes, "INPUT_COMPLETE_TYPE")
    _inline_need(0 < len(line) <= _INPUT_COMPLETE_LIMIT, "INPUT_COMPLETE_LIMIT")
    _inline_need(line[-1:] == b"\n" and line.count(b"\n") == 1 and b"\r" not in line,
                 "INPUT_COMPLETE_FORM")
    parser = _InlineParser(line[:-1])
    actual = parser.value()
    _inline_need(parser.pos == len(parser.data), "INPUT_COMPLETE_FORM")
    _report_shape(_INPUT_COMPLETE_SHAPE, actual)
    return actual


def _inline_match_input_complete(line, *, expected_format, expected_phase, expected_context):
    """Eigener deklarativer Rückkanalrecord; kein Bodycheck oder Phasenübergang."""
    anchor, encoder_anchor = None, None
    try:
        _inline_need(type(expected_format) is str and expected_format == _COMMAND_FORMAT,
                     "FORMAT_SELECTION")
        _inline_need(type(expected_phase) is str and expected_phase == "AWAIT_INPUT_COMPLETE",
                     "PHASE_SELECTION")
        _inline_need(type(line) is bytes, "INPUT_COMPLETE_TYPE")
        _inline_need(0 < len(line) <= _INPUT_COMPLETE_LIMIT, "INPUT_COMPLETE_LIMIT")
        # Beide vollständigen Primitiveformen vor Semantik, Repack und SHA.
        _report_shape(_INLINE_K, expected_context)
        actual = _input_complete_received(line)
        _command_context(expected_context)
        _inline_need(actual[0] == "INPUT_COMPLETE", "INPUT_COMPLETE_KIND")
        _inline_need(1 <= actual[1] <= 3, "INPUT_COMPLETE_FORM")
        _semantic_hex(actual[2], 64)
        _semantic_hex(actual[3], 64)
        encoder_anchor = _report_encoder_anchor()
        anchor = _semantic_provider_anchor()
        canonical = _report_json(actual, encoder_anchor) + b"\n"
        _inline_need(len(canonical) <= _INPUT_COMPLETE_LIMIT, "INPUT_COMPLETE_LIMIT")
        _inline_need(canonical == line, "INPUT_COMPLETE_CANONICAL")
        # Dieselben Anker über beide Kodierungen; kein inneres Rebaselining.
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        data = _command_k_json(expected_context, encoder_anchor)
        digest = _report_sha(data, anchor)
        _inline_need(actual == ("INPUT_COMPLETE", expected_context[5],
                                expected_context[3], digest), "INPUT_COMPLETE_MISMATCH")
        _report_encoder_check(encoder_anchor)
        _semantic_provider_check(anchor)
        return ("MATCHED_DECLARED_INPUT_COMPLETE", "NONE", (line, actual))
    except _InlineSyntaxRejected as error:
        issue = error.args[0]
    except UnicodeError:
        issue = "TEXT_LIMIT"
    except BaseException:
        issue = "INPUT_COMPLETE_INTERNAL"
    # Auch bei Callfehlern: Providerverlust > Encoderverlust > sonstiger Fehler.
    if encoder_anchor is not None:
        try:
            _report_encoder_check(encoder_anchor)
        except BaseException:
            issue = "REPORT_ENCODER_BINDING"
    if anchor is not None:
        try:
            _semantic_provider_check(anchor)
        except BaseException:
            issue = "HASH_PROVIDER_BINDING"
    return ("REJECTED_INPUT_COMPLETE", issue, None)
'''


def build_inline_input_complete_control_bootstrap(profile_raw, *, logical_profile,
                                                 expected_soabi, expected_destshared) -> BootstrapSource:
    """Dreizehnte additive Quellenroute für deklarativ gebundene INPUT_COMPLETE-Records."""
    selected = build_inline_profile_body_release_control_bootstrap(
        profile_raw, logical_profile=logical_profile, expected_soabi=expected_soabi,
        expected_destshared=expected_destshared)
    text = selected.source.decode("utf-8", "strict")
    old = '\nif __name__ == "__main__":\n    _CONTROL_RESULT = _load_bound_control()\n'
    _need(text.count(old) == 1, "TEMPLATE_FORM")
    text = text.replace(old, '\n' + _INLINE_INPUT_COMPLETE + old, 1)
    source = text.encode("utf-8", "strict")
    _need(len(source) <= MAX_SCRIPT_BYTES, "SCRIPT_LIMIT")
    return BootstrapSource(source, profile_raw, logical_profile,
                           hashlib.sha256(source).hexdigest(),
                           hashlib.sha256(profile_raw).hexdigest(), len(source))
