SET NOCOUNT ON;

DECLARE @major int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @version nvarchar(128) = CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion'));
DECLARE @target xml;
DECLARE @summary table (
    event_name sysname NOT NULL,
    event_count int NOT NULL,
    statement_nodes int NOT NULL,
    nonempty_statements int NOT NULL,
    missing_event_sequence int NOT NULL,
    missing_session_id int NOT NULL,
    missing_database_id int NOT NULL,
    missing_query_hash int NOT NULL,
    missing_query_plan_hash int NOT NULL
);

IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = N'DGN007_PayloadGate')
    THROW 51000, 'DGN-007 payload gate session name is already present', 1;

BEGIN TRY
    CREATE EVENT SESSION [DGN007_PayloadGate] ON SERVER
    ADD EVENT sqlserver.sql_statement_starting (
        SET collect_statement = (0)
        ACTION (
            package0.event_sequence,
            sqlserver.database_id,
            sqlserver.query_hash,
            sqlserver.query_plan_hash,
            sqlserver.session_id
        )
    ),
    ADD EVENT sqlserver.sql_statement_completed (
        SET collect_statement = (0), collect_parameterized_plan_handle = (0)
        ACTION (
            package0.event_sequence,
            sqlserver.database_id,
            sqlserver.query_hash,
            sqlserver.query_plan_hash,
            sqlserver.session_id
        )
    )
    ADD TARGET package0.ring_buffer (SET max_memory = (1024))
    WITH (
        MAX_MEMORY = 4096 KB,
        EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS,
        MAX_DISPATCH_LATENCY = 1 SECONDS,
        MAX_EVENT_SIZE = 0 KB,
        MEMORY_PARTITION_MODE = NONE,
        TRACK_CAUSALITY = OFF,
        STARTUP_STATE = OFF
    );

    ALTER EVENT SESSION [DGN007_PayloadGate] ON SERVER STATE = START;
    DECLARE @synthetic_marker int;
    SELECT @synthetic_marker = CONVERT(int, 7);

    -- Reading this active target forces buffered events to the ring buffer.
    SELECT @target = TRY_CONVERT(xml, targets.target_data)
    FROM sys.dm_xe_session_targets AS targets
    INNER JOIN sys.dm_xe_sessions AS sessions
        ON sessions.address = targets.event_session_address
    WHERE sessions.name = N'DGN007_PayloadGate'
      AND targets.target_name = N'ring_buffer';

    IF @target IS NULL
        THROW 51001, 'DGN-007 payload gate ring buffer is unavailable', 1;

    ;WITH event_rows AS (
        SELECT
            event_name = event_node.value('(@name)[1]', 'nvarchar(128)'),
            has_statement = event_node.exist('data[@name="statement"]/value[1]'),
            has_statement_text = event_node.exist(
                'data[@name="statement"]/value[1][string-length(.) > 0]'
            ),
            has_event_sequence = event_node.exist('action[@name="event_sequence"]/value'),
            has_session_id = event_node.exist('action[@name="session_id"]/value'),
            has_database_id = event_node.exist('action[@name="database_id"]/value'),
            has_query_hash = event_node.exist('action[@name="query_hash"]/value'),
            has_query_plan_hash = event_node.exist('action[@name="query_plan_hash"]/value')
        FROM @target.nodes('/RingBufferTarget/event') AS ring(event_node)
    )
    INSERT @summary (
        event_name, event_count, statement_nodes, nonempty_statements,
        missing_event_sequence, missing_session_id, missing_database_id, missing_query_hash,
        missing_query_plan_hash
    )
    SELECT
        event_name,
        COUNT(*),
        SUM(CONVERT(int, has_statement)),
        SUM(CONVERT(int, has_statement_text)),
        SUM(1 - has_event_sequence),
        SUM(1 - has_session_id),
        SUM(1 - has_database_id),
        SUM(1 - has_query_hash),
        SUM(1 - has_query_plan_hash)
    FROM event_rows
    WHERE event_name IN (N'sql_statement_starting', N'sql_statement_completed')
    GROUP BY event_name;

    ALTER EVENT SESSION [DGN007_PayloadGate] ON SERVER STATE = STOP;
    DROP EVENT SESSION [DGN007_PayloadGate] ON SERVER;

    SELECT CONCAT(N'DGN007_PAYLOAD|ENGINE|', @major, N'|', @version);
    SELECT CONCAT(
        N'DGN007_PAYLOAD|EVENT|', event_name, N'|', event_count, N'|',
        statement_nodes, N'|', nonempty_statements, N'|',
        missing_event_sequence, N'|', missing_session_id, N'|', missing_database_id, N'|',
        missing_query_hash, N'|', missing_query_plan_hash
    )
    FROM @summary
    ORDER BY event_name;

    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = N'DGN007_PayloadGate')
        THROW 51002, 'DGN-007 payload gate session cleanup was not confirmed', 1;

    SELECT N'DGN007_PAYLOAD|SESSION|ABSENT';
    SELECT N'DGN007_PAYLOAD|END|1';
END TRY
BEGIN CATCH
    IF EXISTS (SELECT 1 FROM sys.dm_xe_sessions WHERE name = N'DGN007_PayloadGate')
        ALTER EVENT SESSION [DGN007_PayloadGate] ON SERVER STATE = STOP;
    IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = N'DGN007_PayloadGate')
        DROP EVENT SESSION [DGN007_PayloadGate] ON SERVER;
    THROW;
END CATCH;
