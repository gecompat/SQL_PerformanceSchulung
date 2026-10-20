"""Auswahl und frische Aufnahme ausschließlich in eigener Modellumgebung."""
import ast
import builtins
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_selected_profile as f

m = f.m
R = f.replace_at


def fixture():
    install, controls, rows, cache = f.fixture()
    install = R(install, 14, ())  # Keine physisch ausgewählten F3 oder Reads.
    bootstrap, row = f.own_module("_frozen_importlib_external", "FROZEN",
        module_name="importlib._bootstrap_external", spec_name="_frozen_importlib_external")
    bootstrap.__dict__["__builtins__"] = dict(vars(builtins))
    # Ausschließlich fixtureeigener statischer Code in fixtureeigener Namespace.
    exec("""class FileFinder:
    @classmethod
    def path_hook(cls, *loader_details):
        def own_hook(path):
            if cls or loader_details:
                raise AssertionError('HOOK_MUST_NOT_RUN')
        return own_hook
class ExtensionFileLoader: pass
class SourceFileLoader: pass
class SourcelessFileLoader: pass
EXTENSION_SUFFIXES = ['.synthetic-so']
SOURCE_SUFFIXES = ['.py']
BYTECODE_SUFFIXES = ['.pyc']
""", bootstrap.__dict__)
    d = bootstrap.__dict__
    details = tuple((d[loader], d[suffix].copy()) for loader, suffix in (
        ("ExtensionFileLoader", "EXTENSION_SUFFIXES"), ("SourceFileLoader", "SOURCE_SUFFIXES"),
        ("SourcelessFileLoader", "BYTECODE_SUFFIXES")))
    hook = d["FileFinder"].path_hook(*details)
    cache[row[0]] = bootstrap
    rows = tuple(sorted(rows + (row,)))
    runtime = cache["sys"]
    runtime.__dict__.update(modules=cache, platform="linux",
        implementation=SimpleNamespace(name="cpython"), version_info=install[3],
        executable=install[4], prefix=install[6][0], exec_prefix=install[6][1],
        base_prefix=install[6][2], base_exec_prefix=install[6][3], path=list(install[8]),
        meta_path=[f.BuiltinImporter, f.FrozenImporter, f.PathFinder], path_hooks=[f.zipimporter, hook],
        flags=SimpleNamespace(isolated=1, no_site=1, ignore_environment=1, safe_path=True, optimize=0),
        dont_write_bytecode=True)
    filesystem = SimpleNamespace(path=SimpleNamespace(
        isabs=lambda path: path.startswith("/"), isdir=lambda path: path in install[9],
        isfile=lambda path: path == install[4], realpath=lambda path: path,
        lexists=lambda path: path != install[10], islink=lambda path: False))
    config = SimpleNamespace(get_config_var=lambda name: install[7] if name == "SOABI" else None)
    return install, controls, rows, cache, runtime, filesystem, config, hook


