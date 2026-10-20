"""Gemeinsame I/O-Arithmetik und Parentaufnahme ohne native Prozesse."""
import ast
from contextlib import ExitStack, contextmanager
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests/Tools"))
import dgn007_handshake_channel as handshake

channel = handshake.channel


@contextmanager
def admission(*, count=3, io_steps=4096, prepare_failure=False, platform_issue=None, owner_issue=None):
    events, budgets = [], []
    selected = tuple(channel.ChannelSelection(b"pass", (), (None,) * 5 + (n,))
                     for n in range(1, count + 1))
    class Control:
        def __init__(self, namespace, guard): self.guard = guard
        def capture(self): self.check()
        def check(self): self.guard.check()
    class Reaper:
        def enable(self): events.append("REAPER")
        def restore(self): return True
    def prepare(driver, control, selections, limits):
        # Eigener Phasenstub prüft nur die Ownerreihenfolge. Vollständige echte
        # Inputsemantik bleibt den bestehenden separaten Regressionen vorbehalten.
        for n, item in enumerate(selected, 1):
            events.append(("PREFLIGHT", n))
            if prepare_failure and n == count: raise channel._Rejected("CHANNEL_INPUT")
        driver.base = selected
        if owner_issue: control.guard.issue = owner_issue
        return selected
    original = channel._Budget.reserve_worker_io
    def reserve(budget, slots):
        budgets.append(budget)
        events.append(("RESERVE", slots))
        return original(budget, slots)
    def platform():
        events.append("PLATFORM")
        if platform_issue: raise channel._Rejected(platform_issue)
    def launch(program):
        events.append("LAUNCH")
        raise channel._Rejected("CHANNEL_INPUT")
    with ExitStack() as stack:
        for target, name, value in ((channel, "_Control", Control),
            (handshake._Driver, "prepare", prepare), (channel._Budget, "reserve_worker_io", reserve),
            (channel, "_platform", platform), (channel, "_Reaper", Reaper),
            (handshake._Driver, "launch", staticmethod(launch)),
            (channel, "_no_children", lambda: True), (channel, "_cleanup", lambda *args: True)):
            stack.enter_context(patch.object(target, name, value))
        report = handshake.run_handshake_channels({}, selected, limits=channel.ChannelLimits(io_steps=io_steps))
        yield report, events, budgets


