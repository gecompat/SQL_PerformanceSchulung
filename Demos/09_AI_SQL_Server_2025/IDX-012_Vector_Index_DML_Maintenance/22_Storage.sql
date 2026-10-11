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


IF NOT EXISTS(SELECT 1 FROM (VALUES(N'BASELINE'),(N'INDEXED'),(N'REBUILT')) AS Allowed(Stage)
 WHERE DATALENGTH(N'$(StorageStage)')=DATALENGTH(Stage)
 AND CONVERT(varbinary(max),N'$(StorageStage)')=CONVERT(varbinary(max),Stage))
 THROW 51000,'Vollständige feste Speicherphase fehlt.',1;
DECLARE @TranCount int=@@TRANCOUNT,@TranState int=XACT_STATE();
DECLARE @Stage nvarchar(max)=N'$(StorageStage)',@IndexCount int=(SELECT COUNT(*) FROM sys.vector_indexes),
 @Rows int=(SELECT COUNT(*) FROM lab.VectorFixture),
 @FileCount int=(SELECT COUNT(*) FROM sys.database_files),
 @InternalCount int=(SELECT COUNT(*) FROM sys.internal_tables),
 @PartitionCount int=(SELECT COUNT(*) FROM sys.dm_db_partition_stats);
SELECT N'STORAGE_GUARD' AS [kind],@Stage AS [Stage],DB_ID() AS [DatabaseId],
 DB_NAME() AS [Context],N'$(RunToken)' AS [RunToken],@Rows AS [SourceRows],@IndexCount AS [VectorIndexes],
 @TranCount AS [TransactionCount],@TranState AS [TransactionState],
 @FileCount AS [FileCount],@InternalCount AS [InternalCount],@PartitionCount AS [PartitionCount]
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES;
IF @Rows<>999 OR @TranCount<>0 OR @TranState<>0
 OR @IndexCount<>CASE WHEN @Stage=N'BASELINE' THEN 0 ELSE 1 END
 OR @PartitionCount NOT BETWEEN 1 AND 128 OR @InternalCount NOT BETWEEN 0 AND 64 OR @FileCount<>2
 THROW 51003,'Tatsächliche feste Speicheraufnahme überschreitet ihre Grenzen.',1;
DECLARE @Output nvarchar(max)=(SELECT N'STORAGE' AS [kind],@Stage AS [Stage],
 DB_ID() AS [DatabaseId],DB_NAME() AS [Context],N'$(RunToken)' AS [RunToken],
 OBJECT_ID(N'lab.VectorFixture') AS [FixtureObject],@Rows AS [SourceRows],@IndexCount AS [VectorIndexes],
 @TranCount AS [TransactionCount],@TranState AS [TransactionState],
 @FileCount AS [FileCount],@InternalCount AS [InternalCount],@PartitionCount AS [PartitionCount],
 JSON_QUERY((SELECT file_id,type,size,FILEPROPERTY(name,'SpaceUsed') AS [space_used_pages]
  FROM sys.database_files ORDER BY file_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS [files],
 JSON_QUERY((SELECT object_id,parent_id,parent_minor_id,internal_type,internal_type_desc
  FROM sys.internal_tables ORDER BY object_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS [internal_tables],
 JSON_QUERY((SELECT partition_id,object_id,index_id,partition_number,row_count,
  used_page_count,reserved_page_count,in_row_used_page_count,lob_used_page_count,row_overflow_used_page_count
  FROM sys.dm_db_partition_stats ORDER BY partition_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS [partitions]
 FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
IF @Output IS NULL OR DATALENGTH(@Output)>120000
 THROW 51003,'Vollständige Speicheraufnahme außerhalb Outputgrenze.',1;
SELECT @Output;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
