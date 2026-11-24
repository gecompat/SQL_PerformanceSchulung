from ipaddress import IPv4Interface
from pathlib import Path
import sys
from time import monotonic
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Runtime"))

import external_tables_driver_evidence as evidence
from external_tables_guest_network import GuestNetwork


NETWORK = GuestNetwork(IPv4Interface((0xC0A8FD02, 29)), IPv4Interface((0xC0A8FD03, 29)))
DRIVER = evidence.DriverEvidence("mssql-ees.service", "17.0.5065.9-3", "libmsodbcsql-18.5.so.1.1", "a" * 64)
STAT = "232 (external) " + " ".join(["S", *(["0"] * 18), "80917"])


class DriverEvidenceTests(unittest.TestCase):
    def test_readable_socket_owners_must_agree(self):
        line = f'0 0 {NETWORK.query.ip}:50841 {NETWORK.source.ip}:1433 users:(("dotnet",pid=232,fd=9))'
        self.assertIsNone(evidence._unique_pid(""))
        self.assertEqual(evidence._unique_pid(line + "\n" + line.replace("50841", "50842")), 232)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            evidence._unique_pid(line + "\n" + line.replace("232", "233"))
        with self.assertRaisesRegex(ValueError, "recognized process"):
            evidence._unique_pid(line.split("users:")[0])

    def test_live_capture_rejects_request_exit_and_pid_reuse(self):
        for case in ("ok", "request ended", "pid changed"):
            with (
                self.subTest(case=case),
                patch.object(evidence, "_live_pid", return_value=232),
                patch.object(evidence, "_read", side_effect=[
                    STAT, STAT if case != "pid changed" else STAT.replace("80917", "80918"),
                ]),
                patch.object(evidence, "_inspect_driver", return_value=DRIVER) as inspect,
            ):
                finished = Mock(side_effect=[False, case == "request ended"])
                if case == "ok":
                    self.assertEqual(evidence.observe_connector_driver(NETWORK, finished, monotonic() + 4), DRIVER)
                else:
                    with self.assertRaises(ValueError):
                        evidence.observe_connector_driver(NETWORK, finished, monotonic() + 4)
                    self.assertEqual(inspect.call_count, int(case == "pid changed"))

    def test_driver_metadata_can_contain_only_reviewable_identifiers(self):
        for service, version, driver_name, digest in (
            ("outside.service", DRIVER.version, DRIVER.driver_file, DRIVER.sha256),
            (DRIVER.service, "unbound", DRIVER.driver_file, DRIVER.sha256),
            (DRIVER.service, DRIVER.version, "/local/" + DRIVER.driver_file, DRIVER.sha256),
            (DRIVER.service, DRIVER.version, DRIVER.driver_file, "x" * 64),
        ):
            with self.subTest(service=service, version=version, driver_name=driver_name), self.assertRaises(ValueError):
                evidence.DriverEvidence(service, version, driver_name, digest)


if __name__ == "__main__":
    unittest.main()
