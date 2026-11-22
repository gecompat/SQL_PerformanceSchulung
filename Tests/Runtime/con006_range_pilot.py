#!/usr/bin/env python3
"""Bounded CON-006 key-range feasibility pilot on an owned SQL container."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Tests/Runtime"))
import execution_target  # noqa: E402
from execution_target import ExecutionTargetError  # noqa: E402
from Tests.Static.con006_conversion_graph_contract import (  # noqa: E402
    ActorOutcome, CaptureEvidence, GraphIdentity, Verdict,
)
from Tests.Static.con006_range_graph_contract import (  # noqa: E402
    RangeCaptureEvidence, RangeControlEvidence, RangeInsertOutcome,
    evaluate_range_capture, evaluate_range_control,
)


OWNER_LABEL = "sqlperf.ci.owner"
SUBJECT_LABEL = "sqlperf.ci.subject"
MAX_SQL_BYTES = 256 * 1024
ACTOR_SECONDS = 35
WAIT_SECONDS = 12
RUN_TOKEN_PATTERN = re.compile(r"[A-F0-9]{8}\Z")
IMAGE_LOCK = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables/container-images.proposed.json"


class PilotError(RuntimeError):
    pass


def _sql(target: Any, database: str, text: str, timeout: int = 20) -> str:
    command = [
        "docker", "exec", "-i", "-e", "SQLCMDPASSWORD", target.container or "",
        target.sqlcmd_path, "-S", "127.0.0.1", "-d", database, "-U", "sa", "-C",
        "-b", "-r", "1", "-W", "-s", "|", "-h", "-1", "-w", "65535",
    ]
    result = subprocess.run(
        command, input=text, check=False, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
        env=target.child_environment(),
    )
    if result.returncode:
        raise PilotError(f"SQL probe failed in {database} ({result.returncode})")
    if len(result.stdout.encode("utf-8")) > MAX_SQL_BYTES:
        raise PilotError("SQL result exceeded the fixed output limit")
    return result.stdout


def _identity(container: str) -> dict[str, Any]:
    result = subprocess.run(
        ["docker", "inspect", container], capture_output=True, text=True,
        timeout=15, check=False,
    )
    if result.returncode:
        raise PilotError("owned container cannot be inspected")
    items = json.loads(result.stdout)
    if len(items) != 1:
        raise PilotError("container identity is ambiguous")
    return items[0]


def _profile(major: int) -> dict[str, Any]:
    try:
        lock = json.loads(IMAGE_LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PilotError("pinned image lock is unavailable") from exc
    if lock.get("contract_version") != "1.0" or lock.get("status") != "PROPOSED":
        raise PilotError("pinned image lock contract changed")
    if lock.get("runtime_authorized") is not False:
        raise PilotError("shared QRY-023 runtime authorization changed")
    profiles = [item for item in lock.get("profiles", [])
                if item.get("product_major_version") == major]
    if len(profiles) != 1:
        raise PilotError("exactly one pinned engine profile is required")
    profile = profiles[0]
    if (profile.get("platform") != "linux/amd64"
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", profile.get("manifest_digest", ""))
            or profile.get("image") != "mcr.microsoft.com/mssql/server@" + profile["manifest_digest"]
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", profile.get("config_digest", ""))):
        raise PilotError("pinned engine profile is malformed")
    return profile


def _sqlcmd_process(target: Any, database: str, script: str) -> subprocess.Popen[str]:
    command = [
        "docker", "exec", "--interactive", "--env", "SQLCMDPASSWORD",
        target.container or "", target.sqlcmd_path,
        "-S", "127.0.0.1", "-d", database, "-U", "sa", "-C", "-b", "-r", "1",
        "-s", "|", "-w", "65535", "-y", "0",
    ]
    return subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", env=target.child_environment(),
    )


def _run_actor(target: Any, database: str, script: str, timeout: int = ACTOR_SECONDS) -> str:
    process = _sqlcmd_process(target, database, script)
    try:
        stdout, stderr = process.communicate(script, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.communicate(timeout=5)
        raise PilotError("actor SQL exceeded its fixed deadline") from exc
    if process.returncode:
        raise PilotError(f"actor SQL failed ({process.returncode}): {stderr[-2000:]}")
    return stdout


def _setup_sql(database: str, major: int, token: str) -> str:
    level = {15: 150, 16: 160, 17: 170}[major]
    quoted = f"[{database}]"
    return f"""SET NOCOUNT ON;
