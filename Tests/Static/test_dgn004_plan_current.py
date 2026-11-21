"""Synthetic counterexamples for DGN-004 actual-plan identity binding."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "Tests" / "Static"
if str(STATIC) not in sys.path:
    sys.path.insert(0, str(STATIC))

from dgn004_identity_snapshot import registered_text_views  # noqa: E402
from dgn004_plan_current import (  # noqa: E402
    CurrentPlanError,
    PLAN_NAMESPACE,
    TABLES,
    inspect_current_form_a_plan,
)


DB = "SQLPERF_LAB_DGN004_TEST123456"
NS = "http://schemas.microsoft.com/sqlserver/2004/07/showplan"


def showplan(role: str = "R", *, text: str | None = None, use_plan: str | None = "true",
             database: str = DB, omit_table: str | None = None, joins: int = 9,
             concat: int = 1, statements: int = 1) -> str:
    views = registered_text_views()[role]
    root = ET.Element(f"{{{NS}}}ShowPlanXML")
    batch = ET.SubElement(root, f"{{{NS}}}BatchSequence")
    batch_stmt = ET.SubElement(batch, f"{{{NS}}}Batch")
    for _ in range(statements):
        statements_node = ET.SubElement(batch_stmt, f"{{{NS}}}Statements")
        attrs = {"StatementText": text if text is not None else views.statement_text}
        if use_plan is not None:
            attrs["UsePlan"] = use_plan
        stmt = ET.SubElement(statements_node, f"{{{NS}}}StmtSimple", attrs)
        query_plan = ET.SubElement(stmt, f"{{{NS}}}QueryPlan")
    for name in sorted(TABLES):
        if name == omit_table:
            continue
        ET.SubElement(query_plan, f"{{{NS}}}Object", {
            "Database": f"[{database}]", "Schema": "[dgn004]", "Table": f"[{name}]",
        })
    for _ in range(joins):
        ET.SubElement(query_plan, f"{{{NS}}}RelOp", {"LogicalOp": "Inner Join", "PhysicalOp": "Hash Match"})
    for _ in range(concat):
        ET.SubElement(query_plan, f"{{{NS}}}RelOp", {"LogicalOp": "Concatenation", "PhysicalOp": "Concatenation"})
    return ET.tostring(root, encoding="unicode")


class Dgn004CurrentPlanTests(unittest.TestCase):
    def test_complete_registered_form_a_actual_plan_passes(self):
        result = inspect_current_form_a_plan(showplan("H"), role="H", database_name=DB)
        self.assertEqual("H", result.role)
        self.assertTrue(result.use_plan)
        self.assertEqual(TABLES, result.table_names)
        self.assertEqual(9, result.join_count)
        self.assertEqual(1, result.concatenation_count)

    def test_stale_or_wrong_statement_and_database_fail(self):
        views = registered_text_views()["R"]
        invalid = (
            showplan(text=views.statement_text.replace("OrderId", "OtherId", 1)),
            showplan(database="FOREIGN_DB"),
        )
        for plan in invalid:
            with self.subTest(plan=plan[:80]), self.assertRaises(CurrentPlanError):
                inspect_current_form_a_plan(plan, role="R", database_name=DB)

    def test_showplan_statement_whitespace_is_normalized_without_changing_tokens(self):
        views = registered_text_views()["R"]
        spaced = "  \n" + views.statement_text.replace(" FROM ", "\nFROM\n") + "  "
        result = inspect_current_form_a_plan(showplan(text=spaced), role="R", database_name=DB)
        self.assertEqual(result.role, "R")
        with self.assertRaises(CurrentPlanError):
            inspect_current_form_a_plan(
                showplan(text=views.statement_text.replace("OrderId", "OtherId", 1)),
                role="R", database_name=DB,
            )

    def test_showplan_parameter_declaration_prefix_is_removed_before_source_binding(self):
        views = registered_text_views()["R"]
        result = inspect_current_form_a_plan(
            showplan(text="(@p0 int, @p1 bigint) " + views.statement_text),
            role="R", database_name=DB,
        )
        self.assertEqual(result.role, "R")

    def test_showplan_may_report_the_registered_module_batch_as_statement_text(self):
        views = registered_text_views()["R"]
        result = inspect_current_form_a_plan(
            showplan(text=views.module_text.rstrip("\r\n")[:-1]), role="R", database_name=DB
        )
        self.assertEqual(result.role, "R")

    def test_missing_hint_useplan_object_or_form_a_shape_fail(self):
        invalid = (
            showplan(use_plan="false"),
            showplan(omit_table="Countries"),
            showplan(joins=8),
            showplan(concat=0),
            showplan(statements=2),
        )
        for plan in invalid:
            with self.subTest(plan=plan[:80]), self.assertRaises(CurrentPlanError):
                inspect_current_form_a_plan(plan, role="R", database_name=DB)

    def test_unforced_actual_plan_must_not_claim_useplan(self):
        plan_without_marker = inspect_current_form_a_plan(
            showplan(use_plan=None), role="R", database_name=DB, expected_use_plan=False
        )
        self.assertFalse(plan_without_marker.use_plan)
        with self.assertRaisesRegex(CurrentPlanError, "unexpectedly"):
            inspect_current_form_a_plan(
                showplan(), role="R", database_name=DB, expected_use_plan=False
            )

    def test_invalid_role_or_malformed_xml_fails(self):
        for plan, role in (("<bad", "R"), (showplan(), "X")):
            with self.subTest(role=role), self.assertRaises(CurrentPlanError):
                inspect_current_form_a_plan(plan, role=role, database_name=DB)


if __name__ == "__main__":
    unittest.main()
