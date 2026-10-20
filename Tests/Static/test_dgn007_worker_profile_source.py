"""Neue Workerzusammensetzung und Kontrollpfadbindung in eigenen Modellen."""
import ast
import builtins
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
from types import ModuleType
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_selected_observation as fixtures

f = fixtures.f
ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "Tests/Tools/dgn007_control_bootstrap_source.py"
PROFILE_PATH = ROOT / "Tests/Tools/dgn007_import_runtime_profile.py"
spec = importlib.util.spec_from_file_location("synthetic_worker_source_generator", GENERATOR_PATH)
generator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = generator
spec.loader.exec_module(generator)
OPTIONS = dict(logical_profile="/synthetic/control.py", expected_soabi="cpython-312",
               expected_destshared="/synthetic/stdlib/lib-dynload")
RAW = PROFILE_PATH.read_bytes()


def model(*, initialize=True):
    install, controls, rows, cache, runtime, filesystem, config, hook = fixtures.fixture()
    previous = cache["dgn007_import_runtime_profile"]
    control = ModuleType("dgn007_import_runtime_profile")
    control.__dict__.update(previous.__dict__)
    control.__dict__["__builtins__"] = dict(vars(builtins))
    code = compile(RAW, OPTIONS["logical_profile"], "exec", dont_inherit=True, optimize=0)
    # Echte Kontrollfunktionen, eigener Modulnamespace; kein Worker oder Cacheeintrag.
    exec(code, control.__dict__)
    control.__dict__.update(sys=runtime, os=filesystem, sysconfig=config)
    cache[control.__name__] = control
    source = generator.build_inline_worker_profile_control_bootstrap(RAW, **OPTIONS)
    tree = ast.parse(source.source)
    definitions = ast.Module(body=[node for node in tree.body
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.If))], type_ignores=[])
    namespace = cache["__main__"].__dict__
    namespace.update(__builtins__=dict(vars(builtins)), sys=runtime, struct=struct, json=json)
    # Direkte Imports und generiertes Main werden niemals ausgeführt.
    exec(compile(definitions, "/synthetic/model.py", "exec"), namespace)
    anchor = (control, control.__spec__, control.__loader__, f.SourceFileLoader, f.ModuleSpec,
              cache, cache["__main__"], RAW, code, ModuleType, control.__name__, control.__file__)
    calls = []
    def coherent(*actual):
        calls.append(1)
        if (len(actual) != 12 or any(a is not b for a, b in zip(actual, anchor))
                or namespace["sys"] is not runtime or runtime.modules is not cache
                or cache.get(control.__name__) is not control):
            raise ValueError("MODEL_COHERENCY")
    namespace.update(_coherent=coherent, _SEMANTIC_CONTROL_ANCHOR=anchor)
    initial = namespace["_initialize_worker_profile_control"]() if initialize else None
    worker = (1, "run_dgn007_automated_setup", "PRE_IMPORT", install, controls, rows)
    return dict(ns=namespace, control=control, cache=cache, runtime=runtime, filesystem=filesystem,
                config=config, hook=hook, worker=worker, calls=calls, initial=initial, source=source)


