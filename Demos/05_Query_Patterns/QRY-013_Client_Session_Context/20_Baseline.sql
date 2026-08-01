/* QRY-013 baseline: CLIENT_PROFILE_A, seltener Parameterwert, frisch kompiliertes Demoobjekt. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

EXEC sys.sp_recompile @objname = N'lab.usp_Qry013Probe';
GO

/* CLIENT_PROFILE_A: vollständig explizit gesetzter, neutraler Sessionkontext. */
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ANSI_NULL_DFLT_ON ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
SET ARITHABORT ON;
GO

SET NOCOUNT ON;
DECLARE @ResultRowCount int;
DECLARE @ResultChecksum int;

EXEC lab.usp_Qry013Probe @CategoryCode = 'RARE',
                         @ResultRowCount = @ResultRowCount OUTPUT,
                         @ResultChecksum = @ResultChecksum OUTPUT;

EXEC lab.usp_Qry013Capture @Phase = 'BASELINE',
                           @ProfileCode = 'A',
                           @ParameterValue = 'RARE',
                           @ResultRowCount = @ResultRowCount,
                           @ResultChecksum = @ResultChecksum;
GO

SET NOCOUNT ON;
DECLARE @CachedPlanCount int;
DECLARE @DistinctSetOptions int;
DECLARE @RowCount int;
DECLARE @EvidenceAvailable bit;
DECLARE @SessionOptions int;

SELECT @CachedPlanCount = CachedPlanCount,
       @DistinctSetOptions = DistinctSetOptions,
       @RowCount = ResultRowCount,
       @EvidenceAvailable = EvidenceAvailable,
       @SessionOptions = SessionOptions
FROM lab.Qry013Evidence
WHERE Phase = 'BASELINE';

IF @EvidenceAvailable = 0
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein Cacheeintrag für lab.usp_Qry013Probe auswertbar' AS ObservedValue,
           N'mindestens ein objektbezogener Cacheeintrag' AS RequiredValue,
           N'Die Cacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @RowCount <> 20
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Baseline liefert nicht die erwartete Trefferzahl für RARE.', 1;

IF @CachedPlanCount <> 1 OR @DistinctSetOptions <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Nach objektbezogener Neukompilierung wird genau ein Cacheeintrag erwartet.', 1;

SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Profil=A; @@OPTIONS=', @SessionOptions, N'; Cacheeintraege=', @CachedPlanCount,
              N'; SetOptionsVarianten=', @DistinctSetOptions, N'; Zeilen=', @RowCount) AS ObservedValue,
       N'genau ein Cacheeintrag und 20 Treffer' AS RequiredValue,
       N'Ausgangsmessung mit CLIENT_PROFILE_A ist erfasst.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
