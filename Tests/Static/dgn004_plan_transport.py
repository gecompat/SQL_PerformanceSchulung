"""Pure decoder for already parsed DGN-004 numbered UTF-16 plan chunks."""
from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Iterable


MAX_RAW_PLAN_BYTES = 512 * 1024
MAX_UTF8_PLAN_BYTES = 256 * 1024
MAX_CHUNK_BYTES = 100
_HEX = re.compile(r"\A[0-9A-Fa-f]+\Z")
_SHA256 = re.compile(r"\A[0-9A-Fa-f]{64}\Z")


class PlanTransportError(ValueError):
    """Reject an incomplete, corrupted, or oversized plan payload."""


def decode_plan_chunks(
    chunks: Iterable[tuple[int, str]],
    *,
    declared_chunk_count: int,
    declared_byte_length: int,
    server_sha256: str,
) -> str:
    """Validate and decode parsed (sequence, hex-payload) records.

    Sequence values must be contiguous and ordered. This internal API accepts
    only first indices 0 or 1; that choice does not define the wire convention.
    The function validates payload bytes only. A caller remains responsible for
    parsing and binding any outer start/end records and for bounding process I/O.
    """
    if (not isinstance(declared_chunk_count, int) or isinstance(declared_chunk_count, bool)
            or declared_chunk_count <= 0 or declared_chunk_count > MAX_RAW_PLAN_BYTES):
        raise PlanTransportError("invalid declared chunk count")
    if (not isinstance(declared_byte_length, int) or isinstance(declared_byte_length, bool)
            or not 0 < declared_byte_length <= MAX_RAW_PLAN_BYTES or declared_byte_length % 2):
        raise PlanTransportError("invalid declared plan byte length")
    if declared_chunk_count > declared_byte_length:
        raise PlanTransportError("chunk count cannot fit declared plan length")
    if not isinstance(server_sha256, str) or not _SHA256.fullmatch(server_sha256):
        raise PlanTransportError("invalid server checksum")

    iterator = iter(chunks)
    payload = bytearray()
    first_sequence: int | None = None
    for offset in range(declared_chunk_count):
        try:
            record = next(iterator)
        except StopIteration as exc:
            raise PlanTransportError("missing plan chunk") from exc
        if (not isinstance(record, tuple) or len(record) != 2
                or not isinstance(record[0], int) or isinstance(record[0], bool)
                or record[0] < 0 or not isinstance(record[1], str)):
            raise PlanTransportError("invalid plan chunk record")
        sequence, encoded = record
        if first_sequence is None:
            if sequence not in (0, 1):
                raise PlanTransportError("unsupported internal sequence start")
            first_sequence = sequence
        if sequence != first_sequence + offset:
            raise PlanTransportError("plan chunk sequence has a gap, duplicate, or reordering")
        if len(encoded) < 2 or len(encoded) > MAX_CHUNK_BYTES * 2 or len(encoded) % 2 or not _HEX.fullmatch(encoded):
            raise PlanTransportError("invalid plan chunk hex")
        chunk = bytes.fromhex(encoded)
        if len(chunk) > MAX_CHUNK_BYTES or len(payload) + len(chunk) > declared_byte_length:
            raise PlanTransportError("plan chunk exceeds declared length")
        payload.extend(chunk)

    try:
        next(iterator)
    except StopIteration:
        pass
    else:
        raise PlanTransportError("unexpected extra plan chunk")

    if len(payload) != declared_byte_length:
        raise PlanTransportError("truncated plan payload")
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if not hmac.compare_digest(actual_sha256, server_sha256.lower()):
        raise PlanTransportError("server checksum mismatch")
    try:
        text = payload.decode("utf-16-le", errors="strict")
    except UnicodeDecodeError as exc:
        raise PlanTransportError("invalid UTF-16 plan text") from exc
    if len(text.encode("utf-8", errors="strict")) > MAX_UTF8_PLAN_BYTES:
        raise PlanTransportError("decoded UTF-8 plan exceeds limit")
    return text
