"""ODBC transport for the fixed External Tables measurement on the query guest."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date
from hashlib import file_digest, sha256
from importlib.machinery import EXTENSION_SUFFIXES
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from math import floor, isfinite
import os
from pathlib import Path
import re
from stat import S_ISREG
import sys
from tempfile import NamedTemporaryFile
from threading import Thread
from time import monotonic
from typing import TYPE_CHECKING, Protocol
from zipfile import BadZipFile, ZipFile

from external_tables_measurement import (
    AggregateRows, MeasurementResult, PendingAggregate, UnconfirmedRequestCleanup, measure_pushdown,
)
from external_tables_pilot_sql import (
    CONNECTION_OPTIONS, EDITION, ROWS, SOURCE_PORT, VERSION, Role, Route, aggregate_batch,
    database_name, fixture_read_batch, source_host,
)
from external_tables_principals import PASSWORD, Principal, principal_name, principal_probe_batch
from external_tables_pushdown_evidence import Work


if TYPE_CHECKING:
    from external_tables_guest_network import GuestNetwork


REQUEST_IDENTITY = "SET NOCOUNT ON; SELECT @@SPID AS session_id, CURRENT_REQUEST_ID() AS request_id;\n"


class Cursor(Protocol):
    description: object | None

    def execute(self, sql: str) -> object: ...
    def fetchmany(self, size: int) -> Iterable[Iterable[object]]: ...
    def nextset(self) -> bool | None: ...
    def close(self) -> None: ...


class Connection(Protocol):
    timeout: int

    def cursor(self) -> Cursor: ...
    def close(self) -> None: ...


PrincipalConnection = Callable[[Principal, str, int], Connection]


class OdbcDriver(Protocol):
    Error: type[Exception]
    pooling: bool

    def connect(self, connection_string: str, *, timeout: int, autocommit: bool) -> Connection: ...


def _extension_spec(wheel_entry: dict) -> tuple[str, int, str]:
    try:
        extension = wheel_entry["installed_extension"]
        filename, size, digest = extension["filename"], extension["size"], extension["sha256"]
    except (KeyError, TypeError):
        raise ValueError("invalid pyodbc extension lock") from None
    if (
        filename != "pyodbc.cpython-312-x86_64-linux-gnu.so"
        or type(size) is not int or not 0 < size <= 4 * 1024 * 1024
        or not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None
    ):
        raise ValueError("invalid pyodbc extension lock")
    return filename, size, digest


def read_pinned_pyodbc_wheel(wheel: Path, wheel_entry: dict) -> bytes:
    """Read only the verified extension from one hash-bound wheel snapshot."""
    filename, size, digest = _extension_spec(wheel_entry)
    wheel_size = wheel_entry.get("size")
    if wheel.name != wheel_entry.get("filename") or type(wheel_size) is not int or not 0 < wheel_size <= 4 * 1024 * 1024:
        raise ValueError("Python wheel differs from the guest role lock")
    with wheel.open("rb") as stream:
        archive = stream.read(wheel_size + 1)
    if len(archive) != wheel_size or sha256(archive).hexdigest() != wheel_entry.get("sha256"):
        raise ValueError("Python wheel differs from the guest role lock")
    try:
        with ZipFile(BytesIO(archive)) as package:
            entries = [member for member in package.infolist() if member.filename.endswith(".so")]
            if len(entries) != 1 or entries[0].filename != filename or entries[0].file_size != size:
                raise ValueError("Python wheel extension differs from the guest role lock")
            with package.open(entries[0]) as binary:
                payload = binary.read(size + 1)
    except BadZipFile:
        raise ValueError("Python wheel is not a valid archive") from None
    if len(payload) != size or sha256(payload).hexdigest() != digest:
        raise ValueError("Python wheel extension differs from the guest role lock")
    return payload


def stage_pinned_pyodbc(install_dir: Path, wheel_entry: dict, payload: bytes) -> None:
    """Install into the owned private directory without replacing existing files."""
    filename, size, digest = _extension_spec(wheel_entry)
    if len(payload) != size or sha256(payload).hexdigest() != digest:
        raise ValueError("Python wheel extension differs from the guest role lock")
    directory = install_dir.resolve(strict=True)
    destination = directory / filename
    with NamedTemporaryFile(dir=directory, prefix=".pyodbc-", delete=False) as staging:
        temporary = Path(staging.name)
        try:
            staging.write(payload)
            staging.close()
            try:
                os.link(temporary, destination)
            except FileExistsError:
                _verify_native_extension(destination, size, digest)
        finally:
            staging.close()
            temporary.unlink()


def _verify_native_extension(path: Path, size: int, digest: str) -> None:
    metadata = path.lstat()
    if not S_ISREG(metadata.st_mode) or metadata.st_size != size:
        raise ValueError("installed pyodbc extension differs from the wheel lock")
    with path.open("rb") as binary:
        if file_digest(binary, "sha256").hexdigest() != digest:
            raise ValueError("installed pyodbc extension differs from the wheel lock")


def load_pinned_pyodbc(install_dir: Path, wheel_entry: dict) -> OdbcDriver:
    """Load the verified native file from a guest's private install directory."""
    filename, size, digest = _extension_spec(wheel_entry)
    version = wheel_entry.get("version")
    if not isinstance(version, str) or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None:
        raise ValueError("invalid pyodbc extension lock")
    if (
        sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12)
        or sys.platform != "linux" or os.uname().machine != "x86_64"
        or filename.removeprefix("pyodbc") not in EXTENSION_SUFFIXES
    ):
        raise ValueError("the pyodbc wheel requires Linux x86_64 CPython 3.12")
    if "pyodbc" in sys.modules:
        raise ValueError("the query process must verify pyodbc before loading any driver")

    path = install_dir.resolve(strict=True) / filename
    _verify_native_extension(path, size, digest)

    spec = spec_from_file_location("pyodbc", path)
    if spec is None or spec.loader is None:
        raise ValueError("pinned pyodbc extension has no native loader")
    try:
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
    except ImportError:
        raise OSError("could not load the verified pyodbc extension and its native dependencies") from None
    if getattr(module, "version", None) != version or getattr(module, "__file__", None) != str(path):
        raise ValueError("loaded pyodbc identity differs from the wheel lock")
    module.pooling = False
    sys.modules["pyodbc"] = module
    return module


