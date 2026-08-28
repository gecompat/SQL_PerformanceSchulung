SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @SessionName sysname=CONVERT(sysname,N'SQLPERF_'+REPLACE('$(DemoId)','-','')+N'_$(RunToken)'),@Events int=(SELECT EventCount FROM lab.XeEvidence),@Stopped bit=(SELECT SessionStopped FROM lab.XeEvidence);
IF COALESCE(@Events,0)<=0 OR @Stopped<>1 THROW 51006,'FAIL_RESULT_CONTRACT: DGN-005-Evidenz- oder Stopvertrag ist unvollständig.',1;
IF EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName) THROW 51002,'FAIL_STATE: DGN-005-XE-Session läuft nach Stop weiter.',1;
SELECT 1 Sequence,'COMPARISON' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Events=',@Events,N'; Stopped=',@Stopped) ObservedValue,N'Evidenz vorhanden und Erfassung beendet' RequiredValue,N'Der begrenzte Lifecycle ist vollständig.' Message; PRINT 'SQLPERF_SUMMARY|PASS|OK';
