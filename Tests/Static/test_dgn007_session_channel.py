"""Getrennte portable Vorläufe und eigene isolierte Linux-Kanalgegenproben."""
from dataclasses import replace
import ctypes
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_session_match as fixture
import dgn007_session_channel as subject

NATIVE = sys.platform == "linux" and sys.version_info[:2] == (3, 12)
HEADER = """import os, signal, time
signal.alarm(3)
def put(fd, body):
    while body:
        body = body[os.write(fd, body):]
"""


def selection(harness, ordinal=1, *, tail="", stderr=b"\xff\0PRIVATE_PAYLOAD", change=None):
    payload = fixture.fixture.semantic_fixture(ordinal)
    reported, _, _ = fixture.fixture.reporter_reference(payload, fixture.fixture.reporter_scalars(payload))
    rows, err = harness.make_session(reported, stderr=stderr)
    if change is not None:
        rows, err = change(rows, err)
    out = b"".join(rows)
    program = HEADER + f"put(1, {out!r})\nput(2, {err!r})\n" + tail
    return subject.ChannelSelection(program.encode("utf-8"), reported, reported[0]), len(out) + len(err)


def subreaper_value():
    value = ctypes.c_int()
    if ctypes.CDLL(None).prctl(37, ctypes.byref(value), 0, 0, 0) != 0:
        raise AssertionError("SUBREAPER_READ")
    return value.value


