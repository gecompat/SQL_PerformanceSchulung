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

SET NOCOUNT ON;
IF DB_ID(N'SQLPERF_LAB_IDX012_$(RunToken)') IS NULL BEGIN SELECT N'ANN_RESTORE|ALREADY_ABSENT';PRINT 'SQLPERF_SUMMARY|PASS|OK';RETURN;END;
EXEC(N'USE [SQLPERF_LAB_IDX012_$(RunToken)];

IF (SELECT COUNT(*) FROM (VALUES
 (N''SQLPERF.Project'',N''SQL_PerformanceSchulung''),
 (N''SQLPERF.ContractVersion'',N''1.0''),
 (N''SQLPERF.DemoId'',N''IDX-012''),
 (N''SQLPERF.RunToken'',N''$(RunToken)'')) e(Name,Expected)
 JOIN sys.extended_properties p ON p.name=e.Name AND p.class=0
 AND DATALENGTH(p.name)=DATALENGTH(e.Name)
 AND CONVERT(varbinary(max),p.name)=CONVERT(varbinary(max),e.Name)
 AND p.major_id=0 AND p.minor_id=0
 WHERE DATALENGTH(CONVERT(nvarchar(max),p.value))=DATALENGTH(e.Expected)
 AND CONVERT(varbinary(max),CONVERT(nvarchar(max),p.value))=
 CONVERT(varbinary(max),e.Expected))<>4
 THROW 51001,''Full ownership binding lost.'',1;


IF OBJECT_ID(N''dbo.PreviewState'',N''U'') IS NULL
 THROW 51003,''Persistent preview baseline missing.'',1;
IF (SELECT COUNT(*) FROM dbo.PreviewState)<>1
 THROW 51003,''Persistent preview baseline count invalid.'',1;
IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE Id=1 AND OriginalValue IN(0,1)
 AND DATALENGTH(RunToken)=DATALENGTH(N''$(RunToken)'')
 AND CONVERT(varbinary(max),RunToken)=CONVERT(varbinary(max),N''$(RunToken)''))
 THROW 51003,''Persistent preview baseline invalid.'',1;

IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE MaxDopOriginal=0)
 THROW 51003,''Persistent actual MAXDOP baseline invalid.'',1;

IF NOT EXISTS(SELECT 1 FROM dbo.PreviewState WHERE OriginalValue=TRY_CONVERT(int,N''$(OriginalPreview)'') AND MaxDopOriginal=0)
 THROW 51003,''Captured original dual baseline changed before recovery.'',1;

DECLARE @Original int=(SELECT OriginalValue FROM dbo.PreviewState),
 @MaxDop int=(SELECT MaxDopOriginal FROM dbo.PreviewState);
IF @Original=0 ALTER DATABASE SCOPED CONFIGURATION SET PREVIEW_FEATURES=OFF;
ELSE ALTER DATABASE SCOPED CONFIGURATION SET PREVIEW_FEATURES=ON;
-- Feste tatsächlich gespeicherte 0; Guard verlangt genau diese Baseline.
ALTER DATABASE SCOPED CONFIGURATION SET MAXDOP=0;
IF (SELECT COUNT(*) FROM sys.database_scoped_configurations WHERE
 (name=N''PREVIEW_FEATURES'' AND TRY_CONVERT(int,value)=@Original) OR
 (name=N''MAXDOP'' AND TRY_CONVERT(int,value)=@MaxDop))<>2
 THROW 51003,''Actual dual restore failed.'',1;
SELECT CONCAT(N''ANN_RESTORE|$(RunToken)|'',@Original,N''|'',@MaxDop);');

PRINT 'SQLPERF_SUMMARY|PASS|OK';
