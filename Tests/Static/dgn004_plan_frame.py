"""Pure parser for the bounded DGN-004 plan-frame text format."""
from __future__ import annotations

import hashlib
import re

from dgn004_plan_transport import (
    MAX_CHUNK_BYTES,
    MAX_RAW_PLAN_BYTES,
    MAX_UTF8_PLAN_BYTES,
    PlanTransportError,
    decode_plan_chunks,
)


MAX_FRAME_TEXT_BYTES = 2 * 1024 * 1024
MAX_RUN_FIELD_CHARS = 64
_DECIMAL = re.compile(r"\A(?:0|[1-9][0-9]*)\Z")
_SHA256 = re.compile(r"\A[0-9A-Fa-f]{64}\Z")


class PlanFrameError(ValueError):
    """Reject malformed, misbound, or incomplete frame records."""


def encode_plan_frame(raw_plan_bytes: bytes, *, run: str, role: str, call: int) -> str:
    """Serialize captured UTF-16 plan bytes in the fixed DGN-004 frame format.

    Run/role/call are labels supplied by the caller. They do not establish
    query, plan, or engine identity.
    """
    if not isinstance(raw_plan_bytes, bytes):
        raise PlanFrameError("plan payload must be bytes")
    if not isinstance(run, str) or not run or len(run) > MAX_RUN_FIELD_CHARS:
        raise PlanFrameError("invalid caller run binding")
    if not run.isascii() or any(char in run for char in "|\r\n"):
        raise PlanFrameError("invalid caller run binding")
    if role not in ("R", "H"):
        raise PlanFrameError("invalid caller role binding")
    if not isinstance(call, int) or isinstance(call, bool) or not 1 <= call <= 9:
        raise PlanFrameError("invalid caller call binding")
    if not 0 < len(raw_plan_bytes) <= MAX_RAW_PLAN_BYTES or len(raw_plan_bytes) % 2:
        raise PlanFrameError("plan payload is empty, oversized, or odd-length")
    try:
        decoded = raw_plan_bytes.decode("utf-16-le", errors="strict")
    except UnicodeDecodeError as exc:
        raise PlanFrameError("plan payload is not strict UTF-16LE") from exc
    if len(decoded.encode("utf-8", errors="strict")) > MAX_UTF8_PLAN_BYTES:
        raise PlanFrameError("decoded UTF-8 plan exceeds limit")

    chunk_count = (len(raw_plan_bytes) + MAX_CHUNK_BYTES - 1) // MAX_CHUNK_BYTES
    checksum = hashlib.sha256(raw_plan_bytes).hexdigest()
    common = f"{run}|{role}|{call}|{len(raw_plan_bytes)}|{chunk_count}|{checksum}"
    records = [f"DGN004_PLAN_START|{common}"]
    for sequence, offset in enumerate(range(0, len(raw_plan_bytes), MAX_CHUNK_BYTES), start=1):
        chunk = raw_plan_bytes[offset:offset + MAX_CHUNK_BYTES]
        records.append(f"DGN004_PLAN_CHUNK|{sequence}|{chunk.hex()}")
    records.append(f"DGN004_PLAN_END|{common}")
    frame = "\n".join(records)
    if len(frame) > MAX_FRAME_TEXT_BYTES:
        raise PlanFrameError("frame text exceeds the planned stdout ceiling")
    return frame


