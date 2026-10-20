"""Reine Footer-/Kanalhashkomponenten; kein vollständiger SESSION_END-Matcher.

Geprüft werden deklarierte Felder und Bounds; übergebene Kanalbytes werden
gehasht. Tatsächliche Aufnahme, Trace, K8/D9, Providerbindung, EOF und
Ressourcen bleiben ungeprüft.
Die Standardbibliothek ist eine Kontrollannahme, keine Trustattestation.
"""
from dataclasses import dataclass, field
import hashlib
import json

MAX_FOOTER_BYTES = 256
MAX_CHANNEL_BYTES = 65536
_ROLES = ((8, 2, 24), (1, 0, 6), (3, 0, 10))
_CHANNEL_DOMAIN = b"DGN007-SESSION-CHANNEL/v1\x00"
_ISSUES = frozenset(("SESSION_END_TYPE", "SESSION_END_LIMIT", "SESSION_END_FORM",
                     "SESSION_END_CANONICAL", "SESSION_END_COUNTS"))


@dataclass(frozen=True, slots=True, repr=False)
class DecodedFooter:
    line: bytes = field(repr=False)
    values: tuple = field(repr=False)
    status: str = field(default="DECODED_SESSION_END_FOOTER", init=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    full_trace_verified: bool = field(default=False, init=False)
    context_verified: bool = field(default=False, init=False)
    channel_verified: bool = field(default=False, init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)

    def __repr__(self):
        return "DecodedFooter(PROJECT_SEMANTIC)"


class FooterRejected(ValueError):
    """Ausschließlich ein fester Issue ohne private Fehlerkette."""


class ChannelRejected(ValueError):
    """Ausschließlich ein fester Issue ohne private Kanal- oder Fehlerwerte."""


class _Rejected(Exception):
    pass


def _need(ok, issue="SESSION_END_FORM"):
    if not ok:
        raise _Rejected(issue)


def _fields(values):
    _need(type(values) is tuple, "SESSION_END_TYPE")
    _need(len(values) == 12)
    # Alle primitiven Typen vor Vergleichen oder Dispatch auf Feldwerten.
    for index, value in enumerate(values):
        expected = str if index in (0, 2, 11) else int
        _need(type(value) is expected, "SESSION_END_TYPE")
    _need(values[0] == "SESSION_END")
    for index in (2, 11):
        value = values[index]
        _need(len(value) == 64 and all(c in "0123456789abcdef" for c in value))
    for index in (1, 3, 4, 5, 6, 7, 8, 9, 10):
        _need(0 <= values[index] <= MAX_CHANNEL_BYTES, "SESSION_END_LIMIT")
    ordinal, fragments = values[1], values[3]
    _need(1 <= ordinal <= 3 and 1 <= fragments <= 19, "SESSION_END_COUNTS")
    sources, parents, offset = _ROLES[ordinal - 1]
    _need(values[4:9] == (sources, sources, parents, parents, fragments + offset),
          "SESSION_END_COUNTS")


def _encode(values):
    _fields(values)
    line = (json.dumps(values, ensure_ascii=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")
    _need(len(line) <= MAX_FOOTER_BYTES, "SESSION_END_LIMIT")
    # Notwendige Einzelworkergrenze, keine globale Drei-Worker-Buchung.
    _need(values[9] + values[10] + len(line) <= MAX_CHANNEL_BYTES,
          "SESSION_END_LIMIT")
    return line


def _integer(text):
    _need(len(text.lstrip("-")) <= 5, "SESSION_END_LIMIT")
    return int(text)


def _reject_number(_text):
    raise _Rejected("SESSION_END_FORM")


def _decode(line):
    _need(type(line) is bytes, "SESSION_END_TYPE")
    _need(0 < len(line) <= MAX_FOOTER_BYTES, "SESSION_END_LIMIT")
    _need(line.endswith(b"\n") and line.count(b"\n") == 1 and b"\r" not in line)
    value = json.loads(line[:-1].decode("ascii"), parse_int=_integer,
                       parse_float=_reject_number, parse_constant=_reject_number)
    _need(type(value) is list and len(value) == 12)
    values = tuple(value)
    canonical = _encode(values)
    _need(canonical == line, "SESSION_END_CANONICAL")
    return DecodedFooter(line, values)


def _public(operation, value, rejection=FooterRejected):
    issue = "SESSION_END_FORM"
    try:
        return operation(value)
    except _Rejected as error:
        if len(error.args) == 1 and error.args[0] in _ISSUES:
            issue = error.args[0]
    except Exception:
        pass
    # Außerhalb des except-Blocks: weder Cause noch privater Context.
    raise rejection(issue) from None


def encode_footer(values):
    """Zwölf deklarierte Felder formatieren, ohne Counts oder Hash zu ergänzen."""
    return _public(_encode, values)


def decode_footer(line):
    """Nur Footerfelder prüfen; keine Caller-, Trace-, Kanal- oder EOF-Abnahme."""
    return _public(_decode, line)


def _channel(arguments):
    ordinal, context_digest, stdout_prefix, stderr = arguments
    # Alle vier exakten Typen vor Bounds, Vergleich oder Hashprovideraufruf.
    _need(type(ordinal) is int and type(context_digest) is str
          and type(stdout_prefix) is bytes and type(stderr) is bytes,
          "SESSION_END_TYPE")
    _need(1 <= ordinal <= 3, "SESSION_END_COUNTS")
    _need(len(context_digest) == 64
          and all(c in "0123456789abcdef" for c in context_digest))
    out_size, err_size = len(stdout_prefix), len(stderr)
    _need(out_size + err_size <= MAX_CHANNEL_BYTES, "SESSION_END_LIMIT")
    # Inkrementell: keine zusätzliche vollständige Payloadkonkatenation.
    digest = hashlib.sha256()
    for part in (_CHANNEL_DOMAIN, bytes((ordinal,)), bytes.fromhex(context_digest),
                 out_size.to_bytes(4, "big"), stdout_prefix,
                 err_size.to_bytes(4, "big"), stderr):
        digest.update(part)
    result = digest.hexdigest()
    _need(type(result) is str, "SESSION_END_FORM")
    _need(len(result) == 64 and all(c in "0123456789abcdef" for c in result))
    return result


def channel_digest(ordinal, context_digest, stdout_prefix, stderr):
    """Nur übergebene Rohbytes hashen; Caller bucht zusätzlich Footer/Workers.

    Keine Pipeaufnahme, EOF-, Kontext-, Provider- oder vollständige Kanalprüfung.
    """
    return _public(_channel, (ordinal, context_digest, stdout_prefix, stderr),
                   ChannelRejected)
