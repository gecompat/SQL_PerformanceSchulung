/*
  DGN-004 bounded plan-cache candidate snapshot only.

  This script returns every cached statement row matching the exact current
  registered module source, database/object IDs, and registered statement start
  offset. It never chooses a plan_handle. The caller compares complete snapshots
  around exactly one invocation and must fail closed on ambiguity or change.

  The expected module UTF-16LE bytes are inserted by the bounded Python caller
  through the single hexadecimal template token below; other values are
  validated sqlcmd variables. No SQL or runtime evidence is produced by static
  use of this fixture.
*/
SET NOCOUNT ON;

DECLARE @Run varchar(64) = '$(DGN004_RUN)';
DECLARE @Role char(1) = '$(DGN004_ROLE)';
DECLARE @Call tinyint = TRY_CONVERT(tinyint, '$(DGN004_CALL)');
DECLARE @DatabaseId int = TRY_CONVERT(int, '$(DGN004_DATABASE_ID)');
DECLARE @ObjectId int = TRY_CONVERT(int, '$(DGN004_OBJECT_ID)');
DECLARE @StatementStartOffset int = TRY_CONVERT(int, '$(DGN004_STATEMENT_START_OFFSET)');
DECLARE @ExpectedModule varbinary(max) = TRY_CONVERT(
    varbinary(max), '__DGN004_EXPECTED_MODULE_UTF16_HEX__', 2);

IF @Run IS NULL
    OR @Role IS NULL
    OR @Call IS NULL
    OR @DatabaseId IS NULL
    OR @ObjectId IS NULL
    OR @StatementStartOffset IS NULL
    OR LEN(@Run) NOT BETWEEN 1 AND 64
    OR @Run LIKE '%[^A-Za-z0-9._-]%'
    OR @Role NOT IN ('R', 'H')
    OR @Call NOT BETWEEN 1 AND 9
    OR @DatabaseId NOT BETWEEN 1 AND 32767
    OR @ObjectId <= 0
    OR @StatementStartOffset < 0
    OR @StatementStartOffset % 2 <> 0
    OR @ExpectedModule IS NULL
    OR DATALENGTH(@ExpectedModule) NOT BETWEEN 2 AND 16384
    OR DATALENGTH(@ExpectedModule) % 2 <> 0
    OR DB_ID() <> @DatabaseId
    THROW 51010, 'Invalid DGN-004 plan candidate snapshot input.', 1;

DECLARE @ExpectedSchema sysname = N'dgn004';
DECLARE @ExpectedModuleName sysname =
    CASE @Role WHEN 'R' THEN N'ReplayReference' ELSE N'ReplayHintControl' END;
DECLARE @CurrentModules TABLE (ModuleBytes varbinary(max) NOT NULL);

INSERT INTO @CurrentModules (ModuleBytes)
SELECT CONVERT(varbinary(max), sm.definition)
FROM sys.objects AS o
INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
INNER JOIN sys.sql_modules AS sm ON sm.object_id = o.object_id
WHERE o.object_id = @ObjectId
  AND o.type = 'P'
  AND s.name = @ExpectedSchema
  AND o.name = @ExpectedModuleName;

IF (SELECT COUNT_BIG(*) FROM @CurrentModules) <> 1
    THROW 51011, 'DGN-004 module identity is missing or ambiguous.', 1;

DECLARE @CurrentModule varbinary(max);
SELECT @CurrentModule = ModuleBytes FROM @CurrentModules;
IF @CurrentModule <> @ExpectedModule
    THROW 51012, 'DGN-004 current module source differs from the registered bytes.', 1;

DECLARE @ExpectedModuleByteCount int = DATALENGTH(@ExpectedModule);
DECLARE @ExpectedModuleSha256 varchar(64) = UPPER(CONVERT(
    varchar(64), HASHBYTES('SHA2_256', @ExpectedModule), 2));

DECLARE @Candidates TABLE
(
    RowNo bigint NOT NULL,
    PlanHandleHex varchar(128) NOT NULL,
    SqlHandleHex varchar(128) NOT NULL,
    DatabaseId int NOT NULL,
    ObjectId int NOT NULL,
    StatementStartOffset int NOT NULL,
    StatementEndOffset int NOT NULL,
    PlanGenerationNum bigint NOT NULL,
    CreationTime varchar(23) NOT NULL,
    LastExecutionTime varchar(23) NOT NULL,
    ExecutionCount bigint NOT NULL,
    QueryHashHex varchar(16) NOT NULL,
    QueryPlanHashHex varchar(16) NOT NULL,
    ModuleByteCount int NOT NULL,
    ModuleSha256 varchar(64) NOT NULL
);