def decode_plan_frame(
    frame_text: str,
    *,
    expected_run: str,
    expected_role: str,
    expected_call: int,
) -> str:
    """Parse exact Start/Chunk/End records and pass bytes to the pure decoder.

    The caller supplies the expected run/role/call binding independently from
    the frame. This text format associates bytes with that invocation; it does
    not attest query, plan, or engine identity.
    """
    if (not isinstance(frame_text, str) or not isinstance(expected_run, str)
            or not expected_run or len(expected_run) > MAX_RUN_FIELD_CHARS or not expected_run.isascii()
            or any(char in expected_run for char in "|\r\n")):
        raise PlanFrameError("invalid caller run binding")
    if expected_role not in ("R", "H"):
        raise PlanFrameError("invalid caller role binding")
    if not isinstance(expected_call, int) or isinstance(expected_call, bool) or not 1 <= expected_call <= 9:
        raise PlanFrameError("invalid caller call binding")
    # For ASCII strings, character count equals encoded byte count. Reject
    # before creating a second copy of an oversized input.
    if len(frame_text) > MAX_FRAME_TEXT_BYTES:
        raise PlanFrameError("frame text exceeds the planned stdout ceiling")
    if not frame_text.isascii():
        raise PlanFrameError("frame text is not ASCII")

    lines = frame_text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    normalized: list[str] = []
    for index, line in enumerate(lines):
        if line.endswith("\r"):
            if index == len(lines) - 1 and not frame_text.endswith("\n"):
                raise PlanFrameError("bare carriage return at end of frame")
            line = line[:-1]
        if not line or "\r" in line:
            raise PlanFrameError("empty line or unsupported line break in frame")
        normalized.append(line)
    if len(normalized) < 3:
        raise PlanFrameError("incomplete plan frame")

    start = normalized[0].split("|")
    end = normalized[-1].split("|")
    if len(start) != 7 or start[0] != "DGN004_PLAN_START":
        raise PlanFrameError("invalid start record")
    if len(end) != 7 or end[0] != "DGN004_PLAN_END":
        raise PlanFrameError("invalid end record")
    run, role = start[1], start[2]
    if not run or len(run) > MAX_RUN_FIELD_CHARS:
        raise PlanFrameError("invalid frame run field")
    call = _parse_decimal(start[3], "call")
    byte_length = _parse_decimal(start[4], "byte length")
    chunk_count = _parse_decimal(start[5], "chunk count")
    checksum = start[6]
    if (run != expected_run or role != expected_role or call != expected_call
            or role not in ("R", "H")):
        raise PlanFrameError("frame does not match caller run/role/call binding")
    if (not 0 < byte_length <= MAX_RAW_PLAN_BYTES or byte_length % 2
            or chunk_count != (byte_length + MAX_CHUNK_BYTES - 1) // MAX_CHUNK_BYTES):
        raise PlanFrameError("declared plan byte/chunk limits do not match")
    if not _SHA256.fullmatch(checksum):
        raise PlanFrameError("invalid start checksum")
    expected_end = ["DGN004_PLAN_END", run, role, str(call), str(byte_length), str(chunk_count), checksum]
    if end != expected_end:
        raise PlanFrameError("end record differs from start binding")
    if len(normalized) != chunk_count + 2:
        raise PlanFrameError("plan frame has missing or extra records")

    chunks: list[tuple[int, str]] = []
    remaining = byte_length
    for sequence, line in enumerate(normalized[1:-1], start=1):
        fields = line.split("|")
        if len(fields) != 3 or fields[0] != "DGN004_PLAN_CHUNK":
            raise PlanFrameError("invalid plan chunk record")
        if _parse_decimal(fields[1], "chunk sequence") != sequence:
            raise PlanFrameError("chunk sequence is missing, duplicate, or reordered")
        expected_bytes = min(MAX_CHUNK_BYTES, remaining)
        payload = fields[2]
        if len(payload) != expected_bytes * 2:
            raise PlanFrameError("chunk byte length is truncated or oversized")
        chunks.append((sequence, payload))
        remaining -= expected_bytes
    if remaining != 0:
        raise PlanFrameError("plan frame byte count is incomplete")
    try:
        return decode_plan_chunks(
            chunks,
            declared_chunk_count=chunk_count,
            declared_byte_length=byte_length,
            server_sha256=checksum,
        )
    except PlanTransportError as exc:
        raise PlanFrameError(str(exc)) from exc


def _parse_decimal(value: str, label: str) -> int:
    if not _DECIMAL.fullmatch(value):
        raise PlanFrameError(f"invalid {label}")
    try:
        return int(value)
    except ValueError as exc:
        raise PlanFrameError(f"invalid {label}") from exc
