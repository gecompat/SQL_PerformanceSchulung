"""Reine Profilgegenproben und direkte Linux-Kontrollruntimebeobachtung."""
import ast
import io
from dataclasses import replace, FrozenInstanceError
import hashlib
from importlib.machinery import BuiltinImporter, FrozenImporter, PathFinder, ModuleSpec, SourceFileLoader
import importlib.util
import os
from pathlib import Path
import sys
import sysconfig
import tempfile
from types import ModuleType
from zipimport import zipimporter

PATH = Path(__file__).resolve().parents[1] / "Tools/dgn007_import_runtime_profile.py"
spec = importlib.util.spec_from_file_location("dgn007_import_runtime_profile", PATH)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def declared_linux_bootstrap():
    # Separate Callerbaseline VOR Testharnessimports; keine Ableitung von Trust aus einem Match.
    roots = (sysconfig.get_path("stdlib"), sysconfig.get_config_var("DESTSHARED"))
    abi = sysconfig.get_config_var("SOABI") or ""
    missing = tuple(p for p in sys.path if p.endswith(".zip") and not os.path.lexists(p))
    if len(missing) != 1:
        return m.ProfileReport("REJECTED_PROFILE", "TEST_BASELINE_UNAVAILABLE")
    controls = ("__main__", "dgn007_import_runtime_profile")
    rows = []
    for name, module in sorted(sys.modules.copy().items()):
        d = module.__dict__
        s, loader = d.get("__spec__"), d.get("__loader__")
        kind = ("CONTROL" if name in controls else "BUILTIN" if loader is BuiltinImporter else
                "FROZEN" if loader is FrozenImporter else "SOURCE" if type(loader) is SourceFileLoader else "EXTENSION")
        locations = () if s is None or s.submodule_search_locations is None else tuple(s.submodule_search_locations)
        rows.append(m.ModuleRecord(name, "" if s is None else s.origin, d.get("__file__", ""), kind,
                                   locations, module, s, loader))
    expected = m.DeclaredProfile(m.ASSUMPTION, b"c" * 32, sys.implementation.name, tuple(sys.version_info[:3]),
                                sys.executable, os.path.realpath(sys.executable),
                                (sys.prefix, sys.exec_prefix, sys.base_prefix, sys.base_exec_prefix),
                                abi, tuple(sys.path), roots, missing[0], controls,
                                tuple(sys.meta_path), tuple(sys.path_hooks), tuple(rows), ())
    return m.observe_current_interpreter(expected)


LINUX_BOOTSTRAP = declared_linux_bootstrap() if sys.platform == "linux" else None
import unittest
from unittest.mock import patch


def hook(path):
    pass


def fixture():
    row = m.ModuleRecord("sys", "built-in", "", "BUILTIN", (), sys, sys.__spec__, BuiltinImporter)
    p = m.DeclaredProfile(m.ASSUMPTION, b"t" * 32, "cpython", (3, 12, 14), "/declared/bin/python", "/declared/bin/python",
                         ("/declared",) * 4, "cpython-312", ("/declared/lib", "/declared/lib-dynload", "/declared/python312.zip"),
                         ("/declared/lib", "/declared/lib-dynload"), "/declared/python312.zip", (),
                         (BuiltinImporter, FrozenImporter, PathFinder), (zipimporter, hook), (row,), ())
    o = m.Observation(p.token, "linux", p.implementation, p.version, p.executable, p.executable_target, p.prefixes,
                      p.abi, (1, 1, 1, 1, 1, 0), p.paths, p.finders, p.hooks, p.modules, ())
    return p, o


