#!/usr/bin/env python3
"""Synthetic regression tests for the QRY-023 image-lock matrix resolver."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import qry023_image_matrix as resolver  # noqa: E402


class Qry023ImageMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = json.loads(resolver.LOCK.read_text(encoding="utf-8"))

    def test_fixed_profiles_resolve_to_exact_workflow_shape(self) -> None:
        self.assertEqual(
            [(item["year"], item["major"], item["image"]) for item in resolver.resolve(self.lock)],
            [
                (2019, 15, self.lock["profiles"][0]["image"]),
                (2022, 16, self.lock["profiles"][1]["image"]),
                (2025, 17, self.lock["profiles"][2]["image"]),
            ],
        )

    def test_rejects_changed_image_digest(self) -> None:
        changed = copy.deepcopy(self.lock)
        changed["profiles"][0]["image"] = "mcr.microsoft.com/mssql/server@sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "does not match"):
            resolver.resolve(changed)

    def test_rejects_reordered_or_duplicate_major(self) -> None:
        reordered = copy.deepcopy(self.lock)
        reordered["profiles"][0], reordered["profiles"][1] = (
            reordered["profiles"][1], reordered["profiles"][0]
        )
        with self.assertRaisesRegex(ValueError, "does not match"):
            resolver.resolve(reordered)

    def test_rejects_runtime_authorization_escalation(self) -> None:
        changed = copy.deepcopy(self.lock)
        changed["runtime_authorized"] = True
        with self.assertRaisesRegex(ValueError, "non-authorizing"):
            resolver.resolve(changed)

    def test_rejects_missing_or_additional_profiles(self) -> None:
        for profiles in (self.lock["profiles"][:-1], self.lock["profiles"] + [self.lock["profiles"][-1]]):
            changed = copy.deepcopy(self.lock)
            changed["profiles"] = profiles
            with self.subTest(count=len(profiles)), self.assertRaisesRegex(ValueError, "exactly three"):
                resolver.resolve(changed)

    def test_cli_emits_only_the_resolved_matrix_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "github-output.txt"
            self.assertEqual(resolver.main(["qry023_image_matrix.py", str(output)]), 0)
            line = output.read_text(encoding="utf-8").strip()
        key, value = line.split("=", 1)
        self.assertEqual(key, "matrix")
        self.assertEqual(
            json.loads(value),
            {"include": resolver.resolve(self.lock)},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
