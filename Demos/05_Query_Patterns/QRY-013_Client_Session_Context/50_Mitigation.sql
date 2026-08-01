/* QRY-013 mitigation: genau eine Massnahme - der Sessionkontext beider Clientprofile wird angeglichen. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

EXEC sys.sp_recompile @objname = N'lab.usp_Qry013Probe';
GO

/* Angeglichener Kontext: CLIENT_PROFILE_B übernimmt exakt die SET-Optionen von CLIENT_PROFILE_A. */
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

/* Erster Aufruf steht für CLIENT_PROFILE_A, zweiter für das angeglichene CLIENT_PROFILE_B. */
EXEC lab.usp_Qry013Probe @CategoryCode = 'RARE',
                         @ResultRowCount = @ResultRowCount OUTPUT,
                         @ResultChecksum = @ResultChecksum OUTPUT;

EXEC lab.usp_Qry013Probe @CategoryCode = 'RARE',
                         @ResultRowCount = @ResultRowCount OUTPUT,
                         @ResultChecksum = @ResultChecksum OUTPUT;

EXEC lab.usp_Qry013Capture @Phase = 'MITIGATION',
                           @ProfileCode = 'B_ALIGNED',
                           @ParameterValue = 'RARE',
                           @ResultRowCount = @ResultRowCount,
                           @ResultChecksum = @ResultChecksum;
GO

SET NOCOUNT ON;
DECLARE @CachedPlanCount int;
DECLARE @DistinctSetOptions int;
DECLARE @RowCount int;
DECLARE @Checksum int;
DECLARE @EvidenceAvailable bit;
DECLARE @SessionOptions int;
DECLARE @BaselineOptions int;
DECLARE @BaselineChecksum int;

SELECT @CachedPlanCount = CachedPlanCount,
       @DistinctSetOptions = DistinctSetOptions,
       @RowCount = ResultRowCount,
       @Checksum = ResultChecksum,
       @EvidenceAvailable = EvidenceAvailable,
       @SessionOptions = SessionOptions
FROM lab.Qry013Evidence
WHERE Phase = 'MITIGATION';

SELECT @BaselineOptions = SessionOptions,
       @BaselineChecksum = ResultChecksum
FROM lab.Qry013Evidence
WHERE Phase = 'BASELINE';

IF @EvidenceAvailable = 0 OR @BaselineOptions IS NULL
BEGIN
    SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'Cacheattribute oder Baselinewerte fehlen' AS ObservedValue,
           N'Baselinewerte und objektbezogene Cacheeintraege' AS RequiredValue,
           N'Die Wirkung der Angleichung ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @SessionOptions <> @BaselineOptions
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der angeglichene Kontext entspricht nicht dem Kontext der Baseline.', 1;

IF @RowCount <> 20 OR @Checksum <> @BaselineChecksum
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Angleichung darf das fachliche Ergebnis nicht verändern.', 1;

IF @CachedPlanCount <> 1 OR @DistinctSetOptions <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Nach der Angleichung wird genau ein Cacheeintrag erwartet.', 1;

SELECT 1 AS Sequence, 'MITIGATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Angeglichener Kontext; @@OPTIONS=', @SessionOptions, N'; Cacheeintraege=', @CachedPlanCount,
              N'; SetOptionsVarianten=', @DistinctSetOptions) AS ObservedValue,
       N'genau ein Cacheeintrag für beide Clientprofile' AS RequiredValue,
       N'Die Angleichung genau einer Kontextdimension beseitigt den zusätzlichen Cacheeintrag.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
