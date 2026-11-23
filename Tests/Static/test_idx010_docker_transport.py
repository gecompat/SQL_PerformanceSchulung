from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from time import monotonic
from unittest import TestCase, main
from unittest.mock import patch
from pathlib import Path
import sys
from subprocess import CompletedProcess
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from idx010_docker_transport import CATALOG_JOIN_WARNING, DockerPilotTransport, IMAGE, OWNER_LABEL, PROFILE, PROFILE_SQL, _run
from idx010_pilot_sequence import Arm, ArmEvidence, PilotResult, Target
from idx010_query_evidence import SegmentCounts
from run_idx010_ordered_ncci import main as run_ordered_ncci
from idx010_pilot_setup import fixture_identity_batch
from idx010_provision_sql import TEMPDB_CAPS, drop_database_batch, grant_reader_batch, provision_database_batch


CID = "4" * 64
TARGET = Target("TEST1", Arm.CONTROL)


class OrderedNcciEntrypointTests(TestCase):
    def test_confirmation_is_required_before_transport_creation(self):
        with patch("run_idx010_ordered_ncci.DockerPilotTransport") as transport, redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as stopped:
                run_ordered_ncci([])
        self.assertEqual(stopped.exception.code, 2)
        transport.assert_not_called()

    def test_output_and_exit_status_are_bounded(self):
        arms = (
            ArmEvidence(Arm.CONTROL, 6, SegmentCounts(4, 0)),
            ArmEvidence(Arm.ORDERED, 0, SegmentCounts(1, 3)),
        )
        expected = (
            "IDX010_NCCI|ARM|CONTROL|overlapping_pairs=6|segments_read=4|segments_skipped=0\n"
            "IDX010_NCCI|ARM|ORDERED|overlapping_pairs=0|segments_read=1|segments_skipped=3\n"
        )
        for status, code in (("PASS", 0), ("NOT_PROVEN", 1), ("FAIL_CLEANUP", 3)):
            output = StringIO()
            with (
                self.subTest(status=status),
                redirect_stdout(output),
                patch("run_idx010_ordered_ncci.run_pilot", return_value=PilotResult(status, "comparison", arms)) as run,
            ):
                self.assertEqual(run_ordered_ncci(["--confirm-disposable-container"]), code)
                self.assertRegex(run.call_args.args[1], r"^[0-9A-F]{20}$")
                self.assertEqual(output.getvalue(), expected + f"IDX010_NCCI|{status}|stage=comparison\n")


