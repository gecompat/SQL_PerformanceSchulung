"""Orchestrate the admitted two-guest External Tables pilot."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from secrets import token_bytes, token_hex
from time import monotonic
from typing import Protocol

from external_tables_guest_admin import AdminAction, AdminCommand
from external_tables_driver_evidence import DriverEvidence
from external_tables_measurement import MeasurementResult
from external_tables_pilot_sql import Role, Route, database_name
from external_tables_principals import Principal


WORK_SECONDS = 600
CLEANUP_SECONDS = 120


class GuestPilotTransport(Protocol):
    """Operate only the guest identities recorded for this admitted run."""

    def start_verified_guests(self, token: str, deadline: float) -> None:
        """Record ownership before effects and verify isolation, caps and build.

        Use Test-ExternalTablesHyperVResources.ps1 against both recorded VM
        and disk identities before SQL. Keep the guest adapters detached during
        locked package installation.
        Verify each exact VM and its live package digest through the current
        identity exchange before executing any SQL. Load the pinned pyodbc
        extension on each guest before opening its first ODBC connection.
        Check private switch membership on the host and both guest networks
        against the two provisioned IPv4 endpoints. Install the source ingress
        policy before attachment and verify the live rules before source access.
        Keep the source leaf key in its guest and transfer only the public CA
        certificate to the query guest.
        """

    def admin(self, role: Role, command: AdminCommand, deadline: float) -> bool | None:
        """Dispatch one fixed operation on the identity-bound guest connection."""

    def record_login(self, principal: Principal, sid: bytes, deadline: float) -> None:
        """Record the role and SID in the owned run inventory before CREATE LOGIN."""

    def verify_source_tls(self, token: str, secret: str, deadline: float) -> None:
        """Bind source TLS to both provisioned addresses and reject a wrong certificate identity."""

    def probe_principal(self, principal: Principal, secret: str, deadline: float) -> None:
        """Run the rights probe over the actual principal connection and confirm its close."""

    def measure(self, token: str, reader_secret: str, observer_secret: str, deadline: float) -> MeasurementResult:
        """Return the normalized result of the query guest's local measurement."""

    def close_data_connections(self, token: str, login_sids: Mapping[Principal, bytes], deadline: float) -> bool:
        """Prevent new calls and confirm closure of the owned Reader and connector sessions."""

    def remove_verified_guests(self, token: str, deadline: float) -> bool:
        """Remove only recorded guest, switch, and disk identities and confirm absence.

        Run Test-ExternalTablesHyperVAbsence.ps1 with the original inventory
        before releasing the run directory. Its PASS is required for guest
        cleanup, independently of SQL cleanup.
        """


@dataclass(frozen=True)
class PilotResult:
    status: str
    stage: str
    filters: tuple[str, str] | None
    sql_cleanup: bool
    guest_cleanup: bool
    driver: DriverEvidence | None = None


