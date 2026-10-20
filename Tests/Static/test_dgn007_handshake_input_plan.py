"""Gehaltene Inputs und gemeinsame Transferkosten; keine Worker oder alten Tests."""
import ast
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import struct
import sys
from types import FunctionType
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_session_match as fixture
import dgn007_handshake_input_plan as subject

ROLES = ("METADATA", "REPORTED", "pooled-installation-declaration/v1",
         "pooled-worker-declaration/v1", "pooled-profile-binding-context/v1")
KINDS = ("BODY_RELEASE", "BODY_END", "IMPORT_RELEASE")


def payload_for(ordinal=1, bodies=None, padding=0):
    payload = fixture.fixture.semantic_fixture(ordinal)
    bodies = tuple(b"synthetic-source-" + str(n).encode() for n in range(9)) if bodies is None else bodies
    rows = tuple(row[:3] + (len(body), hashlib.sha256(body).hexdigest())
                 for row, body in zip(payload[0][5], bodies))
    payload = fixture.fixture.semantic_change(payload, (0, 5), rows)
    payload = fixture.fixture.semantic_change(payload, (2, 4), rows)
    payload = fixture.fixture.InlineMetadataMatchTests.rehashed(None, payload)
    if padding:
        prefixes = tuple("/synthetic/p%d/" % n + "x" * padding for n in range(4))
        payload = fixture.fixture.semantic_change(payload, (1, 3, 6), prefixes)
    return payload, bodies


def selected(payload=None, bodies=None, *, ordinal=1, actual=None, padding=0):
    if payload is None:
        payload, bodies = payload_for(ordinal, bodies, padding)
    actual = payload if actual is None else actual
    metadata = fixture.pooled(actual, "METADATA")
    header = struct.pack(">8sII", b"DGNC001\0", len(metadata), sum(r[3] for r in actual[0][5]))
    raw = header + metadata
    chunks = tuple(raw[n:n + 1024] for n in range(0, len(raw), 1024))
    reported = (payload[2],) + payload[1][3:]
    return subject.HandshakeInputSelection(chunks, bodies, *payload, reported)


def oracle_forms(item):
    payload = (item.input_metadata, item.worker, item.context)
    values = (payload, item.reported, (item.worker[3],), (item.worker,), (item.context,))
    return tuple(fixture.pooled(value, role) for role, value in zip(ROLES, values))


def oracle_commands(item):
    return tuple(fixture.line((kind, item.context[5], item.context[3], fixture.context_sha(item.context)))
                 for kind in KINDS)


def _padded_json(form, anchor):
    raw = _plan_test_original_json(form, anchor)
    if type(form) is tuple and len(form) == 4 and form[0] == "pooled-binding-design/v1" and form[1] != "METADATA":
        return raw + b" " * max(0, _plan_test_target - len(raw))
    return raw