DECLARE @db sysname=N'{database}';
IF DB_ID(@db) IS NOT NULL THROW 51100,'FAIL_STATE: pilot database already exists',1;
EXEC(N'CREATE DATABASE {quoted}; ALTER DATABASE {quoted} SET RECOVERY SIMPLE; ALTER DATABASE {quoted} SET COMPATIBILITY_LEVEL={level};');
DECLARE @ddl nvarchar(max)=N'USE {quoted};
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.Project'',@value=N''SQL_PerformanceSchulung'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.ContractVersion'',@value=N''1.0'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.DemoId'',@value=N''CON-006'';
EXEC sys.sp_addextendedproperty @name=N''SQLPERF.RunToken'',@value=N''{token}'';
EXEC(N''CREATE SCHEMA lab''); EXEC(N''CREATE SCHEMA fwk'');
CREATE TABLE lab.RangeRows(KeyValue int NOT NULL CONSTRAINT PK_RangeRows PRIMARY KEY CLUSTERED);
INSERT lab.RangeRows(KeyValue) VALUES(10),(50),(90);
CREATE TABLE lab.RangeEvidence(Attempt varchar(8) NOT NULL,RoleName varchar(8) NOT NULL,InsertKey int NOT NULL,SessionId smallint NOT NULL,Outcome varchar(16) NOT NULL,ErrorNumber int NULL,CONSTRAINT PK_RangeEvidence PRIMARY KEY(Attempt,RoleName));
CREATE TABLE lab.RangeRun(RunToken varchar(8) NOT NULL,StartedUtc datetimeoffset(7) NOT NULL,FinishedUtc datetimeoffset(7) NULL,DatabaseId int NOT NULL);
INSERT lab.RangeRun VALUES(''{token}'',TODATETIMEOFFSET(SYSUTCDATETIME(),''+00:00''),NULL,DB_ID());
CREATE TABLE fwk.SignalState(SignalName sysname NOT NULL PRIMARY KEY,SignaledAtUtc datetime2(7) NOT NULL);
EXEC(N''CREATE PROCEDURE fwk.Signal @name sysname AS BEGIN SET NOCOUNT ON; IF EXISTS(SELECT 1 FROM fwk.SignalState WHERE SignalName=@name) UPDATE fwk.SignalState SET SignaledAtUtc=SYSUTCDATETIME() WHERE SignalName=@name; ELSE INSERT fwk.SignalState VALUES(@name,SYSUTCDATETIME()); END'');
EXEC(N''CREATE PROCEDURE fwk.Wait @name sysname,@timeout_ms int AS BEGIN SET NOCOUNT ON; DECLARE @start datetime2(3)=SYSUTCDATETIME(); WHILE NOT EXISTS(SELECT 1 FROM fwk.SignalState WITH(READUNCOMMITTED) WHERE SignalName=@name) BEGIN IF DATEDIFF_BIG(millisecond,@start,SYSUTCDATETIME())>=@timeout_ms THROW 51101,\''''FAIL_TIMEOUT: range signal\'''',1; WAITFOR DELAY \''''00:00:00.050\''''; END END'');';
EXEC sys.sp_executesql @ddl;
SELECT CONCAT('SETUP|',DB_ID(@db));
"""


def _actor_sql(role: str, attempt: str, token: str, key: int,
               low: int, high: int, priority: str) -> str:
    release_barrier = "START_INSERTS" if role == "ACTOR_A" else "A_IS_WAITING"
    comment = f"CON006_RANGE_{token}_{role}"
    return f"""SET NOCOUNT ON; SET XACT_ABORT ON; SET QUOTED_IDENTIFIER ON;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE; SET DEADLOCK_PRIORITY {priority};
DECLARE @sid smallint=@@SPID,@n bigint,@e int=0;
INSERT lab.RangeEvidence VALUES('{attempt}','{role}',{key},@sid,'ACTIVE',NULL);
BEGIN TRY
  BEGIN TRANSACTION;
  SELECT @n=COUNT_BIG(*) FROM lab.RangeRows WITH(INDEX(PK_RangeRows),FORCESEEK)
   WHERE KeyValue>{low} AND KeyValue<{high};
  EXEC fwk.Wait N'{release_barrier}',12000;
  /* {comment} */ INSERT lab.RangeRows(KeyValue) VALUES({key});
  COMMIT TRANSACTION;
  UPDATE lab.RangeEvidence SET Outcome='INSERTED',ErrorNumber=NULL WHERE Attempt='{attempt}' AND RoleName='{role}';
