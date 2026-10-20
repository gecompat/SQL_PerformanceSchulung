"""Empfang, tatsächliche Aufnahme und vollständiger Report in eigenen Modellen."""
import ast
import hashlib
import json
import struct
import sys
from types import FunctionType
import unittest

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_worker_profile_source as fixture

g, f = fixture.generator, fixture.f
ROLES = ("run_dgn007_automated_setup", "docker_sqlcmd_proxy", "run_demo")
MEMBERS = (
    ("run_dgn007_automated_setup", "Tests/Runtime/run_dgn007_automated_setup.py"),
    ("execution_target", "Tests/Runtime/execution_target.py"),
    ("docker_sqlcmd_proxy", "Tests/Runtime/docker_sqlcmd_proxy.py"),
    ("run_demo", "Demos/00_Framework/Tools/run_demo.py"),
    ("orchestrate_sessions", "Demos/00_Framework/Tools/orchestrate_sessions.py"),
    ("sqlcmd_process", "Demos/00_Framework/Tools/sqlcmd_process.py"),
    ("Tests.Contracts.dgn007_capture_projection", "Tests/Contracts/dgn007_capture_projection.py"),
    ("Tests.Contracts.dgn007_collector_transport", "Tests/Contracts/dgn007_collector_transport.py"),
    ("Tests.Contracts.dgn007_prospective_acceptance", "Tests/Contracts/dgn007_prospective_acceptance.py"))


