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

SET NOCOUNT ON;
IF CASE WHEN CONVERT(nvarchar(80),SERVERPROPERTY('ProductVersion'))=N'17.0.5005.3'
 AND TRY_CONVERT(int,SERVERPROPERTY('EngineEdition'))=3
 AND EXISTS(SELECT 1 FROM sys.dm_os_host_info WHERE host_platform=N'Linux'
 AND host_distribution=N'Ubuntu' AND host_release=N'24.04') THEN 1 ELSE 0 END<>1
 THROW 51001,'Build, edition or OS binding missing.',1;
IF DB_ID(N'SQLPERF_LAB_IDX011_$(RunToken)') IS NOT NULL THROW 51001,'Existing database rejected.',1;
CREATE DATABASE [SQLPERF_LAB_IDX011_$(RunToken)];
GO
USE [SQLPERF_LAB_IDX011_$(RunToken)];
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.Project',@value=N'SQL_PerformanceSchulung';
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.ContractVersion',@value=N'1.0';
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.DemoId',@value=N'IDX-011';
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.RunToken',@value=N'$(RunToken)';

IF (SELECT COUNT(*) FROM (VALUES
 (N'SQLPERF.Project',N'SQL_PerformanceSchulung'),
 (N'SQLPERF.ContractVersion',N'1.0'),
 (N'SQLPERF.DemoId',N'IDX-011'),
 (N'SQLPERF.RunToken',N'$(RunToken)')) e(Name,Expected)
 JOIN sys.extended_properties p ON p.name=e.Name AND p.class=0
 AND DATALENGTH(p.name)=DATALENGTH(e.Name)
 AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 AND p.major_id=0 AND p.minor_id=0
 WHERE DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Expected)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=
 CONVERT(varbinary(max),e.Expected))<>4
 THROW 51001,'Full ownership binding lost.',1;

ALTER DATABASE CURRENT SET RECOVERY SIMPLE;
ALTER DATABASE CURRENT SET COMPATIBILITY_LEVEL=170;
ALTER DATABASE CURRENT MODIFY FILE(NAME=N'SQLPERF_LAB_IDX011_$(RunToken)',MAXSIZE=256MB,FILEGROWTH=16MB);
ALTER DATABASE CURRENT MODIFY FILE(NAME=N'SQLPERF_LAB_IDX011_$(RunToken)_log',MAXSIZE=64MB,FILEGROWTH=16MB);
CREATE TABLE dbo.PreviewState(Id int NOT NULL PRIMARY KEY CHECK(Id=1),
 OriginalValue int NOT NULL CHECK(OriginalValue IN(0,1)),RunToken nvarchar(16) NOT NULL,
 MaxDopOriginal int NOT NULL CHECK(MaxDopOriginal=0));
IF (SELECT COUNT(*) FROM sys.database_scoped_configurations WHERE name=N'MAXDOP'
 AND TRY_CONVERT(int,value)=0)<>1 THROW 51003,'MAXDOP baseline outside fixed profile.',1;
INSERT dbo.PreviewState SELECT 1,TRY_CONVERT(int,value),N'$(RunToken)',
 (SELECT TRY_CONVERT(int,value) FROM sys.database_scoped_configurations WHERE name=N'MAXDOP')
 FROM sys.database_scoped_configurations WHERE name=N'PREVIEW_FEATURES';
GO

IF OBJECT_ID(N'dbo.PreviewState',N'U') IS NULL
 THROW 51003,'Persistent preview baseline missing.',1;
IF (SELECT COUNT(*) FROM dbo.PreviewState)<>1
 THROW 51003,'Persistent preview baseline count invalid.',1;
IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE Id=1 AND OriginalValue IN(0,1)
 AND DATALENGTH(RunToken)=DATALENGTH(N'$(RunToken)')
 AND CONVERT(varbinary(max),RunToken)=CONVERT(varbinary(max),N'$(RunToken)'))
 THROW 51003,'Persistent preview baseline invalid.',1;

IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE MaxDopOriginal=0)
 THROW 51003,'Persistent actual MAXDOP baseline invalid.',1;

SELECT CONCAT(N'ANN_BUILD_BASELINE|$(RunToken)|',OriginalValue,N'|',MaxDopOriginal) FROM dbo.PreviewState;

SELECT CONCAT(N'IDX011_DATABASE|$(RunToken)|',DB_ID());
PRINT 'SQLPERF_SUMMARY|PASS|OK';
