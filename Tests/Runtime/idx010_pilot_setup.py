"""SQL batches for the ordered NCCI pilot proposal. This module does not run SQL."""
from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from hashlib import sha256
import re


ROWGROUP_ROWS = 1_048_576
ROWGROUP_COUNT = 4
FIXTURE_ROWS = ROWGROUP_ROWS * ROWGROUP_COUNT
MULTIPLIER = 1_048_573
FIXTURE_SHA256 = "bfa6e87fc9501d335d859b5d509d6ed466cd1a272e026cbd60e9657c065d955f"
INDEX_NAME = "IX_Events"
RUN_TOKEN = re.compile(r"[A-Z0-9]{1,20}", re.ASCII)


class Arm(Enum):
    CONTROL = "CONTROL"
    ORDERED = "ORDERED"


def target_database(run_token: str, arm: Arm) -> str:
    if not isinstance(run_token, str) or RUN_TOKEN.fullmatch(run_token) is None:
        raise ValueError("expected an uppercase ASCII run token of 1–20 characters")
    if not isinstance(arm, Arm):
        raise ValueError("expected a fixed pilot arm")
    return f"SQLPERF_LAB_IDX010_NCCI_{run_token}_{arm.value}"


def _ownership_guard(run_token: str, arm: Arm) -> str:
    database = target_database(run_token, arm)
    return f"""SET NOCOUNT ON;
SET XACT_ABORT ON;
SET IMPLICIT_TRANSACTIONS OFF;

IF @@TRANCOUNT <> 0
    THROW 51009, 'FAIL_CONTRACT: IDX-010 NCCI requires autocommit.', 1;

IF COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'ProductVersion')), N'') <> N'17.0.5065.9'
    OR COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY(N'Edition')), N'') <> N'Enterprise Developer Edition (64-bit)'
    THROW 51000, 'SKIP_VERSION: IDX-010 ordered NCCI requires the pinned Developer build.', 1;

IF DB_NAME() COLLATE Latin1_General_100_BIN2 <> N'{database}'
    OR DATALENGTH(DB_NAME()) <> DATALENGTH(N'{database}')
    OR NOT EXISTS (
        SELECT 1 FROM sys.databases
        WHERE database_id = DB_ID() AND compatibility_level = 170 AND recovery_model = 3
    )
    THROW 51001, 'FAIL_CONTRACT: IDX-010 NCCI database or settings differ.', 1;

IF (
    SELECT COUNT_BIG(*) FROM sys.extended_properties AS p
    INNER JOIN (VALUES
        (N'SQLPERF.Project', N'SQL_PerformanceSchulung'),
        (N'SQLPERF.ContractVersion', N'1.0'),
        (N'SQLPERF.DemoId', N'IDX-010'),
        (N'SQLPERF.RunToken', N'{run_token}'),
        (N'SQLPERF.PilotProfile', N'ORDERED_NCCI_{arm.value}')
    ) AS m(name, value)
        ON p.name COLLATE Latin1_General_100_BIN2 = m.name
        AND DATALENGTH(p.name) = DATALENGTH(m.name)
        AND CONVERT(nvarchar(128), p.value) COLLATE Latin1_General_100_BIN2 = m.value
        AND DATALENGTH(CONVERT(nvarchar(max), p.value)) = DATALENGTH(m.value)
    WHERE p.class = 0 AND p.major_id = 0 AND p.minor_id = 0
) <> 5
    THROW 51002, 'FAIL_OWNERSHIP: IDX-010 NCCI database markers differ.', 1;
"""


def fixture_setup_batch(run_token: str, arm: Arm) -> str:
    return _ownership_guard(run_token, arm) + """
IF EXISTS (SELECT 1 FROM sys.objects WHERE schema_id = SCHEMA_ID(N'dbo') AND name = N'Events')
    THROW 51003, 'FAIL_STATE: IDX-010 fixture already exists.', 1;

CREATE TABLE dbo.Events (
    EventId bigint NOT NULL,
    EventDayKey bigint NOT NULL,
    CONSTRAINT PK_Events PRIMARY KEY CLUSTERED (EventId)
);
"""


def fixture_chunk_batch(run_token: str, arm: Arm, chunk: int) -> str:
    if type(chunk) is not int or not 0 <= chunk < ROWGROUP_COUNT:
        raise ValueError("expected a fixture chunk index from 0 to 3")
    start = chunk * ROWGROUP_ROWS
    end = start + ROWGROUP_ROWS - 1
    return _ownership_guard(run_token, arm) + f"""
IF EXISTS (
    SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID(N'dbo.Events') AND type IN (5, 6)
)
    THROW 51004, 'FAIL_STATE: IDX-010 fixture cannot change after index creation.', 1;

IF (SELECT COUNT_BIG(*) FROM dbo.Events) <> {start}
    THROW 51005, 'FAIL_STATE: IDX-010 fixture chunk is out of sequence.', 1;

INSERT dbo.Events (EventId, EventDayKey)
SELECT value, (value * {MULTIPLIER}) % {FIXTURE_ROWS}
FROM GENERATE_SERIES(CONVERT(bigint, {start}), CONVERT(bigint, {end}), CONVERT(bigint, 1))
OPTION (MAXDOP 1);

IF @@ROWCOUNT <> {ROWGROUP_ROWS}
    THROW 51006, 'NOT_PROVEN: IDX-010 fixture chunk has an unexpected row count.', 1;
"""


def fixture_identity_batch(run_token: str, arm: Arm) -> str:
    return _ownership_guard(run_token, arm) + """
SELECT EventId, EventDayKey
FROM dbo.Events
ORDER BY EventId
OPTION (MAXDOP 1);
"""


def verify_fixture_identity(rows: Iterable[tuple[int, int]]) -> str:
    """Stream a sorted fixture without retaining its rows or logging payload."""
    digest = sha256()
    count = 0
    for event_id, day_key in rows:
        if (
            count >= FIXTURE_ROWS
            or type(event_id) is not int
            or type(day_key) is not int
            or event_id != count
            or day_key != (count * MULTIPLIER) % FIXTURE_ROWS
        ):
            raise ValueError("fixture row differs from its expected identity")
        digest.update(f"{event_id},{day_key}\n".encode("ascii"))
        count += 1
    if count != FIXTURE_ROWS or digest.hexdigest() != FIXTURE_SHA256:
        raise ValueError("fixture stream does not match the fixed count and digest")
    return FIXTURE_SHA256


def index_build_batch(run_token: str, arm: Arm) -> str:
    """The caller must first prove the fixture identities for *both* arms."""
    guard = _ownership_guard(run_token, arm)
    order = " ORDER (EventDayKey)" if arm is Arm.ORDERED else ""
    return guard + f"""
IF (SELECT COUNT_BIG(*) FROM dbo.Events) <> {FIXTURE_ROWS}
    THROW 51007, 'NOT_PROVEN: IDX-010 fixture is incomplete.', 1;

IF EXISTS (
    SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID(N'dbo.Events') AND type IN (5, 6)
)
    THROW 51008, 'FAIL_STATE: IDX-010 columnstore index already exists.', 1;

CREATE NONCLUSTERED COLUMNSTORE INDEX {INDEX_NAME}
    ON dbo.Events (EventDayKey, EventId){order}
    WITH (MAXDOP = 1, ONLINE = OFF);
"""
