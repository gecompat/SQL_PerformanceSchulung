"""Capture peak cgroup-v2 usage for the owned QRY-023 disposable container."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


EXPECTED_MEMORY_LIMIT_BYTES = 4 * 1024 * 1024 * 1024
EXPECTED_NANO_CPUS = 2_000_000_000
CONTAINER_ID_RE = re.compile(r"[0-9a-f]{64}\Z")
CGROUP_PATH_RE = re.compile(r"/[A-Za-z0-9._/-]+\Z")


class ResourceCaptureError(RuntimeError):
    pass


def _inspect(container: str, template: str) -> str:
    result = subprocess.run(
        ["docker", "inspect", "--format", template, container],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


def _read_int(path: Path, label: str) -> int:
    try:
        value = path.read_text(encoding="ascii").strip()
    except OSError as exc:
        raise ResourceCaptureError(f"cannot read cgroup {label}") from exc
    if not value.isdecimal():
        raise ResourceCaptureError(f"cgroup {label} is not a decimal integer")
    return int(value)


def capture(
    container: str,
    expected_owner: str,
    *,
    proc_root: Path = Path("/proc"),
    cgroup_root: Path = Path("/sys/fs/cgroup"),
) -> dict[str, int | str]:
    """Read bounded peak memory and cumulative CPU only for this owned container."""
    if not re.fullmatch(r"sqlperf-qry023-(15|16|17)-[0-9]+-[0-9]+", container):
        raise ResourceCaptureError("container name is outside the QRY-023 run contract")
    if not expected_owner or not re.fullmatch(r"[0-9a-f]{32}", expected_owner):
        raise ResourceCaptureError("expected owner marker is invalid")

    container_id = _inspect(container, "{{.Id}}")
    if not CONTAINER_ID_RE.fullmatch(container_id):
        raise ResourceCaptureError("container ID is malformed")
    owner = _inspect(container_id, '{{ index .Config.Labels "sqlperf.ci.owner" }}')
    if owner != expected_owner:
        raise ResourceCaptureError("container owner marker does not match this run")
    pid_text = _inspect(container_id, "{{.State.Pid}}")
    if not pid_text.isdecimal() or int(pid_text) <= 0:
        raise ResourceCaptureError("owned container has no live init process")
    memory_limit = _inspect(container_id, "{{.HostConfig.Memory}}")
    nano_cpus = _inspect(container_id, "{{.HostConfig.NanoCpus}}")
    if memory_limit != str(EXPECTED_MEMORY_LIMIT_BYTES):
        raise ResourceCaptureError("container memory limit differs from the QRY-023 contract")
    if nano_cpus != str(EXPECTED_NANO_CPUS):
        raise ResourceCaptureError("container CPU limit differs from the QRY-023 contract")

    try:
        cgroup_lines = (proc_root / pid_text / "cgroup").read_text(encoding="ascii").splitlines()
    except OSError as exc:
        raise ResourceCaptureError("cannot read the container process cgroup") from exc
    unified = [line[3:] for line in cgroup_lines if line.startswith("0::")]
    if len(unified) != 1 or not CGROUP_PATH_RE.fullmatch(unified[0]):
        raise ResourceCaptureError("container does not expose one safe cgroup-v2 path")
    if container_id not in unified[0]:
        raise ResourceCaptureError("cgroup path is not bound to the inspected container ID")

    root = cgroup_root.resolve(strict=True)
    try:
        cgroup_dir = (root / unified[0].lstrip("/")).resolve(strict=True)
    except OSError as exc:
        raise ResourceCaptureError("container cgroup directory is unavailable") from exc
    if root not in cgroup_dir.parents:
        raise ResourceCaptureError("resolved cgroup directory escapes the cgroup root")

    peak = _read_int(cgroup_dir / "memory.peak", "memory.peak")
    actual_limit = _read_int(cgroup_dir / "memory.max", "memory.max")
    if actual_limit != EXPECTED_MEMORY_LIMIT_BYTES or peak > actual_limit:
        raise ResourceCaptureError("observed cgroup memory limit or peak violates the contract")
    try:
        cpu_values = dict(
            line.split(maxsplit=1)
            for line in (cgroup_dir / "cpu.stat").read_text(encoding="ascii").splitlines()
            if len(line.split(maxsplit=1)) == 2
        )
        quota, period = (cgroup_dir / "cpu.max").read_text(encoding="ascii").split()
        cpu_usage = int(cpu_values["usage_usec"])
        quota_value, period_value = int(quota), int(period)
    except (OSError, ValueError, KeyError) as exc:
        raise ResourceCaptureError("cannot parse cgroup CPU counters") from exc
    if cpu_usage <= 0 or quota_value <= 0 or period_value <= 0:
        raise ResourceCaptureError("cgroup CPU counters or limit are not positive")
    if quota_value / period_value != 2:
        raise ResourceCaptureError("observed cgroup CPU quota differs from two CPUs")

    return {
        "container_id": container_id,
        "memory_peak_bytes": peak,
        "memory_limit_bytes": actual_limit,
        "cpu_usage_usec": cpu_usage,
        "cpu_quota_usec": quota_value,
        "cpu_period_usec": period_value,
    }


def main() -> int:
    container = os.environ.get("SQLPERF_SQL_CONTAINER", "")
    owner = os.environ.get("SQLPERF_CI_OWNER", "")
    if not container and not owner:
        print("QRY023_RESOURCE_USAGE|SKIP|container_not_started")
        return 0
    try:
        metrics = capture(container, owner)
    except (ResourceCaptureError, subprocess.SubprocessError) as exc:
        print(f"QRY023_RESOURCE_USAGE|FAIL|{exc}", file=sys.stderr)
        return 1
    fields = "|".join(f"{key}={value}" for key, value in metrics.items())
    print(f"QRY023_RESOURCE_USAGE|PASS|{fields}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
