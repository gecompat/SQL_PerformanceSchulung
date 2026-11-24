from dataclasses import replace
import json
import os
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
    _PROBES, HyperVPreparedTransport, HyperVRunInventory, RunJournal, provision_detached_hyperv, run_prepared_hyperv_pilot,
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

    def test_default_cleanup_requires_disk_ids_and_checks_absence_after_removal(self):
        legacy = HyperVPreparedTransport(self.journal, b"base", {})
        with self.assertRaisesRegex(ValueError, "recorded VHDX identities"):
            legacy.start_verified_guests(TOKEN, self.deadline)
        self.assertFalse(legacy.remove_verified_guests(TOKEN, self.deadline))

        directory = self.directory / "v2"
        directory.mkdir()
        inventory = replace(self.inventory, source_disk_id=uuid4(), query_disk_id=uuid4())
        journal = RunJournal(directory, inventory)
        journal.bind()
        self.assertEqual(RunJournal.load(directory).inventory, inventory)
        transport = HyperVPreparedTransport(journal, b"base", {})

        def process(command, **options):
            if Path(command[4]).stem == "Remove-ExternalTablesHyperVOwnedRun":
                self.assertIn("-ApplyOwnedRun", command)
                self.assertIn(str(inventory.source_disk_id), command)
                self.assertIn(str(inventory.query_disk_id), command)
                self.assertEqual(options["timeout_ceiling_seconds"], 90)
                return SimpleNamespace(returncode=0, stdout=b'{"status":"REMOVED"}', stderr=b"")
            return self._probe_result(command, **options)

        with (
            patch("external_tables_hyperv_host.collect_bounded_process", side_effect=process) as probe,
            patch("external_tables_hyperv_host.verify_guest"),
        ):
            transport.start_verified_guests(TOKEN, self.deadline)
            self.assertTrue(transport.remove_verified_guests(TOKEN, self.deadline))
        self.assertEqual([Path(call.args[0][4]).stem for call in probe.call_args_list][-2:],
                         ["Remove-ExternalTablesHyperVOwnedRun", "Test-ExternalTablesHyperVAbsence"])

    @unittest.skipUnless(os.name == "nt", "the host receipt paths are Windows paths")
    def test_detached_provider_receipt_binds_all_individual_records(self):
        directory = self.directory / "fresh"
        directory.mkdir()
        source = self.directory / "approved-source.vhdx"
        query = self.directory / "approved-query.vhdx"
        source.touch()
        query.touch()
        prefix = f"SQLPerfExt-{TOKEN}"
        receipt = {"run": TOKEN, **{key: str(uuid4()) for key in (
            "source_vm", "query_vm", "switch", "source_disk_id", "query_disk_id",
        )}}

        def publish(name, content):
            (directory / name).write_text(json.dumps(content), encoding="utf-8")

        def provision(command, **kwargs):
            self.assertTrue(command[4].endswith("New-ExternalTablesHyperVDetachedRun.ps1"))
            self.assertIn("-ApplyOwnedRun", command)
            self.assertEqual(kwargs["timeout_ceiling_seconds"], 600)
            publish("external-tables-provision-intent.json", {
                "version": 1, "run": TOKEN, "switch": prefix, "vms": [f"{prefix}-SOURCE", f"{prefix}-QUERY"],
                "disks": ["source.vhdx", "query.vhdx"],
            })
            publish("external-tables-switch.json", {"name": prefix, "id": receipt["switch"]})
            for role in Role:
                name = role.value.lower()
                publish(f"external-tables-vm-{role.value}.json", {
                    "role": role.value, "name": f"{prefix}-{role.value}", "id": receipt[f"{name}_vm"],
                })
                publish(f"external-tables-disk-{role.value}.json", {
                    "role": role.value, "file": f"{name}.vhdx", "id": receipt[f"{name}_disk_id"],
                })
            publish("external-tables-detached.json", receipt)
            return SimpleNamespace(returncode=0, stdout=b'{"status":"DETACHED"}', stderr=b"")

        with patch("external_tables_hyperv_host.collect_bounded_process", side_effect=provision):
            journal = provision_detached_hyperv(
                directory, TOKEN, 2762, self.deadline, source_template=source, source_sha256="a" * 64,
                query_template=query, query_sha256="b" * 64,
            )
        self.assertEqual(str(journal.inventory.source_disk_id), receipt["source_disk_id"])
        self.assertEqual(str(journal.inventory.query_vm), receipt["query_vm"])
        publish("external-tables-disk-QUERY.json", {"role": "QUERY", "file": "query.vhdx", "id": receipt["source_disk_id"]})
        with self.assertRaisesRegex(ValueError, "guest or disk differs"):
            RunJournal.from_detached(directory, TOKEN, 2762)

    @staticmethod
    def _probe_result(command, **_):
        name = Path(command[4]).stem.removeprefix("Test-ExternalTablesHyperV").lower()
        return SimpleNamespace(returncode=0, stdout=json.dumps(_PROBES[name]).encode(), stderr=b"")


if __name__ == "__main__":
    unittest.main()
