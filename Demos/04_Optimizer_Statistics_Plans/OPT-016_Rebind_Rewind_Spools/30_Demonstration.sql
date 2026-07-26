/* OPT-016 demonstration: remove the supporting index and inspect an optimizer-chosen reuse plan. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF NOT EXISTS
(
    SELECT 1 FROM sys.indexes AS i
    INNER JOIN sys.objects AS o ON o.object_id = i.object_id
    INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
    WHERE s.name = N'lab' AND o.name = N'WorkItemDetail'
      AND i.name = N'IX_WorkItemDetail_Group_Sequence'
)
    THROW 51003, 'FAIL_STATE: Der OPT-016-Baseline-Index ist vor der Demonstration nicht vorhanden.', 1;

DROP INDEX IX_WorkItemDetail_Group_Sequence ON lab.WorkItemDetail;
EXEC sys.sp_recompile N'lab.usp_Opt016Workload';

DECLARE @Rows bigint;
DECLARE @Checksum int;
EXEC lab.usp_Opt016Workload @ProfileCode = 'H', @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt016Capture @Phase = 'PROBLEM_HIGH_REUSE', @ProfileCode = 'H', @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

DECLARE @Loops int;
DECLARE @OuterRefs int;
DECLARE @Spools int;
DECLARE @SpoolKind nvarchar(60);
DECLARE @Rebinds bigint;
DECLARE @Rewinds bigint;
DECLARE @Executions bigint;

SELECT @Loops = NestedLoopsCount, @OuterRefs = OuterReferenceCount,
       @Spools = SpoolCount, @SpoolKind = FirstSpoolKind,
       @Rebinds = SpoolActualRebinds, @Rewinds = SpoolActualRewinds,
       @Executions = SpoolActualExecutions
FROM lab.Opt016Evidence
WHERE Phase = 'PROBLEM_HIGH_REUSE';

IF @Rows <> 5000 OR @Checksum IS NULL
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-016-Problemabfrage liefert nicht die vollständige Ergebnismenge.', 1;

IF @Spools < 1
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'PLAN_SHAPE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_PLAN_SHAPE_NOT_PRODUCED' AS Code,
           CONCAT(N'Loops=', COALESCE(@Loops, 0), N'; OuterReferences=', COALESCE(@OuterRefs, 0), N'; Spools=', COALESCE(@Spools, 0)) AS ObservedValue,
           N'mindestens eine optimizergewählte Index- oder Table-Spool im korrelierten Plan' AS RequiredValue,
           N'Die konkrete Spool-Planform wurde auf diesem Build trotz geeignetem Datenprofil nicht erzeugt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PLAN_SHAPE_NOT_PRODUCED';
    RETURN;
END;

IF @Loops < 1 OR @OuterRefs < 1 OR @Executions < 1 OR (@Rebinds + @Rewinds) < 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die erzeugte OPT-016-Spool besitzt keine vollständige Outer-Reference- und Runtime-Evidenz.', 1;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Rows=', @Rows, N'; Spool=', @SpoolKind, N'; Rebinds=', @Rebinds,
              N'; Rewinds=', @Rewinds, N'; Executions=', @Executions) AS ObservedValue,
       N'5000 Ergebnisse; Spool mit Outer References und Runtime-Reuse-Zählern' AS RequiredValue,
       N'Der optimizergewählte Wiederverwendungsplan ist erfasst.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