DECLARE @CandidateCount bigint;
SELECT @CandidateCount = COUNT_BIG(*)
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
WHERE qs.plan_handle IS NOT NULL
  AND st.dbid = @DatabaseId
  AND st.objectid = @ObjectId
  AND qs.statement_start_offset = @StatementStartOffset
  AND CONVERT(varbinary(max), st.text) = @ExpectedModule;

IF @CandidateCount > 4096
    THROW 51013, 'DGN-004 plan candidate row limit exceeded.', 1;

INSERT INTO @Candidates
(
    RowNo, PlanHandleHex, SqlHandleHex, DatabaseId, ObjectId,
    StatementStartOffset, StatementEndOffset, PlanGenerationNum,
    CreationTime, LastExecutionTime, ExecutionCount, QueryHashHex,
    QueryPlanHashHex, ModuleByteCount, ModuleSha256
)
SELECT
    ROW_NUMBER() OVER
    (
        ORDER BY qs.plan_handle, qs.sql_handle,
                 qs.statement_start_offset, qs.statement_end_offset,
                 qs.plan_generation_num, qs.creation_time
    ),
    UPPER(CONVERT(varchar(128), qs.plan_handle, 2)),
    UPPER(CONVERT(varchar(128), qs.sql_handle, 2)),
    st.dbid,
    st.objectid,
    qs.statement_start_offset,
    qs.statement_end_offset,
    qs.plan_generation_num,
    CONVERT(varchar(23), qs.creation_time, 126),
    CONVERT(varchar(23), qs.last_execution_time, 126),
    qs.execution_count,
    UPPER(CONVERT(varchar(16), qs.query_hash, 2)),
    UPPER(CONVERT(varchar(16), qs.query_plan_hash, 2)),
    DATALENGTH(CONVERT(varbinary(max), st.text)),
    UPPER(CONVERT(varchar(64), HASHBYTES(
        'SHA2_256', CONVERT(varbinary(max), st.text)), 2))
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
WHERE qs.plan_handle IS NOT NULL
  AND st.dbid = @DatabaseId
  AND st.objectid = @ObjectId
  AND qs.statement_start_offset = @StatementStartOffset
  AND CONVERT(varbinary(max), st.text) = @ExpectedModule;

IF (SELECT COUNT_BIG(*) FROM @Candidates) <> @CandidateCount
    THROW 51014, 'DGN-004 plan candidate snapshot changed while being captured.', 1;

DECLARE @RowCount bigint = (SELECT COUNT_BIG(*) FROM @Candidates);
DECLARE @StartRecord varchar(512) = 'DGN004_CACHE_START|'
    + @Run + '|' + @Role + '|' + CONVERT(varchar(2), @Call) + '|'
    + CONVERT(varchar(20), @RowCount) + '|'
    + CONVERT(varchar(10), @ExpectedModuleByteCount) + '|'
    + @ExpectedModuleSha256;
DECLARE @EndRecord varchar(512) = 'DGN004_CACHE_END|'
    + @Run + '|' + @Role + '|' + CONVERT(varchar(2), @Call) + '|'
    + CONVERT(varchar(20), @RowCount) + '|'
    + CONVERT(varchar(10), @ExpectedModuleByteCount) + '|'
    + @ExpectedModuleSha256;

;WITH FrameRecords AS
(
    SELECT CONVERT(bigint, 0) AS Ordinal, @StartRecord AS Record
    UNION ALL
    SELECT RowNo,
           CONVERT(varchar(512), 'DGN004_CACHE_ROW|'
               + PlanHandleHex + '|' + SqlHandleHex + '|'
               + CONVERT(varchar(10), DatabaseId) + '|'
               + CONVERT(varchar(10), ObjectId) + '|'
               + CONVERT(varchar(10), StatementStartOffset) + '|'
               + CONVERT(varchar(10), StatementEndOffset) + '|'
               + CONVERT(varchar(20), PlanGenerationNum) + '|'
               + CreationTime + '|' + LastExecutionTime + '|'
               + CONVERT(varchar(20), ExecutionCount) + '|'
               + QueryHashHex + '|' + QueryPlanHashHex + '|'
               + CONVERT(varchar(10), ModuleByteCount) + '|'
               + ModuleSha256)
    FROM @Candidates
    UNION ALL
    SELECT @RowCount + 1, @EndRecord
)
SELECT Record
FROM FrameRecords
ORDER BY Ordinal;
