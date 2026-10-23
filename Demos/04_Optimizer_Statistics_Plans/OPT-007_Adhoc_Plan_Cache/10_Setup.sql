USE [master];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 15000;
DECLARE @DemoRaw nvarchar(max)=N'$(DemoId)', @RunRaw nvarchar(max)=N'$(RunToken)',
        @TargetRaw nvarchar(max)=N'$(TargetDatabase)';
DECLARE @TrimmedRun nvarchar(max)=LTRIM(RTRIM(@RunRaw));
IF @DemoRaw IS NULL OR @DemoRaw COLLATE Latin1_General_100_BIN2<>N'OPT-007' OR DATALENGTH(@DemoRaw)<>14
   OR @TrimmedRun IS NULL OR DATALENGTH(@TrimmedRun) NOT BETWEEN 2 AND 32
   OR @TrimmedRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Za-z0-9]%'
    THROW 51000,'FAIL_CONTRACT: Ungültige vollständige Demo-/Laufkennung.',1;
DECLARE @Run nvarchar(max)=UPPER(@TrimmedRun COLLATE Latin1_General_100_BIN2);
DECLARE @Expected nvarchar(max)=N'SQLPERF_LAB_OPT007_'+@Run;
IF @TargetRaw IS NULL OR @TargetRaw COLLATE Latin1_General_100_BIN2<>@Expected OR DATALENGTH(@TargetRaw)<>DATALENGTH(@Expected)
    THROW 51000,'FAIL_CONTRACT: Ungültiger vollständiger Zieldatenbankname.',1;
DECLARE @Target sysname=CONVERT(sysname,@Expected), @Sql nvarchar(max);
IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2 THROW 51002,'FAIL_STATE: Keine explizite oder implizite Transaktion am Einstieg erlaubt.',1;

IF ISNULL(TRY_CONVERT(int,N'$(ConfirmIsolatedLab)'),0)<>1
   OR ISNULL(TRY_CONVERT(int,N'$(HighImpactConfirmed)'),0)<>1
   OR ISNULL(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),0) NOT BETWEEN 1 AND 120
    THROW 51001,'FAIL_SAFETY: Isoliertes Lab, Hochlastbestätigung und Budget von 1 bis 120 Sekunden erforderlich.',1;

DECLARE @Major int=TRY_CONVERT(int,SERVERPROPERTY('ProductMajorVersion'));
IF @Major NOT IN(15,16,17) THROW 51000,'FAIL_CONTRACT: Nicht unterstützte Engineversion.',1;
IF DB_ID(@Target) IS NULL
BEGIN
 SET @Sql=N'CREATE DATABASE '+QUOTENAME(@Target)+N';';
 EXEC sys.sp_executesql @Sql;
 -- Bei fehlgeschlagener Erstmarkierung keine unmarkierte Datenbank erzwingen.
 SET @Sql=N'USE '+QUOTENAME(@Target)+N';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''OPT-007'';
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=@Run;';
 EXEC sys.sp_executesql @Sql,N'@Run nvarchar(16)',@Run=@Run;
END;

IF DB_ID(@Target)<=4 OR NOT EXISTS(SELECT 1 FROM sys.databases WHERE database_id=DB_ID(@Target) AND state=0 AND is_read_only=0)
    THROW 51002,'FAIL_STATE: Zieldatenbank fehlt, ist geschützt oder nicht online und schreibbar.',1;
DECLARE @P nvarchar(max),@C nvarchar(max),@D nvarchar(max),@R nvarchar(max);
SET @Sql=N'SELECT @P=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(max),value) END),
 @C=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(max),value) END),
 @D=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(max),value) END),
 @R=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(max),value) END)
 FROM '+QUOTENAME(@Target)+N'.sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;';
