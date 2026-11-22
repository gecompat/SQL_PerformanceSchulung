"""Static contract checks for the bounded DGN-004 fixture setup."""
from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Tests" / "Fixtures" / "DGN004_SourcePair" / "SetupSchemaAndData.sql"
EXPECTED_TABLES = (
    "Orders", "OrderLines", "Customers", "Categories", "Contacts",
    "Cities", "Regions", "Countries", "Items", "ItemGroups",
)
EXPECTED_INDEXES = (
    "IX_DGN004_Orders_CustomerId",
    "IX_DGN004_Orders_ContactId",
    "IX_DGN004_OrderLines_OrderId",
    "IX_DGN004_OrderLines_ItemId",
    "IX_DGN004_Customers_CategoryId",
    "IX_DGN004_Customers_CityId",
    "IX_DGN004_Cities_RegionId",
    "IX_DGN004_Regions_CountryId",
    "IX_DGN004_ItemGroups_ItemId_GroupNo",
)
EXPECTED_ROWS = {
    "Orders": 96,
    "OrderLines": 192,
    "Customers": 48,
    "Categories": 4,
    "Contacts": 24,
    "Cities": 12,
    "Regions": 6,
    "Countries": 3,
    "Items": 48,
    "ItemGroups": 96,
}


class Dgn004SetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = SOURCE.read_text(encoding="ascii")

    def test_exact_ten_tables_and_nine_secondary_indexes(self) -> None:
        tables = re.findall(r"(?im)^CREATE\s+TABLE\s+dgn004\.([A-Za-z0-9_]+)\b", self.sql)
        indexes = re.findall(
            r"(?im)^CREATE\s+NONCLUSTERED\s+INDEX\s+([A-Za-z0-9_]+)\s+ON\s+dgn004\.",
            self.sql,
        )
        self.assertEqual(EXPECTED_TABLES, tuple(tables))
        self.assertEqual(EXPECTED_INDEXES, tuple(indexes))
        self.assertNotRegex(self.sql, r"(?i)\b(?:DROP|TRUNCATE)\s+(?:DATABASE|TABLE|INDEX)\b")
        self.assertIn("<> 529", self.sql)
        self.assertIn("<> 10", self.sql)
        self.assertIn("<> 9", self.sql)

    def test_closed_recursive_generators_match_registered_row_counts(self) -> None:
        pairs = re.findall(
            r"(?is)WITH\s+N\s+AS\s*\(\s*SELECT\s+CONVERT\(int,\s*1\)\s+AS\s+Id"
            r"\s+UNION\s+ALL\s+SELECT\s+Id\s*\+\s*1\s+FROM\s+N\s+WHERE\s+Id\s*<\s*(\d+)"
            r"\s*\)\s*INSERT\s+dgn004\.([A-Za-z0-9_]+)",
            self.sql,
        )
        self.assertEqual(
            tuple((str(count), table) for table, count in EXPECTED_ROWS.items()),
            tuple((count, table) for count, table in pairs),
        )
        self.assertEqual(529, sum(int(count) for count in EXPECTED_ROWS.values()))

    def test_four_exact_ownership_markers_are_required_before_schema_change(self) -> None:
        guards = self.sql.index("IF (SELECT COUNT(*) FROM sys.extended_properties")
        schema_check = self.sql.index("IF SCHEMA_ID(N'dgn004') IS NOT NULL")
        create_schema = self.sql.index("CREATE SCHEMA dgn004 AUTHORIZATION dbo")
        self.assertLess(guards, schema_check)
        self.assertLess(schema_check, create_schema)
        for marker in (
            "SQLPERF.Project", "SQLPERF.ContractVersion", "SQLPERF.DemoId", "SQLPERF.RunToken",
        ):
            self.assertIn(marker, self.sql)
        self.assertIn("THROW 51020", self.sql)
        self.assertIn("THROW 51021", self.sql)


if __name__ == "__main__":
    unittest.main()
