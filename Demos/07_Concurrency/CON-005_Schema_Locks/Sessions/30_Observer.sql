SET NOCOUNT ON;
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 15000;
DECLARE @DemoRaw nvarchar(max)=N'$(DemoId)', @RunRaw nvarchar(max)=N'$(RunToken)',
        @TargetRaw nvarchar(max)=DB_NAME();
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

IF DB_NAME() COLLATE Latin1_General_100_BIN2<>@Target OR DATALENGTH(DB_NAME())<>DATALENGTH(@Target)
 THROW 51000,'FAIL_CONTRACT: Sitzung ist nicht in der erwarteten Datenbank.',1;

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

DECLARE @Context varbinary(128)=CONVERT(varbinary(128),N'CON005|'+@Run);
SET CONTEXT_INFO @Context;
GO
DECLARE @Run nvarchar(max)=UPPER(LTRIM(RTRIM(N'$(RunToken)')) COLLATE Latin1_General_100_BIN2);


DECLARE @Context varbinary(128)=CONVERT(varbinary(128),N'CON005|'+@Run);
DECLARE @ObjectId int=(SELECT TargetObjectId FROM lab.SchemaState WHERE StateId=1),
 @DatabaseId int=DB_ID(),@Blocker smallint,@Reader smallint,@Started datetime2(3);
-- Alle drei Akteure schließen ihre Eigentums-/Metadatenprüfung vor dem ALTER TABLE ab.
EXEC fwk.USP_Signal @DemoId='CON-005',@RunToken=@Run,@SignalName='OBSERVER_READY';
EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken=@Run,@SignalName='BLOCKER_START',@TimeoutMs=15000;
EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken=@Run,@SignalName='READER_READY',@TimeoutMs=15000;
SELECT @Blocker=MAX(CASE WHEN SignalName='BLOCKER_START' THEN SignaledBySessionId END),
 @Reader=MAX(CASE WHEN SignalName='READER_READY' THEN SignaledBySessionId END)
FROM fwk.SessionSignal WHERE DemoId='CON-005' AND RunToken=@Run;
IF @Blocker IS NULL OR @Reader IS NULL OR @Blocker=@Reader OR @ObjectId IS NULL
 THROW 51006,'FAIL_RESULT_CONTRACT: Akteur- oder Objektbindung fehlt.',1;
SET @Started=SYSUTCDATETIME();
WHILE NOT EXISTS
(
 SELECT 1 FROM sys.dm_tran_locks l JOIN sys.dm_exec_sessions s ON s.session_id=l.request_session_id
 WHERE l.request_session_id=@Blocker AND s.context_info=@Context AND l.resource_database_id=@DatabaseId
 AND l.resource_type=N'OBJECT' AND l.resource_associated_entity_id=@ObjectId
 AND l.request_mode=N'Sch-M' AND l.request_status=N'GRANT'
)
BEGIN
 IF DATEDIFF_BIG(millisecond,@Started,SYSUTCDATETIME())>=15000
  THROW 51005,'FAIL_TIMEOUT: Gewährtes Sch-M auf dem erwarteten Objekt fehlt.',1;
 WAITFOR DELAY '00:00:00.050';
END;
EXEC fwk.USP_Signal @DemoId='CON-005',@RunToken=@Run,@SignalName='READER_GO';
SET @Started=SYSUTCDATETIME();
WHILE NOT EXISTS(SELECT 1 FROM lab.SchemaEvidence)
BEGIN
 INSERT lab.SchemaEvidence(EvidenceId,DatabaseId,ObjectId,BlockerSessionId,ReaderSessionId,BlockingSessionId,WaitType,
 GrantedMode,GrantedStatus,WaitingMode,WaitingStatus,ResourceType,ResourceSubtype,ResourceDescription,ResourcePartition)
 SELECT TOP(1) 1,@DatabaseId,@ObjectId,@Blocker,@Reader,r.blocking_session_id,r.wait_type,
 h.request_mode,h.request_status,w.request_mode,w.request_status,
 w.resource_type,ISNULL(w.resource_subtype,N''),ISNULL(w.resource_description,N''),w.resource_lock_partition
 FROM sys.dm_exec_requests r
 JOIN sys.dm_exec_sessions rs ON rs.session_id=r.session_id AND rs.context_info=@Context
 JOIN sys.dm_tran_locks w ON w.request_session_id=r.session_id AND w.request_request_id=r.request_id
 JOIN sys.dm_tran_locks h ON h.request_session_id=@Blocker
  AND h.resource_type=w.resource_type AND ISNULL(h.resource_subtype,N'')=ISNULL(w.resource_subtype,N'')
  AND h.resource_database_id=w.resource_database_id AND h.resource_associated_entity_id=w.resource_associated_entity_id
  AND ISNULL(h.resource_description,N'')=ISNULL(w.resource_description,N'') AND h.resource_lock_partition=w.resource_lock_partition
 JOIN sys.dm_exec_sessions hs ON hs.session_id=h.request_session_id AND hs.context_info=@Context
 WHERE r.session_id=@Reader AND r.database_id=@DatabaseId AND r.blocking_session_id=@Blocker AND r.wait_type=N'LCK_M_SCH_S'
 AND w.resource_database_id=@DatabaseId AND w.resource_type=N'OBJECT' AND w.resource_associated_entity_id=@ObjectId
 AND w.request_mode=N'Sch-S' AND w.request_status=N'WAIT' AND h.request_mode=N'Sch-M' AND h.request_status=N'GRANT';
 IF EXISTS(SELECT 1 FROM lab.SchemaEvidence) BREAK;
 IF DATEDIFF_BIG(millisecond,@Started,SYSUTCDATETIME())>=15000
  THROW 51005,'FAIL_TIMEOUT: Exakter Sch-M-/Sch-S-Konflikt mit Blockerbeziehung fehlt.',1;
 WAITFOR DELAY '00:00:00.050';
END;
EXEC fwk.USP_Signal @DemoId='CON-005',@RunToken=@Run,@SignalName='RELEASE_BLOCKER';
EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken=@Run,@SignalName='BLOCKER_DONE',@TimeoutMs=15000;
EXEC fwk.USP_WaitForSignal @DemoId='CON-005',@RunToken=@Run,@SignalName='READER_DONE',@TimeoutMs=15000;
SELECT 1 Sequence,'DEMONSTRATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
 N'CON-005' ObservedValue,N'begrenzter Schemasperrenvertrag' RequiredValue,N'Gewährtes Sch-M und wartendes Sch-S auf derselben Ressource nachgewiesen.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
