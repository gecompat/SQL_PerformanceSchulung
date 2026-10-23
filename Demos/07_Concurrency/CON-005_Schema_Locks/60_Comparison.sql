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

IF DB_NAME() COLLATE Latin1_General_100_BIN2<>@Target OR DATALENGTH(DB_NAME())<>DATALENGTH(@Target)
 THROW 51000,'FAIL_CONTRACT: Falscher Datenbankkontext.',1;

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

DECLARE @Rows bigint,@Sum int;
EXEC sys.sp_executesql N'SELECT @Rows=COUNT_BIG(*),@Sum=SUM(Payload) FROM lab.SchemaTarget WITH (NOLOCK);',N'@Rows bigint OUTPUT,@Sum int OUTPUT',@Rows OUTPUT,@Sum OUTPUT;
IF @Rows<>2 OR @Sum<>30 THROW 51006,'FAIL_RESULT_CONTRACT: Vergleichslesung liefert nicht die erwarteten Daten.',1;
UPDATE lab.SchemaState SET ComparisonRows=@Rows,ComparisonSum=@Sum WHERE StateId=1;

IF (SELECT COUNT(*) FROM lab.SchemaEvidence)<>1 OR NOT EXISTS
(
 SELECT 1 FROM lab.SchemaEvidence e JOIN lab.SchemaState s ON s.StateId=1 AND e.ObjectId=s.TargetObjectId
 WHERE e.DatabaseId=DB_ID() AND e.BlockerSessionId=e.BlockingSessionId AND e.ReaderSessionId<>e.BlockerSessionId
 AND e.WaitType=N'LCK_M_SCH_S' AND e.GrantedMode=N'Sch-M' AND e.GrantedStatus=N'GRANT'
 AND e.WaitingMode=N'Sch-S' AND e.WaitingStatus=N'WAIT' AND e.ResourceType=N'OBJECT'
 AND s.ReaderRows=2 AND s.ReaderSum=30
 AND e.BlockerSessionId=(SELECT SignaledBySessionId FROM fwk.SessionSignal WHERE DemoId='CON-005' AND RunToken=@Run AND SignalName='BLOCKER_START')
 AND e.ReaderSessionId=(SELECT SignaledBySessionId FROM fwk.SessionSignal WHERE DemoId='CON-005' AND RunToken=@Run AND SignalName='READER_READY')
 AND EXISTS(SELECT 1 FROM fwk.SessionSignal WHERE DemoId='CON-005' AND RunToken=@Run AND SignalName='BLOCKER_DONE' AND SignaledBySessionId=e.BlockerSessionId)
 AND EXISTS(SELECT 1 FROM fwk.SessionSignal WHERE DemoId='CON-005' AND RunToken=@Run AND SignalName='READER_DONE' AND SignaledBySessionId=e.ReaderSessionId)
)
 THROW 51006,'FAIL_RESULT_CONTRACT: Sperrnachweis oder Leserabschluss ist unvollständig.',1;
IF COL_LENGTH(N'lab.SchemaTarget',N'TransientColumn') IS NOT NULL
 OR (SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.SchemaTarget'))<>2
 OR (SELECT COUNT_BIG(*) FROM lab.SchemaTarget)<>2 OR (SELECT SUM(Payload) FROM lab.SchemaTarget)<>30
 THROW 51006,'FAIL_RESULT_CONTRACT: Schemaänderung oder Datenzustand nicht zurückgenommen.',1;
IF EXISTS(SELECT 1 FROM sys.dm_tran_locks WHERE resource_database_id=DB_ID() AND resource_type=N'OBJECT'
 AND resource_associated_entity_id=(SELECT TargetObjectId FROM lab.SchemaState WHERE StateId=1) AND request_mode=N'Sch-M')
 OR EXISTS(SELECT 1 FROM sys.dm_exec_requests WHERE database_id=DB_ID() AND blocking_session_id<>0)
 OR EXISTS(SELECT 1 FROM sys.dm_tran_session_transactions st JOIN sys.dm_tran_database_transactions dt
 ON dt.transaction_id=st.transaction_id WHERE dt.database_id=DB_ID() AND st.session_id<>@@SPID AND st.is_user_transaction=1)
 THROW 51002,'FAIL_STATE: Eigene Schemasperre, Blockierung oder offene Transaktion verblieben.',1;

IF NOT EXISTS(SELECT 1 FROM lab.SchemaState WHERE StateId=1 AND ComparisonRows=ReaderRows AND ComparisonSum=ReaderSum)
 THROW 51006,'FAIL_RESULT_CONTRACT: Problem- und Vergleichsergebnis unterscheiden sich.',1;
SELECT 1 Sequence,'COMPARISON' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
 N'CON-005' ObservedValue,N'begrenzter Schemasperrenvertrag' RequiredValue,N'Identische NOLOCK-Lesung ohne offene Schemaänderung erfolgreich; keine Leistungsaussage.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
