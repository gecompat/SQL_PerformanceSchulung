"""Send fixed SQL administration commands to an identity-verified pilot guest."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from enum import Enum
import json
from socket import socket
from struct import Struct
from threading import Lock
from time import monotonic
from typing import TYPE_CHECKING
from uuid import UUID

from external_tables_cleanup import drop_pilot_database_batch, drop_pilot_logins_batch, quiesce_pilot_logins_batch
from external_tables_guest_identity import (
    _receive, _remaining, _reply_to_probe, _send, connect_verified_guest, linux_service_id, open_parent_listener,
)
from external_tables_driver_evidence import DriverEvidence
from external_tables_measurement import MeasurementResult
from external_tables_odbc import (
    Connection, OdbcDriver, OdbcPilotAdministration, PrincipalConnection, run_guest_measurement,
    verify_guest_principal, verify_source_tls,
)
from external_tables_pilot_sql import (
    Role, Route, configure_database_batch, create_database_batch, database_name, external_tables_batch,
    fixture_batch, fixture_read_batch, statistics_batch, verify_fixture,
)
from external_tables_polybase_service import stop_query_connector
from external_tables_principals import Principal, create_connector_credential_batch, create_principal_batch
from external_tables_pushdown_evidence import PUSHDOWN_FILTER_EVIDENCE


if TYPE_CHECKING:
    from external_tables_guest_network import GuestNetwork


class AdminAction(Enum):
    CREATE_DATABASE = "create_database"
    CONFIGURE_DATABASE = "configure_database"
    CREATE_FIXTURE = "create_fixture"
    VERIFY_FIXTURE = "verify_fixture"
    CREATE_PRINCIPAL = "create_principal"
    CREATE_CREDENTIAL = "create_credential"
    CREATE_EXTERNAL_TABLES = "create_external_tables"
    CREATE_STATISTICS = "create_statistics"
    CHECK_PRINCIPAL = "check_principal"
    CHECK_SOURCE_TLS = "check_source_tls"
    MEASURE = "measure"
    DATABASE_EXISTS = "database_exists"
    DROP_DATABASE = "drop_database"
    DROP_LOGINS = "drop_logins"
    QUIESCE = "quiesce"
    STOP_QUERY_ENGINE = "stop_query_engine"


@dataclass(frozen=True)
class AdminCommand:
    action: AdminAction
    fields: tuple[str, ...] = field(default=(), repr=False)


_SIZE = Struct("!H")
_COMMAND_HEADER = Struct("!IH")
_MAX_COMMAND = 1024
_REJECTED, _DONE, _ABSENT, _PRESENT = b"\x00", b"\x01", b"\x02", b"\x03"
_MEASUREMENT = b"\x04"
_MAX_DRIVER_EVIDENCE = 512
_MEASUREMENT_STATES = ("NOT_PROVEN", "FAIL_CLEANUP", "PASS")
_MEASUREMENT_STAGES = ("query_connection", *(route.name for route in Route), "comparison", "driver_unconfirmed")
_NO_FIELDS = {
    AdminAction.CREATE_DATABASE: create_database_batch,
    AdminAction.CONFIGURE_DATABASE: configure_database_batch,
    AdminAction.CREATE_FIXTURE: fixture_batch,
    AdminAction.CREATE_EXTERNAL_TABLES: external_tables_batch,
    AdminAction.CREATE_STATISTICS: statistics_batch,
    AdminAction.DROP_DATABASE: drop_pilot_database_batch,
}
_CLEANUP_ACTIONS = frozenset((
    AdminAction.QUIESCE, AdminAction.DATABASE_EXISTS, AdminAction.DROP_DATABASE, AdminAction.DROP_LOGINS,
    AdminAction.STOP_QUERY_ENGINE,
))
_QUERY_ONLY = {AdminAction.CREATE_CREDENTIAL, AdminAction.CREATE_EXTERNAL_TABLES, AdminAction.CREATE_STATISTICS}


class GuestSqlAccess:
    """Keep one access state for the guest service's entire run."""

    def __init__(self, token: str, role: Role) -> None:
        self._identity = token, role
        self._lock = Lock()
        self._closing = False
        self._closed = False
        self._logins_dropped = False

    @contextmanager
    def command(self, token: str, role: Role, action: AdminAction, deadline: float) -> Iterator[None]:
        if (token, role) != self._identity:
            raise ValueError("guest command differs from the configured run or role")
        if not self._lock.acquire(timeout=_remaining(deadline)):
            raise TimeoutError("guest command did not acquire its service scope")
        try:
            if action is AdminAction.QUIESCE:
                self._closing = True
                self._closed = False
                self._logins_dropped = False
            elif action in (AdminAction.DROP_DATABASE, AdminAction.DROP_LOGINS):
                if not self._closed:
                    raise ValueError("guest has not confirmed that its logins are closed")
            elif action is AdminAction.STOP_QUERY_ENGINE:
                if role is not Role.QUERY or not self._closed or not self._logins_dropped:
                    raise ValueError("query engine teardown requires verified SQL object and login cleanup")
            elif self._closing and action is not AdminAction.DATABASE_EXISTS:
                raise ValueError("guest is in SQL cleanup")
            yield
            if action is AdminAction.QUIESCE:
                self._closed = True
            elif action is AdminAction.DROP_LOGINS:
                self._logins_dropped = True
        finally:
            self._lock.release()


