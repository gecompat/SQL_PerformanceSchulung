from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_cleanup import drop_pilot_database_batch, drop_pilot_logins_batch
from external_tables_pilot_sql import Role
from external_tables_principals import Principal


TOKEN = "TEST0005"
READER_SID = bytes.fromhex("1a" * 16)
OBSERVER_SID = bytes.fromhex("2b" * 16)


class CleanupContractTests(unittest.TestCase):
    def test_query_drops_dependencies_in_order_after_marker_and_session_checks(self):
        sql = drop_pilot_database_batch(TOKEN, Role.QUERY)
        sequence = (
            "FAIL_OWNERSHIP", "FROM sys.dm_exec_sessions", "BEGIN TRANSACTION",
            "DROP EXTERNAL TABLE dbo.FactsPush", "DROP EXTERNAL TABLE dbo.FactsLocalFilter",
            "DROP EXTERNAL DATA SOURCE [PilotPush]", "DROP EXTERNAL DATA SOURCE [PilotLocalFilter]",
            "DROP DATABASE SCOPED CREDENTIAL [PilotSourceReader]",
            "DROP MASTER KEY", "COMMIT", "USE [master]", "DROP DATABASE [SQLPERF_LAB_EXT_TEST0005_QUERY]",
        )
        positions = [sql.index(part) for part in sequence]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("IF DB_ID(N'SQLPERF_LAB_EXT_TEST0005_QUERY') IS NOT NULL", sql)
        self.assertNotIn("SINGLE_USER", sql)
        self.assertNotIn("KILL ", sql)

    def test_source_only_targets_its_marked_database(self):
        sql = drop_pilot_database_batch(TOKEN, Role.SOURCE)
        self.assertIn("EXTERNAL_TABLES_SOURCE", sql)
        self.assertIn("DROP DATABASE [SQLPERF_LAB_EXT_TEST0005_SOURCE]", sql)
        self.assertNotIn("DROP EXTERNAL", sql)
        self.assertNotIn("DROP MASTER KEY", sql)

    def test_login_cleanup_checks_all_sids_before_first_drop(self):
        sql = drop_pilot_logins_batch(TOKEN, Role.QUERY, {
            Principal.QUERY_READER: READER_SID, Principal.OBSERVER: OBSERVER_SID,
        })
        self.assertLess(sql.index("DB_ID(N'SQLPERF_LAB_EXT_TEST0005_QUERY')"), sql.index("DROP LOGIN"))
        for sid in ("1A", "2B"):
            self.assertLess(sql.index(f"original_security_id = 0x{sid * 16}"), sql.index("DROP LOGIN"))
        self.assertIn("COLLATE Latin1_General_100_BIN2", sql)
        self.assertEqual(sql.count("DROP LOGIN"), 2)
        self.assertNotIn("SqlPerfExtReader_TEST0005", sql)

    def test_partial_inventory_rejects_adoption_of_an_unrecorded_login(self):
        sql = drop_pilot_logins_batch(TOKEN, Role.QUERY, {Principal.OBSERVER: OBSERVER_SID})
        self.assertIn("IF SUSER_ID(N'SqlPerfExtQueryReader_TEST0005') IS NOT NULL", sql)
        self.assertIn("login was not recorded", sql)
        self.assertNotIn("DROP LOGIN [SqlPerfExtQueryReader_TEST0005]", sql)
        self.assertIn("DROP LOGIN [SqlPerfExtObserver_TEST0005]", sql)

    def test_duplicate_sid_wrong_role_and_bad_token_fail_without_sql(self):
        with self.assertRaises(ValueError):
            drop_pilot_logins_batch(TOKEN, Role.SOURCE, {Principal.OBSERVER: OBSERVER_SID})
        with self.assertRaises(ValueError):
            drop_pilot_logins_batch(TOKEN, Role.QUERY, {
                Principal.QUERY_READER: OBSERVER_SID, Principal.OBSERVER: OBSERVER_SID,
            })
        with self.assertRaises(ValueError):
            drop_pilot_database_batch("TEST'005", Role.SOURCE)


if __name__ == "__main__":
    unittest.main()
