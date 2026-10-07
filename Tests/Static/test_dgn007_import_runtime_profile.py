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
        report = m.ProfileReport("REJECTED_PROFILE", "TEST_BASELINE_UNAVAILABLE")
        return m.ObservationResult(report), report, m.ScalarObservationResult(report)
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
    known_hook = sys.path_hooks[1]  # Separate Kontrollauswahl vor dem beobachtenden Aufruf.
    records = m.observe_current_interpreter_records(expected)
    legacy = m.observe_current_interpreter(expected)
    scalars = m.observe_current_interpreter_scalars(expected, known_hook)
    return records, legacy, scalars


LINUX_RECORDS, LINUX_BOOTSTRAP, LINUX_SCALARS = declared_linux_bootstrap() if sys.platform == "linux" else (None, None, None)
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


class ObservationRecordsTests(unittest.TestCase):
    def observe(self, expected, captures, opened=None):
        # Nur Aufnahme-/I/O-Gegenproben; kein neuer Trust- oder Workerbootstrap.
        with patch.object(m.sys, "platform", "linux"), patch.object(m, "_capture", side_effect=captures) as capture, \
             patch.object(m.os.path, "isdir", return_value=True), patch.object(m.os.path, "isfile", return_value=True), \
             patch.object(m.os.path, "islink", return_value=False), patch.object(m.os.path, "lexists", return_value=False), \
             patch.object(m.os.path, "realpath", side_effect=lambda path: path), \
             patch("builtins.open", side_effect=opened) as stream:
            result = m.observe_current_interpreter_records(expected)
        return result, capture, stream

    def rejected(self, result, issue):
        self.assertIs(type(result), m.ObservationResult)
        self.assertEqual((result.report.status, result.report.issue), ("REJECTED_PROFILE", issue))
        self.assertIsNone(result.observation)
        self.assertFalse(result.report.trust_attested or result.report.runtime_attested or
                         result.report.import_used_bytes_attested or result.report.method_approved)

    def test_returns_exact_after_object_and_computed_hash_rows(self):
        p, before = fixture()
        raw = b"synthetic\r\n"
        file = m.FileDigest(p.executable_target, len(raw), hashlib.sha256(raw).hexdigest())
        p, before = replace(p, files=(file,)), replace(before, files=(file,))
        captured = []
        def capture(expected, files):
            row = replace(before, files=files)
            captured.append(row)
            return row
        result, calls, stream = self.observe(p, capture, lambda name, mode: io.BytesIO(raw))
        self.assertIs(result.observation, captured[1])
        self.assertIsNot(result.observation, captured[0])
        self.assertIsNot(result.observation, before)
        self.assertIs(result.observation.files[0], calls.call_args.args[1][0])
        self.assertIsNot(result.observation.files[0], file)
        self.assertEqual(result.observation.files, (file,))
        self.assertEqual(result.report.status, "MATCHED_DECLARED_BASELINE")
        stream.assert_called_once_with(file.path, "rb")

    def test_shape_and_preflight_failures_never_return_records(self):
        p, o = fixture()
        result, captures, stream = self.observe(replace(p, token=True), (o, o))
        self.rejected(result, "INVALID_RECORD")
        captures.assert_not_called()
        stream.assert_not_called()
        for check, issue in (("isdir", "ROOT_MISMATCH"), ("isfile", "INTERPRETER_MISMATCH")):
            with patch.object(m.sys, "platform", "linux"), patch.object(m.os.path, "isdir", return_value=True), \
                 patch.object(m.os.path, "realpath", side_effect=lambda path: path), \
                 patch.object(m.os.path, check, return_value=False), \
                 patch.object(m, "_capture") as capture, patch("builtins.open") as opened:
                result = m.observe_current_interpreter_records(p)
            self.rejected(result, issue)
            capture.assert_not_called()
            opened.assert_not_called()

    def test_before_and_after_capture_errors_have_no_partial_observation(self):
        p, o = fixture()
        for captures in ((OSError("private fixture"),), (o, OSError("private fixture")),
                         (o, object.__new__(m.Observation))):
            result, _, _ = self.observe(p, captures)
            self.rejected(result, "OBSERVATION_FAILED")
            self.assertNotIn("private fixture", repr(result))

    def test_comparison_failure_at_either_stage_drops_records(self):
        p, o = fixture()
        for captures, count in (((replace(o, abi="changed"),), 1),
                                ((o, replace(o, abi="changed")), 2)):
            result, capture, _ = self.observe(p, captures)
            self.rejected(result, "PROFILE_MISMATCH")
            self.assertEqual(capture.call_count, count)

    def test_after_with_equal_scalars_but_changed_live_anchors_drops_records(self):
        p, o = fixture()
        origin = "/declared/lib/fixture.py"
        loader = SourceFileLoader("fixture", origin)
        module = ModuleType("fixture")
        module.__spec__, module.__loader__, module.__file__ = ModuleSpec("fixture", loader, origin=origin), loader, origin
        row = m.ModuleRecord("fixture", origin, origin, "SOURCE", (), module, module.__spec__, loader)
        p, before = replace(p, modules=(row,)), replace(o, modules=(row,))
        for changed in ("module", "spec", "loader"):
            other_loader = SourceFileLoader("fixture", origin) if changed == "loader" else loader
            other_spec = module.__spec__ if changed == "module" else ModuleSpec("fixture", other_loader, origin=origin)
            other = ModuleType("fixture")
            other.__spec__, other.__loader__, other.__file__ = other_spec, other_loader, origin
            other_row = replace(row, module=other, spec=other_spec, loader=other_loader)
            after = replace(before, modules=(other_row,))
            # Beide Aufnahmen sind einzeln kohärent; Gleichheit der Skalare ersetzt keine Ankerbindung.
            m._shape(after, False)
            result, capture, _ = self.observe(p, (before, after))
            self.rejected(result, "MODULE_MISMATCH")
            self.assertEqual(capture.call_count, 2)

    def test_file_open_read_and_final_digest_failures_drop_before(self):
        p, o = fixture()
        raw = b"synthetic\r\n"
        file = m.FileDigest(p.executable_target, len(raw), hashlib.sha256(raw).hexdigest())
        p, o = replace(p, files=(file,)), replace(o, files=(file,))
        class FailedRead(io.BytesIO):
            def read(self, size):
                raise OSError("private read")
        for opened in (lambda name, mode: FailedRead(), OSError("private open")):
            result, capture, _ = self.observe(p, (o,), opened)
            self.rejected(result, "OBSERVATION_FAILED")
            self.assertEqual(capture.call_count, 1)
        result, capture, _ = self.observe(p, lambda expected, files: replace(o, files=files),
                                         lambda name, mode: io.BytesIO(b"synthetic\n"))
        self.rejected(result, "PROFILE_MISMATCH")
        self.assertEqual(capture.call_count, 2)

    def test_file_overflow_drops_records_before_final_capture(self):
        p, o = fixture()
        file = m.FileDigest(p.executable_target, 1, hashlib.sha256(b"x").hexdigest())
        p, o = replace(p, files=(file,)), replace(o, files=(file,))
        with patch.object(m, "MAX_FILE", 1):
            result, capture, _ = self.observe(p, (o,), lambda name, mode: io.BytesIO(b"xx"))
        self.rejected(result, "FILE_LIMIT")
        self.assertEqual(capture.call_count, 1)

    def test_foreign_and_uninitialized_expected_are_closed_before_io(self):
        class Foreign:
            def __getattribute__(self, name):
                raise RuntimeError("foreign getter")
            def __eq__(self, other):
                raise RuntimeError("foreign equality")
        p, o = fixture()
        for expected, issue in ((Foreign(), "INVALID_RECORD"),
                                (object.__new__(m.DeclaredProfile), "OBSERVATION_FAILED")):
            result, capture, opened = self.observe(expected, (o,))
            self.rejected(result, issue)
            capture.assert_not_called()
            opened.assert_not_called()

    def test_windows_records_fail_before_any_capture_or_io(self):
        with patch.object(m.sys, "platform", "win32"), patch.object(m, "_capture") as capture, \
             patch("builtins.open") as opened, patch.object(m.os.path, "isdir") as directory:
            result = m.observe_current_interpreter_records(object())
        self.rejected(result, "UNSUPPORTED_PLATFORM")
        capture.assert_not_called()
        opened.assert_not_called()
        directory.assert_not_called()

    def test_legacy_wrapper_delegates_once_and_preserves_report_identity(self):
        p, o = fixture()
        for report, observation in ((m.ProfileReport("MATCHED_DECLARED_BASELINE", "NONE", True), o),
                                    (m.ProfileReport("REJECTED_PROFILE", "PROFILE_MISMATCH"), None)):
            result = m.ObservationResult(report, observation)
            with patch.object(m, "observe_current_interpreter_records", return_value=result) as shared:
                self.assertIs(m.observe_current_interpreter(p), report)
            shared.assert_called_once_with(p)

    def test_result_is_frozen_and_does_not_render_private_records(self):
        p, o = fixture()
        result, _, _ = self.observe(p, (o, o))
        self.assertNotIn("/declared", repr(result))
        self.assertNotIn(repr(p.token), repr(result))
        with self.assertRaises(FrozenInstanceError):
            result.observation = None
        with self.assertRaises(FrozenInstanceError):
            result.report = m.ProfileReport("REJECTED_PROFILE", "INVALID_RECORD")

    def test_held_module_mutation_invalidates_later_pure_comparison(self):
        p, o = fixture()
        module = ModuleType("fixture")
        module.__spec__ = ModuleSpec("fixture", BuiltinImporter, origin="built-in")
        module.__loader__ = BuiltinImporter
        row = m.ModuleRecord("fixture", "built-in", "", "BUILTIN", (), module, module.__spec__, BuiltinImporter)
        p, o = replace(p, modules=(row,)), replace(o, modules=(row,))
        result, _, _ = self.observe(p, (o, o))
        self.assertIs(result.observation, o)
        module.__spec__.origin = "changed"
        self.assertEqual(m.validate_profile(p, result.observation).issue, "MODULE_COHERENCY")

    def test_current_cache_exchange_is_not_revalidated_by_held_anchors(self):
        p, o = fixture()
        module = ModuleType("fixture")
        module.__spec__ = ModuleSpec("fixture", BuiltinImporter, origin="built-in")
        module.__loader__ = BuiltinImporter
        row = m.ModuleRecord("fixture", "built-in", "", "BUILTIN", (), module, module.__spec__, BuiltinImporter)
        p, o = replace(p, modules=(row,)), replace(o, modules=(row,))
        result, _, _ = self.observe(p, (o, o))
        replacement = ModuleType("fixture")
        replacement.__spec__, replacement.__loader__ = module.__spec__, BuiltinImporter
        with patch.dict(sys.modules, {"fixture": replacement}):
            self.assertIsNot(sys.modules["fixture"], result.observation.modules[0].module)
            self.assertEqual(m.validate_profile(p, result.observation).status, "MATCHED_DECLARED_BASELINE")
        # Reine Ankerprüfung ist keine aktuelle Cache-/Suchpfad-/Finderinventur.


