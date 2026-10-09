"""Begrenzte synthetische Budget-/Linux-Prozessgegenproben; keine SQL-Runtime."""

import ast
from dataclasses import FrozenInstanceError, replace
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch


PATH = Path(__file__).resolve().parents[1] / "Tools" / "dgn007_streaming_budget_prototype.py"
spec = importlib.util.spec_from_file_location("streaming_budget_prototype", PATH)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class Clock:
    def __init__(self):
        self.value = 0

    def __call__(self):
        return self.value


GOOD = m.CleanupReceipt(True, True, True, True, True, True)


def complete():
    return [m.Step("stdout", b"hello\r\n", True, input_complete=True),
            m.Step("stderr", b"", True, m.Exit.SUCCESS, True)]


class Adapter:
    def __init__(self, clock, steps=None, costs=None, cleanup=GOOD):
        self.clock = clock
        self.steps = iter(complete() if steps is None else steps)
        self.costs = iter(() if costs is None else costs)
        self.receipt = cleanup
        self.calls = []
        self.cleanup_cost = 0
        self.start_cost = 0

    def start(self, data):
        self.calls.append(("start", len(data)))
        self.clock.value += self.start_cost

    def step(self, maximum):
        self.calls.append(("step", maximum))
        self.clock.value += next(self.costs, 0)
        return next(self.steps, m.Step())

    def pause(self, ns):
        self.calls.append(("pause", ns))
        self.clock.value += ns

    def cleanup(self, deadline):
        self.calls.append(("cleanup", deadline))
        self.clock.value += self.cleanup_cost
        return self.receipt