class WorkerProfileSourceTests(unittest.TestCase):
    def setUp(self):
        self.real = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.real))
        self.assertTrue(all(sys.modules[name] is value for name, value in self.real.items()))

    def initialized(self, environment):
        self.assertEqual(environment["initial"], ("BOUND_WORKER_PROFILE_CONTROL", "NONE"))

    def call(self, environment, **changes):
        values = dict(worker=environment["worker"], token=b"t" * 32,
                      separately_known_filefinder_hook=environment["hook"])
        values.update(changes)
        return environment["ns"]["_inline_observe_selected_worker_profile"](**values)

    def rejected(self, environment, **changes):
        result = self.call(environment, **changes)
        self.assertEqual(result[0], "REJECTED_SELECTED_WORKER_PROFILE")
        self.assertIn(result[1], ("WORKER_PROFILE_REJECTED", "WORKER_PROFILE_BINDING"))
        self.assertIsNone(result[2])
        self.assertIsNone(environment["ns"]["_WORKER_PROFILE_BINDING"])
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_full_actual_profile_source_fits_and_raw_literal_is_unchanged(self):
        result = generator.build_inline_worker_profile_control_bootstrap(RAW, **OPTIONS)
        self.assertLessEqual(result.source_size, 131072)
        self.assertEqual(result.source_size, len(result.source))
        self.assertEqual(result.profile_raw, RAW)
        self.assertEqual(result.source_sha256, hashlib.sha256(result.source).hexdigest())
        tree = ast.parse(result.source)
        raw = next(node.value.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "_EXPECTED_PROFILE_RAW"
                           for target in node.targets))
        self.assertEqual(raw, RAW)
        self.assertFalse(result.runtime_attested or result.trust_attested
                         or result.import_used_bytes_attested or result.method_approved)

    def test_fixed_worker_helpers_imports_and_absent_parent_matchers(self):
        result = generator.build_inline_worker_profile_control_bootstrap(RAW, **OPTIONS)
        tree = ast.parse(result.source)
        imports = [alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertTrue({"_inline_receive_metadata_chunks", "_inline_profile_report",
                         "_inline_command_match", "_inline_receive_declared_bodies",
                         "_inline_observe_selected_worker_profile"} <= names)
        self.assertTrue({"_inline_match_session_end", "_inline_match_profile_records",
                         "_inline_plan_profile_body_release", "_inline_match_input_complete"}.isdisjoint(names))
        main = [node for node in tree.body if isinstance(node, ast.If)]
        self.assertEqual(len(main), 1)
        calls = [node.value.func.id for node in main[0].body if isinstance(node, ast.Assign)]
        self.assertEqual(calls, ["_load_bound_control", "_initialize_worker_profile_control"])

    def test_actual_private_profile_and_scalars_from_the_pr265_path(self):
        environment = model()
        self.initialized(environment)
        paths = []
        environment["filesystem"].path.realpath = lambda path: paths.append(path) or path
        result = self.call(environment)
        self.assertEqual(result[:2], ("OBSERVED_SELECTED_WORKER_PROFILE", "NONE"))
        actual = result[2]
        self.assertEqual(actual.scalars[2], environment["worker"][5])
        self.assertEqual(actual.profile.token, b"t" * 32)
        for row in actual.profile.modules:
            self.assertIs(row.module, environment["cache"][row.name])
        self.assertGreaterEqual(len(paths), 3)
        self.assertGreaterEqual(len(environment["calls"]), 5)
        self.assertNotIn("/synthetic", repr(actual))
        self.assertFalse(actual.report.runtime_attested or actual.report.trust_attested
                         or actual.report.import_used_bytes_attested or actual.report.method_approved)
        self.assertEqual(self.call(environment)[:2], result[:2])

    def test_full_late_form_failures_precede_control_access_and_callbacks(self):
        accessed = []
        class Foreign:
            def __iter__(self):
                accessed.append("ITER")
                raise AssertionError("FOREIGN")
            def __eq__(self, other):
                accessed.append("EQ")
                raise AssertionError("FOREIGN")
        for change in ("w6", "s15", "p11", "token", "hook"):
            environment = model()
            self.initialized(environment)
            environment["calls"].clear()
            worker = environment["worker"]
            values = (dict(worker=Foreign()) if change == "w6" else
                      dict(worker=f.replace_at(worker, 3, f.replace_at(worker[3], 14, (Foreign(),))))
                      if change == "s15" else
                      dict(worker=f.replace_at(worker, 5, worker[5][:-1] + (Foreign(),)))
                      if change == "p11" else {change if change == "token" else
                          "separately_known_filefinder_hook": Foreign()})
            self.rejected(environment, **values)
            self.assertEqual(environment["calls"], [])
        self.assertEqual(accessed, [])

    def test_helper_replacement_is_rejected_before_and_after_initial_binding(self):
        for name in ("observe_selected_profile_scalars", "_selected_shapes", "_bind_selected",
                     "_capture", "observe_current_interpreter_scalars"):
            for initialize in (False, True):
                environment = model(initialize=initialize)
                called = []
                def foreign(*args, **kwargs):
                    called.append(1)
                    raise RuntimeError("/synthetic/private")
                environment["control"].__dict__[name] = foreign
                if initialize:
                    self.rejected(environment)
                else:
                    result = environment["ns"]["_initialize_worker_profile_control"]()
                    self.assertEqual(result, ("REJECTED_WORKER_PROFILE_CONTROL", "WORKER_PROFILE_BINDING"))
                self.assertEqual(called, [])

    def test_function_defaults_code_globals_and_closure_drift(self):
        for change in ("defaults", "keywords", "code", "globals", "closure"):
            environment = model()
            self.initialized(environment)
            function = environment["control"].__dict__["_need"]
            if change == "defaults":
                function.__defaults__ = ("CHANGED",)
            elif change == "keywords":
                function.__kwdefaults__ = {"other": None}
            elif change == "code":
                function.__code__ = function.__code__.replace()
            elif change == "globals":
                environment["control"].__dict__["_need"] = type(function)(function.__code__, {})
            else:
                def factory():
                    value = 1
                    return lambda *args: value
                environment["control"].__dict__["_need"] = factory()
            self.rejected(environment)

    def test_module_class_and_known_mutable_configuration_drift(self):
        for change in ("namespace", "class", "class_method", "frozen"):
            environment = model()
            self.initialized(environment)
            control = environment["control"]
            if change == "namespace":
                control.extra = None
            elif change == "class":
                control.ProfileReport.extra = None
            elif change == "class_method":
                control.ProfileReport.__init__.__defaults__ = (True,)
            else:
                control.FROZEN_NAMES["os.path"] = ("other", "other")
            self.rejected(environment)

    def test_drift_during_actual_provider_callback_is_dominant_on_success_or_failure(self):
        for fail in (False, True):
            for change in ("helper", "cache", "anchor", "class"):
                environment = model()
                self.initialized(environment)
                reached = []
                def provider(name):
                    reached.append(name)
                    if change == "helper":
                        environment["control"]._capture = lambda *args: None
                    elif change == "cache":
                        environment["cache"]["dgn007_import_runtime_profile"] = ModuleType("other")
                    elif change == "anchor":
                        environment["ns"]["_SEMANTIC_CONTROL_ANCHOR"] = None
                    else:
                        environment["control"].SelectedScalarObservationResult.extra = None
                    if fail:
                        raise RuntimeError("/synthetic/private")
                    return environment["worker"][3][7]
                environment["config"].get_config_var = provider
                result = self.rejected(environment)
                self.assertEqual(result[1], "WORKER_PROFILE_BINDING")
                self.assertGreaterEqual(len(reached), 1)

    def test_matching_report_cannot_replace_full_actual_scalars(self):
        for change in ("version", "abi", "paths", "module"):
            environment = model()
            self.initialized(environment)
            if change == "version":
                environment["runtime"].version_info = (3, 12, 99)
            elif change == "abi":
                environment["config"].get_config_var = lambda name: "different"
            elif change == "paths":
                environment["runtime"].path.reverse()
            else:
                environment["cache"]["package"].__file__ = "/synthetic/other.py"
            self.rejected(environment)

    def test_initialization_and_failure_never_rebaseline(self):
        environment = model()
        self.initialized(environment)
        environment["control"]._capture.__defaults__ = (None,)
        self.rejected(environment)
        environment["control"]._capture.__defaults__ = None
        self.rejected(environment)
        self.assertEqual(environment["ns"]["_initialize_worker_profile_control"](),
                         ("REJECTED_WORKER_PROFILE_CONTROL", "WORKER_PROFILE_ALREADY_ATTEMPTED"))
        self.rejected(environment)
        other = model()
        self.initialized(other)
        self.assertEqual(other["ns"]["_initialize_worker_profile_control"]()[0], "REJECTED_WORKER_PROFILE_CONTROL")
        self.rejected(other)

    def test_generator_negative_forms_and_caps_without_fallback(self):
        for raw, options, issue in ((b"", OPTIONS, "PROFILE_SIZE"),
                (b"x" * 131073, OPTIONS, "PROFILE_SIZE"),
                (RAW, dict(OPTIONS, logical_profile="relative"), "LOCATOR_FORM"),
                (RAW, dict(OPTIONS, expected_soabi="bad\0abi"), "SOABI_FORM")):
            with self.subTest(issue=issue), self.assertRaises(generator.BootstrapSourceRejected) as caught:
                generator.build_inline_worker_profile_control_bootstrap(raw, **options)
            self.assertEqual(str(caught.exception), issue)

    def test_sixteenth_builder_selects_one_fixed_worker_route(self):
        tree = ast.parse(GENERATOR_PATH.read_bytes())
        names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name.startswith("build_")]
        self.assertEqual(len(names), 16)
        self.assertEqual(names[-1], "build_inline_worker_profile_control_bootstrap")
        # Neuer Pfad wählt festen vorhandenen Workerunterbau, keine dynamische Route.
        last = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == names[-1])
        builders = [node.func.id for node in ast.walk(last) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id.startswith("build_")]
        self.assertEqual(builders, ["build_inline_body_control_bootstrap"])


if __name__ == "__main__":
    unittest.main()
