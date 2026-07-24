/* OPT-013 observation: compare equal results and the last completed spill counters. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @BaselineChecksum int,@ProblemChecksum int;
DECLARE @BaselineSpills bigint,@ProblemSpills bigint;
DECLARE @BaselineSort bit,@ProblemSort bit;

SELECT @BaselineChecksum=ResultChecksum,@BaselineSpills=LastSpills,@BaselineSort=PlanHasSort
FROM lab.SpillEvidence WHERE Phase='BASELINE';
SELECT @ProblemChecksum=ResultChecksum,@ProblemSpills=LastSpills,@ProblemSort=PlanHasSort
FROM lab.SpillEvidence WHERE Phase='PROBLEM';

IF @BaselineChecksum IS NULL OR @ProblemChecksum IS NULL
    THROW 51002,'FAIL_STATE: OPT-013-Baseline oder Problem-Evidenz fehlt.',1;
IF @BaselineChecksum<>@ProblemChecksum
    THROW 51006,'FAIL_RESULT_CONTRACT: Baseline und Problemzustand liefern unterschiedliche fachliche Ergebnisse.',1;
IF @BaselineSpills<>0 OR @ProblemSpills<=0 OR @BaselineSort<>1 OR @ProblemSort<>1
    THROW 51006,'FAIL_RESULT_CONTRACT: Die erwartete Spill-Richtung 0 zu positiv ist nicht belegt.',1;

SELECT Phase,ResultChecksum,LastSpills,PlanHasSort,CapturedAtUtc
FROM lab.SpillEvidence
ORDER BY CASE Phase WHEN 'BASELINE' THEN 1 ELSE 2 END;

SELECT 1 Sequence,'OBSERVATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       CONCAT(N'Checksumgleichheit=1; BaselineSpills=',@BaselineSpills,N'; ProblemSpills=',@ProblemSpills) ObservedValue,
       N'gleiches Ergebnis; Sort in beiden Plänen; last_spills 0 zu positiv' RequiredValue,
       N'Der Spill ist als Runtime-Ereignis des konkreten Sortoperators bestätigt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
