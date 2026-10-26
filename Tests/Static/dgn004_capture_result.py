"""Invocation-bound decoding and XML well-formedness for DGN-004 frames.

This module validates payload shape only. It does not query SQL Server or
establish query, plan, execution, or engine identity.
"""
from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET

from dgn004_plan_frame import PlanFrameError, decode_plan_frame


SHOWPLAN_ROOT = "{http://schemas.microsoft.com/sqlserver/2004/07/showplan}ShowPlanXML"


class PlanCaptureResultError(ValueError):
    """Reject a framed payload that is not a complete Showplan XML document."""


@dataclass(frozen=True)
class DecodedPlanCapture:
    """Decoded XML associated with caller-supplied run/role/call labels only."""

    run: str
    role: str
    call: int
    xml_text: str
    root_tag: str


def decode_plan_capture_result(
    frame_text: str,
    *,
    expected_run: str,
    expected_role: str,
    expected_call: int,
) -> DecodedPlanCapture:
    """Decode the exact frame, parse its whole XML document, and bind labels.

    Binding is only to values independently supplied by the caller. This does
    not prove the SQL statement, plan, query, or engine that produced the bytes.
    """
    try:
        xml_text = decode_plan_frame(
            frame_text,
            expected_run=expected_run,
            expected_role=expected_role,
            expected_call=expected_call,
        )
    except PlanFrameError as exc:
        raise PlanCaptureResultError(str(exc)) from exc
    if "<!DOCTYPE" in xml_text:
        raise PlanCaptureResultError("document type declarations are not accepted")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise PlanCaptureResultError("payload is not one complete XML document") from exc
    if root.tag != SHOWPLAN_ROOT:
        raise PlanCaptureResultError("XML root is not SQL Server ShowPlanXML")
    return DecodedPlanCapture(
        run=expected_run,
        role=expected_role,
        call=expected_call,
        xml_text=xml_text,
        root_tag=root.tag,
    )
