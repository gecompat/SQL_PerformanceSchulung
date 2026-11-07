#!/usr/bin/env python3
"""Regression checks for the offline QRY-023 proposed-harness validator."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import validate_qry023_proposed_harness as validator


class Qry023ProposedHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.demo = self.root / "Demos/05_Query_Patterns/QRY-023_Graph_Tables"
        shutil.copytree(validator.DEMO, self.demo)
        (self.root / "Documentation/Demo_Catalog").mkdir(parents=True)
        (self.root / "Tests/Lab").mkdir(parents=True)
        shutil.copy2(validator.ROOT / "Documentation/Demo_Catalog/demo_execution_paths.json",
                     self.root / "Documentation/Demo_Catalog/demo_execution_paths.json")
        shutil.copy2(validator.ROOT / "Tests/Lab/performance-lab-matrix.json",
                     self.root / "Tests/Lab/performance-lab-matrix.json")

    def errors(self) -> list[str]:
        return validator.validate(self.demo, self.root)

    def test_current_draft_satisfies_offline_contract(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_catalog_manifest_is_rejected(self) -> None:
        (self.demo / "manifest.json").write_text("{}", encoding="utf-8")
        self.assertTrue(any("catalog manifest.json" in error for error in self.errors()))

    def test_missing_required_cleanup_phase_is_rejected(self) -> None:
        path = self.demo / "manifest.proposed.json"
        text = path.read_text(encoding="utf-8").replace('"required":true,"require_summary":true,"timeout_seconds":90',
                                                       '"required":false,"require_summary":true,"timeout_seconds":90')
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("cleanup must be required" in error for error in self.errors()))

    def test_cleanup_without_run_token_marker_is_rejected(self) -> None:
        path = self.demo / "90_Cleanup.sql"
        path.write_text(path.read_text(encoding="utf-8").replace("SQLPERF.RunToken", "SQLPERF.OtherToken"),
                        encoding="utf-8")
        self.assertTrue(any("cleanup must bind the sqlperf.runtoken" in error for error in self.errors()))


if __name__ == "__main__":
    unittest.main()
