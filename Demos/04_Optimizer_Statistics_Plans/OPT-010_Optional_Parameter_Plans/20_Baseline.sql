/* OPT-010 baseline: Optimierung abgeschaltet, der belegte Parameter erzeugt den zwischengespeicherten Plan. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

ALTER DATABASE SCOPED CONFIGURATION SET OPTIONAL_PARAMETER_OPTIMIZATION = OFF;
EXEC sys.sp_recompile @objname = N'lab.usp_Opt010SearchSelectiveFirst';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT010' + N'_MARK_BASELINE';

/* Kompilierungsreihenfolge: der belegte Parameter bestimmt die Planform. */
EXEC lab.usp_Opt010SearchSelectiveFirst @AgentId = 42,
                                        @ResultRowCount = @Rows OUTPUT,
                                        @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'BASELINE', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

/* Derselbe zwischengespeicherte Plan wird für den offenen Parameter wiederverwendet. */
EXEC lab.usp_Opt010SearchSelectiveFirst @AgentId = NULL,
                                        @ResultRowCount = @Rows OUTPUT,
                                        @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'BASELINE', @ParameterLabel = 'OPTIONAL', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @Missing int;
DECLARE @SelectiveRows int;
DECLARE @OptionalRows int;
DECLARE @MaxPlans int;
DECLARE @Dispatchers int;
DECLARE @Variants int;
DECLARE @SelectiveReads bigint;
DECLARE @OptionalReads bigint;

SELECT @Missing = SUM(CASE WHEN EvidenceAvailable = 0 THEN 1 ELSE 0 END),
       @MaxPlans = MAX(CachedPlanCount),
       @Dispatchers = MAX(DispatcherPlanCount),
       @Variants = MAX(VariantPlanCount)
FROM lab.Opt010Evidence
WHERE Phase = 'BASELINE';

IF @Missing IS NULL OR @Missing > 0
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'PLAN_CACHE_EVIDENCE' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'kein markierter Cacheeintrag für lab.usp_Opt010SearchSelectiveFirst auswertbar' AS ObservedValue,
           N'markerbezogene Cacheevidenz für beide Ausführungen' AS RequiredValue,
           N'Die Plancacheattribute des Demoobjekts sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

SELECT @SelectiveRows = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN ResultRowCount END),
       @OptionalRows = MAX(CASE WHEN ParameterLabel = 'OPTIONAL' THEN ResultRowCount END),
       @SelectiveReads = MAX(CASE WHEN ParameterLabel = 'SELECTIVE' THEN LogicalReads END),
       @OptionalReads = MAX(CASE WHEN ParameterLabel = 'OPTIONAL' THEN LogicalReads END)
FROM lab.Opt010Evidence
WHERE Phase = 'BASELINE';

IF @SelectiveRows <> 50 OR @OptionalRows <> 100000
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die OPT-010-Baseline liefert nicht die vereinbarten Trefferzahlen.', 1;

IF @MaxPlans <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Für den markierten Querytext wird in der Baseline genau ein zwischengespeicherter Plan erwartet.', 1;

IF @Dispatchers <> 0 OR @Variants <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Bei abgeschalteter Optimierung darf weder ein Dispatcherplan noch eine Queryvariante entstehen.', 1;

IF @SelectiveReads IS NULL OR @OptionalReads IS NULL
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'LOGICAL_READS' AS CheckId,
           'SKIP' AS Outcome, 'SKIP_EVIDENCE_MISSING' AS Code,
           N'keine Lesezahlen im Plancache' AS ObservedValue,
           N'logische Lesevorgänge je Parameterbelegung' AS RequiredValue,
           N'Die Lesekosten sind in dieser Umgebung nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';
    RETURN;
END;

/*
   Kernaussage: eine einzige Planform muss fuer beide Parameterzustaende gueltig bleiben.
   Der belegte Parameter zahlt deshalb den Aufwand des offenen Parameters mit,
   obwohl er nur 50 von 100 000 Zeilen trifft.
*/
IF @SelectiveReads * 2 < @OptionalReads
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'OPTIONAL_PREDICATE_COST' AS CheckId,
           'WARN' AS Outcome, 'WARN_EMPIRICAL_VARIANCE' AS Code,
           CONCAT(N'belegt=', @SelectiveReads, N'; offen=', @OptionalReads) AS ObservedValue,
           N'vergleichbare Lesekosten für beide Parameterbelegungen' AS RequiredValue,
           N'Der Optimierer hat hier keine gemeinsame Planform mit voller Prüfbreite erzeugt; die Aussage ist nicht belegt.' AS Message;
    PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';
    RETURN;
END;

SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       CONCAT(N'ein Plan; Lesevorgänge belegt=', @SelectiveReads,
              N', offen=', @OptionalReads,
              N'; Dispatcher=0; Varianten=0') AS ObservedValue,
       N'ein wiederverwendeter Plan mit vergleichbaren Lesekosten' AS RequiredValue,
       N'Der belegte Parameter zahlt die Kosten des offenen Parameters mit, obwohl er nur 50 Zeilen trifft.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
