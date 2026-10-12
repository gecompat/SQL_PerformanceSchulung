/* RES-008: begrenzte synthetische float32-Quellen-/Dimensions-/Storagevorbereitung. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @RawDemo nvarchar(max)=N'$(DemoId)',@RawRun nvarchar(max)=N'$(RunToken)',@RawTarget nvarchar(max)=N'$(TargetDatabase)';
IF DATALENGTH(@RawDemo)<>14 OR CONVERT(varbinary(max),@RawDemo)<>CONVERT(varbinary(max),N'RES-008')
 OR DATALENGTH(@RawRun) NOT BETWEEN 2 AND 32 OR @RawRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
 OR DATALENGTH(@RawTarget)<>DATALENGTH(N'SQLPERF_LAB_RES008_'+@RawRun)
 OR CONVERT(varbinary(max),@RawTarget)<>CONVERT(varbinary(max),N'SQLPERF_LAB_RES008_'+@RawRun)
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
IF DB_ID(@TargetDatabase) IS NULL
BEGIN
 SET @Sql=N'CREATE DATABASE '+QUOTENAME(@TargetDatabase)+N';'; EXEC sys.sp_executesql @Sql;
 SET @Sql=N'USE '+QUOTENAME(@TargetDatabase)+N';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=@D;
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@R;';
 EXEC sys.sp_executesql @Sql,N'@D varchar(7),@R varchar(16)',@D=@DemoId,@R=@RunToken;
END;
-- Marker wurden vor jeder Aenderung an einer vorhandenen Datenbank validiert.
SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET COMPATIBILITY_LEVEL=170;
 ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET RECOVERY SIMPLE;
 ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_CLOSE OFF;
 ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' SET AUTO_SHRINK OFF;';
EXEC sys.sp_executesql @Sql;
DECLARE @LogicalName sysname,@FileType int;
DECLARE OwnFiles CURSOR LOCAL FAST_FORWARD FOR SELECT name,type FROM sys.master_files WHERE database_id=DB_ID(@TargetDatabase) AND type IN (0,1);
OPEN OwnFiles; FETCH NEXT FROM OwnFiles INTO @LogicalName,@FileType;
WHILE @@FETCH_STATUS=0
BEGIN
 SET @Sql=N'ALTER DATABASE '+QUOTENAME(@TargetDatabase)+N' MODIFY FILE (NAME='+QUOTENAME(@LogicalName,N'''')+N',MAXSIZE='+CASE WHEN @FileType=0 THEN N'256MB' ELSE N'64MB' END+N',FILEGROWTH=16MB);';
 EXEC sys.sp_executesql @Sql;
 FETCH NEXT FROM OwnFiles INTO @LogicalName,@FileType;
END;
CLOSE OwnFiles; DEALLOCATE OwnFiles;
GO
USE [$(TargetDatabase)];
GO
SET NOCOUNT ON; SET XACT_ABORT ON;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');

DROP TABLE IF EXISTS lab.V32;
CREATE TABLE lab.V32(Id int NOT NULL PRIMARY KEY,V VECTOR(32) NOT NULL);
INSERT lab.V32(Id,V)
SELECT Id,CONVERT(VECTOR(32),'['+CONVERT(varchar(10),Id)+',1'+REPLICATE(',0',32-2)+']')
FROM(SELECT a.N*10+b.N+1 AS Id FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))a(N)
CROSS JOIN(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))b(N))s;

DROP TABLE IF EXISTS lab.V384;
CREATE TABLE lab.V384(Id int NOT NULL PRIMARY KEY,V VECTOR(384) NOT NULL);
INSERT lab.V384(Id,V)
SELECT Id,CONVERT(VECTOR(384),'['+CONVERT(varchar(10),Id)+',1'+REPLICATE(',0',384-2)+']')
FROM(SELECT a.N*10+b.N+1 AS Id FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))a(N)
CROSS JOIN(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))b(N))s;

DROP TABLE IF EXISTS lab.V768;
CREATE TABLE lab.V768(Id int NOT NULL PRIMARY KEY,V VECTOR(768) NOT NULL);
INSERT lab.V768(Id,V)
SELECT Id,CONVERT(VECTOR(768),'['+CONVERT(varchar(10),Id)+',1'+REPLICATE(',0',768-2)+']')
FROM(SELECT a.N*10+b.N+1 AS Id FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))a(N)
CROSS JOIN(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))b(N))s;

DROP TABLE IF EXISTS lab.V1536;
CREATE TABLE lab.V1536(Id int NOT NULL PRIMARY KEY,V VECTOR(1536) NOT NULL);
INSERT lab.V1536(Id,V)
SELECT Id,CONVERT(VECTOR(1536),'['+CONVERT(varchar(10),Id)+',1'+REPLICATE(',0',1536-2)+']')
FROM(SELECT a.N*10+b.N+1 AS Id FROM(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))a(N)
CROSS JOIN(VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9))b(N))s;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