def dispatch_admin(
    admin: OdbcPilotAdministration, token: str, role: Role, command: AdminCommand, deadline: float,
) -> bool | None:
    """Build SQL locally, using only the fixed operation and bounded data fields."""
    _remaining(deadline)
    db = database_name(token, role)
    action, fields = command.action, command.fields
    if action in _QUERY_ONLY and role is not Role.QUERY:
        raise ValueError("operation is not allowed on the source guest")
    if action in _NO_FIELDS and not fields:
        builder = _NO_FIELDS[action]
        sql = builder(token) if action in _QUERY_ONLY else builder(token, role)
        admin.execute("master" if action is AdminAction.CREATE_DATABASE else db, sql, deadline)
    elif action is AdminAction.VERIFY_FIXTURE and len(fields) == 1:
        route = Route.__members__.get(fields[0])
        verify_fixture(admin.fixture_rows(fixture_read_batch(token, role, route), deadline))
    elif action is AdminAction.CREATE_PRINCIPAL and len(fields) == 3:
        principal = _principal(fields[0], role)
        admin.execute(db, create_principal_batch(token, principal, fields[1], _sid(fields[2])), deadline)
    elif action is AdminAction.CREATE_CREDENTIAL and len(fields) == 2:
        admin.execute(db, create_connector_credential_batch(token, *fields), deadline)
    elif action is AdminAction.STOP_QUERY_ENGINE and not fields and role is Role.QUERY:
        stop_query_connector(deadline)
    elif action is AdminAction.DATABASE_EXISTS and not fields:
        return admin.database_exists(db, deadline)
    elif action in (AdminAction.DROP_LOGINS, AdminAction.QUIESCE) and len(fields) in (0, 2, 4):
        principals = {
            _principal(name, role): _sid(sid) for name, sid in zip(fields[::2], fields[1::2], strict=True)
        }
        if len(principals) * 2 != len(fields):
            raise ValueError("duplicate principal in guest cleanup command")
        builder = quiesce_pilot_logins_batch if action is AdminAction.QUIESCE else drop_pilot_logins_batch
        admin.execute("master", builder(token, role, principals), deadline)
    else:
        raise ValueError("invalid guest administration command")
    return None


def _principal(name: str, role: Role) -> Principal:
    principal = Principal.__members__.get(name)
    if principal is None or principal.role is not role:
        raise ValueError("unknown principal for the verified guest role")
    return principal


def _sid(value: str) -> bytes:
    if len(value) != 32 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError("invalid recorded guest login SID")
    sid = bytes.fromhex(value)
    if not any(sid):
        raise ValueError("invalid recorded guest login SID")
    return sid


def invoke_guest_admin(
    vm_id: UUID, port: int, token: str, role: Role, command: AdminCommand, deadline: float, *,
    base_status: bytes, package_lock: dict,
) -> bool | MeasurementResult | None:
    """Verify this VM and its package inventory on the command connection."""
    with connect_verified_guest(
        vm_id, port, token, role, deadline, base_status=base_status, package_lock=package_lock,
    ) as channel:
        return _send_command(channel, command, deadline)


def invoke_guest_measurement(
    vm_id: UUID, port: int, token: str, reader_secret: str, observer_secret: str, deadline: float, *,
    base_status: bytes, package_lock: dict,
) -> MeasurementResult:
    result = invoke_guest_admin(
        vm_id, port, token, Role.QUERY, AdminCommand(AdminAction.MEASURE, (reader_secret, observer_secret)), deadline,
        base_status=base_status, package_lock=package_lock,
    )
    if not isinstance(result, MeasurementResult):
        raise OSError("guest measurement result was not confirmed")
    return result


