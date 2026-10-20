"""Eigene verschachtelte Harness-Bodies; keine DGN-Raw- oder Nativeexecution."""
import ast
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_proxy_loader_source as previous
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_harness_loader_source as subject

fixture = previous.fixture
RAW, OPTIONS = fixture.RAW, fixture.OPTIONS
NAMES = ("run_demo", "orchestrate_sessions", "sqlcmd_process")
BODIES = (
    b"from orchestrate_sessions import run_manifest\nfrom sqlcmd_process import build_sqlcmd_command, extract_summary, resolve_sqlcmd, run_sqlcmd\nSYNTHETIC_VALUE = run_manifest\n",
    b"from sqlcmd_process import build_sqlcmd_command, collect_process, resolve_sqlcmd, start_sqlcmd\nrun_manifest = build_sqlcmd_command\n",
    b"build_sqlcmd_command = collect_process = resolve_sqlcmd = start_sqlcmd = extract_summary = run_sqlcmd = 7\n")


def rows(env):
    digest = hashlib.sha256(fixture.fixture.pooled((env["payload"][2],), "pooled-profile-binding-context/v1")).hexdigest()
    return tuple(fixture.fixture.line((tag, 3, index - 2, "SOURCE", index, digest,
        hashlib.sha256(env["bodies"][index]).hexdigest(), index, index - 2)) + b"\n"
        for tag, index in (("BEGIN", 3), ("BEGIN", 4), ("BEGIN", 5),
                           ("COMPLETE", 5), ("COMPLETE", 4), ("COMPLETE", 3)))


def model(*, bodies=BODIES, ordinal=3, initialize=True, extras=None):
    trace, hooks, results = [], [None], [None]
    def setup(env):
        bi = env["ns"]["__builtins__"]
        bi.update({} if extras is None else extras)
        stdlib = fixture.f.ModuleType("os")
        bi.update(_real_compile=compile, _real_exec=exec, _trace=trace, _hooks=hooks,
                  _results=results, _fixture_env=env, _stdlib=stdlib)
        exec('def compile(raw, origin, mode, *, dont_inherit, optimize):\n'
             ' _trace.append(("COMPILE", raw, origin, mode, dont_inherit, optimize))\n'
             ' if _results[0] is not None: return _results[0]\n'
             ' code = _real_compile(raw, origin, mode, dont_inherit=dont_inherit, optimize=optimize)\n'
             ' _trace.append(("CODE", code))\n'
             ' if _hooks[0] is not None: _hooks[0]("compiled", code, None)\n'
             ' return code\n'
             'def exec(code, namespace):\n'
             ' _trace.append(("EXEC", code, namespace))\n'
             ' _real_exec(code, namespace)\n'
             ' _trace.append(("EXEC_RETURN", code, namespace))\n'
             ' if _hooks[0] is not None: _hooks[0]("executed", code, namespace)\n'
             'def __import__(name, globals=None, locals=None, fromlist=(), level=0):\n'
             ' _trace.append(("DELEGATE", name, globals, locals, fromlist, level))\n'
             ' if _hooks[0] is not None: _hooks[0]("delegated", None, globals)\n'
             ' if name != "os": raise ImportError()\n'
             ' return _stdlib\n', bi)
        env["hl_initial"] = env["ns"]["_initialize_hl_control"]() if initialize else None
    all_bodies = fixture.DEFAULT_BODIES[:3] + bodies + fixture.DEFAULT_BODIES[6:]
    env = fixture.model(ordinal=ordinal, bodies=all_bodies, before_io=setup,
                        builder=subject.build_harness_loader_control_bootstrap)
    env.update(trace=trace, hooks=hooks, results=results)
    env["source_rows"] = rows(env)
    return env


