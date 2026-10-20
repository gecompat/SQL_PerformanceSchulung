"""Vollständige Eingangsfolge mit eigenen Queues; keine nativen OS-I/O."""
import ast
import builtins
import hashlib
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_dgn007_observed_worker_report as fixture
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import dgn007_worker_input_source as subject

f = fixture.f
RAW, OPTIONS = fixture.fixture.RAW, fixture.fixture.OPTIONS
KINDS = ("BODY_RELEASE", "BODY_END", "IMPORT_RELEASE")
DEFAULT_BODIES = (b"\xff\0\r\n", b"", b"x\r\n") + tuple(b"raw-" + bytes((n,)) for n in range(6))


class IO:
    def __init__(self):
        self.input, self.output, self.events = b"", bytearray(), []
        self.offset, self.read_max, self.write_max = 0, 4096, 1024
        self.callback = self.read_value = self.write_value = None
        self.error = None

    def read(self, fd, size):
        if fd != 0 or not 1 <= size <= 4096: raise AssertionError("READ_ENDPOINT")
        self.events.append(("read", size, self.offset, len(self.output)))
        if self.callback is not None: self.callback(self, "read")
        if self.error == "read": raise OSError("PRIVATE /synthetic/value")
        if self.read_value is not None: return self.read_value(size)
        data = self.input[self.offset:self.offset + min(size, self.read_max)]
        self.offset += len(data)
        return data

    def write(self, fd, data):
        if fd != 1 or type(data) is not bytes or not 0 < len(data) <= 1024:
            raise AssertionError("WRITE_ENDPOINT")
        self.events.append(("write", len(data), self.offset, len(self.output)))
        if self.callback is not None: self.callback(self, "write")
        if self.error == "write": raise OSError("PRIVATE /synthetic/value")
        if self.write_value is not None: return self.write_value(data)
        count = min(len(data), self.write_max)
        self.output.extend(data[:count])
        return count


def full_payload(worker, bodies):
    original = fixture.selected(worker)
    rows = tuple(row[:3] + (len(body), hashlib.sha256(body).hexdigest())
                 for row, body in zip(original[0][5], bodies))
    ip = list(original[0])
    ip[5] = rows
    named = dict(zip(("protocol", "commit", "raw27_binding", "source_profile", "nonce"), ip[:5]))
    named["modules"] = [dict(zip(("ordinal", "module", "member", "size", "sha256"), row)) for row in rows]
    ip[6] = hashlib.sha256(fixture.line(named)).hexdigest()
    return tuple(ip), worker, tuple(ip[1:5]) + (rows,) + worker[:3]


def wire(payload, bodies):
    metadata = b"".join(fixture.chunks(payload))
    context = payload[2]
    digest = hashlib.sha256(fixture.pooled((context,), "pooled-profile-binding-context/v1")).hexdigest()
    commands = tuple(fixture.line((kind, context[5], context[3], digest)) + b"\n" for kind in KINDS)
    complete = fixture.line(("INPUT_COMPLETE", context[5], context[3], digest)) + b"\n"
    return metadata, commands, complete


def model(*, ordinal=1, bodies=DEFAULT_BODIES, seal=True):
    io = IO()
    def setup(env):
        filesystem, row = f.own_module("os", "SOURCE")
        filesystem.__dict__.update(path=env["filesystem"].path, __builtins__=dict(vars(builtins)),
                                   _driver_read=io.read, _driver_write=io.write)
        exec("def read(fd, size):\n    return _driver_read(fd, size)\n"
             "def write(fd, data):\n    return _driver_write(fd, data)\n", filesystem.__dict__)
        env["filesystem"] = env["control"].os = filesystem
        env["cache"]["os"] = filesystem
        worker = f.replace_at(env["worker"], 5, tuple(sorted(env["worker"][5] + (row,))))
        env["worker"], env["payload"] = worker, full_payload(worker, bodies)
        env["chunks"] = fixture.chunks(env["payload"])
    env = fixture.model(ordinal=ordinal, initialize=False,
                        builder=subject.build_worker_input_control_bootstrap, setup=setup)
    env["io_initial"] = env["ns"]["_initialize_worker_input_control"]()
    env["report_initial"] = env["ns"]["_initialize_worker_report_control"]()
    env["sealed"] = env["ns"]["_worker_input_seal"]() if seal else None
    metadata, commands, complete = wire(env["payload"], bodies)
    io.input = metadata + commands[0] + b"".join(bodies) + commands[1] + commands[2]
    env.update(io=io, bodies=bodies, metadata=metadata, commands=commands, complete=complete)
    return env


