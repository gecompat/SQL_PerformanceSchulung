"""Offline SQL contract for the bounded External Tables pilot profile."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta
from enum import Enum
import re


TOKEN = re.compile(r"[A-Z0-9]{8}", re.ASCII)
VERSION = "17.0.5065.9"
ROWS = 4096
DAY_ZERO = date(2026, 1, 1)
EXPECTED = ((0, 128, 250560), (1, 128, 251840), (2, 128, 253120), (3, 128, 254400))
COLUMNS = "FactId int NOT NULL, EventDate date NOT NULL, CategoryId int NOT NULL, Amount int NOT NULL"
CONNECTION_OPTIONS = "Encrypt=Yes;TrustServerCertificate=No;"


class Role(Enum):
    SOURCE = "SOURCE"
    QUERY = "QUERY"


class Route(Enum):
    LOCAL = "Facts"
    PUSHDOWN_ON = "FactsPush"
    PUSHDOWN_OFF = "FactsLocalFilter"


def database_name(token: str, role: Role) -> str:
    if not isinstance(token, str) or TOKEN.fullmatch(token) is None or not isinstance(role, Role):
        raise ValueError("expected an eight-character ASCII pilot token and a fixed VM role")
    return f"SQLPERF_LAB_EXT_{token}_{role.value}"


def database_guard(token: str, role: Role) -> str:
    expected_db = database_name(token, role)
    return f"""SET NOCOUNT ON;
IF DB_NAME() COLLATE Latin1_General_100_BIN2 <> N'{expected_db}'
    OR DATALENGTH(DB_NAME()) <> DATALENGTH(N'{expected_db}')
    OR NOT EXISTS (
        SELECT 1 FROM sys.databases WHERE database_id = DB_ID() AND compatibility_level = 170
    )
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'ProductVersion')), N'') <> N'{VERSION}'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'Edition')), N'') <> N'Enterprise Developer Edition (64-bit)'
    THROW 51060, 'FAIL_CONTRACT: unexpected External Tables pilot database or engine.', 1;
"""


def _owner_guard(token: str, role: Role) -> str:
    return database_guard(token, role) + f"""
SET XACT_ABORT ON;
IF (
    SELECT COUNT_BIG(*) FROM sys.extended_properties AS p
    INNER JOIN (VALUES
        (N'SQLPERF.Project', N'SQL_PerformanceSchulung'),
        (N'SQLPERF.ContractVersion', N'1.0'),
        (N'SQLPERF.RunToken', N'{token}'),
        (N'SQLPERF.PilotProfile', N'EXTERNAL_TABLES_{role.value}')
    ) AS marker(name, value)
        ON p.name COLLATE Latin1_General_100_BIN2 = marker.name
        AND DATALENGTH(p.name) = DATALENGTH(marker.name)
        AND CONVERT(nvarchar(128), p.value) COLLATE Latin1_General_100_BIN2 = marker.value
        AND DATALENGTH(CONVERT(nvarchar(max), p.value)) = DATALENGTH(marker.value)
    WHERE p.class = 0 AND p.major_id = 0 AND p.minor_id = 0
) <> 4
    THROW 51061, 'FAIL_OWNERSHIP: External Tables pilot markers differ.', 1;
"""


def fixture_batch(token: str, role: Role) -> str:
    return _owner_guard(token, role) + f"""
IF OBJECT_ID(N'dbo.Facts') IS NOT NULL
    THROW 51062, 'FAIL_STATE: pilot fixture already exists.', 1;
BEGIN TRANSACTION;
CREATE TABLE dbo.Facts (
    {COLUMNS},
    CONSTRAINT PK_Facts PRIMARY KEY (FactId)
);
INSERT dbo.Facts (FactId, EventDate, CategoryId, Amount)
SELECT 64 * d.value + 16 * c.value + r.value,
    DATEADD(day, d.value, CONVERT(date, '20260101', 112)),
    c.value, 100 * d.value + 10 * c.value + r.value
FROM GENERATE_SERIES(0, 63, 1) AS d
CROSS JOIN GENERATE_SERIES(0, 3, 1) AS c
CROSS JOIN GENERATE_SERIES(0, 15, 1) AS r;
IF @@ROWCOUNT <> {ROWS}
    THROW 51063, 'NOT_PROVEN: pilot fixture row count differs.', 1;