class ScalarProjectionTests(unittest.TestCase):
    def setUp(self):
        self.boot = sys.modules["_frozen_importlib_external"]
        # Portables Modell: kohärenter Frozenrecord ohne Windows-Dateilocator.
        change = patch.dict(self.boot.__dict__, {"__file__": ""})
        change.start()
        self.addCleanup(change.stop)

    def fixture(self):
        p, o = fixture()
        row = m.ModuleRecord("_frozen_importlib_external", "frozen", "", "FROZEN", (),
                             self.boot, self.boot.__spec__, FrozenImporter)
        known = sys.path_hooks[1]
        p = replace(p, hooks=(zipimporter, known), modules=(row,) + p.modules)
        return p, replace(o, hooks=p.hooks, modules=p.modules), known

    def observe(self, p, o, known, captures=None):
        with patch.object(m.sys, "platform", "linux"), \
             patch.object(m, "_capture", side_effect=captures or (o, replace(o))) as capture, \
             patch.object(m.os.path, "isdir", return_value=True), patch.object(m.os.path, "isfile", return_value=True), \
             patch.object(m.os.path, "realpath", side_effect=lambda path: path), \
             patch.object(m.os.path, "lexists", return_value=False):
            result = m.observe_current_interpreter_scalars(p, known)
        return result, capture

    def reject(self, result, issue):
        self.assertEqual((result.report.status, result.report.issue), ("REJECTED_PROFILE", issue))
        self.assertIsNone(result.scalars)
        self.assertFalse(result.report.trust_attested or result.report.runtime_attested or
                         result.report.method_approved or result.report.import_used_bytes_attested)

    def test_fresh_projection_complete_primitives_and_private_frozen_result(self):
        p, o, known = self.fixture()
        result, capture = self.observe(p, o, known)
        self.assertEqual(capture.call_count, 2)
        self.assertEqual(result.report.status, "MATCHED_DECLARED_BASELINE")
        selection, installation, modules = result.scalars
        self.assertEqual(selection, (p.assumption, p.roots, p.inert_zip, p.controls))
        self.assertEqual(installation, (o.platform, o.implementation, o.version, o.executable, o.executable_target,
                                      o.prefixes, o.abi, o.flags, o.paths, ("BUILTIN", "FROZEN", "PATH"),
                                      ("ZIPIMPORTER", "FILEFINDER"), ()))
        self.assertEqual(modules[0], ("_frozen_importlib_external", "importlib._bootstrap_external",
                                     "_frozen_importlib_external", "frozen", "", "FROZEN", (), "FROZEN", "", "", ()))
        self.assertEqual(modules[1], ("sys", "sys", "sys", "built-in", "", "BUILTIN", (), "BUILTIN", "", "", ()))
        def primitive(value):
            self.assertIn(type(value), (tuple, str, int, type(None)))
            if type(value) is tuple:
                for item in value:
                    primitive(item)
        primitive(result.scalars)
        self.assertNotIn("/declared", repr(result))
        with self.assertRaises(FrozenInstanceError):
            result.scalars = ()

    def test_known_hook_missing_foreign_or_unrelated_is_closed(self):
        p, o, known = self.fixture()
        class Foreign:
            def __getattribute__(self, name):
                raise RuntimeError("private getter")
        for value in (None, Foreign(), hook):
            result, _ = self.observe(p, o, value)
            self.reject(result, "FILEFINDER_BINDING")
        # Selbst eine gleiche harmlose Funktion in Soll, Ist UND separatem Parameter ist keine Factoryhook.
        p, o = replace(p, hooks=(zipimporter, hook)), replace(o, hooks=(zipimporter, hook))
        result, _ = self.observe(p, o, hook)
        self.reject(result, "FILEFINDER_BINDING")

    def test_hook_factory_globals_and_closure_are_actually_bound(self):
        p, o, known = self.fixture()
        wrong = type(known)(known.__code__, {}, closure=known.__closure__)
        p, o = replace(p, hooks=(zipimporter, wrong)), replace(o, hooks=(zipimporter, wrong))
        result, _ = self.observe(p, o, wrong)
        self.reject(result, "FILEFINDER_BINDING")
        wrong = self.boot.FileFinder.path_hook((self.boot.SourceFileLoader, [".synthetic"]))
        p, o = replace(p, hooks=(zipimporter, wrong)), replace(o, hooks=(zipimporter, wrong))
        result, _ = self.observe(p, o, wrong)
        self.reject(result, "FILEFINDER_BINDING")

    def test_factory_requires_complete_observed_frozen_binding(self):
        p, o, known = self.fixture()
        p, o = replace(p, modules=p.modules[1:]), replace(o, modules=o.modules[1:])
        result, _ = self.observe(p, o, known)
        self.reject(result, "FILEFINDER_BINDING")

    def test_actual_source_and_control_fields_are_copied_without_synthesis(self):
        p, o, known = self.fixture()
        loader = SourceFileLoader("fixture", "/declared/lib/fixture.py")
        module = ModuleType("fixture")
        module.__spec__, module.__loader__, module.__file__ = ModuleSpec("fixture", loader, origin=loader.path), loader, loader.path
        row = m.ModuleRecord("fixture", loader.path, loader.path, "SOURCE", (), module, module.__spec__, loader)
        rows = (p.modules[0], row, p.modules[1])
        p, o = replace(p, modules=rows), replace(o, modules=rows)
        result, _ = self.observe(p, o, known)
        self.assertEqual(result.scalars[2][1], ("fixture", "fixture", "fixture", loader.path, loader.path,
                                             "SOURCE", (), "SOURCE", "fixture", loader.path, ()))
        control = ModuleType("__main__")
        control.__spec__, control.__loader__, control.__file__ = None, None, "/declared/control.py"
        row = m.ModuleRecord("__main__", "", control.__file__, "CONTROL", (), control, None, None)
        rows = (row,) + p.modules
        p, o = replace(p, modules=rows, controls=("__main__",)), replace(o, modules=rows)
        result, _ = self.observe(p, o, known)
        self.assertEqual(result.scalars[2][0][2], None)
        self.assertEqual(result.scalars[2][0][7:10], ("NONE", "", ""))

    def test_scalar_controlset_must_equal_complete_observed_roles(self):
        p, o, known = self.fixture()
        result, _ = self.observe(replace(p, controls=("__main__",)), o, known)
        self.reject(result, "CONTROL_MISMATCH")

    def test_projection_files_use_verified_final_hash_rows(self):
        p, o, known = self.fixture()
        raw = b"synthetic\r\n"
        file = m.FileDigest(p.executable_target, len(raw), hashlib.sha256(raw).hexdigest())
        p, o = replace(p, files=(file,)), replace(o, files=(file,))
        def capture(expected, files):
            return replace(o, files=files)
        with patch("builtins.open", side_effect=lambda path, mode: io.BytesIO(raw)):
            result, _ = self.observe(p, o, known, capture)
        self.assertEqual(result.scalars[1][-1], ((file.path, len(raw), file.sha256),))
        with patch("builtins.open", side_effect=lambda path, mode: io.BytesIO(b"synthetic\n")):
            result, _ = self.observe(p, o, known, capture)
        self.reject(result, "PROFILE_MISMATCH")

    def test_stricter_scalar_text_prefix_and_frozen_locator_forms(self):
        p, o, known = self.fixture()
        for field, value in (("abi", "bad\0abi"), ("prefixes", ("relative",) * 4)):
            result, _ = self.observe(replace(p, **{field: value}), replace(o, **{field: value}), known)
            self.reject(result, "SCALAR_FORM" if field == "abi" else "PATH_MISMATCH")
        for path in ("relative.py", "/declared/../file.py", "/declared//file.py"):
            with patch.dict(self.boot.__dict__, {"__file__": path}):
                rows = (replace(p.modules[0], file=path), p.modules[1])
                result, _ = self.observe(replace(p, modules=rows), replace(o, modules=rows), known)
                self.reject(result, "PATH_MISMATCH")

    def test_alias_pairs_preserve_fixed_names_and_local_identity(self):
        p, o, known = self.fixture()
        alias = replace(p.modules[0], name="importlib._bootstrap_external")
        rows = (p.modules[0], alias, p.modules[1])
        p, o = replace(p, modules=rows), replace(o, modules=rows)
        result, _ = self.observe(p, o, known)
        pair = ("_frozen_importlib_external", "importlib._bootstrap_external")
        self.assertEqual(result.scalars[2][0][-1], pair)
        self.assertEqual(result.scalars[2][1][-1], pair)
        other = ModuleType("importlib._bootstrap_external")
        other.__spec__, other.__loader__, other.__file__ = self.boot.__spec__, FrozenImporter, ""
        rows = (p.modules[0], replace(alias, module=other), p.modules[2])
        result, _ = self.observe(replace(p, modules=rows), replace(o, modules=rows), known)
        self.reject(result, "MODULE_COHERENCY")

    def test_all_other_fixed_frozen_pairs_and_singletons(self):
        for pair, names in ((("_frozen_importlib", "importlib._bootstrap"),
                             ("importlib._bootstrap", "_frozen_importlib")),
                            (("_collections_abc", "collections.abc"), ("collections.abc", "_collections_abc")),
                            (("os.path", "posixpath"), ("posixpath", "posixpath"))):
            p, o, known = self.fixture()
            module = ModuleType(names[0])
            module.__spec__, module.__loader__ = ModuleSpec(names[1], FrozenImporter, origin="frozen"), FrozenImporter
            for selected in (pair[:1], pair):
                extra = tuple(m.ModuleRecord(n, "frozen", "", "FROZEN", (), module, module.__spec__, FrozenImporter)
                              for n in selected)
                rows = tuple(sorted(p.modules + extra, key=lambda r: r.name))
                result, _ = self.observe(replace(p, modules=rows), replace(o, modules=rows), known)
                self.assertEqual(result.report.status, "MATCHED_DECLARED_BASELINE")
                projected = {r[0]: r for r in result.scalars[2]}
                for n in selected:
                    self.assertEqual(projected[n][1:3], names)
                    self.assertEqual(projected[n][-1], tuple(sorted(pair)) if len(selected) == 2 else ())

    def test_foreign_suffixes_are_rejected_before_equality_or_iteration(self):
        p, o, known = self.fixture()
        class Foreign:
            def __getattribute__(self, name):
                raise RuntimeError("foreign getter")
            def __eq__(self, other):
                raise RuntimeError("foreign equality")
            def __iter__(self):
                raise RuntimeError("foreign iteration")
        for value in ([Foreign()], ["x" * 4097], Foreign(), [".x"] * 257):
            with patch.dict(self.boot.__dict__, {"EXTENSION_SUFFIXES": value}):
                result, _ = self.observe(p, o, known)
            self.reject(result, "INVALID_RECORD" if type(value) is list and len(value) <= 256 else "FILEFINDER_BINDING")

    def test_hook_and_factory_code_changes_during_projection_are_rejected(self):
        p, o, known = self.fixture()
        factory = self.boot.FileFinder.__dict__["path_hook"].__func__
        original = m._project_scalars
        for target in (known, factory):
            old = target.__code__
            def mutate(expected, observation):
                scalars = original(expected, observation)
                target.__code__ = old.replace(co_name="synthetic_changed_code")
                return scalars
            try:
                with patch.object(m, "_project_scalars", side_effect=mutate):
                    result, _ = self.observe(p, o, known)
                self.reject(result, "FILEFINDER_BINDING")
            finally:
                target.__code__ = old

    def test_failed_fresh_capture_cannot_project_old_report_or_records(self):
        p, o, known = self.fixture()
        result, _ = self.observe(p, o, known, (o, OSError("private capture")))
        self.reject(result, "OBSERVATION_FAILED")
        self.assertNotIn("private capture", repr(result))

    def test_module_mutation_during_projection_prevents_scalar_return(self):
        p, o, known = self.fixture()
        original = m._project_scalars
        def mutate(expected, observation):
            scalars = original(expected, observation)
            observation.modules[0].module.__file__ = "/changed/file.py"
            return scalars
        with patch.object(m, "_project_scalars", side_effect=mutate):
            result, _ = self.observe(p, o, known)
        self.reject(result, "MODULE_COHERENCY")

    def test_hook_configuration_mutation_during_projection_is_closed(self):
        p, o, known = self.fixture()
        original = m._project_scalars
        suffixes = self.boot.SOURCE_SUFFIXES
        old = suffixes[:]
        def mutate(expected, observation):
            scalars = original(expected, observation)
            suffixes.append(".synthetic")
            return scalars
        try:
            with patch.object(m, "_project_scalars", side_effect=mutate):
                result, _ = self.observe(p, o, known)
            self.reject(result, "FILEFINDER_BINDING")
        finally:
            suffixes[:] = old

    def test_deleted_module_name_during_projection_is_fixed_rejection(self):
        p, o, known = self.fixture()
        original = m._project_scalars
        old_name = self.boot.__dict__["__name__"]
        def mutate(expected, observation):
            del observation.modules[0].module.__dict__["__name__"]
            return original(expected, observation)
        try:
            with patch.object(m, "_project_scalars", side_effect=mutate):
                result, _ = self.observe(p, o, known)
            self.reject(result, "INVALID_RECORD")
        finally:
            self.boot.__dict__["__name__"] = old_name

    def test_windows_scalar_api_is_unsupported_before_io_or_hook_access(self):
        with patch.object(m.sys, "platform", "win32"), patch.object(m, "_capture") as capture, \
             patch("builtins.open") as opened:
            result = m.observe_current_interpreter_scalars(object(), object())
        self.reject(result, "UNSUPPORTED_PLATFORM")
        capture.assert_not_called()
        opened.assert_not_called()


