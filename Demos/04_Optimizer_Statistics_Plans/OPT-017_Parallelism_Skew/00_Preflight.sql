/* OPT-017 / FWK-001 / FWK-008 / FWK-012 */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @DemoId varchar(7)='$(DemoId)',@RunToken varchar(20)='$(RunToken)',@TargetDatabase sysname=N'$(TargetDatabase)';
DECLARE @Expected sysname=CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken);
DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion')),@Confirm bit=$(ConfirmIsolatedLab),@Runtime int=$(MaximumRuntimeSeconds);
DECLARE @Cpu int=(SELECT COUNT(*) FROM sys.dm_os_schedulers WHERE status=N'VISIBLE ONLINE' AND scheduler_id<1048576);
DECLARE @ConfiguredDop int=(SELECT CONVERT(int,value_in_use) FROM sys.configurations WHERE name=N'max degree of parallelism');
DECLARE @EffectiveDop int=CASE WHEN @ConfiguredDop=0 OR @ConfiguredDop>@Cpu THEN @Cpu ELSE @ConfiguredDop END;
DECLARE @HasCreate bit=CASE WHEN HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE')=1 OR HAS_PERMS_BY_NAME(NULL,NULL,'ALTER ANY DATABASE')=1 OR IS_SRVROLEMEMBER('sysadmin')=1 THEN 1 ELSE 0 END;

IF @DemoId<>'OPT-017' OR @TargetDatabase<>@Expected THROW 51000,'FAIL_CONTRACT: OPT-017-Zielkennung ist ungueltig.',1;
IF @Major NOT BETWEEN 15 AND 17 BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'ENGINE_VERSION' CheckId,'SKIP' Outcome,'SKIP_VERSION' Code,CONVERT(nvarchar(20),@Major) ObservedValue,N'15 bis 17' RequiredValue,N'OPT-017 unterstuetzt SQL Server 2019 bis 2025.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';RETURN;END;
IF @HasCreate=0 BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'PERMISSION' CheckId,'SKIP' Outcome,'SKIP_PERMISSION' Code,N'CREATE DATABASE fehlt' ObservedValue,N'markergebundene Testdatenbank' RequiredValue,N'Die isolierte Demo kann nicht aufgebaut werden.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';RETURN;END;
IF @Cpu<4 OR @EffectiveDop<2 BEGIN SELECT 1 Sequence,'PREFLIGHT' Phase,'PARALLEL_PROFILE' CheckId,'SKIP' Outcome,'SKIP_RESOURCE_PROFILE' Code,CONCAT(N'VisibleCpu=',@Cpu,N'; EffectiveDop=',@EffectiveDop) ObservedValue,N'mindestens 4 sichtbare Kerne und effektive DOP >= 2' RequiredValue,N'Das PARALLEL-Profil reicht fuer Kernevidenz nicht aus.' Message;PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_RESOURCE_PROFILE';RETURN;END;
IF @Confirm<>1 OR @Runtime<=0 THROW 51001,'FAIL_SAFETY: OPT-017 benoetigt ein bestaetigtes isoliertes Lab und ein positives Zeitbudget.',1;

SELECT 1 Sequence,'PREFLIGHT' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Major=',@Major,N'; VisibleCpu=',@Cpu,N'; EffectiveDop=',@EffectiveDop,N'; Runtime=',@Runtime) ObservedValue,N'YELLOW; isoliertes Lab; mindestens vier Kerne; begrenztes Zeitbudget' RequiredValue,N'Das PARALLEL-Profil ist freigegeben.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
