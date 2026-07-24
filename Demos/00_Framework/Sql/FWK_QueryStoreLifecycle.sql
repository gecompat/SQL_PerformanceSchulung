/*
    FWK-007 Query Store reference implementation
    Actions: STATUS | ENABLE | CLEAR | RESTORE

    Run only inside a FWK-002-marked test database.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @Action varchar(10) = 'STATUS';
DECLARE @DemoId varchar(7) = 'DGN-003';
DECLARE @RunToken varchar(20) = 'LOCAL';
DECLARE @ConfirmClear bit = 0;
DECLARE @ConfirmRestore bit = 0;
DECLARE @MaxStorageSizeMB bigint = 128;
DECLARE @IntervalLengthMinutes int = 5;
DECLARE @StaleQueryThresholdDays bigint = 1;
DECLARE @DataFlushIntervalSeconds bigint = 60;

DECLARE @ProjectMarker nvarchar(128);
DECLARE @ContractMarker nvarchar(128);
DECLARE @MarkerDemoId varchar(7);
DECLARE @MarkerRunToken varchar(20);
DECLARE @DatabaseName sysname = DB_NAME();
DECLARE @Sql nvarchar(max);

SELECT
    @ProjectMarker = MAX(CASE WHEN ep.name = N'SQLPERF.Project' THEN CONVERT(nvarchar(128), ep.value) END),
    @ContractMarker = MAX(CASE WHEN ep.name = N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(128), ep.value) END),
    @MarkerDemoId = MAX(CASE WHEN ep.name = N'SQLPERF.DemoId' THEN CONVERT(varchar(7), ep.value) END),
    @MarkerRunToken = MAX(CASE WHEN ep.name = N'SQLPERF.RunToken' THEN CONVERT(varchar(20), ep.value) END)
FROM sys.extended_properties AS ep
WHERE ep.class = 0
  AND ep.major_id = 0
  AND ep.minor_id = 0
  AND ep.name IN
      (
          N'SQLPERF.Project',
          N'SQLPERF.ContractVersion',
          N'SQLPERF.DemoId',
          N'SQLPERF.RunToken'
      );

IF DB_ID() <= 4
   OR @ProjectMarker <> N'SQL_PerformanceSchulung'
   OR @ContractMarker <> N'1.0'
   OR @MarkerDemoId <> @DemoId
   OR @MarkerRunToken <> @RunToken
    THROW 51001, 'FAIL_SAFETY: Query Store darf nur in der erwarteten markierten Testdatenbank verändert werden.', 1;

SET @Action = UPPER(@Action);

IF @Action NOT IN ('STATUS', 'ENABLE', 'CLEAR', 'RESTORE')
    THROW 51000, 'FAIL_CONTRACT: Unbekannte Query-Store-Aktion.', 1;

IF @MaxStorageSizeMB NOT BETWEEN 64 AND 2048
   OR @IntervalLengthMinutes NOT IN (1, 5, 10, 15, 30, 60, 1440)
   OR @StaleQueryThresholdDays NOT BETWEEN 1 AND 30
   OR @DataFlushIntervalSeconds NOT BETWEEN 60 AND 900
    THROW 51000, 'FAIL_CONTRACT: Query-Store-Konfiguration liegt außerhalb des Frameworkvertrags.', 1;

IF SCHEMA_ID(N'fwk') IS NULL
    EXEC(N'CREATE SCHEMA fwk AUTHORIZATION dbo;');

IF OBJECT_ID(N'fwk.QueryStoreBaseline', N'U') IS NULL
BEGIN
    CREATE TABLE fwk.QueryStoreBaseline
    (
        DemoId varchar(7) NOT NULL,
        RunToken varchar(20) NOT NULL,
        CapturedAtUtc datetime2(3) NOT NULL,
        DesiredStateDesc nvarchar(60) NOT NULL,
        QueryCaptureModeDesc nvarchar(60) NULL,
        MaxStorageSizeMB bigint NULL,
        IntervalLengthMinutes bigint NULL,
        StaleQueryThresholdDays bigint NULL,
        SizeBasedCleanupModeDesc nvarchar(60) NULL,
        DataFlushIntervalSeconds bigint NULL,
        WaitStatsCaptureModeDesc nvarchar(60) NULL,
        MaxPlansPerQuery bigint NULL,
        CONSTRAINT PK_fwk_QueryStoreBaseline PRIMARY KEY (DemoId, RunToken)
    );
END;

IF @Action = 'STATUS'
BEGIN
    SELECT
        Sequence = 1,
        Phase = 'TELEMETRY',
        CheckId = 'QUERY_STORE_STATUS',
        Outcome = 'PASS',
        Code = 'OK',
        ObservedValue = CONVERT
        (
            nvarchar(4000),
            CONCAT
            (
                N'Desired=', desired_state_desc,
                N'; Actual=', actual_state_desc,
                N'; Capture=', query_capture_mode_desc,
                N'; CurrentMB=', current_storage_size_mb
            )
        ),
        RequiredValue = CONVERT(nvarchar(4000), N'Query-Store-Status der markierten Testdatenbank'),
        Message = CONVERT(nvarchar(4000), N'Query-Store-Status wurde gelesen.')
    FROM sys.database_query_store_options;

    SELECT *
    FROM sys.database_query_store_options;

    SELECT *
    FROM fwk.QueryStoreBaseline
    WHERE DemoId = @DemoId
      AND RunToken = @RunToken;
END
ELSE IF @Action = 'ENABLE'
BEGIN
    IF EXISTS
    (
        SELECT 1
        FROM sys.database_query_store_options
        WHERE query_capture_mode_desc = N'CUSTOM'
    )
    BEGIN
        SELECT
            Sequence = 1,
            Phase = 'TELEMETRY',
            CheckId = 'QUERY_STORE_ENABLE',
            Outcome = 'SKIP',
            Code = 'SKIP_CONFIGURATION',
            ObservedValue = CONVERT(nvarchar(4000), N'CUSTOM'),
            RequiredValue = CONVERT(nvarchar(4000), N'AUTO, ALL, NONE oder OFF'),
            Message = CONVERT(nvarchar(4000), N'CUSTOM-Capture-Policy wird nicht unvollständig überschrieben.');
        PRINT 'SQLPERF_SUMMARY|SKIP|SKIP_CONFIGURATION';
        RETURN;
    END;

    IF NOT EXISTS
    (
        SELECT 1
        FROM fwk.QueryStoreBaseline
        WHERE DemoId = @DemoId
          AND RunToken = @RunToken
    )
    BEGIN
        INSERT fwk.QueryStoreBaseline
        (
            DemoId,
            RunToken,
            CapturedAtUtc,
            DesiredStateDesc,
            QueryCaptureModeDesc,
            MaxStorageSizeMB,
            IntervalLengthMinutes,
            StaleQueryThresholdDays,
            SizeBasedCleanupModeDesc,
            DataFlushIntervalSeconds,
            WaitStatsCaptureModeDesc,
            MaxPlansPerQuery
        )
        SELECT
            @DemoId,
            @RunToken,
            SYSUTCDATETIME(),
            desired_state_desc,
            query_capture_mode_desc,
            max_storage_size_mb,
            interval_length_minutes,
            stale_query_threshold_days,
            size_based_cleanup_mode_desc,
            data_flush_interval_seconds,
            wait_stats_capture_mode_desc,
            max_plans_per_query
        FROM sys.database_query_store_options;
    END;

    SET @Sql =
        N'ALTER DATABASE ' + QUOTENAME(@DatabaseName) + N'
          SET QUERY_STORE = ON
          (
              OPERATION_MODE = READ_WRITE,
              CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = ' + CONVERT(nvarchar(20), @StaleQueryThresholdDays) + N'),
              DATA_FLUSH_INTERVAL_SECONDS = ' + CONVERT(nvarchar(20), @DataFlushIntervalSeconds) + N',
              QUERY_CAPTURE_MODE = AUTO,
              MAX_STORAGE_SIZE_MB = ' + CONVERT(nvarchar(20), @MaxStorageSizeMB) + N',
              INTERVAL_LENGTH_MINUTES = ' + CONVERT(nvarchar(20), @IntervalLengthMinutes) + N',
              SIZE_BASED_CLEANUP_MODE = AUTO,
              WAIT_STATS_CAPTURE_MODE = ON
          );';

    EXEC sys.sp_executesql @Sql;

    SELECT
        Sequence = 1,
        Phase = 'TELEMETRY',
        CheckId = 'QUERY_STORE_ENABLE',
        Outcome = 'PASS',
        Code = 'OK',
        ObservedValue = CONVERT(nvarchar(4000), N'READ_WRITE/AUTO'),
        RequiredValue = CONVERT(nvarchar(4000), N'begrenzte Query-Store-Laborkonfiguration'),
        Message = CONVERT(nvarchar(4000), N'Query Store wurde aktiviert und die Ausgangskonfiguration gesichert.');

    PRINT 'SQLPERF_SUMMARY|PASS|OK';
END
ELSE IF @Action = 'CLEAR'
BEGIN
    IF @ConfirmClear <> 1
        THROW 51001, 'FAIL_SAFETY: Query Store CLEAR benötigt ConfirmClear=1.', 1;

    SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@DatabaseName) + N' SET QUERY_STORE CLEAR ALL;';
    EXEC sys.sp_executesql @Sql;

    SELECT
        Sequence = 1,
        Phase = 'CLEANUP',
        CheckId = 'QUERY_STORE_CLEAR',
        Outcome = 'PASS',
        Code = 'OK',
        ObservedValue = CONVERT(nvarchar(4000), N'Query Store geleert'),
        RequiredValue = CONVERT(nvarchar(4000), N'bestätigte synthetische Testdatenbank'),
        Message = CONVERT(nvarchar(4000), N'Query-Store-Inhalt wurde entfernt.');

    PRINT 'SQLPERF_SUMMARY|PASS|OK';
END
ELSE
BEGIN
    IF @ConfirmRestore <> 1
        THROW 51001, 'FAIL_SAFETY: Query Store RESTORE benötigt ConfirmRestore=1.', 1;

    DECLARE @DesiredStateDesc nvarchar(60);
    DECLARE @QueryCaptureModeDesc nvarchar(60);
    DECLARE @BaselineMaxStorageSizeMB bigint;
    DECLARE @BaselineIntervalLengthMinutes bigint;
    DECLARE @BaselineStaleQueryThresholdDays bigint;
    DECLARE @BaselineSizeBasedCleanupModeDesc nvarchar(60);
    DECLARE @BaselineDataFlushIntervalSeconds bigint;
    DECLARE @BaselineWaitStatsCaptureModeDesc nvarchar(60);
    DECLARE @BaselineMaxPlansPerQuery bigint;

    SELECT
        @DesiredStateDesc = DesiredStateDesc,
        @QueryCaptureModeDesc = QueryCaptureModeDesc,
        @BaselineMaxStorageSizeMB = MaxStorageSizeMB,
        @BaselineIntervalLengthMinutes = IntervalLengthMinutes,
        @BaselineStaleQueryThresholdDays = StaleQueryThresholdDays,
        @BaselineSizeBasedCleanupModeDesc = SizeBasedCleanupModeDesc,
        @BaselineDataFlushIntervalSeconds = DataFlushIntervalSeconds,
        @BaselineWaitStatsCaptureModeDesc = WaitStatsCaptureModeDesc,
        @BaselineMaxPlansPerQuery = MaxPlansPerQuery
    FROM fwk.QueryStoreBaseline
    WHERE DemoId = @DemoId
      AND RunToken = @RunToken;

    IF @DesiredStateDesc IS NULL
        THROW 51002, 'FAIL_STATE: Kein Query-Store-Ausgangszustand für diese Demo-/Run-Kombination vorhanden.', 1;

    IF @DesiredStateDesc = N'OFF'
    BEGIN
        SET @Sql = N'ALTER DATABASE ' + QUOTENAME(@DatabaseName) + N' SET QUERY_STORE = OFF;';
    END
    ELSE
    BEGIN
        IF @QueryCaptureModeDesc NOT IN (N'AUTO', N'ALL', N'NONE')
           OR @DesiredStateDesc NOT IN (N'READ_ONLY', N'READ_WRITE')
            THROW 51002, 'FAIL_STATE: Der Ausgangszustand kann durch FWK-007 nicht vollständig rekonstruiert werden.', 1;

        SET @Sql =
            N'ALTER DATABASE ' + QUOTENAME(@DatabaseName) + N'
              SET QUERY_STORE = ON
              (
                  OPERATION_MODE = ' + @DesiredStateDesc + N',
                  CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = ' + CONVERT(nvarchar(20), @BaselineStaleQueryThresholdDays) + N'),
                  DATA_FLUSH_INTERVAL_SECONDS = ' + CONVERT(nvarchar(20), @BaselineDataFlushIntervalSeconds) + N',
                  QUERY_CAPTURE_MODE = ' + @QueryCaptureModeDesc + N',
                  MAX_STORAGE_SIZE_MB = ' + CONVERT(nvarchar(20), @BaselineMaxStorageSizeMB) + N',
                  INTERVAL_LENGTH_MINUTES = ' + CONVERT(nvarchar(20), @BaselineIntervalLengthMinutes) + N',
                  SIZE_BASED_CLEANUP_MODE = ' + @BaselineSizeBasedCleanupModeDesc + N',
                  MAX_PLANS_PER_QUERY = ' + CONVERT(nvarchar(20), @BaselineMaxPlansPerQuery) + N',
                  WAIT_STATS_CAPTURE_MODE = ' + COALESCE(@BaselineWaitStatsCaptureModeDesc, N'ON') + N'
              );';
    END;

    EXEC sys.sp_executesql @Sql;

    DELETE fwk.QueryStoreBaseline
    WHERE DemoId = @DemoId
      AND RunToken = @RunToken;

    SELECT
        Sequence = 1,
        Phase = 'CLEANUP',
        CheckId = 'QUERY_STORE_RESTORE',
        Outcome = 'PASS',
        Code = 'OK',
        ObservedValue = CONVERT(nvarchar(4000), @DesiredStateDesc),
        RequiredValue = CONVERT(nvarchar(4000), N'erfasster Ausgangszustand'),
        Message = CONVERT(nvarchar(4000), N'Query Store wurde in den erfassten Ausgangszustand zurückgeführt.');

    PRINT 'SQLPERF_SUMMARY|PASS|OK';
END;