END TRY
BEGIN CATCH
  SET @e=ERROR_NUMBER();
  IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
  UPDATE lab.RangeEvidence SET Outcome=CASE WHEN @e=1205 THEN 'ROLLED_BACK' ELSE 'ERROR' END,ErrorNumber=@e WHERE Attempt='{attempt}' AND RoleName='{role}';
  EXEC fwk.Signal N'{role}_DONE';
  IF @e<>1205 THROW;
END CATCH;
IF NOT EXISTS(SELECT 1 FROM fwk.SignalState WHERE SignalName=N'{role}_DONE') EXEC fwk.Signal N'{role}_DONE';
SELECT CONCAT('ACTOR|{attempt}|{role}|',@sid);
"""


def _control_sql(role: str, token: str, key: int) -> str:
    if role == "ACTOR_A":
        before_insert, after_insert = "B_READY", "A_COMMITTED"
        final_wait = "B_DONE"
    else:
        before_insert, after_insert = "A_COMMITTED", "B_DONE"
        final_wait = None
    wait_before = (f"EXEC fwk.Wait N'{before_insert}',12000;" if before_insert else "")
    wait_after = (f"EXEC fwk.Wait N'{final_wait}',12000;" if final_wait else "")
    ready_signal = "EXEC fwk.Signal N'B_READY';" if role == "ACTOR_B" else ""
    return f"""SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @sid smallint=@@SPID;
INSERT lab.RangeEvidence VALUES('CONTROL','{role}',{key},@sid,'ACTIVE',NULL);
{ready_signal}
{wait_before}
/* CON006_RANGE_{token}_{role}_CONTROL */ INSERT lab.RangeRows(KeyValue) VALUES({key});
UPDATE lab.RangeEvidence SET Outcome='INSERTED' WHERE Attempt='CONTROL' AND RoleName='{role}';
EXEC fwk.Signal N'{after_insert}';
{wait_after}
SELECT CONCAT('CONTROL|{role}|',@sid);
"""


def _poll(target: Any, database: str, query: str, predicate, seconds: float) -> str | None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        output = _sql(target, database, query, timeout=10)
        if predicate(output):
            return output
        time.sleep(0.05)
    return None


def _signals(target: Any, database: str, *names: str) -> None:
    statements = " ".join(f"EXEC fwk.Signal N'{name}';" for name in names)
    _sql(target, database, f"SET NOCOUNT ON; {statements}")


def _optimized_locking_state(target: Any, database: str) -> int | None:
    output = _sql(target, database, """SET NOCOUNT ON;
SELECT CONCAT('OPTLOCK|',COALESCE(CONVERT(varchar(1),DATABASEPROPERTYEX(DB_NAME(),N'IsOptimizedLockingOn')),'NULL'));""")
    line = next((item.strip() for item in output.splitlines()
                 if item.strip().startswith("OPTLOCK|")), None)
    if line is None:
        raise PilotError("optimized-locking state could not be captured")
    value = line.split("|", 1)[1]
    return int(value) if value in {"0", "1"} else None


def _evidence(target: Any, database: str, attempt: str) -> list[dict[str, Any]]:
    output = _sql(target, database, f"""SET NOCOUNT ON;
SELECT CONCAT('EVIDENCE|',RoleName,'|',InsertKey,'|',SessionId,'|',Outcome,'|',COALESCE(CONVERT(varchar(12),ErrorNumber),''))
FROM lab.RangeEvidence WHERE Attempt='{attempt}' ORDER BY RoleName;""")
    rows = []
    for line in output.splitlines():
        parts = line.strip().split('|')
        if len(parts) == 6 and parts[0] == "EVIDENCE":
            rows.append({"role": parts[1], "key": int(parts[2]), "spid": int(parts[3]),
                         "outcome": parts[4], "error": int(parts[5]) if parts[5] else None})
    return rows


def _keys(target: Any, database: str) -> tuple[int, ...]:
    output = _sql(target, database,
                  "SET NOCOUNT ON; SELECT CONCAT('KEY|',KeyValue) FROM lab.RangeRows ORDER BY KeyValue;")
    return tuple(int(line.strip().split('|', 1)[1]) for line in output.splitlines()
                 if line.strip().startswith("KEY|"))


def _capture_sql(attempt: str) -> str:
    return f"""SET NOCOUNT ON; SET QUOTED_IDENTIFIER ON;
