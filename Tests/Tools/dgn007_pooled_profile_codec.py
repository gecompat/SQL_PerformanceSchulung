"""Experimenteller reiner E4-Formcodec; keine Worker- oder Legacyroute.

Der Caller hält seine Deklaration und Rawbodies getrennt. Einzelne S/W-Formen
tragen keinen Kontext. Auch vollständiger skalarer Match attestiert keine
Herkunft, Consumption, Replayfreiheit, Runtime, Trust oder UsedBytes.
"""
from dataclasses import dataclass, field
import hashlib
import json
import struct

import dgn007_pooled_profile_sizing as sizing

b = sizing.binding
VERSION = sizing.DESIGN_TAG
ROLES = sizing.ROLES
HEADER = struct.Struct(">8sII")
MAGIC = b"DGNP001\0"
MAX_FRAME = 16384
MAX_OUTPUT = 65536
MAX_NODES = 16368
MAX_DEPTH = 8
MAX_SEQUENCE = 256
MAX_TEXT = 4096


class CodecRejected(ValueError):
    """Feste Labels, ohne Rohfehlercontext."""


@dataclass(frozen=True, slots=True, repr=False)
class DecodedForm:
    role: str
    payload: tuple
    declared_context_match: bool
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


@dataclass(frozen=True, slots=True)
class CodecReport:
    status: str
    issue: str
    assumption: str = ""
    installation_digest: str = ""
    worker_digest: str = ""
    context_digest: str = ""
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


def _need(ok, issue="INVALID_RECORD"):
    if not ok:
        raise CodecRejected(issue)


def _selection(version, role):
    _need(type(version) is str and version == VERSION, "VERSION_SELECTION")
    _need(type(role) is str and role in ROLES, "ROLE_SELECTION")
    return ROLES.index(role)


def _canonical(form):
    chunks, size = [], HEADER.size
    encoder = json.JSONEncoder(ensure_ascii=True, sort_keys=True,
                              separators=(",", ":"), allow_nan=False)
    for piece in encoder.iterencode(form):
        size += len(piece)
        _need(size <= MAX_FRAME, "FRAME_LIMIT")
        chunks.append(piece.encode("ascii"))
    return b"".join(chunks)


def _gated_forms(prepared, worker):
    # Sämtliche Semantik-/Pool-/Knotengates vor Byteaufnahme oder Digests.
    forms = sizing._forms(prepared, worker)
    lengths = tuple(sizing._size(form) for form in forms)
    _need(all(n <= MAX_FRAME for n in lengths), "FRAME_LIMIT")
    _need(sum(lengths) <= MAX_OUTPUT, "OUTPUT_LIMIT")
    return forms


def _frame(form, index):
    body = _canonical(form)
    return HEADER.pack(MAGIC, index + 1, len(body)) + body


