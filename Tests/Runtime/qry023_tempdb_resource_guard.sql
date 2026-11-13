SET NOCOUNT ON;

IF EXISTS (SELECT 1 FROM sys.databases WHERE database_id > 4)
    THROW 51023, 'QRY-023 resource guard requires a fresh disposable instance.', 1;

DECLARE @file_count int;
DECLARE @log_count int;
DECLARE @data_count int;
DECLARE @max_file_mib int;
DECLARE @configure nvarchar(max);
DECLARE @attempt int=0;
DECLARE @stable_passes int=0;
DECLARE @current_file_count int;

/* SQL Server may finish materializing tempdb files after client readiness. Reconfigure
   the complete observed set and require two stable, fully capped observations. */
WHILE @stable_passes<2 AND @attempt<16
BEGIN
    SET @attempt+=1;
    SELECT @file_count=COUNT(*),
           @log_count=SUM(CASE WHEN type=1 THEN 1 ELSE 0 END),
           @data_count=SUM(CASE WHEN type=0 THEN 1 ELSE 0 END)
    FROM tempdb.sys.database_files;
    IF @file_count NOT BETWEEN 2 AND 16 OR @log_count<>1 OR @data_count<>@file_count-1
        THROW 51023, 'QRY-023 resource guard requires one log and one through fifteen data files.', 1;

    SET @max_file_mib=1024/@file_count;
    IF EXISTS (
        SELECT 1 FROM tempdb.sys.database_files
        WHERE CONVERT(bigint,size)>CONVERT(bigint,@max_file_mib)*128
    )
        THROW 51023, 'An existing TempDB file exceeds its bounded per-file maximum.', 1;

    SELECT @configure=STRING_AGG(
        CONVERT(nvarchar(max),N'ALTER DATABASE tempdb MODIFY FILE (NAME = '
            +QUOTENAME(name)+N', MAXSIZE = '
            +CONVERT(nvarchar(10),@max_file_mib)+N'MB, FILEGROWTH = 64MB);'),
        NCHAR(10))
    FROM tempdb.sys.database_files;
    EXEC sys.sp_executesql @configure;

    SELECT @current_file_count=COUNT(*) FROM tempdb.sys.database_files;
    IF @current_file_count=@file_count AND NOT EXISTS (
        SELECT 1 FROM tempdb.sys.database_files
        WHERE max_size<>@max_file_mib*128 OR growth<>8192 OR is_percent_growth<>0
    )
        SET @stable_passes+=1;
    ELSE
        SET @stable_passes=0;

    IF @stable_passes<2 WAITFOR DELAY '00:00:01';
END;

IF @stable_passes<2
BEGIN
    SELECT @file_count=COUNT(*) FROM tempdb.sys.database_files;
    SELECT CONCAT(N'QRY023_TEMPDB_GUARD|DIAG|file_id=',file_id,
        N';type=',type,N';size_pages=',size,N';max_size_pages=',max_size,
        N';growth=',growth,N';is_percent_growth=',is_percent_growth,
        N';attempt=',@attempt,N';stable_passes=',@stable_passes) AS result
    FROM tempdb.sys.database_files
    WHERE max_size<>@max_file_mib*128 OR growth<>8192 OR is_percent_growth<>0;
    THROW 51023, 'QRY-023 TempDB file set did not stabilize within the bounded configuration attempts.', 1;
END;

DECLARE @total_max_mib bigint = (
    SELECT SUM(CONVERT(bigint, max_size)) / 128 FROM tempdb.sys.database_files
);
IF @total_max_mib > 1024
    THROW 51023, 'QRY-023 TempDB maximum exceeds 1 GiB.', 1;

SELECT CONCAT(N'QRY023_TEMPDB_GUARD|PASS|files=', @file_count,
    N';max_mib=', @total_max_mib, N';growth_mib=64') AS result;
