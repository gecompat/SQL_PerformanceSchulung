"""Bounded IDX-007 two-burst live wait/page binding pilot."""
from __future__ import annotations

import json
import os
import secrets
import string
import subprocess
import sys
import time
from datetime import datetime


PROFILES = {
    15: ("15.0.4500.2", "sha256:07d7dedecdbfcf6776035dc5eefb5bfd9aa1804b2f6b99f7dedb397d8a599069"),
    16: ("16.0.4305.5", "sha256:cf8f0ab2ebe61feec2eed2629061a07d247f791c2a8ddda74a4ac9f06a291718"),
    17: ("17.0.5035.5", "sha256:6972fb831759433def6a34e107fa32a85230bff5af8014c6263fe4633ea9cc0f"),
}
DB = "SQLPERF_LAB_IDX007_PENDING"
ACTORS = 48
ROWS_PER_BURST = 1


class PilotError(RuntimeError):
    pass


def run(args: list[str], env: dict[str, str], *, input: str | None = None,
        check: bool = True, timeout: int = 45) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, env=env, input=input, text=True,
                            encoding="utf-8", errors="replace", capture_output=True,
                            timeout=timeout, check=False)
    if check and result.returncode:
        raise PilotError(f"command failed ({result.returncode}): {(result.stdout + result.stderr)[-1000:]}")
    return result


def sqlcmd(container: str, env: dict[str, str], query: str, *, check: bool = True) -> str:
    result = run([
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", container, "sh", "-lc",
        'if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then s=/opt/mssql-tools18/bin/sqlcmd; else s=/opt/mssql-tools/bin/sqlcmd; fi; "$s" -S 127.0.0.1 -U sa -C -b -h -1 -W -w 8000 -s "|" -i /dev/stdin',
    ], env, input=query, check=check, timeout=60)
    return result.stdout


