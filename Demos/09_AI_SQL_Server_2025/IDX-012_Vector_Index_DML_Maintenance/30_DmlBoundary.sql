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

SET QUOTED_IDENTIFIER ON;
SET XACT_ABORT OFF;
IF @@TRANCOUNT<>0 OR XACT_STATE()<>0 THROW 51003,'Unexpected entry transaction.',1;
IF EXISTS(SELECT 1 FROM sys.database_scoped_configurations WHERE name=N'ALLOW_STALE_VECTOR_INDEX')
 THROW 51003,'Fixed absent stale-option profile changed.',1;
IF (SELECT COUNT(*) FROM lab.VectorFixture)<>999 OR (SELECT COUNT(*) FROM lab.FrozenSource)<>999
 OR EXISTS(SELECT 1 FROM lab.VectorFixture WHERE Id NOT BETWEEN 1 AND 999)
 OR EXISTS(SELECT 1 FROM sys.triggers WHERE parent_id=OBJECT_ID(N'lab.VectorFixture'))
 OR EXISTS(SELECT 1 FROM sys.vector_indexes)
 THROW 51003,'Fixed fresh source/index state missing.',1;
DECLARE @Stage int=0,@Operation int,@Ordinal int=0,@Sql nvarchar(max),@Label nvarchar(40),
 @TargetId int,@Succeeded bit,@Rows int,@Error int,@ErrorState int,@Message nvarchar(4000),
 @ActualBytes varbinary(max),@ExpectedChange bit,@DuringRows int,@RestoredRows int,
 @TranCount int,@TranState int,@IndexBefore nvarchar(max),@IndexAfter nvarchar(max),
 @IndexUnchanged bit,@Output nvarchar(max),@BuildStarted datetime2(7),@BuildEnded datetime2(7),
 @NewVector VECTOR(3)=CONVERT(VECTOR(3),N'[1,0,0]'),@TargetBytes varbinary(max);
