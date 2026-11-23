from __future__ import annotations

from time import monotonic
from unittest import TestCase, main
from unittest.mock import patch
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

from idx010_docker_transport import DockerPilotTransport, IMAGE, OWNER_LABEL, PROFILE, PROFILE_SQL, _run
from idx010_pilot_sequence import Arm, Target
from idx010_pilot_setup import fixture_identity_batch
from idx010_provision_sql import TEMPDB_CAPS, drop_database_batch, grant_reader_batch, provision_database_batch


CID = "4" * 64
TARGET = Target("TEST1", Arm.CONTROL)


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
            image_id + b"|none|2000000000|4294967296|4294967296|[]|{}",
            b"  Avail\n 2883584\n",
        ]
        with patch.object(transport, "_sql", side_effect=[PROFILE.encode(), b"", b""]) as sql:
            transport.start_verified_instance("TEST1", monotonic() + 30)
        argv = docker.call_args_list[1].args[0]
        self.assertEqual(argv[-1], IMAGE)
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
                    image_id + b"|none|2000000000|4294967296|4294967296|[]|{}",
                    capacity,
                ]
                with patch.object(transport, "_sql", return_value=PROFILE.encode()) as sql:
                    with self.assertRaisesRegex(OSError, "confirmed free capacity"):
                        transport.start_verified_instance("TEST1", monotonic() + 30)
                self.assertEqual([call.args[1] for call in sql.call_args_list], [PROFILE_SQL])

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
