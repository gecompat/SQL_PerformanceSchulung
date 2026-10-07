#!/usr/bin/env python3
"""Commitgebundene Offline-Gegenproben; kein Kandidatenimport oder SQLstart."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Tools"))
import dgn007_source_bundle as bundle
import dgn007_execution_edges as edges


def git(repo, *args):
    env = bundle.git_environment()
    env.update(GIT_AUTHOR_DATE="2026-10-07T00:00:00Z", GIT_COMMITTER_DATE="2026-10-07T00:00:00Z")
    return subprocess.check_output(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo),
        "-c", "core.hooksPath=" + str(repo / "empty-hooks"), "-c", "core.autocrlf=false",
        "-c", "commit.gpgSign=false", "-c", "user.name=Synthetic Lab",
        "-c", "user.email=synthetic-fixture", *args], env=env, stderr=subprocess.DEVNULL,
        timeout=10, shell=False)


class ExecutionEdgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.head = git(ROOT, "rev-parse", "HEAD").decode().strip()
        cls.sources = {p: git(ROOT, "cat-file", "blob", cls.head + ":" + p)
                       for p in bundle.DGN007.members}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dgn007-edges-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.candidate = self.root / "repo", self.root / "candidate"
        self.repo.mkdir(); self.candidate.mkdir()
        git(self.repo, "init", "--quiet", "--template=")
        self.bodies = dict(self.sources)
        self.commit()

    def commit(self):
        for path, body in self.bodies.items():
            for root in (self.repo, self.candidate):
                p = root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(body)
        git(self.repo, "add", "--all")
        git(self.repo, "commit", "--quiet", "-m", "Synthetic edge fixture")
        self.oid = git(self.repo, "rev-parse", "HEAD").decode().strip()

    def change(self, path, body, rebind=False):
        self.bodies[path] = body
        if rebind:
            contract = json.loads(self.bodies[edges.CONTRACT])
            contract["source_sha256"][Path(path).name] = hashlib.sha256(
                body.replace(b"\r\n", b"\n")).hexdigest()
            self.bodies[edges.CONTRACT] = json.dumps(contract, ensure_ascii=True).encode()
        self.commit()

    def manifest(self, name, mutate):
        path = edges.AUTOMATED + name
        value = json.loads(self.bodies[path])
        mutate(value)
        self.change(path, json.dumps(value).encode())

    def verify(self):
        return edges.verify_execution_edges(self.repo, self.oid, self.candidate)

    def reject(self, issue):
        report = self.verify()
        self.assertEqual((report.status, report.issue), ("FAIL_STATIC_CANDIDATE", issue))
        self.assertTrue(report.raw_bytes_verified)
        self.assertFalse(report.declared_execution_edges_verified)
        self.assertFalse(report.runtime_attested or report.method_approved)
        return report

    def test_current_27_source_profile_is_positive(self):
        report = self.verify()
        self.assertEqual(report.status, "PASS_STATIC_CANDIDATE", report.issue)
        self.assertTrue(report.declared_import_graph_verified and report.declared_execution_edges_verified)
        self.assertEqual((report.members, report.validation_scope, report.source_profile),
                         (27, "PROJECT_SEMANTIC", edges.PROFILE))
        self.assertFalse(report.runtime_attested or report.method_approved)
        with self.assertRaises(FrozenInstanceError):
            report.method_approved = True

    def test_all_six_manifest_phase_projections(self):
        self.assertEqual(tuple(len(specs) + 1 for _, specs in edges.MANIFEST_PROJECTIONS),
                         (4, 5, 6, 8, 8, 8))
        for name, _ in edges.MANIFEST_PROJECTIONS:
            with self.subTest(name=name):
                path = edges.AUTOMATED + name
                original = self.bodies[path]
                self.manifest(name, lambda m: m["phases"].reverse())
                self.reject("MANIFEST_PROJECTION")
                self.bodies[path] = original

    def test_manifest_exact_flags_selectors_and_budgets(self):
        path = edges.AUTOMATED + "setup.manifest.json"
        original = self.bodies[path]
        for key, value in (("required", False), ("require_summary", False), ("database", "target"),
                           ("timeout_seconds", 29), ("timeout_seconds", True), ("extra", 1)):
            with self.subTest(key=key, value=value):
                self.bodies[path] = original
                self.manifest("setup.manifest.json", lambda m: m["phases"][0].update({key: value}))
                self.reject("MANIFEST_PROJECTION")

    def test_manifest_header_and_cleanup_are_exact(self):
        path = edges.AUTOMATED + "setup.manifest.json"
        original = self.bodies[path]
        for key, value in (("timeout_seconds", 181), ("cleanup_timeout_seconds", 61),
                           ("run_token", "FOREIGN"), ("safety_level", "GREEN"), ("unknown", 0)):
            with self.subTest(key=key):
                self.bodies[path] = original
                self.manifest("setup.manifest.json", lambda m: m.update({key: value}))
                self.reject("MANIFEST_PROJECTION")
        self.bodies[path] = original
        self.manifest("setup.manifest.json", lambda m: m["cleanup"].update({"timeout_seconds": 59}))
        self.reject("MANIFEST_PROJECTION")

    def test_unknown_sessions_and_external_paths(self):
        path = edges.AUTOMATED + "setup.manifest.json"
        original = self.bodies[path]
        for value in ({"kind": "multi_session", "manifest": "Sessions/manifest.json"},
                      {"script": "../foreign.sql"}, {"script": "/foreign.sql"},
                      {"script": "90_Cleanup.sql"}):
            with self.subTest(value=value):
                self.bodies[path] = original
                self.manifest("setup.manifest.json", lambda m: m["phases"][0].update(value))
                self.reject("MANIFEST_PROJECTION")

    def test_duplicate_keys_at_root_phase_and_cleanup(self):
        p = edges.AUTOMATED + "setup.manifest.json"
        original = self.bodies[p]
        for body in (original.replace(b'"contract_version":', b'"contract_version":"1.0","contract_version":', 1),
                     original.replace(b'"id":"PREFLIGHT"', b'"id":"PREFLIGHT","id":"PREFLIGHT"', 1),
                     original.replace(b'"id":"CLEANUP"', b'"id":"CLEANUP","id":"CLEANUP"', 1)):
            self.change(p, body)
            self.reject("JSON_DUPLICATE_KEY")

    def test_json_extra_payload_null_float_constants_and_depth(self):
        p = edges.AUTOMATED + "setup.manifest.json"
        for body, issue in ((self.sources[p] + b'{}', "JSON_SHAPE"), (b'null', "JSON_SHAPE"),
                            (b'{"x":NaN}', "JSON_NUMBER"), (b'{"x":Infinity}', "JSON_NUMBER"),
                            (b'{"x":180.0}', "JSON_NUMBER"), (b'{"x":100000000000000000000}', "JSON_LIMIT"),
                            (b'{"x":' + b'[' * 10 + b'0' + b']' * 10 + b'}', "JSON_LIMIT")):
            self.change(p, body)
            self.reject(issue)

    def test_each_python_member_is_bound_not_only_entrypoint(self):
        for path in bundle.PYTHON_MEMBERS:
            with self.subTest(path=path):
                self.change(path, self.sources[path] + b'\nunused_new_call = 42\n')
                self.reject("PYTHON_PROFILE_CHANGED")
                self.bodies[path] = self.sources[path]

    def test_uncalled_io_function_is_rejected(self):
        p = bundle.PYTHON_MEMBERS[3]
        self.change(p, self.bodies[p] + b'\ndef unused_io():\n    return Path("foreign").read_text()\n')
        self.reject("PYTHON_PROFILE_CHANGED")

    def test_top_level_sentinel_is_never_executed(self):
        marker = self.root / "sentinel"
        p = bundle.PYTHON_MEMBERS[2]
        self.change(p, self.bodies[p] + ("\nPath(" + repr(str(marker)) + ").write_text('executed')\n").encode())
        self.reject("PYTHON_PROFILE_CHANGED")
        self.assertFalse(marker.exists())
        self.assertNotIn("docker_sqlcmd_proxy", sys.modules)

    def test_runner_recovery_and_runcontract_changes_are_rejected(self):
        p = bundle.PYTHON_MEMBERS[0]
        for old, new in ((b'script=AUTOMATED / "90_Cleanup.sql"', b'script=AUTOMATED / "10_Setup.sql"'),
                         (b'("CONTROL_CONFIG", "15_Control_AB.sql", "target", 5)',
                          b'("CONTROL_CONFIG", "15_Control_BA.sql", "target", 5)'),
                         (b'choices=(execution_target.DOCKER,)', b'choices=(execution_target.HOST,)')):
            self.assertIn(old, self.sources[p])
            self.change(p, self.sources[p].replace(old, new, 1))
            self.reject("PYTHON_PROFILE_CHANGED")

    def test_ast_allows_comments_but_not_docstring_semantics(self):
        p = bundle.PYTHON_MEMBERS[2]
        self.change(p, self.sources[p] + b'\n# Nur Layoutkommentar\n')
        self.assertTrue(self.verify().declared_execution_edges_verified)
        self.change(p, self.sources[p].replace(b'"""Minimal', b'"""Changed', 1))
        self.reject("PYTHON_PROFILE_CHANGED")

    def test_utf7_cookie_cannot_hide_behind_same_utf8_ast(self):
        p = bundle.PYTHON_MEMBERS[2]
        self.change(p, b'# coding: utf-7\n' + self.sources[p])
        self.reject("PYTHON_ENCODING")

    def test_unknown_ast_schema_version_is_closed(self):
        with patch.object(edges.sys, "version_info", (3, 15, 0)):
            self.reject("PYTHON_AST_VERSION")

    def test_14_source_hashes_use_bound_lf_bytes(self):
        p = edges.AUTOMATED + "10_Setup.sql"
        self.change(p, self.sources[p].replace(b'\n', b'\r\n'))
        report = self.verify()
        self.assertTrue(report.declared_execution_edges_verified, report.issue)
        self.assertNotEqual(report.raw_binding, report.lf_binding)
        self.change(p, self.sources[p] + b'-- changed source\n')
        self.reject("CONTRACT_SOURCE_HASH")

    def test_changed_source_can_only_pass_with_matching_contract_hash(self):
        p = edges.AUTOMATED + "10_Setup.sql"
        self.change(p, self.sources[p] + b'SELECT 1 AS SyntheticEdge;\n', rebind=True)
        self.assertTrue(self.verify().declared_execution_edges_verified)

    def test_contract_unknown_fields_duplicate_and_source_keys(self):
        original = self.sources[edges.CONTRACT]
        for mutate, issue in ((lambda c: c.update(extra=False), "CONTRACT_POLICY"),
                              (lambda c: c["resources_policy"].update(extra=False), "CONTRACT_POLICY"),
                              (lambda c: c["source_sha256"].pop("10_Setup.sql"), "CONTRACT_SOURCE_KEYS"),
                              (lambda c: c["source_sha256"].update({"setup.manifest.json": "0" * 64}), "CONTRACT_SOURCE_KEYS"),
                              (lambda c: c["source_sha256"].update({"10_Setup.sql": "F" * 64}), "CONTRACT_SOURCE_HASH")):
            value = json.loads(original)
            mutate(value)
            self.change(edges.CONTRACT, json.dumps(value).encode())
            self.reject(issue)
        self.change(edges.CONTRACT, original.replace(b'"schema":', b'"schema":"duplicate","schema":', 1))
        self.reject("JSON_DUPLICATE_KEY")

    def test_three_other_manifests_are_checked_outside_14_hashes(self):
        self.assertEqual(len(edges.SOURCE_KEYS), 14)
        self.assertNotIn("windows.manifest.json", edges.SOURCE_KEYS)
        self.manifest("windows.manifest.json", lambda c: c.update(timeout_seconds=179))
        self.reject("MANIFEST_PROJECTION")

    def test_all_sqlcmd_directives_rejected_even_after_source_rebinding(self):
        p = edges.AUTOMATED + "00_Preflight.sql"
        for line in (b':r foreign.sql', b'  :setvar X foreign', b':unknown', b'!! command'):
            self.change(p, self.sources[p] + line + b'\n', rebind=True)
            self.reject("SQLCMD_DIRECTIVE")

    def test_sqlcmd_directive_scan_covers_all_11_sql_sources(self):
        for p in tuple(p for p in bundle.DATA_MEMBERS if p.endswith('.sql')):
            with self.subTest(path=p):
                self.change(p, self.sources[p] + b'\n:r foreign.sql\n', rebind=True)
                self.reject("SQLCMD_DIRECTIVE")
                self.bodies[p] = self.sources[p]
                self.bodies[edges.CONTRACT] = self.sources[edges.CONTRACT]

    def test_sql_bom_and_nul_cannot_hide_directive(self):
        p = edges.AUTOMATED + "00_Preflight.sql"
        for body in (b'\xef\xbb\xbf:r foreign.sql\n' + self.sources[p],
                     self.sources[p] + b'\x00:r foreign.sql\n'):
            self.change(p, body, rebind=True)
            self.reject("SQL_ENCODING")

    def test_byte_mismatch_never_reaches_callback(self):
        p = self.candidate / bundle.PYTHON_MEMBERS[0]
        p.write_bytes(b'not valid syntax')
        with patch.object(edges, "_validate_edges", side_effect=AssertionError("must not run")) as callback:
            report = self.verify()
        self.assertEqual(report.issue, "RAW_BYTES_DIFFER")
        callback.assert_not_called()

    def test_callback_is_after_imports_and_mapping_is_immutable(self):
        observed = []
        def inspect(bodies):
            self.assertIs(type(bodies), MappingProxyType)
            self.assertEqual(dict(bodies), self.bodies)
            with self.assertRaises(TypeError):
                bodies["foreign"] = b'payload'
            # Neue Dateibytes nach Aufnahme ersetzen nicht den geprüften Body.
            (self.candidate / bundle.PYTHON_MEMBERS[0]).write_bytes(b'changed after read')
            observed.append(True)
        with patch.object(bundle, "_imports", wraps=bundle._imports) as imports:
            result = bundle.verify_bundle(self.repo, self.oid, self.candidate,
                                          bound_validator=inspect)
        imports.assert_called_once()
        self.assertEqual(observed, [True])
        self.assertEqual(result.status, "PASS_STATIC_CANDIDATE")
        self.assertFalse(result.runtime_attested)

    def test_invalid_import_never_reaches_callback(self):
        p = bundle.PYTHON_MEMBERS[2]
        self.change(p, self.sources[p] + b'\nimport foreign_module\n')
        with patch.object(edges, "_validate_edges") as callback:
            report = self.verify()
        self.assertEqual(report.issue, "UNRESOLVED_IMPORT")
        callback.assert_not_called()

    def test_trusted_callback_exception_has_only_fixed_public_issue(self):
        def broken(_):
            raise RuntimeError("private source must not be exposed")
        result = bundle.verify_bundle(self.repo, self.oid, self.candidate, bound_validator=broken)
        self.assertEqual(result.issue, "BOUND_VALIDATOR_FAILED")
        self.assertNotIn("private source", str(result))

    def test_default_bundle_report_is_unchanged_and_has_no_edge_claim(self):
        result = bundle.verify_bundle(self.repo, self.oid, self.candidate)
        self.assertEqual(result.status, "PASS_STATIC_CANDIDATE")
        self.assertFalse(hasattr(result, "declared_execution_edges_verified"))


if __name__ == "__main__":
    unittest.main()
