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
