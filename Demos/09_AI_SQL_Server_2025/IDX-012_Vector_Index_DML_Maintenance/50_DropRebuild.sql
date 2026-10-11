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
 OR EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture
 EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource)
 OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource
 EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture)
 THROW 51003,'Vollständige ursprüngliche Quelle fehlt.',1;
IF (SELECT COUNT(*) FROM sys.vector_indexes)<>1 OR NOT EXISTS(SELECT 1 FROM sys.vector_indexes
 WHERE object_id=OBJECT_ID(N'lab.VectorFixture') AND type=8 AND is_disabled=0 AND is_hypothetical=0
 AND DATALENGTH(name)=DATALENGTH(N'IDX012_OwnVector')
 AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'IDX012_OwnVector')
 AND DATALENGTH(CONVERT(nvarchar(max),vector_index_type))=DATALENGTH(N'DiskANN')
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),vector_index_type))=CONVERT(varbinary(max),N'DiskANN')
 AND DATALENGTH(CONVERT(nvarchar(max),distance_metric))=DATALENGTH(N'COSINE')
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),distance_metric))=CONVERT(varbinary(max),N'COSINE'))
 THROW 51003,'Eigener aktiver Index vor Drop fehlt.',1;
CREATE TABLE #Result(Stage nvarchar(30),Path nvarchar(10),Id int,DistanceValue float);
DECLARE @q VECTOR(3)=CONVERT(VECTOR(3),N'[1,0,0]'),@Step int=0,@Stage nvarchar(30),
 @Output nvarchar(max),@Started datetime2(7),@Ended datetime2(7),@Affected int,
 @BeforeMetadata nvarchar(max),@AfterMetadata nvarchar(max),@BeforeBytes varbinary(max),@AfterBytes varbinary(max);