SET @TargetBytes=CONVERT(varbinary(max),CONVERT(nvarchar(max),@NewVector));
WHILE @Stage<2
BEGIN
 IF @Stage=1
 BEGIN
  IF COALESCE(TRY_CONVERT(int,SESSIONPROPERTY('QUOTED_IDENTIFIER')),-1)<>1
   THROW 51003,'Required actual build session option missing.',1;
  SET @BuildStarted=SYSUTCDATETIME();
  EXEC(N'CREATE VECTOR INDEX IDX012_OwnVector ON lab.VectorFixture(V)
   WITH (METRIC=''cosine'',TYPE=''diskann'');');
  SET @BuildEnded=SYSUTCDATETIME();
  IF (SELECT COUNT(*) FROM sys.vector_indexes)<>1 OR NOT EXISTS(
   SELECT 1 FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture') AND type=8
   AND is_disabled=0 AND is_hypothetical=0 AND type_desc=N'VECTOR'
   AND DATALENGTH(name)=DATALENGTH(N'IDX012_OwnVector')
   AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'IDX012_OwnVector')
   AND DATALENGTH(CONVERT(nvarchar(max),vector_index_type))=DATALENGTH(N'DiskANN')
   AND CONVERT(varbinary(max),CONVERT(nvarchar(max),vector_index_type))=CONVERT(varbinary(max),N'DiskANN')
   AND DATALENGTH(CONVERT(nvarchar(max),distance_metric))=DATALENGTH(N'COSINE')
   AND CONVERT(varbinary(max),CONVERT(nvarchar(max),distance_metric))=CONVERT(varbinary(max),N'COSINE'))
   THROW 51003,'Actual own fixed index profile missing.',1;
  SET @IndexBefore=(SELECT * FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
   ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
  SET @Output=(SELECT N'INDEX' kind,DB_ID() DatabaseId,N'$(RunToken)' RunToken,
   DATEDIFF_BIG(MICROSECOND,@BuildStarted,@BuildEnded) BuildElapsedUs,
   JSON_QUERY(@IndexBefore) metadata FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
  IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Full index evidence outside bound.',1;
  SELECT @Output;
 END;
 SET @Operation=1;
 WHILE @Operation<=4
 BEGIN
  IF @@TRANCOUNT<>0 OR XACT_STATE()<>0 THROW 51003,'Unexpected transaction before operation.',1;
  IF EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
   EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource)
   OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource
   EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
   THROW 51003,'Full frozen source changed before operation.',1;
  SELECT @Succeeded=0,@Rows=NULL,@Error=NULL,@ErrorState=NULL,@Message=NULL,
   @ActualBytes=NULL,@ExpectedChange=NULL,@DuringRows=NULL,@IndexUnchanged=NULL;
  SET @TargetId=CASE WHEN @Operation=3 THEN 1000 ELSE 23 END;
  SET @Label=CASE @Operation WHEN 1 THEN N'UPDATE_ID_23' WHEN 2 THEN N'DELETE_ID_23'
   WHEN 3 THEN N'INSERT_ID_1000' ELSE N'MERGE_UPDATE_ID_23' END;
  SET @Sql=CASE @Operation
   WHEN 1 THEN N'UPDATE lab.VectorFixture SET V=@v WHERE Id=23; SET @n=@@ROWCOUNT;'
   WHEN 2 THEN N'DELETE FROM lab.VectorFixture WHERE Id=23; SET @n=@@ROWCOUNT;'
   WHEN 3 THEN N'INSERT lab.VectorFixture(Id,V) VALUES(1000,@v); SET @n=@@ROWCOUNT;'
   ELSE N'MERGE lab.VectorFixture AS t USING(SELECT 23 AS Id,@v AS V) AS s ON t.Id=s.Id
    WHEN MATCHED THEN UPDATE SET V=s.V; SET @n=@@ROWCOUNT;' END;
  BEGIN TRANSACTION;
  BEGIN TRY
   EXEC sys.sp_executesql @Sql,N'@v VECTOR(3),@n int OUTPUT',@v=@NewVector,@n=@Rows OUTPUT;
   SET @Succeeded=1;
   SET @DuringRows=(SELECT COUNT(*) FROM lab.VectorFixture);
   SELECT @ActualBytes=CONVERT(varbinary(max),CONVERT(nvarchar(max),V))
    FROM lab.VectorFixture WHERE Id=@TargetId;
   SET @ExpectedChange=CASE WHEN @Operation=2 AND @ActualBytes IS NULL THEN 1
    WHEN @Operation<>2 AND @ActualBytes IS NOT NULL AND DATALENGTH(@ActualBytes)=DATALENGTH(@TargetBytes)
     AND @ActualBytes=@TargetBytes THEN 1 ELSE 0 END;
   IF EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture WHERE Id<>@TargetId
    EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource WHERE Id<>@TargetId)
    OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource WHERE Id<>@TargetId
    EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture WHERE Id<>@TargetId)
    SET @ExpectedChange=0;
  END TRY
  BEGIN CATCH
   SELECT @Error=ERROR_NUMBER(),@ErrorState=ERROR_STATE(),@Message=ERROR_MESSAGE();
  END CATCH;
  IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
  SELECT @TranCount=@@TRANCOUNT,@TranState=XACT_STATE();
  SET @RestoredRows=(SELECT COUNT(*) FROM lab.VectorFixture);
  IF @TranCount<>0 OR @TranState<>0 OR @RestoredRows<>999
   OR EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
   EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource)
   OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource
   EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
   THROW 51003,'Full actual source/transaction restore missing.',1;
  IF @Stage=1
  BEGIN
   SET @IndexAfter=(SELECT * FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
    ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
   SET @IndexUnchanged=CASE WHEN @IndexAfter IS NOT NULL AND DATALENGTH(@IndexAfter)=DATALENGTH(@IndexBefore)
    AND CONVERT(varbinary(max),@IndexAfter)=CONVERT(varbinary(max),@IndexBefore) THEN 1 ELSE 0 END;
  END;
  SET @Ordinal+=1;
  SET @Output=(SELECT N'DML_BOUNDARY' kind,CASE WHEN @Stage=0 THEN N'NO_INDEX' ELSE N'WITH_INDEX' END Stage,
   @Label Operation,@Ordinal Ordinal,N'$(RunToken)' RunToken,DB_ID() DatabaseId,DB_NAME() Context,
   N'ABSENT' StaleOptionState,@Succeeded Succeeded,@Rows AffectedRows,@DuringRows DuringRowCount,
   @ExpectedChange ExpectedChange,@Error ErrorNumber,@ErrorState ErrorState,@Message ErrorMessage,
   CONVERT(bit,1) SourceRestored,CONVERT(bit,CASE WHEN @TranCount=0 AND @TranState=0 THEN 1 ELSE 0 END) RolledBack,
   @TranCount TransactionCount,@TranState TransactionState,@RestoredRows RestoredRowCount,
   @IndexUnchanged IndexMetadataUnchanged FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
  IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'DML evidence outside fixed bound.',1;
  SELECT @Output;
  -- Der tatsächliche Datensatz steht vor dem Guard im privaten Rohoutput.
  IF @Stage=0 AND (@Succeeded<>1 OR COALESCE(@Rows,-1)<>1 OR COALESCE(@ExpectedChange,0)<>1 OR @Error IS NOT NULL
   OR COALESCE(@DuringRows,-1)<>CASE @Operation WHEN 2 THEN 998 WHEN 3 THEN 1000 ELSE 999 END)
   THROW 51003,'Actual successful positive control missing.',1;
  IF @Stage=1 AND (@Succeeded<>0 OR COALESCE(@Error,-1)<>42231 OR COALESCE(@ErrorState,-1)<>1
   OR COALESCE(@IndexUnchanged,0)<>1 OR @Message IS NULL OR LEN(@Message)=0)
   THROW 51003,'Actual fixed-profile index rejection missing.',1;
  SET @Operation+=1;
 END;
 SET @Stage+=1;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
