"""Synthetische Offline-Proben des DGN-007 Import-Only-Workers."""
import hashlib
import ast
from pathlib import Path
import sys
import threading
import time
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "Tools"
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))
import dgn007_import_probe_input as input_protocol
import dgn007_import_used_bytes_probe as probe
import dgn007_source_bundle as bundle


def prepared(overrides=None):
    overrides = overrides or {}
    rows = []
    for module, member in bundle.MODULES:
        body = overrides.get(module, b"SYNTHETIC_IMPORT_ONLY = True\n")
        rows.append(input_protocol.SourceBytes(module, member, hashlib.sha256(body).hexdigest(), body))
    return input_protocol.PreparedInput("a" * 40, "b" * 64,
        input_protocol.edges.PROFILE, b"n" * 32, tuple(rows))


def source_set(entry):
    bodies = {
        "run_dgn007_automated_setup": (
            b"import execution_target\nimport run_demo\nimport sqlcmd_process\n"
            b"import Tests.Contracts.dgn007_capture_projection\n"
            b"import Tests.Contracts.dgn007_collector_transport\n"
            b"import Tests.Contracts.dgn007_prospective_acceptance\n"),
        "execution_target": b"import sqlcmd_process\n",
        "run_demo": b"import orchestrate_sessions\n",
        "orchestrate_sessions": b"import sqlcmd_process\n",
        "Tests.Contracts.dgn007_capture_projection": (
            b"import Tests.Contracts.dgn007_collector_transport\n"
            b"import Tests.Contracts.dgn007_prospective_acceptance\n"),
        "Tests.Contracts.dgn007_collector_transport":
            b"import Tests.Contracts.dgn007_prospective_acceptance\n",
    }
    if entry == "docker_sqlcmd_proxy":
        bodies[entry] = b"SYNTHETIC_PROXY = True\n"
    return prepared(bodies)


class PreparationGateTests(unittest.TestCase):
    def test_public_entry_rejects_unverified_parent_input(self):
        report = probe.run_import_only(prepared())
        self.assertEqual((report.status, report.issue),
                         ("FAIL_IMPORT_ONLY", "INPUT_NOT_PREPARED"))
        self.assertFalse(report.runtime_attested or report.import_used_bytes_attested
                         or report.trust_attested or report.method_approved)

    def test_fixed_worker_sequences_match_top_level_bound_import_graph(self):
        module_by_name = dict(bundle.MODULES)
        def direct_imports(name):
            tree = ast.parse((ROOT / module_by_name[name]).read_bytes())
            names = []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    names.extend(alias.name for alias in node.names if alias.name in module_by_name)
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    if node.module in module_by_name:
                        names.append(node.module)
                    else:
                        names.extend(node.module + "." + alias.name for alias in node.names
                                     if node.module + "." + alias.name in module_by_name)
            return tuple(names)
        def visit(name, result, seen):
            if name in seen: return
            seen.add(name)
            result.append(name)
            for dependency in direct_imports(name):
                visit(dependency, result, seen)
        for ordinal, (entry, expected) in enumerate(probe.WORKERS, 1):
            actual, seen = [], set()
            visit(entry, actual, seen)
            with self.subTest(ordinal=ordinal, entry=entry):
                self.assertEqual(tuple(actual), expected)


class ReadBudgetTests(unittest.TestCase):
    def test_parallel_readers_recompute_allowance_before_buffer_append(self):
        barrier = threading.Barrier(2)
        class ConcurrentPipe:
            def __init__(self): self.calls = 0
            def read(self, _size):
                self.calls += 1
                if self.calls == 1:
                    barrier.wait(timeout=2.0)
                    return b"xx"
                return b""
        budget, lock, overflow = [1, 0], threading.Lock(), threading.Event()
        buffers = [bytearray(), bytearray()]
        readers = [threading.Thread(target=probe._read_bounded,
                    args=(ConcurrentPipe(), output, budget, lock, overflow))
                   for output in buffers]
        for reader in readers: reader.start()
        for reader in readers: reader.join(timeout=3.0)
        self.assertTrue(all(not reader.is_alive() for reader in readers))
        self.assertTrue(overflow.is_set())
        self.assertEqual(budget[1], 2)
        self.assertLessEqual(sum(map(len, buffers)), budget[0] + 1)