EXEC sys.sp_executesql @Sql,N'@P nvarchar(max) OUTPUT,@C nvarchar(max) OUTPUT,@D nvarchar(max) OUTPUT,@R nvarchar(max) OUTPUT',@P OUTPUT,@C OUTPUT,@D OUTPUT,@R OUTPUT;
IF @P IS NULL OR @P COLLATE Latin1_General_100_BIN2<>N'SQL_PerformanceSchulung' OR DATALENGTH(@P)<>DATALENGTH(N'SQL_PerformanceSchulung')
 OR @C IS NULL OR @C COLLATE Latin1_General_100_BIN2<>N'1.0' OR DATALENGTH(@C)<>DATALENGTH(N'1.0')
 OR @D IS NULL OR @D COLLATE Latin1_General_100_BIN2<>@DemoRaw OR DATALENGTH(@D)<>DATALENGTH(@DemoRaw)
 OR @R IS NULL OR @R COLLATE Latin1_General_100_BIN2<>@Run OR DATALENGTH(@R)<>DATALENGTH(@Run)
    THROW 51002,'FAIL_STATE: Vollständige Eigentumsmarker fehlen oder weichen ab; Datenbank bleibt erhalten.',1;

SET @Sql=N'ALTER DATABASE '+QUOTENAME(@Target)+N' SET RECOVERY SIMPLE;
 ALTER DATABASE '+QUOTENAME(@Target)+N' SET AUTO_CLOSE OFF;
 ALTER DATABASE '+QUOTENAME(@Target)+N' SET AUTO_SHRINK OFF;
 ALTER DATABASE '+QUOTENAME(@Target)+N' SET PAGE_VERIFY CHECKSUM;
 ALTER DATABASE '+QUOTENAME(@Target)+N' SET COMPATIBILITY_LEVEL='+CONVERT(nvarchar(3),@Major*10)+N';';
EXEC sys.sp_executesql @Sql;
GO
USE [$(TargetDatabase)];
GO
SET ANSI_NULLS ON;SET ANSI_PADDING ON;SET ANSI_WARNINGS ON;SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;SET QUOTED_IDENTIFIER ON;SET NUMERIC_ROUNDABORT OFF;
SET LANGUAGE us_english;SET DATEFORMAT mdy;SET DATEFIRST 7;
SET NOCOUNT ON;SET XACT_ABORT ON;SET LOCK_TIMEOUT 15000;
IF NOT EXISTS(SELECT 1 FROM sys.database_scoped_configurations WHERE name='OPTIMIZE_FOR_AD_HOC_WORKLOADS' AND value=0)
 OR NOT EXISTS(SELECT 1 FROM sys.configurations WHERE name='optimize for ad hoc workloads' AND value_in_use=0)
 THROW 51002,'FAIL_STATE: Vollplanmodus fehlt nach Setup; keine Umschaltung.',1;
IF EXISTS(SELECT 1 FROM sys.database_files WHERE size>16384)
 THROW 51001,'FAIL_SAFETY: Datei überschreitet 128 MiB.',1;
DECLARE @File sysname,@Sql nvarchar(max);
DECLARE Files CURSOR LOCAL FAST_FORWARD FOR SELECT name FROM sys.database_files;
OPEN Files;FETCH NEXT FROM Files INTO @File;
WHILE @@FETCH_STATUS=0
BEGIN
 SET @Sql=N'ALTER DATABASE CURRENT MODIFY FILE(NAME='+QUOTENAME(@File,NCHAR(39))+N',MAXSIZE=128MB,FILEGROWTH=8MB);';
 EXEC sys.sp_executesql @Sql;
 FETCH NEXT FROM Files INTO @File;