@unittest.skipUnless(sys.platform == "linux", "Linux-only observation; portable validation runs everywhere")
class ActualLinuxProfileTests(unittest.TestCase):
    def test_current_isolated_controlruntime_matches_explicit_caller_baseline(self):
        self.assertTrue(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)
        r = LINUX_BOOTSTRAP
        self.assertEqual((r.status, r.issue), ("MATCHED_DECLARED_BASELINE", "NONE"))
        self.assertFalse(r.trust_attested or r.runtime_attested)

    def test_actual_records_result_retains_successful_after_inventory(self):
        result = LINUX_RECORDS
        self.assertIs(type(result), m.ObservationResult)
        self.assertEqual(result.report, LINUX_BOOTSTRAP)
        self.assertIs(type(result.observation), m.Observation)
        self.assertTrue(result.observation.modules)
        self.assertEqual(result.observation.files, ())
        self.assertEqual(result.observation.flags, (1, 1, 1, 1, 1, 0))
        self.assertFalse(result.report.runtime_attested or result.report.import_used_bytes_attested)

    def test_actual_scalar_projection_before_mock_bootstrap(self):
        self.assertEqual(LINUX_SCALARS.report, LINUX_BOOTSTRAP)
        self.assertIs(type(LINUX_SCALARS.scalars), tuple)
        selection, installation, modules = LINUX_SCALARS.scalars
        self.assertEqual(selection[3], ("__main__", "dgn007_import_runtime_profile"))
        self.assertEqual(installation[10], ("ZIPIMPORTER", "FILEFINDER"))
        self.assertEqual(tuple(r[0] for r in modules), tuple(r.name for r in LINUX_RECORDS.observation.modules))


if __name__ == "__main__":
    unittest.main()