def sqlcmd_actor(container: str, env: dict[str, str], query: str) -> subprocess.Popen[str]:
    args = [
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", container, "sh", "-lc",
        'if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then s=/opt/mssql-tools18/bin/sqlcmd; else s=/opt/mssql-tools/bin/sqlcmd; fi; "$s" -S 127.0.0.1 -U sa -C -b -h -1 -W -w 8000 -s "|" -i /dev/stdin',
    ]
    proc = subprocess.Popen(args, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    assert proc.stdin is not None
    proc.stdin.write(query)
    proc.stdin.flush()
    proc.stdin.close()
    # communicate() attempts to flush stdin unless the attribute is cleared.
    proc.stdin = None
    return proc


def create_xe_sql(session: str, database_id: int) -> str:
    return f"""
SET NOCOUNT ON;
IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'{session}')
    THROW 51020,'IDX-007 pilot XE session name collision',1;
CREATE EVENT SESSION [{session}] ON SERVER
ADD EVENT sqlserver.latch_suspend_begin
(
    ACTION(package0.event_sequence,sqlserver.session_id,sqlserver.request_id)
    WHERE ([database_id]=({database_id}))
),
ADD EVENT sqlserver.latch_suspend_end
(
    ACTION(package0.event_sequence,sqlserver.session_id,sqlserver.request_id)
    WHERE ([database_id]=({database_id}))
)
ADD TARGET package0.ring_buffer(SET max_memory=(1024))
WITH (MAX_MEMORY=4096 KB,EVENT_RETENTION_MODE=ALLOW_SINGLE_EVENT_LOSS,
      MAX_DISPATCH_LATENCY=1 SECONDS,MAX_EVENT_SIZE=0 KB,
      MEMORY_PARTITION_MODE=NONE,TRACK_CAUSALITY=OFF,STARTUP_STATE=OFF);
ALTER EVENT SESSION [{session}] ON SERVER STATE=START;
SELECT 'XE_STARTED|{session}';
"""


def read_xe_sql(session: str, stage: int) -> str:
    return f"""
SET NOCOUNT ON;
SET QUOTED_IDENTIFIER ON;
WAITFOR DELAY '00:00:01';
DECLARE @target xml,@drops bigint,@drop_buffers bigint,@truncated bit;
SELECT @target=TRY_CONVERT(xml,t.target_data),@drops=s.dropped_event_count,
       @drop_buffers=s.dropped_buffer_count
FROM sys.dm_xe_sessions AS s
JOIN sys.dm_xe_session_targets AS t ON t.event_session_address=s.address
WHERE s.name=N'{session}' AND t.target_name=N'ring_buffer';
IF @target IS NULL THROW 51021,'IDX-007 pilot ring buffer is unavailable',1;
SET @truncated=CASE WHEN @target.exist('/RingBufferTarget[@truncated="1"]')=1 THEN 1 ELSE 0 END;
SELECT CONCAT('XE_STATS|{stage}|',@drops,'|',@drop_buffers,'|',@target.value('count(/RingBufferTarget/event)','int'),'|',@truncated);
SELECT CONCAT('XE_ROW|{stage}|',
  n.value('(@name)[1]','nvarchar(40)'),'|',
  n.value('(@timestamp)[1]','nvarchar(64)'),'|',
  n.value('(action[@name="event_sequence"]/value/text())[1]','bigint'),'|',
  n.value('(action[@name="session_id"]/value/text())[1]','int'),'|',
  n.value('(action[@name="request_id"]/value/text())[1]','int'),'|',
  n.value('(data[@name="database_id"]/value/text())[1]','int'),'|',
  n.value('(data[@name="file_id"]/value/text())[1]','int'),'|',
  n.value('(data[@name="page_id"]/value/text())[1]','int'),'|',
  COALESCE(n.value('(data[@name="mode"]/text/text())[1]','nvarchar(32)'),''),'|',
  COALESCE(n.value('(data[@name="class"]/text/text())[1]','nvarchar(32)'),''),'|',
  COALESCE(n.value('(data[@name="success"]/value/text())[1]','nvarchar(8)'),''),'|',
  COALESCE(n.value('(data[@name="duration"]/value/text())[1]','nvarchar(32)'),''))
FROM @target.nodes('/RingBufferTarget/event') AS ring(n)
WHERE n.value('(@name)[1]','nvarchar(40)') IN (N'latch_suspend_begin',N'latch_suspend_end')
  AND n.value('(action[@name="session_id"]/value/text())[1]','int')
      IN (SELECT SessionId FROM [{DB}].lab.ActorSessions)
ORDER BY n.value('(action[@name="event_sequence"]/value/text())[1]','bigint');
"""


def drop_xe_sql(session: str) -> str:
    return f"""
SET NOCOUNT ON;
IF EXISTS(SELECT 1 FROM sys.dm_xe_sessions WHERE name=N'{session}')
    ALTER EVENT SESSION [{session}] ON SERVER STATE=STOP;
IF EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'{session}')
    DROP EVENT SESSION [{session}] ON SERVER;
SELECT CONCAT('XE_ABSENT|',CASE WHEN EXISTS(SELECT 1 FROM sys.server_event_sessions WHERE name=N'{session}') THEN 0 ELSE 1 END);
"""


def parse_wait_pairs(output: str, stage: int, bindings: dict[int, int], database_id: int):
    stats = next((line for line in output.splitlines() if line.startswith(f"XE_STATS|{stage}|")), None)
    if stats is None:
        raise PilotError("XE capture summary is missing")
    _, _, dropped, dropped_buffers, event_count, truncated = stats.split("|")
    if int(dropped) or int(dropped_buffers) or truncated != "0" or int(event_count) > 4096:
        raise PilotError("XE target reported loss, truncation, or cap overflow")
    rows = []
    for line in output.splitlines():
        if not line.startswith(f"XE_ROW|{stage}|"):
            continue
        fields = line.split("|")
        (_, _, event_name, stamp, seq, session_id, request_id, db_id, file_id, page_id,
         mode, latch_class, success, duration) = fields
        sid, rid = int(session_id), int(request_id)
        if sid not in bindings or rid != bindings[sid]:
            raise PilotError("XE session/request binding differs from the expected actor request")
        rows.append({
            "event": event_name, "stamp": datetime.fromisoformat(stamp.replace("Z", "+00:00")),
            "seq": int(seq), "sid": sid, "rid": rid, "db": int(db_id),
            "file": int(file_id), "page": int(page_id), "mode": mode.upper(),
            "class": latch_class.upper(), "success": success.lower(),
            "duration": int(duration or 0),
        })
    sequences = [row["seq"] for row in rows]
    if len(sequences) != len(set(sequences)):
        raise PilotError("XE event sequence contains duplicate values")
    grouped: dict[tuple[int, int], dict[str, list[dict]]] = {}
    for row in rows:
        grouped.setdefault((row["sid"], row["rid"]), {"latch_suspend_begin": [], "latch_suspend_end": []})[row["event"]].append(row)
    pairs = []
    for key, kinds in grouped.items():
        begins = sorted(kinds["latch_suspend_begin"], key=lambda row: row["seq"])
        ends = sorted(kinds["latch_suspend_end"], key=lambda row: row["seq"])
        if len(begins) != len(ends):
            raise PilotError("XE latch begin/end event counts do not balance per actor request")
        for begin, end in zip(begins, ends):
            if begin["seq"] >= end["seq"]:
                raise PilotError("XE latch interval is not chronological by event sequence")
            if ((begin["db"], begin["file"], begin["page"], begin["mode"], begin["class"])
                    != (end["db"], end["file"], end["page"], end["mode"], end["class"])):
                raise PilotError("XE latch begin/end resource binding changed")
            if (begin["db"] == database_id and begin["file"] > 0 and begin["page"] > 0 and
                    begin["class"] == "BUF" and begin["mode"] in {"EX", "EXCLUSIVE"} and
                    end["success"] in {"1", "true"} and
                    0 < end["duration"] <= 60_000_000):
                pairs.append({"sid": begin["sid"], "rid": begin["rid"], "db": begin["db"],
                              "file": begin["file"], "page": begin["page"],
                              "begin_seq": begin["seq"], "end_seq": end["seq"],
                              "duration_us": end["duration"]})
    overlaps = []
    for index, left in enumerate(pairs):
        for right in pairs[index + 1:]:
            if (left["sid"] != right["sid"] and (left["db"], left["file"], left["page"])
                    == (right["db"], right["file"], right["page"])
                    and max(left["begin_seq"], right["begin_seq"])
                    < min(left["end_seq"], right["end_seq"])):
                overlaps.append((left, right))
    return rows, pairs, overlaps


def page_metadata_sql(addresses: set[tuple[int, int]]) -> str:
    if not addresses or len(addresses) > 128:
        raise PilotError("candidate page address set is empty or over its fixed cap")
    values = ",".join(f"({file_id},{page_id})" for file_id, page_id in sorted(addresses))
    return f"""
SET NOCOUNT ON; USE [{DB}];
DECLARE @candidate table(FileId int NOT NULL,PageId int NOT NULL);
INSERT @candidate(FileId,PageId) VALUES {values};
DECLARE @meta table(FileId int,PageId int,ObjectId int,IndexId int,PartitionId bigint,PageLevel int,
 PrevFile int,PrevPage int,NextFile int,NextPage int,PrevObjectId int,PrevIndexId int,
 PrevPartitionId bigint,PrevPageLevel int,PrevNextFile int,PrevNextPage int,LeafPages bigint);
DECLARE @file int,@page int;
DECLARE page_cursor CURSOR LOCAL FAST_FORWARD FOR SELECT FileId,PageId FROM @candidate;
OPEN page_cursor; FETCH NEXT FROM page_cursor INTO @file,@page;
WHILE @@FETCH_STATUS=0
BEGIN
  BEGIN TRY
    INSERT @meta
    SELECT @file,@page,i.object_id,i.index_id,i.partition_id,i.page_level,
      COALESCE(i.prev_page_file_id,0),COALESCE(i.prev_page_page_id,0),
      COALESCE(i.next_page_file_id,0),COALESCE(i.next_page_page_id,0),
      COALESCE(p.object_id,0),COALESCE(p.index_id,0),COALESCE(p.partition_id,0),COALESCE(p.page_level,-1),
      COALESCE(p.next_page_file_id,0),COALESCE(p.next_page_page_id,0),ps.leaf_pages
    FROM sys.dm_db_page_info(DB_ID(),@file,@page,'DETAILED') AS i
    OUTER APPLY sys.dm_db_page_info(DB_ID(),NULLIF(i.prev_page_file_id,0),NULLIF(i.prev_page_page_id,0),'DETAILED') AS p
    CROSS APPLY (SELECT SUM(page_count) AS leaf_pages
      FROM sys.dm_db_index_physical_stats(DB_ID(),OBJECT_ID(N'dbo.Hot'),1,NULL,'DETAILED')
      WHERE index_level=0 AND alloc_unit_type_desc='IN_ROW_DATA') AS ps;
  END TRY
  BEGIN CATCH
    -- Invalid or deallocated event resources are not candidates for this proof.
  END CATCH;
  FETCH NEXT FROM page_cursor INTO @file,@page;
END;
CLOSE page_cursor; DEALLOCATE page_cursor;
SELECT CONCAT('META|',FileId,'|',PageId,'|',ObjectId,'|',IndexId,'|',PartitionId,'|',PageLevel,'|',
 PrevFile,'|',PrevPage,'|',NextFile,'|',NextPage,'|',PrevObjectId,'|',PrevIndexId,'|',PrevPartitionId,'|',
 PrevPageLevel,'|',PrevNextFile,'|',PrevNextPage,'|',LeafPages) FROM @meta;
"""


def wait_until(name: str, env: dict[str, str], sql: str, expected: str,
               *, seconds: float = 20) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        output = sqlcmd(name, env, sql, check=False)
        if expected in output.splitlines():
            return
        time.sleep(0.05)
    raise PilotError(f"bounded state wait expired for {expected}")


def run_live_pilot(major: int) -> int:
    global DB
    build, digest = PROFILES[major]
    run_token = secrets.token_hex(4).upper()
    DB = f"SQLPERF_LAB_IDX007_{run_token}"
    name = f"sqlperf-idx007-xe-{major}-{secrets.token_hex(4)}"
    owner = secrets.token_hex(16)
    password = "Aa7!" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(28))
    env = os.environ.copy()
    env.update(MSSQL_SA_PASSWORD=password, SQLCMDPASSWORD=password)
    created = False
    database_created = False
    actors: list[subprocess.Popen[str]] = []
    xe_sessions: list[str] = []
    try:
        image = "mcr.microsoft.com/mssql/server@" + digest
        run(["docker", "run", "--pull=never", "--name", name,
             "--label", f"sqlperf.ci.owner={owner}", "--label", "sqlperf.ci.subject=IDX007-XE-LIVE-PILOT",
             "--network", "none", "--cpus=2", "--memory=4g", "--memory-swap=4g", "--restart=no",
             "-e", "ACCEPT_EULA=Y", "-e", "MSSQL_PID=Developer", "--env", "MSSQL_SA_PASSWORD", "-d", image], env, timeout=60)
        created = True
        for _ in range(90):
            logs = run(["docker", "logs", name], env, check=False)
            if "SQL Server is now ready for client connections" in logs.stdout + logs.stderr:
                break
            time.sleep(2)
        else:
            raise PilotError("SQL Server ready timeout")
        for _ in range(30):
            login = sqlcmd(name, env, "SET NOCOUNT ON; SELECT 1;", check=False)
            if "1" in login.split():
                break
            time.sleep(2)
        else:
            raise PilotError("SQLCMD login timeout")

        engine_profile = sqlcmd(name, env, "SET NOCOUNT ON; SELECT CONCAT('ENGINE_BUILD|',CONVERT(varchar(32),SERVERPROPERTY('ProductVersion')));")
        if f"ENGINE_BUILD|{build}" not in engine_profile.splitlines():
            raise PilotError(f"container engine build differs from pinned profile: {engine_profile.strip()}")
        print(f"ENGINE_BUILD|{build}|PASS")

        setup = f"""
SET NOCOUNT ON; IF DB_ID(N'{DB}') IS NOT NULL THROW 51000,'database name collision',1; CREATE DATABASE [{DB}];
GO
ALTER DATABASE [{DB}] SET COMPATIBILITY_LEVEL={major * 10};
GO
USE [{DB}];
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.Project',@value=N'SQL_PerformanceSchulung';
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.ContractVersion',@value=N'1.0';
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.DemoId',@value=N'IDX-007';
EXEC sys.sp_addextendedproperty @name=N'SQLPERF.RunToken',@value=N'{run_token}';
CREATE TABLE dbo.Hot(KeyValue bigint IDENTITY(1,1) NOT NULL, CONSTRAINT PK_Hot PRIMARY KEY CLUSTERED(KeyValue) WITH (FILLFACTOR=1));
GO
CREATE SCHEMA lab;
GO
CREATE TABLE lab.ActorSessions(SessionId smallint NOT NULL PRIMARY KEY,RequestId int NOT NULL,Done1 bit NOT NULL DEFAULT(0),Done2 bit NOT NULL DEFAULT(0));
CREATE TABLE lab.Go(Stage int NOT NULL PRIMARY KEY);
DECLARE @seed int=0; WHILE @seed<451 BEGIN INSERT dbo.Hot DEFAULT VALUES; SET @seed+=1; END;
GO
ALTER INDEX PK_Hot ON dbo.Hot REBUILD WITH (FILLFACTOR=10);
GO
SELECT CONCAT('DBID|',DB_ID());
"""
        setup_output = sqlcmd(name, env, setup)
        database_created = True
        database_id = int(next(line.split("|", 1)[1] for line in setup_output.splitlines() if line.startswith("DBID|")))
        compatibility = sqlcmd(name, env, f"SET NOCOUNT ON; SELECT CONCAT('COMPATIBILITY|',compatibility_level) FROM sys.databases WHERE name=N'{DB}';")
        if f"COMPATIBILITY|{major * 10}" not in compatibility.splitlines():
            raise PilotError("synthetic database compatibility level differs from the selected engine major")
        print(f"COMPATIBILITY|{major * 10}|PASS")
        profile = sqlcmd(name, env, f"""
SET NOCOUNT ON;
SELECT CONCAT('XE_PROFILE|',
 (SELECT COUNT(DISTINCT o.name) FROM sys.dm_xe_objects AS o JOIN sys.dm_xe_packages AS p ON p.guid=o.package_guid WHERE p.name=N'sqlserver' AND o.object_type=N'event' AND o.name IN(N'latch_suspend_begin',N'latch_suspend_end')),'|',
 (SELECT COUNT(*) FROM sys.dm_xe_object_columns AS c JOIN sys.dm_xe_objects AS o ON o.name=c.object_name AND o.package_guid=c.object_package_guid JOIN sys.dm_xe_packages AS p ON p.guid=o.package_guid WHERE p.name=N'sqlserver' AND o.object_type=N'event' AND ((o.name=N'latch_suspend_begin' AND c.name IN(N'database_id',N'file_id',N'page_id',N'mode',N'class')) OR (o.name=N'latch_suspend_end' AND c.name IN(N'database_id',N'file_id',N'page_id',N'mode',N'class',N'success',N'duration')))),'|',
 (SELECT COUNT(DISTINCT o.name) FROM sys.dm_xe_objects AS o JOIN sys.dm_xe_packages AS p ON p.guid=o.package_guid WHERE p.name IN(N'sqlserver',N'package0') AND o.object_type=N'action' AND o.name IN(N'session_id',N'request_id',N'event_sequence')));
SELECT CONCAT('XE_DURATION_UNIT|',COALESCE(c.description,N''))
FROM sys.dm_xe_object_columns AS c
JOIN sys.dm_xe_objects AS o ON o.name=c.object_name AND o.package_guid=c.object_package_guid
JOIN sys.dm_xe_packages AS p ON p.guid=o.package_guid
WHERE p.name=N'sqlserver' AND o.name=N'latch_suspend_end' AND c.name=N'duration' AND c.column_type=N'data';
""")
        profile_line = next((line for line in profile.splitlines() if line.startswith("XE_PROFILE|")), "")
        if profile_line != "XE_PROFILE|2|12|3":
            raise PilotError(f"latch XE profile differs from the accepted shape: {profile_line}")
        print(f"XE_PROFILE|build={build}|events=2|fields=12|actions=3|PASS")
        duration_unit = next((line for line in profile.splitlines() if line.startswith("XE_DURATION_UNIT|")), "XE_DURATION_UNIT|MISSING")
        if "microseconds" not in duration_unit.lower():
            raise PilotError(f"latch XE duration unit is not verified: {duration_unit}")
        print(duration_unit)

        for _ in range(ACTORS):
            actor_sql = f"""
SET NOCOUNT ON; USE [{DB}]; DECLARE @spid smallint=@@SPID,@request_id int,@i int=0;
SELECT @request_id=request_id FROM sys.dm_exec_requests WHERE session_id=@spid;
INSERT lab.ActorSessions(SessionId,RequestId) VALUES(@spid,@request_id);
WHILE NOT EXISTS(SELECT 1 FROM lab.Go WHERE Stage=1) WAITFOR DELAY '00:00:00.002';
WHILE @i<{ROWS_PER_BURST} BEGIN INSERT dbo.Hot DEFAULT VALUES; WAITFOR DELAY '00:00:00.010'; SET @i+=1; END;
UPDATE lab.ActorSessions SET Done1=1 WHERE SessionId=@spid;
WHILE NOT EXISTS(SELECT 1 FROM lab.Go WHERE Stage=2) WAITFOR DELAY '00:00:00.002';
SET @i=0;
WHILE @i<{ROWS_PER_BURST} BEGIN INSERT dbo.Hot DEFAULT VALUES; WAITFOR DELAY '00:00:00.010'; SET @i+=1; END;
UPDATE lab.ActorSessions SET Done2=1 WHERE SessionId=@spid;
SELECT CONCAT('ACTOR|',@spid,'|',@request_id);
"""
            actors.append(sqlcmd_actor(name, env, actor_sql))
        wait_until(name, env, f"SET NOCOUNT ON; USE [{DB}]; SELECT CONCAT('READY|',COUNT(*)) FROM lab.ActorSessions;", f"READY|{ACTORS}")
        bindings_output = sqlcmd(name, env, f"SET NOCOUNT ON; USE [{DB}]; SELECT CONCAT('BIND|',SessionId,'|',RequestId) FROM lab.ActorSessions ORDER BY SessionId;")
        bindings = {int(parts[1]): int(parts[2]) for line in bindings_output.splitlines()
                    if line.startswith("BIND|") for parts in [line.split("|")]}
        if len(bindings) != ACTORS or any(request < 0 for request in bindings.values()):
            raise PilotError("actor request bindings are incomplete")

        captures = []
        for stage in (1, 2):
            session = f"IDX007_{secrets.token_hex(8)}"
            xe_sessions.append(session)
            sqlcmd(name, env, create_xe_sql(session, database_id))
            sqlcmd(name, env, f"SET NOCOUNT ON; USE [{DB}]; INSERT lab.Go(Stage) VALUES({stage});")
            wait_until(name, env,
                f"SET NOCOUNT ON; USE [{DB}]; SELECT CONCAT('DONE|',COUNT(*)) FROM lab.ActorSessions WHERE Done{stage}=1;",
                f"DONE|{ACTORS}")
            capture_output = sqlcmd(name, env, read_xe_sql(session, stage), check=True)
            drop_output = sqlcmd(name, env, drop_xe_sql(session), check=True)
            if f"XE_ABSENT|1" not in drop_output.splitlines():
                raise PilotError("bounded XE session cleanup was not confirmed")
            xe_sessions.remove(session)
            rows, _, overlaps = parse_wait_pairs(capture_output, stage, bindings, database_id)
            if not overlaps:
                shapes = sorted({f"{row['event']}:{row['class']}:{row['mode']}" for row in rows})
                if shapes:
                    print(f"LATCH_SHAPE|stage={stage}|{'/'.join(shapes)}")
                print(f"NOT_PROVEN|stage={stage}|no-overlapping-exclusive-page-latch-waits")
                return 2
            addresses = {(left["file"], left["page"]) for left, _ in overlaps}
            address_meta = sqlcmd(name, env, page_metadata_sql(addresses))
            meta_rows = {}
            for line in address_meta.splitlines():
                if not line.startswith("META|"):
                    continue
                parts = line.split("|")
                values = tuple(map(int, parts[1:]))
                meta_rows[(values[0], values[1])] = values
            valid = []
            for address, values in meta_rows.items():
                # file/page, object/index/partition/level, previous, next, previous-page identity/link, leaf count
                if (values[2] > 0 and values[3] == 1 and values[4] > 0 and values[5] == 0
                        and (values[8], values[9]) == (0, 0)
                        and values[6] > 0 and values[7] > 0
                        and tuple(values[10:14]) == (values[2], values[3], values[4], 0)
                        and tuple(values[14:16]) == address and values[16] > 1):
                    valid.append((address, values))
            if not valid:
                print(f"NOT_PROVEN|stage={stage}|wait-overlap-page-not-terminal-for-target-index")
                return 2
            valid.sort(key=lambda item: (-sum(1 for left, right in overlaps
                if (left["file"], left["page"]) == item[0]), item[0]))
            address, values = valid[0]
            group = next((pair for pair in overlaps if (pair[0]["file"], pair[0]["page"]) == address), None)
            if group is None:
                raise PilotError("terminal page lacks the paired wait overlap");
            captures.append((database_id, address, values))
            left, right = group
            print(f"WAIT_OVERLAP|stage={stage}|sessions={left['sid']},{right['sid']}|request_ids={left['rid']},{right['rid']}|class=BUF|mode=EXCLUSIVE|page={database_id}:{address[0]}:{address[1]}|wait_us={left['duration_us']},{right['duration_us']}|PASS")
            print(f"CHAIN_BRACKET|stage={stage}|index_pages={values[16]}|target_prev={values[6]}:{values[7]}|previous_next={values[14]}:{values[15]}|target_next=0:0|PASS")

        actor_results = []
        for actor in actors:
            stdout, stderr = actor.communicate(timeout=30)
            if actor.returncode:
                raise PilotError("an actor request failed")
            actor_results.extend(line for line in stdout.splitlines() if line.startswith("ACTOR|"))
        if len(actor_results) != ACTORS:
            raise PilotError("actor completion count differs")
        final = sqlcmd(name, env, f"SET NOCOUNT ON; USE [{DB}]; SELECT CONCAT('FINAL|',COUNT_BIG(*)) FROM dbo.Hot;")
        final_count = int(next(line.split("|", 1)[1] for line in final.splitlines() if line.startswith("FINAL|")))
        expected_rows = 451 + ACTORS * ROWS_PER_BURST * 2
        if final_count != expected_rows:
            raise PilotError("exact successful row count differs from the burst contract")
        if len(captures) != 2:
            raise PilotError("both burst captures were not independently verified")
        print(f"RESULT|build={build}|actors={ACTORS}|burst_rows={ROWS_PER_BURST}|final_rows={final_count}|PASS")
        return 0
    finally:
        for session in tuple(xe_sessions):
            try:
                sqlcmd(name, env, drop_xe_sql(session), check=False)
            except (OSError, subprocess.TimeoutExpired, PilotError):
                pass
        for actor in actors:
            if actor.poll() is None:
                actor.kill()
                try:
                    actor.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
        if created:
            try:
                inspected = json.loads(run(["docker", "inspect", name], env).stdout)[0]
                labels = inspected.get("Config", {}).get("Labels", {})
                if labels.get("sqlperf.ci.owner") != owner or inspected.get("HostConfig", {}).get("NetworkMode") != "none":
                    raise PilotError("owned container identity changed; refusing cleanup")
                cleanup_failure: Exception | None = None
                if database_created:
                    try:
                        cleanup = sqlcmd(name, env, f"""
SET NOCOUNT ON; DECLARE @db sysname=N'{DB}',@p nvarchar(128),@c nvarchar(16),@d nvarchar(16),@r nvarchar(16),@sql nvarchar(max),@drop nvarchar(max);
IF DB_ID(@db) IS NOT NULL
BEGIN
 SET @sql=N'SELECT @p=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),@c=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(16),value) END),@d=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(16),value) END),@r=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(16),value) END) FROM '+QUOTENAME(@db)+N'.sys.extended_properties WHERE class=0;';
 EXEC sys.sp_executesql @sql,N'@p nvarchar(128) OUT,@c nvarchar(16) OUT,@d nvarchar(16) OUT,@r nvarchar(16) OUT',@p OUT,@c OUT,@d OUT,@r OUT;
 IF ISNULL(@p,N'')<>N'SQL_PerformanceSchulung' OR ISNULL(@c,N'')<>N'1.0' OR ISNULL(@d,N'')<>N'IDX-007' OR ISNULL(@r,N'')<>N'{run_token}' THROW 51022,'IDX-007 pilot database ownership markers differ',1;
 SET @drop=N'ALTER DATABASE '+QUOTENAME(@db)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE '+QUOTENAME(@db)+N';';
 EXEC sys.sp_executesql @drop;
END;
SELECT CONCAT('DB_ABSENT|',CASE WHEN DB_ID(@db) IS NULL THEN 1 ELSE 0 END);
""", check=True)
                        if "DB_ABSENT|1" not in cleanup.splitlines():
                            raise PilotError("synthetic database cleanup was not confirmed")
                        print("DB_ABSENT=PASS")
                    except (OSError, subprocess.TimeoutExpired, PilotError) as exc:
                        cleanup_failure = exc
                try:
                    run(["docker", "rm", "--force", name], env)
                    if run(["docker", "ps", "-a", "--filter", f"name=^/{name}$", "--format", "{{.ID}}"], env).stdout.strip():
                        raise PilotError("owned container remains after cleanup")
                    print("CONTAINER_REMOVED=PASS")
                except (OSError, subprocess.TimeoutExpired, PilotError) as exc:
                    cleanup_failure = cleanup_failure or exc
                if cleanup_failure is not None:
                    raise PilotError(f"owned resource cleanup failed: {type(cleanup_failure).__name__}: {cleanup_failure}")
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                raise PilotError(f"owned container cleanup failed: {type(exc).__name__}: {exc}") from exc


if __name__ == "__main__":
    try:
        code = run_live_pilot(int(sys.argv[1]))
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, PilotError, StopIteration, ValueError) as exc:
        print(f"idx007-live-pilot: FAIL ({type(exc).__name__}: {exc})", file=sys.stderr)
        code = 1
    raise SystemExit(code)