class DockerPilotTransportTests(TestCase):
    def test_sql_provisions_caps_and_reader_before_guarded_cleanup(self):
        sql = provision_database_batch(TARGET)
        self.assertIn("MAXSIZE = 512 MB", sql)
        self.assertIn("SQLPERF.PilotProfile", sql)
        self.assertIn("AND max_size = 65536", sql)
        self.assertIn("GRANT SHOWPLAN TO [idx010_reader_TEST1]", sql)
        self.assertIn("GRANT SELECT ON OBJECT::dbo.Events", grant_reader_batch(TARGET))
        self.assertIn("WHERE max_size <= 0 OR size > max_size", TEMPDB_CAPS)
        drop = drop_database_batch(TARGET)
        self.assertLess(drop.index("FAIL_OWNERSHIP"), drop.index("DROP DATABASE"))
        self.assertNotIn("DROP DATABASE [master]", drop)

    @patch("idx010_docker_transport._docker")
    def test_start_binds_digest_network_resources_and_runtime_identity(self, docker):
        transport = DockerPilotTransport()
        image_id = b"sha256:" + b"a" * 64
        docker.side_effect = [
            image_id, CID.encode(), CID.encode(), CID.encode(),
            image_id + b"|none|2000000000|4294967296|4294967296|[]|{}|created", CID.encode(),
            b"  Avail\n 2883584\n",
        ]
        with patch.object(transport, "_sql", side_effect=[PROFILE.encode(), b"", b""]) as sql:
            transport.start_verified_instance("TEST1", monotonic() + 30)
        argv = docker.call_args_list[1].args[0]
        self.assertEqual(argv[:3], ["create", "--pull", "never"])
        self.assertEqual(argv[-1], IMAGE)
        self.assertEqual(docker.call_args_list[4].args[0][0], "inspect")
        self.assertEqual(docker.call_args_list[5].args[0], ["start", CID])
        self.assertIn("none", argv)
        self.assertIn("MSSQL_SA_PASSWORD", argv)
        self.assertNotIn(transport._sa_password, argv)
        self.assertIn(TEMPDB_CAPS, [call.args[1] for call in sql.call_args_list])
        self.assertEqual(
            docker.call_args.args[0],
            ["exec", "-e", "LC_ALL=C", CID, "df", "-k", "--output=avail", "/var/opt/mssql/data"],
        )

    @patch("idx010_docker_transport._docker")
    def test_unconfirmed_capacity_stops_before_any_sql_mutation(self, docker):
        image_id = b"sha256:" + b"a" * 64
        for capacity in (b"Avail\n2883583\n", b"Avail\nunknown\n", b"Avail\n9999999\n9999999\n"):
            with self.subTest(capacity=capacity):
                transport = DockerPilotTransport()
                docker.side_effect = [
                    image_id, CID.encode(), CID.encode(), CID.encode(),
                    image_id + b"|none|2000000000|4294967296|4294967296|[]|{}|created", CID.encode(),
                    capacity,
                ]
                with patch.object(transport, "_sql", return_value=PROFILE.encode()) as sql:
                    with self.assertRaisesRegex(OSError, "confirmed free capacity"):
                        transport.start_verified_instance("TEST1", monotonic() + 30)
                self.assertEqual([call.args[1] for call in sql.call_args_list], [PROFILE_SQL])

    @patch("idx010_docker_transport._docker")
    def test_mismatched_resources_prevent_container_start(self, docker):
        transport = DockerPilotTransport()
        image_id = b"sha256:" + b"a" * 64
        docker.side_effect = [
            image_id, CID.encode(), CID.encode(), CID.encode(),
            image_id + b"|bridge|2000000000|4294967296|4294967296|[]|{}|created",
        ]
        with patch.object(transport, "_sql") as sql:
            with self.assertRaisesRegex(OSError, "container limits"):
                transport.start_verified_instance("TEST1", monotonic() + 30)
        sql.assert_not_called()
        self.assertNotIn("start", [call.args[0][0] for call in docker.call_args_list])

    @patch("idx010_docker_transport._docker")
    def test_interrupted_create_requires_positive_cleanup_evidence(self, docker):
        transport = DockerPilotTransport()
        image_id = b"sha256:" + b"a" * 64
        docker.side_effect = [image_id, TimeoutError(), b"", b""]
        with self.assertRaises(TimeoutError):
            transport.start_verified_instance("TEST1", monotonic() + 30)
        self.assertFalse(transport.cleanup("TEST1", (), monotonic() + 30))

    @patch("idx010_docker_transport._docker")
    def test_cleanup_recovers_owned_container_after_interrupted_create(self, docker):
        transport = DockerPilotTransport()
        image_id = b"sha256:" + b"a" * 64
        docker.side_effect = [
            image_id, TimeoutError(), CID.encode(), CID.encode(),
            CID.encode(), CID.encode(), b"", b"", b"",
        ]
        with self.assertRaises(TimeoutError):
            transport.start_verified_instance("TEST1", monotonic() + 30)
        self.assertTrue(transport.cleanup("TEST1", (), monotonic() + 30))
        commands = [call.args[0] for call in docker.call_args_list]
        self.assertIn(["rm", "--force", "--volumes", CID], commands)
        self.assertNotIn(["start", CID], commands)

    @patch("idx010_docker_transport._docker")
    def test_reader_creation_timeout_requires_sql_cleanup(self, docker):
        image_id = b"sha256:" + b"a" * 64
        for cleanup_error in (None, OSError("reader SID mismatch")):
            with self.subTest(cleanup_error=cleanup_error):
                transport = DockerPilotTransport()
                docker.reset_mock()
                docker.side_effect = [
                    image_id, CID.encode(), CID.encode(), CID.encode(),
                    image_id + b"|none|2000000000|4294967296|4294967296|[]|{}|created", CID.encode(),
                    b"Avail\n2883584\n", CID.encode(), CID.encode(), CID.encode(), CID.encode(), b"", b"", b"",
                ]
                with patch.object(
                    transport, "_sql", side_effect=[PROFILE.encode(), b"", TimeoutError(), cleanup_error or b""]
                ) as sql:
                    with self.assertRaises(TimeoutError):
                        transport.start_verified_instance("TEST1", monotonic() + 30)
                    self.assertEqual(transport.cleanup("TEST1", (), monotonic() + 30), cleanup_error is None)
                create_sql, cleanup_sql = [call.args[1] for call in sql.call_args_list[-2:]]
                self.assertIn(f"SID = 0x{transport._reader_sid}", create_sql)
                self.assertIn(f"AND sid = 0x{transport._reader_sid}", cleanup_sql)
                self.assertLess(cleanup_sql.index("ownership cannot be confirmed"), cleanup_sql.index("DROP LOGIN"))
                self.assertIn(["rm", "--force", "--volumes", CID], [call.args[0] for call in docker.call_args_list])

    @patch("idx010_docker_transport._docker")
    def test_mismatched_owner_is_never_removed(self, docker):
        transport = DockerPilotTransport()
        transport._name = "sqlperf-idx010-test"
        transport._run_token = "TEST1"
        docker.side_effect = [CID.encode(), b"5" * 64]
        with self.assertRaises(OSError):
            transport.cleanup("TEST1", (TARGET,), monotonic() + 90)
        self.assertTrue(all(call.args[0][0] == "container" for call in docker.call_args_list))

    @patch("idx010_docker_transport._docker", return_value=b"")
    def test_unconfirmed_sql_cleanup_removes_only_verified_container(self, docker):
        transport = DockerPilotTransport()
        transport._name = "sqlperf-idx010-test"
        transport._run_token = "TEST1"
        with (
            patch.object(transport, "_find_owned", side_effect=[CID, CID, None]),
            patch.object(transport, "_sql", side_effect=[b"1", OSError]),
        ):
            self.assertFalse(transport.cleanup("TEST1", (TARGET,), monotonic() + 90))
        self.assertEqual(docker.call_args.args[0], ["rm", "--force", "--volumes", CID])

    def test_real_process_uses_pilot_deadline_above_diagnostic_default(self):
        result = _run(
            [sys.executable, "-c", "print('owned synthetic output')"],
            b"", os.environ.copy(), monotonic() + 30, 64,
        )
        self.assertEqual(result.strip(), b"owned synthetic output")

    def test_catalog_warning_requires_opt_in_and_successful_process(self):
        command = ["synthetic"]
        args = command, b"", {}, monotonic() + 30, 64
        for exit_code, stderr, allow, accepted in (
            (0, CATALOG_JOIN_WARNING, None, False),
            (0, CATALOG_JOIN_WARNING, CATALOG_JOIN_WARNING, True),
            (0, CATALOG_JOIN_WARNING + b"\nUnexpected warning", CATALOG_JOIN_WARNING, False),
            (1, CATALOG_JOIN_WARNING, CATALOG_JOIN_WARNING, False),
        ):
            with self.subTest(exit_code=exit_code, stderr=stderr, allow=allow):
                response = CompletedProcess(command, exit_code, b"catalog result", stderr)
                with patch("idx010_docker_transport.collect_bounded_process", return_value=response):
                    if accepted:
                        self.assertEqual(_run(*args, allowed_warning=allow), b"catalog result")
                    else:
                        with self.assertRaises(OSError):
                            _run(*args, allowed_warning=allow)

    def test_catalog_capture_removes_only_outer_sqlcmd_padding(self):
        transport = DockerPilotTransport()
        transport._ready = True
        transport._run_token = TARGET.run_token
        receipt = b'{"test": "  content  "}'
        with (
            patch.object(transport, "_sql", return_value=receipt.ljust(4096) + b"\n") as sql,
            patch("idx010_docker_transport.decode_index_evidence") as decode,
        ):
            transport.index_evidence(TARGET, monotonic() + 30)
        self.assertEqual(sql.call_args.kwargs["allowed_warning"], CATALOG_JOIN_WARNING)
        decode.assert_called_once_with(receipt, TARGET)

    def test_identity_reads_fixed_pages_in_primary_key_order(self):
        transport = DockerPilotTransport()
        transport._ready = True
        transport._run_token = "TEST1"
        query = fixture_identity_batch(TARGET.run_token, TARGET.arm)
        with (
            patch("idx010_docker_transport.FIXTURE_ROWS", 4),
            patch("idx010_docker_transport.PAGE_ROWS", 2),
            patch.object(transport, "_sql", side_effect=[b"0|0\n1|1\n", b"2|2\n3|3\n"]) as sql,
        ):
            self.assertEqual(list(transport.stream_rows(TARGET, query, monotonic() + 30)), [
                (0, 0), (1, 1), (2, 2), (3, 3),
            ])
        self.assertIn("EventId >= 0 AND EventId < 2", sql.call_args_list[0].args[1])
        self.assertIn("EventId >= 2 AND EventId < 4", sql.call_args_list[1].args[1])


if __name__ == "__main__":
    main()
