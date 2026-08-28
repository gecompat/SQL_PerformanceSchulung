/* DGN-003 / FWK-001 / FWK-007 / FWK-012 */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),@Expected sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @HasCreate bit=CASE WHEN HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE')=1 OR IS_SRVROLEMEMBER('sysadmin')=1 THEN 1 ELSE 0 END;
IF @DemoId<>'DGN-003' OR @TargetDatabase<>@Expected THROW 51000,'FAIL_CONTRACT: DGN-003-Zielkennung ist ungültig.',1;
IF @Major NOT BETWEEN 15 AND 17 BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'ENGINE_VERSION' CheckId,'SKIP' Outcome,'SKIP_VERSION' Code,CONVERT(nvarchar(20),@Major) ObservedValue,N'15 bis 17' RequiredValue,N'DGN-003 unterstützt SQL Server 2019 bis 2025.' Message; PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION'; RETURN; END;
IF @HasCreate=0 BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'PERMISSION' CheckId,'SKIP' Outcome,'SKIP_PERMISSION' Code,N'CREATE DATABASE fehlt' ObservedValue,N'CREATE ANY DATABASE' RequiredValue,N'Die markergebundene Testdatenbank kann nicht erstellt werden.' Message; PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION'; RETURN; END;
SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Major=',@Major) ObservedValue,N'SQL Server 2019 bis 2025' RequiredValue,N'Preflight bestanden.' Message; PRINT 'SQLPERF_SUMMARY|PASS|OK';
