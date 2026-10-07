#!/usr/bin/env python3
"""Echte, feste synthetische Loaderfälle; keine DGN- oder Prozessausführung."""
from __future__ import annotations

import ast
import builtins
from dataclasses import FrozenInstanceError, replace
import hashlib
from importlib.machinery import ModuleSpec
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Tools"))
import dgn007_memory_loader_fixture as fixture


class MemoryLoaderTests(unittest.TestCase):
    def session(self, case=fixture.FixtureCase.LF_SUCCESS):
        return fixture._Session(case)

    def rejected(self, operation, issue=None):
        with self.assertRaises(fixture._Rejected) as caught:
            operation()
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        if issue:
            self.assertEqual(str(caught.exception), issue)

    def execute(self, session):
        session._loader.exec_module(session._module)
        return session._report()

    def test_real_success_receipts_have_exact_order_and_claim_boundaries(self):
        for case in (fixture.FixtureCase.LF_SUCCESS, fixture.FixtureCase.CRLF_SUCCESS):
            report = fixture.exercise_fixture(case)
            self.assertEqual((report.status, report.issue), ("PASS_SYNTHETIC_LOADER", "NONE"))
            self.assertEqual(tuple((r.sequence, r.phase) for r in report.receipts), ((1, "BEGIN"), (2, "COMPLETE")))
            self.assertEqual(report.claim, "SYNTHETIC_LOADER_COMPONENT_ONLY")
            self.assertEqual(report.validation_scope, "PROJECT_SEMANTIC")
            self.assertFalse(report.runtime_attested or report.import_used_bytes_attested or report.method_approved)
            self.assertEqual(report.receipts[0].nonce, report.receipts[1].nonce)
            self.assertEqual(report.receipts[0].context_digest, report.receipts[1].context_digest)

    def test_compile_receives_same_held_raw_bytes_after_begin(self):
        actual_compile = builtins.compile
        for case in (fixture.FixtureCase.LF_SUCCESS, fixture.FixtureCase.CRLF_SUCCESS):
            session = self.session(case)
            observed = []
            def measured(body, filename, mode, **flags):
                observed.append(body)
                self.assertIs(body, session._source.body)
                self.assertIs(body, session._begin_bytes)
                self.assertIs(session._begin_object, session._module)
                self.assertEqual(tuple(r.phase for r in session._receipts), ("BEGIN",))
                self.assertEqual(session._receipts[0].raw_sha256, hashlib.sha256(body).hexdigest())
                self.assertEqual((filename, mode, flags), (session._origin, "exec", {"dont_inherit": True, "optimize": 0}))
                return actual_compile(body, filename, mode, **flags)
            with patch("builtins.compile", side_effect=measured):
                self.execute(session)
            self.assertEqual(len(observed), 1)
            self.assertEqual(session._module.SYNTHETIC_VALUE, 7)

    def test_crlf_and_lf_hashes_are_distinct_without_normalization(self):
        lf = fixture._catalog(fixture.FixtureCase.LF_SUCCESS)
        crlf = fixture._catalog(fixture.FixtureCase.CRLF_SUCCESS)
        self.assertEqual(lf.body, crlf.body.replace(b"\r\n", b"\n"))
        self.assertNotEqual(lf.sha256, crlf.sha256)
        report = fixture.exercise_fixture(fixture.FixtureCase.CRLF_SUCCESS)
        self.assertEqual(report.receipts[0].raw_sha256, hashlib.sha256(crlf.body).hexdigest())

    def test_compile_and_exec_failures_never_complete_or_leak_error_text(self):
        for case, issue in ((fixture.FixtureCase.COMPILE_FAILURE, "FIXTURE_COMPILE_FAILED"),
                            (fixture.FixtureCase.EXEC_FAILURE, "FIXTURE_EXEC_FAILED")):
            report = fixture.exercise_fixture(case)
            self.assertEqual((report.status, report.issue), ("FAIL_SYNTHETIC_LOADER", issue))
            self.assertEqual(tuple(r.phase for r in report.receipts), ("BEGIN",))
            self.assertNotIn("Synthetic fixture failure", repr(report))
            self.assertFalse(report.runtime_attested or report.import_used_bytes_attested or report.method_approved)
            session = self.session(case)
            self.rejected(lambda: session._loader.exec_module(session._module), issue)
            self.rejected(session._report, "MISSING_COMPLETE")

    def test_no_finder_path_cache_or_global_module_registration(self):
        path, finders, hooks = tuple(sys.path), tuple(sys.meta_path), tuple(sys.path_hooks)
        cache, importer_cache = dict(sys.modules), dict(sys.path_importer_cache)
        for case in fixture.FixtureCase:
            fixture.exercise_fixture(case)
        self.assertEqual(tuple(sys.path), path)
        self.assertEqual(tuple(sys.meta_path), finders)
        self.assertEqual(tuple(sys.path_hooks), hooks)
        self.assertEqual(sys.path_importer_cache, importer_cache)
        self.assertEqual(set(sys.modules), set(cache))
        self.assertTrue(all(sys.modules[name] is module for name, module in cache.items()))
        self.assertTrue(all(s.module not in sys.modules for s in fixture._SOURCES))

    def test_reports_and_receipts_are_frozen_and_payloads_hidden(self):
        report = fixture.exercise_fixture(fixture.FixtureCase.LF_SUCCESS)
        with self.assertRaises(FrozenInstanceError):
            report.status = "fake"
        with self.assertRaises(FrozenInstanceError):
            report.receipts[0].phase = "fake"
        self.assertIs(type(report.receipts), tuple)
        self.assertNotIn("SYNTHETIC_VALUE", repr(fixture._SOURCES))

    def test_rng_failure_and_malformed_nonce_never_compile(self):
        for error in (OSError("raw secret"), ValueError("raw secret"), TypeError("raw secret")):
            with (patch.object(fixture.secrets, "token_bytes", side_effect=error),
                  patch("builtins.compile", side_effect=AssertionError("must not compile")) as compiler):
                report = fixture.exercise_fixture(fixture.FixtureCase.LF_SUCCESS)
                self.assertEqual((report.status, report.issue, report.receipts), ("FAIL_SYNTHETIC_LOADER", "PREPARE_FIXTURE", ()))
                compiler.assert_not_called()
        for nonce in (None, False, b"short", bytearray(32)):
            with patch.object(fixture.secrets, "token_bytes", return_value=nonce):
                report = fixture.exercise_fixture(fixture.FixtureCase.LF_SUCCESS)
                self.assertEqual((report.issue, report.receipts), ("PREPARE_FIXTURE", ()))

    def test_unknown_enum_alias_and_foreign_getters_before_compile(self):
        class Foreign:
            def __getattribute__(self, name):
                raise AssertionError("foreign getter")
            def __eq__(self, other):
                raise AssertionError("foreign equality")
        forged = object.__new__(fixture.FixtureCase)
        for value in (None, True, "LF_SUCCESS", "dgn007_synthetic_lf", Foreign(), forged):
            with patch("builtins.compile", side_effect=AssertionError("must not compile")) as compiler:
                report = fixture.exercise_fixture(value)
                self.assertEqual((report.status, report.issue, report.receipts), ("FAIL_SYNTHETIC_LOADER", "FIXTURE_CASE", ()))
                compiler.assert_not_called()

    def test_public_signature_does_not_accept_free_sources_or_prepared_input(self):
        with self.assertRaises(TypeError):
            fixture.exercise_fixture(fixture.FixtureCase.LF_SUCCESS, b"pass")
        with self.assertRaises(TypeError):
            fixture.exercise_fixture(body=b"pass")

    def test_modified_source_member_module_hash_bytes_before_compile(self):
        for key, value in (("module", "foreign"), ("member", "Synthetic/foreign.py"),
                           ("sha256", "0" * 64), ("body", b"SYNTHETIC_VALUE = 8\n"),
                           ("body", bytearray(b"SYNTHETIC_VALUE = 7\n")),
                           ("body", b"x" * (fixture.MAX_SOURCE_BYTES + 1))):
            session = self.session()
            session._source = replace(session._source, **{key: value})
            with patch("builtins.compile", side_effect=AssertionError("must not compile")) as compiler:
                self.rejected(lambda: session._loader.exec_module(session._module))
                compiler.assert_not_called()
                self.assertEqual(session._receipts, [])

    def test_equal_hash_wrong_module_object_is_rejected(self):
        session = self.session()
        foreign = ModuleType(session._source.module)
        foreign.__spec__, foreign.__loader__, foreign.__file__ = session._spec, session._loader, session._origin
        with patch("builtins.compile", side_effect=AssertionError("must not compile")) as compiler:
            self.rejected(lambda: session._loader.exec_module(foreign), "OBJECT_BINDING")
            compiler.assert_not_called()

    def test_changed_spec_loader_origin_or_name_is_rejected(self):
        for mutate in (lambda s: setattr(s._spec, "name", "foreign"),
                       lambda s: setattr(s._spec, "origin", "foreign"),
                       lambda s: setattr(s._spec, "loader", object()),
                       lambda s: setattr(s._module, "__file__", "foreign"),
                       lambda s: setattr(s._module, "__spec__", ModuleSpec(s._source.module, s._loader))):
            session = self.session()
            mutate(session)
            self.rejected(lambda: session._loader.exec_module(session._module), "SPEC_BINDING")
            self.assertEqual(session._receipts, [])

    def test_create_module_wrong_spec_and_duplicate_creation_are_closed(self):
        session = self.session()
        self.rejected(lambda: session._loader.create_module(ModuleSpec("foreign", session._loader)), "SPEC_BINDING")
        self.rejected(lambda: session._loader.create_module(session._spec), "DUPLICATE_CREATE")

    def test_missing_begin_or_execution_cannot_complete_from_effect_alone(self):
        session = self.session()
        session._module.SYNTHETIC_VALUE = 7
        self.rejected(lambda: session._complete(session._module), "LIFECYCLE_COMPLETE")
        session._begin(session._module)
        self.rejected(lambda: session._complete(session._module), "MISSING_EXECUTION")
        self.rejected(session._report, "MISSING_COMPLETE")

    def test_missing_receipts_cannot_create_public_success(self):
        with patch.object(fixture._MemoryLoader, "exec_module", return_value=None):
            report = fixture.exercise_fixture(fixture.FixtureCase.LF_SUCCESS)
        self.assertEqual((report.issue, report.receipts), ("MISSING_COMPLETE", ()))

    def test_duplicate_complete_reload_and_second_exec_are_rejected(self):
        session = self.session()
        self.execute(session)
        with patch("builtins.compile", side_effect=AssertionError("must not compile")) as compiler:
            self.rejected(lambda: session._loader.exec_module(session._module), "LIFECYCLE_BEGIN")
            compiler.assert_not_called()
        self.rejected(lambda: session._complete(session._module), "LIFECYCLE_COMPLETE")
        session._receipts.append(session._receipts[-1])
        self.rejected(session._report, "MISSING_COMPLETE")

    def test_begin_receipt_context_fields_are_checked_after_real_execution(self):
        for field_name, value in (("sequence", 2), ("sequence", True), ("phase", "COMPLETE"),
                                  ("fixture", "foreign"), ("module", "foreign"), ("member", "foreign"),
                                  ("raw_sha256", "0" * 64), ("nonce", b"z" * 32),
                                  ("context_digest", "0" * 64), ("object_slot", 2)):
            session = self.session()
            original = session._complete
            def tamper(module):
                session._receipts[0] = replace(session._receipts[0], **{field_name: value})
                original(module)
            session._complete = tamper
            self.rejected(lambda: session._loader.exec_module(session._module), "RECEIPT_BINDING")
            self.assertEqual(len(session._receipts), 1)

    def test_identity_and_context_change_between_begin_and_completion_fail(self):
        for mutate in (lambda s: setattr(s, "_begin_object", ModuleType(s._source.module)),
                       lambda s: setattr(s, "_nonce", b"z" * 32),
                       lambda s: setattr(s, "_digest", "0" * 64),
                       lambda s: setattr(s._module, "__spec__", None),
                       lambda s: setattr(s._module, "SYNTHETIC_VALUE", True)):
            session = self.session()
            original = session._complete
            def tamper(module):
                mutate(session)
                original(module)
            session._complete = tamper
            self.rejected(lambda: session._loader.exec_module(session._module))
            self.assertEqual(tuple(r.phase for r in session._receipts), ("BEGIN",))

    def test_final_receipt_tampering_cannot_be_reported_as_pass(self):
        session = self.session()
        self.execute(session)
        for index in (0, 1):
            old = session._receipts[index]
            session._receipts[index] = replace(old, phase="fake")
            self.rejected(session._report, "RECEIPT_BINDING")
            session._receipts[index] = old

    def test_equal_spec_replacement_after_begin_is_not_original_identity(self):
        session = self.session()
        original = session._complete
        def exchange(module):
            session._spec = ModuleSpec(session._source.module, session._loader, origin=session._origin)
            module.__spec__ = session._spec
            original(module)
        session._complete = exchange
        self.rejected(lambda: session._loader.exec_module(session._module), "RECEIPT_BINDING")
        self.assertEqual(tuple(r.phase for r in session._receipts), ("BEGIN",))

    def test_final_equal_module_replacement_is_not_original_live_object(self):
        session = self.session()
        self.execute(session)
        replacement = ModuleType(session._source.module)
        replacement.__dict__.update(session._module.__dict__)
        session._module = replacement
        self.rejected(session._report, "RECEIPT_BINDING")

    def test_final_equal_spec_and_execution_anchor_exchange_are_rejected(self):
        session = self.session()
        self.execute(session)
        session._spec = ModuleSpec(session._source.module, session._loader, origin=session._origin)
        session._module.__spec__ = session._spec
        self.rejected(session._report, "RECEIPT_BINDING")
        for field_name, issue in (("_begin_bytes", "RECEIPT_BINDING"),
                                  ("_begin_loader", "RECEIPT_BINDING"),
                                  ("_compiled_code", "MISSING_EXECUTION"),
                                  ("_executed_code", "MISSING_EXECUTION"),
                                  ("_completed_code", "MISSING_EXECUTION")):
            session = self.session()
            self.execute(session)
            setattr(session, field_name, None)
            self.rejected(session._report, issue)
        session = self.session()
        self.execute(session)
        other = self.session()
        self.execute(other)
        session._compiled_code = session._executed_code = other._executed_code
        self.rejected(session._report, "MISSING_EXECUTION")
        for effect in (None, True, 8):
            session = self.session()
            self.execute(session)
            session._module.SYNTHETIC_VALUE = effect
            self.rejected(session._report, "FIXTURE_EFFECT")

    def test_foreign_source_and_receipt_fields_never_invoke_getters_or_equality(self):
        class Foreign:
            def __getattribute__(self, name):
                raise AssertionError("foreign getter")
            def __eq__(self, other):
                raise AssertionError("foreign equality")
        for key in ("case", "module", "member", "body", "sha256"):
            session = self.session()
            session._source = replace(session._source, **{key: Foreign()})
            with patch("builtins.compile", side_effect=AssertionError("must not compile")) as compiler:
                self.rejected(lambda: session._loader.exec_module(session._module))
                compiler.assert_not_called()
        for source in (Foreign(), object.__new__(fixture._Source)):
            self.rejected(lambda: fixture._checked_source(source))
        session = self.session()
        session._begin(session._module)
        expected = session._receipts[0]
        for key in ("sequence", "phase", "fixture", "module", "member", "raw_sha256", "nonce", "context_digest", "object_slot"):
            self.rejected(lambda: fixture._receipt_equal(replace(expected, **{key: Foreign()}), expected), "RECEIPT_BINDING")
        self.rejected(lambda: fixture._receipt_equal(object.__new__(fixture.LoaderReceipt), expected), "RECEIPT_BINDING")

    def test_missing_module_fields_do_not_invoke_module_getattr(self):
        session = self.session()
        session._module.__dict__["__getattr__"] = lambda name: (_ for _ in ()).throw(AssertionError("foreign getter"))
        del session._module.__dict__["__file__"]
        self.rejected(lambda: session._loader.exec_module(session._module), "SPEC_BINDING")

    def test_recordcap_is_checked_before_append(self):
        session = self.session()
        session._receipts = [None] * fixture.MAX_RECEIPTS
        self.rejected(lambda: session._receipt("BEGIN"), "RECEIPT_LIMIT")
        self.assertEqual(len(session._receipts), fixture.MAX_RECEIPTS)

    def test_literal_catalog_has_only_bounded_harmless_controlled_statements(self):
        self.assertEqual(len(fixture._SOURCES), 4)
        for source in fixture._SOURCES:
            self.assertLessEqual(len(source.body), 4096)
            self.assertEqual(hashlib.sha256(source.body).hexdigest(), source.sha256)
            if source.case is fixture.FixtureCase.COMPILE_FAILURE:
                self.assertEqual(source.body, b"return\n")
                continue
            tree = ast.parse(source.body)
            for node in ast.walk(tree):
                self.assertNotIsInstance(node, (ast.Import, ast.ImportFrom, ast.While, ast.For, ast.With))
                if isinstance(node, ast.Call):
                    self.assertIsInstance(node.func, ast.Name)
                    self.assertEqual(node.func.id, "RuntimeError")

    def test_tool_dependencies_and_execution_sites_are_narrow(self):
        tree = ast.parse((ROOT / "Tests/Tools/dgn007_memory_loader_fixture.py").read_text(encoding="utf-8"))
        self.assertEqual({a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names},
                         {"hashlib", "json", "secrets"})
        self.assertEqual({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)},
                         {"__future__", "dataclasses", "enum", "importlib.abc", "importlib.machinery", "importlib.util", "types"})
        sites = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                self.assertNotIn(name, {"open", "Popen", "read_bytes", "write_bytes", "import_module", "find_spec", "eval", "__import__"})
                if name in {"exec", "compile"}:
                    sites.append(name)
        self.assertCountEqual(sites, ["compile", "exec"])


if __name__ == "__main__":
    unittest.main()
