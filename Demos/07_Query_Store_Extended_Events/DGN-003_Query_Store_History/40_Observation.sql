SET NOCOUNT ON; SET XACT_ABORT ON;
EXEC sys.sp_query_store_flush_db;
DECLARE @QueryCount int,@PlanCount int,@RuntimeRows int,@WaitRows int=0;
SELECT @QueryCount=COUNT(DISTINCT q.query_id),@PlanCount=COUNT(DISTINCT p.plan_id),@RuntimeRows=COUNT(rs.runtime_stats_id)
FROM sys.query_store_query_text qt JOIN sys.query_store_query q ON q.query_text_id=qt.query_text_id JOIN sys.query_store_plan p ON p.query_id=q.query_id LEFT JOIN sys.query_store_runtime_stats rs ON rs.plan_id=p.plan_id
WHERE qt.query_sql_text LIKE N'%lab.SearchData%GroupId%';
IF OBJECT_ID(N'sys.query_store_wait_stats') IS NOT NULL
 SELECT @WaitRows=COUNT(*) FROM sys.query_store_wait_stats ws JOIN sys.query_store_plan p ON p.plan_id=ws.plan_id JOIN sys.query_store_query q ON q.query_id=p.query_id JOIN sys.query_store_query_text qt ON qt.query_text_id=q.query_text_id WHERE qt.query_sql_text LIKE N'%lab.SearchData%GroupId%';
IF COALESCE(@QueryCount,0)=0 OR COALESCE(@RuntimeRows,0)=0 BEGIN SELECT 1 Sequence,'OBSERVATION' Phase,'QUERY_STORE_EVIDENCE' CheckId,'SKIP' Outcome,'SKIP_EVIDENCE_MISSING' Code,CONCAT(N'Queries=',COALESCE(@QueryCount,0),N'; RuntimeRows=',COALESCE(@RuntimeRows,0)) ObservedValue,N'mindestens eine Query und Runtimezeile' RequiredValue,N'Query Store hat innerhalb des Laufzeitfensters keine belastbare Evidenz geliefert.' Message; PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_EVIDENCE_MISSING'; RETURN; END;
UPDATE lab.QueryStoreEvidence SET QueryCount=@QueryCount,PlanCount=@PlanCount,RuntimeRows=@RuntimeRows,WaitRows=@WaitRows WHERE Phase='DEMONSTRATION';
SELECT @QueryCount QueryCount,@PlanCount PlanCount,@RuntimeRows RuntimeRows,@WaitRows WaitRows;
IF @PlanCount<2 BEGIN SELECT 1 Sequence,'OBSERVATION' Phase,'PLAN_VARIANCE' CheckId,'WARN' Outcome,'WARN_EMPIRICAL_VARIANCE' Code,CONVERT(nvarchar(20),@PlanCount) ObservedValue,N'mehrere Pläne sind möglich, aber nicht garantiert' RequiredValue,N'Die Historie ist vorhanden; der Optimizer hat keine zweite Planform erzeugt.' Message; PRINT 'SQLPERF_SUMMARY|WARN|WARN_EMPIRICAL_VARIANCE'; RETURN; END;
SELECT 1 Sequence,'OBSERVATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Queries=',@QueryCount,N'; Plans=',@PlanCount,N'; Runtime=',@RuntimeRows,N'; Wait=',@WaitRows) ObservedValue,N'Query-, Plan- und Runtime-Historie' RequiredValue,N'Query Store liefert die vorgesehene Historienevidenz.' Message; PRINT 'SQLPERF_SUMMARY|PASS|OK';
