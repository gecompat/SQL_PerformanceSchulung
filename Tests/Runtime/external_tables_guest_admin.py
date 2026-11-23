"""Send fixed SQL administration commands to an identity-verified pilot guest."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from socket import socket
from struct import Struct
from uuid import UUID

from external_tables_cleanup import drop_pilot_database_batch, drop_pilot_logins_batch
from external_tables_guest_identity import (
    _receive, _remaining, _reply_to_probe, _send, accept_parent_connection, connect_verified_guest,
)
from external_tables_odbc import Connection, OdbcPilotAdministration
from external_tables_pilot_sql import (
    Role, Route, configure_database_batch, create_database_batch, database_name, external_tables_batch,
    fixture_batch, fixture_read_batch, statistics_batch, verify_fixture,
)
from external_tables_principals import Principal, create_connector_credential_batch, create_principal_batch


class AdminAction(Enum):
    CREATE_DATABASE = "create_database"
    CONFIGURE_DATABASE = "configure_database"
    CREATE_FIXTURE = "create_fixture"
    VERIFY_FIXTURE = "verify_fixture"
    CREATE_PRINCIPAL = "create_principal"
    CREATE_CREDENTIAL = "create_credential"
    CREATE_EXTERNAL_TABLES = "create_external_tables"
    CREATE_STATISTICS = "create_statistics"
    DATABASE_EXISTS = "database_exists"
    DROP_DATABASE = "drop_database"
    DROP_LOGINS = "drop_logins"


@dataclass(frozen=True)
class AdminCommand:
    action: AdminAction
    fields: tuple[str, ...] = field(default=(), repr=False)


_SIZE = Struct("!H")
_MAX_COMMAND = 1024
_REJECTED, _DONE, _ABSENT, _PRESENT = b"\x00", b"\x01", b"\x02", b"\x03"
_NO_FIELDS = {
    AdminAction.CREATE_DATABASE: create_database_batch,
    AdminAction.CONFIGURE_DATABASE: configure_database_batch,
    AdminAction.CREATE_FIXTURE: fixture_batch,
    AdminAction.CREATE_EXTERNAL_TABLES: external_tables_batch,
    AdminAction.CREATE_STATISTICS: statistics_batch,
    AdminAction.DROP_DATABASE: drop_pilot_database_batch,
}
_QUERY_ONLY = {AdminAction.CREATE_CREDENTIAL, AdminAction.CREATE_EXTERNAL_TABLES, AdminAction.CREATE_STATISTICS}


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
    elif action is AdminAction.DATABASE_EXISTS and not fields:
        return admin.database_exists(db, deadline)
    elif action is AdminAction.DROP_LOGINS and len(fields) in (0, 2, 4):
        principals = {
            _principal(name, role): _sid(sid) for name, sid in zip(fields[::2], fields[1::2], strict=True)
        }
        if len(principals) * 2 != len(fields):
            raise ValueError("duplicate principal in guest cleanup command")
        admin.execute("master", drop_pilot_logins_batch(token, role, principals), deadline)
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
) -> bool | None:
    """Verify this VM and its package inventory on the command connection."""
    with connect_verified_guest(
        vm_id, port, token, role, deadline, base_status=base_status, package_lock=package_lock,
    ) as channel:
        return _send_command(channel, command, deadline)


def _send_command(channel: socket, command: AdminCommand, deadline: float) -> bool | None:
    payload = json.dumps([command.action.value, *command.fields], separators=(",", ":")).encode("ascii")
    if not 0 < len(payload) <= _MAX_COMMAND:
        raise ValueError("guest administration command exceeds its frame")
    _send(channel, _SIZE.pack(len(payload)) + payload, deadline)
    reply = _receive(channel, 1, deadline)
    if command.action is AdminAction.DATABASE_EXISTS:
        if reply in (_ABSENT, _PRESENT):
            return reply == _PRESENT
    elif reply == _DONE:
        return None
    raise OSError("guest administration command was not confirmed")


def serve_guest_admin(
    port: int, token: str, role: Role, open_admin: Callable[[str, int], Connection], deadline: float,
) -> None:
    """Serve one fixed command on a dedicated parent-only VSOCK listener."""
    with accept_parent_connection(port, deadline) as channel:
        _reply_to_probe(channel, token, role, deadline)
        _receive_command(channel, token, role, OdbcPilotAdministration(token, role, open_admin), deadline)


def _receive_command(
    channel: socket, token: str, role: Role, admin: OdbcPilotAdministration, deadline: float,
) -> None:
    try:
        (size,) = _SIZE.unpack(_receive(channel, _SIZE.size, deadline))
        if not 0 < size <= _MAX_COMMAND:
            raise ValueError("guest administration command exceeds its frame")
        fields = json.loads(_receive(channel, size, deadline).decode("ascii"))
        if type(fields) is not list or not fields or any(type(field) is not str for field in fields):
            raise ValueError("expected bounded guest command fields")
        command = AdminCommand(AdminAction(fields[0]), tuple(fields[1:]))
        result = dispatch_admin(admin, token, role, command, deadline)
        reply = _PRESENT if result is True else _ABSENT if result is False else _DONE
    except (OSError, ValueError, RecursionError):
        reply = _REJECTED
    _send(channel, reply, deadline)
