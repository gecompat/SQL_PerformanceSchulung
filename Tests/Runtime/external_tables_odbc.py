"""ODBC transport for the fixed External Tables measurement on the query guest."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass, field
from math import floor, isfinite
from threading import Thread
from time import monotonic
from typing import Protocol

from external_tables_measurement import AggregateRows, PendingAggregate, UnconfirmedRequestCleanup
from external_tables_pilot_sql import Route, aggregate_batch
from external_tables_pushdown_evidence import Work


REQUEST_IDENTITY = "SET NOCOUNT ON; SELECT @@SPID AS session_id, CURRENT_REQUEST_ID() AS request_id;\n"


class Cursor(Protocol):
    def execute(self, sql: str) -> object: ...
    def fetchmany(self, size: int) -> Iterable[Iterable[object]]: ...
    def nextset(self) -> bool | None: ...
    def close(self) -> None: ...


class Connection(Protocol):
    timeout: int

    def cursor(self) -> Cursor: ...
    def close(self) -> None: ...


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
