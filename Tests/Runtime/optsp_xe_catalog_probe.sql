SET NOCOUNT ON;

DECLARE @ProductMajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
IF @ProductMajorVersion <> 17
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
  AND package.name = N'sqlserver'
  AND (
        event_object.name LIKE N'%compil%'
        OR event_object.description LIKE N'%compil%'
        OR event_object.name IN (
            N'sp_cache_insert',
            N'sql_statement_recompile',
            N'wait_info',
            N'lock_acquired'
        )
  )
ORDER BY event_object.name;

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