class ProfileTests(unittest.TestCase):
    def reject(self, p, o, issue=None):
        r = m.validate_profile(p, o)
        self.assertEqual(r.status, "REJECTED_PROFILE")
        if issue:
            self.assertEqual(r.issue, issue)
        self.assertFalse(r.trust_attested or r.runtime_attested or r.method_approved or r.import_used_bytes_attested)
        return r

    def test_match_is_only_declared_baseline_not_trust(self):
        p, o = fixture()
        r = m.validate_profile(p, o)
        self.assertEqual(r.status, "MATCHED_DECLARED_BASELINE")
        self.assertTrue(r.trust_assumed)
        self.assertFalse(r.trust_attested or r.runtime_attested or r.method_approved or r.import_used_bytes_attested)
        self.assertNotIn("/declared", repr(p) + repr(o) + repr(r))
        with self.assertRaises(FrozenInstanceError):
            p.token = b"x" * 32

    def test_metadata_patch_token_executable_and_abi_drift(self):
        p, o = fixture()
        for field, value in (("version", (3, 12, 15)), ("token", b"z" * 32), ("executable", "/other/python"),
                             ("abi", "other"), ("prefixes", ("/other",) * 4), ("implementation", "pypy")):
            self.reject(p, replace(o, **{field: value}))

    def test_flags_platform_and_missing_trust(self):
        p, o = fixture()
        for index in range(6):
            flags = list(o.flags)
            flags[index] = 1 - flags[index]
            self.reject(p, replace(o, flags=tuple(flags)), "FLAGS_MISMATCH")
        self.reject(p, replace(o, platform="win32"), "UNSUPPORTED_PLATFORM")
        self.reject(replace(p, assumption="UNKNOWN"), o, "TRUST_UNDECLARED")

    def test_finder_and_hook_changes_are_closed(self):
        p, o = fixture()
        for finders in ((), (BuiltinImporter, PathFinder, FrozenImporter), (object(),) * 3):
            self.reject(p, replace(o, finders=finders))
        self.reject(p, replace(o, hooks=(zipimporter, lambda path: None)), "HOOK_MISMATCH")
        self.reject(p, replace(o, hooks=(object(), hook)))

    def test_module_identity_spec_loader_and_missing_records(self):
        p, o = fixture()
        row = o.modules[0]
        for update in ({"module": ModuleType("sys")}, {"spec": ModuleSpec("sys", BuiltinImporter)},
                       {"origin": "other"}, {"loader": FrozenImporter}):
            self.reject(p, replace(o, modules=(replace(row, **update),)))
        self.reject(p, replace(o, modules=()))
        self.reject(p, replace(o, modules=(row, row)))

    def test_own_names_and_unlisted_controls_rejected_even_when_declared(self):
        p, o = fixture()
        for name in ("Tests", "Tests.Contracts", "run_demo", "execution_target", "docker_sqlcmd_proxy"):
            module = ModuleType(name)
            module.__spec__ = ModuleSpec(name, BuiltinImporter, origin="built-in")
            module.__loader__ = BuiltinImporter
            row = m.ModuleRecord(name, "built-in", "", "BUILTIN", (), module, module.__spec__, BuiltinImporter)
            self.reject(replace(p, modules=(row,)), replace(o, modules=(row,)), "OWN_MODULE_CACHED")
        row = replace(o.modules[0], kind="CONTROL")
        self.reject(replace(p, modules=(row,)), replace(o, modules=(row,)), "CONTROL_MISMATCH")

    def test_loaded_origin_outside_and_parent_traversal(self):
        p, o = fixture()
        for origin in ("/foreign/file.py", "/declared/lib/../foreign.py", "/declared/library/file.py"):
            loader = SourceFileLoader("fixture", origin)
            module = ModuleType("fixture")
            module.__spec__, module.__loader__, module.__file__ = ModuleSpec("fixture", loader, origin=origin), loader, origin
            row = m.ModuleRecord("fixture", origin, origin, "SOURCE", (), module, module.__spec__, loader)
            self.reject(replace(p, modules=(row,)), replace(o, modules=(row,)))

    def test_paths_and_unknown_loader_kinds(self):
        p, o = fixture()
        self.reject(replace(p, paths=("/foreign",)), replace(o, paths=("/foreign",)), "PATH_MISMATCH")
        for kind in ("NAMESPACE", "LAZY", "ZIP", "SITE"):
            row = replace(o.modules[0], kind=kind)
            self.reject(replace(p, modules=(row,)), replace(o, modules=(row,)))

    def test_metadata_and_record_bounds(self):
        p, o = fixture()
        for value in ("x" * 4097, "é" * 2049, "\ud800"):
            self.reject(p, replace(o, abi=value))
        self.reject(p, replace(o, modules=o.modules * 257))
        for size in (-1, True, m.MAX_FILE + 1):
            self.reject(p, replace(o, files=(m.FileDigest("/declared/lib/file", size, "0" * 64),)))
        rows = tuple(m.FileDigest(f"/declared/lib/f{i}", m.MAX_FILE, "0" * 64) for i in range(3))
        self.reject(replace(p, files=rows), replace(o, files=rows))

    def test_foreign_fields_and_uninitialized_records_never_execute_getters(self):
        class Foreign:
            def __getattribute__(self, name):
                raise RuntimeError("foreign getter")
            def __eq__(self, other):
                raise RuntimeError("foreign equality")
        p, o = fixture()
        self.reject(Foreign(), o)
        self.reject(p, Foreign())
        for field in p.__dataclass_fields__:
            self.reject(replace(p, **{field: Foreign()}), o)
        for field in o.__dataclass_fields__:
            self.reject(p, replace(o, **{field: Foreign()}))
        for field in o.modules[0].__dataclass_fields__:
            self.reject(p, replace(o, modules=(replace(o.modules[0], **{field: Foreign()}),)))
        for cls in (m.DeclaredProfile, m.Observation, m.ModuleRecord, m.FileDigest):
            empty = object.__new__(cls)
            if cls is m.DeclaredProfile:
                self.reject(empty, o)
            elif cls is m.Observation:
                self.reject(p, empty)
            elif cls is m.ModuleRecord:
                self.reject(p, replace(o, modules=(empty,)))
            else:
                self.reject(p, replace(o, files=(empty,)))

    def test_windows_early_unsupported_without_read_or_capture(self):
        with patch.object(m.sys, "platform", "win32"), patch.object(m, "_capture") as capture, patch("builtins.open") as opened:
            r = m.observe_current_interpreter(object())
        self.assertEqual(r.issue, "UNSUPPORTED_PLATFORM")
        capture.assert_not_called()
        opened.assert_not_called()

    def test_raw_hash_changed_file_and_limits_before_read(self):
        p, o = fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "declared.py"
            path.write_bytes(b"synthetic\r\n")
            digest = m.FileDigest(p.executable, path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())
            p, o = replace(p, files=(digest,)), replace(o, files=(digest,))
            # Capture is mocked; only explicitly named temporary fixture file is read.
            with patch.object(m.sys, "platform", "linux"), patch.object(m.os.path, "isdir", return_value=True), \
                 patch.object(m.os.path, "isfile", return_value=True), patch.object(m.os.path, "islink", return_value=False), \
                 patch.object(m.os.path, "realpath", side_effect=lambda path: path), patch.object(m.os.path, "lexists", return_value=False), \
                 patch.object(m, "_capture", side_effect=lambda expected, files: replace(o, files=files)), \
                 patch("builtins.open", side_effect=lambda name, mode: path.open(mode)):
                self.assertEqual(m.observe_current_interpreter(p).status, "MATCHED_DECLARED_BASELINE")
                path.write_bytes(b"synthetic\n")
                self.assertEqual(m.observe_current_interpreter(p).issue, "PROFILE_MISMATCH")
            bad = replace(p, files=(replace(digest, size=m.MAX_FILE + 1),))
            with patch.object(m.sys, "platform", "linux"), patch("builtins.open") as opened:
                self.assertEqual(m.observe_current_interpreter(bad).status, "REJECTED_PROFILE")
                opened.assert_not_called()

    def test_inventory_before_after_mutation_is_not_accepted(self):
        p, o = fixture()
        changed = replace(o, abi="changed")
        with patch.object(m.sys, "platform", "linux"), patch.object(m, "_capture", side_effect=(o, changed)), \
             patch.object(m.os.path, "isdir", return_value=True), patch.object(m.os.path, "isfile", return_value=True), \
             patch.object(m.os.path, "realpath", side_effect=lambda path: path), \
             patch.object(m.os.path, "lexists", return_value=False):
            r = m.observe_current_interpreter(p)
        self.assertEqual(r.issue, "PROFILE_MISMATCH")

    def test_noncanonical_paths_and_undeclared_hash_selection_before_io(self):
        p, o = fixture()
        for path in ("", "relative", "/declared//python", "/declared/../python", "/declared/python/"):
            self.reject(replace(p, executable=path), o)
        for files in ((m.FileDigest("/declared/lib/other", 1, "0" * 64),),
                      tuple(m.FileDigest(f"/declared/lib/f{i}", 1, "0" * 64) for i in range(3))):
            with patch.object(m.sys, "platform", "linux"), patch("builtins.open") as opened:
                self.assertEqual(m.observe_current_interpreter(replace(p, files=files)).status, "REJECTED_PROFILE")
                opened.assert_not_called()

    def test_second_declared_hashfile_requires_root_binding_in_pure_validator(self):
        p, o = fixture()
        files = (m.FileDigest(p.executable_target, 1, "0" * 64),
                 m.FileDigest("/foreign/file", 1, "0" * 64))
        self.reject(replace(p, files=files), replace(o, files=files), "HASH_PATH_MISMATCH")
        files = (files[0], replace(files[1], path="/declared/lib/file"))
        self.assertEqual(m.validate_profile(replace(p, files=files), replace(o, files=files)).status,
                         "MATCHED_DECLARED_BASELINE")

    def test_symlink_parent_and_executable_alias_targets_are_bound_before_open(self):
        p, o = fixture()
        digest = m.FileDigest(p.executable_target, 1, "0" * 64)
        for changed_path in (p.roots[0], p.executable):
            with patch.object(m.sys, "platform", "linux"), patch.object(m.os.path, "isdir", return_value=True), \
                 patch.object(m.os.path, "isfile", return_value=True), \
                 patch.object(m.os.path, "realpath", side_effect=lambda path: "/escaped" if path == changed_path else path), \
                 patch("builtins.open") as opened:
                self.assertEqual(m.observe_current_interpreter(replace(p, files=(digest,))).status, "REJECTED_PROFILE")
                opened.assert_not_called()
        self.reject(p, replace(o, executable_target="/changed/target"), "PROFILE_MISMATCH")

    def test_live_spec_and_loader_fields_cannot_drift_under_equal_records(self):
        p, o = fixture()
        origin = "/declared/lib/fixture.py"
        loader = SourceFileLoader("fixture", origin)
        module = ModuleType("fixture")
        module.__spec__, module.__loader__, module.__file__ = ModuleSpec("fixture", loader, origin=origin), loader, origin
        row = m.ModuleRecord("fixture", origin, origin, "SOURCE", (), module, module.__spec__, loader)
        p, o = replace(p, modules=(row,)), replace(o, modules=(row,))
        self.assertEqual(m.validate_profile(p, o).status, "MATCHED_DECLARED_BASELINE")
        for target, field, value in ((loader, "name", "foreign"), (loader, "path", "/foreign"),
                                     (module.__spec__, "origin", "/foreign")):
            old = getattr(target, field)
            setattr(target, field, value)
            self.reject(p, o, "MODULE_COHERENCY")
            setattr(target, field, old)

    def test_foreign_cache_keys_and_locations_are_not_sorted_or_iterated(self):
        class Foreign:
            def __lt__(self, other):
                raise RuntimeError("foreign comparison")
            def __iter__(self):
                raise RuntimeError("foreign iteration")
        p, o = fixture()
        with patch.object(m.sys, "modules", {Foreign(): sys}):
            with self.assertRaises(m._Failure) as raised:
                m._capture(p, ())
            self.assertEqual(str(raised.exception), "INVALID_RECORD")
        module = ModuleType("fixture")
        loader = SourceFileLoader("fixture", "/declared/lib/fixture.py")
        module.__spec__ = ModuleSpec("fixture", loader, origin=loader.path)
        module.__loader__, module.__file__ = loader, loader.path
        for locations in (Foreign(), [Foreign()], ["/declared/lib"] * 257):
            module.__spec__.submodule_search_locations = locations
            with self.assertRaises(m._Failure):
                m._module("fixture", module, ())

    def test_false_builtin_labels_and_unprofiled_cacheobjects_are_closed(self):
        p, o = fixture()
        self.reject(replace(p, controls=("json",)), o, "CONTROL_MISMATCH")
        self.reject(p, replace(o, abi=""), "INTERPRETER_MISMATCH")
        for kind in ("FROZEN", "SOURCE", "EXTENSION"):
            row = replace(o.modules[0], kind=kind)
            self.reject(replace(p, modules=(row,)), replace(o, modules=(row,)), "MODULE_COHERENCY")
        with self.assertRaises(m._Failure):
            m._module("typing.io", object(), ())

    def test_fixed_frozen_bootstrap_alias_requires_live_object_cohesion(self):
        p, o = fixture()
        module = ModuleType("importlib._bootstrap")
        module.__spec__ = ModuleSpec("_frozen_importlib", FrozenImporter, origin="frozen")
        module.__loader__ = FrozenImporter
        rows = tuple(m.ModuleRecord(name, "frozen", "", "FROZEN", (), module, module.__spec__, FrozenImporter)
                     for name in ("_frozen_importlib", "importlib._bootstrap"))
        p, o = replace(p, modules=rows), replace(o, modules=rows)
        self.assertEqual(m.validate_profile(p, o).status, "MATCHED_DECLARED_BASELINE")
        other = ModuleType("importlib._bootstrap")
        other.__spec__, other.__loader__ = module.__spec__, FrozenImporter
        changed = (rows[0], replace(rows[1], module=other))
        self.reject(replace(p, modules=changed), replace(o, modules=changed), "MODULE_COHERENCY")
        with self.assertRaises(m._Failure):
            m._module("foreign.alias", module, ())

    def test_foreign_and_oversize_search_containers_before_tuple_capture(self):
        class Foreign:
            def __iter__(self):
                raise RuntimeError("foreign iteration")
        p, o = fixture()
        for name in ("path", "meta_path", "path_hooks"):
            for value in (Foreign(), [None] * 257):
                with patch.object(m.sys, "modules", {"sys": sys}), patch.object(m.sys, name, value):
                    with self.assertRaises(m._Failure):
                        m._capture(p, ())

    def test_actual_read_sentinel_crosses_file_bound_before_hashing_overflow(self):
        p, o = fixture()
        digest = m.FileDigest(p.executable_target, 1, hashlib.sha256(b"x").hexdigest())
        p, o = replace(p, files=(digest,)), replace(o, files=(digest,))
        with patch.object(m.sys, "platform", "linux"), patch.object(m, "MAX_FILE", 1), \
             patch.object(m.os.path, "isdir", return_value=True), patch.object(m.os.path, "isfile", return_value=True), \
             patch.object(m.os.path, "islink", return_value=False), patch.object(m.os.path, "lexists", return_value=False), \
             patch.object(m.os.path, "realpath", side_effect=lambda path: path), \
             patch.object(m, "_capture", return_value=o), patch("builtins.open", return_value=io.BytesIO(b"xx")):
            self.assertEqual(m.observe_current_interpreter(p).issue, "FILE_LIMIT")

    def test_dependencies_and_no_runtime_launch_or_candidate_resolver(self):
        tree = ast.parse(PATH.read_text(encoding="utf-8"))
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertEqual(imports, {"dataclasses", "importlib.machinery", "types", "zipimport"})
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                name = n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "")
                self.assertNotIn(name, {"Popen", "run", "exec", "compile", "find_spec", "import_module", "walk", "rglob"})


@unittest.skipUnless(sys.platform == "linux", "Linux-only observation; portable validation runs everywhere")
class ActualLinuxProfileTests(unittest.TestCase):
    def test_current_isolated_controlruntime_matches_explicit_caller_baseline(self):
        self.assertTrue(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)
        r = LINUX_BOOTSTRAP
        self.assertEqual((r.status, r.issue), ("MATCHED_DECLARED_BASELINE", "NONE"))
        self.assertFalse(r.trust_attested or r.runtime_attested)


if __name__ == "__main__":
    unittest.main()
