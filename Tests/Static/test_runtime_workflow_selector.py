#!/usr/bin/env python3
"""Positive, negative, shared-dependency and unknown-input selector controls."""

from __future__ import annotations

import subprocess
import re
import unittest
from unittest.mock import patch

import select_runtime_workflow as selector


class RuntimeSelectorTests(unittest.TestCase):
    def test_dgn010_runtime_consumed_records_select_native_but_tests_stay_static(self) -> None:
        workflow=selector.WORKFLOWS['sql2025-ai-local'];patterns=selector.trigger_paths(workflow)
        for path in ('Tests/Static/dgn010_window_evidence.py','Tests/Static/dgn010_benchmark_evidence.py','Tests/Static/Fixtures/dgn010/DGN010_DML.result-contract.json'):
            with self.subTest(path=path):
                self.assertTrue(selector.select_runtime({path},patterns,workflow,runtime_job_changed=False))
        self.assertFalse(selector.select_runtime({'Tests/Static/test_dgn010_profile.py'},patterns,workflow,runtime_job_changed=False))

    def test_full_privacy_scan_has_one_ci_owner(self) -> None:
        owners = []
        for path in (selector.ROOT / ".github/workflows").glob("*.yml"):
            body = path.read_text(encoding="utf-8")
            if re.search(r"(?m)^\s+(?:run: )?python3? Tests/Static/validate_privacy_metadata\.py\b", body):
                owners.append(path.name)
        self.assertEqual(owners, ["privacy-metadata.yml"])

    def test_every_selected_workflow_has_parseable_inputs_and_runtime_body(self) -> None:
        for name, workflow in selector.WORKFLOWS.items():
            with self.subTest(workflow=workflow):
                self.assertTrue(selector.trigger_paths(workflow))
                text = (selector.ROOT / workflow).read_text(encoding="utf-8")
                self.assertTrue(selector.runtime_block(text))
                self.assertIn("  changes:\n", text)
                self.assertIn("fetch-depth: 0", text)
                self.assertIn(f"--workflow {name} --event", text)
                expected_needs = "    needs: [static, changes]\n"
                self.assertIn(expected_needs, text)
                self.assertIn("    if: needs.changes.outputs.run_runtime == 'true'\n", text)

    def test_runtime_body_ignores_scheduling_but_detects_execution_change(self) -> None:
        before = "  runtime:\n    needs: static\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo old\n"
        after = before.replace("needs: static", "needs: [static, changes]")
        self.assertEqual(selector.runtime_block(before), selector.runtime_block(after))
        self.assertNotEqual(selector.runtime_block(before), selector.runtime_block(after.replace("echo old", "echo new")))

    def test_dgn007_static_workflow_edit_does_not_claim_runtime(self) -> None:
        workflow = selector.WORKFLOWS["dgn007"]
        self.assertFalse(selector.select_runtime(
            {workflow, "Tests/Static/validate_dgn007_automated_setup.py", ".ai/PROJECT_RULES.md"}, selector.trigger_paths(workflow),
            workflow, runtime_job_changed=False,
        ))
        self.assertTrue(selector.select_runtime(
            {workflow}, selector.trigger_paths(workflow), workflow,
            runtime_job_changed=True,
        ))

    def test_dgn007_sql_and_shared_tool_changes_select_runtime(self) -> None:
        workflow = selector.WORKFLOWS["dgn007"]
        patterns = selector.trigger_paths(workflow)
        for path in (
            "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/20_Query_Store_Windows.sql",
            "Demos/00_Framework/Tools/run_demo.py",
            "Tests/Runtime/execution_target.py",
        ):
            with self.subTest(path=path):
                self.assertTrue(selector.select_runtime(
                    {path}, patterns, workflow, runtime_job_changed=False,
                ))

    def test_framework_excludes_unrelated_demo_runner_but_keeps_common_dependency(self) -> None:
        workflow = selector.WORKFLOWS["framework"]
        patterns = selector.trigger_paths(workflow)
        self.assertFalse(selector.select_runtime(
            {"Tests/Runtime/run_dgn007_automated_setup.py"}, patterns,
            workflow, runtime_job_changed=False,
        ))
        self.assertTrue(selector.select_runtime(
            {"Tests/Runtime/docker_sqlcmd_proxy.py"}, patterns,
            workflow, runtime_job_changed=False,
        ))

    def test_static_oracle_change_is_static_validation_without_qualification_claim(self) -> None:
        workflow = selector.WORKFLOWS["adv008-opt009"]
        patterns = selector.trigger_paths(workflow)
        self.assertFalse(selector.select_runtime(
            {"Tests/Static/validate_adv008_opt009.py"}, patterns,
            workflow, runtime_job_changed=False,
        ))
        self.assertTrue(selector.select_runtime(
            {"Demos/00_Framework/Tools/run_demo.py"}, patterns,
            workflow, runtime_job_changed=False,
        ))

    def test_pilot_and_coverage_filters_exclude_unrelated_dgn007(self) -> None:
        path = "Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/20_Query_Store_Windows.sql"
        for name in ("dgn003-dgn005-pilots", "w-cov-001"):
            workflow = selector.WORKFLOWS[name]
            with self.subTest(workflow=name):
                self.assertFalse(selector.select_runtime(
                    {path}, selector.trigger_paths(workflow), workflow,
                    runtime_job_changed=False,
                ))

    def test_setup_ownership_selects_only_actual_runtime_inputs(self) -> None:
        workflow = selector.WORKFLOWS['setup-ownership']
        patterns = selector.trigger_paths(workflow)
        for path in (
            'Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/10_Setup.sql',
            'Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/90_Cleanup.sql',
            'Tests/Runtime/setup_ownership.py',
            'Tests/Runtime/cleanup_ownership.py',
            'Tests/Runtime/execution_target.py',
            'Demos/00_Framework/Tools/sqlcmd_process.py',
        ):
            with self.subTest(path=path):
                self.assertTrue(selector.select_runtime({path}, patterns, workflow, runtime_job_changed=False))
        for path in (
            'Tests/Static/test_setup_ownership.py',
            'Tests/Static/test_runtime_workflow_selector.py',
            'Demos/04_Optimizer_Statistics_Plans/OPT-002_Statistics_Anatomy/README.md',
            'Demos/04_Optimizer_Statistics_Plans/OPT-003_Sampling_And_Skew/10_Setup.sql',
        ):
            with self.subTest(path=path):
                self.assertFalse(selector.select_runtime({path}, patterns, workflow, runtime_job_changed=False))
        self.assertTrue(selector.select_runtime({workflow}, patterns, workflow, runtime_job_changed=True))

    def test_framework_ownership_runtime_dependencies_and_pure_oracle(self) -> None:
        workflow = selector.WORKFLOWS['framework']
        patterns = selector.trigger_paths(workflow)
        for path in ('Tests/Runtime/framework_ownership.py', 'Tests/Runtime/framework_inputs.py', 'Tests/Runtime/cleanup_ownership.py'):
            self.assertTrue(selector.select_runtime({path}, patterns, workflow, runtime_job_changed=False))
        self.assertFalse(selector.select_runtime({'Tests/Static/test_framework_ownership.py'}, patterns, workflow, runtime_job_changed=False))
        self.assertFalse(selector.select_runtime({'Tests/Static/test_framework_inputs.py'}, patterns, workflow, runtime_job_changed=False))

    def test_unknown_binding_and_missing_git_object_fail_closed(self) -> None:
        workflow = selector.WORKFLOWS["dgn007"]
        self.assertEqual(selector.decide(workflow, "pull_request", "", ""),
                         (True, "unknown event or revision binding"))
        with patch.object(selector, "git_bytes", side_effect=subprocess.CalledProcessError(1, "git")):
            selected, _ = selector.decide(workflow, "pull_request", "a" * 40, "b" * 40)
        self.assertTrue(selected)
        self.assertTrue(selector.decide(workflow, "workflow_dispatch", "", "")[0])

    def test_old_trigger_is_kept_during_selector_change(self) -> None:
        workflow = selector.WORKFLOWS["framework"]
        old = "  pull_request:\n    paths:\n      - 'Tests/Runtime/**'\n  runtime:\n    runs-on: ubuntu-latest\n"
        new = "  pull_request:\n    paths:\n      - 'Tests/Runtime/execution_target.py'\n  runtime:\n    runs-on: ubuntu-latest\n"
        with patch.object(selector, "git_bytes", side_effect=[
            b"Tests/Runtime/run_dgn007_automated_setup.py\0", old.encode(), new.encode(),
        ]):
            selected, _ = selector.decide(workflow, "pull_request", "a" * 40, "b" * 40)
        self.assertTrue(selected)


if __name__ == "__main__":
    unittest.main()