@unittest.skipUnless(sys.platform == "linux", "der echte Worker ist auf Linux begrenzt")
class ImportWorkerTests(unittest.TestCase):
    def run_worker(self, source, ordinal):
        frame = input_protocol.encode_input(source)
        command = [sys.executable, "-I", "-S", "-B", "-c",
                   probe._worker_source(ordinal, b"w" * 32)]
        state, stdout, stderr = probe._collect_process(
            command, frame, time.monotonic() + 10.0, probe.MAX_OUTPUT_BYTES)
        return state, stdout, stderr, frame

    def test_three_fixed_entrypoints_measure_expected_module_bytes(self):
        for ordinal, (entry, expected) in enumerate(probe.WORKERS, 1):
            with self.subTest(entry=entry):
                source = source_set(entry)
                state, stdout, stderr, _ = self.run_worker(source, ordinal)
                self.assertEqual(state, "PROCESS_EXIT_0", stderr.decode("utf-8", "replace")[-800:])
                self.assertEqual(stderr, b"")
                self.assertTrue(all(len(line) <= probe.MAX_LINE_BYTES for line in stdout.splitlines()))
                observation = probe._decode_worker_output(stdout, stderr,
                    (entry, expected), source, b"w" * 32)
                begins = tuple(r for r in observation.imports if r.phase == "BEGIN")
                completes = tuple(r for r in observation.imports if r.phase == "COMPLETE")
                self.assertEqual(tuple(r.module for r in begins), expected)
                self.assertEqual({r.module for r in completes}, set(expected))
                self.assertEqual(len(begins), len(completes))
                for receipt in begins:
                    row = next(s for s in source.sources if s.module == receipt.module)
                    self.assertEqual((receipt.member, receipt.size, receipt.sha256),
                                     (row.member, len(row.body), hashlib.sha256(row.body).hexdigest()))

    def test_worker_rejects_unknown_import_instead_of_using_live_files(self):
        source = source_set("docker_sqlcmd_proxy")
        source = input_protocol.PreparedInput(source.commit, source.raw27_binding, source.source_profile,
            source.nonce, tuple(input_protocol.SourceBytes(s.module, s.member,
                hashlib.sha256(b"import foreign_package\n").hexdigest(), b"import foreign_package\n")
                if s.module == "docker_sqlcmd_proxy" else s for s in source.sources))
        state, _, _, _ = self.run_worker(source, 2)
        self.assertEqual(state, "PROCESS_EXIT_NONZERO")

    def test_worker_rejects_reload_of_a_consumed_member(self):
        source = source_set("run_dgn007_automated_setup")
        changed = []
        for row in source.sources:
            body = row.body
            if row.module == "execution_target":
                body = b"import sqlcmd_process\nimport importlib, sys\nimportlib.reload(sys.modules['sqlcmd_process'])\n"
            changed.append(input_protocol.SourceBytes(row.module, row.member,
                hashlib.sha256(body).hexdigest(), body))
        source = input_protocol.PreparedInput(source.commit, source.raw27_binding,
            source.source_profile, source.nonce, tuple(changed))
        state, _, _, _ = self.run_worker(source, 1)
        self.assertEqual(state, "PROCESS_EXIT_NONZERO")

    def test_worker_rejects_an_unmapped_alias_for_a_bound_member(self):
        source = source_set("run_dgn007_automated_setup")
        changed = []
        for row in source.sources:
            body = b"import execution_target_alias\n" if row.module == "run_dgn007_automated_setup" else row.body
            changed.append(input_protocol.SourceBytes(row.module, row.member,
                hashlib.sha256(body).hexdigest(), body))
        source = input_protocol.PreparedInput(source.commit, source.raw27_binding,
            source.source_profile, source.nonce, tuple(changed))
        state, _, _, _ = self.run_worker(source, 1)
        self.assertEqual(state, "PROCESS_EXIT_NONZERO")

    def test_stale_worker_receipt_is_rejected_under_a_fresh_nonce(self):
        source = source_set("docker_sqlcmd_proxy")
        state, stdout, stderr, _ = self.run_worker(source, 2)
        self.assertEqual((state, stderr), ("PROCESS_EXIT_0", b""))
        with self.assertRaisesRegex(probe.ProbeRejected, "WORKER_BINDING"):
            probe._decode_worker_output(stdout, stderr, probe.WORKERS[1], source, b"x" * 32)

    def test_worker_rejects_body_exchange_after_frame_binding(self):
        source = source_set("docker_sqlcmd_proxy")
        frame = bytearray(input_protocol.encode_input(source))
        frame[-1] ^= 1
        command = [sys.executable, "-I", "-S", "-B", "-c",
                   probe._worker_source(2, b"w" * 32)]
        state, _, _ = probe._collect_process(command, bytes(frame), time.monotonic() + 10.0,
                                             probe.MAX_OUTPUT_BYTES)
        self.assertEqual(state, "PROCESS_EXIT_NONZERO")

    def test_exited_leader_with_inherited_pipe_stops_its_process_group(self):
        code = ("import subprocess,sys; "
                "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
                "print(p.pid, flush=True)")
        state, stdout, _ = probe._collect_process(
            [sys.executable, "-I", "-S", "-B", "-c", code], b"",
            time.monotonic() + 5.0, 1024)
        self.assertEqual(state, "PROCESS_END_UNKNOWN")
        pid = int(stdout.strip())
        stopped = False
        for _ in range(100):
            try:
                with open(f"/proc/{pid}/stat", encoding="ascii") as stream:
                    state_letter = stream.read().split()[2]
                stopped = state_letter == "Z"
            except FileNotFoundError:
                stopped = True
            if stopped: break
            time.sleep(0.01)
        self.assertTrue(stopped, f"synthetic child {pid} survived its process-group stop")

    def test_stdout_and_stderr_share_one_read_time_cap(self):
        code = "import os; os.write(1, b'x' * 8192); os.write(2, b'y' * 8192)"
        cap = 256
        state, stdout, stderr = probe._collect_process(
            [sys.executable, "-I", "-S", "-B", "-c", code], b"",
            time.monotonic() + 5.0, cap)
        self.assertEqual(state, "OUTPUT_LIMIT")
        self.assertLessEqual(len(stdout) + len(stderr), cap + 1)


if __name__ == "__main__":
    unittest.main()
