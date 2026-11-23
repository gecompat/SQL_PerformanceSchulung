from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_measurement import MeasurementResult
from external_tables_pilot import CLEANUP_SECONDS, WORK_SECONDS, run_pilot
from external_tables_pilot_sql import DAY_ZERO, ROWS, Role, database_name
from external_tables_principals import Principal


TOKEN = "TEST0006"


class GuestTransport:
    def __init__(self, failing=(), guests_clean=True):
        self.events = []
        self.databases = set()
        self.marked = set()
        self.login_sids = {}
        self.failing = set(failing)
        self.guests_clean = guests_clean

    def _event(self, name, value, deadline):
        self.events.append((name, value, deadline))
        if (name, value) in self.failing:
            raise OSError("synthetic operation failed")

    def start_verified_guests(self, token, deadline):
        assert token == TOKEN
        self._event("boot", token, deadline)

    def execute(self, role, database, sql, deadline):
        if "CREATE DATABASE" in sql and "CREATE DATABASE SCOPED CREDENTIAL" not in sql:
            assert database == "master"
            self.databases.add(role)
            event = "create_database"
        elif "sp_addextendedproperty" in sql:
            assert database == database_name(TOKEN, role)
            self.marked.add(role)
            event = "configure_database"
        elif "DROP DATABASE [" in sql:
            assert database == database_name(TOKEN, role)
            event = "drop_database"
            if role not in self.marked:
                raise OSError("database was never marked")
        elif "SQL login still exists" in sql:
            assert database == "master" and role not in self.databases
            for principal, sid in self.login_sids.items():
                if principal.role is role:
                    assert "0x" + sid.hex().upper() in sql
            event = "drop_logins"
        elif "CREATE LOGIN" in sql:
            assert any(sid.hex().upper() in sql for sid in self.login_sids.values())
            event = "create_login"
        elif "CREATE STATISTICS" in sql:
            event = "statistics"
        else:
            event = "fixture_or_external_sql"
        self._event(event, role, deadline)
        if event == "drop_database":
            self.databases.remove(role)

    def record_login(self, principal, sid, deadline):
        assert principal not in self.login_sids
        self._event("record_login", principal, deadline)
        self.login_sids[principal] = sid

    def verify_source_tls(self, token, secret, deadline):
        assert token == TOKEN and secret.startswith("Ext9!")
        self._event("tls", token, deadline)

    def probe_principal(self, principal, secret, sql, deadline):
        assert secret.startswith("Ext9!") and "ORIGINAL_LOGIN()" in sql
        self._event("rights", principal, deadline)

    def fixture_rows(self, role, sql, deadline):
        assert "ORDER BY FactId" in sql
        self._event("rows", role, deadline)
        for index in range(ROWS):
            day, offset = divmod(index, 64)
            category, ordinal = divmod(offset, 16)
            yield index, DAY_ZERO + timedelta(days=day), category, day * 100 + category * 10 + ordinal

    @contextmanager
    def open_measurement(self, token, reader_secret, observer_secret, deadline):
        assert token == TOKEN and reader_secret != observer_secret
        self._event("open_measurement", token, deadline)
        try:
            yield object()
        finally:
            self._event("close_measurement", token, deadline)

    def close_data_connections(self, token, deadline):
        self._event("close_data", token, deadline)
        return True

    def database_exists(self, role, name, deadline):
        assert name == database_name(TOKEN, role)
        self._event("database_exists", role, deadline)
        return role in self.databases

    def remove_verified_guests(self, token, deadline):
        self._event("remove_guests", token, deadline)
        return self.guests_clean


