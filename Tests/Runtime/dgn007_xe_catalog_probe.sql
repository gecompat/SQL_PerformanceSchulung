SET NOCOUNT ON;

DECLARE @major int = TRY_CONVERT(int, SERVERPROPERTY('ProductMajorVersion'));
DECLARE @version nvarchar(128) = CONVERT(nvarchar(128), SERVERPROPERTY('ProductVersion'));
DECLARE @edition nvarchar(128) = CONVERT(nvarchar(128), SERVERPROPERTY('Edition'));

SELECT CONCAT(N'DGN007_XE|ENGINE|', @major, N'|', @version, N'|', @edition);

SELECT CONCAT(
    N'DGN007_XE|EVENT|', event_object.name, N'|',
    COALESCE(STRING_AGG(CONCAT(event_column.name, N':', event_column.column_type), N',')
        WITHIN GROUP (ORDER BY event_column.column_id), N'')
)
FROM sys.dm_xe_objects AS event_object
INNER JOIN sys.dm_xe_packages AS package
    ON package.guid = event_object.package_guid
LEFT JOIN sys.dm_xe_object_columns AS event_column
    ON event_column.object_name = event_object.name
   AND event_column.object_package_guid = event_object.package_guid
WHERE event_object.object_type = N'event'
  AND package.name = N'sqlserver'
  AND event_object.name IN (
      N'sql_statement_starting',
      N'sql_statement_completed'
  )
GROUP BY event_object.name
ORDER BY event_object.name;

SELECT CONCAT(N'DGN007_XE|ACTION|', package.name, N'|', action_object.name)
FROM sys.dm_xe_objects AS action_object
INNER JOIN sys.dm_xe_packages AS package
    ON package.guid = action_object.package_guid
WHERE action_object.object_type = N'action'
  AND action_object.name IN (
      N'database_id',
      N'event_sequence',
      N'query_hash',
      N'query_plan_hash',
      N'session_id',
      N'sql_text',
      N'tsql_stack'
  )
ORDER BY package.name, action_object.name;

SELECT N'DGN007_XE|END|1';