END;
CLOSE Files;DEALLOCATE Files;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
IF OBJECT_ID(N'dbo.CacheProbe') IS NULL
BEGIN
 CREATE TABLE dbo.CacheProbe(Id int NOT NULL PRIMARY KEY,Payload int NOT NULL);
 INSERT dbo.CacheProbe SELECT TOP(40) ROW_NUMBER() OVER(ORDER BY a.object_id),ROW_NUMBER() OVER(ORDER BY a.object_id) FROM sys.all_objects a;
 CREATE TABLE lab.CacheState(StateId int PRIMARY KEY CHECK(StateId=1),StartedAt datetime2(3) NOT NULL,
  RunToken nvarchar(16) NOT NULL,DatabaseId int NOT NULL,Stage int NOT NULL,Options int NOT NULL,Config xml NOT NULL,
  Forced bit NOT NULL,Compatibility int NOT NULL,LanguageId smallint NOT NULL,DateFirst int NOT NULL,DateFormat nvarchar(3) NOT NULL);
 CREATE TABLE lab.CacheResult(Arm char(1) NOT NULL,KeyValue int NOT NULL,Id int NOT NULL,Payload int NOT NULL,PRIMARY KEY(Arm,KeyValue));
 CREATE TABLE lab.CacheSnapshot(Arm char(1) NOT NULL,Calls int NOT NULL,Handle varbinary(64) NOT NULL,
  BatchKey int NOT NULL,Bytes bigint NOT NULL,ObjType nvarchar(60) NOT NULL,CacheType nvarchar(60) NOT NULL,
  ExecutionCount bigint NOT NULL,Created datetime NOT NULL,Generation bigint NOT NULL,SetOptions bigint NOT NULL,
  CapturedAt datetime2(3) NOT NULL,PRIMARY KEY(Arm,Calls,Handle),UNIQUE(Arm,Calls,BatchKey));
END;
IF (SELECT COUNT(*) FROM dbo.CacheProbe)<>40 OR EXISTS(SELECT 1 FROM dbo.CacheProbe WHERE Id NOT BETWEEN 1 AND 40 OR Payload<>Id)
 THROW 51002,'FAIL_STATE: Synthetische Tupel weichen ab.',1;
GO
CREATE OR ALTER PROCEDURE lab.USP_Context @RunRaw nvarchar(max),@CheckState bit=1
AS
BEGIN
 SET NOCOUNT ON;
 DECLARE @Run nvarchar(max)=UPPER(LTRIM(RTRIM(@RunRaw)) COLLATE Latin1_General_100_BIN2);
 IF @Run IS NULL OR DATALENGTH(@Run) NOT BETWEEN 2 AND 32 OR @Run COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
  THROW 51000,'FAIL_CONTRACT: Ungültiger Lauftoken.',1;
 IF DB_ID()<=4 OR DB_NAME() COLLATE Latin1_General_100_BIN2<>N'SQLPERF_LAB_OPT007_'+@Run
  OR DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_OPT007_'+@Run)
  THROW 51002,'FAIL_STATE: Falsche Datenbank.',1;
 IF EXISTS(SELECT 1 FROM (VALUES(N'SQLPERF.Project',N'SQL_PerformanceSchulung'),(N'SQLPERF.ContractVersion',N'1.0'),
  (N'SQLPERF.DemoId',N'OPT-007'),(N'SQLPERF.RunToken',@Run)) e(Name,Value)
  WHERE NOT EXISTS(SELECT 1 FROM sys.extended_properties p WHERE p.class=0 AND p.major_id=0 AND p.minor_id=0 AND p.name=e.Name
   AND CONVERT(nvarchar(max),p.value) COLLATE Latin1_General_100_BIN2=e.Value COLLATE Latin1_General_100_BIN2
   AND DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Value)))
  THROW 51002,'FAIL_STATE: Vollständiges Eigentum fehlt.',1;
 IF @@TRANCOUNT<>0 OR (2 & @@OPTIONS)=2 THROW 51002,'FAIL_STATE: Offene Transaktion.',1;
 IF NOT EXISTS(SELECT 1 FROM sys.database_scoped_configurations WHERE name='OPTIMIZE_FOR_AD_HOC_WORKLOADS' AND value=0)
  OR NOT EXISTS(SELECT 1 FROM sys.configurations WHERE name='optimize for ad hoc workloads' AND value_in_use=0)
  THROW 51002,'FAIL_STATE: Vollplanmodus wurde geändert.',1;
 IF @CheckState=1
 BEGIN
  DECLARE @Config xml=(SELECT name,value,value_for_secondary FROM sys.database_scoped_configurations ORDER BY name FOR XML RAW,ROOT('Config'),TYPE);
  IF NOT EXISTS(SELECT 1 FROM lab.CacheState WHERE StateId=1 AND DatabaseId=DB_ID()
   AND RunToken COLLATE Latin1_General_100_BIN2=@Run AND DATALENGTH(RunToken)=DATALENGTH(@Run)
   AND Options=@@OPTIONS AND CONVERT(nvarchar(max),Config)=CONVERT(nvarchar(max),@Config)
   AND Forced=(SELECT is_parameterization_forced FROM sys.databases WHERE database_id=DB_ID())
   AND Compatibility=(SELECT compatibility_level FROM sys.databases WHERE database_id=DB_ID())
   AND LanguageId=@@LANGID AND DateFirst=@@DATEFIRST
   AND DateFormat=(SELECT date_format FROM sys.dm_exec_sessions WHERE session_id=@@SPID))
   THROW 51002,'FAIL_STATE: Lauf-/SET-/Konfigurationskontext weicht ab.',1;
  IF EXISTS(SELECT 1 FROM lab.CacheState WHERE DATEDIFF_BIG(millisecond,StartedAt,SYSUTCDATETIME())>=120000)
   THROW 51005,'FAIL_TIMEOUT: Reguläres Zeitbudget verbraucht.',1;
 END;
