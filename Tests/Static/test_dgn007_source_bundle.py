#!/usr/bin/env python3
"""Temporäre Git-/Dateifixtures; Kandidaten werden niemals ausgeführt."""
from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tests" / "Tools"))
import dgn007_source_bundle as bundle

SOURCES = {"entry.py": b"import helper\nimport json\nanswer = helper.answer\n",
           "helper.py": b"answer = 42\n", "statement.sql": b"SELECT 42;\n",
           "manifest.json": b'{"scope":"synthetic"}\n'}
POLICY = bundle.Policy(tuple(SOURCES), (("entry", "entry.py"), ("helper", "helper.py")),
                       ("entry.py",))


def git(repo, *args):
    env = bundle.git_environment()
    env.update(GIT_AUTHOR_DATE="2026-10-07T00:00:00Z", GIT_COMMITTER_DATE="2026-10-07T00:00:00Z")
    return subprocess.check_output(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo),
        "-c", "core.hooksPath=" + str(repo / "empty-hooks"), "-c", "core.autocrlf=false",
        "-c", "commit.gpgSign=false", "-c", "user.name=Synthetic Lab",
        "-c", "user.email=synthetic-fixture", *args], env=env, stderr=subprocess.DEVNULL,
        timeout=10, shell=False)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dgn007-bundle-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.candidate = self.root / "repo", self.root / "candidate"
        self.repo.mkdir(); self.candidate.mkdir()
        git(self.repo, "init", "--quiet", "--template=")
        for path, body in SOURCES.items():
            (self.repo / path).write_bytes(body)
            (self.candidate / path).write_bytes(body)
        self.commit = self.commit_sources()

    def commit_sources(self):
        git(self.repo, "add", "--all")
        git(self.repo, "commit", "--quiet", "-m", "Synthetic fixture")
        return git(self.repo, "rev-parse", "HEAD").decode().strip()

    def verify(self, policy=POLICY):
        return bundle.verify_bundle(self.repo, self.commit, self.candidate, policy)

    def new_source(self, path, body):
        (self.repo / path).write_bytes(body)
        (self.candidate / path).write_bytes(body)
        self.commit = self.commit_sources()

    def rejected(self, issue, policy=POLICY):
        result = self.verify(policy)
        self.assertEqual(result.status, "FAIL_STATIC_CANDIDATE")
        self.assertEqual(result.issue, issue)
        self.assertFalse(result.runtime_attested)
        self.assertFalse(result.method_approved)
        return result

    def test_exact_candidate_pass_and_stable_bindings(self):
        a, b = self.verify(), self.verify()
        self.assertEqual(a, b)
        self.assertEqual(a.status, "PASS_STATIC_CANDIDATE")
        self.assertTrue(a.raw_bytes_verified and a.declared_import_graph_verified)
        self.assertEqual(a.members, 4)
        self.assertEqual(a.raw_binding, a.lf_binding)
        self.assertFalse(a.runtime_attested or a.method_approved)

    def test_executor_change_does_not_hide_behind_sql_manifest(self):
        unchanged = (self.candidate / "manifest.json").read_bytes()
        (self.candidate / "entry.py").write_bytes(SOURCES["entry.py"] + b"# changed\n")
        result = self.rejected("RAW_BYTES_DIFFER")
        self.assertFalse(result.logical_text_equivalent)
        self.assertEqual((self.candidate / "manifest.json").read_bytes(), unchanged)

    def test_missing_member(self):
        (self.candidate / "helper.py").unlink()
        self.rejected("MEMBER_SET")

    def test_extra_member(self):
        (self.candidate / "foreign.py").write_bytes(b"pass\n")
        self.rejected("MEMBER_SET")

    def test_extra_empty_directory(self):
        (self.candidate / "foreign").mkdir()
        self.rejected("EXTRA_MEMBER")

    def test_duplicate_policy_before_set_conversion(self):
        self.rejected("DUPLICATE_OR_MEMBER_LIMIT", replace(POLICY, members=POLICY.members + ("entry.py",)))

    def test_policy_case_collision(self):
        self.rejected("DUPLICATE_OR_MEMBER_LIMIT", replace(POLICY, members=POLICY.members + ("ENTRY.py",)))

    def test_path_aliases_traversal_and_windows_names(self):
        for value in ("../entry.py", "./entry.py", "/entry.py", "C:/entry.py", "a\\entry.py",
                      "entry.py:stream", "entry.py.", "entry.py ", "a//b", "NUL.py", "COM1.txt"):
            with self.subTest(value=value):
                self.rejected("INVALID_PATH", replace(POLICY, members=(value,)))

    def test_noncanonical_candidate_name(self):
        (self.candidate / "entry.py.").write_bytes(b"pass\n")
        # Win32 normalisiert den Namen bereits beim Schreiben auf entry.py.
        self.rejected("RAW_BYTES_DIFFER" if os.name == "nt" else "INVALID_PATH")

    def test_crlf_equivalent_still_no_raw_pass(self):
        (self.candidate / "entry.py").write_bytes(SOURCES["entry.py"].replace(b"\n", b"\r\n"))
        r = self.rejected("RAW_BYTES_DIFFER")
        self.assertTrue(r.logical_text_equivalent)
        self.assertFalse(r.raw_bytes_verified or r.declared_import_graph_verified)

    def test_eol_equivalence_does_not_hide_later_content_change(self):
        (self.candidate / "entry.py").write_bytes(SOURCES["entry.py"].replace(b"\n", b"\r\n"))
        (self.candidate / "statement.sql").write_bytes(b"SELECT 43;\n")
        self.assertFalse(self.rejected("RAW_BYTES_DIFFER").logical_text_equivalent)

    def test_bom_lone_cr_and_final_newline_are_content_changes(self):
        for body in (b"\xef\xbb\xbf" + SOURCES["entry.py"], SOURCES["entry.py"].replace(b"\n", b"\r"),
                     SOURCES["entry.py"].rstrip(b"\n")):
            with self.subTest(body=body):
                (self.candidate / "entry.py").write_bytes(body)
                self.assertFalse(self.rejected("RAW_BYTES_DIFFER").logical_text_equivalent)

    def test_candidate_is_not_parsed_before_byte_binding(self):
        (self.candidate / "entry.py").write_bytes(b"syntax? broken")
        with patch.object(bundle.ast, "parse", side_effect=AssertionError("must not parse")):
            self.rejected("RAW_BYTES_DIFFER")

    def test_no_candidate_execution_or_parent_import(self):
        marker = self.root / "should-not-exist"
        self.new_source("entry.py", ("from pathlib import Path\nPath(" + repr(str(marker)) +
                                    ").write_text('executed')\nimport helper\n").encode())
        self.assertEqual(self.verify().status, "PASS_STATIC_CANDIDATE")
        self.assertFalse(marker.exists())
        self.assertNotIn("helper", sys.modules)

    def test_unknown_import(self):
        self.new_source("entry.py", b"import foreign_module\n")
        self.rejected("UNRESOLVED_IMPORT")

    def test_bound_nul_source_is_closed_syntax_failure(self):
        self.new_source("entry.py", b"import helper\n\x00")
        self.rejected("PYTHON_SYNTAX")

    def test_dynamic_and_aliased_imports_remain_open(self):
        for source in (b"__import__('helper')\n", b"from builtins import __import__ as load\n",
                       b"import importlib as load\nload.import_module('helper')\n",
                       b"import runpy\nrunpy.run_path('helper.py')\n"):
            with self.subTest(source=source):
                self.new_source("entry.py", source)
                self.assertNotEqual(self.verify().status, "PASS_STATIC_CANDIDATE")

    def test_relative_and_star_imports_are_explicitly_unsupported(self):
        for source in (b"from . import helper\n", b"from helper import *\n"):
            with self.subTest(source=source):
                self.new_source("entry.py", source)
                self.rejected("UNRESOLVED_IMPORT")

    def test_sys_path_and_alias_mutations(self):
        for source in (b"import sys\nsys.path.insert(0,'foreign')\n",
                       b"import sys as s\ns.modules.clear()\n"):
            with self.subTest(source=source):
                self.new_source("entry.py", source)
                self.rejected("IMPORT_ENVIRONMENT_OPEN")

    def test_from_sys_import_environment_aliases(self):
        for name in ("path", "meta_path", "path_hooks", "path_importer_cache", "modules"):
            with self.subTest(name=name):
                self.new_source("entry.py", ("from sys import " + name + " as p\np.clear()\n").encode())
                self.rejected("IMPORT_ENVIRONMENT_OPEN")

    def test_stdlib_shadow_and_namespace_init_extra(self):
        for name in ("json.py", "Tests/__init__.py"):
            with self.subTest(name=name):
                p = self.candidate / name
                p.parent.mkdir(exist_ok=True)
                p.write_bytes(b"raise RuntimeError('must not execute')\n")
                self.assertNotEqual(self.verify().status, "PASS_STATIC_CANDIDATE")
                p.unlink()
                if name.startswith("Tests/"):
                    p.parent.rmdir()

    def test_bad_entrypoint_and_module_policy(self):
        self.rejected("ENTRYPOINT_POLICY", replace(POLICY, entrypoints=("foreign.py",)))
        self.rejected("MODULE_POLICY", replace(POLICY, modules=(("entry", "entry.py"),)))

    def test_file_limit(self):
        self.rejected("FILE_LIMIT", replace(POLICY, file_bytes=10))

    def test_total_limit(self):
        self.rejected("TOTAL_LIMIT", replace(POLICY, total_bytes=1))

    def test_entry_limit(self):
        self.rejected("ENTRY_LIMIT", replace(POLICY, entries=3))

    def test_ast_limit(self):
        self.rejected("AST_LIMIT", replace(POLICY, ast_nodes=1))

    def test_explicit_full_commit_and_missing_commit(self):
        for commit in ("HEAD", self.commit[:7], "--help"):
            self.assertEqual(bundle.verify_bundle(self.repo, commit, self.candidate, POLICY).issue,
                             "EXPLICIT_COMMIT_REQUIRED")
        self.assertEqual(bundle.verify_bundle(self.repo, "0" * 40, self.candidate, POLICY).issue,
                         "GIT_READ_FAILED")

    def test_git_replace_and_environment_redirect_do_not_change_object(self):
        original = self.commit
        self.new_source("entry.py", b"import foreign\n")
        replacement = self.commit
        git(self.repo, "replace", original, replacement)
        for p, body in SOURCES.items():
            (self.candidate / p).write_bytes(body)
        self.commit = original
        with patch.dict(os.environ, {"GIT_DIR": str(self.root / "foreign"),
                "GIT_WORK_TREE": str(self.root / "foreign"), "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.autocrlf", "GIT_CONFIG_VALUE_0": "true"}):
            self.assertEqual(self.verify().status, "PASS_STATIC_CANDIDATE")

    def test_export_ignore_and_subst_do_not_modify_git_blob_expectation(self):
        (self.repo / ".gitattributes").write_bytes(b"helper.py export-ignore\nstatement.sql export-subst\n")
        self.new_source("statement.sql", b"-- $Format:%H$\nSELECT 42;\n")
        self.assertEqual(self.verify().status, "PASS_STATIC_CANDIDATE")
        (self.candidate / "helper.py").unlink()
        self.rejected("MEMBER_SET")
        (self.candidate / "helper.py").write_bytes(SOURCES["helper.py"])
        (self.candidate / "statement.sql").write_bytes(b"-- replaced hash\nSELECT 42;\n")
        self.rejected("RAW_BYTES_DIFFER")

    def symlink_or_skip(self, target, link, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError:
            if os.name == "nt":
                self.skipTest("Windows-Symlinkberechtigung fehlt; Linux-CI prüft den Fall")
            raise

    def test_file_symlink(self):
        p = self.candidate / "helper.py"
        p.unlink()
        self.symlink_or_skip(self.repo / "helper.py", p)
        self.rejected("LINK_OR_REPARSE")

    def test_actual_file_hardlink(self):
        p = self.candidate / "helper.py"
        p.unlink()
        os.link(self.repo / "helper.py", p)
        self.rejected("HARDLINK")

    def test_git_symlink_and_submodule_modes(self):
        original = self.commit
        blob = git(self.repo, "rev-parse", original + ":helper.py").decode().strip()
        for mode, oid in (("120000", blob), ("160000", original)):
            with self.subTest(mode=mode):
                git(self.repo, "update-index", "--cacheinfo", mode + "," + oid + ",helper.py")
                git(self.repo, "commit", "--quiet", "-m", "Synthetic member mode")
                self.commit = git(self.repo, "rev-parse", "HEAD").decode().strip()
                self.rejected("GIT_MEMBER_TYPE")

    def test_root_parent_symlink(self):
        p = self.root / "alias"
        self.symlink_or_skip(self.candidate, p, True)
        self.assertEqual(bundle.verify_bundle(self.repo, self.commit, p, POLICY).issue, "LINK_OR_REPARSE")

    def test_windows_reparse_attribute_is_rejected(self):
        with patch.object(bundle.Path, "lstat", return_value=type("Info", (), {
                "st_mode": bundle.stat.S_IFDIR, "st_file_attributes": 0x400})()):
            with self.assertRaisesRegex(bundle.Rejected, "LINK_OR_REPARSE"):
                bundle._regular(self.candidate, True)

    def test_git_output_and_deadline_bound(self):
        with self.assertRaisesRegex(bundle.Rejected, "GIT_READ_FAILED"):
            bundle._git(self.repo, ("cat-file", "blob", self.commit + ":entry.py"), 1, time.monotonic()+5)
        with self.assertRaisesRegex(bundle.Rejected, "GIT_READ_FAILED"):
            bundle._git(self.repo, ("rev-parse", "HEAD"), 64, time.monotonic()-1)


class CurrentCandidateTests(unittest.TestCase):
    def test_fixed_current_union_and_bootstrap(self):
        commit = git(ROOT, "rev-parse", "HEAD").decode().strip()
        with tempfile.TemporaryDirectory(prefix="dgn007-fixed-bundle-") as tmp:
            root = Path(tmp)
            for member in bundle.DGN007.members:
                p = root / member
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(git(ROOT, "cat-file", "blob", commit + ":" + member))
            report = bundle.verify_bundle(ROOT, commit, root)
            self.assertEqual(report.status, "PASS_STATIC_CANDIDATE", report.issue)
            self.assertEqual(report.members, 27)
            self.assertFalse(report.runtime_attested)
            # Neuer Commit mit geändertem Bootstrap wird separat als kontrollierte
            # In-memory-Graphgegenprobe geprüft; keine Runtimequellenänderung.
            bodies = {p: (root / p).read_bytes() for p in bundle.DGN007.members}
            bodies[bundle.PYTHON_MEMBERS[0]] = bodies[bundle.PYTHON_MEMBERS[0]].replace(
                b"(ROOT, RUNTIME, FRAMEWORK)", b"(FRAMEWORK, ROOT, RUNTIME)")
            with self.assertRaisesRegex(bundle.Rejected, "BOOTSTRAP_CHANGED"):
                bundle._imports(bodies, bundle.DGN007)


if __name__ == "__main__":
    unittest.main()