@dataclass(frozen=True)
class GuestSqlChannel:
    """Bind the host's SQL operations to the two recorded VM identities."""

    token: str
    source_vm: UUID = field(repr=False)
    query_vm: UUID = field(repr=False)
    port: int
    base_status: bytes = field(repr=False)
    package_lock: dict = field(repr=False)

    def __post_init__(self) -> None:
        database_name(self.token, Role.QUERY)
        linux_service_id(self.port)
        ids = (self.source_vm, self.query_vm)
        if any(not isinstance(vm_id, UUID) or not vm_id.int for vm_id in ids) or len(set(ids)) != 2:
            raise ValueError("expected distinct recorded source and query VM IDs")

    def admin(self, role: Role, command: AdminCommand, deadline: float) -> bool | None:
        vm_id = {Role.SOURCE: self.source_vm, Role.QUERY: self.query_vm}.get(role)
        if vm_id is None or command.action is AdminAction.MEASURE:
            raise ValueError("expected a fixed guest administration operation")
        result = invoke_guest_admin(
            vm_id, self.port, self.token, role, command, deadline,
            base_status=self.base_status, package_lock=self.package_lock,
        )
        if result is not None and type(result) is not bool:
            raise OSError("guest administration result was not confirmed")
        return result

    def probe_principal(self, principal: Principal, secret: str, deadline: float) -> None:
        result = self.admin(principal.role, AdminCommand(AdminAction.CHECK_PRINCIPAL, (principal.name, secret)), deadline)
        if result is not None:
            raise OSError("guest principal check was not confirmed")

    def verify_source_tls(self, token: str, secret: str, deadline: float) -> None:
        self._verify_token(token)
        result = self.admin(Role.QUERY, AdminCommand(AdminAction.CHECK_SOURCE_TLS, (secret,)), deadline)
        if result is not None:
            raise OSError("guest source TLS check was not confirmed")

    def measure(self, token: str, reader_secret: str, observer_secret: str, deadline: float) -> MeasurementResult:
        self._verify_token(token)
        return invoke_guest_measurement(
            self.query_vm, self.port, self.token, reader_secret, observer_secret, deadline,
            base_status=self.base_status, package_lock=self.package_lock,
        )

    def close_data_connections(self, role: Role, token: str, login_sids: Mapping[Principal, bytes], deadline: float) -> bool:
        self._verify_token(token)
        fields = tuple(
            field for principal, sid in login_sids.items() if principal.role is role
            for field in (principal.name, sid.hex())
        )
        return self.admin(role, AdminCommand(AdminAction.QUIESCE, fields), deadline) is None

    def _verify_token(self, token: str) -> None:
        if token != self.token:
            raise ValueError("unexpected guest channel run token")


def _send_command(channel: socket, command: AdminCommand, deadline: float) -> bool | MeasurementResult | None:
    payload = json.dumps([command.action.value, *command.fields], separators=(",", ":")).encode("ascii")
    if not 0 < len(payload) <= _MAX_COMMAND:
        raise ValueError("guest administration command exceeds its frame")
    budget_ms = int(_remaining(deadline) * 1000)
    if not 0 < budget_ms <= 0xFFFFFFFF:
        raise TimeoutError("guest administration budget cannot be encoded")
    _send(channel, _COMMAND_HEADER.pack(budget_ms, len(payload)) + payload, deadline)
    reply = _receive(channel, 1, deadline)
    if command.action is AdminAction.DATABASE_EXISTS:
        if reply in (_ABSENT, _PRESENT):
            return reply == _PRESENT
    elif command.action is AdminAction.MEASURE:
        if reply == _MEASUREMENT:
            codes = _receive(channel, 2, deadline)
            (size,) = _SIZE.unpack(_receive(channel, _SIZE.size, deadline))
            if size > _MAX_DRIVER_EVIDENCE:
                raise OSError("guest driver evidence exceeds its frame")
            return _decode_measurement(codes, _receive(channel, size, deadline))
    elif reply == _DONE:
        return None
    raise OSError("guest administration command was not confirmed")


def _decode_measurement(codes: bytes, payload: bytes) -> MeasurementResult:
    state, stage = codes
    if state >= len(_MEASUREMENT_STATES) or stage >= len(_MEASUREMENT_STAGES):
        raise OSError("guest measurement result was not confirmed")
    status, phase = _MEASUREMENT_STATES[state], _MEASUREMENT_STAGES[stage]
    if (
        (status == "PASS" and phase != "comparison") or (payload and status != "PASS")
        or (phase == "driver_unconfirmed" and status != "NOT_PROVEN")
    ):
        raise OSError("guest measurement result was not confirmed")
    driver = None
    if payload:
        try:
            driver = DriverEvidence(**json.loads(payload.decode("ascii")))
        except (TypeError, ValueError, RecursionError):
            raise OSError("guest driver evidence was not confirmed") from None
    filters = PUSHDOWN_FILTER_EVIDENCE if status == "PASS" or phase == "driver_unconfirmed" else None
    return MeasurementResult(status, phase, filters, driver)