def verify_source_tls(
    driver: OdbcDriver, token: str, secret: str, deadline: float, *, network: GuestNetwork,
) -> None:
    """Check from the query guest with pooling disabled before the first driver connection."""
    host = source_host(token)
    database = database_name(token, Role.SOURCE)
    login = principal_name(token, Principal.SOURCE_READER)
    if not PASSWORD.fullmatch(secret) or driver.pooling is not False:
        raise ValueError("TLS probe requires the run-bound secret and disabled pooling")

    settings = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Database={database};UID={login};PWD={secret};{CONNECTION_OPTIONS}"
        "MARS_Connection=No;ConnectRetryCount=0;"
    )
    try:
        connection = driver.connect(
            f"Server=tcp:{host},{SOURCE_PORT};" + settings,
            timeout=_query_timeout(deadline),
            autocommit=True,
        )
        try:
            connection.timeout = _query_timeout(deadline)
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SET NOCOUNT ON; SELECT DB_NAME(), ORIGINAL_LOGIN(), "
                    "CONVERT(varchar(48), CONNECTIONPROPERTY('local_net_address')), "
                    "CONVERT(int, CONNECTIONPROPERTY('local_tcp_port')), "
                    "CONVERT(varchar(48), CONNECTIONPROPERTY('client_net_address'));"
                )
                (identity,) = _fetch(cursor, 1, 5)
                actual_database, actual_login, address, port, client_address = identity
                if (
                    actual_database != database or actual_login != login
                    or address != str(network.source.ip) or client_address != str(network.query.ip)
                    or type(port) is not int or port != SOURCE_PORT
                    or cursor.nextset()
                ):
                    raise ValueError("TLS endpoint did not return the expected database, login and TCP identity")
            finally:
                cursor.close()
        finally:
            connection.close()
    except Exception:
        raise OSError("trusted source TLS connection was not confirmed") from None

    # The Linux driver can also accept the name in Server. Use the verified
    # numeric endpoint so neither Server nor HostnameInCertificate matches.
    wrong_name = f"pbn-{token.lower()}"
    try:
        rejected = driver.connect(
            f"Server=tcp:{network.source.ip},{SOURCE_PORT};" + settings + f"HostnameInCertificate={wrong_name};",
            timeout=_query_timeout(deadline),
            autocommit=True,
        )
    except driver.Error as failure:
        if not _is_certificate_name_rejection(failure):
            raise OSError("source TLS rejection could not be attributed to the certificate name") from None
    except Exception:
        raise OSError("source TLS negative control did not complete") from None
    else:
        try:
            rejected.close()
        except Exception:
            raise OSError("source TLS negative control connection closure was not confirmed") from None
        raise ValueError("source TLS connection accepted the wrong certificate name")
    _remaining(deadline)