DECLARE @start datetimeoffset(7),@finish datetimeoffset(7),@db int,@a smallint,@b smallint;
SELECT @start=StartedUtc,@finish=FinishedUtc,@db=DatabaseId FROM lab.RangeRun WHERE RunToken=(SELECT TOP(1) RunToken FROM lab.RangeRun);
SELECT @a=SessionId FROM lab.RangeEvidence WHERE Attempt='{attempt}' AND RoleName='ACTOR_A';
SELECT @b=SessionId FROM lab.RangeEvidence WHERE Attempt='{attempt}' AND RoleName='ACTOR_B';
;WITH T AS(SELECT TRY_CONVERT(xml,target_data) AS TargetData FROM sys.dm_xe_session_targets t JOIN sys.dm_xe_sessions s ON s.address=t.event_session_address WHERE s.name=N'system_health' AND t.target_name=N'ring_buffer'),
E AS(SELECT e.query('.') AS EventData FROM T CROSS APPLY TargetData.nodes('/RingBufferTarget/event[@name="xml_deadlock_report"]') X(e)),
B AS(SELECT EventData,TRY_CONVERT(datetimeoffset(7),EventData.value('(/event/@timestamp)[1]','nvarchar(40)'),127) AS EventAt,EventData.query('(/event/data[@name="xml_report"]/value/deadlock)[1]') AS Graph FROM E),
S AS(SELECT B.EventAt,REPLACE(REPLACE(CONVERT(nvarchar(max),B.Graph),NCHAR(13),N'&#xD;'),NCHAR(10),N'&#xA;') AS GraphText
     FROM B WHERE B.EventAt>=@start AND B.EventAt<=@finish
     AND B.Graph.exist('/deadlock/process-list/process[@spid=sql:variable("@a") and @currentdb=sql:variable("@db")]')=1
     AND B.Graph.exist('/deadlock/process-list/process[@spid=sql:variable("@b") and @currentdb=sql:variable("@db")]')=1)
,
N AS(SELECT TOP (500) CONVERT(int,ROW_NUMBER() OVER(ORDER BY (SELECT NULL))) AS Segment
     FROM sys.all_objects a CROSS JOIN sys.all_objects b)
SELECT CONCAT('GRAPH|',CONVERT(nvarchar(40),S.EventAt,127),'|',N.Segment,'|',
       SUBSTRING(S.GraphText,(N.Segment-1)*300+1,300))
FROM S CROSS JOIN N
WHERE N.Segment<=CEILING(CONVERT(float,LEN(S.GraphText))/300.0)
ORDER BY S.EventAt,N.Segment;
"""


def _run_probe(major: int, expected_build: str) -> dict[str, Any]:
    container = os.environ.get("SQLPERF_SQL_CONTAINER", "")
    if not re.fullmatch(r"sqlperf-con006-range-[0-9]+", container):
        raise PilotError("owned CON-006 pilot container name is missing")
    identity = _identity(container)
    labels = identity.get("Config", {}).get("Labels") or {}
    owner = os.environ.get("SQLPERF_CI_OWNER", "")
    profile = _profile(major)
    image_result = subprocess.run(
        ["docker", "image", "inspect", profile["image"]], capture_output=True,
        text=True, timeout=15, check=False,
    )
    if image_result.returncode:
        raise PilotError("pinned runtime image is not locally inspectable")
    image_rows = json.loads(image_result.stdout)
    if (len(image_rows) != 1
            or image_rows[0].get("Id") not in {profile["manifest_digest"], profile["config_digest"]}
            or profile["image"] not in (image_rows[0].get("RepoDigests") or [])
            or image_rows[0].get("Os") != "linux"
            or image_rows[0].get("Architecture") != "amd64"):
        raise PilotError("runtime image digest or Linux/AMD64 identity differs from the lock")
    host = identity.get("HostConfig", {})
    if (labels.get(OWNER_LABEL) != owner or not re.fullmatch(r"[0-9a-f]{32}", owner)
            or labels.get(SUBJECT_LABEL) != "CON006-RANGE-PILOT"
            or identity.get("Config", {}).get("Image") != profile["image"]
            or identity.get("Image") not in {profile["manifest_digest"], profile["config_digest"]}
            or host.get("NetworkMode") != "none"
            or host.get("NanoCpus") != 2_000_000_000
            or host.get("Memory") != 4 * 1024**3
            or host.get("MemorySwap") != 4 * 1024**3
            or host.get("PortBindings") not in (None, {})
            or identity.get("Mounts")):
        raise PilotError("container ownership does not match the pilot")
    target = execution_target.docker_target(container=container)
    engine_output = _sql(target, "master", execution_target.ENGINE_QUERY, timeout=60)
    engine_match = execution_target.ENGINE_PATTERN.search(engine_output)
    if engine_match is None or int(engine_match.group(1)) != major:
        raise PilotError("runtime engine major version differs from the requested profile")
    actual = int(engine_match.group(1))
    token = os.urandom(4).hex().upper()
    database = f"SQLPERF_LAB_CON006_{token}"
    try:
        _sql(target, "master", _setup_sql(database, major, token), timeout=45)
        optlock_before_deadlock = _optimized_locking_state(target, database)
        start_a = _actor_sql("ACTOR_A", "DEADLOCK", token, 70, 20, 40, "LOW")
        start_b = _actor_sql("ACTOR_B", "DEADLOCK", token, 30, 60, 80, "HIGH")
        process_a = _sqlcmd_process(target, database, start_a)
        process_b = _sqlcmd_process(target, database, start_b)
        process_a.stdin.write(start_a); process_a.stdin.close(); process_a.stdin = None
        process_b.stdin.write(start_b); process_b.stdin.close(); process_b.stdin = None
        active_query = "SET NOCOUNT ON; SELECT CONCAT('ACTIVE|',COUNT(*)) FROM lab.RangeEvidence WHERE Attempt='DEADLOCK' AND Outcome='ACTIVE';"
        ready = _poll(target, database, active_query, lambda v: "ACTIVE|2" in v, 10)
        if ready is None:
            _signals(target, database, "START_INSERTS", "A_IS_WAITING")
            try:
                out_a, err_a = process_a.communicate(timeout=ACTOR_SECONDS)
                out_b, err_b = process_b.communicate(timeout=ACTOR_SECONDS)
            except subprocess.TimeoutExpired as exc:
                process_a.kill(); process_b.kill()
                process_a.communicate(timeout=5); process_b.communicate(timeout=5)
                raise PilotError("range actors failed to reach the barrier and exceeded cleanup deadline") from exc
            evidence = _evidence(target, database, "DEADLOCK")
            raise PilotError(
                "both serializable range readers did not reach the barrier; "
                f"evidence={evidence!r}; actor_errors={(err_a[-1000:], err_b[-1000:])!r}; "
                f"actor_output={(out_a[-1000:], out_b[-1000:])!r}"
            )
        actors = {r["role"]: r["spid"] for r in _evidence(target, database, "DEADLOCK")}
        if set(actors) != {"ACTOR_A", "ACTOR_B"} or actors["ACTOR_A"] == actors["ACTOR_B"]:
            raise PilotError("range actors are not bound to two distinct SPIDs")
        hobt_output = _sql(target, database, """SET NOCOUNT ON;