class PilotCoordinatorTests(unittest.TestCase):
    @patch("external_tables_pilot.measure_pushdown", return_value=MeasurementResult("PASS", "comparison", ("on", "off")))
    def test_pilot_uses_one_work_deadline_and_a_separate_cleanup_window(self, measure):
        transport = GuestTransport()
        with patch("external_tables_pilot.monotonic", return_value=100):
            result = run_pilot(transport, TOKEN)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.filters, ("on", "off"))
        work, teardown = (100 + WORK_SECONDS, 100 + CLEANUP_SECONDS)
        measure.assert_called_once()
        self.assertEqual(measure.call_args.args[1:], (TOKEN, work))
        self.assertEqual(transport.events[0], ("boot", TOKEN, work))
        self.assertIn(("rights", Principal.SOURCE_READER, work), transport.events)
        self.assertIn(("statistics", Role.QUERY, work), transport.events)
        relevant = [(event, value) for event, value, _ in transport.events if event in ("drop_database", "drop_logins")]
        self.assertEqual(relevant, [
            ("drop_database", Role.QUERY), ("drop_logins", Role.QUERY),
            ("drop_database", Role.SOURCE), ("drop_logins", Role.SOURCE),
        ])
        self.assertEqual(transport.events[-1], ("remove_guests", TOKEN, teardown))
        self.assertTrue(result.sql_cleanup and result.guest_cleanup)

    @patch("external_tables_pilot.measure_pushdown")
    def test_partly_created_second_database_and_attempted_logins_are_cleaned(self, measure):
        for failure, expected_stage in (
            (("configure_database", Role.QUERY), "database_setup"),
            (("create_login", Role.QUERY), "query_access"),
        ):
            with self.subTest(failure=failure):
                transport = GuestTransport(failing=(failure,))
                result = run_pilot(transport, TOKEN)
                self.assertEqual((result.status, result.stage), ("NOT_PROVEN", expected_stage))
                self.assertFalse(transport.databases)
                self.assertTrue(result.sql_cleanup and result.guest_cleanup)
        measure.assert_not_called()

    def test_guest_cleanup_is_attempted_after_partial_boot_or_sql_cleanup_failure(self):
        for failures, expected in (
            ((("boot", TOKEN),), ("NOT_PROVEN", True)),
            (
                (("create_database", Role.QUERY),),
                ("FAIL_CLEANUP", False),
            ),
        ):
            with self.subTest(failures=failures):
                transport = GuestTransport(failing=failures)
                result = run_pilot(transport, TOKEN)
                self.assertEqual((result.status, result.sql_cleanup), expected)
                self.assertEqual(transport.events[-1][:2], ("remove_guests", TOKEN))
                self.assertTrue(result.guest_cleanup)
                self.assertNotIn(Role.SOURCE, transport.databases)

    @patch("external_tables_pilot.measure_pushdown", return_value=MeasurementResult("PASS", "comparison", ("on", "off")))
    def test_unconfirmed_connection_closure_prevents_sql_teardown(self, _):
        for confirmation in (False, OSError("closure could not be observed")):
            with self.subTest(confirmation=confirmation):
                transport = GuestTransport()
                with patch.object(transport, "close_data_connections") as close_data:
                    if isinstance(confirmation, OSError):
                        close_data.side_effect = confirmation
                    else:
                        close_data.return_value = confirmation
                    result = run_pilot(transport, TOKEN)
                close_data.assert_called_once()
                self.assertEqual((result.status, result.sql_cleanup, result.guest_cleanup),
                                 ("FAIL_CLEANUP", False, True))
                self.assertIsNone(result.filters)
                self.assertEqual(transport.databases, {Role.SOURCE, Role.QUERY})
                sql_teardown = {"database_exists", "drop_database", "drop_logins"}
                observed = {name for name, _, _ in transport.events}
                self.assertFalse(observed & sql_teardown)
                self.assertEqual(transport.events[-1][:2], ("remove_guests", TOKEN))

    @patch("external_tables_pilot.measure_pushdown", return_value=MeasurementResult("PASS", "comparison", ("on", "off")))
    def test_guest_cleanup_failure_overrides_a_positive_sql_result(self, _):
        result = run_pilot(GuestTransport(guests_clean=False), TOKEN)
        self.assertEqual(result.status, "FAIL_CLEANUP")
        self.assertIsNone(result.filters)
        self.assertTrue(result.sql_cleanup)
        self.assertFalse(result.guest_cleanup)


if __name__ == "__main__":
    unittest.main()
