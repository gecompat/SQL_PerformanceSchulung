/* IDX-012: gebundenes DEC-074-Profil; eigene synthetische Datenbank. */
SET NOCOUNT ON;
IF DATALENGTH(N'$(DemoId)')<>DATALENGTH(N'IDX-012')
 OR CONVERT(varbinary(max),N'$(DemoId)')<>CONVERT(varbinary(max),N'IDX-012')
 OR DATALENGTH(N'$(RunToken)')<>32 OR N'$(RunToken)' COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-F0-9]%'
 OR DATALENGTH(N'$(TargetDatabase)')<>DATALENGTH(N'SQLPERF_LAB_IDX012_$(RunToken)')
 OR CONVERT(varbinary(max),N'$(TargetDatabase)')<>CONVERT(varbinary(max),N'SQLPERF_LAB_IDX012_$(RunToken)')
 THROW 51000,'FAIL_CONTRACT: Vollständige Demo-/Token-/DB-Bindung fehlt.',1;
IF DATALENGTH(N'$(ConfirmIsolatedLab)')<>2 OR CONVERT(varbinary(max),N'$(ConfirmIsolatedLab)')<>CONVERT(varbinary(max),N'1')
 OR DATALENGTH(N'$(HighImpactConfirmed)')<>2 OR CONVERT(varbinary(max),N'$(HighImpactConfirmed)')<>CONVERT(varbinary(max),N'1')
 OR COALESCE(TRY_CONVERT(int,N'$(MaximumRuntimeSeconds)'),-1)<>300
 THROW 51000,'FAIL_SAFETY: YELLOW-Bestätigung und festes Laufbudget fehlen.',1;


IF (SELECT COUNT(*) FROM (VALUES
 (N'SQLPERF.Project',N'SQL_PerformanceSchulung'),
 (N'SQLPERF.ContractVersion',N'1.0'),
 (N'SQLPERF.DemoId',N'IDX-012'),
 (N'SQLPERF.RunToken',N'$(RunToken)')) e(Name,Expected)
 JOIN sys.extended_properties p ON p.name=e.Name AND p.class=0
 AND DATALENGTH(p.name)=DATALENGTH(e.Name)
 AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 AND p.major_id=0 AND p.minor_id=0
 WHERE DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Expected)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=
 CONVERT(varbinary(max),e.Expected))<>4
 THROW 51001,'Full ownership binding lost.',1;

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

IF (SELECT COUNT(*) FROM sys.database_scoped_configurations WHERE
 (name=N'PREVIEW_FEATURES' AND TRY_CONVERT(int,value)=1) OR
 (name=N'MAXDOP' AND TRY_CONVERT(int,value)=1))<>2
 THROW 51003,'Actual preview and MAXDOP must both be one.',1;



IF NOT EXISTS(SELECT 1 FROM (VALUES(N'DML_BOUNDARY'),(N'REBUILD')) A(Stage)
 WHERE DATALENGTH(N'$(CostStage)')=DATALENGTH(Stage)
 AND CONVERT(varbinary(max),N'$(CostStage)')=CONVERT(varbinary(max),Stage))
 OR NOT EXISTS(SELECT 1 FROM (VALUES(N'BEFORE'),(N'AFTER')) A(Frame)
 WHERE DATALENGTH(N'$(CostFrame)')=DATALENGTH(Frame)
 AND CONVERT(varbinary(max),N'$(CostFrame)')=CONVERT(varbinary(max),Frame))
 THROW 51000,'Vollständige feste Kostenphase fehlt.',1;
IF OBJECT_ID(N'tempdb..#IDX012CostContext') IS NULL
 THROW 51003,'Eigener Phasenverbindungskontext fehlt.',1;
