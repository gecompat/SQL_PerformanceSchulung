SET NOCOUNT ON;

DECLARE @ProductMajorVersion int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
IF @ProductMajorVersion <> 17
    THROW 51000, 'SKIP_VERSION: XE catalog probe requires SQL Server 2025.', 1;

SELECT
    CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion')) AS product_version,
    @ProductMajorVersion AS product_major_version,
    CONVERT(nvarchar(128), SERVERPROPERTY('Edition')) AS edition,
    JSON_QUERY((
        SELECT
            package.name AS package_name,
            event_object.name AS event_name,
            event_object.description AS event_description,
            JSON_QUERY((
                SELECT
                    event_column.name AS column_name,
                    event_column.column_type,
                    event_column.type_name,
                    event_column.description AS column_description
                FROM sys.dm_xe_object_columns AS event_column
                WHERE event_column.object_name = event_object.name
                  AND event_column.object_package_guid = event_object.package_guid
                ORDER BY event_column.column_id, event_column.column_type
                FOR JSON PATH, INCLUDE_NULL_VALUES
            )) AS event_columns
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
        ORDER BY event_object.name
        FOR JSON PATH, INCLUDE_NULL_VALUES
    )) AS compile_related_events,
    JSON_QUERY((
        SELECT
            package.name AS package_name,
            action_object.name AS action_name,
            action_object.description AS action_description
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
        ORDER BY action_object.name
        FOR JSON PATH, INCLUDE_NULL_VALUES
    )) AS correlation_actions
FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;