class ChildIOReservationTests(unittest.TestCase):
    def budget(self, **limits):
        return channel._Budget(channel.ChannelLimits(**limits), channel.time.monotonic_ns())

    def rejected(self, action, issue="CHANNEL_IO"):
        with self.assertRaises(channel._Rejected) as caught: action()
        self.assertEqual(caught.exception.args, (issue,))

    def tearDown(self):
        self.assertIsNone(channel._ACTIVE_OWNER)

    def test_independent_worker_literal_and_fixed_parent_value_agree(self):
        tree = ast.parse((ROOT / "Tests/Tools/dgn007_worker_input_source.py").read_bytes())
        fragment = next(node.value.value for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "_INLINE_WORKER_INPUT"
                                for target in node.targets))
        worker = ast.parse(fragment)
        cap = next(node.value.value for node in worker.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "_WORKER_INPUT_IO_CAP"
                           for target in node.targets))
        self.assertEqual(cap, 1088)
        budget = self.budget()
        budget.reserve_worker_io(1)
        self.assertEqual(budget.child_io_reserved, cap)

    def test_one_two_three_slots_reserve_exactly_and_leave_exact_parent_steps(self):
        for slots, reserved, remaining in ((1, 1088, 3008), (2, 2176, 1920), (3, 3264, 832)):
            budget = self.budget()
            budget.reserve_worker_io(slots)
            self.assertEqual((budget.child_io_reserved, budget.io), (reserved, 0))
            for _ in range(remaining): budget.step()
            self.rejected(budget.step)
            self.assertEqual((budget.io, budget.child_io_reserved), (remaining, reserved))
            self.assertEqual(budget.io + budget.child_io_reserved, 4096)

    def test_foreign_bool_and_integer_subclasses_fail_before_comparison_or_math(self):
        calls = []
        class Foreign:
            def __ge__(self, other): calls.append("COMPARE"); raise AssertionError()
            def __mul__(self, other): calls.append("MATH"); raise AssertionError()
        class Integer(int):
            def __mul__(self, other): calls.append("MATH"); raise AssertionError()
        for slots in (True, False, Integer(1), Foreign(), None, (), 0, -1, 4):
            budget = self.budget()
            self.rejected(lambda: budget.reserve_worker_io(slots))
            self.assertTrue(budget.reservation_failed)
            self.assertEqual((budget.io, budget.child_io_reserved), (0, 0))
        self.assertEqual(calls, [])

    def test_tight_limits_fail_atomically_or_leave_one_parent_step(self):
        for slots, total in ((1, 1088), (2, 2176), (3, 3264)):
            budget = self.budget(io_steps=total)
            self.rejected(lambda: budget.reserve_worker_io(slots))
            self.assertEqual((budget.child_io_reserved, budget.io), (0, 0))
            budget = self.budget(io_steps=total + 1)
            budget.reserve_worker_io(slots)
            budget.step()
            self.rejected(budget.step)
            self.assertEqual(budget.io, 1)

    def test_duplicate_reservation_preserves_amount_and_poison_all_usage(self):
        budget = self.budget()
        budget.reserve_worker_io(2)
        self.rejected(lambda: budget.reserve_worker_io(1))
        for action in (budget.check, budget.step, lambda: budget.book(b"x"), lambda: budget.progress(True),
                       lambda: budget.reserve_worker_io(3)):
            self.rejected(action)
        self.assertEqual((budget.io, budget.bytes, budget.quiet, budget.child_io_reserved), (0, 0, 0, 2176))

    def test_late_reservation_fails_and_never_refunds_or_restarts(self):
        budget = self.budget()
        budget.step()
        self.rejected(lambda: budget.reserve_worker_io(1))
        self.rejected(budget.step)
        self.rejected(lambda: budget.reserve_worker_io(1))
        self.assertEqual((budget.io, budget.child_io_reserved), (1, 0))

    def test_failed_reservation_and_parent_exhaustion_are_terminal(self):
        budget = self.budget(io_steps=1088)
        self.rejected(lambda: budget.reserve_worker_io(1))
        for action in (budget.check, budget.step, lambda: budget.book(b""), lambda: budget.progress(True)):
            self.rejected(action)
        budget = self.budget(io_steps=1089)
        budget.reserve_worker_io(1)
        budget.step()
        self.rejected(budget.step)
        self.rejected(budget.step)
        self.assertEqual((budget.io, budget.child_io_reserved), (1, 1088))

    def test_original_deadline_still_precedes_reservation_and_poison(self):
        budget = self.budget()
        budget.reserve_worker_io(1)
        self.rejected(lambda: budget.reserve_worker_io(1))
        with patch.object(channel, "time", SimpleNamespace(monotonic_ns=lambda: budget.deadline)):
            self.rejected(budget.check, "CHANNEL_TIMEOUT")
            self.rejected(budget.step, "CHANNEL_TIMEOUT")
            self.rejected(lambda: budget.reserve_worker_io(3), "CHANNEL_TIMEOUT")
        self.assertEqual((budget.io, budget.child_io_reserved), (0, 1088))

    def test_output_and_no_progress_caps_have_no_reserve_refund(self):
        budget = self.budget(output_bytes=1, no_progress=1)
        budget.reserve_worker_io(1)
        budget.book(b"x")
        self.rejected(lambda: budget.book(b"x"), "CHANNEL_BYTES")
        self.rejected(lambda: budget.progress(False), "CHANNEL_STALLED")
        self.assertEqual((budget.bytes, budget.quiet, budget.child_io_reserved), (2, 1, 1088))

    def test_public_parent_rejects_insufficient_cohort_before_all_native_effects(self):
        with admission(io_steps=3264) as (report, events, budgets):
            self.assertEqual(report.issue, "CHANNEL_IO")
            self.assertEqual(events, [("PREFLIGHT", 1), ("PREFLIGHT", 2), ("PREFLIGHT", 3), ("RESERVE", 3)])
            self.assertEqual((report.channels.start_attempts, report.channels.io_steps,
                              report.channels.child_io_reserved), (0, 0, 0))
            self.assertTrue(budgets[0].reservation_failed)

    def test_public_parent_books_entire_cohort_before_first_start_and_later_preflight(self):
        with admission() as (report, events, budgets):
            self.assertEqual(events[:6], [("PREFLIGHT", 1), ("PREFLIGHT", 2), ("PREFLIGHT", 3),
                                          ("RESERVE", 3), "PLATFORM", "REAPER"])
            self.assertEqual(events[6:], ["LAUNCH"])
            self.assertEqual((report.issue, report.channels.start_attempts, report.channels.started,
                              report.channels.child_io_reserved), ("CHANNEL_CLEANUP", 1, 0, 3264))
            self.assertFalse(report.channels.cleanup_complete)
            self.assertEqual(budgets[0].child_io_reserved, 3264)
        with admission(prepare_failure=True) as (report, events, budgets):
            self.assertEqual((report.issue, report.channels.start_attempts), ("CHANNEL_INPUT", 0))
            self.assertEqual(events, [("PREFLIGHT", 1), ("PREFLIGHT", 2), ("PREFLIGHT", 3)])
            self.assertEqual(budgets, [])

    def test_platform_owner_and_plain_session_diagnostics_keep_original_boundaries(self):
        with admission(count=1, platform_issue="CHANNEL_PLATFORM") as (report, events, budgets):
            self.assertEqual((report.issue, report.channels.start_attempts,
                              report.channels.child_io_reserved), ("CHANNEL_PLATFORM", 0, 1088))
            self.assertFalse(report.runtime_attested or report.trust_attested
                             or report.import_used_bytes_attested or report.method_approved)
        with admission(owner_issue="CHANNEL_REENTRANT") as (report, events, budgets):
            self.assertEqual((report.issue, report.channels.first_issue,
                              report.channels.start_attempts), ("CHANNEL_REENTRANT", "CHANNEL_REENTRANT", 0))
            self.assertEqual(budgets, [])
        budget = self.budget(io_steps=2)
        budget.step(); budget.step()
        self.rejected(budget.step)
        self.assertEqual((budget.io, budget.child_io_reserved), (2, 0))
        self.assertEqual(channel.ChannelReport("REJECTED_SESSION_CHANNELS", "CHANNEL_OWNER", "CHANNEL_OWNER").child_io_reserved, 0)


if __name__ == "__main__":
    unittest.main()
