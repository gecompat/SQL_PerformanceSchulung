from __future__ import annotations

from unittest import TestCase, main
from unittest.mock import Mock, patch

from inspect_external_tables_driver import VERSION, _start_time, in_service_group, observe, select_driver_mapping


GROUP = "/system.slice/mssql-ees.service"
DRIVER = "/var/opt/mssql/binn/PolyBase/ODBC Drivers/libmsodbcsql-18.5.so.1.1"
MAP = f"1000-2000 r-xp 00000000 08:02 701 {DRIVER}"
STAT = "232 (external ) service) " + " ".join(["S", *(["0"] * 18), "80917"])


class GuestDriverTests(TestCase):
    def test_collapses_memory_regions_for_same_file(self):
        result = select_driver_mapping(MAP + "\n" + MAP.replace("1000-2000 r-xp", "3000-4000 r--p"))
        self.assertEqual((result.major, result.minor, result.inode), (8, 2, 701))
        self.assertEqual(result.path.name, "libmsodbcsql-18.5.so.1.1")

    def test_rejects_missing_wrong_or_replaced_library(self):
        for maps in (
            "", MAP.replace("-18.5", "-17.10"), MAP + " (deleted)",
            MAP + "\n" + MAP.replace(" 701 ", " 702 "), MAP.replace(" 701 ", " 0 "),
        ):
            with self.subTest(maps=maps), self.assertRaises(ValueError):
                select_driver_mapping(maps)

    def test_requires_exact_cgroup_or_child(self):
        self.assertTrue(in_service_group(f"0::{GROUP}", GROUP))
        self.assertTrue(in_service_group(f"0::{GROUP}/child", GROUP))
        self.assertFalse(in_service_group(f"0::{GROUP}-other", GROUP))
        self.assertFalse(in_service_group("0::/system.slice", GROUP))
        self.assertFalse(in_service_group(f"0::{GROUP}\n0::{GROUP}", GROUP))
        self.assertEqual(_start_time(STAT), "80917")

    @patch("inspect_external_tables_driver._mapped_digest", return_value="f" * 64)
    @patch("inspect_external_tables_driver._command")
    @patch("inspect_external_tables_driver._read")
    @patch("inspect_external_tables_driver.subprocess.run", return_value=Mock(returncode=0))
    def test_observation_rechecks_process_instance_and_does_not_export_path(self, run, read, command, digest):
        installed = f"install ok installed|{VERSION}|amd64"
        command.side_effect = [GROUP, installed, installed, GROUP, installed, installed]
        read.side_effect = [STAT, f"0::{GROUP}", MAP, STAT, f"0::{GROUP}", MAP,
                            STAT, f"0::{GROUP}", MAP, STAT.replace("80917", "80918")]
        result = observe(232, "mssql-ees.service")
        self.assertEqual(result, {
            "service": "mssql-ees.service", "version": VERSION,
            "driver_file": "libmsodbcsql-18.5.so.1.1", "sha256": "f" * 64,
        })
        with self.assertRaisesRegex(ValueError, "identity or driver mapping changed"):
            observe(232, "mssql-ees.service")


if __name__ == "__main__":
    main()
