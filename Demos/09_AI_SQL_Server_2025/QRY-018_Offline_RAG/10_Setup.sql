/* QRY-018: Chunking, Overlap und Provenienz; synthetische Fixture; FWK-001 bis FWK-012. */
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @DemoId varchar(7)='$(DemoId)', @RunToken varchar(16)='$(RunToken)', @TargetDatabase sysname=N'$(TargetDatabase)';
IF @DemoId <> 'QRY-018' OR @RunToken IS NULL OR LEN(@RunToken) NOT BETWEEN 1 AND 16
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
DROP VIEW IF EXISTS lab.ReplayEvaluation;
DROP VIEW IF EXISTS lab.RetrievedContext;
DROP TABLE IF EXISTS lab.Replay;
DROP TABLE IF EXISTS lab.Questions;
DROP TABLE IF EXISTS lab.Chunks;
DROP TABLE IF EXISTS lab.Documents;
DROP TABLE IF EXISTS lab.VectorFixture;
CREATE TABLE lab.VectorFixture(Id int NOT NULL PRIMARY KEY,ModelSpace varchar(32) NOT NULL,V VECTOR(3) NOT NULL);
INSERT lab.VectorFixture VALUES(10,'GEOMETRY_V1','[1,0,0]'),(11,'GEOMETRY_V1','[1,0,0]'),(20,'GEOMETRY_V1','[0.9,0.1,0]');
CREATE TABLE lab.Documents(SourceId int NOT NULL PRIMARY KEY,DocId varchar(32) NOT NULL,Version int NOT NULL,IsCurrent bit NOT NULL,FactDays int NOT NULL,Content nvarchar(200) NOT NULL);
INSERT lab.Documents VALUES
(10,'module-a',1,0,5,N'Modul A bewahrt Bausteine 5 Tage auf.'),
(11,'module-a',2,1,7,N'Modul A bewahrt Bausteine 7 Tage auf.'),
(20,'alternate-a',1,1,9,N'Modul A bewahrt Bausteine 9 Tage auf.');
CREATE TABLE lab.Chunks(SourceId int NOT NULL,ChunkOrder int NOT NULL,ChunkOffset int NOT NULL,ChunkLength int NOT NULL,ChunkText nvarchar(200) NOT NULL,PRIMARY KEY(SourceId,ChunkOrder));
CREATE TABLE lab.Questions(QuestionId int NOT NULL PRIMARY KEY,AllowAlternate bit NOT NULL,Q VECTOR(3) NOT NULL,Question nvarchar(200) NOT NULL);
INSERT lab.Questions VALUES
(1,0,'[1,0,0]',N'Wie lange bewahrt Modul A Bausteine auf?'),
(2,0,'[0,0,1]',N'Welche Transportkosten hat Modul A?'),
(3,1,'[1,0,0]',N'Welche Aufbewahrung gilt bei widerspruechlichen Quellen?');
CREATE TABLE lab.Replay(ReplayId int NOT NULL PRIMARY KEY,QuestionId int NOT NULL,ClaimDays int NULL,CitedSourceId int NULL,Abstain bit NOT NULL,ExpectedOutcome varchar(12) NOT NULL);
-- Vorab eingefrorene Antwortfixtures, keine Modellantworten.
INSERT lab.Replay VALUES
(1,1,7,11,0,'ACCEPTED'),(2,1,99,11,0,'REJECTED'),(3,1,5,10,0,'REJECTED'),
(4,2,7,11,0,'REJECTED'),(5,3,7,11,0,'REJECTED'),(6,2,NULL,NULL,1,'ABSTAINED'),
(7,3,NULL,NULL,1,'ABSTAINED'),(8,1,9,20,0,'REJECTED'),(9,1,NULL,11,0,'REJECTED'),
(10,1,NULL,NULL,1,'REJECTED');
GO
CREATE VIEW lab.RetrievedContext AS
WITH Candidate AS (
 SELECT q.QuestionId,d.SourceId,d.DocId,d.Version,d.FactDays,c.ChunkText,c.ChunkOffset,c.ChunkLength,
 VECTOR_DISTANCE('cosine',q.Q,v.V) AS Distance,
 ROW_NUMBER() OVER(PARTITION BY q.QuestionId ORDER BY VECTOR_DISTANCE('cosine',q.Q,v.V),d.SourceId,c.ChunkOrder) AS RetrievalOrder
 FROM lab.Questions q JOIN lab.Documents d ON d.IsCurrent=1 AND (d.DocId='module-a' OR q.AllowAlternate=1)
 JOIN lab.VectorFixture v ON v.Id=d.SourceId AND v.ModelSpace='GEOMETRY_V1'
 JOIN lab.Chunks c ON c.SourceId=d.SourceId
 WHERE VECTOR_DISTANCE('cosine',q.Q,v.V)<=0.05
)
SELECT * FROM Candidate WHERE RetrievalOrder<=2;
GO
CREATE VIEW lab.ReplayEvaluation AS
WITH Evidence AS (
 SELECT q.QuestionId,COUNT(c.SourceId) AS ContextCount,COUNT(DISTINCT c.FactDays) AS DistinctFacts
 FROM lab.Questions q LEFT JOIN lab.RetrievedContext c ON c.QuestionId=q.QuestionId GROUP BY q.QuestionId
), Judgement AS (
 SELECT r.*,e.ContextCount,e.DistinctFacts,
 CASE
 WHEN r.Abstain=1 AND r.ClaimDays IS NULL AND r.CitedSourceId IS NULL AND (e.ContextCount=0 OR e.DistinctFacts>1) THEN 'ABSTAINED'
 WHEN r.Abstain=0 AND e.ContextCount>0 AND e.DistinctFacts=1 AND EXISTS(
  SELECT 1 FROM lab.RetrievedContext c JOIN lab.Documents d ON d.SourceId=c.SourceId
  WHERE c.QuestionId=r.QuestionId AND c.SourceId=r.CitedSourceId AND c.FactDays=r.ClaimDays
  AND CONVERT(varbinary(max),c.ChunkText)=CONVERT(varbinary(max),SUBSTRING(d.Content,c.ChunkOffset,c.ChunkLength))
  AND CHARINDEX(CONCAT(N'bewahrt Bausteine ',r.ClaimDays,N' Tage auf.'),c.ChunkText)>0
 ) THEN 'ACCEPTED' ELSE 'REJECTED' END AS ActualOutcome
 FROM lab.Replay r JOIN Evidence e ON e.QuestionId=r.QuestionId
)
SELECT *,CASE WHEN ContextCount=0 THEN 'MISSING_EVIDENCE' WHEN DistinctFacts>1 THEN 'CONFLICTING_EVIDENCE'
 WHEN ActualOutcome='ACCEPTED' THEN 'SUPPORTED_RETRIEVED_CITATION' ELSE 'UNSUPPORTED_REPLAY' END AS ReasonCode FROM Judgement;
GO
PRINT 'SQLPERF_SUMMARY|PASS|OK';