class HarnessLoaderSourceTests(unittest.TestCase):
    assert_local_alpha = previous.ProxyLoaderSourceTests.assert_local_alpha

    def setUp(self): self.cache = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.cache))
        self.assertTrue(all(sys.modules[n] is v for n, v in self.cache.items()))

    def call(self, env): return env["ns"]["_hl_entry"]()

    def reject(self, env):
        result = self.call(env)
        self.assertEqual(result[0], "REJECTED_HARNESS_SOURCES")
        self.assertIn(result[1], ("HARNESS_SOURCE_BINDING", "HARNESS_SOURCE_REJECTED"))
        self.assertIsNone(result[2])
        return result

    def events(self, env, kind): return [e for e in env["trace"] if e[0] == kind]

    def test_actual_source_fit_raw_imports_and_independent_alpha_ast(self):
        prefix = "def _inline_need(ok, issue): pass\n_inline_need(True, 'X')\n"
        positive = subject._shorten_need(ast.parse(prefix + "held = b'_inline_need'\n"))
        self.assertEqual(ast.dump(positive), ast.dump(ast.parse(
            "def _n(ok, issue): pass\n_n(True, 'X')\nheld = b'_inline_need'\n")))
        for bad in ("pass", prefix + "_n = 1\n", prefix + "x = '_inline_need'\n",
                    prefix + "x._inline_need(1, 2)\n", prefix + "def bad(_inline_need): pass\n",
                    prefix + "def bad():\n global _inline_need\n",
                    prefix + "_inline_need = 1\n", prefix + "def _inline_need(ok, issue): pass\n"):
            with self.assertRaises(subject.base.inputs.base.BootstrapSourceRejected):
                subject._shorten_need(ast.parse(bad))
        for raw in (RAW, RAW.replace(b"\r\n", b"\n")):
            built = subject.build_harness_loader_control_bootstrap(raw, **OPTIONS)
            self.assertEqual(built.source_size, len(built.source))
            self.assertLessEqual(built.source_size, 131072)
            self.assertEqual(built.source_sha256, hashlib.sha256(built.source).hexdigest())
            self.assertFalse(built.runtime_attested or built.import_used_bytes_attested
                             or built.trust_attested or built.method_approved)
            actual = ast.parse(built.source)
            literal = next(n.value.value for n in actual.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "_EXPECTED_PROFILE_RAW" for t in n.targets))
            self.assertEqual(literal, raw)
            self.assertEqual([a.name for n in actual.body if isinstance(n, ast.Import) for a in n.names],
                             ["importlib.util", "sys", "sysconfig", "json", "struct"])
            expected = ast.parse(subject.base.inputs.build_worker_input_control_bootstrap(raw, **OPTIONS).source)
            init = next(n for n in expected.body if isinstance(n, ast.FunctionDef) and n.name == "_initialize_worker_input_control")
            block = next(n for n in init.body if isinstance(n, ast.Try)).body
            pos = next(i for i, n in enumerate(block) if isinstance(n, ast.Assign)
                and ast.unparse(n.targets[0]).startswith("(_worker_input_entry,"))
            block.insert(pos + 1, ast.parse("_hl_input_handoff(owner, _worker_input_entry)").body[0])
            receive = next(n for n in expected.body if isinstance(n, ast.FunctionDef) and n.name == "_worker_input_run")
            receive.body.insert(len(receive.body) - 1, ast.parse("_hl_eof_handoff(owner, frame, result)").body[0])
            helpers = []
            for node in ast.parse(previous.subject._INLINE_PROXY_SOURCE).body:
                if not isinstance(node, ast.FunctionDef) or node.name not in (
                    "_proxy_namespace", "_proxy_spec_state", "_proxy_original", "_proxy_guard", "_proxy_write", "_proxy_execute"):
                    continue
                for item in ast.walk(node):
                    if isinstance(item, ast.FunctionDef): item.name = item.name.replace("_proxy_", "_hl_")
                    if isinstance(item, ast.Name): item.id = "_HL_MARKER" if item.id == "_PROXY_SOURCE_MARKER" else item.id.replace("_proxy_", "_hl_")
                    if isinstance(item, ast.Constant) and type(item.value) is str:
                        item.value = "_HL_MARKER" if item.value == "_PROXY_SOURCE_MARKER" else item.value.replace("PROXY_SOURCE_", "HARNESS_SOURCE_")
                if node.name == "_hl_guard":
                    node.body[-1:] = ast.parse('''
_worker_input_function_check(owner[18], owner[3].get("__import__"), owner[3])
f, c, held = state[7][0]
_inline_need(f.__code__ is c and f.__globals__ is namespace
    and _worker_profile_function_equal(held, _worker_profile_function(f, [0])), "HARNESS_SOURCE_BINDING")
for invocation in state[5]:
    _hl_original(owner[16], namespace)(owner, invocation)
published = tuple(v[1][1] for v in state[5] if v[8] is True)
_inline_need(all(name not in owner[11] for name in _HL_OWN if name not in published), "HARNESS_SOURCE_BINDING")
''').body
                if node.name == "_hl_execute":
                    assignment = next(n for n in node.body if isinstance(n, ast.Assign)
                                      and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "invocation")
                    assignment.value = ast.parse("owner[2][8][-1]", mode="eval").body
                helpers.append(node)
            main = next(n for n in expected.body if isinstance(n, ast.If))
            main.body.insert(2, ast.parse("_initialize_hl_control()").body[0])
            main.body[-1] = ast.parse("_hl_main()").body[0]
            expected.body = [n for n in expected.body if n is not main] + helpers + ast.parse(subject._INLINE_HARNESS).body + [main]
            # Genau diese globale Umbenennung unabhängig rückführen; keine
            # lokale Bindung, zusätzliche Definition oder reflektive Referenz.
            renamed = [n for n in actual.body if isinstance(n, ast.FunctionDef) and n.name == "_n"]
            self.assertEqual(len(renamed), 1)
            self.assertEqual(sum(isinstance(n, ast.FunctionDef) and n.name == "_n" for n in ast.walk(actual)), 1)
            expected_loads = [n for n in ast.walk(expected) if isinstance(n, ast.Name) and n.id == "_inline_need"]
            actual_loads = [n for n in ast.walk(actual) if isinstance(n, ast.Name) and n.id == "_n"]
            self.assertEqual(len(actual_loads), len(expected_loads))
            self.assertTrue(all(isinstance(n.ctx, ast.Load) for n in actual_loads))
            for node in ast.walk(actual):
                for field in ("arg", "name", "asname", "rest"):
                    if node is not renamed[0]: self.assertNotEqual(getattr(node, field, None), "_n")
                if isinstance(node, (ast.Global, ast.Nonlocal)):
                    self.assertNotIn("_n", node.names)
                if isinstance(node, ast.Name): self.assertNotEqual(node.id, "_inline_need")
                if isinstance(node, ast.Attribute): self.assertNotIn(node.attr, ("_n", "_inline_need"))
                if isinstance(node, ast.Constant) and type(node.value) is str:
                    self.assertNotIn("_inline_need", node.value)
                    self.assertNotEqual(node.value, "_n")
            renamed[0].name = "_inline_need"
            for node in actual_loads: node.id = "_inline_need"
            self.assert_local_alpha(expected, actual)
            print("HARNESS_SOURCE_BYTES=" + str(built.source_size))

    def test_nested_raw_code_namespaces_wire_order_and_cachehit(self):
        for ending in (b"\n", b"\r\n"):
            env = model(bodies=tuple(b.replace(b"\n", ending) for b in BODIES))
            self.assertEqual(env["hl_initial"], ("BOUND_HARNESS_CONTROL", "NONE"))
            observed = []
            def hook(phase, code, namespace):
                observed.append((phase, code, bytes(env["io"].output), env["io"].offset))
            env["hooks"][0] = hook
            main = env["cache"]["__main__"]
            result = self.call(env)
            self.assertEqual(result[:2], ("EXECUTED_HARNESS_SOURCES", "NONE"))
            self.assertEqual(len(result[2]), 3)
            for offset, (m, s, loader, code, raw) in enumerate(result[2]):
                event = self.events(env, "COMPILE")[offset]
                self.assertIs(event[1], raw)
                self.assertEqual(raw, env["bodies"][offset + 3])
                self.assertEqual(event[2:], (code.co_filename, "exec", True, 0))
                self.assertIs(self.events(env, "CODE")[offset][1], code)
                self.assertIs(self.events(env, "EXEC")[offset][1], code)
                self.assertIs(self.events(env, "EXEC")[offset][2], m.__dict__)
                self.assertIs(env["cache"][NAMES[offset]], m)
                self.assertIs(m.__spec__, s)
                self.assertIs(m.__loader__, loader)
                self.assertEqual(s.origin, code.co_filename)
            self.assertEqual(result[2][0][0].SYNTHETIC_VALUE, 7)
            self.assertIs(env["cache"]["__main__"], main)
            self.assertTrue(all(offset == len(env["io"].input) for _, _, _, offset in observed))
            for phase, code, output, offset in observed:
                index = int(code.co_filename.rsplit("/", 1)[1][:-3])
                self.assertIn(env["source_rows"][index - 3], output)
                self.assertNotIn(env["source_rows"][8 - index], output)
            self.assertTrue(bytes(env["io"].output).endswith(b"".join(env["source_rows"])))
            self.assertEqual([e[1].co_filename for e in self.events(env, "EXEC_RETURN")],
                             ["/dgn007/source/5.py", "/dgn007/source/4.py", "/dgn007/source/3.py"])
            self.assertEqual(self.events(env, "DELEGATE"), [])
            self.assertTrue(all(n not in env["cache"] for n in ("Tests", "Tests.Contracts", "docker_sqlcmd_proxy")))

    def test_partial_confirmed_io_shares_original_budget(self):
        env = model()
        env["io"].read_max = env["io"].write_max = 64
        self.assertEqual(self.call(env)[0], "EXECUTED_HARNESS_SOURCES")
        budget = fixture.owner(env)[2]
        self.assertEqual((budget[3], budget[5]), (len(env["io"].events), len(env["io"].output)))
        self.assertLessEqual(budget[3], 1088)
        self.assertTrue(bytes(env["io"].output).endswith(b"".join(env["source_rows"])))

    def test_wrong_role_input_failure_and_existing_cache_precede_compile(self):
        for kind in ("runner", "proxy", "eof", "hash", "cache"):
            env = model(ordinal={"runner": 1, "proxy": 2}.get(kind, 3))
            foreign = object()
            if kind == "eof": env["io"].input = env["io"].input[:-1]
            if kind == "hash": env["io"].input = env["io"].input.replace(BODIES[2], BODIES[2][:-2] + b"8\n")
            if kind == "cache": env["cache"][NAMES[2]] = foreign
            self.reject(env)
            self.assertEqual(self.events(env, "COMPILE"), [])
            if kind == "cache": self.assertIs(env["cache"][NAMES[2]], foreign)
        for index in (4, 5):
            env, reached, foreign = model(), [], object()
            def hook(phase, code, namespace):
                if phase == "compiled" and code.co_filename == "/dgn007/source/" + str(index - 1) + ".py":
                    reached.append(1)
                    env["cache"][NAMES[index - 3]] = foreign
            env["hooks"][0] = hook
            self.assertEqual(self.reject(env)[1], "HARNESS_SOURCE_BINDING")
            self.assertEqual(reached, [1])
            self.assertEqual(len(self.events(env, "COMPILE")), index - 3)
            self.assertIs(env["cache"][NAMES[index - 3]], foreign)
            self.assertIn(env["source_rows"][index - 4], env["io"].output)

    def test_closed_project_routes_and_fromlists(self):
        for raw in (b"import orchestrate_sessions\n", b"from orchestrate_sessions import other\n",
                    b"from orchestrate_sessions import *\n", b"from sqlcmd_process import build_sqlcmd_command, extract_summary, resolve_sqlcmd, run_sqlcmd\n",
                    b"from execution_target import x\n", b"from Tests import x\n"):
            env = model(bodies=(raw,) + BODIES[1:])
            self.reject(env)
            self.assertEqual(len(self.events(env, "COMPILE")), 1)
            self.assertEqual(self.events(env, "DELEGATE"), [])

    def test_foreign_gateway_arguments_precede_dispatch(self):
        for expression in ("_foreign, globals(), locals(), ('run_manifest',), 0",
                           "'orchestrate_sessions', _foreign, None, ('run_manifest',), 0",
                           "'orchestrate_sessions', globals(), locals(), (_foreign,), 0",
                           "'orchestrate_sessions', globals(), locals(), ('run_manifest',), False"):
            raw = ("__import__(" + expression + ")\n").encode()
            calls = []
            class Foreign:
                def __getattribute__(self, key): calls.append(key); raise AssertionError()
                def __eq__(self, other): calls.append("EQ"); raise AssertionError()
                def __len__(self): calls.append("LEN"); raise AssertionError()
            env = model(bodies=(raw,) + BODIES[1:], extras={"_foreign": Foreign()})
            self.reject(env)
            self.assertEqual((calls, self.events(env, "DELEGATE")), ([], []))
            self.assertEqual(len(self.events(env, "EXEC")), 1)

    def test_stdlib_delegate_is_exact_and_unknown_names_are_rejected(self):
        env = model(bodies=(b"import os\n" + BODIES[0],) + BODIES[1:])
        self.assertEqual(self.call(env)[0], "EXECUTED_HARNESS_SOURCES")
        event = self.events(env, "DELEGATE")[0]
        self.assertEqual((len(self.events(env, "DELEGATE")), event[1], event[4:]), (1, "os", (None, 0)))
        for raw in (b"import synthetic_unknown\n", b"from os import path\n"):
            env = model(bodies=(raw,) + BODIES[1:])
            self.reject(env)
            self.assertEqual(self.events(env, "DELEGATE"), [])

    def test_missing_project_attribute_does_not_call_getattr(self):
        raw = BODIES[2].replace(b"collect_process = ", b"") + b'def __getattr__(name):\n _trace.append(("GETATTR", name))\n raise AssertionError()\n'
        env = model(bodies=BODIES[:2] + (raw,))
        self.reject(env)
        self.assertEqual(self.events(env, "GETATTR"), [])
        self.assertNotIn(env["source_rows"][4], env["io"].output)

    def test_compile_exec_failures_cleanup_only_own_slots(self):
        for offset in range(3):
            for broken in (b"if\n", b"raise RuntimeError('PRIVATE')\n"):
                env = model(bodies=BODIES[:offset] + (broken,) + BODIES[offset + 1:])
                result = self.reject(env)
                self.assertNotIn("PRIVATE", repr(result))
                self.assertNotIn(env["source_rows"][5], env["io"].output)
                self.assertTrue(all(n not in env["cache"] for n in NAMES))

    def test_compile_exec_import_provider_drift_is_dominant(self):
        for provider, phase in (("compile", "compiled"), ("exec", "executed"), ("__import__", "delegated")):
            env = model(bodies=(b"import os\n" + BODIES[0],) + BODIES[1:])
            reached = []
            def hook(actual, code, namespace):
                if actual == phase and not reached:
                    reached.append(1)
                    f = env["ns"]["__builtins__"][provider]
                    f.__code__ = f.__code__.replace()
            env["hooks"][0] = hook
            self.assertEqual(self.reject(env)[1], "HARNESS_SOURCE_BINDING")
            self.assertEqual(reached, [1])
            self.assertNotIn(env["source_rows"][5], env["io"].output)

    def test_completed_module_binding_is_checked_while_unwinding(self):
        calls = []
        class ForeignModule(fixture.f.ModuleType):
            def __getattribute__(self, key): calls.append(key); raise AssertionError()
        for kind in ("spec", "cache", "builtins", "class"):
            env, reached = model(), []
            foreign = object()
            def callback(io, operation):
                if reached or operation != "write" or not bytes(io.output).endswith(env["source_rows"][2]): return
                reached.append(1)
                m = env["cache"][NAMES[2]]
                if kind == "spec": m.__spec__.origin = "/synthetic/changed"
                elif kind == "cache": env["cache"][NAMES[2]] = foreign
                elif kind == "builtins": m.__builtins__["__import__"] = foreign
                else: m.__class__ = ForeignModule
            env["io"].callback = callback
            self.assertEqual(self.reject(env)[1], "HARNESS_SOURCE_BINDING")
            self.assertEqual(reached, [1])
            self.assertTrue(bytes(env["io"].output).endswith(env["source_rows"][3]))
            self.assertNotIn(env["source_rows"][4], env["io"].output)
            if kind == "cache": self.assertIs(env["cache"][NAMES[2]], foreign)
        self.assertEqual(calls, [])

    def test_duplicate_cachehit_and_late_cache_replacement_are_rejected(self):
        env = model(bodies=(BODIES[0] + b"from sqlcmd_process import build_sqlcmd_command, extract_summary, resolve_sqlcmd, run_sqlcmd\n",) + BODIES[1:])
        self.reject(env)
        self.assertEqual(len(self.events(env, "COMPILE")), 3)
        env, reached, foreign = model(), [], object()
        def callback(io, operation):
            if operation == "write" and not reached and bytes(io.output).endswith(env["source_rows"][3]):
                reached.append(1)
                env["cache"][NAMES[2]] = foreign
        env["io"].callback = callback
        self.reject(env)
        self.assertEqual(reached, [1])
        self.assertIs(env["cache"][NAMES[2]], foreign)

    def test_reentrancy_and_loader_before_begin_are_sticky(self):
        for kind in ("entry", "loader", "compile_gateway"):
            env, reached = model(), []
            def callback(io, operation):
                if reached or operation != "write" or not bytes(io.output).endswith(fixture.wire(env["payload"], env["bodies"])[2]): return
                reached.append(1)
                if kind == "entry": self.call(env)
                else:
                    cls = env["ns"]["_HL_CLASS"]
                    try: cls().exec_module(env["cache"][NAMES[0]])
                    except BaseException: pass
            if kind == "compile_gateway":
                def hook(phase, code, namespace):
                    if phase == "compiled" and not reached:
                        reached.append(1)
                        m = env["cache"][NAMES[0]]
                        try: m.__builtins__["__import__"]("orchestrate_sessions", m.__dict__, m.__dict__, ("run_manifest",), 0)
                        except BaseException: pass
                env["hooks"][0] = hook
            else: env["io"].callback = callback
            self.reject(env)
            self.assertEqual(reached, [1])
            self.assertNotIn(env["source_rows"][1], env["io"].output)

    def test_bad_source_write_counts_and_foreign_code_are_closed(self):
        for value in (0, True, object()):
            env, reached = model(), []
            def callback(io, operation):
                if operation == "write" and not reached and bytes(io.output).endswith(fixture.wire(env["payload"], env["bodies"])[2]):
                    reached.append(1)
                    io.write_value = lambda data: value
            env["io"].callback = callback
            self.reject(env)
            self.assertEqual(reached, [1])
            self.assertEqual(self.events(env, "COMPILE"), [])
        env = model()
        env["results"][0] = object()
        self.reject(env)
        self.assertEqual(self.events(env, "EXEC"), [])

    def test_same_caps_and_partial_begin_exhaustion_precede_compile(self):
        for slot, value in ((3, 1088), (5, 65536), (4, True), (6, False)):
            env, reached = model(), []
            def callback(io, operation):
                if not reached and operation == "read" and io.offset == len(io.input):
                    reached.append(1)
                    fixture.owner(env)[2][slot] = value
            env["io"].callback = callback
            self.reject(env)
            self.assertEqual((reached, self.events(env, "COMPILE")), ([1], []))

    def test_retry_marker_missing_init_and_public_entry_are_not_authority(self):
        for kind in ("retry", "marker", "missing", "entry"):
            env = model(initialize=kind != "missing")
            if kind == "marker": env["ns"]["_HL_MARKER"] = object()
            if kind == "entry": env["ns"]["_worker_input_entry"] = lambda: ("RECEIVED_WORKER_INPUTS", "NONE", ())
            if kind == "retry": self.assertEqual(self.call(env)[0], "EXECUTED_HARNESS_SOURCES")
            before = (len(self.events(env, "COMPILE")), len(env["io"].events))
            self.reject(env)
            self.assertEqual((len(self.events(env, "COMPILE")), len(env["io"].events)), before if kind == "retry" else (0, len(env["io"].events)))


if __name__ == "__main__":
    unittest.main()
