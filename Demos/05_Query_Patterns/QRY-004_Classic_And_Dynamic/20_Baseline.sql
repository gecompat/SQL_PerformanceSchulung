/* QRY-004 baseline: Catch-all-Prädikat, drei Selektivitäten, ein einziger zwischengespeicherter Plan. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

EXEC sys.sp_recompile @objname = N'lab.usp_Qry004CatchAll';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;

/* Kompilierungsreihenfolge: der selektive Wert erzeugt den zwischengespeicherten Plan. */
EXEC lab.usp_Qry004CatchAll @CategoryCode = 'RARE',
                            @ResultRowCount = @Rows OUTPUT,
                            @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'BASELINE', @Strategy = 'CATCHALL', @Combination = 'RARE',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Qry004CatchAll @CategoryCode = 'CMMN',
                            @ResultRowCount = @Rows OUTPUT,
                            @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'BASELINE', @Strategy = 'CATCHALL', @Combination = 'COMMON',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Qry004CatchAll @StatusCode = 1,
                            @ResultRowCount = @Rows OUTPUT,
                            @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Qry004Capture @Phase = 'BASELINE', @Strategy = 'CATCHALL', @Combination = 'STATUS',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @RareRows int;
DECLARE @CommonRows int;
DECLARE @StatusRows int;
DECLARE @MaxPlans int;
DECLARE @RareReads bigint;
DECLARE @CommonReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @MaxPlans = MAX(CachedPlanCount)
FROM lab.Qry004Evidence
WHERE Phase = 'BASELINE';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein Cacheeintrag für lab.usp_Qry004CatchAll auswertbar' AS ObservedValue,
           N'objektbezogene Cacheevidenz für alle drei Ausführungen' AS RequiredValue,
           N'Die Cacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @RareRows = MAX(CASE WHEN Combination = 'RARE' THEN ResultRowCount END),
       @CommonRows = MAX(CASE WHEN Combination = 'COMMON' THEN ResultRowCount END),
       @StatusRows = MAX(CASE WHEN Combination = 'STATUS' THEN ResultRowCount END),
       @RareReads = MAX(CASE WHEN Combination = 'RARE' THEN LogicalReads END),
       @CommonReads = MAX(CASE WHEN Combination = 'COMMON' THEN LogicalReads END)
FROM lab.Qry004Evidence
WHERE Phase = 'BASELINE' AND Strategy = 'CATCHALL';

IF @RareRows <> 20 OR @CommonRows <> 19980 OR @StatusRows <> 4000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die Catch-all-Baseline liefert nicht die erwarteten Trefferzahlen.', 1;

IF @MaxPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Für den Catch-all-Querytext wird genau ein zwischengespeicherter Plan erwartet.', 1;

SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Zeilen RARE/COMMON/STATUS=', @RareRows, N'/', @CommonRows, N'/', @StatusRows,
              N'; Cacheeintraege=', @MaxPlans,
              N'; Reads RARE/COMMON=', ISNULL(@RareReads, -1), N'/', ISNULL(@CommonReads, -1)) AS ObservedValue,
       N'ein Plan für drei sehr unterschiedliche Selektivitäten' AS RequiredValue,
       N'Der Catch-all-Querytext bedient alle drei Filterformen mit derselben Planform.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
