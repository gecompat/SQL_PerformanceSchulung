from __future__ import annotations

import json
from pathlib import Path
import sys
from unittest import TestCase, main

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from idx010_index_metadata import METADATA_LIMIT, decode_index_evidence, index_evidence_batch
from idx010_pilot_sequence import Arm, Target
from idx010_pilot_setup import INDEX_NAME, ROWGROUP_COUNT, ROWGROUP_ROWS


TARGET = Target("RUN8", Arm.ORDERED)
RECORD = {
    "database_name": TARGET.database_name,
    "index_name": INDEX_NAME,
    "order_ordinal": 1,
    "rowgroup_count": ROWGROUP_COUNT,
    "rowgroup_size": ROWGROUP_ROWS,
    "eligible_segments": ROWGROUP_COUNT,
    "overlapping_pairs": 2,
}


class IndexMetadataTests(TestCase):
    def test_catalog_batch_binds_segment_rowgroups_and_validates_all_endpoints(self):
        sql = index_evidence_batch(TARGET)
        for fragment in (
            "SQLPERF.PilotProfile",
            "i.type = 6",
            "ic.index_id = @IndexId",
            "p.data_compression_desc = N'COLUMNSTORE'",
            "AND p.internal_object_type = 4",
            "s.partition_id = @PartitionId AND s.column_id = @ColumnId",
            "s.encoding_type IN (1, 2)",
            "s.min_data_id >= 0 AND s.max_data_id < 4194304",
            "SELECT group_id FROM @Segments EXCEPT SELECT group_id FROM @Groups",
            "SELECT group_id FROM @Groups EXCEPT SELECT group_id FROM @Segments",
            "SELECT minimum AS endpoint FROM @Segments\n            UNION",
            "a.group_id < b.group_id",
            "a.minimum < b.maximum AND b.minimum < a.maximum",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, sql)
        self.assertLess(sql.index("FAIL_OWNERSHIP"), sql.index("FROM sys.indexes"))
        self.assertNotIn("minimum AS", sql[sql.rindex("SELECT DB_NAME()"):])

    def test_catalog_batch_requires_exact_two_column_projection_and_no_second_order_key(self):
        sql = index_evidence_batch(TARGET)
        for fragment in (
            "ic.is_included_column = 1 AND ic.key_ordinal = 0 AND ic.partition_ordinal = 0",
            "FROM @IndexColumns WHERE column_name = N'EventDayKey'",
            "FROM sys.index_columns WHERE object_id = @ObjectId AND index_id = @IndexId) <> 2",
            "FROM @IndexColumns) <> 2",
            "FROM @IndexColumns WHERE column_name = N'EventId' AND order_ordinal = 0",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, sql)
        self.assertLess(sql.index("index partition, columns or order differ"), sql.index("DECLARE @Groups"))


    def test_decodes_only_bounded_normalized_receipt(self):
        evidence = decode_index_evidence(json.dumps(RECORD).encode(), TARGET)
        self.assertEqual(evidence.overlapping_pairs, 2)
        self.assertEqual(evidence.rowgroup_sizes, (ROWGROUP_ROWS,) * ROWGROUP_COUNT)
        self.assertFalse(evidence.has_delta_or_deleted_rows)

    def test_rejects_foreign_identity_or_partial_coverage(self):
        for key, value in (
            ("database_name", Target("RUN8", Arm.CONTROL).database_name),
            ("index_name", "IX_Other"),
            ("order_ordinal", 0),
            ("order_ordinal", True),
            ("rowgroup_count", 3),
            ("rowgroup_size", ROWGROUP_ROWS - 1),
            ("eligible_segments", 3),
            ("overlapping_pairs", 7),
            ("overlapping_pairs", False),
        ):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                decode_index_evidence(json.dumps(RECORD | {key: value}).encode(), TARGET)

    def test_rejects_duplicate_unexpected_or_unbounded_payloads(self):
        valid = json.dumps(RECORD).encode()
        for payload in (
            b"",
            valid + valid,
            b'{"overlapping_pairs": 1,' + valid[1:],
            json.dumps(RECORD | {"min_data_id": 100}).encode(),
            b" " * METADATA_LIMIT + valid,
        ):
            with self.subTest(payload=payload[:40]), self.assertRaises(ValueError):
                decode_index_evidence(payload, TARGET)


if __name__ == "__main__":
    main()
