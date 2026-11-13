SET NOCOUNT ON;

IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4)
    THROW 51023, 'QRY-023 resource guard requires a fresh disposable instance.', 1;

DECLARE @file_count int = (SELECT COUNT(*) FROM tempdb.sys.database_files);
IF @file_count <> 9
    THROW 51023, 'QRY-023 resource guard requires the qualified nine-file TempDB layout.', 1;

DECLARE @configure nvarchar(max);
SELECT @configure = STRING_AGG(
    CONVERT(nvarchar(max), N'ALTER DATABASE tempdb MODIFY FILE (NAME = '
        + QUOTENAME(name) + N', MAXSIZE = 96MB, FILEGROWTH = 64MB);'),
    NCHAR(10))
FROM tempdb.sys.database_files;
EXEC sys.sp_executesql @configure;

IF (SELECT COUNT(*) FROM tempdb.sys.database_files
    WHERE max_size <> 12288 OR growth <> 8192 OR is_percent_growth <> 0) <> 9
    THROW 51023, 'QRY-023 TempDB per-file size and growth limits were not applied.', 1;

IF (SELECT SUM(CONVERT(bigint, max_size)) FROM tempdb.sys.database_files) > 131072
    THROW 51023, 'QRY-023 TempDB maximum exceeds 1 GiB.', 1;

SELECT N'QRY023_TEMPDB_GUARD|PASS|files=9;max_mib=864;growth_mib=64' AS result;
