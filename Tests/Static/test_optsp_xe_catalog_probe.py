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
IF COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion')), N'') <> N'17.0.5065.9'
    THROW 51003, 'SKIP_VERSION', 1;
SELECT name, value FROM sys.database_scoped_configurations
WHERE name IN (N'OPTIMIZED_SP_EXECUTESQL', N'ASYNC_STATS_UPDATE_WAIT_AT_LOW_PRIORITY');
SELECT is_auto_create_stats_on, is_auto_update_stats_on, is_auto_update_stats_async_on
FROM sys.databases WHERE database_id = DB_ID();
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
SELECT field_map.map_key FROM sys.dm_xe_map_values AS field_map
JOIN sys.dm_xe_object_columns AS event_column
ON field_map.object_package_guid = event_column.type_package_guid AND field_map.name = event_column.type_name
JOIN sys.dm_xe_objects AS event_object ON event_column.object_package_guid = event_object.package_guid
JOIN sys.dm_xe_packages AS event_package ON event_package.guid = event_object.package_guid
WHERE (event_package.name = N'sqlserver' AND event_object.name = N'compile_synchronization'
AND event_column.name IN (N'query_type', N'step'))
OR (event_package.name = N'sqlos' AND event_object.name = N'wait_info' AND event_column.name = N'opcode');
SELECT name FROM sys.dm_xe_objects WHERE name IN (N'lock_acquired', N'lock_released');
-- candidate fields: sql_text session_id database_id query_hash query_plan_hash
"""
BASE_WORKFLOW = """
image: mcr.microsoft.com/mssql/server@sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9
run: cat Tests/Runtime/optsp_xe_catalog_probe.sql | docker exec -i -h -1 -y 8000 -w 8000
- name: cleanup
  if: always()
  run: bash Tests/Runtime/cleanup_ci_container.sh
"""


class OptSpXeCatalogProbeTests(unittest.TestCase):
    def test_read_only_sql_server_2025_metadata_probe_is_accepted(self) -> None:
        self.assertEqual(validate(BASE_SQL, BASE_WORKFLOW), [])

    def test_database_settings_must_use_the_current_context_and_include_async_statistics(self):
        for unbound in (
            BASE_SQL.replace("WHERE database_id = DB_ID()", "WHERE database_id = 1"),
            BASE_SQL.replace("is_auto_update_stats_async_on", "0"),
        ):
            self.assertTrue(any("settings in the current database" in item for item in validate(unbound, BASE_WORKFLOW)))


    def test_wrong_wait_package_and_unbound_map_are_rejected(self) -> None:
        wrong_event = BASE_SQL.replace("N'sqlos' AND event_object.name", "N'sqlserver' AND event_object.name")
        unbound_map = wrong_event.replace("package.guid = wait_map.object_package_guid", "1=1")
        findings = validate(unbound_map, BASE_WORKFLOW)
        self.assertTrue(any("wait_info from the sqlos package" in finding for finding in findings))
        self.assertTrue(any("package GUID" in finding for finding in findings))

    def test_field_maps_without_the_type_package_guid_are_rejected(self) -> None:
        unbound = BASE_SQL.replace("field_map.object_package_guid = event_column.type_package_guid AND ", "")
        self.assertTrue(any("event and type packages" in finding for finding in validate(unbound, BASE_WORKFLOW)))

    def test_different_engine_build_is_rejected(self) -> None:
        wrong_build = BASE_SQL.replace("17.0.5065.9", "17.0.5035.5")
        self.assertTrue(any("exact engine build" in finding for finding in validate(wrong_build, BASE_WORKFLOW)))

    def test_mutation_or_unbounded_host_access_is_rejected(self) -> None:
        mutating_sql = BASE_SQL.replace("SELECT JSON_QUERY", "ALTER DATABASE x; SELECT JSON_QUERY")
        unsafe_workflow = BASE_WORKFLOW.replace("@sha256:", " --publish 1433:1433 @sha256:")
        findings = validate(mutating_sql, unsafe_workflow)
        self.assertTrue(any("read-only" in finding for finding in findings))
        self.assertTrue(any("publish" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