SELECT CONCAT('HOBT|',hobt_id) FROM sys.partitions
WHERE object_id=OBJECT_ID(N'lab.RangeRows') AND index_id=1;""")
        hobt_line = next((line.strip() for line in hobt_output.splitlines()
                          if line.strip().startswith("HOBT|")), None)
        if not hobt_line:
            _signals(target, database, "START_INSERTS", "A_IS_WAITING")
            raise PilotError("range index HoBT identity is unavailable")
        hobt_id = int(hobt_line.split("|", 1)[1])
        lock_query = f"""SET NOCOUNT ON;
SELECT CONCAT('LOCKS|',COUNT(DISTINCT r.session_id))
FROM sys.dm_exec_requests r
WHERE r.session_id IN({actors['ACTOR_A']},{actors['ACTOR_B']})
  AND r.wait_type=N'WAITFOR'
  AND EXISTS(SELECT 1 FROM sys.dm_tran_locks l
    WHERE l.request_session_id=r.session_id AND l.resource_type=N'KEY'
      AND l.resource_associated_entity_id={hobt_id}
      AND l.request_status=N'GRANT' AND l.request_mode IN(N'RangeS-S',N'RangeS-U'));"""
        both_ranges_ready = _poll(target, database, lock_query,
                                  lambda v: "LOCKS|2" in v, WAIT_SECONDS)
        if both_ranges_ready is None:
            _signals(target, database, "START_INSERTS", "A_IS_WAITING")
            raise PilotError("both range readers did not expose granted serializable key-range locks")
        _signals(target, database, "START_INSERTS")
        wait_query = f"""SET NOCOUNT ON; SELECT CONCAT('WAIT|',session_id,'|',blocking_session_id,'|',wait_type)