class _Parser:
    """Nur Arrays/Text/null/nonnegative Integer; Bounds vor jedem Aufbau."""
    def __init__(self, data):
        self.data, self.pos, self.nodes = data, 0, 0

    def _take(self, byte):
        _need(self.pos < len(self.data) and self.data[self.pos] == byte, "JSON_FORM")
        self.pos += 1

    def _hex4(self):
        _need(self.pos + 4 <= len(self.data), "JSON_TEXT")
        value = 0
        for offset in range(4):
            ch = self.data[self.pos + offset]
            _need(ch in b"0123456789abcdefABCDEF", "JSON_TEXT")
            value = value * 16 + int(chr(ch), 16)
        self.pos += 4
        return value

    def _string(self):
        self._take(34)
        chars, utf8 = [], 0
        escapes = {34: '"', 92: "\\", 47: "/", 98: "\b", 102: "\f",
                   110: "\n", 114: "\r", 116: "\t"}
        while True:
            _need(self.pos < len(self.data), "JSON_TEXT")
            ch = self.data[self.pos]
            self.pos += 1
            if ch == 34:
                return "".join(chars)
            if ch == 92:
                _need(self.pos < len(self.data), "JSON_TEXT")
                esc = self.data[self.pos]
                self.pos += 1
                if esc == 117:
                    cp = self._hex4()
                    if 0xD800 <= cp <= 0xDBFF:
                        self._take(92)
                        self._take(117)
                        low = self._hex4()
                        _need(0xDC00 <= low <= 0xDFFF, "JSON_TEXT")
                        cp = 0x10000 + ((cp - 0xD800) << 10) + low - 0xDC00
                    else:
                        _need(not 0xDC00 <= cp <= 0xDFFF, "JSON_TEXT")
                    char = chr(cp)
                else:
                    _need(esc in escapes, "JSON_TEXT")
                    char = escapes[esc]
            else:
                _need(32 <= ch < 128, "JSON_TEXT")
                char = chr(ch)
            _need(char != "\0", "JSON_TEXT")
            utf8 += len(char.encode("utf-8"))
            _need(utf8 <= MAX_TEXT, "TEXT_LIMIT")
            chars.append(char)

    def value(self, depth=1):
        self.nodes += 1
        _need(self.nodes <= MAX_NODES, "NODE_LIMIT")
        _need(self.pos < len(self.data), "JSON_FORM")
        ch = self.data[self.pos]
        if ch == 91:
            _need(depth <= MAX_DEPTH, "DEPTH_LIMIT")
            self.pos += 1
            rows = []
            if self.pos < len(self.data) and self.data[self.pos] == 93:
                self.pos += 1
                return ()
            while True:
                _need(len(rows) < MAX_SEQUENCE, "SEQUENCE_LIMIT")
                rows.append(self.value(depth + 1))
                _need(self.pos < len(self.data), "JSON_FORM")
                if self.data[self.pos] == 93:
                    self.pos += 1
                    return tuple(rows)
                self._take(44)
        if ch == 34:
            return self._string()
        if ch == 110:
            _need(self.data[self.pos:self.pos + 4] == b"null", "JSON_FORM")
            self.pos += 4
            return None
        _need(48 <= ch <= 57, "JSON_FORM")
        start = self.pos
        while self.pos < len(self.data) and 48 <= self.data[self.pos] <= 57:
            self.pos += 1
            _need(self.pos - start <= 8, "INTEGER_LIMIT")
        _need(self.pos - start == 1 or self.data[start] != 48, "JSON_FORM")
        return int(self.data[start:self.pos])


# Positionstypen, keine selbstbeschreibenden Integercodes oder freien Objekte.
def _seq(schema, count=None):
    return ("sequence", schema, count)


D = ("n", "t", "t", "n", "t")
F = ("t", "n", "t")
S = ("t", "t", "t", _seq("n", 3), "t", "t", _seq("t", 4), "t",
     _seq("t"), _seq("t", 2), "t", _seq("n", 6), _seq("t", 3),
     _seq("t", 2), _seq(F))
P = ("t", "t", "z", "t", "t", "t", _seq("t"), "t", "t", "t", _seq("t"))
W = ("n", "t", "t", S, _seq("t"), _seq(P))
K = ("t", "t", "t", "t", _seq(D, 9), "n", "t", "t")
I = ("t", "t", "t", "t", "t", _seq(D, 9), "t")
SCHEMAS = ((I, W, K), (K, S, _seq("t"), _seq(P)), (S,), (W,), (K,))


