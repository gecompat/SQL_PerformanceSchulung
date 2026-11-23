from __future__ import annotations

from pathlib import Path
import sys
import unittest
from xml.sax.saxutils import quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from idx010_query_evidence import (  # noqa: E402
    EXPECTED_RESULT,
    QUERY,
    QueryEvidenceMissing,
    SegmentCounts,
    verify_query_evidence,
)


PLAN = f"""<ShowPlanXML xmlns="http://schemas.microsoft.com/sqlserver/2004/07/showplan">
  <BatchSequence><Batch><Statements>
    <StmtSimple StatementText={quoteattr(QUERY + ";")}><QueryPlan>
      <RelOp PhysicalOp="Index Scan">
        <RunTimeInformation>
          <RunTimeCountersPerThread Thread="0" ActualRows="4096" ActualEndOfScans="1" ActualExecutions="1" />
        </RunTimeInformation>
        <IndexScan Ordered="false" Storage="ColumnStore">
          <Object Database="[Idx010_control]" Schema="[dbo]" Table="[Events]"
                  Index="[IX_Events]" IndexKind="NonClustered" />
        </IndexScan>
      </RelOp>
    </QueryPlan></StmtSimple>
  </Statements></Batch></BatchSequence>
</ShowPlanXML>"""
IO = "Table 'Events'. Scan count 0, logical reads 0, physical reads 0, Segment reads 1, segment skipped 3."


class QueryEvidenceTests(unittest.TestCase):
    def verify(self, plan=PLAN, messages=(IO,), result=(EXPECTED_RESULT,)):
        return verify_query_evidence(
            plan_xml=plan,
            info_messages=messages,
            result_rows=result,
            database_name="Idx010_control",
            index_name="IX_Events",
        )

    def test_accepts_single_executed_target_scan_and_segment_record(self):
        self.assertEqual(self.verify(), SegmentCounts(reads=1, skipped=3))
        self.assertEqual(
            self.verify(messages=("Table 'Events'. Segment reads 4, segment skipped 0.",)),
            SegmentCounts(reads=4, skipped=0),
        )

    def test_rejects_plan_from_wrong_statement_or_data_access(self):
        for original, replacement in (
            ("1048576", "1048577"),
            ("[Idx010_control]", "[Idx010_ordered]"),
            ("[IX_Events]", "[IX_Other]"),
            ('IndexKind="NonClustered"', 'IndexKind="Clustered"'),
            ('Storage="ColumnStore"', 'Storage="RowStore"'),
            ('Ordered="false"', 'Ordered="false" ForcedIndex="true"'),
        ):
            with self.subTest(original=original), self.assertRaises(QueryEvidenceMissing):
                self.verify(plan=PLAN.replace(original, replacement))

    def test_rejects_estimated_or_unexecuted_scan(self):
        for candidate in (
            PLAN.replace("ActualExecutions=\"1\"", "ActualExecutions=\"0\""),
            PLAN.replace("RunTimeInformation", "MissingRuntimeInformation"),
        ):
            with self.subTest(candidate=candidate), self.assertRaises(QueryEvidenceMissing):
                self.verify(plan=candidate)

    def test_rejects_multiple_statements_or_accesses(self):
        for candidate in (
            PLAN.replace("</Statements>", "<StmtSimple /></Statements>"),
            PLAN.replace("</IndexScan>", "<Object /></IndexScan>"),
        ):
            with self.subTest(candidate=candidate), self.assertRaises(QueryEvidenceMissing):
                self.verify(plan=candidate)

    def test_rejects_decoy_or_incomplete_segment_messages(self):
        for messages in (
            (),
            (IO, IO),
            (IO, "Table 'Events'. Scan count 1, logical reads 0."),
            (IO.replace("'Events'", "'Other'"),),
            (IO.replace("segment skipped 3", "segment skipped 2"),),
            (IO.replace("Segment reads 1", "Segment reads 0").replace("segment skipped 3", "segment skipped 4"),),
            (IO.replace("Segment reads 1", "Segment reads 1, Segment reads 1"),),
        ):
            with self.subTest(messages=messages), self.assertRaises(QueryEvidenceMissing):
                self.verify(messages=messages)

    def test_rejects_wrong_result_or_excess_rows(self):
        for result in ((), ((4095, 4303353856),), (EXPECTED_RESULT, EXPECTED_RESULT), ((4096.0, 4303353856),)):
            with self.subTest(result=result), self.assertRaises(QueryEvidenceMissing):
                self.verify(result=result)


if __name__ == "__main__":
    unittest.main()
