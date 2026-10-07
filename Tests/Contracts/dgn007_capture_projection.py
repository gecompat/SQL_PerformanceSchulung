"""Reiner Packager der begrenzten skalaren DGN-007-SQL-Projektion.

Wire v1: DGN007_CAPTURE_FRAME|1|ordinal|total_frames|total_payload_chars|chunk.
SQL emittiert neun gemessene Bodyfelder als druckbaren ASCII-JSON-Text.
Nur schema/contract_digest/source_digest kommen vom erwarteten Vertrag.
Der tatsächliche Decoder prüft danach den vollständigen Body; dieser Weg
attestiert weder Herkunft noch Vorabfreeze, Ressourcen, Phasen oder Cleanup.
"""
from __future__ import annotations

import re

from Tests.Contracts.dgn007_collector_transport import (
    CaptureBody, SCHEMA, TransportError, decode_capture,
)
from Tests.Contracts.dgn007_prospective_acceptance import AcceptanceContract, _contract_valid

FRAME_PREFIX = "DGN007_CAPTURE_FRAME|"
FRAME_VERSION = "1"
MAX_CHUNK_CHARS = 512
MAX_PROJECTION_CHARS = 32000
MAX_FRAMES = 64
MAX_FRAME_CHARS = MAX_CHUNK_CHARS + 64
_UNSIGNED = re.compile(r"[1-9][0-9]{0,4}")


class ProjectionError(ValueError):
    """Feste öffentliche Codes ohne Rohdaten oder Exceptioncontext."""

    def __init__(self, code: str = "FAIL_CONTRACT"):
        self.code = code if code in ("FAIL_CONTRACT", "FAIL_RESULT_CONTRACT") else "FAIL_CONTRACT"
        super().__init__(self.code)


def _projection(frames: tuple[str, ...]) -> str:
    if type(frames) is not tuple or not 1 <= len(frames) <= MAX_FRAMES:
        raise ProjectionError()
    chunks: list[str] = []
    expected_length = None
    for ordinal, frame in enumerate(frames, 1):
        if (type(frame) is not str or len(frame) > MAX_FRAME_CHARS
                or any(not 32 <= ord(char) <= 126 for char in frame)):
            raise ProjectionError()
        parts = frame.split("|", 5)
        if (len(parts) != 6 or parts[0] != "DGN007_CAPTURE_FRAME" or parts[1] != FRAME_VERSION
                or any(_UNSIGNED.fullmatch(value) is None for value in parts[2:5])):
            raise ProjectionError()
        index, total, length = (int(value) for value in parts[2:5])
        if (index != ordinal or total != len(frames) or not 1 <= length <= MAX_PROJECTION_CHARS
                or total != (length + MAX_CHUNK_CHARS - 1) // MAX_CHUNK_CHARS
                or (expected_length is not None and length != expected_length)):
            raise ProjectionError()
        expected_length = length
        required = MAX_CHUNK_CHARS if ordinal < total else length - MAX_CHUNK_CHARS * (total - 1)
        if len(parts[5]) != required:
            raise ProjectionError()
        chunks.append(parts[5])
    projection = "".join(chunks)
    if (len(projection) != expected_length or not projection.startswith("{")
            or not projection.endswith("}")):
        raise ProjectionError()
    return projection


def decode_projection(frames: tuple[str, ...], expected_contract: AcceptanceContract) -> CaptureBody:
    """Frameprüfung, externe Metadaten ergänzen, anschließend tatsächlicher Decoder.

    JSON wird nicht vorab geparst oder normalisiert: Duplikate, unbekannte
    Felder, zusätzliche Payloads und numerische Fehler bleiben sichtbar.
    Keine fehlenden Messwerte oder anderen Laufdaten werden ergänzt.
    """
    failure = None
    body = None
    try:
        if not _contract_valid(expected_contract):
            raise ProjectionError()
        projection = _projection(frames)
        # Geprüfte Digests und SCHEMA sind ausschließlich feste ASCII-Tokens.
        envelope = ('{"schema":"' + SCHEMA + '","contract_digest":"'
                    + expected_contract.contract_digest + '","source_digest":"'
                    + expected_contract.source_digest + '",' + projection[1:])
        body = decode_capture(envelope, expected_contract)
        if not body.row_evidence_complete:
            raise ProjectionError("FAIL_RESULT_CONTRACT")
    except (ProjectionError, TransportError) as error:
        failure = error.code
    except Exception:
        failure = "FAIL_CONTRACT"
    # Außerhalb des except-Blocks: keine Rohdaten in cause/context verketten.
    if failure is not None:
        raise ProjectionError(failure)
    return body
