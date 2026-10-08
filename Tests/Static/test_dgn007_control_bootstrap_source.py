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


def reporter_scalars(payload):
    """Gegebene Scalar3-Fixture; unabhängige benannte Feldzuordnung."""
    names = ("assumption", "platform", "implementation", "version", "exe", "target", "prefixes",
             "abi", "paths", "roots", "inert", "flags", "finders", "hooks", "files")
    fields = dict(zip(names, payload[1][3]))
    selection = tuple(fields[k] for k in ("assumption", "roots", "inert")) + (payload[1][4],)
    installation = tuple(fields[k] for k in ("platform", "implementation", "version", "exe", "target",
                          "prefixes", "abi", "flags", "paths", "finders", "hooks", "files"))
    return (selection, installation, payload[1][5])


def reporter_reference(payload, scalars):
    """Eigene benannte Referenz, ohne Produktionsprojektion oder M-Sollfallback."""
    selection = dict(zip(("assumption", "roots", "inert", "controls"), scalars[0]))
    values = dict(zip(("platform", "implementation", "version", "exe", "target", "prefixes", "abi",
                      "flags", "paths", "finders", "hooks", "files"), scalars[1]))
    values.update(selection)
    installation = tuple(values[k] for k in ("assumption", "platform", "implementation", "version",
        "exe", "target", "prefixes", "abi", "paths", "roots", "inert", "flags", "finders", "hooks", "files"))
    reported = (payload[2], installation, selection["controls"], scalars[2])
    _, _, pool, positions = syntax_form(reported)
    form = ("pooled-binding-design/v1", "REPORTED", pool, positions)
    return reported, form, syntax_bytes(form)


def reporter_reassemble(records):
    """Testreferenz für vollständige Records, kein produktiver Receiver."""
    begin, end = json.loads(records[0]), json.loads(records[-1])
    assert begin[0] == "PROFILE_BEGIN" and end[0] == "PROFILE_END"
    assert begin[1:] == end[1:4] and len(records) == begin[3] + 2
    parts = []
    for sequence, record in enumerate(records[1:-1], 1):
        fields = record[:-1].split(b"|", 4)
        assert record.endswith(b"\n") and len(record) <= 1024
        assert fields[:4] == [b"P", str(begin[1]).encode(), str(sequence).encode(), str(begin[3]).encode()]
        assert 0 < len(fields[4]) <= 896
        assert sequence == begin[3] or len(fields[4]) == 896
        parts.append(fields[4])
    data = b"".join(parts)
    assert len(data) == begin[2] and hashlib.sha256(data).hexdigest() == end[4]
    return data


def _fixture_report_encoder_init(instance, **kwargs):
    """Feste synthetische Dispatchmutation, nur mit getrennt eingesetzten Globals."""
    _REPORT_HELD_INIT(instance, **kwargs)
    _REPORT_ENCODER_CLASS.synthetic_dispatch = 1


def _fixture_report_encoder_iterencode(instance, value):
    global _REPORT_ITER_CALLED
    _REPORT_ITER_CALLED += 1
    return _REPORT_HELD_ITER(instance, value)


def _fixture_report_encoder_exchange_provider(instance, value):
    _REPORT_FACTORY.__code__ = _REPORT_REPLACEMENT_CODE
    return _REPORT_HELD_ITER(instance, value)


def _fixture_report_encoder_instance_shadow(instance, **kwargs):
    _REPORT_HELD_INIT(instance, **kwargs)
    instance.iterencode = _REPORT_SHADOW


def _fixture_report_encoder_instance_setting(instance, **kwargs):
    _REPORT_HELD_INIT(instance, **kwargs)
    instance.ensure_ascii = False


_REPORT_OMITTED = object()