class SelectedObservationTests(unittest.TestCase):
    def setUp(self):
        (self.install, self.controls, self.rows, self.cache, self.runtime,
         self.filesystem, self.config, self.hook) = fixture()
        self.real = sys.modules.copy()
        self.token = b"t" * 32
        self.patches = (patch.object(m, "sys", self.runtime), patch.object(m, "os", self.filesystem),
                        patch.object(m, "sysconfig", self.config))
        for selected in self.patches:
            selected.start()
            self.addCleanup(selected.stop)

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.real))
        self.assertTrue(all(sys.modules[name] is value for name, value in self.real.items()))

    def call(self, **changes):
        values = dict(installation=self.install, controls=self.controls, modules=self.rows,
                      token=self.token, separately_known_filefinder_hook=self.hook)
        values.update(changes)
        return m.observe_selected_profile_scalars(**values)

    def accepted(self, **changes):
        result = self.call(**changes)
        self.assertEqual((result.report.status, result.report.issue), ("MATCHED_SELECTED_PROFILE", "NONE"))
        self.assertIsNotNone(result.profile)
        self.assertIsNotNone(result.scalars)
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        self.assertFalse(result.report.runtime_attested or result.report.trust_attested
                         or result.report.import_used_bytes_attested or result.report.method_approved)
        self.assertNotIn("/synthetic", repr(result))
        return result

    def rejected(self, **changes):
        result = self.call(**changes)
        self.assertEqual((result.report.status, result.report.issue),
                         ("REJECTED_SELECTED_OBSERVATION", "SELECTED_OBSERVATION_FAILED"))
        self.assertIsNone(result.profile)
        self.assertIsNone(result.scalars)
        self.assertFalse(result.report.runtime_attested or result.report.trust_attested
                         or result.report.import_used_bytes_attested or result.report.method_approved)
        self.assertNotIn("/synthetic", repr(result))
        return result

    def after_inner(self, change):
        original = m.observe_current_interpreter_scalars
        def observed(expected, known):
            result = original(expected, known)
            self.assertIsNotNone(result.scalars, result.report)
            change(expected)
            return result
        return patch.object(m, "observe_current_interpreter_scalars", observed)

    def test_actual_capture_complete_scalars_same_profile_and_no_io(self):
        captured, original = [], m._capture
        def capture(expected, files):
            captured.append(expected)
            return original(expected, files)
        def forbidden(*args, **kwargs):
            raise AssertionError("UNSELECTED_OPERATION")
        namespaces = {name: module.__dict__.copy() for name, module in self.cache.items()}
        with patch.object(m, "_capture", capture), \
             patch.dict(m.__dict__["__builtins__"], open=forbidden, __import__=forbidden), \
             patch.object(m, "hashlib", SimpleNamespace(sha256=forbidden)):
            result = self.accepted()
        self.assertEqual(len(captured), 3)
        self.assertTrue(all(expected is result.profile for expected in captured))
        s = self.install
        self.assertEqual(result.scalars, ((s[0], s[9], s[10], self.controls),
            (s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[11], s[8], s[12], s[13], s[14]), self.rows))
        self.assertEqual(result.profile.token, self.token)
        for row in result.profile.modules:
            self.assertIs(row.module, self.cache[row.name])
        for name, module in self.cache.items():
            self.assertEqual(module.__dict__, namespaces[name])
        with self.assertRaises(FrozenInstanceError):
            result.scalars = None

    def test_late_primitive_fault_precedes_all_ambient_access(self):
        accessed = []
        class Ambient:
            def __getattr__(self, name):
                accessed.append(name)
                raise AssertionError("EARLY_RUNTIME_ACCESS")
        changed = R(self.rows[-1], 10, (object(),))
        with patch.object(m, "sys", Ambient()), \
             patch.object(m, "observe_current_interpreter_scalars", side_effect=AssertionError("OBSERVE")) as observer:
            self.rejected(modules=R(self.rows, len(self.rows) - 1, changed))
            self.rejected(installation=R(self.install, 3, (3, 12, True)))
        self.assertEqual(accessed, [])
        observer.assert_not_called()

    def test_every_selected_scalar_field_must_match_actual_full_projection(self):
        original = m.observe_current_interpreter_scalars
        def wrong(value):
            return "DIFFERENT" if type(value) is str else (value + 1 if type(value) is int else ("DIFFERENT",))
        # Alle vier Selection-, zwölf Installations- und elf P11-Felder.
        for section, count in ((0, 4), (1, 12), (2, 11)):
            for index in range(count):
                def observed(expected, known):
                    result = original(expected, known)
                    self.assertIsNotNone(result.scalars, result.report)
                    scalar = result.scalars
                    if section == 2:
                        row = scalar[2][0]
                        scalar = R(scalar, 2, R(scalar[2], 0, R(row, index, wrong(row[index]))))
                    else:
                        row = scalar[section]
                        scalar = R(scalar, section, R(row, index, wrong(row[index])))
                    return m.ScalarObservationResult(result.report, scalar)
                with self.subTest(section=section, field=index), \
                     patch.object(m, "observe_current_interpreter_scalars", observed):
                    self.rejected()

    def test_actual_runtime_differs_from_valid_selected_values(self):
        for index, value in ((3, (3, 12, 99)), (4, "/synthetic/other-python"),
                             (5, "/synthetic/other-target"), (6, ("/other",) * 4),
                             (7, "different-abi"), (8, self.install[8][::-1])):
            with self.subTest(field=index):
                self.rejected(installation=R(self.install, index, value))

    def test_platform_and_foreign_container_forms_are_rejected_without_dispatch(self):
        accessed = []
        class Foreign(list):
            def __iter__(self):
                accessed.append("ITERATION")
                raise AssertionError("FOREIGN_ITERATION")
        for attribute, value in (("modules", Foreign()), ("meta_path", Foreign()),
                                 ("path_hooks", Foreign()), ("platform", "win32")):
            with patch.object(self.runtime, attribute, value):
                self.rejected()
        self.assertEqual(accessed, [])
        with patch.object(self.runtime, "meta_path", tuple(self.runtime.meta_path)), \
             patch.object(self.runtime, "path_hooks", tuple(self.runtime.path_hooks)):
            self.accepted()

    def test_cache_exchange_accession_and_coherent_module_replacement_after_inner(self):
        for change in ("exchange", "accession", "replacement"):
            def mutate(expected):
                if change == "exchange":
                    self.runtime.modules = self.cache.copy()
                elif change == "accession":
                    self.cache["extra"] = f.own_module("extra", "BUILTIN", file="")[0]
                else:
                    self.cache["sys"] = f.own_module("sys", "BUILTIN", file="")[0]
            with self.subTest(change=change), self.after_inner(mutate):
                self.rejected()
            self.runtime.modules = self.cache
            self.cache.pop("extra", None)
            self.cache["sys"] = self.runtime

    def test_module_spec_loader_metadata_drift_after_inner(self):
        module = self.cache["package"]
        for target, attribute, value in ((module, "__file__", "/synthetic/other.py"),
                (module.__spec__, "origin", "/synthetic/other.py"),
                (module.__spec__, "loader", f.SourceFileLoader("package", module.__file__)),
                (module.__loader__, "path", "/synthetic/other.py"),
                (module.__spec__, "submodule_search_locations", ["/synthetic/stdlib/other"])):
            old = getattr(target, attribute)
            with self.after_inner(lambda expected: setattr(target, attribute, value)):
                self.rejected()
            setattr(target, attribute, old)

    def test_runtime_scalar_drift_after_inner_is_freshly_checked(self):
        for attribute, value in (("version_info", (3, 12, 99)), ("executable", "/synthetic/other"),
                                 ("prefix", "/other"), ("path", self.runtime.path[::-1])):
            old = getattr(self.runtime, attribute)
            with self.after_inner(lambda expected: setattr(self.runtime, attribute, value)):
                self.rejected()
            setattr(self.runtime, attribute, old)
        with self.after_inner(lambda expected: setattr(self.config, "get_config_var", lambda name: "other")):
            self.rejected()

    def test_finder_hook_container_identity_and_content_post(self):
        for attribute in ("meta_path", "path_hooks"):
            old = getattr(self.runtime, attribute)
            with self.after_inner(lambda expected: setattr(self.runtime, attribute, list(old))):
                self.rejected()
            setattr(self.runtime, attribute, old)
            with self.after_inner(lambda expected: old.reverse()):
                self.rejected()
            old.reverse()

    def test_hook_factory_code_closure_and_suffix_anchors_precede_observation(self):
        namespace = self.cache["_frozen_importlib_external"].__dict__
        finder = namespace["FileFinder"]
        descriptor = finder.__dict__["path_hook"]
        def mutate(expected):
            # Gleiche Werte und derselbe Hook, aber ausgetauschte Factory.
            function = descriptor.__func__
            replacement = type(function)(function.__code__, namespace, function.__name__)
            finder.path_hook = classmethod(replacement)
        with self.after_inner(mutate):
            self.rejected()
        finder.path_hook = descriptor
        configured = namespace["SOURCE_SUFFIXES"]
        details = self.hook.__closure__[1].cell_contents
        with self.after_inner(lambda expected: (configured.append(".other"), details[1][1].append(".other"))):
            self.rejected()
        configured.pop(); details[1][1].pop()
        self.rejected(separately_known_filefinder_hook=f.hook)

    def test_provider_exchange_after_inner_does_not_accept_held_receipt(self):
        for name in ("sys", "os", "sysconfig"):
            old = getattr(m, name)
            with self.after_inner(lambda expected: setattr(m, name, SimpleNamespace())):
                self.rejected()
            setattr(m, name, old)

    def test_unknown_exception_is_fixed_and_has_no_partial_payload(self):
        with patch.object(m, "observe_current_interpreter_scalars", side_effect=RuntimeError("/synthetic/private")):
            result = self.rejected()
        self.assertNotIn("private", repr(result.report))

    def test_report_or_foreign_scalar_is_not_authority(self):
        accessed = []
        class Foreign:
            def __eq__(self, other):
                accessed.append("EQUALITY")
                raise AssertionError("FOREIGN_EQUALITY")
        good = m.ProfileReport("MATCHED_DECLARED_BASELINE", "NONE", True)
        for result in (object(), m.ScalarObservationResult(good),
                m.ScalarObservationResult(good, (Foreign(),)),
                m.ScalarObservationResult(m.ProfileReport("REJECTED_PROFILE", "NONE"), ()),
                SimpleNamespace(report=good, scalars=())):
            with patch.object(m, "observe_current_interpreter_scalars", return_value=result):
                self.rejected()
        self.assertEqual(accessed, [])

    def test_post_key_caps_before_metadata_lookup_and_shared_scan(self):
        package = self.cache["package"]
        for key in ("x" * 4097, "bad\0key"):
            with self.after_inner(lambda expected: package.__dict__.update({key: None})):
                self.rejected()
            package.__dict__.pop(key)
        with self.after_inner(lambda expected: package.__dict__.update(
                ("filler_" + str(index), object()) for index in range(16369))):
            self.rejected()

    def test_returned_profile_keeps_anchors_for_later_body_observation(self):
        result = self.accepted()
        profile = result.profile
        self.cache["package"].__file__ = "/synthetic/other.py"
        # Bestehende API prüft dieselben Anker, keine neue Baseline aus Drift.
        again = m.observe_current_interpreter_scalars(profile, self.hook)
        self.assertIsNone(again.scalars)
        self.assertIs(profile.modules[4].module, self.cache["package"])

    def test_new_bridge_has_no_execution_import_file_or_hash_calls(self):
        tree = ast.parse(f.PATH.read_bytes())
        selected = {"observe_selected_profile_scalars", "_selected_containers", "_selected_post",
                    "_selected_hook_post", "_bind_selected"}
        nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in selected]
        self.assertEqual(len(nodes), len(selected))
        calls = {node.func.id for root in nodes for node in ast.walk(root)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertTrue({"open", "exec", "eval", "compile", "__import__", "print", "Popen"}.isdisjoint(calls))
        self.assertFalse(any(isinstance(node, ast.Attribute) and node.attr in ("sha256", "get_code", "exec_module")
                             for root in nodes for node in ast.walk(root)))


if __name__ == "__main__":
    unittest.main()
