"""Reine Auswahlbindung mit eigenen synthetischen Metadaten und Ankern."""
import ast
import builtins
from dataclasses import FrozenInstanceError
from importlib.machinery import BuiltinImporter, FrozenImporter, PathFinder, ModuleSpec, SourceFileLoader, ExtensionFileLoader
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
from zipimport import zipimporter

PATH = Path(__file__).resolve().parents[1] / "Tools/dgn007_import_runtime_profile.py"
spec = importlib.util.spec_from_file_location("dgn007_import_runtime_profile", PATH)
m = importlib.util.module_from_spec(spec)
m.__dict__["__builtins__"] = dict(vars(builtins))
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def hook(path):
    raise AssertionError("HOOK_MUST_NOT_RUN")


def replace_at(value, index, replacement):
    return value[:index] + (replacement,) + value[index + 1:]


def own_module(name, kind, *, module_name=None, spec_name=None, file=None, locations=()):
    module_name = name if module_name is None else module_name
    spec_name = name if spec_name is None else spec_name
    filename = file if file is not None else ("/synthetic/stdlib/" + name.replace(".", "/") + ".py")
    loader = {"BUILTIN": BuiltinImporter, "FROZEN": FrozenImporter, "NONE": None}.get(kind)
    if kind == "SOURCE":
        loader = SourceFileLoader(name, filename)
    elif kind == "EXTENSION":
        loader = ExtensionFileLoader(name, filename)
    origin = "built-in" if kind == "BUILTIN" else "frozen" if kind == "FROZEN" else filename
    selected_spec = None if kind == "NONE" else ModuleSpec(spec_name, loader, origin=origin)
    if selected_spec is not None:
        selected_spec.submodule_search_locations = list(locations) if locations else None
    module = ModuleType(module_name)
    module.__dict__.update(__spec__=selected_spec, __loader__=loader, __file__=filename)
    public_kind = "CONTROL" if kind == "NONE" or name == "dgn007_import_runtime_profile" else kind
    row = (name, module_name, None if selected_spec is None else spec_name,
           "" if selected_spec is None else origin, filename, public_kind, locations,
           kind, name if kind in ("SOURCE", "EXTENSION") else "",
           filename if kind in ("SOURCE", "EXTENSION") else "", ())
    return module, row