def _is_certificate_name_rejection(failure: Exception) -> bool:
    if len(failure.args) != 2 or failure.args[0] != "08001" or type(failure.args[1]) is not str:
        return False
    message = failure.args[1].lower()
    return "ssl provider:" in message and "subject name does not match host name" in message


class OdbcPilotAdministration:
    """Execute trusted pilot SQL inside a host-verified guest.

    The factory opens a fresh autocommit admin connection on this guest's
    TCP loopback, with pooling disabled. Guest identity and process deadlines
    are owned by the enclosing guest transport.
    """

    def __init__(self, token: str, role: Role, open_admin: Callable[[str, int], Connection]) -> None:
        self._database = database_name(token, role)
        self._admin = open_admin
        routes = (Route.LOCAL,) if role is Role.SOURCE else tuple(Route)
        self._fixture_reads = {fixture_read_batch(token, role, route) for route in routes}

    def execute(self, database: str, sql: str, deadline: float) -> None:
        """Execute the coordinator's setup or cleanup batch with no result rows."""
        if database not in ("master", self._database):
            raise ValueError("unexpected database for guest administration")
        with self._cursor(database, deadline) as cursor:
            cursor.execute(self._guard(database) + sql)
            _consume_status_results(cursor, deadline)

    def fixture_rows(self, sql: str, deadline: float) -> tuple[tuple[int, date, int, int], ...]:
        if sql not in self._fixture_reads:
            raise ValueError("unexpected fixture query for this guest")
        with self._cursor(self._database, deadline) as cursor:
            cursor.execute(self._guard(self._database) + sql)
            rows = _fetch(cursor, ROWS, 4)
            if len(rows) != ROWS or cursor.nextset():
                raise ValueError("incomplete or ambiguous guest fixture")
        return rows

    def database_exists(self, name: str, deadline: float) -> bool:
        if name != self._database:
            raise ValueError("unexpected cleanup database for this guest")
        with self._cursor("master", deadline) as cursor:
            cursor.execute(
                self._guard("master") +
                f"SELECT CONVERT(int, CASE WHEN DB_ID(N'{name}') IS NULL THEN 0 ELSE 1 END);"
            )
            rows = _fetch(cursor, 1, 1)
            if len(rows) != 1 or type(rows[0][0]) is not int or rows[0][0] not in (0, 1) or cursor.nextset():
                raise ValueError("guest database existence was not confirmed")
        return rows[0][0] == 1

    @contextmanager
    def _cursor(self, database: str, deadline: float) -> Iterator[Cursor]:
        try:
            connection = self._admin(database, _query_timeout(deadline))
            try:
                connection.timeout = _query_timeout(deadline)
                cursor = connection.cursor()
                try:
                    yield cursor
                finally:
                    cursor.close()
            finally:
                connection.close()
        except Exception:
            raise OSError("guest administration could not be confirmed") from None
        _remaining(deadline)

    @staticmethod
    def _guard(database: str) -> str:
        return f"""SET NOCOUNT ON;
IF DB_NAME() COLLATE Latin1_General_100_BIN2 <> N'{database}'
    OR DATALENGTH(DB_NAME()) <> DATALENGTH(N'{database}')
    OR @@TRANCOUNT <> 0 OR (@@OPTIONS & 2) <> 0
    OR COALESCE(IS_SRVROLEMEMBER(N'sysadmin'), 0) <> 1
    OR COALESCE(CONVERT(varchar(48), CONNECTIONPROPERTY('local_net_address')), '') <> '127.0.0.1'
    OR COALESCE(CONVERT(varchar(48), CONNECTIONPROPERTY('client_net_address')), '') <> '127.0.0.1'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'ProductVersion')), N'') <> N'{VERSION}'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'Edition')), N'') <> N'{EDITION}'
    THROW 51083, 'FAIL_CONTRACT: unexpected local guest administration session.', 1;
"""


