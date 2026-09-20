/* DGN-007: reversibler Rückfall und begrenzte XE-Bereinigung; kein Datenbank-Drop. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @SessionName sysname=N'SQLPERF_DGN007_LOCAL',@Sql nvarchar(max),@Original nvarchar(max),@Restore nvarchar(max),@Expected sysname=N'SQLPERF_LAB_DGN007_LOCAL',@ProcedurePosition int;
IF DB_NAME()<>@Expected THROW 51011, 'FAIL_CONTRACT: Cleanup muss in der markierten DGN-007-Testdatenbank laufen.', 1;
DECLARE @Project nvarchar(128),@Contract nvarchar(32),@DemoId varchar(7),@RunToken varchar(20);
SELECT @Project=MAX(CASE WHEN name=N'SQLPERF.Project' THEN CONVERT(nvarchar(128),value) END),@Contract=MAX(CASE WHEN name=N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(32),value) END),@DemoId=MAX(CASE WHEN name=N'SQLPERF.DemoId' THEN CONVERT(varchar(7),value) END),@RunToken=MAX(CASE WHEN name=N'SQLPERF.RunToken' THEN CONVERT(varchar(20),value) END)
FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0;
IF @Project<>N'SQL_PerformanceSchulung' OR @Contract<>N'1.0' OR @DemoId<>'DGN-007' OR @RunToken<>'LOCAL'
    THROW 51013, 'FAIL_CLEANUP: Die vier DGN-007-Eigentumsmarker stimmen nicht überein.', 1;
IF OBJECT_ID(N'lab.Dgn007ReferenceState',N'U') IS NOT NULL
BEGIN
    SELECT @Original=OriginalProcedureDefinition FROM lab.Dgn007ReferenceState WHERE StateId=1 AND MitigationApplied=1;
    IF @Original IS NOT NULL
    BEGIN
        SET @ProcedurePosition=CHARINDEX(N'PROCEDURE',@Original);
        IF @ProcedurePosition=0 THROW 51014, 'FAIL_CLEANUP: Der erwartete Prozedurkopf für den Rückfall fehlt.', 1;
        SET @Restore=N'ALTER '+SUBSTRING(@Original,@ProcedurePosition,LEN(@Original));
        EXEC sys.sp_executesql @Restore;
    END;
    UPDATE lab.Dgn007ReferenceState SET OriginalProcedureDefinition=NULL,OriginalChecksum=NULL,MitigationApplied=0,T2Utc=NULL,XeStartedUtc=NULL WHERE StateId=1;
END;
IF OBJECT_ID(N'lab.IncidentQueryStoreProfile',N'U') IS NOT NULL
    DELETE FROM lab.IncidentQueryStoreProfile WHERE IncidentPhase=N'T2_COMPARISON';
DELETE FROM lab.IncidentState WHERE IncidentPhase=N'T2_COMPARISON';
IF EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=@SessionName)
BEGIN
    SET @Sql=N'ALTER EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER STATE=STOP;'; EXEC sys.sp_executesql @Sql;
END;
IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName)
BEGIN
    SET @Sql=N'DROP EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER;'; EXEC sys.sp_executesql @Sql;
END;
SELECT 1 AS Sequence,'CLEANUP' AS Phase,'SUMMARY' AS CheckId,'PASS' AS Outcome,'OK' AS Code,
       N'Originalprozedur wiederhergestellt; XE-Session entfernt' AS ObservedValue,N'reversibler Rückfall ohne Datenbank-Drop' AS RequiredValue,
       N'Der Adapter-Cleanup bleibt für den markergebundenen Datenbankabbau zuständig.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