FROM sys.dm_exec_requests WHERE session_id={actors['ACTOR_A']} AND blocking_session_id={actors['ACTOR_B']} AND wait_type LIKE N'LCK_M%';"""
        observed_wait = _poll(target, database, wait_query,
                              lambda v: "WAIT|" in v, WAIT_SECONDS)
        _signals(target, database, "A_IS_WAITING")
        with ThreadPoolExecutor(max_workers=2) as pool:
            future_a = pool.submit(process_a.communicate, timeout=ACTOR_SECONDS)
            future_b = pool.submit(process_b.communicate, timeout=ACTOR_SECONDS)
            out_a, err_a = future_a.result(timeout=ACTOR_SECONDS + 5)
            out_b, err_b = future_b.result(timeout=ACTOR_SECONDS + 5)
        if process_a.returncode or process_b.returncode:
            raise PilotError(
                "range actor returned an unexpected SQL failure; "
                f"exit_codes={(process_a.returncode, process_b.returncode)!r}; "
                f"actor_errors={(err_a[-1500:], err_b[-1500:])!r}; "
                f"actor_output={(out_a[-1500:], out_b[-1500:])!r}"
            )
        actor_rows = _evidence(target, database, "DEADLOCK")
        _sql(target, database, "SET NOCOUNT ON; UPDATE lab.RangeRun SET FinishedUtc=SYSUTCDATETIME();")
        optlock_after_deadlock = _optimized_locking_state(target, database)
        boundary = _sql(target, database, """SET NOCOUNT ON; SET QUOTED_IDENTIFIER ON;
