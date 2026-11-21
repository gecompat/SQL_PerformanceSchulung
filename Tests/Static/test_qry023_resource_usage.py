"""Synthetic ownership, path, and limit regressions for QRY-023 resource capture."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "Runtime/qry023_resource_usage.py"
SPEC = importlib.util.spec_from_file_location("qry023_resource_usage", SCRIPT)
assert SPEC and SPEC.loader
resource_usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resource_usage)

OWNER = "a" * 32
CONTAINER_ID = "b" * 64
CONTAINER = "sqlperf-qry023-17-12345-1"
PID = "321"
CGROUP_PATH = f"/docker/{CONTAINER_ID}"


class Qry023ResourceUsageTests(unittest.TestCase):
    def _fixture(self, root: Path, *, peak: int = 512_000_000, memory_limit: int = 4 * 1024**3):
        cgroup = root / "docker" / CONTAINER_ID
        cgroup.mkdir(parents=True)
        (cgroup / "memory.peak").write_text(f"{peak}\n", encoding="ascii")
        (cgroup / "memory.max").write_text(f"{memory_limit}\n", encoding="ascii")
        (cgroup / "cpu.stat").write_text("usage_usec 123456\nuser_usec 100000\nsystem_usec 23456\n", encoding="ascii")
        (cgroup / "cpu.max").write_text("200000 100000\n", encoding="ascii")
        proc = root.parent / "proc"
        (proc / PID).mkdir(parents=True)
        (proc / PID / "cgroup").write_text(f"0::{CGROUP_PATH}\n", encoding="ascii")
        return proc, root

    def _inspect(self, *, owner: str = OWNER, memory: str | None = None, nano_cpus: str | None = None):
        def answer(container: str, template: str) -> str:
            if template == "{{.Id}}":
                return CONTAINER_ID
            if template == '{{ index .Config.Labels "sqlperf.ci.owner" }}':
                return owner
            if template == "{{.State.Pid}}":
                return PID
            if template == "{{.HostConfig.Memory}}":
                return memory or str(4 * 1024**3)
            if template == "{{.HostConfig.NanoCpus}}":
                return nano_cpus or "2000000000"
            raise AssertionError(template)
        return answer

    def test_captures_only_contract_bounded_owned_cgroup_usage(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            proc, cgroup = self._fixture(base / "sys", peak=987_654_321)
            with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect()):
                result = resource_usage.capture(CONTAINER, OWNER, proc_root=proc, cgroup_root=cgroup)
        self.assertEqual(result["container_id"], CONTAINER_ID)
        self.assertEqual(result["memory_peak_bytes"], 987_654_321)
        self.assertEqual(result["memory_limit_bytes"], 4 * 1024**3)
        self.assertEqual(result["cpu_usage_usec"], 123456)

    def test_rejects_unexpected_container_name(self):
        with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "name"):
            resource_usage.capture("foreign-sql", OWNER)

    def test_rejects_owner_mismatch_before_reading_proc(self):
        with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect(owner="c" * 32)):
            with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "owner"):
                resource_usage.capture(CONTAINER, OWNER)

    def test_rejects_wrong_docker_memory_limit(self):
        with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect(memory="4096")):
            with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "memory limit"):
                resource_usage.capture(CONTAINER, OWNER)

    def test_rejects_wrong_docker_cpu_limit(self):
        with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect(nano_cpus="1000000000")):
            with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "CPU limit"):
                resource_usage.capture(CONTAINER, OWNER)

    def test_rejects_cgroup_path_for_another_container(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            proc, cgroup = self._fixture(base / "sys")
            (proc / PID / "cgroup").write_text("0::/docker/" + "c" * 64 + "\n", encoding="ascii")
            with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect()):
                with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "container ID"):
                    resource_usage.capture(CONTAINER, OWNER, proc_root=proc, cgroup_root=cgroup)

    def test_rejects_memory_peak_above_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            proc, cgroup = self._fixture(base / "sys", peak=5 * 1024**3)
            with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect()):
                with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "violates"):
                    resource_usage.capture(CONTAINER, OWNER, proc_root=proc, cgroup_root=cgroup)

    def test_rejects_missing_unified_cgroup(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            proc, cgroup = self._fixture(base / "sys")
            (proc / PID / "cgroup").write_text("1:memory:/legacy\n", encoding="ascii")
            with mock.patch.object(resource_usage, "_inspect", side_effect=self._inspect()):
                with self.assertRaisesRegex(resource_usage.ResourceCaptureError, "cgroup-v2"):
                    resource_usage.capture(CONTAINER, OWNER, proc_root=proc, cgroup_root=cgroup)


if __name__ == "__main__":
    unittest.main()
