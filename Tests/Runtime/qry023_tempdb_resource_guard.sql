SET NOCOUNT ON;

IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4)
    THROW 51023, 'QRY-023 resource guard requires a fresh disposable instance.', 1;

DECLARE @file_count int = (SELECT COUNT(*) FROM tempdb.sys.database_files);
DECLARE @log_count int = (
    SELECT COUNT(*) FROM tempdb.sys.database_files WHERE type = 1
);
IF @file_count NOT BETWEEN 2 AND 16
   OR @log_count <> 1
   OR (SELECT COUNT(*) FROM tempdb.sys.database_files WHERE type = 0) <> @file_count - 1
    THROW 51023, 'QRY-023 resource guard requires one log and one through fifteen data files.', 1;

DECLARE @max_file_mib int = 1024 / @file_count;
IF EXISTS (
    SELECT 1 FROM tempdb.sys.database_files
    WHERE CONVERT(bigint, size) > CONVERT(bigint, @max_file_mib) * 128
)
    THROW 51023, 'An existing TempDB file exceeds its bounded per-file maximum.', 1;

DECLARE @configure nvarchar(max);
SELECT @configure = STRING_AGG(
    CONVERT(nvarchar(max), N'ALTER DATABASE tempdb MODIFY FILE (NAME = '
        + QUOTENAME(name) + N', MAXSIZE = '
        + CONVERT(nvarchar(10), @max_file_mib) + N'MB, FILEGROWTH = 64MB);'),
    NCHAR(10))
FROM tempdb.sys.database_files;
EXEC sys.sp_executesql @configure;

IF (SELECT COUNT(*) FROM tempdb.sys.database_files
    WHERE max_size <> @max_file_mib * 128 OR growth <> 8192 OR is_percent_growth <> 0) <> @file_count
    THROW 51023, 'QRY-023 TempDB per-file size and growth limits were not applied.', 1;

DECLARE @total_max_mib bigint = (
    SELECT SUM(CONVERT(bigint, max_size)) / 128 FROM tempdb.sys.database_files
);
IF @total_max_mib > 1024
    THROW 51023, 'QRY-023 TempDB maximum exceeds 1 GiB.', 1;

SELECT CONCAT(N'QRY023_TEMPDB_GUARD|PASS|files=', @file_count,
    N';max_mib=', @total_max_mib, N';growth_mib=64') AS result;