END;
GO
CREATE OR ALTER FUNCTION lab.QueryText(@Run nvarchar(16),@Arm char(1),@Key int)
RETURNS nvarchar(2048)
AS
BEGIN
 RETURN N'/* OPT-007:'+@Run+CASE WHEN @Arm='L' THEN N':LITERAL */'+NCHAR(10)+N'DECLARE @Key int = '+CONVERT(nvarchar(2),@Key)+N';'
 ELSE N':PARAMETER */' END+NCHAR(10)+N'SELECT Id, Payload'+NCHAR(10)+N'FROM dbo.CacheProbe'+NCHAR(10)+N'WHERE Id = @Key;';
END;
GO
CREATE OR ALTER PROCEDURE lab.USP_Capture @RunRaw nvarchar(max),@Arm char(1),@Calls int,@Store bit=0
AS
BEGIN
 SET NOCOUNT ON;
 EXEC lab.USP_Context @RunRaw;
 DECLARE @Run nvarchar(16)=UPPER(LTRIM(RTRIM(@RunRaw)) COLLATE Latin1_General_100_BIN2);
 IF @Arm IS NULL OR @Arm NOT IN('L','P') OR @Calls IS NULL OR @Calls NOT BETWEEN 0 AND 40 OR @Store IS NULL OR (@Store=1 AND @Calls NOT IN(0,20,40))
  THROW 51000,'FAIL_CONTRACT: Ungültiger Messpunkt.',1;
 DECLARE @Prefix nvarchar(100)=N'/* OPT-007:'+@Run+CASE WHEN @Arm='L' THEN N':LITERAL */' ELSE N':PARAMETER */' END;
 -- Schutzprüfung umfasst beide Arme; keine Joinvervielfachung der Bytes.
 IF (SELECT ISNULL(SUM(CONVERT(bigint,cp.size_in_bytes)),0) FROM sys.dm_exec_cached_plans cp CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
  WHERE EXISTS(SELECT 1 FROM sys.dm_exec_plan_attributes(cp.plan_handle) a WHERE a.attribute='dbid' AND CONVERT(int,a.value)=DB_ID())
   AND (CHARINDEX(N'/* OPT-007:'+@Run+N':LITERAL */',st.text COLLATE Latin1_General_100_BIN2)>0
    OR CHARINDEX(N'/* OPT-007:'+@Run+N':PARAMETER */',st.text COLLATE Latin1_General_100_BIN2)>0))>16777216
  THROW 51001,'FAIL_SAFETY: Gesamte eigene Cachebelegung überschreitet 16 MiB.',1;
 -- Die Enginegrenzen des SELECT schließen den abschließenden Batchdelimiter aus.
 DECLARE @Select nvarchar(200)=N'SELECT Id, Payload'+NCHAR(10)+N'FROM dbo.CacheProbe'+NCHAR(10)+N'WHERE Id = @Key';
 DECLARE @Expected TABLE(BatchKey int PRIMARY KEY,Text nvarchar(2048));
 IF @Arm='L' INSERT @Expected SELECT Id,lab.QueryText(@Run,'L',Id) FROM dbo.CacheProbe WHERE Id<=@Calls;
 ELSE IF @Calls>0 INSERT @Expected VALUES(0,N'(@Key int)'+lab.QueryText(@Run,'P',0));
 DECLARE @Plans TABLE(Handle varbinary(64) PRIMARY KEY,Text nvarchar(max),Bytes bigint,ObjType nvarchar(60),CacheType nvarchar(60),
  PlanXml xml,SetOptions bigint,DatabaseId int,AttributeCount int);
 INSERT @Plans
 SELECT cp.plan_handle,st.text,cp.size_in_bytes,cp.objtype,cp.cacheobjtype,qp.query_plan,a.SetOptions,a.DatabaseId,a.AttributeCount
 FROM sys.dm_exec_cached_plans cp
 CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
 OUTER APPLY sys.dm_exec_query_plan(cp.plan_handle) qp
 CROSS APPLY(SELECT MAX(CASE WHEN attribute='dbid' THEN CONVERT(int,value) END) DatabaseId,
  MAX(CASE WHEN attribute='set_options' THEN CONVERT(bigint,value) END) SetOptions,
  SUM(CASE WHEN attribute='dbid' THEN 1 ELSE 0 END) AttributeCount FROM sys.dm_exec_plan_attributes(cp.plan_handle)) a
 WHERE a.DatabaseId=DB_ID() AND CHARINDEX(@Prefix COLLATE Latin1_General_100_BIN2,st.text COLLATE Latin1_General_100_BIN2)>0;
 IF ISNULL((SELECT SUM(Bytes) FROM @Plans),0)>16777216 THROW 51001,'FAIL_SAFETY: Eigene Cachebelegung überschreitet 16 MiB.',1;
 IF (SELECT COUNT(*) FROM @Plans)<>(SELECT COUNT(*) FROM @Expected)
  OR EXISTS(SELECT 1 FROM @Plans p WHERE NOT EXISTS(SELECT 1 FROM @Expected e WHERE p.Text COLLATE Latin1_General_100_BIN2=e.Text COLLATE Latin1_General_100_BIN2 AND DATALENGTH(p.Text)=DATALENGTH(e.Text)))
  OR EXISTS(SELECT 1 FROM @Expected e WHERE (SELECT COUNT(*) FROM @Plans p WHERE p.Text COLLATE Latin1_General_100_BIN2=e.Text COLLATE Latin1_General_100_BIN2 AND DATALENGTH(p.Text)=DATALENGTH(e.Text))<>1)
  THROW 51006,'FAIL_RESULT_CONTRACT: Vollständige Cachetext-/Handlezuordnung fehlt.',1;
 IF EXISTS(SELECT 1 FROM @Plans WHERE ObjType<>CASE WHEN @Arm='L' THEN N'Adhoc' ELSE N'Prepared' END OR CacheType<>N'Compiled Plan'
  OR DatabaseId IS NULL OR DatabaseId<>DB_ID() OR SetOptions IS NULL OR AttributeCount<>1 OR Bytes IS NULL OR Bytes<=0 OR PlanXml IS NULL
  OR PlanXml.exist('declare default element namespace "http://schemas.microsoft.com/sqlserver/2004/07/showplan"; /ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple[@StatementType="SELECT"]/QueryPlan/RelOp')<>1
  OR PlanXml.exist('declare default element namespace "http://schemas.microsoft.com/sqlserver/2004/07/showplan"; //@ParameterizedPlanHandle')=1
  OR PlanXml.exist('declare default element namespace "http://schemas.microsoft.com/sqlserver/2004/07/showplan"; //ParameterList/ColumnReference[@Column!="@Key"]')=1)
  THROW 51006,'FAIL_RESULT_CONTRACT: Shell, Stub, Template oder fehlender echter SELECT-Plan.',1;
 IF EXISTS(SELECT 1 FROM @Plans WHERE
  PlanXml.value('declare default element namespace "http://schemas.microsoft.com/sqlserver/2004/07/showplan"; count(/ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple[@StatementType="SELECT"])','int')<>1
  OR NOT (CONVERT(varbinary(max),PlanXml.value('declare default element namespace "http://schemas.microsoft.com/sqlserver/2004/07/showplan"; (/ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple[@StatementType="SELECT"]/@StatementText)[1]','nvarchar(max)'))=CONVERT(varbinary(max),@Select)
   OR (@Arm='P' AND CONVERT(varbinary(max),PlanXml.value('declare default element namespace "http://schemas.microsoft.com/sqlserver/2004/07/showplan"; (/ShowPlanXML/BatchSequence/Batch/Statements/StmtSimple[@StatementType="SELECT"]/@StatementText)[1]','nvarchar(max)'))=CONVERT(varbinary(max),N'(@Key int)'+LEFT(lab.QueryText(@Run,'P',0),LEN(lab.QueryText(@Run,'P',0))-1)))))
  THROW 51006,'FAIL_RESULT_CONTRACT: XML-Knoten gehört nicht eindeutig zum Soll-SELECT.',1;
 DECLARE @Stats TABLE(Handle varbinary(64),ExecutionCount bigint,Created datetime,Generation bigint,StatementText nvarchar(max),BatchMatches bit,ValidOffsets bit);
 INSERT @Stats
 SELECT q.plan_handle,q.execution_count,q.creation_time,q.plan_generation_num,
  SUBSTRING(t.text,q.statement_start_offset/2+1,(CASE WHEN q.statement_end_offset=-1 THEN DATALENGTH(t.text) ELSE q.statement_end_offset END-q.statement_start_offset)/2+1),
  CASE WHEN CONVERT(varbinary(max),t.text)=CONVERT(varbinary(max),p.Text) THEN 1 ELSE 0 END,
  CASE WHEN q.statement_start_offset>=0 AND q.statement_start_offset%2=0 AND q.statement_start_offset<DATALENGTH(t.text)
   AND (q.statement_end_offset=-1 OR (q.statement_end_offset>=q.statement_start_offset AND q.statement_end_offset%2=0 AND q.statement_end_offset<DATALENGTH(t.text))) THEN 1 ELSE 0 END
 FROM sys.dm_exec_query_stats q JOIN @Plans p ON p.Handle=q.plan_handle CROSS APPLY sys.dm_exec_sql_text(q.sql_handle) t;
 -- Ein einziges exaktes SELECT-Statement pro Handle; kein Zähler eines Wrappers.
 IF EXISTS(SELECT 1 FROM @Stats WHERE StatementText IS NULL OR BatchMatches<>1 OR ValidOffsets<>1) THROW 51006,'FAIL_RESULT_CONTRACT: NULL- oder abweichende Statementmetadaten.',1;
 DELETE FROM @Stats WHERE CONVERT(varbinary(max),StatementText)<>CONVERT(varbinary(max),@Select)
  AND NOT(@Arm='P' AND CONVERT(varbinary(max),StatementText)=CONVERT(varbinary(max),LEFT(lab.QueryText(@Run,'P',0),LEN(lab.QueryText(@Run,'P',0))-1)));
 IF EXISTS(SELECT 1 FROM @Plans p WHERE (SELECT COUNT(*) FROM @Stats s WHERE s.Handle=p.Handle)<>1)
  OR EXISTS(SELECT 1 FROM @Stats WHERE ExecutionCount<>CASE WHEN @Arm='P' THEN @Calls ELSE 1 END OR Created IS NULL OR Generation IS NULL)
  THROW 51006,'FAIL_RESULT_CONTRACT: Exakte SELECT-Ausführungsstatistik fehlt.',1;
 IF @Store=1
 BEGIN
  IF EXISTS(SELECT 1 FROM lab.CacheSnapshot WHERE Arm=@Arm AND Calls=@Calls) THROW 51002,'FAIL_STATE: Messpunkt existiert bereits.',1;
  INSERT lab.CacheSnapshot
  SELECT @Arm,@Calls,p.Handle,e.BatchKey,p.Bytes,p.ObjType,p.CacheType,s.ExecutionCount,s.Created,s.Generation,p.SetOptions,SYSUTCDATETIME()
  FROM @Plans p JOIN @Expected e ON p.Text COLLATE Latin1_General_100_BIN2=e.Text COLLATE Latin1_General_100_BIN2 AND DATALENGTH(p.Text)=DATALENGTH(e.Text)
  JOIN @Stats s ON s.Handle=p.Handle;
 END;
