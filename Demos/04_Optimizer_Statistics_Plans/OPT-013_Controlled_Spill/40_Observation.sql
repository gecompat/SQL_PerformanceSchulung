/* OPT-013 observation: correlate identical results, statistics state and spill counters. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @BaselineChecksum int,@ProblemChecksum int;
DECLARE @BaselineSpills bigint,@ProblemSpills bigint;
DECLARE @BaselineSort bit,@ProblemSort bit;
DECLARE @BaselineStatsRows bigint,@ProblemStatsRows bigint;
DECLARE @BaselineModifications bigint,@ProblemModifications bigint;
DECLARE @BaselineActualRows bigint,@ProblemActualRows bigint;

SELECT
    @BaselineChecksum=ResultChecksum,
    @BaselineSpills=LastSpills,
    @BaselineSort=PlanHasSort,
    @BaselineStatsRows=StatisticsRows,
    @BaselineModifications=ModificationCounter,
    @BaselineActualRows=ActualFilteredRows
FROM lab.SpillEvidence
WHERE Phase='BASELINE';

SELECT
    @ProblemChecksum=ResultChecksum,
    @ProblemSpills=LastSpills,
    @ProblemSort=PlanHasSort,
    @ProblemStatsRows=StatisticsRows,
    @ProblemModifications=ModificationCounter,
    @ProblemActualRows=ActualFilteredRows
FROM lab.SpillEvidence
WHERE Phase='PROBLEM';

IF @BaselineChecksum IS NULL OR @ProblemChecksum IS NULL
    THROW 51002,'FAIL_STATE: OPT-013-Baseline oder Problem-Evidenz fehlt.',1;
IF @BaselineChecksum<>@ProblemChecksum OR @BaselineActualRows<>299000 OR @ProblemActualRows<>299000
    THROW 51006,'FAIL_RESULT_CONTRACT: Baseline und Problemzustand liefern nicht dieselbe Ergebnismenge.',1;
IF @BaselineStatsRows<>300000 OR @BaselineModifications<>0 OR @BaselineSpills<>0 OR @BaselineSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Die Baseline besitzt nicht die erwartete aktuelle Statistik ohne Spill.',1;
IF @ProblemStatsRows<>1000 OR @ProblemModifications<299000 OR @ProblemSpills<=0 OR @ProblemSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Der Problemzustand belegt keine veraltete Statistik mit Sort-Spill.',1;

SELECT
    Phase,ResultChecksum,LastSpills,PlanHasSort,StatisticsRows,StatisticsRowsSampled,
    ModificationCounter,ActualFilteredRows,CapturedAtUtc
FROM lab.SpillEvidence
ORDER BY CASE Phase WHEN 'BASELINE' THEN 1 ELSE 2 END;

SELECT 1 Sequence,'OBSERVATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'ActualRows=',@ProblemActualRows,N'; StatsRows=',@ProblemStatsRows,
              N'; Modifications=',@ProblemModifications,N'; Spills=',@ProblemSpills) ObservedValue,
       N'gleiche 299000 Zeilen; Statistik 300000/0 zu 1000/299000; last_spills 0 zu positiv' RequiredValue,
       N'Der Sort-Spill ist gemeinsam mit dem kontrolliert veralteten Statistikzustand belegt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
