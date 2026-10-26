"""Consumer and oracle counterexamples for DGN-004 decoded plan results."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dgn004_capture_result import PlanCaptureResultError, decode_plan_capture_result
from dgn004_plan_frame import encode_plan_frame


RUN = "capture-test-1"
XML = ('<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan">'
       '<BatchSequence><Batch><Statements><StmtSimple/></Statements></Batch></BatchSequence>'
       '</ShowPlanXML>')


def framed(xml_text: str) -> str:
    return encode_plan_frame(xml_text.encode("utf-16-le"), run=RUN, role="R", call=1)


class Dgn004CaptureResultTests(unittest.TestCase):
    def test_complete_showplan_document_returns_separate_invocation_binding(self) -> None:
        result = decode_plan_capture_result(
            framed(XML), expected_run=RUN, expected_role="R", expected_call=1
        )
        self.assertEqual((result.run, result.role, result.call), (RUN, "R", 1))
        self.assertEqual(result.xml_text, XML)
        self.assertEqual(result.root_tag, "{http://schemas.microsoft.com/sqlserver/2004/07/showplan}ShowPlanXML")

    def test_utf16_byte_order_mark_is_accepted(self) -> None:
        payload = b"\xff\xfe" + XML.encode("utf-16-le")
        frame = encode_plan_frame(payload, run=RUN, role="R", call=1)
        result = decode_plan_capture_result(
            frame, expected_run=RUN, expected_role="R", expected_call=1
        )
        self.assertTrue(result.xml_text.startswith("\ufeff"))
        self.assertEqual(result.root_tag, "{http://schemas.microsoft.com/sqlserver/2004/07/showplan}ShowPlanXML")

    def test_frame_binding_mismatch_is_rejected_before_result(self) -> None:
        with self.assertRaisesRegex(PlanCaptureResultError, "caller run/role/call binding"):
            decode_plan_capture_result(
                framed(XML), expected_run=RUN, expected_role="H", expected_call=1
            )

    def test_truncated_or_multiple_xml_documents_are_rejected(self) -> None:
        for value in (XML[:-12], XML + XML):
            with self.subTest(value=value[-30:]):
                with self.assertRaisesRegex(PlanCaptureResultError, "one complete XML document"):
                    decode_plan_capture_result(
                        framed(value), expected_run=RUN, expected_role="R", expected_call=1
                    )

    def test_non_showplan_root_is_rejected(self) -> None:
        invalid = "<root/>"
        with self.assertRaisesRegex(PlanCaptureResultError, "not SQL Server ShowPlanXML"):
            decode_plan_capture_result(
                framed(invalid), expected_run=RUN, expected_role="R", expected_call=1
            )

    def test_empty_showplan_root_is_only_shape_validation(self) -> None:
        # The helper checks XML well-formedness and root QName, not plan schema,
        # statement identity, runtime counters, or execution provenance.
        result = decode_plan_capture_result(
            framed('<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan"/>'),
            expected_run=RUN, expected_role="R", expected_call=1,
        )
        self.assertTrue(result.xml_text.endswith("/>"))

    def test_document_type_declarations_are_rejected(self) -> None:
        invalid = ('<!DOCTYPE ShowPlanXML [<!ENTITY x "expanded">]>'
                   '<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan">&x;</ShowPlanXML>')
        with self.assertRaisesRegex(PlanCaptureResultError, "document type declarations"):
            decode_plan_capture_result(
                framed(invalid), expected_run=RUN, expected_role="R", expected_call=1
            )


if __name__ == "__main__":
    unittest.main()
