from __future__ import annotations

import unittest

from res003_memory_signal_contract import (
    MemorySignalSample,
    Phase,
    Verdict,
    evaluate_memory_signals,
)


TOKEN = "synthetic-run-3"
START = "2026-11-07T09:59:00Z"
END = "2026-11-07T10:02:00Z"


def fixture(pressure_process: bool = True, pressure_system: bool = False,
            recovery_process: bool = False, recovery_system: bool = False):
    return (
        MemorySignalSample(TOKEN, Phase.BASELINE, "2026-11-07T10:00:00Z", False, False),
        MemorySignalSample(TOKEN, Phase.PRESSURE, "2026-11-07T10:01:00Z", pressure_process, pressure_system),
        MemorySignalSample(TOKEN, Phase.RECOVERY, "2026-11-07T10:02:00Z", recovery_process, recovery_system),
    )


class MemorySignalContractTests(unittest.TestCase):
    def test_process_signal_transition_and_recovery_pass(self):
        result = evaluate_memory_signals(TOKEN, fixture(), START, "2026-11-07T10:03:00Z")
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertTrue(result.process_low_observed)
        self.assertFalse(result.system_low_observed)
        self.assertTrue(result.recovery_signals_clear)

    def test_system_signal_transition_passes_independently(self):
        result = evaluate_memory_signals(TOKEN, fixture(False, True), START, "2026-11-07T10:03:00Z")
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertFalse(result.process_low_observed)
        self.assertTrue(result.system_low_observed)

    def test_both_signals_remain_separately_visible(self):
        result = evaluate_memory_signals(TOKEN, fixture(True, True), START, "2026-11-07T10:03:00Z")
        self.assertEqual(result.verdict, Verdict.PASS)
        self.assertTrue(result.process_low_observed)
        self.assertTrue(result.system_low_observed)

    def test_no_pressure_signal_is_not_proven(self):
        self.assertEqual(evaluate_memory_signals(TOKEN, fixture(False, False), START, "2026-11-07T10:03:00Z").verdict, Verdict.NOT_PROVEN)

    def test_missing_samples_are_not_proven(self):
        self.assertEqual(evaluate_memory_signals(TOKEN, None, START, END).verdict, Verdict.NOT_PROVEN)

    def test_incomplete_phase_set_is_not_proven(self):
        self.assertEqual(evaluate_memory_signals(TOKEN, fixture()[:2], START, END).verdict, Verdict.NOT_PROVEN)

    def test_pressure_still_present_in_recovery_is_not_proven(self):
        result = evaluate_memory_signals(TOKEN, fixture(recovery_system=True), START, "2026-11-07T10:03:00Z")
        self.assertEqual(result.verdict, Verdict.NOT_PROVEN)
        self.assertFalse(result.recovery_signals_clear)

    def test_baseline_pressure_is_not_a_new_transition(self):
        samples = list(fixture())
        samples[0] = MemorySignalSample(TOKEN, Phase.BASELINE, samples[0].captured_at, True, False)
        self.assertEqual(evaluate_memory_signals(TOKEN, tuple(samples), START, "2026-11-07T10:03:00Z").verdict, Verdict.NOT_PROVEN)

    def test_run_token_mismatch_fails(self):
        samples = list(fixture())
        samples[1] = MemorySignalSample("other-run", Phase.PRESSURE, samples[1].captured_at, True, False)
        self.assertEqual(evaluate_memory_signals(TOKEN, tuple(samples), START, "2026-11-07T10:03:00Z").verdict, Verdict.FAIL)

    def test_duplicate_phase_is_not_proven(self):
        samples = fixture()
        duplicate = (samples[0], samples[1], MemorySignalSample(TOKEN, Phase.PRESSURE, samples[2].captured_at, False, False))
        self.assertEqual(evaluate_memory_signals(TOKEN, duplicate, START, "2026-11-07T10:03:00Z").verdict, Verdict.NOT_PROVEN)

    def test_unknown_phase_value_fails(self):
        samples = list(fixture())
        samples[1] = MemorySignalSample(TOKEN, "during", samples[1].captured_at, True, False)
        self.assertEqual(evaluate_memory_signals(TOKEN, tuple(samples), START, "2026-11-07T10:03:00Z").verdict, Verdict.FAIL)

    def test_phase_timestamps_must_be_strictly_ordered(self):
        samples = fixture()
        unordered = (
            MemorySignalSample(TOKEN, Phase.BASELINE, "2026-11-07T10:01:00Z", False, False),
            MemorySignalSample(TOKEN, Phase.PRESSURE, "2026-11-07T10:00:00Z", True, False),
            samples[2],
        )
        self.assertEqual(evaluate_memory_signals(TOKEN, unordered, START, "2026-11-07T10:03:00Z").verdict, Verdict.FAIL)

    def test_capture_outside_window_fails(self):
        self.assertEqual(evaluate_memory_signals(TOKEN, fixture(), "2026-11-07T10:00:30Z", "2026-11-07T10:03:00Z").verdict, Verdict.FAIL)

    def test_boolean_flags_require_exact_bool(self):
        samples = list(fixture())
        samples[1] = MemorySignalSample(TOKEN, Phase.PRESSURE, samples[1].captured_at, 1, False)
        self.assertEqual(evaluate_memory_signals(TOKEN, tuple(samples), START, "2026-11-07T10:03:00Z").verdict, Verdict.FAIL)

    def test_bad_timestamp_fails(self):
        samples = list(fixture())
        samples[2] = MemorySignalSample(TOKEN, Phase.RECOVERY, "not-a-time", False, False)
        self.assertEqual(evaluate_memory_signals(TOKEN, tuple(samples), START, END).verdict, Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
