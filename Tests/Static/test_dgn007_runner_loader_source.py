"""Eigene vollständige Runnerbodies; keine tatsächlichen Projektquellen ausführen."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import symtable
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_harness_loader_source as previous
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_runner_loader_source as subject

fixture = previous.fixture
RAW, OPTIONS = fixture.RAW, fixture.OPTIONS
ORDER = (0, 1, 5, 3, 4, 6, 7, 8)
NAMES = ("run_dgn007_automated_setup", "execution_target", "docker_sqlcmd_proxy", "run_demo",
         "orchestrate_sessions", "sqlcmd_process", "Tests.Contracts.dgn007_capture_projection",
         "Tests.Contracts.dgn007_collector_transport", "Tests.Contracts.dgn007_prospective_acceptance")
BODIES = (
    b"import execution_target\nfrom execution_target import ExecutionTarget, ExecutionTargetError\nfrom run_demo import load_manifest\n"
    b"from sqlcmd_process import SqlcmdResult, build_sqlcmd_command, run_sqlcmd\nfrom sqlcmd_process import start_sqlcmd, _terminate_process_tree\n"
    b"from sqlcmd_process import _linux_descendants, _linux_process_identity\n"
    b"from Tests.Contracts.dgn007_capture_projection import decode_projection, ProjectionError\n"
    b"from Tests.Contracts.dgn007_collector_transport import CaptureBody\n"
    b"from Tests.Contracts.dgn007_prospective_acceptance import contract_from_mapping\nSYNTHETIC_VALUE = decode_projection\n",
    b"from sqlcmd_process import resolve_sqlcmd\nExecutionTarget = ExecutionTargetError = resolve_sqlcmd\n",
    b"\xff\0opaque-proxy",
    previous.BODIES[0] + b"load_manifest = run_manifest\n",
    previous.BODIES[1],
    previous.BODIES[2] + b"SqlcmdResult = _terminate_process_tree = _linux_descendants = _linux_process_identity = 7\n",
    b"from Tests.Contracts.dgn007_collector_transport import CaptureBody, SCHEMA, TransportError, decode_capture\n"
    b"from Tests.Contracts.dgn007_prospective_acceptance import AcceptanceContract, _contract_valid\n"
    b"decode_projection = ProjectionError = CaptureBody\n",
    b"from Tests.Contracts.dgn007_prospective_acceptance import AcceptanceContract, ActivePlanRecord, MAX_SQL_TICKS, PlanUnionRecord, QueryFamilyRecord, REQUEST_MAPPING, WindowRecord, _contract_valid\n"
    b"CaptureBody = SCHEMA = TransportError = decode_capture = AcceptanceContract\n",
    b"AcceptanceContract = ActivePlanRecord = MAX_SQL_TICKS = PlanUnionRecord = QueryFamilyRecord = REQUEST_MAPPING = WindowRecord = _contract_valid = contract_from_mapping = 7\n")
TRACE = (("BEGIN", "SOURCE", 0, 1), ("BEGIN", "SOURCE", 1, 2), ("BEGIN", "SOURCE", 5, 3),
    ("COMPLETE", "SOURCE", 5, 3), ("COMPLETE", "SOURCE", 1, 2), ("BEGIN", "SOURCE", 3, 4),
    ("BEGIN", "SOURCE", 4, 5), ("COMPLETE", "SOURCE", 4, 5), ("COMPLETE", "SOURCE", 3, 4),
    ("BEGIN", "PARENT", 0, 6), ("COMPLETE", "PARENT", 0, 6), ("BEGIN", "PARENT", 1, 7),
    ("COMPLETE", "PARENT", 1, 7), ("BEGIN", "SOURCE", 6, 8), ("BEGIN", "SOURCE", 7, 9),
    ("BEGIN", "SOURCE", 8, 10), ("COMPLETE", "SOURCE", 8, 10), ("COMPLETE", "SOURCE", 7, 9),
    ("COMPLETE", "SOURCE", 6, 8), ("COMPLETE", "SOURCE", 0, 1))


def rows(env):
    digest = hashlib.sha256(fixture.fixture.pooled((env["payload"][2],), "pooled-profile-binding-context/v1")).hexdigest()
    return tuple(json.dumps([tag, 1, seq, kind, index, digest,
        None if kind == "PARENT" else hashlib.sha256(env["bodies"][index]).hexdigest(),
        index + 9 if kind == "PARENT" else index, seq], separators=(",", ":"), ensure_ascii=True).encode() + b"\n"
        for tag, kind, index, seq in TRACE)


def model(*, bodies=BODIES, ordinal=1, extras=None):
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
        env["runner_initial"] = env["ns"]["_initialize_rl_control"]()
    env = fixture.model(ordinal=ordinal, bodies=bodies, before_io=setup,
                        builder=subject.build_runner_loader_control_bootstrap)
    env.update(trace=trace, hooks=hooks, results=results)
    env["source_rows"] = rows(env)
    return env


def owner(env):
    entry = env["ns"]["_rl_entry"]
    return dict(zip(entry.__code__.co_freevars, (c.cell_contents for c in entry.__closure__)))["o"]


class RunnerLoaderSourceTests(unittest.TestCase):
    assert_local_alpha = previous.HarnessLoaderSourceTests.assert_local_alpha

    def setUp(self): self.modules = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.modules))
        self.assertTrue(all(sys.modules[k] is v for k, v in self.modules.items()))

    def call(self, env): return env["ns"]["_rl_entry"]()

    def events(self, env, kind): return [e for e in env["trace"] if e[0] == kind]

    def reject(self, env):
        result = self.call(env)
        self.assertEqual(result[0], "REJECTED_RUNNER_SOURCES")
        self.assertIn(result[1], ("RUNNER_SOURCE_BINDING", "RUNNER_SOURCE_REJECTED"))
        self.assertIsNone(result[2])
        return result

    def inverse_uniform(self, expected, actual):
        # Aus gepaarten Bäumen abgeleitet; keine Produktmap/-Auswahl verwenden.
        left, right = tuple(ast.walk(expected)), tuple(ast.walk(actual))
        self.assertEqual([type(n) for n in left], [type(n) for n in right])
        parent_nodes = {id(n) for p in expected.body if isinstance(p, ast.FunctionDef)
                        and p.name == "make_codefree_parent_registry" for n in ast.walk(p)}
        pairs = []
        for a, b in zip(left, right):
            if id(a) in parent_nodes: continue
            if isinstance(a, ast.Name): pairs.append((a.id, b.id))
            elif isinstance(a, ast.arg): pairs.append((a.arg, b.arg))
            elif isinstance(a, ast.ExceptHandler) and a.name: pairs.append((a.name, b.name))
            elif isinstance(a, ast.Nonlocal):
                self.assertEqual(len(a.names), len(b.names))
                pairs.extend(zip(a.names, b.names))
        mapping = {}
        for old, new in pairs:
            if old != new and new.startswith("z") and new[1:].isdigit():
                self.assertEqual(mapping.setdefault(old, new), new)
        self.assertEqual(len(mapping), len(set(mapping.values())))
        originals = {getattr(n, f, None) for n in left for f in ("id", "arg", "name", "asname", "rest", "attr")}
        originals.update(name for n in left if isinstance(n, (ast.Global, ast.Nonlocal)) for name in n.names)
        texts = [n.value for n in left if isinstance(n, ast.Constant) and type(n.value) is str]
        tables = [symtable.symtable(ast.unparse(expected), "<independent-alpha-oracle>", "exec")]
        blocked = set()
        while tables:
            table = tables.pop(0)
            originals.update(table.get_identifiers())
            blocked.update(s.get_name() for s in table.get_symbols() if s.is_global() or table.get_type() == "class")
            tables += table.get_children()
        public = {"_worker_input_seal", "_worker_input_entry", "_worker_profile_state",
                  "_inline_observe_selected_worker_profile", "_inline_kernel_check", "entry", "seal",
                  "handoff", "gateway", "input_handoff", "eof_handoff", "parent_guard", "parent_write",
                  "create_module", "exec_module"}
        def boundary(node, enclosing=()):
            path = enclosing + ((node,) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)) else ())
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in public or (enclosing and isinstance(enclosing[-1], ast.ClassDef)):
                    blocked.update(a.arg for a in ast.walk(node.args) if isinstance(a, ast.arg))
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ("locals", "vars", "eval", "exec")):
                for n in ast.walk(path[0] if path else expected):
                    blocked.update(getattr(n, f, None) for f in ("id", "arg", "name", "asname", "rest"))
            if isinstance(node, (ast.Match, ast.TypeAlias)):
                for n in ast.walk(node):
                    blocked.update(getattr(n, f, None) for f in ("id", "arg", "name", "asname", "rest"))
            for child in ast.iter_child_nodes(node): boundary(child, path)
        boundary(expected)
        for n in left:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.alias)): blocked.add(n.name)
            if isinstance(n, ast.alias): blocked.add(n.asname)
            if isinstance(n, ast.Attribute): blocked.add(n.attr)
            if isinstance(n, ast.keyword): blocked.add(n.arg)
        for old, new in mapping.items():
            self.assertGreaterEqual(len(old), 4)
            self.assertFalse(old.startswith("__"))
            self.assertNotIn(old, blocked)
            self.assertNotIn(new, originals)
            self.assertTrue(all(old not in s and new not in s for s in texts))
        for old, new in pairs:
            if old in mapping: self.assertEqual(new, mapping[old])
        inverse = {new: old for old, new in mapping.items()}
        for n in right:
            if isinstance(n, ast.Name): n.id = inverse.get(n.id, n.id)
            elif isinstance(n, ast.arg): n.arg = inverse.get(n.arg, n.arg)
            elif isinstance(n, ast.ExceptHandler): n.name = inverse.get(n.name, n.name)
            elif isinstance(n, ast.Nonlocal): n.names = [inverse.get(s, s) for s in n.names]
        return mapping

    def test_actual_source_fit_full_raw_parent_and_independent_alpha_ast(self):
        # Kleines eigenes Alpha-Modell: Globalgleichnamigkeit, Defaults,
        # Erstiterable, Closures/Shadowing, Keywords, Methoden und Reflexion.
        sample = '''global_value = 7
def outer(argument_long, keyword_kept=1):
 captured_long = argument_long
 def inner(shadow_long):
  nonlocal captured_long
  captured_long += shadow_long
  return captured_long
 sequence_long = [element_long for element_long in range(argument_long)]
 try:
  temporary_long = inner(argument_long)
 except ValueError as failure_long:
  temporary_long = failure_long
 return sequence_long, temporary_long, keyword_kept
def global_reader(): return global_value
def local_writer(global_value): return global_value
def default_reader(another_long=global_value): return another_long
def comp_reader(): return [global_value for global_value in global_value]
def keyword_user(): return outer(1, keyword_kept=2)
def reflected(reflected_long): return locals()
def collision_long(longer_local):
 global z0
 return longer_local
class Example:
 class_slot_long = 1
 def method(self, method_argument): return method_argument
'''
        parent_model = ast.parse("def fixed_parent(): return None").body[0]
        before = ast.parse(sample)
        changed = subject._shorten_uniform_locals(ast.parse(sample), parent_model)
        mapping = self.inverse_uniform(before, changed)
        self.assertIn("argument_long", mapping)
        self.assertIn("captured_long", mapping)
        self.assertIn("element_long", mapping)
        self.assertTrue(all(n not in mapping for n in ("global_value", "keyword_kept", "reflected_long", "method_argument", "class_slot_long")))
        self.assertNotIn("z0", mapping.values())
        self.assertEqual(ast.dump(before), ast.dump(changed))
        collision = ast.parse("def f(longer_local):\n global z0\n return longer_local\n")
        invalid = ast.parse(ast.unparse(collision))
        invalid.body[0].args.args[0].arg = "z0"
        invalid.body[0].body[1].value.id = "z0"
        with self.assertRaises(AssertionError): self.inverse_uniform(collision, invalid)
        for raw_sample in (b"a\nb\r\n", b"'''\"\"\"\\\0\t\x0b\x0c\x7f\xff\n", b"\n" * 40):
            text = "_EXPECTED_PROFILE_RAW = " + repr(raw_sample) + "\n"
            rendered = subject._compact_raw_literal(text, raw_sample)
            self.assertEqual(ast.dump(ast.parse(text)), ast.dump(ast.parse(rendered)))
            self.assertLessEqual(len(rendered.encode()), len(text.encode()))
        parent = next(n for n in ast.parse(Path(subject.parents.__file__).read_bytes()).body if isinstance(n, ast.FunctionDef))
        for raw in (RAW, RAW.replace(b"\r\n", b"\n")):
            built = subject.build_runner_loader_control_bootstrap(raw, **OPTIONS)
            self.assertLessEqual(built.source_size, 131072)
            self.assertEqual(built.source_size, len(built.source))
            self.assertEqual(built.source_sha256, hashlib.sha256(built.source).hexdigest())
            self.assertFalse(built.runtime_attested or built.import_used_bytes_attested or built.trust_attested or built.method_approved)
            actual = ast.parse(built.source)
            self.assertEqual([a.name for n in actual.body if isinstance(n, ast.Import) for a in n.names],
                             ["importlib.util", "sys", "sysconfig", "json", "struct"])
            self.assertEqual(next(n.value.value for n in actual.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "_EXPECTED_PROFILE_RAW" for t in n.targets)), raw)
            held_parent = next(n for n in actual.body if isinstance(n, ast.FunctionDef) and n.name == parent.name)
            self.assertEqual(ast.dump(held_parent), ast.dump(parent))
            expected = ast.parse(subject.base.base.inputs.build_worker_input_control_bootstrap(raw, **OPTIONS).source)
            init = next(n for n in expected.body if isinstance(n, ast.FunctionDef) and n.name == "_initialize_worker_input_control")
            block = next(n for n in init.body if isinstance(n, ast.Try)).body
            at = next(i for i, n in enumerate(block) if isinstance(n, ast.Assign)
                      and ast.unparse(n.targets[0]).startswith("(_worker_input_entry,"))
            block.insert(at + 1, ast.parse("_rl_input_handoff(owner, _worker_input_entry)").body[0])
            receiver = next(n for n in expected.body if isinstance(n, ast.FunctionDef) and n.name == "_worker_input_run")
            receiver.body.insert(len(receiver.body) - 1, ast.parse("_rl_eof_handoff(owner, frame, result)").body[0])
            helpers = []
            for n in ast.parse(previous.previous.subject._INLINE_PROXY_SOURCE).body:
                if not isinstance(n, ast.FunctionDef) or n.name not in (
                    "_proxy_namespace", "_proxy_spec_state", "_proxy_original", "_proxy_guard", "_proxy_write", "_proxy_execute"): continue
                for value in ast.walk(n):
                    if isinstance(value, ast.FunctionDef): value.name = value.name.replace("_proxy_", "_rl_")
                    if isinstance(value, ast.Name): value.id = "_RL_MARKER" if value.id == "_PROXY_SOURCE_MARKER" else value.id.replace("_proxy_", "_rl_")
                    if isinstance(value, ast.Constant) and type(value.value) is str:
                        value.value = "_RL_MARKER" if value.value == "_PROXY_SOURCE_MARKER" else value.value.replace("PROXY_SOURCE_", "RUNNER_SOURCE_")
                if n.name == "_rl_guard":
                    n.body[-1:] = ast.parse('''
_worker_input_function_check(owner[18], owner[3].get("__import__"), owner[3])
f, c, held = state[7][0]
_inline_need(f.__code__ is c and f.__globals__ is namespace
    and _worker_profile_function_equal(held, _worker_profile_function(f, [0])), "RUNNER_SOURCE_BINDING")
for invocation in state[5]:
    _rl_original(owner[16], namespace)(owner, invocation)
published = tuple(v[1][1] for v in state[5] if v[8] is True)
_inline_need(all(name not in owner[11] for name in _RL_NAMES if name not in published), "RUNNER_SOURCE_BINDING")
_rl_original(owner[19], namespace)(owner, packet)
''').body
                if n.name == "_rl_execute":
                    next(v for v in n.body if isinstance(v, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "invocation" for t in v.targets)).value = ast.parse("owner[2][8][-1]", mode="eval").body
                helpers.append(n)
            template = ast.parse(previous.subject._INLINE_HARNESS.replace("_hl_", "_rl_").replace("_HL_", "_RL_").replace("HARNESS", "RUNNER"))
            added = ast.parse(subject._INLINE_RUNNER).body
            function_names = {n.name for n in added if isinstance(n, ast.FunctionDef)}
            constant_names = {t.id for n in added if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)} | {"_RL_COMMON"}
            kept = [n for n in template.body if not (isinstance(n, ast.FunctionDef) and n.name in function_names)
                and not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constant_names for t in n.targets))]
            main = next(n for n in expected.body if isinstance(n, ast.If))
            main.body.insert(2, ast.parse("_initialize_rl_control()").body[0])
            main.body[-1] = ast.parse("_rl_main()").body[0]
            expected.body = [n for n in expected.body if n is not main] + helpers + kept + added + [parent, main]
            definitions = [n for n in expected.body if isinstance(n, ast.FunctionDef)]
            observed = [n for n in actual.body if isinstance(n, ast.FunctionDef)]
            self.assertEqual(len(definitions), len(observed))
            original_nodes = tuple(ast.walk(expected))
            identifiers = {getattr(n, f, None) for n in original_nodes for f in ("id", "arg", "name", "asname", "rest", "attr")}
            identifiers.update(s for n in original_nodes if isinstance(n, (ast.Global, ast.Nonlocal)) for s in n.names)
            strings = [n.value for n in original_nodes if isinstance(n, ast.Constant) and type(n.value) is str]
            inverse = {}
            preserved = {"_worker_input_seal", "_worker_input_entry", "_worker_profile_state",
                         "_inline_observe_selected_worker_profile", "_inline_kernel_check", parent.name}
            for before, after in zip(definitions, observed):
                if before.name == after.name: continue
                old, new = before.name, after.name
                self.assertTrue(old.startswith(("_inline_", "_semantic_", "_worker_profile_", "_worker_input_", "_report_", "_rl_", "_worker_report_")) or old in ("_require", "_dictionary"))
                self.assertNotIn(old, preserved)
                self.assertNotIn(new, identifiers)
                self.assertTrue(all(old not in t and new not in t for t in strings))
                self.assertNotIn(new, inverse)
                self.assertEqual(sum(isinstance(n, ast.FunctionDef) and n.name == old for n in original_nodes), 1)
                for node in original_nodes:
                    if isinstance(node, ast.Name) and node.id == old: self.assertIsInstance(node.ctx, ast.Load)
                    if isinstance(node, (ast.Global, ast.Nonlocal)): self.assertNotIn(old, node.names)
                    if isinstance(node, ast.Attribute): self.assertNotEqual(node.attr, old)
                    if node is not before:
                        for field in ("arg", "name", "asname", "rest"): self.assertNotEqual(getattr(node, field, None), old)
                inverse[new] = old
                self.assertEqual(sum(isinstance(n, ast.Name) and n.id == old for n in original_nodes),
                                 sum(isinstance(n, ast.Name) and n.id == new for n in ast.walk(actual)))
                after.name = old
            self.assertTrue(inverse)
            for node in ast.walk(actual):
                if isinstance(node, ast.Name) and node.id in inverse:
                    self.assertIsInstance(node.ctx, ast.Load)
                    node.id = inverse[node.id]
                for field in ("arg", "name", "asname", "rest", "attr"):
                    self.assertNotIn(getattr(node, field, None), inverse)
                if isinstance(node, (ast.Global, ast.Nonlocal)):
                    self.assertTrue(all(n not in inverse for n in node.names))
            self.assertTrue(self.inverse_uniform(expected, actual))
            self.assert_local_alpha(expected, actual)
            print("RUNNER_SOURCE_BYTES=" + str(built.source_size))

    def test_full_nested_raw_code_namespace_wire_and_cache_reuse(self):
        for ending in (b"\n", b"\r\n"):
            env = model(bodies=tuple(b.replace(b"\n", ending) for b in BODIES))
            self.assertEqual(env["runner_initial"], ("BOUND_RUNNER_CONTROL", "NONE"))
            snapshots = []
            env["hooks"][0] = lambda phase, code, ns: snapshots.append((phase, code, bytes(env["io"].output), env["io"].offset))
            main = env["cache"]["__main__"]
            result = self.call(env)
            self.assertEqual(result[:2], ("EXECUTED_RUNNER_SOURCES", "NONE"))
            sources, package = result[2]
            self.assertEqual((len(sources), len(package)), (8, 2))
            for offset, (m, spec, loader, code, raw) in enumerate(sources):
                index = ORDER[offset]
                event = self.events(env, "COMPILE")[offset]
                self.assertIs(event[1], raw)
                self.assertEqual(raw, env["bodies"][index])
                self.assertEqual(event[2:], (code.co_filename, "exec", True, 0))
                self.assertEqual(code.co_filename, "/dgn007/source/" + str(index) + ".py")
                self.assertIs(self.events(env, "CODE")[offset][1], code)
                self.assertIs(self.events(env, "EXEC")[offset][1], code)
                self.assertIs(self.events(env, "EXEC")[offset][2], m.__dict__)
                self.assertIs(env["cache"][NAMES[index]], m)
                self.assertIs(m.__spec__, spec)
                self.assertIs(m.__loader__, loader)
                self.assertEqual(spec.origin, code.co_filename)
                self.assertEqual(m.__package__, "Tests.Contracts" if index >= 6 else "")
            self.assertEqual(sources[0][0].SYNTHETIC_VALUE, 7)
            self.assertEqual([e[1].co_filename for e in self.events(env, "EXEC_RETURN")],
                ["/dgn007/source/" + str(i) + ".py" for i in (5, 1, 4, 3, 8, 7, 6, 0)])
            for i, (m, spec, locations) in enumerate(package):
                self.assertIs(m.__path__, locations)
                self.assertIs(spec.submodule_search_locations, locations)
                self.assertIsNone(spec.origin)
                self.assertNotIn("__file__", m.__dict__)
                self.assertEqual(locations, [])
            self.assertIs(package[0][0].Contracts, package[1][0])
            for index in (6, 7, 8):
                self.assertIs(package[1][0].__dict__[NAMES[index].rsplit(".", 1)[1]], env["cache"][NAMES[index]])
            self.assertTrue(bytes(env["io"].output).endswith(b"".join(env["source_rows"])))
            self.assertTrue(all(offset == len(env["io"].input) for _, _, _, offset in snapshots))
            for phase, code, output, offset in snapshots:
                index = int(code.co_filename.rsplit("/", 1)[1][:-3])
                begin = next(row for row, fields in zip(env["source_rows"], TRACE) if fields[:3] == ("BEGIN", "SOURCE", index))
                self.assertIn(begin, output)
                complete = next(row for row, fields in zip(env["source_rows"], TRACE) if fields[:3] == ("COMPLETE", "SOURCE", index))
                self.assertNotIn(complete, output)
            self.assertIs(env["cache"]["__main__"], main)
            self.assertNotIn(NAMES[2], env["cache"])
            self.assertEqual(self.events(env, "DELEGATE"), [])

    def test_parent_factory_original_anchors_and_actual_digest_handoff(self):
        env = model()
        o = owner(env)
        held = o[2][13][0]
        self.assertEqual(o[2][14], [False, False, [], [], []])
        self.assertIs(held[0].__code__, held[1])
        self.assertIs(held[0].__globals__, held[2])
        self.assertIsNot(held[2], env["ns"])
        calls = []
        def observe(frame, event, arg):
            if event == "call" and frame.f_code is held[1]: calls.append("factory")
            if event == "call" and frame.f_code is held[5]: calls.append("run")
        original = sys.getprofile()
        try:
            sys.setprofile(observe)
            result = self.call(env)
        finally:
            sys.setprofile(original)
        self.assertEqual(result[0], "EXECUTED_RUNNER_SOURCES")
        self.assertEqual(calls, ["factory", "run"])
        entry = o[2][14][2][0]
        self.assertIs(entry.__code__, held[5])
        self.assertIs(entry.__globals__, held[2])
        current = tuple(sorted(held[2].items()))
        self.assertEqual(tuple(k for k, v in current), tuple(k for k, v in held[3]))
        self.assertTrue(all(a[1] is b[1] for a, b in zip(current, held[3])))
        expected = hashlib.sha256(fixture.fixture.pooled((env["payload"][2],), "pooled-profile-binding-context/v1")).hexdigest()
        self.assertTrue(all(json.loads(row)[5] == expected for row in env["source_rows"]))
        early = b"from Tests.Contracts.dgn007_capture_projection import decode_projection, ProjectionError\n"
        env = model(bodies=(early + BODIES[0],) + BODIES[1:])
        held = owner(env)[2][13][0]
        calls = []
        original = sys.getprofile()
        try:
            sys.setprofile(observe)
            self.reject(env)
        finally:
            sys.setprofile(original)
        self.assertEqual(calls, [])
        self.assertEqual(len(self.events(env, "EXEC")), 1)
        self.assertEqual(owner(env)[2][14], [False, False, [], [], []])
        self.assertTrue(all(b'"PARENT"' not in row for row in bytes(env["io"].output).splitlines()))

    def test_closed_edges_fromlists_and_stdlib_delegate(self):
        for call in (b"import unknown", b"from sqlcmd_process import *", b"from execution_target import Missing"):
            bodies = (call + b"\n",) + BODIES[1:]
            env = model(bodies=bodies)
            self.reject(env)
            self.assertEqual(len(self.events(env, "COMPILE")), 1)
            self.assertEqual(self.events(env, "DELEGATE"), [])
        env = model(bodies=(b"import os\n" + BODIES[0],) + BODIES[1:])
        self.assertEqual(self.call(env)[0], "EXECUTED_RUNNER_SOURCES")
        self.assertEqual([e[1] for e in self.events(env, "DELEGATE")], ["os"])

    def test_wrong_roles_missing_eof_and_preexisting_foreign_slots(self):
        for ordinal in (2, 3):
            env = model(ordinal=ordinal)
            self.reject(env)
            self.assertEqual(self.events(env, "COMPILE"), [])
        env = model()
        env["io"].input += b"x"
        self.reject(env)
        self.assertEqual(self.events(env, "COMPILE"), [])
        for name in (NAMES[8], "Tests", "Tests.Contracts"):
            env = model()
            foreign = fixture.f.ModuleType("foreign")
            env["cache"][name] = foreign
            self.reject(env)
            self.assertIs(env["cache"][name], foreign)
            self.assertEqual(self.events(env, "COMPILE"), [])

    def test_late_foreign_source_and_parent_slots_are_not_overwritten(self):
        for name in (NAMES[8], "Tests.Contracts"):
            env, reached = model(), []
            foreign = fixture.f.ModuleType("foreign")
            def hook(phase, code, namespace):
                if phase == "compiled" and code.co_filename.endswith("/0.py"):
                    env["cache"][name] = foreign
                    reached.append(True)
            env["hooks"][0] = hook
            self.reject(env)
            self.assertEqual(reached, [True])
            self.assertIs(env["cache"][name], foreign)
            self.assertEqual(len(self.events(env, "COMPILE")), 1)

    def test_original_parent_factory_namespace_and_callback_drift(self):
        for kind in ("factory", "namespace", "guard"):
            env, reached = model(), []
            held = owner(env)[2][13][0]
            def hook(phase, code, namespace):
                if phase == "compiled" and code.co_filename.endswith("/0.py"):
                    reached.append(True)
                    if kind == "factory": held[0].__code__ = held[0].__code__.replace()
                    elif kind == "namespace": held[2]["__name__"] = "foreign"
                    else: held[6][0][0].__code__ = held[6][0][0].__code__.replace()
            env["hooks"][0] = hook
            self.reject(env)
            self.assertEqual(reached, [True])
            self.assertNotIn("Tests", env["cache"])

    def test_returned_parent_run_code_drift_before_first_record(self):
        for kind in ("run", "cell", "helper_code"):
            env, reached = model(), []
            def io_hook(io, phase):
                st = owner(env)[2]
                if phase == "write" and st[14][2] and not reached:
                    entry = st[14][2][0]
                    if kind == "run": entry.__code__ = entry.__code__.replace()
                    else:
                        cell = dict(zip(entry.__code__.co_freevars, entry.__closure__))["close"]
                        if kind == "cell": cell.cell_contents = lambda: None
                        else: cell.cell_contents.__code__ = cell.cell_contents.__code__.replace()
                    reached.append(True)
            env["io"].callback = io_hook
            self.reject(env)
            self.assertEqual(reached, [True])
            self.assertEqual(len(self.events(env, "COMPILE")), 5)
            self.assertNotIn(NAMES[6], env["cache"])

    def test_parent_spec_locations_and_foreign_child_drift(self):
        for kind in ("spec", "locations", "child"):
            env, reached, held = model(), [], []
            foreign = object()
            def io_hook(io, phase):
                if phase == "write" and "Tests" in env["cache"] and not reached:
                    m = env["cache"]["Tests"]
                    held.append(m)
                    reached.append(True)
                    if kind == "spec": m.__spec__.origin = "foreign"
                    elif kind == "locations": m.__path__.append("foreign")
                    else: m.Contracts = foreign
            env["io"].callback = io_hook
            self.reject(env)
            self.assertEqual(reached, [True])
            self.assertEqual(len(self.events(env, "COMPILE")), 5)
            self.assertNotIn("Tests", env["cache"])
            if kind == "child": self.assertIs(held[0].Contracts, foreign)

    def test_package_child_links_remain_bound_during_source_execution(self):
        env, reached, package = model(), [], []
        foreign = object()
        def hook(phase, code, namespace):
            if phase == "compiled" and code.co_filename.endswith("/6.py"):
                m = env["cache"]["Tests.Contracts"]
                package.append(m)
                m.dgn007_collector_transport = foreign
                reached.append(True)
        env["hooks"][0] = hook
        self.reject(env)
        self.assertEqual(reached, [True])
        self.assertEqual(len(self.events(env, "COMPILE")), 6)
        self.assertIs(package[0].dgn007_collector_transport, foreign)
        self.assertTrue(all(name not in env["cache"] for name in NAMES + ("Tests", "Tests.Contracts")))

    def test_compile_exec_failures_do_not_complete_or_keep_own_slots(self):
        for index, body in ((0, b"def ?"), (5, b"raise RuntimeError('PRIVATE_SYNTHETIC')"),
                            (8, b"raise RuntimeError('PRIVATE_SYNTHETIC')")):
            bodies = BODIES[:index] + (body,) + BODIES[index + 1:]
            env = model(bodies=bodies)
            result = self.reject(env)
            self.assertNotIn("PRIVATE_SYNTHETIC", repr(result))
            self.assertTrue(all(name not in env["cache"] for name in NAMES + ("Tests", "Tests.Contracts")))
            self.assertNotIn(env["source_rows"][-1], bytes(env["io"].output))

    def test_original_compile_exec_import_provider_drift(self):
        for name in ("compile", "exec", "__import__"):
            env, reached = model(), []
            def hook(phase, code, namespace):
                if phase == "compiled" and code.co_filename.endswith("/0.py"):
                    fn = env["ns"]["__builtins__"][name]
                    fn.__code__ = fn.__code__.replace()
                    reached.append(True)
            env["hooks"][0] = hook
            self.reject(env)
            self.assertEqual(reached, [True])
            self.assertNotIn(env["source_rows"][-1], bytes(env["io"].output))

    def test_partial_writes_and_original_budget_holders(self):
        env = model()
        env["io"].read_max, env["io"].write_max = 64, 64
        self.assertEqual(self.call(env)[0], "EXECUTED_RUNNER_SOURCES")
        self.assertTrue(bytes(env["io"].output).endswith(b"".join(env["source_rows"])))
        io_owner = owner(env)[2][3][0][0]
        self.assertEqual(io_owner[2][3], len(env["io"].events))
        self.assertLessEqual(io_owner[2][3], 1088)
        self.assertLessEqual(io_owner[2][5], 65536)
        for bad in (True, 1064961):
            env, reached = model(), []
            def hook(phase, code, namespace):
                if phase == "compiled" and code.co_filename.endswith("/0.py"):
                    owner(env)[2][3][0][0][2][4] = bad
                    reached.append(True)
            env["hooks"][0] = hook
            self.reject(env)
            self.assertEqual(reached, [True])

    def test_foreign_gateway_primitive_checks_reach_without_dispatch(self):
        calls = []
        class Foreign:
            def __len__(self): calls.append("len"); raise AssertionError()
            def __eq__(self, other): calls.append("eq"); raise AssertionError()
            def __getattribute__(self, name): calls.append("get"); raise AssertionError()
        for arguments in (b"_foreign, globals(), globals(), None, 0",
                          b"'execution_target', globals(), globals(), None, False",
                          b"'execution_target', globals(), globals(), (_foreign,), 0"):
            bodies = (b"__import__(" + arguments + b")\n",) + BODIES[1:]
            env = model(bodies=bodies, extras={"_foreign": Foreign()})
            self.reject(env)
            self.assertEqual(len(self.events(env, "EXEC")), 1)
        self.assertEqual(calls, [])

    def test_reentry_direct_loader_and_retry_are_sticky(self):
        for kind in ("entry", "loader"):
            env, reached = model(), []
            def hook(phase, code, namespace):
                if phase == "compiled" and code.co_filename.endswith("/0.py"):
                    reached.append(True)
                    if kind == "entry": self.call(env)
                    else:
                        o = owner(env)
                        try: o[2][6][0][2](o[2][6][0][1][0], env["cache"][NAMES[0]])
                        except BaseException: pass
            env["hooks"][0] = hook
            self.reject(env)
            self.assertEqual(reached, [True])
            before = bytes(env["io"].output)
            self.reject(env)
            self.assertEqual(bytes(env["io"].output), before)

    def test_completed_cache_replacement_and_missing_attribute_no_getter(self):
        env, reached = model(), []
        foreign = fixture.f.ModuleType("foreign")
        def hook(phase, code, namespace):
            if phase == "executed" and code.co_filename.endswith("/8.py"):
                env["cache"][NAMES[5]] = foreign
                reached.append(True)
        env["hooks"][0] = hook
        self.reject(env)
        self.assertEqual(reached, [True])
        self.assertIs(env["cache"][NAMES[5]], foreign)
        getters = []
        body = BODIES[8] + b"del _contract_valid\ndef __getattr__(name):\n _getters.append(name)\n return 7\n"
        env = model(bodies=BODIES[:8] + (body,), extras={"_getters": getters})
        self.reject(env)
        self.assertEqual(getters, [])
        self.assertEqual(len(self.events(env, "COMPILE")), 8)


if __name__ == "__main__":
    unittest.main()