SELECT CONCAT('IDENTITY|',DB_ID(),'|',OBJECT_NAME(OBJECT_ID(N'lab.RangeRows')),'|',
 (SELECT name FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.RangeRows') AND index_id=1),'|',
 (SELECT hobt_id FROM sys.partitions WHERE object_id=OBJECT_ID(N'lab.RangeRows') AND index_id=1),'|',
 CONVERT(nvarchar(40),StartedUtc,127),'|',CONVERT(nvarchar(40),FinishedUtc,127),'|',RunToken)
FROM lab.RangeRun;""")
        identity_row = next((line.strip().split('|') for line in boundary.splitlines()
                             if line.strip().startswith("IDENTITY|")), None)
        if not identity_row or len(identity_row) != 8:
            raise PilotError("range database identity boundary is incomplete")
        dbid, objectname, indexname, hobt, started, finished, observed_token = identity_row[1:]
        graph_output = _run_actor(target, database, _capture_sql("DEADLOCK"), timeout=20)
        graph_chunks: dict[str, list[tuple[int, str]]] = {}
        for line in graph_output.splitlines():
            parts = line.lstrip().rstrip("\r").split('|', 3)
            if len(parts) == 4 and parts[0] == "GRAPH":
                try:
                    graph_chunks.setdefault(parts[1], []).append((int(parts[2]), parts[3]))
                except ValueError:
                    continue
        graph_rows = [["GRAPH", timestamp, "".join(chunk for _, chunk in sorted(chunks))]
                      for timestamp, chunks in graph_chunks.items()]
        graph_parse_issue = None
        graph_parse_context_codes = None
        if len(graph_rows) == 1 and len(graph_rows[0]) == 3:
            try:
                import xml.etree.ElementTree as ET
                ET.fromstring(graph_rows[0][2])
            except ET.ParseError as exc:
                graph_parse_issue = f"{exc}:line={exc.position[0]},column={exc.position[1]}"
                graph_parse_context_codes = [ord(ch) for ch in graph_rows[0][2][max(0, exc.position[1]-4):exc.position[1]+5]]
        initial_keys = (10, 50, 90)
        final_deadlock = _keys(target, database)
        insert_outcomes = tuple(RangeInsertOutcome(
            row["role"], row["spid"], row["key"], row["outcome"], row["error"]
        ) for row in actor_rows)
        capture_result = None
        if len(graph_rows) == 1 and len(actor_rows) == 2:
            spids = tuple((role, actors[role]) for role in ("ACTOR_A", "ACTOR_B"))
            victim_spid = None
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(graph_rows[0][2])
                victim_node = root.find("victim-list/victimProcess")
                victim_process = root.find(f"process-list/process[@id='{victim_node.get('id') if victim_node is not None else ''}']")
                victim_spid = int(victim_process.get("spid")) if victim_process is not None else None
            except (ValueError, ET.ParseError):
                victim_spid = None
            outcomes = tuple(ActorOutcome(
                row["role"], row["spid"],
                "VICTIM" if row["error"] == 1205 else "SURVIVOR",
                row["error"],
            ) for row in actor_rows)
            graph_identity = GraphIdentity(
                int(dbid), spids, f"SQLPERF_LAB_CON006_{token}.lab.RangeRows",
                indexname, str(hobt),
            )
            evidence = CaptureEvidence(
                token, observed_token, "xml_deadlock_report", "system_health", int(dbid),
                spids, graph_rows[0][1], started, finished, len(graph_rows), outcomes,
                graph_identity, graph_rows[0][2],
            )
            capture_result = evaluate_range_capture(RangeCaptureEvidence(
                evidence, initial_keys, (("ACTOR_A", 70), ("ACTOR_B", 30)),
                insert_outcomes, final_deadlock,
            ))

        # The control arm is a separate, sequential pair of autocommit sessions.
        _sql(target, database, "SET NOCOUNT ON; DELETE lab.RangeRows WHERE KeyValue NOT IN(10,50,90); DELETE lab.RangeEvidence;")
        optlock_before_control = _optimized_locking_state(target, database)
        control_start = _sql(target, database, "SET NOCOUNT ON; SELECT CONCAT('UTC|',CONVERT(nvarchar(40),TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00'),127));")
        control_spids: dict[str, int] = {}
        control_a = _control_sql("ACTOR_A", token, 70)
        control_b = _control_sql("ACTOR_B", token, 30)
        proc_ca = _sqlcmd_process(target, database, control_a)
        proc_cb = _sqlcmd_process(target, database, control_b)
        proc_ca.stdin.write(control_a); proc_ca.stdin.close(); proc_ca.stdin = None
        proc_cb.stdin.write(control_b); proc_cb.stdin.close(); proc_cb.stdin = None
        with ThreadPoolExecutor(max_workers=2) as pool:
            future_ca = pool.submit(proc_ca.communicate, timeout=15)
            future_cb = pool.submit(proc_cb.communicate, timeout=15)
            out_ca, err_ca = future_ca.result(timeout=20)
            out_cb, err_cb = future_cb.result(timeout=20)
        if proc_ca.returncode or proc_cb.returncode:
            raise PilotError("serial control actor returned an unexpected SQL failure")
        optlock_after_control = _optimized_locking_state(target, database)
        for output in (out_ca, out_cb):
            marker = next((x.strip().split('|') for x in output.splitlines()
                           if x.strip().startswith("CONTROL|")), None)
            if marker and len(marker) == 3:
                control_spids[marker[1]] = int(marker[2])
        control_end = _sql(target, database, "SET NOCOUNT ON; SELECT CONCAT('UTC|',CONVERT(nvarchar(40),TODATETIMEOFFSET(SYSUTCDATETIME(),'+00:00'),127));")
        control_events = 0
        if set(control_spids) == {"ACTOR_A", "ACTOR_B"}:
            for spid in control_spids.values():
                query = f"""SET NOCOUNT ON; SET QUOTED_IDENTIFIER ON;
DECLARE @start datetimeoffset(7)=TRY_CONVERT(datetimeoffset(7),N'{control_start.split('|')[-1].strip()}',127),@finish datetimeoffset(7)=TRY_CONVERT(datetimeoffset(7),N'{control_end.split('|')[-1].strip()}',127);
;WITH T AS(SELECT TRY_CONVERT(xml,target_data) x FROM sys.dm_xe_session_targets t JOIN sys.dm_xe_sessions s ON s.address=t.event_session_address WHERE s.name=N'system_health' AND t.target_name=N'ring_buffer'),E AS(SELECT e.query('.') x FROM T CROSS APPLY x.nodes('/RingBufferTarget/event[@name="xml_deadlock_report"]') X(e))
SELECT CONCAT('COUNT|',COUNT(*)) FROM E WHERE TRY_CONVERT(datetimeoffset(7),x.value('(/event/@timestamp)[1]','nvarchar(40)'),127) BETWEEN @start AND @finish AND x.exist('/event/data[@name="xml_report"]/value/deadlock/process-list/process[@spid={spid}]')=1;"""
                output = _sql(target, database, query)
                control_events += sum(int(line.strip().split('|')[1]) for line in output.splitlines()
                                      if line.strip().startswith("COUNT|"))
        control_rows = _evidence(target, database, "CONTROL")
        final_control = _keys(target, database)
        control_result = evaluate_range_control(RangeControlEvidence(
            token, observed_token,
            tuple((role, control_spids[role]) for role in ("ACTOR_A", "ACTOR_B"))
            if set(control_spids) == {"ACTOR_A", "ACTOR_B"} else None,
            tuple(ActorOutcome(r["role"], r["spid"], "SUCCESS" if r["outcome"] == "INSERTED" else "ERROR", r["error"])
                  for r in control_rows) if len(control_rows) == 2 else None,
            initial_keys, (("ACTOR_A", 70), ("ACTOR_B", 30)), final_control,
            control_events, tuple((r["role"], r["key"]) for r in control_rows),
        ))
        statuses = {
            "deadlock_arm": capture_result.verdict.value if capture_result else Verdict.NOT_PROVEN.value,
            "serial_control": control_result.verdict.value,
            "wait_observed_before_release": observed_wait is not None,
            "deadlock_graph_count": len(graph_rows),
            "deadlock_graph_chars": len(graph_rows[0][2]) if len(graph_rows) == 1 and len(graph_rows[0]) == 3 else 0,
            "deadlock_graph_parse_issue": graph_parse_issue,
            "deadlock_graph_parse_context_codes": graph_parse_context_codes,
            "deadlock_final_keys": list(final_deadlock),
            "control_final_keys": list(final_control),
            "control_deadlock_count": control_events,
            "optimized_locking": {
                "before_deadlock": optlock_before_deadlock,
                "after_deadlock": optlock_after_deadlock,
                "before_control": optlock_before_control,
                "after_control": optlock_after_control,
            },
        }
        if capture_result:
            statuses["deadlock_reasons"] = list(capture_result.reasons)
        statuses["control_reasons"] = list(control_result.reasons)
        optlock_values = (optlock_before_deadlock, optlock_after_deadlock,
                          optlock_before_control, optlock_after_control)
        optlock_stable = optlock_before_deadlock == optlock_after_deadlock == optlock_before_control == optlock_after_control
        optlock_required = major != 17 or all(value in (0, 1) for value in optlock_values)
        statuses["outcome"] = "PASS" if (
            observed_wait is not None and capture_result
            and capture_result.verdict is Verdict.PASS
            and control_result.verdict is Verdict.PASS
            and optlock_stable and optlock_required
        ) else "NOT_PROVEN"
        statuses["product_major_version"] = actual
        build_output = _sql(target, "master", "SET NOCOUNT ON; SELECT CONCAT('BUILD|',CONVERT(nvarchar(128),SERVERPROPERTY('ProductVersion')));")
        product_build = next((line.strip().split("|", 1)[1] for line in build_output.splitlines()
                              if line.strip().startswith("BUILD|")), None)
        if product_build != expected_build:
            raise PilotError("runtime engine build differs from the digest-pinned matrix expectation")
        statuses["product_build"] = product_build
        return statuses
    finally:
        # The outer workflow removes the fresh, owner-checked disposable container.
        try:
            _sql(target, "master", f"""SET NOCOUNT ON; DECLARE @db sysname=N'{database}';
IF DB_ID(@db) IS NOT NULL BEGIN
 DECLARE @p nvarchar(128),@c nvarchar(16),@d nvarchar(16),@r nvarchar(16),@s nvarchar(max);
 SET @s=N'SELECT @p=MAX(CASE WHEN name=N''SQLPERF.Project'' THEN CONVERT(nvarchar(128),value) END),@c=MAX(CASE WHEN name=N''SQLPERF.ContractVersion'' THEN CONVERT(nvarchar(16),value) END),@d=MAX(CASE WHEN name=N''SQLPERF.DemoId'' THEN CONVERT(nvarchar(16),value) END),@r=MAX(CASE WHEN name=N''SQLPERF.RunToken'' THEN CONVERT(nvarchar(16),value) END) FROM '+QUOTENAME(@db)+N'.sys.extended_properties WHERE class=0;';
 EXEC sys.sp_executesql @s,N'@p nvarchar(128) OUT,@c nvarchar(16) OUT,@d nvarchar(16) OUT,@r nvarchar(16) OUT',@p OUT,@c OUT,@d OUT,@r OUT;
 IF @p<>N'SQL_PerformanceSchulung' OR @c<>N'1.0' OR @d<>N'CON-006' OR @r<>N'{token}' THROW 51102,'FAIL_CLEANUP: pilot ownership markers differ',1;
 SET @s=N'ALTER DATABASE '+QUOTENAME(@db)+N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE '+QUOTENAME(@db)+N';'; EXEC(@s);
END;
IF DB_ID(@db) IS NOT NULL THROW 51103,'FAIL_CLEANUP: pilot database remains',1;""", timeout=45)
        except Exception as exc:
            raise PilotError("owned pilot database cleanup failed") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-major-version", type=int, choices=(15, 16, 17), required=True)
    parser.add_argument("--expected-product-build", required=True,
                        help="exact SERVERPROPERTY('ProductVersion') value for the pinned image")
    args = parser.parse_args()
    try:
        print(json.dumps(_run_probe(args.product_major_version, args.expected_product_build), sort_keys=True))
        return 0
    except (PilotError, ExecutionTargetError, OSError, subprocess.TimeoutExpired,
            ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"outcome": "FAIL", "scope": "CON-006 range pilot",
                          "reason": str(exc)[:2000]}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
