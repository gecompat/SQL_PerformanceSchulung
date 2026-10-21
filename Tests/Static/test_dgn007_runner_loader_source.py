"""Eigene Runnerbodies; finite Diagnosen unter vertrauenswürdigem Kontrollcode."""
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


def model(*, bodies=BODIES, ordinal=1, extras=None, before_seal=None):
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
        env["trusted_caller"] = env["ns"]["_rl_call"]
        if before_seal is not None:
            before_seal(env)
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

    def call(self, env): return env["trusted_caller"]()

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
        blocked = {"owner"}
        while tables:
            table = tables.pop(0)
            originals.update(table.get_identifiers())
            blocked.update(s.get_name() for s in table.get_symbols() if s.is_global() or table.get_type() == "class")
            tables += table.get_children()
        public = {"_worker_input_factory", "_worker_input_seal", "_worker_input_entry", "_worker_profile_state",
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
        for raw in (RAW, RAW.replace(b"\r\n", b"\n")):
            try:
                built = subject.build_runner_loader_control_bootstrap(raw, **OPTIONS)
            except subject.base.base.inputs.base.BootstrapSourceRejected as failure:
                # Nur aggregierte Größe aus diesem einen verworfenen Fitframe.
                if str(failure) == "SCRIPT_LIMIT":
                    tb = failure.__traceback__
                    while tb is not None:
                        if tb.tb_frame.f_code is subject.build_runner_loader_control_bootstrap.__code__:
                            data = tb.tb_frame.f_locals.get("source")
                            if type(data) is bytes:
                                print("REJECTED_RUNNER_SOURCE_BYTES=" + str(len(data)))
                                print("REJECTED_RUNNER_SOURCE_EXCESS=" + str(len(data) - 131072))
                        tb = tb.tb_next
                raise
            self.assertLessEqual(built.source_size, 131072)
            self.assertEqual(built.source_size, len(built.source))
            self.assertEqual(built.source_sha256, hashlib.sha256(built.source).hexdigest())
            self.assertFalse(built.runtime_attested or built.import_used_bytes_attested or built.trust_attested or built.method_approved)
            actual = ast.parse(built.source)
            self.assertEqual([a.name for n in actual.body if isinstance(n, ast.Import) for a in n.names],
                             ["importlib.util", "sys", "sysconfig", "json", "struct"])
            self.assertEqual(next(n.value.value for n in actual.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "_EXPECTED_PROFILE_RAW" for t in n.targets)), raw)
            self.assertFalse(any(isinstance(n, ast.FunctionDef) and n.name == "make_codefree_parent_registry" for n in actual.body))
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
                    for comparison in ast.walk(n):
                        if isinstance(comparison, ast.Compare) and ast.unparse(comparison) == "state[2] is False":
                            comparison.left = ast.Call(func=ast.Name(id="type", ctx=ast.Load()), args=[comparison.left], keywords=[])
                            comparison.comparators = [ast.Name(id="bool", ctx=ast.Load())]
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
                if n.name in ("_rl_write", "_rl_execute"):
                    n = next(f for f in ast.parse(subject._INLINE_SHARED_IO).body if isinstance(f, ast.FunctionDef) and f.name == n.name)
                helpers.append(n)
            template = ast.parse(previous.subject._INLINE_HARNESS.replace("_hl_", "_rl_").replace("_HL_", "_RL_").replace("HARNESS", "RUNNER"))
            added = ast.parse(subject._INLINE_RUNNER).body
            function_names = {n.name for n in added if isinstance(n, ast.FunctionDef)}
            constant_names = {t.id for n in added if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)} | {"_RL_COMMON"}
            kept = [n for n in template.body if not (isinstance(n, ast.FunctionDef) and n.name in function_names)
                and not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constant_names for t in n.targets))]
            for n in kept:
                if isinstance(n, ast.FunctionDef) and n.name == "_rl_main":
                    n.body = ast.parse("result = _rl_call()\nif result[:2] != ('EXECUTED_RUNNER_SOURCES', 'NONE'): raise SystemExit(1)").body
            report = next(n for n in expected.body if isinstance(n, ast.FunctionDef) and n.name == "_initialize_worker_report_control")
            matches = []
            class BeforeSnapshot(ast.NodeTransformer):
                def visit_Expr(self, node):
                    if ast.unparse(node) == "script.append(_worker_report_script())":
                        matches.append(node)
                        return [ast.parse("_rl_pre_snapshot()").body[0], node]
                    return self.generic_visit(node)
            BeforeSnapshot().visit(report)
            self.assertEqual(len(matches), 1)
            main = next(n for n in expected.body if isinstance(n, ast.If))
            main.body.insert(2, ast.parse("_initialize_rl_control()").body[0])
            main.body[-1] = ast.parse("_rl_main()").body[0]
            expected.body = [n for n in expected.body if n is not main] + helpers + kept + added + [main]
            class SharedCheckpoint(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Eigene Scope-Suche: verschachtelte Funktionen gehören nicht
                    # zum aktiven Frame dieser Funktion.
                    queue = list(node.body)
                    owns_checkpoint = False
                    while queue:
                        item = queue.pop()
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                            continue
                        if (isinstance(item, ast.Expr) and isinstance(item.value, ast.Call)
                                and isinstance(item.value.func, ast.Name)
                                and item.value.func.id == "_rl_checkpoint"):
                            owns_checkpoint = True
                        queue.extend(ast.iter_child_nodes(item))
                    self.generic_visit(node)
                    if owns_checkpoint:
                        prefix = [ast.Assign(targets=[ast.Name(id="_frame_kernel", ctx=ast.Store())],
                                             value=ast.Name(id="_kernel", ctx=ast.Load())),
                                  ast.Assign(targets=[ast.Name(id="_frame_primitives", ctx=ast.Store())],
                                             value=ast.Name(id="_primitives", ctx=ast.Load())),
                                  ast.Assign(targets=[ast.Name(id="_frame_record", ctx=ast.Store())],
                                             value=ast.Constant(value=None))]
                        node.body[0:0] = prefix
                    return node

                def visit_Expr(self, node):
                    if not (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                            and node.value.func.id == "_rl_checkpoint"):
                        return self.generic_visit(node)
                    selftest = node.value
                    if len(selftest.args) != 2: raise AssertionError("CHECKPOINT_FORM")
                    keywords = []
                    if selftest.keywords:
                        if (len(selftest.keywords) != 1 or selftest.keywords[0].arg != "diagnostic"
                                or not isinstance(selftest.keywords[0].value, ast.Constant)
                                or selftest.keywords[0].value.value is not True):
                            raise AssertionError("DIAGNOSTIC_FORM")
                        keywords = [ast.keyword(arg="diagnostic", value=ast.Constant(value=True))]
                    # Eigene Rekonstruktion des Callassignments; kein produktiver
                    # Binder und kein Kopieren seines resultierenden Baums.
                    arguments = [ast.parse(ast.unparse(arg), mode="eval").body for arg in selftest.args]
                    arguments.extend(ast.Name(id=name, ctx=ast.Load()) for name in
                                     ("_frame_kernel", "_frame_primitives", "_frame_record"))
                    return ast.Assign(targets=[ast.Name(id="_frame_record", ctx=ast.Store())],
                        value=ast.Call(func=ast.Name(id="_rl_checkpoint", ctx=ast.Load()),
                                       args=arguments, keywords=keywords))
            SharedCheckpoint().visit(expected)
            diagnostic = [n for n in ast.walk(expected) if isinstance(n, ast.Call)
                          and isinstance(n.func, ast.Name) and n.func.id == "_rl_checkpoint"
                          and n.keywords]
            self.assertEqual(len(diagnostic), 1)
            factory = next(n for n in expected.body if isinstance(n, ast.FunctionDef)
                           and n.name == "_rl_factory")
            entry = next(n for n in factory.body if isinstance(n, ast.FunctionDef) and n.name == "entry")
            final_check = next(n for n in entry.body if isinstance(n, ast.Try)
                               and isinstance(n.body[0], ast.Assign)
                               and n.body[0].value is diagnostic[0])
            self.assertEqual(len(final_check.body), 1)
            self.assertEqual(ast.unparse(final_check.handlers[0].body[0]),
                             "result, issue = (None, 'RUNNER_SOURCE_BINDING')")
            shared = ast.parse(subject._CHECKPOINT).body
            self.assertEqual(len(shared), 1)
            self.assertIsInstance(shared[0], ast.FunctionDef)
            self.assertEqual(shared[0].name, "_rl_checkpoint")
            expected.body.insert(len(expected.body) - 1, shared[0])
            definitions = [n for n in expected.body if isinstance(n, ast.FunctionDef)]
            observed = [n for n in actual.body if isinstance(n, ast.FunctionDef)]
            self.assertEqual(len(definitions), len(observed))
            original_nodes = tuple(ast.walk(expected))
            identifiers = {getattr(n, f, None) for n in original_nodes for f in ("id", "arg", "name", "asname", "rest", "attr")}
            identifiers.update(s for n in original_nodes if isinstance(n, (ast.Global, ast.Nonlocal)) for s in n.names)
            strings = [n.value for n in original_nodes if isinstance(n, ast.Constant) and type(n.value) is str]
            inverse = {}
            preserved = {"_worker_input_seal", "_worker_input_entry", "_worker_profile_state",
                         "_inline_observe_selected_worker_profile", "_inline_kernel_check", "_worker_input_factory"}
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

    def test_shared_partial_capture_root_path_and_actual_digest_handoff(self):
        env = model()
        o = owner(env)
        self.assertIs(o[0], env['ns'])
        self.assertIs(env['ns']['_RL_OWNER'], o)
        self.assertEqual(o[2][14], [])
        self.assertEqual(len(o[2][13]), 1)
        self.assertTrue(o[2][13][0])
        seen = set()
        gate_code = o[22][0][1]
        def observe(frame, event, arg):
            if event != 'call' or frame.f_code is not gate_code: return
            for v in o[2][5] + o[2][14]:
                index = v[1][0]
                kind = 'P' if index >= 9 else 'S'
                seen.add((kind, v[14]))
                if v[14] == 2:
                    self.assertIs(type(v[3]), o[9])
                    self.assertIsNone(v[4])
                    self.assertNotIn('__path__', v[3].__dict__)
                if v[14] == 4:
                    self.assertIs(type(v[4]), o[10][0])
                    self.assertIsNone(v[3].__spec__)
                    self.assertFalse(v[4]._set_fileattr)
                if v[18]: seen.add(('LINK', index))
                for slot in (0, 1): seen.add((kind, 'RECORD', slot, v[19][slot]))
                if kind == 'P' and v[9] is False:
                    self.assertTrue(o[2][5][0][13])
                    self.assertIsNone(o[2][5][0][7])
                    self.assertTrue(all(v[9] for v in o[2][5][1:5]))
                    self.assertTrue(o[2][9][10])
        original = sys.getprofile()
        env['io'].write_max = 64
        try:
            sys.setprofile(observe)
            result = self.call(env)
        finally:
            sys.setprofile(original)
        self.assertEqual(result[0], 'EXECUTED_RUNNER_SOURCES')
        for kind in ('S','P'):
            for stage in (1,2,3,4,5,6): self.assertIn((kind,stage), seen)
            for slot in (0,1):
                for phase in (1,2,3,4): self.assertIn((kind,'RECORD',slot,phase), seen)
        self.assertIn(('LINK',10),seen)
        expected = hashlib.sha256(fixture.fixture.pooled((env['payload'][2],), 'pooled-profile-binding-context/v1')).hexdigest()
        self.assertEqual(o[2][12], [expected])
        self.assertTrue(all(json.loads(row)[5] == expected for row in env['source_rows']))
        early = b'from Tests.Contracts.dgn007_capture_projection import decode_projection, ProjectionError\n'
        env = model(bodies=(early + BODIES[0],) + BODIES[1:])
        self.reject(env)
        self.assertEqual(len(self.events(env,'EXEC')),1)
        self.assertEqual(owner(env)[2][14], [])
        self.assertNotIn(b'"PARENT"', bytes(env['io'].output))

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

    def test_private_root_owner_and_primitive_pre_dispatch_drift(self):
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append('get'); raise AssertionError()
            def __len__(self): calls.append('len'); raise AssertionError()
            def __eq__(self, other): calls.append('eq'); raise AssertionError()
            def __hash__(self): calls.append('hash'); raise AssertionError()
            def __call__(self, *a, **kw): calls.append('call'); raise AssertionError()
        for kind in ('foreign-owner','copied-owner','guard-code','kernel-code','builtin','entry-cell'):
            env = model()
            o = owner(env)
            if kind == 'foreign-owner': env['ns']['_RL_OWNER'] = Foreign()
            elif kind == 'copied-owner':
                copied = tuple(list(o))
                self.assertIsNot(copied, o)
                self.assertIs(copied[13][0], o[13][0])
                env['ns']['_RL_OWNER'] = copied
            elif kind == 'guard-code': o[13][0].__code__ = o[13][0].__code__.replace()
            elif kind == 'kernel-code':
                f = o[2][3][0][0][12]
                f.__code__ = f.__code__.replace()
            elif kind == 'builtin': env['ns']['__builtins__']['len'] = Foreign()
            else:
                entry = env['ns']['_rl_entry']
                cell = dict(zip(env['trusted_caller'].__code__.co_freevars,env['trusted_caller'].__closure__))['entry']
                self.assertIs(cell.cell_contents, entry)
                cell.cell_contents = Foreign()
            result = self.reject(env)
            self.assertEqual(result[1], 'RUNNER_SOURCE_BINDING')
            self.assertEqual(env['io'].events, [])
            self.assertEqual(self.events(env,'COMPILE'), [])
        self.assertEqual(calls, [])

    def test_parent_phase_drift_has_dominant_post_and_no_source6(self):
        for kind in ('gate-code','gate-defaults','guard-code','gateway-cell','kernel-code'):
            env, reached = model(), []
            o = owner(env)
            def io_hook(io, phase):
                if phase != 'write' or not o[2][14] or reached: return
                self.assertEqual(o[2][14][0][19][0], 2)
                reached.append('PARENT_BEGIN_CALL')
                if kind == 'gate-code':
                    f = o[22][0][0]; f.__code__ = f.__code__.replace()
                elif kind == 'gate-defaults':
                    f = o[22][0][0]; f.__defaults__ = tuple(list(f.__defaults__))
                elif kind == 'guard-code':
                    f = o[13][0]; f.__code__ = f.__code__.replace()
                elif kind == 'gateway-cell':
                    f = o[2][7][0][0]
                    cell = dict(zip(f.__code__.co_freevars,f.__closure__))['invoke']
                    cell.cell_contents = lambda index: None
                else:
                    f = o[2][3][0][0][12]; f.__code__ = f.__code__.replace()
            env['io'].callback = io_hook
            self.assertEqual(self.reject(env)[1], 'RUNNER_SOURCE_BINDING')
            self.assertEqual(reached, ['PARENT_BEGIN_CALL'])
            self.assertEqual(len(self.events(env,'COMPILE')),5)
            self.assertNotIn(NAMES[6],env['cache'])
            self.assertTrue(all(name not in env['cache'] for name in NAMES + ('Tests','Tests.Contracts')))

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

        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append('get'); raise AssertionError()
            def __len__(self): calls.append('len'); raise AssertionError()
            def __eq__(self, other): calls.append('eq'); raise AssertionError()
            def __hash__(self): calls.append('hash'); raise AssertionError()
            def __call__(self, *a, **kw): calls.append('call'); raise AssertionError()
        for parent, stage in ((False,2),(False,4),(True,2),(True,4)):
            env, reached, held = model(), [], []
            o = owner(env)
            code = o[22][0][1]
            def observe(frame, event, arg):
                if event != 'call' or frame.f_code is not code or reached: return
                values = o[2][14] if parent else o[2][5]
                if values and values[-1][14] == stage:
                    v = values[-1]
                    self.assertIsNone(v[4]) if stage == 2 else self.assertIs(type(v[4]),o[10][0])
                    held.append(v[3 if stage == 2 else 4])
                    v[3 if stage == 2 else 4] = Foreign()
                    reached.append(('P' if parent else 'S',stage))
            previous_profile = sys.getprofile()
            try:
                sys.setprofile(observe)
                result = self.reject(env)
            finally:
                sys.setprofile(previous_profile)
            self.assertEqual(result[1],'RUNNER_SOURCE_BINDING')
            self.assertEqual(reached,[('P' if parent else 'S',stage)])
            self.assertEqual(len(held),1)
            self.assertEqual(len(self.events(env,'COMPILE')),5 if parent else 0)
            self.assertNotIn(NAMES[6],env['cache'])
        self.assertEqual(calls,[])

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

        for bad in ('zero','bool','overflow','error','limit'):
            env, reached = model(), []
            o = owner(env)
            def inject(io, phase):
                if phase != 'write' or not o[2][14] or reached: return
                self.assertEqual(o[2][14][0][19][0],2)
                reached.append('PARENT_BEGIN_CALL')
                if bad == 'error': io.error = 'write'
                elif bad == 'limit': o[2][3][0][0][2][3] = 1089
                else: io.write_value = lambda data: 0 if bad == 'zero' else True if bad == 'bool' else len(data)+1
            env['io'].callback = inject
            result = self.reject(env)
            self.assertEqual(result[1],'RUNNER_SOURCE_BINDING' if bad == 'limit' else 'RUNNER_SOURCE_REJECTED')
            self.assertEqual(reached,['PARENT_BEGIN_CALL'])
            self.assertEqual(o[2][14][0][16],0)
            self.assertNotEqual(o[2][14][0][19][0],4)
            self.assertEqual(len(self.events(env,'COMPILE')),5)
            self.assertTrue(all(name not in env['cache'] for name in NAMES+('Tests','Tests.Contracts')))

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
                    if kind == "entry":
                        self.assertEqual(self.call(env),
                            ("REJECTED_RUNNER_SOURCES", "RUNNER_SOURCE_BINDING", None))
                    else:
                        o = owner(env)
                        try: o[2][6][0][2](o[2][6][0][1][0], env["cache"][NAMES[0]])
                        except BaseException: pass
            env["hooks"][0] = hook
            self.reject(env)
            self.assertEqual(reached, [True])
            self.assertEqual(len(self.events(env, "COMPILE")), 1)
            self.assertEqual(self.events(env, "EXEC"), [])
            self.assertEqual(self.events(env, "EXEC_RETURN"), [])
            self.assertFalse(any(name in env["cache"] for name in NAMES + ("Tests", "Tests.Contracts")))
            before = (list(env["trace"]), list(env["io"].events), bytes(env["io"].output))
            self.reject(env)
            self.assertEqual((env["trace"], env["io"].events, bytes(env["io"].output)), before)

    def test_reentrant_partial_writer_stops_further_writes_and_sources(self):
        env, reached = model(), []
        def callback(io, phase):
            state = owner(env)[2]
            if phase == "write" and state[5] and state[5][-1][19][0] == 2:
                reached.append((len(io.events), len(io.output), state[5][-1]))
                io.write_max = 1
                self.assertEqual(self.call(env),
                    ("REJECTED_RUNNER_SOURCES", "RUNNER_SOURCE_BINDING", None))
        env["io"].callback = callback
        self.reject(env)
        self.assertEqual(len(reached), 1)
        event_count, written, record = reached[0]
        self.assertEqual(len(env["io"].events), event_count)
        self.assertEqual(len(env["io"].output), written + 1)
        self.assertEqual(record[16], 0)
        self.assertEqual(self.events(env, "COMPILE"), [])
        self.assertEqual(self.events(env, "EXEC"), [])
        self.assertFalse(any(name in env["cache"] for name in NAMES + ("Tests", "Tests.Contracts")))
        before = (list(env["trace"]), list(env["io"].events), bytes(env["io"].output))
        self.reject(env)
        self.assertEqual((env["trace"], env["io"].events, bytes(env["io"].output)), before)

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

        traps, reached = [], []
        class Key:
            def __hash__(self): traps.append('hash'); return 157
            def __eq__(self, other): traps.append('eq'); raise AssertionError()
        key = Key()
        env = model()
        def corrupt(phase, code, namespace):
            if phase == 'compiled' and code.co_filename.endswith('/0.py'):
                env['cache'][key] = object()
                traps.clear()
                reached.append(True)
        env['hooks'][0] = corrupt
        self.assertEqual(self.reject(env)[1],'RUNNER_SOURCE_BINDING')
        self.assertEqual(reached,[True])
        self.assertEqual(traps,[])
        self.assertTrue(any(k is key for k in env['cache']))
        # Corrupted cache prevents a complete own-cleanup claim.
        self.assertIn(NAMES[0],env['cache'])


    def test_guard_slot_record_and_input_handoff_replacement_precede_foreign_dispatch(self):
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append("get"); raise AssertionError()
            def __getitem__(self, key): calls.append("item"); raise AssertionError()
            def __iter__(self): calls.append("iter"); raise AssertionError()
            def __len__(self): calls.append("len"); raise AssertionError()
            def __eq__(self, other): calls.append("eq"); raise AssertionError()
            def __hash__(self): calls.append("hash"); raise AssertionError()
            def __call__(self, *a, **kw): calls.append("call"); raise AssertionError()
        for phase in ("BEFORE_CALL", "PARENT_BEGIN"):
            for kind in ("foreign-slot", "foreign-record", "copied-record", "carrier-and-slot", "input-record"):
                env, reached = model(), []
                o = owner(env)
                original = o[22][0]
                def mutate():
                    reached.append((phase, kind))
                    if kind == "foreign-slot":
                        o[22][:] = [Foreign()]
                    elif kind == "foreign-record":
                        o[22][0] = (Foreign(),) * 5
                    elif kind == "copied-record":
                        replacement = tuple(list(original))
                        self.assertIsNot(replacement, original)
                        self.assertIs(replacement[0], original[0])
                        o[22][0] = replacement
                    elif kind == "carrier-and-slot":
                        carrier = env["ns"]["_RL_D1_CARRIER"]
                        cell, = carrier.__closure__
                        replacement = tuple(list(original))
                        cell.cell_contents = replacement
                        o[22][0] = replacement
                    else:
                        o[2][3][0] = (o[2][3][0][0], Foreign(), original[1])
                if phase == "BEFORE_CALL":
                    mutate()
                else:
                    def callback(io, operation):
                        if operation == "write" and o[2][14] and not reached:
                            self.assertEqual(o[2][14][0][19][0], 2)
                            mutate()
                    env["io"].callback = callback
                result = self.reject(env)
                self.assertEqual(result[1], "RUNNER_SOURCE_BINDING")
                self.assertEqual(reached, [(phase, kind)])
                self.assertEqual(len(self.events(env, "COMPILE")), 0 if phase == "BEFORE_CALL" else 5)
                self.assertTrue(all(name not in env["cache"] for name in NAMES + ("Tests", "Tests.Contracts")))
        self.assertEqual(calls, [])

    def test_seal_closes_original_d0_and_reseal_is_sticky(self):
        for kind in ("slot", "sealer-code", "gate-defaults", "entry-cell"):
            reached = []
            def before_seal(env):
                o = owner(env)
                reached.append(kind)
                if kind == "slot":
                    o[22][0] = tuple(list(o[22][0]))
                elif kind == "sealer-code":
                    f = env["ns"]["_RL_SEALER"]
                    f.__code__ = f.__code__.replace()
                elif kind == "gate-defaults":
                    f = o[22][0][0]
                    f.__defaults__ = tuple(list(f.__defaults__))
                else:
                    f = env["ns"]["_rl_entry"]
                    cell = dict(zip(f.__code__.co_freevars, f.__closure__))["o"]
                    cell.cell_contents = tuple(list(o))
            env = model(before_seal=before_seal)
            self.assertEqual(reached, [kind])
            self.assertNotEqual(env["report_initial"][0], "BOUND_WORKER_REPORT_CONTROL")
            self.assertEqual(self.reject(env)[1], "RUNNER_SOURCE_BINDING")
            self.assertEqual(env["io"].events, [])
        env = model()
        self.assertEqual(env["report_initial"][0], "BOUND_WORKER_REPORT_CONTROL")
        with self.assertRaises(RuntimeError):
            env["ns"]["_rl_pre_snapshot"]()
        self.assertIs(owner(env)[2][2], True)
        self.assertEqual(self.reject(env)[1], "RUNNER_SOURCE_BINDING")
        self.assertEqual(env["io"].events, [])

    def test_active_entry_retains_cleanup_anchors_after_closure_exchange(self):
        calls = []
        class Foreign:
            def __getattribute__(self, key): calls.append("get"); raise AssertionError()
            def __getitem__(self, key): calls.append("item"); raise AssertionError()
            def __setitem__(self, key, value): calls.append("set"); raise AssertionError()
            def __iter__(self): calls.append("iter"); raise AssertionError()
            def __len__(self): calls.append("len"); raise AssertionError()
            def __eq__(self, other): calls.append("eq"); raise AssertionError()
            def __hash__(self): calls.append("hash"); raise AssertionError()
            def __call__(self, *a, **kw): calls.append("call"); raise AssertionError()
        for name in ("o", "st", "_kernel"):
            env, reached = model(), []
            o = owner(env)
            state = o[2]
            cache = o[11]
            foreign = object()
            def callback(io, operation):
                if operation == "write" and state[14] and not reached:
                    self.assertEqual(state[14][0][19][0], 2)
                    reached.append(name)
                    cache["foreign_preserved"] = foreign
                    if name == "o":
                        # The old cleanup reread this swapped owner's cache.
                        replacement = list(o)
                        replacement[11] = Foreign()
                        value = tuple(replacement)
                    else:
                        value = Foreign()
                    f = env["ns"]["_rl_entry"]
                    cell = dict(zip(f.__code__.co_freevars, f.__closure__))[name]
                    cell.cell_contents = value
                    raise RuntimeError("SYNTHETIC_CALLBACK_FAILURE")
            env["io"].callback = callback
            self.assertEqual(self.reject(env)[1], "RUNNER_SOURCE_BINDING")
            self.assertEqual(reached, [name])
            self.assertEqual(len(self.events(env, "COMPILE")), 5)
            self.assertIs(state[2], True)
            self.assertIs(cache["foreign_preserved"], foreign)
            self.assertTrue(all(key not in cache for key in NAMES + ("Tests", "Tests.Contracts")))
        self.assertEqual(calls, [])


    def test_c7_context_field_zero_regression_is_finite_diagnosis(self):
        # DEC-076: gezielte Diagnose, keine Absicherung gemeinsam gefälschter
        # Kontrollanker und kein Sandbox- oder Hostattestationsnachweis.
        calls, reached = [], []
        class Foreign:
            def __getattribute__(self, key): calls.append("get"); raise AssertionError()
            def __getitem__(self, key): calls.append("item"); raise AssertionError()
            def __iter__(self): calls.append("iter"); raise AssertionError()
            def __len__(self): calls.append("len"); raise AssertionError()
            def __eq__(self, other): calls.append("eq"); raise AssertionError()
            def __hash__(self): calls.append("hash"); raise AssertionError()
            def __call__(self, *a, **kw): calls.append("call"); raise AssertionError()
        for kind in ("context", "field-zero"):
            env = model()
            f = env["trusted_caller"]
            cell = dict(zip(f.__code__.co_freevars, f.__closure__))["_kernel"]
            original = cell.cell_contents
            if kind == "context":
                cell.cell_contents = Foreign()
            else:
                copied = list(original)
                copied[0] = Foreign()
                cell.cell_contents = tuple(copied)
                self.assertEqual(len(cell.cell_contents), 17)
            reached.append((kind, "BEFORE_CALL"))
            self.assertEqual(self.reject(env)[1], "RUNNER_SOURCE_BINDING")
            self.assertEqual(env["io"].events, [])
            self.assertEqual(self.events(env, "COMPILE"), [])
        self.assertEqual(reached, [("context", "BEFORE_CALL"), ("field-zero", "BEFORE_CALL")])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
