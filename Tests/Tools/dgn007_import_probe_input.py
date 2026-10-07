#!/usr/bin/env python3
"""Kontrollseitiger gebundener Eingang; keine Worker- oder Importausführung.

Der Nonce bindet einen Frame an den separat gehaltenen Parent-Snapshot. Er
attestiert weder einen Actor noch Replayfreiheit eines späteren Workers.
Der Parent ist vertrauenswürdiger Kontrollinput; seine Form kann einen früheren
prepare_input-PASS nicht unabhängig attestieren, auch bei identischen Bytes.
Rohbytes werden ohne LF-Konversion übernommen. Decoder und Encoder lesen
keine Dateien; nur prepare_input nutzt den unveränderten Bundle-Verifier.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import secrets
import struct

import dgn007_source_bundle as bundle
import dgn007_execution_edges as edges

MAGIC = b"DGNI001\0"
PROTOCOL = "dgn007-import-input/v1"
HEADER = struct.Struct(">8sII")
MAX_MEMBER_BYTES = 128 * 1024
MAX_BODY_BYTES = 1024 * 1024
MAX_METADATA_BYTES = 16 * 1024  # Einschließlich HEADER.size.
MAX_FRAME_BYTES = MAX_BODY_BYTES + MAX_METADATA_BYTES
MODULES = bundle.MODULES


@dataclass(frozen=True, slots=True)
class SourceBytes:
    module: str
    member: str
    sha256: str
    body: bytes = field(repr=False)


@dataclass(frozen=True, slots=True)
class PreparedInput:
    """Nur unveränderlicher Eingang; keine Importverwendungsreceipt."""
    commit: str
    raw27_binding: str
    source_profile: str
    nonce: bytes = field(repr=False)
    sources: tuple[SourceBytes, ...] = field(repr=False)
    status: str = field(default="PREPARED_INPUT_ONLY", init=False)
    validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


@dataclass(frozen=True, slots=True)
class PreparationResult:
    status: str
    issue: str
    verification: bundle.Report | None = None
    prepared: PreparedInput | None = field(default=None, repr=False)
    runtime_attested: bool = field(default=False, init=False)
    import_used_bytes_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)


class InputRejected(ValueError):
    """Ausschließlich feste technische Fehlerlabels ohne Payload."""


def _require(condition: bool, issue: str) -> None:
    if not condition:
        raise InputRejected(issue)


def _hex(value, size: int) -> bool:
    return type(value) is str and re.fullmatch("[0-9a-f]{" + str(size) + "}", value) is not None


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def _binding(bodies) -> str:
    rows = [[p, hashlib.sha256(bodies[p]).hexdigest()] for p in sorted(bodies)]
    return hashlib.sha256(json.dumps(rows, ensure_ascii=True,
                                     separators=(",", ":")).encode("ascii")).hexdigest()


def _metadata(prepared: PreparedInput) -> dict:
    _require(type(prepared) is PreparedInput, "PARENT_SHAPE")
    _require(_hex(prepared.commit, 40) and _hex(prepared.raw27_binding, 64), "PARENT_CONTEXT")
    _require(type(prepared.source_profile) is str and prepared.source_profile == edges.PROFILE,
             "PARENT_CONTEXT")
    _require(type(prepared.nonce) is bytes and len(prepared.nonce) == 32, "PARENT_CONTEXT")
    _require(type(prepared.sources) is tuple and len(prepared.sources) == 9, "PARENT_SHAPE")
    _require(type(prepared.status) is str and prepared.status == "PREPARED_INPUT_ONLY"
             and type(prepared.validation_scope) is str and prepared.validation_scope == "PROJECT_SEMANTIC"
             and prepared.runtime_attested is False and prepared.import_used_bytes_attested is False
             and prepared.method_approved is False,
             "PARENT_SHAPE")
    rows, total = [], 0
    for ordinal, (source, (module, member)) in enumerate(zip(prepared.sources, MODULES)):
        _require(type(source) is SourceBytes, "PARENT_SHAPE")
        _require(type(source.module) is str and source.module == module
                 and type(source.member) is str and source.member == member, "PARENT_MAPPING")
        _require(type(source.body) is bytes and len(source.body) <= MAX_MEMBER_BYTES, "PARENT_LIMIT")
        total += len(source.body)
        _require(total <= MAX_BODY_BYTES, "PARENT_LIMIT")
        _require(_hex(source.sha256, 64)
                 and hashlib.sha256(source.body).hexdigest() == source.sha256, "PARENT_HASH")
        rows.append(dict(ordinal=ordinal, module=module, member=member,
                         size=len(source.body), sha256=source.sha256))
    value = dict(protocol=PROTOCOL, commit=prepared.commit, raw27_binding=prepared.raw27_binding,
                 source_profile=prepared.source_profile, nonce=prepared.nonce.hex(), modules=rows)
    value["context_sha256"] = hashlib.sha256(_canonical(value)).hexdigest()
    _require(len(_canonical(value)) + HEADER.size <= MAX_METADATA_BYTES, "PARENT_LIMIT")
    return value


def _encode(prepared: PreparedInput) -> bytes:
    metadata = _canonical(_metadata(prepared))
    total = sum(len(s.body) for s in prepared.sources)
    return HEADER.pack(MAGIC, len(metadata), total) + metadata + b"".join(s.body for s in prepared.sources)


def _parse(metadata: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            _require(key not in value, "METADATA_DUPLICATE")
            value[key] = item
        return value

    def integer(text):
        _require(len(text) <= 7, "METADATA_NUMBER")
        return int(text)

    def forbidden(_):
        raise InputRejected("METADATA_NUMBER")

    value = json.loads(metadata.decode("ascii"), object_pairs_hook=pairs, parse_int=integer,
                       parse_float=forbidden, parse_constant=forbidden)
    _require(type(value) is dict and set(value) == {
        "protocol", "commit", "raw27_binding", "source_profile", "nonce", "modules", "context_sha256"},
        "METADATA_SHAPE")
    _require(type(value["modules"]) is list and len(value["modules"]) == 9, "METADATA_SHAPE")
    total = 0
    for ordinal, (row, (module, member)) in enumerate(zip(value["modules"], MODULES)):
        _require(type(row) is dict and set(row) == {"ordinal", "module", "member", "size", "sha256"},
                 "METADATA_SHAPE")
        _require(type(row["ordinal"]) is int and row["ordinal"] == ordinal
                 and type(row["module"]) is str and row["module"] == module
                 and type(row["member"]) is str and row["member"] == member, "METADATA_MAPPING")
        _require(type(row["size"]) is int and 0 <= row["size"] <= MAX_MEMBER_BYTES, "METADATA_LIMIT")
        _require(_hex(row["sha256"], 64), "METADATA_HASH")
        total += row["size"]
    _require(total <= MAX_BODY_BYTES, "METADATA_LIMIT")
    for key, size in (("commit", 40), ("raw27_binding", 64), ("nonce", 64), ("context_sha256", 64)):
        _require(_hex(value[key], size), "METADATA_CONTEXT")
    _require(type(value["protocol"]) is str and value["protocol"] == PROTOCOL
             and type(value["source_profile"]) is str and value["source_profile"] == edges.PROFILE,
             "METADATA_CONTEXT")
    return value


def _decode(frame: bytes, expected: PreparedInput) -> PreparedInput:
    parent = _metadata(expected)
    _require(type(frame) is bytes, "FRAME_SHAPE")
    _require(HEADER.size <= len(frame) <= MAX_FRAME_BYTES, "FRAME_LIMIT")
    magic, metadata_size, body_size = HEADER.unpack_from(frame)
    _require(magic == MAGIC, "FRAME_MAGIC")
    _require(0 < metadata_size <= MAX_METADATA_BYTES - HEADER.size
             and body_size <= MAX_BODY_BYTES, "FRAME_LIMIT")
    _require(HEADER.size + metadata_size + body_size == len(frame), "FRAME_LENGTH")
    # Längenprüfung vor Metadata-Slice/Parse und vor jeder Bodykopie.
    metadata_bytes = frame[HEADER.size:HEADER.size + metadata_size]
    value = _parse(metadata_bytes)
    _require(sum(row["size"] for row in value["modules"]) == body_size, "FRAME_LENGTH")
    context = dict(value)
    digest = context.pop("context_sha256")
    _require(hashlib.sha256(_canonical(context)).hexdigest() == digest, "CONTEXT_HASH")
    _require(value == parent, "PARENT_MISMATCH")
    offset = HEADER.size + metadata_size
    view = memoryview(frame)
    for row, source in zip(value["modules"], expected.sources):
        body = view[offset:offset + row["size"]]
        _require(hashlib.sha256(body).hexdigest() == source.sha256 and body == source.body, "BODY_MISMATCH")
        offset += row["size"]
    _require(offset == len(frame), "FRAME_LENGTH")
    return expected


def _public(operation, *args):
    issue = None
    try:
        return operation(*args)
    except InputRejected as error:
        issue = str(error)
    except (AttributeError, ValueError, UnicodeError, RecursionError, OverflowError):
        issue = "INVALID_RECORD"
    # Außerhalb des except: keine verborgene Rohfehler-/Payloadcontextkette.
    raise InputRejected(issue)


def encode_input(prepared: PreparedInput) -> bytes:
    """Prüft den kontrollseitigen Snapshot erneut und rahmt seine Rohbytes."""
    return _public(_encode, prepared)


def decode_input(frame: bytes, *, expected: PreparedInput) -> PreparedInput:
    """Nur Kontext-/Rohbyteprüfung gegen den separat gehaltenen Parent-Snapshot."""
    return _public(_decode, frame, expected)


def prepare_input(repository: Path, commit: str, candidate: Path) -> PreparationResult:
    """Nach unverändertem Bundle-/Edge-PASS einen frischen Eingang vorbereiten."""
    if type(repository) is not type(Path()) or type(candidate) is not type(Path()) or not _hex(commit, 40):
        return PreparationResult("FAIL_PREPARE_INPUT", "PREPARE_ARGUMENT")
    captured = []

    def bound(bodies):
        edges._validate_edges(bodies)
        sources = tuple(SourceBytes(module, member, hashlib.sha256(bodies[member]).hexdigest(), bodies[member])
                        for module, member in MODULES)
        captured.append((_binding(bodies), sources))

    verification = bundle.verify_bundle(repository, commit, candidate, bound_validator=bound)
    if verification.status != "PASS_STATIC_CANDIDATE":
        return PreparationResult("FAIL_PREPARE_INPUT", verification.issue, verification)
    if len(captured) != 1 or captured[0][0] != verification.raw_binding:
        return PreparationResult("FAIL_PREPARE_INPUT", "PREPARE_BINDING", verification)
    try:
        nonce = secrets.token_bytes(32)
    except (OSError, ValueError, TypeError):
        return PreparationResult("FAIL_PREPARE_INPUT", "PREPARE_NONCE", verification)
    if type(nonce) is not bytes or len(nonce) != 32:
        return PreparationResult("FAIL_PREPARE_INPUT", "PREPARE_NONCE", verification)
    prepared = PreparedInput(commit, verification.raw_binding, edges.PROFILE, nonce, captured[0][1])
    try:
        encode_input(prepared)
    except InputRejected:
        return PreparationResult("FAIL_PREPARE_INPUT", "PREPARE_SHAPE", verification)
    return PreparationResult("PREPARED_INPUT_ONLY", "NONE", verification, prepared)