COMMIT;
"""


def external_tables_batch(token: str) -> str:
    guard = _owner_guard(token, Role.QUERY)
    location = f"sqlserver://pbs-{token.lower()}:1433"
    source = database_name(token, Role.SOURCE)
    return guard + f"""
IF NOT EXISTS (
    SELECT 1 FROM sys.database_scoped_credentials
    WHERE name = N'PilotSourceReader' AND credential_identity = N'SqlPerfExtReader_{token}'
)
    THROW 51064, 'FAIL_CONTRACT: run-bound source reader credential is unavailable.', 1;
IF EXISTS (SELECT 1 FROM sys.external_data_sources)
    OR OBJECT_ID(N'dbo.FactsPush') IS NOT NULL OR OBJECT_ID(N'dbo.FactsLocalFilter') IS NOT NULL
    THROW 51065, 'FAIL_STATE: query pilot target is not fresh.', 1;

CREATE EXTERNAL DATA SOURCE PilotPush
WITH (LOCATION = '{location}', PUSHDOWN = ON, CREDENTIAL = PilotSourceReader,
    CONNECTION_OPTIONS = '{CONNECTION_OPTIONS}');
CREATE EXTERNAL DATA SOURCE PilotLocalFilter
WITH (LOCATION = '{location}', PUSHDOWN = OFF, CREDENTIAL = PilotSourceReader,
    CONNECTION_OPTIONS = '{CONNECTION_OPTIONS}');

CREATE EXTERNAL TABLE dbo.FactsPush ({COLUMNS})
WITH (LOCATION = '{source}.dbo.Facts', DATA_SOURCE = PilotPush);
CREATE EXTERNAL TABLE dbo.FactsLocalFilter ({COLUMNS})
WITH (LOCATION = '{source}.dbo.Facts', DATA_SOURCE = PilotLocalFilter);
"""


def statistics_batch(token: str) -> str:
    sql = _owner_guard(token, Role.QUERY)
    for route in Route:
        sql += (
            f"CREATE STATISTICS PilotEventDate ON dbo.{route.value} (EventDate) WITH FULLSCAN;\n"
            f"CREATE STATISTICS PilotCategory ON dbo.{route.value} (CategoryId) WITH FULLSCAN;\n"
        )
    return sql


def fixture_read_batch(token: str, role: Role, route: Route = Route.LOCAL) -> str:
    guard, table = _read_path(token, role, route)
    return guard + f"SELECT FactId, EventDate, CategoryId, Amount FROM dbo.{table} ORDER BY FactId;\n"


def measurement_marker(token: str, route: Route) -> str:
    _read_path(token, Role.QUERY, route)
    return f"SQLPERF_EXT_{token}_{route.name}"


def aggregate_batch(token: str, route: Route) -> str:
    guard, table = _read_path(token, Role.QUERY, route)
    return guard + f"""
SELECT /* {measurement_marker(token, route)} */ CategoryId, COUNT_BIG(*) AS [RowCount], SUM(CONVERT(bigint, Amount)) AS TotalAmount
FROM dbo.{table}
WHERE EventDate >= CONVERT(date, '20260117', 112) AND EventDate < CONVERT(date, '20260125', 112)
GROUP BY CategoryId
ORDER BY CategoryId;
"""


def _read_path(token: str, role: Role, route: Route) -> tuple[str, str]:
    if not isinstance(route, Route) or (role is Role.SOURCE and route is not Route.LOCAL):
        raise ValueError("unexpected External Tables read route")
    return database_guard(token, role), route.value


def verify_fixture(rows: Iterable[tuple[int, date, int, int]]) -> None:
    count = 0
    for row in rows:
        if count >= ROWS or len(row) != 4 or any(type(row[i]) is not int for i in (0, 2, 3)) or type(row[1]) is not date:
            raise ValueError("pilot fixture contains an unexpected row shape or count")
        day, part = divmod(count, 64)
        category, ordinal = divmod(part, 16)
        expected = (count, DAY_ZERO + timedelta(days=day), category, 100 * day + 10 * category + ordinal)
        if row != expected:
            raise ValueError("pilot fixture rows differ from the deterministic source")
        count += 1
    if count != ROWS:
        raise ValueError("pilot fixture is incomplete")


def verify_aggregate(rows: tuple[tuple[int, int, int], ...]) -> None:
    if rows != EXPECTED or any(type(value) is not int for row in rows for value in row):
        raise ValueError("pilot aggregate differs from the four-category oracle")