SET @BeforeMetadata=(SELECT * FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
 ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
SELECT @BeforeBytes=CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture WHERE Id=999;
WHILE @Step<3
BEGIN
 SET @Stage=CASE @Step WHEN 0 THEN N'BASELINE' WHEN 1 THEN N'AFTER_CHANGE' ELSE N'REBUILT' END;
 IF @Step=1
 BEGIN
  DROP INDEX IDX012_OwnVector ON lab.VectorFixture;
  IF EXISTS(SELECT 1 FROM sys.vector_indexes) THROW 51003,'Tatsächlicher Indexdrop fehlt.',1;
  DECLARE @DropTranCount int=@@TRANCOUNT,@DropTranState int=XACT_STATE();
  SET @Output=(SELECT N'LIFECYCLE_DROP' kind,DB_ID() DatabaseId,N'$(RunToken)' RunToken,
   (SELECT COUNT(*) FROM sys.vector_indexes) [IndexCount],
   (SELECT COUNT(*) FROM lab.VectorFixture) [RowCount],
   @DropTranCount TransactionCount,@DropTranState TransactionState
   FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
  IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Dropaufnahme außerhalb Grenze.',1;
  SELECT @Output;
  BEGIN TRY
   BEGIN TRANSACTION;
   -- Die DML erst nach dem tatsächlichen Drop in einem neuen Compile-Scope binden.
   EXEC sys.sp_executesql N'UPDATE lab.VectorFixture SET V=@v WHERE Id=999; SET @n=@@ROWCOUNT;',
    N'@v VECTOR(3),@n int OUTPUT',@v=@q,@n=@Affected OUTPUT;
   SELECT @AfterBytes=CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture WHERE Id=999;
   IF COALESCE(@Affected,-1)<>1 OR @BeforeBytes IS NULL OR @AfterBytes IS NULL OR @BeforeBytes=@AfterBytes
    OR DATALENGTH(@AfterBytes)<>DATALENGTH(CONVERT(varbinary(max),CONVERT(nvarchar(max),@q)))
    OR @AfterBytes<>CONVERT(varbinary(max),CONVERT(nvarchar(max),@q))
    OR (SELECT COUNT(*) FROM lab.VectorFixture)<>999
    OR EXISTS(SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture WHERE Id<>999
    EXCEPT SELECT Id,BytesValue FROM lab.FrozenSource WHERE Id<>999)
    OR EXISTS(SELECT Id,BytesValue FROM lab.FrozenSource WHERE Id<>999
    EXCEPT SELECT Id,CONVERT(varbinary(max),CONVERT(nvarchar(max),V)) FROM lab.VectorFixture WHERE Id<>999)
    THROW 51003,'Exakte eigene Ein-Row-Änderung fehlt.',1;
   COMMIT TRANSACTION;
  END TRY
  BEGIN CATCH
   IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
   THROW;
  END CATCH;
  -- Vor der Ausgabe aufnehmen: JSON-Auswertung verändert keine Transaktionsattestation.
  DECLARE @TranCount int=@@TRANCOUNT,@TranState int=XACT_STATE();
  IF @TranCount<>0 OR @TranState<>0 THROW 51003,'Tatsächlicher Commitabschluss fehlt.',1;
  SET @Output=(SELECT N'LIFECYCLE_CHANGE' kind,DB_ID() DatabaseId,N'$(RunToken)' RunToken,
   @Affected AffectedRows,(SELECT COUNT(*) FROM lab.VectorFixture) [RowCount],@TranCount TransactionCount,@TranState TransactionState,
   CONVERT(bit,1) Committed,CONVERT(bit,1) OtherSourceUnchanged,
   CONVERT(nvarchar(max),@q) NewVector,(SELECT COUNT(*) FROM sys.vector_indexes) [IndexCount]
   FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
  IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Änderungsaufnahme außerhalb Grenze.',1;
  SELECT @Output;
 END;
 IF @Step=2
 BEGIN
  IF COALESCE(TRY_CONVERT(int,SESSIONPROPERTY('QUOTED_IDENTIFIER')),-1)<>1
   THROW 51003,'Tatsächliche Buildoption fehlt.',1;
  SET @Started=SYSUTCDATETIME();
  EXEC(N'CREATE VECTOR INDEX IDX012_OwnVector ON lab.VectorFixture(V)
   WITH (METRIC=''cosine'',TYPE=''diskann'');');
  SET @Ended=SYSUTCDATETIME();
  SET @AfterMetadata=(SELECT * FROM sys.vector_indexes WHERE object_id=OBJECT_ID(N'lab.VectorFixture')
   ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES);
  SET @Output=(SELECT N'LIFECYCLE_REBUILD' kind,DB_ID() DatabaseId,N'$(RunToken)' RunToken,
   DATEDIFF_BIG(MICROSECOND,@Started,@Ended) BuildElapsedUs,
   JSON_QUERY(@BeforeMetadata) BeforeMetadata,JSON_QUERY(@AfterMetadata) AfterMetadata
   FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
  IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Buildaufnahme außerhalb Grenze.',1;
  SELECT @Output;
 END;
 INSERT #Result SELECT TOP(5) @Stage,N'EXACT',Id,VECTOR_DISTANCE('cosine',V,@q)
  FROM lab.VectorFixture ORDER BY VECTOR_DISTANCE('cosine',V,@q),Id;
 IF @Step<>1
  EXEC sys.sp_executesql N'INSERT #Result SELECT @s,N''ANN'',c.Id,r.distance FROM VECTOR_SEARCH(
   TABLE=lab.VectorFixture AS c,COLUMN=V,SIMILAR_TO=@q,METRIC=''cosine'',TOP_N=5) AS r;',
   N'@q VECTOR(3),@s nvarchar(30)',@q=@q,@s=@Stage;
 SET @Step+=1;
END;
DECLARE @Ordinal int=1,@Path nvarchar(10);
WHILE @Ordinal<=5
BEGIN
 SELECT @Stage=CASE WHEN @Ordinal<=2 THEN N'BASELINE' WHEN @Ordinal=3 THEN N'AFTER_CHANGE' ELSE N'REBUILT' END,
  @Path=CASE WHEN @Ordinal IN(2,5) THEN N'ANN' ELSE N'EXACT' END;
 SET @Output=(SELECT N'LIFECYCLE_QUERY' kind,DB_ID() DatabaseId,N'$(RunToken)' RunToken,
  @Ordinal Ordinal,@Stage Stage,@Path Path,
  JSON_QUERY((SELECT Id,DistanceValue FROM #Result WHERE Stage=@Stage AND Path=@Path
   ORDER BY DistanceValue,Id FOR JSON PATH)) rows
  FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
 IF @Output IS NULL OR DATALENGTH(@Output)>120000 THROW 51003,'Suchaufnahme außerhalb Grenze.',1;
 SELECT @Output;
 SET @Ordinal+=1;
END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
