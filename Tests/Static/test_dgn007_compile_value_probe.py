import os
import unittest
from unittest.mock import patch

from Tests.Runtime import run_dgn007_compile_value_probe as probe


class CompileProbeTests(unittest.TestCase):
    @patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic"}, clear=True)
    def test_independent_absence_is_still_checked_after_cleanup_failure(self):
        outputs = ["EMPTY_DEVELOPER", probe.SETUP_SUMMARY, probe.SUMMARY,
                   probe.runner.RunnerFailure("NOT_PROVEN"), "ABSENT"]
        with patch.object(probe.runner, "resolve_target", return_value=object()), \
             patch.object(probe, "_batch", side_effect=outputs) as run:
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "FAIL_CLEANUP"):
                probe.run_probe("synthetic-container")
        self.assertEqual(run.call_args.args[1], probe.ABSENCE)

    @patch.dict(os.environ, {"SQLCMDPASSWORD": "synthetic"}, clear=True)
    def test_wrong_target_is_not_modified(self):
        with patch.object(probe.runner, "resolve_target", return_value=object()), \
             patch.object(probe, "_batch", return_value="NOT_EMPTY") as run:
            with self.assertRaisesRegex(probe.runner.RunnerFailure, "NOT_PROVEN"):
                probe.run_probe("synthetic-container")
        run.assert_called_once()
        self.assertEqual(run.call_args.args[1], probe.PREFLIGHT)


if __name__ == "__main__":
    unittest.main()
