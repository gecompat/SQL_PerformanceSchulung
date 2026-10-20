"""Vollständige deklarative SESSION_END-Gegenproben mit eigenen Traces/Oracles."""
import ast
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_control_bootstrap_source as fixture

subject = fixture.subject
FORMAT = "pooled-combined-input-design/v1"
OMITTED = object()
# Eigene Ereignisnotation; keine Implementierungstabellen als Sollwerte.
EVENTS = {
    1: ("S0+", "S1+", "S5+", "S5-", "S1-", "S3+", "S4+", "S4-", "S3-",
        "P0+", "P0-", "P1+", "P1-", "S6+", "S7+", "S8+", "S8-", "S7-", "S6-", "S0-"),
    2: ("S2+", "S2-"),
    3: ("S3+", "S4+", "S5+", "S5-", "S4-", "S3-"),
}


def line(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii") + b"\n"


def pooled(payload, role):
    texts = set()
    def collect(value):
        if type(value) is str:
            texts.add(value)
        elif type(value) is tuple:
            for child in value:
                collect(child)
    collect(payload)
    pool = tuple(sorted(texts))
    def project(value):
        if type(value) is str:
            return pool.index(value)
        if type(value) is tuple:
            return tuple(project(child) for child in value)
        return value
    return line(("pooled-binding-design/v1", role, pool, project(payload)))[:-1]


def context_sha(context):
    return hashlib.sha256(pooled((context,), "pooled-profile-binding-context/v1")).hexdigest()


def channel_sha(prefix, err, context, ordinal):
    # Unabhängige binäre Konkatenation, nicht der inkrementelle Implementierungspfad.
    raw = (b"DGN007-SESSION-CHANNEL/v1\x00" + {1: b"\x01", 2: b"\x02", 3: b"\x03"}[ordinal]
           + bytes.fromhex(context) + len(prefix).to_bytes(4, "big") + prefix
           + len(err).to_bytes(4, "big") + err)
    return hashlib.sha256(raw).hexdigest()


class SessionMatchTests(unittest.TestCase):
    # Nur Harnessmethoden, keine alten Tests mitvererben oder ausführen.
    records = fixture.InlineProfileRecordsMatchTests.records
    bytes_for = fixture.InlineProfileRecordsMatchTests.bytes_for

    def setUp(self):
        selected = subject.build_inline_session_end_control_bootstrap(
            fixture.RAW, logical_profile=fixture.LOCATOR,
            expected_soabi=fixture.SOABI, expected_destshared=fixture.DESTSHARED)
        with patch.object(subject, "build_inline_profile_records_match_control_bootstrap", return_value=selected):
            fixture.InlineProfileRecordsMatchTests.setUp(self)
        self.match = self.namespace["_inline_match_session_end"]
        self.rows, self.err = self.make_session()
        self.provider_baseline = dict(self.provider.__dict__)
        self.native_baseline = dict(self.native.__dict__)
        self.factory_state = self.function_state(self.factory)
        self.fourth_encoder = sys.modules["json.encoder"]._make_iterencode
        self.fourth_state = self.function_state(self.fourth_encoder)

    @staticmethod
    def function_state(fn):
        return (fn.__code__, fn.__defaults__, fn.__kwdefaults__, fn.__closure__,
                dict(fn.__dict__), None if fn.__kwdefaults__ is None else dict(fn.__kwdefaults__))

    def same_mapping(self, actual, expected):
        self.assertEqual(set(actual), set(expected))
        self.assertTrue(all(actual[key] is expected[key] for key in expected))

    def same_function(self, fn, state):
        self.assertIs(fn.__code__, state[0]); self.assertIs(fn.__defaults__, state[1])
        self.assertIs(fn.__kwdefaults__, state[2]); self.assertIs(fn.__closure__, state[3])
        self.same_mapping(fn.__dict__, state[4])
        if state[5] is not None:
            self.same_mapping(fn.__kwdefaults__, state[5])

    def tearDown(self):
        # Tatsächliche Abschlussprüfung; kein pauschales Reparieren vor dem Vergleich.
        fixture.InlineProfileRecordsMatchTests.tearDown(self)
        self.same_function(self.fourth_encoder, self.fourth_state)
        self.same_function(self.factory, self.factory_state)
        self.same_mapping(self.native.__dict__, self.native_baseline)
        self.assertIs(type(self.provider._HASH_CALLS), int)
        self.assertGreaterEqual(self.provider._HASH_CALLS, 0)
        self.same_mapping({k: v for k, v in self.provider.__dict__.items() if k != "_HASH_CALLS"},
                          {k: v for k, v in self.provider_baseline.items() if k != "_HASH_CALLS"})

    def make_session(self, reported=None, stderr=b""):
        reported = self.reported if reported is None else reported
        context = reported[0]; ordinal = context[5]; digest = context_sha(context)
        _, metadata, _ = self.bytes_for(reported)
        profile = self.records(metadata, ordinal)
        loaders, sequences = [], {}
        for event in EVENTS[ordinal]:
            source = event[0] == "S"; index = int(event[1:-1]); begin = event[-1] == "+"
            key = event[:-1]
            if begin:
                sequences[key] = len(sequences) + 1
            seq = sequences[key]
            loaders.append(line(("BEGIN" if begin else "COMPLETE", ordinal, seq,
                                 "SOURCE" if source else "PARENT", index, digest,
                                 context[4][index][4] if source else None,
                                 index if source else 9 + index, seq)))
        prefix_rows = profile + (line(("INPUT_COMPLETE", ordinal, context[3], digest)),) + tuple(loaders)
        prefix = b"".join(prefix_rows)
        f = len(profile) - 2
        sources = sum(event.startswith("S") and event.endswith("+") for event in EVENTS[ordinal])
        parents = sum(event.startswith("P") and event.endswith("+") for event in EVENTS[ordinal])
        footer = ("SESSION_END", ordinal, digest, f, sources, sources, parents, parents,
                  len(prefix_rows) + 1, len(prefix), len(stderr), channel_sha(prefix, stderr, digest, ordinal))
        return prefix_rows + (line(footer),), stderr

    def reseal(self, rows, stderr=b""):
        footer = list(json.loads(rows[-1]))
        prefix = b"".join(rows[:-1])
        footer[9:12] = len(prefix), len(stderr), channel_sha(prefix, stderr, footer[2], footer[1])
        return rows[:-1] + (line(footer),)

    def changed_row(self, rows, index, field, value, seal=True):
        row = json.loads(rows[index]); row[field] = value
        rows = rows[:index] + (line(row),) + rows[index + 1:]
        return self.reseal(rows) if seal and index != len(rows) - 1 and index != -1 else rows

    def call(self, rows=OMITTED, stderr=OMITTED, *, reported=OMITTED, context=OMITTED,
             format=FORMAT, phase="AWAIT_SESSION_END"):
        return self.match(self.rows if rows is OMITTED else rows, self.err if stderr is OMITTED else stderr,
                          expected_format=format, expected_phase=phase,
                          expected_reported=self.reported if reported is OMITTED else reported,
                          expected_context=self.reported[0] if context is OMITTED else context)

    def reject(self, result, issue=None):
        self.assertEqual(result[0], "REJECTED_SESSION_END")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("PRIVATE_PAYLOAD", repr(result))
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_three_complete_named_traces_and_original_footer(self):
        for ordinal in (1, 2, 3):
            payload = fixture.semantic_fixture(ordinal)
            reported, _, _ = fixture.reporter_reference(payload, fixture.reporter_scalars(payload))
            rows, err = self.make_session(reported, b"\x00\xff\r\n")
            result = self.call(rows, err, reported=reported, context=reported[0])
            self.assertEqual(result[:2], ("MATCHED_DECLARED_SESSION_END", "NONE"))
            self.assertIs(result[2][0], rows[-1])
            self.assertEqual(result[2][1], tuple(json.loads(rows[-1])))
            self.assertEqual(sum(json.loads(r)[0] == "BEGIN" for r in rows if not r.startswith(b"P|")),
                             {1: 10, 2: 1, 3: 3}[ordinal])
        self.assertEqual(self.provider._HASH_CALLS, 9)

    def test_repeat_is_declarative_without_consumption(self):
        self.assertEqual(self.call(), self.call())
        self.assertEqual(self.provider._HASH_CALLS, 6)
        self.assertIs(type(self.call()), tuple)

    def test_all_outer_types_before_dispatch_and_parser(self):
        class Bytes(bytes):
            def __len__(self): raise AssertionError("FOREIGN_LENGTH")
        class Tuple(tuple):
            def __len__(self): raise AssertionError("FOREIGN_LENGTH")
        for rows in (None, list(self.rows), Tuple(self.rows), fixture.Foreign()):
            self.reject(self.call(rows), "SESSION_END_TYPE")
        for err in (None, bytearray(), memoryview(b""), Bytes(b""), fixture.Foreign()):
            self.reject(self.call(stderr=err), "SESSION_END_TYPE")
        rows = (b"x" * 1025,) + self.rows[1:-1] + (fixture.Foreign(),)
        self.reject(self.call(rows), "SESSION_END_TYPE")
        self.reject(self.call((Bytes(b"x"),) + self.rows[1:]), "SESSION_END_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_complete_caller_forms_before_record_parse_or_sha(self):
        for path in ((0, 4, 8, 4), (3, len(self.reported[3]) - 1, 10)):
            invalid = fixture.semantic_change(self.reported, path, fixture.Foreign())
            self.reject(self.call((b"!\n",), reported=invalid), "SCALAR_FORM")
        context = fixture.semantic_change(self.reported[0], (4, 8, 4), fixture.Foreign())
        self.reject(self.call(context=context), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_caller_selection_and_full_k_semantics_before_hash(self):
        self.reject(self.call(format="other"), "FORMAT_SELECTION")
        self.reject(self.call(phase="AWAIT_PROFILE"), "PHASE_SELECTION")
        for path, value in (((7,), "POST_IMPORT"), ((4, 8, 4), "G" * 64)):
            context = fixture.semantic_change(self.reported[0], path, value)
            self.reject(self.call(context=context))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_actual_form_and_semantics_precede_valid_caller_difference(self):
        expected = fixture.semantic_change(self.reported, (0, 0), "d" * 40)
        for path, value in (((0, 4, 8, 4), None), ((0, 4, 8, 4), "G" * 64),
                            ((3, len(self.reported[3]) - 1, 10), ("wrong",))):
            actual = fixture.semantic_change(self.reported, path, value)
            rows, err = self.make_session(actual)
            self.reject(self.call(rows, err, reported=expected))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_loader_footer_form_before_valid_caller_difference(self):
        expected = fixture.semantic_change(self.reported, (0, 0), "d" * 40)
        for index, field, value in ((len(self.rows) - 2, 6, "G" * 64),
                                    (-1, 11, None), (-1, 11, "G" * 64)):
            rows = self.changed_row(self.rows, index, field, value, seal=False)
            self.reject(self.call(rows, reported=expected))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_separate_full_k_and_r_bindings(self):
        for path, value in (((0,), "d" * 40), ((1,), "b" * 64), ((3,), "f" * 64),
                            ((4, 8, 4), "c" * 64)):
            expected = fixture.semantic_change(self.reported[0], path, value)
            self.reject(self.call(context=expected), "SESSION_END_BINDING")
        expected = fixture.semantic_change(self.reported, (1, 3, 2), 99)
        self.reject(self.call(reported=expected), "SESSION_END_BINDING")

    def test_every_loader_field_binding_and_pair(self):
        loader = len(self.rows) - 21
        changes = ((1, 2), (2, 2), (3, "PARENT"), (4, 2), (5, "f" * 64),
                   (6, "e" * 64), (7, 8), (8, 2))
        for field, value in changes:
            self.reject(self.call(self.changed_row(self.rows, loader, field, value)))
        # Kohärente falsche Raw-/Kontextpaare sind erst Crossbindungsfehler.
        for field in (5, 6):
            rows = self.changed_row(self.rows, loader, field, "f" * 64)
            rows = self.changed_row(rows, len(rows) - 2, field, "f" * 64)
            self.reject(self.call(rows), "SESSION_END_BINDING")

    def test_source_null_parent_hash_and_foreign_parent_rejected(self):
        for index, row in enumerate(self.rows):
            if row.startswith(b"P|"): continue
            value = json.loads(row)
            if value[0] == "BEGIN":
                self.reject(self.call(self.changed_row(self.rows, index, 6,
                    None if value[3] == "SOURCE" else "a" * 64)))
        parent = next(i for i, r in enumerate(self.rows) if b'"PARENT"' in r)
        self.reject(self.call(self.changed_row(self.rows, parent, 4, 2)))

    def test_missing_duplicate_reordered_pairs_and_equal_counts(self):
        loader = len(self.rows) - 21
        for index in range(loader, len(self.rows) - 1):
            rows = self.rows[:index] + self.rows[index + 1:]
            self.reject(self.call(self.reseal(rows)))
        rows = list(self.rows); rows[loader + 2], rows[loader + 3] = rows[loader + 3], rows[loader + 2]
        self.reject(self.call(self.reseal(tuple(rows))), "SESSION_END_ORDER")
        rows = list(self.rows); rows[loader + 3] = rows[loader + 4]
        self.reject(self.call(self.reseal(tuple(rows))), "SESSION_END_ORDER")

    def test_footer_all_declared_fields_and_complete_record_count(self):
        for field in range(1, 12):
            value = json.loads(self.rows[-1])[field]
            self.reject(self.call(self.changed_row(self.rows, -1, field,
                        "f" * 64 if type(value) is str else value + 1)))
        self.reject(self.call(self.changed_row(self.rows, -1, 8, 43)), "SESSION_END_COUNTS")

    def test_absent_duplicate_early_footer_and_stdout_after_footer(self):
        self.reject(self.call(self.rows[:-1]), "SESSION_END_MISSING")
        for rows in (self.rows + (self.rows[-1],),
                     (self.rows[-1],) + self.rows[:-1], self.rows + (b"{}\n",)):
            self.reject(self.call(rows))
        # Auch ein gültiger anderer Controlrecord nach Footer scheitert.
        self.reject(self.call(self.rows + (self.rows[0],)))

    def test_profile_fragment_and_input_complete_bindings(self):
        first = self.rows[1]
        for bad in (first.replace(b"P|1|1|", b"P|2|1|", 1),
                    first.replace(b"P|1|1|", b"P|1|2|", 1)):
            rows = self.reseal((self.rows[0], bad) + self.rows[2:])
            self.reject(self.call(rows))
        index = next(i for i, r in enumerate(self.rows) if b'"INPUT_COMPLETE"' in r)
        for field, value in ((1, 2), (2, "f" * 64), (3, "e" * 64)):
            self.reject(self.call(self.changed_row(self.rows, index, field, value)), "SESSION_END_BINDING")
        self.reject(self.call(self.reseal(self.rows[:index] + self.rows[index + 1:])), "SESSION_END_MISSING")

    def test_context_domain_profile_digest_and_channel_digest_are_distinct(self):
        footer = json.loads(self.rows[-1]); end = json.loads(self.rows[len(self.rows) - 23])
        self.assertEqual(len({footer[2], footer[11], end[4]}), 3)
        wrong = hashlib.sha256(pooled((self.reported[0],), "REPORTED")).hexdigest()
        self.reject(self.call(self.changed_row(self.rows, -1, 2, wrong)), "SESSION_END_BINDING")

    def test_opaque_stderr_truncation_added_bytes_and_channel_swap(self):
        rows, err = self.make_session(stderr=b"\xff\x00A\r\n")
        self.assertEqual(self.call(rows, err)[0], "MATCHED_DECLARED_SESSION_END")
        for changed in (err[:-1], err + b"x", err.replace(b"\r\n", b"\n")):
            self.reject(self.call(rows, changed), "SESSION_END_CHANNEL")
        swapped = list(json.loads(rows[-1]))
        swapped[11] = channel_sha(err, b"".join(rows[:-1]), swapped[2], swapped[1])
        self.reject(self.call(rows[:-1] + (line(swapped),), err), "SESSION_END_CHANNEL")

    def test_noncanonical_controls_loader_and_footer(self):
        indices = [0, len(self.rows) - 23, len(self.rows) - 22, len(self.rows) - 21, len(self.rows) - 1]
        for index in indices:
            old = self.rows[index]
            for bad in (b" " + old, old.replace(b",", b", ", 1),
                        old.replace(b'"', b'"\\u0053', 1)):
                rows = self.rows[:index] + (bad,) + self.rows[index + 1:]
                self.reject(self.call(rows))
        for bad in (self.rows[-1][:-1], self.rows[-1] + b"\n",
                    self.rows[-1].replace(b"\n", b"\r\n"), b"\xff\n", b"[" * 100 + b"]" * 100 + b"\n"):
            self.reject(self.call(self.rows[:-1] + (bad,)))

    def test_json_bool_float_null_and_missing_or_added_fields(self):
        for index in (0, len(self.rows) - 21, len(self.rows) - 1):
            for field in range(len(json.loads(self.rows[index]))):
                for bad in (True, 1.5, None):
                    self.reject(self.call(self.changed_row(self.rows, index, field, bad, seal=False)))
            row = json.loads(self.rows[index])
            for value in (row[:-1], row + [0]):
                self.reject(self.call(self.rows[:index] + (line(value),) + self.rows[index + 1:]))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_bounds_before_parser_and_shared_exact_65536(self):
        for rows in ((), (b"x\n",) * 44, (b"x" * 1025,) + self.rows[1:]):
            self.reject(self.call(rows), "SESSION_END_LIMIT")
        self.reject(self.call(stderr=b"x" * 65536), "SESSION_END_LIMIT")
        # Fester Punkt der Footerbreite; gesamte tatsächliche Menge inklusive Footer.
        err_size = 60000
        for _ in range(4):
            rows, err = self.make_session(stderr=b"x" * err_size)
            err_size = 65536 - sum(map(len, rows))
        rows, err = self.make_session(stderr=b"x" * err_size)
        self.assertEqual(sum(map(len, rows)) + len(err), 65536)
        self.assertEqual(self.call(rows, err)[0], "MATCHED_DECLARED_SESSION_END")
        self.reject(self.call(rows, err + b"x"), "SESSION_END_LIMIT")

    def test_provider_encoder_pre_and_private_constructor_failure(self):
        with patch.object(self.provider, "sha256", fixture.Foreign()):
            self.reject(self.call(), "HASH_PROVIDER_BINDING")
        with patch.object(json.JSONEncoder, "default", fixture.Foreign()):
            self.reject(self.call(), "REPORT_ENCODER_BINDING")
        with patch.object(self.provider, "_HASH_ERROR", RuntimeError("PRIVATE_PAYLOAD")):
            self.reject(self.call(), "HASH_PROVIDER_CALL")

    def test_each_sha_constructor_drift_and_dominant_post(self):
        for target in (1, 2, 3):
            self.provider._HASH_CALLS = 0
            old = self.provider.sha256
            def drift():
                if self.provider._HASH_CALLS == target:
                    self.provider.sha256 = fixture.Foreign()
            try:
                with patch.object(self.provider, "_HASH_CALLBACK", drift):
                    self.reject(self.call(), "HASH_PROVIDER_BINDING")
            finally:
                self.provider.sha256 = old
            self.assertEqual(self.provider._HASH_CALLS, target)

    def test_outer_anchors_cover_every_repack_and_fourth_encoder_function(self):
        encode = self.namespace["_report_json"]
        old_code = self.fourth_encoder.__code__
        def changed(*args): return None
        count = sum(not row.startswith(b"P|") for row in self.rows) + 2
        for target in range(1, count + 1):
            calls = []
            def drifting(value, anchor):
                data = encode(value, anchor)
                calls.append(value)
                if len(calls) == target:
                    self.fourth_encoder.__code__ = changed.__code__
                    raise RuntimeError("PRIVATE_PAYLOAD")
                return data
            try:
                with patch.dict(self.namespace, {"_report_json": drifting}):
                    self.reject(self.call(), "REPORT_ENCODER_BINDING")
            finally:
                self.fourth_encoder.__code__ = old_code
            self.assertEqual(len(calls), target)

    def test_actual_iterencoder_provider_drift_blocks_constructor(self):
        cls, original = json.JSONEncoder, json.JSONEncoder.iterencode
        old_code = self.factory.__code__
        namespace = self.real_encoder_module.__dict__
        keys = ("_REPORT_FACTORY", "_REPORT_REPLACEMENT_CODE", "_REPORT_HELD_ITER")
        self.assertTrue(all(key not in namespace for key in keys))
        namespace.update(_REPORT_FACTORY=self.factory,
                         _REPORT_REPLACEMENT_CODE=fixture._fixture_config_var.__code__,
                         _REPORT_HELD_ITER=original)
        try:
            cls.iterencode = FunctionType(fixture._fixture_report_encoder_exchange_provider.__code__, namespace)
            self.reject(self.call(), "HASH_PROVIDER_BINDING")
        finally:
            cls.iterencode = original
            self.factory.__code__ = old_code
            for key in keys:
                del namespace[key]
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_encoder_and_provider_post_dominate_private_error(self):
        encode = self.namespace["_report_json"]; old = self.provider.sha256
        old_default = json.JSONEncoder.default
        def drift(value, anchor):
            encode(value, anchor)
            self.provider.sha256 = fixture.Foreign()
            json.JSONEncoder.default = lambda self, value: None
            raise RuntimeError("PRIVATE_PAYLOAD")
        try:
            with patch.dict(self.namespace, {"_report_json": drift}):
                self.reject(self.call(), "HASH_PROVIDER_BINDING")
        finally:
            self.provider.sha256 = old
            json.JSONEncoder.default = old_default

    def test_channel_constructor_encoder_loss_and_wrong_object(self):
        old_default = json.JSONEncoder.default
        def drift():
            if self.provider._HASH_CALLS == 3:
                json.JSONEncoder.default = lambda self, value: None
        try:
            with patch.object(self.provider, "_HASH_CALLBACK", drift):
                self.reject(self.call(), "REPORT_ENCODER_BINDING")
        finally:
            json.JSONEncoder.default = old_default
        with patch.object(self.provider, "_HASH_RESULT", fixture.Foreign()):
            self.reject(self.call(), "HASH_PROVIDER_OBJECT")

    def test_unknown_private_issue_and_active_exception_do_not_escape(self):
        def fail(*args):
            raise self.namespace["_InlineSyntaxRejected"]("PRIVATE_PAYLOAD")
        with patch.dict(self.namespace, {"_session_parse": fail}):
            try:
                raise ValueError("PRIVATE_PAYLOAD")
            except ValueError:
                self.reject(self.call(), "SESSION_END_FORM")

    def test_no_public_inner_rebaseline_or_runtime_adapter_delegation(self):
        keys = ("_inline_match_profile_records", "_inline_match_input_complete", "_inline_context_digest",
                "_inline_match_profile_report", "_inline_reassemble_profile_records", "_semantic_original_digest")
        with patch.dict(self.namespace, {key: fixture.Foreign() for key in keys}):
            self.assertEqual(self.call()[0], "MATCHED_DECLARED_SESSION_END")

    def test_prior_fourteen_builders_unchanged_five_imports_and_scriptcap(self):
        kwargs = dict(logical_profile=fixture.LOCATOR, expected_soabi=fixture.SOABI,
                      expected_destshared=fixture.DESTSHARED)
        previous = subject.build_inline_profile_records_match_control_bootstrap(fixture.RAW, **kwargs)
        self.assertEqual(self.selected.source.replace(
            ("\n" + subject._INLINE_SESSION_END_MATCH).encode(), b"", 1), previous.source)
        before, after = ast.parse(previous.source), ast.parse(self.selected.source)
        definitions = {node.name: ast.dump(node) for node in after.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        self.assertTrue(all(definitions[node.name] == ast.dump(node) for node in before.body
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef))))
        imports = [alias.name for node in after.body if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        builder = subject.build_inline_session_end_control_bootstrap
        overhead = len(builder(b"x", **kwargs).source) - 1
        raw = b"x" * (131072 - overhead)
        selected = builder(raw, **kwargs)
        self.assertEqual(selected.source_size, 131072)
        self.assertIs(selected.profile_raw, raw)
        for value in (raw + b"x", b"\0" * len(raw)):
            with self.assertRaises(subject.BootstrapSourceRejected):
                builder(value, **kwargs)
        with self.assertRaises(FrozenInstanceError):
            selected.source = b"other"
        for name in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(selected, name), False)


if __name__ == "__main__":
    unittest.main()
