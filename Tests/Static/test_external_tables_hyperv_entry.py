from contextlib import redirect_stdout
from dataclasses import replace
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from external_tables_hyperv_host import BootstrapMedia
from external_tables_pilot import PilotResult
import run_external_tables_hyperv as entry


TOKEN = "TEST0284"
STATUS = b"Package: ubuntu-base\nArchitecture: amd64\nVersion: 1\nStatus: install ok installed\n\n"


class HyperVEntryTests(unittest.TestCase):
    def setUp(self):
        owner = TemporaryDirectory(prefix="sqlperf-entry-test-")
        self.addCleanup(owner.cleanup)
        root = Path(owner.name)
        run = root / "run"
        run.mkdir()
        source_snapshot = root / "source.iso"
        source_snapshot.write_bytes(b"source boot media")
        query_snapshot = root / "query.iso"
        query_snapshot.write_bytes(b"query boot media")
        template = root / "base.vhdx"
        template.write_bytes(b"pinned base template")
        status = root / "status"
        status.write_bytes(STATUS)
        media = BootstrapMedia(sha256(source_snapshot.read_bytes()).hexdigest(), sha256(query_snapshot.read_bytes()).hexdigest())
        self.inputs = entry.PilotInputs(
            TOKEN, run, template, sha256(template.read_bytes()).hexdigest(), source_snapshot, query_snapshot, media, status,
            2760, 2762,
        )
        package_lock = root / "lock.json"
        self.lock = {"dpkg_status_sha256": sha256(STATUS).hexdigest()}
        package_lock.write_text(json.dumps(self.lock), encoding="utf-8")
        patcher = patch.object(entry, "_LOCK", package_lock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_missing_host_registration_stops_before_any_provider_call(self):
        with (
            patch.object(entry, "require_registered_hyperv_ports", side_effect=OSError()) as verify,
            patch.object(entry, "provision_detached_hyperv") as provision,
            patch.object(entry, "run_prepared_hyperv_pilot") as execute,
        ):
            result = entry.run_hyperv_lab(self.inputs, apply=True)
        self.assertEqual((result.status, result.stage), ("NOT_PROVEN", "host_services"))
        verify.assert_called_once_with(2760, 2762)
        provision.assert_not_called()
        execute.assert_not_called()
        self.assertEqual(list(self.inputs.directory.iterdir()), [])

    def test_read_only_preflight_stops_before_provision_and_rejects_wrong_hash(self):
        with (
            patch.object(entry, "require_registered_hyperv_ports"),
            patch.object(entry, "provision_detached_hyperv") as provision,
        ):
            result = entry.run_hyperv_lab(self.inputs)
            self.assertEqual((result.status, result.stage), ("VERIFIED", "host_preflight"))
            bad = replace(self.inputs, template_sha256="0" * 64)
            result = entry.run_hyperv_lab(bad, apply=True)
            self.assertEqual((result.status, result.stage), ("NOT_PROVEN", "host_inputs"))
        provision.assert_not_called()
        self.assertEqual(list(self.inputs.directory.iterdir()), [])

    def test_apply_stages_both_media_and_passes_only_the_bound_inputs(self):
        journal = Mock()
        result = PilotResult("PASS", "comparison", ("pushdown-on", "pushdown-off"), True, True)

        def execute(bound, status, package_lock, *, bootstrap_port, boot_media, expected_driver_sha256):
            self.assertIs(bound, journal)
            self.assertEqual(expected_driver_sha256, "f" * 64)
            self.assertEqual((status, package_lock, bootstrap_port, boot_media), (STATUS, self.lock, 2760, self.inputs.media))
            self.assertEqual((self.inputs.directory / "source.iso").read_bytes(), self.inputs.source_iso.read_bytes())
            self.assertEqual((self.inputs.directory / "query.iso").read_bytes(), self.inputs.query_iso.read_bytes())
            return result

        with (
            patch.object(entry, "require_registered_hyperv_ports"),
            patch.object(entry, "provision_detached_hyperv", return_value=journal) as provision,
            patch.object(entry, "run_prepared_hyperv_pilot", side_effect=execute),
        ):
            self.assertIs(entry.run_hyperv_lab(replace(self.inputs, expected_driver_sha256="f" * 64), apply=True), result)
        self.assertEqual(provision.call_args.args[:3], (self.inputs.directory, TOKEN, 2762))
        for role in ("source", "query"):
            self.assertEqual(provision.call_args.kwargs[f"{role}_template"], self.inputs.template)
            self.assertEqual(provision.call_args.kwargs[f"{role}_sha256"], self.inputs.template_sha256)

    def test_provisioning_failure_recovers_only_its_bound_attempt(self):
        for recovery_error in (None, ValueError("unbound")):
            with (
                self.subTest(recovery_error=recovery_error),
                patch.object(entry, "require_registered_hyperv_ports"),
                patch.object(entry, "provision_detached_hyperv", side_effect=OSError("partial")) as provision,
                patch.object(entry, "recover_partial_hyperv", side_effect=recovery_error) as recover,
                patch.object(entry, "run_prepared_hyperv_pilot") as execute,
            ):
                result = entry.run_hyperv_lab(self.inputs, apply=True)
                self.assertEqual(result.stage, "guest_provisioning")
                self.assertEqual(result.guest_cleanup, recovery_error is None)
                self.assertEqual(result.status, "NOT_PROVEN" if recovery_error is None else "FAIL_CLEANUP")
                self.assertEqual(recover.call_args.args[:3], (
                    self.inputs.directory, TOKEN, provision.call_args.kwargs["attempt_id"],
                ))
                execute.assert_not_called()

    def test_media_changed_after_preflight_discards_only_the_bound_preparation(self):
        for cleanup in (True, False):
            with self.subTest(cleanup=cleanup):
                snapshot = self.inputs.source_iso
                snapshot.write_bytes(b"source boot media")
                journal = Mock()
                provider = Mock()
                provider.discard_unstarted_guests.return_value = cleanup

                def poison(*args, **kwargs):
                    snapshot.write_bytes(b"changed after provisioning")
                    return journal

                with (
                    patch.object(entry, "require_registered_hyperv_ports"),
                    patch.object(entry, "provision_detached_hyperv", side_effect=poison),
                    patch.object(entry, "run_prepared_hyperv_pilot") as execute,
                    patch.object(entry, "HyperVPreparedTransport", return_value=provider) as transport,
                ):
                    result = entry.run_hyperv_lab(self.inputs, apply=True)
                self.assertEqual((result.status, result.stage, result.guest_cleanup),
                                 ("NOT_PROVEN" if cleanup else "FAIL_CLEANUP", "host_media_staging", cleanup))
                execute.assert_not_called()
                transport.assert_called_once_with(journal, STATUS, self.lock)
                provider.discard_unstarted_guests.assert_called_once()
                self.assertFalse((self.inputs.directory / "source.iso").exists())

    def test_cli_returns_a_bounded_json_result(self):
        x = self.inputs
        options = [
            "--token", x.token, "--run-directory", str(x.directory), "--template", str(x.template),
            "--template-sha256", x.template_sha256, "--source-iso", str(x.source_iso), "--source-sha256", x.media.source_sha256,
            "--query-iso", str(x.query_iso), "--query-sha256", x.media.query_sha256, "--base-status", str(x.base_status),
            "--bootstrap-port", str(x.bootstrap_port), "--sql-port", str(x.sql_port),
        ]
        with patch.object(entry, "require_registered_hyperv_ports"), redirect_stdout(StringIO()) as output:
            self.assertEqual(entry.main(options), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "VERIFIED")
        self.assertNotIn(x.directory.name, json.loads(output.getvalue()).values())


if __name__ == "__main__":
    unittest.main()