def run_guest_measurement(
    token: str, reader_secret: str, observer_secret: str, deadline: float, open_principal: PrincipalConnection,
) -> MeasurementResult:
    """Run measurements and observation locally, returning only the normalized result."""
    if not all(PASSWORD.fullmatch(secret) for secret in (reader_secret, observer_secret)) or reader_secret == observer_secret:
        raise ValueError("measurement requires distinct generated principal secrets")
    try:
        observer = _open_verified_principal(token, Principal.OBSERVER, observer_secret, deadline, open_principal)
        try:
            def reader(_: int) -> Connection:
                return _open_verified_principal(
                    token, Principal.QUERY_READER, reader_secret, deadline, open_principal,
                )

            result = measure_pushdown(OdbcMeasurementTransport(token, reader, observer), token, deadline)
        finally:
            _close_principal_resource(observer)
    except UnconfirmedRequestCleanup:
        return MeasurementResult("FAIL_CLEANUP", "query_connection")
    except (OSError, ValueError):
        return MeasurementResult("NOT_PROVEN", "query_connection")
    return result


def verify_guest_principal(
    token: str, principal: Principal, secret: str, deadline: float, open_principal: PrincipalConnection,
) -> None:
    """Verify rights on an actual dedicated local connection and confirm its closure."""
    if not PASSWORD.fullmatch(secret):
        raise ValueError("expected a generated guest principal secret")
    connection = _open_verified_principal(token, principal, secret, deadline, open_principal)
    _close_principal_resource(connection)
    _remaining(deadline)


def _open_verified_principal(
    token: str, principal: Principal, secret: str, deadline: float, open_principal: PrincipalConnection,
) -> Connection:
    probe = principal_probe_batch(token, principal)
    try:
        connection = open_principal(principal, secret, _query_timeout(deadline))
    except Exception:
        raise OSError("local guest principal connection failed") from None
    try:
        connection.timeout = _query_timeout(deadline)
        cursor = connection.cursor()
        try:
            cursor.execute("""
IF COALESCE(CONVERT(varchar(48), CONNECTIONPROPERTY('local_net_address')), '') <> '127.0.0.1'
    OR COALESCE(CONVERT(varchar(48), CONNECTIONPROPERTY('client_net_address')), '') <> '127.0.0.1'
    THROW 51084, 'FAIL_CONTRACT: expected a local guest principal connection.', 1;
""" + probe)
            _consume_status_results(cursor, deadline)
        finally:
            _close_principal_resource(cursor)
    except Exception as error:
        _close_principal_resource(connection)
        if isinstance(error, UnconfirmedRequestCleanup):
            raise
        raise OSError("local guest principal was not verified") from None
    return connection


def _close_principal_resource(resource: Cursor | Connection) -> None:
    try:
        resource.close()
    except Exception:
        raise UnconfirmedRequestCleanup("guest principal resource closure was not confirmed") from None


@dataclass
class _Aggregate:
    session_id: int
    request_id: int
    _rows: Future[AggregateRows] = field(repr=False)

    def finished(self) -> bool:
        return self._rows.done()

    def result(self, deadline: float) -> AggregateRows:
        return self._rows.result(timeout=_remaining(deadline))


