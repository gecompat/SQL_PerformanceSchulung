"""Orchestrate the admitted two-guest External Tables pilot."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from secrets import token_bytes, token_hex
from time import monotonic
from typing import ContextManager, Protocol

from external_tables_cleanup import drop_pilot_database_batch, drop_pilot_logins_batch
from external_tables_measurement import MeasurementResult, MeasurementTransport, measure_pushdown
from external_tables_pilot_sql import (
    Role, Route, configure_database_batch, create_database_batch, database_name, external_tables_batch, fixture_batch,
    fixture_read_batch, statistics_batch, verify_fixture,
)
from external_tables_principals import (
    Principal, create_connector_credential_batch, create_principal_batch, principal_probe_batch,
)


WORK_SECONDS = 600
CLEANUP_SECONDS = 120


class GuestPilotTransport(Protocol):
    """Operate only the guest identities recorded for this admitted run."""

    def start_verified_guests(self, token: str, deadline: float) -> None:
        """Record ownership before effects and verify isolation, caps and build.

        Keep the guest adapters detached during locked package installation.
        Verify each exact VM and its live package digest through the current
        identity exchange before executing any SQL. Load the pinned pyodbc
        extension on the query guest before opening its first ODBC connection.
        Check private switch membership on the host and both guest networks
        against the two provisioned IPv4 endpoints.
        """

    def execute(self, role: Role, database: str, sql: str, deadline: float) -> None:
        """Execute one complete admin batch without exposing payloads or retaining secrets."""

    def record_login(self, principal: Principal, sid: bytes, deadline: float) -> None:
        """Record the role and SID in the owned run inventory before CREATE LOGIN."""

    def verify_source_tls(self, token: str, secret: str, deadline: float) -> None:
        """Bind source TLS to both provisioned addresses and reject a wrong certificate identity."""

    def probe_principal(self, principal: Principal, secret: str, sql: str, deadline: float) -> None:
        """Run the rights probe over the actual principal connection and confirm its close."""

    def fixture_rows(self, role: Role, sql: str, deadline: float) -> Iterable[tuple[int, date, int, int]]:
        """Return bounded, complete ordered rows from the exact setup statement."""

    def open_measurement(
        self, token: str, reader_secret: str, observer_secret: str, deadline: float,
    ) -> ContextManager[MeasurementTransport]:
        """Open the verified query-side connections and close them at scope exit."""

    def close_data_connections(self, token: str, deadline: float) -> bool:
        """Prevent new calls and confirm closure of the owned Reader and connector sessions."""

    def database_exists(self, role: Role, name: str, deadline: float) -> bool:
        """Check exact existence on the owned guest; unverified access must raise."""

    def remove_verified_guests(self, token: str, deadline: float) -> bool:
        """Remove only recorded guest, switch, and disk identities and confirm absence."""


@dataclass(frozen=True)
class PilotResult:
    status: str
    stage: str
    filters: tuple[str, str] | None
    sql_cleanup: bool
    guest_cleanup: bool


def run_pilot(transport: GuestPilotTransport, token: str) -> PilotResult:
    databases = {role: database_name(token, role) for role in Role}
    deadline = monotonic() + WORK_SECONDS
    attempted: list[Role] = []
    login_sids: dict[Principal, bytes] = {}
    secrets = {principal: "Ext9!" + token_hex(16) for principal in Principal}
    stage = "guest_preflight"
    measured = MeasurementResult("NOT_PROVEN", stage)
    try:
        transport.start_verified_guests(token, deadline)
        stage = "database_setup"
        for role, database in databases.items():
            _require_time(deadline)
            attempted.append(role)
            transport.execute(role, "master", create_database_batch(token, role), deadline)
            transport.execute(role, database, configure_database_batch(token, role), deadline)
            transport.execute(role, database, fixture_batch(token, role), deadline)
            verify_fixture(transport.fixture_rows(role, fixture_read_batch(token, role), deadline))

        stage = "source_access"
        _setup_principal(transport, token, Principal.SOURCE_READER, secrets, login_sids, deadline)
        transport.verify_source_tls(token, secrets[Principal.SOURCE_READER], deadline)

        stage = "external_setup"
        query_db = databases[Role.QUERY]
        credential = create_connector_credential_batch(
            token, secrets[Principal.SOURCE_READER], "Ext9!" + token_hex(16),
        )
        transport.execute(Role.QUERY, query_db, credential, deadline)
        transport.execute(Role.QUERY, query_db, external_tables_batch(token), deadline)

        stage = "query_access"
        for principal in (Principal.QUERY_READER, Principal.OBSERVER):
            _setup_principal(transport, token, principal, secrets, login_sids, deadline)

        stage = "external_fixture"
        for route in (Route.PUSHDOWN_ON, Route.PUSHDOWN_OFF):
            _require_time(deadline)
            verify_fixture(transport.fixture_rows(Role.QUERY, fixture_read_batch(token, Role.QUERY, route), deadline))

        stage = "statistics"
        transport.execute(Role.QUERY, query_db, statistics_batch(token), deadline)
        stage = "measurement"
        _require_time(deadline)
        with transport.open_measurement(
            token, secrets[Principal.QUERY_READER], secrets[Principal.OBSERVER], deadline,
        ) as connections:
            measured = measure_pushdown(connections, token, deadline)
        _require_time(deadline)
        stage = measured.stage
    except (OSError, ValueError):
        measured = MeasurementResult("NOT_PROVEN", stage)
    finally:
        sql_clean, guests_clean = _cleanup(transport, token, databases, attempted, login_sids)

    if not sql_clean or not guests_clean or measured.status == "FAIL_CLEANUP":
        return PilotResult("FAIL_CLEANUP", stage, None, sql_clean, guests_clean)
    return PilotResult(measured.status, stage, measured.filters, sql_clean, guests_clean)


def _setup_principal(
    transport: GuestPilotTransport, token: str, principal: Principal, secrets: dict[Principal, str],
    login_sids: dict[Principal, bytes], deadline: float,
) -> None:
    _require_time(deadline)
    sid = token_bytes(16)
    transport.record_login(principal, sid, deadline)
    login_sids[principal] = sid
    transport.execute(
        principal.role, database_name(token, principal.role),
        create_principal_batch(token, principal, secrets[principal], sid), deadline,
    )
    transport.probe_principal(principal, secrets[principal], principal_probe_batch(token, principal), deadline)


def _cleanup(
    transport: GuestPilotTransport, token: str, databases: dict[Role, str],
    attempted: list[Role], login_sids: dict[Principal, bytes],
) -> tuple[bool, bool]:
    deadline = monotonic() + CLEANUP_SECONDS
    sql_clean = True
    try:
        if attempted:
            sql_clean = transport.close_data_connections(token, deadline) is True
    except (OSError, ValueError):
        sql_clean = False

    # Queries have to stop using the source before the source is removed.
    for role in reversed(attempted):
        try:
            _require_time(deadline)
            exists = transport.database_exists(role, databases[role], deadline)
            if exists is True:
                transport.execute(role, databases[role], drop_pilot_database_batch(token, role), deadline)
            elif exists is not False:
                raise ValueError("database absence was not confirmed")
            owned_sids = {principal: sid for principal, sid in login_sids.items() if principal.role is role}
            transport.execute(role, "master", drop_pilot_logins_batch(token, role, owned_sids), deadline)
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
