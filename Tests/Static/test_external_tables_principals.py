from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_pilot_sql import Role, external_tables_batch, fixture_batch
from external_tables_principals import (
    Principal, create_connector_credential_batch, create_principal_batch, principal_name, principal_probe_batch,
)


TOKEN = "TEST0004"
PASSWORD = "Ext9!" + "0" * 32
SID = bytes.fromhex("1a" * 16)


class PrincipalContractTests(unittest.TestCase):
    def test_source_reader_matches_the_connector_credential_and_has_one_object_grant(self):
        name = principal_name(TOKEN, Principal.SOURCE_READER)
        create = create_principal_batch(TOKEN, Principal.SOURCE_READER, PASSWORD, SID)
        self.assertIn(f"credential_identity = N'{name}'", external_tables_batch(TOKEN))
        self.assertIn("EXTERNAL_TABLES_SOURCE", create)
        self.assertIn("SID = 0x" + "1A" * 16, create)
        with self.assertRaises(ValueError):
            create_principal_batch(TOKEN, Principal.SOURCE_READER, PASSWORD, bytes(16))
        self.assertIn(f"GRANT SELECT ON OBJECT::dbo.Facts TO [{name}];", create)
        self.assertEqual(create.count("GRANT"), 1)
        self.assertLess(create.index("FAIL_OWNERSHIP"), create.index("CREATE LOGIN"))
        self.assertLess(create.index("BEGIN TRANSACTION"), create.index("CREATE LOGIN"))
        self.assertIn("CREATE TABLE dbo.PilotDenied", fixture_batch(TOKEN, Role.SOURCE))

    def test_query_reader_requires_external_tables_and_has_three_select_grants(self):
        create = create_principal_batch(TOKEN, Principal.QUERY_READER, PASSWORD, SID)
        self.assertIn("EXTERNAL_TABLES_QUERY", create)
        self.assertLess(create.index("sys.external_tables"), create.index("CREATE LOGIN"))
        self.assertIn("GRANT SELECT ON OBJECT::dbo.FactsPush", create)
        self.assertIn("GRANT SELECT ON OBJECT::dbo.FactsLocalFilter", create)
        self.assertEqual(create.count("GRANT"), 3)
        self.assertNotIn("SERVER PERFORMANCE STATE", create)

    def test_only_observer_has_performance_state_and_no_object_grant(self):
        create = create_principal_batch(TOKEN, Principal.OBSERVER, PASSWORD, SID)
        self.assertIn("GRANT VIEW SERVER PERFORMANCE STATE", create)
        self.assertNotIn("GRANT VIEW SERVER STATE", create)
        self.assertEqual(create.count("GRANT"), 1)
        self.assertLess(create.index("USE [master]"), create.index("GRANT VIEW SERVER PERFORMANCE STATE"))
        self.assertLess(create.index("USE [SQLPERF_LAB_EXT_TEST0004_QUERY]"), create.index("CREATE USER"))
        probe = principal_probe_batch(TOKEN, Principal.OBSERVER)
        self.assertIn("ORIGINAL_LOGIN()", probe)
        self.assertIn("FROM sys.dm_exec_requests", probe)
        self.assertIn("IF ERROR_NUMBER() <> 229 THROW", probe)
        self.assertIn("TOP (0) @prohibited", probe)
        self.assertNotIn("EXECUTE AS", probe)

    def test_invalid_names_and_sql_password_characters_fail_before_setup(self):
        for token, principal, password in (
            ("TEST'004", Principal.SOURCE_READER, PASSWORD),
            (TOKEN, "SOURCE_READER", PASSWORD),
            (TOKEN, Principal.SOURCE_READER, "Ext9!';" + "0" * 32),
        ):
            with self.subTest(token=token, principal=principal), self.assertRaises(ValueError):
                create_principal_batch(token, principal, password, SID)

    def test_credential_is_bound_to_query_database_and_separate_secrets(self):
        key_password = "Ext9!" + "1" * 32
        sql = create_connector_credential_batch(TOKEN, PASSWORD, key_password)
        self.assertIn("EXTERNAL_TABLES_QUERY", sql)
        self.assertLess(sql.index("FAIL_OWNERSHIP"), sql.index("CREATE MASTER KEY"))
        self.assertLess(sql.index("CREATE MASTER KEY"), sql.index("CREATE DATABASE SCOPED CREDENTIAL"))
        self.assertIn(f"IDENTITY = N'SqlPerfExtReader_TEST0004', SECRET = '{PASSWORD}'", sql)
        key_literal = "'" + key_password + "'"
        self.assertIn(f"ENCRYPTION BY PASSWORD = {key_literal}", sql)
        with self.assertRaises(ValueError):
            create_connector_credential_batch(TOKEN, PASSWORD, PASSWORD)

    def test_live_reader_probe_checks_writes_without_serializing_secrets(self):
        probe = principal_probe_batch(TOKEN, Principal.QUERY_READER)
        self.assertIn("ORIGINAL_LOGIN()", probe)
        self.assertIn("N'SqlPerfExtQueryReader_TEST0004'", probe)
        for name in ("Facts", "FactsPush", "FactsLocalFilter"):
            for action in ("INSERT", "UPDATE", "DELETE"):
                self.assertIn(f"HAS_PERMS_BY_NAME(N'dbo.{name}', N'OBJECT', N'{action}')", probe)
        self.assertNotIn(PASSWORD, probe)


if __name__ == "__main__":
    unittest.main()