END;
GO
CREATE OR ALTER PROCEDURE lab.USP_Workload @RunRaw nvarchar(max),@Arm char(1)
AS
BEGIN
 SET NOCOUNT ON;SET XACT_ABORT ON;SET LOCK_TIMEOUT 15000;
 EXEC lab.USP_Context @RunRaw;
 IF @Arm IS NULL OR @Arm NOT IN('L','P') OR NOT EXISTS(SELECT 1 FROM lab.CacheState WHERE Stage=CASE WHEN @Arm='L' THEN 1 ELSE 2 END)
  THROW 51002,'FAIL_STATE: Falsche Reihenfolge oder wiederholter Arm.',1;
 DECLARE @Run nvarchar(16)=UPPER(LTRIM(RTRIM(@RunRaw)) COLLATE Latin1_General_100_BIN2),@Key int=1,@Text nvarchar(max),@Start datetime2(3)=SYSUTCDATETIME();
 DECLARE @Result TABLE(Id int,Payload int);
 WHILE @Key<=40
 BEGIN
  EXEC lab.USP_Context @RunRaw;
  SET @Text=lab.QueryText(@Run,@Arm,@Key);
  IF @Text IS NULL OR DATALENGTH(@Text)>4096 THROW 51001,'FAIL_SAFETY: Nutztext überschreitet 4096 UTF-16-Bytes.',1;
  DELETE @Result;
  IF @Arm='L' INSERT @Result EXEC(@Text);
  ELSE INSERT @Result EXEC sys.sp_executesql @Text,N'@Key int',@Key=@Key;
  IF (SELECT COUNT(*) FROM @Result)<>1 OR NOT EXISTS(SELECT 1 FROM @Result WHERE Id=@Key AND Payload=@Key)
   THROW 51006,'FAIL_RESULT_CONTRACT: Vollständiges Tupel (k,k) fehlt.',1;
  INSERT lab.CacheResult SELECT @Arm,@Key,Id,Payload FROM @Result;
  DECLARE @Store bit=CASE WHEN @Key IN(20,40) THEN 1 ELSE 0 END;
  EXEC lab.USP_Capture @RunRaw,@Arm,@Key,@Store;
  IF DATEDIFF_BIG(millisecond,@Start,SYSUTCDATETIME())>=15000 THROW 51005,'FAIL_TIMEOUT: Armbudget verbraucht.',1;
  SET @Key+=1;
 END;
 UPDATE lab.CacheState SET Stage=Stage+1;
END;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
