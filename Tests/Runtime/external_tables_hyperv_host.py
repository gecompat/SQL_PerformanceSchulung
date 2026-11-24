"""Bind the admitted External Tables pilot to its prepared Hyper-V guests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import json
import os
from pathlib import Path, PureWindowsPath
from stat import S_ISREG
from tempfile import NamedTemporaryFile
from uuid import UUID

from dgn004_capture_runner import CaptureRunnerError, collect_bounded_process
from external_tables_guest_admin import AdminCommand, GuestSqlChannel
from external_tables_guest_identity import _remaining, linux_service_id, verify_guest
from external_tables_measurement import MeasurementResult
from external_tables_pilot import PilotResult, run_pilot
from external_tables_pilot_sql import Role, database_name
from external_tables_principals import Principal, login_sid_literal


@dataclass(frozen=True)
class HyperVRunInventory:
    token: str
    source_vm: UUID = field(repr=False)
    query_vm: UUID = field(repr=False)
    switch: UUID = field(repr=False)
    source_disk: PureWindowsPath = field(repr=False)
    query_disk: PureWindowsPath = field(repr=False)
    service_port: int
    source_disk_id: UUID | None = field(default=None, repr=False)
    query_disk_id: UUID | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        database_name(self.token, Role.QUERY)
        linux_service_id(self.service_port)
        ids = (self.source_vm, self.query_vm, self.switch)
        if any(not isinstance(value, UUID) or not value.int for value in ids) or len(set(ids)) != 3:
            raise ValueError("expected distinct recorded Hyper-V resource IDs")
        disk_ids = self.source_disk_id, self.query_disk_id
        if any(value is not None for value in disk_ids):
            all_ids = (*ids, *disk_ids)
            if any(not isinstance(value, UUID) or not value.int for value in all_ids) or len(set(all_ids)) != 5:
                raise ValueError("expected distinct recorded VHDX identities")
        disks = (self.source_disk, self.query_disk)
        if any(
            not isinstance(path, PureWindowsPath) or not path.is_absolute() or len(path.drive) != 2
            or ".." in path.parts or path.suffix.lower() != ".vhdx" or path.parent == PureWindowsPath(path.anchor)
            for path in disks
        ) or self.source_disk == self.query_disk or self.source_disk.parent != self.query_disk.parent:
            raise ValueError("expected two recorded local VHDX files in one runtime directory")

    def binding(self) -> bytes:
        """Canonical non-secret record used to reopen the same run inventory."""
        record = {
            "version": 1,
            "run": self.token,
            "source_vm": str(self.source_vm),
            "query_vm": str(self.query_vm),
            "switch": str(self.switch),
            "source_disk": str(self.source_disk),
            "query_disk": str(self.query_disk),
            "service_port": self.service_port,
        }
        if self.source_disk_id is not None:
            record.update(version=2, source_disk_id=str(self.source_disk_id), query_disk_id=str(self.query_disk_id))
        return json.dumps(record, sort_keys=True, ensure_ascii=True).encode("ascii") + b"\n"


class RunJournal:
    """Publish immutable ownership and SID records in the private run directory."""

    def __init__(self, directory: Path, inventory: HyperVRunInventory) -> None:
        self._directory = directory.resolve(strict=True)
        if not self._directory.is_dir():
            raise ValueError("expected the private External Tables run directory")
        self.inventory = inventory

    @classmethod
    def load(cls, directory: Path) -> RunJournal:
        owner = cls._read(directory.resolve(strict=True) / "external-tables-owner.json", 4096)
        if owner is None:
            raise ValueError("External Tables run has no recorded ownership")
        try:
            record = json.loads(owner)
            inventory = HyperVRunInventory(
                record["run"], UUID(record["source_vm"]), UUID(record["query_vm"]), UUID(record["switch"]),
                PureWindowsPath(record["source_disk"]), PureWindowsPath(record["query_disk"]), record["service_port"],
                UUID(record["source_disk_id"]) if record["version"] == 2 else None,
                UUID(record["query_disk_id"]) if record["version"] == 2 else None,
            )
        except (AttributeError, KeyError, TypeError, ValueError, RecursionError):
            raise ValueError("invalid recorded External Tables ownership") from None
        if owner != inventory.binding():
            raise ValueError("External Tables run ownership record is not canonical")
        return cls(directory, inventory)

    @classmethod
    def from_detached(cls, directory: Path, token: str, service_port: int) -> RunJournal:
        """Bind the completed provision receipt and its individual ownership records."""
        root = directory.resolve(strict=True)

        def record(name: str) -> dict:
            data = cls._read(root / name, 4096)
            if data is None:
                raise ValueError("External Tables detached provision record is missing")
            try:
                value = json.loads(data)
            except (ValueError, RecursionError):
                raise ValueError("invalid External Tables detached provision record") from None
            if type(value) is not dict:
                raise ValueError("invalid External Tables detached provision record")
            return value

        receipt = record("external-tables-detached.json")
        prefix = f"SQLPerfExt-{token}"
        if set(receipt) != {"run", "source_vm", "query_vm", "switch", "source_disk_id", "query_disk_id"} or receipt["run"] != token:
            raise ValueError("detached provision receipt differs from the expected run")
        if record("external-tables-provision-intent.json") != {
            "version": 1, "run": token, "switch": prefix, "vms": [f"{prefix}-SOURCE", f"{prefix}-QUERY"],
            "disks": ["source.vhdx", "query.vhdx"],
        } or record("external-tables-switch.json") != {"name": prefix, "id": receipt["switch"]}:
            raise ValueError("detached provision intent or switch differs from the receipt")
        for role in Role:
            key = role.value.lower()
            if record(f"external-tables-vm-{role.value}.json") != {
                "role": role.value, "name": f"{prefix}-{role.value}", "id": receipt[f"{key}_vm"],
            } or record(f"external-tables-disk-{role.value}.json") != {
                "role": role.value, "file": f"{key}.vhdx", "id": receipt[f"{key}_disk_id"],
            }:
                raise ValueError("detached provision guest or disk differs from the receipt")
        try:
            inventory = HyperVRunInventory(
                token, UUID(receipt["source_vm"]), UUID(receipt["query_vm"]), UUID(receipt["switch"]),
                PureWindowsPath(root / "source.vhdx"), PureWindowsPath(root / "query.vhdx"), service_port,
                UUID(receipt["source_disk_id"]), UUID(receipt["query_disk_id"]),
            )
        except (AttributeError, TypeError, ValueError):
            raise ValueError("invalid detached External Tables identity") from None
        journal = cls(root, inventory)
        journal.bind()
        return journal

    def bind(self) -> None:
        self._publish(self._directory / "external-tables-owner.json", self.inventory.binding(), allow_existing=True)

    def claim_work(self) -> None:
        self.require_binding()
        self._publish(self._directory / "external-tables-work", b"STARTED\n")

    def require_binding(self) -> None:
        if self._read(self._directory / "external-tables-owner.json", 4096) != self.inventory.binding():
            raise ValueError("External Tables run inventory does not match its journal")

    def record_login(self, principal: Principal, sid: bytes) -> None:
        self.require_binding()
        login_sid_literal(sid)
        self._publish(self._login_path(principal), sid, allow_existing=True)

    def login_sids(self) -> dict[Principal, bytes]:
        self.require_binding()
        inventory = {}
        for principal in Principal:
            sid = self._read(self._login_path(principal), 16)
            if sid is not None:
                login_sid_literal(sid)
                inventory[principal] = sid
        return inventory

    def _login_path(self, principal: Principal) -> Path:
        if not isinstance(principal, Principal):
            raise ValueError("expected an External Tables login role")
        return self._directory / f"{principal.name.lower()}.sid"

    @staticmethod
    def _read(path: Path, limit: int) -> bytes | None:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            return None
        if not S_ISREG(metadata.st_mode) or metadata.st_size > limit:
            raise ValueError("unexpected External Tables journal record type or size")
        with path.open("rb") as record:
            body = record.read(limit + 1)
        if len(body) > limit:
            raise ValueError("External Tables journal record exceeds its size limit")
        return body

    @classmethod
    def _publish(cls, path: Path, body: bytes, *, allow_existing: bool = False) -> None:
        with NamedTemporaryFile(dir=path.parent, prefix=".external-tables-", delete=False) as staging:
            temporary = Path(staging.name)
            try:
                staging.write(body)
                staging.flush()
                os.fsync(staging.fileno())
                staging.close()
                try:
                    os.link(temporary, path)
                except FileExistsError:
                    if not allow_existing or cls._read(path, len(body)) != body:
                        raise ValueError("External Tables refuses to replace a recorded run identity")
            finally:
                staging.close()
                temporary.unlink()


_PROBES = {
    "resources": {
        "status": "PASS", "guest_count": 2, "vcpus_per_guest": 2,
        "memory_bytes_per_guest": 4 * 1024 ** 3, "max_disk_bytes_per_guest": 24 * 1024 ** 3,
    },
    "network": {"status": "PASS", "switch_type": "Private", "attached_guest_count": 2},
    "absence": {"status": "PASS", "guest_count": 0, "switch_count": 0, "disk_count": 0},
}


class HyperVPreparedTransport:
    """Verify the provider's already prepared owned guests and run the SQL plan."""

    def __init__(
        self, journal: RunJournal, base_status: bytes, package_lock: dict,
        remove_owned: Callable[[HyperVRunInventory, float], None] | None = None,
    ) -> None:
        self._journal = journal
        self._inventory = journal.inventory
        self._base_status = base_status
        self._package_lock = package_lock
        self._remove_owned = self._remove_recorded if remove_owned is None else remove_owned
        self._use_builtin_cleanup = remove_owned is None
        self._channel = GuestSqlChannel(
            self._inventory.token, self._inventory.source_vm, self._inventory.query_vm,
            self._inventory.service_port, base_status, package_lock,
        )
        self._claimed = False
        self._verified = False

    def start_verified_guests(self, token: str, deadline: float) -> None:
        self._check_token(token)
        self._verified = False
        _remaining(deadline)
        if self._use_builtin_cleanup and self._inventory.source_disk_id is None:
            raise ValueError("External Tables cleanup requires both recorded VHDX identities")
        self._journal.claim_work()
        self._claimed = True
        self._probe("resources", deadline)
        self._probe("network", deadline)
        for role, vm_id in ((Role.SOURCE, self._inventory.source_vm), (Role.QUERY, self._inventory.query_vm)):
            verify_guest(
                vm_id, self._inventory.service_port, token, role, deadline,
                base_status=self._base_status, package_lock=self._package_lock,
            )
        self._verified = True

    def admin(self, role: Role, command: AdminCommand, deadline: float) -> bool | None:
        return self._sql().admin(role, command, deadline)

    def record_login(self, principal: Principal, sid: bytes, deadline: float) -> None:
        self._sql()
        _remaining(deadline)
        self._journal.record_login(principal, sid)

    def verify_source_tls(self, token: str, secret: str, deadline: float) -> None:
        self._sql().verify_source_tls(token, secret, deadline)

    def probe_principal(self, principal: Principal, secret: str, deadline: float) -> None:
        self._sql().probe_principal(principal, secret, deadline)

    def measure(self, token: str, reader_secret: str, observer_secret: str, deadline: float) -> MeasurementResult:
        return self._sql().measure(token, reader_secret, observer_secret, deadline)

    def close_data_connections(self, token: str, login_sids: Mapping[Principal, bytes], deadline: float) -> bool:
        if self._journal.login_sids() != login_sids:
            raise ValueError("External Tables cleanup SIDs differ from the recorded inventory")
        return self._sql().close_data_connections(token, login_sids, deadline)

    def remove_verified_guests(self, token: str, deadline: float) -> bool:
        self._check_token(token)
        if not self._claimed:
            return False
        self._journal.require_binding()
        _remaining(deadline)
        self._verified = False
        self._remove_owned(self._inventory, deadline)
        self._probe("absence", deadline)
        self._claimed = False
        return True

    def _sql(self) -> GuestSqlChannel:
        if not self._verified:
            raise OSError("External Tables host and guest preflight has not passed")
        return self._channel

    def _check_token(self, token: str) -> None:
        if token != self._inventory.token:
            raise ValueError("unexpected External Tables host run token")

    def _probe(self, name: str, deadline: float) -> None:
        script = Path(__file__).resolve().with_name(f"Test-ExternalTablesHyperV{name.title()}.ps1")
        target = self._inventory
        arguments = ["-SourceVmId", str(target.source_vm), "-QueryVmId", str(target.query_vm)]
        if name != "resources":
            arguments.extend(["-SwitchId", str(target.switch)])
        if name != "network":
            arguments.extend(["-SourceDiskPath", str(target.source_disk), "-QueryDiskPath", str(target.query_disk)])
        self._run_hyperv_script(script, arguments, _PROBES[name], name, deadline, 20)

    def _remove_recorded(self, target: HyperVRunInventory, deadline: float) -> None:
        if target != self._inventory or target.source_disk_id is None or target.query_disk_id is None:
            raise ValueError("External Tables cannot remove resources without the bound VHDX identities")
        script = Path(__file__).resolve().with_name("Remove-ExternalTablesHyperVOwnedRun.ps1")
        arguments = [
            "-RunToken", target.token, "-SourceVmId", str(target.source_vm), "-QueryVmId", str(target.query_vm),
            "-SwitchId", str(target.switch), "-SourceDiskPath", str(target.source_disk),
            "-QueryDiskPath", str(target.query_disk), "-SourceDiskId", str(target.source_disk_id),
            "-QueryDiskId", str(target.query_disk_id), "-ApplyOwnedRun",
        ]
        self._run_hyperv_script(script, arguments, {"status": "REMOVED"}, "removal", deadline, 90)

    @staticmethod
    def _run_hyperv_script(
        script: Path, arguments: list[str], expected: dict, name: str, deadline: float, limit: int,
    ) -> None:
        try:
            result = collect_bounded_process(
                ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(script), *arguments],
                input_bytes=b"", environment=os.environ.copy(), timeout_seconds=min(limit, _remaining(deadline)),
                timeout_ceiling_seconds=limit, stdout_limit_bytes=4096, stderr_limit_bytes=4096,
            )
            actual = json.loads(result.stdout)
            if result.returncode or result.stderr or actual != expected or any(
                type(actual[key]) is not type(value) for key, value in expected.items()
            ):
                raise ValueError("unexpected Hyper-V verifier output")
            _remaining(deadline)
        except (CaptureRunnerError, OSError, ValueError, RecursionError):
            raise OSError(f"External Tables Hyper-V {name} verification failed") from None