def _resolve(form, index):
    _need(type(form) is tuple and len(form) == 4, "SCHEMA_FORM")
    _need(type(form[0]) is str and form[0] == VERSION, "VERSION_MISMATCH")
    _need(type(form[1]) is str and form[1] == ROLES[index], "ROLE_MISMATCH")
    pool = form[2]
    _need(type(pool) is tuple and len(pool) <= 256, "POOL_LIMIT")
    for text in pool:
        _need(type(text) is str, "POOL_FORM")
        b._text(text)
    _need(pool == tuple(sorted(set(pool))), "POOL_FORM")
    used = set()

    def walk(value, schema):
        if type(schema) is str:
            if schema == "z" and value is None:
                return None
            _need(type(value) is int and 0 <= value <= 99999999, "POSITION_TYPE")
            if schema == "n":
                return value
            _need(value < len(pool), "REFERENCE_RANGE")
            used.add(value)
            return pool[value]
        _need(type(value) is tuple and len(value) <= 256, "SCHEMA_FORM")
        if schema[0] == "sequence":
            _need(schema[2] is None or len(value) == schema[2], "SCHEMA_FORM")
            return tuple(walk(v, schema[1]) for v in value)
        _need(len(value) == len(schema), "SCHEMA_FORM")
        return tuple(walk(v, sc) for v, sc in zip(value, schema))

    payload = walk(form[3], SCHEMAS[index])
    _need(used == set(range(len(pool))), "POOL_UNUSED")
    return payload


def _installation(row):
    return b.InstallationDeclaration(*row[:-1], tuple(b.FileFingerprint(*r) for r in row[-1]))


def _modules(rows):
    return tuple(b.ModuleDeclaration(*r) for r in rows)


def _worker(row):
    return b.WorkerDeclaration(*row[:3], _installation(row[3]), row[4], _modules(row[5]))


def _context(row):
    b._hex(row[3], 64)
    return b.BindingContext(*row[:3], bytes.fromhex(row[3]),
        tuple(b.SourceDescriptor(*r) for r in row[4]), *row[5:])