class CoreTests(unittest.TestCase):
    def run_case(self, steps=None, limits=m.Limits(), costs=None, cleanup=GOOD, data=b"input"):
        clock = Clock()
        adapter = Adapter(clock, steps, costs, cleanup)
        return m.run_budget(adapter, clock, data, limits), adapter

    def issue(self, issue, *args, **kwargs):
        result, adapter = self.run_case(*args, **kwargs)
        self.assertFalse(result.success)
        self.assertIn(issue, result.issues)
        self.assertEqual(adapter.calls[-1][0], "cleanup")
        return result, adapter

    def test_positive_explicit_both_eof_and_fixed_scope(self):
        result, _ = self.run_case()
        self.assertTrue(result.success)
        self.assertEqual(result.observed_bytes, 7)
        self.assertEqual(result.retained_bytes, 7)
        self.assertTrue(result.stdout_eof and result.stderr_eof and result.input_written)
        self.assertEqual(result.scope, "PROJECT_SEMANTIC")
        self.assertFalse(result.runtime_attested or result.method_approved)

    def test_input_limit_before_start(self):
        for value in (b"i" * (m.MAX_INPUT + 1), bytearray(b"x"), None):
            result, adapter = self.run_case(data=value)
            self.assertEqual(result.issues, (m.Issue.INPUT,))
            self.assertEqual(adapter.calls, [])

    def test_input_exact_limit(self):
        result, adapter = self.run_case(data=b"i" * m.MAX_INPUT)
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0], ("start", m.MAX_INPUT))

    def test_global_cross_channel_exact_cap(self):
        steps = [m.Step("stdout", b"abc", True, input_complete=True),
                 m.Step("stderr", b"de", True, m.Exit.SUCCESS, True)]
        result, _ = self.run_case(steps, replace(m.Limits(), output_bytes=5))
        self.assertTrue(result.success)
        self.assertEqual(result.retained_bytes, 5)

    def test_cap_plus_one_before_decode_and_retention(self):
        steps = [m.Step("stdout", b"abc", True), m.Step("stderr", b"de\xff")]
        result, adapter = self.issue(m.Issue.OUTPUT, steps, replace(m.Limits(), output_bytes=5))
        self.assertEqual((result.observed_bytes, result.retained_bytes), (6, 3))
        self.assertNotIn(m.Issue.TEXT, result.issues)
        self.assertEqual(adapter.calls[2], ("step", 3))

    def test_oversized_adapter_read_rejected(self):
        result, _ = self.issue(m.Issue.INVALID, [m.Step("stdout", b"x" * 5)],
                               replace(m.Limits(), read_bytes=4))
        self.assertEqual(result.retained_bytes, 0)

    def test_split_utf8_and_crlf(self):
        steps = [m.Step("stdout", x) for x in (b"\xe2", b"\x82", b"\xac\r", b"\n")]
        steps += [m.Step("stdout", eof=True), m.Step("stderr", eof=True, exit=m.Exit.SUCCESS, input_complete=True)]
        result, _ = self.run_case(steps, replace(m.Limits(), line_bytes=4))
        self.assertTrue(result.success)
        self.assertEqual(result.retained_bytes, 5)

    def test_truncated_utf8_at_eof(self):
        self.issue(m.Issue.TEXT, [m.Step("stdout", b"\xe2"), m.Step("stdout", eof=True)])

    def test_invalid_utf8(self):
        self.issue(m.Issue.TEXT, [m.Step("stderr", b"\xff")])

    def test_line_limit_across_chunks(self):
        self.issue(m.Issue.LINE, [m.Step("stdout", b"123"), m.Step("stdout", b"45")],
                   replace(m.Limits(), line_bytes=4))

    def test_line_limit_exact_with_newline(self):
        steps = [m.Step("stdout", b"1234\n", True), m.Step("stderr", eof=True, exit=m.Exit.SUCCESS, input_complete=True)]
        self.assertTrue(self.run_case(steps, replace(m.Limits(), line_bytes=4))[0].success)

    def test_data_after_eof_rejected(self):
        self.issue(m.Issue.INVALID, [m.Step("stdout", eof=True), m.Step("stdout", b"x")])

    def test_exit_does_not_establish_drain(self):
        self.issue(m.Issue.STEPS, [m.Step(exit=m.Exit.SUCCESS, input_complete=True)] * 4,
                   replace(m.Limits(), io_steps=4))

    def test_repeated_exit_and_input_receipts_are_not_new_progress(self):
        result, _ = self.issue(m.Issue.STALLED,
                               [m.Step(exit=m.Exit.SUCCESS, input_complete=True)] * 8,
                               replace(m.Limits(), no_progress_steps=2))
        self.assertEqual(result.io_steps, 4)

    def test_one_eof_not_success(self):
        self.issue(m.Issue.STEPS, [m.Step("stdout", eof=True, exit=m.Exit.SUCCESS, input_complete=True)] +
                   [m.Step(exit=m.Exit.SUCCESS, input_complete=True)] * 3, replace(m.Limits(), io_steps=4))

    def test_uncompleted_writer_not_success(self):
        self.issue(m.Issue.STEPS, [m.Step("stdout", eof=True), m.Step("stderr", eof=True, exit=m.Exit.SUCCESS)],
                   replace(m.Limits(), io_steps=2))

    def test_child_failure(self):
        self.issue(m.Issue.CHILD, [m.Step(exit=m.Exit.FAILURE)])

    def test_stationary_clock_finite_no_progress_cap(self):
        result, _ = self.issue(m.Issue.STALLED, limits=replace(m.Limits(), no_progress_steps=3), steps=[])
        self.assertEqual(result.io_steps, 4)

    def test_io_limit_independent_of_semantic_polls(self):
        steps = [m.Step("stdout", b"x\n")] * 5
        result, _ = self.issue(m.Issue.STEPS, steps, replace(m.Limits(), io_steps=4))
        self.assertEqual(result.semantic_polls, 0)

    def test_semantic_poll_limit_counts_failures(self):
        steps = [m.Step("stdout", b"x\n", semantic_poll=True)] * 65
        result, _ = self.issue(m.Issue.POLLS, steps)
        self.assertEqual(result.semantic_polls, 65)

    def test_acquisition_attempt_limit_no_reset(self):
        steps = [m.Step("stdout", b"x\n", acquisition_stage=1)] * 3
        result, _ = self.issue(m.Issue.ATTEMPTS, steps)
        self.assertEqual(result.acquisitions, 3)

    def test_coupled_sixteen_acquisitions_exceed_global_bytes(self):
        chunk = (b"x" * 4095 + b"\n") * 4
        class Bounded(Adapter):
            def step(self, maximum):
                value = super().step(maximum)
                return replace(value, data=value.data[:maximum])
        clock = Clock()
        adapter = Bounded(clock, [m.Step("stdout", chunk, acquisition_stage=i // 2 + 1) for i in range(16)])
        result = m.run_budget(adapter, clock, b"x")
        self.assertIn(m.Issue.OUTPUT, result.issues)
        self.assertEqual(result.observed_bytes, m.MAX_OUTPUT + 1)
        self.assertEqual(result.retained_bytes, m.MAX_OUTPUT)

    def test_coupled_acquisition_cost_exceeds_global_active(self):
        steps = [m.Step("stdout", b"x\n", acquisition_stage=i // 2 + 1) for i in range(16)]
        result, _ = self.issue(m.Issue.COST, steps, costs=[2 * m.NS] * 16)
        self.assertEqual(result.acquisitions, 11)
        self.assertNotIn(m.Issue.ACQUIRE_COST, result.issues)

    def test_acquisition_cost_limit(self):
        self.issue(m.Issue.ACQUIRE_COST, [m.Step(acquisition_stage=1)], costs=[2 * m.NS + 1])

    def test_sleep_elapsed_separate_from_active(self):
        steps = [m.Step(semantic_poll=True, sleep_ns=m.NS)] + complete()
        result, _ = self.run_case(steps, costs=[7, 11, 13])
        self.assertTrue(result.success)
        self.assertEqual(result.active_ns, 31)
        self.assertEqual(result.sleep_ns, m.NS)
        self.assertEqual(result.elapsed_ns, m.NS + 31)

    def test_deadline_never_reset_by_sleep_retry_or_drain(self):
        steps = [m.Step(semantic_poll=True, sleep_ns=m.NS, acquisition_stage=1)] * 2 + complete()
        result, _ = self.issue(m.Issue.TIMEOUT, steps, replace(m.Limits(), phase_ns=2 * m.NS))
        self.assertEqual(result.acquisitions, 2)
        self.assertEqual(result.sleep_ns, 2 * m.NS)

    def test_exact_deadline_before_success_is_timeout(self):
        self.issue(m.Issue.TIMEOUT, complete(), replace(m.Limits(), phase_ns=100), costs=[0, 100])

    def test_regular_deadline_can_be_tighter(self):
        self.issue(m.Issue.TIMEOUT, complete(), replace(m.Limits(), regular_ns=100), costs=[0, 100])

    def test_start_cost_part_of_active_and_deadline(self):
        clock = Clock()
        adapter = Adapter(clock)
        adapter.start_cost = 100
        result = m.run_budget(adapter, clock, b"", replace(m.Limits(), phase_ns=100))
        self.assertIn(m.Issue.TIMEOUT, result.issues)
        self.assertEqual(result.active_ns, 100)
        self.assertFalse(any(call[0] == "step" for call in adapter.calls))

    def test_cleanup_failure_dominates_timeout(self):
        result, _ = self.issue(m.Issue.TIMEOUT, complete(), replace(m.Limits(), phase_ns=1),
                               costs=[1], cleanup=replace(GOOD, absent=False))
        self.assertEqual(result.issues[0], m.Issue.CLEANUP)

    def test_each_cleanup_receipt_boundary_sticky(self):
        for field in GOOD.__dataclass_fields__:
            with self.subTest(field=field):
                self.issue(m.Issue.CLEANUP, cleanup=replace(GOOD, **{field: False}))
        # Successful recovery receipts cannot heal a failed initial cleanup.
        self.issue(m.Issue.CLEANUP, cleanup=replace(GOOD, initial_success=False))

    def test_cleanup_timeout_separate(self):
        clock = Clock()
        adapter = Adapter(clock)
        adapter.cleanup_cost = 61
        result = m.run_budget(adapter, clock, b"", replace(m.Limits(), cleanup_ns=60))
        self.assertEqual(result.issues, (m.Issue.CLEANUP,))
        self.assertEqual(result.elapsed_ns, 0)
        self.assertEqual(result.cleanup_ns, 61)

    def test_clock_backward_invalid_and_bool(self):
        for clock in (lambda: True, lambda: -1, lambda: 1.5):
            adapter = Adapter(Clock())
            self.assertEqual(m.run_budget(adapter, clock, b"").issues, (m.Issue.CLOCK,))
            self.assertEqual(adapter.calls, [])
        clock = Clock()
        adapter = Adapter(clock, costs=[-1])
        result = m.run_budget(adapter, clock, b"")
        self.assertIn(m.Issue.CLOCK, result.issues)
        self.assertEqual(adapter.calls[-1][0], "cleanup")

    def test_malformed_step_and_limits(self):
        for value in (None, m.Step.__new__(m.Step), replace(m.Step(), exit=True),
                      replace(m.Step(), eof=1), replace(m.Step(), data=bytearray()),
                      replace(m.Step(), semantic_poll=1), replace(m.Step(), acquisition_stage=9)):
            self.issue(m.Issue.INVALID, [value])
        for value in (None, m.Limits.__new__(m.Limits), replace(m.Limits(), output_bytes=True),
                      replace(m.Limits(), output_bytes=m.MAX_OUTPUT + 1)):
            result, adapter = self.run_case(limits=value)
            self.assertEqual(result.issues, (m.Issue.INVALID,))
            self.assertEqual(adapter.calls, [])

    def test_exception_messages_not_exported(self):
        class Broken(Adapter):
            def step(self, maximum):
                raise RuntimeError("SYNTHETIC_PRIVATE_SENTINEL")
        clock = Clock()
        adapter = Broken(clock)
        result = m.run_budget(adapter, clock, b"")
        self.assertEqual(result.issues, (m.Issue.ADAPTER,))
        self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", repr(result))
        self.assertEqual(adapter.calls[-1][0], "cleanup")

    def test_cleanup_exception_and_start_partial_failure(self):
        class Broken(Adapter):
            def start(self, data):
                super().start(data)
                raise ValueError("private")

            def cleanup(self, deadline):
                super().cleanup(deadline)
                raise RuntimeError("private")
        clock = Clock()
        adapter = Broken(clock)
        result = m.run_budget(adapter, clock, b"")
        self.assertEqual(result.issues, (m.Issue.CLEANUP, m.Issue.ADAPTER))
        self.assertEqual([call[0] for call in adapter.calls], ["start", "cleanup"])
        self.assertFalse(result.cleanup_complete)

    def test_failed_start_and_step_costs_still_charge_regular_budget(self):
        for operation in ("start", "step"):
            class Broken(Adapter):
                def start(self, data):
                    super().start(data)
                    if operation == "start":
                        self.clock.value += 21 * m.NS
                        raise RuntimeError("private")

                def step(self, maximum):
                    self.clock.value += 21 * m.NS
                    raise RuntimeError("private")
            clock = Clock()
            adapter = Broken(clock)
            adapter.cleanup_cost = 7
            result = m.run_budget(adapter, clock, b"")
            self.assertIn(m.Issue.ADAPTER, result.issues)
            self.assertIn(m.Issue.COST, result.issues)
            self.assertEqual(result.active_ns, 21 * m.NS)
            self.assertEqual(result.elapsed_ns, 21 * m.NS)
            self.assertEqual(result.cleanup_ns, 7)
            self.assertTrue(result.cleanup_complete)

    def test_failed_pause_costs_consume_deadline_but_not_active_cost(self):
        class Broken(Adapter):
            def pause(self, duration):
                self.clock.value += 3 * m.NS
                raise RuntimeError("private")
        clock = Clock()
        adapter = Broken(clock, [m.Step(semantic_poll=True, sleep_ns=m.NS)])
        adapter.cleanup_cost = 9
        result = m.run_budget(adapter, clock, b"", replace(m.Limits(), phase_ns=2 * m.NS))
        self.assertIn(m.Issue.ADAPTER, result.issues)
        self.assertIn(m.Issue.TIMEOUT, result.issues)
        self.assertEqual(result.active_ns, 0)
        self.assertEqual(result.sleep_ns, 3 * m.NS)
        self.assertEqual(result.elapsed_ns, 3 * m.NS)
        self.assertEqual(result.cleanup_ns, 9)

    def test_failed_step_can_cross_deadline_and_cleanup_failure_stays_dominant(self):
        class Broken(Adapter):
            def step(self, maximum):
                self.clock.value += 146 * m.NS
                raise RuntimeError("private")
        clock = Clock()
        adapter = Broken(clock, cleanup=replace(GOOD, restored=False))
        result = m.run_budget(adapter, clock, b"")
        self.assertEqual(result.issues[0], m.Issue.CLEANUP)
        self.assertIn(m.Issue.TIMEOUT, result.issues)
        self.assertIn(m.Issue.COST, result.issues)
        self.assertEqual(result.elapsed_ns, 146 * m.NS)

    def test_cleanup_malformed_receipts(self):
        for receipt in (None, m.CleanupReceipt.__new__(m.CleanupReceipt), replace(GOOD, absent=1)):
            self.issue(m.Issue.CLEANUP, cleanup=receipt)

    def test_start_clock_error_still_calls_cleanup(self):
        clock = Clock()
        adapter = Adapter(clock)
        adapter.start_cost = -1
        result = m.run_budget(adapter, clock, b"")
        self.assertEqual(result.issues[0], m.Issue.CLEANUP)
        self.assertIn(m.Issue.CLOCK, result.issues)
        self.assertEqual(adapter.calls[-1][0], "cleanup")

    def test_final_clock_check_cannot_pass_at_boundary(self):
        class FinalClock(Clock):
            def __init__(self):
                super().__init__()
                self.calls = 0

            def __call__(self):
                self.calls += 1
                return 100 if self.calls >= 9 else 0
        clock = FinalClock()
        adapter = Adapter(clock)
        result = m.run_budget(adapter, clock, b"", replace(m.Limits(), phase_ns=100))
        self.assertIn(m.Issue.TIMEOUT, result.issues)
        self.assertTrue(result.cleanup_complete)

    def test_end_receipts_cannot_regress(self):
        self.issue(m.Issue.INVALID, [m.Step(input_complete=True), m.Step()])
        self.issue(m.Issue.INVALID, [m.Step(exit=m.Exit.SUCCESS), m.Step()])

    def test_foreign_fields_do_not_execute_getters_or_equality(self):
        class Foreign:
            def __eq__(self, other):
                raise RuntimeError("must not execute")

            def __getattr__(self, key):
                raise RuntimeError("must not execute")
        foreign = Foreign()
        for field in m.Step.__dataclass_fields__:
            self.issue(m.Issue.INVALID, [replace(m.Step(), **{field: foreign})])
        for field in m.Limits.__dataclass_fields__:
            result, adapter = self.run_case(limits=replace(m.Limits(), **{field: foreign}))
            self.assertEqual(result.issues, (m.Issue.INVALID,))
            self.assertEqual(adapter.calls, [])


class LinuxControlAlgorithmTests(unittest.TestCase):
    """Portable mocks test ordering only, not Linux syscall feasibility."""

    def cleanup(self, *, previous=0, anchor_error=False, pgid=123, reap_error=False,
                restore_error=False, restore_mismatch=False, wait_error=False,
                absence=False, child_sequence=None):
        adapter = m._LinuxAdapter(m.Scenario.BOTH)
        adapter.previous = previous
        events = []
        adapter.process = Mock(pid=123)
        adapter.process.stdin = Mock()
        adapter.process.stdout = Mock()
        adapter.process.stderr = Mock()

        def leader():
            events.append("anchor")
            if anchor_error:
                raise ChildProcessError
            return m.Exit.SUCCESS  # unreaped exit still anchors identity.

        def kill(group, sig):
            events.append(("kill", group, sig))
            if sig == 0 and not absence:
                raise ProcessLookupError

        def wait(*args, **kwargs):
            events.append("leader-reap")
            if wait_error:
                raise TimeoutError

        sequence = iter([] if child_sequence is None else child_sequence)

        def waitpid(group, flags):
            events.append(("group-reap", group))
            if reap_error:
                raise OSError
            value = next(sequence, None)
            if value is None:
                raise ChildProcessError
            return value, 0

        def prctl(option, argument, *rest):
            events.append(("prctl", option))
            if option == 36:
                return -1 if restore_error else 0
            argument._obj.value = 1 - previous if restore_mismatch else previous
            return 0

        adapter._leader = leader
        adapter.process.wait.side_effect = wait
        adapter.libc = Mock()
        adapter.libc.prctl.side_effect = prctl
        with patch.object(m.os, "getpgid", return_value=pgid, create=True), \
                patch.object(m.os, "killpg", side_effect=kill, create=True), \
                patch.object(m.os, "waitpid", side_effect=waitpid, create=True), \
                patch.object(m.os, "WNOHANG", 1, create=True), \
                patch.object(m.signal, "SIGKILL", 9, create=True), \
                patch.object(m.time, "sleep"), patch.object(m.time, "monotonic_ns", return_value=0):
            receipt = adapter.cleanup(m.NS)
        return receipt, events

    def test_anchored_stop_before_reap_then_presence_check_and_restore(self):
        receipt, events = self.cleanup(child_sequence=[124])
        self.assertEqual(receipt, GOOD)
        self.assertEqual(events[:5], ["anchor", ("kill", 123, 9), "leader-reap",
                                     ("group-reap", -123), ("group-reap", -123)])
        self.assertEqual(events[5:], [("kill", 123, 0), ("prctl", 36), ("prctl", 37)])

    def test_prior_subreaper_one_restored_and_verified(self):
        self.assertEqual(self.cleanup(previous=1)[0], GOOD)

    def test_lost_leader_anchor_never_signals_old_pgid(self):
        receipt, events = self.cleanup(anchor_error=True)
        self.assertFalse(receipt.initial_success or receipt.absent)
        self.assertFalse(any(type(event) is tuple and event[0] == "kill" for event in events))
        self.assertIn(("prctl", 36), events)

    def test_wrong_group_never_signals(self):
        receipt, events = self.cleanup(pgid=999)
        self.assertFalse(receipt.initial_success)
        self.assertFalse(any(type(event) is tuple and event[0] == "kill" for event in events))

    def test_reap_error_not_healed_by_restore(self):
        receipt, _ = self.cleanup(reap_error=True)
        self.assertFalse(receipt.initial_success or receipt.reaped or receipt.absent)
        self.assertTrue(receipt.restored)

    def test_leader_wait_error_never_proceeds_to_presence_claim(self):
        receipt, events = self.cleanup(wait_error=True)
        self.assertFalse(receipt.initial_success or receipt.absent)
        self.assertNotIn(("kill", 123, 0), events)

    def test_kill_success_not_absence(self):
        receipt, _ = self.cleanup(absence=True)
        self.assertTrue(receipt.stopped and receipt.reaped)
        self.assertFalse(receipt.absent)

    def test_restore_error_and_readback_mismatch_reject(self):
        for options in ({"restore_error": True}, {"restore_mismatch": True}):
            receipt, _ = self.cleanup(**options)
            self.assertFalse(receipt.restored)

    def test_cleanup_no_progress_has_independent_finite_cap(self):
        receipt, events = self.cleanup(child_sequence=[0] * 4096)
        self.assertFalse(receipt.reaped or receipt.absent)
        self.assertEqual(events.count(("group-reap", -123)), 4096)

    def test_existing_child_refused_without_reap_or_prctl(self):
        adapter = m._LinuxAdapter(m.Scenario.BOTH)
        # Explicit mock of isolated-worker prerequisites; no process is started.
        flags = Mock(isolated=1, no_site=1)
        with patch.object(m, "_WORKER_AUTHORIZED", True), patch.object(m, "__name__", "__main__"), \
                patch.object(m.sys, "platform", "linux"), patch.object(m.sys, "flags", flags), \
                patch.object(m.signal, "getsignal", return_value=m.signal.SIG_DFL), \
                patch.object(m.signal, "SIGCHLD", 17, create=True), \
                patch.object(m.os, "waitid", return_value=None, create=True) as waited, \
                patch.object(m.os, "P_ALL", 0, create=True), patch.object(m.os, "WEXITED", 4, create=True), \
                patch.object(m.os, "WNOWAIT", 16, create=True), patch.object(m.os, "WNOHANG", 1, create=True), \
                patch.object(m.ctypes, "CDLL") as libc, patch.object(m.subprocess, "Popen") as popen:
            with self.assertRaises(RuntimeError):
                adapter.start(b"")
            waited.assert_called_once()
            libc.assert_not_called()
            popen.assert_not_called()

    def test_sigchld_ignore_rejected_before_child_inspection(self):
        adapter = m._LinuxAdapter(m.Scenario.BOTH)
        flags = Mock(isolated=1, no_site=1)
        with patch.object(m, "_WORKER_AUTHORIZED", True), patch.object(m, "__name__", "__main__"), \
                patch.object(m.sys, "platform", "linux"), patch.object(m.sys, "flags", flags), \
                patch.object(m.signal, "getsignal", return_value=m.signal.SIG_IGN), \
                patch.object(m.signal, "SIGCHLD", 17, create=True), \
                patch.object(m.os, "waitid", create=True) as waited, patch.object(m.subprocess, "Popen") as popen:
            with self.assertRaises(RuntimeError):
                adapter.start(b"")
            waited.assert_not_called()
            popen.assert_not_called()

    def test_actual_pipe_capacity_must_be_smaller_than_validated_input(self):
        adapter = m._LinuxAdapter(m.Scenario.BACKPRESSURE)
        flags = Mock(isolated=1, no_site=1)
        process = Mock()
        fcntl = Mock(F_SETPIPE_SZ=1)
        fcntl.fcntl.return_value = m.MAX_INPUT  # simulated large Linux page, no forced backpressure.
        with patch.object(m, "_WORKER_AUTHORIZED", True), patch.object(m, "__name__", "__main__"), \
                patch.object(m.sys, "platform", "linux"), patch.object(m.sys, "flags", flags), \
                patch.object(m.signal, "getsignal", return_value=m.signal.SIG_DFL), \
                patch.object(m.signal, "SIGCHLD", 17, create=True), \
                patch.object(m.os, "waitid", side_effect=ChildProcessError, create=True), \
                patch.object(m.os, "P_ALL", 0, create=True), patch.object(m.os, "WEXITED", 4, create=True), \
                patch.object(m.os, "WNOWAIT", 16, create=True), patch.object(m.os, "WNOHANG", 1, create=True), \
                patch.object(m.ctypes, "CDLL", return_value=Mock(prctl=Mock(return_value=0))), \
                patch.object(m.subprocess, "Popen", return_value=process), patch.dict(sys.modules, {"fcntl": fcntl}):
            with self.assertRaises(m._AdapterUnsupported):
                adapter.start(b"i" * m.MAX_INPUT)
            fcntl.fcntl.assert_called_once()
        adapter.selector.close()

    def test_imported_adapter_cannot_mutate_subreaper(self):
        clock = Clock()
        result = m.run_budget(m._LinuxAdapter(m.Scenario.BOTH), clock, b"")
        self.assertFalse(result.success)
        self.assertIn(m.Issue.ADAPTER, result.issues)

    def test_frozen_reports_and_policy(self):
        for obj, name in ((m.Limits(), "io_steps"), (m.Step(), "eof"), (GOOD, "absent"),
                          (m.Report(True, ()), "success")):
            with self.assertRaises(FrozenInstanceError):
                setattr(obj, name, None)

    def test_fixed_source_no_candidate_or_sql_integration(self):
        source = PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {"dataclasses", "enum"})
        self.assertNotIn("run_dgn007_automated_setup", source)
        self.assertNotIn("decode_capture", source)
        self.assertNotIn("shell=True", source)
        self.assertNotIn("capture_output", source)
        self.assertNotIn(".poll(", source)


@unittest.skipUnless(sys.platform == "linux", "Linux-only fixed fresh-worker adapter; no start on Windows")
class LinuxTests(unittest.TestCase):
    def worker(self, scenario):
        # Trusted fixed worker, never candidate code. The report has fixed scalar fields.
        result = subprocess.run([sys.executable, "-I", "-S", str(PATH), "--synthetic-worker", scenario],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8,
                                env={"LANG": "C", "LC_ALL": "C"}, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        self.assertLessEqual(len(result.stdout), 4096)
        record = json.loads(result.stdout)
        self.assertFalse(record["runtime_attested"] or record["method_approved"])
        self.assertNotIn(m.Issue.CLEANUP.value, record["issues"])
        self.assertTrue(record["cleanup_complete"])
        return record

    def test_split_utf8_crlf_actual_pipes(self):
        record = self.worker("split")
        self.assertTrue(record["success"])
        self.assertTrue(record["stdout_eof"] and record["stderr_eof"])
        self.assertEqual(record["observed_bytes"], 5)

    def test_both_actual_channels(self):
        record = self.worker("both")
        self.assertTrue(record["success"])
        self.assertEqual(record["observed_bytes"], 9)

    def test_flood_bounded_before_decode(self):
        record = self.worker("flood")
        self.assertIn(m.Issue.OUTPUT.value, record["issues"])
        self.assertLessEqual(record["observed_bytes"], m.MAX_OUTPUT + 1)
        self.assertLessEqual(record["retained_bytes"], m.MAX_OUTPUT)

    def test_invalid_utf8_actual_pipe(self):
        self.assertIn(m.Issue.TEXT.value, self.worker("invalid")["issues"])

    def test_writer_backpressure_own_cleanup(self):
        record = self.worker("backpressure")
        self.assertFalse(record["success"])
        self.assertFalse(record["input_written"])
        self.assertTrue(set(record["issues"]) & {m.Issue.STALLED.value, m.Issue.TIMEOUT.value})

    def test_root_exit_before_inherited_pipe_eof(self):
        record = self.worker("inherited-pipe")
        self.assertFalse(record["success"])
        self.assertTrue(set(record["issues"]) & {m.Issue.STALLED.value, m.Issue.TIMEOUT.value})
        self.assertFalse(record["stdout_eof"] and record["stderr_eof"])


if __name__ == "__main__":
    unittest.main()