class OdbcMeasurementTransport:
    """Run owned queries via preflight-bound local ODBC connections.

    The Reader factory must open a fresh dedicated connection with pooling and
    MARS disabled, login timeout supplied in seconds, and credentials held in
    memory. The distinct observer is opened and closed by the guest pilot.
    """

    def __init__(self, token: str, open_reader: Callable[[int], Connection], observer: Connection) -> None:
        self._reader = open_reader
        self._observer = observer
        self._unused = {aggregate_batch(token, route) for route in Route}

    @contextmanager
    def aggregate(self, sql: str, deadline: float) -> Iterator[PendingAggregate]:
        if sql not in self._unused:
            raise ValueError("expected an unused fixed aggregate in this pilot")
        _remaining(deadline)
        self._unused.remove(sql)
        identity: Future[tuple[int, int]] = Future()
        rows: Future[AggregateRows] = Future()
        worker = Thread(target=self._execute_reader, args=(sql, deadline, identity, rows), daemon=True)
        worker.start()
        try:
            session_id, request_id = identity.result(timeout=_remaining(deadline))
            yield _Aggregate(session_id, request_id, rows)
        finally:
            # On a failed observation, the driver timeout bounds the same
            # request. The outer pilot handles recovery if it still owns work.
            worker.join(timeout=max(0.0, deadline - monotonic()))
            if worker.is_alive() or not rows.done() or isinstance(rows.exception(), UnconfirmedRequestCleanup):
                raise UnconfirmedRequestCleanup("Reader connection closure was not confirmed")

    def _execute_reader(
        self, sql: str, deadline: float, identity: Future[tuple[int, int]], result: Future[AggregateRows],
    ) -> None:
        connection = None
        cursor = None
        try:
            connection = self._reader(_query_timeout(deadline))
            connection.timeout = _query_timeout(deadline)
            cursor = connection.cursor()
            cursor.execute(REQUEST_IDENTITY)
            (request,) = _fetch(cursor, 1, 2)
            session_id, request_id = request
            if (
                type(session_id) is not int or not 1 <= session_id <= 32767
                or type(request_id) is not int or request_id != 0 or cursor.nextset()
            ):
                raise ValueError("invalid SQL session identity for a dedicated request")
            identity_cursor, cursor = cursor, None
            try:
                identity_cursor.close()
            except Exception:
                raise UnconfirmedRequestCleanup("Reader identity cursor closure was not confirmed") from None
            identity.set_result((session_id, request_id))

            # pyodbc applies SQL_ATTR_QUERY_TIMEOUT when it allocates a cursor.
            connection.timeout = _query_timeout(deadline)
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = _fetch(cursor, 4, 3)
            if any(type(value) is not int for row in rows for value in row) or cursor.nextset():
                raise ValueError("invalid aggregate response")
        except UnconfirmedRequestCleanup as exc:
            failure = exc
        except Exception:
            failure = OSError("Reader request failed")
        else:
            failure = None
        finally:
            try:
                if cursor is not None:
                    cursor.close()
            except Exception:
                failure = UnconfirmedRequestCleanup("Reader cursor closure was not confirmed")
            finally:
                try:
                    if connection is not None:
                        connection.close()
                except Exception:
                    failure = UnconfirmedRequestCleanup("Reader connection closure was not confirmed")
            if failure is not None:
                if not identity.done():
                    identity.set_exception(failure)
                result.set_exception(failure)
            else:
                result.set_result(rows)

    def active_handles(self, sql: str, deadline: float) -> tuple[str, ...]:
        records = self._read_observer(sql, deadline, max_rows=2, columns=1)
        if any(type(row[0]) is not str for row in records):
            raise ValueError("invalid SQL handle result")
        return tuple(row[0] for row in records)

    def external_work(self, sql: str, deadline: float) -> tuple[Work, ...]:
        records = self._read_observer(sql, deadline, max_rows=5, columns=5)
        rows = []
        for execution_id, request_status, work_status, input_name, read_command in records:
            if any(type(value) is not str for value in (execution_id, request_status, work_status, input_name)):
                raise ValueError("incomplete distributed work row")
            if read_command is not None and type(read_command) is not str:
                raise ValueError("invalid remote command result")
            rows.append(Work(execution_id, input_name, read_command, request_status, work_status))
        return tuple(rows)

    def _read_observer(self, sql: str, deadline: float, max_rows: int, columns: int) -> tuple[tuple, ...]:
        try:
            self._observer.timeout = _query_timeout(deadline)
            cursor = self._observer.cursor()
            try:
                cursor.execute(sql)
                rows = _fetch(cursor, max_rows, columns)
                if cursor.nextset():
                    raise ValueError("unexpected observer result set")
            finally:
                cursor.close()
        except Exception:
            raise OSError("observer request failed") from None
        _remaining(deadline)
        return rows


def _consume_status_results(cursor: Cursor, deadline: float) -> None:
    # SQL Server can emit non-row results for context changes. Consume all of
    # them to detect late errors, while bounding the result chain.
    for _ in range(32):
        _remaining(deadline)
        if cursor.description is not None:
            raise ValueError("unexpected row results")
        if not cursor.nextset():
            return
    raise ValueError("too many status results")


def _fetch(cursor: Cursor, limit: int, columns: int) -> tuple[tuple, ...]:
    rows = tuple(tuple(row) for row in cursor.fetchmany(limit + 1))
    if len(rows) > limit or any(len(row) != columns for row in rows):
        raise ValueError("unexpected ODBC result shape")
    return rows


def _remaining(deadline: float) -> float:
    seconds = deadline - monotonic()
    if not isfinite(seconds) or seconds <= 0:
        raise TimeoutError("measurement deadline exceeded")
    return seconds


def _query_timeout(deadline: float) -> int:
    seconds = floor(_remaining(deadline))
    if seconds < 1:
        raise TimeoutError("insufficient time for an ODBC request")
    return seconds
