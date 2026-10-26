/*
  DGN-004 transport fragment only.

  The caller must supply a plan_handle that has already passed its separate
  source/query/execution binding gate. Run/role/call are frame labels supplied
  by that caller; this file does not establish those identities or prove that
  the handle belongs to the most recent intended execution.

  Required sqlcmd variables are validated by the future runner before use:
    DGN004_RUN: 1-64 ASCII letters, digits, dot, underscore, or hyphen
    DGN004_ROLE: R or H
    DGN004_CALL: decimal 1..9
    DGN004_PLAN_HANDLE: exactly 128 hexadecimal characters

  Run with the existing sqlcmd_process output shape (-h -1, -W, one column,
  no headers). Runtime channel bounds remain a runner responsibility.
*/
SET NOCOUNT ON;

DECLARE @Run varchar(64) = '$(DGN004_RUN)';
DECLARE @Role char(1) = '$(DGN004_ROLE)';
DECLARE @Call tinyint = TRY_CONVERT(tinyint, '$(DGN004_CALL)');
DECLARE @PlanHandle varbinary(64) = TRY_CONVERT(varbinary(64), '$(DGN004_PLAN_HANDLE)', 2);

IF LEN(@Run) NOT BETWEEN 1 AND 64
    OR @Run LIKE '%[^A-Za-z0-9._-]%'
    OR @Role NOT IN ('R', 'H')
    OR @Call NOT BETWEEN 1 AND 9
    OR @PlanHandle IS NULL
    OR DATALENGTH(@PlanHandle) <> 64
    THROW 51000, 'Invalid DGN-004 capture input.', 1;

DECLARE @PlanRows TABLE (QueryPlan xml NULL);
INSERT INTO @PlanRows (QueryPlan)
SELECT qps.query_plan
FROM sys.dm_exec_query_plan_stats(@PlanHandle) AS qps;

IF (SELECT COUNT_BIG(*) FROM @PlanRows) <> 1
    THROW 51001, 'DGN-004 plan handle did not return exactly one row.', 1;

DECLARE @PlanXml xml;
SELECT @PlanXml = QueryPlan FROM @PlanRows;
IF @PlanXml IS NULL
    THROW 51002, 'DGN-004 plan handle returned no plan XML.', 1;

/* XML-to-varbinary serialization is the server-side UTF-16 byte stream. */
DECLARE @PlanBytes varbinary(max) = CONVERT(varbinary(max), @PlanXml);
DECLARE @ByteCount int = DATALENGTH(@PlanBytes);
IF @ByteCount <= 0 OR @ByteCount > 524288 OR @ByteCount % 2 <> 0
    THROW 51003, 'DGN-004 plan byte limit exceeded.', 1;

DECLARE @ChunkCount int = (@ByteCount + 99) / 100;
DECLARE @Sha256 varchar(64) = UPPER(CONVERT(varchar(64), HASHBYTES('SHA2_256', @PlanBytes), 2));
DECLARE @Common varchar(160) = @Run + '|' + @Role + '|'
    + CONVERT(varchar(2), @Call) + '|'
    + CONVERT(varchar(10), @ByteCount) + '|'
    + CONVERT(varchar(10), @ChunkCount) + '|'
    + @Sha256;

;WITH ChunkSequence AS
(
    SELECT CONVERT(int, 1) AS SequenceNo
    WHERE @ChunkCount > 0
    UNION ALL
    SELECT SequenceNo + 1
    FROM ChunkSequence
    WHERE SequenceNo < @ChunkCount
),
FrameRows AS
(
    SELECT CONVERT(int, 0) AS Ordinal,
           CONVERT(varchar(256), 'DGN004_PLAN_START|' + @Common) AS Record
    UNION ALL
    SELECT SequenceNo,
           CONVERT(varchar(256), 'DGN004_PLAN_CHUNK|'
               + CONVERT(varchar(10), SequenceNo) + '|'
               + CONVERT(varchar(200), SUBSTRING(@PlanBytes, ((SequenceNo - 1) * 100) + 1, 100), 2))
    FROM ChunkSequence
    UNION ALL
    SELECT @ChunkCount + 1,
           CONVERT(varchar(256), 'DGN004_PLAN_END|' + @Common)
)
SELECT Record
FROM FrameRows
ORDER BY Ordinal
OPTION (MAXRECURSION 0);
