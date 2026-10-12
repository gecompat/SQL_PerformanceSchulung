"""Feste DGN-010-Kosteneingaben vorbereiten; keine SQLausführung oder Clients."""
import importlib.util
from pathlib import Path
import dgn010_cost_evidence as costs

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dgn010_cost_markers',ROOT/'Tests/Runtime/dgn010_marker_controls.py')
markers=importlib.util.module_from_spec(spec);spec.loader.exec_module(markers)

def identity(database_id,object_id):
    for value,minimum in ((database_id,5),(object_id,1)):
        costs.window.integer(value,minimum)
        if value>2147483647:raise ValueError('Actual SQL int identity required')

def state_sql(*,database_id,object_id):
    identity(database_id,object_id)
    return markers.binding(markers.MARKERS,database_id)+f"IF ISNULL(OBJECT_ID(N'lab.SourceRows'),-1)<>{object_id} THROW 51004,'FAIL_STATE: Eigene Sourcebindung verloren.',1; "+markers.STATE_SQL

def build_sql(*,database_id,object_id,kind,cycle,held_lease):
    identity(database_id,object_id)
    if type(kind) is not str or kind not in costs.DDL or type(cycle) is not int or cycle not in (1,2):raise ValueError('Fixed own DDL/cycle required')
    costs.lease(held_lease,object_id,kind=='DROP')
    return _compose(database_id,object_id,kind,cycle,held_lease)

def drop_absent_sql(*,database_id,object_id):
    identity(database_id,object_id)
    return _compose(database_id,object_id,'DROP',1,costs.EMPTY)

def _compose(database_id,object_id,kind,cycle,held_lease):
    sql=BUILD_TEMPLATE
    for name,value in {'Kind':kind,'Cycle':str(cycle),'ObjectId':str(object_id),'Lease':held_lease.replace("'","''")}.items():sql=sql.replace('$('+name+')',value)
    if '$(' in sql:raise ValueError('Unbound SQL input')
    return markers.binding(markers.MARKERS,database_id)+sql