def _semantics(payload, index):
    # Erst vollständige positionsgebundene Rückgewinnung/Usedset, dann DTOs.
    if index == 0:
        ip, wr, kr = payload
        worker, context = _worker(wr), _context(kr)
        b._worker(worker)
        b._context(context)
        expected = b._input_metadata(context)
        descriptors = tuple(tuple(r[k] for k in ("ordinal", "module", "member", "size", "sha256"))
                            for r in expected["modules"])
        original = tuple(expected[k] for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (
            descriptors, expected["context_sha256"])
        _need(ip == original, "INPUT_BINDING")
        _need((worker.ordinal, worker.entry, worker.phase) ==
              (context.ordinal, context.entry, context.phase), "CONTEXT_MISMATCH")
        return (ip, worker, context)
    if index == 1:
        report = b.ReportedProfile(_context(payload[0]), _installation(payload[1]),
                                   payload[2], _modules(payload[3]))
        b._reported(report)
        return (report,)
    if index == 2:
        value = _installation(payload[0])
        b._installation(value)
    elif index == 3:
        value = _worker(payload[0])
        b._worker(value)
    else:
        value = _context(payload[0])
        b._context(value)
    return (value,)


def _decode(frame, index):
    _need(type(frame) is bytes, "FRAME_TYPE")
    _need(HEADER.size <= len(frame) <= MAX_FRAME, "FRAME_LIMIT")
    magic, code, length = HEADER.unpack_from(frame)
    _need(magic == MAGIC, "FRAME_MAGIC")
    _need(code == index + 1, "FRAME_ROLE")
    _need(0 < length <= MAX_FRAME - HEADER.size and HEADER.size + length == len(frame), "FRAME_LENGTH")
    body = frame[HEADER.size:]
    parser = _Parser(body)
    form = parser.value()
    _need(parser.pos == len(body), "JSON_END")
    payload = _resolve(form, index)
    _need(_canonical(form) == body, "NONCANONICAL")
    return form, _semantics(payload, index)


def _comparison(form, expected, index):
    _need(form == expected, "DECLARATION_MISMATCH")
    return index in (0, 1, 4)


def _public(operation, *args):
    issue = None
    try:
        return operation(*args)
    except (CodecRejected, sizing._Rejected) as error:
        issue = str(error)
    except (b.BindingRejected, b.input82.InputRejected, AttributeError, TypeError,
            ValueError, UnicodeError, RecursionError, OverflowError, struct.error):
        issue = "INVALID_RECORD"
    raise CodecRejected(issue)


def _encode(prepared, worker, version, role, full):
    index = _selection(version, role)
    forms = _gated_forms(prepared, worker)
    return tuple(_frame(v, n) for n, v in enumerate(forms)) if full else _frame(forms[index], index)


def encode_declared_form(prepared, worker, *, expected_version, role) -> bytes:
    """Ein Frame erst nach sämtlichen fünf Gates einschließlich 64 KiB."""
    return _public(_encode, prepared, worker, expected_version, role, False)


def encode_declared_formset(prepared, worker, *, expected_version) -> tuple:
    """Fünf Frames in fester Rollenfolge; keine kombinierten Rawbodies."""
    return _public(_encode, prepared, worker, expected_version, ROLES[0], True)


def _decode_selected(frame, version, role, prepared, worker):
    index = _selection(version, role)
    # Callerformen dienen nur anschließendem Vergleich, niemals als Defaults.
    metadata = b.input82._metadata(prepared)
    b._worker(worker)
    context = b.derive_binding_context(prepared, worker.ordinal)
    if index == 0:
        descriptors = tuple(tuple(r[k] for k in ("ordinal", "module", "member", "size", "sha256"))
                            for r in metadata["modules"])
        ip = tuple(metadata[k] for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (
            descriptors, metadata["context_sha256"])
        expected = (ip, worker, context)
    elif index == 1:
        expected = (b.ReportedProfile(context, worker.installation, worker.controls, worker.modules),)
    elif index == 2:
        expected = (worker.installation,)
    elif index == 3:
        expected = (worker,)
    else:
        expected = (context,)
    form, payload = _decode(frame, index)
    bound = _comparison(payload, expected, index)
    return DecodedForm(role, payload, bound)


def decode_declared_form(frame, *, expected_version, expected_role,
                         prepared, expected_worker) -> DecodedForm:
    """Eigene vollständige Formprüfung vor rein deklarativem Caller-Vergleich."""
    return _public(_decode_selected, frame, expected_version, expected_role, prepared, expected_worker)


def _digests(forms):
    return tuple(hashlib.sha256(_canonical(form)).hexdigest() for form in forms[2:])


def _digest_profile(prepared, worker, version):
    _selection(version, ROLES[0])
    forms = _gated_forms(prepared, worker)
    return CodecReport("CHECKED_DECLARED_FORMSET", "NONE", b.ASSUMPTION, *_digests(forms))


def digest_declared_profile(prepared, worker, *, expected_version) -> CodecReport:
    return _public(_digest_profile, prepared, worker, expected_version)


def _match(frames, prepared, worker, version):
    _selection(version, ROLES[0])
    _need(type(frames) is tuple and len(frames) == 5, "FORMSET_TYPE")
    _need(all(type(f) is bytes for f in frames), "FRAME_TYPE")
    _need(all(HEADER.size <= len(f) <= MAX_FRAME for f in frames), "FRAME_LIMIT")
    _need(sum(len(f) for f in frames) <= MAX_OUTPUT, "OUTPUT_LIMIT")
    expected = _gated_forms(prepared, worker)
    # Keine frühe Vergleichsabweichung darf einen späteren Formfehler verdecken.
    parsed = tuple(_decode(frame, n)[0] for n, frame in enumerate(frames))
    for index, form in enumerate(parsed):
        _comparison(form, expected[index], index)
    return CodecReport("MATCHED_DECLARED_FORMSET", "NONE", b.ASSUMPTION, *_digests(parsed))


def match_declared_formset(frames, prepared, expected_worker, *, expected_version) -> CodecReport:
    try:
        return _public(_match, frames, prepared, expected_worker, expected_version)
    except CodecRejected as error:
        return CodecReport("REJECTED_DECLARED_FORMSET", str(error))