IF (SELECT COUNT(*) FROM #IDX012CostContext)<>1 OR NOT EXISTS(
 SELECT 1 FROM #IDX012CostContext WHERE SessionId=@@SPID AND DatabaseId=DB_ID()
 AND DATALENGTH(RunToken)=32
 AND CONVERT(varbinary(max),RunToken)=CONVERT(varbinary(max),N'$(RunToken)')
 AND DATALENGTH(Stage)=DATALENGTH(N'$(CostStage)')
 AND CONVERT(varbinary(max),Stage)=CONVERT(varbinary(max),N'$(CostStage)'))
 THROW 51003,'Vollständiger eigener Phasenverbindungskontext fehlt.',1;
DECLARE @TranCount int=@@TRANCOUNT,@TranState int=XACT_STATE();
DECLARE @Stage nvarchar(max)=N'$(CostStage)',@Frame nvarchar(max)=N'$(CostFrame)',
 @Rows int=(SELECT COUNT(*) FROM lab.VectorFixture),@Indexes int=(SELECT COUNT(*) FROM sys.vector_indexes),
 @SessionCount int=(SELECT COUNT(*) FROM sys.dm_exec_sessions WHERE session_id=@@SPID),
 @TempdbCount int=(SELECT COUNT(*) FROM tempdb.sys.dm_db_session_space_usage WHERE session_id=@@SPID AND database_id=2),
 @FileCount int=(SELECT COUNT(*) FROM sys.dm_io_virtual_file_stats(DB_ID(),NULL));
SELECT N'COST_GUARD' AS [kind],@Stage AS [Stage],@Frame AS [Frame],DB_ID() AS [DatabaseId],
 N'$(RunToken)' AS [RunToken],@@SPID AS [SessionId],@Rows AS [SourceRows],@Indexes AS [VectorIndexes],
 @TranCount AS [TransactionCount],@TranState AS [TransactionState],
 @SessionCount AS [SessionCount],@TempdbCount AS [TempdbCount],@FileCount AS [FileCount]
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES;
IF @Rows<>999 OR @TranCount<>0 OR @TranState<>0 OR @SessionCount<>1 OR @TempdbCount<>1 OR @FileCount<>2
 OR (SELECT COUNT(*) FROM sys.database_files)<>2
 OR @Indexes<>CASE WHEN @Stage=N'DML_BOUNDARY' AND @Frame=N'BEFORE' THEN 0 ELSE 1 END
 THROW 51003,'Tatsächliche feste Kostengrenzen verletzt.',1;
DECLARE @Output nvarchar(max)=(SELECT N'PHASE_COST' AS [kind],@Stage AS [Stage],@Frame AS [Frame],
 DB_ID() AS [DatabaseId],DB_NAME() AS [Context],N'$(RunToken)' AS [RunToken],@@SPID AS [SessionId],
 @Rows AS [SourceRows],@Indexes AS [VectorIndexes],@TranCount AS [TransactionCount],@TranState AS [TransactionState],
 @SessionCount AS [SessionCount],@TempdbCount AS [TempdbCount],@FileCount AS [FileCount],
 JSON_QUERY((SELECT session_id,cpu_time,reads,writes,logical_reads FROM sys.dm_exec_sessions
  WHERE session_id=@@SPID FOR JSON PATH,INCLUDE_NULL_VALUES)) AS [session],
 JSON_QUERY((SELECT session_id,database_id,user_objects_alloc_page_count,user_objects_dealloc_page_count,
  internal_objects_alloc_page_count,internal_objects_dealloc_page_count FROM tempdb.sys.dm_db_session_space_usage
  WHERE session_id=@@SPID AND database_id=2 FOR JSON PATH,INCLUDE_NULL_VALUES)) AS [tempdb],
 JSON_QUERY((SELECT database_id,file_id,sample_ms,num_of_writes,num_of_bytes_written,io_stall_write_ms
  FROM sys.dm_io_virtual_file_stats(DB_ID(),NULL) ORDER BY file_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS [files]
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Vollständige Kostenaufnahme außerhalb Grenze.',1;
SELECT @Output;
