/* QRY-013 observation: CLIENT_PROFILE_A mit abweichendem Parameterwert widerlegt die Ein-Ursachen-Hypothese. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

/* CLIENT_PROFILE_A: identisch zur Baseline, damit die SET-Optionen als Ursache ausscheiden. */
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

EXEC lab.usp_Qry013Probe @CategoryCode = 'CMMN',
                         @ResultRowCount = @ResultRowCount OUTPUT,
                         @ResultChecksum = @ResultChecksum OUTPUT;

EXEC lab.usp_Qry013Capture @Phase = 'OBSERVATION',
                           @ProfileCode = 'A',
                           @ParameterValue = 'CMMN',
                           @ResultRowCount = @ResultRowCount,
                           @ResultChecksum = @ResultChecksum;
GO

SET NOCOUNT ON;
DECLARE @CachedPlanCount int;
DECLARE @RowCount int;
DECLARE @EvidenceAvailable bit;
DECLARE @SessionOptions int;
DECLARE @Reads bigint;
DECLARE @BaselineOptions int;
DECLARE @BaselineReads bigint;

SELECT @CachedPlanCount = CachedPlanCount,
       @RowCount = ResultRowCount,
       @EvidenceAvailable = EvidenceAvailable,
       @SessionOptions = SessionOptions,
       @Reads = LogicalReads
FROM lab.Qry013Evidence
WHERE Phase = 'OBSERVATION';

SELECT @BaselineOptions = SessionOptions,
       @BaselineReads = LogicalReads
FROM lab.Qry013Evidence
WHERE Phase = 'BASELINE';

IF @EvidenceAvailable = 0 OR @BaselineOptions IS NULL
BEGIN
    SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'Cacheattribute oder Baselinewerte fehlen' AS ObservedValue,
           N'Baselinewerte und objektbezogene Cacheeintraege' AS RequiredValue,
           N'Die zweite Kontextdimension ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

IF @RowCount <> 20000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der häufige Parameterwert liefert nicht die erwartete Trefferzahl.', 1;

IF @SessionOptions <> @BaselineOptions
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Observation muss denselben Sessionkontext wie die Baseline verwenden.', 1;

IF @CachedPlanCount <> 2
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der bereits vorhandene Cacheeintrag von CLIENT_PROFILE_A wird nicht wiederverwendet.', 1;

IF @Reads IS NULL OR @BaselineReads IS NULL OR @Reads < @BaselineReads
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Arbeitsmenge des wiederverwendeten Plans ist nicht auswertbar.', 1;

IF @Reads = @BaselineReads
BEGIN
    SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'PARAMETER_DIMENSION' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'Reads=', @Reads, N'; BaselineReads=', @BaselineReads) AS ObservedValue,
           N'messbar hoehere Arbeitsmenge bei wiederverwendetem Plan' AS RequiredValue,
           N'Die Parameterdimension ist sichtbar, die Arbeitsmenge unterscheidet sich in dieser Umgebung jedoch nicht messbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Profil=A; @@OPTIONS unveraendert=', @SessionOptions, N'; Cacheeintraege=', @CachedPlanCount,
              N'; Reads=', @Reads, N' statt ', @BaselineReads, N'; Zeilen=', @RowCount) AS ObservedValue,
       N'identischer Sessionkontext, dennoch abweichende Arbeitsmenge' AS RequiredValue,
       N'Die Hypothese, allein die SET-Optionen erklaerten den Unterschied, ist widerlegt: Parameterwert und Planwiederverwendung sind eine eigene Dimension.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