def line(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def pooled(payload, role):
    texts = set()
    def collect(value):
        if type(value) is str:
            texts.add(value)
        elif type(value) is tuple:
            for child in value:
                collect(child)
    collect(payload)
    pool = tuple(sorted(texts))
    def project(value):
        if type(value) is str:
            return pool.index(value)
        if type(value) is tuple:
            return tuple(project(child) for child in value)
        return value
    return line(("pooled-binding-design/v1", role, pool, project(payload)))


def selected(worker):
    rows = tuple(dict(ordinal=n, module=module, member=member, size=n,
                      sha256=hashlib.sha256(bytes(n)).hexdigest())
                 for n, (module, member) in enumerate(MEMBERS))
    original = dict(protocol="dgn007-import-input/v1", commit="1" * 40,
                    raw27_binding="2" * 64, source_profile="dgn007-docker-sql-only/v1",
                    nonce="3" * 64, modules=list(rows))
    descriptors = tuple(tuple(row[key] for key in ("ordinal", "module", "member", "size", "sha256"))
                        for row in rows)
    ip = tuple(original[key] for key in ("protocol", "commit", "raw27_binding", "source_profile", "nonce"))
    ip += (descriptors, hashlib.sha256(line(original)).hexdigest())
    context = ip[1:5] + (descriptors,) + worker[:3]
    return ip, worker, context


def chunks(payload):
    data = pooled(payload, "METADATA")
    raw = struct.pack(">8sII", b"DGNC001\0", len(data), sum(row[3] for row in payload[0][5])) + data
    return tuple(raw[n:n + 1024] for n in range(0, len(raw), 1024))


def model(*, ordinal=1, initialize=True, encoder_callback=None,
          builder=g.build_inline_worker_report_control_bootstrap, setup=None):
    env = fixture.model(initialize=False, builder=builder)
    own = {}
    for name, kind, actual in (("hashlib", "SOURCE", hashlib),
                               ("_hashlib", "EXTENSION", hashlib._hashlib),
                               ("json", "SOURCE", json), ("json.encoder", "SOURCE", json.encoder)):
        module, row = f.own_module(name, kind)
        metadata = module.__dict__.copy()
        module.__dict__.update(vars(actual))
        module.__dict__.update(metadata)
        module.__dict__["__package__"] = ""
        module.__dict__["__cached__"] = None
        module.__spec__._set_fileattr = True
        module.__spec__._cached = None
        env["cache"][name] = module
        own[name] = module
        env["worker"] = f.replace_at(env["worker"], 5, env["worker"][5] + (row,))
    encoder = own["json.encoder"]
    def clone(function):
        result = FunctionType(function.__code__, encoder.__dict__, function.__name__,
                              function.__defaults__, function.__closure__)
        result.__kwdefaults__ = None if function.__kwdefaults__ is None else function.__kwdefaults__.copy()
        return result
    members = {key: clone(value) if type(value) is FunctionType else value
               for key, value in vars(json.JSONEncoder).items() if key not in ("__dict__", "__weakref__")}
    encoder.JSONEncoder = type("JSONEncoder", (object,), members)
    encoder._make_iterencode = clone(json.encoder._make_iterencode)
    encoder._observed_callback = encoder_callback
    if encoder_callback is not None:
        encoder._original_iterencode = encoder.JSONEncoder.iterencode
        exec("""def observed_iterencode(self, value, _one_shot=False):
    for piece in _original_iterencode(self, value, _one_shot):
        if _observed_callback is not None:
            _observed_callback(value)
        yield piece
""", encoder.__dict__)
        encoder.JSONEncoder.iterencode = encoder.observed_iterencode
    own["json"].JSONEncoder = encoder.JSONEncoder
    own["hashlib"]._hashlib = own["_hashlib"]
    env["control"].hashlib = own["hashlib"]
    env["ns"]["json"] = own["json"]
    env["worker"] = (ordinal, ROLES[ordinal - 1], "PRE_IMPORT") + env["worker"][3:5] + (
        tuple(sorted(env["worker"][5])),)
    env.update(own=own, payload=selected(env["worker"]))
    env["chunks"] = chunks(env["payload"])
    if setup is not None:
        setup(env)
    env["initial"] = env["ns"]["_initialize_worker_profile_control"]()
    env["report_initial"] = env["ns"]["_initialize_worker_report_control"]() if initialize else None
    return env


class ObservedWorkerReportTests(unittest.TestCase):
    def setUp(self):
        self.real = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.real))
        self.assertTrue(all(sys.modules[name] is value for name, value in self.real.items()))

    def ready(self, env):
        self.assertEqual(env["initial"], ("BOUND_WORKER_PROFILE_CONTROL", "NONE"))
        self.assertEqual(env["report_initial"], ("BOUND_WORKER_REPORT_CONTROL", "NONE"))

    def call(self, env, received=None, **changes):
        kwargs = dict(token=b"t" * 32, separately_known_filefinder_hook=env["hook"])
        kwargs.update(changes)
        return env["ns"]["_inline_observed_worker_report"](
            env["chunks"] if received is None else received, **kwargs)

    def rejected(self, env, received=None, **changes):
        result = self.call(env, received, **changes)
        self.assertEqual(result[0], "REJECTED_OBSERVED_WORKER_REPORT")
        self.assertIn(result[1], ("WORKER_REPORT_REJECTED", "WORKER_REPORT_BINDING",
                                 "WORKER_REPORT_ALREADY_ATTEMPTED"))
        self.assertIsNone(result[2])
        self.assertIsNone(env["ns"]["_WORKER_REPORT_BINDING"])
        self.assertNotIn("/synthetic", repr(result))
        return result

    def test_actual_full_source_fit_raw_literal_and_five_imports(self):
        source = g.build_inline_worker_report_control_bootstrap(fixture.RAW, **fixture.OPTIONS)
        self.assertEqual(source.source_size, len(source.source))
        self.assertLessEqual(source.source_size, 131072)
        self.assertEqual(source.source_sha256, hashlib.sha256(source.source).hexdigest())
        self.assertEqual(source.profile_raw, fixture.RAW)
        tree = ast.parse(source.source)
        imports = [alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        raw = next(node.value.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "_EXPECTED_PROFILE_RAW"
                           for target in node.targets))
        self.assertEqual(raw, fixture.RAW)
        main = next(node for node in tree.body if isinstance(node, ast.If))
        calls = [node.value.func.id for node in main.body]
        self.assertEqual(calls, ["_load_bound_control", "_initialize_worker_profile_control",
                                 "_initialize_worker_report_control"])
        base = ast.parse(g.build_inline_worker_profile_control_bootstrap(fixture.RAW, **fixture.OPTIONS).source)
        original_main = next(node for node in base.body if isinstance(node, ast.If))
        original_main.body.append(ast.Expr(value=ast.Call(
            func=ast.Name(id="_initialize_worker_report_control", ctx=ast.Load()), args=[], keywords=[])))
        retained = [node for node in base.body if node is not original_main
                    and not (isinstance(node, ast.FunctionDef) and node.name == "_inline_match_metadata_chunks")]
        expected = ast.Module(body=retained + ast.parse(g._INLINE_WORKER_REPORT).body + [original_main],
                              type_ignores=[])
        self.assertEqual(ast.dump(tree, include_attributes=False), ast.dump(expected, include_attributes=False))
        names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("_inline_match_metadata_chunks", names)
        self.assertTrue({"_match_intake", "_match_original", "_match_intrinsic",
                         "_inline_receive_declared_bodies", "_inline_command_match"} <= names)
        self.assertFalse(source.runtime_attested or source.trust_attested
                         or source.import_used_bytes_attested or source.method_approved)

    def test_complete_actual_report_for_all_three_roles_against_independent_oracle(self):
        for ordinal in (1, 2, 3):
            env = model(ordinal=ordinal)
            self.ready(env)
            paths = []
            env["filesystem"].path.realpath = lambda path: paths.append(path) or path
            result = self.call(env)
            self.assertEqual(result[:2], ("OBSERVED_WORKER_REPORT", "NONE"))
            header, metadata, actual, observation, records = result[2]
            self.assertEqual(header + metadata, b"".join(env["chunks"]))
            self.assertEqual(actual, env["payload"])
            self.assertEqual(observation.profile.token, b"t" * 32)
            self.assertTrue(all(row.module is env["cache"][row.name] for row in observation.profile.modules))
            self.assertGreaterEqual(len(paths), 3)
            begin, end = json.loads(records[0]), json.loads(records[-1])
            data = b"".join(row[:-1].split(b"|", 4)[4] for row in records[1:-1])
            expected = (env["payload"][2],) + env["worker"][3:]
            self.assertEqual(data, pooled(expected, "REPORTED"))
            self.assertEqual(begin, ["PROFILE_BEGIN", ordinal, len(data), len(records) - 2])
            self.assertEqual(end, ["PROFILE_END", ordinal, len(data), len(records) - 2,
                                   hashlib.sha256(data).hexdigest()])
            self.assertFalse(observation.report.runtime_attested or observation.report.trust_attested)

    def test_foreign_chunks_and_limits_have_no_foreign_callbacks_or_profile_reads(self):
        called = []
        class Foreign:
            def __len__(self): called.append("LEN"); raise AssertionError()
            def __iter__(self): called.append("ITER"); raise AssertionError()
            def __eq__(self, other): called.append("EQ"); raise AssertionError()
        for received in (Foreign(), (Foreign(),), (b"x" * 1025,), (b"",) * 257,
                         (b"x" * 1024,) * 17):
            env = model()
            self.ready(env)
            reads = []
            env["filesystem"].path.realpath = lambda path: reads.append(path) or path
            self.rejected(env, received)
            self.assertEqual(reads, [])
        self.assertEqual(called, [])

    def test_late_metadata_form_errors_never_reach_profile(self):
        for field, value in ((3, None), (4, ("__main__",)), (5, ()), (2, "POST_IMPORT")):
            env = model()
            worker = f.replace_at(env["worker"], field, value)
            payload = f.replace_at(env["payload"], 1, worker)
            reads = []
            env["filesystem"].path.realpath = lambda path: reads.append(path) or path
            self.rejected(env, chunks(payload))
            self.assertEqual(reads, [])

    def test_full_original_digest_header_and_body_declarations_are_required(self):
        for kind in ("digest", "header", "suffix", "descriptors"):
            env = model()
            payload = env["payload"]
            if kind == "digest":
                payload = f.replace_at(payload, 0, f.replace_at(payload[0], 6, "0" * 64))
            elif kind == "descriptors":
                payload = f.replace_at(payload, 2, f.replace_at(payload[2], 4, payload[2][4][:-1]))
            received = b"".join(chunks(payload))
            if kind == "header": received = received[:12] + struct.pack(">I", 0) + received[16:]
            if kind == "suffix": received += b"extra-body"
            self.rejected(env, tuple(received[n:n + 1024] for n in range(0, len(received), 1024)))

    def test_actual_profile_mismatch_never_produces_records(self):
        for kind in ("version", "cache", "hook", "token"):
            env = model()
            changes = {}
            if kind == "version": env["runtime"].version_info = (3, 12, 99)
            elif kind == "cache": env["cache"]["EXTRA"] = object()
            elif kind == "hook": changes["separately_known_filefinder_hook"] = lambda path: None
            else: changes["token"] = b"short"
            self.rejected(env, **changes)

    def test_helper_replacement_before_entry_is_never_dispatched(self):
        called = []
        def foreign(*args, **kwargs): called.append(1); return None
        for name in ("_inline_receive_metadata_chunks", "_inline_profile_report",
                     "_inline_observe_selected_worker_profile", "_worker_profile_state",
                     "_report_encoder_check", "_worker_report_check", "_worker_report_script_check",
                     "_worker_report_run", "_worker_report_entry_factory"):
            env = model()
            env["ns"][name] = foreign
            self.rejected(env)
        class ForeignCheck:
            @property
            def __code__(self):
                called.append("CODE")
                raise AssertionError()
            def __call__(self, *args):
                called.append("CALL")
                raise AssertionError()
        for foreign_check in (False, True):
            env = model()
            self.ready(env)
            original = env["ns"]["_WORKER_REPORT_BINDING"]
            replacement = list(original)
            if foreign_check:
                replacement[4] = (ForeignCheck(), original[4][1])
            env["ns"]["_WORKER_REPORT_BINDING"] = tuple(replacement)
            reads = []
            env["filesystem"].path.realpath = lambda path: reads.append(path) or path
            self.assertIsNot(env["ns"]["_WORKER_REPORT_BINDING"], original)
            self.rejected(env)
            self.assertEqual(reads, [])
        self.assertEqual(called, [])

    def test_code_defaults_keyword_contents_and_class_drift(self):
        for kind in ("code", "defaults", "keywords", "class"):
            env = model(initialize=False)
            function = env["ns"]["_report_shape"]
            if kind == "keywords": function.__kwdefaults__ = {"synthetic": None}
            self.assertEqual(env["ns"]["_initialize_worker_report_control"](),
                             ("BOUND_WORKER_REPORT_CONTROL", "NONE"))
            if kind == "code": function.__code__ = function.__code__.replace()
            elif kind == "defaults": function.__defaults__ = (None,)
            elif kind == "keywords": function.__kwdefaults__["synthetic"] = object()
            else: env["ns"]["_InlineParser"].extra = object()
            self.rejected(env)

    def test_receiver_callback_drift_is_closed_before_report_dispatch(self):
        for kind in ("helper", "provider", "encoder"):
            reached, dispatched, box = [], [], {}
            def callback(value):
                if reached: return
                reached.append(1)
                env = box["env"]
                if kind == "helper":
                    env["ns"]["_inline_profile_report"] = lambda *args: dispatched.append(1)
                elif kind == "provider": env["own"]["hashlib"].sha256 = lambda: None
                else: env["own"]["json.encoder"].JSONEncoder.extra = None
            env = model(encoder_callback=callback)
            box["env"] = env
            self.ready(env)
            self.rejected(env)
            self.assertEqual(reached, [1])
            self.assertEqual(dispatched, [])

    def test_late_report_callback_and_exception_cannot_hide_control_loss(self):
        for fail in (False, True):
            reached, box = [], {}
            def callback(value):
                if reached or type(value) is not tuple or value[:2] != ("pooled-binding-design/v1", "REPORTED"):
                    return
                reached.append(1)
                box["env"]["control"].FROZEN_NAMES["added"] = ("a", "b")
                if fail: raise RuntimeError("PRIVATE /synthetic/value")
            env = model(encoder_callback=callback)
            box["env"] = env
            result = self.rejected(env)
            self.assertEqual(result[1], "WORKER_REPORT_BINDING")
            self.assertEqual(reached, [1])

    def test_reentrancy_consumes_outer_attempt_and_never_heals(self):
        nested, box = [], {}
        def callback(value):
            if not nested:
                nested.append(self.call(box["env"]))
        env = model(encoder_callback=callback)
        box["env"] = env
        self.rejected(env)
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0], ("REJECTED_OBSERVED_WORKER_REPORT", "WORKER_REPORT_ALREADY_ATTEMPTED", None))
        self.rejected(env)

    def test_retry_after_success_or_failure_and_reinitialization_are_rejected(self):
        for valid in (False, True):
            env = model()
            if valid: self.assertEqual(self.call(env)[0], "OBSERVED_WORKER_REPORT")
            else: self.rejected(env, ())
            result = self.rejected(env)
            self.assertEqual(result[1], "WORKER_REPORT_ALREADY_ATTEMPTED")
            self.assertEqual(env["ns"]["_initialize_worker_report_control"](),
                             ("REJECTED_WORKER_REPORT_CONTROL", "WORKER_REPORT_ALREADY_INITIALIZED"))

    def test_held_check_code_drift_does_not_invoke_replacement(self):
        reached, called, box = [], [], {}
        def callback(value):
            if reached: return
            reached.append(1)
            env = box["env"]
            exec("def changed(*args):\n    _foreign_calls.append(1)\n", env["ns"])
            env["ns"]["_foreign_calls"] = called
            env["ns"]["_worker_report_check"].__code__ = env["ns"]["changed"].__code__
        env = model(encoder_callback=callback)
        box["env"] = env
        self.rejected(env)
        self.assertEqual(reached, [1])
        self.assertEqual(called, [])

    def test_excluded_attempt_cell_cannot_be_reset_by_provider(self):
        reached, box = [], {}
        def callback(value):
            if reached: return
            reached.append(1)
            box["env"]["ns"]["_WORKER_REPORT_USED"] = False
        env = model(encoder_callback=callback)
        box["env"] = env
        self.rejected(env)
        self.assertEqual(reached, [1])
        self.rejected(env)

    def test_shared_state_budget_and_namespace_limit_reject_before_copy(self):
        for kind in ("namespace", "states"):
            env = model(initialize=False)
            if kind == "namespace":
                env["ns"].update(("own_%d" % n, None) for n in range(257))
            else:
                code = (lambda: None).__code__
                methods = {"own_%d" % n: FunctionType(code, env["ns"], argdefs=(None,) * 200)
                           for n in range(200)}
                methods["__module__"] = "__main__"
                env["ns"]["OwnBudgetClass"] = type("OwnBudgetClass", (), methods)
            self.assertEqual(env["ns"]["_initialize_worker_report_control"](),
                             ("REJECTED_WORKER_REPORT_CONTROL", "WORKER_REPORT_BINDING"))
            self.rejected(env)

    def test_source_cap_and_fixed_locator_forms_stay_closed(self):
        for raw, options in ((b"x" * 131073, fixture.OPTIONS),
                             (fixture.RAW, dict(fixture.OPTIONS, logical_profile="relative.py")),
                             (fixture.RAW, dict(fixture.OPTIONS, expected_soabi=None))):
            with self.assertRaises(g.BootstrapSourceRejected):
                g.build_inline_worker_report_control_bootstrap(raw, **options)


if __name__ == "__main__":
    unittest.main()
