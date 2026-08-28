SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @SessionName sysname=CONVERT(sysname,N'SQLPERF_'+REPLACE('$(DemoId)','-','')+N'_$(RunToken)'),@Sql nvarchar(max);
IF NOT EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName) THROW 51002,'FAIL_STATE: DGN-005-XE-Session fehlt.',1;
IF EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName) BEGIN SET @Sql=N'ALTER EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER STATE=STOP;'; EXEC sys.sp_executesql @Sql; END;
UPDATE lab.XeEvidence SET SessionStopped=1;
SELECT 1 Sequence,'MITIGATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,N'Session gestoppt' ObservedValue,N'reversible Zustandsänderung' RequiredValue,N'Die Telemetrieerfassung wurde beendet.' Message; PRINT 'SQLPERF_SUMMARY|PASS|OK';
