/* OPT-017 compare result equivalence and retained skew evidence. */
SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @BalancedRows bigint,@SkewRows bigint,@SerialRows bigint,@BalancedMeasure bigint,@SkewMeasure bigint,@SerialMeasure bigint,@SkewChecksum int,@SerialChecksum int,@Ratio decimal(19,4),@Dop int,@Exchanges int;
SELECT @BalancedRows=ResultRows,@BalancedMeasure=ResultMeasure FROM lab.Opt017Evidence WHERE Phase='BALANCED';
SELECT @SkewRows=ResultRows,@SkewMeasure=ResultMeasure,@SkewChecksum=ResultChecksum,@Ratio=SkewRatio,@Dop=ActualDop,@Exchanges=ExchangeCount FROM lab.Opt017Evidence WHERE Phase='SKEW';
SELECT @SerialRows=ResultRows,@SerialMeasure=ResultMeasure,@SerialChecksum=ResultChecksum FROM lab.Opt017Evidence WHERE Phase='SERIAL';
IF @BalancedRows IS NULL OR @SkewRows IS NULL OR @SerialRows IS NULL THROW 51002,'FAIL_STATE: OPT-017-Evidenz ist unvollstaendig.',1;
IF @BalancedRows<>@SkewRows OR @SkewRows<>@SerialRows OR @BalancedMeasure<>@SkewMeasure OR @SkewMeasure<>@SerialMeasure OR @SkewChecksum<>@SerialChecksum THROW 51006,'FAIL_RESULT_CONTRACT: Ergebnisgleichheit ist verletzt.',1;
SELECT Phase,ProfileCode,RequestedDop,ActualDop,ExchangeCount,ActiveThreads,MinimumThreadRows,MaximumThreadRows,SkewRatio,ResultChecksum,ResultRows,ResultMeasure FROM lab.Opt017Evidence ORDER BY CASE Phase WHEN 'BALANCED' THEN 1 WHEN 'SKEW' THEN 2 ELSE 3 END;
IF @Ratio IS NULL OR @Ratio<=1 BEGIN SELECT 1 Sequence,'COMPARISON' Phase,'THREAD_SKEW' CheckId,'WARN' Outcome,'WARN_EMPIRICAL_VARIANCE' Code,CONCAT(N'DOP=',@Dop,N'; Exchanges=',@Exchanges,N'; Ratio=',COALESCE(CONVERT(nvarchar(30),@Ratio),N'NULL')) ObservedValue,N'positive ungleiche Threadverteilung; keine universelle Schwelle' RequiredValue,N'Die Planform ist parallel, die Skew-Differenz aber empirisch nicht deutlich.' Message;PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE';RETURN;END;
SELECT 1 Sequence,'COMPARISON' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'DOP=',@Dop,N'; Exchanges=',@Exchanges,N'; SkewRatio=',@Ratio,N'; Rows=',@SkewRows) ObservedValue,N'parallele Kernevidenz, ungleiche Threadarbeit und ergebnisgleiche serielle Gegenprobe' RequiredValue,N'OPT-017 belegt Parallel Skew ohne eine pauschale DOP-Empfehlung.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