def owner(env):
    entry = env["ns"]["_worker_input_entry"]
    return dict(zip(entry.__code__.co_freevars,
                    (cell.cell_contents for cell in entry.__closure__)))["owner"]


class WorkerInputSourceTests(unittest.TestCase):
    def setUp(self):
        self.real = sys.modules.copy()

    def tearDown(self):
        self.assertEqual(tuple(sys.modules), tuple(self.real))
        self.assertTrue(all(sys.modules[name] is value for name, value in self.real.items()))

    def ready(self, env):
        self.assertEqual(env["initial"], ("BOUND_WORKER_PROFILE_CONTROL", "NONE"))
        self.assertEqual(env["io_initial"], ("BOUND_WORKER_INPUT_CONTROL", "NONE", None))
        self.assertEqual(env["report_initial"], ("BOUND_WORKER_REPORT_CONTROL", "NONE"))
        self.assertEqual(env["sealed"], ("SEALED_WORKER_INPUT_CONTROL", "NONE", None))

    def call(self, env):
        return env["ns"]["_worker_input_entry"]()

    def rejected(self, env):
        result = self.call(env)
        self.assertEqual(result[0], "REJECTED_WORKER_INPUT")
        self.assertIn(result[1], ("WORKER_INPUT_BINDING", "WORKER_INPUT_REJECTED"))
        self.assertIsNone(result[2])
        self.assertNotIn("/synthetic", repr(result))
        self.assertLessEqual(len(env["io"].events), 1088)
        return result

    def test_actual_full_source_fit_raw_five_imports_and_independent_whole_ast(self):
        result = subject.build_worker_input_control_bootstrap(RAW, **OPTIONS)
        self.assertLessEqual(result.source_size, 131072)
        self.assertEqual(result.source_size, len(result.source))
        self.assertEqual(result.source_sha256, hashlib.sha256(result.source).hexdigest())
        self.assertEqual(result.profile_raw, RAW)
        actual = ast.parse(result.source)
        imports = [alias.name for node in actual.body if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(imports, ["importlib.util", "sys", "sysconfig", "json", "struct"])
        expected = ast.parse(subject.base.build_inline_worker_report_control_bootstrap(RAW, **OPTIONS).source)
        initialize = next(node for node in expected.body if isinstance(node, ast.FunctionDef)
                          and node.name == "_initialize_worker_report_control")
        block = next(node for node in initialize.body if isinstance(node, ast.Try)).body
        index = next(n for n, node in enumerate(block) if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "_WORKER_REPORT_BINDING"
                             for target in node.targets))
        block.insert(index + 1, ast.parse("_worker_input_report_handoff(held, marker, entry)").body[0])
        main = next(node for node in expected.body if isinstance(node, ast.If))
        main.body.insert(2, ast.parse("_initialize_worker_input_control()").body[0])
        main.body.extend(ast.parse("_worker_input_seal()\n_worker_input_main()").body)
        expected.body = [node for node in expected.body if node is not main]
        expected.body += ast.parse(subject._INLINE_WORKER_INPUT).body + [main]
        self.assertEqual(ast.dump(actual, include_attributes=False), ast.dump(expected, include_attributes=False))
        literal = next(node.value.value for node in actual.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "_EXPECTED_PROFILE_RAW"
                               for target in node.targets))
        self.assertEqual(literal, RAW)
        self.assertFalse(result.runtime_attested or result.trust_attested
                         or result.import_used_bytes_attested or result.method_approved)

    def test_full_three_roles_actual_bodies_report_complete_and_exact_eof(self):
        for ordinal in (1, 2, 3):
            env = model(ordinal=ordinal)
            self.ready(env)
            paths = []
            env["filesystem"].path.realpath = lambda path: paths.append(path) or path
            result = self.call(env)
            self.assertEqual(result[:2], ("RECEIVED_WORKER_INPUTS", "NONE"))
            held, first, second = result[2]
            self.assertEqual(held[3], env["bodies"])
            self.assertEqual(first.scalars, second.scalars)
            self.assertEqual(first.profile.token, bytes.fromhex(env["payload"][2][3]))
            self.assertGreaterEqual(len(paths), 6)
            output = bytes(env["io"].output)
            self.assertTrue(output.endswith(env["complete"]))
            rows = output[:-len(env["complete"])].splitlines(keepends=True)
            data = b"".join(row[:-1].split(b"|", 4)[4] for row in rows[1:-1])
            self.assertEqual(data, fixture.pooled((env["payload"][2],) + env["worker"][3:], "REPORTED"))
            self.assertEqual(env["io"].offset, len(env["io"].input))
            writes = [event for event in env["io"].events if event[0] == "write"]
            self.assertEqual(writes[0][2], len(env["metadata"]))
            self.assertEqual(writes[-1][2], len(env["metadata"]) + len(env["commands"][0])
                             + sum(map(len, env["bodies"])) + len(env["commands"][1]))
            self.assertTrue(all(event[1] > 0 for event in env["io"].events))
            self.assertLessEqual(len(env["io"].events), 1088)

    def test_partial_reads_and_writes_keep_offsets_without_phase_overread(self):
        env = model()
        env["io"].read_max = env["io"].write_max = 64
        self.ready(env)
        self.assertEqual(self.call(env)[0], "RECEIVED_WORKER_INPUTS")
        self.assertTrue(bytes(env["io"].output).endswith(env["complete"]))
        self.assertEqual(env["io"].offset, len(env["io"].input))
        self.assertLessEqual(len(env["io"].events), 1088)

    def test_nine_empty_bodies_never_request_zero_byte_read(self):
        env = model(bodies=(b"",) * 9)
        self.assertEqual(self.call(env)[0], "RECEIVED_WORKER_INPUTS")
        self.assertTrue(all(event[1] > 0 for event in env["io"].events))

    def test_eof_in_each_input_phase_is_atomic_and_never_completes(self):
        template = model()
        m, c, bodies = len(template["metadata"]), template["commands"], sum(map(len, template["bodies"]))
        for cut in (0, 8, m - 1, m + len(c[0]) - 1, m + len(c[0]) + 1,
                    m + len(c[0]) + bodies + len(c[1]) - 1, len(template["io"].input) - 1):
            env = model()
            env["io"].input = env["io"].input[:cut]
            self.rejected(env)
            if cut < m + len(c[0]) + bodies + len(c[1]):
                self.assertNotIn(b'"INPUT_COMPLETE"', env["io"].output)

    def test_wrong_commands_nonce_and_order_never_admit_following_phase(self):
        for n in (0, 1, 2):
            env = model()
            context = env["payload"][2]
            digest = "0" * 64
            wrong = fixture.line((KINDS[n], context[5], "0" * 64, digest)) + b"\n"
            commands = list(env["commands"])
            commands[n] = wrong
            env["io"].input = env["metadata"] + commands[0] + b"".join(env["bodies"]) + commands[1] + commands[2]
            self.rejected(env)
            if n == 0:
                self.assertEqual(env["io"].offset, len(env["metadata"]) + len(wrong))
            if n < 2: self.assertNotIn(b'"INPUT_COMPLETE"', env["io"].output)

    def test_body_hash_and_extra_eof_byte_fail_without_candidate_operation(self):
        for kind in ("body", "extra"):
            env = model()
            if kind == "body":
                start = len(env["metadata"]) + len(env["commands"][0])
                env["io"].input = env["io"].input[:start] + b"X" + env["io"].input[start + 1:]
            else: env["io"].input += b"X"
            self.rejected(env)
            if kind == "body": self.assertNotIn(b'"INPUT_COMPLETE"', env["io"].output)
            self.assertFalse(any(name in env["cache"] for name, _ in fixture.MEMBERS))

    def test_profile_hook_and_cache_drift_after_body_end_precede_input_complete(self):
        for kind in ("version", "hook", "cache"):
            env = model()
            boundary = len(env["metadata"]) + len(env["commands"][0]) + sum(map(len, env["bodies"]))
            boundary += len(env["commands"][1]) - 1
            reached = []
            def callback(io, operation):
                if reached or operation != "read" or io.offset != boundary: return
                reached.append(1)
                if kind == "version": env["runtime"].version_info = (3, 12, 99)
                elif kind == "hook": env["runtime"].path_hooks = env["runtime"].path_hooks.copy()
                else: env["cache"]["EXTRA"] = object()
            env["io"].callback = callback
            self.rejected(env)
            self.assertEqual(reached, [1])
            self.assertNotIn(b'"INPUT_COMPLETE"', env["io"].output)

    def test_foreign_io_results_counts_zero_progress_and_errors_are_closed(self):
        calls = []
        class Foreign:
            def __len__(self): calls.append("LEN"); raise AssertionError()
            def __eq__(self, other): calls.append("EQ"); raise AssertionError()
        class Bytes(bytes): pass
        for kind in ("foreign", "subclass", "oversize", "bool", "zero", "count", "readerror", "writeerror"):
            env = model()
            if kind == "foreign": env["io"].read_value = lambda size: Foreign()
            elif kind == "subclass": env["io"].read_value = lambda size: Bytes(b"x")
            elif kind == "oversize": env["io"].read_value = lambda size: b"x" * (size + 1)
            elif kind == "bool": env["io"].write_value = lambda data: True
            elif kind == "zero": env["io"].write_value = lambda data: 0
            elif kind == "count": env["io"].write_value = lambda data: len(data) + 1
            else: env["io"].error = "read" if kind == "readerror" else "write"
            self.rejected(env)
        self.assertEqual(calls, [])

    def test_child_io_input_and_output_caps_never_reset_or_write_past_cap(self):
        for slot, limit in ((3, 1088), (4, 1064960), (5, 65536)):
            env = model()
            state = owner(env)[2]
            state[slot] = limit
            self.rejected(env)
            before = len(env["io"].events)
            self.rejected(env)
            self.assertEqual(len(env["io"].events), before)
            self.assertEqual(state[slot], limit)
            if slot == 5: self.assertEqual(bytes(env["io"].output), b"")
            else: self.assertEqual(env["io"].events, [])

    def test_reentrancy_reserves_before_first_read_and_stops_outer_attempt(self):
        env, nested = model(), []
        def callback(io, operation):
            if not nested: nested.append(self.call(env))
        env["io"].callback = callback
        self.rejected(env)
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0][0], "REJECTED_WORKER_INPUT")
        self.assertEqual(len(env["io"].events), 1)

    def test_foreign_io_method_replacement_has_no_getter_or_dispatch(self):
        calls = []
        class Foreign:
            @property
            def __code__(self): calls.append("CODE"); raise AssertionError()
            def __call__(self, *args): calls.append("CALL"); raise AssertionError()
        for name in ("read", "write"):
            env = model()
            setattr(env["filesystem"], name, Foreign())
            self.rejected(env)
            self.assertEqual(env["io"].events, [])
        self.assertEqual(calls, [])

    def test_global_markers_script_helpers_and_runner_code_cannot_replace_authority(self):
        calls = []
        class Foreign:
            def __getattribute__(self, name): calls.append(name); raise AssertionError()
        for kind in ("marker", "reportmarker", "helper", "runner"):
            env = model()
            if kind == "marker": env["ns"]["_WORKER_INPUT_MARKER"] = Foreign()
            elif kind == "reportmarker": env["ns"]["_WORKER_REPORT_BINDING"] = Foreign()
            elif kind == "helper": env["ns"]["_inline_receive_declared_bodies"] = Foreign()
            else:
                function = env["ns"]["_worker_input_run"]
                function.__code__ = function.__code__.replace()
            self.rejected(env)
            self.assertEqual(env["io"].events, [])
        self.assertEqual(calls, [])

    def test_retry_reseal_reinitialize_and_missing_seal_are_sticky(self):
        for valid in (False, True):
            env = model()
            if valid: self.assertEqual(self.call(env)[0], "RECEIVED_WORKER_INPUTS")
            else:
                env["io"].input = b""
                self.rejected(env)
            before = len(env["io"].events)
            self.rejected(env)
            self.assertEqual(env["ns"]["_worker_input_seal"]()[0], "REJECTED_WORKER_INPUT")
            self.assertEqual(env["ns"]["_initialize_worker_input_control"]()[0], "REJECTED_WORKER_INPUT")
            self.assertEqual(len(env["io"].events), before)
        env = model(seal=False)
        self.rejected(env)
        self.assertEqual(env["io"].events, [])

    def test_invalid_header_and_generator_caps_fail_before_metadata_read(self):
        for magic, metadata, body in ((b"BAD0000\0", 1, 0), (b"DGNC001\0", 16369, 0),
                                      (b"DGNC001\0", 1, 1048577)):
            env = model()
            env["io"].input = struct.pack(">8sII", magic, metadata, body) + env["io"].input[16:]
            self.rejected(env)
            self.assertEqual(env["io"].offset, 16)
            self.assertEqual(bytes(env["io"].output), b"")
        with self.assertRaises(subject.base.BootstrapSourceRejected):
            subject.build_worker_input_control_bootstrap(b"x" * 131073, **OPTIONS)

    def test_binding_loss_dominates_io_exception_and_stops_additional_dispatch(self):
        for fail in (False, True):
            env, reached = model(), []
            def callback(io, operation):
                if reached: return
                reached.append(1)
                function = env["control"]._capture
                function.__code__ = function.__code__.replace()
                if fail: raise OSError("PRIVATE /synthetic/value")
            env["io"].callback = callback
            result = self.rejected(env)
            self.assertEqual(result[1], "WORKER_INPUT_BINDING")
            self.assertEqual(reached, [1])
            self.assertEqual(len(env["io"].events), 1)


if __name__ == "__main__":
    unittest.main()
