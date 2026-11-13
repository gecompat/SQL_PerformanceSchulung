/* Five paired measurements; raw FWK-004 values stay bound to variant and pair. */
SET NOCOUNT ON;
SET XACT_ABORT ON;
DECLARE @RunToken varchar(20)='$(RunToken)';
DECLARE @Captured table
(
    PairNumber int NOT NULL,
    ExecutionOrder int NOT NULL,
    Variant varchar(12) NOT NULL,
    Phase varchar(20) NOT NULL,
    MeasurementRunId uniqueidentifier NOT NULL,
    PathCount bigint NOT NULL
);
DECLARE @Pair int=1,@Order int,@Variant varchar(12),@Phase varchar(20),@MeasurementRunId uniqueidentifier,@PathCount bigint;

/* One excluded warm-up per variant; statistics are not cleared between variants. */
EXEC lab.USP_Qry023MeasureVariant @Variant='GRAPH',@Phase='WARMUP',@Iteration=1,@RunToken=@RunToken,
     @MeasurementRunId=@MeasurementRunId OUTPUT,@PathCount=@PathCount OUTPUT;
IF @PathCount<>10000 THROW 51006,'FAIL_RESULT_CONTRACT: Graph-Warm-up lieferte nicht 10.000 Pfade.',1;
EXEC lab.USP_Qry023MeasureVariant @Variant='RELATIONAL',@Phase='WARMUP',@Iteration=1,@RunToken=@RunToken,
     @MeasurementRunId=@MeasurementRunId OUTPUT,@PathCount=@PathCount OUTPUT;
IF @PathCount<>10000 THROW 51006,'FAIL_RESULT_CONTRACT: Relational-Warm-up lieferte nicht 10.000 Pfade.',1;

WHILE @Pair<=5
BEGIN
    SET @Order=1;
    WHILE @Order<=2
    BEGIN
        SET @Variant=CASE WHEN (@Pair%2=1 AND @Order=1) OR (@Pair%2=0 AND @Order=2) THEN 'GRAPH' ELSE 'RELATIONAL' END;
        SET @Phase=CASE WHEN @Variant='GRAPH' THEN 'COMPARISON' ELSE 'BASELINE' END;
        SET @MeasurementRunId=NULL;
        SET @PathCount=NULL;
        EXEC lab.USP_Qry023MeasureVariant @Variant=@Variant,@Phase=@Phase,@Iteration=@Pair,@RunToken=@RunToken,
             @MeasurementRunId=@MeasurementRunId OUTPUT,@PathCount=@PathCount OUTPUT;
        IF @PathCount<>10000 OR @MeasurementRunId IS NULL
            THROW 51006,'FAIL_RESULT_CONTRACT: Eine Messwiederholung lieferte kein gültiges Ergebnis oder keine gebundene Messungs-ID.',1;
        INSERT @Captured(PairNumber,ExecutionOrder,Variant,Phase,MeasurementRunId,PathCount)
        VALUES(@Pair,@Order,@Variant,@Phase,@MeasurementRunId,@PathCount);
        SET @Order+=1;
    END;
    SET @Pair+=1;
END;

IF (SELECT COUNT_BIG(*) FROM @Captured)<>10
    THROW 51002,'FAIL_STATE: Die QRY-023-Messreihe enthält nicht genau zehn Variantenläufe.',1;
IF EXISTS
(
    SELECT 1
    FROM @Captured AS c
    LEFT JOIN lab.MeasurementRun AS m ON m.MeasurementRunId=c.MeasurementRunId
    WHERE m.MeasurementRunId IS NULL OR m.EndedAtUtc IS NULL OR m.OverallOutcome<>'PASS'
       OR m.CpuMs IS NULL OR m.LogicalReads IS NULL OR m.Reads IS NULL
       OR m.Writes IS NULL OR m.ElapsedMs IS NULL
)
    THROW 51003,'FAIL_EXECUTION: Mindestens ein Messlauf besitzt nicht alle vollständigen FWK-004-Messwertdeltas.',1;

SELECT c.PairNumber,c.ExecutionOrder,c.Variant,c.Phase,c.PathCount,
       m.CpuMs,m.LogicalReads,m.Reads,m.Writes,m.ElapsedMs,m.OverallOutcome,m.OverallCode
FROM @Captured AS c
JOIN lab.MeasurementRun AS m ON m.MeasurementRunId=c.MeasurementRunId
ORDER BY c.PairNumber,c.ExecutionOrder;

;WITH Paired AS
(
    SELECT b.PairNumber,
           CpuDeltaMs=CONVERT(float,cRun.CpuMs-bRun.CpuMs),
           LogicalReadDelta=CONVERT(float,cRun.LogicalReads-bRun.LogicalReads),
           ReadDelta=CONVERT(float,cRun.Reads-bRun.Reads),
           WriteDelta=CONVERT(float,cRun.Writes-bRun.Writes),
           ElapsedDeltaMs=CONVERT(float,cRun.ElapsedMs-bRun.ElapsedMs)
    FROM @Captured AS b
    JOIN lab.MeasurementRun AS bRun ON bRun.MeasurementRunId=b.MeasurementRunId
    JOIN @Captured AS c ON c.PairNumber=b.PairNumber
    JOIN lab.MeasurementRun AS cRun ON cRun.MeasurementRunId=c.MeasurementRunId
    WHERE b.Variant='RELATIONAL' AND c.Variant='GRAPH'
), DeltaRows AS
(
    SELECT PairNumber,Metric='CPU_MS',Delta=CpuDeltaMs FROM Paired
    UNION ALL SELECT PairNumber,'LOGICAL_READS',LogicalReadDelta FROM Paired
    UNION ALL SELECT PairNumber,'READS',ReadDelta FROM Paired
    UNION ALL SELECT PairNumber,'WRITES',WriteDelta FROM Paired
    UNION ALL SELECT PairNumber,'ELAPSED_MS',ElapsedDeltaMs FROM Paired
)
SELECT DISTINCT Metric,
       PairCount=COUNT(*) OVER(PARTITION BY Metric),
       MedianDelta=PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY Delta) OVER(PARTITION BY Metric),
       MinimumDelta=MIN(Delta) OVER(PARTITION BY Metric),
       MaximumDelta=MAX(Delta) OVER(PARTITION BY Metric),
       Spread=MAX(Delta) OVER(PARTITION BY Metric)-MIN(Delta) OVER(PARTITION BY Metric)
FROM DeltaRows
ORDER BY Metric;

SELECT 1 AS Sequence,'MEASUREMENT' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'5 gepaarte Läufe; BASELINE=relational; COMPARISON=Graph; AB/BA alterniert; Warm-up ausgeschlossen' AS ObservedValue,
       N'alle Ergebnisanzahlen=10.000; fünf Metriken mit Rohwerten und Median/Streuung der gepaarten Deltas sichtbar' AS RequiredValue,
       N'Die Messreihe enthält keine Performance-Schwelle oder allgemeine Leistungsrangfolge.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
