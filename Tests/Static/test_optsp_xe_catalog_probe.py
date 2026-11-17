from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Static"))
from validate_optsp_xe_catalog_probe import validate  # noqa: E402


BASE_SQL = """
DECLARE @ProductMajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
IF @ProductMajorVersion <> 17 THROW 51000, 'SKIP_VERSION', 1;
SELECT JSON_QUERY((SELECT name FROM sys.dm_xe_objects
JOIN sys.dm_xe_object_columns ON 1=1
JOIN sys.dm_xe_packages ON 1=1 FOR JSON PATH))
FROM sys.dm_xe_objects;
-- candidate fields: sql_text session_id database_id query_hash query_plan_hash
"""
BASE_WORKFLOW = """
image: mcr.microsoft.com/mssql/server:2025-latest
run: cat Tests/Runtime/optsp_xe_catalog_probe.sql | docker exec -i -h -1 -y 65535 -w 65535
- name: cleanup
  if: always()
  run: bash Tests/Runtime/cleanup_ci_container.sh
"""


class OptSpXeCatalogProbeTests(unittest.TestCase):
    def test_read_only_sql_server_2025_metadata_probe_is_accepted(self) -> None:
        self.assertEqual(validate(BASE_SQL, BASE_WORKFLOW), [])

    def test_mutation_or_unbounded_host_access_is_rejected(self) -> None:
        mutating_sql = BASE_SQL.replace("SELECT JSON_QUERY", "ALTER DATABASE x; SELECT JSON_QUERY")
        unsafe_workflow = BASE_WORKFLOW.replace("2025-latest", "2025-latest --publish 1433:1433")
        findings = validate(mutating_sql, unsafe_workflow)
        self.assertTrue(any("read-only" in finding for finding in findings))
        self.assertTrue(any("publish" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
