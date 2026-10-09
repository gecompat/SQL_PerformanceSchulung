"""Reiner experimenteller E4-/Rawbody-Eingang ohne Worker oder Migration.

Die eigene empfangene Metadata und sämtliche Bodies werden vor dem Vergleich
mit dem separat gehaltenen Caller geprüft. Ein deklarativer Match attestiert
keine Herkunft, Verwendung, Trust, Consumption oder Replayfreiheit.
"""
from dataclasses import dataclass, field
import hashlib
import struct

import dgn007_pooled_profile_codec as codec

b = codec.b
input82 = b.input82
FORMAT = "pooled-combined-input-design/v1"
MAGIC = b"DGNC001\0"
HEADER = struct.Struct(">8sII")
MAX_METADATA_BYTES = 16384
MAX_MEMBER_BYTES = 131072
MAX_BODY_BYTES = 1048576
MAX_FRAME_BYTES = 1064960


class CombinedInputRejected(ValueError):
    """Ausschließlich feste technische Labels ohne Exceptionkette."""


@dataclass(frozen=True, slots=True, repr=False)
class ReceivedSource:
    ordinal: int
    module: str
    member: str
    sha256: str
    body: bytes


@dataclass(frozen=True, slots=True, repr=False)
class DecodedCombinedInput:
    input_metadata: tuple
    worker: b.WorkerDeclaration
    context: b.BindingContext
    sources: tuple[ReceivedSource, ...]
    declared_context_match: bool = field(default=True, init=False)
    status: str = field(default="MATCHED_DECLARED_COMBINED_INPUT", init=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    trust_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


def _need(condition, issue):
    if not condition:
        raise CombinedInputRejected(issue)


def _selection(value):
    _need(type(value) is str and value == FORMAT, "FORMAT_SELECTION")


def _encode(prepared, worker, expected_format):
    _selection(expected_format)
    # Bestehende API prüft alle fünf Formen samt gemeinsamem 64-KiB-Gate.
    metadata_frame = codec.encode_declared_form(prepared, worker,
        expected_version=codec.VERSION, role=codec.ROLES[0])
    metadata = metadata_frame[codec.HEADER.size:]
    total = sum(len(source.body) for source in prepared.sources)
    # Input82 wurde bereits vollständig geprüft; keine erneute Vorbereitung.
    return HEADER.pack(MAGIC, len(metadata), total) + metadata + b"".join(
        source.body for source in prepared.sources)


def _caller_metadata(prepared, worker):
    value = input82._metadata(prepared)
    b._worker(worker)
    context = b.derive_binding_context(prepared, worker.ordinal)
    descriptors = tuple(tuple(row[key] for key in
        ("ordinal", "module", "member", "size", "sha256")) for row in value["modules"])
    ip = tuple(value[key] for key in
        ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (
        descriptors, value["context_sha256"])
    return (ip, worker, context)


def _decode(frame, prepared, worker, expected_format):
    _selection(expected_format)
    _need(type(frame) is bytes, "FRAME_TYPE")
    _need(HEADER.size <= len(frame) <= MAX_FRAME_BYTES, "FRAME_LIMIT")
    magic, metadata_size, body_size = HEADER.unpack_from(frame)
    _need(magic == MAGIC, "FRAME_MAGIC")
    _need(0 < metadata_size <= MAX_METADATA_BYTES - HEADER.size
          and body_size <= MAX_BODY_BYTES, "FRAME_LIMIT")
    _need(HEADER.size + metadata_size + body_size == len(frame), "FRAME_LENGTH")
    # Erst jetzt begrenzte Metadata-Slices; keine fremdbestimmten Bodykopien.
    end_metadata = HEADER.size + metadata_size
    metadata_frame = codec.HEADER.pack(codec.MAGIC, 1, metadata_size) + frame[HEADER.size:end_metadata]
    _, actual = codec._decode(metadata_frame, 0)
    ip, received_worker, context = actual
    descriptors = context.modules
    _need(len(descriptors) == 9 and all(type(row.size) is int
        and 0 <= row.size <= MAX_MEMBER_BYTES for row in descriptors), "BODY_LIMIT")
    _need(sum(row.size for row in descriptors) <= MAX_BODY_BYTES, "BODY_LIMIT")
    _need(sum(row.size for row in descriptors) == body_size, "BODY_LENGTH")
    view, offset, bodies = memoryview(frame), end_metadata, []
    for row in descriptors:
        body = view[offset:offset + row.size]
        _need(hashlib.sha256(body).hexdigest() == row.sha256, "BODY_HASH")
        bodies.append(body)
        offset += row.size
    _need(offset == len(frame), "BODY_LENGTH")
    # Sämtliche empfangenen Felder/Hashes gültig, bevor ein Sollvergleich läuft.
    expected = _caller_metadata(prepared, worker)
    _need(actual == expected, "DECLARATION_MISMATCH")
    _need(all(body == source.body for body, source in zip(bodies, prepared.sources)), "BODY_MISMATCH")
    sources = tuple(ReceivedSource(row.ordinal, row.module, row.member, row.sha256, bytes(body))
                    for row, body in zip(descriptors, bodies))
    return DecodedCombinedInput(ip, received_worker, context, sources)


def _public(operation, *args):
    issue = None
    try:
        return operation(*args)
    except (CombinedInputRejected, codec.CodecRejected, codec.sizing._Rejected) as error:
        issue = str(error)
    except (b.BindingRejected, input82.InputRejected, AttributeError, TypeError,
            ValueError, UnicodeError, RecursionError, OverflowError, struct.error):
        issue = "INVALID_RECORD"
    # Außerhalb des Handlers: weder Rohfehler noch verborgener Context.
    raise CombinedInputRejected(issue)


def encode_combined_input(prepared, worker, *, expected_format) -> bytes:
    """Alle fünf erzeugten Metadataformen prüfen, dann neun Rohbytes rahmen."""
    return _public(_encode, prepared, worker, expected_format)


def decode_combined_input(frame, *, expected_format, prepared, expected_worker) -> DecodedCombinedInput:
    """Vollständiger empfangener M-/Bodybeleg gegen getrennte Callerwerte."""
    return _public(_decode, frame, prepared, expected_worker, expected_format)
