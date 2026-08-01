/* QRY-013 demonstration: CLIENT_PROFILE_B, identischer Querytext und identischer Parameterwert. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

/* CLIENT_PROFILE_B: unterscheidet sich ausschliesslich in ARITHABORT von CLIENT_PROFILE_A. */
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ANSI_NULL_DFLT_ON ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
SET ARITHABORT OFF;
GO

SET NOCOUNT ON;
DECLARE @ResultRowCount int;
DECLARE @ResultChecksum int;

EXEC lab.usp_Qry013Probe @CategoryCode = 'RARE',
                         @ResultRowCount = @ResultRowCount OUTPUT,
                         @ResultChecksum = @ResultChecksum OUTPUT;

EXEC lab.usp_Qry013Capture @Phase = 'DEMONSTRATION',
                           @ProfileCode = 'B',
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
WHERE Phase = 'DEMONSTRATION';

SELECT @BaselineOptions = SessionOptions,
       @BaselineChecksum = ResultChecksum
FROM lab.Qry013Evidence
WHERE Phase = 'BASELINE';

IF @EvidenceAvailable = 0 OR @BaselineOptions IS NULL
BEGIN
    SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'Cacheattribute oder Baselinewerte fehlen' AS ObservedValue,
           N'Baselinewerte und objektbezogene Cacheeintraege' AS RequiredValue,
           N'Der Kontextvergleich ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @RowCount <> 20 OR @Checksum <> @BaselineChecksum
    THROW 51006, 'FAIL_RESULT_CONTRACT: Beide Clientprofile müssen dasselbe fachliche Ergebnis liefern.', 1;

IF @SessionOptions = @BaselineOptions
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die beiden Clientprofile unterscheiden sich nicht im Sessionkontext.', 1;

IF @CachedPlanCount <> 2 OR @DistinctSetOptions <> 2
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der abweichende Sessionkontext erzeugt nicht den erwarteten zweiten Cacheeintrag.', 1;

SELECT 1 AS Sequence, 'DEMONSTRATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Profil=B; @@OPTIONS=', @SessionOptions, N' statt ', @BaselineOptions,
              N'; Cacheeintraege=', @CachedPlanCount, N'; SetOptionsVarianten=', @DistinctSetOptions,
              N'; Ergebnis identisch zur Baseline') AS ObservedValue,
       N'zwei Cacheeintraege bei identischem Ergebnis' AS RequiredValue,
       N'Gleicher Querytext und gleicher Parameterwert erzeugen bei abweichendem Sessionkontext einen zusätzlichen Cacheeintrag.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
