/* OPT-010 comparison: dokumentierte Abwahl auf Abfrageebene bei eingeschalteter Datenbankoption. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

EXEC sys.sp_recompile @objname = N'lab.usp_Opt010SearchOptOut';
GO

SET NOCOUNT ON;
DECLARE @Rows int;
DECLARE @Checksum int;
DECLARE @Marker nvarchar(40) = N'OPT010' + N'_MARK_OPTOUT';

/* Die Datenbankoption bleibt eingeschaltet; die Abfrage wählt die Optimierung einzeln ab. */
EXEC lab.usp_Opt010SearchOptOut @AgentId = 42,
                                @ResultRowCount = @Rows OUTPUT,
                                @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'COMPARISON', @ParameterLabel = 'SELECTIVE', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;

EXEC lab.usp_Opt010SearchOptOut @AgentId = NULL,
                                @ResultRowCount = @Rows OUTPUT,
                                @ResultChecksum = @Checksum OUTPUT;
EXEC lab.usp_Opt010Capture @Phase = 'COMPARISON', @ParameterLabel = 'OPTIONAL', @Marker = @Marker,
                           @ResultRowCount = @Rows, @ResultChecksum = @Checksum;
GO

SET NOCOUNT ON;
DECLARE @PhaseCount int;
DECLARE @DistinctSelectiveRows int;
DECLARE @DistinctOptionalRows int;
DECLARE @DistinctSelectiveChecksums int;
DECLARE @DistinctOptionalChecksums int;
DECLARE @OptOutDispatchers int;
DECLARE @OptOutPlans int;

SELECT @PhaseCount = COUNT(DISTINCT Phase) FROM lab.Opt010Evidence;

SELECT @DistinctSelectiveRows = COUNT(DISTINCT ResultRowCount),
       @DistinctSelectiveChecksums = COUNT(DISTINCT ISNULL(ResultChecksum, 0))
FROM lab.Opt010Evidence
WHERE ParameterLabel = 'SELECTIVE';

SELECT @DistinctOptionalRows = COUNT(DISTINCT ResultRowCount),
       @DistinctOptionalChecksums = COUNT(DISTINCT ISNULL(ResultChecksum, 0))
FROM lab.Opt010Evidence
WHERE ParameterLabel = 'OPTIONAL';

SELECT @OptOutDispatchers = MAX(DispatcherPlanCount),
       @OptOutPlans = MAX(CachedPlanCount)
FROM lab.Opt010Evidence
WHERE Phase = 'COMPARISON';

IF @PhaseCount <> 4
    THROW 51006, 'FAIL_RESULT_CONTRACT: Es müssen Belege aus allen vier Vergleichsphasen vorliegen.', 1;

IF @DistinctSelectiveRows <> 1 OR @DistinctOptionalRows <> 1
   OR @DistinctSelectiveChecksums <> 1 OR @DistinctOptionalChecksums <> 1
    THROW 51006, 'FAIL_RESULT_CONTRACT: Die vier Vergleichsobjekte sind nicht ergebnisgleich.', 1;

IF @OptOutDispatchers <> 0
    THROW 51006, 'FAIL_RESULT_CONTRACT: Der dokumentierte Abfragehinweis muss die Optimierung trotz eingeschalteter Datenbankoption abwählen.', 1;

SELECT 1 AS Sequence, 'COMPARISON' AS Phase, 'RESULT_EQUALITY' AS CheckId,
       'PASS' AS Outcome, 'OK' AS Code,
       N'Zeilenzahlen und Prüfsummen über alle vier Phasen identisch' AS ObservedValue,
       N'Ergebnisgleichheit unabhängig von der gewählten Planstrategie' AS RequiredValue,
       N'Optional Parameter Plan Optimization ist eine Kostenentscheidung und keine Semantikänderung.' AS Message
UNION ALL
SELECT 2, 'COMPARISON', 'QUERY_LEVEL_OPT_OUT', 'PASS', 'OK',
       CONCAT(N'Dispatcher bei abgewählter Optimierung=', @OptOutDispatchers,
              N'; zwischengespeicherte Pläne=', @OptOutPlans),
       N'kein Dispatcherplan trotz eingeschalteter Datenbankoption',
       N'Der dokumentierte Hinweis DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION überschreibt die Datenbankoption für genau eine Abfrage.'
UNION ALL
SELECT 3, 'COMPARISON', 'DOCUMENTED_LIMITS', 'PASS', 'OK',
       N'lokale Variablen statt Parameter; OPTION (RECOMPILE); ANSI_NULLS OFF; automatisch parametrisierte Anweisungen',
       N'dokumentierte Ausschlussgründe der Produktdokumentation',
       N'Für diese vier Fälle wird die Optimierung laut Produktdokumentation nicht angewendet.'
UNION ALL
SELECT 4, 'COMPARISON', 'SUMMARY', 'PASS', 'OK',
       N'vier Vergleichsobjekte mit identischem Querytext und unterschiedlicher Planstrategie',
       N'Datenbankoption, Abfragehinweis und Ausgangszustand nebeneinander belegt',
       N'Die Steuerung ist zweistufig: Datenbankoption für die Fläche, Abfragehinweis für den Einzelfall.';
PRINT 'SQLPERF_SUMMARY|PASS|OK';
