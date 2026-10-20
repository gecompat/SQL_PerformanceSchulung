"""Eigene Proxybytes nach echten Modellphasen; kein DGN- oder Nativeworker."""
import ast
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_worker_input_source as fixture
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_proxy_loader_source as subject

RAW, OPTIONS = fixture.RAW, fixture.OPTIONS
NAME = "docker_sqlcmd_proxy"
SUCCESS = b"SYNTHETIC_VALUE = 7\n"


def rows(env):
    context = env["payload"][2]
    digest = hashlib.sha256(fixture.fixture.pooled((context,), "pooled-profile-binding-context/v1")).hexdigest()
    fields = (2, 1, "SOURCE", 2, digest, hashlib.sha256(env["bodies"][2]).hexdigest(), 2, 1)
    return tuple(fixture.fixture.line((tag,) + fields) + b"\n" for tag in ("BEGIN", "COMPLETE"))


def model(*, raw=SUCCESS, ordinal=2, initialize=True):
    trace, hooks, results = [], [None], [None]
    def setup(env):
        namespace = env["ns"]["__builtins__"]
        namespace.update(_real_compile=compile, _real_exec=exec, _trace=trace, _hooks=hooks,
                         _results=results, _fixture_env=env)
        exec('def compile(raw, origin, mode, *, dont_inherit, optimize):\n'
             '    env = _fixture_env\n'
             '    _trace.append(("COMPILE", raw, origin, mode, dont_inherit, optimize))\n'
             '    if _results[0] is not None: return _results[0]\n'
             '    code = _real_compile(raw, origin, mode, dont_inherit=dont_inherit, optimize=optimize)\n'
             '    _trace.append(("CODE", code))\n'
             '    if _hooks[0] is not None: _hooks[0]("compiled", code, None)\n'
             '    return code\n'
             'def exec(code, namespace):\n'
             '    _trace.append(("EXEC", code, namespace))\n'
             '    _real_exec(code, namespace)\n'
             '    _trace.append(("EXEC_RETURN", code, namespace))\n'
             '    if _hooks[0] is not None: _hooks[0]("executed", code, namespace)\n', namespace)
        env["proxy_initial"] = env["ns"]["_initialize_proxy_source_control"]() if initialize else None
    bodies = fixture.DEFAULT_BODIES[:2] + (raw,) + fixture.DEFAULT_BODIES[3:]
    env = fixture.model(ordinal=ordinal, bodies=bodies, before_io=setup,
                        builder=subject.build_proxy_loader_control_bootstrap)
    env.update(trace=trace, hooks=hooks, results=results)
    env["source_begin"], env["source_complete"] = rows(env)
    return env


