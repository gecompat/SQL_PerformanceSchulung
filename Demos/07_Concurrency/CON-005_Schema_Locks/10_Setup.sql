SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 15000;
DECLARE @DemoRaw nvarchar(max)=N'$(DemoId)', @RunRaw nvarchar(max)=N'$(RunToken)',
        @TargetRaw nvarchar(max)=N'$(TargetDatabase)';
DECLARE @TrimmedRun nvarchar(max)=LTRIM(RTRIM(@RunRaw));
IF @DemoRaw IS NULL OR @DemoRaw COLLATE Latin1_General_100_BIN2<>N'CON-005' OR DATALENGTH(@DemoRaw)<>14
   OR @TrimmedRun IS NULL OR DATALENGTH(@TrimmedRun) NOT BETWEEN 2 AND 32
   OR @TrimmedRun COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Za-z0-9]%'
    THROW 51000,'FAIL_CONTRACT: Ungültige vollständige Demo-/Laufkennung.',1;
DECLARE @Run nvarchar(max)=UPPER(@TrimmedRun COLLATE Latin1_General_100_BIN2);
DECLARE @Expected nvarchar(max)=N'SQLPERF_LAB_CON005_'+@Run;
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
 EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''CON-005'';
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
SET NOCOUNT ON;SET XACT_ABORT ON;SET LOCK_TIMEOUT 15000;
-- Schutzgrenze je bestehender Standarddatei; kein hart codierter Dateipfad.
IF EXISTS(SELECT 1 FROM sys.database_files WHERE size>16384)
 THROW 51001,'FAIL_SAFETY: Standarddatei überschreitet 128 MiB; Setup endet ohne Last.',1;