def native_case(name):
    """Ein fester Fall pro frischem Worker; kein Callerprogramm aus argv."""
    harness = fixture.SessionMatchTests(methodName="runTest")
    harness.setUp()
    previous = subreaper_value()
    original_launch, original_cleanup = subject._launch, subject._cleanup
    original_restore, original_check = subject._Reaper.restore, subject._Control.check
    original_clock = subject.time.monotonic_ns
    provider_sha = harness.provider.sha256
    encoder = sys.modules["json.encoder"].JSONEncoder
    encoder_default = encoder.default
    namespace_match = harness.namespace["_inline_match_session_end"]
    try:
        one, size = selection(harness)
        selected = (one,)
        limits = subject.ChannelLimits()
        if name in ("cohort", "shared_cap", "shared_cap_minus_one"):
            pairs = [selection(harness, ordinal) for ordinal in (1, 2, 3)]
            selected = tuple(pair[0] for pair in pairs)
            size = sum(pair[1] for pair in pairs)
            if name != "cohort":
                limits = replace(limits, output_bytes=size - (name == "shared_cap_minus_one"))
        elif name == "chunked":
            limits = replace(limits, read_bytes=17)
        elif name == "eof_first":
            selected = (selection(harness, tail="os.close(1)\nos.close(2)\ntime.sleep(.12)\n")[0],)
        elif name == "exit_first":
            rows, err = harness.make_session(stderr=b"LATE_PRIVATE_PAYLOAD")
            body = HEADER + f"put(1, {b''.join(rows)!r})\n"
            body += ("pid = os.fork()\nif pid == 0:\n    signal.alarm(3)\n"
                     f"    time.sleep(.12)\n    put(2, {err!r})\n    os._exit(0)\nos._exit(0)\n")
            selected = (replace(one, program=body.encode()),)
            size = sum(map(len, rows)) + len(err)
        elif name == "inherited_stall":
            body = HEADER + ("pid = os.fork()\nif pid == 0:\n    signal.alarm(3)\n"
                             "    time.sleep(2)\n    os._exit(0)\nos._exit(0)\n")
            selected = (replace(one, program=body.encode()), selection(harness, 2)[0])
            limits = replace(limits, no_progress=8)
        elif name == "eof_timeout":
            body = HEADER + "os.close(1)\nos.close(2)\ntime.sleep(2)\n"
            selected = (replace(one, program=body.encode()),)
            limits = replace(limits, regular_ns=100_000_000)
        elif name == "exit7":
            selected = (replace(one, program=(HEADER + "os._exit(7)\n").encode()),)
        elif name == "signal_exit":
            selected = (replace(one, program=(HEADER + "os.kill(os.getpid(), signal.SIGTERM)\n").encode()),)
        elif name in ("missing_footer", "extra_footer", "bad_hash", "bad_nonce", "truncated"):
            def change(rows, err):
                if name == "missing_footer": return rows[:-1], err
                if name == "extra_footer": return rows + (rows[-1],), err
                if name == "truncated": return rows[:-1] + (rows[-1][:-1],), err
                if name == "bad_hash": return harness.changed_row(rows, -1, 11, "0" * 64), err
                index = next(i for i, row in enumerate(rows) if json.loads(row)[0] == "INPUT_COMPLETE")
                nonce = json.loads(rows[index])[2]
                other = ("0" if nonce[0] != "0" else "1") + nonce[1:]
                changed = harness.changed_row(rows, index, 2, other, seal=False)
                return harness.reseal(changed, err), err
            selected = (selection(harness, change=change)[0], selection(harness, 2)[0])
        elif name in ("line1024", "line1025", "records44", "byte_overflow"):
            raw = {"line1024": b"x" * 1023 + b"\n", "line1025": b"x" * 1024 + b"\n",
                   "records44": b"{}\n" * 44, "byte_overflow": b"x" * 65537}[name]
            fd = 2 if name == "byte_overflow" else 1
            selected = (replace(one, program=(HEADER + f"put({fd}, {raw!r})\n").encode()),)
        elif name == "io_limit":
            limits = replace(limits, io_steps=1)
        elif name in ("provider_drift", "encoder_drift", "both_drift", "owner_drift"):
            def launch(program):
                process = original_launch(program)
                if name in ("provider_drift", "both_drift"):
                    harness.provider.sha256 = lambda *_: None
                if name in ("encoder_drift", "both_drift"):
                    encoder.default = lambda *_: None
                if name == "owner_drift":
                    harness.namespace["_inline_match_session_end"] = lambda *_: None
                return process
            subject._launch = launch
        elif name in ("cleanup_sticky", "cleanup_raises", "restore_raises"):
            selected = (one, selection(harness, 2)[0])
            if name == "restore_raises":
                old_restore = subject._Reaper.restore
                def restore(reaper):
                    if not old_restore(reaper): raise AssertionError("RESTORE_FAILED")
                    raise ValueError("PRIVATE_PAYLOAD")
                subject._Reaper.restore = restore
            else:
                def cleanup(*args):
                    if not original_cleanup(*args): raise AssertionError("REAL_CLEANUP_FAILED")
                    if name == "cleanup_raises": raise ValueError("PRIVATE_PAYLOAD")
                    return False
                subject._cleanup = cleanup
        elif name == "private_error":
            def launch(program):
                raise ValueError("PRIVATE_PAYLOAD")
            subject._launch = launch
        elif name == "final_post_timeout":
            phase = dict(restored=False, checks=0)
            def restore(reaper):
                result = original_restore(reaper)
                phase["restored"] = True
                return result
            def check(control):
                original_check(control)
                if phase["restored"]:
                    phase["checks"] += 1
                    if phase["checks"] == 2:
                        subject.time.monotonic_ns = lambda: original_clock() + 21 * subject.NS
            subject._Reaper.restore, subject._Control.check = restore, check
        elif name not in ("single",):
            raise AssertionError("UNKNOWN_FIXED_CASE")
        try:
            report = subject.run_session_channels(harness.namespace, selected, limits=limits)
        finally:
            subject._Reaper.restore, subject._Control.check = original_restore, original_check
            subject.time.monotonic_ns = original_clock
            subject._launch, subject._cleanup = original_launch, original_cleanup
            harness.provider.sha256 = provider_sha
            encoder.default = encoder_default
            harness.namespace["_inline_match_session_end"] = namespace_match
        # Unabhängige frische Absenz und echtes Restore; UNKNOWN bleibt im Ownerreport.
        if not subject._no_children() or subreaper_value() != previous:
            raise AssertionError("NATIVE_ABSENCE_OR_RESTORE")
        fields = ("status", "issue", "first_issue", "start_attempts", "started", "matched", "closed",
                  "observed_bytes", "io_steps", "cleanup_attempts", "cleanup_complete", "stdout_eofs",
                  "stderr_eofs", "zero_exits", "eof_before_exit", "exit_before_eofs", "validation_scope",
                  "runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved")
        result = {key: getattr(report, key) for key in fields}
        result["expected_bytes"] = size
        if repr(report) != "ChannelReport(PROJECT_SEMANTIC)": raise AssertionError("PRIVATE_REPR")
    finally:
        harness.tearDown()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


