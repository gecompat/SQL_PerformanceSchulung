"""Derive an offline NoCloud VHDX from the fixed 24 GiB External Tables image."""

from __future__ import annotations

import argparse
from hashlib import file_digest
import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import monotonic

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from external_tables_guest_identity import _remaining
from external_tables_package_state import read_dpkg_status
from verify_external_tables_ubuntu_base import verify_derived_vhdx


_PLANNING = Path(__file__).resolve().parents[2] / "Documentation/Project_Planning"
_CLOUD_CONFIG = "/etc/cloud/cloud.cfg.d/90_dpkg.cfg"
_HOTPLUG_CONFIG = "/etc/netplan/90-hotplug-azure.yaml"
_AGENT_UNIT = "/etc/systemd/system/walinuxagent.service"
_NO_CLOUD = b"datasource_list: [ NoCloud ]\nnetwork:\n  config: disabled\n"
_TOOLS_ENV = {"LC_ALL": "C", "PATH": "/usr/sbin:/usr/bin:/sbin:/bin"}
_BLOCK = 4 * 1024 * 1024
_SECONDS = 600


def prepare_nocloud_base(source: Path, destination: Path, *, qemu_img: Path = Path("/usr/bin/qemu-img")) -> str:
    """Publish a new disk after checking the logical contents against the edited copy."""
    if sys.platform != "linux":
        raise OSError("offline template preparation requires Linux image tools")
    source = source.resolve(strict=True)
    output = destination.parent.resolve(strict=True) / destination.name
    if output.suffix.lower() != ".vhdx" or os.path.lexists(output):
        raise ValueError("expected a new VHDX in the private template directory")
    executable = str(qemu_img.resolve(strict=True))
    deadline = monotonic() + _SECONDS
    verify_derived_vhdx(source)
    evidence = json.loads((_PLANNING / "external_tables_vhdx_evidence.json").read_bytes())
    lock = json.loads((_PLANNING / "external_tables_apt_lock.json").read_bytes())
    [root_record] = [entry for entry in evidence["partitions_before_and_after"] if entry["number"] == 1]
    sector_bytes = evidence["logical_sector_bytes"]
    offset, length = root_record["first_lba"] * sector_bytes, root_record["sectors"] * sector_bytes

    with TemporaryDirectory(prefix="sqlperf-nocloud-", dir="/tmp") as folder:
        work = Path(folder)
        raw = work / "disk.raw"
        _run([executable, "convert", "-f", "vhdx", "-O", "raw", str(source), str(raw)], deadline)
        if raw.stat().st_size != evidence["derived_virtual_bytes"]:
            raise ValueError("raw image size differs from the fixed base")
        root = work / "root.ext4"
        with raw.open("rb") as source_stream, root.open("xb") as output_stream:
            source_stream.seek(offset)
            _copy_partition(source_stream, output_stream, length, deadline)
        if _digest(root) != root_record["sha256"]:
            raise ValueError("root partition differs from the fixed base")
        _set_nocloud(root, work, lock["dpkg_status_sha256"], deadline)
        with root.open("rb") as source_stream, raw.open("r+b") as output_stream:
            output_stream.seek(offset)
            _copy_partition(source_stream, output_stream, length, deadline)

        with NamedTemporaryFile(prefix=".sqlperf-nocloud-", suffix=".vhdx", dir=output.parent, delete=False) as stage:
            candidate = Path(stage.name)
        try:
            _run([executable, "convert", "-f", "raw", "-O", "vhdx", "-o", "subformat=dynamic", str(raw), str(candidate)], deadline)
            _run([executable, "compare", "-f", "raw", "-F", "vhdx", str(raw), str(candidate)], deadline)
            digest = _digest(candidate)
            _remaining(deadline)
            os.link(candidate, output)
        finally:
            candidate.unlink()
    return digest


def _copy_partition(source, destination, size: int, deadline: float) -> None:
    remaining = size
    while remaining:
        _remaining(deadline)
        data = source.read(min(_BLOCK, remaining))
        if not data:
            raise ValueError("unexpected end of root partition")
        destination.write(data)
        remaining -= len(data)


def _set_nocloud(root: Path, work: Path, package_status_digest: str, deadline: float) -> None:
    def inspect(command: str) -> bytes:
        return _run(["/usr/sbin/debugfs", "-R", command, str(root)], deadline)

    if b"datasource_list: [ Azure ]" not in inspect(f"cat {_CLOUD_CONFIG}").splitlines():
        raise ValueError("the base does not have the expected Azure datasource")
    if b"dhcp4: true" not in inspect(f"cat {_HOTPLUG_CONFIG}"):
        raise ValueError("the base does not have the expected Azure hotplug policy")
    config = work / "nocloud.cfg"
    config.write_bytes(_NO_CLOUD)
    changes = work / "debugfs.commands"
    changes.write_text("\n".join((
        f"rm {_CLOUD_CONFIG}",
        f"write {config} {_CLOUD_CONFIG}",
        f"set_inode_field {_CLOUD_CONFIG} uid 0",
        f"set_inode_field {_CLOUD_CONFIG} gid 0",
        f"set_inode_field {_CLOUD_CONFIG} mode 0100644",
        f"rm {_HOTPLUG_CONFIG}",
        f"symlink {_AGENT_UNIT} /dev/null",
        "",
    )), encoding="ascii")
    _run(["/usr/sbin/debugfs", "-w", "-f", str(changes), str(root)], deadline)
    if (
        inspect(f"cat {_CLOUD_CONFIG}") != _NO_CLOUD
        or b'Fast link dest: "/dev/null"' not in inspect(f"stat {_AGENT_UNIT}")
        or Path(_HOTPLUG_CONFIG).name.encode() in inspect("ls -p /etc/netplan")
    ):
        raise ValueError("offline guest bootstrap settings could not be confirmed")
    status = work / "status"
    inspect(f"dump /var/lib/dpkg/status {status}")
    read_dpkg_status(status)
    if _digest(status) != package_status_digest:
        raise ValueError("pinned package inventory changed during offline preparation")
    _run(["/usr/sbin/e2fsck", "-fn", str(root)], deadline)


def _run(command: list[str], deadline: float) -> bytes:
    try:
        result = collect_bounded_process(
            command, input_bytes=b"", environment=_TOOLS_ENV,
            timeout_seconds=_remaining(deadline), timeout_ceiling_seconds=_SECONDS,
            stdout_limit_bytes=256 * 1024, stderr_limit_bytes=65536,
        )
    except CaptureRunnerError:
        raise OSError("offline VHDX preparation could not complete an image operation") from None
    if result.returncode:
        raise OSError(f"offline VHDX preparation failed in {Path(command[0]).name}")
    return result.stdout


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--qemu-img", type=Path, default=Path("/usr/bin/qemu-img"))
    args = parser.parse_args(argv)
    try:
        digest = prepare_nocloud_base(args.source, args.destination, qemu_img=args.qemu_img)
    except (KeyError, OSError, ValueError) as error:
        print(f"EXTERNAL_TABLES_NOCLOUD_BASE|FAIL|{type(error).__name__}", file=sys.stderr)
        return 1
    print(json.dumps({"sha256": digest}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
