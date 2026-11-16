#!/usr/bin/env python3
"""Synthetic checks for contract-bound DGN-007 source snapshots."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Tests" / "Static"))
from Tests.Runtime import dgn007_source_freeze as freeze
from validate_dgn007_prospective_acceptance import AUTOMATED, CONTRACT
from Tests.Contracts.dgn007_prospective_acceptance import contract_from_mapping, SOURCE_FILES


class SourceFreezeTests(unittest.TestCase):
    def setUp(self):
        self.contract = contract_from_mapping(json.loads(CONTRACT.read_text(encoding="utf-8")))

    def test_captures_the_complete_pinned_set(self):
        snapshot = freeze.capture_source_snapshot(ROOT, self.contract)
        self.assertEqual(tuple(name for name, _ in snapshot.hashes), SOURCE_FILES)
        self.assertTrue(freeze.verify_source_freeze(snapshot, snapshot, self.contract))

    def test_rejects_changed_source_bytes_and_unpinned_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated"
            target.mkdir(parents=True)
            for name in SOURCE_FILES:
                (target / name).write_bytes((AUTOMATED / name).read_bytes())
            before = freeze.capture_source_snapshot(root, self.contract)
            (target / SOURCE_FILES[0]).write_bytes((target / SOURCE_FILES[0]).read_bytes() + b"\n")
            with self.assertRaises(freeze.SourceFreezeError):
                freeze.capture_source_snapshot(root, self.contract)
            after = freeze.SourceSnapshot(self.contract.source_digest,
                                          tuple((n, "0" * 64) for n in SOURCE_FILES))
            self.assertFalse(freeze.verify_source_freeze(before, after, self.contract))


if __name__ == "__main__":
    unittest.main()