class PortableTests(unittest.TestCase):
    def test_limits_are_exact_and_fail_before_start(self):
        harness = fixture.SessionMatchTests(methodName="runTest"); harness.setUp()
        try:
            one, _ = selection(harness)
            with patch.object(subject, "_launch", side_effect=AssertionError("NO_START")):
                for limits in (None, replace(subject.ChannelLimits(), output_bytes=True),
                               replace(subject.ChannelLimits(), output_bytes=65537),
                               replace(subject.ChannelLimits(), cleanup_ns=0)):
                    with self.subTest(limits=limits):
                        report = subject.run_session_channels(harness.namespace, (one,), limits=limits)
                        self.assertEqual((report.issue, report.start_attempts), ("CHANNEL_FORM", 0))
        finally: harness.tearDown()

    def test_all_selection_forms_precede_launch(self):
        harness = fixture.SessionMatchTests(methodName="runTest"); harness.setUp()
        try:
            one, _ = selection(harness)
            choices = ((), [one], (fixture.fixture.Foreign(),), (replace(one, program=fixture.fixture.Foreign()),),
                       (replace(one, program=b"\0"),), (replace(one, program=b"\xff"),),
                       (replace(one, program=b"x" * 131073),), (one, one),
                       (replace(one, context=()),))
            with patch.object(subject, "_launch", side_effect=AssertionError("NO_START")):
                for index, selected in enumerate(choices):
                    with self.subTest(index=index):
                        report = subject.run_session_channels(harness.namespace, selected)
                        self.assertEqual((report.issue, report.start_attempts), ("CHANNEL_FORM", 0))
        finally: harness.tearDown()

    @unittest.skipIf(NATIVE and sys.flags.isolated and sys.flags.no_site, "Native Plattform ist hier zulässig")
    def test_platform_rejection_has_no_native_side_effect(self):
        harness = fixture.SessionMatchTests(methodName="runTest"); harness.setUp()
        try:
            one, _ = selection(harness)
            with patch.object(subject, "_launch", side_effect=AssertionError("NO_START")):
                report = subject.run_session_channels(harness.namespace, (one,))
            self.assertEqual((report.issue, report.start_attempts), ("CHANNEL_PLATFORM", 0))
            self.assertTrue(report.cleanup_complete)
        finally: harness.tearDown()

    def test_shared_budget_arithmetic_and_no_reset(self):
        limits = subject.ChannelLimits(output_bytes=7, io_steps=2, no_progress=2, regular_ns=10)
        with patch.object(subject.time, "monotonic_ns", return_value=100):
            budget = subject._Budget(limits, 95)
            budget.book(b"abc"); budget.book(b"defg")
            with self.assertRaisesRegex(subject._Rejected, "CHANNEL_BYTES"): budget.book(b"h")
            self.assertEqual(budget.bytes, 8)
            budget.step(); budget.step()
            with self.assertRaisesRegex(subject._Rejected, "CHANNEL_IO"): budget.step()
            budget.progress(False)
            with self.assertRaisesRegex(subject._Rejected, "CHANNEL_STALLED"): budget.progress(False)
            budget.progress(True); self.assertEqual(budget.quiet, 0)
        with patch.object(subject.time, "monotonic_ns", return_value=105):
            with self.assertRaisesRegex(subject._Rejected, "CHANNEL_TIMEOUT"): budget.check()

    def test_issue_diagnostics_are_closed_and_private(self):
        self.assertEqual(subject._issue(ValueError("PRIVATE_PAYLOAD")), "CHANNEL_INTERNAL")
        self.assertEqual(subject._issue(ValueError("x" * 100000)), "CHANNEL_INTERNAL")
        self.assertEqual(subject._dominant("CHANNEL_MATCH", "CHANNEL_TIMEOUT"), "CHANNEL_MATCH")
        self.assertEqual(subject._dominant("REPORT_ENCODER_BINDING", "HASH_PROVIDER_BINDING"),
                         "HASH_PROVIDER_BINDING")
        self.assertEqual(subject._dominant("CHANNEL_CLEANUP", "HASH_PROVIDER_BINDING"), "CHANNEL_CLEANUP")


