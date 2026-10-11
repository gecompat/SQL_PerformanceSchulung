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
IF CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),@TargetDatabase) OR DB_ID(@TargetDatabase) IS NULL THROW 51004,'FAIL_STATE: Falscher Datenbankkontext.',1;
IF (SELECT COUNT(*) FROM lab.Documents)<>3 OR (SELECT COUNT(*) FROM lab.VectorFixture)<>3 OR (SELECT COUNT(*) FROM lab.Questions)<>3 OR (SELECT COUNT(*) FROM lab.Replay)<>10
 THROW 51003,'FAIL_RESULT_CONTRACT: Korpus-/Fragen-/Replaybestand fehlt.',1;
IF (SELECT COUNT(*) FROM lab.Chunks)<>3 OR EXISTS(
 SELECT 1 FROM lab.Documents d LEFT JOIN lab.Chunks c ON c.SourceId=d.SourceId
 WHERE c.SourceId IS NULL OR c.ChunkOrder<>1 OR c.ChunkOffset<>1 OR c.ChunkLength<>LEN(d.Content)
 OR CONVERT(varbinary(max),c.ChunkText)<>CONVERT(varbinary(max),d.Content)
 OR CHARINDEX(CONCAT(N'bewahrt Bausteine ',d.FactDays,N' Tage auf.'),d.Content)=0)
 THROW 51003,'FAIL_RESULT_CONTRACT: Quellenbereich oder Faktmetadatum ungueltig.',1;
IF (SELECT COUNT(*) FROM lab.ReplayEvaluation)<>10 OR EXISTS(SELECT 1 FROM lab.ReplayEvaluation WHERE ActualOutcome<>ExpectedOutcome)
 THROW 51003,'FAIL_RESULT_CONTRACT: Antwortbewertung verletzt den eingefrorenen Fall.',1;
IF (SELECT COUNT(*) FROM lab.RetrievedContext WHERE QuestionId=1)<>1 OR NOT EXISTS(SELECT 1 FROM lab.RetrievedContext WHERE QuestionId=1 AND SourceId=11)
 OR EXISTS(SELECT 1 FROM lab.RetrievedContext WHERE QuestionId=2) OR (SELECT COUNT(DISTINCT FactDays) FROM lab.RetrievedContext WHERE QuestionId=3)<>2
 THROW 51003,'FAIL_RESULT_CONTRACT: Positive, fehlende oder widerspruechliche Evidenz fehlt.',1;
DECLARE @Accepted int=(SELECT COUNT(*) FROM lab.ReplayEvaluation WHERE ActualOutcome='ACCEPTED'),
 @Rejected int=(SELECT COUNT(*) FROM lab.ReplayEvaluation WHERE ActualOutcome='REJECTED'),
 @Abstained int=(SELECT COUNT(*) FROM lab.ReplayEvaluation WHERE ActualOutcome='ABSTAINED');
PRINT CONCAT('AI_ASSERT|comparison|accepted_claims|',@Accepted);
PRINT CONCAT('AI_ASSERT|comparison|rejected_claims|',@Rejected);
PRINT CONCAT('AI_ASSERT|comparison|reasoned_abstentions|',@Abstained);
PRINT 'SQLPERF_SUMMARY|PASS|OK';
