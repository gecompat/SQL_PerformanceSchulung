"""Reine Größenrechnung des vollständig erhaltenden Darstellungsentwurfs.

Nur separat ausgewählte Deklarationen; kein Bericht einer Workerbeobachtung.
Keine Wirebytes, Decoder, neuen Digests oder Änderung des Legacy-Matchers.
Eine passende Entwurfsgröße attestiert weder Herkunft noch Runtime oder Trust.
"""
from dataclasses import dataclass, field
import json

import dgn007_import_profile_binding as binding

HEADER_SIZE = 16
MAX_METADATA = 16384
DESIGN_TAG = "compact-binding-design"
FORM_NAMES = ("METADATA", "REPORTED", "INSTALLATION_PREIMAGE",
              "WORKER_PREIMAGE", "CONTEXT_PREIMAGE")


@dataclass(frozen=True, slots=True)
class FormSize:
    form: str
    bytes_including_header: int
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


def _installation(value):
    return (value.assumption, value.platform, value.implementation, value.version,
            value.executable, value.executable_target, value.prefixes, value.abi,
            value.paths, value.roots, value.inert_zip, value.flags, value.finders,
            value.hooks, tuple((r.path, r.size, r.sha256) for r in value.files))


def _modules(rows):
    return tuple((r.name, r.moduleName, r.specName, r.origin, r.file, r.kind,
                  r.locations, r.loader, r.loaderName, r.loaderPath, r.aliasGroup)
                 for r in rows)


def _descriptors(rows):
    return tuple((r.ordinal, r.module, r.member, r.size, r.sha256) for r in rows)


def _forms(prepared, worker):
    # Alle vollständigen Formen werden vor der ersten Größenrechnung geprüft.
    # Nur Legacy-Formguards; niemals die benannte Matcher-Kanonisierung aufrufen.
    metadata = binding.input82._metadata(prepared)
    binding._worker(worker)
    context = binding.derive_binding_context(prepared, worker.ordinal)
    binding._context(context)
    installation = _installation(worker.installation)
    modules = _modules(worker.modules)
    descriptor_rows = tuple((r["ordinal"], r["module"], r["member"], r["size"], r["sha256"])
                            for r in metadata["modules"])
    input_projection = (metadata["protocol"], metadata["commit"], metadata["raw27_binding"],
                        metadata["source_profile"], metadata["nonce"], descriptor_rows,
                        metadata["context_sha256"])
    context_projection = (context.commit, context.raw27_binding, context.source_profile,
                          context.nonce.hex(), _descriptors(context.modules),
                          context.ordinal, context.entry, context.phase)
    worker_projection = (worker.ordinal, worker.entry, worker.phase, installation,
                         worker.controls, modules)
    # REPORTED ist hier eine ausgewählte Deklaration für die Größenrechnung.
    # Sie ist ausdrücklich kein tatsächlich beobachteter Report.
    return ((DESIGN_TAG, "METADATA", input_projection, worker_projection, context_projection),
            (DESIGN_TAG, "REPORTED", context_projection, installation, worker.controls, modules),
            (DESIGN_TAG, "compact-installation-declaration", installation),
            (DESIGN_TAG, "compact-worker-declaration", worker_projection),
            (DESIGN_TAG, "compact-profile-binding-context", context_projection))


def _size(value):
    # Inkrementell zählen; kein vollständiger ASCII-Buffer oder frühes Cap-Abbrechen.
    # Einzelstrings sind zuvor auf 4096 UTF-8-Bytes und Sequenzen auf 256 begrenzt.
    encoder = json.JSONEncoder(ensure_ascii=True, sort_keys=True,
                               separators=(",", ":"), allow_nan=False)
    return HEADER_SIZE + sum(len(part) for part in encoder.iterencode(value))


def size_declared_profile(prepared, worker) -> SizingReport:
    """Alle fünf vollständigen Entwurfsgrößen, auch bei mehreren Überschreitungen.

    Der Caller hält die separat ausgewählte Deklaration und den ursprünglichen
    PreparedInput. Der Prüfer attestiert keinen früheren Prepare-/Aufnahmeerfolg.
    """
    try:
        values = _forms(prepared, worker)
        sizes = tuple(_size(value) for value in values)
        rows = tuple(FormSize(name, size, size > MAX_METADATA)
                     for name, size in zip(FORM_NAMES, sizes))
        status = "DESIGN_SIZING_OVERFLOW" if any(row.overflow for row in rows) else "DESIGN_SIZING_ONLY"
        return SizingReport(status, "NONE", worker.ordinal, rows)
    except (binding.BindingRejected, binding.input82.InputRejected, AttributeError,
            TypeError, ValueError, RecursionError):
        return SizingReport("REJECTED_DESIGN_SIZING", "INVALID_RECORD")
