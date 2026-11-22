"""Regression tests for the DGN-004 qualification workflow contract."""
from __future__ import annotations

import unittest

from validate_dgn004_runtime_workflow import validate


class Dgn004RuntimeWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        cls.workflow = (root / ".github/workflows/dgn004-runtime-qualification.yml").read_text(encoding="utf-8")
        cls.container = (root / "Tests/Runtime/dgn004_container.py").read_text(encoding="utf-8")

    def test_pinned_sequential_build_jobs_are_accepted(self) -> None:
        self.assertEqual(validate(self.workflow, self.container), [])

    def test_parallelism_and_timeout_expansion_are_rejected(self) -> None:
        changed = self.workflow.replace("max-parallel: 1", "max-parallel: 2").replace(
            "timeout-minutes: 30", "timeout-minutes: 60",
        )
        self.assertTrue(validate(changed, self.container))

    def test_digest_drift_and_unsupported_2019_scope_are_rejected(self) -> None:
        changed = self.workflow.replace(
            "sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89",
            "sha256:" + "0" * 64,
        ).replace("build: '2025'", "build: '2019'\n            image: 'mcr.microsoft.com/mssql/server:2019-latest'\n          - build: '2025'", 1)
        self.assertTrue(validate(changed, self.container))

    def test_direct_unowned_cleanup_is_rejected(self) -> None:
        self.assertTrue(validate(self.workflow + "\nrun: docker rm -f $(docker ps -q)\n", self.container))

    def test_pull_request_trigger_is_rejected(self) -> None:
        changed = self.workflow.replace("  workflow_dispatch:", "  pull_request:\n    types: [opened]\n  workflow_dispatch:")
        self.assertTrue(validate(changed, self.container))

    def test_push_trigger_is_rejected(self) -> None:
        changed = self.workflow.replace("  workflow_dispatch:", "  push:\n    branches: [main]\n  workflow_dispatch:")
        self.assertTrue(validate(changed, self.container))


if __name__ == "__main__":
    unittest.main()
