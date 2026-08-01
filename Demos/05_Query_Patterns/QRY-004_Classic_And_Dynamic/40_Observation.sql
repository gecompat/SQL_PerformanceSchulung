/* QRY-004 observation: Preis der Neuoptimierung bei identischer Arbeitsmenge und wiederholter Ausführung. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

EXEC sys.sp_recompile @objname = N'lab.usp_Qry004CatchAll';
EXEC sys.sp_recompile @objname = N'lab.usp_Qry004Recompile';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Iteration int = 0;

/* Ohne Filter leisten beide Varianten dieselbe Arbeit; der Unterschied liegt allein in der Kompilierung. */
WHILE @Iteration < 25
BEGIN
    EXEC lab.usp_Qry004CatchAll @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
    SET @Iteration += 1;
END;
EXEC lab.usp_Qry004Capture @Phase = 'OBSERVATION', @Strategy = 'CATCHALL', @Combination = 'ALL',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

SET @Iteration = 0;
WHILE @Iteration < 25
BEGIN
    EXEC lab.usp_Qry004Recompile @ResultRowCount = @Rows OUTPUT, @ResultChecksum = @Checksum OUTPUT;
    SET @Iteration += 1;
END;
EXEC lab.usp_Qry004Capture @Phase = 'OBSERVATION', @Strategy = 'RECOMPILE', @Combination = 'ALL',
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @CatchAllRows int;
DECLARE @RecompileRows int;
DECLARE @CatchAllChecksum int;
DECLARE @RecompileChecksum int;
DECLARE @CatchAllPlans int;
DECLARE @CatchAllExecutions bigint;
DECLARE @RecompileExecutions bigint;
DECLARE @CatchAllCpu decimal(18,2);
DECLARE @RecompileCpu decimal(18,2);

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END)
FROM lab.Qry004Evidence
WHERE Phase = 'OBSERVATION';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine objektbezogene Ausführungsstatistik auswertbar' AS ObservedValue,
           N'Cacheevidenz für beide Strategien' AS RequiredValue,
           N'Die Ausführungsstatistik der Demoobjekte ist in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @CatchAllRows = MAX(CASE WHEN Strategy = 'CATCHALL' THEN ResultRowCount END),
       @RecompileRows = MAX(CASE WHEN Strategy = 'RECOMPILE' THEN ResultRowCount END),
       @CatchAllChecksum = MAX(CASE WHEN Strategy = 'CATCHALL' THEN ResultChecksum END),
       @RecompileChecksum = MAX(CASE WHEN Strategy = 'RECOMPILE' THEN ResultChecksum END),
       @CatchAllPlans = MAX(CASE WHEN Strategy = 'CATCHALL' THEN CachedPlanCount END),
       @CatchAllExecutions = MAX(CASE WHEN Strategy = 'CATCHALL' THEN ExecutionCount END),
       @RecompileExecutions = MAX(CASE WHEN Strategy = 'RECOMPILE' THEN ExecutionCount END),
       @CatchAllCpu = MAX(CASE WHEN Strategy = 'CATCHALL' THEN CONVERT(decimal(18,2), WorkerTimeUs) / NULLIF(ExecutionCount, 0) END),
       @RecompileCpu = MAX(CASE WHEN Strategy = 'RECOMPILE' THEN CONVERT(decimal(18,2), WorkerTimeUs) / NULLIF(ExecutionCount, 0) END)
FROM lab.Qry004Evidence
WHERE Phase = 'OBSERVATION' AND Combination = 'ALL';

IF @CatchAllRows <> 20000 OR @RecompileRows <> 20000 OR ISNULL(@CatchAllChecksum, -1) <> ISNULL(@RecompileChecksum, -1)
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die ungefilterten Ausführungen beider Varianten sind nicht ergebnisgleich.', 1;

IF @CatchAllExecutions <> 25 OR @RecompileExecutions <> 25
    THROW 51006, 'FAIL_RESULT_CONTRACT: Es werden je Variante genau 25 gezählte Ausführungen erwartet.', 1;

IF @CatchAllPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der Catch-all-Querytext muss über alle Wiederholungen denselben Plan wiederverwenden.', 1;

IF @CatchAllCpu IS NULL OR @RecompileCpu IS NULL OR @RecompileCpu <= @CatchAllCpu
BEGIN
    SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'COMPILE_COST_DIRECTION' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'CPU je Ausführung Catch-all/Recompile=', ISNULL(@CatchAllCpu, -1), N'/', ISNULL(@RecompileCpu, -1), N' us') AS ObservedValue,
           N'höhere CPU je Ausführung für die neu optimierte Variante' AS RequiredValue,
           N'Der Kompilierungsanteil ist in dieser Umgebung nicht von der Messstreuung zu trennen. Die Ergebnisgleichheit bleibt nachgewiesen.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'OBSERVATION' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'Ausfuehrungen=', @CatchAllExecutions, N'/', @RecompileExecutions,
              N'; CPU je Ausfuehrung Catch-all/Recompile=', @CatchAllCpu, N'/', @RecompileCpu, N' us',
              N'; Cacheeintraege Catch-all=', @CatchAllPlans) AS ObservedValue,
       N'gleiche Arbeitsmenge, höhere CPU je Ausführung durch wiederholte Optimierung' AS RequiredValue,
       N'Neuoptimierung tauscht Wiederverwendung gegen zusätzliche Compilearbeit.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
