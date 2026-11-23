SET NOCOUNT ON;

DECLARE @ProductMajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
IF @ProductMajorVersion IS NULL OR @ProductMajorVersion <> 17
    THROW 51000, 'SKIP_VERSION: XE catalog probe requires SQL Server 2025.', 1;

SELECT CONCAT(
    N'{"record_type":"ENGINE","product_version":',
    CONCAT(N'"', STRING_ESCAPE(CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion')), 'json'), N'"'),
    N',"product_major_version":', @ProductMajorVersion,
    N',"edition":',
    CONCAT(N'"', STRING_ESCAPE(CONVERT(nvarchar(128), SERVERPROPERTY('Edition')), 'json'), N'"'),
    N'}'
);

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
                N'lock_acquired'
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
  AND package.name = N'sqlserver'
  AND action_object.name IN (
        N'database_id',
        N'query_hash',
        N'query_plan_hash',
        N'session_id',
        N'sql_text',
        N'tsql_stack'
  )
ORDER BY action_object.name;
