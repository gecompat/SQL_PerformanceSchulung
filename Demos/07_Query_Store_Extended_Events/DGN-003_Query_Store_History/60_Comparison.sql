SET NOCOUNT ON; SET XACT_ABORT ON;
IF (SELECT COUNT(*) FROM lab.QueryStoreEvidence WHERE Phase IN('BASELINE','DEMONSTRATION'))<>2 THROW 51006,'FAIL_RESULT_CONTRACT: DGN-003-Vergleichsevidenz ist unvollständig.',1;
DECLARE @BaselineRows bigint=(SELECT RowCount FROM lab.QueryStoreEvidence WHERE Phase='BASELINE'),@DemoRows bigint=(SELECT RowCount FROM lab.QueryStoreEvidence WHERE Phase='DEMONSTRATION');
IF @BaselineRows<=0 OR @DemoRows<>45000 THROW 51006,'FAIL_RESULT_CONTRACT: DGN-003-Ausführungsergebnisse sind nicht reproduzierbar.',1;
SELECT Phase,RowCount,ChecksumValue,QueryCount,PlanCount,RuntimeRows,WaitRows FROM lab.QueryStoreEvidence ORDER BY Phase;
SELECT 1 Sequence,'COMPARISON' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'BaselineRows=',@BaselineRows,N'; CommonRows=',@DemoRows) ObservedValue,N'identische Messmethode bei unterschiedlicher Selektivität' RequiredValue,N'Liveausführung und historische Sicht bleiben getrennt interpretierbar.' Message; PRINT 'SQLPERF_SUMMARY|PASS|OK';