def _encode_measurement(result: MeasurementResult) -> bytes:
    codes = bytes((_MEASUREMENT_STATES.index(result.status), _MEASUREMENT_STAGES.index(result.stage)))
    payload = json.dumps(asdict(result.driver), separators=(",", ":")).encode("ascii") if result.driver else b""
    if len(payload) > _MAX_DRIVER_EVIDENCE or _decode_measurement(codes, payload) != result:
        raise ValueError("unexpected guest measurement result")
    return _MEASUREMENT + codes + _SIZE.pack(len(payload)) + payload


def serve_guest_admin(
    port: int, token: str, role: Role, open_admin: Callable[[str, int], Connection], deadline: float, *,
    open_principal: PrincipalConnection | None = None,
    source_driver: OdbcDriver | None = None,
    network: GuestNetwork | None = None,
    work_deadline: float | None = None,
) -> None:
    """Serve sequential parent requests under one bounded guest lifecycle."""
    admin = OdbcPilotAdministration(token, role, open_admin)
    access = GuestSqlAccess(token, role)
    _remaining(deadline)
    with open_parent_listener(port) as (listener, host_cid):
        while monotonic() < deadline:
            try:
                listener.settimeout(_remaining(deadline))
                channel, (peer_cid, _) = listener.accept()
            except TimeoutError:
                return
            with channel:
                if peer_cid != host_cid:
                    continue
                try:
                    input_deadline = min(deadline, monotonic() + 5)
                    _reply_to_probe(channel, token, role, input_deadline)
                    _receive_command(
                        channel, token, role, admin, deadline, access=access, open_principal=open_principal,
                        source_driver=source_driver, network=network, input_deadline=input_deadline, work_deadline=work_deadline,
                    )
                except (OSError, ValueError):
                    # A failed or expired peer cannot reset admission or stop cleanup.
                    continue


def _receive_command(
    channel: socket, token: str, role: Role, admin: OdbcPilotAdministration, deadline: float, *,
    access: GuestSqlAccess,
    open_principal: PrincipalConnection | None = None,
    source_driver: OdbcDriver | None = None,
    network: GuestNetwork | None = None,
    input_deadline: float | None = None,
    work_deadline: float | None = None,
) -> None:
    receive_until = deadline if input_deadline is None else min(deadline, input_deadline)
    try:
        received_at = monotonic()
        budget_ms, size = _COMMAND_HEADER.unpack(_receive(channel, _COMMAND_HEADER.size, receive_until))
        if not budget_ms or not 0 < size <= _MAX_COMMAND:
            raise ValueError("guest administration command exceeds its frame")
        fields = json.loads(_receive(channel, size, receive_until).decode("ascii"))
        if type(fields) is not list or not fields or any(type(field) is not str for field in fields):
            raise ValueError("expected bounded guest command fields")
        command = AdminCommand(AdminAction(fields[0]), tuple(fields[1:]))
        command_deadline = min(deadline, received_at + budget_ms / 1000)
        if work_deadline is not None and command.action not in _CLEANUP_ACTIONS:
            command_deadline = min(command_deadline, work_deadline)
        with access.command(token, role, command.action, command_deadline):
            if command.action is AdminAction.CHECK_PRINCIPAL:
                if open_principal is None or len(command.fields) != 2:
                    raise ValueError("guest principal check is unavailable")
                name, secret = command.fields
                verify_guest_principal(token, _principal(name, role), secret, command_deadline, open_principal)
                reply = _DONE
            elif command.action is AdminAction.CHECK_SOURCE_TLS:
                if role is not Role.QUERY or source_driver is None or network is None or len(command.fields) != 1:
                    raise ValueError("guest source TLS check is unavailable")
                verify_source_tls(source_driver, token, command.fields[0], command_deadline, network=network)
                reply = _DONE
            elif command.action is AdminAction.MEASURE:
                if role is not Role.QUERY or open_principal is None or len(command.fields) != 2:
                    raise ValueError("query guest measurement is unavailable")
                reply = _encode_measurement(
                    run_guest_measurement(token, *command.fields, command_deadline, open_principal, network=network),
                )
            else:
                result = dispatch_admin(admin, token, role, command, command_deadline)
                reply = _PRESENT if result is True else _ABSENT if result is False else _DONE
    except (OSError, ValueError, RecursionError):
        reply = _REJECTED
    _send(channel, reply, deadline)