def provision_detached_hyperv(
    directory: Path, token: str, service_port: int, deadline: float, *,
    source_template: Path, source_sha256: str, query_template: Path, query_sha256: str,
) -> RunJournal:
    """Create the detached resources only inside an admitted provider operation."""
    database_name(token, Role.QUERY)
    linux_service_id(service_port)
    if os.name != "nt":
        raise OSError("External Tables Hyper-V provisioning requires Windows")
    root = directory.resolve(strict=True)
    script = Path(__file__).resolve().with_name("New-ExternalTablesHyperVDetachedRun.ps1")
    arguments = [
        "-RunToken", token, "-RunDirectory", str(root),
        "-SourceTemplate", str(source_template.resolve(strict=True)), "-SourceSha256", source_sha256,
        "-QueryTemplate", str(query_template.resolve(strict=True)), "-QuerySha256", query_sha256,
        "-ApplyOwnedRun",
    ]
    HyperVPreparedTransport._run_hyperv_script(script, arguments, {"status": "DETACHED"}, "provision", deadline, 600)
    return RunJournal.from_detached(root, token, service_port)


def run_prepared_hyperv_pilot(
    journal: RunJournal, base_status: bytes, package_lock: dict,
    remove_owned: Callable[[HyperVRunInventory, float], None] | None = None,
) -> PilotResult:
    """Run only after the provider has journaled both prepared, admitted guests."""
    return run_pilot(HyperVPreparedTransport(journal, base_status, package_lock, remove_owned), journal.inventory.token)
