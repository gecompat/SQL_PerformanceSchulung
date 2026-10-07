"""Reine Größenprüfung des lokalen verlustfreien Stringpoolentwurfs.

Nur separat gewählte Deklarationen; keine Wireausgabe, Decoder, neuen Digests,
Worker oder Änderung der alten Prüfer. Kleine Größen attestieren keine Herkunft.
"""
from dataclasses import dataclass, field
import json

import dgn007_compact_profile_sizing as compact

binding = compact.binding
HEADER_SIZE = 16
MAX_METADATA = 16384
MAX_POOL = 256
MAX_NODES = MAX_METADATA - HEADER_SIZE
MAX_DEPTH = 8
DESIGN_TAG = "pooled-binding-design/v1"
FORM_NAMES = compact.FORM_NAMES
ROLES = ("METADATA", "REPORTED", "pooled-installation-declaration/v1",
         "pooled-worker-declaration/v1", "pooled-profile-binding-context/v1")

# Exakte DTO-Typen und sämtliche positionsgebundenen Felder aus §12.
_FIELDS = {
    binding.FileFingerprint: ("path", "size", "sha256"),
    binding.SourceDescriptor: ("ordinal", "module", "member", "size", "sha256"),
    binding.InstallationDeclaration: ("assumption", "platform", "implementation", "version",
        "executable", "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip",
        "flags", "finders", "hooks", "files"),
    binding.ModuleDeclaration: ("name", "moduleName", "specName", "origin", "file", "kind",
        "locations", "loader", "loaderName", "loaderPath", "aliasGroup"),
    binding.WorkerDeclaration: ("ordinal", "entry", "phase", "installation", "controls", "modules"),
    binding.BindingContext: ("commit", "raw27_binding", "source_profile", "nonce", "modules",
                             "ordinal", "entry", "phase"),
}


@dataclass(frozen=True, slots=True)
class FormSize:
    form: str
    bytes_including_header: int
    pool_count: int
    overflow: bool


@dataclass(frozen=True, slots=True)
class SizingReport:
    status: str
    issue: str
    ordinal: int | None = None
    forms: tuple[FormSize, ...] = ()
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


class _Rejected(ValueError):
    pass


def _need(ok, issue="INVALID_RECORD"):
    if not ok:
        raise _Rejected(issue)


def _children(value):
    """Nur bereits formgeprüfte exakte Container; keine freie Iteration."""
    if type(value) is tuple:
        _need(len(value) <= 256)
        yield from value
    else:
        names = _FIELDS.get(type(value))
        _need(names is not None)
        for name in names:
            item = getattr(value, name)
            # Der Kontext hält dieselbe Nonce als bytes; die Form überträgt Hex.
            if type(value) is binding.BindingContext and name == "nonce":
                _need(type(item) is bytes and len(item) == 32)
                item = item.hex()
            yield item


def _preflight(payload):
    """Direkte DTO-Aufnahme vor Poolsortierung und größerer Projektion.

    E4, Tag, Rolle und Poolcontainer zählen vier Knoten. Jeder unterschiedliche
    Pooltext zählt zusätzlich; jedes physische Payloadvorkommen zählt erneut.
    Gehaltene Texte werden nicht kopiert. Pool257 beendet die Aufnahme geschlossen.
    """
    texts = set()
    nodes = 4

    def visit(value, depth):
        nonlocal nodes
        nodes += 1
        _need(nodes <= MAX_NODES, "NODE_LIMIT")
        typ = type(value)
        if typ is str:
            binding._text(value)
            if value not in texts:
                _need(len(texts) < MAX_POOL, "POOL_LIMIT")
                texts.add(value)
                nodes += 1
                _need(nodes <= MAX_NODES, "NODE_LIMIT")
        elif typ is int:
            _need(0 <= value <= 99999999)
        elif value is None:
            pass
        else:
            _need(depth <= MAX_DEPTH, "DEPTH_LIMIT")
            for child in _children(value):
                visit(child, depth + 1)

    visit(payload, 2)
    return tuple(sorted(texts))


def _project(value, indices):
    # Aufruf erst nach vollständiger Vorprüfung aller fünf Payloads.
    if type(value) is str:
        return indices[value]
    if type(value) is int or value is None:
        return value
    return tuple(_project(v, indices) for v in _children(value))


def _forms(prepared, worker):
    # Formfehler werden vor irgendeiner Pool-/Kostenprüfung vollständig geprüft.
    metadata = binding.input82._metadata(prepared)
    binding._worker(worker)
    context = binding.derive_binding_context(prepared, worker.ordinal)
    binding._context(context)
    # Kleine feste I7-Projektion; D9 bleibt zunächst eine Folge geprüfter DTOs.
    ip = tuple(metadata[k] for k in ("protocol", "commit", "raw27_binding",
        "source_profile", "nonce")) + (context.modules, metadata["context_sha256"])
    payloads = ((ip, worker, context),
                (context, worker.installation, worker.controls, worker.modules),
                (worker.installation,), (worker,), (context,))
    pools = tuple(_preflight(payload) for payload in payloads)
    return tuple((DESIGN_TAG, role, pool,
                  _project(payload, {text: n for n, text in enumerate(pool)}))
                 for role, pool, payload in zip(ROLES, pools, payloads))


def _size(form):
    # Nur ASCII-Längen, keine fertigen Wirebytes oder vollständigen JSONpuffer.
    encoder = json.JSONEncoder(ensure_ascii=True, sort_keys=True,
                              separators=(",", ":"), allow_nan=False)
    return HEADER_SIZE + sum(len(part) for part in encoder.iterencode(form))


def size_declared_profile(prepared, worker) -> SizingReport:
    """Alle fünf Größen und Poolanzahlen bei Byteoverflow; Formfehler ohne Formen.

    Kein deklarativer Match oder Metadatentransfer. Der Caller hält die eigene
    vorgewählte Deklaration; frühere Prepare-/Aufnahmeerfolge werden nicht attestiert.
    """
    try:
        forms = _forms(prepared, worker)
        sizes = tuple(_size(form) for form in forms)
        rows = tuple(FormSize(name, size, len(form[2]), size > MAX_METADATA)
                     for name, size, form in zip(FORM_NAMES, sizes, forms))
        status = "POOL_DESIGN_SIZING_OVERFLOW" if any(r.overflow for r in rows) else "POOL_DESIGN_SIZING_ONLY"
        return SizingReport(status, "NONE", worker.ordinal, rows)
    except _Rejected as error:
        return SizingReport("REJECTED_POOL_DESIGN_SIZING", str(error))
    except (binding.BindingRejected, binding.input82.InputRejected, AttributeError,
            TypeError, ValueError, RecursionError):
        return SizingReport("REJECTED_POOL_DESIGN_SIZING", "INVALID_RECORD")
