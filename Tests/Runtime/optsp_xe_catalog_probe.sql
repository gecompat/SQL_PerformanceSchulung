SET NOCOUNT ON;

DECLARE @ProductMajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
IF @ProductMajorVersion IS NULL OR @ProductMajorVersion <> 17
    THROW 51000, 'SKIP_VERSION: XE catalog probe requires SQL Server 2025.', 1;

IF COALESCE(CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion')), N'') <> N'17.0.5065.9'
    THROW 51003, 'SKIP_VERSION: XE catalog probe requires build 17.0.5065.9.', 1;

SELECT CONCAT(
    N'{"record_type":"ENGINE","product_version":',
    CONCAT(N'"', STRING_ESCAPE(CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion')), 'json'), N'"'),
    N',"product_major_version":', @ProductMajorVersion,
    N',"edition":',
    CONCAT(N'"', STRING_ESCAPE(CONVERT(nvarchar(128), SERVERPROPERTY('Edition')), 'json'), N'"'),
    N'}'
);

-- Sample the primary-replica option and statistics policy in the current context.
DECLARE @CompileOption int, @LowPriority int;
SELECT @CompileOption = TRY_CONVERT(int, value)
FROM sys.database_scoped_configurations
WHERE name = N'OPTIMIZED_SP_EXECUTESQL';

IF @@ROWCOUNT <> 1 OR @CompileOption IS NULL OR @CompileOption NOT IN (0, 1)
    THROW 51004, 'NOT_PROVEN: expected the convertible compile option.', 1;

SELECT @LowPriority = TRY_CONVERT(int, value)
FROM sys.database_scoped_configurations
WHERE name = N'ASYNC_STATS_UPDATE_WAIT_AT_LOW_PRIORITY';

IF @@ROWCOUNT <> 1 OR @LowPriority IS NULL OR @LowPriority NOT IN (0, 1)
    THROW 51005, 'NOT_PROVEN: expected the convertible statistics option.', 1;

SELECT N'DATABASE_SETTINGS' AS record_type,
       database_id,
       compatibility_level,
       @CompileOption AS optimized_sp_executesql,
       CONVERT(int, is_auto_create_stats_on) AS auto_create_statistics,
       CONVERT(int, is_auto_update_stats_on) AS auto_update_statistics,
       CONVERT(int, is_auto_update_stats_async_on) AS auto_update_statistics_async,
       @LowPriority AS async_stats_update_wait_at_low_priority
FROM sys.databases
WHERE database_id = DB_ID()
FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;


SELECT CONCAT(
    N'{"record_type":"EVENT","package_name":',
    CONCAT(N'"', STRING_ESCAPE(package.name, 'json'), N'"'),
    N',"event_name":',
    CONCAT(N'"', STRING_ESCAPE(event_object.name, 'json'), N'"'),
    N',"event_description":',
    CONCAT(N'"', STRING_ESCAPE(LEFT(COALESCE(event_object.description, N''), 512), 'json'), N'"'),
    N',"event_columns":',
    COALESCE((
        SELECT
            event_column.name AS column_name,
            event_column.column_type,
            event_column.type_name,
            LEFT(event_column.description, 256) AS column_description
        FROM sys.dm_xe_object_columns AS event_column
        WHERE event_column.object_name = event_object.name
          AND event_column.object_package_guid = event_object.package_guid
        ORDER BY event_column.column_id, event_column.column_type
        FOR JSON PATH, INCLUDE_NULL_VALUES
    ), N'[]'),
    N'}'
)
FROM sys.dm_xe_objects AS event_object
INNER JOIN sys.dm_xe_packages AS package
    ON package.guid = event_object.package_guid
WHERE event_object.object_type = N'event'
  AND (
        (package.name = N'sqlserver' AND (
            event_object.name LIKE N'%compil%'
            OR event_object.description LIKE N'%compil%'
            OR event_object.name IN (
                N'sp_cache_insert',
                N'sql_statement_recompile',
                N'lock_acquired',
                N'lock_released',
                N'rpc_starting',
                N'rpc_completed',
                N'sql_statement_completed',
                N'sp_cache_hit'
            )
        ))
        OR (package.name = N'sqlos' AND event_object.name = N'wait_info')
  )
ORDER BY package.name, event_object.name;

-- Capture the build-specific key. The wait name alone does not identify its cause.
DECLARE @WaitMapKey int;
SELECT @WaitMapKey = MIN(wait_map.map_key)
FROM sys.dm_xe_map_values AS wait_map
INNER JOIN sys.dm_xe_packages AS package
    ON package.guid = wait_map.object_package_guid
WHERE package.name = N'sqlos'
  AND wait_map.name = N'wait_types'
  AND wait_map.map_value = N'LCK_M_X'
HAVING COUNT_BIG(*) = 1;

IF @WaitMapKey IS NULL
    THROW 51001, 'NOT_PROVEN: sqlos.wait_types must expose exactly one LCK_M_X key.', 1;

IF (
    SELECT COUNT_BIG(*)
    FROM sys.dm_xe_objects AS event_object
    INNER JOIN sys.dm_xe_packages AS package
        ON package.guid = event_object.package_guid
    WHERE event_object.object_type = N'event'
      AND package.name = N'sqlos' AND event_object.name = N'wait_info'
) <> 1
    THROW 51002, 'NOT_PROVEN: sqlos.wait_info must resolve to exactly one event.', 1;

SELECT CONCAT(
    N'{"record_type":"WAIT_MAP","package_name":"sqlos","map_name":"wait_types","map_key":',
    @WaitMapKey,
    N',"map_value":"LCK_M_X"}'
);

-- Resolve the enum from the event field's type identity, including its package.
SELECT CONCAT(
    N'{"record_type":"FIELD_MAP","event_package":',
    CONCAT(N'"', STRING_ESCAPE(event_package.name, 'json'), N'"'),
    N',"event_name":',
    CONCAT(N'"', STRING_ESCAPE(event_object.name, 'json'), N'"'),
    N',"field_name":',
    CONCAT(N'"', STRING_ESCAPE(event_column.name, 'json'), N'"'),
    N',"map_package":',
    CONCAT(N'"', STRING_ESCAPE(map_package.name, 'json'), N'"'),
    N',"map_name":',
    CONCAT(N'"', STRING_ESCAPE(field_map.name, 'json'), N'"'),
    N',"map_key":', field_map.map_key,
    N',"map_value":',
    CONCAT(N'"', STRING_ESCAPE(LEFT(field_map.map_value, 256), 'json'), N'"'),
    N'}'
)
FROM sys.dm_xe_objects AS event_object
JOIN sys.dm_xe_packages AS event_package
    ON event_package.guid = event_object.package_guid
JOIN sys.dm_xe_object_columns AS event_column
    ON event_column.object_name = event_object.name
   AND event_column.object_package_guid = event_object.package_guid
JOIN sys.dm_xe_map_values AS field_map
    ON field_map.object_package_guid = event_column.type_package_guid
   AND field_map.name = event_column.type_name
JOIN sys.dm_xe_packages AS map_package
    ON map_package.guid = field_map.object_package_guid
WHERE event_object.object_type = N'event'
  AND event_column.column_type = N'data'
  AND (
      (event_package.name = N'sqlserver' AND event_object.name = N'compile_synchronization'
          AND event_column.name IN (N'query_type', N'step'))
      OR (event_package.name = N'sqlos' AND event_object.name = N'wait_info'
          AND event_column.name = N'opcode')
  )
ORDER BY event_package.name, event_object.name, event_column.name, field_map.map_key;

SELECT CONCAT(
    N'{"record_type":"ACTION","package_name":',
    CONCAT(N'"', STRING_ESCAPE(package.name, 'json'), N'"'),
    N',"action_name":',
    CONCAT(N'"', STRING_ESCAPE(action_object.name, 'json'), N'"'),
    N',"action_description":',
    CONCAT(N'"', STRING_ESCAPE(LEFT(COALESCE(action_object.description, N''), 512), 'json'), N'"'),
    N'}'
)
FROM sys.dm_xe_objects AS action_object
INNER JOIN sys.dm_xe_packages AS package
    ON package.guid = action_object.package_guid
WHERE action_object.object_type = N'action'
  AND (
        (package.name = N'sqlserver' AND action_object.name IN (
            N'database_id',
            N'query_hash',
            N'query_plan_hash',
            N'session_id',
            N'sql_text',
            N'tsql_stack',
            N'plan_handle',
            N'request_id'
        ))
        OR (package.name = N'package0' AND action_object.name = N'event_sequence')
  )
ORDER BY package.name, action_object.name;
