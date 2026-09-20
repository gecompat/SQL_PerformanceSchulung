/* DGN-007: T0/T1 dokumentieren und die begrenzte, markergefilterte XE-Session vorbereiten. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @TargetDatabase sysname = DB_NAME(), @Expected sysname = N'SQLPERF_LAB_DGN007_LOCAL';
DECLARE @SessionName sysname = N'SQLPERF_DGN007_LOCAL', @Sql nvarchar(max), @DatabaseId int = DB_ID();
IF @TargetDatabase<>@Expected THROW 51002, 'FAIL_CONTRACT: Baseline muss in der markierten DGN-007-Testdatenbank laufen.', 1;
IF OBJECT_ID(N'lab.IncidentState',N'U') IS NULL OR NOT EXISTS (SELECT 1 FROM lab.IncidentState WHERE IncidentPhase=N'T0_BASELINE') OR NOT EXISTS (SELECT 1 FROM lab.IncidentState WHERE IncidentPhase=N'T1_INCIDENT')
BEGIN
    SELECT 1 AS Sequence, 'BASELINE' AS Phase, 'TIME_WINDOWS' AS CheckId, 'SKIP' AS Outcome, 'SKIP_INCIDENT_NOT_REPRODUCED' AS Code,
           N'T0 oder T1 fehlt' AS ObservedValue, N'T0_BASELINE und T1_INCIDENT' AS RequiredValue, N'Der vorbereitete Incidentzustand ist nicht auswertbar.' AS Message;
    PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_INCIDENT_NOT_REPRODUCED'; RETURN;
END;
IF OBJECT_ID(N'lab.Dgn007ReferenceState',N'U') IS NULL
    CREATE TABLE lab.Dgn007ReferenceState(StateId tinyint NOT NULL CONSTRAINT PK_Dgn007ReferenceState PRIMARY KEY CHECK(StateId=1),OriginalProcedureDefinition nvarchar(max) NULL,OriginalChecksum varbinary(32) NULL,MitigationApplied bit NOT NULL CONSTRAINT DF_Dgn007ReferenceState_MitigationApplied DEFAULT(0),T2Utc datetimeoffset(7) NULL,XeStartedUtc datetimeoffset(7) NULL);
IF NOT EXISTS (SELECT 1 FROM lab.Dgn007ReferenceState WHERE StateId=1)
    INSERT lab.Dgn007ReferenceState(StateId) VALUES(1);
IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name=@SessionName)
    THROW 51003, 'FAIL_STATE: Die DGN-007-XE-Session existiert bereits; zuerst Cleanup ausführen.', 1;
SET @Sql=N'CREATE EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER ADD EVENT sqlserver.rpc_completed(SET collect_statement=(0) WHERE ([sqlserver].[database_id]=('+CONVERT(nvarchar(12),@DatabaseId)+N'))) ADD TARGET package0.ring_buffer(SET max_memory=1024) WITH (MAX_MEMORY=1024 KB,EVENT_RETENTION_MODE=ALLOW_SINGLE_EVENT_LOSS,MAX_DISPATCH_LATENCY=5 SECONDS,STARTUP_STATE=OFF); ALTER EVENT SESSION '+QUOTENAME(@SessionName)+N' ON SERVER STATE=START;';
EXEC sys.sp_executesql @Sql;
UPDATE lab.Dgn007ReferenceState SET XeStartedUtc=SYSUTCDATETIME() WHERE StateId=1;
SELECT IncidentPhase,MarkerUtc FROM lab.IncidentState WHERE IncidentPhase IN(N'T0_BASELINE',N'T1_INCIDENT') ORDER BY MarkerUtc;
SELECT 2 AS Sequence, 'BASELINE' AS Phase, 'SUMMARY' AS CheckId, 'PASS' AS Outcome, 'OK' AS Code,
       N'T0/T1 abgegrenzt; XE-Ring-Buffer aktiv' AS ObservedValue, N'getrennte Ausgangs- und Incidentfenster' AS RequiredValue,
       N'Die XE-Aufnahme beginnt erst nach T1 und kann daher nur nachfolgende Vergleichsausführungen begrenzt belegen.' AS Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
