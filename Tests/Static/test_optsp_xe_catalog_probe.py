from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Static"))
from validate_optsp_xe_catalog_probe import validate  # noqa: E402


BASE_SQL = """
DECLARE @ProductMajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
IF @ProductMajorVersion IS NULL OR @ProductMajorVersion <> 17 THROW 51000, 'SKIP_VERSION', 1;
SELECT JSON_QUERY((SELECT name FROM sys.dm_xe_objects
JOIN sys.dm_xe_object_columns ON 1=1
JOIN sys.dm_xe_packages ON 1=1 FOR JSON PATH))
FROM sys.dm_xe_objects AS event_object
JOIN sys.dm_xe_packages AS package ON package.guid = event_object.package_guid
WHERE package.name = N'sqlos' AND event_object.name = N'wait_info';
SELECT wait_map.map_key FROM sys.dm_xe_map_values AS wait_map
JOIN sys.dm_xe_packages AS package ON package.guid = wait_map.object_package_guid
WHERE package.name = N'sqlos'
  AND wait_map.name = N'wait_types'
  AND wait_map.map_value = N'LCK_M_X';
-- candidate fields: sql_text session_id database_id query_hash query_plan_hash
"""
BASE_WORKFLOW = """
image: mcr.microsoft.com/mssql/server:2025-latest
run: cat Tests/Runtime/optsp_xe_catalog_probe.sql | docker exec -i -h -1 -y 8000 -w 8000
- name: cleanup
  if: always()
  run: bash Tests/Runtime/cleanup_ci_container.sh
"""


class OptSpXeCatalogProbeTests(unittest.TestCase):
    def test_read_only_sql_server_2025_metadata_probe_is_accepted(self) -> None:
        self.assertEqual(validate(BASE_SQL, BASE_WORKFLOW), [])

    def test_wrong_wait_package_and_unbound_map_are_rejected(self) -> None:
        wrong_event = BASE_SQL.replace("N'sqlos' AND event_object.name", "N'sqlserver' AND event_object.name")
        unbound_map = wrong_event.replace("package.guid = wait_map.object_package_guid", "1=1")
        findings = validate(unbound_map, BASE_WORKFLOW)
        self.assertTrue(any("wait_info from the sqlos package" in finding for finding in findings))
        self.assertTrue(any("package GUID" in finding for finding in findings))

    def test_mutation_or_unbounded_host_access_is_rejected(self) -> None:
        mutating_sql = BASE_SQL.replace("SELECT JSON_QUERY", "ALTER DATABASE x; SELECT JSON_QUERY")
        unsafe_workflow = BASE_WORKFLOW.replace("2025-latest", "2025-latest --publish 1433:1433")
        findings = validate(mutating_sql, unsafe_workflow)
        self.assertTrue(any("read-only" in finding for finding in findings))
        self.assertTrue(any("publish" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
