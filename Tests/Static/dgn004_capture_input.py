"""Lexically safe sqlcmd variables for the DGN-004 frame transport fragment."""
from __future__ import annotations

from dataclasses import dataclass
import re

from dgn004_plan_frame import is_valid_run_token


_HANDLE_HEX = re.compile(r"\A[0-9A-Fa-f]{128}\Z")


class CaptureInputError(ValueError):
    """Reject unsafe or malformed values before sqlcmd variable expansion."""


@dataclass(frozen=True)
class CaptureInput:
    """Caller-provided labels and already-bound plan handle; no identity proof."""

    run: str
    role: str
    call: int
    plan_handle_hex: str


def build_sqlcmd_variables(value: CaptureInput) -> dict[str, str]:
    """Validate the exact interpolation alphabet before producing `-v` data.

    This is injection/truncation prevention only. It does not establish that
    the plan handle belongs to the expected module, query, or execution.
    """
    if type(value) is not CaptureInput:
        raise CaptureInputError("exact CaptureInput value required")
    if type(value.run) is not str or not is_valid_run_token(value.run):
        raise CaptureInputError("invalid run token")
    if type(value.role) is not str or value.role not in ("R", "H"):
        raise CaptureInputError("invalid role")
    if type(value.call) is not int or not 1 <= value.call <= 9:
        raise CaptureInputError("invalid call")
    if type(value.plan_handle_hex) is not str or not _HANDLE_HEX.fullmatch(value.plan_handle_hex):
        raise CaptureInputError("plan handle must be exactly 128 hexadecimal characters")
    return {
        "DGN004_RUN": value.run,
        "DGN004_ROLE": value.role,
        "DGN004_CALL": str(value.call),
        "DGN004_PLAN_HANDLE": value.plan_handle_hex.upper(),
    }
