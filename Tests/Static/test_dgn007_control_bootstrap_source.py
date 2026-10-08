"""Feste synthetische Tests des Kontrollquellenvorschnitts, ohne Worker."""
import ast
import builtins
from dataclasses import FrozenInstanceError
import hashlib
import importlib.util
from importlib.machinery import ExtensionFileLoader, ModuleSpec, SourceFileLoader
import json
from pathlib import Path
import struct
import sys
import sysconfig
import tempfile
from types import FunctionType, ModuleType
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_control_bootstrap_source as subject
import dgn007_pooled_profile_codec as syntax_reference

RAW = b"SYNTHETIC_VALUE = 7\n"
LOCATOR = "/synthetic/control/profile.py"
MAIN_FILE = "/synthetic/control/bootstrap.py"
NAME = subject.CONTROL_NAME
SOABI = "synthetic-cpython-312"
DESTSHARED = "/synthetic/stdlib/lib-dynload"


def _fixture_config_var(name):
    """Fester Code mit getrennten Fake-Sysconfigglobals; kein realer Sysconfigcall."""
    _CALLS.append(name)
    if _CALLBACK is not None:
        _CALLBACK(name)
    if name in _ERRORS:
        raise _ERRORS[name]
    return _VALUES[name]


class Foreign:
    """Fremde Methoden dürfen nicht zur Formprüfung ausgeführt werden."""
    def __getattribute__(self, name):
        raise AssertionError("FOREIGN_GETTER")

    def __eq__(self, other):
        raise AssertionError("FOREIGN_EQUALITY")

    def __repr__(self):
        raise AssertionError("FOREIGN_REPR")

    def __len__(self):
        raise AssertionError("FOREIGN_LENGTH")