BUILD_TEMPLATE=r"""SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @RawKind nvarchar(max)=N'$(Kind)',@Cycle int=$(Cycle),@Held nvarchar(max)=N'$(Lease)';
IF (CONVERT(varbinary(max),@RawKind) NOT IN(CONVERT(varbinary(max),N'CREATE'),CONVERT(varbinary(max),N'DROP'))) OR @Cycle NOT IN(1,2) THROW 51000,'FAIL_CONTRACT: Fixed cost input.',1;
IF ISNULL(OBJECT_ID(N'lab.SourceRows'),-1)<>$(ObjectId) THROW 51004,'FAIL_STATE: Original own object binding.',1;
DECLARE @Present int=(SELECT COUNT(*) FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND name=N'DGN010_OwnCandidate');
IF @Present<>CASE WHEN @RawKind=N'CREATE' THEN 0 ELSE 1 END THROW 51003,'FAIL_RESULT_CONTRACT: Actual own candidate prestate.',1;
DECLARE @LeaseBefore nvarchar(max)=(SELECT JSON_QUERY(COALESCE((SELECT object_id,index_id,name,type,is_unique,is_primary_key,is_disabled,has_filter,filter_definition FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND DATALENGTH(name)=DATALENGTH(N'DGN010_OwnCandidate') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'DGN010_OwnCandidate') ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) AS indexes,JSON_QUERY(COALESCE((SELECT c.object_id,c.index_id,c.index_column_id,c.column_id,c.key_ordinal,c.is_descending_key,c.is_included_column FROM sys.index_columns c JOIN sys.indexes i ON c.object_id=i.object_id AND c.index_id=i.index_id WHERE i.object_id=OBJECT_ID(N'lab.SourceRows') AND DATALENGTH(i.name)=DATALENGTH(N'DGN010_OwnCandidate') AND CONVERT(varbinary(max),i.name)=CONVERT(varbinary(max),N'DGN010_OwnCandidate') ORDER BY c.index_id,c.index_column_id FOR JSON PATH),N'[]')) AS columns FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF DATALENGTH(@LeaseBefore)<>DATALENGTH(@Held) OR CONVERT(varbinary(max),@LeaseBefore)<>CONVERT(varbinary(max),@Held) THROW 51004,'FAIL_STATE: Full held own index catalog differs.',1;
DECLARE @Ddl nvarchar(max)=CASE WHEN @RawKind=N'CREATE' THEN N'CREATE NONCLUSTERED INDEX DGN010_OwnCandidate ON lab.SourceRows(Id) INCLUDE(Value,Payload) WITH(MAXDOP=1);' ELSE N'DROP INDEX DGN010_OwnCandidate ON lab.SourceRows;' END;
DECLARE @Session int=@@SPID,@Db int=DB_ID(),@Request int,@RequestStarted datetime,@Connection uniqueidentifier,
 @Cpu0 bigint,@Cpu1 bigint,@Reads0 bigint,@Reads1 bigint,@Logical0 bigint,@Logical1 bigint,@Writes0 bigint,@Writes1 bigint,
 @Started datetime2(7),@Ended datetime2(7),@Ordinal int=1,@Impersonating bit=0;
SELECT @Request=request_id,@RequestStarted=start_time,@Connection=connection_id
 FROM sys.dm_exec_requests WHERE session_id=@Session AND database_id=@Db;
IF @@ROWCOUNT<>1 OR @Request IS NULL OR @RequestStarted IS NULL OR @Connection IS NULL
 THROW 51003,'FAIL_STATE: Actual own request identity missing.',1;
SELECT @Cpu0=CONVERT(bigint,cpu_time),@Reads0=CONVERT(bigint,reads),@Logical0=CONVERT(bigint,logical_reads),@Writes0=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request AND database_id=@Db AND start_time=@RequestStarted AND connection_id=@Connection;
IF @@ROWCOUNT<>1 OR @Cpu0 IS NULL OR @Reads0 IS NULL OR @Logical0 IS NULL OR @Writes0 IS NULL OR @Cpu0<0 OR @Reads0<0 OR @Logical0<0 OR @Writes0<0
 THROW 51003,'FAIL_STATE: Actual initial counters missing.',1;
SET @Started=SYSUTCDATETIME();
EXEC sys.sp_executesql @Ddl;
SET @Ended=SYSUTCDATETIME();
SELECT @Cpu1=CONVERT(bigint,cpu_time),@Reads1=CONVERT(bigint,reads),@Logical1=CONVERT(bigint,logical_reads),@Writes1=CONVERT(bigint,writes)
 FROM sys.dm_exec_requests WHERE session_id=@Session AND request_id=@Request AND database_id=@Db AND start_time=@RequestStarted AND connection_id=@Connection;
IF @@ROWCOUNT<>1 OR @Cpu1 IS NULL OR @Reads1 IS NULL OR @Logical1 IS NULL OR @Writes1 IS NULL
 OR @Cpu1<@Cpu0 OR @Reads1<@Reads0 OR @Logical1<@Logical0 OR @Writes1<@Writes0 OR @Ended<@Started
 THROW 51003,'FAIL_STATE: Actual final counters missing.',1;
DECLARE @LeaseAfter nvarchar(max)=(SELECT JSON_QUERY(COALESCE((SELECT object_id,index_id,name,type,is_unique,is_primary_key,is_disabled,has_filter,filter_definition FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') AND DATALENGTH(name)=DATALENGTH(N'DGN010_OwnCandidate') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'DGN010_OwnCandidate') ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) AS indexes,JSON_QUERY(COALESCE((SELECT c.object_id,c.index_id,c.index_column_id,c.column_id,c.key_ordinal,c.is_descending_key,c.is_included_column FROM sys.index_columns c JOIN sys.indexes i ON c.object_id=i.object_id AND c.index_id=i.index_id WHERE i.object_id=OBJECT_ID(N'lab.SourceRows') AND DATALENGTH(i.name)=DATALENGTH(N'DGN010_OwnCandidate') AND CONVERT(varbinary(max),i.name)=CONVERT(varbinary(max),N'DGN010_OwnCandidate') ORDER BY c.index_id,c.index_column_id FOR JSON PATH),N'[]')) AS columns FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
DECLARE @Before nvarchar(max)=(SELECT @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu0 CpuMs,@Reads0 Reads,@Logical0 LogicalReads,@Writes0 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),
 @After nvarchar(max)=(SELECT @Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
 @Cpu1 CpuMs,@Reads1 Reads,@Logical1 LogicalReads,@Writes1 Writes FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
DECLARE @Output nvarchar(max)=(SELECT @RawKind Kind,@Cycle Cycle,CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),@Ddl)),2) DdlSha256,
@Session SessionId,@Request RequestId,@RequestStarted RequestStartTime,@Connection ConnectionId,@Db DatabaseId,
@Cpu1-@Cpu0 CpuMs,@Reads1-@Reads0 Reads,@Logical1-@Logical0 LogicalReads,@Writes1-@Writes0 Writes,
DATEDIFF_BIG(microsecond,@Started,@Ended) ElapsedUs,CONVERT(nvarchar(30),@Started,126) StartedUtc,CONVERT(nvarchar(30),@Ended,126) EndedUtc,
JSON_QUERY(@Before) CountersBefore,JSON_QUERY(@After) CountersAfter,@LeaseBefore LeaseBefore,@LeaseAfter LeaseAfter FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
IF @Output IS NULL OR DATALENGTH(@Output)>100000 THROW 51003,'FAIL_RESULT_CONTRACT: Actual bounded evidence missing.',1;
DECLARE @Chars int=LEN(@Output),@Part int=1,@Parts int=(LEN(@Output)+199)/200;
WHILE @Part<=@Parts
BEGIN
 SELECT CONVERT(varchar(256),'DGN010_BUILDPART|'+CONVERT(varchar(10),@Part)+'|'+CONVERT(varchar(10),@Parts)+'|'+CONVERT(varchar(10),@Chars)+'|'
 +CONVERT(varchar(200),SUBSTRING(@Output,(@Part-1)*200+1,200)));
 SET @Part+=1;
END;
SELECT 'SQLPERF_SUMMARY|PASS|OK';
"""
