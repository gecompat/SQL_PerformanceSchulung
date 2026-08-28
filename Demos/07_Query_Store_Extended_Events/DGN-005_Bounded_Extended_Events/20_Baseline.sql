SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @SessionName sysname=CONVERT(sysname,N'SQLPERF_'+REPLACE('$(DemoId)','-','')+N'_$(RunToken)');
IF NOT EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName) THROW 51002,'FAIL_STATE: DGN-005-XE-Session läuft nicht.',1;
SELECT 1 Sequence,'BASELINE' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,@SessionName ObservedValue,N'aktive begrenzte Session' RequiredValue,N'Der Ausgangszustand ist bereit.' Message; PRINT 'SQLPERF_SUMMARY|PASS|OK';