class InlineProfileReporterTests(unittest.TestCase):
    def setUp(self):
        self.real_cache = sys.modules
        self.real_names = (NAME, "__main__", "sysconfig", "json", "json.encoder", "_hashlib")
        self.real_values = tuple(sys.modules.get(name, _REPORT_OMITTED) for name in self.real_names)
        self.real_main_name = sys.modules["__main__"].__name__
        self.real_encoder = json.JSONEncoder
        self.real_encoder_namespace = tuple(sorted(self.real_encoder.__dict__.items()))
        self.real_json_namespace = tuple(sorted(json.__dict__.items()))
        self.real_encoder_module = sys.modules["json.encoder"]
        self.real_encoder_module_namespace = tuple(sorted(self.real_encoder_module.__dict__.items()))
        self.real_encoder_functions = tuple(self.real_encoder.__dict__[k] for k in ("__init__", "iterencode", "default"))
        self.real_encoder_states = tuple((fn.__code__, fn.__defaults__, fn.__kwdefaults__,
            None if fn.__kwdefaults__ is None else tuple(sorted(fn.__kwdefaults__.items())))
            for fn in self.real_encoder_functions)
        loader = SourceFileLoader("hashlib", "/synthetic/stdlib/hashlib.py")
        spec = ModuleSpec("hashlib", loader, origin=loader.path)
        spec._set_fileattr = True
        spec._cached = "/synthetic/stdlib/__pycache__/hashlib.cpython-312.pyc"
        self.provider = importlib.util.module_from_spec(spec)
        native_file = "/synthetic/stdlib/lib-dynload/_hashlib.so"
        native_loader = ExtensionFileLoader("_hashlib", native_file)
        native_spec = ModuleSpec("_hashlib", native_loader, origin=native_file)
        native_spec._set_fileattr = True
        self.native = ModuleType("_hashlib")
        self.native.__dict__.update(__file__=native_file, __package__="", __spec__=native_spec,
            __loader__=native_loader, __cached__=None, HASH=hashlib.__dict__["_hashlib"].HASH,
            openssl_sha256=hashlib.sha256)
        self.provider.__dict__.update(_hashlib=self.native, _NATIVE_SHA=hashlib.sha256,
            _HASH_CALLS=0, _HASH_CALLBACK=None, _HASH_ERROR=None, _HASH_RESULT=None)
        self.factory = FunctionType(_fixture_sha256.__code__, self.provider.__dict__, "sha256")
        self.provider.sha256 = self.factory
        def bind_provider(run):
            run.cache[NAME].hashlib = self.provider
            run.cache[NAME].ExtensionFileLoader = ExtensionFileLoader
            run.cache.update(hashlib=self.provider, _hashlib=self.native,
                             json=json, **{"json.encoder": sys.modules["json.encoder"]})
        self.selected = subject.build_inline_report_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True, after_exec=bind_provider)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.report = self.namespace["_inline_profile_report"]
        self.payload = semantic_fixture()
        self.scalars = reporter_scalars(self.payload)

    def tearDown(self):
        # Nach dem ganzen synthetischen Reporttest; keine Reparatur realer Caches.
        self.assertIs(sys.modules, self.real_cache)
        for name, value in zip(self.real_names, self.real_values):
            self.assertIs(sys.modules.get(name, _REPORT_OMITTED), value)
        self.assertEqual(sys.modules["__main__"].__name__, self.real_main_name)
        self.assertIs(json.JSONEncoder, self.real_encoder)
        for current, expected in ((tuple(sorted(self.real_encoder.__dict__.items())), self.real_encoder_namespace),
            (tuple(sorted(json.__dict__.items())), self.real_json_namespace),
            (tuple(sorted(self.real_encoder_module.__dict__.items())), self.real_encoder_module_namespace)):
            self.assertEqual(tuple(k for k, _ in current), tuple(k for k, _ in expected))
            self.assertTrue(all(a[1] is b[1] for a, b in zip(current, expected)))
        for fn, state in zip(self.real_encoder_functions, self.real_encoder_states):
            self.assertIs(fn.__code__, state[0])
            self.assertIs(fn.__defaults__, state[1])
            self.assertIs(fn.__kwdefaults__, state[2])
            if state[3] is not None:
                current = tuple(sorted(fn.__kwdefaults__.items()))
                self.assertEqual(tuple(k for k, _ in current), tuple(k for k, _ in state[3]))
                self.assertTrue(all(a[1] is b[1] for a, b in zip(current, state[3])))

    def call(self, payload=None, scalars=_REPORT_OMITTED):
        payload = self.payload if payload is None else payload
        scalars = self.scalars if scalars is _REPORT_OMITTED else scalars
        metadata = syntax_bytes(syntax_form(payload))
        header = struct.pack(">8sII", b"DGNC001\0", len(metadata), sum(row[3] for row in payload[0][5]))
        return self.report(header, metadata, scalars)

    def accepted(self, payload=None, scalars=_REPORT_OMITTED):
        payload = self.payload if payload is None else payload
        scalars = self.scalars if scalars is _REPORT_OMITTED else scalars
        result = self.call(payload, scalars)
        self.assertEqual(result[:2], ("FORMATTED_PROFILE_REPORT", "NONE"), result[:2])
        self.assertIs(type(result[2]), tuple)
        actual = reporter_reassemble(result[2])
        expected, form, data = reporter_reference(payload, scalars)
        self.assertEqual(actual, data)
        parser = syntax_reference._Parser(actual)
        parsed = parser.value()
        self.assertEqual(parser.pos, len(actual))
        self.assertEqual(parsed, form)
        self.assertEqual(syntax_reference._resolve(parsed, 1), expected)
        reference = syntax_reference._semantics(expected, 1)[0]
        self.assertEqual(reference.installation.version, expected[1][3])
        self.assertEqual(reference.controls, expected[2])
        self.assertEqual(tuple(tuple(getattr(row, k) for k in (
            "name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader",
            "loaderName", "loaderPath", "aliasGroup")) for row in reference.modules), expected[3])
        return result[2]

    def rejected(self, scalars=_REPORT_OMITTED, issue=None, payload=None):
        result = self.call(payload, scalars)
        self.assertEqual(result[0], "REJECTED_PROFILE_REPORT")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("/synthetic", repr(result))
        self.assertNotIn("PRIVATE_PAYLOAD", repr(result))
        return result

    def test_all_three_ordinals_complete_reference_and_codec(self):
        for ordinal in (1, 2, 3):
            payload = semantic_fixture(ordinal)
            self.accepted(payload, reporter_scalars(payload))

    def test_given_installation_and_inventory_are_not_worker_defaults(self):
        changed = semantic_change(self.scalars, (1, 2), (3, 12, 99))
        row = ("additional", "additional", "additional", "built-in", "", "BUILTIN", (), "BUILTIN", "", "", ())
        changed = semantic_change(changed, (2,), tuple(sorted(changed[2] + (row,))))
        self.accepted(scalars=changed)

    def test_context_original_digest_and_report_digest_are_distinct(self):
        records = self.accepted()
        end = json.loads(records[-1])
        data = reporter_reassemble(records)
        self.assertEqual(end[4], hashlib.sha256(data).hexdigest())
        self.assertNotEqual(end[4], self.payload[0][6])
        self.assertEqual(self.provider._HASH_CALLS, 2)
        actual = syntax_reference._resolve(syntax_reference._Parser(data).value(), 1)
        self.assertEqual(actual[0], self.payload[2])

    def test_one_metadata_parser_pass_and_separate_digest_preimages(self):
        original = self.namespace["_inline_metadata_syntax"]
        calls = []
        def counted(*args):
            calls.append(args)
            return original(*args)
        self.namespace["_inline_metadata_syntax"] = counted
        self.accepted()
        self.assertEqual(len(calls), 1)

    def test_late_scalar_primitive_failure_before_bad_input_digest(self):
        payload = semantic_change(self.payload, (0, 6), "0" * 64)
        for path, value in (((2, 2, 10), Foreign()), ((1, 11, 0, 2), None),
                            ((1, 2, 2), True), ((0, 3), ["__main__", NAME])):
            self.rejected(semantic_change(self.scalars, path, value), "SCALAR_FORM", payload)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_semantic_scalar_failure_before_bad_input_digest(self):
        payload = semantic_change(self.payload, (0, 6), "0" * 64)
        self.rejected(semantic_change(self.scalars, (2, 2, 7), "NONE"), "MODULE_FORM", payload)
        self.rejected(semantic_change(self.scalars, (1, 11, 0, 2), "BAD"), "CONTEXT_FORM", payload)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_missing_foreign_subclass_scalar_containers(self):
        class ForeignTuple(tuple):
            pass
        class ForeignText(str):
            pass
        for value in (Foreign(), None, (), self.scalars[:2], ForeignTuple(self.scalars)):
            self.rejected(value, "SCALAR_FORM")
        self.rejected(semantic_change(self.scalars, (1, 0), ForeignText("linux")), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_text_encoding_nul_utf8_and_4096_byte_bounds(self):
        for value in ("\0", "\ud800", "x" * 4097, "é" * 2049):
            result = self.rejected(semantic_change(self.scalars, (1, 6), value))
            self.assertIn(result[1], ("SCALAR_FORM", "TEXT_LIMIT"))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_s15_policy_and_source_root_loader_contamination(self):
        for path, value, issue in (((1, 0), "win32", "INSTALLATION_FORM"),
            ((0, 1), ("/same", "/same"), "INSTALLATION_FORM"),
            ((1, 8), ("/foreign",), "PATH_FORM"), ((2, 1, 8), "wrong", "MODULE_FORM"),
            ((2, 1, 9), "/foreign", "MODULE_FORM"), ((2, 2, 4), "relative", "PATH_FORM")):
            self.rejected(semantic_change(self.scalars, path, value), issue)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_generic_controls_nullspec_and_own_cache_names(self):
        row = ("chosen_control", "chosen_control", None, "", "", "CONTROL", (), "NONE", "", "", ())
        scalars = semantic_change(self.scalars, (2,), tuple(sorted(self.scalars[2] + (row,))))
        scalars = semantic_change(scalars, (0, 3), self.scalars[0][3] + ("chosen_control",))
        self.accepted(scalars=scalars)
        self.rejected(semantic_change(self.scalars, (0, 3), ("__main__",)), "CONTROL_FORM")
        self.rejected(semantic_change(self.scalars, (2, 2, 0), "Tests.Contracts"), "OWN_MODULE_CACHED")

    def test_complete_frozen_pairs_optional_singletons_and_mixed(self):
        for pair in self.namespace["_SEMANTIC_PAIRS"]:
            rows = []
            for name in pair:
                module, spec = self.namespace["_SEMANTIC_FROZEN"].get(name, (name, name))
                rows.append((name, module, spec, "frozen", "", "FROZEN", (), "FROZEN", "", "", pair))
            changed = semantic_change(self.scalars, (2,), tuple(sorted(self.scalars[2] + tuple(rows))))
            self.accepted(scalars=changed)
            self.rejected(semantic_change(changed, (2,), tuple(r for r in changed[2] if r[0] != pair[1])), "ALIAS_FORM")
            singleton = rows[0][:-1] + ((),)
            self.accepted(scalars=semantic_change(self.scalars, (2,), tuple(sorted(self.scalars[2] + (singleton,)))))
        frozen = ("_collections_abc", "collections.abc", "_collections_abc", "frozen", "", "FROZEN", (), "FROZEN", "", "", ())
        path = "/synthetic/stdlib/collections/abc.py"
        source = ("collections.abc", "collections.abc", "collections.abc", path, path, "SOURCE", (), "SOURCE", "collections.abc", path, ())
        self.accepted(scalars=semantic_change(self.scalars, (2,), tuple(sorted(self.scalars[2] + (frozen, source)))))

    def test_reordered_duplicate_inventory_and_late_second_d9(self):
        self.rejected(semantic_change(self.scalars, (2,), self.scalars[2][::-1]), "INVENTORY_FORM")
        self.rejected(semantic_change(self.scalars, (2,), self.scalars[2] + (self.scalars[2][-1],)), "INVENTORY_FORM")
        self.rejected(payload=semantic_change(self.payload, (2, 4, 8, 4), None), issue="POSITION_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_input_digest_and_context_selector_fail_without_records(self):
        self.rejected(payload=semantic_change(self.payload, (0, 6), "0" * 64), issue="INPUT_DIGEST")
        self.rejected(payload=semantic_change(self.payload, (2, 3), "a" * 64), issue="INPUT_BINDING")
        self.rejected(payload=semantic_change(self.payload, (2,), self.payload[2][:5] + semantic_fixture(2)[2][5:]), issue="CONTEXT_MISMATCH")

    def test_own_pool_not_input_pool_and_semantic_integer_zero(self):
        scalars = semantic_change(self.scalars, (1, 6), "pooled-binding-design/v1")
        records = self.accepted(scalars=scalars)
        parsed = syntax_reference._Parser(reporter_reassemble(records)).value()
        self.assertIn("pooled-binding-design/v1", parsed[2])
        self.assertEqual(parsed[3][0][4][0][0], 0)  # D5 ordinal is an integer, not a TextRef.
        self.assertIsNone(parsed[3][3][0][2])
        self.assertIn("", parsed[2])

    def test_unicode_and_pipe_payload_without_second_escape_layer(self):
        value = 'ABI|quote"slash\\é😀\u007f'
        records = self.accepted(scalars=semantic_change(self.scalars, (1, 6), value))
        data = reporter_reassemble(records)
        self.assertIn(b"|quote", data)
        self.assertIn(b"\\u00e9", data)
        self.assertIn(b"\\ud83d\\ude00", data)
        self.assertNotIn(b"\n", data)

    def test_pool_exact_256_then_257_with_valid_source_locations(self):
        expected, _, _ = reporter_reference(self.payload, self.scalars)
        count = len(syntax_form(expected)[2])
        locations = tuple("/synthetic/stdlib/location%03d" % n for n in range(256 - count))
        scalars = semantic_change(self.scalars, (2, 1, 6), locations)
        self.accepted(scalars=scalars)
        self.assertEqual(len(reporter_reference(self.payload, scalars)[1][2]), 256)
        self.rejected(semantic_change(scalars, (2, 1, 6), locations + ("/synthetic/stdlib/extra",)), "POOL_LIMIT")

    def scalar_with_json_size(self, size):
        # Vier vollständige zulässige Locatorfelder, keine künstliche Counteränderung.
        prefix = "/synthetic/stdlib/"
        for count in range(4):
            locations = tuple(prefix + chr(97 + n) * (4096 - len(prefix)) for n in range(count))
            last = prefix + "z"
            scalars = semantic_change(self.scalars, (2, 1, 6), locations + (last,))
            delta = size - len(reporter_reference(self.payload, scalars)[2])
            if 0 <= delta <= 4096 - len(last):
                scalars = semantic_change(scalars, (2, 1, 6), locations + (last + "z" * delta,))
                self.assertEqual(len(reporter_reference(self.payload, scalars)[2]), size)
                return scalars
        self.fail("Keine gültige synthetische Locatorgröße gefunden")

    def test_actual_report_metadata_cap_exact_then_one_byte_over(self):
        at_cap = self.scalar_with_json_size(16368)
        records = self.accepted(scalars=at_cap)
        self.assertEqual(len(reporter_reassemble(records)), 16368)
        self.assertEqual(len(records), 21)
        self.rejected(self.scalar_with_json_size(16369), "METADATA_LIMIT")

    def test_bounded_repeated_locations_before_pool_and_hash(self):
        rows = tuple(("source%03d" % n, "source%03d" % n, "source%03d" % n,
                      "/synthetic/stdlib/x", "/synthetic/stdlib/x", "SOURCE",
                      ("/synthetic/stdlib/pkg",) * 256, "SOURCE", "source%03d" % n,
                      "/synthetic/stdlib/x", ()) for n in range(70))
        scalars = semantic_change(self.scalars, (2,), tuple(sorted(self.scalars[2] + rows)))
        self.rejected(scalars, "NODE_LIMIT")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_internal_shape_depth_and_node_guard_arithmetic(self):
        # Interne Aufnahmegrenzen, kein behaupteter gültiger Scalar3 mit dieser Tiefe.
        shape, value = "n", 0
        for _ in range(8):
            shape, value = (shape,), (value,)
        self.namespace["_report_shape"](shape, value)
        with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
            self.namespace["_report_shape"]((shape,), (value,))
        self.assertEqual(caught.exception.args, ("DEPTH_LIMIT",))
        counter = [16367]
        self.namespace["_report_shape"]("n", 0, counter=counter)
        with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
            self.namespace["_report_shape"]("n", 0, counter=counter)
        self.assertEqual(caught.exception.args, ("NODE_LIMIT",))

    def test_header_metadata_foreign_before_scalar_or_hash(self):
        metadata = syntax_bytes(syntax_form(self.payload))
        header = struct.pack(">8sII", b"DGNC001\0", len(metadata), 0)
        for a, b in ((Foreign(), metadata), (header, Foreign()), (b"", metadata)):
            result = self.report(a, b, Foreign())
            self.assertEqual(result[0], "REJECTED_PROFILE_REPORT")
            self.assertIsNone(result[2])
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_private_records_896_897_and_exact_last_rest(self):
        # Interne Framingarithmetik über harmlose Bytes, kein Canonical-/Decoderclaim.
        encoder = self.namespace["_report_encoder_anchor"]()
        for size in (1, 895, 896, 897, 1792, 1793, 16128, 16368):
            data = b"x" * size
            records = self.namespace["_report_records"](data, 3, hashlib.sha256(data).hexdigest(), encoder)
            self.assertEqual(reporter_reassemble(records), data)
            self.assertEqual(len(records), (size + 895) // 896 + 2)
            self.assertTrue(all(len(r) <= 1024 for r in records))
            self.assertTrue(len(records[0]) <= 256 and len(records[-1]) <= 256)
        with self.assertRaises(self.namespace["_InlineSyntaxRejected"]):
            self.namespace["_report_records"](b"x" * 16369, 1, "0" * 64, encoder)

    def test_test_reassembly_rejects_missing_duplicate_order_and_footer(self):
        records = self.accepted()
        self.assertGreater(len(records), 3)
        changed = list(records)
        changed[1], changed[2] = changed[2], changed[1]
        for rows in (records[:-1], records[:1] + records[2:], records[:2] + records[1:], tuple(changed),
                     records[:-1] + (records[-1].replace(b'"PROFILE_END"', b'"WRONG"'),)):
            with self.assertRaises((AssertionError, ValueError, IndexError)):
                reporter_reassemble(rows)

    def test_encoder_class_exchange_and_code_drift_closed(self):
        anchor = self.namespace["_report_encoder_anchor"]()
        with patch.object(json, "JSONEncoder", Foreign()):
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]):
                self.namespace["_report_encoder_check"](anchor)
        method = json.JSONEncoder.iterencode
        code = method.__code__
        try:
            method.__code__ = _fixture_config_var.__code__
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]):
                self.namespace["_report_encoder_check"](anchor)
        finally:
            method.__code__ = code

    def test_public_report_foreign_encoder_has_encoder_binding_label(self):
        header_metadata = InlineMetadataSemanticsTests.packet(self, self.payload)
        original = self.namespace["_inline_metadata_syntax"]
        def changed(*args):
            actual = original(*args)
            json.JSONEncoder = Foreign()
            return actual
        # Erstaufnahme des Encoderankers nach tatsächlich erfolgreichem M-Repack.
        with patch.dict(self.namespace, {"_inline_metadata_syntax": changed}):
            with patch.object(json, "JSONEncoder", json.JSONEncoder):
                result = self.report(*header_metadata, self.scalars)
        self.assertEqual(result, ("REJECTED_PROFILE_REPORT", "REPORT_ENCODER_BINDING", None))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_encoder_drift_during_original_hash_is_closed(self):
        self.provider._HASH_CALLBACK = lambda: self.run.cache.__setitem__("json.encoder", Foreign())
        self.rejected(issue="REPORT_ENCODER_BINDING")

    def test_encoder_drift_during_report_hash_is_closed(self):
        def change():
            if self.provider._HASH_CALLS == 2:
                self.run.cache["json.encoder"] = Foreign()
        self.provider._HASH_CALLBACK = change
        self.rejected(issue="REPORT_ENCODER_BINDING")

    def test_encoder_binding_loss_dominates_failed_original_constructor(self):
        def change():
            self.run.cache["json.encoder"] = Foreign()
            self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.provider._HASH_CALLBACK = change
        self.rejected(issue="REPORT_ENCODER_BINDING")

    def test_provider_binding_loss_dominates_both_encoder_and_call_failure(self):
        def change():
            self.run.cache["json.encoder"] = Foreign()
            self.run.cache["hashlib"] = Foreign()
            self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.provider._HASH_CALLBACK = change
        self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_class_dispatch_and_keyword_default_mutation_guard(self):
        cls = json.JSONEncoder
        anchor = self.namespace["_report_encoder_anchor"]()
        try:
            cls.synthetic_field = 1
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]):
                self.namespace["_report_encoder_check"](anchor)
        finally:
            del cls.synthetic_field
        keywords = cls.__init__.__kwdefaults__
        old = keywords["ensure_ascii"]
        try:
            keywords["ensure_ascii"] = not old
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]):
                self.namespace["_report_encoder_check"](anchor)
        finally:
            keywords["ensure_ascii"] = old
        invoked = []
        def foreign_getattribute(obj, name):
            invoked.append(name)
            return object.__getattribute__(obj, name)
        try:
            cls.__getattribute__ = foreign_getattribute
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]):
                self.namespace["_report_encoder_check"](anchor)
            self.assertEqual(invoked, [])
        finally:
            del cls.__getattribute__

    def test_constructor_class_drift_before_first_iterencode_lookup(self):
        cls = json.JSONEncoder
        held, held_iter = cls.__init__, cls.iterencode
        namespace = sys.modules["json.encoder"].__dict__
        # Ausschließlich gehaltene eigene temporäre Globale; vollständig zurücksetzen.
        keys = ("_REPORT_HELD_INIT", "_REPORT_ENCODER_CLASS", "_REPORT_ITER_CALLED", "_REPORT_HELD_ITER")
        self.assertTrue(all(k not in namespace for k in keys))
        namespace.update(_REPORT_HELD_INIT=held, _REPORT_ENCODER_CLASS=cls,
                         _REPORT_ITER_CALLED=0, _REPORT_HELD_ITER=held_iter)
        function = FunctionType(_fixture_report_encoder_init.__code__, namespace)
        iterator = FunctionType(_fixture_report_encoder_iterencode.__code__, namespace)
        try:
            cls.__init__ = function
            cls.iterencode = iterator
            anchor = self.namespace["_report_encoder_anchor"]()
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
                self.namespace["_report_json"](("x",), anchor)
            self.assertEqual(caught.exception.args, ("REPORT_ENCODER_BINDING",))
            self.assertEqual(namespace["_REPORT_ITER_CALLED"], 0)
            self.assertIn("synthetic_dispatch", cls.__dict__)
        finally:
            cls.__init__ = held
            cls.iterencode = held_iter
            if "synthetic_dispatch" in cls.__dict__:
                del cls.synthetic_dispatch
            for key in keys:
                del namespace[key]

    def test_encoder_cannot_execute_changed_provider_constructor(self):
        encoder_anchor = self.namespace["_report_encoder_anchor"]()
        provider_anchor = self.namespace["_semantic_provider_anchor"]()
        old = self.factory.__code__
        try:
            self.factory.__code__ = _fixture_config_var.__code__
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
                self.namespace["_report_sha"](b"synthetic", provider_anchor)
            self.assertEqual(caught.exception.args, ("HASH_PROVIDER_BINDING",))
            self.assertEqual(self.provider._HASH_CALLS, 0)
        finally:
            self.factory.__code__ = old
        self.namespace["_report_encoder_check"](encoder_anchor)

    def test_actual_encoder_exchange_precedes_hash_constructor_rejection(self):
        cls, old_code = json.JSONEncoder, self.factory.__code__
        held_iter = cls.iterencode
        namespace = sys.modules["json.encoder"].__dict__
        keys = ("_REPORT_FACTORY", "_REPORT_REPLACEMENT_CODE", "_REPORT_HELD_ITER")
        self.assertTrue(all(k not in namespace for k in keys))
        namespace.update(_REPORT_FACTORY=self.factory, _REPORT_REPLACEMENT_CODE=_fixture_config_var.__code__,
                         _REPORT_HELD_ITER=held_iter)
        try:
            cls.iterencode = FunctionType(_fixture_report_encoder_exchange_provider.__code__, namespace)
            # Feste Callbackroute wird vor PRE gewählt; sie bleibt im Encoderanker identisch.
            encoder_anchor = self.namespace["_report_encoder_anchor"]()
            provider_anchor = self.namespace["_semantic_provider_anchor"]()
            data = self.namespace["_report_json"](("synthetic",), encoder_anchor)
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
                self.namespace["_report_sha"](data, provider_anchor)
            self.assertEqual(caught.exception.args, ("HASH_PROVIDER_BINDING",))
            self.assertEqual(self.provider._HASH_CALLS, 0)
        finally:
            cls.iterencode = held_iter
            self.factory.__code__ = old_code
            for key in keys:
                del namespace[key]

    def test_constructor_instance_shadow_is_closed_before_foreign_call(self):
        cls, held = json.JSONEncoder, json.JSONEncoder.__init__
        namespace = sys.modules["json.encoder"].__dict__
        keys = ("_REPORT_HELD_INIT", "_REPORT_SHADOW")
        self.assertTrue(all(key not in namespace for key in keys))
        calls = []
        def shadow(value):
            calls.append(value)
            return ("PRIVATE_PAYLOAD",)
        namespace.update(_REPORT_HELD_INIT=held, _REPORT_SHADOW=shadow)
        try:
            cls.__init__ = FunctionType(_fixture_report_encoder_instance_shadow.__code__, namespace)
            anchor = self.namespace["_report_encoder_anchor"]()
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
                self.namespace["_report_json"](("synthetic",), anchor)
            self.assertEqual(caught.exception.args, ("REPORT_ENCODER_BINDING",))
            self.assertEqual(calls, [])
        finally:
            cls.__init__ = held
            for key in keys:
                del namespace[key]

    def test_constructor_silent_instance_setting_change_is_closed(self):
        cls, held = json.JSONEncoder, json.JSONEncoder.__init__
        namespace = sys.modules["json.encoder"].__dict__
        self.assertNotIn("_REPORT_HELD_INIT", namespace)
        namespace["_REPORT_HELD_INIT"] = held
        try:
            cls.__init__ = FunctionType(_fixture_report_encoder_instance_setting.__code__, namespace)
            anchor = self.namespace["_report_encoder_anchor"]()
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
                self.namespace["_report_json"](("é",), anchor)
            self.assertEqual(caught.exception.args, ("REPORT_ENCODER_BINDING",))
        finally:
            cls.__init__ = held
            del namespace["_REPORT_HELD_INIT"]

    def test_all_canonical_instance_setting_forms_and_values(self):
        anchor = self.namespace["_report_encoder_anchor"]()
        for name, value in (("skipkeys", True), ("ensure_ascii", False), ("check_circular", False),
                            ("allow_nan", True), ("sort_keys", False), ("indent", 0),
                            ("item_separator", ", "), ("key_separator", ": "),
                            ("ensure_ascii", 1), ("item_separator", Foreign()), ("default", Foreign())):
            encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
            setattr(encoder, name, value)
            with self.assertRaises(self.namespace["_InlineSyntaxRejected"]) as caught:
                self.namespace["_report_encoder_instance"](encoder, anchor)
            self.assertEqual(caught.exception.args, ("REPORT_ENCODER_BINDING",))

    def test_provider_error_on_second_hash_has_no_records(self):
        def change():
            if self.provider._HASH_CALLS == 2:
                self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.provider._HASH_CALLBACK = change
        self.rejected(issue="HASH_PROVIDER_CALL")

    def test_provider_post_binding_loss_dominates_constructor_failure(self):
        def change():
            if self.provider._HASH_CALLS == 2:
                self.run.cache["hashlib"] = Foreign()
                self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.provider._HASH_CALLBACK = change
        self.rejected(issue="HASH_PROVIDER_BINDING")

    def test_provider_code_and_hash_class_drift_closed(self):
        self.native.HASH = Foreign()
        self.rejected(issue="HASH_PROVIDER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_reporter_source_no_capture_or_pipe_and_fixed_five_imports(self):
        tree = ast.parse(self.selected.source)
        imports = [n.names[0].name for n in tree.body if isinstance(n, ast.Import)]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(isinstance(n, ast.ImportFrom) for n in ast.walk(tree)))
        report = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_inline_profile_report")
        forbidden = {"print", "input", "open", "observe_current_interpreter_scalars", "Popen", "write"}
        self.assertFalse(any(isinstance(n, ast.Call) and (isinstance(n.func, ast.Name) and n.func.id in forbidden
            or isinstance(n.func, ast.Attribute) and n.func.attr in forbidden) for n in ast.walk(report)))
        self.assertFalse(self.selected.runtime_attested)
        self.assertFalse(self.selected.trust_attested)
        self.assertFalse(self.selected.import_used_bytes_attested)
        self.assertFalse(self.selected.method_approved)

    def test_four_old_source_builders_and_definition_bytes_unchanged(self):
        fourth = subject.build_inline_semantics_control_bootstrap(RAW, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(self.selected.source.decode().replace("\n" + subject._INLINE_REPORT, "", 1), fourth.source.decode())
        previous = ast.parse(fourth.source)
        actual = ast.parse(self.selected.source)
        definitions = {n.name: ast.dump(n) for n in actual.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
        self.assertTrue(all(definitions[n.name] == ast.dump(n) for n in previous.body
            if isinstance(n, (ast.ClassDef, ast.FunctionDef))))

    def test_full_report_source_cap_and_foreign_generation_inputs(self):
        base = subject.build_inline_report_control_bootstrap(b"x", logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        raw = b"x" * (subject.MAX_SCRIPT_BYTES - len(base.source) + 1)
        at_cap = subject.build_inline_report_control_bootstrap(raw, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(len(at_cap.source), subject.MAX_SCRIPT_BYTES)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_inline_report_control_bootstrap(raw + b"x", logical_profile=LOCATOR,
                expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))
        self.assertNotIn(LOCATOR, repr(self.selected))


class InlineMetadataReceiverTests(unittest.TestCase):
    def setUp(self):
        # Derselbe rein synthetische Provider; eigene Cache-/Main-Anker um jeden Test.
        self.real_cache = sys.modules
        self.real_names = (NAME, "__main__", "sysconfig", "json", "json.encoder", "_hashlib")
        self.real_values = tuple(sys.modules.get(name, _REPORT_OMITTED) for name in self.real_names)
        self.real_main_name = sys.modules["__main__"].__name__
        self.real_encoder = json.JSONEncoder
        self.real_encoder_namespace = tuple(sorted(self.real_encoder.__dict__.items()))
        self.real_json_namespace = tuple(sorted(json.__dict__.items()))
        self.real_encoder_module = sys.modules["json.encoder"]
        self.real_encoder_module_namespace = tuple(sorted(self.real_encoder_module.__dict__.items()))
        self.real_encoder_functions = tuple(self.real_encoder.__dict__[key]
                                           for key in ("__init__", "iterencode", "default"))
        self.real_encoder_states = tuple((fn.__code__, fn.__defaults__, fn.__kwdefaults__,
            None if fn.__kwdefaults__ is None else tuple(sorted(fn.__kwdefaults__.items())))
            for fn in self.real_encoder_functions)
        loader = SourceFileLoader("hashlib", "/synthetic/stdlib/hashlib.py")
        spec = ModuleSpec("hashlib", loader, origin=loader.path)
        spec._set_fileattr = True
        spec._cached = "/synthetic/stdlib/__pycache__/hashlib.cpython-312.pyc"
        self.provider = importlib.util.module_from_spec(spec)
        native_file = "/synthetic/stdlib/lib-dynload/_hashlib.so"
        native_loader = ExtensionFileLoader("_hashlib", native_file)
        native_spec = ModuleSpec("_hashlib", native_loader, origin=native_file)
        native_spec._set_fileattr = True
        self.native = ModuleType("_hashlib")
        self.native.__dict__.update(__file__=native_file, __package__="", __spec__=native_spec,
            __loader__=native_loader, __cached__=None, HASH=hashlib.__dict__["_hashlib"].HASH,
            openssl_sha256=hashlib.sha256)
        self.provider.__dict__.update(_hashlib=self.native, _NATIVE_SHA=hashlib.sha256,
            _HASH_CALLS=0, _HASH_CALLBACK=None, _HASH_ERROR=None, _HASH_RESULT=None)
        self.factory = FunctionType(_fixture_sha256.__code__, self.provider.__dict__, "sha256")
        self.provider.sha256 = self.factory
        def bind_provider(run):
            run.cache[NAME].hashlib = self.provider
            run.cache[NAME].ExtensionFileLoader = ExtensionFileLoader
            run.cache.update(hashlib=self.provider, _hashlib=self.native,
                             json=json, **{"json.encoder": sys.modules["json.encoder"]})
        self.selected = subject.build_inline_receive_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True, after_exec=bind_provider)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.receive = self.namespace["_inline_receive_metadata_chunks"]
        self.payload = semantic_fixture()
        self.format = "pooled-combined-input-design/v1"

    def tearDown(self):
        # Dieselben vollständigen gehaltenen Realstate-Prüfungen, ohne Reparatur.
        InlineProfileReporterTests.tearDown(self)

    def packet(self, payload=None, *, body_size=None):
        return InlineMetadataSemanticsTests.packet(self, self.payload if payload is None else payload,
                                                   body_size=body_size)

    def chunks(self, data, size=1024):
        return tuple(data[n:n + size] for n in range(0, len(data), size))

    def accepted(self, chunks=None, payload=None):
        payload = self.payload if payload is None else payload
        header, metadata = self.packet(payload)
        chunks = self.chunks(header + metadata) if chunks is None else chunks
        result = self.receive(chunks, expected_format=self.format)
        self.assertEqual(result[:2], ("VALID_RECEIVED_METADATA", "NONE"), result[:2])
        self.assertIs(type(result[2]), tuple)
        self.assertEqual(result[2], (header, metadata, payload))
        self.assertTrue(all(type(value) is bytes for value in result[2][:2]))
        return result[2]

    def rejected(self, chunks, issue=None, *, expected_format=_REPORT_OMITTED):
        selected = self.format if expected_format is _REPORT_OMITTED else expected_format
        result = self.receive(chunks, expected_format=selected)
        self.assertEqual(result[0], "REJECTED_RECEIVED_METADATA")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("/synthetic", repr(result))
        self.assertNotIn("PRIVATE_PAYLOAD", repr(result))
        return result

    def test_all_header_splits_and_single_byte_header_chunks(self):
        header, metadata = self.packet()
        for split in range(17):
            self.accepted((header[:split], header[split:]) + self.chunks(metadata))
            self.accepted((b"", header[:split], b"", header[split:]) + self.chunks(metadata) + (b"",))
        self.accepted(tuple(bytes((n,)) for n in header) + self.chunks(metadata))

    def test_chunks_can_cross_header_metadata_and_1024_boundaries(self):
        header, metadata = self.packet()
        for size in (127, 511, 1023, 1024):
            chunks = self.chunks(header + metadata, size)
            self.assertTrue(all(len(c) <= 1024 for c in chunks))
            self.accepted(chunks)

    def test_full_all_ordinal_payloads_match_independent_codec_fields(self):
        for ordinal in (1, 2, 3):
            payload = semantic_fixture(ordinal)
            held = self.accepted(payload=payload)
            actual = held[2]
            reference = syntax_reference._semantics(payload, 0)
            self.assertEqual(actual[0], reference[0])
            worker, context = reference[1:]
            installation = worker.installation
            self.assertEqual(actual[1][:3], (worker.ordinal, worker.entry, worker.phase))
            self.assertEqual(actual[1][3], tuple(getattr(installation, key)
                if key != "files" else tuple((row.path, row.size, row.sha256) for row in installation.files)
                for key in ("assumption", "platform", "implementation", "version", "executable",
                    "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip", "flags",
                    "finders", "hooks", "files")))
            self.assertEqual(actual[1][4], worker.controls)
            self.assertEqual(actual[1][5], tuple(tuple(getattr(row, key) for key in (
                "name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader",
                "loaderName", "loaderPath", "aliasGroup")) for row in worker.modules))
            self.assertEqual(actual[2][:4], (context.commit, context.raw27_binding,
                context.source_profile, context.nonce.hex()))
            self.assertEqual(actual[2][4], tuple((row.ordinal, row.module, row.member, row.size, row.sha256)
                                               for row in context.modules))
            self.assertEqual(actual[2][5:], (context.ordinal, context.entry, context.phase))

    def test_empty_chunks_are_finite_and_count_toward_256(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        self.accepted((b"",) * (256 - len(chunks)) + chunks)
        self.rejected((b"",) * (257 - len(chunks)) + chunks, "CHUNKS_LIMIT")
        self.rejected((), "HEADER_LENGTH")
        self.rejected((b"",) * 256, "HEADER_LENGTH")

    def test_format_exact_and_chosen_before_foreign_chunks(self):
        for value in (None, True, Foreign(), ForeignKey(self.format), "other",
                      "pooled-binding-design/v1"):
            self.rejected(Foreign(), "FORMAT_SELECTION", expected_format=value)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_foreign_tuple_and_byte_subclasses_are_never_dispatched(self):
        class Tuples(tuple):
            def __iter__(self):
                raise AssertionError("FOREIGN_ITERATOR")
        class Bytes(bytes):
            def __len__(self):
                raise AssertionError("FOREIGN_LENGTH")
        for value in (None, [], Foreign(), Tuples(())):
            self.rejected(value, "CHUNKS_TYPE")
        for value in (None, True, bytearray(), memoryview(b""), Foreign(), Bytes(b"x")):
            self.rejected((value,), "CHUNK_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_foreign_type_dominates_early_large_or_invalid_header(self):
        with patch.dict(self.namespace, {"_inline_metadata_semantics": Foreign(), "_INLINE_HEADER": Foreign()}):
            self.rejected((b"x" * 1025, Foreign()), "CHUNK_TYPE")
            self.rejected((b"x" * 16, Foreign()), "CHUNK_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_chunk_1024_allowed_and_1025_closed_before_parser(self):
        header, metadata = self.packet()
        data = header + metadata
        self.assertGreater(len(data), 1025)
        self.accepted(self.chunks(data, 1024))
        with patch.dict(self.namespace, {"_inline_metadata_semantics": Foreign(), "_INLINE_HEADER": Foreign()}):
            self.rejected((data[:1025],) + self.chunks(data[1025:]), "CHUNK_LIMIT")

    def test_entire_total_preflight_before_header_or_parser(self):
        with patch.dict(self.namespace, {"_inline_metadata_semantics": Foreign(), "_INLINE_HEADER": Foreign()}):
            self.rejected((b"x" * 1024,) * 16 + (b"x",), "METADATA_LIMIT")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_every_short_header_and_truncated_metadata_no_hash(self):
        header, metadata = self.packet()
        for size in range(16):
            self.rejected((header[:size],), "HEADER_LENGTH")
        for data in (header, header + metadata[:-1], header + metadata[:1]):
            self.rejected(self.chunks(data), "METADATA_LENGTH")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_extra_body_command_and_suffix_are_rejected_before_semantics(self):
        header, metadata = self.packet()
        for extra in (b"x", b'BODY_RELEASE\n', b'\0', b'\r\n'):
            with patch.dict(self.namespace, {"_inline_metadata_semantics": Foreign()}):
                self.rejected(self.chunks(header + metadata + extra), "METADATA_LENGTH")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_header_magic_metadata_and_body_bounds(self):
        _, metadata = self.packet()
        cases = ((b"WRONG001", len(metadata), 0, "HEADER_FORM"),
                 (b"DGNC001\0", 0, 0, "METADATA_LIMIT"),
                 (b"DGNC001\0", 16369, 0, "METADATA_LIMIT"),
                 (b"DGNC001\0", len(metadata), 1048577, "BODY_LIMIT"))
        for magic, length, body, issue in cases:
            with patch.dict(self.namespace, {"_inline_metadata_semantics": Foreign()}):
                self.rejected(self.chunks(struct.pack(">8sII", magic, length, body) + metadata), issue)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_positive_body_announcement_is_not_body_intake(self):
        payload = self.payload
        descriptors = tuple(row[:3] + (1,) + row[4:] for row in payload[0][5])
        payload = semantic_change(payload, (0, 5), descriptors)
        payload = semantic_change(payload, (2, 4), descriptors)
        original = dict(protocol=payload[0][0], commit=payload[0][1], raw27_binding=payload[0][2],
            source_profile=payload[0][3], nonce=payload[0][4], modules=[dict(zip(
                ("ordinal", "module", "member", "size", "sha256"), row)) for row in descriptors])
        digest = hashlib.sha256(json.dumps(original, sort_keys=True, ensure_ascii=True,
            separators=(",", ":"), allow_nan=False).encode("ascii")).hexdigest()
        payload = semantic_change(payload, (0, 6), digest)
        held = self.accepted(payload=payload)
        self.assertEqual(struct.unpack(">8sII", held[0])[2], 9)
        self.assertEqual(len(held), 3)

    def test_declared_body_sum_mismatch_has_no_partial_return(self):
        header, metadata = self.packet(body_size=1)
        self.rejected(self.chunks(header + metadata), "DECLARED_BODY_LENGTH")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_last_field_second_ninth_descriptor_before_original_digest(self):
        changed = semantic_change(self.payload, (0, 6), "0" * 64)
        changed = semantic_change(changed, (2, 4, 8, 4), None)
        header, metadata = self.packet(changed)
        self.rejected(self.chunks(header + metadata), "POSITION_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_original_digest_context_and_selector_fail_atomic(self):
        for payload, issue in ((semantic_change(self.payload, (0, 6), "0" * 64), "INPUT_DIGEST"),
            (semantic_change(self.payload, (2, 3), "a" * 64), "INPUT_BINDING"),
            (semantic_change(self.payload, (2,), self.payload[2][:5] + semantic_fixture(2)[2][5:]),
             "CONTEXT_MISMATCH")):
            header, metadata = self.packet(payload)
            self.rejected(self.chunks(header + metadata), issue)

    def test_provider_pre_and_dominant_failed_constructor_post(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        with patch.dict(self.run.cache, {"hashlib": Foreign()}):
            self.rejected(chunks, "HASH_PROVIDER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 0)
        def drift():
            self.run.cache["hashlib"] = Foreign()
            self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.provider._HASH_CALLBACK = drift
        self.rejected(chunks, "HASH_PROVIDER_BINDING")

    def test_provider_call_failure_never_returns_received_bytes(self):
        self.provider._HASH_ERROR = RuntimeError("PRIVATE_PAYLOAD")
        header, metadata = self.packet()
        self.rejected(self.chunks(header + metadata), "HASH_PROVIDER_CALL")

    def test_valid_metadata_total_cap_exact_and_plus_one(self):
        # Gültige S15 ABI-Texte: gleiche Providerdaten, nur deklarative Metadata wächst.
        initial = semantic_change(self.payload, (1, 3, 7), "x")
        for count in range(3, 6):
            locations = tuple("/synthetic/stdlib/" + chr(97 + n) * 3900 for n in range(count))
            source = ("source", "source", "source", "/synthetic/stdlib/source.py",
                "/synthetic/stdlib/source.py", "SOURCE", locations, "SOURCE", "source",
                "/synthetic/stdlib/source.py", ())
            candidate = semantic_change(initial, (1, 5), tuple(sorted(initial[1][5] + (source,))))
            header, metadata = self.packet(candidate)
            padding = 16384 - 16 - len(metadata)
            if 0 <= padding <= 4095:
                candidate = semantic_change(candidate, (1, 3, 7), "x" * (padding + 1))
                header, metadata = self.packet(candidate)
                self.assertEqual(len(header + metadata), 16384)
                self.accepted(self.chunks(header + metadata), candidate)
                over = semantic_change(candidate, (1, 3, 7), "x" * (padding + 2))
                header, metadata = self.packet(over)
                self.assertEqual(len(header + metadata), 16385)
                self.rejected(self.chunks(header + metadata), "METADATA_LIMIT")
                return
        self.fail("Keine gültige synthetische Metadata-Grenzfixture")

    def test_received_exact_bytes_unicode_without_normalization(self):
        payload = semantic_change(self.payload, (1, 3, 7), 'ABI|quote"slash\\é😀')
        header, metadata = self.packet(payload)
        self.assertIn(b"\\u00e9", metadata)
        self.assertIn(b"|", metadata)
        self.accepted(self.chunks(header + metadata, 127), payload)
        altered = metadata.replace(b",", b", ", 1)
        new_header = struct.pack(">8sII", b"DGNC001\0", len(altered), 0)
        self.rejected(self.chunks(new_header + altered), "JSON_FORM")

    def test_failure_under_active_exception_has_only_fixed_tuple(self):
        try:
            raise OSError("PRIVATE_PAYLOAD")
        except OSError:
            result = self.rejected((Foreign(),), "CHUNK_TYPE")
        self.assertEqual(result, ("REJECTED_RECEIVED_METADATA", "CHUNK_TYPE", None))

    def test_repeat_given_chunks_has_no_consumption_or_replay_claim(self):
        first = self.accepted()
        second = self.accepted()
        self.assertEqual(first, second)
        self.assertEqual(self.provider._HASH_CALLS, 2)

    def test_five_old_builders_and_definitions_unchanged(self):
        fifth = subject.build_inline_report_control_bootstrap(RAW, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(self.selected.source.replace(
            ("\n" + subject._INLINE_RECEIVER).encode("utf-8"), b"", 1), fifth.source)
        before, after = ast.parse(fifth.source), ast.parse(self.selected.source)
        actual = {node.name: ast.dump(node) for node in after.body
                  if type(node) in (ast.ClassDef, ast.FunctionDef)}
        self.assertTrue(all(actual[node.name] == ast.dump(node) for node in before.body
                           if type(node) in (ast.ClassDef, ast.FunctionDef)))

    def test_fixed_imports_no_pipe_body_observation_or_release(self):
        tree = ast.parse(self.selected.source)
        self.assertEqual([n.names[0].name for n in tree.body if type(n) is ast.Import],
                         ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(n) is ast.ImportFrom for n in ast.walk(tree)))
        helper = next(n for n in tree.body if type(n) is ast.FunctionDef
                      and n.name == "_inline_receive_metadata_chunks")
        forbidden = {"read", "readinto", "open", "print", "input", "write", "Popen", "exec", "compile",
                     "observe_current_interpreter_scalars"}
        self.assertFalse(any(type(n) is ast.Call and (type(n.func) is ast.Name and n.func.id in forbidden
            or type(n.func) is ast.Attribute and n.func.attr in forbidden) for n in ast.walk(helper)))
        self.assertEqual(self.selected.claim, "GENERATED_CONTROL_SOURCE_ONLY")
        for field in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertFalse(getattr(self.selected, field))

    def test_full_source_cap_and_private_generation_failure(self):
        base = subject.build_inline_receive_control_bootstrap(b"x", logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        raw = b"x" * (subject.MAX_SCRIPT_BYTES - len(base.source) + 1)
        selected = subject.build_inline_receive_control_bootstrap(raw, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(len(selected.source), subject.MAX_SCRIPT_BYTES)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_inline_receive_control_bootstrap(raw + b"x", logical_profile=LOCATOR,
                expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertNotIn(LOCATOR, repr(selected))


class InlineContextCommandTests(unittest.TestCase):
    def setUp(self):
        self.real_cache = sys.modules
        self.real_names = (NAME, "__main__", "sysconfig", "json", "json.encoder", "_hashlib")
        self.real_values = tuple(sys.modules.get(name, _REPORT_OMITTED) for name in self.real_names)
        self.real_main_name = sys.modules["__main__"].__name__
        self.real_encoder = json.JSONEncoder
        self.real_encoder_namespace = tuple(sorted(self.real_encoder.__dict__.items()))
        self.real_json_namespace = tuple(sorted(json.__dict__.items()))
        self.real_encoder_module = sys.modules["json.encoder"]
        self.real_encoder_module_namespace = tuple(sorted(self.real_encoder_module.__dict__.items()))
        self.real_encoder_functions = tuple(self.real_encoder.__dict__[key]
                                           for key in ("__init__", "iterencode", "default"))
        self.real_encoder_states = tuple((fn.__code__, fn.__defaults__, fn.__kwdefaults__,
            None if fn.__kwdefaults__ is None else tuple(sorted(fn.__kwdefaults__.items())))
            for fn in self.real_encoder_functions)
        loader = SourceFileLoader("hashlib", "/synthetic/stdlib/hashlib.py")
        spec = ModuleSpec("hashlib", loader, origin=loader.path)
        spec._set_fileattr = True
        spec._cached = "/synthetic/stdlib/__pycache__/hashlib.cpython-312.pyc"
        self.provider = importlib.util.module_from_spec(spec)
        path = "/synthetic/stdlib/lib-dynload/_hashlib.so"
        native_loader = ExtensionFileLoader("_hashlib", path)
        native_spec = ModuleSpec("_hashlib", native_loader, origin=path)
        native_spec._set_fileattr = True
        self.native = ModuleType("_hashlib")
        self.native.__dict__.update(__file__=path, __package__="", __spec__=native_spec,
            __loader__=native_loader, __cached__=None, HASH=hashlib.__dict__["_hashlib"].HASH,
            openssl_sha256=hashlib.sha256)
        self.provider.__dict__.update(_hashlib=self.native, _NATIVE_SHA=hashlib.sha256,
            _HASH_CALLS=0, _HASH_CALLBACK=None, _HASH_ERROR=None, _HASH_RESULT=None)
        self.factory = FunctionType(_fixture_sha256.__code__, self.provider.__dict__, "sha256")
        self.provider.sha256 = self.factory
        def bind_provider(run):
            run.cache[NAME].hashlib = self.provider
            run.cache[NAME].ExtensionFileLoader = ExtensionFileLoader
            run.cache.update(hashlib=self.provider, _hashlib=self.native,
                             json=json, **{"json.encoder": sys.modules["json.encoder"]})
        self.selected = subject.build_inline_command_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True, after_exec=bind_provider)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.digest = self.namespace["_inline_context_digest"]
        self.encode = self.namespace["_inline_command_encode"]
        self.match = self.namespace["_inline_command_match"]
        self.context = semantic_fixture()[2]
        self.format = "pooled-combined-input-design/v1"
        self.kinds = ("BODY_RELEASE", "BODY_END", "IMPORT_RELEASE")

    def tearDown(self):
        InlineProfileReporterTests.tearDown(self)

    def reference(self, context):
        # Unabhängige vollständige Textaufnahme und K-Arity, nicht Produktionspacker.
        texts = set()
        def collect(value):
            if type(value) is str:
                texts.add(value)
            elif type(value) is tuple:
                for child in value:
                    collect(child)
        collect(context)
        pool = tuple(sorted(texts))
        def project(value):
            if type(value) is str:
                return pool.index(value)
            if type(value) is tuple:
                return tuple(project(child) for child in value)
            return value
        form = ("pooled-binding-design/v1", "pooled-profile-binding-context/v1",
                pool, (project(context),))
        data = json.dumps(form, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
                          allow_nan=False).encode("ascii")
        return form, data, hashlib.sha256(data).hexdigest()

    def line(self, *, kind="BODY_RELEASE", context=_REPORT_OMITTED, digest=_REPORT_OMITTED):
        context = self.context if context is _REPORT_OMITTED else context
        digest = self.reference(context)[2] if digest is _REPORT_OMITTED else digest
        return json.dumps((kind, context[5], context[3], digest), ensure_ascii=True,
                          separators=(",", ":"), allow_nan=False).encode("ascii") + b"\n"

    def reject(self, result, issue=None):
        self.assertIn(result[0], ("REJECTED_CONTEXT_DIGEST", "REJECTED_BOUND_COMMAND"))
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("PRIVATE_PAYLOAD", repr(result))
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_complete_k_reference_codec_arity_and_all_three_ordinals(self):
        for ordinal in (1, 2, 3):
            context = semantic_fixture(ordinal)[2]
            form, data, digest = self.reference(context)
            result = self.digest(context, expected_format=self.format)
            self.assertEqual(result, ("FORMATTED_CONTEXT_DIGEST", "NONE", digest))
            self.assertEqual(self.namespace["_command_k_json"](context,
                self.namespace["_report_encoder_anchor"]()), data)
            self.assertEqual(syntax_reference._resolve(form, 4), (context,))
            actual = syntax_reference._semantics((context,), 4)[0]
            self.assertEqual(actual.commit, context[0])
            self.assertEqual(actual.raw27_binding, context[1])
            self.assertEqual(actual.source_profile, context[2])
            self.assertEqual(actual.nonce.hex(), context[3])
            self.assertEqual(tuple((r.ordinal, r.module, r.member, r.size, r.sha256)
                for r in actual.modules), context[4])
            self.assertEqual((actual.ordinal, actual.entry, actual.phase), context[5:])
            self.assertEqual(hashlib.sha256(syntax_reference._canonical(form)).hexdigest(), digest)
            self.assertEqual(len(form[3]), 1)

    def test_all_kinds_and_ordinals_encode_match_actual_fields(self):
        for ordinal in (1, 2, 3):
            context = semantic_fixture(ordinal)[2]
            for kind in self.kinds:
                line = self.line(kind=kind, context=context)
                self.assertEqual(self.encode(kind, context, expected_format=self.format),
                    ("FORMATTED_BOUND_COMMAND", "NONE", line))
                actual = self.match(line, expected_kind=kind, expected_context=context,
                                    expected_format=self.format)
                self.assertEqual(actual, ("MATCHED_DECLARED_COMMAND", "NONE",
                    (kind, ordinal, context[3], self.reference(context)[2])))
                self.assertLessEqual(len(line), 256)
                self.assertEqual(line.count(b"\n"), 1)

    def test_original_input_domain_and_header_are_not_k_digest(self):
        form, data, digest = self.reference(self.context)
        original = semantic_fixture()[0][6]
        alternatives = (original, hashlib.sha256(struct.pack(">8sII", b"DGNP001\0", 5,
            len(data)) + data).hexdigest(), hashlib.sha256(syntax_bytes(
            (form[0], "REPORTED", form[2], form[3]))).hexdigest(),
            hashlib.sha256(syntax_bytes((form[0], form[1], form[2], form[3][0]))).hexdigest())
        for wrong in alternatives:
            self.assertNotEqual(digest, wrong)
            self.reject(self.match(self.line(digest=wrong), expected_kind=self.kinds[0],
                expected_context=self.context, expected_format=self.format), "COMMAND_MISMATCH")

    def test_every_k_field_mutation_changes_complete_digest(self):
        base = self.reference(self.context)[2]
        for path, value in (((0,), "b" * 40), ((1,), "c" * 64), ((3,), "d" * 64),
                            ((4, 8, 3), 1), ((4, 8, 4), "e" * 64)):
            context = semantic_change(self.context, path, value)
            digest = self.reference(context)[2]
            self.assertNotEqual(base, digest)
            self.assertEqual(self.digest(context, expected_format=self.format)[2], digest)
        self.assertNotEqual(base, self.reference(semantic_fixture(2)[2])[2])

    def test_fixed_format_precedes_foreign_intake(self):
        for value in (None, True, Foreign(), ForeignKey(self.format), "other", "pooled-binding-design/v1"):
            self.reject(self.digest(Foreign(), expected_format=value), "FORMAT_SELECTION")
            self.reject(self.encode(Foreign(), Foreign(), expected_format=value), "FORMAT_SELECTION")
            self.reject(self.match(Foreign(), expected_kind=Foreign(), expected_context=Foreign(),
                expected_format=value), "FORMAT_SELECTION")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_separate_expected_kind_never_received_fallback(self):
        for kind in (None, True, Foreign(), ForeignKey("BODY_RELEASE"), "INPUT_COMPLETE", "body_release"):
            self.reject(self.encode(kind, self.context, expected_format=self.format), "COMMAND_KIND")
            self.reject(self.match(self.line(), expected_kind=kind, expected_context=self.context,
                expected_format=self.format), "COMMAND_KIND")
        self.reject(self.match(self.line(kind="BODY_END"), expected_kind="BODY_RELEASE",
            expected_context=self.context, expected_format=self.format), "COMMAND_MISMATCH")

    def test_exact_k_container_and_primitive_subclasses(self):
        class Tuples(tuple):
            def __iter__(self):
                raise AssertionError("FOREIGN_ITERATOR")
        class Text(str):
            def __eq__(self, other):
                raise AssertionError("FOREIGN_EQUALITY")
        class Number(int):
            pass
        for context in (None, (), [], Foreign(), Tuples(self.context)):
            self.reject(self.digest(context, expected_format=self.format), "SCALAR_FORM")
        for path, value in (((0,), Text("a" * 40)), ((5,), True), ((5,), Number(1)),
                            ((4,), Tuples(self.context[4])), ((4, 8, 4), Foreign())):
            self.reject(self.digest(semantic_change(self.context, path, value),
                expected_format=self.format), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_d9_primitive_dominates_early_semantic_difference(self):
        context = semantic_change(self.context, (0,), "nothex")
        context = semantic_change(context, (4, 8, 4), Foreign())
        for result in (self.digest(context, expected_format=self.format),
            self.encode("BODY_RELEASE", context, expected_format=self.format),
            self.match(self.line(kind="BODY_END"), expected_kind="BODY_RELEASE",
                expected_context=context, expected_format=self.format)):
            self.reject(result, "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_full_d9_exact_arity_order_mapping_and_digest_forms(self):
        cases = ((self.context[4][:-1], "SCALAR_FORM"),
                 (self.context[4][::-1], "CONTEXT_FORM"),
                 (self.context[4][:-1] + (self.context[4][0],), "CONTEXT_FORM"))
        for rows, issue in cases:
            self.reject(self.digest(semantic_change(self.context, (4,), rows),
                expected_format=self.format), issue)
        for path, value in (((4, 8, 0), 7), ((4, 8, 1), "wrong"), ((4, 8, 2), "wrong.py"),
                            ((4, 8, 4), "A" * 64), ((4, 8, 4), "0" * 63)):
            self.reject(self.digest(semantic_change(self.context, path, value),
                expected_format=self.format), "CONTEXT_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_source_profile_hex_and_selector_policy_without_fake_i7(self):
        for path, value in (((0,), "g" * 40), ((1,), "0" * 63), ((2,), "other"),
                            ((3,), "A" * 64), ((5,), 0), ((5,), 4),
                            ((6,), "other-entry"), ((7,), "POST_IMPORT")):
            self.reject(self.digest(semantic_change(self.context, path, value),
                expected_format=self.format), "CONTEXT_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_declared_member_and_total_body_caps_without_body_read(self):
        context = semantic_change(self.context, (4, 8, 3), 131072)
        self.assertEqual(self.digest(context, expected_format=self.format)[0], "FORMATTED_CONTEXT_DIGEST")
        self.reject(self.digest(semantic_change(context, (4, 8, 3), 131073),
            expected_format=self.format), "CONTEXT_FORM")
        rows = tuple(r[:3] + (131072,) + r[4:] for r in self.context[4])
        self.reject(self.digest(semantic_change(self.context, (4,), rows),
            expected_format=self.format), "CONTEXT_FORM")

    def test_text_encoding_nul_surrogate_and_utf8_caps_before_provider(self):
        for value in ("\0", "\ud800", "x" * 4097, "é" * 2049):
            self.reject(self.digest(semantic_change(self.context, (4, 8, 2), value),
                expected_format=self.format))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_received_exact_bytes_not_foreign_or_subclass(self):
        class Bytes(bytes):
            def __len__(self):
                raise AssertionError("FOREIGN_LENGTH")
        for line in (None, True, [], Foreign(), bytearray(self.line()), memoryview(self.line()), Bytes(self.line())):
            self.reject(self.match(line, expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format), "COMMAND_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_received_lf_exact_no_cr_suffix_or_multiple_record(self):
        line = self.line()
        for value in (line[:-1], line + b"\n", line + b"x", line[:-1] + b"\r\n",
                      line[:1] + b"\n" + line[1:]):
            self.reject(self.match(value, expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format), "COMMAND_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_received_line_256_intake_257_preparser_and_empty(self):
        # 256 synthetische Paddingbytes sind keine gültige kanonische Commandform.
        line = self.line()
        at = line[:-1] + b" " * (256 - len(line)) + b"\n"
        self.assertEqual(len(at), 256)
        self.reject(self.match(at, expected_kind="BODY_RELEASE", expected_context=self.context,
            expected_format=self.format), "COMMAND_FORM")
        with patch.dict(self.namespace, {"_InlineParser": Foreign()}):
            for value in (at[:-1] + b"x\n", b""):
                self.reject(self.match(value, expected_kind="BODY_RELEASE", expected_context=self.context,
                    expected_format=self.format), "COMMAND_LIMIT")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_received_arity_null_bool_float_object_and_late_bad_field(self):
        for value in (b'[]\n', b'["BODY_RELEASE",1]\n', b'["BODY_RELEASE",true,"a","b"]\n',
                      b'["BODY_RELEASE",1.0,"a","b"]\n', b'{}\n',
                      b'["BODY_RELEASE",1,"' + b"a" * 64 + b'",null]\n'):
            self.reject(self.match(value, expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format))
        # Tatsächlich empfangene gültige Viererform mit zusätzlichem fünften Feld.
        self.reject(self.match(self.line()[:-2] + b',"extra"]\n', expected_kind="BODY_RELEASE",
            expected_context=self.context, expected_format=self.format), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_received_semantic_forms_before_hash_and_wrong_selector(self):
        valid = json.loads(self.line())
        for index, value in ((0, "INPUT_COMPLETE"), (1, 0), (1, 4), (2, "A" * 64),
                             (2, "0" * 63), (3, "g" * 64)):
            actual = valid.copy()
            actual[index] = value
            line = json.dumps(actual, separators=(",", ":")).encode("ascii") + b"\n"
            self.reject(self.match(line, expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_noncanonical_escapes_spaces_and_integer_leading_zero(self):
        line = self.line()
        for value in (line.replace(b'"BODY_RELEASE"', b'"\\u0042ODY_RELEASE"'),
                      line.replace(b",", b", ", 1), line.replace(b",1,", b",01,", 1)):
            result = self.reject(self.match(value, expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format))
            self.assertIn(result[1], ("COMMAND_CANONICAL", "JSON_FORM"))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_valid_received_kind_ordinal_nonce_and_digest_mismatch(self):
        valid = json.loads(self.line())
        for index, value in ((0, "BODY_END"), (1, 2), (2, "a" * 64), (3, "b" * 64)):
            actual = valid.copy()
            actual[index] = value
            line = json.dumps(actual, separators=(",", ":")).encode("ascii") + b"\n"
            self.reject(self.match(line, expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format), "COMMAND_MISMATCH")

    def test_late_received_form_dominates_valid_early_kind_mismatch(self):
        line = b'["BODY_END",1,"' + self.context[3].encode("ascii") + b'",null]\n'
        self.reject(self.match(line, expected_kind="BODY_RELEASE", expected_context=self.context,
            expected_format=self.format), "SCALAR_FORM")
        # Gültige Caller-Typform, aber falsches Commithex: späte Actual-Form geht vor.
        self.reject(self.match(line, expected_kind="BODY_RELEASE",
            expected_context=semantic_change(self.context, (0,), "nothex"),
            expected_format=self.format), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_provider_pre_without_changed_constructor_execution(self):
        with patch.dict(self.run.cache, {"hashlib": Foreign()}):
            self.reject(self.digest(self.context, expected_format=self.format), "HASH_PROVIDER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_provider_call_failure_private_and_dominant_post(self):
        self.provider._HASH_ERROR = RuntimeError("PRIVATE_PAYLOAD")
        self.reject(self.digest(self.context, expected_format=self.format), "HASH_PROVIDER_CALL")
        def drift():
            self.run.cache["hashlib"] = Foreign()
        self.provider._HASH_CALLBACK = drift
        self.reject(self.encode("BODY_RELEASE", self.context, expected_format=self.format),
                    "HASH_PROVIDER_BINDING")

    def test_bad_hash_result_has_no_partial_command(self):
        for value in (None, Foreign(), "A" * 64):
            if value is None:
                self.provider._HASH_RESULT = "short"
            else:
                self.provider._HASH_RESULT = value
            self.reject(self.encode("BODY_RELEASE", self.context, expected_format=self.format))

    def test_encoder_pre_rejects_foreign_without_provider_call(self):
        with patch.object(json, "JSONEncoder", Foreign()):
            self.reject(self.digest(self.context, expected_format=self.format), "REPORT_ENCODER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_encoder_constructor_instance_shadow_never_called(self):
        cls, old = json.JSONEncoder, json.JSONEncoder.__init__
        namespace = self.real_encoder_module.__dict__
        keys = ("_REPORT_HELD_INIT", "_REPORT_SHADOW")
        self.assertTrue(all(key not in namespace for key in keys))
        calls = []
        def shadow(value):
            calls.append(value)
            return ("PRIVATE_PAYLOAD",)
        namespace.update(_REPORT_HELD_INIT=old, _REPORT_SHADOW=shadow)
        try:
            cls.__init__ = FunctionType(_fixture_report_encoder_instance_shadow.__code__, namespace)
            self.reject(self.digest(self.context, expected_format=self.format), "REPORT_ENCODER_BINDING")
        finally:
            cls.__init__ = old
            for key in keys:
                del namespace[key]
        self.assertEqual(calls, [])
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_encoder_callback_provider_drift_before_hash_constructor(self):
        cls, old_code = json.JSONEncoder, self.factory.__code__
        held_iter = cls.iterencode
        namespace = self.real_encoder_module.__dict__
        keys = ("_REPORT_FACTORY", "_REPORT_REPLACEMENT_CODE", "_REPORT_HELD_ITER")
        self.assertTrue(all(key not in namespace for key in keys))
        namespace.update(_REPORT_FACTORY=self.factory, _REPORT_REPLACEMENT_CODE=_fixture_config_var.__code__,
                         _REPORT_HELD_ITER=held_iter)
        try:
            cls.iterencode = FunctionType(_fixture_report_encoder_exchange_provider.__code__, namespace)
            self.reject(self.digest(self.context, expected_format=self.format), "HASH_PROVIDER_BINDING")
        finally:
            cls.iterencode = held_iter
            self.factory.__code__ = old_code
            for key in keys:
                del namespace[key]
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_encoder_post_on_failed_hash_and_provider_higher_priority(self):
        original = json.JSONEncoder.default
        replacement = FunctionType(original.__code__, original.__globals__, "default")
        def drift():
            json.JSONEncoder.default = replacement
            self.provider._HASH_ERROR = RuntimeError("PRIVATE_PAYLOAD")
        try:
            self.provider._HASH_CALLBACK = drift
            self.reject(self.digest(self.context, expected_format=self.format), "REPORT_ENCODER_BINDING")
            json.JSONEncoder.default = original
            def both():
                drift()
                self.run.cache["hashlib"] = Foreign()
            self.provider._HASH_CALLBACK = both
            self.reject(self.digest(self.context, expected_format=self.format), "HASH_PROVIDER_BINDING")
        finally:
            json.JSONEncoder.default = original

    def test_encoder_error_post_and_no_raw_exception_context(self):
        def failing(*args):
            raise OSError("PRIVATE_PAYLOAD")
        try:
            raise ValueError("PRIVATE_PAYLOAD")
        except ValueError:
            with patch.dict(self.namespace, {"_command_k_json": failing}):
                self.reject(self.digest(self.context, expected_format=self.format), "COMMAND_INTERNAL")

    def test_encoding_hash_counts_no_original_digest_or_m_parser(self):
        calls = []
        original = self.namespace["_report_json"]
        def counted(form, anchor):
            calls.append(form)
            return original(form, anchor)
        with patch.dict(self.namespace, {"_report_json": counted, "_semantic_inputs": Foreign(),
                        "_semantic_original_digest": Foreign(), "_inline_metadata_syntax": Foreign()}):
            self.assertEqual(self.digest(self.context, expected_format=self.format)[0], "FORMATTED_CONTEXT_DIGEST")
            self.assertEqual(len(calls), 1)
            calls.clear()
            encoded = self.encode("BODY_RELEASE", self.context, expected_format=self.format)
            self.assertEqual(encoded[0], "FORMATTED_BOUND_COMMAND")
            self.assertEqual(len(calls), 2)
            calls.clear()
            self.assertEqual(self.match(encoded[2], expected_kind="BODY_RELEASE", expected_context=self.context,
                expected_format=self.format)[0], "MATCHED_DECLARED_COMMAND")
            self.assertEqual(len(calls), 2)
        self.assertEqual(self.provider._HASH_CALLS, 3)

    def test_k_cap_honestly_small_valid_form_and_internal_counter_guard(self):
        _, data, _ = self.reference(self.context)
        self.assertLess(len(data) + 16, 16384)
        # Feste K-Schemawerte tragen keine frei wählbaren langen Locatorfelder.
        with patch.dict(self.namespace, {"_INLINE_METADATA_CAP": len(data) + 16}):
            self.assertEqual(self.digest(self.context, expected_format=self.format)[0], "FORMATTED_CONTEXT_DIGEST")
        with patch.dict(self.namespace, {"_INLINE_METADATA_CAP": len(data) + 15}):
            self.reject(self.digest(self.context, expected_format=self.format), "METADATA_LIMIT")

    def test_internal_pool_node_and_depth_guards_no_cap_promotion(self):
        # Bekannter vollständiger K-Packer; künstlich abgesenkte interne Limits.
        for key, value, issue in (("_INLINE_NODES", 4, "NODE_LIMIT"),
                                 ("_INLINE_DEPTH", 1, "DEPTH_LIMIT")):
            with patch.dict(self.namespace, {key: value}):
                self.reject(self.digest(self.context, expected_format=self.format), issue)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_repeat_match_has_no_consumption_or_release_transition(self):
        line = self.line(kind="IMPORT_RELEASE")
        results = tuple(self.match(line, expected_kind="IMPORT_RELEASE", expected_context=self.context,
            expected_format=self.format) for _ in range(2))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0][0], "MATCHED_DECLARED_COMMAND")
        self.assertEqual(self.provider._HASH_CALLS, 2)

    def test_six_old_builders_and_all_definition_bytes_unchanged(self):
        sixth = subject.build_inline_receive_control_bootstrap(RAW, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(self.selected.source.replace(("\n" + subject._INLINE_COMMAND).encode(), b"", 1),
                         sixth.source)
        before, after = ast.parse(sixth.source), ast.parse(self.selected.source)
        definitions = {n.name: ast.dump(n) for n in after.body if type(n) in (ast.FunctionDef, ast.ClassDef)}
        self.assertTrue(all(definitions[n.name] == ast.dump(n) for n in before.body
                           if type(n) in (ast.FunctionDef, ast.ClassDef)))

    def test_source_imports_claims_and_no_channel_candidate_io(self):
        tree = ast.parse(self.selected.source)
        self.assertEqual([n.names[0].name for n in tree.body if type(n) is ast.Import],
                         ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(n) is ast.ImportFrom for n in ast.walk(tree)))
        helpers = ast.parse(subject._INLINE_COMMAND)
        forbidden = {"read", "write", "open", "print", "input", "exec", "compile", "Popen",
                     "observe_current_interpreter_scalars", "prepare_input"}
        self.assertFalse(any(type(n) is ast.Call and (type(n.func) is ast.Name and n.func.id in forbidden
            or type(n.func) is ast.Attribute and n.func.attr in forbidden) for n in ast.walk(helpers)))
        self.assertEqual(self.selected.claim, "GENERATED_CONTROL_SOURCE_ONLY")
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertFalse(getattr(self.selected, key))

    def test_full_generated_script_cap_and_private_failure(self):
        base = subject.build_inline_command_control_bootstrap(b"x", logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        raw = b"x" * (subject.MAX_SCRIPT_BYTES - len(base.source) + 1)
        selected = subject.build_inline_command_control_bootstrap(raw, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(len(selected.source), subject.MAX_SCRIPT_BYTES)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_inline_command_control_bootstrap(raw + b"x", logical_profile=LOCATOR,
                expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertNotIn(LOCATOR, repr(selected))


class InlineMetadataMatchTests(unittest.TestCase):
    def setUp(self):
        # Neue Route, aber derselbe ausdrücklich getrennte synthetische Provider.
        self.real_cache = sys.modules
        self.real_names = (NAME, "__main__", "sysconfig", "json", "json.encoder", "_hashlib")
        self.real_values = tuple(sys.modules.get(name, _REPORT_OMITTED) for name in self.real_names)
        self.real_main_name = sys.modules["__main__"].__name__
        self.real_encoder = json.JSONEncoder
        self.real_encoder_namespace = tuple(sorted(self.real_encoder.__dict__.items()))
        self.real_json_namespace = tuple(sorted(json.__dict__.items()))
        self.real_encoder_module = sys.modules["json.encoder"]
        self.real_encoder_module_namespace = tuple(sorted(self.real_encoder_module.__dict__.items()))
        self.real_encoder_functions = tuple(self.real_encoder.__dict__[key]
                                           for key in ("__init__", "iterencode", "default"))
        self.real_encoder_states = tuple((fn.__code__, fn.__defaults__, fn.__kwdefaults__,
            None if fn.__kwdefaults__ is None else tuple(sorted(fn.__kwdefaults__.items())))
            for fn in self.real_encoder_functions)
        loader = SourceFileLoader("hashlib", "/synthetic/stdlib/hashlib.py")
        spec = ModuleSpec("hashlib", loader, origin=loader.path)
        spec._set_fileattr = True
        spec._cached = "/synthetic/stdlib/__pycache__/hashlib.cpython-312.pyc"
        self.provider = importlib.util.module_from_spec(spec)
        path = "/synthetic/stdlib/lib-dynload/_hashlib.so"
        native_loader = ExtensionFileLoader("_hashlib", path)
        native_spec = ModuleSpec("_hashlib", native_loader, origin=path)
        native_spec._set_fileattr = True
        self.native = ModuleType("_hashlib")
        self.native.__dict__.update(__file__=path, __package__="", __spec__=native_spec,
            __loader__=native_loader, __cached__=None, HASH=hashlib.__dict__["_hashlib"].HASH,
            openssl_sha256=hashlib.sha256)
        self.provider.__dict__.update(_hashlib=self.native, _NATIVE_SHA=hashlib.sha256,
            _HASH_CALLS=0, _HASH_CALLBACK=None, _HASH_ERROR=None, _HASH_RESULT=None)
        self.factory = FunctionType(_fixture_sha256.__code__, self.provider.__dict__, "sha256")
        self.provider.sha256 = self.factory
        def bind_provider(run):
            run.cache[NAME].hashlib = self.provider
            run.cache[NAME].ExtensionFileLoader = ExtensionFileLoader
            run.cache.update(hashlib=self.provider, _hashlib=self.native,
                             json=json, **{"json.encoder": sys.modules["json.encoder"]})
        self.selected = subject.build_inline_match_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True, after_exec=bind_provider)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.match = self.namespace["_inline_match_metadata_chunks"]
        self.payload = semantic_fixture()
        self.format = "pooled-combined-input-design/v1"

    def tearDown(self):
        InlineProfileReporterTests.tearDown(self)

    def packet(self, payload=_REPORT_OMITTED, *, body_size=None):
        payload = self.payload if payload is _REPORT_OMITTED else payload
        return InlineMetadataSemanticsTests.packet(self, payload, body_size=body_size)

    def chunks(self, data, size=1024):
        return tuple(data[n:n + size] for n in range(0, len(data), size))

    def call(self, *, actual=_REPORT_OMITTED, expected=_REPORT_OMITTED,
             chunks=_REPORT_OMITTED, expected_format=_REPORT_OMITTED):
        actual = self.payload if actual is _REPORT_OMITTED else actual
        expected = self.payload if expected is _REPORT_OMITTED else expected
        if chunks is _REPORT_OMITTED:
            header, metadata = self.packet(actual)
            chunks = self.chunks(header + metadata)
        return self.match(chunks, expected_format=self.format if expected_format is _REPORT_OMITTED
            else expected_format, expected_input=expected[0], expected_worker=expected[1],
            expected_context=expected[2])

    def reject(self, result, issue=None):
        self.assertEqual(result[0], "REJECTED_DECLARED_METADATA")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("PRIVATE_PAYLOAD", repr(result))
        self.assertNotIn("/synthetic", repr(result))
        return result

    def rehashed(self, payload):
        # Benannte unabhängige Originaldarstellung: modules ist ausdrücklich list.
        ip = payload[0]
        named = dict(protocol=ip[0], commit=ip[1], raw27_binding=ip[2], source_profile=ip[3], nonce=ip[4],
            modules=[dict(ordinal=r[0], module=r[1], member=r[2], size=r[3], sha256=r[4]) for r in ip[5]])
        digest = hashlib.sha256(json.dumps(named, sort_keys=True, ensure_ascii=True,
            separators=(",", ":"), allow_nan=False).encode("ascii")).hexdigest()
        return semantic_change(payload, (0, 6), digest)

    def test_full_reference_all_roles_and_three_ordinals_actual_return(self):
        for ordinal in (1, 2, 3):
            payload = semantic_fixture(ordinal)
            header, metadata = self.packet(payload)
            result = self.call(actual=payload, expected=payload)
            self.assertEqual(result, ("MATCHED_DECLARED_METADATA", "NONE", (header, metadata, payload)))
            parsed = syntax_reference._Parser(metadata)
            form = parsed.value()
            self.assertEqual(syntax_reference._resolve(form, 0), payload)
            ip, worker, context = syntax_reference._semantics(payload, 0)
            self.assertEqual(ip, payload[0])
            self.assertEqual(tuple((r.ordinal, r.module, r.member, r.size, r.sha256) for r in context.modules), payload[2][4])
            self.assertEqual(tuple(getattr(worker.installation, name) for name in (
                "assumption", "platform", "implementation", "version", "executable", "executable_target",
                "prefixes", "abi", "paths", "roots", "inert_zip", "flags", "finders", "hooks")), payload[1][3][:14])
            self.assertEqual(tuple((r.path, r.size, r.sha256) for r in worker.installation.files), payload[1][3][14])
            self.assertEqual(tuple(tuple(getattr(r, name) for name in (
                "name", "moduleName", "specName", "origin", "file", "kind", "locations", "loader",
                "loaderName", "loaderPath", "aliasGroup")) for r in worker.modules), payload[1][5])
            self.assertEqual(worker.controls, payload[1][4])
            self.assertEqual((context.ordinal, context.entry, context.phase), payload[2][5:])

    def test_actual_private_bytes_and_payload_are_not_expected_defaults(self):
        expected = tuple(tuple(row) for row in self.payload)
        header, metadata = self.packet()
        result = self.call(expected=expected, chunks=(header,) + self.chunks(metadata))
        self.assertEqual(result[0], "MATCHED_DECLARED_METADATA")
        self.assertEqual(result[2], (header, metadata, expected))
        self.assertIsNot(result[2][2], expected)
        self.assertIsNot(result[2][2][1], expected[1])

    def test_valid_installation_and_complete_p11_differences_remain_mismatch(self):
        for path, value in (((1, 3, 7), "another-abi"), ((1, 3, 6, 3), "/other-prefix"),
                            ((1, 3, 14, 0, 1), 1), ((1, 3, 14, 0, 2), "a" * 64),
                            ((1, 5, 0, 4), "/other-main.py")):
            changed = semantic_change(self.payload, path, value)
            self.reject(self.call(actual=changed), "METADATA_DECLARATION_MISMATCH")
            self.reject(self.call(expected=changed), "METADATA_DECLARATION_MISMATCH")

    def test_two_independent_valid_original_preimages_both_hashed(self):
        changed = self.payload
        for ip_index, k_index, value in ((1, 0, "a" * 40), (2, 1, "b" * 64), (4, 3, "c" * 64)):
            changed = semantic_change(changed, (0, ip_index), value)
            changed = semantic_change(changed, (2, k_index), value)
        changed = self.rehashed(changed)
        self.assertNotEqual(changed[0][6], self.payload[0][6])
        self.reject(self.call(actual=changed), "METADATA_DECLARATION_MISMATCH")
        self.assertEqual(self.provider._HASH_CALLS, 2)
        self.assertEqual(self.call(actual=changed, expected=changed)[0], "MATCHED_DECLARED_METADATA")

    def test_both_complete_d9_arrays_change_and_are_retained(self):
        rows = tuple(r[:3] + (r[3] + 1, "d" * 64) for r in self.payload[0][5])
        changed = semantic_change(self.payload, (0, 5), rows)
        changed = self.rehashed(semantic_change(changed, (2, 4), rows))
        self.reject(self.call(actual=changed), "METADATA_DECLARATION_MISMATCH")
        self.assertEqual(self.call(actual=changed, expected=changed)[2][2], changed)

    def test_format_first_without_foreign_dispatch(self):
        for value in (None, True, Foreign(), ForeignKey(self.format), "other"):
            self.reject(self.match(Foreign(), expected_format=value, expected_input=Foreign(),
                expected_worker=Foreign(), expected_context=Foreign()), "FORMAT_SELECTION")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_chunk_types_precede_expected_forms_and_lengths(self):
        for chunks in (None, [], Foreign(), (b"x" * 1025, Foreign())):
            self.reject(self.call(chunks=chunks, expected=(Foreign(), Foreign(), Foreign())))
        class Bytes(bytes):
            def __len__(self):
                raise AssertionError("FOREIGN_LENGTH")
        self.reject(self.call(chunks=(Bytes(b"x"),)), "CHUNK_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_all_expected_primitive_fields_before_actual_parse_or_hash(self):
        with patch.dict(self.namespace, {"_InlineParser": Foreign()}):
            for path, value in (((0,), None), ((1,), []), ((2,), Foreign()),
                                ((1, 3, 14, 0, 2), Foreign()), ((2, 4, 8, 4), True)):
                self.reject(self.call(expected=semantic_change(self.payload, path, value)), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_expected_subclasses_bool_and_foreign_getters_closed(self):
        class TupleSubclass(tuple):
            def __iter__(self):
                raise AssertionError("FOREIGN_ITERATOR")
        class TextSubclass(str):
            def __eq__(self, other):
                raise AssertionError("FOREIGN_EQUALITY")
        class IntSubclass(int):
            pass
        for path, value in (((0,), TupleSubclass(self.payload[0])),
            ((1, 3, 7), TextSubclass(SOABI)), ((1, 0), True), ((2, 5), IntSubclass(1)),
            ((1, 5, 2, 4), Foreign())):
            self.reject(self.call(expected=semantic_change(self.payload, path, value)), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_both_sides_identical_invalid_late_descriptor_never_match(self):
        for path, value in (((0, 5, 8, 2), "wrong.py"), ((2, 4, 8, 4), "A" * 64),
                            ((1, 3, 14, 0, 0), "/foreign/executable")):
            bad = semantic_change(self.payload, path, value)
            self.reject(self.call(actual=bad, expected=bad))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_expected_malformed_dominates_early_valid_difference(self):
        early = semantic_change(self.payload, (1, 3, 7), "valid-other-abi")
        for path in ((1, 5, 2, 10), (1, 3, 14, 0, 2), (2, 4, 8, 4)):
            changed = semantic_change(early, path, Foreign())
            self.reject(self.call(expected=changed), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_actual_form_dominates_early_expected_semantic_error(self):
        expected = semantic_change(self.payload, (0, 1), "nothex")
        for path in ((1, 5, 2, 10), (1, 3, 14, 0, 2), (2, 4, 8, 4)):
            actual = semantic_change(self.payload, path, None)
            self.reject(self.call(actual=actual, expected=expected))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_actual_module_semantics_before_early_valid_mismatch(self):
        expected = semantic_change(self.payload, (1, 3, 7), "valid-other-abi")
        actual = semantic_change(self.payload, (1, 5, 2, 7), "SOURCE")
        with patch.dict(self.namespace, {"_report_json": Foreign()}):
            self.reject(self.call(actual=actual, expected=expected), "MODULE_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_expected_semantics_before_first_repack_or_digest(self):
        for path, value in (((1, 3, 14, 0, 2), "A" * 64), ((2, 4, 8, 1), "wrong")):
            with patch.dict(self.namespace, {"_report_json": Foreign()}):
                self.reject(self.call(expected=semantic_change(self.payload, path, value)))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_identical_invalid_roots_loader_controls_and_cached_candidates_reject(self):
        cases = (((1, 3, 9, 0), "/synthetic/stdlib/../escape"),
                 ((1, 5, 1, 9), "/wrong/profile.py"),
                 ((1, 4), ("__main__",)), ((1, 5, 2, 0), "Tests"))
        for path, value in cases:
            changed = semantic_change(self.payload, path, value)
            self.reject(self.call(actual=changed, expected=changed))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_complete_mixed_and_frozen_alias_records_without_live_claim(self):
        file = "/synthetic/stdlib/collections/abc.py"
        mixed = (("_collections_abc", "collections.abc", "_collections_abc", "frozen",
            "/synthetic/stdlib/_collections_abc.py", "FROZEN", (), "FROZEN", "", "", ()),
            ("collections.abc", "collections.abc", "collections.abc", file, file,
             "SOURCE", (), "SOURCE", "collections.abc", file, ()))
        pair = ("_frozen_importlib", "importlib._bootstrap")
        frozen = tuple((name, "importlib._bootstrap", "_frozen_importlib", "frozen", "",
            "FROZEN", (), "FROZEN", "", "", pair) for name in pair)
        changed = semantic_change(self.payload, (1, 5), tuple(sorted(self.payload[1][5] + mixed + frozen)))
        self.assertEqual(self.call(actual=changed, expected=changed)[2][2], changed)
        bad = semantic_change(changed, (1, 5), tuple(r for r in changed[1][5] if r[0] != pair[1]))
        self.reject(self.call(actual=bad, expected=bad), "ALIAS_FORM")

    def test_both_original_digest_failures_are_separate_and_atomic(self):
        bad = semantic_change(self.payload, (0, 6), "0" * 64)
        self.reject(self.call(actual=bad), "INPUT_DIGEST")
        self.assertEqual(self.provider._HASH_CALLS, 2)
        self.reject(self.call(expected=bad), "INPUT_DIGEST")
        self.assertEqual(self.provider._HASH_CALLS, 4)

    def test_intrinsic_i_k_and_worker_selector_before_caller_mismatch(self):
        cases = ((semantic_change(self.payload, (2, 3), "a" * 64), "INPUT_BINDING"),
                 (semantic_change(self.payload, (2,), self.payload[2][:5] + semantic_fixture(2)[2][5:]),
                  "CONTEXT_MISMATCH"))
        for payload, issue in cases:
            self.reject(self.call(actual=payload), issue)
            self.reject(self.call(expected=payload), issue)

    def test_original_sha_is_not_k_domain_or_header_sha(self):
        bad = semantic_change(self.payload, (0, 6), hashlib.sha256(
            syntax_bytes(syntax_form(self.payload))).hexdigest())
        self.reject(self.call(actual=bad, expected=bad), "INPUT_DIGEST")

    def test_header_splits_and_leading_trailing_empty_chunks(self):
        header, metadata = self.packet()
        for split in range(17):
            chunks = (b"", header[:split], b"", header[split:]) + self.chunks(metadata) + (b"",)
            self.assertEqual(self.call(chunks=chunks)[2], (header, metadata, self.payload))

    def test_chunk_256_257_and_chunk_1024_1025_limits(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        exact = (b"",) * (255 - len(chunks)) + chunks + (b"",)
        self.assertEqual(len(exact), 256)
        self.assertEqual(self.call(chunks=exact)[0], "MATCHED_DECLARED_METADATA")
        self.reject(self.call(chunks=exact + (b"",)), "CHUNKS_LIMIT")
        with patch.dict(self.namespace, {"_InlineParser": Foreign()}):
            self.reject(self.call(chunks=(b"x" * 1025,)), "CHUNK_LIMIT")
        self.assertTrue(all(len(c) <= 1024 for c in chunks))

    def test_declared_positive_body_is_not_received_and_no_suffix_permitted(self):
        header, metadata = self.packet()
        self.assertGreater(struct.unpack(">8sII", header)[2], 0)
        for suffix in (b"x", b"\n", b'["BODY_RELEASE"]\n'):
            self.reject(self.call(chunks=self.chunks(header + metadata + suffix)), "METADATA_LENGTH")
        for data in (header[:15], header + metadata[:-1]):
            self.reject(self.call(chunks=self.chunks(data)))

    def test_header_errors_preparser_and_actual_body_sum_only(self):
        header, metadata = self.packet()
        with patch.dict(self.namespace, {"_InlineParser": Foreign()}):
            for magic, size, body in ((b"DGNP001\0", len(metadata), 0),
                (b"DGNC001\0", 16369, 0), (b"DGNC001\0", len(metadata), 1048577)):
                self.reject(self.call(chunks=self.chunks(struct.pack(">8sII", magic, size, body) + metadata)))
        wrong, metadata = self.packet(body_size=0)
        self.reject(self.call(chunks=self.chunks(wrong + metadata)), "DECLARED_BODY_LENGTH")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_valid_total_16384_and_16385_preparser(self):
        initial = semantic_change(self.payload, (1, 3, 7), "x")
        for count in range(3, 6):
            locations = tuple("/synthetic/stdlib/" + chr(97 + n) * 3900 for n in range(count))
            path = "/synthetic/stdlib/source.py"
            source = ("source", "source", "source", path, path, "SOURCE", locations,
                      "SOURCE", "source", path, ())
            candidate = semantic_change(initial, (1, 5), tuple(sorted(initial[1][5] + (source,))))
            header, metadata = self.packet(candidate)
            padding = 16384 - 16 - len(metadata)
            if 0 <= padding <= 4095:
                candidate = semantic_change(candidate, (1, 3, 7), "x" * (padding + 1))
                header, metadata = self.packet(candidate)
                self.assertEqual(len(header + metadata), 16384)
                self.assertEqual(self.call(actual=candidate, expected=candidate)[0], "MATCHED_DECLARED_METADATA")
                over = semantic_change(candidate, (1, 3, 7), "x" * (padding + 2))
                header, metadata = self.packet(over)
                self.assertEqual(len(header + metadata), 16385)
                with patch.dict(self.namespace, {"_InlineParser": Foreign()}):
                    self.reject(self.call(expected=over, chunks=self.chunks(header + metadata)), "METADATA_LIMIT")
                return
        self.fail("Keine gültige synthetische Metadata-Grenzfixture")

    def test_exact_unicode_and_noncanonical_repack_before_sha(self):
        payload = semantic_change(self.payload, (1, 3, 7), 'ABI|é😀"\\')
        self.assertEqual(self.call(actual=payload, expected=payload)[2][2], payload)
        self.provider._HASH_CALLS = 0
        header, metadata = self.packet()
        changed = metadata.replace(b"pooled-binding", b"\\u0070ooled-binding", 1)
        header = struct.pack(">8sII", b"DGNC001\0", len(changed), sum(r[3] for r in self.payload[0][5]))
        self.reject(self.call(chunks=self.chunks(header + changed)), "NONCANONICAL")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_m_repack_provider_drift_prevents_changed_constructor(self):
        header, metadata = self.packet()
        held_chunks = self.chunks(header + metadata)
        cls, original = json.JSONEncoder, json.JSONEncoder.iterencode
        old_code = self.factory.__code__
        namespace = self.real_encoder_module.__dict__
        keys = ("_REPORT_FACTORY", "_REPORT_REPLACEMENT_CODE", "_REPORT_HELD_ITER")
        self.assertTrue(all(k not in namespace for k in keys))
        namespace.update(_REPORT_FACTORY=self.factory, _REPORT_REPLACEMENT_CODE=_fixture_config_var.__code__,
                         _REPORT_HELD_ITER=original)
        try:
            cls.iterencode = FunctionType(_fixture_report_encoder_exchange_provider.__code__, namespace)
            self.reject(self.call(chunks=held_chunks), "HASH_PROVIDER_BINDING")
        finally:
            cls.iterencode = original
            self.factory.__code__ = old_code
            for k in keys:
                del namespace[k]
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_m_repack_encoder_drift_has_no_digest(self):
        original = self.namespace["_report_json"]
        def drift(form, anchor):
            result = original(form, anchor)
            self.run.cache["json.encoder"] = Foreign()
            return result
        with patch.dict(self.namespace, {"_report_json": drift}):
            self.reject(self.call(), "REPORT_ENCODER_BINDING")
        # Der erste Original-Encoder-PRE scheitert vor dem ersten SHA.
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_first_and_second_hash_provider_drift_dominates_failure(self):
        for number in (1, 2):
            self.provider._HASH_CALLS = 0
            def drift():
                if self.provider._HASH_CALLS == number:
                    self.run.cache["hashlib"] = Foreign()
                    self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
            self.provider._HASH_CALLBACK = drift
            with patch.dict(self.run.cache, {"hashlib": self.provider}):
                self.reject(self.call(), "HASH_PROVIDER_BINDING")
            self.provider._HASH_ERROR = None
            self.assertEqual(self.provider._HASH_CALLS, number)

    def test_first_and_second_hash_encoder_post_on_call_failure(self):
        for number in (1, 2):
            self.provider._HASH_CALLS = 0
            def drift():
                if self.provider._HASH_CALLS == number:
                    self.run.cache["json.encoder"] = Foreign()
                    self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
            self.provider._HASH_CALLBACK = drift
            with patch.dict(self.run.cache, {"json.encoder": self.real_encoder_module}):
                self.reject(self.call(), "REPORT_ENCODER_BINDING")
            self.provider._HASH_ERROR = None
            self.assertEqual(self.provider._HASH_CALLS, number)

    def test_provider_and_encoder_pre_fixed_labels(self):
        header, metadata = self.packet()
        held_chunks = self.chunks(header + metadata)
        with patch.dict(self.run.cache, {"hashlib": Foreign()}):
            self.reject(self.call(chunks=held_chunks), "HASH_PROVIDER_BINDING")
        with patch.object(json, "JSONEncoder", Foreign()):
            self.reject(self.call(chunks=held_chunks), "REPORT_ENCODER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_exact_cost_one_parser_three_encodings_two_original_hashes(self):
        events, encodings = [], []
        parser, encode = self.namespace["_InlineParser"], self.namespace["_report_json"]
        def parse(data):
            events.append(data)
            return parser(data)
        def record(form, anchor):
            encodings.append(form)
            return encode(form, anchor)
        with patch.dict(self.namespace, {"_InlineParser": parse, "_report_json": record,
            "_inline_metadata_syntax": Foreign(), "_inline_receive_metadata_chunks": Foreign(),
            "_inline_metadata_semantics": Foreign(), "_semantic_original_digest": Foreign()}):
            self.assertEqual(self.call()[0], "MATCHED_DECLARED_METADATA")
        self.assertEqual(len(events), 1)
        self.assertEqual(len(encodings), 3)
        self.assertEqual(encodings[0], syntax_form(self.payload))
        self.assertEqual(encodings[1], encodings[2])
        self.assertIs(type(encodings[1]["modules"]), list)
        self.assertNotIn("context_sha256", encodings[1])
        self.assertEqual(self.provider._HASH_CALLS, 2)

    def test_private_active_exception_failure_and_repeat_no_consumption(self):
        try:
            raise ValueError("PRIVATE_PAYLOAD")
        except ValueError:
            self.reject(self.call(expected=(None, None, None)), "SCALAR_FORM")
        first, second = self.call(), self.call()
        self.assertEqual(first, second)
        self.assertEqual(first[0], "MATCHED_DECLARED_METADATA")

    def test_seven_legacy_builder_bytes_and_definitions_preserved(self):
        previous = subject.build_inline_command_control_bootstrap(RAW, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(self.selected.source.replace(("\n" + subject._INLINE_MATCH).encode(), b"", 1), previous.source)
        old, new = ast.parse(previous.source), ast.parse(self.selected.source)
        definitions = {n.name: ast.dump(n) for n in new.body if type(n) in (ast.FunctionDef, ast.ClassDef)}
        self.assertTrue(all(definitions[n.name] == ast.dump(n) for n in old.body
            if type(n) in (ast.FunctionDef, ast.ClassDef)))
        self.assertEqual([n.names[0].name for n in new.body if type(n) is ast.Import],
                         ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(n) is ast.ImportFrom for n in ast.walk(new)))

    def test_full_script_cap_and_false_claims(self):
        base = subject.build_inline_match_control_bootstrap(b"x", logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        raw = b"x" * (subject.MAX_SCRIPT_BYTES - len(base.source) + 1)
        selected = subject.build_inline_match_control_bootstrap(raw, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(len(selected.source), subject.MAX_SCRIPT_BYTES)
        with self.assertRaises(subject.BootstrapSourceRejected) as caught:
            subject.build_inline_match_control_bootstrap(raw + b"x", logical_profile=LOCATOR,
                expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertNotIn(LOCATOR, repr(selected))
        self.assertEqual(selected.claim, "GENERATED_CONTROL_SOURCE_ONLY")
        for key in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertFalse(getattr(selected, key))


class InlineBodyReceiveTests(unittest.TestCase):
    def setUp(self):
        # Neue Route, aber derselbe ausdrücklich getrennte synthetische Provider.
        self.real_cache = sys.modules
        self.real_names = (NAME, "__main__", "sysconfig", "json", "json.encoder", "_hashlib")
        self.real_values = tuple(sys.modules.get(name, _REPORT_OMITTED) for name in self.real_names)
        self.real_main_name = sys.modules["__main__"].__name__
        self.real_encoder = json.JSONEncoder
        self.real_encoder_namespace = tuple(sorted(self.real_encoder.__dict__.items()))
        self.real_json_namespace = tuple(sorted(json.__dict__.items()))
        self.real_encoder_module = sys.modules["json.encoder"]
        self.real_encoder_module_namespace = tuple(sorted(self.real_encoder_module.__dict__.items()))
        self.real_encoder_functions = tuple(self.real_encoder.__dict__[key]
                                           for key in ("__init__", "iterencode", "default"))
        self.real_encoder_states = tuple((fn.__code__, fn.__defaults__, fn.__kwdefaults__,
            None if fn.__kwdefaults__ is None else tuple(sorted(fn.__kwdefaults__.items())))
            for fn in self.real_encoder_functions)
        loader = SourceFileLoader("hashlib", "/synthetic/stdlib/hashlib.py")
        spec = ModuleSpec("hashlib", loader, origin=loader.path)
        spec._set_fileattr = True
        spec._cached = "/synthetic/stdlib/__pycache__/hashlib.cpython-312.pyc"
        self.provider = importlib.util.module_from_spec(spec)
        path = "/synthetic/stdlib/lib-dynload/_hashlib.so"
        native_loader = ExtensionFileLoader("_hashlib", path)
        native_spec = ModuleSpec("_hashlib", native_loader, origin=path)
        native_spec._set_fileattr = True
        self.native = ModuleType("_hashlib")
        self.native.__dict__.update(__file__=path, __package__="", __spec__=native_spec,
            __loader__=native_loader, __cached__=None, HASH=hashlib.__dict__["_hashlib"].HASH,
            openssl_sha256=hashlib.sha256)
        self.provider.__dict__.update(_hashlib=self.native, _NATIVE_SHA=hashlib.sha256,
            _HASH_CALLS=0, _HASH_CALLBACK=None, _HASH_ERROR=None, _HASH_RESULT=None)
        self.factory = FunctionType(_fixture_sha256.__code__, self.provider.__dict__, "sha256")
        self.provider.sha256 = self.factory
        def bind_provider(run):
            run.cache[NAME].hashlib = self.provider
            run.cache[NAME].ExtensionFileLoader = ExtensionFileLoader
            run.cache.update(hashlib=self.provider, _hashlib=self.native,
                             json=json, **{"json.encoder": sys.modules["json.encoder"]})
        self.selected = subject.build_inline_body_control_bootstrap(
            RAW, logical_profile=LOCATOR, expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.run = Run(config=True, after_exec=bind_provider)
        self.assertEqual(self.run.execute(self.selected)[:2], ("LOADED_BOUND_CONTROL_SOURCE", "NONE"))
        self.namespace = self.run.main_namespace
        self.receive = self.namespace["_inline_receive_declared_bodies"]
        self.payload = semantic_fixture()
        self.bodies = tuple(b"synthetic-source-" + str(n).encode("ascii") for n in range(9))
        self.format = "pooled-combined-input-design/v1"

    tearDown = InlineMetadataMatchTests.tearDown
    packet = InlineMetadataMatchTests.packet
    chunks = InlineMetadataMatchTests.chunks
    rehashed = InlineMetadataMatchTests.rehashed

    def data(self, ordinal=1, bodies=_REPORT_OMITTED):
        bodies = self.bodies if bodies is _REPORT_OMITTED else bodies
        payload = semantic_fixture(ordinal)
        rows = tuple(r[:3] + (len(raw), hashlib.sha256(raw).hexdigest())
                     for r, raw in zip(payload[0][5], bodies))
        payload = semantic_change(payload, (0, 5), rows)
        payload = self.rehashed(semantic_change(payload, (2, 4), rows))
        return payload, bodies

    def call(self, *, actual=_REPORT_OMITTED, expected=_REPORT_OMITTED,
             bodies=_REPORT_OMITTED, chunks=_REPORT_OMITTED, expected_format=_REPORT_OMITTED):
        actual = self.payload if actual is _REPORT_OMITTED else actual
        expected = self.payload if expected is _REPORT_OMITTED else expected
        bodies = self.bodies if bodies is _REPORT_OMITTED else bodies
        if chunks is _REPORT_OMITTED:
            header, metadata = self.packet(actual)
            chunks = self.chunks(header + metadata)
        return self.receive(chunks, bodies,
            expected_format=self.format if expected_format is _REPORT_OMITTED else expected_format,
            expected_input=expected[0], expected_worker=expected[1], expected_context=expected[2])

    def reject(self, result, issue=None):
        self.assertEqual(result[0], "REJECTED_DECLARED_BODIES")
        self.assertIsNone(result[2])
        if issue is not None:
            self.assertEqual(result[1], issue)
        self.assertNotIn("PRIVATE_PAYLOAD", repr(result))
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_three_ordinals_full_independent_original_and_raw_oracle(self):
        for ordinal in (1, 2, 3):
            payload, bodies = self.data(ordinal)
            header, metadata = self.packet(payload)
            result = self.call(actual=payload, expected=payload, bodies=bodies)
            self.assertEqual(result, ("RECEIVED_DECLARED_BODIES", "NONE", (header, metadata, payload, bodies)))
            self.assertIs(result[2][3], bodies)
            self.assertIsNot(result[2][2], payload)
            parser = syntax_reference._Parser(metadata)
            self.assertEqual(syntax_reference._resolve(parser.value(), 0), payload)
            syntax_reference._semantics(payload, 0)
            self.assertEqual(self.rehashed(payload)[0][6], payload[0][6])
            for n, raw in enumerate(bodies):
                self.assertIs(result[2][3][n], raw)
                for rows in (result[2][2][0][5], result[2][2][2][4]):
                    self.assertEqual(rows[n][3:], (len(raw), hashlib.sha256(raw).hexdigest()))
        self.assertEqual(self.provider._HASH_CALLS, 33)

    def test_nine_empty_original_objects_and_zero_body_header(self):
        payload, bodies = self.data(bodies=(b"",) * 9)
        result = self.call(actual=payload, expected=payload, bodies=bodies)
        self.assertEqual(result[0], "RECEIVED_DECLARED_BODIES")
        self.assertEqual(struct.unpack(">8sII", result[2][0])[2], 0)
        self.assertIs(result[2][3], bodies)
        self.assertEqual(self.provider._HASH_CALLS, 11)

    def test_crlf_bom_nul_and_non_utf8_are_opaque(self):
        bodies = (b"line\r\n", b"line\n", b"\xef\xbb\xbftext", b"\0", b"\xff\xfe", b"\r", b"\n", b"", b"a\0b")
        payload, bodies = self.data(bodies=bodies)
        result = self.call(actual=payload, expected=payload, bodies=bodies)
        self.assertEqual(result[0], "RECEIVED_DECLARED_BODIES")
        self.assertIs(result[2][3], bodies)
        self.assertNotEqual(payload[0][5][0][4], payload[0][5][1][4])

    def test_member_exact_131072_and_plus_one_before_hash(self):
        bodies = (b"a" * 131072,) + (b"",) * 8
        payload, bodies = self.data(bodies=bodies)
        self.assertEqual(self.call(actual=payload, expected=payload, bodies=bodies)[0], "RECEIVED_DECLARED_BODIES")
        self.provider._HASH_CALLS = 0
        self.reject(self.call(actual=payload, expected=payload, bodies=(bodies[0] + b"a",) + bodies[1:]), "MEMBER_LIMIT")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_total_exact_1048576_and_plus_one_before_hash(self):
        bodies = (b"a" * 131072,) * 8 + (b"",)
        payload, bodies = self.data(bodies=bodies)
        self.assertEqual(sum(map(len, bodies)), 1048576)
        result = self.call(actual=payload, expected=payload, bodies=bodies)
        self.assertEqual(result[0], "RECEIVED_DECLARED_BODIES")
        self.assertIs(result[2][3], bodies)
        self.provider._HASH_CALLS = 0
        self.reject(self.call(actual=payload, expected=payload, bodies=bodies[:-1] + (b"x",)), "BODY_LIMIT")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_container_counts_eight_ten_mutable_foreign(self):
        bodies = self.data()[1]
        for value, issue in ((None, "BODIES_TYPE"), ([], "BODIES_TYPE"), (Foreign(), "BODIES_TYPE"),
                             (bodies[:8], "BODIES_COUNT"), (bodies + (b"",), "BODIES_COUNT")):
            self.reject(self.call(bodies=value), issue)
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_all_body_types_before_any_body_length(self):
        class Bytes(bytes):
            def __len__(self):
                raise AssertionError("FOREIGN_LENGTH")
        class Tuple(tuple):
            def __iter__(self):
                raise AssertionError("FOREIGN_ITERATOR")
        for value in (bytearray(b"x"), memoryview(b"x"), Bytes(b"x"), Foreign(), True):
            self.reject(self.call(bodies=(b"x" * 131073,) + (b"",) * 7 + (value,)), "BODY_TYPE")
        self.reject(self.call(bodies=Tuple(self.data()[1])), "BODIES_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_format_before_foreign_bodies_chunks_or_expected(self):
        for value in (None, True, Foreign(), ForeignKey(self.format), "other"):
            self.reject(self.receive(Foreign(), Foreign(), expected_format=value,
                expected_input=Foreign(), expected_worker=Foreign(), expected_context=Foreign()), "FORMAT_SELECTION")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_chunk_foreign_and_limits_before_body_hash(self):
        for chunks in ((b"x" * 1025, Foreign()), (b"x" * 1025,), (b"",) * 257,
                       (b"x" * 1024,) * 16 + (b"x",), (b"",)):
            self.reject(self.call(chunks=chunks))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_expected_form_before_parser_and_body_lengths(self):
        bad = semantic_change(self.payload, (2, 4, 8, 4), Foreign())
        with patch.dict(self.namespace, {"_InlineParser": Foreign()}):
            self.reject(self.call(expected=bad, bodies=(b"x" * 131073,) + (b"",) * 8), "SCALAR_FORM")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_late_actual_form_before_early_valid_caller_difference(self):
        expected = semantic_change(self.payload, (1, 3, 7), "other-abi")
        bad = semantic_change(self.payload, (2, 4, 8, 4), None)
        self.reject(self.call(actual=bad, expected=expected), "POSITION_TYPE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_identical_invalid_module_and_descriptor_never_succeed(self):
        for path, value in (((1, 5, 2, 4), "relative"), ((0, 5, 8, 2), "wrong.py"),
                            ((2, 4, 8, 4), "A" * 64)):
            bad = semantic_change(self.payload, path, value)
            self.reject(self.call(actual=bad, expected=bad))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_both_actual_size_arrays_and_header_total_before_hash(self):
        for path in ((0, 5, 8, 3), (2, 4, 8, 3)):
            bad = semantic_change(self.payload, path, self.payload[0][5][8][3] + 1)
            self.reject(self.call(actual=bad), "DECLARED_BODY_LENGTH")
        rows = tuple(r[:3] + (r[3] + 1, r[4]) if n == 8 else r for n, r in enumerate(self.payload[0][5]))
        bad = semantic_change(semantic_change(self.payload, (0, 5), rows), (2, 4), rows)
        self.reject(self.call(actual=bad), "DECLARED_BODY_LENGTH")
        header, metadata = self.packet(body_size=1)
        self.reject(self.call(chunks=self.chunks(header + metadata)), "DECLARED_BODY_LENGTH")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_individual_actual_sizes_cannot_hide_in_equal_total(self):
        rows = list(self.payload[0][5])
        rows[0] = rows[0][:3] + (rows[0][3] + 1, rows[0][4])
        rows[8] = rows[8][:3] + (rows[8][3] - 1, rows[8][4])
        bad = semantic_change(semantic_change(self.payload, (0, 5), tuple(rows)), (2, 4), tuple(rows))
        self.reject(self.call(actual=bad), "BODY_SIZE")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_mapping_order_and_member_contract_before_hash(self):
        rows = self.payload[0][5]
        for changed in (rows[::-1], (rows[0],) * 9,
                        rows[:-1] + (rows[8][:1] + ("wrongmodule",) + rows[8][2:],)):
            bad = semantic_change(semantic_change(self.payload, (0, 5), changed), (2, 4), changed)
            self.reject(self.call(actual=bad))
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_last_rawhash_precedes_early_valid_caller_mismatch(self):
        expected = semantic_change(self.payload, (1, 3, 7), "other-abi")
        bodies = self.data()[1]
        bodies = bodies[:-1] + (b"X" * len(bodies[8]),)
        self.reject(self.call(expected=expected, bodies=bodies), "BODY_HASH")
        self.assertEqual(self.provider._HASH_CALLS, 11)

    def test_first_rawhash_failure_still_checks_all_nine_hashes(self):
        bodies = self.data()[1]
        bodies = (b"X" * len(bodies[0]),) + bodies[1:]
        self.reject(self.call(bodies=bodies), "BODY_HASH")
        self.assertEqual(self.provider._HASH_CALLS, 11)

    def test_both_actual_hash_arrays_and_intrinsic_original_bindings(self):
        for path in ((0, 5, 8, 4), (2, 4, 8, 4)):
            bad = self.rehashed(semantic_change(self.payload, path, "a" * 64))
            self.reject(self.call(actual=bad), "INPUT_BINDING")
        rows = tuple(r[:4] + ("a" * 64,) if n == 8 else r for n, r in enumerate(self.payload[0][5]))
        bad = self.rehashed(semantic_change(semantic_change(self.payload, (0, 5), rows), (2, 4), rows))
        self.reject(self.call(actual=bad, expected=bad), "BODY_HASH")

    def test_original_digest_and_context_selector_are_not_rawhashes(self):
        for path, value, issue in (((0, 6), "a" * 64, "INPUT_DIGEST"),
                                   ((2, 3), "a" * 64, "INPUT_BINDING"),
                                   ((1, 0), 2, "CONTEXT_FORM")):
            self.reject(self.call(actual=semantic_change(self.payload, path, value)), issue)

    def test_valid_changed_actual_raws_never_fill_expected_fields(self):
        bodies = tuple(b"another-source-" + str(n).encode() for n in range(9))
        payload, bodies = self.data(bodies=bodies)
        self.reject(self.call(actual=payload, bodies=bodies), "METADATA_DECLARATION_MISMATCH")
        self.assertEqual(self.provider._HASH_CALLS, 11)
        self.assertEqual(self.call(actual=payload, expected=payload, bodies=bodies)[0], "RECEIVED_DECLARED_BODIES")

    def test_m_repack_provider_drift_prevents_first_constructor(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        cls, original, old_code = json.JSONEncoder, json.JSONEncoder.iterencode, self.factory.__code__
        namespace = self.real_encoder_module.__dict__
        keys = ("_REPORT_FACTORY", "_REPORT_REPLACEMENT_CODE", "_REPORT_HELD_ITER")
        self.assertTrue(all(k not in namespace for k in keys))
        namespace.update(_REPORT_FACTORY=self.factory, _REPORT_REPLACEMENT_CODE=_fixture_config_var.__code__,
                         _REPORT_HELD_ITER=original)
        try:
            cls.iterencode = FunctionType(_fixture_report_encoder_exchange_provider.__code__, namespace)
            self.reject(self.call(chunks=chunks), "HASH_PROVIDER_BINDING")
        finally:
            cls.iterencode = original
            self.factory.__code__ = old_code
            for key in keys:
                del namespace[key]
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_first_and_last_raw_constructor_drift_and_raise(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        for number in (3, 11):
            self.provider._HASH_CALLS = 0
            def drift():
                if self.provider._HASH_CALLS == number:
                    self.run.cache["hashlib"] = Foreign()
                    self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
            self.provider._HASH_CALLBACK = drift
            with patch.dict(self.run.cache, {"hashlib": self.provider}):
                self.reject(self.call(chunks=chunks), "HASH_PROVIDER_BINDING")
            self.provider._HASH_ERROR = None
            self.assertEqual(self.provider._HASH_CALLS, number)

    def test_encoder_post_and_provider_higher_priority_after_last_raw_error(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        for provider_loss in (False, True):
            self.provider._HASH_CALLS = 0
            def drift():
                if self.provider._HASH_CALLS == 11:
                    self.run.cache["json.encoder"] = Foreign()
                    if provider_loss:
                        self.run.cache["hashlib"] = Foreign()
                    self.provider._HASH_ERROR = RuntimeError("PRIVATE_PAYLOAD")
            self.provider._HASH_CALLBACK = drift
            with patch.dict(self.run.cache, {"hashlib": self.provider, "json.encoder": self.real_encoder_module}):
                self.reject(self.call(chunks=chunks), "HASH_PROVIDER_BINDING" if provider_loss else "REPORT_ENCODER_BINDING")
            self.provider._HASH_ERROR = None

    def test_first_original_hash_drift_dominates_constructor_failure(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        def drift():
            self.run.cache["hashlib"] = Foreign()
            self.provider._HASH_ERROR = OSError("PRIVATE_PAYLOAD")
        self.provider._HASH_CALLBACK = drift
        with patch.dict(self.run.cache, {"hashlib": self.provider}):
            self.reject(self.call(chunks=chunks), "HASH_PROVIDER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 1)

    def test_provider_and_encoder_pre_fixed_labels_no_calls(self):
        header, metadata = self.packet()
        chunks = self.chunks(header + metadata)
        with patch.dict(self.run.cache, {"hashlib": Foreign()}):
            self.reject(self.call(chunks=chunks), "HASH_PROVIDER_BINDING")
        with patch.object(json, "JSONEncoder", Foreign()):
            self.reject(self.call(chunks=chunks), "REPORT_ENCODER_BINDING")
        self.assertEqual(self.provider._HASH_CALLS, 0)

    def test_exact_one_parser_three_json_eleven_sha_no_early_matcher(self):
        events, encodings = [], []
        parser, encode = self.namespace["_InlineParser"], self.namespace["_report_json"]
        def parse(data):
            events.append(data)
            return parser(data)
        def record(form, anchor):
            encodings.append(form)
            return encode(form, anchor)
        with patch.dict(self.namespace, {"_InlineParser": parse, "_report_json": record,
            "_inline_match_metadata_chunks": Foreign(), "_semantic_original_digest": Foreign(),
            "_inline_receive_metadata_chunks": Foreign(), "_inline_metadata_semantics": Foreign()}):
            result = self.call()
        self.assertEqual(result[0], "RECEIVED_DECLARED_BODIES")
        self.assertEqual(len(events), 1)
        self.assertEqual(len(encodings), 3)
        self.assertEqual(encodings[0], syntax_form(self.payload))
        self.assertEqual(encodings[1], encodings[2])
        self.assertIs(type(encodings[1]["modules"]), list)
        self.assertNotIn("context_sha256", encodings[1])
        self.assertEqual(self.provider._HASH_CALLS, 11)

    def test_private_failure_active_context_and_repeat_no_consumption(self):
        try:
            raise RuntimeError("PRIVATE_PAYLOAD")
        except RuntimeError:
            self.reject(self.call(bodies=(None,) * 9), "BODY_TYPE")
        first, second = self.call(), self.call()
        self.assertEqual(first, second)
        self.assertEqual(first[0], "RECEIVED_DECLARED_BODIES")

    def test_eight_old_builders_bytes_definitions_imports_and_false_flags(self):
        previous = subject.build_inline_match_control_bootstrap(RAW, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(self.selected.source.replace(("\n" + subject._INLINE_BODY).encode(), b"", 1), previous.source)
        old, new = ast.parse(previous.source), ast.parse(self.selected.source)
        defs = {n.name: ast.dump(n) for n in new.body if type(n) in (ast.FunctionDef, ast.ClassDef)}
        self.assertTrue(all(defs[n.name] == ast.dump(n) for n in old.body if type(n) in (ast.FunctionDef, ast.ClassDef)))
        self.assertEqual([n.names[0].name for n in new.body if type(n) is ast.Import],
                         ["importlib.util", "sys", "sysconfig", "json", "struct"])
        self.assertFalse(any(type(n) is ast.ImportFrom for n in ast.walk(new)))
        self.assertEqual(self.selected.claim, "GENERATED_CONTROL_SOURCE_ONLY")
        for name in ("runtime_attested", "trust_attested", "import_used_bytes_attested", "method_approved"):
            self.assertFalse(getattr(self.selected, name))
        tree = ast.parse(subject._INLINE_BODY)
        forbidden = {"read", "write", "open", "print", "input", "exec", "compile", "Popen", "prepare_input"}
        self.assertFalse(any(type(n) is ast.Call and (type(n.func) is ast.Name and n.func.id in forbidden
            or type(n.func) is ast.Attribute and n.func.attr in forbidden) for n in ast.walk(tree)))

    def test_generated_script_cap_includes_literal_expansion(self):
        base = subject.build_inline_body_control_bootstrap(b"x", logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        raw = b"x" * (subject.MAX_SCRIPT_BYTES - len(base.source) + 1)
        selected = subject.build_inline_body_control_bootstrap(raw, logical_profile=LOCATOR,
            expected_soabi=SOABI, expected_destshared=DESTSHARED)
        self.assertEqual(len(selected.source), subject.MAX_SCRIPT_BYTES)
        for value in (raw + b"x", b"\0" * len(raw)):
            with self.assertRaises(subject.BootstrapSourceRejected) as caught:
                subject.build_inline_body_control_bootstrap(value, logical_profile=LOCATOR,
                    expected_soabi=SOABI, expected_destshared=DESTSHARED)
            self.assertEqual(caught.exception.args, ("SCRIPT_LIMIT",))
            self.assertTrue(caught.exception.__suppress_context__)
        self.assertNotIn(LOCATOR, repr(selected))

if __name__ == "__main__":
    unittest.main()
