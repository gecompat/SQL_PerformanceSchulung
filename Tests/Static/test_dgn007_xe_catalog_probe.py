"""Regression tests for the DGN-007 XE catalog probe contract."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Tests/Runtime/dgn007_xe_catalog_probe.py"
SPEC = importlib.util.spec_from_file_location("dgn007_xe_catalog_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = probe
SPEC.loader.exec_module(probe)


def inventory() -> str:
    return "\n".join((
        "DGN007_XE|ENGINE|17|17.0.5035.5|Developer Edition (64-bit)",
        "DGN007_XE|EVENT|sql_statement_starting|statement:data,collect_statement:customizable",
        "DGN007_XE|EVENT|sql_statement_completed|statement:data,collect_statement:customizable,collect_parameterized_plan_handle:customizable,duration:data",
        "DGN007_XE|ACTION|package0|event_sequence",
        "DGN007_XE|ACTION|sqlserver|database_id",
        "DGN007_XE|ACTION|sqlserver|session_id",
        "DGN007_XE|END|1",
    ))


class Dgn007XeCatalogProbeTests(unittest.TestCase):
    def test_catalog_inventory_binds_exact_engine_and_retains_payload_field_names(self) -> None:
        result = probe.parse_catalog_output(
            inventory(), expected_major=17, expected_version="17.0.5035.5"
        )
        self.assertEqual(result["product_major_version"], 17)
        self.assertIn("statement:data", result["events"]["sql_statement_starting"])
        self.assertEqual(result["available_actions"][0], {
            "package": "package0", "name": "event_sequence",
        })
        self.assertIn("catalog metadata", result["scope"])

    def test_wrong_or_missing_engine_identity_is_rejected(self) -> None:
        for output in (
            inventory().replace("17|17.0.5035.5", "16|16.0.4305.5"),
            inventory().replace("DGN007_XE|ENGINE|17|17.0.5035.5|Developer Edition (64-bit)\n", ""),
        ):
            with self.subTest(output=output[:60]), self.assertRaises(probe.ProbeError):
                probe.parse_catalog_output(output, expected_major=17, expected_version="17.0.5035.5")

    def test_missing_required_event_is_rejected(self) -> None:
        output = inventory().replace(
            "DGN007_XE|EVENT|sql_statement_starting|statement:data,collect_statement:customizable\n", ""
        )
        with self.assertRaisesRegex(probe.ProbeError, "event metadata"):
            probe.parse_catalog_output(output, expected_major=17, expected_version="17.0.5035.5")

    def test_unexpected_action_or_malformed_field_is_rejected(self) -> None:
        for output in (
            inventory() + "\nDGN007_XE|ACTION|sqlserver|input_buffer",
            inventory().replace("statement:data", "statement:payload"),
        ):
            with self.subTest(output=output[-70:]), self.assertRaises(probe.ProbeError):
                probe.parse_catalog_output(output, expected_major=17, expected_version="17.0.5035.5")

    def test_output_is_bounded(self) -> None:
        with self.assertRaisesRegex(probe.ProbeError, "bounded"):
            probe.parse_catalog_output(
                inventory() + ("x" * probe.MAX_SQL_OUTPUT_BYTES),
                expected_major=17,
                expected_version="17.0.5035.5",
            )

    def test_truncated_or_unknown_output_is_rejected(self) -> None:
        for output in (
            inventory().replace("DGN007_XE|END|1", ""),
            inventory().replace("DGN007_XE|END|1", "DGN007_XE|OTHER|unexpected"),
        ):
            with self.subTest(output=output[-70:]), self.assertRaises(probe.ProbeError):
                probe.parse_catalog_output(output, expected_major=17, expected_version="17.0.5035.5")

    def test_password_contains_required_character_classes(self) -> None:
        for _ in range(100):
            password = probe._password()
            self.assertEqual(len(password), 32)
            self.assertRegex(password, r"[A-Z]")
            self.assertRegex(password, r"[a-z]")
            self.assertRegex(password, r"[0-9]")
            self.assertIn("!", password)

    def test_readiness_sql_suppresses_row_count_output(self) -> None:
        self.assertEqual(probe.READY_SQL, "SET NOCOUNT ON; SELECT 1;")

    def test_payload_gate_accepts_suppressed_synthetic_event_metadata(self) -> None:
        output = "\n".join((
            "DGN007_PAYLOAD|ENGINE|17|17.0.5035.5",
            "DGN007_PAYLOAD|EVENT|sql_statement_starting|2|2|0|0|0|0|0|0",
            "DGN007_PAYLOAD|EVENT|sql_statement_completed|2|2|0|0|0|0|0|0",
            "DGN007_PAYLOAD|SESSION|ABSENT",
            "DGN007_PAYLOAD|END|1",
        ))
        result = probe.parse_payload_output(output, expected_major=17, expected_version="17.0.5035.5")
        self.assertTrue(result["xe_session_removed"])
        self.assertFalse(result["raw_payload_emitted"])
        self.assertEqual(result["events"]["sql_statement_completed"]["nonempty_statement_values"], 0)

    def test_payload_gate_rejects_statement_text_and_missing_correlation(self) -> None:
        base = "\n".join((
            "DGN007_PAYLOAD|ENGINE|17|17.0.5035.5",
            "DGN007_PAYLOAD|EVENT|sql_statement_starting|2|2|0|0|0|0|0|0",
            "DGN007_PAYLOAD|EVENT|sql_statement_completed|2|2|0|0|0|0|0|0",
            "DGN007_PAYLOAD|SESSION|ABSENT",
            "DGN007_PAYLOAD|END|1",
        ))
        for output in (
            base.replace("completed|2|2|0", "completed|2|2|1"),
            base.replace("completed|2|2|0|0|0|0|0|0", "completed|2|2|0|1|0|0|0|0"),
            base.replace("DGN007_PAYLOAD|SESSION|ABSENT", "DGN007_PAYLOAD|SESSION|PRESENT"),
            base + "\nunclassified output row",
        ):
            with self.subTest(output=output), self.assertRaises(probe.ProbeError):
                probe.parse_payload_output(output, expected_major=17, expected_version="17.0.5035.5")

    def test_profile_is_exactly_bound_to_the_shared_digest_lock(self) -> None:
        expected_versions = {15: "15.0.4500.2", 16: "16.0.4305.5", 17: "17.0.5035.5"}
        for major, version in expected_versions.items():
            with self.subTest(major=major):
                self.assertEqual(probe.load_profile(major)["product_version_label"], version)
        with self.assertRaises(probe.ProbeError):
            probe.load_profile(18)

    def test_event_specific_suppression_controls_are_required(self) -> None:
        for output in (
            inventory().replace(
                "collect_statement:customizable,collect_parameterized_plan_handle:customizable,duration:data",
                "collect_statement:customizable,duration:data",
            ),
            inventory().replace(
                "sql_statement_starting|statement:data,collect_statement:customizable",
                "sql_statement_starting|statement:data",
            ),
        ):
            parsed = probe.parse_catalog_output(
                output, expected_major=17, expected_version="17.0.5035.5"
            )
            with self.subTest(output=output), self.assertRaisesRegex(
                probe.ProbeError, "suppression controls"
            ):
                probe.validate_suppression_controls(parsed)

    def test_docker_image_identity_accepts_manifest_or_config_id_but_binds_reference(self) -> None:
        profile = probe.load_profile(15)
        image = profile["image"]
        for image_id in (profile["manifest_digest"], profile["config_digest"]):
            with self.subTest(image_id=image_id):
                self.assertTrue(probe.validate_image_identity([{
                    "Id": image_id,
                    "RepoDigests": [image],
                    "Os": "linux",
                    "Architecture": "amd64",
                }], image, profile))
        self.assertFalse(probe.validate_image_identity([{
            "Id": profile["manifest_digest"],
            "RepoDigests": ["mcr.microsoft.com/mssql/server@sha256:" + "0" * 64],
            "Os": "linux",
            "Architecture": "amd64",
        }], image, profile))


if __name__ == "__main__":
    unittest.main()
