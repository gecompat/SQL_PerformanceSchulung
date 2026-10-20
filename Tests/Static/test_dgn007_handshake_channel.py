"""Eigene frische Nativeworker prüfen vollständige Bytes und echte Phasenfolge."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_handshake_input_plan as input_fixture
import test_dgn007_session_channel as channel_fixture
import dgn007_handshake_channel as subject

channel = subject.channel
NATIVE = channel_fixture.NATIVE
CASES = frozenset(("single", "cohort", "zero_bodies", "partial_writes", "backpressure", "bad_profile",
    "bad_nonce", "early_input", "partial_early_input", "duplicate_profile", "early_loader", "duplicate_input",
    "stdin_early", "write_stall", "input_stall", "io_limit", "byte_limit", "timeout", "eof_first", "exit_first",
    "inherited_stall", "exit7", "reentrant_prepare", "reentrant_profile", "provider_drift", "encoder_drift",
    "both_drift", "cleanup_sticky"))
PROGRAM = r'''import os, signal, time, select
signal.alarm(3)
def put(fd, body):
    while body:
        body = body[os.write(fd, body):]
def take(n):
    pieces = []
    while n:
        data = os.read(0, n)
        if not data: os._exit(91)
        pieces.append(data)
        n -= len(data)
    return b"".join(pieces)
def expect_line(expected):
    raw = b""
    for _ in range(256):
        raw += take(1)
        if raw.endswith(b"\n"):
            if raw != expected: os._exit(92)
            return
    os._exit(92)
def no_early_input():
    if select.select([0], [], [], .03)[0]: os._exit(93)
'''


def make_selection(harness, name="single", ordinal=1):
    bodies = (b"\xff\0\r\n", b"", b"raw\r\n") + tuple(b"source-" + str(n).encode() for n in range(6))
    padding = 0
    if name == "zero_bodies": bodies = (b"",) * 9
    if name in ("backpressure", "stdin_early", "write_stall"):
        bodies = (b"x" * 8192,) * 4 + (b"",) * 5
        padding = 3000
    item = input_fixture.selected(ordinal=ordinal, bodies=bodies, padding=padding)
    metadata = b"".join(item.metadata_chunks)
    commands = input_fixture.oracle_commands(item)
    err = b"\xff\0PRIVATE_PAYLOAD" if name != "backpressure" else b"x" * 32768
    reported = item.reported
    if name == "bad_profile":
        reported = input_fixture.fixture.fixture.semantic_change(reported, (1, 3, 2), 15)
    rows, _ = harness.make_session(reported, stderr=err)
    profile_end = next(n for n, row in enumerate(rows) if row.startswith(b'["PROFILE_END",'))
    ic = profile_end + 1
    if name == "bad_nonce":
        nonce = json.loads(rows[ic])[2]
        changed = harness.changed_row(rows, ic, 2, ("0" if nonce[0] != "0" else "1") + nonce[1:], seal=False)
        rows = harness.reseal(changed, err)
    profile, complete, final = b"".join(rows[:ic]), rows[ic], b"".join(rows[ic + 1:])
    program = PROGRAM
    if name in ("stdin_early", "write_stall"):
        program += "take(1)\n" + ("os.close(0)\n" if name == "stdin_early" else "") + "time.sleep(2)\n"
    else:
        if name == "backpressure":
            program += f"first = take(1)\nput(2, {err!r})\nreceived = first + take({len(metadata)-1})\n"
        else:
            program += f"received = take({len(metadata)})\nput(2, {err!r})\n"
        program += f"if received != {metadata!r}: os._exit(94)\nno_early_input()\n"
        if name in ("early_input", "partial_early_input", "duplicate_profile"):
            extra = complete if name == "early_input" else complete[:8] if name == "partial_early_input" else rows[profile_end]
            if len(profile + extra) > 4096: raise AssertionError("COALESCED_FIXTURE_LIMIT")
            program += f"put(1, {profile + extra!r})\ntime.sleep(2)\n"
        else:
            program += f"put(1, {profile!r})\nexpect_line({commands[0]!r})\n"
            for body in bodies:
                program += f"if take({len(body)}) != {body!r}: os._exit(95)\n"
            program += f"expect_line({commands[1]!r})\nno_early_input()\n"
            if name == "input_stall":
                program += "time.sleep(2)\n"
            else:
                extra = rows[ic + 1] if name == "early_loader" else complete if name == "duplicate_input" else b""
                if extra and len(complete + extra) > 4096: raise AssertionError("COALESCED_FIXTURE_LIMIT")
                program += f"put(1, {complete + extra!r})\nexpect_line({commands[2]!r})\n"
                program += "if os.read(0, 1) != b\"\": os._exit(96)\n"
                if name == "exit7": program += "os._exit(7)\n"
                else: program += f"put(1, {final!r})\n"
                if name in ("eof_first", "timeout"):
                    program += "os.close(1)\nos.close(2)\ntime.sleep(" + ("2" if name == "timeout" else ".12") + ")\n"
                if name in ("exit_first", "inherited_stall"):
                    delay = 2 if name == "inherited_stall" else .12
                    program += ("pid = os.fork()\nif pid == 0:\n    signal.alarm(3)\n"
                                f"    time.sleep({delay})\n    os._exit(0)\nos._exit(0)\n")
    expected = sum(map(len, item.metadata_chunks + item.bodies + commands))
    return subject.HandshakeSelection(program.encode(), item), expected


def native_case(name):
    import fcntl
    if name not in CASES: raise AssertionError("UNKNOWN_FIXED_CASE")
    harness = input_fixture.fixture.SessionMatchTests(methodName="runTest")
    harness.setUp()
    previous = channel_fixture.subreaper_value()
    original_init, original_write, original_cleanup = subject._Phase.__init__, subject._write, channel._cleanup
    original_sha, original_default = harness.provider.sha256, json.JSONEncoder.default
    captured, nested, fired = [], [], False
    try:
        def phase_init(phase, driver, plan, process, selector, budget, control):
            # Erst nach gebundenem Popen-Handle: beide eigenen Pipepuffer sicher verkleinern.
            captured.append(process)
            if name in ("backpressure", "stdin_early", "write_stall"):
                fcntl.fcntl(process.stdin.fileno(), fcntl.F_SETPIPE_SZ, 4096)
                fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETPIPE_SZ, 4096)
            original_init(phase, driver, plan, process, selector, budget, control)
        subject._Phase.__init__ = phase_init
        if name == "partial_writes":
            subject._write = lambda fd, data: original_write(fd, data[:17])
        if name == "cleanup_sticky":
            def cleanup(*args):
                if not original_cleanup(*args): raise AssertionError("REAL_CLEANUP_FAILED")
                return False
            channel._cleanup = cleanup
        def drift():
            nonlocal fired
            if fired or name != "reentrant_prepare" and not captured: return
            fired = True
            if name in ("reentrant_prepare", "reentrant_profile"):
                owner = channel._ACTIVE_OWNER
                nested.append(channel.run_session_channels(harness.namespace, ()).issue)
                nested.append(subject.run_handshake_channels(harness.namespace, ()).issue)
                if channel._ACTIVE_OWNER is not owner: raise AssertionError("OWNER_LOST")
            if name in ("provider_drift", "both_drift"): harness.provider.sha256 = lambda *_: None
            if name in ("encoder_drift", "both_drift"): json.JSONEncoder.default = lambda *_: None
        if name in ("reentrant_prepare", "reentrant_profile", "provider_drift", "encoder_drift", "both_drift"):
            harness.provider._HASH_CALLBACK = drift
        count = 3 if name == "cohort" else 2 if name in (
            "bad_profile", "bad_nonce", "early_input", "partial_early_input", "duplicate_profile",
            "early_loader", "duplicate_input", "stdin_early", "write_stall", "input_stall",
            "inherited_stall", "cleanup_sticky") else 1
        pairs = [make_selection(harness, name, n) for n in range(1, count + 1)]
        selected = tuple(pair[0] for pair in pairs)
        limits = channel.ChannelLimits()
        if name in ("write_stall", "input_stall", "inherited_stall"):
            limits = replace(limits, no_progress=8)
        if name == "io_limit": limits = replace(limits, io_steps=1)
        if name == "byte_limit": limits = replace(limits, output_bytes=32)
        if name == "timeout": limits = replace(limits, regular_ns=channel.NS)
        report = subject.run_handshake_channels(harness.namespace, selected, limits=limits)
        if not channel._no_children() or channel_fixture.subreaper_value() != previous:
            raise AssertionError("ABSENCE_OR_RESTORE")
        if channel._ACTIVE_OWNER is not None: raise AssertionError("OWNER_NOT_RELEASED")
        if any(not stream.closed for process in captured for stream in (process.stdin, process.stdout, process.stderr)):
            raise AssertionError("PIPE_NOT_CLOSED")
        result = {key: getattr(report, key) for key in (
            "status", "issue", "first_issue", "written_bytes", "body_release_reserved", "body_release_sent",
            "body_end_reserved", "body_end_sent", "import_release_reserved", "import_release_sent", "stdin_closed",
            "validation_scope", "runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved")}
        result.update({key: getattr(report.channels, key) for key in (
            "start_attempts", "started", "matched", "closed", "observed_bytes", "io_steps", "child_io_reserved", "cleanup_complete",
            "stdout_eofs", "stderr_eofs", "zero_exits", "eof_before_exit", "exit_before_eofs")})
        result["expected_bytes"] = sum(pair[1] for pair in pairs)
        result["nested"] = nested
        if repr(report) != "HandshakeChannelReport(PROJECT_SEMANTIC)": raise AssertionError("PRIVATE_REPR")
    finally:
        subject._Phase.__init__, subject._write, channel._cleanup = original_init, original_write, original_cleanup
        harness.provider._HASH_CALLBACK = None
        harness.provider.sha256, json.JSONEncoder.default = original_sha, original_default
        harness.tearDown()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.f = input_fixture.fixture.SessionMatchTests(methodName="runTest"); self.f.setUp()

    def tearDown(self):
        self.assertIsNone(channel._ACTIVE_OWNER)
        self.f.tearDown()

    def test_exact_types_and_full_preflight_without_start(self):
        one = make_selection(self.f)[0]
        foreign = input_fixture.fixture.fixture.Foreign()
        with patch.object(channel, "_launch", side_effect=AssertionError("NO_START")):
            for values in ((), [one], (foreign,), (replace(one, program=foreign),),
                           (replace(one, input_selection=foreign),), (replace(one, program=b"\0"),)):
                self.assertEqual(subject.run_handshake_channels(self.f.namespace, values).issue, "CHANNEL_FORM")
            report = subject.run_handshake_channels(self.f.namespace, (one,), limits=replace(channel.ChannelLimits(), io_steps=True))
            self.assertEqual(report.issue, "CHANNEL_FORM")

    def test_input_preflight_covers_later_slot_before_start(self):
        one, two = make_selection(self.f)[0], make_selection(self.f, ordinal=2)[0]
        bad = replace(two, input_selection=replace(two.input_selection, bodies=(b"",)))
        with patch.object(channel, "_launch", side_effect=AssertionError("NO_START")):
            report = subject.run_handshake_channels(self.f.namespace, (one, bad))
        self.assertEqual((report.issue, report.channels.start_attempts), ("CHANNEL_INPUT", 0))
        self.assertEqual(self.f.provider._HASH_CALLS, 0)

    @unittest.skipIf(NATIVE and sys.flags.isolated and sys.flags.no_site, "Native Plattform ist hier zulässig")
    def test_platform_rejection_is_private_and_has_no_process(self):
        one = make_selection(self.f)[0]
        with patch.object(channel, "_launch", side_effect=AssertionError("NO_START")):
            report = subject.run_handshake_channels(self.f.namespace, (one,))
        self.assertEqual((report.issue, report.channels.started), ("CHANNEL_PLATFORM", 0))
        self.assertEqual(repr(report), "HandshakeChannelReport(PROJECT_SEMANTIC)")


@unittest.skipUnless(NATIVE, "Native Linux-/CPython-3.12-Gegenproben separat erforderlich")
class NativeTests(unittest.TestCase):
    def run_case(self, name):
        try:
            completed = subprocess.run([sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()),
                                        "--native-case", name], capture_output=True, timeout=12)
        except subprocess.TimeoutExpired:
            raise AssertionError("NATIVE_WORKER_UNKNOWN_TIMEOUT") from None
        self.assertEqual(completed.returncode, 0, "NATIVE_WORKER_FAILED")
        self.assertLessEqual(len(completed.stdout), 4096)
        self.assertFalse(b"PRIVATE_PAYLOAD" in completed.stdout, "NATIVE_REPORT_PRIVATE")
        try: report = json.loads(completed.stdout)
        except (ValueError, UnicodeError): raise AssertionError("NATIVE_REPORT_FORM") from None
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(report[key], False)
        self.assertEqual(report["validation_scope"], "PROJECT_SEMANTIC")
        return report

    def test_full_bytes_all_phases_roles_zero_and_binary_bodies(self):
        for name, count in (("single", 1), ("cohort", 3), ("zero_bodies", 1), ("partial_writes", 1), ("backpressure", 1)):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["closed"], r["written_bytes"]), ("NONE", count, r["expected_bytes"]))
                for key in ("body_release_reserved", "body_release_sent", "body_end_reserved", "body_end_sent",
                            "import_release_reserved", "import_release_sent", "stdin_closed", "stdout_eofs", "stderr_eofs", "zero_exits"):
                    self.assertEqual(r[key], count)
                self.assertTrue(r["cleanup_complete"])
                self.assertEqual(r["child_io_reserved"], count * 1088)
                self.assertLessEqual(r["io_steps"] + r["child_io_reserved"], 4096)

    def test_wrong_profile_and_input_nonce_never_advance_or_restart(self):
        for name in ("bad_profile", "bad_nonce"):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["started"], r["closed"], r["import_release_reserved"]), ("CHANNEL_PHASE", 1, 0, 0))
                self.assertEqual(r["body_release_sent"], 0 if name == "bad_profile" else 1)
                self.assertTrue(r["cleanup_complete"])

    def test_observed_coalesced_or_partial_early_records_never_become_later_phase(self):
        for name in ("early_input", "partial_early_input", "duplicate_profile", "early_loader", "duplicate_input"):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["started"], r["closed"], r["import_release_sent"]), ("CHANNEL_PHASE", 1, 0, 0))
                self.assertTrue(r["cleanup_complete"])

    def test_closed_stdin_or_missing_progress_is_terminal(self):
        for name, issue in (("stdin_early", "CHANNEL_INPUT"), ("write_stall", "CHANNEL_STALLED"), ("input_stall", "CHANNEL_STALLED")):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["started"], r["import_release_sent"]), (issue, 1, 0))
                self.assertTrue(r["cleanup_complete"])

    def test_shared_io_output_and_regular_time_limits(self):
        for name, issue in (("io_limit", "CHANNEL_IO"), ("byte_limit", "CHANNEL_BYTES"), ("timeout", "CHANNEL_TIMEOUT")):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual(r["issue"], issue)
                self.assertTrue(r["cleanup_complete"])
                if name == "io_limit":
                    self.assertEqual((r["start_attempts"], r["started"], r["io_steps"],
                                      r["child_io_reserved"]), (0, 0, 0, 0))

    def test_real_eof_exit_orderings_and_inherited_pipes(self):
        for name, field in (("eof_first", "eof_before_exit"), ("exit_first", "exit_before_eofs")):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r[field], r["closed"]), ("NONE", 1, 1))
        r = self.run_case("inherited_stall")
        self.assertEqual((r["issue"], r["started"], r["zero_exits"]), ("CHANNEL_STALLED", 1, 1))
        self.assertTrue(r["cleanup_complete"])

    def test_native_nonzero_exit_after_handshake_remains_rejected(self):
        r = self.run_case("exit7")
        self.assertEqual((r["issue"], r["stdin_closed"], r["zero_exits"]), ("CHANNEL_EXIT", 1, 0))
        self.assertTrue(r["cleanup_complete"])

    def test_shared_native_owner_reentrancy_is_sticky_before_and_after_start(self):
        for name, count in (("reentrant_prepare", 0), ("reentrant_profile", 1)):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["first_issue"], r["started"], r["body_release_sent"]),
                                 ("CHANNEL_REENTRANT", "CHANNEL_REENTRANT", count, 0))
                self.assertEqual(r["nested"], ["CHANNEL_REENTRANT", "CHANNEL_REENTRANT"])
                self.assertTrue(r["cleanup_complete"])

    def test_binding_drift_before_command_commit_and_cleanup_sticky(self):
        for name, issue in (("provider_drift", "HASH_PROVIDER_BINDING"), ("encoder_drift", "REPORT_ENCODER_BINDING"),
                            ("both_drift", "HASH_PROVIDER_BINDING")):
            with self.subTest(case=name):
                r = self.run_case(name)
                self.assertEqual((r["issue"], r["body_release_sent"]), (issue, 0))
                self.assertTrue(r["cleanup_complete"])
        r = self.run_case("cleanup_sticky")
        self.assertEqual((r["issue"], r["started"], r["closed"]), ("CHANNEL_CLEANUP", 1, 0))
        self.assertFalse(r["cleanup_complete"])


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--native-case": native_case(sys.argv[2])
    else: unittest.main()