class HandshakeInputTests(unittest.TestCase):
    def setUp(self):
        self.f = fixture.SessionMatchTests(methodName="runTest")
        self.f.setUp()
        self.ns = self.f.namespace

    def tearDown(self):
        self.f.tearDown()

    def call(self, selections=None, **kwargs):
        return subject.plan_handshake_inputs(self.ns, (selected(),) if selections is None else selections,
                                             expected_format=kwargs.get("format", subject.FORMAT))

    def reject(self, report, issue=None):
        self.assertEqual(report.status, "REJECTED_HANDSHAKE_INPUTS")
        self.assertEqual((report.plans, report.transfer_bytes), ((), 0))
        if issue is not None: self.assertEqual(report.issue, issue)
        self.assertEqual(repr(report), "HandshakePlanReport(PROJECT_SEMANTIC)")

    def test_full_role_prefixes_original_bytes_and_independent_oracles(self):
        for count in (1, 2, 3):
            items = tuple(selected(ordinal=n) for n in range(1, count + 1))
            result = self.call(items)
            self.assertEqual((result.status, result.issue), ("PLANNED_DECLARED_HANDSHAKE_INPUTS", "NONE"))
            self.assertEqual(len(result.plans), count)
            for item, plan in zip(items, result.plans):
                self.assertIs(plan.selected, item)
                self.assertEqual(plan.header + plan.metadata, b"".join(item.metadata_chunks))
                self.assertEqual(plan.commands, oracle_commands(item))
                self.assertEqual(plan.form_sizes, tuple(16 + len(raw) for raw in oracle_forms(item)))
                self.assertEqual(plan.transfer_bytes, sum(map(len, item.metadata_chunks + item.bodies + plan.commands)))
                self.assertTrue(all(a is b for a, b in zip(plan.selected.bodies, item.bodies)))
            self.assertEqual(result.transfer_bytes, sum(plan.transfer_bytes for plan in result.plans))

    def test_frozen_private_reports_and_explicit_false_claims(self):
        result = self.call()
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(result, key), False)
        for obj, key in ((result, "status"), (result.plans[0], "metadata"), (result.plans[0].selected, "bodies")):
            with self.assertRaises(FrozenInstanceError): setattr(obj, key, None)
        self.assertNotIn("/synthetic", repr(result.plans[0]))

    def test_all_caller_types_and_last_slot_precede_sha(self):
        a, b, c = (selected(ordinal=n) for n in (1, 2, 3))
        foreign = fixture.fixture.Foreign()
        cases = ((), [a], (foreign,), (replace(a, bodies=foreign),), (replace(a, reported=foreign),),
                 (a, b, replace(c, metadata_chunks=(foreign,))),
                 (a, b, replace(c, bodies=c.bodies[:-1] + (foreign,))),
                 (a, b, replace(c, context=c.context[:5] + (True,) + c.context[6:])))
        for index, items in enumerate(cases):
            with self.subTest(index=index): self.reject(self.call(items), "PLAN_FORM")
        self.assertEqual(self.f.provider._HASH_CALLS, 0)

    def test_raw_chunk_body_and_metadata_limits_precede_sha(self):
        one = selected()
        cases = (replace(one, bodies=one.bodies[:-1]), replace(one, bodies=(b"x" * 131073,) + one.bodies[1:]),
                 replace(one, bodies=(b"x" * 131072,) * 9), replace(one, metadata_chunks=(b"x" * 1025,)),
                 replace(one, metadata_chunks=(b"",) * 257), replace(one, metadata_chunks=(b"",)),
                 replace(one, metadata_chunks=(b"x" * 1024,) * 17))
        for index, item in enumerate(cases):
            with self.subTest(index=index): self.reject(self.call((item,)), "PLAN_FORM")
        self.assertEqual(self.f.provider._HASH_CALLS, 0)

    def test_separate_whole_r_and_cohort_bindings_precede_sha(self):
        one, two = selected(), selected(ordinal=2)
        changed = fixture.fixture.semantic_change(one.reported, (1, 3, 2), 15)
        for items in ((two,), (one, one), (replace(one, reported=changed),),
                      (one, replace(two, context=one.context))):
            self.reject(self.call(items), "PLAN_BINDING")
        self.assertEqual(self.f.provider._HASH_CALLS, 0)

    def test_all_nine_actual_body_hashes_and_no_partial_plan(self):
        first, second = selected(), selected(ordinal=2)
        for index in range(9):
            bodies = list(second.bodies); bodies[index] = b"X" + bodies[index][1:]
            self.reject(self.call((first, replace(second, bodies=tuple(bodies)))), "PLAN_RECEIVE")

    def test_original_input_digest_and_received_full_binding(self):
        payload, bodies = payload_for()
        bad = fixture.fixture.semantic_change(payload, (0, 6), "0" * 64)
        self.reject(self.call((selected(payload, bodies, actual=bad),)), "PLAN_RECEIVE")
        other = fixture.fixture.semantic_change(payload, (0, 4), "5" * 64)
        other = fixture.fixture.semantic_change(other, (2, 3), "5" * 64)
        other = fixture.fixture.InlineMetadataMatchTests.rehashed(None, other)
        self.reject(self.call((selected(payload, bodies, actual=other),)), "PLAN_RECEIVE")

    def test_header_truncation_suffix_and_noncanonical_metadata(self):
        one = selected(); raw = b"".join(one.metadata_chunks)
        for data in (raw[:-1], raw + b"x", b"WRONGMAG" + raw[8:], raw[:16] + b" " + raw[16:]):
            chunks = tuple(data[n:n + 1024] for n in range(0, len(data), 1024))
            self.reject(self.call((replace(one, metadata_chunks=chunks),)), "PLAN_RECEIVE")

    def test_commands_are_three_distinct_context_bound_domains_with_lf(self):
        item = selected(); report = self.call((item,))
        commands = report.plans[0].commands
        self.assertEqual(tuple(json.loads(raw)[0] for raw in commands), KINDS)
        self.assertTrue(all(raw.endswith(b"\n") and raw.count(b"\n") == 1 and len(raw) <= 256 for raw in commands))
        self.assertTrue(all(json.loads(raw)[3] != item.input_metadata[6] for raw in commands))
        self.assertEqual(commands, oracle_commands(item))

    def test_per_form_and_joint_formset_limits_fail_atomically(self):
        # Kontrollierte Dependency-Gegenprobe: Größen nach korrektem JSONdispatch aufblasen.
        # Echte Metadata/Hashes bleiben intakt; keine Ausgabe oder Nativequalifikation.
        original = self.ns["_report_json"]
        wrapper = FunctionType(_padded_json.__code__, self.ns)
        for target in (16368, 16369):
            with self.subTest(target=target), patch.dict(self.ns, {
                    "_report_json": wrapper, "_plan_test_original_json": original, "_plan_test_target": target}):
                self.reject(self.call(), "PLAN_FORMSET_LIMIT")

    def test_real_exact_transfer_cap_includes_commands_without_extra_budget(self):
        bodies = (b"x" * 131072,) * 8 + (b"",)
        low, high = 0, 4050
        while low < high:
            middle = (low + high + 1) // 2
            item = selected(bodies=bodies, padding=middle)
            size = len(b"".join(item.metadata_chunks))
            if size <= 16250: low = middle
            else: high = middle - 1
        large = selected(bodies=bodies, padding=low)
        raw_cost = sum(map(len, large.metadata_chunks + large.bodies + oracle_commands(large)))
        excess = raw_cost - 1064960
        self.assertGreater(excess, 0)
        trimmed = (bodies[0][:-excess],) + bodies[1:]
        exact = selected(bodies=trimmed, padding=low)
        # Neue Rawhashes können Stringpoolpositionen verändern. Ein reiner S15-
        # Prefixtext gleicht die tatsächlichen Bytes ohne weitere I7/K-Hashänderung aus.
        delta = sum(map(len, exact.metadata_chunks + exact.bodies + oracle_commands(exact))) - 1064960
        prefixes = list(exact.worker[3][6])
        if delta > 0: prefixes[0] = prefixes[0][:-delta]
        elif delta < 0: prefixes[0] += "x" * -delta
        payload = fixture.fixture.semantic_change((exact.input_metadata, exact.worker, exact.context),
                                                  (1, 3, 6), tuple(prefixes))
        exact = selected(payload, trimmed)
        self.assertEqual(sum(map(len, exact.metadata_chunks + exact.bodies + oracle_commands(exact))), 1064960)
        self.assertEqual(self.call((exact,)).issue, "NONE")
        prefixes[0] += "x"
        over_payload = fixture.fixture.semantic_change(payload, (1, 3, 6), tuple(prefixes))
        over = selected(over_payload, trimmed)
        self.reject(self.call((over,)), "PLAN_TRANSFER_LIMIT")

    def test_raw_crlf_and_empty_bodies_remain_original(self):
        bodies = (b"\r\n", b"", b"\xff\0") + (b"unchanged\n",) * 6
        item = selected(bodies=bodies)
        report = self.call((item,))
        self.assertEqual(report.issue, "NONE")
        self.assertIs(report.plans[0].selected.bodies, bodies)

    def test_provider_encoder_and_owner_drift_after_actual_hash(self):
        original_sha, default = self.f.provider.sha256, json.JSONEncoder.default
        original_command = self.ns["_inline_command_encode"]
        for kind, issue in (("provider", "HASH_PROVIDER_BINDING"), ("encoder", "REPORT_ENCODER_BINDING"),
                            ("both", "HASH_PROVIDER_BINDING"), ("owner", "PLAN_OWNER")):
            def drift():
                if kind in ("provider", "both"): self.f.provider.sha256 = lambda *_: None
                if kind in ("encoder", "both"): json.JSONEncoder.default = lambda *_: None
                if kind == "owner": self.ns["_inline_command_encode"] = lambda *_: None
            try:
                self.f.provider._HASH_CALLBACK = drift
                self.reject(self.call(), issue)
            finally:
                self.f.provider._HASH_CALLBACK = None
                self.f.provider.sha256 = original_sha
                json.JSONEncoder.default = default
                self.ns["_inline_command_encode"] = original_command

    def test_foreign_helper_and_format_fail_without_foreign_dispatch(self):
        for value in (fixture.fixture.Foreign(), None, True, "other"):
            self.reject(self.call(format=value), "PLAN_FORM")
        with patch.dict(self.ns, {"_inline_command_encode": fixture.fixture.Foreign()}):
            self.reject(self.call(), "PLAN_OWNER")
        self.assertEqual(self.f.provider._HASH_CALLS, 0)

    def test_private_exceptions_never_escape_or_appear_in_report(self):
        try:
            self.f.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
            self.reject(self.call(), "PLAN_RECEIVE")
        finally: self.f.provider._HASH_ERROR = None
        self.assertEqual(subject._issue(ValueError("PRIVATE_PAYLOAD")), "PLAN_FORM")
        self.assertEqual(subject._issue(ValueError("x" * 100000)), "PLAN_FORM")

    def test_no_process_io_phase_or_public_receipt_dispatch(self):
        tree = ast.parse(Path(subject.__file__).read_text(encoding="utf-8"))
        forbidden = {"open", "read", "write", "Popen", "poll", "wait", "communicate", "print", "exec", "compile"}
        self.assertFalse(any(isinstance(node, ast.Call) and (
            isinstance(node.func, ast.Name) and node.func.id in forbidden or
            isinstance(node.func, ast.Attribute) and node.func.attr in forbidden) for node in ast.walk(tree)))
        self.assertEqual({node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call)
                          and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                          and node.func.value.id == "channel"}, {"_Control", "_dominant"})


if __name__ == "__main__":
    unittest.main()
