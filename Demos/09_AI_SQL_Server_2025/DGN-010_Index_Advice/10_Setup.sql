/* DGN-010: begrenzte synthetische Quellen- und Indexmessung. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'DGN-010')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_DGN010_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_DGN010_'+@RawRun)
 THROW 51000,'FAIL_CONTRACT: Vollstaendige Demo-/Run-/Zielbindung verletzt.',1;
DECLARE @DemoId varchar(7)=CONVERT(varchar(7),@RawDemo),@RunToken varchar(16)=CONVERT(varchar(16),@RawRun),@TargetDatabase sysname=CONVERT(sysname,@RawTarget);
DECLARE @Sql nvarchar(max),@Matches int;
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @M=COUNT(*) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties p
 JOIN (VALUES(N''SQLPERF.Project'',N''SQL_PerformanceSchulung''),
 (N''SQLPERF.ContractVersion'',N''1.0''),(N''SQLPERF.DemoId'',CONVERT(nvarchar(max),@D)),
 (N''SQLPERF.RunToken'',CONVERT(nvarchar(max),@R))) e(Name,Value)
 ON DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 WHERE p.class=0 AND p.major_id=0 AND p.minor_id=0
 AND DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Value)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=CONVERT(varbinary(max),e.Value);';
 EXEC sys.sp_executesql @Sql,N'@D varchar(7),@R varchar(16),@M int OUTPUT',@D=@DemoId,@R=@RunToken,@M=@Matches OUTPUT;
 IF @Matches<>4 THROW 51004,'FAIL_STATE: Vollstaendige bytegenaue Eigentumsmarker fehlen.',1;
END;
IF DATALENGTH(@RawRun)<>DATALENGTH(N'LOCAL') OR CONVERT(varbinary(max),@RawRun)<>CONVERT(varbinary(max),N'LOCAL') THROW 51000,'FAIL_CONTRACT: Fixed LOCAL setup required.',1;
IF DB_ID(N'SQLPERF_LAB_DGN010_LOCAL') IS NULL
BEGIN
 CREATE DATABASE SQLPERF_LAB_DGN010_LOCAL;
 EXEC(N'USE SQLPERF_LAB_DGN010_LOCAL;
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''DGN-010'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=N''LOCAL'';');
END;
GO
USE SQLPERF_LAB_DGN010_LOCAL;
/* DGN-010: begrenzte synthetische Quellen- und Indexmessung. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'DGN-010')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_DGN010_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_DGN010_'+@RawRun)
 THROW 51000,'FAIL_CONTRACT: Vollstaendige Demo-/Run-/Zielbindung verletzt.',1;
DECLARE @DemoId varchar(7)=CONVERT(varchar(7),@RawDemo),@RunToken varchar(16)=CONVERT(varchar(16),@RawRun),@TargetDatabase sysname=CONVERT(sysname,@RawTarget);
DECLARE @Sql nvarchar(max),@Matches int;
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @M=COUNT(*) FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties p
 JOIN (VALUES(N''SQLPERF.Project'',N''SQL_PerformanceSchulung''),
 (N''SQLPERF.ContractVersion'',N''1.0''),(N''SQLPERF.DemoId'',CONVERT(nvarchar(max),@D)),
 (N''SQLPERF.RunToken'',CONVERT(nvarchar(max),@R))) e(Name,Value)
 ON DATALENGTH(p.name)=DATALENGTH(e.Name) AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 WHERE p.class=0 AND p.major_id=0 AND p.minor_id=0
 AND DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Value)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=CONVERT(varbinary(max),e.Value);';
 EXEC sys.sp_executesql @Sql,N'@D varchar(7),@R varchar(16),@M int OUTPUT',@D=@DemoId,@R=@RunToken,@M=@Matches OUTPUT;
 IF @Matches<>4 THROW 51004,'FAIL_STATE: Vollstaendige bytegenaue Eigentumsmarker fehlen.',1;
END;
IF DATALENGTH(DB_NAME())<>DATALENGTH(@TargetDatabase) OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),@TargetDatabase) OR DB_ID(@TargetDatabase) IS NULL THROW 51004,'FAIL_STATE: Falscher Datenbankkontext.',1;

ALTER DATABASE CURRENT SET COMPATIBILITY_LEVEL=170;
ALTER DATABASE CURRENT SET RECOVERY SIMPLE;
ALTER DATABASE CURRENT MODIFY FILE(NAME=N'SQLPERF_LAB_DGN010_LOCAL',MAXSIZE=256MB,FILEGROWTH=16MB);
ALTER DATABASE CURRENT MODIFY FILE(NAME=N'SQLPERF_LAB_DGN010_LOCAL_log',MAXSIZE=64MB,FILEGROWTH=16MB);
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
GO
IF OBJECT_ID(N'lab.SourceRows') IS NULL
 CREATE TABLE lab.SourceRows(Id int NOT NULL CONSTRAINT DGN010_OwnPK PRIMARY KEY CLUSTERED,Value int NOT NULL,Payload varchar(100) NOT NULL);
IF EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND name=N'DGN010_OwnCandidate')
 DROP INDEX DGN010_OwnCandidate ON lab.SourceRows;
DELETE FROM lab.SourceRows;
INSERT lab.SourceRows SELECT value,value*3,REPLICATE('F',100) FROM GENERATE_SERIES(1,1000);
IF USER_ID(N'DGN010_reader') IS NULL CREATE USER DGN010_reader WITHOUT LOGIN;
GRANT SELECT ON OBJECT::lab.SourceRows TO DGN010_reader;
SELECT 'SQLPERF_SUMMARY|PASS|OK';
