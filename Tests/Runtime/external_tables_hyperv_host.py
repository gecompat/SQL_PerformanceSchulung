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

    def __post_init__(self) -> None:
        database_name(self.token, Role.QUERY)
        linux_service_id(self.service_port)
        ids = (self.source_vm, self.query_vm, self.switch)
        if any(not isinstance(value, UUID) or not value.int for value in ids) or len(set(ids)) != 3:
            raise ValueError("expected distinct recorded Hyper-V resource IDs")
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
            )
        except (AttributeError, KeyError, TypeError, ValueError, RecursionError):
            raise ValueError("invalid recorded External Tables ownership") from None
        if owner != inventory.binding():
            raise ValueError("External Tables run ownership record is not canonical")
        return cls(directory, inventory)

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
        remove_owned: Callable[[HyperVRunInventory, float], None],
    ) -> None:
        self._journal = journal
        self._inventory = journal.inventory
        self._base_status = base_status
        self._package_lock = package_lock
        self._remove_owned = remove_owned
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
        try:
            result = collect_bounded_process(
                ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(script), *arguments],
                input_bytes=b"", environment=os.environ.copy(), timeout_seconds=min(20, _remaining(deadline)),
                timeout_ceiling_seconds=20, stdout_limit_bytes=4096, stderr_limit_bytes=4096,
            )
            expected = _PROBES[name]
            actual = json.loads(result.stdout)
            if result.returncode or result.stderr or actual != expected or any(
                type(actual[key]) is not type(value) for key, value in expected.items()
            ):
                raise ValueError("unexpected Hyper-V verifier output")
            _remaining(deadline)
        except (CaptureRunnerError, OSError, ValueError, RecursionError):
            raise OSError(f"External Tables Hyper-V {name} verification failed") from None


def run_prepared_hyperv_pilot(
    journal: RunJournal, base_status: bytes, package_lock: dict,
    remove_owned: Callable[[HyperVRunInventory, float], None],
) -> PilotResult:
    """Run only after the provider has journaled both prepared, admitted guests."""
    return run_pilot(HyperVPreparedTransport(journal, base_status, package_lock, remove_owned), journal.inventory.token)
