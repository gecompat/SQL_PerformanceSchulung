import json
from pathlib import Path, PureWindowsPath
import sys
from tempfile import TemporaryDirectory
from time import monotonic
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_guest_admin import AdminAction, AdminCommand
from external_tables_hyperv_host import (
    _PROBES, HyperVPreparedTransport, HyperVRunInventory, RunJournal, run_prepared_hyperv_pilot,
)
from external_tables_measurement import MeasurementResult
from external_tables_pilot_sql import Role
from external_tables_principals import Principal
from external_tables_pushdown_evidence import PUSHDOWN_FILTER_EVIDENCE


TOKEN = "TEST0049"
SID = b"a" * 16


class HyperVHostTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.inventory = HyperVRunInventory(
            TOKEN, uuid4(), uuid4(), uuid4(),
            PureWindowsPath(r"C:\Synthetic\Pilot\source.vhdx"), PureWindowsPath(r"C:\Synthetic\Pilot\query.vhdx"), 2762,
        )
        self.journal = RunJournal(self.directory, self.inventory)
        self.journal.bind()
        self.deadline = monotonic() + 8

    def test_journal_reopens_exact_identity_and_never_replaces_a_sid(self):
        self.journal.record_login(Principal.SOURCE_READER, SID)
        self.journal.record_login(Principal.SOURCE_READER, SID)
        reopened = RunJournal.load(self.directory)
        self.assertEqual(reopened.inventory, self.inventory)
        self.assertEqual(reopened.login_sids(), {Principal.SOURCE_READER: SID})
        with self.assertRaisesRegex(ValueError, "refuses to replace"):
            reopened.record_login(Principal.SOURCE_READER, b"b" * 16)
        self.assertEqual(reopened.login_sids(), {Principal.SOURCE_READER: SID})
        self.assertFalse(tuple(self.directory.glob(".external-tables-*")))
        (self.directory / "external-tables-owner.json").write_bytes(b"{}")
        with self.assertRaises(ValueError):
            self.journal.require_binding()
        with self.assertRaises(ValueError):
            RunJournal.load(self.directory)

    def test_duplicate_attempt_never_touches_the_active_run(self):
        self.journal.claim_work()
        with (
            patch("external_tables_hyperv_host.collect_bounded_process") as probe,
            patch("external_tables_hyperv_host.verify_guest") as verify,
        ):
            remove = Mock()
            result = run_prepared_hyperv_pilot(RunJournal.load(self.directory), b"base", {}, remove)
        self.assertEqual((result.status, result.stage, result.guest_cleanup), ("FAIL_CLEANUP", "guest_preflight", False))
        probe.assert_not_called()
        verify.assert_not_called()
        remove.assert_not_called()

    def test_sql_requires_both_host_probes_and_both_guest_identities(self):
        remove = Mock()
        transport = HyperVPreparedTransport(self.journal, b"base", {}, remove)
        with self.assertRaisesRegex(OSError, "preflight"):
            transport.admin(Role.SOURCE, AdminCommand(AdminAction.CREATE_DATABASE), self.deadline)
        with (
            patch("external_tables_hyperv_host.collect_bounded_process", side_effect=self._probe_result) as probe,
            patch("external_tables_hyperv_host.verify_guest", side_effect=[None, ValueError("synthetic identity mismatch")]) as verify,
        ):
            with self.assertRaises(ValueError):
                transport.start_verified_guests(TOKEN, self.deadline)
            with self.assertRaisesRegex(OSError, "preflight"):
                transport.admin(Role.SOURCE, AdminCommand(AdminAction.CREATE_DATABASE), self.deadline)
            self.assertTrue(transport.remove_verified_guests(TOKEN, self.deadline))
        self.assertEqual([call.args[0] for call in verify.call_args_list], [self.inventory.source_vm, self.inventory.query_vm])
        remove.assert_called_once_with(self.inventory, self.deadline)
        self.assertEqual(len(probe.call_args_list), 3)
        for call in probe.call_args_list:
            arguments = call.args[0]
            self.assertEqual(arguments[:4], ["pwsh", "-NoProfile", "-NonInteractive", "-File"])
            self.assertIn(str(self.inventory.source_vm), arguments)
            self.assertIn(str(self.inventory.query_vm), arguments)
            self.assertLessEqual(call.kwargs["timeout_seconds"], 20)

    def test_complete_coordinator_uses_recorded_sids_and_confirms_absence_after_removal(self):
        events = []
        channel = Mock()
        channel.close_data_connections.return_value = True
        channel.measure.return_value = MeasurementResult("PASS", "comparison", PUSHDOWN_FILTER_EVIDENCE)

        def run_admin(role, command, deadline):
            if command.action is AdminAction.CREATE_PRINCIPAL:
                recorded = self.journal.login_sids()
                principal = Principal[command.fields[0]]
                self.assertEqual(recorded[principal], bytes.fromhex(command.fields[2]))
            if command.action is AdminAction.DATABASE_EXISTS:
                return True
            return None

        channel.admin.side_effect = run_admin

        def bounded(command, **options):
            events.append(Path(command[4]).stem)
            return self._probe_result(command, **options)

        def remove(inventory, deadline):
            self.assertEqual(inventory, self.inventory)
            events.append("provider removal")

        with (
            patch("external_tables_hyperv_host.GuestSqlChannel", return_value=channel),
            patch("external_tables_hyperv_host.collect_bounded_process", side_effect=bounded),
            patch("external_tables_hyperv_host.verify_guest"),
        ):
            result = run_prepared_hyperv_pilot(self.journal, b"base", {}, remove)
        self.assertEqual((result.status, result.filters), ("PASS", PUSHDOWN_FILTER_EVIDENCE))
        self.assertTrue(result.guest_cleanup and result.sql_cleanup)
        self.assertEqual(
            events, ["Test-ExternalTablesHyperVResources", "Test-ExternalTablesHyperVNetwork",
                     "provider removal", "Test-ExternalTablesHyperVAbsence"],
        )

    @staticmethod
    def _probe_result(command, **_):
        name = Path(command[4]).stem.removeprefix("Test-ExternalTablesHyperV").lower()
        return SimpleNamespace(returncode=0, stdout=json.dumps(_PROBES[name]).encode(), stderr=b"")


if __name__ == "__main__":
    unittest.main()