class ForeignKey(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        raise AssertionError("FOREIGN_KEY_EQUALITY")


class ForeignModule(ModuleType):
    def __getattribute__(self, name):
        raise AssertionError("FOREIGN_MODULE_GETTER")


class Run:
    """Nur synthetischer Cache; Dateiread ausschließlich aus eigener Fixture."""
    def __init__(self, raw=RAW, actual=None, cache_change=None, spec_change=None,
                 module_change=None, after_exec=None, read_error=None, *, config=False,
                 config_values=None, config_callback=None, config_errors=None,
                 expected_soabi=SOABI, expected_destshared=DESTSHARED):
        self.raw = raw
        self.actual = raw if actual is None else actual
        self.cache_change = cache_change
        self.spec_change = spec_change
        self.module_change = module_change
        self.after_exec = after_exec
        self.read_error = read_error
        self.reads = []
        self.compile_calls = []
        self.compile_codes = []
        self.exec_codes = []
        self.factory_calls = []
        self.config = config
        self.expected_soabi = expected_soabi
        self.expected_destshared = expected_destshared
        self.config_calls = []
        self.main = ModuleType("__main__")
        self.main.__file__ = MAIN_FILE
        self.main_namespace = self.main.__dict__
        self.fake_sys = ModuleType("sys")
        self.cache = {
            "__main__": self.main,
            "_frozen_importlib": sys.modules["_frozen_importlib"],
            "_frozen_importlib_external": sys.modules["_frozen_importlib_external"],
        }
        self.fake_sys.modules = self.cache
        selected_sysconfig = sysconfig
        if config:
            filename = "/synthetic/stdlib/sysconfig.py"
            config_loader = SourceFileLoader("sysconfig", filename)
            config_spec = ModuleSpec("sysconfig", config_loader, origin=filename)
            config_spec._set_fileattr = True
            config_spec._cached = "/synthetic/stdlib/__pycache__/sysconfig.cpython-312.pyc"
            selected_sysconfig = importlib.util.module_from_spec(config_spec)
            namespace = selected_sysconfig.__dict__
            namespace.update(_CALLS=self.config_calls,
                             _VALUES={"SOABI": SOABI, "DESTSHARED": DESTSHARED}
                             if config_values is None else config_values,
                             _CALLBACK=config_callback,
                             _ERRORS={} if config_errors is None else config_errors)
            namespace["get_config_var"] = FunctionType(_fixture_config_var.__code__, namespace,
                                                        "get_config_var")
            self.cache["sysconfig"] = selected_sysconfig
        self.selected_sysconfig = selected_sysconfig
        fake_importlib = ModuleType("importlib")
        util = ModuleType("importlib.util")
        fake_importlib.util = util

        def spec_factory(name, filename, *, loader):
            self.factory_calls.append("SPEC")
            # Gewählte synthetische Linuxmetadaten, keine lokale Factoryattestation:
            # spec_from_file_location würde den Locator unter Windows umformen.
            spec = ModuleSpec(name, loader, origin=filename)
            spec._set_fileattr = True
            spec._cached = "/synthetic/control/__pycache__/profile.cpython-312.pyc"
            if self.spec_change is not None:
                self.spec_change(spec, loader)
            return spec

        def module_factory(spec):
            self.factory_calls.append("MODULE")
            module = importlib.util.module_from_spec(spec)
            # Der synthetische Body muss denselben separat gehaltenen Fakecache benutzen.
            module.__dict__["__builtins__"] = self.custom_builtins
            if self.module_change is not None:
                replacement = self.module_change(module)
                if replacement is not None:
                    module = replacement
            return module

        util.spec_from_file_location = spec_factory
        util.module_from_spec = module_factory
        self.util = util
        selected_imports = {
            "importlib.util": fake_importlib, "sys": self.fake_sys,
            "sysconfig": selected_sysconfig, "json": json, "struct": struct,
        }

        def fixed_import(name, globals=None, locals=None, fromlist=(), level=0):
            if type(name) is not str or level != 0 or name not in selected_imports:
                raise AssertionError("UNSELECTED_IMPORT")
            return selected_imports[name]

        def actual_compile(raw_bytes, filename, mode, *, dont_inherit, optimize):
            self.compile_calls.append((raw_bytes, filename, mode, dont_inherit, optimize))
            code = builtins.compile(raw_bytes, filename, mode,
                                    dont_inherit=dont_inherit, optimize=optimize)
            self.compile_codes.append(code)
            return code

        def actual_exec(code, globals, locals):
            self.exec_codes.append(code)
            builtins.exec(code, globals, locals)
            if self.after_exec is not None:
                self.after_exec(self)

        self.custom_builtins = dict(vars(builtins))
        self.custom_builtins.update(__import__=fixed_import, compile=actual_compile, exec=actual_exec)
        self.main.__dict__["__builtins__"] = self.custom_builtins

    def execute(self, selected=None):
        if selected is not None:
            pass
        elif self.config:
            selected = subject.build_sysconfig_control_bootstrap(
                self.raw, logical_profile=LOCATOR, expected_soabi=self.expected_soabi,
                expected_destshared=self.expected_destshared)
        else:
            selected = subject.build_control_bootstrap(self.raw, logical_profile=LOCATOR)
        absent = object()
        real_profile_before = sys.modules.get(NAME, absent)
        real_main_before = sys.modules["__main__"]
        real_main_name_before = real_main_before.__dict__["__name__"]
        real_sysconfig_before = sys.modules.get("sysconfig", absent)
        with tempfile.TemporaryDirectory(prefix="synthetic-control-") as directory:
            path = Path(directory) / "profile.py"
            pyc = Path(directory) / "profile.pyc"
            path.write_bytes(self.actual)
            pyc.write_bytes(b"SYNTHETIC_UNUSED_PYC")
            owner = self

            class Reader:
                def __enter__(self):
                    self.handle = builtins.open(path, "rb")
                    return self

                def read(self, size):
                    owner.reads.append(size)
                    data = self.handle.read(size)
                    owner.read_object = data
                    return data

                def __exit__(self, *args):
                    self.handle.close()

            def fixture_open(filename, mode):
                if filename != LOCATOR or mode != "rb":
                    raise AssertionError("UNSELECTED_READ")
                if self.read_error is not None:
                    raise self.read_error
                return Reader()

            self.custom_builtins["open"] = fixture_open
            if self.cache_change is not None:
                self.cache_change(self)
            # Ausschließlich erzeugte Kontrollquelle mit fest harmlosen Fixturebytes.
            code = builtins.compile(selected.source, MAIN_FILE, "exec", dont_inherit=True, optimize=0)
            builtins.exec(code, self.main.__dict__, self.main.__dict__)
            self.pyc_after = pyc.read_bytes()
            if (sys.modules.get(NAME, absent) is not real_profile_before
                    or sys.modules.get("__main__") is not real_main_before
                    or sys.modules.get("sysconfig", absent) is not real_sysconfig_before
                    or real_main_before.__dict__.get("__name__") != real_main_name_before):
                raise AssertionError("REAL_CACHE_CHANGED")
        if Path(directory).exists():
            raise AssertionError("OWN_FIXTURE_CLEANUP")
        return self.main_namespace["_CONTROL_RESULT"]


class ControlBootstrapTests(unittest.TestCase):
    def rejected(self, run, issue):
        result = run.execute()
        self.assertEqual(result[:2], ("REJECTED_CONTROL_SOURCE", issue))
        self.assertIsNone(result[2])
        return result

    def generator_rejected(self, raw=RAW, locator=LOCATOR, issue="LOCATOR_FORM"):
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_control_bootstrap(raw, logical_profile=locator)
        error = caught.exception
        self.assertEqual(error.args, (issue,))
        self.assertIsNone(error.__cause__)
        self.assertTrue(error.__suppress_context__)

    def test_generator_is_pure_and_hashes_exact_bytes(self):
        with patch.object(builtins, "open", side_effect=AssertionError("NO_READ")):
            result = subject.build_control_bootstrap(RAW, logical_profile=LOCATOR)
        self.assertEqual(result.profile_sha256, hashlib.sha256(RAW).hexdigest())
        self.assertEqual(result.source_sha256, hashlib.sha256(result.source).hexdigest())
        self.assertEqual(result.source_size, len(result.source))
        self.assertIs(result.profile_raw, RAW)

    def test_frozen_private_result_and_claims(self):
        result = subject.build_control_bootstrap(RAW, logical_profile=LOCATOR)
        self.assertEqual(repr(result), "BootstrapSource(GENERATED_CONTROL_SOURCE_ONLY)")
        with self.assertRaises(FrozenInstanceError):
            result.source = b"replacement"
        self.assertEqual(result.validation_scope, "PROJECT_SEMANTIC")
        self.assertTrue(result.trust_assumed)
        for field in ("trust_attested", "runtime_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(result, field), False)

    def test_foreign_raw_and_locator_never_dispatch(self):
        for value in (Foreign(), bytearray(RAW), None, True):
            self.generator_rejected(raw=value, issue="PROFILE_TYPE")
        for value in (Foreign(), None, True):
            self.generator_rejected(locator=value)

    def test_subclasses_rejected_before_methods(self):
        class Raw(bytes):
            def __repr__(self):
                raise AssertionError("FOREIGN_REPR")
        self.generator_rejected(raw=Raw(RAW), issue="PROFILE_TYPE")
        self.generator_rejected(locator=ForeignKey(LOCATOR))

    def test_locator_lexical_forms_and_utf8_bound(self):
        for locator in ("", "relative.py", "/", "/a/", "/a//b", "/a/../b", "/a/./b",
                        "/a\\b", "/a\0b", "/\ud800", "/" + "x" * 4096, "/" + "é" * 2048):
            with self.subTest(label="LOCATOR_FORM"):
                self.generator_rejected(locator=locator)

    def test_raw_size_and_script_literal_expansion_bounds(self):
        self.generator_rejected(raw=b"", issue="PROFILE_SIZE")
        self.generator_rejected(raw=b"x" * 131073, issue="PROFILE_SIZE")
        self.generator_rejected(raw=b"\0" * 40000, issue="SCRIPT_LIMIT")
        self.generator_rejected(raw=b"x" * 131072, issue="SCRIPT_LIMIT")

    def test_script_cap_exact_and_plus_one(self):
        overhead = len(subject.build_control_bootstrap(b"x", logical_profile=LOCATOR).source) - 1
        raw = b"x" * (131072 - overhead)
        self.assertEqual(len(subject.build_control_bootstrap(raw, logical_profile=LOCATOR).source), 131072)
        self.generator_rejected(raw=raw + b"x", issue="SCRIPT_LIMIT")

    def test_active_caller_exception_is_suppressed(self):
        try:
            raise RuntimeError("SYNTHETIC_PRIVATE_CALLER_PAYLOAD")
        except RuntimeError:
            self.generator_rejected(raw=None, issue="PROFILE_TYPE")

    def test_template_has_exact_five_direct_imports(self):
        result = subject.build_control_bootstrap(RAW, logical_profile=LOCATOR)
        tree = ast.parse(result.source)
        imports = [node.names[0].name for node in ast.walk(tree) if type(node) is ast.Import]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(node) is ast.ImportFrom for node in ast.walk(tree)))
        attributes = {node.attr for node in ast.walk(tree) if type(node) is ast.Attribute}
        self.assertTrue({"get_code", "exec_module", "observe_current_interpreter"}.isdisjoint(attributes))

    def test_literals_hold_raw_crlf_and_quoted_locator(self):
        raw = b"# ' \\ _PROFILE_FILE {}\r\nSYNTHETIC_VALUE=7\r\n"
        locator = "/synthetic/quote'\"é/profile.py"
        tree = ast.parse(subject.build_control_bootstrap(raw, logical_profile=locator).source)
        values = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
                  if type(node) is ast.Assign and type(node.value) is ast.Constant}
        self.assertEqual(values["_EXPECTED_PROFILE_RAW"], raw)
        self.assertEqual(values["_PROFILE_FILE"], locator)

    def test_actual_received_bytes_and_same_compile_code_execute(self):
        run = Run(RAW + b"import sys\nSYNTHETIC_SYS = sys\n")
        status, issue, module = run.execute()
        self.assertEqual((status, issue), ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.assertEqual(module.SYNTHETIC_VALUE, 7)
        self.assertIs(module, run.cache[NAME])
        self.assertIs(module.SYNTHETIC_SYS, run.fake_sys)
        self.assertIs(module.__dict__["__builtins__"], run.custom_builtins)
        self.assertEqual(module.__file__, LOCATOR)
        self.assertEqual(module.__spec__.origin, LOCATOR)
        self.assertEqual(module.__loader__.path, LOCATOR)
        self.assertEqual(module.__cached__, module.__spec__.cached)
        self.assertEqual(run.reads, [131073])
        self.assertIs(run.compile_calls[0][0], run.read_object)
        self.assertEqual(run.compile_calls[0][1:], (LOCATOR, "exec", True, 0))
        self.assertEqual(len(run.exec_codes), 1)
        self.assertIs(run.exec_codes[0], run.compile_codes[0])
        self.assertEqual(run.exec_codes[0].co_filename, LOCATOR)

    def test_crlf_preserved_and_compiler_accepts_bom_and_encoding_cookie(self):
        for raw in (b"SYNTHETIC_VALUE = 7\r\n", b"\xef\xbb\xbfSYNTHETIC_VALUE = 7\n",
                    b"# coding: latin-1\n# \xe9\nSYNTHETIC_VALUE = 7\n"):
            run = Run(raw)
            result = run.execute()
            self.assertEqual(result[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
            self.assertEqual(run.compile_calls[0][0], raw)

    def test_changed_file_rejected_before_spec_or_compile(self):
        run = Run(actual=b"SYNTHETIC_VALUE = 8\n")
        self.rejected(run, "CONTROL_SOURCE_MISMATCH")
        self.assertEqual(run.compile_calls, [])
        self.assertEqual(run.factory_calls, [])
        self.assertNotIn(NAME, run.cache)

    def test_read_sentinel_overflow_before_compile(self):
        run = Run(actual=b"#" * 131074)
        self.rejected(run, "CONTROL_SOURCE_LIMIT")
        self.assertEqual(run.reads, [131073])
        self.assertEqual(len(run.read_object), 131073)
        self.assertEqual(run.compile_calls, [])

    def test_pyc_sidefile_and_loader_code_routes_are_unused(self):
        def block_routes(spec, loader):
            def forbidden(*args, **kwargs):
                raise AssertionError("LOADER_CODE_ROUTE")
            loader.get_code = forbidden
            loader.exec_module = forbidden
        run = Run(spec_change=block_routes)
        result = run.execute()
        self.assertEqual(result[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.assertEqual(run.pyc_after, b"SYNTHETIC_UNUSED_PYC")

    def test_read_error_has_fixed_private_label(self):
        run = Run(read_error=OSError("SYNTHETIC_PRIVATE_FILE_PAYLOAD"))
        self.rejected(run, "CONTROL_READ")
        self.assertEqual(run.compile_calls, [])

    def test_compile_failure_has_no_module_or_complete(self):
        run = Run(b"return\n")
        self.rejected(run, "CONTROL_COMPILE")
        self.assertNotIn(NAME, run.cache)
        self.assertEqual(run.exec_codes, [])

    def test_exec_exception_types_do_not_masquerade_as_read_or_compile(self):
        for exception in ("RuntimeError", "OSError", "SyntaxError", "SystemExit"):
            run = Run(("raise " + exception + "('SYNTHETIC_PRIVATE_PAYLOAD')\n").encode("ascii"))
            self.rejected(run, "CONTROL_EXEC")
            self.assertNotIn(NAME, run.cache)

    def test_existing_cache_entry_preserved_before_read(self):
        foreign = Foreign()
        run = Run(cache_change=lambda owner: owner.cache.__setitem__(NAME, foreign))
        self.rejected(run, "CONTROL_CACHE_PRESENT")
        self.assertIs(run.cache[NAME], foreign)
        self.assertEqual(run.reads, [])

    def test_foreign_cache_key_rejected_before_lookup(self):
        run = Run(cache_change=lambda owner: owner.cache.__setitem__(ForeignKey(NAME), object()))
        self.rejected(run, "CONTROL_CACHE")
        self.assertEqual(run.reads, [])

    def test_cache_key_count_bound_before_read(self):
        def add(owner):
            for index in range(254):
                owner.cache["synthetic_" + str(index)] = None
        run = Run(cache_change=add)
        self.rejected(run, "CONTROL_CACHE")
        self.assertEqual(run.reads, [])

    def test_foreign_namespace_keys_do_not_dispatch(self):
        def mutate(module):
            del module.__dict__["__name__"]
            module.__dict__[ForeignKey("__name__")] = "replacement"
        run = Run(module_change=mutate)
        self.rejected(run, "CONTROL_COHERENCY")
        self.assertNotIn(NAME, run.cache)

    def test_foreign_spec_cached_values_rejected_before_equality(self):
        def mutate(spec, loader):
            spec._cached = Foreign()
        run = Run(spec_change=mutate)
        self.rejected(run, "CONTROL_COHERENCY")

    def test_wrong_module_type_before_getter(self):
        run = Run(module_change=lambda module: Foreign())
        self.rejected(run, "CONTROL_COHERENCY")
        self.assertEqual(run.exec_codes, [])

    def test_pre_exec_module_name_and_package_coherence(self):
        for field, value in (("__name__", "wrong"), ("__file__", "/synthetic/other.py"),
                             ("__package__", "wrong"), ("__spec__", None),
                             ("__loader__", None), ("__path__", [])):
            run = Run(module_change=lambda module, f=field, v=value: setattr(module, f, v))
            self.rejected(run, "CONTROL_COHERENCY")
            self.assertEqual(run.exec_codes, [])

    def test_spec_and_loader_field_changes_rejected(self):
        for field, value in (("name", "wrong"), ("origin", "/synthetic/other.py"),
                             ("submodule_search_locations", []), ("_set_fileattr", False)):
            run = Run(spec_change=lambda spec, loader, f=field, v=value: setattr(spec, f, v))
            self.rejected(run, "CONTROL_COHERENCY")
        run = Run(spec_change=lambda spec, loader: setattr(loader, "path", "/synthetic/other.py"))
        self.rejected(run, "CONTROL_COHERENCY")

    def test_post_exec_metadata_mutation_removes_only_owned_module(self):
        raw = b"import sys\nsys.modules[__name__].__name__ = 'wrong'\n"
        run = Run(raw)
        self.rejected(run, "CONTROL_COHERENCY")
        self.assertNotIn(NAME, run.cache)

    def test_foreign_cache_replacement_preserved_with_cleanup_failure(self):
        raw = b"import sys\nsys.modules[__name__] = type(sys)('synthetic_replacement')\n"
        run = Run(raw)
        self.rejected(run, "CONTROL_CLEANUP")
        self.assertEqual(run.cache[NAME].__name__, "synthetic_replacement")

    def test_changed_cache_container_not_repaired(self):
        run = Run(after_exec=lambda owner: setattr(owner.fake_sys, "modules", {}))
        self.rejected(run, "CONTROL_CLEANUP")
        self.assertEqual(run.fake_sys.modules, {})
        self.assertIn(NAME, run.cache)

    def test_foreign_key_after_exec_blocks_cleanup_lookup(self):
        def mutate(owner):
            del owner.cache[NAME]
            owner.cache[ForeignKey(NAME)] = object()
        run = Run(after_exec=mutate)
        self.rejected(run, "CONTROL_CLEANUP")

    def test_main_class_drift_rejected_before_namespace_getter(self):
        run = Run(after_exec=lambda owner: setattr(owner.main, "__class__", ForeignModule))
        self.rejected(run, "CONTROL_CACHE")
        self.assertNotIn(NAME, run.cache)

    def test_repeat_call_does_not_read_or_reload(self):
        run = Run()
        first = run.execute()
        second = run.main.__dict__["_load_bound_control"]()
        self.assertEqual(second, ("REJECTED_CONTROL_SOURCE", "CONTROL_ALREADY_ATTEMPTED", None))
        self.assertIs(run.cache[NAME], first[2])
        self.assertEqual(run.reads, [131073])
        self.assertEqual(len(run.exec_codes), 1)


class SysconfigBootstrapTests(unittest.TestCase):
    rejected = ControlBootstrapTests.rejected

    def build(self, soabi=SOABI, destshared=DESTSHARED, raw=RAW):
        return subject.build_sysconfig_control_bootstrap(
            raw, logical_profile=LOCATOR, expected_soabi=soabi, expected_destshared=destshared)

    def test_legacy_generated_bytes_remain_exact(self):
        result = subject.build_control_bootstrap(RAW, logical_profile=LOCATOR)
        self.assertEqual(len(result.source), 8101)
        self.assertEqual(result.source_sha256,
                         "6b6307c021e97a5c4949306b5b9ac7f7063a7f31522be70db27c14c6a79956df")
        self.assertEqual(hashlib.sha256(subject._BODY.encode()).hexdigest(),
                         "7fa4b5d58c27c41a9ccd4e05adb51ae36112214d33c7c96d3c7eec7503391029")

    def test_new_generator_pure_private_and_fixed_imports(self):
        with patch.object(builtins, "open", side_effect=AssertionError("NO_READ")):
            result = self.build()
        self.assertEqual(result.source_sha256, hashlib.sha256(result.source).hexdigest())
        self.assertEqual(repr(result), "BootstrapSource(GENERATED_CONTROL_SOURCE_ONLY)")
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(result, key), False)
        tree = ast.parse(result.source)
        self.assertEqual([node.names[0].name for node in ast.walk(tree) if type(node) is ast.Import],
                         ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(node) is ast.ImportFrom for node in ast.walk(tree)))

    def test_expected_forms_before_literal_foreign_operations(self):
        for value in (Foreign(), ForeignKey("synthetic"), None, True, b"text",
                      "x\0y", "\ud800", "é" * 2049):
            for key, label in (("soabi", "SOABI_FORM"), ("destshared", "DESTSHARED_FORM")):
                with self.assertRaises(subject.BootstrapSourceRejected) as caught:
                    self.build(**{key: value})
                self.assertEqual(caught.exception.args, (label,))
                self.assertTrue(caught.exception.__suppress_context__)
        for value in ("", "relative", "/", "/a/", "/a//b", "/a/../b", "/a/./b", "/a\\b"):
            with self.assertRaises(subject.BootstrapSourceRejected) as caught:
                self.build(destshared=value)
            self.assertEqual(caught.exception.args, ("DESTSHARED_FORM",))

    def test_expected_literals_utf8_bounds_and_expansion(self):
        result = self.build(soabi="é" * 2048, destshared="/" + "x" * 4095)
        tree = ast.parse(result.source)
        values = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                  if type(n) is ast.Assign and type(n.value) is ast.Constant}
        self.assertEqual(values["_EXPECTED_SOABI"], "é" * 2048)
        self.assertEqual(values["_EXPECTED_DESTSHARED"], "/" + "x" * 4095)
        self.assertEqual(values["_EXPECTED_PROFILE_RAW"], RAW)
        overhead = len(self.build(raw=b"x").source) - 1
        self.assertEqual(len(self.build(raw=b"x" * (131072 - overhead)).source), 131072)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            self.build(raw=b"x" * (131073 - overhead))
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))

    def test_active_caller_context_suppressed_in_new_api(self):
        try:
            raise RuntimeError("SYNTHETIC_PRIVATE_PAYLOAD")
        except RuntimeError:
            with self.assertRaises(subject.BootstrapSourceRejected) as caught:
                self.build(soabi=None)
        self.assertEqual(caught.exception.args, ("SOABI_FORM",))
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_actual_calls_after_exec_use_only_fake_module(self):
        run = Run(RAW + b"import sys\nSYNTHETIC_SYS = sys\n", config=True)
        seen = []
        def check(name):
            seen.append((name, len(run.exec_codes), run.cache[NAME].SYNTHETIC_VALUE))
        run.selected_sysconfig._CALLBACK = check
        status, issue, module = run.execute()
        self.assertEqual((status, issue), ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.assertEqual(seen, [("SOABI", 1, 7), ("DESTSHARED", 1, 7)])
        self.assertEqual(run.config_calls, ["SOABI", "DESTSHARED"])
        self.assertIs(module.SYNTHETIC_SYS, run.fake_sys)
        self.assertIsNot(run.selected_sysconfig, sysconfig)
        self.assertIs(run.selected_sysconfig.get_config_var.__globals__, run.selected_sysconfig.__dict__)
        self.assertIs(run.exec_codes[0], run.compile_codes[0])

    def test_empty_explicit_soabi_is_value_not_missing(self):
        run = Run(config=True, expected_soabi="", config_values={"SOABI": "", "DESTSHARED": DESTSHARED})
        self.assertEqual(run.execute()[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.rejected(Run(config=True, expected_soabi="",
                          config_values={"SOABI": None, "DESTSHARED": DESTSHARED}),
                      "CONTROL_SYSCONFIG_FORM")

    def test_both_actual_calls_and_forms_precede_mismatch(self):
        for invalid in (None, Foreign(), True, ForeignKey(DESTSHARED), "relative", "\ud800",
                        "/" + "é" * 2048):
            run = Run(config=True, config_values={"SOABI": "wrong", "DESTSHARED": invalid})
            self.rejected(run, "CONTROL_SYSCONFIG_FORM")
            self.assertEqual(run.config_calls, ["SOABI", "DESTSHARED"])
            self.assertNotIn(NAME, run.cache)

    def test_actual_soabi_forms_and_separate_mismatches(self):
        for value in (Foreign(), True, None, b"text", "\0", "\ud800", "x" * 4097):
            run = Run(config=True, config_values={"SOABI": value, "DESTSHARED": DESTSHARED})
            self.rejected(run, "CONTROL_SYSCONFIG_FORM")
            self.assertEqual(run.config_calls, ["SOABI", "DESTSHARED"])
        for values in ({"SOABI": "wrong", "DESTSHARED": DESTSHARED},
                       {"SOABI": SOABI, "DESTSHARED": "/synthetic/other"}):
            run = Run(config=True, config_values=values)
            self.rejected(run, "CONTROL_SYSCONFIG_MISMATCH")
            self.assertNotIn(NAME, run.cache)

    def test_config_call_errors_have_fixed_phase_and_cleanup(self):
        for name in ("SOABI", "DESTSHARED"):
            for error in (OSError("PRIVATE"), SyntaxError("PRIVATE"), RuntimeError("PRIVATE"),
                          SystemExit("PRIVATE"), UnicodeError("PRIVATE")):
                run = Run(config=True, config_errors={name: error})
                self.rejected(run, "CONTROL_SYSCONFIG_CALL")
                self.assertEqual(run.config_calls, ["SOABI"] if name == "SOABI"
                                 else ["SOABI", "DESTSHARED"])
                self.assertNotIn(NAME, run.cache)

    def test_profile_exec_failure_never_initializes_config(self):
        run = Run(b"raise OSError('PRIVATE')\n", config=True)
        self.rejected(run, "CONTROL_EXEC")
        self.assertEqual(run.config_calls, [])
        self.assertNotIn(NAME, run.cache)

    def test_profile_cannot_exchange_held_config_function(self):
        raw = b"import sysconfig\nsysconfig.get_config_var = lambda name: 'wrong'\n"
        run = Run(raw, config=True)
        self.rejected(run, "CONTROL_SYSCONFIG_BINDING")
        self.assertEqual(run.config_calls, [])
        self.assertNotIn(NAME, run.cache)

    def test_config_cache_namespace_and_foreign_callable_pre_exec(self):
        for mutate in (lambda r: r.cache.__setitem__("sysconfig", Foreign()),
                       lambda r: setattr(r.selected_sysconfig, "get_config_var", Foreign()),
                       lambda r: setattr(r.selected_sysconfig, "__name__", Foreign()),
                       lambda r: setattr(r.selected_sysconfig, "__class__", ForeignModule)):
            run = Run(config=True, cache_change=mutate)
            self.rejected(run, "CONTROL_SYSCONFIG_BINDING")
            self.assertEqual(run.exec_codes, [])
            self.assertNotIn(NAME, run.cache)

    def test_config_spec_loader_and_cached_metadata_binding(self):
        for field, value in (("__spec__", None), ("__loader__", None), ("__package__", "wrong")):
            run = Run(config=True)
            setattr(run.selected_sysconfig, field, value)
            self.rejected(run, "CONTROL_SYSCONFIG_BINDING")
        run = Run(config=True)
        run.selected_sysconfig.__loader__.path = "/synthetic/other.py"
        self.rejected(run, "CONTROL_SYSCONFIG_BINDING")
        run = Run(config=True)
        run.selected_sysconfig.__cached__ = Foreign()
        self.rejected(run, "CONTROL_SYSCONFIG_BINDING")

    def test_metadata_unicode_forms_have_same_label_before_and_after_exec(self):
        for field in ("__file__", "__cached__"):
            for stage in ("BEFORE", "SOABI", "DESTSHARED"):
                run = Run(config=True)
                def mutate(name, owner=run, chosen=field, when=stage):
                    if name == when:
                        setattr(owner.selected_sysconfig, chosen, "/synthetic/\ud800")
                        if chosen == "__cached__":
                            owner.selected_sysconfig.__spec__._cached = "/synthetic/\ud800"
                if stage == "BEFORE":
                    mutate("BEFORE")
                else:
                    run.selected_sysconfig._CALLBACK = mutate
                self.rejected(run, "CONTROL_SYSCONFIG_FORM")
                self.assertNotIn(NAME, run.cache)

    def test_config_mutation_after_each_call_stops_without_retry(self):
        for when in ("SOABI", "DESTSHARED"):
            run = Run(config=True)
            def mutate(name, owner=run, selected=when):
                if name == selected:
                    owner.selected_sysconfig.__spec__.origin = "/synthetic/changed.py"
            run.selected_sysconfig._CALLBACK = mutate
            self.rejected(run, "CONTROL_SYSCONFIG_BINDING")
            self.assertEqual(run.config_calls, ["SOABI"] if when == "SOABI"
                             else ["SOABI", "DESTSHARED"])
            self.assertNotIn(NAME, run.cache)

    def test_config_callable_code_mutation_is_not_same_anchor(self):
        run = Run(config=True)
        def alternate(name):
            return "synthetic"
        def mutate(name):
            run.selected_sysconfig.get_config_var.__code__ = alternate.__code__
        run.selected_sysconfig._CALLBACK = mutate
        self.rejected(run, "CONTROL_SYSCONFIG_BINDING")
        self.assertEqual(run.config_calls, ["SOABI"])

    def test_profile_mutation_in_config_call_rejected_before_second(self):
        run = Run(config=True)
        def mutate(name):
            run.cache[NAME].__name__ = "wrong"
        run.selected_sysconfig._CALLBACK = mutate
        self.rejected(run, "CONTROL_COHERENCY")
        self.assertEqual(run.config_calls, ["SOABI"])
        self.assertNotIn(NAME, run.cache)

    def test_cleanup_preserves_foreign_profile_and_config_entries(self):
        run = Run(config=True)
        replacement = ModuleType("synthetic_replacement")
        def mutate(name):
            run.cache[NAME] = replacement
        run.selected_sysconfig._CALLBACK = mutate
        self.rejected(run, "CONTROL_CLEANUP")
        self.assertIs(run.cache[NAME], replacement)
        self.assertIs(run.cache["sysconfig"], run.selected_sysconfig)

    def test_sysconfig_build_cache_is_not_reset_or_repaired(self):
        run = Run(config=True, config_values={"SOABI": "wrong", "DESTSHARED": DESTSHARED})
        marker = object()
        def add(name):
            run.cache["synthetic_buildmodule"] = marker
        run.selected_sysconfig._CALLBACK = add
        self.rejected(run, "CONTROL_SYSCONFIG_MISMATCH")
        self.assertIs(run.cache["synthetic_buildmodule"], marker)
        self.assertIs(run.cache["sysconfig"], run.selected_sysconfig)

    def test_new_route_read_mismatch_prevents_config_calls(self):
        run = Run(config=True, actual=b"SYNTHETIC_VALUE=8\n")
        self.rejected(run, "CONTROL_SOURCE_MISMATCH")
        self.assertEqual(run.config_calls, [])
        self.assertEqual(run.compile_calls, [])


def syntax_fixture(ordinal=1, *, marker="synthetic", locations=()):
    """Benannte vollständige Syntaxwerte; ausdrücklich keine gültige Profilauswahl."""
    files = ({"path": "file-locator", "size": 0, "sha256": "file-hash"},)
    installation = dict(
        assumption="assumption", platform="platform", implementation="implementation",
        version=(3, 12, 14), executable="executable", executable_target="target",
        prefixes=("prefix", "exec-prefix", "base-prefix", "base-exec-prefix"),
        abi="abi", paths=("search-path",), roots=("root-a", "root-b"), inert_zip="",
        flags=(1, 1, 1, 1, 1, 0), finders=("finder-a", "finder-b", "finder-c"),
        hooks=("hook-a", "hook-b"), files=files)
    module = dict(name="cache-key", moduleName="module-name", specName=None,
                  origin="origin", file="module-file", kind="kind", locations=locations,
                  loader="loader", loaderName="loader-name", loaderPath="loader-path",
                  aliasGroup=("alias-a", "alias-b"))
    def descriptors(prefix):
        return tuple(dict(ordinal=n, module=prefix + "module" + str(n),
                          member=prefix + "member" + str(n), size=n,
                          sha256=prefix + "hash" + str(n)) for n in range(1, 10))
    ip = dict(protocol="protocol", commit="input-commit", raw27_binding="input-raw27",
              source_profile="input-profile", nonce="input-nonce", modules=descriptors("I"),
              context_sha256="original-input-digest")
    kr = dict(commit="different-context-commit", raw27_binding="context-raw27",
              source_profile="context-profile", nonce="different-context-nonce",
              modules=descriptors("K"), ordinal=ordinal, entry="context-entry", phase="context-phase")
    wr = dict(ordinal=ordinal, entry="worker-entry", phase=marker,
              installation=installation, controls=("control-a", "control-b"), modules=(module,))
    # Vollständige Namensfeldprojektion, unabhängig vom erzeugten Schemacode.
    d_fields = ("ordinal", "module", "member", "size", "sha256")
    s_fields = ("assumption", "platform", "implementation", "version", "executable",
                "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip",
                "flags", "finders", "hooks", "files")
    p_fields = ("name", "moduleName", "specName", "origin", "file", "kind", "locations",
                "loader", "loaderName", "loaderPath", "aliasGroup")
    sr = tuple(installation[k] if k != "files" else
               tuple(tuple(f[j] for j in ("path", "size", "sha256")) for f in files)
               for k in s_fields)
    pr = tuple(module[k] for k in p_fields)
    ir = tuple(ip[k] if k != "modules" else tuple(tuple(d[j] for j in d_fields) for d in ip[k])
               for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce",
                         "modules", "context_sha256"))
    cr = tuple(kr[k] if k != "modules" else tuple(tuple(d[j] for j in d_fields) for d in kr[k])
               for k in ("commit", "raw27_binding", "source_profile", "nonce", "modules",
                         "ordinal", "entry", "phase"))
    payload = (ir, (wr["ordinal"], wr["entry"], wr["phase"], sr, wr["controls"], (pr,)), cr)
    return payload


def syntax_form(payload):
    """Unabhängige Poolaufnahme aus festen eigenen Tuplefixtures."""
    texts = set()
    def collect(value):
        if type(value) is str:
            texts.add(value)
        elif type(value) is tuple:
            for item in value:
                collect(item)
    collect(payload)
    pool = tuple(sorted(texts))
    def project(value):
        if type(value) is str:
            return pool.index(value)
        if type(value) is tuple:
            return tuple(project(item) for item in value)
        return value
    return ("pooled-binding-design/v1", "METADATA", pool, project(payload))


def syntax_bytes(form):
    return json.dumps(form, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


class InlineMetadataSyntaxTests(unittest.TestCase):
    def setUp(self):
        self.selected = subject.build_inline_syntax_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.decode = self.namespace["_inline_metadata_syntax"]
        self.payload = syntax_fixture()

    def packet(self, body, *, declared_body=0):
        return struct.pack(">8sII", b"DGNC001\0", len(body), declared_body), body

    def accepted(self, payload=None):
        value = self.payload if payload is None else payload
        result = self.decode(*self.packet(syntax_bytes(syntax_form(value))))
        self.assertEqual(result[:2], ("VALID_METADATA_SYNTAX", "NONE"))
        self.assertEqual(result[2], value)
        return result[2]

    def rejected(self, header, body, issue=None):
        result = self.decode(header, body)
        self.assertEqual(result[0], "REJECTED_METADATA_SYNTAX")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        return result

    def test_full_named_field_recovery_three_ordinals(self):
        for ordinal in (1, 2, 3):
            payload = syntax_fixture(ordinal)
            actual = self.accepted(payload)
            self.assertEqual(tuple(map(len, actual)), (7, 6, 8))
            self.assertEqual(len(actual[1][3]), 15)
            self.assertEqual(len(actual[1][5][0]), 11)
            self.assertEqual(len(actual[1][3][-1][0]), 3)
            for descriptor_array in (actual[0][5], actual[2][4]):
                self.assertEqual(len(descriptor_array), 9)
                self.assertTrue(all(len(row) == 5 for row in descriptor_array))
            self.assertNotEqual(actual[0][5], actual[2][4])
            self.assertIsNot(actual[0][5], actual[2][4])

    def test_semantic_contradictions_are_only_syntax_success(self):
        actual = self.accepted()
        self.assertNotEqual(actual[0][1], actual[2][0])
        self.assertNotEqual(actual[0][4], actual[2][3])
        self.assertNotEqual(actual[1][1:3], actual[2][6:8])
        self.assertEqual(actual[0][-1], "original-input-digest")
        self.assertEqual(actual[1][3][4], "executable")  # Kein absoluter Profilocator.
        self.assertIsNone(actual[1][5][0][2])

    def test_literal_integer_zero_null_empty_and_shared_text(self):
        actual = self.accepted(syntax_fixture(marker="", locations=("", "")))
        self.assertEqual(actual[1][3][-1][0][1], 0)
        self.assertIsNone(actual[1][5][0][2])
        self.assertEqual(actual[1][2], "")
        self.assertIs(actual[1][5][0][6][0], actual[1][5][0][6][1])

    def test_unicode_exact_and_no_normalization(self):
        for text in ("é", "e\u0301", "😀", "\x7f", "\b\f\n\r\t\"\\"):
            self.accepted(syntax_fixture(marker=text))
        self.assertNotEqual(syntax_bytes(syntax_form(syntax_fixture(marker="é"))),
                            syntax_bytes(syntax_form(syntax_fixture(marker="e\u0301"))))

    def test_no_body_read_release_or_digest_claim(self):
        body = syntax_bytes(syntax_form(self.payload))
        result = self.decode(*self.packet(body, declared_body=1048576))
        self.assertEqual(result[:2], ("VALID_METADATA_SYNTAX", "NONE"))
        self.assertEqual(self.run.reads, [131073])
        self.assertNotIn("declared_context_match", self.namespace)
        self.assertEqual(self.selected.claim, "GENERATED_CONTROL_SOURCE_ONLY")
        for field in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertIs(getattr(self.selected, field), False)

    def test_header_limits_before_parser_or_payload_methods(self):
        body = syntax_bytes(syntax_form(self.payload))
        with patch.dict(self.namespace, _InlineParser=Foreign()):
            for header in (b"", b"x" * 17, struct.pack(">8sII", b"WRONG000", len(body), 0)):
                self.rejected(header, body, "HEADER_FORM")
            for length in (0, 16369, 0xffffffff):
                self.rejected(struct.pack(">8sII", b"DGNC001\0", length, 0), body, "METADATA_LIMIT")
            self.rejected(struct.pack(">8sII", b"DGNC001\0", len(body), 1048577), body, "BODY_LIMIT")
            self.rejected(struct.pack(">8sII", b"DGNC001\0", len(body) + 1, 0), body, "METADATA_LENGTH")

    def test_exact_bytes_types_before_foreign_dispatch(self):
        header, body = self.packet(syntax_bytes(syntax_form(self.payload)))
        class ByteSubclass(bytes):
            def __len__(self):
                raise AssertionError("FOREIGN_LENGTH")
        for value in (Foreign(), None, True, bytearray(body), memoryview(body), ByteSubclass(body)):
            self.rejected(value, body, "INPUT_TYPE")
            self.rejected(header, value, "INPUT_TYPE")

    def test_json_forbidden_scalar_forms(self):
        for body in (b"true", b"false", b"-1", b"1.0", b"1e0", b"{}", b"[01]", b"[nullx]",
                     b"[1,]", b"", b" [0]", b"[0] ", b"[0][0]"):
            self.rejected(*self.packet(body))

    def test_integer_eight_digits_and_nine_rejected(self):
        parser = self.namespace["_InlineParser"](b"99999999")
        self.assertEqual(parser.value(), 99999999)
        self.rejected(*self.packet(b"100000000"), "INTEGER_LIMIT")

    def test_depth_eight_and_nine_before_schema(self):
        parser = self.namespace["_InlineParser"](b"[" * 8 + b"0" + b"]" * 8)
        parser.value()
        self.assertEqual(parser.pos, 17)
        self.rejected(*self.packet(b"[" * 9 + b"0" + b"]" * 9), "DEPTH_LIMIT")

    def test_node_guard_is_internal_boundary_not_valid_frame_claim(self):
        parser = self.namespace["_InlineParser"](b"0")
        parser.nodes = 16367
        self.assertEqual(parser.value(), 0)
        parser = self.namespace["_InlineParser"](b"0")
        parser.nodes = 16368
        with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
            parser.value()
        self.assertEqual(caught.exception.args, ("NODE_LIMIT",))
        self.assertEqual(parser.pos, 0)

    def test_sequence_256_and_257_before_schema(self):
        body = b"[" + b",".join([b"0"] * 256) + b"]"
        self.assertEqual(len(self.namespace["_InlineParser"](body).value()), 256)
        self.rejected(*self.packet(b"[" + b",".join([b"0"] * 257) + b"]"), "SEQUENCE_LIMIT")

    def test_text_utf8_caps_before_pool(self):
        self.accepted(syntax_fixture(marker="a" * 4096))
        self.rejected(*self.packet(syntax_bytes(syntax_form(syntax_fixture(marker="a" * 4097)))), "TEXT_LIMIT")
        parser = self.namespace["_InlineParser"](syntax_bytes("é" * 2048))
        self.assertEqual(len(parser.value().encode("utf-8")), 4096)
        self.rejected(*self.packet(syntax_bytes("é" * 2049)), "TEXT_LIMIT")

    def test_bad_unicode_and_nul_no_raw_errors(self):
        for body, issue in ((b'"\\ud800"', "JSON_FORM"), (b'"\\udc00"', "JSON_TEXT"),
                            (b'"\\ud800\\u0041"', "JSON_TEXT"), (b'"\\u0000"', "JSON_TEXT"),
                            (b'"\\q"', "JSON_TEXT"), (b'"\\uZZZZ"', "JSON_TEXT"),
                            (b'"\xff"', "JSON_TEXT"), (b'"\x01"', "JSON_TEXT"),
                            (b'"unterminated', "JSON_TEXT")):
            self.rejected(*self.packet(body), issue)

    def test_alternative_escapes_and_whitespace_are_noncanonical(self):
        body = syntax_bytes(syntax_form(self.payload))
        for changed in (body.replace(b"synthetic", b"\\u0073ynthetic", 1),
                        body.replace(b"METADATA", b"\\u004dETADATA", 1)):
            self.rejected(*self.packet(changed), "NONCANONICAL")
        self.rejected(*self.packet(body.replace(b",", b", ", 1)), "JSON_FORM")

    def test_tag_and_role_before_positions(self):
        form = syntax_form(self.payload)
        for index, value, issue in ((0, "wrong-version", "VERSION_MISMATCH"),
                                   (1, "REPORTED", "ROLE_MISMATCH")):
            changed = list(form)
            changed[index] = value
            changed[3] = ()
            self.rejected(*self.packet(syntax_bytes(changed)), issue)

    def test_pool_order_duplicate_unused_and_type(self):
        form = syntax_form(self.payload)
        for pool, issue in ((tuple(reversed(form[2])), "POOL_FORM"),
                            ((form[2][0],) + form[2], "POOL_FORM"),
                            (form[2] + ("zz-unused",), "POOL_UNUSED"), ((0,), "POOL_FORM")):
            self.rejected(*self.packet(syntax_bytes(form[:2] + (pool, form[3]))), issue)

    def test_pool_256_used_and_257_closed(self):
        base = len(syntax_form(self.payload)[2])
        locations = tuple("extra-%03d" % n for n in range(256 - base))
        payload = syntax_fixture(locations=locations)
        self.assertEqual(len(syntax_form(payload)[2]), 256)
        self.accepted(payload)
        self.rejected(*self.packet(syntax_bytes(syntax_form(
            syntax_fixture(locations=locations + ("extra-overflow",))))), "SEQUENCE_LIMIT")

    def test_wrong_text_reference_and_integer_position(self):
        form = syntax_form(self.payload)
        i, w, k = form[3]
        changed = (i, (None,) + w[1:], k)
        self.rejected(*self.packet(syntax_bytes(form[:3] + (changed,))), "POSITION_TYPE")
        changed = ((len(form[2]),) + i[1:], w, k)
        self.rejected(*self.packet(syntax_bytes(form[:3] + (changed,))), "REFERENCE_RANGE")
        changed = ((None,) + i[1:], w, k)
        self.rejected(*self.packet(syntax_bytes(form[:3] + (changed,))), "POSITION_TYPE")

    def test_each_closed_arity_and_both_descriptor_counts(self):
        i, w, k = self.payload
        variants = ((i[:-1], w, k), (i, w[:-1], k), (i, w, k[:-1]),
                    (i[:5] + (i[5][:-1],) + i[6:], w, k),
                    (i, w, k[:4] + (k[4] + (k[4][0],),) + k[5:]),
                    (i, w[:3] + (w[3][:-1],) + w[4:], k),
                    (i, w[:5] + ((w[5][0][:-1],),), k))
        for payload in variants:
            self.rejected(*self.packet(syntax_bytes(syntax_form(payload))), "SCHEMA_FORM")

    def test_late_malformed_has_no_partial_payload(self):
        i, w, k = self.payload
        damaged = k[:-1] + (None,)
        self.rejected(*self.packet(syntax_bytes(syntax_form((i, w, damaged)))), "POSITION_TYPE")

    def test_last_field_ninth_second_descriptor_never_partial(self):
        i, w, k = self.payload
        rows = k[4][:-1] + (k[4][-1][:-1] + (None,),)
        damaged = k[:4] + (rows,) + k[5:]
        self.rejected(*self.packet(syntax_bytes(syntax_form((i, w, damaged)))), "POSITION_TYPE")

    def test_existing_codec_syntax_reference_without_semantics(self):
        with patch.object(syntax_reference, "_semantics", side_effect=AssertionError("NO_SEMANTICS")):
            for ordinal in (1, 2, 3):
                payload = syntax_fixture(ordinal, marker="é😀", locations=("", "shared", "shared"))
                body = syntax_bytes(syntax_form(payload))
                parser = syntax_reference._Parser(body)
                form = parser.value()
                self.assertEqual(parser.pos, len(body))
                expected = syntax_reference._resolve(form, 0)
                actual = self.decode(*self.packet(body))
                self.assertEqual(actual[:2], ("VALID_METADATA_SYNTAX", "NONE"))
                self.assertEqual(actual[2], expected)
                self.assertEqual(actual[2], payload)

    def test_exact_metadata_cap_and_plus_one_before_parser(self):
        # Vier eindeutig verwendete Felder, jedes unter eigenem Textcap.
        def padded(n):
            i, w, k = self.payload
            a, b, c, d = (4000, 4000, 3000, n - 11000)
            i = ("A" * a, "B" * b, "C" * c, "D" * d) + i[4:]
            return syntax_bytes(syntax_form((i, w, k)))
        # Nach dieser festen Umbenennung bleibt die Poolreihenfolge bei Padding gleich.
        # Die unabhängige Stdlibreferenz berücksichtigt auch geänderte Indexbreiten.
        needed = 13000 + 16368 - len(padded(13000))
        body = padded(needed)
        self.assertEqual(len(body), 16368)
        self.assertEqual(self.decode(*self.packet(body))[:2], ("VALID_METADATA_SYNTAX", "NONE"))
        body = padded(needed + 1)
        self.assertEqual(len(body), 16369)
        self.rejected(*self.packet(body), "METADATA_LIMIT")

    def test_syntax_error_labels_hide_payload(self):
        secret = b"SYNTHETIC_PRIVATE_PAYLOAD"
        result = self.rejected(*self.packet(secret), "JSON_FORM")
        self.assertNotIn(secret.decode(), repr(result))
        with patch.dict(self.namespace, _InlineParser=Foreign()):
            result = self.rejected(*self.packet(syntax_bytes(syntax_form(self.payload))), "SYNTAX_INTERNAL")
        self.assertEqual(result, ("REJECTED_METADATA_SYNTAX", "SYNTAX_INTERNAL", None))

    def test_new_generator_imports_closure_and_legacy_golden_bytes(self):
        tree = ast.parse(self.selected.source)
        imports = [n.names[0].name for n in ast.walk(tree) if type(n) is ast.Import]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(n) is ast.ImportFrom for n in ast.walk(tree)))
        names = {n.id for n in ast.walk(tree) if type(n) is ast.Name}
        self.assertTrue({"_semantics", "_comparison", "input", "print"}.isdisjoint(names))
        legacy = subject.build_control_bootstrap(RAW, logical_profile=LOCATOR)
        self.assertEqual(legacy.source_sha256,
                         "6b6307c021e97a5c4949306b5b9ac7f7063a7f31522be70db27c14c6a79956df")
        self.assertEqual(hashlib.sha256(subject._BODY.encode()).hexdigest(),
                         "7fa4b5d58c27c41a9ccd4e05adb51ae36112214d33c7c96d3c7eec7503391029")
        config = subject.build_sysconfig_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(self.selected.source.replace(("\n" + subject._INLINE_SYNTAX).encode(), b"", 1),
                         config.source)

    def test_new_generator_cap_type_privacy_and_no_read(self):
        with patch.object(builtins, "open", side_effect=AssertionError("NO_READ")):
            selected = subject.build_inline_syntax_control_bootstrap(
                RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(selected.source_sha256, hashlib.sha256(selected.source).hexdigest())
        self.assertNotIn(LOCATOR, repr(selected))
        for raw in (Foreign(), bytearray(RAW), None, b"\0" * 40000):
            with self.assertRaises(subject.BootstrapSourceRejected) as caught:
                subject.build_inline_syntax_control_bootstrap(
                    raw, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
            self.assertTrue(caught.exception.__suppress_context__)
        overhead = len(subject.build_inline_syntax_control_bootstrap(
            b"x", logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED).source) - 1
        raw = b"x" * (131072 - overhead)
        selected = subject.build_inline_syntax_control_bootstrap(
            raw, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(selected.source_size, 131072)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_inline_syntax_control_bootstrap(
                raw + b"x", logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))


def semantic_fixture(ordinal=1):
    """Unabhängige benannte Originalmetadata aus ausschließlich eigenen Bytes."""
    rows = tuple(dict(ordinal=n, module=module, member=member, size=len(raw),
                      sha256=hashlib.sha256(raw).hexdigest())
                 for n, (module, member) in enumerate(syntax_reference.b.input82.MODULES)
                 for raw in (b"synthetic-source-" + str(n).encode("ascii"),))
    original = dict(protocol="dgn007-import-input/v1", commit="1" * 40,
                    raw27_binding="2" * 64, source_profile="dgn007-docker-sql-only/v1",
                    nonce="3" * 64, modules=list(rows))
    digest = hashlib.sha256(json.dumps(original, sort_keys=True, ensure_ascii=True,
                            separators=(",", ":"), allow_nan=False).encode("ascii")).hexdigest()
    descriptors = tuple(tuple(row[k] for k in ("ordinal", "module", "member", "size", "sha256"))
                        for row in rows)
    ip = tuple(original[k] for k in ("protocol", "commit", "raw27_binding", "source_profile", "nonce")) + (descriptors, digest)
    installation = ("DECLARED_SETUP_PYTHON_CONTROL_RUNTIME", "linux", "cpython", (3, 12, 14),
                    "/synthetic/bin/python", "/synthetic/bin/python", ("/synthetic",) * 4,
                    SOABI, ("/synthetic/stdlib", "/synthetic/stdlib/lib-dynload", "/synthetic/python312.zip"),
                    ("/synthetic/stdlib", "/synthetic/stdlib/lib-dynload"), "/synthetic/python312.zip",
                    (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"), ("ZIPIMPORTER", "FILEFINDER"),
                    (("/synthetic/bin/python", 0, "4" * 64),))
    modules = (("__main__", "__main__", None, "", MAIN_FILE, "CONTROL", (), "NONE", "", "", ()),
               (NAME, NAME, NAME, LOCATOR, LOCATOR, "CONTROL", (), "SOURCE", NAME, LOCATOR, ()),
               ("sys", "sys", "sys", "built-in", "", "BUILTIN", (), "BUILTIN", "", "", ()))
    entry = ("run_dgn007_automated_setup", "docker_sqlcmd_proxy", "run_demo")[ordinal - 1]
    worker = (ordinal, entry, "PRE_IMPORT", installation, ("__main__", NAME), modules)
    context = ip[1:5] + (descriptors, ordinal, entry, "PRE_IMPORT")
    return (ip, worker, context)


def semantic_change(payload, path, value):
    """Gehaltene synthetische Tupleänderung ohne JSON-/Semantikdefault."""
    if not path:
        return value
    rows = list(payload)
    rows[path[0]] = semantic_change(rows[path[0]], path[1:], value)
    return tuple(rows)


def _fixture_sha256():
    """Fester Constructorcode mit getrenntem synthetischem Providernamespace."""
    global _HASH_CALLS
    _HASH_CALLS += 1
    if _HASH_CALLBACK is not None:
        _HASH_CALLBACK()
    if _HASH_ERROR is not None:
        raise _HASH_ERROR
    if _HASH_RESULT is not None:
        return _HASH_RESULT
    return _NATIVE_SHA()


class InlineMetadataSemanticsTests(unittest.TestCase):
    def setUp(self):
        loader = SourceFileLoader("hashlib", "/synthetic/stdlib/hashlib.py")
        spec = ModuleSpec("hashlib", loader, origin="/synthetic/stdlib/hashlib.py")
        spec._set_fileattr = True
        spec._cached = "/synthetic/stdlib/__pycache__/hashlib.cpython-312.pyc"
        self.provider = importlib.util.module_from_spec(spec)
        native_file = "/synthetic/stdlib/lib-dynload/_hashlib.so"
        native_loader = ExtensionFileLoader("_hashlib", native_file)
        native_spec = ModuleSpec("_hashlib", native_loader, origin=native_file)
        native_spec._set_fileattr = True
        self.native = ModuleType("_hashlib")
        # Nur synthetische Metadaten: module_from_spec würde eine Extension laden.
        self.native.__dict__.update(__file__=native_file, __package__="", __spec__=native_spec,
                                    __loader__=native_loader, __cached__=None,
                                    HASH=hashlib.__dict__["_hashlib"].HASH,
                                    openssl_sha256=hashlib.sha256)
        self.provider.__dict__.update(
            _hashlib=self.native, _NATIVE_SHA=hashlib.sha256,
            _HASH_CALLS=0, _HASH_CALLBACK=None, _HASH_ERROR=None, _HASH_RESULT=None)
        self.factory = FunctionType(_fixture_sha256.__code__, self.provider.__dict__, "sha256")
        self.provider.sha256 = self.factory

        def bind_provider(run):
            profile = run.cache[NAME]
            profile.hashlib = self.provider
            profile.ExtensionFileLoader = ExtensionFileLoader
            run.cache["hashlib"] = self.provider
            run.cache["_hashlib"] = self.native

        self.selected = subject.build_inline_semantics_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True, after_exec=bind_provider)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.decode = self.namespace["_inline_metadata_semantics"]
        self.payload = semantic_fixture()

    def packet(self, payload, *, body_size=None):
        metadata = syntax_bytes(syntax_form(payload))
        declared = sum(row[3] for row in payload[0][5]) if body_size is None else body_size
        return struct.pack(">8sII", b"DGNC001\0", len(metadata), declared), metadata

    def accepted(self, payload=None):
        payload = self.payload if payload is None else payload
        result = self.decode(*self.packet(payload))
        self.assertEqual(result[:2], ("VALID_METADATA_SEMANTICS", "NONE"))
        self.assertEqual(result[2], payload)
        return result[2]

    def rejected(self, payload=None, issue=None, *, body_size=None):
        payload = self.payload if payload is None else payload
        result = self.decode(*self.packet(payload, body_size=body_size))
        self.assertEqual(result[0], "REJECTED_METADATA_SEMANTICS")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_full_semantics_all_ordinals_matches_actual_codec(self):
        for ordinal in (1, 2, 3):
            payload = semantic_fixture(ordinal)
            actual = self.accepted(payload)
            reference = syntax_reference._semantics(payload, 0)
            self.assertEqual(actual[0], reference[0])
            worker, context = reference[1:]
            self.assertEqual(actual[1][:3], (worker.ordinal, worker.entry, worker.phase))
            self.assertEqual(actual[1][3], tuple(getattr(worker.installation, key)
                if key != "files" else tuple((r.path, r.size, r.sha256) for r in worker.installation.files)
                for key in ("assumption", "platform", "implementation", "version", "executable",
                            "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip",
                            "flags", "finders", "hooks", "files")))
            self.assertEqual(actual[1][4], worker.controls)
            self.assertEqual(actual[1][5], tuple(tuple(getattr(r, key) for key in (
                "name", "moduleName", "specName", "origin", "file", "kind", "locations",
                "loader", "loaderName", "loaderPath", "aliasGroup")) for r in worker.modules))
            self.assertEqual(actual[2][:4], (context.commit, context.raw27_binding,
                                           context.source_profile, context.nonce.hex()))
            self.assertEqual(actual[2][4], tuple((r.ordinal, r.module, r.member, r.size, r.sha256)
                                               for r in context.modules))
            self.assertEqual(actual[2][5:], (context.ordinal, context.entry, context.phase))

    def test_original_named_digest_preimage_has_no_ordinal_or_pool(self):
        seen = []
        encoder = json.JSONEncoder
        class RecordingEncoder(encoder):
            def iterencode(self, value, *args, **kwargs):
                if type(value) is dict:
                    seen.append(value)
                return super().iterencode(value, *args, **kwargs)
        with patch.object(json, "JSONEncoder", RecordingEncoder):
            self.accepted()
        self.assertEqual(len(seen), 1)
        self.assertEqual(set(seen[0]), {"protocol", "commit", "raw27_binding", "source_profile", "nonce", "modules"})
        self.assertIs(type(seen[0]["modules"]), list)
        self.assertTrue(all(set(r) == {"ordinal", "module", "member", "size", "sha256"} for r in seen[0]["modules"]))
        digest = hashlib.sha256(json.dumps(seen[0], sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False).encode("ascii")).hexdigest()
        self.assertEqual(digest, self.payload[0][6])

    def test_original_mapping_constants_match_current_source_contract(self):
        self.assertEqual(self.namespace["_SEMANTIC_MODULES"], syntax_reference.b.input82.MODULES)
        self.assertEqual(self.namespace["_SEMANTIC_ENTRIES"], syntax_reference.b.ENTRIES)
        self.assertEqual(self.namespace["_SEMANTIC_FROZEN"], syntax_reference.b.FROZEN_NAMES)
        self.assertEqual(self.namespace["_SEMANTIC_PAIRS"], syntax_reference.b.ALIAS_PAIRS)

    def test_semantics_rejects_previous_syntax_only_contradictions(self):
        self.rejected(syntax_fixture(), "CONTEXT_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_installation_policy_fields_and_lexical_paths(self):
        for index, value, issue in (
            (0, "wrong", "INSTALLATION_FORM"), (1, "win32", "INSTALLATION_FORM"),
            (2, "other", "INSTALLATION_FORM"), (3, (3, 13, 0), "INSTALLATION_FORM"),
            (3, (3, 12, 1000), "INSTALLATION_FORM"), (7, "", "INSTALLATION_FORM"),
            (9, ("/same", "/same"), "INSTALLATION_FORM"),
            (8, ("/foreign",), "PATH_FORM"), (4, "relative", "PATH_FORM"),
            (5, "/synthetic/../escape", "PATH_FORM"), (10, "/double//slash", "PATH_FORM"),
            (11, (1, 1, 1, 1, 1, 1), "INSTALLATION_FORM"),
            (12, ("BUILTIN", "FROZEN", "OTHER"), "INSTALLATION_FORM"),
            (13, ("ZIPIMPORTER", "OTHER"), "INSTALLATION_FORM")):
            self.rejected(semantic_change(self.payload, (1, 3, index), value), issue)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_file_forms_optional_selection_and_bounds(self):
        self.accepted(semantic_change(self.payload, (1, 3, 14), ()))
        first = self.payload[1][3][14][0]
        self.accepted(semantic_change(self.payload, (1, 3, 14), (first, ("/synthetic/stdlib/file", 0, "4" * 64))))
        for files in ((first, first), (("/other", 0, "4" * 64),),
                      (first, ("/foreign/file", 0, "4" * 64)),
                      ((first[0], 33554433, first[2]),), (first,) * 3):
            self.rejected(semantic_change(self.payload, (1, 3, 14), files), "FILE_FORM")

    def test_source_extension_loader_root_and_locations(self):
        for kind in ("SOURCE", "EXTENSION"):
            row = ("synthetic", "synthetic", "synthetic", "/synthetic/stdlib/x", "/synthetic/stdlib/x",
                   kind, ("/synthetic/stdlib/pkg",), kind, "synthetic", "/synthetic/stdlib/x", ())
            payload = semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (row,))))
            self.accepted(payload)
            for index, value, issue in ((3, "/foreign/x", "MODULE_FORM"), (8, "other", "MODULE_FORM"),
                                        (9, "/other", "MODULE_FORM"), (6, ("/foreign",), "PATH_FORM")):
                changed = list(row)
                changed[index] = value
                self.rejected(semantic_change(self.payload, (1, 5), tuple(sorted(
                    self.payload[1][5] + (tuple(changed),)))), issue)
            outside = tuple("/foreign/x" if n in (3, 4, 9) else value for n, value in enumerate(row))
            self.rejected(semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (outside,)))), "PATH_FORM")

    def test_builtin_frozen_nullspec_and_metadata_rules(self):
        for index, value in ((1, "other"), (2, None), (3, "foreign"), (5, "other"),
                             (7, "SOURCE"), (8, "not-empty"), (9, "not-empty")):
            self.rejected(semantic_change(self.payload, (1, 5, 2, index), value), "MODULE_FORM")
        self.rejected(semantic_change(self.payload, (1, 5, 0, 3), "/nonempty"), "MODULE_FORM")
        self.rejected(semantic_change(self.payload, (1, 5, 0, 6), ("relative",)), "PATH_FORM")
        row = ("os.path", "posixpath", "posixpath", "frozen", "/synthetic/stdlib/posixpath.py", "FROZEN",
               (), "FROZEN", "", "", ())
        self.accepted(semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (row,)))))
        self.rejected(semantic_change(self.payload, (1, 5, 2, 4), "relative"), "PATH_FORM")

    def test_inventory_order_duplicates_ownnames_and_generic_controls(self):
        self.rejected(semantic_change(self.payload, (1, 5), ()), "INVENTORY_FORM")
        self.rejected(semantic_change(self.payload, (1, 5), self.payload[1][5][::-1]), "INVENTORY_FORM")
        self.rejected(semantic_change(self.payload, (1, 5), self.payload[1][5] + (self.payload[1][5][-1],)), "INVENTORY_FORM")
        for name in self.namespace["_SEMANTIC_OWN"]:
            self.rejected(semantic_change(self.payload, (1, 5, 2, 0), name), "OWN_MODULE_CACHED")
        self.rejected(semantic_change(self.payload, (1, 4), ("__main__",)), "CONTROL_FORM")
        self.rejected(semantic_change(self.payload, (1, 4), ("__main__", "__main__")), "CONTROL_FORM")
        extra = ("selected_control", "selected_control", None, "", "", "CONTROL", (), "NONE", "", "", ())
        payload = semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (extra,))))
        self.accepted(semantic_change(payload, (1, 4), payload[1][4] + ("selected_control",)))

    def test_all_frozen_pairs_singleton_empty_and_mixed_source(self):
        for pair in self.namespace["_SEMANTIC_PAIRS"]:
            rows = []
            for name in pair:
                names = self.namespace["_SEMANTIC_FROZEN"].get(name, (name, name))
                rows.append((name, *names, "frozen", "", "FROZEN", (), "FROZEN", "", "", pair))
            self.accepted(semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + tuple(rows)))))
            missing = self.payload[1][5] + (rows[0],)
            self.rejected(semantic_change(self.payload, (1, 5), tuple(sorted(missing))), "ALIAS_FORM")
            single = rows[0][:-1] + ((),)
            self.accepted(semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (single,)))))
            different = rows[1][:-1] + ((),)
            self.rejected(semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (rows[0], different)))), "ALIAS_FORM")
        frozen = ("_collections_abc", "collections.abc", "_collections_abc", "frozen", "", "FROZEN", (), "FROZEN", "", "", ())
        source = ("collections.abc", "collections.abc", "collections.abc", "/synthetic/stdlib/collections/abc.py",
                  "/synthetic/stdlib/collections/abc.py", "SOURCE", (), "SOURCE", "collections.abc",
                  "/synthetic/stdlib/collections/abc.py", ())
        self.accepted(semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + (frozen, source)))))

    def test_each_descriptor_mapping_size_hash_and_late_cell(self):
        for prefix in ((0, 5), (2, 4)):
            for field, value in ((0, 8), (1, "wrong"), (2, "wrong"), (3, 131073), (4, "z" * 64)):
                self.rejected(semantic_change(self.payload, prefix + (0, field), value), "CONTEXT_FORM")
            self.rejected(semantic_change(self.payload, prefix + (8, 4), "BAD"), "CONTEXT_FORM")
            oversized = tuple(row[:3] + (131072, row[4]) for row in self.payload[0][5])
            self.rejected(semantic_change(self.payload, prefix, oversized), "CONTEXT_FORM",
                          body_size=sum(row[3] for row in self.payload[0][5]))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_context_texts_nonce_protocol_hex_forms(self):
        for path, value in (((0, 0), "wrong"), ((0, 1), "a" * 39), ((0, 2), "A" * 64),
                            ((0, 3), "wrong"), ((0, 4), "3" * 63), ((0, 6), "g" * 64),
                            ((2, 0), "wrong"), ((2, 1), "g" * 64), ((2, 2), "wrong"), ((2, 3), "wrong")):
            self.rejected(semantic_change(self.payload, path, value), "CONTEXT_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_selector_forms_and_valid_selector_mismatch(self):
        for path, value in (((1, 0), 0), ((1, 1), "wrong"), ((1, 2), "POST_IMPORT"),
                            ((2, 5), 4), ((2, 6), "wrong"), ((2, 7), "POST_IMPORT")):
            self.rejected(semantic_change(self.payload, path, value), "CONTEXT_FORM")
        payload = semantic_change(self.payload, (2,), self.payload[2][:5] + semantic_fixture(2)[2][5:])
        self.rejected(payload, "CONTEXT_MISMATCH")

    def test_declared_body_sum_before_provider_and_no_body_claim(self):
        self.rejected(issue="DECLARED_BODY_LENGTH", body_size=0)
        self.assertEqual(self.provider._HASH_CALLS, 0)
        self.accepted()  # Bodies are absent; accepted SHA/size fields are declarations only.

    def test_valid_digest_context_mismatch_and_opaque_hashes(self):
        self.rejected(semantic_change(self.payload, (0, 6), "0" * 64), "INPUT_DIGEST")
        for path in ((2, 0), (2, 1), (2, 3), (2, 4, 8, 4)):
            old = self.payload
            for position in path:
                old = old[position]
            self.rejected(semantic_change(self.payload, path, "a" * len(old)), "INPUT_BINDING")
        # Declared hashes are not recomputed from bodies by this API.
        payload = semantic_change(self.payload, (2, 4, 8, 4), "0" * 64)
        payload = semantic_change(payload, (0, 5, 8, 4), "0" * 64)
        ip = payload[0]
        value = dict(zip(("protocol", "commit", "raw27_binding", "source_profile", "nonce"), ip[:5]))
        value["modules"] = [dict(zip(("ordinal", "module", "member", "size", "sha256"), r)) for r in ip[5]]
        digest = hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")).hexdigest()
        self.accepted(semantic_change(payload, (0, 6), digest))

    def test_late_form_failure_dominates_early_binding_and_digest(self):
        changed = semantic_change(self.payload, (0, 6), "0" * 64)
        self.rejected(semantic_change(changed, (2, 4, 8, 4), "BAD"), "CONTEXT_FORM")
        self.rejected(semantic_change(changed, (1, 5, 2, 7), "NONE"), "MODULE_FORM")
        malformed = semantic_change(changed, (2, 4, 8, 4), None)
        self.rejected(malformed, "POSITION_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_wrong_header_and_foreign_bytes_precede_provider(self):
        header, metadata = self.packet(self.payload)
        for a, b in ((Foreign(), metadata), (header, Foreign()), (b"", metadata)):
            result = self.decode(a, b)
            self.assertEqual(result[0], "REJECTED_METADATA_SEMANTICS")
            self.assertIsNone(result[2])
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_missing_bound_profile_and_provider_foreign_fields(self):
        original = self.namespace["_SEMANTIC_CONTROL_ANCHOR"]
        for value in (None, Foreign(), ()):
            self.namespace["_SEMANTIC_CONTROL_ANCHOR"] = value
            self.rejected(issue="HASH_PROVIDER_BINDING")
        self.namespace["_SEMANTIC_CONTROL_ANCHOR"] = original
        profile = self.run.cache[NAME]
        for value in (None, Foreign(), ForeignModule("hashlib")):
            profile.hashlib = value
            self.rejected(issue="HASH_PROVIDER_BINDING")
        profile.hashlib = self.provider
        self.provider.__dict__[ForeignKey("foreign-key")] = Foreign()
        self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_provider_metadata_spec_loader_and_callable_drift(self):
        for target, key, value in (
            (self.provider.__dict__, "__name__", Foreign()),
            (self.provider.__dict__, "__spec__", Foreign()),
            (self.provider.__spec__.__dict__, "origin", Foreign()),
            (self.provider.__loader__.__dict__, "path", Foreign()),
            (self.provider.__dict__, "sha256", Foreign()),
            (self.provider.__dict__, "_hashlib", Foreign())):
            old = target[key]
            target[key] = value
            self.rejected(issue="HASH_PROVIDER_BINDING")
            target[key] = old
        old = self.factory.__defaults__
        self.factory.__defaults__ = (None,)
        self.rejected(issue="HASH_PROVIDER_BINDING")
        self.factory.__defaults__ = old

    def test_native_constructor_supported_and_result_exact_type(self):
        self.provider.sha256 = hashlib.sha256
        self.accepted()
        self.provider.sha256 = self.factory
        for value in (Foreign(), ForeignModule("HASH"), object()):
            self.provider._HASH_RESULT = value
            self.rejected(issue="HASH_PROVIDER_OBJECT")

    def test_constructor_failure_fixed_and_post_drift_dominant(self):
        self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.rejected(issue="HASH_PROVIDER_CALL")
        self.provider._HASH_CALLBACK = lambda: self.run.cache.__setitem__("hashlib", Foreign())
        self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_provider_code_and_cache_drift_during_constructor(self):
        old = self.factory.__code__
        self.provider._HASH_CALLBACK = lambda: setattr(self.factory, "__code__", _fixture_config_var.__code__)
        self.rejected(issue="HASH_PROVIDER_BINDING")
        self.factory.__code__ = old
        self.provider._HASH_CALLBACK = lambda: self.run.cache.__setitem__(NAME, ModuleType(NAME))
        self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_native_class_and_method_descriptor_exchange_is_closed(self):
        held = self.native.HASH
        # Ein gleich beschrifteter Python-Typ erhält keine native Methodenbindung.
        for update in (Foreign(), property(lambda obj: self.fail("FOREIGN_METHOD_GETTER")),
                       held.__dict__["update"]):
            replacement = type("HASH", (), {"__module__": "_hashlib", "update": update,
                                            "hexdigest": held.__dict__["hexdigest"]})
            self.native.HASH = replacement
            self.rejected(issue="HASH_PROVIDER_BINDING")
        self.native.HASH = held
        contaminated = type("HASH", (), {"__module__": "_hashlib", "update": held.__dict__["update"],
                                         "hexdigest": held.__dict__["hexdigest"],
                                         ForeignKey("foreign-key"): None})
        self.native.HASH = contaminated
        self.rejected(issue="HASH_PROVIDER_BINDING")
        oversized = type("HASH", (), {"field" + str(n): None for n in range(257)})
        self.native.HASH = oversized
        self.rejected(issue="HASH_PROVIDER_BINDING")
        self.native.HASH = held
        self.provider._HASH_CALLBACK = lambda: setattr(self.native, "HASH", Foreign())
        self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_hash_update_error_and_profile_mutation_during_encoding(self):
        encoder = json.JSONEncoder
        class BrokenEncoder(encoder):
            def iterencode(self, value, *args, **kwargs):
                if type(value) is dict:
                    yield "x"
                    raise ValueError("PRIVATE_PAYLOAD")
                yield from super().iterencode(value, *args, **kwargs)
        with patch.object(json, "JSONEncoder", BrokenEncoder):
            self.rejected(issue="HASH_PROVIDER_CALL")
        class ChangedEncoder(encoder):
            def iterencode(inner, value, *args, **kwargs):
                if type(value) is dict:
                    self.run.cache[NAME].__name__ = "wrong"
                yield from super().iterencode(value, *args, **kwargs)
        with patch.object(json, "JSONEncoder", ChangedEncoder):
            self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_cleanup_never_repairs_foreign_provider_or_cache(self):
        replacement = ModuleType("hashlib")
        self.run.cache["hashlib"] = replacement
        self.rejected(issue="HASH_PROVIDER_BINDING")
        self.assertIs(self.run.cache["hashlib"], replacement)
        self.assertIs(self.run.cache[NAME], self.namespace["_CONTROL_RESULT"][2])

    def test_no_actual_provider_call_before_shapes_or_under_caller_exception(self):
        try:
            raise RuntimeError("PRIVATE_PAYLOAD")
        except RuntimeError:
            result = self.rejected(semantic_change(self.payload, (1, 3, 1), "wrong"), "INSTALLATION_FORM")
        self.assertEqual(result, ("REJECTED_METADATA_SEMANTICS", "INSTALLATION_FORM", None))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_additive_route_legacy_bytes_imports_and_private_claim(self):
        old = subject.build_inline_syntax_control_bootstrap(RAW, logical_profile=LOCATOR,
                                                           expected_soabi=SOABI, expected_destshared=DESTSHARED)
        rebuilt = self.selected.source.decode("utf-8").replace("\n" + subject._INLINE_SEMANTICS + "\n", "\n", 1)
        rebuilt = rebuilt.replace("global _CONTROL_ATTEMPTED, _SEMANTIC_CONTROL_ANCHOR", "global _CONTROL_ATTEMPTED", 1)
        rebuilt = rebuilt.replace("    _SEMANTIC_CONTROL_ANCHOR = coherence\n", "", 1)
        self.assertEqual(rebuilt.encode("utf-8"), old.source)
        tree = ast.parse(self.selected.source)
        imports = [n.names[0].name for n in tree.body if type(n) is ast.Import]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(n) is ast.ImportFrom for n in tree.body))
        self.assertEqual(self.selected.claim, "GENERATED_CONTROL_SOURCE_ONLY")
        self.assertFalse(self.selected.runtime_attested)
        self.assertFalse(self.selected.trust_attested)
        self.assertFalse(self.selected.import_used_bytes_attested)

    def test_semantics_generator_script_cap_and_rejection_privacy(self):
        base = subject.build_inline_semantics_control_bootstrap(b"x", logical_profile=LOCATOR,
                         expected_soabi=SOABI, expected_destshared=DESTSHARED)
        overhead = len(base.source) - 1
        raw = b"x" * (subject.MAX_SCRIPT_BYTES - overhead)
        selected = subject.build_inline_semantics_control_bootstrap(raw, logical_profile=LOCATOR,
                            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(len(selected.source), subject.MAX_SCRIPT_BYTES)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_inline_semantics_control_bootstrap(raw + b"x", logical_profile=LOCATOR,
                            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))
        for field in ("profile_raw", "logical_profile", "expected_soabi", "expected_destshared"):
            fields = dict(profile_raw=RAW, logical_profile=LOCATOR, expected_soabi=SOABI,
                          expected_destshared=DESTSHARED)
            fields[field] = Foreign()
            with self.assertRaises(subject.BootstrapSourceRejected):
                subject.build_inline_semantics_control_bootstrap(**fields)


if __name__ == "__main__":
    unittest.main()