DECLARE @File sysname,@Sql nvarchar(max);
DECLARE Files CURSOR LOCAL FAST_FORWARD FOR SELECT name FROM sys.database_files;
OPEN Files;FETCH NEXT FROM Files INTO @File;
WHILE @@FETCH_STATUS=0
BEGIN
 SET @Sql=N'ALTER DATABASE CURRENT MODIFY FILE(NAME='+QUOTENAME(@File,'''')+N',MAXSIZE=128MB,FILEGROWTH=8MB);';
 EXEC sys.sp_executesql @Sql;
 FETCH NEXT FROM Files INTO @File;
END;
CLOSE Files;DEALLOCATE Files;
IF SCHEMA_ID(N'lab') IS NULL EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');
IF SCHEMA_ID(N'fwk') IS NULL EXEC(N'CREATE SCHEMA fwk AUTHORIZATION dbo;');
DROP TABLE IF EXISTS lab.SchemaEvidence;
DROP TABLE IF EXISTS lab.SchemaState;
DROP TABLE IF EXISTS lab.SchemaTarget;
DROP TABLE IF EXISTS fwk.SessionSignal;
CREATE TABLE lab.SchemaTarget(RowId int NOT NULL PRIMARY KEY,Payload int NOT NULL);
INSERT lab.SchemaTarget VALUES(1,10),(2,20);
CREATE TABLE lab.SchemaState
(
 StateId int NOT NULL PRIMARY KEY CHECK(StateId=1),TargetObjectId int NOT NULL,
 ReaderRows bigint NULL,ReaderSum int NULL,ComparisonRows bigint NULL,ComparisonSum int NULL
);
INSERT lab.SchemaState(StateId,TargetObjectId) VALUES(1,OBJECT_ID(N'lab.SchemaTarget'));
CREATE TABLE lab.SchemaEvidence
(
 EvidenceId int NOT NULL PRIMARY KEY CHECK(EvidenceId=1),
 DatabaseId int NOT NULL,ObjectId int NOT NULL,BlockerSessionId smallint NOT NULL,ReaderSessionId smallint NOT NULL,
 BlockingSessionId smallint NOT NULL,WaitType nvarchar(60) NOT NULL,
 GrantedMode nvarchar(60) NOT NULL,GrantedStatus nvarchar(60) NOT NULL,
 WaitingMode nvarchar(60) NOT NULL,WaitingStatus nvarchar(60) NOT NULL,
 ResourceType nvarchar(60) NOT NULL,ResourceSubtype nvarchar(60) NOT NULL,
 ResourceDescription nvarchar(256) NOT NULL,ResourcePartition int NOT NULL,
 CapturedAtUtc datetime2(3) NOT NULL DEFAULT SYSUTCDATETIME()
);
CREATE TABLE fwk.SessionSignal
(
 DemoId varchar(7) NOT NULL,RunToken varchar(20) NOT NULL,SignalName varchar(64) NOT NULL,
 SignaledAtUtc datetime2(3) NOT NULL CONSTRAINT DF_SessionSignal_Captured DEFAULT SYSUTCDATETIME(),
 SignaledBySessionId smallint NOT NULL,
 CONSTRAINT PK_SessionSignal PRIMARY KEY(DemoId,RunToken,SignalName)
);
GO
CREATE OR ALTER PROCEDURE fwk.USP_Signal @DemoId varchar(7),@RunToken varchar(20),@SignalName varchar(64)
AS
BEGIN
 SET NOCOUNT ON;SET XACT_ABORT ON;
 IF @SignalName IS NULL OR @SignalName COLLATE Latin1_General_100_BIN2 LIKE '%[^A-Z0-9_]%' THROW 51000,'FAIL_CONTRACT: Ungültiger Signalname.',1;
 UPDATE fwk.SessionSignal SET SignaledAtUtc=SYSUTCDATETIME(),SignaledBySessionId=@@SPID WHERE DemoId=@DemoId AND RunToken=@RunToken AND SignalName=@SignalName;
 IF @@ROWCOUNT=0 BEGIN TRY INSERT fwk.SessionSignal(DemoId,RunToken,SignalName,SignaledBySessionId) VALUES(@DemoId,@RunToken,@SignalName,@@SPID); END TRY BEGIN CATCH IF ERROR_NUMBER() NOT IN(2601,2627) THROW;UPDATE fwk.SessionSignal SET SignaledAtUtc=SYSUTCDATETIME(),SignaledBySessionId=@@SPID WHERE DemoId=@DemoId AND RunToken=@RunToken AND SignalName=@SignalName;END CATCH;
END;
GO
CREATE OR ALTER PROCEDURE fwk.USP_WaitForSignal @DemoId varchar(7),@RunToken varchar(20),@SignalName varchar(64),@TimeoutMs int
AS
BEGIN
 SET NOCOUNT ON;SET XACT_ABORT ON;
 DECLARE @Start datetime2(3)=SYSUTCDATETIME();
 IF @TimeoutMs IS NULL OR @TimeoutMs NOT BETWEEN 1 AND 30000 THROW 51000,'FAIL_CONTRACT: Signal-Timeout ist ungültig.',1;
 WHILE NOT EXISTS(SELECT 1 FROM fwk.SessionSignal WHERE DemoId=@DemoId AND RunToken=@RunToken AND SignalName=@SignalName)
 BEGIN
  IF DATEDIFF_BIG(millisecond,@Start,SYSUTCDATETIME())>=@TimeoutMs THROW 51005,'FAIL_TIMEOUT: Erwartetes CON-005-Signal fehlt.',1;
  WAITFOR DELAY '00:00:00.100';
 END;
END;
GO
CREATE OR ALTER PROCEDURE fwk.USP_ClearSignals @DemoId varchar(7),@RunToken varchar(20)
AS
BEGIN SET NOCOUNT ON;DELETE fwk.SessionSignal WHERE DemoId=@DemoId AND RunToken=@RunToken;END;
GO
SELECT 1 Sequence,'SETUP' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
 N'CON-005' ObservedValue,N'begrenzter Schemasperrenvertrag' RequiredValue,N'Zwei synthetische Zeilen, Signale und begrenzte Evidenzobjekte angelegt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
