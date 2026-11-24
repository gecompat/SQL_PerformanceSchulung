"""Request and remote-command evidence for the External Tables pushdown pilot."""
from __future__ import annotations

from dataclasses import dataclass, field
import re

from external_tables_pilot_sql import Role, Route, database_guard, database_name, measurement_marker


HANDLE = re.compile(r"[0-9A-Fa-f]{2,128}", re.ASCII)
IDENTIFIER = r'(?:\[[a-zA-Z_][a-zA-Z_0-9]*\]|"[a-zA-Z_][a-zA-Z_0-9]*"|[a-zA-Z_][a-zA-Z_0-9]*)'
COLUMN = rf"(?:(?P<qualifier>{IDENTIFIER})\s*\.\s*)?(?P<column>{IDENTIFIER})"
COMPARISON = re.compile(rf"{COLUMN}\s*(>=|<)\s*(.+)", re.ASCII | re.IGNORECASE)


@dataclass(frozen=True)
class Work:
    execution_id: str
    input_name: str
    read_command: str | None = field(repr=False)
    request_status: str
    work_status: str


def active_request_batch(token: str, route: Route, session_id: int, request_id: int) -> str:
    marker = measurement_marker(token, route)
    if route is Route.LOCAL or type(session_id) is not int or not 1 <= session_id <= 32767:
        raise ValueError("expected a bound external measurement session")
    if type(request_id) is not int or not 0 <= request_id <= 2**31 - 1:
        raise ValueError("expected a bound SQL request")
    return database_guard(token, Role.QUERY) + f"""
SELECT CONVERT(varchar(128), req.sql_handle, 2) AS sql_handle
FROM sys.dm_exec_requests AS req
CROSS APPLY sys.dm_exec_sql_text(req.sql_handle) AS batch
WHERE req.session_id = {session_id} AND req.request_id = {request_id} AND req.database_id = DB_ID()
    AND req.sql_handle IS NOT NULL
    AND CHARINDEX(N'/* {marker} */',
        SUBSTRING(batch.text, req.statement_start_offset / 2 + 1,
            CASE WHEN req.statement_end_offset = -1 THEN DATALENGTH(batch.text) / 2
                 ELSE (req.statement_end_offset - req.statement_start_offset) / 2 + 1 END)
            COLLATE Latin1_General_100_BIN2) > 0;
"""


def external_work_batch(token: str, sql_handle: str) -> str:
    if not HANDLE.fullmatch(sql_handle) or len(sql_handle) % 2:
        raise ValueError("expected a hexadecimal handle from the active request")
    return database_guard(token, Role.QUERY) + f"""
SELECT TOP (5) dr.execution_id, dr.status AS request_status, w.status AS work_status,
    w.input_name, w.read_command
FROM sys.dm_exec_distributed_requests AS dr
LEFT JOIN sys.dm_exec_external_work AS w ON w.execution_id = dr.execution_id
WHERE dr.sql_handle = 0x{sql_handle}
ORDER BY dr.execution_id, w.step_index, w.compute_node_id, w.work_id;
"""


PUSHDOWN_FILTER_EVIDENCE = ("REMOTE_DATE_FILTER", "NO_REMOTE_FILTER")


def verify_pushdown(
    token: str, on_records: tuple[Work, ...], off_records: tuple[Work, ...],
) -> tuple[str, str]:
    """The caller must bind each recordset to its own witnessed active request."""
    source = database_name(token, Role.SOURCE)
    location = f"sqlserver://pbs-{token.lower()}:1433/{source}.dbo.Facts"
    on = _single_work(on_records, location)
    off = _single_work(off_records, location)
    if on.execution_id == off.execution_id:
        raise ValueError("pushdown arms share a distributed execution")
    if not _is_filtered(on.read_command, source) or _is_filtered(off.read_command, source):
        raise ValueError("remote filter differs from the expected ON/OFF comparison")
    return PUSHDOWN_FILTER_EVIDENCE


def _single_work(records: tuple[Work, ...], source: str) -> Work:
    if len(records) != 1:
        raise ValueError("expected one complete distributed work row per arm")
    record = records[0]
    if (
        not record.execution_id or len(record.execution_id) > 32
        or record.input_name != source
        or record.request_status not in {"Complete", "Completed"} or record.work_status != "Done"
        or record.read_command is None
    ):
        raise ValueError("external work was incomplete or could not be bound to the source")
    return record


def _unquote(identifier: str) -> str:
    return identifier.strip('[]"').lower()


def _is_filtered(command: str | None, database: str) -> bool:
    # Keep the grammar deliberately small. Other remote SQL shapes need a new source-bound rule.
    if command is None or not command or len(command.encode("utf-16-le")) >= 8000:
        raise ValueError("missing or potentially truncated remote command")
    shape = re.compile(
        rf"SELECT\s+(?P<projection>[^;]+?)\s+FROM\s+"
        rf"(?P<database>{IDENTIFIER})\s*\.\s*(?P<schema>{IDENTIFIER})\s*\.\s*(?P<table>{IDENTIFIER})"
        rf"(?:\s+(?:AS\s+)?(?P<alias>(?!WHERE\b){IDENTIFIER}))?"
        r"(?:\s+WHERE\s+(?P<predicate>.+))?\s*;?",
        re.ASCII | re.IGNORECASE | re.DOTALL,
    )
    match = shape.fullmatch(command.strip().removesuffix(";").rstrip())
    if match is None or tuple(_unquote(match[key]) for key in ("database", "schema", "table")) != (
        database.lower(), "dbo", "facts",
    ):
        raise ValueError("remote command does not select the exact pilot source")
    alias = _unquote(match["alias"]) if match["alias"] else "facts"
    projection = match["projection"].strip()
    if projection != "*":
        for item in projection.split(","):
            field = re.fullmatch(COLUMN, item.strip(), re.ASCII | re.IGNORECASE)
            if not _matches_field(field, alias, {"factid", "eventdate", "categoryid", "amount"}):
                raise ValueError("unexpected remote projection")
    if match["predicate"] is None:
        return False
    terms = re.split(r"\bAND\b", _without_outer_parens(match["predicate"]), flags=re.ASCII | re.IGNORECASE)
    if len(terms) != 2:
        raise ValueError("remote date predicate has an unexpected shape")
    bounds = set()
    for term in terms:
        bound = COMPARISON.fullmatch(_without_outer_parens(term))
        if not _matches_field(bound, alias, {"eventdate"}):
            raise ValueError("remote predicate is not a direct date comparison")
        date_literal = _without_outer_parens(bound[4])
        literal = re.fullmatch(r"(?:'([0-9]{8}|[0-9]{4}-[0-9]{2}-[0-9]{2})'|\{d\s+'([0-9]{4}-[0-9]{2}-[0-9]{2})'\})", date_literal, re.ASCII | re.IGNORECASE)
        if literal is None:
            raise ValueError("remote predicate date is not an explicit supported literal")
        bounds.add((bound[3], (literal[1] or literal[2]).replace("-", "")))
    if bounds != {(">=", "20260117"), ("<", "20260125")}:
        raise ValueError("remote date bounds differ from the pilot")
    return True


def _matches_field(match: re.Match | None, alias: str, fields: set[str]) -> bool:
    return (
        match is not None and _unquote(match["column"]) in fields
        and (match["qualifier"] is None or _unquote(match["qualifier"]) == alias)
    )


def _without_outer_parens(text: str) -> str:
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        for index, char in enumerate(text):
            depth += (char == "(") - (char == ")")
            if depth == 0:
                break
        if index != len(text) - 1:
            break
        text = text[1:-1].strip()
    return text
