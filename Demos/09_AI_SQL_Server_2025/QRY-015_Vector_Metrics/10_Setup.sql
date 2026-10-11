/* QRY-015: Distanz, Norm und Normalisierung; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'QRY-015' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
 OR @RunToken COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9]%'
 OR CONVERT(varbinary(max),@TargetDatabase) <> CONVERT(varbinary(max),CONVERT(sysname,N'SQLPERF_LAB_'+REPLACE(@DemoId,'-','')+N'_'+@RunToken))
 THROW 51000,'FAIL_CONTRACT: Demo-ID, Run-Token oder Zieldatenbank ist ungueltig.',1;
DECLARE @Project nvarchar(max),@Contract nvarchar(max),@ExistingDemo nvarchar(max),@ExistingRun nvarchar(max),@Sql nvarchar(max);
IF DB_ID(@TargetDatabase) IS NOT NULL
BEGIN
 SET @Sql=N'SELECT @P=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
 @C=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
 @D=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
 @R=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
 FROM '+QUOTENAME(@TargetDatabase)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
 EXEC sys.sp_executesql @Sql,N'@P nvarchar(max) OUTPUT,@C nvarchar(max) OUTPUT,@D nvarchar(max) OUTPUT,@R nvarchar(max) OUTPUT',@P=@Project OUTPUT,@C=@Contract OUTPUT,@D=@ExistingDemo OUTPUT,@R=@ExistingRun OUTPUT;
 IF CONVERT(varbinary(max),ISNULL(@Project,N'')) <> CONVERT(varbinary(max),N'SQL_PerformanceSchulung')
 OR CONVERT(varbinary(max),ISNULL(@Contract,N'')) <> CONVERT(varbinary(max),N'1.0')
 OR CONVERT(varbinary(max),ISNULL(@ExistingDemo,N'')) <> CONVERT(varbinary(max),CONVERT(nvarchar(max),@DemoId))
 OR CONVERT(varbinary(max),ISNULL(@ExistingRun,N'')) <> CONVERT(varbinary(max),CONVERT(nvarchar(max),@RunToken))
 THROW 51004,'FAIL_STATE: Eigentumsmarker stimmen nicht vollstaendig und exakt ueberein.',1;
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
DROP TABLE IF EXISTS lab.VectorFixture;
CREATE TABLE lab.VectorFixture(Id int NOT NULL PRIMARY KEY, ModelSpace varchar(32) NOT NULL,V VECTOR(3) NOT NULL);
INSERT lab.VectorFixture VALUES(0,'GEOMETRY_V1','[0,0,0]'),(1,'GEOMETRY_V1','[1,0,0]'),(2,'GEOMETRY_V1','[10,0,0]'),(3,'GEOMETRY_V1','[0,1,0]'),(4,'GEOMETRY_V1','[1,1,0]');
PRINT 'SQLPERF_SUMMARY|PASS|OK';