def run_pilot(transport: GuestPilotTransport, token: str) -> PilotResult:
    database_name(token, Role.QUERY)
    deadline = monotonic() + WORK_SECONDS
    attempted: list[Role] = []
    login_sids: dict[Principal, bytes] = {}
    secrets = {principal: "Ext9!" + token_hex(16) for principal in Principal}
    stage = "guest_preflight"
    measured = MeasurementResult("NOT_PROVEN", stage)
    try:
        transport.start_verified_guests(token, deadline)
        stage = "database_setup"
        for role in Role:
            _require_time(deadline)
            attempted.append(role)
            _admin(transport, role, AdminAction.CREATE_DATABASE, deadline)
            _admin(transport, role, AdminAction.CONFIGURE_DATABASE, deadline)
            _admin(transport, role, AdminAction.CREATE_FIXTURE, deadline)
            _admin(transport, role, AdminAction.VERIFY_FIXTURE, deadline, Route.LOCAL.name)

        stage = "source_access"
        _setup_principal(transport, token, Principal.SOURCE_READER, secrets, login_sids, deadline)
        transport.verify_source_tls(token, secrets[Principal.SOURCE_READER], deadline)

        stage = "external_setup"
        _admin(transport, Role.QUERY, AdminAction.CREATE_CREDENTIAL, deadline,
               secrets[Principal.SOURCE_READER], "Ext9!" + token_hex(16))
        _admin(transport, Role.QUERY, AdminAction.CREATE_EXTERNAL_TABLES, deadline)

        stage = "query_access"
        for principal in (Principal.QUERY_READER, Principal.OBSERVER):
            _setup_principal(transport, token, principal, secrets, login_sids, deadline)

        stage = "external_fixture"
        for route in (Route.PUSHDOWN_ON, Route.PUSHDOWN_OFF):
            _require_time(deadline)
            _admin(transport, Role.QUERY, AdminAction.VERIFY_FIXTURE, deadline, route.name)

        stage = "statistics"
        _admin(transport, Role.QUERY, AdminAction.CREATE_STATISTICS, deadline)
        stage = "measurement"
        _require_time(deadline)
        measured = transport.measure(token, secrets[Principal.QUERY_READER], secrets[Principal.OBSERVER], deadline)
        if measured.status != "FAIL_CLEANUP":
            _require_time(deadline)
        stage = measured.stage
    except (OSError, ValueError):
        measured = MeasurementResult("NOT_PROVEN", stage)
    finally:
        sql_clean, guests_clean = _cleanup(transport, token, attempted, login_sids)

    if not sql_clean or not guests_clean or measured.status == "FAIL_CLEANUP":
        return PilotResult("FAIL_CLEANUP", stage, None, sql_clean, guests_clean)
    return PilotResult(measured.status, stage, measured.filters, sql_clean, guests_clean, measured.driver)


def _admin(
    transport: GuestPilotTransport, role: Role, action: AdminAction, deadline: float, *fields: str,
) -> None:
    if transport.admin(role, AdminCommand(action, fields), deadline) is not None:
        raise ValueError("guest returned an unexpected administration result")


def _setup_principal(
    transport: GuestPilotTransport, token: str, principal: Principal, secrets: dict[Principal, str],
    login_sids: dict[Principal, bytes], deadline: float,
) -> None:
    _require_time(deadline)
    sid = token_bytes(16)
    transport.record_login(principal, sid, deadline)
    login_sids[principal] = sid
    _admin(transport, principal.role, AdminAction.CREATE_PRINCIPAL, deadline,
           principal.name, secrets[principal], sid.hex())
    transport.probe_principal(principal, secrets[principal], deadline)


def _cleanup(
    transport: GuestPilotTransport, token: str,
    attempted: list[Role], login_sids: dict[Principal, bytes],
) -> tuple[bool, bool]:
    deadline = monotonic() + CLEANUP_SECONDS
    sql_clean = True
    try:
        if attempted:
            sql_clean = transport.close_data_connections(token, login_sids, deadline) is True
    except (OSError, ValueError):
        sql_clean = False

    # The SQL batches check current sessions, but only the transport can
    # confirm that the reader and connector can no longer start requests.
    roles = reversed(attempted) if sql_clean else ()
    for role in roles:
        try:
            _require_time(deadline)
            exists = transport.admin(role, AdminCommand(AdminAction.DATABASE_EXISTS), deadline)
            if exists is True:
                _admin(transport, role, AdminAction.DROP_DATABASE, deadline)
            elif exists is not False:
                raise ValueError("database absence was not confirmed")
            sid_fields = tuple(
                field for principal, sid in login_sids.items() if principal.role is role
                for field in (principal.name, sid.hex())
            )
            _admin(transport, role, AdminAction.DROP_LOGINS, deadline, *sid_fields)
        except (OSError, ValueError):
            sql_clean = False

    try:
        guests_clean = transport.remove_verified_guests(token, deadline) is True
        _require_time(deadline)
    except (OSError, ValueError):
        guests_clean = False
    return sql_clean, guests_clean


def _require_time(deadline: float) -> None:
    if monotonic() >= deadline:
        raise TimeoutError("External Tables pilot deadline exceeded")