@unittest.skipUnless(NATIVE, "Native Linux-/CPython-3.12-Gegenproben separat erforderlich")
class NativeTests(unittest.TestCase):
    def run_case(self, name):
        try:
            completed = subprocess.run([sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()),
                                        "--native-case", name], capture_output=True, timeout=12, check=False)
        except subprocess.TimeoutExpired:
            raise AssertionError("NATIVE_WORKER_UNKNOWN_TIMEOUT") from None
        self.assertEqual(completed.returncode, 0, "NATIVE_WORKER_FAILED")
        self.assertLessEqual(len(completed.stdout), 4096)
        try:
            report = json.loads(completed.stdout)
        except (ValueError, UnicodeError):
            raise AssertionError("NATIVE_REPORT_FORM") from None
        self.assertFalse(b"PRIVATE_PAYLOAD" in completed.stdout, "NATIVE_REPORT_PRIVATE")
        self.assertEqual(report["validation_scope"], "PROJECT_SEMANTIC")
        for field in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(report[field], False)
        return report

    def test_actual_channels_match_all_roles_and_shared_exact_cap(self):
        for name, count in (("single", 1), ("cohort", 3), ("chunked", 1), ("shared_cap", 3)):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["started"], r["matched"], r["closed"]), ("NONE", count, count, count))
                self.assertEqual((r["stdout_eofs"], r["stderr_eofs"], r["zero_exits"]), (count, count, count))
                self.assertEqual(r["observed_bytes"], r["expected_bytes"])
                self.assertTrue(r["cleanup_complete"])

    def test_both_real_eof_exit_orderings(self):
        for name, field in (("eof_first", "eof_before_exit"), ("exit_first", "exit_before_eofs")):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r[field], r["closed"]), ("NONE", 1, 1))
                self.assertTrue(r["cleanup_complete"])

    def test_inherited_pipe_stall_never_restarts_after_exit(self):
        r = self.run_case("inherited_stall")
        self.assertEqual((r["issue"], r["started"], r["closed"], r["zero_exits"]), ("CHANNEL_STALLED", 1, 0, 1))
        self.assertEqual((r["stdout_eofs"], r["stderr_eofs"]), (0, 0))
        self.assertTrue(r["cleanup_complete"])

    def test_eof_does_not_replace_exit(self):
        r = self.run_case("eof_timeout")
        self.assertEqual((r["issue"], r["stdout_eofs"], r["stderr_eofs"], r["zero_exits"]), ("CHANNEL_TIMEOUT", 1, 1, 0))
        self.assertTrue(r["cleanup_complete"])

    def test_nonzero_and_signal_exit_are_rejected(self):
        for name in ("exit7", "signal_exit"):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["zero_exits"], r["closed"]), ("CHANNEL_EXIT", 0, 0))
                self.assertTrue(r["cleanup_complete"])

    def test_actual_bad_channels_and_footer_never_start_next_slot(self):
        for name in ("missing_footer", "extra_footer", "bad_hash", "bad_nonce", "truncated"):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual(r["issue"], "CHANNEL_LINE_EOF" if name == "truncated" else "CHANNEL_MATCH")
                self.assertEqual((r["started"], r["closed"]), (1, 0))
                self.assertTrue(r["cleanup_complete"])

    def test_actual_framing_and_global_resources(self):
        cases = (("line1024", "CHANNEL_MATCH"), ("line1025", "CHANNEL_LINE"),
                 ("records44", "CHANNEL_RECORDS"), ("byte_overflow", "CHANNEL_BYTES"),
                 ("io_limit", "CHANNEL_IO"), ("shared_cap_minus_one", "CHANNEL_BYTES"))
        for name, issue in cases:
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual(r["issue"], issue)
                self.assertTrue(r["cleanup_complete"])
                if name == "byte_overflow": self.assertEqual(r["observed_bytes"], 65537)
                if name == "shared_cap_minus_one":
                    self.assertEqual((r["started"], r["closed"], r["observed_bytes"]), (3, 2, r["expected_bytes"]))

    def test_held_outer_bindings_reject_real_postlaunch_drift(self):
        cases = (("provider_drift", "HASH_PROVIDER_BINDING"), ("encoder_drift", "REPORT_ENCODER_BINDING"),
                 ("both_drift", "HASH_PROVIDER_BINDING"), ("owner_drift", "CHANNEL_OWNER"))
        for name, issue in cases:
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["started"], r["matched"]), (issue, 1, 0))
                self.assertTrue(r["cleanup_complete"])

    def test_first_cleanup_failure_is_not_healed_by_later_absence(self):
        for name in ("cleanup_sticky", "cleanup_raises", "restore_raises"):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["started"], r["closed"]), ("CHANNEL_CLEANUP", 1, 0))
                self.assertFalse(r["cleanup_complete"])

    def test_start_without_handle_remains_unknown_and_private(self):
        r = self.run_case("private_error")
        self.assertEqual((r["issue"], r["first_issue"], r["start_attempts"], r["started"]),
                         ("CHANNEL_CLEANUP", "CHANNEL_START_UNKNOWN", 1, 0))
        self.assertFalse(r["cleanup_complete"])

    def test_deadline_is_rechecked_after_last_real_binding_check(self):
        r = self.run_case("final_post_timeout")
        self.assertEqual((r["status"], r["issue"], r["first_issue"]),
                         ("REJECTED_SESSION_CHANNELS", "CHANNEL_TIMEOUT", "CHANNEL_TIMEOUT"))
        self.assertEqual((r["started"], r["matched"], r["cleanup_attempts"]), (1, 1, 1))
        self.assertTrue(r["cleanup_complete"])


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--native-case":
        native_case(sys.argv[2])
    else:
        unittest.main()
