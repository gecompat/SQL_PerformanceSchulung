/* OPT-017 normalized Actual-DOP, exchange and per-thread evidence. */
SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @Plan xml;
SELECT TOP(1) @Plan=qps.query_plan FROM sys.dm_exec_procedure_stats ps CROSS APPLY sys.dm_exec_query_plan_stats(ps.plan_handle) qps WHERE ps.database_id=DB_ID() AND ps.object_id=OBJECT_ID(N'lab.usp_Opt017Aggregate') ORDER BY ps.last_execution_time DESC;
IF @Plan IS NULL BEGIN SELECT 1 Sequence,'OBSERVATION' Phase,'ACTUAL_PLAN' CheckId,'SKIP' Outcome,'SKIP_EVIDENCE_MISSING' Code,N'kein Last Actual Plan' ObservedValue,N'LAST_QUERY_PLAN_STATS mit Runtime-Plan' RequiredValue,N'Die Kernevidenz ist nicht verfuegbar.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';RETURN;END;
DECLARE @Dop int,@ExchangeCount int;
;WITH XMLNAMESPACES(DEFAULT 'http://schemas.microsoft.com/sqlserver/2004/07/showplan') SELECT @Dop=MAX(T.N.value('(@DegreeOfParallelism)[1]','int')) FROM @Plan.nodes('//QueryPlan')T(N);
;WITH XMLNAMESPACES(DEFAULT 'http://schemas.microsoft.com/sqlserver/2004/07/showplan') SELECT @ExchangeCount=COUNT(*) FROM @Plan.nodes('//RelOp[@LogicalOp="Repartition Streams" or @LogicalOp="Distribute Streams" or @LogicalOp="Gather Streams"]')T(N);
DECLARE @Thread TABLE(ThreadId int,ActualRows bigint);
;WITH XMLNAMESPACES(DEFAULT 'http://schemas.microsoft.com/sqlserver/2004/07/showplan') INSERT @Thread(ThreadId,ActualRows) SELECT T.N.value('(@Thread)[1]','int'),T.N.value('(@ActualRows)[1]','bigint') FROM @Plan.nodes('//RelOp[@LogicalOp="Repartition Streams"]/RunTimeInformation/RunTimeCountersPerThread')T(N) WHERE T.N.value('(@ActualRows)[1]','bigint')>0;
DECLARE @Active int=(SELECT COUNT(*) FROM @Thread),@Min bigint=(SELECT MIN(ActualRows) FROM @Thread),@Max bigint=(SELECT MAX(ActualRows) FROM @Thread),@Ratio decimal(19,4);
SET @Ratio=CASE WHEN @Min>0 THEN CONVERT(decimal(19,4),@Max*1.0/@Min) END;
UPDATE lab.Opt017Evidence SET ActualDop=@Dop,ExchangeCount=@ExchangeCount,ActiveThreads=@Active,MinimumThreadRows=@Min,MaximumThreadRows=@Max,SkewRatio=@Ratio WHERE Phase='SKEW';
IF ISNULL(@Dop,0)<2 OR ISNULL(@ExchangeCount,0)=0 OR ISNULL(@Active,0)<2 BEGIN SELECT 1 Sequence,'OBSERVATION' Phase,'PLAN_SHAPE' CheckId,'SKIP' Outcome,'SKIP_EVIDENCE_MISSING' Code,CONCAT(N'DOP=',COALESCE(CONVERT(nvarchar(20),@Dop),N'NULL'),N'; Exchanges=',@ExchangeCount,N'; Threads=',@Active) ObservedValue,N'Actual DOP >= 2, Exchange und mindestens zwei Threads' RequiredValue,N'Der Optimizer hat die benoetigte parallele Planform nicht erzeugt.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING';RETURN;END;
SELECT 1 Sequence,'OBSERVATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'DOP=',@Dop,N'; Exchanges=',@ExchangeCount,N'; Threads=',@Active,N'; Ratio=',@Ratio) ObservedValue,N'Actual DOP, Exchanges und positive Threadarbeit' RequiredValue,N'Die parallele Kernevidenz ist vorhanden.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
