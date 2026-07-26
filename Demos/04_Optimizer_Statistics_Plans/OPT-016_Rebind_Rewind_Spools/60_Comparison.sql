/* OPT-016 comparison: repeat the high-reuse workload with the supporting access path restored. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Rows bigint;
DECLARE @Checksum int;
EXEC lab.usp_Opt016Workload @ProfileCode = 'H', @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt016Capture @Phase = 'COMPARISON', @ProfileCode = 'H', @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

DECLARE @BaselineChecksum int;
DECLARE @ProblemChecksum int;
DECLARE @Spools int;
DECLARE @Access nvarchar(60);
DECLARE @OuterRefs int;

SELECT @BaselineChecksum = ResultChecksum FROM lab.Opt016Evidence WHERE Phase = 'BASELINE';
SELECT @ProblemChecksum = ResultChecksum FROM lab.Opt016Evidence WHERE Phase = 'PROBLEM_HIGH_REUSE';
SELECT @Spools = SpoolCount, @Access = InnerAccessPhysicalOp, @OuterRefs = OuterReferenceCount
FROM lab.Opt016Evidence WHERE Phase = 'COMPARISON';

IF @Rows <> 5000 OR @Checksum IS NULL
   OR @Checksum <> @BaselineChecksum OR @Checksum <> @ProblemChecksum
   OR @Spools <> 0 OR @Access NOT LIKE N'%Seek%' OR @OuterRefs < 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der OPT-016-Vergleich besitzt nicht dieselbe Ergebnismenge und den erwarteten direkten Zugriffspfad.', 1;

SELECT Phase, ProfileCode, ResultRowCount, ResultChecksum,
       NestedLoopsCount, OuterReferenceCount, SpoolCount, FirstSpoolKind,
       SpoolActualRebinds, SpoolActualRewinds, InnerAccessPhysicalOp,
       LastLogicalReads, LastWorkerTimeUs, LastElapsedTimeUs
FROM lab.Opt016Evidence
WHERE Phase IN ('BASELINE', 'PROBLEM_HIGH_REUSE', 'COMPARISON')
ORDER BY CASE Phase WHEN 'BASELINE' THEN 1 WHEN 'PROBLEM_HIGH_REUSE' THEN 2 ELSE 3 END;

SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Rows=', @Rows, N'; Checksum=', @Checksum, N'; Spools=', @Spools, N'; InnerAccess=', @Access) AS ObservedValue,
       N'identische High-Reuse-Ergebnismenge; korrelierter Seek-Pfad; keine Performance Spool' AS RequiredValue,
       N'Der passende Zugriffspfad beseitigt die Notwendigkeit des untersuchten Spoolplans.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
