"""Isolierte Parentmodelle; keine Verwendung des tatsächlichen Modulcaches."""
import ast
import json
from pathlib import Path
import sys
import unittest
from importlib.machinery import ModuleSpec
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_codefree_parents as subject

DIGEST = "a" * 64


def fixture(*, digest=DIGEST, cache=None, guard_hook=None, write_hook=None):
    env = {"cache": {} if cache is None else cache, "rows": [], "guards": [], "hooks": [guard_hook, write_hook]}
    def guard(*, held=None):
        env["guards"].append(True)
        if env["hooks"][0] is not None:
            return env["hooks"][0](env)
    def write(row):
        env["rows"].append(row)
        if env["hooks"][1] is not None:
            return env["hooks"][1](env, row)
    env.update(guard=guard, write=write)
    env["run"] = subject.make_codefree_parent_registry(module_type=ModuleType,
        spec_type=ModuleSpec, cache=env["cache"], context_digest=digest, guard=guard, write=write)
    return env


class CodefreeParentTests(unittest.TestCase):
    def setUp(self):
        self.modules = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.modules))
        self.assertTrue(all(sys.modules[k] is v for k, v in self.modules.items()))

    def rejected(self, env, binding=None):
        result = env["run"]()
        self.assertEqual(result[0], "REJECTED_CODEFREE_PARENTS")
        self.assertIsNone(result[2])
        if binding is not None:
            self.assertEqual(result[1], "PARENT_REGISTRATION_BINDING" if binding else "PARENT_REGISTRATION_REJECTED")
        return result

    def test_exact_objects_package_locations_and_independent_wire(self):
        main = ModuleType("__main__")
        env = fixture(cache={"__main__": main})
        result = env["run"]()
        self.assertEqual(result[:2], ("REGISTERED_CODEFREE_PARENTS", "NONE"))
        self.assertEqual(len(result[2]), 2)
        for index, (m, spec, locations) in enumerate(result[2]):
            name = ("Tests", "Tests.Contracts")[index]
            self.assertIs(type(m), ModuleType)
            self.assertIs(type(spec), ModuleSpec)
            self.assertIs(env["cache"][name], m)
            self.assertIs(m.__spec__, spec)
            self.assertIs(m.__path__, locations)
            self.assertIs(spec.submodule_search_locations, locations)
            self.assertEqual(locations, [])
            self.assertEqual((m.__name__, m.__package__, spec.name), (name,) * 3)
            self.assertIsNone(spec.origin)
            self.assertIsNone(spec.loader)
            self.assertIsNone(m.__loader__)
            self.assertFalse(spec.has_location)
            self.assertNotIn("__file__", m.__dict__)
            self.assertNotIn("__cached__", m.__dict__)
        self.assertIs(result[2][0][0].Contracts, result[2][1][0])
        self.assertIs(env["cache"]["__main__"], main)
        expected = [json.dumps([tag, 1, index + 6, "PARENT", index, DIGEST, None,
                    index + 9, index + 6], separators=(",", ":"), ensure_ascii=True).encode() + b"\n"
                    for index in range(2) for tag in ("BEGIN", "COMPLETE")]
        self.assertEqual(env["rows"], expected)
        self.assertTrue(all(len(row) <= 256 for row in env["rows"]))

    def test_component_has_no_compile_exec_import_or_native_dispatch(self):
        tree = ast.parse(Path(subject.__file__).read_text(encoding="utf-8-sig"))
        factory = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(factory)))
        forbidden = {"compile", "exec", "eval", "__import__", "open", "get_code", "exec_module", "read", "write"}
        calls = [n.func for n in ast.walk(factory) if isinstance(n, ast.Call)]
        self.assertFalse(any(isinstance(n, ast.Name) and n.id in forbidden for n in calls))
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr in forbidden for n in calls))

    def test_primitive_factory_boundaries_before_foreign_dispatch(self):
        calls = []
        class Foreign:
            def __len__(self): calls.append("len"); raise AssertionError()
            def __eq__(self, other): calls.append("eq"); raise AssertionError()
            def __getattribute__(self, name): calls.append("get"); raise AssertionError()
        base = dict(module_type=ModuleType, spec_type=ModuleSpec, cache={}, context_digest=DIGEST,
                    guard=lambda: None, write=lambda row: None)
        for key, bad in (("cache", Foreign()), ("context_digest", Foreign()),
                ("guard", Foreign()), ("write", Foreign()), ("module_type", Foreign()),
                ("spec_type", Foreign()), ("context_digest", "A" * 64),
                ("context_digest", "a" * 63), ("cache", {1: object()}),
                ("cache", {str(n): None for n in range(257)})):
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.make_codefree_parent_registry(**(base | {key: bad}))
        self.assertEqual(calls, [])

    def test_preexisting_and_late_foreign_cache_slots_are_preserved(self):
        foreign = ModuleType("foreign")
        for name in ("Tests", "Tests.Contracts"):
            env = fixture(cache={name: foreign})
            self.rejected(env, True)
            self.assertEqual(env["rows"], [])
            self.assertIs(env["cache"][name], foreign)
        reached = []
        def hook(env, row):
            if len(env["rows"]) == 2:
                reached.append(True)
                env["cache"]["Tests.Contracts"] = foreign
        env = fixture(write_hook=hook)
        self.rejected(env, True)
        self.assertEqual(reached, [True])
        self.assertEqual(len(env["rows"]), 2)
        self.assertIs(env["cache"]["Tests.Contracts"], foreign)
        self.assertNotIn("Tests", env["cache"])

    def test_late_foreign_child_slot_is_preserved_before_own_binding(self):
        foreign, reached, parents = object(), [], []
        def hook(env, row):
            if len(env["rows"]) == 2:
                parent = env["cache"]["Tests"]
                parents.append(parent)
                parent.Contracts = foreign
                reached.append(True)
        env = fixture(write_hook=hook)
        self.rejected(env, True)
        self.assertEqual(reached, [True])
        self.assertEqual(len(env["rows"]), 2)
        self.assertIs(parents[0].Contracts, foreign)
        self.assertEqual(env["cache"], {})

    def test_original_provider_code_kwdefaults_and_closure_contents(self):
        for kind in ("code", "kwdefault", "closure"):
            reached = []
            def hook(env, row):
                if len(env["rows"]) == 1:
                    reached.append(True)
                    if kind == "code":
                        env["guard"].__code__ = env["guard"].__code__.replace()
                    elif kind == "kwdefault":
                        env["guard"].__kwdefaults__["held"] = object()
                    else:
                        env["guard"].__closure__[0].cell_contents = dict(env)
            env = fixture(write_hook=hook)
            self.rejected(env, True)
            self.assertEqual(reached, [True])
            self.assertEqual(len(env["rows"]), 1)
            self.assertEqual(env["cache"], {})

    def test_provider_container_bounds_before_external_dispatch(self):
        env = fixture()
        env["guard"].__kwdefaults__ = {str(n): None for n in range(33)}
        self.rejected(env, True)
        self.assertEqual(env["guards"], [])
        self.assertEqual(env["rows"], [])

    def test_spec_module_locations_and_class_drift_after_begin(self):
        for kind in ("spec", "path", "locations", "file", "class", "class_limit"):
            reached = []
            def hook(env, row):
                if len(env["rows"]) == 1:
                    m = env["cache"]["Tests"]
                    reached.append(True)
                    if kind == "spec": m.__spec__.origin = "foreign"
                    elif kind == "path": m.__path__ = []
                    elif kind == "locations": m.__path__.append("foreign")
                    elif kind == "file": m.__file__ = "foreign"
                    elif kind == "class": ModuleSpec._synthetic_parent_drift = None
                    else:
                        for index in range(128):
                            setattr(ModuleSpec, "_synthetic_parent_limit_" + str(index), None)
            env = fixture(write_hook=hook)
            try:
                self.rejected(env, True)
                self.assertEqual(reached, [True])
                self.assertEqual(len(env["rows"]), 1)
                self.assertEqual(env["cache"], {})
            finally:
                if kind == "class" and "_synthetic_parent_drift" in ModuleSpec.__dict__:
                    del ModuleSpec._synthetic_parent_drift
                if kind == "class_limit":
                    for index in range(128):
                        key = "_synthetic_parent_limit_" + str(index)
                        if key in ModuleSpec.__dict__: delattr(ModuleSpec, key)

    def test_completed_parent_and_own_child_binding_remain_checked(self):
        for kind in ("parent", "child"):
            foreign, reached, originals = object(), [], []
            def hook(env, row):
                if len(env["rows"]) == 3:
                    reached.append(True)
                    originals.append(env["cache"]["Tests"])
                    if kind == "parent": env["cache"]["Tests"].__package__ = "foreign"
                    else: env["cache"]["Tests"].Contracts = foreign
            env = fixture(write_hook=hook)
            self.rejected(env, True)
            self.assertEqual(reached, [True])
            self.assertEqual(len(env["rows"]), 3)
            self.assertEqual(env["cache"], {})
            if kind == "child": self.assertIs(originals[0].Contracts, foreign)

    def test_callback_errors_and_return_values_do_not_publish_success(self):
        for bad in (0, True, b"", object(), "raise"):
            def hook(env, row):
                if bad == "raise": raise RuntimeError("PRIVATE_SYNTHETIC_ERROR")
                return bad
            env = fixture(write_hook=hook)
            result = self.rejected(env, False)
            self.assertEqual(len(env["rows"]), 1)
            self.assertEqual(env["cache"], {})
            self.assertNotIn("PRIVATE", repr(result))
        env = fixture(guard_hook=lambda env: False)
        self.rejected(env, True)
        self.assertEqual(env["rows"], [])

    def test_reentrancy_and_retry_are_sticky(self):
        nested = []
        def hook(env, row): nested.append(env["run"]())
        env = fixture(write_hook=hook)
        self.rejected(env, True)
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0][:2], ("REJECTED_CODEFREE_PARENTS", "PARENT_REGISTRATION_BINDING"))
        self.assertEqual(len(env["rows"]), 1)
        self.assertEqual(env["cache"], {})
        self.rejected(env, True)
        env = fixture()
        self.assertEqual(env["run"]()[0], "REGISTERED_CODEFREE_PARENTS")
        before = tuple(env["rows"])
        self.rejected(env, True)
        self.assertEqual(tuple(env["rows"]), before)

    def test_foreign_replacement_and_own_cleanup_identity(self):
        foreign, reached, originals = ModuleType("foreign"), [], []
        def hook(env, row):
            if len(env["rows"]) == 4:
                reached.append(True)
                originals.append(env["cache"]["Tests"])
                env["cache"]["Tests.Contracts"] = foreign
        main = ModuleType("__main__")
        env = fixture(cache={"__main__": main}, write_hook=hook)
        self.rejected(env, True)
        self.assertEqual(reached, [True])
        self.assertEqual(len(env["rows"]), 4)
        self.assertIs(env["cache"]["Tests.Contracts"], foreign)
        self.assertIs(env["cache"]["__main__"], main)
        self.assertNotIn("Tests", env["cache"])
        self.assertNotIn("Contracts", originals[0].__dict__)


if __name__ == "__main__":
    unittest.main()