def fixture():
    install = (m.ASSUMPTION, "linux", "cpython", (3, 12, 14),
        "/synthetic/bin/python", "/synthetic/bin/python", ("/synthetic",) * 4, "cpython-312",
        ("/synthetic/stdlib", "/synthetic/stdlib/lib-dynload", "/synthetic/python312.zip"),
        ("/synthetic/stdlib", "/synthetic/stdlib/lib-dynload"), "/synthetic/python312.zip",
        (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"), ("ZIPIMPORTER", "FILEFINDER"),
        (("/synthetic/bin/python", 123, "4" * 64),))
    cache, rows = {}, []
    for name, kind, filename, locations in (
        ("__main__", "NONE", "/synthetic/bootstrap.py", ()),
        ("dgn007_import_runtime_profile", "SOURCE", "/synthetic/control.py", ()),
        ("native", "EXTENSION", "/synthetic/stdlib/lib-dynload/native.so", ()),
        ("package", "SOURCE", "/synthetic/stdlib/package/__init__.py", ("/synthetic/stdlib/package",)),
        ("sys", "BUILTIN", "", ())):
        module, row = own_module(name, kind, file=filename, locations=locations)
        cache[name] = module
        rows.append(row)
    return install, ("__main__", "dgn007_import_runtime_profile"), tuple(rows), cache


class SelectedProfileTests(unittest.TestCase):
    def setUp(self):
        self.install, self.controls, self.rows, self.cache = fixture()
        self.real = sys.modules.copy()
        self.finders = (BuiltinImporter, FrozenImporter, PathFinder)
        self.hooks = (zipimporter, hook)
        self.token = b"t" * 32

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.real))
        self.assertTrue(all(sys.modules[name] is value for name, value in self.real.items()))

    def call(self, **changes):
        values = dict(installation=self.install, controls=self.controls, modules=self.rows,
                      token=self.token, cache=self.cache, finders=self.finders, hooks=self.hooks)
        values.update(changes)
        return m.bind_selected_profile(**values)

    def accepted(self, **changes):
        result = self.call(**changes)
        self.assertEqual((result.report.status, result.report.issue), ("BOUND_SELECTED_PROFILE", "NONE"))
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        self.assertFalse(result.report.runtime_attested or result.report.trust_attested
                         or result.report.import_used_bytes_attested or result.report.method_approved)
        return result

    def rejected(self, issue=None, **changes):
        result = self.call(**changes)
        self.assertEqual(result.report.status, "REJECTED_SELECTED_PROFILE")
        self.assertIsNone(result.profile)
        if issue is not None:
            self.assertEqual(result.report.issue, issue)
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_complete_private_binding_and_selected_field_roundtrip(self):
        result = self.accepted()
        p = result.profile
        self.assertEqual((p.assumption, "linux", p.implementation, p.version, p.executable,
            p.executable_target, p.prefixes, p.abi, p.paths, p.roots, p.inert_zip,
            (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"), ("ZIPIMPORTER", "FILEFINDER"),
            tuple((f.path, f.size, f.sha256) for f in p.files)), self.install)
        self.assertEqual(p.token, self.token)
        self.assertEqual(p.controls, self.controls)
        for expected, actual in zip(self.rows, p.modules):
            local = self.cache[expected[0]]
            self.assertIs(actual.module, local)
            self.assertIs(actual.spec, local.__spec__)
            self.assertIs(actual.loader, local.__loader__)
            self.assertEqual((actual.name, actual.origin, actual.file, actual.kind, actual.locations),
                             tuple(expected[i] for i in (0, 3, 4, 5, 6)))
        self.assertNotIn("/synthetic", repr(result) + repr(p))
        with self.assertRaises(FrozenInstanceError):
            result.profile = None

    def test_valid_selected_installation_changes_are_not_host_observations(self):
        variants = [(3, (3, 12, 99)), (4, "/synthetic/bin/alias"), (6, ("/other",) * 4),
                    (7, "other-abi"), (8, self.install[8][::-1]), (9, self.install[9][::-1]),
                    (14, ((self.install[5], 999, "5" * 64),))]
        for index, value in variants:
            selected = replace_at(self.install, index, value)
            result = self.accepted(installation=selected)
            p = result.profile
            field = {3: "version", 4: "executable", 6: "prefixes", 7: "abi", 8: "paths", 9: "roots"}
            if index in field:
                self.assertEqual(getattr(p, field[index]), value)
            else:
                self.assertEqual(tuple((f.path, f.size, f.sha256) for f in p.files), value)
        target = "/synthetic/bin/target"
        selected = replace_at(replace_at(self.install, 5, target), 14, ((target, 0, "6" * 64),))
        self.assertEqual(self.accepted(installation=selected).profile.executable_target, target)
        inert = "/synthetic/missing.zip"
        selected = replace_at(replace_at(self.install, 10, inert), 8, self.install[8][:2] + (inert,))
        self.assertEqual(self.accepted(installation=selected).profile.inert_zip, inert)

    def test_all_installation_field_shapes_and_context_constraints(self):
        invalid = ("OTHER", "win32", "pypy", (3, 13, 0), "relative", "/bad/../target", ("/x",),
                   "", ("/unselected",), ("/same", "/same"), "/bad//zip", (0,) * 6,
                   ("FROZEN", "BUILTIN", "PATH"), ("FILEFINDER", "ZIPIMPORTER"), (("relative", 0, "4" * 64),))
        for index, value in enumerate(invalid):
            with self.subTest(field=index):
                self.rejected(installation=replace_at(self.install, index, value))

    def test_all_eleven_module_fields_are_bound(self):
        row = self.rows[3]
        invalid = ("other", "other", "other", "/synthetic/stdlib/other.py",
                   "/synthetic/stdlib/other.py", "EXTENSION", ("/synthetic/stdlib/other",),
                   "EXTENSION", "other", "/synthetic/stdlib/other.py", ("os.path", "posixpath"))
        for index, value in enumerate(invalid):
            with self.subTest(field=index):
                self.rejected(modules=replace_at(self.rows, 3, replace_at(row, index, value)))
        # Konsistente alternative Sourcefelder bleiben am tatsächlichen lokalen Modul gebunden.
        changed = row[:3] + ("/synthetic/stdlib/other.py",) * 2 + row[5:9] + ("/synthetic/stdlib/other.py",) + row[10:]
        self.rejected("MODULE_COHERENCY", modules=replace_at(self.rows, 3, changed))

    def test_exact_cache_set_and_irrelevant_insertion_order(self):
        self.accepted(cache=dict(reversed(tuple(self.cache.items()))))
        self.rejected(cache={k: v for k, v in self.cache.items() if k != "sys"})
        self.rejected(cache=dict(self.cache, extra=ModuleType("extra")))
        self.rejected(modules=self.rows[::-1])
        self.rejected(modules=self.rows + (self.rows[-1],))

    def test_late_invalid_selection_precedes_early_anchor_failure(self):
        broken = dict(self.cache, __main__=object())
        changed = replace_at(self.rows[-1], 10, (object(),))
        self.rejected("SELECTION_FORM", cache=broken, modules=replace_at(self.rows, 4, changed))
        self.rejected("SELECTION_FORM", cache=broken, installation=replace_at(self.install, 3, (3, 12, True)))

    def test_foreign_primitives_and_containers_do_not_dispatch(self):
        class Foreign:
            def __iter__(self):
                raise AssertionError("ITERATION")
            def __eq__(self, other):
                raise AssertionError("EQUALITY")
        class ForeignTuple(tuple):
            def __iter__(self):
                raise AssertionError("ITERATION")
        for changes in (dict(installation=Foreign()), dict(modules=ForeignTuple(self.rows)),
                        dict(controls=Foreign()), dict(token=Foreign()), dict(hooks=Foreign()),
                        dict(modules=replace_at(self.rows, 4, replace_at(self.rows[4], 1, Foreign())))):
            self.rejected(**changes)

    def test_foreign_local_metadata_and_namespace_keys_do_not_dispatch(self):
        class Foreign:
            def __hash__(self):
                return hash("__name__")
            def __eq__(self, other):
                raise AssertionError("EQUALITY")
        for location in ("module", "spec", "loader"):
            install, controls, rows, cache = fixture()
            module = cache["package"]
            namespace = (module.__dict__ if location == "module" else module.__spec__.__dict__
                         if location == "spec" else module.__loader__.__dict__)
            key = "__name__" if location == "module" else "name"
            namespace[key] = Foreign()
            self.rejected(cache=cache)
        module = self.cache["package"]
        foreign = Foreign()
        # Kein kollidierender echter Key bei Fixtureanlage; während der API kein Lookup.
        module.__dict__.pop("__name__")
        module.__dict__[foreign] = None
        self.rejected("ANCHOR_FORM")
        self.rejected("ANCHOR_FORM", cache={foreign: object()})

    def test_full_frozen_aliases_require_shared_live_objects(self):
        module, row = own_module("posixpath", "FROZEN")
        pair = ("os.path", "posixpath")
        rows = tuple(sorted(self.rows + (replace_at(replace_at(row, 0, "os.path"), 10, pair),
                                              replace_at(row, 10, pair))))
        cache = dict(self.cache, posixpath=module)
        cache["os.path"] = module
        self.accepted(modules=rows, cache=cache)
        other, _ = own_module("posixpath", "FROZEN")
        cache["os.path"] = other
        self.rejected("MODULE_COHERENCY", modules=rows, cache=cache)
        self.rejected("ALIAS_FORM", modules=tuple(replace_at(r, 10, ()) if r[0] in pair else r for r in rows))

    def test_both_mixed_frozen_source_orientations_keep_complete_records(self):
        for frozen, source in (("os.path", "posixpath"), ("posixpath", "os.path"),
                               ("importlib._bootstrap", "_frozen_importlib"),
                               ("_frozen_importlib", "importlib._bootstrap")):
            module_name, spec_name = m.FROZEN_NAMES.get(frozen, (frozen, frozen))
            a, row_a = own_module(frozen, "FROZEN", module_name=module_name, spec_name=spec_name)
            b, row_b = own_module(source, "SOURCE")
            cache = dict(self.cache)
            cache.update({frozen: a, source: b})
            rows = tuple(sorted(self.rows + (row_a, row_b)))
            result = self.accepted(modules=rows, cache=cache)
            self.assertEqual(len(result.profile.modules), len(rows))

    def test_package_loader_spec_and_control_drift(self):
        for change in ("locations", "loader_path", "spec_origin", "module_file", "loader_identity"):
            _, _, _, cache = fixture()
            module = cache["package"]
            if change == "locations":
                module.__spec__.submodule_search_locations = ["/synthetic/stdlib/other"]
            elif change == "loader_path":
                module.__loader__.path = "/synthetic/stdlib/other.py"
            elif change == "spec_origin":
                module.__spec__.origin = "/synthetic/stdlib/other.py"
            elif change == "module_file":
                module.__file__ = "/synthetic/stdlib/other.py"
            else:
                module.__spec__.loader = SourceFileLoader("package", module.__file__)
            self.rejected(cache=cache)
        self.rejected(controls=("__main__",))
        self.rejected(controls=self.controls + ("other",))
        self.rejected(finders=self.finders[::-1])
        self.rejected(hooks=(zipimporter, object()))

    def test_caps_utf8_nul_and_no_partial_profile(self):
        self.accepted(installation=replace_at(self.install, 7, "x" * 4096))
        self.rejected("SELECTION_LIMIT", modules=self.rows * 52)
        self.rejected(installation=replace_at(self.install, 7, "x" * 4097))
        self.rejected(installation=replace_at(self.install, 7, "é" * 2049))
        self.rejected(installation=replace_at(self.install, 7, "bad\0abi"))
        self.rejected(installation=replace_at(self.install, 7, "\ud800"))
        files = ((self.install[5], m.MAX_FILE + 1, "4" * 64),)
        self.rejected(installation=replace_at(self.install, 14, files))
        locations = tuple("/synthetic/stdlib/x" for _ in range(128))
        rows = tuple(replace_at(replace_at(self.rows[3], 0, "p" + str(i)), 6, locations) for i in range(128))
        self.rejected("SELECTION_LIMIT", modules=rows)

    def test_no_io_hash_import_observation_or_hook_calls(self):
        cache_before = self.cache.copy()
        namespaces = {name: module.__dict__.copy() for name, module in self.cache.items()}
        def forbidden(*args, **kwargs):
            raise AssertionError("UNSELECTED_OPERATION")
        class Ambient:
            def __getattr__(self, name):
                raise AssertionError("AMBIENT_RUNTIME")
        with patch.dict(m.__dict__["__builtins__"], open=forbidden, __import__=forbidden), \
             patch.object(m, "hashlib", SimpleNamespace(sha256=forbidden)), \
             patch.object(m, "sys", Ambient()), patch.object(m, "os", Ambient()), \
             patch.object(m, "observe_current_interpreter_records", side_effect=AssertionError("OBSERVE")), \
             patch.object(m, "observe_current_interpreter_scalars", side_effect=AssertionError("OBSERVE")):
            self.accepted()
        self.assertEqual(self.cache, cache_before)
        for name, module in self.cache.items():
            self.assertEqual(module.__dict__, namespaces[name])

    def test_cache_or_module_drift_during_projection_is_not_healed(self):
        original = m._project_scalars
        for change in ("cache", "module"):
            _, _, _, cache = fixture()
            def changed(expected, observed):
                result = original(expected, observed)
                if change == "cache":
                    cache["sys"] = ModuleType("sys")
                else:
                    cache["package"].__file__ = "/synthetic/stdlib/other.py"
                return result
            with patch.object(m, "_project_scalars", changed):
                self.rejected(cache=cache)

    def test_source_bridge_has_no_ambient_runtime_or_execution_calls(self):
        tree = ast.parse(PATH.read_bytes())
        bridge = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                      and node.name == "bind_selected_profile")
        calls = {node.func.id for node in ast.walk(bridge)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertTrue({"open", "eval", "exec", "compile", "__import__", "print", "Popen"}.isdisjoint(calls))
        self.assertFalse(any(isinstance(node, ast.Name) and node.id in ("sys", "os", "hashlib")
                             for node in ast.walk(bridge)))


if __name__ == "__main__":
    unittest.main()
