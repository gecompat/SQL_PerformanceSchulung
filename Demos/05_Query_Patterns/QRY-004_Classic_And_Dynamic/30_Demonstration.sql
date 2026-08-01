/* QRY-004 demonstration: identischer Querytext mit OPTION (RECOMPILE), je Ausführung neu optimiert. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

EXEC sys.sp_recompile @objname = N'lab.usp_Qry004Recompile';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;

EXEC lab.usp_Qry004Recompile @CategoryCode = 'RARE',
                             @ResultRowCount = @Rows OUTPUT,
                             @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'DEMONSTRATION', @Strategy = 'RECOMPILE', @Combination = 'RARE',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Qry004Recompile @CategoryCode = 'CMMN',
                             @ResultRowCount = @Rows OUTPUT,
                             @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'DEMONSTRATION', @Strategy = 'RECOMPILE', @Combination = 'COMMON',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Qry004Recompile @StatusCode = 1,
                             @ResultRowCount = @Rows OUTPUT,
                             @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'DEMONSTRATION', @Strategy = 'RECOMPILE', @Combination = 'STATUS',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @Mismatch int;
DECLARE @BaselineRareReads bigint;
DECLARE @RecompileRareReads bigint;
DECLARE @RecompileCommonReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END)
FROM lab.Qry004Evidence
WHERE Phase = 'DEMONSTRATION';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein Cacheeintrag für lab.usp_Qry004Recompile auswertbar' AS ObservedValue,
           N'objektbezogene Cacheevidenz für alle drei Ausführungen' AS RequiredValue,
           N'Die Cacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @Mismatch = COUNT(*)
FROM lab.Qry004Evidence AS baseline
INNER JOIN lab.Qry004Evidence AS recompiled
        ON recompiled.Phase = 'DEMONSTRATION'
       AND recompiled.Strategy = 'RECOMPILE'
       AND recompiled.Combination = baseline.Combination
WHERE baseline.Phase = 'BASELINE'
  AND baseline.Strategy = 'CATCHALL'
  AND (baseline.ResultRowCount <> recompiled.ResultRowCount
       OR ISNULL(baseline.ResultChecksum, -1) <> ISNULL(recompiled.ResultChecksum, -1));

IF @Mismatch IS NULL OR @Mismatch > 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Recompile-Variante und Catch-all-Baseline liefern nicht dasselbe Ergebnis.', 1;

SELECT @BaselineRareReads = LogicalReads
FROM lab.Qry004Evidence
WHERE Phase = 'BASELINE' AND Strategy = 'CATCHALL' AND Combination = 'RARE';

SELECT @RecompileRareReads = MAX(CASE WHEN Combination = 'RARE' THEN LogicalReads END),
       @RecompileCommonReads = MAX(CASE WHEN Combination = 'COMMON' THEN LogicalReads END)
FROM lab.Qry004Evidence
WHERE Phase = 'DEMONSTRATION' AND Strategy = 'RECOMPILE';

IF @BaselineRareReads IS NULL OR @RecompileRareReads IS NULL OR @RecompileRareReads >= @BaselineRareReads
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SELECTIVE_READ_DIRECTION' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'Reads Catch-all/Recompile für RARE=', ISNULL(@BaselineRareReads, -1), N'/', ISNULL(@RecompileRareReads, -1)) AS ObservedValue,
           N'weniger logische Lesevorgänge für den selektiven Wert' AS RequiredValue,
           N'Die Neuoptimierung hat in dieser Umgebung keine günstigere Zugriffsform für den selektiven Wert gewählt. Das Ergebnis bleibt gleichwertig.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Reads Catch-all RARE=', @BaselineRareReads,
              N'; Reads Recompile RARE/COMMON=', @RecompileRareReads, N'/', ISNULL(@RecompileCommonReads, -1)) AS ObservedValue,
       N'gleiches Ergebnis bei geringeren Lesevorgängen für den selektiven Wert' AS RequiredValue,
       N'Die je Ausführung neu optimierte Variante nutzt die Selektivität des konkreten Werts.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
