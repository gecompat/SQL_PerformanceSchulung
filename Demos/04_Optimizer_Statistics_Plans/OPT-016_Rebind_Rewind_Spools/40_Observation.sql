/* OPT-016 observation: reuse the same cached plan for the unique-key profile. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF NOT EXISTS (SELECT 1 FROM lab.Opt016Evidence WHERE Phase = 'PROBLEM_HIGH_REUSE')
    THROW 51003, 'FAIL_STATE: Die OPT-016-High-Reuse-Evidenz fehlt.', 1;

DECLARE @Rows bigint;
DECLARE @Checksum int;
EXEC lab.usp_Opt016Workload @ProfileCode = 'L', @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt016Capture @Phase = 'PROBLEM_LOW_REUSE', @ProfileCode = 'L', @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

DECLARE @HighHash binary(8);
DECLARE @LowHash binary(8);
DECLARE @HighRebinds bigint;
DECLARE @HighRewinds bigint;
DECLARE @LowRebinds bigint;
DECLARE @LowRewinds bigint;
DECLARE @HighSpools int;
DECLARE @LowSpools int;

SELECT @HighHash = QueryHash, @HighRebinds = SpoolActualRebinds,
       @HighRewinds = SpoolActualRewinds, @HighSpools = SpoolCount
FROM lab.Opt016Evidence WHERE Phase = 'PROBLEM_HIGH_REUSE';
SELECT @LowHash = QueryHash, @LowRebinds = SpoolActualRebinds,
       @LowRewinds = SpoolActualRewinds, @LowSpools = SpoolCount
FROM lab.Opt016Evidence WHERE Phase = 'PROBLEM_LOW_REUSE';

IF @Rows <> 20 OR @Checksum IS NULL OR @HighHash IS NULL OR @LowHash IS NULL OR @HighHash <> @LowHash
   OR @HighSpools < 1 OR @LowSpools < 1 OR @HighRewinds <= @LowRewinds
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-016-Reuse-Profile zeigen nicht die erwartete Rewind-Richtung im selben Queryvertrag.', 1;

SELECT Phase, ProfileCode, ResultRowCount, ResultChecksum,
       QueryHashHex = CONVERT(varchar(18), QueryHash, 1),
       NestedLoopsCount, OuterReferenceCount, SpoolCount, FirstSpoolKind,
       SpoolActualRebinds, SpoolActualRewinds, SpoolActualExecutions, SpoolActualRows,
       InnerAccessPhysicalOp, LastLogicalReads, LastWorkerTimeUs, LastElapsedTimeUs
FROM lab.Opt016Evidence
WHERE Phase IN ('PROBLEM_HIGH_REUSE', 'PROBLEM_LOW_REUSE')
ORDER BY CASE Phase WHEN 'PROBLEM_HIGH_REUSE' THEN 1 ELSE 2 END;

SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'HighRebinds=', @HighRebinds, N'; HighRewinds=', @HighRewinds,
              N'; LowRebinds=', @LowRebinds, N'; LowRewinds=', @LowRewinds) AS ObservedValue,
       N'identischer Query Hash und Spoolplan; High-Reuse-Profil mit mehr Rewinds als Unique-Key-Profil' AS RequiredValue,
       N'Rebind und Rewind werden zusammen mit dem äußeren Schlüsselprofil interpretiert.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
