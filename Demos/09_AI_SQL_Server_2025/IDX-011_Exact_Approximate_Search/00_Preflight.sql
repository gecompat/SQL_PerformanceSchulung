/* IDX-011: gebundenes DEC-074-Profil; eigene synthetische Datenbank. */
SET NOCOUNT ON;
IF DATALENGTH(N'$(DemoId)')<>DATALENGTH(N'IDX-011')
 OR CONVERT(varbinary(max),N'$(DemoId)')<>CONVERT(varbinary(max),N'IDX-011')
 OR DATALENGTH(N'$(RunToken)')<>32 OR N'$(RunToken)' COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-F0-9]%'
 OR DATALENGTH(N'$(TargetDatabase)')<>DATALENGTH(N'SQLPERF_LAB_IDX011_$(RunToken)')
 OR CONVERT(varbinary(max),N'$(TargetDatabase)')<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX011_$(RunToken)')
 THROW 51000,'FAIL_CONTRACT: Vollständige Demo-/Token-/DB-Bindung fehlt.',1;
IF DATALENGTH(N'$(ConfirmIsolatedLab)')<>2 OR CONVERT(varbinary(max),N'$(ConfirmIsolatedLab)')<>CONVERT(varbinary(max),N'1')
 OR DATALENGTH(N'$(HighImpactConfirmed)')<>2 OR CONVERT(varbinary(max),N'$(HighImpactConfirmed)')<>CONVERT(varbinary(max),N'1')
 OR COALESCE(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),-1)<>300
 THROW 51000,'FAIL_SAFETY: YELLOW-Bestätigung und festes Laufbudget fehlen.',1;


DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
IF @Major IN(15,16) BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';RETURN;END;
IF @Major IS NULL THROW 51000,'FAIL_CONTRACT: Tatsächliche Version unbekannt.',1;
IF @Major<>17 BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_VERSION';RETURN;END;
IF CONVERT(varbinary(max),CONVERT(nvarchar(max),SERVERPROPERTY('ProductVersion')))<>CONVERT(varbinary(max),N'17.0.5005.3')
 OR TRY_CONVERT(int,SERVERPROPERTY('EngineEdition'))<>3
 OR NOT EXISTS(SELECT 1 FROM sys.dm_os_host_info WHERE host_platform=N'Linux'
 AND host_distribution=N'Ubuntu' AND host_release=N'24.04')
BEGIN PRINT 'IDX011_DETAIL|PROFILE_UNQUALIFIED';PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_CONFIGURATION';RETURN;END;
IF COALESCE(HAS_PERMS_BY_NAME(NULL,NULL,'CREATE ANY DATABASE'),0)<>1
 AND COALESCE(HAS_PERMS_BY_NAME(N'master','DATABASE','CREATE DATABASE'),0)<>1
BEGIN PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_PERMISSION';RETURN;END;
IF DB_ID(N'$(TargetDatabase)') IS NOT NULL THROW 51004,'FAIL_STATE: Frische eigene DB erforderlich.',1;
PRINT 'IDX011_DETAIL|GENERATION_UNKNOWN|DEC_074';
PRINT 'SQLPERF_SUMMARY|WARN|WARN_OPTIONAL_EVIDENCE_SKIPPED';