class ProxyLoaderSourceTests(unittest.TestCase):
    def setUp(self):
        self.cache = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.cache))
        self.assertTrue(all(sys.modules[name] is value for name, value in self.cache.items()))

    def call(self, env):
        return env["ns"]["_proxy_source_entry"]()

    def reject(self, env):
        result = self.call(env)
        self.assertEqual(result[0], "REJECTED_PROXY_SOURCE")
        self.assertIn(result[1], ("PROXY_SOURCE_BINDING", "PROXY_SOURCE_REJECTED"))
        self.assertIsNone(result[2])
        self.assertNotIn("PRIVATE", repr(result))
        return result

    def events(self, env, kind):
        return [event for event in env["trace"] if event[0] == kind]

    def test_actual_source_fit_raw_five_imports_and_independent_whole_ast(self):
        built = subject.build_proxy_loader_control_bootstrap(RAW, **OPTIONS)
        self.assertEqual((built.source_size, built.source_sha256),
                         (len(built.source), hashlib.sha256(built.source).hexdigest()))
        self.assertLessEqual(len(built.source), 131072)
        self.assertFalse(built.runtime_attested or built.import_used_bytes_attested
                         or built.trust_attested or built.method_approved)
        actual = ast.parse(built.source)
        expected = ast.parse(subject.inputs.build_worker_input_control_bootstrap(RAW, **OPTIONS).source)
        init = next(node for node in expected.body if isinstance(node, ast.FunctionDef)
                    and node.name == "_initialize_worker_input_control")
        block = next(node for node in init.body if isinstance(node, ast.Try)).body
        pos = next(n for n, node in enumerate(block) if isinstance(node, ast.Assign)
                   and ast.unparse(node.targets[0]).startswith("(_worker_input_entry,"))
        block.insert(pos + 1, ast.parse("_proxy_input_handoff(owner, _worker_input_entry)").body[0])
        receive = next(node for node in expected.body if isinstance(node, ast.FunctionDef) and node.name == "_worker_input_run")
        receive.body.insert(len(receive.body) - 1, ast.parse("_proxy_eof_handoff(owner, frame, result)").body[0])
        main = next(node for node in expected.body if isinstance(node, ast.If))
        main.body.insert(2, ast.parse("_initialize_proxy_source_control()").body[0])
        main.body[-1] = ast.parse("_proxy_source_main()").body[0]
        expected.body = [node for node in expected.body if node is not main]
        expected.body += ast.parse(subject._INLINE_PROXY_SOURCE).body + [main]
        self.assertEqual(ast.dump(actual, include_attributes=False), ast.dump(expected, include_attributes=False))
        self.assertEqual([alias.name for node in actual.body if isinstance(node, ast.Import) for alias in node.names],
                         ["importlib.util", "sys", "sysconfig", "json", "struct"])
        literal = next(node.value.value for node in actual.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "_EXPECTED_PROFILE_RAW" for target in node.targets))
        self.assertEqual(literal, RAW)

    def test_lf_crlf_eof_begin_actual_raw_code_namespace_and_complete(self):
        for raw in (SUCCESS, b"SYNTHETIC_VALUE = 7\r\n"):
            env = model(raw=raw)
            self.assertEqual(env["proxy_initial"], ("BOUND_PROXY_SOURCE_CONTROL", "NONE"))
            main = env["cache"]["__main__"]
            observed = []
            def observer(phase, code, namespace):
                observed.append((phase, bytes(env["io"].output), env["io"].offset))
            env["hooks"][0] = observer
            result = self.call(env)
            self.assertEqual(result[:2], ("EXECUTED_PROXY_SOURCE", "NONE"))
            module, spec, loader, code, heldraw, begin, complete = result[2]
            compile_event, exec_event = self.events(env, "COMPILE")[0], self.events(env, "EXEC")[0]
            self.assertIs(compile_event[1], heldraw)
            self.assertEqual(heldraw, raw)
            self.assertEqual(compile_event[2:], (code.co_filename, "exec", True, 0))
            self.assertIs(self.events(env, "CODE")[0][1], code)
            self.assertIs(exec_event[1], code)
            self.assertIs(exec_event[2], module.__dict__)
            self.assertIs(env["cache"][NAME], module)
            self.assertIs(module.__spec__, spec)
            self.assertIs(module.__loader__, loader)
            self.assertEqual((module.__name__, module.SYNTHETIC_VALUE), (NAME, 7))
            self.assertIs(env["cache"]["__main__"], main)
            self.assertEqual(main.__name__, "__main__")
            self.assertEqual((begin, complete), (env["source_begin"], env["source_complete"]))
            self.assertTrue(all(output.endswith(begin) and offset == len(env["io"].input)
                                for phase, output, offset in observed))
            self.assertTrue(bytes(env["io"].output).endswith(begin + complete))
            self.assertTrue(all(name not in env["cache"] for name in ("Tests", "Tests.Contracts", "execution_target")))

    def test_partial_confirmed_writes_share_original_offsets_and_budget(self):
        env = model()
        env["io"].read_max = env["io"].write_max = 64
        result = self.call(env)
        self.assertEqual(result[0], "EXECUTED_PROXY_SOURCE")
        self.assertTrue(bytes(env["io"].output).endswith(env["source_begin"] + env["source_complete"]))
        budget = fixture.owner(env)[2]
        self.assertEqual(budget[3], len(env["io"].events))
        self.assertEqual(budget[5], len(env["io"].output))
        self.assertLessEqual(budget[3], 1088)

    def test_other_roles_never_compile_or_create_proxy_module(self):
        for ordinal in (1, 3):
            env = model(ordinal=ordinal)
            self.reject(env)
            self.assertEqual(env["trace"], [])
            self.assertNotIn(NAME, env["cache"])

    def test_input_failure_early_eof_bad_body_and_extra_byte_precede_all_source_operations(self):
        for kind in ("early", "body", "extra"):
            env = model()
            if kind == "early": env["io"].input = env["metadata"][:-1]
            elif kind == "body":
                offset = len(env["metadata"]) + len(env["commands"][0])
                env["io"].input = env["io"].input[:offset] + b"X" + env["io"].input[offset + 1:]
            else: env["io"].input += b"X"
            self.reject(env)
            self.assertEqual(env["trace"], [])
            self.assertNotIn(NAME, env["cache"])

    def test_forged_early_handoff_and_replaced_public_input_entry_are_not_authority(self):
        env, reached = model(), []
        def callback(io, operation):
            if not reached:
                reached.append(1)
                env["ns"]["_proxy_eof_handoff"](fixture.owner(env), (None,) * 4, (None,) * 3)
        env["io"].callback = callback
        self.reject(env)
        self.assertEqual(reached, [1])
        self.assertEqual(env["trace"], [])
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
            def __call__(self): calls.append("CALL"); raise AssertionError()
        env = model()
        env["ns"]["_worker_input_entry"] = Foreign()
        self.reject(env)
        self.assertEqual((calls, env["trace"], env["io"].events), ([], [], []))

    def test_existing_foreign_cache_slot_is_preserved_without_getter(self):
        env, reached, calls = model(), [], []
        class Foreign:
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
        foreign = Foreign()
        def callback(io, operation):
            if not reached and operation == "read" and io.offset == len(io.input):
                reached.append(1)
                env["cache"][NAME] = foreign
        env["io"].callback = callback
        self.reject(env)
        self.assertEqual((reached, calls, env["trace"]), ([1], [], []))
        self.assertIs(env["cache"][NAME], foreign)

    def test_compile_and_exec_failures_never_attempt_complete_and_remove_only_own_slot(self):
        for raw, executions in ((b"return\n", 0), (b"raise RuntimeError('PRIVATE fixture failure')\n", 1)):
            env = model(raw=raw)
            self.reject(env)
            self.assertEqual(len(self.events(env, "COMPILE")), 1)
            self.assertEqual(len(self.events(env, "EXEC")), executions)
            self.assertTrue(bytes(env["io"].output).endswith(env["source_begin"]))
            self.assertNotIn(NAME, env["cache"])
            before = len(env["io"].events)
            self.reject(env)
            self.assertEqual(len(env["io"].events), before)

    def test_compile_exec_provider_code_drift_has_dominant_post_failure(self):
        for phase, executions in (("compiled", 0), ("executed", 1)):
            env, reached = model(), []
            def callback(current, code, namespace):
                if current == phase:
                    reached.append(1)
                    function = env["ns"]["__builtins__"]["compile" if phase == "compiled" else "exec"]
                    function.__code__ = function.__code__.replace()
            env["hooks"][0] = callback
            result = self.reject(env)
            self.assertEqual(result[1], "PROXY_SOURCE_BINDING")
            self.assertEqual((reached, len(self.events(env, "EXEC"))), ([1], executions))
            self.assertNotIn(env["source_complete"], env["io"].output)
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
            def __call__(self, *args): calls.append("CALL"); raise AssertionError()
        for name in ("_proxy_original", "_proxy_guard"):
            env, reached = model(), []
            def callback(phase, code, namespace):
                if phase == "compiled":
                    reached.append(1)
                    env["ns"][name] = Foreign()
            env["hooks"][0] = callback
            self.assertEqual(self.reject(env)[1], "PROXY_SOURCE_BINDING")
            self.assertEqual((reached, calls, self.events(env, "EXEC")), ([1], [], []))

    def test_late_module_spec_cache_and_class_drift_precede_complete(self):
        calls = []
        class ForeignModule(fixture.f.ModuleType):
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
        for kind in ("origin", "file", "spec", "cache", "class"):
            env, reached = model(), []
            foreign = object()
            def callback(phase, code, namespace):
                if phase != "executed": return
                reached.append(1)
                if kind == "origin": namespace["__spec__"].origin = "/synthetic/changed"
                elif kind == "file": namespace["__file__"] = "/synthetic/changed"
                elif kind == "spec": namespace["__spec__"] = foreign
                elif kind == "cache": env["cache"][NAME] = foreign
                else: env["cache"][NAME].__class__ = ForeignModule
            env["hooks"][0] = callback
            self.assertEqual(self.reject(env)[1], "PROXY_SOURCE_BINDING")
            self.assertEqual(reached, [1])
            self.assertNotIn(env["source_complete"], env["io"].output)
            if kind == "cache": self.assertIs(env["cache"][NAME], foreign)
        self.assertEqual(calls, [])

    def test_foreign_namespace_keys_fail_before_any_comparison(self):
        calls = []
        for kind in ("module", "spec", "builtins", "cache"):
            env, reached = model(), []
            keyname = {"module": "__file__", "spec": "origin", "builtins": "compile", "cache": NAME}[kind]
            class Key:
                def __hash__(self): return hash(keyname)
                def __eq__(self, other): calls.append("EQ"); raise AssertionError()
            def callback(phase, code, namespace):
                if phase != "executed": return
                reached.append(1)
                target = {"module": namespace, "spec": namespace["__spec__"].__dict__,
                          "builtins": env["ns"]["__builtins__"], "cache": env["cache"]}[kind]
                value = target.pop(keyname)
                target[Key()] = value
            env["hooks"][0] = callback
            self.reject(env)
            self.assertEqual((reached, calls), ([1], []))

    def test_same_io_output_caps_and_partial_begin_exhaustion_stop_before_compile(self):
        for kind in ("io", "output", "partial"):
            env, reached = model(), []
            def callback(io, operation):
                if reached or operation != "read" or io.offset != len(io.input): return
                reached.append(1)
                state = fixture.owner(env)[2]
                if kind == "output": state[5] = 65536
                else:
                    state[3] = 1088 if kind == "io" else 1087
                    if kind == "partial": io.write_max = 1
            env["io"].callback = callback
            self.reject(env)
            self.assertEqual((reached, env["trace"]), ([1], []))
            self.assertLessEqual(fixture.owner(env)[2][3], 1088)

    def test_bad_write_counts_and_foreign_code_are_closed_without_getter(self):
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
        for value in (0, True, Foreign()):
            env, reached = model(), []
            def callback(io, operation):
                if not reached and operation == "read" and io.offset == len(io.input):
                    reached.append(1)
                    io.write_value = lambda data: value
            env["io"].callback = callback
            self.reject(env)
            self.assertEqual(env["trace"], [])
        env = model()
        env["results"][0] = Foreign()
        self.reject(env)
        self.assertEqual(self.events(env, "EXEC"), [])
        self.assertEqual(calls, [])

    def test_complete_wire_bytes_are_not_rolled_back_after_post_binding_failure(self):
        env, reached = model(), []
        def callback(io, operation):
            if not reached and operation == "write" and bytes(io.output).endswith(env["source_begin"]):
                reached.append(1)
                env["cache"][NAME].__spec__.origin = "/synthetic/changed"
        env["io"].callback = callback
        self.assertEqual(self.reject(env)[1], "PROXY_SOURCE_BINDING")
        self.assertEqual(reached, [1])
        self.assertTrue(bytes(env["io"].output).endswith(env["source_complete"]))
        self.assertEqual(len(self.events(env, "EXEC_RETURN")), 1)
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
            def __le__(self, other): calls.append("COMPARE"); raise AssertionError()
        for slot, value in ((4, True), (4, -1), (4, 1064961), (4, Foreign()),
                            (6, False), (6, 1), (6, Foreign())):
            env, reached = model(), []
            def callback(io, operation):
                if not reached and operation == "write" and bytes(io.output).endswith(env["source_begin"]):
                    reached.append(1)
                    fixture.owner(env)[2][slot] = value
            env["io"].callback = callback
            self.assertEqual(self.reject(env)[1], "PROXY_SOURCE_BINDING")
            self.assertEqual((reached, calls), ([1], []))
            self.assertTrue(bytes(env["io"].output).endswith(env["source_complete"]))
            self.assertEqual(len(self.events(env, "EXEC_RETURN")), 1)

    def test_reentrancy_entry_and_direct_loader_before_begin_are_sticky(self):
        for phase in ("read", "compiled", "executed", "loader"):
            env, reached, nested = model(), [], []
            if phase in ("compiled", "executed"):
                def callback(current, code, namespace):
                    if not reached and current == phase:
                        reached.append(1)
                        nested.append(self.call(env))
                env["hooks"][0] = callback
            else:
                def callback(io, operation):
                    if reached: return
                    if phase == "read" and operation == "read":
                        reached.append(1)
                        nested.append(self.call(env))
                    elif phase == "loader" and operation == "write" and io.offset == len(io.input):
                        reached.append(1)
                        module = env["cache"][NAME]
                        try: module.__loader__.exec_module(module)
                        except BaseException: nested.append("REJECTED")
                env["io"].callback = callback
            self.reject(env)
            self.assertEqual(reached, [1])
            self.assertEqual(len(nested), 1)
            if phase in ("read", "loader"): self.assertEqual(env["trace"], [])
            if phase == "compiled": self.assertEqual(self.events(env, "EXEC"), [])

    def test_retry_missing_init_marker_and_loader_code_cannot_reauthorize(self):
        env = model()
        result = self.call(env)
        self.assertEqual(result[0], "EXECUTED_PROXY_SOURCE")
        before = len(env["io"].events)
        self.reject(env)
        with self.assertRaises(RuntimeError): result[2][2].exec_module(result[2][0])
        self.assertEqual((len(env["io"].events), len(self.events(env, "EXEC"))), (before, 1))
        env = model(initialize=False)
        self.reject(env)
        self.assertEqual((env["io"].events, env["trace"]), ([], []))
        for kind in ("marker", "init", "method"):
            env = model()
            if kind == "marker": env["ns"]["_PROXY_SOURCE_MARKER"] = object()
            elif kind == "init": env["ns"]["_initialize_proxy_source_control"]()
            else:
                method = env["ns"]["_PROXY_LOADER_CLASS"].__dict__["exec_module"]
                method.__code__ = method.__code__.replace()
            self.reject(env)
            self.assertEqual((env["io"].events, env["trace"]), ([], []))


if __name__ == "__main__":
    unittest.main()
